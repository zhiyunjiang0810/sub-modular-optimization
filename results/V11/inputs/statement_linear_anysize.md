# Statement: thm:linear-anysize (T10d thm:linear-anysize (J7))

This is the exact statement to be proved independently. Do not consult any other file except definition1.md, assumptions.md and notation.md in this directory.

```latex
\begin{theorem}[Arbitrary query sizes at linear budget]
\label{thm:linear-anysize}
Let $K\ge3$ and $\eta>1$, and let $\alpha_{\mathrm{lin}}(K,\eta)$ denote
the limit as $n\to\infty$ of the optimal worst-case ratio of deterministic
algorithms that make $O(nK)$ queries to $\tilde f$ \emph{of arbitrary
size} and output a set of size at most $K$, over instances with monotone
submodular $f$ and error product at most $\eta$ (randomized algorithms
measured in expectation over their own randomness).  Then
\[
  \rho_K(\eta)\;\le\;\alpha_{\mathrm{lin}}(K,\eta)\;\le\;
  \min\Bigl\{\frac1\eta,\;W_K(\eta)\Bigr\}
  \;\le\;
  \min\Bigl\{\frac1\eta,\;\rho_K(\eta)+\frac{1}{K\,\bigl(e^{K-1}-K-1\bigr)}\Bigr\},
\]
where $W_K(\eta)$ is the explicit constant of
Appendix~\ref{app:hardness-anysize}: even with arbitrary-size queries,
predictive greedy is optimal among algorithms of its own oracle
complexity up to an additive term exponentially small in $K$.  For
$\eta\ge K$ both ends equal $1/\eta$.
\end{theorem}
```
