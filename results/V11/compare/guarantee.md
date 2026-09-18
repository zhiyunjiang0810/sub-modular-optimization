# ROUTE-COMPARISON：prop:guarantee（ledger T3，Goundan-Schulz 2007 归属）

TASKS11 Q5a，criterion B。本文件只做比对，不修改任何既有文件，未运行 git。

- **路线一（repo proof）**：`paper/sections/appendix_proofs.tex` 的 `\subsection{...}\label{app:guarantee}`（第 215 行起，Step 1 至 Step 4 加 `rem:app-product`），
  陈述在 `paper/sections/results.tex` 第 79 行，定义在 `paper/sections/model.tex`（`def:eta`、`def:etasel`、模型约定），
  台账卡 `THEOREM_LEDGER.md` 的 `## T3`。
- **路线二（blind derivation）**：`results/V11/route2/guarantee.md`，oracle 脚本 `results/V11/route2/verify_guarantee.py`。
- **本轮独立复算脚本**：`/tmp/claude-0/-home-user/09d7d9a5-0b14-54a1-894a-d76a6d641333/scratchpad/judge_guarantee.py` 与
  `judge_instance.py`（全部 `fractions.Fraction` / `sympy`，float 只在打印里）。

---

## 1. Step 对应表

列 "路线一位置" 指 `app:guarantee` 的 paragraph 编号，或 `model.tex` 的定义/约定行。

| 路线二的步骤 | 路线一的对应位置 | 判定 |
|---|---|---|
| Step 1 run 良定义（`\|S^t\|=t`，`t<=K-1<=n-1` 故候选集非空） | `model.tex` 模型约定 "Throughout, `1<=K<=n`; ... `K>=1` excludes empty runs" | 对应（路线一不单列此步，放在模型约定里） |
| Step 2 `d_e(S)>=0`、`g_t<=M_t`、`a_t>=1`、`etasel in [1,inf]` | `def:etasel` 的括注 "(monotonicity of f gives `g_t>=0`)" 与 app Step 2 首句 | 对应 |
| Step 3 `etasel=inf` 或 `f(O*)=0` 的平凡闭合 | app Step 2 的 harmful 分支（`M_t>0` 则 `a_t=inf`，`L_K(inf)=0`，"nothing needs proving"）加 `model.tex` 的 "`f(O*)=0` ... trivially" | 对应 |
| Step 4 per-step `M_t<=etasel g_t`，按 `a_t` 三分支核对 | app Step 1 末段 "`M_t=a_t g_t<=etasel d_{e_t}(S^t)` whenever `etasel` is finite" 加 app Step 2 | 对应 |
| Step 5 覆盖引理 `f(O*)-f(S)<=sum_{e in O*\S} d_e(S)<=K max_{e notin S} d_e(S)` | app Step 1 前段（telescoping、每项一次 submodularity、monotonicity 给 `f(O* ∪ S)>=f(O*)`、`m<=\|O*\|<=K`） | 对应，逐字同构。路线一注明 "This is the only place where the count `m<=K` enters"，路线二 Q3 给出同一观察 |
| Step 6 合并为 `Delta_t<=K etasel (Delta_t-Delta_{t+1})` | app Step 1 的第一个 display | 对应 |
| Step 7 递推 `Delta_{t+1}<=(1-c)Delta_t`，`c=1/(K etasel) in (0,1]` | app Step 1 的第二个 display | 对应 |
| Step 8 归纳 K 次，显式指出只需 `1-c>=0`、不需要 `Delta_t>=0` | app Step 3 "iterating K times" | 对应但**更强**：路线一在 app Step 2 的 benign 分支里用了 `r_t>=0`（"the run has already reached the optimal value"），路线二的归纳对 `Delta_t` 的符号不作要求 |
| Step 9 `Delta_0=f(O*)`（用 `f(∅)=0`），得第一个不等式 | app Step 3 的 display | 对应 |
| Step 10 `1-u<=e^{-u}`、`u=1/(xK) in (0,1]`，得第二个不等式 | app Step 3 末句 | 对应，逐字同构 |
| Step 11 `dL_K/dx=-(1-1/(xK))^{K-1}/x^2<=0` 加 `lim_{x->inf}L_K=0=L_K(inf)` | app Step 4 末段 "`x -> 1-1/(xK)` is increasing on `x>=1` with values in `[0,1)`, so ... `L_K` is decreasing" | **不同论证，同一结论**：路线一走底数单调，路线二走导数。两者都成立；路线二额外补了 `x=inf` 端点 |
| Step 12 `etatr` 的形式定义（band 只在 `S^0..S^{K-1}` 上要求，两因子各取最紧值相乘并以 1 截断） | `model.tex` 只有一句 "The trajectory error restricts Definition~\ref{def:eta} to the states of the run ... written `etatr`"，无公式；`def:etasel` 的状态集正是 `S^0,...,S^{K-1}` | **路线一无公式**。路线二自行补定义，见第 4 节第 1 条：状态集选择与 `def:etasel` 一致，因子下限 1 与 `def:eta` 的 "`eta_u,eta_o>=1`" 一致，故该 added assumption 在 verbatim 约定下与路线一吻合 |
| Step 13 `etasel<=etatr`（argmax 加 band 上下夹，三分支核对） | app Step 4 的 display 加其后两句 | 对应。路线一在 `g_t=0` 时断言 "the same display forces `M_t=0`, so `a_t=1`"（以有限 band 为前提）；路线二的分支 (iii) 允许 `etatr=inf` 并给 `a_t=inf=etatr`。两者相容，路线二覆盖面更宽 |
| Step 14 `etatr<=eta`（轨迹状态集是 `2^N` 的子族） | app Step 4 括注 "(`etatr<=eta` because the states of the run are a subset of all sets)" | 对应，但截断约定有差别，见第 3 节 D2 |
| Step 15 串联得 `L_K(etasel)>=L_K(etatr)>=L_K(eta)` 与整条不等式链 | app Step 4 末句 "the bound of Step 3 holds a fortiori with `etatr` or `eta`" | 对应 |
| 3.1 至 3.2 节 `K=3, eta=3/2` 数值走查（`L_3(3/2)=386/729`，递推表 `1, 7/9, 49/81, 343/729`） | 路线一无数值走查 | 路线二独有，本轮独立复算逐位一致 `[VERIFIED-SYMBOLIC]` |
| 3.3 节精确取等的 weighted coverage 实例（6 元素，`etasel=3/2`，`f(T)=386/729=L_3(3/2)`） | `thm:tightness`（`results.tex` 第 122 行）与 `app:tightness` 的 `U_K` 族（`2K` 元素，`etasel=etatr=â`）；**不在 `app:guarantee` 内** | 不同构造。两者都只是存在性证据，互不矛盾；差别见第 3 节 D5 |
| 3.4 节 400 个随机 coverage 实例 | 台账 T3 记 "[VERIFIED-LP 第一晚基线]"，`app:guarantee` 正文明确写 "No script checks the computations of this proof"（该句在第 213 行，紧邻 subsection 之前，属上一小节） | 路线二独有的 oracle 支持 |

### 路线一中路线二未覆盖的内容

| 路线一的步骤 | 路线二的状态 |
|---|---|
| app Step 2 的 benign 零步论证：由覆盖不等式得 `r_t<=K M_t=0`，"run 已达最优"，且 `r_s=0` 对一切 `s>=t` | **不同路线**。路线二不作分类讨论，Step 6/7 的不等式在 `g_t=0` 时自动读作 `Delta_t<=0`，Step 8 的归纳不需要 `Delta_t>=0`。结论相同，路线二的写法少用一个前提（`r_t>=0`，它需要 `O*` 在 K-set 中最优） |
| `rem:app-product` 逐步乘积界 `f(S^K)>=(1-prod_t(1-1/(K a_t)))f(O*)`，以及提前停止只有已执行步的乘积界、两元素实例把停止版压到 `1/2` 对照 `L_2(1)=3/4` | **路线二未覆盖**。路线二 Q7 只说明提前停止不在本命题范围，未推导乘积界 |
| Goundan-Schulz 归属：`alpha=etasel`（同向，不取倒数），per-step condition 对应 `a_t=inf` 分支（`def:etasel` 尾段 + `results.tex` 正文 + 台账 D2） | **路线二未覆盖**（盲证，输入包不含归属信息）。写入正文时须保留 D2 的归属措辞 |
| D3 历史注记：旧定义（只算正步）的无条件证书读法被 J2 三元素 modular 反例推翻，`results/H3_j2_recheck.py` 复验；新定义下 benign 零步无需求助全局 band | **路线二未覆盖**，但结构上免疫：路线二第一个不等式全程不使用 `def:eta` 的全局 band，只用 per-run 的 `etasel` |
| 台账 T3 的 must-not-claim 清单（禁 "we prove"、禁对非单调目标称 certificate、禁对提前停止变体声称本命题、禁由停止前 `etasel` 推 `L_K`） | 路线二遵守了措辞禁令（全文标 `[HAND-PROOF-UNREVIEWED]`，未用禁用动词），但未复述清单 |

---

## 2. 判定

### (1) 结论与量词

**结论完全一致。** 两条路线都给出，对任意 monotone submodular `f`（`f(∅)=0`，取值非负）、任意 `f̃`（`f̃(∅)=0`）、任意 `1<=K<=n`、predictive greedy 恰跑 K 步且 ties 对抗打破的每一条轨迹：

```
f(T) >= L_K(etasel) f(O*) >= (1-e^{-1/etasel}) f(O*),   L_K(x)=1-(1-1/(xK))^K, L_K(inf)=0
```

并在 predictor 有有限 `(eta_u,eta_o)` 时给出 `etasel<=etatr<=eta` 与 `L_K(etasel)>=L_K(etatr)>=L_K(eta)`。

量词清单**不完全重合**，差异两条，见第 3 节 D1 与 D2。

### (2) 路线二是否依赖补加假设 / 有 gap 或 error

有一条补加假设（`etatr` 的形式定义，路线二自己登记为 `[ASSUMPTION-ADDED]`），在 verbatim 约定下与路线一吻合；另有两处可复算的瑕疵（D2、D4），均不在结论链上。主链 Step 1 至 Step 10 本轮逐步复核未发现错误。所有数值本轮独立复算一致：

- `L_3(3/2)=386/729=0.5294924554...`，`1-e^{-2/3}=0.4865828809...`，余量 `0.0429...` `[VERIFIED-SYMBOLIC]`
- 递推表 `Delta` 依次 `1, 7/9, 49/81, 343/729`，`f(S^t)` 下界依次 `0, 2/9, 32/81, 386/729` `[VERIFIED-SYMBOLIC]`
- `dL_K/dx + (1-1/(xK))^{K-1}/x^2` 经 sympy 对符号 `K` 化简为 `0` `[VERIFIED-SYMBOLIC]`
- 精确有理网格 `K in 1..12`、`x in {1,1.25,...,10}`：`min (L_K(x)-(1-e^{-1/x})) = 3.790439e-04 > 0`，在 `K=12, x=10` 取到 `[VERIFIED-EXHAUSTIVE]`
- 3.3 节实例本轮从描述独立重建（weighted coverage，6 元素，`c_0=100/343`）：`a_0=a_1=a_2=3/2`，`f(T)=386/729=L_3(3/2) f(O*)`，`eta_u^tr=49/22`、`eta_o^tr=1`、`eta_u=343/100`、`eta_o=1`，`L_3` 值 `0.529492 > 0.385137 > 0.264130`，与路线二 PART B 输出逐位相同 `[VERIFIED-EXHAUSTIVE]`
- `results/V11/route2/verify_guarantee.py` 本轮复跑 OVERALL: PASS（PART A/B/C 全过，PART C 400 例 0 违反）

### (3) 路线二是否与路线一的某一步矛盾

**没有。** 唯一的结构性差别是 benign 零步的处理（路线一分类讨论，路线二统一递推），两者给出同一结论且路线二的前提更少。路线一本身本轮未发现可展示的错误。

### 结论

**verdict: B-PASS**（同一路线，其中一个 sub-step 由不同且更弱前提的论证给出；路线二无影响结论的错误）。

---

## 3. Divergences（逐条）

- **D1（量词域，`(eta_u,eta_o)` 的取值范围）**：路线一用 `def:eta` verbatim，`eta_u,eta_o>=1`；路线二 Q9 写 convention B，`eta_u,eta_o>0` 且乘积 `>=1`（取自 `results/V11/inputs/definition1.md` 末段）。这是两条量词清单唯一的实质差异。
- **D2（由 D1 派生的 `etatr` 截断方向，可复算）**：路线二 Step 12 把 `etatr` 的**两个因子各自**以 1 截断，Step 14 的括注 "`eta=eta_u eta_o>=1` 也被同样截断" 默认全局因子同样逐因子截断。在 verbatim 约定下这是自洽的，`etatr<=eta` 成立。但在路线二 Q9 自己引用的 convention B 下不成立：取 `f̃=2f`（任意 monotone submodular `f`），全局 `(eta_u,eta_o)=(1/2,2)`、`eta=1`，而路线二逐因子截断后的 `etatr=max(1,1/2)*max(1,2)=2>1=eta`，序关系反向 `[VERIFIED-EXHAUSTIVE]`（`judge_instance.py` 末段）。修法是把截断放在**乘积**上而不是因子上，此时 `etatr<=eta` 由 "轨迹 band 的可行 `(eta_u,eta_o)` 对是全局可行对的超集" 直接成立，与路线一 app Step 4 的括注同构。路线二 4.2 条称该截断 "只会让 `L_K(etatr)` 变小，是保守方向"：这对 `etasel<=etatr` 方向正确，对 `etatr<=eta` 方向不正确。路线一因为只在 `def:eta` verbatim 内部论证，不暴露该问题；若论文整体切换到 convention B，路线一 app Step 4 的括注同样需要改写成 "可行对的子族" 措辞。**不影响本命题结论**：`f̃=2f` 时 `etasel=1`，`f(T)>=L_K(1)f(O*)` 与命题的 `eta` 版本都成立。
- **D3（`etatr` 的形式定义缺位）**：路线一（`model.tex` 与 `app:guarantee`）都没有 `etatr` 的公式，只有 "restricts Definition 1 to the states of the run"。路线二 Step 12 补了公式。状态集取 `S^0,...,S^{K-1}` 与 `def:etasel` 一致，故这条 added assumption 在字面上也与路线一吻合；若正文日后把状态集改成含终态 `S^K`，Step 13 与 Step 14 的方向不变。
- **D4（Q10 的反例侧注，奇偶写反，可复算）**：路线二 Q10 称 "若允许 `x<1/K`，底数为负，`K` 为偶数时 `L_K(x)>1`"。实际是**奇数** `K`：`K=3, x=1/6` 给 `L_3=2>1`，`K=5, x=1/10` 给 `L_5=2>1`，而 `K=2, x=1/6` 给 `L_2=-3<1`，`K=4, x=1/6` 给 `L_4=15/16<1` `[VERIFIED-EXHAUSTIVE]`。该区域被命题的 `x in [1,inf]` 排除，不影响任何推导，只是量词表里那句解释写反了。
- **D5（取等实例的构造不同）**：路线二 3.3 节的 6 元素 coverage 实例给出 `f(T)=L_3(3/2)f(O*)`，但其上 `etasel=3/2 < etatr=49/22 < eta=343/100`；路线一的 `thm:tightness`（`U_K` 族，`2K` 元素）在取等实例上另有 `etasel=etatr=â`。两者都是存在性陈述，互不矛盾；若引用取等实例来说明 `etatr` 也紧，只能用论文的 `U_K` 族，不能用路线二这一个。
- **D6（归属与 remark 未覆盖）**：路线二不含 Goundan-Schulz 归属（D2 决定）与 `rem:app-product` 的逐步乘积界及提前停止定价。这两条是路线一独有内容，合并时须从路线一取。
- **D7（`f̃` 非负性的措辞张力）**：`def:eta` verbatim 说 "all predicted gains are nonnegative"，而模型约定只要求 `f̃:2^N -> R`。两条路线都不依赖该非负性（路线一第一个不等式不碰 `f̃`，路线二 Step 1 至 Step 9 同样不碰），路线二 4.4 条已记录。不是分歧，仅登记。

---

## 4. Route-two gaps（逐条）

1. `[ASSUMPTION-ADDED]` **`etatr` 的形式定义**（路线二 Step 12 / 第 4 节第 1 条）。路线一未提供公式，故该假设不可由路线一证伪；本轮核对结论是它与 `def:etasel` 的状态集与 `def:eta` 的因子下限一致。**未闭合项**：论文若采用 convention B，这个定义要改成乘积层面截断（见 D2）。
2. `[ASSUMPTION-ADDED]` **全零轨迹时的截断到 1**（路线二第 4 节第 2 条）。方向判断只对 `etasel<=etatr` 正确，对 `etatr<=eta` 不正确（D2 的 `f̃=2f` 反例）。这是本轮为路线二新发现的 gap，路线二自己未识别。
3. **`rem:app-product` 未推导**：路线二未给出逐步乘积界，也未给出提前停止版的 `1/2` 对照 `L_2(1)=3/4` 的反例。路线一有，属路线二覆盖缺口（非错误）。
4. **归属未给出**：路线二未标 Goundan-Schulz，台账 T3 的 D2 要求必须标注。
5. **Q10 奇偶写反**（D4），范围外的解释性瑕疵。
6. **tightness 未做**：路线二 4.5 条自述 `rho_K(eta)` 与 `L_K` 的关系未检查。与本命题无关，路线一也把它放在 `thm:exact` / `thm:tightness`。
7. **隔离说明**：路线二未打开 `HANDOFF_2026-09-18.md`、`HANDOFF_ADDENDUM_2026-09-18.md`、`appendix_model_proofs.tex`、`J8_claude_spotcheck.py`。本轮比对已代为核对：`appendix_model_proofs.tex` 不含 `prop:guarantee` 的证明（该证明在 `appendix_proofs.tex` 的 `app:guarantee`），`etatr` 在这两份 handoff 之外也没有公式定义，故路线二第 4.1 条的不确定性维持为 D3。

---

## 5. 本轮读过与复跑的文件

- `paper/sections/appendix_proofs.tex`（第 205 至 330 行，`app:guarantee` 全文加 `rem:app-product`）
- `paper/sections/results.tex`（第 79 至 130 行，命题陈述与 `rem:etasel-measurable`、`thm:tightness`）
- `paper/sections/model.tex`（全文：`def:eta`、`lem:scaling`、predictive greedy、`def:etasel`、`etatr` 一句）
- `THEOREM_LEDGER.md` 的 `## T3`
- `results/V11/route2/guarantee.md`、`results/V11/route2/verify_guarantee.py`（复跑 PASS）
- `results/V11/inputs/{statement_guarantee,assumptions,definition1}.md`

本文件为新建，未修改任何既有文件，未运行 git。
