/* Apply the five requested Bloom's Taxonomy levels to every loaded MCQ set. */
(function () {
  const levels = [
    { name: 'Remember', prompt: 'Recall the relevant fact, term, or definition, then answer:' },
    { name: 'Understand', prompt: 'Interpret the concept described and select the option that best explains it:' },
    { name: 'Apply', prompt: 'Apply the relevant rule, method, or procedure to the given situation:' },
    { name: 'Analyze', prompt: 'Analyze the given information and determine the correct relationship or result:' },
    { name: 'Evaluate', prompt: 'Evaluate the alternatives against the stated conditions and select the most defensible answer:' }
  ];

  const escapePattern = value => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const oldPrompt = new RegExp(`^(?:${levels.map(level => escapePattern(level.prompt)).join('|')})\\s*`, 'i');
  const legacyPrompt = /^Evaluate every constraint and choose the most technically defensible conclusion\.\s*/i;

  Object.entries(QUESTION_SETS).forEach(([setNumber, questions]) => {
    const total = questions.length;

    questions.forEach((question, index) => {
      /* Proportional bands ensure that short and long sets both cover all five levels. */
      const band = Math.min(levels.length - 1, Math.floor(index * levels.length / total));
      const bloom = levels[band];
      const originalStem = String(question.q || '')
        .replace(oldPrompt, '')
        .replace(legacyPrompt, '')
        .trim();

      question.q = `${bloom.prompt} ${originalStem}`;
      question.level = bloom.name;
      question.bloomLevel = band + 1;
      question.bloomTaxonomy = bloom.name;

      const source = String(question.s || '').trim();
      const withoutOldLevel = source
        .replace(/\s*•\s*(?:Level\s*[1-5]|Remember|Understand|Apply|Analyze|Evaluate)\s*•\s*/i, ' • ')
        .trim();

      if (/^Set\s+\d+\s*•/i.test(withoutOldLevel)) {
        question.s = withoutOldLevel.replace(/^(Set\s+\d+)\s*•\s*/i, `$1 • ${bloom.name} • `);
      } else {
        question.s = `Set ${setNumber} • ${bloom.name}${withoutOldLevel ? ` • ${withoutOldLevel}` : ''}`;
      }
    });
  });
})();
