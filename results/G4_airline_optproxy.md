# G4.2 airline 的 OPT 保守下估（sanity check，不进主表）

状态：`[VERIFIED-PARTIAL-ENUM]`。OPT_hat 是**在一个明确写死的候选池上取的精确最大值**，
它是 OPT 的**下估**（lower estimate），不是 OPT。因此本文件里所有以 OPT_hat 为分母的比值
都是相应 OPT 归一化比值的**上估**。**这只是 sanity check，实验表的 ratio 分母不变，
仍是 greedy-on-f。**

一键复现：

```
python3 results/G4_airline_optproxy.py     # 默认 --K 7 --seeds 10 --workers 3
```

产出：`results/G4_airline_optproxy.csv`（10 行，每 seed 一行）、
`results/G4_airline_optproxy.log`（含每 seed 的 OPT_hat argmax 集合与 surrogate core）。

## 1 为什么不能全枚举

E1 的 airline 行是 K=7、22 个特征，全枚举需要 C(22,7) = 170,544 个子集/seed：

- 真值 f（决策树 held-out accuracy，20,300 train / 5,075 test）本机实测 0.033 s/次
  → 约 94 分钟/seed，10 个 seed 约 15.6 小时。
- 若还要按 f̃（train-only 5-fold CV）对这 170,544 个子集排序，f̃ 实测 0.148 s/次
  → 约 7.0 小时/seed。

两者都远超本任务 45 分钟的时间盒，所以全枚举不做。

## 2 OPT_hat 的定义（写死，可复现）

对每个 seed（split 与 E1 相同：`train_test_split(test_size=0.2, random_state=seed)`）：

```
OPT_hat = max f(S) over  A ∪ B ∪ {S^{greedy-on-f}, S^{greedy-on-f̃}}
```

- **A（f̃ 排序的 top-200）**：先用 f̃ 跑 12 步 greedy 得到一个 12 特征的 surrogate core，
  枚举它的全部 C(12,7) = 792 个 K-子集并逐个用 f̃ 打分，按 f̃ 降序取前 200
  （并列用排序后的下标元组打破，确定性）。
- **B（2000 个均匀随机 K-子集）**：从全部 22 个特征里均匀抽 7 个，去重到 2000 个，
  随机源 `np.random.default_rng([MASTER_SEED, seed])`，`MASTER_SEED = 20260905` 写死在脚本里。
- **两个 greedy 集合**：必须加进去，否则 OPT_hat 可能低于一个已知可行的值，
  比值会大于 1，"下估"就不成立了。加进去以后 OPT_hat >= f(greedy-on-f) 按构造成立。

实际候选池去重后每 seed 2,197 到 2,200 个不同子集。

**与任务描述的一处偏离（记录在案）**：任务写的是"用 f̃ 上穷举 top-200 候选集"。
在全部 C(22,7) 上按 f̃ 排序需要 7 小时/seed（见上），做不了，所以把 f̃ 的排序范围限制在
surrogate core 的 792 个子集上。这个限制只会让 A 变小、让 OPT_hat 变小，
所以**下估的方向没有变**，只是下估可能比理想情况更松。

f、f̃、split、greedy 全部由 `importlib` 从 `results/E1_run.py` 载入调用，
没有改动 `results/E1_run.py`、`src/`、`code/`。

## 3 自检

脚本重算的 `table_ratio = f(greedy^f̃)/f(greedy^f)` 与 `results/E1_rows.csv` 里
airline、K=7、同 seed 的 `ratio` 列逐个比较（6 位小数）：

```
[G4.2] E1 consistency: PASS (table_ratio identical to E1_rows.csv at K=7 for 10 seeds)
```

不通过就 assert 失败，脚本不会写出 CSV。

## 4 结果（seeds 0..9，K=7）

wall time **726.0 s（12.1 分钟）**，3 个 worker，中位 167.5 s/seed。未触发 45 分钟时间盒。

| 量 | median | min | max | IQR |
|---|---|---|---|---|
| f(greedy^f)/OPT_hat | **1.0000** | 0.9967 | 1.0000 | [0.9983, 1.0000] |
| f(greedy^f̃)/OPT_hat | **0.9978** | 0.9942 | 0.9988 | [0.9972, 0.9979] |
| 表口径 ratio = f(greedy^f̃)/f(greedy^f) | 0.9979 | 0.9942 | 1.0013 | [0.9972, 0.9997] |

- OPT_hat 中位 0.947783（held-out accuracy）。
- **10 个 seed 里只有 3 个（seed 2、4、9）在候选池里找到了严格优于 greedy-on-f 的集合**，
  提升量 0.00217 / 0.00296 / 0.00315 个 accuracy 点，相对提升最大 **0.333%**。
- OPT_hat 的 argmax 来源：8 次来自 A（f̃ top-200），2 次就是 greedy-on-f 本身。
  **2000 个均匀随机子集一次都没有成为 argmax**，说明随机池在这个问题上几乎不起作用，
  真正有用的是 f̃ 排序出来的候选。
- 每个 seed 的 OPT_hat argmax 集合与 greedy-on-f 集合最多差 1 到 2 个特征
  （见 log；例如 seed 4：`[1,3,4,6,9,12,18]` vs `[1,3,4,6,9,11,18]`）。

## 5 怎么读这些数（方向必须写清）

1. **OPT_hat <= OPT**，因为它是在可行 K-子集的一个真子集上取 max。
2. 因此对任意 S 有 **f(S)/OPT_hat >= f(S)/OPT**：本文件里每个比值都是对应 OPT 归一化比值的**上估**。
3. 于是 "把表格分母从 greedy-on-f 换成 OPT 会掉多少" 这件事，本测量给的是一个**下界**：
   airline 行至少掉 0（中位数 0.9979 → 0.9978，中位下降 0.00000，最大下降 0.00333），
   真实的下降只会更大，不会更小。
4. 反过来说，airline 上 "greedy-on-f 当 OPT 代理" 这件事**至多**能被证伪到 0.33% 的量级，
   在这个候选池里看不到更大的空隙。这与 breast_cancer 的 2% 形成对比
   （`results/G4_bc_opt.md`：K=5 全枚举，median f(greedy^f)/OPT = 0.9821），
   也与 airline 本来 ratio 就接近 1（E1 30 seed 中位 0.9990）一致。

**不要写的话**：

- 不要说 "airline 上 greedy-on-f 就是 OPT"。本测量只覆盖 2,200 / 170,544 = 1.3% 的可行集合，
  没覆盖到的 98.7% 里可能有更好的集合。正确说法是 "在 top-200(f̃) ∪ 2000 random 的候选池里
  没有找到比 greedy-on-f 好过 0.34% 的集合"。
- 不要把 0.33% 当成 OPT gap 的估计，它是 gap 的**下界**。
- 不要把这个数字放进 `results/EXP_table.tex` 的主表或 Note (i)。Note (i) 的定性陈述
  （分母是 OPT 上估代理、表里 ratio 都是上估）不受影响；要引数量级请用
  breast_cancer 的全枚举结果，那个是真 OPT。

## 6 遗留

- `[FAILED]` 无。两项都在时间盒内完成（12.1 分钟 < 45 分钟）。
- 未做：airline 的真 OPT（15.6 小时量级）；候选池扩大（例如在真值 f 上做 local search
  收紧 OPT_hat）没有做，因为那会偏离任务写死的两个候选来源。
- seeds 只跑 0..9（E1 是 0..29），为控时间；对照用的表口径 ratio 也取的同样 10 个 seed
  （seeds 0..9 中位 0.9979，全 30 seed 中位 0.9990），两者不要混用。
