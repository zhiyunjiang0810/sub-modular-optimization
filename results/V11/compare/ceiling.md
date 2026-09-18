# ROUTE-COMPARISON：thm:ceiling（台账 T8，criterion B）

判定人：route-comparison judge（TASKS11 Q3）。本文件只新建，不改动仓库中任何已有文件。未运行 git。

## 0. 比对的两条路线

- **路线一（仓库证明）**
  - 甲：`paper/sections/appendix_proofs.tex` 的 `\subsection{The ceiling ...}\label{app:ceiling}`（约 1211 行起）
    与 `results/J5_hardcore/J5_ceiling_proof.md`（J5 三步交换证明、slack 恒等式 (7)(8)(9)）。
  - 乙：`paper/sections/appendix_model_proofs.tex` 末尾 remark（Prop 2(iii) 加 Horel-Singer observation）
    与 `HANDOFF_ADDENDUM_2026-09-18.md` §C（三行 adversary 与 chain-sum 下界）。
  - 台账卡：`THEOREM_LEDGER.md` 的 `## T8`。
- **路线二（盲证）**：`results/V11/route2/ceiling.md`，输入只有 `results/V11/inputs/` 四个文件。

判定人自己的复核脚本（放在 scratchpad，不入库）：
`judge_ceiling.py`（sympy 恒等式 + Fraction 网格）、`judge_ceiling2.py` + `grid.py`（任意 in-band predictor 抽样 + 全格点 LP）。

---

## 1. Step correspondence table（路线二每一步 → 路线一）

| 路线二 | 内容 | 路线一对应步 | 判定 |
|---|---|---|---|
| L0 | chain bound $f(A)/\eta_u\le\tilde f(A)\le\eta_o f(A)$ | app:ceiling "matching upper bound by exhaustive search" 第一段的 telescoping；等价于 appendix_model_proofs.tex 的 \eqref{eq:valueband} | 同一步 |
| L1 | 归一化 $\hat f=\tilde f/\eta_o$，band 变 $[d/\eta,d]$ | 无对应步 | **different route**：路线一全程保留 $(\eta_u,\eta_o)$ 两个因子，不做归一化。两者等价，L1 只是记账方式 |
| L2 | 残差 $r=f-\tilde f$ 单调且 marginal $\le\theta d$ | 无对应步 | **different route**：路线一用 $X,Y$ 两个并集增量直接耦合，不引入 $r$ |
| U1 | $\tilde f(A)=|A|$，$f_H=\eta_u|A\cap H|+|A\setminus H|/\eta_o$，$h=\min\{K,n-K\}$ | J5 §4 / app:ceiling "The construction"：$\tilde f(T)=b|T|$，权重 $b/\eta_o$ 在 $S$ 上、$\eta_u b$ 在 $S$ 外 | 同一构造的两种摆法。路线一把重元素放在 $N\setminus S$（$n-K$ 个），路线二只放 $h$ 个。两者比值恒等 `[VERIFIED-SYMBOLIC]`（judge_ceiling.py A3'） |
| U2 | error 恰好 $(\eta_u,\eta_o)$，两侧都取等 | J5 §4 "单独取高权元素和低权元素分别达到 $u$ 与 $o$"；app:ceiling 同段并补 all-pairs | 同一步，但路线一多覆盖 all-pairs 定义（见 §2） |
| U3 | determinism 落点：transcript 与 $T$ 先于 $H$ 固定 | app:ceiling "Deterministic algorithms" 第一句；J5 §4 "其完整查询 transcript 和输出都确定" | 同一步 |
| U4 | $|T|\le K\Rightarrow$ 存在 $H\subseteq N\setminus T$ | app:ceiling "With $n\ge2K$ there is a $K$-set $O\subseteq N\setminus T$"；J5 §4 把输出补成 $K$-集 $S$ 再把重权放到 $S$ 外 | 同一步。路线一的 J5 版本用"补足输出"绕开 $H$ 与 $T$ 不交的计数，覆盖 $n>K$；app:ceiling 正文版只写 $n\ge2K$ |
| U5 | modular 的 optimal $K$-set $=H\cup(K-h)$ 轻元素 | J5 §4 "一个最优解取 $a_0$ 个高权元素与 $K-a_0$ 个低权元素" | 同一步 |
| U6 | 比值 $=K/(K+(\eta-1)h)=C^\ast_{n,K}$ | J5 §4 同式 | 同一步 `[VERIFIED-SYMBOLIC]` |
| U7 | $n=K$：$h=0$ 时另取单元素 $H$ 做端点校准 | J5 §4 末段与 app:ceiling "At $n=K$ ... mix high and low weights on at least two elements" | 同一步，修法相同 |
| C1 | 主不等式 (J)：$f(O^\ast)-f(S)\le\theta[f(S\cup O^\ast)-f(S)]$ | J5 第二步式 (6) $B\le(1-1/\eta)Z+A/\eta$ | **同一不等式，不同推法**。路线一：$X\le Y$ 加两条链的 band；路线二：$\tilde f(S)\ge\tilde f(O^\ast)$ 加 $r$ 的单调性。代数上恒等（$B-A\le\theta(Z-A)\Leftrightarrow B\le\theta Z+A/\eta$） |
| C2 | $f(S\cup O^\ast)-f(S)\le\sum_{o}d_o(S)$ | J5 第一步式 (5) 的 $Z-A\le D$ | 同一步 |
| C3 | $d_o(S)\le d_o(S\setminus s)\le\eta\Delta_s$ | J5 第一步式 (3) | 同一步，逐字相同 |
| C4 | $\sum_s\Delta_s\le f(S)$，故 $m\le f(S)/K$ | J5 第一步式 (2) $0\le R\le A$ 再对 $aK$ 对求和成式 (4) | 同一步的两种取法：路线一求和用 $R$，路线二取 $\min$ 用 $m$。$Km\le R\le A$，最终界相同 |
| C5 | 合并得 $(\ast)$ $f(S)\ge\frac{K}{K+(\eta-1)j}f(O^\ast)$ | J5 第三步式 (1) $B\le(1+(\eta-1)a/K)A$ | 同一步 `[VERIFIED-SYMBOLIC]`（A4, A4'） |
| C6 | $j\le\min\{K,n-K\}$，$x\mapsto K/(K+(\eta-1)x)$ 不增 | J5 §2 "随后只用 $a\le\min\{K,n-K\}$"；app:ceiling "$a\le\min\{K,n-K\}$ then gives $C^\ast_{n,K}$" | 同一步 |
| C7 | 逐 $j$ 的紧实例族（$S$ 权重 1，$j$ 个权重 $\eta$，$\tilde w$ 全相等） | 无对应步 | **路线二独有**：路线一只给最坏 $j$ 处的紧性（对手族），没有"对每个 $j$ 逐实例式不可改进"的族 |
| R1 / §4(c) | randomized：同族 Yao 值 $=C^\ast\cdot\frac{n+(\eta-1)h}{n}$ | app:ceiling "Randomized algorithms" 段的 $(1-\frac Kn)\frac1\eta+\frac Kn$ | 同一计算，路线二覆盖全部 $n$；令 $h=K$ 时两式恒等 `[VERIFIED-SYMBOLIC]`（A5, A5'） |
| §4(b)(d) | deterministic 非空洞；逐串应用不是更强结论 | 台账 T8 的"禁止声称（M4 追加）"与 J5 §5 末段 | 结论一致，路线一更强（见 §4 divergence D5） |
| N1 / check_candidate | 只用成对推论不够（$n=4,K=3,\eta=2$，比值 $5/7$ 但 LP infeasible） | J5 §5 "需要 $\tilde f(S)\ge\tilde f(O)$ 与全部交换比较" | 路线二把定性说明量化 |
| G5 | 只留 single-swap 族时 $n=6,K=3,\eta=2,j=3$ 最坏值 $3/7$，`[FAILED]` 位置明确 | J5 §5 "只有 one-swap local optimality 时，不能直接调用这个证明" | 同一结论，路线二给出确切数字。判定人独立复算：LP 值 $0.428571\ldots=3/7$，与完整族的 $1/2$ 分离 `[VERIFIED-LP]` |

---

## 2. 路线一中路线二没有覆盖的步骤

| 路线一步骤 | 位置 | 路线二是否覆盖 |
|---|---|---|
| 四项非负 slack 恒等式 (7)，$E$ 的三项分解 (8)，单次交换四项分解 (9)，`[VERIFIED-SYMBOLIC]` | J5 §3 与 app:ceiling 的 `\eqref{eq:ceiling-slack}` | **未覆盖**。路线二逐条不等式推导，没有做成一条非负组合证书，也没有等价物 |
| adversary 的 all-pairs error 也恰为 $(\eta_u,\eta_o)$（modular 故任意 all-pairs 比值是两个单元素值的加权平均） | app:ceiling "The construction"；J5 §4 | **未覆盖**。路线二只按 Definition 1 的 single-element 版检验（其输入 `definition1.md` 也只给这一版），故这不是路线二的缺口，是覆盖面差异 |
| 穷举给出 $1/\eta$ 的三行论证作为独立推论 | app:ceiling "The matching upper bound by exhaustive search" | **部分覆盖**。路线二证了 L0（该论证的全部内容），但没有把 $f(S)\ge\tilde f(S)/\eta_o\ge\tilde f(O^\ast)/\eta_o\ge f(O^\ast)/\eta$ 这一行写出来 |
| 输出小于 $K$ 时"补足到 $K$-集"这一归约 | J5 §4、§5 与 app:ceiling "completing a smaller predicted maximizer to size $K$ loses nothing" | **覆盖方式不同**。路线二 U4 直接按 $|T|\le K$ 处理上界，attainment 侧直接设 $|S|=K$ |
| randomized 与 deterministic 的严格分离反例：$n=3,K=2,\eta=3$，均匀随机 2-集期望 $\ge\frac23 f(N)$ 而确定性值 $1/2$ | J5 §5 末段、app:ceiling "Scope"、台账 T8 | **未覆盖**。路线二只说"自己这一族给不出 $C^\ast$ 级别的 randomized 上界"，不判断 randomized 值是否超过 $C^\ast$（其 G1） |
| 范围声明：穷举查询 $\binom nK$ 次，不产生多项式查询算法，不改变 thm:hardness 的适用范围 | J5 §5、app:ceiling 的 GLOSSARY 注释 | **部分覆盖**。路线二在 1.3 与 G4 记了 query size $\binom nK$，没有写与 hardness 定理的范围隔离（不在其输入范围内） |

---

## 3. 结论与 quantifier 比对

### 3.1 结论

两条路线得到**同一个结论**：

- 上界侧：$\forall$ deterministic $\mathcal A$（任意查询、$|T|\le K$），$\forall\eta_u,\eta_o\ge1$，$\exists(f,\tilde f)$ error 恰为 $(\eta_u,\eta_o)$，使 $f(T)\le C^\ast_{n,K}(\eta)f(O^\ast)$。
- 下界侧：$\tilde f$ 在全部 $K$-subsets 上的 maximizer $S$ 满足逐实例式 $f(S)\ge\frac{K}{K+(\eta-1)|O^\ast\setminus S|}f(O^\ast)\ge C^\ast_{n,K}(\eta)f(O^\ast)$。
- 闭式两支与 $n=2K$ 处相接，两路线写法一致。

### 3.2 quantifier 逐条

两侧共有且写法一致的量词：`deterministic`；`arbitrary query access`；`output size $|T|\le K$`；`$\forall(\eta_u,\eta_o)$，$\eta$ 只依赖乘积`；`error exactly（两侧取等）`；`$\exists$ 实例依赖算法（$\forall\mathcal A\exists(f,\tilde f)$）`；`attainment 的量词是"存在算法对所有实例"`；`$|S|=K$`；`每一个 maximizer $S$（对抗 tie-breaking）`；`无最小重叠假设`；`$f(O^\ast)=0$ 平凡`。

**只在路线二出现、路线一没有的量词/限定**

- Q1 `$O^\ast$ 的 optimality 在 attainment 推导中未被使用，$(\ast)$ 对任意 $K$-集 $O^\ast$ 成立`。路线一的陈述与 J5 §2 始终把 $O$ 设为 optimal，只说"不需要最小重叠"，没有把 optimality 本身声明为多余。
- Q2 `$K=1$ 也成立；$K\ge2$ 对本命题非必需`。路线二在 G4 逐字检验；判定人在 $2\le n\le8$、$K=1$ 的网格上复核通过。
- Q3 `"arbitrary query access" 的最强读法：输出是 $\tilde f$ 这个函数的确定性函数`。路线一只说 transcript 相同，未把读法写成量词。

**只在路线一出现、路线二没有的量词/限定**

- Q4 `构造的 error 在 all-pairs 定义下也恰为 $(\eta_u,\eta_o)$`（台账另记 J4 的 253,220 个 all-pairs 增益 `[VERIFIED-EXHAUSTIVE]`）。路线二未涉及 all-pairs 定义。
- Q5 `app:ceiling 开头写 $K\ge1$、$n\ge2K$`，而 `statement_ceiling.md` 与台账 T8 写 $2\le K\le n$。路线一内部两处 $K$ 的下界不一致；路线二的 Q2 与 app:ceiling 的 $K\ge1$ 同向。
- Q6 `randomized 上界的量词是"逐算法固定实例"，且随机值不能逐种子套用确定性界`。路线二 §4(b) 表达了同一意思，但没有写成台账那条"禁止声称"。

因此 `quantifier_match = false`：两份量词清单不完全重合。上列五条差异**没有一条改变命题的真值**，全部是覆盖面或强化，不是冲突。

---

## 4. 路线二是否有额外假设、缺口或错误

判定人逐条独立复算（不复用路线二的脚本）：

| 检查 | 方法 | 结果 |
|---|---|---|
| 两支闭式等价、$n=2K$ 相接 | sympy `simplify` | `[VERIFIED-SYMBOLIC]` 全 0 |
| U6 比值化简（任意拆分 $\eta_u,\eta_o$） | sympy | `[VERIFIED-SYMBOLIC]` |
| 路线一对手比值 $\equiv$ 路线二对手比值 | sympy | `[VERIFIED-SYMBOLIC]` |
| $\theta\eta=\eta-1$ 与 $(\ast)$ 的重排 | sympy | `[VERIFIED-SYMBOLIC]` |
| randomized 因子（一般拆分）与 $h=K$ 时退化为 $(1-K/n)/\eta+K/n$ | sympy | `[VERIFIED-SYMBOLIC]` |
| 路线乙的 $\epsilon=(\eta-1)/(\eta+1)$、$c=2\eta_u/(\eta+1)$、$(1-\epsilon)/(1+\epsilon)=1/\eta$ | sympy | `[VERIFIED-SYMBOLIC]` |
| U1/U2 对手族：band 可行、两侧都取到、比值 $=C^\ast$ | Fraction，$2\le n\le8$、$1\le K\le n$、四组 $(\eta_u,\eta_o)$ 全格点 | `[VERIFIED-EXHAUSTIVE]` 无例外 |
| C7 紧实例族：band、$S$ 的 maximality、$O^\ast$ 的 optimality、比值 | Fraction，$2\le n\le8$、$1\le K\le n$、$\eta\in\{3/2,2,3\}$、全部 $j$ | `[VERIFIED-EXHAUSTIVE]` 无例外 |
| C1/C2/C3/C4/$(\ast)$ 在**任意 in-band predictor** 上 | 逐子集构造 $\tilde f$（不限 modular），coverage 型 $f$，88 个成功实例、434 对 $(S,O^\ast)$，Fraction | `[VERIFIED-EXHAUSTIVE]` 无违反 |
| $(\ast)$ 是否可改进 | 全格点 LP（$f$ 与 $\tilde f$ 各 $2^n$ 个变量，monotone + submodular + band + $\tilde f$-maximality），$n\in\{3,4,5\}$、$K\in\{2,3\}$、$\eta\in\{3/2,2,3\}$、全部 $j$ | `[VERIFIED-LP]` 每一格 LP 最优值 $=K/(K+(\eta-1)j)$，逐格相等 |
| G5 的 `[FAILED]` 位置 | 同一 LP，只留 single-swap 族 | `[VERIFIED-LP]` $n=6,K=3,\eta=2,j=3$：single-swap 只给 $0.428571\ldots=3/7$，完整族给 $1/2$。路线二的数字正确 |

**没有发现错误**。路线二的每一条数值与代数断言都复算通过。

**路线二的额外假设（G3，全部是保守读法，不构成缺口）**

1. "arbitrary query access" 取最强读法（输出是整张 $\tilde f$ 表的确定性函数）。更弱的 query model 是其子类，结论照样成立。
2. "output of size at most $K$" 读作 $|T|\le K$ 且 $T\subseteq N$。
3. $\eta_u,\eta_o\ge1$ 与 convention B 的 $\eta_u,\eta_o>0$ 两种读法都覆盖（U1/U2 只用 $\eta_u>0,\eta_o>0,\eta\ge1$）。
4. attainment 侧先用 L1 把 band 归一化成 $[d/\eta,d]$，合法性来自 convention B 的 scaling 段。判定人复核：归一化只是除以正常数，不改 argmax，不改 $\eta$。

**路线二的 gaps**

- G1（randomized ceiling 的精确值）：路线二只从自己那一族得到 $C^\ast\cdot\frac{n+(\eta-1)h}{n}$，不判断真正的 randomized minimax 值。**路线一同样把它记为 OPEN**，并且多给一个严格分离反例。所以这是两条路线共有的开口，不是路线二独有的缺口。
- G2（$n=K$ 时 error 两侧不能同时取等）：路线二在 U7 里自行闭合（改取单元素 $H$），与路线一 J5 §4 末段的修法一致。**已闭合**，只剩一条正文措辞提醒（正文若写"该实例即为所需"需加 $n>K$）。
- G3（上列四条读法）：保守选择，已记录理由。
- G4/G5 不是缺口，是量词审计与推广边界的记录。
- 真正留白的只有一条：**路线二没有做非负 slack 组合证书**（路线一的 (7)(8)(9)）。这不影响结论，只是缺一层 oracle 覆盖。

**路线二有没有与路线一矛盾的地方**：没有。逐条核对下来，路线二的每一步要么与路线一同步，要么是路线一某条定性说明的量化版本。

---

## 5. 路线甲 vs 路线乙（$n\ge2K$ 的 attainment 方向）

| | 路线甲（app:ceiling） | 路线乙（Prop 2(iii) + Horel-Singer） |
|---|---|---|
| 位置 | `paper/sections/appendix_proofs.tex`，"The matching upper bound by exhaustive search" | `paper/sections/appendix_model_proofs.tex` 末尾 remark；`HANDOFF_ADDENDUM_2026-09-18.md` §C 第二段 |
| 论证 | 沿链把 band 逐项加起来得 $f(S)/\eta_u\le\tilde f(S)\le\eta_o f(S)$；取 $\hat S$ 为 $\tilde f$ 在 $|\cdot|\le K$ 上的 maximizer，三个不等式串起来得 $f(\hat S)\ge f(O^\ast)/\eta$ | Prop 2(iii)：同一条链求和给出 \eqref{eq:valueband}，再乘 $c=2\eta_u/(\eta+1)$ 把 $c\tilde f$ 变成 level $\epsilon=(\eta-1)/(\eta+1)$ 的 value-accurate surrogate；引 Horel-Singer 的 observation（$1\pm\epsilon$ 内函数的 $\alpha$-approx 是 $f$ 的 $\alpha\frac{1-\epsilon}{1+\epsilon}$-approx），$\alpha=1$ 代入得 $1/\eta$；再说明 rescaling 不改 maximizer |
| 依赖 | 自足，只用 Definition 1 加 monotonicity | 依赖 Prop 2(iii)（同文件内已证）加一条外部 observation（文中只引不证，但那一行本身可一步展开：$f(S)\ge g(S)/(1+\epsilon)\ge g(O^\ast)/(1+\epsilon)\ge\frac{1-\epsilon}{1+\epsilon}f(O^\ast)$） |
| 覆盖 | $n\ge2K$ 给 $1/\eta$；per-instance 段另外覆盖 $K\le n<2K$ | 只给 $1/\eta$，即只覆盖 $n\ge2K$；不给逐实例式，也不给 $n<2K$ 的 $C^\ast$ |
| 代数复核 | $\eqref{eq:valueband}$ 的链求和：判定人复核通过 | $\epsilon,c$ 三条等式 `[VERIFIED-SYMBOLIC]`（A6, A6', A6''） |
| 完整性 | **完整** | **完整**（在 $n\ge2K$ 这一档内；引用的 observation 是一行可展开的） |

两条都完整，并且两条都是同一条链求和的两种包装：路线乙比路线甲多绕一次 value accuracy 的转换。addendum B11 定的分工（正文用乙、附录用甲）与这个判断不冲突。

**路线乙的一个非数学缺陷**：`paper/sections/appendix_model_proofs.tex` 第 51 行引的 bib 键是 `horel2016`，而 `paper/references.bib` 里只有 `horel2016maximization`（`paper/sections/related.tex` 与 addendum §C 用的都是后者）。这一条会在编译时变成未定义引用。

---

## 6. Divergences（确切清单）

- **D1**（构造摆法）路线一把重权放在 $N\setminus S$（$n-K$ 个元素），路线二只放 $h=\min\{K,n-K\}$ 个。比值恒等 `[VERIFIED-SYMBOLIC]`，无实质差别。
- **D2**（C1 的推法）路线一用 $X\le Y$ 加两条链的 band；路线二引入残差 $r=f-\tilde f$ 并用其单调性。代数上恒等，路线二多了一步 L1 归一化。
- **D3**（C4 的取法）路线一求和（$R=\sum_s r_s\le A$），路线二取最小（$m\le f(S)/K$）。最终界相同。
- **D4**（紧性）路线二给出逐 $j$ 的紧实例族 C7，说明 $(\ast)$ 对每个 $j$ 都不可改进；路线一只在最坏 $j$ 处给紧性。判定人 LP 复核支持路线二的更强说法。
- **D5**（randomized）路线一给出 $n=3,K=2,\eta=3$ 的严格分离（随机 $\ge2/3>1/2=C^\ast$），据此把 randomized minimax 记为 OPEN；路线二只说自己那一族给不出 $C^\ast$，不判断是否可超过。路线一在这一点上更强，路线二更保守，不冲突。
- **D6**（all-pairs）路线一额外声明构造在 all-pairs 定义下 error 也恰为 $(\eta_u,\eta_o)$；路线二的输入只给 single-element 版，未涉及。
- **D7**（slack 证书）路线一有非负组合恒等式 (7)(8)(9) 并已符号核过；路线二无对应物，改用逐格 LP 的"最优值相等"作为不可改进性的 oracle。两种 oracle 互补。
- **D8**（$K$ 的下界）`statement_ceiling.md` 与台账 T8 写 $2\le K\le n$，而 `app:ceiling` 开头写 $K\ge1$。路线二独立发现 $K=1$ 逐字成立。路线一内部这两处需要对齐。
- **D9**（$n$ 的下界）`app:ceiling` 的正文构造段固定 $n\ge2K$，一般 $n>K$ 的对手在同一 subsection 后面的 "The matching adversary for every $n>K$" 段。路线二从一开始就用统一的 $h=\min\{K,n-K\}$。读者会在同一 subsection 里看到两个不同的 $n$ 前提，建议正文点一句。
- **D10**（措辞，非数学）`appendix_proofs.tex` 的 "Scope" 段第一句用了 CLAUDE.md 第 8 条与 addendum §A6 禁用词表里的那个副词（"The randomized value is ...ly different"）。该段需改写。
- **D11**（bib，非数学）`appendix_model_proofs.tex` 第 51 行的 `horel2016` 是未定义键，应为 `horel2016maximization`。

## 7. Route-two gaps（确切清单）

- **RG1** randomized ceiling 的精确值未定。路线二只从 U1 那一族得 $C^\ast\cdot\frac{n+(\eta-1)h}{n}$。**同一开口在路线一也是 OPEN**，且路线一另有严格分离反例，所以这一条不构成路线二相对路线一的欠缺。
- **RG2** $n=K$ 时 "error 恰好 $(\eta_u,\eta_o)$" 需换实例。路线二在 U7 里已自行闭合，与路线一修法一致。剩下的只是一条正文措辞提醒。
- **RG3** 四条添加的读法（arbitrary query access 的最强读法、$|T|\le K$、$\eta_u,\eta_o$ 的域、L1 归一化）。全部保守，全部不改变结论。
- **RG4** 任务描述里的 "$K=2$ 用于 ProbeLottery item" 在本陈述中无对应项。路线二仍补了 $K=2$ 走查。非缺口。
- **RG5** 路线二没有做非负 slack 组合证书（路线一的 (7)(8)(9)）。属于 oracle 覆盖面的欠缺，不影响结论。
- **RG6** 路线二未检验 all-pairs 版 error（其输入文件不含该定义）。属于覆盖面差异。

## 8. Verdict

**B-PASS**。

理由三条。第一，两条路线的结论逐字一致，上界侧与下界侧的核心量词全部重合。第二，路线二的每一步都能在路线一里找到对应步（L1、L2、C7 除外，这三步是记账方式与额外紧性，不是不同结论），且判定人独立用 sympy、Fraction 全格点与全格点 LP 复算，未发现任何错误。第三，路线二没有与路线一的任何一步相矛盾；它留下的开口（RG1）在路线一里同样是 OPEN。

路线甲与路线乙对 $n\ge2K$ 的 attainment 方向**都完整**，两者是同一条链求和的两种包装，路线乙多依赖一条一行可展开的外部 observation 与一个当前写错的 bib 键。

状态标签汇总：路线二的构造与紧实例 `[VERIFIED-EXHAUSTIVE]`；闭式、比值与 randomized 因子 `[VERIFIED-SYMBOLIC]`；$(\ast)$ 的不可改进性 `[VERIFIED-LP]`；一般集合上的装配仍是 `[HAND-PROOF-UNREVIEWED]`，与路线一的标签一致。
