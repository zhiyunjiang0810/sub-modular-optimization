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
用来核对结论对模型族的稳健性（§8）。论文正文写的是决策树，legacy 脚本用 GBC，与论文不符，
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

1. `df.drop(["Unnamed: 0", "id"], axis=1)` —— 照搬。
2. `df["Arrival Delay in Minutes"].fillna(mean)` —— 照搬（全列均值，83 个缺失）。
3. `df.sample(n=1000, random_state=42)` —— **删除**（任务要求全量）。
4. `LabelEncoder` 编码 `Gender, Customer Type, Type of Travel, Class, satisfaction` ——
   照搬（legacy 复用同一个 `le` 对象逐列 `fit_transform`，等价于每列独立编码）。
5. 异常值剔除，三条固定阈值，照搬且顺序一致：
   `Flight Distance > 3736.5`（全量剔除 596 行）、
   `Departure Delay in Minutes > 800`（3 行）、
   `Arrival Delay in Minutes > 650`（2 行）。
   合计 25976 → 25375 行。
   注意：这三个阈值在 legacy 里是在 1000 行样本上定的，我们按任务要求"沿用清洗步骤"
   把它们当作固定阈值用在全量数据上（不重新按全量 IQR 计算）。
6. `StandardScaler` 循环 —— **跳过**，两个理由：
   (a) legacy 里这段是 no-op —— 它的判断条件是 `df[column].dtype == type(float)`，
       而 `type(float)` 是 `type`，pandas dtype 永远不等于它，所以没有任何一列被缩放；
   (b) 即使执行，逐列的 standardize 是单调仿射变换，决策树/GBC 对此不变，accuracy 不变。
7. `X = df.drop(columns=['satisfaction'])`, `y = df['satisfaction']` —— 照搬，22 个特征。

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
四个数据集的探针结果见 §7 诊断表下方。

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
