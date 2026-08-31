/* Build the final explanation only after every source-bank overlay has loaded. */
(function(){
const prompts={
  'Level 1':'Apply the governing definition carefully before selecting.',
  'Level 2':'Analyze the conditions, rule out near-correct alternatives, and then answer.',
  'Level 3':'Evaluate every constraint and choose the most technically defensible conclusion.'
};
const quote=value=>`“${String(value??'').trim()}”`;
const clean=value=>String(value||'')
  .replace(/\s*Solution derivation:.*$/is,'')
  .replace(/^\s*(?:Correct answer|The (?:published |keyed )?answer is|The published key gives)\s*:\?\s*/i,'')
  .replace(/\s*Source:\s*.*$/is,'')
  .trim();
const weak=value=>!value||value.length<65||/^(?:Correct answer|The (?:published |keyed )?answer|The published key gives)\b/i.test(value);

function conceptRationale(question){
  const stem=String(question.q||''),topic=String(question.t||''),text=`${topic} ${stem}`,correct=question.o[question.a];
  if(/Child-window browsing histories/i.test(stem))return 'A parent browsing context and its child windows contribute entries to a joint session history in the time order in which navigations occur. Their entries are therefore chronologically interleaved; there is no numeric interleaving rule, and the histories are not unrelated.';
  if(/default positioning value/i.test(stem))return 'CSS sets the initial value of the position property to static. A statically positioned element remains in normal document flow; relative, absolute, and fixed positioning apply only when explicitly selected.';
  if(/browser viewport/i.test(stem)&&/position/i.test(text))return 'position: fixed uses the viewport as its containing block in the normal case, so the element stays at the same screen position while the document scrolls. Relative positioning offsets an element from its normal position, while static does not create a positioned element.';
  if(/all-pairs shortest/i.test(stem))return 'Floyd–Warshall performs dynamic programming over every possible intermediate vertex and computes shortest paths for all ordered vertex pairs. Dijkstra is normally single-source, whereas Prim and Kruskal construct minimum spanning trees rather than shortest paths.';
  if(/pushdown automaton differs/i.test(stem))return 'A pushdown automaton augments finite control with an unbounded LIFO stack. That stack supplies the memory needed for nested structures in context-free languages; the other choices do not describe the defining extension beyond a finite automaton.';
  if(/PDA may accept/i.test(stem))return 'A pushdown automaton can be defined to accept when it reaches a final state or when its stack becomes empty. For nondeterministic PDAs these two acceptance conventions recognize the same class of context-free languages.';
  if(/Regular expressions describe/i.test(stem))return 'Regular expressions denote exactly the regular languages, which are Type 3 in the Chomsky hierarchy. Types 2, 1, and 0 respectively allow context-free, context-sensitive, and unrestricted languages and are strictly more expressive.';
  if(/multi-head Turing/i.test(stem))return 'A multi-head Turing machine has two or more read/write heads operating on its tape or tapes under one finite control. Multiple heads change how cells are accessed, not the existence of the tape alphabet or finite controller.';
  if(/assignment problem.*special case/i.test(stem))return 'The assignment problem is a balanced transportation problem in which every source supply and destination demand equals one. Knapsack, shortest-path, and maximum-flow problems have different variables and constraints.';
  if(/Kuhn.?Tucker/i.test(stem))return 'Karush–Kuhn–Tucker conditions generalize Lagrange multiplier conditions for constrained nonlinear optimization. They express stationarity, feasibility, complementary slackness, and multiplier sign conditions—not parsing or operating-system scheduling rules.';
  if(/MYCIN/i.test(stem))return 'MYCIN was a rule-based medical expert system developed to recommend antibiotics for bacterial infections. It is an AI system using knowledge rules and certainty factors, not a database function, programming identifier, or isolated PROLOG clause.';
  if(/Forward reasoning/i.test(stem))return 'Forward chaining is data-driven: it begins with known facts and repeatedly fires applicable rules until a goal is derived or no rule applies. Backward chaining instead starts with a goal and works toward supporting facts.';
  if(/PROLOG.*facts and rules|statement about PROLOG/i.test(stem))return 'PROLOG is a declarative logic-programming language. A program states facts and rules, and execution attempts to satisfy queries through unification and backtracking rather than following C-style imperative structure.';
  if(/data warehouse/i.test(text)&&/decision-support/i.test(stem))return 'A data warehouse integrates historical, subject-oriented, nonvolatile data specifically for analysis and decision support. Operational files and individual MIS reports lack the integrated historical organization required for broad analytical queries.';
  if(/reference unlike a pointer/i.test(stem))return 'A C++ reference is an alias that must normally be initialized, cannot be reseated after binding, and is used without an explicit dereference operator. Those properties jointly distinguish it from a pointer, so the inclusive option is correct.';
  if(/change in one element affecting another/i.test(stem))return 'In UML, dependency means that a client element relies on a supplier, so a supplier change may affect the client. Association models a structural link, aggregation a whole–part relationship, and realization implementation of a specification.';
  if(/vectored interrupt/i.test(stem))return 'In a vectored interrupt, the interrupting device or interrupt mechanism provides vector information that identifies the appropriate service routine. This avoids using one fixed branch address for every interrupt source.';
  if(/direct peripheral-to-memory/i.test(stem))return 'Direct Memory Access transfers blocks between an I/O device and main memory with minimal CPU intervention. The DMA controller temporarily controls the bus; the other terms do not name this transfer mechanism.';
  if(/first commercial microprocessor/i.test(stem))return 'Intel introduced the 4004 in 1971 as its first commercially available microprocessor. The 8008 and 8080 were later processors, while 8800 is not the correct Intel model here.';
  if(/cyclomatic complexity/i.test(text)&&/edges|vertices|flow graph/i.test(stem))return 'For one connected control-flow graph, McCabe cyclomatic complexity is V(G)=E−N+2. Substitute the stated edge count for E and vertex count for N; the alternatives change the constant or reverse E and N.';
  if(/complete graph K|edges.*complete graph/i.test(stem))return 'Every pair of distinct vertices in a simple complete graph contributes exactly one edge. Therefore Kₙ has C(n,2)=n(n−1)/2 edges; ordered-pair and self-loop counts are not applicable.';
  if(/tree contains.*vertices.*edges/i.test(stem))return 'Every finite connected acyclic graph with V vertices has exactly V−1 edges. Adding an edge creates a cycle, while removing one disconnects the tree.';
  if(/full binary tree/i.test(stem)&&/leaves|count/i.test(stem))return 'In a full binary tree every internal node has exactly two children, which gives the invariant L=I+1 and total nodes 2I+1. Applying the relevant invariant yields the keyed option.';
  if(/load factor/i.test(stem)&&/hash/i.test(text))return 'A hash table’s load factor is α=n/m, where n is the number of stored keys and m is the number of slots. Dividing in the reverse order or changing either quantity produces the distractor values.';
  if(/page size 2\^|page offset/i.test(stem))return 'A page of 2^p bytes needs p low-order address bits to select a byte within that page. The remaining high-order bits identify the virtual page number.';
  if(/FCFS.*average waiting/i.test(stem))return 'FCFS runs jobs in arrival order. The first waits 0, the second waits for the first burst, and the third waits for both preceding bursts; averaging those three waiting times yields the keyed value.';
  if(/Cache time|average access|hit rate/i.test(stem))return 'With the formula stated in the stem, average access time is cache time plus miss probability multiplied by the memory penalty: Tc+(1−H)Tm. The hit rate must first be converted from a percentage to a fraction.';
  if(/pipeline.*latency/i.test(stem))return 'Ignoring latch overhead, one instruction must pass through every pipeline stage. Its latency is therefore number of stages × stage time; pipelining improves throughput but does not reduce this single-instruction latency.';
  if(/Transmission time/i.test(stem))return 'Serialization delay is L/R. Convert bytes to bits by multiplying by eight, divide by the link rate in bits per second, and convert seconds to milliseconds; propagation delay is not part of the stated calculation.';
  if(/IPv4 prefix|usable hosts|subnet/i.test(stem))return 'For h host bits an ordinary IPv4 subnet provides 2^h−2 usable addresses after reserving network and broadcast addresses. Choose the smallest h meeting the requirement, then the prefix length is 32−h.';
  if(/CRC.*degree|remainder bits/i.test(stem))return 'A generator polynomial of degree r produces an r-bit CRC remainder. Polynomial degree is one less than the number of coefficients, so using r+1 confuses coefficients with appended remainder bits.';
  if(/CROSS JOIN|Cartesian product/i.test(stem))return 'A CROSS JOIN forms every possible pair consisting of one row from each input. Its cardinality is therefore |A|×|B| when no predicate filters the result.';
  if(/selection retains|output cardinality/i.test(stem))return 'Estimated selection cardinality equals input rows multiplied by the selectivity fraction. Convert the percentage to a decimal, multiply by the row count, and apply the rounding instruction in the stem.';
  if(/confidence/i.test(text)&&/X.*Y|jointly/i.test(stem))return 'Association-rule confidence is support(X∪Y)/support(X). It estimates the conditional probability of Y given X; dividing by joint-plus-antecedent support or reversing the ratio answers a different quantity.';
  if(/Confusion counts|Accuracy/i.test(stem))return 'Classification accuracy is (TP+TN)/(TP+TN+FP+FN): all correct predictions divided by all predictions. TP/(TP+FP) is precision, while TP/(TP+FN) is recall.';
  if(/Caesar/i.test(stem))return 'Caesar encryption maps the letter to 0–25, adds the stated shift modulo 26, and maps the result back to a letter. Subtraction performs decryption, while omitting modulo fails when the alphabet wraps.';
  if(/binary search/i.test(stem))return 'Binary search compares the middle element and discards half of the remaining sorted range after each comparison. Repeated halving gives logarithmic growth, approximately log₂(n) steps.';
  if(/committees|chosen from/i.test(stem))return 'A committee is unordered, so use the combination C(n,r)=n!/[r!(n−r)!]. Permutations and n^r count order or repeated choices that the question does not allow.';
  if(/Product construction.*DFA/i.test(stem))return 'The product automaton records one state from each DFA, so its states are ordered pairs. With m and n component states there can be at most mn product states.';
  if(/two.?s-complement/i.test(text)&&/largest signed/i.test(stem))return 'An n-bit two’s-complement integer has range −2^(n−1) through 2^(n−1)−1. One bit represents sign weight, making the largest positive value one less than 2^(n−1).';
  if(/binary|decimal|hexadecimal/i.test(text)&&/Convert|Express|value/i.test(stem))return 'Use positional notation: each digit contributes its value multiplied by the base raised to its position. Repeated division by the target base gives the same result, while the distractors reflect a changed value, wrong base, or reversed digits.';
  if(/2PL|two-phase locking/i.test(text))return 'Two-phase locking has a growing phase that acquires locks and a shrinking phase that releases them. This guarantees conflict serializability, although ordinary 2PL can still deadlock and only stricter variants guarantee stronger recovery properties.';
  if(/foreign key|referential integrity/i.test(text))return 'Referential integrity requires each non-null foreign-key value to match an existing candidate or primary key in the referenced relation. A foreign key need not be unique and may be null when the schema permits it.';
  if(/postfix/i.test(stem)&&/stack|evaluate/i.test(text))return 'Postfix evaluation scans left to right, pushes operands, and on each operator pops its operands, applies the operator, and pushes the result. This LIFO requirement makes a stack the appropriate structure.';
  if(/page fault/i.test(stem))return 'A page fault occurs when a referenced virtual-memory page is not currently resident in physical memory. The operating system must locate and load the page, possibly replacing another frame, before restarting the instruction.';
  if(/starvation/i.test(stem)&&/Shortest Job|SJF|priority/i.test(text))return 'A steady stream of shorter or higher-priority jobs can repeatedly overtake a waiting long or low-priority job, causing starvation. Aging is a standard mitigation; FCFS does not permit such overtaking.';
  if(/binary exponential backoff|fourth collision/i.test(text))return 'After k collisions, binary exponential backoff chooses uniformly from 2^k slots. Immediate retry means choosing slot zero, so after four collisions its probability is 1/16.';
  if(/HTTPS|TLS/i.test(text))return 'HTTPS carries HTTP through TLS. Public-key techniques authenticate and establish shared secrets, after which efficient symmetric session encryption protects application data and integrity checks detect modification.';
  if(/deterministic finite automaton|DFA recognizes/i.test(text))return 'A DFA has finite memory and recognizes exactly the regular languages. Context-free languages may require stack memory, while the higher Chomsky classes require still more powerful machines.';
  if(/Lexical analysis|lexer/i.test(text))return 'The lexical analyzer groups the input character stream into tokens such as identifiers, keywords, literals, and operators. The parser consumes those tokens to construct grammatical structure; lexical analysis does not directly emit machine code.';
  if(/black-box|source-code knowledge/i.test(text))return 'Black-box testing derives cases from specified inputs and outputs without relying on internal code structure. White-box measures such as statement coverage require knowledge of the implementation.';
  if(/Apriori/i.test(text))return 'The Apriori downward-closure property says every non-empty subset of a frequent itemset must also be frequent. Consequently, any candidate containing an infrequent subset can be pruned safely.';
  if(/A\* search|g\(n\).*h\(n\)/i.test(text))return 'A* evaluates a node with f(n)=g(n)+h(n), combining the exact cost from the start with an estimate to the goal. Using only h is greedy best-first search, and subtraction does not represent estimated path cost.';
  if(/Cache memory.*locality|locality of reference/i.test(text))return 'Cache works because programs exhibit temporal locality (recently used data is likely to be reused) and spatial locality (nearby data is likely to be used). The other choices are unrelated to memory-hierarchy hit behavior.';
  if(/inorder|binary search tree.*sorted/i.test(text))return 'Inorder traversal visits the left subtree, then the node, then the right subtree. Because every BST left key is smaller and every right key larger, this order produces sorted keys.';
  return '';
}

function fallbackRationale(question){
  const correct=question.o[question.a],wrong=question.o.filter((_,index)=>index!==question.a);
  return `The stem asks specifically: ${quote(question.q)}. In ${question.t}, the applicable definition or computation leads to ${quote(correct)}. This choice satisfies every condition stated in the question. The alternatives ${wrong.map(quote).join(', ')} either describe different concepts or fail at least one stated condition, so they cannot complete this MCQ correctly.`;
}

function distractorRationale(question,option,correct){
  const stem=String(question.q||''),choice=String(option||''),answer=String(correct||'');
  const numeric=value=>/^-?\d+(?:\.\d+)?(?:\s*(?:ns|ms|bytes|bits|MB|KB|%))?$/i.test(value.trim());
  if(numeric(choice)&&numeric(answer))return `${quote(choice)} is not the result obtained when the quantities and units in the stem are substituted into the required formula. It reflects a different arithmetic operation, conversion, or rounding step. Following the calculation described below produces ${quote(answer)} instead.`;
  if(/\bonly\b|\balways\b|\bnever\b|\bevery\b/i.test(choice))return `${quote(choice)} makes a stronger absolute claim than the rule in the stem permits. A single excluded case is enough to reject an “only,” “always,” “never,” or “every” statement; the applicable rule supports ${quote(answer)} without that unsupported restriction.`;
  if(/none|neither|cannot|invalid|unrelated/i.test(choice))return `${quote(choice)} denies the relationship or result tested by the stem, but the governing ${question.t} rule establishes that relationship directly. The evidence therefore supports ${quote(answer)}, not the negative distractor.`;
  if(/all|both|either/i.test(choice)&&!/all|both|either/i.test(answer))return `${quote(choice)} incorrectly combines alternatives. The stem’s conditions identify one specific result—${quote(answer)}—and at least one claim bundled into ${quote(choice)} is not supported.`;
  return `${quote(choice)} is a plausible distractor, but it does not match the precise definition, operation, layer, property, or result requested in the stem ${quote(stem)}. Applying the relevant ${question.t} principle leads to ${quote(answer)}; the detailed reasoning below shows the decisive distinction.`;
}

Object.values(QUESTION_SETS).forEach(questions=>questions.forEach(question=>{
  const original=String(question.e||'').replace(/\s*Solution derivation:.*$/is,'').trim();
  const specific=conceptRationale(question);
  let explanation;
  if(specific)explanation=specific;
  else if(!weak(original))explanation=original;
  else explanation=fallbackRationale(question);
  const answer=question.o[question.a];
  question.e=`${explanation} Therefore, ${quote(answer)} is the correct option.`;
  question.optionReasons=question.o.map((option,index)=>index===question.a
    ? `${quote(option)} is correct because it is the result established by the rule or calculation explained below.`
    : distractorRationale(question,option,answer));
  const prompt=prompts[question.level]||prompts['Level 2'];
  if(!question.q.startsWith(prompt))question.q=`${prompt} ${question.q}`;
}));
})();
