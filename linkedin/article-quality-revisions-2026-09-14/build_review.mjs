// Build local review artifacts only. This directory is excluded from Pages staging.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
const here = path.dirname(fileURLToPath(import.meta.url));
// CODEX_NODE_MODULES may override the installed desktop dependency location.
const modules = process.env.CODEX_NODE_MODULES || '/Users/adityasingh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const require = createRequire(path.join(modules, '_review-loader.cjs'));
const { marked } = require('marked');
const sharp = require('sharp');
const read = name => fs.readFile(path.join(here, name), 'utf8');
const write = (name, text) => fs.writeFile(path.join(here, name), text);
const sha = value => createHash('sha256').update(value).digest('hex');
const escape = s => s.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('"', '&quot;');
const css = `
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#fff;color:#101828;font:19px/1.75 Georgia,serif}
main{max-width:940px;margin:auto;padding:36px 34px 90px}h1,h2,h3{font-family:Arial,sans-serif;line-height:1.22;color:#1048a8;overflow-wrap:break-word}
h1{font-size:42px;letter-spacing:-1px;margin:0 0 22px}h2{font-size:29px;margin:2em 0 .8em}h3{font-size:23px;margin:1.7em 0 .8em}
p,li{overflow-wrap:break-word}p{margin:1.15em 0}a{color:#1048a8;text-underline-offset:3px}li{margin:.55em 0}figure{margin:36px 0}
img{max-width:100%;height:auto;display:block;margin:24px auto}figcaption{font:15px/1.6 Arial,sans-serif}pre{font:14px/1.65 Menlo,Consolas,monospace;overflow:auto;padding:20px;border:1px solid #b8cdf3;border-radius:8px;background:white}
code{font-size:.84em}pre code{font-size:inherit}table{border-collapse:collapse;width:100%;font:16px/1.5 Arial,sans-serif}th,td{border:1px solid #b8cdf3;padding:12px;text-align:left;vertical-align:top}th{color:#1048a8;background:white}
.table-scroll{overflow-x:auto;margin:24px 0}.review{border:1px solid #175cd3;border-left:5px solid #175cd3;padding:17px 20px;margin:0 0 38px;font:14px/1.6 Arial,sans-serif}
.review p{margin:.5em 0}.eyebrow{font:700 13px/1.5 Arial,sans-serif;letter-spacing:1.2px;color:#175cd3}nav{font:15px/1.7 Arial,sans-serif;margin-bottom:22px}
.card{padding:24px 0;border-top:1px solid #b8cdf3}.card h2{margin:6px 0 12px}.card p{margin:8px 0}.caption{font:15px/1.6 Arial,sans-serif}.meta{font:14px/1.6 Arial,sans-serif}hr{border:0;border-top:1px solid #b8cdf3;margin:35px 0}
@media(max-width:600px){main{padding:22px 18px 60px}body{font-size:18px;line-height:1.7}h1{font-size:32px;letter-spacing:-.5px}h2{font-size:26px}h3{font-size:22px}table{min-width:570px;font-size:15px}.review{padding:14px}.table-scroll{outline-offset:3px}pre{padding:14px}}
@media print{.review,nav{display:none}main{padding:0}h2{break-after:avoid}figure,table{break-inside:avoid}}
`;
const layout = (title, body, source) => `<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escape(title)} — revision review</title><style>${css}</style></head><body><main><nav><a href="index.html">← Four-article review</a> · <a href="README.md">Changes and validation</a></nav><aside class="review"><strong>REVISED DRAFT · NOT APPLIED TO LINKEDIN OR MEDIUM</strong><p>Prepared 14 September 2026. Review this exact body and its figures before approving replacement. Existing URLs, schedules, covers and publication settings are unchanged.</p><p><a href="${source}">Original published LinkedIn edition</a> · <a href="protocol.py">Local teaching model</a> · <a href="test_protocol.py">Protocol tests</a> · <a href="test_calculations.py">Arithmetic tests</a></p></aside><article>${body.replaceAll('<table>', '<div class="table-scroll" tabindex="0" role="region" aria-label="Scrollable data table"><table>').replaceAll('</table>', '</table></div>')}</article></main></body></html>\n`;

const edits = [];
const baselinePath = '../newsletter-backfill-2026-09-14/N01-agentic-crm.html';
const baseline = await read(baselinePath);
let crm = baseline.match(/<article>([\s\S]*?)<\/article>/)[1];
function replaceExactly(before, after, reason) {
  const hits = crm.split(before).length - 1;
  if (hits !== 1) throw new Error(`${reason}: expected one anchor, got ${hits}`);
  crm = crm.replace(before, after);
  edits.push({reason, before, after});
}
function paragraph(prefix, after, reason) {
  const matches = [...crm.matchAll(/<p>[\s\S]*?<\/p>/g)].map(m => m[0]).filter(p => p.startsWith(prefix));
  if (matches.length !== 1) throw new Error(`Missing/ambiguous paragraph: ${prefix}`);
  replaceExactly(matches[0], after, reason);
}
replaceExactly('<p>A strategic customer submits', '<p>In this illustrative scenario, a strategic customer submits', 'Label opening as illustrative, not a measured customer incident');
replaceExactly('verify that each</p>\n<p>system actually changed.', 'verify that each system actually changed.', 'Repair split sentence from source export');
paragraph('<p>The enthusiasm is real;', '<p>Adoption forecasts are not evidence that a particular workflow is safe. In its <a href="https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027">June 25, 2025 forecast</a>, Gartner projected that more than 40% of agentic-AI projects would be cancelled by the end of 2027 and that 33% of enterprise software applications would include agentic AI by 2028. These were forecasts, not observed completion rates.</p>', 'Date Gartner forecast and distinguish projected from observed outcomes');
paragraph('<p><a href="https://www.mckinsey.com/', '<p>The linked <a href="https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai/">McKinsey survey, updated August 25, 2026</a>, reports regular AI use in at least one business function among nearly nine in ten respondents, while 37% report some enterprise-level EBIT impact. These are respondent reports, not causal evidence for this architecture. They reinforce the need to measure the workflow\'s own baseline, costs and outcomes.</p>', 'Replace stale 2025 figures because the source URL now contains the 2026 survey');
replaceExactly('<figure><img src="../../assets/images/agentic-crm-reference-architecture/figure-01.webp"', '<p>Before granting CRM write access, require a typed command contract, an explicit unknown-outcome path and a demonstrated failure test. This blueprint supplies all three for one internal routing action. The runnable companion is a local teaching model, not a production-readiness certificate.</p>\n<figure><img src="../../assets/images/agentic-crm-reference-architecture/figure-01.webp"', 'Add the operating decision and concrete reader deliverables before the architecture');
replaceExactly('idempotency keys so retries do not send the same email or issue the same refund twice;', 'domain-enforced idempotency contracts and stable action identifiers for supported retries;', 'A key alone does not prevent duplicate external effects');
paragraph('<p>“Rollback”', '<p>“Rollback” needs a defined boundary. A database transaction can roll back before commit; a later compensating action may reduce harm but cannot erase history. A customer email cannot be unsent. A correction, freeze or reassignment is a new action with its own authority and current preconditions, and it may fail. Route unsafe compensation into incident management with an accountable owner.</p>', 'Separate transaction rollback from authorized, potentially fallible compensation');
paragraph('<p>Execution is incomplete until', '<p>Execution is incomplete until an authoritative acknowledgement with sufficient outcome detail, a versioned read or a correlated change event establishes the expected postcondition. A transport acknowledgement alone does not. A transactional outbox can atomically record a local mutation and its outgoing event; it does not make all downstream effects exactly once. A timeout leaves the outcome unknown: resolve the original action identity and retry only under a supported domain idempotency contract. Otherwise reconcile or escalate. A model saying “done” is never proof.</p>', 'Replace unconditional retry and cross-system outbox implications with explicit guarantees');
function replaceFigure(number, file, alt, caption) {
  const pattern = new RegExp(`<figure><img src="\\.\\./\\.\\./assets/images/agentic-crm-reference-architecture/figure-${number}\\.png"[\\s\\S]*?<\\/figure>`, 'g');
  const matches = [...crm.matchAll(pattern)];
  if (matches.length !== 1) throw new Error(`Expected figure ${number}`);
  replaceExactly(matches[0][0], `<figure><img src="figures/${file}.svg" alt="${alt}"/><figcaption>${caption}</figcaption></figure>`, `Replace figure ${number} to show the actual enforcement/recovery contract`);
}
replaceFigure('04', 'crm-unknown-outcome', 'Timeout enters an unknown state; resolve the original action identity, retry only under a valid domain contract, otherwise reconcile or escalate.', 'Figure 4. A timeout does not establish failure. Resolve a recorded result or use a supported same-key retry; an unresolved action without that contract goes to reconciliation or an owner.');
replaceFigure('05', 'crm-atomic-contract', 'One local transaction checks authority and version, mutates the case, consumes approval and records the outcome and outbox. Downstream effects and independent verification remain separate.', 'Figure 5. One domain can bind its mutation, approval consumption, outcome and outbox. Event delivery may repeat, and every downstream effect needs its own contract.');
replaceExactly('ACK and CDC events return thr"', 'ACK and CDC events return through controlled ingress for correlated outcome verification."', 'Repair truncated alternative text on retained figure 6');
paragraph('<p>The queue acknowledgement or CDC event returns', '<p>A correlated authoritative observation returns through the Event Gateway and is checked against the approved postcondition. If the CRM response is lost, the runtime retains the original action ID and resolves its outcome; only a supported same-key retry is eligible. If one domain commits while another remains unavailable, the workflow records a partial or unresolved result, reconciles safely and alerts the owner. New telemetry that contradicts the customer promise stops that message for reassessment. Every plan, permit, command, outcome and verification remains linked in the trace.</p>', 'Carry unknown outcome and independent message authority through the original case');
replaceExactly('<h2>Evaluation is part of the architecture</h2>', `${marked.parse(await read('Q2-contract-insertion.md'))}\n<h2>Evaluation is part of the architecture</h2>`, 'Add exact domain contract, lost-response trace and runnable acceptance model');
// Make the original stored Figure 2 overview caption consistent with the stricter contract.
replaceExactly('acknowledgements close the loop.</figcaption>', 'correlated authoritative observations support postcondition verification.</figcaption>', 'Qualify retained topology caption: transport acknowledgement alone is insufficient');

const specs = [
 {id:'Q1', slug:'Q1-passport', title:'Every AI Agent Needs a Passport', source:'https://www.linkedin.com/pulse/every-ai-agent-needs-passport-aditya-singh-qrvrc/', summary:'Resource-owner enforcement, revocation ordering, one-use approval and a runnable failure model.'},
 {id:'Q2', slug:'Q2-agentic-crm', title:'How to Build an Agentic CRM: A Reference Architecture', source:'https://www.linkedin.com/pulse/how-build-agentic-crm-reference-architecture-aditya-singh-lollc/', summary:'Full architecture retained; exact retry contract, lost-response trace and two corrected diagrams.'},
 {id:'Q3', slug:'Q3-accuracy', title:'99.5% Accurate—and Still Wrong 500 Times', source:'https://www.linkedin.com/pulse/995-accurateand-still-wrong-500-times-aditya-singh-get5c/', summary:'Conditional denominators, sensitivity, independent adjudication and sampling uncertainty.'},
 {id:'Q4', slug:'Q4-three-minute', title:'The 3-Minute Decision That Took 3 Weeks to Ship', source:'https://www.linkedin.com/pulse/3-minute-decision-took-3-weeks-ship-aditya-singh-kmejc/', summary:'Waiting versus work, 80-hour baseline versus 60-hour counterfactual, acceptance memo and recovery.'},
];
const manifest = {schema_version:1, prepared_date:'2026-09-14', status:'review_drafts_not_applied', external_mutations:[], preservation:['original public URLs','all schedules','existing title/subtitle','featured images','publication/newsletter membership','email and paywall settings'], baseline:{path:baselinePath, sha256:sha(baseline)}, articles:[], figures:[]};
for (const spec of specs) {
  const body = spec.id === 'Q2' ? crm : marked.parse(await read(`${spec.slug}.md`));
  const html = layout(spec.title, body, spec.source);
  await write(`${spec.slug}.html`, html);
  const words = body.replace(/<[^>]+>/g,' ').trim().split(/\s+/).length;
  manifest.articles.push({...spec, preview:`${spec.slug}.html`, word_count_approx:words, body_sha256:sha(body), preview_sha256:sha(html), figures:(body.match(/<img /g)||[]).length});
}
for (const name of ['passport-enforcement','crm-unknown-outcome','crm-atomic-contract']) {
  const svg = await read(`figures/${name}.svg`);
  const output = await sharp(Buffer.from(svg), {density:192}).png().toBuffer();
  await fs.writeFile(path.join(here, `figures/${name}.png`), output);
  const meta = await sharp(output).metadata();
  manifest.figures.push({svg:`figures/${name}.svg`,png:`figures/${name}.png`,svg_sha256:sha(svg),png_sha256:sha(output),width:meta.width,height:meta.height});
}
await write('crm-change-map.json', `${JSON.stringify(edits,null,2)}\n`);
await write('manifest.json', `${JSON.stringify(manifest,null,2)}\n`);
await write('index.html', `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Four article revisions — review</title><style>${css}</style></head><body><main><div class="eyebrow">EDITORIAL REVIEW / 14 SEPTEMBER 2026</div><h1>Four stronger technical articles.</h1><p>Revised full bodies, inspectable calculations and a runnable local failure model. These are review drafts; the published LinkedIn and Medium editions remain unchanged.</p><aside class="review"><strong>Approval boundary</strong><p>Review the complete body and affected figures below. No public save, publishing, scheduling or subscriber email is included in this package.</p><a href="README.md">Change log, reproducibility and validation</a></aside>${manifest.articles.map(a=>`<section class="card"><div class="eyebrow">${a.id} / REVISED FULL ARTICLE</div><h2><a href="${a.preview}">${escape(a.title)}</a></h2><p>${a.summary}</p><div class="meta">About ${a.word_count_approx.toLocaleString('en-US')} words · ${a.figures} figures · <a href="${a.source}">original edition</a></div></section>`).join('')}<section class="card"><h2>Three corrected technical diagrams</h2><p>White background, black/blue text; vector sources and high-resolution PNG copies.</p>${manifest.figures.map(f=>`<p><a href="${f.svg}">${f.svg.split('/')[1]}</a> · <a href="${f.png}">PNG</a></p>`).join('')}</section><section class="card"><h2>Reproducible companion</h2><p><a href="protocol.py">Local transaction model</a> · <a href="test_protocol.py">Failure tests</a> · <a href="calculations.py">Calculations</a> · <a href="test_calculations.py">Arithmetic tests</a></p><p>This code does not connect to CRM, authenticate workloads or model distributed policy propagation. Passing its tests is not production certification.</p></section></main></body></html>\n`);
console.log(JSON.stringify({built:manifest.articles.map(a=>a.preview), figures:manifest.figures.length, crm_edits:edits.length}));
