/* Raise cognitive demand consistently and introduce multi-select questions in every set. */
const COMPLEXITY_PROMPTS={
  'Level 1':'Apply the governing definition carefully before selecting.',
  'Level 2':'Analyze the conditions, rule out near-correct alternatives, and then answer.',
  'Level 3':'Evaluate every constraint and choose the most technically defensible conclusion.'
};
const derivationFor=question=>{
  const text=`${question.t} ${question.q}`;
  if(/minimum distance|code.*correct.*error/i.test(text))return 'Formula: correctable errors t = floor((d_min − 1)/2). Substitute the stated minimum distance, simplify, and compare the result with the options.';
  if(/collision|backoff|retransmit immediately/i.test(text))return 'Formula: after k collisions, binary exponential backoff selects one of 2^k slots; immediate retransmission has probability 1/2^k. Substitute k from the question.';
  if(/cyclomatic/i.test(text))return 'Formula: for one connected control-flow graph, V(G) = E − N + 2, where E is the number of edges and N is the number of vertices.';
  if(/recurrence|T\(n\)/i.test(text))return 'Process: identify a, b and f(n) in T(n)=aT(n/b)+f(n), compute n^(log_b a), then apply the matching Master-Theorem case.';
  if(/probability|birthday/i.test(text))return 'Process: count favourable arrangements, divide by all equally likely outcomes, and simplify. For twelve distinct months the ratio is 12!/12^12.';
  if(/subnet|host.*mask/i.test(text))return 'Formula: usable hosts = 2^h − 2. Choose the smallest h satisfying the host requirement, then prefix length = 32 − h and convert it to dotted-decimal mask.';
  if(/cache.*average|hit ratio|access time/i.test(text))return 'Formula: average access = cache time + miss probability × main-memory time = T_cache + (1−H)T_memory.';
  if(/binary|decimal equivalent|two.?s complement|number system/i.test(text))return 'Process: expand positional weights Σ(bit × 2^position). For a two’s-complement negative value, invert, add 1, and apply the negative sign.';
  if(/permission|octal/i.test(text))return 'Process: convert each octal digit independently to three permission bits using 4=r, 2=w and 1=x, then concatenate owner, group and other permissions.';
  if(/fragment|MTU/i.test(text))return 'Formula: payload per nonfinal fragment = floor((MTU−header)/8)×8; fragments = ceil(original payload/payload per fragment). The multiple-of-eight rule comes from the IPv4 fragment offset.';
  if(/full binary tree|binary trees possible|Catalan/i.test(text))return 'Formula/process: use the full-tree invariant N=2I+1 when applicable; structural binary-tree counts use Catalan C_n=(1/(n+1))·binomial(2n,n).';
  if(/complexity|linear search|binary search|sorting/i.test(text))return 'Process: count the dominant operations as input size grows, discard constants/lower-order terms, and compare the resulting asymptotic bounds.';
  if(/SQL|DBMS|functional depend|normal form|serializ/i.test(text))return 'Process: apply relational constraints in order—identify keys/determinants, test the stated dependency or integrity rule, then reject choices that violate tuple or transaction semantics.';
  if(/Automata|grammar|PDA|FSM|regular expression|compiler|parser/i.test(text))return 'Process: classify the machine or production by its memory and production restrictions, derive the accepted language/parse behaviour, and eliminate options belonging to a stronger or weaker language class.';
  if(/graph|shortest path|MST|AVL|heap|linked|queue|stack|tree/i.test(text))return 'Process: apply the data-structure invariant step by step, update the affected nodes/links, and verify the final ordering, balance, path, or traversal condition.';
  if(/network|Ethernet|TCP|HTTP|GSM|OSI|router|protocol|security|encrypt|signature/i.test(text))return 'Process: locate the operation in the protocol stack, identify the addressing/reliability/security responsibility at that layer, and eliminate choices assigned to other layers.';
  if(/operating|UNIX|scheduling|deadlock|paging|memory|file system|thread/i.test(text))return 'Process: trace the relevant OS state transition or allocation rule, apply the scheduler/memory/file invariant, and compare the resulting state with each option.';
  if(/software|testing|cohesion|coupling|function point|requirement|prototype/i.test(text))return 'Process: identify the lifecycle phase and engineering objective, apply the corresponding design/testing/measurement rule, and reject activities belonging to another phase.';
  if(/Artificial|AI|PROLOG|LISP|expert|speech|MYCIN|reasoning/i.test(text))return 'Process: identify the knowledge representation or search/inference direction, follow how facts and rules produce the conclusion, and compare that mechanism with each alternative.';
  if(/Graphics|transformation|clipping|pixel|touch screen/i.test(text))return 'Process: represent the operation using its transformation or device rule, apply operations in the stated order, and test the resulting geometry/interaction against the choices.';
  if(/C\+\+|Java|C Programming|program|reference|pointer/i.test(text))return 'Process: trace values, scope, storage duration and side effects statement by statement; the final value/state determines the correct option.';
  return 'Process: identify the governing definition, substitute the facts supplied in the stem, eliminate choices that violate a stated constraint, and verify the remaining conclusion against the standard subject rule.';
};
Object.values(QUESTION_SETS).forEach((questions,setIndex)=>questions.forEach((question,index)=>{
  const prompt=COMPLEXITY_PROMPTS[question.level]||COMPLEXITY_PROMPTS['Level 2'];
  question.q=`${prompt} ${question.q}`;
  /* Keep the authored explanation attached to this exact MCQ. The former
     keyword-based derivation could select a rule that belonged to a different
     concept merely because both stems contained a broad term such as
     "memory", "graph", or "complexity". */
  question.e=String(question.e||'').replace(/\s*Solution derivation:.*$/s,'').trim();
}));
