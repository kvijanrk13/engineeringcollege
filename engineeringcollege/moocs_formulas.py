"""Formula catalogue for the MOOCS TS SET / UGC NET / GATE mock examination.

Every subject used by the examination is defined once in ``SUBJECT_LIBRARY``.
Each examination pattern then references the subject keys it covers, so a
formula added to a subject automatically appears in every pattern that uses it.

Each formula entry is ``{"name", "latex", "note"}``. ``latex`` is rendered with
MathJax on the client; if MathJax is unavailable the raw TeX source is still
readable, which keeps the page useful offline.
"""

SUBJECT_LIBRARY = {
    "engineering-mathematics": {
        "name": "Engineering Mathematics",
        "icon": "∑",
        "colour": "#0ea5e9",
        "topics": [
            {
                "title": "Set Theory & Relations",
                "items": [
                    {
                        "name": "De Morgan's Laws",
                        "latex": r"\overline{A \cup B} = \overline{A} \cap \overline{B}, \qquad \overline{A \cap B} = \overline{A} \cup \overline{B}",
                        "note": "Complement of a union is the intersection of complements and vice versa.",
                    },
                    {
                        "name": "Cardinality of a Set Difference",
                        "latex": r"|A - B| = |A| - |A \cap B|",
                        "note": "Elements of A that are not in B.",
                    },
                    {
                        "name": "n-ary Cartesian Product",
                        "latex": r"|A_1 \times A_2 \times \cdots \times A_n| = \prod_{i=1}^{n} |A_i|",
                        "note": "Multiply the sizes of all participating sets.",
                    },
                    {
                        "name": "Equivalence Relation",
                        "latex": "R \\text{ is an equivalence relation} \\iff R \\text{ is reflexive, symmetric and transitive}",
                        "note": "A partition of a set into disjoint equivalence classes always exists for such an R.",
                    },
                    {
                        "name": "Inclusion-Exclusion (two sets)",
                        "latex": r"|A \cup B| = |A| + |B| - |A \cap B|",
                        "note": "Subtract the overlap counted twice.",
                    },
                    {
                        "name": "Inclusion-Exclusion (three sets)",
                        "latex": r"|A \cup B \cup C| = |A|+|B|+|C| - |A \cap B| - |B \cap C| - |C \cap A| + |A \cap B \cap C|",
                        "note": "Alternating sum of intersections.",
                    },
                    {
                        "name": "Principle of Mathematical Induction",
                        "latex": r"\big[P(1) \;\wedge\; \big(P(k) \Rightarrow P(k+1)\big)\big] \Rightarrow \forall k \ge 1, P(k)",
                        "note": "Base case plus inductive step proves the statement for all natural numbers.",
                    },
                ],
            },
            {
                "title": "Relations & Counting",
                "items": [
                    {
                        "name": "Function Counting onto (Surjective)",
                        "latex": r"\text{Onto}(n,m) = m!\, S(n,m) = \sum_{i=0}^{m} (-1)^{i} \binom{m}{i} (m-i)^{n}",
                        "note": "S(n,m) is a Stirling number of the second kind; the sum is inclusion-exclusion.",
                    },
                    {
                        "name": "Injective (One-One) Function Count",
                        "latex": r"\text{One-one}(n,m) = {}^{m}P_{n} = \frac{m!}{(m-n)!}, \quad m \ge n",
                        "note": "Without repetition: m choices first, m-1 second, and so on.",
                    },
                    {
                        "name": "Number of Surjections from n-set onto k-set",
                        "latex": r"\sum_{i=0}^{k} (-1)^i \binom{k}{i} (k-i)^n",
                        "note": "Inclusion-exclusion over the missing codomain elements.",
                    },
                    {
                        "name": "Number of Relations",
                        "latex": r"\text{Relations on a set of size } n = 2^{n^2}",
                        "note": "Every ordered pair is either in or out of the relation.",
                    },
                    {
                        "name": "Number of Functions",
                        "latex": r"\text{Functions} = m^n \quad (\text{from an } n\text{-set to an } m\text{-set})",
                        "note": "Each domain element picks one image independently.",
                    },
                    {
                        "name": "Total Weak Ordering / Precedence",
                        "latex": r"\sum_{k=1}^{n} k!\, S(n,k)",
                        "note": "Ordered partitions; used in ranking combinatorics.",
                    },
                    {
                        "name": "Circular Permutations",
                        "latex": r"(n-1)!",
                        "note": "Rotations are considered identical.",
                    },
                ],
            },
            {
                "title": "Combinatorics",
                "items": [
                    {
                        "name": "Permutation",
                        "latex": r"{}^{n}P_{r} = \frac{n!}{(n-r)!}",
                        "note": "Ordered selection of r distinct objects from n.",
                    },
                    {
                        "name": "Combination",
                        "latex": r"{}^{n}C_{r} = \frac{n!}{r!\,(n-r)!}",
                        "note": "Unordered selection of r objects from n.",
                    },
                    {
                        "name": "Identical Objects in Groups",
                        "latex": r"\frac{n!}{n_1!\, n_2! \cdots n_k!}, \qquad n_1 + n_2 + \cdots + n_k = n",
                        "note": "Multinomial distribution of indistinguishable groups.",
                    },
                    {
                        "name": "Negative Binomial Distribution",
                        "latex": r"P(X=x) = {x+r-1 \choose r-1} p^{r} (1-p)^{x-r}",
                        "note": "Probability of the r-th success occurring on the (r+x-1)-th trial.",
                    },
                    {
                        "name": "Binomial Recurrence",
                        "latex": r"{}^{n}C_{r} = {}^{n-1}C_{r} + {}^{n-1}C_{r-1}",
                        "note": "Pascal's identity.",
                    },
                ],
            },
            {
                "title": "Graph Theory",
                "items": [
                    {
                        "name": "Handshaking Lemma",
                        "latex": r"\sum_{v \in V} \deg(v) = 2|E|",
                        "note": "Every edge contributes exactly two endpoints.",
                    },
                    {
                        "name": "Euler Circuit Exists",
                        "latex": r"\text{Euler circuit} \iff \text{graph is connected} \;\wedge\; \deg(v) \text{ even } \forall v",
                        "note": "Necessary and sufficient for a closed trail using every edge once.",
                    },
                    {
                        "name": "Euler Path Exists",
                        "latex": r"\text{Euler path} \iff \text{exactly 0 or 2 vertices of odd degree} \;\wedge\; \text{connected}",
                        "note": "Two odd-degree vertices mean the path is open, not closed.",
                    },
                    {
                        "name": "Number of Trees (Cayley's Formula)",
                        "latex": r"\text{Number of labelled trees on } n \text{ vertices} = n^{\,n-2}",
                        "note": "Exponent counts each vertex choice of parent in a rooted tree.",
                    },
                    {
                        "name": "Complete Graph K_n",
                        "latex": r"|E| = \frac{n(n-1)}{2}, \qquad \deg(v) = n-1",
                        "note": "Every pair of distinct vertices is connected by one edge.",
                    },
                    {
                        "name": "Chromatic Number of a Tree",
                        "latex": r"\chi(T) = 2 \quad (|E| \ge 1)",
                        "note": "Trees are bipartite; a single-edge tree needs two colours.",
                    },
                    {
                        "name": "Planar Graph Euler Bound",
                        "latex": r"|E| \le 3|V| - 6 \quad \text{(simple planar, } |V| \ge 3\text{)}",
                        "note": "Each face needs at least three edges.",
                    },
                    {
                        "name": "Minimum Spanning Tree (Prim / Kruskal)",
                        "latex": r"|V| - 1 \text{ edges}, \qquad W_{MST} = \min_{T} \sum_{e \in T} w(e)",
                        "note": "Any spanning tree of n vertices has exactly n-1 edges.",
                    },
                ],
            },
            {
                "title": "Discrete Probability",
                "items": [
                    {
                        "name": "Addition Rule",
                        "latex": r"P(A \cup B) = P(A) + P(B) - P(A \cap B)",
                        "note": "Use when A and B overlap.",
                    },
                    {
                        "name": "Multiplication Rule",
                        "latex": r"P(A \cap B) = P(A)\, P(B \mid A)",
                        "note": "Joint probability from conditional probability.",
                    },
                    {
                        "name": "Bayes' Theorem",
                        "latex": r"P(H \mid E) = \frac{P(E \mid H)\, P(H)}{P(E)}, \qquad P(E) = \sum_{i} P(E \mid H_i) P(H_i)",
                        "note": "Total probability in the denominator; the prior is updated by the evidence.",
                    },
                    {
                        "name": "Law of Total Expectation",
                        "latex": r"E[X] = \sum_i P(A_i) E[X \mid A_i]",
                        "note": "Partition of the sample space conditions.",
                    },
                    {
                        "name": "Variance of a Sum of Independent Variables",
                        "latex": r"\mathrm{Var}(X+Y) = \mathrm{Var}(X) + \mathrm{Var}(Y)",
                        "note": "Covariance term vanishes only under independence.",
                    },
                    {
                        "name": "Joint Normal Density",
                        "latex": r"f(x,y) = \frac{1}{2\pi \sigma_1 \sigma_2 \sqrt{1-\rho^2}} \exp\!\left(-\frac{1}{2(1-\rho^2)}\left[\frac{(x-\mu_1)^2}{\sigma_1^2} - \frac{2\rho (x-\mu_1)(y-\mu_2)}{\sigma_1\sigma_2} + \frac{(y-\mu_2)^2}{\sigma_2^2}\right]\right)",
                        "note": "rho = 0 recovers the product of two independent Gaussians.",
                    },
                    {
                        "name": "Chebyshev's Inequality",
                        "latex": r"P(|X - \mu| \ge k\sigma) \le \frac{1}{k^2}",
                        "note": "Only uses mean and variance; no distributional assumption.",
                    },
                ],
            },
            {
                "title": "Continuous Probability & Distributions",
                "items": [
                    {
                        "name": "Uniform Distribution",
                        "latex": r"f(x) = \frac{1}{b-a}, \quad a \le x \le b; \qquad E[X] = \frac{a+b}{2}, \quad \mathrm{Var}(X) = \frac{(b-a)^2}{12}",
                        "note": "Rectangular density over the interval.",
                    },
                    {
                        "name": "Exponential Distribution",
                        "latex": r"f(x) = \lambda e^{-\lambda x}, \quad x \ge 0; \qquad E[X] = \frac{1}{\lambda}, \quad \mathrm{Var}(X) = \frac{1}{\lambda^2}",
                        "note": "Memoryless: P(X>s+t | X>s) = P(X>t).",
                    },
                    {
                        "name": "Poisson Process",
                        "latex": r"P(N(t)=k) = \frac{(\lambda t)^k e^{-\lambda t}}{k!}, \qquad P(N(t_1+t_2)=k) = \sum_{i=0}^{k} P(N(t_1)=i) P(N(t_2)=k-i)",
                        "note": "Independent increments; a binomial limit as p -> 0, n*p -> lambda.",
                    },
                    {
                        "name": "Normal PDF and CDF",
                        "latex": r"f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-(x-\mu)^2 / (2\sigma^2)}, \qquad \Phi(z) = \int_{-\infty}^{z} f(t)\,dt",
                        "note": "Approximately 68-95-99.7 rule for 1, 2 and 3 standard deviations.",
                    },
                    {
                        "name": "Standard Normal Score",
                        "latex": r"Z = \frac{X - \mu}{\sigma}",
                        "note": "Transforms any normal variable to the standard normal.",
                    },
                    {
                        "name": "Covariance & Correlation",
                        "latex": r"\mathrm{Cov}(X,Y) = E[(X-E[X])(Y-E[Y])], \qquad \rho = \frac{\mathrm{Cov}(X,Y)}{\sigma_X \sigma_Y}",
                        "note": "rho in [-1, 1]; rho = 0 implies no linear correlation.",
                    },
                ],
            },
            {
                "title": "Linear Algebra & Matrices",
                "items": [
                    {
                        "name": "Determinant of a 2x2 Matrix",
                        "latex": r"\begin{vmatrix} a & b \\ c & d \end{vmatrix} = ad - bc",
                        "note": "Standard expansion along the first row.",
                    },
                    {
                        "name": "Rank of a Matrix",
                        "latex": r"\mathrm{rank}(A) = \text{number of non-zero rows in the row echelon form of } A",
                        "note": "Row reduction preserves rank; rank <= min(m, n).",
                    },
                    {
                        "name": "Inverse of a Square Matrix",
                        "latex": r"A^{-1} = \frac{1}{|A|} \mathrm{adj}(A), \qquad A^{-1} \text{ exists} \iff |A| \ne 0",
                        "note": "Adjugate is the transpose of the cofactor matrix.",
                    },
                    {
                        "name": "Solution of a Linear System (Cramer's Rule)",
                        "latex": r"x_i = \frac{|A_i|}{|A|} \quad \text{where } |A| \ne 0",
                        "note": "Replace column i of A with the RHS vector b.",
                    },
                    {
                        "name": "Eigenvalue Equation",
                        "latex": r"|A - \lambda I| = 0, \qquad A v = \lambda v",
                        "note": "Eigenvalues are the roots of the characteristic polynomial.",
                    },
                    {
                        "name": "Cayley-Hamilton Theorem",
                        "latex": r"A^{n} + c_{n-1}A^{n-1} + \cdots + c_1 A + c_0 I = 0",
                        "note": "Every square matrix satisfies its own characteristic equation.",
                    },
                    {
                        "name": "Eigenvector Orthogonality (Symmetric Matrix)",
                        "latex": r"v_i^T v_j = 0 \quad (i \ne j), \qquad A = Q \Lambda Q^T",
                        "note": "Symmetric matrices are orthogonally diagonalisable.",
                    },
                ],
            },
            {
                "title": "Calculus & Optimisation",
                "items": [
                    {
                        "name": "Derivative of a Composite",
                        "latex": r"\frac{d}{dx} f(g(x)) = f'(g(x))\, g'(x)",
                        "note": "Chain rule.",
                    },
                    {
                        "name": "Fundamental Theorem of Calculus",
                        "latex": r"\int_a^b f'(x)\, dx = f(b) - f(a), \qquad \frac{d}{dx} F(x) = f(x) \text{ where } F(x)=\int_a^x f(t)dt",
                        "note": "Links differentiation and integration.",
                    },
                    {
                        "name": "Integration by Parts",
                        "latex": r"\int u\, dv = uv - \int v\, du",
                        "note": "Choose u by LIATE ordering.",
                    },
                    {
                        "name": "Maxima and Minima",
                        "latex": r"f'(x^{*}) = 0, \qquad f''(x^{*}) > 0 \Rightarrow \text{minimum}, \quad f''(x^{*}) < 0 \Rightarrow \text{maximum}",
                        "note": "Second-derivative test.",
                    },
                    {
                        "name": "Taylor Series",
                        "latex": r"f(x) = \sum_{n=0}^{\infty} \frac{f^{(n)}(a)}{n!} (x-a)^n",
                        "note": "Maclaurin series is the special case a = 0.",
                    },
                    {
                        "name": "Lagrange Multipliers",
                        "latex": r"\nabla f = \lambda \nabla g",
                        "note": "Stationary points of f subject to the constraint g = 0.",
                    },
                    {
                        "name": "Gradient / Directional Derivative",
                        "latex": r"\nabla f = \left(\frac{\partial f}{\partial x}, \frac{\partial f}{\partial y}\right), \qquad D_{\hat{u}} f = \nabla f \cdot \hat{u}",
                        "note": "The gradient is normal to the level curve.",
                    },
                ],
            },
        ],
    },
    "digital-logic-coa": {
        "name": "Digital Logic & Computer Organisation",
        "icon": "⚡",
        "colour": "#f97316",
        "topics": [
            {
                "title": "Number Systems",
                "items": [
                    {
                        "name": "Binary to Decimal (positional)",
                        "latex": r"(b_n b_{n-1} \cdots b_0)_2 = \sum_{i=0}^{n} b_i 2^i",
                        "note": "111011.10 base 2 = 59.5 in base 10.",
                    },
                    {
                        "name": "Decimal to Binary (repeated division)",
                        "latex": r"N = q_0 \cdot 2 + r_0, \quad \text{repeat with } q_0",
                        "note": "Remainders read bottom to top give the binary digits.",
                    },
                    {
                        "name": "Decimal to Octal / Hexadecimal",
                        "latex": r"\text{Group binary digits in 3 (octal) or 4 (hex) from the right}",
                        "note": "2^3 = 8 and 2^4 = 16 make the grouping exact.",
                    },
                    {
                        "name": "1's and 2's Complement Ranges",
                        "latex": r"\text{Range of } n\text{-bit 1's complement} = -(2^{n-1}-1) \text{ to } (2^{n-1}-1)",
                        "note": "n-bit 2's complement: -2^{n-1} to 2^{n-1} - 1.",
                    },
                    {
                        "name": "2's Complement (radix complement)",
                        "latex": r"N' = 2^n - |N|, \qquad N' + 1 \text{ is stored}",
                        "note": "A number is its own 2's complement: -x = ~x + 1.",
                    },
                    {
                        "name": "Ones Complement (dimidend)",
                        "latex": r"\text{If } N \ge 0 \text{ keep bits; if } N < 0, \text{ complement all } n \text{ bits}",
                        "note": "Two zeroes exist: +0 and -0.",
                    },
                    {
                        "name": "Excess / Bias Representation",
                        "latex": r"\text{Stored} = N + 2^{k-1}",
                        "note": "Shifts the range so the most significant bit is a sign flag.",
                    },
                    {
                        "name": "Gray Code Successor",
                        "latex": r"g_{i+1} = b_{i+1} \oplus b_{i}",
                        "note": "Adjacent codes differ in exactly one bit.",
                    },
                ],
            },
            {
                "title": "Boolean Algebra",
                "items": [
                    {
                        "name": "De Morgan's Theorems",
                        "latex": r"\overline{A \cdot B} = \bar{A} + \bar{B}, \qquad \overline{A + B} = \bar{A} \cdot \bar{B}",
                        "note": "Complement flips the operator as well.",
                    },
                    {
                        "name": "Distributive Laws",
                        "latex": r"A(B+C) = AB + AC, \qquad A + BC = (A+B)(A+C)",
                        "note": "The second form is the dual of the first.",
                    },
                    {
                        "name": "Absorption Law",
                        "latex": r"A + AB = A, \qquad A(A+B) = A",
                        "note": "A redundant term is absorbed.",
                    },
                    {
                        "name": "Consensus Theorem",
                        "latex": r"AB + A'C + BC = AB + A'C",
                        "note": "The consensus term BC is redundant.",
                    },
                    {
                        "name": "Universal Gates",
                        "latex": r"\text{NOT} = (A \cdot A)', \quad \text{NAND} = (AB)', \quad \text{NOR} = (A+B)'",
                        "note": "Any one of these alone is functionally complete.",
                    },
                    {
                        "name": "Sum of Products / Product of Sums",
                        "latex": r"F = \Sigma m(\cdot) = \Pi M(\cdot)",
                        "note": "SOP lists 1-rows; POS lists 0-rows of the truth table.",
                    },
                    {
                        "name": "XOR and XNOR",
                        "latex": r"A \oplus B = A'B + AB', \qquad \overline{A \oplus B} = AB + A'B'",
                        "note": "XOR is 1 when the inputs differ.",
                    },
                    {
                        "name": "Excess-3 Code",
                        "latex": r"\text{Excess-3}(A) = \text{Binary}(A) + 0011",
                        "note": "Self-complementing like 2421 code; used in BCD counters.",
                    },
                ],
            },
            {
                "title": "Digital Logic Circuits",
                "items": [
                    {
                        "name": "Multiplexer Data Selection",
                        "latex": r"Y = \Sigma\, \overline{S_i} D_i",
                        "note": "For 2^n inputs there are n select lines.",
                    },
                    {
                        "name": "Demultiplexer",
                        "latex": r"Y_i = \overline{S} \cdot D",
                        "note": "Routes one data input to one of 2^n outputs.",
                    },
                    {
                        "name": "Full Adder Sum and Carry",
                        "latex": r"S = A \oplus B \oplus C_{in}, \qquad C_{out} = AB + C_{in}(A \oplus B)",
                        "note": "Two half adders plus one OR gate.",
                    },
                    {
                        "name": "Half Adder",
                        "latex": r"S = A \oplus B, \qquad C = A \cdot B",
                        "note": "Adds two single-bit inputs only.",
                    },
                    {
                        "name": "Full Subtractor",
                        "latex": r"D = A \oplus B \oplus B_{in}, \qquad B_{out} = A'B + A B_{in} + B B_{in}",
                        "note": "Borrow logic is the dual of the adder carry.",
                    },
                    {
                        "name": "Number of Inputs for an n-bit Comparator",
                        "latex": r"\text{Inputs} = 2^{2^n} \quad (2^n \text{ output combinations})",
                        "note": "Minimum inputs for a truth table with 2^n outputs.",
                    },
                    {
                        "name": "Karnaugh Map Grouping",
                        "latex": r"\text{Group size} = 2^k \ \text{ones} \Rightarrow k \text{ literals cancelled}",
                        "note": "Use octets, quads, pairs and wrap-around adjacency.",
                    },
                ],
            },
            {
                "title": "Memory & Storage",
                "items": [
                    {
                        "name": "Byte Addressability",
                        "latex": r"\text{Address space} = 2^{n} \times \text{bytes per addressable unit}",
                        "note": "With n address lines and byte addressing there are 2^n locations.",
                    },
                    {
                        "name": "Required Address Lines",
                        "latex": r"n = \lceil \log_2 (\text{memory size in addressable units}) \rceil",
                        "note": "Round up to the next power of two.",
                    },
                    {
                        "name": "Required Data Lines",
                        "latex": r"d = \frac{\text{size in bits}}{\text{number of addressable units}}",
                        "note": "Word width equals the data line count.",
                    },
                    {
                        "name": "Chip Select Decoding",
                        "latex": r"\text{Address lines used} = \log_2(\text{number of memory chips})",
                        "note": "Higher-order address lines select the chip.",
                    },
                ],
            },
            {
                "title": "Instruction Cycle & Addressing",
                "items": [
                    {
                        "name": "Instruction Cycle Phases",
                        "latex": r"\text{Fetch} \rightarrow \text{Decode} \rightarrow \text{Execute} \rightarrow \text{Interrupt Check}",
                        "note": "The fetch-decode-execute loop of any CPU.",
                    },
                    {
                        "name": "Effective Address (Indexed / Base)",
                        "latex": r"EA = A + (\text{IX}) \quad \text{or} \quad EA = A + (\text{Base Register})",
                        "note": "Index register offset or base register displacement.",
                    },
                    {
                        "name": "Displacement Addressing",
                        "latex": r"EA = A + D",
                        "note": "Effective address is the address field plus the displacement.",
                    },
                    {
                        "name": "Relative Addressing",
                        "latex": r"EA = (PC) + D",
                        "note": "Relocatable because the base is the program counter.",
                    },
                    {
                        "name": "Program Counter Update (Sequential)",
                        "latex": r"PC \leftarrow PC + \text{length of current instruction}",
                        "note": "Fetch increments the PC by the instruction length.",
                    },
                ],
            },
            {
                "title": "Cache Memory",
                "items": [
                    {
                        "name": "Cache Hit Ratio",
                        "latex": r"H = \frac{\text{Number of hits}}{\text{Total accesses}}",
                        "note": "Averaged over all references.",
                    },
                    {
                        "name": "Average Memory Access Time",
                        "latex": r"T_{avg} = H \cdot T_c + (1-H)\cdot T_m",
                        "note": "Sequential lookup on a miss.",
                    },
                    {
                        "name": "Effective Access Time (Parallel Lookup)",
                        "latex": r"T_{avg} = t_c + (1-H)\, t_m",
                        "note": "Tag check and data fetch happen in parallel.",
                    },
                    {
                        "name": "AMAT with Miss Penalty",
                        "latex": r"AMAT = T_c + \text{Miss Rate} \times \text{Miss Penalty}",
                        "note": "Standard GATE-style formulation.",
                    },
                    {
                        "name": "Locality of Reference",
                        "latex": r"\text{Temporal} + \text{Spatial} \text{ locality} \Rightarrow \text{high hit ratio}",
                        "note": "Recently used or nearby addresses are likely to be used again.",
                    },
                    {
                        "name": "Cache Address Split",
                        "latex": r"\text{Address} = \underbrace{\text{Tag} \mid \text{Index} \mid \text{Offset}}_{\text{Word bits}}",
                        "note": "Index selects the block; tag verifies the match.",
                    },
                ],
            },
            {
                "title": "Pipelining & Parallelism",
                "items": [
                    {
                        "name": "Speedup of Pipelining",
                        "latex": r"S = \frac{T_{non\text{-}pipe}}{T_{pipe}} = \frac{nk}{k + (n-1)} = \frac{nk}{k + n - 1}",
                        "note": "n stages, k cycles per stage, n instructions.",
                    },
                    {
                        "name": "Pipeline Efficiency",
                        "latex": r"\eta = \frac{\text{Actual speedup}}{\text{Maximum speedup}} \times 100",
                        "note": "Quantifies the loss from pipeline bubbles.",
                    },
                    {
                        "name": "CPI in a Pipeline",
                        "latex": r"\text{CPI}_{avg} = 1 + \text{stall cycles per instruction}",
                        "note": "Hazards and cache misses add stall cycles.",
                    },
                    {
                        "name": "Hazard Detection",
                        "latex": r"\text{No forwarding} \Rightarrow \text{stall } (k-1) \text{ cycles on RAW dependency}",
                        "note": "Write-after-read, read-after-write, write-after-write.",
                    },
                    {
                        "name": "ILP Equation",
                        "latex": r"\text{CPU time} = \text{IC} \times \text{CPI} \times \text{Clock cycle time}",
                        "note": "The three-factor performance equation.",
                    },
                    {
                        "name": "Flynn's Taxonomy",
                        "latex": r"\text{SISD, SIMD, MISD, MIMD}",
                        "note": "Single/Multiple instruction and data streams.",
                    },
                ],
            },
        ],
    },
    "programming": {
        "name": "Programming (C / Java)",
        "icon": "{ }",
        "colour": "#8b5cf6",
        "topics": [
            {
                "title": "C Pointers & Arrays",
                "items": [
                    {
                        "name": "Address Arithmetic",
                        "latex": r"a[i] \equiv *(a + i), \qquad \&a[i] = \&a[0] + i",
                        "note": "Array indexing is defined in terms of pointer arithmetic.",
                    },
                    {
                        "name": "Size of a Pointer",
                        "latex": r"\text{sizeof}(p) = \text{sizeof}(\text{address})",
                        "note": "Independent of the pointed-to type; 4 or 8 bytes in practice.",
                    },
                    {
                        "name": "Passing Arrays to Functions",
                        "latex": r"\text{Arrays are passed by address} \Rightarrow \text{modifications are visible to the caller}",
                        "note": "Only a pointer to the first element is copied.",
                    },
                    {
                        "name": "Dynamic Memory",
                        "latex": r"p = (\text{type}*)\,\text{malloc}(n \cdot \text{sizeof(type)}); \quad \text{free}(p);",
                        "note": "free() releases the block and should be called exactly once.",
                    },
                ],
            },
            {
                "title": "C Pointers & Strings",
                "items": [
                    {
                        "name": "Null Pointer Check",
                        "latex": r"p \ne \text{NULL} \quad \text{before any dereference}",
                        "note": "NULL expands to ((void*)0) in C.",
                    },
                    {
                        "name": "C String Length",
                        "latex": r"\text{strlen}(s) \text{ counts characters up to the first NUL terminator}",
                        "note": "The terminator is not counted.",
                    },
                ],
            },
            {
                "title": "Functions & Recursion",
                "items": [
                    {
                        "name": "Recurrence for Factorial",
                        "latex": r"n! = \begin{cases} 1, & n = 0,1 \\ n \cdot (n-1)!, & n > 1 \end{cases}",
                        "note": "Base case plus recursive call on a smaller input.",
                    },
                    {
                        "name": "Fibonacci Recurrence",
                        "latex": r"F_n = F_{n-1} + F_{n-2}, \qquad F_0 = 0, \ F_1 = 1",
                        "note": "Naive recursion is O(phi^n); memoisation makes it O(n).",
                    },
                    {
                        "name": "Call Stack Frame Contents",
                        "latex": r"\text{Frame} = \{ \text{return address, saved registers, locals, parameters} \}",
                        "note": "Activation records grow and shrink with the call depth.",
                    },
                    {
                        "name": "Master Theorem",
                        "latex": r"T(n) = a T\!\left(\frac{n}{b^d}\right) + \Theta(n^c) \Rightarrow T(n) = \Theta\!\left(n^{c} \log^{\,p} n\right), \ p = 1 - d + \frac{\log_b a}{c}",
                        "note": "a subproblems of size n/b^d plus f(n) = Theta(n^c).",
                    },
                ],
            },
            {
                "title": "Java Language Features",
                "items": [
                    {
                        "name": "Widening vs Narrowing Conversion",
                        "latex": r"\text{Widening (implicit): } byte \to short \to int \to long \to float \to double",
                        "note": "Narrowing needs an explicit cast and may lose data.",
                    },
                    {
                        "name": "super() Rule",
                        "latex": r"\text{super()} \text{ must be the first statement of a constructor}",
                        "note": "Implicit when omitted.",
                    },
                    {
                        "name": "Method Overloading vs Overriding",
                        "latex": r"\text{Overloading: same name, different signature} \quad | \quad \text{Overriding: same signature, different class}",
                        "note": "Overriding needs inheritance and a compatible return type.",
                    },
                    {
                        "name": "String Concatenation Operator",
                        "latex": r"\text{String} + \text{anything} \Rightarrow \text{String}",
                        "note": "One operand must be a String for concatenation rather than addition.",
                    },
                    {
                        "name": "Java Thread States",
                        "latex": r"\text{NEW} \to \text{RUNNABLE} \to \text{BLOCKED/WAITING} \to \text{TERMINATED}",
                        "note": "Runnable covers both ready and running.",
                    },
                    {
                        "name": "Exception Hierarchy",
                        "latex": r"\text{Throwable} \supset \text{Error}, \ \text{Exception} \supset \text{RuntimeException}",
                        "note": "Checked exceptions must be declared or caught.",
                    },
                ],
            },
            {
                "title": "Web Technologies",
                "items": [
                    {
                        "name": "CSS Specificity",
                        "latex": r"\text{Specificity} = (\text{IDs},\ \text{classes},\ \text{elements})",
                        "note": "Compare column by column from the left.",
                    },
                    {
                        "name": "CSS Box Model Width",
                        "latex": r"W_{total} = W_{content} + P_{left} + P_{right} + B_{left} + B_{right} + M_{left} + M_{right}",
                        "note": "For the default content-box model.",
                    },
                    {
                        "name": "Bootstrap Grid",
                        "latex": r"12 \text{ column fluid grid}, \quad \text{col-md-} n \Rightarrow 12n/100\%",
                        "note": "Columns total 12 per row.",
                    },
                    {
                        "name": "HTML5 Semantic Elements",
                        "latex": r"\langle header \rangle, \langle nav \rangle, \langle section \rangle, \langle article \rangle, \langle aside \rangle, \langle footer \rangle",
                        "note": "Improves accessibility and SEO over generic divs.",
                    },
                    {
                        "name": "HTTP Status Codes",
                        "latex": r"2xx\, \text{success}; \ 3xx\, \text{redirection}; \ 4xx\, \text{client error}; \ 5xx\, \text{server error}",
                        "note": "404 not found, 403 forbidden, 500 internal server error.",
                    },
                    {
                        "name": "HTTP Request Methods",
                        "latex": r"\text{GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS}",
                        "note": "GET is safe and idempotent; POST is neither.",
                    },
                ],
            },
        ],
    },
    "dsa": {
        "name": "Data Structures & Algorithms",
        "icon": "\U0001f9f0",
        "colour": "#22c55e",
        "topics": [
            {
                "title": "Asymptotic Analysis",
                "items": [
                    {
                        "name": "Time Complexity Classes (Common)",
                        "latex": r"O(1) < O(\log n) < O(n) < O(n\log n) < O(n^2) < O(2^n) < O(n!)",
                        "note": "Strict asymptotic growth ordering.",
                    },
                    {
                        "name": "Theta vs O vs Omega",
                        "latex": r"f(n) = O(g(n)) \Leftrightarrow f(n) \le c\,g(n) \ \text{beyond } n_0",
                        "note": "Omega is the lower bound; Theta is tight in both directions.",
                    },
                    {
                        "name": "Space Complexity of Recursion",
                        "latex": r"S(n) = S(n-1) + O(1) \Rightarrow O(n) \text{ call-stack space}",
                        "note": "Frame size is constant but the depth grows linearly.",
                    },
                ],
            },
            {
                "title": "Sorting",
                "items": [
                    {
                        "name": "Merge Sort",
                        "latex": r"T(n) = 2T\!\left(\frac{n}{2}\right) + O(n) \Rightarrow O(n \log n)",
                        "note": "Stable, not in-place, needs O(n) auxiliary space.",
                    },
                    {
                        "name": "Quick Sort",
                        "latex": r"T(n) = T(n-k) + T(k) + O(n) \Rightarrow O(n \log n) \text{ avg}, \ O(n^2) \text{ worst}",
                        "note": "In-place and fast; worst case when the pivot is poor.",
                    },
                    {
                        "name": "Heap Sort",
                        "latex": r"T(n) = 2T\!\left(\frac{n}{2}\right) + O(n) \Rightarrow O(n \log n)",
                        "note": "In-place, not stable, guaranteed worst case O(n log n).",
                    },
                    {
                        "name": "Heap Insertion / Deletion",
                        "latex": r"\text{Insert: sift-up} \Rightarrow O(\log n), \qquad \text{Delete-max: sift-down} \Rightarrow O(\log n)",
                        "note": "Both maintain the complete-binary-tree invariant.",
                    },
                    {
                        "name": "Counting Sort",
                        "latex": r"T(n) = O(n + k), \quad k = \text{number of distinct keys}",
                        "note": "Non-comparison sort, linear time, needs a bounded key range.",
                    },
                    {
                        "name": "Lower Bound for Comparison Sorting",
                        "latex": r"\Omega(n \log n)",
                        "note": "Holds for any algorithm that only compares elements.",
                    },
                ],
            },
            {
                "title": "Searching",
                "items": [
                    {
                        "name": "Binary Search",
                        "latex": r"T(n) = T\!\left(\frac{n}{2}\right) + O(1) \Rightarrow O(\log n)",
                        "note": "Requires a sorted, randomly accessible sequence.",
                    },
                    {
                        "name": "Interpolation Search",
                        "latex": r"T(n) = O\!\left(\log_{\frac{m}{n}} n\right) \text{ for uniformly distributed data}",
                        "note": "O(log log n) on uniform data, O(n) on the worst case.",
                    },
                    {
                        "name": "Binary Search on a Recurrence",
                        "latex": r"T(n) = T(n/2) + c, \quad T(1) = k \Rightarrow T(n) = k + c\log_2 n",
                        "note": "One step of work per halving.",
                    },
                ],
            },
            {
                "title": "Linked Lists",
                "items": [
                    {
                        "name": "Traversal of a Singly Linked List",
                        "latex": r"T(n) = T(n-1) + O(1) \Rightarrow O(n)",
                        "note": "No random access; insertion after a node is O(1).",
                    },
                    {
                        "name": "Doubly Linked List Node",
                        "latex": r"\text{node} = \{ \text{prev}, \text{data}, \text{next} \}",
                        "note": "Costs 2n pointers for n nodes; deletion is O(1) given the node.",
                    },
                    {
                        "name": "Circular Linked List",
                        "latex": r"\text{last} \rightarrow \text{next} = \text{first}",
                        "note": "Enables round-robin scheduling.",
                    },
                ],
            },
            {
                "title": "Stacks & Queues",
                "items": [
                    {
                        "name": "Infix Evaluation with a Stack",
                        "latex": r"\text{Scan left to right: operand} \to \text{push}; \text{operator} \to \text{push, pop, reduce}",
                        "note": "Postfix needs no parentheses and no operator stack.",
                    },
                    {
                        "name": "Infix to Postfix Precedence",
                        "latex": r"\text{Parenthesis} > \text{*} \div > + \div (-) \text{ then } \text{associativity}",
                        "note": "Left-associative operators pop equal precedence on the left.",
                    },
                    {
                        "name": "Stack Applications",
                        "latex": r"\text{Paren matching, expression eval, undo, recursion sim, backtracking}",
                        "note": "LIFO order is the defining constraint.",
                    },
                    {
                        "name": "Circular Queue Full Condition",
                        "latex": r"(rear + 1) \bmod n = front \Rightarrow \text{full}",
                        "note": "One slot is always sacrificed to distinguish full from empty.",
                    },
                ],
            },
            {
                "title": "Trees",
                "items": [
                    {
                        "name": "Inorder Traversal of a BST",
                        "latex": r"\text{Inorder}(\text{BST}) = \text{sorted ascending order}",
                        "note": "Preorder = root-left-right, Postorder = left-right-root.",
                    },
                    {
                        "name": "Height vs Number of Nodes",
                        "latex": r"\text{Minimum nodes for height } h = h, \qquad \text{Maximum} = 2^{h} - 1",
                        "note": "Complete binary tree relation.",
                    },
                    {
                        "name": "AVL Balance Factor",
                        "latex": r"BF = h_{left} - h_{right} \in \{-1, 0, 1\}",
                        "note": "Violation triggers LL, RR, LR or RL rotation.",
                    },
                    {
                        "name": "Number of Binary Search Trees",
                        "latex": r"\text{Catalan number} \ C_n = \frac{1}{n+1}\binom{2n}{n}, \quad n = \text{keys}",
                        "note": "Counts distinct BST shapes for sorted keys.",
                    },
                    {
                        "name": "Optimal BST Expected Search Cost",
                        "latex": r"E = \sum_{i=1}^{n} p_i \cdot c_i",
                        "note": "Optimal trees minimise the weighted path length.",
                    },
                    {
                        "name": "Heap Property (Min-Heap)",
                        "latex": r"key(\text{parent}) \le key(\text{child}) \quad \forall \text{ internal nodes}",
                        "note": "Complete binary tree plus heap order.",
                    },
                    {
                        "name": "B-Tree Search Height",
                        "latex": r"\text{Height} = \left\lceil \log_{m+1} \frac{n+1}{m} \right\rceil \text{ for order } m",
                        "note": "Keeps disk access count low for large blocks.",
                    },
                    {
                        "name": "Hashing Load Factor",
                        "latex": r"\alpha = \frac{n}{m} \quad (n = \text{keys}, m = \text{table size})",
                        "note": "Average successful search under uniform hashing is about (1 + 1/alpha)/2.",
                    },
                ],
            },
            {
                "title": "Graph Algorithms",
                "items": [
                    {
                        "name": "BFS / DFS Time Complexity",
                        "latex": r"T(|V| + |E|) = O(|V| + |E|)",
                        "note": "Each vertex and edge is processed a constant number of times.",
                    },
                    {
                        "name": "Dijkstra's Relaxation",
                        "latex": r"d(v) \leftarrow \min \big( d(v),\ d(u) + w(u,v) \big)",
                        "note": "Fails with negative edge weights; Bellman-Ford handles those.",
                    },
                    {
                        "name": "Bellman-Ford",
                        "latex": r"T(|V| \cdot |E|) \text{ and detects negative cycles when } d(v) > d(u) + w(u,v)",
                        "note": "Relax every edge |V|-1 times.",
                    },
                    {
                        "name": "Floyd-Warshall",
                        "latex": r"d[i][j] \leftarrow \min\big(d[i][j],\ d[i][k] + d[k][j]\big), \quad T = O(|V|^3)",
                        "note": "All-pairs shortest paths with intermediate node k.",
                    },
                    {
                        "name": "Prim's Algorithm",
                        "latex": r"T(|E| \log |V|) \text{ with a priority queue}",
                        "note": "Grows one tree; safe edge by cut property.",
                    },
                    {
                        "name": "Kruskal's Algorithm",
                        "latex": r"T(|E| \log |E|), \quad \text{sort edges, add if no cycle}",
                        "note": "Uses union-find; builds the forest bottom-up.",
                    },
                    {
                        "name": "Topological Sort",
                        "latex": r"T(|V| + |E|); \text{ exists only for a DAG}",
                        "note": "A cycle makes topological ordering impossible.",
                    },
                    {
                        "name": "Articulation Point & Bridge",
                        "latex": r"\text{Increasing } \mathrm{low}[v] \text{ relative to } \mathrm{disc}[u] \text{ marks a bridge}",
                        "note": "Removing it disconnects the graph.",
                    },
                ],
            },
            {
                "title": "Algorithm Design Paradigms",
                "items": [
                    {
                        "name": "Dynamic Programming Recurrence",
                        "latex": r"DP[i] = \text{best of } \{ DP[j] + \text{cost} \} \text{ over all valid } j < i",
                        "note": "Optimal substructure plus overlapping subproblems.",
                    },
                    {
                        "name": "Optimal Substructure",
                        "latex": r"OPT(i) = \min_{j \in S} \{ w(j) + OPT(i-1) \}",
                        "note": "Term used for the coin-change and rod-cutting problems.",
                    },
                    {
                        "name": "Greedy Choice Property",
                        "latex": r"\text{Choose the locally best option; it is also globally optimal}",
                        "note": "Holds only when the problem has the matroid/exchange property.",
                    },
                    {
                        "name": "Divide and Conquer",
                        "latex": r"T(n) = 2T(n/2) + f(n) \Rightarrow \text{recurrence plus combining step}",
                        "note": "Merge sort, quicksort, FFT and binary search follow it.",
                    },
                ],
            },
        ],
    },
    "dbms": {
        "name": "DBMS",
        "icon": "\U0001f5c2",
        "colour": "#14b8a6",
        "topics": [
            {
                "title": "Relational Model & Algebra",
                "items": [
                    {
                        "name": "Relational Algebra - Selection & Projection",
                        "latex": r"\sigma_{p}(R) = \{ t \in R \mid p(t) \}, \qquad \pi_{A_1,\ldots,A_k}(R)",
                        "note": "sigma filters rows, pi removes columns and duplicates.",
                    },
                    {
                        "name": "Natural Join",
                        "latex": r"R \bowtie S = \{(t \cup u) \mid t \in R,\ u \in S,\ t \text{ and } u \text{ agree on common attributes}\}",
                        "note": "Cartesian product plus selection on equality of common attributes.",
                    },
                    {
                        "name": "Cartesian Product Size",
                        "latex": r"|R \times S| = |R| \cdot |S|",
                        "note": "Tuple combination; the reason joins are written as product plus filter.",
                    },
                    {
                        "name": "Outer Join",
                        "latex": r"R \bowtie_{\mathrm{left}} S \;\text{keeps unmatched tuples with NULLs in the missing columns}",
                        "note": "Left, right or full outer join.",
                    },
                    {
                        "name": "Division in Relational Algebra",
                        "latex": r"R \div S = \{ t \mid \forall s \in S,\ (t \cup s) \in R \}",
                        "note": "\"Find all students enrolled in every course of S\".",
                    },
                    {
                        "name": "Relational Calculus Predicate",
                        "latex": r"\{ t \mid P(t) \}",
                        "note": "Tuple relational calculus; equivalent to relational algebra.",
                    },
                ],
            },
            {
                "title": "Keys & Normalisation",
                "items": [
                    {
                        "name": "Superkey vs Candidate Key",
                        "latex": r"\text{Candidate key} = \text{minimal superkey}, \quad \text{Primary key} \leftarrow \text{selected candidate key}",
                        "note": "Composite key requires all component attributes.",
                    },
                    {
                        "name": "1NF",
                        "latex": r"\text{Atomic values only; no repeating groups, no nested relations}",
                        "note": "Every attribute value is a single indivisible value.",
                    },
                    {
                        "name": "2NF",
                        "latex": r"\text{1NF} \;\wedge\; \text{no partial dependency of a non-prime attribute on part of a candidate key}",
                        "note": "Applies only to composite keys.",
                    },
                    {
                        "name": "3NF",
                        "latex": r"R \text{ is in 3NF} \iff \text{for every } F^+: X \to A \text{ with } A \notin X,\ X \text{ is a superkey or } A \text{ is prime}",
                        "note": "Removes transitive dependency on the key.",
                    },
                    {
                        "name": "BCNF",
                        "latex": r"\text{For every } X \to A \text{ in } F^+,\ X \text{ must be a superkey}",
                        "note": "Stronger than 3NF; every determinant becomes a key.",
                    },
                    {
                        "name": "Functional Dependency Closure",
                        "latex": r"(XY)^{+} = X^{+} \cup \Big( \bigcup_{A \to B \in F^{+}\!\restriction_{X^{+}}} B \Big)",
                        "note": "Attribute closure decides candidate keys and 3NF/BCNF.",
                    },
                    {
                        "name": "Lossless Join Dependency",
                        "latex": r"R \to (R_1, R_2) \text{ is lossless} \iff (R_1 \cap R_2) \to R_1 \text{ or } (R_1 \cap R_2) \to R_2 \text{ in } F^+",
                        "note": "Guarantees no spurious tuples on join.",
                    },
                    {
                        "name": "Dependency Preservation",
                        "latex": r"(R_1 \cup R_2)^+ = (R_1^+) \cup (R_2^+) \text{ under the decomposed constraint set}",
                        "note": "Avoids checking the original F after decomposition.",
                    },
                ],
            },
            {
                "title": "SQL",
                "items": [
                    {
                        "name": "SELECT .. DISTINCT",
                        "latex": r"\text{SELECT DISTINCT } A_1, A_2 \text{ FROM R WHERE } p",
                        "note": "Removes duplicate tuples from the result.",
                    },
                    {
                        "name": "UPDATE vs DELETE",
                        "latex": r"\text{UPDATE R SET } A = v \text{ WHERE } p \qquad \text{DELETE FROM R WHERE } p",
                        "note": "ALTER changes the schema; UPDATE changes rows.",
                    },
                    {
                        "name": "GROUP BY + HAVING",
                        "latex": r"\text{WHERE filters rows before grouping; HAVING filters groups after aggregation}",
                        "note": "Aggregate rules restrict non-aggregated columns in the SELECT list.",
                    },
                    {
                        "name": "IN vs EXISTS",
                        "latex": r"\text{IN compares against a value set; EXISTS tests for row existence (usually cheaper)}",
                        "note": "NOT IN with NULLs behaves unexpectedly; NOT EXISTS is safer.",
                    },
                    {
                        "name": "ORDER BY",
                        "latex": r"\text{ORDER BY } A_1 \text{ ASC/DESC}, A_2 \text{ ASC/DESC}",
                        "note": "The result is a bag unless DISTINCT is used.",
                    },
                ],
            },
            {
                "title": "Indexing & Query Optimisation",
                "items": [
                    {
                        "name": "B+ Tree Height",
                        "latex": r"h = \left\lceil \log_{m} \frac{n+1}{1} \right\rceil \approx \left\lceil \log_m (n+1) \right\rceil",
                        "note": "All leaves at the same level; linked for range scans.",
                    },
                    {
                        "name": "B+ Tree Search",
                        "latex": r"\text{Binary search within a node of } m \text{ keys} \Rightarrow O(\log_m n)",
                        "note": "Choosing m = fanout keeps the height tiny for large n.",
                    },
                    {
                        "name": "Clustered vs Non-Clustered Index",
                        "latex": r"\text{Clustered: at most one per table, defines physical row order}",
                        "note": "A heap table may have many non-clustered indexes.",
                    },
                    {
                        "name": "Cost Model",
                        "latex": r"\text{Cost} = \text{IO cost} + \text{CPU cost}",
                        "note": "Full scan I/O is n / pages held in a buffer block.",
                    },
                    {
                        "name": "Indexed Nested-Loop Join",
                        "latex": r"\text{Cost} \approx |R| \cdot \log_2 |S| \text{ with an index on the inner relation}",
                        "note": "Advantageous when the inner table has an index.",
                    },
                    {
                        "name": "Hash Join",
                        "latex": r"\text{Cost} \approx |R| + |S| \text{ pages for a single pass build and probe}",
                        "note": "Best for equality joins; degrades with skew or overflow.",
                    },
                ],
            },
            {
                "title": "Transactions & Concurrency",
                "items": [
                    {
                        "name": "ACID Properties",
                        "latex": r"\text{Atomicity, Consistency, Isolation, Durability}",
                        "note": "Atomicity via the log, isolation via locking, durability via write-ahead logging.",
                    },
                    {
                        "name": "Two-Phase Locking",
                        "latex": r"\text{Phase 1: growing (shared then exclusive)} \;\to\; \text{Phase 2: shrinking (release only)}",
                        "note": "Guarantees conflict serializability; deadlocks are still possible.",
                    },
                    {
                        "name": "Conflict Serializability",
                        "latex": r"\text{Schedule is conflict-serializable} \iff \text{its precedence graph is acyclic}",
                        "note": "Cycle implies a non-serializable schedule.",
                    },
                    {
                        "name": "View Serializability",
                        "latex": r"\text{Every conflict-serializable schedule is view-serializable, not conversely}",
                        "note": "Blind writes distinguish the two.",
                    },
                    {
                        "name": "Isolation Levels",
                        "latex": r"\text{Read Uncommitted} < \text{Read Committed} < \text{Repeatable Read} < \text{Serializable}",
                        "note": "Higher levels reduce anomalies but lower concurrency.",
                    },
                    {
                        "name": "Optimistic Concurrency (Validation)",
                        "latex": r"\text{Read} \to \text{Compute} \to \text{Validate} \to \text{Write phases}",
                        "note": "Assumes few conflicts; timestamps order the transactions.",
                    },
                    {
                        "name": "MVCC",
                        "latex": r"\text{Each transaction reads the snapshot } T_s \text{ taken at its start time}",
                        "note": "Readers never block writers.",
                    },
                ],
            },
        ],
    },
    "operating-systems": {
        "name": "Operating Systems",
        "icon": "\u2699",
        "colour": "#ef4444",
        "topics": [
            {
                "title": "Processes & Threads",
                "items": [
                    {
                        "name": "Process States",
                        "latex": r"\text{New} \to \text{Ready} \to \text{Running} \to \text{Waiting} \to \text{Terminated}",
                        "note": "Preemption moves Running back to Ready.",
                    },
                    {
                        "name": "Threads vs Processes",
                        "latex": r"\text{Context switch cost: process} = O(\text{address space}), \ \text{thread} = O(1)",
                        "note": "Threads share the address space and resources.",
                    },
                    {
                        "name": "Amdahl's Law",
                        "latex": r"S = \frac{1}{(1-p) + \dfrac{p}{n}}",
                        "note": "p is the parallelisable fraction, n the number of processors.",
                    },
                    {
                        "name": "Gustafson's Law",
                        "latex": r"S = n - (1-p)\,n = n\,p",
                        "note": "Assumes the problem size grows with the machine.",
                    },
                    {
                        "name": "Speedup Bound",
                        "latex": r"S \le \dfrac{1}{1-p} \quad \text{as } n \to \infty",
                        "note": "Amdahl's law ceiling for a fixed problem size.",
                    },
                ],
            },
            {
                "title": "CPU Scheduling",
                "items": [
                    {
                        "name": "FCFS",
                        "latex": r"\text{Waiting time} = \text{Completion time} - \text{Burst time}",
                        "note": "Non-preemptive; suffers the convoy effect.",
                    },
                    {
                        "name": "Round Robin",
                        "latex": r"\text{Response time} \le \text{time slice} + \text{shortest remaining burst}",
                        "note": "Preemptive; best for time-sharing systems.",
                    },
                    {
                        "name": "Shortest Job First",
                        "latex": r"\text{Minimises average waiting time} \Rightarrow \text{minimum waiting time}",
                        "note": "Optimal but needs burst-time knowledge; can starve long jobs.",
                    },
                    {
                        "name": "SJF Non-Preemptive Formula",
                        "latex": r"\text{Avg. waiting time} = \frac{\sum (T_i - B_i)}{n}",
                        "note": "B_i is the burst time of process i in FCFS order.",
                    },
                    {
                        "name": "Highest Response Ratio Next",
                        "latex": r"HRRN = \frac{W + S}{S}",
                        "note": "Ages waiting processes, so starvation is avoided.",
                    },
                    {
                        "name": "Multilevel Queue",
                        "latex": r"\text{One queue per priority; each queue has its own scheduling policy}",
                        "note": "Possible starvation in the low-priority queue.",
                    },
                    {
                        "name": "Multilevel Feedback Queue",
                        "latex": r"\text{CPU-bound jobs demoted, I/O-bound jobs promoted}",
                        "note": "Adapts priorities dynamically without explicit priority input.",
                    },
                    {
                        "name": "Turnaround Time",
                        "latex": r"TAT = \text{Completion time} - \text{Arrival time}, \qquad \text{TAT} = B + W",
                        "note": "Average TAT = average burst + average waiting.",
                    },
                ],
            },
            {
                "title": "Synchronisation & Deadlocks",
                "items": [
                    {
                        "name": "Critical Section Requirements",
                        "latex": r"\text{Mutual exclusion, Progress, Bounded waiting}",
                        "note": "Standard conditions for a correct solution.",
                    },
                    {
                        "name": "Semaphore Operations",
                        "latex": r"\text{wait}(S) \to P(S), \qquad \text{signal}(S) \to V(S)",
                        "note": "P decrements and blocks; V increments and wakes.",
                    },
                    {
                        "name": "Producer-Consumer with Semaphores",
                        "latex": r"\text{mutex} = 1, \quad \text{empty} = n, \quad \text{full} = 0",
                        "note": "Producer waits on empty then full; consumer reverses the order.",
                    },
                    {
                        "name": "Dining Philosophers (Odd-Even Solution)",
                        "latex": r"\text{If } i \text{ is even take the left fork first, else the right fork}",
                        "note": "Guarantees that not all philosophers are blocked at once.",
                    },
                    {
                        "name": "Banker's Algorithm",
                        "latex": r"\text{Request}_i \le \text{Available}, \qquad \text{Need}_i \le (\text{Available} + \text{Allocation})",
                        "note": "Grant only if the resulting state stays safe.",
                    },
                    {
                        "name": "Safety Sequence",
                        "latex": r"\text{Find } \langle P_1, P_2, \ldots P_n \rangle \text{ with } \text{Need}_i \le \text{Available}",
                        "note": "A safe sequence guarantees no deadlock.",
                    },
                    {
                        "name": "Coffman Conditions for Deadlock",
                        "latex": r"\text{Mutual exclusion, Hold and wait, No preemption, Circular wait}",
                        "note": "Breaking any one condition prevents deadlock.",
                    },
                    {
                        "name": "Wait-for Graph Cycle",
                        "latex": r"\text{Deadlock} \iff \text{the wait-for graph contains a cycle (for single-instance resources)}",
                        "note": "Multi-instance resources make a cycle necessary but not sufficient.",
                    },
                ],
            },
            {
                "title": "Memory Management",
                "items": [
                    {
                        "name": "Paging Address Translation",
                        "latex": r"PA = \text{Page Number} \times \text{Page Size} + \text{Offset}",
                        "note": "Frame number comes from the page table using the page number.",
                    },
                    {
                        "name": "Average Access Time with TLB",
                        "latex": r"EAT = (1-p)\times m + p \times a",
                        "note": "p = TLB hit ratio, m = memory access, a = TLB access.",
                    },
                    {
                        "name": "Effective Access Time with Page Faults",
                        "latex": r"EAT = (1-p)\,t_{mem} + p \big( t_{page} + t_{restart} \big)",
                        "note": "Page faults require a full restart of the instruction.",
                    },
                    {
                        "name": "Number of Pages",
                        "latex": r"n = \left\lceil \frac{\text{Process size}}{\text{Page size}} \right\rceil",
                        "note": "Internal fragmentation = page size x n - process size.",
                    },
                    {
                        "name": "Optimal Page Replacement",
                        "latex": r"\text{Replace the page whose next use is farthest in the future}",
                        "note": "Belady's anomaly appears with FIFO and with LRU for stacks.",
                    },
                    {
                        "name": "Page Fault Rate (FIFO)",
                        "latex": r"\text{Fault rate} = \frac{\text{Page faults}}{\text{Number of page references}}",
                        "note": "Computed from the reference string.",
                    },
                    {
                        "name": "Belady's Anomaly",
                        "latex": r"\text{More frames} \Rightarrow \text{more page faults} \text{ under FIFO}",
                        "note": "LRU and OPT are stack algorithms and avoid it.",
                    },
                    {
                        "name": "Segmentation vs Paging Fragmentation",
                        "latex": r"\text{Paging: internal; \quad Segmentation: external}",
                        "note": "Pure segmentation needs compaction; pure paging wastes a partial page.",
                    },
                ],
            },
            {
                "title": "File Systems & Disk",
                "items": [
                    {
                        "name": "Disk Access Time",
                        "latex": r"T_{access} = T_{seek} + \frac{\text{rotation latency}}{1} + T_{transfer}",
                        "note": "Seek time is roughly proportional to the square of the track distance.",
                    },
                    {
                        "name": "Average Seek Time",
                        "latex": r"\frac{0 + 1 + 2 + \cdots + (N-1)}{N} = \frac{N-1}{2} \text{ cylinders}",
                        "note": "Track-to-track seek is constant; the average is half the range.",
                    },
                    {
                        "name": "FCFS vs SSTF",
                        "latex": r"T_{SSTF} \le T_{FCFS}, \qquad \text{SSTF can starve a far request}",
                        "note": "SCAN services requests in order of position.",
                    },
                    {
                        "name": "SCAN / C-SCAN Arm Movement",
                        "latex": r"\text{SCAN reverses at the end; C-SCAN returns immediately to the start}",
                        "note": "LOOK stops at the last request instead of the end of the disk.",
                    },
                    {
                        "name": "Disk Formatting Capacity",
                        "latex": r"\text{Capacity} = N_{heads} \times N_{cylinders} \times N_{sectors} \times \text{bytes per sector}",
                        "note": "Multiplies all the addressing components.",
                    },
                ],
            },
        ],
    },
    "toc-compiler": {
        "name": "TOC & Compiler Design",
        "icon": "\U0001f9ee",
        "colour": "#eab308",
        "topics": [
            {
                "title": "Formal Languages & Automata",
                "items": [
                    {
                        "name": "Finite Automaton Transition",
                        "latex": r"\delta(q, a) = q' \quad\text{with}\quad F = \{ q \mid \delta^{*}(q, w) \in f \}",
                        "note": "Delta-star is the extended transition function.",
                    },
                    {
                        "name": "Deterministic Finite Automaton Classes",
                        "latex": r"L(\text{DFA}) = L(\text{NFA}) = L(\text{NFA-}\varepsilon) = \{\text{regular languages}\}",
                        "note": "All three recognise exactly the regular languages.",
                    },
                    {
                        "name": "NFA to DFA (Subset Construction)",
                        "latex": r"\delta_D(S, a) = \bigcup_{q \in S} \delta_N(q, a)",
                        "note": "The DFA can have up to 2^n states for an n-state NFA.",
                    },
                    {
                        "name": "Epsilon Closure",
                        "latex": r"\varepsilon\text{-closure}(q) = \{ q \} \cup \{ p \mid q \Rightarrow^{*} p \text{ by } \varepsilon \}",
                        "note": "Take the union over all states of a subset before a move.",
                    },
                    {
                        "name": "Pumping Lemma for Regular Languages",
                        "latex": r"|w| \ge n \Rightarrow \exists\, xyz \text{ with } |xy| \le n,\ |y| \ge 1,\ xy^{i} z \in L \ \forall i \ge 0",
                        "note": "Used to prove a language is not regular.",
                    },
                    {
                        "name": "Pumping Lemma for CFL",
                        "latex": r"|w| \ge 2n \Rightarrow \exists\, uvxyz,\ uv^{i} x y^{i} z \in L \ \forall i \ge 0",
                        "note": "Only the strings of length at least 2n are guaranteed.",
                    },
                    {
                        "name": "Regular Expression Rules",
                        "latex": r"L(R_1 \cup R_2) = L(R_1) \cup L(R_2), \quad L(R_1 R_2) = L(R_1) L(R_2), \quad L(R^*) = \bigcup_{i=0}^{\infty} L(R)^i",
                        "note": "Equivalence with regular languages.",
                    },
                    {
                        "name": "Context-Free Grammar",
                        "latex": r"G = (V_N, V_T, P, S), \qquad A \to \alpha \in P",
                        "note": "Left recursion enables left factoring and top-down parsing.",
                    },
                    {
                        "name": "Chomsky Hierarchy",
                        "latex": r"\text{Type 0: } L_0 \supset \text{Type 1: } L_1 \supset \text{Type 2: } L_2 \supset \text{Type 3: } L_3",
                        "note": "Type 0 = RE, 1 = CS, 2 = CFL, 3 = regular.",
                    },
                    {
                        "name": "Chomsky Normal Form",
                        "latex": r"A \to BC \ \text{or} \ A \to a \ \text{or} \ S \to \varepsilon",
                        "note": "CNF makes membership testing polynomial.",
                    },
                ],
            },
            {
                "title": "Parsing",
                "items": [
                    {
                        "name": "LL(1) Condition",
                        "latex": r"\text{For each production } A \to \alpha, \ \text{FIRST}(\beta) \cap \text{FOLLOW}(A) = \emptyset \ \forall \beta \Rightarrow^* \alpha",
                        "note": "No left recursion plus no common prefixes gives an LL(1) grammar.",
                    },
                    {
                        "name": "FIRST and FOLLOW Sets",
                        "latex": r"\text{FIRST}(\beta) = \{ a \} \cup \text{FIRST of what follows } \beta, \quad \text{FOLLOW}(A) = \text{FIRST}(\beta) \cup \{ \$\}",
                        "note": "$ is the end-of-input marker.",
                    },
                    {
                        "name": "LR Parsing Table Size",
                        "latex": r"\text{Table} = O(|G| \times |\Sigma|) \quad \text{for } \text{LR}(k) \text{ parsers}",
                        "note": "Canonical LR(1) is linear in the grammar size; SLR and LALR compress it.",
                    },
                    {
                        "name": "LALR vs SLR",
                        "latex": r"\text{LALR merges LR(1) states with the same cores, so it is smaller but not as precise as LR(1)}",
                        "note": "Slotted by the DeRemer-Pennello algorithm in yacc.",
                    },
                    {
                        "name": "Left Factoring",
                        "latex": r"A \to \alpha \beta,\ A \to \alpha \gamma \Rightarrow A \to \alpha A', \ A' \to \beta \mid \gamma",
                        "note": "Removes common prefixes for top-down parsing.",
                    },
                ],
            },
            {
                "title": "Intermediate & Target Code",
                "items": [
                    {
                        "name": "Three-Address Code Instruction",
                        "latex": r"x = y \ \text{op} \ z, \quad \text{if } x \text{ goto } L, \quad \text{return } x",
                        "note": "Each instruction has at most three operands.",
                    },
                    {
                        "name": "Representation of Expressions",
                        "latex": r"\text{Syntax tree}, \ \text{Postfix (RPN)}, \ \text{DAG}, \ \text{Three-address code}",
                        "note": "The DAG captures common subexpressions.",
                    },
                    {
                        "name": "Quadruple, Triple, Indirect Triple",
                        "latex": r"\text{Quadruple} = (i, op, arg_1, arg_2) \Rightarrow \text{100 quadruples per 100 statements}",
                        "note": "A quadruple implicitly represents the DAG.",
                    },
                ],
            },
            {
                "title": "Syntax-Directed Translation & SDT",
                "items": [
                    {
                        "name": "Attribute Definition",
                        "latex": r"A.s \to f(B.x, C.y, A.s) \quad (s,t) \text{ - } (l,r) \text{ attributes}",
                        "note": "Synthetic and inherited attributes.",
                    },
                    {
                        "name": "Inherited Attribute for Type Checking",
                        "latex": r"T.type \leftarrow \text{if } E.type = \text{integer and } F.type = \text{integer then integer else error}",
                        "note": "Needed when information must flow downward.",
                    },
                    {
                        "name": "Types of Syntax-Directed Translation",
                        "latex": r"\text{L-attributed, S-attributed, L(1), S(1)}",
                        "note": "Bottom-up needs synthesised attributes only.",
                    },
                    {
                        "name": "Translation Scheme (Grammar Rule + Semantic Rule)",
                        "latex": r"A \to \alpha \ \{ p_1, p_2, \ldots, p_k \}",
                        "note": "The semantic actions run after the production is applied.",
                    },
                ],
            },
            {
                "title": "Code Optimisation & Symbol Table",
                "items": [
                    {
                        "name": "Basic Block & DAG Construction",
                        "latex": r"\text{Basic block} = \text{straight-line code with one entry and one exit}",
                        "note": "The DAG shares common subexpressions across the block.",
                    },
                    {
                        "name": "Peephole Optimisation",
                        "latex": r"w_1 w_2 w_3 = y;\ z;\ \text{with } y \text{ in } w_1 \text{ and } z \text{ not used elsewhere} \Rightarrow w_1 w_2 w_3 = y",
                        "note": "Local, single-block transformation.",
                    },
                    {
                        "name": "Global Code Optimisation",
                        "latex": r"\text{Data-flow analysis: } \text{reach}, \ \text{liveness}, \ \text{available expressions}, \ \text{constant folding}",
                        "note": "Works across basic blocks over the CFG.",
                    },
                    {
                        "name": "Loop Optimisation",
                        "latex": r"\text{Code hoisting, strength reduction, induction variables, loop unrolling}",
                        "note": "Strength reduction turns a multiply in a loop into an add.",
                    },
                    {
                        "name": "Static vs Dynamic Scope",
                        "latex": r"\text{Static: bindings fixed at compile time; Dynamic: at run time}",
                        "note": "Dynamic scope is useful for error handlers and debugger hooks.",
                    },
                    {
                        "name": "Bootstrapping",
                        "latex": r"\text{A language compiles itself once its own compiler is available}",
                        "note": "A compiler written in C compiled by gcc can then compile itself.",
                    },
                ],
            },
        ],
    },
    "networks": {
        "name": "Computer Networks",
        "icon": "\U0001f310",
        "colour": "#06b6d4",
        "topics": [
            {
                "title": "OSI & Physical Layer",
                "items": [
                    {
                        "name": "OSI Layers (bottom to top)",
                        "latex": r"\text{Bit} \to \text{Frame} \to \text{Packet} \to \text{Segment} \to \text{Message}",
                        "note": "Physical, Data Link, Network, Transport, Session, Presentation, Application.",
                    },
                    {
                        "name": "Data Rate",
                        "latex": r"\text{Rate (bps)} = \frac{\text{Bits}}{\text{Seconds}}, \qquad \text{Throughput} \le \text{Rate} \times \text{Efficiency}",
                        "note": "Utilisation ratio accounts for overhead and idle time.",
                    },
                    {
                        "name": "Nyquist Bit Rate",
                        "latex": r"C = 2B \log_2 L",
                        "note": "B is the bandwidth in Hz, L the number of signal levels.",
                    },
                    {
                        "name": "Shannon Capacity",
                        "latex": r"C = B \log_2 \left(1 + \frac{S}{N}\right)",
                        "note": "The absolute maximum noiseless-channel capacity.",
                    },
                    {
                        "name": "Encoding Efficiency",
                        "latex": r"\eta = \frac{\text{Actual bandwidth in bps}}{\text{Nyquist bit rate}} \times 100",
                        "note": "Determined by the signal-to-noise ratio.",
                    },
                    {
                        "name": "Baud Rate",
                        "latex": r"\text{Baud} = \text{symbols per second}, \qquad \text{data rate} = \text{Baud} \times \log_2 L",
                        "note": "Baud counts symbols; bit rate counts information.",
                    },
                ],
            },
            {
                "title": "Data Link Layer",
                "items": [
                    {
                        "name": "Parity Bit (Even/Odd)",
                        "latex": r"\text{Even parity: } \sum \text{bits} \equiv 0 \ (\bmod 2)",
                        "note": "Detects all odd numbers of bit errors.",
                    },
                    {
                        "name": "2D Parity (VRC + LRC)",
                        "latex": r"\text{VRC per row, LRC per column, \text{then overall parity}}",
                        "note": "Detects burst errors up to the square of the array dimension.",
                    },
                    {
                        "name": "CRC Polynomial Division",
                        "latex": r"M(x) = x^r \cdot A(x) \oplus \frac{A(x)x^r}{G(x)} G(x) = A(x)x^r \oplus R(x)",
                        "note": "Modulo-2 division; the remainder R is the checksum.",
                    },
                    {
                        "name": "CRC Error Detection",
                        "latex": r"\frac{M(x) \oplus R(x)}{G(x)} = 0 \Rightarrow \text{no error detected}",
                        "note": "A zero remainder after division confirms correctness.",
                    },
                    {
                        "name": "Sliding Window Protocol",
                        "latex": r"\text{Window size} \le 2^k - 1 \quad (\text{stop and wait}), \quad \le 2^{k}-1 \text{ with } k\text{-bit sequence numbers}",
                        "note": "The maximum window is bounded by the sequence number space.",
                    },
                    {
                        "name": "Go-Back-N",
                        "latex": r"\text{Retransmit from the errored frame onwards}; \quad W \le 2^k - 1",
                        "note": "Receiver discards out-of-sequence frames.",
                    },
                    {
                        "name": "Selective Repeat",
                        "latex": r"\text{Retransmit only the errored frames}; \quad W \le 2^{k-1}",
                        "note": "Needs buffering at the receiver; more efficient than GBN.",
                    },
                    {
                        "name": "Stop-and-Wait Efficiency",
                        "latex": r"\eta = \frac{1}{1 + 2a}, \qquad a = \frac{\text{propagation time}}{\text{frame transmission time}}",
                        "note": "Very low for long links, hence sliding windows.",
                    },
                ],
            },
            {
                "title": "Network Layer & IP",
                "items": [
                    {
                        "name": "IPv4 Address Classes",
                        "latex": r"A: 1-126, \ B: 128-191, \ C: 192-223, \ D: 224-239 \ (\text{multicast}), \ E: 240-255",
                        "note": "Classful addressing is obsolete; CIDR replaced it.",
                    },
                    {
                        "name": "CIDR Notation",
                        "latex": r"A.B.C.D/n \Rightarrow \text{Network} = A.B.C.D \ \text{and} \ n \ \text{host bits}",
                        "note": "n=26 gives 6 host bits and 64 usable addresses per subnet.",
                    },
                    {
                        "name": "Usable Host Addresses",
                        "latex": r"2^{h} - 2 \quad (h = 32 - \text{prefix length})",
                        "note": "Network and broadcast addresses are excluded.",
                    },
                    {
                        "name": "Subnet Mask",
                        "latex": r"\text{Mask} = 2^{\text{prefix}} - 1 \text{ shifted}; \quad \text{AND operation gives the network part}",
                        "note": "e.g. /24 mask is 255.255.255.0.",
                    },
                    {
                        "name": "Longest Prefix Match",
                        "latex": r"\text{Route} = \{\text{entry with the largest matching prefix length}\}",
                        "note": "Router lookup rule for CIDR tables.",
                    },
                    {
                        "name": "Distance Vector Routing (Bellman-Ford)",
                        "latex": r"D_x(y) = \min_{v} \{ c(x,v) + D_v(y) \}",
                        "note": "Count-to-infinity problem on failures.",
                    },
                    {
                        "name": "Link State Routing (Dijkstra)",
                        "latex": r"D(v) = \min_{u \in \text{settled}} \{ D(u) + c(u,v) \}",
                        "note": "Each node has the full topology; converges fast.",
                    },
                ],
            },
            {
                "title": "Transport Layer",
                "items": [
                    {
                        "name": "TCP Header Checksum",
                        "latex": r"\text{1's complement of the 1's complement sum of the whole segment including the pseudo-header}",
                        "note": "The pseudo-header is IP address, protocol, port and length.",
                    },
                    {
                        "name": "TCP Three-Way Handshake",
                        "latex": r"SYN \to SYN\!-\!ACK \to ACK",
                        "note": "Establishes sequence numbers and ends the connection politely.",
                    },
                    {
                        "name": "TCP Four-Way Termination",
                        "latex": r"FIN \to ACK \to FIN \to ACK",
                        "note": "Each direction is closed independently.",
                    },
                    {
                        "name": "TCP Sliding Window",
                        "latex": r"\text{Sender} \leftarrow \text{ACK} + 1, \qquad \text{flow} = \text{RTT} \times \text{bandwidth}",
                        "note": "Bandwidth-delay product sizes the window.",
                    },
                    {
                        "name": "Congestion Control Phases",
                        "latex": r"\text{Slow start} \to \text{congestion avoidance} \to \text{fast recovery}",
                        "note": "Threshold ssthresh = cwnd/2 on loss.",
                    },
                    {
                        "name": "Slow Start Growth",
                        "latex": r"\text{cwnd} = \text{cwnd} + 1 \ \text{per RTT} \quad (|\text{cwnd}| < \text{ssthresh})",
                        "note": "Exponential growth until the threshold.",
                    },
                    {
                        "name": "Congestion Avoidance (AIMD)",
                        "latex": r"\text{cwnd} \leftarrow \text{cwnd} + \frac{1}{\text{cwnd}} \ \text{per RTT}",
                        "note": "Additive increase, multiplicative decrease.",
                    },
                    {
                        "name": "TCP Throughput",
                        "latex": r"\text{Window size} = \text{RTT} \times \text{throughput}",
                        "note": "Links the flow-control window to the achieved rate.",
                    },
                    {
                        "name": "UDP Datagram",
                        "latex": r"\text{Header} = 8 \text{ bytes (source port, dest port, length, checksum)}",
                        "note": "Connectionless, no flow or congestion control.",
                    },
                ],
            },
            {
                "title": "Application Layer",
                "items": [
                    {
                        "name": "DNS Record Lookup",
                        "latex": r"\text{Client} \to \text{Resolver} \to \text{Root} \to \text{TLD} \to \text{Authoritative}",
                        "note": "Iterative or recursive resolution.",
                    },
                    {
                        "name": "DHCP DORA",
                        "latex": r"\text{Discover} \to \text{Offer} \to \text{Request} \to \text{Acknowledge}",
                        "note": "Four-step lease negotiation.",
                    },
                    {
                        "name": "HTTP Default Port",
                        "latex": r"\text{HTTP} = 80, \ \text{HTTPS} = 443, \ \text{FTP} = 21, \ \text{SSH} = 22, \ \text{SMTP} = 25, \ \text{DNS} = 53",
                        "note": "Well-known TCP port assignments.",
                    },
                    {
                        "name": "Email Addressing",
                        "latex": r"\text{mailbox} @ \text{mail server domain}",
                        "note": "SMTP for sending, POP3/IMAP for retrieval.",
                    },
                    {
                        "name": "Simple Mail Transfer",
                        "latex": r"\text{Client} \to \text{Server: MAIL FROM} \to RCPT TO \to DATA",
                        "note": "The POP3 commands USER, PASS, LIST, RETR, QUO.",
                    },
                ],
            },
            {
                "title": "Network Security",
                "items": [
                    {
                        "name": "RSA Encryption",
                        "latex": r"c = m^{e} \bmod n, \qquad m = c^{d} \bmod n, \qquad e \cdot d \equiv 1 \ (\bmod \phi(n))",
                        "note": "n = pq; never reuse p and q across different key pairs.",
                    },
                    {
                        "name": "Modular Exponentiation (Fast)",
                        "latex": r"a^{b \bmod m} \equiv \prod a^{b_i} \pmod{m} \text{ by repeated squaring}",
                        "note": "O(log b) multiplications.",
                    },
                    {
                        "name": "ElGamal / Diffie-Hellman",
                        "latex": r"y = g^{a} \bmod p; \quad K = y^{b} \equiv g^{ab} \pmod{p}",
                        "note": "Based on the discrete logarithm problem.",
                    },
                    {
                        "name": "Digital Signature",
                        "latex": r"S = h^{d} \bmod n \quad \text{(sign)}, \qquad h = S^{e} \bmod n \quad \text{(verify)}",
                        "note": "Provides authentication, integrity and non-repudiation.",
                    },
                    {
                        "name": "AES Rounds",
                        "latex": r"\text{AES-128} = 10 \text{ rounds}, \ \text{AES-192} = 12, \ \text{AES-256} = 14",
                        "note": "Blocks of 128 bits; keys of 128, 192 or 256 bits.",
                    },
                    {
                        "name": "Symmetric vs Asymmetric",
                        "latex": r"\text{HTTPS} = \text{asymmetric for key exchange} + \text{symmetric for bulk data}",
                        "note": "Asymmetric is slow but solves key distribution.",
                    },
                ],
            },
        ],
    },
    "software-engineering": {
        "name": "Software Engineering",
        "icon": "\U0001f4dd",
        "colour": "#ec4899",
        "topics": [
            {
                "title": "Process Models",
                "items": [
                    {
                        "name": "Waterfall Phase Order",
                        "latex": r"\text{Requirements} \to \text{Design} \to \text{Coding} \to \text{Testing} \to \text{Deployment} \to \text{Maintenance}",
                        "note": "Linear, document-driven, with feedback only to the previous phase.",
                    },
                    {
                        "name": "Spiral Model Quadrants",
                        "latex": r"\text{Objectives} \to \text{Risk assessment} \to \text{Engineering} \to \text{Planning}",
                        "note": "Risk-driven; the inner loop is a complete mini-project.",
                    },
                    {
                        "name": "V-Model",
                        "latex": r"\text{Traceability from requirement to unit test, integration test, system test, acceptance test}",
                        "note": "Each test level corresponds to a design decomposition level.",
                    },
                    {
                        "name": "Incremental Delivery",
                        "latex": r"\text{Increment} = \text{usable product slice delivered in cycles}",
                        "note": "Customers see value early; planning must be incremental too.",
                    },
                    {
                        "name": "Agile Sprint Cadence",
                        "latex": r"\text{Sprint} \to \text{Sprint planning} \to \text{Daily stand-up} \to \text{Sprint review} \to \text{Retrospective}",
                        "note": "Continuous integration, testing and delivery within a sprint.",
                    },
                ],
            },
            {
                "title": "Estimation",
                "items": [
                    {
                        "name": "Function Point (FP) Formula",
                        "latex": r"FP = \sum \text{weight}_i \times \text{complexity}_i \times 0.65 + 50 \times \text{scale factor}",
                        "note": "UFP times a technical adjustment factor gives the final FP.",
                    },
                    {
                        "name": "Unadjusted Function Point Weights",
                        "latex": r"\text{External inputs: 6 (avg), 4 (low), 3 (high)}",
                        "note": "External outputs 7/5/4; inquiries 4/3/2; files 15/10/7; interfaces 7/5/3.",
                    },
                    {
                        "name": "COCOMO II Estimation",
                        "latex": r"ES = a (KLOC)^{b} \times \prod EM_i",
                        "note": "Productivity (E) and schedule (T) models follow from this base effort.",
                    },
                    {
                        "name": "Staffing (Staffing Model)",
                        "latex": r"\text{Optimal staffing} = N \cdot 0.7 + 1 \text{ (Brooks)}, \quad N = 1 - 10^{-d/3}",
                        "note": "The late-curve factor N falls off exponentially with delay.",
                    },
                    {
                        "name": "Empirical Estimation Model (K-Collections)",
                        "latex": r"\text{Mean} = a \cdot (KLOC)^{b}, \qquad \sigma = c \cdot (KLOC)^{d}",
                        "note": "Standard deviation of the effort estimate.",
                    },
                    {
                        "name": "Earned Value Analysis",
                        "latex": r"\text{EV} = \text{BCP} \times \text{ACWP}, \qquad \text{CPI} = \frac{\text{EV}}{\text{ACWP}}",
                        "note": "CPI < 1 means the project is over budget.",
                    },
                ],
            },
            {
                "title": "Testing",
                "items": [
                    {
                        "name": "Cyclomatic Complexity",
                        "latex": r"V(G) = E - N + 2P",
                        "note": "E edges, N nodes, P connected components. Independent paths = V(G).",
                    },
                    {
                        "name": "Control-Flow Graph Test Paths",
                        "latex": r"\text{Number of paths} = V(G) \text{ by McCabe's basis-path approach}",
                        "note": "Cyclomatic measure equals the loop count plus 1.",
                    },
                    {
                        "name": "Statement / Decision / Condition Coverage",
                        "latex": r"\text{Decision} = 100\% \Rightarrow \text{condition} = 100\% \Rightarrow \text{statement} = 100\%",
                        "note": "Full statement coverage does not guarantee decision coverage.",
                    },
                    {
                        "name": "McCabe Threshold",
                        "latex": r"V(G) \le 10 \text{ is the conventional quality limit for a module}",
                        "note": "Higher complexity correlates strongly with defects.",
                    },
                    {
                        "name": "Black Box vs White Box",
                        "latex": r"\text{Equivalence partitioning: one representative from each class} \quad | \quad \text{Boundary values: } a, a\pm1, b",
                        "note": "Pairwise / combinatorial testing reduces the number of cases.",
                    },
                    {
                        "name": "White Box Coverage Measures",
                        "latex": r"\text{All paths} = \text{Untestable} \quad (\text{infinite with loops})",
                        "note": "Therefore use structural, not path, coverage.",
                    },
                ],
            },
            {
                "title": "Metrics & Maintenance",
                "items": [
                    {
                        "name": "Code Metrics (Halstead)",
                        "latex": r"N_1 = \log_2 n_1, \quad N_2 = \log_2 n_2, \quad N = N_1 + N_2, \quad V = N \log_2 N",
                        "note": "n1 = distinct operators, n2 = distinct operands.",
                    },
                    {
                        "name": "Maintainability Index",
                        "latex": r"MI = \max\left(0,\ \frac{171 - 5.2 \ln V - 0.23 G - 16.2 \ln LOC}{171}\right) \times 100",
                        "note": "Higher is better; falls with size and complexity.",
                    },
                    {
                        "name": "Software Quality Factors (McCall)",
                        "latex": r"\text{Correctness, Reliability, Efficiency, Integrity, Usability, Maintainability, Flexibility, Testability, Portability, Reusability}",
                        "note": "Measured indirectly through product and process metrics.",
                    },
                    {
                        "name": "Cost of Defect",
                        "latex": r"\text{Cost} \propto \text{Defect origin phase}^{-1}",
                        "note": "Defects caught in the design phase cost roughly ten times less than in production.",
                    },
                ],
            },
        ],
    },
    "ai-ml": {
        "name": "AI & Machine Learning",
        "icon": "\U0001f916",
        "colour": "#a855f7",
        "topics": [
            {
                "title": "Search Algorithms",
                "items": [
                    {
                        "name": "BFS and DFS",
                        "latex": r"\text{BFS uses a } \textbf{queue} \text{ (level order)}; \qquad \text{DFS uses a } \textbf{stack} \text{ (depth order)}",
                        "note": "Both are complete if the branching factor is finite.",
                    },
                    {
                        "name": "Heuristic Search (A*)",
                        "latex": r"f(n) = g(n) + h(n)",
                        "note": "g is the path cost so far, h the estimated cost to the goal.",
                    },
                    {
                        "name": "Admissible vs Consistent Heuristic",
                        "latex": r"\text{Admissible: } h(n) \le h^{*}(n) \quad | \quad \text{Consistent: } h(n) \le c(n,n') + h(n')",
                        "note": "Consistency implies admissibility; it prevents reopening of nodes.",
                    },
                    {
                        "name": "IDA*",
                        "latex": r"f_{\text{bound}} \text{ increased to the smallest exceeded value}",
                        "note": "Iterative-deepening A* uses O(d) memory instead of O(b^d).",
                    },
                    {
                        "name": "Minimax with Alpha-Beta Pruning",
                        "latex": r"\alpha \ge \beta \Rightarrow \text{cut off the branch}",
                        "note": "Ideal ordering visits about sqrt(b^d) nodes instead of b^d.",
                    },
                    {
                        "name": "Constraint Satisfaction Backtracking",
                        "latex": r"\text{Forward checking} + \text{MRV heuristic} = \text{earliest-failure ordering}",
                        "note": "Select the variable with the fewest remaining domain values.",
                    },
                ],
            },
            {
                "title": "Knowledge Representation & Logic",
                "items": [
                    {
                        "name": "Propositional Logic Connectives",
                        "latex": r"\neg, \ \wedge, \ \vee, \ \to, \ \leftrightarrow",
                        "note": "Any Boolean function can be expressed with these.",
                    },
                    {
                        "name": "First-Order Predicate Logic",
                        "latex": r"\forall x\, P(x) \to Q(x), \qquad \exists x\, [P(x) \land Q(x)]",
                        "note": "Quantifiers range over the domain of discourse.",
                    },
                    {
                        "name": "Resolution",
                        "latex": r"\frac{A \lor B \quad \neg A \lor C}{B \lor C} \quad \text{(binary resolution)}",
                        "note": "Refutation by resolution proves unsatisfiability of KB and negation of the goal.",
                    },
                    {
                        "name": "Bayes' Rule (Probabilistic Reasoning)",
                        "latex": r"P(A \mid B) = \frac{P(B \mid A) P(A)}{P(B)}",
                        "note": "Foundation of Bayesian networks and naive Bayes classifiers.",
                    },
                    {
                        "name": "Naive Bayes Classifier",
                        "latex": r"\hat{c} = \arg\max_c P(c \mid a_1 \ldots a_n) = \arg\max_c P(c) \prod_i P(a_i \mid c)",
                        "note": "Conditional independence of attributes given the class.",
                    },
                    {
                        "name": "Bayesian Network Joint Distribution",
                        "latex": r"P(x_1, \ldots, x_n) = \prod_{i=1}^{n} P(x_i \mid \mathrm{Pa}(x_i))",
                        "note": "Compact representation of a joint distribution over a DAG.",
                    },
                ],
            },
            {
                "title": "Learning & Decision Trees",
                "items": [
                    {
                        "name": "ID3 Information Gain",
                        "latex": r"\text{Entropy}(S) = -\sum_{i} p_i \log_2 p_i, \qquad \text{Gain}(S, A) = \text{Entropy}(S) - \sum \frac{|S_v|}{|S|}\text{Entropy}(S_v)",
                        "note": "C4.5 uses gain ratio to penalise attributes with many values.",
                    },
                    {
                        "name": "Gini Index",
                        "latex": r"\text{Gini} = 1 - \sum_i p_i^2, \qquad \Delta\text{Gini} = \text{Gini(parent)} - \sum \frac{|S_v|}{|S|} \text{Gini}(S_v)",
                        "note": "CART splits on the attribute with the highest Gini decrease.",
                    },
                    {
                        "name": "Gain Ratio",
                        "latex": r"\text{GainRatio}(A) = \frac{\text{Gain}(S, A)}{\text{SplitInfo}(A)}",
                        "note": "Corrects the bias of information gain towards attributes with high cardinality.",
                    },
                    {
                        "name": "Inductive Bias in Decision Trees",
                        "latex": r"\text{Prefer smaller trees and attributes with fewer values}",
                        "note": "Unbiased trees grow very large and overfit.",
                    },
                    {
                        "name": "Overfitting",
                        "latex": r"\text{Training error low, test error high} \Rightarrow \text{overfitting}",
                        "note": "Controlled by pruning, early stopping and regularisation.",
                    },
                ],
            },
            {
                "title": "Neural Networks",
                "items": [
                    {
                        "name": "Perceptron Learning Rule",
                        "latex": r"w_{i}^{new} = w_i + \alpha (y - y') x_i",
                        "note": "Online, single-sample update for a linear threshold unit.",
                    },
                    {
                        "name": "Delta / LMS Rule",
                        "latex": r"w = w + \alpha (t - y) \phi",
                        "note": "Least mean squares; y is the network output.",
                    },
                    {
                        "name": "Sigmoid Activation",
                        "latex": r"\sigma(s) = \frac{1}{1 + e^{-s}}, \qquad \sigma'(s) = \sigma(s)\big(1 - \sigma(s)\big)",
                        "note": "Output lies in (0,1), which suits probability outputs.",
                    },
                    {
                        "name": "Backpropagation Weight Update",
                        "latex": r"\Delta w_{ji} = \eta\, \delta_j\, x_i, \qquad \delta_j = \frac{\partial E}{\partial y_j} = f'(y_j) \sum_k \delta_k w_{jk}",
                        "note": "Error is propagated backwards and the weights are adjusted to reduce it.",
                    },
                    {
                        "name": "Generalisation Error",
                        "latex": r"E_{gen} \approx E_{train} + \text{bias}^2 + \text{variance} + \sigma^2",
                        "note": "Overfitting raises the variance term.",
                    },
                    {
                        "name": "Cross-Validation",
                        "latex": r"\text{k-fold}: \text{repeat } k \text{ times, train on } k-1 \text{ folds, test on the remaining one}",
                        "note": "Uses every sample for both training and testing exactly once.",
                    },
                ],
            },
            {
                "title": "Reinforcement Learning & Genetic Algorithms",
                "items": [
                    {
                        "name": "Q-Value Update",
                        "latex": r"Q(s, a) \leftarrow Q(s, a) + \alpha [R + \gamma \max_{a'} Q(s', a') - Q(s, a)]",
                        "note": "Temporal-difference error with discount factor gamma.",
                    },
                    {
                        "name": "Exploration vs Exploitation",
                        "latex": r"\varepsilon\text{-greedy}: \text{explore with probability } \varepsilon",
                        "note": "The explore/exploit dilemma in action selection.",
                    },
                    {
                        "name": "Genetic Algorithm Operators",
                        "latex": r"\text{Selection} \to \text{Crossover} \to \text{Mutation} \to \text{Evaluation}",
                        "note": "Crossover exchanges gene segments; mutation perturbs one gene.",
                    },
                    {
                        "name": "Fitness-Proportionate Selection",
                        "latex": r"P_i = \frac{f_i}{\sum_j f_j}",
                        "note": "Roulette wheel selection; higher fitness means a larger share.",
                    },
                    {
                        "name": "Markov Decision Process",
                        "latex": r"M = (S, A, P, R, \gamma)",
                        "note": "The formal tuple describing a reinforcement learning problem.",
                    },
                ],
            },
        ],
    },
    "data-mining": {
        "name": "Data Mining & Warehousing",
        "icon": "\U0001f5c3",
        "colour": "#0d9488",
        "topics": [
            {
                "title": "Association Rule Mining",
                "items": [
                    {
                        "name": "Support of a Rule",
                        "latex": r"\text{support}(A \to B) = P(A \cup B)",
                        "note": "Fraction of transactions containing both A and B.",
                    },
                    {
                        "name": "Confidence of a Rule",
                        "latex": r"\text{confidence}(A \to B) = P(B \mid A) = \frac{\text{support}(A \cup B)}{\text{support}(A)}",
                        "note": "Conditional probability of B given A.",
                    },
                    {
                        "name": "Lift",
                        "latex": r"\text{lift}(A \to B) = \frac{\text{confidence}(A \to B)}{P(B)} = \frac{\text{support}(A \cup B)}{\text{support}(A)\,\text{support}(B)}",
                        "note": "Lift > 1 means positive correlation, = 1 independence, < 1 negative.",
                    },
                    {
                        "name": "Leverage and Conviction",
                        "latex": r"\text{leverage} = \text{support}(A \cup B) - \text{support}(A)\text{support}(B)",
                        "note": "Zero leverage indicates independence; conviction measures the strength of a rule.",
                    },
                    {
                        "name": "Apriori Algorithm",
                        "latex": r"\text{Frequent} \Rightarrow \text{all subsets frequent (downward closure)}",
                        "note": "Prunes candidates whose subset is infrequent.",
                    },
                    {
                        "name": "Apriori Candidate Generation",
                        "latex": r"L_{k+1} = \{ L_1 \cup L_2 \mid L_1, L_2 \in L_k,\ |L_1 \cap L_2| = k-1 \}",
                        "note": "Frequent (k+1)-itemsets come from merging frequent k-itemsets.",
                    },
                    {
                        "name": "FP-Growth",
                        "latex": r"\text{Build a frequent-pattern tree} \Rightarrow \text{conditional pattern bases} \Rightarrow \text{no candidate generation}",
                        "note": "Faster than Apriori because it avoids the repeated database scans.",
                    },
                ],
            },
            {
                "title": "Classification & Evaluation",
                "items": [
                    {
                        "name": "Precision and Recall",
                        "latex": r"\text{Precision} = \frac{TP}{TP + FP}, \qquad \text{Recall} = \frac{TP}{TP + FN}",
                        "note": "F-measure: harmonic mean of the two.",
                    },
                    {
                        "name": "F1 Score",
                        "latex": r"F_1 = 2 \cdot \frac{P \cdot R}{P + R} = \frac{2TP}{2TP + FP + FN}",
                        "note": "High only when both precision and recall are high.",
                    },
                    {
                        "name": "Accuracy",
                        "latex": r"\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}",
                        "note": "Misleading on imbalanced classes.",
                    },
                    {
                        "name": "Confusion Matrix",
                        "latex": r"\begin{pmatrix} TP & FP \\ FN & TN \end{pmatrix}",
                        "note": "Rows are actual, columns predicted.",
                    },
                ],
            },
            {
                "title": "Clustering",
                "items": [
                    {
                        "name": "K-Means Objective",
                        "latex": r"J = \sum_{i=1}^{n} \sum_{j=1}^{k} \|x_i - \mu_j\|^2, \qquad \mu_j = \frac{1}{|C_j|}\sum_{x_i \in C_j} x_i",
                        "note": "Minimise within-cluster sum of squares.",
                    },
                    {
                        "name": "K-Means Convergence",
                        "latex": r"\text{Complexity: } O(n k t) \text{ for } n \text{ points, } k \text{ clusters, } t \text{ iterations}",
                        "note": "Sensitive to initial centres and to outliers.",
                    },
                    {
                        "name": "Distance Measures",
                        "latex": r"\text{Euclidean} = \sqrt{\sum (x_i - y_i)^2}, \quad \text{Manhattan} = \sum |x_i - y_i|, \quad \text{Cosine} = \frac{x \cdot y}{\|x\|\|y\|}",
                        "note": "Cosine suits text and high-dimensional sparse data.",
                    },
                    {
                        "name": "K-Medoids",
                        "latex": r"\text{Use actual data points as medoids} \Rightarrow \text{robust to noise}",
                        "note": "PAM algorithm, k-medoids objective with Manhattan distance.",
                    },
                ],
            },
            {
                "title": "Data Warehousing & OLAP",
                "items": [
                    {
                        "name": "Data Warehouse Characteristics",
                        "latex": r"\text{Subject-oriented, Integrated, Non-volatile, Time-variant}",
                        "note": "The four defining properties of a warehouse.",
                    },
                    {
                        "name": "OLTP vs OLAP",
                        "latex": r"\text{OLTP: many short transactions, normalised} \quad | \quad \text{OLAP: few long queries, multidimensional}",
                        "note": "Normalisation is used in OLTP but star schemas in OLAP.",
                    },
                    {
                        "name": "Fact vs Dimension Tables",
                        "latex": r"\text{Fact table holds measures and is the centre of the star; dimension tables give the descriptive axes}",
                        "note": "The snowflake schema normalises the dimension tables further.",
                    },
                    {
                        "name": "OLAP Operations",
                        "latex": r"\text{Roll-up, Drill-down, Slice, Dice, Pivot}",
                        "note": "Roll-up aggregates up, drill-down decomposes.",
                    },
                    {
                        "name": "ETL",
                        "latex": r"\text{Extract} \to \text{Transform} \to \text{Load}",
                        "note": "Cleaning, integration, aggregation and derivation happen in Transform.",
                    },
                ],
            },
        ],
    },
    "computer-graphics": {
        "name": "Computer Graphics",
        "icon": "\U0001f3a8",
        "colour": "#db2777",
        "topics": [
            {
                "title": "Transformations",
                "items": [
                    {
                        "name": "Translation",
                        "latex": r"x' = x + T_x, \quad y' = y + T_y, \quad z' = z + T_z",
                        "note": "Matrix form: a 4x4 identity with the translation in the last column.",
                    },
                    {
                        "name": "2D Rotation",
                        "latex": r"\begin{pmatrix} x' \\ y' \end{pmatrix} = \begin{pmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{pmatrix} \begin{pmatrix} x \\ y \end{pmatrix}",
                        "note": "Rotation is about the origin unless translated to the pivot first.",
                    },
                    {
                        "name": "Scaling",
                        "latex": r"x' = S_x \cdot x, \quad y' = S_y \cdot y",
                        "note": "S = -1 reflects; uniform scaling preserves the shape.",
                    },
                    {
                        "name": "Shearing",
                        "latex": r"\begin{pmatrix} 1 & sh_x \\ sh_y & 1 \end{pmatrix}",
                        "note": "Slants the figure along one axis.",
                    },
                    {
                        "name": "Composite 2D Transformation Matrix",
                        "latex": r"M = T \cdot R \cdot S",
                        "note": "Column-vector convention applies transformations right to left.",
                    },
                    {
                        "name": "Homogeneous 3D Rotation about Z",
                        "latex": r"\begin{pmatrix} \cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1 \end{pmatrix}",
                        "note": "About Y and X use the analogous matrices.",
                    },
                ],
            },
            {
                "title": "Line & Polygon Filling",
                "items": [
                    {
                        "name": "Bresenham's Line Algorithm",
                        "latex": r"D = 2\Delta y - \Delta x, \qquad D \ge 0 \Rightarrow y \leftarrow y + 1, \ D \leftarrow D + 2\Delta y - 2\Delta x",
                        "note": "Only integer additions; no multiplication or division per pixel.",
                    },
                    {
                        "name": "Midpoint Circle Algorithm",
                        "latex": r"D = 4(x^2 + y^2) - 4a x - 1; \quad D < 0 \Rightarrow D \leftarrow D + 8y + 4, \text{ else } D \leftarrow D + 8y - 8x + 12",
                        "note": "Plots an octant and reflects the rest.",
                    },
                    {
                        "name": "Cohen-Sutherland Line Clipping",
                        "latex": r"\text{Outcode} = \text{concatenation of four out bits (L,R,B,T)}",
                        "note": "AND of the endpoints is nonzero for trivial rejection; OR is nonzero for trivial acceptance.",
                    },
                    {
                        "name": "Liang-Barsky Parametric Clipping",
                        "latex": r"p_0 = -x_0 - x_{min}, \quad p_1 = x_1 - x_{max}, \quad p_2 = -y_0 - y_{min}, \quad p_3 = y_1 - y_{max}",
                        "note": "Computes the parameter t_entry and t_exit.",
                    },
                    {
                        "name": "Scanline Polygon Fill",
                        "latex": r"\text{For each scanline } y, \text{ find intersections, sort, fill alternate spans (even-odd rule)}",
                        "note": "Handles concavity correctly; use the nonzero rule for holes.",
                    },
                ],
            },
            {
                "title": "Projection & Clipping",
                "items": [
                    {
                        "name": "Perspective Projection",
                        "latex": r"x' = \frac{x}{z}, \quad y' = \frac{y}{z}",
                        "note": "Weak perspective divides by z; the true perspective maps to x/z, y/z, z.",
                    },
                    {
                        "name": "Field of View",
                        "latex": r"\alpha = 2 \arctan \left(\frac{h}{2f}\right) \quad (\text{vertical})",
                        "note": "f is the focal length of the lens.",
                    },
                    {
                        "name": "Viewing Transformation",
                        "latex": r"M_{view} = T(-C) \cdot R \cdot T(-D)",
                        "note": "Maps world coordinates into the camera coordinate system.",
                    },
                    {
                        "name": "Near and Far Clipping Planes",
                        "latex": r"-1 \le z \le 1 \text{ in the normalised device coordinate range}",
                        "note": "Anything outside is discarded before rasterisation.",
                    },
                ],
            },
            {
                "title": "Hidden Surface Removal",
                "items": [
                    {
                        "name": "Z-Buffer Algorithm",
                        "latex": r"\text{If } z_{buffer}(x, y) > z_{pixel} \text{ then } z_{buffer} \leftarrow z_{pixel} \text{ and write the colour}",
                        "note": "Works for any polygon, resolution is proportional to pixel count.",
                    },
                    {
                        "name": "Polygon Area (Shoelace Formula)",
                        "latex": r"A = \frac{1}{2} \left| \sum_{i=0}^{n-1} (x_i y_{i+1} - x_{i+1} y_i) \right|",
                        "note": "Shoelace formula for simple polygons.",
                    },
                    {
                        "name": "Flood Fill",
                        "latex": r"\text{4-connected} \Rightarrow \text{cross neighbours}, \qquad \text{8-connected} \Rightarrow \text{cross + diagonal}",
                        "note": "Used for region filling after boundary detection.",
                    },
                ],
            },
        ],
    },
    "paper-one": {
        "name": "General Aptitude & Reasoning",
        "icon": "\U0001f9e0",
        "colour": "#4f46e5",
        "topics": [
            {
                "title": "Quantitative Aptitude",
                "items": [
                    {
                        "name": "Average",
                        "latex": r"\bar{x} = \frac{\sum x_i}{n}, \qquad \text{if } p \text{ values are } a \text{ and the rest are } b: \ \bar{x} = \frac{pa + (n-p)b}{n}",
                        "note": "Weighted average replaces values, it does not add to them.",
                    },
                    {
                        "name": "Ratio and Proportion",
                        "latex": r"\frac{a}{b} = \frac{k a'}{k b'}, \qquad a : b = c : d \Rightarrow ad = bc",
                        "note": "Alligation for mixing two ratios in given proportions.",
                    },
                    {
                        "name": "Percentage Change",
                        "latex": r"\Delta\% = \frac{\text{new} - \text{old}}{\text{old}} \times 100",
                        "note": "Successive percentage changes multiply, they do not add.",
                    },
                    {
                        "name": "Simple Interest",
                        "latex": r"SI = \frac{P \cdot R \cdot T}{100}, \qquad CI = P\left[\left(1 + \frac{R}{100}\right)^{T} - 1\right]",
                        "note": "On compound interest, the difference is always the interest on interest.",
                    },
                    {
                        "name": "Profit and Loss",
                        "latex": r"\text{Profit \%} = \frac{\text{SP} - \text{CP}}{\text{CP}} \times 100",
                        "note": "Successive percentage profit compounds multiplicatively.",
                    },
                    {
                        "name": "Time and Work",
                        "latex": r"\text{If } A \text{ does work in } a \text{ days, rate} = \frac{1}{a}; \quad \text{together: rate} = \frac{1}{a} + \frac{1}{b}",
                        "note": "Time together = ab / (a + b).",
                    },
                    {
                        "name": "Speed, Distance and Time",
                        "latex": r"S = \left(\frac{d_1}{t_1} + \frac{d_2}{t_2}\right) \cdot \frac{t_1 t_2}{t_1 + t_2}",
                        "note": "Average speed is total distance over total time, not the mean of the speeds.",
                    },
                    {
                        "name": "Area, Perimeter and Circumference",
                        "latex": r"\text{Circle: } A = \pi r^2, \ C = 2\pi r; \quad \text{Triangle: } A = \frac{1}{2} b h; \quad \text{Square: } A = s^2",
                        "note": "Perimeter of a triangle satisfies P = 2s.",
                    },
                ],
            },
            {
                "title": "Logical Reasoning",
                "items": [
                    {
                        "name": "Syllogism Rule",
                        "latex": r"A \to B, \ B \to C \Rightarrow A \to C \quad \text{(transitive)}",
                        "note": "The most frequent reasoning pattern in Paper I.",
                    },
                    {
                        "name": "Venn Diagram Region Counting",
                        "latex": r"|A \cup B| = |A| + |B| - |A \cap B|",
                        "note": "Apply inclusion-exclusion to the two-set questions.",
                    },
                    {
                        "name": "Number Series",
                        "latex": r"2, 6, 12, 20, 30 \Rightarrow a_n = n(n+1)",
                        "note": "Identify n^2, n(n+1), n^2 + n patterns first.",
                    },
                    {
                        "name": "Letter Series / Coding",
                        "latex": r"x \to x + k, \quad k \text{ is constant or follows its own series}",
                        "note": "Check for alternating patterns before assuming a constant step.",
                    },
                    {
                        "name": "Ranking and Ordering",
                        "latex": r"\text{If } A > B \text{ and } C > B, \text{ only the relative order of A and C is undetermined}",
                        "note": "Avoid assuming transitivity where none is given.",
                    },
                ],
            },
            {
                "title": "Data Interpretation",
                "items": [
                    {
                        "name": "Data Interpretation Charts",
                        "latex": r"\text{Bar, Pie, Line, Table, Pie-of-Pie, Area, Scatter}",
                        "note": "Read the axis values and compute the required difference or ratio.",
                    },
                    {
                        "name": "Growth Rate",
                        "latex": r"\text{Growth} = \left(\frac{v_{new} - v_{old}}{v_{old}}\right) \times 100\%",
                        "note": "Compound growth over n periods: V(1 + r)^n.",
                    },
                    {
                        "name": "Pie Chart Angle",
                        "latex": r"\theta = \frac{\text{value}}{\text{total}} \times 360^\circ",
                        "note": "Ratio comparisons are usually simpler than angle computations.",
                    },
                ],
            },
            {
                "title": "Communication, Research & Teaching Aptitude",
                "items": [
                    {
                        "name": "Types of Communication",
                        "latex": r"\text{Verbal, Non-verbal, Written, Oral, Formal, Informal}",
                        "note": "Feedback closes the communication loop.",
                    },
                    {
                        "name": "Communication Barriers",
                        "latex": r"\text{Semantic, Physical, Psychological, Cultural, Organisational}",
                        "note": "Noise can be internal, external or physiological.",
                    },
                    {
                        "name": "Research Design Steps",
                        "latex": r"\text{Problem} \to \text{Literature} \to \text{Hypothesis} \to \text{Design} \to \text{Data collection} \to \text{Analysis} \to \text{Report}",
                        "note": "Sampling must match the design.",
                    },
                    {
                        "name": "Levels of Measurement",
                        "latex": r"\text{Nominal} < \text{Ordinal} < \text{Interval} < \text{Ratio}",
                        "note": "Only ratio scales have a meaningful absolute zero.",
                    },
                    {
                        "name": "Tests of Significance",
                        "latex": r"\text{H}_0: \mu = \mu_0 \text{ vs } H_1: \mu \ne \mu_0; \qquad \alpha = \text{significance level}",
                        "note": "Reject H0 when the p-value is below alpha.",
                    },
                    {
                        "name": "Bloom's Taxonomy",
                        "latex": r"\text{Knowledge} \to \text{Comprehension} \to \text{Application} \to \text{Analysis} \to \text{Synthesis} \to \text{Evaluation}",
                        "note": "Revised 2001 version renames the top levels.",
                    },
                    {
                        "name": "Validity and Reliability",
                        "latex": r"\text{Content, Construct, Criterion validity}; \qquad \text{Test-retest, Inter-rater, Internal consistency}",
                        "note": "Reliability is a necessary but not sufficient condition for validity.",
                    },
                    {
                        "name": "Teaching Methods",
                        "latex": r"\text{Lecture, Discussion, Demonstration, Problem solving, Seminars, Team teaching, Brainstorming}",
                        "note": "Each suits a different learning objective level.",
                    },
                ],
            },
            {
                "title": "ICT, Environment & Higher Education",
                "items": [
                    {
                        "name": "ICT Abbreviations",
                        "latex": r"\text{LAN, WAN, MAN, USB, HTTP, URL, IP, DNS, SMTP, PDF, WWW}",
                        "note": "An extranet gives controlled intranet access to external partners.",
                    },
                    {
                        "name": "Number System of a Computer",
                        "latex": r"\text{Binary (2), Octal (8), Decimal (10), Hexadecimal (16)}",
                        "note": "One byte = 8 bits; one nibble = 4 bits.",
                    },
                    {
                        "name": "Sustainable Development (Brundtland)",
                        "latex": r"\text{Development that meets present needs without compromising the ability of future generations to meet theirs}",
                        "note": "Report of the 1987 Brundtland Commission.",
                    },
                    {
                        "name": "Greenhouse Gases",
                        "latex": r"\text{CO}_2, \ \text{CH}_4, \ \text{N}_2\text{O}, \ \text{CFCs}, \ \text{H}_2\text{O}",
                        "note": "CO2 and methane drive the greenhouse effect.",
                    },
                    {
                        "name": "Biodiversity Hotspots",
                        "latex": r"\text{Criteria: at least 1500 endemic vascular plants and 70\% habitat loss}",
                        "note": "India has four hotspots.",
                    },
                    {
                        "name": "UGC / Regulatory Bodies",
                        "latex": r"\text{UGC, AICTE, UPTU, NCTE, NAAC, NBA}",
                        "note": "UGC coordinates standards in higher education.",
                    },
                    {
                        "name": "NEP 2020 Pillars",
                        "latex": r"\text{Academic freedom, Autonomy, Multidisciplinary education, Board exams, Teacher quality, Accreditation}",
                        "note": "Emphasises holistic and multidisciplinary education.",
                    },
                ],
            },
        ],
    },
}


# Each pattern lists the subject keys it covers. A subject key that appears in
# several patterns is rendered once per pattern, so no formula is ever missed.
PATTERNS = [
    {
        "slug": "gate",
        "name": "GATE Pattern",
        "short": "GATE",
        "description": (
            "GATE Computer Science and Applications question paper. The seven core "
            "units plus Engineering Mathematics and General Aptitude."
        ),
        "subjects": [
            "engineering-mathematics",
            "digital-logic-coa",
            "programming",
            "dsa",
            "dbms",
            "operating-systems",
            "toc-compiler",
            "networks",
            "software-engineering",
            "ai-ml",
            "data-mining",
            "computer-graphics",
            "paper-one",
        ],
    },
    {
        "slug": "ugc-net",
        "name": "UGC NET Pattern",
        "short": "UGC NET",
        "description": (
            "UGC NET Computer Science paper I (general aptitude) plus paper II "
            "(computer science and applications)."
        ),
        "subjects": [
            "paper-one",
            "engineering-mathematics",
            "digital-logic-coa",
            "programming",
            "dsa",
            "dbms",
            "operating-systems",
            "toc-compiler",
            "networks",
            "software-engineering",
            "ai-ml",
            "data-mining",
            "computer-graphics",
        ],
    },
    {
        "slug": "ts-set",
        "name": "TS SET Pattern",
        "short": "TS SET",
        "description": (
            "TS SET Computer Science and Applications paper: mathematics, core "
            "computer science units and general studies."
        ),
        "subjects": [
            "engineering-mathematics",
            "digital-logic-coa",
            "programming",
            "dbms",
            "operating-systems",
            "toc-compiler",
            "networks",
            "software-engineering",
            "ai-ml",
            "dsa",
            "data-mining",
            "computer-graphics",
            "paper-one",
        ],
    },
]


def build_formula_payload():
    """Return the pattern list with every subject fully expanded.

    Each subject is a plain dict copy so templates and the JSON endpoint never
    mutate the shared library.
    """
    payload = []
    for pattern in PATTERNS:
        subjects = []
        for key in pattern["subjects"]:
            source = SUBJECT_LIBRARY.get(key)
            if source is None:
                continue
            subjects.append(
                {
                    "key": key,
                    "name": source["name"],
                    "icon": source.get("icon", ""),
                    "colour": source.get("colour", "#4f46e5"),
                    "topic_count": len(source["topics"]),
                    "formula_count": sum(
                        len(topic["items"]) for topic in source["topics"]
                    ),
                    "topics": [
                        {
                            "title": topic["title"],
                            "items": [dict(item) for item in topic["items"]],
                        }
                        for topic in source["topics"]
                    ],
                }
            )
        payload.append(
            {
                "slug": pattern["slug"],
                "name": pattern["name"],
                "short": pattern["short"],
                "description": pattern["description"],
                "subjects": subjects,
                "formula_count": sum(
                    len(topic["items"]) for subject in subjects for topic in subject["topics"]
                ),
            }
        )
    return payload


def formula_totals():
    """Return (patterns, subjects, formulas) counts for the catalogue."""
    patterns = len(PATTERNS)
    subjects = len({key for pattern in PATTERNS for key in pattern["subjects"]})
    formulas = sum(
        len(topic["items"]) for subject in SUBJECT_LIBRARY.values() for topic in subject["topics"]
    )
    return patterns, subjects, formulas
