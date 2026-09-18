# ROUTE-TWO 盲证：cor:limit（ledger T9）

本文件是对 `results/V11/inputs/statement_limit.md` 中 `cor:limit` 的独立推导。写作时只使用
`results/V11/inputs/` 下的四个输入文件（definition1.md、assumptions.md、notation.md、
statement_limit.md）与标准数学，没有查看 paper/、THEOREM_LEDGER.md、HANDOFF*、REPORT.md 或
仓库中任何其他文件，也没有使用 web search 或 git。

可复现脚本：`results/V11/route2/verify_limit.py`（exact rational + sympy + mpmath，
运行结果 `FAILURES: 0`）。

---

## 1. 陈述复述（含全部 quantifier）

### 1.1 固定的对象与其定义域

- ground set $N$，$|N|=n$；monotone submodular $f:2^N\to\mathbb R_{\ge0}$，$f(\emptyset)=0$；
  算法不能 query $f$，只能 query predictor $\tilde f$，$\tilde f(\emptyset)=0$
  （assumptions.md）。
- cardinality budget $K$ 是整数，$1\le K\le n$（assumptions.md）。
- 误差参数 $\eta=\eta_u\eta_o$ 是实数，$\eta\ge1$；本推论中 $\eta$ 固定，$K$ 变动
  （definition1.md 的 convention B：两个因子如何拆分不影响任何结论，所有陈述只用 $\eta$）。
- query 类型：single-element multiplicative band，即对**所有** $S\subseteq N$ 与**所有**
  $e\notin S$ 有 $d_e(S)/\eta_u\le\tilde d_e(S)\le\eta_o d_e(S)$；算法可见的量是
  $\tilde d_e(S)$（single-element predicted marginal gain），不是 all-pairs 或集合值 query。
- 算法：deterministic single-step predictive greedy，即在 $\tilde f$ 上跑单步 greedy；
  $t=0,\dots,K-1$ 每步取 $\arg\max_{e\notin S^t}\tilde d_e(S^t)$。
- tie breaking：adversarial（assumptions.md 明写 "ties broken adversarially in all
  worst-case statements"）。
- 步数：run **恰好**执行 $K$ 步，不允许 early stopping；某步最大 predicted gain 为 $0$ 时
  仍然选元素（assumptions.md）。
- 近似比约定：$\alpha\in(0,1]$，$F^{\mathrm{ALG}}\ge\alpha F^{\mathrm{OPT}}$，越大越好；
  $f(O^\ast)=0$ 时所有比值语句 trivially 成立。
- $\rho_K(\eta)$：上述算法在 error level $\eta$、adversarial ties 下的 **exact worst-case
  ratio**，即对所有满足 band 的 instance $(N,f,\tilde f)$ 取 infimum 并且该 infimum 可达。

### 1.2 公式对象（notation.md）

$$L_K(x)=1-\Big(1-\frac{1}{xK}\Big)^{K},\qquad
k_1=(K-1)\eta+1,\qquad q=\frac{(K-1)\eta}{k_1},$$
$$V_j(\eta)=1-q^{j}\Big(1-\frac{K-j}{K\eta}\Big),\qquad
\rho_K=\min_j V_j\ \ (\text{Theorem thm:exact，本推导中作为给定}),$$
$$U_K(\eta)=1-\Big(1-\frac{1}{\eta(K-1)+1}\Big)^{K}.$$

$j$ 的取值范围在 notation.md 中没有写出。本文取 $j\in\{0,1,\dots,K\}$（见第 4 节 A1，
这是由两个端点反推出的唯一自洽读法：$V_0=1/\eta$、$V_K=U_K(\eta)$）。

### 1.3 待证命题（逐条量词化）

对**每一个**固定实数 $\eta\ge1$：

- (C-a) $\displaystyle\lim_{K\to\infty}L_K(\eta)=1-e^{-1/\eta}$（$K$ 取遍正整数；由于
  assumptions.md 要求 $K\le n$，这里隐含 $n\to\infty$，即极限是在 ground set 可以任意大的
  instance 族上取的，见第 4 节 A2）。
- (C-b) $\displaystyle\lim_{K\to\infty}\rho_K(\eta)=1-e^{-1/\eta}$。
- (C-c) $L_K(\eta)$ 关于整数 $K\ge1$ 单调；本文给出的方向是**严格递减**。
- (C-d) $\rho_K(\eta)$ 关于整数 $K\ge1$ 非增（non-increasing）。
- (C-e) 对**所有**整数 $K$ 满足 $1\le K\le\lfloor\eta\rfloor$ 有 $\rho_K(\eta)=1/\eta$
  （plateau）；并且这是充要的，即 $K>\lfloor\eta\rfloor$ 时 $\rho_K<1/\eta$。
- (C-f) 对**所有**整数 $K\ge\lfloor\eta\rfloor$（且 $K\ge1$）有
  $\rho_{K+1}(\eta)<\rho_K(\eta)$（从 $K\ge\lfloor\eta\rfloor$ 起严格递减）。
- (C-g) 极限从上方逼近：对**所有** $K\ge1$ 有 $L_K(\eta)>1-e^{-1/\eta}$ 且
  $\rho_K(\eta)\ge1-e^{-1/\eta}$。

空洞性检验（CLAUDE.md 第 "空洞性检验" 节）：
- 去掉 "deterministic"：$\rho_K$ 的定义就是 single-step predictive greedy 这一条确定性
  算法的最坏比，换成 randomized 算法类整个 $\rho_K$ 就不是这个对象了，限定词不空洞。
- 去掉 "adversarial tie breaking"：$V_1<V_0$ 这一支（第 2.6 步）依赖最坏情形可被 tie
  实现；若 tie 按最优打破，worst case 只会变好，$\rho_K$ 的值会改变，限定词不空洞。
- 去掉 "恰好 $K$ 步"：assumptions.md 明说 early-stopping 变体只有 executed-steps product
  bound，$\rho_K$ 不再是同一个量，限定词不空洞。
- 去掉 "fixed $\eta$"：极限是逐点（对每个 $\eta$）取的，不是关于 $\eta$ 一致的，限定词不空洞。
- 去掉 "$K\le\lfloor\eta\rfloor$" 中的 floor：$K$ 是整数，$K\le\eta\iff K\le\lfloor\eta\rfloor$，
  两种写法等价，floor 只是把条件写成整数形式，可以保留但不增加内容。

---

## 2. 推导

全程记
$$c_j:=1-\frac{K-j}{K\eta}=\frac{K\eta-K+j}{K\eta},\qquad
h_K(j):=q^{\,j}c_j,\qquad V_j=1-h_K(j),$$
于是
$$\rho_K=\min_{0\le j\le K}V_j=1-\max_{0\le j\le K}h_K(j).$$
约定 $0^0=1$（只在 $K=1$ 时用到，此时 $q=0$）。注意 $c_0=1-\frac1\eta\ge0$ 且 $c_j$ 关于 $j$
严格递增到 $c_K=1$，所以所有 $h_K(j)\ge0$。

---

**Step 1（端点恒等式）** $V_0=1/\eta$，$V_K=U_K(\eta)$。

用 Step 0 的记号：$V_0=1-c_0=1-(1-\frac1\eta)=\frac1\eta$；
$V_K=1-q^K c_K=1-q^K=1-\big(1-\frac{1}{k_1}\big)^K=1-\big(1-\frac{1}{\eta(K-1)+1}\big)^K=U_K(\eta)$。
依据：notation.md 中 $k_1,q,V_j,U_K$ 的定义。
状态：[VERIFIED-SYMBOLIC]（`verify_limit.py` 检查 C1，exact rational，$\eta$ 网格 17 个值、
$K\le14$，全过）。

---

**Step 2（$L_K$ 严格递减）** 对固定 $\eta\ge1$ 与整数 $K\ge1$，$L_{K+1}(\eta)<L_K(\eta)$。

记 $a=1/\eta\in(0,1]$。$L_K=1-(1-a/K)^K$，故只需证 $K\mapsto(1-a/K)^K$ 在整数 $K\ge1$ 上严格递增。

- 若 $a=1$ 且 $K=1$：$(1-1)^1=0<(1-\frac12)^2=\frac14$，成立。
- 其余情形 $1-a/K>0$。令 $G(x)=x\ln(1-a/x)$，$x\ge1$，$x>a$。
  $$G'(x)=\ln\Big(1-\frac ax\Big)+\frac{a}{x-a}=\psi(u),\qquad u:=\frac ax\in(0,1),$$
  其中 $\psi(u)=\ln(1-u)+\frac{u}{1-u}$。由 $\psi(0)=0$ 与
  $\psi'(u)=-\frac{1}{1-u}+\frac{1}{(1-u)^2}=\frac{u}{(1-u)^2}>0$（$u\in(0,1)$）得 $\psi(u)>0$。
  所以 $G$ 在 $[\max(1,a),\infty)$ 上严格递增，$(1-a/K)^K=e^{G(K)}$ 严格递增。

依据：Step 0 的定义与 notation.md 的 $L_K$；用到 $\eta\ge1$ 保证 $a\le1$。
状态：[HAND-PROOF-UNREVIEWED]（一元微积分）；数值确认 [VERIFIED-EXHAUSTIVE]
（检查 C6，17 个 $\eta$、$K\le60$，exact rational，全过）。

---

**Step 3（$L_K$ 的极限）** $\lim_{K\to\infty}L_K(\eta)=1-e^{-1/\eta}$。

$K\ln\big(1-\frac{1}{\eta K}\big)\to-\frac1\eta$（$\ln(1-u)=-u+O(u^2)$，$u=\frac{1}{\eta K}\to0$），
故 $(1-\frac{1}{\eta K})^K\to e^{-1/\eta}$。结合 Step 2，$L_K$ 严格递减并收敛到
$1-e^{-1/\eta}$，即**从上方**逼近，且对所有 $K$ 有 $L_K(\eta)>1-e^{-1/\eta}$。
这给出 (C-a)、(C-c) 与 (C-g) 的 $L$ 部分。
状态：[HAND-PROOF-UNREVIEWED] + 数值确认见第 3 节表。

---

**Step 4（一步差分恒等式）** 对 $1\le j\le K$，
$$h_K(j)-h_K(j-1)=q^{\,j-1}\cdot\frac{K-\eta+1-j}{K\eta\,k_1}.$$

推导：$h_K(j)-h_K(j-1)=q^{j-1}\big(q c_j-c_{j-1}\big)$，而 $c_{j-1}=c_j-\frac{1}{K\eta}$，
$1-q=\frac{1}{k_1}$，于是
$$qc_j-c_{j-1}=\frac{1}{K\eta}-(1-q)c_j=\frac{1}{K\eta}-\frac{c_j}{k_1}
=\frac{k_1-K\eta c_j}{K\eta\,k_1}=\frac{k_1-(K\eta-K+j)}{K\eta\,k_1}
=\frac{K-\eta+1-j}{K\eta\,k_1},$$
最后一步用 $k_1=(K-1)\eta+1=K\eta-\eta+1$。
依据：Step 0 与 notation.md 中 $k_1,q$ 的定义。
状态：[VERIFIED-SYMBOLIC]（sympy 因式分解给出
`-(-K + eta + j - 1)/(K*eta*(K*eta - eta + 1))`，与上式相同；脚本检查 C3）。

推论 4a（unimodality 与判据）：$h_K(j)\ge h_K(j-1)\iff j\le K-\eta+1$，且严格不等号对应
$j<K-\eta+1$。因此 $h_K$ 关于 $j$ 先不减后严格递减（unimodal）。

推论 4b（$j=1$ 的情形）：取 $j=1$ 得
$$V_1-V_0=-(h_K(1)-h_K(0))=\frac{\eta-K}{\eta\,k_1\,K},$$
即 $V_1<V_0\iff K>\eta$，$V_1\ge V_0\iff K\le\eta$。
状态：[VERIFIED-SYMBOLIC]（脚本检查 C2，sympy 残差为 $0$）。

---

**Step 5（argmax 的闭式）** 记 $p:=\lceil\eta\rceil$（整数，$p\ge1$）。则
$$j^\ast_K:=\max\{0,\;K-p+1\}$$
是 $\max_{0\le j\le K}h_K(j)$ 的一个取到者。

由推论 4a，整数 $j$ 满足 $h_K(j)\ge h_K(j-1)$ 当且仅当 $j\le\lfloor K-\eta+1\rfloor$；
而 $\lfloor K-\eta+1\rfloor=K+1+\lfloor-\eta\rfloor=K+1-\lceil\eta\rceil=K-p+1$（$K$ 为整数）。
于是 $h_K$ 在 $j=0,\dots,K-p+1$ 上不减、在其后严格递减，最大值在
$j=\max\{0,K-p+1\}$ 处取到（注意 $K-p+1\le K$ 因 $p\ge1$）。
依据：Step 4 推论 4a。
状态：[HAND-PROOF-UNREVIEWED] + [VERIFIED-EXHAUSTIVE]（脚本检查 C4，17 个 $\eta$、
$K\le60$，逐点比对 exact rational 的真实 argmax 值，全过）。

---

**Step 6（plateau 与其充要性，(C-e)）** 对整数 $K\ge1$：
$$\rho_K(\eta)=\frac1\eta\iff K\le\lfloor\eta\rfloor .$$

(⇐) 设 $K\le\lfloor\eta\rfloor$，即 $K\le\eta$。
- 若 $K<\eta$：由推论 4b，$h_K(1)<h_K(0)$，再由推论 4a 的 unimodality，$h_K$ 在 $j\ge1$ 上
  严格递减，故 $\max_jh_K(j)=h_K(0)=1-\frac1\eta$，$\rho_K=\frac1\eta$。
- 若 $K=\eta$（此时 $\eta$ 必为整数）：推论 4b 给出 $h_K(1)=h_K(0)$，而 Step 4 对 $j\ge2$ 的
  分子 $K-\eta+1-j=1-j<0$，故其后严格递减，$\max_jh_K(j)=h_K(0)=1-\frac1\eta$，
  仍有 $\rho_K=\frac1\eta$。

(⇒) 设 $K>\lfloor\eta\rfloor$，即 $K>\eta$（$K$ 整数）。推论 4b 给出 $h_K(1)>h_K(0)$，
于是 $\max_jh_K(j)\ge h_K(1)>h_K(0)=1-\frac1\eta$，即 $\rho_K\le V_1<V_0=\frac1\eta$。

依据：Step 1、Step 4（推论 4a、4b）。
状态：[HAND-PROOF-UNREVIEWED] + [VERIFIED-EXHAUSTIVE]（脚本检查 C9 的 plateau 充要性部分）。

---

**Step 7（一致下界 $\rho_K\ge1-e^{-1/\eta}$，(C-g) 的 $\rho$ 部分）**
对**所有**整数 $K\ge1$ 与所有 $0\le j\le K$：$h_K(j)\le e^{-1/\eta}$，故
$\rho_K(\eta)\ge1-e^{-1/\eta}$。

1. $q=1-\frac{1}{k_1}$，由 $\ln(1-u)\le-u$（$u\in[0,1)$）得 $q^j\le e^{-j/k_1}$。
   （$K=1$ 时 $q=0$，$j=0$ 项为 $c_0\le1-\frac1\eta\le e^{-1/\eta}$ 亦成立，见下面第 4 点。）
2. $k_1=(K-1)\eta+1\le K\eta$ 等价于 $\eta\ge1$，成立；故 $\frac{j}{k_1}\ge\frac{j}{K\eta}$，
   于是 $q^j\le e^{-j/(K\eta)}$。
3. 令 $x=j/K\in[0,1]$。则 $c_j=1-\frac{1-x}{\eta}$，且
   $$h_K(j)\le e^{-x/\eta}\Big(1-\frac{1-x}{\eta}\Big)=:g(x).$$
   （这里用到 $c_j\ge0$，来自 $c_j\ge c_0=1-\frac1\eta\ge0$。）
4. $g'(x)=e^{-x/\eta}\Big[-\frac1\eta\Big(1-\frac{1-x}{\eta}\Big)+\frac1\eta\Big]
   =\frac{e^{-x/\eta}}{\eta}\cdot\frac{1-x}{\eta}\ge0$，故 $g$ 在 $[0,1]$ 上不减，
   $g(x)\le g(1)=e^{-1/\eta}$。
5. 综上 $\max_jh_K(j)\le e^{-1/\eta}$，即 $\rho_K=1-\max_jh_K(j)\ge1-e^{-1/\eta}$。

依据：Step 0、notation.md 的 $q,k_1$、以及 $\eta\ge1$（assumptions.md / definition1.md）。
状态：[HAND-PROOF-UNREVIEWED] + [VERIFIED-EXHAUSTIVE]（脚本检查 C5，mpmath 60 位，
17 个 $\eta$、$K\le60$，最小 slack $\approx4.998\times10^{-7}$ 出现在 $K=1,\eta=1000$，为正）。

---

**Step 8（最大值的闭式）** 对整数 $K\ge p=\lceil\eta\rceil$：
$$\Lambda(K):=\max_{0\le j\le K}h_K(j)
=\Big(\frac{(K-1)\eta}{(K-1)\eta+1}\Big)^{K-p+1}\Big(1-\frac{p-1}{K\eta}\Big).$$

由 Step 5，$j^\ast_K=K-p+1\ge1$；代入 $h_K(j)=q^jc_j$，其中
$$c_{j^\ast}=1-\frac{K-(K-p+1)}{K\eta}=1-\frac{p-1}{K\eta}.$$
依据：Step 5、Step 0。
状态：[VERIFIED-EXHAUSTIVE]（脚本检查 C7，exact rational，$p\le K\le60$，17 个 $\eta$，
与逐点 $\max_j$ 完全相等）。

顺带：$\rho_K=1-\Lambda(K)$ 对 $K\ge p$；$\rho_K=1/\eta$ 对 $K\le\lfloor\eta\rfloor$。
两个区间在 $\eta$ 为整数时于 $K=\eta=p$ 处重叠，且此处 $\Lambda(p)=1-\frac1\eta$
（把 $\eta=p$ 代入上式：$\big(\frac{p(p-1)}{p(p-1)+1}\big)\big(\frac{p^2-p+1}{p^2}\big)
=\frac{p^2-p}{p^2}=1-\frac1p$），两式一致。

---

**Step 9（$\Lambda$ 严格递增）** 把 $\Lambda$ 视为实变量 $K\ge p$ 的函数（$p,\eta$ 固定），
则 $\Lambda$ 严格递增。

换元：令 $t:=k_1=(K-1)\eta+1$（关于 $K$ 严格递增，$t\ge(p-1)\eta+1>1$ 当 $K\ge p\ge2$；
$p=1$ 即 $\eta=1$ 的情形 $t=K$，$K\ge2$ 时 $t>1$），并令 $s:=p-1\ge0$。则
$$K\eta=t+\eta-1,\qquad K-1=\frac{t-1}{\eta},\qquad
u:=K-p+1=\frac{t-1}{\eta}+1-s,$$
$$\ln\Lambda=u\ln\Big(1-\frac1t\Big)+\ln\big(t+\eta-1-s\big)-\ln\big(t+\eta-1\big).$$
对 $t$ 求导（$\frac{du}{dt}=\frac1\eta$，$\frac{d}{dt}\ln(1-\frac1t)=\frac{1}{t(t-1)}$）：
$$\frac{d\ln\Lambda}{dt}
=\frac1\eta\ln\Big(1-\frac1t\Big)+\frac{u}{t(t-1)}
+\frac{s}{(t+\eta-1-s)(t+\eta-1)} .$$
把 $\ln(1-\frac1t)=-\frac1t-\Sigma(t)$，$\Sigma(t):=\sum_{i\ge2}\frac{1}{i\,t^{i}}>0$，
以及 $\frac{u}{t(t-1)}=\frac{1}{\eta t}+\frac{1-s}{t(t-1)}$ 代入，$\frac{1}{\eta t}$ 相消：
$$\boxed{\ \frac{d\ln\Lambda}{dt}
=-\frac{\Sigma(t)}{\eta}+\frac{1-s}{t(t-1)}+\frac{s}{(t+\eta-1-s)(t+\eta-1)}\ }$$

以下证明右端为正。

9.1 级数界：$\Sigma(t)=\sum_{i\ge2}\frac{1}{i t^i}<\frac12\sum_{i\ge2}t^{-i}
=\frac12\cdot\frac{t^{-2}}{1-t^{-1}}=\frac{1}{2t(t-1)}$（$t>1$）。

9.2 分母界：$s=\lceil\eta\rceil-1$ 满足 $\eta-1\le s<\eta$（左端：$\lceil\eta\rceil\ge\eta$；
右端：$\lceil\eta\rceil<\eta+1$）。由 $s\ge\eta-1$ 得 $t+\eta-1-s\le t$；又
$t+\eta-1=K\eta$。故
$$\frac{s}{(t+\eta-1-s)(t+\eta-1)}\ \ge\ \frac{s}{t\cdot K\eta}.$$

9.3 合并：结合 9.1、9.2 与 $t-1=(K-1)\eta$，
$$\frac{d\ln\Lambda}{dt}>\frac{s}{t\,K\eta}-\frac{s-1}{t(t-1)}-\frac{1}{2\eta\,t(t-1)}
=\frac{1}{t}\Big[\frac{s}{K\eta}-\frac{s-1+\frac{1}{2\eta}}{(K-1)\eta}\Big].$$
（当 $s=0$ 时 $-\frac{s-1}{t(t-1)}$ 为正，下式的充分条件同样覆盖该情形。）
括号非负等价于 $s(K-1)\ge K\big(s-1+\frac{1}{2\eta}\big)$，即
$$K\cdot\frac{2\eta-1}{2\eta}\ \ge\ s .$$

9.4 该充分条件成立：$K\ge p=s+1$，故
$K\frac{2\eta-1}{2\eta}\ge(s+1)\frac{2\eta-1}{2\eta}$，而
$$(s+1)\frac{2\eta-1}{2\eta}-s=\frac{2\eta-s-1}{2\eta}\ \ge\ 0
\quad\Longleftrightarrow\quad s\le2\eta-1 .$$
由 9.2 有 $s<\eta$，又 $\eta\ge1$ 给出 $\eta\le2\eta-1$，故 $s<\eta\le2\eta-1$，条件成立。

结论：$\frac{d\ln\Lambda}{dt}>0$，$\Lambda$ 关于 $t$（从而关于实数 $K\ge p$）严格递增；
特别地对整数 $K\ge p$ 有 $\Lambda(K+1)>\Lambda(K)$。

依据：Step 8 的闭式；$\eta\ge1$（definition1.md）；$K\ge p$（Step 5 的 argmax 非零条件）。
状态：[HAND-PROOF-UNREVIEWED] + [VERIFIED-EXHAUSTIVE]（脚本检查 C8：exact rational 下
$\Lambda(K+1)>\Lambda(K)$，17 个 $\eta$、$p\le K\le60$，最小比值 $1.0000226$（$K=60,\eta=10$）；
C11：$\frac{d\ln\Lambda}{dt}$ 在同一网格及每格 $1/3,2/3$ 偏移处的 mpmath 50 位数值最小为
$2.248\times10^{-6}>0$；C11b：$\Sigma(t)<\frac{1}{2t(t-1)}$；C10：充分条件
$K\frac{2\eta-1}{2\eta}\ge s$）。

---

**Step 10（$\rho_K$ 非增且从 $K\ge\lfloor\eta\rfloor$ 起严格递减，(C-d)(C-f)）**

写 $F:=\lfloor\eta\rfloor$，$p=\lceil\eta\rceil$。

- 区间 I（$1\le K\le F$）：Step 6 给出 $\rho_K=\frac1\eta$，常数，故非增。
- 交界（$K=F\to K+1=F+1$）：
  - 若 $\eta$ 非整数，则 $F+1=p$，由 Step 6 的 (⇒) 方向（$F+1>\eta$）得
    $\rho_{F+1}<\frac1\eta=\rho_F$，严格递减。
  - 若 $\eta$ 为整数，则 $F=p=\eta$，$\rho_F=\frac1\eta=1-\Lambda(p)$（Step 8 末尾的一致性），
    而 Step 9 给出 $\Lambda(p+1)>\Lambda(p)$，故 $\rho_{F+1}=1-\Lambda(p+1)<\rho_F$。
- 区间 II（$K\ge p$）：$\rho_K=1-\Lambda(K)$，由 Step 9 严格递减。

综合：$\rho_K$ 在整个 $K\ge1$ 上非增；并且对所有 $K\ge F=\lfloor\eta\rfloor$ 有
$\rho_{K+1}<\rho_K$，即 "从 $K\ge\lfloor\eta\rfloor$ 起严格递减"。
（注意：当 $\eta$ 非整数时区间 I 与区间 II 无缝衔接，因为 $F+1=p$；当 $\eta$ 为整数时
$F=p$，两区间在 $K=\eta$ 处重叠且取值一致。）

依据：Step 6、Step 8、Step 9。
状态：[HAND-PROOF-UNREVIEWED] + [VERIFIED-EXHAUSTIVE]（脚本检查 C9，17 个 $\eta$、$K\le60$，
exact rational，非增与从 $\lfloor\eta\rfloor$ 起严格三项全过）。

---

**Step 11（$\rho_K$ 的极限，(C-b)）** $\lim_{K\to\infty}\rho_K(\eta)=1-e^{-1/\eta}$，从上方。

- 上界：由 Step 1，$\rho_K\le V_K=U_K(\eta)=1-q^K$。而
  $$K\ln q=K\ln\Big(1-\frac{1}{k_1}\Big)=-\frac{K}{k_1}+O\Big(\frac{K}{k_1^2}\Big),
  \qquad \frac{K}{k_1}=\frac{K}{(K-1)\eta+1}\xrightarrow[K\to\infty]{}\frac1\eta,$$
  且 $\frac{K}{k_1^2}\to0$，故 $q^K\to e^{-1/\eta}$，即 $U_K(\eta)\to1-e^{-1/\eta}$。
- 下界：Step 7 给出 $\rho_K\ge1-e^{-1/\eta}$ 对所有 $K$。
- 夹逼：$1-e^{-1/\eta}\le\rho_K\le U_K(\eta)\to1-e^{-1/\eta}$，故 $\rho_K\to1-e^{-1/\eta}$。
  再由 Step 10 的非增性与 Step 7 的下界，收敛是**从上方**且单调的。

依据：Step 1、Step 7、Step 10。
状态：[HAND-PROOF-UNREVIEWED] + 数值确认见第 3 节（$\eta=3/2$，$K=1000$ 时
$\rho_K=0.4868110664$ 对 $1-e^{-2/3}=0.4865828810$）。

---

**Step 12（汇总）** (C-a)(C-c)(C-g 的 $L$ 部分) 来自 Step 2 与 Step 3；(C-e) 来自 Step 6；
(C-d)(C-f) 来自 Step 10；(C-b) 与 (C-g 的 $\rho$ 部分) 来自 Step 7 与 Step 11。
即 `cor:limit` 的全部断言在 "thm:exact 给定 $\rho_K=\min_jV_j$、$j\in\{0,\dots,K\}$" 之下成立，
其中 "$L_K$ 关于 $K$ 单调" 的方向为严格递减。

---

## 3. 数值走查

### 3.1 $\eta=3/2$，$K=1,2,3,4$（exact rational）

$p=\lceil3/2\rceil=2$，$\lfloor\eta\rfloor=1$，$1/\eta=2/3$，$1-e^{-2/3}=0.4865828810$。

| $K$ | $k_1$ | $q$ | $j$ | $h_K(j)$ | $V_j$ |
|---|---|---|---|---|---|
| 1 | $1$ | $0$ | 0 | $1/3$ | $2/3$ |
| | | | 1 | $0$ | $1$ |
| 2 | $5/2$ | $3/5$ | 0 | $1/3$ | $2/3$ |
| | | | **1** | $\mathbf{2/5}$ | $\mathbf{3/5}$ |
| | | | 2 | $9/25$ | $16/25$ |
| 3 | $4$ | $3/4$ | 0 | $1/3$ | $2/3$ |
| | | | 1 | $5/12$ | $7/12$ |
| | | | **2** | $\mathbf{7/16}$ | $\mathbf{9/16}$ |
| | | | 3 | $27/64$ | $37/64$ |
| 4 | $11/2$ | $9/11$ | 0 | $1/3$ | $2/3$ |
| | | | 1 | $9/22$ | $13/22$ |
| | | | 2 | $54/121$ | $67/121$ |
| | | | **3** | $\mathbf{1215/2662}$ | $\mathbf{1447/2662}$ |
| | | | 4 | $6561/14641$ | $8080/14641$ |

（粗体为 $\max_jh_K(j)$ / $\min_jV_j$。）

核对 Step 5：$j^\ast_K=\max\{0,K-p+1\}=\max\{0,K-1\}$，给出 $0,1,2,3$，与表一致。
核对 Step 8：$\Lambda(3)=\big(\frac34\big)^{3-2+1}\big(1-\frac{1}{3\cdot3/2}\big)
=\frac{9}{16}\cdot\frac{7}{9}=\frac{7}{16}$，与表一致。
核对 Step 6：$\lfloor\eta\rfloor=1$，故只有 $K=1$ 落在 plateau，$\rho_1=2/3=1/\eta$；
$K\ge1$ 起严格递减：
$$\rho_1=\tfrac23=0.666667>\rho_2=\tfrac35=0.6>\rho_3=\tfrac{9}{16}=0.5625
>\rho_4=\tfrac{1447}{2662}=0.543576 .$$
核对 Step 7：全部 $h_K(j)\le e^{-2/3}=0.5134171$，表中最大值 $0.456424$，成立。
核对 Step 2/3：$L_1=2/3=0.666667>L_2=5/9=0.555556>L_3=386/729=0.529492
>L_4=671/1296=0.517747>1-e^{-2/3}=0.486583$。

### 3.2 收敛（$\eta=3/2$）

| $K$ | $\rho_K$ | $L_K$ | $U_K=V_K$ | $1-e^{-1/\eta}$ |
|---|---|---|---|---|
| 1 | 0.6666666667 | 0.6666666667 | 1.0000000000 | 0.4865828810 |
| 2 | 0.6000000000 | 0.5555555556 | 0.6400000000 | 0.4865828810 |
| 3 | 0.5625000000 | 0.5294924554 | 0.5781250000 | 0.4865828810 |
| 5 | 0.5321949188 | 0.5110544856 | 0.5373356340 | 0.4865828810 |
| 10 | 0.5093987245 | 0.4983881747 | 0.5106071020 | 0.4865828810 |
| 50 | 0.4911465694 | 0.4888800684 | 0.4911927197 | 0.4865828810 |
| 200 | 0.4877238076 | 0.4871542971 | 0.4877266679 | 0.4865828810 |
| 1000 | 0.4868110664 | 0.4866970117 | 0.4868111805 | 0.4865828810 |

夹逼 $1-e^{-1/\eta}\le\rho_K\le U_K$ 在每一行都可见。

### 3.3 plateau 的一个正例（$\eta=3$）

$\lfloor\eta\rfloor=3$，故 $\rho_1=\rho_2=\rho_3=1/3=0.3333333333$，而
$\rho_5=0.3183431953$、$\rho_{10}=0.3022776431$、$\rho_{1000}=0.2836676274$，
极限 $1-e^{-1/3}=0.2834686894$。这同时验证了 plateau 的长度恰为 $\lfloor\eta\rfloor$。

### 3.4 关于 "$K=2$（ProbeLottery item）"

任务文本要求 "$K=2$ for the ProbeLottery item"。四个输入文件中没有出现 ProbeLottery 这个
对象（definition1.md、assumptions.md、notation.md、statement_limit.md 均无该词，也无任何
lottery / probe 类算法），`cor:limit` 的陈述里也没有与之相关的分支。在 strict isolation 下
无法补读其定义。保守处理：不臆造该对象，改为给出 $K=2$ 在本推论各分支上的取值，作为替代的
$K=2$ 走查，见 3.1 的 $K=2$ 行（$\rho_2=3/5$，$L_2=5/9$，$U_2=16/25$，$j^\ast_2=1$）。
该缺口记入第 4 节 G1。

---

## 4. 未能闭合的步骤 / 追加的假设

**A1（追加的读法假设，已用）** notation.md 写 $\rho_K=\min_jV_j$ 但未给 $j$ 的范围。本文取
$j\in\{0,1,\dots,K\}$。理由（保守选择的记录）：$V_0=1/\eta$ 恰是 plateau 值，若把 $j=0$
排除则 $K\le\lfloor\eta\rfloor$ 时 $\min_{j\ge1}V_j=V_1>1/\eta$，与待证的 plateau 断言矛盾；
$V_K=U_K(\eta)$ 恰是 notation.md 中 "value of the per-$K$ tightness family"，若把 $j=K$
排除则 Step 11 的上界失去来源。两个端点同时可解释，唯有 $\{0,\dots,K\}$。若原文的范围实为
$\{1,\dots,K\}$ 或 $\{0,\dots,K-1\}$，本文的 Step 6 与 Step 11 需要重做。
状态：[CONJECTURE]（关于原文意图），但在该读法下后续推导完整。

**A2（量词上的一个缝隙）** assumptions.md 规定 $1\le K\le n$。`cor:limit` 取 $K\to\infty$，
因此该极限只能在 $n$ 同步趋于无穷的 instance 族上理解；换言之 $\rho_K$ 被当作与 $n$ 无关的量
（notation.md 写作 $\rho_K(\eta)$ 而非 $\rho_{n,K}(\eta)$，thm:exact 的 $V_j$ 也不含 $n$）。
本文按 "$\rho_K$ 与 $n$ 无关，只要 $n\ge$ 某个依赖 $K$ 的阈值" 来读。这一点在输入文件里没有
显式写出，属于本文追加的读法。若实际结果是 $\rho_{n,K}$ 且对有限 $n$ 有别的值，(C-a)(C-b)
的陈述需要补 "$n\ge n_0(K)$" 或 "$n\to\infty$" 的量词。
状态：[CONJECTURE]（关于原文意图）。

**A3（thm:exact 作为给定）** 本文按任务要求把 $\rho_K=\min_jV_j$ 当作已知，没有独立验证
"predictive greedy 的 exact worst case 等于该最小值"。因此 (C-b)(C-d)(C-e)(C-f) 的正确性
条件性地依赖 thm:exact。本文未接触该定理的证明。
状态：[HAND-PROOF-UNREVIEWED]（条件性）。

**F1（一条被证伪的中间引理，记录以免他人重走）** 我先尝试的单调性证法是配对
$h_{K+1}(j+1)\ge h_K(j)$（对所有 $0\le j\le K$），它**不成立**：
$\eta=10$、$K=4$、$j=1$ 时
$$h_4(1)=\frac{111}{124}=0.8951612903,\qquad h_5(2)=\frac{1504}{1681}=0.8947055324,$$
即 $h_5(2)<h_4(1)$。同样的失败在 $\eta=10$ 的 $K=4,\dots,8$（$j=1$）与 $\eta=100$ 的一大片
$(K,j)$ 上出现。这些 $(K,j)$ 都落在 plateau 区（$K\le\lfloor\eta\rfloor$，此时 argmax 为
$j=0$），所以不影响结论，但把该配对当成引理会得到错误的证明。第 2 节改用 Step 5 的 argmax
闭式，只在 $j=j^\ast_K$ 处比较（$j^\ast_{K+1}=j^\ast_K+1$）。
状态：[FAILED]，失败的不等式为 $h_{K+1}(j+1)\ge h_K(j)$，参数 $\eta=10,K=4,j=1$。

**F2（Bernoulli 化的多项式证书）** 为 F1 配套的多项式证书
$K^2\eta[(K-1)B+j](D+\eta)-(K^2-1)B^2D\ge0$（$B=K\eta+1$，$D=K(\eta-1)+j$）在同一参数
$\eta=10,K=4,j=1$ 处为负（$932480<932955$），随 F1 一并作废。
状态：[FAILED]。

**G1（无法完成的任务项）** 任务要求 "$K=2$ 的 ProbeLottery item" 走查。四个输入文件中不存在
ProbeLottery，strict isolation 下无法取得其定义或与 `cor:limit` 的关系，故未完成；替代内容见
3.4。
状态：[FAILED]（原因：输入包缺该对象的定义）。

**G2（未做 oracle 的部分）** Step 2、3、7、9、11 的一般 $\eta$、一般 $K$ 论证是手写微积分，
oracle 只在 17 个 $\eta$ 值（$1,1.1,1.25,1.5,2,7/3,2.5,3,3.5,4,4.5,5,6,8.5,10,100,1000$）
与 $K\le60$ 的网格上做了 exact rational / 50-60 位数值确认，不是对全参数域的证明。
Step 1、4 的恒等式有 sympy 符号确认，属 [VERIFIED-SYMBOLIC]。
状态：[HAND-PROOF-UNREVIEWED] + [VERIFIED-EXHAUSTIVE]（网格）。

---

## 5. 读过的文件

- `/home/user/sub-modular-optimization/results/V11/inputs/definition1.md`
- `/home/user/sub-modular-optimization/results/V11/inputs/assumptions.md`
- `/home/user/sub-modular-optimization/results/V11/inputs/notation.md`
- `/home/user/sub-modular-optimization/results/V11/inputs/statement_limit.md`
- `/home/user/sub-modular-optimization/CLAUDE.md`（由 harness 自动置入上下文的 house rules，
  非数学输入）

自写文件（本次新建，未修改任何已有文件）：
- `/home/user/sub-modular-optimization/results/V11/route2/verify_limit.py`
- `/home/user/sub-modular-optimization/results/V11/route2/limit.md`（本文件）
