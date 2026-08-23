import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const projectRoot = path.resolve(import.meta.dirname, '..');
const staticRoot = path.join(projectRoot, 'static');
const root = path.join(staticRoot, 'academics', 'dm-textbook');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'manifest.json'), 'utf8'));
const audit = JSON.parse(fs.readFileSync(path.join(root, 'page-audit.json'), 'utf8'));
const template = fs.readFileSync(path.join(projectRoot, 'templates', 'academics', 'academics.html'), 'utf8');

assert.equal(manifest.page_count, 740);
assert.equal(audit.pages.length, 740, 'every source page must be inventoried');
assert.deepEqual(audit.pages.map(page => page.pdf_page), Array.from({ length: 740 }, (_, index) => index + 1));
assert.equal(manifest.algorithm_count, 17);
assert.ok(manifest.diagram_count >= 200);
assert.equal(manifest.items.length, manifest.algorithm_count + manifest.diagram_count);
assert.equal(new Set(manifest.items.map(item => item.id)).size, manifest.items.length);
for (const item of manifest.items) {
  for (const key of ['id', 'type', 'chapter', 'chapter_title', 'number', 'title', 'pdf_page', 'image', 'alt', 'keywords', 'sha256']) assert.notEqual(item[key], undefined, `${item.id} missing ${key}`);
  const file = path.join(staticRoot, ...item.image.split('/'));
  assert.ok(fs.statSync(file).size > 1000, `${item.id} asset missing or too small`);
  assert.equal(crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'), item.sha256, `${item.id} checksum mismatch`);
}
for (const hook of ['dm-textbook-library', 'dm-textbook-search', 'dm-type-filters', 'dm-chapter-filters', 'dm-textbook-grid', 'dm-textbook-lightbox', 'dm-algorithm-count', 'dm-diagram-count']) assert.ok(template.includes(hook), `template missing ${hook}`);
console.log(`Data Mining textbook validation passed: ${manifest.algorithm_count} algorithms, ${manifest.diagram_count} diagrams, ${audit.pages.length} pages audited.`);
