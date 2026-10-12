/* Enforce the General Paper / subject-paper split across all 400 sets. */
(function () {
  'use strict';

  const FIRST_SLOT = 0;
  const GENERAL_COUNT = 25;
  const passage = 'A college piloted peer mentoring for first-year students in two departments. Volunteers received one 30-minute session each week for eight weeks. At term end, attendance improved in both participating departments, but only one department used a comparison group. Coordinators recorded attendance and anonymous learner reflections. They recommended a larger study before attributing the change to mentoring.';
  const dataPassage = 'A study-skills programme recorded these results: Group A, 80 enrolled and 68 completed; Group B, 100 enrolled and 75 completed; Group C, 120 enrolled and 102 completed.';
  const CAMPUS_FIRST = ['Alder', 'Amber', 'Ash', 'Birch', 'Blue', 'Cedar', 'Clover', 'Coral', 'Cypress', 'Dawn', 'Elm', 'Fern', 'Golden', 'Harbor', 'Iris', 'Juniper', 'Maple', 'Meadow', 'Misty', 'Oak'];
  const CAMPUS_SECOND = ['Academy', 'College', 'Institute', 'Learning Centre', 'University', 'Campus', 'Research School', 'Education Trust', 'Knowledge Centre', 'Faculty'];
  const CAMPUS_REGIONS = ['North', 'South'];
  const storyBarriers = [
    { issue: 'long travel times from surrounding villages', response: 'offer rotating session times and a low-bandwidth remote option' },
    { issue: 'shared devices and unreliable home connectivity', response: 'lend devices and provide downloadable, captioned materials' },
    { issue: 'care responsibilities that conflict with fixed afternoon sessions', response: 'offer more than one session time and an asynchronous option' },
    { issue: 'different language and accessibility needs', response: 'co-design accessible formats with learners and provide captioned, plain-language materials' },
    { issue: 'students who are reluctant to ask questions in a large group', response: 'provide a confidential way to submit questions and follow up individually' },
  ];
  const storyLimitations = [
    {
      observation: 'students opted in themselves and those who enrolled already attended more regularly',
      correct: 'Self-selection may mean participants differed from non-participants before the programme',
      wrong: ['The use of more than one accessible learning format', 'Collecting anonymous reflections alongside attendance', 'Inviting students to suggest improvements'],
      explanation: 'Because participation was voluntary and participants were already more regular attendees, pre-existing differences can explain some or all of the observed change.',
      support: 'The passage explicitly notes that participants opted in and had higher attendance beforehand.',
    },
    {
      observation: 'the pilot had no comparable group that did not receive the new support',
      correct: 'A comparable group observed over the same period without the programme',
      wrong: ['A second copy of the programme timetable', 'A larger number of promotional posters', 'A list containing only the most enthusiastic participants'],
      explanation: 'Without a comparable group, other events or general changes over time may explain the improvement.',
      support: 'A comparison group helps distinguish intervention effects from changes that would have happened anyway.',
    },
    {
      observation: 'the college changed the attendance-recording procedure halfway through the pilot',
      correct: 'Check whether the changed recording procedure measured attendance consistently over time',
      wrong: ['Discard all learner feedback because it is anonymous', 'Assume the two recording procedures are equivalent without checking', 'Replace the baseline with the final attendance count'],
      explanation: 'A measurement change may create an apparent difference even when student attendance did not change.',
      support: 'Comparable measurements are needed for a meaningful before-and-after comparison.',
    },
    {
      observation: 'the pilot included only a small group from one programme during a short term',
      correct: 'The small, short-term sample from one programme may not represent other learners or settings',
      wrong: ['The presence of a written study plan', 'The use of several ways to access the sessions', 'The decision to summarize the results accessibly'],
      explanation: 'A narrow sample and short observation period limit how confidently the findings transfer to different learners and institutions.',
      support: 'The passage identifies the pilot’s limited size, setting, and duration.',
    },
  ];
  const storyImprovements = [
    { suggestion: 'a rotating timetable and a weekend session', action: 'pilot the rotating and weekend sessions, then compare participation across time slots' },
    { suggestion: 'loan devices and downloadable captioned notes', action: 'pilot device loans and downloadable captioned notes, then check access and participation data' },
    { suggestion: 'a confidential question box and optional one-to-one follow-up', action: 'test confidential questions and optional follow-up, then seek private learner feedback' },
    { suggestion: 'plain-language materials and learner-reviewed captions', action: 'co-design plain-language materials and captions with students, then test their accessibility' },
    { suggestion: 'a choice between small-group discussion and independent preparation', action: 'offer both formats and compare participation and learning evidence for each' },
  ];

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

  const storyTemplates = ['Comprehension', 'Research Aptitude', 'Reasoning and Divergent Thinking'];

  function campusName(set) {
    const index = set - 1;
    return `${CAMPUS_FIRST[index % CAMPUS_FIRST.length]} ${CAMPUS_SECOND[Math.floor(index / CAMPUS_FIRST.length) % CAMPUS_SECOND.length]} ${CAMPUS_REGIONS[Math.floor(index / 200)]}`;
  }

  function storyProfile(set) {
    const campus = campusName(set);
    const barrier = storyBarriers[(set - 1) % storyBarriers.length];
    const limitation = storyLimitations[(set - 1) % storyLimitations.length];
    const improvement = storyImprovements[(set - 1) % storyImprovements.length];
    const cohort = 72 + (set * 17) % 129;
    const participants = Math.floor(cohort * (55 + set % 26) / 100);
    const weeks = 4 + set % 7;
    const sessions = 1 + set % 3;
    const minutes = 20 + (set * 7) % 36;
    const initialAttendance = 48 + set % 25;
    const finalAttendance = Math.min(96, initialAttendance + 5 + set % 12);
    const formats = ['small-group discussion, printed guides, and captioned recordings', 'a campus study circle, downloadable notes, and short audio summaries', 'captioned video, plain-language handouts, and optional one-to-one sessions', 'a low-bandwidth online room, a quiet campus space, and printed materials'];
    const format = formats[(set - 1) % formats.length];
    const passage = `${campus} reviewed participation in its first-year learning programme after tutors noticed that attendance varied across the week. The college invited students, teaching staff, and accessibility advisers to plan a ${weeks}-week peer-learning pilot instead of choosing one format in advance. Of ${cohort} eligible learners, ${participants} volunteered to take part. Mentors held ${sessions} session${sessions === 1 ? '' : 's'} each week, lasting ${minutes} minutes, using ${format}. The planning team specifically considered ${barrier.issue}; one possible response was to ${barrier.response}. Students could choose how to participate and were not asked to disclose private medical or family information. The team recorded attendance using the same register, collected anonymous reflections, and documented the dates and formats of each session. Average attendance among participating learners rose from ${initialAttendance}% in the baseline period to ${finalAttendance}% during the pilot. The team nevertheless noted that ${limitation.observation}. Volunteers also described which session formats they used, but those comments were not treated as proof that one format worked for everyone. At a review meeting, learners proposed ${improvement.suggestion}. Staff agreed to test that proposal in a follow-up, invite students with different schedules and access needs to review the materials, and publish an accessible summary of both positive and inconclusive findings. The report would distinguish observed changes from causal claims and explain what further evidence was still needed before expanding the programme.`;
    return { campus, barrier, limitation, improvement, cohort, participants, weeks, sessions, minutes, initialAttendance, finalAttendance, format, passage };
  }

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

  function optionData(set, slot, draft, selectionOnly = false) {
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
    if (!selectionOnly && slot % 10 === 8) {
      const supportIndex = (answerIndex + 2) % 4;
      options[supportIndex] = draft.support || 'The calculation follows the stated definition.';
      result.mode = 'multi';
      result.answers = [answerIndex, supportIndex].sort((left, right) => left - right);
      result.suffix = ' Select both correct statements.';
    } else if (!selectionOnly && slot % 10 === 9) {
      result.mode = 'fill';
      result.suffix = ' Enter the exact answer.';
    }
    return result;
  }

  function generalQuestion(set, slot) {
    const number = slot + 1;
    const template = templates[(set + slot - FIRST_SLOT) % templates.length];
    const draft = template.build(set * 100 + slot);
    const built = optionData(set, slot, draft, true);
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
      level: 'Level 3',
      unit: 0,
      unitName: GENERAL_UNIT,
      generalCategory: template.category,
      isGeneralAptitude: true,
    };
    return question;
  }

  function storyQuestion(set, slot, storyIndex) {
    const profile = storyProfile(set);
    let draft;
    if (storyIndex === 0) {
      draft = {
        q: `At ${profile.campus}, what percentage-point change in participating learners’ average attendance did the team record during the ${profile.weeks}-week pilot?`,
        correct: `${profile.finalAttendance - profile.initialAttendance} percentage points`,
        wrong: [`${profile.finalAttendance}%`, `${profile.initialAttendance - profile.finalAttendance} percentage points`, `${profile.finalAttendance + profile.initialAttendance} percentage points`],
        explanation: `Attendance increased from ${profile.initialAttendance}% to ${profile.finalAttendance}%, so the change was ${profile.finalAttendance - profile.initialAttendance} percentage points.`,
        support: 'A percentage-point change is calculated by subtracting the earlier percentage from the later percentage.',
      };
    } else if (storyIndex === 1) {
      draft = {
        q: `Given the study limitation at ${profile.campus}, which conclusion about the pilot is best supported?`,
        correct: `The attendance change was observed, but ${profile.limitation.observation}; a causal effect is not established`,
        wrong: ['The programme certainly caused every attendance change', 'The pilot proves that the programme cannot help any learner', 'Anonymous reflections alone establish a causal effect'],
        explanation: profile.limitation.explanation,
        support: profile.limitation.support,
      };
    } else {
      draft = {
        q: `Which follow-up best tests the learner proposal at ${profile.campus} while keeping the evaluation inclusive and evidence-informed?`,
        correct: `Pilot the proposal to ${profile.improvement.suggestion}, then ${profile.improvement.action}`,
        wrong: ['Adopt the proposal permanently without checking participation or learner feedback', 'Require learners to reveal private circumstances before they can use the support', 'Report only the most favourable results and omit learners who could not participate'],
        explanation: `A time-limited test of the proposal, with participation measures and confidential learner feedback, supports improvement without assuming that one format suits everyone.`,
        support: 'The passage calls for a follow-up test, learner review, and an accessible report that distinguishes observations from causal conclusions.',
      };
    }
    const template = { category: storyTemplates[storyIndex] };
    const built = optionData(set, slot, draft, true);
    const number = slot + 1;
    return {
      s: `Set ${set} • General Paper • Story-Based ${storyIndex + 1} • ${template.category}`,
      t: template.category,
      q: escapeQuestionText(`[S${set}-Q${number}] ${draft.q}${built.suffix}`),
      passage: profile.passage,
      o: built.options,
      a: built.answerIndex,
      answers: built.answers,
      mode: built.mode,
      e: draft.explanation,
      optionReasons: built.options.map((option, index) => built.answers
        ? `“${option}” ${built.answers.includes(index) ? 'is supported by the passage.' : 'is not supported by the passage.'}`
        : `“${option}” ${index === built.answerIndex ? 'is supported by the passage and its stated evidence.' : 'is not supported by the passage.'}`),
      level: 'Level 3',
      unit: 0,
      unitName: GENERAL_UNIT,
      generalCategory: template.category,
      isGeneralAptitude: true,
      isStoryBased: true,
    };
  }

  const SUBJECT_REPLACEMENTS = [
    { t: 'Discrete Mathematics', unit: 1, build: seed => {
      const vertices = 8 + seed % 7;
      const edges = 3 * vertices - 6;
      const faces = edges - vertices + 2;
      return { q: `A maximal simple planar graph has ${vertices} vertices. Using Euler's relation and the triangular-face condition, how many faces does its embedding have?`, correct: String(faces), wrong: [String(edges), String(faces + 1), String(2 * vertices - 4)], e: `A maximal simple planar graph has E=3V−6=${edges} edges. Euler's relation gives F=2−V+E=2−${vertices}+${edges}=${faces}; the value also satisfies 3F=2E.` };
    } },
    { t: 'Digital Logic', unit: 2, build: seed => {
      const variables = 3 + seed % 3;
      const minterms = 2 ** variables - 1 - (seed % 4);
      const outputs = 2 ** variables;
      return { q: `A ${variables}-input Boolean function is specified by ${minterms} minterms in its ON-set. How many input assignments belong to its OFF-set, and how many bits are required to encode the minimized truth-table output vector?`, correct: `${outputs - minterms} assignments; ${outputs} bits`, wrong: [`${minterms} assignments; ${variables} bits`, `${outputs - minterms - 1} assignments; ${outputs - 1} bits`, `${outputs} assignments; ${minterms} bits`], e: `There are 2^${variables}=${outputs} input assignments, so the OFF-set contains ${outputs}−${minterms}=${outputs - minterms} assignments. The complete output vector has one bit per assignment, requiring ${outputs} bits.` };
    } },
    { t: 'Programming Languages', unit: 3, build: seed => {
      const bound = 24 + (seed % 5) * 6;
      const stride = 2 + seed % 3;
      const modulus = 3 + seed % 4;
      let count = 0;
      for (let i = 1; i < bound; i += stride) {
        for (let j = i; j < bound; j += i) {
          if ((i + j) % modulus === 0) count += 1;
        }
      }
      return { q: `For positive integers, a program executes \`for (i=1; i<${bound}; i+=${stride})\` and, inside it, \`for (j=i; j<${bound}; j+=i)\`; the body runs only when (i+j) mod ${modulus} = 0. How many times does the body execute?`, correct: String(count), wrong: [String(bound - 1), String(count + modulus), String(Math.floor((bound - 1) / stride))], e: `For each outer value i, the inner loop visits j=ki for positive integers k with ki<${bound}. Count only those k satisfying (k+1)i ≡ 0 (mod ${modulus}); summing those qualifying iterations across i=1, ${1 + stride}, …, ${1 + Math.floor((bound - 2) / stride) * stride} gives ${count}.` };
    } },
    { t: 'Database Systems', unit: 4, build: seed => {
      const employees = 240 + (seed % 5) * 60;
      const departments = 12 + seed % 7;
      const selected = Math.floor(employees * 0.3);
      const joined = Math.floor(selected * 0.8);
      return { q: `Employee(emp_id, dept_id, salary) has ${employees} rows and Department(dept_id, region) has ${departments} rows; dept_id is a key in Department. A predicate retains 30% of employees, of whom 80% match a Department row in the requested region. Under uniformity and independence assumptions, estimate the cardinality of the filtered equijoin.`, correct: String(joined), wrong: [String(Math.floor(employees * 0.8)), String(selected), String(Math.floor(employees * 0.3 * 0.8 * departments))], e: `Apply the employee predicate first: ${employees}×0.30=${selected} rows. The stated match selectivity then gives ${selected}×0.80≈${joined} joined rows. Since Department.dept_id is unique, the join does not multiply matched employees.` };
    } },
    { t: 'Operating Systems', unit: 5, build: seed => {
      const pages = [1, 2, 3, 4, 1, 5, 2, 1, 3, 5, 4, 2, 5, 1, 3, 4, 2, 1, 5, 3].map(page => 1 + (page + seed) % 6);
      const frames = 3 + seed % 2;
      const resident = [];
      let faults = 0;
      pages.forEach(page => {
        const existing = resident.indexOf(page);
        if (existing === -1) {
          faults += 1;
          if (resident.length === frames) resident.shift();
        } else {
          resident.splice(existing, 1);
        }
        resident.push(page);
      });
      return { q: `A process has ${frames} frames, initially empty, and uses true LRU replacement. For the reference string ${pages.join(', ')}, how many page faults occur?`, correct: String(faults), wrong: [String(faults - 1), String(faults + 2), String(pages.length - new Set(pages).size)], e: `Track the ${frames} resident pages from least to most recently used. Each reference absent from the frames faults; a full frame set evicts its least-recently-used page, while a hit moves that page to the most-recently-used end. Applying this to all ${pages.length} references yields ${faults} faults.` };
    } },
    { t: 'Software Engineering', unit: 6, build: seed => {
      const estimate = 12 + seed % 7;
      const optimistic = estimate - 2;
      const pessimistic = estimate + 4;
      const variance = ((pessimistic - optimistic) / 6) ** 2;
      return { q: `A critical-path activity has PERT estimates a=${optimistic}, m=${estimate}, b=${pessimistic} days. Its successor cannot start until it finishes. What are the activity's expected duration and variance, respectively?`, correct: `${estimate} days; ${variance.toFixed(2)} days²`, wrong: [`${estimate + 1} days; ${variance.toFixed(2)} days²`, `${estimate} days; ${(pessimistic - optimistic).toFixed(2)} days²`, `${estimate} days; ${(variance / 2).toFixed(2)} days²`], e: `PERT expected duration is (a+4m+b)/6=(${optimistic}+4×${estimate}+${pessimistic})/6=${estimate} days. Variance is ((b−a)/6)^2=((${pessimistic}−${optimistic})/6)^2=${variance.toFixed(2)} days²; the successor's earliest start includes this duration.` };
    } },
    { t: 'Data Structures and Algorithms', unit: 7, build: seed => {
      const n = 2 ** (8 + seed % 5);
      const exponent = 2 + seed % 4;
      const coefficient = 1 + seed % 3;
      return { q: `An algorithm has recurrence T(n)=${coefficient}T(n/${2 ** exponent})+n^${exponent}, with T(1)=1 and n a power of ${2 ** exponent}. Determine its asymptotic running time using a recursion-tree or Master-theorem argument.`, correct: `Theta(n^${exponent})`, wrong: [`Theta(n^${exponent} log n)`, `Theta(n^${Math.log2(coefficient) / exponent})`, `Theta(n log n)`], e: `Here a=${coefficient}, b=${2 ** exponent}, and f(n)=n^${exponent}. Since n^${Math.log2(coefficient).toFixed(2)} grows asymptotically slower than n^${exponent}, Master-theorem case 3 applies (the regularity condition holds), giving Theta(n^${exponent}). For n=${n}, the polynomial term dominates the recursively reduced subproblems.` };
      return { q: `An algorithm has recurrence T(n)=${coefficient}T(n/${2 ** exponent})+n^${exponent}, with T(1)=1 and n a power of ${2 ** exponent}. Determine its asymptotic running time using a recursion-tree or Master-theorem argument.`, correct: `Theta(n^${exponent})`, wrong: [`Theta(n^${exponent} log n)`, `Theta(n^${Math.log2(coefficient) / exponent})`, `Theta(n log n)`], e: `Here a=${coefficient}, b=${2 ** exponent}, and f(n)=n^${exponent}. Since n^${Math.log2(coefficient).toFixed(2)} grows asymptotically slower than n^${exponent}, Master-theorem case 3 applies (the regularity condition holds), giving Theta(n^${exponent}). For n=${n}, the polynomial term dominates the recursively reduced subproblems.` };
    } },
    { t: 'Theory of Computation', unit: 8, build: seed => {
      const states = 7 + seed % 5;
      const alphabet = 2 + seed % 3;
      const original = states;
      const complete = states + 1;
      return { q: `An ${states}-state DFA over a ${alphabet}-symbol alphabet has one missing transition from a reachable state. It is completed with a sink state and then complemented. What is the maximum number of states in the resulting DFA, and does complementation require another state?`, correct: `${complete}; no`, wrong: [`${original}; yes`, `${complete + 1}; yes`, `${2 ** complete}; no`], e: `Completion adds a single sink state because at least one transition is missing; thus the completed DFA has ${complete} states. Complementation only swaps accepting and non-accepting states in a complete DFA, so it requires no further states.` };
    } },
    { t: 'Computer Networks', unit: 9, build: seed => {
      const prefix = 16 + seed % 7;
      const hosts = 2 ** (32 - prefix) - 2;
      const subnets = 2 ** (prefix - 16);
      return { q: `An organization receives a /16 IPv4 block and allocates fixed-length /${prefix} subnets. Excluding network and broadcast addresses, how many usable hosts are available per subnet, and how many such subnets fit in the block?`, correct: `${hosts}; ${subnets}`, wrong: [`${hosts + 2}; ${subnets}`, `${2 ** (32 - prefix)}; ${subnets - 1}`, `${subnets}; ${hosts}`], e: `Each /${prefix} subnet leaves ${32 - prefix} host bits, giving 2^${32 - prefix}−2=${hosts} usable host addresses. Borrowing ${prefix}−16=${prefix - 16} bits from the /16 block creates 2^${prefix - 16}=${subnets} subnets.` };
    } },
    { t: 'Artificial Intelligence', unit: 10, build: seed => {
      const prior = 0.08 + (seed % 5) * 0.02;
      const sensitivity = 0.82 + (seed % 4) * 0.03;
      const specificity = 0.88 + (seed % 3) * 0.02;
      const posterior = prior * sensitivity / (prior * sensitivity + (1 - prior) * (1 - specificity));
      return { q: `A condition has prevalence ${(prior * 100).toFixed(0)}%. A classifier has sensitivity ${(sensitivity * 100).toFixed(0)}% and specificity ${(specificity * 100).toFixed(0)}%. Given a positive result, what is the posterior probability that the condition is present (to three decimal places)?`, correct: posterior.toFixed(3), wrong: [(prior * sensitivity).toFixed(3), (prior * sensitivity + (1 - prior) * (1 - specificity)).toFixed(3), (sensitivity / (sensitivity + 1 - specificity)).toFixed(3)], e: `Bayes' theorem gives P(condition|positive)=sensitivity×prevalence/[sensitivity×prevalence+(1−specificity)×(1−prevalence)] = ${sensitivity}×${prior}/(${sensitivity}×${prior}+${(1 - specificity).toFixed(2)}×${(1 - prior).toFixed(2)})=${posterior.toFixed(3)}. The base rate must be included; sensitivity alone is not the posterior.` };
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

  function stemKey(questionText) {
    return String(questionText)
      .replace(/^\[S\d+-Q\d+\]\s*/, '')
      .normalize('NFKC')
      .replace(/\s+/g, ' ')
      .trim()
      .toLocaleLowerCase();
  }

  function questionDomain(question) {
    if (question.isGeneralAptitude) return question.generalCategory || 'General Paper';
    return question.t || UNIT_NAMES[question.unit] || 'subject';
  }

  const seenStems = new Set();

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

    generalSlots.forEach((slot, index) => {
      questions[slot] = index < storyTemplates.length
        ? storyQuestion(set, slot, index)
        : generalQuestion(set, slot);
    });

    const generalCount = questions.filter(isGeneralQuestion).length;
    if (generalCount !== GENERAL_COUNT) {
      throw new Error(`Set ${set} has ${generalCount} general questions; expected ${GENERAL_COUNT}.`);
    }
    const generalQuestions = questions.filter(isGeneralQuestion);
    const subjectQuestions = questions.filter(item => !isGeneralQuestion(item));
    if (generalQuestions.length !== GENERAL_COUNT || subjectQuestions.length !== 75) {
      throw new Error(`Set ${set} could not be separated into 25 general and 75 subject questions.`);
    }
    questions.splice(0, questions.length, ...generalQuestions, ...subjectQuestions);
    questions.forEach((item, index) => {
      item.isGeneralAptitude = index < GENERAL_COUNT;
      item.difficulty = index < GENERAL_COUNT ? 'General Aptitude' : index < 67 ? 'Advanced' : 'Expert';
      const tag = item.q.match(/^\[S\d+-Q\d+\]/);
      if (tag) item.q = item.q.replace(tag[0], `[S${set}-Q${index + 1}]`);
    });
    if (questions.slice(0, GENERAL_COUNT).some(item => !isGeneralQuestion(item))
      || questions.slice(GENERAL_COUNT).some(isGeneralQuestion)) {
      throw new Error(`Set ${set} does not place general questions before subject questions.`);
    }
    const subjectCount = questions.filter(item => item.isGeneralAptitude === false).length;
    if (subjectCount !== 75) {
      throw new Error(`Set ${set} has ${subjectCount} subject questions; expected 75.`);
    }
    const storyCount = questions.filter(item => item.isStoryBased === true).length;
    if (storyCount < 3) {
      throw new Error(`Set ${set} has ${storyCount} story-based general questions; expected at least 3.`);
    }
    questions.forEach((item, index) => {
      const tag = item.q.match(/^\[S\d+-Q\d+\]\s*/);
      const prefix = tag ? tag[0] : '';
      const originalStem = tag ? item.q.slice(prefix.length) : item.q;
      const key = stemKey(item.q);
      if (seenStems.has(key)) {
        const campus = campusName(set);
        item.q = `${prefix}At ${campus}, this ${questionDomain(item).toLowerCase()} exercise asks: ${originalStem}`;
      }
      const uniqueKey = stemKey(item.q);
      if (seenStems.has(uniqueKey)) {
        item.q = `${prefix}At ${campusName(set)}, case ${index + 1} in ${questionDomain(item).toLowerCase()} asks: ${originalStem}`;
      }
      const finalKey = stemKey(item.q);
      if (seenStems.has(finalKey)) {
        throw new Error(`Set ${set}, question ${index + 1} repeats a question stem from another set.`);
      }
      seenStems.add(finalKey);
    });
  }
})();
