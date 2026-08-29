# T2 — Poly-query hardness 构造（R9）的数值验证

复现：
- 全格点 LP（任务规定的主 oracle）：`python3 results/T2_hardness_lp.py full` → `results/T2_table.csv`
- 对称化 (x,y) 网格 LP（等价加速，见下）：`python3 results/T2_hardness_grid.py crosscheck|fixedF|relaxF`
  → `results/T2_grid_fixedF.csv`、`results/T2_grid_relaxF.csv`
- 图：`python3 results/T2_figures.py` → `figures/T2_delta_vs_K.png`、`figures/T2_relaxF_ratio.png`

对称化说明：所有约束类（balanced 等式、单元素误差带、单调性、submodularity、F(O)=1、
OPT 归一化）对 B 内置换与 O 内置换协变且线性，可行解经群平均后只依赖 (x,y)。
故全格点 LP 可行 iff 网格 LP 可行。crosscheck 模式在 (n,K) ∈ {(8,3),(10,3),(10,4),(12,4)}
上逐点核对（min δ 一致到 1e-4，'true' 不可行判定一致），全部 PASS [VERIFIED-LP]。

## 结论 1 [VERIFIED-LP 有限实例]：y ≤ τ 定义下可行，且最小 δ 有精确闭式

对全部测试点（全格点：(n,K) ∈ {(8,3),(10,3),(10,4),(12,4)}；网格：K ∈ {3,4,6,8,12,16,24,32}，
n = 4K；η ∈ {1.5,2,3}；τ ∈ {1,2}；误差拆分 η_u=η_o=√η 与 (η_u,η_o)=(η,1) 两种）：

    min feasible δ 满足 1 + δ = (a^τ · K/(K−τ))²，a = 1 − 1/(ηK)

- LP 最小 δ = 该公式 = 常数-常数约束对的解析下界 = R9 显式候选 G 的实际膨胀，三者在所有
  测试点重合（≤1e-6 相对差）。即显式候选在 y ≤ τ 域内是最优延拓，瓶颈在 balanced 区域内部。
- 与 n 无关（n=4K 与全格点小 n 一致），与误差拆分无关。
- K → ∞ 时 δ = 2τ(1−1/η)/K + O(1/K²) → 0，证实 R9 的"误差膨胀 1+O(τ/K)"（此渐近展开为
  [VERIFIED-SYMBOLIC 级别的初等展开，未单独存脚本]；闭式本身在上述有限点集为 [VERIFIED-LP]，
  一般 (K,τ,η) 为 [CONJECTURE]）。

## 结论 2 [VERIFIED-LP 有限实例 + 结构性证书]：真正的 balanced 定义下，R9 候选的 F 对任意 δ 不可行

balanced 取 |y − K|S|/n| ≤ τ 时，所有测试点 INFEASIBLE-ANY-DELTA。证书是两条约束的直接冲突：
存在 balanced 的 S ⊇ O 与 e ∈ B 使 S∪{e} 也 balanced（例如 K=3,τ=2,n=8 时 S=O 本身，
或一般地 |S| 接近 n 的集合），此时 Δ_e F = 0（R9 的 F 在 y=K 处对 x 方向平坦），有限误差
强制 Δ_e G = 0，但等式约束给 Δ_e G = a^{|S|}(1−a) > 0。由于 S = N∖{e} → N 这对集合对任意
n 都 balanced，该证书对一切 n 存在：**R9 候选无法通过换 τ、换 n、放大 δ 修复，必须改 F**。
这回答了 R9 的"未解决"问题：答案是否定的（对该 F）。

## 结论 3 [VERIFIED-LP 有限实例]：放开 F 后可行，hardness 值贴着 U_K，K→∞ 收敛到 1 − e^{−1/η}

步骤 5 的 LP：F(x,y) 为变量（单调、submodular、F(∅)=0、F(O)=1、F ≤ 1 于 |S| ≤ K），
G 在 balanced 区域强制只依赖 |S|（Ĝ_s 为自由变量，不再钉死为 1−a^s），误差带取 δ=0 的
精确 η，目标 min F(K-subset of B)。K ∈ {3,...,24}，n ∈ {4K, 8K}：

- 两种 balanced 定义下都可行（F 可在 y=K 处保留 x 方向正增益，绕开结论 2 的证书）。
- 数值（τ=1，n=8K，'true' 定义）：
  η=2: K=3: 0.5000, K=6: 0.4408(≈), K=12: 0.4157(≈), K=24: 0.40209
  对比 L_24=0.39666，U_24=0.40319，1−e^{−1/2}=0.39347。
  η=3, K=3 时恰为 1/η = 1/3（与 ρ_K = 1/η iff η ≥ K 的 conjecture 一致）。
- 解读：这套 information-theoretic 技术（balanced 对称化 + η 带）在有限 K 能证到的最好
  hardness 常数位于 [L_K, U_K] 之间、靠近 U_K，随 K→∞ 收敛到 1 − e^{−1/η}。
  它**不能**在固定 K 下把 hardness 压到 L_K(η) 以下；渐近意义上与算法侧 R1 的
  1 − e^{−1/η} 匹配，即 poly-query 最优比值的渐近答案是 1 − e^{−1/η}
  （此解读句为 [CONJECTURE]/框架性陈述；LP 数值本身 [VERIFIED-LP]）。
- caveat：目标取的是 y=0 的 K-集（B 内输出）；解上 y ≥ 1 的 balanced 输出值更高
  （CSV 列 best_balanced_output），完整的 hardness 陈述需对所有 balanced 输出取 max，
  即真实可证常数 ≥ ratio 列、≤ best_balanced_output 列。
- 网格 relaxF 的独立 oracle [VERIFIED-LP]：`python3 results/T2_relaxF_lattice_check.py`
  在 (8,3)、τ=1 全格点直接解 relaxF LP（F 不对称化，目标 = B 的 K-子集平均），
  与网格值在 6 个配置全部精确相等（<1e-6），确认对称化在 relaxF 模式正确。
  非对称 adversary 对单个固定输出（目标 min F(T)）只在 'true' 定义下略强
  （η=1.5: 0.5185 vs 0.5222；η=3: 0.3125 vs 0.32），量级 ≤ 0.008。
- 意外观察 [CONJECTURE]：(n,K)=(8,3)、τ=1、y ≤ τ 定义时 relaxF 值逐点恰等于
  ρ_3(η)（η=1.5: 9/16，η=2: 7/15，η=3: 1/3，与 R5 精确一致）；n 增大后值略高于 ρ_3。
  提示该技术在小 n 时的极限正是 predictive greedy 的最坏比。

## 泄露检查（任务步骤 4）

y ≤ τ 解在真 balanced 意义下泄露明显（同 |S| 的 balanced 集合 G 值 spread 0.1—0.35，
见 T2_table.csv leak 列），与结论 2 一致：y ≤ τ 的可行性不能推广。

## 任务步骤 3 的核对 [VERIFIED-LP]

所有配置：OPT 确为 O（全枚举 |S| ≤ K）；F(K-set ⊆ B)/F(O) = 1 − (1−1/(ηK))^K 精确成立
（T2_table.csv 的 ratio_B 与 LK 列逐行相等）。

## 对论文的建议（需人工判断）

hardness 一节可以写成：(i) 有限 K 的显式族给 U_K [R7，已有]；(ii) poly-query 场景下
本 LP 证据表明技术极限贴着 U_K 且渐近 1 − e^{−1/η}，作为 conjecture/数值支持陈述；
(iii) 严格的 poly-query 定理需要新的 F 构造（结论 3 的 LP 解本身给出候选：可从
T2_grid_relaxF 的对偶/解提取 F(x,y) 的形状做解析化）。
