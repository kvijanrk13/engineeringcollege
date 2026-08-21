import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const root = path.resolve(import.meta.dirname, '..');
const staticRoot = path.join(root, 'static');
const libraryRoot = path.join(staticRoot, 'academics', 'coa-diagrams');
const manifest = JSON.parse(fs.readFileSync(path.join(libraryRoot, 'manifest.json'), 'utf8'));
const audit = JSON.parse(fs.readFileSync(path.join(libraryRoot, 'page-audit.json'), 'utf8'));
const template = fs.readFileSync(path.join(root, 'templates', 'academics', 'academics.html'), 'utf8');

assert.equal(manifest.page_count, 524, 'source page count');
assert.equal(audit.audited_pages, 524, 'every PDF page must have an audit record');
assert.deepEqual(audit.pages.map(page => page.pdf_page), Array.from({ length: 524 }, (_, index) => index + 1), 'audit pages must be complete and ordered');
assert.equal(manifest.figure_count, manifest.figures.length, 'figure count must match manifest entries');
assert.ok(manifest.figure_count > 150, 'expected a substantial textbook figure library');
assert.equal(new Set(manifest.figures.map(figure => figure.id)).size, manifest.figure_count, 'canonical IDs must be unique');
assert.equal(manifest.chapters.reduce((sum, chapter) => sum + chapter.count, 0), manifest.figure_count, 'chapter counts must cover every figure');

for (const figure of manifest.figures) {
  for (const key of ['chapter','chapter_title','section','topic','caption','figure_number','pdf_page','image','alt','keywords','sha256']) assert.ok(figure[key] !== undefined && figure[key] !== '', `${figure.id} missing ${key}`);
  assert.match(figure.figure_number, /^\d{1,2}-\d{1,3}$/);
  assert.ok(figure.source_pages.includes(figure.pdf_page), `${figure.id} source provenance`);
  const asset = path.join(staticRoot, ...figure.image.split('/'));
  assert.ok(fs.existsSync(asset), `${figure.id} image missing`);
  assert.ok(fs.statSync(asset).size > 1000, `${figure.id} image is unexpectedly small`);
  assert.equal(crypto.createHash('sha256').update(fs.readFileSync(asset)).digest('hex'), figure.sha256, `${figure.id} checksum mismatch`);
}

for (const hook of ['coa-diagram-library','coa-diagram-search','coa-chapter-filters','coa-diagram-grid','coa-diagram-lightbox','showModal()','workingSteps','coa-animation-play','coa-animation-step-previous','coa-animation-step-next','coa-card-steps','coa-card-step-status','activeCardStop','prefers-reduced-motion','ArrowLeft','ArrowRight','PageUp','PageDown']) assert.ok(template.includes(hook), `template missing ${hook}`);
console.log(`COA diagram validation passed: ${audit.audited_pages} pages, ${manifest.figure_count} figures, ${manifest.chapters.length} chapters.`);
