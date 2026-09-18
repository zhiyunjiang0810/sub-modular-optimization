# Statement: J8 ProbeLottery (Proposition; K = 2, eta = 3/2)

This is the exact statement and the exact algorithm. Do not consult any other file except definition1.md, assumptions.md and notation.md in this directory.


**Proposition (ProbeLottery).** Let $K=2$ and $\eta=3/2$. There is a randomized algorithm, ProbeLottery,
that makes at most $9n$ queries to $\tilde f$, each on a set of size at most $5$, outputs a set of size
$2$, and satisfies on every instance $(f,\tilde f)$ with $f$ monotone submodular, $f(\emptyset)=0$, and
$\tilde f$ of error at most $\eta=3/2$ (Definition 1, any split with $\eta_u\eta_o=3/2$; in particular
$d_e(S)\le\tilde d_e(S)\le\tfrac32 d_e(S)$ after rescaling):
$$\mathbb E[f(T)]\;\ge\;\Bigl(\tfrac35+\tfrac{1}{400000}\Bigr)\,\mathrm{OPT},$$
the expectation over the algorithm's own randomness only. Since $\rho_2(3/2)=3/5$ is the exact worst
case of predictive greedy, this shows the query-size restriction $|S|\le K$ of the linear-budget
optimality theorem is necessary for randomized algorithms with budget $\tfrac92 nK$.
(Source: HANDOFF_2026-09-18 section 4; the proof file J8_probe_lottery.md with inequalities (3),(8)-(12)
was not delivered. On the tight $K=2,\eta=3/2$ instance the implemented algorithm attains exactly
$3/5+1/2048$.)



## The algorithm ProbeLottery (exactly as implemented in the delivered spot-check script)

Input: ground set $N$ in a fixed tie-break order (argmax returns the first maximiser), oracle
$\tilde f$ (written $g$ below), constant $\mathrm{EPS}=1/10000$. All comparisons exact.

1. Singletons: $b\in\arg\max_{e\in N} g(\{e\})$, $M=g(\{b\})$.
2. Pairs containing $b$: $c\in\arg\max_{e\ne b} g(\{b,e\})$, $p=g(\{b,c\})$; $P_0=\{b,c\}$.
3. Pool: $C=\{e\ne b:\ g(\{e\})\ge M-\mathrm{EPS}\cdot M\ \text{and}\ g(\{b,e\})\ge p-\mathrm{EPS}\cdot M\}$.
4. Extensions: $B\leftarrow[b]$; secondary list empty. Repeat up to 4 times: among $e\in C\setminus B$
   (stop if empty) pick $v\in\arg\max g(B\cup\{e\})$, append $v$ to $B$; pick
   $z_v\in\arg\max_{z\ne v} g(\{v,z\})$; append $\{v,z_v\}$ and $\{b,v\}$ to the secondary list.
   Pad the secondary list with copies of $P_0$ until it has 8 entries.
5. Output distribution: $P_0$ with probability $127/128$, and each of the 8 secondary sets with
   probability $1/1024$ (probabilities add over repeated sets). Total mass 1.

Query accounting: each distinct set is queried once (cached); the script asserts at most $9n$ queries
and maximum queried set size $5$ ($|B|\le5$).

