# ROUTE-TWO 盲证：prop:guarantee（ledger T3，Goundan-Schulz 2007 归属）

本文件是 TASKS11 Q5a 的独立推导。只使用 `results/V11/inputs/` 下四个输入文件中的定义，
外加标准数学（submodularity、telescoping、归纳法、`1-u\le e^{-u}`）。
没有查阅 `paper/`、台账、REPORT、HANDOFF 或任何已有证明。

隔离说明：本次会话的上游消息里附带了 `HANDOFF_2026-09-18.md`、`HANDOFF_ADDENDUM_2026-09-18.md`、
`appendix_model_proofs.tex`、`J8_claude_spotcheck.py` 四个上传文件。按 ROUTE-TWO 盲证的要求，
其中 `appendix_model_proofs.tex` 极可能含本命题的既有证明，读它会破坏"独立"这一条；
按"卡住就选保守选项并记录原因"的规则，这四个文件一律未打开。若需要以它们为准，
应另起一个非盲审任务。

配套 oracle 脚本：`results/V11/route2/verify_guarantee.py`（一键复跑，
`python3 verify_guarantee.py`，全部 PASS）。所有判定用 `fractions.Fraction` 或
`sympy.Rational` 的精确有理数，float 只出现在打印里。

---

## 1. 陈述的复述与量词清单

### 1.1 用自己的话复述

**固定的对象。** 给定 ground set $N$，$|N|=n$；给定 monotone submodular
$f:2^{N}\to\mathbb R_{\ge0}$ 且 $f(\emptyset)=0$；给定 cardinality budget $K$，
满足 $1\le K\le n$。算法不能 query $f$，只能 query predictor
$\tilde f:2^{N}\to\mathbb R$，$\tilde f(\emptyset)=0$。边际增益记
$d_e(S)=f(S\cup\{e\})-f(S)$，$\tilde d_e(S)=\tilde f(S\cup\{e\})-\tilde f(S)$。
$O^{\ast}$ 是一个 optimal $K$-set，$F^{\mathrm{OPT}}=f(O^{\ast})$。

**算法。** predictive greedy 是在 $\tilde f$ 上跑的 single-step greedy：
$S^{0}=\emptyset$；对 $t=0,\dots,K-1$ 取
$e_t\in\arg\max_{e\notin S^{t}}\tilde d_{e}(S^{t})$，令 $S^{t+1}=S^{t}\cup\{e_t\}$；
输出 $T=S^{K}$。运行**恰好** $K$ 步，即使某步的最大 predicted gain 为 $0$ 也照选不误；
ties 在所有 worst-case 陈述里由对手打破。

**选择误差。** 对这一条具体轨迹，令 $M_t=\max_{e\notin S^{t}}d_e(S^{t})$，
$g_t=d_{e_t}(S^{t})$，
$$a_t=\begin{cases}M_t/g_t,&g_t>0,\\ 1,&M_t=g_t=0,\\ \infty,&g_t=0<M_t,\end{cases}
\qquad \etasel=\max\{1,a_0,\dots,a_{K-1}\}\in[1,\infty].$$

**待证的结论。** 记 $L_K(x)=1-\bigl(1-\tfrac1{xK}\bigr)^{K}$，约定 $L_K(\infty)=0$。则

$$f(T)\;\ge\;L_K(\etasel)\,f(O^{\ast})\;\ge\;\bigl(1-e^{-1/\etasel}\bigr)f(O^{\ast}).$$

若 predictor 另外还有有限的 $(\eta_u,\eta_o)$ 误差（Definition 1，convention B），
则把 $\etasel$ 换成 trajectory error $\etatr$ 或 global error $\eta=\eta_u\eta_o$
后同一个不等式仍成立，且三者有序：$L_K(\etasel)\ge L_K(\etatr)\ge L_K(\eta)$。

### 1.2 量词逐条（空洞性检验按 CLAUDE.md 执行）

| # | 量词 | 取值域 / 含义 | 去掉或取反会怎样 |
|---|---|---|---|
| Q1 | **for all** $f$ | 一切 monotone submodular、$f(\emptyset)=0$、取值 $\mathbb R_{\ge0}$ 的目标 | monotone 去掉则 $d_e(S)$ 可负，$M_t\ge g_t\ge0$ 与 Step 5 的覆盖引理同时失效；submodular 去掉则 Step 5 的 diminishing-returns 求和失效。两者都是本质的 |
| Q2 | **for all** $\tilde f$ | 一切满足 $\tilde f(\emptyset)=0$ 的 set function；**第一个不等式不对 $\tilde f$ 加任何精度假设**，$\tilde f$ 只通过它产生的那条轨迹进入结论 | 这是第一个不等式与第二段的分界：前者是 per-run 的，后者才需要 $(\eta_u,\eta_o)$ |
| Q3 | **there exists / 任取** $O^{\ast}$ | 任一 optimal $K$-set；证明只用 $|O^{\ast}|\le K$ 与 $f(O^{\ast})$ 最大，最优性本身只在把 $f(O^{\ast})$ 解释成 $F^{\mathrm{OPT}}$ 时用到 | 换成任意 $\le K$ 元集合 $A$，同一个证明给出 $f(T)\ge L_K(\etasel)f(A)$；所以"optimal"可以弱化，但陈述里保留它是为了与 $F^{\mathrm{OPT}}$ 的约定对齐 |
| Q4 | $n\ge K\ge 1$ | $1\le K\le n$（assumptions 明写） | $K>n$ 时第 $t=n$ 步没有可选元素，$\arg\max$ 为空，run 不良定义（Step 1）。$K\ge1$ 排除空 run，$K=0$ 时 $L_0$ 无定义 |
| Q5 | **deterministic** | 算法本身是确定性的；唯一的自由度是 ties，由对手打破 | 结论对**每一条**执行轨迹成立，不是对期望成立。对手 ties 不会破坏结论：$\etasel$ 是按实际轨迹算的，对手只能把 $\etasel$ 抬高，不等式自动变弱。所以"adversarial tie breaking"在这里不是空洞词，它保证结论对 argmax 的任何一种实现都成立 |
| Q6 | **query size** | 只用 single-element 的 $\tilde d_e(S)$，每步 $\le n$ 次 query，共 $\le nK$ 次；不需要 all-pairs 或大集合 query | 去掉这个限定不改变真值（结论对更强的算法仍然成立），但它刻画了 $\etasel$ 的来源：$\etasel$ 只由 single-element gains 定义 |
| Q7 | **恰好 $K$ 步** | run 不提前停止；某步 $\max_e\tilde d_e(S^t)=0$ 时仍然选一个元素 | 这是 Step 8 的归纳长度必须等于 $L_K$ 指数的原因。提前停止的变体不在本命题范围内（assumptions 明确指出它拿不到本保证） |
| Q8 | $\etasel$ 的定义域 | $[1,\infty]$，含 $\infty$；$\etasel$ 是 run 的函数，不是 instance 的函数 | $a_t=\infty$ 的情形（选中元素真增益为 $0$ 而存在更好候选）必须单列，否则 Step 4 的 $M_t\le\etasel g_t$ 在 $g_t=0$ 时不可能成立。约定 $L_K(\infty)=0$ 使该情形的结论退化为 $f(T)\ge0$ |
| Q9 | $\eta$ 的定义域 | $\eta=\eta_u\eta_o\ge1$（convention B：$\eta_u,\eta_o>0$ 但乘积 $\ge1$）；$\etatr$ 同样取 $[1,\infty]$ | $\eta<1$ 在 convention B 下不可能出现（只要存在某个 $d_e(S)>0$，band 非空即强制 $\eta_u\eta_o\ge1$，见 Step 12 注） |
| Q10 | $L_K$ 的定义域 | $x\in[1,\infty]$。这里 $xK\ge1$，故底数 $1-\frac1{xK}\in[0,1)$ | 若允许 $x<1/K$，底数为负，$K$ 为偶数时 $L_K(x)>1$，命题会失真。本命题不涉及该区域 |
| Q11 | **worst-case** | 结论是对每个 instance、每条轨迹逐点成立的下界，不是平均情形 | 这是下界方向 $\ge$，不含任何 tightness 断言。tightness 不属于本命题（第 3 节给的紧实例只是额外证据） |

---

## 2. 推导

记 $c=\dfrac1{K\,\etasel}$，$\Delta_t=f(O^{\ast})-f(S^{t})$，$t=0,\dots,K$。
以下每步注明依据。整条链的状态标签见每步末尾；总标签在第 2.4 节。

### 2.1 第一个不等式 $f(T)\ge L_K(\etasel)f(O^{\ast})$

**Step 1（run 良定义）.** 对 $t=0,\dots,K-1$，greedy 每步加入一个之前未选的元素，故
$|S^{t}|=t$。由 Q4 的 $t\le K-1\le n-1<n$ 得 $S^{t}\subsetneq N$，于是
$\{e:e\notin S^{t}\}\neq\emptyset$，$\arg\max_{e\notin S^t}\tilde d_e(S^t)$ 与
$M_t=\max_{e\notin S^t}d_e(S^t)$ 都在非空集合上取，良定义。
依据：assumptions 的 $1\le K\le n$ 与 predictive greedy 的描述。

**Step 2（符号与 $a_t\ge1$）.** $f$ monotone 给出 $d_e(S)\ge0$，故 $M_t\ge0$，$g_t\ge0$。
又 $e_t\notin S^{t}$，所以 $g_t=d_{e_t}(S^t)$ 是 $\max$ 所取的那族数中的一个，
从而 $g_t\le M_t$。于是 $g_t>0$ 时 $a_t=M_t/g_t\ge1$；另两种情形按定义分别是 $1$ 和 $\infty$。
结论：$a_t\ge1$ 对所有 $t$，故 $\etasel=\max\{1,a_0,\dots,a_{K-1}\}$ 里的那个 $1$ 是冗余的保险，
$\etasel\in[1,\infty]$。依据：assumptions（monotone）+ 选择误差定义。

**Step 3（$\etasel=\infty$ 的情形）.** 若 $\etasel=\infty$，按约定 $L_K(\infty)=0$，
待证式变成 $f(T)\ge0$，由 $f$ 取值于 $\mathbb R_{\ge0}$ 立即成立。
同理若 $f(O^{\ast})=0$，两边都是 $0$ 或左边非负，结论平凡（assumptions 明写此情形按平凡处理）。
以下设 $\etasel<\infty$。依据：Step 2、assumptions、约定 $L_K(\infty)=0$。

**Step 4（逐步的 per-step 不等式）.** 对每个 $t\in\{0,\dots,K-1\}$：
$$M_t\;\le\;\etasel\,g_t. \tag{4}$$
分三种情形（正是选择误差定义的三个分支）：
(i) $g_t>0$：$a_t=M_t/g_t\le\etasel$，两边乘 $g_t>0$ 得 (4)；
(ii) $M_t=g_t=0$：(4) 读作 $0\le0$；
(iii) $g_t=0<M_t$：此时 $a_t=\infty$，与 $\etasel<\infty$ 矛盾，本情形在 Step 3 之后不会出现。
依据：选择误差定义 + Step 3。

**Step 5（覆盖引理）.** 对任意 $S\subseteq N$，
$$f(O^{\ast})-f(S)\;\le\;\sum_{e\in O^{\ast}\setminus S}d_e(S)\;\le\;K\max_{e\notin S}d_e(S)
\quad(\text{当 }S\subsetneq N). \tag{5}$$
推导：monotone 给出 $f(O^{\ast})\le f(O^{\ast}\cup S)$。把
$O^{\ast}\setminus S=\{u_1,\dots,u_m\}$ 任意排序并 telescoping，
$$f(O^{\ast}\cup S)-f(S)=\sum_{j=1}^{m}d_{u_j}\bigl(S\cup\{u_1,\dots,u_{j-1}\}\bigr)
\;\le\;\sum_{j=1}^{m}d_{u_j}(S),$$
最后一步用 submodularity 的 diminishing-returns 形式
（$A\subseteq B$、$e\notin B$ 蕴含 $d_e(A)\ge d_e(B)$），这里
$S\subseteq S\cup\{u_1,\dots,u_{j-1}\}$ 且 $u_j$ 不在后者中。
再由每个 $u_j\notin S$ 得 $d_{u_j}(S)\le\max_{e\notin S}d_e(S)$，
以及 $m=|O^{\ast}\setminus S|\le|O^{\ast}|=K$，配合 $\max_{e\notin S}d_e(S)\ge0$（Step 2）
得到 (5)。$m=0$ 时右端求和为空 $=0$，不等式仍成立。
依据：assumptions（monotone、submodular、$|O^{\ast}|=K$）+ Step 1（$S^t\subsetneq N$）+ Step 2。

**Step 6（合并）.** 在 (5) 中取 $S=S^{t}$（$t\le K-1$，由 Step 1 合法），并用 (4)：
$$\Delta_t\;=\;f(O^{\ast})-f(S^{t})\;\le\;K\,M_t\;\le\;K\,\etasel\,g_t
\;=\;K\,\etasel\bigl(f(S^{t+1})-f(S^{t})\bigr)\;=\;K\,\etasel(\Delta_t-\Delta_{t+1}).$$
其中 $g_t=f(S^t\cup\{e_t\})-f(S^t)=f(S^{t+1})-f(S^{t})=\Delta_t-\Delta_{t+1}$。
依据：Step 4 + Step 5 + $S^{t+1}=S^t\cup\{e_t\}$。

**Step 7（改写成递推）.** $K\etasel\ge1>0$（Step 2 给 $\etasel\ge1$，Q4 给 $K\ge1$），
把 Step 6 除以 $K\etasel$ 再移项：
$$\Delta_{t+1}\;\le\;\Bigl(1-\frac1{K\etasel}\Bigr)\Delta_t\;=\;(1-c)\,\Delta_t,
\qquad c=\frac1{K\etasel}\in(0,1]. \tag{7}$$
注意 $1-c\in[0,1)$，非负，这一点在 Step 8 里要用。
依据：Step 6 + Step 2 + Q4。

**Step 8（归纳）.** 断言 $\Delta_t\le(1-c)^{t}\Delta_0$，$t=0,\dots,K$。
$t=0$ 平凡。设 $\Delta_t\le(1-c)^{t}\Delta_0$，由 (7) 及 $1-c\ge0$
（乘以非负数保持不等号方向，这里不需要 $\Delta_t\ge0$）：
$$\Delta_{t+1}\le(1-c)\Delta_t\le(1-c)\cdot(1-c)^{t}\Delta_0=(1-c)^{t+1}\Delta_0.$$
取 $t=K$：$\Delta_K\le(1-c)^{K}\Delta_0$。
依据：Step 7 + 归纳法。
`[VERIFIED-SYMBOLIC]` 展开式与 $L_K$ 的一致性由 `verify_guarantee.py` PART A 对
$K=1,\dots,8$ 用 sympy 验证：$\frac{\Delta_0-(1-c)^K\Delta_0}{\Delta_0}=1-(1-\frac1{xK})^K$。

**Step 9（结论一）.** $\Delta_0=f(O^{\ast})-f(S^{0})=f(O^{\ast})-f(\emptyset)=f(O^{\ast})$，
于是
$$f(T)=f(S^{K})=f(O^{\ast})-\Delta_K\;\ge\;f(O^{\ast})-\Bigl(1-\frac1{K\etasel}\Bigr)^{K}f(O^{\ast})
\;=\;L_K(\etasel)\,f(O^{\ast}).$$
依据：Step 8 + assumptions（$f(\emptyset)=0$）+ $L_K$ 的定义。
`[HAND-PROOF-UNREVIEWED]`（Step 1 至 Step 9 的手写链），
`[VERIFIED-EXHAUSTIVE]`（PART C：400 个随机 coverage instance，$n\le7$、$K\le n$，
精确有理数，对手 tie breaking，主不等式 $0$ 次违反；PART B：一个精确达到等号的实例）。

### 2.2 第二个不等式 $L_K(x)\ge 1-e^{-1/x}$

**Step 10.** 设 $x\in[1,\infty)$，$K\ge1$，令 $u=\frac1{xK}\in(0,1]$。
由标准不等式 $1-u\le e^{-u}$（对一切实 $u$ 成立）且 $1-u\ge0$，两边取 $K$ 次幂保序：
$$\Bigl(1-\frac1{xK}\Bigr)^{K}\le e^{-K/(xK)}=e^{-1/x}
\;\Longrightarrow\;L_K(x)=1-\Bigl(1-\frac1{xK}\Bigr)^{K}\ge1-e^{-1/x}.$$
$x=\infty$ 时左端按约定为 $0$，右端 $1-e^{0}=0$，等号成立。
把 $x=\etasel$ 代入并乘以 $f(O^{\ast})\ge0$ 得命题的第二个不等式。
依据：Step 2（$\etasel\ge1$）+ Q4 + $1-u\le e^{-u}$。
`[HAND-PROOF-UNREVIEWED]`，数值支持见 PART A：在
$K\in\{1,\dots,12\}$、$x\in\{1,1.25,\dots,10\}$ 的精确有理网格上，
$\min\bigl(L_K(x)-(1-e^{-1/x})\bigr)=3.79\times10^{-4}>0$（在 $K=12,x=10$ 处取到）。

### 2.3 $\etatr$ 与 $\eta$ 的版本及三者的序

**Step 11（$L_K$ 单调不增）.** 在 $x\in[1,\infty)$ 上
$$\frac{\mathrm d}{\mathrm dx}L_K(x)=-\Bigl(1-\frac1{xK}\Bigr)^{K-1}\cdot\frac1{x^{2}}\;\le\;0,$$
因为 $xK\ge1$ 时底数 $1-\frac1{xK}\in[0,1)$ 非负。又
$\lim_{x\to\infty}L_K(x)=0=L_K(\infty)$，故 $L_K$ 在 $[1,\infty]$ 上单调不增。
于是 $x\le y\Rightarrow L_K(x)\ge L_K(y)$。
依据：微积分 + Q10。`[VERIFIED-SYMBOLIC]`：PART A 用 sympy 对符号 $K$ 验证了该导数恒等式。

**Step 12（$\etatr$ 的定义；这里加了一个假设）.** notation 表只给了一句
"error bound restricted to the run's states"。四个输入文件没有 $\etatr$ 的公式定义，
所以本文采用下面这个最保守、也是最直接的读法，并在第 4 节登记为 added assumption：
$$\eta_u^{\mathrm{tr}}=\max\Bigl\{1,\ \max_{0\le t\le K-1}\ \max_{e\notin S^{t}}
\frac{d_e(S^{t})}{\tilde d_e(S^{t})}\Bigr\},\qquad
\eta_o^{\mathrm{tr}}=\max\Bigl\{1,\ \max_{0\le t\le K-1}\ \max_{e\notin S^{t}}
\frac{\tilde d_e(S^{t})}{d_e(S^{t})}\Bigr\},\qquad
\etatr=\eta_u^{\mathrm{tr}}\eta_o^{\mathrm{tr}},$$
其中约定 $0/0=1$（Definition 1 强制 $d=0\iff\tilde d=0$，此情形在有限误差下不产生约束），
分母为 $0$ 而分子为正时该 $\max$ 取 $\infty$。等价地：$\etatr$ 是使得
$d_e(S^{t})/\eta_u\le\tilde d_e(S^{t})\le\eta_o\,d_e(S^{t})$ 在**轨迹状态上**成立的
所有 $(\eta_u,\eta_o)$ 的乘积的下确界（两个约束解耦，故下确界之积就是积的下确界），
再以 $1$ 为下限截断。截断的理由：若某条轨迹上所有 $d_e(S^t)$ 全为 $0$，约束全空，
下确界会掉到 $0$；截断到 $1$ 与论文把 $\eta$ 下限取在 $1$ 的做法一致，而且只会让
$L_K(\etatr)$ 变小，即让结论变弱，是保守方向。
同理，global 版本 $\eta_u,\eta_o$ 是把上面的 $\max$ 取遍**所有** $S\subseteq N$、
$e\notin S$（Definition 1），$\eta=\eta_u\eta_o$。

**Step 13（$\etasel\le\etatr$）.** 设 $t\in\{0,\dots,K-1\}$，取
$e^{\ast}\in\arg\max_{e\notin S^{t}}d_e(S^{t})$，即 $d_{e^{\ast}}(S^{t})=M_t$。
predictive greedy 的选法给出
$$\tilde d_{e_t}(S^{t})\;\ge\;\tilde d_{e^{\ast}}(S^{t}).$$
由 Step 12 的 band 在状态 $S^{t}$ 上成立：
$$\tilde d_{e^{\ast}}(S^{t})\;\ge\;\frac{d_{e^{\ast}}(S^{t})}{\eta_u^{\mathrm{tr}}}
=\frac{M_t}{\eta_u^{\mathrm{tr}}},
\qquad
\tilde d_{e_t}(S^{t})\;\le\;\eta_o^{\mathrm{tr}}\,d_{e_t}(S^{t})=\eta_o^{\mathrm{tr}}g_t.$$
串起来：$\dfrac{M_t}{\eta_u^{\mathrm{tr}}}\le\eta_o^{\mathrm{tr}}g_t$，即
$$M_t\;\le\;\etatr\,g_t. \tag{13}$$
再对照 $a_t$ 的三个分支：
(i) $g_t>0$：(13) 给 $a_t=M_t/g_t\le\etatr$；
(ii) $M_t=g_t=0$：$a_t=1\le\etatr$（Step 12 的截断保证 $\etatr\ge1$）；
(iii) $g_t=0<M_t$：(13) 变成 $M_t\le0$，与 $M_t>0$ 矛盾，除非 $\etatr=\infty$；
故此时 $a_t=\infty=\etatr$。
三种情形都有 $a_t\le\etatr$，取 $\max$ 得 $\etasel\le\etatr$。
依据：predictive greedy 的 argmax 性质 + Step 12 + 选择误差定义。
注意这一步用到的只是**轨迹上**的 band，不需要 global band。
`[HAND-PROOF-UNREVIEWED]` + `[VERIFIED-EXHAUSTIVE]`（PART C 逐例检查，$0$ 次违反）。

**Step 14（$\etatr\le\eta$）.** 轨迹状态集合 $\{S^{0},\dots,S^{K-1}\}$ 是 $2^{N}$ 的子集，
所以 Step 12 里定义 $\eta_u^{\mathrm{tr}}$ 的那个 $\max$ 取遍的是定义 $\eta_u$ 的那个
$\max$ 的一个子族，故 $\eta_u^{\mathrm{tr}}\le\eta_u$；同理
$\eta_o^{\mathrm{tr}}\le\eta_o$。两者非负，相乘得 $\etatr\le\eta$。
（截断到 $1$ 不影响：$\eta=\eta_u\eta_o\ge1$ 也被同样截断，见 Q9。）
依据：Definition 1（global）+ Step 12（trajectory）。
`[HAND-PROOF-UNREVIEWED]` + `[VERIFIED-EXHAUSTIVE]`（PART C，$0$ 次违反）。

**Step 15（收束）.** 由 Step 13、Step 14 得 $\etasel\le\etatr\le\eta$，
再由 Step 11 的单调性得
$$L_K(\etasel)\;\ge\;L_K(\etatr)\;\ge\;L_K(\eta),$$
与 Step 9 串联（$f(O^{\ast})\ge0$）：
$$f(T)\;\ge\;L_K(\etasel)f(O^{\ast})\;\ge\;L_K(\etatr)f(O^{\ast})\;\ge\;L_K(\eta)f(O^{\ast})
\;\ge\;\bigl(1-e^{-1/\eta}\bigr)f(O^{\ast}),$$
最后一步用 Step 10。这正是命题第二段的内容：同一个界在 $\etasel\to\etatr\to\eta$ 的替换下
逐次变弱但仍然成立。$\square$

### 2.4 边界情形与总标签

- $K=1$：$L_1(x)=1-(1-1/x)=1/x$。若还有 $\etasel=1$，则 $c=1$，Step 8 给 $\Delta_1\le0$，
  即 $f(T)\ge f(O^{\ast})$，与 $L_1(1)=1$ 一致。这是 $1-c=0$ 的边界，Step 8 的
  "$1-c\ge0$"写成闭区间正是为了覆盖它。
- $f(O^{\ast})=0$：assumptions 规定按平凡处理；Step 9 两边同为 $0$。
- $\etasel=\infty$：Step 3。
- $\Delta_t<0$ 的可能（某步已超过 $f(O^{\ast})$，在 $|O^{\ast}|=K$ 且 $O^{\ast}$ 最优时不会发生，
  但证明不依赖这一点）：Step 8 的归纳没有用到 $\Delta_t\ge0$。

整条推导的状态：`[HAND-PROOF-UNREVIEWED]`，并带三类 oracle 支持
`[VERIFIED-SYMBOLIC]`（Step 8 的展开、Step 11 的导数）、
`[VERIFIED-EXHAUSTIVE]`（第 3 节的精确紧实例、PART C 的 400 个随机实例）。
本文件回避 CLAUDE.md 禁用的那两个断言性动词短语。

---

## 3. 数值走查：$K=3$，$\eta=3/2$

（命题里出现的 ProbeLottery 相关的 $K=2$ 走查在本陈述中不适用：prop:guarantee 不含
ProbeLottery item，故此处只做 $K=3$。）

### 3.1 曲线值（精确有理）

$$L_3(3/2)=1-\Bigl(1-\frac{1}{(3/2)\cdot3}\Bigr)^{3}=1-\Bigl(1-\frac29\Bigr)^{3}
=1-\Bigl(\frac79\Bigr)^{3}=1-\frac{343}{729}=\frac{386}{729}\approx0.529492 .$$
对照第二个不等式：$1-e^{-1/(3/2)}=1-e^{-2/3}\approx0.486583$，确实
$\frac{386}{729}\ge0.486583$，余量 $\approx0.0429$。

### 3.2 递推的逐步走查（Step 7 至 Step 9）

取 $f(O^{\ast})=1$ 归一化，$c=\frac1{K\etasel}=\frac1{4.5}=\frac29$，$1-c=\frac79$。

| $t$ | $\Delta_t$ 上界 | $f(S^{t})$ 下界 | 本步保证的增益 $g_t\ge\Delta_t/(K\etasel)$ |
|---|---|---|---|
| 0 | $1$ | $0$ | $\ge 2/9\approx0.2222$ |
| 1 | $7/9\approx0.7778$ | $\ge 2/9\approx0.2222$ | $\ge 14/81\approx0.1728$ |
| 2 | $49/81\approx0.6049$ | $\ge 32/81\approx0.3951$ | $\ge 98/729\approx0.1344$ |
| 3 | $343/729\approx0.4705$ | $\ge 386/729\approx0.5295$ | 终止 |

最后一行的 $f(S^{3})\ge386/729=L_3(3/2)$ 就是结论。

### 3.3 一个把不等式全部取等号的实例（`[VERIFIED-EXHAUSTIVE]`）

构造（weighted coverage，故 monotone submodular，$f(\emptyset)=0$）：
universe 总测度 $1$，分成三块 $B_1,B_2,B_3$，每块测度 $1/3$。
令 $r_t=\frac13\bigl(\frac79\bigr)^{t}$ 是每块在第 $t$ 步前的剩余测度。
在每块 $B_i$ 内部切出三个小片 $P_{i,t}$（$t=0,1,2$），
$\mu(P_{i,t})=\frac29 r_t$，且 $P_{i,t}$ 落在前 $t$ 个小片之外；块内剩下的部分记 $L_i$，
$\mu(L_i)=\bigl(\frac79\bigr)^{3}\cdot\frac13$。

- 元素 $o_i$（$i=1,2,3$）覆盖整块 $B_i$；$O^{\ast}=\{o_1,o_2,o_3\}$，$f(O^{\ast})=1$。
- 元素 $d_t$（$t=0,1,2$，decoy）覆盖 $P_{1,t}\cup P_{2,t}\cup P_{3,t}$，真增益在 $S^{t}$ 处为
  $3\cdot\frac29 r_t=\frac29\bigl(\frac79\bigr)^{t}$。

predictor $\tilde f$ 也是 coverage，只把 $L_i$ 的权重乘以 $c_0=\frac{100}{343}$，
小片 $P_{i,t}$ 权重不变。选 $c_0$ 是为了让 $t=0$ 时
$\tilde d_{o_i}(\emptyset)=\frac23 d_{o_i}(\emptyset)$，从而与 $\tilde d_{d_0}(\emptyset)$ 打平：
$\frac{386}{729}+\frac{343}{729}c_0=\frac{486}{729}=\frac23$ 给出 $343c_0=100$。

脚本 PART B 的精确有理输出：

```
picks (0,1,2 = decoys; 3,4,5 = o_i): [0, 1, 2]
  t=0: M_t=1/3    g_t=2/9     a_t=3/2
  t=1: M_t=7/27   g_t=14/81   a_t=3/2
  t=2: M_t=49/243 g_t=98/729  a_t=3/2
eta^sel = 3/2
f(T) = 386/729 = 0.529492   f(O*) = 1
L_3(3/2) = 386/729
tightness  f(T) == L_3(3/2) f(O*) : True
trajectory factors: eta_u^tr=49/22, eta_o^tr=1, eta^tr=49/22 = 2.227273
global factors    : eta_u=343/100, eta_o=1, eta=343/100 = 3.430000
ordering eta^sel <= eta^tr <= eta : True
L_3 values: 0.529492 >= 0.385137 >= 0.264130
```

读法：
- $t=0$ 是 tie（$\tilde d_{o_i}=\tilde d_{d_0}=2/9$），对手把 tie 打向 decoy，这正是 Q5 说的
  adversarial tie breaking 在起作用；$t=1,2$ 则是严格胜出，不依赖 tie。
- 三步的 $a_t$ 恒等于 $3/2$，$\etasel=3/2$，且 $f(T)=L_3(3/2)f(O^{\ast})$ 精确取等，
  说明 Step 4 至 Step 9 的每一个不等号在这条轨迹上都可以同时收紧，本命题的下界在
  $\etasel$ 这个参数上不可改进（这条只是本实例的 `[VERIFIED-EXHAUSTIVE]` 观察，
  并不是关于 $\rho_K$ 的任何断言）。
- 同一实例上 $\etasel=3/2<\etatr=49/22<\eta=343/100$，
  对应 $L_3$ 值 $0.5295>0.3851>0.2641$，即 Step 15 的序在这里是严格的：
  换成 $\etatr$ 或 $\eta$ 会实打实地损失界值，这说明第二段的三个版本不是同一句话的重复。

### 3.4 随机压力测试（PART C，`[VERIFIED-EXHAUSTIVE]`）

400 个随机 coverage instance，$n\in[2,7]$、$K\in[1,n]$、atom 数 $\le8$，
一半用与 $f$ 无关的随机 predictor（此时 global $\eta$ 常为 $\infty$），
一半用同支撑扰动权重的 predictor（198 个实例的 global $\eta$ 有限）。
全部用 `Fraction` 精确计算，tie 按"predicted gain 最大者中真增益最小者"打破（对手方向）。
结果：主不等式违反 $0$ 次，序关系 $\etasel\le\etatr\le\eta$ 与
$L_K(\etasel)\ge L_K(\etatr)\ge L_K(\eta)$ 违反 $0$ 次，
$f(T)\ge L_K(\eta)f(O^{\ast})$ 违反 $0$ 次。

---

## 4. 没能闭合的步骤，以及补加的假设

1. **`[ASSUMPTION-ADDED]` $\etatr$ 的形式定义。** 四个输入文件里 $\etatr$ 只有 notation 表
   的一句话 "trajectory error (error bound restricted to the run's states)"，没有公式。
   本文按 Step 12 的写法定义它（Definition 1 的 band 只在 $S^{0},\dots,S^{K-1}$ 上要求，
   两个因子各取最紧值再相乘，并以 $1$ 截断）。若论文的正式定义把状态集合取成
   $S^{0},\dots,S^{K}$（含终态 $S^{K}$），Step 13 与 Step 14 都不受影响：Step 13 只用
   $t\le K-1$ 的状态，多加一个状态只会让 $\etatr$ 变大或不变，$\etasel\le\etatr$ 仍成立；
   Step 14 的子族论证同样不变。所以这个不确定性不影响结论方向，但定义的字面形式需要与
   正文核对。
2. **`[ASSUMPTION-ADDED]` 全零轨迹时的截断。** 若某条轨迹上所有 $d_e(S^{t})=0$，
   band 约束为空，$\eta^{\mathrm{tr}}_u,\eta^{\mathrm{tr}}_o$ 的下确界会退化到 $0$。
   本文统一截断到 $1$（与 Definition 1 verbatim 版把两个因子下限取在 $1$ 一致）。
   截断方向使 $L_K(\etatr)$ 更小，是保守方向。此时 $\etasel=1$，第一个不等式仍是
   $f(T)\ge L_K(1)f(O^{\ast})$，而该轨迹上 $M_t\equiv0$ 配合 Step 5 给出
   $f(O^{\ast})\le f(S^{0})=0$，两边都是 $0$，无矛盾。
3. **未闭合：$|O^{\ast}|=K$ 与 $|O^{\ast}|\le K$。** assumptions 说 $O^{\ast}$ 是
   optimal $K$-set，Step 5 只用 $|O^{\ast}\setminus S|\le K$。若论文别处允许
   $|O^{\ast}|<K$（例如 $f$ 在 $<K$ 元处已达最大），结论不变。这是一个记号层面的
   宽松处，不是 gap。
4. **未闭合：$\tilde f$ 的取值域。** assumptions 只要求
   $\tilde f:2^{N}\to\mathbb R$（允许负值与非单调），Definition 1 又说"all predicted gains
   are nonnegative"。第一个不等式（Step 1 至 Step 9）完全不用这条，任何 $\tilde f$ 都行；
   Step 13 用到的是 band 而不是非负性，也不受影响。故两处措辞的张力不影响本命题，
   但本文记录在此。
5. **未闭合（范围外）：tightness。** 第 3.3 节给了一个精确取等的实例，
   但本命题只断言 $\ge$。$\rho_K(\eta)$ 与 $L_K$ 的关系不在本任务范围，未做任何检查。
6. **未打开的文件。** 上游附带的 `HANDOFF_2026-09-18.md`、
   `HANDOFF_ADDENDUM_2026-09-18.md`、`appendix_model_proofs.tex`、
   `J8_claude_spotcheck.py` 按盲证隔离要求未读（理由见开头）。
   若其中对 $\etatr$ 有正式定义，第 4.1 条的不确定性应以那里为准。

---

## 5. 读过的文件

- `/home/user/sub-modular-optimization/results/V11/inputs/definition1.md`
- `/home/user/sub-modular-optimization/results/V11/inputs/assumptions.md`
- `/home/user/sub-modular-optimization/results/V11/inputs/notation.md`
- `/home/user/sub-modular-optimization/results/V11/inputs/statement_guarantee.md`
- `/home/user/sub-modular-optimization/CLAUDE.md`（会话规则，自动载入上下文，非数学输入）

本次写入的文件（均为新建，未修改任何既有文件）：
- `/home/user/sub-modular-optimization/results/V11/route2/guarantee.md`（本文件）
- `/home/user/sub-modular-optimization/results/V11/route2/verify_guarantee.py`（oracle 脚本）
