# N1: reduced LP 的一般 K 对偶证书

复现脚本：`results/N1_dual_certificate.py`（实测 60 秒，320/320 检查 PASS，退出码 0 当且仅当全部 PASS）。
数据：`results/N1_dual_certificate.json`。
前置：`results/T3_K3_closed_form.md`（第一晚的 K=2,3,4 证书与 primal 结构）、`code/reduced_lp.py`（LP 定义与行序）、`RESEARCH_STATE.md` 的 R6、R10。

## 0. 净结论（先读这段）

R10 的一般 K 猜想 **ρ_K^LP(η) = min_{0≤j≤K−1} V_j(η)**，两个方向现在都是符号级结论：

| 方向 | 内容 | N1 之前 | N1 之后 |
|---|---|---|---|
| LP ≤ V_j（易） | T3 的 primal 解在整段可行、目标 = V_j | [VERIFIED-SYMBOLIC]（T3，一般 K） | 独立复验通过（Part B / Part E） |
| **LP ≥ V_j（难）** | 每段一个显式 dual feasible 解，b'y = V_j | 仅 K=2,3,4 [VERIFIED-SYMBOLIC]；一般 K [CONJECTURE] | **一般 K 的显式公式 + sympy 符号验证**（Part A/C）+ K=2..10 逐段独立机器验证（Part E） |
| V_j = min_i V_i 于段 j | 分段点为整数 2..K | 只符号验证了相邻 V_j 的交点 | 一般 K 的完整全序结论（Part D） |

于是：

> **[VERIFIED-SYMBOLIC]（一般符号 K；关于"一般 K"的确切含义见 §4）**
> 对每个 K ≥ 2、每个 j = 0,…,K−1、每个 η ∈ [K−j, K−j+1]（j=0 时 η ∈ [K,∞)），
> reduced LP（`code/reduced_lp.py`）的最优值恰等于 V_j(η) = 1 − q^j(1 − (K−j)/(Kη))。
> 等价地 ρ_K^LP(η) = min_{0≤j≤K−1} V_j(η)，分段点恰为整数 η = 2,3,…,K。

这把 R10 里"一般 K 猜想 [CONJECTURE]（205 点数值支持 + 两个辅助恒等式）"升级为定理（在 reduced LP 这一层）。

**没有**改变的是 R6/R10 的另一半（务必不要在论文里混淆）：reduced LP 值 = 真实 ρ_K(η) 仍依赖
(i) "reduced LP ≤ ρ_K"（每条约束都是有效不等式）的手证 [HAND-PROOF-UNREVIEWED]，
(ii) 相等方向（存在实例达到该值）只在 K ≤ 4 的有限点 [VERIFIED-LP]。
所以对论文可写的净陈述是：

> **single-step predictive greedy 的保证 ρ_K(η) ≥ min_j V_j(η) 现在对一切 K 有一个机器验证过的证明**（模 R6 那一步手证），
> 而"这个界紧"仍只在 K ≤ 4 的有限点验证过。

两个附带结论：

- **推论 A（mono 冗余）**：monotonicity 约束 g_{t+1,i} ≤ g_{t,i} 的对偶乘子恒为 0，下界证明完全不用它；把 mono 行从 LP 删掉不改变最优值。[VERIFIED-SYMBOLIC]（Part A/E）+ [VERIFIED-LP]（Part F3，K=2..7 网格，偏差 2.2e−16）。见 §5。
- **推论 B（与已知两界的关系）**：U_K − V_{K−1} = q^{K−1}(η−1)/(Kηk1) ≥ 0（[VERIFIED-SYMBOLIC]，一般 K），且 L_K(η) ≤ min_j V_j(η) ≤ U_K(η) 在 K=2..24 网格上成立（[VERIFIED-LP]；L_K 一侧无符号证明）。即新闭式严格夹在论文的 Theorem 6 下界与 R7 显式实例上界之间，η=1 处三者的 U/V 差为 0。

## 1. 记号与符号约定

LP（`code/reduced_lp.py`，行序原样保留）：变量 x = (d_0..d_{K−1}, g_{0,0}..g_{K,K−1})，全部 ≥ 0，
min Σ_t d_t s.t. A x ≤ b，对每个 t = 0..K−1 一个 1+3K 行的块：

    sum(t)     : −Σ_i g_{t,i} − Σ_{s<t} d_s          ≤ −1
    pred(t,i)  : g_{t,i}/η − d_t                     ≤ 0
    mono(t,i)  : g_{t+1,i} − g_{t,i}                 ≤ 0
    cons(t,i)  : g_{t,i} − d_t − (1−1/η) g_{t+1,i}   ≤ 0

**符号约定**：min c'x s.t. Ax ≤ b, x ≥ 0 的对偶是 max b'y s.t. A'y ≤ c, **y ≤ 0**。这正是 scipy
`res.ineqlin.marginals` 的约定，本文件与脚本全程使用，所以下面所有乘子都是**非正数**。弱对偶给出
b'y ≤ c'x，因此一个 dual feasible 的 y 配上 b'y = V_j 就证明 LP ≥ V_j。手写证明改用 λ = −y ≥ 0（见 §5）。

    k1 = (K−1)η + 1,   q = (K−1)η/k1 = 1 − 1/k1,   M = Kη − (K−j),
    V_j(η) = 1 − q^j (1 − (K−j)/(Kη)) = 1 − q^j M/(Kη).

## 2. 一般 K 的对偶乘子（本任务的主结果）

乘子对 i 对称（每个 i 取同一个值），且 **y_mono(t,i) ≡ 0**。

**段 j ≥ 1，η ∈ [K−j, K−j+1]：**

| 乘子 | 公式 | 下标范围 / 备注 |
|---|---|---|
| y_sum(0)  | −q^{j−1} M / (K k1)      | |
| y_sum(t)  | −q^{j−1−t} M / k1²       | 1 ≤ t ≤ j−1 |
| y_sum(j)  | (η − (K−j+1)) / k1       | 段**右**端点归零 |
| y_sum(t)  | 0                        | t > j |
| y_cons(t) | −q^{j−1−t} M / (K k1)    | 0 ≤ t ≤ j−1 |
| y_cons(t) | −(K−1−t) / (K(η−1))      | j ≤ t ≤ K−1（t = K−1 时恒为 0）|
| y_pred(t) | 0                        | t < j |
| y_pred(t) | −(η − (K−t)) / (K(η−1))  | j ≤ t ≤ K−1；t = j 时段**左**端点归零 |
| y_mono(t) | 0                        | 全部 t |

**段 j = 0，η ∈ [K, ∞)**（与 T3 已给出的一般 K 公式相同）：

    y_sum(0) = −1/η,   y_sum(t) = 0 (t ≥ 1),
    y_cons(t) = −(K−1−t)/(K(η−1)),   y_pred(t) = −(η−(K−t))/(K(η−1)),   t = 0..K−1.

读法：

- 支撑集与 T3 报告的模式完全一致：sum(0..j)、cons(0..K−2)、pred(j..K−1)；mono 全 0。
- 两个边界因子正如 T3 预测：段 j 的**最后一个** sum 乘子含因子 (η − (K−j+1))，在段右端点归零；段 j 的**第一个** pred 乘子含因子 (η − (K−j))，在段左端点归零。两端点上对偶退化，这就是分段点落在整数上的机制。
- t < j 的乘子是"几何"部分（q 的幂 × M / k1 或 k1²），t ≥ j 的乘子是"预测"部分（η 的一次有理函数，**与 j 无关**）。分界恰好落在 primal 从 consistency 步切换到 prediction 步的位置。
- y_sum(0) = y_cons(0)（j ≥ 1 时）不是巧合：这正是变量 g_{0,i} 的对偶等式，因为 g_{0,i} 只出现在 sum(0)、pred(0)、mono(0)、cons(0) 四行里，而 y_pred(0) = y_mono(0) = 0。
- j = 0 段不是 j ≥ 1 公式在 j→0 的特例（段 [K,∞) 没有右端点，y_sum(0) 的表达式不同），必须单独写。
- **与第一晚的一致性**：脚本 Part G 把上表代入 K=2,3,4 的全部 9 个段，与 `results/T3_K3_closed_form.json` 里第一晚独立求得的乘子逐个符号比对，**58 个乘子全部相等，0 处不符**。

**primal（来自 T3，此处复用并复验）**，对 i 对称 g_{t,i} = G_t：

    d_t = q^t / k1        (t < j),      d_t = q^j / (Kη)   (t ≥ j),
    G_t = q^{min(t,j)}/K  (t = 0..K).

（注：T3 文档正文写的"G_t = q^j 冻结"应读作**指数**冻结在 j，即 G_t = q^j/K；字面理解成 G_t = q^j 会违反 mono 约束。`results/T3_K3_closed_form.py` 的 `primal_x` 用的正是 q^{min(t,j)}/K，本文与代码一致。）

紧/松模式（Part B 全部符号验证）：

| 约束族 | t < j | t ≥ j |
|---|---|---|
| sum(t)  | 紧 | 松，松量 (t−j) q^j/(Kη) |
| pred(t) | 松，松量 q^t(η−1)/(Kη k1) | 紧 |
| mono(t) | 松，松量 q^t/(K k1) | 紧 |
| cons(t) | 紧 | 紧 |

与 §2 的对偶支撑集互补松弛相容；mono 是唯一"紧但乘子为 0"的一族（这是允许的，见推论 A）。

## 3. 验证方法与结果（320/320 PASS）

脚本分 7 部分。A–D 是**一般符号 K** 的验证（K, j, t, i 同时是自由符号）；E 是 K = 2..10 逐 (K,j) 的独立暴力验证；F 是数值对照；G 是与第一晚的一致性。

**Part A — 对偶可行性 A'y = c（11 项 PASS）。** primal 最优解每个分量都 > 0，互补松弛强制取等号，所以验证的是等式而非不等式。
- 变量 g_{t,i} 的对偶等式（记 D2_t）：−y_sum(t) + y_pred(t)/η + y_cons(t) − (1−1/η)y_cons(t−1) = 0（mono 项因 y_mono = 0 消失）。按 t 的 6 个分支（t=0；1≤t≤j−1；t=j；j+1≤t≤K−1；t=K；以及 j=0 段的 t=0）逐一符号验证。q 的幂由一个自由正符号承载（Qp = q^{j−1−t}），所以每条恒等式对**所有**指数同时成立，即对该分支里的所有 t 同时成立。
- 变量 d_t 的对偶等式（记 D1_t）：−Σ_{s>t} y_sum(s) − K(y_pred(t)+y_cons(t)) = 1。含对 t 的求和，用**向下归纳**消掉求和号：
  (i) t ≥ j：Σ_{s>t} y_sum(s) = 0，且 y_pred(t) + y_cons(t) = −1/K（符号验证）；
  (ii) 基例 t = j−1：−y_sum(j) − K·y_cons(j−1) = 1（符号验证）；
  (iii) 步进 t ≤ j−2：(D1_t) − (D1_{t+1}) = −y_sum(t+1) − K y_cons(t) + K y_cons(t+1) = 0（符号验证；这一条等价于 q = 1 − 1/k1 的定义）。
  三条合起来给出每个 t 的 D1_t，全程没有符号求和。
- b'y = V_j：b 在 sum 行为 −1、别处为 0，故 b'y = −Σ_{t=0}^{j} y_sum(t)，同样含求和。绕开方式：由 D1 在 t=0 处得 Σ_{s>0} y_sum(s) = −1 − K(y_pred(0)+y_cons(0))，于是
  b'y = −y_sum(0) − Σ_{s>0} y_sum(s) = 1 + K·y_cons(0) − y_sum(0)，代入公式后 sympy 精确化简为 1 − q^j M/(Kη) = V_j。j = 0 段直接 b'y = −y_sum(0) = 1/η = V_0。

**Part B — primal 可行性与 c'x = V_j（12 项 PASS）。** 部分和 P_t = Σ_{s<t} d_s 同样用归纳而非几何级数：t ≤ j 时 P_t = 1 − q^t，t ≥ j 时 P_t = 1 − q^j + (t−j)q^j/(Kη)；基例与步进各一条符号等式，两个断言在 t=j 处相容也验证了。随后逐族验证四类约束的紧/松表达式（§2 末的表），最后 c'x = P_K = V_j。结论与 T3 相同（T3 已对一般 K 验证过 primal 可行性），此处是独立复验。

**Part C — 符号不等式 y ≤ 0（15 项 PASS）。** 段 j ≥ 1 参数化为 η = u + s，u = K−j ∈ [1,K−1]，s ∈ [0,1]；高分支下标写成 t = j+m，m ∈ [0,u−1]，于是 K−1−t = u−1−m ≥ 0。把每个变量平移到下界（K = 2+kk，u = 1+vv 或 2+vv，1−s = ww），每个符号不等式就化成"多项式的所有系数 ≥ 0（常数项 > 0 表示严格）"——这是盒上正性的精确证书，比 Sturm 更直接。例如 M = (K−1)u + Ks 展开后系数全正 ⟹ M > 0；−y_sum(j) 的分子 = 1 − s = ww ≥ 0。
两处可去奇点单独处理：j = K−1（段 [1,2]，u = 1）时高分支只剩 t = K−1，y_pred(K−1) = −(η−1)/(K(η−1)) 约分为 −1/K、y_cons(K−1) 的分子恒为 0，所以 η=1 处没有真奇点；j ≤ K−2 时段左端点 η = K−j ≥ 2，故 η−1 ≥ 1 > 0。

**Part D — V_j 在段 j 上确实是 min（6 项 PASS）。** 关键恒等式（符号 K, i, η）：

    V_i − V_{i+1} = q^i (K − i − η) / (K η k1).

在段 [K−j, K−j+1] 上：i ≤ j−1 时 K−i−η = 1 + a − s ≥ 0（a = j−1−i ≥ 0，s ≤ 1），序列递减；i ≥ j 时 K−i−η = −a−s ≤ 0，序列递增。所以 argmin_i V_i = j，相邻两段在整数 η = K−j+1 处相等（分段点为整数 2..K）。这把 T3 只验证过的"相邻交点"升级为完整的全序结论。本部分还含推论 B 的符号恒等式 U_K − V_{K−1} = q^{K−1}(η−1)/(Kηk1)。

**Part E — 逐 K 的独立暴力验证，K = 2..10（默认），η 保持符号（270 项 PASS，54 个段）。** 对每个 (K,j)：重建完整的符号 LP 矩阵（行序与 `code/reduced_lp.py` 一致），把 §2 的 y 与 x 代入，检查四件事：
(1) A'y = c（逐列 `cancel` 为 0）；
(2) y ≤ 0（每个非零乘子做精确 Sturm 根计数 + 内点与两端点符号；j=0 的无穷段用 Cauchy 根界截断）；
(3) A x ≤ b 且 x ≥ 0（同法，逐行逐变量）；
(4) b'y = c'x = V_j。
这一部分**不复用 A–D 的任何手工分支推理**，是一次完全独立的机器验证。KMAX 由环境变量 `N1_KMAX` 控制；实测 K≤8 用 22 秒、K≤10 用 55 秒、K≤12 用 121 秒，全部 PASS。

**Part F — 数值对照（5 项 PASS）。**
- F1a：K=2..6 每段各 3 点（η = K−j+1/4, 1/2, 3/4，共 60 点），闭式 y 数值上 dual feasible（y ≤ 0，A'y ≤ c）且 b'y = LP 值，最大违反 3.3e−16。
- F1b：与 scipy 的 `ineqlin.marginals` 对 i 求平均后比较（LP 关于 i 的置换对称，所以对称化后的对偶仍是对偶最优解）。**重要观察**：60 点里有 **2 点**（K=6, j=3, η=3.25 和 K=6, j=4, η=2.75）scipy 返回的是**另一个**对偶最优解——那里 primal 退化（K=6,j=3,η=3.25 处 114 行里有 76 行紧、而只有 48 个变量），对偶最优集是一个面而非顶点，scipy 的解带非零 mono 乘子（0.040 / 0.010），与我们的解在 (pred(4), cons(4), mono(4)) 三元组上不同但 y_pred+y_cons 之和相同、b'y 相同。其余 58 点对称化后与闭式在 7.6e−16 内相等。所以本检查的 PASS 判据写成"在 scipy 停留在同一面（mono 乘子为 0）的点上完全吻合"，退化点在 JSON 的 `dual_face_degenerate` 里逐条列出，**不**当作反例。
- F2：K=2..10、η 网格上 LP 值 = V_{j(η)}，最大偏差 6.7e−16。
- F3：删掉 mono 行后重解 LP，值不变（K=2..7 网格，最大偏差 2.2e−16）——推论 A 的数值确认。
- F4：L_K(η) ≤ min_j V_j(η) ≤ U_K(η)，K=2..24 网格（推论 B 的数值部分）。

**Part G — 与第一晚的一致性（1 项 PASS）。** 一般 K 公式代入 K=2,3,4 的 9 个段，与 `T3_K3_closed_form.json` 中独立得到的 58 个乘子逐个符号比对，0 处不符。

## 4. 状态标签与"一般 K"的确切含义（诚实声明）

- **[VERIFIED-SYMBOLIC]**：Part A–D 的全部恒等式与符号不等式，是关于**符号 K, j, t, i** 的精确 sympy 结论（精确有理算术，无浮点）。
- **[VERIFIED-SYMBOLIC]**：Part E 对 K = 2..10 的每个段、η 为符号变量的完整证书（Sturm 精确根计数）。
- **[VERIFIED-LP]**：Part F 的全部数值对照。
- 需要读者自行确认、**不是** oracle 验证的一步：把 Part A–D 的分支恒等式组装成"对每个 t = 0..K 恰好落入一个已验证分支"的**有限分类枚举**。这是纯组合记账（t < j / t = j / t > j / t = K；i 全对称；j = 0 单列），没有代数内容；Part E 对 K ≤ 10 的暴力验证正是这一步的机器化确认。
  因此严格的状态表述应写成：**"K = 2..10 完全 [VERIFIED-SYMBOLIC]；一般 K [VERIFIED-SYMBOLIC，模一次分支枚举]"**。REPORT 与论文里请用这种表述，不要简写成无条件的 "proved for all K"。
- 本任务**没有**触碰的：reduced LP 值 = 真实 ρ_K（R6 的手证方向与可实现性方向）。见 §0。

## 5. 翻译成手写证明（论文可直接用的形式）

令 λ = −y ≥ 0，把约束写成松弛量 ≥ 0 的形式：

    S_t     := Σ_i g_{t,i} + Σ_{s<t} d_s − 1        ≥ 0     （覆盖不等式）
    P_{t,i} := d_t − g_{t,i}/η                      ≥ 0     （prediction，coherence lemma R3(i) 型）
    M_{t,i} := g_{t,i} − g_{t+1,i}                  ≥ 0     （monotonicity）
    C_{t,i} := (1−1/η) g_{t+1,i} − g_{t,i} + d_t    ≥ 0     （coherence，R3(ii)）

因为 A'y = c 与 b'y = V_j 都是恒等式，所以对**任意** x（不必可行）成立代数恒等式

    Σ_t d_t − V_j
      = Σ_{t=0}^{j} λ_S(t)·S_t
      + Σ_{t=j}^{K−1} Σ_i λ_P(t)·P_{t,i}
      + Σ_{t=0}^{K−2} Σ_i λ_C(t)·C_{t,i},

其中 λ_S = −y_sum、λ_P = −y_pred、λ_C = −y_cons 由 §2 的表给出，在段 [K−j, K−j+1] 上全部 ≥ 0。
对可行 x，右端每项非负，故 Σ_t d_t ≥ V_j。这就是论文里可以直接写的"非负组合"证明：一行恒等式 + 一句"每项非负"。K=2 时它退化为 R4 的手证（cons(0) 与第 1 步 pred 的凸组合）。

**推论 A（mono 冗余）**：上式右端没有 M_{t,i} 项（λ_M ≡ 0）。所以 LP ≥ V_j 的证明**完全不用** monotonicity；而 T3 的 primal 解在含 mono 的 LP 里可行，故删掉 mono 行后 LP 值不变。[VERIFIED-SYMBOLIC]（Part A/E 中 y_mono = 0）+ [VERIFIED-LP]（Part F3）。
论文含义：这个下界只需要 coherence lemma R3(ii)、prediction bound R3(i) 与覆盖不等式；"greedy 增益沿轨迹不增"这条性质在最坏情况分析里是多余的，写证明时不必引入。

**推论 B（与已知两界的关系）**：U_K(η) = 1 − (1 − 1/k1)^K = 1 − q^K（R7 的显式实例上界），且

    U_K − V_{K−1} = q^{K−1} (η − 1) / (K η k1)  ≥ 0   (η ≥ 1，等号仅在 η = 1)   [VERIFIED-SYMBOLIC]

即在段 [1,2] 上 LP 闭式严格低于 R7 上界（η=1 除外）。整体上 L_K ≤ min_j V_j ≤ U_K 在 K=2..24 网格成立 [VERIFIED-LP]；L_K 一侧目前**没有**符号证明，标 [CONJECTURE]。

## 6. 已知局限 / 下一步

1. 只覆盖 η ≥ 1（LP 与论文的误差模型本身如此）。段 j=K−1 的左端点 η=1 是可去奇点，已单独处理。
2. Part E 默认 K ≤ 10，可用 `N1_KMAX` 调大（K ≤ 12 约 2 分钟）。真正的一般 K 结论来自 Part A–D，Part E 只是独立复核。
3. 剩下的主要缺口仍是 R6 的另一半：**存在实例达到 min_j V_j**（相等/上界方向）目前只在 K ≤ 4 的有限点 [VERIFIED-LP]。由推论 B，R7 的实例族只达到 U_K > V_{K−1}，所以现有实例族**不足以**证紧；需要新的实例构造（对应 primal 解 x_j 的 "consistency 步 j 次 + prediction 步 K−j 次" 结构）。这是明显的下一个任务。
4. 用 §5 的恒等式重写论文 Theorem 6 的证明，可以把现有的 L_K(η) = 1 − (1−1/(ηK))^K 下界替换成更强的 min_j V_j(η)。两者的大小关系在 K ≤ 24 网格上验证过 [VERIFIED-LP]，符号证明未做，标 [CONJECTURE]。
5. 空洞性检验（CLAUDE.md §空洞性检验）对 §0 的定理陈述：
   - 去掉 "reduced LP"：陈述变成关于 ρ_K 的，真值未知（依赖 R6 两个方向）——限定词必须保留，理由已写进 §0。
   - 去掉 "η ∈ [K−j, K−j+1]"：V_j 在段外不再是最优值（Part D 证明 argmin 会换成别的 j）——必须保留。
   - 去掉 "符号 K"改成"每个具体 K"：内容变弱（只剩 Part E 的 K ≤ 10）——保留，但按 §4 的口径加"模一次分支枚举"。
   - 去掉 "dual"（只说存在证书）：不变真值但丢失可发表的证明形式（§5 的非负组合恒等式），保留是为了指向 §5。
