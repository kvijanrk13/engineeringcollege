/* Sets 12-100: List-I / List-II matching-table banks for every subject.
   Each entry pairs four List-I concepts with four List-II properties.
   `pair` maps List-I index -> List-II index and defines the keyed answer. */
window.VARIED_MATCHING_BANK = (function () {
  'use strict';

  const bank = {

    /* ---------------- 1. Engineering Mathematics ---------------- */
    1: [
      {
        left: ['Descartes rule of signs', 'Newton-Raphson method', 'Regula falsi method', 'Bisection method'],
        right: ['Counts the positive real roots of a polynomial', 'Requires the derivative of the function at each step', 'Uses linear interpolation between a bracketing pair', 'Requires the function to change sign across the initial interval'],
        pair: [0, 1, 2, 3],
        why: 'Each root-finding method is identified by what information it consumes. Descartes uses only the sign changes of coefficients, Newton-Raphson uses the first derivative, regula falsi interpolates linearly between two points, and bisection only needs a sign change.'
      },
      {
        left: ['Eigenvalue of a matrix', 'Trace of a matrix', 'Rank of a matrix', 'Determinant of a matrix'],
        right: ['Sum of the eigenvalues', 'Number of linearly independent rows or columns', 'Product of the eigenvalues', 'Signed factor by which a linear map scales area'],
        pair: [0, 1, 3, 2],
        why: 'The trace is the sum of the eigenvalues and the determinant is their product, so the remaining identity fixes the rank as the dimension of the column space and the determinant as the area scaling factor.'
      },
      {
        left: ['Necessary condition for an extremum', 'Sufficient condition for a minimum', 'Mean value theorem', 'Rolle theorem'],
        right: ['Derivative vanishes at a stationary point', 'Second derivative is positive at the point', 'A continuous closed interval with equal endpoint values', 'A differentiable function attains a point of zero derivative'],
        pair: [0, 1, 3, 2],
        why: 'Fermat gives the necessary first-order condition, the second derivative test gives the sufficient condition for a local minimum, the mean value theorem supplies a point with a specified slope, and Rolle theorem is its zero-slope special case.'
      },
      {
        left: ['Vector space over a field', 'Subspace of a vector space', 'Linear transformation', 'Eigenvector'],
        right: ['Closed under addition and scalar multiplication containing the zero vector', 'A non-empty subset closed under the vector space operations', 'A map preserving vector addition and scalar multiplication', 'A non-zero vector mapped to a scalar multiple of itself'],
        pair: [0, 2, 1, 3],
        why: 'The list is ordered by strength: a vector space satisfies the operations, a linear transformation preserves them, a subspace is a subset that inherits them, and an eigenvector is a single vector fixed up to scaling by a transformation.'
      },
    ],

    /* ---------------- 2. Digital Logic & COA ---------------- */
    2: [
      {
        left: ['NAND gate', 'NOR gate', 'XOR gate', 'XNOR gate'],
        right: ['Universal gate, logical complement of AND', 'Universal gate, logical complement of OR', 'Output is 1 when inputs differ', 'Output is 1 when inputs are equal'],
        pair: [0, 1, 2, 3],
        why: 'NAND and NOR are both universal because any Boolean function can be built from either, while XOR and XNOR are defined purely by the parity of their two inputs and are not universal.'
      },
      {
        left: ['Two\'s complement', 'Ones complement', 'Sign-magnitude', 'Excess-64'],
        right: ['Arithmetic shift right preserves the sign bit', 'Negative zero has two representations', 'Leading bit distinguishes sign from magnitude', 'Bias added to the exponent to avoid a signed exponent'],
        pair: [0, 1, 2, 3],
        why: 'The identity of each representation is fixed by its defining defect: two\'s complement has a single zero and a sign-extendable leading bit, ones complement admits positive and negative zero, sign-magnitude splits sign from magnitude, and excess-64 biases the exponent field.'
      },
      {
        left: ['Direct mapped cache', 'Set associative cache', 'Fully associative cache', 'Write-through policy'],
        right: ['One memory block maps to exactly one line', 'A block maps to any line within a fixed set', 'A block may map to any line in the cache', 'Every write updates both cache and memory'],
        pair: [0, 1, 2, 3],
        why: 'These four entries form a progression of increasing placement freedom followed by a write policy. Direct mapping is the most restrictive, set associative relaxes it within a set, fully associative removes the set restriction, and write-through describes coherence rather than placement.'
      },
      {
        left: ['Cache hit time', 'Memory access time', 'Address translation with TLB', 'Paging lookup cost'],
        right: ['Typically one or two processor cycles', 'Typically hundreds of cycles', 'One memory plus one cache access on a miss', 'One memory plus one cache access on a page fault'],
        pair: [0, 2, 1, 3],
        why: 'The orderings follow the cost hierarchy of the memory system. A hit is a single cache comparison, a TLB miss costs one memory access, a normal memory access costs hundreds of cycles, and a page fault additionally requires the page to be brought in from secondary storage.'
      },
    ],

    /* ---------------- 3. Programming ---------------- */
    3: [
      {
        left: ['Encapsulation', 'Abstraction', 'Inheritance', 'Polymorphism'],
        right: ['Hiding internal state behind a defined interface', 'Describing what an entity does rather than how', 'Deriving a new type from an existing one', 'One interface with several possible implementations'],
        pair: [0, 1, 2, 3],
        why: 'These four object-oriented principles are distinguished by their concern: encapsulation controls access to state, abstraction controls the description offered to a client, inheritance reuses a type hierarchy, and polymorphism lets a single message select an implementation at run time.'
      },
      {
        left: ['Recursion', 'Iteration', 'Tail recursion', 'Backtracking'],
        right: ['A function calling itself on a smaller subproblem', 'Repeating a statement over a sequence', 'A recursive call in return position, compiled as a loop', 'Exploring alternatives and undoing a failed choice'],
        pair: [0, 1, 3, 2],
        why: 'Recursion and iteration are the two general control strategies. Tail recursion is a specialised recursion that is optimisable to iteration, and backtracking is recursion driven by an explicit undo of a choice that turned out to be wrong.'
      },
      {
        left: ['Overloading', 'Overriding', 'Operator overloading', 'Static binding'],
        right: ['Same name with different parameter types', 'Same signature redefined in a subclass', 'A built-in operator used with user-defined types', 'The target of a call is fixed at compile time'],
        pair: [0, 1, 2, 3],
        why: 'Overloading resolves a name across parameter types, overriding replaces an inherited definition, operator overloading extends the expression syntax to user types, and static binding fixes the call target when the program is compiled.'
      },
      {
        left: ['Stack frame', 'Heap allocation', 'Automatic storage', 'Register allocation'],
        right: ['Local variables and saved return address', 'Memory obtained from the allocator at run time', 'Storage released when the block scope ends', 'Values held in CPU registers for speed'],
        pair: [1, 0, 2, 3],
        why: 'The mapping is fixed by lifetime and size. A stack frame holds the fixed-size locals and return address of an activation, the heap serves dynamically sized run-time objects, automatic storage is reclaimed on scope exit, and register allocation is a compile-time promotion of frequently used values.'
      },
    ],

    /* ---------------- 4. DBMS ---------------- */
    4: [
      {
        left: ['First normal form', 'Second normal form', 'Third normal form', 'BCNF'],
        right: ['Every attribute value is atomic', 'No partial dependency on a composite key', 'No transitive dependency on the key', 'Every determinant is a candidate key'],
        pair: [0, 1, 2, 3],
        why: 'The normal forms are cumulative, each removing a specific kind of redundancy. 1NF removes repeating groups, 2NF removes partial dependencies, 3NF removes transitive dependencies, and BCNF strengthens 3NF by requiring every determinant to be a candidate key.'
      },
      {
        left: ['View', 'Index', 'Foreign key', 'Trigger'],
        right: ['A virtual table defined by a query', 'An auxiliary structure that speeds retrieval', 'A reference enforcing existence in another relation', 'A statement executed automatically on an event'],
        pair: [0, 1, 2, 3],
        why: 'Each database object is identified by its function. A view is a derived virtual table, an index is a physical access path, a foreign key is a declarative referential constraint, and a trigger is an event-driven procedural action.'
      },
      {
        left: ['Serializability', 'Atomicity', 'Isolation', 'Durability'],
        right: ['Concurrent transactions appear to run one at a time', 'A transaction either fully applies or not at all', 'A transaction sees a consistent snapshot', 'Committed changes survive a crash'],
        pair: [0, 2, 1, 3],
        why: 'The four ACID properties are distinguished by the failure or interference each prevents. Isolation maps to serializability, atomicity maps to all-or-nothing, consistency maps to snapshot integrity, and durability maps to persistence across a crash.'
      },
      {
        left: ['B+ tree index', 'Hash index', 'Clustered index', 'Bitmap index'],
        right: ['Balanced tree giving ordered range access', 'Direct lookup by a hash function', 'Physical rows stored in index order', 'Bit vector per distinct value, best for low cardinality'],
        pair: [0, 2, 1, 3],
        why: 'Each index structure suits a different access pattern. A B+ tree keeps keys ordered for range scans, a hash index gives equality lookup, a clustered index fixes the physical order of the rows themselves, and a bitmap index is efficient for columns with few distinct values.'
      },
    ],

    /* ---------------- 5. Operating Systems ---------------- */
    5: [
      {
        left: ['Mutual exclusion', 'Hold and wait', 'No preemption', 'Circular wait'],
        right: ['Only one process may hold a resource at a time', 'A process holds resources while waiting for more', 'Resources are released only voluntarily', 'A cycle of processes each waiting for the next resource'],
        pair: [0, 1, 2, 3],
        why: 'These are the four Coffman conditions for deadlock, each a distinct requirement. They are listed in the standard order and the three deadlocks of the preceding entry do not satisfy them.'
      },
      {
        left: ['FCFS scheduling', 'Round robin scheduling', 'SJF scheduling', 'Priority scheduling'],
        right: ['Non-preemptive queue in arrival order', 'Preemptive with a fixed time quantum', 'Chooses the shortest remaining burst time', 'Chooses the highest priority process first'],
        pair: [0, 1, 2, 3],
        why: 'The four schedulers differ in the policy used to pick the next process. FCFS follows arrival order, round robin adds preemption on a time slice, shortest job first optimises average waiting time, and priority scheduling orders by an assigned rank.'
      },
      {
        left: ['Segmentation fault', 'Page fault', 'Memory overcommit', 'Thrashing'],
        right: ['A reference outside the mapped region', 'The referenced page is not resident', 'More memory is promised than physically present', 'Processes spend more time paging than executing'],
        pair: [0, 1, 2, 3],
        why: 'Each entry names a distinct memory condition. A segmentation fault violates the address space, a page fault is a normal demand load, overcommit is an admission decision that outruns physical memory, and thrashing is the resulting sustained paging collapse.'
      },
      {
        left: ['Semaphore', 'Monitor', 'Condition variable', 'Spinlock'],
        right: ['Counter manipulated by wait and signal', 'Language construct bundling a lock and shared data', 'A queue of threads waiting on a predicate', 'A lock that busy-waits rather than blocking'],
        pair: [0, 1, 2, 3],
        why: 'These are the four synchronisation primitives in increasing order of abstraction. A semaphore is a raw counter, a monitor adds mutual exclusion and condition waiting to the language, a condition variable is the waiting mechanism inside a monitor, and a spinlock is the lock itself.'
      },
    ],

    /* ---------------- 6. Software Engineering ---------------- */
    6: [
      {
        left: ['Unit testing', 'Integration testing', 'System testing', 'Acceptance testing'],
        right: ['Individual modules in isolation', 'Interactions between combined modules', 'The complete system against specified requirements', 'The system in the customer operational environment'],
        pair: [0, 1, 2, 3],
        why: 'The four test levels widen the scope of the system under test at each step, from a single module to the deployed system with the customer.'
      },
      {
        left: ['Coupling', 'Cohesion', 'Modularity', 'Refactoring'],
        right: ['Degree of interdependence between modules', 'Degree to which parts of a module belong together', 'Decomposition into separately addressable units', 'Restructuring code without changing behaviour'],
        pair: [0, 1, 2, 3],
        why: 'Design quality is measured by the relationship between units. Coupling and cohesion describe the strength of inter-module and intra-module relationships, modularity is the decomposition itself, and refactoring is the controlled improvement of that structure.'
      },
      {
        left: ['Waterfall model', 'Spiral model', 'Incremental delivery', 'Prototype model'],
        right: ['Sequential phases with a fixed plan', 'Iterative cycles of risk-driven development', 'Working subsets delivered in increasing scope', 'A throwaway mock-up built to clarify requirements'],
        pair: [0, 1, 2, 3],
        why: 'Each lifecycle model responds differently to uncertainty. The waterfall assumes stable requirements, the spiral manages risk across repeated cycles, incremental delivery ships partial value early, and prototyping resolves unclear requirements before the real build.'
      },
      {
        left: ['Code review', 'Static analysis', 'Dynamic analysis', 'Regression testing'],
        right: ['Human inspection of source and design', 'Tool-based analysis of code without execution', 'Tool-based analysis during actual execution', 'Re-running the suite after a change to confirm nothing broke'],
        pair: [0, 1, 2, 3],
        why: 'Verification methods are separated by whether a human inspects the artefact, whether analysis is performed without execution, whether it is performed during execution, and whether the whole prior suite is re-checked after a change.'
      },
    ],

    /* ---------------- 7. Data Structures & Algorithms ---------------- */
    7: [
      {
        left: ['Binary search', 'Merge sort', 'Quick sort', 'Heap sort'],
        right: ['Needs a sorted array', 'Needs extra space of the array size', 'Worst case quadratic, average n log n', 'Builds a priority queue and repeatedly extracts the maximum'],
        pair: [0, 1, 2, 3],
        why: 'Each algorithm is identified by its precondition and cost profile. Binary search requires sorted order, merge sort allocates an auxiliary array, quick sort degrades on already ordered input, and heap sort works through an in-place priority queue.'
      },
      {
        left: ['Inorder traversal', 'Preorder traversal', 'Postorder traversal', 'Level order traversal'],
        right: ['Produces sorted keys on a binary search tree', 'Visits the root before its subtrees', 'Visits the root after its subtrees', 'Visits nodes level by level using a queue'],
        pair: [0, 1, 2, 3],
        why: 'The three depth-first orders differ only in when the root is visited, while the fourth is breadth-first and is implemented with a queue rather than recursion.'
      },
      {
        left: ['Dijkstra algorithm', 'Bellman-Ford algorithm', 'Floyd-Warshall algorithm', 'Prim algorithm'],
        right: ['Single-source shortest paths with non-negative weights', 'Single-source shortest paths allowing negative weights', 'All-pairs shortest paths', 'Minimum spanning tree of a connected graph'],
        pair: [0, 1, 2, 3],
        why: 'The four are distinguished by the problem they solve. Dijkstra needs non-negative weights, Bellman-Ford relaxes edges repeatedly to handle negative weights, Floyd-Warshall solves all pairs by dynamic programming, and Prim builds a minimum spanning tree.'
      },
      {
        left: ['Stack', 'Queue', 'Priority queue', 'Hash table'],
        right: ['Last in, first out access', 'First in, first out access', 'Access by key order rather than arrival', 'Constant-time average lookup by a computed address'],
        pair: [0, 1, 2, 3],
        why: 'The list orders the abstract types by the discipline they enforce on access. The priority queue and the hash table depart from the arrival discipline, the former ordering by key and the latter replacing ordering entirely with direct addressing.'
      },
    ],

    /* ---------------- 8. TOC & Compiler Design ---------------- */
    8: [
      {
        left: ['Finite automaton', 'Pushdown automaton', 'Linear bounded automaton', 'Turing machine'],
        right: ['Recognises regular languages', 'Recognises context-free languages', 'Recognises context-sensitive languages', 'Recognises recursively enumerable languages'],
        pair: [0, 1, 2, 3],
        why: 'The four machines are listed in the order of the Chomsky hierarchy they realise, each adding a strictly more powerful memory structure: none, a stack, a bounded tape, and an unbounded tape.'
      },
      {
        left: ['Lexical analysis', 'Syntax analysis', 'Semantic analysis', 'Code generation'],
        right: ['Groups characters into tokens', 'Builds a parse tree from the grammar', 'Checks types and declaration consistency', 'Emits the target machine instruction sequence'],
        pair: [0, 1, 2, 3],
        why: 'The compiler phases run front to back on the program representation: characters become tokens, tokens become a tree, the tree is checked for meaning, and the validated tree becomes instructions.'
      },
      {
        left: ['Context-free grammar', 'Regular expression', 'Regular grammar', 'Attribute grammar'],
        right: ['Defines the context-free languages', 'Defines the regular languages', 'Defines a regular language in grammar form', 'Attaches semantic rules to grammar symbols'],
        pair: [1, 0, 3, 2],
        why: 'The four formalisms are distinguished by expressive power and purpose. Regular expressions and regular grammars both denote the regular languages, context-free grammars denote the context-free languages, and an attribute grammar extends a grammar with semantic information.'
      },
      {
        left: ['Constant folding', 'Dead code elimination', 'Loop unrolling', 'Common subexpression elimination'],
        right: ['Evaluates constant expressions at compile time', 'Removes computation whose result is unused', 'Replicates a short loop body a fixed number of times', 'Reuses the value of an already computed expression'],
        pair: [0, 1, 2, 3],
        why: 'The four optimisations are named by the transformation they perform: precomputing constants, deleting unreachable computation, expanding iterations, and sharing repeated results.'
      },
    ],

    /* ---------------- 9. Computer Networks ---------------- */
    9: [
      {
        left: ['ARP', 'ICMP', 'DHCP', 'DNS'],
        right: ['Maps an IP address to a MAC address', 'Carries control and error messages such as ping', 'Assigns an address and configuration automatically', 'Translates a name into an address record'],
        pair: [0, 1, 2, 3],
        why: 'The four protocols are identified by the addressing or control task they perform: link-layer address resolution, network-layer diagnostics, host configuration, and name resolution.'
      },
      {
        left: ['Stop-and-wait ARQ', 'Go-back-N ARQ', 'Selective repeat ARQ', 'Sliding window'],
        right: ['One outstanding frame at a time', 'Resends from the damaged frame onwards', 'Resends only the frames actually lost', 'The unacknowledged and unacknowledged range that may be in flight'],
        pair: [0, 1, 2, 3],
        why: 'The three flow-control schemes differ in how much they retransmit on loss, while the sliding window is the underlying mechanism that bounds how many frames may be unacknowledged.'
      },
      {
        left: ['Base 2', 'Base 8', 'Base 16', 'Decimal 24-bit addressing'],
        right: ['A bit', 'Three bits', 'Four bits', 'A dotted-quad address written as four octal-free decimal fields'],
        pair: [0, 1, 2, 3],
        why: 'The first three entries give the bit group each base encodes per digit, and the fourth names the textual IPv4 convention that renders those bits as decimal octets.'
      },
      {
        left: ['Symmetric encryption', 'Asymmetric encryption', 'Hash function', 'Digital signature'],
        right: ['One shared key both encrypts and decrypts', 'A public and a private key pair', 'A one-way fixed-length digest', 'A private-key operation verifiable with the public key'],
        pair: [0, 1, 2, 3],
        why: 'The four security mechanisms are separated by key handling and direction of use. Symmetric cryptography shares one key, asymmetric cryptography uses a pair, a hash is one-way with no key, and a signature is a private-key operation checked with the public key.'
      },
    ],

    /* ---------------- 10. Artificial Intelligence ---------------- */
    10: [
      {
        left: ['Breadth-first search', 'Depth-first search', 'A* search', 'Best-first search'],
        right: ['Expands all nodes of a depth before the next', 'Expands a branch fully before backtracking', 'Expands on lowest g plus h with an admissible heuristic', 'Expands the node with the best heuristic value alone'],
        pair: [0, 1, 2, 3],
        why: 'The four uninformed and informed searches are separated by their expansion rule. Breadth-first and depth-first ignore the heuristic, A* combines the cost so far with an admissible estimate, and best-first uses the estimate alone.'
      },
      {
        left: ['Supervised learning', 'Unsupervised learning', 'Reinforcement learning', 'Semi-supervised learning'],
        right: ['Learns from labelled examples', 'Finds structure in unlabelled data', 'Learns from a reward signal over actions', 'Learns from a small labelled and a large unlabelled set'],
        pair: [0, 1, 2, 3],
        why: 'The four paradigms are defined by the supervision signal available during training: full labels, no labels, an action reward, or a mixture of both.'
      },
      {
        left: ['True positive', 'False positive', 'False negative', 'True negative'],
        right: ['A present class correctly predicted present', 'An absent class incorrectly predicted present', 'A present class incorrectly predicted absent', 'An absent class correctly predicted absent'],
        pair: [0, 1, 2, 3],
        why: 'The four confusion-matrix cells are read off the combination of the actual class and the predicted class, and every metric such as precision, recall and accuracy is built from these four counts.'
      },
      {
        left: ['Perceptron', 'Decision tree', 'Support vector machine', 'k-nearest neighbours'],
        right: ['A single linear threshold unit', 'A hierarchical partition by attribute tests', 'A maximum-margin separating hyperplane', 'A majority vote of the closest labelled points'],
        pair: [0, 1, 2, 3],
        why: 'The four classifiers are identified by the decision surface they construct: a single linear threshold, axis-parallel splits, a maximum-margin hyperplane, and a local neighbourhood vote.'
      },
    ],

    /* ---------------- 11. Software Engineering / Management ---------------- */
    11: [
      {
        left: ['Functional requirement', 'Non-functional requirement', 'Stakeholder', 'Risk'],
        right: ['Specifies what the system must do', 'Specifies the quality attribute or constraint', 'Any party affected by or able to affect the system', 'An uncertain event whose occurrence would harm the objectives'],
        pair: [0, 1, 2, 3],
        why: 'The four requirements concepts are separated by what each one constrains: system behaviour, system quality, the parties consulted, and the uncertainty managed during the project.'
      },
      {
        left: ['Gantt chart', 'PERT chart', 'Milestone', 'Critical path'],
        right: ['A bar schedule over calendar time', 'A dependency network with three-point estimates', 'A zero-duration marker of a significant event', 'The longest dependency chain determining project duration'],
        pair: [0, 1, 2, 3],
        why: 'The four planning artefacts are distinguished by the model they use: calendar bars, a precedence network, an event marker, and the controlling chain of that network.'
      },
      {
        left: ['Effort estimation', 'Schedule estimation', 'Defect density', 'Code churn'],
        right: ['Man-hours required to complete the work', 'Calendar time required to complete the work', 'Defects per thousand lines of code', 'Lines added, removed and modified over a period'],
        pair: [0, 1, 2, 3],
        why: 'The four process metrics measure different things. Effort and schedule are forward-looking project quantities, while defect density and churn are measured properties of delivered code.'
      },
      {
        left: ['Availability', 'Reliability', 'Maintainability', 'Portability'],
        right: ['Probability the service is up when required', 'Probability the service performs correctly over time', 'Effort required to correct a defect', 'Effort required to move the system to another environment'],
        pair: [0, 1, 2, 3],
        why: 'These four non-functional attributes are distinguished by the quantity each measures: uptime, failure-free operation, repair effort, and migration effort.'
      },
    ],

    /* ---------------- 0. General Aptitude ---------------- */
    0: [
      {
        left: ['Data sufficiency statement', 'Assumption', 'Syllogism', 'Venn diagram'],
        right: ['Information split into two statements to be combined', 'Something taken as true without being proved', 'A conclusion drawn from two categorical premises', 'A diagram of overlapping closed curves for set relations'],
        pair: [0, 1, 2, 3],
        why: 'The four reasoning constructs are identified by their structure: a pair of information statements, an unstated premise, a two-premise categorical argument, and a set-theoretic picture.'
      },
      {
        left: ['Analogy', 'Classification', 'Series', 'Coding'],
        right: ['A relation is extended from one pair to another', 'Placing an item in a stated category', 'Finding the next term of a defined pattern', 'Assigning symbols to words by a stated rule'],
        pair: [0, 1, 2, 3],
        why: 'The four verbal reasoning forms are distinguished by the task they set: extending a relation, naming a category, continuing a pattern, and applying an encoding rule.'
      },
      {
        left: ['Profit percentage', 'Marked price', 'Cost price', 'Selling price'],
        right: ['Profit divided by the cost price', 'The listed price before discount', 'The price at which the item was acquired', 'The price finally received from the customer'],
        pair: [0, 1, 2, 3],
        why: 'The four commercial quantities are distinguished by their position in the pricing chain, from the percentage gain measured against cost, through the listed and acquisition prices, to the price finally charged.'
      },
      {
        left: ['Simple interest', 'Compound interest', 'Average speed', 'Relative speed'],
        right: ['Interest computed on the original principal only', 'Interest computed on the accumulated amount', 'Total distance divided by total time', 'Speed of one object expressed against another'],
        pair: [0, 1, 2, 3],
        why: 'The four quantitative concepts are separated by their defining relationship: the base used for interest, the compounding of interest, the averaging of distance over time, and the reference point for velocity.'
      },
    ],

  };

  return bank;
})();
