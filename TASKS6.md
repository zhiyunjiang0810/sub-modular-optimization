# TASKS6.md — 第六晚：修错误 + 加硬核（预算 12 小时；若超时，先砍 H-C，再砍 H-E）

顺序硬性：先 TASKS_J2.md 的 K1–K7（K0 已由 H3 完成并通过），再本文件的 H 系列，顺序 K9 → H-J3 → H-F → H-B → H-E → H-C。
硬核项不得挤占修错误的时间；H 系列每项允许 FAILED，但必须交出"卡在哪里"的记录。
台账规则：THEOREM_LEDGER.md 是定理陈述的唯一来源，任何陈述改动先改台账卡，再改 .tex。

---

## 第一段：修错误（约 6 小时）
执行 TASKS_J2.md 的 K1–K7。补充要求：
- 新 η^sel 定义落实后，在 U_K 实例上数值确认 η^sel=η^tr=â 不变，记入 REPORT。
- hardness 替换后加 remark：τ=1 时 H_{K,1}=U_K，故 L_K ≤ ρ_K ≤ U_K=H_{K,1}；F3 版放附录补充定理。
- 主图拆两幅（η^sel 轴：L_K + 真实任务；全局 η 轴：ρ_K + E4）。
- 不改 abstract/intro；在 REPORT 单列"contribution (iv) 需改写的要点"。

## 第二段：硬核内容（约 4.5 小时）

### H-J3 主定理的结构化证明（1.5 小时，优先于 H-B）
输入：results/J3_proof_structure.md 与 J3_structure_oracles.py。
1. 闸门：复跑 J3 脚本（40 个最优面、2,480 次坐标极值、恒等式）；自写 sympy 验证 §1 的不等式
   d − g/η ≥ (1−1/η)(g−h) 与 coherence (ii) 等价、§3 的相邻差公式与两条 7/15 轨迹。
2. 新 Lemma（放 lem:coherence 之后）：sharp form d − g/η ≥ (1−1/η)(g−h) ≥ 0，附一句解释
   （d=g/η 时 h=g）。
3. 新 Proposition（thm:exact 之后，"Structure of worst-case runs"）：非断点 η、精确达到时
   d_t 与 g_{t,i} 的唯一序列（两阶段公式）。证明：互补松弛 + §2.1 的递推归纳，逐步写出，
   标 [HAND-PROOF-UNREVIEWED]；范围句照 J3 §2.2（只约束轨迹量，不确定整个函数；最坏 run 与 O 不交）。
4. Remarks：断点 = active-constraint switch（含 K=3, η=2 两条轨迹）；精确取等强迫每步与最优元素
   tie（分解到 P=Q）；近等号 slack ≤ ε/λ_r（不升级为稳定性定理）。
5. 按 J3 §5 顺序重组 thm:exact 的正文证明概要与附录证明的开头；配平细节留附录。
6. 台账：T5 加 sharp form；新增 T6b（刚性命题）；T6 的"禁止声称"加"唯一性不延伸到断点、不约束未选候选"。
Deliverable：编译通过的 .tex 改动 + results/H_J3_integration.md。

### H-F 有限 K 下 partial enumeration 能否突破 ρ_K（1 小时，Tianming 问题 B 的探针）
背景：NW 1978 第 7 节证明 "枚举所有 R-子集，各接 greedy，取最好" 在 η=1 时严格改善有限 K 的常数。
预测版算法 PE_R：对每个 R-子集 S 以 S 为起点跑 predictive greedy 至 K 个元素得 T_S，输出 argmax_S f̃(T_S)。
1. 用全格点 LP 求 PE_1 在 K=3（n=6,7）、η∈{1.5, 2, 2.5} 的精确最坏值：变量 f、f̃；约束为模型约束加
   "每个起点 S 的 greedy 轨迹按 f̃ 选择"与"最终按 f̃ 选 T_S"；目标 min f(输出)。
   注意枚举起点数为 n，需对每个起点固定其轨迹（枚举轨迹组合或用对称性缩减），先做 n=6。
2. 与 ρ_3(η) 比较：若 PE_1 > ρ_3，记录差值并猜公式（对照 NW 7.1 的形式 1−((K−R)/K)β(K−R) 与 η 因子）；
   若 PE_1 ≤ ρ_3，说明最终按 f̃ 选取的 η 损失抵消了枚举收益，作为 greedy 有限 K 最优性的证据。
3. 写 results/H_F_partial_enumeration.md：结论、LP 数值、状态标签；供 open problem 段与 Tianming 讨论用。
Deliverable：上述 md + 脚本；台账 T11 加一条"PE_R 在 K=3 的数值结论"。

### H-B 渐近展开的精确常数（1.5 小时）
目标：ρ_K(η)=1−e^{−1/η}+c(η)/K+O(1/K²) 的 c(η) 闭式，并证 ρ_K 关于 K 单调（若真）。
1. 数值：用 reduced_lp.py 在 K∈{50,100,200,400}、η∈{1.25,1.5,2,2.5,3,4,6} 上算 (ρ_K−(1−e^{−1/η}))·K，
   Richardson 外推得 c(η) 到 6 位；同时算 ρ_K−ρ_{K+1} 的符号（单调性证据）。
2. 推导：活跃段 j=K−⌈η⌉ 附近（注意 η 为整数时两段相邻取等），对 V_j(η) 做 K→∞ 展开到 1/K 项，
   得 c(η) 候选；用 sympy series 验证；与数值对到 1e−6。若 c(η) 随 η 的整数部分分段，如实写分段式。
3. 单调性：若数值全为正差，尝试证 V_{j(K)}(η) 关于 K 单调（对偶或直接展开）；证不出标 [CONJECTURE] 并给数值范围。
Deliverable：results/H_B_asymptotic.md + 脚本；台账 T9 更新。

### H-E 无限算力下对所有 n 的精确最优比（1 小时）
目标：n<2K 时 1/η 天花板的精确形式。
1. 对称化 LP：f̃ 对称，算法输出 S 固定，对手选 O 与 f；n ∈ {K+1,…,2K−1}，K∈{2,3,4}，η∈{1.5,2,3}，
   用全格点 LP 求对手最优值（对输出集合的类型枚举）。
2. 猜闭式（预期形如 max over 重叠数 m=|S∩O| ≥ 2K−n 的 (…)/η 组合），符号验证，写成 T8 的推广。
Deliverable：results/H_E_ceiling_small_n.md；台账 T8 更新。

### H-C submodular surrogate 的刻画（1 小时，允许 FAILED）
目标：ρ_K^sub=min_m W_m 的证书。
1. 在全格点 LP 加 f̃ submodular 约束，K=2,3,4，取对偶乘子，找 W_m 的对偶模式（照 N1 流程）。
2. 若模式清楚：符号验证 K=2,3；并尝试造实例（照 N2 流程，注意 U_K 族失效，实例的 f̃ 必须 submodular）。
3. 否则：记录对偶支撑集与卡点。
Deliverable：results/H_C_submodular_surrogate.md；台账 T7 更新（升级或维持 OPEN）。

## 第二段补充：J4 指出的范围与措辞修正（K9，45 分钟，放在 H-J3 之前）
输入 results/J4_Tianming_requirements_audit.md。逐条落实：
1. F3 从 theorem 环境降为附录里的"构造方向与有限证据"段落，明确：一般参数合法性只有有限穷举、
   预算界 Q ≤ n²/(2K²(t*+K)²)、"指数 2 内在上限"只覆盖已检查参数；删除 n^{2−o(1)} 表述或加 K、η 增长限制。
2. thm:hardness 与 rem：把 "non-trivial" 改为 asymptotically matching，或陈述为 min{H_{K,τ}, 1/η}；
   随机版极限量词写清（ε_n→0 需 n ≥ 4K^{c+3} 之类）；查询大小限制明确为模型条件而非多项式时间。
3. thm:ceiling 相关文字：η ≥ K 时写 "greedy attains the unbounded-query deterministic optimum 1/η"，
   删除"与任何算法相同"式表述；随机上界 (1−K/n)/η+K/n 注明是上界不是精确最优。
4. 新 remark（thm:exact 后或 thm:ceiling 后）：1 ≤ η < K 时穷举的最坏保证 1/η 严格优于 greedy 的 ρ_K，
   差 ≥ V_0−V_1 = (K−η)/(Kηk_1)；表格 K=3 四个 η。措辞：比较最坏保证，不表示逐实例更好。
5. "原界对有限 K 严格不紧"处加 η > 1；notation_table 的 τ 改 ⌈c⌉+1；related.tex 的 "unimprovable"
   限定为渐近常数，"matching obstruction" 改 asymptotically matching。
6. 台账 T8、T10、T11、T12 的"禁止声称"同步加上以上各条。

## 第三段：台账与收尾（30 分钟）
1. 按当晚实际落实的陈述逐卡更新 THEOREM_LEDGER.md（T3、T4、T6、T7、T8、T9、T10、T11、T15），
   每卡的状态标签与 results/ 脚本一一对应；新增的定理加新卡。
2. 全文编译 0 错误，数字审计 0 违规；REPORT 顶部 5 行 summary（含"台账已同步"字样）；push。
