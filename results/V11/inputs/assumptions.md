# Model assumptions, verbatim from the paper

```latex
A ground set $N$ with $|N|=n$, a monotone submodular $f:2^{N}\to\mathbb
R_{\ge0}$ with $f(\emptyset)=0$, and a cardinality budget $K$ are fixed.  The
algorithm cannot evaluate $f$; it can only query a predictor
$\tilde f:2^{N}\to\mathbb R$ with $\tilde f(\emptyset)=0$.  Marginal gains are
written $d_e(S)=f(S\cup\{e\})-f(S)$ and
$\tilde d_e(S)=\tilde f(S\cup\{e\})-\tilde f(S)$.
Throughout, $1\le K\le n$; when $f(O^{\ast})=0$ every ratio statement is
read as holding trivially, and $K\ge1$ excludes empty runs.


```

# Predictive greedy, verbatim

```latex
Predictive greedy is the single-step greedy run on $\tilde f$: for
$t=0,\dots,K-1$ it adds an element maximizing $\tilde d_e(S^{t})$, with ties
broken adversarially in all worst-case statements.  The run always executes
exactly $K$ steps; a step whose maximum predicted gain is zero still
selects, and the cases of Definition~\ref{def:etasel} cover it.  A variant
that stops early obtains none of the guarantees below: it is limited to the
executed-steps product bound of Remark~\ref{rem:app-product}, and a
two-element instance drives it to ratio $1/2$ against $L_2(1)=3/4$.
Its exact worst-case ratio
at error level $\eta$ is written $\rho_K(\eta)$.
```

Conventions: ratios alpha in (0,1] with F_ALG >= alpha F_OPT (larger is better); O* denotes an optimal K-set; adversarial tie-breaking in all worst-case statements; the run always executes exactly K steps.
