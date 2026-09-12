# TASKS10.md — 同预算类的精确 hardness（计算路线，预算 8 小时，允许 FAILED）

## 目标定理（两边共用的陈述）
固定 K ≥ 2、η > 1。存在 n_0(K,η) 与实例族 (F_n, G_n)，n ≥ n_0，满足：
(a) F_n 单调 submodular，F_n(∅)=0；G_n 任意集合函数，G_n(∅)=0；单元素误差带 d/η_u ≤ d̃ ≤ η_o d 对所有 (S,e) 成立，η_uη_o = η（或 ≤ η 后校准到恰为 η）；
(b) G_n(S) 在所有 |S| ≤ K 且 |S∩O| ≤ 1 的集合上只依赖 |S|（O-无关）；
(c) 与 O 不交的 K-集的比值 F_n(T)/F_n(O) = ρ_K^{(n)}(η)，且 ρ_K^{(n)} → ρ_K(η) = min_j V_j(η)（n → ∞）。
由 (b)(c) 与现有 transcript 论证（thm:hardness 的 τ=1 版本，并集界 K⁵/(2n)）即得：
𝒜_lin（≤ nK 次、每次 |S| ≤ K 的查询）中任何确定性算法的最坏比 ≤ ρ_K^{(n)}(η)；与 greedy 达到 ρ_K 合并，
该类最优值随 n → ∞ 趋于 ρ_K(η)。这将闭合 cor:greedybudget 的夹逼区间。

## 已知事实（起点，不要重做）
- N2 实例族（n=2K，三类元素 C: j 个 / P: K−j 个 / O: K 个）是 greedy 在段 j 的精确最坏实例；轨迹量由 prop:rigidity 唯一确定：
  d_t = q^t/k_1 (t<j)，q^j/(Kη) (t≥j)；g_{t,i} = q^{min(t,j)}/K。results/N2_instances.md 有显式 f, f̃。
- N4（第二晚）：放开 F 后的 relaxed-F LP 在 n → ∞ 时极限 = min_j V_j（K ≤ 24 网格）；LP 顶点的 (F,G) 表存于 results/N4_*。
- F3（第四晚）：N4 的 G 在 x > T 处自动 O-无关；泄露集合限制在 |S∩O| ≥ 2 且 |S| ≤ T+K；合法性只在 48 组参数上穷举验证；
  切换指标 j、m* 的闭式无证明（J4 裁定为 candidate bound）；(5,4) 差异源于闭式多加了 F(x,K)≡1 的约束。
- 对 𝒜_lin 的 transcript 论证已在 app:greedybudget（τ=1 计数链 [VERIFIED-SYMBOLIC]），可直接复用。

## Q0 数据整理（1 小时）
从 results/N4_*、F3_* 提取每个 (K, j, η, n) 的 LP 顶点 (F(x,y), G(x,y))，K ∈ {3,4,5}，n ∈ {2K, 4K, 8K, 16K}，
η 取每段中点与一个端点附近。对每个表：确认合法性（单调、submodular、带）、O-无关区域、比值；记录 x 方向增益序列
Δ_xF(x,0) 与 Δ_xG(x,0) 随 x 的形状（预期：前 j 步几何衰减 q，之后平台，x > T 后另一模式）。

## Q1 闭式提取（2 小时）
对固定 (K, j, η) 观察 F(x,y)、G(x,y) 随 n 的规律，猜闭式（提示：F 只依赖 (x,y)；y ≤ 1 处 G 只依赖 x+y；
x 方向增益分三段：t<j 几何、j ≤ t<K 平台、t ≥ K 与 T 相关的尾巴；y 方向增益需使 O 元素在带内且 greedy 不选它）。
用有理数在 K=3,4、n=8K 上把猜的闭式与 LP 顶点逐格比对；允许闭式与 LP 顶点不同但目标值相同（顶点不唯一）。

## Q2 一般 K 符号验证（2.5 小时，核心）
对猜出的闭式（含符号 K、j、η、n、T）：
1. F 单调 submodular：Δ_xF、Δ_yF ≥ 0，且关于 x、y 非增（分段情形逐一）。
2. 单元素带：四类边的 ΔG/ΔF 落在 [1/η_u, η_o]，乘积 ≤ η；写出极值出现的边。
3. G 在 |S| ≤ K、|S∩O| ≤ 1 上只依赖 |S|。
4. 比值 F(K,0)/F(0,K) 的闭式及 n → ∞ 极限 = V_j；与相邻段的切换在整数 η。
照 T5/N2 的脚本风格：sympy 对符号参数验证，t 的有限分支枚举，K ≤ 8 有理数全格点复核。
任一条失败：记录失败的参数区间与具体不等式（这是 FAILED 时的交付物）。

## Q3 定理装配（1 小时）
若 Q2 全过：写 thm:linear-exact 的陈述与附录证明（构造 + 合法性引理 + 复用 app:greedybudget 的 transcript），
标 [VERIFIED-SYMBOLIC 合法性] + [HAND-PROOF-UNREVIEWED 装配]；cor:greedybudget 改写为夹逼闭合；台账新卡 T10c。
若失败：results/Q3_failure_point.md 写清卡点，正文不动。

## Q4 交叉核对（30 分钟，明早人类给你 GPT 的输出后做）
若 GPT 给出不同的闭式：用 Q2 的脚本验证 GPT 的构造；若两者目标值不同，以能通过全部合法性检查者为准。

规则：台账优先、状态标签、每任务 commit、卡 45 分钟跳过、REPORT 顶部 5 行、push、停止、不提问。
