# E3 notes — Text summarization，启发式作 surrogate

脚本：`results/E3_run.py`（一键复现：`python3 results/E3_run.py --limit 100 --fig`，全量 11 秒）
产物：`results/E3_rows.csv`（4377 行统一格式）、`results/E3_pairs.csv.gz`（91,683 个 (d, d̃) 对）、
`results/E3_summary.json`（脚本产出的全部聚合量，本文件的所有数字均由它转写）、
`figures/E3_overview.png` / `.pdf`。

本任务在论文中的定位：**模型边界外的行为**。ROUGE-1 F 既不单调也不 submodular（下文有实测），
所以这里得到的 ratio 与 η 不是对定理条件的确认，而是"当假设不成立时管线读数长什么样"的记录。

---

## 1. 数据与一个必须写清楚的偏差

- 文章：`data/bbc/BBC News Summary/News Articles/{business,sport,tech}/`，
  每类按文件名排序取前 100 篇（`001.txt` .. `100.txt`）。`seed` 列 = 文件名整数 1..100。
- 编码：三类 300 个文件**全部是合法 UTF-8**（英镑号为 `\xc2\xa3`）。脚本先按 UTF-8 解码，
  失败才回退 `errors='replace'`；本次运行回退次数 = 0（`bad_bytes` 未计数）。
  注：若按 latin-1 读会把 `£` 读成 `Â£`，进而污染 unigram，本次没有发生。
- **参考摘要缺口（重要）**：仓库内 `data/bbc/BBC News Summary/Summaries/` 只有 `business` 一个类目
  （118 个文件），`sport` 与 `tech` 的参考摘要在本地**不存在**；`data/raw/bbc.zip` 原始压缩包里同样只有
  119 个 Summaries 条目，所以不是解压丢失，而是入库的数据本身不全（`data/INVENTORY.md` 记录的
  "含 Summaries 各 5 类目" 与实际不符，建议订正）。
  - fallback：从 HuggingFace 下载同一数据集的 CSV 版
    `https://huggingface.co/datasets/gopalkalpande/bbc-news-summary/resolve/main/bbc-news-summary.csv`
    （2224 行，business 510 / sport 510 / tech 401，与本地文章数一致），
    按**文章全文 token 序列精确匹配**回填 sport / tech 的参考摘要。
  - 该 fallback 的可信度做了核对：business 的 100 篇中 99 篇能唯一匹配上 CSV 行，
    这 99 篇的 CSV 摘要与本地 `Summaries/business/*.txt` **逐 token 完全相同**（99/99）。
    因此把它当作同一份数据的另一份拷贝是有依据的。
  - 本次实际来源：`business:local=100, sport:csv=100, tech:csv=99, tech:ambiguous=1`。
    `tech/048.txt` 在 CSV 中对应两行重复文章且两行摘要不同，无法判定，**整篇跳过并在此记录**
    （唯一被跳过的文章）。
  - CSV 缓存路径：`$E3_BBC_CSV`，默认 `/tmp/e3_bbc_cache/bbc-news-summary.csv`，缺失时脚本用 curl 自动下载。
    按"只写 results/E3_* 与 figures/E3_*"的约束，**没有**把这个 7.3 MB 文件写进 `data/`；
    要长期可复现，需要人工把它归档进 `data/` 并更新 INVENTORY。

## 2. 句子切分（无 nltk，不联网装包）

- 按行 strip，去空行；**首行（标题）单独算一句，且是 ground set 的 0 号元素**（选择 A：不并入正文）。
  理由：BBC 标题是完整的抽取单元，参考摘要里经常出现标题的实词，把它并入首段会让 0 号元素虚胖。
- 正文：其余非空行用空格拼接，按正则 `(?<=[.!?])\s+` 切分，丢弃不含 `\w` 的碎片。
- 已知局限：以句点结尾的缩写会被过切；BBC 语料写 `US`/`UK`/`Mr` 不带点，所以实际很少发生，未做特例处理。
- ground set 规模：min 6，median 15，max 97 句（300 篇）。
- K 的处理：每篇取 `K_max = min(7, n_sent - 2)`（保证每步至少还剩 2 个候选），K 从 3 到 K_max。
  因此 K=7 的样本量比 K=3 小：business 297、tech 297、sport 243 行（sport 短文多）。
  **没有**为了凑齐 K=7 而丢弃短文章，样本量差异如实写在表的 n 列里。

## 3. f = ROUGE-1 F-measure（自实现）

- 小写 → `re.findall(r'\w+')` 分词 → unigram clipped counts；
  `P = overlap / |候选 token|`，`R = overlap / |参考 token|`，`F = 2PR/(P+R)`，`P+R=0` 时取 0；`f(∅)=0`。
- **不去停用词、不做 stemming、不做 ROUGE-1.5.5 的任何后处理**（保持简单，明确记在此处）。
  这会让绝对分数高于官方 ROUGE 脚本，但 E3 关心的是同一 f 下的比值与 η，绝对值不进论文。
- 候选摘要 = 所选句子的拼接；unigram 计数与句子顺序无关，所以 f 是良定义的集合函数。

## 4. 三个 surrogate f̃（都只看文章，从不接触参考摘要）

原稿 `SubModular.ipynb` 缺失（`data/INVENTORY.md` 已记录），**原参数不可得**，以下为本次选定的标准形式与参数，
全部写死在 `results/E3_run.py` 顶部常量里：

| f̃ | 定义 | 参数 |
|---|---|---|
| `coverage` | `C(S) = Σ_{w∈doc 词表} min(tf_S(w), α·tf_doc(w))`（saturated coverage） | `α = 0.25` |
| `diversity` | `D(S) = Σ_i sqrt( Σ_{s∈S∩P_i} r_s )`，`r_s = (1/n)Σ_j sim(j,s)` | 簇数 `k = max(2, round(0.2·n))` |
| `facility` | `FL(S) = Σ_{i∈句子} max_{j∈S} sim(i,j)` | — |

- `sim` = 句子 tf 向量的余弦（原始词频，不用 tf-idf；按 E3 说明"sim = tf 向量余弦"）。
- `diversity` 的聚类**没有随机性**：farthest-first traversal（k-center 贪心），
  第一个中心 = `argmax r_s`（并列取小下标），之后每次取"到已有中心的最小余弦相似度最低"的句子，
  最后每句归到最相似的中心。不用 k-means，不用 RNG。
- `diversity` 是 Lin–Bilmes 型 `C + λ·D` 里的纯 D 部分，作为独立 f̃ 评分，因此 λ 无关
  [CITATION-NEEDS-VERIFICATION：Lin & Bilmes 的确切年份/会议在定稿时核对]。
- 三个 f̃ 都是单调 submodular，CELF 合法（下节有实测核对）。**全程 `quantize=None`**。

## 5. η 的度量口径（一个必须交代的细节）

`η^path` 的 ε = 0.005（TASKS_EXP 规定的摘要任务量化单位）。但三个 f̃ 的量纲各不相同
（词频 / sqrt-reward / 相似度求和），而 0.005 是 ROUGE-F 的单位。`η^path = max(d/d̃)·max(d̃/d)` 本身是
**尺度不变**的，只有 ε 裁剪不是。因此统计前把 d̃ 乘一个**每篇每 surrogate 一个常数**

    c = max_e d_e(∅) / max_e d̃_e(∅)

（两个 max 都在 S=∅ 上取），使 ε 对两侧对称。这个常数只用于测量，不进入任何 greedy；
`E3_pairs.csv.gz` 里落盘的是**未缩放的原始 d̃**，而 c 可以从该文件 `step==0` 的行重算，所以口径可复核。
`η^sel` 只用真值，与尺度无关。

必须强调：f 只在**测量**（η、ratio、d≤0 统计）里出现；产生 `S_greedy^{f̃}` 的 greedy 从头到尾只调用 f̃。
不存在人工扰动 oracle，也不存在从 f 到 f̃ 的信息泄露。

`ratio` 的分母是同一篇文章上的 greedy-on-f（同管线、同 cache），是 OPT 的**上估代理**，
所以 ratio 是对真实近似比的**低估**。本次 300×3 条轨迹里 ratio > 1 的比例 = **0.0%**。

---

## 6. 主结果（由 `results/E3_summary.json` 转写）

| f̃ | K | n | ratio 中位数 | ratio IQR | η^sel 中位数 | η^sel q90 | η^sel max | η^path 中位数 | L_K(η^sel) 中位数 | d≤0 步 % | d≤0 候选对 % | 方向违反 % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| coverage | 3 | 299 | 0.777 | [0.670, 0.858] | 2.19 | 8.8 | 2882 | 15.5 | 0.3901 | 7.6 | 5.1 | 7.5 |
| coverage | 4 | 299 | 0.735 | [0.643, 0.834] | 2.90 | 17.0 | 2882 | 18.6 | 0.3027 | 14.7 | 8.8 | 12.6 |
| coverage | 5 | 293 | 0.712 | [0.635, 0.800] | 3.54 | 20.8 | 2882 | 21.0 | 0.2523 | 19.2 | 12.3 | 16.6 |
| coverage | 6 | 289 | 0.701 | [0.633, 0.784] | 4.14 | 26.2 | 2882 | 23.2 | 0.2187 | 24.6 | 15.5 | 20.1 |
| coverage | 7 | 279 | 0.711 | [0.644, 0.780] | 5.00 | 32.9 | 2882 | 24.7 | 0.1835 | 28.0 | 18.2 | 22.7 |
| diversity | 3 | 299 | 0.647 | [0.533, 0.754] | 5.73 | 26.3 | 1076 | 32.1 | 0.1645 | 5.0 | 3.4 | 5.4 |
| diversity | 4 | 299 | 0.645 | [0.548, 0.739] | 7.83 | 32.9 | 3961 | 34.5 | 0.1218 | 8.9 | 5.6 | 8.8 |
| diversity | 5 | 293 | 0.662 | [0.569, 0.755] | 9.90 | 52.6 | 3961 | 34.8 | 0.0970 | 12.0 | 8.1 | 12.2 |
| diversity | 6 | 289 | 0.669 | [0.591, 0.772] | 11.21 | 53.5 | 3961 | 35.4 | 0.0859 | 15.8 | 10.5 | 15.5 |
| diversity | 7 | 279 | 0.690 | [0.614, 0.780] | 12.61 | 61.3 | 3961 | 36.5 | 0.0767 | 18.1 | 12.7 | 17.9 |
| facility | 3 | 299 | 0.679 | [0.567, 0.768] | 3.92 | 24.6 | 492 | 30.9 | 0.2340 | 7.8 | 3.9 | 6.1 |
| facility | 4 | 299 | 0.641 | [0.540, 0.742] | 6.28 | 43.3 | 523 | 34.0 | 0.1499 | 13.7 | 6.1 | 9.3 |
| facility | 5 | 293 | 0.628 | [0.535, 0.716] | 9.34 | 76.4 | 5776 | 35.9 | 0.1026 | 17.5 | 8.1 | 11.8 |
| facility | 6 | 289 | 0.619 | [0.551, 0.703] | 11.72 | 94.5 | 8229 | 36.2 | 0.0824 | 21.2 | 9.7 | 13.8 |
| facility | 7 | 279 | 0.626 | [0.562, 0.721] | 16.84 | 105.8 | 8229 | 36.8 | 0.0579 | 23.6 | 11.0 | 15.2 |

列的口径：
- `d≤0 步 %`：greedy-on-f̃ 轨迹前 K 步中，**被选中元素的真实增益 ≤ 0** 的步数占比。这些步按
  `src/statistics.py` 的规定从 η^sel 的 max 中剔除并单独计数（不是丢掉不看）。
- `d≤0 候选对 %`：前 K 步所有 (状态, 候选) 对里 d ≤ 0 的占比。
- `方向违反 %`：`|d| ≥ ε 或 |d̃| ≥ ε` 的候选对中 d 与 d̃ **严格反号**的占比（`TrajectoryStats.viol_sign_pct` 的均值）。

按类目 × surrogate（K=5）：

| 类目 | f̃ | n | ratio 中位数 | η^sel 中位数 | d≤0 步 % | 方向违反 % |
|---|---|---|---|---|---|---|
| business | coverage | 100 | 0.662 | 4.01 | 24.4 | 20.3 |
| business | diversity | 100 | 0.648 | 8.76 | 14.8 | 15.1 |
| business | facility | 100 | 0.588 | 10.83 | 21.2 | 14.3 |
| sport | coverage | 94 | 0.737 | 2.75 | 22.8 | 20.5 |
| sport | diversity | 94 | 0.708 | 9.42 | 15.1 | 16.5 |
| sport | facility | 94 | 0.639 | 7.81 | 21.3 | 15.5 |
| tech | coverage | 99 | 0.725 | 4.18 | 10.5 | 9.1 |
| tech | diversity | 99 | 0.609 | 10.86 | 6.3 | 5.2 |
| tech | facility | 99 | 0.638 | 10.16 | 10.3 | 5.8 |

读数（只陈述数据支持的事）：
- 三个 f̃ 里 **coverage 最好**：ratio 中位数最高（K=5 为 0.712）且 η^sel 中位数最低（3.54）。
  两个指标方向一致，这一点在三个类目上都成立（表二）。
- η^sel 随 K 单调上升（后面的步越来越难有正增益），d≤0 步占比也随 K 上升，两者是同一现象的两面。
- η^sel 的尾极重：中位数个位数，最大值到 10³–10⁴。这些极值全部来自"被选中元素的真实增益是极小正数"
  的步（分母趋 0），不是 f̃ 选错了大东西。用中位数/分位数汇报，均值无意义。
- 认证下界基本失效：K=5 时 `L_K(η^sel)` 中位数只有 0.10–0.25，而实测 ratio 中位数 0.63–0.71；
  ratio > L_K(η^sel) 的行占 96.6% / 99.7% / 98.6%（coverage / diversity / facility）。
  这正是 E5 money plot 想要的图景：真实任务的点远在最坏情况曲线上方。**不能**因此说定理"保守得没用"——
  ROUGE 本来就不满足定理的前提（见下节），这里的 L_K 只是把同一把尺子放到边界外读一次。

## 7. 结构检验：f 确实在模型之外（实测，不是断言）

`E3_run.py::structure_check` 对每 10 篇取 1 篇（3 类共 30 篇），在每篇前 8 个句子上**穷举**
所有 `A ⊆ B = A∪{b}`（`|A| ≤ 3`）与元素 e，检查 `d_e(A) ≥ d_e(B)`（submodular）与 `d_e(A) ≥ 0`（单调），
共 70,560 个三元组：

| 函数 | 三元组数 | submodular 违反 | 违反率 | 最大违反幅度 | 单调违反率 |
|---|---|---|---|---|---|
| ROUGE-1 F (= f) | 70560 | 1508 | **2.14%** | 0.0203 | **7.12%** |
| coverage (f̃) | 70560 | 0 | 0.00% | 0.0 | 0.00% |
| diversity (f̃) | 70560 | 0 | 0.00% | 0.0 | 0.00% |
| facility (f̃) | 70560 | 0 | 0.00% | 0.0 | 0.00% |

状态标签：[VERIFIED-LP]（穷举 oracle，脚本 `results/E3_run.py --limit 100` 会重跑并写进
`E3_summary.json.structure_check`）。作用域限于"每篇前 8 句、|A| ≤ 3"这个窗口内的穷举，**不是**全格点。
结论只写到：ROUGE-1 F 在真实文章上确实同时违反单调与 submodular；三个 f̃ 在同一窗口内一次都没违反，
与它们各自的标准结构（saturated coverage / sqrt-of-modular / facility location 均单调 submodular）一致，
所以对 f̃ 用 CELF 是合法的。

## 8. CELF 用在非 submodular 的 f 上（分母 greedy）的偏差

分母 `greedy on f` 按原则 2 也走 `lazy_greedy`，但 f 不 submodular 时 CELF 的惰性没有理论保证。
脚本对每篇同时跑一遍**非惰性精确 greedy**做对照：

- K = 3, 4, 5：偏差比例 **0.00%**（lazy 从未比 exact 差）。
- K = 6：**1.04%** 的文章 lazy 更差，最大差 0.0263（ROUGE-F 绝对值）。
- K = 7：**1.08%**，最大差 0.0122。

影响方向：分母偏小 → ratio 被**高估**，且只发生在 ~1% 的 K≥6 行上，量级 ~0.01–0.03。
如实记录，不做修正（修正就违反"统一管线"）。若审稿人追问，可以把 K≥6 的分母换成 exact greedy 重跑，
脚本里 `exact_greedy` 已经在算，改一行即可。

## 9. 诚实声明 / caveats

1. `ratio` 的分母是 greedy-on-f 而非 OPT，是 OPT 的上估代理，ratio 因此是低估；这一点在每张表下重复。
2. sport / tech 的参考摘要**不来自仓库**，来自外部 CSV 回填（第 1 节给了核对证据与失败案例 tech/048）。
   在 `data/` 补齐之前，E3 不是"纯本地可复现"的。
3. ROUGE 实现是自写的简化版（无停用词处理、无 stemming），与官方 ROUGE-1.5.5 的绝对分数不可比。
4. 句子切分是正则的，标题单独成句是一个**选择**，换成并入正文会改变 ground set 与所有数字。
5. η^path 的 ε 裁剪依赖第 5 节的尺度归一化；换归一化方式会改变 η^path（不会改变 η^sel、ratio、方向违反）。
6. K=7 的样本量小于 K=3（sport 尤其），跨 K 比较时要看 n 列。
7. 全程无随机数：`seed` 列是文章编号，不是随机种子；重复运行逐位相同。
8. 三个 f̃ 的参数是本次选定的标准形式，**不是**原稿参数（原稿 notebook 缺失），论文里必须这么写。
