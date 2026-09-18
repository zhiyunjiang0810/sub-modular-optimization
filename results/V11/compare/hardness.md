# ROUTE-COMPARISON：thm:hardness（ledger T10，论文 Theorem 3）

TASKS11 Q7，criterion B。本文件只做比对，不修改任何既有文件，未运行 git。

- **路线一（repo proof）**：`paper/sections/appendix_proofs.tex` 的
  `\subsection{Bounded-query hardness}\label{app:hardness}`（第 1461 至 1698 行，七个 paragraph），
  族的参数 `a_theta, A_theta, B_theta, delta(theta), Psi(theta)` 与 `thetabar=Psi^{-1}(eta)` 在
  `paper/sections/results.tex` 第 551 至 585 行（`\subsection{Hardness for bounded-query algorithms}\label{sec:hardness}`），
  定理陈述在同文件第 587 行起；台账卡 `THEOREM_LEDGER.md` 的 `## T10`（第 230 至 246 行）。
  oracle：`results/J2_core_oracles.py`（本轮复跑 `all_passed: true`，264 个精确有理 count-grid 实例、57728 条边、K=2..12、全部整数 tau）与
  `results/H3_j2_recheck.py`（本轮复跑 `ALL PASS`，含 "edge extremes = A and 1/(theta B); eta_act=(theta K-1)/(K-tau)" 一行）。
- **路线二（blind derivation）**：`results/V11/route2/hardness.md`，oracle 脚本 `results/V11/route2/q7_verify_hardness.py`。
- **本轮独立复算脚本**（全部 `sympy` / `fractions.Fraction`，float 只出现在打印里）：
  `/tmp/claude-0/-home-user/09d7d9a5-0b14-54a1-894a-d76a6d641333/scratchpad/judge_hardness.py`（21 条符号恒等式 + 1999 点有理网格穷举）与
  `judge_hardness2.py`（5 组参数上把 `F_O, G_O` 作为真实集合函数在小 ground set 上逐子集重建，检 monotone、submodular、band 极值、`eta_act` 与值上界）。

---

## 1. Step 对应表

"路线一位置" 指 `app:hardness` 的 paragraph 名，或 `sec:hardness` 的定义行。

| 路线二的步骤 | 路线一的对应位置 | 判定 |
|---|---|---|
| Step 1 `H_{K,tau}(eta)=L_K(thetabar)`，`thetabar=(eta(K-tau)+1)/K` [VERIFIED-SYMBOLIC] | `app:hardness` 的 Calibration 段第一个 display；`sec:hardness` 的 `Psi^{-1}(eta)=(eta(K-tau)+1)/K` | 对应，逐字同构。本轮复算 R3/R4 差为 0 [VERIFIED-SYMBOLIC]。差别只在方向：路线一由 `Psi` 的闭式求逆得到 `thetabar`，路线二是从 `H=L_K(thetabar)` 反解出 `thetabar`（它自己在 GAP-5 里注明了这一点） |
| Step 2 `thetabar>=1 <=> eta>=(K-1)/(K-tau)`（需 `K>tau`） [VERIFIED-SYMBOLIC] | `sec:hardness` 末句 "which is at least 1 exactly when `eta>=(K-1)/(K-tau)`" | 对应。本轮复算 R5：`thetabar-1=(K-tau)/K*(eta-(K-1)/(K-tau))`，差为 0 [VERIFIED-SYMBOLIC] |
| Step 3 一致性 `H>=L_K(eta)`（由 `eta*tau>=1`） [VERIFIED-EXHAUSTIVE] | Calibration 段 "Since `eta tau>=1` gives `thetabar<=eta` and `L_K` is decreasing" | 对应，逐字同构。本轮复算：`K=2..12`、`tau=1..K-1`、`eta` 取 1/4 步长有理网格且只取 `thetabar>=1` 的 1999 个格点，0 反例 [VERIFIED-EXHAUSTIVE] |
| Step 4 硬族形状：hidden `O*` 加 window 内 oblivious `Psi(\|S\|)` [HAND-PROOF-UNREVIEWED] | The family 段（`F_O, G_O` 的显式定义）加 canonical transcript 段的 canonical oracle `S -> hatG(\|S\|)`，其中 `hatG(s)=1-a^s` | 部分对应。形状判断正确（hidden set 加只依赖 `\|S\|` 的 profile），但 **window 门限不同**：路线二取 `\|S∩O*\|<=tau-1`，路线一取 `\|S∩O\|<=tau`（`G_O` 的第一分支 `y<=tau` 上恰有 `G_O(S)=hatG(\|S\|)`）。见 D1 |
| Step 5 `(*)`：band 把 hidden 与 dummy 的真增益比锁在 `eta` 内 [HAND-PROOF-UNREVIEWED] | 无对应段落 | **不同路线**。路线一不经过 `(*)`：它把 `r=Delta G_O/(sqrt(theta) Delta F_O)` 在 count grid 的四类边上直接算出（四行表），再取极值 `A` 与 `1/(theta B)`，得 `eta_o^act=sqrt(theta)A`、`eta_u^act=sqrt(theta)B`、`eta^act=theta A B=Psi(theta)`。本轮复算 R6d-R6g 四行表差全为 0，R7 的 `h_{y+1}/h_y-1=((theta-1)K+y)/(theta K(K-y-1))` 差为 0 [VERIFIED-SYMBOLIC] |
| Step 6 每步吃掉剩余的 `beta=1/(eta(K-tau)+1)`，"`K-tau` 项乘 `eta` 加当前 1 项" [HAND-PROOF-UNREVIEWED] | 无对应段落 | **不同路线，且路线二此步不成立**。路线一的 `eta(K-tau)+1` 来自 `thetabar*K=Psi^{-1}(eta)*K`，即族的 error 闭式求逆，不是 per-step 计数。路线二的 "+1" 由它自己的 `(*)` 推不出，见 G7 |
| Step 7 `K` 步几何衰减给 `1-(1-beta)^K` [HAND-PROOF-UNREVIEWED] | The true objective and its optimum 段：`F_O(T)/F_O(O*)=1-a^{\|T\|}<=1-a^K=L_K(theta)`，只用 `T∩O=∅` | **不同路线**。路线一的值上界是族的闭式取值，不做 per-step 分析；路线二此步另有一处可举反例的等式错误，见 G8 |
| Step 8 union bound，bad event 取 level `tau`，得 `K^{2tau}/(tau! n^{tau-c})` 与充分条件 `n>=4K^{2tau}` [HAND-PROOF-UNREVIEWED] | Counting 段：bad event 取 level `tau+1`（`\{\|S∩O\|>tau\}`），`Pr[R⊆O]=prod_{i=0}^{tau}(K-i)/(n-i)<=(K/n)^{tau+1}`，`binom(K,tau+1)<=K^{tau+1}/(tau+1)!`，得 `K^{2tau+2}/((tau+1)! n^{tau+1})` | **同方法、不同 level**，由 D1 的 window 门限差直接带来。路线一在 `n>=4K^{c+2}` 下的估计我逐项复算：指数 `2tau+2-(c+2)(tau+1-c)=c(c+1-tau)<=0`（R9 差为 0），`4^{tau+1-c}>=16`，故第一项 `<=1/(16(tau+1)!)<=1/32` [VERIFIED-SYMBOLIC]。路线二的 `[FAILED]` 只针对它自己的 level-`tau` 计数 |
| Step 9 把输出 `T` 纳入 union（`Q -> Q+1`），得 `T` 落在 window 内 [HAND-PROOF-UNREVIEWED] | canonical transcript 段：另加 `Pr[T_0∩O≠∅]<=E\|T_0∩O\|=\|T_0\|K/n<=K^2/n`，要求的是 **`T_0∩O=∅`** 而不是 `T_0` 在 window 内 | **不同路线**。路线一的值上界需要 `y=0`，所以输出项必须单列且用期望计数；路线二的值上界只需要 `T` 在 window 内，所以它把输出并进同一条 union。两者都闭合了 `\|T\|<=K` 与 `=K` 的等价性（monotone） |
| Step 10 任意劈分由 rescaling 实现 [HAND-PROOF-UNREVIEWED] | A prescribed split 段：`tilde f=G_O -> beta G_O`，`beta=eta_o/(sqrt(theta)A)`，并注明 `hatG` 乘同一常数后仍只依赖 `\|S\|`，故 rescaling 不泄露 `O` 的身份；`beta=sqrt(B/A)` 给对称劈分 | 对应，但路线一更完整：它显式给出 `beta` 并补了 "rescaling 不携带 `O` 的信息" 这一条（路线二只说 argmax 不变）。劈分的量词域两条路线不同，见 D7 |
| Step 11 随机化走 Yao，`eps_n = K/n + K^{2tau}/(tau! n^{tau-c})` [部分 FAILED] | Randomized algorithms 段：固定 seed `r`，pointwise `f_O(T)/f_O(O*)<=1-a^K+\|T_0^{(r)}∩O\|/K+1[E_r^c]`，对 `O` 平均把中项压到 `K/n`、末项压到查询 union bound，再对 `r` 平均 | **不同路线**。路线一不需要把输出事件也排除，而是用 pointwise 不等式 `1-a^x(1-y/K)<=1-a^K+y/K`（`x<=K`、`a in (0,1)`；本轮复算 R10 恒等式差为 0，不等式由 `a^x>=a^K` 与 `a^x<=1` 两步得出）把输出与 `O` 的相交量线性吸收。因此 `eps_n` 的两项分别是 `E\|T_0∩O\|/K<=K/n` 与 level-`(tau+1)` 的查询 union bound，与 displayed 式逐字一致。路线二的两条 `[FAILED]` 是其 D1 门限选择的后果，见 G3、G4 |
| Step 12 `H->1-e^{-1/eta}` [VERIFIED-SYMBOLIC]；`K delta(theta)->tau-1/theta` 无法检验 | Calibration 段末：`delta(theta)=AB-1=(tau-1/theta)/(K-tau)`，故 `K delta(theta)->tau-1/theta`；`K/(eta(K-tau)+1)->1/eta` 故 `H->1-e^{-1/eta}` | 前半对应（本轮复算 R11 `limit` 给 `1-e^{-1/eta}`，差为 0 [VERIFIED-SYMBOLIC]）。后半路线二因输入包缺 `delta, theta, a_theta, Psi` 的定义而无法检验；本轮按路线一的定义复算 R2（`AB-1=(tau-1/theta)/(K-tau)`，差为 0）与 R12（`K delta -> tau-1/theta`，差为 0）[VERIFIED-SYMBOLIC] |
| 第 3 节数值走查（`K=3,eta=3/2,tau=1`：`beta=1/4`，残量 `1,3/4,9/16,27/64`，`H=37/64`；`K=2,eta=3/2`：`H=16/25`；`L_3(3/2)=386/729`，`L_2(1)=3/4`） | 路线一无数值走查 | 路线二独有。本轮独立复算逐位一致：`H(3,1,3/2)=37/64`、`H(2,1,3/2)=16/25`、`L_3(3/2)=386/729`、`L_2(1)=3/4`、`thetabar(3,1,3/2)=4/3` [VERIFIED-SYMBOLIC] |
| 第 4.6 节空洞性检验（deterministic、查询大小 `<=K`、`n>=4K^{c+2}`、`K>tau`、`eta>1`、tie breaking、"exactly eta"） | 台账 T10 的禁止声称清单；`sec:hardness` 定理后的 Three scope notes | 部分对应。路线二关于 `eta>1` 在 `tau>=2` 时空洞的观察在路线一里没有对应句；tie breaking 的观察同样没有。见 D8 |

### 路线一中路线二未覆盖的内容

| 路线一的步骤 | 路线二的状态 |
|---|---|
| 显式族 `F_O(S)=theta^{-1/2}[1-a^x(1-y/K)]`、`G_O` 的两分支与 `hatG(s)=1-a^s`，`a=a_theta=1-1/(theta K)`，`A=a^tau K/(K-tau)`，`B=a^{1-tau}`；两分支在 `y=tau` 相接（复算 R6a 差为 0） | **未覆盖**，正是路线二自报的 GAP-6（它称为本次推导最大的缺口）。本轮把该族在 `(n,K,tau,eta)=(6,3,1,3/2), (7,3,2,5/2), (7,4,2,2), (6,3,1,5/2), (8,4,1,3)` 上逐子集重建为真实集合函数：`F_O` normalized、monotone、submodular 全通过，`F_O(O)` 归一后为 1 [VERIFIED-EXHAUSTIVE] |
| 通过二阶差分 `Delta_x^2 barF, Delta_y Delta_x barF, Delta_y^2 barF` 全 `<=0` 与 `lem:app-count` 得 `F_O` 在任意有限 ground set 上单调 submodular | **未覆盖**。本轮复算 R8a/R8b/R8c 三条差全为 0 [VERIFIED-SYMBOLIC]，与上一行的穷举一致 |
| 四行 edge table 与 "每个 `x` 都约掉，故对一切 `n>K` 同表"，以及 `y=K` 的两类边不带 band 约束、`y=tau-1 -> tau` 与 `tau -> tau+1` 两条边分属第三、四行故 junction 无需另论 | **未覆盖** | 
| 极值取到与 `eta^act=theta A B=Psi(theta)=(theta K-1)/(K-tau)`，且两个因子都 `>=1`，故 "smallest admissible factors 的乘积恰为 `eta`" 的**下界方向**闭合 | 路线二自报 GAP-4 (ii) 未闭合。本轮复算：五组参数上 `max r = A`、`min r = 1/(theta B)` 全部成立且在实际边上取到，`eta_act` 与目标 `eta` 精确相等（`3/2, 5/2, 2, 5/2, 3`）[VERIFIED-EXHAUSTIVE]；符号侧 R1 `theta A B-(theta K-1)/(K-tau)` 差为 0 [VERIFIED-SYMBOLIC] |
| `Psi` 与旧的对称 band `Phi(theta)=theta max\{A,B\}^2` 的对照，`Psi<=Phi`（等号仅在 `A=B`），故 `H_{K,tau}(eta)=L_K(thetabar)<=L_K(hateta)`；`(K,tau,theta)=(4,1,4)` 处 `(eta_u,eta_o)=(2,5/2)`、error 5 而 `Phi(4)=25/4`，说明旧的 "error exactly eta" 读法不成立 | **未覆盖**（输入包不含 `Phi`）。`results/J2_core_oracles.py` 本轮复跑把这一反例逐字打印出来 |
| `tau=ceil(c)+1` 而不是 `c+1` 的理由：Counting 段需要 `tau` 是整数（`(tau+1)`-subset 计数） | 路线二把 `tau=ceil(c)+1` 当作给定，只用到推论 `tau-c>=1`，未指出整数性从哪一步进来 |
| 门槛 `n>=4K^{c+2}` 的具体估计链：第一项 `<=K^{c(c+1-tau)}/((tau+1)! 4^{tau+1-c})<=1/(16(tau+1)!)<=1/32`，第二项 `K^2/n<=1/(4K^c)<=1/4`，和 `<=9/32<1` | 路线二自报 GAP-1，在自己的 level-`tau` 计数下把它标 `[FAILED]`。本轮对 `c=0..3`、`K<=29` 在 `n=4K^{c+2}` 上逐点精确复算路线一的两项之和，最大值 `9/32=0.28125`，全部 `<1` [VERIFIED-EXHAUSTIVE] |
| canonical transcript 归纳（若前 `i-1` 个回答与 canonical 一致则 determinism 使第 `i` 个查询等于 `S_i`，`\|S_i∩O\|<=tau` 把 `S_i` 放进第一分支，故 `G_O(S_i)=hatG(\|S_i\|)`），以及 "两个论证的顺序不可交换" 的注记 | 路线二 Step 8 有 "回答序列与 `O*` 无关" 的同向观察，但没有写归纳，也没有写顺序注记 |
| 随机化的 pointwise 不等式与两次平均（`min_O<=E_O`，只用 minimax 的平均方向，不引用 minimax 定理） | 路线二走 Yao 的一般说法，未给 pointwise 不等式，也因此推不出 `K/n` |
| 台账 T10 的 must-not-claim 清单（禁用旧 `Phi` 校准说 "error exactly eta"、禁把查询大小限制等同于多项式时间、禁称随机版 `eps_n` 在 `K->oo` 自动消失、禁称本族可用于任意大小查询）与 P0/P1 的 `[VERIFIED-LP]` 塌缩结果 | **未覆盖**（盲证，输入包不含台账）。路线二未违反其中任何一条 |

---

## 2. 判定

### (1) 结论与量词

**结论一致。** 两条路线给出同一个值公式与同一个骨架：对所有实数 `c>=0`（`tau=ceil(c)+1`）、所有整数 `K>tau` 与 `n>=4K^{c+2}`、所有实数 `eta>1` 且 `eta>=(K-1)/(K-tau)`，对每个至多 `n^c` 次、每次集合大小至多 `K` 的确定性算法，存在 monotone submodular `f` 与 predictor `tilde f`（最小可行 error factors 之积恰为 `eta`）使输出 `T`（`\|T\|<=K`）满足

```
f(T)/f(O*) <= H_{K,tau}(eta) = 1-(1-1/(eta(K-tau)+1))^K = L_K(thetabar),  thetabar=(eta(K-tau)+1)/K
```

加三条从句：任意劈分由 rescaling 实现；随机版在期望意义下加 `eps_n`；`K->oo` 时 `H->1-e^{-1/eta}` 且 `K delta(theta)->tau-1/theta`。

**量词不完全重合**，差三处：

- **劈分从句的 `(eta_u,eta_o)` 定义域**。路线一按 `def:eta` verbatim（`eta_u,eta_o>=1`）陈述 "any prescribed split"，其 rescaling `beta=eta_o/(sqrt(theta)A)` 对任意正 `eta_o` 都可执行；路线二按输入包 `definition1.md` 的 convention B（`eta_u,eta_o>0`）读同一句，并指出 verbatim 文本下只有 `eta_u in [1,eta]` 可实现。两读法下路线一的构造都成立，但 "any prescribed split" 这个全称量词的范围不同。
- **设计参数 `theta>=1` 的全称量词**。路线一先对所有 `theta>=1` 造族、算 `Psi(theta)`，再取 `theta=thetabar` 校准；`K delta(theta)->tau-1/theta` 这条从句就是在这个 `theta` 上取的。路线二的输入包不含 `theta, delta, a_theta, Psi` 的定义，它没有这一层量词，只有反解出来的单个 `thetabar`，因此该从句它无法检验。
- **`K` 与 `n` 的关系**。路线一的 `app:hardness` 第一句是 `1<=tau<K<n`（严格）；路线二写 `tau<K<=n`。因 `n>=4K^{c+2}>=4K^2>K`，无实质影响。

路线二额外写明而路线一未写明的限定词：算法是 **adaptive** 的（路线一在 canonical transcript 段隐含使用），以及把 "exactly `eta`" 读作 "inf 取到"（与路线一的 "smallest admissible error factors" 同义，且路线一在极值取到那句里闭合了它）。这两条不改变量词的实际范围。

### (2) 路线二是否有 added assumption、gap 或 error

**有。** 路线二自报六条 gap（GAP-1 至 GAP-6），本轮复算另找到两处它未认定为错误的步骤（G7、G8）。其中：

- 三条 gap（GAP-1 门槛、GAP-2 `eps_n` 第二项、GAP-3 `eps_n` 第一项）**不是定理的问题，是路线二 window 门限选择的后果**。路线二把 window 取成 `\|S∩O*\|<=tau-1`，于是 bad event 落在 level `tau`，union bound 的指数比路线一低 1，门槛与 `eps_n` 都跟着变弱。路线一把 window 取成 `\|S∩O\|<=tau`，bad event 落在 level `tau+1`，并把输出条件单列成 `T_0∩O=∅`，两项都对上了 displayed 的 `eps_n`。
- 路线二在 GAP-2 里提出的分叉 "(a) 若 window 是 `\|S∩O*\|<=tau`，则计数变成 `eta(K-tau-1)+1`，与 `H` 冲突" **被路线一的族证伪**：路线一的 window 就是 `\|S∩O\|<=tau`，而 `eta(K-tau)+1` 来自 `Psi^{-1}(eta)K`，与 per-step 计数无关。本轮在五组参数上把该族重建为真实集合函数，window 门限 `y<=tau`、bad event level `tau+1`、`eta_act` 精确等于 `eta`、值上界精确等于 `H`，三者同时成立 [VERIFIED-EXHAUSTIVE]。
- GAP-4 的下界方向与 GAP-6 的显式族**在路线一里是闭合的**，且本轮独立复算通过。
- GAP-5 是输入包缺定义，不是数学问题。
- **G7（新发现）**：Step 6 的 "`K-tau` 项乘 `eta` 加当前这一步的 1 项" 从它自己的 `(*)` 推不出。`(*)` 只给 `d_o(S)<=eta g` 对每个 `o in O*\S`，而 `\|O*\S\|=K-tau+1`，所以只能得 `R<=(K-tau+1) eta g`，即 `beta=1/(eta(K-tau+1))`，比 statement 的 `beta` 小（给出更强的 hardness 值）。要拿到 "+1" 必须假设某个 `o in O*\S` 的真增益不超过算法这一步吃到的 `g`，而算法是按预测增益选的（window 内预测增益全相等），这一点没有依据。路线二在 GAP-6 的候选 1 里观察到了同一现象（该候选给 `beta=1/(eta(K-tau+1))`），但没有把它回溯认定为 Step 6 的漏洞。 `[FAILED]`：不等式 `R(S)<=(K-tau)eta g+g`，参数为任意 `K>tau>=1`、`eta>1`，仅由 `(*)` 与 submodularity 推不出。
- **G8（新发现）**：Step 7 写 `R_{t+1}=R_t-g_t`，其中 `R(S)=f(O*∪S)-f(S)`。该等式一般不成立：加入 `e∉O*` 时 `f(O*∪S^{t+1})-f(O*∪S^t)=d_e(O*∪S^t)` 可为正。精确反例（coverage，`Fraction` 无关，整数）：`N=\{o1,o2,e\}`，`cov(o1)=\{1\}, cov(o2)=\{2\}, cov(e)=\{3\}`，`O*=\{o1,o2\}`，`K=2`，`S^1=\{e\}`：`R_0=2`、`g_0=1`、`R_1=2`，而 `R_0-g_0=1`。且方向与推导需要的相反（`R_{t+1}>=R_t-g_t`）。**可修复且不改结论**：改用 `r_t=f(O*)-f(S^t)`，则 `r_{t+1}=r_t-g_t` 精确成立，`(dagger)` 给的 `R(S)>=f(O*)-f(S)=r_t` 仍能串上 `g_t>=beta R(S)>=beta r_t`，几何衰减与终值不变。 `[FAILED]`：等式 `R_{t+1}=R_t-g_t`，参数如上。

路线二没有引入路线一之外的 added assumption（它用的 monotone、submodular、`f(∅)=0`、band、`\|S\|<=K`、deterministic 都在陈述里），唯一的约定依赖是 convention B（见上一节）。

### (3) 路线一是否有被路线二反驳的步骤

**没有。** 路线二的两条 `[FAILED]` 都明确限定为 "我的计数给不出"，不是对路线一的反驳；本轮把路线一的对应两步逐项精确复算，全部成立：

- Counting 段的 `Pr[R⊆O]=prod_{i=0}^{tau}(K-i)/(n-i)<=(K/n)^{tau+1}`：`(K-i)n<=K(n-i)` 在 `n>=K` 下成立，逐项验证通过。
- 门槛估计的指数 `2tau+2-(c+2)(tau+1-c)=c(c+1-tau)`：符号复算差为 0；`tau>=c+1` 使其 `<=0`，`tau+1-c>=2` 使 `4^{tau+1-c}>=16`。两项之和在 `c=0..3`、`K<=29` 的最坏点为 `9/32`。
- 随机化的 pointwise 不等式与 `E\|T_0∩O\|/K<=K/n`：恒等式 R10 差为 0，两步放缩（`a^x>=a^K` 与 `a^x<=1`）逐条成立。

本轮也没有在路线一里找到可举反例的步骤。路线一自己标注的 `[HAND-PROOF-UNREVIEWED]`（counting bound、canonical transcript 归纳、两次平均）保持不变：任何有限计算都不遍历 adaptive 算法，本轮的复算只覆盖了这三步里的**不等式链**，不覆盖 "对任意 adaptive 算法" 这一层量词。

---

## 3. divergences（逐条）

- **D1（核心）window 门限**。路线二：`W_tau=\{\|S\|<=K, \|S∩O*\|<=tau-1\}`；路线一：`G_O` 的 oblivious 分支是 `y<=tau`，bad event 是 `\|S∩O\|>tau`。D2、D3 全部由此派生。
- **D2 门槛条件**。路线二自己的充分条件是 `n>=4K^{2tau}`（`c=0,tau=1` 时与 statement 的 `4K^2` 相同，概率恰为 `1/4`）；路线一在 `n>=4K^{c+2}` 下用 level-`(tau+1)` 计数得总失败概率 `<=9/32`。两者不矛盾，路线一的条件严格更弱。
- **D3 `eps_n` 第二项**。路线二得 `K^{2tau}/(tau! n^{tau-c})` 并判定 displayed 项是 off-by-one；路线一得 displayed 的 `K^{2tau+2}/((tau+1)! n^{tau+1-c})`，来源是 level-`(tau+1)` 的查询 union bound。displayed 式正确，路线二的判定只对它自己的 window 成立。
- **D4 `eps_n` 第一项 `K/n`**。路线二标 `[CONJECTURE]` 猜测为 `Pr[e in O*]`；路线一给出确切来源：`E_O\|T_0^{(r)}∩O\|/K<=\|T_0\|K/(Kn)<=K/n`，配 pointwise 不等式 `1-a^x(1-y/K)<=1-a^K+y/K`。
- **D5 `eta(K-tau)+1` 的来源**。路线二：per-step 计数（`K-tau` 个被 band 放大 `eta` 倍的 hidden 元素加当前 1 项），heuristic；路线一：`thetabar K=Psi^{-1}(eta)K`，即族的 error 闭式 `Psi(theta)=(theta K-1)/(K-tau)` 求逆。两者数值相同，来路无关。
- **D6 值上界的条件**。路线二：`T` 落在 window 内；路线一：`T∩O=∅`（`y=0`），由此 `F_O(T)/F_O(O*)=1-a^{\|T\|}<=1-a^K`。路线一的条件更强，所以它必须单列输出项 `K^2/n`。
- **D7 劈分的量词域**。路线二按 convention B（`eta_u,eta_o>0`）；路线一按 `def:eta` verbatim（`eta_u,eta_o>=1`）并给出 `beta=eta_o/(sqrt(theta)A)`。路线一的 rescaling 在两种 convention 下都可执行，但 "any prescribed split" 的范围不同。建议在定理处点明用的是哪一种，这与路线二 GAP-4 的建议一致。
- **D8 空洞性检验的两条观察只在路线二里**。(a) `eta>1` 在 `tau>=2` 时被 `eta>=(K-1)/(K-tau)>1` 吞掉（`K>tau>=2` 时 `K-1>K-tau`），建议写成 `eta>=max\{1,(K-1)/(K-tau)\}`；(b) adversarial tie breaking 在本定理里两条路线都没有用到（算法是任意确定性算法而非 greedy），建议说明它在本定理是否有作用点。这两条是 statement 卫生问题，不影响真值。
- **D9 `K<n` 与 `K<=n`**。路线一的 `app:hardness` 写 `1<=tau<K<n`，路线二写 `tau<K<=n`。因 `n>=4K^{c+2}>K`，无实质差别。
- **D10 数值走查**。路线二有（`K=3` 与 `K=2` 两格，含 `eps_n` 在 `n=36`、`n=16` 的两版对照），路线一无。路线二的数字本轮逐位复算一致。
- **D11 `Psi` 与 `Phi`**。路线一区分了族的真实 error `Psi(theta)=theta AB` 与旧的对称 band `Phi(theta)=theta max\{A,B\}^2`，并用 `(K,tau,theta)=(4,1,4)` 说明旧的 "error exactly eta" 读法不成立；路线二的输入包不含 `Phi`，未覆盖这一层。

---

## 4. route-two gaps（逐条，含状态标签）

| 编号 | 内容 | 路线二自报状态 | 本轮判定 |
|---|---|---|---|
| G1 | GAP-6 显式硬族 `f` 未构造（路线二称其为本次最大缺口） | `[FAILED]` | 路线一给出 `F_O, G_O`；本轮在 5 组参数上逐子集重建，monotone、submodular、`eta_act=eta`、值 `=H` 全通过 `[VERIFIED-EXHAUSTIVE]`。缺口在路线一处闭合 |
| G2 | GAP-1 statement 的 `n>=4K^{c+2}` 不足以让路线二的 union bound `<1`（`c>=1` 且 `K` 大时；`c=1` 需 `K<8`，`c=2` 需 `K<=4`） | `[FAILED]` | 算术正确（本轮复算 `P_tau(4K^{c+2})=K^c/(4(c+1)!)`，差为 0），但结论只对路线二自己的 level-`tau` 计数成立。路线一的 level-`(tau+1)` 计数在同一门槛下给 `<=9/32` `[VERIFIED-EXHAUSTIVE]` |
| G3 | GAP-2 displayed `eps_n` 第二项被判为 level 错位 / off-by-one | `[FAILED]` | displayed 项正确，来源是路线一的 level-`(tau+1)` 查询 union bound。路线二为排除该判定给出的分叉 (a) 被路线一的族证伪（见第 2(2) 节） |
| G4 | GAP-3 `eps_n` 第一项 `K/n` 来源推不出 | `[CONJECTURE]` | 路线一给出确切来源（随机化段的 pointwise 不等式加对 `O` 的平均）。缺口在路线一处闭合 |
| G5 | GAP-4 "最小可行 error factors 之积恰为 `eta`" 的下界方向未闭合 | `[HAND-PROOF-UNREVIEWED]` | 路线一闭合：`max r=A`、`min r=1/(theta B)` 都在实际边上取到（`n>K` 且 `1<=tau<K`），`eta^act=theta AB=Psi(theta)`。本轮 5 组参数复算全部精确相等 `[VERIFIED-EXHAUSTIVE]` |
| G6 | GAP-5 `delta(theta), theta, a_theta, Psi` 定义缺失，`K delta(theta)->tau-1/theta` 无法检验 | 无法检验 | 输入包问题，不是数学问题。按路线一的定义本轮复算 `delta=AB-1=(tau-1/theta)/(K-tau)` 与 `K delta->tau-1/theta`，差均为 0 `[VERIFIED-SYMBOLIC]`。建议把这四个符号补进 `results/V11/inputs/notation.md` |
| G7 | Step 6 的 "+1"（`R<=(K-tau)eta g+g`）从路线二自己的 `(*)` 推不出；`(*)` 只给 `R<=(K-tau+1)eta g` | 未自报（路线二在 GAP-6 候选 1 里观察到同一现象但未回溯） | 本轮认定为路线二的推导漏洞 `[FAILED]`（不等式与参数见第 2(2) 节 G7）。不影响结论，因为 `eta(K-tau)+1` 在路线一有独立来源 |
| G8 | Step 7 的 `R_{t+1}=R_t-g_t`（`R(S)=f(O*∪S)-f(S)`）一般不成立，且方向与所需相反 | 未自报 | 本轮给出精确反例（3 元素 coverage，`R_0=2, g_0=1, R_1=2`）`[FAILED]`。改用 `r_t=f(O*)-f(S^t)` 即可修复，几何衰减与终值不变 |

另记两条 statement 卫生建议（路线二提出，本轮确认，不计为 gap）：`eta>1` 在 `tau>=2` 时空洞；adversarial tie breaking 在本定理里未被任何一条路线用到。

---

## 5. 结论

**verdict：B-GAP（路线二不完整）。**

理由三句：两条路线给出同一个值公式、同一个量词骨架，值公式一侧路线二有 oracle 且与路线一逐字一致；路线二的三块内容（显式硬族、门槛 `n>=4K^{c+2}`、随机版 `eps_n`）未闭合，其中两块被它自己标 `[FAILED]`，而这三块在路线一里都闭合并通过本轮独立复算；路线二没有反驳路线一的任何一步，本轮也没有在路线一里找到可举反例的步骤，所以不是 B-FAIL。

`consistent=false`（结论一致，但路线二含两处未更正的错误 G7、G8）；`quantifier_match=false`（劈分从句的 `(eta_u,eta_o)` 定义域、设计参数 `theta` 的全称量词、`K<n` 与 `K<=n` 三处不重合）。

路线一的整体状态保持台账 T10 的分解不变：边表、极值因子、`Psi`、二阶差分、校准恒等式与两条极限 `[VERIFIED-SYMBOLIC]` + `[VERIFIED-LP]`（本轮复跑 `results/J2_core_oracles.py` `all_passed: true`、`results/H3_j2_recheck.py` `ALL PASS`，另加本文件第 1 节的 21 条独立恒等式与 5 组集合函数穷举）；counting bound、canonical transcript 归纳与两次平均仍是 `[HAND-PROOF-UNREVIEWED]`，本轮只复算了其中的不等式链，不覆盖 "对任意 adaptive 算法" 那一层量词，该标签不升级。
