# Statement: thm:linear-exact (T10c thm:linear-exact (J6))

This is the exact statement to be proved independently. Do not consult any other file except definition1.md, assumptions.md and notation.md in this directory.

```latex
\begin{theorem}[Exact optimality within the greedy query budget]
\label{thm:linear-exact}\label{cor:greedybudget}
Let $K\ge2$, $\eta>1$ and $n\ge4K^{5}$, and let $\mathcal A_{\mathrm{lin}}$
be the class of deterministic algorithms that make at most $nK$ queries to
$\tilde f$, each on a set of size at most $K$, and output a set of size at
most $K$; predictive greedy, at $Kn-K(K-1)/2$ queries, belongs to
$\mathcal A_{\mathrm{lin}}$.  For every $A\in\mathcal A_{\mathrm{lin}}$
and every prescribed split $\eta_u,\eta_o\ge1$ with $\eta_u\eta_o=\eta$,
there is an instance $(f,\tilde f)$ with monotone submodular $f$, whose
smallest admissible error factors in Definition~\ref{def:eta} are exactly
$(\eta_u,\eta_o)$, on which the output $T$ satisfies
\[
  \frac{f(T)}{f(O^{\ast})}\;\le\;\rho_K(\eta).
\]
Combined with Theorem~\ref{thm:exact}, whose guarantee holds on every
instance with error at most $\eta$,
\[
  \sup_{A\in\mathcal A_{\mathrm{lin}}}\;
  \inf_{(f,\tilde f)}\;
  \frac{f(A^{\tilde f})}{f(O^{\ast})}\;=\;\rho_K(\eta):
\]
predictive greedy is exactly optimal within its own query budget, at every
such $n$, with no asymptotics in $n$ or $K$.  For every randomized
algorithm with the same budget there is again an instance with error
exactly $\eta$ on which the expectation over the algorithm's randomness
satisfies
$\mathbb E\bigl[f(T)/f(O^{\ast})\bigr]\le\rho_K(\eta)+\varepsilon_n$, where
$\varepsilon_n=K^{2}/n+K^{5}/(2n)$; for the randomized class the matching
is therefore asymptotic in $n$ at fixed $K$, and no exact finite-$n$
statement is claimed.
\end{theorem}
```
