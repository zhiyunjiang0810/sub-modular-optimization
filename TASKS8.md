# TASKS8.md — 落实独立审计 J5（预算 6 小时）

输入：results/INDEPENDENT_THEORY_AUDIT_2026-09-12.md、VERIFICATION_SUMMARY.md、verify_audit.py、
submodular_K4_exact_duals.json（放入 results/J5/）。规则不变：台账优先、每项改动在 REPORT 注明"J5 §x"、
状态标签、每任务 commit、子代理 Opus、卡 45 分钟跳过、.tex 编译存日志、数字走宏。
J5 给出的新手证登记为 [HAND-PROOF-UNREVIEWED，来源 J5]，不因采纳而升级。

执行顺序：M0 → M1 → M2 → M3 → M4 → M5。

## M0 闸门（30 分钟）
运行 results/J5/verify_audit.py（标准库，需 JSON 同目录），确认四个 PASS；复跑 J5 列出的脚本清单中
本地可跑的（N1、N2、T5、H_J3、H_B --quick、L1、J2_core、H3_j2、H_E），记录退出码到 results/M0_j5_gate.md。
用有理数独立复算 J5 的三个反例：§3 停止版反例（ratio 1/2 vs L_2(1)=3/4）；§11 固定 n=4,K=2,η=3/2 的
穷举反例（6 次查询保证 2/3 > 3/5）；§10 的 N∖{e} 攻击在 K=4, τ=1, n=12 上的 G 值差。

## M1 定义与算法统一（1 小时）
1. 全文（model.tex、results.tex、appendix、dossier 副本、statistics.py）统一为固定 K 步 greedy：零预测增益
   也继续选；a_t 三类穷尽；提前停止版删除或改为"若停止则 T=S^{K*} 且仅对已执行步给乘积界 1−∏(1−1/(K a_t))"。
   statistics.py 按固定 K 步重算 E2 的 η^sel 与证书列，检查是否有未记入的早停 run。
2. Lemma 0′ 改写：定义 band 类 𝓕(η_u,η_o)，缩放给出乘积相同的两个 band 类之间的双射并保持 argmax；
   不再对"实际最小因子"陈述。
3. ρ_K 的 n 量词：定义 ρ_{n,K}，加 restriction（到 T∪O*）+ padding 引理，得 n ≥ 2K 时 ρ_{n,K}=ρ_{2K,K}
   [HAND-PROOF-UNREVIEWED，来源 J5 §13 的论证移植到主模型]；n<K、OPT=0、空轨迹的约定写进 §0。
4. prop:nobound 与 thm:ceiling 的随机版本改为"对每个随机算法存在固定实例使 E_seed[...] ≤ ..."。
5. prop:valueacc (iii) 的 ε 定义域扩到 ε ≥ 0 或加"若该值 < 1"。

## M2 标签与措辞收缩（1 小时）
1. L2/L2R/H_F 的全部"精确分数"改为 [VERIFIED-LP，有限参数，浮点求解]；台账 T11 与 md 同步；
   若要保留"精确"，需补每格的有理数对偶或向外舍入下界（本晚不做）。
2. 候选总结重写：PE_1 预算 O(n²K)，不属 𝒜_lin，在 n=2K 优于 greedy、n ≥ 7 劣于；shortlist 属 𝒜_lin；
   swap pass 预算 2nK−K²、tie 为对抗选择。删除任何"三个候选均不超过 greedy"式句子。
3. cor:greedybudget 标题改 "An upper bound within the greedy query budget"；正文与 open-problem 段的
   猜想加量词：n ≥ 4K⁵（或 inf over n）；引用 J5 的 n=4 反例说明为何必须加。
4. rem:hardness-pins：适用条件写 nK ≤ n^c（非"c ≥ 2"）；c=0 反例只说明 c=0。
5. thm:hardness 后加 remark：N∖{e} 攻击说明该构造族不能去掉查询大小限制；摘要与 intro 占位注释里
   加"query-size restriction must appear wherever hardness is mentioned"。
6. 随机版 ε_n 的联合极限条件（n/K⁵ → ∞）写清；min{H,1/η} 仅对确定性。
7. R-step remark：删"三点相等故极限不变"的推理，改为 J5 给的证明路线一句或删句。
8. additive band 的"ε 项紧"限定到已验证参数；单元素与 all-pairs 版本不混写。
9. H-B 的证据来源改为"闭式 + Fraction/mpmath 外推，LP 为对拍"。
10. §2 前的解释句改为 "value accuracy need not imply the marginal-gain assumptions used in our bounds"。

## M3 新增证明与结果（1.5 小时）
1. thm:ceiling 推广：把 J5 §9 的补集损失证明（h supermodular、三步）写入附录，陈述 α*_det(n,K,η) 的完整
   形式 (9.4)；台账 T8 更新（n<2K 达到方向由 [CONJECTURE] 升为 [HAND-PROOF-UNREVIEWED，来源 J5]，
   随机版仍 [OPEN]）。
2. rem:exact-gap（submodular surrogate）：删除"实例背书 U_K 失效"的错误方向；加入 K=4, η=3/2 的精确点
   ρ^sub_{8,4}=23/41 > U_4(3/2)，证据为 16 个轨道代表的有理对偶证书 + 匹配实例（results/J5）；
   加 restriction+padding 得 n ≥ 8 同值；一般 W_m 上界改为 J5 §13 的简短手证 [HAND-PROOF-UNREVIEWED，来源 J5]。
3. 台账 T3/T6/T6b/T8/T9/T10 的 [HAND-PROOF-UNREVIEWED] 项加注 "J5 人工复核：已闭合；待作者复核后升级"；
   T9 清理新旧并存状态，历史移到卡末。
4. cor:greedybudget 补 η=1 情形（θ=1、F=G，U_K(1)=ρ_K(1)）与 K=1 单列。

## M4 must-not-claim 追加与卫生（30 分钟）
追加到对应卡：随机算法逐种子满足确定性界；由停止前 η^sel 得 L_K；c<2 一律不含 greedy；所有 n 上 greedy
同预算最优；PE_1 属 nK 类；浮点分支穷尽等于精确有理最优；高比值实例证明 worst-case 下界；小查询 hardness
已解决 unrestricted-size optimum；本文证明了 learned predictors 满足全局误差假设。
删除 main.tex 的 \\iclrfinalcopy（PDF 页眉当前显示 Published as a conference paper）。

## M5 收尾（30 分钟）
全文编译 0 错误、数字审计、台账逐卡同步、REPORT 顶部 5 行（含"J5 严重项 5/5 已处理"）、push。
