# 量词审计（criteria A 与 E）：prop:guarantee / 台账 T3（TASKS11 Q5a）

本文件只做两件事：A 项逐量词比对正文环境与台账卡，E 项建立量词审计表并把每个量词落到路线一证明的具体位置。
不修改任何已有文件，不运行 git。本文件自带的算术用 fractions.Fraction 与 sympy，浮点只出现在打印里。
状态标签按 CLAUDE.md：[VERIFIED-SYMBOLIC] [VERIFIED-LP] [VERIFIED-EXHAUSTIVE] [HAND-PROOF-UNREVIEWED] [CONJECTURE] [FAILED]。

路线一材料：`paper/sections/appendix_proofs.tex` 的 subsection `app:guarantee`（第 215 至 336 行），
四个 paragraph 标签依次为 Step 1（第 226 行）、Step 2（第 251 行）、Step 3（第 273 行）、Step 4（第 285 行），
其后是 `rem:app-product`（第 310 至 329 行）与收尾句（第 331 至 336 行）。下文简称 Step 1..Step 4。

读过的文件见 §7。

---

## 1. Criterion A：正文陈述与台账陈述的逐量词比对

### 1.1 两段原文

正文（`paper/sections/results.tex` 第 79 至 91 行，environment `proposition`，label `prop:guarantee`；
与 `results/V11/statements.md` 第 131 至 145 行、`results/V11/inputs/statement_guarantee.md` 第 6 至 18 行三处逐字一致，本项无 convention 改写版）：

```latex
\begin{proposition}[Guarantee of predictive greedy]\label{prop:guarantee}
Let $f$ be monotone submodular with $f(\emptyset)=0$ and let $T=S^{K}$ be the
output of a run of predictive greedy whose selection error is $\etasel$
(Definition~\ref{def:etasel}, with $L_K(\infty)=0$).
Then, with $L_K(x)=1-(1-\tfrac1{xK})^{K}$,
\[
  f(T)\;\ge\;L_K(\etasel)\,f(O^{\ast})
  \;\ge\;\bigl(1-e^{-1/\etasel}\bigr)f(O^{\ast}).
\]
If moreover the predictor has finite error $(\eta_u,\eta_o)$, the same bound
holds with $\etasel$ replaced by $\etatr$ or by $\eta$, and the three bounds
are ordered $L_K(\etasel)\ge L_K(\etatr)\ge L_K(\eta)$.
\end{proposition}
```

台账（`THEOREM_LEDGER.md` 第 69 至 75 行，卡 `## T3 prop:guarantee`，陈述字段在第 70 行）：

> 陈述（K1 后）：f 单调 submodular；run 的选择误差 η^sel（新定义：a_t=M_t/g_t，M_t=g_t=0 取 1，g_t=0<M_t 取 ∞，η^sel=max{1,a_t}，L_K(∞)=0）。则 f(T) ≥ L_K(η^sel) f(O\*) ≥ (1−e^{−1/η^sel}) f(O\*)，L_K(x)=1−(1−1/(xK))^K。同一界对 η^tr、η 成立。

台账卡的其余字段（归属 GS 2007 Theorem 1、状态、禁止声称、附属 remark）不属于陈述字段，不计入 A 比对，只在 §5 记录。

### 1.2 逐项对照

| 量词 / 形容词 | 正文 | 台账 | 判定 |
|---|---|---|---|
| f monotone | 有，"Let $f$ be monotone submodular" | 有，"f 单调 submodular" | 一致 |
| f submodular | 有 | 有 | 一致 |
| f 的 normalization f(∅)=0 | 有，"with $f(\emptyset)=0$" | 无 | **差异 D1** |
| 输出 T 的定义 T=S^K（固定 K 步） | 有，"let $T=S^{K}$ be the output of a run" | 只写 f(T)，未定义 T，也未写固定 K 步 | **差异 D2** |
| 对 run 的全称（任意 tie-break） | 有，"a run of predictive greedy"（不定冠词，任意一次执行） | 有，"run 的选择误差 η^sel" | 一致 |
| η^sel 的定义 | 引用 Definition~\ref{def:etasel}，不展开 | 展开：a_t=M_t/g_t，M_t=g_t=0 取 1，g_t=0<M_t 取 ∞，η^sel=max{1,a_t} | 一致（同一定义，展开与引用之别；与 `model.tex` 第 84 至 116 行逐项相符） |
| 约定 L_K(∞)=0 | 有，写在括号里 | 有，写在定义括号里 | 一致 |
| L_K 的表达式 | 有，"$L_K(x)=1-(1-\tfrac1{xK})^{K}$" | 有，同式 | 一致 |
| 主结论 f(T) ≥ L_K(η^sel) f(O\*) | 有 | 有 | 一致 |
| 第二不等式 ≥ (1−e^{−1/η^sel}) f(O\*) | 有 | 有 | 一致 |
| η^tr / η 条款的前提 "finite error (η_u,η_o)" | 有，"If moreover the predictor has finite error $(\eta_u,\eta_o)$" | 无前提，直接写"同一界对 η^tr、η 成立" | **差异 D3** |
| 三界排序 L_K(η^sel) ≥ L_K(η^tr) ≥ L_K(η) | 有，作为结论的一部分 | 无 | **差异 D4** |
| 误差的拆分 (η_u,η_o) 与乘积 η | 只在最后一句出现，作为前提的载体 | 只出现 η、η^tr，不出现 (η_u,η_o) | 见 D3 |
| K 的定义域 | 未写（继承 `model.tex` 第 15 行 1 ≤ K ≤ n、K ≥ 1） | 未写 | 一致（共同省略，见 §3 的 E 表第 14、15 行） |
| n 的定义域 | 未写 | 未写 | 一致（本陈述不需要 n 条件） |
| OPT > 0 | 未写 | 未写 | 一致（共同省略，见 §3 GAP-3） |
| O\* 的定义（最优 K-set） | 未写，直接用 f(O\*) | 未写，直接用 f(O\*) | 一致（共同省略，定义只在 `notation_table.tex` 第 25 行） |
| deterministic / randomized | 无（本陈述不量化算法类） | 无 | 一致 |
| arbitrary query access、at most nK queries、\|S\| ≤ K | 无 | 无 | 一致（本陈述无查询量词） |
| adversarial ties | 无（对任意 run 成立） | 无 | 一致 |
| expectation / fixed random string | 无（无随机条款） | 无 | 一致 |
| error "exactly" 还是 "at most" | 写 "finite error $(\eta_u,\eta_o)$"，而 `def:eta` 的措辞是 "error at most $(\eta_u,\eta_o)$" | 不出现 (η_u,η_o) | 记为 N1（措辞，不改真值，见 §5） |

### 1.3 A_diffs（四条）

- **D1**：正文把 normalization `$f(\emptyset)=0$` 写进陈述，台账陈述字段只写"f 单调 submodular"。这不是冗余：路线一 Step 3 的第一步就是 r_0 = f(O\*)，用到 f(S^0)=f(∅)=0（见 §3 GAP-1）。保守处理：建议台账陈述字段补 f(∅)=0（只动台账，不动正文）。
- **D2**：正文写 `$T=S^{K}$ be the output of a run`，把"跑满 K 步"的语义绑进 T 的定义；台账只写 f(T)，T 无定义。台账卡的"禁止声称"字段里写了早停变体不适用本命题，但那是禁令，不是陈述里的量词。按逐字比对口径两边的陈述文本不重合。
- **D3**：正文的 η^tr / η 条款带前提 "If moreover the predictor has finite error $(\eta_u,\eta_o)$"；台账写成无前提的"同一界对 η^tr、η 成立"。这是四条里唯一影响作用范围的差异：路线一 Step 4 的最后一句明写 "this is where the finiteness hypothesis of the last sentence of the Proposition is used"，而 `model.tex` 第 120 至 126 行的注释记录了没有有限 band 时链 η^sel ≤ η^tr ≤ η 可以失效（J2 §4）。按台账的字面读法会把一条有前提的结论读成无前提的。
- **D4**：正文把三界排序 L_K(η^sel) ≥ L_K(η^tr) ≥ L_K(η) 写进结论；台账陈述字段没有排序句。排序由 L_K 的单调性得到（Step 4 末段；本文件 §4 已符号核过），台账因此比正文弱一句。

**A_match = false**（两份清单不重合）。四条差异中 D1、D2、D4 是台账压缩导致的省略，不改变命题真值；D3 是作用范围差异，按"最坏读法"会让台账版的最后一句越界，是四条里唯一需要改台账的。

---

## 2. Criterion E：量词审计表

表内"处理位置"一律给 file + 段落标签或可检索的原文片段。状态取值：覆盖（路线一有明写的一句）、隐式（路线一用到但没有一句建立或点名）、不需要（本证明不用这个条件）、不适用（陈述里没有这个量词）、GAP。

| 量词 / 形容词 | 处理位置（file + 段落） | 状态 |
|---|---|---|
| f monotone | `appendix_proofs.tex` app:guarantee Step 1 "Monotonicity gives $f(O^{\ast}\cup S^{t})\ge f(O^{\ast})$"；Step 2 "Monotonicity of $f$ makes $g_t=d_{e_t}(S^{t})\ge0$ always" | 覆盖 |
| f submodular | Step 1 telescope 后 "one application of submodularity per term" | 覆盖 |
| f 的 normalization f(∅)=0 | Step 3 首句 "With $r_0=f(O^{\ast})$"（由 r_t=f(O\*)−f(S^t) 与 S^0=∅ 得到，需 f(∅)=0，未点名） | GAP-1（隐式） |
| f 非负（值域 R_{≥0}） | 本证明不使用；`model.tex` 第 9 至 10 行 | 不需要 |
| T=S^K，run 固定执行 K 步 | app:guarantee 前言 "Let $S^{0}=\emptyset,S^{1},\dots,S^{K}$ be the states of a run of predictive greedy"；Step 3 "iterating $K$ times"；`model.tex` 第 71 至 72 行 "The run always executes exactly $K$ steps" | 覆盖 |
| 对任意一次 run 全称（含任意 tie-break / adversarial ties） | 前言的 "a run of predictive greedy"；tie 规则本身在 `model.tex` 第 70 至 71 行，Step 1 至 Step 4 均不使用 | 覆盖（本命题不需要 tie 假设） |
| 早停变体被排除 | `model.tex` 第 73 至 76 行；`appendix_proofs.tex` `rem:app-product`（第 319 至 322 行）"For a run stopped after $K^{*}<K$ steps ... no $L_K$ bound follows" | 覆盖 |
| \|O\*\| ≤ K（计数 m ≤ K） | Step 1 "$m\le|O^{\ast}|\le K$" 与 "This is the only place where the count $m\le K$ enters" | 覆盖 |
| O\* 是最优 K-set（记号定义） | `notation_table.tex` 第 25 行 "an optimal $K$-set"；`prop:guarantee` 与 app:guarantee 都未引入该记号 | 隐式 |
| r_t ≥ 0（即 f(S^t) ≤ f(O\*)，需 \|S^t\|=t ≤ K 且 O\* 在 \|S\| ≤ K 内最优） | Step 2 benign 分支 "reads $r_t\le0$: the run has already reached the optimal value, and $r_s=0$ for every $s\ge t$" 用到，app:guarantee 无一句建立 | GAP-2（隐式） |
| η^sel 的主分支 a_t=M_t/g_t（g_t>0） | Step 1 "Definition~\ref{def:etasel} gives $M_t=\max_{e\notin S^{t}}d_e(S^{t})=a_tg_t\le\etasel\,d_{e_t}(S^{t})$" | 覆盖 |
| η^sel 的分支 a_t=1（M_t=g_t=0，benign zero step） | Step 2 "If the step is benign ($M_t=0$), the covering inequality ... reads $r_t\le0$" | 覆盖 |
| η^sel 的分支 a_t=∞（g_t=0<M_t，harmful zero step）与约定 L_K(∞)=0 | Step 2 "then $a_t=\infty$, so $\etasel=\infty$, $L_K(\infty)=0$, and the claimed bound is the trivial one; nothing needs proving" | 覆盖 |
| η^sel 有限（Step 1 收缩式的前提） | Step 1 "whenever $\etasel$ is finite (Step 2 handles the zero steps)"；Step 2 末 "Therefore, when $\etasel$ is finite, the contraction of Step 1 may be applied at every step" | 覆盖 |
| η^sel ≥ 1 与 K ≥ 1（收缩因子 1−1/(η^sel K) ∈ [0,1)） | Step 3 "Since $\etasel\ge1$ and $K\ge1$, the quantity $u=1/(\etasel K)$ lies in $(0,1]$" | 覆盖 |
| K ≥ 2 | 本命题不需要；Step 3 只要 K ≥ 1。K=1 时 L_1(x)=1/x（本文件 §4，[VERIFIED-SYMBOLIC]） | 不需要 |
| 第二不等式 L_K(η^sel) ≥ 1−e^{−1/η^sel} | Step 3 "$1-u\le e^{-u}$ gives $L_K(\etasel)\ge1-e^{-1/\etasel}$" | 覆盖 |
| 最后一句的前提 "finite error (η_u,η_o)" | Step 4 末 "this is where the finiteness hypothesis of the last sentence of the Proposition is used" | 覆盖 |
| 拆分 (η_u,η_o) 与乘积 η 的关系 | Step 4 的三段式 "$\le\eta_u\max_{e\notin S^{t}}\tilde d_{e}(S^{t})=\eta_u\,\tilde d_{e_t}(S^{t})\le\eta_u\eta_o\,d_{e_t}(S^{t})$"，随后 "$a_t\le\eta_u\eta_o$ when the band is the global one"；class 层面的缩放不变另见 `model.tex` `lem:scaling`（第 44 至 54 行） | 覆盖 |
| η^tr 的定义 | `model.tex` 第 117 至 119 行的散文句（无编号 definition）；Step 4 以 "when it is restricted to the states of the run" 使用 | GAP-4（只有散文定义） |
| 链 η^sel ≤ η^tr ≤ η | Step 4 "Taking the maximum over the steps gives $\etasel\le\etatr\le\eta$ for every predictor with finite error ($\etatr\le\eta$ because the states of the run are a subset of all sets)" | 覆盖 |
| 三界排序所需的 L_K 单调性 | Step 4 末 "The map $x\mapsto1-\tfrac{1}{xK}$ is increasing on $x\ge1$ with values in $[0,1)$, so ... $L_K$ is decreasing" | 覆盖（本文件 §4 [VERIFIED-SYMBOLIC]） |
| g_t=0 时 band 强制 M_t=0（链在零步上的闭合） | Step 4 "at a step with $g_t=0$ the same display forces $M_t=0$, so $a_t=1$" | 覆盖 |
| OPT > 0（f(O\*) > 0） | app:guarantee 全篇不讨论；`model.tex` 第 15 至 16 行的约定写的是 "every ratio statement"，而本命题是乘积形不等式，该约定字面不覆盖 | GAP-3 |
| ground set 大小 n | 本证明不需要任何 n 条件；1 ≤ K ≤ n 在 `model.tex` 第 15 行，用于保证存在 K-set | 不需要 |
| f̃ 的 normalization f̃(∅)=0 与结构假设 | 本证明不使用（η^sel 只由真 gain 定义；Step 4 只用 band 的两侧） | 不需要 |
| deterministic / randomized | 陈述不量化算法类 | 不适用 |
| fixed random string / expectation over what | 陈述无随机条款，无期望 | 不适用 |
| arbitrary query access、at most nK queries、\|S\| ≤ K | 陈述无查询量词；仓库版 `model.tex` 也没有查询预算段落（该段只在 HANDOFF 的 Model 草稿里，未入库），证明不使用 | 不适用 |
| error "exactly" 还是 "at most" | `def:eta`（`model.tex` 第 23 至 32 行）的措辞是 "error at most $(\eta_u,\eta_o)$"；Step 4 按 at most 使用（两侧都是不等号） | 覆盖（正文陈述的 "finite error" 措辞见 §5 N1） |

### 2.1 模板附带问题（本项不适用，逐条记录理由）

- "thm:ceiling 的 fixed random string 量词是否在陈述里"：本项是 prop:guarantee，陈述无随机段落，问题不适用。该问题属 Q3，已在 `results/V11/audit/ceiling.md` §3 回答，本文件不重复也不复制其结论。
- "thm:linear-exact 的 n ≥ 4K^5 能否紧到约 K^3(K−1)^2/2 + K^2"：本项与 `app:greedybudget` 无引用关系（`app:guarantee` 不出现 n 的门槛），不适用。本文件不对该 counting chain 作任何判断，以免与负责该项的审计重复或冲突。

---

## 3. GAP 清单

四条，按保守口径列出。判定标准：路线一 app:guarantee 里没有一句建立或点名该条件，即使它在别处可补。四条都不动摇结论，都是"补一句话"的量级，均不需要改正文陈述。

- **GAP-1（轻）normalization f(∅)=0**。Step 3 直接写 "With $r_0=f(O^{\ast})$"。由前言的 S^0=∅ 与 r_t=f(O\*)−f(S^t) 得 r_0=f(O\*)−f(∅)，等号成立需要 f(∅)=0。正文陈述里有这个假设（A 项 D1），路线一没点名它被用在哪。建议：Step 3 首句改写成"with $f(\emptyset)=0$ the residual starts at $r_0=f(O^{\ast})$"。状态 [HAND-PROOF-UNREVIEWED]，不影响真值。
- **GAP-2（轻）r_t ≥ 0**。Step 2 的 benign 分支从 r_t ≤ 0 断定"the run has already reached the optimal value"并推出 r_s=0（s ≥ t）。这一步用到 r_t ≥ 0，即 f(S^t) ≤ f(O\*)，其依据是 \|S^t\|=t ≤ K 加上 O\* 是 \|S\| ≤ K 内的最优集。app:guarantee 没有一句建立它，前言也没说 \|S^t\|=t。建议：在前言补一句 "$|S^{t}|=t\le K$, so $r_t\ge0$"。状态 [HAND-PROOF-UNREVIEWED]，不影响真值。
- **GAP-3（中）f(O\*)=0 的退化情形**。`model.tex` 第 15 至 16 行的约定是"when $f(O^{\ast})=0$ every ratio statement is read as holding trivially"，而 prop:guarantee 写成乘积形 f(T) ≥ L_K(η^sel) f(O\*)，不是比值式，约定字面不覆盖它。app:guarantee 也不讨论。结论本身在 f(O\*)=0 时仍成立（右端为 0，左端由单调性与 f(∅)=0 得非负；η^sel=∞ 时右端为 0·0=0），但仓库里没有一处记录这件事。这是四条里唯一牵涉 model 层面措辞的一条。建议：把 `model.tex` 的约定从 "every ratio statement" 放宽到 "every guarantee statement"，或在 app:guarantee 开头加一句退化情形。状态 [HAND-PROOF-UNREVIEWED]。
- **GAP-4（轻）η^tr 无编号定义**。prop:guarantee 的最后一句把 η^tr 当已定义符号使用，Step 4 也用它，但 η^tr 只在 `model.tex` 第 117 至 119 行的散文里给出（"The trajectory error restricts Definition~\ref{def:eta} to the states of the run"），没有 definition 环境，`notation_table.tex` 第 23 至 24 行也只给一句描述。η^sel 有编号定义 `def:etasel`，两者待遇不一致。建议：在 `def:etasel` 尾部加一句正式定义 η^tr，或在正文陈述里把最后一句的 η^tr 展开。不影响真值。

不列为 GAP 但记录的一条：O\* 的记号只在附录的 notation table 里定义，正文陈述与 app:guarantee 都直接用 f(O\*)。这是全文共享的记号惯例（statements 包的 `inputs/assumptions.md` 第 31 行也这样写），不单独算作本命题的缺口。

---

## 4. 本文件自身算术的核对（exact arithmetic）

用 sympy 与 fractions.Fraction，浮点只在打印。脚本内容如下，可直接重跑（本文件不在仓库里新增脚本文件）：

```python
from fractions import Fraction as F
import sympy as sp
x, K = sp.symbols('x K', positive=True)
LK = 1 - (1 - 1/(x*K))**K
print(sp.simplify(sp.diff(LK, x)))          # L_K 对 x 的导数
print(sp.simplify(LK.subs(K, 1)))           # L_1(x)
print(1 - (1 - F(1,1)/(F(3,2)*3))**3)       # L_3(3/2)
for v in [F(1), F(5,4), F(3,2)]:
    print(v, 1 - (1 - F(1,1)/(v*3))**3)     # 排序链的数值示例
```

结果：

- dL_K/dx = −K·(1/(Kx))^K·(Kx−1)^{K−1}/x，在 x ≥ 1、K ≥ 1 上非正，故 L_K 关于 x 非增。这正是 Step 4 末段排序句所需。[VERIFIED-SYMBOLIC]
- L_1(x) = 1/x。K=1 时命题读作 f(T) ≥ f(O\*)/η^sel，成立且不需要 K ≥ 2。[VERIFIED-SYMBOLIC]
- L_K(x) ≥ 1−e^{−1/x}：K=1..12、x=1,3/2,...,10 共 228 格全部通过，零违反（有理左端与 exp 右端按 30 位精度比较）。[VERIFIED-EXHAUSTIVE（网格）]
- running example（K=3，η=3/2）：L_3(3/2)=386/729（约 0.5295），1−e^{−2/3} 约 0.4866，前者确实更大。排序链的数值示例 L_3(1)=19/27（约 0.7037）≥ L_3(5/4)=2044/3375（约 0.6056）≥ L_3(3/2)=386/729。[VERIFIED-SYMBOLIC]
- 收缩因子 1−1/(η^sel K) 在 η^sel=1、K=1 时取到下端 0，仍在 [0,1) 内，Step 3 的 unrolling 不会出现负因子。[VERIFIED-SYMBOLIC]

这些核对只覆盖 L_K 的解析性质与 Step 3、Step 4 用到的两条不等式，不覆盖 Step 1 的 covering 论证与 Step 2 的分情形论证，后两者仍是 [HAND-PROOF-UNREVIEWED]，与附录第 331 行的收尾句一致（"No script certifies the steps of the main argument."）。

---

## 5. 记录项（不计入 A_diffs，也不计入 GAP）

- **N1 措辞**：正文陈述写 "the predictor has finite error $(\eta_u,\eta_o)$"，`def:eta` 的措辞是 "has ... error at most $(\eta_u,\eta_o)$"。按 def:eta 读，"finite error $(\eta_u,\eta_o)$"应理解为"存在有限的 $(\eta_u,\eta_o)$ 使 Definition 1 成立"。Step 4 按 at most 的读法使用，无歧义风险，但两处措辞不统一。
- **N2 归属**：台账卡第 71 行的归属（Goundan & Schulz 2007, Theorem 1，α=η^sel 同向不取倒数）与正文第 92 至 95 行、`model.tex` 第 101 至 105 行、`related.tex` 第 39 至 51 行一致，四处互不冲突。本审计不核原文页码。
- **N3 台账状态行**：台账写 "[VERIFIED-LP 第一晚基线] + 附录证明（NWF 权重求和）"。按本审计，附录证明的四个 Step 里只有 Step 3、Step 4 的解析部分有 oracle 支持（§4），Step 1、Step 2 无脚本。建议台账状态行区分这两层，不建议改写为更强的标签。
- **N4 禁止声称的覆盖**：台账"禁止声称"字段里的早停变体一条，在正文与附录都有对应文字（`model.tex` 第 73 至 76 行、`rem:app-product`），E 表已记为覆盖。

---

## 6. 结论

- **A_match = false**，差异四条：D1（normalization 只在正文）、D2（T=S^K 与固定 K 步只在正文）、D3（η^tr / η 条款的 finite error 前提只在正文）、D4（三界排序只在正文）。四条都是台账压缩造成的省略，其中 D3 是唯一的作用范围差异，按字面读台账会把有前提的结论读成无前提的，建议只改台账。
- **Criterion E**：共 27 行。覆盖 17 行，隐式或 GAP 4 行（GAP-1 至 GAP-4），不需要 4 行，不适用 3 行（其中 arbitrary query access / nK queries / |S| ≤ K 合并为一行）。四条 GAP 都不影响命题真值，都可用一句话补齐，均不要求改正文陈述。
- 全局状态维持 [HAND-PROOF-UNREVIEWED]：本文件的 §4 只把 L_K 的单调性、K=1 情形、第二不等式与收缩因子非负这四件事升为 [VERIFIED-SYMBOLIC] / [VERIFIED-EXHAUSTIVE（网格）]，Step 1 的 covering 论证与 Step 2 的零步分情形论证没有 oracle 支持。

---

## 7. 状态标签小结

| 对象 | 标签 |
|---|---|
| L_K 关于 x 非增（Step 4 排序句所需） | [VERIFIED-SYMBOLIC] |
| L_1(x)=1/x（K ≥ 2 不是本命题的前提） | [VERIFIED-SYMBOLIC] |
| L_K(x) ≥ 1−e^{−1/x}（K=1..12，x=1..10 半步网格，228 格零违反） | [VERIFIED-EXHAUSTIVE（网格）] |
| 收缩因子 1−1/(η^sel K) ∈ [0,1) | [VERIFIED-SYMBOLIC] |
| Step 1 的 covering 论证 r_t ≤ K·max_e d_e(S^t) | [HAND-PROOF-UNREVIEWED] |
| Step 2 的零步分情形（benign / harmful） | [HAND-PROOF-UNREVIEWED] |
| Step 4 的链 η^sel ≤ η^tr ≤ η | [HAND-PROOF-UNREVIEWED]（与 `model.tex` 第 123 至 126 行的注释一致） |
| 命题整体 | [HAND-PROOF-UNREVIEWED]，归属 GS 2007 |

---

## 8. 读过的文件

- `/home/user/sub-modular-optimization/results/V11/statements.md`（T3 段，第 120 至 145 行）
- `/home/user/sub-modular-optimization/results/V11/inputs/statement_guarantee.md`
- `/home/user/sub-modular-optimization/results/V11/inputs/assumptions.md`
- `/home/user/sub-modular-optimization/results/V11/inputs/notation.md`
- `/home/user/sub-modular-optimization/THEOREM_LEDGER.md`（T3 卡，第 69 至 75 行；T2、T4、T5、T6 卡只作邻接核对）
- `/home/user/sub-modular-optimization/paper/sections/results.tex`（第 30 至 170 行，prop:guarantee 在第 79 至 91 行）
- `/home/user/sub-modular-optimization/paper/sections/model.tex`（全文，def:etasel 在第 84 至 116 行）
- `/home/user/sub-modular-optimization/paper/sections/appendix_proofs.tex`（app:guarantee，第 215 至 336 行；文件头第 1 至 30 行）
- `/home/user/sub-modular-optimization/paper/sections/notation_table.tex`
- `/home/user/sub-modular-optimization/results/V11/audit/nobound.md`（只取格式，不取结论）
- `/home/user/sub-modular-optimization/CLAUDE.md`
- HANDOFF 2026-09-18 与 HANDOFF ADDENDUM 2026-09-18（上传件，只取约定）

本文件未修改任何已有文件，未运行 git。
