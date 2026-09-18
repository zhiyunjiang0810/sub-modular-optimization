# Statement: lem:coherence (T5 lem:coherence)

This is the exact statement to be proved independently. Do not consult any other file except definition1.md, assumptions.md and notation.md in this directory.

```latex
\begin{lemma}[Coherence]\label{lem:coherence}
Let $f$ be monotone, $S\subseteq N$, $e,e'\notin S$, and suppose
$\tilde d_{e}(S)\ge\tilde d_{e'}(S)$.  Then
\[
  \text{(i)}\;\; d_{e}(S\cup\{e'\})\ge\tfrac1\eta\,d_{e'}(S\cup\{e\}),
  \qquad
  \text{(ii)}\;\;\bigl(1-\tfrac1\eta\bigr)\,d_{e'}(S\cup\{e\})
  \ge d_{e'}(S)-d_{e}(S).
\]
\end{lemma}
```
