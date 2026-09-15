// Local review build. No publishing, browser sessions or API clients.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
const dir=path.dirname(fileURLToPath(import.meta.url));
const mod=process.env.CODEX_NODE_MODULES || '/Users/adityasingh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const req=createRequire(path.join(mod,'_newsletter.cjs'));
const sharp=req('sharp'); const {marked}=req('marked');
const figures=JSON.parse(await fs.readFile(path.join(dir,'figures.json'),'utf8'));
const render=process.argv.includes('--figures-only');
for(const f of figures){
  const svg=await fs.readFile(path.join(dir,'figures',f.file+'.svg'));
  await sharp(svg,{density:144}).png().toFile(path.join(dir,'figures',f.file+'.png'));
}
// Contact sheet is a generated gallery, not a substitute for full-size visual inspection.
const tw=768,th=544,gap=32;
const composites=[];
for(let i=0;i<figures.length;i++){
  const input=await sharp(path.join(dir,'figures',figures[i].file+'.png')).resize(tw,th).png().toBuffer();
  composites.push({input,left:gap+(i%3)*(tw+gap),top:gap+Math.floor(i/3)*(th+gap)});
}
await sharp({create:{width:3*tw+4*gap,height:4*th+5*gap,channels:3,background:'#ffffff'}}).composite(composites).png().toFile(path.join(dir,'contact-sheet.png'));
if(render){console.log('Rendered 12 high-resolution PNGs and contact sheet');process.exit(0);}
let md=await fs.readFile(path.join(dir,'newsletter.md'),'utf8');
let body=marked.parse(md);
for(const f of figures){
  const token=`<p>[[EXHIBIT:${f.number}]]</p>`;
  if(body.split(token).length!==2) throw Error('Missing or duplicate exhibit anchor '+f.number);
  body=body.replace(token,`<figure id="exhibit-${f.number}"><a href="figures/${f.file}.png" target="_blank" aria-label="Open exhibit ${f.number} full-size"><img src="figures/${f.file}.png" width="3840" height="2720" alt="${f.caption}" loading="lazy"></a><figcaption><b>Exhibit ${f.number}.</b> ${f.caption} <a href="figures/${f.file}.svg">Editable SVG</a> · <a href="figures/${f.file}.png">Full-resolution PNG</a></figcaption></figure>`);
}
body=body.replaceAll('loading="lazy"','loading="eager"').replaceAll('<table>','<div class="table-scroll" tabindex="0" role="region" aria-label="Scrollable metric table"><table>').replaceAll('</table>','</table></div>');
const nav=figures.map(f=>`<a href="#exhibit-${f.number}">${String(f.number).padStart(2,'0')} ${f.title}</a>`).join('');
const html=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AI Agents Need an Exception Budget — technical newsletter</title><style>
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#fff;color:#101828;font:20px/1.8 Georgia,serif}a{color:#1457c5;text-underline-offset:3px}header{border-bottom:1px solid #bfd2ef;padding:22px 5vw;font:14px/1.6 Arial,sans-serif;color:#1457c5;display:flex;justify-content:space-between;gap:22px}main{max-width:1500px;margin:0 auto;padding:52px 28px 100px}article>p,article>h1,article>h2,article>h3,article>ul,article>ol,article>blockquote,article>pre,article>.table-scroll,article>hr{max-width:890px;margin-left:auto;margin-right:auto}h1,h2,h3{font-family:Arial,sans-serif;line-height:1.16;letter-spacing:-.7px}h1{font-size:58px;margin-top:20px;margin-bottom:25px}h2{font-size:36px;margin-top:76px;margin-bottom:25px}h3{font-size:25px;margin-top:40px}article>p{margin-top:1em;margin-bottom:1em}blockquote{border-left:4px solid #1457c5;padding:15px 25px;font-size:19px}blockquote p{margin:0}figure{margin:42px 0 58px;padding:20px 0;border-top:1px solid #bfd2ef;border-bottom:1px solid #bfd2ef}figure img{display:block;width:100%;height:auto}figcaption{max-width:1080px;margin:18px auto 5px;font:15px/1.65 Arial,sans-serif}pre{overflow:auto;border:1px solid #bfd2ef;padding:25px;font:15px/1.65 Menlo,Consolas,monospace}code{font-size:.86em}pre code{font-size:inherit}table{width:100%;border-collapse:collapse;font:16px/1.6 Arial,sans-serif}th,td{padding:14px;border-bottom:1px solid #bfd2ef;text-align:left;vertical-align:top}th{color:#1457c5}table th:first-child{min-width:160px}.table-scroll{overflow-x:auto}li{margin:10px 0}hr{border:0;border-top:1px solid #bfd2ef;margin-top:45px;margin-bottom:45px}.review{max-width:890px;margin:0 auto 40px;padding:20px 25px;border:1px solid #1457c5;font:15px/1.65 Arial,sans-serif}.review strong{color:#1457c5}details{max-width:890px;margin:0 auto 35px;font:15px/1.6 Arial,sans-serif}summary{cursor:pointer;color:#1457c5;font-weight:bold}nav{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:18px 0}footer{border-top:1px solid #bfd2ef;padding:30px 5vw;font:14px/1.7 Arial,sans-serif}
@media(max-width:650px){body{font-size:18px}main{padding:30px 18px 65px}header{display:block}h1{font-size:38px}h2{font-size:28px}h3{font-size:23px}figure{margin-left:-8px;margin-right:-8px}figcaption{padding:0 9px}table{min-width:680px}nav{grid-template-columns:1fr}pre{font-size:13px;padding:14px}.review{padding:15px}blockquote{padding:12px 17px}}
@media(max-width:650px){header b,header span{display:block}header span{margin-top:7px}}
@media print{header,details,.review{display:none}main{padding:0}h2{break-after:avoid}figure{break-inside:avoid}body{font-size:14px}h1{font-size:38px}h2{font-size:26px}}</style></head><body><header><b>THE OPERATING AI LEDGER / TECHNICAL NEWSLETTER</b><span>Aditya Singh · 14 September 2026 · Review edition</span></header><main><aside class="review"><strong>DRAFT FOR REVIEW — NOT PUBLISHED OR SCHEDULED</strong><br>10 detailed architecture plates + 2 statistical exhibits. Every numeric operating example is hypothetical and reproducible; no customer results are claimed. Click any image for its full-resolution version.<br><a href="newsletter.md">Markdown manuscript</a> · <a href="calculations.json">Calculation outputs</a> · <a href="README.md">Methods and validation</a> · <a href="contact-sheet.png">All 12 exhibits</a></aside><details><summary>Architecture and statistical exhibit index</summary><nav>${nav}</nav></details><article>${body}</article></main><footer>Local editorial review package. Existing LinkedIn / Medium bodies, media, schedules and settings are unchanged.</footer></body></html>`;
await fs.writeFile(path.join(dir,'index.html'),html);
const artifactNames=['newsletter.md','index.html','analytics.py','test_analytics.py','calculations.json','draw_figures.py','build.mjs','figures.json','contact-sheet.png',...figures.flatMap(f=>['figures/'+f.file+'.svg','figures/'+f.file+'.png'])];
const files=[];
for(const name of artifactNames){const bytes=await fs.readFile(path.join(dir,name));files.push({name,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')});}
await fs.writeFile(path.join(dir,'manifest.json'),JSON.stringify({status:'draft-not-published',figure_count:figures.length,architecture_count:10,statistical_count:2,files},null,2)+'\n');
console.log('Built newsletter preview, 12 PNGs, contact sheet and content manifest');
