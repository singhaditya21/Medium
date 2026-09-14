"""Local teaching model: one SQLite domain, not an IAM service or CRM adapter.

Authentication, signature validation, external policy distribution, network access,
and remote side effects are deliberately absent. Fixtures represent already
validated grants. Run tests before using this model to reason about a real API.
"""
from dataclasses import asdict, dataclass
import hashlib
import json
import sqlite3
import time


class Denied(Exception):
    pass


class Conflict(Exception):
    pass


class UnknownOutcome(Exception):
    """The caller lost a response; the transaction may already have committed."""


@dataclass(frozen=True)
class Command:
    tenant: str
    principal: str
    actor: str
    key: str
    record: str
    expected_version: int
    destination: str
    policy_epoch: int

    def digest(self):
        # Sufficient only for this restricted string/integer schema, not a
        # general cross-language canonical-JSON/signature implementation.
        for field in (self.expected_version, self.policy_epoch):
            if type(field) is not int or field < 0:
                raise ValueError("versions must be nonnegative integers")
        for field in (self.tenant, self.principal, self.actor, self.key,
                      self.record, self.destination):
            if not isinstance(field, str) or not field:
                raise ValueError("identifiers must be nonempty strings")
        raw = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()


class Domain:
    def __init__(self, path, clock=time.time):
        self.path, self.clock = str(path), clock

    def connect(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        db.row_factory = sqlite3.Row
        return db

    def initialize(self, command, grant_id="approval-1", expires=200):
        """Install synthetic fixtures in a NEW temporary teaching database."""
        db = self.connect()
        try:
            db.executescript("""
            CREATE TABLE policy (tenant TEXT PRIMARY KEY, epoch INTEGER NOT NULL);
            CREATE TABLE records (tenant TEXT, id TEXT, version INTEGER NOT NULL,
                destination TEXT NOT NULL, PRIMARY KEY(tenant,id));
            CREATE TABLE grants (id TEXT PRIMARY KEY, digest TEXT NOT NULL,
                expires REAL NOT NULL, revoked INTEGER NOT NULL DEFAULT 0,
                consumed INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE effects (tenant TEXT, principal TEXT, key TEXT,
                digest TEXT NOT NULL, result TEXT NOT NULL,
                PRIMARY KEY(tenant,principal,key));
            CREATE TABLE outbox (tenant TEXT, principal TEXT, key TEXT,
                payload TEXT NOT NULL, PRIMARY KEY(tenant,principal,key));
            """)
            db.execute("INSERT INTO policy VALUES (?,?)", (command.tenant, command.policy_epoch))
            db.execute("INSERT INTO records VALUES (?,?,?,?)",
                       (command.tenant, command.record, command.expected_version, "general"))
            self.add_grant(grant_id, command, expires)
        finally:
            db.close()

    def add_grant(self, grant_id, command, expires=200):
        db = self.connect()
        try:
            db.execute("INSERT INTO grants(id,digest,expires) VALUES (?,?,?)",
                       (grant_id, command.digest(), expires))
        finally:
            db.close()

    def revoke(self, grant_id):
        db = self.connect()
        try:
            db.execute("UPDATE grants SET revoked=1 WHERE id=?", (grant_id,))
        finally:
            db.close()

    def execute(self, command, grant_id, lose_response=False):
        digest = command.digest()
        db = self.connect()
        try:
            # All records here are in ONE local transaction domain. This is not
            # a lock on a remote CRM or on an external authorization server.
            db.execute("BEGIN IMMEDIATE")
            grant = db.execute("SELECT * FROM grants WHERE id=?", (grant_id,)).fetchone()
            if not grant or grant["digest"] != digest:
                raise Denied("grant is not bound to this exact command")
            if grant["revoked"] or self.clock() >= grant["expires"]:
                raise Denied("revoked or expired at the admission check")
            policy = db.execute("SELECT epoch FROM policy WHERE tenant=?", (command.tenant,)).fetchone()
            if not policy or policy["epoch"] != command.policy_epoch:
                raise Denied("policy epoch changed; reassess")
            old = db.execute("SELECT digest,result FROM effects WHERE tenant=? AND principal=? AND key=?",
                             (command.tenant, command.principal, command.key)).fetchone()
            if old:
                if old["digest"] != digest:
                    raise Conflict("same key with different intent")
                db.commit()
                return json.loads(old["result"])
            if grant["consumed"]:
                raise Denied("approval already consumed")
            changed = db.execute("""UPDATE records SET destination=?,version=version+1
                WHERE tenant=? AND id=? AND version=?""",
                (command.destination, command.tenant, command.record, command.expected_version))
            if changed.rowcount != 1:
                raise Conflict("record version changed; reassess")
            used = db.execute("UPDATE grants SET consumed=1 WHERE id=? AND consumed=0", (grant_id,))
            if used.rowcount != 1:
                raise Denied("approval already consumed")
            result = {"record": command.record, "version": command.expected_version + 1,
                      "destination": command.destination, "action_key": command.key}
            encoded = json.dumps(result, sort_keys=True)
            db.execute("INSERT INTO effects VALUES (?,?,?,?,?)",
                       (command.tenant, command.principal, command.key, digest, encoded))
            db.execute("INSERT INTO outbox VALUES (?,?,?,?)",
                       (command.tenant, command.principal, command.key, encoded))
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()
        if lose_response:
            raise UnknownOutcome("simulated response loss after commit")
        return result

    def lookup(self, command):
        """Read-only lookup. A real service MUST authorize this read separately."""
        db = self.connect()
        try:
            row = db.execute("SELECT digest,result FROM effects WHERE tenant=? AND principal=? AND key=?",
                             (command.tenant, command.principal, command.key)).fetchone()
            if row and row["digest"] != command.digest():
                raise Conflict("same key with different intent")
            return json.loads(row["result"]) if row else None
        finally:
            db.close()

    def inspect(self):
        db = self.connect()
        try:
            return {"effects": db.execute("SELECT count(*) FROM effects").fetchone()[0],
                    "outbox": db.execute("SELECT count(*) FROM outbox").fetchone()[0],
                    "consumed": db.execute("SELECT sum(consumed) FROM grants").fetchone()[0],
                    "version": db.execute("SELECT version FROM records").fetchone()[0]}
        finally:
            db.close()


def unknown_outcome_policy(has_atomic_idempotency_contract):
    return "resolve-or-same-key-retry" if has_atomic_idempotency_contract else "reconcile-or-escalate"
