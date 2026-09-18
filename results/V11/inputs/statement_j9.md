# Statement: J9 (deterministic, arbitrary-size queries, linear budget: exact matching value rho_K)

This statement is RECONSTRUCTED from the TASKS11 Q11 instruction wording only; the proof file
results/J9/j9_proof.md was not delivered. Do not consult any other file except definition1.md,
assumptions.md and notation.md in this directory.

**Theorem (to be proved independently).** Let $K\ge2$, $\eta>1$ and $c\ge1$. Let
$n\ge\lceil 4cK^{5}(K+2)^{2}\rceil$. For every deterministic algorithm that makes at most $cnK$ queries
to $\tilde f$, each on a set of ARBITRARY size, and outputs a set $T_0$ of size at most $K$ (an output of
size less than $K$ is completed to a $K$-set by adding arbitrary elements, which cannot decrease $f$),
and for every split $\eta_u,\eta_o>0$ with $\eta_u\eta_o=\eta$, there is an instance $(f,\tilde f)$ with
$f$ monotone submodular, $f(\emptyset)=\tilde f(\emptyset)=0$, whose smallest admissible error factors
are exactly $(\eta_u,\eta_o)$, on which
$$\frac{f(T_0)}{\mathrm{OPT}}\;\le\;\rho_K(\eta)=\min_{0\le j\le K-1}V_j(\eta),
\qquad V_j(\eta)=1-q^{j}\Bigl(1-\frac{K-j}{K\eta}\Bigr),\ q=\frac{(K-1)\eta}{(K-1)\eta+1}.$$
Two branches are expected: $1<\eta<K$ (the active segment $j=K-\lfloor\eta\rfloor\ge1$) and $\eta\ge K$
(where $\rho_K=1/\eta$). Combined with the exact guarantee of predictive greedy, the optimal worst-case
ratio of deterministic $O(nK)$-query algorithms with arbitrary-size queries equals $\rho_K(\eta)$ exactly
for every such $n$ (no $n\to\infty$ limit, no exponentially small excess).

Context you may use: a family whose surrogate is a function of $|S|$ on every set with $|S\cap O|\le1$
(all sizes) cannot achieve value below $\rho_K+$ a positive excess (the excess is forced for such
count-grid families), so an exact construction must let the surrogate depend on the hidden optimum
through something other than $|S\cap O|\le1$ alone, or must depend on the algorithm's fixed output
$T_0$ as well (the instruction names the instance $F_{T,O}$, $G_O$).
