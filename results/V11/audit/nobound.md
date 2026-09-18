# 量词审计（criteria A 与 E）：prop:necessity / 台账 T1 prop:nobound（TASKS11 Q1）

本文件只做两件事：A 项逐量词比对正文环境与台账卡，E 项建立量词审计表并把每个量词落到路线一证明的具体位置。
不修改任何已有文件，不运行 git。精确算术用 fractions.Fraction 与 sympy，浮点只出现在打印里。
状态标签按 CLAUDE.md：[VERIFIED-SYMBOLIC] [VERIFIED-EXHAUSTIVE] [HAND-PROOF-UNREVIEWED] [CONJECTURE] [FAILED]。

读过的文件见 §7。

---

## 1. Criterion A：正文陈述与台账陈述的逐量词比对

### 1.1 两段原文

正文（`paper/sections/results.tex` 第 21 至 28 行，environment `proposition`，label `prop:necessity`；按 `results/V11/statements.md` 的取材规则去掉 % 注释行）：

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

台账（`THEOREM_LEDGER.md` 第 37 至 45 行，卡 `## T1 prop:nobound`）：

- 陈述（M1 量词校正）：不假设 η 上界时，对任意**确定性**算法、任意 n ≥ 2K，存在 (f,f̃) 使输出 T 满足 f(T) ≤ K/(n−K)·f(O*)。
- 前提：任意查询访问 f̃。
- 随机版（M1，J5 量词规格）：未单独陈述。正文注释注明：随机类比需按"对每个随机算法存在固定实例使 E_seed[·] ≤ …"的量词经 app:hardness 式平均得出，本文未给常数，不声称。

### 1.2 逐项对照

| 量词 / 形容词 | 正文 | 台账 | 判定 |
|---|---|---|---|
| 前提「no upper bound on η」 | 有（句首条件从句） | 有（"不假设 η 上界时"） | 一致 |
| ∀ deterministic algorithm | 有，"for every deterministic algorithm" | 有，"对任意**确定性**算法" | 一致 |
| 形容词 arbitrary query access to f̃ | 在陈述内，修饰被全称的算法 | 在陈述外的独立字段"前提" | **差异 D1**（范围同，位置不同） |
| ∀ n ≥ 2K | 有，与算法并列的全称 | 有，"任意 n ≥ 2K" | 一致 |
| K 的定义域 | 未写（继承 model.tex 的 1 ≤ K ≤ n，且 n ≥ 2K 蕴含 K ≤ n/2） | 未写 | 一致（共同省略） |
| ∃ (f, f̃) | 有，"there are pairs (f,f̃)"（复数） | 有，"存在 (f,f̃)"（单数） | **差异 D3**（同一存在量词，措辞不同，不改变真值） |
| pair 需满足除 η 上界外的全部模型假设 | 未写 | 未写 | 一致（共同省略，见 §3 G3） |
| 输出 T 的可行性 \|T\| ≤ K | 未写（只写 "the output T"） | 未写（只写"输出 T"） | 一致（共同省略，见 §3 G1） |
| 结论不等式 f(T) ≤ K/(n−K)·f(O*) | 有 | 有 | 一致 |
| OPT 记号 | f(O^*) | f(O*) | 一致（HANDOFF §3 要求改成 OPT，两边都尚未落实） |
| 第二句「no constant worst-case ratio」 | 在陈述内 | 陈述字段无，只在卡标题"无误差假设则无常数保证" | **差异 D2** |
| 第二句的隐含量词（固定 K、n→∞） | 未写 | 未写 | 一致（共同省略，见 §3 G2） |
| 随机算法条款 | 环境内无（第 29 至 35 行的 % 注释里有，按取材规则不计入） | 有独立字段"随机版：未单独陈述 + 量词规格 + 不声称" | **差异 D4** |
| 误差 (η_u, η_o) 的拆分 | 未出现，只出现 η | 未出现，只出现 η | 一致 |
| 期望 / random string | 无 | 陈述字段无（在"随机版"字段） | 见 D4 |
| tie breaking | 无 | 无 | 一致（本陈述对任意确定性算法，不涉及 greedy 内部规则） |

### 1.3 A_diffs（四条）

- **D1**：`arbitrary query access to $\tilde f$` 在正文里是被全称的算法的形容词，写在陈述内部；台账把它放在陈述之外的"前提"字段。作用范围相同（都限定被全称的算法），但按"逐字比对陈述"的口径两边的陈述文本不重合。保守处理：矩阵记为差异，建议把台账"前提"行并入陈述行（只动台账，不动正文）。
- **D2**：正文第二句 `Consequently no constant worst-case ratio is achievable without an error assumption.` 不在台账的陈述字段里，只以中文出现在卡标题。台账陈述因此比正文弱一句。
- **D3**：正文 `there are pairs`（复数），台账"存在 (f,f̃)"（单数）。两条路线一证明给出的都是以 O 为指标的一族 pair，复数与单数都成立，真值不变。
- **D4**：台账多一条"随机版"字段（量词规格 + 不声称）；正文环境内没有对应文字，同样内容只在 % 注释里。

**A_match = false**（差异清单不重合）。四条差异都不改变命题的真值，属记录口径与覆盖范围的差异，不是数学冲突。

---

## 2. Criterion E：量词审计表

路线一材料两份，本表用简称：

- **甲** = `paper/sections/appendix_proofs.tex`，subsection `app:necessity`（第 80 至 141 行），构造 γ = K²/(n(n−K))，f̃(S) = |S|，f_O(S) = |S∩O| + γ|S∖O|。段落标签：setup、`The pair is admissible and has finite error.`、`Deterministic algorithms.`、`Randomized algorithms.`。
- **乙** = `paper/sections/appendix_model_proofs.tex`，subsection `Proof of Proposition~\ref{prop:nobound}`（第 6 至 22 行），构造 δ = K/(n−K)，f̃(S) = |S|，f(S) = |S∩O| + δ|S∖O|，末尾带一条 remark。该文件**未被 main.tex \input**（`grep input paper/main.tex` 无此行；理由见 `results/V11/MISSING_INPUTS.md`）。

| 量词 / 形容词 | 路线一中被使用或建立的位置（file + paragraph 或引语） | 状态 |
|---|---|---|
| 前提：η 无上界（η 有限但不受任何预给上界约束） | 甲 `The pair is admissible and has finite error.`："the error is exactly $\eta=1/\gamma=n(n-K)/K^{2}$, which is finite for every $n$ and grows without bound as $n\to\infty$"；甲 `Randomized algorithms.` 末句："no constant worst-case ratio survives when $\eta$ is unconstrained"。乙 proof："with the finite error $\eta=1/\delta=(n-K)/K$"；乙 remark："without an upper bound on $\eta$ no algorithm has any constant guarantee" | 已覆盖 [HAND-PROOF-UNREVIEWED] |
| ∀ deterministic algorithm | 甲 `Deterministic algorithms.`："$\tilde f$ does not depend on $O$, so the whole query transcript of $\mathcal A$, and therefore its output $T$ with $\lvert T\rvert\le K$, are the same for every $O$"。乙 proof 首句："Fix a deterministic algorithm and $n\ge 2K$ … every answer the algorithm receives is determined before $f$ is chosen" | 已覆盖 [HAND-PROOF-UNREVIEWED]（information-theoretic 一步，无 oracle 可直接检验） |
| 形容词 arbitrary query access to f̃ | 甲 setup："let $\mathcal A$ be an algorithm with arbitrary query access to $\tilde f$"，其后全程不使用 query 次数或 query 大小。乙 只写 "It is normalized and can be evaluated on any set"，没有 "arbitrary query access" 字样 | 甲 已覆盖；乙 部分覆盖（措辞缺，语义由"answers determined before f is chosen"承担） |
| "query" 本身的定义 | model.tex 只有一句 "it can only query a predictor $\tilde f$"，没有"一次求值算一次 query"的定义；查询类的计数与大小只在 sec:hardness 出现 | **GAP**（定义层；HANDOFF §8 计划中的 Model 重写含该句，尚未落地） |
| ∀ n ≥ 2K（域限制） | 甲 两处：setup "where $\gamma\le1$ because $n\ge2K$ gives $n(n-K)\ge 2K\cdot K>K^{2}$"；`Deterministic algorithms.` "Since $n\ge2K$ and $\lvert T\rvert\le K$, a $K$-set $O\subseteq N\setminus T$ exists"。乙 一处："which exists because $n\ge 2K$"（δ ≤ 1 只以 "$\delta=K/(n-K)\in(0,1]$" 的区间断言给出，未点名 n ≥ 2K） | 已覆盖；乙 的 δ ≤ 1 是断言而非推导 |
| ∃ (f, f̃)，且 O 在算法输出之后选 | 甲 `Deterministic algorithms.`："For that $O$"（先固定 transcript 与 T，再取 O）。乙 proof："Choose a set $O\subseteq N\setminus T$ with $\lvert O\rvert=K$" | 已覆盖 |
| 输出 T 的可行性 \|T\| ≤ K（隐含） | 甲 `Deterministic algorithms.`："its output $T$ with $\lvert T\rvert\le K$"。乙 proof："hence the output $T$, with $\lvert T\rvert\le K$, is a fixed set determined by the algorithm alone" | 证明已覆盖；**陈述层 GAP**（正文与台账都只写 "the output T"） |
| ground set 的大小要求（是否需要补元素） | 甲 setup 只要求 \|N\| = n 且 n ≥ 2K，无 padding；乙 同。对照 prop:valueacc(i) 需要 "Any number of further elements … may be added to reach a prescribed $n$"，本命题不需要 | 已覆盖 |
| 归一化 f(∅) = 0 | 甲 `The pair is admissible…`："$f_O$ is modular with coefficients in $\{1,\gamma\}\subseteq(0,1]$, so it is monotone and submodular with $f_O(\emptyset)=0$"。乙 proof："The function $f$ is modular, hence normalized, monotone and submodular" | 已覆盖 |
| f 单调 submodular | 同上一行（两份都由 modular 且系数非负直接得出） | 已覆盖 |
| f̃(∅) = 0 且可在任意集合求值 | 甲 同段末："and $\tilde f(\emptyset)=0$"。乙 proof："It is normalized and can be evaluated on any set" | 已覆盖 |
| f̃ 不要求 submodular（模型 D1 的自由度） | 两份都取 f̃(S) = \|S\|，是 modular，比模型要求更强，构造不依赖该自由度 | 已覆盖（不需用到） |
| Definition 1 成立；(η_u, η_o) 的拆分 vs 乘积 η | 甲 `The pair is admissible…`："$\eta_u=\max_{S,e}d/\tilde d=1$ and $\eta_o=\max_{S,e}\tilde d/d=1/\gamma$"。乙 proof："Definition~\ref{def:eta} holds with $\eta_u=1$ and $\eta_o=1/\delta$" | 已覆盖。两份都取 η_u = 1，正文约定（η_u, η_o ≥ 1）与 convention B（η_u, η_o > 0）都满足；陈述只用 η，不需要 lem:scaling |
| OPT > 0 与 OPT 的值 | 甲 `The pair is admissible…` 末："$\max_{\lvert S\rvert\le K}f_O(S)=f_O(O)=K$, because $\gamma\le1$ makes the $K$ largest modular coefficients exactly those of $O$"。乙 proof："while $\mathrm{OPT}\ge f(O)=K$" | 已覆盖；K ≥ 1 故 OPT = K > 0，model.tex 的 "f(O*) = 0 时比值陈述平凡成立"旁路不被触发 |
| K ≥ 2 是否需要 | 甲 setup："Fix $K\ge1$ and $n\ge2K$"，全程不需要 K ≥ 2。乙 未写 K 的定义域 | 甲 已覆盖（K ≥ 1 足够）；乙 **GAP**（K 域缺，仅由 model.tex 的 1 ≤ K ≤ n 继承） |
| tie breaking（adversarial ties） | 甲、乙 都不涉及：陈述全称于任意确定性算法，tie breaking 是 predictive greedy 的内部规则。但若把 A 特化为 predictive greedy，f̃(S) = \|S\| 使每步所有候选并列，必须 adversarial tie breaking 才能走出与 O 不交的轨迹；两份路线一材料都没写这句（`results/V11/route2/nobound.md` Step 11' 写了） | **GAP**（对本陈述的真值无影响，属正文引用时的缺口） |
| 界 K/(n−K) 的来源与松紧 | 甲 `Deterministic algorithms.` 不等式链：$f_O(T)/f_O(O^{\ast})=\gamma\lvert T\rvert/K\le\gamma=K^{2}/(n(n-K))\le K/(n-K)$，确定性条款上**严格更强**（差一个因子 K/n）。乙 proof 末：$f(T)\le\delta\cdot\mathrm{OPT}=\tfrac{K}{n-K}\cdot\mathrm{OPT}$，恰好取到陈述的常数 | 已覆盖；陈述的常数由甲的随机段决定（甲 第 132 至 139 行注释自述："the constant in Proposition prop:necessity is the price of covering randomized algorithms"） |
| 随机算法条款的量词（固定 random string / 期望对谁取） | 甲 `Randomized algorithms.`：先对均匀随机 K-子集 O 取期望（"the hypergeometric mean gives $\mathbb E[\lvert T\cap O\rvert]=\mathbb E\lvert T\rvert\cdot K/n\le K^{2}/n$"），再用 "$\min_{O}\le\mathbb E_{O}$ produces a single $O$ attaining the bound in expectation over the random string"，即量词为"∃ 固定 instance 使 E_{random string}[·] ≤ 界"，与台账"随机版"字段的规格一致。乙 无随机段 | 证明已覆盖（甲）；**陈述层 GAP**（正文与台账陈述都只管 deterministic，台账明确"不声称"，属有意为之）；乙 若单独留用会丢该段 |
| 第二句"no constant"的隐含量词（固定 K，n→∞） | 甲 `Randomized algorithms.` 末："Letting $n\to\infty$ with $K$ fixed drives the right side to $0$"。乙 remark 走另一条路：不经 n→∞，直接由"any $\delta\in(0,1]$ gives $f(T)\le\delta\cdot\mathrm{OPT}$ with $\eta=1/\delta$"得出 | 证明已覆盖；**陈述层 GAP**（正文第二句未写"固定 K、n→∞"或"对任意 δ"） |
| 其他模板形容词（at most nK queries、fixed K steps、error exactly / at most、\|S\| ≤ K） | 本陈述不含这些限定；它们属 thm:linear-exact、prop:guarantee、thm:hardness 的卡 | 不适用 |

### 2.1 模板附带问题

- "thm:ceiling 的随机段落 fixed random string 量词是否在陈述里"：本项审计的 statement 是 prop:necessity，不适用，留给 thm:ceiling 那一项。就本命题而言，对应问题的答案见上表倒数第三行：随机量词只在路线一甲的证明段里，正文陈述与台账陈述都没有，台账明确记为"不声称"。
- "thm:linear-exact 的 n ≥ 4K^5 能否紧到约 K³(K−1)²/2 + K²"：不适用（那是 app:greedybudget 与 T10c 的项）。本文件不对该数做任何断言，以免与该项的审计结论冲突。

---

## 3. GAP 清单

| 编号 | GAP | 影响 | 保守处理建议（本次不改任何文件） |
|---|---|---|---|
| G1 | 陈述层：\|T\| ≤ K 未写，正文与台账都只写 "the output T" | 字面上若允许 \|T\| > K，取 T = N 即得 f(T) > f(O*)，命题不成立 | 在陈述里补 "feasible output T, \|T\| ≤ K"，或在 Model 里把"算法输出可行解"写成模型条款 |
| G2 | 陈述层：第二句的量词（固定 K、n→∞，或"对任意 δ ∈ (0,1]"）未写 | "no constant" 相对于谁没有说清，属空洞性检验第 41 行意义上的待补限定 | 第二句改为带量词的版本，或把它移到 remark |
| G3 | 陈述层：pair 需满足"除 η 上界外 Section 2 的全部假设"未写 | HANDOFF_ADDENDUM §B 第 9 条已要求这句措辞，正文与台账均未落实 | 按 addendum 第 9 条补入（正文改动不在本次授权内） |
| G4 | 模型层："query" 与 "arbitrary query access" 无定义 | prop:necessity 与 thm:ceiling 都用这个形容词，model.tex 只有"只能 query f̃"一句 | HANDOFF §8 的 Model 重写含"each evaluation is one query"，落地后此 GAP 关闭 |
| G5 | tie breaking：两份路线一材料都没写"特化为 predictive greedy 时需要 adversarial tie breaking" | 对本陈述真值无影响（陈述全称于任意确定性算法）；正文若用本构造谈 greedy 会缺一句 | 附录加一句，或引 `results/V11/route2/nobound.md` Step 11' |
| G6 | 随机条款只存在于路线一甲的证明段；陈述层没有，乙无随机段 | 若按 MISSING_INPUTS 的建议只保留乙、删甲的 γ 构造，随机段与 γ 的平衡取法一并丢失 | 删甲之前把 `Randomized algorithms.` 段迁到乙，或在乙的 remark 里保留 γ = K²/(n(n−K)) 的取法 |
| G7 | 乙未写 K 的定义域；δ ≤ 1 只以区间断言 "$\delta\in(0,1]$" 给出 | 读者需自己从 n ≥ 2K 推出 n − K ≥ K | 乙 补 "Fix K ≥ 1" 与一句 δ ≤ 1 的理由 |
| G8 | 两份路线一材料常数不同（γ = K²/(n(n−K)) 与 δ = K/(n−K)），label 也不同（`prop:necessity` / `app:necessity` 对 `prop:nobound` / `app:model`），乙未 \input | 同一命题在仓库里有两份不等价的证明；乙的确定性界恰好取到陈述常数，甲的确定性界比陈述强 K/n 倍 | 按 MISSING_INPUTS 的记录，接线与二选一留给作者；本次不动 |

---

## 4. 两份路线一材料的定量对照（精确算术复核）

复核脚本（写在 scratchpad，不入仓库）：`/tmp/claude-0/-home-user/09d7d9a5-0b14-54a1-894a-d76a6d641333/scratchpad/check_nobound_quant.py`。

- 恒等式 K/n + K²/(n(n−K)) = K/(n−K)：sympy 化简得 0。[VERIFIED-SYMBOLIC]（甲随机段的关键一步）
- K/(n−K) − γ = K/n > 0，故甲的确定性界严格强于陈述常数。[VERIFIED-SYMBOLIC]
- δ = K/(n−K) ≤ 1 当且仅当 n ≥ 2K。[VERIFIED-SYMBOLIC]
- 确定性条款穷举：K ∈ {1,2,3}，n 从 2K 到 2K+5，对所有 |T| ≤ K 与两种构造逐一验算 f(T) ≤ K/(n−K)·OPT，全部成立。[VERIFIED-EXHAUSTIVE]
- 随机条款穷举：K ∈ {2,3}，n ∈ {2K, 2K+2}，对所有 |T| = K 取 O 均匀随机的精确平均，最坏值分别为 3/4 ≤ 1、4/9 ≤ 1/2、3/4 ≤ 1、33/64 ≤ 3/5，全部不超过界。[VERIFIED-EXHAUSTIVE]

| n | K | 甲的 γ | 甲的 η = 1/γ | 乙的 δ | 乙的 η = 1/δ | 陈述的界 K/(n−K) |
|---|---|---|---|---|---|---|
| 7 | 3 | 9/28 | 28/9 | 3/4 | 4/3 | 3/4 |
| 8 | 3 | 9/40 | 40/9 | 3/5 | 5/3 | 3/5 |
| 6 | 2 | 1/6 | 6 | 1/2 | 2 | 1/2 |
| 8 | 2 | 1/12 | 12 | 1/3 | 3 | 1/3 |

读法：乙用更小的 η 达到同一个界（确定性条款上更省），甲用更大的 η 换来随机条款也成立。两者都不与陈述冲突。

---

## 5. 结论

- A：**A_match = false**，四条差异 D1 至 D4，均为口径与覆盖范围差异，无数学冲突。
- E：21 行量词审计表，路线一（甲）覆盖除 tie breaking 之外的全部行；GAP 共 8 条，其中 G1 至 G3 为陈述层省略（证明里有、陈述里没有），G4 为模型定义层，G5 至 G8 为材料层。
- 本次未修改任何已有文件，未运行 git。本文件是新建文件。

---

## 6. 状态标签小结

- 命题本身：[HAND-PROOF-UNREVIEWED]（台账 T1 原状；两条 information-theoretic 步骤，即 transcript 与 O 无关、输出为固定集合，没有 oracle 可直接检验）。
- 构造的合法性与两条不等式链：[VERIFIED-EXHAUSTIVE]（K ≤ 3，n ≤ 2K+5）+ [VERIFIED-SYMBOLIC]（三条恒等式 / 不等式）。
- 一般 (n, K) 的代数：[HAND-PROOF-UNREVIEWED]。

## 7. 读过的文件

- `/home/user/sub-modular-optimization/results/V11/statements.md`
- `/home/user/sub-modular-optimization/results/V11/inputs/statement_nobound.md`
- `/home/user/sub-modular-optimization/results/V11/inputs/definition1.md`
- `/home/user/sub-modular-optimization/results/V11/inputs/assumptions.md`
- `/home/user/sub-modular-optimization/results/V11/MISSING_INPUTS.md`
- `/home/user/sub-modular-optimization/results/V11/route2/nobound.md`
- `/home/user/sub-modular-optimization/THEOREM_LEDGER.md`（T0、T1、T2 卡）
- `/home/user/sub-modular-optimization/paper/sections/results.tex`（prop:necessity 环境与其后注释）
- `/home/user/sub-modular-optimization/paper/sections/model.tex`
- `/home/user/sub-modular-optimization/paper/sections/appendix_proofs.tex`（app:necessity，第 80 至 141 行）
- `/home/user/sub-modular-optimization/paper/sections/appendix_model_proofs.tex`
- `/home/user/sub-modular-optimization/paper/main.tex`（确认 appendix_model_proofs 未 \input）
- `/home/user/sub-modular-optimization/CLAUDE.md`
- `HANDOFF_2026-09-18.md` 与 `HANDOFF_ADDENDUM_2026-09-18.md`（uploads 版，与仓库根目录同名文件一致）
