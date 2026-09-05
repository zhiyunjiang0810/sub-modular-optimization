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

## R3 [HAND-PROOF-UNREVIEWED] Coherence lemma（原名 consistency lemma，因与 LAA 术语撞名改称，见 GLOSSARY.md）
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
η^sel 度量下 L_K 同样逐 K 紧：U_K 实例上 η^sel = η^path = â，realized ratio = L_K(â)（差 ≤ 1e−12）[VERIFIED-LP K=2..8×â∈{1.5,2}，results/F2_etasel_tight.py]

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
- Section 1.1 近似比定义方向写反（写成 OPT ≤ α·A）；应为 F^ALG ≥ α·F^OPT，α ∈ (0,1]（第二晚 N0 追加，见 GLOSSARY.md）。
- Section 3.3 λ 不等式方向写反；Theorem 10 K*=K 情形漏 1/λ；θ(f̃)/λ_o 项需重推。
- 负面结果的引用应为 Horel & Singer NeurIPS 2016（ε > n^{−1/2} 指数查询下界），不是 [5] Hassidim–Singer 2017（i.i.d. 噪声的正面结果）。
- R-step 部分将整体删除，只保留穷举达到 1/η 的一句 remark。

## R10 [VERIFIED-SYMBOLIC K=2,3,4（作为 reduced LP 值）；一般 K CONJECTURE] ρ_K^LP 闭式
k1 = (K−1)η + 1，q = (K−1)η/k1，V_j(η) = 1 − q^j(1 − (K−j)/(Kη))。
reduced LP 值在段 η ∈ [K−j, K−j+1] 上 = V_j（j ≥ 1），在 [K, ∞) 上 = V_0 = 1/η；分段点为整数 2..K。
K=2,3,4 全部 9 段有显式 primal 解 + 对偶证书（sympy 精确算术 + Sturm 根计数，duality gap ≤ 1.1e−16）。
K=3：(16η+3)/(3(2η+1)²)，7/(3(2η+1))，1/η。K=4：(135η²+36η+4)/(4(3η+1)³)，(21η+2)/(2(3η+1)²)，13/(4(3η+1))，1/η。
一般 K 猜想 ρ_K^LP = min_j V_j：205 点（K=2..6）偏差 ≤ 8.9e−16；两个一般 K 恒等式已符号证。
净状态：ρ_K ≥ 闭式 = 符号证书 + R6 手证；相等方向只在 R5/R6 有限点 [VERIFIED-LP]。
primal 最优解结构（段 j）：t < j 为 consistency 步（d_t = q^t/k1，G_t = q^t/K），t ≥ j 为 prediction 步
（d_t = q^j/(Kη)，G_t = q^j 冻结）。对偶支撑集：sum(0..j)、cons(0..K−2)、pred(j..K−1)。
详见 results/T3_K3_closed_form.md（含 j=0 段乘子的显式一般 K 公式）。

## R11 [VERIFIED-LP 有限实例] Poly-query hardness 候选（R9）的三条结论
(a) balanced 取 y ≤ τ：候选可行，最小误差膨胀有精确闭式
**1+δ = max{a^τK/(K−τ), a^{1−τ}}²**（N5 修正：第二支来自 y 方向 balanced 边；第一支占优 iff
η ≥ 2−1/τ，τ=1 时第二支恒平凡，第一晚测试点全在第一支区所以未暴露；40 个 LP 点 + 主会话
独立分歧点复核确认），a = 1−1/(ηK)（δ = 2τ(1−1/η)/K + O(1/K²) → 0 在第一支区；
一般 (K,τ,η) 为 CONJECTURE）。LP 最小 δ = 常数-常数约束解析下界 = 显式候选的实际膨胀，三者重合。
(b) balanced 取真集中带 |y − K|S|/n| ≤ τ：R9 候选对任意 δ 不可行，结构性证书 = balanced 的 S ⊇ O
加 B 元素时 Δ_e F = 0（F 在 y=K 处 x 方向平坦）但 Ĝ 严格递增；证书对一切 n 存在，必须改 F。
(c) 放开 F（保单调、submodular、F(O)=1、OPT 归一化，G 在 balanced 区域只依赖 |S|，δ=0）：
两种定义都可行；min F(K-set ⊆ B) 贴着 U_K(η)，K→∞ → 1−e^{−1/η}（K ≤ 24 网格 + (8,3) 全格点
双 oracle，对称化经 crosscheck 严格等价）。LP 最优解形状（Ĝ 大集合处饱和、F 线性化）已导出：
results/T2_relaxF_solution_example.json。意外观察 [CONJECTURE]：(8,3) τ=1 y≤τ 时 relaxF 值 = ρ_3(η) 逐点。
详见 results/T2_summary.md。

## R12 [VERIFIED-LP n=8,9] Pair greedy（R=2 lookahead）在 K=4 恰为 ρ_2(η)
all-pairs 误差、tie 对抗下，pair greedy 的精确最坏值在 η ∈ {1.5,2,3} 为 3/5, 1/2, 1/3 = ρ_2(η)
（吻合到 3.3e−16）。同误差模型 single-step = R5 值；改善 +0.056/+0.051/+0.008，η ≥ K/2 时 pair 达 1/η。
论文 R-step 下界 1−(1−1/(2η))² 成立但不紧。一般 K 的 ρ_{K/R} 对应关系 [CONJECTURE]；
若成立则由 R8 知常数 R lookahead 不改变 1−e^{−1/η} 极限。数据 results/T4_pair_vs_single.csv。

## R13 [实证测量] 真实 surrogate 的 η^path（feature selection，30 splits）
η^path 大且重尾（K=7 中位数：breast_cancer 43，wine 60，digits20 371），L_K(η^path) 下界 vacuous；
但 ratio(K=7) 中位数 0.963/0.941/0.957（630 行最差 0.718）。机制：η 爆炸由 accuracy 量化尺度的
近零增益主导（argmax 对的 d̃ 或 d 恰为 1 个量化单位）；方向一致性违反率 17%-32%，d ≤ 0 占 29%-53%。
含义：multiplicative 误差对 ML surrogate 过于悲观，动机 → additive-multiplicative / trimmed 变体（N6）。
数据 results/T6_eta_path.csv，诊断 results/T6_argmax_diagnostic.json。

## 更新（第二晚 N0）
- R7 已由 T5 升级为一般 K [VERIFIED-SYMBOLIC]（p=a^x、Q=a^dx 参数化；results/T5_symbolic.py，105/105）。
- R3 改称 coherence lemma（GLOSSARY.md）。

## 更新（第二晚 N1/N3/N4）
- R10 下界方向升级：一般 K 对偶证书 [VERIFIED-SYMBOLIC，模 t 分支有限枚举]，K=2..10 完全符号复核；
  mono 乘子恒为 0（下界不需 monotonicity）；U_K − V_{K−1} > 0 符号证明，R7 族不足以证紧
  （results/N1_dual_certificate.md）。
- R6 的"上界 = reduced LP"由 K ≤ 4 扩到 K ≤ 5 [VERIFIED-LP]（results/N3_K5_lattice_vs_reduced.csv）。
- **R11(c) 解读修正（N4）**：relaxF LP 的 n=8K 数值未收敛；n→∞ 极限 = min_j V_j（R10 闭式），
  严格小于 U_K。最优 (F,G) 有完整显式公式（相位 1 = R7 实例取 a=q；相位 2 = coherence 取等尾巴），
  一般 (K,η) 符号验证 + 42 组精确有理可行性（results/N4_hardness_construction.md）。

## R14 [实验之夜 E0-E6] 实验结果（全部无人工扰动 oracle；ratio 分母是 greedy-on-f，即 OPT 上估代理）
- E4 最坏实例数值实现：N2 的 V_j 实例（K∈{3,5,8}）与 U_K 实例经实验管线（CELF + 缓存）
  realized ratio 与理论差 ≤1.1e-16；V_j 实例上 η^sel = η、η^path = η 精确。
  worst case 在真实 greedy 代码上逐点发生（主图叉点）。results/E4_*。
- E1 feature selection：f = 决策树 held-out acc，f̃ = train 5-fold CV（结构性隔离测试集，
  四层断言+行为探针）；airline 全量 25,375 行。K=7 中位数：ratio 0.971（airline 0.999），
  η^sel 2.0，L_7(η^sel) 0.405 有信息量；η^path 10-52，其下界 0.02-0.10 几乎无信息量
  → 论文主用 η^sel。基线：airline 上每个 K 不劣于 SelectKBest/RFE/MI/ExtraTrees 最好者。
  发现：held-out acc 非 submodular，纯 CELF 轨迹偏离精确 argmax（真值 greedy 已改逐步精确）。
  results/E1_*。
- E2 influence maximization：一跳覆盖，f̃ = 边保留概率 p 的观测图；4 个替代图全量 240 轨迹
  （artist 50,515 节点全图）。K=30 中位数：ratio 0.963，η^sel 4.3。p-η 单调：p 0.8→0.3 时
  η^sel 升 3.2-87×，ratio 仅 0.99→0.88-0.96。viol=0 是结构性的（两覆盖函数）。results/E2_*。
- E3 summarization（模型边界外）：f = ROUGE-1 F 自实现，f̃ ∈ {coverage, diversity, facility}；
  BBC 三类各 100 篇（sport/tech 参考摘要 HF 回填，99/100 逐 token 验证，源 CSV 入库）。
  K=5 中位数：ratio 0.670，η^sel 7.2；ROUGE-1 F 实测 submodular 违反 2.14%、单调违反 7.12%。
  results/E3_*。
- 主图 figures/money_plot：真实任务散点悬在 ρ_K/L_K 上方，E4 构造实例贴线。

## 更新（第四晚 F0）
- R10 补：L_K(η) ≤ min_j V_j(η) 由 [CONJECTURE] 改为 [PROVED]。一行理由：reduced LP 的约束集
  包含 Theorem 6 分析所用 LP 的全部约束；约束更多可行域更小，最小值不减，故 reduced LP 值 ≥ L_K。

## 更新（第四晚 F1-F4）
- F1：E2 的 η^path 去截断全量重算（K=30 合并中位数 71.7→284；ratio/η^sel/viol 逐行不变）；
  ROUGE 自实现与 rouge-score 精确 0 差（90 篇负控制验证）；统一行新增 n/frac_steps_nonpos 列；
  breast_cancer 暴力 OPT 到 K=4：f(greedy^f)/OPT 中位 0.9823。
- F2：(5,4) 判定为真实差异（N4 闭式隐含 F(x,K)≡1，LP 不要求；加回后精确复原）[VERIFIED-LP 精确有理]；
  R6 四族有效不等式手证成文（results/F2_R6_validity.tex）；关键 remark：cons 约束用离轨 band，
  故精确值只对全局 η 成立、L_K 可对 η^sel 陈述。U_K 实例上 η^sel=η^path=â [VERIFIED-LP K=2..8]。
- F3：真带 τ=1 下 N4 构造 δ=0 可行 iff n > K(T+1)（12/12 [CONJECTURE]）；τ≥2 对任意 n/δ 不可行
  （2 约束 IIS，240/240）。意外正面：G 在 x>T 自动 O-无关 ⇒ 任意大小查询的 hardness 定理草稿，
  预算 Q=O(n²/((2+η)²K⁴))，指数 2 是该族内在上限（results/F3_hardness_full.tex）。
- **F4（重要建模结论）**：要求 f̃ 也 submodular 时最坏值在 η < K−1 区严格变大
  （K=3,η=1.5: 9/16→19/33；K=4,η=2: 22/49→23/50）[VERIFIED-LP + 实例验证器确认可达]；
  新闭式猜想 ρ_K^sub = min_m W_m，W_m=(K−m r^m)/(K(1+(η−1)r^m))，r=1−1/K，76/76 点吻合
  [CONJECTURE]；渐近极限比 1−e^{−1/η} 高约 10%；U_K 在新模型失效为上界。
  若论文采用 submodular surrogate 模型，R7/U_K 陈述需重写（results/F4_submodular_ftilde.md）。

## 更新（第五晚 G0：建模决定定案，2026-09-05）
- **D1（主模型不限制 f̃）**：主模型对 surrogate f̃ 不作 submodular 假设；"f̃ 也 submodular" 的变体只以
  一条 Remark 出现（正文措辞：if the surrogate is itself submodular, the exact worst case strictly
  improves for η < K−1，引 F4 的 LP 验证点 K=3, η=1.5: 9/16 → 19/33，general characterization
  left open）。W_m 闭式猜想不进正文（留在 results/F4_submodular_ftilde.md）。"more robust" 措辞禁用
  （见 GLOSSARY robust 行）。理由：F4 结论目前仅 [VERIFIED-LP 有限点] + [CONJECTURE]，不足以支撑
  重写 R7/U_K 全线陈述。
- **D2（Theorem 6 降为 Proposition）**：原 Theorem 6（L_K 保证）改为 Proposition，正文措辞固定为
  "restated in the prediction-error model of Section 2; essentially due to Goundan & Schulz (2007,
  Theorem 1)"；证明移入附录并注明 included for completeness。全文不得对该结果写 "we prove/show"。
  对应 label 由 thm:guarantee 改为 prop:guarantee（results.tex、notation_table.tex、
  appendix_proofs.tex、captions.tex、EXP_table 已同步）。
