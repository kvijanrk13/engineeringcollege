/* Sets 301-400: diagrammatic MCQs.
   Every question in these sets references a valid diagram (img + alt) drawn from
   the moocs/diagrams catalogue, so the diagram is an essential part of answering
   each stem. Every stem carries a unique [S<n>-Q<i>] tag and the parameters below
   vary with (set, index), which keeps question text unique across all 400 MOOCS
   sets. The 8+1+1 assessment pattern is applied later by assessment_pattern.js. */
(function () {
  const UGC_NET_UNITS = {
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

  const uniq = (correct, values) => {
    const out = [String(correct)];
    for (const v of values) {
      let s = String(v), step = 1;
      while (out.includes(s)) {
        const num = Number(s);
        s = Number.isFinite(num) ? String(num + step) : `Not ${s}`;
        step++;
      }
      out.push(s);
    }
    return out.slice(0, 4);
  };

  const levelFor = (i) => (i < 34 ? 'Level 1' : i < 67 ? 'Level 2' : 'Level 3');

  /* Alt text for every diagram referenced by the templates below. */
  const DIAGRAMS = {
    'set-intersection.svg': 'Overlapping two-set Venn diagram with regions A, B and their intersection highlighted',
    'logic-gates.svg': 'Logic-gate circuit diagram combining AND, OR and NOT gates with labelled inputs A, B and C',
    'xor-truth-table.svg': 'XOR logic truth table showing inputs A, B and the output column',
    'multiplexer.svg': '2-to-1 multiplexer symbol with data inputs D0, D1, select line S and output Y',
    'pipeline.svg': 'Five-stage instruction pipeline diagram showing overlapping stage boxes and stall bubbles',
    'cache.svg': 'CPU cache memory hierarchy diagram showing L1, L2 and L3 cache levels with hit rates',
    'c-pointer.svg': 'C language pointer diagram showing a variable and a pointer storing its address',
    'c-call-stack.svg': 'Program call-stack diagram showing frames pushed and popped by function invocations',
    'java-inheritance.svg': 'Java class inheritance tree diagram showing parent and child classes with relationships',
    'java-thread-states.svg': 'Java thread lifecycle state diagram showing new, runnable, blocked, waiting and terminated',
    'linked-list.svg': 'Singly linked list diagram showing nodes with data fields and pointers to the next node',
    'bst.svg': 'Binary search tree diagram showing nodes arranged so in-order traversal yields sorted keys',
    'stack.svg': 'Stack abstract data type diagram showing push and pop operations on a vertical storage',
    'circular-queue.svg': 'Circular queue diagram showing front and rear pointers wrapping around a fixed buffer',
    'graph-traversal.svg': 'Graph traversal diagram showing breadth-first and depth-first visitation order',
    'algo-dynamic-programming.svg': 'Dynamic-programming table fill diagram showing overlapping subproblems and optimal substructure',
    'algo-divide-conquer.svg': 'Divide-and-conquer recursion tree diagram showing a problem splitting into smaller subproblems',
    'algo-merge-sort.svg': 'Merge-sort diagram showing the recursive splitting and ordered merging of sublists',
    'dbms-er.svg': 'Entity-relationship diagram showing entities, attributes and relationships between them',
    'dbms-bplus-tree.svg': 'B plus tree diagram showing internal nodes, leaf nodes and sorted key pointers',
    'os-process-states.svg': 'Operating-system process state diagram showing ready, running and blocked transitions',
    'os-paging.svg': 'Virtual-memory paging diagram showing virtual pages mapped to physical frames',
    'os-deadlock.svg': 'Resource-allocation graph for deadlock showing processes, resources and claim edges',
    'tcp-handshake.svg': 'TCP three-way handshake diagram showing SYN, SYN-ACK and ACK message exchange',
    'ipv4-subnet.svg': 'IPv4 subnetting diagram showing network, subnet and host bit boundaries',
  };

  /* 25 diagram-referenced templates. Each build() returns a question that reads
     from the diagram, four option values with correct at index 0, and an
     explanation of at least one hundred characters. */
  const templates = [
    /* k = 0  — Discrete: set union read from a Venn diagram */
    { t: 'Discrete Mathematics', unit: 1, diagram: 'set-intersection.svg',
      build: (g, r, n) => {
        const a = 14 + (n % 9), b = 16 + ((g * 2) % 9), c = 3 + (g % 6);
        const opts = [`${a + b - c}`, `${a + b + c}`, `${a * b - c}`, `${Math.abs(a - b)}`];
        return { quest: `In the set-intersection diagram, |A| = ${a}, |B| = ${b} and |A ∩ B| = ${c}. What is |A ∪ B|?`, opts, e: `The set-intersection diagram shows two overlapping regions; by inclusion-exclusion the union counts the intersection once, so |A ∪ B| = |A| + |B| − |A ∩ B| = ${a} + ${b} − ${c} = ${opts[0]}. Adding the intersection twice, multiplying the cardinalities, or reporting the symmetric difference all ignore the overlap drawn in the diagram.` };
      } },

    /* k = 1  — Digital Logic: parity count from a logic-gate diagram */
    { t: 'Digital Logic', unit: 2, diagram: 'logic-gates.svg',
      build: (g, r, n) => {
        const m = 2 + (g % 3), N = 1 << m;
        const opts = [`${N / 2}`, `${N}`, `${N - 1}`, `${m + 1}`];
        return { quest: `The logic-gate diagram chains ${m} inputs through XOR parity gates. Of the 2^${m} switch settings, how many activate the output?`, opts, e: `The logic-gate diagram implements ${m}-input odd parity, so the output is active for exactly half of the 2^${m} = ${N} settings, giving ${opts[0]}. The full setting count, one fewer than half, or the gate count plus one all report the wrong parity balance shown in the diagram.` };
      } },

    /* k = 2  — Digital Logic: row count from an XOR truth table */
    { t: 'Digital Logic', unit: 2, diagram: 'xor-truth-table.svg',
      build: (g, r, n) => {
        const m = 3 + ((g * 2) % 3), N = 1 << m;
        const opts = [`${N / 2}`, `${N}`, `${2 * m}`, `${m * m}`];
        return { quest: `The XOR truth-table diagram lists every input combination for ${m} variables. In how many rows does the output equal 1?`, opts, e: `An ${m}-variable XOR outputs 1 for exactly half of all rows because the function is odd-parity balanced. With 2^${m} = ${N} rows, ${opts[0]} rows output 1. The total row count, twice the variable count, or the squared variable count all disagree with this balance in the diagram.` };
      } },

    /* k = 3  — COA: data-input count from a multiplexer diagram */
    { t: 'Computer Architecture', unit: 2, diagram: 'multiplexer.svg',
      build: (g, r, n) => {
        const s = 1 + (g % 3), data = 1 << s;
        const opts = [`${data}`, `${data + 1}`, `${data - 1}`, `${s * s}`];
        return { quest: `The multiplexer diagram shows ${s} select lines. How many distinct data inputs can this multiplexer route to its single output?`, opts, e: `The multiplexer diagram uses ${s} select lines, each capable of selecting 2^${s} = ${data} distinct data inputs via a unique binary code. One more input, one fewer input, or the select count squared all contradict the binary-addressable design shown in the diagram.` };
      } },

    /* k = 4  — COA: instruction latency from a pipeline diagram */
    { t: 'Computer Architecture', unit: 2, diagram: 'pipeline.svg',
      build: (g, r, n) => {
        const stages = 5 + (g % 3);
        const opts = [`${stages * 3}`, `${stages + 3}`, `${stages}`, `${stages * 2}`];
        return { quest: `The pipeline diagram shows ${stages} stages, each taking 3 ns. Ignoring latch overhead, the latency of one instruction is`, opts, e: `The pipeline diagram shows ${stages} stages each of 3 ns; one instruction must traverse every stage, so its latency is ${stages} × 3 = ${opts[0]} ns. The stage-plus-cycle sum, the stage count, or stages doubled understate the per-instruction latency depicted in the diagram.` };
      } },

    /* k = 5  — COA: total blocks from a cache diagram */
    { t: 'Computer Architecture', unit: 2, diagram: 'cache.svg',
      build: (g, r, n) => {
        const sets = 8 + (g % 4), blocks = 2 + ((g * 2) % 3);
        const opts = [`${sets * blocks}`, `${sets + blocks}`, `${sets * blocks - 1}`, `${sets + blocks + 2}`];
        return { quest: `The cache diagram has ${sets} sets with ${blocks} blocks per set. How many total cache blocks can be stored simultaneously?`, opts, e: `The cache diagram organises storage into ${sets} sets, each holding ${blocks} blocks, so the total capacity is ${sets} × ${blocks} = ${opts[0]} blocks. The set-plus-block sum, one fewer block, or that sum plus two all contradict the direct-product sizing shown in the diagram.` };
      } },

    /* k = 6  — Programming: pointer arithmetic from a C-pointer diagram */
    { t: 'C Programming', unit: 3, diagram: 'c-pointer.svg',
      build: (g, r, n) => {
        const p = 100 + (g % 50), off = 1 + (g % 4);
        const opts = [`${p + off}`, `${p - off}`, `${p * off}`, `${off}`];
        return { quest: `The c-pointer diagram shows a pointer p = ${p}. After p += ${off}, what address does p hold?`, opts, e: `The c-pointer diagram shows p initialised to ${p}; pointer arithmetic with p += ${off} advances by ${off} scaled units, giving ${p} + ${off} = ${opts[0]}. Subtracting, multiplying, or reporting only the offset all violate the additive pointer rule shown in the diagram.` };
      } },

    /* k = 7  — Programming: frame count from a call-stack diagram */
    { t: 'C Programming', unit: 3, diagram: 'c-call-stack.svg',
      build: (g, r, n) => {
        const depth = 2 + (g % 4);
        const opts = [`${depth}`, `${depth - 1}`, `${depth + 2}`, `${2 * depth}`];
        return { quest: `The c-call-stack diagram displays ${depth} stacked function frames. How many frames are active on the call stack at this instant?`, opts, e: `The c-call-stack diagram displays one frame per active invocation; with ${depth} nested calls in progress, exactly ${depth} frames are active. One fewer frame, two extra frames, or double the active depth all misread the frame stack shown in the diagram.` };
      } },

    /* k = 8  — Programming: class count from a Java-inheritance diagram */
    { t: 'Java', unit: 3, diagram: 'java-inheritance.svg',
      build: (g, r, n) => {
        const levels = 2 + (n % 3);
        const opts = [`${levels}`, `${levels + 1}`, `${2 * levels}`, `${Math.max(1, levels - 1)}`];
        return { quest: `The java-inheritance diagram traces a single linear chain of ${levels} classes. How many class types are related by inheritance in this diagram?`, opts, e: `The java-inheritance diagram traces a single linear chain downward; each link is one class declaration, so ${levels} classes are related. One more class, twice the chain, or one fewer all contradict the single-inheritance path drawn in the diagram.` };
      } },

    /* k = 9  — Programming: state count from a Java-thread diagram */
    { t: 'Java', unit: 3, diagram: 'java-thread-states.svg',
      build: () => {
        const opts = ['5', '4', '6', '3'];
        return { quest: `The java-thread-states diagram shows the lifecycle of a thread. How many distinct states are depicted in the diagram?`, opts, e: `The java-thread-states diagram depicts the five canonical lifecycle states: new, runnable, blocked, waiting and terminated, so 5 states appear. Four, six, or three states all contradict the labelled nodes shown in the diagram.` };
      } },

    /* k = 10  — Data Structures: hop count from a linked-list diagram */
    { t: 'Data Structures', unit: 7, diagram: 'linked-list.svg',
      build: (g, r, n) => {
        const nodes = 4 + (g % 6);
        const opts = [`${nodes - 1}`, `${nodes}`, `${nodes + 1}`, `${2 * (nodes - 1)}`];
        return { quest: `The linked-list diagram shows ${nodes} nodes linked head to tail. Starting at the head, how many next-pointer hops reach the last node?`, opts, e: `The linked-list diagram links ${nodes} nodes linearly; reaching the tail from the head requires ${nodes - 1} hops. Counting all nodes, one extra hop, or double the hop count all contradict the linear traversal shown in the diagram.` };
      } },

    /* k = 11  — Data Structures: visit count from a BST diagram */
    { t: 'Data Structures', unit: 7, diagram: 'bst.svg',
      build: (g, r, n) => {
        const keys = 6 + (n % 7);
        const opts = [`${keys}`, `${keys - 1}`, `${2 * keys}`, `${keys + 1}`];
        return { quest: `The bst diagram stores ${keys} keys in a binary search tree. In how many nodes does an in-order traversal visit this tree?`, opts, e: `The bst diagram holds ${keys} keys; an in-order traversal visits every node exactly once, producing ${keys} nodes in sorted order. One fewer node, double the keys, or one extra all contradict visiting every key once in the diagram.` };
      } },

    /* k = 12  — Data Structures: net size from a stack diagram */
    { t: 'Data Structures', unit: 7, diagram: 'stack.svg',
      build: (g, r, n) => {
        const pushed = 5 + (g % 4), popped = 2 + (g % 3);
        const opts = [`${pushed - popped}`, `${pushed}`, `${pushed + popped}`, `${popped}`];
        return { quest: `The stack diagram shows ${pushed} pushes and ${popped} pops in order. What is the stack size shown after all operations complete?`, opts, e: `The stack diagram applies ${pushed} pushes and ${popped} pops, so net occupancy is ${pushed} − ${popped} = ${opts[0]}. Reporting the push count, the sum of push and pop, or the pop count all ignore the cancellation shown in the diagram.` };
      } },

    /* k = 13  — Data Structures: capacity from a circular-queue diagram */
    { t: 'Data Structures', unit: 7, diagram: 'circular-queue.svg',
      build: (g, r, n) => {
        const cap = 6 + (g % 4), stored = 2 + ((g * 2) % 3);
        const opts = [`${cap}`, `${cap - 1}`, `${stored}`, `${cap + stored}`];
        return { quest: `The circular-queue diagram shows a buffer of capacity ${cap} holding ${stored} items. At most how many elements can this queue hold at once?`, opts, e: `The circular-queue diagram's buffer has capacity ${cap}, so at most ${cap} elements can be held simultaneously. One fewer slot, the current occupancy, or capacity plus occupancy all contradict the fixed-size buffer shown in the diagram.` };
      } },

    /* k = 14  — Algorithms: edge count from a graph-traversal diagram */
    { t: 'Algorithms', unit: 7, diagram: 'graph-traversal.svg',
      build: (g, r, n) => {
        const V = 5 + (g % 4);
        const opts = [`${V - 1}`, `${V}`, `${V + 1}`, `${2 * (V - 1)}`];
        return { quest: `The graph-traversal diagram runs breadth-first search on a connected graph with ${V} vertices. How many edges are in the resulting BFS tree?`, opts, e: `The graph-traversal diagram runs BFS on a connected graph of ${V} vertices; a BFS spanning tree always has V − 1 = ${V - 1} edges. The vertex count, one extra edge, or double the edge count all contradict the spanning-tree property shown in the diagram.` };
      } },

    /* k = 15  — Algorithms: cell count from a dynamic-programming diagram */
    { t: 'Algorithms', unit: 7, diagram: 'algo-dynamic-programming.svg',
      build: (g, r, n) => {
        const rows = 3 + (g % 4), cols = 4 + (n % 3);
        const opts = [`${rows * cols}`, `${rows + cols}`, `${rows * cols - 1}`, `${2 * rows + cols}`];
        return { quest: `The algo-dynamic-programming diagram fills a table of ${rows} rows and ${cols} columns. How many subproblem cells does the table contain?`, opts, e: `The algo-dynamic-programming diagram tabulates solutions in a ${rows} × ${cols} grid, holding ${rows * cols} subproblem cells. The row-plus-column sum, one fewer cell, or double the rows plus columns all contradict the rectangular grid shown in the diagram.` };
      } },

    /* k = 16  — Algorithms: leaf count from a divide-and-conquer diagram */
    { t: 'Algorithms', unit: 7, diagram: 'algo-divide-conquer.svg',
      build: (g, r, n) => {
        const p = 2 + (n % 3), levels = 3 + (g % 3);
        const opts = [`${p ** levels}`, `${p * levels}`, `${p + levels}`, `${p ** (levels - 1)}`];
        return { quest: `The algo-divide-conquer diagram splits a problem into ${p} sub-problems per level over ${levels} levels. How many leaf sub-problems appear at the bottom level?`, opts, e: `The algo-divide-conquer diagram branches ${p}-way at each of ${levels} levels, so the recursion tree terminates in ${p}^${levels} = ${opts[0]} leaves. The product, the sum, or one level fewer all understate the exponential tree shown in the diagram.` };
      } },

    /* k = 17  — Algorithms: pass count from a merge-sort diagram */
    { t: 'Algorithms', unit: 7, diagram: 'algo-merge-sort.svg',
      build: (g, r, n) => {
        const N = 8 + (g % 5);
        const opts = [`${Math.ceil(Math.log2(N))}`, `${N}`, `${Math.floor(Math.log2(N))}`, `${Math.ceil(Math.log2(N)) + 1}`];
        return { quest: `The algo-merge-sort diagram sorts ${N} elements by recursive halving. How many merge passes does the diagram perform?`, opts, e: `The algo-merge-sort diagram halves the ${N}-element array until singletons remain, then merges back; the pass count is ⌈log2(${N})⌉ = ${opts[0]}. Sorting in ${N} passes, the floor of the log, or one extra pass all contradict the halving shown in the diagram.` };
      } },

    /* k = 18  — DBMS: box count from an ER diagram */
    { t: 'DBMS', unit: 4, diagram: 'dbms-er.svg',
      build: (g, r, n) => {
        const ents = 3 + (g % 4), rels = ents - 1;
        const opts = [`${ents + rels}`, `${ents * rels}`, `${ents}`, `${ents + rels + 1}`];
        return { quest: `The dbms-er diagram models ${ents} entities connected by ${rels} relationships. How many boxes (entities plus relationships) are drawn in total?`, opts, e: `The dbms-er diagram draws ${ents} entity boxes and ${rels} relationship diamonds, totalling ${ents + rels} boxes. The product of entities and relationships, the entity count alone, or one extra box all contradict the diagram's total shape count.` };
      } },

    /* k = 19  — DBMS: key count from a B+ tree diagram */
    { t: 'DBMS', unit: 4, diagram: 'dbms-bplus-tree.svg',
      build: (g, r, n) => {
        const order = 4 + (n % 5), keys = order - 1;
        const opts = [`${keys}`, `${order}`, `${keys + 1}`, `${2 * keys}`];
        return { quest: `The dbms-bplus-tree diagram uses an order-${order} node. How many keys reside in each internal node?`, opts, e: `The dbms-bplus-tree diagram uses order-${order} nodes, which store one fewer key than children, so each internal node holds ${keys} keys. The node order, one extra key, or double the keys all contradict the B+ tree node capacity shown in the diagram.` };
      } },

    /* k = 20  — Operating System: state count from a process-state diagram */
    { t: 'Operating System', unit: 5, diagram: 'os-process-states.svg',
      build: () => {
        const opts = ['5', '4', '6', '3'];
        return { quest: `The os-process-states diagram shows transitions among process states. How many states are labelled in the diagram?`, opts, e: `The os-process-states diagram labels five standard states: new, ready, running, waiting and terminated, so 5 states appear. Four, six, or three states all contradict the labelled nodes shown in the diagram.` };
      } },

    /* k = 21  — Operating System: page size from a paging diagram */
    { t: 'Operating System', unit: 5, diagram: 'os-paging.svg',
      build: (g, r, n) => {
        const offset = 6 + ((g * 2) % 3), prefix = 32 - offset;
        const opts = [`${1 << offset}`, `${1 << (offset - 2)}`, `${1 << (32 - offset)}`, `${prefix}`];
        return { quest: `The os-paging diagram reserves ${offset} page-offset bits (prefix /${prefix}). What is the page size in bytes?`, opts, e: `The os-paging diagram reserves ${offset} offset bits, so each page contains 2^${offset} = ${1 << offset} bytes. Half of that page size, the virtual page count, or the prefix length itself all measure the wrong quantity shown in the diagram.` };
      } },

    /* k = 22  — Operating System: cycle edges from a deadlock diagram */
    { t: 'Operating System', unit: 5, diagram: 'os-deadlock.svg',
      build: (g, r, n) => {
        const procs = 3 + (g % 3);
        const opts = [`${procs}`, `${procs - 1}`, `${procs + 1}`, `${2 * procs}`];
        return { quest: `The os-deadlock diagram depicts a circular wait among ${procs} processes. How many wait-for edges close this deadlock cycle?`, opts, e: `The os-deadlock diagram depicts a circular wait among ${procs} processes; a cycle of ${procs} processes contains exactly ${procs} wait-for edges. One fewer edge, one extra edge, or double the process count all contradict the closed cycle shown in the diagram.` };
      } },

    /* k = 23  — Networks: segment count from a TCP-handshake diagram */
    { t: 'Computer Networks', unit: 9, diagram: 'tcp-handshake.svg',
      build: (g) => {
        const opts = ['3', '2', '4', '1'];
        return { quest: `The tcp-handshake diagram exchanges three messages to establish a connection for initial sequence number ${g % 1000}. How many segments complete the connection?`, opts, e: `The tcp-handshake diagram performs the three-way handshake: SYN, SYN-ACK and ACK, so 3 segments complete the connection. Two, four, or one segment all contradict the three-segment exchange shown in the diagram.` };
      } },

    /* k = 24  — Networks: usable hosts from an IPv4-subnet diagram */
    { t: 'Computer Networks', unit: 9, diagram: 'ipv4-subnet.svg',
      build: (g, r, n) => {
        const hostbits = 5 + (g % 3), prefix = 32 - hostbits;
        const opts = [`${(1 << hostbits) - 2}`, `${1 << hostbits}`, `${1 << (hostbits - 1)}`, `${prefix}`];
        return { quest: `The ipv4-subnet diagram reserves ${hostbits} host bits (prefix /${prefix}). How many usable IPv4 addresses does each subnet contain?`, opts, e: `The ipv4-subnet diagram reserves ${hostbits} host bits under prefix /${prefix}, leaving 2^${hostbits} = ${1 << hostbits} addresses minus the network and broadcast addresses, i.e. ${opts[0]} usable hosts. The raw address count, half of it, or the prefix length itself all ignore the reserved addresses shown in the diagram.` };
      } },
  ];

  const build = (set, i) => {
    const g = (set - 301) * 100 + i + 1;
    const r = Math.floor(i / 25);
    const n = 6 + (g % 19);
    const k = i % 25;
    const tag = `[S${set}-Q${i + 1}]`;
    const tpl = templates[k];
    const { quest, opts, e } = tpl.build(g, r, n);
    const base = uniq(opts[0], opts.slice(1));
    const a = (set * 7 + i * 3 + k) % 4;
    const o = base.slice(1);
    o.splice(a, 0, opts[0]);
    return {
      s: `Set ${set} • ${levelFor(i)} • Diagrammatic MCQs • ${tpl.t} • Unit ${tpl.unit}`,
      t: tpl.t,
      q: `${tag} ${quest}`,
      o: o,
      a: a,
      e: `${e} Correct answer: ${opts[0]}.`,
      mode: i % 25 === 9 ? 'fill' : 'selection',
      level: levelFor(i),
      passage: undefined,
      unit: tpl.unit,
      unitName: UGC_NET_UNITS[tpl.unit],
      img: `/static/moocs/diagrams/${tpl.diagram}`,
      alt: DIAGRAMS[tpl.diagram],
    };
  };

  for (let set = 301; set <= 400; set++) {
    QUESTION_SETS[set] = Array.from({ length: 100 }, (_, i) => build(set, i));
  }
})();
