# V11 Q5b oracle 报告：lem:coherence（台账 T5）与其 sharp form

脚本：`results/V11/oracle/coherence.py`（一键运行 `python3 results/V11/oracle/coherence.py`，全部通过时 exit 0）
日志：`results/V11/oracle/coherence.log`
机器可读：`results/V11/oracle/coherence.json`
复跑产物副本：`results/V11/oracle/reruns/`
本次运行：12 个 check 全 PASS，0 个 violation，exit code 0，用时 27.3 秒。

陈述来源 `results/V11/inputs/statement_coherence.md`；Definition 1 用 `results/V11/inputs/definition1.md` 的 convention B；
路线甲证明材料来自 `paper/sections/appendix_proofs.tex` 的 `app:coherence`（约第 524 行：f̃ 的两序展开给 eq:coh-pred，
再套两侧 band 得 (i)，同一展开对 f 得 (ii)）；sharp form 的 slack certificate 来自 `results/H_J3_gate_check.py`；
三项非负 slack 分解来自 `results/J2_core_oracles.py`（`symbolic_core` 的 R6 恒等式与 `R6_full_lattice_lp`）；
台账卡 `THEOREM_LEDGER.md` 的 "## T5"。

记号：d = d_e(S)，g = d_{e'}(S)，h = d_{e'}(S∪{e})，D = d_e(S∪{e'})；预测侧 P = d̃_e(S)，Q = d̃_{e'}(S)，
R = d̃_{e'}(S∪{e})，P' = d̃_e(S∪{e'})。所有判定用 `fractions.Fraction` 或 sympy，浮点只出现在打印文本与被复跑的两个既有脚本内部。
种子固定（20260918 / 20260919 / 20260920 / 20260921 / 20260922 / 20260923）。未修改任何既有仓库文件。

**"actual eta" 的口径**：每个随机实例抽完 f̃ 后，在**整个 lattice** 上重算实现的 (η_u, η_o) = (max d/d̃, max d̃/d)，
按 convention B **不把两个因子各自向上截断到 1**（只有乘积 η = η_u η_o ≥ 1 是自动的）。这样得到的是最小可行 scalar error，
因此 (i) 的 1/η 最大、(ii) 的 (1−1/η) 最小，是两个不等式的最尖锐读法。

---

## 1. Criterion C：查了什么，结果如何

| 编号 | 内容 | 状态标签 | 精确计数 |
|---|---|---|---|
| C0 | 自己用 sympy 重推（不是复用 J2）：f 与 f̃ 的两序交换恒等式；(i) 的三项非负 slack 分解 D − h/η = (η_o D − P')/η_o + (P − Q)/η_o + (η_u R − h)/(η_u η_o)；(ii) 的同一三项分解；(i) 的 slack、(ii) 的 slack 与 sharp form 第一个不等号的 slack 是**同一个有理函数**；prediction slack d − g/η 自己的三项分解 (η_o d − P)/η_o + (P − Q)/η_o + (η_u Q − g)/(η_u η_o)，且 d − g/η = slack_(ii) + (1−1/η)(g−h)；第二个不等号写成两个非负因子之积；corollary（η > 1 且 d = g/η 推出 h = g）；η = 1 时 (i)(ii) 都塌成 d ≥ g | [VERIFIED-SYMBOLIC] PASS | 12 条恒等式，residual 全为 0 |
| C1 | 2,400 个随机精确实例（1,200 个 f 只单调不 submodular，1,200 个 f 单调 submodular；n ∈ {3,4,5,6}，f̃ 按 Definition 1 抽样后重算实际 (η_u, η_o)）。对每个实例**穷举** lattice 上全部满足 d̃_e(S) ≥ d̃_{e'}(S) 的三元组 (S, e, e')（预测增益打平时两个朝向都测），检 (i) 与 (ii)；submodular 那一半另检 sharp form 的两个不等号 | [VERIFIED-EXHAUSTIVE] PASS | 185,272 个三元组；(i) 185,272 次、(ii) 185,272 次、sharp 第一式 92,788 次、sharp 第二式 92,788 次、d ≥ g/η 185,272 次；462,732 次单调检查、377,764 次 submodular 检查、169,816 个 band pair；3,367 次抽样被拒 |
| C2 | 在 C1 的每个三元组上把 C0 的三项分解用 Fraction 逐项算出：每项 ≥ 0，且三项之和精确等于 slack | [VERIFIED-EXHAUSTIVE] PASS | 555,816 个非负项（每三元组 3 项），0 次违反 |
| C3 | 复跑 `results/H_J3_gate_check.py`（sharp form 的 slack certificate） | [VERIFIED-SYMBOLIC] + [VERIFIED-LP 浮点] PASS | exit code 0，6.9 秒，9 PASS / 0 FAIL，`ALL PASS`；本项相关行 `PASS sharp form == coherence (ii) rearranged`；同脚本的 facet 项 `PASS facet uniqueness on 40 facets (2480 LPs, max coordinate deviation 3.94e-15)` |
| C4 | 复跑 `results/J2_core_oracles.py`，只取 coherence 部分：6 条 R6 符号恒等式 residual 全为 0（含 `R6 pred nonnegative-slack identity` 与 `R6 cons nonnegative-slack identity`）；`R6_full_lattice_lp` 里 pred / cons / mono 三族在 case a,b,c 上的最小 slack | [VERIFIED-SYMBOLIC] + [VERIFIED-LP 浮点] PASS | exit code 0，6.4 秒；6 条恒等式；1,368 个 coherence 方向的 LP 目标；最小 slack：pred_a 0、pred_b −6.66e−16、pred_c 0、cons_a 0、cons_b −1.11e−16、cons_c 0、mono_a/b/c 0（HiGHS 浮点，故标 [VERIFIED-LP 浮点]）；`results/J2_core_oracles.json` 复跑后按字节还原 |
| C5 | Running example：K = 3、η = 3/2 的精确最坏轨迹（prop:rigidity 的 j = 2 分支），在三步上逐步检 sharp form | [VERIFIED-EXHAUSTIVE] PASS | 3 步，3 步全取等 |

精确性说明：C3 的 facet 项与 C4 的 LP 项走 HiGHS 浮点，按房规标 [VERIFIED-LP 浮点]，不标 exact；两者的符号部分标 [VERIFIED-SYMBOLIC]。
本脚本自身的每个判定（C0–C2、C5 与全部 Criterion D）都是精确有理或符号的。

### 一个值得记的结构事实

C0 查出：(i) 的 slack、(ii) 的 slack、sharp form 第一个不等号的 slack 三者**恒等**，因为 f 的两序展开给出 D = d + h − g 是恒等式。
也就是说 (i) 与 (ii) 不是"前者推后者"，而是同一条不等式的两种写法；附录 `app:coherence` 里"把 (i) 代入"的那一步是恒等改写。
C1/C2 在 185,272 个三元组上把这一点逐个核到精确相等（slack_(i) ≠ slack_(ii) 会被记成 violation，实际 0 次）。

---

## 2. Criterion D：对陈述本身的反例搜索

随机实例总数 **3,468**（C1 的 2,400 ＋ D1 的 200 ＋ D2 的 212 ＋ D3 的 205 ＋ D4b 的 451），**violations = 0**，没有 witness。
搜索覆盖的族见 `coherence.json` 的 `families` 段：单调非 submodular 半边以 convex_cardinality 699、free_monotone 193、
modular 140 与 mono_mix 混合 168 为主；submodular 半边以 modular 629、budget_additive 137、concave_cardinality 127、
coverage 120 与 mixture 187 为主。两半合计实现了 358 个不同的有理 η 值，从 1 到 5（`eta_histogram`）。

worst slack / ratio：

- (ii) 的 slack（＝ (i) 的 slack）最小值 **0**，取等；全体 199,348 个三元组里有 **29,398 个取等**。
- (i) 的比值 η·d_e(S∪{e'}) / d_{e'}(S∪{e}) 最小值 **1**；限制到更有信息量的一格（η > 1 且 d_{e'}(S∪{e}) > 0，共 126,455 个三元组）
  最小值**仍是 1**，在 n = 6、S = {4}、e = 0、e' = 5、η = 3/2、d = 1、g = 3/2、h = 3/2、d_e(S∪{e'}) = 1 处达到。
  也就是说 (i) 在随机实例上就已经紧，不需要专门构造。
- sharp form 第二个不等号 (1−1/η)(g−h) 的最小值 **0**（submodular 半边），在 η = 3、g = h = 5/2 处达到。

结构化情形：

| 情形 | 构造 | 结果 |
|---|---|---|
| D1 η = 1（取等） | 200 个实例，f̃ = c·f（convention B 下实现 η = (1/c)·c = 1 精确） | 7,376 个三元组，每个的实际 η 都是 1，(i)(ii) 都塌成 d ≥ g（假设 d̃_e ≥ d̃_{e'} 在 η = 1 时就是 d ≥ g），其中 3,099 个取等，0 violation |
| D2 d_e(S) = 0 | 212 个 budget-additive 实例（饱和后大量零边际） | 5,138 个三元组里 1,395 个有 d_e(S) = 0。Definition 1 强制 d̃_e(S) = 0，再由假设 d̃_e(S) ≥ d̃_{e'}(S) ≥ 0 得 d̃_{e'}(S) = 0，故 g = d_{e'}(S) = 0；于是 (i) 读作 h ≥ h/η、(ii) 读作 (1−1/η)h ≥ 0。0 violation |
| D3 S = 空集 | 205 个实例，只测 S = ∅ | 1,562 个三元组，0 violation |
| D4a must-not-claim（显式 witness） | 见下一节 | **确认台账 T5 的禁止声称**：只在 run states 上假设 band 时引理不成立 |
| D4b must-not-claim（随机计数） | 451 个"预测器只在 run states {∅, {e_0}} 上合法"的实例 | 1,126 个三元组在 η^tr 下测试，**15 个实例违反 (ii)**，最差 slack −3/2（n = 3、coverage、η^tr = 4、d = 5、g = 11、h = 6） |
| D5 sharp form 第二式需要 submodularity | f = (0,1,1,3) 于 N = {e,e'}，单调但非 submodular | g − h = 1 − 2 = −1 < 0；配 f̃ = (0,1,1,2) 得实现 η = 2，(1−1/η)(g−h) = −1/2 < 0，**第二个不等号失效**；而 (i)(ii) 的 slack 都还是 1 ≥ 0。故 (i)(ii) 不需要 submodularity，sharp form 的第二式需要 |

### D4a：台账 T5 "禁止声称"的显式反例

N = {e, e'}；f(∅) = 0、f({e}) = 1、f({e'}) = 2、f({e,e'}) = 2（单调且 submodular）；
f̃(∅) = 0、f̃({e}) = 1、f̃({e'}) = 1、f̃({e,e'}) = 3/2。

- 假设成立：d̃_e(∅) = 1 ≥ d̃_{e'}(∅) = 1。predictive greedy 在 ∅ 上打平，对抗 tie 选 e，run states 是 {∅, {e}}。
- 这两个 state 上 Definition 1 没有任何违反，实现的 **η^tr = 2**（η_u^tr = 2，η_o^tr = 1）。
- 离轨 state {e'} 上 d_e({e'}) = 0 而 d̃_e({e'}) = 1/2 > 0，Definition 1 要求 d = 0 时 d̃ = 0，所以**全局 band 失效**（全局 η 无穷）。
- 在 η^tr = 2 处：(ii) 读作 (1 − 1/2)·1 = 1/2 ≥ 2 − 1 = 1，**假**，slack = −1/2；
  (i) 读作 d_e({e'}) = 0 ≥ (1/2)·d_{e'}({e}) = 1/2，**假**，slack = −1/2。

这正是台账 T5 "禁止声称：对 η^sel 或 η^tr 成立（它用到离轨状态 S∪{e} 的误差带，必须全局 η）"所记的事。
一处措辞补正：证明用到的离轨状态是 **S∪{e'}**（未被选中的那个元素加进去的状态，上面 (i) 的第三步 upper band 就在这里），
不是台账卡上写的 S∪{e}；S∪{e} 在 run 里就是下一个 run state。禁令本身成立，理由的状态名建议按此更正。

---

## 3. Running example（K = 3，η = 3/2）

k_1 = 4、q = 3/4、j = 2：轨迹 d_t = (1/4, 3/16, 1/8)，最优元素边际 g_t = (1/3, 1/4, 3/16, 3/16)，Σd_t = 9/16 = V_2(3/2) = ρ_3(3/2)。
逐步 sharp form：t=0 的 d − g/η = 1/4 − 2/9 = 1/36 = (1−1/η)(g−h) = (1/3)(1/3 − 1/4)；t=1 的 1/48 = (1/3)(1/4 − 3/16)；t=2 的 0 = (1/3)·0。
三步的第一个不等号**全部取等**，t=2 恰是 corollary 的情形（η > 1 且 d = g/η = 1/8，于是 h = g = 3/16）。

---

## 4. FAILED 项

无。12 个 check 全 PASS，Criterion D 的 3,468 个随机实例与 5 组结构化情形共 0 次违反；
D4/D5 两项是**按预期失败的反向情形**（各自的失败条件和参数写在上表与上一节），不是本引理的反例。

---

## 5. 结论（按房规的状态标签）

- lem:coherence (i)(ii)，f 单调（不必 submodular），全局 η：[VERIFIED-SYMBOLIC]（三项非负 slack 分解，C0 自推 + C4 复跑 J2 的 R6 恒等式）
  ＋ [VERIFIED-EXHAUSTIVE]（2,400 个随机精确实例的 185,272 个三元组，0 violation）。
- sharp form 第一个不等号 d − g/η ≥ (1−1/η)(g−h)：与 (ii) 恒等，[VERIFIED-SYMBOLIC]（C0 自推 + C3 复跑 H_J3）。
- sharp form 第二个不等号 (1−1/η)(g−h) ≥ 0：需要 f 的 submodularity 与 η ≥ 1，[VERIFIED-SYMBOLIC] ＋ D5 给出去掉 submodularity 后的失效实例。
- 对 η^sel / η^tr 的版本：[FAILED]，D4a 的显式实例 f = (0,1,2,2)、f̃ = (0,1,1,3/2) 在 η^tr = 2 下同时违反 (i) 与 (ii)（各 slack = −1/2），
  D4b 在 451 个只保证 run-state band 的实例里数到 15 个违反。台账的禁止声称成立。
