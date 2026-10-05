/* Enforce the General Paper / subject-paper split across all 400 sets. */
(function () {
  'use strict';

  const FIRST_SLOT = 12;
  const GENERAL_COUNT = 25;
  const passage = 'A college piloted peer mentoring for first-year students in two departments. Volunteers received one 30-minute session each week for eight weeks. At term end, attendance improved in both participating departments, but only one department used a comparison group. Coordinators recorded attendance and anonymous learner reflections. They recommended a larger study before attributing the change to mentoring.';
  const dataPassage = 'A study-skills programme recorded these results: Group A, 80 enrolled and 68 completed; Group B, 100 enrolled and 75 completed; Group C, 120 enrolled and 102 completed.';

  const GENERAL_UNIT = 'General Paper: Teaching, Research, Reasoning and Awareness';
  const UNIT_NAMES = {
    1: 'Discrete Structures and Optimization',
    2: 'Computer System Architecture',
    3: 'Programming Languages and Computer Graphics',
    4: 'Database Management Systems',
    5: 'System Software and Operating System',
    6: 'Software Engineering',
    7: 'Data Structures and Algorithms',
    8: 'Theory of Computation and Compilers',
    9: 'Data Communication and Computer Networks',
    10: 'Artificial Intelligence',
  };

  const templates = [
    { category: 'Teaching Aptitude', build: () => ({
      q: 'A teacher wants learners to apply a concept to unfamiliar cases. Which activity best aligns with that outcome?',
      correct: 'Have learners solve and justify new cases using the concept',
      wrong: ['Ask learners only to copy the definition', 'Repeat the same worked example without discussion', 'Assess handwriting instead of application'],
      explanation: 'Transfer to unfamiliar cases requires learners to use the concept beyond recall and explain their reasoning.',
      support: 'Assessment should measure the stated learning outcome.',
    }) },
    { category: 'Teaching Aptitude', build: () => ({
      q: 'Which practice is formative assessment?',
      correct: 'Give feedback during learning and let students use it to improve',
      wrong: ['Publish a final grade with no feedback', 'Rank students only at the end of the course', 'Assess a topic before it is taught'],
      explanation: 'Formative assessment gathers evidence during learning and uses it to guide next steps for the learner and teacher.',
      support: 'Timely feedback can inform the next instructional step.',
    }) },
    { category: 'Teaching Aptitude', build: () => ({
      q: 'A class has varied prior knowledge and language proficiency. What is the strongest inclusive response?',
      correct: 'Offer multiple ways to access the material and demonstrate the same learning goals',
      wrong: ['Lower the learning goals for the entire class', 'Use one explanation and one response format for everyone', 'Separate learners permanently by one initial score'],
      explanation: 'Flexible access and expression support learner differences while keeping shared, meaningful outcomes.',
      support: 'Inclusive design anticipates learner variability.',
    }) },
    { category: 'Teaching Aptitude', build: () => ({
      q: 'Which feedback is most useful for improving a learner’s next attempt?',
      correct: 'Identify the specific gap and give an actionable next step',
      wrong: ['Say only “good” or “poor”', 'Compare the learner publicly with classmates', 'Give the correct answer without explaining the gap'],
      explanation: 'Specific, actionable feedback connects current performance to a clear improvement step.',
      support: 'Feedback should refer to criteria and observable work.',
    }) },
    { category: 'Teaching Aptitude', build: () => ({
      q: 'Why use an analytic rubric for a complex project?',
      correct: 'It makes separate criteria and performance levels explicit',
      wrong: ['It removes the need to communicate expectations', 'It guarantees every project receives the same score', 'It replaces feedback with a single unexplained number'],
      explanation: 'An analytic rubric separates dimensions of quality, making expectations and feedback more transparent.',
      support: 'Transparent criteria can improve consistency in assessment.',
    }) },
    { category: 'Research Aptitude', build: seed => ({
      q: `A pre-registered test uses significance level 0.05 and returns p = 0.${String(2 + seed % 3).padStart(2, '0')}. Which conclusion is justified?`,
      correct: 'Reject the null hypothesis at the stated significance level',
      wrong: ['Prove the alternative hypothesis is certainly true', 'Prove the null hypothesis has zero probability', 'Conclude the effect is practically important without an effect-size analysis'],
      explanation: 'Because p is below 0.05, the result is statistically significant under the stated test assumptions; this alone does not prove truth or practical importance.',
      support: 'Statistical significance does not by itself establish practical importance.',
    }) },
    { category: 'Research Aptitude', build: () => ({
      q: 'A population contains urban and rural learners, and the researcher needs both groups represented. Which sampling design is most directly suitable?',
      correct: 'Stratified sampling by residence, followed by sampling within each stratum',
      wrong: ['Convenience sampling from one urban class', 'Snowball sampling with no group targets', 'Select only the largest available stratum'],
      explanation: 'Stratification explicitly represents relevant subgroups before sampling within each one.',
      support: 'A sampling frame should cover every target stratum.',
    }) },
    { category: 'Research Aptitude', build: () => ({
      q: 'Which design feature most strengthens a causal claim about an intervention?',
      correct: 'Randomly assign eligible participants to intervention and comparison groups',
      wrong: ['Survey only participants after the intervention', 'Select volunteers who already achieved the outcome', 'Measure the outcome once with no comparison'],
      explanation: 'Random assignment helps balance confounders on average, supporting a causal comparison when the design is otherwise sound.',
      support: 'A suitable comparison group helps distinguish intervention effects from other changes.',
    }) },
    { category: 'Research Aptitude', build: () => ({
      q: 'A measure produces nearly identical scores on repeated administrations but does not measure the intended skill. It is best described as',
      correct: 'Reliable but not valid for the intended construct',
      wrong: ['Valid because it is consistent', 'Both reliable and valid by definition', 'Neither reliable nor measurable'],
      explanation: 'Reliability concerns consistency; validity concerns whether evidence supports the intended interpretation and use.',
      support: 'Consistency alone does not establish construct validity.',
    }) },
    { category: 'Research Aptitude', build: () => ({
      q: 'Before collecting identifiable information on a sensitive topic, a researcher should first',
      correct: 'Obtain informed consent and minimize identifiable data',
      wrong: ['Collect extra personal details in case they become useful', 'Promise absolute confidentiality without checking the data flow', 'Share raw responses with all project members'],
      explanation: 'Ethical research requires informed participation, data minimization, and realistic safeguards for confidentiality.',
      support: 'Participants should understand the purpose and relevant risks.',
    }) },
    { category: 'Reasoning and Divergent Thinking', build: seed => {
      const start = 1 + seed % 4;
      const terms = [start, start + 1, start + 2, start + 3].map(value => value * value + 1);
      return {
        q: `A sequence follows n² + 1 for consecutive integers n. What is the next term after ${terms.join(', ')}?`,
        correct: String((start + 4) ** 2 + 1),
        wrong: [String((start + 4) * 2 + 1), String((start + 3) ** 2 + 2), String((start + 5) ** 2 + 1)],
        explanation: `The terms are generated by n² + 1. Substituting n = ${start + 4} gives ${(start + 4) ** 2} + 1 = ${(start + 4) ** 2 + 1}.`,
        support: 'A pattern answer should satisfy the rule for every listed term.',
      };
    } },
    { category: 'Reasoning and Divergent Thinking', build: () => ({
      q: 'All field researchers record observations. Some graduate students are field researchers. Which conclusion follows?',
      correct: 'Some graduate students record observations',
      wrong: ['All graduate students are field researchers', 'All people who record observations are graduate students', 'No graduate student records observations'],
      explanation: 'The graduate students who are field researchers belong to the group that records observations, so at least some graduate students do so.',
      support: 'A conclusion must follow from the premises, not from an assumed converse.',
    }) },
    { category: 'Reasoning and Divergent Thinking', build: () => ({
      q: 'A proposal claims, “The new timetable improved results because the average mark rose.” Which additional evidence would best test that claim?',
      correct: 'Compare similar cohorts and examine other changes that could explain the rise',
      wrong: ['Repeat the claim in a larger font', 'Ask only the highest-scoring student', 'Ignore attendance and assessment differences'],
      explanation: 'A rise alone does not identify its cause; a suitable comparison and checks for confounding changes strengthen the inference.',
      support: 'Correlation or before-after change alone does not prove causation.',
    }) },
    { category: 'Reasoning and Divergent Thinking', build: seed => {
      const first = 8 + seed % 9;
      const second = 12 + (seed * 3) % 11;
      const total = first + second;
      return {
        q: `A group has ${total} members. The ratio of mentors to learners is ${first}:${second}. How many are learners?`,
        correct: String(second),
        wrong: [String(first), String(total - 1), String(total)],
        explanation: `The ratio has ${first + second} total parts, and the group has ${total} members, so each part represents one member. Learners account for ${second} parts.`,
        support: 'Check that the two ratio parts add to the stated group total.',
      };
    } },
    { category: 'Reasoning and Divergent Thinking', build: () => ({
      q: 'Which response best demonstrates divergent thinking when a low-cost water sensor must be made accessible to users with different abilities?',
      correct: 'Generate several distinct, safe feedback modes and test them with users',
      wrong: ['Choose the first idea without testing', 'Reject every idea that differs from the current design', 'Optimize appearance while ignoring access and safety'],
      explanation: 'Divergent thinking explores multiple distinct possibilities; user testing and constraints then help evaluate them.',
      support: 'Fluency and flexibility involve generating varied ideas before selection.',
    }) },
    { category: 'Comprehension', passage, build: () => ({
      q: 'How long was each peer-mentoring session in the passage?',
      correct: '30 minutes',
      wrong: ['15 minutes', '45 minutes', '60 minutes'],
      explanation: 'The passage states that volunteers received one 30-minute session each week.',
      support: 'Answer from the information explicitly stated in the passage.',
    }) },
    { category: 'Comprehension', passage, build: () => ({
      q: 'What limits the strength of a causal conclusion in the pilot?',
      correct: 'Only one participating department used a comparison group',
      wrong: ['No attendance information was recorded', 'The sessions lasted for one hour', 'The programme included no first-year students'],
      explanation: 'The passage says attendance improved in both departments, but only one used a comparison group; causal attribution therefore remains limited.',
      support: 'A comparison group helps interpret whether observed change is attributable to an intervention.',
    }) },
    { category: 'Comprehension', passage, build: () => ({
      q: 'Which evidence did the coordinators record?',
      correct: 'Attendance and anonymous learner reflections',
      wrong: ['Named exam scripts only', 'Employment records and fee receipts', 'Only the mentors’ personal opinions'],
      explanation: 'The passage explicitly identifies attendance and anonymous learner reflections as recorded evidence.',
      support: 'The passage distinguishes recorded evidence from proposed future research.',
    }) },
    { category: 'Comprehension', passage, build: () => ({
      q: 'Why did coordinators recommend a larger study?',
      correct: 'To gather stronger evidence before attributing the change to mentoring',
      wrong: ['To avoid recording attendance again', 'To prove the programme had no effect', 'To replace learner reflections with interviews of mentors only'],
      explanation: 'The passage concludes that a larger study is needed before attributing the observed attendance change to mentoring.',
      support: 'A cautious conclusion reflects the limits of the pilot design.',
    }) },
    { category: 'Data Interpretation', passage: dataPassage, build: () => ({
      q: 'How many learners in Group B completed the study-skills programme?',
      correct: '75',
      wrong: ['25', '100', '175'],
      explanation: 'The data passage reports 100 enrolled and 75 completed in Group B.',
      support: 'Read the completed count directly from the Group B row.',
    }) },
    { category: 'Data Interpretation', passage: dataPassage, build: () => ({
      q: 'Which group has the highest completion rate?',
      correct: 'Groups A and C tie at 85%',
      wrong: ['Group A alone at 80%', 'Group B alone at 75%', 'Group C alone at 90%'],
      explanation: 'Group A is 68/80 = 85%; Group B is 75/100 = 75%; Group C is 102/120 = 85%. A and C tie.',
      support: 'Compare completed divided by enrolled, not raw completion counts.',
    }) },
    { category: 'Data Interpretation', passage: dataPassage, build: () => ({
      q: 'What proportion of all enrolled learners completed the programme?',
      correct: 'About 81.7%',
      wrong: ['75%', '85%', '245%'],
      explanation: 'Across the groups, 68 + 75 + 102 = 245 completed out of 80 + 100 + 120 = 300, so 245/300 × 100 ≈ 81.7%.',
      support: 'For a combined rate, divide total completions by total enrolments.',
    }) },
    { category: 'General Awareness', build: () => ({
      q: 'Which Article of the Constitution of India provides for free and compulsory education for children aged 6–14?',
      correct: 'Article 21A',
      wrong: ['Article 14', 'Article 19(1)(a)', 'Article 32'],
      explanation: 'Article 21A provides for free and compulsory education for children within the specified age group.',
      support: 'Constitutional provisions should be distinguished by their stated subject.',
    }) },
    { category: 'General Awareness', build: () => ({
      q: 'Which action is an example of in-situ biodiversity conservation?',
      correct: 'Protecting a species in its natural habitat within a national park',
      wrong: ['Keeping every specimen only in a laboratory collection', 'Preserving seeds only in a storage vault', 'Moving a species into a botanical garden outside its habitat'],
      explanation: 'In-situ conservation protects species within their natural ecosystems; seed banks and captive collections are ex-situ approaches.',
      support: 'The key distinction is whether conservation occurs in the species’ natural habitat.',
    }) },
    { category: 'General Awareness', build: () => ({
      q: 'What is the primary purpose of institutional accreditation in higher education?',
      correct: 'Evaluate quality against stated standards and support improvement',
      wrong: ['Guarantee that every graduate receives employment', 'Replace all teaching and assessment', 'Award intellectual-property patents to students'],
      explanation: 'Accreditation evaluates institutions against defined quality criteria and can guide continuous improvement; it cannot guarantee every outcome.',
      support: 'Quality assurance evaluates evidence against published criteria.',
    }) },
  ];

  function seededShuffle(values, seed) {
    const result = values.slice();
    let state = seed >>> 0;
    for (let index = result.length - 1; index > 0; index -= 1) {
      state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
      const target = state % (index + 1);
      [result[index], result[target]] = [result[target], result[index]];
    }
    return result;
  }

  function escapeQuestionText(value) {
    return String(value).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function optionData(set, slot, draft) {
    const correct = String(draft.correct);
    const distractors = seededShuffle(
      [...new Set(draft.wrong.map(String))].filter(option => option !== correct),
      set * 131 + slot * 17,
    );
    while (distractors.length < 3) distractors.push(`None of these (${distractors.length + 1})`);
    const answerIndex = (set + slot * 3) % 4;
    const options = distractors.slice(0, 3);
    options.splice(answerIndex, 0, correct);

    const result = { options, answerIndex, mode: 'selection', answers: null, suffix: '' };
    if (slot % 10 === 8) {
      const supportIndex = (answerIndex + 2) % 4;
      options[supportIndex] = draft.support || 'The calculation follows the stated definition.';
      result.mode = 'multi';
      result.answers = [answerIndex, supportIndex].sort((left, right) => left - right);
      result.suffix = ' Select both correct statements.';
    } else if (slot % 10 === 9) {
      result.mode = 'fill';
      result.suffix = ' Enter the exact answer.';
    }
    return result;
  }

  function generalQuestion(set, slot) {
    const number = slot + 1;
    const template = templates[(set + slot - FIRST_SLOT) % templates.length];
    const draft = template.build(set * 100 + slot);
    const built = optionData(set, slot, draft);
    const question = {
      s: `Set ${set} • General Paper • ${template.category}`,
      t: template.category,
      q: escapeQuestionText(`[S${set}-Q${number}] ${draft.q}${built.suffix}`),
      passage: draft.passage || undefined,
      o: built.options,
      a: built.answerIndex,
      answers: built.answers,
      mode: built.mode,
      e: draft.explanation,
      optionReasons: built.options.map((option, index) => {
        if (built.answers) {
          return built.answers.includes(index)
            ? `“${option}” is supported by the passage, data, or principle tested.`
            : `“${option}” is not supported by the information or rule in the question.`;
        }
        return index === built.answerIndex
          ? `“${option}” is the only choice supported by the stated evidence or governing principle.`
          : `“${option}” does not follow from the stated evidence or governing principle.`;
      }),
      level: number <= 34 ? 'Level 1' : number <= 67 ? 'Level 2' : 'Level 3',
      unit: 0,
      unitName: GENERAL_UNIT,
      generalCategory: template.category,
      isGeneralAptitude: true,
    };
    return question;
  }

  const SUBJECT_REPLACEMENTS = [
    { t: 'Discrete Mathematics', unit: 1, build: seed => {
      const n = 8 + seed % 9;
      const answer = n * (n - 1) / 2;
      return { q: `How many edges does the complete graph K${n} have?`, correct: String(answer), wrong: [String(n * (n + 1) / 2), String(n * (n - 1)), String(n * n)], e: `A complete graph has one edge per unordered vertex pair: n(n−1)/2 = ${n}×${n - 1}/2 = ${answer}.` };
    } },
    { t: 'Digital Logic', unit: 2, build: seed => {
      const variables = 3 + seed % 4;
      return { q: `How many rows are in a complete truth table for ${variables} Boolean inputs?`, correct: String(2 ** variables), wrong: [String(variables * 2), String(2 ** variables - 1), String(variables ** 2)], e: `Each input has two values, so the table has 2^${variables} = ${2 ** variables} rows.` };
    } },
    { t: 'Programming Languages', unit: 3, build: seed => {
      const start = 2 + seed % 5;
      return { q: `A loop starts at i = 0 and executes while i < ${start * 4}, increasing i by 4 each time. How many iterations run?`, correct: String(start), wrong: [String(start + 1), String(start * 4), String(start - 1)], e: `The loop visits 0, 4, 8, …, ${start * 4 - 4}, giving ${start} iterations.` };
    } },
    { t: 'Database Systems', unit: 4, build: seed => {
      const rows = 12 + (seed % 20) * 4;
      return { q: `A relation has ${rows} rows. A selection retains 25% of them. How many rows remain?`, correct: String(rows / 4), wrong: [String(rows / 2), String(rows - rows / 4), String(rows)], e: `Selection cardinality is 0.25×${rows} = ${rows / 4} rows.` };
    } },
    { t: 'Operating Systems', unit: 5, build: seed => {
      const power = 10 + seed % 7;
      return { q: `A page contains 2^${power} bytes. How many bits are needed for the page offset?`, correct: String(power), wrong: [String(power + 1), String(power - 1), String(2 * power)], e: `An offset selects one of 2^${power} bytes, requiring ${power} bits.` };
    } },
    { t: 'Software Engineering', unit: 6, build: seed => {
      const edges = 14 + seed % 12;
      const nodes = 8 + seed % 7;
      return { q: `A connected control-flow graph has E = ${edges} edges and N = ${nodes} nodes. What is V(G) = E − N + 2?`, correct: String(edges - nodes + 2), wrong: [String(edges - nodes), String(edges - nodes + 1), String(edges + nodes - 2)], e: `For one connected component, V(G)=E−N+2=${edges}−${nodes}+2=${edges - nodes + 2}.` };
    } },
    { t: 'Data Structures and Algorithms', unit: 7, build: seed => {
      const n = 16 * (1 + seed % 8);
      return { q: `A sorted array has ${n} elements. What is the maximum number of comparisons in binary search?`, correct: String(Math.floor(Math.log2(n)) + 1), wrong: [String(Math.ceil(Math.log2(n))), String(n), String(Math.floor(Math.log2(n)))], e: `Binary search halves the remaining range; at most floor(log₂(${n}))+1 = ${Math.floor(Math.log2(n)) + 1} comparisons are needed.` };
    } },
    { t: 'Theory of Computation', unit: 8, build: seed => {
      const first = 2 + seed % 5;
      const second = 3 + seed % 6;
      return { q: `The product construction combines DFAs with ${first} and ${second} states. What is the maximum number of product states?`, correct: String(first * second), wrong: [String(first + second), String(first * second - 1), String(Math.max(first, second))], e: `The product construction has at most ${first}×${second} = ${first * second} state pairs.` };
    } },
    { t: 'Computer Networks', unit: 9, build: seed => {
      const payload = 500 + (seed % 25) * 20;
      const rate = 2 + seed % 8;
      const millis = (payload * 8 / (rate * 1000)).toFixed(2);
      return { q: `How long does it take to transmit ${payload} bytes over a ${rate} Mbps link, ignoring overhead?`, correct: `${millis} ms`, wrong: [`${(payload / (rate * 1000)).toFixed(2)} ms`, `${(payload * 8 / rate).toFixed(2)} ms`, `${(payload * 8 / (rate * 100)).toFixed(2)} ms`], e: `Transmission time = bits/rate = ${payload}×8 / (${rate}×10^6) seconds = ${millis} ms.` };
    } },
    { t: 'Artificial Intelligence', unit: 10, build: seed => {
      const truePositive = 20 + seed % 25;
      const falsePositive = 3 + seed % 7;
      return { q: `A classifier has TP = ${truePositive} and FP = ${falsePositive}. What is its precision?`, correct: (truePositive / (truePositive + falsePositive)).toFixed(2), wrong: [(falsePositive / (truePositive + falsePositive)).toFixed(2), (truePositive / (truePositive + 1)).toFixed(2), (truePositive / falsePositive).toFixed(2)], e: `Precision = TP/(TP+FP) = ${truePositive}/(${truePositive}+${falsePositive}) = ${(truePositive / (truePositive + falsePositive)).toFixed(2)}.` };
    } },
  ];

  function subjectQuestion(set, slot, ordinal) {
    const template = SUBJECT_REPLACEMENTS[(set * 7 + slot + ordinal) % SUBJECT_REPLACEMENTS.length];
    const draft = template.build(set * 1000 + slot * 13 + ordinal);
    const built = optionData(set + 401, slot, draft);
    const number = slot + 1;
    return {
      s: `Set ${set} • ${template.t} • Unit ${template.unit}`,
      t: template.t,
      q: escapeQuestionText(`[S${set}-Q${number}] ${draft.q}${built.suffix}`),
      o: built.options,
      a: built.answerIndex,
      answers: built.answers,
      mode: built.mode,
      e: draft.e,
      optionReasons: built.options.map((option, index) => built.answers
        ? `“${option}” ${built.answers.includes(index) ? 'is consistent with the calculation or definition.' : 'is not consistent with the calculation or definition.'}`
        : `“${option}” ${index === built.answerIndex ? 'follows from the stated rule and calculation.' : 'does not follow from the stated rule and calculation.'}`),
      unit: template.unit,
      unitName: UNIT_NAMES[template.unit],
      level: number <= 34 ? 'Level 1' : number <= 67 ? 'Level 2' : 'Level 3',
      isGeneralAptitude: false,
    };
  }

  function isGeneralQuestion(question) {
    if (question.isGeneralAptitude === true) return true;
    if (question.unitName === GENERAL_UNIT || question.unitName === 'General Paper: Teaching, Research and General Aptitude' || question.unitName === 'General Aptitude') return true;
    if (/general paper|general studies|general aptitude/i.test(question.s || '')) return true;
    return /^(general aptitude|teaching(?: aptitude)?|research(?: aptitude| methods| ethics)?|learners|methods|sampling|measurement|communication|reasoning|aptitude|data interpretation|ict|environment|higher education|statistics|general awareness|comprehension)$/i.test(String(question.t || '').trim());
  }

  function isPreservedGeneral(question) {
    return (question.isMatching === true && /general aptitude/i.test(String(question.t || '')))
      || (question.isDiagramQuestion === true && question.isGeneralAptitude === true);
  }

  for (let set = 1; set <= 400; set += 1) {
    const questions = QUESTION_SETS[set];
    if (!Array.isArray(questions) || questions.length !== 100) {
      throw new Error(`General Paper bank expected 100 questions in Set ${set}.`);
    }

    const preserved = new Set();
    questions.forEach((item, index) => {
      if (isPreservedGeneral(item)) {
        item.isGeneralAptitude = true;
        item.generalCategory = item.generalCategory || 'General Aptitude';
        preserved.add(index);
      }
    });
    if (preserved.size > GENERAL_COUNT) {
      throw new Error(`Set ${set} contains more preserved general questions than the 25-question quota.`);
    }

    const generalSlots = [];
    for (let slot = FIRST_SLOT; slot < 100 && generalSlots.length < GENERAL_COUNT - preserved.size; slot += 1) {
      if (!preserved.has(slot)) generalSlots.push(slot);
    }
    if (generalSlots.length !== GENERAL_COUNT - preserved.size) {
      throw new Error(`Unable to allocate 25 general questions in Set ${set}.`);
    }

    const replacedGeneral = new Set();
    questions.forEach((item, index) => {
      if (!preserved.has(index) && isGeneralQuestion(item)) {
        questions[index] = subjectQuestion(set, index, replacedGeneral.size);
        replacedGeneral.add(index);
      }
    });

    generalSlots.forEach(slot => {
      questions[slot] = generalQuestion(set, slot);
    });

    const generalCount = questions.filter(isGeneralQuestion).length;
    if (generalCount !== GENERAL_COUNT) {
      throw new Error(`Set ${set} has ${generalCount} general questions; expected ${GENERAL_COUNT}.`);
    }
    questions.forEach(item => {
      if (item.isGeneralAptitude !== true) item.isGeneralAptitude = false;
    });
    const subjectCount = questions.filter(item => item.isGeneralAptitude === false).length;
    if (subjectCount !== 75) {
      throw new Error(`Set ${set} has ${subjectCount} subject questions; expected 75.`);
    }
  }
})();
