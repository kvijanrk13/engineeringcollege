/** Extract every numbered figure and formal pseudocode algorithm from Han, Kamber & Pei (3e). */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import process from 'node:process';
import * as pdfjs from 'pdfjs-dist/legacy/build/pdf.mjs';
import mupdf from 'mupdf';
import sharp from 'sharp';

const pdfPath = path.resolve(process.argv[2] || '');
const projectRoot = path.resolve(process.argv[3] || path.join(import.meta.dirname, '..'));
if (!fs.existsSync(pdfPath)) throw new Error(`PDF not found: ${pdfPath}`);
const root = path.join(projectRoot, 'static', 'academics', 'dm-textbook');
const imageRoot = path.join(root, 'images');
fs.mkdirSync(imageRoot, { recursive: true });

const chapters = {
  1: 'Introduction', 2: 'Getting to Know Your Data', 3: 'Data Preprocessing',
  4: 'Data Warehousing and OLAP', 5: 'Data Cube Technology',
  6: 'Mining Frequent Patterns, Associations, and Correlations',
  7: 'Advanced Pattern Mining', 8: 'Classification: Basic Concepts',
  9: 'Classification: Advanced Methods', 10: 'Cluster Analysis: Basic Concepts',
  11: 'Advanced Cluster Analysis', 12: 'Outlier Detection', 13: 'Data Mining Trends and Research Frontiers',
};
const rawPdf = fs.readFileSync(pdfPath);
const renderDocument = mupdf.Document.openDocument(new Uint8Array(rawPdf), 'application/pdf');
const pdf = await pdfjs.getDocument({ data: new Uint8Array(rawPdf), disableWorker: true }).promise;
const pages = [];

function linesFrom(items) {
  const rows = [];
  for (const item of items) {
    if (!item.str?.trim()) continue;
    const y = item.transform[5];
    let row = rows.find(candidate => Math.abs(candidate.y - y) < 2.4);
    if (!row) { row = { y, items: [] }; rows.push(row); }
    row.items.push(item);
  }
  return rows.sort((a, b) => b.y - a.y).map(row => ({
    y: row.y,
    text: row.items.sort((a, b) => a.transform[4] - b.transform[4]).map(item => item.str).join(' ').replace(/\s+/g, ' ').trim(),
  }));
}

for (let number = 1; number <= pdf.numPages; number += 1) {
  const page = await pdf.getPage(number);
  const content = await page.getTextContent();
  const lines = linesFrom(content.items);
  pages.push({ number, width: page.view[2], height: page.view[3], lines, text: lines.map(line => line.text).join(' ') });
  if (number % 100 === 0) console.log(`Inventoried ${number}/${pdf.numPages} pages`);
}

const candidates = [];
for (const page of pages) {
  for (let index = 0; index < page.lines.length; index += 1) {
    const line = page.lines[index];
    const match = line.text.match(/^Figure\s+(\d{1,2})\.(\d{1,3})\s+(.+)/i);
    if (!match) continue;
    let caption = match[3];
    for (let next = index + 1; next < Math.min(index + 4, page.lines.length); next += 1) {
      const more = page.lines[next];
      if (more.y > line.y || /^\d+(?:\.\d+)+\s/.test(more.text) || /^(?:Source|Example)\s*:/i.test(more.text)) break;
      if (line.y - more.y > 34) break;
      caption += ` ${more.text}`;
    }
    caption = caption.replace(/\s+/g, ' ').trim();
    candidates.push({ type: 'diagram', chapter: Number(match[1]), number: `${match[1]}.${match[2]}`, page: page.number, y: line.y, title: caption });
  }
  const marker = page.lines.find(line => /^Algorithm\s*:/i.test(line.text));
  if (marker) {
    const name = marker.text.replace(/^Algorithm\s*:\s*/i, '').split(/\.(?:\s|$)/)[0].trim();
    if (name && !/analysis and implementation/i.test(name)) candidates.push({ type: 'algorithm', chapter: null, number: name, page: page.number, y: marker.y, title: name });
  }
}

// Remove duplicate caption detections while retaining the canonical earliest page.
const unique = [...new Map(candidates.map(item => [`${item.type}:${item.number}`, item])).values()];
const rendered = new Map();
async function renderPage(number) {
  if (rendered.has(number)) return rendered.get(number);
  const scale = 2;
  const page = renderDocument.loadPage(number - 1);
  const pixmap = page.toPixmap([scale, 0, 0, scale, 0, 0], mupdf.ColorSpace.DeviceRGB, false);
  const buffer = Buffer.from(pixmap.asPNG());
  rendered.set(number, { buffer, width: pixmap.getWidth(), height: pixmap.getHeight(), scale });
  pixmap.destroy(); page.destroy();
  return rendered.get(number);
}

const records = [];
for (let index = 0; index < unique.length; index += 1) {
  const item = unique[index];
  const pageInfo = pages[item.page - 1];
  if (!item.chapter) {
    const heading = pageInfo.text.match(/Chapter\s+(\d{1,2})/i);
    item.chapter = heading ? Number(heading[1]) : Number(pageInfo.text.match(/^(\d{1,2})\./)?.[1] || 0);
    if (!item.chapter) {
      const nearest = [...candidates].reverse().find(other => other.page <= item.page && other.chapter);
      item.chapter = nearest?.chapter || 1;
    }
  }
  const renderedPage = await renderPage(item.page);
  const captionTop = Math.round((pageInfo.height - item.y) * renderedPage.scale);
  const top = Math.max(0, captionTop - Math.round(renderedPage.height * (item.type === 'algorithm' ? 0.04 : 0.44)));
  const bottom = Math.min(renderedPage.height, captionTop + Math.round(renderedPage.height * (item.type === 'algorithm' ? 0.72 : 0.055)));
  const slug = item.type === 'diagram' ? `figure-${item.number.replace('.', '-')}` : `algorithm-${item.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')}`;
  const file = `${slug}-p${String(item.page).padStart(3, '0')}.webp`;
  const destination = path.join(imageRoot, file);
  await sharp(renderedPage.buffer).extract({ left: 0, top, width: renderedPage.width, height: Math.max(80, bottom - top) })
    .resize({ width: 1500, withoutEnlargement: true }).webp({ quality: 86 }).toFile(destination);
  const cleaned = item.title.replace(/\s+(?:Source|Example)\s*:.*$/i, '').slice(0, 280);
  records.push({
    id: slug, type: item.type, chapter: item.chapter, chapter_title: chapters[item.chapter] || `Chapter ${item.chapter}`,
    number: item.number, title: cleaned, pdf_page: item.page,
    image: `academics/dm-textbook/images/${file}`,
    alt: `${item.type === 'diagram' ? `Figure ${item.number}` : `Algorithm ${item.title}`} — ${cleaned}`,
    keywords: [...new Set(`${item.title} ${chapters[item.chapter] || ''}`.toLowerCase().match(/[a-z0-9]+/g) || [])],
    sha256: crypto.createHash('sha256').update(fs.readFileSync(destination)).digest('hex'),
  });
  if ((index + 1) % 25 === 0) console.log(`Rendered ${index + 1}/${unique.length} assets`);
}

const manifest = {
  source: path.basename(pdfPath), title: 'Data Mining: Concepts and Techniques, Third Edition',
  authors: 'Jiawei Han, Micheline Kamber, Jian Pei', page_count: pdf.numPages,
  generated_at: new Date().toISOString(), algorithm_count: records.filter(x => x.type === 'algorithm').length,
  diagram_count: records.filter(x => x.type === 'diagram').length,
  chapters: Object.entries(chapters).map(([number, title]) => ({ number: Number(number), title, count: records.filter(x => x.chapter === Number(number)).length })),
  items: records,
};
const keep = new Set(records.map(record => path.basename(record.image)));
for (const file of fs.readdirSync(imageRoot)) if (!keep.has(file)) fs.unlinkSync(path.join(imageRoot, file));
fs.writeFileSync(path.join(root, 'manifest.json'), JSON.stringify(manifest, null, 2));
fs.writeFileSync(path.join(root, 'page-audit.json'), JSON.stringify({ source: manifest.source, page_count: pdf.numPages, pages: pages.map(page => ({ pdf_page: page.number, inventoried: true })) }, null, 2));
console.log(`Created ${manifest.algorithm_count} algorithms and ${manifest.diagram_count} diagrams from ${pdf.numPages} pages.`);
