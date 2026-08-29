# RESEARCH_STATE.md — 已确立的结果（2026-08-30）

问题：max{f(S): |S| ≤ K}，f 单调 submodular 且不可访问，只能查询预测器 f̃。误差定义见 CLAUDE.md。

## R1 [论文 Theorem 6] 下界 L_K(η)
single-step predictive greedy 满足 F^PG/F^OPT ≥ 1 − (1 − 1/(ηK))^K ≥ 1 − e^{−1/η}。
证明只使用 greedy 轨迹状态 S^t 上的单元素增益，所以对 η^path 同样成立（严格更强的陈述）。
本质上是 (1/η)-approximate greedy 的经典分析（Goundan–Schulz 2007 [CITATION-NEEDS-VERIFICATION]）。

## R2 [HAND-PROOF-UNREVIEWED，证明简单] 任何算法 ≤ 1/η
f̃(S) = c|S| 对称；算法输出 S；取 O ⊆ N∖S（n ≥ 2K），f(S) = c(|S∩B|/η_o + η_u|S∩O|)，B = N∖O。
误差恰为 (η_u, η_o)（all-pairs 定义），比值 1/η。随机算法：O 均匀随机，≤ (1−K/n)/η + K/n。
对 f̃ 穷举 K-子集达到 1/η：f(S̃) ≥ f̃(S̃)/η_o ≥ f̃(O)/η_o ≥ f(O)/η。

## R3 [HAND-PROOF-UNREVIEWED] Consistency lemma
f 单调，S ⊆ N，e,e' ∉ S，d̃_e(S) ≥ d̃_{e'}(S)。则
(i) d_e(S∪{e'}) ≥ d_{e'}(S∪{e})/η；
(ii) (1 − 1/η)·d_{e'}(S∪{e}) ≥ d_{e'}(S) − d_e(S)。
证明：f̃(S∪{e,e'}) − f̃(S) 两种展开给 d̃_e(S∪{e'}) ≥ d̃_{e'}(S∪{e})，套误差界得 (i)；对 f 用同一恒等式得 (ii)。只用单元素误差界。

## R4 [下界 HAND-PROOF-UNREVIEWED；上界 VERIFIED-LP] K=2 精确值
ρ_2(η) = min{1/η, 3/(2(η+1))}。下界证明用 R3(ii) 取 S=∅、e=b₁、e'=o₁（p₁ ≥ 1/2）。
上界 witness 在 `results/k2_witness_instances.json`（来自全格点 LP）。

## R5 [VERIFIED-LP] 精确最坏值（single-element 误差，η_u=η_o=√η，n=2K；n=2K+1 及 all-pairs 数值相同）
| η | 1 | 1.5 | 2 | 2.5 | 3 | 4 |
|---|---|---|---|---|---|---|
| K=2 | 3/4 | 3/5 | 1/2 | 2/5 | 1/3 | 1/4 |
| K=3 | 19/27 | 9/16 | 7/15 | 7/18 | 1/3 | 1/4 |
| K=4 | 175/256 | 0.543576 | 22/49 | 0.377163 | 13/40 | 1/4 |
另：K=3 η=1.1: 0.670573, η=1.25: 0.625850, η=2.8: 0.353535, η=2.95: 0.338164, η=3.05: 1/3.05。
K=4 η=3.8: 0.262097, η=4.2: 1/4.2。
[CONJECTURE] ρ_K(η) = 1/η 当且仅当 η ≥ K。
代码：`code/worst_case_lp.py`（全格点，2^n 变量 ×2，枚举 O）。

## R6 [VERIFIED-LP] O(K²) reduced LP 与全格点 LP 在全部 19 个测试点一致
变量 d_t, g_{t,i}；约束：Σ_i g_{t,i} ≥ r_t；d_t ≥ g_{t,i}/η；g_{t+1,i} ≤ g_{t,i}；(1−1/η)g_{t+1,i} ≥ g_{t,i} − d_t。
每条约束都是有效不等式，所以 reduced LP 的值对任意 K 都是可证的下界 [HAND-PROOF-UNREVIEWED：b_t ∈ O 的情形令对应 g_{t+1,i}=0 后约束仍成立]。
上界 = reduced LP 只在 K ≤ 4 验证过（依赖全格点 LP 可实现性）。
代码：`code/reduced_lp.py`。K=200 一个 LP 约 80 秒。

## R7 [VERIFIED-LP 全格点 K ≤ 6] 显式实例族 U_K
基础集 B ∪ O，|B|=|O|=K，x=|S∩B|，y=|S∩O|，â > 1，a = 1 − 1/(âK)：
- f = F(x,y) = 1 − a^x(1 − y/K)
- f̃ = G(x,0) = 1 − a^x；G(x,y) = 1 − a^x + a^x[(1−a) + (y−1)a/(K−1)]，1 ≤ y ≤ K
性质（全部数值验证）：F 单调 submodular；误差有限；η_u = â，η_o = aK/(K−1)，η = (âK−1)/(K−1)（all-pairs）；
greedy（tie 向 B）选满 B，比值 1 − a^K；**path error = â**。
四类比值（预测/真实）：Δ_x(·,0): 1；Δ_x(·,y≥1): aK/(K−1)；Δ_y(·,0): 1/â；Δ_y(·,y≥1): aK/(K−1)。
推论：
- 以 η^path 度量，L_K 对每个 K 精确紧（实例 path error = â，值 = L_K(â)）。
- 以全局 η 度量，ρ_K(η) ≤ U_K(η) := 1 − (1 − 1/(η(K−1)+1))^K。
- L_K ≤ ρ_K ≤ U_K，两侧 → 1 − e^{−1/η}。数值：U_K − ρ_K ≈ O(1/K²)。
代码：`code/check_explicit_instance.py`。
已知缺陷：这个实例对 pair 查询泄露 O（G(0,2) ≠ G(2,0)），所以它**不是** poly-query hardness 的实例。

## R8 [VERIFIED-LP，Richardson 外推 5 位小数] lim_{K→∞} ρ_K(η) = 1 − e^{−1/η}
η=1.5,2,3 均吻合。也可由 R1 + R7 解析推出。

## R9 [启发式，未验证] Poly-query hardness 的候选构造（今晚 T2 的对象）
隐藏 O，|O|=K，n ≫ K，x=|S∖O|，y=|S∩O|。对 poly 次查询，随机 O 使所有查询 balanced（y ≤ τ，τ ~ √(K log Q)），
所以 f̃ 在 balanced 区域必须只依赖 |S|：G = Ĝ(|S|)。约束链
F(K,0) ≥ Ĝ(K)/η_o，F(0,K) ≤ F(K,K) ≤ F(K,0) + η_u·K·ΔĜ(K)
给出 balanced 输出的比值 ≥ Ĝ(K)/(Ĝ(K) + ηKΔĜ(K))；取 Ĝ(s) = 1 − (1−1/(cK))^s，另一条约束逼出 c ≥ η，c = η 时恰为 1 − e^{−1/η}。
候选：a = 1 − 1/(ηK)，F(x,y) = (1/η_o)[1 − a^x(1 − y/K)]，
G(x,y) = 1 − a^{x+y}（y ≤ τ），G(x,y) = 1 − a^{x+τ}(K−y)/(K−τ)（y ≥ τ）。
小集合上 band 检查通过（误差膨胀 1+O(τ/K)）。**未解决**：真正的 balanced 区域是 |y − K|S|/n| ≤ τ（不是 y ≤ τ），大集合上 G 的定义是否能同时不泄露 O 且留在 η 带内。

## 已知的论文错误（改稿时修）
- Section 3.3 λ 不等式方向写反；Theorem 10 K*=K 情形漏 1/λ；θ(f̃)/λ_o 项需重推。
- 负面结果的引用应为 Horel & Singer NeurIPS 2016（ε > n^{−1/2} 指数查询下界），不是 [5] Hassidim–Singer 2017（i.i.d. 噪声的正面结果）。
- R-step 部分将整体删除，只保留穷举达到 1/η 的一句 remark。
