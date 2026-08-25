const Q=(s,t,q,o,a,e)=>({s,t,q,o,a,e});
const QUESTIONS=[
Q('Architecture 01','Digital Logic','Which gate outputs 1 only when all its inputs are 1?',['OR','AND','XOR','NOR'],1,'An AND gate asserts its output only when every input is asserted.'),
Q('Architecture 02','Boolean Algebra','The complement of A+B is:',['A′+B′','A′B′','AB','A+B′'],1,'De Morgan’s law gives (A+B)′=A′B′.'),
Q('Architecture 03','Combinational Circuits','A decoder with n inputs can select at most:',['n outputs','2n outputs','2ⁿ outputs','n² outputs'],2,'An n-to-2ⁿ decoder generates one output for each binary input combination.'),
Q('Architecture 04','Combinational Circuits','A multiplexer primarily performs:',['One-to-many routing','Many-to-one selection','Binary counting','Data storage'],1,'A multiplexer selects one of several inputs and forwards it to one output.'),
Q('Architecture 05','Sequential Logic','Which flip-flop toggles when both inputs are 1?',['SR','JK','D','Master reset'],1,'The JK flip-flop resolves the SR invalid case by toggling for J=K=1.'),
Q('Architecture 06','Registers','A 4-bit register can store:',['One bit','Four bits','Eight bits','Sixteen bytes'],1,'A register contains one flip-flop per stored bit.'),
Q('Architecture 07','Counters','A mod-16 binary counter requires how many flip-flops?',['2','3','4','16'],2,'Four flip-flops represent 2⁴=16 distinct states.'),
Q('Architecture 08','Number Systems','The hexadecimal equivalent of binary 1110 is:',['C','D','E','F'],2,'1110₂ equals decimal 14, represented by E in hexadecimal.'),
Q('Architecture 09','Data Representation','Two’s complement of 00101100 is:',['11010011','11010100','10101100','00110100'],1,'Invert 00101100 to 11010011 and add one to obtain 11010100.'),
Q('Architecture 10','Computer Arithmetic','Overflow in signed two’s-complement addition occurs when:',['Operands have different signs','Same-sign operands produce an opposite-sign result','A carry enters bit zero','The result is zero'],1,'Adding equal-sign operands should preserve their sign; a changed result sign signals overflow.'),
Q('Architecture 11','Floating Point','The exponent field in floating-point representation mainly determines:',['Precision only','Magnitude range','Sign of mantissa','Parity'],1,'The exponent scales the significand and therefore controls representable magnitude.'),
Q('Architecture 12','Error Detection','A parity bit can always detect:',['Any two-bit error','Any odd number of bit errors','Burst errors of every length','All substitutions'],1,'Odd parity changes flip the computed parity; an even number may cancel.'),
Q('Architecture 13','Register Transfer','RTL is used to describe:',['Physical transistor layout','Microoperations and data transfers among registers','Only machine opcodes','Network packets'],1,'Register Transfer Language specifies register-level transfers and operations.'),
Q('Architecture 14','Bus Organization','A common bus reduces hardware by:',['Giving every register a private memory','Sharing transfer paths among registers','Removing control signals','Eliminating registers'],1,'Multiple sources and destinations reuse a controlled set of shared lines.'),
Q('Architecture 15','Microoperations','A logical shift right inserts which value into the vacated MSB?',['Previous LSB','Sign bit','Zero','One always'],2,'A logical shift fills vacated positions with zero.'),
Q('Architecture 16','Microoperations','An arithmetic right shift preserves:',['Parity bit','Sign bit','Carry flag only','Opcode'],1,'Sign extension copies the most significant sign bit into the new position.'),
Q('Architecture 17','Basic Computer','The program counter normally contains:',['Current operand','Address of the next instruction','ALU result','Interrupt mask only'],1,'The PC directs instruction fetch to the next instruction address.'),
Q('Architecture 18','Instruction Cycle','The first major phase of an instruction cycle is:',['Execute','Fetch','Interrupt','Write back only'],1,'The processor first fetches an instruction from memory using the PC.'),
Q('Architecture 19','Instruction Format','An opcode identifies:',['Where the program is stored','The operation to perform','Only the operand size','The clock frequency'],1,'The opcode selects the instruction operation implemented by control logic.'),
Q('Architecture 20','Addressing Modes','Immediate addressing obtains the operand from:',['The instruction itself','A memory pointer','The stack top only','The interrupt vector'],0,'The literal operand is encoded directly in the instruction.'),
Q('Architecture 21','Addressing Modes','Effective address in indexed addressing is usually:',['Index register only','Address field plus index register','PC minus opcode','Stack pointer plus zero'],1,'Indexing adds an index-register displacement to the instruction address field.'),
Q('Architecture 22','Interrupts','An interrupt causes the processor to:',['Erase main memory','Temporarily suspend normal execution and service an event','Disable all I/O permanently','Restart every program'],1,'Control transfers to an interrupt service routine after saving required state.'),
Q('Architecture 23','Assembly Language','An assembler translates:',['Assembly language into machine code','Machine code into C','High-level code into English','Data into addresses only'],0,'An assembler resolves mnemonics, symbols, and directives into object code.'),
Q('Architecture 24','Subroutines','A return address is commonly saved so that:',['The ALU can divide','Execution resumes after the call','Memory can refresh','The opcode can change'],1,'The return address identifies the instruction following the subroutine call.'),
Q('Architecture 25','Microprogrammed Control','Control memory stores:',['User documents','Microinstructions','Only operands','Cache tags'],1,'Microinstructions encode control signals and sequencing for machine instructions.'),
Q('Architecture 26','Control Unit','A hardwired control unit is generally:',['Slower and easier to modify','Faster but less flexible','Stored on disk','Independent of opcode'],1,'Fixed logic responds quickly but is harder to redesign than microcode.'),
Q('Architecture 27','CPU Organization','A stack-organized CPU commonly uses which implicit operands?',['Top stack elements','Disk blocks','Cache tags','Interrupt vectors'],0,'Stack instructions operate on values at the top of the stack.'),
Q('Architecture 28','Instruction Sets','RISC designs typically emphasize:',['Many complex variable-length operations','Simple instructions and regular formats','No registers','Microcode only'],1,'RISC favors simple, often fixed-length instructions suited to pipelining.'),
Q('Architecture 29','Instruction Sets','CISC architecture typically provides:',['Only load/store operations','A large set of complex instructions','No addressing modes','One register'],1,'CISC exposes richer instructions and addressing forms to software.'),
Q('Architecture 30','Pipelining','Pipelining improves primarily:',['Single-instruction latency always','Instruction throughput','Memory capacity','Numerical precision'],1,'Overlapping stages increases the number of completed instructions per unit time.'),
Q('Architecture 31','Pipeline Hazards','A read-after-write dependency creates a:',['Control hazard','Data hazard','Structural reset','Parity hazard'],1,'The consumer needs a result that an earlier instruction has not yet produced.'),
Q('Architecture 32','Pipeline Hazards','A conditional branch mainly produces a:',['Data hazard','Control hazard','Memory leak','Bus arbitration error'],1,'The next fetch address is uncertain until the branch decision is known.'),
Q('Architecture 33','Vector Processing','A vector instruction operates on:',['One bit only','An ordered collection of data elements','Only addresses','Microcode words'],1,'Vector processors apply one operation across many elements.'),
Q('Architecture 34','I/O Organization','DMA transfers data between I/O and memory with:',['CPU handling every word','Minimal CPU intervention','No controller','Only programmed I/O'],1,'A DMA controller performs bulk transfers after CPU setup.'),
Q('Architecture 35','I/O Organization','Polling requires the CPU to:',['Repeatedly test device status','Wait for a power failure','Execute DMA only','Ignore the device'],0,'Programmed polling repeatedly reads a status flag until the device is ready.'),
Q('Architecture 36','Interrupt Priority','Daisy chaining establishes priority using:',['A serial grant path','Virtual memory','Round-robin software only','A parity tree'],0,'The interrupt acknowledge propagates through devices in fixed priority order.'),
Q('Architecture 37','Asynchronous Transfer','A handshake protocol coordinates transfer using:',['Request and acknowledge signals','A shared clock only','Cache misses','Opcode bits'],0,'Request/acknowledge signals permit reliable timing without a common clock.'),
Q('Architecture 38','Memory Hierarchy','The fastest storage in a typical hierarchy is:',['Magnetic disk','CPU registers','Main memory','Optical media'],1,'Registers are located in the processor datapath and have the lowest access latency.'),
Q('Architecture 39','Cache Memory','A cache hit means:',['Requested block is in cache','Cache is full','Memory has failed','The address is invalid'],0,'A hit lets the processor obtain the requested item from cache.'),
Q('Architecture 40','Cache Mapping','Direct mapping places a main-memory block in:',['Any cache line','Exactly one cache line','Two arbitrary lines','No cache line'],1,'The block index determines one permitted cache location.'),
Q('Architecture 41','Cache Mapping','Fully associative cache lookup compares a tag against:',['One fixed line','All cache lines','Only main memory','The disk directory'],1,'A block may occupy any line, so tags are searched associatively.'),
Q('Architecture 42','Virtual Memory','A page fault indicates that the referenced page is:',['Already in a register','Not resident in main memory','Read-only','In the TLB'],1,'The OS must bring the nonresident page from secondary storage.'),
Q('Architecture 43','Virtual Memory','The TLB caches:',['Instructions only','Recent page-table translations','Disk sectors','I/O interrupts'],1,'A translation lookaside buffer speeds virtual-to-physical address translation.'),
Q('Architecture 44','Memory Devices','RAM is described as volatile because it:',['Cannot be written','Loses contents without power','Is slower than disk','Stores only programs'],1,'Ordinary RAM requires power to retain stored state.'),
Q('Architecture 45','Associative Memory','Content-addressable memory is accessed by:',['Physical row number only','Matching stored content','Program counter only','Disk cylinder'],1,'Associative memory searches for a word by comparing its content in parallel.'),
Q('Architecture 46','Multiprocessors','Cache coherence protocols maintain:',['Identical clock rates','A consistent view of shared data','One cache total','No shared memory'],1,'They coordinate copies of shared blocks held in different processor caches.'),
Q('Architecture 47','Multiprocessors','A bus arbitration mechanism decides:',['Which requester controls the bus','Which opcode is legal','How data is compressed','The page size'],0,'Arbitration resolves simultaneous requests for a shared interconnect.'),
Q('Architecture 48','Parallel Processing','Speedup with p processors is defined as:',['Tp/T1','T1/Tp','T1+Tp','p/T1'],1,'Speedup compares sequential execution time T1 with parallel time Tp.'),
Q('Architecture 49','Parallel Processing','Amdahl’s law limits speedup because of the program’s:',['Parallel portion','Serial fraction','Register count','Cache associativity'],1,'The portion that cannot be parallelized becomes the ultimate bottleneck.'),
Q('Architecture 50','Synchronization','An atomic test-and-set instruction can implement a:',['Floating-point adder','Mutual-exclusion lock','Cache replacement','Decoder'],1,'Atomic read-modify-write permits safe lock acquisition among processors.'),
Q('Data Mining 01','Foundations','Data mining is primarily the process of:',['Storing every record','Discovering useful patterns from data','Encrypting files','Deleting redundancy only'],1,'Mining extracts valid, novel, useful, and understandable patterns.'),
Q('Data Mining 02','Data Types','A nominal attribute has values that are:',['Ordered quantities','Categories without intrinsic order','Always continuous','Binary only'],1,'Nominal values label categories and do not define rank or distance.'),
Q('Data Mining 03','Statistics','Which measure is least affected by extreme outliers?',['Mean','Median','Variance','Range'],1,'The median depends on order rather than magnitude of extreme values.'),
Q('Data Mining 04','Similarity','Cosine similarity compares vectors using their:',['Euclidean sum','Angle','Minimum component','Variance only'],1,'It is the normalized dot product and reflects directional alignment.'),
Q('Data Mining 05','Preprocessing','Replacing missing values with an estimated value is called:',['Sampling','Imputation','Pruning','Indexing'],1,'Imputation supplies plausible substitutes using constants or model-based estimates.'),
Q('Data Mining 06','Preprocessing','Min-max normalization typically maps values into:',['A chosen bounded interval','Integers only','A random order','Missing values'],0,'It linearly rescales values using the observed minimum and maximum.'),
Q('Data Mining 07','Preprocessing','Principal component analysis is mainly used for:',['Dimensionality reduction','Rule generation','Database locking','Web crawling'],0,'PCA projects correlated attributes onto fewer orthogonal components.'),
Q('Data Mining 08','Preprocessing','Binning can reduce noise by:',['Sorting and smoothing nearby values','Adding random columns','Duplicating tuples','Encrypting attributes'],0,'Values are grouped into bins and replaced or smoothed using bin statistics.'),
Q('Data Mining 09','Data Warehousing','A data warehouse is characteristically:',['Volatile and transaction-oriented','Subject-oriented and time-variant','Unintegrated','Write-only'],1,'Warehouses integrate historical data organized around analysis subjects.'),
Q('Data Mining 10','OLAP','Roll-up performs:',['Aggregation to a higher concept level','Detail expansion','Tuple deletion','Model training'],0,'Roll-up summarizes along a hierarchy or removes a dimension.'),
Q('Data Mining 11','OLAP','Drill-down is the inverse of:',['Slice','Roll-up','Pivot','Join'],1,'Drill-down moves from summarized values toward more detailed levels.'),
Q('Data Mining 12','Warehouse Schema','In a star schema, dimension tables connect directly to:',['Other dimensions only','A central fact table','A compiler','An FP-tree'],1,'The fact table holds measures and foreign keys to denormalized dimensions.'),
Q('Data Mining 13','Data Cubes','An iceberg cube stores cells that:',['Have zero dimensions','Meet a minimum aggregate threshold','Are encrypted','Contain only strings'],1,'Iceberg conditions retain only sufficiently significant aggregate cells.'),
Q('Data Mining 14','Data Cubes','BUC computes an iceberg cube primarily in which direction?',['Apex downward','Base upward only','Left to right','Randomly'],0,'Bottom-Up Computation recursively explores cuboids from the apex downward.'),
Q('Data Mining 15','Frequent Patterns','Support of itemset X is the:',['Fraction of transactions containing X','Number of items in X','Confidence of X→Y','Database size'],0,'Support measures how often an itemset occurs in the transaction database.'),
Q('Data Mining 16','Association Rules','Confidence of X→Y equals:',['support(Y)/support(X)','support(X∪Y)/support(X)','support(X)/support(Y)','support(X∩Y)²'],1,'Confidence estimates the conditional probability of Y given X.'),
Q('Data Mining 17','Apriori','The Apriori property states that:',['Every subset of a frequent itemset is frequent','Every superset is frequent','Support rises with size','No pruning is possible'],0,'Downward closure allows candidates with an infrequent subset to be pruned.'),
Q('Data Mining 18','FP-Growth','FP-growth avoids expensive:',['Tree construction','Candidate itemset generation','Support counting','Database input'],1,'It compresses transactions into an FP-tree and mines conditional patterns.'),
Q('Data Mining 19','Pattern Evaluation','Lift greater than 1 suggests X and Y are:',['Negatively correlated','Positively associated','Independent','Mutually exclusive'],1,'Observed co-occurrence exceeds that expected under independence.'),
Q('Data Mining 20','Closed Patterns','A frequent itemset is closed when no proper superset has:',['The same support','Higher confidence','Fewer items','Any transaction'],0,'Closed itemsets compactly preserve support information.'),
Q('Data Mining 21','Classification','Classification predicts:',['A categorical class label','Only a distance','A database key','A cluster count'],0,'A classifier maps an object to one of predefined categories.'),
Q('Data Mining 22','Decision Trees','Information gain is based on reduction in:',['Entropy','Support','Euclidean distance','Disk space'],0,'It favors splits that most reduce class impurity measured by entropy.'),
Q('Data Mining 23','Decision Trees','Tree pruning is used mainly to:',['Increase overfitting','Improve generalization','Add every attribute','Remove training data'],1,'Removing weak branches reduces variance and overfitting.'),
Q('Data Mining 24','Naive Bayes','Naive Bayes assumes attributes are conditionally independent given:',['The record ID','The class','The sample size','The mean'],1,'The simplifying conditional-independence assumption enables factorized likelihoods.'),
Q('Data Mining 25','Evaluation','In k-fold cross-validation, each fold is used once as:',['The test set','A duplicate set','A class label','A cluster center'],0,'Models train on k−1 folds and evaluate on the held-out fold.'),
Q('Data Mining 26','Evaluation','Precision equals:',['TP/(TP+FP)','TP/(TP+FN)','TN/(TN+FP)','(TP+TN)/N'],0,'Precision is the fraction of predicted positives that are truly positive.'),
Q('Data Mining 27','Evaluation','Recall equals:',['TP/(TP+FP)','TP/(TP+FN)','FP/(FP+TN)','TN/N'],1,'Recall measures the fraction of actual positives correctly retrieved.'),
Q('Data Mining 28','Ensembles','Bagging combines models trained on:',['Identical fixed records only','Bootstrap samples','No labels','One feature'],1,'Bootstrap aggregation reduces variance by averaging diverse fitted models.'),
Q('Data Mining 29','Ensembles','AdaBoost increases weights for examples that are:',['Correctly classified','Misclassified','Unlabeled','Duplicated only'],1,'Later weak learners focus more strongly on prior mistakes.'),
Q('Data Mining 30','Random Forests','Random forests add diversity by sampling records and:',['Deleting trees','Randomly selecting feature subsets','Using one fixed split','Avoiding voting'],1,'Bootstrap samples and random feature selection decorrelate the trees.'),
Q('Data Mining 31','Support Vector Machines','An SVM seeks a separating hyperplane with:',['Minimum support','Maximum margin','Maximum depth','Minimum records'],1,'Maximizing the margin generally improves robustness and generalization.'),
Q('Data Mining 32','k-NN','k-nearest-neighbor is called lazy because it:',['Never predicts','Defers model computation until a query arrives','Uses no data','Always sleeps'],1,'It stores examples and performs most work during prediction.'),
Q('Data Mining 33','Neural Networks','Backpropagation computes gradients using:',['The chain rule','Apriori pruning','Breadth-first search','OLAP roll-up'],0,'Derivatives propagate backward through composed network operations.'),
Q('Data Mining 34','Clustering','Clustering groups objects to obtain:',['High within-cluster similarity','Random membership','Known class labels only','Maximum missing data'],0,'Good clusters are cohesive internally and separated from one another.'),
Q('Data Mining 35','k-Means','A k-means cluster center is the:',['Medoid object','Mean of assigned points','Farthest point','First record'],1,'Each iteration replaces a centroid by the arithmetic mean of its members.'),
Q('Data Mining 36','k-Means','The k-means objective minimizes:',['Within-cluster squared error','Number of records','All pair distances globally','Class entropy only'],0,'It minimizes the sum of squared distances from points to assigned centroids.'),
Q('Data Mining 37','k-Medoids','Unlike k-means, a k-medoids representative is:',['Always the mean','An actual data object','A class probability','A cube cell'],1,'Medoids are observed objects, making the method more robust to outliers.'),
Q('Data Mining 38','Hierarchical Clustering','Agglomerative clustering begins with:',['One cluster containing all points','Each point as its own cluster','No clusters','Known class labels'],1,'It repeatedly merges the closest clusters from singleton initialization.'),
Q('Data Mining 39','DBSCAN','A DBSCAN core point has:',['Enough neighbors within ε','The largest coordinate','A known label','Zero distance to all points'],0,'Core points meet the MinPts density threshold inside the ε-neighborhood.'),
Q('Data Mining 40','DBSCAN','A major advantage of DBSCAN is its ability to find:',['Only spherical clusters','Arbitrarily shaped clusters and noise','Exactly two clusters','Supervised labels'],1,'Density connectivity captures irregular shapes while leaving sparse points as noise.'),
Q('Data Mining 41','BIRCH','BIRCH summarizes clusters using a:',['Clustering feature tree','Decision stump','Page table','Hash join'],0,'A CF-tree compactly stores count, linear sum, and squared sum statistics.'),
Q('Data Mining 42','Cluster Evaluation','Silhouette values near 1 indicate:',['Poor assignment','Well-separated cohesive assignment','Missing labels','Random scaling'],1,'A point is much closer to its own cluster than to the nearest alternative.'),
Q('Data Mining 43','Outliers','A contextual outlier is abnormal:',['In every situation','Only under a specific context','Only because it is missing','Only in a label'],1,'Its deviation depends on contextual attributes such as time or location.'),
Q('Data Mining 44','Outliers','Local Outlier Factor compares a point’s density with:',['Global mean only','Densities of its neighbors','Its class label','Cube dimensions'],1,'A much lower local density than neighbors yields a high LOF score.'),
Q('Data Mining 45','High Dimensions','The curse of dimensionality often makes distances:',['More discriminative','Less meaningful','Always zero','Integer-valued'],1,'In high dimensions, nearest and farthest distances tend to concentrate.'),
Q('Data Mining 46','Subspace Mining','CLIQUE is designed to discover clusters in:',['All dimensions only','Subspaces of high-dimensional data','Labeled sequences only','One numeric field'],1,'CLIQUE uses dense units to identify clusters in relevant dimension subsets.'),
Q('Data Mining 47','Sequence Mining','A sequential pattern preserves:',['Only item frequency','Order of events','Class labels only','Database schema'],1,'Sequence mining searches for frequent ordered subsequences.'),
Q('Data Mining 48','Graph Mining','A frequent subgraph is a graph pattern that:',['Occurs above a support threshold','Has no edges','Is always complete','Contains all vertices'],0,'Frequency is defined across graph transactions or embeddings.'),
Q('Data Mining 49','Privacy','Data anonymization aims to:',['Increase identification','Reduce disclosure risk while retaining utility','Delete every attribute','Guarantee perfect prediction'],1,'Anonymization limits re-identification while preserving useful analytical structure.'),
Q('Data Mining 50','Applications','A recommender system commonly estimates:',['User preference for items','CPU clock frequency','Page-table entries','Compiler tokens'],0,'Recommendation models rank items according to predicted relevance or preference.')
];

Object.assign(QUESTIONS[0],{img:'/static/moocs/diagrams/logic-gates.svg',alt:'AND and OR logic gate truth-flow diagram'});
Object.assign(QUESTIONS[3],{img:'/static/moocs/diagrams/multiplexer.svg',alt:'Four input multiplexer with select lines and one output'});
Object.assign(QUESTIONS[12],{img:'/static/moocs/diagrams/register-transfer.svg',alt:'Register transfer through a common system bus'});
Object.assign(QUESTIONS[17],{img:'/static/moocs/diagrams/instruction-cycle.svg',alt:'Fetch decode execute and interrupt instruction cycle'});
Object.assign(QUESTIONS[29],{img:'/static/moocs/diagrams/pipeline.svg',alt:'Overlapped instruction pipeline timing diagram'});
Object.assign(QUESTIONS[33],{img:'/static/moocs/diagrams/dma.svg',alt:'DMA controller path between input output device and main memory'});
Object.assign(QUESTIONS[38],{img:'/static/moocs/diagrams/cache.svg',alt:'CPU cache and main memory hierarchy diagram'});
Object.assign(QUESTIONS[45],{img:'/static/moocs/diagrams/multiprocessor.svg',alt:'Shared-memory multiprocessor with private caches'});

const DATA_STRUCTURE_QUESTIONS=[
Q('Data Structures 1','Abstract Data Types','An abstract data type is defined primarily by:',['Its memory address','Its operations and behavior','A specific programming language','Its file extension'],1,'An ADT specifies values and permitted operations independently of implementation.'),
Q('Data Structures 2','Algorithm Analysis','Binary search on a sorted array has worst-case time:',['O(1)','O(n)','O(log n)','O(n²)'],2,'Each comparison halves the remaining search interval.'),
Q('Data Structures 3','Recursion','Every correct recursive algorithm requires:',['A base case','A queue','Two loops','A hash function'],0,'The base case stops further recursive calls.'),
Q('Data Structures 4','Stacks','Which order characterizes a stack?',['FIFO','Random order','Priority order','LIFO'],3,'A stack removes the most recently pushed item first.'),
Q('Data Structures 5','Stacks','Postfix expression evaluation primarily uses a:',['Stack','Graph','B-tree','Circular queue'],0,'Operands are pushed and operators combine values from the stack.'),
Q('Data Structures 6','Queues','A standard queue removes an item from the:',['Rear','Middle','Front','Highest index only'],2,'Enqueue occurs at the rear and dequeue occurs at the front.'),
Q('Data Structures 7','Linked Lists','A singly linked node normally contains data and:',['A link to the next node','A CPU register','A hash table','A matrix row'],0,'The link connects the node to its successor.'),
Q('Data Structures 8','Linked Lists','A circular linked list is identified because:',['Every node is null','The last node links to the first','It has no head','Nodes are stored contiguously'],1,'The final link closes the list by referring to the first node.'),
Q('Data Structures 9','Doubly Linked Lists','Compared with a singly linked list, a doubly linked list adds:',['A parent link','A previous-node link','A hash key','A stack pointer'],1,'Previous and next links support traversal in both directions.'),
Q('Data Structures 10','Trees','A node with no children is called a:',['Root','Ancestor','Leaf','Sibling'],2,'A leaf is a terminal node with degree zero.'),
Q('Data Structures 11','Binary Trees','The maximum number of nodes at level k, with root at level 0, is:',['k','2^k','2k','k²'],1,'Each level can contain twice as many nodes as the preceding level.'),
Q('Data Structures 12','Tree Traversal','Preorder traversal visits nodes in which order?',['Left, root, right','Left, right, root','Root, left, right','Right, root, left'],2,'Preorder processes the root before its subtrees.'),
Q('Data Structures 13','Binary Search Trees','Inorder traversal of a binary search tree produces keys in:',['Sorted order','Random order','Reverse insertion order','Level order'],0,'BST ordering makes left-root-right traversal sorted.'),
Q('Data Structures 14','Binary Search Trees','Searching a balanced BST is typically:',['O(n²)','O(log n)','O(2^n)','O(n!)'],1,'A balanced tree discards about half of the remaining keys at each level.'),
Q('Data Structures 15','AVL Trees','An AVL node balance factor must be:',['Only 0','Between -1 and 1','Greater than 2','Equal to tree height'],1,'AVL balance permits -1, 0, or +1.'),
Q('Data Structures 16','AVL Trees','An LL imbalance is corrected with a:',['Left rotation','Double right-left rotation','Right rotation','Heapify operation'],2,'A single right rotation repairs a left-left imbalance.'),
Q('Data Structures 17','Heaps','In a max-heap, every parent key is:',['No smaller than its children','Smaller than both children','Always equal to its children','Unrelated to its children'],0,'The max-heap order places a maximum key at the root.'),
Q('Data Structures 18','Priority Queues','An efficient implementation of a priority queue is a:',['Linked stack only','Binary heap','Adjacency matrix','Sequential file'],1,'A heap supports insertion and priority removal in logarithmic time.'),
Q('Data Structures 19','B-Trees','B-trees are especially useful for:',['Expression parsing only','Disk-based indexing','CPU instruction decoding','Image compression only'],1,'Their high branching factor reduces expensive storage accesses.'),
Q('Data Structures 20','Graphs','An undirected graph edge connects:',['An ordered pair only','Two vertices symmetrically','A vertex to itself only','Exactly three vertices'],1,'Undirected adjacency has no source-to-destination orientation.'),
Q('Data Structures 21','Graph Storage','For a sparse graph, the more space-efficient representation is usually:',['Adjacency list','Full adjacency matrix','Truth table','Binary heap array'],0,'Adjacency lists store existing edges instead of every possible pair.'),
Q('Data Structures 22','Graph Traversal','Breadth-first search uses a:',['Stack','Priority register','Queue','Binary search'],2,'The queue processes vertices level by level.'),
Q('Data Structures 23','Graph Traversal','Depth-first search is naturally implemented using:',['A queue only','A stack or recursion','A B-tree only','A cache line'],1,'The call stack or an explicit stack follows one path deeply.'),
Q('Data Structures 24','Minimum Spanning Trees','A minimum spanning tree of a connected graph with V vertices has:',['V edges','V+1 edges','V-1 edges','2V edges'],2,'Every tree connecting V vertices contains V-1 edges.'),
Q('Data Structures 25','Shortest Paths','Dijkstra’s algorithm assumes edge weights are:',['Nonnegative','All equal to zero','Negative only','Complex numbers'],0,'Its greedy finalization is valid for nonnegative weights.'),
Q('Data Structures 26','Sorting','Which sorting method is stable in its standard form?',['Heap sort','Quick sort','Insertion sort','Selection sort'],2,'Insertion sort preserves the relative order of equal keys.'),
Q('Data Structures 27','Sorting','The average time complexity of quicksort is:',['O(log n)','O(n log n)','O(n² log n)','O(1)'],1,'Balanced partitions across levels yield n log n average work.'),
Q('Data Structures 28','Sorting','Heap sort has worst-case time complexity:',['O(n log n)','O(n²)','O(log n)','O(2^n)'],0,'Heap construction and repeated logarithmic deletion remain O(n log n).'),
Q('Data Structures 29','Searching','Sequential search is appropriate when data is:',['Necessarily sorted','Unsorted or small','Stored only in a BST','Always hashed perfectly'],1,'Linear search requires no ordering or preprocessing.'),
Q('Data Structures 30','Hashing','A collision occurs when:',['A table is empty','Two keys map to the same slot','A key is deleted','The load factor is zero'],1,'Collision resolution is needed when hash addresses coincide.'),
Q('Data Structures 31','Hashing','Separate chaining resolves collisions by:',['Rejecting every collision','Keeping a list at each table slot','Sorting the entire table each time','Doubling every key'],1,'Each bucket stores all keys assigned to that hash location.'),
Q('Data Structures 32','Complexity','Two nested loops each running n times usually require:',['O(log n)','O(n)','O(n²)','O(1)'],2,'Their iteration counts multiply to n squared.'),
Q('Data Structures 33','Queues','The diagrammed circular queue reuses array space by applying:',['Modulo arithmetic','Tree rotation','Recursion only','Hash chaining'],0,'Modulo arithmetic wraps front and rear indices to the start.'),
Q('Data Structures 34','Trees','In the diagrammed BST, values smaller than a node belong in its:',['Right subtree','Parent node','Left subtree','Root only'],2,'The BST invariant places smaller keys to the left.')
];

Object.assign(DATA_STRUCTURE_QUESTIONS[3],{img:'/static/moocs/diagrams/stack.svg',alt:'LIFO stack push and pop diagram'});
Object.assign(DATA_STRUCTURE_QUESTIONS[6],{img:'/static/moocs/diagrams/linked-list.svg',alt:'Singly linked list nodes and pointers'});
Object.assign(DATA_STRUCTURE_QUESTIONS[21],{img:'/static/moocs/diagrams/graph-traversal.svg',alt:'Graph for breadth-first traversal'});
Object.assign(DATA_STRUCTURE_QUESTIONS[32],{img:'/static/moocs/diagrams/circular-queue.svg',alt:'Circular queue front and rear positions'});
Object.assign(DATA_STRUCTURE_QUESTIONS[33],{img:'/static/moocs/diagrams/bst.svg',alt:'Binary search tree with ordered keys'});

const DISCRETE_MATHEMATICS_QUESTIONS=[
Q('Discrete Mathematics 1','Propositional Logic','The negation of p AND q is logically equivalent to:',['NOT p AND NOT q','NOT p OR NOT q','p OR q','p implies q'],1,'De Morgan’s law gives NOT(p AND q) = NOT p OR NOT q.'),
Q('Discrete Mathematics 2','Propositional Logic','A proposition that is true for every truth assignment is a:',['Contradiction','Contingency','Tautology','Predicate'],2,'A tautology evaluates to true under all possible assignments.'),
Q('Discrete Mathematics 3','Implication','The implication p → q is false only when:',['p and q are true','p is false and q is true','p and q are false','p is true and q is false'],3,'An implication fails precisely when a true premise leads to a false conclusion.'),
Q('Discrete Mathematics 4','Predicate Logic','The negation of “for every x, P(x)” is:',['For every x, not P(x)','There exists x such that not P(x)','There exists x such that P(x)','P(x) is always true'],1,'Negating a universal quantifier produces an existential counterexample.'),
Q('Discrete Mathematics 5','Sets','The diagrammed shaded overlap of sets A and B represents:',['A union B','A minus B','A intersection B','The empty set'],2,'The shared region contains elements belonging to both sets.'),
Q('Discrete Mathematics 6','Sets','If a finite set has n elements, its power set contains:',['n² elements','2n elements','n! elements','2^n elements'],3,'Each element has two inclusion choices, giving 2^n subsets.'),
Q('Discrete Mathematics 7','Relations','A relation R is reflexive when:',['aRb for all distinct a,b','aRa for every a','aRb implies bRa only','aRb and bRc never occur'],1,'Reflexivity requires every element to relate to itself.'),
Q('Discrete Mathematics 8','Relations','An equivalence relation must be:',['Reflexive, symmetric, and transitive','Irreflexive and asymmetric','Only transitive','Only symmetric'],0,'These three properties characterize equivalence relations.'),
Q('Discrete Mathematics 9','Partial Orders','In the diagrammed divisibility poset, a Hasse diagram omits:',['All vertices','Loops and transitive edges','Maximal elements','Cover relations'],1,'Hasse diagrams show cover relations while suppressing loops and transitively implied edges.'),
Q('Discrete Mathematics 10','Functions','A function is injective if:',['Every codomain value is used','Distinct inputs have distinct outputs','Every input has two outputs','Domain equals codomain'],1,'Injectivity prevents two different domain elements from sharing an image.'),
Q('Discrete Mathematics 11','Functions','A bijection is a function that is:',['Only injective','Only surjective','Both injective and surjective','Neither injective nor surjective'],2,'A bijection pairs domain and codomain elements one-to-one and onto.'),
Q('Discrete Mathematics 12','Induction','Mathematical induction requires a base case and:',['An inductive step','A truth table','A graph coloring','A random example'],0,'The inductive step proves that truth for k implies truth for k+1.'),
Q('Discrete Mathematics 13','Counting','The number of permutations of n distinct objects is:',['2^n','n!','n²','n+1'],1,'There are n choices, then n-1, continuing to 1, whose product is n!.'),
Q('Discrete Mathematics 14','Counting','The number of ways to choose r objects from n without regard to order is:',['n^r','n!','n choose r','r choose n'],2,'Combinations count unordered selections and equal n!/(r!(n-r)!).'),
Q('Discrete Mathematics 15','Pigeonhole Principle','Placing 11 objects into 10 boxes guarantees that:',['Every box is occupied','Some box contains at least two objects','One box contains all objects','No box contains two objects'],1,'More objects than boxes forces at least one shared box.'),
Q('Discrete Mathematics 16','Recurrence Relations','The recurrence T(n)=T(n-1)+1 with T(1)=1 has solution:',['T(n)=n','T(n)=log n','T(n)=n²','T(n)=2^n'],0,'Repeated substitution adds one at each of n-1 steps.'),
Q('Discrete Mathematics 17','Graph Theory','The sum of all vertex degrees in an undirected graph equals:',['The number of vertices','The number of edges','Twice the number of edges','The square of the edges'],2,'The handshaking lemma counts each edge at both endpoints.'),
Q('Discrete Mathematics 18','Graph Theory','A connected graph with n vertices is a tree exactly when it has:',['n edges','n-1 edges and no cycles','n+1 edges','No leaves'],1,'A tree is minimally connected and therefore contains n-1 edges.'),
Q('Discrete Mathematics 19','Euler Paths','The diagrammed connected graph has an Euler circuit when:',['Exactly two vertices have odd degree','Every vertex has even degree','Every vertex has odd degree','It has no edges'],1,'A connected graph has an Euler circuit precisely when all degrees are even.'),
Q('Discrete Mathematics 20','Planar Graphs','For a connected planar graph, Euler’s formula is:',['V+E+F=2','V-E+F=2','V-E-F=0','E=V²'],1,'Vertices minus edges plus faces equals two.'),
Q('Discrete Mathematics 21','Graph Coloring','The chromatic number is the minimum number of:',['Edges in a path','Colors for adjacent vertices to differ','Cycles in a graph','Vertices in a tree'],1,'A proper vertex coloring assigns different colors to adjacent vertices.'),
Q('Discrete Mathematics 22','Boolean Algebra','In Boolean algebra, x + x equals:',['0','1','x','NOT x'],2,'The idempotent law states x OR x = x.'),
Q('Discrete Mathematics 23','Boolean Algebra','The diagrammed truth table shows p XOR q is true when:',['Both inputs are equal','Exactly one input is true','Both inputs are false','p is always false'],1,'Exclusive OR is true exactly when the inputs differ.'),
Q('Discrete Mathematics 24','Algebraic Structures','A group operation must satisfy closure, associativity, identity, and:',['Distributivity','An inverse for every element','Commutativity always','Idempotence'],1,'Each group element must have an inverse; commutativity is optional.'),
Q('Discrete Mathematics 25','Finite State Machines','A deterministic finite automaton has:',['Exactly one transition for each state-symbol pair','No accepting states','An infinite state set','Two mandatory start states'],0,'Determinism assigns one next state for each state and input symbol.')
];

Object.assign(DISCRETE_MATHEMATICS_QUESTIONS[4],{img:'/static/moocs/diagrams/set-intersection.svg',alt:'Venn diagram with the intersection of sets A and B shaded'});
Object.assign(DISCRETE_MATHEMATICS_QUESTIONS[8],{img:'/static/moocs/diagrams/hasse-diagram.svg',alt:'Hasse diagram for divisibility on a finite set'});
Object.assign(DISCRETE_MATHEMATICS_QUESTIONS[18],{img:'/static/moocs/diagrams/euler-graph.svg',alt:'Connected graph whose vertices have even degree'});
Object.assign(DISCRETE_MATHEMATICS_QUESTIONS[22],{img:'/static/moocs/diagrams/xor-truth-table.svg',alt:'Truth table for the exclusive OR operation'});

const DATA_COMMUNICATION_QUESTIONS=[
Q('Data Communications 1','Network Models','Which OSI layer is responsible for end-to-end process delivery?',['Data link','Transport','Physical','Presentation'],1,'The transport layer provides process-to-process delivery and reliability services.'),
Q('Data Communications 2','Network Models','The diagrammed encapsulation process adds headers as data moves:',['Up the sender stack','Down the sender stack','Only across the physical medium','Directly to the application'],1,'Each lower protocol layer encapsulates the unit received from the layer above.'),
Q('Data Communications 3','Signals','A signal completes 200 cycles in one second. Its frequency is:',['20 Hz','100 Hz','200 Hz','400 Hz'],2,'Frequency is the number of cycles per second, measured in hertz.'),
Q('Data Communications 4','Transmission','If a noiseless channel has bandwidth B and L signal levels, Nyquist bit rate is:',['B log₂L','2B log₂L','B/L','2B/L'],1,'Nyquist gives 2B log₂L bits per second for a noiseless channel.'),
Q('Data Communications 5','Transmission','Shannon capacity increases when:',['Bandwidth or signal-to-noise ratio increases','Noise power alone increases','Bandwidth becomes zero','The signal is removed'],0,'Capacity is B log₂(1+S/N), so bandwidth and SNR improve the limit.'),
Q('Data Communications 6','Line Coding','Manchester encoding represents each bit using:',['No transition','A transition in the middle of the bit interval','Only positive voltage','A separate carrier frequency'],1,'A mid-bit transition provides both data and synchronization.'),
Q('Data Communications 7','Multiplexing','Which technique assigns different frequency bands to simultaneous signals?',['TDM','FDM','CRC','ARQ'],1,'Frequency-division multiplexing separates channels in frequency.'),
Q('Data Communications 8','Switching','A datagram network routes each packet:',['Along an independently selected path','Only after a dedicated circuit is reserved','Without an address','Through one permanent physical wire'],0,'Connectionless packets carry addressing information and may follow different routes.'),
Q('Data Communications 9','Error Detection','The diagrammed CRC sender appends:',['The divisor itself','The quotient','The division remainder','The original frame length'],2,'CRC appends the modulo-2 division remainder as redundant bits.'),
Q('Data Communications 10','Data Link Control','In Stop-and-Wait ARQ, the sender retransmits when:',['A timer expires before a valid acknowledgment','Every acknowledgment arrives','The window becomes larger','The receiver sends data'],0,'Timeout indicates a lost or damaged frame or acknowledgment.'),
Q('Data Communications 11','Multiple Access','CSMA/CD was designed for:',['Traditional shared Ethernet','Circuit-switched telephony','IPv6 routing','DNS name resolution'],0,'Shared half-duplex Ethernet detects collisions while transmitting.'),
Q('Data Communications 12','Ethernet','A standard Ethernet switch primarily forwards frames using:',['IP port numbers','MAC addresses','Domain names','Process identifiers'],1,'Layer-2 switches learn and use destination MAC addresses.'),
Q('Data Communications 13','IPv4 Addressing','The diagrammed /26 IPv4 subnet contains how many total addresses?',['32','64','128','256'],1,'A /26 prefix leaves six host bits, producing 2^6 = 64 addresses.'),
Q('Data Communications 14','IPv4','Which field prevents an IPv4 datagram from circulating forever?',['Version','Header length','Time to Live','Source address'],2,'Routers decrement TTL and discard the packet when it reaches zero.'),
Q('Data Communications 15','Routing','A router chooses a forwarding entry using:',['Longest-prefix matching','Shortest MAC address','Largest port number','Alphabetical order'],0,'The most specific matching network prefix determines the route.'),
Q('Data Communications 16','Transport Layer','UDP differs from TCP because UDP:',['Requires a connection handshake','Provides byte-stream reliability','Is connectionless and has lower overhead','Uses no port numbers'],2,'UDP sends independent datagrams without connection setup or reliability machinery.'),
Q('Data Communications 17','TCP','The diagrammed TCP connection establishment sequence is:',['ACK, SYN, FIN','SYN, SYN-ACK, ACK','FIN, ACK, SYN','SYN, FIN, RST'],1,'TCP establishes synchronized sequence numbers with the three-way handshake.'),
Q('Data Communications 18','Application Layer','DNS normally maps:',['Domain names to IP addresses','MAC addresses to passwords','Frames to checksums','Ports to cables'],0,'The Domain Name System resolves names into network addresses and related records.'),
Q('Data Communications 19','Application Layer','HTTP status code 404 indicates:',['Successful request','Permanent redirect','Resource not found','Server gateway success'],2,'A 404 response means the requested resource was not found.'),
Q('Data Communications 20','Security','TLS primarily provides communication:',['Compression only','Confidentiality, integrity, and authentication','Physical addressing','Route discovery'],1,'TLS protects application traffic using authenticated cryptographic sessions.')
];

Object.assign(DATA_COMMUNICATION_QUESTIONS[1],{img:'/static/moocs/diagrams/osi-encapsulation.svg',alt:'OSI encapsulation from application data to transmitted bits'});
Object.assign(DATA_COMMUNICATION_QUESTIONS[8],{img:'/static/moocs/diagrams/crc-division.svg',alt:'CRC modulo-2 division and appended remainder'});
Object.assign(DATA_COMMUNICATION_QUESTIONS[12],{img:'/static/moocs/diagrams/ipv4-subnet.svg',alt:'IPv4 address divided into a 26-bit network prefix and 6 host bits'});
Object.assign(DATA_COMMUNICATION_QUESTIONS[16],{img:'/static/moocs/diagrams/tcp-handshake.svg',alt:'TCP three-way handshake between client and server'});

const JAVA_QUESTIONS=[
Q('Java 1','Java Platform','Java source code is normally compiled into:',['Native machine code only','Bytecode executed by the JVM','SQL statements','HTML elements'],1,'The Java compiler produces platform-neutral bytecode for a Java Virtual Machine.'),
Q('Java 2','Java Platform','In the diagrammed Java execution flow, which component loads and runs bytecode?',['Text editor','JVM','Database server','Web browser DOM'],1,'The JVM loads, verifies, and executes compiled class bytecode.'),
Q('Java 3','Data Types','Which Java primitive type stores a true or false value?',['char','int','boolean','String'],2,'boolean is the primitive logical type; String is a reference type.'),
Q('Java 4','Operators','For int x=7, the expression x%3 evaluates to:',['0','1','2','3'],1,'The remainder after dividing 7 by 3 is 1.'),
Q('Java 5','Control Flow','A break inside nested loops without a label terminates:',['All enclosing loops','Only the innermost loop','The JVM','The current method always'],1,'An unlabeled break exits the nearest enclosing loop or switch.'),
Q('Java 6','Arrays','For int[] a=new int[5], the valid final index is:',['5','4','3 only','6'],1,'Java arrays are zero-indexed, so a five-element array uses indices 0 through 4.'),
Q('Java 7','Classes','A constructor differs from an ordinary method because it:',['Must return int','Has the class name and no return type','Must be static','Cannot accept parameters'],1,'A constructor initializes a new object and has no declared return type.'),
Q('Java 8','Methods','Method overloading requires methods to differ in their:',['Return type alone','Parameter lists','Access modifier only','Exception message'],1,'Overloaded methods share a name but have distinct parameter signatures.'),
Q('Java 9','Inheritance','In the diagrammed hierarchy, class Dog inherits accessible members from:',['Object only, never Animal','Animal','Cat','No class'],1,'Dog extends Animal and inherits its accessible state and behavior.'),
Q('Java 10','Interfaces','A concrete class implementing an interface must:',['Implement its abstract methods or remain abstract','Extend two concrete classes','Declare every field private','Avoid polymorphism'],0,'A non-abstract implementing class supplies implementations for required abstract methods.'),
Q('Java 11','Exceptions','The diagrammed catch block runs when:',['No statement executes','A matching exception is thrown in try','The class is compiled only','The JVM starts normally'],1,'Control transfers from try to the first compatible catch handler.'),
Q('Java 12','Exceptions','Which construct runs whether or not an exception is caught, barring abnormal termination?',['throw','finally','extends','import'],1,'A finally block is intended for cleanup after try/catch processing.'),
Q('Java 13','Threads','Calling start() on a Thread normally causes the JVM to:',['Invoke run() on a new execution thread','Delete the object','Run the constructor again','Block forever immediately'],0,'start() schedules a new thread whose entry point is run().'),
Q('Java 14','Threads','In the diagrammed lifecycle, a waiting thread becomes runnable after:',['Notification or its wait condition completes','Compilation fails','Its object is garbage-collected','The source file is deleted'],0,'Notification, timeout, or completion of the relevant condition allows the thread to contend again.'),
Q('Java 15','Generics','The primary benefit of List<String> over a raw List is:',['Automatic network access','Compile-time type safety','Multiple inheritance','Faster CPU clock speed'],1,'Generic type arguments let the compiler detect incompatible element types.'),
Q('Java 16','Collections and Lambdas','Which expression correctly represents a no-argument lambda returning 42?',['() -> 42','lambda = 42 only','return -> () 42','[] => 42'],0,'The empty parameter list is followed by the arrow and expression body.')
];

Object.assign(JAVA_QUESTIONS[1],{img:'/static/moocs/diagrams/java-execution.svg',alt:'Java source compiled to bytecode and executed by a JVM'});
Object.assign(JAVA_QUESTIONS[8],{img:'/static/moocs/diagrams/java-inheritance.svg',alt:'Animal superclass with Dog and Cat subclasses'});
Object.assign(JAVA_QUESTIONS[10],{img:'/static/moocs/diagrams/java-exception-flow.svg',alt:'Java try catch finally control flow'});
Object.assign(JAVA_QUESTIONS[13],{img:'/static/moocs/diagrams/java-thread-states.svg',alt:'Simplified Java thread lifecycle states'});

const DBMS_QUESTIONS=[
Q('DBMS 1','Database Systems','Compared with separate application files, a DBMS most directly helps control:',['Data redundancy and inconsistent copies','CPU instruction length','Network signal frequency','Java bytecode'],0,'Centralized schemas and constraints reduce uncontrolled duplication and inconsistency.'),
Q('DBMS 2','ER Modeling','In the diagrammed university model, the diamond labeled Enrolls represents a:',['Entity set','Relationship set','Attribute domain','Physical file'],1,'ER diamonds represent relationships between entity sets.'),
Q('DBMS 3','Relational Model','A candidate key is a set of attributes that:',['May identify several tuples','Minimally and uniquely identifies each tuple','Must contain every attribute','Can contain only nulls'],1,'A candidate key is both unique and minimal.'),
Q('DBMS 4','Integrity Constraints','A non-null foreign-key value must match:',['Any value in the same row','A referenced candidate or primary-key value','Only a view name','A disk page number'],1,'Referential integrity requires a corresponding referenced tuple.'),
Q('DBMS 5','Relational Algebra','Which relational algebra operator selects columns?',['Selection','Projection','Cartesian product','Union'],1,'Projection retains specified attributes; selection retains qualifying rows.'),
Q('DBMS 6','SQL','Which clause filters groups after aggregate computation?',['WHERE','HAVING','ORDER BY only','FROM'],1,'HAVING applies predicates to groups produced by GROUP BY.'),
Q('DBMS 7','Normalization','A relation is in BCNF when every nontrivial functional dependency X→Y has X as a:',['Foreign key only','Superkey','Nullable attribute','Multivalued field'],1,'BCNF requires every determinant of a nontrivial dependency to be a superkey.'),
Q('DBMS 8','SQL Aggregation','To report departments whose average salary exceeds 60000, the aggregate predicate belongs in:',['WHERE AVG(salary)>60000','HAVING AVG(salary)>60000','FROM AVG(salary)','ORDER BY only'],1,'Aggregate conditions over groups are expressed with HAVING.'),
Q('DBMS 9','B+ Tree Indexes','In the diagrammed B+ tree, actual data entries or record references are stored at the:',['Root only','Leaf level','Every separator only','Buffer header'],1,'B+ tree leaves contain data entries and are typically linked for range scans.'),
Q('DBMS 10','Hash Indexes','A hash index is especially effective for:',['Equality lookup','Ordered range scan','Sorting every row','Prefix hierarchy traversal'],0,'Hashing quickly locates a bucket for equality predicates but does not preserve order.'),
Q('DBMS 11','Query Optimization','In the diagrammed plan, pushing a selective filter below a join usually:',['Increases intermediate rows','Reduces intermediate rows','Removes all indexes','Changes SQL semantics always'],1,'Early selection reduces the data processed by later operators when the rewrite is valid.'),
Q('DBMS 12','Transactions','Atomicity means that a transaction:',['Executes completely or has no effect','Always runs alone','Never reads data','Must finish in one CPU instruction'],0,'Atomicity prevents a partially completed transaction from remaining visible.'),
Q('DBMS 13','Concurrency Control','Strict two-phase locking holds exclusive locks until:',['The first read','Commit or abort','A second lock is requested','The query is parsed'],1,'Holding write locks to transaction end prevents cascading aborts and ensures strict schedules.'),
Q('DBMS 14','Distributed Transactions','The diagrammed two-phase commit protocol first asks participants to:',['Delete their logs','Prepare and vote','Return query rows','Rebuild every index'],1,'The coordinator gathers prepare votes before announcing commit or abort.'),
];

Object.assign(DBMS_QUESTIONS[1],{img:'/static/moocs/diagrams/dbms-er.svg',alt:'ER diagram connecting Student and Course through Enrolls'});
Object.assign(DBMS_QUESTIONS[8],{img:'/static/moocs/diagrams/dbms-bplus-tree.svg',alt:'B plus tree with internal separators and linked leaves'});
Object.assign(DBMS_QUESTIONS[10],{img:'/static/moocs/diagrams/dbms-query-plan.svg',alt:'Query plan with selection pushed below a join'});
Object.assign(DBMS_QUESTIONS[13],{img:'/static/moocs/diagrams/dbms-two-phase-commit.svg',alt:'Two-phase commit messages between coordinator and participants'});

const OPERATING_SYSTEM_QUESTIONS=[
Q('Operating Systems 1','OS Services','Which mechanism lets a user program request a protected kernel service?',['System call','Cache hit','SQL view','Logic gate'],0,'A system call crosses the user-kernel boundary through a controlled interface.'),
Q('Operating Systems 2','Processes','In the diagrammed lifecycle, a process waiting for I/O is in the:',['Running state','Waiting or blocked state','New state only','Terminated state'],1,'A process that cannot proceed until an event completes is blocked.'),
Q('Operating Systems 3','Threads','Threads within one process normally share:',['Program counter values','Address space and open resources','Every stack frame','Thread identifiers'],1,'Threads have separate execution state but share their process resources and memory.'),
Q('Operating Systems 4','CPU Scheduling','For the diagrammed ready queue, which nonpreemptive policy selects the shortest next CPU burst?',['FCFS','SJF','Round Robin','FIFO paging'],1,'Shortest-Job-First chooses the ready process with the smallest predicted CPU burst.'),
Q('Operating Systems 5','Synchronization','A counting semaphore is changed atomically by:',['wait and signal operations','SQL SELECT and JOIN','compile and link','push and pop only'],0,'Atomic wait and signal operations coordinate access to a counted resource.'),
Q('Operating Systems 6','Deadlocks','The diagrammed resource-allocation graph indicates deadlock when its cycle involves:',['Single-instance resource types','No processes','Only free resources','Acyclic dependencies'],0,'With one instance per resource type, a cycle is both necessary and sufficient for deadlock.'),
Q('Operating Systems 7','Memory Management','Paging divides logical memory into fixed-size:',['Pages','Segments of arbitrary size','Files only','Processes'],0,'Logical pages map to equal-sized physical frames.'),
Q('Operating Systems 8','Paging','In the diagrammed translation, the page-table entry supplies the:',['Frame number','Process priority','File name','CPU burst'],0,'The frame number combines with the page offset to form a physical address.'),
Q('Operating Systems 9','Virtual Memory','A page fault occurs when the referenced page:',['Is not currently in physical memory','Is already in the TLB','Has offset zero','Belongs to the current process'],0,'The OS must bring a nonresident page into a frame before the access continues.'),
Q('Operating Systems 10','Page Replacement','Belady’s anomaly can occur with:',['FIFO replacement','Optimal replacement','LRU stack property','Every stack algorithm'],0,'FIFO may produce more faults when more frames are allocated.'),
Q('Operating Systems 11','File Systems','Which allocation method stores each file as a linked sequence of disk blocks?',['Linked allocation','Contiguous allocation only','Paging','Segmentation'],0,'Linked allocation lets each file block point to the next block.'),
Q('Operating Systems 12','Protection','An access matrix associates subjects and objects with:',['Permitted access rights','CPU clock rates','Page sizes only','Network frequencies'],0,'Each matrix entry describes the operations a domain or subject may perform on an object.')
];

Object.assign(OPERATING_SYSTEM_QUESTIONS[1],{img:'/static/moocs/diagrams/os-process-states.svg',alt:'Operating system process state transition diagram'});
Object.assign(OPERATING_SYSTEM_QUESTIONS[3],{img:'/static/moocs/diagrams/os-scheduling.svg',alt:'Ready queue with CPU burst lengths for scheduling'});
Object.assign(OPERATING_SYSTEM_QUESTIONS[5],{img:'/static/moocs/diagrams/os-deadlock.svg',alt:'Cyclic resource allocation graph with two processes and resources'});
Object.assign(OPERATING_SYSTEM_QUESTIONS[7],{img:'/static/moocs/diagrams/os-paging.svg',alt:'Logical address translated through a page table to physical memory'});

const CRYPTOGRAPHY_QUESTIONS=[
Q('Cryptography 1','Security Services','Which security property prevents unauthorized disclosure of information?',['Confidentiality','Availability','Nonrepudiation','Traffic routing'],0,'Confidentiality restricts information access to authorized parties.'),
Q('Cryptography 2','Security Attacks','Passive eavesdropping primarily threatens:',['Confidentiality','Availability only','CPU scheduling','Database normalization'],0,'A passive listener attempts to learn message contents without modifying traffic.'),
Q('Cryptography 3','Symmetric Encryption','In the diagrammed symmetric system, sender and receiver must share:',['The same secret key','Only public usernames','Different hash outputs','No cryptographic material'],0,'Symmetric encryption uses a shared secret for encryption and decryption.'),
Q('Cryptography 4','Classical Ciphers','A Caesar cipher with shift 3 maps plaintext A to:',['A','B','C','D'],3,'Shifting A forward by three alphabet positions produces D.'),
Q('Cryptography 5','Block Ciphers','The diagrammed AES structure repeatedly applies substitution, permutation, mixing, and:',['Round-key addition','SQL projection','Page replacement','Packet fragmentation'],0,'AES rounds transform state and combine it with round-key material.'),
Q('Cryptography 6','Modes of Operation','Which block-cipher mode uses an unpredictable initialization vector and chains ciphertext blocks?',['ECB','CBC','Raw RSA','Caesar'],1,'CBC XORs each plaintext block with the previous ciphertext block and begins with an IV.'),
Q('Cryptography 7','Public-Key Cryptography','To send confidential data to Bob using public-key encryption, Alice encrypts with:',['Alice’s private key','Bob’s public key','Bob’s private key','A public hash only'],1,'Only Bob should possess the private key that reverses encryption under his public key.'),
Q('Cryptography 8','Key Exchange','The diagrammed Diffie–Hellman exchange enables two parties to derive:',['A shared secret over a public channel','Each other’s private exponent','An unencrypted password','A database foreign key'],0,'Each party combines its private exponent with the other party’s public value to obtain the same secret.'),
Q('Cryptography 9','Hashes and MACs','A message authentication code provides integrity and:',['Source authentication using a shared secret','Confidentiality by itself','Disk allocation','Anonymous routing'],0,'A MAC lets parties sharing a key detect modification and authenticate the source.'),
Q('Cryptography 10','Digital Signatures','In the diagrammed signature workflow, a verifier checks the signature using the signer’s:',['Public key','Private key','Symmetric session key only','Password database'],0,'The signer uses a private key and verifiers use the corresponding public key.'),
Q('Cryptography 11','Firewalls','A firewall placed at a network boundary primarily enforces:',['Traffic access-control policy','Java inheritance','CPU burst prediction','Relational normalization'],0,'A firewall permits or blocks traffic according to configured security policy.')
];

Object.assign(CRYPTOGRAPHY_QUESTIONS[2],{img:'/static/moocs/diagrams/crypto-symmetric.svg',alt:'Symmetric encryption and decryption using one shared secret key'});
Object.assign(CRYPTOGRAPHY_QUESTIONS[4],{img:'/static/moocs/diagrams/crypto-aes-rounds.svg',alt:'Simplified AES round transformation sequence'});
Object.assign(CRYPTOGRAPHY_QUESTIONS[7],{img:'/static/moocs/diagrams/crypto-diffie-hellman.svg',alt:'Diffie Hellman public exchange producing a shared secret'});
Object.assign(CRYPTOGRAPHY_QUESTIONS[9],{img:'/static/moocs/diagrams/crypto-signature.svg',alt:'Digital signature generation and public key verification'});

const SOFTWARE_ENGINEERING_QUESTIONS=[
Q('Software Engineering 1','Software Process','A software process provides a framework for:',['Organizing development activities and work products','Replacing every stakeholder','Encrypting network packets','Scheduling CPU bursts'],0,'A process structures activities, actions, tasks, milestones, and deliverables.'),
Q('Software Engineering 2','Process Models','The diagrammed spiral model is explicitly driven by repeated:',['Risk analysis','Database normalization','Page replacement','Key exchange'],0,'Each spiral cycle evaluates objectives and risks before engineering the next increment.'),
Q('Software Engineering 3','Requirements','A good software requirement should be testable and:',['Ambiguous','Verifiable','Implementation-dependent always','Secret from stakeholders'],1,'Clear, consistent, feasible, and verifiable requirements support validation.'),
Q('Software Engineering 4','Use Cases','In the diagrammed use-case model, the external stick figure represents a:',['Database table','Actor','Software class only','Test stub'],1,'An actor is an external role that interacts with the system.'),
Q('Software Engineering 5','Project Risk','Risk exposure is commonly estimated as probability multiplied by:',['Impact or loss','Lines of code only','Team size only','Number of passwords'],0,'Combining likelihood and consequence helps prioritize mitigation.'),
Q('Software Engineering 6','Design Quality','Functional independence is encouraged by:',['High cohesion and low coupling','Low cohesion and high coupling','Global data everywhere','Duplicated modules'],0,'Focused modules with limited dependencies are easier to understand, test, and change.'),
Q('Software Engineering 7','Analysis Modeling','In the diagrammed data-flow model, arrows represent:',['Data movement','Class inheritance','CPU interrupts','Encryption keys'],0,'DFD arrows show data flowing among processes, stores, and external entities.'),
Q('Software Engineering 8','Testing','Boundary-value analysis concentrates tests:',['At and near input-domain limits','Only at average values','Only after deployment','On source comments'],0,'Defects often occur at boundaries, so tests include boundary and adjacent values.'),
Q('Software Engineering 9','White-Box Testing','For the diagrammed flow graph, cyclomatic complexity estimates the number of:',['Independent execution paths','Database relations','Encryption rounds','Project stakeholders'],0,'Cyclomatic complexity provides an upper bound on basis paths for white-box testing.'),
Q('Software Engineering 10','Configuration Management','After a baseline is established, a proposed change should first undergo:',['Formal change control','Untracked direct editing','Immediate production release','Deletion of version history'],0,'Change control evaluates, approves, records, and tracks modifications to baselined items.')
];

Object.assign(SOFTWARE_ENGINEERING_QUESTIONS[1],{img:'/static/moocs/diagrams/se-spiral.svg',alt:'Risk driven spiral software process model'});
Object.assign(SOFTWARE_ENGINEERING_QUESTIONS[3],{img:'/static/moocs/diagrams/se-use-case.svg',alt:'Actor interacting with examination system use cases'});
Object.assign(SOFTWARE_ENGINEERING_QUESTIONS[6],{img:'/static/moocs/diagrams/se-data-flow.svg',alt:'Data flow diagram with process data store and external entity'});
Object.assign(SOFTWARE_ENGINEERING_QUESTIONS[8],{img:'/static/moocs/diagrams/se-flow-graph.svg',alt:'Control flow graph containing decisions and independent paths'});

const ALGORITHM_QUESTIONS=[
Q('Algorithms 1','Asymptotic Analysis','If T(n)=3n squared+7n+4, its tight asymptotic bound is:',['Theta(n squared)','Theta(n)','Theta(log n)','Theta(2 to the n)'],0,'The highest-order term dominates as n grows, so the running time is Theta(n squared).'),
Q('Algorithms 2','Divide and Conquer','The diagrammed divide-and-conquer strategy solves a problem by:',['Splitting it into smaller subproblems and combining their solutions','Always examining every permutation','Using only a single loop','Discarding all recursive results'],0,'Divide-and-conquer recursively solves smaller instances and combines their results.'),
Q('Algorithms 3','Merge Sort','In the diagrammed merge-sort tree, merging two sorted lists of total length n takes:',['Theta(n)','Theta(n squared)','Theta(log n)','Theta(1)'],0,'Each element is examined and copied a constant number of times during one merge.'),
Q('Algorithms 4','Greedy Method','Kruskal\'s algorithm constructs a minimum spanning tree by repeatedly selecting:',['The lightest safe edge that does not form a cycle','The heaviest edge incident on the source','Every edge in input order','Only edges of equal weight'],0,'Kruskal adds a minimum-weight edge that connects different components.'),
Q('Algorithms 5','Dynamic Programming','The diagrammed table is useful when subproblems overlap because it:',['Stores solutions so they are not recomputed','Forces exponential recursion','Removes the recurrence relation','Requires all edge weights to be negative'],0,'Dynamic programming records subproblem results and reuses them.'),
Q('Algorithms 6','Shortest Paths','Dijkstra\'s standard greedy algorithm is guaranteed to find shortest paths when edge weights are:',['Nonnegative','All negative','Complex numbers only','Unknown and changing during execution'],0,'A negative edge can invalidate the settled-distance property used by Dijkstra\'s algorithm.'),
Q('Algorithms 7','Backtracking','For the N-Queens problem, backtracking prunes a partial placement as soon as:',['Two placed queens attack one another','Every row has been filled successfully','The board size is even','The first queen is placed'],0,'A conflicting partial placement cannot lead to a valid complete arrangement.'),
Q('Algorithms 8','Branch and Bound','In the diagrammed branch-and-bound tree, a live node may be pruned when its bound:',['Cannot improve the best feasible solution found so far','Is written as an integer','Has two children','Was generated before another node'],0,'A noncompetitive bound proves that no descendant can beat the incumbent solution.'),
Q('Algorithms 9','NP-Completeness','To prove a new decision problem X is NP-hard using a known NP-complete problem Y, the required polynomial reduction direction is:',['Y reduces to X','X reduces to Y only','X equals Y syntactically','X and Y must use identical inputs'],0,'Reducing Y to X shows that an efficient solver for X would also solve the known hard problem Y.')
];

Object.assign(ALGORITHM_QUESTIONS[1],{img:'/static/moocs/diagrams/algo-divide-conquer.svg',alt:'Divide and conquer problem decomposition and combination tree'});
Object.assign(ALGORITHM_QUESTIONS[2],{img:'/static/moocs/diagrams/algo-merge-sort.svg',alt:'Merge sort splitting and merging sequence'});
Object.assign(ALGORITHM_QUESTIONS[4],{img:'/static/moocs/diagrams/algo-dynamic-programming.svg',alt:'Dynamic programming table with reused subproblem values'});
Object.assign(ALGORITHM_QUESTIONS[7],{img:'/static/moocs/diagrams/algo-branch-bound.svg',alt:'Branch and bound state space tree with a pruned node'});

// Set 1 contains 10 COA questions and 9 questions from each other subject.
const ARCHITECTURE_QUESTIONS=QUESTIONS.slice(0,10);
const MINING_QUESTIONS=QUESTIONS.slice(50,59);
const SET_ONE=[];
for(let index=0;index<10;index++){
  SET_ONE.push(ARCHITECTURE_QUESTIONS[index]);
  if(index<9){
    SET_ONE.push(DATA_STRUCTURE_QUESTIONS[index]);
    SET_ONE.push(MINING_QUESTIONS[index]);
    SET_ONE.push(DISCRETE_MATHEMATICS_QUESTIONS[index]);
    SET_ONE.push(DATA_COMMUNICATION_QUESTIONS[index]);
    SET_ONE.push(JAVA_QUESTIONS[index]);
    SET_ONE.push(DBMS_QUESTIONS[index]);
    SET_ONE.push(OPERATING_SYSTEM_QUESTIONS[index]);
    SET_ONE.push(CRYPTOGRAPHY_QUESTIONS[index]);
    SET_ONE.push(SOFTWARE_ENGINEERING_QUESTIONS[index]);
    SET_ONE.push(ALGORITHM_QUESTIONS[index]);
  }
}
QUESTIONS.splice(0,QUESTIONS.length,...SET_ONE);

// Randomize the answer-key positions on every exam load. The pool contains 25
// of each position, so A/B/C/D remain balanced without forming a visible cycle.
const RANDOM_ANSWER_POSITIONS=Array.from({length:100},(_,index)=>index%4);
for(let index=RANDOM_ANSWER_POSITIONS.length-1;index>0;index--){
  const swapIndex=Math.floor(Math.random()*(index+1));
  [RANDOM_ANSWER_POSITIONS[index],RANDOM_ANSWER_POSITIONS[swapIndex]]=[RANDOM_ANSWER_POSITIONS[swapIndex],RANDOM_ANSWER_POSITIONS[index]];
}

QUESTIONS.forEach((item,index)=>{
  const subject=item.s.startsWith('Architecture')?'COA':item.s.startsWith('Data Structures')?'Data Structures':item.s.startsWith('Data Mining')?'Data Mining':item.s.startsWith('Discrete Mathematics')?'Discrete Mathematics':item.s.startsWith('Data Communications')?'Data Communications and Networking':item.s.startsWith('Java')?'Java Programming':item.s.startsWith('DBMS')?'Database Management Systems':item.s.startsWith('Operating Systems')?'Operating Systems':item.s.startsWith('Cryptography')?'Cryptography and Network Security':item.s.startsWith('Software Engineering')?'Software Engineering':'Fundamentals of Computer Algorithms';
  item.level=index<34?'Level 1':index<67?'Level 2':'Level 3';
  item.s=`Set 1 • ${item.level} • ${subject}`;
  const randomPosition=RANDOM_ANSWER_POSITIONS[index];
  if(item.a!==randomPosition){
    [item.o[item.a],item.o[randomPosition]]=[item.o[randomPosition],item.o[item.a]];
    item.a=randomPosition;
  }
});

// Passage-based questions require learners to interpret a scenario before
// applying the concept. They are distributed across all three levels.
const PARAGRAPH_QUESTIONS={
  4:'A student sends a project file from a browser to a server. The data must reach the correct server process, be divided into manageable units, and—when reliability is requested—be reordered and recovered after loss.',
  16:'A learner saves Hello.java, compiles it into a class file, and moves that same class file from Windows to Linux. Each computer has a suitable runtime installed.',
  29:'Several worker threads belong to one process. Each has its own call stack and program counter, but they cooperate over common objects and open files.',
  48:'Two engineers compare links for a sensor network. Link X has greater bandwidth, while Link Y has the same bandwidth but a much stronger signal relative to noise. They use Shannon’s capacity relationship to compare the limits.',
  61:'A payroll query groups employees by department and calculates AVG(salary). Management wants the output to contain only departments whose computed average exceeds 60000.',
  64:'A team reviews a module that performs one focused responsibility and communicates with other modules through a small, stable interface.',
  92:'A sender treats a frame as a polynomial, appends zero bits, and performs modulo-2 division using a shared generator. The receiver repeats the calculation to detect transmission errors.',
  96:'Two systems share a secret key. One system sends a message and an authentication tag; the receiver recomputes the tag to detect alteration and authenticate the source.',
  97:'A tester converts a routine with decisions into a control-flow graph and wants a basis set that exercises every independent path.',
  98:'A researcher proposes a polynomial-time transformation from a known NP-complete problem Y into a new decision problem X to establish the difficulty of X.'
};
Object.entries(PARAGRAPH_QUESTIONS).forEach(([index,passage])=>{
  QUESTIONS[Number(index)].passage=passage;
  QUESTIONS[Number(index)].mode='paragraph';
});

// Convert three randomly chosen questions per subject into fill-in-the-blank
// items for this attempt; all remaining items use selection buttons.
['COA','Data Structures','Data Mining','Discrete Mathematics','Data Communications and Networking','Java Programming','Database Management Systems','Operating Systems','Cryptography and Network Security','Software Engineering','Fundamentals of Computer Algorithms'].forEach(subject=>{
  const candidates=QUESTIONS.map((item,index)=>item.s.endsWith(subject)&&item.mode!=='paragraph'?index:-1).filter(index=>index>=0);
  for(let index=candidates.length-1;index>0;index--){
    const swapIndex=Math.floor(Math.random()*(index+1));
    [candidates[index],candidates[swapIndex]]=[candidates[swapIndex],candidates[index]];
  }
  candidates.slice(0,3).forEach(index=>{ QUESTIONS[index].mode='fill'; });
});
