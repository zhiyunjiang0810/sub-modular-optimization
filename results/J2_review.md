# J2 独立联合审查报告

日期：2026-09-07。对象：`submodular_review_20260907.zip` 与配套 27 页 `main (1).pdf`。再次上传的同名带 `(1)` 文件与前一份逐字节相同。本报告接续 J1，并以此次完整源码为准。

**结论：R6 的关键归约可以闭合，精确最坏值主定理的核心证据通过本次核验。Hardness 的两支公式没有遗漏第三支，但它计算的是最小对称误差带；按论文实际使用的误差乘积重新校准，可以得到更强、更简单的界。需要优先改写的是 selection-error 定义、实验的 certificate 表述，以及查询类“最优”的范围。**

本次没有把有限测试提升成任意规模的机器证明。下文区分符号恒等式、有限 LP/精确穷举、一般手工装配；概率与 adaptive transcript 的一般证明仍标 `[HAND-PROOF-UNREVIEWED]`。主定理通过本次审查不等于全文已达到可直接投稿的状态。

## 1. 对交接文档五项请求的答复

| 请求 | 独立审查结果 | 证据与范围 |
|---|---|---|
| R6 四族约束，特别是 case (c) | PASS。case (c) 的 consistency slack 恒为零；case (b) 有独立非负 slack 分解 | `J2_core_oracles.py`；一般参数恒等式与 1,536 个全格点 LP |
| Proposition 5 非正步修法 | 推荐重定义每一步的误差：有害零步取无穷大，全部候选增益为零时取 1 | J1 三元素严格反例、1,905 条小实例轨迹；J2 子图 coverage 反例及数据复算 |
| Hardness 的两支是否穷尽 | 是，四类全局边际可穷尽；另发现实际误差乘积比对称带更小 | 一般参数恒等式；264 个精确实例、57,728 条边；附替换证明草稿 |
| GS 2007 的参数方向 | 当前稿的 `alpha = eta_sel` 正确，且必须覆盖每一步 | 核对原文第 7 页 Step 2 与 Theorem 1 |
| 对偶在 `t=j` 的配平 | PASS；未发现该分支错误 | 字面分子恒等式为零；456 个精确有理加权求和检查；原 N1 320/320 |

交接文档的编号落后一位。当前 PDF 中：逐 K tightness 是 **Theorem 7**，coherence 是 **Lemma 8**，精确值是 **Theorem 9**，ceiling 是 **Theorem 11**，hardness 是 **Theorem 13**，查询类最优性是 **Remark 14**。以下优先使用源码标签，避免编号混淆。

## 2. R6：给出独立证明，最担心的 case (c) 没有反例

位置：`paper/sections/appendix_proofs.tex`，`app:validity`，从第 1236 行开始。

状态：`[VERIFIED-SYMBOLIC：下列 slack 恒等式]`；`[VERIFIED-LP：有限全格点搜索]`。非负性依赖的每个模型前提写在下文；有限 LP 本身不代替一般归约论证。

令最优值归一化为 1，`d_t` 是选中元素的真实增益，`g_{t,i}` 是最优元素 `o_i` 的真实增益，已选入时按原文置零。令 `eta = eta_u eta_o`。四族约束为

\[
\sum_i g_{t,i}+\sum_{s<t}d_s\ge1,\qquad
d_t-\frac{g_{t,i}}\eta\ge0,
\]
\[
g_{t,i}-g_{t+1,i}\ge0,\qquad
\left(1-\frac1\eta\right)g_{t+1,i}-g_{t,i}+d_t\ge0.
\]

### 2.1 Case (b) 的非负 slack 分解

固定状态 `S`、选中元素 `e` 与另一个未选最优元素 `o`。简记

\[
d=d_e(S),\quad g=d_o(S),\quad h=d_o(S\cup\{e\}),
\]
\[
P=\widetilde d_e(S),\quad Q=\widetilde d_o(S),\quad
R=\widetilde d_o(S\cup\{e\}).
\]

因为两边来自同一个 set function，另一侧真实与预测边际分别是 `d+h-g` 与 `P+R-Q`。Greedy 给出 `P >= Q`。直接配平得到

\[
d-\frac g{\eta_u\eta_o}
=\frac{\eta_o d-P}{\eta_o}
+\frac{P-Q}{\eta_o}
+\frac{\eta_uQ-g}{\eta_u\eta_o}.
\]

右侧三项依次由选中边的上误差带、greedy、候选边的下误差带非负，得到 prediction 约束。

关键的 consistency 约束有同样明确的证书：

\[
\boxed{
\left(1-\frac1{\eta_u\eta_o}\right)h-g+d
=\frac{\eta_o(d+h-g)-(P+R-Q)}{\eta_o}
+\frac{P-Q}{\eta_o}
+\frac{\eta_uR-h}{\eta_u\eta_o}.}
\]

三项分别使用离轨边 `e` 在 `S∪{o}` 的上误差带、greedy、以及边 `o` 在 `S∪{e}` 的下误差带。每项非负。这也精确指出为什么该约束需要**全局**误差带，不能仅用访问过的状态或 selection error 替代。

这一分解不要求预测器 submodular；只要求预测边际来自同一个 `ftilde`，且满足相应误差带。`g >= h` 则直接来自真实目标的 diminishing returns。

### 2.2 Cases (a)、(c) 与 coverage

| 情形 | 代入 | 三个逐元素约束 |
|---|---|---|
| (a) `o_i` 已选入 | `g_{t,i}=g_{t+1,i}=0` | prediction 与 consistency 的 slack 均为 `d_t >= 0`；mono 为零 |
| (c) `o_i=e_t` | `g_{t,i}=d_t`，`g_{t+1,i}=0` | prediction 为 `d_t(1-1/eta)>=0`；mono 为 `d_t>=0`；consistency **恰为零** |

Coverage 使用

\[
1=f(O^*)\le f(S^t\cup O^*)
\le f(S^t)+\sum_{o_i\notin S^t}d_{o_i}(S^t)
=\sum_{s<t}d_s+\sum_i g_{t,i}.
\]

中间一步对 `O*\S^t` 逐个加入并使用 diminishing returns，已选最优元素自然不再出现。若最优值为零，近似不等式平凡；否则归一化合法。

### 2.3 Oracle 如何避免循环论证

新脚本并非只检查 reduced LP 自己的约束。它以全格点上的真实函数值和预测函数值为变量，加入真实 monotonicity/submodularity、全局误差带、指定 greedy 路径与最优集条件，然后分别**最小化待审查约束的 slack**。

覆盖 `(n,K)=(4,2),(5,3)`、所有最优 K-set、四组误差带 `(1,1),(1,2),(2,1),(2,2)`，共 1,536 个目标。最小 slack 约为 `-6.7e-16`，在求解器舍入范围内；三种交叠情形全部实际出现。该结果与上面的独立代数证书一致。

## 3. 精确值主定理：核心通过，端点附带表述需修

位置：`app:exact`、`thm:exact`。

`[VERIFIED-LP]` 原 `N1_dual_certificate.py` 复跑 **320/320**，原 `N2_check.py` 复跑 **480/480**。另用独立的 `Fraction` 实现，遍历 `K=2..17` 的全部 j，检查有限分段的端点、中点，并在 `j=0` 的无界段取三个测试点；包含 `eta=1` 可去奇点。非负乘子和字面加权求和共 **456** 例全部通过。

`[VERIFIED-SYMBOLIC]` 令 `v=K-j`、`k_1=(K-1)eta+1`，原文 `t=j` 配平中的分子

\[
K\eta(\eta-1)(v+1-\eta)
-k_1(\eta-v)-(v-1)\eta k_1
+(\eta-1)^2(K\eta-v)
\]

恒为零。原文的中间两项可以合并成 `-k_1 v(eta-1)`，没有隐藏的段内假设。

**mono 乘子恒为零不是漏洞。** 它表示该族 LP 约束对这份最优对偶证书不承重；不能据此删掉真实目标的 submodularity，因为 coverage 约束的归约仍使用它。

需要修正两处附带细节：

1. `V_i-V_{i+1}` 的索引应为 `0 <= i <= K-2`。当前写到 `K-1` 会用到未定义的 `V_K`，不影响后续实际比较的相邻项。
2. 严格偏好扰动“固定 j，取 eta'<eta”没有处理段的左端点。`[VERIFIED-LP：精确有理反例]` 在 `K=3,j=1,eta=2`，取 `eta'=19/10` 后，原 capped 构造在 `(x,z,y)=(1,2,2)` 加最后一个 O 元素的增益为 **-1/72**，失去 monotonicity。N2 的严格扰动测试只覆盖所选内点，不能消除此端点问题。

建议的端点补法：整数端点 `eta>=2` 使用相邻的 `j+1` 段从左侧逼近；`eta=1` 另对真实函数与预测器同时加入趋零的适当正 modular 扰动。前者利用相邻分支端点相等，后者保留 `ftilde=f`。这段修复的一般装配暂标 `[HAND-PROOF-UNREVIEWED]`，需要写清扰动顺序与极限。它不影响以 adversarial tie 为前提的主定理。

## 4. Selection error：推荐重定义，保留事后证书

位置：`model.tex` 的 `def:etasel`、`results.tex` 的 `prop:guarantee` 与 `rem:etasel-measurable`。

### 4.1 旧定义的反例与最小修法

`[FAILED：旧的无条件 certificate 表述]`。三元素 modular 反例即可排除 tie 与非 submodularity 的干扰：真实权重 `(1,1,0)`，预测权重 `(2,1,3)`，预算 `K=2`。Greedy 严格依次选第三、第一元素，输出比为 `1/2`。旧定义跳过第一步的真实零增益，留下 `eta_sel=1`，却声称下界 `L_2(1)=3/4`。两函数都 normalized、monotone、submodular；它不满足有限的全局误差带，而这正是无条件事后证书原本不想额外要求的前提。

令

\[
M_t=\max_{e\notin S^t}d_e(S^t),\qquad g_t=d_{e_t}(S^t),
\]

建议用下面的完整定义替换：

\[
a_t=\begin{cases}
M_t/g_t,&g_t>0,\\
1,&M_t=g_t=0,\\
\infty,&g_t=0<M_t,
\end{cases}
\qquad
\boxed{\eta^{\mathrm{sel}}=\max\{1,a_0,\ldots,a_{K-1}\}.}
\]

保留真实目标 normalized、monotone、submodular 的前提，定义 `L_K(infinity)=0`。出现真实负增益意味着实例已超出此前提，不能靠丢弃该步来“修复”证书。

三种修法中，**推荐这一种**：它只修补定义的未覆盖情形，继续允许只凭真实目标与完成的轨迹出具证书。添加全局 Definition 1 虽然数学上可行，却引入事后往往不可检查的前提；只保留全正步 run 则丢弃了 `M_t=0` 这类已经无损停止的情形，并容易掩盖筛选比例。

### 4.2 保证、零步与 tightness 的连锁影响

当 `a_t` 有限时，coverage 给出

\[
f(O^*)-f(S^t)\le K M_t\le K a_tg_t.
\]

若 `M_t=g_t=0`，coverage 与最优性说明当前已达到最优值，取 `a_t=1` 不会制造虚假保证；有害零步取无穷大时，统一的 `L_K` 界退化为零。

若希望保留其余好步骤的信息，可另外报告逐步乘积界

\[
\frac{f(S^K)}{f(O^*)}
\ge 1-\prod_{t=0}^{K-1}\left(1-\frac1{Ka_t}\right),
\qquad 1/\infty=0.
\]

此界对有害零步给收缩因子 1，不把此前及此后的有效进展抹掉。三元素反例中它给出 `1/2`，恰好取等。`[VERIFIED-LP]` J1 用精确算术检查了 1,905 条小实例轨迹，统一界和乘积界全部通过；一般递推装配保留 `[HAND-PROOF-UNREVIEWED]` 标签。这仍要求真实目标满足模型，不能用于挽救 E1/E3 的负边际。

有限全局误差带下，有害零步不会发生：预测选中边为零会使所有候选预测边际为零，有限带又使所有真实候选增益为零。因此修法保留 `eta_sel <= eta_tr <= eta` 的链，也保留 Theorem 7 原达到实例的 `eta_sel=eta_tr=ahat` 与逐 K 取等。

关于内部审稿将 tie 视作致命问题的判断，需要收敛措辞。若某步实现 `M_t/g_t=eta_tr=A>1`，则沿轨迹误差带有

\[
M_t/\eta_u\le\widetilde M_t
\le\widetilde g_t\le\eta_o g_t=M_t/\eta_u,
\]

这里 `widetilde M_t` 指真实最佳候选的预测边际。整条链被迫取等，所以精确实现两把轨迹尺相等时，至少存在这种 tie。该等号论证的手工装配标 `[HAND-PROOF-UNREVIEWED]`。Adversarial tie 是明示的 worst-case 模型，并不自动使定理无效；严格扰动应另行陈述其误差与极限。

### 4.3 GS 2007 的归属与参数方向

原文第 7 页 Step 2 要求 `alpha * selected_gain >= best_gain`；Theorem 1 给出的 `OPT/ALG` 上界是 `1/[1-(1-1/(alpha K))^K]`。换成本稿 `ALG/OPT` 的方向，正是 `L_K(alpha)`，所以 **alpha = eta_sel，不能取倒数**。这一实例化要求每一步满足近似选择条件；旧定义排除的有害零步不满足该条件。[Goundan–Schulz，原文第 7 页](https://optimization-online.org/wp-content/uploads/2007/08/1740.pdf)

继续采用 “essentially due to” 与完整性附录是正确的。新的有限 K 精确式和全局 coherence 结构应单独说明贡献，不能从经典保证的归属直接推断整篇论文“没有正面结果”。本次没有进行全面的新颖性文献检索。

## 5. 两把误差尺：不能把 rho 当作 selection-error 保证

`[VERIFIED-LP：全格点精确反例]`。取 `K=2`，`C`、`O` 各两个元素，记 `x=|S∩C|, y=|S∩O|`，令

\[
f(S)=1-(3/4)^x(1-y/2),\qquad
\widetilde f(S)=1-(1/3)^x(1-y/2).
\]

两函数均 monotone submodular，且全局误差有限。每一步 C 的预测增益严格大于 O 的预测增益；Greedy 选满 C。精确结果是

\[
\eta^{\rm sel}=2,\quad\eta^{\rm tr}=6,\quad\eta=27/2,
\qquad\frac{f(T)}{f(O^*)}=\frac7{16}=L_2(2)<\rho_2(2)=\frac12.
\]

因此，即使修复零步、即使预测器也 submodular、即使全局 band 有限，把 `rho_K(eta_sel)` 称为该 run 的精确最坏保证仍然错误。这个反例不依赖预测器在 C 与 O 间的 tie。

建议主图按横轴的语义组织：selection-error 图的保证曲线是 `L_K`；若保留 `rho_K`，必须明确是另一误差类的参照曲线，不能称为这张图上所有 run 的 worst-case envelope。需要展示全局精确值时，用已知全局 `eta` 的构造实例单独作图。不同 K 的 E4 对照点也应放在相同 K 的曲线下比较。

## 6. Hardness：两支完备，但可改成更强的闭式

位置：`app:hardness`、`thm:hardness`。可插入的英文完整草稿见 `J2_hardness_repair.tex`。

### 6.1 全局边际表：无遗漏第三支

取整数 `1<=tau<K`、`theta>=1`、`a=1-1/(theta K)`。原构造是

\[
F=\theta^{-1/2}[1-a^x(1-y/K)],
\]
\[
G=\begin{cases}
1-a^{x+y},&y\le\tau,\\
1-a^{x+\tau}(K-y)/(K-\tau),&y\ge\tau.
\end{cases}
\]

两式在 `y=tau` 相等。对真实增益非零的边，令 `r=Delta G/(sqrt(theta) Delta F)`，完整列表为：

| 方向 | 起点范围 | `r` |
|---|---|---|
| x | `0<=y<=tau` | `a^y K/(K-y)` |
| x | `tau<=y<K` | `A=a^tau K/(K-tau)` |
| y | `0<=y<=tau-1` | `a^y/theta` |
| y | `tau<=y<K` | `A` |

`y=K` 的 x 边两增益都为零；从 `y=K` 出发没有可行 y 边。跨出 balanced strip 的边已经是第四行，所有 x 坐标均在公式中消去，所以结论不受 n 增长影响。

令 `B=a^(1-tau)`。第一行随 y 递增，因为

\[
\frac{h_{y+1}}{h_y}-1
=\frac{(\theta-1)K+y}{\theta K(K-y-1)}\ge0,
\quad h_y=a^yK/(K-y).
\]

第三行递减，最小值是 `1/(theta B)`。因而最大、最小比值分别在表内达到，不需要诉诸“其余边由 LP 保证”。

`[VERIFIED-SYMBOLIC]` 四类边、拼接点、零边、真实函数的一二阶差分和误差乘积均通过符号恒等式核验。`[VERIFIED-LP]` 精确有理格点检查覆盖 `K=2..12`、每个整数 `tau=1..K-1`、`theta∈{1,6/5,2,4}`、`0<=x<=K+2,0<=y<=K`，共 264 实例、57,728 条边。

### 6.2 原 Phi 是最小对称带，不是该实例的实际误差乘积

从全边表得到原函数对的最小可行误差因子：

\[
\eta_o^{\rm act}=\sqrt\theta A,\qquad
\eta_u^{\rm act}=\sqrt\theta B,
\]
\[
\boxed{\eta^{\rm act}=\theta AB=\frac{\theta K-1}{K-\tau}.}
\]

两因子都至少为 1，符合 Definition 1。原文

\[
\Phi(\theta)=\theta\max\{A,B\}^2
\]

确实是强制 `eta_u=eta_o=sqrt(theta)s` 时的最小共同带乘积，但通常大于实际乘积。例：`K=4,tau=1,theta=4`，实际因子 `(eta_u,eta_o)=(2,5/2)`，实际 `eta=5`，而 `Phi(4)=25/4`。

因此 Step 4 关于这个**未缩放 witness**“误差恰为 eta”的解释不成立；若只要求误差至多 eta，原构造仍可用。这不是对原 hardness 存在性结论的反例，而是其 exact-error 证明与参数校准的缺口。

若需要预先指定误差拆分，可把预测器乘以

\[
\beta=\frac{\eta_o}{\sqrt\theta A},
\qquad\eta_u\eta_o=\eta^{\rm act}.
\]

两端就分别达到所需 `eta_o` 和 `1/eta_u`。Balanced profile 同时乘上常数，仍不泄露隐藏集身份。特别地，`beta=sqrt(B/A)` 得到实际对称拆分。

### 6.3 建议替换的有限 K 上界

令实数 `c>=0`，取整数 `tau=ceil(c)+1`。若

\[
K>\tau,\qquad n\ge4K^{c+2},\qquad
\eta>1,\quad\eta\ge\frac{K-1}{K-\tau},
\]

则可取

\[
\bar\theta=\frac{\eta(K-\tau)+1}{K}\ge1.
\]

同一隐藏最优集构造给出的候选加强结论为：对至多 `n^c` 次、每次集合大小至多 K 的确定性查询算法，存在实际误差恰为 eta 的实例，使

\[
\boxed{\frac{f(T)}{f(O^*)}\le
H_{K,\tau}(\eta)
=1-\left(1-\frac1{\eta(K-\tau)+1}\right)^K
=L_K(\bar\theta).}
\]

Randomized 版对期望值增加

\[
\varepsilon_n=\frac Kn+
\frac{K^{2\tau+2}}{(\tau+1)!n^{\tau+1-c}}.
\]

整数 c 时，这正好回到原稿的 additive term。取 `ceil(c)` 是为了修复原稿 `c>=0` 未要求整数、却直接把 `tau=c+1` 用作组合数和阶乘计数阈值的问题。

| K | c | eta | 原反函数校准上界 | 新上界 | `L_K(eta)` |
|---:|---:|---:|---:|---:|---:|
| 8 | 1 | 2 | 0.485451 | 0.472888 | 0.403281 |
| 16 | 2 | 2 | 0.458480 | 0.453295 | 0.398290 |
| 32 | 2 | 3 | 0.316269 | 0.306302 | 0.284720 |
| 64 | 3 | 1.5 | 0.511796 | 0.506972 | 0.488375 |

这里 hardness 上界越小越强。对同一整数 tau，`Psi(theta)=theta AB<=Phi(theta)`，所以新设计参数不小于旧反函数参数，而 `L_K` 随参数增大而减小。这解释了表中改善的方向。

一般证明的状态必须拆开：代数与极限为 `[VERIFIED-SYMBOLIC]`，表中数值与有限格点为 `[VERIFIED-LP]`，任意 adaptive/randomized 算法的概率装配为 `[HAND-PROOF-UNREVIEWED]`。附带 TeX 已写出 canonical transcript、并集界与两次平均，没有以有限实例测试代替这一部分。

具体地，先在不依赖隐藏 O 的 canonical profile 下固定查询和输出，再对 O 取并集界，不能反过来把实际自适应查询当作固定集合。坏查询概率不超过第二项；输出与 O 相交的概率不超过 `K^2/n`。给定 n 下两项分别至多 `1/32`、`1/4`，足够保证确定性所需的 O 存在。随机版先固定 random seed，最后平均得到一个对算法期望值成立的 O。这与原稿的总体证明结构一致。

实际 inflation 也简化为

\[
\delta_{\rm act}(\theta)=AB-1
=\frac{\tau-1/\theta}{K-\tau},\qquad
K\delta_{\rm act}(\theta)\to\tau-1/\theta.
\]

固定 c、eta 时，新上界仍趋于 `1-exp(-1/eta)`。无需对 max 的两支反求参数。

### 6.4 对既有 N5 与 J1 结论的校正

原 `N5_delta_at_etahat.py` 本次为 **40 PASS、0 FAIL、2 SKIP**。但它使用旧的显式 `etahat=eta/(1+delta(eta))` 校准，不是当前正文的 `Phi^{-1}`；不能把这次运行称为当前反函数定理的直接验证。

`2-1/tau` 是两支主导项的渐近分界，有限 K 的精确交点是

\[
\theta_*=\frac1{K\left[1-(1-\tau/K)^{1/(2\tau-1)}\right]}.
\]

J1 指出的有限分界错误确实出现在 `RESEARCH_STATE.md` 与 brief 的旧措辞中；读到完整包后可确认，N5 当前有关分界的说明已指明一阶意义，不能把旧文字问题重复算成 N5 新错误。

另一个局部排版错误是 `Phi` 第二支对 theta 求导时多了 `1/K`。例如 `K=4,tau=1` 应为 1，打印式给 1/4。正号不变，因此不推翻原可逆性论证。

## 7. “查询类最优”需要比一个查询数笔误更大的修订

位置：`rem:hardness-pins`。

直接 predictive greedy 的预测值查询数至多

\[
\sum_{t=0}^{K-1}(n-t)=Kn-K(K-1)/2,
\]

可缓存当前集的值。每步不是 K 次查询。将 greedy 下界与 hardness 上界合并成“该查询类的最优渐近值”，需要先保证这一类容纳 greedy；`nK<=n^c` 是充分条件，例如整数 `c>=2` 且 `K<=n`。

`[VERIFIED-LP：精确穷举反例]` 对 `c=0`，算法只有一次集合大小至多 K 的查询。考虑它获得零回答时的查询 Q 和输出 T，在 `Q∪T` 外隐藏两个元素，真实 modular 权重 `(1,1)`、预测权重 `(1,2)`，其余权重为零。回答确实为零，实际误差恰为 2，而输出比为零。

新脚本对 `n=16,K=2` 的所有 Q、T 组合共 **18,769** 对逐一构造了该 witness；这里也满足 `n>=4K^(c+2)`。相同的隐藏两元素论证适用于任意 `K>=2,n>=2K+2`，因此不是仅在小 K 下出现的偏差。故 Remark 14 按所有 `c>=0` 理解时，其正的“最优渐近值”陈述是错的，不能只改每步查询数后保留原句。一般隐藏集论证保留手证状态，有限实例由精确穷举支持。

有限 K 的间隙也宜写作 `O((c+1)/K)`；在包含 `c=0` 时直接写 `O(c/K)` 会把非零间隙写成零。任意查询权下的 `1/eta` ceiling 与有限查询 hardness 不矛盾，比较的是不同查询类。

## 8. 实验复算：不只是已有的 63 个 E3 违例

`[VERIFIED-LP：提供 CSV 的确定性复算，浮点符号容差 1e-9]`。以下“前缀”是同一轨迹在某个预算 K 下的一行，并非独立重复实验。

| 实验 | K>=2 行数 | 比值低于旧 `L_K(eta_sel)` | 含非正选中步的前缀 | 访问状态中观察到负候选边际的前缀 |
|---|---:|---:|---:|---:|
| E1 | 720 | 0 | 295 | 711 |
| E2 | 6,960 | 0 | 225 | 0，coverage 结构保证非负 |
| E3 | 4,377 | 63 | 2,269 | 3,526 |
| 合计 | 12,057 | 63 | 2,789 | 不宜据此比较全局模型满足率 |

63 条与 G5 一致，38 条旧 `eta_sel=1`；最坏一条 `sport_coverage,K=4,seed=7` 是 `0.415324 < 0.68359375`。在 K=5 的主图预算中也有 15 条 E3 低于旧 L 曲线。另有 70 条低于把 selection error 错代入的 rho 曲线；后者不是一个合法的理论违例计数。

### 8.1 E1 也在原 monotone 模型外

E1 的完整候选日志中，720 个预算前缀有 **711** 个在访问状态上实际观察到负真实候选增益，其中 **208** 个前缀选中过负增益元素、**173** 个含有害零步。这些类别可重叠，不能相加。

一条负边际已足够否定该目标的全局 monotonicity；没有观察到负值则不能证明全局成立。即使筛掉非正的**选中**步骤，剩下 425 个前缀也不会因此自动成为 monotone submodular 实例。E1 的“median run certifies”不能保留为原 Proposition 5 的应用。

E3 同理：2,266 个前缀选中过负增益元素，7 个含有害零步。修零步定义能修定理，但不能把 ROUGE 目标变成模型内实例。

### 8.2 E2 的零步问题是真实存在的

E2 的 true/observed coverage 都 monotone submodular，但“观测图是子图”只约束集合覆盖值，不保证二者的**边际零点一致**。在 613,935 条提供的 sampled pair 记录中，有 **30,416** 条真实零、预测正，有 **5,952** 条真实正、预测零；这已经排除这些 pair 上任何有限乘性带。

Sample 文件没有 chosen 标志，因此没有把 sampled 最大值冒充完整候选最大值。做法是：对完整 `E2_rows.csv` 的累计非正步数逐 K 作差，识别选中零步；再用该步任意一个正真实增益的 sampled candidate 证明它是有害零步。共 **16** 个不同零步，**16 个全部有正候选证据**，没有未决步骤；影响 **225** 个 K>=2 前缀，修正后的 `eta_sel` 均应为无穷大。

在 240 条 K=30 轨迹中，16 条受到影响，即约 6.67%；合并步骤的零步率为 `16/(240*30)=0.2222%`。宏 `ETwoNonposPctKMain=0.0` 计算的是**各 run 非正步比例的中位数**，不是总体零步率，更不是“结构上不可能有零步”。`G3_gen_numbers.py` 中相应的 structurally zero 注释应删除。

还给出一个不依赖数据实现的八元素反例：真实无向边为

`{01,02,03,04,34,56,57,67}`，观测边为 `{01,02,34}`，目标为包含自身的闭邻域覆盖。预算 `K=2`。第一步唯一选择节点 0，真实增益 5、预测增益 3；第二步选择 3 或 4，真实增益 0、预测增益 2，而 5、6、7 的真实增益均为 3、预测增益为 1。结果为

\[
\eta_{\rm old}^{\rm sel}=1,\qquad
f(T)/OPT=5/8<3/4=L_2(1).
\]

两个目标都是 coverage，观测图严格是子图；第二步的 tie 只发生在同样坏的候选之间。脚本精确枚举两函数的 256 个集合值及全部 submodular 成对不等式。

### 8.3 OPT 代理与图注

Greedy-on-f 返回的是可行解，因此其值是 **OPT 的下界**。于是 `f(T)/f(greedy_f)` 是真实近似比 `f(T)/OPT` 的**上估计**。正文和图注将分母称作 optimum 的 upper-estimate proxy，方向写反；G5 的相关措辞也应一起纠正。

观察代理比值高于某条保证曲线，并不能验证真实 `ALG/OPT` 高于该曲线。反之，若代理比值已低于合法下界，则真实比值只会更低。小数据集的精确 OPT 检查有帮助，但不能认证所有数据集的代理误差。

建议实验保留三种可清楚解释的产物：E2 的修正后 run certificate（有害零步明确为无穷大，可补逐步乘积界）；E1/E3 的经验 selection diagnostic 与模型违反记录；已知误差与 OPT 的构造实例核验。更新图注，取消“所有真实任务都高于两条保证曲线”及 `rho_K(eta_sel)` 的 certificate 含义。

## 9. 其他会影响结论的局部文字

`rem:exact-gap` 的 submodular-surrogate remark 需要收缩：

- `[FAILED：含 eta=1 的严格改善表述]` 当 `eta=1`，Definition 1 强制 `eta_u=eta_o=1` 且 `ftilde=f`，两个模型完全相同。例如 `K=3` 都为 `19/27`。因此 “strictly improves for eta<K-1” 至少应排除 eta=1；剩余一般区间也不能仅凭几个有限 LP 点宣称。
- 构造失去 admissibility，表示它不再**证明**同一个上界；不等于该上界本身不成立。原句 “so U_K is no longer an upper bound” 的推理不充分。例如稿中给出的 `K=3,eta=1.5` 有 `19/33 < U_3(1.5)=37/64`，此例的 U_K 仍是上界。

对 G5 的总体评价也需区分“缺少 oracle”“陈述有反例”“贡献归属”三个问题。R6 原本只有手证不意味着它错；本次已有独立证书。两支 delta 原本标为 conjecture 也不意味着存在第三支；本次已穷尽全边。Adversarial tie 不是自动否定 tightness 的理由。真正有明确反例的问题，应优先于推测性的创新性或写作风险。

## 10. 修改顺序与交付清单

建议按以下顺序落实：

1. 替换 `def:etasel`，修 `prop:guarantee` 的零步论证及 GS 对应句；定义 infinity 的输出规则。
2. 撤回 E1/E3 的原模型 certificate 用语；重算 E2 的无穷大前缀；修 rho 横轴含义、OPT 代理方向和图注。
3. 将第 2 节的非负 slack 证书加入 `app:validity`，把原“无 oracle”注释改成准确的验证范围。
4. 用 `J2_hardness_repair.tex` 的实际误差校准替换旧反函数装配；限定整数计数阈值与查询类最优性。
5. 修严格扰动端点、submodular-surrogate remark、索引与导数；最后更新 brief、RESEARCH_STATE 和 PDF 中对贡献的表述。

| 文件 | 内容 |
|---|---|
| `results/J2_review.md` | 本报告 |
| `results/J2_core_oracles.py/.json/.log` | R6、对偶、hardness 与校准对比 |
| `results/J2_extra_audit.py/.json/.log` | 图 coverage 反例、查询预算反例、端点反例、CSV 复算 |
| `results/J2_hardness_repair.tex` | 完整的英文替换证明草稿，带验证范围 |
| `results/J2_bound_violations.csv` | 63 条旧 L 界违例 |
| `results/J2_selection_diagnostics.csv` | E1/E3 逐前缀符号与模型诊断 |
| `results/J2_E2_zero_step_evidence.csv` | E2 零步识别、正候选证据及受影响前缀 |
| `results/J2_original_N1.log`、`J2_original_N2.log`、`J2_original_N5_delta.log` | 原 oracle 的本次运行日志 |
| `results/J1_independent_audit.py` 与输出 | 保留不变的精确 selection 反例、两把尺反例与 1,905 轨迹检查 |

复现包包含 J2 所需的六份原始 CSV/压缩 CSV 副本，可独立运行新增检查。J1 文件保留其初审时间点的范围说明，J2 对完整源码的审查结论以本报告为准。未对其余全部文献、所有附带命题和全文版式逐项重新认证。
