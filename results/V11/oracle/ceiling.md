# V11 Q3 oracle 报告：thm:ceiling（台账 T8，降级为 Proposition）

脚本：`results/V11/oracle/ceiling.py`（一键运行 `python3 results/V11/oracle/ceiling.py`，全部通过时 exit 0）
日志：`results/V11/oracle/ceiling.log`
机器可读：`results/V11/oracle/ceiling.json`
本次运行：9 个 check 全 PASS，0 个 violation，exit code 0，用时 55.0 秒。

陈述来源 `results/V11/inputs/statement_ceiling.md`。路线甲（upper bound + J5 三步交换证明）来自
`paper/sections/appendix_proofs.tex` 的 `app:ceiling` 与 `results/J5_hardcore/J5_ceiling_proof.md`；
路线乙（n ≥ 2K 的达到方向）来自 `paper/sections/appendix_model_proofs.tex` 末尾 remark（Prop 2(iii) 加
Horel-Singer 观察）与 `HANDOFF_ADDENDUM_2026-09-18.md` 的 C 节。按 addendum B.3，正文只留 n ≥ 2K，
K ≤ n < 2K 的精确值进附录 remark；本脚本两段都查。

---

## 1. 查了什么，结果如何

| 编号 | 内容 | 状态标签 | 精确计数 |
|---|---|---|---|
| C0 | sympy 恒等式：C* 两个分支、slack 恒等式 (7)、E 的三项分解 (8)、单次交换四项分解 (9)、Horel-Singer 的 eps=(η−1)/(η+1) 与 (1−eps)/(1+eps)=1/η、对手比值两式 | [VERIFIED-SYMBOLIC] PASS | 10 条恒等式，residual 全为 0 |
| C1 | n ≥ 2K 对手族（K=2..4，n=2K..10，14 组有理拆分）：f 单调 submodular、band 的最小因子恰为 (η_u,η_o)、O 最优且 f(O)=cKη_u、每个与 O 不交的输出 T 满足 f(T) ≤ f(O)/η | [VERIFIED-EXHAUSTIVE] PASS | 186 个实例，73,280 个子集，337,728 次单调、704,096 次 submodular、337,728 个 band pair、4,828 次不交 T 检查 |
| C1b | 同上，K=1 单独跑（n=2..10） | [VERIFIED-EXHAUSTIVE] PASS | 108 个实例，24,528 个子集，110,592 次单调、227,316 次 submodular、110,592 个 band pair、648 次不交 T 检查 |
| C2 | 达到方向，随机精确实例（n ≥ 2K，n ≤ 7，K ≤ 3）：对抗 tie 下最差的 f̃-argmax K-集 S 满足 f(S) ≥ OPT/η，且对每个最优 O* 满足逐实例式 f(S) ≥ K/(K+(η−1)|O*∖S|)·OPT | [VERIFIED-EXHAUSTIVE] PASS | 2,200 个实例，4,454 次逐实例检查，2,830 次 f̃ 抽样被拒；族分布 modular 987、budget_additive 297、concave_cardinality 262、coverage 242、mixture 412 |
| C3 | 对手方向打三类算法（f̃ 上的 predictive greedy、f̃ 的穷举 argmax、固定输出）：比值 ≤ 1/η | [VERIFIED-EXHAUSTIVE] PASS | 882 次算法运行（K=1..4，n=2K..10，14 组拆分，3 类算法） |
| C4 | 复跑 `results/J5_hardcore/J5_hardcore_oracles.py --output-dir results/V11/oracle/j5_reproduced` | [VERIFIED-LP 浮点]（52 个 LP 用 scipy linprog）＋[VERIFIED-SYMBOLIC]（恒等式）＋[VERIFIED-EXHAUSTIVE]（modular 实例） PASS | exit code 0，26.9 秒；log 关键计数：status PASS、symbolic identities 14、monotonicity numerator terms 84、exhaustive-search independent LPs 52、modular witnesses 24 实例 / 37,056 个 all-pairs 增量、double-submodular instances 56、K=4 η=3/2 的 16 个有理对偶证书最小值 23/41、PE1 有理 witness 4/9 |
| C5 | K ≤ n < 2K 的随机精确实例（K=2..4，n=K..2K−1）：穷举 argmax f̃ 满足逐实例式与 C*_{n,K} | [VERIFIED-EXHAUSTIVE] PASS | 1,200 个实例，2,330 次逐实例检查，966 次抽样被拒 |
| C6 | app:ceiling 的小 n 对手（K=1..5，n=K..2K−1）：比值恰为 K/(K+(η−1)min{K,n−K})，band 因子恰为 (η_u,η_o)；n=K 用混合高低权的校准变体，输出整个 ground set，比值 1 | [VERIFIED-EXHAUSTIVE] PASS | 198 个实例，68,892 次单调、119,116 次 submodular、68,892 个 band pair |
| D | 结构化情形 η=1、η=K、n=2K、n=K、n=2K−1 | PASS | 5 个情形全 PASS |

C4 的精确性说明：J5 脚本里 52 个全格点算法侧 LP 调 `scipy.optimize.linprog`，判定用浮点加
`1e-8` 容差，所以该项标 [VERIFIED-LP 浮点]，不标 exact；同一脚本的 14 条 sympy 恒等式、24 个 modular
对手实例（37,056 个 all-pairs 增量）与 K=4 的 16 个对偶证书用 `Fraction` 精确复算，这几项是 exact。
本脚本自身的每个判定都用 `fractions.Fraction` 或 sympy，浮点只出现在打印文本里。未修改任何既有仓库文件。

---

## 2. Criterion D：对陈述本身的反例搜索

随机实例总数 **3,544**（C2 的 2,200 ＋ C5 的 1,200 ＋ η=1 结构化情形的 144），覆盖 modular、coverage、
concave-of-cardinality、budget-additive 与它们的两两有理混合，配随机合法 f̃（按 Definition 1 的约束
逐层抽样，实际因子事后精确算出）。**违反数 0。**

最紧的三处（slack 都恰为 0，即不等式在这些点取等，不是违反）：

- 逐实例式最紧：slack = 0，C2，n=2，K=1，η=372/227，a=0，比值 1 对界 1，族 concave_cardinality。
- 全局式 f(S) ≥ OPT/η 最紧：slack = 0，C2，n=5，K=1，η=1，比值 1 对界 1，族 budget_additive。
- 对手侧最紧：1/η − max 比值 = 0，C1，K=2，n=4，(η_u,η_o)=(1,1)，不交 T 的最大比值 1 对界 1。
- C3 三类算法里最大比值：1（predictive greedy，K=1，n=2，η=1，界 1）。

结构化情形逐条结果：

- **η=1**：C* = 1；144 个 f̃ = c·f 的随机实例实际 η 精确为 1，f̃-argmax 的 K-集恰是最优集。PASS
- **η=K**：K=2,3,4 在 n=2K 上对手比值分别为 1/2、1/3、1/4，与 C* 相同。PASS
- **n=2K**：C* 的两个分支在此处相等，都等于 1/η；η=3/2 时 K=1..4 的对手比值均为 2/3。PASS
- **n=K（输出整个 ground set）**：C* = 1，比值精确为 1；混合高低权的校准变体仍使误差两端恰好取到（K=2..5）。PASS
- **n=2K−1**：C* = K/(1+(K−1)η) 被精确取到；η=3/2 时 K=2..5 分别为 4/5、3/4、8/11、5/7。PASS

一处范围说明：n = K = 1 时 ground set 只有一个元素，只带一个权重，误差两端只能在 η=1 时同时取到。
陈述本身假设 2 ≤ K ≤ n，附录的校准也要求至少两个元素，所以脚本在 n=1 的 12 个格点上不施加
“两端都取到”的要求，比值与 f 的合法性仍然检查。这不是违反，是量词范围。

---

## 3. Running example：K=3，η=3/2

n=6 对手（c=1，拆分 (η_u,η_o)=(3/2,1)）：f(O)=9/2，f(T)=3，比值 2/3 = 1/η。
n=5（=2K−1）对手：f(S)=3，f(O)=4，比值 3/4 = C*_{5,3}(3/2)。
逐实例式按 a=|O*∖S|=0,1,2,3 依次给 1、6/7、3/4、2/3。

---

## 4. 未被 oracle 覆盖的部分

- 一般集合上的交换求和、望远镜求和与 minimax 量词装配仍是 [HAND-PROOF-UNREVIEWED]（来源 J5 套 A）。
  本脚本查的是有限实例族加符号恒等式，不是任意 n、K 的机器证明。
- 随机算法的 minimax 值仍 [OPEN]；本脚本不碰随机侧，n=3、K=2、η=3 的确定性值与随机期望不同这一点由
  台账 T8 记录。
- C4 的 52 个 LP 是浮点判定，见上。

## 5. FAILED 项

无。本次运行 0 个 FAILED，0 个 violation。
