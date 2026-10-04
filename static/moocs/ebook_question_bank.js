/* Replace a small slice of every paper with original, ebook-informed MCQs.
   Keep the question count and each set's existing paper-specific questions. */
(function () {
  'use strict';

  const MAX_SET = 400;
  const REPLACE_FROM = 80;
  const QUESTIONS_PER_SET = 20;

  const choose = (n, r) => {
    if (r < 0 || r > n) return 0;
    let result = 1;
    for (let index = 1; index <= r; index += 1) {
      result = result * (n - r + index) / index;
    }
    return result;
  };

  const banks = [
    { topic: 'Discrete Mathematics', unit: 1, build: seed => {
      const vertices = 8 + seed % 13;
      const edges = choose(vertices, 2);
      return {
        q: `A simple complete graph has ${vertices} vertices. How many edges does it contain?`,
        correct: String(edges),
        wrong: [String(vertices * vertices), String(vertices * (vertices - 1)), String(edges + vertices)],
        e: `Each edge joins one unordered pair of distinct vertices, so the count is C(${vertices},2) = ${vertices}(${vertices}−1)/2 = ${edges}.`,
      };
    } },
    { topic: 'Discrete Mathematics', unit: 1, build: seed => {
      const variables = 3 + seed % 5;
      return {
        q: `A Boolean function has ${variables} independent binary inputs. How many input rows are in its complete truth table?`,
        correct: String(2 ** variables),
        wrong: [String(variables + 1), String(2 ** variables - 1), String(2 ** (variables + 1))],
        e: `Each of the ${variables} inputs has two possible values, giving 2^${variables} = ${2 ** variables} rows.`,
      };
    } },
    { topic: 'Algorithms', unit: 7, build: () => ({
      q: 'For a divide-and-conquer recurrence T(n)=2T(n/2)+Θ(n), with constant-size base cases, what is the asymptotic running time?',
      correct: 'Θ(n log n)',
      wrong: ['Θ(n)', 'Θ(log n)', 'Θ(n²)'],
      e: 'At each recursion depth the combined non-recursive work is Θ(n), and there are Θ(log n) levels, yielding Θ(n log n).',
    }) },
    { topic: 'Algorithms', unit: 7, build: seed => {
      const size = 16 + seed % 113;
      const maximum = Math.floor(Math.log2(size)) + 1;
      return {
        q: `A successful binary search examines at most how many array elements when the sorted array has ${size} elements?`,
        correct: String(maximum),
        wrong: [String(maximum - 1), String(maximum + 1), String(size)],
        e: `Each comparison halves the remaining interval. The maximum is floor(log₂(${size}))+1 = ${maximum} comparisons.`,
      };
    } },
    { topic: 'Algorithms', unit: 7, build: () => ({
      q: 'Which traversal finds a shortest path in an unweighted graph when all edges have equal cost?',
      correct: 'Breadth-first search',
      wrong: ['Depth-first search', 'Inorder traversal', 'Topological sorting'],
      e: 'Breadth-first search explores vertices in nondecreasing distance from the source, so its first discovery gives a shortest path in an unweighted graph.',
    }) },
    { topic: 'Data Structures', unit: 7, build: seed => {
      const keys = 30 + seed % 71;
      const slots = 2 * keys;
      return {
        q: `A hash table stores ${keys} keys in ${slots} slots. What is its load factor?`,
        correct: (keys / slots).toFixed(2),
        wrong: [(slots / keys).toFixed(2), ((keys + 1) / slots).toFixed(2), ((keys - 1) / slots).toFixed(2)],
        e: `The load factor is α = number of stored keys / number of slots = ${keys}/${slots} = ${(keys / slots).toFixed(2)}.`,
      };
    } },
    { topic: 'Data Structures', unit: 7, build: () => ({
      q: 'Which structure supports removing the oldest item and adding new items at the opposite end?',
      correct: 'Queue',
      wrong: ['Stack', 'Binary search tree', 'Disjoint-set forest'],
      e: 'A queue follows FIFO order: insertion is at the rear and removal is at the front.',
    }) },
    { topic: 'Data Structures', unit: 7, build: () => ({
      q: 'Why are the leaves of a B+ tree commonly linked in key order?',
      correct: 'To support efficient sequential and range scans',
      wrong: ['To eliminate internal index nodes', 'To make every search examine every leaf', 'To store duplicate copies of every record in the root'],
      e: 'Linked leaves let a range query move through adjacent key ranges without restarting a tree search for every result.',
    }) },
    { topic: 'Database Systems', unit: 4, build: () => ({
      q: 'In a left outer join, what appears for a left-side row with no matching right-side row?',
      correct: 'The left row is retained and right-side columns are NULL',
      wrong: ['The row is discarded', 'The row is paired with every right-side row', 'The query must fail'],
      e: 'A left outer join preserves every left input row and supplies NULLs for unmatched right-side attributes.',
    }) },
    { topic: 'Database Systems', unit: 4, build: () => ({
      q: 'What condition distinguishes a candidate key from a non-minimal superkey?',
      correct: 'No proper subset of the candidate key is a superkey',
      wrong: ['It must contain every attribute in the relation', 'It may contain duplicate tuples', 'It must be a foreign key in another relation'],
      e: 'A candidate key is a minimal superkey: it uniquely identifies tuples, and removing any of its attributes loses that property.',
    }) },
    { topic: 'Database Systems', unit: 4, build: () => ({
      q: 'For conflict serializability, what does a directed cycle in a schedule’s precedence graph imply?',
      correct: 'The schedule is not conflict-serializable',
      wrong: ['The schedule is conflict-serializable', 'Every transaction is read-only', 'The schedule is necessarily recoverable'],
      e: 'A schedule is conflict-serializable exactly when its precedence graph is acyclic.',
    }) },
    { topic: 'Data Mining', unit: 4, build: seed => {
      const joint = 8 + seed % 23;
      const antecedent = joint + 9 + seed % 31;
      return {
        q: `An association rule X→Y appears ${joint} times, while X appears ${antecedent} times. What is the rule confidence as a percentage?`,
        correct: `${(100 * joint / antecedent).toFixed(1)}%`,
        wrong: [`${(100 * joint / (joint + antecedent)).toFixed(1)}%`, `${(100 * antecedent / joint).toFixed(1)}%`, `${(100 * joint / (antecedent + 10)).toFixed(1)}%`],
        e: `Confidence(X→Y) = support(X∪Y)/support(X) = ${joint}/${antecedent} = ${(100 * joint / antecedent).toFixed(1)}%.`,
      };
    } },
    { topic: 'Operating Systems', unit: 5, build: seed => {
      const exponent = 10 + seed % 7;
      return {
        q: `A system uses a page size of 2^${exponent} bytes. How many low-order address bits identify the offset within a page?`,
        correct: String(exponent),
        wrong: [String(exponent - 1), String(exponent + 1), String(2 ** exponent)],
        e: `Selecting one of 2^${exponent} byte positions requires log₂(2^${exponent}) = ${exponent} offset bits.`,
      };
    } },
    { topic: 'Operating Systems', unit: 5, build: seed => {
      const first = 2 + seed % 8;
      const second = 3 + (seed * 3) % 9;
      const third = 4 + (seed * 5) % 11;
      const average = (first + (first + second)) / 3;
      return {
        q: `FCFS schedules CPU bursts of ${first}, ${second}, and ${third} time units in that order. What is the average waiting time?`,
        correct: average.toFixed(2),
        wrong: [(average + 0.5).toFixed(2), (average + 1).toFixed(2), (average - 0.5).toFixed(2)],
        e: `The waiting times are 0, ${first}, and ${first + second}; their mean is (${first + first + second})/3 = ${average.toFixed(2)}.`,
      };
    } },
    { topic: 'Operating Systems', unit: 5, build: () => ({
      q: 'What is the principal purpose of a counting semaphore?',
      correct: 'To coordinate access to a resource with a bounded number of instances',
      wrong: ['To translate virtual addresses into physical addresses', 'To select the next disk cylinder', 'To replace a process control block'],
      e: 'A counting semaphore tracks available instances and supports atomic wait/signal operations for synchronization.',
    }) },
    { topic: 'UNIX Systems Programming', unit: 5, build: () => ({
      q: 'Immediately after fork(), how do the parent and child file descriptors refer to opened files?',
      correct: 'They refer to corresponding open-file descriptions and share the file offset',
      wrong: ['The child inherits no descriptors', 'Each descriptor has an unrelated open-file description and offset', 'All descriptors are closed in the parent'],
      e: 'The child receives descriptor copies that refer to the same open-file descriptions as the parent, so operations can share file offsets.',
    }) },
    { topic: 'UNIX Systems Programming', unit: 5, build: () => ({
      q: 'What is the usual data-flow property of the byte stream created by the POSIX pipe() call?',
      correct: 'It is unidirectional, with one read end and one write end',
      wrong: ['It is a bidirectional message queue', 'It preserves record boundaries for arbitrary writes', 'It is a shared-memory mapping'],
      e: 'A pipe has distinct read and write file descriptors and transports a byte stream in one direction; it does not preserve general message boundaries.',
    }) },
    { topic: 'C Programming', unit: 3, build: seed => {
      const elements = 3 + seed % 8;
      return {
        q: `In C, adding ${elements} to a pointer to an element of type int advances it by how many bytes?`,
        correct: `${elements} × sizeof(int) bytes`,
        wrong: [`${elements} bytes`, `sizeof(int) bytes`, `${elements + 1} × sizeof(int) bytes`],
        e: 'Pointer arithmetic is scaled by the size of the pointed-to type, so adding k advances by k elements, or k×sizeof(int) bytes here.',
      };
    } },
    { topic: 'C Programming', unit: 3, build: () => ({
      q: 'In a C function parameter declaration, what happens to a parameter declared as an array type?',
      correct: 'It is adjusted to a pointer parameter',
      wrong: ['The complete array is copied into the function', 'It becomes a variable-length array with automatic copying', 'It is converted to a structure'],
      e: 'In a function parameter list, an array parameter declaration is adjusted to a pointer to its first element; the array length is not passed implicitly.',
    }) },
    { topic: 'C++ Programming', unit: 3, build: () => ({
      q: 'When deleting a derived object through a base-class pointer, what should a polymorphic base class normally provide?',
      correct: 'A virtual destructor',
      wrong: ['A pure virtual data member', 'A private constructor only', 'A static destructor'],
      e: 'A virtual destructor ensures destruction dispatches through the dynamic type when an object is deleted through a base pointer.',
    }) },
    { topic: 'Java Programming', unit: 3, build: () => ({
      q: 'Which statement correctly distinguishes Java method overloading from overriding?',
      correct: 'Overloading is selected from the declared parameter signatures; overriding dispatches by the runtime object type',
      wrong: ['Both are selected only by the runtime object type', 'Overriding requires different parameter lists in one class', 'Overloading is possible only for constructors'],
      e: 'Overload resolution uses compile-time signatures; an overridden instance method is dynamically dispatched according to the receiver object.',
    }) },
    { topic: 'Python Programming', unit: 3, build: () => ({
      q: 'In Python, what does the expression a is b test?',
      correct: 'Whether a and b refer to the same object',
      wrong: ['Whether a and b have equal values', 'Whether a is a subclass of b', 'Whether a and b have the same printed representation'],
      e: 'The is operator tests object identity. Equality of values is tested with ==.',
    }) },
    { topic: 'Python Programming', unit: 3, build: seed => {
      const first = 2 + seed % 7;
      const second = first + 3;
      return {
        q: `After executing x=[${first}]; y=x; y.append(${second}), what is x?`,
        correct: `[${first}, ${second}]`,
        wrong: [`[${first}]`, `[${second}]`, `[${first}, ${first}]`],
        e: 'Assignment y=x creates another reference to the same mutable list; appending through y changes the object also referenced by x.',
      };
    } },
    { topic: 'Object-Oriented Programming', unit: 3, build: () => ({
      q: 'What does the Liskov substitution principle require of a subtype?',
      correct: 'It should be usable wherever its supertype is expected without breaking the client’s correctness',
      wrong: ['It must expose every implementation detail of its supertype', 'It must inherit from exactly two classes', 'It must replace all inherited methods with static methods'],
      e: 'The substitution principle requires subtype behavior to preserve the expectations clients have of the base type.',
    }) },
    { topic: 'Algorithms', unit: 7, build: seed => {
      const calls = 5 + seed % 12;
      return {
        q: `A recursive routine makes ${calls} nested calls before reaching its base case. What is the maximum number of simultaneously active routine frames, ignoring the caller?`,
        correct: String(calls),
        wrong: [String(calls - 1), String(2 ** calls), '1'],
        e: `Each nested call remains active until the base case returns, so the call stack contains one frame per nested call: ${calls}.`,
      };
    } },
    { topic: 'Software Engineering', unit: 6, build: seed => {
      const nodes = 8 + seed % 14;
      const edges = nodes + 3 + (seed * 3) % 12;
      return {
        q: `A connected control-flow graph has ${nodes} nodes and ${edges} edges. What is its cyclomatic complexity?`,
        correct: String(edges - nodes + 2),
        wrong: [String(edges - nodes + 1), String(edges + nodes - 2), String(edges - nodes)],
        e: `For one connected graph, V(G)=E−N+2=${edges}−${nodes}+2=${edges - nodes + 2}.`,
      };
    } },
    { topic: 'Software Testing', unit: 6, build: () => ({
      q: 'What extra obligation does branch coverage impose beyond executing every statement?',
      correct: 'Exercise each decision outcome, including true and false outcomes where applicable',
      wrong: ['Execute every possible input value', 'Run every statement exactly twice', 'Prove that no defects remain'],
      e: 'Branch coverage requires each control-flow decision outcome to be taken; statement coverage alone can miss an unexecuted branch.',
    }) },
    { topic: 'Software Engineering', unit: 6, build: () => ({
      q: 'What is the main purpose of a requirements traceability matrix?',
      correct: 'Link requirements to their design, implementation, and verification evidence',
      wrong: ['Replace the project schedule', 'Automatically prove every requirement is correct', 'Store only source-code comments'],
      e: 'Traceability links each requirement across lifecycle artifacts, helping assess coverage and the impact of changes.',
    }) },
    { topic: 'Computer Networks', unit: 9, build: seed => {
      const hostBits = 4 + seed % 5;
      return {
        q: `An IPv4 subnet reserves ${hostBits} host bits. Under the conventional network/broadcast reservation, how many usable host addresses does it provide?`,
        correct: String(2 ** hostBits - 2),
        wrong: [String(2 ** hostBits), String(2 ** hostBits - 1), String(2 ** (hostBits - 1) - 2)],
        e: `There are 2^${hostBits} total addresses; subtract the network and broadcast addresses to obtain ${2 ** hostBits}−2 = ${2 ** hostBits - 2}.`,
      };
    } },
    { topic: 'Computer Networks', unit: 9, build: seed => {
      const seq = 1000 + seed % 5000;
      const length = 20 + seed % 91;
      return {
        q: `A TCP segment begins with sequence number ${seq} and carries ${length} data bytes. What acknowledgment number confirms receipt of all its data, assuming no wraparound?`,
        correct: String(seq + length),
        wrong: [String(seq + length - 1), String(seq), String(seq + 1)],
        e: `TCP acknowledges the next byte expected, so the acknowledgment is ${seq}+${length} = ${seq + length}.`,
      };
    } },
    { topic: 'Data Communications', unit: 9, build: seed => {
      const channels = 3 + seed % 8;
      return {
        q: `A fiber system sends ${channels} independent optical channels simultaneously using distinct wavelengths. Which multiplexing technique is being used?`,
        correct: 'Wavelength-division multiplexing',
        wrong: ['Time-division multiplexing', 'Code-division multiple access', 'Frequency-division multiplexing on copper pairs'],
        e: 'Wavelength-division multiplexing carries multiple optical channels on different wavelengths in the same fiber.',
      };
    } },
    { topic: 'Cloud Computing', unit: 10, build: () => ({
      q: 'Which cloud service model gives a customer virtual machines, storage, and networking while leaving the operating system under customer management?',
      correct: 'Infrastructure as a Service (IaaS)',
      wrong: ['Software as a Service (SaaS)', 'Platform as a Service (PaaS)', 'Function as a Service only'],
      e: 'IaaS exposes configurable computing infrastructure; customers typically manage the guest operating system and applications.',
    }) },
    { topic: 'Cloud Computing', unit: 10, build: seed => {
      const demand = 2 + seed % 8;
      return {
        q: `A cloud service automatically adds instances during a ${demand}-fold traffic surge and removes them when demand falls. Which cloud property does this illustrate?`,
        correct: 'Rapid elasticity',
        wrong: ['Measured service only', 'Resource pooling only', 'Broad network access only'],
        e: 'Rapid elasticity scales provisioned resources outward and inward in response to workload demand.',
      };
    } },
    { topic: 'Information Security', unit: 9, build: () => ({
      q: 'Why does a plain cryptographic hash not by itself authenticate a message sent over an attacker-controlled channel?',
      correct: 'An attacker can replace both the message and its unkeyed hash',
      wrong: ['A hash always encrypts the message', 'Hashes cannot detect accidental changes', 'A hash requires a private key to be computed'],
      e: 'An unkeyed hash detects a mismatch only if the expected digest is trusted; an attacker can recompute the digest after altering the message.',
    }) },
    { topic: 'Cryptography', unit: 9, build: () => ({
      q: 'What secret material is required by a standard message authentication code such as HMAC?',
      correct: 'A shared secret key',
      wrong: ['Only the sender’s public key', 'A different private key for every byte', 'No secret material'],
      e: 'HMAC combines a cryptographic hash with a shared secret key to provide message authentication and integrity.',
    }) },
    { topic: 'Information Security', unit: 9, build: () => ({
      q: 'Which CIA-triad property is primarily violated when an unauthorized person reads confidential records?',
      correct: 'Confidentiality',
      wrong: ['Integrity', 'Availability', 'Non-repudiation'],
      e: 'Confidentiality prevents unauthorized disclosure; integrity and availability concern unauthorized modification and disruption of access.',
    }) },
    { topic: 'Artificial Intelligence', unit: 10, build: () => ({
      q: 'What property of a heuristic supports A* tree search returning a least-cost solution when the goal test is applied on node removal?',
      correct: 'Admissibility: it never overestimates the remaining optimal cost',
      wrong: ['Consistency with every non-optimal path', 'A strictly positive estimate at every goal', 'Overestimation by a constant factor'],
      e: 'An admissible heuristic is a lower bound on the remaining optimal cost, which is the key condition for optimality in A* tree search.',
    }) },
    { topic: 'Machine Learning', unit: 10, build: seed => {
      const tp = 20 + seed % 31;
      const fp = 3 + (seed * 3) % 17;
      return {
        q: `A classifier has TP=${tp} and FP=${fp}. What is its precision?`,
        correct: (tp / (tp + fp)).toFixed(3),
        wrong: [(tp / (tp + 20 + seed % 11)).toFixed(3), (fp / (tp + fp)).toFixed(3), ((tp + fp) / tp).toFixed(3)],
        e: `Precision=TP/(TP+FP)=${tp}/(${tp}+${fp})=${(tp / (tp + fp)).toFixed(3)}.`,
      };
    } },
    { topic: 'Machine Learning', unit: 10, build: () => ({
      q: 'Why must a test set remain separate from model fitting and hyperparameter selection?',
      correct: 'To provide an unbiased estimate on data not used to make modeling decisions',
      wrong: ['To increase the number of training examples implicitly', 'To guarantee zero training error', 'To make feature scaling unnecessary'],
      e: 'Repeatedly using test outcomes to choose a model leaks information and makes the reported test performance optimistic.',
    }) },
    { topic: 'Natural Language Processing', unit: 10, build: seed => {
      const contextCount = 12 + seed % 37;
      const nextCount = 3 + seed % 9;
      return {
        q: `In an unsmoothed bigram language model, a context occurs ${contextCount} times and is followed by the word “data” ${nextCount} times. What is P(data | context)?`,
        correct: (nextCount / contextCount).toFixed(3),
        wrong: [(contextCount / nextCount).toFixed(3), (nextCount / (contextCount + nextCount)).toFixed(3), (1 / contextCount).toFixed(3)],
        e: `The maximum-likelihood bigram estimate is count(context,data)/count(context) = ${nextCount}/${contextCount} = ${(nextCount / contextCount).toFixed(3)}.`,
      };
    } },
    { topic: 'Natural Language Processing', unit: 10, build: () => ({
      q: 'Why are subword tokenizers useful for words that did not occur in the training corpus?',
      correct: 'They can represent an unseen word as a sequence of known subword units',
      wrong: ['They require a separate vocabulary entry for every possible word', 'They remove word order from every model', 'They guarantee the word meaning is known'],
      e: 'Subword segmentation can compose an out-of-vocabulary word from learned pieces, reducing unknown-token cases without guaranteeing its semantics.',
    }) },
    { topic: 'Natural Language Processing', unit: 10, build: () => ({
      q: 'What does self-attention allow a Transformer token representation to use?',
      correct: 'Weighted information from other token positions in the same sequence',
      wrong: ['Only the immediately preceding token', 'Only a fixed-size recurrent hidden state', 'Only token-frequency counts from training'],
      e: 'Self-attention computes query-key weights across sequence positions and combines the corresponding value representations.',
    }) },
    { topic: 'Web Technologies', unit: 3, build: seed => {
      const ids = 1 + seed % 3;
      const classes = 1 + (seed * 3) % 5;
      const types = 1 + (seed * 7) % 6;
      return {
        q: `A CSS selector contains ${ids} ID selectors, ${classes} class/attribute/pseudo-class selectors, and ${types} type/pseudo-element selectors. What is its specificity tuple?`,
        correct: `(${ids}, ${classes}, ${types})`,
        wrong: [`(${ids + 1}, ${classes}, ${types})`, `(${ids}, ${classes + 1}, ${types})`, `(${ids}, ${classes}, ${types + 1})`],
        e: `CSS specificity is compared lexicographically as (IDs, class-like selectors, type-like selectors), giving (${ids}, ${classes}, ${types}).`,
      };
    } },
    { topic: 'Web Technologies', unit: 3, build: () => ({
      q: 'In a typical Node.js application, what does the event loop do while asynchronous I/O is pending?',
      correct: 'It can run other ready callbacks instead of blocking on that I/O',
      wrong: ['It starts one operating-system thread for every JavaScript callback', 'It makes all CPU-bound JavaScript execute in parallel', 'It disables completion callbacks'],
      e: 'The event loop dispatches ready work while asynchronous operations complete; it does not make CPU-bound JavaScript automatically parallel.',
    }) },
    { topic: 'Web Technologies', unit: 3, build: () => ({
      q: 'In the MERN stack, which component is the document-oriented database?',
      correct: 'MongoDB',
      wrong: ['Express', 'React', 'Node.js'],
      e: 'MERN names MongoDB, Express, React, and Node.js; MongoDB is the database, Express and Node form the server side, and React is the UI library.',
    }) },
    { topic: 'Artificial Intelligence', unit: 10, build: () => ({
      q: 'In a rule-based expert system, what is the inference engine primarily responsible for?',
      correct: 'Applying rules to known facts to derive conclusions',
      wrong: ['Storing all raw sensor signals as source code', 'Rendering the user interface only', 'Compiling the operating system kernel'],
      e: 'The inference engine matches facts against knowledge-base rules and derives new facts or recommendations.',
    }) },
  ];

  for (let set = 1; set <= MAX_SET; set += 1) {
    const questions = QUESTION_SETS[set];
    if (!Array.isArray(questions) || questions.length !== 100) {
      throw new Error(`MOOCS ebook overlay expected 100 questions in Set ${set}.`);
    }

    for (let slot = 0; slot < QUESTIONS_PER_SET; slot += 1) {
      const index = REPLACE_FROM + slot;
      const seed = set * 100 + index;
      const template = banks[(set * 7 + slot * 13) % banks.length];
      const draft = template.build(seed);
      const correctIndex = (set * 7 + slot * 3) % 4;
      const wrong = draft.wrong.slice();
      const options = [];
      for (let attempt = 0; options.length < 3 && attempt < wrong.length; attempt += 1) {
        const candidate = String(wrong[(attempt + seed) % wrong.length]);
        if (candidate !== draft.correct && !options.includes(candidate)) options.push(candidate);
      }
      if (options.length !== 3) {
        throw new Error(`MOOCS ebook question ${set}/${index + 1} does not have three distinct distractors.`);
      }
      options.splice(correctIndex, 0, draft.correct);

      questions[index] = {
        s: `Set ${set} • Ebook-informed • ${template.topic}`,
        t: template.topic,
        q: `[S${set}-Q${index + 1}] ${draft.q}`,
        o: options,
        a: correctIndex,
        e: draft.e,
        mode: 'selection',
        level: index < 87 ? 'Level 2' : 'Level 3',
        unit: template.unit,
        unitName: UGC_NET_UNITS[template.unit],
      };
    }
  }
})();
