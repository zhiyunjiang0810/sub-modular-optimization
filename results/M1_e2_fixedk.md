# M1.1 实验管线的固定 K 步语义核查（TASKS8 M1 第 1 项，实验部分）

任务：核查 E2 生成管线是否与正文的**固定 K 步** predictive greedy 语义一致（零或负预测增益也继续选），
并按 D3 逐步定义（台账 T3/T15：a_t = M_t/g_t；M_t=g_t=0 取 1；g_t=0<M_t 取 ∞；η^sel=max{1,a_t}；L_K(∞)=0）
重算 E2 的 η^sel 与证书列。不改 E2_rows.csv，不改 code/、src/、paper/、台账。

一键复现见 §6。全部结论的数据来自 `results/M1_e2_fixedk.py`（240 条 run 全量重放，2 分 01 秒）。

---

## §1 代码审计与行引用

### 1.1 greedy 循环：固定 K 步，无增益相关的提前退出

- `src/im_graph.py:139` `while len(S) < K and pq:`：E2 的唯一 greedy 实现（CELF lazy greedy）。
  循环条件只有两项：已选够 K 个、候选堆为空。函数体 `src/im_graph.py:140-152` 里只有
  `if e in Sset: continue`（跳过已选元素）与 staleness 复算分支，**没有任何对增益取值或符号的测试**，
  因此 d̃ = 0 甚至 d̃ < 0 的元素照样被选中并计入 S。这与正文的固定 K 步语义一致。
- `results/E2_run.py:295` `picks = lazy_greedy(F_obs, ground, K, record=record, quantize=None)`：
  E2 的每条轨迹就是上面这一个调用，K = `K_MAX` = 30，没有外层 while、没有 break。
- `results/E2_run.py:265-266` `if d_chosen <= 0: diag['nonpos_steps'] += 1`：真实增益非正的步**只被计数**，
  不触发任何停止；record 回调随后照常 `true_state.add(chosen)` / `obs_state.add(chosen)` 推进轨迹。
- 候选池耗尽这条退出路径在 E2 不可能触发：ground set 大小为 1,005（email_eu_core）、5,908（politician）、
  7,057（government）、50,515（artist），都远大于 K=30（重放记录在 `M1_e2_fixedk.json` 的 `per_run[].ground_n`）。

结论：**E2 的 greedy 本来就是固定 K 步**。没有"无正预测增益就 break"、"max 取到 0 就停"之类的代码。

### 1.2 统计层：η^sel 的口径与 D3 不一致（这是真正的偏差点）

- `src/statistics.py:89-91`
  ```
  if d_c <= 0:
      n_nonpos_steps += 1
      continue
  ```
  取 max 时**跳过**所有 g_t ≤ 0 的步，只把它计入 `n_steps_nonpos`。按 D3，g_t = 0 < M_t 的步应给 a_t = ∞，
  于是整条 run 的 η^sel = ∞；现在这类步被从 max 里删掉，run 拿到的是一个有限 η^sel。
  模块 docstring（`src/statistics.py:11-26`）把这条写成了显式的"fixed policy, TASKS4 F1.3"，
  即它是一个**有意的旧口径**，不是 bug，但它早于 D3，语义与 D3 不同。
- `src/statistics.py:49` `if eta is None or eta <= 0 or not math.isfinite(eta): return float('nan')`：
  `L_K` 在 η=∞ 时返回 nan 而不是 D3 要求的 0；`src/statistics.py:132` 的
  `LK_eta_sel=f'{L_K(es, K):.6f}' if es else ''` 也没有 ∞ 分支。也就是说**统计层根本无法表达 D3 的 ∞ 与 L_K(∞)=0**。
- 后果：`results/E2_rows.csv` 的 `eta_sel` / `LK_eta_sel` 两列是 pre-D3 口径，对含有害零步的 run 偏乐观
  （给出了本不该有的正证书）。

### 1.3 下游已经打了补丁（所以宏基本没受影响）

- `results/G3_gen_numbers.py:325-327`
  `e2sel = [float('inf') if float(r['n_steps_nonpos']) > 0 else float(r['eta_sel']) for r in main]`：
  宏生成层对 E2 行施加 ∞ override，`ETwoKMainEtaSelMedian` / `ETwoKMainBound` / `ETwoHarmfulZeroTrajKMain`
  等宏因此已是 D3 口径。
- `results/K3_split_figs.py:86-87`、`:166`：money plot 与 aux_p_vs_eta 同样施加 override。
- **例外**：`results/EXP_table_build.py:57` `_, emed, _ = quantiles(col(rows, 'eta_sel'))` 直接读 CSV 列，
  **没有** override，见 §4。

### 1.4 E1 / E3 顺带的语义检查（按任务要求不重算）

- E1：`results/E1_run.py:261-273` `greedy_exact` 是 `for t in range(K)` 固定 K 步，唯一 `break`
  在 `results/E1_run.py:265-266` `if not rem: break`（候选池空），无增益测试；
  `E1_rows.csv` 的 120 条 run 全部恰好 7 个前缀行（K=1..7），无早停。
- E3：主轨迹是 `results/E3_run.py:312` 的一次 `lazy_greedy(..., Kmax, ...)`；对拍用的
  `exact_greedy`（`results/E3_run.py:320-334`）唯一 `break` 在 `:328` `if best is None`（候选池空）。
  E3 的 K 上限是**文章长度决定的** `results/E3_run.py:443` `Kmax = min(K_MAX, n - 2)`，
  `Kmax < K_MIN` 的文章整篇跳过（`:444`）。这是预算随实例变化，不是"增益不好就停"，
  语义上仍是固定 K 步。E1/E3 的目标非单调、出模型，按 T15 其 η^sel 是 finite-step diagnostic，
  本任务不重算（它们的 `n_steps_nonpos` 分别是 21.4% / 20.0% 量级，若强行套 D3 会把绝大多数 run 判成 ∞，
  这正是把 L_K 列当 reference 而非 certificate 的原因）。

---

## §2 未记入的早停 run 清单

**无。**证据两条，互相独立：

1. **CSV 结构证据（全体 240 条 run）**：`results/E2_run.py:299` 的
   `for k in range(1, len(num_vals) + 1)` 表明每条 run 每**执行过的一步**恰好写出一行前缀；
   若某条 run 少走了步，它的前缀行就会少于 30。实测 `E2_rows.csv` 共 7,200 行 = 240 run × 30 前缀，
   每条 run 的 K 集合恰为 {1,…,30}，**0 条 run 前缀数 < 30**（`M1_e2_fixedk.json` 的
   `early_stopped_runs: []`）。
2. **重放证据（全体 240 条 run）**：`M1_e2_fixedk.py` 用同一张真图、同一个 `edge_subsample(p, seed)`、
   同一个 `lazy_greedy` 重放每条轨迹，`len(picks) == 30` 对 240/240 成立
   （`runs_with_short_trajectory: []`）。

另外重放记录了每步的 (g_t, M_t)，用于 D3 三分类：

| 分类 | 步数（240 run × 30 步 = 7,200 步） |
| --- | --- |
| g_t > 0（正常步） | 7,184 |
| g_t = 0 < M_t（有害零步 → a_t = ∞） | **16** |
| g_t = M_t = 0（良性零步 → a_t = 1） | 0 |
| g_t < 0（出模型） | 0 |

16 条有害零步分布在 16 条不同的 run（每条 run 恰好 1 个），与 `E2_rows.csv` 的 `n_steps_nonpos` 逐 run 吻合，
也与台账 T15 的"16 条 ∞ 轨迹"一致。**覆盖函数单调，所以 g_t < 0 不可能出现，实测确认 0 条。**
"良性零步 0 条"是本次新增的独立确认：此前 `G3_gen_numbers.py` 的 override 是按 `n_steps_nonpos > 0` 一刀切，
默认所有零步都有害；重放直接取 M_t 验证了这个默认在 E2 上确实成立（16/16 有害）。

---

## §3 按固定 K 步（D3）重算的对比

重算规则：η^sel_(k) = max{1, max_{t ≤ k} a_t}，a_t 按 D3 三分类；L_K(∞) = 0。
逐 run 逐前缀的完整结果在 `results/M1_e2_fixedk_rows.csv`（7,200 行，列含 `eta_sel_csv`、`eta_sel_fixedk`、
`LK_csv`、`LK_fixedk`、`is_inf`、`n_harmful_zero_replay`、`eta_sel_changed`）。

总量：**240 条 run 中 16 条的 η^sel 改变（6.7%），7,200 个前缀行中 225 行改变（3.1%）**；
其余 224 条 run 的 η^sel 与 L_K 与 `E2_rows.csv` 逐行一致（比较容差按 CSV 的 `%.6g` / `%.6f` 取
相对 2e−5 / 绝对 1e−4，见脚本注释）。改变全部是"有限 → ∞"，即**证书变弱，方向安全**，没有任何一行的
证书被这次重算调高。

### 逐 run 差异表（16 条；t* = 首个有害零步的步序）

| run | t* | 受影响前缀 K | η^sel(K=30) CSV → fixed-K | L_K(K=30) CSV → fixed-K | η^sel(K=t*−1)（不变） |
| --- | --- | --- | --- | --- | --- |
| email_eu_core p=0.3 seed=12 | 19 | 19..30（12） | 10 → ∞ | 0.095314 → 0 | 4.33333 |
| email_eu_core p=0.3 seed=19 | 27 | 27..30（4） | 9 → ∞ | 0.105345 → 0 | 8 |
| email_eu_core p=0.5 seed=1 | 25 | 25..30（6） | 5 → ∞ | 0.181817 → 0 | 5 |
| email_eu_core p=0.5 seed=3 | 30 | 30..30（1） | 6 → ∞ | 0.153912 → 0 | 6 |
| email_eu_core p=0.5 seed=12 | 21 | 21..30（10） | 4 → ∞ | 0.222015 → 0 | 2.75 |
| facebook_government p=0.5 seed=0 | 9 | 9..30（22） | 4.29412 → ∞ | 0.208468 → 0 | 1.84615 |
| facebook_government p=0.5 seed=1 | 15 | 15..30（16） | 5.15789 → ∞ | 0.176759 → 0 | 2.55319 |
| facebook_government p=0.5 seed=2 | 12 | 12..30（19） | 4.05882 → ∞ | 0.219167 → 0 | 2.32632 |
| facebook_government p=0.5 seed=7 | 9 | 9..30（22） | 6.53333 → ∞ | 0.142259 → 0 | 1.84615 |
| facebook_government p=0.5 seed=9 | 7 | 7..30（24） | 4.71429 → ∞ | 0.191743 → 0 | 1.89362 |
| facebook_government p=0.5 seed=10 | 13 | 13..30（18） | 3.96 → ∞ | 0.223993 → 0 | 1.84615 |
| facebook_government p=0.5 seed=15 | 12 | 12..30（19） | 6.47619 → ∞ | 0.143423 → 0 | 6.47619 |
| facebook_government p=0.5 seed=16 | 14 | 14..30（17） | 6.55556 → ∞ | 0.141812 → 0 | 6.55556 |
| facebook_government p=0.5 seed=17 | 9 | 9..30（22） | 5.95 → ∞ | 0.155102 → 0 | 1.84615 |
| facebook_government p=0.5 seed=19 | 21 | 21..30（10） | 6.38889 → ∞ | 0.145237 → 0 | 6.38889 |
| facebook_politician p=0.3 seed=15 | 28 | 28..30（3） | 33.5 → ∞ | 0.029424 → 0 | 33.5 |

受影响前缀合计 Σ(31 − t*) = **225**，与台账 T15 / J2 §8.2 记的 225 个 K≥2 前缀数字逐位一致（独立复算吻合）。
16 条 run 落在 3 个网络（email_eu_core 5 条、facebook_government 10 条、facebook_politician 1 条），
facebook_artist 0 条；p 的分布是 p=0.3 三条、p=0.5 十三条、p=0.8 零条。

### ∞ 标记与已发布基线的一致性

- 16 条 ∞ 轨迹：与 T15 卡"16 条有害零步 run 的 η^sel=∞"**完全一致**（同样的 16 个 (dataset, p, seed)）。
- 本次是第一次用重放直接取 M_t 来判定"有害"，此前的证据（J2 §8.2、`H3_j2_recheck.py`）是从
  sampled candidate pairs 里找一个正真实增益作为存在性见证；两条独立路径给出同一份 16 条清单。

---

## §4 结论与受影响的已发布数字

**三选一结论：「管线本来就是固定 K 步」**（§1.1、§2 两条独立证据：0 条早停 run），
**但附一条必须上报的次级发现：统计层 `src/statistics.py` 的 η^sel 口径不是 D3**，
它把有害零步从 max 里删掉（`src/statistics.py:89-91`），因此 `results/E2_rows.csv` 的 `eta_sel` /
`LK_eta_sel` 两列对 16 条 run（225 个前缀行）比 D3 口径偏乐观。这不是早停，是**记账口径**问题。

### numbers.tex 宏：0 个受影响

`results/G3_gen_numbers.py:325-327` 在生成宏之前已经施加 ∞ override，所以
`\ETwoKMainEtaSelMedian`(4.5)、`\ETwoKMainBound`(0.199)、`\ETwoHarmfulZeroTrajKMain`(16)、
`\ETwoHarmfulZeroTrajPctKMain`(6.7)、`\ETwoHarmfulZeroPrefixes`(225)、`\ETwoInfMedianCells` 等
E2 宏**已经是固定 K 步 / D3 口径**，本次重算逐一复现了这些值（16、6.7%、225 见 §2/§3；
override 后的 K=30 中位数 4.532405 → `%.1f` = 4.5，L_30(4.532405) = 0.198643 → `%.3f` = 0.199）。

### 但有 2 个已发布数字不是宏、且仍是 pre-D3 口径

`results/EXP_table_build.py:57` 直接对 `E2_rows.csv` 的 `eta_sel` 列取中位数，没有 override，
生成 `results/EXP_table.tex` → `paper/sections/EXP_table.tex`（`paper/sections/experiments.tex:207`
`\input`），表 1 "Influence max. (30)" 行：

| 表 1 单元格 | 当前值（pre-D3） | 固定 K 步 / D3 值 | 与正文的关系 |
| --- | --- | --- | --- |
| $\eta^{sel}$ | **4.3** | **4.5** | 正文同一量用 `\ETwoKMainEtaSelMedian` = 4.5（`experiments.tex:146`） |
| $L_K$ | **0.207** | **0.199** | 正文同一量用 `\ETwoKMainBound` = 0.199（`experiments.tex:147`） |

即同一篇论文里，表 1 与正文对"K=30 的中位 η^sel 与其证书"印了两组不同的数。同表的
`d_t ≤ 0 %` 列（0.0）不受影响（它是 `frac_steps_nonpos` 的**逐 run 中位数**，与 override 无关，
且与 `\ETwoNonposPctKMain` = 0.0 一致）；E1 / E3 两行不在本次重算范围（出模型的 finite-step diagnostic）。

**建议（不执行，交主代理决定）**：要么给 `EXP_table_build.py` 的 E2 行加同一个 override（两格变 4.5 / 0.199），
要么让表 1 的 η^sel 列走宏。本报告未改动 `EXP_table_build.py`、`EXP_table.tex`、任何 `.tex` 或宏。

### 可选的更彻底做法（同样不执行）

若希望 CSV 本身也 D3 自洽，需要在 `src/statistics.py` 里让 `upto` 记录 M_t 并对 g_t=0<M_t 返回 ∞、
让 `L_K` 支持 `L_K(∞)=0`，然后重跑 E2（~2 分钟）。但 `src/statistics.py` 属"不修改已验证文件"的范围，
且下游已 override，所以本任务只提供并行文件 `results/M1_e2_fixedk_rows.csv` 作为 D3 口径的对照，
不动原 CSV。

---

## §5 状态标签

- 「E2 的 greedy 循环是固定 K 步，240 条 run 各执行恰好 30 步，无早停 run」
  状态 `[VERIFIED-LP]`（口径：穷举/重放确认，非 LP；240 条 run 全量重放 + CSV 结构双证据，
  脚本 `results/M1_e2_fixedk.py`）。
- 「E2 的 16 个零步全部有害（M_t > 0），良性零步 0 个，负增益步 0 个」
  状态 `[VERIFIED-LP]`（同脚本，逐步取 M_t 判定；与 J2 §8.2 的 sampled-pair 见证路径独立吻合）。
- 「按 D3 重算：16 条 run / 225 个前缀行的 η^sel 由有限变 ∞，L_K 变 0；其余 224 条 run 逐行不变」
  状态 `[VERIFIED-LP]`（同脚本，`results/M1_e2_fixedk_rows.csv` 可逐行核对）。
- 「numbers.tex 的 E2 宏已是 D3 口径，0 个受影响；表 1 的两个单元格（4.3 / 0.207）仍是 pre-D3，
  D3 值为 4.5 / 0.199」：`[VERIFIED-LP]`（脚本 `table_impact()` 复算，与现有宏值逐位比对）。
- 「E1 / E3 的 greedy 同样是固定 K 步（唯一退出是候选池空；E3 的 K 上限由文章长度决定）」
  状态 `[VERIFIED-LP]`（代码逐行 + E1 的 120 条 run 前缀数全为 7 的结构检查；E3 按任务要求不重算）。

未使用 `[HAND-PROOF-UNREVIEWED]` / `[CONJECTURE]`：本任务的每条结论都由脚本输出直接支撑。

---

## §6 一键复现

```
cd /home/user/sub-modular-optimization
timeout 600  python3 results/M1_e2_fixedk.py --audit-only     # 约 1 秒：CSV 结构审计 + 表 1 两格
timeout 3000 python3 results/M1_e2_fixedk.py --runs all       # 约 2 分 01 秒：240 条 run 全量重放
timeout 600  python3 results/M1_e2_fixedk.py                  # 约 6 秒：仅 16 条 flagged + 4 条对照
```

输出（均为新文件，`E2_rows.csv` 未被触碰）：

- `results/M1_e2_fixedk_rows.csv`：逐 run × 逐前缀的 `eta_sel_csv` vs `eta_sel_fixedk`、
  `LK_csv` vs `LK_fixedk`、`is_inf`、`n_harmful_zero_replay`、`eta_sel_changed`。
- `results/M1_e2_fixedk.json`：`early_stopped_runs`（空）、`flagged_runs`（16）、
  `per_run`（240 条，含 `n_steps_executed`、`first_harmful_step`、`n_benign_zero`、`out_of_model_steps`）、
  `table1_e2_cells`、`n_runs_with_diff` = 16、`n_prefix_rows_with_diff` = 225。
- `results/M1_e2_fixedk.md`：本文件。

重放依赖：`data/graphs/email_eu_core/`、`data/graphs/facebook_gemsec/`（已在仓库内），
`src/im_graph.py`、`src/statistics.py`、`results/E2_run.py`（只 import，不修改）。
