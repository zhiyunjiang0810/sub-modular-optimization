# 量词审计（criteria A 与 E）：thm:linear-anysize / 台账 T10d（来源 J7，TASKS11 Q8，正文 Proposition）

本文件只做两件事：A 项把正文 environment 与台账卡的陈述逐量词比对；E 项建立量词审计表，
把陈述里的每个量词与形容词（含隐含项）落到路线甲证明材料的具体位置，落不上的记 GAP。
TASKS11 给本条目的两条专项问题（thm:ceiling 的 fixed random string、thm:linear-exact 的
n ≥ 4K⁵ 收紧）属于另外两个条目，本文件 §3 只作 N/A 说明并给出本条目的对应位置。

范围与纪律：不修改任何已有仓库文件，不运行 git。本文件自身的算术用 `fractions.Fraction`
精确复核（脚本在 scratchpad，未入库；表达式与结论见 §4），浮点只出现在打印里。
状态标签按 CLAUDE.md：[VERIFIED-SYMBOLIC] [VERIFIED-LP] [VERIFIED-EXHAUSTIVE]
[HAND-PROOF-UNREVIEWED] [CONJECTURE] [FAILED]。读过的文件见 §5。

---

## 1. Criterion A：正文陈述与台账陈述的逐量词比对

### 1.1 三份原文位置

- 正文：`paper/sections/results.tex` 第 884 至 905 行，environment 为 **`proposition`**，
  label `thm:linear-anysize`，标题 "Arbitrary query sizes at linear budget"。
  之前第 876 至 882 行是状态注释（Q4 把 T10c 闭合、本条是 any-size 档），
  之后第 906 至 931 行是状态与空洞性检验注释（K ≥ 3、arbitrary size、n → ∞、O(nK)、
  deterministic/randomized 五条，以及 W_K 与 rem:exact-gap 的 W_m 不可混同）。
- 矩阵输入：`results/V11/statements.md` 第 317 至 352 行（含元数据行"正文环境: `theorem`"）与
  `results/V11/inputs/statement_linear_anysize.md` 第 6 至 25 行。两者逐字符相同；
  与正文 environment 的差别只有环境名（`theorem` 对 `proposition`）与正文里的两行 LaTeX 注释
  （本次用 diff 逐行比对，正文块去掉注释行后与矩阵块只差首尾两行的环境名，§4 第 7 条）。
- 台账：`THEOREM_LEDGER.md` 第 331 至 367 行，卡 `## T10d thm:linear-anysize`。
  其"陈述"行是第 332 至 335 行；另有"修正截断规则"（336–341）、"构造"（342–347）、
  "状态"（348–353）、"模拟证据"（354–356）、"量词检验"（357–361）、"禁止声称"（362–365）、
  "open problem"（366–367）。A 项只比对"陈述"行，其余行在 E 表里作为落点引用。

### 1.2 逐项对照

| 量词 / 形容词 | 正文（results.tex 884-905） | 台账（T10d 陈述行 332-335） | 判定 |
|---|---|---|---|
| environment 类型 | `proposition` | 卡名与 statements.md 元数据写 `theorem` | **差异 D0** |
| $K\ge3$ | "Let $K\ge3$" | "K ≥ 3" | 一致 |
| $\eta>1$ | "$\eta>1$" | "η > 1" | 一致 |
| $\alpha_{\mathrm{lin}}$ 是 $n\to\infty$ 的极限 | "the limit as $n\to\infty$ of the optimal worst-case ratio" | "在 n → ∞ 时的最优最坏近似比" | 一致（两边都预设极限存在，见 E 表第 3 行） |
| deterministic 算法类 | "deterministic algorithms" | "确定性" | 一致 |
| 查询次数 $O(nK)$ | "make $O(nK)$ queries to $\tilde f$" | "O(nK) 次查询" | 一致 |
| 查询集合大小任意 | "\emph{of arbitrary size}" | "**任意大小**查询" | 一致 |
| 输出集合大小 ≤ K | "output a set of size at most $K$" | "输出 ≤ K 元素" | 一致 |
| 实例族：$f$ monotone submodular | "over instances with monotone submodular $f$" | 陈述行不写实例族 | **差异 D1** |
| 实例族：误差乘积 ≤ η | "error product at most $\eta$" | 陈述行不写（卡的构造行才有 band） | **差异 D1** |
| 随机版量词 | "(randomized algorithms measured in expectation over their own randomness)" | "（随机算法按期望）" | 一致（两边都不写 over what 的第二层，见 E 表第 13 行） |
| 结论式左端 $\rho_K(\eta)\le\alpha_{\mathrm{lin}}$ | 有 | 有 | 一致 |
| 下界出处与 greedy 属于该类 | environment 内不写（附录 2104-2105 行与注释 914 行才写） | "下界即 thm:exact（greedy 属于该类）" | **差异 D2** |
| 上界 $\min\{1/\eta,\ W_K(\eta)\}$ | 有 | 有 | 一致 |
| 上界第二级 $\min\{1/\eta,\ \rho_K+\frac{1}{K(e^{K-1}-K-1)}\}$ | 有 | 有 | 一致 |
| $W_K$ 的定位 | "the explicit constant of Appendix~\ref{app:hardness-anysize}"（给指针不给公式） | 陈述行只写 $W_K(\eta)$，公式在同卡第 339 行（$W_K=1-Q+(K-j)Qd$） | **差异 D3** |
| 解读句（greedy 在同阶复杂度内最优到指数小项） | "even with arbitrary-size queries, predictive greedy is optimal among algorithms of its own oracle complexity up to an additive term exponentially small in $K$" | 陈述行无（对应内容在 open problem 行与禁止声称行） | **差异 D4** |
| $\eta\ge K$ 的塌缩 | "For $\eta\ge K$ both ends equal $1/\eta$" | "η ≥ K 时两端塌到 1/η" | 一致 |
| adversarial ties、fixed K steps、$f(\emptyset)=0$、OPT > 0、$1\le K\le n$ | 均不出现 | 均不出现 | 一致（两边都继承 model.tex，见 E 表第 19 至 22 行） |
| 拆分 $(\eta_u,\eta_o)$ 的量词 | 不出现（只说 error product） | 不出现 | 一致（两边都缺，见 E 表第 12 行） |
| 显式 $n_0$ | 不出现 | 陈述行不出现（量词检验行第 359 行注明"有限 n 版需要显式 n₀ ~ K³(T+K)² 未陈述"） | 一致（作为陈述行；见 E 表第 21 行 GAP-2） |

### 1.3 A_diffs

**A_match = false**，共 5 条差异：

- **D0（environment 名）**：正文是 `\begin{proposition}`，台账卡标题与 `statements.md`
  第 319 行的元数据都写 `theorem`，`statements.md` 与 `inputs/` 的 LaTeX 块也写 `theorem`。
  正文正文里 J7 结果被降格为 Proposition（与 HANDOFF §4 "Prop (J7, thm:linear-anysize)" 一致），
  台账与矩阵输入未跟进。这是呈现层差异，但会让盲审路线二拿到的环境类型与正文不符。
- **D1（实例族形容词）**：正文在 environment 内写明 "over instances with monotone submodular
  $f$ and error product at most $\eta$"；台账陈述行只描述算法类，不描述实例族。
  实例族是 worst-case ratio 里 inf 的定义域，缺它时"最优最坏近似比"的对象不完整。
  台账的构造行（342–347）给了 band 与 $F$ 的性质，但那是构造侧不是陈述侧。
- **D2（下界出处与 greedy 的类归属）**：台账写"下界即 thm:exact（greedy 属于该类）"，
  正文 environment 内不写。正文把它放在附录第 2104 至 2105 行
  （"the lower bound being Theorem~\ref{thm:exact}"）与第 914 行的状态注释里。
  "greedy 属于该类"这一句是承重的：greedy 的预算 $Kn-K(K-1)/2=O(nK)$、
  查询大小 ≤ K ≤ 任意，所以它落在 any-size 类内，$\rho_K$ 才是该类的下界。
  正文两处都没有把这个归属写成句子（附录只写引用）。
- **D3（$W_K$ 的公式位置）**：正文只给 Appendix 指针，台账在同卡给显式公式
  $W_K=1-Q+(K-j)Qd$ 并给 gap 恒等式。方向相反的缺失，记一条。
- **D4（解读句）**：正文 environment 内带一句解读（greedy 在自身 oracle complexity 内最优
  到指数小项），台账陈述行没有。按空洞性检验，这句话的内容等价于
  $W_K-\rho_K<1/(K(e^{K-1}-K-1))$，不是新量词，但它把"最优"读成了带附加项的最优，
  若单独引用容易被读成 $\alpha_{\mathrm{lin}}=\rho_K$（台账禁止声称第 362 行明令禁止）。

---

## 2. Criterion E：量词审计表

路线甲材料：`paper/sections/appendix_proofs.tex` 的 `app:hardness-anysize`
（第 1985 至 2146 行，其中正文段 2012 至 2146，状态注释 1988 至 2010）、
被它引用的 `app:hardness`（第 1462 至 1700 行）与 `app:greedybudget`（第 1703 行起）、
`results/J7/linear_anysize.md`、四个 J7 脚本。模型层继承写 `model.tex`。

| 量词 / 形容词 | 路线甲的落点（文件 + 段落 / 引用句） | 状态 |
|---|---|---|
| 1. $K\ge3$ | `appendix_proofs.tex` 2014 "Fix $K\ge3$ and $\eta>1$"；消费点在"Value and the exponential gap"段 2103-2104 "for $K\ge3$, using $K-j\le\eta$..."（$e^{K-1}-K-1>0$ 需 $K\ge3$）与 `results/J7_symbolic.py` S1.5、S10 | OK |
| 2. $\eta>1$ | 同 2014 行；消费点是 $\nu=\eta/(\eta-1)$ 的定义（2015 行）与 S1 的 $\phi$ 凹性；$\eta=1$ 时 $\nu$ 无定义，故承重 | OK |
| 3. $n\to\infty$ 的**极限存在性** | 无。附录只证 limsup 侧（泄漏概率 $cK^{3}(t^{\ast}+K)^{2}/(2n)\to0$，2088-2091）与 liminf 侧（$\rho_K$，2104-2105），没有任何一处论证该序列收敛或对 $n$ 单调 | **GAP-1** |
| 4. "optimal worst-case ratio"（sup over 算法，inf over 实例）的 inf 定义域 | 部分：实例族在正文 environment 里写了（monotone submodular、error product ≤ η），附录只在 Legality 段给出构造侧的族成员资格（2078-2080 "$F(0,0)=H(0,0)=0$, $F(0,K)=1$ and $0\le F\le1$ ... so $O$ is optimal with $f(O)=1$"），没有一句把 sup-inf 的两侧实例族对齐 | 部分 |
| 5. deterministic | `app:hardness` 1606-1636 "The canonical transcript, and the deterministic statement."（"determinism makes the $i$th query equal to $S_i$"），由 2091-2092 "the canonical-transcript induction and the averaging are those of Appendix~\ref{app:hardness}" 继承 | OK（继承，[HAND-PROOF-UNREVIEWED]） |
| 6. $O(nK)$ 次查询（常数 $c$） | 2088-2091 "$cnK$ queries leak with total probability at most $cK^{3}(t^{\ast}+K)^{2}/(2n)\to0$"；超线性预算被 2121-2128 "Beyond the linear budget." 明确排除在定理外 | OK |
| 7. 查询 **of arbitrary size** | 2082-2086 "\paragraph{Arbitrary query sizes.}"：$H(x+1,0)=H(x,1)$ 对 every $x\ge0$，"the predictor depends only on $\lvert S\rvert$ on the whole region $\lvert S\cap O\rvert\le1$, at every size"；脚本侧 `results/J7_grid_check.py` D 段（"the ANY-SIZE key"）逐格精确核对 [VERIFIED-LP 精确有理] | OK |
| 8. 输出集合大小 ≤ $K$ | 部分：2095-2096 "Every $K$-set disjoint from $O$ has value $W_K(\eta)$" 只算 $\lvert T\rvert=K$；$\lvert T\rvert<K$ 只有更小（$F(x,0)=1-r_x$ 对 $x$ 非降）在 any-size 段没有一句写出来，$T\cap O=\emptyset$ 的那一项来自 `app:hardness` 1613 行的 $\Pr[T_0\cap O\ne\emptyset]\le\lvert T_0\rvert K/n$，靠 2091-2092 继承 | 部分 |
| 9. $f$ monotone | 2065-2074 Legality 段（"$g$ and $a$ are nonnegative and nonincreasing"，"These one-dimensional facts yield every monotonicity and diminishing-returns inequality of $F$ on the count grid"）；脚本 `results/J7_grid_check.py` B 段全格点精确核对 | OK（count grid 层 [VERIFIED-LP 精确有理]） |
| 10. $f$ submodular | 同上；集合函数层需 `lem:app-count`（`appendix_proofs.tex` 53 行），但 any-size 段**没有**显式援引该引理，只说 "on the count grid"；状态注释 2001-2003 把 "the lift from the count grid to set functions" 记作 [HAND-PROOF-UNREVIEWED] | 部分 |
| 11. error product ≤ $\eta$（Definition 1 的双侧 band） | 2074-2078 "the same four-edge-class table as in Appendix~\ref{app:greedybudget} yields $\Delta F\le\Delta H\le\eta\,\Delta F$ on every edge, with both split endpoints attained on positive-gain edges at $x=0$"；脚本 C 段逐边精确核对，两端点可达 | OK |
| 12. 拆分 $(\eta_u,\eta_o)$ 对乘积 $\eta$ | 部分：附录用 $H=\eta_u\tilde f$ 的缩放读法（2053 行 $\eta_u\tilde f=H(x,y)$）并在 2079-2080 说 "the smallest admissible error factors are exactly $(\eta_u,\eta_o)$"；任意指定拆分的实现靠 `app:hardness` 1560-1568 "A prescribed split of the error." 与 `model.tex` 44-54 的 `lem:scaling`，any-size 段没有重述，陈述侧也没有 split 量词 | 部分 |
| 13. randomized：expectation over the algorithm's own randomness；fixed random string | `app:hardness` 1638-1656 "\paragraph{Randomized algorithms, by averaging.} Fix the random seed $r$; then $\mathcal R_r$ is deterministic..."，"averaging over $r$, exchanging the two finite expectations and using $\min_O\le\mathbb E_O$"。**fixed random string 的量词在陈述里没有**（陈述只写 in expectation），且 any-size 版没有写出对应的 $\varepsilon_n$，靠 $n\to\infty$ 吸收 | 部分 |
| 14. 下界 $\rho_K(\eta)$（thm:exact） | 2104-2105 "the lower bound being Theorem~\ref{thm:exact}"；`results.tex` 191-207 的 thm:exact 给 $\rho_K=\min_j V_j$ 与 $\eta\ge K$ 时 $=1/\eta$ | OK（引用） |
| 15. 上界的 $1/\eta$ 分支 | 无。`app:hardness-anysize` 全段只证 $W_K$ 分支，没有一句处理 $\min$ 里的 $1/\eta$；它实际来自 `results.tex` 441-462 的 `thm:ceiling`（deterministic、$n\ge2K$）与 464-474 的随机段（$((1-K/n)/\eta+K/n)$，$n\to\infty$ 时趋 $1/\eta$），但本条目的路线甲材料里没有指针 | **GAP-3** |
| 16. 上界的 $W_K(\eta)$ 分支与其显式常数 | 2094-2096 "Value and the exponential gap." $W_K(\eta)=1-Q+(K-j)Qd$，配 2014-2055 的 $\Psi$ 规则、$m$ 的定位、$d$ 的两条恒等式、$j,Q,D,t^{\ast}$ 与两条序列；脚本 `results/J7_symbolic.py` S1-S9 [VERIFIED-SYMBOLIC]、`results/J7_grid_check.py` E 段 [VERIFIED-LP 精确有理] | OK |
| 17. 指数小项 $1/(K(e^{K-1}-K-1))$ | 2097-2104 的 display 与 "using $K-j\le\eta$, $Q\le1$, $m-\eta(K-1)<\eta$ and $\nu^{m}>e^{K-1}$"；`results/J7_symbolic.py` S10、`results/J7_bound18_check.py`（$e$ 用有理上界，判定精确，99 组） | OK |
| 18. "$\eta\ge K$ 时两端相等" | 部分：$\rho_K(\eta)=1/\eta$ 由 thm:exact（`results.tex` 199-201 "In particular $\rho_K(\eta)=1/\eta$ exactly when $\eta\ge K$"）；上端需要 $W_K\ge1/\eta$ 才能让 $\min$ 取到 $1/\eta$，这一条 any-size 段没有写（本审计在 140 组精确配置上核过，$W_K\ge1/\eta$ 恰在 $\eta\ge K$ 处成立，§4 第 3 条） | 部分 |
| 19. 归一化 $f(\emptyset)=0$、$\tilde f(\emptyset)=0$ | 2078-2079 "$F(0,0)=H(0,0)=0$"（$H=\eta_u\tilde f$ 故 $\tilde f(\emptyset)=0$）；模型层 `model.tex` 9-14 | OK |
| 20. OPT > 0 / $O$ 为最优集 | 2078-2080 "$F(0,K)=1$ and $0\le F\le1$ on the whole grid, so $O$ is optimal with $f(O)=1$"；`model.tex` 15-16 给 OPT = 0 时的平凡读法 | OK |
| 21. 构造需要的 ground set 规模（隐含 $n_0$） | 无显式落点。构造要占满 $x\le t^{\ast}$ 需 $n-K\ge t^{\ast}$；泄漏界 $cK^{3}(t^{\ast}+K)^{2}/(2n)<1$ 需 $n>cK^{3}(t^{\ast}+K)^{2}/2$（$K=3,\eta=3/2$ 为 $n>1093$，§4 第 5 条）。附录只在注释 2005-2008 记了 finite-n caveat（$n<K+t^{\ast}$ 时反向 greedy 比值恰为 1，`results/J7_grid_check.py` 的 sim 段），正文段与陈述都没有 $n_0$ | **GAP-2** |
| 22. tie-breaking（adversarial） | 只服务下界侧：`model.tex` 69-72 "with ties broken adversarially in all worst-case statements"；`results.tex` 192 thm:exact "under adversarial tie breaking"；脚本侧 `results/J7_grid_check.py` 的 `sim()`（fwd/rev 在并列最优上取 `min`，即对抗平局） | OK（继承） |
| 23. fixed $K$ steps（greedy 跑满 K 步） | `model.tex` 72-78 "The run always executes exactly $K$ steps"；只服务下界侧的 $\rho_K$ | OK（继承） |
| 24. $K\ge2$ 类的隐含需求 | $c_y=(K-y)/(K-1)$ 需 $K\ge2$（2048-2049），$\phi(0)=K-1>0$ 需 $K\ge2$（2022-2023，脚本 S1.4/S1.5）。本条陈述的 $K\ge3$ 严格更强，故隐含项被覆盖 | OK |
| 25. 均匀随机 $K$-集 $O$ 与 $\min_O\le\mathbb E_O$ | 2088 "For a uniformly random $K$-set $O$"；`app:hardness` 1591-1604 的 Counting 段与 1652-1656 的平均段 | OK（继承，[HAND-PROOF-UNREVIEWED]） |
| 26. 算法只查 $\tilde f$、可自适应 | `app:hardness` 1606-1636 的 canonical transcript 归纳（"if the first $i-1$ answers ... determinism makes the $i$th query equal to $S_i$"）覆盖自适应；模型层 `model.tex` 10-12 | OK（继承） |
| 27. 截断规则 $m$ 的良定义与定位 $\eta(K-1)<m<K\eta$ | 2018-2028；`results/J7_symbolic.py` S1（含 $\nu^{\eta}>e$ 的初等不等式，记为 ASSEMBLY 残留）；旧规则 $m=\lceil K\eta\rceil-1$ 的反例见 2109-2120 与 `results/J7_fragment_checks.py` Part 1 | OK（[VERIFIED-SYMBOLIC]，两条经典初等不等式残留） |
| 28. predictive greedy 属于 any-size 线性类 | 无独立句子。正文 environment 与附录都不写；台账陈述行写了（见 A 的 D2）。可由 `results.tex` 764 行（thm:linear-exact 里的 "predictive greedy, at $Kn-K(K-1)/2$ queries, belongs to $\mathcal A_{\mathrm{lin}}$"）与 `appendix_proofs.tex` 1871 行（$\sum_{t}(n-t)=nK-K(K-1)/2\le nK$，size $\le K$）推出，但 any-size 这一侧没有落点句 | **GAP-4**（轻，可由已有数字一句话补上） |
| 29. 解读句 "optimal up to an additive term exponentially small in $K$" | 等价于表第 17 行的 (18)；另有 2138-2142 的数值衰减行与 $L_K\le V_j\le W_K<U_K$ 链 | OK |
| 30. 与 T10c（$\lvert S\rvert\le K$）的分工 | 2012-2014 "Theorem~\ref{thm:hardness} restricts every query to at most $K$ elements, and Theorem~\ref{thm:linear-exact} inherits that restriction. Removing it costs an additive term exponentially small in $K$." | OK |

### 2.1 GAP 汇总

- **GAP-1（极限存在性）**：陈述把 $\alpha_{\mathrm{lin}}$ 定义成"$n\to\infty$ 的极限"，
  但路线甲只给了两侧的夹逼：上侧是 $n\to\infty$ 的渐近上界，下侧是与 $n$ 无关的 $\rho_K$。
  由于 $\rho_K<W_K$ 严格（§4 第 2 条，140 组配置全部严格），夹逼不蕴含收敛。
  保守读法：把 $\alpha_{\mathrm{lin}}$ 读成 $\limsup$（上界方向）与 $\liminf$（下界方向），
  或者补一句零填充单调性论证。不动正文，只记录；矩阵里本条目应注明"极限存在性未论证"。
- **GAP-2（显式 $n_0$）**：陈述与附录正文段都没有 $n_0$；构造需要 $n\ge K+t^{\ast}$，
  泄漏界还需 $n\gtrsim cK^{3}(t^{\ast}+K)^{2}/2$。台账量词检验行第 359 行已记
  "有限 n 版需要显式 n₀ ~ K³(T+K)² 未陈述"，且 $n<K+t^{\ast}$ 的反例（反向 greedy 比值恰 1）
  已在禁止声称里。这条不是错误，是缺一个显式门槛。
- **GAP-3（$\min$ 里的 $1/\eta$）**：路线甲材料里没有任何一处处理上界的 $1/\eta$ 分支。
  本审计核过：$W_K\ge1/\eta$ 恰在 $\eta\ge K$ 处发生（§4 第 3 条），
  也就是说 $1/\eta$ 分支**只在 $\eta\ge K$ 时承重**，而正是在那里它撑起了
  "both ends equal $1/\eta$" 这句话（没有它上端会是 $W_K>1/\eta$）。
  它在论文别处是有出处的（`thm:ceiling`，deterministic 且 $n\ge2K$；随机版是
  `results.tex` 464-474 的 $((1-K/n)/\eta+K/n)$，$n\to\infty$ 趋 $1/\eta$），
  但 `app:hardness-anysize` 没有指针，且随机版的 $1/\eta$ 只有极限意义。
- **GAP-4（greedy 的类归属）**：下界 $\rho_K$ 要成立必须先说 predictive greedy 落在
  any-size、$O(nK)$、输出 ≤ K 的类里。台账陈述行有这句，正文与附录都没有。
- 次要记录（不计入 GAP）：表第 8 行（$\lvert T\rvert<K$ 只会更差）、
  第 10 行（count grid 到集合函数的提升，[HAND-PROOF-UNREVIEWED]）、
  第 12 行（split 的任意性靠 `lem:scaling` 与 `app:hardness` 继承）、
  第 13 行（randomized 的 fixed seed 量词不在陈述里，any-size 版没有写出 $\varepsilon_n$）、
  第 18 行（$\eta\ge K$ 时上端取 $1/\eta$ 需要 $W_K\ge1/\eta$，附录未写）。
  这五条都是"有落点但落点在别处或被略写"，不是无落点。

### 2.2 与路线二 oracle 的关系

`results/V11/oracle/linear_anysize.md` 已把四个 J7 脚本复跑（148 项 + 99 组 + 99 组 + 片段检查，
0 FAILED）并自写了 count-grid 电池与算法端模拟。本审计不重复那些判定，只用它们作为 E 表的
落点证据等级。两份文件的未覆盖清单一致：提升、泄漏界、transcript 归纳、平均、下界引用仍是
[HAND-PROOF-UNREVIEWED，来源 J7]。本审计新增的是 GAP-1、GAP-3、GAP-4 三条量词层面的缺口，
它们不在 oracle 的"不支持的声称"清单里。

---

## 3. TASKS11 的两条条目专属问题

- **thm:ceiling 的 "fixed random string" 是否在陈述里**：不属本条目。就本条目而言，
  陈述只写 "randomized algorithms measured in expectation over their own randomness"，
  没有 fixed random string 这一层；证明侧的 "Fix the random seed $r$" 在
  `app:hardness` 1639 行（见 E 表第 13 行）。thm:ceiling 的对应审计见
  `results/V11/audit/ceiling.md`。
- **thm:linear-exact 的 $n\ge4K^{5}$ 能否收紧到约 $K^{3}(K-1)^{2}/2+K^{2}$**：不属本条目
  （那条计数链在 `app:greedybudget`），见 `results/V11/audit/linear_exact.md` §3。
  本条目的附录没有对应的显式门槛（这正是 GAP-2）。

---

## 4. 本次自查的精确算术

脚本在 scratchpad（`q8_audit_checks.py`，未入库），全部判定用 `fractions.Fraction`；
$e$ 用 $\sum_{k\le40}1/k!$ 及其加 $1/(40!\cdot40)$ 的有理上下界。扫描域：
$K\in\{3,\dots,12\}$，$\eta\in\{21/20,11/10,5/4,3/2,2,5/2,3,7/2,4,9/2,5,6,8,12\}$ 中大于 1 者，
共 140 组配置，violations = 0。

1. running example $K=3,\eta=3/2$：$j=2$、$m=4$、$t^{\ast}=6$、$q=3/4$、$\nu=3$、$Q=9/16$、
   $B_m=116$、$d=13/58$、$D=117/928$，$W_3=523/928=9/16+1/928$，$\rho_3=9/16$，
   $1/\eta=2/3$，$W_3<2/3$。与附录 2105-2107 行、`results/J7/linear_anysize.md` 第 102 行逐位相同
   [VERIFIED-EXHAUSTIVE]。
2. 140 组配置上：$j$ 是 $V_j$ 的 argmin、$W_K-\rho_K>0$ 严格、$W_K-\rho_K<1/(K(e^{K-1}-K-1))$
   （$e$ 取有理下界，判定保守）、$\eta(K-1)<m<K\eta$、$1/(m+1)\le d\le1/m$ 全部成立
   [VERIFIED-EXHAUSTIVE]。
3. $\min\{1/\eta,W_K\}$ 的活跃分支：140 组里 29 组满足 $W_K\ge1/\eta$，且这 29 组**恰好**是
   $\eta\ge K$ 的那些；其余 111 组 $W_K<1/\eta$，$\min$ 取 $W_K$。在 $\eta\ge K$ 的组上
   $\rho_K=1/\eta$ 且 $\min\{1/\eta,W_K\}=1/\eta$，即陈述末句的塌缩成立 [VERIFIED-EXHAUSTIVE]。
4. $K=2$ 的空洞性：$e-3<0$（有理上下界同号），故指数形式在 $K=2$ 无内容；
   但 $W_2$ 本身存在（$K=2,\eta=3/2$：$W_2=61/100$，$\rho_2=3/5$，gap $=1/100$），
   与台账量词检验行第 357 行一致 [VERIFIED-EXHAUSTIVE]。
5. ground set 门槛样本：$K+t^{\ast}$ 在 $(K,\eta)=(3,3/2),(3,2),(3,3),(4,3/2),(5,3)$ 处为
   $9,10,12,12,22$；泄漏界 $cK^{3}(t^{\ast}+K)^{2}/(2n)<1$ 在 $K=3,\eta=3/2,c=1$ 处需 $n>1093$
   [VERIFIED-EXHAUSTIVE]。这两个数都不在陈述里，对应 GAP-2。
6. $\rho_K$ 用 thm:exact 的闭式 $\rho_K=\min_{0\le j\le K-1}V_j$，$V_j=1-q^{j}(1-\frac{K-j}{K\eta})$
   自写实现，与 `results/J7_grid_check.py` 的 `rho_exact` 独立同值（同一闭式，两处代码不共享）。
7. 文本比对：`results/V11/statements.md` 第 332 至 351 行与
   `results/V11/inputs/statement_linear_anysize.md` 第 6 至 25 行逐行相同（diff 空）；
   与 `paper/sections/results.tex` 第 884 至 905 行的差别只有首尾环境名与两行 LaTeX 注释。

---

## 5. 读过的文件（路线甲与比对材料）

- `paper/sections/results.tex`（884-931 为本条目；另读 191-207 thm:exact、441-474 thm:ceiling
  与其随机段、756-789 thm:linear-exact、876-882 引导注释）
- `paper/sections/appendix_proofs.tex`（1985-2146 app:hardness-anysize；1462-1700 app:hardness
  含 Counting、canonical transcript、randomized averaging、prescribed split；1703 起 app:greedybudget
  的四边表引用；53-64 lem:app-count）
- `paper/sections/model.tex`（9-16 ground set 与归一化、23-32 def:eta、44-54 lem:scaling、
  69-78 predictive greedy 的 adversarial ties 与 fixed K steps）
- `THEOREM_LEDGER.md`（331-367 卡 T10d；另读 369-448 T11、449-459 T12 的收编行）
- `results/V11/statements.md`（317-352）、`results/V11/inputs/statement_linear_anysize.md`（1-26）
- `results/J7/linear_anysize.md`（全文 122 行）
- `results/J7_symbolic.py`（S1-S12 段标题与 S1、S2 的判定形式）、`results/J7_grid_check.py`
  （文件头的 A-G 检查清单、`run_config`、`sim`）、`results/J7_fragment_checks.py`（三个 Part）、
  `results/J7_bound18_check.py`（`gap_exact`）
- `results/V11/oracle/linear_anysize.md`（只作证据等级对照）、
  `results/V11/audit/linear_exact.md`（只作格式与 §3 的指向）
- `CLAUDE.md`、`HANDOFF_2026-09-18.md`（§4 的 J7 行与 must-not-claim）
