/**
 * Audits a scanned COA textbook and creates the static diagram library.
 * Usage: node extract_coa_diagrams.mjs <pdf> [project-root]
 */
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import crypto from 'node:crypto';
import * as pdfjsLib from 'pdfjs-dist/legacy/build/pdf.mjs';
import sharp from 'sharp';
import { createWorker } from 'tesseract.js';
import { buildWorkingSteps } from './coa_working_steps.mjs';

const pdfPath = path.resolve(process.argv[2] || '');
const projectRoot = path.resolve(process.argv[3] || path.join(import.meta.dirname, '..'));
if (!fs.existsSync(pdfPath)) throw new Error(`PDF not found: ${pdfPath}`);

const outputRoot = path.join(projectRoot, 'static', 'academics', 'coa-diagrams');
const imageRoot = path.join(outputRoot, 'images');
const workRoot = path.join(projectRoot, 'tmp_coa_extraction');
const pageRoot = path.join(workRoot, 'pages');
const ocrRoot = path.join(workRoot, 'ocr');
for (const directory of [outputRoot, imageRoot, workRoot, pageRoot, ocrRoot]) fs.mkdirSync(directory, { recursive: true });

const CHAPTERS = {
  1: 'Digital Logic Circuits', 2: 'Digital Components', 3: 'Data Representation',
  4: 'Register Transfer and Microoperations', 5: 'Basic Computer Organization and Design',
  6: 'Programming the Basic Computer', 7: 'Microprogrammed Control', 8: 'Central Processing Unit',
  9: 'Pipeline and Vector Processing', 10: 'Computer Arithmetic', 11: 'Input-Output Organization',
  12: 'Memory Organization', 13: 'Multiprocessors',
};

const rawPdf = fs.readFileSync(pdfPath);
const latinPdf = rawPdf.toString('latin1');
const pdf = await pdfjsLib.getDocument({ data: new Uint8Array(rawPdf), disableWorker: true }).promise;
const pageRefs = [...latinPdf.matchAll(/\/Type\/Page>>/g)].map(match => {
  const windowStart = Math.max(0, match.index - 1000);
  const prefix = latinPdf.slice(windowStart, match.index);
  const refs = [...prefix.matchAll(/(\d+)\s+(\d+)\s+obj/g)];
  const ref = refs.at(-1);
  const start = windowStart + ref.index;
  return { num: Number(ref[1]), gen: Number(ref[2]), start, body: latinPdf.slice(start, latinPdf.indexOf('endobj', start)) };
});
if (pageRefs.length !== pdf.numPages) throw new Error(`Page inventory mismatch: ${pageRefs.length} raw pages vs ${pdf.numPages} PDF pages`);

function objectBody(ref) {
  const marker = `${ref.num} ${ref.gen || 0} obj`;
  const start = latinPdf.indexOf(marker);
  if (start < 0) throw new Error(`PDF object not found: ${marker}`);
  return { start, body: latinPdf.slice(start, latinPdf.indexOf('endobj', start)) };
}

function tiffFromCcitt(bytes, width, height) {
  const entries = [[256,4,width],[257,4,height],[258,3,1],[259,3,4],[262,3,0],[273,4,122],[277,3,1],[278,4,height],[279,4,bytes.length]];
  const header = Buffer.alloc(122);
  header.write('II', 0); header.writeUInt16LE(42, 2); header.writeUInt32LE(8, 4); header.writeUInt16LE(entries.length, 8);
  entries.forEach(([tag,type,value], index) => {
    const p = 10 + index * 12;
    header.writeUInt16LE(tag,p); header.writeUInt16LE(type,p+2); header.writeUInt32LE(1,p+4);
    type === 3 ? header.writeUInt16LE(value,p+8) : header.writeUInt32LE(value,p+8);
  });
  return Buffer.concat([header, bytes]);
}

async function extractPage(pageNumber) {
  const existing = fs.readdirSync(pageRoot).find(name => name.startsWith(`${String(pageNumber).padStart(3, '0')}.`));
  if (existing) return path.join(pageRoot, existing);
  const pageRef = pageRefs[pageNumber - 1];
  const pageBody = pageRef.body;
  const imageRefMatch = pageBody.match(/\/Im[01]\s+(\d+)\s+(\d+)\s+R/);
  if (!imageRefMatch) throw new Error(`PDF page ${pageNumber} has no scanned image`);
  const imageRef = { num: Number(imageRefMatch[1]), gen: Number(imageRefMatch[2]) };
  const imageMarker = `${imageRef.num} ${imageRef.gen || 0} obj`;
  let imageStart = latinPdf.indexOf(imageMarker, pageRef.start);
  if (imageStart < 0) imageStart = objectBody(imageRef).start;
  const streamToken = latinPdf.indexOf('stream', imageStart);
  const dictionary = latinPdf.slice(imageStart, streamToken);
  const length = Number(dictionary.match(/\/Length\s+(\d+)/)?.[1]);
  let dataStart = streamToken + 6;
  if (rawPdf[dataStart] === 13) dataStart += 1;
  if (rawPdf[dataStart] === 10) dataStart += 1;
  const bytes = rawPdf.subarray(dataStart, dataStart + length);
  const prefix = String(pageNumber).padStart(3, '0');
  if (/\/DCTDecode/.test(dictionary)) {
    const file = path.join(pageRoot, `${prefix}.jpg`); fs.writeFileSync(file, bytes); return file;
  }
  if (/\/CCITTFaxDecode/.test(dictionary)) {
    const width = Number(dictionary.match(/\/Width\s+(\d+)/)?.[1]);
    const height = Number(dictionary.match(/\/Height\s+(\d+)/)?.[1]);
    const file = path.join(pageRoot, `${prefix}.tif`); fs.writeFileSync(file, tiffFromCcitt(bytes, width, height)); return file;
  }
  throw new Error(`Unsupported page encoding on page ${pageNumber}`);
}

function flattenLines(blocks = []) {
  return blocks.flatMap(block => (block.paragraphs || []).flatMap(paragraph => paragraph.lines || []))
    .map(line => ({ text: line.text.replace(/\s+/g, ' ').trim(), bbox: line.bbox, confidence: line.confidence }))
    .filter(line => line.text).sort((a, b) => a.bbox.y0 - b.bbox.y0 || a.bbox.x0 - b.bbox.x0);
}

async function auditPage(worker, pageNumber) {
  const cache = path.join(ocrRoot, `${String(pageNumber).padStart(3, '0')}.json`);
  if (fs.existsSync(cache)) return JSON.parse(fs.readFileSync(cache, 'utf8'));
  const source = await extractPage(pageNumber);
  const result = await worker.recognize(source, {}, { blocks: true, text: true });
  const metadata = await sharp(source, { pages: 1 }).metadata();
  const lines = flattenLines(result.data.blocks);
  const audit = { pdf_page: pageNumber, width: metadata.width, height: metadata.height, confidence: Math.round(result.data.confidence), text: result.data.text, lines };
  fs.writeFileSync(cache, JSON.stringify(audit));
  return audit;
}

const workers = await Promise.all(Array.from({ length: 3 }, () => createWorker('eng')));
const audits = new Array(pdf.numPages);
let cursor = 1;
await Promise.all(workers.map(async worker => {
  while (cursor <= pdf.numPages) {
    const pageNumber = cursor++;
    audits[pageNumber - 1] = await auditPage(worker, pageNumber);
    if (pageNumber % 20 === 0) console.log(`Audited ${pageNumber}/${pdf.numPages}`);
  }
}));
await Promise.all(workers.map(worker => worker.terminate()));

const captionStart = /^figure[\s:]*([0-9]{1,2})\s*[-â€“—.]\s*([0-9]{1,3})(?:\s*[a-z])?\b[\s:.-]*(.*)$/i;
const figures = [];
const auditManifest = [];
for (const page of audits) {
  const captions = [];
  page.lines.forEach((line, index) => {
    const match = line.text.match(captionStart);
    if (!match) return;
    let caption = match[3].trim();
    if (/^(?:shows?|illustrates?|depicts?|the\s+(?:two|figure|processors?|diagram|configuration))\b/i.test(caption) || caption.length > 180) return;
    let bottom = line.bbox.y1;
    caption = caption.replace(/\s+/g, ' ').replace(/^[.\-: ]+/, '').trim();
    captions.push({ chapter: Number(match[1]), number: Number(match[2]), figure: `${match[1]}-${match[2]}`, caption: caption || `Figure ${match[1]}-${match[2]}`, bbox: line.bbox, bottom });
  });
  auditManifest.push({ pdf_page: page.pdf_page, disposition: captions.length ? 'instructional_figures' : 'no_qualifying_figure', figures: captions.map(item => item.figure), ocr_confidence: page.confidence });
  for (let index = 0; index < captions.length; index += 1) {
    const item = captions[index];
    const previousBottom = index ? captions[index - 1].bottom : Math.round(page.height * 0.04);
    const proposedTop = Math.max(previousBottom, Math.round(item.bbox.y0 - page.height * 0.52));
    const top = Math.max(0, Math.min(proposedTop, page.height - 80, item.bbox.y0 - 20));
    const left = Math.max(0, Math.min(Math.round(Math.min(item.bbox.x0, page.width * 0.04)), page.width - 80));
    const right = Math.max(left + 80, Math.min(page.width, Math.round(Math.max(item.bbox.x1, page.width * 0.96))));
    const bottom = Math.max(top + 80, Math.min(page.height, Math.round(item.bottom + page.height * 0.012)));
    const id = `figure-${item.figure}`;
    const source = await extractPage(page.pdf_page);
    const fileName = `${id}-p${String(page.pdf_page).padStart(3, '0')}-i${index + 1}.webp`;
    const destination = path.join(imageRoot, fileName);
    try {
      await sharp(source, { pages: 1 }).extract({ left, top, width: right - left, height: bottom - top })
        .flatten({ background: '#ffffff' }).resize({ width: 1800, withoutEnlargement: true })
        .webp({ quality: 88, smartSubsample: true }).toFile(destination);
    } catch (error) {
      throw new Error(`Crop failed for PDF page ${page.pdf_page}, ${item.figure}: source=${page.width}x${page.height}, crop=${left},${top},${right-left},${bottom-top}: ${error.message}`);
    }
    const digest = crypto.createHash('sha256').update(fs.readFileSync(destination)).digest('hex');
    const title = item.caption.replace(/[.;:]$/, '') || `Figure ${item.figure}`;
    const figure = { id, chapter: item.chapter, chapter_title: CHAPTERS[item.chapter] || `Chapter ${item.chapter}`, section: `Chapter ${item.chapter}`, topic: title, caption: item.caption, figure_number: item.figure, pdf_page: page.pdf_page, source_pages: [page.pdf_page], image: `academics/coa-diagrams/images/${fileName}`, alt: `${title}, Figure ${item.figure} from ${CHAPTERS[item.chapter] || `Chapter ${item.chapter}`}`, keywords: [...new Set(`${title} ${item.figure} ${CHAPTERS[item.chapter] || ''}`.toLowerCase().match(/[a-z0-9]+/g) || [])], sha256: digest };
    figure.working_steps = buildWorkingSteps(figure);
    figures.push(figure);
  }
}

// Caption/figure-number duplicates resolve to the earliest canonical crop while retaining page provenance.
const canonical = [];
const byId = new Map();
for (const figure of figures.sort((a,b) => a.chapter - b.chapter || a.number - b.number || a.pdf_page - b.pdf_page)) {
  if (!byId.has(figure.id)) { byId.set(figure.id, figure); canonical.push(figure); }
  else if (!byId.get(figure.id).source_pages.includes(figure.pdf_page)) byId.get(figure.id).source_pages.push(figure.pdf_page);
}
const manifest = { source: path.basename(pdfPath), page_count: pdf.numPages, generated_at: new Date().toISOString(), figure_count: canonical.length, chapters: Object.entries(CHAPTERS).map(([number,title]) => ({ number: Number(number), title, count: canonical.filter(item => item.chapter === Number(number)).length })), figures: canonical };
const referencedFiles = new Set(canonical.map(item => path.basename(item.image)));
for (const fileName of fs.readdirSync(imageRoot)) if (!referencedFiles.has(fileName)) fs.unlinkSync(path.join(imageRoot, fileName));
fs.writeFileSync(path.join(outputRoot, 'manifest.json'), JSON.stringify(manifest, null, 2));
fs.writeFileSync(path.join(outputRoot, 'page-audit.json'), JSON.stringify({ source: path.basename(pdfPath), page_count: pdf.numPages, audited_pages: auditManifest.length, pages: auditManifest }, null, 2));
console.log(`Created ${canonical.length} canonical diagrams from ${pdf.numPages} audited pages.`);
