# 量词审计（criteria A 与 E）：thm:linear-exact / 台账 T10c（来源 J6，TASKS11 Q6，正文 Theorem 2）

本文件只做两件事：A 项逐量词比对正文环境与台账卡；E 项建立量词审计表，把陈述里的每个量词与形容词
落到路线甲证明的具体位置，落不上的记 GAP。附带回答 TASKS11 给本条目的专项问题：
app:greedybudget 的计数链能否把 n ≥ 4K⁵ 收紧到约 K³(K−1)²/2 + K²（§3）。

范围与纪律：不修改任何已有文件，不运行 git。本文件自身的算术用 sympy 与 `fractions.Fraction`
精确核对（结果见 §5），浮点只出现在打印里。状态标签按 CLAUDE.md：[VERIFIED-SYMBOLIC]
[VERIFIED-LP] [VERIFIED-EXHAUSTIVE] [HAND-PROOF-UNREVIEWED] [CONJECTURE] [FAILED]。
读过的文件见 §6。

---

## 1. Criterion A：正文陈述与台账陈述的逐量词比对

### 1.1 三份原文

正文：`paper/sections/results.tex` 第 756 至 789 行，environment `theorem`，双 label
`thm:linear-exact` 与 `cor:greedybudget`，标题 "Exact optimality within the greedy query budget"。
环境之前第 747 至 754 行是引导段（把预算从 n^c 尺度换成 greedy 自己的预算），
之后第 791 至 829 行是 `rem:greedybudget`（旧天花板对比、n=4 K=2 反例、η=1 与 K=1 情形）。

矩阵输入：`results/V11/statements.md` 第 244 至 281 行的 LaTeX 块与
`results/V11/inputs/statement_linear_exact.md` 第 6 至 36 行。两者与正文 environment
**逐字符相同**（本次以 python 去掉注释行后做全等比较，两项均为 True，§5 第 8 条）。
因此 A 项的实质比对对象是正文 environment 对台账卡的中文陈述行。

台账：`THEOREM_LEDGER.md` 第 290 至 329 行，卡 `## T10c thm:linear-exact`。
其中"陈述"行是第 294 至 301 行（含 (i)、(ii) 与随机版三段），
另有"构造"（302–305）、"关键点"（306–310）、"状态"（311–318）、"量词检验"（319–322）、
"禁止声称"（323–326）、"与旧卡关系"（327–329）六组，A 项只比对"陈述"行。

### 1.2 逐项对照

| 量词 / 形容词 | 正文（results.tex 756-789） | 台账（T10c 陈述行 294-301） | 判定 |
|---|---|---|---|
| $K\ge2$ | "Let $K\ge2$" | "K ≥ 2" | 一致 |
| $\eta>1$ | "$\eta>1$" | "η > 1" | 一致 |
| $n\ge4K^{5}$ | "$n\ge4K^{5}$" | "n ≥ 4K⁵" | 一致 |
| 类 $\mathcal A_{\mathrm{lin}}$ deterministic | "the class of deterministic algorithms" | "确定性" | 一致 |
| 查询次数 ≤ nK | "at most $nK$ queries to $\tilde f$" | "≤ nK 次 f̃ 查询" | 一致 |
| 每次查询集合大小 ≤ K | "each on a set of size at most $K$" | "每次查询集合大小 ≤ K" | 一致 |
| 输出集合大小 ≤ K | "output a set of size at most $K$" | "输出 ≤ K 元素" | 一致 |
| predictive greedy 属于该类 | "predictive greedy, **at** $Kn-K(K-1)/2$ queries, belongs to $\mathcal A_{\mathrm{lin}}$" | "predictive greedy 用 **≤** Kn−K(K−1)/2 次查询，属于该类" | **差异 D7**（at 对 ≤） |
| ∀ $A\in\mathcal A_{\mathrm{lin}}$ | "For every $A\in\mathcal A_{\mathrm{lin}}$" | "对任意 A ∈ 𝒜_lin" | 一致 |
| ∀ prescribed split，$\eta_u,\eta_o\ge1$，$\eta_u\eta_o=\eta$ | "every prescribed split $\eta_u,\eta_o\ge1$ with $\eta_u\eta_o=\eta$" | "任意给定拆分 η_u, η_o ≥ 1、η_uη_o = η" | 一致 |
| ∃ instance $(f,\tilde f)$（实例在 $A$ 与拆分之后） | "there is an instance $(f,\tilde f)$" | "存在实例 (f, f̃)" | 一致（量词顺序同） |
| $f$ monotone submodular | "with monotone submodular $f$" | "f 单调 submodular 归一化" | **差异 D1**（归一化只在台账） |
| 误差因子"恰为"$(\eta_u,\eta_o)$ | "whose **smallest admissible** error factors in Definition~\ref{def:eta} are exactly $(\eta_u,\eta_o)$" | "**实际单元素**误差因子恰为 (η_u, η_o)" | **差异 D2**（single-element 只在台账；smallest admissible 只在正文） |
| 结论式 $f(T)/f(O^{\ast})\le\rho_K(\eta)$ | 有 | "使 f(T)/f(O*) ≤ ρ_K(η)" | 一致 |
| 与 thm:exact 合并的适用域 | "Theorem~\ref{thm:exact}, **whose guarantee holds on every instance with error at most $\eta$**" | 只写"与 thm:exact 合并" | **差异 D3**（正文多一个适用域子句） |
| sup–inf 等式 | $\sup_{A}\inf_{(f,\tilde f)}f(A^{\tilde f})/f(O^{\ast})=\rho_K(\eta)$ | "sup_{A ∈ 𝒜_lin} inf_{(f,f̃)} f(A)/OPT = ρ_K(η)" | 一致（两边都没写 inf 的定义域，见 E 表第 24 行） |
| 在每个这样的 n 上精确 | "at every such $n$" | "值在每个 n ≥ 4K⁵ 处精确" | 一致 |
| 无渐近 | "with no asymptotics in $n$ **or $K$**" | "夹逼闭合，无 n → ∞ 极限" | **差异 D4**（K 的无渐近只在正文） |
| 随机版：∀ randomized，同预算 | "For every randomized algorithm with the same budget" | "对任意同预算随机算法" | 一致 |
| 随机版：∃ instance，误差 | "there is again an instance **with error exactly $\eta$**" | "存在实例"（无误差校准） | **差异 D5** |
| 随机版：expectation 的对象 | "the expectation over **the algorithm's randomness**" | "E_seed[f(T)/f(O*)]" | 一致 |
| 随机版：$\varepsilon_n$ 的值 | $\varepsilon_n=K^{2}/n+K^{5}/(2n)$ | ε_n = K²/n + K⁵/(2n) | 一致 |
| 随机版：$\varepsilon_n$ 的来源注 | 无 | "（装配给 K/n + K⁵/(2n)，K²/n 沿 T10b 保守取整）" | **差异 D6**（值相同，出处注只在台账） |
| 随机版：不声称有限 n 精确 | "the matching is therefore asymptotic in $n$ at fixed $K$, and no exact finite-$n$ statement is claimed" | "不声称随机类有限 n 精确" | 一致（正文多写"at fixed K"，与 D4 同源） |
| adversarial ties / fixed K steps | 不出现 | 不出现 | 一致（两边都继承 model.tex，见 E 表第 17、18 行） |
| $f(\emptyset)=0$、$\tilde f(\emptyset)=0$、OPT > 0、$1\le K\le n$ | 不出现 | 只有"归一化"一词（见 D1） | 见 D1，其余一致（继承 model.tex） |

### 1.3 A_diffs

**A_match = false**，共 7 条差异：

- **D1（归一化）**：台账写"f 单调 submodular 归一化"，正文 environment 只写
  "monotone submodular $f$"。$f(\emptyset)=0$ 由 `model.tex` 第 9 行的全局设定承担，
  构造侧 app:greedybudget 也证了 $F(0,0)=0$ 与 $\tilde f(\varnothing)=0$，
  所以这是**呈现层的缺词而不是内容分歧**，但按 A 项的规则它落在差异里。
- **D2（single-element 对 smallest admissible）**：台账写"实际**单元素**误差因子恰为"，
  正文写"**smallest admissible** error factors in Definition~\ref{def:eta} are exactly"。
  `def:eta`（model.tex 第 23 至 32 行）本身带 "(single-element, multiplicative)" 限定，
  所以正文经由 Definition 1 指针继承了 single-element；反过来台账没有 "smallest admissible"
  这层"是最小可行因子而不是某组可行因子"的措辞。两个方向各缺一半，记为一条差异。
- **D3（thm:exact 的适用域）**：正文在合并处插入 "whose guarantee holds on every instance
  with error at most $\eta$"，台账的 (ii) 只说"与 thm:exact 合并"。这一句是 sup–inf 等式
  两侧实例族对齐的唯一说明（上界侧实例误差**恰为** η，下界侧保证对误差**至多** η 成立），
  所以它是承重的，缺它会让 inf 的定义域更不清楚。
- **D4（no asymptotics in K）**：正文写 "with no asymptotics in $n$ or $K$"，
  台账只写"无 n → ∞ 极限"。K 方向的无渐近在台账卡里出现在别处（第 280 至 282 行 T10b 的
  "Q4 日更新"与本卡标题的"有限 K"），但不在陈述行内。
- **D5（随机版的误差校准）**：正文写 "an instance with error exactly $\eta$"，
  台账随机版行只写"存在实例"。另外两边都在随机版里**不**重复 split 量词，这一点一致。
- **D6（ε_n 的出处注）**：ε_n 的值两边相同；台账多一个括号注说明装配实际给的是
  K/n + K⁵/(2n)，K²/n 是沿 T10b 的保守取整。正文把这一步写在 app:greedybudget 第 1896 至
  1899 行（"The theorem states the slightly larger $\varepsilon_n$..."），不在 environment 内。
- **D7（greedy 的查询次数：at 对 ≤）**：正文写 "at $Kn-K(K-1)/2$ queries"（等号读法），
  台账写"用 ≤ Kn−K(K−1)/2 次查询"（不等号读法）。附录第 1874 至 1877 行给的是等号
  $\sum_{t=0}^{K-1}(n-t)=nK-K(K-1)/2\le nK$，与正文一致；台账的 ≤ 更弱，不影响结论。

不计入 A_diffs 的呈现差异一条：台账用 (i)/(ii) 编号加"夹逼闭合"的说法，正文用散文加
"predictive greedy is exactly optimal within its own query budget"。两者内容相同。

---

## 2. Criterion E：量词审计表（落到路线甲）

路线甲 = `paper/sections/appendix_proofs.tex` 的
`\subsection{Exact optimality at the greedy budget (Theorem~\ref{thm:linear-exact})}`
`\label{app:greedybudget}`（第 1701 至 1928 行），段落锚点：
`\paragraph{The double-residual family.}`（1723）、`\paragraph{Legality.}`（1750）、
`\paragraph{Small-set indistinguishability and the rigid trajectory.}`（1793）、
`\paragraph{The value.}`（1823）、`\paragraph{Counting at the budget $Q=nK$.}`（1835）、
`\paragraph{Transcript induction and the two directions.}`（1857）、
`\paragraph{Randomized algorithms.}`（1885）、
`\paragraph{The improvement over the former ceiling.}`（1907，只服务 rem:greedybudget）。
数据来源 `results/J6/linear_exact.md`（第 114 行定理陈述、第 120 行证明、第 122 行随机版推论）；
脚本 `results/Q4_gpt_check.py`、`results/Q4_symbolic_ineq.py`、`results/Q4_indep_check.py`、
`results/Q4_smallset_lp.py`、`results/L1_table.py`（section 1 是计数链）。

状态列：**OK** = 路线甲有明确处理；**OK(隐含)** = 有处理但无独立句子；**部分** = 有处理但缺一步
或缺定义；**GAP** = 路线甲没有对应位置；**N/A** = 本陈述没有这个量词。

| 量词 / 形容词 | 处理位置（file + paragraph） | 状态 |
|---|---|---|
| 1. $K\ge2$ | app:greedybudget `The double-residual family.`（1724 行 "Fix $K\ge2$, $\eta>1$ and a split"）；实际消费点是 $c_y=(K-y)/(K-1)$ 与 $h_x$ 的 $\frac{K-1}{K}q^{x}$（$K=1$ 时分母为 0）；$K=1$ 由 `rem:greedybudget`（results.tex 第 824 至 828 行）单独处理 | OK |
| 2. $\eta>1$ | 同 1724 行的设定句。附录内**没有任何一步消费严格性**：族在 $\eta=1$ 处仍有定义，$j=K-1$、$F(K,0)=L_K(1)=\rho_K(1)$（本审计电池，$K=2..8$，§5 第 6 条 [VERIFIED-SYMBOLIC]）；正文把 $\eta=1$ 另走 `rem:greedybudget` 第 818 至 823 行的 app:hardness 退化族 | **部分**（形容词是充分设定，非承重；两条路线在 $\eta=1$ 处结论一致） |
| 3. $n\ge4K^{5}$ | `Counting at the budget $Q=nK$.`（1835）末段 "Under $n\ge4K^{5}$ the first term is at most $\tfrac18$ and the second is at most $1/(4K^{3})\le\tfrac1{32}$, so the total is at most $\tfrac5{32}<\tfrac12$"；`results/L1_table.py` section 1 的 (c)(c')(c'')(c''') [VERIFIED-SYMBOLIC] | OK（充分非必要，见 §3） |
| 4. 形容词 deterministic | `Transcript induction and the two directions.`（1857）首句 "Run the algorithm against the canonical oracle ... this fixes queries $S_1,\dots,S_Q$ and output $T_0$ **independently of $O$**"：确定性正是"transcript 只由答案决定"的前提 | OK |
| 5. 查询次数 ≤ nK | `Counting at the budget $Q=nK$.`（1835）"the canonical transcript's $Q=nK$ queries $S_1,\dots,S_Q$"；同段末 1878 至 1881 行 "The only property of the budget that the computation uses is $Q\le n^{2}/(4K^{4})$, which $Q=nK$ satisfies exactly when $n\ge4K^{5}$" | OK（本审计核对 $Q\cdot\binom K2(K/n)^2\le1/8\iff Q\le n^{2}/(4K^{3}(K-1))$，正文再放宽到 $n^{2}/(4K^{4})$，§5 第 2 条） |
| 6. 每次查询 $\lvert S\rvert\le K$ | `Small-set indistinguishability and the rigid trajectory.`（1793）"$\tilde f(S)=\widehat H_{\lvert S\rvert}/\eta_u$ whenever $\lvert S\rvert\le K$ and $\lvert S\cap O\rvert\le1$"；同段给出大集合的泄漏数字（$K=3,\eta=3/2$：$(x,y)=(6,0)$ 得 61/48，$(5,1)$ 得 4/3） | OK（恒等式与泄漏均经本审计精确复算，§5 第 4、5 条 [VERIFIED-SYMBOLIC]；LP 侧 `results/Q4_smallset_lp.py` [VERIFIED-LP]） |
| 7. 输出集合大小 ≤ K | `Transcript induction ...`（1857）"The actual output is therefore $T_0$, disjoint from $O$ and of size at most $K$, so monotonicity and the value paragraph give $f(T_0)/f(O^{\ast})\le F(K,0)$" | OK（$\lvert T_0\rvert<K$ 由 $r_x$ 非增即 $F(x,0)\le F(K,0)$ 兜住） |
| 8. predictive greedy ∈ $\mathcal A_{\mathrm{lin}}$ | `Transcript induction ...`（1874 至 1877 行）"predictive greedy spends $\sum_{t=0}^{K-1}(n-t)=nK-K(K-1)/2\le nK$ queries, all of size at most $K$, by retaining previously queried values" | OK（求和恒等式 §5 第 7 条 [VERIFIED-SYMBOLIC]；"retaining previously queried values" 即 memoization，是该计数的前提，附录已写明） |
| 9. ∀ $A\in\mathcal A_{\mathrm{lin}}$（实例依赖算法） | `Transcript induction ...`（1857）canonical transcript 是对给定算法定义的；台账"禁止声称"第 325 行明写"(i) 的实例对全部算法统一"不可声称 | OK |
| 10. ∀ prescribed split $(\eta_u,\eta_o)$ | `The double-residual family.`（1724）"Fix ... a split $\eta_u,\eta_o\ge1$ with $\eta_u\eta_o=\eta$"；`Legality.`（1750）末 "Hence on every edge $\Delta F/\eta_u\le\Delta\tilde f\le\eta_o\Delta F$ for $\tilde f=H/\eta_u$" | OK（族只经 $H=\eta_u\tilde f$ 依赖拆分，$F$ 与 $H$ 都与拆分无关） |
| 11. 误差因子"恰为"$(\eta_u,\eta_o)$（下确界被取到） | `Legality.`（1750）末句 "Both split endpoints are attained on positive-gain edges already at $x=0$ (the first $O$-edge has ratio $1/\eta_u$ in $\tilde f$-form, the second $\eta_o$), so the smallest admissible error factors of Definition~\ref{def:eta} are exactly $(\eta_u,\eta_o)$" | OK（四类边比值表与两端点达到：`results/Q4_symbolic_ineq.py` 34 条分支不等式 [VERIFIED-SYMBOLIC]；`results/Q4_indep_check.py` 111 组精确电池 [VERIFIED-LP]） |
| 12. $f$ monotone | `Legality.`（1750）"The first differences of $F$ are ... all nonnegative by (i)--(ii)" | OK |
| 13. $f$ submodular | 同段 "each is nonincreasing in $x$ and in $y$, which is submodularity on the count grid, and chaining single-element additions transfers monotonicity and diminishing returns to the set function $f$" | OK(格点层) + **部分（提升层）**：count-grid → 集合函数的 DR 链接状态 [HAND-PROOF-UNREVIEWED]（第 1719 至 1722 行的注释与台账第 317 至 318 行都写明） |
| 14. 归一化 $f(\emptyset)=0$ 与 $\tilde f(\varnothing)=0$ | `Legality.`（1750）"Moreover $F(0,0)=0$" 与 "$H(0,0)=C-1-(\eta-1)(K-1)/K=0$ gives $\tilde f(\varnothing)=0$" | OK（本审计电池核对 $F(0,0)=H(0,0)=0$，§5 第 4 条） |
| 15. OPT > 0 与 $O^{\ast}=O$ | `Legality.`（1750）"$F(0,0)=0$, $F(0,K)=1$ and $0\le F\le1$ on the entire grid, so $O$ is optimal under the cardinality constraint and $f(O)=1$" | OK（$f(O^{\ast})=1>0$，比值良定义；$f(O^{\ast})=0$ 的退化由 model.tex 第 15 至 16 行的全局约定承担） |
| 16. 构造所需的 ground-set 大小 | `The double-residual family.`（1723）"On a ground set $N=B\sqcup O$ with $\lvert O\rvert=K$ and $\lvert B\rvert=n-K$"；同段末 "The formulas do not involve $n$: every $n\ge2K$ restricts the same table to its available count grid" | OK（族的最低要求是 $n\ge2K$，被定理的 $n\ge4K^{5}$ 严格覆盖；$n$ 只在计数段起作用） |
| 17. tie-breaking（adversarial） | `Small-set indistinguishability and the rigid trajectory.`（1793）末段 "At every state $(t,0)$, $t<K$, the predicted marginals of all remaining elements tie at $q^{\min(t,j)}/(K\eta_u)$, so adversarial tie-breaking keeps greedy inside $B$ for all $K$ steps" | OK；注意**这一句只服务下界侧的刚性轨迹演示**，上界方向（任意 $A$）不用 tie，匹配方向的 tie 假设在 thm:exact 里 |
| 18. fixed $K$ steps | 同段 "for all $K$ steps"；定义在 `model.tex` 第 70 至 74 行 "The run always executes exactly $K$ steps" | OK(模型层继承)（陈述与台账都不写，见 A 表末两行） |
| 19. 值 $F(K,0)=V_j=\rho_K(\eta)$ | `The value.`（1823）"$\frac{f(T)}{f(O)}=F(K,0)=1-Q+(K-j)\delta=V_j(\eta)$" 加相邻支恒等式 $V_{j+1}-V_j=q^{j}(\eta-K+j)/(K\eta k_1)$ 与 "$j=\max\{0,K-\lfloor\eta\rfloor\}$ minimizes over branches, with ties exactly at integer $\eta$" | OK（本审计电池：$K=2..8$、11 个 $\eta$ 上 $F(K,0)=V_j=\min_i V_i$，§5 第 4 条 [VERIFIED-SYMBOLIC]） |
| 20. "at every such $n$，无 $n$ 渐近" | `The value.`（1823）末 "Hence $F(K,0)=\rho_K(\eta)$ for every $n\ge2K$: the value is exact at each $n$, and no limit is taken" | OK |
| 21. "无 $K$ 渐近" | 路线甲没有专门句子；它由"每一步都在固定有限 $K$ 上做"隐含（计数段的常数 $\binom K2$、$K^{5}/2$、$K^{2}$ 都是固定 $K$ 的算术；唯一取 $K\to\infty$ 的是 `The improvement over the former ceiling.`（1907），那段只服务 rem:greedybudget） | **部分**（无落点句子，但也没有任何一步取 $K$ 的极限） |
| 22. 下界方向（matching）：greedy 达到 $\rho_K$ 且适用于误差**至多** $\eta$ 的实例 | `Transcript induction ...`（1874 至 1877 行）"and achieves $\rho_K(\eta)$ on every instance with error at most $\eta$ (Theorem~\ref{thm:exact}); together these give the sup--inf identity" | OK（引用 thm:exact，其自身状态见 `results/V11/audit/exact.md`） |
| 23. 上界侧实例的误差"恰为 $\eta$"与拆分的实现 | `Transcript induction ...`（1872 至 1874 行）"with error exactly $\eta$ and any prescribed split realized directly by $\tilde f=H/\eta_u$" | OK |
| 24. sup–inf 里 **inf 的定义域** | 陈述里写作 $\inf_{(f,\tilde f)}$，没有写"在误差至多 $\eta$、$f$ 单调 submodular 归一化、ground set 大小恰为 $n$ 的实例上取 inf"；附录 1876 至 1877 行只说 "together these give the sup--inf identity"，也没有把定义域写出来。唯一的线索是正文里的 D3 子句（"error at most $\eta$"） | **GAP-1** |
| 25. 随机版：∀ randomized，同预算 | `Randomized algorithms.`（1885）"for every randomized algorithm of the class" | OK |
| 26. 随机版：expectation 只对算法随机性 | 同段末 "The quantifier order is that of Theorem~\ref{thm:hardness}: the instance may depend on the algorithm, and the expectation is over the algorithm's randomness only" | OK |
| 27. 随机版：fixed random string | **陈述里没有"fixed random string"，也不需要**（陈述用的是 expectation 量词）。附录把定 seed 作为证明装置：`Randomized algorithms.`（1885）"fixing the seed and its canonical transcript ... averaging over the seed and then selecting one $O$ no worse than the average" | OK（见 §4 的专项回答） |
| 28. 随机版：$\varepsilon_n=K^{2}/n+K^{5}/(2n)$ 与装配值的差 | 同段 "The theorem states the slightly larger $\varepsilon_n=K^{2}/n+K^{5}/(2n)$, matching the deterministic output count"（装配给的是 $K/n+K^{5}/(2n)$） | OK（与台账第 301 行括号注一致，即 A 表的 D6） |
| 29. 随机版：不声称有限 $n$ 精确 | 同段末（1899 至 1902 行）"The additive term vanishes only in the joint limit $n/K^{5}\to\infty$; at fixed $n$ it does not, and no exact finite-$n$ randomized statement is claimed" | OK |
| 30. 随机版实例的误差"恰为 $\eta$"（正文 D5 的那半句） | `Randomized algorithms.`（1885）只说 "a single instance"，没有重述误差校准；它继承自同一个族（族的误差恒为 $\eta$，见第 11 行） | **部分**（继承成立，缺一句话） |
| 31. 隐含：$\tilde f$ 不必 submodular | 族本身不 submodular（$H$ 的 $y$ 方向有 $\eta c_y h_x$ 的跳变）；`model.tex` 第 18 至 20 行的 D1 决定写明主模型对 $\tilde f$ 无结构假设 | OK(隐含)（路线甲无句子，属模型层继承） |
| 32. 隐含：算法可自适应（adaptive） | `Transcript induction ...`（1857）"identical previous answers determine the same next query, and the small-set identity above supplies the same answer" | OK（状态 [HAND-PROOF-UNREVIEWED]，见第 1719 至 1722 行的注释） |
| 33. 隐含：算法只能查 $\tilde f$（不能查 $f$） | `Transcript induction ...`（1857）"Run the algorithm against the canonical oracle $S\mapsto\widehat H_{\lvert S\rvert}/\eta_u$ for $\lvert S\rvert\le K$"；模型层在 model.tex 第 10 至 12 行 | OK |
| 34. arbitrary query access（任意大小查询） | 本陈述**没有**这个形容词，恰恰相反（$\lvert S\rvert\le K$）。任意大小的对应结果是 T10d / `thm:linear-anysize`，其附录 app:hardness-anysize 第 2011 至 2015 行明写 "Theorem~\ref{thm:linear-exact} inherits that restriction" | N/A |
| 35. 本条目不含的量词：$\eta$ 的上端限制、$\tau$、$n^{c}$ 预算、$K>\tau$ | 属 thm:hardness（T10） | N/A |

### 2.1 GAP 与"部分"汇总

- **GAP-1（唯一的真 GAP，表第 24 行）：sup–inf 等式里 inf 的定义域没有写出来。**
  正文与台账的 display 都写 $\inf_{(f,\tilde f)}$ 而不带下标条件；app:greedybudget 第 1876 至
  1877 行的收束句也不写。要让等式成立，inf 必须取在"误差至多 $\eta$、$f$ 单调 submodular
  归一化、ground set 大小为该 $n$"的实例族上：上界侧给的实例误差**恰为** $\eta$（属于该族），
  下界侧 thm:exact 的保证对误差**至多** $\eta$ 成立（覆盖该族）。正文靠 D3 那个从句
  提示了一半，台账连这半句也没有。保守处理：不动正文，只记录；矩阵里本条目的 sup–inf 行
  应注明"inf 定义域靠上下文推断"。
- **部分-1（表第 2 行）**：$\eta>1$ 在 app:greedybudget 里没有被消费的位置。空洞性检验的结论是
  它**不空洞但也不承重**：去掉它（取 $\eta=1$）族仍合法且 $F(K,0)=L_K(1)=\rho_K(1)$
  （§5 第 6 条 [VERIFIED-SYMBOLIC]），结论不变；正文另走 rem:greedybudget 的退化族，属于
  保守重复。建议记录而不改文。
- **部分-2（表第 13 行）**：count grid 的 submodularity 到集合函数 $f$ 的提升
  （"chaining single-element additions"）状态 [HAND-PROOF-UNREVIEWED]，这是整条定理里
  三处未验证装配之一（另两处是 canonical transcript 归纳与随机版两次平均）。
- **部分-3（表第 21 行）**："no asymptotics in **$K$**" 在路线甲没有落点句子。
- **部分-4（表第 30 行）**：随机版实例的"误差恰为 $\eta$"在附录随机段没有重述，靠同族继承。
- 次要记录（不计入 GAP）：表第 17 行的 adversarial tie 只服务下界侧的刚性轨迹演示，
  上界方向不用它；表第 18、31 行是模型层继承；表第 5 行的预算条件在附录被放宽成
  $Q\le n^{2}/(4K^{4})$，比精确形式 $Q\le n^{2}/(4K^{3}(K-1))$ 松（§5 第 2 条）。

---

## 3. 专项问题：计数链能否把 $n\ge4K^{5}$ 收紧到约 $K^{3}(K-1)^{2}/2+K^{2}$

### 3.1 链条原文（`paper/sections/appendix_proofs.tex` 第 1835 至 1856 行）

> For a uniformly random $K$-subset $O$,
> $\Pr[R\subseteq O]=\frac{K(K-1)}{n(n-1)}=\bigl(\frac Kn\bigr)^{2}-\frac{K(n-K)}{n^{2}(n-1)}\le\bigl(\frac Kn\bigr)^{2}$,
> so one query is unbalanced with probability at most $\binom K2(K/n)^{2}$, and the canonical
> transcript's $Q=nK$ queries $S_1,\dots,S_Q$ together with its output $T_0$ fail with
> probability at most
> $nK\binom K2\bigl(\frac Kn\bigr)^{2}+\Pr[T_0\cap O\ne\emptyset]\le\frac{K^{4}(K-1)}{2n}+\frac{K^{2}}{n}\le\frac{K^{5}}{2n}+\frac{K^{2}}{n}$.
> Under $n\ge4K^{5}$ the first term is at most $\tfrac18$ and the second is at most
> $1/(4K^{3})\le\tfrac1{32}$, so the total is at most $\tfrac5{32}<\tfrac12$: some $K$-set $O$
> makes every canonical query balanced and misses $T_0$.

链里有两处可收的松弛，都是链自己写出来的：

1. 把 $\Pr[R\subseteq O]=\frac{K(K-1)}{n(n-1)}$ 放宽成 $(K/n)^{2}$（松弛量正文自己给了：
   $\frac{K(n-K)}{n^{2}(n-1)}$），再把 $K^{4}(K-1)$ 放宽成 $K^{5}$（松弛量 $K^{4}/(2n)$）。
2. 结论只需要"存在一个好的 $O$"，即失败概率 **< 1**；正文压到 **< 1/2**（实到 5/32）。

### 3.2 收紧后的门槛（精确算术）

保留第 1 处的精确形式：
$nK\binom K2\frac{K(K-1)}{n(n-1)}=\frac{K^{3}(K-1)^{2}}{2(n-1)}$（§5 第 1 条 [VERIFIED-SYMBOLIC]）。
记 $A=K^{3}(K-1)^{2}/2$、$B=K^{2}$，链给出

$$\Pr[\text{fail}]\ \le\ \frac{A}{n-1}+\frac{B}{n}.$$

要求 < 1 等价于 $n^{2}-(A+B+1)n+B>0$，较大根落在 $(A+B,\,A+B+1)$ 内（因 $0<B<A+B+1$），
所以**使链给出结论的最小整数 $n$ 恰为 $A+B+1=K^{3}(K-1)^{2}/2+K^{2}+1$**。
两端各用一行验证（§5 第 3 条 [VERIFIED-SYMBOLIC]）：

- $n=A+B+1$：$\frac{A}{A+B}+\frac{B}{A+B+1}=1-\frac{B}{(A+B)(A+B+1)}<1$；
- $n=A+B$：$\frac{A}{A+B-1}+\frac{B}{A+B}=1+\frac{A}{(A+B)(A+B-1)}>1$。

逐 $K$ 的精确值（$K=2..50$ 样本，`fractions.Fraction`，§5 第 3 条 [VERIFIED-EXHAUSTIVE]）：

| K | $4K^{5}$（定理） | $K^{3}(K-1)^{2}/2+K^{2}$（handoff 数字） | 链的最小 n（失败 < 1） | 链的最小 n（失败 < 1/2） |
|---|---|---|---|---|
| 2 | 128 | 8 | 9 | 17 |
| 3 | 972 | 63 | 64 | 127 |
| 4 | 4096 | 304 | 305 | 609 |
| 5 | 12500 | 1025 | 1026 | 2051 |
| 6 | 31104 | 2736 | 2737 | 5473 |
| 10 | 400000 | 40600 | 40601 | 81201 |
| 20 | 12800000 | 1444400 | 1444401 | 2888801 |
| 50 | 1250000000 | 150065000 | 150065001 | 300130001 |

作为对照，若保留正文写出的宽松式 $K^{5}/(2n)+K^{2}/n$ 而只把 1/2 换成 1，门槛是
$\lfloor K^{5}/2+K^{2}\rfloor+1$（$K=2$ 得 21，$K=3$ 得 131，$K=5$ 得 1588）。

### 3.3 结论

**支持，但要带两个限定，且 handoff 的数字要读成严格门槛而不是最小 n。**

- 计数链本身（不改任何构造、不改 transcript 归纳）确实能把 $n$ 的充分条件从 $4K^{5}$ 降到
  $K^{3}(K-1)^{2}/2+K^{2}$ 量级，前提是：(a) 不把 $\frac{K(K-1)}{n(n-1)}$ 放宽成 $(K/n)^{2}$，
  (b) 把"失败 < 1/2"换成推论实际需要的"失败 < 1"。
- 精确说法应写成 $n>K^{3}(K-1)^{2}/2+K^{2}$，即最小可取整数 $n=K^{3}(K-1)^{2}/2+K^{2}+1$。
  handoff 与 TASKS11 里的 $K^{3}(K-1)^{2}/2+K^{2}$ 是**严格门槛本身**，在该点链给出的失败上界
  恰好 ≥ 1，用不了。这一条与 `results/V11/oracle/linear_exact.md` §C5 的独立结论一致
  （本审计是另写脚本重算的，两处数字逐 K 相同）。
- 若坚持正文现在的"失败 < 1/2"读法，收紧后的门槛是 $K^{3}(K-1)^{2}+2K^{2}+1$（表最后一列），
  仍远小于 $4K^{5}$。
- 连带影响（不改文也要记录）：$4K^{5}$ 一旦改动，同段末句 "The only property of the budget that
  the computation uses is $Q\le n^{2}/(4K^{4})$"（第 1878 至 1881 行）要跟着换成对应的精确形式
  $Q\le\frac{2n(n-1)}{K^{2}(K-1)^{2}}\bigl(1-\frac{K^{2}}{n}\bigr)$ 一类；
  随机版的 $\varepsilon_n$ 里的 $K^{5}/(2n)$ 也可同步换成 $K^{3}(K-1)^{2}/(2(n-1))$。
- 状态：门槛算术 [VERIFIED-SYMBOLIC]（§5 第 1、2、3 条）；"该门槛足以支撑定理"这一条仍受制于
  整条链上游的 canonical transcript 归纳与 count-grid 提升，状态 [HAND-PROOF-UNREVIEWED]，
  本审计不升级。**按纪律本文件不修改 `appendix_proofs.tex`、`results.tex` 或台账**，
  上面的收紧只作记录，供人类决定是否改写。

---

## 4. TASKS11 的另一个条件问题

**"fixed random string" 量词是否在陈述里**：该问题点名的是 thm:ceiling（T8），答案在
`results/V11/audit/ceiling.md`。对本条目（thm:linear-exact）一并记录：陈述的随机段用的是
expectation 量词（"the expectation over the algorithm's randomness"，正文第 784 至 786 行），
**没有也不需要** "fixed random string"。定 seed 只出现在 app:greedybudget 的
`Randomized algorithms.` 段里，作为"先定 seed 得到 canonical transcript、再对 $O$ 平均、
再对 seed 平均"的证明装置（E 表第 27 行）。两个量词的顺序（实例可依赖算法、期望只对算法随机性）
在同段末句写明，与 thm:hardness 一致。

---

## 5. 本文件自身算术的核对

临时脚本（不入库，位于本次会话的 scratchpad）用 sympy 与 `fractions.Fraction` 做了 8 组精确核对，
residual 全为 0，无 FAILED：

1. 计数链三条恒等式 [VERIFIED-SYMBOLIC]：
   $nK\binom K2(K/n)^{2}=K^{4}(K-1)/(2n)$；$K^{5}/(2n)-nK\binom K2(K/n)^{2}=K^{4}/(2n)$；
   $nK\binom K2\frac{K(K-1)}{n(n-1)}=\frac{K^{3}(K-1)^{2}}{2(n-1)}$。
2. 预算形式 [VERIFIED-SYMBOLIC]：$Q\binom K2(K/n)^{2}\le1/8\iff Q\le n^{2}/(4K^{3}(K-1))$，
   正文放宽成 $Q\le n^{2}/(4K^{4})$；$Q=nK$ 时后者等价于 $n\ge4K^{5}$。
3. 门槛闭式 [VERIFIED-SYMBOLIC + VERIFIED-EXHAUSTIVE]：$1-(\frac{A}{A+B}+\frac{B}{A+B+1})=\frac{B}{(A+B)(A+B+1)}>0$ 与
   $\frac{A}{A+B-1}+\frac{B}{A+B}-1=\frac{A}{(A+B)(A+B-1)}>0$；并对 $K\in\{2,3,4,5,6,8,10,13,20,50\}$
   用精确有理二分核对最小 $n$ 恰为 $A+B+1$（失败 < 1）与 $2(A+B)+1$（失败 < 1/2）。
4. 族的电池 [VERIFIED-SYMBOLIC]：自写一份 $r_x,h_x,F,H,\widehat H$ 实现，
   $K=2..8$ 乘 11 个 $\eta$（含 $\eta=K$、$\eta=K+1$ 的 $j=0$ 域与整数 $\eta$ 的双支），逐点核对
   $H(x,0)=\widehat H_x$（$0\le x\le K$）、$H(x,1)=\widehat H_{x+1}$（$x+1\le K$）、
   $F(K,0)=V_j=\min_i V_i$、$F(0,0)=0$、$F(0,K)=1$、$H(0,0)=0$，无反例。
5. 泄漏数字 [VERIFIED-SYMBOLIC]：$K=3,\eta=3/2$ 处 $H(6,0)=61/48$、$H(5,1)=4/3$，
   与附录第 1806 至 1808 行与台账第 308 行相同。
6. $\eta=1$ 的退化 [VERIFIED-SYMBOLIC]：族在 $\eta=1$ 处 $j=K-1$ 且
   $F(K,0)=1-(1-1/K)^{K}=L_K(1)=\rho_K(1)$，$K=2..8$（支持 E 表第 2 行的空洞性判定）。
7. greedy 查询数 [VERIFIED-SYMBOLIC]：$\sum_{t=0}^{K-1}(n-t)=nK-K(K-1)/2\le nK$。
8. 三份陈述文本的全等比较：`paper/sections/results.tex`（去注释行后）与
   `results/V11/statements.md`、`results/V11/inputs/statement_linear_exact.md` 的 LaTeX 块
   逐字符相同（两项均 True）。

---

## 6. 读过的文件

- `paper/sections/results.tex`（第 740 至 830 行：引导段、thm:linear-exact、rem:greedybudget）
- `paper/sections/appendix_proofs.tex`（第 1695 至 2030 行：app:greedybudget 全节，
  加 app:pe 与 app:hardness-anysize 开头的 inherits 那句）
- `paper/sections/model.tex`（第 1 至 80 行：全局设定、def:eta、lem:scaling、predictive greedy）
- `THEOREM_LEDGER.md`（第 280 至 330 行：T10b 尾注与 T10c 卡全文；第 331 行起 T10d 的对照行）
- `results/V11/statements.md`（第 226 至 281 行）
- `results/V11/inputs/statement_linear_exact.md`
- `results/J6/linear_exact.md`（第 1 至 10、110 至 130、225 至 231 行）
- `results/L1_table.py`（section 1，计数链）
- `results/Q4_gpt_check.py`、`results/Q4_symbolic_ineq.py`、`results/Q4_indep_check.py`、
  `results/Q4_smallset_lp.py`（头部说明与检查项，未重跑：oracle 报告已原样复跑，见下）
- `results/V11/oracle/linear_exact.md`（对照用，§C4/C5 的门槛结论与本审计一致）
- `results/V11/audit/exact.md`（格式与 thm:exact 的交叉引用）
