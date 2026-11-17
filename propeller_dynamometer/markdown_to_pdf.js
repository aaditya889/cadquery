// Markdown document -> A4 PDF: formulas typeset with KaTeX, a contents list from the ## headings, page numbers in the
// footer, links to other documents rewritten to their PDF titles, links to scripts reduced to their text.
// The vendor edition of the dyno manufacturing package (--vendor-edition) drops what is only for us: the "Good answer"
// column, the answer log, our open decisions, the in-house assembly, the not-yet-designed list, internal file references;
// the remaining sections are renumbered and every § reference with them. It stops if the source no longer has a text it
// expects to edit, so the two editions cannot drift apart silently.
// Usage: node markdown_to_pdf.js <input.md> <output.pdf> [--vendor-edition]   (build_pdfs_and_vendor_zip.sh runs it)
// Needs markdown-it and @vscode/markdown-it-katex (an npx cache; set MARKDOWN_NODE_MODULES to another node_modules) and
// google-chrome.
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

const MODULES = process.env.MARKDOWN_NODE_MODULES || '/home/aaditya/.npm/_npx/cfa50097a276e20d/node_modules';
const MarkdownIt = require(path.join(MODULES, 'markdown-it'));
const katex = require(path.join(MODULES, '@vscode/markdown-it-katex')).default;
const KATEX_CSS = path.join(MODULES, 'katex/dist/katex.min.css');

// other documents a link may point to: file name -> title of its PDF
const TITLES = {
  'propeller_dynamometer_theory.md': 'Propeller dynamometer: theory',
  'propeller_dynamometer_design.md': 'Propeller dynamometer: design',
  'propeller_dynamometer_manufacturing_package.md': 'Propeller dynamometer: manufacturing package',
  'battery_cell_rig_theory.md': 'Battery cell rig: theory',
};

function vendorEdition(src) {
  const edit = (from, to) => {
    if (!src.includes(from)) throw new Error(`vendor edition: text not found, update markdown_to_pdf.js: ${from.slice(0, 70)}`);
    src = src.split(from).join(to);
  };
  const drop = (title) => {                        // a whole ## section, up to the next ## heading
    const re = new RegExp(`\\n## ${title.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\n[\\s\\S]*?(?=\\n## |$)`);
    if (!re.test(src)) throw new Error(`vendor edition: section not found: ${title}`);
    src = src.replace(re, '\n');
  };
  const dropColumn = (header) => {                 // a column from every table whose header row has it
    let n = 0;
    src = src.replace(/(^\|.*\|\n\|[-| :]+\|\n(?:\|.*\|\n?)*)/gm, (table) => {
      const rows = table.trimEnd().split('\n').map((r) => r.trim().slice(1, -1).split('|').map((c) => c.trim()));
      const i = rows[0].indexOf(header);
      if (i < 0) return table;
      if (rows.some((r) => r.length !== rows[0].length)) throw new Error(`vendor edition: uneven table under ${header}`);
      n++;
      return rows.map((r) => '| ' + r.filter((_, j) => j !== i).join(' | ') + ' |').join('\n') + '\n';
    });
    if (!n) throw new Error(`vendor edition: no table has the column ${header}`);
  };
  edit('# Prop dyno and cell rig: manufacturing package', '# Propeller dynamometer and cell rig: manufacturing package');
  src = src.replace(/\nWhat every vendor needs[\s\S]*?\n---\n/, `
This package asks for quotations to make, finish, inspect and deliver the parts of our propeller dynamometer (a test
stand that measures a propeller's thrust and torque) and its battery cell and pack rig. Each requirement comes with the
reason for it, so you can tell us where a different method would serve the same purpose better.

**In this package**

- This document: the processes and terms we use (§2), the machine in numbers (§3), the parts lists (§4), the requirements
  (§5), the acceptance tests (§7), our questions for each industry (§8) and the cell-rig items (§11).
- The drawing set (one sheet per part we make or outsource: views, material, process, quantity, tolerances, hole table).
- One STEP file per part, and the assembly STEP, for each of the two configurations (large head and small head). The STEP
  file is the master geometry; the drawing sheet states what the STEP cannot (tolerances, finishes, threads).
- \`parts.csv\`, \`fasteners.csv\` and \`holes.csv\` for each configuration: the same lists as §4, and every hole's position
  measured from the part's bounding-box corner.

**How to reply:** answer the questions for your industry in §8 by their IDs, and quote each part or weldment you can make,
itemised, with lead time and delivery to our site. Requirements marked **P** are proposals: tell us if you would do it
differently and why.

Drawings and models dated 4 Nov 2026.

---
`);
  drop('6. Assembly (in-house)');
  drop('9. Answer log');
  drop('10. Our open decisions');
  drop('12. Not yet designed');
  edit('| Item | Value | Source |', '| Item | Value | Our source |');   // §3 only: there "Source" means our scripts
  dropColumn('Our source');
  dropColumn('Good answer');
  edit('Status: **D** decided, **P** proposed (confirm with the vendor\'s answer), **O** open (§10).',
       'Status: **D** fixed; **P** proposed: tell us if you would do it differently and why.');
  edit('| Calibration | design doc §7: weights', '| Calibration | weights');
  edit('| Tap test | design doc §7: impulse', '| Tap test | impulse');
  edit('## 8. Questions for vendors, by industry', '## 8. Questions, by industry: please answer those for your industry, by ID');
  edit('Everything here is bought, fabricated from simple drawings, or electronics; the design is in\n' +
       '[design §12](propeller_dynamometer_design.md#12-cell-and-pack-rig).',
       'Everything here is bought, fabricated from simple drawings, or electronics.');
  edit('| make (CNC) | — (design is a gap, §12) |', '| made by us | — |');
  edit('| electronics (gap, §12) + heat-sink supplier |', '| electronics (by us) + heat-sink supplier |');
  // renumber the remaining sections and every § reference to them (every text above uses the source's numbers)
  const kept = [...src.matchAll(/^## (\d+)\. /gm)].map((m) => m[1]);
  const map = Object.fromEntries(kept.map((n, i) => [n, String(i + 1)]));
  src = src.replace(/^(#{2,4}) (\d+)((?:\.\d+)*)([. ])/gm, (_, h, n, rest, end) => `${h} ${map[n]}${rest}${end}`);
  src = src.replace(/§(\d+)/g, (whole, n) => {
    if (!map[n]) throw new Error(`vendor edition: reference to a dropped section: ${whole}`);
    return '§' + map[n];
  });
  for (const word of ['design doc', 'dyno doc', '.py', 'Good answer', 'Answer log', 'open decisions'])
    if (src.includes(word)) throw new Error(`vendor edition: internal text left: ${word}`);
  return src;
}

function slug(text) {                               // GitHub's heading anchors, so #links keep working
  return text.trim().toLowerCase().replace(/[^\p{L}\p{N}\- ]/gu, '').replace(/ /g, '-');
}

function render(src) {
  src = src.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (whole, text, target) => {
    if (/^(https?:|mailto:|#)/.test(target)) return whole;
    const file = path.basename(target.split('#')[0]);
    if (TITLES[file]) return `${text} (document *${TITLES[file]}*)`;
    return text;                                    // scripts and other files: not part of a PDF
  });
  const md = new MarkdownIt({ html: true, typographer: false });
  md.use(katex);
  const headings = [];
  md.core.ruler.push('anchors', (state) => {
    state.tokens.forEach((t, i) => {
      if (t.type !== 'heading_open') return;
      const text = state.tokens[i + 1].content;
      const id = slug(text);
      t.attrSet('id', id);
      if (t.tag === 'h2') headings.push([id, text]);
    });
  });
  const body = md.render(src);
  const title = (src.match(/^# (.+)$/m) || [, 'Document'])[1];
  const toc = headings.length > 2 ? '<nav><b>Contents</b><ul>' +
    headings.map(([id, t]) => `<li><a href="#${id}">${md.renderInline(t)}</a></li>`).join('') + '</ul></nav>' : '';
  const html = body.replace(/(<h1[^>]*>[\s\S]*?<\/h1>)/, `$1${toc}`)
    .replace(/<table>([\s\S]*?<\/tr>)/g, (whole, head) =>        // 8 or more columns: on a landscape page
      (head.match(/<th/g) || []).length >= 8 ? `<table class="wide">${head}` : whole);
  return { title, html: `<!doctype html><html><head><meta charset="utf-8"><title>${title}</title>
<link rel="stylesheet" href="file://${KATEX_CSS}">
<style>
  body { font-family: "Noto Sans", "DejaVu Sans", sans-serif; font-size: 10pt; line-height: 1.4; color: #111; }
  h1 { font-size: 18pt; margin: 0 0 8pt; } h2 { font-size: 13pt; margin-top: 18pt; break-after: avoid; }
  h3 { font-size: 11pt; break-after: avoid; } h4 { font-size: 10pt; break-after: avoid; }
  nav { border: 1px solid #ccc; padding: 6pt 10pt; margin: 8pt 0 14pt; font-size: 9pt; }
  nav ul { margin: 4pt 0 0; padding-left: 0; list-style: none; }
  nav a { color: #111; text-decoration: none; } a { color: #1a4f9c; }
  table { border-collapse: collapse; width: 100%; font-size: 7.5pt; margin: 6pt 0; }
  th, td { border: 1px solid #bbb; padding: 2pt 4pt; vertical-align: top; overflow-wrap: break-word; hyphens: manual; }
  @page landscape { size: A4 landscape; }
  table.wide { page: landscape; font-size: 7pt; }
  table.wide td:first-child, table.wide td:nth-child(3) { white-space: nowrap; }
  th { background: #eee; } tr { break-inside: avoid; }
  code { font-family: "DejaVu Sans Mono", monospace; font-size: 8.5pt; background: #f3f3f3; padding: 0 2pt; }
  pre { background: #f3f3f3; padding: 6pt; font-size: 8pt; overflow-wrap: anywhere; white-space: pre-wrap; }
  pre code { background: none; padding: 0; }
  .katex { font-size: 1.05em; } .katex-display { margin: 6pt 0; overflow: hidden; }
  hr { border: none; border-top: 1px solid #ccc; margin: 12pt 0; }
</style></head><body>${html}</body></html>` };
}

async function printToPdf(htmlFile, pdfFile, title) {
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'chrome-pdf-'));
  const chrome = spawn('google-chrome', ['--headless=new', '--remote-debugging-port=0', `--user-data-dir=${profile}`,
    '--no-first-run', '--allow-file-access-from-files', 'about:blank'], { stdio: 'ignore', detached: true });
  try {
    const portFile = path.join(profile, 'DevToolsActivePort');
    for (let i = 0; i < 100 && !fs.existsSync(portFile); i++) await new Promise((r) => setTimeout(r, 100));
    const port = fs.readFileSync(portFile, 'utf8').split('\n')[0];
    const pages = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
    const ws = new WebSocket(pages.find((p) => p.type === 'page').webSocketDebuggerUrl);
    await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
    let id = 0;
    const waiting = {}, events = {};
    ws.onmessage = (m) => {
      const d = JSON.parse(m.data);
      if (d.id && waiting[d.id]) { waiting[d.id](d); delete waiting[d.id]; }
      if (d.method && events[d.method]) events[d.method]();
    };
    const send = (method, params = {}) => new Promise((r) => { waiting[++id] = r; ws.send(JSON.stringify({ id, method, params })); });
    await send('Page.enable');
    const loaded = new Promise((r) => { events['Page.loadEventFired'] = r; });
    await send('Page.navigate', { url: 'file://' + path.resolve(htmlFile) });
    await loaded;
    await send('Runtime.evaluate', { expression: 'document.fonts.ready', awaitPromise: true });
    const esc = title.replace(/&/g, '&amp;').replace(/</g, '&lt;');
    const res = await send('Page.printToPDF', {
      paperWidth: 8.27, paperHeight: 11.69, marginTop: 0.6, marginBottom: 0.7, marginLeft: 0.6, marginRight: 0.6,
      printBackground: true, displayHeaderFooter: true, headerTemplate: '<span></span>',
      footerTemplate: `<div style="font-size:7pt;width:100%;text-align:center;color:#666">${esc} · page ` +
        '<span class="pageNumber"></span> of <span class="totalPages"></span></div>',
    });
    if (res.error) throw new Error(res.error.message);
    fs.writeFileSync(pdfFile, Buffer.from(res.result.data, 'base64'));
    ws.close();
  } finally {
    // Chrome's helper processes outlive the main one: stop the whole process group, then remove the profile
    await new Promise((r) => { chrome.once('exit', r); try { process.kill(-chrome.pid, 'SIGTERM'); } catch { r(); } setTimeout(r, 5000); });
    await new Promise((r) => setTimeout(r, 500));
    try { fs.rmSync(profile, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 }); }
    catch (e) { console.error(`note: could not remove the temporary Chrome profile ${profile}: ${e.message}`); }
  }
}

(async () => {
  const [input, output, flag] = process.argv.slice(2);
  if (!input || !output) { console.error('usage: node markdown_to_pdf.js <input.md> <output.pdf> [--vendor-edition]'); process.exit(2); }
  let src = fs.readFileSync(input, 'utf8');
  if (flag === '--vendor-edition') src = vendorEdition(src);
  const { title, html } = render(src);
  const errors = (html.match(/katex-error/g) || []).length;
  const tmp = path.join(os.tmpdir(), `markdown-to-pdf-${process.pid}.html`);
  fs.writeFileSync(tmp, html);
  try { await printToPdf(tmp, output, title); } finally { fs.rmSync(tmp, { force: true }); }
  console.log(`${output}  (${title}${errors ? `; ${errors} formulas failed to typeset` : ''})`);
})().catch((e) => { console.error(e.message); process.exit(1); });
