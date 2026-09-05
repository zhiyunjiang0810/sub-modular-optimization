# G5_review.md 对抗审稿报告（只读子代理，第五晚 G5）

生成时间：2026-09-05。审稿对象：`paper/main.pdf`（25 页，abstract 与 introduction 为
占位，按任务要求不攻击其缺失）与全部 `paper/sections/*.tex`、`paper/references.bib`。

## 0 输入说明与一处必须记录的缺失

- **`PROJECT_INSTRUCTIONS` 在本仓库不存在。** 已核查：`ls PROJECT_INSTRUCTIONS*` 返回
  "No such file or directory"，仓库根目录下 `find -maxdepth 2 -iname "*PROJECT*"` 零命中，
  全部 `.md` 文件清单里也没有同名或近名文件。TASKS5 G5 里"TPAMI 两位审稿人的意见要点
  （在 RESEARCH_STATE 已知的论文错误与 PROJECT_INSTRUCTIONS 叙事节）"这条输入只兑现了
  一半。本报告因此**只依据 `RESEARCH_STATE.md` 的"已知的论文错误"节与文末 D1/D2 决定块**，
  以及 `GLOSSARY.md`、`CLAUDE.md`。原审稿人意见的叙事部分无法复现，本报告中凡涉及"原审
  稿人抱怨了什么"的推断都已避免，改为按 ICLR 审稿维度独立发起攻击。
- 审稿期间仓库处于**并行写入状态**（G4/G6 子任务在 16:04-16:12 之间改写了
  `sections/statements.tex`、`sections/numbers.tex`、`sections/appendix_experiments.tex`、
  `sections/EXP_table.tex` 并重编译 `main.pdf`）。本报告的所有引用与数字核对已在
  16:12 之后的版本上重跑一遍，结论以该版本为准。
- 本报告**不改动任何正文文件**，唯一落盘文件是本文件。

## 1 最具杀伤力的五条（Top-5）

| # | 级别 | 一句话 | 位置 |
|---|---|---|---|
| **T1** | 严重 | Proposition 4（`prop:guarantee`）按其自己写下的假设是**假命题**，且论文自己的实验数据里有 **63 行 run 实测 ratio 低于 L_K(η^sel)**，其中 38 行的 η^sel 恰为 1.0。漏洞出在"零增益步骤不进 η^sel"这一条：附录 Step 2 用**全局 band** 补住了它，而定理陈述里根本没有全局 band 这个假设 | `results.tex:35-46`；`model.tex:40-58`；`appendix_proofs.tex:178-196` |
| **T2** | 严重 | 全文头号定理 Theorem 8（`thm:exact`）的 ≥ 方向唯一支撑是 Appendix B.9（`app:validity`），该小节自己写着"No script checks the derivations of this subsection"，状态是 `[HAND-PROOF-UNREVIEWED]`。但这个状态只存在于 LaTeX **注释**里，PDF 读者完全看不到 | `results.tex:126-139`（注释）；`appendix_proofs.tex:1165-1172, 1332-1334` |
| **T3** | 严重 | Theorem 12（`thm:hardness`）的**定理陈述本体**里含 `[CONJECTURE]`：δ 的闭式以及事实 (F2)(F3)(F4)（其中 (F2) 包含"F_O 是 monotone submodular"与"误差恰为 η"）在一般 (K,τ,η) 下只是猜想，只在 40 个有限点 `[VERIFIED-LP]` | `results.tex:202-228`；`appendix_proofs.tex:1018-1024, 1103-1104` |
| **T4** | 严重 | D2 把 L_K 保证降为 Proposition 并归给 Goundan-Schulz 之后，novelty 承重全压在 ρ_K 与 hardness 上；而 Theorem 6（per-K tightness）的构造里**每一步全部 2K−t 个候选并列**，整条"紧性"只由 adversarial tie 规则撑起，正文对此只字未提 | `results.tex:66-80`；`appendix_proofs.tex:353-371` |
| **T5** | 严重 | Figure 1 的 caption 断言 "Real tasks sit far above both curves"，被自己的数据证伪：K=5 左面板上有 **15 行**低于 L_K 曲线；同一面板还有 **10 个点被截断在坐标轴外**（图内注记 "10 pts beyond"），正文对这 10 个点一字未提 | `experiments.tex:84-95`；`figures/money_plot.pdf` |

---

# A. ICLR 四维攻击

## A.1 Novelty（原创性）

### N1 [严重] D2 之后，本文的正面结果为零，reviewer 会直接问"算法上新在哪"

- **位置**：`results.tex:35-50`（Proposition 4 + D2 措辞）；`related.tex:34-51`
  （"We differ in the question, not the bound"）；`model.tex:47-51`。
- **为什么伤**：D2 已把 L_K 保证定性为 "essentially due to Goundan and Schulz (2007,
  Theorem 1)"，并且 `model.tex:50-51` 明说 η^sel 就是他们的 α。于是：算法是他们的
  （greedy with α-approximate incremental oracle），保证是他们的定理，误差度量 η^sel
  与他们的 α **数值相等**（`related.tex:38` 原文："whose α ≥ 1 is exactly the selection
  error η^sel"）。剩下的三件事里，Theorem 6 是一族构造（见 N2，且被 tie 规则架空），
  Theorem 8 是同一个已知算法的最坏值刻画，Theorem 12 的关键步骤是猜想（T3）。ICLR 的
  reviewer 对"给已知算法算出精确最坏常数"这类工作的默认反应是 "solid but incremental"，
  而本文连唯一的新算法接口（η^sel）都承认是旧的重命名。更糟的是被引来源
  `goundan2007revisiting` 是 `@techreport`，note 字段写着 "Optimization Online preprint
  1740"，即**未经同行评议的 2007 预印本**（`references.bib:53-59`）。reviewer 会追问：
  既然核心保证归属于一篇未发表预印本，是否说明它其实是 folklore？若是 folklore，
  "restated"这个措辞是否又高估了它的引用价值？
- **建议修法**：正文必须有一段（放在 intro 或 §4 开头）明确写出**"新在哪、旧在哪"的分账
  表**，三行即可：(a) 保证曲线 L_K 与其误差度量 α = η^sel：旧，GS 2007；(b) 精确最坏值
  ρ_K = min_j V_j 与其对偶证书：新；(c) bounded-query 障碍：新但依赖 (T3) 的猜想。
  同时把 `related.tex` 那句 "We differ in the question, not the bound" 提到 §1 的
  contributions 里，别藏在 related work 第一段结尾。另外补一句 GS 之外的 fallback 引用
  （若 L_K 确为 folklore，找一条已发表的出处并列引），以免整篇论文的地基挂在一篇预印本上。

### N2 [严重] Theorem 6 的"per-K tightness"是 tie-breaking 的产物，不是 prediction error 的产物

- **位置**：`results.tex:68-74`；证明在 `appendix_proofs.tex:353-371`（Step 6）。
- **为什么伤**：附录 Step 6 自己写得清清楚楚："every candidate is a maximizer and the step
  is a tie among all 2K−t of them"。也就是说在这族实例上，predictor 对**每一步的每一个候选
  给出完全相同的预测增益**，它没有提供任何排序信息；greedy 之所以输，纯粹是因为 adversary
  被允许在全并列里挑 B。换任何一条确定性 tie 规则（例如"选下标最小"配合把 O 排在前面），
  同一实例上 greedy 立刻返回 O，ratio = 1。于是"Proposition 4 is an equality on this family
  for every K"这句话的真正内容是"存在一个 predictor 什么都不说、且 adversary 掌管 tie 的
  实例"，这远弱于读者读到 "Tightness for every K" 时的理解。对照 `thm:exact`，附录在
  `appendix_proofs.tex:858-867` 为 V_j 族补了严格偏好下的 infimum 论证；**Theorem 6 没有对应
  的补丁**，所以在严格偏好下这条"紧性"目前什么都不是。
- **建议修法**：两条二选一。(i) 把 Theorem 6 的陈述改成"under adversarial tie breaking,
  and the ties are total at every step"，并在正文加一句说明 tie 规则是 load bearing、
  在严格偏好下该值只是 infimum；(ii) 照搬 `appendix_proofs.tex:858-867` 的 ε 扰动做法给
  U_K 族也补一个严格偏好版本（把 f 里的 â 换成 â′ < â 而 band 仍按 â 声明），把结论改写为
  "attained in the limit of strict preferences"。无论哪条，正文都必须出现"每一步全并列"
  这个事实，它现在只在附录里。

### N3 [中等] 与 learning-augmented algorithms 的定位没有对齐，consistency 那一栏是空的

- **位置**：`related.tex:83-107`（LAA 段）；`GLOSSARY.md` 第 8 行对 consistency 的定义。
- **为什么伤**：论文在 related work 里主动引入了 LAA 框架和 consistency 的 LAA 含义
  （`related.tex:86-87`），但从不回答 LAA 读者的第一个问题：**本文在 η = 1 时的
  consistency 是多少？** 答案是 ρ_K(1) = 1 − (1−1/K)^K → 1 − 1/e，**不是 1**。也就是说，
  即使预测完美，predictive greedy 也只拿到 1−1/e，这在 LAA 的话语里叫 "not consistent"。
  一个 LAA 背景的 reviewer 会说：你把自己摆进 LAA 的邻居里，却既没有 consistency 也没有
  （按 GLOSSARY 已禁用的）robustness，那么"prediction"这个框架在本文里到底买到了什么？
- **建议修法**：在 `related.tex` LAA 段末尾或 §4.5 后加两句：明确写出 η = 1 时
  ρ_K(1) = 1 − (1−1/K)^K 正是 Nemhauser 界（这一点其实是本文闭式的一个漂亮推论，
  目前完全没被利用），并说明本文不追求 LAA 意义上的 consistency，因为完美的 marginal-gain
  预测并不等于免费的 exact oracle（后者才对应 1−1/e 的不可超越性）。这样既堵住攻击，
  又白捡一个 sanity check。

### N4 [中等] 仓库里已经有比 Theorem 12 更强的版本，论文却用了弱版

- **位置**：`results.tex:206-221`（"each on a set of size at most K"）；对照
  `results/F3_summary.md:15` 与 `:272`（"对任意大小查询的 hardness 定理草稿"，
  预算 `Q = Ω(n²/((2+η)²K⁴))`，即 `n^{2−o(1)}` 次**任意大小**查询），成文在
  `results/F3_hardness_full.tex`。
- **为什么伤**：论文的 hardness 定理带 query-size cap（见 C.4 与 B 段 V16），而本仓库第四晚
  的 F3 已经把 size cap 拆掉了（机制：G 在 x > T 之后自动 O-无关）。reviewer 若拿到
  supplementary（reproducibility statement 承诺会给），会看见一个更强的草稿没进正文，
  这在评审里读起来像是"作者自己也不信那个更强的版本"。
- **建议修法**：要么把 F3 的任意大小版本以 Theorem 或 Proposition 形式收进正文/附录并注明
  其独立状态，要么在 §4.8 加一句脚注说明为什么本文选择 size-capped 版本
  （例如 F3 版本的预算指数 2 是该族内在上限、与 n^c 的参数化不兼容），把选择变成一个
  被解释过的决定而不是一个空缺。

---

## A.2 Soundness（正确性）

### S1 [严重] Proposition 4 按其陈述的假设是假命题（附一个两元素反例）

- **位置**：陈述 `results.tex:35-46`；η^sel 定义 `model.tex:40-58`；证明的漏洞在
  `appendix_proofs.tex:178-196`（Step 2）。
- **为什么伤**：Definition 2 把 η^sel 定义成
  `max{ max_{e∉S^t} d_e(S^t) / d_{e_t}(S^t) : t<K, d_{e_t}(S^t) > 0 }`，
  **明确排除了"所选元素真增益为 0"的步**。Proposition 4 的假设只有两条：f monotone
  submodular、T 是一次 selection error 为 η^sel 的 predictive greedy run。附录 Step 2 想补
  这个洞，用的却是 **Definition 1 的全局 band**（原文：`By Definition 1,
  d̃_{e_t}(S^t) ≤ η_o d_{e_t}(S^t) = 0 ... the lower band ... then forces d_e(S^t) = 0`）。
  可是 Definition 1 根本没有出现在 Proposition 4 的假设里，整篇论文把 Proposition 4
  卖点定位成"只收 η^sel 的钱、不收全局 band 的钱"（`appendix_proofs.tex:1307-1320` 的
  `rem:app-rulers` 就是这么写的）。于是命题在字面上是假的。**反例**（K=1，N={a,b}）：
  f(∅)=0, f({a})=0, f({b})=1, f({a,b})=1（monotone、submodular 都成立，逐对可验），
  f̃({a})=1, f̃({b})=0。predictive greedy 选 a，该步 d_{e_0}(∅)=0 被 Definition 2 排除，
  于是 η^sel 取在空集上，按定义"≥1"读作 1，L_1(1) = 1，命题断言
  f(T) = 0 ≥ 1·f(O*) = 1，假。
- **这不是学院派抬杠：论文自己的数据上它真的发生了。** 我按论文自己的公式
  `L_K(x)=1-(1-1/(xK))^K` 逐行重算 E1/E2/E3 的 12,057 行（K≥2），得到：
  - **63 行满足 ratio < L_K(η^sel)**，全部来自 E3；另有 **70 行 ratio < ρ_K(η^sel)**；
  - 这 63 行**全部** `frac_steps_nonpos > 0`（中位数 0.60，全体 E3 中位数 0.143），
    其中 **38 行的 η^sel 恰等于 1.0**；
  - 最坏的几例（gap = L_K − ratio）：`sport_coverage K=4, η^sel=1.0, ratio=0.4153,
    L_4(1)=0.6836`（差 0.268）；`sport_coverage K=3, η^sel=1.0, ratio=0.4628,
    L_3(1)=0.7037`；`business_coverage K=7, η^sel=1.0, ratio=0.5225, L_7(1)=0.6601`。
  - 复现方式：读 `results/E1_rows.csv`、`E2_rows.csv`、`E3_rows.csv` 的
    `ratio`/`eta_sel`/`K`/`frac_steps_nonpos` 四列，逐行比较 `ratio` 与
    `1-(1-1/(eta_sel*K))**K`。注意 ratio 的分母还是 greedy-on-f（OPT 的**上估**代理），
    所以真实的 f(S^f̃)/f(OPT) 只会比这更低，违反只会更多。
  - 机制完全对得上：η^sel = 1 意味着"每个**正增益**步都选了真 argmax"，而 E3 有 20% 的步
    真增益非正，轨迹恰恰在这些被排除的步上偏离，损失全部发生在 η^sel 看不见的地方。
- **建议修法**（三选一，我推荐第一条）：
  1. 给 Proposition 4 补上它实际需要的假设：`(f, f̃) satisfies Definition 1 for some finite
     (η_u, η_o)`。这样 Step 2 的论证合法，命题为真，代价是"只收 η^sel 的钱"这个卖点要
     诚实降级为"η^sel 决定常数，Definition 1 决定可用性"。
  2. 改 Definition 2：当存在某步 d_{e_t}(S^t)=0 而 max_{e∉S^t} d_e(S^t) > 0 时，令
     η^sel = ∞。这样命题在无额外假设下为真，代价是 E1 的 21.4%、E3 的 20.0% 非正步会把
     大量 run 的 η^sel 打成 ∞，Table 1 的 L_K 列要重算。
  3. 把 Proposition 4 的结论限制在"到第一个非正步为止的前缀"上，并在 Table 1 里明确
     这一列只对前缀有效。
  无论选哪条，**Table 1 note (ii) 现在那句 "the certified bound in the L_K column is a
  statement about those steps" 必须重写**：它把一个关于 f(T)/f(O*) 的界说成"关于某些步的
  陈述"，这在逻辑上不成立，界要么覆盖输出要么不覆盖。

### S2 [严重] Theorem 8 的下界方向压在一个没有任何 oracle 的手证上，而状态标签读者看不到

- **位置**：`results.tex:126-139`（状态注释）；`appendix_proofs.tex:1165-1172`
  （`app:validity` 的 STATUS 注释，`[HAND-PROOF-UNREVIEWED]`）；
  `appendix_proofs.tex:1332-1334`（可见正文："No script checks the derivations of this
  subsection"）；`appendix_proofs.tex:1298-1305`（`rem:app-status`）。
- **为什么伤**：Theorem 8 是 ρ_K(η) = min_j V_j 的**等式**。等式的链条是
  (a) 每次真实 run 都是 reduced LP 的可行点 ⇒ LP 值 ≤ ρ_K；(b) 对偶证书 ⇒ LP 值 ≥ V_j；
  (c) 显式实例 ⇒ ρ_K ≤ V_j。(b) 是 `[VERIFIED-SYMBOLIC]`，(c) 是 `[VERIFIED-SYMBOLIC]`，
  **(a) 是纯手证、无 oracle**，而 (a) 恰恰是"greedy 永远不会更差"这个正面方向的全部内容。
  CLAUDE.md 第 5-7 行的规则是"没有 oracle 确认的断言一律标 tag，不准写 proved"，而 LaTeX
  的 `\begin{theorem}` 环境在读者眼里就是 proved。更关键的是：**所有状态标签都写在 `%` 注释
  里**，编译后一个字都不进 PDF。我用 `mutool draw -F txt` 逐页导出 25 页，PDF 里
  `[HAND-PROOF-UNREVIEWED]`、`[CONJECTURE]`、`[VERIFIED-LP]` 出现次数为 0。于是论文对内
  维持了一套诚实的状态体系，对外呈现的却是一份全部"已证"的稿子。
- **建议修法**：把状态从注释提到**可见文本**。最省页数的做法是在附录开头加一张
  "verification status" 小表（每行：定理号 / 哪一步 / 由哪个脚本核验 / 哪一步只有手证），
  正文每条定理后面挂一个 `\ref` 指过去。特别地，`app:validity` 的 `rem:app-status` 已经写得
  很好（承认反方向不 claim），把它**提到 Theorem 8 正下方作为一条可见 Remark**，代价一行，
  收益是把"审稿人自己发现"变成"作者主动披露"。另外，`appendix_proofs.tex:871-872` 那句
  "The identities of this proof are machine-checked by results/N2_check.py" 容易被读成整条
  证明都被机器核过，建议改成"the dual identities and the instance identities are
  machine-checked; the relaxation step of Appendix B.9 is not"。

### S3 [严重] Theorem 12 的陈述里内嵌 [CONJECTURE]

- **位置**：`results.tex:202-204`（δ 的闭式，写在定理**之前**的正文里）、`results.tex:206-221`
  （定理本体："single-element error exactly η"）、`results.tex:222-228`（状态注释：
  "the delta closed form [VERIFIED-LP at 40 finite points, general (K,tau,eta) CONJECTURE]"）；
  `appendix_proofs.tex:1018-1024`（事实 (F1)-(F4) 与其状态）、`appendix_proofs.tex:1103-1104`
  （"That no other pair of sets binds harder is the part supplied by the linear program
  rather than by hand"）。
- **为什么伤**：定理断言存在一个实例，其中 (i) f 是 monotone submodular，(ii) single-element
  error **恰为** η。这两条都装在事实 (F2) 里，而 (F2) 的状态是"在 N5 的有限测试集上
  `[VERIFIED-LP]`、一般 (K,τ,η) 下 `[CONJECTURE]`"。δ 的闭式同理，附录 Step 3 只手算了
  strip 内部的四类边，"没有别的集合对把界绷得更紧"这句话交给了 LP。换句话说：**如果真实的
  最小 s 比 max{a^τ K/(K−τ), a^{1−τ}} 大，那么这族实例的误差就超过 η，定理里"error exactly
  η"这句话为假，整条 hardness 结论作废。** 这是 ICLR reviewer 最容易一击致命的位置：定理
  陈述本身依赖一个未证的等式。附录的 STATUS 注释还额外记了一条极不利的事实："N5 records
  that this max-form CORRECTS the single-branch form of T2 Conclusion 1, which the oracle
  refutes at 8 of those 40 points"，即这个闭式**上一版本已经被 oracle 推翻过一次**。
- **建议修法**：把 Theorem 12 改成**条件定理**，形式为"Assume the family of Appendix B.8
  has single-element error exactly Φ(θ) (verified for the parameter set of Table X; proved
  for τ = 1). Then ..."，并把 τ = 1（此时第二支恒为 1，δ 只剩单支，手算可闭合）的情形单独
  提成一条无条件的 Corollary。这样正文里至少有一条**无条件**的 bounded-query 下界，
  而一般 τ 的版本诚实地挂上假设。另外建议把"哪 40 个点被验过"以表格形式放进附录，
  reviewer 才有办法判断猜想的覆盖度。

### S4 [中等] Proposition 3 缺算法类别限定，且在自己的边界参数上是平凡真

- **位置**：`results.tex:21-27`。
- **为什么伤**：两处。(1) 陈述写的是 "for every algorithm with arbitrary query access ...
  the output T satisfies f(T) ≤ K/(n−K) f(O*)"。对随机算法，T 是随机变量，这句话在字面上
  只能在期望意义下成立，而附录 `appendix_proofs.tex:115-131` 也确实只证到期望。
  GLOSSARY 第 16 行是硬规定："声明任何下界时必须写明适用的算法类别，缺省即空洞"。
  对照 Theorem 10（`results.tex:167-175`）就规规矩矩写了 deterministic / randomized 两支，
  Proposition 3 却没有，**同一节里两种标准**。(2) 常数在 n = 2K 处是 K/(n−K) = 1，即命题
  在其自身允许的最小 n 上退化成"f(T) ≤ f(O*)"，恒真。真正的内容需要 n → ∞，这句话只在
  附录最后一行出现（"Letting n → ∞ with K fixed drives the right side to 0"），正文的
  "Consequently no constant worst-case ratio is achievable" 因此是一个没有交代前提的跳跃。
- **建议修法**：改成 "For every deterministic algorithm ... f(T) ≤ K²/(n(n−K)) f(O*);
  for randomized algorithms the expected ratio is at most K/(n−K). Letting n → ∞ with K
  fixed, no ratio bounded away from 0 uniformly in n survives."（顺带把确定性情形更强的
  常数 K²/(n(n−K)) 亮出来，附录本来就证了，现在被随机化的弱常数吞掉了）。

### S5 [中等] Remark 13 里"K evaluations of f̃ per step"是错的，而且这个数正是与 Theorem 12 对比的关键

- **位置**：`results.tex:230-237`。
- **为什么伤**：predictive greedy 在状态 S^t 上要对**每个** e ∉ S^t 求 d̃_e(S^t)，即每步
  n − t 次 f̃ 求值，全程 Θ(nK) 次，不是"K evaluations per step"。这不只是笔误：Remark 13
  的整句话是"greedy 达到 L_K(η)、而预算内的算法超不过 L_K(η̂)"，要成立就必须先说明
  **greedy 自己落在 Theorem 12 的预算里**。而 Theorem 12 的预算是 n^c 次、每次集合大小 ≤ K。
  greedy 用 Θ(nK) 次大小 ≤ K 的查询，落进 n^c 需要 nK ≤ n^c，即 K ≤ n^{c−1}：**c = 1 时
  除非 K = 1 否则不成立**，要 c ≥ 2 才自动成立（此时 τ = 3、K ≥ 6、n ≥ 4K⁴）。也就是说
  "pinned"这个词在 c = 1 时并没有被证成，Remark 13 完全没有讨论这一点。
- **建议修法**：把该句改为 "predictive greedy uses at most nK queries, each on a set of
  size at most K, which lies inside the budget of Theorem 12 whenever c ≥ 2"，并把 c = 1
  的缺口列入 conclusion 的 open problems（`conclusion.tex` 目前只列了 finite-K gap、
  submodular surrogate、all-pairs 三条，加这条正合适）。

### S6 [中等] §4.6 的 1/η 天花板与 §4.8 的 hardness 在正文里看起来互相矛盾，调和只写在注释里

- **位置**：`results.tex:167-178`（Theorem 10，含 "exhaustive search over all K-subsets ...
  achieves f(Ŝ) ≥ f(O*)/η on every instance"）；`results.tex:199-237`（Theorem 12 + Remark 13）；
  调和只在 `appendix_proofs.tex:937-939` 的 `%` 注释里（"GLOSSARY.md, any algorithm: this
  whole subsection lives in range (i) ... the two must not be quoted interchangeably"）。
- **为什么伤**：读者在第 4 页先读到"穷举 K-子集可以拿到 1/η"，两小节后读到"n^c 次、
  大小 ≤ K 的查询拿不到超过 L_K(η̂) → 1 − e^{−1/η}"。而 1/η **严格大于** 1 − e^{−1/η}
  （η=1: 1.000 vs 0.632；η=1.5: 0.667 vs 0.487；η=2: 0.500 vs 0.394；η=4: 0.250 vs 0.221），
  两条定理里的算法**查询的集合大小都 ≤ K**，唯一的区别是次数（C(n,K) vs n^c）。正文里没有
  任何一句话点破这一点，读者必须自己回去数查询次数。这是 clarity 问题，但它伤的是
  soundness 的观感：reviewer 的第一反应是"这两条冲突"。
- **建议修法**：在 Theorem 10 后面加一句可见的桥："The matching algorithm uses C(n,K)
  queries; Theorem 12 shows that the gap between 1/η and 1 − e^{−1/η} is exactly what a
  polynomial query budget costs."两行，把冲突变成卖点。

### S7 [中等] η^tr 的 trimming 是事后的、单边的、且论文的核心修辞完全靠它

- **位置**：`appendix_experiments.tex:27-37`；正文用处 `experiments.tex:106-111`。
- **为什么伤**：论文的核心修辞是"要在 η^sel 上读保证，不要在 η（或 η^tr）上读"，证据是
  E1 在 η^sel = 2.0 时保证 0.405、在 η^tr = 19.4 时只剩 0.050。但 η^tr = 19.4 是**修剪过**的：
  附录明说只统计"真增益与预测增益都超过一个量化单位"的候选对。不修剪的话 η^tr（以及 η）
  在这些 surrogate 上是 **∞**（accuracy 量化导致 d = 0 而 d̃ > 0），保证是 0。也就是说
  真实的对比是"0.405 vs 0"，而不是"0.405 vs 0.050"。附录把方向说清楚了（修剪让 η^tr 偏小、
  让 L_K(η^tr) 偏大，两边都有利于 η^tr），这一点是诚实的；但仍有两个可攻击处：
  (a) 修剪只施加于 η^tr，从不施加于 η^sel，而 η^sel **在定义上就不会发散**（分母恒正，
  零增益步被排除），所以两把尺子的"有限性"是结构性不对称，不是测量结果；
  (b) "一个量化单位"这个阈值是 per-dataset 的、事后选的，正文里没有敏感性分析。
- **建议修法**：正文那句改成"the untrimmed trajectory error is infinite on these
  surrogates, since predicted gains can be positive where the true gain is exactly zero;
  with a quantization-unit trim it has median 19.4, at which the bound is 0.050"。
  另在附录加一条阈值敏感性（阈值 ×0.5、×2 时 η^tr 中位数怎么动），三行表格即可。
  更重要的是承认 (a)：η^sel 的有限性来自定义排除了零增益步，这正是 S1 的漏洞所在，
  两处应当合并处理。

### S8 [轻微] Corollary 11 的 monotone 方向没写，而方向本身是个不太好看的事实

- **位置**：`results.tex:183-187`；附录 `appendix_proofs.tex:946-950`。
- 附录证明 (1−x/K)^K 关于 K 递增，故 **L_K 关于 K 递减**，从上方收敛。正文只写
  "the convergence is monotone in K"，没写方向。方向意味着：**预算越大，保证越差**
  （L_2 > L_3 > ... > 1 − e^{−1/η}）。这对读者是有信息的，藏起来只会让 reviewer 觉得
  是在回避。建议直接写 "monotone from above"。

## A.3 Clarity（清晰度）

### C1 [严重] 状态标签全部不可见（与 T2/T3 同源，但作为 clarity 单列）

- **位置**：全仓库 `.tex` 的 `%` 注释；PDF 中零命中。
- **为什么伤**：`statements.tex:15-18`（AI use statement）向读者承诺 "statements whose
  proofs have not been so checked are explicitly marked in the source with their
  verification status"。"in the source"这个措辞在 PDF 里读起来像是"在本文里"，而实际上
  是"在我们不提交的 .tex 注释里"。reviewer 拿不到 .tex（除非 supplementary 打包了），
  于是这句承诺对他而言是空的。这同时是 soundness 与 ethics 的问题。
- **建议修法**：见 S2 的修法（附录加一张 verification-status 表），并把 statements.tex 那句
  改成 "... are marked in Table X of Appendix B"。

### C2 [中等] α 在同一节里承担两个互相矛盾的约定

- **位置**：`model.tex:30-31`（"Approximation ratios are stated as α ∈ (0,1] with
  F^ALG ≥ α F^OPT; larger is better"）与 `model.tex:50-51`（"an α-approximate incremental
  oracle with α = η^sel"，而 η^sel ≥ 1）；`related.tex:37-41` 同样两义并用；
  `notation_table.tex:23-24` **只登记了第一义**。
- **为什么伤**：两处相距 20 行，一处说 α ≤ 1 越大越好，一处说 α = η^sel ≥ 1 越小越好。
  RESEARCH_STATE 的"已知的论文错误"第一条正是原稿把近似比方向写反，GLOSSARY 第 7 行也把
  这一条列为必修项；现在方向修对了，却引入了同名不同义。而且 `GLOSSARY.md:20` 记录过
  F6 在这个方向上**已经栽过一次**（"此前误写 α = 1/η^sel，方向反了"），说明这个记号是
  高风险区。
- **建议修法**：把 GS 的参数改写成 `\alpha_{\mathrm{GS}}`（或直接沿用论文自己的 η^sel，
  只在首次出现时说"in their notation this parameter is called α"），notation table 里加一行
  写明"α_GS ≥ 1, the incremental-oracle parameter of Goundan and Schulz; equals η^sel"。

### C3 [中等] T 同时是算法输出与附录里的任意上集，且相隔三行

- **位置**：`appendix_proofs.tex:43-44`（"submodularity is used in its diminishing-returns
  form: d_e(T) ≤ d_e(S) for S ⊆ T and e ∉ T"）与 `appendix_proofs.tex:67-73`
  （Lemma B.1 里 "For S ⊆ T and e ∈ N_i∖T"），对照 `results.tex:24, 36, 171, 213` 与
  `appendix_proofs.tex:107-122, 903-915, 1054-1139` 里 T = 算法输出；
  再加 `appendix_proofs.tex:1022-1023` 的 "(F4) F_O(T)/F_O(O) = 1 − a_θ^K for every K-set
  T disjoint from O"（这里 T 又是任意 K-集）。
- **为什么伤**：附录开头三条"全局约定"的第一条就用 T 当哑变量，第三条又把 T 定成输出，
  同一段里自相冲突。在 B.8 的 hardness 证明里更乱：T 是输出、T_0 是 canonical 输出、
  (F4) 里的 T 是任意 K-集。
- **建议修法**：把 diminishing-returns 约定和 Lemma B.1 里的哑变量改成 A ⊆ B 或 S ⊆ S′，
  T 全篇只保留"算法输出"一义；(F4) 里的 T 改成 R。

### C4 [中等] "bounded-query" 这个提法把 size cap 吞掉了，而 size cap 才是构造的真正限制

- **位置**：小节标题 `results.tex:197`（"Hardness for bounded-query algorithms"）、
  `results.tex:230-237`（Remark 13 的 "the bounded-query optimum"、"within the stated
  query budget"）。定理本体 `results.tex:211-212` 确实写了 "each on a set of size at most K"。
- **为什么伤**：陈述里写了，标题和 remark 里没写，而摘要占位里写的是 "bounded-size
  queries"。三处口径不一。reviewer 会问：为什么要 cap size？（真正的答案在
  `results/F3_summary.md`：构造在大集合上会泄露 O，除非 x > T 之后 G 自动 O-无关，而那是
  F3 的另一族。）论文正文对此没有任何解释，size cap 看起来像是为了让证明能走通而加的，
  这正是 reviewer 会咬住不放的地方。
- **建议修法**：小节标题改 "Hardness for polynomially many bounded-size queries"，
  Remark 13 里补 "of size at most K"，并在 §4.8 开头加一句为什么需要 size cap
  （一句机制解释：balanced 集合的定义与 hypergeometric 集中带在大集合上会失效）。

### C5 [中等] "all-pairs error" 在附录里被使用，但全文从未定义

- **位置**：`appendix_proofs.tex:894-897`（"every all-pairs ratio is a weighted average of
  the two single-element values and the all-pairs error is exactly (η_u, η_o) as well"）。
  全文搜 "all-pairs" 只有这一处可见文本 + `conclusion.tex:8` 的注释。Definition 1
  （`model.tex:19-28`）只定义了 single-element 版本。
- **为什么伤**：读者读到"all-pairs error"会以为漏了定义。而这句话在 Theorem 10 的证明里
  其实是有用的（说明天花板对更强的误差模型也成立），删掉可惜。
- **建议修法**：在 Definition 1 后加一句括注定义 all-pairs 版本（"the same inequalities
  for marginal gains of arbitrary sets A ⊆ B"），或者把附录那句改写成不引用未定义术语的
  形式（"the same two constants bound the ratio for the gain of any set, since both
  functions are modular"）。

### C6 [中等] "the previously used explicit family" 是一次没有出处的自引

- **位置**：`results.tex:143-145`（Remark 9："the previously used explicit family attains
  only U_K(η)"）；`notation_table.tex:33-34` 同样写 "value of the per-K tightness family"。
- **为什么伤**：读者会问"previously used by whom"。文献里没有这一族（它来自本项目
  RESEARCH_STATE R7），所以这是对作者自己**未发表**前稿的隐式引用。在双盲稿里这既是清晰度
  问题，也有轻微的去匿名风险（暗示存在一份更早的投稿）。
- **建议修法**：改成中性表述 "the explicit family of Theorem 6 attains only U_K(η) when
  charged the global error η"，直接指向本文的 Theorem 6，删掉"previously"。

### C7 [轻微] δ 和 Φ 在 τ 被定义之前就用上了

- **位置**：`results.tex:202-204` 的显示式用了 τ，而 τ = c+1 在 `results.tex:208`
  （定理第一句）才定义。
- **建议修法**：把 "Fix c ≥ 0, put τ = c+1" 提到显示式之前的那句话里。

### C8 [轻微] related.tex 用小写 k 表示预算，与全文的 K 冲突

- **位置**：`related.tex:40`（"$1-(1-1/(\alpha k))^{k}\ge1-e^{-1/\alpha}$"）。PDF 第 1 页
  确实渲染成 "1 − (1 − 1/(αk))k"。
- 与 `k_1`（segment 参数，`results.tex:103`）在同一篇文章里，读者要分辨 k、K、k_1 三个符号。
  建议统一成 K。

### C9 [轻微] notation table 与 model.tex 都说 η^tr "只出现在一处 remark"，事实不是

- **位置**：`model.tex:59-61`（"it is used in a remark and in the appendix"）、
  `notation_table.tex:20-21`（"one remark only"）。实际可见出现：Proposition 4 本体
  （`results.tex:43,45`）、Theorem 6 本体（`results.tex:70`）、Experiments 正文两句
  （`experiments.tex:106-111`），另加附录多处。
- 这是 GLOSSARY 第 19 行"记号定稿"那条决定的自我描述失效，属于自查失守，建议直接把两处
  描述改成"used in Propositions 4 and Theorem 6, in Section 5, and in the appendix"。

### C10 [轻微] Table 1 的 L_K 列在最后一行放的是 ρ_K，与 caption 声明的列义不符

- **位置**：`EXP_table.tex:24, 30`（表头 `$L_K$`，worst-case 行填 `$\rho_K$`）与
  caption `EXP_table.tex:14-18`（"$L_K$ is the certified lower bound $L_K(\etasel)$ ...
  evaluated at the median measured $\etasel$"）。
- 建议把该列改名 "bound / value"，或给 worst-case 行同时给出 L_K 与 ρ_K。

### C11 [轻微] E4 的精度在两处写成不同的数

- **位置**：`experiments.tex:173-175` 写 "match the theoretical values to 1.1×10^{-16}"
  （宏 `\EFourMaxDeviation`），而 `EXP_table.tex:34-36` 的脚注与
  `appendix_experiments.tex:123` 写 "to $10^{-10}$"。
- 我核了 `results/E4_worst_case.csv` 的 `diff` 列，最大值确为 1.1102e-16，所以
  10^{-10} 只是更松的说法，不算错，但同一事实在同一篇论文里出现两个数会被 reviewer
  记一笔。建议全部走 `\EFourMaxDeviation` 宏。

### C12 [轻微] 残留 overfull hbox 93.26pt

- **位置**：`main.log:540`，来源 `sections/notation_table.tex` 第 8-43 行（表格过宽）。
  G6 checklist 已把它列为人类 TODO，此处只做确认。

## A.4 Reproducibility（可复现性）

### R1 [中等] 表里印的 η^sel 与表里印的 L_K / ρ_K 对不上，读者拿计算器一算就发现

- **位置**：`EXP_table.tex:26-28`；`experiments.tex:113-122, 137-143`；生成器
  `results/G3_gen_numbers.py`（`L_K`、`rho_K` 用**未舍入**的 η^sel 中位数计算，
  而 η^sel 本身按 `f1` 只印一位小数）。
- **证据（我实算的）**：
  - E2 行：CSV 里 K=30 的 η^sel 中位数是 **4.33937**，印成 4.3。
    `L_30(4.33937) = 0.206529 → 0.207`（论文印 0.207，与 CSV 一致），但读者按印出来的
    4.3 重算得到 `L_30(4.3) = 0.208214 → 0.208`。ρ 更明显：
    `ρ_30(4.33937) = 0.211009 → 0.211`（论文印 0.211），`ρ_30(4.3) = 0.212717 → 0.213`。
  - E3 行：CSV 里 K=5 的 η^sel 中位数是 **7.15034**，印成 7.2。
    `L_5(7.15034) = 0.132246 → 0.132`（论文印 0.132），读者按 7.2 重算得 `L_5(7.2) = 0.131`。
    `ρ_5(7.15034) = 0.139853 → 0.140`（论文印 0.140），按 7.2 重算得 0.139。
  - E1 行没问题，因为 η^sel 中位数恰为 2.00000（airline 那句用了两位小数 1.55，
    L_7(1.55) = 0.4918 → 0.492 与论文一致）。
- **为什么伤**：论文明确把 L_K 列定义成"evaluated at the median measured η^sel"，即邀请
  读者自己代入验证；四个可验数字里有四个（E2 的 L 与 ρ、E3 的 L 与 ρ）对不上末位。
  这不是数字错误（CSV 与宏完全一致，见下面 R2），但它是**审稿现场最容易被抓的一类**。
- **建议修法**：η^sel 一律印两位有效小数（4.34 / 7.15），或在 caption 加一句
  "bounds are computed at the unrounded median"。前者更好，成本为零。

### R2 [已核验，无问题] 29 个头条实验数字全部与 CSV 逐位吻合

我用独立脚本（不 import `G3_gen_numbers.py`，只重写 quantile / L_K / ρ_K）重算了
`paper/sections/numbers.tex` 里所有进入正文与 Table 1 的实验宏，**29/29 完全一致，
0 处不符**：`EOneKMainRatioMedian 0.971`、`LoQ 0.943`、`HiQ 0.998`、
`EtaSelMedian 2.0`、`Bound 0.405`、`ExactWorst 0.426`、`EtaTrMedian 19.4`、
`EtaTrBound 0.050`、`SignViolPct 22.7`、`NonposPct 21.4`、
`AirlineRatioMedian 0.999`、`AirlineEtaSelMedian 1.55`、`AirlineBound 0.492`、
`ETwo Ratio 0.963/0.936/0.989`、`EtaSel 4.3`、`Bound 0.207`、`ExactWorst 0.211`、
`NonposPct 0.0`、`EThree Ratio 0.670/0.576/0.757`、`EtaSel 7.2`、`Bound 0.132`、
`ExactWorst 0.140`、`NonposPct 20.0`、`SignViolPct 10.0`、`BestSurrogateRatio 0.712`。
另外单独核过：E2 的 p 扫描全部 9 个宏（`EtaRiseMin 3.2`←3.222、`EtaRiseMax 88`←87.509、
`RatioPHighMin 0.988`、`RatioPLowMin 0.882`、`RatioPLowMax 0.963`、
`BoundPHighMin 0.361`、`BoundPHighMax 0.573`、`BoundPLowMin 0.008`、
`BoundPLowMax 0.230`、`BoundDropFactorMax 64`←63.54）对 `results/E2_p_eta.csv` 全部正确；
E3 结构检查（`2.14`、`7.12`、`0.020`、`70,560`、`0`）对 `results/E3_summary.json` 正确；
E4 的 `0.278 / 3.5 / K=5 / j=2 / 1.1e-16 / 5.3e-15 / 1.8e-15` 对
`results/E4_rows.csv` 与 `E4_worst_case.csv` 正确；G4 新并入的
`EOneBreastOptK 5 / GreedyF 0.982 / GreedyFtilde 0.942 / InflationPct 1.8`
对 `results/G4_bc_opt_K5.csv` 正确（K=5 时 median f(greedy^f)/OPT = 0.982063，
1/0.982063 − 1 = 1.827% → 1.8）。**本报告不指控任何一个数字是错的。**

### R3 [中等] OPT 代理的 1.8% 修正只在 30 特征、K ≤ 5、单个数据集上量过，正文的摆放位置却邀请读者外推到 K=7 的合并行

- **位置**：`experiments.tex:66-73`（"on the one dataset small enough to enumerate the
  optimum, that proxy inflates a ratio by 1.8%"，紧跟在 E1 的 K=7 叙述之后）；
  `appendix_experiments.tex:47-58`。
- **为什么伤**：仓库自己的 `results/G4_bc_opt.md` 第 5 节写了明确禁令：
  "**不要写的话（会越界）**：不要把这个 2% 直接套到表里的 K=7 行"，理由是
  breast_cancer 的 K=7 OPT 没有测（C(30,7) 约 12 小时），"K=3..5 平坦所以 K=7 也差不多"
  是 `[CONJECTURE]`。而正文这句话恰好放在 Setup 段末尾、四个数据集与 K=7 一起讲的位置，
  读者的默认读法就是"表里的 ratio 高估约 1.8%"。E3 的情况更糟：那里 f 连 monotone
  submodular 都不是（违反率 2.14% / 7.12%），greedy-on-f 与 OPT 的距离**完全没有测过**，
  ratio 0.670 的分母可能离 OPT 很远。
- **补充核验**：我另外算了 K=4 时两种"inflation"统计的差别（逐 run 中位数 1.802% vs
  中位数之比 2.341%），在 K=5 上两者收敛（1.827% vs 1.810%），所以现在选用的统计量
  是稳的，这一点**不构成指控**；问题只在适用范围的措辞。
- **建议修法**：把那句改成"on breast\_cancer, the only dataset where the optimum was
  enumerated (K ≤ 5, 30 features), the proxy inflates a ratio by 1.8% in the median;
  no such measurement exists for the other datasets or for K = 7"，并在 E3 段加一句
  "for the third family no optimum was enumerated and the proxy gap is unknown"。

### R4 [中等] Figure 1 静默丢弃了 10 个点，而它们正是证书最空洞的那些 run

- **位置**：`experiments.tex:78-96`（图与 caption）；图内注记 "10 pts beyond"（我从
  `figures/money_plot.pdf` 导出文本确认）。
- **证据**：`results/E3_rows.csv` 里 K=5 共 879 行，其中 **10 行 η^sel > 500**
  （E1 K=5 与 E2 K=5/K=30 均为 0 行），与图内注记一致。E3 的 η^sel 最大值是 **8229.32**。
- **为什么伤**：截断本身可以接受，但 caption 只写 "Real tasks sit far above both curves"，
  正文完全不提有点被截。配合 T5（15 个 K=5 的点其实在曲线**下方**），这张主图给出的
  视觉结论与数据不符。
- **建议修法**：caption 加一句 "ten runs with η^sel > 500 fall outside the axis and are
  annotated in the panel; fifteen summarization runs at K = 5 fall below the L_K curve,
  which is possible because their true objective is not submodular (Section 5, out-of-model
  paragraph)"。把它写成一个发现，比让 reviewer 自己算出来强得多。

### R5 [中等] AI use statement 的两句承诺与附录的状态自陈冲突

- **位置**：`statements.tex:9-22`（"the authors re-ran the verification scripts and checked
  the proofs line by line before submission"、"No claim in this paper rests solely on an
  unverified AI-generated argument"）对照 `appendix_proofs.tex:1332`（"No script checks the
  derivations of this subsection"，指的正是 Theorem 8 赖以成立的 `app:validity`）、
  `appendix_proofs.tex:141`（necessity）、`:469`（coherence）、`:941`（ceiling）同样写着
  "No script checks the computations of this proof"。
- **为什么伤**：Theorem 8 的正面方向、Proposition 3、Lemma 7、Theorem 10 这四条都只有手证。
  "no claim rests solely on an unverified argument"在字面上就是假的，除非把"unverified"
  解释成"未经人类复核"（而人类复核这件事是否发生，`statements.tex:23-25` 的注释自己都
  留了"adjust the re-running claim to what the authors actually did"）。ICLR 2027 对
  AI use statement 是**required** 项，写得比事实更满是实打实的风险。
- **建议修法**：把第二句改成 "Claims whose proofs are not machine-checked are listed in
  Table X of Appendix B"，并把 `statements.tex:23-25` 的注释兑现成实际口径。

### R6 [轻微] 复现脚本路径进了 PDF 可见正文，但没有"哪一条覆盖哪一步"的索引

- **位置**：`appendix_proofs.tex:232-233, 413-414, 703-705, 871-872, 976-977, 1161-1162,
  1332-1334, 1349-1351`。
- 每小节末尾的一行 "machine-checked by results/X.py" 是好设计，但读者无法从中区分
  "这一小节全部被核过"与"这一小节的某几个恒等式被核过"。见 S2 的修法。

### R7 [轻微] 双盲与投稿模式的两个残留项

- `main.tex:29` 的 `\iclrfinalcopy` 仍在，PDF 每页页眉印着 "Published as a conference
  paper at ICLR 2027"；`\author{Anonymous}`。这两项 `results/G6_submission_checklist.md`
  已列为人类 TODO，此处仅确认存在，不重复计分。

---

# B. 空洞性检验（逐限定词的删除/取反替换）

方法：对 `sections/results.tex` 与 `sections/model.tex` 里每一条 Definition / Proposition /
Lemma / Theorem / Corollary / Remark 的陈述，逐个限定词做两步测试：
(1) **删除**该词，重读整句；(2) 换成**对立面**，重读整句。
判据（CLAUDE.md 第 39-44 行）：句子内容/真值不变 ⇒ 该词应删；变了但正文/脚注没有一句话
说清变在哪 ⇒ 必须补说明。

## B.1 通过的限定词（摘要式）

以下限定词全部**通过**（删除或取反后句子真值改变，且改变之处在正文或紧邻脚注/附录有
明确一句话交代）：

- `model.tex` Definition 1：`(single-element, multiplicative)`（取反成 all-pairs 会改变
  模型，正文与附录 B.6 都用到区别）、`η_u, η_o ≥ 1`（取反后 band 无意义）、
  `for every S ⊆ N and e ∉ S`（限制到轨迹即 η^tr，正文有对照）、
  `d_e(S) = 0 forces d̃_e(S) = 0`（这是 band 的推论，删掉读者要自己推）。
- `model.tex` 正文：`with ties broken adversarially in all worst-case statements`
  （取反 ⇒ Theorem 6/8 全部失效，改变巨大；但**说明只在附录**，见 V6/V9 的 FAIL）。
- `model.tex` Definition 2：`t < K`、`d_{e_t}(S^t) > 0`、`≥ 1`（三者删除后定义不良）。
- `results.tex` Prop 4：`monotone`、`submodular`、`f(∅)=0`（附录 Step 1 明确指出
  submodularity 与 monotonicity 各用在哪一步）、`whose selection error is η^sel`、
  `the three bounds are ordered`（附录 Step 4 给出单调性论证）。
- `results.tex` Thm 6：`for every K ≥ 2`、`â > 1`、`on 2K elements`、
  `η^sel = η^tr = â`（附录 Step 7 明确算出并与 η 比较）、
  `not only in the limit`（对照 Corollary 11 的渐近陈述，信息量真实）。
- `results.tex` Lemma 7：`monotone`（f 的 submodularity 在此不用，这一点附录点明了：
  "Only η ≥ 1 is used beyond the bands"）、`e, e' ∉ S`、
  `suppose d̃_e(S) ≥ d̃_{e'}(S)`（假设方向决定结论方向）。
- `results.tex` Thm 8：`for every K ≥ 2 and η ≥ 1`（η = 1 时退化成 Nemhauser 界，
  我数值验过 K=2 给 3/4）、`the minimum is attained by V_j on the segment`、
  `so the breakpoints are the integers 2,…,K`（我按闭式验过分段与断点）、
  `exactly when η ≥ K`（我在 K=3,5 的 η = K∓0.05 上验过：K=3 η=2.95 时
  ρ=0.338164 < 1/η=0.338983，η=3.05 时相等；K=5 同理）。
- `results.tex` Rem 9：`strictly above V_{K−1} for every η > 1`（我验了闭式
  U_K − V_{K−1} = q^{K−1}(η−1)/(Kη k_1)，K∈{3,7,15}×η∈{1.5,2,3.7} 共 9 点，
  与直接相减的差 ≤ 1e-16）、`monotone but not submodular`、`for η < K−1`、
  `left open`。
- `results.tex` Thm 10：`deterministic`（randomized 分支给出且常数不同）、
  `every n ≥ 2K`、`in expectation`。
- `results.tex` Cor 11：`for fixed η ≥ 1`、`as K → ∞`。
- `results.tex` Thm 12：`deterministic`（randomized 分支给出 ε_n）、
  `at most n^c queries`、`n ≥ 4K^{c+2}`（我验过这正是让坏事件 ≤ 9/32 的条件：
  n² ≥ 16K^{2c+4} ⇒ 首项 ≤ 1/(16·(c+2)!) ≤ 1/32，K²/n ≤ 1/(4K^c) ≤ 1/4）、
  `Φ(1) ≤ η`、`(sufficient: K ≥ τ(1+2/ln η))`（我验过该充分条件的推导链
  2τ/(K−τ) ≤ ln η 以及第二支所需的 K ≥ 2τ − τ²，成立）、
  `up to an additive ε_n`（我验过 ε_n 的两项分别来自 |T_0 ∩ O|/K 的平均 K/n
  与 Q = n^c 次查询的并集界 K^{2c+4}/((c+2)! n²)）。
- `results.tex` Rem 13：`asymptotically in K`、`at finite K a gap of order c/K ... remains
  open`（与 Kδ(η) → max{2τ(1−1/η), 2(τ−1)/η}、τ = c+1 一致）。

另外一条**数量级**核验：Remark 9 的 "L_K and ρ_K differ by O(1/K) for fixed η"，
我在 η=2、K ∈ {5,10,20,50,100,200,400} 上算得 K·(ρ_K − L_K) → 0.1515，确为 Θ(1/K)；
顺带 K²·(U_K − ρ_K) → 0.152，即 U_K − ρ_K = Θ(1/K²)，与 RESEARCH_STATE R7 一致。

## B.2 未通过的限定词（逐条）

### V1 [中等] Prop 3，`for every algorithm`：**缺算法类别，取反测试直接把命题打成假**

替换成 "every deterministic algorithm" ⇒ 句子为真且附录支持；替换成 "every randomized
algorithm" ⇒ 句子（字面上断言"输出 T 满足…"）为假，附录只证到期望。所以这个限定词的
外延超出了证明，且正文没有一句话说明 randomized 情形要改成期望。
**判定：必须补说明或收窄。** 修法见 S4。

### V2 [中等] Prop 3，`every n ≥ 2K`：**在其允许的边界上句子退化为恒真**

代入 n = 2K，结论 f(T) ≤ K/(n−K) f(O*) = f(O*)，恒真。也就是说这个限定词允许一整类
参数取值让整条命题空洞。真正的内容（n → ∞）只出现在附录最后一行。
**判定：必须在正文补一句 n → ∞，或把常数换成确定性情形的 K²/(n(n−K))。**

### V3 [严重] Thm 6，`on the adversarial-tie run`：**改变了但正文一字未解释**

删除 ⇒ 命题为假（该族每一步全并列，换 tie 规则 greedy 返回 O，ratio = 1）。
取反（"under any tie-breaking rule"）⇒ 明确为假。所以它是本条定理里最 load bearing 的词，
而"每一步是全并列"这个关键事实只写在 `appendix_proofs.tex:353-371`，正文零提示。
**判定：必须把说明写进正文或脚注。** 修法见 N2。

### V4 [中等] Thm 8，`under adversarial tie breaking`：**改变了，说明只在附录**

删除 ⇒ 等式变成 infimum 而非 max（附录 `:858-867` 自己写了这一点，并给了 ε 扰动构造）。
CLAUDE.md 要求"把这句话写进正文或脚注"，附录不算。
**判定：补一句脚注即可，成本一行。**

### V5 [中等] Thm 12，`each on a set of size at most K`：**改变了但未解释为什么需要**

删除 ⇒ 命题的真值状态未知（仓库里 F3 有一个不同族的任意大小版本草稿，见 N4），
所以这个词是硬性 load bearing。但正文没有任何一句说明它为什么在那里。
**判定：必须补一句机制解释。** 修法见 C4。

### V6 [中等] Thm 12，`single-element error exactly η`：**"exactly" 改变真值且依赖 [CONJECTURE]**

把 `exactly` 换成 `at most` ⇒ 命题变弱但仍有内容（下界仍成立，因为 L_K 关于 η 递减、
误差更小时界更强，方向反而不利），换成 `at least` ⇒ 无意义。所以 `exactly` 是必要的，
但它的成立依赖 (F2)，而 (F2) 在一般 (K,τ,η) 下是 `[CONJECTURE]`（S3/T3）。
**判定：这是"改变了、但支撑不足"的类型，必须把条件写进定理陈述。**

### V7 [严重] Prop 4 / Def 2，`over the steps with positive chosen gain`：**改变了，且改变的方向使命题为假**

删除该限制 ⇒ η^sel 在有零增益步时无定义或为 ∞，命题的常数变差；保留该限制 ⇒ 命题在
无全局 band 时为假（S1 的两元素反例）。两边都出问题，说明这个限定词现在的写法既没有
让命题为真、也没有被解释清楚。附录 Step 2 试图解释，但它偷偷用了 Definition 1。
**判定：FAIL，且是全文最严重的一条。** 修法见 S1。

### V8 [轻微] Cor 11，`for L_K the convergence is monotone in K`：**方向缺失**

删除 ⇒ 句子仍为真（只是少了信息）；保留但不写方向 ⇒ 读者不知道 L_K 是递增还是递减。
按 CLAUDE.md，"变了但说不清变在哪"就不准用。这里能说清（递减，从上方收敛），
只是没说。
**判定：补两个词 "from above" 即可。**

### V9 [轻微] Thm 10，`with error exactly (η_u, η_o)`：**改变了，说明只在附录**

`exactly` 保证 adversary 不能靠更小的误差取巧；附录 `:890-893` 写了"both factors
attained"，正文没有。一行脚注即可。

### V10 [轻微] Rem 13，`with K evaluations of f̃ per step`：**这不是限定词问题而是事实错误**

见 S5：正确的是每步 n − t 次、全程 Θ(nK) 次。取反测试在这里直接暴露了一个错数。

### V11 [轻微] `model.tex` "it is used in a remark and in the appendix"（关于 η^tr）

删除/取反测试：该句作为对全文用法的描述，与实际用法矛盾（见 C9）。属于自描述失效。

---

# C. 术语撞名与记号冲突检查

扫描方法：对 11 个 `.tex` 文件先用正则剥掉 `%` 注释（保留 `\%`），再逐行匹配
GLOSSARY 的禁用/歧义词表；`T`、`q`、`k` 等单字母用词边界正则单独扫。

## C.1 GLOSSARY 禁用/歧义词逐条

| 词 | 结论 | 证据 |
|---|---|---|
| **robust / robustness** | ✅ **零命中**（可见正文与注释均无） | 全文正则扫描 0 命中。D1 决定里"more robust 措辞禁用"被严格执行 |
| **bare "tight"** | ⚠️ **4 处可见命中，全部是 "tightness"** | `results.tex:66`（小节标题 "Per-$K$ tightness"）、`results.tex:68`（定理名 **"Tightness for every $K$"**）、`notation_table.tex:33`（"the per-$K$ tightness family"）、`appendix_proofs.tex:236`（附录小节标题）。GLOSSARY 第 10 行："论文中裸写 tight 一律视为未完成句"。"Per-K tightness" 勉强算被 "per-K" 限定成含义 (a)，但**定理名 "Tightness for every K" 完全没有说 tight for what**，读者极易读成含义 (c)（无任何算法能更好），而本定理只讲 predictive greedy 在一族实例上取等。**更严重的是自我认证失败**：`results.tex:6-7` 的文件头注释白纸黑字写着 "the words \"robust\" and bare \"tight\" do not appear"，而同一文件第 66、68 行就有。`experiments.tex:24-25` 有同样的自我认证句（该文件里 tight 只出现在 `\ref{thm:tightness}` 中，渲染后不可见，故该文件通过） |
| **any algorithm** | ✅ 未出现该裸短语；实际用词是 `every algorithm`（`results.tex:22`，**缺类别，见 V1**）、`every deterministic algorithm`（`results.tex:168`，✅）、`no algorithm`（`results.tex:200` 与 `:234`，前者紧接 "with polynomially many small queries"、后者紧接 "within the stated query budget"，✅ 有范围） | GLOSSARY 第 11 行要求指明 (i)/(ii)/(iii) 三个范围之一；除 `results.tex:22` 外均满足 |
| **consistency（LAA 含义之外）** | ✅ 技术含义只出现一次且被显式限定：`related.tex:86-87`（"the first property being consistency in its learning-augmented sense"）。另有三处英语常用义的 "consistent"：`appendix_proofs.tex:1154`（"the theorem and Proposition 4 are consistent"）、`:1193`（"It is consistent with reading g_{t,i} as a marginal gain"）、`:1328`（"which is consistent with the predictor being an arbitrary set function"） | 三处 "consistent" 都是普通形容词，不构成 LAA 撞名；但 `:1154` 出现在讨论两条界的关系时，建议改成 "compatible"，成本为零 |
| **coherence lemma** | ✅ 改名执行到位：`results.tex:83-98` 用 Coherence，并在注释里写明改名理由；LP 约束标识仍叫 `cons(t,i)`（`appendix_proofs.tex:499`），这属于 GLOSSARY 第 8 行允许的"脚本内部命名"，但它进了**可见正文**（`\eqref{eq:redlp}` 的约束名）。轻微：读者会把 `cons` 读成 consistency。建议改成 `coh(t,i)` | `appendix_proofs.tex:493-501, 1265-1281, 1312` |
| **information-theoretic** | ✅ 只在附录出现一次且首次使用即给定义：`appendix_proofs.tex:998-1001`（"the bound depends only on the number and the size of the queries ... and uses no computational assumption"）。正文零命中 | 符合 GLOSSARY 第 15 行 |
| **η 与 Agarwal-Balkanski 撞名** | ✅ 处理正确：`related.tex:96-102` 把对方的参数改写成 `\eta_{\mathrm{AB}}` 并加脚注说明"counts elements whose actual insertion or deletion time is far from the predicted one; it is unrelated to the multiplicative marginal-gain error η of Definition 1" | 符合 GLOSSARY 第 13 行 |
| **η^path / η^tr 首次出现需定义** | ✅ `model.tex:59-61` 定义了 trajectory error 并给出链 η^sel ≤ η^tr ≤ η；⚠️ 但对"只出现在一处 remark"的自我描述不实（C9） | |
| **ρ_K 与 ρ_K^LP 的区分** | ⚠️ 论文只用 ρ_K，从不提 reduced LP 值 ρ_K^LP 是一个**不同的量**；Theorem 8 直接写 ρ_K = min_j V_j，把 GLOSSARY 第 17 行要求区分的两者合并了。合并的合法性正是 S2 里那条无 oracle 的手证。轻微记号问题，实质是 S2 | `results.tex:109-125` |
| **balanced（查询/集合）** | ⚠️ `appendix_proofs.tex:1052`（"Step 2: valuation on the balanced event"）与 `:1074-1075`（"the balanced strip"）使用了 balanced，但**从未写明取 GLOSSARY 第 18 行的哪一种形式化**（y ≤ τ 还是 \|y − K\|S\|/n\| ≤ τ）。从 (F1) 与 Step 1 的 `{\|S ∩ O\| > τ}` 可以反推是前者，但 GLOSSARY 明确要求"使用时必须写明取哪种定义"，而 R11(b) 记录了两种定义结论**截然不同**（后者下该构造对任意 δ 不可行）。**判定：中等，必须补一句"balanced means \|S ∩ O\| ≤ τ throughout"，并在 open problems 里点出另一种形式化下构造失效** | |

## C.2 今晚新引入的记号冲突

| 冲突 | 位置 | 判定 |
|---|---|---|
| **α：ratio 约定 (0,1] vs Goundan-Schulz 的 α ≥ 1** | `model.tex:30-31` vs `model.tex:50-51`（相隔 20 行）；`related.tex:37-41`；`notation_table.tex:23-24` 只登记第一义 | **中等**，见 C2。这是本次扫描里最实质的记号冲突 |
| **T：算法输出 vs 附录里的任意上集/任意 K-集** | `results.tex:24,36,171,213` vs `appendix_proofs.tex:43-44, 67-73, 1022-1023` | **中等**，见 C3 |
| **q（segment 参数）vs Q（查询预算 n^c）** | `notation_table.tex:29`（q）与 `:37`（Q），同一张表相隔 8 行；正文 `results.tex:103` 与 `:212` | **轻微**：大小写相差一个字母而语义毫不相干。建议把查询预算改成 `\mathcal Q` 或直接写 n^c |
| **k_1（segment 参数）vs k（related.tex 里的预算）vs K（预算）** | `results.tex:103`（k_1）、`related.tex:40`（小写 k）、全文 K | **轻微**，见 C8。把 related.tex 的 k 统一成 K 即可消解三分之二 |
| **τ 在被定义之前使用** | `results.tex:202-204` 用 τ，`results.tex:208` 才定义 | **轻微**，见 C7 |
| **cons(t,i) 约束名 vs 已改名的 coherence lemma** | `appendix_proofs.tex:499, 1265` | **轻微**，见 C.1 表 |
| **"all-pairs error" 未定义即使用** | `appendix_proofs.tex:894-897` | **中等**，见 C5 |

---

# D. 全部发现的分级汇总

## 严重（6 条）

| ID | 标题 | 位置 |
|---|---|---|
| T1 / S1 / V7 | Proposition 4 按其陈述假设为假；63 行实测 run 违反 L_K(η^sel)，38 行在 η^sel = 1.0 | `results.tex:35-46`, `model.tex:40-58`, `appendix_proofs.tex:178-196` |
| T2 / S2 | Theorem 8 的 ≥ 方向唯一支撑 `app:validity` 无 oracle，且状态标签对读者不可见 | `results.tex:126-139`, `appendix_proofs.tex:1165-1172, 1332-1334` |
| T3 / S3 / V6 | Theorem 12 的陈述本体内嵌 `[CONJECTURE]`（δ 闭式与 (F2)-(F4)） | `results.tex:202-228`, `appendix_proofs.tex:1018-1024, 1103-1104` |
| T4 / N1 | D2 之后 novelty 承重不足；核心接口 η^sel 自认等同 GS 的 α，来源是未评议预印本 | `results.tex:35-50`, `related.tex:34-51`, `references.bib:53-59` |
| T4b / N2 / V3 | Theorem 6 的 per-K tightness 完全由 adversarial tie 支撑（每步 2K−t 个候选全并列），正文零提示，且无严格偏好版本 | `results.tex:68-74`, `appendix_proofs.tex:353-371` |
| T5 / C1 | 状态标签全部只在 LaTeX 注释里，PDF 零命中，而 statements.tex 向读者承诺"marked in the source" | 全仓库 `.tex` 注释；`statements.tex:9-22` |

## 中等（16 条）

N3（LAA consistency 空栏，`related.tex:83-107`）、N4（更强的任意大小 hardness 版本未采用，
`results.tex:206-221` vs `results/F3_summary.md`）、S4/V1/V2（Prop 3 缺算法类别 +
n=2K 边界恒真，`results.tex:21-27`）、S5/V10（Remark 13 的 "K evaluations per step" 错误
且 c=1 时 greedy 未必在预算内，`results.tex:230-237`）、S6（1/η 天花板与 hardness 的表观
冲突未在正文调和，`results.tex:167-178` vs `:199-237`）、S7（η^tr trimming 单边且事后，
`appendix_experiments.tex:27-37`）、C2（α 双义，`model.tex:30-31` vs `:50-51`）、
C3（T 双义，`appendix_proofs.tex:43-44` vs 输出 T）、C4（bounded-query 吞掉 size cap，
`results.tex:197,230-237`）、C5（all-pairs error 未定义，`appendix_proofs.tex:894-897`）、
C6（"previously used explicit family" 无出处自引，`results.tex:143-145`）、
R1（印出的 η^sel 与印出的 L_K/ρ_K 对不上：L_30(4.3)=0.208 vs 印 0.207；ρ_30(4.3)=0.213
vs 印 0.211；L_5(7.2)=0.131 vs 印 0.132；ρ_5(7.2)=0.139 vs 印 0.140）、
R3（1.8% 的 OPT 代理修正被摆在邀请外推的位置，`experiments.tex:66-73`，仓库自己有禁令）、
R4（Figure 1 静默丢 10 个点且 caption 与数据矛盾，`experiments.tex:78-96`）、
R5（AI use statement 与附录状态自陈冲突，`statements.tex:9-22`）、
C.1 表里的 **bare "tight"**（`results.tex:66,68` 等 4 处，含 `results.tex:6-7` 的自我认证
失败）与 **balanced 未写明取哪种形式化**（`appendix_proofs.tex:1052,1074`）。

## 轻微（10 条）

S8/V8（Cor 11 缺 "from above"）、V9（Thm 10 的 "exactly" 说明只在附录）、
C7（τ 的前向引用）、C8（related.tex 用小写 k）、C9（η^tr "one remark only" 不实）、
C10（Table 1 的 L_K 列在最后一行放 ρ_K）、C11（E4 精度 1.1e-16 vs 1e-10 两个口径）、
C12（notation_table 的 93.26pt overfull hbox）、R6（脚本索引粒度不足）、
R7（`\iclrfinalcopy` 与页眉，G6 已列 TODO）；另加记号类轻微项：q/Q、k/k_1/K、
`cons(t,i)` 约束名。

## 已核验、不构成指控的项（供明早放心）

- `paper/sections/numbers.tex` 里进入正文与 Table 1 的 **29 个头条实验数字全部与
  E1/E2/E3/E4 的 CSV 逐位吻合，0 处不符**；E2 p 扫描 9 个宏、E3 结构检查 5 个数、
  E4 的 7 个数、G4 新并入的 4 个数亦全部吻合（详见 R2）。
- 理论侧我独立复算并确认：U_K − V_{K−1} = q^{K−1}(η−1)/(Kη k_1) 在 9 个 (K,η) 点上
  与直接相减差 ≤ 1e-16；ρ_K = 1/η 当且仅当 η ≥ K（在 K=3,5 的 η = K∓0.05 上验证）；
  Remark 9 的 O(1/K) 与 RESEARCH_STATE 的 U_K − ρ_K = O(1/K²) 数值成立；
  Theorem 12 的 ε_n 两项与附录 Step 1/Step 5 的推导一致；充分条件
  K ≥ τ(1+2/ln η) ⇒ Φ(1) ≤ η 的两支推导都成立（第二支需要 K ≥ 2τ − τ²，由 K ≥ 2τ 保证）。
- RESEARCH_STATE"已知的论文错误"四条的修复状态：近似比方向 ✅ 已修
  （`model.tex:30-31` 并留了 erratum 注释）；负面结果引用 ✅ 已改为
  `horel2016maximization`（`related.tex:71-74`），`hassidim2017submodular` 被正确地放在
  正面结果的位置；R-step 整体删除 ✅，只剩 Theorem 10 的 exhaustive-search 一句；
  Section 3.3 的 λ 方向与 Theorem 10 的 1/λ 已随 R-step 一并消失，无残留。

---

# 明早我自己会先修的三条

如果只有一个上午，我会按这个顺序动手。**第一条是 Proposition 4 的假设漏洞（T1/S1/V7）**：
它不是措辞问题，是命题在字面上为假，而且论文自己的 `results/E3_rows.csv` 里有 63 行
实测反例、38 行的 η^sel 恰为 1.0、最坏一例（`sport_coverage`, K=4, η^sel=1.0）实测 ratio
0.4153 而 L_4(1) = 0.6836；只要有一位 reviewer 下载 supplementary 跑一遍这三行 pandas，
论文的标题里那个 "Per-Run Certificates" 就没了。最省事的修法是在 Proposition 4 里补上
"(f, f̃) satisfies Definition 1 for some finite (η_u, η_o)"，同时把 Table 1 的 note (ii)
重写成"L_K 列在 f 不满足 Definition 1 的族（E1 的 21.4%、E3 的 20.0% 非正步）上不是
certificate"，并在 out-of-model 段主动报出这 63 行违反，把被抓变成主动披露。
**第二条是把状态标签变成可见文本（T2/T5/C1/R5）**：在附录加一张 verification-status 表
（定理号 / 哪一步 / 哪个脚本 / 哪一步只有手证），把 `rem:app-status` 提到 Theorem 8 底下，
并把 AI use statement 里 "no claim rests solely on an unverified argument" 改成指向那张表。
成本半页，收益是把"作者在藏"变成"作者在标"，这对一份把 Theorem 8 的下界压在无 oracle
手证上的稿子是唯一站得住的姿态。**第三条是给 Theorem 12 加条件、给 Theorem 6 加 tie 说明
（T3/T4b/V3/V6）**：Theorem 12 改成"Assume the family has single-element error exactly
Φ(θ)（τ = 1 时可证，一般情形在 40 个点上 LP 验证）"，并把 τ = 1 单独提成一条无条件
Corollary；Theorem 6 的陈述里加"the ties are total at every step, and adversarial tie
breaking is load bearing"一句。这两处都是一句话的成本，但它们决定了 reviewer 读到
"Theorem" 三个字时是信任还是警觉。
