# THEOREM_LEDGER.md — 定理台账（写作时的唯一调用来源）

规则：每条定理一张卡，字段固定。写作时只准从这里取陈述与状态，不准凭记忆。
状态标签：[VERIFIED-SYMBOLIC] [VERIFIED-LP] [VERIFIED-EXHAUSTIVE] [HAND-PROOF-UNREVIEWED] [CONJECTURE] [OPEN]。
"禁止声称"一栏是空洞性检验和审稿反例的沉淀，比陈述本身更重要。
本版：2026-09-07，J2 修正后的目标形态；标注 (K1)(K4) 等的字段以当晚 Claude Code 落实的版本为准。

---

## T0 模型（model.tex）
- 对象：N，|N|=n；f 单调 submodular，f(∅)=0，不可查询；f̃ 任意集合函数（D1：不要求 submodular），f̃(∅)=0，可查询。
- 误差（Definition 1）：η_u,η_o ≥ 1，∀S,e∉S：d_e(S)/η_u ≤ d̃_e(S) ≤ η_o d_e(S)；η=η_u η_o。蕴含 d=0 ⇔ d̃=0，d̃ ≥ 0。
- 近似比 α∈(0,1]，F^ALG ≥ α F^OPT。
- 尺子链 η^sel ≤ η^tr ≤ η（三行证明，第二条不等式 = 原 Lemma 5 首行）。
- 禁止声称：η 只依赖乘积 η_u η_o 是 LP 观察 + 一行缩放论证（f̃→c f̃ 不改 argmax），写进正文前要把这一行写成 lemma。

## T1 prop:nobound — 无误差假设则无常数保证
- 陈述：不假设 η 上界时，对任意算法、任意 n ≥ 2K，存在 (f,f̃) 使输出 T 满足 f(T) ≤ K/(n−K)·f(O*)。
- 前提：任意查询访问 f̃。
- 状态：[HAND-PROOF-UNREVIEWED]（两实例不可区分，原 Lemma 1 的推广）。
- 禁止声称："no algorithm is robust" 可以说，"robust" 一词不得用于描述本文算法。

## T2 prop:valueacc — value accuracy 既不充分也不必要（H1 恢复）
- 陈述：(i) ∀ε∈(0,1) 存在 value-accurate at level ε 的 f̃，某处 d̃=0 而 d>0，故 Definition 1 的 (η_u,η_o) 无限；
  (ii) ∀M>0，f̃=(1+M)f 在任何 ε<M 下不 value-accurate，但 η^sel=1，保证完整成立；
  (iii) 误差 ≤(η_u,η_o) 的 f̃（f 非负）是 value-accurate at level max{1−1/η_u, η_o−1}。
- 状态：(i)(iii) 按原 Lemma 2/3 重写 [HAND-PROOF-UNREVIEWED]；(ii) 两行缩放观察。
- 禁止声称："value accuracy is irrelevant"——(iii) 说明 η 有界蕴含 value accuracy，是单向蕴含。

## T3 prop:guarantee — predictive greedy 的保证（D2：归属 GS）
- 陈述（K1 后）：f 单调 submodular；run 的选择误差 η^sel（新定义：a_t=M_t/g_t，M_t=g_t=0 取 1，g_t=0<M_t 取 ∞，η^sel=max{1,a_t}，L_K(∞)=0）。则 f(T) ≥ L_K(η^sel) f(O*) ≥ (1−e^{−1/η^sel}) f(O*)，L_K(x)=1−(1−1/(xK))^K。同一界对 η^tr、η 成立。
- 归属：essentially due to Goundan & Schulz (2007, Theorem 1)，α=η^sel（同向，不取倒数），要求每步满足近似选择条件。证明附录 for completeness。
- 状态：[VERIFIED-LP 第一晚基线] + 附录证明（NWF 权重求和）。
- 禁止声称："we prove"；旧定义下的无条件证书（J2 三元素反例 (1,1,0)/(2,1,3) 比值 1/2 < 3/4）；对非单调目标（E1 accuracy、E3 ROUGE）称 certificate。
- 附属 remark：逐步乘积界 1−∏(1−1/(K a_t)) [HAND-PROOF-UNREVIEWED]，反例上取等。

## T4 thm:tight — 逐 K 紧（选择误差）
- 陈述：∀K ≥ 2, â>1，存在 2K 元素实例 U_K（f=1−a^x(1−y/K)，a=1−1/(âK)，f̃ 显式），adversarial-tie run 上 η^sel=η^tr=â，输出恰 L_K(â) f(O*)。
- 状态：[VERIFIED-SYMBOLIC 一般 K]（T5 脚本 105/105，含 all-pairs 误差 η_u=â、η_o=aK/(K−1)）。
  K1 数值确认已完成：新逐步定义下 η^sel=η^tr=â 逐位不变、全程无零步，14/14
  （results/K1_etasel_newdef_check.py，K=2..8，â∈{1.5,2}）。
- 禁止声称：作为独立新结果（本质是 GS 模型的紧性，注明）；"strict preference" 版本未经端点处理（J2 §3：段左端点扰动破坏单调性，主定理以 adversarial tie 为前提）。

## T5 lem:coherence — coherence lemma（唯一新引理）
- 陈述：f 单调，S⊆N，e,e'∉S，d̃_e(S) ≥ d̃_{e'}(S)。则 (i) d_e(S∪{e'}) ≥ d_{e'}(S∪{e})/η；(ii) (1−1/η) d_{e'}(S∪{e}) ≥ d_{e'}(S)−d_e(S)。
- 状态：两行证明（f̃(S∪{e,e'}) 两种展开）；J2 §2 给出三项非负 slack 分解 [VERIFIED-SYMBOLIC]。
- Sharp form（H-J3 采纳）：d − g/η ≥ (1−1/η)(g−h) ≥ 0，其中 d=d_e(S)、g=d_{e'}(S)、h=d_{e'}(S∪{e})；
  第一个不等号是 (ii) 的等价改写 [VERIFIED-SYMBOLIC，results/H_J3_gate_check.py]，第二个另用 f 的
  submodularity。推论：η>1 且 d=g/η 时必有 h=g。作为 lemma 的 sharp form 陈述，不另立新定理。
- 禁止声称：对 η^sel 或 η^tr 成立（它用到离轨状态 S∪{e} 的误差带，必须全局 η）。

## T6 thm:exact — 精确最坏值（主定理）
- 注意："原界对有限 K 严格不紧"必须限定 η > 1；η=1 时 ρ_K(1)=L_K(1)。
- 陈述：K ≥ 2, η ≥ 1，adversarial tie：ρ_K(η)=min_{0≤j≤K−1} V_j(η)，V_j=1−q^j(1−(K−j)/(Kη))，q=(K−1)η/((K−1)η+1)；段 [K−j,K−j+1] 上由 V_j 取到，[K,∞) 上 V_0=1/η；分段点整数 2..K；ρ_K=1/η ⇔ η ≥ K。K=2,3,4 显式闭式见正文。
- ≥ 方向：四族有效不等式（R6：J2 slack 证书 [VERIFIED-SYMBOLIC] + 1,536 目标 LP）+ 一般 K 显式对偶乘子（N1 320/320，J2 独立 456 例；G2 附录逐行）。
- ≤ 方向：每个 j 的三类元素显式实例（N2 480/480，一般 K 符号）。
- 全格点=reduced LP：K ≤ 5 [VERIFIED-LP]。
- 禁止声称：ρ_K(η^sel) 是某 run 的保证（J2 §5 反例：η^sel=2 而 ratio=7/16<ρ_2(2)）；主图 ρ_K 曲线不得画在 η^sel 轴；V_i−V_{i+1} 索引 i ≤ K−2；对 η^sel 陈述精确值。
- 副产品：下界证书中单调约束乘子恒为零（不等于可删 f 的单调性，coverage 归约仍用）；U_K > V_{K−1} 对所有 η>1（U_K 族不紧）。
- 禁止声称（H-J3 追加）：T6b 的轨迹唯一性延伸到整数断点（K=3, η=2 有两条 7/15 轨迹）；唯一性约束未选候选的边际。

## T6b prop:rigidity — 非断点最坏轨迹的刚性（H-J3 新增）
- 陈述：K ≥ 2；η ∈ (K−j, K−j+1) 且 1 ≤ j ≤ K−1，或 j=0 且 η > K；OPT 归一化为 1。若一次
  adversarial-tie run 达到 ρ_K(η)=V_j(η)，则其诱导的 reduced-LP 变量满足
  d_t = q^t/k_1（t<j）、q^j/(Kη)（t≥j），g_{t,i} = q^{min(t,j)}/K（0 ≤ t ≤ K）。
- 证明：互补松弛（正乘子支撑：coverage t=0..j、consistency t=0..K−2 每个 i、prediction t=j..K−1
  每个 i）+ J3 §2.1 递推归纳（早期几何段、t=j 对称化、后期冻结、向后回推、末步锁定）。
- 状态：递推恒等式 [VERIFIED-SYMBOLIC，results/H_J3_gate_check.py]；40 个有限最优面、2,480 次
  坐标极值 LP 全塌缩到该序列 [VERIFIED-LP 同脚本，最大偏差 4e-15]；从一般对偶证书到任意规模
  实际轨迹的互补松弛与归纳装配 [HAND-PROOF-UNREVIEWED]。
- 范围：只约束选中增益与最优元素沿轨迹的边际；不唯一确定整个 f、f̃ 或未选候选的边际；
  由 g 全正与置零约定，此类精确最坏 run 与所固定的 O* 不交。
- 附属 remarks：断点 = active-constraint switch（λ_P(j) 在段左端点消失、λ_S(j) 在段右端点消失；
  K=3, η=2 两条轨迹 (1/5,2/15,2/15) 与 (1/5,4/25,8/75) 均和 7/15）；精确取等强迫每步与最优元素
  的预测增益打平（P=Q，slack 分解逐项为零推出，装配 [HAND-PROOF-UNREVIEWED]）；近等号
  slack_r ≤ ε/λ_r（不升级为统一稳定性定理）。
- 禁止声称：断点处唯一性；全体候选的最大真实边际被约束；"相变" 措辞（用 active-constraint switch）。

## T7 rem:exact-gap — submodular surrogate（D1 remark）
- 陈述（K6 后）：若额外要求 f̃ submodular，在已验证的 LP 点上最坏值严格更高（K=3, η=1.5: 9/16→19/33）；η=1 时两模型重合；一般刻画 [CONJECTURE ρ_K^sub=min_m W_m，q→r=1−1/K，76/76 点]，[OPEN]。
- 禁止声称："strictly improves for all η<K−1"；"U_K no longer an upper bound"（实例失效≠界失效，19/33<37/64）；"more robust"。

## T8 thm:ceiling — 1/η 天花板
- 陈述：任意确定性算法、任意 η_u,η_o ≥ 1、n ≥ 2K，存在误差恰为 (η_u,η_o) 的实例使 f(T) ≤ f(O*)/η；随机算法期望 ≤ (1−K/n)/η+K/n；对 f̃ 穷举 K-子集在任何实例上 ≥ f(O*)/η。
- 状态：[HAND-PROOF-UNREVIEWED]（对称 f̃=c|S|，modular f，O 藏在输出外）。
- 禁止声称：n<2K 时的值（[OPEN]，明晚 E 项）；"1/η 是多项式算法的界"（它是信息论的）；
  "η ≥ K 时 greedy、穷举与任何算法相同"（只能写 greedy 达到不限查询的确定性最优保证）；
  随机上界 (1−K/n)/η+K/n 是有限 n 下的精确最优（它只是上界）。
- 构造的误差恰为 (η_u,η_o)：J4 精确穷举 253,220 个 all-pairs 增益 [VERIFIED-EXHAUSTIVE]。
- 副产品（J4）：1 ≤ η < K 时穷举的最坏保证 1/η 严格优于 greedy 的 ρ_K（ρ_K ≤ V_1 < V_0），
  差 ≥ (K−η)/(Kηk_1)；K=3：η=1: 19/27 vs 1；1.5: 9/16 vs 2/3；2: 7/15 vs 1/2；3: 相等。比较的是最坏保证。

## T9 cor:limit — 渐近
- 陈述：固定 η，L_K(η)、ρ_K(η) → 1−e^{−1/η}；L_K 关于 K 单调（ρ_K 单调性 [OPEN]，G2 已删该子句）。
- 状态：由 L_K ≤ ρ_K ≤ U_K 与两侧极限。
- 待加（明晚 B 项）：ρ_K=1−e^{−1/η}+c(η)/K+O(1/K²)，c(1.5)≈0.228, c(2)≈0.227, c(3)≈0.197 [数值]。

## T10 thm:hardness — 有界查询 hardness（K4 后按 J2 校准）
- 陈述：c ≥ 0 实数，τ=⌈c⌉+1，K>τ，n ≥ 4K^{c+2}，η>1 且 η ≥ (K−1)/(K−τ)，θ̄=(η(K−τ)+1)/K。任意确定性算法，≤n^c 次、每次集合大小 ≤K 的 f̃ 查询、输出 ≤K 元素，存在实际误差恰为 η 的实例使 f(T)/f(O*) ≤ H_{K,τ}(η)=1−(1−1/(η(K−τ)+1))^K=L_K(θ̄)。随机版加 ε_n=K/n+K^{2τ+2}/((τ+1)! n^{τ+1−c})。
- 状态：边表与校准 [VERIFIED-SYMBOLIC]（J2 264 实例 + 我方复核）；transcript/并集界/两次平均 [HAND-PROOF-UNREVIEWED]。
- 副产品：τ=1 时 H_{K,1}=U_K，故 L_K ≤ ρ_K ≤ U_K=H_{K,1}。
- 禁止声称："error exactly η" 用旧 Φ 校准；查询大小不限（那是 F3 版本）；任意多项式次数的类最优（见 T11）；
  "non-trivial" 而不说明是渐近匹配（有限参数下 H 可大于 1/η，如 η=2,c=2,K=8 时 H≈0.533）；
  随机版 K→∞ 时 ε_n 自动消失（需 n ≥ 4K^{c+3} 之类）；把查询大小限制等同于多项式时间。

## T11 rem:hardness-pins — 查询类最优性（K5 后）
- 陈述：greedy 用 ≤ Kn−K(K−1)/2 次查询；当 nK ≤ n^c（如整数 c ≥ 2, K ≤ n）时，该查询类的渐近最优值为 1−e^{−1/η}，有限 K 间隙 O((c+1)/K)。
- 禁止声称：c=0,1 的类（精确穷举反例：单查询算法可被逼到 0）；"O(c/K)"；有限 K 的同预算最优性
  （[OPEN]：只排除渐近常数的统一改进，不排除有限 K 或低阶项的改进）。

## T12 F3 任意大小查询 hardness（附录：构造方向与有限证据，不作 theorem）
- 内容：任意大小查询、预算 Q ≤ n²/(2K²(t*+K)²) 的确定性算法在已检查参数上不超过 greedy 的渐近值。
- 状态：坏实例的单调、submodular、归一化只有有限参数穷举 [VERIFIED-LP 有限]；j、m* 一般闭式无证明；
  随机版另用未核查的构造不等式；装配 [HAND-PROOF-UNREVIEWED]。J4 裁定：不能以已完成定理计入。
- 禁止声称：作为 theorem；任意多项式预算；n^{2−o(1)} 而不限制 K、η 的增长；"指数 2 内在上限"超出已检查的 48 组参数。

## T13 附录：pair greedy（R12）
- 陈述：K=4、all-pairs 误差下 pair greedy 精确最坏值 = ρ_2(η)（η∈{1.5,2,3}）。一般 K [CONJECTURE]。
- 禁止声称："exactly halves K for all K"。

## T14 附录：加性混合模型（N6）
- 陈述：d/η_u−ε ≤ d̃ ≤ η_o d+ε ⇒ F^PG ≥ L_K(η)(OPT−2Kη_u ε)；LP 显示 ε 项紧。
- 禁止声称：真实 surrogate 满足该模型（量化尺度 ε 下 88% 数据行不满足）。

## T15 实验中的理论量（K2 后）
- ratio 分母 greedy-on-f 是 OPT 的下估 ⇒ ratio 是真实比的上估（方向勿反）。
- E2（coverage，模型内）：新定义下 16 个有害零步 run 的 η^sel=∞；其余 run 有 per-run certificate。
- E1/E3（非单调目标）：selection diagnostic + 模型违反记录；L_K 列为 reference 非 certificate。
- E4：19 个构造实例贴理论值 ≤1e−16；只在全局 η 轴与 ρ_K 比较。
- 禁止声称："all real tasks lie above both guarantee curves"；"structurally zero"（E2 零对正 pair 30,416 条）。

---
维护规则：任何定理陈述改动，先改本文件对应卡，再改 .tex；卡上的状态标签与 results/ 脚本一一对应。
