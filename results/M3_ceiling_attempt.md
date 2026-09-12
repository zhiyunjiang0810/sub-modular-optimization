# M3.1 记录：n < 2K 天花板"达到方向"的本地重构尝试（FAILED）

任务（TASKS8 M3.1）：把 J5 §9 的补集损失证明（"h supermodular、三步"）写入附录，把台账 T8 的
n < 2K 达到方向由 [CONJECTURE] 升为 [HAND-PROOF-UNREVIEWED，来源 J5]。

**输入缺失**：J5 报告未送达（results/J5/MISSING_INPUTS.md），证明原文不可转录，
陈述 (9.4) 的完整形式也不可得（按 H-E 的 T8 卡推断应为 α*_det = K/(m0+(K−m0)η)，m0 = max(0, 2K−n)，
但无法核对）。按 M0 闸门裁定改为限时本地重构。

**尝试记录（约 20 分钟，未到 45 分钟上限即判定收敛无望）**：

1. 值带 telescoping（f̃(S) ∈ [f(S)/η_u, η_o f(S)]，由单元素带沿链求和）+ 穷举的
   f̃(Ŝ) ≥ f̃(O)：只给 f(Ŝ) ≥ f(O)/η，即 n ≥ 2K 的老结论，重叠信息未用上。
2. 用 |Ŝ∩O| ≥ m0 = 2K−n 改进：需要把 f(Ŝ) 下界拆成"Ŝ∩O 部分贴近真值 + 其余部分按 1/η"。
   卡点与 H-E 手证完全相同：f(Ŝ∩O) 没有下界（可为 0），两段分解失效。
3. 按提示引入补集损失 h(S) = f(N) − f(N∖S)（f submodular 时 h supermodular）：
   没有找到把 h 的 supermodularity 与穷举选择 f̃(Ŝ) ≥ f̃(O) 结合出 per-overlap 常数
   K/(m+(K−m)η) 的三步组合；两词提示（"h supermodular、三步"）不足以约束重构方向。

**结论**：FAILED。T8 的达到方向维持 [CONJECTURE]（网格 [VERIFIED-LP at grid] 不变），
附录不加证明。若 J5 文件后续送达，按其 §9 原文重启（登记 [HAND-PROOF-UNREVIEWED，来源 J5]，
不因采纳而升级）。
