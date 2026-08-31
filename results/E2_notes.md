# E2 notes — Influence maximization，部分观测图作 surrogate

脚本：`results/E2_run.py`（全部结果由该脚本实际运行产生，2026-08-31）。
共享管线：`src/im_graph.py`（Graph / coverage / CachedSetFunction / lazy_greedy / true_max_gain）
与 `src/statistics.py`（TrajectoryStats / unified_row / L_K）。未修改 `src/`、`data/` 或其他任务文件。

## 1 设定

- `f(S)` = 真图上的一跳覆盖 `|{v : v ∈ S 或 v 被 S 指到}|`（`Graph.coverage`；无向图在 `Graph.__init__`
  中已按双向存边，因此"出邻居"即全部邻居）。
- `f̃(S)` = 同一公式，算在**观测图**上：真图每条输入边以概率 p 独立保留（`Graph.edge_subsample`，
  无向边整条保留或丢弃），p ∈ {0.3, 0.5, 0.8}，每个 p 取 20 个观测图，seed = 0..19。
  f̃ 只用观测图，不接触真图，符合原则 1（**无任何人工扰动 oracle**，没有 d̃ = d·exp(X) 这类构造）。
- K = 1..30：每个 (dataset, p, seed) 只跑一条 K=30 的 greedy-on-f̃ 轨迹，30 个前缀各出一行。
- ratio = f(greedy^f̃ 的前 K 个) / f(greedy^f 的前 K 个)。分母对每个 dataset 只算一次并缓存复用。
- greedy 一律 CELF lazy（`lazy_greedy`，真实数据 `quantize=None`），f 与 f̃ 的每次取值都过
  `CachedSetFunction`（key = frozenset）。
- η^path 的 ε = **1**（覆盖计数的量化单位）。

## 2 数据集与实际规模（未做节点截断）

原 Twitter / reddit / Facebook_1 / Facebook_2 已丢失（见 `data/INVENTORY.md`），按指派使用替代图，
`dataset` 列写实际名称：

| dataset | 文件 | 有向 | n | m（输入边数） | f(greedy^f, K=30) | 单 run 耗时 |
|---|---|---|---|---|---|---|
| `email_eu_core` | `data/graphs/email_eu_core/email-Eu-core.txt` | 是 | 1,005 | 25,571 | 831 | 0.4 s |
| `facebook_politician` | `.../facebook_gemsec/politician_edges.csv` | 否 | 5,908 | 41,729 | 2,794 | 0.2 s |
| `facebook_government` | `.../facebook_gemsec/government_edges.csv` | 否 | 7,057 | 89,455 | 3,827 | 0.3 s |
| `facebook_artist` | `.../facebook_gemsec/artist_edges.csv` | 否 | 50,515 | 819,306 | 15,777 | 3.2 s |

**规模控制的实际决定：没有触发任何节点截断。** 按要求先在 `email_eu_core` 上跑通全流程，再对
`facebook_artist` 做单 (p=0.5, seed=0) 估时（`--mode probe`）：load 3.4 s + subsample 2.6 s +
单条 K=30 轨迹 0.9 s，远低于 3 分钟阈值，因此**未**截到 top-20,000 诱导子图，`dataset` 名保持
`facebook_artist`（脚本保留 `--top-nodes` 与 `induced_top_degree`，若日后需要可用
`--top-nodes 20000 --label facebook_artist_top20k`；本次未使用）。
seeds 也未降规模：每个 (dataset, p) 都跑满 20 个观测图种子，合计 4 × 3 × 20 = **240 条轨迹，7,200 行**。
总运行时间约 6 分钟（email 约 30 s，politician + government 约 30 s，artist 约 3.5 min），
另加验证与截断校验约 3 分钟。

能不截断的原因是把每次边际增益做成了 O(deg)（下节），而不是降低了任何定义的精度。

## 3 两法一致性验证（`results/E2_validation.txt`，`--mode validate`）

η^sel 需要每步真图上的 `max_e d_e(S^t)`。按要求不做逐步全扫描，改用**真图上的第二个 CELF 式
惰性最大堆**（`LazyTop`）：coverage 是单调 submodular、S^t 沿轨迹单调增长，因此堆里的陈旧值恒为
上界，lazy 合法。同时用 `covered` 布尔数组（`CoverageState`）做 O(deg) 的增量增益。

在 `email_eu_core` 上对 p ∈ {0.3,0.5,0.8} × seed ∈ {0,1} 共 6 条 K=30 轨迹，逐步对比：

- `max |lazy 堆给的 dmax − im_graph.true_max_gain 全扫描给的 dmax| = 0`（6/6 条轨迹，全部 30 步）；
- `max |增量 coverage − Graph.coverage| = 0`；
- `max |增量 gain − CachedSetFunction.gain| = 0`；
- 用 O(deg) 快速取值函数跑出的 greedy 轨迹与用朴素 `Graph.coverage` 跑出的轨迹**逐元素相同**。

另在 `facebook_politician`（p=0.5, seed=0）前 8 步再做一次堆 vs 全扫描对比，差值同样为 0。
结论：加速结构与共享管线的朴素实现给出的是同一批数字，加速只影响耗时。

## 4 (d, d̃) 落盘的截断，以及它对 η^path 的影响（重要）

- 大图（三个 facebook 图）：每步只保留 **top-50 d̃ 候选**的 (d, d̃)；`statistics.TrajectoryStats`
  的 η^path 与 viol% 也**只在这 50 对上**计算。`email_eu_core` 用**全部候选**（每步约 1,000 对）。
- 落盘文件 `E2_pairs_sample.csv.gz`：三个 facebook 图全部 60 条轨迹各步 top-50；`email_eu_core`
  的 seed 0/1/2 落全部候选，seed ≥ 3 只落 top-50（统计仍用全候选）。共 613,935 行。

截断会**系统性低估 η^path**，这一点用 `--mode trunccheck` 直接量了出来
（`results/E2_truncation_check.csv`：对若干 run 用全候选重算 K=30 的 η^path，再与 top-50 限制值对比）：

| dataset | top50 / full 的比值范围（K=30） |
|---|---|
| `email_eu_core` (6 runs) | 0.27 – 0.40 |
| `facebook_politician` (6 runs) | 0.043 – 0.272 |
| `facebook_government` (6 runs) | 0.098 – 0.365 |
| `facebook_artist` (3 runs) | 0.002 – 0.163 |

例：`facebook_artist` p=0.8 seed=0 的全候选 η^path = 678，top-50 限制值只有 1.62（0.002 倍）。
所以：**`E2_rows.csv` 中三个 facebook 图的 `eta_path_trimmed` 是下估，只能当作"轨迹上高 d̃ 候选之间的
误差尺度"读，不能当作全候选 η^path。`email_eu_core` 的 `eta_path_trimmed` 是全候选值，未被截断。**
E5 若要用 η^path 作横轴，建议只用 email 的列，或用 `E2_truncation_check.csv` 的全候选值。
η^sel 不受此截断影响（它只用真值的 max，来自真图上的完整堆）。

校验：`email_eu_core` 的 6 个 trunccheck 全候选 η^path 与 `E2_rows.csv` 里对应行完全相等；
21 行 trunccheck 的 η^sel 与 `E2_rows.csv` 对应 run 完全相等（0 处不一致）。

## 5 统一行格式与新增的 p 列

`E2_rows.csv` 的前 10 列就是 `src/statistics.py` 的 `ROW_FIELDS`
（task, dataset, K, seed, ratio, eta_sel, eta_path_trimmed, viol_sign_pct, LK_eta_sel, LK_eta_path），
由 `unified_row` 生成；`seed` = 观测图种子。因为共享格式里没有 p，而 E2 必须区分 p，
在**末尾追加了一列 `p`**（dataset 列保持真实数据集名，未把 p 编进名字）。
用 `csv.DictReader` 或 pandas 读取时，前 10 列与其他任务完全对齐，多出的 `p` 列对其他任务为空。

## 6 对照基线（`E2_baselines.csv`：dataset, method, p, seed, K, f_value；f_value 一律是真图上的 f）

- `greedy_f`：真图上的完整信息 greedy，即 ratio 的分母（p、seed 列留空，每 dataset 一条 K=1..30）。
- `degree_obs`：**按观测图的出度排序取 top-K**，再在真图上算 f。选观测图度数而不是真图度数，
  是因为这是"无预测"基线，它只应使用与 f̃ 相同的可得信息（真图度数是不可得的，用它会让基线偷看
  ground truth）。因此该基线对每个 (p, seed) 各有一条（3 × 20 = 60 条 / dataset）。
- `random`：固定种子 `random.Random(10000+r)`，r = 0..9，各取 30 个节点的随机前缀，10 次全部落盘
  （取平均在分析端做）。

K=30 的对照结果（f 归一到 `greedy_f`，中位数）：

| dataset | pred. greedy p=0.3 | p=0.5 | p=0.8 | degree_obs (p=0.5) | random (10 次均值) |
|---|---|---|---|---|---|
| email_eu_core | 0.945 | 0.963 | 0.989 | 0.889 | 0.541 |
| facebook_artist | 0.963 | 0.988 | 0.997 | 0.794 | 0.062 |
| facebook_government | 0.882 | 0.940 | 0.990 | 0.660 | 0.182 |
| facebook_politician | 0.899 | 0.942 | 0.988 | 0.679 | 0.156 |

即使只看到 30% 的边，用观测图做 surrogate 的 greedy 仍然稳定优于观测图度数排序（0.88–0.96 vs
0.66–0.89），random 远远落后。

## 7 p 与 η 的经验关系（`E2_p_eta.csv`，K=30，20 个观测图种子）

| dataset | p | η^sel 中位数 | η^sel IQR | ratio 中位数 | L_30(η^sel 中位数) |
|---|---|---|---|---|---|
| email_eu_core | 0.3 | 10.00 | 1.88 | 0.945 | 0.095 |
| email_eu_core | 0.5 | 6.50 | 4.13 | 0.963 | 0.143 |
| email_eu_core | 0.8 | 2.25 | 0.75 | 0.989 | 0.361 |
| facebook_politician | 0.3 | 20.60 | 20.83 | 0.899 | 0.047 |
| facebook_politician | 0.5 | 11.67 | 10.50 | 0.942 | 0.082 |
| facebook_politician | 0.8 | 1.89 | 0.28 | 0.988 | 0.413 |
| facebook_government | 0.3 | 124.00 | 119.44 | 0.882 | 0.008 |
| facebook_government | 0.5 | 11.78 | 13.68 | 0.940 | 0.082 |
| facebook_government | 0.8 | 1.42 | 0.11 | 0.990 | 0.510 |
| facebook_artist | 0.3 | 3.84 | 216.43 | 0.963 | 0.230 |
| facebook_artist | 0.5 | 1.57 | 0.10 | 0.988 | 0.476 |
| facebook_artist | 0.8 | 1.19 | 0.12 | 0.997 | 0.573 |

- 趋势在四个图上一致且单调：**p 越小，η^sel 越大，ratio 越低**。四个图从 p=0.8 到 p=0.3，
  η^sel 中位数上升 3.2 倍（artist）到 87 倍（government）。
- 但 ratio 的下降远比 η^sel 的上升温和：η^sel 中位数跨越 1.19 → 124（两个数量级），
  实测 ratio 只从 0.997 掉到 0.882。相应的认证下界 L_30(η^sel) 从 0.57 掉到 0.008，
  也就是说**在真实实例上，认证下界比实际表现悲观 2 个数量级**。这正是 E5 想要的"何时重要"的展品：
  η 在部分观测下确实会变得很大，但典型实例远没有触到最坏情形。
- 尾部很重，不要只看中位数：`facebook_artist` p=0.3 的 20 个种子里，9 个的 η^sel > 10（最大 456），
  其余 11 个在 2.1–4.9，所以中位数 3.84 而 IQR 高达 216。`facebook_government` p=0.3 则是 20/20 都 > 10。
  η^sel 由单步的 `max_e d_e / d_chosen` 决定，只要有一步 greedy-on-f̃ 挑中一个"真图上邻域已被覆盖"
  的高度数节点，比值就会跳到几百。诊断示例（government, p=0.3, seed=0, 第 3 步）：被选中的节点真图度数
  697，但真实边际只有 25，而当步真图最大边际是 272，单这一步就贡献 η^sel = 10.9。
- η^sel 随 K 的形状：几乎全部增长发生在前几步，例如 government p=0.3 的中位 η^sel 在 K=1 是 1.02，
  K=5 已经是 124，之后到 K=30 不再变化。

图：`figures/E2_p_eta.png` / `.pdf`（左：η^sel 中位数 + IQR 带 vs p，对数纵轴；中：ratio vs p；右：K=30 基线对比）。

## 8 诚实声明

1. **ratio 的分母是 greedy-on-f，不是 OPT。** greedy 本身只有 1−1/e 保证，所以这里的 ratio 是对真实
   竞争比的**上估**（分母偏小时 ratio 偏大）。全部表格与图都按此口径读。
2. **ratio > 1 会出现。** 7,200 行里有 93 行（1.3%）ratio > 1，最大 1.0087，全部出现在 K = 4..20；
   K=30 时 240 条 run 无一超过 1。原因同上：观测图 greedy 偶尔在中间前缀上比真图 greedy 更好，
   这不是 bug，也不违反任何定理。
3. **viol_sign_pct 在全部 7,200 行都是 0.00，这是结构性的，不是"零违反"的实验发现。**
   f 与 f̃ 都是覆盖函数，边际增益恒 ≥ 0，观测图是真图的子图，所以 (d, d̃) 不可能异号。
   方向一致性违反这条尺子在 E2 上没有信息量，要看它请用 E1/E3。
4. **d ≤ 0 的步：240 条轨迹、7,200 步里出现 0 次**（每一步被选中节点的真实边际至少是 1，即它自己）。
   因此 `TrajectoryStats` 的非正增益剔除逻辑在 E2 上没有实际启用。
5. **三个 facebook 图的 η^path 被 top-50 截断低估**，量化见第 4 节；email 的 η^path 未截断。
6. η^sel 用真值 max，来自真图上的完整惰性堆，未做任何候选截断，且与全扫描逐点相等（第 3 节）。
7. 无人工扰动 oracle；f 与 f̃ 均缓存；greedy 为 CELF lazy 且 `quantize=None`；观测图种子固定为 0..19；
   随机基线种子固定为 10000..10009；图同时存 PNG 与 PDF。
8. p 是"每条边独立保留"的爬取模型，不是 IC/LT 传播模型；一次 (p, seed) 对应"平台的一次不完整爬取"。
   真实爬取的缺失通常不是均匀独立的（更可能按节点或社区成块缺失），本实验没有覆盖这种相关缺失。
9. `facebook_*` 三个图是 GEMSEC page-page 网络（无向），`email_eu_core` 是有向图；原稿的
   Twitter/reddit 图已丢失，数字不可与原稿逐一对齐（见 `data/INVENTORY.md`）。

## 9 产出文件与复现命令

产出（全部实际运行生成）：

- `results/E2_run.py`（支持 `--dataset --p --seeds` 分块、断点续跑：已在 `E2_rows.csv` 里的
  (dataset, p, seed) 自动跳过；写盘一律追加）
- `results/E2_rows.csv`（7,200 行 = 240 run × K=1..30；统一行格式 + 末列 p）
- `results/E2_pairs_sample.csv.gz`（613,935 行：dataset, p, seed, step, element, d, d_tilde）
- `results/E2_baselines.csv`（8,520 行：greedy_f / degree_obs / random）
- `results/E2_p_eta.csv`（12 行：dataset × p 的 η^sel 中位数、四分位、IQR、ratio、L_30）
- `results/E2_truncation_check.csv`（21 行：top-50 截断对 η^path 的偏差）
- `results/E2_validation.txt`（两法一致性验证输出）
- `results/E2_notes.md`（本文件）
- `figures/E2_p_eta.png` / `figures/E2_p_eta.pdf`

复现：

```bash
python3 results/E2_run.py --mode validate                                   # 两法一致性
python3 results/E2_run.py --mode probe --dataset facebook_artist --p 0.5 --seeds 0   # 估时
python3 results/E2_run.py --mode run --dataset email_eu_core --p all --seeds 0-19
python3 results/E2_run.py --mode run --dataset facebook_politician,facebook_government --p all --seeds 0-19
python3 results/E2_run.py --mode run --dataset facebook_artist --p all --seeds 0-19
python3 results/E2_run.py --mode trunccheck --dataset facebook_politician,facebook_government --p all --seeds 0,1
python3 results/E2_run.py --mode trunccheck --dataset facebook_artist --p all --seeds 0
python3 results/E2_run.py --mode trunccheck --dataset email_eu_core --p all --seeds 0,1
python3 results/E2_run.py --mode aggregate                                  # E2_p_eta.csv
python3 results/E2_run.py --mode figures                                    # figures/E2_p_eta.*
```

（`--mode run` 会自动跳过 `E2_rows.csv` 中已有的 run；要重跑请先移走该文件，
`E2_pairs_sample.csv.gz`、`E2_baselines.csv`、`E2_truncation_check.csv` 同为追加写。）
