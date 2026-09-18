# V11 Q2 oracle 报告：prop:valueacc（台账 T2，2026-09-18 方案二 / convention-B 改写）

复现命令：`python3 results/V11/oracle/valueacc.py`（exit 0 当且仅当全部检查通过）。
本次运行：exit 0，21 项检查全 PASS，0 FAILED，耗时 7.9 秒。
产物：`results/V11/oracle/valueacc.py`、`valueacc.log`（全部输出）、`valueacc.json`（机器可读）、本文件。
全部判定用 `fractions.Fraction` 或 sympy，float 只出现在打印文本里。随机种子固定：(i) 20260918、(ii) 20260919、(iii) 20260920。

## 1. 被测陈述与 route-one 材料

被测陈述：`results/V11/inputs/statement_valueacc.md`（convention B：eta_u, eta_o > 0 无下限，eta = eta_u eta_o >= 1，d_e(S)/eta_u <= dtilde_e(S) <= eta_o d_e(S)）。

读过但未修改的 route-one 材料：

- `paper/sections/appendix_model_proofs.tex`，subsection "Proof of Proposition~\ref{prop:valueacc}"（convention B：(ii) eta_u = 1/(1+M)、eta_o = 1+M、eta = 1；(iii) 沿链求和后取 c = 2 eta_u/(eta+1)，level (eta-1)/(eta+1)）。
- `paper/sections/appendix_proofs.tex`，subsection `app:valueacc`（约第 145 行，旧约定，带 eta_o < 2 前提，(i) 用的是另一个两元素实例）。
- `THEOREM_LEDGER.md` 的 `## T2` 卡（改写后的头部）。

## 2. Criterion C：oracle 结果（逐项）

| 编号 | 检查内容 | 状态 | 计数 |
|---|---|---|---|
| C1 | (i) 两元素构造 N = {a,b}，f(∅)=0、f(a)=f(b)=1、f({a,b})=1+eps，ftilde(a)=ftilde(b)=ftilde({a,b})=1，eps ∈ {1/10, 1/2, 9/10}：f normalized + monotone + submodular；ftilde 在每个子集上 value-accurate at level eps；dtilde_b({a}) = 0 < d_b({a}) = eps，故不存在有限 eta_u | PASS [VERIFIED-EXHAUSTIVE] | 3 个 eps × 4 个子集 |
| C1 | 同上补 4 个零增益元素到 n = 6（在 f 与 ftilde 下都零增益）：三项重查全过，且 band 要求的 "d = 0 处 dtilde = 0" 在 128 个 d = 0 的 (S,e) pair 上逐个成立 | PASS [VERIFIED-EXHAUSTIVE] | 3 个 eps × 64 个子集，每个 384 个 (S,e) pair |
| C1b | 旧附录 `app:valueacc` 的 (i) 实例（f(b) = 2eps/(1-eps)、f(ab) = (1+eps)/(1-eps)、ftilde(a) = ftilde(ab) = 1+eps）交叉核对：modular、monotone、value-accurate at level eps 且在 {a,b} 上取到下端，dtilde_b({a}) = 0 < d_b({a}) = 2eps/(1-eps) | PASS [VERIFIED-EXHAUSTIVE] | 3 个 eps |
| C2a | (ii) sympy 关于 M：ftilde = (1+M) f 的最小可行因子恰为 eta_o = 1+M、eta_u = 1/(1+M)，乘积 eta = 1；band 两端都取到 | PASS [VERIFIED-SYMBOLIC] | 4 个 residual 全为 0 |
| C2b | (ii) 数值精确重查：200 个随机单调 submodular f（coverage / modular / mixture / budget-additive，n <= 6）配随机有理 M：最小因子 = (1/(1+M), 1+M)、eta = 1；在任意 eps < M 处 value accuracy 被违反（给出见证集合）；每个 state 上 argmax dtilde = argmax d（故 eta^sel = 1） | PASS [VERIFIED-EXHAUSTIVE] | 200 个 instance，0 failure |
| C3a | (iii) sympy 恒等式：c/eta_u = 1-eps、c·eta_o = 1+eps（c = 2 eta_u/(eta+1)，eps = (eta-1)/(eta+1)），另加 1-eps = 2/(eta+1)、1+eps = 2eta/(eta+1)、(1-eps)/(1+eps) = 1/eta | PASS [VERIFIED-SYMBOLIC] | 5 个 residual 全为 0 |
| C3b | (iii) 定义域：eps(1) = 0，1-eps = 2/(eta+1) > 0，d eps/d eta = 2/(eta+1)^2 > 0，故 eta >= 1 时 eps ∈ [0,1) | PASS [VERIFIED-SYMBOLIC] | 3 个 residual 全为 0 |
| C4 | (iii) 2200 个随机**合法** surrogate（n <= 7；f 逐个精确验过 monotone + submodular；eta_u、eta_o 取**实际最小**可行因子）：中间式 f/eta_u <= ftilde <= eta_o f 与 (1-eps) f <= c ftilde <= (1+eps) f 在每个子集上成立 | PASS [VERIFIED-EXHAUSTIVE] | 2200 个 surrogate，57840 个子集，404 次抽样被判非法而重抽，0 violation |
| C4b | (iii) 陈述里 "No submodularity of f is used in (iii)"：400 个**单调但 submodularity 测试不通过**的 f（每个都先验过单调、且确实存在 submodularity 违反），配合法 surrogate：两条式子仍逐子集成立 | PASS [VERIFIED-EXHAUSTIVE] | 400 个 instance，0 violation |
| C5a | 结构化：eta = 1（ftilde = c0 f，c0 ∈ {1, 1/7, 13/3, 1000}）：c = 2 eta_u/(eta+1) = eta_u = 1/c0，且 c·ftilde = f 逐子集精确相等，eps = 0 | PASS [VERIFIED-EXHAUSTIVE] | 4 个 c0 |
| C5b | 结构化：很大的 eta（modular f 上逐元素因子，spread ∈ {100, 10^4, 10^6}，eta = spread^2 直到 10^12）：eps = (eta-1)/(eta+1) 精确落在 (0,1)，两条式子成立 | PASS [VERIFIED-EXHAUSTIVE] | 3 个 spread |
| C5c | 结构化：f 带零增益元素：两条式子成立，且 d = 0 处 dtilde = 0 | PASS [VERIFIED-EXHAUSTIVE] | 25 个 instance |
| C6 | 缩放不变性：ftilde 乘 c 时 (eta_u, eta_o) 两因子按倒数移动、eta 不变；(iii) 的缩放常数随之复合，c·ftilde 是同一个函数 | PASS [VERIFIED-SYMBOLIC] | 2 个 residual 全为 0 |
| C7a | 旧约定对照：max{1-1/eta_u, eta_o-1} 离开 (0,1) 当且仅当 eta_o >= 2（旧陈述那条前提的来源）；convention-B 的 level (eta-1)/(eta+1) 永不离开。显式点 (eta_u, eta_o) = (1, 5/2)：旧 level = 3/2 >= 1，新 level = 3/7 | PASS [VERIFIED-SYMBOLIC] | 2 个 residual + 1 个有理算例 |
| C7b | 复跑既有仓库脚本 `results/M1_checks.py`（旧约定 (iii) 定义域边界 + band 缩放恒等式；未修改） | PASS | exit code 0，8 行 PASS，0 行 FAIL，末行 `ALL PASS` |
| RE | K = 3、eta = 3/2 running example 的数字 | PASS [VERIFIED-EXHAUSTIVE] | 见 §4 |

累计精确判定次数：monotone 检查 182476 次，submodularity（local exchange 形式）检查 401245 次，band 的 (S,e) pair 检查 183231 次。

worst slack（C4，所有 2200 个合法 surrogate × 全部子集，取 min{c ftilde - (1-eps) f, (1+eps) f - c ftilde} / f(S)）：**0**，即 band 处处成立且在某些子集上取到等号，没有一次为负。限制到 eta > 1 的 1253 个 surrogate 上 worst slack 同样是 0，取等点例如 n = 2、f 为 budget-additive、surrogate = f + (9/8)·modular、eta_u = 1、eta_o = 89/80、eta = 89/80、eps = 9/169、c = 160/169、S 上 f(S) = ftilde(S) = 1/2。等号出现次数：下端 34472 次、上端 31725 次（共 57840 个子集）。这说明 (iii) 的 level (eta-1)/(eta+1) 在这一族上不可再降。

见到的最大 eta：22608/35 ≈ 645.9（n = 6，modular f，jitter surrogate，eta_u = 360，eta_o = 314/175）；C5b 的结构化算例把 eta 推到 10^12。

## 3. Criterion D：对陈述本身的反例搜索

随机抽样总数 **6597**，violations **0**。

- (i)：2000 次随机 eps ∈ (0,1)（分母 1000）配随机 0..5 个零增益补元素，逐次重查 f 单调 submodular、value accuracy at level eps、dtilde_b({a}) = 0 < d_b({a})、不存在有限 eta_u、以及 d = 0 处 dtilde = 0。violations 0。
- (ii)：1997 次随机 (f, M)（f 为随机单调 submodular，n <= 5；M 为随机正有理数，最大到 5000），逐次重查最小因子 = (1/(1+M), 1+M)、eta = 1、eps < M 处 value accuracy 被违反、每个 state 上 argmax dtilde = argmax d。violations 0。
- (iii)：2200 个随机合法 surrogate（C4）加 400 个单调非 submodular 实例（C4b）就是搜索本身。violations 0。

结构化 case 与结果：eta = 1（PASS）、很大的 eta（PASS）、单调非 submodular 的 f（PASS）、带零增益元素的 f（PASS）。

worst 记录：worst slack = 0（取等，非违反），参数见 §2；worst ratio 意义下最极端的是 C5b 的 eta = 10^12、eps = 999999999999/1000000000001，两条式子仍精确成立。

## 4. K = 3、eta = 3/2 running example

K = 3，eta = 3/2：(eta_u, eta_o) = (1, 3/2)，eps = (eta-1)/(eta+1) = 1/5，c = 2 eta_u/(eta+1) = 4/5。
modular 实例 n = 4、权重 (1,1,1,1)、预测因子 (1, 3/2, 1, 3/2)；在 3-set S = {0,1,2} 上 f(S) = 3、ftilde(S) = 7/2、c ftilde(S) = 14/5。
band：(1-eps) f(S) = 12/5 <= 14/5 <= 18/5 = (1+eps) f(S)，且 (1-eps)/(1+eps) = 2/3 = 1/eta。

## 5. FAILED 项

无。21 项检查全 PASS，Criterion D 的 6597 次抽样 0 violation。

## 6. 记录与限度

- 本脚本核的是陈述里可判定的部分。(i) 的末句 "no bound of the form L_K(eta) follows from value accuracy alone" 的可判定部分是"不存在有限 (eta_u, eta_o)"，已核；"因此任何 L_K(eta) 界落空"这一步是对 L_K(∞) = 0 约定的读法，属陈述解读，不由本 oracle 判定，仍按台账 T2 标 [HAND-PROOF-UNREVIEWED]。
- (ii) 的 eta^sel = 1 用的判据是：在每个 state 上 dtilde 的 argmax 集合与 d 的 argmax 集合相等。这对任何 tie-breaking（含对抗）都成立，比只跑一条 greedy 轨迹强。
- addendum §B 第 10 条提到的"96 个合法 surrogate 零违反"那次检查在仓库里找不到对应脚本；本脚本以 2600 个合法 surrogate（含 400 个非 submodular 实例）取代并扩展它，不引用那次结果。
- 未修改任何既有仓库文件；未运行 git。合法 surrogate 的四个生成器（scaled、plus_modular、elementwise、jitter）都按拒绝采样保证 band 合法，被拒 404 次已计入日志。
