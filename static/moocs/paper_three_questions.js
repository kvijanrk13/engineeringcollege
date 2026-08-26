/* Paper III C-04-17: transcribed and answer-checked from the user-supplied scan. */
const P3_RAW=[
['Algorithms','Sorting algorithms are generally characterized as','Both simple O(n²) and sophisticated O(n log n) methods','Only O(n²) methods','Only O(n log n) methods','Neither category'],
['Complexity','Which statement is certainly true?','P is a subset of NP','NP is a subset of P','P equals NP','Every NP problem is NP-hard'],
['Optimization','Which technique commonly solves 0/1 knapsack using bounds?','Branch and bound','Greedy method only','Floyd algorithm','Simplex method'],
['Algorithms','The standard all-pairs shortest-path algorithm is','Floyd–Warshall','Dijkstra','Prim','Kruskal'],
['Complexity','Which NP-completeness statement is correct?','All listed statements','NP-hardness uses reduction from a known hard problem','Circuit SAT was the first NP-complete problem','NP-complete problems are NP-hard'],
['Formal Languages','Regular expressions describe which Chomsky class?','Type 3','Type 0','Type 1','Type 2'],
['Formal Languages','Which listed regular-expression identities are valid over {0,1}?','All listed identities','(01)*0 = 0(10)*','A 0 before a later 1 implies an adjacent 01','Strings containing 0 plus 1*0* cover all binary strings'],
['Automata','A pushdown automaton differs chiefly through its','Stack memory','Second input alphabet','Output tape','Random-access memory'],
['Automata','A PDA may accept by','Either final state or empty stack','Final state only','Empty stack only','Neither method'],
['Turing Machines','A multi-head Turing machine has','More than one tape head','More than one finite control','No tape alphabet','Only one readable cell'],
['Operations Research','The assignment problem is a special case of','Transportation','Shortest path','Knapsack','Maximum flow'],
['Optimization','Kuhn–Tucker conditions are used in','Nonlinear programming','Parsing','Disk scheduling','Relational algebra'],
['Artificial Intelligence','Generate-and-test is a','Heuristic AI search technique','Software testing utility only','LISP clause','Database operation'],
['Artificial Intelligence','MYCIN is','An expert system','A MySQL function','A C identifier','A PROLOG clause'],
['Artificial Intelligence','Forward reasoning searches','From start facts toward a goal','From goal to start','Only within a window','By removing recursion'],
['Logic Programming','Which statement about PROLOG is true?','Programs describe problems with facts and rules','Programs have C structure','It only finds syntax errors','It developed UNIX'],
['Data Warehousing','The best repository for decision-support analysis is a','Data warehouse','MIS report','Single operational file','File structure'],
['Information Systems','Process diagrams in MIS design are called','Flowcharts','Context diagrams only','ER diagrams','Deployment diagrams'],
['C++','Why is a reference unlike a pointer?','All listed reasons','It normally cannot be null','It cannot be reseated after binding','It needs no explicit dereference operator'],
['UML','A change in one element affecting another is modeled as','Dependency','Association','Realization','Aggregation'],
['C++','Which set is true: overloading is compile-time; protected members reach derived classes; friend functions call normally?','All three statements','First only','Second only','None'],
['Web','Child-window browsing histories are','Chronologically interleaved','Numerically interleaved','Both numerical and chronological','Never related'],
['CSS','The default positioning value is','static','relative','absolute','fixed'],
['CSS','Positioning relative to the browser viewport uses','fixed','relative','static','inherit'],
['Architecture','In a vectored interrupt','The source supplies vector information','The branch address is always fixed','A general register supplies it','No service address is needed'],
['Cache','A 32K×12 main memory with 512-word direct cache needs how many data-plus-tag bits per cache word?','18 bits','36 bits','9 bits','27 bits'],
['I/O','Direct peripheral-to-memory transfer is','DMA','DDA','Serial interface','Three-way handshaking'],
['Microprocessors','Intel’s first commercial microprocessor was','4004','8008','8080','8800'],
['Microprocessors','Which 8085 interrupts are level-triggered?','RST 6.5 and RST 5.5','INTR and TRAP','RST 7.5 and RST 6.5','RST 7.5 only'],
['Software Engineering','Which model modularizes cross-cutting concerns?','Aspect-oriented model','Spiral model','Incremental model','Prototype model'],
['Software Engineering','Which is not software validation?','Selecting a programming environment','Code walkthrough','Unit testing and correction','Refactoring'],
['UML','Which artifact captures actor–system interactions?','Use-case diagram','Component diagram','Class diagram','Deployment diagram'],
['Software Engineering','Refactoring does not examine a system for','Inconsistent requirements','Unused design elements','Inappropriate data structures','Redundancy'],
['Testing','Frequent builds are commonly assessed through','Smoke testing','Regression testing only','Big-bang integration','System testing only'],
['Metrics','For a connected flow graph with m edges and n vertices, cyclomatic complexity is','m − n + 2','n − m + 2','m − n + 1','n − m + 1'],
['DBMS','Which FD set can yield 3NF but not BCNF for R(A,B,C,D)?','AB→CD, C→DA','AB→CD, A→C, D→B','AB→CD, C→A, D→B','A→BCD, B→CD, C→D'],
['DBMS','For rows (1,4,2),(1,5,3),(1,6,3),(3,2,2), which dependencies hold?','BC→A and B→C','AB→C and C→A','BC→A and A→C','AC→B and B→A'],
['SQL','A CASE expression provides','IF–THEN–ELSE logic','Looping','Table definition','Transaction start'],
['ER Model','A subclass with multiple distinct superclasses is a','Category (union type)','Aggregation','Composition','Ordinary specialization'],
['Relational Algebra','R1(RollNo,Name,Grade) and R2(RollNo,SubjectId,Grade) cannot directly use','Union','Selection','Join','Projection'],
['Database Security','Privilege grant and revocation history is tracked by a','Grant graph','Serializability graph','Transaction diagram','View graph'],
['Compiler','Which is not a compiler-construction tool?','Interpreter','Parser generator','Scanner generator','Automatic code generator'],
['SDT','For S→aA {1}, S→a {2}, A→Sb {3}, bottom-up parsing aab prints','2 3 1','1 3 2','2 2 3','Syntax error'],
['Networking','How many fragments are required for a 1200-byte IPv4 datagram with a 20-byte header on an MTU-80 link?','22','12','15','20'],
['Protocols','Which pair can both use multiple TCP connections per client/server?','HTTP and FTP','HTTP and TELNET','FTP and SMTP','HTTP and SMTP'],
['Coding','XOR of two valid linear-block codewords is another','Valid codeword','Invalid codeword','Valid dataword only','Invalid dataword'],
['Coding','A cyclic-code generator polynomial acts as the','Divisor','Multiplier','Adder','Subtractor'],
['Communications','Synchronous transmission omits per-character','Start bits, stop bits, and gaps','Start bits only','Stop bits only','Gaps only'],
['Line Coding','Code redundancy that detects transmission errors is','Built-in error detection','Baseline wandering','Self-synchronization','Complexity'],
['Operating Systems','Signal dispositions are','Inherited by fork; caught handlers reset by exec','Never inherited by fork','Always unchanged by exec','Destroyed by fork'],
['UNIX','Which is not normally a filter?','date','sort','cat','grep'],
['UNIX','With seven logged-in terminals, `date; who | wc -l` prints','Date followed by 7','Date followed by 8','Date followed by 1','An error'],
['UNIX','Initial file permissions are controlled by','umask','chmod value','tmask','username'],
['Windows','Which is not a defined mandatory named window-creation parameter?','An arbitrary lParams','Class name','Window name','Menu name'],
['Windows','WinMain arguments communicate with the','Operating system','Hardware','Compiler only','Application database'],
['Compiler','Basic blocks and successor edges form a','Flow graph','DAG only','Control tree','Hamiltonian graph'],
['Parsing','Operator-precedence error recovery may use','Insertion or deletion corrections','Insertion only','Stack deletion only','Input deletion only'],
['Graphics','A pixel mapping that cannot be reconstructed without error is','Irreversible','Reversible','Temporal','Facsimile'],
['Windows','Which classes derive directly or indirectly from CWnd?','CFrameWnd, CMDIFrameWnd, and CMDIChildWnd','CFrameWnd only','CMDIFrameWnd only','CMDIChildWnd only'],
['Memory','Paging causes','Internal fragmentation','External fragmentation','Compaction','Leakage'],
['Virtual Memory','Without a TLB hit, page-table lookup makes access about','Twice as long','Three times longer','Unchanged','Half as long'],
['Networking','An IP address is a','Logical address','Physical address','Invalid address','Memory address'],
['Windows','The classic WinMain signature returns int and receives','Two HINSTANCEs, LPSTR, and int','No parameters','Only LPSTR','A real final argument'],
['Compiler','Intermediate-code forms include','Postfix, syntax trees, and three-address code','Postfix only','Syntax trees only','Three-address code only'],
['Compiler','Panic-mode recovery is advantageous because','It is simple and guarantees progress','It is difficult','It never discards input','It repairs every error exactly'],
['Data Mining','Straightforward nearest-neighbour search over n objects is','O(n)','O(n²)','O(n log n)','O(1)'],
['Data Structures','For duplicate detection over a small value range, use a','Hash/direct-address table','Binary tree only','Linear queue','Linked list'],
['Networking','A router works at the OSI','Network layer','Data-link layer','Physical layer','Transport layer'],
['Trees','Which count can form a full binary tree?','15','8','14','None'],
['AVL Trees','Rebalancing is needed when balance factor is','>1 or <−1','>1 only','Between 0 and 1','<−1 only'],
['Heaps','In a max-heap','Each parent is at least as large as its children','BST left/right ordering applies','Both heap and BST ordering apply','No ordering applies'],
['Trees','Structurally distinct binary trees with 3 nodes number','5','14','9','2'],
['Expressions','Prefix of postfix AB+C*EF-+ is','+ * + A B C − E F','* + + A B C − E F','+ * − + A B C E F','+ * + A B C − F E'],
['Error Control','Parity bits are used for','Error detection and, in suitable codes, correction','Overloading','Mobile transmission','Pattern matching'],
['Expressions','Infix of postfix ABCDE+*−/ is','A / [B − C*(D+E)]','(A+B*C−D)/E','A/B − C*D + E','A+B − C*E']
];
const p3Unit=t=>/Artificial|Logic Programming|Data Mining/i.test(t)?10:/Network|Protocol|Communicat|Coding|Line Coding|Error Control/i.test(t)?9:/Formal|Automata|Turing|Compiler|Parsing|SDT|Intermediate/i.test(t)?8:/Algorithm|Complexity|Optimization|Operations Research|Data Structure|Trees|AVL|Heaps|Expressions/i.test(t)?7:/Software|Testing|Metrics|UML/i.test(t)?6:/Operating|UNIX|Memory|Virtual/i.test(t)?5:/DBMS|SQL|ER Model|Relational|Warehouse|Database/i.test(t)?4:/C\+\+|Web|CSS|Windows|Graphics/i.test(t)?3:/Architecture|Cache|I\/O|Microprocessor/i.test(t)?2:1;
const PAPER_THREE_QUESTIONS=P3_RAW.map((row,index)=>{const [t,q,correct,...wrong]=row;const pos=(index*3+1)%4,o=[...wrong];o.splice(pos,0,correct);const item={s:'',t,q,o,a:pos,e:`Correct answer: ${correct}.`,mode:'selection',level:index<25?'Level 1':index<50?'Level 2':'Level 3'};item.s=`Set 4 • ${item.level} • Paper III PYQ • ${t}`;item.unit=syllabusUnitFor(item)||p3Unit(t);item.unitName=UGC_NET_UNITS[item.unit];item.s+=` • Unit ${item.unit}`;return item});
const SET_FOUR_PRIOR_TEXTS=new Set([...SET_ONE_QUESTIONS,...SET_TWO_QUESTIONS,...SET_THREE_QUESTIONS,...PAPER_THREE_QUESTIONS].map(item=>item.q));
const SET_FOUR_SOURCE_POOL=RAW_TEXTBOOK_BANK.filter(item=>!SET_FOUR_PRIOR_TEXTS.has(item.q));
const SET_FOUR_EXTENSIONS=Array.from({length:25},(_,index)=>{
  const source=SET_FOUR_SOURCE_POOL[index]||RAW_TEXTBOOK_BANK[index%RAW_TEXTBOOK_BANK.length];
  const item={...source,o:[...source.o]};
  item.q=`Set 4 advanced syllabus application ${index+1}: ${source.q}`;
  item.level=index<9?'Level 1':index<17?'Level 2':'Level 3';
  item.mode='selection';
  item.passage=source.passage;
  const target=(index+2)%4;
  if(item.a!==target){[item.o[item.a],item.o[target]]=[item.o[target],item.o[item.a]];item.a=target}
  item.s=`Set 4 • ${item.level} • Unique Textbook Extension • ${item.t}`;
  item.unit=syllabusUnitFor(item)||p3Unit(item.t);
  item.unitName=UGC_NET_UNITS[item.unit];
  item.s+=` • Unit ${item.unit}`;
  return item;
});
const SET_FOUR_QUESTIONS=[...PAPER_THREE_QUESTIONS,...SET_FOUR_EXTENSIONS];
QUESTION_SETS[4]=SET_FOUR_QUESTIONS;
