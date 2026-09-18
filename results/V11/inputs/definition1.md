# Definition 1 (prediction error), verbatim from the paper

```latex
\begin{definition}[Prediction error]\label{def:eta}
For $\eta_u,\eta_o\ge1$ the predictor $\tilde f$ has (single-element,
multiplicative) error at most $(\eta_u,\eta_o)$ if for every $S\subseteq N$
and $e\notin S$,
\[
  d_e(S)/\eta_u\;\le\;\tilde d_e(S)\;\le\;\eta_o\,d_e(S).
\]
In particular $d_e(S)=0$ forces $\tilde d_e(S)=0$, and all predicted gains are
nonnegative.  The scalar error is $\eta=\eta_u\eta_o$.
\end{definition}
```

# Definition (selection error), verbatim

```latex
\begin{definition}[Selection error]\label{def:etasel}
For an execution of predictive greedy with states
$S^{0},\dots,S^{K-1}$ and picks $e_{0},\dots,e_{K-1}$, write
$M_t=\max_{e\notin S^{t}} d_{e}(S^{t})$ and $g_t=d_{e_t}(S^{t})$
(monotonicity of $f$ gives $g_t\ge0$), and set
\[
  a_t\;=\;\begin{cases}
    M_t/g_t, & g_t>0,\\
    1, & M_t=g_t=0,\\
    \infty, & g_t=0<M_t .
  \end{cases}
  \qquad
  \etasel\;=\;\max\{1,a_0,\dots,a_{K-1}\},
\]
the largest factor by which a step of the run fell short of the best true
gain; a step whose chosen true gain vanishes while a better candidate
exists makes the selection error infinite.  Bounds evaluated at
$\etasel$ use the convention $L_K(\infty)=0$.  In the terminology of
Goundan and Schulz, a run with finite $\etasel$ is an execution of greedy
with an $\alpha$-approximate incremental oracle with $\alpha=\etasel$;
their condition is a per-step condition, which is what the case
$a_t=\infty$ records \citep{goundan2007revisiting}.
\end{definition}
```

# Definition 1, convention B ("方案二", the settled convention; HANDOFF_2026-09-18 section 3)

For $\eta_u,\eta_o>0$ with $\eta=\eta_u\eta_o\ge1$, the surrogate $\tilde f$ has marginal-gain error $(\eta_u,\eta_o)$ if for all $S\subseteq N$ and $e\notin S$: $d_e(S)/\eta_u\le\tilde d_e(S)\le\eta_o\,d_e(S)$. Scaling: multiplying $\tilde f$ by $c>0$ maps $(\eta_u,\eta_o)\to(c\eta_u,\eta_o/c)$ and leaves $\eta$ unchanged; $\tilde f=cf$ has $\eta=1$. The two factors are the two sides of the band; no result depends on the split and every statement uses only $\eta$. The definition forces $\tilde d_e(S)=0$ exactly when $d_e(S)=0$.

Relation to the verbatim text above: the paper text currently floors both factors at 1; under convention B a predictor with factors $(\eta_u,\eta_o)$, $\eta_u<1$, is the same object as the rescaled predictor with factors $(1,\eta)$. Class statements over $\eta$ are unaffected; prop:valueacc (ii)(iii) are stated under convention B.
