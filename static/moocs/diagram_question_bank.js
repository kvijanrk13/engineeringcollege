/* Add diagram-based practice to every MOOCS set after all other banks load. */
(function () {
  'use strict';

  const FIRST_QUESTION = 40;
  const UNIT_NAMES = {
    0: 'General Aptitude',
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
  const COLORS = ['#2563eb', '#16a34a', '#d97706', '#7c3aed', '#dc2626', '#0891b2'];

  function svgData(svg) {
    return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
  }

  const sixCycle = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]];
  const sixPositions = [[120, 88], [180, 138], [180, 205], [120, 235], [60, 205], [60, 138]];

  function isomorphismDiagram(isomorphic) {
    const permutation = [2, 5, 1, 4, 0, 3];
    const permutedCycle = sixCycle.map(([from, to]) => [permutation[from], permutation[to]]);
    const twoTriangles = [[0, 1], [1, 2], [2, 0], [3, 4], [4, 5], [5, 3]];
    const edgeMarkup = (edges, offset) => edges.map(([from, to]) => {
      const [x1, y1] = sixPositions[from];
      const [x2, y2] = sixPositions[to];
      return `<line x1="${x1 + offset}" y1="${y1 + 10}" x2="${x2 + offset}" y2="${y2 + 10}" stroke="#607b96" stroke-width="3"/>`;
    }).join('');
    const vertexMarkup = offset => sixPositions.map(([x, y], index) =>
      `<circle cx="${x + offset}" cy="${y + 10}" r="17" fill="${COLORS[index]}" stroke="#fff" stroke-width="3"/><text x="${x + offset}" y="${y + 15}" text-anchor="middle" font-family="Arial" font-size="14" font-weight="700" fill="#fff">${String.fromCharCode(65 + index)}</text>`
    ).join('');
    return svgData(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 300" role="img"><rect width="760" height="300" rx="18" fill="#f8fbff"/><text x="190" y="28" text-anchor="middle" font-family="Arial" font-size="18" font-weight="700" fill="#123">Graph G</text><text x="570" y="28" text-anchor="middle" font-family="Arial" font-size="18" font-weight="700" fill="#123">Graph H</text>${edgeMarkup(sixCycle, 70)}${vertexMarkup(70)}${edgeMarkup(isomorphic ? permutedCycle : twoTriangles, 450)}${vertexMarkup(450)}</svg>`);
  }

  function coloringDiagram(kind) {
    const positions = kind === 'path'
      ? [[100, 160], [210, 160], [320, 160], [430, 160]]
      : kind === 'square'
        ? [[140, 90], [360, 90], [360, 210], [140, 210]]
        : kind === 'odd-cycle'
          ? [[250, 65], [390, 115], [340, 230], [160, 230], [110, 115]]
          : [[250, 60], [390, 190], [110, 190], [250, 145]];
    let edges;
    if (kind === 'path') edges = [[0, 1], [1, 2], [2, 3]];
    else if (kind === 'square') edges = [[0, 1], [1, 2], [2, 3], [3, 0]];
    else if (kind === 'odd-cycle') edges = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]];
    else edges = [[0, 1], [1, 2], [2, 0], [3, 0], [3, 1], [3, 2]];
    const count = positions.length;
    const edgeMarkup = edges.map(([from, to]) => {
      const [x1, y1] = positions[from];
      const [x2, y2] = positions[to];
      return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#607b96" stroke-width="4"/>`;
    }).join('');
    const vertexMarkup = positions.map(([x, y], index) =>
      `<circle cx="${x}" cy="${y}" r="22" fill="#dbeafe" stroke="#2563eb" stroke-width="3"/><text x="${x}" y="${y + 5}" text-anchor="middle" font-family="Arial" font-size="15" font-weight="700" fill="#123">${String.fromCharCode(65 + index)}</text>`
    ).join('');
    const title = kind === 'path' ? 'Path graph P₄' : kind === 'square' ? 'Cycle graph C₄' : kind === 'odd-cycle' ? 'Cycle graph C₅' : 'Planar graph K₄';
    return svgData(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 280" role="img"><rect width="500" height="280" rx="18" fill="#f8fbff"/><text x="250" y="28" text-anchor="middle" font-family="Arial" font-size="19" font-weight="700" fill="#123">${title}</text>${edgeMarkup}${vertexMarkup}</svg>`);
  }

  function graphicsTranslationDiagram() {
    return svgData('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 300" role="img"><rect width="520" height="300" rx="18" fill="#f8fbff"/><text x="260" y="28" text-anchor="middle" font-family="Arial" font-size="19" font-weight="700" fill="#123">2D Translation by vector (3, 2)</text><path d="M100 230 180 230 180 150 100 150Z" fill="#dbeafe" stroke="#2563eb" stroke-width="4"/><text x="140" y="202" text-anchor="middle" font-family="Arial" font-size="17" font-weight="700" fill="#123">P(1,1)</text><path d="M260 150 340 150 340 70 260 70Z" fill="#dcfce7" stroke="#16a34a" stroke-width="4"/><text x="300" y="122" text-anchor="middle" font-family="Arial" font-size="17" font-weight="700" fill="#123">P′(4,3)</text><path d="M185 205 250 145" fill="none" stroke="#d97706" stroke-width="4"/><path d="m240 146 12-3-3 12" fill="none" stroke="#d97706" stroke-width="4"/><text x="225" y="195" font-family="Arial" font-size="15" fill="#92400e">(+3,+2)</text></svg>');
  }

  function itemsetLatticeDiagram() {
    return svgData('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 300" role="img"><rect width="520" height="300" rx="18" fill="#f8fbff"/><text x="260" y="28" text-anchor="middle" font-family="Arial" font-size="19" font-weight="700" fill="#123">Frequent-itemset lattice</text><g stroke="#7890a8" stroke-width="3"><path d="M260 90 130 155M260 90 260 155M260 90 390 155M130 195v35M130 195 260 230M260 195 130 230M260 195 390 230M390 195 260 230M390 195v35"/></g><g fill="#dcfce7" stroke="#16a34a" stroke-width="3"><rect x="202" y="48" width="116" height="42" rx="10"/><rect x="83" y="145" width="94" height="50" rx="10"/><rect x="213" y="145" width="94" height="50" rx="10"/><rect x="343" y="145" width="94" height="50" rx="10"/></g><g fill="#dbeafe" stroke="#2563eb" stroke-width="2"><rect x="83" y="230" width="94" height="42" rx="9"/><rect x="213" y="230" width="94" height="42" rx="9"/><rect x="343" y="230" width="94" height="42" rx="9"/></g><g font-family="Arial" font-size="15" font-weight="700" text-anchor="middle" fill="#123"><text x="260" y="75">{A,B,C}</text><text x="130" y="176">{A,B}</text><text x="260" y="176">{A,C}</text><text x="390" y="176">{B,C}</text><text x="130" y="256">{A}</text><text x="260" y="256">{B}</text><text x="390" y="256">{C}</text></g></svg>');
  }

  function uniqueOptions(correct, wrong) {
    return [...new Set([String(correct), ...wrong.map(String)])].slice(0, 4);
  }

  function shuffle(values, seed) {
    const result = values.slice();
    let state = seed >>> 0;
    for (let index = result.length - 1; index > 0; index -= 1) {
      state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
      const swapIndex = state % (index + 1);
      [result[index], result[swapIndex]] = [result[swapIndex], result[index]];
    }
    return result;
  }

  function optionsFor(set, slot, correct, wrong, support) {
    const correctIndex = (set + slot * 3) % 4;
    const distractors = shuffle(uniqueOptions(correct, wrong).filter(option => option !== String(correct)), set * 97 + slot * 31);
    while (distractors.length < 3) distractors.push(`None of these (${distractors.length + 1})`);
    const options = distractors.slice(0, 3);
    options.splice(correctIndex, 0, String(correct));
    const position = (FIRST_QUESTION + slot) % 10;
    let answers = null;
    let mode = 'selection';
    let suffix = '';
    if (position === 8) {
      const supportIndex = (correctIndex + 1) % 4;
      options[supportIndex] = support;
      answers = [correctIndex, supportIndex].sort((left, right) => left - right);
      mode = 'multi';
      suffix = ' Select both correct statements.';
    } else if (position === 9) {
      mode = 'fill';
      suffix = ' Enter the exact answer.';
    }
    return { options, correctIndex, answers, mode, suffix };
  }

  function question(set, slot, topic, unit, stem, correct, wrong, explanation, image, alt, support) {
    const built = optionsFor(set, slot, correct, wrong, support);
    const questionNumber = FIRST_QUESTION + slot + 1;
    const correctText = built.mode === 'multi'
      ? `The keyed answer is “${correct}”; the other correct option states: “${support}”.`
      : `The keyed answer is “${correct}”.`;
    return {
      s: `Set ${set} • Diagram • ${topic}`,
      t: topic,
      q: `[S${set}-Q${questionNumber}] ${stem}${built.suffix}`,
      img: image,
      alt,
      o: built.options,
      a: built.correctIndex,
      answers: built.answers,
      mode: built.mode,
      e: `${explanation} ${correctText}`,
      unit,
      unitName: UNIT_NAMES[unit],
      level: questionNumber <= 34 ? 'Level 1' : questionNumber <= 67 ? 'Level 2' : 'Level 3',
    };
  }

  function buildQuestions(set) {
    const isoIsomorphic = set % 2 === 0;
    const colorTypes = ['path', 'square', 'odd-cycle', 'clique'];
    const colorType = colorTypes[(set - 1) % colorTypes.length];
    const chromaticNumber = { path: 2, square: 2, 'odd-cycle': 3, clique: 4 }[colorType];
    const image = name => `/static/moocs/diagrams/${name}`;
    return [
      question(set, 0, 'Graph Theory — Isomorphism', 1,
        'Are the two graphs in the diagram isomorphic?',
        isoIsomorphic ? 'Yes — a relabelling preserves every adjacency.' : 'No — one graph is connected and the other has two components.',
        isoIsomorphic
          ? ['No — the vertex labels differ.', 'Yes — any two graphs with six vertices are isomorphic.', 'No — the graphs have different numbers of edges.']
          : ['Yes — both graphs have six vertices.', 'Yes — both graphs have six edges.', 'No — vertex labels are different.'],
        isoIsomorphic
          ? 'The second graph is obtained by permuting the labels of the same six-cycle, so the adjacency relation is preserved.'
          : 'The left graph is one connected six-cycle; the right graph consists of two separate triangles. Connectivity is preserved by isomorphism, so these graphs are not isomorphic.',
        isomorphismDiagram(isoIsomorphic),
        'Two labelled six-vertex graphs shown side by side for an isomorphism comparison.',
        'Graph isomorphism preserves adjacency even when vertex labels change.'),
      question(set, 1, 'Graph Theory — Chromatic Number', 1,
        'What is the chromatic number of the graph shown?',
        String(chromaticNumber),
        ['1', '2', '3', '4'].filter(value => value !== String(chromaticNumber)),
        `A proper vertex colouring assigns different colours to adjacent vertices. The ${colorType === 'odd-cycle' ? 'odd cycle requires three colours' : colorType === 'clique' ? 'four mutually adjacent vertices require four colours' : 'graph is bipartite and requires two colours'}, so its chromatic number is ${chromaticNumber}.`,
        coloringDiagram(colorType),
        `A ${colorType} graph diagram whose vertices must be coloured so adjacent vertices differ.`,
        'A proper colouring gives every adjacent pair different colours.'),
      question(set, 2, 'Graph Theory — Four-Color Problem', 1,
        'The diagram is a planar region-adjacency graph. What is the minimum number of colours needed so adjacent regions differ?',
        '4',
        ['1', '2', '3'],
        'The graph shown is K₄ in a planar embedding. Every pair of its four vertices is adjacent, so all four require distinct colours; this is a planar example that attains the four-colour bound.',
        coloringDiagram('clique'),
        'Planar embedding of K4 representing four regions that are pairwise adjacent.',
        'The four-colour theorem states that every planar map can be coloured with at most four colours.'),
      question(set, 3, 'Computer Architecture', 2,
        'How many processing stages are labelled in the instruction pipeline diagram?',
        '5', ['4', '6', '3'],
        'The pipeline shows IF, ID, EX, MEM and WB. Counting these labelled stages gives five.',
        image('pipeline.svg'), 'Five-stage instruction pipeline with IF, ID, EX, MEM and WB stages.',
        'Pipeline stages overlap across instructions to improve throughput.'),
      question(set, 4, 'Programming', 3,
        'In the array-pointer diagram, which element does p + 2 point to when p points to a[0]?',
        'a[2]', ['a[1]', 'a[3]', 'a[4]'],
        'Pointer arithmetic advances by elements of the pointed-to type. Adding two to a pointer at a[0] addresses a[2].',
        image('c-array-pointer.svg'), 'Array pointer p starts at a[0], while p plus two points at a[2].',
        'Pointer addition counts array elements rather than bytes.'),
      question(set, 5, 'Database Systems', 4,
        'The ER diagram shows an M:N relationship between STUDENT and COURSE. How is it normally represented relationally?',
        'A junction relation containing foreign keys to STUDENT and COURSE',
        ['A single foreign key in STUDENT only', 'A single foreign key in COURSE only', 'A self-referencing key in both tables'],
        'An M:N relationship cannot be represented by a single foreign key on either entity table. A separate relation stores the keys of both participating entities.',
        image('dbms-er.svg'), 'Student and Course entities connected by an M:N Enrolls relationship.',
        'A junction relation stores one row per entity-pair association.'),
      question(set, 6, 'Operating Systems', 5,
        'According to the process-state diagram, what event moves a running process to the waiting state?',
        'An I/O wait request',
        ['The scheduler dispatches it', 'The process is admitted to the ready queue', 'The process exits normally'],
        'The outgoing transition from RUNNING to WAITING is labelled I/O wait; dispatch moves READY to RUNNING instead.',
        image('os-process-states.svg'), 'Process-state diagram with a running-to-waiting I/O wait transition.',
        'A blocked process returns to READY when its I/O completes.'),
      question(set, 7, 'Software Engineering', 6,
        'The flow graph has E = 6 edges and N = 5 nodes. Using V(G) = E − N + 2, what is its cyclomatic complexity?',
        '3', ['2', '4', '5'],
        'Cyclomatic complexity is E − N + 2P. For this single connected component, P = 1, so V(G) = 6 − 5 + 2 = 3.',
        image('se-flow-graph.svg'), 'Control-flow graph with five numbered nodes and six directed edges.',
        'Cyclomatic complexity counts linearly independent paths in a control-flow graph.'),
      question(set, 8, 'Data Structures and Algorithms', 7,
        'In the binary search tree diagram, what are the two children of the root node 50?',
        '30 and 70', ['20 and 80', '30 and 40', '60 and 80'],
        'The root is 50. Its left child is 30 and its right child is 70, as shown by the two edges leaving the root.',
        image('bst.svg'), 'Binary search tree rooted at 50 with direct children 30 and 70.',
        'A BST stores smaller keys in the left subtree and larger keys in the right subtree.'),
      question(set, 9, 'Compiler Design', 8,
        'Which compiler phase follows lexical analysis in the phase diagram?',
        'Syntax analysis', ['Semantic analysis', 'Code generation', 'Register allocation'],
        'The phase sequence shown is lexical analysis, syntax analysis, semantic analysis, then code generation.',
        image('compiler-pipeline.svg'), 'Compiler pipeline from source characters through lexical, syntax and semantic analysis to target code.',
        'Lexical analysis groups source characters into tokens.'),
      question(set, 10, 'Computer Networks', 9,
        'What flags appear in the second message of the TCP handshake diagram?',
        'SYN + ACK', ['SYN only', 'ACK only', 'FIN + ACK'],
        'TCP connection establishment proceeds with SYN, then SYN + ACK, then ACK.',
        image('tcp-handshake.svg'), 'TCP three-way handshake: client SYN, server SYN plus ACK, and client ACK.',
        'The server acknowledges the client SYN while sending its own SYN.'),
      question(set, 11, 'Artificial Intelligence', 10,
        'Which attribute is tested at the root of the decision tree diagram?',
        'Outlook', ['Humidity', 'Temperature', 'Wind'],
        'The root node is labelled Outlook. Humidity appears lower in the tree on one branch.',
        image('ml-decision-tree.svg'), 'Decision tree with Outlook as the root attribute and Humidity on a later branch.',
        'A decision tree routes examples through tests at internal nodes.'),
      question(set, 12, 'General Aptitude — Data Interpretation', 0,
        'According to the bar-chart labels, how much higher is Department A’s pass rate than Department B’s?',
        '15 percentage points', ['15 percent', '20 percentage points', 'Department B is higher by 15 percentage points'],
        'The chart labels Department A at 75% and Department B at 60%. Their difference is 75 − 60 = 15 percentage points.',
        image('general-data-bars.svg'), 'Bar chart comparing Department A at 75% pass rate and Department B at 60%.',
        'A percentage-point difference is calculated by subtracting the two percentages.'),
      question(set, 13, 'Digital Logic', 2,
        'In the XOR truth-table diagram, what is the output for p = 1 and q = 0?',
        '1', ['0', 'p AND q', 'p OR q'],
        'XOR is true when its two inputs differ. The row p = 1, q = 0 therefore has output 1 in the table.',
        image('xor-truth-table.svg'), 'Truth table for p exclusive OR q with the p=1, q=0 output row highlighted.',
        'XOR outputs 1 exactly when its inputs differ.'),
      question(set, 14, 'Computer Graphics', 3,
        'The transformation diagram translates P(1,1) by vector (+3,+2). What are the coordinates of P′?',
        '(4, 3)', ['(3, 2)', '(4, 2)', '(1, 3)'],
        'A translation adds the vector components to the point: (1+3, 1+2) = (4,3), matching the translated square.',
        graphicsTranslationDiagram(), 'A square moves by translation vector (+3,+2) from P(1,1) to P prime (4,3).',
        'Translation adds the same displacement vector to every point.'),
      question(set, 15, 'Data Mining', 4,
        'The lattice marks {A,B,C} as frequent. What must be true of each of its non-empty subsets under the Apriori property?',
        'Every non-empty subset is frequent',
        ['At least one pair must be infrequent', 'Only the single-item subsets must be frequent', 'Subset frequency cannot be inferred'],
        'Support is anti-monotone: every subset of a frequent itemset is frequent. Thus {A,B}, {A,C}, {B,C}, and all singleton subsets must be frequent.',
        itemsetLatticeDiagram(), 'Frequent-itemset lattice showing a frequent three-item set and its pair and singleton subsets.',
        'An infrequent subset lets Apriori prune every superset containing it.'),
      question(set, 16, 'Cryptography', 9,
        'In the Diffie–Hellman exchange diagram, why do Alice and Bob compute the same shared secret?',
        'Both compute g^(ab) mod p',
        ['They transmit their private exponents to each other', 'They use different public moduli', 'The public values A and B are themselves the private keys'],
        'Alice computes B^a = (g^b)^a = g^(ab) mod p; Bob computes A^b = (g^a)^b = g^(ab) mod p. The private exponents remain local.',
        image('crypto-diffie-hellman.svg'), 'Alice and Bob exchange public Diffie–Hellman values and derive the same secret.',
        'The commutativity of exponent multiplication gives both parties the same shared value.'),
      question(set, 17, 'Web Technologies', 3,
        'Which layer lies directly outside CONTENT in the CSS box-model diagram?',
        'PADDING', ['BORDER', 'MARGIN', 'The viewport'],
        'The diagram nests the layers from inside to outside as content, padding, border, and margin. Padding is immediately outside the content box.',
        image('web-box-model.svg'), 'Nested CSS box-model layers: content, padding, border and margin.',
        'CSS box-model order from inner to outer is content, padding, border, then margin.'),
    ];
  }

  for (let set = 1; set <= 400; set += 1) {
    const questions = QUESTION_SETS[set];
    if (!Array.isArray(questions) || questions.length !== 100) {
      throw new Error(`MOOCS diagram bank expected 100 questions in Set ${set}.`);
    }
    buildQuestions(set).forEach((item, slot) => {
      questions[FIRST_QUESTION + slot] = item;
    });
  }
})();
