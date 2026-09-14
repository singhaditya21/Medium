import concurrent.futures
from dataclasses import replace
from pathlib import Path
import tempfile
import threading
import sqlite3
import unittest

from protocol import Command, Domain, Denied, Conflict, UnknownOutcome, unknown_outcome_policy


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "domain.sqlite"
        self.cmd = Command("IN", "ops-owner", "routing-agent", "case-471-route-v7",
                           "case-471", 7, "enterprise-support", 12)
        self.domain = Domain(self.path, clock=lambda: 100)
        self.domain.initialize(self.cmd)

    def test_commit_and_outbox_are_one_effect(self):
        result = self.domain.execute(self.cmd, "approval-1")
        self.assertEqual(result["version"], 8)
        self.assertEqual(self.domain.inspect(), {"effects": 1, "outbox": 1, "consumed": 1, "version": 8})

    def test_lost_response_resolved_after_connection_restart(self):
        with self.assertRaises(UnknownOutcome):
            self.domain.execute(self.cmd, "approval-1", lose_response=True)
        restarted = Domain(self.path, clock=lambda: 100)
        result = restarted.lookup(self.cmd)
        self.assertEqual(result["version"], 8)
        self.assertEqual(restarted.execute(self.cmd, "approval-1"), result)
        self.assertEqual(restarted.inspect()["effects"], 1)

    def test_two_workers_same_action_have_one_effect(self):
        barrier = threading.Barrier(2)
        def run(_):
            barrier.wait(timeout=5)
            return Domain(self.path, clock=lambda: 100).execute(self.cmd, "approval-1")
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            a, b = list(pool.map(run, range(2)))
        self.assertEqual(a, b)
        self.assertEqual(self.domain.inspect()["effects"], 1)

    def test_same_key_different_intent_is_rejected_even_with_new_grant(self):
        self.domain.execute(self.cmd, "approval-1")
        other = replace(self.cmd, destination="other-team")
        self.domain.add_grant("approval-2", other)
        with self.assertRaises(Conflict):
            self.domain.execute(other, "approval-2")
        self.assertEqual(self.domain.inspect()["consumed"], 1)

    def test_approval_cannot_be_reused_for_another_key(self):
        self.domain.execute(self.cmd, "approval-1")
        with self.assertRaises(Denied):
            self.domain.execute(replace(self.cmd, key="another-key", expected_version=8), "approval-1")

    def test_expiry_boundary_fails_closed(self):
        with self.assertRaises(Denied):
            Domain(self.path, clock=lambda: 200).execute(self.cmd, "approval-1")
        self.assertEqual(self.domain.inspect()["effects"], 0)

    def test_wrong_tenant_principal_or_actor_rejected(self):
        for field in ("tenant", "principal", "actor"):
            with self.subTest(field=field), self.assertRaises(Denied):
                self.domain.execute(replace(self.cmd, **{field: "wrong"}), "approval-1")

    def test_stale_record_rolls_back_approval_consumption(self):
        db = self.domain.connect()
        db.execute("UPDATE records SET version=8")
        db.close()
        with self.assertRaises(Conflict):
            self.domain.execute(self.cmd, "approval-1")
        self.assertEqual(self.domain.inspect()["consumed"], 0)

    def test_revocation_committed_after_precheck_before_execution_rejected(self):
        # A gateway precheck could see revoked=0, then an admin commits revocation.
        db = self.domain.connect()
        self.assertEqual(db.execute("SELECT revoked FROM grants").fetchone()[0], 0)
        db.close()
        self.domain.revoke("approval-1")
        with self.assertRaises(Denied):
            self.domain.execute(self.cmd, "approval-1")
        self.assertEqual(self.domain.inspect()["effects"], 0)

    def test_new_policy_epoch_blocks_old_approval(self):
        db = self.domain.connect()
        db.execute("UPDATE policy SET epoch=13")
        db.close()
        with self.assertRaises(Denied):
            self.domain.execute(self.cmd, "approval-1")

    def test_revocation_transaction_wins_while_worker_is_running(self):
        # Force one legitimate ordering: revocation owns the database writer
        # lock before a competing worker attempts admission. No timing sleeps.
        db = self.domain.connect()
        db.execute("BEGIN IMMEDIATE")
        db.execute("UPDATE grants SET revoked=1 WHERE id='approval-1'")
        attempted = threading.Event()

        def run():
            class ObservedDomain(Domain):
                def connect(inner):
                    connection = super().connect()
                    connection.set_trace_callback(
                        lambda sql: attempted.set() if sql == "BEGIN IMMEDIATE" else None)
                    return connection
            return ObservedDomain(self.path, clock=lambda: 100).execute(self.cmd, "approval-1")

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            result = pool.submit(run)
            try:
                self.assertTrue(attempted.wait(timeout=5))
                db.commit()
            finally:
                db.rollback()
                db.close()
            with self.assertRaises(Denied):
                result.result(timeout=5)
        self.assertEqual(self.domain.inspect()["effects"], 0)

    def test_action_admitted_before_concurrent_revocation_can_commit(self):
        admitted, release, revoking = threading.Event(), threading.Event(), threading.Event()
        def admission_clock():
            admitted.set()  # execute already owns its write transaction
            if not release.wait(timeout=5):
                raise TimeoutError("test admission release not signaled")
            return 100
        class ObservedRevoker(Domain):
            def connect(inner):
                connection = super().connect()
                connection.set_trace_callback(
                    lambda sql: revoking.set() if sql.startswith("UPDATE grants") else None)
                return connection
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            action = pool.submit(Domain(self.path, clock=admission_clock).execute,
                                 self.cmd, "approval-1")
            try:
                self.assertTrue(admitted.wait(timeout=5))
                revocation = pool.submit(ObservedRevoker(self.path).revoke, "approval-1")
                self.assertTrue(revoking.wait(timeout=5))
            finally:
                release.set()
            self.assertEqual(action.result(timeout=5)["version"], 8)
            revocation.result(timeout=5)
        self.assertEqual(self.domain.inspect()["effects"], 1)
        with self.assertRaises(Denied):
            self.domain.execute(self.cmd, "approval-1")

    def test_outbox_failure_rolls_back_record_grant_and_effect(self):
        db = self.domain.connect()
        db.execute("""CREATE TRIGGER fail_outbox BEFORE INSERT ON outbox
            BEGIN SELECT RAISE(ABORT, 'synthetic outbox failure'); END""")
        db.close()
        with self.assertRaises(sqlite3.IntegrityError):
            self.domain.execute(self.cmd, "approval-1")
        self.assertEqual(self.domain.inspect(),
                         {"effects": 0, "outbox": 0, "consumed": 0, "version": 7})

    def test_later_revocation_does_not_undo_committed_effect(self):
        self.domain.execute(self.cmd, "approval-1")
        self.domain.revoke("approval-1")
        with self.assertRaises(Denied):
            self.domain.execute(self.cmd, "approval-1")
        self.assertEqual(self.domain.lookup(self.cmd)["version"], 8)

    def test_no_contract_never_selects_blind_retry(self):
        self.assertEqual(unknown_outcome_policy(False), "reconcile-or-escalate")

    def test_schema_rejects_boolean_version(self):
        with self.assertRaises(ValueError):
            replace(self.cmd, expected_version=True).digest()


if __name__ == "__main__":
    unittest.main(verbosity=2)
