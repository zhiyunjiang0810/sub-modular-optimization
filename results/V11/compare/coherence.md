# ROUTE-COMPARISON：lem:coherence（ledger T5）及其 sharp form

TASKS11 Q5b，criterion B。本文件只做比对，不修改任何既有文件，未运行 git。

- **路线一（repo proof）**：
  - 引理陈述 `paper/sections/results.tex` 第 136 至 175 行（`\subsection{The coherence lemma}\label{sec:coherence}`，含 sharp form 段落）；
  - 主证明 `paper/sections/appendix_proofs.tex` 第 524 行起 `\subsection{Coherence}\label{app:coherence}`；
  - sharp form 的 slack 证书 `results/H_J3_gate_check.py` item 1；
  - 三项非负 slack 分解 `results/J2_core_oracles.py` 的 `R6 pred / R6 cons nonnegative-slack identity`，
    以及它在正文中的落点 `paper/sections/appendix_proofs.tex` 第 2219 行 `lem:app-pred`、第 2253 行 `lem:app-cons`；
  - 台账卡 `THEOREM_LEDGER.md` 的 `## T5`。
- **路线二（blind derivation）**：`results/V11/route2/coherence.md`，oracle 脚本 `results/V11/route2/verify_coherence.py`。
- **本轮独立复算脚本**（全部 `fractions.Fraction` / `sympy`，float 只在打印里）：
  - `/tmp/claude-0/-home-user/09d7d9a5-0b14-54a1-894a-d76a6d641333/scratchpad/judge_coherence.py`
    （四条恒等式 + 路线一的 pred/cons/sharp form 三条恒等式 + 9 组 split 的有理顶点枚举 LP + 三组删行实验）；
  - `.../judge_coherence2.py`（4.3 取等族 23 组参数、6.2 的 K=2 实例、6.1 的 K=3 coverage 走查与全部 6 个 (t,e,e') 配对）；
  - `.../judge_coherence3.py`（路线一 sharp form 与其刚性推论在同一多面体上的精确求值）。
  - 三个脚本本轮全部通过，无 FAIL。

记号统一（下文与路线二一致）：固定 `S`、`e != e'`（`e,e' notin S`），
`A=d_e(S)`、`B=d_{e'}(S)`、`C=d_{e'}(S+e)`、`D=d_e(S+e')`，
带 tilde 者为对应预测量。路线一在 `sec:coherence` 与 `J2_core_oracles.py` 里用的是
`d=A`、`g=B`、`h=C`、`P=Ã`、`Q=B̃`、`R=C̃`，并把 `D`、`D̃` 写成 `d+h-g`、`P+R-Q`
（这正是交换恒等式的代入形式）。

---

## 1. Step 对应表

### 1.1 路线二的每一步对应到路线一

| 路线二的步骤 | 路线一的对应位置 | 判定 |
|---|---|---|
| §2 记号 `A,B,C,D,Ã,B̃,C̃,D̃` | `sec:coherence` 的 `d,g,h`，`lem:app-cons` 证明的 `d,g,h,P,Q,R` 加 `d+h-g`、`P+R-Q` | 对应。路线一把 `D`、`D̃` 直接写成交换恒等式的代入形式，等价于路线二把恒等式单列为 Step 1、Step 2 |
| Step 1：`f` 的交换恒等式 `A+C=B+D` | `app:coherence` 的 Part (ii) 首句 "The same two-order expansion applied to `f` reads `d_e(S)+d_{e'}(S+e)=d_{e'}(S)+d_e(S+e')`" | 对应，逐字同构。本轮 `[VERIFIED-SYMBOLIC]` |
| Step 2：`f̃` 的交换恒等式 `Ã+C̃=B̃+D̃` | `app:coherence` 的 paragraph "The exchange identity"（展开 `f̃(S+e+e')-f̃(S)` 的两种次序），并注明 "This uses nothing but the definition of a set function" | 对应，逐字同构 |
| Step 3：order transfer `D̃-C̃=Ã-B̃>=0` | `app:coherence` 的 `\eqref{eq:coh-pred}`：`d̃_{e'}(S+e)-d̃_e(S+e')=d̃_{e'}(S)-d̃_e(S)<=0` | 对应，同一式的符号翻转写法。路线二额外指出这条是**等式级、无常数损失**，路线一只用它的不等号方向 |
| Step 4：`eta_o D >= D̃ >= C̃ >= C/eta_u`，除以 `eta_o` 得 (i) | `app:coherence` 的 Part (i) 四项链 `C <= eta_u C̃ <= eta_u D̃ <= eta_u eta_o D`，除以 `eta` | 对应，同一条链只差一次整体乘 `eta_u`。两侧用的 band 实例完全相同：下界在 `(S+e, e')`，上界在 `(S+e', e)` |
| Step 5：恒等式 `(1-1/eta)C-(B-A) = D-C/eta`，故 (i) 与 (ii) 等价、同时取等 | `app:coherence` 的 Part (ii)：由 `f` 的交换恒等式加 (i) 的代入 `-D <= -(1/eta)C` 得到 (ii) | **对应但更强**。路线一只给 (i) ⇒ (ii) 的单向代入；路线二把它升级为恒等式，因此得到双向等价与"同时取等"。本轮 `[VERIFIED-SYMBOLIC]`，不与路线一冲突 |
| Step 6：`B <= eta A`，进而 `B-A <= (1-1/eta)B` | `lem:app-pred`（`appendix_proofs.tex` 第 2219 行）的 case (b) 链 `d_t >= d̃_{e_t}(S^t)/eta_o >= d̃_{o_i}(S^t)/eta_o >= g_{t,i}/eta`；其三项 slack 分解见 `J2_core_oracles.py` 的 `R6 pred nonnegative-slack identity` | **对应**，路线二称之为"同一状态上的平行推论"，路线一把它独立成 `pred(t,i)` 约束族。路线二未意识到这一步在路线一里是 reduced LP 的一整族约束 |
| Step 7：松弛分解 `eta_o D - C/eta_u = (eta_o D - D̃)+(Ã-B̃)+(C̃-C/eta_u)` | `lem:app-cons` 证明里的 display：`(1-1/eta)h-g+d = (eta_o(d+h-g)-(P+R-Q))/eta_o + (P-Q)/eta_o + (eta_u R-h)/(eta_u eta_o)`；亦即 `J2_core_oracles.py` 的 `R6 cons nonnegative-slack identity` | **对应，逐项同构**。两式相差整体因子 `eta_o`：路线二的 (3.8) 等于路线一 display 两端乘 `eta_o`，三项一一对齐（band 上界项、greedy 假设项、band 下界项）。本轮 `[VERIFIED-SYMBOLIC]` 同时验证了两种写法 |
| §4.1 (S1) order transfer 无常数 | 路线一无对应条目 | 路线二独有（是 Step 3 的重述） |
| §4.1 (S2) 常数 `1/eta` 不可改进 + 显式取等族 | 路线一无对应条目：`app:coherence` 与 `sec:coherence` 都不含 tightness 断言 | **路线二独有**。本轮独立复算 23 组 `(eta,c)` 参数逐条通过 `[VERIFIED-EXHAUSTIVE]` |
| §4.1 (S3) min 形式 `B-A <= (1-1/eta) min{C,B}`，submodularity 只用于判定 `min=C` | 路线一 sharp form 的第二个不等号 `(1-1/eta)(g-h) >= 0`（即 `C <= B`，由 submodularity 加 `eta>=1`），以及 `lem:app-mono`（`g_{t+1,i} <= g_{t,i}`，"submodularity in its diminishing-returns form"） | **部分对应**。同一个数学事实（`C<=B` 需要 submodularity），但打包方式不同：路线一用它把 sharp form 的右端钉到非负，路线二用它判定 min 取在哪一支 |
| §4.1 (S4) 取等刻画（三项松弛同时为零） | 路线一无对应条目（`prop:rigidity` 是 reduced LP 层面的轨迹刚性，不是本引理的取等刻画） | 路线二独有 |
| §4.4 删掉 `f̃` 交换恒等式后 `min(eta D-C)=-1/6`、`min((1-1/eta)C-(B-A))=-1/9`，见证点 `A=1/3,B=1/2,C=1/6,D=0,Ã=B̃=1/2,C̃=1/6,D̃=0` | 路线一无删行实验 | **路线二独有**。本轮独立顶点枚举复现了两个最小值与该见证点，逐位一致 `[VERIFIED-LP]` |
| §4.6 monotonicity 的三重作用 | `rem:app-census`（"`cons(t,i)` uses the greedy choice and both bands through `lem:coherence`, and monotonicity in cases (a) and (c)"）、`lem:app-pred` case (c)、`lem:app-mono` case (c) | 结论相容但角度不同：路线一按 reduced LP 的 case 分类记账，路线二按"band 是否非空"作 soundness 论证。路线二的论证无 oracle，标 `[HAND-PROOF-UNREVIEWED]`，本轮也只做手工核对（`d<0` 且 `eta>1` 时 `eta_o d < d/eta_u`，正确） |
| §5 submodularity 对 (i)(ii) 空洞（删行后 `min` 仍为 0；删掉后 `min(B-C)=-1/2`） | `app:coherence` 的证明确实一次也没用 submodularity；`rem:app-census` 的记账与此一致 | **对应**（路线一以"证明里没出现"隐含，路线二以删行 LP 显式确认）。本轮独立复现 `min(B-C)=-1/2`（见证点 `A=B=0, C=D=1/2`）`[VERIFIED-LP]` |
| §6.1 `K=3, eta=3/2` 的 weighted coverage 走查 | 路线一无数值走查（`app:coherence` 明写 "No script checks the computations of this proof"） | 路线二独有。本轮独立重跑：band `(1,3/2)` 对全部 single-element 增益成立，run 选 `a,c,b`，`f(S^3)=17=F^OPT`，6 个 `(t,e,e')` 配对 × 7 项检查全过 `[VERIFIED-EXHAUSTIVE]` |
| §6.2 `K=2` 取等实例 | 路线一无对应条目 | 路线二独有，本轮逐位复算通过 `[VERIFIED-EXHAUSTIVE]` |
| §6.3 9 组 `(eta_u,eta_o)` split 的有理顶点枚举 | 路线一无 LP | 路线二独有。本轮用独立实现的 `Fraction` 高斯消元顶点枚举复算，9 组全部得 `min(eta D-C)=0`、`min((1-1/eta)C-(B-A))=0` `[VERIFIED-LP]` |

### 1.2 路线一中路线二未覆盖的内容

| 路线一的步骤 | 路线二的状态 |
|---|---|
| **sharp form 本体**：`sec:coherence` 的 `d - g/eta >= (1-1/eta)(g-h) >= 0`，第一个不等号是 (ii) 的等价改写 `[VERIFIED-SYMBOLIC, H_J3_gate_check.py item 1]`，第二个用 `f` 的 submodularity 加 `eta>=1` | **路线二未覆盖**（GAP-1，自报）。路线二第 4 节的 (S1)-(S4) 是自行重构的另一组命题。**不矛盾**：路线二的材料一行即给出路线一的 sharp form，第一个不等号就是路线二 Step 5 的恒等式（本轮 `[VERIFIED-SYMBOLIC]`：`(d-g/eta)-(1-1/eta)(g-h)` 与 `(1-1/eta)h-(g-d)` 之差恒为零），第二个不等号就是路线二 §5 里"只有 `C<=B` 需要 submodularity"那一条 |
| **sharp form 的刚性推论**：`eta>1` 且 `d=g/eta` 时必有 `h=g`（"a maximally wrong selection cannot also erode that candidate's future gain"） | **路线二未覆盖**。路线二的 (S4) 刻画的是 (i)(ii) 的取等（cons 松弛为零），与此处的 pred 取等是两件事。本轮在同一多面体上独立核验：`(eta_u,eta_o)=(1,3/2)` 与 `(2,1)` 下附加 `A=B/eta` 后 `B-C` 的取值范围塌缩为 `[0,0]`；`eta=1` 时范围是 `[0,1/2]`，故路线一的 `eta>1` 限定词**不空洞** `[VERIFIED-LP]` |
| `e != e'` 写在引理前提里（`app:coherence` 首句 "Let `S subseteq N` and `e,e' notin S` with `e != e'`"），并在 `lem:app-cons` case (c) 注明 "`lem:coherence`, which requires `e != e'`, is not invoked in this case, which is what closes the gap this subsection exists to close" | 路线二把 `e != e'` 作为"非实质的小规格补充"自行补上。**结论一致**。差异的来源是输入包：`results/V11/inputs/statement_coherence.md` 与 `results.tex` 的引理陈述都没有 `e != e'`，只有附录有 |
| `rem:app-rulers`：`cons` 族（即本引理）用到离轨状态的 band，因此**不能**换成 `etatr` 或 `etasel`；台账 T5 的 must-not-claim 同此 | 路线二未复述该禁令，但结构上相容：它明确记录 Step 4 用的是 `(S+e', e)` 与 `(S+e, e')` 两条 band 实例，并在 §7 声明未使用 `eta^sel`、`eta^path` |
| 引理在上层的用途：它是 reduced LP 的 `cons(t,i)` 约束族（`lem:app-cons`），以及 `thm:exact` 的出发点（`app:exact` 的 roadmap） | 路线二未覆盖（盲证，输入包不含上层定理）。其 §1.3 把 `K`、`n` 判为对本引理空洞，与路线一一致（引理陈述里确实不出现 `K`、`n`） |
| `app:coherence` 的状态注释 "Status: `[HAND-PROOF-UNREVIEWED]`; four lines, single-element bounds only" 与 "No script checks the computations of this proof" | 路线二给出的 oracle 覆盖**严格更多**（符号 + 顶点枚举 LP + 穷举实例）。注意路线一内部有一处不一致：`app:coherence` 说没有脚本查这条证明，但 `lem:app-cons` 的同一条 slack 恒等式在 `J2_core_oracles.py` 与 `H3_j2_recheck.py` 里确实被符号验证过。这是路线一的注释滞后，不是数学错误 |

---

## 2. 判定

### (1) 结论与量词

**引理本体的结论完全一致，推导是同一条路线。** 两条路线都给出：对任意 `f: 2^N -> R_{>=0}` monotone 且 `f(∅)=0`、任意集合函数 `f̃` 且满足 Definition 1 的 band `(eta_u, eta_o)`、任意 `S subseteq N`、任意 `e != e'` 在 `N \ S` 中、在假设 `d̃_e(S) >= d̃_{e'}(S)` 下，

```
(i)  d_e(S+e') >= (1/eta) d_{e'}(S+e),
(ii) (1-1/eta) d_{e'}(S+e) >= d_{e'}(S) - d_e(S),      eta = eta_u eta_o.
```

两条路线用的都是"把 `f̃(S+e+e')-f̃(S)` 按两种次序展开 + 两端各用一次 band"，连 band 实例的位置都相同。路线二的 Step 1 至 Step 5 与路线一 `app:coherence` 的三段一一对应。

量词的差异（详见第 3 节）：

- `e != e'`：路线一的附录**有**，路线一的引理陈述（`results.tex`）**没有**，路线二把它作为补充约定加上。三者的真值相同（`e=e'` 时两式读作 `0>=0`），不构成分歧，但它说明引理陈述本身缺一个限定词。
- `eta_u, eta_o` 的域：路线一引用 Definition 1 的逐字版（`eta_u, eta_o >= 1`）；路线二在 convention B（`eta_u, eta_o > 0`，`eta >= 1`）下推导，并在 LP 里同时测了 `eta_o < 1` 与 `eta_u < 1` 的 split。路线二的域**严格更宽**且推导在更宽的域上仍然成立（链条只用到 `eta_u > 0`、`eta_o > 0`），本轮在 `(3/4,2)` 与 `(2,3/4)` 上复算确认。
- **sharp form 的量词完全不同**：路线一的 sharp form 是一条 `forall` 链（多一个 submodularity 前提，不含任何 `exists`）；路线二的 (S2) 含一条 `forall eta >= 1, forall c in (0,eta], exists 实例` 的 tightness 量词，路线一全文没有这个 `exists`。反过来，路线一 sharp form 的刚性推论（`eta > 1` 且 `d = g/eta` ⇒ `h = g`）在路线二里没有对应命题。

因此 **quantifier_match = false**：不是因为矛盾，而是因为 criterion B 覆盖的 sharp form 在两条路线里是两个不同的命题。

### (2) 路线二是否依赖额外假设、是否有缺口或错误

- **额外假设**：一处，且是路线二自报的 `[ADDED-ASSUMPTION]`：sharp form 的陈述由它自行重构（§4.0、GAP-1）。理由是输入包 `results/V11/inputs/statement_coherence.md` 只含引理本体，TASKS11 Q5b 的 sharp form 正式文本不在允许打开的四个文件里。路线二没有为闭合引理本体而引入任何未声明的前提。
- **缺口**：见第 4 节，两条实质缺口（sharp form 未按原文、路线一 sharp form 的刚性推论未覆盖）加两条形式缺口。
- **错误**：**未发现**。本轮把路线二全部可判定的计算独立重做了一遍，逐项一致：
  - 四条恒等式 (3.1)(3.2)(3.5)(3.8) `[VERIFIED-SYMBOLIC]`；
  - 9 组 split 的 `min(eta D - C) = 0` 与 `min((1-1/eta)C-(B-A)) = 0`，独立实现的有理顶点枚举 `[VERIFIED-LP]`；
  - 删掉 submodularity 后两个 min 仍为 0、`min(B-C) = -1/2`（见证点 `A=B=0, C=D=1/2`）、`min((1-1/eta)B-(B-A))` 仍为 0 `[VERIFIED-LP]`；
  - 删掉 `f̃` 交换恒等式后 `min(eta D-C) = -1/6`、`min((1-1/eta)C-(B-A)) = -1/9`，见证点与路线二给出的 `A=1/3, B=1/2, C=1/6, D=0, Ã=B̃=1/2, C̃=1/6, D̃=0` 逐位相同 `[VERIFIED-LP]`；
  - 4.3 的取等族在 `eta in {1,3/2,2,5/2,3,7/3}` × `c in {1/2,1,3/2,eta}` 共 23 组上，交换恒等式、monotone、submodular（`c<eta` 时严格）、四条 band、平手假设、(i)(ii) 同时取等、三项松弛全零，逐条通过 `[VERIFIED-EXHAUSTIVE]`；
  - 6.2 的 `K=2` 实例 `A,B,C,D = 1, 4/3, 1, 2/3`、`Ã,B̃,C̃,D̃ = 3/2, 3/2, 1, 1`，严格 submodular，(i)(ii) 同时取等，三项松弛全零 `[VERIFIED-EXHAUSTIVE]`；
  - 6.1 的 `K=3` coverage 走查：`(eta_u,eta_o)=(1,3/2)` 对全部 single-element 增益成立，run 为 `a, c, b`，`f(S^3)=17=F^OPT_3`，`t=0` 的 `A,B,C,D = 6,7,5,4`、`Ã,B̃,C̃,D̃ = 9,8,5,6`，松弛 `1` 全部来自 `Ã-B̃`，6 个配对 × 7 项全过 `[VERIFIED-EXHAUSTIVE]`。
  - 一处措辞不精确（不是错误，也不在交付文件里）：上游 blind agent summary 写"对每个 `eta>=1` 和每个 `c in (0,eta]` 有一族**严格** submodular 的取等实例"，而 `c=eta` 时该族只是 submodular 不严格。路线二的报告 §4.3 第 3 条写的是"`c<eta` 时严格"，是对的。

### (3) 路线一是否有被路线二反驳的步骤

**没有。** 路线一 `app:coherence` 的每一步都在路线二里有逐字同构的对应，路线一的 sharp form 两个不等号本轮都独立验证成立（第一个是恒等改写 `[VERIFIED-SYMBOLIC]`，第二个在同一多面体上 `min(B-C)=0` `[VERIFIED-LP]`），刚性推论的 `eta>1` 限定词也不空洞 `[VERIFIED-LP]`。路线二唯一"更强"的地方（Step 5 把单向代入升级为等价、Step 4 的链只需 `eta_u, eta_o > 0`）是补强而不是反驳。

### 结论

**verdict = B-GAP（route two incomplete）。** 引理本体：路线二与路线一同结论、同路线、无错误，且 oracle 覆盖严格更多。扣在 sharp form：criterion B 的判定对象包含 sharp form，而路线二在未见到原文的情况下重构了一组不同的命题，既没有产出路线一的 sharp form 链 `d - g/eta >= (1-1/eta)(g-h) >= 0`，也没有产出它的刚性推论。这是输入包缺失导致的缺口，不是数学分歧；补法见第 4 节 GAP-A 的一行推导。

---

## 3. 分歧清单（exact list of divergences）

| 编号 | 分歧 | 性质 |
|---|---|---|
| D1 | **sharp form 是两个不同的命题**。路线一：`d - g/eta >= (1-1/eta)(g-h) >= 0`（`d=A, g=B, h=C`），第一个不等号是 (ii) 的恒等改写，第二个用 submodularity 加 `eta>=1`，推论是 `eta>1` 且 `d=g/eta` ⇒ `h=g`。路线二：自行重构的 (S1) order transfer、(S2) 常数 `1/eta` 不可改进、(S3) min 形式、(S4) 取等刻画 | 实质分歧（来源：输入包缺 Q5b 文本）。不矛盾：两组命题本轮都验证成立 |
| D2 | **量词 `exists`**。路线二 (S2) 含 `forall eta>=1, forall c in (0,eta], exists 取等实例`；路线一全文对本引理没有任何 tightness 的 `exists` 断言 | 路线二独有的加强 |
| D3 | **刚性推论缺失**。路线一的 "`eta>1` 且 `d=g/eta` ⇒ `h=g`" 在路线二里无对应；路线二的 (S4) 刻画的是另一个取等（cons 松弛为零） | 路线二未覆盖，可一行补上 |
| D4 | **`e != e'` 的位置**。路线一附录写在前提里，路线一引理陈述（`results.tex` 第 138 行）与盲审输入 `statement_coherence.md` 都没有；路线二把它作为补充约定 | 非实质（`e=e'` 时两式读作 `0>=0`），但暴露引理**陈述**缺一个限定词，建议回写正文 |
| D5 | **`eta_u, eta_o` 的域**。路线一用逐字 Definition 1（两因子 `>=1`）；路线二用 convention B（两因子 `>0`）并在 `(3/4,2)`、`(2,3/4)` 上验证 | 路线二严格更宽且成立；与 `HANDOFF` 已确立的 convention B 一致 |
| D6 | **(i) 与 (ii) 的关系**。路线一：由 (i) 代入得 (ii)（单向）；路线二：`(1-1/eta)C-(B-A) = D-C/eta` 是恒等式，故双向等价、同时取等 | 路线二更强，`[VERIFIED-SYMBOLIC]`，不与路线一冲突 |
| D7 | **Step 6 / `pred` 族的地位**。路线二把 `B <= eta A` 当作"供比较用的平行推论"；路线一把同一条式子独立成 reduced LP 的 `pred(t,i)` 约束族（`lem:app-pred`），并配同一形式的三项 slack 分解 | 路线二低估了这一步在上层的作用（盲证不知上层定理） |
| D8 | **oracle 状态标签**。路线一 `app:coherence` 标 `[HAND-PROOF-UNREVIEWED]` 且写"No script checks the computations of this proof"；路线二给出 `[VERIFIED-SYMBOLIC]` + `[VERIFIED-LP]` + `[VERIFIED-EXHAUSTIVE]` | 建议把 T5 卡与 `app:coherence` 的注释升级，并顺带修正路线一内部的注释滞后（`lem:app-cons` 的同一恒等式已被 `J2_core_oracles.py` 与 `H3_j2_recheck.py` 符号验证） |
| D9 | **submodularity 的记账方式**。路线一把 `C<=B` 用在 sharp form 的右端非负（并在 `lem:app-mono` 里作为独立约束族）；路线二把它用于判定 `min{C,B}` 取在哪一支 | 同一数学事实的两种打包，结论一致（两条路线都认定 (i)(ii) 本身不需要 submodularity） |
| D10 | **`f̃` 交换恒等式的必需性**。路线二用删行 LP 给出反例（`min` 变负，附有理见证点）证明这条不可删；路线一只说"This uses nothing but the definition of a set function"，未讨论必需性 | 路线二独有，本轮复现 |

---

## 4. 路线二的缺口清单（route-two gaps）

| 编号 | 缺口 | 状态 | 补法 |
|---|---|---|---|
| GAP-A | **未产出路线一的 sharp form**：`d - g/eta >= (1-1/eta)(g-h) >= 0`。路线二 §4 的 (S1)-(S4) 是重构版，自标 `[ADDED-ASSUMPTION]`（其 GAP-1） | 未闭合，但可一行闭合 | 第一个不等号 = 路线二 Step 5 的恒等式（`(d-g/eta)-(1-1/eta)(g-h)` 与 (ii) 的松弛量恒等，本轮 `[VERIFIED-SYMBOLIC]`）；第二个不等号 = 路线二 §5 里"`C<=B` 是唯一需要 submodularity 的一条"加 `eta>=1`。两块材料路线二都有，只是没有组装 |
| GAP-B | **未产出刚性推论** `eta>1` 且 `d=g/eta` ⇒ `h=g` | 未闭合 | 由 (ii) 代入 `A=B/eta` 得 `(1-1/eta)C >= (1-1/eta)B`，`eta>1` 除掉因子得 `C>=B`，配 submodularity 的 `C<=B` 得 `C=B`。本轮在同一多面体上 `[VERIFIED-LP]` 确认取值范围塌缩为单点，且 `eta=1` 时不成立 |
| GAP-C | **sharp form 原文缺失**（路线二的 GAP-1，输入包问题）。`results/V11/inputs/statement_coherence.md` 只含引理本体，TASKS11 Q5b 的文本与 `sec:coherence` 的 sharp form 段落都不在允许打开的四个文件里 | 输入缺口，非路线二的过错 | 若要重跑盲审，输入包需补 `sec:coherence` 第 153 至 167 行的 sharp form 段落（但补了就不再是对该段的盲证） |
| GAP-D | **ProbeLottery 的 `K=2` 走查 `[FAILED]`**（路线二的 GAP-2）。`statement_probelottery.md` 确实在 `results/V11/inputs/` 里存在，但不在本统计的四个允许输入之列 | 与 lem:coherence 的数学内容无关 | 本判定不因此扣分；路线二已明确声明其 §6.2 的 `K=2` 实例**不是** ProbeLottery 实例，这个声明是必要且正确的 |
| GAP-E | **§4.6 monotonicity 三重作用的定性说明**无 oracle，路线二自标 `[HAND-PROOF-UNREVIEWED]` | 保持该标签 | 其中第 1 条（`d<0` 且 `eta>1` 时 band 两端次序颠倒）本轮手工核对正确：`eta_o d < d/eta_u` 等价于 `eta_u eta_o > 1`。第 2、3 条是措辞层面的，无可判定内容 |
| GAP-F | **未覆盖引理在上层的用途与 must-not-claim**：`cons(t,i)` 约束族、`thm:exact` 的出发点、台账 T5 的"禁止对 `eta^sel` / `eta^tr` 声称本引理" | 盲证的必然结果 | 回写正文时须保留 T5 的禁令。路线二的推导结构与该禁令相容（它用了 `(S+e', e)` 上的 band，那是离轨状态） |

---

## 5. 状态标签汇总（本轮独立复算）

| 命题 | 本轮状态 |
|---|---|
| 路线二 (3.1)(3.2)(3.5)(3.8) 四条恒等式 | `[VERIFIED-SYMBOLIC]`（judge_coherence.py Part A） |
| 路线一 `lem:app-cons` / `lem:app-pred` 两条 slack 恒等式 | `[VERIFIED-SYMBOLIC]`（同上；与路线二 (3.8)、Step 6 相差整体因子 `eta_o`） |
| 路线一 sharp form 第一个不等号 = (ii) 的恒等改写 | `[VERIFIED-SYMBOLIC]` |
| (i) 与 (ii) 在 9 组 `(eta_u,eta_o)` split 上 `min = 0` | `[VERIFIED-LP]`（有理顶点枚举，`binom(15,5)=3003` 基） |
| 删 submodularity：两个 `min` 仍为 0；`min(B-C)=-1/2`；`min((1-1/eta)B-(B-A))=0` | `[VERIFIED-LP]` |
| 删 `f̃` 交换恒等式：`min(eta D-C)=-1/6`、`min((1-1/eta)C-(B-A))=-1/9`，见证点复现 | `[VERIFIED-LP]` |
| 路线二 4.3 取等族（23 组 `(eta,c)`） | `[VERIFIED-EXHAUSTIVE]` |
| 路线二 6.1 `K=3` coverage 走查（6 配对 × 7 项） | `[VERIFIED-EXHAUSTIVE]` |
| 路线二 6.2 `K=2` 取等实例 | `[VERIFIED-EXHAUSTIVE]` |
| 路线一刚性推论 `eta>1` 且 `d=g/eta` ⇒ `h=g`；`eta=1` 时失效 | `[VERIFIED-LP]`（附加等式后 `B-C` 范围塌缩为 `[0,0]`；`eta=1` 时为 `[0,1/2]`） |
| 路线二 §4.6 monotonicity 的定性说明 | `[HAND-PROOF-UNREVIEWED]`（保持路线二的标签） |
| 路线二重构的 sharp form 陈述本身 | `[ADDED-ASSUMPTION]`（GAP-A / GAP-C） |
| ProbeLottery 的 `K=2` 走查 | `[FAILED]`（GAP-D，与本引理无关） |

---

## 6. 建议回写正文的三条（供 Q10 采纳，本文件不改任何既有文件）

1. `results.tex` 第 138 行的引理陈述补 `e \ne e'`，与 `app:coherence` 首句对齐。
2. `app:coherence` 的 "No script checks the computations of this proof" 需要更新：同一条 slack 恒等式在 `J2_core_oracles.py`、`H3_j2_recheck.py`、`H_J3_gate_check.py` 里已有符号验证；若采纳路线二的顶点枚举，可把 T5 卡的 (i)(ii) 升级为 `[VERIFIED-LP]` 并注明常数 `1/eta` 不可改进（路线二 4.3 的显式族）。
3. 在引理下补一句脚注（路线二 §5 的建议，与路线一 `rem:app-census` 的记账一致）："(i)(ii) 只用到 monotonicity 与 Definition 1 的 band；submodularity 只用于把 sharp form 的第二个不等号钉到非负（即 `d_{e'}(S+e) <= d_{e'}(S)`）。"
