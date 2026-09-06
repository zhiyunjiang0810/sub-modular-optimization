# H1_bib_crosscheck.md — TPAMI 版与 ICLR 版文献交叉验证（2026-09-06）

来源：legacy/tpami_submission/（自 legacy/Submodular_ICLR.zip 解压，原 zip 由
paper/ 移入 legacy/）。旧 bib：legacy/tpami_submission/submodular.bib，
155 条；旧正文实际引用 50 个 key（python 正则抽取，剔除注释行；脚本内联于
本次会话，等价一行命令 `grep -o` 可复现）。新 bib：paper/references.bib，
此前 23 条（F6 全过四步核验），本任务后 29 条。

## 1. 交集逐字段 diff（两 bib 共有 4 个 key）

| key | 字段 | 旧 bib | 新 bib | 以哪边为准 / 依据 |
|---|---|---|---|---|
| nemhauser1978analysis | number / doi | 无 | number=1, doi=10.1007/BF01588971 | **新**。F6 四步（注意 F6 标记 PASS*：出版方页 403，字段来自 DBLP/Springer 元数据）；author/journal/volume/pages/year 两边一致 |
| horel2016maximization | 条目类型 | @article（把 NeurIPS 当 journal） | @inproceedings + pages 3045-3053 + 官方 proceedings URL | **新**。NeurIPS 是会议录，旧类型错误；F6 以 proceedings.neurips.cc 官方页核验 |
| kempe2003maximizing | doi / booktitle 拼写 | 无 doi，全小写 booktitle | doi=10.1145/956750.956769，规范 booktitle | **新**。pages/year 两边一致 |
| lin2011class | publisher/address/URL | 无 | ACL + Portland + aclanthology P11-1052 | **新**。pages/year 两边一致 |

无"两边都可疑"的字段冲突；4 条的核心字段（作者/年份/页码）两边一致，差异全部是新版补全的规范化字段。附带发现：旧 bib 对 Horel–Singer 同一篇论文有两个 key（horel2016maximization 与 maximizingApproximatelySubmodularFunctions），正文两个都引过。

## 2. 旧有新无的分类（旧正文引用的 47 个 key）

### 2a. 同一论文、key 更名（9 条，无需处理，新 bib 已有）

greedySubmodularFunctions=nemhauser1978analysis；maximizingApproximatelySubmodularFunctions=horel2016maximization；cachingWithPredictions=lykouris2021competitive；ImproveOnlineAlgorithmsViaML=purohit2018improving；learningAugmentedSubmodularUpdates=agarwal2024learning；setCoverisHard=feige1998threshold；facebook2=rozemberczki2019gemsec；submodularOptNoise=hassidim2017submodular；submodularFunctionsLearn=balcan2018submodular。

### 2b. 仍需要：本次过 F6 四步后入库（6 条）与使用位置

| 旧 key | 新 key | 四步核验记录 | 写入位置 |
|---|---|---|---|
| SchedulingViaWeights | lattanzi2020online | DBLP conf/soda/LattanziLMV20；SODA 2020 pp.1859-1877；doi 10.1137/1.9781611975994.114；支撑句=乘性预测误差的 LAA scheduling 惯例（learned weights，保证随误差退化）；版本=唯一会议版 | model.tex，Definition 1 后的 spirit-of 句 |
| FlowTimeScheduling | azar2021flow | ACM 10.1145/3406325.3451023；STOC 2021 pp.1070-1080；arXiv:2103.05604 摘要明确 constant factor distortion between predictions and real processing time（乘性）；版本=STOC 正式版 | 同上 |
| RealTimeSchedulingwithPredictions | zhao2022real | DBLP conf/rtss/0002LZ22；RTSS 2022 pp.331-343；doi 10.1109/RTSS55097.2022.00036；竞争比为预测误差 η 的函数；**作者自引，双盲下须第三人称**（已在 bib 注释标明） | 同上（旧 error-metric 节在同一位置引的正是这三篇） |
| extra-trees | geurts2006extremely | Springer 10.1007/s10994-006-6226-1；Machine Learning 63(1):3-42, 2006；E1 baseline 面板的 extra_trees 选择器出处 | appendix_experiments.tex baselines 段 |
| feature-selection | peng2005feature | IEEE 10.1109/TPAMI.2005.159；TPAMI 27(8):1226-1238, 2005；E1 baseline 的 mutual_info 排序所属的 max-relevance 判据 | 同上 |
| bbcnews_dataset | greene2006practical | 旧文引的是 UCD 数据页 @misc；升级为引入该语料的论文：ACM 10.1145/1143844.1143892，ICML 2006 pp.377-384（greene2006practical 在旧 bib 里有但旧文未引）；E3 数据出处 | experiments.tex E3 setup 句 |

### 2c. 随删除内容淘汰（32 条）

- **旧实验的应用背书类（13）**：Chakraborty2020、Kalaivani2021、Salini2024、abdulkareem2021evaluation、assegie2021breast、chen2018decision、jiang2022forecast、minaee2021deep、otchere2022application、sachdeva2022systematic、sharaff2019extra、yadav2022extractive、wei2014submodular。新实验章按三族谱系叙事，不再逐应用引证。
- **旧数据/自引（3）**：reddit、facebook&twitter（已被 SNAP 替代图的引用 rozemberczki2019gemsec/leskovec2007graph/yin2017local 取代）、anonymous2024submodularexperiment（旧匿名实验仓库占位，被 statements 的 anonymous repository 占位取代）。
- **旧 related-work 理论背景（15）**：ahmed2011maximizing、approxSubmodularFunctions、banihashem2023dynamic、bogunovic2017robust、linearTimeApproximationForUnconstrainedSubmodular、maximizingNonMonotoneSubmodularFunctions、minimizingSubmodularFunctionsUnderNoise、mossel2010submodularity、submodularOptNoisetoImageCollection、learnValueFunctions、representationApproxLearnSubmodularFunctions、Krause_Golovin_2014、errorMetricsForGraphs、matchingWithPredictions、secretaryWithPredictions。多属非单调/无约束/最小化/动态/robust-partition 等不同问题线，或 LAA 邻线已由 purohit/lykouris 覆盖；其中 **errorMetricsForGraphs（universal error measure）、Krause_Golovin_2014（综述）、mossel2010submodularity、submodularOptNoisetoImageCollection、learnValueFunctions、representationApproxLearnSubmodularFunctions 标为"可选，人工裁决"**：若 related 篇幅放宽可回收（当前 related 已 1.0 页超预算 0.25 页，保守不加）。
- **旧文自身缺陷（1）**：vergara2014review 在旧正文被引但两版 bib 都没有该条目（旧稿 dangling citation），仅记录。

旧 bib 其余 105 条未被旧正文引用（多为与调度论文共用 bib 的条目），不逐条处理。

### 2d. 留给人工的缺口

- RFE（recursive feature elimination）与 SelectKBest 两个 baseline 无学术出处：旧 bib 只有 RFE 的应用类论文（已归淘汰类）；标准出处 Guyon et al. 2002 (Gene selection for cancer classification) 两版 bib 都没有，属新增引用而非恢复，超出本任务范围，留人工决定是否入库。
- 三条 scheduling 引用中 zhao2022real 是作者自引；camera-ready 阶段是否保留由人工定夺（双盲阶段第三人称引用合规）。

## 3. Section 4.1 恢复的命题

旧 Lemma 2（lem:any-epsilon-error-can-be-infite-eta）与 Lemma 3
（lem:any-eta-error-has-bounded-epsilon-error）合并为
Proposition prop:valueacc（"Value accuracy is neither sufficient nor
necessary"），置于 results.tex 4.1 节 prop:necessity 之后；证明在
appendix_proofs.tex 新小节 app:valueacc，[HAND-PROOF-UNREVIEWED]。
(i)/(iii) 按旧证明用本文记号重写；(iii) 旧证明用的是 all-pairs 形式的
d_∅(S)，重写为单元素定义沿枚举 telescoping（附录注释已注明差异）；
(ii)（"nor necessary" 半边）是 H1 新增的两行 scaling 观察
（f̃=(1+M)f：value accuracy 任意坏、η^sel=1、Proposition 4 全额适用），
注释中已声明其来源。编译 0 错误 0 未定义引用（results/H1_compile.log，
27 页）；数字审计仍 0 违规（命题中的 ε 常数属 results.tex 理论常数白名单）。

## 4. 其他

- G6 checklist 已追加硬规则：任何匿名化产物排除 legacy/（TPAMI 原稿含作者
  姓名、作者照片 images/*.jpg/png、IEEE 传记，入包即破盲）。
- 新增引用后 references 共 29 条，全部有 F6 级核验记录（23 条 F6 + 6 条本
  任务，核验注释在 references.bib 条目上方）。
