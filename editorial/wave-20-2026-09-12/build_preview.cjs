// Local editorial preview only: no network, account access, scheduling or publication.
// Usage: node build_preview.cjs <bundled-node-modules-path>
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const crypto = require('node:crypto');

async function main() {
  const modules = process.argv[2];
  if (!modules) throw new Error('Provide the installed dependency directory; no installation is performed.');
  const sharp = require(require.resolve('sharp', {paths:[modules]}));
  const {marked} = await import(pathToFileURL(require.resolve('marked', {paths:[modules]})));
  const root = path.resolve(__dirname, '../..');
  const manifest = JSON.parse(fs.readFileSync(path.join(__dirname, 'manifest.json')));
  const out = path.join(__dirname, 'preview');
  fs.mkdirSync(out, {recursive:true});
  const esc = x => String(x ?? '').replace(/[&<>\"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]));
  const hash = x => crypto.createHash('sha256').update(x).digest('hex');
  const sheet = `body{margin:0;background:#fff;color:#111;font:19px/1.65 system-ui,sans-serif}main{max-width:1020px;margin:48px auto;padding:0 28px}h1{line-height:1.15;font-size:44px}h2{color:#155cce;line-height:1.3;margin-top:2em}a{color:#155cce}img{width:100%;height:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f5f8ff;padding:24px;font-size:15px}table{border-collapse:collapse;width:100%;font-size:16px}th,td{border:1px solid #a7bde3;padding:12px;text-align:left;vertical-align:top}figcaption,.status{font-size:15px}.status{border:2px solid #155cce;padding:18px;color:#155cce}blockquote{border-left:4px solid #155cce;margin-left:0;padding-left:22px}code{overflow-wrap:anywhere}`;
  const page = (title,html) => `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)}</title><style>${sheet}</style><main><p class="status">EDITORIAL REVIEW ONLY · Not published or scheduled on Medium or LinkedIn</p>${html}</main></html>`;
  const launch = fs.readFileSync(path.join(root,'editorial/next-wave/linkedin-launch-drafts.md'),'utf8');
  const rows=[]; const records=[]; const posts=[];
  let date = new Date('2026-10-12T00:00:00Z');
  for (const [index,item] of [...manifest.existing,...manifest.new].entries()) {
    const source = fs.readFileSync(path.join(root,item.source),'utf8');
    let title,body,topics,post,figures,wordCount;
    if (index<12) {
      const s=JSON.parse(source); title=s.title; topics=s.tags; figures=s.blocks.filter(b=>b.type==='figure').length; wordCount=s.wordCount;
      body=`<h1>${esc(s.title)}</h1><p>${esc(s.subtitle || s.description)}</p>`+s.blocks.map(b=>{
        if(b.type==='figure') return `<figure><img src="../../../${esc(b.src)}" alt="${esc(b.alt)}"><figcaption>${esc(b.caption)}</figcaption></figure>`;
        if(b.type==='html') return `<${b.tag}>${b.html}</${b.tag}>`;
        if(b.type==='table') return `<table><thead><tr>${b.headers.map(v=>`<th>${esc(v)}</th>`).join('')}</tr></thead><tbody>${b.rows.map(row=>`<tr>${row.map(v=>`<td>${esc(v)}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
        throw new Error('Unsupported block type: '+b.type);
      }).join('\n');
      const section=launch.split('## '+item.linkedinId+' — ')[1];
      if(!section) throw new Error('Missing existing LinkedIn draft '+item.linkedinId);
      post=section.split('\n## ')[0].split('\n').filter(l=>l.startsWith('>')).map(l=>l.replace(/^> ?/,'')).join('\n').trim();
      // Clarify illustrative quantities only in this new approval package; originals unchanged.
      if(item.linkedinId==='NW-LI-05') post=post.replace('Trace coverage can be 99.99%', 'In an illustrative scorecard, trace coverage can be 99.99%');
      if(item.linkedinId==='NW-LI-07') post=post.replace('The workers can stop in 74 seconds', 'In the illustrative scenario, workers stop in 74 seconds');
      if(item.linkedinId==='NW-LI-02') post=post.replace('It rarely does.', 'That assumption needs to be tested against current effect and authority state.');
    } else {
      title=item.title; topics=item.topics; post=item.linkedinDraft; figures=1; wordCount=source.trim().split(/\s+/).length;
      const svg=path.join(root,item.hero), png=svg.replace(/\.svg$/,'.png');
      await sharp(svg).png().toFile(png);
      body=marked.parse(source).replaceAll('src="media/','src="../drafts/media/').replaceAll('.svg"','.png"');
    }
    if(post.length>2800) throw new Error('Leave room for verified Medium URL: '+item.id);
    const mediumDate=date.toISOString().slice(0,10);
    const liDate=new Date(date.getTime()+86400000).toISOString().slice(0,10);
    fs.writeFileSync(path.join(out,item.slug+'.html'),page(title,body));
    rows.push(`| ${item.id} | [${title}](preview/${item.slug}.html) | ${index<12?'Existing GitHub-only draft':'New full-text draft'} | ${mediumDate} 14:00 | ${liDate} 08:45 |`);
    posts.push(`## ${item.id} — ${title}\n\nMedium proposal: ${mediumDate}, 14:00 IST. LinkedIn proposal: ${liDate}, 08:45 IST.\n\n${post}\n\n**Finalization gate:** append the verified public Medium link and approve the completed animated media, then obtain exact action-time approval. No native mentions proposed.\n`);
    records.push({id:item.id,title,source:item.source,sourceSha256:hash(source),linkedinTextSha256:hash(post),wordCount,figureCount:figures,topics,mediumDate,linkedinDate:liDate,canonical:index<12?`https://singhaditya21.github.io/Medium/articles/${item.slug}/`:null,subscriberEmail:true,paywall:false,publication:null,mediumUrl:null,status:'draft_human_review_required'});
    date=new Date(date.getTime()+(index%2===0?3:4)*86400000);
  }
  if(records.length!==20 || new Set(records.map(r=>r.title)).size!==20) throw new Error('Expected twenty distinct titles.');
  const intro=`# Twenty-story release package\n\nStatus: **20 full-text story drafts assembled, not 20 new publications.** Twelve already existed as GitHub Pages editorial drafts; eight are newly written local drafts. Twenty corresponding LinkedIn text drafts are included. Existing schedules are unchanged.\n\nLive inventory checked 12 September 2026: Medium 13 published plus one scheduled (Standing Role, September 14); LinkedIn 11 scheduled through October 9. The twelve-story October calendar was a proposal, not a live schedule.\n\n## Proposed calendar, Asia/Kolkata\n\n| ID | Story preview | Draft origin | Medium proposal | LinkedIn proposal |\n|---|---|---|---|---|\n${rows.join('\n')}\n\n## Approval and quality gates\n\n- Review every body and its original analysis. Examples are labelled synthetic or illustrative; no personal experience has been invented. New drafts contain roughly 700–800 words each, one architecture figure, a contract or code sketch, failure tests and primary-source references. They are editorial drafts, not independently tested production implementations.\n- Existing twelve drafts retain their source bodies and three figures each; their source-by-source technical and visual review remains required. Their existing release JSON has subscriberEmail=false, so it must not be executed as the new publish configuration. The proposed setting below is explicitly on.\n- Proposed Medium settings: Aditya Singh personal profile, public, no publication submission, five topics as listed in metadata, subscriber email ON, paywall OFF, opening AI disclosure and labelled figures. Existing twelve retain their GitHub Pages canonical; new eight need approved archive publication or an explicit Medium-first canonical choice.\n- Proposed LinkedIn settings: Anyone, comments enabled, no native mentions. The final public Medium link is not yet known. [All twenty text drafts](linkedin-posts.md) must be finalized with that link. Existing animated-media preference is preserved: MP4/GIF launch media is still to be built and approved; current static diagrams are source assets, not approved replacements for animation.\n- This is a ten-week editorial proposal, not a bulk-send commitment or a claim that all dates fit today's platform scheduling horizon. Use rolling scheduling windows and recheck performance and collisions before each release.\n- No Medium import, publish, subscriber email, LinkedIn post or schedule was executed in this task. No release-state or receipt files claim otherwise.\n\n## What is ready and what remains\n\nReady: source inventory, twenty story bodies, twenty LinkedIn text drafts, eight new SVG/PNG architecture assets, local HTML previews and five exact LinkedIn comment drafts in the engagement queue.\n\nRemaining: human technical/editorial review; full source and visual QA of the existing twelve; refinement of the new shorter drafts where desired; animated launch-media production and QA; public canonical/Medium URL resolution; exact publishing settings approval; visible publication verification. Approval of the comment batch does not approve any story or post.\n\nThe [manifest](manifest.json) is preparation data only, outside the production data and release directories. The Pages staging script does not deploy this folder. [Validation inventory](review-inventory.json) records source hashes for review; hashes do not constitute technical validation.\n`;
  fs.writeFileSync(path.join(__dirname,'README.md'),intro);
  fs.writeFileSync(path.join(__dirname,'linkedin-posts.md'),'# Twenty LinkedIn companion drafts\n\nDrafts only, not approved or scheduled. M01–M12 reuse the earlier next-wave copy, with illustrative-number clarification for observability/incident copy and removal of an unsupported retry-frequency assertion. M13–M20 are new. No original post, schedule or approved body was edited.\n\n'+posts.join('\n'));
  fs.writeFileSync(path.join(__dirname,'review-inventory.json'),JSON.stringify(records,null,2)+'\n');
  fs.writeFileSync(path.join(__dirname,'preview.html'),page('Twenty-story editorial review',marked.parse(intro)));
  console.log(JSON.stringify({stories:records.length,newStories:manifest.new.length,linkedinDrafts:posts.length,figures:records.reduce((s,r)=>s+r.figureCount,0),scheduled:0,published:0}));
}
main().catch(e=>{console.error(e.message);process.exitCode=1;});
