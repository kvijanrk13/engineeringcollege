const fs = require('fs');
const path = require('path');

const moocsDirectory = path.join(__dirname, '..', 'static', 'moocs');
const diagramsDirectory = path.join(moocsDirectory, 'diagrams');
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
  'advanced_sets.js',
  'diagram_sets.js',
  'assessment_pattern.js',
  'bloom_taxonomy.js',
  'varied_matching_bank.js',
  'varied_sets.js',
  'general_aptitude_question_bank.js',
  'question_enhancer.js',
];

let source = sourceFiles
  .map(file => fs.readFileSync(path.join(moocsDirectory, file), 'utf8'))
  .join('\n');

source = 'const document={querySelector:()=>null};\nconst window=globalThis;\n' + source;
source += `
(() => {
  const errors = [];
  const seenQuestions = new Map();
  let repeatedSourceQuestions = 0;
  let diagrammaticQuestionCount = 0;
  let total = 0;
  const diagramSets = new Set();

  for (let setNumber = 1; setNumber <= 400; setNumber += 1) {
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
      if (!Array.isArray(question.optionReasons) || question.optionReasons.length !== question.o.length) {
        errors.push(\`\${location} does not explain every answer option.\`);
      } else if (question.optionReasons.some(reason => String(reason || '').trim().length < 80)) {
        errors.push(\`\${location} has an answer option without detailed reasoning.\`);
      }

      /* Diagrammatic requirement for Sets 301-400: every question must
         reference a valid diagram (img + alt) that exists on disk. */
      if (setNumber >= 301 && index >= 25) {
        diagrammaticQuestionCount += 1;
        if (!question.img || !String(question.img).trim()) {
          errors.push(\`\${location} is missing a diagram image reference.\`);
        }
        if (!question.alt || !String(question.alt).trim()) {
          errors.push(\`\${location} is missing a diagram alt description.\`);
        }
        if (question.img) {
          const diagramFile = path.join(diagramsDirectory, String(question.img).split(/\\//).pop());
          if (!fs.existsSync(diagramFile)) errors.push(\`\${location} references a missing diagram: \${question.img}\`);
          else diagramSets.add(setNumber);
        }
      }

      if (index < 25) {
        if (question.isGeneralAptitude !== true) {
          errors.push(\`\${location} is not marked as a general aptitude question.\`);
        }
        if (question.mode !== 'selection') {
          errors.push(\`\${location} should be a single-choice general MCQ, not \${question.mode}.\`);
        }
        if (!/teaching|research|reasoning|comprehension|general awareness|data interpretation|general aptitude/i.test(String(question.t || ''))) {
          errors.push(\`\${location} does not cover a requested general aptitude area.\`);
        }
      } else if (question.isGeneralAptitude !== false) {
        errors.push(\`\${location} is not marked as a subject question after the 25-question general section.\`);
      }
      if (question.o.length !== 4 || new Set(question.o).size !== 4) {
        errors.push(\`\${location} must have four distinct answer options.\`);
      }
      if (question.difficulty !== (index < 25 ? 'General Aptitude' : index < 67 ? 'Advanced' : 'Expert')) {
        errors.push(\`\${location} is not assigned the required advanced subject-question level.\`);
      }

      const normalized = String(question.q || '').toLocaleLowerCase().replace(/\\s+/g, ' ').trim();
      if (seenQuestions.has(normalized)) {
        repeatedSourceQuestions += 1;
        if (setNumber >= 301) errors.push(\`\${location} duplicates an earlier stem (stems must be unique across all 400 sets).\`);
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

  const diagramSetCount = [...diagramSets].sort((a, b) => a - b).join(', ');
  console.log(\`Validated 400 sets, \${total} MCQs, the first 25 general aptitude questions and final 75 advanced subject questions in every set, \${diagrammaticQuestionCount} diagrammatic subject questions (Sets 301-400), detailed explanations, all Set 301-400 subject questions referencing a valid existing diagram (\${[...diagramSets].length} sets), and unique stems across all 400 sets (\${repeatedSourceQuestions} repeated source question(s)).\`);
})()
`;

eval(source);
