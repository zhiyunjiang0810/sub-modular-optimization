# E1 Feature selection：学出来的 surrogate（notes）

一键复现：`python results/E1_run.py`（分块跑见文末"运行方式"）。
产出：`E1_rows.csv`（统一行格式）、`E1_pairs.csv.gz`、`E1_baselines.csv`、
`E1_gbc_seed0.csv`、`E1_diagnostics.csv`、`figures/E1_baselines.png/.pdf`。

## 1. 设定

| 项 | 取值 |
|---|---|
| f(S) | `DecisionTreeClassifier(random_state=42)`（其余 sklearn 默认）在 80% train 上拟合，在 20% held-out 上的 accuracy |
| f̃(S) | 同一 estimator 在 **80% train 上**的 5-fold `cross_val_score` accuracy 均值（`cv=5` 即 StratifiedKFold，不 shuffle，给定划分后完全确定） |
| f(∅), f̃(∅) | majority-class 预测器（`DummyClassifier(strategy='most_frequent')`）的对应 accuracy；即 d_e(∅) 是相对"无特征预测器"的 accuracy 增量 |
| 划分 | `train_test_split(test_size=0.2, random_state=seed)`，不 stratify（与 legacy 一致），seed = 0..29，每个 seed 一个划分 |
| K | 1..7，一条 K=7 轨迹给出全部前缀 |
| greedy | 每步在当前状态上对所有候选取 argmax d̃（实现见 §4），无人工扰动 |
| ratio | f(S^{f̃}_K) / f(S^{f}_K)，分母是**真值 greedy**，不是 OPT |
| η^sel | max_t max_e d_e(S^t) / d_t，只用真值；d_t ≤ 0 的步单独计数并剔除（`src/statistics.py`） |
| η^path(ε) | 轨迹上 d ≥ ε 且 d̃ ≥ ε 的候选对的 max(d/d̃)·max(d̃/d) |
| ε | 1 个 accuracy 量化单位 = 1/n_test（每个数据集不同，见 §2） |

数据集：`data/airline.csv`（全量，清洗见 §3）、sklearn 内置 `breast_cancer`(30 特征)、
`wine`(13)、`digits` 前 20 个像素特征（`digits20`）。

`GradientBoostingClassifier`（默认参数 + random_state=42）作为 estimator 只跑 seed=0，
用来核对结论对模型族的稳健性（§10）。论文正文写的是决策树，legacy 脚本用 GBC，与论文不符，
此处以决策树为准。

## 2. 量化单位 ε = 1/n_test

| dataset | n | n_features | n_train | n_test | ε = 1/n_test |
|---|---|---|---|---|---|
| airline | 25375 | 22 | 20300 | 5075 | 1.9704e-4 |
| breast_cancer | 569 | 30 | 455 | 114 | 8.7719e-3 |
| wine | 178 | 13 | 142 | 36 | 2.7778e-2 |
| digits20 | 1797 | 20 | 1437 | 360 | 2.7778e-3 |

airline 的 held-out 5075 行，accuracy 量化单位 ≈ 2e-4，与任务书给的量级一致
（任务书说 25,977 行 / 约 5,200 行，实际 CSV 是 25,976 行，清洗后 25,375 行）。

## 3. airline 清洗步骤清单（逐条对照 legacy/airline_performance.py）

按 legacy 的原顺序：

1. `df.drop(["Unnamed: 0", "id"], axis=1)`：照搬。
2. `df["Arrival Delay in Minutes"].fillna(mean)`：照搬（全列均值，83 个缺失）。
3. `df.sample(n=1000, random_state=42)`：**删除**（任务要求全量）。
4. `LabelEncoder` 编码 `Gender, Customer Type, Type of Travel, Class, satisfaction`：
   照搬（legacy 复用同一个 `le` 对象逐列 `fit_transform`，等价于每列独立编码）。
5. 异常值剔除，三条固定阈值，照搬且顺序一致：
   `Flight Distance > 3736.5`（全量剔除 596 行）、
   `Departure Delay in Minutes > 800`（3 行）、
   `Arrival Delay in Minutes > 650`（2 行）。
   合计 25976 → 25375 行。
   注意：这三个阈值在 legacy 里是在 1000 行样本上定的，我们按任务要求"沿用清洗步骤"
   把它们当作固定阈值用在全量数据上（不重新按全量 IQR 计算）。
6. `StandardScaler` 循环：**跳过**，两个理由：
   (a) legacy 里这段是 no-op，它的判断条件是 `df[column].dtype == type(float)`，
       而 `type(float)` 是 `type`，pandas dtype 永远不等于它，所以没有任何一列被缩放；
   (b) 即使执行，逐列的 standardize 是单调仿射变换，决策树/GBC 对此不变，accuracy 不变。
7. `X = df.drop(columns=['satisfaction'])`, `y = df['satisfaction']`：照搬，22 个特征。

legacy 里**没有移植**的部分：`generate_error` / `oracle_simulation`
（d̃ = d·exp(Uniform(−ln η_u, ln η_o))，在测试集上算真实增益再乘噪声）。
这是本任务要修正的两个问题（信息泄露 + 人工扰动），全文不出现。

## 4. 结构性信息隔离

f̃ 的实现是 `CVSurrogate`，由 `make_surrogate(X_train, y_train, make_model)` 构造。
隔离由四层保证，`check_isolation()` 在每个数据集的第一个 seed 上以 assert 形式实际检查：

1. **作用域**：`make_surrogate` 的形参只有训练数组，函数体内没有任何 test 变量可捕获；
   f（真值）在另一个函数 `make_true_eval(X_train, y_train, X_test, y_test, ...)` 的闭包里。
2. **`__slots__`**：`CVSurrogate.__slots__ = ('_X_train','_y_train','_make_model','_folds','n_evals')`。
   有 `__slots__` 就没有 `__dict__`，因此**根本无法**给 f̃ 对象挂上任何 test 属性；
   assert 检查 `not hasattr(sur, '__dict__')`，且没有一个 slot 名字含 "test"。
3. **无闭包**：assert `CVSurrogate.__call__.__closure__ is None` 且
   `make_model.__closure__ is None`（模型工厂是 module-level 函数，不捕获任何东西），
   所以 f̃ 的代码路径里不存在指向外层 test 数据的自由变量。
4. **内存不共享**：对每个 slot 里的 ndarray assert `v is not X_test`、`v is not y_test`
   且 `not np.shares_memory(v, X_test/y_test)`。

另加一个**行为探针**（比结构检查更强）：把 `y_test` 原地随机置换，再重新计算 f̃ 与 f。
断言 f̃ 的值**逐位不变**（`v1 == v2`），同时记录 f 确实变了（说明探针有效力，不是空转）。
四个数据集的探针实测值见 §11。

真值 d 的用途：只进 `TrajectoryStats`（统计）和 `E1_pairs.csv.gz`（落盘供 E5 画散点），
不进 f̃、不进选择规则。选择规则只看 d̃。

## 5. greedy 的实现与一个必须诚实报告的问题

按原则 2，f 与 f̃ 的每次评估都走 `src/im_graph.py::CachedSetFunction`（frozenset 做 key），
greedy 走 `src/im_graph.py::lazy_greedy`，`quantize=None`。

**实测发现：held-out accuracy 不是 submodular，CELF 的懒惰性在这里是错的。**
CELF 的正确性依赖 d_e(S) 随 S 增大不增；accuracy 有特征交互，增益会变大，
于是一个"陈旧"的堆键会**低估**当前增益，该候选就再也不会被翻上来。
直接调用 `lazy_greedy(F, ground, 7)` 时，它选出的元素与真正的 argmax 在 7 步里
有 3 到 6 步不一致（四个数据集都如此，见 `E1_diagnostics.csv` 的 `celf_agree_steps_*`）。

处理方式（既守规则又不让科学出错）：轨迹改为**每步调用同一个 `lazy_greedy(..., K=1)`**
（作用在状态平移视图 `_Shift` 上，共用同一个 `CachedSetFunction` 缓存）。
CELF 的第 1 轮本来就是全扫描，所以 K=1 的调用返回的是精确 argmax；
代码里再用 `assert F.gain(base, pick) >= max_e F.gain(base, e) - 1e-12` 逐步验证。
因为"每个轨迹状态记录所有候选的 (d, d̃)"这一要求本来就要把所有候选算一遍，
全扫描不增加任何评估成本（缓存命中）。
同时仍然跑一遍朴素的 `lazy_greedy(F, ground, 7)` 作为诊断，把它的轨迹一致步数和
realized ratio 写进 `E1_diagnostics.csv`（`celf_agree_steps_ftilde/f`、`celf_ratio_K7`）。

这条也是给 E2/E3 的提醒：只要 f 不是 submodular，CELF 就不是"加速"，是换算法。

## 6. ratio 的分母

ratio 的分母是同一管线、同一缓存结构下的**真值 greedy** f(S^f_K)，不是 OPT。
对 monotone submodular 的 f，greedy ≤ OPT，所以这个 ratio 是对
f(S^{f̃})/f(OPT) 的**上估**（分母偏小）。
本任务的 f 还不是 submodular，greedy-on-f 甚至不一定是同预算下最好的子集，
所以 ratio > 1 会实际发生（见 §7），上估这一点只会更严重。
所有出现 ratio 的地方都按"OPT 上估代理"读。

## 7. 结果：中位数表（每格 30 个 seed）

`E1_rows.csv` 共 4 dataset × 7 K × 30 seed = 840 行。

### K = 7

| dataset | ratio 中位数 | ratio IQR | ratio min | η^sel 中位数 | η^sel max | η^path 中位数 | η^path max | 方向违反 % 中位数 | L_7(η^sel) 中位数 | L_7(η^path) 中位数 |
|---|---|---|---|---|---|---|---|---|---|---|
| airline | 0.9990 | [0.9979, 1.0002] | 0.9942 | 1.548 | 5.375 | 26.51 | 204.0 | 10.08 | 0.4923 | 0.0371 |
| breast_cancer | 0.9550 | [0.9399, 0.9730] | 0.8818 | 2.000 | 7.000 | 12.25 | 50.0 | 32.35 | 0.4047 | 0.0789 |
| wine | 0.9444 | [0.9167, 0.9712] | 0.8529 | 1.375 | 4.000 | 10.12 | 48.8 | 26.82 | 0.5380 | 0.0951 |
| digits20 | 0.9585 | [0.9234, 0.9851] | 0.8465 | 2.905 | 19.00 | 51.57 | 267.1 | 23.53 | 0.2989 | 0.0192 |

### K = 1 / 3 / 5（同格式，节选中位数）

| dataset | K | ratio | η^sel | η^path | viol% | L_K(η^sel) |
|---|---|---|---|---|---|---|
| airline | 1 | 1.0000 | 1.000 | 2.10 | 0.00 | 1.0000 |
| airline | 3 | 1.0000 | 1.000 | 12.06 | 7.75 | 0.7037 |
| airline | 5 | 0.9979 | 1.280 | 17.88 | 6.42 | 0.5725 |
| breast_cancer | 1 | 0.9615 | 1.141 | 4.10 | 16.67 | 0.8767 |
| breast_cancer | 3 | 0.9725 | 1.369 | 12.25 | 26.32 | 0.5669 |
| breast_cancer | 5 | 0.9631 | 2.000 | 12.25 | 32.56 | 0.4095 |
| wine | 1 | 0.9815 | 1.033 | 6.36 | 15.38 | 0.9688 |
| wine | 3 | 0.9437 | 1.225 | 10.12 | 20.61 | 0.6145 |
| wine | 5 | 0.9444 | 1.375 | 10.12 | 22.66 | 0.5464 |
| digits20 | 1 | 1.0000 | 1.000 | 2.94 | 0.00 | 1.0000 |
| digits20 | 3 | 0.9709 | 1.504 | 19.47 | 14.44 | 0.5284 |
| digits20 | 5 | 0.9674 | 1.774 | 36.14 | 19.14 | 0.4502 |

一句话读法：**实测 ratio 在 0.94 到 1.00 之间，认证下界 L_K(η^sel) 在 0.30 到 0.54，
实测点远在理论曲线上方**（这正是 E5 money plot 想展示的图景）。
airline 上 f̃ 几乎无害：K ≤ 3 时 30/30 个 seed 的 η^sel = 1（f̃ 选的就是真值 argmax），
K=7 时 ratio 中位数 0.9990。

## 8. 诚实报告的几件事

1. **ratio > 1 会发生**：K=7 时 airline 8/30、digits20 4/30、wine 1/30 个 seed 的
   ratio > 1（breast_cancer 0/30）。因为 f 不是 submodular，greedy-on-f 只是启发式，
   不是同预算最优，被 greedy-on-f̃ 超过完全可能。分母是"greedy on f"不是 OPT。
2. **分母到底高估多少**（暴力枚举 OPT，`--part opt_check`）：
   wine K=7、seeds 0..9：median f(greedy^f)/OPT = 0.9722（min 0.9167），
   median f(greedy^f̃)/OPT = 0.9444（min 0.8611）；
   airline K=3、seeds 0..4：两者都是 0.9819（min 0.9764），即两条轨迹选到同一个集合。
   所以"用 greedy-on-f 当 OPT 代理"在这些任务上把 ratio 抬高了约 2%–3%。
   airline K=7 的 OPT 需要枚举 C(22,7)=170544 个子集，没做，标注为未测。

   **附注（TASKS4 F1.4，2026-09-01 补测）：breast_cancer 的暴力 OPT。**
   脚本 `results/E1_run.py --part opt_bc --opt-k 4`，输出 `results/E1_opt_breast_cancer.csv`
   （10 seeds × K=1..4 每行一条，含 OPT、两条 greedy 的 f 值与两个比值）。
   f 与正文完全同一个：80/20 划分上的决策树 held-out accuracy，过同一个 frozenset 缓存。

   | K | 枚举子集数 | median f(greedy^f)/OPT | min | median f(greedy^f̃)/OPT | min |
   |---|---|---|---|---|---|
   | 1 | 30 | 1.0000 | 1.0000 | 0.9659 | 0.9065 |
   | 2 | 435 | 1.0000 | 0.9727 | 0.9726 | 0.9364 |
   | 3 | 4,060 | 0.9820 | 0.9640 | 0.9591 | 0.9273 |
   | **4** | **27,405** | **0.9823** | 0.9554 | 0.9464 | 0.9115 |

   即 breast_cancer 上"greedy-on-f 当 OPT 代理"把 ratio 抬高约 1.8%（K=4 中位数 0.9823），
   与 wine K=7 的 0.9722 同量级，方向一致：分母偏小、报出的 ratio 是上估。

   **为什么是 K=4 而不是 K≤5**：先估时（同一台机器、与 E2/E1 主跑并行占核）得到约 394 次
   f 评估/秒，K=1..5 共需 C(30,1..5) = 174,436 次/seed，10 个 seed 约 74 分钟，超过 TASKS4
   给的 30 分钟上限；降到 K=4（31,930 次/seed）实测每 seed 75–109 秒、10 个 seed 共
   约 13.6 分钟。**K=5 的 OPT 没有测，任何地方都不要报 K=5 的 OPT 比值。**
3. **d ≤ 0 的步**（chosen 的真实增益非正，按 statistics.py 从 η^sel 的 max 中剔除并计数）：
   K=7 的 210 步里，airline 0 步、digits20 17 步、breast_cancer 98 步、wine 109 步。
   小数据集上"加一个特征反而掉 accuracy"是常态，这一点必须写进论文，不能只报 η。
4. **候选对里非正增益的比例**（`E1_pairs.csv.gz`，全部 15330 对）：
   d ≤ 0 的比例 airline 34.5%、digits20 34.9%、breast_cancer 55.2%、wine 55.6%；
   d̃ ≤ 0 的比例 38.2% / 31.0% / 70.9% / 55.4%。
5. **方向一致性违反**（d 与 d̃ 严格反号，在 |d| ≥ ε 或 |d̃| ≥ ε 的对里统计）：
   K=7 中位数 airline 10.1%、digits20 23.5%、wine 26.8%、breast_cancer 32.3%。
   全部候选对上的原始反号比例是 10.1% / 23.2% / 19.9% / 29.2%。
   这些违反几乎都发生在近零增益处（E5 的散点图会直接展示）。
6. **η^path 的 trimming**：ε = 1/n_test，只保留 d ≥ ε 且 d̃ ≥ ε 的对。
   被保留的对占全部候选对的比例：airline 57.9%、digits20 49.7%、wine 24.8%、
   breast_cancer 15.9%（breast_cancer 的 ε 相对大，剪掉的多）。
   即使 trim 过，η^path 仍然是 10–50 的量级，比 η^sel 大一个数量级以上：
   **η^path 在真实数据上不是一个有用的紧尺子**，η^sel 才是。这条结论建议写进论文。
7. **CELF 在这里不精确**（见 §5）：`celf_agree_steps_ftilde` 的中位数是 7 步里只有
   2–3 步与精确 argmax 一致（airline 中位数 3，breast_cancer 2，wine/digits20 3）。
   朴素 CELF 轨迹的 ratio 中位数（`celf_ratio_K7`）反而更高
   （airline 1.0015、digits20 1.0000、breast_cancer 0.9814、wine 0.9714），
   因为它同时"打乱"了分子和分母两条轨迹，这个数**不能**当作 predictive greedy 的性能，
   只作为"别用 CELF 跑非 submodular f"的证据。
8. **η^sel = 1 的比例**（f̃ 的选择与真值 argmax 完全一致的 seed 占比）：

| dataset | K=1 | K=2 | K=3 | K=4 | K=5 | K=6 | K=7 |
|---|---|---|---|---|---|---|---|
| airline | 1.000 | 1.000 | 1.000 | 0.833 | 0.300 | 0.133 | 0.067 |
| breast_cancer | 0.200 | 0.200 | 0.200 | 0.133 | 0.100 | 0.033 | 0.033 |
| digits20 | 0.533 | 0.100 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| wine | 0.500 | 0.300 | 0.300 | 0.300 | 0.300 | 0.300 | 0.300 |

  n_test 越大，f̃ 越接近 f：airline（n_test=5075）在 K ≤ 3 上 100% 一致，
  breast_cancer（n_test=114）只有 20%。这与 TASKS_EXP 备选项里
  "检验 η^sel 是否随 n_test 变小而降"的猜想方向一致（这里是反过来读：n_test 小 → η^sel 大）。

## 9. 基线对照（论文 Fig.1 的替代）

`E1_baselines.csv`：dataset × seed(0..9) × K(1..7) × method(6) 的 held-out accuracy。
四个基线从 legacy 移植：`SelectKBest(f_classif)`、`RFE(DecisionTree)`、
`mutual_info_classif`、`ExtraTreesClassifier` importances。
**与 legacy 的差别**：legacy 的下游分类器是 GBC，这里统一换成决策树，
使"基线选出的集合"和"greedy 选出的集合"用的是同一个 f，才是公平对照。
只跑 seed 0..9（10 个种子）控制时间，已注明。图：`figures/E1_baselines.png/.pdf`。

### airline（10 个 seed 的中位数 held-out accuracy）

| method | K=1 | K=2 | K=3 | K=4 | K=5 | K=6 | K=7 |
|---|---|---|---|---|---|---|---|
| greedy on f（真值，参照） | 0.7845 | 0.8510 | 0.8911 | 0.9229 | 0.9307 | 0.9403 | 0.9475 |
| **greedy on f̃** | 0.7845 | 0.8510 | 0.8911 | 0.9229 | 0.9285 | 0.9385 | 0.9458 |
| SelectKBest | 0.7845 | 0.8510 | 0.8510 | 0.8673 | 0.8836 | 0.8882 | 0.8965 |
| RFE | 0.7845 | 0.7488 | 0.7931 | 0.8491 | 0.8542 | 0.8924 | 0.8971 |
| Mutual Information | 0.7845 | 0.8167 | 0.8803 | 0.8991 | 0.9249 | 0.9281 | 0.9277 |
| Extra Trees | 0.6837 | 0.7720 | 0.8911 | 0.8991 | 0.9246 | 0.9347 | 0.9367 |

greedy on f̃ 在 K = 1..7 的**每一个** K 上都 ≥ 四个基线里最好的那个，
且与 greedy on f（真值上界代理）只差 0.002 左右。

### breast_cancer（10 个 seed 的中位数）

| method | K=1 | K=2 | K=3 | K=4 | K=5 | K=6 | K=7 |
|---|---|---|---|---|---|---|---|
| greedy on f（真值，参照） | 0.8860 | 0.9518 | 0.9561 | 0.9737 | 0.9649 | 0.9737 | 0.9737 |
| **greedy on f̃** | 0.8640 | 0.9254 | 0.9298 | 0.9298 | 0.9254 | 0.9342 | 0.9254 |
| SelectKBest | 0.8772 | 0.8947 | 0.9123 | 0.9167 | 0.9211 | 0.9211 | 0.9342 |
| RFE | 0.8509 | 0.9167 | 0.9386 | 0.9298 | 0.9342 | 0.9342 | 0.9211 |
| Mutual Information | 0.8640 | 0.8684 | 0.8640 | 0.9079 | 0.9211 | 0.9211 | 0.9211 |
| Extra Trees | 0.8640 | 0.8596 | 0.9079 | 0.9254 | 0.9211 | 0.9211 | 0.9079 |

breast_cancer 上 greedy on f̃ 只在 K ∈ {2,4,6} 上不劣于最好的基线，
K=1、3、5、7 上被 SelectKBest 或 RFE 略微超过（差 0.005–0.009，样本只有 114 行 held-out，
即 1 个量化单位是 0.0088，也就是说这些差距只有 1 个量化单位左右）。

**结论（诚实版）**：在样本量大的 airline 上，学出来的 surrogate + greedy 全面优于四个经典基线；
在 569 行的 breast_cancer 上，它与基线打平（互有胜负，差距在 1 个 accuracy 量化单位量级）。
不能写成"全面碾压"。

## 10. GBC 稳健性核对（seed 0）

`E1_gbc_seed0.csv`：把 estimator 从决策树换成 `GradientBoostingClassifier(random_state=42)`
（f 与 f̃ 同时换），只跑 seed = 0，只跑 wine / breast_cancer / airline。

| dataset | K=7 ratio (GBC) | K=7 ratio (DT) | η^sel (GBC) | η^sel (DT) | viol% (GBC) | viol% (DT) |
|---|---|---|---|---|---|---|
| airline | 0.99958 | 0.99772 | 1.24 | 1.355 | 12.00 | 10.32 |
| breast_cancer | 0.99099 | 0.95455 | 3.00 | 6.00 | 29.33 | 44.17 |
| wine | 0.97143 | 1.00000 | 1.50 | 1.50 | 15.79 | 34.04 |

一句话对比：**换成 GBC 结论不变**，ratio 仍然贴近 1、η^sel 仍然是个位数，
GBC 甚至更"好"一点（f 更平滑，f̃ 追踪得更准，breast_cancer 上 η^sel 从 6 降到 3、
方向违反从 44% 降到 29%）；所以论文里"典型实例远离最坏情况"的结论不依赖模型选择。

`digits20` 没跑 GBC：10 类 × 100 轮的 GBC 在这份数据上单次 5-fold CV 实测 8.7 秒，
整条轨迹需要约 120 次 f̃ 评估，单是这一个数据集就要 20 分钟以上，
按原则 5 的时间控制跳过并在此注明（不是失败，是主动取舍）。

## 11. 隔离探针的实测值

`check_isolation()` 在每个数据集的第一个 seed 上跑，输出
`(f̃ 置换前, f̃ 置换后, f 置换前, f 置换后)`：

| dataset | f̃ before | f̃ after | f before | f after | 判定 |
|---|---|---|---|---|---|
| wine | 0.6689655172413793 | 0.6689655172413793 | 0.8611 | 0.2222 | f̃ 逐位不变，f 变了 |
| digits20 | 0.26860481997677116 | 0.26860481997677116 | 0.2167 | 0.0972 | 同上 |
| breast_cancer | 0.8813186813186814 | 0.8813186813186814 | 0.8947 | 0.4912 | 同上 |
| airline | 0.6430049261083743 | 0.6430049261083743 | 0.6463 | 0.5111 | 同上 |

四个数据集全部通过：把 held-out 标签彻底打乱之后 f̃ 的值一位都没动，
而 f 的值大幅下降（说明探针确实作用在被使用的数据上，不是空转）。
加上 §4 的四层结构性断言，**旧 oracle 的信息泄露路径在这套代码里不存在**。

## 12. 运行方式与耗时（原则 5）

实际按数据集分两块跑，CSV 增量写（第二块加 `--append`），全部实际运行完成：

```
python results/E1_run.py --datasets wine,digits20,breast_cancer --seeds 0:30 --part main   # 323 s
python results/E1_run.py --datasets airline --seeds 0:30 --part main --append              # 497 s
python results/E1_run.py --part gbc --datasets wine,breast_cancer,airline                  # 925 s
python results/E1_run.py --part baselines_fig                                              #   1 s
python results/E1_run.py --part opt_check                                                  # 177 s
python results/E1_run.py --part summary                                                    #   1 s
```

合计约 32 分钟单进程 CPU（4 核机器上另有两个任务并行，脚本本身不开进程池）。
没有任何一步超过 30 分钟，因此**没有降过样本量**：airline 用的是清洗后全部 25375 行。
`--datasets`/`--seeds`/`--append` 支持任意分块；`python results/E1_run.py` 不带参数
就是一键从头跑全部（main + gbc + 图 + summary）。

每个数据集每个 seed 的耗时中位数：airline 12–28 s（含基线）、breast_cancer 4–6 s、
digits20 4 s、wine 1.4 s。f 的评估次数中位数约 180–380 次/seed，
f̃ 约 71–195 次/seed（都算缓存后的实际评估数）。

## 13. 诚实声明（列全进表）

- 没有任何人工扰动 oracle。f̃ 是真的从训练集上学出来的 5-fold CV accuracy，
  与 f 的差异完全来自"训练集 CV 估不准 held-out accuracy"这一真实现象。
- ratio 的分母是 greedy on f，不是 OPT，是**上估**；实测高估幅度见 §8 第 2 条。
- d ≤ 0 的步数、候选对里 d ≤ 0 / d̃ ≤ 0 的比例、方向违反比例、trim 掉的比例、
  ε 的取值，全部在 §8 与 CSV 里，没有隐藏。
- CELF 在这个非 submodular 的 f 上不精确，这一点被测量、被报告、被绕开（§5），
  不是"假装没发生"。
- breast_cancer 上 greedy-on-f̃ 并没有稳定赢过四个经典基线（§9），照实写。
- η^path 在真实数据上比 η^sel 大一个数量级以上，对应的 L_K(η^path) 中位数只有
  0.02–0.10，也就是说**用 η^path 做认证下界在真实任务上几乎没有信息量**；
  这是本任务对论文最有用的一条负面结论。
- 未做：airline K=7 的暴力 OPT（C(22,7)=170544）；digits20 的 GBC 核对；
  openml adult（TASKS_EXP 的备选项，时间未到）。

## 14. 给 E5 的接口

`results/E1_pairs.csv.gz`：列 `dataset, seed, step, d, dtilde, chosen`，
15330 行 = 4 dataset × 30 seed × Σ_{t=0..6}(n_features − t)，其中 840 行 `chosen=1`。
`step` 是 0-based 的轨迹步号（0 表示从空集出发那一步）。
`d` 是 held-out 真值边际增益，`dtilde` 是 5-fold CV 边际增益，两者都可能 ≤ 0。
画散点时建议画 |d| 与 |d̃| 的 log-log 并把 ε = 1/n_test 的十字带标出来，
方向违反的点（d 与 d̃ 反号）会集中在原点附近的十字带里。

`results/E1_rows.csv`：统一行格式，task='E1'，
dataset ∈ {airline, breast_cancer, wine, digits20}，K=1..7 × seed=0..29 每组一行。
2026-09-01（TASKS4 F1.3）起末尾多两列 `n_steps_nonpos` 与 `frac_steps_nonpos`
（前 K 步里被选中真实增益 d_t ≤ 0 的步数与占比；η^sel 与 `LK_eta_sel` 只在 d_t > 0 的步上定义，
所以 `LK_eta_sel` 报的保证是"对正增益步成立"，其余步的比例就是这一列）。
K=7 的 `frac_steps_nonpos` 中位数：airline 0.000、digits20 0.000、breast_cancer 0.4286、
wine 0.5714。该次重跑（`--part main`，全部 4 dataset × 30 seed）与旧文件的
ratio / eta_sel / eta_path_trimmed / viol_sign_pct / LK 两列**逐行完全一致**（840 行 0 处不同），
新增的只有这两列。

`results/E1_opt_breast_cancer.csv`（TASKS4 F1.4）：列
`dataset, seed, K, opt, f_greedy_f, f_greedy_ftilde, greedy_f_over_opt, greedy_ftilde_over_opt`，
40 行 = 10 seed × K=1..4，OPT 为暴力枚举。
