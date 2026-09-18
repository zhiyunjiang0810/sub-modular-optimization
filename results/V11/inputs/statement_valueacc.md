# Statement: prop:valueacc (T2, convention B rewrite of 2026-09-18)

This is the exact statement to be proved independently. Do not consult any other file except definition1.md, assumptions.md and notation.md in this directory. Use the convention-B Definition 1 (factors eta_u, eta_o > 0 without floors).


Convention B of Definition 1: $\eta_u,\eta_o>0$, $\eta=\eta_u\eta_o\ge1$, and for all $S$ and $e\notin S$:
$d_e(S)/\eta_u\le\tilde d_e(S)\le\eta_o\,d_e(S)$ (so $d_e(S)=0$ forces $\tilde d_e(S)=0$).
Value accuracy at level $\varepsilon\in(0,1)$ (Hassidim--Singer): $(1-\varepsilon)f(S)\le\tilde f(S)\le(1+\varepsilon)f(S)$ for every $S$.

**Proposition (Value accuracy is neither sufficient nor necessary for predictive greedy).**
(i) For every $\varepsilon\in(0,1)$ there are a monotone submodular $f$ with $f(\emptyset)=0$ and a
predictor $\tilde f$ with $\tilde f(\emptyset)=0$, value-accurate at level $\varepsilon$, with
$\tilde d_e(S)=0$ at a pair $(S,e)$ where $d_e(S)>0$; hence no finite $(\eta_u,\eta_o)$ of Definition 1
exists for $\tilde f$, and no bound of the form $L_K(\eta)$ follows from value accuracy alone.
(ii) For every $M>0$ and every monotone submodular $f$ not identically zero, the predictor
$\tilde f=(1+M)f$ fails value accuracy at every level $\varepsilon<M$, yet Definition 1 holds with
$\eta_u=1/(1+M)$ and $\eta_o=1+M$, so its global error is $\eta=1$; predictive greedy on $\tilde f$
picks at every state an element of maximum true gain ($\eta^{\mathrm{sel}}=1$).
(iii) Let $\tilde f$ have error $(\eta_u,\eta_o)$ with $\eta=\eta_u\eta_o$ for a monotone $f$ with
$f(\emptyset)=\tilde f(\emptyset)=0$. Then $f(S)/\eta_u\le\tilde f(S)\le\eta_o f(S)$ for every $S$, and
with $c=2\eta_u/(\eta+1)$ and $\varepsilon=(\eta-1)/(\eta+1)\in[0,1)$ the rescaled predictor $c\tilde f$
is value-accurate at level $\varepsilon$: $(1-\varepsilon)f(S)\le c\tilde f(S)\le(1+\varepsilon)f(S)$ for
all $S$. No submodularity of $f$ is used in (iii).

