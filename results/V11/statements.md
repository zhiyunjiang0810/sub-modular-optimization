# V11 statements (Q0)

来源规则：正文陈述逐字取自 paper/sections/results.tex 的环境（去掉 % 注释行）；
台账陈述逐字取自 THEOREM_LEDGER.md 对应卡的"陈述"条目。矩阵的 A 项比对二者的量词。
输入送达与缺失情况见 MISSING_INPUTS.md（J8 算法由 spot-check 脚本给出，证明文件未送达）。


## T1 prop:nobound (paper label prop:necessity)

- 正文环境: `proposition`, label `prop:necessity`
- 台账卡: ## T1 prop:nobound — 无误差假设则无常数保证

### 台账陈述（逐字）

- 陈述（M1 量词校正）：不假设 η 上界时，对任意**确定性**算法、任意 n ≥ 2K，存在 (f,f̃) 使输出 T 满足
  f(T) ≤ K/(n−K)·f(O*)。

### 正文陈述（逐字，LaTeX）

```latex
\begin{proposition}[No bound, no guarantee]\label{prop:necessity}
If no upper bound on $\eta$ is assumed, then for every deterministic
algorithm with
arbitrary query access to $\tilde f$ and every $n\ge2K$ there are pairs
$(f,\tilde f)$ on which the output $T$ satisfies
$f(T)\le\tfrac{K}{n-K}\,f(O^{\ast})$.  Consequently no constant worst-case
ratio is achievable without an error assumption.
\end{proposition}
```

## T2 prop:valueacc

- 正文环境: `proposition`, label `prop:valueacc`
- 台账卡: ## T2 prop:valueacc — value accuracy 既不充分也不必要（H1 恢复；2026-09-18 方案二改写，待验证）

### 台账陈述（逐字）

- 陈述（方案二）：(i) ∀ε∈(0,1) 存在单调 submodular f 与 value-accurate at level ε 的 f̃，某处
  d̃_e(S)=0 而 d_e(S)>0，故 Definition 1 的 (η_u,η_o) 无限，value accuracy 单独不给任何 L_K(η) 界；
  (ii) ∀M>0、∀不恒零的单调 submodular f，f̃=(1+M)f 在任何 ε<M 下不 value-accurate，但
  Definition 1 以 η_u=1/(1+M)、η_o=1+M 成立，**全局 η=1**（且 predictive greedy 每步选真增益最大者，
  η^sel=1）；
  (iii) 任意误差 (η_u,η_o)、η=η_uη_o 的 f̃：沿链求和得 f(S)/η_u ≤ f̃(S) ≤ η_o f(S) ∀S；取
  c = 2η_u/(η+1) 则 (1−ε)f ≤ c f̃ ≤ (1+ε)f，ε=(η−1)/(η+1) ∈ [0,1)，即**存在正缩放使 f̃
  value-accurate at level (η−1)/(η+1)**；无 η_o<2 前提；只用 f 单调与 f(∅)=f̃(∅)=0，不用 submodularity。

### 正文陈述（逐字，LaTeX）

```latex
\begin{proposition}[Value accuracy is neither sufficient nor necessary]
\label{prop:valueacc}\mbox{}
\begin{itemize}
\item[(i)] For every $\varepsilon\in(0,1)$ there are a monotone submodular
$f$ and a predictor $\tilde f$, value-accurate at level $\varepsilon$, with
$\tilde d_e(S)=0$ at a pair where $d_e(S)>0$; hence no
$(\eta_u,\eta_o)$ of Definition~\ref{def:eta} is finite for $\tilde f$, and
no bound of the form $L_K(\eta)$ follows from value accuracy alone.
\item[(ii)] For every $M>0$ and every monotone submodular $f$ not
identically zero, the predictor $\tilde f=(1+M)f$ fails value accuracy at
every level $\varepsilon<M$, yet predictive greedy on $\tilde f$ picks at
every state an element of maximum true gain, so $\etasel=1$ and the full
guarantee of Proposition~\ref{prop:guarantee} applies to the run.
\item[(iii)] Conversely, every predictor with error at most
$(\eta_u,\eta_o)$ for a nonnegative $f$ is value-accurate at level
$\max\{1-1/\eta_u,\ \eta_o-1\}$, provided that this value is below $1$
(that is, $\eta_o<2$), so that it lies in the domain of the definition
above.
\end{itemize}
\end{proposition}
```

## T8 thm:ceiling

- 正文环境: `theorem`, label `thm:ceiling`
- 台账卡: ## T8 thm:ceiling — 确定性天花板，统一到全部 ground-set 大小（J5H2 重写）

### 台账陈述（逐字）

- 统一陈述（来源 J5 套 A，results/J5_hardcore/J5_ceiling_proof.md）：2 ≤ K ≤ n，确定性、任意查询
  次数与大小、输出 ≤ K。minimax 值 **C*_{n,K}(η) = K/(K+(η−1)·min{K, n−K})**
  （K ≤ n ≤ 2K 时 = K/((2K−n)+(n−K)η)，n ≥ 2K 时 = 1/η）。
  上界侧：对每个确定性算法存在实例（f̃ = b|S| 线性预测 + modular 高低权 f，任意拆分 (η_u,η_o)
  实际误差两端恰取到；n=K 时输出全集比值 1，端点校准用混合高低权）。
  下界侧（**达到**）：穷举 argmax_{|T|=K} f̃ 在每个实例上 ≥ C*，且有更强的**逐实例式**
  f(S)/f(O) ≥ K/(K+(η−1)|O∖S|)（重叠越多越强，无最小重叠假设）。

### 正文陈述（逐字，LaTeX）

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

### TASKS11 要求的拆分读法（同一陈述，两个 n 区间）

- n >= 2K（Proposition 读法）: C*_{n,K}(eta) = 1/eta；对手侧对每个确定性算法存在实例使 f(T) <= f(O*)/eta；达到侧穷举 argmax f~ 满足 f(S) >= f(O*)/eta。
- K <= n < 2K（remark 读法）: C*_{n,K}(eta) = K/((2K-n)+(n-K)eta)；逐实例式 f(S) >= K/(K+(eta-1)|O*\S|) f(O*)。

## T3 prop:guarantee

- 正文环境: `proposition`, label `prop:guarantee`
- 台账卡: ## T3 prop:guarantee — predictive greedy 的保证（D2：归属 GS）

### 台账陈述（逐字）

- 陈述（K1 后）：f 单调 submodular；run 的选择误差 η^sel（新定义：a_t=M_t/g_t，M_t=g_t=0 取 1，g_t=0<M_t 取 ∞，η^sel=max{1,a_t}，L_K(∞)=0）。则 f(T) ≥ L_K(η^sel) f(O*) ≥ (1−e^{−1/η^sel}) f(O*)，L_K(x)=1−(1−1/(xK))^K。同一界对 η^tr、η 成立。

### 正文陈述（逐字，LaTeX）

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

## T5 lem:coherence

- 正文环境: `lemma`, label `lem:coherence`
- 台账卡: ## T5 lem:coherence — coherence lemma（唯一新引理）

### 台账陈述（逐字）

- 陈述：f 单调，S⊆N，e,e'∉S，d̃_e(S) ≥ d̃_{e'}(S)。则 (i) d_e(S∪{e'}) ≥ d_{e'}(S∪{e})/η；(ii) (1−1/η) d_{e'}(S∪{e}) ≥ d_{e'}(S)−d_e(S)。

### 正文陈述（逐字，LaTeX）

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

## T6 thm:exact

- 正文环境: `theorem`, label `thm:exact`
- 台账卡: ## T6 thm:exact — 精确最坏值（主定理）

### 台账陈述（逐字）

- 陈述：K ≥ 2, η ≥ 1，adversarial tie：ρ_K(η)=min_{0≤j≤K−1} V_j(η)，V_j=1−q^j(1−(K−j)/(Kη))，q=(K−1)η/((K−1)η+1)；段 [K−j,K−j+1] 上由 V_j 取到，[K,∞) 上 V_0=1/η；分段点整数 2..K；ρ_K=1/η ⇔ η ≥ K。K=2,3,4 显式闭式见正文。

### 正文陈述（逐字，LaTeX）

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

## T9 cor:limit

- 正文环境: `corollary`, label `cor:limit`
- 台账卡: ## T9 cor:limit — 渐近（J5H5 首行统一：单调性已证，历史移卡末）

### 台账陈述（逐字）

- 陈述（最终状态）：固定 η，L_K、ρ_K、U_K → 1−e^{−1/η}；ρ_K 关于 K **非增**，K ≤ ⌊η⌋ 平台 1/η，
  K ≥ ⌊η⌋ 起严格递减（[VERIFIED-SYMBOLIC，conditional on thm:exact]，证明已迁入 app:asymptotics，
  J5H5）；一阶展开 ρ_K = 1−e^{−1/η} + c(η)/K + O_η(1/K²)，c(η) = e^{−1/η}(2η−1)/(2η²)（不随
  ⌊η⌋ 分段；c_L = e^{−1/η}/(2η²)、c_U = c，同样已迁入附录）。

### 正文陈述（逐字，LaTeX）

```latex
\begin{corollary}[Limit in $K$]\label{cor:limit}
For fixed $\eta\ge1$, both $L_K(\eta)$ and $\rho_K(\eta)$ converge to
$1-e^{-1/\eta}$ as $K\to\infty$; $L_K$ is monotone in $K$, and
$\rho_K$ is non-increasing in $K$, equal to $1/\eta$ for
$K\le\lfloor\eta\rfloor$ and strictly decreasing from
$K\ge\lfloor\eta\rfloor$ on, so the limit is approached from above.
\end{corollary}
```

## T10c thm:linear-exact (J6)

- 正文环境: `theorem`, label `thm:linear-exact`
- 台账卡: ## T10c thm:linear-exact — greedy 同预算类的精确最优值（Q4 装配，取代 T10b 的单边天花板）

### 台账陈述（逐字）

- 陈述：K ≥ 2，η > 1，n ≥ 4K⁵。𝒜_lin 同 T10b（确定性、≤ nK 次 f̃ 查询、每次查询集合大小 ≤ K、输出 ≤ K 元素；
  predictive greedy 用 ≤ Kn−K(K−1)/2 次查询，属于该类）。
  (i) 上界：对任意 A ∈ 𝒜_lin 与任意给定拆分 η_u, η_o ≥ 1、η_uη_o = η，存在实例 (f, f̃)，f 单调 submodular
  归一化，实际单元素误差因子恰为 (η_u, η_o)，使 f(T)/f(O*) ≤ ρ_K(η)。
  (ii) 与 thm:exact 合并：sup_{A ∈ 𝒜_lin} inf_{(f,f̃)} f(A)/OPT = ρ_K(η)。夹逼闭合，无 n → ∞ 极限，
  值在每个 n ≥ 4K⁵ 处精确。
  随机版（单列，仅渐近）：对任意同预算随机算法存在实例使 E_seed[f(T)/f(O*)] ≤ ρ_K(η) + ε_n，
  ε_n = K²/n + K⁵/(2n)（装配给 K/n + K⁵/(2n)，K²/n 沿 T10b 保守取整）；不声称随机类有限 n 精确。

### 正文陈述（逐字，LaTeX）

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

## T10 thm:hardness

- 正文环境: `theorem`, label `thm:hardness`
- 台账卡: ## T10 thm:hardness — 有界查询 hardness（K4 后按 J2 校准）

### 台账陈述（逐字）

- 陈述：c ≥ 0 实数，τ=⌈c⌉+1，K>τ，n ≥ 4K^{c+2}，η>1 且 η ≥ (K−1)/(K−τ)，θ̄=(η(K−τ)+1)/K。任意确定性算法，≤n^c 次、每次集合大小 ≤K 的 f̃ 查询、输出 ≤K 元素，存在实际误差恰为 η 的实例使 f(T)/f(O*) ≤ H_{K,τ}(η)=1−(1−1/(η(K−τ)+1))^K=L_K(θ̄)。随机版加 ε_n=K/n+K^{2τ+2}/((τ+1)! n^{τ+1−c})。

### 正文陈述（逐字，LaTeX）

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

## T10d thm:linear-anysize (J7)

- 正文环境: `theorem`, label `thm:linear-anysize`
- 台账卡: ## T10d thm:linear-anysize — 任意大小查询线性类的上界（J6/J7 日装配，来源 J7）

### 台账陈述（逐字）

- 陈述：K ≥ 3，η > 1。记 α_lin(K,η) 为确定性、O(nK) 次**任意大小**查询、输出 ≤ K 元素的算法类
  在 n → ∞ 时的最优最坏近似比（随机算法按期望）。则
  ρ_K(η) ≤ α_lin(K,η) ≤ min{1/η, W_K(η)} ≤ min{1/η, ρ_K(η) + 1/(K(e^{K−1}−K−1))}。
  下界即 thm:exact（greedy 属于该类）；η ≥ K 时两端塌到 1/η。

### 正文陈述（逐字，LaTeX）

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

## T2 方案二改写后的陈述（2026-09-18，台账已改，正文未改；矩阵以此为准）


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


## J8 ProbeLottery（陈述来源 HANDOFF_2026-09-18 §4；证明文件未送达）


**Proposition (ProbeLottery).** Let $K=2$ and $\eta=3/2$. There is a randomized algorithm, ProbeLottery,
that makes at most $9n$ queries to $\tilde f$, each on a set of size at most $5$, outputs a set of size
$2$, and satisfies on every instance $(f,\tilde f)$ with $f$ monotone submodular, $f(\emptyset)=0$, and
$\tilde f$ of error at most $\eta=3/2$ (Definition 1, any split with $\eta_u\eta_o=3/2$; in particular
$d_e(S)\le\tilde d_e(S)\le\tfrac32 d_e(S)$ after rescaling):
$$\mathbb E[f(T)]\;\ge\;\Bigl(\tfrac35+\tfrac{1}{400000}\Bigr)\,\mathrm{OPT},$$
the expectation over the algorithm's own randomness only. Since $\rho_2(3/2)=3/5$ is the exact worst
case of predictive greedy, this shows the query-size restriction $|S|\le K$ of the linear-budget
optimality theorem is necessary for randomized algorithms with budget $\tfrac92 nK$.
(Source: HANDOFF_2026-09-18 section 4; the proof file J8_probe_lottery.md with inequalities (3),(8)-(12)
was not delivered. On the tight $K=2,\eta=3/2$ instance the implemented algorithm attains exactly
$3/5+1/2048$.)

