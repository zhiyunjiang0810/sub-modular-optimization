# V11 criterion B 路线比对：cor:limit（ledger T9）

判定者：V11 route-comparison judge。本文件只读不写仓库既有文件，未运行 git。

- 路线一（repository proof）：`paper/sections/appendix_proofs.tex` 的 `\subsection{Asymptotics}`
  `app:asymptotics`（第 1373 行起），正文陈述在 `paper/sections/results.tex` 第 523 行 block 8，
  ledger card `THEOREM_LEDGER.md` 的 `## T9`，脚本 `results/H_B_asymptotic.py`。
- 路线二（blind derivation）：`results/V11/route2/limit.md`，脚本
  `results/V11/route2/limit.md` 所附 `results/V11/route2/verify_limit.py`
  （本判定复跑，尾行 `FAILURES: 0`）。
- 本判定自写的交叉验证脚本：`results/V11/compare/judge_limit_checks.py`
  （exact `fractions.Fraction` + sympy，transcendental 比较用 mpmath 60 位；
  24 项检查，尾行 `FAILURES: 0`）。下文的 check 编号 A..Q4 指该脚本。

---

## 1. 结论（verdict）

**B-PASS-with-different-route。**

两条路线得到同一个结论：固定 $\eta\ge1$ 时 $L_K,\rho_K\to1-e^{-1/\eta}$；$L_K$ 关于 $K$ 单调
（两条路线给出的方向都是递减）；$\rho_K$ 非增，$K\le\lfloor\eta\rfloor$ 时等于 $1/\eta$，
$K\ge\lfloor\eta\rfloor$ 起严格递减，从上方逼近。

判为 with-different-route 的原因有两处实质不同的技术路径，见第 2 节 Step 9 与 Step 11 两行：
$\rho_K$ 极限一步，路线一直接展开 active branch $V_{K-\lfloor\eta\rfloor}$，路线二改用
一致上界 $h_K(j)\le e^{-1/\eta}$ 加 $\rho_K\le U_K$ 的 squeeze；单调性的正性证书，路线一用
$-\log(1-1/x)$ 的三项尾界加坐标变换后 84/165 项非负系数证书，路线二用
$\Sigma(t)<\frac{1}{2t(t-1)}$ 加一条充分条件 $K\frac{2\eta-1}{2\eta}\ge s$。两套论证在本判定
的网格上都成立，且两者的核心导数恒等式经 sympy 确认**逐字相同**（check F）。

路线二没有出现可展示的错误。路线一没有被路线二推翻的步骤；路线一的两处措辞不精确见第 4 节。

---

## 2. 步骤对应表

记 $m=\lfloor\eta\rfloor$，$p=\lceil\eta\rceil$，$s=p-1$，$k_1=(K-1)\eta+1$，
$q=(K-1)\eta/k_1$，$h_K(j)=q^j(1-\frac{K-j}{K\eta})$，$V_j=1-h_K(j)$。

| 路线二步骤 | 内容 | 路线一对应 | 关系与本判定的复核 |
|---|---|---|---|
| Step 0 记号 | $c_j,h_K,V_j=1-h_K(j)$，$\rho_K=1-\max_jh_K(j)$ | app:asymptotics 直接用 $V_j$ 与 $P(K)=q^{K-m}(1-\frac{m}{K\eta})$ | 同一对象换写法。$P(K)=\max_jh_K(j)$ 对全部 $K\ge m$（含 integer $\eta$）exact rational 相等 [VERIFIED-EXHAUSTIVE]（check E，17 个 $\eta$、$K\le60$） |
| Step 1 端点恒等式 $V_0=1/\eta$、$V_K=U_K$ | 提供 plateau 值与 squeeze 的上端 | 路线一不用 $V_K$；它用 $\rho_K\le V_{K-1}<U_K$（`results.tex` 第 683 行注释，来源 `results/N1_dual_certificate.py` part G） | **不同 route**，但两者都给出 $\rho_K\le U_K$。$V_{K-1}<U_K$（$\eta>1$）[VERIFIED-EXHAUSTIVE]（check M2）；$\rho_K\le U_K$ 两种读法下都成立（check M1） |
| Step 2 $L_K$ 严格递减（$\psi(u)=\ln(1-u)+\frac{u}{1-u}>0$） | 完整一元微积分证明 | 路线一只写一句 "$(1-\tfrac xK)^K$ increases in $K$ for $x\in(0,1]$"，无证明 | 路线二**更完整**，方向一致。[VERIFIED-EXHAUSTIVE]（check O1） |
| Step 3 $L_K$ 极限 | $\ln(1-u)=-u+O(u^2)$ | app:asymptotics 第 1375-1379 行，同一代换 $u=1/(\eta K)$ | 同一 route |
| Step 4 一步差分恒等式 | $h_K(j)-h_K(j-1)=q^{j-1}\frac{K-\eta+1-j}{K\eta k_1}$ | 路线一无此恒等式（它直接给 $\partial\log P/\partial K$） | 路线二新增的中间量。[VERIFIED-SYMBOLIC]（check C，除以 $q^{j-1}$ 后 sympy 残差为 0；另有整数 $j$ 的 exact rational 网格） |
| 推论 4a unimodality | $h_K(j)\ge h_K(j-1)\iff j\le K-\eta+1$ | 路线一以 "the minimizing index is the unique $j$ with $\eta\in[K-j,K-j+1]$" 表达同一事实 | 等价。noninteger $\eta$ 下 argmin 唯一且等于 $K-m$ [VERIFIED-EXHAUSTIVE]（check Q1）；integer $\eta$ 下两个相邻端点同时取到（check Q2），与路线一 "either endpoint value at an integer $\eta$" 一致 |
| 推论 4b $V_1-V_0=\frac{\eta-K}{\eta k_1K}$ | plateau 的充要判据 | 路线一 app:asymptotics 第 1430-1431 行的 "strict drop by $(K-\eta)/(K\eta k_1)$ at $K=\lfloor\eta\rfloor+1$" 是同一表达式 | 同一量。该量确为 $\rho_{\lfloor\eta\rfloor}-\rho_{\lfloor\eta\rfloor+1}$ 的下界 [VERIFIED-EXHAUSTIVE]（check Q3） |
| Step 5 argmax 闭式 $j^\ast=\max\{0,K-p+1\}$ | 带 clamp 的 argmax | 路线一散文写 $j=K-\lfloor\eta\rfloor$（无 clamp）；其脚本 `results/H_B_asymptotic.py` 的 `jstar()` 带 clamp `max(0, K-floor(eta))` | 两个下标都取到 $\max_jh_K(j)$ [VERIFIED-EXHAUSTIVE]（check B）。路线二的表述**更精确**（路线一散文缺 clamp，见第 4 节 D3） |
| Step 6 plateau 充要 $\rho_K=1/\eta\iff K\le\lfloor\eta\rfloor$ | 从闭式推出，含 (⇐)(⇒) 两向 | 路线一**不证**，直接引用 thm:exact（"the plateau of Theorem~\ref{thm:exact}"）；ledger T6 写作 $\rho_K=1/\eta\iff\eta\ge K$ | 路线二给出独立推导，且 $\eta\ge K\iff K\le\lfloor\eta\rfloor$（$K$ 整数）。[VERIFIED-EXHAUSTIVE]（check J1） |
| Step 7 一致下界 $h_K(j)\le e^{-1/\eta}$ | $q^j\le e^{-j/(K\eta)}$ 加 $g(x)=e^{-x/\eta}(1-\frac{1-x}{\eta})$ 不减 | **路线一没有对应步骤** | 路线二新增。[VERIFIED-EXHAUSTIVE]（check L，mpmath 60 位，最小 slack $4.998\times10^{-7}$ 在 $K=1,\eta=1000$，为正；与路线二自报一致） |
| Step 8 $\Lambda(K)$ 闭式 | $\Lambda=q^{K-p+1}(1-\frac{p-1}{K\eta})$ | 路线一的 $P(K)=q^{K-m}(1-\frac{m}{K\eta})$ | 两式在 $K\ge m$ 上逐点相等（check E）。noninteger $\eta$ 时 $m=s$ 字面相同；integer $\eta$ 时指数差 1、因子不同而值相等（Step 4 在 $j=K-\eta+1$ 处分子为 0 的 tie）。[VERIFIED-EXHAUSTIVE]（check D、E） |
| Step 9 $\Lambda$ 严格递增 | 换元 $t=k_1$，boxed 恒等式 $\frac{d\ln\Lambda}{dt}=-\frac{\Sigma(t)}{\eta}+\frac{1-s}{t(t-1)}+\frac{s}{(t+\eta-1-s)(t+\eta-1)}$，再用 $\Sigma(t)<\frac{1}{2t(t-1)}$ 与 $K\frac{2\eta-1}{2\eta}\ge s$ | 路线一 $\frac{\partial\log P}{\partial K}=\log(1-\frac1x)+\frac{K-m}{(K-1)x}+\frac{m}{K(K\eta-m)}$，再用三项尾界与 84/165 项非负系数证书 | **导数恒等式完全相同**：$\frac{\partial\log P}{\partial K}=\eta\cdot\frac{d\ln\Lambda}{dt}$ 的残差 sympy 为 0 [VERIFIED-SYMBOLIC]（check F）；路线二的 boxed 形式独立 [VERIFIED-SYMBOLIC]（check G）。**正性证书是不同 route**：两者都在网格上成立（check H、I），路线一的尾界本判定另行确认（check Q4，mpmath 60 位，$x$ 从 $1.0001$ 到 $10^8$） |
| Step 10 $\rho_K$ 非增、$K\ge\lfloor\eta\rfloor$ 起严格 | 分区间 I / 交界 / 区间 II | 路线一同样分两段：plateau 加 "first step off the plateau" 加 $K\ge m$ 的导数段 | 结构对应。[VERIFIED-EXHAUSTIVE]（check J2、J3，17 个 $\eta$、$K\le60$，exact rational） |
| Step 11 $\rho_K$ 极限（squeeze） | 下界 Step 7 加上界 $U_K\to1-e^{-1/\eta}$ | 路线一直接算 active branch：$j/k_1=\frac{K-m}{(K-1)\eta+1}\to\frac1\eta$，$1-\frac{m}{K\eta}\to1$ | **不同 route**，同一结论。路线一的算法是 $\rho_K=V_{K-m}$ 的逐项极限；路线二回避了 active branch 的极限，只用一个一致上界与一个逐点上界 |
| Step 12 汇总 | 逐条挂回 (C-a)..(C-g) | 路线一无汇总段 | 无冲突 |
| （无） | 无对应 | **路线一独有：$1/K$ 展开** $\rho_K=1-e^{-1/\eta}+\frac{c(\eta)}{K}+O_\eta(1/K^2)$，$c(\eta)=e^{-1/\eta}\frac{2\eta-1}{2\eta^2}$，以及 $c_L=e^{-1/\eta}/(2\eta^2)$、$c_U=c$、$\rho_K-L_K$ 与 $U_K-\rho_K$ 的阶 | 路线二完全没有这一块。它不属于 `cor:limit` 的陈述本身（正文里是 corollary 之后的 "Quantitatively" 句），所以不算 route-two 的缺口，只算覆盖差。本判定数值抽查 $\eta=3/2,K=4000$：$K(\rho_K-\lim)=0.22818539$ 对 $c(3/2)=0.22818539$（check P），与路线二的数值表不矛盾 |
| （无） | 无对应 | **路线一独有**：integer $\eta$ 由坐标变换端点 $s=0$ 覆盖的说明 | 路线二用 Step 8 末尾的两分支一致性处理同一情形，结论相同（check E） |

---

## 3. 量词比对

| 量词 | 路线一 | 路线二 | 判定 |
|---|---|---|---|
| $\eta$ 固定、$\eta\ge1$、实数 | 有（"Fix $\eta\ge1$"） | 有 | 一致 |
| 极限是逐点的，不关于 $\eta$ 一致 | 有，并显式写 uniformity of the $O(1/K^2)$ remainder in $\eta$ 是 [CONJECTURE] | 有（空洞性检验第四条） | 一致 |
| $K$ 取正整数，$K\to\infty$ | 有 | 有 | 一致 |
| conditional on thm:exact | 有（ledger T9 与附录 status 注释） | 有（A3） | 一致 |
| **thm:exact 的 $K\ge2$ 前提** | **有**（ledger T6 陈述首句 "$K\ge2,\eta\ge1$"；$K=1$ 由 T10b 的单独三行论证给出 $\rho_1=1/\eta$） | **无**（输入包的 notation.md 未写 $K\ge2$，路线二在 $K=1$ 上直接用闭式） | **不一致**。数值上无后果：$K=1$ 时两种下标范围都给 $\rho_1=V_0=1/\eta$（check J1 覆盖 $K=1$），但这是路线二未声明的一条借用 |
| **$n$ 的量词** | **有**（ledger T6 M1：$\rho_{n,K}$ 是固定 $n$ 的精确最坏比，$n\ge2K$ 时 $\rho_{n,K}=\rho_{2K,K}=\rho_K$；[HAND-PROOF-UNREVIEWED] 加 [VERIFIED-LP] 支持） | **无**（路线二 A2 明确把 "$\rho_K$ 与 $n$ 无关" 记为自己追加的读法，并说若实为 $\rho_{n,K}$ 则 (C-a)(C-b) 需补量词） | **不一致**，但路线二提的正是路线一已经有答案的那条；用 T6 M1 的 $n\ge2K$ 即可闭合 |
| **$\min_jV_j$ 中 $j$ 的范围** | $0\le j\le K-1$（`results.tex` 第 194 行与 ledger T6） | $0\le j\le K$（A1，追加读法） | **不一致的读法**，但**不改变 $\rho_K$ 的值**：$\min_{0\le j\le K-1}V_j=\min_{0\le j\le K}V_j$ [VERIFIED-EXHAUSTIVE]（check A，17 个 $\eta$、$K\le60$，exact rational）。原因：$\eta>1$ 时 $j^\ast\le K-1$；$\eta=1$ 时 $j^\ast=K$ 但 $h_K(K)=h_K(K-1)$ |
| deterministic / adversarial tie / 恰好 $K$ 步 | 由 `assumptions.md` 与 $\rho_K$ 的定义携带 | 有，且逐条做了空洞性检验 | 一致；路线二的检验更细 |

`quantifier_match = false`：差在上表加粗的三行（$K\ge2$、$n$、$j$ 范围）。三条都不改变结论的真值，其中两条（$n$、$j$ 范围）是路线二主动记录的读法假设，一条（$K\ge2$）是路线二未察觉的借用。

---

## 4. divergences（逐条）

- **D1（$\rho_K$ 极限的证明路径不同）** 路线一算 active branch $V_{K-\lfloor\eta\rfloor}$ 的逐项极限；
  路线二用 $1-e^{-1/\eta}\le\rho_K\le U_K\to1-e^{-1/\eta}$ 的 squeeze。两者结论相同，路线二额外得到
  一条对所有 $K$ 成立的一致下界（Step 7），这正是 `cor:limit` 里 "approached from above" 的
  $\rho$ 部分；路线一的 "from above" 只能由单调性段落间接给出。
- **D2（单调性正性证书不同）** 路线一：三项尾界
  $-\log(1-1/x)\le\frac1x+\frac{1}{2x^2}+\frac{1}{3x^2(x-1)}$ 加坐标变换 $s=t/(1+t)$ 后
  84 项分子 / 165 项分母全非负；路线二：$\Sigma(t)<\frac{1}{2t(t-1)}$ 加充分条件
  $K\frac{2\eta-1}{2\eta}\ge s$（由 $K\ge s+1$ 与 $s<\eta\le2\eta-1$ 推出）。
  本判定分别确认两者（check Q4 / check H），且确认两者所导的导数恒等式相同（check F）。
- **D3（路线一散文的 argmax 缺 clamp）** app:asymptotics 写 "the minimizing index is the unique $j$
  with $\eta\in[K-j,K-j+1]$, that is $j=K-\lfloor\eta\rfloor$"，在 plateau 区 $K<\lfloor\eta\rfloor$
  该下标为负，字面不成立；正确写法是 $\max\{0,K-\lfloor\eta\rfloor\}$，路线一自己的脚本
  `results/H_B_asymptotic.py` 的 `jstar()` 就是带 clamp 的。该段上下文是 $K\to\infty$，所以不影响
  结论，属措辞范围问题，不是路线二与之矛盾。
- **D4（"unique" 在 integer $\eta$ 处）** 同一句的 "unique" 在 $\eta$ 为整数时不成立（两个相邻下标
  同时取到，check Q2），路线一随后用 "either endpoint value at an integer $\eta$" 自行补上；
  路线二用 tie（Step 4 分子为 0）表达同一事实。不构成冲突。
- **D5（$\rho_K\le U_K$ 的来源不同）** 路线一：$\rho_K\le V_{K-1}$ 且 $U_K-V_{K-1}=q^{K-1}\frac{\eta-1}{K\eta k_1}>0$；
  路线二：$\rho_K\le V_K=U_K$（依赖 A1 把 $j=K$ 放进范围）。在 paper 的范围 $\{0,\dots,K-1\}$ 下
  路线二这一步失去字面来源，但结论 a fortiori 成立（check M1、M2），且换成 $V_{K-1}$ 后
  squeeze 照样闭合（$V_{K-1}\to1-e^{-1/\eta}$）。
- **D6（覆盖差）** 路线一含 $1/K$ 展开与 $c(\eta),c_L,c_U$，路线二没有；路线二含 plateau 的
  充要性独立推导、$L_K$ 严格递减的完整证明、一致下界 Step 7，路线一没有或只有一句断言。
- **D7（$L_K$ 单调的方向）** 陈述只说 "monotone"；两条路线给出的方向都是严格递减
  （路线一写 "monotone from above"）。方向一致，不是分歧，记录以备正文措辞收紧。

---

## 5. route-two gaps（逐条，含本判定的处置）

- **R2-G1（A1：$\min_jV_j$ 的下标范围是追加读法）** 路线二取 $j\in\{0,\dots,K\}$，仓库是
  $\{0,\dots,K-1\}$。本判定 exact rational 复核：两者给出同一个 $\rho_K$（check A，
  17 个 $\eta$、$K\le60$）[VERIFIED-EXHAUSTIVE]。受影响的只有 Step 11 上界那一步的**出处**
  （见 D5），结论不变。**不是错误，是可闭合的读法缺口。**
- **R2-G2（A2：$n$ 的量词缺失）** 路线二把 "$\rho_K$ 与 $n$ 无关" 记为自己的追加读法。仓库
  ledger T6 M1 给出 $n\ge2K\Rightarrow\rho_{n,K}=\rho_K$（状态 [HAND-PROOF-UNREVIEWED] 加
  [VERIFIED-LP] 数值支持）。**缺口在路线二侧，仓库已有答案；补上 $n\ge2K$ 即可。**
- **R2-G3（A3：条件依赖 thm:exact）** 与路线一相同，不是差异。
- **R2-G4（Step 9 的定义域在 $\eta=1,K=1\to2$ 处没有覆盖）** Step 9 的换元需要 $t=k_1>1$；
  $p=1$（即 $\eta=1$）时 $t=K$，$K=1$ 落在奇点 $t=1$，而 Step 10 的 integer-$\eta$ 交界一支
  在 $\eta=1$ 时正是要比较 $\Lambda(2)$ 与 $\Lambda(1)$。结论仍真：$\rho_1(1)=1>\rho_2(1)=3/4$
  [VERIFIED-EXHAUSTIVE]（check K，exact rational）。路线一在这一格用的是另一条论证
  （first drop $=(K-\eta)/(K\eta k_1)=1/4$，与实际差值相等），所以该格由路线一覆盖。
  **本判定认定这是路线二的一个 boundary 缺口，可由路线一的 first-drop 论证直接补上。**
- **R2-G5（$K=1$ 处借用 thm:exact 而未声明 $K\ge2$）** 见第 3 节。数值无后果，属未声明的借用。
- **R2-G6（G1：ProbeLottery 走查未完成）** 路线二的任务文本要求了一个 "$K=2$ ProbeLottery item"
  走查，输入包里没有该对象。路线二保守处理为给出 $K=2$ 的各分支取值并记 [FAILED]。
  **这与 `cor:limit` 的正确性无关**，是盲审任务文本与输入包不匹配，不计入数学缺口。
- **R2-G7（一般参数域仍是手写）** Step 2、3、7、9、11 的一般 $(\eta,K)$ 论证是
  [HAND-PROOF-UNREVIEWED]，oracle 只在 17 个 $\eta$ 与 $K\le60$ 的网格上。这一点与路线一的
  处境相同（路线一的尾界与从连续导数到离散差分的装配同样是 [HAND-PROOF-UNREVIEWED]，
  ledger T9 明写）。不构成路线间的差异。
- **路线二记录的两条 [FAILED]（F1、F2）** 配对引理 $h_{K+1}(j+1)\ge h_K(j)$ 在
  $\eta=10,K=4,j=1$ 失效（$h_4(1)=111/124>h_5(2)=1504/1681$），以及配套的多项式证书
  在同一参数为负。本判定确认该反例数值正确，且这两条已被路线二废弃、不进入最终论证。
  记录在此以免他人重走。

---

## 6. 路线一是否有被路线二推翻的步骤

没有。本判定逐条复核了 app:asymptotics 的每一处可机检断言：

| 路线一断言 | 复核 | 状态 |
|---|---|---|
| $(1-x/K)^K$ 关于 $K$ 递增（$x\in(0,1]$） | check O1 | [VERIFIED-EXHAUSTIVE] |
| $L_K\to1-e^{-1/\eta}$ 且 $L_K>$ 极限 | check O2 | [VERIFIED-EXHAUSTIVE] |
| active branch $j=K-\lfloor\eta\rfloor$（integer $\eta$ 两端点） | check B、Q1、Q2 | [VERIFIED-EXHAUSTIVE] |
| $\partial\log P/\partial K$ 恒等式 | check F（与路线二的独立推导逐字相同） | [VERIFIED-SYMBOLIC] |
| 尾界 $-\log(1-1/x)\le\frac1x+\frac1{2x^2}+\frac1{3x^2(x-1)}$ | check Q4（mpmath 60 位，$x\in[1.0001,10^8]$），级数逐项 $1/i\le1/3$（$i\ge3$）的推导本判定手核无误 | [HAND-PROOF-UNREVIEWED] 加数值 |
| plateau 的 first drop $(K-\eta)/(K\eta k_1)>0$ | check Q3 | [VERIFIED-EXHAUSTIVE] |
| $\rho_K\le V_{K-1}<U_K$（$\eta>1$） | check M2 | [VERIFIED-EXHAUSTIVE] |
| $c(\eta)=e^{-1/\eta}(2\eta-1)/(2\eta^2)$ | check P（$\eta=3/2$，$K=4000$，与闭式差 $<10^{-3}$；不是对一般 $\eta$ 的确认） | [VERIFIED-SYMBOLIC，来源 results/H_B_asymptotic.py]，本判定只做一点抽查 |

唯一未由本判定独立重跑的是路线一的 84/165 项非负系数证书（ledger T9 记为
[VERIFIED-SYMBOLIC conditional on T6]，来源 `results/H_B_asymptotic.py` 第 4-5 节与
J5 hardcore 的独立重跑）。本判定不重复该项，理由是路线二的独立正性论证（check H、I）
已在同一网格上给出同向结论，两者不冲突。

---

## 7. 数值一致性抽查

路线二第 3 节的表与本判定 exact rational 复算一致（check N）：
$\eta=3/2$ 时 $\rho_1=2/3$、$\rho_2=3/5$、$\rho_3=9/16$、$\rho_4=1447/2662$。
其中 $\rho_2=3/5$、$\rho_3=9/16$ 与 HANDOFF §4 的四档梯子表（$K=3,\eta=3/2$ 时 greedy 恰
$9/16=0.5625$）一致；$\rho_K=1/\eta\iff\eta\ge K$（ledger T6）与路线二的
$K\le\lfloor\eta\rfloor$ 判据在整数 $K$ 上等价（check J1）。

---

## 8. 一句话给写作侧的提示

`cor:limit` 的 "approached from above" 目前在附录里只有单调性支撑；路线二的 Step 7
给出的一致下界 $\rho_K\ge1-e^{-1/\eta}$（$h_K(j)\le e^{-1/\eta}$，$j$ 全域）是一条可直接
补进 app:asymptotics 的独立支撑，状态 [HAND-PROOF-UNREVIEWED] 加
[VERIFIED-EXHAUSTIVE]（17 个 $\eta$、$K\le60$、mpmath 60 位）。是否采用由人类决定，
本判定不改动任何既有文件。
