# 量词审计（criteria A 与 E）：cor:limit / 台账 T9（TASKS11 Q4c，正文 Corollary，环境 `corollary`）

本文件只做两件事：A 项逐量词比对正文环境与台账卡；E 项建立量词审计表，把陈述里的每个量词与形容词
落到路线甲证明的具体位置，落不上的记 GAP。

范围与纪律：不修改任何已有文件，不运行 git。本文件自身的算术用 sympy 与 `fractions.Fraction` 精确核对
（结果见 §5），浮点只出现在打印里。状态标签按 CLAUDE.md：[VERIFIED-SYMBOLIC] [VERIFIED-LP]
[VERIFIED-EXHAUSTIVE] [HAND-PROOF-UNREVIEWED] [CONJECTURE] [FAILED]。读过的文件见 §6。

HANDOFF_ADDENDUM 的 B.1 只重编号 Theorem 1/2/3 与 thm:ceiling 的降级，本条目不在该清单内：
环境仍是 `corollary`，label 仍是 `cor:limit`，与 `results/V11/statements.md` 第 202 至 205 行的
元数据行一致。

---

## 1. Criterion A：正文陈述与台账陈述的逐量词比对

### 1.1 三段原文

正文：`paper/sections/results.tex` 第 523 至 529 行，environment `corollary`，label `cor:limit`，
标题 "Limit in $K$"，位于 `\subsection{Asymptotics}\label{sec:asymptotics}`（第 521 行）之下。
环境**之后**第 530 至 534 行是一段非环境正文（"Quantitatively, for fixed $\eta\ge1$ ..."），
给出 $\rho_K=1-e^{-1/\eta}+c(\eta)/K+O(1/K^{2})$、$c(\eta)=e^{-1/\eta}(2\eta-1)/(2\eta^{2})$、
$c_U=c$ 与 $c_L=e^{-1/\eta}/(2\eta^{2})$；第 535 至 549 行是状态注释。

矩阵输入：`results/V11/statements.md` 第 217 至 223 行的 LaTeX 块与
`results/V11/inputs/statement_limit.md` 第 6 至 12 行。三份逐字符相同（§5 第 10 条，字符串比对）。

台账：`THEOREM_LEDGER.md` 第 205 至 228 行，卡 `## T9 cor:limit`。卡的"陈述（最终状态）"行
（第 206 至 209 行）为：

> 固定 η，L_K、ρ_K、U_K → 1−e^{−1/η}；ρ_K 关于 K **非增**，K ≤ ⌊η⌋ 平台 1/η，K ≥ ⌊η⌋ 起严格递减
> （[VERIFIED-SYMBOLIC，conditional on thm:exact]，证明已迁入 app:asymptotics，J5H5）；一阶展开
> ρ_K = 1−e^{−1/η} + c(η)/K + O_η(1/K²)，c(η) = e^{−1/η}(2η−1)/(2η²)（不随 ⌊η⌋ 分段；
> c_L = e^{−1/η}/(2η²)、c_U = c，同样已迁入附录）。

卡里另有独立条目：状态行（210 至 212）、渐近展开（213 至 217，含"固定 η ≥ 1"与 1/K² 系数 d(η,m)）、
单调性（218 至 221，含"从上方收敛"）、副产品（222 至 223）、禁止声称（224 至 225）、历史（226 至 228）。

### 1.2 逐项对照

| 量词 / 形容词 | 正文（results.tex 523-529） | 台账（T9 陈述行 206-209） | 判定 |
|---|---|---|---|
| "for fixed $\eta$"（η 先取定，K 后动） | "For fixed $\eta\ge1$" | "固定 η" | 一致 |
| η 的定义域 $\eta\ge1$ | 写在环境内 | 陈述行只写"固定 η"，$\eta\ge1$ 出现在同卡第 213 行的渐近展开条 | **差异 D1**（同卡内可补齐，但陈述行本身缺定义域） |
| 收敛对象：$L_K$ | 有 | 有 | 一致 |
| 收敛对象：$\rho_K$ | 有 | 有 | 一致 |
| 收敛对象：$U_K$ | 环境内**没有**（$U_K$ 只在环境后第 533 行以 1/K 系数的身份出现） | 陈述行写 "L_K、ρ_K、U_K → 1−e^{−1/η}" | **差异 D2** |
| 极限值 $1-e^{-1/\eta}$ | 有 | 有 | 一致 |
| 极限量词 $K\to\infty$ | "as $K\to\infty$" | "→"（同义） | 一致 |
| "$L_K$ is monotone in $K$" | 有，方向未写 | **没有 L_K 的单调子句** | **差异 D3** |
| "$\rho_K$ is non-increasing in $K$" | 有 | "ρ_K 关于 K 非增" | 一致 |
| 平台 "equal to $1/\eta$ for $K\le\lfloor\eta\rfloor$" | 有 | "K ≤ ⌊η⌋ 平台 1/η" | 一致 |
| "strictly decreasing from $K\ge\lfloor\eta\rfloor$ on" | 有 | "K ≥ ⌊η⌋ 起严格递减" | 一致 |
| "so the limit is approached from above" | 有，写在环境内 | 陈述行没有，第 218 行单调性条写"从上方收敛" | **差异 D4**（同卡内可补齐） |
| 一阶展开 $\rho_K=1-e^{-1/\eta}+c(\eta)/K+O_\eta(1/K^2)$ 与 $c(\eta)$ | 环境**之外**（第 530 至 532 行） | 写在陈述行内 | **差异 D5**（位置差，内容一致） |
| $c$ 不随 $\lfloor\eta\rfloor$ 分段、$c_L$、$c_U$ | 环境之外（第 532 至 534 行，$c_L$ 有、"不随 ⌊η⌋ 分段"无） | 写在陈述行内（三项齐） | **差异 D6** |
| 状态与条件性（conditional on thm:exact） | 环境内没有，只在第 535 至 549 行的注释里 | 写进陈述行括号内 | **差异 D7**（呈现层，非量词） |
| $K$ 的定义域（$K\ge2$ 或 $K\ge1$） | 两边都不出现 | 两边都不出现 | 一致（共同缺口，进 E 表 GAP-1） |
| ground-set size $n$ | 两边都不出现 | 两边都不出现 | 一致（共同缺口，进 E 表 GAP-2） |
| deterministic / randomized、expectation、fixed random string | 两边都不出现 | 同 | 一致（本条目无随机子句） |
| 查询次数、查询集合大小、arbitrary query access | 两边都不出现 | 同 | 一致（本条目不是查询类结果） |
| adversarial ties、fixed K steps、$f(\emptyset)=0$、OPT>0 | 两边都不出现，继承 $\rho_K$ 的定义 | 同 | 一致（隐含量词进 E 表） |
| $O_\eta(1/K^2)$ 对 η 的一致性 | 环境外用 $O(1/K^{2})$，注释里明写不声称一致性 | 陈述行用 $O_\eta(1/K^2)$，禁止声称条（224 行）明写不一致 | 一致（两边都不声称，正文外层符号略弱，见 N2） |

### 1.3 A_diffs 与判定

两张清单**不重合**，因此 **A_match = false**。差异七条（D1 至 D7），按承重程度排序：

1. **D2（$U_K$）**：台账陈述行把 $U_K\to1-e^{-1/\eta}$ 写进结论，正文 corollary 环境只讲 $L_K$ 与 $\rho_K$。
   正文里 $U_K$ 只在环境后一句以"同一个 1/K 系数"的身份出现，没有极限断言。矩阵若只抄环境体，
   台账的三条收敛会缩成两条。这也是 E 表第 25 行的 GAP-3。
2. **D3（$L_K$ 的单调性）**：正文有"$L_K$ is monotone in $K$"，台账陈述行完全没有这个子句，
   同卡其他条目也没有。方向上正文还漏了：附录（第 1378 至 1380 行）证的是 $L_K$ **递减**、从上方收敛，
   正文只写 monotone。按 CLAUDE.md 的空洞性检验，monotone 去掉方向后句子的内容会变（递增也叫 monotone），
   说不清就不该用；本审计独立核到 $L_K$ 在 $\eta\ge1$ 上对 $K$ 严格递减（§5 第 6 条）。
3. **D5 + D6（一阶展开与三个系数）**：台账把 $c(\eta)$、$c_L$、$c_U$、"不随 ⌊η⌋ 分段"写进陈述，
   正文放在环境外的一段散文里，且"不随 ⌊η⌋ 分段"这一句正文没有。内容本身一致（§5 第 2 条核对过）。
4. **D1（η 的定义域）**：正文 "For fixed $\eta\ge1$"，台账陈述行只写"固定 η"。$\eta\ge1$ 在同卡第 213 行有，
   但陈述行单独被抄进矩阵时会丢掉定义域，而 $\eta\ge1$ 是承重的（$u=1/(\eta K)\in(0,1]$、
   $x=1/\eta\in(0,1]$ 两处都要它，见 E 表第 2 行）。
5. **D4（from above）**：正文写在结论末尾，台账陈述行没有，第 218 行有。同卡可补齐。
6. **D7（条件性）**：台账把 [VERIFIED-SYMBOLIC, conditional on thm:exact] 写进陈述行，正文环境无任何
   条件标记（按写作规则正文不出现状态标签，这是正常的），只在注释第 535 至 549 行。记录为呈现层差异。

补充记录（不计入 A_diffs）：

- **N1**：正文 corollary 体内出现的 $L_K$、$\rho_K$ 都是环境外定义（$L_K$ 在 `prop:guarantee`，
  results.tex 第 79 至 90 行；$\rho_K$ 在 `model.tex` 第 70 至 78 行与 `thm:exact`）。矩阵栏若只抄环境体，
  两个符号都无定义。与 `results/V11/audit/exact.md` 的 N1 是同一类问题。
- **N2**：台账用 $O_\eta(1/K^2)$（下标显式说明常数依赖 η），正文用 $O(1/K^{2})$，靠注释说明不声称一致性。
  两者不矛盾，正文的符号弱一点。

---

## 2. Criterion E：量词审计表（落到路线甲）

路线甲 = `paper/sections/appendix_proofs.tex` 的
`\subsection{Asymptotics (Corollary~\ref{cor:limit})}\label{app:asymptotics}`（第 1373 至 1459 行），
脚本 `results/H_B_asymptotic.py`（sections 0 至 6）与 `results/N5_asymptotics.py`（hardness 里的同型极限）。

app:asymptotics 的段落锚点（行号）：无名首段 `Fix $\eta\ge1$.`（1375，内含 $L_K$ 的极限与单调、
$\rho_K=\min_jV_j$ 的极限）、状态注释（1393 至 1400）、`\paragraph{The $1/K$ expansion.}`（1402）、
其状态注释（1422 至 1426）、`\paragraph{Monotonicity of $\rho_K$ in $K$.}`（1428）、
其状态注释（1447 至 1455）、末句 "The limit identities of this proof are machine-checked ...
\texttt{results/N5\_asymptotics.py}"（1457 至 1458）。

状态列：**OK** = 路线甲有明确处理；**OK(隐含)** = 有处理但无独立句子；**部分** = 有处理但缺一步或缺定义；
**GAP** = 路线甲没有对应位置；**N/A** = 本陈述没有这个量词。

| 量词 / 形容词 | 处理位置（file + paragraph） | 状态 |
|---|---|---|
| 1. "for fixed $\eta$"（量词顺序：先 η 后 K） | app:asymptotics 第 1375 行 "Fix $\eta\ge1$"；第 1381 行 "fix $\eta$ and let $K$ grow"；第 1403 行 "Fix $\eta\ge1$ and write $m=\lfloor\eta\rfloor$"；单调性段把 η 当参数、对 K 求导（1433 至 1437） | OK |
| 2. 定义域 $\eta\ge1$ | 同第 1375 行。消费点三处：$L_K$ 段要 $u=1/(\eta K)\in(0,1]$（1375 至 1377）与 $x=1/\eta\in(0,1]$（1378 至 1380）；单调性证书的坐标变换 $m=1+w$、$w\ge0$，即 $\lfloor\eta\rfloor\ge1$（`results/H_B_asymptotic.py` section 5 的 `NumSub.subs({ms: 1 + w})`） | OK |
| 3. $K\to\infty$：$L_K\to1-e^{-1/\eta}$ | 第 1375 至 1378 行："the substitution $u=1/(\eta K)\in(0,1]$ and the expansion $\ln(1-u)=-u-u^{2}/2-\dots$ give $K\ln(1-\frac{1}{\eta K})=-\frac1\eta+O(1/K)$, so $L_K(\eta)\to1-e^{-1/\eta}$" | OK（状态 [HAND-PROOF-UNREVIEWED]，注释第 1393 行；本审计另用 sympy 取极限核对，§5 第 1 条 [VERIFIED-SYMBOLIC]） |
| 4. $K\to\infty$：$\rho_K\to1-e^{-1/\eta}$ | 第 1381 至 1392 行：$\rho_K=\min_jV_j$ 的 active index $j=K-\lfloor\eta\rfloor$，$\ln q^{j}=-j/k_1+O(j/k_1^{2})$，$j/k_1\to1/\eta$，$1-\frac{K-j}{K\eta}\to1$，"Hence $\rho_K(\eta)=V_j(\eta)\to1-e^{-1/\eta}$" | OK（[HAND-PROOF-UNREVIEWED]，第 1393 行；active branch 的极限本审计符号核对，§5 第 1 条） |
| 5. 两条曲线并列（"both ... and ..."） | 两段分别独立处理（1375 至 1380 给 $L_K$，1381 至 1392 给 $\rho_K$），不互相引用 | OK |
| 6. "$L_K$ is monotone in $K$"（方向未写） | 第 1378 至 1380 行："moreover $(1-\frac{x}{K})^{K}$ increases in $K$ for $x\in(0,1]$, so the convergence of $L_K(\eta)$ is monotone from above" | **部分**：附录给的是递减（从上方），陈述里的 monotone 无方向，空洞性检验不过（见 §1.3 第 2 条）。本审计核到 $\eta\in\{1,5/4,3/2,2,5/2,3,4,13/2,7\}$、$K=1..79$ 上严格递减，§5 第 6 条 [VERIFIED-EXHAUSTIVE]（有理网格） |
| 7. "$\rho_K$ is non-increasing in $K$"（对每个 $K$） | `\paragraph{Monotonicity of $\rho_K$ in $K$.}`（1428 至 1446）：平台段 + 首跌 + $\partial\log P/\partial K>0$ 的证书；数值侧 `results/H_B_asymptotic.py` section 4（$K=2..400$、7 个 η、精确有理差分、0 个负号，零差只出现在 $K<\lfloor\eta\rfloor$） | OK（证书 [VERIFIED-SYMBOLIC conditional on thm:exact]；连续导数到离散差分的装配 [HAND-PROOF-UNREVIEWED]，注释第 1451 至 1454 行） |
| 8. 平台 "equal to $1/\eta$ for $K\le\lfloor\eta\rfloor$" | 第 1429 至 1430 行 "For $K\le\lfloor\eta\rfloor$, $\rho_K(\eta)=1/\eta$ (the plateau of Theorem~\ref{thm:exact})"，来源是 thm:exact 的 "$\rho_K(\eta)=1/\eta$ exactly when $\eta\ge K$" | OK（对 $K\ge2$；$K=1$ 见第 12 行 GAP-1）。本审计核到 $2\le K\le\lfloor\eta\rfloor$ 时 $\rho_K=1/\eta$，§5 第 3 条 |
| 9. "strictly decreasing from $K\ge\lfloor\eta\rfloor$ on" 的第一步（$K=\lfloor\eta\rfloor\to\lfloor\eta\rfloor+1$） | 第 1430 至 1432 行 "the first step off the plateau is a strict drop by $(K-\eta)/(K\eta k_1)>0$ at $K=\lfloor\eta\rfloor+1>\eta$"；恒等式 $V_0-V_1=(K-\eta)/(K\eta k_1)$ 由 `results/H_B_asymptotic.py` section 5 (f) 符号验证 | OK（本审计另用精确有理数核到 $\rho_{\lfloor\eta\rfloor}-\rho_{\lfloor\eta\rfloor+1}$ 等于该式，§5 第 4 条） |
| 10. 同一子句的其余步（$K\ge\lfloor\eta\rfloor+1$） | 第 1432 至 1446 行：$\rho_K=1-P(K)$、$\partial\log P/\partial K$ 恒等式、$-\log(1-1/x)$ 的逐项尾界、$s=t/(1+t)$ 后的非负系数证书（分子 84 项、常数 14；分母 165 项、常数 48）。证书的定义域图恰是 $K=m+1+u$（$u\ge0$），即 $K\ge\lfloor\eta\rfloor+1$，与第 9 行的首跌拼起来覆盖 "from $K\ge\lfloor\eta\rfloor$ on" | OK（拼接是两段式，附录写清楚了；[VERIFIED-SYMBOLIC conditional on thm:exact]，唯一手写步是尾界） |
| 11. 整数 η 处的分支切换 | 极限段第 1384 至 1385 行 "either endpoint value at an integer $\eta$"；单调段第 1445 至 1446 行 "Integer $\eta$ corresponds to the endpoint $s=0$ and is included" | OK（注释第 1452 至 1454 行仍把"含整数 η 的分支切换"的离散化装配记为 [HAND-PROOF-UNREVIEWED]） |
| 12. 隐含：$K$ 的定义域（$K\ge2$，以及 $K=1$） | 路线甲**没有任何位置**写 K 的下端。$\rho_K$ 的闭式来自 thm:exact，而 thm:exact 的前提是 $K\ge2$（results.tex 第 192 行）。$1\le\eta<2$ 时 $\lfloor\eta\rfloor=1$，平台子句"$K\le\lfloor\eta\rfloor$"只谈 $K=1$，而"从 $K\ge\lfloor\eta\rfloor=1$ 起严格递减"要用到 $\rho_1$；$\rho_1=1/\eta$ 的三行链在台账 T10b 的"K=1 情形"条（THEOREM_LEDGER.md 第 261 至 264 行），状态 [HAND-PROOF-UNREVIEWED]，不在 app:asymptotics 也不在 T9 卡 | **GAP-1** |
| 13. 隐含：ground-set size $n$，以及 $K\to\infty$ 下的 $n$ | 路线甲全篇不出现 $n$。$\rho_K$ 与 $n$ 的关系由 `rem:exact-n`（results.tex 第 208 至 215 行，$\rho_{n,K}=\rho_{2K,K}$ 对每个 $n\ge2K$，[HAND-PROOF-UNREVIEWED]）承担；"$K\to\infty$"因此隐含要求 ground set 随 K 增长（$n\ge2K\to\infty$），这一点没有任何位置写出 | **GAP-2** |
| 14. 隐含：$\rho_K=\min_jV_j$（整条结论 conditional on thm:exact） | 第 1381 行 "For $\rho_K=\min_jV_j$"；三处状态注释（1393、1422 至 1426、1447 至 1454）都写明 conditional on thm:exact；台账禁止声称条（第 225 行）明写"不得把本卡当对 $\rho_K=\min_jV_j$ 的独立确认" | OK（条件性已到位） |
| 15. 隐含：$L_K$ 的定义与"在全局 η 处取值" | $L_K(x)=1-(1-\frac{1}{xK})^{K}$ 定义在 `prop:guarantee`（results.tex 第 83 行）与 notation 表；路线甲第 1375 至 1377 行直接代 $x=\eta$ | OK（口径正确：cor:limit 谈的是全局 η 轴上的曲线，与 T6/T9 的"$\rho_K$ 只对全局 η"一致） |
| 16. 隐含：adversarial tie breaking | 路线甲不出现；由 $\rho_K$ 的定义继承（`model.tex` 第 70 至 74 行 "ties broken adversarially in all worst-case statements"，thm:exact 环境 "under adversarial tie breaking"） | OK(隐含)（路线甲只操作闭式，不重建实例，故不需要重述） |
| 17. 隐含：fixed $K$ steps（不提前停） | 同上，`model.tex` 第 70 至 74 行 "The run always executes exactly $K$ steps" | OK(隐含) |
| 18. 隐含：$f$ monotone submodular、$f(\emptyset)=0$、$|S|\le K$ | 同上，`assumptions.md` 与 thm:exact；路线甲不碰实例 | OK(隐含) |
| 19. 隐含：OPT > 0 | `assumptions.md` 的约定"$f(O^{\ast})=0$ 时每个比值陈述平凡成立"；路线甲不出现 | OK(隐含) |
| 20. 隐含：拆分 $(\eta_u,\eta_o)$ 与乘积 $\eta$ | 陈述与路线甲只出现 $\eta$；$L_K$、$V_j$、$U_K$ 三个闭式都只含 $\eta$，拆分不进入 | OK（不承重：本条目是闭式的渐近性质，拆分在 thm:exact 的达到方向才出现） |
| 21. 隐含：$K\ge2$ 时 $q\in(0,1)$（$q^{j}\to0$ 的前提） | 第 1386 至 1389 行的 $\ln q^{j}$ 展开默认 $q\in(0,1)$；该事实在 app:exact 第 607 行 "Note $k_1\ge K\ge2$, so $q\in(0,1)$"，路线甲未重述 | OK(隐含)（与第 12 行同源：$K\ge2$ 没有在本 subsection 出现） |
| 22. "so the limit is approached from above"（$\rho_K$ 侧） | 路线甲没有独立句子，由第 7 至 10 行的非增加第 4 行的极限推出；`results/H_B_asymptotic.py` section 6 打印 "c(eta) > 0 for every eta >= 1 (factor 2eta-1 > 0): rho_K approaches 1-e^(-1/eta) from above" | OK(隐含)（本审计核到 $K=2..59$、9 个 η 上 $\rho_K$ 与 $U_K$ 都严格大于极限，§5 第 7 条） |
| 23. "approached from above"（$L_K$ 侧） | 第 1379 至 1380 行 "the convergence of $L_K(\eta)$ is monotone from above" | OK |
| 24. 台账多出的一阶展开与 $c(\eta)$、$c_L$、$c_U$、"不随 ⌊η⌋ 分段" | `\paragraph{The $1/K$ expansion.}`（1402 至 1421）：active branch $V_{K-m}$ 的 $\varepsilon=1/K$ 展开、"the $1/K$ coefficient $c(\eta)$ does not depend on $m$"、$c_L$ 与 $c_U=c$、两条差的量级；脚本 `results/H_B_asymptotic.py` section 2（sympy series，含 $\partial c/\partial m=0$）、section 3（Richardson 对照）、section 6（$c_L$、$c_U$） | OK（[VERIFIED-SYMBOLIC conditional on thm:exact]；Taylor 余项装配 [HAND-PROOF-UNREVIEWED]，注释第 1425 行。本审计独立重算 $c(\eta)$ 与 $\partial c/\partial m=0$，§5 第 2 条） |
| 25. 台账多出的 $U_K\to1-e^{-1/\eta}$ | 路线甲**没有 $U_K$ 的极限句**。$U_K$ 只在 1/K 展开段以 "The same expansion for $L_K$ and $U_K$ yields the companion coefficients ... $c_U=c$"（第 1416 至 1418 行）出现；`results/H_B_asymptotic.py` section 6 的 `lin_coeff` 只提取 $\varepsilon$ 的系数，不检查零阶项 | **GAP-3（部分）**：结论为真（本审计 sympy 取极限，§5 第 1 条 [VERIFIED-SYMBOLIC]），但路线甲与脚本都没有落点；台账陈述行写了这一条 |
| 26. $O_\eta(1/K^{2})$ 对 η 的一致性 | 明确不声称：附录注释第 1425 至 1426 行 "uniformity of the remainder in eta is not claimed (ledger T9)"；results.tex 第 547 至 548 行同；台账禁止声称条第 224 行同 | OK（禁止声称三处一致） |
| 27. 台账状态行说的证明路线（sandwich $L_K\le\rho_K\le U_K$ 加两侧极限） | 路线甲**不走 sandwich**，走 active branch 的直接展开（第 1381 至 1392 行）。sandwich 的两端另有出处：$L_K\le\rho_K$ 来自 `prop:guarantee`（全局 η 代入），$\rho_K\le V_{K-1}<U_K$ 来自 `rem:exact-gap`（results.tex 第 371 至 375 行）加 T6 副产品，两者都不在 app:asymptotics | **部分（记录）**：不是 GAP，两条路线各自自足，但台账状态行描述的依据与附录实际写的证明不是同一条，读卡的人会去附录找 sandwich 而找不到。本审计核到 $L_K\le\rho_K\le U_K$ 在 $K=2..59$、9 个 η 上成立（§5 第 8 条） |
| 28. deterministic / randomized 量词、fixed random string、expectation | 陈述里没有随机子句，台账卡也没有；$\rho_K$ 是确定性算法 predictive greedy 的最坏比，唯一的非确定性是 tie，由 adversary 解 | **N/A** |
| 29. 查询次数、查询集合大小、arbitrary query access、$|S|\le K$、$\le nK$ 次 | 陈述里没有这些形容词；它们属于 T8（thm:ceiling）、T10c（thm:linear-exact）、T10（thm:hardness） | **N/A** |
| 30. "error exactly $\eta$" / "at most $\eta$" | 陈述里没有实例层的误差形容词（本条目只谈三条闭式曲线，实例层的量词在 thm:exact 内） | **N/A** |

### 2.1 GAP 汇总

- **GAP-1（$K$ 的定义域，最承重）**：陈述、台账卡、路线甲三处都没有写 $K$ 的下端。$\rho_K$ 的闭式只对
  $K\ge2$ 成立（thm:exact 的前提），而平台子句"$K\le\lfloor\eta\rfloor$"在 $1\le\eta<2$ 时只覆盖 $K=1$，
  严格递减子句"从 $K\ge\lfloor\eta\rfloor$ 起"在同一区间要用 $\rho_1$。$\rho_1=1/\eta$ 只在台账 T10b 的
  "K=1 情形"条（第 261 至 264 行）有三行手证（[HAND-PROOF-UNREVIEWED]），不在本卡也不在 app:asymptotics。
  保守处理：不动正文，只记录；矩阵里本条目的 K 量词应标成"未写，$\rho_K$ 的 $K\ge2$ 由 thm:exact 继承，
  $K=1$ 另有出处且未复核"。
- **GAP-2（$n$ 量词与 $K\to\infty$ 的相容性）**：app:asymptotics 全篇不含 $n$。$\rho_K$ 作为与 $n$ 无关的量
  只在 $n\ge2K$ 时成立（`rem:exact-n`，[HAND-PROOF-UNREVIEWED]，且该 remark 的正文注释自述是本地重构）。
  因此"$K\to\infty$"隐含 ground set 同时增长，没有任何位置写出这一点。与 `results/V11/audit/exact.md`
  的 GAP-1 同源，本条目是它的下游。
- **GAP-3（$U_K$ 的极限没有落点）**：台账陈述行把 $U_K\to1-e^{-1/\eta}$ 与另外两条并列，但路线甲只给
  $U_K$ 的 1/K 系数，脚本 section 6 也只提取一阶系数。结论为真（§5 第 1 条 [VERIFIED-SYMBOLIC]），
  缺的是一句话与一个 oracle 项。正文环境不含 $U_K$，所以这条只影响台账与矩阵的一致性。
- **部分-1（表第 6 行）**：陈述里的 "$L_K$ is monotone in $K$" 没有方向，附录证的是递减、从上方收敛。
  空洞性检验不过。证据充分（§5 第 6 条），缺的是正文一个词。
- **部分-2（表第 27 行）**：台账状态行写的证明依据是 sandwich，附录写的是 active branch 直接展开。
  两条都成立，但卡与附录的指向不一致。
- 次要记录（不计入 GAP）：表第 16 至 21 行是 OK(隐含)，都属于 $\rho_K$ 定义层的继承，路线甲只操作闭式，
  不重建实例，这一点是合理的；表第 11 行的整数 η 分支切换在附录有句子，但其离散化装配仍是
  [HAND-PROOF-UNREVIEWED]。

---

## 3. TASKS11 的两个条件问题

两个都不适用于本条目，按要求明确记录：

- **"fixed random string" 量词是否在陈述里**：这是 thm:ceiling（T8）的专项问题。cor:limit 没有随机段落，
  正文与台账都不含 randomized 子句，见 E 表第 28 行。thm:ceiling 的答案在
  `results/V11/audit/ceiling.md` §3。
- **$n\ge4K^{5}$ 能否收紧到约 $K^{3}(K-1)^{2}/2+K^{2}$**：这是 thm:linear-exact（T10c）的专项问题，
  依赖 `app:greedybudget` 的计数链（`paper/sections/appendix_proofs.tex` 第 1701 行起）。
  本条目的 $n$ 量词是 GAP-2 里的 $n\ge2K$，与那条计数链无关。本文件不回答该问题，也没有读那条计数链。

---

## 4. 与台账其他卡的接口（只作参照，不计入 E 表）

- 本条目整条 conditional on T6（thm:exact）。台账禁止声称条（第 225 行）写明：不得把本卡结论当作对
  $\rho_K=\min_jV_j$ 的独立确认。E 表第 14 行已把这条记进去。
- $U_K-\rho_K=c'(\eta)/K^{2}+O(1/K^{3})$ 在台账 T10b 的 Gap 条，状态 "conditional on thm:exact 与 T9 的
  H-B 展开"；也就是说 T10b 的那条依赖本卡，本卡的 GAP-3 不影响它（它用的是 $c_U=c$ 这一条，有落点）。
- 台账禁止声称条还有一条"由单调推凸凹（未查）"。正文与附录都没有凸凹断言，本审计确认无越界。

---

## 5. 本文件自身算术的核对

临时脚本（不入库，位于本次会话的 scratchpad）用 sympy 与 `fractions.Fraction` 做了十条精确核对，
全部通过，浮点只出现在打印里。η 网格取 $\{1,\,5/4,\,3/2,\,2,\,5/2,\,3,\,4,\,13/2,\,7\}$（含整数与
非整数、含 $\eta=1$ 端点、含 $\lfloor\eta\rfloor\ge2$ 的多个值）：

1. 三个极限 $\lim_{K\to\infty}L_K=\lim_{K\to\infty}U_K=\lim_{K\to\infty}V_{K-m}=1-e^{-1/\eta}$
   （sympy `limit`，符号 η、m）[VERIFIED-SYMBOLIC]。第二条就是 GAP-3 里缺落点的那一条。
2. active branch 的 $\varepsilon=1/K$ 展开一阶系数等于 $e^{-1/\eta}(2\eta-1)/(2\eta^{2})$，且 $\partial c/\partial m=0$
   [VERIFIED-SYMBOLIC]；$c(\eta)>0$ 在 $\eta\in\{1,5/4,3/2,2,3,10,1000\}$ 上逐点为正（$2\eta-1>0$）。
3. 平台：$2\le K\le\lfloor\eta\rfloor$ 时 $\rho_K=\min_jV_j=1/\eta$，精确有理，无反例 [VERIFIED-EXHAUSTIVE]。
4. 首跌恒等式：$\rho_{\lfloor\eta\rfloor}-\rho_{\lfloor\eta\rfloor+1}=(K-\eta)/(K\eta k_1)$ 在 $K=\lfloor\eta\rfloor+1$ 处成立
   （对 $\lfloor\eta\rfloor\ge2$ 的 η），精确有理 [VERIFIED-SYMBOLIC]。
5. 非增与严格递减：$K=2..79$ 上 $\rho_K-\rho_{K+1}\ge0$ 无反例，且 $K\ge\lfloor\eta\rfloor$ 时严格为正
   [VERIFIED-EXHAUSTIVE]（这是 `results/H_B_asymptotic.py` section 4 的独立小规模复跑，该脚本本身跑到 $K=400$）。
6. $L_K$ 在 $K=1..79$ 上严格递减，且 $L_{80}>1-e^{-1/\eta}$（从上方）[VERIFIED-EXHAUSTIVE]。
   这补上了陈述里 monotone 缺的方向。
7. $\rho_K$ 与 $U_K$ 在 $K=2..59$ 上都严格大于 $1-e^{-1/\eta}$（从上方收敛的数值面）[VERIFIED-EXHAUSTIVE]。
8. sandwich $L_K\le\rho_K\le U_K$ 在 $K=2..59$ 上无反例 [VERIFIED-EXHAUSTIVE]（对应 E 表第 27 行）。
9. $U_K$ 在 $K=2..79$ 上非增 [VERIFIED-EXHAUSTIVE]。记录用：正文与台账都没有 $U_K$ 的单调子句，
   本审计不建议加，只记下数值事实。
10. `paper/sections/results.tex` 第 523 至 529 行、`results/V11/statements.md` 第 217 至 223 行、
    `results/V11/inputs/statement_limit.md` 第 6 至 12 行三份 LaTeX 逐字符相同（字符串比对，True）。

---

## 6. 读过的文件

- `paper/sections/results.tex`（第 79 至 130、185 至 215、360 至 400、500 至 550 行）
- `paper/sections/appendix_proofs.tex`（第 1373 至 1460 行，即 app:asymptotics 全段；另看了 subsection 目录）
- `THEOREM_LEDGER.md`（T9 卡第 205 至 228 行；T6、T10b、T10c 的相关条目）
- `results/H_B_asymptotic.py`（全文，sections 0 至 6）
- `results/V11/statements.md`（T9 段，第 202 至 224 行）
- `results/V11/inputs/statement_limit.md`、`inputs/definition1.md`、`inputs/assumptions.md`、`inputs/notation.md`
- `results/V11/audit/exact.md`（格式与 GAP 对照）
- `CLAUDE.md`、`HANDOFF_2026-09-18.md`、`HANDOFF_ADDENDUM_2026-09-18.md`（§B 的编号决定）
