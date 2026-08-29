# T6 — 真实 surrogate 的 η^path 测量（feature selection，对应审稿意见 R2-2）

状态：实证测量（非数学断言，不适用 VERIFIED-* 标签体系）。所有数字可由
`results/T6_eta_path.py`（主实验）与 `results/T6_argmax_diagnostic.py`（机制诊断）
一键复现；原始数据 `results/T6_eta_path.csv`（630 行 = 3 数据集 × 30 splits × K=1..7），
图 `figures/T6_eta_path_distribution.png`、`figures/T6_ratio_vs_bound.png`。

## 实验设置

- Ground set = 特征集合；f(S) = DecisionTreeClassifier(random_state=0, 其余默认)
  在 80% 训练集的特征子集 S 上训练、在 held-out 20% 上的 accuracy。
  f̃(S) = 同一模型在训练集上的 5-fold CV accuracy（cross_val_score 均值，
  StratifiedKFold(5) 不 shuffle，确定性）。两者均在 split 内用 dict（key = frozenset）memo 缓存。
- f(∅) = 训练集多数类在测试集上的频率；f̃(∅) = 训练集多数类在训练集上的频率
  （等价于 DummyClassifier(most_frequent) 的 accuracy；直接按频率计算）。
- 数据集：breast_cancer（30 特征）、wine（13 特征）、digits 前 20 个像素特征（记 digits20）。
  **openml airline satisfaction 跳过：环境网络受限（agent proxy），按任务说明记录。**
- split：train_test_split(test_size=0.2, stratify=y, random_state=0..29)，30 次。
- Predictive greedy on f̃，一条 K=7 轨迹（含全部前缀）；tie 打破取最小特征编号；
  即使最优预测增益 ≤ 0 也继续选满预算（与论文算法一致）。每个轨迹状态 S^t
  对所有剩余候选 e 记录 (d_e(S^t), d̃_e(S^t))。Oracle greedy on f 用同样机制。
- η_u^path = max d/d̃，η_o^path = max d̃/d，η^path = η_u·η_o，只在 d > tol 且 d̃ > tol
  的对上取 max（tol = 1e-12，防浮点噪声）；d ≤ 0 或 d̃ ≤ 0 的对**排除出 η 计算但如实统计**
  （下表 frac 列）。方向不一致 = d 与 d̃ 严格反号（d > tol 且 d̃ < −tol，或反之）。
- ratio(K) = f(S̃_K)/f(S_K^oracle)（原始 accuracy 之比）；L_K = 1 − (1 − 1/(η^path(K)·K))^K
  用同一 split 同一 K 的实测 η^path。
- 全量运行约 5 分钟（4 核机器，单进程）。无 silent caps：三个数据集均为完整 30 splits。

## 主要数字（30 splits 的中位数，[q1, q3]）

| dataset | K | η^path | ratio | L_K(η^path) | frac d≤0 | frac d̃≤0 | frac 反号 |
|---|---|---|---|---|---|---|---|
| breast_cancer | 1 | 5.0 [3.1, 8.5] | 0.966 | 0.198 | 0.38 | 0.40 | 0.13 |
| breast_cancer | 3 | 36 [24, 72] | 0.964 | 0.028 | 0.41 | 0.48 | 0.23 |
| breast_cancer | 7 | 43 [25, 72] | 0.963 [0.944, 0.973] | 0.023 | 0.53 | 0.72 | 0.32 |
| wine | 1 | 7.0 [5.2, 18.5] | 0.944 | 0.142 | 0.08 | 0.08 | 0.08 |
| wine | 3 | 46 [26, 278] | 0.971 | 0.022 | 0.26 | 0.25 | 0.19 |
| wine | 7 | 60 [26, 294] | 0.941 [0.917, 0.971] | 0.017 | 0.52 | 0.55 | 0.17 |
| digits20 | 1 | 3.3 [2.2, 4.9] | 0.994 | 0.299 | 0.15 | 0.13 | 0.00 |
| digits20 | 3 | 70 [32, 157] | 0.974 | 0.014 | 0.25 | 0.23 | 0.12 |
| digits20 | 7 | 371 [152, 5551] | 0.957 [0.925, 0.980] | 0.003 | 0.29 | 0.31 | 0.26 |

η 的拆分（K=7 中位数）：breast_cancer η_u = 14.6、η_o = 3.1；wine η_u = 18.5、η_o = 2.5；
digits20 η_u = 31.5、η_o = 7.5。η_u（低估真实增益）系统性地大于 η_o。
完整逐 K 数据见 CSV。

## 发现

1. **η^path 在实践中很大**（K=7 中位数 43 / 60 / 371），且分布重尾（digits20 的 q3 达 5551）。
   对应的 L_K(η^path) 下界为 0.023 / 0.017 / 0.003，完全 vacuous。
2. **但实际表现极好**：ratio(K=7) 中位数 0.963 / 0.941 / 0.957，所有 (dataset, split, K)
   630 行里最差 0.718，且 9%-27% 的行 ratio ≥ 1（predictive greedy 不劣于 oracle greedy）。
   ratio ≥ L_K 在全部 630 行成立，但因下界接近 0，这不构成对定理的有效检验
   （且此处 f 不满足单调 submodular 前提，见发现 4）。
3. **η^path 被量化尺度的微小增益主导**（`T6_argmax_diagnostic.py`，90 个 (dataset, split)）：
   取到 η_u^path 的对，其分母 d̃ 的中位数恰为 1 个 CV 量化单位（1/n_train，
   三个数据集的中位数分别为 1.00 / 0.93 / 0.99 个单位）；取到 η_o^path 的对，
   其分母 d 的中位数恰为 1 个测试集量化单位（≈ 4/n_train，即 3.99 / 7.89 / 3.99 个
   1/n_train 单位）。即：η 的爆炸不是"大增益被预测错"，而是"接近零的增益之间的比值不稳定"。
   大增益（greedy 实际会选的那些）的预测排序基本正确，这正是 ratio 接近 1 的原因。
4. **方向一致性在实践中不成立，f 也不单调**：K=7 时 17%-32% 的候选对 d 与 d̃ 严格反号；
   29%-53% 的对 d ≤ 0（加特征降低 held-out accuracy），31%-72% 的对 d̃ ≤ 0。
   任何假设"d > 0 ⇔ d̃ > 0"或 f 单调的叙述都需要限定。

## 对论文叙事的建议（诚实版）

- 不能把这组数字讲成"实测 η 小所以界有意义"。相反，它支持的是论文"何时重要"判据的
  另一面：**raw multiplicative single-element error 对 ML surrogate 是过于悲观的度量**，
  因为它被近零增益的比值主导（发现 3）；在近零增益上乘性误差模型本身失效。
- 可以讲的实证故事：(a) predictive greedy 在真实 surrogate 上几乎不损失（ratio ≈ 0.94-0.96，
  经常 ≥ 1）；(b) 造成 η 大的对集中在一个量化单位内的增益，若论文引入
  additive-multiplicative 或 trimmed（忽略 |d̃| ≤ ε 的候选）误差变体，这组数据是直接动机；
  (c) 方向一致性失败率 17%-32% 是引入该讨论的实证依据。
- 局限（写论文时需声明）：oracle greedy 不是 OPT，ratio 是对强 baseline 的比值而非近似比；
  accuracy 作为 f 不单调也不 submodular；f̃（CV）与 f（held-out）同源相关，
  属于"好的 surrogate"情形；决策树 + 默认参数，未调参。

## 复现

```
cd results
python3 T6_eta_path.py               # 约 5 分钟：CSV + 两张图 + 聚合表 + sanity checks
python3 T6_argmax_diagnostic.py      # 约 4 分钟：机制诊断 JSON + stdout 汇总
```
Sanity checks（主脚本自动运行，本次全部通过）：ratio < L_K 的行数 = 0/630；
η^path = η_u·η_o 全行成立；min η^path = 1.78 ≥ 1（max-product 自动 ≥ 1）。
