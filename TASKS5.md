# TASKS5.md — 第五晚：装配全文骨架（预算 9.5 小时）

前提：两个建模决定已定案——(D1) 主模型 f̃ 无限制，submodular f̃ 作 remark；
(D2) Theorem 6 降为 Proposition，标注 "restated in the prediction-error model of Section 2,
essentially due to Goundan & Schulz (2007, Theorem 1)"，证明放附录并注明为完整性收录。
本晚一切改动以这两条为准。规则不变（状态标签、45 分钟跳过、每任务 commit、子代理 Opus、
所有 .tex 必须在 paper/ 模板下编译通过并存日志）。

明早人类要在骨架上写 abstract 与 intro，所以：G0–G3 必须完成；G4–G6 尽力。
执行顺序：G0 → G1 → G2 → G3 → G4 → G5 → G6 → G7。

---

## G0 落实两个决定（45 分钟）
1. results.tex：Theorem 6 改为 Proposition + D2 措辞；全文搜查确保它附近无 "we prove/show"；
   新增 Remark（D1）：if the surrogate is itself submodular, the exact worst case strictly
   improves for η < K−1（引 F4 的 LP 验证点 K=3, η=1.5: 9/16 → 19/33），general
   characterization left open；禁用 "more robust"。
2. RESEARCH_STATE.md 与 GLOSSARY.md 追加 D1、D2 两条决定与日期。
3. appendix_proofs.tex 里 Proposition（原 Thm 6）证明开头加一句 included for completeness。
4. 编译，commit。

## G1 装配 paper/main.tex 全文骨架（2 小时，本晚最高优先级）
目标：一份从头到尾可编译、除 abstract/intro 外全部有实质内容的 main.pdf。
1. 结构：abstract（占位：只放一句话故事的英文版作注释）；intro（占位：注释里放四个承重位
   的清单与 hook 的 A/B surrogate 例子，正文留空）；Section 2 model & preliminaries（从
   notation_table 与 results.tex 的模型段落抽出）；Section 3 related work（见 G3）；
   Section 4 theoretical results（results.tex，按 D1/D2 更新后的版本）；Section 5 experiments
   （见 G3）；Section 6 conclusion 占位；statements（AI use、reproducibility）；references；
   appendix（proofs + 实验补充）。
2. 生成 results/G1_pagebudget.md：逐节页数实测、9 页预算的分配建议（建议值：intro 1.5、
   model 1、related 0.75、theory 3.5、experiments 1.75、conclusion 0.25）、当前超支最多的三处
   与可压缩点（定理合并、remark 下沉附录）。
3. 编译四遍（pdflatex+bibtex+pdflatex×2）0 错误 0 未定义引用，日志入 results/。

## G2 附录证明写给人读（2 小时）
现有 appendix_proofs.tex 多处以 "verified symbolically" 代替论证，投稿版必须是人能逐行检查的证明。
1. U_K 紧性：写成完整归纳/直接验证证明（四类比值恒等式的代数展开、单调与 submodular 的
   逐情形验证、greedy 归纳），2–3 页，[HAND-PROOF-UNREVIEWED]，注释标注"由 T5 脚本符号复核"。
2. ρ_K = min V_j 下界：一般 K 对偶权重的显式公式、非负性论证、加权求和恒等式的展开步骤
   （关键消项写出来，不许只写 "direct expansion"）；上界：三类元素实例的定义、每步增益表、
   greedy 归纳。各 2 页左右，[HAND-PROOF-UNREVIEWED]。
3. R6 有效不等式（F2 已有）整合进来；coherence、1/η、渐近推论、n² 预算 hardness 依既有草稿
   润写。每个证明后加一行 "machine-checked by results/<script>"（如实指向）。
4. 编译，页数报告并入 G1_pagebudget.md 附录部分。

## G3 Experiments 与 Related work 正文（2 小时）
1. paper/sections/numbers.tex：从 E1–E4/F1 的 CSV 自动生成命名宏（\\EOneAirlineRatio 等），
   正文所有实验数字一律用宏，禁止手打数字。生成脚本 results/G3_gen_numbers.py。
2. paper/sections/experiments.tex：三任务谱系叙事（学出的 surrogate / 部分观测 / 启发式+边界外），
   主图与三辅图引用，EXP_table 编入，固定表注两句（OPT 代理、非正步），E3 的边界外发现
   如实一段，E2 的 p–η 一段。全部数字来自 numbers.tex。
3. paper/sections/related.tex：四组（approximate oracle / approximate submodularity / noise /
   learn-then-optimize）+ 两条邻线（预测解、预测动态），每组三句：误差是什么、答案是多少、
   与本文差别；只用 references.bib 里核验过的 23 条；Bhawalkar 放 noise 组。
4. results/G3_number_audit.md：脚本扫描 experiments.tex 与 results.tex 中的每个数字字面量，
   报告哪些不是宏（应为 0 个，除 K、页码等结构数字白名单）。
5. 编译，commit。

## G4 补测（1.5 小时，尽力）
1. breast_cancer K=5 的 OPT 暴力枚举（估 74 分钟，缓存决策树评估），更新 OPT 代理脚注宏。
2. airline 的 OPT 代理：全枚举不可行，改报保守替代——用 f̃ 上穷举 top-200 候选集 ∪ 随机
   2000 个 K-子集的最大真值作为 OPT 的下估，得到 ratio 的上估区间，写清这只是 sanity check，
   表格主数仍用 greedy-on-f 分母。若超时 45 分钟则跳过并记录。

## G5 对抗审稿（1 小时，独立子代理）
开一个只读的 Opus 子代理，输入：main.pdf 全文 + TPAMI 两位审稿人的意见要点（在 RESEARCH_STATE
"已知的论文错误"与 PROJECT_INSTRUCTIONS 叙事节）+ GLOSSARY 禁用表。任务：按 ICLR 审稿维度
（novelty/soundness/clarity/reproducibility）各给至少 3 条最强攻击，每条注明位置与建议修法；
另单独跑一遍空洞性检验（每个限定词做替换测试）与术语撞名检查。产出 results/G5_review.md，
按 严重/中等/轻微 分级。规则：只提意见不改正文；指控数字错误必须给出与 CSV 对照的证据。

## G6 投稿卫生（45 分钟）
1. 双盲检查：正文与附录无作者名、无致谢、无可识别仓库链接；repo 链接位置写
   "anonymous repository (link withheld)" 占位，并在 results/G6_submission_checklist.md 写
   匿名化仓库的待办（如 Anonymous GitHub）。
2. AI use statement 与 reproducibility statement 按模板要求的位置放置并确认不计页。
3. 图字号检查：主图与辅图在双栏缩放后最小字号 ≥ 7pt，不足则重出图。
4. checklist 全部落盘。

## G7 收尾（30 分钟）
REPORT.md 顶部 5 行 summary（明早第一眼要看的三个文件路径写明：main.pdf、G1_pagebudget.md、
G5_review.md）；commit + push。
