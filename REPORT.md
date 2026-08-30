# REPORT.md

## Summary（第二晚）

- 全部 PASS：N0 术语表/规则；N1 一般 K 对偶证书；N2 显式 V_j 实例；N3 K=5 验证；N4 hardness 解析化；N5 有界查询定理草稿；N6 加性误差模型。无任务级 FAIL。
- 头条：**ρ_K(η) = min_j V_j(η) 两个方向都到证书级**（N1 对偶 + N2 实例，均一般 K 符号验证），只剩 R6 有效不等式一步手证；N4 进一步表明 poly-query 技术的 n→∞ 极限恰是这同一闭式（修正第一晚"贴 U_K"的解读）。
- 两处对第一晚结论的修正已同步进文档：δ 闭式是 max 双支形式（N5，分歧点经独立 LP 复核）；relaxF 的 n=8K 数值未收敛（N4）。
- 最需人类判断：N2 实例的 f̃ 单调但不 submodular（R7 同病）——若模型要求 f̃ 也 submodular，全部上界实例失效，ρ_K 可能变大，这是建模决定；其次是 N6 的混合误差模型在量化尺度 ε 下对大多数真实数据行不可行，论文实证叙事需按 md 中的读法措辞。
- 复现：每个数字有一键脚本（results/N*_*.py，主会话全部复跑过）；第一晚 summary 存档在下方。

## Summary（第一晚，存档）

- 全部 PASS：T1 基线一致；T2 hardness；T3 闭式；T4 lookahead；T5 符号化；T6 实证；T7 定理草稿。无 FAIL（仅 T2 的 4 个超大 LP 超时跳过，已记录）。
- 最重要发现：R9 候选在真 balanced 定义下有结构性不可行证书（F 在 y=K 处平坦 vs Ĝ 递增，任意 n/δ/τ 都救不了）；放开 F 后 LP 值贴 U_K、K→∞ → 1−e^{−1/η}，且 y≤τ 下最小 δ 有精确闭式 1+δ=(a^τK/(K−τ))²。（注：两处解读已被第二晚 N4/N5 修正，见上。）
- 意外收获：T3 得到 K=3、K=4 分段闭式 + 一般 K 猜想 min_j V_j（符号对偶证书）；T4 发现 pair greedy 在 K=4 恰等于 ρ_2(η)；T5 把 R7 升级为一般 K [VERIFIED-SYMBOLIC]。
- 最需人类判断（当晚）：论文 hardness 一节怎么讲——第二晚 N4/N5 已给出答案的主体。

---

## 任务日志（倒序追加在此行之下）

### ——— 第二晚（TASKS2.md）———

### N6 加性修正的误差模型 — PASS（理论紧 + 实证半正半负，全部诚实落盘）
- 理论 [HAND-PROOF-UNREVIEWED + LP oracle]：模型 d/η_u − ε ≤ d̃ ≤ η_o·d + ε 下
  F^PG ≥ L_K(η)·(OPT − 2Kη_u·ε)；关键结构：ε 只与 η_u 相乘（回代发生在被选元素上）。
- LP 检验超预期：16/16 无违反且发现 **LP(ε) = ρ_K(η)·max(0, 1−2Kη_u·ε) 精确成立**
  （29 点残差 ≤2.8e-16，覆盖 K=2,3,4 与三种误差拆分）[CONJECTURE N6-C1]——
  即推导的 ε 部分是紧的，唯一松弛就是 ε=0 时已有的 ρ_K − L_K。ε* = OPT/(2Kη_u) 只依赖 η_u（已验证）。
- 实证 trimmed 重测（1260 行）：η^path 大幅下降（K=7 中位数 43→4.8、60→5.5、371→17.9）但
  下界在 K ≥ 5 仍实质 vacuous（数值 0.009-0.074 vs 实测 ratio 0.94-0.96；wine 转负）；
  **实质进步在 K=3 的 ε 优化认证下界**：0.286/0.439（breast_cancer/digits20，比 T6 好 10-31 倍），wine 例外。
- 重要负面结果：任务规定的 ε（1-2 个量化单位）下混合模型对 1110/1260 行不可行
  （存在 d>0 且 d̃<−ε 的对）；使可行的最小 ε 中位数 3-12.6 个单位。additive_bound 的正确读法
  已在 md 中写明。s10 的 10 行"违反"全部是前提失配（f(∅)≠0、oracle greedy 非 OPT），非定理反例。
- 复现：N6_additive_lp.py（11 秒）、N6_eta_trimmed.py（247 秒），主会话复跑均退出码 0；
  详见 results/N6_additive_model.md、N6_eta_trimmed.csv、figures/N6_*.png。
- 未做（[FAILED] 子项）：结合 N1 "mono 乘子恒为 0" 检查加性项能否绕开 monotonicity（时间用尽）。

### N5 有界查询版 hardness 定理草稿 — PASS（含对 T2 结论 1 的实质修正）
- results/N5_bounded_query_hardness.tex：concentration 引理（并集界 + 超几何，n ≥ 4K^{c+2}）、
  取值引理、确定性定理 + 随机化推论（只用平均论证，不冒称 Yao minimax），每步状态标签，
  第 6 节逐词空洞性检验 V1-V17（删 adaptive；poly-query/查询大小≤K/K≥2τ/(H)/η>1 为承重限定词；
  all-pairs 版标 open；全文不写 tight）。
- **修正 T2 结论 1**：δ 闭式完整形式是 1+δ = max{a^τK/(K−τ), a^{1−τ}}²，第二支来自 y 方向
  balanced 边，第一支占优 iff η ≥ 2−1/τ。第一晚测试点全在第一支区所以未暴露。
  Oracle：N5_delta_at_etahat.py 40 点 + 主会话在分歧点 (4,1.2,2) 用第一晚网格 LP 独立复核
  （LP=0.595568=第二支）。已同步修正 RESEARCH_STATE R11(a) 与 T2_summary。
- 定理需两处结构性修改：加假设 (H) η̂ ≥ 1（充分条件 K ≥ τ(1+2/ln η)）；η̂ 用 Φ(θ)=θ(1+δ(θ))
  的不动点定义（δ 对 η 不再单调）。sympy 15/15：δ→0（首阶 2τ(1−1/η)/K）、L_K(η̂) → 1−e^{−1/η} 等。
- 诚实边界：max 闭式一般 (K,τ,η) 仍 [CONJECTURE]，τ 只测 {1,2}（c ∈ {0,1}）；F 固定非最优
  （N4 的最优 (F,G) 代入会更强但只测 τ=1，列为下一步）；有限 K 下本定理弱于 greedy 侧曲线，
  内容是渐近的。主会话复跑两个脚本均退出码 0。

### N2 中间 j 的可实现实例 [VERIFIED-SYMBOLIC 一般 K，模分支枚举] — PASS（R10 升级为精确最坏值）
- 对每个 j（0 ≤ j ≤ K）构造显式 (f, f̃)：三类元素 C(j)+P(K−j)+O(K)，
  f = 1 − q^x(1−y/K) + zδ_jχ(y)，f̃ = W(0) − q^xW(y) + zδ̃χ(y)（W(0)=k1/(Kη_u)，W(y)=(K−y)η_o/K，
  δ_j=q^j/(Kη)）。机制：f̃ 把每步候选压成 O 真实增益/η_u，每步与 O 打平（tie 对抗承重）。
- j=0 退化为 R2 modular 实例；j=K 与 R7/U_K 逐点相同；中间 j 全新。取 j*(η) 即 ρ_K ≤ min_j V_j。
- 验证：480/480（主会话复跑退出码 0）：44 条一般 K 符号 + K=2..6 全格点 + K=2..8 精确 Fraction
  + R5 表 25 点重现 + 与 K=2 witness 逐元素一致 + strict tie 变体极限。
- **净结论：ρ_K(η) = min_j V_j(η) 两个方向都到证书级**（≤ 方向 N2 实例；≥ 方向 N1 对偶证书），
  仅剩 R6 有效不等式那一步 [HAND-PROOF-UNREVIEWED]。
- 最需人类判断（N2 caveat 3）：f̃ 单调但不 submodular（与 R7 同病）；若模型要求 f̃ 也 submodular，
  ρ_K 可能变大，现有全部上界实例失效，这是建模层面的决定。

### N4 Hardness 的解析化 [VERIFIED-SYMBOLIC 一般 (K,η) + VERIFIED-LP 42 组精确有理] — PASS
- **修正 T2 结论 3 的解读**：relaxF LP 值对 n 未收敛（T2 用的 n=8K 不够大）；n→∞ 极限
  逐点等于 y≤τ 定义下的值，而后者 = **ρ_K^LP = min_j V_j（R10 闭式），严格小于 U_K**。
  超额项衰减极快（η=2: K=4/8/16/32 为 3.2e-4/5.9e-7/4.4e-12/5.2e-22）。
  两条研究线合流：poly-query 技术的极限恰是 greedy 最坏比闭式。
- 拿到 LP 最优 (F,G) 完整显式公式：相位 1（x ≤ j）逐字是 R7/U_K 实例（a=q=1−1/(η(K−1)+1)）；
  相位 2（j < x ≤ T）是 coherence lemma R3(ii) 处处取等的常数增量尾巴，g_T=r_T 处闭合；
  D 与 value 的闭式见 results/N4_hardness_construction.md。
- T2 的 (8,3) 意外观察获解释：X=n−K 太小放不下相位 2 尾巴，长程约束族 L 消失，值掉回 V_j。
- 紧约束 100% 落入 8 个族（K=3..6 全覆盖）：A-D 精确复现 reduced LP 的四类约束；
  族 L（穿过非平衡行的长程链）是 reduced LP 没有的，正是有限 n 超额项来源。
- 诚实边界：j、m* 索引闭式 [CONJECTURE]（264 点）；η > K−1 时闭式仅可行非最优；
  (5,4) 一个点差 3.2e-7 未查明；显式构造只对 y≤τ 可行，真 balanced 定义仍需 N5 的
  concentration 论证；只测 τ=1、√η 拆分。
- 复现：N4_check.py（42 组精确有理可行性，主会话复跑退出码 0）、N4_symbolic.py（19/19，
  主会话复跑退出码 0）、N4_duals.py、N4_figures.py；图 figures/N4_*.png。

### N3 R6 在 K=5 的验证 [VERIFIED-LP] — PASS
- n=10 全格点 LP（2048 变量 × 38435 行）与 reduced(5,η) 在 η ∈ {1.5,2,3,4.5} 完全一致
  （≤1.7e-16），且都等于 R10 闭式 min_j V_j；四个值为干净有理数 6389/12005、1597/3645、
  269/845、21/95，段号 j=4,3,2,1 与分段吻合。R6 的"上界=reduced"由 K≤4 扩到 K≤5。
- 关键自检：同一构造器在 n=6,K=3 枚举全部 20 个 O 与 code/worst_case_lp.py 逐位一致（diff=0）。
- O 类型扫描（η=1.5,2 全部 6 类）：值随 |O∩greedy| 严格递增，不相交类型确为 argmin。
- 支持 R5 猜想：η=4.5 < K=5 时 21/95 < 1/4.5。
- 复现：python3 results/N3_K5_lattice.py（约 17 分钟；主会话核对 CSV 与日志后跳过整体复跑，
  理由：脚本自带 n=6 对已验证代码的逐位等价自检）。caveats：每类型只解一个 O（对称性依据）、
  只测 single-element √η 拆分、n=2K。

### N1 一般 K 的对偶证书 [VERIFIED-SYMBOLIC] — PASS（R10 下界方向升级为一般 K 定理级）
- 全部乘子写成 (K,η,j) 显式公式（记 M = Kη−(K−j)）：段 j≥1 上 y_sum(0)=−q^{j−1}M/(Kk1)、
  y_sum(t)=−q^{j−1−t}M/k1²（1≤t≤j−1）、y_sum(j)=(η−(K−j+1))/k1、y_cons(t≤j−1)=−q^{j−1−t}M/(Kk1)、
  y_cons(t≥j)=−(K−1−t)/(K(η−1))、y_pred(t≥j)=−(η−(K−t))/(K(η−1))、y_mono≡0；j=0 段沿用 T3。
- 验证：符号 (K,j,t,i) 全自由的三条恒等式（对偶可行等式、段内非正性的盒上正性证书、bᵀy=V_j）
  + K=2..10 共 54 段的独立暴力符号 LP 复核 + 与第一晚 58 个乘子逐个比对 0 不符。
  320/320 PASS，主会话复跑确认（60 秒，退出码 0）。唯一非 oracle 步骤是 t 分支的有限枚举（组合记账）。
- 重要副产品：(i) mono 乘子恒为 0，下界证明不需要 monotonicity（删 mono 行 LP 值不变，双验证）；
  (ii) U_K − V_{K−1} = q^{K−1}(η−1)/(Kηk1) > 0 [VERIFIED-SYMBOLIC]，R7 实例族达不到 V_{K−1}，
  证紧需要新实例（正是 N2）；(iii) V_i−V_{i+1} 恒等式给出整数分段点的直接证明。
- 诚实边界：reduced LP 值 = 真实 ρ_K 仍依赖 R6（[HAND-PROOF-UNREVIEWED] + K≤4 有限点）；
  L_K ≤ min_j V_j 仅数值支持 [CONJECTURE]；两个 scipy 对偶退化点已如实列出（非反例）。
- 复现：python3 results/N1_dual_certificate.py；详见 results/N1_dual_certificate.md/.json。

### N0 术语表与规则更新 — PASS
- GLOSSARY.md 建立（13 个词条，含任务规定的 8 个必含术语：近似比方向、consistency 撞名改称
  coherence lemma、tight 三义、any algorithm 三范围、robust 禁用、η 与 Agarwal-Balkanski 撞名、
  information-theoretic、deterministic vs randomized 下界）。
- CLAUDE.md 末尾新增"空洞性检验"规则；RESEARCH_STATE.md 追加 R10-R13（各带状态标签）、
  R7 升级注记、R3 更名、已知论文错误新增"Section 1.1 近似比定义方向写反"。
- results/T7_theorems.tex 的 Lemma B 同步改名 Coherence。代码内部约束标识 cons(t) 不动
  （属脚本内部命名，改动会破坏第一晚脚本的可复现性，保守处理并在 GLOSSARY 注明）。

### T7 定理陈述与证明草稿 — PASS
- `results/T7_theorems.tex`：Theorem A（trajectory-tight，L_K(η^path) 下界 + U_K 逐 K 紧，
  紧性现为一般 K [VERIFIED-SYMBOLIC]）、Lemma B（consistency，[HAND-PROOF-UNREVIEWED]）、
  Theorem C（K=2 精确，min{1/η, 3/(2(η+1))}）+ K=3,4 闭式 remark（[VERIFIED-SYMBOLIC]
  作为 reduced LP 值）、Theorem D（1/η ceiling + 穷举匹配，[HAND-PROOF-UNREVIEWED]）、
  Corollary E（weak submodularity，γ 版本，Das–Kempe [CITATION-NEEDS-VERIFICATION]）。
- 每条定理的状态标签与复现脚本以 LaTeX 注释内联；需人工检查的证明步骤已逐一标注。

### T5 显式实例 U_K 的符号验证 [VERIFIED-SYMBOLIC 一般 K] — PASS
- 105/105 检查通过（35 项一般 K 符号 + 70 项 K=2..8 具体符号），运行 4 秒，主会话复跑确认。
- 关键技巧：p=a^x、Q=a^dx 参数化把全部断言化为有理函数恒等式，无符号指数，
  故 R7 的 5 个 item（四类比值、单调+submodular、G(x,K)=1、tie 恒等式、η 与 U_K 重参数化）
  全部一般 K 符号验证。额外收获：all-pairs 误差 η_u=â、η_o=aK/(K−1) 也一般 K 符号可证。
- 剩两个平凡手工步骤（论文一句话）：greedy 轨迹 y=0 的一行归纳（K=2..8 已显式符号模拟）；
  参数化忠实性（a∈(0,1) 已符号证）。R7 升级为 [VERIFIED-SYMBOLIC]。
- 复现：`python3 results/T5_symbolic.py`（退出码 0 当且仅当全过），输出 T5_symbolic.txt/json。

### T4 R=2 lookahead 的精确最坏值 [VERIFIED-LP] — PASS
- K=4 pair greedy（all-pairs 误差，tie 对抗）的 LP 精确最坏值：η=1.5: 3/5，η=2: 1/2，
  η=3: 1/3，与 K=2 闭式 ρ_2(η)=min{1/η, 3/(2(η+1))} 吻合到 3.3e-16；n=8 与 n=9 完全一致。
  即 2-lookahead 把 K=4 曲线精确抬到 K'=K/2 的 single-step 曲线 [一般 K 为 CONJECTURE]。
- 公平对照：single-step 在 all-pairs 误差下与 R5 single-element 值一致（0.543576, 22/49, 13/40）。
  改善 +0.056/+0.051/+0.008，随 η 增大消失；η ≥ K/2 = 2 时 pair 已达 R2 普适上界 1/η。
- 论文 R-step 下界 1−(1−1/(2η))² 成立但不紧（差 0.03~0.06）。若 ρ_{K/R} 对应关系成立，
  由 R8 得常数 R 的 lookahead 不改变 1−e^{−1/η} 渐近极限，收益是有限 K 效应。
- 复现：`python3 results/T4_pair_greedy_lp.py full|n9|smoke`；对称性检查 T4_symmetry_check.py
  （70 个 O 的 LP 值只依赖类型，PASS）；数据 T4_pair_vs_single.csv/json。

### T2 Poly-query hardness 构造（R9）的数值验证 — PASS（结论对 R9 是"否定 + 修复路线"）
- 结论 1 [VERIFIED-LP 有限实例]：y ≤ τ 定义下候选可行，最小 δ 有精确闭式
  1+δ = (a^τK/(K−τ))²（全格点 4 组 (n,K) × 网格 K ≤ 32 全部吻合，δ = O(τ/K) → 0）。
- 结论 2 [VERIFIED-LP + 结构性证书]：真正的 balanced 定义 |y−K|S|/n| ≤ τ 下，
  R9 候选对任意 δ 不可行。证书：balanced 的 S ⊇ O 加 B 元素时 Δ_e F = 0（F 在 y=K 处
  x 方向平坦）但 Ĝ 严格递增。证书对一切 n 存在，换 τ/n/δ 都救不了，必须改 F。
  这否定了 R9 的未解决问题（对该候选 F）。
- 结论 3 [VERIFIED-LP 有限实例]：放开 F 后（步骤 5）两种定义都可行；技术能证到的
  hardness 值贴着 U_K(η)，K→∞ 收敛到 1 − e^{−1/η}（K ≤ 24，n ≤ 192）。有限 K 时
  该技术不能把 hardness 压到 L_K 以下。LP 最优 F 的形状（Ĝ 大集合处饱和）已导出为
  解析化候选（results/T2_relaxF_solution_example.json）。
- 方法学：约束对 B/O 内置换协变，LP 可对称化到 (x,y) 网格（全格点 crosscheck 全 PASS，
  含 relaxF 模式的独立全格点核对，6/6 精确相等）。
- 复现：results/T2_hardness_lp.py（全格点）、T2_hardness_grid.py（网格三模式）、
  T2_relaxF_lattice_check.py、T2_figures.py；数据 T2_table.csv、T2_grid_*.csv；
  图 figures/T2_delta_vs_K.png、T2_relaxF_ratio.png；详见 results/T2_summary.md。

### T6 真实 surrogate 的 η^path 测量 — PASS（实证测量）
- 做了什么：breast_cancer / wine / digits(前 20 特征)，f = 决策树 held-out accuracy，
  f̃ = 5-fold CV accuracy，greedy on f̃ 轨迹上测 η^path，30 次划分，K=1..7。
  openml airline satisfaction 因网络受限跳过（已记录）。
- 结果：η^path 很大且重尾（K=7 中位数 43 / 60 / 371），L_K(η^path) 下界 vacuous（0.023/0.017/0.003）；
  但实际 ratio(K=7) 中位数 0.963/0.941/0.957，630 行最差 0.718。诊断脚本确认 η 爆炸由
  accuracy 量化尺度的近零增益主导（argmax 对的 d̃ 或 d 中位数恰为 1 个量化单位）。
  方向一致性不成立：17%-32% 候选对 d 与 d̃ 反号；29%-53% 的对 d ≤ 0（f 不单调）。
- 对论文的含义：不能讲"实测 η 小"，应讲 raw multiplicative 误差对 ML surrogate 过于悲观，
  为 additive-multiplicative / trimmed 误差变体提供直接动机。
- 复现：`python3 results/T6_eta_path.py`（约 5 分钟）、`results/T6_argmax_diagnostic.py`。
  数据 `results/T6_eta_path.csv`，图 `figures/T6_*.png`，详见 `results/T6_summary.md`。

### T3 Reduced LP 对偶证书与 K=3(+K=4) 闭式 [VERIFIED-SYMBOLIC]（作为 reduced LP 值）— PASS
- 结果：定义 q=(K−1)η/((K−1)η+1)，V_j(η)=1−q^j(1−(K−j)/(Kη))，分段点为整数 η=2..K，
  则 reduced LP 值在段 [K−j,K−j+1] 上恰为 V_j。
  K=3：[1,2] (16η+3)/(3(2η+1)²)；[2,3] 7/(3(2η+1))；[3,∞) 1/η。
  K=4：[1,2] (135η²+36η+4)/(4(3η+1)³)；[2,3] (21η+2)/(2(3η+1)²)；[3,4] 13/(4(3η+1))；[4,∞) 1/η。
- 验证：K=2,3,4 全部 9 段构造显式 primal 解与对偶证书，sympy 精确算术 + Sturm 根计数
  整段验证（duality gap ≤1.1e−16）；K=2 恰好收回 R4；R5 全表 Fraction 精确重现；
  60 点拟合流程 held-out 残差 ≤3.3e−16。一般 K 猜想 min_j V_j 在 K=2..6×41 点 max 偏差 8.9e−16
  [CONJECTURE]。这把 "ρ_K=1/η iff η≥K"（R5 conjecture）在 K≤4 的 reduced-LP 层面变成定理。
- Caveat：闭式=ρ_K 还依赖 R6 的 reduced=全格点（K≤4 已验，一般 K 是 [HAND-PROOF-UNREVIEWED] 下界）。
- 复现：`python3 results/T3_duals.py`、`results/T3_K3_closed_form.py`；
  详见 `results/T3_K3_closed_form.md`、`results/T3_duals.json`、`figures/T3_K3_pieces.png`。

### T1 基线复现 [VERIFIED-LP] — PASS
- 做了什么：运行 `code/check_explicit_instance.py` 与 `code/worst_case_lp.py` 的 worst_case()
  （K=2 n=4、K=3 n=6，single-element 误差，η_u=η_o=√η，η ∈ {1,1.5,2,2.5,3,4}）。
- 结果：explicit instance 6 组参数 ALL PASS；12 个 LP 值与 RESEARCH_STATE.md R5 全部一致（<1e-7）。
- 复现：`python3 results/T1_baseline.py`，输出 `results/T1_baseline.txt`。
- 下一步：T2。
