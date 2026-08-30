# TASKS2.md — 第二晚任务（在第一晚 results/ 的基础上继续）

开始前：读 CLAUDE.md、RESEARCH_STATE.md、REPORT.md 的全部内容和 results/T2_summary.md、results/T3_K3_closed_form.md。
把第一晚的新结果先追加进 RESEARCH_STATE.md（R10：ρ_K = min_j V_j 闭式与 K≤4 证书；R11：T2 的三条结论；R12：T4 pair greedy = ρ_{K/2}；R13：T6 的 η^path 测量），每条带状态标签，然后再开始。
状态标签规则不变：没有 oracle 不准写 proved。

---

## N0 术语表与规则更新（20 分钟，最先做）
1. 新建 GLOSSARY.md，每个术语一行"本文含义"和"文献中的其他含义"，初版必须包含：approximation ratio 的方向（本文 α ≤ 1，F^ALG/F^OPT ≥ α；原稿 Section 1.1 的定义 OPT ≤ α·A 方向写反，需修）；consistency（LAA 含义：预测完美时的比值）与我们的 consistency lemma 撞名，后者在本仓库和论文中一律改称 coherence lemma；tight 的三个意思（对 greedy 紧、渐近紧、无算法更好）；any algorithm 的三个范围（无限算力 / poly-query / poly-time）及各自的证明方式；robust（Lemma 1 证明不存在，禁用）；η 与 Agarwal–Balkanski 的 η 撞名；information-theoretic 的复杂度含义；deterministic vs randomized 下界各自成立的条件。
2. 在 CLAUDE.md 末尾追加"空洞性检验"规则：定理陈述或贡献句里的每个限定词，去掉或换成对立面后陈述若不变则删除；变了则必须一句话说明变在哪。
3. 把"近似比定义方向写反"追加到 RESEARCH_STATE.md 的已知论文错误列表。
Deliverable：GLOSSARY.md、CLAUDE.md 和 RESEARCH_STATE.md 的 diff，commit。

## N1 一般 K 的对偶证书（3 小时，最高优先级）
目标：把 T3 找到的 K=2,3,4 对偶证书写成关于 (K, η, j) 的显式公式，并对一般 K 做符号验证。
1. 从 results/T3_duals.json 取 K=2,3,4 在每一段 [K−j, K−j+1] 上的非零乘子。列出每个乘子对应的约束（哪一步 t、哪个 o_i、哪类约束）。
2. 猜一般 K 的公式：乘子应当是 q=(K−1)η/((K−1)η+1) 的幂乘以有理系数，分段点在整数 η。用 K=5,6 的数值对偶解（`reduced(K, eta, return_sol=True)`）检验猜测。
3. 对猜出的公式做符号验证（sympy，K 为符号或 K=2..8 逐个符号）：(a) 乘子非负；(b) 加权相加后左边恰为 Σ_t d_t（对偶可行）；(c) 右边恰为 V_j(η)。三条都过才算证书成立。
4. 同时写出每段的显式 primal 解（d_t, g_{t,i} 的公式），符号验证它满足全部约束且目标 = V_j。
Deliverable：results/N1_dual_certificate.md（公式 + 验证脚本 results/N1_dual_certificate.py + 状态标签）。
若一般 K 公式猜不出：交 K=5,6 的数值证书、乘子支撑集随 K 的变化规律描述、以及你认为卡在哪里。

## N2 中间 j 的可实现实例（2 小时）
目标：对每个 j（0<j<K）构造显式 (f, f̃)，使 single-step greedy 恰好得到 V_j(η)。
1. 先看结构：j=0 是 modular 实例，j=K 是 U_K。猜测中间 j 是"前 j 步用 U 型结构、后 K−j 步用 modular 结构"或反之。用全格点 LP（code/worst_case_lp.py）在 K=3、η∈(1,2) 和 (2,3) 两段各取一个 η，把最优解的 f、f̃ 打印出来，看 (x,y) 计数结构。
2. 据此写出显式公式，在 K=3,4、每段各两个 η 上用全格点检查（monotone、submodular、误差恰为 η、greedy tie 向 b、比值 = V_j）。
3. 通过后对一般 K 做符号验证（照 results/T5_symbolic.py 的参数化方法）。
Deliverable：results/N2_instances.md + N2_check.py。通过则 R10 从"reduced LP 值"升级为"精确最坏值 [VERIFIED-SYMBOLIC]"。

## N3 R6 在 K=5 的验证（1 小时，可与 N1 并行）
目标：确认 reduced LP = 全格点 LP 在 K=5 仍成立。
n=10，2^10 变量 ×2。O 只取与 greedy 集合不相交的 K-子集（T4_symmetry_check 已说明 LP 值只依赖 O 的类型；若时间允许再验证一个相交类型）。η ∈ {1.5, 2, 3, 4.5}。与 reduced(5, η) 比较到 1e−7。
Deliverable：results/N3_K5_lattice_vs_reduced.csv。

## N4 Hardness 的解析化（3 小时）
目标：把 T2 步骤 5（relaxed-F）的 LP 最优 (F, G) 写成显式公式。
1. 读 results/T2_relaxF_solution_example.json。对 K∈{4,6,8}、η=2、真 balanced 定义，把最优 F(x,y) 和 G(x,y) 在 (x,y) 网格上打印成表，并画热图（figures/N4_*.png）。
2. 观察：F 在 y=K 处是否随 x 增长、增长的速率；Ĝ 在 |S|>K 处的饱和形状；balanced 区域外 G 的形状。写出猜测公式。
3. 把猜测的 (F, G) 代回全格点或网格 LP 做可行性检查（误差 ≤ η(1+δ)，δ 随 K 的规律；balanced 区域 G 只依赖 |S|；F 单调 submodular；比值 = 1−(1−1/(ηK))^K 或接近 U_K）。
4. 通过则符号验证；不通过则记录 LP 最优解中哪些约束是紧的（对偶乘子非零），作为下一轮线索。
Deliverable：results/N4_hardness_construction.md。这一项允许 [FAILED]，但必须交出紧约束清单。

## N5 有界查询版 hardness 定理草稿（1.5 小时，在 N4 之后）
目标：把 T2 结论 1 写成定理。
陈述：任何只查询大小 ≤ K 的集合、查询次数 Q = n^c 的确定性算法，在误差 η 下比值 ≤ 1−(1−1/(η̂K))^K，其中 η̂ = η/(1+δ)，1+δ = (a^τ K/(K−τ))²，τ = c+1（随机算法用 Yao）。
1. 写出 concentration 引理：O 均匀随机 K-子集，|S|≤K 的查询 S 满足 P(|S∩O| > τ) ≤ C(K,τ+1)·(K/n)^{τ+1}；对 Q 次查询取并集界，给出 n 的下界使失败概率 < 1/2。
2. 写出取值引理和合并步骤。
3. 用 sympy 验证 δ 的闭式随 K→∞ 趋于 0 且 1−(1−1/(η̂K))^K → 1−e^{−1/η}。
Deliverable：results/N5_bounded_query_hardness.tex，每步标状态。concentration 部分标 [HAND-PROOF-UNREVIEWED]，δ 闭式标 [VERIFIED-LP 有限实例]。

## N6 加性修正的误差模型（2 小时）
目标：回应 T6 的发现。
1. 理论：模型 d/η_u − ε ≤ d̃ ≤ η_o·d + ε。推导 greedy 的比值下界，形式应为 L_K(η) − c·K·ε·(常数)/OPT 之类。推导完用全格点 LP 验证：在 n=6、K=3 的 LP 里把误差约束改成这个形式，取 ε ∈ {0.01, 0.05}，检查 LP 最坏值 ≥ 推导的下界。
2. 实证：重跑 T6 的 pipeline，但 η^path 只在 |d| ≥ ε 且 |d̃| ≥ ε 的候选对上计算，ε 取 1/n_test 和 2/n_test 两档。报告 trimmed η^path 的中位数与 IQR，以及新下界是否不再 vacuous。
Deliverable：results/N6_additive_model.md、N6_eta_trimmed.csv、figures/N6_*.png。如实报告 trimmed 后 η 是否仍然很大。

## N7 报告（30 分钟，最后）
REPORT.md 顶部 summary ≤ 5 行；每个任务一段；git commit。

---

执行顺序：N0 → N1 → N3（并行）→ N2 → N4 → N5 → N6 → N7。
子代理用 Opus。任何任务卡住 45 分钟就记录并跳过。
