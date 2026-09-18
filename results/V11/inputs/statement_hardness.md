# Statement: thm:hardness (T10 thm:hardness)

This is the exact statement to be proved independently. Do not consult any other file except definition1.md, assumptions.md and notation.md in this directory.

```latex
\begin{theorem}[Bounded-query hardness, deterministic]\label{thm:hardness}
Let $c\ge0$ be real and put $\tau=\lceil c\rceil+1$, which equals $c+1$ at
integer $c$.  Let the integers
$K>\tau$ and $n\ge4K^{c+2}$ and the real $\eta>1$ with
$\eta\ge\tfrac{K-1}{K-\tau}$ be fixed, so that $\bar\theta\ge1$.  For every
deterministic algorithm making at most $n^{c}$ queries to $\tilde f$, each on
a set of size at most $K$, there is an instance $(f,\tilde f)$ with monotone
submodular $f$, whose smallest admissible error factors in
Definition~\ref{def:eta} have product exactly $\eta$, on which the output $T$
(of size at most $K$) satisfies
\[
  \frac{f(T)}{f(O^{\ast})}\;\le\;
  H_{K,\tau}(\eta)\;:=\;
  1-\Bigl(1-\frac{1}{\eta(K-\tau)+1}\Bigr)^{K}\;=\;L_K(\bar\theta).
\]
Any prescribed split $\eta_u\eta_o=\eta$ of that error is realized by the
rescaling of Appendix~\ref{app:hardness}.  For randomized algorithms the same
bound holds in expectation up to an additive
\[
  \varepsilon_n=\frac Kn+\frac{K^{2\tau+2}}{(\tau+1)!\,n^{\tau+1-c}},
\]
which for integer $c$ reads $\tfrac Kn+\tfrac{K^{2c+4}}{(c+2)!\,n^{2}}$.  As
$K\to\infty$ with $\tau$ and $\theta$ fixed, $K\delta(\theta)\to\tau-1/\theta$;
with $c$ and $\eta$ fixed, $H_{K,\tau}(\eta)\to1-e^{-1/\eta}$.
\end{theorem}
```
