# EXP_SUMMARY.md — 实验之夜汇总（ICLR 版实验数据与图）

统一三量（src/statistics.py）：η^sel（每步真值最优/所选，剔除并计数 d≤0 步）、
η^path(ε)（trimmed 候选对乘积误差）、ratio = f(S_greedy^f̃)/f(S_greedy^f)（分母是 OPT 上估代理，
每处如此注明）。全部无人工扰动 oracle；缓存 + CELF；种子固定；图 PNG+PDF。

## E4 最坏实例（管线 oracle）
- 设定：N2 的 V_j 实例（K∈{3,5,8}×每段一个 η）+ U_K 实例（â=2），跑实验管线本体。
- 结果：19/19 realized ratio 与理论差 ≤1.1e-16；V_j 实例上 η^sel = η、η^path = η 精确。
- 论文一句话：worst case 不是渐近传说，构造实例在真实 greedy 代码上逐点落在 ρ_K 曲线上（主图叉点）。

## E1 Feature selection（学出来的 surrogate）
- 设定：f = 决策树 held-out accuracy，f̃ = train 上 5-fold CV（结构性隔离测试集，四层断言 +
  行为探针）；airline 全量 25,375 行 + breast_cancer/wine/digits20；K=1..7 × 30 seeds。
- 中位数表（K=7，四数据集合并，n=120）：ratio 0.971 [IQR 0.943-0.998]，η^sel 2.0 [1.35-3.0]，
  L_7(η^sel) 0.405，方向违反 22.7%。分数据集：airline ratio 0.999 / η^sel 1.55。
- 基线：airline 上 greedy-on-f̃ 每个 K 不劣于 SelectKBest/RFE/MI/ExtraTrees 最好者；
  breast_cancer 上互有胜负（诚实结论：大样本占优，小样本打平）。
- 论文一句话：学出来的 surrogate 的 η^sel 是个位数小值，认证下界有信息量（0.3-0.55），
  实测 ratio 还远高于它。

## E2 Influence maximization（部分观测图）
- 设定：一跳覆盖；f̃ = 边保留概率 p ∈ {0.3,0.5,0.8} 的观测图（每 p 20 种子）；
  4 个替代图（artist 50,515 节点全图未截断）；K=1..30；240 条轨迹全量。
- 中位数表（K=30，n=240）：ratio 0.963 [0.936-0.989]，η^sel 4.3 [1.66-12.0]，L_30(η^sel) 0.207。
- p-η 关系（展品，figures/aux_p_vs_eta）：p 0.8→0.3 时 η^sel 中位数升 3.2×-87×，
  ratio 仅 0.99→0.88-0.96；对照 degree(观测图) 0.66-0.89、random 0.06-0.54。
- 方法注记：viol=0 是结构性的（两覆盖函数增益非负，这把尺子在 E2 无信息量）；
  facebook 图 (d,d̃) 只存 top-50/步，η^path 系统性下估（已量化，E5 用 η^sel 轴不受影响）。
- 论文一句话：观测残缺度 p 单调决定 η，η 大两个数量级时实际损失只有 4-12%。

## E3 Text summarization（启发式 surrogate，模型边界外）
- 设定：f = ROUGE-1 F（自实现），f̃ ∈ {coverage, diversity, facility-location}（不看参考摘要）；
  BBC 三类各 100 篇；K=3..7。sport/tech 参考摘要由 HF 同源 CSV 回填（99/100 逐 token 验证，
  CSV 已入库 data/raw/ 保证离线复现）。
- 中位数表（K=5，n=879）：ratio 0.670 [0.576-0.757]，η^sel 7.2 [2.77-17.2]，方向违反 10%。
  最好 surrogate = coverage（ratio 0.712）。
- 边界外实测：ROUGE-1 F 在 70,560 个三元组上 submodular 违反 2.14%、单调违反 7.12%；
  被选步 d≤0 占 12-19%。措辞按"模型边界外的行为"定位。
- 论文一句话：启发式 surrogate 的误差与违例都大得多，ratio 掉到 0.6-0.7，与 E1/E2 形成谱系。

## 主图（figures/money_plot.png/.pdf）
K=5 与 K=30 双列：真实任务的 (η^sel, ratio) 散点整体悬在 ρ_K 与 L_K 曲线上方
（worst case 与典型情形的差距），E4 的构造实例精确贴线。辅助图：η^sel 随 K 箱线、
IM 的 p-η 曲线、feature selection 的 (d,d̃) 散点带 η=2 带（违例集中在近零增益）。

## 与原稿实验的差异清单（删了什么、换了什么、为什么）

| 原稿 | 现在 | 原因 |
|---|---|---|
| d̃ = d·exp(X) 人工扰动 oracle | 三类真实 surrogate（CV/观测图/启发式） | 原则 1：扰动 oracle 无外部效度；且旧 oracle 在测试集上算真实增益（信息泄露） |
| airline df.sample(n=1000) | 全量 25,375 行 | 小样本加剧 accuracy 量化噪声；全量后 airline ratio=0.999、η^sel=1.55 |
| GBC 分类器 | 决策树（与论文文字一致），GBC 留 seed0 稳健性核对 | 文实不符修正；结论对分类器不敏感 |
| Twitter/reddit/Facebook_1/2 图 | GEMSEC artist/politician/government + email-Eu-core | 原始文件丢失（INVENTORY 记录）；artist 与原实验同源 |
| R-step 实验 | 删除 | 理论侧已删（R-step 部分整体移除，见第一晚已知错误清单） |
| 无统一误差测量 | η^sel / η^path(ε) / ratio 三量 + 统一行格式 | 主图与认证下界需要；η^path 认证下界在真实数据上几乎无信息量，论文主用 η^sel（E1 结论） |

## 表格草稿（LaTeX, booktabs）：见 results/EXP_table.tex
