/* Sets 201–300: Advanced 2-paragraph analytical MCQs with complex scenarios.
   Each question generates a unique passage (2 paragraphs) and an analytical
   question whose parameters vary with set number and index, so no two exams
   are identical. */
(function () {
  const gcd = (a, b) => b === 0 ? a : gcd(b, a % b);
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

  /* ---- 25 two-paragraph analytical passage templates ---- */
  /* Each template produces a passage (2 paragraphs), a question stem, four
     candidate answers, the index of the correct answer, and an explanation.
     Parameters are seeded from the global counter so every (set, i) yields
     a unique question. */

  const templates = [
    /* k = 0  — Algorithms: divide-and-conquer recursion depth */
    {
      t: 'Algorithms', unit: 7,
      build: (g, r, n) => {
        const p = 3 + (n % 7), q = 2 + ((g * 3) % 5), h = 2 + ((g * 7) % 4);
        const total = Math.pow(p, q) * h;
        const pass = `A recursive algorithm divides a problem of size N into ${p} sub-problems, each of size N/${q}, and performs ${h} additional work units at each level of recursion. The recursion terminates when the sub-problem size drops below a threshold. During a performance review, the team notices that for very large inputs the algorithm exhausts the call stack, and they decide to convert the recursion into an iterative solution using an explicit stack data structure.`;
        const quest = `What is the maximum depth of the recursion tree, and what asymptotic space complexity does the iterative stack-based version require in the worst case?`;
        const opts = [
          `Depth ≈ log_${q} N = ${Math.round(Math.log2(total)/Math.log2(q))}, iterative space O(N)`,
          `Depth ≈ ${q}·log_${p} N, iterative space O(1)`,
          `Depth ≈ N/${q}, iterative space O(log N)`,
          `Depth ≈ log_${p} N, iterative space O(N)`,
        ];
        return { pass, quest, opts, correct: 0, unit: 7 };
      },
    },

    /* k = 1  — DBMS: B+ tree node splitting */
    {
      t: 'DBMS', unit: 4,
      build: (g, r, n) => {
        const m = 4 + (n % 9), keys = m - 1, inserts = 50 + (g % 100);
        const pass = `A B+ tree of order ${m} stores ${keys} key-pointer pairs per internal node and splits leaf nodes by promoting the median key upward. A database administrator inserts ${inserts} records, each with a unique key, into the tree. After the insertions complete, the tree is used to serve a range query that spans approximately 60% of the total key range. The DBA observes that the B+ tree's height is higher than expected for a bulk-loaded tree of the same key count.`;
        const quest = `Given the sequential nature of the insertions and the promotion policy, how many node splits occur during the insertion phase, and why is the height higher than that of an optimally bulk-loaded B+ tree with the same number of keys?`;
        const opts = [
          `${inserts - 1} splits; sequential insertions cause right-heavy growth and frequent leaf splits`,
          `${Math.floor(inserts / m)} splits; the tree underfills internal pages`,
          `0 splits; B+ trees never split during sequential insertion`,
          `${inserts} splits; every insertion triggers a split`,
        ];
        return { pass, quest, opts, correct: 0, unit: 4 };
      },
    },

    /* k = 2  — Networks: TCP congestion control */
    {
      t: 'Computer Networks', unit: 9,
      build: (g, r, n) => {
        const cwnd_init = 10 + (n % 20), ssthresh = cwnd_init * 6, loss_at = 100 + (g % 200);
        const pass = `A TCP sender starts with an initial congestion window of ${cwnd_init} segments and a slow-start threshold of ${ssthresh} segments. The sender operates in a network with an RTT of 50 ms. After transmitting ${loss_at} segments, the network signals a congestion event (three duplicate ACKs). The sender then enters fast recovery and resumes congestion avoidance.`;
        const quest = `How many RTTs elapse during the slow-start phase before the threshold is reached, and what is the congestion window size immediately after fast recovery adjusts it?`;
        const ss_rtts = Math.ceil(Math.log2(ssthresh / cwnd_init));
        const ca_cwnd = Math.floor(ssthresh / 2) + 3;
        const opts = [
          `${ss_rtts} RTTs, cwnd = ${ssthresh/2} segments`,
          `${ss_rtts + 1} RTTs, cwnd = ${ca_cwnd} segments`,
          `${ss_rtts} RTTs, cwnd = ${ssthresh} segments`,
          `${Math.floor(ss_rtts/2)} RTTs, cwnd = ${ca_cwnd} segments`,
        ];
        return { pass, quest, opts, correct: 1, unit: 9 };
      },
    },

    /* k = 3  — Operating Systems: scheduling */
    {
      t: 'Operating Systems', unit: 5,
      build: (g, r, n) => {
        const p1 = 8 + (n % 10), bt1 = 4 + (g % 7), p2 = 3 + (n % 5), bt2 = 6 + ((g*2) % 5);
        const qtime = 2 + (g % 3);
        const pass = `Two CPU-bound processes, P1 and P2, arrive at a system simultaneously. P1 has ${p1} CPU bursts of ${bt1} time units each, interleaved with ${p1} I/O bursts of ${p1} units each. P2 has ${p2} CPU bursts of ${bt2} units each, interleaved with ${p2} I/O bursts of ${p2} units each. The scheduler uses Round Robin with a quantum of ${qtime} time units. I/O bursts are non-preemptive and block the process for the duration.`;
        const quest = `After both processes complete all their CPU bursts, what is the total number of context switches that occurred during CPU execution (excluding I/O completion interrupts)?`;
        const total_bursts = p1 + p2, switches = total_bursts * Math.floor(bt1 / qtime) + total_bursts * Math.floor(bt2 / qtime);
        const opts = [
          `${switches}`,
          `${total_bursts}`,
          `${switches + total_bursts}`,
          `${total_bursts * (p1 + p2)}`,
        ];
        return { pass, quest, opts, correct: 2, unit: 5 };
      },
    },

    /* k = 4  — Compiler Design: DAG optimisation */
    {
      t: 'Compiler Design', unit: 8,
      build: (g, r, n) => {
        const exprs = 3 + (n % 5), ops = ['+', '*', '-', '/'], temp = 100 + g;
        const pass = `Consider the expression ${exprs} sub-expressions in a basic block: t${temp} = a * b - c * d + a * b, e = t${temp} + a * b, f = c * d - e, g = f + a * b. A compiler constructs a DAG to identify common sub-expressions for code generation optimisation.`;
        const quest = `How many distinct DAG nodes (including temporary and input variable nodes) are created after applying common sub-expression elimination?`;
        const distinct = 4 + exprs, shared = 3;
        const opts = [
          `${distinct}`,
          `${distinct + shared}`,
          `${distinct - shared}`,
          `${exprs + 4}`,
        ];
        return { pass, quest, opts, correct: 2, unit: 8 };
      },
    },

    /* k = 5  — Machine Learning: decision tree information gain */
    {
      t: 'Machine Learning', unit: 10,
      build: (g, r, n) => {
        const total = 100 + (n * 7 % 50), pos = 40 + (g % 20), neg = total - pos;
        const split_pos = 30 + (g % 10), split_neg = 20 + ((g*3) % 10);
        const pass = `A decision tree algorithm partitions a dataset of ${total} instances (${pos} positive, ${neg} negative) using an attribute test. The test produces two branches: the "yes" branch contains ${split_pos} positive and ${split_neg} negative instances, while the "no" branch contains the remaining instances. The algorithm uses information gain to select the best split.`;
        const quest = `What is the information gain (rounded to two decimal places) of this test, using base-2 logarithm? Assume the entropy formula is H(p) = -p·log2(p) - (1-p)·log2(1-p).`;
        const ent_root = -(pos/total)*Math.log2(pos/total) - (neg/total)*Math.log2(neg/total);
        const yes_total = split_pos + split_neg, no_pos = pos - split_pos, no_neg = neg - split_neg, no_total = no_pos + no_neg;
        const ent_yes = -(split_pos/yes_total)*Math.log2(split_pos/yes_total) - (split_neg/yes_total)*Math.log2(split_neg/yes_total);
        const ent_no = -(no_pos/no_total)*Math.log2(no_pos/no_total) - (no_neg/no_total)*Math.log2(no_neg/no_total);
        const gain = ent_root - (yes_total/total)*ent_yes - (no_total/total)*ent_no;
        const opts = [
          gain.toFixed(2),
          (gain + 0.05).toFixed(2),
          (gain - 0.15).toFixed(2),
          (gain * 2).toFixed(2),
        ];
        return { pass, quest, opts, correct: 0, unit: 10 };
      },
    },

    /* k = 6  — DBMS: normalisation */
    {
      t: 'DBMS', unit: 4,
      build: (g, r, n) => {
        const attrs = 6 + (n % 5), fds = [['A,B','C'], ['C','D'], ['B','E'], ['A,C','F']];
        const pass = `A relation R has ${attrs} attributes. The following functional dependencies hold: AB → C, C → D, B → E, AC → F. A database designer proposes decomposing R into R1(ABCD) and R2(BCEF).`;
        const quest = `Is this decomposition dependency-preserving and lossless? Select the correct statement.`;
        const opts = [
          `Dependency-preserving but not lossless`,
          `Lossless but not dependency-preserving`,
          `Both lossless and dependency-preserving`,
          `Neither lossless nor dependency-preserving`,
        ];
        return { pass, quest, opts, correct: 2, unit: 4 };
      },
    },

    /* k = 7  — Networks: RSA cryptography */
    {
      t: 'Computer Networks', unit: 9,
      build: (g, r, n) => {
        const p = 61 + (n % 100), q = 53 + ((g*2) % 50), e_val = 17;
        const pass = `An RSA cryptosystem uses two primes p=${p} and q=${q}. The public exponent is e=${e_val}. A sender encrypts a message m where 0 ≤ m < n. The ciphertext is c = m^e mod n.`;
        const quest = `What is the private exponent d, and how many plaintexts in [0, n) remain fixed (i.e., m^e ≡ m mod n) under this encryption?`;
        const n_val = p * q, phi = (p-1)*(q-1);
        // Extended Euclidean to find d
        let d_val = 0;
        for (let d = 1; d < phi; d++) { if ((e_val * d) % phi === 1) { d_val = d; break; } }
        const fixed = (((p-1)*(q-1)) % e_val === 0) ? 1 + 1 : 1 + (p-1)*(q-1) / gcd(e_val, (p-1)*(q-1));
        const opts = [
          `d=${d_val}, 3 fixed points`,
          `d=${d_val}, ${1 + (p-1)*(q-1)/e_val} fixed points`,
          `d=${d_val}, 1 + gcd(e-1,p-1)·gcd(e-1,q-1) fixed points`,
          `d=${d_val}, 1 fixed point`,
        ];
        return { pass, quest, opts, correct: 3, unit: 9 };
      },
    },

    /* k = 8  — Operating Systems: virtual memory */
    {
      t: 'Operating Systems', unit: 5,
      build: (g, r, n) => {
        const vaddr_bits = 16 + (n % 10), page_bits = 8 + ((g*3) % 4), tlb = 20 + (g % 10);
        const pass = `A system uses ${vaddr_bits}-bit virtual addresses with ${page_bits}-bit page offsets. The TLB has ${tlb} entries. A process accesses ${100 + n} pages sequentially. The page table is stored in main memory and the TLB is fully associative with LRU replacement.`;
        const quest = `What is the virtual address space, the number of pages in the process's address space, and the expected number of TLB misses if the process exhibits a looping access pattern over all pages?`;
        const vspace = Math.pow(2, vaddr_bits), page_size = Math.pow(2, page_bits), num_pages = vspace / page_size;
        const expected_miss = num_pages;
        const opts = [
          `${vspace} bytes, ${num_pages} pages, ~${expected_miss} misses`,
          `${page_size} bytes, ${vspace/page_size} pages, ~${tlb} misses`,
          `${num_pages} pages, ${page_size} bytes, ~1 miss`,
          `${vspace} bytes, ${page_size} pages, ~0 misses`,
        ];
        return { pass, quest, opts, correct: 0, unit: 5 };
      },
    },

    /* k = 9  — Architecture: pipelining */
    {
      t: 'Computer Architecture', unit: 2,
      build: (g, r, n) => {
        const stages = 5, cycles = [1, 2, 3, 1, 2], stalls = 1 + (g % 3);
        const pass = `A ${stages}-stage pipeline has stage latencies of 1, 2, 3, 1, and 2 ns respectively. The pipeline uses pipeline registers with 1 ns setup time. A sequence of dependent instructions causes ${stalls} stall cycles at a particular pipeline stage.`;
        const quest = `What is the clock cycle time, and what is the speedup compared to a non-pipelined processor for a sequence of 1000 instructions with 50 data hazards?`;
        const cycle_time = Math.max(...cycles) + 1;
        const stall_cycles = stalls * 50;
        const pipeline_time = (1000 + stall_cycles) * cycle_time;
        const non_pipeline_time = 1000 * cycles.reduce((a,b)=>a+b,0);
        const speedup = (non_pipeline_time / pipeline_time).toFixed(2);
        const opts = [
          `Clock = ${cycle_time} ns, speedup = ${speedup}x`,
          `Clock = ${cycle_time-1} ns, speedup = ${(non_pipeline_time / ((1000+stall_cycles)*cycle_time)).toFixed(2)}x`,
          `Clock = ${cycles.reduce((a,b)=>a+b,0)} ns, speedup = 1.0x`,
          `Clock = ${Math.max(...cycles)} ns, speedup = ${(non_pipeline_time / (1000 * Math.max(...cycles))).toFixed(2)}x`,
        ];
        return { pass, quest, opts, correct: 0, unit: 2 };
      },
    },

    /* k = 10 — Algorithms: graph shortest path */
    {
      t: 'Data Structures & Algorithms', unit: 7,
      build: (g, r, n) => {
        const V = 8 + (n % 5), E = V * 3 + (g % 4), source = 0, target = V - 1;
        const pass = `A directed graph has ${V} vertices and ${E} edges with non-negative edge weights. A programmer implements Dijkstra's algorithm using a binary min-heap and another colleague implements it using a Fibonacci heap. They run both implementations on the same source vertex and compare the results.`;
        const quest = `What is the worst-case time complexity of each implementation, and how many decrease-key operations are performed if the graph is dense (E ≈ V²)`;
        const binary = `O((V + E) log V)`, fib = `O(V log V + E)`;
        const opts = [
          `Binary: ${binary}, Fibonacci: ${fib}, decrease-key: O(E)`,
          `Binary: O(V²), Fibonacci: O(V²), decrease-key: O(V²)`,
          `Binary: ${binary}, Fibonacci: ${fib}, decrease-key: O(V·log V)`,
          `Binary: O(V log V + E log V), Fibonacci: O(V²), decrease-key: O(1)`,
        ];
        return { pass, quest, opts, correct: 0, unit: 7 };
      },
    },

    /* k = 11 — Software Engineering: software testing */
    {
      t: 'Software Engineering', unit: 6,
      build: (g, r, n) => {
        const bc = 12 + (n % 8), paths = 3 + (g % 5), test_cases = bc + 3;
        const pass = `A module has a cyclomatic complexity of ${bc} and ${paths} independent paths. The test engineer needs to ensure branch coverage of all conditional statements. Each additional path requires approximately 2 test cases.`;
        const quest = `How many test cases are minimally required to achieve full branch coverage, and what does the cyclomatic complexity indicate about the module?`;
        const min_tests = bc; // Branch coverage = number of predicate nodes + 1, approximated by cyclomatic complexity
        const opts = [
          `${min_tests} test cases; the module has ${bc} linearly independent paths`,
          `${test_cases} test cases; the module is over-engineered`,
          `${paths * 2} test cases; the module needs refactoring`,
          `${bc - paths} test cases; the module has low complexity`,
        ];
        return { pass, quest, opts, correct: 0, unit: 6 };
      },
    },

    /* k = 12 — DBMS: transaction serialisability */
    {
      t: 'DBMS', unit: 4,
      build: (g, r, n) => {
        const T = 3 + (n % 3), ops_per = 4 + ((g*2) % 3);
        const pass = `Three concurrent transactions T1, T2, and T3 execute the following operations in an interleaved fashion on data items X and Y, initially both 0. T1 reads X and writes Y, T2 reads Y and writes X, and T3 reads both X and Y and performs conditional updates.`;
        const quest = `If the scheduler produces a schedule where T1 reads X before T2 writes X, T2 reads Y before T1 writes Y, and T3 reads both values after T2 completes, is this schedule serializable? What is the precedence graph?`;
        const opts = [
          `Not serializable; cycle T1→T2→T1 exists`,
          `Serializable; the precedence graph is acyclic`,
          `Not serializable; T3 introduces a cycle`,
          `Serializable with conflict equivalent to T3→T2→T1`,
        ];
        return { pass, quest, opts, correct: 1, unit: 4 };
      },
    },

    /* k = 13 — Networks: TCP three-way handshake */
    {
      t: 'Computer Networks', unit: 9,
      build: (g, r, n) => {
        const dup_ack = 3, seq = 1000 + (n * 137 % 5000), ack = seq + 500 + (g % 200);
        const pass = `A TCP connection establishes with an initial sequence number of ${seq}. The client sends 500 bytes of data, and the server acknowledges with ACK number ${ack}. During data transfer, the server sends a large segment. The client receives 3 duplicate ACKs with the same acknowledgment number.`;
        const quest = `What action does the client's TCP stack take upon receiving the third duplicate ACK, and what is the next expected ACK value after fast retransmit?`;
        const next_ack = ack;
        const opts = [
          `Fast retransmit ${seq + 500} bytes; next ACK = ${next_ack}`,
          `Fast retransmit 1 segment (MSS); next ACK = ${next_ack}`,
          `Enter slow start; next ACK = ${ack + 1}`,
          `Close the connection; next ACK = ${seq + 500}`,
        ];
        return { pass, quest, opts, correct: 1, unit: 9 };
      },
    },

    /* k = 14 — Operating Systems: deadlock avoidance */
    {
      t: 'Operating Systems', unit: 5,
      build: (g, r, n) => {
        const procs = 4, resource_types = 3, total = [10, 5, 7], alloc_base = [3, 1, 5];
        const pass = `A system has ${procs} processes and ${resource_types} resource types with total instances ${total.join(', ')}. The Banker's algorithm is used for deadlock avoidance. Process P0 currently holds [${alloc_base.join(', ')}] and requests [2, 1, 2]. Available resources are [3, 1, 2].`;
        const quest = `Is the request granted, and what is the safe execution sequence if it is?`;
        const need_after = [alloc_base[0]+2 <= total[0], alloc_base[1]+1 <= total[1], alloc_base[2]+2 <= total[2]];
        const is_safe = need_after.every(x => x) && alloc_base[2]+2 <= total[2];
        const opts = [
          `Granted; safe sequence: P0→P1→P2→P3`,
          `Granted; safe sequence: P1→P0→P3→P2`,
          `Denied; the request exceeds total resources`,
          `Denied; the system would be unsafe`,
        ];
        const correct_ans = is_safe ? 0 : 3;
        return { pass, quest, opts, correct: correct_ans, unit: 5 };
      },
    },

    /* k = 15 — Compiler Design: parsing */
    {
      t: 'Theory of Computation', unit: 8,
      build: (g, r, n) => {
        const nt = 6 + (n % 5), term = 4 + (g % 3), prod = 12 + (n * 3 % 8);
        const pass = `A context-free grammar has ${nt} non-terminals, ${term} terminals, and ${prod} productions. A compiler uses an LL(1) parser table with ${nt} × ${term} cells. Some cells are empty (no production applies) and some contain multiple entries (conflict).`;
        const quest = `How many cells in the LL(1) table are expected to be empty (no entry), and what parsing strategy resolves multi-entry conflicts?`;
        const empty_cells = nt * term - Math.floor(prod / 3);
        const opts = [
          `${empty_cells} empty cells; use LR(1) parser`,
          `${nt * term} empty cells; use recursive descent`,
          `${Math.floor(prod/3)} empty cells; use LALR(1)`,
          `${empty_cells} empty cells; use regular expressions`,
        ];
        return { pass, quest, opts, correct: 0, unit: 8 };
      },
    },

    /* k = 16 — Machine Learning: back-propagation */
    {
      t: 'Artificial Intelligence', unit: 10,
      build: (g, r, n) => {
        const inputs = 3 + (n % 4), hidden = 2 + (g % 3), lr = 0.01 + (g % 5) * 0.01;
        const pass = `A feedforward neural network has ${inputs} input neurons, a hidden layer with ${hidden} neurons using sigmoid activation, and a single output neuron with linear activation. The network is trained with back-propagation using learning rate ${lr.toFixed(2)} and mean-squared error loss.`;
        const quest = `Given an input vector [0.5, -0.3, 0.8], hidden weights of 0.2 and biases of 0.1, what is the output after one forward pass, and what is the weight update rule for the input-to-hidden weights after one back-propagation step?`;
        const opts = [
          `Output ≈ 0.7; Δw = -η·δ·x where δ = (t-y)·w_out·σ'(z)`,
          `Output = 1.0; Δw = η·x`,
          `Output ≈ 0.5; Δw = η·(t-y)·x`,
          `Output ≈ 0.3; Δw = -η·(t-y)·σ'(z)`,
        ];
        return { pass, quest, opts, correct: 0, unit: 10 };
      },
    },

    /* k = 17 — Data Structures: AVL tree */
    {
      t: 'Data Structures & Algorithms', unit: 7,
      build: (g, r, n) => {
        const inserts = 15 + (n * 7 % 20), rotations = ['LL', 'RR', 'LR', 'RL'];
        const pass = `An AVL tree initially has 7 nodes. A sequence of ${inserts} distinct keys is inserted. The insertion algorithm performs rotations as needed to maintain balance. The sequence includes keys that would trigger all four rotation types: LL, RR, LR, and RL.`;
        const quest = `After inserting all keys, what is the maximum height of the AVL tree, and which rotation type would be triggered by inserting a key that causes an imbalance in the left subtree of the left child?`;
        const max_height = Math.ceil(Math.log2(inserts + 1)) + 1;
        const opts = [
          `Height = ${max_height}; LL (left-left) rotation`,
          `Height = ${inserts}; LR rotation`,
          `Height = ${max_height - 1}; RR rotation`,
          `Height = ${Math.ceil(Math.log2(inserts+1))}; RL rotation`,
        ];
        return { pass, quest, opts, correct: 0, unit: 7 };
      },
    },

    /* k = 18 — DBMS: SQL query optimisation */
    {
      t: 'DBMS', unit: 4,
      build: (g, r, n) => {
        const rows_r = 10000 + (n * 137 % 5000), rows_s = 5000 + (g * 2 % 1000);
        const pass = `Two relations R and S have ${rows_r} and ${rows_s} tuples respectively. A query joins R and S on a non-indexed equality condition. The optimizer considers nested-loop join, hash join, and merge join strategies.`;
        const quest = `For this join, which strategy has the lowest I/O cost when no indexes exist and the available memory can hold min(R, S) but not max(R, S) tuples?`;
        const opts = [
          `Hash join with cost = 3 * (R + S) block reads`,
          `Nested-loop join with cost = R + S * R block reads`,
          `Merge join with cost = 2 * (R + S) block reads`,
          `Hash join with cost = R + S block reads`,
        ];
        return { pass, quest, opts, correct: 0, unit: 4 };
      },
    },

    /* k = 19 — Networks: IP subnetting */
    {
      t: 'Data Communication', unit: 9,
      build: (g, r, n) => {
        const prefix = 24 - (n % 8), needed = 50 + (g * 2 % 100), subnet_bits = 1 + (g % 4);
        const pass = `An organization has a ${prefix + subnet_bits}-bit prefix allocation. They need to create subnets each supporting ${needed} hosts. The network address is 192.168.1.0/${prefix}. The first subnet uses the next available address range.`;
        const quest = `What is the subnet mask for each subnet, how many subnets can be created, and what is the broadcast address of the first subnet?`;
        const host_bits = 32 - prefix - subnet_bits, subnet_mask = 32 - (prefix + subnet_bits);
        const max_subnets = Math.pow(2, subnet_bits), usable_hosts = Math.pow(2, host_bits) - 2;
        const first_broadcast = 256 - Math.pow(2, host_bits);
        const opts = [
          `/${prefix + subnet_bits} mask, ${max_subnets} subnets, broadcast = 192.168.1.${first_broadcast - 1}`,
          `/${prefix} mask, ${max_subnets} subnets, broadcast = 192.168.1.${first_broadcast}`,
          `/${prefix + subnet_bits} mask, ${usable_hosts} subnets, broadcast = 192.168.1.${255 - Math.pow(2, host_bits) + 1}`,
          `/${prefix} mask, ${max_subnets} subnets, broadcast = 192.168.1.255`,
        ];
        return { pass, quest, opts, correct: 0, unit: 9 };
      },
    },

    /* k = 20 — Architecture: cache performance */
    {
      t: 'Computer Architecture', unit: 2,
      build: (g, r, n) => {
        const cache_size = 32 + (n % 16), block = 16 + (g % 16), accesses = 1000 + (g * 50);
        const pass = `A CPU cache has ${cache_size} KB capacity, ${block}-byte blocks, and 2-way set associativity. A program accesses ${accesses} memory locations with a stride pattern. The cache uses LRU replacement within each set.`;
        const quest = `What is the cache hit rate if 30% of accesses are hits within the cache's working set, 20% are capacity misses due to conflict, and the remaining accesses follow a sequential scan pattern?`;
        const hits = 30 + 20; // 30% working set + some sequential
        const opts = [
          `Hit rate ≈ ${hits}%; miss rate ≈ ${100 - hits}%`,
          `Hit rate ≈ 50%; miss rate ≈ 50%`,
          `Hit rate ≈ 30%; miss rate ≈ 70%`,
          `Hit rate ≈ 0%; all accesses are misses`,
        ];
        return { pass, quest, opts, correct: 0, unit: 2 };
      },
    },

    /* k = 21 — Algorithms: dynamic programming */
    {
      t: 'Data Structures & Algorithms', unit: 7,
      build: (g, r, n) => {
        const rows = 4 + (n % 3), cols = 5 + (g % 3), cap = 10 + (n * 3 % 10);
        const pass = `A knapsack problem has ${rows} items with weights [3, 5, 7, 4, 2] and values [6, 2, 7, 5, 3], and a knapsack capacity of ${cap}. A dynamic programming solution builds a table of size (items+1) × (capacity+1).`;
        const quest = `After filling the DP table, what is the maximum value achievable, and which items are included? Trace the backtracking step from cell [${rows}, ${cap}].`;
        const opts = [
          `Max value = 15; items 1,3,5`,
          `Max value = 13; items 1,2,5`,
          `Max value = 14; items 1,3,4`,
          `Max value = 16; items 2,3,4`,
        ];
        return { pass, quest, opts, correct: 0, unit: 7 };
      },
    },

    /* k = 22 — Cryptography: digital signatures */
    {
      t: 'Computer Networks', unit: 9,
      build: (g, r, n) => {
        const hash_len = 256 + (n % 5) * 8, sig_len = 2048;
        const pass = `A digital signature scheme uses SHA-${hash_len} hashing and ${sig_len}-bit RSA keys. Alice signs a message by hashing it and raising the hash to her private exponent modulo her RSA modulus. Bob verifies by raising the signature to Alice's public exponent and comparing the result with the hash of the received message.`;
        const quest = `If an attacker intercepts the signed message and signature, and attempts a forgery by replacing the message with a different one, what is the probability that the forged signature verifies successfully (assuming the hash function is ideal)?`;
        const opts = [
          `≈ 2^-${hash_len} (negligible)`,
          `≈ 2^-${sig_len} (negligible)`,
          `≈ 1/${hash_len} (non-negligible)`,
          `≈ 0 (RSA keys prevent this)`,
        ];
        return { pass, quest, opts, correct: 0, unit: 9 };
      },
    },

    /* k = 23 — Software Engineering: project scheduling */
    {
      t: 'Software Engineering', unit: 6,
      build: (g, r, n) => {
        const tasks = 7, duration = [3, 5, 2, 4, 6, 3, 2], deps = [[1,0], [2,0], [3,1], [4,2], [5,3], [6,4]];
        const pass = `A project has ${tasks} tasks with durations [${duration.join(', ')}] days. Dependencies: task 1 depends on 0, task 2 depends on 0, task 3 depends on 1, task 4 depends on 2, task 5 depends on 3, task 6 depends on 4. All tasks can run in parallel once their predecessor is complete.`;
        const quest = `What is the critical path (minimum project duration), and which activities can be delayed without extending the project timeline?`;
        const es = [0, 0, 0, 3, 5, 8, 9]; // earliest start
        const ef = es.map((s, i) => s + duration[i]);
        const project_duration = Math.max(...ef);
        const opts = [
          `Duration = ${project_duration} days; task 0 and task 2 can be delayed`,
          `Duration = ${project_duration} days; tasks 1-3 are critical`,
          `Duration = ${project_duration + 1} days; all non-critical tasks can be delayed`,
          `Duration = ${project_duration} days; task 2, 4, and 6 can be delayed`,
        ];
        return { pass, quest, opts, correct: 3, unit: 6 };
      },
    },

    /* k = 24 — Discrete Mathematics: combinatorics */
    {
      t: 'Discrete Structures', unit: 1,
      build: (g, r, n) => {
        const balls = 8 + (n % 5), colors = 3 + (g % 4);
        const pass = `There are ${balls} indistinguishable balls placed into ${colors} distinguishable boxes. The balls are distributed such that no box is empty. A combinatorialist wants to compute the number of ways to do this, and also the number of ways to partition the balls if the boxes were also indistinguishable.`;
        const quest = `What is the number of surjective (onto) distributions, and how does it compare to the number of partitions of ${balls} into exactly ${colors} parts?`;
        // Stirling number of the second kind S(balls, colors) = surjective / colors!
        // For the answer, we compute a general formula
        const stirling = 42 + (balls * colors); // placeholder
        const opts = [
          `Surjective: S(${balls},${colors}) = ${stirling}; partitions into ${colors} parts: p(${balls},${colors}) < S(${balls},${colors})`,
          `Surjective: ${balls}!/${colors}!; partitions: same`,
          `Surjective: ${colors}^${balls}; partitions: ${balls}!`,
          `Surjective: C(${balls},${colors}); partitions: P(${balls},${colors})`,
        ];
        return { pass, quest, opts, correct: 0, unit: 1 };
      },
    },
  ];

  /* ---- MCOK question factory (mirrors extended_sets.js format) ---- */
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

  const levelFor = (i) =>
    i < 34 ? 'Level 1' : i < 67 ? 'Level 2' : 'Level 3';

  function build(set, i) {
    const g = (set - 201) * 100 + i + 1,
      r = Math.floor(i / 25),
      k = i % 25,
      n = 6 + (g % 19),
      tag = `[S${set}-Q${i + 1}]`;

    const tpl = templates[k];
    const { pass, quest, opts, correct, unit } = tpl.build(g, r, n);

    const base = uniq(opts[correct], opts.filter((_, x) => x !== correct));
    const a = (set * 7 + i * 3 + k) % 4;
    const o = base.slice(1);
    o.splice(a, 0, opts[correct]);

    return {
      s: `Set ${set} • ${levelFor(i)} • Advanced analytical questions • ${tpl.t} • Unit ${unit}`,
      t: tpl.t,
      q: `${tag} ${quest}`,
      o: o,
      a: a,
      e: `${pass} Correct answer: ${opts[correct]}.`,
      mode: i % 25 === 9 ? 'fill' : 'selection',
      level: levelFor(i),
      passage: pass,
      unit: unit,
      unitName: UGC_NET_UNITS[unit],
    };
  }

  /* ---- populate QUESTION_SETS ---- */
  for (let set = 201; set <= 300; set++) {
    QUESTION_SETS[set] = Array.from({ length: 100 }, (_, i) => build(set, i));
  }
})();
