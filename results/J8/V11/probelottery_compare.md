# ROUTE-COMPARISON：J8 ProbeLottery（Proposition，$K=2$，$\eta=3/2$）

TASKS11 Q9，criterion B。本文件只做比对，不修改任何既有文件，未运行 git。

- **路线一（repo proof）**：**不存在**。仓库里与 J8 相关的全部内容是
  `results/J8/J8_claude_spotcheck.py`（算法的实现 + 紧实例 + 400 个随机 coverage 实例）、
  `results/J8/J8_claude_spotcheck_run.log`、`HANDOFF_2026-09-18.md` §4 的一行状态
  （"Claude 手推通过、GPT 脚本复现、实现在紧实例得 $3/5+1/2048$，状态 [HAND-PROOF-UNREVIEWED]"）
  与 `results/V11/inputs/statement_probelottery.md`（陈述 + 算法五步）。
  陈述文件自己写明 "the proof file J8_probe_lottery.md with inequalities (3),(8)-(12) was not delivered"。
  **因此路线一是 GAP：没有任何推导步骤可供对应。** 本文件的 step 对应表右列只能填
  "路线一无对应步骤"，比对退化为 "路线二 vs 陈述 + spot-check 数值"。
- **路线二（blind derivation）**：`results/V11/route2/probelottery.md`，
  oracle 脚本 `results/V11/route2/J8_route2_check.py`、`J8_route2_constants.py`、`J8_route2_random.py`
  （本轮三个脚本全部复跑通过，输出与文件所述一致）。
- **本轮独立复算脚本**（全部 `sympy` / `fractions.Fraction`，float 只出现在打印里）：
  - `results/V11/compare/judge_probelottery_checks.py`：26 条符号/有理常数检查，0 FAILED。
  - `results/V11/compare/judge_probelottery_instances.py`：两个紧实例的**独立**重建
    （自写的 ProbeLottery 实现 + 全子集 monotone/submodular 穷举 + 全 $(S,e)$ band 穷举）。

---

## 1. Step 对应表

右列 "路线一位置" 只能引用 statement 或 spot-check 脚本的行为；凡是需要推导的地方，路线一都没有。

| 路线二的步骤 | 路线一的对应位置 | 判定 |
|---|---|---|
| §1 命题重述 Q1-Q9（九条量词）| `statement_probelottery.md` 的 Proposition 段 + `assumptions.md` | 对应。数值与访问模型逐字一致（$K=2$、$\eta=3/2$、$\le 9n$ query、$\lvert S\rvert\le5$、$\lvert T\rvert=2$、期望只对算法 randomness）。量词差见 §2(1) |
| §1 空洞性检验（四个限定词逐个去掉）| 路线一无对应内容 | 路线二独有。结论正确：$\lvert S\rvert\le5$ 是唯一 payload；`9n` 可换成任意 $\Theta(n)$ |
| §2 归一化 $\mathrm{OPT}=1$、$O^\ast$ 补元素 | `assumptions.md` 的 $f(O^\ast)=0$ 平凡约定 | 对应，是 monotonicity 的直接推论，不是新假设 |
| L0 scale invariance（两个 pool 判据 1-齐次，故可归一到 $(1,3/2)$）| `definition1.md` convention B 的 scaling 段；statement 括号里的 "after rescaling" | 对应。本轮复核：`J8_claude_spotcheck.py` 的 `tight_instance` 直接取 $\eta_u=1$（注释 "eta_u = 1, so G = H"），与该归一化一致 [VERIFIED-EXHAUSTIVE] |
| L1 集合级 sandwich $f\le\tilde f\le\frac32f$ | 路线一无对应步骤 | 路线二独有，telescoping 一行，正确 |
| **L2 pair-consistency**（$\tilde f(\{u\})-\tilde f(\{e\})\le\frac32d_u(\{e\})-d_e(\{u\})$）| 路线一无对应步骤 | 路线二独有，且是全篇把 $5/9$ 抬到 $3/5$ 的唯一新成分。本轮独立复核：两侧 band 相夹，代数改写 $f(\{u,e\})\ge2(\tilde f(\{u\})-\tilde f(\{e\}))+3f(\{e\})-2f(\{u\})$ 无误 |
| L3 / L3' 第二步 argmax 价值 $\beta\ge\frac13f(\{b\})+\frac23f(\{b,e\})$ | 路线一无对应步骤 | 路线二独有，正确（$\tilde d_c\ge\tilde d_e$ 与 $d\ge\frac23\tilde d$ 两步） |
| L4 第一步 argmax；L5 submodular 分裂 | 路线一无对应步骤 | 路线二独有，正确 |
| **命题 4.1 基线 $\beta\ge\frac35$**（分支 A $\frac{1+2x}3$、分支 B $1-x$，$\min\max$ 在 $x=\frac25$）| statement 只把 $\rho_2(3/2)=3/5$ 当既知事实引用 | **不同路线**：路线一不证，路线二自足证出下界。本轮复算 $x^\ast=2/5$、值 $3/5$ [VERIFIED-SYMBOLIC] |
| 命题 4.2 $n=4$ 有理紧实例（上界方向）| spot-check 的 `tight_instance`（J6 double-residual 族，$n=6,8,12,20$）| **同结论、不同实例**。两个实例都精确给出 $f(P_0)=\frac35\mathrm{OPT}$。本轮把路线二的 $n=4$ 实例独立重建（size 3、4 的 $\tilde f$ 用极大补全），全 16 子集 monotone+submodular、全 $(S,e)$ band 通过 [VERIFIED-EXHAUSTIVE] |
| §5 刚性 R1-R8 | 路线一无对应步骤 | 路线二独有。R1-R5、R7、R8 本轮逐条复算无误 [VERIFIED-SYMBOLIC]；**R6 的常数方向错**，见 §3 D4 |
| §6 引理 P（$\varepsilon\le\mathrm{EPS}/11\Rightarrow o_1,o_2\in C$）与推论 P' | 路线一无对应步骤 | 路线二独有。阈值算术复算通过：$5\cdot\frac1{110000}=4.5455\times10^{-5}\le\mathrm{EPS}\cdot M=4.99985\times10^{-5}$ [VERIFIED-SYMBOLIC] |
| §7 **引理 D**（(D1) $f(\{b,v\})\ge\frac35-\frac23\mathrm{EPS}M$，(D2) $f(\{v,z_v\})\ge\frac35-\frac43\mathrm{EPS}M$）| 路线一无对应步骤 | 路线二独有，是它最有用的一条。本轮在 spot-check 的紧实例上得到**独立确认且取到等号**：$n=6$ 的 8 个 secondary set 里有 6 个恰等于 $\frac35$（见 §3 D3 的表） [VERIFIED-EXHAUSTIVE] |
| §8 彩票算术 (8.1)-(8.3)（$\frac{127}{128}+\frac8{1024}=1$；$\mathbb E/\mathrm{OPT}=\beta+\frac1{1024}\sum(\gamma_j-\beta)$）| statement 第 5 步的输出分布 | 对应，且 (8.1) 被 spot-check 的数值**精确印证**：$n=6$ 实例上 $\sum_j(\gamma_j-\beta)=\frac12$，代入 (8.1) 得 $\frac35+\frac1{2048}$，与交付 log 逐位一致 [VERIFIED-EXHAUSTIVE] |
| §9 情形 0（$\varepsilon\ge\varepsilon^\dagger=\frac{13}{3175000}$）| 路线一无对应步骤 | 路线二独有，复算通过 [VERIFIED-SYMBOLIC] |
| §9 情形 I（某个 $o_i\notin C$，此格为空，强迫 $\varepsilon>\frac3{300010}$）| 路线一无对应步骤 | 路线二独有，复算通过（余量 $2.442$ 倍）[VERIFIED-SYMBOLIC] |
| §9 情形 II-a（某轮取到 $o_i$，surplus $\ge\frac7{30}-\frac{14}9\varepsilon$，净值 $/1024\ge2.2646\times10^{-4}$）| spot-check 的紧实例正落在这一格（$B=[0,1,4,2,3]$，第 2 轮取到 $o_1$）| 对应。本轮复算净值 $2.264632\times10^{-4}\ge2.5\times10^{-6}$ [VERIFIED-SYMBOLIC] |
| §9 情形 II-b（$o_1,o_2\in C$ 但四轮全被挡）`[FAILED]` | 路线一无对应步骤 | **路线二的主缺口**，见 §4 G1 |
| §10 数值 walk-through（$n=4$ 紧实例、$\frac59$ 陷阱、difference-constraint 判定器）| spot-check 脚本的 `tight_instance` 与 400 随机实例 | 部分对应。$\frac59$ 陷阱的两条夹逼本轮复核无误（$\tilde f(\{b,o_1\})$ 同时 $\ge\frac56$ 与 $\le\frac34$）。**对 $\frac1{2048}$ 来源的解释被实测证伪**，见 §3 D3 |
| §10 反例搜索（$n=7$ 四克隆构造被 Bellman-Ford 判不可行，triple 夹逼 $\frac{11}{10}>\frac{21}{20}$）| 路线一无对应步骤 | 路线二独有。两个数值本轮复核无误 [VERIFIED-SYMBOLIC]；不可行性本身由路线二自己的脚本给出，本轮复跑得同一结论 |
| §10 随机搜索 400 例（min $\mathbb E/\mathrm{OPT}=\frac{1537}{2048}$）| spot-check 的 400 个随机 coverage 实例（worst ratio $=\frac45$）| **同方法、不同家族**，见 §3 D8 |
| §11 G1-G4 自报缺口 | 路线一无对应步骤 | 路线二独有。G3（$9n$ 核算）本轮可以收紧到闭合，见 §3 D7 |

### 路线一中路线二未覆盖的内容

| 路线一的内容 | 路线二的状态 |
|---|---|
| statement 末句的 corollary："这说明 linear-budget optimality theorem 的 $\lvert S\rvert\le K$ 限制对预算 $\frac92nK$ 的随机算法是必要的" | **未覆盖**。盲证输入包不含 `thm:linear-exact`，路线二只在空洞性检验里指出 $\lvert S\rvert\le5>K=2$ 是 payload，没有写出这条推论。这是路线一独有的、比对无法闭合的一条 |
| spot-check 的紧实例家族（J6 double-residual，$j=1$，$k_1=4$、$q=\frac34$、$\delta=\frac{Q}{K\eta}$ 的 count-grid 闭式）| **未覆盖**（盲证看不到 J6）。本轮把该族在 $n=6,8$ 上逐子集重建为真实集合函数：normalized、monotone、submodular 全通过，全 $(S,e)$ band 通过 [VERIFIED-EXHAUSTIVE] |
| spot-check 在 $n=6,8,12,20$ 四个规模上 assert `queries <= 9n` 与 `maxsize <= 5`，并实际取到 `maxsize = 5` | 部分覆盖。路线二自己的实例只到 `maxsize = 3`，没有触及 $\lvert S\rvert\le5$ 的实际边界 |
| HANDOFF §4 的 "GPT 脚本复现" 这一条外部证据 | **不可覆盖**（文件未交付） |
| 待补的不等式 (3),(8)-(12) | **不存在**，两条路线都没有 |

---

## 2. 判定

### (1) 结论与量词

**结论不一致：路线二没有达到路线一陈述的结论。**
路线一（statement）断言对**所有**合法实例 $\mathbb E[f(T)]\ge(\frac35+\frac1{400000})\mathrm{OPT}$。
路线二在情形 0、I、II-a 下给出同一结论，但在情形 II-b 下只得到
$\mathbb E[f(T)]\ge(\frac35-\frac1{640000})\mathrm{OPT}$，比目标低 $4.0625\times10^{-6}$
（本轮复算 $\frac1{400000}+\frac1{640000}=4.0625\times10^{-6}$ [VERIFIED-SYMBOLIC]）。
因此路线二交付的是**弱化结论 + 一个未闭合的格子**，不是命题本身。

**量词不完全重合**，差五处：

- **路线二写明、路线一未写明**：(a) $n\ge2$（算法第 2 步要在 $e\ne b$ 上取 argmax；路线一只由
  `assumptions.md` 的 $1\le K\le n$ 与 $K=2$ 间接给出）；(b) $\mathrm{OPT}=0$ 时按平凡约定成立；
  (c) 实例可 adversarial 且可依赖算法描述，但不可依赖抽签结果；(d) worst-case 陈述允许 adversary
  选择 tie-break 序（statement 只说 "fixed tie-break order, argmax returns the first maximiser"，
  是较弱的读法；路线二的读法与 `assumptions.md` 的 "adversarial tie-breaking in all worst-case
  statements" 一致，属于**加强**，不是放松）。
- **路线一写明、路线二未写明**：statement 末句的 corollary（$\lvert S\rvert\le K$ 对预算
  $\frac92nK$ 的随机算法必要），以及 $\frac92nK$ 这个预算记法（$K=2$ 时即 $9n$，数值一致，
  但路线二没有把它写成 $\frac92nK$，因此无法检验对一般 $K$ 的读法）。

两边都写明的量词（$K=2$、$\eta=3/2$、任意 split 且 $\eta_u\eta_o=3/2$、band 对所有 $S$ 与所有
$e\notin S$、$f$ monotone submodular 且 $f(\emptyset)=0$、$\tilde f(\emptyset)=0$ 且无结构假设、
$\le9n$ query、每次 $\lvert S\rvert\le5$、$\lvert T\rvert=2$、期望只对算法自身 randomness）逐条一致。

### (2) 路线二是否有 added assumption、gap 或 error

**没有 added assumption；有一个主缺口、一处算术错误、三处可补的小疏漏。**

- **added assumption：无。** §2 的 "最优值由单点达到时补一个元素" 是 monotonicity 的推论。
  L0 的归一化到 $(\eta_u,\eta_o)=(1,3/2)$ 由 convention B 的 scaling 保证，且算法全部判定
  1-齐次，本轮逐条复核无误。
- **主缺口 G1（情形 II-b）** `[FAILED]`：见 §4。
- **算术错误 R6** `[FAILED]`：$\Delta_i:=M-\tilde f(\{o_i\})$ 的上界。路线二的 §5 表格与
  `J8_route2_constants.py` 第 33 行都给 $\frac52\varepsilon$，但 $\Delta_i\le\frac12h_i-\frac32w_i+x$
  需要 $h_i$ 的**上**界，脚本代入的是 $h_{\min}=\frac7{10}-3\varepsilon$（下界）。
  代入正确的 $h_i\le h^\ast\le\frac7{10}+2\varepsilon$ 得 $\Delta_i\le5\varepsilon$，
  常数项仍恰为 $0$。本轮 `judge_probelottery_checks.py` 的 R6 与 R6b 两条同时复现了
  正确值 $5\varepsilon$ 与路线二的 $\frac52\varepsilon$ [VERIFIED-SYMBOLIC]。
  **下游无影响**：引理 P 的证明本来就写 "由 R6、R8 只需 $5\varepsilon\le\mathrm{EPS}\cdot M$"，
  情形 I 也取两者中较弱的 $5\varepsilon$，两处都已经用的是 $5$ 而不是 $\frac52$。
  修正后阈值链条不变（$\frac3{300010}$、$\frac1{110000}$ 都不变）。
- **小疏漏 1**：引理 D 的 (D2) "下路" 用 (L2) 取 $u=v$、$e=o^\ast$，隐含要求 $o^\ast\ne v$。
  $v\in O^\ast$ 的退化情形文件未写。可补：此时 "上路" 单独给
  $f(\{v,z_v\})\ge\frac13w^\ast+\frac23\ge\frac56>\frac35$，结论不变。
- **小疏漏 2**：§5 的刚性与 §7 的 (D1) 主干都设 $b\notin O^\ast$；$b\in O^\ast$ 由情形 0 吸收
  （$\beta\ge\frac23$，$\varepsilon\ge\frac1{15}\gg\varepsilon^\dagger$）。文件在情形 0 的括注里
  提了一句，但没有把它写成显式的第一层 case split。不影响正确性。
- **小疏漏 3**：情形 II-b 还有一条结构性必要条件路线二没有写出：$r=\min\{4,\lvert C\rvert\}$，
  所以 "$o_1,o_2\in C$ 且四轮都没取到它们" 强迫 $\lvert C\rvert\ge6$（四个挡路者加两个 $o_i$）。
  这与路线二自己构造的 $n=7$ 反例（四克隆 + $b$ + $o_1,o_2$）的规模一致，但文件没有把它
  当作缺口的收紧条件记下来。

**其余全部复算通过**：R1-R5、R7、R8、彩票恒等式、$\varepsilon^\dagger=\frac{13}{3175000}$、
情形 I 的 $\frac3{300010}$、情形 II-a 的 $\frac7{30}-\frac{14}9\varepsilon$ 与净值
$2.264632\times10^{-4}$、II-b 弱界 $\frac35-\frac1{640000}$、挡路链
$\frac35\to\frac{11}{15}\to\frac{37}{45}\to\frac{119}{135}$、triple 夹逼 $\frac{11}{10}>\frac{21}{20}$，
共 26 条，0 FAILED。

### (3) 路线二是否与路线一的某一步矛盾

**没有矛盾，因为路线一没有推导步骤可矛盾。** 与路线一**数值**的比对：

- 基线 $\rho_2(3/2)=\frac35$：路线二自足证出下界并给 $n=4$ 上界实例；spot-check 的紧实例
  独立给 $f(P_0)=\frac35\mathrm{OPT}$。一致。
- 彩票值：路线二的公式 (8.1) 代入 spot-check 实例的 $\sum_j(\gamma_j-\beta)=\frac12$
  精确复现 $\frac35+\frac1{2048}$。一致。
- **路线二对 $\frac1{2048}$ 的解释被实测证伪**（它自己标了 `[CONJECTURE]`），见 §3 D3。
  这是解释层面的错，不是不等式层面的矛盾。

---

## 3. Divergences（逐条）

- **D1（结构性，最重要）**：路线一**不存在**。仓库没有 `results/J8/probe_lottery.md`，
  不等式 (3),(8)-(12) 未交付，HANDOFF §4 自己把 J8 标为 `[HAND-PROOF-UNREVIEWED]` 且
  "Q5 是否已跑未确认"。criterion B 的对偶证书无法组装。
- **D2（紧实例不同）**：路线一的紧实例是 J6 double-residual 族（$n=6,8,12,20$，
  $\lvert C\rvert=5,7,11,19$，$r=4$，max query size $=5$），取到 $\frac35+\frac1{2048}$；
  路线二自造 $n=4$ coverage 实例（$\lvert C\rvert=2$，$r=2$，max query size $=3$），
  取到 $\frac35+\frac1{1024}$。两者都合法（本轮独立穷举复核），都 $>$ 目标。
- **D3（路线二的解释错误）**：路线二 §10 猜 "$\frac1{2048}$ 对应只有一个 $o_i$ 进 pool 的
  非对称紧实例（$\lvert C\rvert=1$，一轮 extension）"。实测**相反**：交付实例的
  $\lvert C\rvert=5$，$o_1$ 与 $o_2$ **都**在 pool 内，$r=4$（四轮全跑满）。
  $\sum_j(\gamma_j-\beta)=\frac12$ 的真实来源是：四轮里只有第 2 轮取到 $o_1$
  （贡献 $(1-\frac35)+(\frac7{10}-\frac35)=\frac12$），另外三轮被 B-block 元素占据，
  产出的 6 个 secondary set 全部恰等于 $\frac35$。$n=6$ 的 8 个 secondary 真值为
  $\frac35,\frac35,1,\frac7{10},\frac35,\frac35,\frac35,\frac35$ [VERIFIED-EXHAUSTIVE]。
  **推论**：交付的紧实例离路线二的缺口只差一轮，它是情形 II-a 里 surplus 最小的形态，
  四轮中三轮已经是 "挡路者" 结构。这使 G1 不是边角情形，而在缺口的主路上。
- **D4（算术常数）**：R6 的 $\frac52\varepsilon$ 应为 $5\varepsilon$（方向用错）。下游无影响。
- **D5（corollary 缺失）**：statement 末句的 "$\lvert S\rvert\le K$ 限制对 $\frac92nK$ 预算的
  随机算法必要" 路线二未写出（盲证输入包不含 `thm:linear-exact`）。
- **D6（tie-breaking 量词）**：路线二把 statement 的 "fixed tie-break order" 读成
  "adversary 可选该序"，与 `assumptions.md` 一致，是加强而非放松。
- **D7（$9n$ 核算）**：路线二 G3 说朴素上界是 $10n-9$、$n\ge10$ 时超过 $9n$，靠缓存才落到 $9n-8$。
  本轮逐步复算给出更紧的结果：第 1 步 $n$、第 2 步 $n-1$、第 3 步 $0$、第 4 步四轮的
  extension argmax 至多 $(n-2)+(n-3)+(n-4)$（第 1 轮全部命中第 2 步的缓存）加
  $z_v$ 的 $4(n-2)$（$\{v,b\}$ 命中缓存），合计 $\le9n-18$。实测 spot-check 家族恰为 $9n-24$
  （$n=6,8,12,20$ 分别 $30,48,84,156$）[VERIFIED-EXHAUSTIVE]。
  **G3 实际是闭合的**，路线二对自己过于保守。
- **D8（随机证据家族不同）**：路线一跑 400 个随机 coverage 实例，
  surrogate $G=F+\frac12F'$，worst ratio $=\frac45$；路线二跑 400 个结构化实例，
  min $\mathbb E/\mathrm{OPT}=\frac{1537}{2048}=0.75049$，min $f(P_0)/\mathrm{OPT}=\frac34$。
  两族的 surrogate 都是 submodular（$F+\frac12F'$ 是两个 coverage 的正组合），
  都离 $\frac35$ 很远，**两条路线的随机证据同样弱**，不能互为佐证。
- **D9（query size 覆盖面）**：命题的 payload 是 $\lvert S\rvert\le5>K=2$，
  路线一的实例实际取到 $5$，路线二的实例只到 $3$。路线二的构造没有行使 payload 的上限。

---

## 4. Route-two gaps（逐条）

- **G1（主缺口，情形 II-b）** `[FAILED]`：需要 "若 $o_1,o_2\in C$ 且 $\varepsilon<4.0945\times10^{-6}$，
  则四轮 extension 中至少有一轮取到某个 $o_i$"。路线二没有证出也没有证伪。
  已知部分结果：挡路的必要条件 $\frac32d_{v_k}(B)\ge d_o(B)$ 与 (L5) 给
  $f(B\cup\{v_k\})\ge\frac{1+2f(B)}3$，故 $\frac35\to\frac{11}{15}\to\frac{37}{45}\to\frac{119}{135}$
  （本轮复算无误），但 $\frac{119}{135}=0.8815<1$ 且 $\lvert B\rvert\ge3$ 时 $f$ 本就可以超过 $\mathrm{OPT}$，
  不产生矛盾。该格下只得到 $\mathbb E\ge(\frac35-1.5625\times10^{-6})\mathrm{OPT}$，比目标低 $4.0625\times10^{-6}$。
  本轮补充的收紧条件：II-b 强迫 $\lvert C\rvert\ge6$（路线二未写）。
- **G2（R6 常数）** `[FAILED]`：$\frac52\varepsilon$ 应为 $5\varepsilon$，见 D4。下游无影响，但文件与脚本都要改。
- **G3（对 $\frac1{2048}$ 的解释）** 路线二标 `[CONJECTURE]`，本轮**证伪**，见 D3。
- **G4（引理 D (D2) 的退化情形）**：$v=o^\ast$ 时 (L2) 的 $u\ne e$ 前提失效，文件未处理。可一行补上。
- **G5（case split 的层次）**：$b\in O^\ast$ 只在情形 0 的括注里被吸收，未写成显式第一层分叉。
- **G6（$n=4$ 实例的展示不完整）**：§10 只列出 $\lvert S\rvert\le2$ 的 $\tilde f$ 值加 $\tilde f(\{o_1,o_2\})$，
  size 3、4 的值没给。本轮用极大补全 $\tilde f(S)=\min_{e\in S}\{\tilde f(S\setminus e)+\frac32d_e(S\setminus e)\}$
  独立重建，全 16 子集与全 $(S,e)$ band 通过 [VERIFIED-EXHAUSTIVE]，所以实例本身没问题，只是文件没写全。
- **G7（$9n$ 的一般性核算）** 路线二标 `[HAND-PROOF-UNREVIEWED]`。本轮收紧到 $\le9n-18$，
  见 D7，可以升级；但仍依赖 statement 明写的 "each distinct set is queried once (cached)"。
- **G8（随机证据弱）** 路线二自报，本轮确认，且路线一的随机证据同样弱，见 D8。

---

## 5. 状态标签汇总

| 对象 | 标签 |
|---|---|
| 路线一（J8 证明） | **不存在**；J8 命题整体维持 `[HAND-PROOF-UNREVIEWED]`，criterion B 无法组装 |
| 路线二 §3 的 L0-L5 | `[HAND-PROOF-UNREVIEWED]`（逐条复核无误，无 oracle 可自动确认集合级推理） |
| 路线二命题 4.1（$\beta\ge\frac35$） | `[HAND-PROOF-UNREVIEWED]`；$\min\max$ 算术 `[VERIFIED-SYMBOLIC]` |
| 路线二命题 4.2（$n=4$ 紧实例） | `[VERIFIED-EXHAUSTIVE]`（本轮独立重建通过） |
| 路线一紧实例（J6 double-residual，$n=6,8$） | `[VERIFIED-EXHAUSTIVE]`（本轮独立重建通过：monotone、submodular、band、$\frac35+\frac1{2048}$、$\le9n$、maxsize $5$） |
| R1-R5、R7、R8 | `[VERIFIED-SYMBOLIC]` |
| R6 | `[FAILED]`（常数 $\frac52\varepsilon$ 错，正确值 $5\varepsilon$；下游无影响） |
| 引理 P、引理 D、情形 0、情形 I、情形 II-a | `[HAND-PROOF-UNREVIEWED]`；全部阈值与余量算术 `[VERIFIED-SYMBOLIC]` |
| 情形 II-b | `[FAILED]`（未闭合，差 $4.0625\times10^{-6}$） |
| $9n$ 与 $\lvert S\rvert\le5$ | `[VERIFIED-EXHAUSTIVE]`（所跑实例）+ $\le9n-18$ 的逐步核算 `[HAND-PROOF-UNREVIEWED]` |
| 随机证据（两条路线合计 800 个实例） | `[CONJECTURE]`，两族 surrogate 都 submodular，证据弱 |

---

## 6. 结论

**verdict: B-MISSING（no route one）。**

理由：criterion B 要求两条独立路线相互作证书；J8 的路线一从未交付，比对退化为
"路线二 vs 陈述"。即使不看这一点，路线二本身也没有闭合（情形 II-b），
所以 **B-PASS 与 B-PASS-with-different-route 都不成立**；
若强行把陈述当作路线一，则退化判定为 **B-GAP（route two incomplete）**。
两种读法下，J8 都不能升级标签，应在台账里保持 `[HAND-PROOF-UNREVIEWED]`，
并在正文里保持 "must-not-claim"：不得声称 J8 已验证，不得把它当作
"$\lvert S\rvert\le K$ 限制必要" 的已证依据。

对下一轮最有价值的两条：
1. 交付 `results/J8/probe_lottery.md` 的 (3),(8)-(12)，特别是覆盖情形 II-b 的那条。
   路线二的证据指出所缺的工具是 **triple 级的 (L2)**（$\tilde f(B\cup\{v\})$ 与
   $\tilde f(B\cup\{o\})$ 的两侧夹逼），而不是任何 pair 级不等式。
2. D3 的发现应回灌：交付的紧实例四轮里有三轮是挡路者结构，说明 II-b 在构造上是可达的邻域，
   不能当作边角情形忽略。
