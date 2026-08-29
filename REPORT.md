# REPORT.md

## Summary（进行中，完成后更新为 ≤5 行终版）

- 会话开始：2026-08-29（环境：Claude Code 远程容器，4 核，scipy/sympy/sklearn 已装）
- 注：原计划新建仓库存放本目录，但 GitHub 集成无创建仓库权限（403），保守选择放入
  `experiment` 仓库 `claude/understand-requirements-oz3ayh` 分支的 `overnight/` 子目录。
  整个目录自包含，之后可原样迁移到新仓库。

---

## 任务日志（倒序追加在此行之下）

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
