# TASKS.md — 今晚任务（按顺序执行，预算总计约 10 小时）

开始前：`git init`（若未初始化），创建 `results/ figures/ REPORT.md`，读完 `CLAUDE.md` 和 `RESEARCH_STATE.md`。每个任务的 deliverable 必须落盘，状态标签必须写进 REPORT.md。

---

## T1 基线复现（15 分钟）
运行 `code/check_explicit_instance.py`（应 ALL PASS）和 `code/worst_case_lp.py` 的 K=2,3 部分，核对 RESEARCH_STATE.md R5 的数字。
Deliverable：`results/T1_baseline.txt`。任何不一致立即停下，写进 REPORT.md 顶部，然后继续其他任务但标注。

## T2 Poly-query hardness 构造的数值验证（2.5 小时，最高价值）
对象：RESEARCH_STATE.md R9。目标是回答"R9 候选的 G 能否延拓到整个格点，使得 (a) 在 balanced 区域只依赖 |S|，(b) 全局落在 η(1+δ) 带内"，并观察 δ 随 K 的变化。

步骤：
1. 写 `results/T2_hardness_lp.py`：基础集 N = B ∪ O，|O| = K，|B| = n − K，n ≤ 12。F 固定为 R9 的形式（参数 η，η_u = η_o = √η 或其他拆分，两种都试）。
   G 的变量：所有 S 的 G(S)。约束：
   - balanced 区域 S（先用 y ≤ τ，τ ∈ {1,2}）：G(S) = Ĝ(|S|) = 1 − a^{|S|}（等式，用 a 对应 c = η）。
   - 所有 S、e ∉ S：Δ_e G(S) ∈ [Δ_e F(S)/η_u', η_o'·Δ_e F(S)]，η' = η(1+δ)；Δ_e F = 0 时强制 Δ_e G = 0。
   - 先只做 single-element 约束；通过后加 all-pairs。
   用二分求最小可行 δ。对 (n,K) ∈ {(8,3),(10,3),(10,4),(12,4)}、η ∈ {1.5,2,3}、τ ∈ {1,2} 各跑一次。
2. 换成真正的 balanced 定义 |y − K·|S|/n| ≤ τ 重跑一遍。这是关键：R9 的候选只在 y ≤ τ 检查过。
3. 检查 F(K-set ⊆ B)/F(O) 是否等于 1 − (1 − 1/(ηK))^K，以及 OPT 是否确实是 O。
4. 泄露检查：对可行解 G，验证所有 balanced 的 pair 查询值只依赖 |S|（即不像 R7 实例那样 G(0,2) ≠ G(2,0)）。
5. 若步骤 2 在某些 (n,K,τ) 不可行：把 F 也放开成变量（保留 submodular、单调、F(O)=1、balanced 区域 G 对称），目标 min F(B 的 K-子集)，看得到的比值是否仍接近 1 − e^{−1/η}。这一步的输出是"这个技术能证到的最好常数"的数值估计。

Deliverable：`results/T2_table.csv`（n,K,τ,η,balanced 定义,最小 δ,比值）、`results/T2_summary.md`。
判据：若最小 δ 随 K 增大而减小且比值趋于 1 − e^{−1/η}，标 `[VERIFIED-LP 有限实例]`，并明确写"这只是有限实例证据，不是对所有 n 的证明"。若不可行，写清是哪类约束冲突（列出 LP 的 infeasible 子集或对偶证书）。

## T3 Reduced LP 的对偶证书与 K=3 闭式（2 小时）
1. 用 `code/reduced_lp.py` 的 `reduced(K, eta, return_sol=True)` 取对偶乘子（`res.ineqlin.marginals`）。对 K=2,3,4、η ∈ {1.25,1.5,2,2.5} 输出非零乘子及其对应约束，存 `results/T3_duals.json`。
2. 对 K=2 验证：对偶乘子组合出的不等式就是 R4 的手证（这是校验 pipeline 的 sanity check）。
3. K=3：在 η ∈ [1,3] 上取 60 个点算精确值；按 1/η 的分段猜测（R5 conjecture 说 η ≥ 3 时为 1/η），在 η < 3 区间用 sympy 拟合低次有理函数 P(η)/Q(η)（deg ≤ 3），分段可能不止一段（观察对偶支撑集的变化点）。拟合用 40 个点，剩余 20 个点作检验，要求残差 < 1e−9。
4. 若得到闭式：对每段用 fractions 做精确有理验证（把 η 取有理数，LP 用 fractions 重解或至少验证拟合值满足所有约束且等于 HiGHS 的值到 1e−9）。
5. 尝试从 K=2,3 的对偶结构猜 K=4 的闭式，用 R5 的 K=4 数据检验。

Deliverable：`results/T3_K3_closed_form.md`（含公式、分段点、验证残差、状态标签）。得不到闭式也要交对偶支撑集的模式描述。

## T4 R=2 lookahead 的精确最坏值（1.5 小时）
问题：2-step greedy（每步选预测增益最大的 pair）在全局 η 下的精确最坏值是否好于 single-step，极限是否仍是 1 − e^{−1/η}。
1. 复制 `code/worst_case_lp.py` 为 `results/T4_pair_greedy_lp.py`，把 greedy 路径约束改为：状态 S_t = {0,…,2t−1}，选中的 pair I_t = {2t, 2t+1} 满足 d̃_{I_t}(S_t) ≥ d̃_I(S_t) 对所有 I ⊆ N∖S_t、|I| ≤ min(2, K−|S_t|)。误差约束用 all-pairs 版本（pair greedy 查询的是 pair 增益）。
2. K=4，n=8，η ∈ {1.5,2,3}，枚举 O。与 R5 的 K=4 single-step 值和论文 R-step 下界 1 − (1 − 1/(2η))^2 对比。
3. 若时间允许，K=4 n=9。

Deliverable：`results/T4_pair_vs_single.csv` 和一段结论：lookahead 在有限 K 是否有改善、改善量级。

## T5 显式实例 U_K 的符号验证（1 小时）
用 sympy，符号变量 a ∈ (0,1)、K ≥ 2 整数（或对 K 取具体值 2..8 再做一般 K 的手工推导），验证 R7 的：
1. 四类比值恒等式；
2. F 的单调性与 submodularity：Δ_x F(x,y) 和 Δ_y F(x,y) 关于 x、y 均非增；
3. G(x,K) = 1 对所有 x（误差有限的边界条件）；
4. greedy 路径上的 tie 恒等式 Δ_x G(t,0) = Δ_y G(t,0)；
5. η = η_u·η_o = (âK−1)/(K−1) 以及 U_K(η) 的重参数化。

Deliverable：`results/T5_symbolic.py` 与输出。全部通过则 R7 升级为 `[VERIFIED-SYMBOLIC]`。

## T6 真实 surrogate 的 η^path 测量（2 小时）
目的：给论文的"何时重要"判据一个实证数字（对应 R2-2 审稿意见）。
1. 数据：sklearn 内置 breast_cancer、wine、digits（digits 取前 20 个特征即可）。若网络允许再加 openml 的 airline satisfaction，失败则跳过并记录。
2. 真实 f(S)：决策树（sklearn 默认）在 S 上训练、在 held-out 20% 上的 accuracy。预测器 f̃(S)：同一模型在训练集上的 5-fold CV accuracy。两者都缓存。
3. 跑 single-step greedy on f̃，K = 1..7。在每个轨迹状态 S^t 对所有候选 e 记录 (d_e(S^t), d̃_e(S^t))。计算 η_u^path、η_o^path、η^path，并报告负增益/零增益的处理方式（方向一致性在实践中是否成立）。
4. 同时报告 greedy on f̃ 的真实 f 值与 greedy on f（oracle greedy）的比值，与 1 − (1 − 1/(η^path K))^K 对比。
5. 30 次随机划分，报告中位数和 IQR。

Deliverable：`results/T6_eta_path.csv`、`figures/T6_*.png`、`results/T6_summary.md`。诚实报告：若 η^path 很大或方向一致性经常被违反，就如实写，这是重要信息。

## T7 定理陈述与证明草稿（1 小时，最后做）
写 `results/T7_theorems.tex`（LaTeX 片段，不是完整文档）：
- Theorem A（trajectory-tight）：L_K(η^path) 下界 + U_K 实例说明逐 K 紧。
- Lemma B（consistency）。
- Theorem C（K=2 exact）。
- Theorem D（1/η impossibility + 穷举匹配）。
- Corollary E（weak submodularity：submodularity ratio γ 下 1 − (1 − γ/(ηK))^K，Das–Kempe 2011 [CITATION-NEEDS-VERIFICATION]）。
每条定理后用注释标状态标签，指向对应的验证脚本。证明按 RESEARCH_STATE.md 写，不要改动逻辑；哪一步你不确定就在注释里写"此步需人工检查"。

---

## 结束时
REPORT.md 顶部 summary（≤ 5 行）；`git log --oneline` 应有 ≥ 7 个 commit；`results/` 里每个数字都有对应脚本。
