# ROUTE-TWO 盲证：J8 ProbeLottery（$K=2$, $\eta=3/2$）

本文件是 route-two blind prover 的独立推导。只使用 `results/V11/inputs/` 下四个输入文件
（definition1.md, assumptions.md, notation.md, statement_probelottery.md）与标准数学。
未打开 paper/、THEOREM_LEDGER.md、RESEARCH_STATE.md、REPORT.md、任何 HANDOFF 文件、
任何已交付的 spot-check 脚本，也未使用 web search、未运行 git。会话开头由 harness 附带的
四个上传文件（HANDOFF_2026-09-18.md、HANDOFF_ADDENDUM_2026-09-18.md、
appendix_model_proofs.tex、J8_claude_spotcheck.py）同样没有打开：它们属于 isolation 清单
明文排除的对象（HANDOFF\*、已交付脚本），打开会使 route-two 失去盲性。这是保守选项，记录于此。

本文件中的每条数学断言都带状态标签。没有 oracle 确认的一律是
`[HAND-PROOF-UNREVIEWED]` 或 `[CONJECTURE]`。

---

## 1. 命题重述（含全部 quantifier）

**重述（ProbeLottery, 本人措辞）.** 固定 budget $K=2$ 与误差水平 $\eta=3/2$。
存在一个 randomized algorithm ProbeLottery（下称 $\mathcal A$），它满足：

- **(Q1) 量词顺序**：算法先被固定（与实例无关，只有一个常数 $\mathrm{EPS}=1/10000$
  与固定的 tie-break 序），然后对**所有**合法实例给出保证；不是先给实例再挑算法。
- **(Q2) 实例类**：对**所有** ground set $N$、所有 $n=|N|\ge 2$、所有 monotone submodular
  $f:2^N\to\mathbb R_{\ge0}$ 且 $f(\emptyset)=0$、所有 $\tilde f:2^N\to\mathbb R$ 且
  $\tilde f(\emptyset)=0$ 满足 Definition 1（convention B）中
  $d_e(S)/\eta_u\le\tilde d_e(S)\le\eta_o d_e(S)$ 对**所有** $S\subseteq N$ 与**所有**
  $e\notin S$ 成立、且 $\eta_u\eta_o=3/2$（split 任意）。$n\ge2$ 是隐含要求：算法第 2 步要
  在 $e\ne b$ 上取 argmax。$K\le n$ 由 assumptions.md 给出。
- **(Q3) 访问模型**：算法不能 evaluate $f$，只能 query $\tilde f$；至多 $9n$ 次 query；
  每次 query 的集合大小至多 $5$（注意 $5>K=2$，这正是命题要说明的“$|S|\le K$ 限制不可去”）。
- **(Q4) 输出**：输出集合 $T$ 恒有 $|T|=2$。
- **(Q5) 随机性**：算法本身是 deterministic 的直到最后一步的抽签；$\mathbb E$ 只对算法自身
  randomness 取，**不**对实例取；实例可以是 adversarial 且可以依赖算法描述（但不能依赖抽签结果）。
- **(Q6) tie-breaking**：所有 argmax 返回固定序中的第一个 maximiser。worst-case 陈述允许
  adversary 选择这个序（等价于 adversarial tie-breaking）。
- **(Q7) 结论**：$\mathbb E[f(T)]\ \ge\ \bigl(\tfrac35+\tfrac1{400000}\bigr)\mathrm{OPT}$，
  其中 $\mathrm{OPT}=\max_{|O|\le2}f(O)=f(O^\ast)$。若 $\mathrm{OPT}=0$ 则按 assumptions.md
  的约定平凡成立。
- **(Q8) $\eta$ 与 $K$ 的定义域**：命题**只**对 $K=2$、$\eta=3/2$ 陈述。$\eta\in[1,\infty)$、
  $K\ge1$ 的一般情形不在本命题范围内；算法描述里的常数（$4$ 轮、$8$ 个 secondary、
  $127/128$、$1/1024$、$\mathrm{EPS}$、$|S|\le5$）都是为 $K=2,\eta=3/2$ 校准的。
- **(Q9) 对比对象**：$\rho_2(3/2)=3/5$ 是 single-step predictive greedy 在 adversarial ties
  下的精确最坏比。结论中的 $3/5+1/400000$ 严格大于它，这是命题的全部内容。

**空洞性检验（CLAUDE.md 第四条规则）**：去掉 "size at most $5$" 则命题与 linear-budget
optimality theorem 不矛盾，整句失去意义（这是唯一的 payload）；去掉 "randomized" 则
$\mathbb E$ 无意义且（据 statement 的说法）结论应当不成立；去掉 "$\eta=3/2$" 则
$3/5$ 这个基线数值不再是 $\rho_K$；去掉 "adversarial tie-breaking" 则 $3/5$ 基线本身变松。
四个限定词都不空洞。"$9n$ queries" 可以换成任何 $\Theta(n)$ 而不改变真值，属于
implementation detail，不是空洞但也不是必需的精确常数。

---

## 2. 归一化与记号

以下恒设 $\mathrm{OPT}=1$（$f$ 齐次，可除以 $\mathrm{OPT}>0$）。记
$O^\ast=\{o_1,o_2\}$ 为一个最优 2-集（若最优值由单点达到，用 monotonicity 补一个任意元素，
不减少 $f$）。记
$$x=f(\{b\}),\quad w_i=f(\{o_i\}),\quad h_i=f(\{b,o_i\}),\quad
w^\ast=\max_i w_i,\quad h^\ast=\max_i h_i,$$
$$M=\tilde f(\{b\}),\quad p=\tilde f(\{b,c\})=\max_{e\ne b}\tilde f(\{b,e\}),\quad
\beta=f(P_0),\quad \varepsilon=\beta-\tfrac35 .$$
$g=\tilde f$。$C$ 为算法第 3 步的 pool，$r\in\{0,1,2,3,4\}$ 为实际执行的 extension 轮数
（$r=\min\{4,|C|\}$，因为 $b\notin C$ 且每轮从 $C\setminus B$ 取一个新元素）。

---

## 3. 预备引理

**L0（scale invariance）** `[HAND-PROOF-UNREVIEWED]`
ProbeLottery 的全部判定在 $\tilde f\mapsto c\tilde f$（$c>0$）下不变。
理由：第 1、2、4 步是 argmax；第 3 步的两个判据
$g(\{e\})\ge M-\mathrm{EPS}\cdot M$ 与 $g(\{b,e\})\ge p-\mathrm{EPS}\cdot M$
两边关于 $g$ 都是 1-齐次。由 definition1.md 的 convention B，rescaling
$(\eta_u,\eta_o)\mapsto(c\eta_u,\eta_o/c)$ 保持 $\eta$ 不变，取 $c=1/\eta_u$ 得
$(\eta_u,\eta_o)=(1,3/2)$。**因此以下恒设**
$$d_e(S)\ \le\ \tilde d_e(S)\ \le\ \tfrac32\,d_e(S)\qquad\forall S,\ \forall e\notin S. \tag{L0}$$

**L1（集合级 sandwich）** `[HAND-PROOF-UNREVIEWED]`
对所有 $S$：$f(S)\le\tilde f(S)\le\frac32 f(S)$。
证：沿 $S$ 的任一枚举 telescoping，$\tilde f(S)=\sum_i\tilde d_{e_i}(S_{i-1})$，
$f(S)=\sum_i d_{e_i}(S_{i-1})$，逐项用 (L0)，再用 $\tilde f(\emptyset)=f(\emptyset)=0$。
同样对任意 $B\subseteq S$：$\tilde f(S)\le\tilde f(B)+\frac32\,(f(S)-f(B))$。

**L2（pair-consistency，band 的双侧夹逼）** `[HAND-PROOF-UNREVIEWED]`
对任意 $u\ne e$：
$$\tilde f(\{u\})-\tilde f(\{e\})\ \le\ \tfrac32\bigl(f(\{u,e\})-f(\{e\})\bigr)-\bigl(f(\{u,e\})-f(\{u\})\bigr),$$
等价地
$$f(\{u,e\})\ \ge\ 2\bigl(\tilde f(\{u\})-\tilde f(\{e\})\bigr)+3f(\{e\})-2f(\{u\}). \tag{L2}$$
证：$\tilde f(\{u,e\})\ge\tilde f(\{u\})+d_e(\{u\})$（(L0) 下界）与
$\tilde f(\{u,e\})\le\tilde f(\{e\})+\frac32 d_u(\{e\})$（(L0) 上界），两式相夹。
这一条是全篇的关键：它说明 $\tilde f$ 是**一个集合函数**（不是逐步独立的预言），
单点预测的排序会反过来约束 pair 的真值。

**L3（第二步 argmax 的价值）** `[HAND-PROOF-UNREVIEWED]`
对任意 $e\ne b$：$\beta=f(P_0)=x+d_c(\{b\})\ \ge\ x+\frac23\tilde d_e(\{b\})\ \ge\
x+\frac23 d_e(\{b\})$，即
$$\beta\ \ge\ \tfrac13 f(\{b\})+\tfrac23 f(\{b,e\})\qquad\forall e\ne b. \tag{L3}$$
（用 $\tilde d_c(\{b\})\ge\tilde d_e(\{b\})$ 与 $d_c\ge\frac23\tilde d_c$。）
同样的论证对任意 $v$ 与 $z_v=\arg\max_{z\ne v}g(\{v,z\})$ 成立：
$$f(\{v,z_v\})\ \ge\ \tfrac13 f(\{v\})+\tfrac23 f(\{v,e\})\qquad\forall e\ne v. \tag{L3'}$$

**L4（第一步 argmax）** `[HAND-PROOF-UNREVIEWED]`
对所有 $e$：$\frac32 f(\{b\})\ge\tilde f(\{b\})\ge\tilde f(\{e\})\ge f(\{e\})$，
故 $x\ge\frac23 f(\{e\})$，且 $M\ge\tilde f(\{e\})$。

**L5（submodular 分裂）** `[HAND-PROOF-UNREVIEWED]`
对任意 $A$：$d_{o_1}(A)+d_{o_2}(A)\ge f(A\cup O^\ast)-f(A)\ge 1-f(A)$，故
$\max_i d_{o_i}(A)\ge\frac{1-f(A)}2$，即 $\max_i f(A\cup\{o_i\})\ge\frac{1+f(A)}2$。
特别地 $w_1+w_2\ge1$（取 $A=\emptyset$），$h_1+h_2\ge 1+x$（取 $A=\{b\}$，
再加 $f(\{b\})$ 到两边的 submodularity 形式 $h_1+h_2\ge f(\{b\}\cup O^\ast)+f(\{b\})$）。

---

## 4. 基线：$\beta\ge 3/5$（不引用外部结果的自足证明）

**命题 4.1** `[HAND-PROOF-UNREVIEWED]`（算术部分 `[VERIFIED-SYMBOLIC]`，见 §10）
在 (Q2) 的任意实例上，predictive greedy 的输出 $P_0=\{b,c\}$ 满足
$f(P_0)\ge\frac35\mathrm{OPT}$。

证明分两种情形。

**情形 $b\in O^\ast$**（设 $b=o_1$）：由 (L3) 取 $e=o_2$，
$\beta\ge\frac13 w_1+\frac23 f(O^\ast)=\frac13w_1+\frac23\ge\frac23>\frac35$。

**情形 $b\notin O^\ast$**：
1. 由 (L5)：$w^\ast\ge\frac12$，$h^\ast\ge\frac{1+x}2$。
2. 由 (L2) 取 $u=b,e=o_i$，并用 (L4) 的 $\tilde f(\{b\})\ge\tilde f(\{o_i\})$（即左端 $\ge0$）：
   $$h_i\ \ge\ 3w_i-2x. \tag{4.1}$$
3. 由 (L3) 取 $e=o_{i^\ast}$（$h_{i^\ast}=h^\ast$）：$\beta\ge\frac{x+2h^\ast}3$。
4. 代入 1 的 $h^\ast\ge\frac{1+x}2$：$\beta\ge\frac{1+2x}3$（分支 A）。
5. 代入 (4.1) 与 $w^\ast\ge\frac12$：$\beta\ge\frac{x+2(3w^\ast-2x)}3=2w^\ast-x\ge1-x$（分支 B）。
6. 故 $\beta\ge\min_{x}\max\{\frac{1+2x}3,\,1-x\}=\frac35$，唯一取到处 $x=\frac25$。

注：只用 (L5)+(L3) 会得到 $\frac{1+2x}{3}\ge\frac59=L_2(3/2)$（$x\ge\frac13$ 来自 (L4)），
比 $3/5$ 弱。把 $5/9$ 提升到 $3/5$ 的**唯一**新成分是 (L2)，也就是
"$\tilde f$ 必须是一个自洽的集合函数" 这一条。这一点在数值上得到确认：
§10 给出的 $5/9$ 候选实例恰好被 (L2) 判为不可行。

**命题 4.2** `[VERIFIED-EXHAUSTIVE]` 存在 $n=4$ 的实例使 $\beta=\frac35$ 精确取到
（脚本 `J8_route2_check.py::tight_instance`，有理数精确、全子集验证 band 与 submodularity）。
与命题 4.1 合并得 $\rho_2(3/2)=3/5$，与 statement 给出的数值一致。

---

## 5. 近紧刚性（rigidity）

设 $\varepsilon=\beta-\frac35\ge0$，且 $b\notin O^\ast$。以下全部由 §4 的不等式直接反解，
对**任意** $\varepsilon\ge0$ 成立（$\varepsilon$ 大时结论平凡）。
`[HAND-PROOF-UNREVIEWED]`，系数由 sympy 复核 `[VERIFIED-SYMBOLIC]`（§10）。

| 编号 | 结论 | 来源 |
|---|---|---|
| R1 | $x\le\frac25+\frac32\varepsilon$ | 分支 A |
| R2 | $x\ge\frac25-\varepsilon$ | 分支 B |
| R3 | $\frac7{10}-\frac\varepsilon2\le h^\ast\le\frac7{10}+2\varepsilon$ | (L5) 与 $\beta\ge\frac{x+2h^\ast}3$ |
| R4 | $h_i\ge\frac7{10}-3\varepsilon$（两个 $i$ 都成立） | $h_1+h_2\ge1+x$ 与 R3 |
| R5 | $\frac12-\frac53\varepsilon\le w_i\le\frac12+\frac53\varepsilon$ | (4.1) 与 $w_1+w_2\ge1$ |
| R6 | $\Delta_i:=M-\tilde f(\{o_i\})\le\frac52\varepsilon$ | (L2) 改写：$\Delta_i\le\frac12 h_i-\frac32w_i+x$ |
| R7 | $M\ge\max\{x,\,w^\ast\}\ge\frac12-\frac53\varepsilon$，且 $M\le\frac32x\le\frac35+\frac94\varepsilon$ | (L4) |
| R8 | $p-\tilde f(\{b,o_i\})\le5\varepsilon$ | $p\le M+\frac32(\beta-x)$ 与 $\tilde f(\{b,o_i\})\ge M+h_i-x$ |

R6、R8 的常数项都恰好为 $0$：在**精确紧**的实例上，$\tilde f(\{o_i\})=M$ 与
$\tilde f(\{b,o_i\})=p$ 是被强制的等式。这就是 pool 判据存在的理由。

---

## 6. 引理 P：近紧时 $O^\ast$ 必在 pool 内

**引理 P** `[HAND-PROOF-UNREVIEWED]`（阈值算术 `[VERIFIED-SYMBOLIC]`）
若 $\varepsilon\le\mathrm{EPS}/11=1/110000$，则 $o_1,o_2\in C$。

证：pool 的两个判据分别要求 $\Delta_i\le\mathrm{EPS}\cdot M$ 与
$p-\tilde f(\{b,o_i\})\le\mathrm{EPS}\cdot M$。由 R6、R8 只需 $5\varepsilon\le\mathrm{EPS}\cdot M$；
由 R7，$M\ge\frac12-\frac53\varepsilon$。代入 $\varepsilon=1/110000$：
$5\varepsilon=4.545\times10^{-5}$，$\mathrm{EPS}\cdot M\ge4.99985\times10^{-5}$，成立。$\square$

**推论 P'** 若 $C=\emptyset$（即 $r=0$），则 $\varepsilon>1/110000>1/400000$，
而此时 secondary list 是 $P_0$ 的 8 个副本，$\mathbb E[f(T)]=\beta$，命题成立。

---

## 7. 引理 D：每个 secondary set 的普遍下界

这是整个证明里最有用的一条，它不需要 rigidity。

**引理 D** `[HAND-PROOF-UNREVIEWED]`
设 $v\in C$，$z_v=\arg\max_{z\ne v}g(\{v,z\})$。则
$$\text{(D1)}\quad f(\{b,v\})\ \ge\ \tfrac35-\tfrac23\mathrm{EPS}\cdot M,
\qquad
\text{(D2)}\quad f(\{v,z_v\})\ \ge\ \tfrac35-\tfrac43\mathrm{EPS}\cdot M .$$
由 $M\le\frac32 f(\{b\})\le\frac32\mathrm{OPT}$，两式都蕴含
$f(A)\ge\bigl(\frac35-2\mathrm{EPS}\bigr)\mathrm{OPT}$。

**(D1) 的证明.** $v\in C$ 给出 $\tilde f(\{b,v\})\ge p-\mathrm{EPS}\cdot M$。于是
$$f(\{b,v\})=x+d_v(\{b\})\ \ge\ x+\tfrac23\bigl(\tilde f(\{b,v\})-M\bigr)
\ \ge\ x+\tfrac23\bigl(p-M\bigr)-\tfrac23\mathrm{EPS}\cdot M .$$
又 $p\ge\tilde f(\{b,o_{i^\ast}\})\ge M+h^\ast-x$，故
$f(\{b,v\})\ge\frac13x+\frac23h^\ast-\frac23\mathrm{EPS}\cdot M$。
而 §4 步骤 3-6 正是证明 $\frac{x+2h^\ast}3\ge\frac35$（情形 $b\notin O^\ast$）；
情形 $b\in O^\ast$ 时改用 $p\ge\tilde f(\{b,o_2\})\ge M+1-x$ 得
$f(\{b,v\})\ge\frac23+\frac x3-\frac23\mathrm{EPS}\cdot M\ge\frac35$。$\square$

**(D2) 的证明.** 记 $\varphi=f(\{v\})$。
- 上路（用 (L3') + (L5)）：$\max_i f(\{v,o_i\})\ge\frac{1+\varphi}2$，故
  $f(\{v,z_v\})\ge\frac13\varphi+\frac23\cdot\frac{1+\varphi}2=\frac13+\frac23\varphi$。
- 下路（用 (L2) + pool）：取 $u=v$、$e=o^\ast$（$w^\ast\ge\frac12$）。pool 给
  $\tilde f(\{v\})\ge(1-\mathrm{EPS})M$，(L4) 给 $\tilde f(\{o^\ast\})\le M$，故
  $\tilde f(\{v\})-\tilde f(\{o^\ast\})\ge-\mathrm{EPS}\cdot M$，(L2) 给
  $f(\{v,o^\ast\})\ge3w^\ast-2\varphi-2\mathrm{EPS}\cdot M\ge\frac32-2\varphi-2\mathrm{EPS}M$。
  再用 (L3')：$f(\{v,z_v\})\ge\frac13\varphi+\frac23 f(\{v,o^\ast\})
  \ge1-\varphi-\frac43\mathrm{EPS}\cdot M$。
- 两路取 max：$\max\{\frac13+\frac23\varphi,\ 1-\varphi\}\ge\frac35$，
  最小值在 $\varphi=\frac25$ 处取到。$\square$

**解读**：$\varphi=\frac25$ 表示 $v$ 是 "$b$ 的克隆"（真值 $2/5$、预测 $3/5$）。
(D2) 说明 adversary 无法在 pool 里放进 "既骗过 pool 判据又使 $\{v,z_v\}$ 差于 $3/5$" 的元素：
克隆越像 $b$，(L2) 就越强迫它与 $O^\ast$ 的 pair 值变大。

---

## 8. 彩票权重的精确算术

$\frac{127}{128}+8\cdot\frac1{1024}=1$ `[VERIFIED-SYMBOLIC]`。
设 $r$ 轮 extension，secondary list 含 $2r$ 个 special set $A_1,\dots,A_{2r}$
与 $8-2r$ 个 $P_0$ 副本，记 $\gamma_j=f(A_j)/\mathrm{OPT}$。于是
$$\frac{\mathbb E[f(T)]}{\mathrm{OPT}}
=\Bigl(1-\frac r{512}\Bigr)\beta+\frac1{1024}\sum_{j=1}^{2r}\gamma_j
=\beta+\frac1{1024}\sum_{j=1}^{2r}(\gamma_j-\beta). \tag{8.1}$$
目标 $\frac35+\frac1{400000}$ 换算成 (8.1) 的第二项：当 $\beta=\frac35$ 时需要
$\sum_j(\gamma_j-\beta)\ \ge\ \frac{1024}{400000}=\frac8{3125}=0.00256$ `[VERIFIED-SYMBOLIC]`。
这说明两件事：
(i) 单靠 $\frac{127}{128}\beta$ 无法收工，除非 $\beta\ge\frac{240001}{396875}\approx0.60473$；
(ii) 8 个 secondary set 即使全部取到 $\mathrm{OPT}$ 也只贡献 $\frac8{1024}=\frac1{128}$，
所以证明必须是 "deficit 全部 $O(\mathrm{EPS})$ + 至少一个 set 有 $\Theta(1)$ surplus" 的结构。

由引理 D，每个 special set 的 deficit
$$\beta-\gamma_j\ \le\ \varepsilon+2\mathrm{EPS}, \tag{8.2}$$
于是无条件地
$$\frac{\mathbb E[f(T)]}{\mathrm{OPT}}\ \ge\ \beta-\frac{8}{1024}\bigl(\varepsilon+2\mathrm{EPS}\bigr)
=\frac35+\frac{127}{128}\varepsilon-\frac{\mathrm{EPS}}{64}. \tag{8.3}$$

---

## 9. 情形分析

记 $\varepsilon=\beta-\frac35\ge0$（由命题 4.1，$\varepsilon\ge0$ 恒成立），并记阈值
$$\varepsilon^{\dagger}:=\frac{128}{127}\Bigl(\frac1{400000}+\frac{\mathrm{EPS}}{64}\Bigr)
=\frac{13}{3175000}=4.0945\times10^{-6}. $$

**情形 0（$\varepsilon\ge\varepsilon^{\dagger}$）** `[HAND-PROOF-UNREVIEWED]`（算术 `[VERIFIED-SYMBOLIC]`）
直接由 (8.3)：$\mathbb E/\mathrm{OPT}\ge\frac35+\frac{127}{128}\varepsilon
-\frac{\mathrm{EPS}}{64}\ge\frac35+\frac1{400000}$。闭合。
（这一格吞掉了 "$\beta$ 很大" 的平凡情形：例如 $\beta\ge\frac{240001}{396875}$ 时
$\varepsilon\ge4.7\times10^{-3}\gg\varepsilon^{\dagger}$；也吞掉了 $b\in O^\ast$ 的情形，
那里 $\beta\ge\frac23$。）

以下设 $\varepsilon<\varepsilon^{\dagger}$。

**情形 I（某个 $o_i\notin C$）** `[HAND-PROOF-UNREVIEWED]`（算术 `[VERIFIED-SYMBOLIC]`）
此格为空。理由：$o_i\notin C$ 意味着 R6 或 R8 的松弛被突破，即
$\frac52\varepsilon>\mathrm{EPS}\cdot M$ 或 $5\varepsilon>\mathrm{EPS}\cdot M$；
两者中较弱者给 $\varepsilon>\frac{\mathrm{EPS}\cdot M}5$，与 R7（$M\ge\frac12-\frac53\varepsilon$）
联立得 $\varepsilon>\frac3{300010}=9.9997\times10^{-6}>\varepsilon^{\dagger}$（余量约 $2.4$ 倍），
与 $\varepsilon<\varepsilon^{\dagger}$ 矛盾。
这同时给出 $C\ne\emptyset$、$r\ge1$：$r=0$ 时 $o_1\notin C$。
（另一条独立路径：$\varepsilon<\varepsilon^{\dagger}<\mathrm{EPS}/11$，引理 P 直接给 $o_1,o_2\in C$。）

**情形 II-a（$o_1,o_2\in C$，且某轮取到 $v_k=o_i$）** `[HAND-PROOF-UNREVIEWED]`
此时 special set $\{o_i,z_{o_i}\}$ 由 (L3') 取 $e=o_{3-i}$ 得
$$f(\{o_i,z_{o_i}\})\ \ge\ \tfrac13w_i+\tfrac23 f(O^\ast)=\tfrac13w_i+\tfrac23
\ \ge\ \tfrac56-\tfrac59\varepsilon\quad(\text{R5}),$$
surplus $\ge\frac56-\frac59\varepsilon-\beta=\frac7{30}-\frac{14}9\varepsilon$。
其余至多 7 个 special set 的 deficit 由 (8.2) 合计至多 $7(\varepsilon+2\mathrm{EPS})$。
代入 $\varepsilon<\varepsilon^{\dagger}<\mathrm{EPS}/11$：
surplus $\ge0.23332$，deficit 合计 $\le0.00147$，净值 $/1024\ \ge2.26\times10^{-4}
\gg\frac1{400000}=2.5\times10^{-6}$。闭合，余量约 $90$ 倍。

**情形 II-b（$o_1,o_2\in C$ 但四轮都没取到它们）** `[FAILED]`
这一格没有闭合，见 §11。

---

## 10. 数值 walk-through（$K=2$, $\eta=3/2$）

脚本 `results/V11/route2/J8_route2_check.py`，有理数精确，一键复跑。

**紧实例（$n=4$）** `[VERIFIED-EXHAUSTIVE]`
ground set 与 tie-break 序 $b\prec c\prec o_1\prec o_2$；$f$ 为 coverage function，
universe 权重 $\{u_1{=}\frac15,\ r_1{=}\frac3{10},\ u_2{=}\frac15,\ r_2{=}\frac3{10},\
cc{=}\frac15\}$，$b=\{u_1,u_2\}$，$c=\{cc\}$，$o_1=\{u_1,r_1\}$，$o_2=\{u_2,r_2\}$。
于是
$$x=\tfrac25,\quad w_1=w_2=\tfrac12,\quad h_1=h_2=\tfrac7{10},\quad
f(\{b,c\})=\tfrac35,\quad \mathrm{OPT}=f(\{o_1,o_2\})=1 .$$
预测器由 difference-constraint 系统（见下）求出的极大解给出：
$$\tilde f(\{b\})=\tilde f(\{o_1\})=\tilde f(\{o_2\})=\tfrac35,\quad
\tilde f(\{c\})=\tfrac3{10},\quad
\tilde f(\{b,c\})=\tilde f(\{b,o_i\})=\tilde f(\{c,o_i\})=\tfrac9{10},\quad
\tilde f(\{o_1,o_2\})=\tfrac{27}{20}.$$
全部 $16$ 个子集、全部 $(S,e)$ 对上 band 成立（脚本 assert）；$f$ 的 monotone +
submodular 由 coverage 结构保证并穷举复核。运行结果：
- 第 1 步：四个单点预测 $\frac35,\frac3{10},\frac35,\frac35$，$b$ 以 tie-break 胜出，$M=\frac35$；
- 第 2 步：$\tilde f(\{b,c\})=\tilde f(\{b,o_1\})=\tilde f(\{b,o_2\})=\frac9{10}$，
  $c$ 以 tie-break 胜出，$p=\frac9{10}$，$P_0=\{b,c\}$，$f(P_0)=\frac35=\rho_2(3/2)\mathrm{OPT}$；
- 第 3 步：$C=\{o_1,o_2\}$（$c$ 因 $\tilde f(\{c\})=\frac3{10}<(1-\mathrm{EPS})\frac35$ 出局）；
- 第 4 步：$r=2$，$B=[b,o_1,o_2]$，secondary list
  $\{o_1,o_2\},\{b,o_1\},\{o_1,o_2\},\{b,o_2\}$ 加 4 个 $\{b,c\}$ 副本，
  真值分别为 $1,\frac7{10},1,\frac7{10},\frac35,\frac35,\frac35,\frac35$；
- 第 5 步：$\mathbb E[f(T)]=\frac{127}{128}\cdot\frac35+\frac1{1024}\bigl(1+\frac7{10}+1+\frac7{10}+4\cdot\frac35\bigr)
  =\frac{3077}{5120}=\frac35+\frac1{1024}$ `[VERIFIED-SYMBOLIC]`；
- query 数 $11\le 9n=36$，最大 query 集合大小 $3\le5$。

余量 $\frac1{1024}=9.77\times10^{-4}$ 是目标 $\frac1{400000}=2.5\times10^{-6}$ 的约 $390$ 倍。

**与 statement 中 "$3/5+1/2048$" 的差异**：statement 说实现版在紧实例上恰好取到
$\frac35+\frac1{2048}$。$\frac1{2048}$ 对应 $\sum_j(\gamma_j-\beta)=\frac12$，
即只有**一轮** extension（$|C|=1$）且该轮产出 $\{o,z_o\}=1$、$\{b,o\}=\frac7{10}$：
$0.4+0.1=0.5$。我构造的紧实例是对称的（$|C|=2$），得 $\sum_j(\gamma_j-\beta)=1$，
即 $\frac35+\frac1{1024}$。两者都 $>\frac35+\frac1{400000}$，不冲突；差异说明对方的紧实例
是非对称的（只有一个 $o_i$ 进 pool）。我尝试过的非对称版本（$w_1=\frac35,w_2=\frac25$）
被 (L2) 判为不可行，所以我没有复现出 $\frac1{2048}$ 这个具体数值。`[CONJECTURE]`

**$5/9$ 陷阱（为什么 (L2) 不可省）** `[VERIFIED-EXHAUSTIVE]`
只用 (L3)+(L4)+(L5) 的下界是 $L_2(3/2)=\frac59$，对应 $x=\frac13$、$w_i=\frac12$、
$d_{o_i}(\{b\})=\frac13$、$d_c(\{b\})=\frac29$ 的 "实例"。它逐步看都合法，但
$\tilde f(\{b,o_1\})$ 同时被要求 $\ge\frac12+\frac13=\frac56$ 与
$\le\frac12+\frac32\cdot\frac16=\frac34$，不存在。difference-constraint 求解器
（`feasible_tilde`）对它给出 negative cycle。

**$K=3$**：ProbeLottery 的常数（4 轮、8 entries、$127/128$、$1/1024$、$|S|\le5$）
是对 $K=2$ 校准的，命题也只在 $K=2$ 陈述，因此 $K=3$ 的 walk-through 对本条目
没有意义。可供对照的只有 notation.md 的曲线值（`[VERIFIED-SYMBOLIC]`，Fraction 复算）：
$k_1=(K-1)\eta+1=4$、$q=\frac34$、$K\eta=\frac92$，
$$V_0=\tfrac23,\quad V_1=1-\tfrac34\cdot\tfrac59=\tfrac7{12},\quad
V_2=1-\tfrac9{16}\cdot\tfrac79=\tfrac9{16},\quad V_3=1-\tfrac{27}{64}=\tfrac{37}{64},$$
故 $\rho_3(3/2)=\min_jV_j=\frac9{16}=0.5625$，而
$L_3(3/2)=1-(1-\frac29)^3=\frac{386}{729}=0.5295$，$U_3(3/2)=\frac{37}{64}$。
一个 $K=3$ 版本的 ProbeLottery 若要超过 $\frac9{16}$，需要重新校准全部常数
（轮数、entry 数、$\mathrm{EPS}$、两个抽签权重），本文件不做。

**验证工具（difference-constraint 判定器）** `[VERIFIED-EXHAUSTIVE]`
band 约束 $d_e(S)\le\tilde f(S\cup e)-\tilde f(S)\le\frac32 d_e(S)$、算法的每个
argmax 结果（$\tilde f(X)\ge\tilde f(Y)$）、以及固定 $M$ 后的 pool 判据
（$\tilde f(\{e\})\ge(1-\mathrm{EPS})M$ 等，常数项挂到 $\emptyset$ 节点）
**全部是 difference constraints**。因此 "是否存在满足给定运行轨迹的合法预测器"
等价于该有向图有无 negative cycle，可用 Fraction 版 Bellman-Ford 精确判定
（$2^n$ 个节点）。这个工具是本文件的主要 oracle。

**反例搜索（对命题的攻击）** `[FAILED]`（未找到反例）
我按 §11 的 II-b 结构显式构造了 $n=7$ 的候选反例：$b$ 与四个 "克隆"
$j_1,\dots,j_4$（真值 $\frac25$、预测 $\frac35$，与 $b$ 各重叠 $\frac15$），
$o_1,o_2$ 覆盖两个不交半区，tie-break 序把 $j$ 排在 $o$ 之前，使四轮 extension
全部被克隆占据、8 个 secondary set 全部等于 $\frac35$，从而 $\mathbb E=\frac35$。
Bellman-Ford 判定：**不可行**，且最小不可行核是
"$\tilde f(\{b\})=\tilde f(\{j_1\})=\tilde f(\{o_i\})=\frac35$ 且 $\tilde f(\{b,j_1\})=\frac9{10}$"
本身。机制是 triple 夹逼：
$$\tilde f(\{b,j_1,o_1\})\ \ge\ \tilde f(\{b,j_1\})+d_{o_1}(\{b,j_1\})=\tfrac9{10}+\tfrac15=\tfrac{11}{10},$$
$$\tilde f(\{b,j_1,o_1\})\ \le\ \tilde f(\{b,o_1\})+\tfrac32 d_{j_1}(\{b,o_1\})
\le\tfrac9{10}+\tfrac32\cdot\tfrac1{10}=\tfrac{21}{20}<\tfrac{11}{10}.$$
这条 triple 不等式是 (L2) 的高阶版本，很可能就是补上 II-b 所缺的那一步的正确工具。
另外跑了 400 个结构化随机实例（两个不交半区 + 2 至 4 个 decoy，两族合法预测器），
最小 $\mathbb E/\mathrm{OPT}=\frac{1537}{2048}=0.7505$，最小 $f(P_0)/\mathrm{OPT}=\frac34$，
无违例；但这两族预测器都过弱（scaled-coverage 预测器是 submodular 的），
所以这只是很弱的旁证 `[CONJECTURE]`。

---

## 11. 未能闭合的步骤（以及被迫添加的假设）

**G1（主缺口，情形 II-b）** `[FAILED]`
需要的命题是：**若 $o_1,o_2\in C$ 且 $\varepsilon<4.1\times10^{-6}$，则四轮 extension
中至少有一轮取到某个 $o_i$。**
我没有证出它，也没有证伪它。已知的部分结果：
- 第 $k$ 轮 $o$ 被 $v_k$ 挡住的必要条件是
  $\frac32 d_{v_k}(B)\ge d_{o}(B)$（band 两侧 + 共同的 $\tilde f(B)$），
  与 (L5) 联立给 $f(B\cup\{v_k\})\ge\frac{1+2f(B)}3$，
  于是 $f(B_1)\ge\frac35\Rightarrow f(B_2)\ge\frac{11}{15}\Rightarrow
  f(B_3)\ge\frac{37}{45}\Rightarrow f(B_4)\ge\frac{119}{135}$。
  这只说明挡路者必须 "真的有用"，没有直接矛盾，因为 $f$ 在 $|B|\ge3$ 上可以超过 $\mathrm{OPT}$。
- 我按这个结构显式构造的 $n=7$ 候选反例被精确判定为不可行（§10），
  阻断它的是 triple 夹逼不等式，而不是我在 §4-§7 里用到的任何一条 pair 级不等式。
- 因此我的判断是：命题多半为真，但证明需要一条我没写出来的 **triple 级 (L2)**
  （形如 $\tilde f(B\cup\{v\})\le\tilde f(B\cup\{o\})+\frac32 d_v(B\cup\{o\})$ 与
  $\tilde f(B\cup\{o\})\ge\tilde f(B)+d_o(B)$ 的组合），把 "$v$ 挡住 $o$" 翻译成
  "$f(\{v,z_v\})$ 或 $f(\{b,v\})$ 出现 $\Theta(1)$ 的 surplus"。
  这一条我在时间盒内没有做出来。`[CONJECTURE]`
- 没有这一步，本文件证明的是下面这个**弱化结论**：
  $$\mathbb E[f(T)]\ \ge\ \Bigl(\tfrac35+\tfrac1{400000}\Bigr)\mathrm{OPT}
  \quad\text{在情形 0、I、II-a 下成立；II-b 下只得到 }\ \mathbb E[f(T)]\ \ge\
  \Bigl(\tfrac35-2\mathrm{EPS}\cdot\tfrac{8}{1024}\Bigr)\mathrm{OPT},$$
  即 $\mathbb E\ge(3/5-1.5625\times10^{-6})\mathrm{OPT}$，比目标低 $4.1\times10^{-6}$。

**G2（$\rho_2(3/2)=3/5$ 的引用方式）** 已消除。statement 把它当作既知事实引用；
我在 §4 给了不依赖它的自足证明（下界）并在 §10 给了达到它的精确实例（上界）。
两个方向都不依赖外部文件。

**G3（$9n$ 与 $|S|\le5$ 的核算）** `[VERIFIED-EXHAUSTIVE]`（仅在所跑实例上）
我只在跑过的实例上做了 assert。一般性论证（草稿）：第 1 步 $n$ 次、第 2 步 $n-1$ 次、
第 3 步复用缓存 $0$ 次、第 4 步每轮至多 $|C|\le n-1$ 次（选 $v$）加 $n-1$ 次（选 $z_v$），
四轮至多 $8(n-1)$ 次，合计 $\le 10n-9$，**超过** $9n$（当 $n\ge10$ 时 $10n-9>9n$）。
要落到 $9n$ 需要用到缓存的重叠（例如 $g(\{b,e\})$ 在第 2 步已经全部算过，
第 4 轮第一轮的 $g(B\cup\{e\})=g(\{b,e\})$ 完全命中缓存，省掉 $\le n-1$ 次），
这样是 $\le 9n-8$。我认为 $9n$ 成立，但这依赖 "每个不同集合只 query 一次" 的缓存假设，
statement 里确实写了这一条。`[HAND-PROOF-UNREVIEWED]`

**G4（$\mathrm{EPS}$ 的取值）** 本文件的阈值链条要求
$\frac{128}{127}(\frac1{400000}+\frac{\mathrm{EPS}}{64})<\frac{\mathrm{EPS}}5\cdot(\frac12-\cdots)$，
即 $\mathrm{EPS}$ 既不能太小（情形 I 的强迫量 $\propto\mathrm{EPS}$ 会掉到目标以下）
也不能太大（deficit $\propto\mathrm{EPS}$ 会吃掉余量）。$\mathrm{EPS}=10^{-4}$ 落在
可行区间内，余量约 $2.4$ 倍。若把目标从 $\frac1{400000}$ 提到 $\frac1{100000}$，
情形 I 就会失效（$10^{-5}<\frac{128}{127}(10^{-5}+1.56\times10^{-6})$ 边缘不成立），
所以 $\frac1{400000}$ 这个具体常数与 $\mathrm{EPS}=10^{-4}$ 是配套的。`[VERIFIED-SYMBOLIC]`

**被迫添加的假设**：除 G1 外没有添加任何假设。§2 中 "最优值由单点达到时补一个元素"
是 monotonicity 的直接推论，不算额外假设。self status 因此是 **partial**。

---

## 12. 读过的文件与产出

读过（全部四个，无其他）：
- `results/V11/inputs/definition1.md`
- `results/V11/inputs/assumptions.md`
- `results/V11/inputs/notation.md`
- `results/V11/inputs/statement_probelottery.md`

新建（只在 `results/V11/route2/` 下，未修改任何既有文件）：
- `results/V11/route2/probelottery.md`（本文件）
- `results/V11/route2/J8_route2_check.py`（紧实例 + difference-constraint 判定器 +
  算法的独立实现 + 候选反例；`python3 J8_route2_check.py`）
- `results/V11/route2/J8_route2_constants.py`（§4-§9 全部常数的 sympy/Fraction 复核；
  `python3 J8_route2_constants.py`）
- `results/V11/route2/J8_route2_random.py`（结构化随机搜索；
  `python3 J8_route2_random.py 400`）
