const fs = require('fs');
const path = require('path');

const moocsDirectory = path.join(__dirname, '..', 'static', 'moocs');
const sourceFiles = [
  'textbook_questions.js',
  'paper_three_questions.js',
  'a0402_paper_two.js',
  'a0403_paper_three.js',
  'a0418_computer_science.js',
  'general_paper_w.js',
  'additional_paper_mix.js',
  'extended_sets.js',
  'paper2_answer_key.js',
  'paper1_2014.js',
  'd8704_paper_two.js',
  'pdf_archive_sets.js',
  'gate_archive_sets.js',
  'question_enhancer.js',
  'assessment_pattern.js',
];

let source = sourceFiles
  .map(file => fs.readFileSync(path.join(moocsDirectory, file), 'utf8'))
  .join('\n');

source = 'const document={querySelector:()=>null};\n' + source;
source += `
(() => {
  const errors = [];
  const seenQuestions = new Map();
  let repeatedSourceQuestions = 0;
  let total = 0;

  for (let setNumber = 1; setNumber <= 50; setNumber += 1) {
    const questions = QUESTION_SETS[setNumber] || [];
    total += questions.length;
    if (questions.length !== 100) errors.push(\`Set \${setNumber} has \${questions.length} questions.\`);

    questions.forEach((question, index) => {
      const location = \`Set \${setNumber}, question \${index + 1}\`;
      if (!question || !question.q || !Array.isArray(question.o) || question.o.length < 4) {
        errors.push(\`\${location} is incomplete.\`);
        return;
      }
      if (!Number.isInteger(question.a) || question.a < 0 || question.a >= question.o.length) {
        errors.push(\`\${location} has an invalid answer key.\`);
      }
      if (!String(question.e || '').trim()) {
        errors.push(\`\${location} has no question-specific explanation.\`);
      }
      if (/Solution derivation:/i.test(String(question.e || ''))) {
        errors.push(\`\${location} still contains a generic keyword-derived explanation.\`);
      }
      if (String(question.e || '').trim().length < 100) {
        errors.push(\`\${location} does not have a detailed explanation.\`);
      }
      const expectedMode = index % 10 === 8 ? 'multi' : index % 10 === 9 ? 'fill' : 'selection';
      if (question.mode !== expectedMode) {
        errors.push(\`\${location} should use \${expectedMode} mode, not \${question.mode}.\`);
      }
      if (expectedMode === 'multi' && (!Array.isArray(question.answers) || question.answers.length !== 2)) {
        errors.push(\`\${location} must have exactly two multiple-selection answers.\`);
      }
      const normalized = question.q.toLocaleLowerCase().replace(/\\s+/g, ' ').trim();
      if (seenQuestions.has(normalized)) {
        repeatedSourceQuestions += 1;
      } else {
        seenQuestions.set(normalized, location);
      }
    });
  }

  if (errors.length) {
    console.error(errors.join('\\n'));
    process.exitCode = 1;
    return;
  }
  console.log(\`Validated 50 sets, \${total} MCQs, detailed explanations, and the 8+1+1 assessment pattern (\${repeatedSourceQuestions} repeated source question(s)).\`);
})();
`;

eval(source);
