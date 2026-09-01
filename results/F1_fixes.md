# F1 实验修补 — 改了什么、数字变了多少、状态

日期 2026-09-01。对应 `TASKS4.md` 的 F1 五项 + 出图核对。
所有改动的脚本都**实际重跑过**，下面每一项的数字都来自这次重跑的产物，不是转抄。
未触碰 `code/`、`paper/`、`N*`/`T*` 文件。

| # | 项目 | 状态 | 一句话结论 |
|---|---|---|---|
| 1 | ROUGE 核对 | **[VERIFIED-NUMERIC] PASS，无需改 E3** | 90 篇 × 1,624 个候选摘要，最大绝对差 **0.0** |
| 2 | E2 η^path 去截断 | **PASS，四个图全量重算** | K=30 合并中位数 71.74 → **284.0**；ratio/η^sel/viol 逐行不变 |
| 3 | statistics.py 写死 d_t ≤ 0 | **PASS，E1–E4 全部重生成行** | 新列 `n_steps_nonpos`/`frac_steps_nonpos`；旧列逐行不变 |
| 4 | breast_cancer OPT 代理 | **PASS，降到 K=4（超时）** | median f(greedy^f)/OPT = **0.9823**（K=4，seeds 0..9） |
| 5 | EXP_table.tex 重生成 | **PASS，脚本化 + 编译过** | 393.7pt / 397.5pt textwidth，无 Overfull |
| 6 | E5 出图 | **PASS，肉眼核对过** | 图例/坐标/超界标注仍正确（数据未变，见下） |

---

## 1 ROUGE 核对（TASKS4 F1.1）

**改了什么**：没有改 `E3_run.py` 的 `Rouge1F`。新增核对脚本 `results/F1_rouge_check.py`，
结果 `results/F1_rouge_check.json` 与报告 `results/F1_rouge_check.md`。

**安装**：`pip install rouge-score` 在系统 Python 上失败（Debian 补丁版 setuptools 的
`AttributeError: install_layout`，**不是网络问题**，包已下载）。改用干净 venv 安装成功
（rouge-score 0.1.2）。因此**不标 [FAILED-网络]**。

**数字**：BBC business/sport/tech 各 30 篇（共 90 篇），每篇取单句 + 前缀 + greedy 前缀，
共 1,624 个 (文章, 候选子集) 对，两边打同一批子集：

- **最大绝对差 0.0，平均绝对差 0.0，> 1e-6 的比较 0/1,624。**
- 参考摘要 token 序列不一致的文章 0/90；90 篇的全部 1,608 段文本（句子 + 参考摘要）
  逐段 token 序列相同。

**原因**：两边公式相同，唯一可能分歧的是 tokenizer（我方 `\w+`；rouge-score 是
`[^a-z0-9]+` 切分）。这批 BBC 文本里"匹配 `\w` 但不在 `[A-Za-z0-9]`"的字符出现 **0 次**
（无下划线、无带重音字母），所以两个 tokenizer 逐 token 相同。负控制（`café`/`under_score`/
`Zürich` 等）证明对比装置能发现 0.05–0.13 量级的差异，见 `F1_rouge_check.md` 第 4 节。

**因此**：差 ≤ 1e-6 → **未以 rouge-score 为准改写 f，未因 ROUGE 重跑 E3**，
E3 的中位数（K=5：ratio 0.670、η^sel 7.15、L_5 0.132）**没有变化**（Δ = 0）。

---

## 2 E2 的 η^path 去截断（TASKS4 F1.2）

**改了什么**（`results/E2_run.py`）：

- `run_one` 里统计用的候选一律是该步的**全部剩余候选**；删掉观测图上的 `LazyTop obs_top`
  与 `cands = obs_top.top(TOP_M)` 分支。
- `DATASETS[*]['full_pairs']` 改名 `dump_all_pairs`，参数 `dump_full_pairs` 改名
  `dump_all_pairs`：**只**决定往 `E2_pairs_sample.csv.gz` 写多少行，不影响任何统计量。
- `TOP_M = 50` 的注释改为"落盘采样用"，模块 docstring 原则 4 同步改写。

**重跑**：`--mode run` 四个图 × p ∈ {0.3,0.5,0.8} × seeds 0-19 = 240 条轨迹（7,200 行），
先删 `E2_rows.csv` 与 `E2_pairs_sample.csv.gz`，保留 `E2_baselines.csv`（基线与候选集合无关，
自动跳过、保持不变），再 `--mode aggregate` + `--mode figures`。

**耗时**（机器上另有 3 个 CPU 密集任务并行）：email 0.4 min、politician 2.3 min、
government 3.2 min、**artist 31.5 min**（单 run 平均 31.5 s，最大 41.4 s）。
四个图都在 40 分钟/图上限内，**没有任何图标 "n/a"**，也没有报任何下估值。
（`unified_row` 里已经加了 `eta_path_override='n/a'` 的通道备用，但本次未使用。）

**数字变了多少**（K=30，每图 60 条 run 的中位数）：

| dataset | 旧（top-50） | 新（全候选） | 新/旧 | 逐 run 新/旧 min–median–max |
|---|---|---|---|---|
| email_eu_core | 78.5 | 78.5 | 1.00 | 1.00 – 1.00 – 1.00 |
| facebook_politician | 41.99 | 200 | 4.76 | 3.12 – 5.52 – 23.4 |
| facebook_government | 86.15 | 493 | 5.72 | 2.74 – 4.74 – 91.6 |
| facebook_artist | 200.1 | 1407 | 7.03 | 5.10 – 8.04 – 575 |
| **合并** | **71.74** | **284.0** | **3.96** | |

**不变量断言（跑了，0 处不一致）**：新旧 7,200 行按 (dataset, p, seed, K) 对齐，
`ratio` / `eta_sel` / `viol_sign_pct` 三列**逐行完全相同**。
另外 `E2_pairs_sample.csv.gz` 与旧文件**逐字节相同**（gzip 内容 SHA-256 一致，613,935 行），
这是"轨迹一点没变、只是统计口径变了"的独立证据。

同步更新：`E2_rows.csv`、`E2_p_eta.csv`、`E2_pairs_sample.csv.gz`（内容不变但重新生成）、
`figures/E2_p_eta.{png,pdf}`、`E2_notes.md` 第 4/5 节与第 8 节第 4、5 条、`EXP_SUMMARY.md` 的截断 caveat。
`E2_truncation_check.csv` 保留为历史记录并在 notes 里标明不要再引用它的 `eta_path_top50` 列。

---

## 3 `src/statistics.py` 把 d_t ≤ 0 的处理写死（TASKS4 F1.3）

**改了什么**：

- 模块 docstring 写死非正步策略：η^sel **只在 d_t > 0 的步上定义**；d_t ≤ 0 的步不进 max、
  计入 `n_nonpos_steps`；`LK_eta_sel` 因此是"对正增益步成立"的保证，
  超出范围的步比例正是 `frac_steps_nonpos`。CSV 列名保持机器可读（`LK_eta_sel` 不改名），
  语义写在表注里（见第 5 项）。
- `TrajectoryStats.upto` 增加 `n_steps`（前缀里被计分的步数），`upto()` 的 docstring 明示同一策略。
- `TrajectoryStats.add_step` 的 docstring 改为"`pairs` 必须包含每一个剩余候选"（配合第 2 项）。
- `ROW_FIELDS` 增加 **`n_steps_nonpos`** 与 **`frac_steps_nonpos`** 两列，`unified_row` 输出它们；
  另加可选参数 `eta_path_override`（给"某图超时只能标 n/a"用，本次未使用）。

**重跑（全部实际跑了）**：

| 任务 | 命令 | 耗时 | 结果 |
|---|---|---|---|
| E1 | `--datasets airline --seeds 0:30 --part main` + `--datasets wine,digits20,breast_cancer --seeds 0:30 --part main --append` | 530 s + 375 s | 840 行，旧 6 列（ratio/eta_sel/eta_path_trimmed/viol_sign_pct/LK×2）**逐行 0 处不同** |
| E2 | 见第 2 项 | 37 min | 7,200 行 |
| E3 | `python3 results/E3_run.py --limit 100 --fig` | 11 s | 4,377 行，旧 6 列**逐行 0 处不同**；`E3_summary.json` 与 `figures/E3_overview.*` 一并重生成 |
| E4 | `python3 results/E4_worst_instances.py` | < 1 min | 19 行，`ALL WITHIN 1e-10` |

**新列的数字**（`frac_steps_nonpos` 中位数）：

| 任务 | K | 中位数 | 备注 |
|---|---|---|---|
| E1 | 7 | **0.2143** | airline 0.000、digits20 0.000、breast_cancer 0.4286、wine 0.5714 |
| E2 | 30 | 0.000 | 224/240 条 run 为 0；16 条各有 1 步（0.033333） |
| E3 | 5 | **0.2000** | coverage 0.200 / diversity 0.000 / facility 0.200（中位数） |
| E4 | 3,5,8 | 0.000 | 19 个构造实例全部 0 |

**顺带查出的一处旧笔记错误（已更正）**：`E2_notes.md` 旧第 8 节第 4 条断言
"240 条轨迹 7,200 步里 d ≤ 0 出现 0 次，因为被选节点的真实边际至少是 1，即它自己"。
这个推理错了：被选节点若已经是先前某个被选节点的真图邻居，它自己也已被覆盖，边际可以是 0。
新列实测 **16/240 条 run 各有 1 步 d_t ≤ 0**。用**旧的、逐字节相同的**
`E2_pairs_sample.csv.gz` 取每步 d̃ 最大的候选（CELF 会选的那个）重数，同样得到 16 步、
同样这 16 条 run，**说明这不是本次改动引入的，是旧笔记漏记**。已在 `E2_notes.md` 更正。

**关于 E1 "只重新聚合"的尝试（记录下来，避免别人再踩）**：给 `E1_run.py` 加了
`--part rebuild_rows`，从 `E1_pairs.csv.gz`（存了每步全部候选的 d, d̃ 与 chosen 标记）
重建行。它**重建不出逐位相同的旧列**：pairs 文件把 d/d̃ 存成 10 位有效数字，而 ε-trim
判据 `|d| ≥ ε`（ε = 1/|held-out|）正好落在边界上——held-out accuracy 的增益是 1/|held-out|
的整数倍，浮点减法常常把它放到 ε 下面一个 ulp，而 10 位十进制又刚好在 ε 上面。
在 wine seed 29 上现场重跑与旧 CSV 完全一致、而重建结果不同，证明是文件精度的锅。
因此该模式改成**只在 0 处不一致时才写盘**，本次它拒绝写盘，E1 走了完整重跑（905 s，两块）。
η^sel 与 ratio 不受此边界影响（η^sel 不用 ε）。

---

## 4 breast_cancer 上的暴力 OPT（TASKS4 F1.4）

**改了什么**：`E1_run.py` 新增 `opt_bruteforce()` 与 `--part opt_bc --opt-k <K>`，
输出 `results/E1_opt_breast_cancer.csv`（40 行 = 10 seed × K=1..4）。
f 与正文同一个（决策树 held-out accuracy，同一个 frozenset 缓存）。

**降到 K=4 的理由（先估时）**：同机估到约 394 次 f 评估/秒（与 E1/E2 主跑并行占核），
K=1..5 需 C(30,1..5) = 174,436 次/seed，10 个 seed 约 **74 分钟 > 30 分钟上限**；
K=1..4 是 31,930 次/seed，实测每 seed 75–109 s，10 个 seed 共 **13.6 分钟**。
**K=5 的 OPT 没有测**，任何地方都不要报 K=5 的 OPT 比值。

**数字**（seeds 0..9）：

| K | 枚举子集数 | median f(greedy^f)/OPT | min | median f(greedy^f̃)/OPT | min |
|---|---|---|---|---|---|
| 1 | 30 | 1.0000 | 1.0000 | 0.9659 | 0.9065 |
| 2 | 435 | 1.0000 | 0.9727 | 0.9726 | 0.9364 |
| 3 | 4,060 | 0.9820 | 0.9640 | 0.9591 | 0.9273 |
| **4** | **27,405** | **0.9823** | 0.9554 | 0.9464 | 0.9115 |

即在 breast_cancer 上"用 greedy-on-f 当 OPT 代理"把 ratio 抬高约 **1.8%**，
与 wine K=7 的 0.9722（抬高约 2.8%）同量级、方向一致：**分母偏小，报出的 ratio 是上估**。
已写进 `E1_notes.md` §8 第 2 条的附注。

---

## 5 重新生成 `results/EXP_table.tex`（TASKS4 F1.5）

**改了什么**：新增 `results/EXP_table_build.py`，表里每个数字都由它从
`E{1,2,3}_rows.csv` + `E4_worst_case.csv` + `E4_rows.csv` 现算（E1 K=7 / E2 K=30 / E3 K=5
的中位数与 IQR），不再手抄。一键：`python3 results/EXP_table_build.py`。

**表注固定两句（外加一句结构性说明）**：
(i) 分母是 greedy-on-f（OPT 上估代理），表里每个 ratio 都是上估；
(ii) η^sel 只在正增益步上定义，`L_K` 列的认证下界是对这些步的陈述，非正步比例见
`frac_steps_nonpos` 列（表里最后一列 `$d_t\le 0$ %`）；
(iii) E2 的 sign-viol 是结构性为 0，写 `--` 而不是当作实验发现。

**新增两列**：`sign-viol. %` 保留，新增 `$d_t\le 0$ %`（即 `frac_steps_nonpos`）。

**数字**（与旧表对照）：

| 行 | ratio | IQR | η^sel | L_K | sign-viol % | d_t≤0 % |
|---|---|---|---|---|---|---|
| Feature sel. (7) | 0.971（不变） | [0.943, 0.998]（不变） | 2.0（不变） | 0.405（不变） | 22.7（不变） | **21.4（新）** |
| Influence max. (30) | 0.963（不变） | [0.936, 0.989]（不变） | 4.3（不变） | 0.207（不变） | --（不变） | **0.0（新）** |
| Summarization (5) | 0.670（不变） | [0.576, 0.757]（不变） | 7.2（不变） | 0.132（不变） | 10.0（不变） | **20.0（新）** |
| Worst-case V_j (5) | 0.278（不变） | exact | 3.5 | ρ_K | 0 | **0.0（新）** |

**旧表的全部数字都复现了**（这也验证了聚合口径：L_K 是在**中位数 η^sel** 上取值，
不是逐 run L_K 的中位数）。唯一的实质变化是新增的最后一列。

**一页宽度**：用 `paper/iclr2027_conference.sty` + booktabs 实测 `\settowidth`：
旧的 7 列表 **465.3pt 已经超出** textwidth 397.5pt；新表加 `\small` + `\tabcolsep 4pt`
并把表头 `$L_K(\eta^{sel})$` 缩成 `$L_K$`（定义移进 caption）后是 **393.7pt < 397.5pt**。
片段单独 `pdflatex` 编译通过，**无 Overfull/Underfull hbox**（只有预期的
`\ref{thm:trajectory}` undefined 警告）。

---

## 6 重跑 E5 出图（TASKS4 F1.5 末条）

`python3 results/E5_money_plot.py` 重跑，4 张图（money_plot + 3 张 aux）PNG+PDF 全部重写。

**数据实际上没变**：money plot 的横轴是 η^sel、纵轴是 ratio，这两列在 E1/E2/E3 的重跑里
逐行不变（第 2、3 项的断言），所以图形与上一版一致。肉眼核对（读了 `figures/money_plot.png`）：

- 横轴 `measured η^sel (log)`，刻度 1/2/5/10/30/100/500 正常；纵轴 ratio 0–1.05 正常。
- 图例四条（E1 蓝 / E2 橙 / E3 绿 / E4 黑 X）齐全，画在 K=30 面板左下，没有压住数据点。
- 超界标注：K=5 面板显示 "10 pts beyond"（该面板 η^sel > 500 的点数，由数据现算），
  K=30 面板无标注 —— 正确，K=30 的 η^sel 最大 456 < 500。
- E4 的黑 X 落在 ρ_K 实线上，E1/E2/E3 的点都在两条曲线上方，与标题一致。
- 唯一的小瑕疵：K=5 面板里 "10 pts beyond" 与 `ρ_K (solid), L_K (dashed)` 两段说明文字
  上下靠得较近（都在左下角），仍可读，未改。

`figures/E2_p_eta.{png,pdf}` 也重跑并肉眼核对（三个面板：η^sel vs p、ratio vs p、基线柱状），
坐标与图例正确；这张图只用 η^sel/ratio/基线，因此与上一版一致。

---

## 7 本次改动的文件清单

改动（脚本）：
- `src/statistics.py`（docstring + 两个新列 + `n_steps` + `eta_path_override`）
- `results/E2_run.py`（去截断、参数改名、docstring）
- `results/E1_run.py`（`--part opt_bc`、`--part rebuild_rows`、`--opt-k`）
- `results/EXP_table_build.py`（新增）
- `results/F1_rouge_check.py`（新增）

重生成（数据/图/表）：
- `results/E1_rows.csv`、`E1_pairs.csv.gz`、`E1_baselines.csv`、`E1_diagnostics.csv`
- `results/E2_rows.csv`、`E2_pairs_sample.csv.gz`、`E2_p_eta.csv`
- `results/E3_rows.csv`、`E3_pairs.csv.gz`、`E3_summary.json`
- `results/E4_rows.csv`、`E4_worst_case.csv`
- `results/E1_opt_breast_cancer.csv`（新）、`results/F1_rouge_check.json`（新）
- `results/E2_validation.txt`（改完后又跑了一遍 `--mode validate` 冒烟，读数仍全为 0）
- `results/EXP_table.tex`
- `figures/money_plot.*`、`aux_eta_sel_by_K.*`、`aux_p_vs_eta.*`、`aux_d_dtilde_scatter.*`、
  `E2_p_eta.*`、`E3_overview.*`

文档：
- `results/F1_rouge_check.md`（新）、`results/F1_fixes.md`（本文件，新）
- `results/E1_notes.md`（§8 第 2 条附注、CSV 列说明）
- `results/E2_notes.md`（§2/§4/§5/§8/§9）
- `results/EXP_SUMMARY.md`（截断 caveat 一行）

## 8 已知遗留

1. ROUGE 的 0 差只覆盖 90 篇；E3 全量是每类 100 篇，含重音字母/下划线的文章两边会分叉
   （量级 0.05–0.13/篇）。要彻底消除这个风险应当直接把 `Rouge1F` 的 tokenizer 换成
   rouge-score 的写法，本次因为差为 0 而没有动它。
2. breast_cancer 的 OPT 只做到 K=4；airline K=7 的 OPT 仍未测（C(22,7)=170,544）。
3. `E1_run.py --part rebuild_rows` 目前只能当一致性检查用，不能替代重跑（原因见第 3 项）。
4. `results/E2_truncation_check.csv` 的 `eta_path_top50` 列是历史值，已在 notes 标注不要引用。
5. 本次没有重跑 `E1_run.py --part gbc` / `--part baselines_fig`：
   `E1_gbc_seed0.csv` 与 `figures/E1_baselines.*` 仍是 8-31 的版本。GBC 行用自己的
   `GBC_FIELDS`（不含统一行格式的新列），基线图只画 `E1_baselines.csv` 的 held-out accuracy，
   而 `E1_baselines.csv` 在这次 `--part main` 重跑里被重新生成且**字节数与旧文件完全相同**
   （83,239 B，840 行），所以那张图重画也是同一张。
