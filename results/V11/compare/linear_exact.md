# ROUTE-COMPARISON：thm:linear-exact（T10c / J6，Theorem 2）

判定角色：TASKS11 Q6 criterion B（route comparison judge）。本文件只做比对与复核，不修改任何既有文件，未运行 git。

- 路线一（repository proof）：`paper/sections/appendix_proofs.tex` 的 `\subsection{... }\label{app:greedybudget}`（第 1703 行起）、
  `results/J6/linear_exact.md`；脚本 `results/Q4_gpt_check.py`、`results/Q4_indep_check.py`、`results/Q4_symbolic_ineq.py`、
  `results/Q4_smallset_lp.py`、`results/L1_table.py`（计数链）；台账卡 `THEOREM_LEDGER.md` 的 `## T10c`。
- 路线二（blind derivation）：`results/V11/route2/linear_exact.md` 及其脚本 `q6_route2_checks.py`、`q6_route2_lp_scipy.py`、`q6_route2_lp_hard.py`。
- 本判定新写的复核脚本：`results/V11/compare/judge_linear_exact_checks.py`（一键复跑，含下文全部数值判定；判定用 `fractions.Fraction`/sympy，float 只出现在 LP 求解与打印）。

任务模板里关于 thm:ceiling（route 甲/乙）、prop:valueacc（convention B）与 J8（route one 缺失）的附加条款，对象不是本陈述，本文件不适用；保守起见在此记录一句，不做无对象的比较。

---

## 1. 步骤对应表

下表左栏是路线二的编号步骤（照其第 2 至第 6 节），右栏给出路线一的对应位置；"different route" 一栏写明理由。

| # | 路线二步骤 | 路线一对应 | 关系与备注 |
|---|---|---|---|
| S0 | 第 1 节：13 条量词逐条展开 | `statement_linear_exact.md` 原文 + T10c 卡的"量词检验"行 | 对应。定理级量词逐条吻合，差异见第 3 节 |
| A | 引理 A：count grid → set function（(A1) 单调 + (A2) 网格 DR） | app:greedybudget "Legality" 段的 "chaining single-element additions transfers monotonicity and diminishing returns to the set function" | 对应。路线一把它写成一句话，路线二写成独立引理并给了推导。两侧都是 [HAND-PROOF-UNREVIEWED]（台账明确此标签不在本节升级） |
| B | 引理 B：band 逐点形式，(B1) 同值两元素比 ≤ η，(B2) selection error ≤ η，(B3) $\tilde f$ 的一致性耦合 | 无直接对应（路线一用四类边表直接核对 band） | different route：路线二把 band 的后果抽象成三条引理，路线一把 band 变成 $\Delta F\le\Delta H\le\eta\Delta F$ 的四行表并逐类验证。两者不冲突，(B3) 是路线二特有的工具 |
| R1 | 反面结果：count-only predictor 的天花板 $1/\eta$ | 无本节对应（近亲是 thm:ceiling 的 $1/\eta$ 与 `results/Q3_failure_point.md`） | different route。结论我方独立复核为真：count grid LP 在 $K=2,3,4$、$\eta=3/2$、$X\le14$ 上恒为 $0.666666667=1/\eta$ [VERIFIED-LP，judge 脚本 §5 mode=count] |
| τ | 由 R1 定出盲度 $\tau=2$（$\tau=3$ 回到 $2/3$） | 无对应 | different route。我方复核：$K=2,3$ 的 $\tau=3$ 为 $2/3$，$K=4$ 为 $0.633634868$（路线二未测 $K=4$）[VERIFIED-LP] |
| 3.3 | 主构造 H：隐藏 $\pi$，$f_\pi=\Phi(|S\cap\pi|,|S\setminus\pi|)$，$\tilde f_\pi$ 满足 1-blind 条件 $\widetilde\Phi(0,s)=\widetilde\Phi(1,s-1)$ **对所有 $s$** | app:greedybudget "The double-residual family" + "Small-set indistinguishability"：显式 $r_x,h_x,F,H$，且 blindness 只要求 $|S|\le K$ 且 $|S\cap O|\le1$ | **实质分歧**。路线一显式声明大集合上 predictor 泄漏（$K=3,\eta=3/2$：$H(6,0)=61/48\ne4/3=H(5,1)$），并说明这一泄漏正是绕开 N4/F3 超额的机制；路线二把盲度要求推到所有 size。见第 4 节 D1 |
| 4.1 | $V_j$ 的组合含义（$j$ 步落在 $O^\ast$ 内给收缩 $q$，$K-j$ 步平坦） | "The value" 段：$F(K,0)=1-Q+(K-j)\delta=V_j$ 与相邻支恒等式 $V_{j+1}-V_j=q^j(\eta-K+j)/(K\eta k_1)$ | 对应但方向相反：路线一在显式族上算出 $V_j$ 并给出最小化支 $j^\ast=\max\{0,K-\lfloor\eta\rfloor\}$；路线二只做组合解释，未定出 $j^\ast$，$\rho_K=\min_jV_j$ 取自 notation.md。两端点恒等式双方一致 [VERIFIED-SYMBOLIC] |
| 4.2 | $L_K$ 不可达的机制（$K=2$ 的有理矛盾 $1/6<2/9$） | 无对应（路线一不需要，$\rho_K$ 的紧性由 thm:exact 给出） | different route。算术我方逐步复算无误 [VERIFIED-EXHAUSTIVE，judge 脚本 §4]，论证本身 [HAND-PROOF-UNREVIEWED] |
| S1 | 基实例 $(\Phi,\widetilde\Phi)$ 存在性 | 显式闭式 $r_x,h_x,F,H$ 对一般 $(K,\eta,\eta_u,\eta_o)$ 给出，且合法性有 13 条恒等式 + 34 条分支不等式 + 111/159 组精确电池 [VERIFIED-SYMBOLIC/LP] | **路线二缺口**：路线二只有 $K\in\{2,3\},\eta=3/2$ 的 LP（自标 GAP-3），并且在其自身写法下 $K=2$ 不可行，见第 4 节 D1/D2。我方独立复核路线一族在 $K=2,3,4,5,6$、三种 split、$x\le14$ 上 monotone/submodular/band/normalization 全过且 $F(K,0)=\rho_K$ [VERIFIED-EXHAUSTIVE] |
| S2 | 族的定义与合法性 | 同上（同一段） | 对应 |
| S3 | canonical transcript induction（deterministic + 1-blind ⟹ transcript 与 $\pi$ 无关） | "Transcript induction and the two directions" 段（引用 app:hardness 的归纳） | 对应，写法几乎相同。两侧都 [HAND-PROOF-UNREVIEWED] |
| S4 | union bound：$\Pr[\mathrm{Vis}]\le nK\binom K2\frac{K(K-1)}{n(n-1)}=\frac{K^3(K-1)^2}{2(n-1)}\le\frac{K^5}{2n}$，$\Pr[\mathrm{Hit}]\le K^2/n$，和 $\le5/32$ | "Counting at the budget" 段：$nK\binom K2(K/n)^2=\frac{K^4(K-1)}{2n}\le\frac{K^5}{2n}$，$\Pr[T_0\cap O\ne\emptyset]\le K^2/n$，和 $\le5/32$ | 对应，中间量不同、终点常数相同。两条链的代数我方符号复核为恒等 [VERIFIED-SYMBOLIC]；路线二的中间界更紧（比值 $(K-1)n/(K(n-1))<1$） |
| S5 | 确定性结论：存在 $\pi^\ast$ 既不可见又与 $T$ 不交，$f(T)/f(O^\ast)=\Phi(0,|T|)/\Phi(K,0)\le\rho_K$ | 同段：固定坏事件之外的 $O$，输出为 $T_0$ 且与 $O$ 不交，$f(T_0)\le F(K,0)=\rho_K$ | 对应。路线一有显式 $\Phi$ 支撑，路线二的 $\Phi$ 悬空（S1 缺口） |
| S6 | 校准到"恰好 $(\eta_u,\eta_o)$"（只有思路） | "Legality" 段末：两个 split 端点在 $x=0$ 的正增益边上达到（第一条 $O$-edge 比值 $1/\eta_u$，第二条 $\eta_o$），故最小可容许因子恰为 $(\eta_u,\eta_o)$ | **路线二缺口**（其 GAP-4）。路线一此步是完成的，并在 Q4 电池里对两个极端 split 逐点核过 |
| S7 | 匹配：与外部 thm:exact 合并得 sup-inf $=\rho_K$ | 同段末尾：predictive greedy 用 $nK-K(K-1)/2$ 次 size $\le K$ 查询，由 thm:exact 给反向不等式 | 对应，双方都把 thm:exact 当外部输入 |
| S8 | randomized averaging：坏事件按 $f/f(O^\ast)\le1$ 处理，好事件用轨道平均 avg-T，需 avg-T $\le\rho_K$ | "Randomized algorithms" 段：成功事件上 $f(T_0)\le\rho_K+|T_0\cap O|/K$（$O$ 的单元素值 $1/K$ + submodularity），失败事件 $f\le1$，对 $O$ 平均得 $K/n$ | **different route 且路线二更弱**。路线一的族里任何与 $O$ 不交的 $K$-set 值都恰为 $F(K,0)=\rho_K$，所以 avg-T 自动等于 $\rho_K$，不需要额外 LP；路线二因为族不同，卡在 avg-T 上（其 GAP-2） |
| 6.1 | $K=3,\eta=3/2$ 走查（$k_1=4$、$q=3/4$、$V=(2/3,7/12,9/16,37/64)$、$n_0=972$、greedy 2913 次、$\varepsilon_{972}=29/216$） | 台账 T10c 与 app:greedybudget 的同一组数字 | 对应，我方逐项精确复核一致 [VERIFIED-EXHAUSTIVE] |
| 6.2 | $K=2$ 走查，把 "ProbeLottery" 读成本定理的随机化条款 | 路线一无此条；ProbeLottery 是 J8（`results/V11/inputs/statement_probelottery.md`、HANDOFF §4）里的另一个命题：$K=2,\eta=3/2$ 的随机算法用 $\le9n$ 次、$|S|\le5$ 的查询在每个实例上拿到 $\ge3/5+1/400000$ | **读法错误（非本定理的错误）**。路线二盲证条件下只读四个 input 文件，看不到 J8，保守读法可以理解；但结论"本节对任意同预算随机算法成立"与 J8 的实际内容不是一回事（J8 的算法查询 size 为 5 > K，不属于 $\mathcal A_{\mathrm{lin}}$） |
| 空洞性检验 | 七个限定词逐个去除检验 | T10c 卡的"量词检验"行（deterministic / $\le nK$ / $|S|\le K$ / $n\ge4K^5$ / 输出 $\le K$ / "恰为 $(\eta_u,\eta_o)$"） | 对应。路线二额外给了"$n>K^2+K^5/2$ 即可"的余量说明（正确），路线一给的是等价形式"预算只用到 $Q\le n^2/(4K^4)$" |

### 路线一有而路线二没有覆盖的步骤

1. 一般 $(K,\eta,\eta_u,\eta_o)$ 的显式闭式族（双残差截断 $r_x,h_x$ 与截断门限 $\alpha=j+(K-1)\eta$、$\beta=j+K\eta$）。路线二完全没有（其 GAP-3）。
2. 合法性的三组残差事实 (i)(ii)(iii)（$0\le s_x\le p_x$ 且不增、$r_x-h_x\ge h_x/(K-1)$、无截断窗口 $(K-j)\delta\le Q/K$），以及四类边的比值表。路线二无对应。
3. 最小化支 $j^\ast=\max\{0,K-\lfloor\eta\rfloor\}$ 与整数 $\eta$ 处的双支并列。路线二只承接 $\rho_K=\min_jV_j$ 的公式。
4. 刚性轨迹（prop:rigidity）：每个状态 $(t,0)$ 上所有剩余元素预测增益并列于 $q^{\min(t,j)}/(K\eta_u)$，adversarial ties 使 greedy 走满 $K$ 步留在 $B$ 内。路线二在 hardness 侧不需要，但其 4.1 的 tight profile 隐含用到同一形态。
5. "为什么不与 N4/F3 超额矛盾"一段（大集合上的泄漏是刻意保留的）。路线二不但没有，而且反向要求了全 size 盲（分歧 D1）。
6. 随机版里 $f(T_0)\le\rho_K+|T_0\cap O|/K$ 的细化，以及 $\varepsilon_n$ 从 $K/n$ 保守取到 $K^2/n$ 的说明。
7. 预算的唯一用处 $Q\le n^2/(4K^4)$，以及与 thm:hardness 的 $\tau=\lceil c\rceil+1\ge3$ 的对照。
8. 旧天花板改进量 $U_K-\rho_K$ 的 $1/K^2$ 展开（在定理之外，附带）。

---

## 2. 我方独立复核（全部可复跑：`results/V11/compare/judge_linear_exact_checks.py`）

1. $V_j$、$L_K$、$U_K$ 的精确有理表；$V_0=1/\eta$、$V_K=U_K$、相邻支恒等式 $V_{j+1}-V_j=q^j(\eta-K+j)/(K\eta k_1)$ 全部为 sympy 恒等 [VERIFIED-SYMBOLIC]。
2. $j$ 的取值范围：在 $2\le K\le13$ 与 14 个 $\eta$ 的 168 个格点上，$\min_{0\le j\le K-1}V_j=\min_{0\le j\le K}V_j$ 且都在 $j^\ast=\max\{0,K-\lfloor\eta\rfloor\}$ 取到 [VERIFIED-EXHAUSTIVE]。故路线二的 GAP-7（$j$ 范围读法）无实际后果。
3. 路线一显式族：$K\in\{2,3,4,5,6\}$、$\eta\in\{3/2,2,5/2,7/4\}$、三种 split、$x\le14$ 的全格点上 monotone、grid DR、band（精确有理不等式）、$F(0,0)=\tilde f(\emptyset)=0$、$F(0,K)=1$、$\max_{a+b=K}F=1$ 全部成立，且 $F(K,0)=\rho_K$ 逐一相等 [VERIFIED-EXHAUSTIVE]。同一复核确认 blindness 在 $|S|\le K$ 成立、在更大集合上按路线一所说泄漏（$K=3,\eta=3/2$ 首个泄漏点 $(6,0)$ 对 $(5,1)$：$61/48$ 对 $4/3$，与附录里的数字逐字一致）。
4. 两条 union bound 链的代数、以及 $\varepsilon_{972}=29/216$、$\varepsilon_{128}=5/32$ 精确复算一致 [VERIFIED-SYMBOLIC + 精确有理]。
5. 路线二 4.2 的 $K=2$ 矛盾：$g_0=1/3$、$d_o(\emptyset)=1/2$、$g_1=2/9$、$d_o(\{e_0\})=1/3$、$f(\{e_0,o_1\})=2/3$、$f(\{o_1\})=1/2$、$d_{e_0}(\{o_1\})=1/6<2/9$ 逐步精确复算无误 [VERIFIED-EXHAUSTIVE]；论证的逻辑本身仍是 [HAND-PROOF-UNREVIEWED]。
6. 决定性对照 LP（count grid 上 min $F(K,0)$，$\eta=3/2$，$X$ 为 $|S\setminus O|$ 的上限）：

| $K$ | $\rho_K$ | count-only（$\tau=1$） | $\tau=3$ | 路线二的 $\tau=2$ 全 size 盲 | 路线一的"只在 $|S|\le K$ 盲" |
|---|---|---|---|---|---|
| 2 | $3/5=0.6$ | 0.666666667 | 0.666666667 | **0.610000000**（$X=4,6,8,14$ 全同） | **0.600000000** |
| 3 | $9/16=0.5625$ | 0.666666667 | 0.666666667 | 0.562500000（$X=4$）→ **0.563577586**（$X\ge6$） | **0.562500000** |
| 4 | $1447/2662\approx0.543576$ | 0.666666667 | 0.633634868 | 0.543576258（$X\le6$）→ **0.543703751**（$X\ge8$） | **0.543576258** |

[VERIFIED-LP，judge 脚本 §5；HiGHS 浮点解，值都是与已知有理数逐位吻合的短小数：$0.563577586=523/928=W_3(3/2)$，与台账 T10d 的 $W_K$ 一致]

---

## 3. 结论与量词是否一致

**结论**：一致。两条路线给出同一个值 $\rho_K(\eta)$、同一个 sup-inf 等式、同一个 $\varepsilon_n=K^2/n+K^5/(2n)$、同一个门限 $n\ge4K^5$，且都把 thm:exact 当外部输入。

**量词**：定理陈述一级的量词逐条吻合（$K\ge2$；$\eta>1$；每一个 $n\ge4K^5$ 而非充分大 $n$；deterministic；$\le nK$ 次查询；每次查询 size $\le K$；输出 size $\le K$；greedy 的成员性；对每个 $A$ 与每个指定 split；最小可容许因子"恰好"$(\eta_u,\eta_o)$；随机化条款的期望只对算法随机性取；无 $n$ 或 $K$ 的渐近）。但两侧的量词清单不是逐字相同，差异如下（故 `quantifier_match = false`）：

- Q-1：$\rho_K$ 的定义域。路线一/台账写 $\rho_K=\min_{0\le j\le K-1}V_j$，路线二读成 $\min_{0\le j\le K}V_j$。两者恒等（第 2 节第 2 条，168 个格点 [VERIFIED-EXHAUSTIVE]；结构理由：$V_K-V_{K-1}=q^{K-1}(\eta-1)/(K\eta k_1)>0$），无后果。
- Q-2：路线一有一个族层面的量词"$F(K,0)=\rho_K$ 对每个 $n\ge2K$"（同一张表被任意 $n\ge2K$ 限制），路线二没有这条，它的族只在 $|N|=m\le7$ 的 LP 上存在。
- Q-3：路线一的小集合不可区分性带 size 限定（$|S|\le K$ 且 $|S\cap O|\le1$），路线二的 1-blind 条件 $(\ast)$ 写成"对所有 $s$"，没有 size 限定。这是实质分歧（D1）。
- Q-4：路线二显式写入 assumptions.md 的两条约定（adversarial tie-breaking、predictive greedy 恒执行 $K$ 步）与 $f(O^\ast)=0$ 时比值命题平凡成立；路线一只在 greedy 侧用到 adversarial ties，不写后一条约定。
- Q-5：随机化条款的余项。路线一装配算出 $K/n+K^5/(2n)$，陈述里保守写成 $K^2/n+K^5/(2n)$；路线二直接按 $K^2/n+K^5/(2n)$ 走（坏事件按 1 计），没有 $|T_0\cap O|/K$ 这一细化。终点数值相同。

---

## 4. 分歧清单（divergences）

**D1（实质，路线二的一条 [VERIFIED-LP] 标签不成立）**：路线二 3.2/3.3 要求 $\tilde f_\pi$ 在**所有** size 的"至多含 1 个 $\pi$-元素"集合上盲，并以 $m=7$ 的 LP 标记 R2 为 [VERIFIED-LP]"1-blind 族达到 $\rho_K$"。在 count grid 上把 $|S\setminus O|$ 的上限 $X$ 放大后，这条要求把最优值顶到 $\rho_K$ 以上：$K=3$ 在 $X\ge6$ 处为 $523/928=W_3(3/2)>9/16$，$K=4$ 在 $X\ge8$ 处为 $0.543703751>1447/2662$，$K=2$ 在任何 $X$ 都是 $0.61>3/5$。路线二的 $m=7$ 只能表达 $X=m-K\le4$，恰好落在看不见该超额的区间里，所以它的 LP 证据不支持它的族。路线一在同一位置反向操作（明确只在 $|S|\le K$ 上要求不可区分，并说明大集合泄漏是必需的），我方对照 LP 在 $K=2,3,4$ 上给出恰好 $\rho_K$ [VERIFIED-LP]。结论：路线一正确，路线二的 R2 是 overclaim，其 S1 基实例在自身写法下对 $K\ge2$ 一般不可行。

**D2（路线二自报缺口的范围被低估）**：路线二把 $K=2$ 的失败只记在随机化条款（GAP-2，avg-T $=0.61$），并写"确定性条款不受影响（per-T $=0.6$）"。但它的 per-T $=0.6$ 来自 $f$ 自由（不是 count grid）的 LP，而 S5 用的是 $f_\pi(T)=\Phi(0,|T|)$ 这一 count-grid 形式。把 $f$ 也限制成 count grid 后，$K=2$ 的 per-T 同样是 $0.610000000$（judge 脚本用路线二自己的 `lp(..., fgrid=True, objective="per")` 复跑，$m=6,7$ 皆然）[VERIFIED-LP]。所以在路线二自己的构造形状下，$K=2$ 的**确定性**条款也没有被建立，GAP-2 的措辞低估了缺口。

**D3（ProbeLottery 的读法）**：路线二把 6.2 标题里的 ProbeLottery 读成本定理的随机化条款。仓库里 ProbeLottery 是 J8 的独立命题（$K=2,\eta=3/2$，随机算法，$\le9n$ 次、$|S|\le5$ 的查询，每个实例 $\ge3/5+1/400000$），它的查询 size 超过 $K$，不在 $\mathcal A_{\mathrm{lin}}$ 内，用途是证明 thm:linear-exact 的 $|S|\le K$ 限制必要。盲证条件下这个读法可以理解，但不能当成对 J8 的覆盖。附带一句：J8 的存在与 D1 的现象同源（放开查询 size 就能打破全 size 盲），两者互相印证。

**D4（计数链的中间量）**：路线二用精确超几何 $\frac{K(K-1)}{n(n-1)}$，路线一用上界 $(K/n)^2$；中间界分别是 $\frac{K^3(K-1)^2}{2(n-1)}$ 与 $\frac{K^4(K-1)}{2n}$，前者更紧，终点同为 $K^5/(2n)$。不是冲突，是写法差异。

**D5（$L_K$ 与 $j^\ast$）**：路线二额外给了 $L_K$ 不可达的机制（4.2）与 $K=2$ 的有理矛盾，路线一没有这一段；路线一额外给了最小化支 $j^\ast$ 与整数 $\eta$ 的双支并列，路线二没有。两者都不与对方冲突。

**路线一是否有被路线二反驳的步骤**：没有。路线二唯一与路线一正面冲突的断言是 R2/S1 的全 size 盲族可达 $\rho_K$，我方的对照 LP 判定路线一正确、路线二错误（D1）。路线一的三处 [HAND-PROOF-UNREVIEWED] 装配（count grid → 集合函数、transcript 归纳、两次平均）在路线二里得到**同构的独立重写**（引理 A、S3、S8），这一点是路线二的正面价值：两次独立写出的归纳与计数在结构和常数上吻合。

---

## 5. 路线二的缺口清单（route-two gaps）

自报的：

- GAP-1：R1（count-only 天花板 $1/\eta$）的手证缺"两条链增益比较"一步，自标 [FAILED]。结论本身我方在 $K=2,3,4$、$X\le14$ 上复核为真 [VERIFIED-LP]，一般证明仍缺。
- GAP-2：$K=2,\eta=3/2$ 的轨道平均 avg-T $=0.61>\rho_2=3/5$，自标 [FAILED]（随机化条款，$n>2000$）。实际范围更大，见 D2。
- GAP-3：一般 $(K,\eta)$ 的基实例 $(\Phi,\widetilde\Phi)$ 只有 $K\in\{2,3\},\eta=3/2$ 的 LP，自标 [CONJECTURE]。对照路线一：一般闭式存在且合法性 [VERIFIED-SYMBOLIC/LP]。
- GAP-4：S6 的"最小可容许因子恰好 $(\eta_u,\eta_o)$"未逐点核验，自标 [HAND-PROOF-UNREVIEWED]。路线一此步完成。
- GAP-5：band 在 $|S|>K$ 的显式延拓未写，自标 [CONJECTURE]。路线一的闭式对所有 size 给出并有截断门限。
- GAP-6：thm:exact 未重证（路线二规则允许），与路线一相同。
- GAP-7：$V_j$ 中 $j$ 的取值范围是读法假设。我方判定无后果（第 2 节第 2 条）。
- 精确有理 LP 路径 `q6_route2_lp_k2.py` 抛 `UnboundedLPError`，改用 scipy/HiGHS，自标 [FAILED]（精确求解器路径），LP 结论无对偶证书。

本判定新增的：

- GAP-8（新）：R2 的 [VERIFIED-LP] 标签不成立，其 $m\le7$ 的 LP 无法表达全 size 盲带来的长程约束；全 size 盲的真实值为 $K=2:0.61$、$K=3:523/928$、$K=4:0.543703751$，均严格大于 $\rho_K$ [VERIFIED-LP]。
- GAP-9（新）：S1 在路线二自身的构造形状（$f$ 为 count grid + 全 size 1-blind）下对 $K=2$ 不可行，因此 $K=2$ 的**确定性**条款也未建立（D2）[VERIFIED-LP]。
- GAP-10（新）：S5 隐含要求"与 $\pi$ 不交的 $K$-set 值不依赖 $T$ 的选择"，路线二在 $f$ 不是 count grid 时（per-T LP 的最优解）没有交代这一点；路线一的族里该值恒为 $F(K,0)$，自动成立。

---

## 6. 判定

- 结论一致：是（同一 $\rho_K$、同一 sup-inf、同一 $\varepsilon_n$、同一 $n\ge4K^5$）。
- 量词一致：定理级一致，清单级有五处差异（Q-1 至 Q-5），其中 Q-3 是实质分歧。
- 路线二是否有额外假设 / 缺口 / 错误：有。额外假设三条（$j\in\{0..K\}$ 的读法、ProbeLottery 的读法、全 size 1-blind）；缺口十条（GAP-1 至 GAP-10）；错误一条（R2 的 [VERIFIED-LP] 标签与 S1 的可行性，D1/D2）。
- 路线一是否被路线二反驳：否。路线一在争议点（大集合泄漏）上被我方独立 LP 支持。

**verdict = B-GAP（route two incomplete）**。路线二独立重建了硬度路线的骨架（隐藏 $\pi$ + 盲 predictor + canonical transcript + union bound + $\Phi(0,K)\le\rho_K$），常数与路线一逐项吻合，这对路线一的三步装配是有价值的独立佐证；但它的硬族要求比路线一强一档（盲度不设 size 上限），在该要求下目标值 $\rho_K$ 不可达，基实例、校准紧性与 band 延拓三处均未闭合。路线一无可展示的错误，装配三步的 [HAND-PROOF-UNREVIEWED] 标签维持不变。
