# TASKS7.md — 第七晚：问题 B 的收口（预算 4 小时）

目标：把"和 greedy 同预算的算法类"的上界写成定理，并测试两个线性预算候选算法能否超过 greedy。
规则不变（台账优先、状态标签、每任务 commit、子代理 Opus、卡 45 分钟跳过、.tex 编译存日志、数字走宏）。
执行顺序：L1 → L2 → L3 → L4。

## L1 Greedy-budget corollary（1.5 小时）
把 thm:hardness（J2 校准版）按 greedy 自己的预算重新参数化：
- 算法类 𝒜_lin：确定性，至多 Q = nK 次 f̃ 查询，每次查询集合大小 ≤ K，输出 ≤ K 个元素。
- 取 τ = 1（balanced ⟺ |S∩O| ≤ 1）。重做集中不等式：单次查询（|S| ≤ K）落入 |S∩O| ≥ 2 的概率
  ≤ C(K,2)·(K/n)²·(1+o(1))，对 Q = nK 取并集界得失败概率 ≤ K⁵/(2n)·(1+o(1))；输出集合与 O 相交的概率 ≤ K²/n。
  写出显式条件（形如 n ≥ 4K⁵）使总失败概率 < 1/2。
- 结论：∀ A ∈ 𝒜_lin、η > 1（且 η ≥ (K−1)/(K−1) = 1 自动满足），存在实际误差恰为 η 的实例使
  f(T)/f(O*) ≤ U_K(η) = 1 − (1 − 1/(η(K−1)+1))^K = H_{K,1}(η)；结合 thm:ceiling 得 ≤ min{U_K(η), 1/η}。
- 随机版：ε_n = K²/n + K⁵/(2n)，写清量词。
- 与 greedy 的差：符号验证 U_K − ρ_K ≥ 0（已有 U_K > V_{K−1} 及 ρ_K ≤ V_{K−1}），并由 H-B 的展开给出
  U_K − ρ_K = c'(η)/K² + O(1/K³) 的 c'(η)（或至少验证 K·(U_K−ρ_K) → 0 与 K²·(U_K−ρ_K) 收敛到常数，数值 K ≤ 400）。
- 交付：paper 新 Corollary "optimality within the greedy query budget"（陈述 + 附录证明，概率装配段标 [HAND-PROOF-UNREVIEWED]）；
  台账新卡 T10b；一张表 results/L1_table.csv：K ∈ {2,3,4,5,8,10,20}、η ∈ {1.25,1.5,2,3,5}：ρ_K、U_K、min{U_K,1/η}、差。
  一句 remark：η ≥ K 时 ρ_K = 1/η，greedy 精确达到该类天花板。

## L2 两个线性预算候选的精确最坏值（1.5 小时）
用全格点 LP（code/worst_case_lp.py 的框架，重新编码算法路径）计算：
- 候选 A（top-m shortlist）：按 f̃ 单元素值取前 m 个（m = K+1），在这 m 个元素的所有 K-子集上按 f̃ 取最大者输出。
  查询数 n + C(m,K)，线性。
- 候选 B（greedy + swap pass）：先跑 predictive greedy 得 T；再对每个 t ∈ T、e ∉ T 用 f̃ 检查 T−t+e，
  若 f̃ 提高则接受（单轮，按固定顺序扫描）；查询数 ≤ nK + K(n−K)。
参数：K=2（n=4,5,6）、K=3（n=6,7）、η ∈ {1.25, 1.5, 2, 2.5}，tie 对抗。
LP 编码要求：每条"按 f̃ 比较"的决策都是线性约束；候选 A 需枚举"哪 m 个进入 shortlist"与"最终选谁"的所有分支取最小；
候选 B 需枚举 swap 序列的接受/拒绝分支。先 n 最小的跑通，再放大。
比较对象：ρ_K(η)（同 K）与 U_K(η)。结论三选一记录：严格优于 ρ_K / 等于 / 劣于，附精确数值。
若某候选严格优于 ρ_K：立即用精确有理复核，并检查该实例是否违反 L1 的假设（查询大小、查询次数）；
这将与 N4/F3 的证据矛盾，标 [最需人类判断]。
交付：results/L2_linear_candidates.md + 脚本 + json；台账 T11 追加一行。

## L3 论文段落与图（40 分钟）
- 正文 open-problem 段落草稿（results/L3_openproblem.tex）：夹逼区间 [ρ_K, min{U_K,1/η}]、宽度 O(1/K²)、
  K=8 η=2 的三个数（0.4216 / 0.4242 / 0.5）、两个候选的 LP 结论、N4/F3 证据一句、"we are not aware of any
  algorithm in 𝒜_lin whose worst-case ratio exceeds ρ_K"。不写 "we conjecture greedy is optimal" 以外的任何断言。
- 把 sandwich 图做成 paper 版（figures/sandwich_paper.pdf，两栏宽、字号 ≥ 7pt、英文标签），caption 草稿。

## L4 收尾（20 分钟）
台账同步（T10b 新卡、T11 更新）、全文编译 0 错误、REPORT 顶部 5 行、push。
