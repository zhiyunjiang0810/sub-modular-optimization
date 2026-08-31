# TASKS_EXP.md — 实验之夜（目标：ICLR 版全部实验数据与图）

原则（写进每个脚本的头注释）：
1. 全文禁止人工扰动 oracle（d̃ = d·exp(X) 一律删除）。每个任务的 f̃ 必须是"不看 f、只看可得数据"就能算出的东西。
2. f 的每次评估都缓存（dict，key 为 frozenset）；greedy 一律用 lazy 评估（CELF 式优先队列）。
3. 每个数字可复现：固定种子列表 seeds=range(30)，结果落盘 CSV，图另存 PNG+PDF。
4. 诚实报告：方向一致性违反比例、零增益处理方式、trimmed 的 ε 取值，全部进表格。
5. CPU 即可，任何脚本单次运行 > 30 分钟就先降规模跑通再放大。

数据：先用 data/ 下的本地文件（启动前人工放好，见 E0 清单），下载只作 fallback；网络失败记录并跳过该数据集，不阻塞其他任务。

理论对照用的三个量（statistics.py 统一实现，所有任务共用）：
- η^sel：每步 max_e d_e(S^t) / d_t，只用真值，d_t ≤ 0 的步单独计数并剔除；
- η^path(ε)：轨迹上 |d| ≥ ε 且 |d̃| ≥ ε 的候选对的 max(d/d̃)·max(d̃/d)，ε 默认 1 个量化单位（feature selection = 1/n_test；IM = 1；摘要 = 0.005）；
- 实际比值 ratio = f(S_greedy^f̃) / f(S_greedy^f)（分母用真值 greedy 作 OPT 代理，注明是上估）。
每个任务输出同一格式的行：task, dataset, K, seed, ratio, eta_sel, eta_path_trimmed, viol_sign_pct, L_K(eta_sel), L_K(eta_path)。

---

## E0 环境与数据盘点（30 分钟）
把 SubModular.ipynb 的可复用部分抽成 src/im_graph.py（图类、coverage f、lazy greedy），
删除 R-step 与 error oracle 代码。盘点 data/：期望文件 Facebook_1、Facebook_2、Twitter、
facebook directed.txt、reddit directed.txt、artist edges.txt、BBC 新闻三类文本、
airline satisfaction CSV。缺失的记录到 REPORT 并尝试下载（SNAP/Gemsec/UCD/openml），
下载失败就跳过。产出 data/INVENTORY.md（文件、节点边数或样本数、来源标注）。

## E1 Feature selection：学出来的 surrogate（2 小时）
数据：data/airline.csv（已找回的原版，约 2.6 万行）。预处理沿用 airline_performance.py 的
清洗步骤（缺失填充、异常值剔除、LabelEncoder），但**不做** df.sample(n=1000)：用全量数据，
held-out 20%（约 5000 行，accuracy 量化单位约 2e-4）。另加 breast_cancer、wine、digits（前 20 特征）。
f(S) = 决策树（sklearn 默认，与论文文字一致；旧脚本用的 GBC 与论文不符，此处修正）
在 held-out 上的 accuracy。f̃(S) = 同模型在训练 80% 上的 5-fold CV accuracy。
f̃ 的代码路径禁止 import 或触碰 X_test/y_test（旧 oracle 在测试集上算真实增益再乘噪声，
存在信息泄露，新管线必须从结构上排除）。
K = 1..7，30 个划分种子；GBC 只跑 1 个种子作稳健性核对并注明。
输出统一行格式；每步 (d, d̃) 对落盘供画散点。
基线直接移植 airline_performance.py 里的 SelectKBest、RFE、Mutual Information、Extra Trees，
在 airline 与 breast_cancer 上报告 oos accuracy 对比表（论文 Fig.1 的替代）。

## E2 Influence maximization：部分观测图作 surrogate（2.5 小时）
f(S) = 真图上的一跳覆盖 |{v : v ∈ S 或 v 被 S 指到}|（沿用原稿定义）。
f̃(S) = 同一公式，但算在"公司实际看得到的图"上：真图每条边以概率 p 保留，
p ∈ {0.3, 0.5, 0.8}；每个 p 抽 20 个观测图（种子固定）。
这是真实场景：平台只有一次不完整的爬取。
数据：Twitter、reddit、Facebook_1、Facebook_2（先全图 + lazy greedy 试跑；
1 小时内跑不完再按度数截到 20000 节点并注明，禁止截到 1000）。
K = 1..30。输出统一行格式（seed = 观测图种子），另记录 p 与 η 的经验关系
（p 越小 η^sel 越大，这条曲线本身就是"何时重要"的展品）。
对照：greedy on f（完整信息）、degree 排序、random。

## E3 Text summarization：启发式作 surrogate（1.5 小时）
f(S) = ROUGE-1 F-measure 对参考摘要（BBC 提供）。
f̃(S) ∈ {coverage, diversity, facility-location}（原稿三个启发式，参数照抄原稿），
它们不看参考摘要，是合法 surrogate。
BBC 三类各 100 篇，K = 3..7。无随机性，seed 列记文章 id。输出统一行格式。
注意：ROUGE 的 f 不单调也未必 submodular，报告 d ≤ 0 的比例即可，不要隐藏；
这个任务在论文里的角色是"模型边界外的行为"，措辞按此定位。

## E4 最坏实例的数值实现（1 小时）
把理论的三类元素实例（V_j 实例，results/N2）与 U_K 实例做成可运行的"数据集"：
K ∈ {3,5,8}，每段取一个 η。跑同一套 greedy 代码（不是符号验证，是实验管线），
表格展示 realized ratio 与理论 V_j 的差 ≤ 1e-10。
作用：管线正确性的 oracle + 论文里"worst case 真的会发生"的一张小表。
同时在这些实例上算 η^sel 与 η^path，展示三把尺子在最坏实例上的读数。

## E5 主图（1.5 小时，依赖 E1–E4 的 CSV）
figures/money_plot：x 轴 η（对数），y 轴 ratio。画理论曲线 L_K、ρ_K（取 K=5 与 K=30 两幅或双列），
叠加 E1–E3 的散点（x = 实测 η^sel，y = 实测 ratio，按任务着色），E4 的点应落在曲线上。
预期图景：真实任务的点远在曲线上方（worst case 与典型的差距），E4 的点贴线。
另出三张辅助图：η^sel 随 K 的分布（箱线）；IM 的 p 与 η^sel 关系；
feature selection 的 (d, d̃) 散点带 η 带（例证方向一致性违反发生在近零增益处）。

## E6 汇总与写作物料（1 小时，最后）
- results/EXP_SUMMARY.md：每个任务一段（设定、f̃ 是什么、中位数表、对论文的一句话结论），
  外加"与原稿实验的差异清单"（删了什么、换了什么、为什么）。
- 论文 Experiments 节的表格草稿（LaTeX，booktabs）：三任务 × {ratio 中位数, IQR, η^sel 中位数,
  认证下界 L_K(η^sel), 方向违反 %}。
- REPORT.md 顶部 5 行 summary，git commit。

---

执行顺序：E0 → E4（先拿到管线 oracle）→ E1 → E3 → E2（最耗时放后，图大时可降规模）→ E5 → E6。
预算总计约 9.5 小时。卡住 45 分钟记录跳过。子代理用 Opus。

数据集备选（时间富余才做，各 30 分钟上限）：
- Feature selection 加 openml adult（大样本、类别特征，检验 η^sel 是否随 n_test 变小而降）；
- IM 加 SNAP email-Eu-core（小而有向，全图秒级，适合放大 K）。
不做：GNN/神经 surrogate、IC/LT 随机传播模型、任何需要 GPU 的东西——留给 future work 一句话。
