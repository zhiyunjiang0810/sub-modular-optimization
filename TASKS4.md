# TASKS4.md — 第四晚：修补、收尾、写作物料（预算 10 小时）

开始前：读 CLAUDE.md、GLOSSARY.md、RESEARCH_STATE.md、REPORT.md、results/EXP_SUMMARY.md、
results/T7_theorems.tex、results/N5_bounded_query_hardness.tex。规则不变（状态标签、45 分钟跳过、
每任务 commit、子代理用 Opus）。本晚新增两条硬规则：
- 任何进入 .bib 的条目必须通过 F6 的四步核验，否则只能以 [CITATION-NEEDS-VERIFICATION] 出现在正文注释里。
- 所有 LaTeX 必须能在 paper/ 下用 ICLR 2027 模板编译通过（pdflatex + bibtex 两遍），编译日志存 results/。
  若 paper/ 下没有模板文件，写成可 \\input 的片段并在 REPORT 顶部标注"未编译"。

执行顺序：F0 → F1 → F2 → F5 → F6 → F3 → F4 → F7。F3 是唯一允许整体 FAILED 的任务。

---

## F0 状态同步与记号定稿（30 分钟）
1. RESEARCH_STATE.md 追加 R14（实验之夜结果，按 EXP_SUMMARY 的四个任务各一段，含"分母是 OPT 代理"）。
2. R10 里"L_K ≤ min_j V_j 仅数值支持 [CONJECTURE]"改为 [PROVED]，附一行理由：reduced LP 的约束集
   包含 Theorem 6 所用 LP 的全部约束，约束更多则最小值不减。
3. GLOSSARY.md 加三条：
   - 记号定稿：全局误差 $\\eta$；选择误差 $\\eta^{\\mathrm{sel}}$（正文用）；轨迹误差只在一处 remark 以文字出现，
     若需记号用 $\\eta^{\\mathrm{tr}}$。η_u、η_o 仍为下标分量。定义 LaTeX 宏 \\etasel、\\etatr 放 paper/macros.tex。
   - η^sel 的出处：Goundan & Schulz 2007 的 α-approximate incremental oracle 的参数，我们的记号；
     论文措辞 "in the terminology of Goundan and Schulz, ..."。
   - 引用四步核验规则（见 F6）。
4. commit。

## F1 实验修补（1.5 小时）
1. ROUGE 核对：pip install rouge-score；在 BBC 每类各 30 篇上，把自实现的 ROUGE-1 F 与 rouge_score
   的 rouge1 fmeasure 逐篇对比，报告最大绝对差与平均差；若差 > 1e-6，找出原因（tokenization/stemming），
   以 rouge-score 为准重跑 E3 全量并更新 CSV/表/图。结果写 results/F1_rouge_check.md。
2. E2 的 η^path：删除 top-50 截断，对 4 个图全量重算 (d, d̃)（artist 单 run 3.4s，可承受），
   更新 E2 的 CSV；若某图重算超过 40 分钟，则该图的 η^path 在所有表中标 "n/a（未全量）"，不得报告下估值。
3. d_t ≤ 0 步的处理写死进 src/statistics.py：η^sel 只在 d_t > 0 的步上定义；每条结果行新增列
   n_steps_nonpos 与 frac_steps_nonpos；认证下界列名改为 L_K(eta_sel | positive steps)。
   重新生成 results/EXP_table.tex，表注固定两句：分母为 greedy-on-f（OPT 上估代理）；
   下界对正增益步成立，非正步比例见列。
4. E1 airline 的 OPT 代理：wine 上已有暴力枚举估计（0.972）；再在 breast_cancer 上做 K ≤ 5 的暴力枚举
   （C(30,5)=142,506 次决策树评估，缓存后可承受，若超过 30 分钟就到 K=4），报告 f(greedy^f)/OPT 中位数。
5. 重跑 E5 出图（若 1–2 改变了数据），核对图例、坐标、caption。
Deliverable：更新后的 CSV/表/图 + results/F1_fixes.md（每项改了什么、数字变了多少）。

## F2 理论卫生（1 小时）
1. (5,4) 点：用精确有理算术重解 reduced LP 与全格点 LP 在该点的值（fractions + 自写单纯形或
   sympy 的 LP，或对 HiGHS 解做有理重构后精确验证可行性与目标），确认差异为 0 或找出原因。
   结果写 results/F2_54_exact.md，状态标签。
2. R6 有效不等式手证：写 results/F2_R6_validity.tex，四族约束各一段推导（submodularity 两条、
   greedy 选择一条、coherence 一条），含 b_t ∈ O 情形令 g_{t+1,i} = 0 的处理。标 [HAND-PROOF-UNREVIEWED]，
   每步一句"此步用到 X"。
3. η^sel 下的紧性：在 U_K 实例（K=2..8，两个 η）上数值确认 η^sel = η^path = η̂，
   写进 results/F2_etasel_tight.txt，并在 RESEARCH_STATE R7 追加一行。

## F5 写作物料（2.5 小时，放在 F3 之前，保证一定完成）
在 paper/ 下产出可编译的片段（若模板不在仓库则为片段）：
1. paper/sections/results.tex：定理陈述的正式版，顺序按 RESEARCH_STATE 的"理论九节"：
   模型与记号（含 η、η^sel、近似比约定）→ 必要性定理 → Theorem 6（对 η^sel 陈述）→ 逐 K 紧性
   → coherence lemma → 精确最坏值 min_j V_j → 1/η 天花板 → 渐近推论 → 有界查询 hardness。
   每条定理后一句 remark 说它意味着什么；证明一律 \\ref 到附录。每条定理旁用注释标状态标签与验证脚本。
   删除所有 "we are the first"、"robust"、不带限定的全称句（对照 GLOSSARY 的禁用表）。
2. paper/sections/appendix_proofs.tex：证明骨架。Theorem 6 半页；U_K 紧性按 T5 的四类比值恒等式写；
   coherence 两行；min_j V_j 的下界给对偶权重公式并说明验证方式（"the identity can be checked by
   direct expansion; a script is provided"），上界给三类元素实例的定义与每步增益；1/η 的构造；
   有界查询 hardness 按 N5。所有 sympy 验证过的恒等式在附录注明 verified symbolically。
3. paper/sections/notation_table.tex：记号表（一页以内）。
4. paper/sections/statements.tex：AI use statement 草稿（如实：LP/符号验证脚本、实验脚本、定理草稿由
   生成式 AI 辅助生成，作者复跑全部脚本并逐行检查证明）；Reproducibility statement 草稿
   （指向附录与匿名代码仓库、数据处理说明、E3 回填摘要的说明）。
5. paper/figures/：主图与三张辅助图的 caption 草稿（captions.tex）。
所有片段的英文遵守写作规则：无 em dash，全称句带限定与引用，simple 不用 elementary/trivial。

## F6 引用核验与 .bib（1.5 小时）
对下列待引文献逐篇执行四步核验，产出 paper/references.bib 与 results/F6_citation_audit.md
（每篇一行：存在性来源 URL、支持的具体陈述及原文页码/定理号、bib 字段核对、版本选择理由）：
Nemhauser–Wolsey–Fisher 1978（Math. Prog.）；Nemhauser–Wolsey 1978 best algorithms（Math. OR）；
Feige 1998；Goundan–Schulz 2007；Horel–Singer 2016；Hassidim–Singer 2017；Das–Kempe 2011；
Elenberg et al. 2018；Balkanski–Rubinstein–Singer 2016 与 2017；Rosenfeld et al. 2018；
Bhawalkar et al. 2025；Agarwal–Balkanski 2024；Cohen-Addad et al. 2024；Balcan–Harvey（STOC 2011 / SICOMP 2018，选支持陈述的版本）；
Mirzasoleiman et al. 2015；Purohit–Svitkina–Kumar 2018；Lykouris–Vassilvitskii；Kempe–Kleinberg–Tardos 2003；
Lin–Bilmes 2011；Rozemberczki et al.（GEMSEC，替代图数据）；SNAP email-Eu-core 出处（Leskovec et al.）。
核验用 web_search / 官方页面（DBLP、出版方、arXiv 列表页）；网络不可达的条目一律标
[CITATION-NEEDS-VERIFICATION] 并不写入 .bib。bib 字段用模板 .bst 兼容的格式（author 全名、booktitle 正式名、year、pages）。

## F3 Hardness 全版本再攻一次（2 小时，允许 FAILED）
1. 取 N4 的显式 (F, G)，在真 balanced 带 |y − K|S|/n| ≤ τ 下做无泄露与 η 带检查：
   n ∈ {8K, 16K, 32K}，K ∈ {4, 6}，τ ∈ {1, 2}，报告最小可行 δ(n, K, τ) 及其随 n 的趋势。
2. 若可行：写 results/F3_hardness_full.tex，四步结构（concentration、构造、取值、Yao），
   每步标状态；concentration 引理对任意大小查询给出超几何尾界的显式形式。
3. 若不可行：给出紧约束清单与对偶证书，说明是构造问题还是技术极限；写 results/F3_summary.md。

## F4 submodular f̃ 约束下的最坏值（1 小时）
在全格点 LP 加 f̃ 的 submodularity 约束，K=2,3,4，η ∈ {1.5, 2, 3}，与 min_j V_j 比较。
若不同，写 results/F4_submodular_ftilde.md 作 remark 素材（"若额外要求 surrogate 为 submodular，最坏值变为…"）；
若相同，记录并说明现有实例族中是否存在 submodular 的 f̃（若不存在但 LP 值相同，说明另有实例）。

## F7 收尾（30 分钟）
REPORT.md 顶部 5 行 summary；results/ 与 paper/ 的文件清单；git commit 并 push。
