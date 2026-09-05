import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const template = fs.readFileSync(new URL('../dashboard/templates/dashboard/exambranch.html', import.meta.url), 'utf8');
const scripts = [...template.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)]
  .filter(([, attributes]) => !/\bsrc\s*=|application\/json/i.test(attributes))
  .map(([, , code]) => code.replace(/\{%[\s\S]*?%\}/g, '/test-url/').replace(/\{\{[\s\S]*?\}\}/g, 'test-value'));
assert.ok(scripts.length, 'Expected inline page scripts');
scripts.forEach((code, index) => new vm.Script(code, { filename: `exambranch-inline-${index}.js` }));

// Exercise the real roster-generation code for every built-in evaluation.
const code = scripts.find(source => source.includes('function generateStudents('));
const start = code.indexOf('const defaultEvaluationRollNumbers');
const end = code.indexOf('function setGradeCell', start);
assert.ok(start >= 0 && end > start, 'Expected roster initialization and generation functions');
const context = vm.createContext({ console: { log() {} } });
vm.runInContext(`let activeEvaluationSheet = '1';\n${code.slice(start, end)}\n`
  + `globalThis.generateRoster = function (sheet) {
      activeEvaluationSheet = sheet;
      return generateStudents(getActiveEvaluationRollNumbers().length);
    };`, context);
for (const sheet of ['1', '2', '3', '4']) {
  const rows = context.generateRoster(sheet);
  assert.ok(rows.length > 0, `Evaluation ${sheet} should have students`);
  assert.ok(rows.every(row => row.rollNo && row.attendance !== ''), `Evaluation ${sheet} should have roll numbers and attendance`);
  console.log(`Evaluation ${sheet}: ${rows.length} students with roll numbers and attendance`);
}
console.log(`All ${scripts.length} inline scripts parse successfully.`);
