# 量词审计（criteria A 与 E）：prop:valueacc / 台账 T2（convention B 改写版，TASKS11 Q2）

本文件只做两件事：A 项逐量词比对正文环境与台账卡，E 项建立量词审计表并把每个量词落到路线一证明的具体位置。
不修改任何已有文件，不运行 git。精确算术用 fractions.Fraction 与 sympy，浮点只出现在打印里。
状态标签按 CLAUDE.md：[VERIFIED-SYMBOLIC] [VERIFIED-LP] [VERIFIED-EXHAUSTIVE] [HAND-PROOF-UNREVIEWED] [CONJECTURE] [FAILED]。

矩阵采用的陈述是 convention B 版本（`results/V11/inputs/statement_valueacc.md`），与台账卡 T2 的"陈述（方案二）"逐条同义；
正文 `prop:valueacc` 仍是 2026-09-18 之前的旧约定文本（TASKS11 禁止改正文）。因此 A 项比的是"新台账 vs 旧正文"，
差异预期较多，下面逐条列出并说明每一条是不是数学冲突。

读过的文件见 §7。

---

## 1. Criterion A：正文陈述与台账陈述的逐量词比对

### 1.1 三段原文

正文（`paper/sections/results.tex` 第 45 至 68 行，environment `proposition`，label `prop:valueacc`；按 `results/V11/statements.md` 的取材规则去掉 % 注释行）：

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

value accuracy 的定义在环境之外（results.tex 第 37 至 43 行）："Following Hassidim and Singer, call $\tilde f$ value-accurate at level $\varepsilon\in(0,1)$ if $(1-\varepsilon)f(S)\le\tilde f(S)\le(1+\varepsilon)f(S)$ for every $S\subseteq N$"。按取材规则它不属于陈述本体，两边都不含该量词，记为共同省略。

台账（`THEOREM_LEDGER.md` 第 47 至 67 行，卡 `## T2 prop:valueacc`）：

- 标题按 addendum 改为 "Value accuracy is neither sufficient nor necessary **for predictive greedy**"。
- 陈述（方案二）：(i) ∀ε∈(0,1) 存在单调 submodular f 与 value-accurate at level ε 的 f̃，某处 d̃_e(S)=0 而 d_e(S)>0，故 Definition 1 的 (η_u,η_o) 无限，value accuracy 单独不给任何 L_K(η) 界；
  (ii) ∀M>0、∀不恒零的单调 submodular f，f̃=(1+M)f 在任何 ε<M 下不 value-accurate，但 Definition 1 以 η_u=1/(1+M)、η_o=1+M 成立，全局 η=1（且 predictive greedy 每步选真增益最大者，η^sel=1）；
  (iii) 任意误差 (η_u,η_o)、η=η_uη_o 的 f̃：沿链求和得 f(S)/η_u ≤ f̃(S) ≤ η_o f(S) ∀S；取 c = 2η_u/(η+1) 则 (1−ε)f ≤ c f̃ ≤ (1+ε)f，ε=(η−1)/(η+1) ∈ [0,1)，即存在正缩放使 f̃ value-accurate at level (η−1)/(η+1)；无 η_o<2 前提；只用 f 单调与 f(∅)=f̃(∅)=0，不用 submodularity。

矩阵输入（`results/V11/inputs/statement_valueacc.md`）与台账同义，另外把三处隐含前提写进了字面：(i) 的 `f(\emptyset)=0` 与 `\tilde f(\emptyset)=0`、(iii) 的 `for a monotone $f$ with $f(\emptyset)=\tilde f(\emptyset)=0$`、(iii) 末句 `No submodularity of $f$ is used in (iii)`。

### 1.2 逐项对照

| 量词 / 形容词 | 正文（results.tex 环境） | 台账（T2 方案二） | 判定 |
|---|---|---|---|
| 标题限定 "for predictive greedy" | 无 | 有（卡内明写改标题） | **差异 D1** |
| value accuracy 的定义与 ∀S⊆N、ε∈(0,1) 的域 | 环境外的前置段落 | 卡内无 | 一致（共同省略；矩阵输入补上） |
| (i) ∀ε∈(0,1) | 有 | 有 | 一致 |
| (i) ∃ monotone submodular f | 有 | 有 | 一致 |
| (i) f(∅)=0、f̃(∅)=0 | 未写 | 未写 | 一致（共同省略；矩阵输入补上，见 §1.4 注 N1） |
| (i) ∃ f̃ value-accurate at level ε | 有 | 有 | 一致 |
| (i) ∃ pair (S,e)：d̃_e(S)=0 而 d_e(S)>0 | 有 | 有 | 一致 |
| (i) "no (η_u,η_o) of Definition 1 is finite" | 有 | 有 | 一致 |
| (i) "no bound of the form L_K(η) follows from value accuracy alone" | 有 | 有 | 一致 |
| (i) ground set 大小 n（构造需 n ≥ 2） | 未写 | 未写 | 一致（共同省略，见 §3 G1） |
| (ii) ∀M>0 | 有 | 有 | 一致 |
| (ii) ∀ monotone submodular f 且 f 不恒零 | 有 | 有 | 一致 |
| (ii) f̃=(1+M)f | 有 | 有 | 一致 |
| (ii) "fails value accuracy at every level ε<M" | 有 | 有 | 一致（ε=M 的边界两边都未写） |
| (ii) Definition 1 以 η_u=1/(1+M)、η_o=1+M 成立，**全局 η=1** | 无 | 有 | **差异 D2**（正文完全没有 η 的结论） |
| (ii) predictive greedy 每步选真增益最大者，η^sel=1 | 有（主句） | 有（括号内） | 一致（位置不同，范围相同） |
| (ii) "the full guarantee of Proposition prop:guarantee applies to the run" | 有 | 无 | **差异 D3** |
| (ii) tie-breaking（adversarial ties） | 未写 | 未写 | 一致（共同省略；结论对任何 tie-breaking 成立） |
| (ii) t 的范围 / K 的定义域 | 未写（"at every state"） | 未写（"每步"） | 一致（共同省略） |
| (iii) ∀ (η_u,η_o)，η=η_uη_o | 有（"error at most (η_u,η_o)"） | 有 | 一致 |
| (iii) f 的假设 | "for a nonnegative $f$" | "只用 f 单调与 f(∅)=f̃(∅)=0" | **差异 D7** |
| (iii) "不用 submodularity" | 未写 | 有 | 计入 D7 |
| (iii) set-level band f(S)/η_u ≤ f̃(S) ≤ η_o f(S) ∀S | 不在陈述内（在附录证明里） | 在陈述内 | **差异 D8** |
| (iii) ∃ 正缩放 c=2η_u/(η+1) | 无（结论直接说 f̃ 本身） | 有（结论说 c f̃） | **差异 D6** |
| (iii) value accuracy 的 level | max{1−1/η_u, η_o−1}（依赖拆分） | (η−1)/(η+1)（只依赖 η） | **差异 D4** |
| (iii) η_o<2 前提 | 有 | 明写"无" | **差异 D5** |
| (iii) ε 的定义域 | "provided that this value is below 1"，落在前置定义的 (0,1) | "∈ [0,1)" | **差异 D9** |
| (iii) 结论量词 ∀S⊆N | 未写（"is value-accurate at level …" 经定义蕴含） | 写了两处 ∀S | 一致（范围相同，措辞不同） |
| 随机算法条款 / 期望 / fixed random string | 无 | 无 | 一致（本命题无随机条款） |
| 查询类形容词（arbitrary query access、\|S\| ≤ K、至多 nK 次、固定 K 步） | 无 | 无 | 一致（不属本命题） |
| OPT > 0 / f(O*)=0 约定 | 无 | 无 | 一致（本命题不含比值陈述） |
| K ≥ 2 | 无 | 无 | 一致（三条都不需要 K ≥ 2） |

### 1.3 A_diffs（九条）

- **D1（标题）**：台账按 addendum §B 第 5 条把标题改成 "…neither sufficient nor necessary **for predictive greedy**"，正文标题仍是无限定版。addendum 的理由是"对不限查询的算法 value accuracy 是充分的（穷举拿 (1−ε)/(1+ε)）"，所以限定词不可省。差异性质：限定范围，正文当前写法比台账强，且按 addendum 的判断是过强。
- **D2（(ii) 的 η=1）**：台账在 (ii) 里给出 Definition 1 的拆分 (η_u,η_o)=(1/(1+M), 1+M) 与全局 η=1；正文 (ii) 只给 η^sel=1，没有任何关于 η 的结论。这是方案二改写的核心内容，正文尚未落实。**注意**：该结论在正文当前的 `def:eta`（η_u,η_o ≥ 1）下为假，最小合法对是 (1, 1+M)，给出 η=1+M>1。[VERIFIED-SYMBOLIC]（§4 A3）
- **D3（(ii) 的 prop:guarantee 句）**：正文 (ii) 末尾多一句 "the full guarantee of Proposition~\ref{prop:guarantee} applies to the run"，台账 (ii) 没有。两者不冲突（η^sel=1 经 prop:guarantee 直接给 L_K(1)），但台账陈述少覆盖一句。
- **D4（(iii) 的 level）**：正文 max{1−1/η_u, η_o−1}，台账 (η−1)/(η+1)。正文的 level 依赖拆分，台账的只依赖乘积 η。两者的关系已精确核对：**在 η_uη_o=η 固定时，min over splits of max{1−1/η_u, η_o−1} 恰等于 (η−1)/(η+1)，最小点是 η_u=(η+1)/2**，而达到该最小点所需的缩放恰是 c=2η_u/(η+1)。[VERIFIED-SYMBOLIC]（§4 A4）。数值：η=3/2 时正文 level 在三种拆分下分别是 1/2、1/3、1，台账 level 恒为 1/5。
- **D5（(iii) 的 η_o<2 前提）**：正文有，台账明写"无"。该前提的来源已核实：max{1−1/η_u, η_o−1} < 1 当且仅当 η_o<2（在正文约定 η_u ≥ 1 下）。[VERIFIED-EXHAUSTIVE]（§4 A5）。台账版本因为 ε=(η−1)/(η+1) 对每个有限 η 都 <1，前提自动消失。
- **D6（(iii) 的 ∃ 正缩放）**：正文结论是 f̃ 本身 value-accurate，台账结论是 c f̃ value-accurate，多一个存在量词 ∃c>0。这是 D4 的配套改动：去掉 c 之后台账的 level 结论为假，(ii) 的 f̃=(1+M)f 就是反例。
- **D7（(iii) 的 f 假设）**：正文写 "for a nonnegative $f$"，台账写 "只用 f 单调与 f(∅)=f̃(∅)=0，不用 submodularity"。三处不一致：nonnegative vs monotone（正文更弱）、归一化只在台账、"不用 submodularity" 只在台账。两份路线一证明用的都是 monotone（见 §2 表），正文的 nonnegative 没有证明支持。
- **D8（(iii) 的 set-level band 是否入陈述）**：台账把 f(S)/η_u ≤ f̃(S) ≤ η_o f(S) ∀S 写进陈述，正文把它留在附录证明里。这是覆盖范围差异，不是冲突；它对 thm:ceiling 的达到方向是被引用的中间结论，写进陈述会方便引用。
- **D9（(iii) 的 ε 定义域）**：台账写 ε ∈ [0,1)，而 value accuracy 的定义域是 ε ∈ (0,1)，端点 ε=0（即 η=1）落在定义域外。路线一甲已用一句括号处理（η=1 时结论加强成 c f̃=f）；台账陈述本身没有这句。正文用 "provided that this value is below 1" 避开上端，但同样没有处理下端 0。

**A_match = false**（差异清单不重合）。九条里 D2、D4、D5、D6、D7 是方案二改写造成的实质分歧（正文旧、台账新，且 D2 在正文约定下为假、D4 在正文写法下不是缩放不变量），D1、D3、D8、D9 是覆盖范围与措辞。没有一条是"台账与正文都成立但互相矛盾"的数学冲突，全部是正文尚未按 addendum §B 落实。

### 1.4 附注（不计入 A_diffs）

- **N1**：矩阵输入 `statement_valueacc.md` 比台账多写 (i) 的 f(∅)=0、f̃(∅)=0 与 (iii) 的 "monotone f with f(∅)=f̃(∅)=0"、"No submodularity of f is used in (iii)"。这些是台账已在别处表达的同一内容的字面化，比对时按同义处理。
- **N2**：正文 (ii) 把 η^sel=1 放主句、台账放括号；正文 (iii) 用 "error at most"、台账用 "任意误差"。均按同义处理。

---

## 2. Criterion E：量词审计表

路线一材料两份，本表用简称：

- **甲** = `paper/sections/appendix_model_proofs.tex`，subsection `Proof of Proposition~\ref{prop:valueacc}`（第 24 至 52 行），convention B。段落标记：`\emph{(i)}`（27 至 33 行）、`\emph{(ii)}`（35 行）、`\emph{(iii)}`（37 至 47 行，含带 label `eq:valueband` 的 set-level band）、`\begin{remark}`（50 至 52 行）。该文件**未被 main.tex \input**（`grep input paper/main.tex` 无此行；理由见 `results/V11/MISSING_INPUTS.md`）。
- **乙** = `paper/sections/appendix_proofs.tex`，subsection `app:valueacc`（第 144 至 212 行），旧约定。段落标记：`\paragraph{Part (i).}`（151 行起）、`\paragraph{Part (ii).}`（179 行起）、`\paragraph{Part (iii).}`（195 行起）。乙 的 (iii) 结论是旧 level，无缩放段。

表内"量词"一列按矩阵采用的 convention B 陈述逐条列出，含隐含项。

| 量词 / 形容词 | 路线一中被使用或建立的位置（file + paragraph 或引语） | 状态 |
|---|---|---|
| (i) ∀ ε ∈ (0,1) | 甲 `\emph{(i)}`："Fix $\epsilon\in(0,1)$"。乙 `Part (i).`："Fix $\varepsilon\in(0,1)$" | 已覆盖 |
| (i) ∃ monotone submodular f | 甲："The function $f$ is normalized, monotone ($\epsilon>0$) and submodular ($d_a(\{b\})=d_b(\{a\})=\epsilon\le 1=d_a(\emptyset)=d_b(\emptyset)$)"。乙："The function $f$ is nonnegative, monotone, and modular (hence submodular)" | 已覆盖 [VERIFIED-EXHAUSTIVE]（§4 A1/A2） |
| (i) 归一化 f(∅)=0 | 甲 定义式首项 "$f(\emptyset)=0$"。乙 定义式首项 "$f(\emptyset)=0$" | 已覆盖 |
| (i) f̃(∅)=0 | 甲 定义式 "$\tilde f(\emptyset)=0$"。乙 定义式 "$\tilde f(\emptyset)=0$" | 已覆盖 |
| (i) ∃ f̃ value-accurate at level ε，且对全部 S 成立 | 甲："The surrogate is value-accurate at level $\epsilon$: on the singletons $\tilde f=f$, and on $\{a,b\}$ we have $\tilde f/f=1/(1+\epsilon)\ge 1-\epsilon$ because $(1-\epsilon)(1+\epsilon)=1-\epsilon^2\le1$"。乙："Value accuracy at level $\varepsilon$ is checked set by set" | 已覆盖 [VERIFIED-EXHAUSTIVE]（两份构造各 4 个 ε 值全 2^n 个集合精确验算） |
| (i) ∃ pair (S,e)，e ∉ S，d̃_e(S)=0 < d_e(S) | 甲："Yet $\tilde d_b(\{a\})=\tilde f(\{a,b\})-\tilde f(\{a\})=0$ while $d_b(\{a\})=\epsilon>0$"。乙："At the pair $(S,e)=(\{a\},b)$ the true gain is $d_b(\{a\})=\tfrac{2\varepsilon}{1-\varepsilon}>0$ while the predicted gain is $\tilde d_b(\{a\})=0$" | 已覆盖 [VERIFIED-EXHAUSTIVE] |
| (i) ∀ η_u, η_o ∈ (0,∞)：无有限取值 | 甲："so no finite $\eta_u$ satisfies $d_b(\{a\})/\eta_u\le\tilde d_b(\{a\})$; that is, $\eta=\infty$"。乙："A zero predicted gain at a positive true gain violates $\tilde d_e(S)\ge d_e(S)/\eta_u$ for every finite $\eta_u$" | 已覆盖 [HAND-PROOF-UNREVIEWED]（一行不等式，前提已 oracle 确认） |
| (i) "no bound of the form L_K(η) follows from value accuracy alone" | 甲 **无对应句**（(i) 段止于 η=∞ 与 padding 句）。乙："and every bound of the form $L_K(\eta)$ is vacuous for it" | 甲 **GAP**；乙 已覆盖 |
| (i) ground set 大小（构造需要 n ≥ 2，陈述未写） | 甲 末句："Any number of further elements with zero marginal gain under both $f$ and $\tilde f$ may be added to reach a prescribed $n$"（给了向上 padding，未说明 n=1 时命题为假）。乙 只取 $N=\{a,b\}$，无 padding 句 | **GAP**（陈述层缺 n ≥ 2；甲 部分覆盖、乙 未覆盖，见 §3 G1） |
| (i) K 的定义域（仅经末句的 L_K 涉及 K） | 甲 不提 K。乙 "every bound of the form $L_K(\eta)$" 不带 K 的限定 | 部分覆盖（由 model.tex 的 1 ≤ K ≤ n 继承） |
| (i) f̃ 不必 submodular（模型 D1 的自由度） | 甲、乙 的 f̃ 都是 monotone submodular，构造不依赖该自由度 | 已覆盖（不需用到） |
| (ii) ∀ M > 0 | 甲 `\emph{(ii)}`："Fix $M>0$ and let $\tilde f=(1+M)f$"。乙 `Part (ii).`："$\tilde f=(1+M)f$ for $M>0$" | 已覆盖 |
| (ii) ∀ monotone submodular f 且 f 不恒零 | 甲 **未声明该前提**，只写 "For every nonempty $S$ with $f(S)>0$"；f ≡ 0 时该句空真而结论失效。乙："Let $f$ be monotone submodular, not identically zero" | 甲 **GAP**（隐含使用未点名）；乙 已覆盖 |
| (ii) f̃(∅)=0 | 甲、乙 都由 f(∅)=0 自动成立，两份都未点名 | 部分覆盖（轻） |
| (ii) ∀ ε < M：value accuracy 失败 | 甲："$\tilde f(S)/f(S)=1+M$, which exceeds $1+\epsilon$ whenever $\epsilon<M$; hence $\tilde f$ is value-accurate at no level below $M$"。乙："$|\tilde f(S)-f(S)|/f(S)=M>\varepsilon$ for every $\varepsilon<M$" | 已覆盖 [VERIFIED-EXHAUSTIVE]；ε=M 的边界两份都未说明（该处取等，严格不等号不可放宽） |
| (ii) Definition 1 的拆分 (η_u, η_o)=(1/(1+M), 1+M) 与乘积 η=1 | 甲 末句："so Definition~\ref{def:eta} holds with $\eta_u=1/(1+M)$ and $\eta_o=1+M$, and $\eta=\eta_u\eta_o=1$"。乙 无（旧约定下不可能给 η=1） | 甲 已覆盖 [VERIFIED-SYMBOLIC + VERIFIED-EXHAUSTIVE]（§4 A3）；乙 **GAP** |
| (ii) convention B（取消 η_u ≥ 1 下限）是 η=1 的前提 | 甲 引用 `Definition~\ref{def:eta}`，而仓库 `model.tex` 的 def:eta 仍写 "For $\eta_u,\eta_o\ge1$"；甲 未点名自己用的是 convention B。乙 无 | **GAP**（约定冲突，见 §3 G5） |
| (ii) predictive greedy 在每个 state S^t（t=0..K−1）选真增益最大者 | 甲 **完全不提 predictive greedy**。乙："at every state the maximizers of $\tilde d_e(S)$ and of $d_e(S)$ are the same set of elements" | 甲 **GAP**；乙 已覆盖 [VERIFIED-EXHAUSTIVE]（§4 A3，n=4 coverage，全部 2^4 个 state） |
| (ii) tie-breaking（adversarial ties） | 甲 无。乙："whichever of them tie breaking picks, the picked element has maximum true gain" | 甲 **GAP**；乙 已覆盖 |
| (ii) η^sel = 1（def:etasel 的三分情形） | 甲 无。乙："Every step with positive chosen gain therefore contributes the factor $\max_{e\notin S^t}d_e(S^t)/d_{e_t}(S^t)=1$ to Definition~\ref{def:etasel}, giving $\etasel=1$. (Gains are nonnegative by monotonicity, so no step has negative chosen gain.)" 只正面处理 g_t>0 一支，g_t=0 的两支靠括号句间接带过 | 甲 **GAP**；乙 部分覆盖 [VERIFIED-EXHAUSTIVE]（§4 A3，K=1..4 穷举全部 tie 打破方式，a_t 恒为 1，从未落入 a_t=∞） |
| (ii) 固定 K 步 / 1 ≤ K ≤ n | 甲 无。乙 隐含于 "Every step" | 部分覆盖（由 assumptions 继承） |
| (ii) 正文附加句 "full guarantee of prop:guarantee applies" | 乙 末句："Proposition~\ref{prop:guarantee} certifies the run at $L_K(1)$"。甲 无 | 乙 已覆盖 |
| (iii) ∀ (η_u, η_o) > 0，η=η_uη_o ≥ 1 | 甲 `\emph{(iii)}` 首句："Let $\tilde f$ have marginal-gain error $\eta=\eta_u\eta_o$"。乙 `Part (iii).`："apply Definition~\ref{def:eta} to the pair $(\emptyset,S)$ read through single elements"（旧约定，两因子 ≥ 1） | 已覆盖（甲 convention B，乙 旧约定） |
| (iii) f 单调；不用 submodularity | 甲："all terms are nonnegative because $f$ is monotone"；甲 remark："Part (iii) uses only that $f$ is monotone and that both functions vanish on the empty set; it does not use submodularity"。乙："increments of a monotone $f$ are nonnegative"，无"不用 submodularity"的话 | 甲 已覆盖；乙 部分覆盖。另注：逐项相加不需要各项非负，monotone 的实际用处是 band 非空与 f(S) ≥ 0，甲 把它记在求和一步，措辞不精确（见 §3 G9） |
| (iii) 正文写的 "nonnegative f" | 甲、乙 的证明都用 monotone，没有一份支持 nonnegative | **GAP**（陈述与证明的假设词不一致，见 §3 G6） |
| (iii) 归一化 f(∅)=f̃(∅)=0（链求和的锚点） | 甲："Since $f(\emptyset)=\tilde f(\emptyset)=0$"，随后写出两条 telescoping 等式。乙 未点名，只写 "summing the telescoping of $f$ and $\tilde f$ along any fixed enumeration of $S$" | 甲 已覆盖；乙 **GAP**（轻，见 §3 G8） |
| (iii) ∀ S ⊆ N 的 set-level band f(S)/η_u ≤ f̃(S) ≤ η_o f(S) | 甲 公式 `\label{eq:valueband}`："$f(S)/\eta_u\le\tilde f(S)\le\eta_o f(S)\qquad\text{for all }S\subseteq N$"。乙 同一不等式（无 label） | 已覆盖 [VERIFIED-EXHAUSTIVE]（route-two 的 C8/C11 已独立核；本次未重复） |
| (iii) 枚举顺序的任意性 | 甲 固定一个枚举 "$S_i=\{e_1,\dots,e_i\}$"，未说明结论与顺序无关（左右两端确实不依赖顺序）。乙："along any fixed enumeration of $S$" | 乙 已覆盖；甲 部分覆盖 |
| (iii) ∃ 正缩放 c=2η_u/(η+1) | 甲："Now set $\epsilon=(\eta-1)/(\eta+1)\in[0,1)$ and $c=2\eta_u/(\eta+1)>0$. Then $c/\eta_u=2/(\eta+1)=1-\epsilon$ and $c\,\eta_o=2\eta/(\eta+1)=1+\epsilon$"。乙 无缩放段 | 甲 已覆盖 [VERIFIED-SYMBOLIC]（§4 A4）；乙 **GAP** |
| (iii) level = (η−1)/(η+1)，只依赖 η 不依赖拆分 | 甲 同上一行；甲 没有明说"只依赖乘积"。乙 给的是旧 level max{1−1/η_u, η_o−1}（依赖拆分） | 甲 已覆盖；乙 与新陈述冲突（见 §3 G7）。两者的精确关系见 §4 A4：新 level = 旧 level 对拆分取最小 |
| (iii) 无 η_o < 2 前提 | 甲 全段无该前提。乙 无该前提字样（前提是正文 `prop:valueacc` 自己加的 proviso，附录只给 level 公式） | 甲 已覆盖；乙 的 level 使正文不得不加 proviso [VERIFIED-EXHAUSTIVE]（§4 A5） |
| (iii) ε 的域 [0,1) 与 value accuracy 定义域 (0,1) 的端点 | 甲 括号句："(For $\eta=1$ this reads $c\tilde f=f$; for $\eta>1$ the level lies in $(0,1)$.)"。乙 无端点讨论 | 甲 已覆盖；乙 **GAP**（轻） |
| (iii) 结论对象是 c f̃ 而非 f̃ | 甲："the rescaled surrogate $c\tilde f$ is value-accurate at level $\epsilon$"。乙 的结论是 f̃ 本身（旧 level） | 甲 已覆盖 |
| OPT > 0 / f(O*) = 0 的约定 | 三条都不含比值陈述，只有正文 (ii) 引用 prop:guarantee 时间接涉及；甲、乙 都不需要 | 不适用 |
| K ≥ 2 | 三条都不需要；(ii) 对每个 K ≥ 1 成立（§4 A3 已在 K=1..4 上确认） | 不适用（并确认不需要） |
| 随机算法条款 / fixed random string / 期望对谁取 | 本 proposition 无随机条款，甲、乙 都无随机段 | 不适用 |
| 查询类形容词（arbitrary query access、\|S\| ≤ K、至多 nK 次查询、固定 K 步、error exactly / at most） | 本 proposition 不含这些限定；它们属 thm:ceiling、thm:linear-exact、thm:hardness 的卡。唯一沾边的是 (iii) 的 "error at most (η_u,η_o)"，甲 用 "have marginal-gain error η=η_uη_o" 表达同一件事 | 不适用 |

### 2.1 模板附带问题

- **"thm:ceiling 的随机段落 fixed random string 量词是否在陈述里"**：本项审计的 statement 是 prop:valueacc，不适用，留给 thm:ceiling 那一项。就本命题而言：三条里没有随机条款，两份路线一材料都没有随机段，正文与台账陈述里都没有期望或 random string 量词。相关的一条依赖记录在此：addendum §B 第 2 条说 thm:ceiling 的达到方向走"路线乙"，即 Horel–Singer 的观察加 prop:valueacc(iii) 并代入 ε=(η−1)/(η+1)。该代入已精确核对：(1−ε)/(1+ε) = 1/η。[VERIFIED-SYMBOLIC]（§4 A7）。**注意**：这条依赖只对台账版 (iii) 成立；用正文版 (iii) 的 level（拆分 (1,3/2) 时为 1/2）代入得 (1−ε)/(1+ε)=1/3，不是 1/η=2/3。所以 D4 不只是措辞问题，它是 thm:ceiling 达到方向的引用前提。
- **"thm:linear-exact 的 n ≥ 4K^5 能否紧到约 K³(K−1)²/2 + K²"**：不适用（那是 app:greedybudget 与台账 T10c 的项）。本文件不对该数做任何断言，以免与该项的审计结论冲突。

---

## 3. GAP 清单

| 编号 | GAP | 影响 | 保守处理建议（本次不改任何文件） |
|---|---|---|---|
| G1 | 陈述层：(i) 缺 n ≥ 2。甲 只给向上 padding，乙 连 padding 句都没有 | n=1 时 (i) 为假：唯一的 pair 是 (∅,e)，value accuracy 给 f̃({e}) ≥ (1−ε)f({e}) > 0，于是 η ≤ (1+ε)/(1−ε) 有限 | 陈述里补 "for every n ≥ 2"，或保留 padding 句并注明 n ≥ 2 |
| G2 | 甲 (i) 缺 "no bound of the form L_K(η) follows" 那一句 | 若最终只保留甲，(i) 的第二半结论在附录里无落点 | 把乙的 "every bound of the form L_K(η) is vacuous for it" 迁进甲 |
| G3 | 甲 (ii) 未声明 f 不恒零 | f ≡ 0 时 f̃=f，value accuracy 在每个 level 成立，(ii) 的前半句失效；甲 只用 "For every nonempty S with f(S)>0" 绕过 | 甲 (ii) 首句补 "and f not identically zero" |
| G4 | 甲 (ii) 完全不含 predictive greedy、argmax 保持、tie-breaking、η^sel=1 | 台账 (ii) 的括号内容与正文 (ii) 的主句在甲里无落点；只有乙有 | 把乙 Part (ii) 的 argmax 段迁进甲，或在甲 (ii) 后补三行 |
| G5 | 约定冲突：甲 (ii)(iii) 引用 `def:eta`，而 `model.tex` 的 def:eta 仍写 η_u,η_o ≥ 1；甲 (ii) 用的 η_u=1/(1+M) 在该约定下非法 | 现状下甲 与 model.tex 放在一起是不自洽的；(ii) 的 η=1 结论依赖 convention B 取消下限 | 与 model.tex 的 Definition 1 改写一并处理（HANDOFF §3 已定方案二），或在甲 (ii) 里点名 convention B |
| G6 | 正文 (iii) 写 "for a nonnegative f"，甲、乙 的证明都用 monotone | 陈述的假设比证明弱；在 η>1 时 Definition 1 本身强制 d_e(S) ≥ 0，所以实际不出错，但字面无支撑 | 陈述改 monotone（台账已是 monotone），或在附录加一句"band 在 η>1 时强制单调" |
| G7 | 乙 (iii) 与新陈述冲突：旧 level max{1−1/η_u, η_o−1}、无 c 缩放段，且该 level 不是缩放不变量 | 仓库里同一命题有两份不等价的 (iii)；乙 是 main.tex 实际编译进 PDF 的那份 | 按 addendum §B 用甲替换乙的 Part (iii)，同时删正文的 η_o<2 proviso（作者操作） |
| G8 | 乙 (iii) 未点名 f(∅)=f̃(∅)=0 是 telescoping 的锚点 | 读者需自己补；若两函数在 ∅ 不取 0，set-level band 会多一个常数偏移 | 乙 补半句，或随 G7 一并被甲取代 |
| G9 | 甲 (iii) 把 monotonicity 记在"summing"一步（"all terms are nonnegative because f is monotone"），但逐项相加不需要各项非负 | 不影响结论，影响的是"monotone 这个限定词用在哪"的空洞性检验（CLAUDE.md 第 39 至 44 行） | 甲 改成"monotone 保证 band 非空且 f(S) ≥ 0，使 (1±ε)f(S) 是围绕非负数的相对带" |
| G10 | 接线层：甲 用 label `prop:nobound`、`app:model` 与 bib 键 `horel2016`，正文用 `prop:valueacc`、`app:valueacc`、`horel2016maximization`；甲 未被 main.tex \input；两份 (i) 的构造不同（甲 f=(1,1,1+ε)，乙 f=(1, 2ε/(1−ε), (1+ε)/(1−ε))） | 同一命题在仓库里有两份证明，二者的 (i) 与 (iii) 都不同 | 按 `results/V11/MISSING_INPUTS.md` 的记录，接线与二选一留给作者 |
| G11 | addendum §B 第 5 条要求的 "value accuracy is not sufficient" 限定（对不限查询的算法它为假）只体现在台账标题，正文标题与两份陈述正文都没有 | 审稿人可以用穷举 f̃ 的 (1−ε)/(1+ε) 反驳无限定的 "not sufficient" | 正文标题按 addendum 加 "for predictive greedy"，并在 Model 的读法句里点明 |
| G12 | (ii) 的 ∀ε<M 中 ε=M 的边界两份都未说明 | ε=M（且 M<1）处 value accuracy 恰好成立，故严格不等号不可放宽；陈述正确但无落点 | 附录加半句，或不处理（不影响真值） |
| G13 | 甲、乙 都不含随机条款；本命题也不需要 | 与 thm:ceiling 的随机段不同，此处无缺口 | 无需处理 |

---

## 4. 精确算术复核

复核脚本（写在 scratchpad，不入仓库）：`/tmp/claude-0/-home-user/09d7d9a5-0b14-54a1-894a-d76a6d641333/scratchpad/check_valueacc_quant.py`。
共 72 项检查，全部通过，0 项 [FAILED]。只用 `fractions.Fraction` 与 `sympy`，浮点只出现在打印里。

- **A1（甲 的 (i) 构造）**：ε ∈ {1/100, 1/5, 1/2, 9/10}，f 归一化、单调、submodular（全部 (S,T,e) 三元组穷举），value accuracy 在全部 2² 个集合上成立，witness pair 为 ({b}, a) 或 ({a}, b)，d̃=0<d。[VERIFIED-EXHAUSTIVE]
- **A2（乙 的 (i) 构造）**：同样四个 ε，另加 modular 恒等式 f({a,b}) = f({a}) + f({b}) 的精确验算，value accuracy 全集合成立，witness pair 为 ({a}, b)。[VERIFIED-EXHAUSTIVE]
- **A3（(ii)）**：η_u η_o = 1 对 (1/(1+M), 1+M) 恒成立；η_u=1/(1+M) < 1 对每个 M>0（故正文 def:eta 的 ≥1 下限把它排除，最小合法对是 (1, 1+M)，η=1+M）。n=4 的 weighted coverage f，M ∈ {1/100, 1/2, 3}：全部 2⁴ 个 state 上 argmax(d̃) = argmax(d) 作为集合相等；convention B 的 band 两端同时取等；K=1,2,3,4 时穷举全部 adversarial tie 打破方式，a_t 恒为 1，η^sel = 1，从未落入 a_t = ∞ 分支；value accuracy 在 ε = M/2 与 ε = 0.99M 处失败。[VERIFIED-SYMBOLIC + VERIFIED-EXHAUSTIVE]
- **A4（(iii) 的两条恒等式与拆分最小化）**：c/η_u − (1−ε) 与 c η_o − (1+ε) 化简为 0；缩放后的因子 (η_u/c, c η_o) = ((η+1)/2, 2η/(η+1))，乘积仍为 η；ε(1)=0，dε/dη = 2/(η+1)² > 0，lim_{η→∞} ε = 1。**关键一条**：固定 η 对拆分求 min max{1−1/η_u, η_o−1}，平衡点解出 η_u = (η+1)/2，平衡值恰为 (η−1)/(η+1)，而把任意拆分搬到该平衡点所需的缩放恰为 c = 2η_u/(η+1)。[VERIFIED-SYMBOLIC]
- **A5（η_o<2 前提）**：在 η_u ≥ 1 的正文约定下，max{1−1/η_u, η_o−1} < 1 当且仅当 η_o < 2（24 个 (η_u, η_o) 格点穷举）。η_o = 3 时正文 (iii) 空转，台账 (iii) 仍给 ε = 1/2。[VERIFIED-EXHAUSTIVE]
- **A6（running example，K=3、η=3/2）**：ε = 1/5；三种拆分 (1, 3/2)、(3/2, 1)、(3/4, 2) 的 c 分别为 4/5、6/5、3/5，且 c/η_u ≡ 4/5、c η_o ≡ 6/5。同一 η 下正文 level 分别是 1/2、1/3、1，台账 level 恒为 1/5。[VERIFIED-EXHAUSTIVE]
- **A7（(iii) 的下游用途）**：(1−ε)/(1+ε) = 1/η 在 ε=(η−1)/(η+1) 处恒成立；用正文 level（拆分 (1,3/2) 得 1/2）代入只得 1/3 ≠ 2/3 = 1/η。[VERIFIED-SYMBOLIC]

拆分对照表（η = 3/2 与两个对照点）：

| η_u | η_o | η | 正文 level max{1−1/η_u, η_o−1} | 台账 level (η−1)/(η+1) |
|---|---|---|---|---|
| 1 | 3/2 | 3/2 | 1/2 | 1/5 |
| 3/2 | 1 | 3/2 | 1/3 | 1/5 |
| 3/4 | 2 | 3/2 | 1 | 1/5 |
| 1 | 3 | 3 | 2 | 1/2 |
| 2 | 2 | 4 | 1 | 3/5 |

读法：正文 level 在同一个 η 上随拆分变动，且可以 ≥ 1（出 value accuracy 的定义域）；台账 level 只依赖 η，恒在 [0,1)，并且恰是正文 level 对拆分的下确界。lem:scaling 只对"类"断言乘积不变，正文 (iii) 的 level 不是类不变量，这是 D4 与 D6 的根因。

---

## 5. 结论

- **A：A_match = false**，九条差异 D1 至 D9。其中 D2、D4、D5、D6、D7 是方案二改写的实质内容（正文旧、台账新）；D2 在正文当前的 def:eta 下为假，D4 的正文 level 不是缩放不变量且不支持 thm:ceiling 的达到方向引用。D1、D3、D8、D9 是覆盖范围与措辞。没有"两边都成立而互相矛盾"的情形。
- **E：** 37 行量词审计表。甲（convention B）覆盖 (iii) 的全部量词与 (ii) 的 η=1，但缺 (i) 的 L_K 句、(ii) 的 f ≢ 0 前提与全部 greedy 相关内容；乙（旧约定）覆盖 (i)(ii) 的全部内容与 tie-breaking，但 (iii) 与新陈述冲突。GAP 共 13 条：G1、G6、G11 在陈述层，G2 至 G5、G8 至 G10、G12 在材料层，G7 是两份材料的冲突，G13 为空。
- 本次未修改任何已有文件，未运行 git。本文件与 scratchpad 里的复核脚本是本次新建的全部内容。

---

## 6. 状态标签小结

- 命题本身：(i)(ii) [HAND-PROOF-UNREVIEWED]（台账 T2 原状）；(iii) 台账按 addendum §B 第 10 条记为 [HAND-PROOF-REVIEWED] + [VERIFIED-EXHAUSTIVE (random)]，本次未改动该判定。
- 两份 (i) 构造的合法性、value accuracy、witness pair：[VERIFIED-EXHAUSTIVE]（各 4 个 ε 值，全 2^n 个集合，Fraction）。
- (ii) 的 band 取等、η=1、argmax 保持、η^sel=1：[VERIFIED-SYMBOLIC] + [VERIFIED-EXHAUSTIVE]（n=4，M 三值，K=1..4 全 tie 打破方式）。
- (iii) 的 c 与 ε 的两条恒等式、ε 的单调性与值域、拆分最小化、(1−ε)/(1+ε)=1/η：[VERIFIED-SYMBOLIC]。
- η_o<2 与 max{1−1/η_u, η_o−1}<1 的等价：[VERIFIED-EXHAUSTIVE]（24 格点）。
- 一般 (η_u, η_o) 下 set-level band 的求和步：[HAND-PROOF-UNREVIEWED]（route-two 已在有限实例上 [VERIFIED-EXHAUSTIVE]，本次未重复）。
- "value accuracy 本身是否蕴含某个 (ε,K) 的乘性保证"：[CONJECTURE]（route-two §7 G2 已记，本次不推进）。

## 7. 读过的文件

- `/home/user/sub-modular-optimization/results/V11/statements.md`（T2 段）
- `/home/user/sub-modular-optimization/results/V11/inputs/statement_valueacc.md`
- `/home/user/sub-modular-optimization/results/V11/inputs/definition1.md`
- `/home/user/sub-modular-optimization/results/V11/inputs/assumptions.md`
- `/home/user/sub-modular-optimization/results/V11/inputs/notation.md`
- `/home/user/sub-modular-optimization/results/V11/MISSING_INPUTS.md`
- `/home/user/sub-modular-optimization/results/V11/notes.md`
- `/home/user/sub-modular-optimization/results/V11/route2/valueacc.md`（仅用于对齐 GAP 编号，不作为路线一材料）
- `/home/user/sub-modular-optimization/results/V11/audit/nobound.md`（仅取格式）
- `/home/user/sub-modular-optimization/THEOREM_LEDGER.md`（T0、T1、T2、T3 卡）
- `/home/user/sub-modular-optimization/paper/sections/results.tex`（prop:valueacc 环境第 45 至 68 行与前置定义段第 37 至 43 行）
- `/home/user/sub-modular-optimization/paper/sections/model.tex`
- `/home/user/sub-modular-optimization/paper/sections/appendix_proofs.tex`（app:valueacc，第 144 至 212 行）
- `/home/user/sub-modular-optimization/paper/sections/appendix_model_proofs.tex`（第 24 至 52 行；与 uploads 版逐字节相同）
- `/home/user/sub-modular-optimization/paper/main.tex`（确认 appendix_model_proofs 未 \input）
- `/home/user/sub-modular-optimization/CLAUDE.md`
- `HANDOFF_2026-09-18.md` 与 `HANDOFF_ADDENDUM_2026-09-18.md`（uploads 版，与仓库根目录同名文件一致）
