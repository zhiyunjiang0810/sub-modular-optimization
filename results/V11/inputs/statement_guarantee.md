# Statement: prop:guarantee (T3 prop:guarantee)

This is the exact statement to be proved independently. Do not consult any other file except definition1.md, assumptions.md and notation.md in this directory.

```latex
\begin{proposition}[Guarantee of predictive greedy]\label{prop:guarantee}
Let $f$ be monotone submodular with $f(\emptyset)=0$ and let $T=S^{K}$ be the
output of a run of predictive greedy whose selection error is $\etasel$
(Definition~\ref{def:etasel}, with $L_K(\infty)=0$).
Then, with $L_K(x)=1-(1-\tfrac1{xK})^{K}$,
\[
  f(T)\;\ge\;L_K(\etasel)\,f(O^{\ast})
  \;\ge\;\bigl(1-e^{-1/\etasel}\bigr)f(O^{\ast}).
\]
If moreover the predictor has finite error $(\eta_u,\eta_o)$, the same bound
holds with $\etasel$ replaced by $\etatr$ or by $\eta$, and the three bounds
are ordered $L_K(\etasel)\ge L_K(\etatr)\ge L_K(\eta)$.
\end{proposition}
```
