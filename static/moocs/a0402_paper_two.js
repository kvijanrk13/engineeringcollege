/* A-04-02 Computer Science and Applications Paper II, transcribed from supplied PDF. */
const A04=[
['Software Engineering','Coupling and cohesion can be represented using a','Structure chart','Cause-effect graph','Dependence matrix','Bar graph'],
['Security','The property that no contract party can later deny signing is','Non-repudiation','Denial of service','Masquerading','Repudiation'],
['Wireless Communication','High carrier frequency is used for wireless modulation chiefly because of','Antenna requirements and multiplexing multiple channels/users','Mobile requirements only','Beam bending','Eliminating bandwidth'],
['DBMS','Entity integrity specifies that','A primary-key value cannot be null','A primary key may be null','Every foreign key is null','A superkey is null'],
['DBMS','Functional dependencies generalize','Key dependencies','Relation names','Database files','None'],
['UNIX','Octal permission 634 represents','rw- -wx r--','-wx r-x -w-','--x r-- -w-','rwx rwx rwx'],
['C Programming','A static var starts at 5; print var-- and recurse while var is nonzero. Output is','5 4 3 2 1','4 3 2 1 0','1 2 3 4 5','3 2 1 0 0'],
['Graph Theory','For the booklet’s directed graph, which stated combination of degree assertions holds?','Both assertions I and II','Only assertion I','Only assertion II','Neither assertion'],
['Combinatorics','How many 5-digit multiples of 5 use distinct digits from 0,1,2,3,4,5?','216','196','144','300'],
['Probability','The probability that 12 randomly chosen people have birthdays in 12 different months is','12!/12^12','11!/12^11','12/12^12','11/12'],
['Automata','Which expression corresponds to the booklet’s three-state automaton?','(0 + 1(1+01)*00)*','0 + (1+01)*','(11+01*)(1*+0*)*','(0*0+11*)*'],
['Coding Theory','A code with minimum distance 7 can correct','3 errors','4 errors','5 errors','6 errors'],
['Operating Systems','Correctly match thread, address space, file system, signal with hardware.','CPU, memory, disk, interrupt','Interrupt, memory, CPU, disk','CPU, disk, memory, interrupt','CPU, interrupt, memory, disk'],
['Networking','Typical optical-fibre bandwidth is on the order of','GHz','kHz','Hz','MHz'],
['Computer Arithmetic','In 4-bit two’s complement, 0011 − 1010 is','1001','0111','-0111','-1001'],
['Data Communications','Baud measures','Symbol rate','Memory capacity','Instruction time','Process wait time'],
['TCP','With MSS 1 KB and congestion window 256 KB, timeout sets cwnd and threshold to','1 KB and 128 KB','1024 KB and 256 KB','1 KB and 256 KB','1024 KB and 128 KB'],
['File Organization','Direct files are stored on','Direct-access storage','Sequential storage only','Magnetic tape only','Primary memory only'],
['Algorithms','Worst-case comparisons for linear and binary search are proportional to','n and log n','log n and n','n² and n','n and n'],
['Trees','An approximately balanced full binary tree with N internal nodes has height','About log₂ N','About log₃ N','About N/2','Always N'],
['Linking and Loading','Relocation primarily','Adds a constant to relative addresses','Performs lexical analysis','Schedules processes','Translates simultaneously'],
['Memory Management','Compaction is used with','Contiguous memory allocation','Paging','Disk fragmentation','Caching'],
['Assembly Language','Assembly is low-level because it is','Close to machine language','Not machine language','Always easy','Only decimal'],
['IP','Which IP class is multicast?','Class D','Class C','Class B','Class A'],
['Networking','RARP is used to','Find IP from a hardware address','Find hardware address from IP','Find address class','Find multicast address'],
['IP','Classify 141.14.25.78.','Class B; netid 141.14; hostid 25.78','Class C; netid 141.14.25','Class A; netid 141','Class D'],
['Process Models','Requirements implemented by category/increments characterize','Evolutionary development','Waterfall','Throwaway prototype only','Big bang'],
['Software Quality','Which is not normally a direct software-quality determinant?','Customer characteristics alone','Business conditions','Software characteristics','Development environment'],
['Software Process','CMM maturity levels are','Initial, repeatable, defined, managed, optimizing','Primary, secondary, defined, managed, optimizing','Initial, stating, defined, managed, optimizing','Primary, secondary, stating, managed, optimizing'],
['Security','A digital signature is based on an','Encrypted message digest','Digitized handwriting','Compression procedure','Unkeyed checksum'],
['C File Handling','fseek(ptr,0,SEEK_CUR) does what?','Keeps the current position','Moves to beginning','Moves to end','Moves to middle'],
['C Programming','Combine char *p and malloc(100) correctly.','char *p = (char*) malloc(100);','char p = *malloc(100);','char *p = (char) malloc(100);','char *p = (char*)(malloc*)(100);'],
['SQL','For varchar(20) Avi and char(20) Reed, stored lengths are','3 and 20','20 and 4','20 and 20','3 and 4'],
['OLAP','ROLAP is','OLAP using multidimensional models with relational SQL','Only an array without SQL','Unable to slice/dice','A single relational operator'],
['Broadcast Systems','Digital audio/video broadcasting uses','A broadcast-disk delivery model','No broadcast model','Only local disks','A CPU queue'],
['SQL','SELECT SAL+NVL(COMM,0) FROM EMP returns','Salary plus commission, null treated as zero','Only table total','A permanent update','Only null salaries'],
['SQL','TRUNC(1234.5678,-2) returns','1200','1234.56','1234.00','1234.57'],
['Data Representation','One megabyte equals','2^23 bits','2^20 bits','2^10 bits','2^40 bits'],
['Java','For X=20, (X<15)?small:(X<22)?tiny:huge produces','tiny','small','huge','all three'],
['C Programming','With 4-byte int/float and 1-byte char, their union size is','4 bytes','8 bytes','7 bytes','5 bytes'],
['UNIX','Which pipeline counts logged-in users?','who | wc -l','who | ls -l','ls -l | who','cat example.c | who'],
['UNIX','Sort file lines in reverse order with','sort -r','sort','sh','sh -r'],
['Storage','Disk-head movement to the required cylinder takes','Seek time','Rotational latency','Response time','Waiting time'],
['Scheduling','Which minimizes average waiting for known CPU bursts?','Shortest-job-first','FCFS','Round robin','Priority'],
['Scheduling','Admission of jobs into the system is done by','Long-term scheduler','Short-term scheduler','Medium-term scheduler','Queue alone'],
['Loader','A loader performs','Memory allocation and reference resolution','Lexical analysis','Compiler symbol-table creation','Intermediate-code construction'],
['C++','Which default-access statement is correct?','Class is private; struct is public','Struct cannot have functions','Class is public; struct private','Pointers cannot be declared'],
['Data Structures','Which is self-referential?','Linked list','Array','Integer','Float'],
['Queues','Circular-queue element count is','(rear-front+n) mod n','rear-front','rear-front+1','(rear-front) without normalization'],
['OSI Model','Which layer changes bits into electromagnetic signals?','Physical','Data-link','Transport','Presentation']
];
const a04unit=t=>/Graph|Combinator|Probability/i.test(t)?1:/Arithmetic/i.test(t)?2:/C Programming|C\+\+|Java/i.test(t)?3:/DBMS|SQL|OLAP/i.test(t)?4:/Operating|UNIX|Memory|File|Storage|Scheduling|Linking|Loader|Assembly/i.test(t)?5:/Software|Process Model/i.test(t)?6:/Algorithm|Trees|Data Structures|Queues/i.test(t)?7:/Automata|Coding Theory/i.test(t)?8:/Security|Network|Wireless|Communication|TCP|IP|OSI|Broadcast/i.test(t)?9:10;
const A0402_PYQ=A04.map((r,i)=>{const[t,q,c,...w]=r,p=(i*3+1)%4,o=[...w];o.splice(p,0,c);const level=i<17?'Level 1':i<34?'Level 2':'Level 3',unit=a04unit(t);return{s:`Set 5 • ${level} • A-04-02 Paper II PYQ • ${t} • Unit ${unit}`,t,q,o,a:p,e:`Correct answer: ${c}.`,mode:'selection',level,unit,unitName:UGC_NET_UNITS[unit]}});
const SET_FIVE_PRIOR_TEXTS=new Set([...QUESTION_SETS[1],...QUESTION_SETS[2],...QUESTION_SETS[3],...QUESTION_SETS[4],...A0402_PYQ].map(item=>item.q));
const SET_FIVE_SOURCE_POOL=RAW_TEXTBOOK_BANK.filter(item=>!SET_FIVE_PRIOR_TEXTS.has(item.q));
const SET_FIVE_EXTENSIONS=Array.from({length:50},(_,index)=>{
  const source=SET_FIVE_SOURCE_POOL[index]||RAW_TEXTBOOK_BANK[(index+50)%RAW_TEXTBOOK_BANK.length];
  const item={...source,o:[...source.o]};
  item.q=`Set 5 advanced non-repeated syllabus problem ${index+1}: ${source.q}`;
  item.level=index<17?'Level 1':index<33?'Level 2':'Level 3';
  item.mode='selection';
  const target=(index+3)%4;
  if(item.a!==target){[item.o[item.a],item.o[target]]=[item.o[target],item.o[item.a]];item.a=target}
  item.s=`Set 5 • ${item.level} • Unique Syllabus Extension • ${item.t}`;
  item.unit=syllabusUnitFor(item)||a04unit(item.t);
  item.unitName=UGC_NET_UNITS[item.unit];
  item.s+=` • Unit ${item.unit}`;
  return item;
});
const SET_FIVE_QUESTIONS=[...A0402_PYQ,...SET_FIVE_EXTENSIONS];
QUESTION_SETS[5]=SET_FIVE_QUESTIONS;
