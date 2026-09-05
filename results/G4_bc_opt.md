# G4.1 breast_cancer 暴力 OPT 扩到 K=5

状态：`[VERIFIED-EXHAUSTIVE]`（OPT_K 由 C(30,K) 全枚举得到，K = 1..5）。
第四晚 F1.4 只做到 K=4 并明确写了"K=5 的 OPT 没有测，任何地方都不要报 K=5 的 OPT 比值"
（`results/F1_fixes.md` 第 4 节）。本次把这一条补上。

一键复现：

```
python3 results/G4_bc_opt_K5.py            # 默认 --kmax 5 --seeds 10 --workers 4
```

产出：`results/G4_bc_opt_K5.csv`（50 行 = 10 seed x K=1..5，列与
`results/E1_opt_breast_cancer.csv` 完全一致）、`results/G4_bc_opt_K5.log`（含每 seed 的
OPT argmax 特征集合与两条 greedy 轨迹的 K=5 前缀）。

## 1 设置（与 E1 逐项相同）

| 项 | 取值 |
|---|---|
| f（真值） | 决策树 held-out accuracy，`E1_run.make_true_eval` + `make_tree`（`random_state=42`） |
| f̃（surrogate） | train-only 5-fold CV accuracy，`E1_run.make_surrogate` |
| split | `train_test_split(test_size=0.2, random_state=seed)`，455 train / 114 test |
| ground set | 30 个特征 |
| seeds | 0..9（与第四晚 F1.4 相同） |
| greedy | `E1_run.greedy_exact`，每步精确 argmax，与 E1 主管线同一函数 |
| 缓存 | `src/im_graph.CachedSetFunction`，frozenset 为键，K 小时算过的子集在大 K 复用 |

脚本用 `importlib` 载入 `results/E1_run.py` 调用其函数，没有改动 `results/E1_run.py`、
`src/`、`code/` 里的任何文件。与 `E1_run.py --part opt_bc` 的唯一差别是把 seed 分到进程池上跑
（每个 seed 的计算完全独立且确定性，`--workers 1` 复现串行顺序，输出逐位相同）。

## 2 耗时

- 每 seed 枚举 C(30,1)+...+C(30,5) = 174,436 个不同子集，实测每 seed 350-396 s。
- 单 worker 吞吐 471 次 f 评估/秒（第四晚估的 394 次/秒是在 E1/E2 主跑占核时测的）。
- 4 worker 并行跑 10 个 seed，**wall time 1107.6 s（18.5 分钟）**，远低于任务给的 6000 s 上限。
  第四晚"74 分钟"的估计是串行数，本次并行后不成立，这是 K=5 能补上的唯一原因。

## 3 自检：K <= 4 逐位复现第四晚

脚本内置对照，把本次 K <= 4 的行与 `results/E1_opt_breast_cancer.csv` 的 40 行逐格比较
（opt / f_greedy_f / f_greedy_ftilde / 两个比值，6 位小数）：

```
[G4.1] night-4 consistency: PASS (40 rows identical to E1_opt_breast_cancer.csv)
```

另外单独核对过：`greedy_ftilde_over_opt / greedy_f_over_opt` 与 `E1_rows.csv` 里
breast_cancer 同 (K, seed) 的 `ratio` 列最大差 1.3e-6（只是 6 位小数的舍入），
即本脚本的 f 和 E1 表格用的 f 确实是同一个。

## 4 结果

seeds 0..9，statistic 与第四晚一致（median，附 min）：

| K | 枚举子集数 | median f(greedy^f)/OPT | min | median f(greedy^f̃)/OPT | min |
|---|---|---|---|---|---|
| 1 | 30 | 1.0000 | 1.0000 | 0.9659 | 0.9065 |
| 2 | 435 | 1.0000 | 0.9727 | 0.9726 | 0.9364 |
| 3 | 4,060 | 0.9820 | 0.9640 | 0.9591 | 0.9273 |
| 4 | 27,405 | 0.9823 | 0.9554 | 0.9464 | 0.9115 |
| **5** | **142,506** | **0.9821** | **0.9643** | **0.9423** | **0.9196** |

K=5 的补充统计（10 个 seed）：

- f(greedy^f)/OPT：median **0.9821**，mean 0.9778，min 0.9643，max 0.9911，IQR [0.9735, 0.9823]。
- 逐 seed：0.9911 0.9643 0.9820 0.9821 0.9821 0.9823 0.9643 0.9825 0.9737 0.9735。
- **10 个 seed 里 0 个** 的 greedy-on-f 达到 OPT（K=1 时 10 个、K=2 时 6 个、K=3 和 K=4 各 1 个）。
  即 K 增大后 greedy-on-f 系统性地不最优，而不是偶尔掉队。
- f(greedy^f̃)/OPT：median 0.9423，IQR [0.9292, 0.9471]，min 0.9196。

## 5 这对实验表的 OPT 代理脚注说明了什么

`results/EXP_table.tex` 的 *Note (i)* 现在写的是定性句：分母是 greedy-on-f，是 OPT 的上估代理，
所以表里每个 ratio 都是 f(S^f̃)/f(OPT) 的上估。本次测量给这句话补上一个量级：

1. **代理把分母压低的幅度在 K=3,4,5 上是平的，约 1.8%。**
   1 − median f(greedy^f)/OPT 依次为 K=3 的 1.80%、K=4 的 1.77%、K=5 的 1.79%。
   第四晚只有 K<=4 时无法判断这个量是否随 K 增长；现在多一个点，K=3..5 区间内它不增长。
2. **换成 OPT 分母后 breast_cancer 的 ratio 下降 1.7 个百分点。**
   同样 seeds 0..9：K=5 时表口径 median ratio = f(greedy^f̃)/f(greedy^f) = 0.9593，
   换成 f(greedy^f̃)/OPT = 0.9423，下降 0.0171。K=2/3/4 的对应下降是 0.0134 / 0.0177 / 0.0222。
3. **方向与 wine K=7 的旧测量一致。** 第四晚 `opt_check` 在 wine K=7 上得到
   median f(greedy^f)/OPT = 0.9722（抬高约 2.8%）。两个数据集都落在"抬高 2-3%"这一档，
   都是分母偏小、报出的 ratio 偏大。

建议脚注最多加一句可核对的量，例如：在 breast\_cancer 上按 K <= 5 全枚举，
median f(greedy-on-f)/OPT = 0.982（`results/G4_bc_opt_K5.csv`），即该行 ratio 作为
OPT 归一化比值的上估，误差量级约 2%。

**不要写的话（会越界）**：

- 不要把这个 2% 直接套到表里的 K=7 行。表格 E1 行是 K=7 且是四个数据集合并的中位数；
  breast_cancer 的 K=7 OPT 没有测（C(30,7) = 2,035,800 子集/seed，按本机 471 次/秒
  约 72 分钟/seed、10 个 seed 约 12 小时）。"K=3..5 平坦所以 K=7 也差不多"是
  `[CONJECTURE]`，不是测量。
- 不要说这个数覆盖 airline / digits20 / wine 的 K=7；airline 的情况见
  `results/G4_airline_optproxy.md`，那只是 OPT 的下估 sanity check。
- 表格主数仍用 greedy-on-f 作分母不变；本节只是给 Note (i) 一个可引用的数量级。

## 6 遗留

- `[FAILED]` 无。本任务两项自检都 PASS。
- 未做：breast_cancer K=6、K=7 的全枚举（12 小时量级，超今晚预算）；
  其他三个数据集的暴力 OPT（wine 只有 K=7 的旧 `opt_check` 打印值，没有落 CSV）。
