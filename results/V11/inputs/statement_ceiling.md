# Statement: thm:ceiling (T8 thm:ceiling)

This is the exact statement to be proved independently. Do not consult any other file except definition1.md, assumptions.md and notation.md in this directory.

```latex
\begin{theorem}[Deterministic ceiling, all ground-set sizes]
\label{thm:ceiling}
Let $2\le K\le n$.  For every deterministic algorithm with arbitrary query
access to $\tilde f$ and output of size at most $K$, and every
$\eta_u,\eta_o\ge1$, there is a pair $(f,\tilde f)$ with error exactly
$(\eta_u,\eta_o)$ on which the output $T$ satisfies
$f(T)\le C^{*}_{n,K}(\eta)\,f(O^{\ast})$, where
\[
  C^{*}_{n,K}(\eta)\;=\;\frac{K}{K+(\eta-1)\min\{K,\,n-K\}}
  \;=\;\begin{cases}
    \dfrac{K}{(2K-n)+(n-K)\eta}, & K\le n\le2K,\\[6pt]
    1/\eta, & n\ge2K.
  \end{cases}
\]
Conversely, a set $S$ maximizing $\tilde f$ over all $K$-subsets satisfies,
on every instance and for every optimal $K$-set $O^{\ast}$,
\[
  f(S)\;\ge\;\frac{K}{K+(\eta-1)\,|O^{\ast}\setminus S|}\,f(O^{\ast})
  \;\ge\;C^{*}_{n,K}(\eta)\,f(O^{\ast}),
\]
so exhaustive search over predicted values attains the ceiling for every
$n$.
\end{theorem}
```
