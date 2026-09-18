# V11 Q5a oracle 报告：prop:guarantee（台账 T3，归属 Goundan-Schulz 2007）

脚本：`results/V11/oracle/guarantee.py`（一键运行 `python3 results/V11/oracle/guarantee.py`，全部通过时 exit 0）
日志：`results/V11/oracle/guarantee.log`
机器可读：`results/V11/oracle/guarantee.json`
复跑产物副本：`results/V11/oracle/reruns/`
本次运行：13 个 check 全 PASS，0 个 violation，exit code 0，用时 22.9 秒。

陈述来源 `results/V11/inputs/statement_guarantee.md`；def:etasel 来自 `paper/sections/model.tex`（第 84 行起）；
路线甲证明材料来自 `paper/sections/appendix_proofs.tex` 的 `app:guarantee`（Step 1 覆盖不等式 r_t ≤ K M_t、
Step 2 零增益步、Step 3 展开、Step 4 三把尺子链）与 `rem:app-product`（逐步乘积界）；台账卡 `THEOREM_LEDGER.md` 的 T3。
所有判定用 `fractions.Fraction` 或 sympy，浮点只出现在打印文本与被复跑的两个既有脚本内部。种子固定。

---

## 1. 查了什么，结果如何

| 编号 | 内容 | 状态标签 | 精确计数 |
|---|---|---|---|
| C0 | sympy 恒等式：L_K 闭式、L_K(1)=1−(1−1/K)^K、L_1(x)=1/x、对 x 的导数为 −(1−1/(Kx))^{K−1}/x²（故 L_K 关于 x 严格递减）、x→∞ 时 L_K→0（即 L_K(∞)=0 约定）、K→∞ 时 L_K(x)→1−e^{−1/x}、h(u)=K log(1−u)+Ku 满足 h(0)=0 且 h′(u)=−Ku/(1−u)（这是 L_K(x) ≥ 1−e^{−1/x} 的那一步）、Step 3 展开恒等式 | [VERIFIED-SYMBOLIC] PASS | 30 条恒等式，residual 全为 0 |
| C1 | 2,400 个随机精确实例（n ≤ 7，K ≤ 4，f 单调 submodular 全格点验过，f̃ 按 Definition 1 抽样后重算实际因子 (η_u, η_o)）：predictive greedy 跑满 K 步，tie 对抗处理（tie 路径数 ≤ 400 时全枚举，否则取 40 条抽样路径里最差的）；每条 run 检 f(T) ≥ L_K(η^sel)·OPT，以及 η^sel ≤ η^tr ≤ η 与 L_K(η^sel) ≥ L_K(η^tr) ≥ L_K(η)，并对 η^tr、η 两把尺子各再检一次主不等式 | [VERIFIED-EXHAUSTIVE] PASS | 2,400 实例 / 9,076 条 run / 9,064 次主不等式检查 / 9,076 次排序检查；tie 树全枚举 2,395 个，抽样 5 个；262,260 次单调、338,802 次 submodular、262,260 个 band pair；2,937 次抽样被拒；12 条 run 的 OPT = 0（平凡） |
| C2 | app:guarantee 的 Step 1：每个 run state 上 r_t ≤ K·M_t，以及 g_t > 0 时的收缩 r_{t+1} ≤ (1−1/(a_t K))·r_t | [VERIFIED-EXHAUSTIVE] PASS | 27,985 次覆盖检查，19,580 次收缩检查 |
| C3 | 附属项（rem:app-product，不是本命题）：逐步乘积界 f(T) ≥ (1−∏_t(1−1/(K a_t)))·OPT | [VERIFIED-EXHAUSTIVE] PASS | 9,064 次检查，最差 slack 0（即有实例取等） |
| C4 | model.tex 的配套断言：band 有限（合法 f̃）时不会出现 harmful zero step，故 η^sel 有限 | [VERIFIED-EXHAUSTIVE] PASS | 9,076 条合法预测器上的 run，零次 a_t = ∞ |
| C5 | Thm D 紧实例：把 `app:tightness` 的 U_K 族用有理数重建（K = 2..5，â ∈ {3/2, 2, 3}，n = 2K），对抗 tie（全取 B）那条 run 精确满足 η^sel = â 且 f(T)/OPT = L_K(â)，同时全局 η = (âK−1)/(K−1)，L_K(η) 严格更小 | [VERIFIED-EXHAUSTIVE] PASS | 12 个实例，12/12 取等 |
| C6 | 复跑 `results/F2_etasel_tight.py` | [VERIFIED-LP 浮点] PASS | exit code 0，0.3 秒，14 行表全 PASS，`STATUS: ALL PASS (14 instances: K = 2..8 x ahat in {1.5, 2})` |
| C7 | 复跑 `results/T5_symbolic.py` | [VERIFIED-SYMBOLIC] PASS | exit code 0，3.4 秒，`TOTAL: 105/105 checks passed (35 general-K, 70 concrete-K)`，json 里 n_pass=105、n_fail=0，all-pairs 穷举 K = 2..8 |
| D | 结构化情形：harmful zero step、benign zero step、η = 1、K = 1、K = n | PASS | 5 个情形全 PASS，共 600 个额外随机实例 |

精确性说明：C6 复跑的 F2 脚本走的是 E4 的 CELF 浮点管线（`quantize=10`，判定带 1e-12/1e-8 容差），所以该项标
[VERIFIED-LP 浮点]，不标 exact；同一紧性事实在本脚本的 C5 里用 `Fraction` 重算到精确取等，两者互为对照。
C7 复跑的 T5 是 sympy 符号验证，标 [VERIFIED-SYMBOLIC]。本脚本自身的每个判定都是精确的。

未修改任何既有仓库文件。F2 与 T5 会在 `results/` 下原地覆写自己的输出文件（`F2_etasel_tight.txt`、
`T5_symbolic.json`），所以复跑前先存字节、复跑后把新产物拷进 `results/V11/oracle/reruns/`、再把原文件写回并核对 sha256；
json 的 `reruns` 段记录了三个 sha256（before / after / restored），两个文件的复跑输出与原文件逐字节相同。

---

## 2. Criterion D：对陈述本身的反例搜索

随机实例总数 **3,000**（C1 的 2,400 ＋ η=1 的 160 ＋ K=1 的 240 ＋ K=n 的 200），覆盖 modular 1,039、
concave-of-cardinality 318、budget-additive 320、coverage 280 与它们的两两有理混合 443（C1 部分的族分布）。
**violations = 0**，没有 witness。

主不等式 f(T) ≥ L_K(η^sel)·OPT 的最差 slack：

- 全体最小值 0，在 K = 1、η^sel = 1（ratio = bound = 1）这类取等情形达到；C1 的 9,064 次检查中有 **790 条 run 取等**。
- 限制到 K ≥ 2 且 η^sel > 1 的信息量更大的一格：最小 slack = **128/539 ≈ 0.2375**，在 n = 6、K = 2、η^sel = 7/4、
  ratio = 8/11、bound = L_2(7/4) = 24/49 的 modular 实例上。也就是说随机实例离界还远，取等要靠 C5 的 U_K 构造。

结构化情形：

| 情形 | 构造 | 结果 |
|---|---|---|
| harmful zero step | n=3, K=2，f modular 权重 (0,1,1)，f̃(S) = card(S)，tie 对抗指向 a | a_0 = ∞，η^sel = ∞，L_2(∞) = 0，f(T) = 1，OPT = 2，ratio = 1/2 ≥ 0，界成立且平凡。该预测器在 Definition 1 下非法（d_a = 0 < d̃_a = 1），这正是 C4 的另一面：合法 f̃ 出不了这种步 |
| benign zero step | n = K = 3，f(S) = 1（S 非空），f̃ = f | 6 条 run，12 个 M_t = g_t = 0 的步，每个 a_t = 1，η^sel = 1，ratio = 1 ≥ L_3(1) = 19/27 |
| η = 1 | 160 个随机实例，f̃ = c·f | 2,361 条 run，η^sel = 1，最差 slack 0（取等） |
| K = 1 | 240 个随机实例，L_1(x) = 1/x | 308 条 run，最差 slack 0（取等） |
| K = n | 200 个随机实例 | 315 条 run，输出恒为整个 ground set，f(T) = OPT，最差 slack 1/4 |

---

## 3. Running example（K = 3，η = 3/2）

U_3 族（â = 3/2，n = 6，OPT = 1）：三步 a_t 全为 3/2，η^sel = η^tr = 3/2，f(T) = 386/729 = L_3(3/2) ≈ 0.5295，精确取等。
同一实例的全局 η = (3·3/2−1)/2 = 7/4，L_3(7/4) = 4348/9261 ≈ 0.4695，故三把尺子读数为 386/729 = 386/729 > 4348/9261。
对照 â = 2：ratio = L_3(2) = 91/216，全局 η = 5/2，L_3(5/2) = 1178/3375。

---

## 4. FAILED 项

无。13 个 check 全部 PASS，0 个 violation，0 个 witness。

---

## 5. 覆盖不到的地方（记录，不夸大）

- 本次是有限枚举与随机搜索，不是对一般 K、一般 n 的证明。附录 `app:guarantee` 的手写论证本身仍是
  [HAND-PROOF-UNREVIEWED]；C0 与 C2 只把它的每一步在这些实例上逐条核到，没有替代人的复核。
- 归属句（Goundan-Schulz 2007 Theorem 1，α = η^sel 同向）是文献事实，不在本 oracle 的射程内，仍按 F6 审计与 J2 复核的结论走。
- tie 路径数超过 400 的实例（C1 里 5 个）用的是 40 条抽样路径的最差值，不是全枚举；这 5 个实例的结论标注为抽样而非穷举。
- 第二个不等式 L_K(η^sel) ≥ 1−e^{−1/η^sel} 只在 C0 里符号验证（1−u ≤ e^{−u} 那一步），没有在每条 run 上逐个用有理数复核，
  因为 e 不是有理数。
