# Statement: thm:exact (T6 thm:exact)

This is the exact statement to be proved independently. Do not consult any other file except definition1.md, assumptions.md and notation.md in this directory.

```latex
\begin{theorem}[Exact worst-case ratio of predictive greedy]\label{thm:exact}
For every $K\ge2$ and $\eta\ge1$, under adversarial tie breaking,
\[
  \rho_K(\eta)\;=\;\min_{0\le j\le K-1}V_j(\eta),
\]
and the minimum is attained by $V_j$ on the segment
$\eta\in[K-j,K-j+1]$ (with $V_0=1/\eta$ on $[K,\infty)$), so the breakpoints
are the integers $2,\dots,K$.  In particular
$\rho_K(\eta)=1/\eta$ exactly when $\eta\ge K$, and for $K\in\{2,3,4\}$ the
closed forms are
$\rho_2=\min\{\tfrac1\eta,\tfrac{3}{2(\eta+1)}\}$,
$\rho_3=\tfrac{16\eta+3}{3(2\eta+1)^2}$, $\tfrac{7}{3(2\eta+1)}$,
$\tfrac1\eta$ on $[1,2],[2,3],[3,\infty)$, and
$\rho_4=\tfrac{135\eta^2+36\eta+4}{4(3\eta+1)^3}$,
$\tfrac{21\eta+2}{2(3\eta+1)^2}$, $\tfrac{13}{4(3\eta+1)}$, $\tfrac1\eta$ on
$[1,2],[2,3],[3,4],[4,\infty)$.
\end{theorem}
```
