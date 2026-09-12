# THEOREM_LEDGER.md — 定理台账（写作时的唯一调用来源）

规则：每条定理一张卡，字段固定。写作时只准从这里取陈述与状态，不准凭记忆。
状态标签：[VERIFIED-SYMBOLIC] [VERIFIED-LP] [VERIFIED-EXHAUSTIVE] [HAND-PROOF-UNREVIEWED] [CONJECTURE] [OPEN]。
"禁止声称"一栏是空洞性检验和审稿反例的沉淀，比陈述本身更重要。
本版：2026-09-12 深夜（J5 到齐日 J5H1-J5H6：T8 统一 ceiling 重写并升级达到方向、T7 加 β_m 下包络与
措辞禁令、T9 首行统一与历史归档、T11 PE₁ 精确证书升级与撤回条；此前同日第八晚 M0-M5：T0 lem:scaling 与固定 K 步、T1/T2/T3 量词与定义域、T6 n 量词、T7 M3.2 精确点与方向更正、T8 随机量词、T10b 改名与 n ≥ 4K⁵ 量词、T11 证据等级与候选总结、T14 范围、M4 九条禁止声称；J5 输入文件未送达，处理规则见 results/J5/MISSING_INPUTS.md；此前第九晚 P0-P3、第七晚 L 系列）；每卡状态标签与 results/ 脚本一一对应。

---

## T0 模型（model.tex）
- 对象：N，|N|=n；f 单调 submodular，f(∅)=0，不可查询；f̃ 任意集合函数（D1：不要求 submodular），f̃(∅)=0，可查询。
- 误差（Definition 1）：η_u,η_o ≥ 1，∀S,e∉S：d_e(S)/η_u ≤ d̃_e(S) ≤ η_o d_e(S)；η=η_u η_o。蕴含 d=0 ⇔ d̃=0，d̃ ≥ 0。
- 近似比 α∈(0,1]，F^ALG ≥ α F^OPT。
- 尺子链 η^sel ≤ η^tr ≤ η（三行证明，第二条不等式 = 原 Lemma 5 首行）。
- lem:scaling（M1 落实，替代原禁止项）：band 类 𝓕(η_u,η_o) = {f̃ : Definition 1 成立}；对 c ∈ [1/η_o, η_u]，
  f̃ ↦ c·f̃ 是 𝓕(η_u,η_o) → 𝓕(η_u/c, c·η_o) 的双射，保持全部 argmax 比较与 f 本身，故 comparison-based
  算法（greedy 在内）的每个 run 与最坏比在乘积相同的 band 类间不变。只对"类"陈述，不对给定 f̃ 的
  实际最小因子陈述（那会随缩放变）。状态：[HAND-PROOF-UNREVIEWED 三行] + 变换恒等式 sympy
  （results/M1_checks.py）。
- 算法语义（M1 统一，J5 §3 反例经 M0 有理复算确认）：predictive greedy 固定执行恰 K 步，最大预测增益
  为零的步也继续选（a_t 三类穷尽该情形）；提前停止变体只享有已执行步的乘积界（rem:app-product 范围），
  不享有 L_K 保证（两元素反例 ratio 1/2 < L_2(1)=3/4，results/M0_counterexamples.py §1）。
- 约定（M1）：全文假设 1 ≤ K ≤ n；f(O*) = 0 时一切比值陈述按约定读作成立（ratio = 1）；K ≥ 1 故无空轨迹。
- 禁止声称：对提前停止变体声称 L_K(η^sel) 保证；lem:scaling 用于依赖 f̃ 数值（非比较）的单个算法的
  逐算法不变性（只有类的双射与 comparison-based run 不变性）。

## T1 prop:nobound — 无误差假设则无常数保证
- 陈述（M1 量词校正）：不假设 η 上界时，对任意**确定性**算法、任意 n ≥ 2K，存在 (f,f̃) 使输出 T 满足
  f(T) ≤ K/(n−K)·f(O*)。
- 前提：任意查询访问 f̃。
- 状态：[HAND-PROOF-UNREVIEWED]（两实例不可区分，原 Lemma 1 的推广）。
- 随机版（M1，J5 量词规格）：未单独陈述。正文注释注明：随机类比需按"对每个随机算法存在固定实例使
  E_seed[·] ≤ …"的量词经 app:hardness 式平均得出，本文未给常数，不声称。
- 禁止声称："no algorithm is robust" 可以说，"robust" 一词不得用于描述本文算法；把 "every algorithm"
  读成含随机算法（陈述已限定 deterministic）。

## T2 prop:valueacc — value accuracy 既不充分也不必要（H1 恢复）
- 陈述：(i) ∀ε∈(0,1) 存在 value-accurate at level ε 的 f̃，某处 d̃=0 而 d>0，故 Definition 1 的 (η_u,η_o) 无限；
  (ii) ∀M>0，f̃=(1+M)f 在任何 ε<M 下不 value-accurate，但 η^sel=1，保证完整成立；
  (iii) 误差 ≤(η_u,η_o) 的 f̃（f 非负）是 value-accurate at level max{1−1/η_u, η_o−1}。
- 状态：(i)(iii) 按原 Lemma 2/3 重写 [HAND-PROOF-UNREVIEWED]；(ii) 两行缩放观察。
- (iii) 定义域修正（M1，J5 §规格）：value accuracy 的引用定义取 ε ∈ (0,1)，而 max{1−1/η_u, η_o−1}
  在 η_o ≥ 2 时 ≥ 1 出域；(iii) 加条件"provided max{1−1/η_u, η_o−1} < 1"（即 η_o < 2），
  不改 Hassidim-Singer 的被引定义（保守二选一，理由：引用定义不动）。
- 禁止声称："value accuracy is irrelevant"——(iii) 说明 η 有界蕴含 value accuracy，是单向蕴含；
  (iii) 在 η_o ≥ 2 时照原样引用。

## T3 prop:guarantee — predictive greedy 的保证（D2：归属 GS）
- 陈述（K1 后）：f 单调 submodular；run 的选择误差 η^sel（新定义：a_t=M_t/g_t，M_t=g_t=0 取 1，g_t=0<M_t 取 ∞，η^sel=max{1,a_t}，L_K(∞)=0）。则 f(T) ≥ L_K(η^sel) f(O*) ≥ (1−e^{−1/η^sel}) f(O*)，L_K(x)=1−(1−1/(xK))^K。同一界对 η^tr、η 成立。
- 归属：essentially due to Goundan & Schulz (2007, Theorem 1)，α=η^sel（同向，不取倒数），要求每步满足近似选择条件。证明附录 for completeness。
- 状态：[VERIFIED-LP 第一晚基线] + 附录证明（NWF 权重求和）。
- 禁止声称："we prove"；旧定义下的无条件证书（J2 三元素反例 (1,1,0)/(2,1,3) 比值 1/2 < 3/4）；对非单调目标（E1 accuracy、E3 ROUGE）称 certificate；对提前停止变体声称本命题（M1：停止版只有已执行步乘积界，反例 results/M0_counterexamples.py §1）；
  由**停止前**的 η^sel 推 L_K 界（M4：同一反例，已执行步 a_t 全为 1 而 ratio = 1/2）。
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
- n 量词（M1，规格转述自 J5 §13）：ρ_{n,K}(η) = 固定 ground set 大小 n 的精确最坏比；n ≥ 2K 时
  ρ_{n,K} = ρ_{2K,K} = ρ_K。证明：restriction（把最坏 run 的实例限制到 T∪O*，run 仍合法、比值与
  OPT 不变）+ padding（补零元素，d = d̃ = 0 保带，attaining run 不受影响）
  [HAND-PROOF-UNREVIEWED，本地重构]；数值支持 [VERIFIED-LP]：L2 Gate 1 的全格点 greedy LP 在
  K=2, n∈{4,5,6} 与 K=3, n∈{6,7} 逐点等于 ρ_K（results/L2_linear_candidates.py gates）。
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

## T7 rem:exact-gap — submodular surrogate（D1 remark；H-C 后）
- 陈述：若额外要求 f̃ submodular，在已验证的 LP 点上最坏值严格更高（K=3, η=1.5: 9/16→19/33；K=4, η=2: 22/49→23/50）；η=1 时两模型重合。
- 上界方向 [VERIFIED-LP]（H-C）：对每个 K、m ∈ {0,…,K−1}、η ≥ 1 与每个拆分 η=η_u η_o，存在显式实例
  （n=2K，f 与 f̃ 都单调 submodular，误差恰 (η_u,η_o)，对抗 tie 下 greedy 选满 K 步）比值恰为
  W_m(K,η)=(K−m r^m)/(K(1+(η−1)r^m))，r=1−1/K；故 ρ_K^sub(η) ≤ min_m W_m(η)。
  实例公式与 410 点验证：results/H_C_submodular_surrogate.md §6 + .py Part F。
- 下界方向仍 [CONJECTURE]/[OPEN]：无证书；94 个全格点 LP 点吻合（F4 76 + H-C 18 个分段边界点）。
  卡点：路径变量 reduced LP 加全部自然 f̃-submodularity 有效不等式后值仍为 min_j V_j（42/42
  [VERIFIED-LP]），该批不等式不足以给下界（H-C §5）。
- 紧系统 ⟹ W_m [VERIFIED-SYMBOLIC]（符号 K,m,η_u,η_o；机制推导非下界证明）。
- 分段点（J5H4，来源 J5 hardcore §1.4）：相邻分支交点 **β_m = 1 + (K−m−1)/(K(1−r^{m+1}))**，
  m = 0..K−2，随 m 严格下降；取 β_{−1}=∞、β_{K−1}=1，则 W_m 在 [β_m, β_{m−1}] 上是全族最小。
  交点恒等式与 W_m−W_{m+1} 的符号判别式 [VERIFIED-SYMBOLIC，results/J5_hardcore/
  J5_hardcore_oracles.py]；由相邻差符号到区间活跃性的装配 [HAND-PROOF-UNREVIEWED，来源 J5]。
  **这是候选上界族的下包络描述，不是一般匹配下界。** 一般参数实例核验升级：J5 对 56 个实例、
  121,344 条边、262,144 个方块 Fraction 精确通过（含非对称拆分），一般参数的四点手证
  （二阶差分非正、band 端点、逐步打平、OPT=1）[HAND-PROOF-UNREVIEWED，来源 J5]。
  措辞禁令：不写"把 V_j 的 q 换成 r"（直接替换得不到该分母；该说法只出现在送审 dossier，
  仓库正文从未使用，本条为预防性登记）。
- 禁止声称（M4 追加）：用高比值实例证明 ρ^sub 的 worst-case 下界（实例只给上界 ρ^sub ≤ 值；
  下界要对偶/保证侧证书，J5 指出的方向错误，M3.2 处理中）。
- 禁止声称："strictly improves for all η<K−1"（只在部分点验证）；"ρ_K^sub = min_m W_m"（下界无证书）；
  "more robust"；把实例族说成证明相等（只给 ≤）；推广到一般 n（族与 LP 都在 n=2K）。
- M3.2 精确点（2026-09-12，本地重建替代未送达的 J5 对偶 JSON，未与 J5 比对）：
  **ρ^sub_{8,4}(3/2) = 23/41，双侧精确**。上界侧：H-C §6 实例 Fraction 重建（两函数单调 submodular、
  band 恰为拆分、greedy 逐步打平、比值精确 23/41、7702 行 0 违反）[VERIFIED-SYMBOLIC-EXACT]；
  下界侧：16 个轨道的精确有理对偶，提升回完整 7702 行逐坐标核对并搬运到全部 70 个 target set，
  y > 23/41 时对偶系统不可行 [VERIFIED-EXACT-DUAL]；模型到 LP 的三步归约（拆分归一化/分支钉住/
  OPT 归一化）[HAND-PROOF-UNREVIEWED]。三个有理拆分同值。results/M3_rhosub_K4_exact.{md,py,json}。
  推论（方向正确的证据）：23/41 > U_4(3/2) = 8080/14641（336743 > 331280）且 > ρ_4(3/2) = 1447/2662，
  故 U_K 在 submodular-surrogate 模型不再一般成立为上界；此前"显式实例背书"是方向错误的证据
  （实例只给 ρ^sub ≤ 值），已按 J5/M3.2 更正。n ≥ 8 同值：restriction+padding（rem:exact-n 论证移植，
  restriction/padding 保持 f̃ 的 submodularity 与 band）[HAND-PROOF-UNREVIEWED，本地]。
- 修订原禁止项："U_K no longer an upper bound" 的禁令限定到原模型：U_K 仍是 ρ_K 的上界，对
  ρ_K^sub 在 K=4, η=3/2 处**证实失效**（上一条，双侧精确）；在其他已验证点（K=3, η=1.5 的
  19/33 < 37/64；K=4, η=2 的 23/50 < 61/125）U_K 数值上仍在其上。
- J5 §13 的 W_m 一般手证未转录（原文缺失）；上界方向维持 H-C 的 [VERIFIED-LP 410 点]。

## T8 thm:ceiling — 确定性天花板，统一到全部 ground-set 大小（J5H2 重写）
- 统一陈述（来源 J5 套 A，results/J5_hardcore/J5_ceiling_proof.md）：2 ≤ K ≤ n，确定性、任意查询
  次数与大小、输出 ≤ K。minimax 值 **C*_{n,K}(η) = K/(K+(η−1)·min{K, n−K})**
  （K ≤ n ≤ 2K 时 = K/((2K−n)+(n−K)η)，n ≥ 2K 时 = 1/η）。
  上界侧：对每个确定性算法存在实例（f̃ = b|S| 线性预测 + modular 高低权 f，任意拆分 (η_u,η_o)
  实际误差两端恰取到；n=K 时输出全集比值 1，端点校准用混合高低权）。
  下界侧（**达到**）：穷举 argmax_{|T|=K} f̃ 在每个实例上 ≥ C*，且有更强的**逐实例式**
  f(S)/f(O) ≥ K/(K+(η−1)|O∖S|)（重叠越多越强，无最小重叠假设）。
- 证明结构（J5 三步）：(i) 交换求和：对全部 aK 对 (b,s) 用 f̃(S) ≥ f̃(S∖{s}∪{b}) 与两侧带得
  KD ≤ ηaR ≤ ηaA，Z ≤ (1+ηa/K)A；(ii) 同一并集上两条误差带耦合：(Z−A)/η_u ≤ X ≤ Y ≤ η_o(Z−B)
  推 B ≤ (1−1/η)Z + A/η；(iii) 消去 Z 得 B ≤ (1+(η−1)a/K)A。
- 状态：四项非负 slack 恒等式 (7)（(1+(η−1)a/K)A−B = E+γH+(γ/K)J+(γηa/K)T）、E 的三项分解 (8)、
  单次交换四项分解 (9)：[VERIFIED-SYMBOLIC，results/J5_hardcore/J5_hardcore_oracles.py，14 项之内]；
  52 个独立全格点算法侧 LP、24 个 modular 对手实例 37,056 个 all-pairs 增量 [VERIFIED-LP 同脚本]；
  一般集合上的交换、望远镜与 minimax 量词装配 [HAND-PROOF-UNREVIEWED，来源 J5 套 A]。
  **达到方向由 [CONJECTURE] 升级为该标签（用户指令，J5H2）；M3.1 的 FAILED 记录由此关闭。**
- 量词五条（J5 §5，写进附录）：下界量词是"存在算法对所有实例"（非任意算法）；|S|=K 是穷举自身的
  输出规范，|S|<K 的算法把输出补足即可被上界覆盖；无需最小重叠；需要全部交换比较（one-swap
  local optimality 不够）；穷举非多项式查询，不改变有限预算 hardness 的适用范围。
- 随机版（单列）：n ≥ 2K 的上界 (1−K/n)/η+K/n 保留（逐算法固定实例量词）。**确定性值不是随机值**：
  n=3, K=2, η=3 时确定性值 1/2，而均匀随机二元集对任何单调 submodular 目标 E ≥ (2/3)·OPT
  （一般：均匀 K-子集 E ≥ (K/n)f(N)，随机排列非增期望边际求和 [HAND-PROOF-UNREVIEWED，来源 J5]）。
  随机 minimax 仍 [OPEN]。
- 乘积依赖禁令缩小（J5 §五）：新对手构造对**任意拆分**实际误差恰取到，故本定理两侧对任意拆分成立、
  值只依赖乘积；原"只对对称族"的限制解除（一般 comparison-based 之外的逐算法不变性仍只有
  lem:scaling 的类意义）。
- 禁止声称："1/η 是多项式算法的界"（它是信息论的）；
  "η ≥ K 时 greedy、穷举与任何算法相同"（只能写 greedy 达到不限查询的确定性最优保证）；
  随机上界 (1−K/n)/η+K/n 是有限 n 下的精确最优（它只是上界）。
- 构造的误差恰为 (η_u,η_o)：J4 精确穷举 253,220 个 all-pairs 增益 [VERIFIED-EXHAUSTIVE]。
- 副产品（J4）：1 ≤ η < K 时穷举的最坏保证 1/η 严格优于 greedy 的 ρ_K（ρ_K ≤ V_1 < V_0），
  差 ≥ (K−η)/(Kηk_1)；K=3：η=1: 19/27 vs 1；1.5: 9/16 vs 2/3；2: 7/15 vs 1/2；3: 相等。比较的是最坏保证。
- 历史（H-E，2026-09-07，被统一陈述覆盖）：对称族天花板 C(n,K,η)=K/(m0+(K−m0)η)、m0=max(0,2K−n)
  与 C*_{n,K} 一致；[VERIFIED-LP 84 点，results/H_E_ceiling_small_n.py] + witness Fraction 精确验证。
  当时算法侧一般证明 FAILED（卡在 f(Ŝ∩O*) 下界）；J5 的交换 + 并集耦合路线绕开该卡点。
- 历史（M3.1，2026-09-12 早）：J5 文件未送达时的本地重构 FAILED（results/M3_ceiling_attempt.md）；
  本晚 J5 原文到齐后按 J5H2 转录，该记录关闭。
- 禁止声称（M4 追加）：随机算法**逐种子**满足确定性界（随机版只是期望陈述，量词是逐算法固定实例）。
- 禁止声称（J5H2 更新）：把达到方向说成机器证明（装配是 [HAND-PROOF-UNREVIEWED，来源 J5]，
  恒等式与有限 LP 才是 oracle）；C* 当 randomized 值（n=3,K=2,η=3 反例，随机 minimax [OPEN]）；
  由 one-swap local optimality 调用该证明（需要全部交换比较）；把穷举当多项式查询算法或据此
  改动 hardness 的适用范围。

## T9 cor:limit — 渐近（J5H5 首行统一：单调性已证，历史移卡末）
- 陈述（最终状态）：固定 η，L_K、ρ_K、U_K → 1−e^{−1/η}；ρ_K 关于 K **非增**，K ≤ ⌊η⌋ 平台 1/η，
  K ≥ ⌊η⌋ 起严格递减（[VERIFIED-SYMBOLIC，conditional on thm:exact]，证明已迁入 app:asymptotics，
  J5H5）；一阶展开 ρ_K = 1−e^{−1/η} + c(η)/K + O_η(1/K²)，c(η) = e^{−1/η}(2η−1)/(2η²)（不随
  ⌊η⌋ 分段；c_L = e^{−1/η}/(2η²)、c_U = c，同样已迁入附录）。
- 状态：极限由 L_K ≤ ρ_K ≤ U_K 与两侧极限；展开与单调性证书 [VERIFIED-SYMBOLIC conditional on T6，
  results/H_B_asymptotic.py，J5 hardcore oracle 独立重验（84 项分子、165 项分母全非负，常数 14/48）]；
  余项的 Taylor 装配与导数论证到离散差分的装配 [HAND-PROOF-UNREVIEWED]。
- 渐近展开（H-B）：固定 η ≥ 1，ρ_K(η)=1−e^{−1/η}+c(η)/K+O(1/K²)，c(η)=e^{−1/η}(2η−1)/(2η²)。
  c 不随 ⌊η⌋ 分段（1/K 项上 m=⌊η⌋ 贡献相消）；分段的是 1/K² 系数
  d(η,m)=e^{−1/η}[24η³(1−m)+12η²(m²+m−3)+20η−3]/(24η⁴)。c 在 η*=1+1/√2 处取最大 0.230579。
  状态：[VERIFIED-SYMBOLIC]（sympy series，conditional on T6）；Richardson（K=50..800）与闭式差
  ≤1.3e−12。更正：旧值 c(3)≈0.197 是 K=50 的原始值，极限为 0.199036；c(1.5)、c(2) 复现。
- 单调性（H-B）：ρ_K 关于 K 非增；K ≤ ⌊η⌋ 平台 1/η，K ≥ ⌊η⌋ 起严格递减，从上方收敛。
  证明：d ln P/dK 恒等式 + 一行 −ln 逐项尾界 + 坐标变换后非负系数证书（分子 84 项全非负）。
  状态：[VERIFIED-SYMBOLIC，conditional on T6]，唯一手写步骤是尾界；精确有理差分 K=2..400 ×
  7 个 η 共 2,793 个符号 0 负。cor:limit 的单调子句按此恢复（ρ_K 非增，K ≥ ⌊η⌋ 起严格）。
- 副产品（H-B）：c_L=e^{−1/η}/(2η²)，ρ_K−L_K=e^{−1/η}(η−1)/η²·(1/K)+O(1/K²)；c_U=c，解释
  U_K−ρ_K=O(1/K²)。均 [VERIFIED-SYMBOLIC]。
- 禁止声称（H-B）：O(1/K²) 对 η 一致或带显式常数（[CONJECTURE]）；c 分段（不是，分段在 1/K²）；
  由单调推凸凹（未查）；把本卡结论当对 ρ_K=min_j V_j 的独立确认（全部 conditional on T6）。
- 历史（J5H5 归档）：G2 曾因无证明删去 cor:limit 的 ρ_K 单调子句并留 [OPEN]；第六晚 H-B 闭合证明后
  正文子句恢复但附录未同步、卡首行未更新（J5 审计 §四 指出）；本晚证明迁入 app:asymptotics，
  首行按最终状态统一。旧值更正记录保留：c(3)≈0.197 是 K=50 原始值，极限 0.199036。

## T10 thm:hardness — 有界查询 hardness（K4 后按 J2 校准）
- 陈述：c ≥ 0 实数，τ=⌈c⌉+1，K>τ，n ≥ 4K^{c+2}，η>1 且 η ≥ (K−1)/(K−τ)，θ̄=(η(K−τ)+1)/K。任意确定性算法，≤n^c 次、每次集合大小 ≤K 的 f̃ 查询、输出 ≤K 元素，存在实际误差恰为 η 的实例使 f(T)/f(O*) ≤ H_{K,τ}(η)=1−(1−1/(η(K−τ)+1))^K=L_K(θ̄)。随机版加 ε_n=K/n+K^{2τ+2}/((τ+1)! n^{τ+1−c})。
- 状态：边表与校准 [VERIFIED-SYMBOLIC]（J2 264 实例 + 我方复核）；transcript/并集界/两次平均 [HAND-PROOF-UNREVIEWED]。
- 副产品：τ=1 时 H_{K,1}=U_K，故 L_K ≤ ρ_K ≤ U_K=H_{K,1}。
- 禁止声称："error exactly η" 用旧 Φ 校准；查询大小不限（那是 F3 版本）；任意多项式次数的类最优（见 T11）；
  "non-trivial" 而不说明是渐近匹配（有限参数下 H 可大于 1/η，如 η=2,c=2,K=8 时 H≈0.533）；
  随机版 K→∞ 时 ε_n 自动消失（需 n ≥ 4K^{c+3} 之类）；把查询大小限制等同于多项式时间。
- 第九晚注（P0/P1）：查询大小 ≤ K 的条件对证明路线是实质性的。把 O-无关要求换成任意大小查询
  真正需要的 size-based typical band 后，(x,y) 对称（含分块推广）count-grid 构造的 LP 在
  Q=n^c、c ≥ 1.5 时最优值恰塌缩到 1/η（最优解为 prop:necessity 的 modular 实例；P0 216 个 LP、
  P1 用"任何合法区域必含"的必要区域 60 点，塌缩链有 11 行目标割证书，results/P0_band_lp_iis.json），
  即该族在任意大小查询下证不出任何强于 thm:ceiling 的常数。[VERIFIED-LP 有限参数]
- 禁止声称（M4 追加）：小查询 hardness（本定理）已解决 unrestricted-size 查询类的最优常数
  （rem:hardness-leak：族在大查询下泄露；unrestricted optimum 两个方向都 [OPEN]，见 P3）。
- 禁止声称（第九晚追加）：本定理的族或其分块推广可用于任意大小查询的 hardness；据 P0/P1 断言
  任意大小查询、多项式次查询类的最优常数是 1/η 或 1−e^{−1/η}（两个方向都 [OPEN]，被排除的只是
  这条构造路线）。

## T10b cor:greedybudget — greedy 同预算类的天花板（L1 新增；M2 改名与量词）
- 标题（M2.3）：改为 "An upper bound within the greedy query budget"（原 "Optimality ..." 高估内容）。
- n 量词（M2.3，J5 §11 反例经 M0 有理复算确认）：天花板与夹逼区间**只在 n ≥ 4K⁵ 的前提下**陈述；
  相关猜想与 "not aware" 句一律限定 n ≥ 4K⁵（或 inf over n）。反例：n=4, K=2, η=3/2 时
  "查询全部 6 个 pair 取 argmax" 属于 𝒜_lin（6 ≤ nK=8）且精确最坏值 2/3 = 1/η > ρ_2 = 3/5，
  且 2/3 > U_2(3/2) = 16/25 = 0.64，故小 n 处上端也失效（results/M0_counterexamples.py §2）。
- 联合极限（M2.6）：ε_n = K²/n + K⁵/(2n) → 0 需 n/K⁵ → ∞（单独 K → ∞ 不够）；
  min{U_K, 1/η} 合并只对确定性（随机版未与 1/η 合并，原禁止项保持）。
- 禁止声称（M4 追加）：greedy 在**所有 n** 上同预算最优（n=4 反例；一切最优性猜想带 n ≥ 4K⁵）。
- η=1 情形（M3.4）：corollary 延伸到 η=1：θ̄=1 时族退化为 F ≡ G（恒等式 a^τ(K−y)/(K−τ) = 1−y/K
  在 τ=1、a=1−1/K 时成立，[VERIFIED-SYMBOLIC，results/M3_checks.py]），误差恰为 1，计数不变，
  界为 U_K(1) = L_K(1) = ρ_K(1)（V_{K−1}(1) = L_K(1) 同脚本验证）；故 η=1、n ≥ 4K⁵ 时 greedy
  在 𝒜_lin 内恰最优。
- K=1 情形（M3.4，单列）：thm:exact 与本卡的族都要求 K ≥ 2；K=1 时 greedy = argmax f̃ 单元素，
  三行链 f(e) ≥ f̃(e)/η_o ≥ f̃(o)/η_o ≥ f(o)/η 给保证 1/η [HAND-PROOF-UNREVIEWED 三行]，
  与 thm:ceiling（n ≥ 2）合并得 ρ_1 = 1/η 且 greedy 在**全部**确定性算法内恰最优（不只 𝒜_lin）；
  U_1 = 1 空洞。
- 陈述：K ≥ 2，η > 1，n ≥ 4K⁵。𝒜_lin = 确定性算法类：至多 nK 次 f̃ 查询、每次查询集合大小 ≤ K、输出 ≤ K 元素
  （predictive greedy 用 ≤ Kn−K(K−1)/2 次查询，属于该类）。对任意 A ∈ 𝒜_lin 存在实际误差恰为 η 的实例
  （f 单调 submodular）使 f(T)/f(O*) ≤ U_K(η) = H_{K,1}(η) = 1−(1−1/(η(K−1)+1))^K；与 thm:ceiling 合并得
  worst-case ratio ≤ min{U_K(η), 1/η}。随机版量词：对任意随机算法存在实例（实际误差恰 η）使
  E_seed[f(T)/f(O*)] ≤ U_K(η) + ε_n，ε_n = K²/n + K⁵/(2n)。
- 证明结构：thm:hardness 的族取 τ=1（η ≥ (K−1)/(K−τ) = 1 自动满足，θ̄ = (η(K−1)+1)/K ≥ 1），预算从 n^c 换为
  Q = nK 重做计数：单查询 P(|S∩O| ≥ 2) ≤ C(K,2)·K(K−1)/(n(n−1)) ≤ C(K,2)(K/n)²；对 Q = nK 并集 ≤ K⁵/(2n)；
  输出相交 ≤ K²/n；n ≥ 4K⁵ 时总失败 ≤ 1/8 + 1/32 = 5/32 < 1/2。
- 状态：计数不等式链 [VERIFIED-SYMBOLIC，results/L1_table.py]；canonical transcript 归纳与两次平均沿
  app:hardness 原样 [HAND-PROOF-UNREVIEWED]，按用户指令不升级。
- Gap：U_K − ρ_K = c'(η)/K² + O(1/K³)，c'(η) = e^{−1/η}·⌊η⌋(2η−⌊η⌋−1)/(2η²)；c' 在整数 η 处两支相等
  （值 e^{−1/η}(η−1)/(2η)），η > 1 时 c' > 0。状态：[VERIFIED-SYMBOLIC conditional on thm:exact 与 T9 的
  H-B 展开，results/L1_table.py]；数值 K ≤ 400 收敛检查同脚本。U_K − ρ_K ≥ 0 由 ρ_K ≤ V_{K−1} < U_K
  （T6 副产品，η > 1 严格）。
- η ≥ K：ρ_K = 1/η 且 1/η ≤ U_K（由 ρ_K ≤ U_K），故 min{U_K,1/η} = 1/η = ρ_K，greedy 恰达该类天花板。
- 禁止声称：有限 K、1 < η < K 时 greedy 在 𝒜_lin 内最优（[OPEN]，同 T11 卡；只知道改进空间 ≤ U_K−ρ_K = O(1/K²)）；
  ε_n 中间项 K²/n 当成装配的产出（装配实际给 K/n，K²/n 是按 TASKS7 规格取的保守上界）；把 n ≥ 4K⁵ 说成必要
  （只是使总失败 < 1/2 的显式充分条件；同一算术覆盖任意 Q ≤ n²/(4K⁴)，未单列陈述）；把查询预算等同多项式时间
  （查询模型条件，同 T10）；随机版与 1/η 合并（thm:ceiling 随机版是 (1−K/n)/η+K/n，未合并陈述）；
  在 η^sel 轴上引用本卡（全局 η 的陈述）。

## T11 rem:hardness-pins — 查询类最优性（K5 后；M2 证据等级与候选总结校正）
- 证据等级（M2.1）：本卡（含 H-F、L2、L2R、P2 各行）出现的一切"精确分数/精确值"，其证据等级统一读作
  [VERIFIED-LP，有限参数，**浮点求解** + 有理化 + witness 复核]；没有逐格的有理对偶证书，
  浮点分支穷尽不等于精确有理最优。要升级需逐格补有理对偶或向外舍入下界（未做）。
- 候选总结（M2.2 统一口径）：PE_1 预算 O(n²K)、**不属** 𝒜_lin，在 n=2K 优于 greedy、n ≥ 7 劣于；
  top-(K+1) shortlist 属 𝒜_lin；greedy+swap 预算 2nK−K²、tie 为对抗选择、不属 Q=nK 类；
  max(fwd,rev)（P2）不属 𝒜_lin。任何"若干候选均不超过 greedy"式总结必须逐候选带上述预算/类别
  归属与 n 范围，且不得忽略 n=2K 处的超越（PE_1、max(fwd,rev)）与 n=4 处 𝒜_lin 内的穷举超越
  （M0 §2 反例）。
- 陈述：greedy 用 ≤ Kn−K(K−1)/2 次查询；当 nK ≤ n^c（如整数 c ≥ 2, K ≤ n）时，该查询类的渐近最优值为 1−e^{−1/η}，有限 K 间隙 O((c+1)/K)。
- 禁止声称：c=0,1 的类（精确穷举反例：单查询算法可被逼到 0）；"O(c/K)"；有限 K 的同预算最优性
  （[OPEN]：只排除渐近常数的统一改进，不排除有限 K 或低阶项的改进）。
- PE_R 数值结论（H-F，K=3, R=1；J5H3 升级与收缩）：
  n=6=2K 时 PE_1 严格优于 greedy（19/29、1/2、2/5 vs 9/16、7/15、7/18，后两值恰为 1/η）；
  n=7,8 时 η∈{2,2.5} 处 PE_1 严格劣于 greedy，η=1.5 仍优（16/27）。
  **(K,η)=(3,2)、n=7 的关键格子现有精确有理穷举证书**（J5 hardcore：七元素实例由两张 3×4 表重建，
  128 子集、448 条边（0 ≤ d/2 ≤ d̃ ≤ d）、672 个 submodularity 方块 Fraction 全核，七条起点轨迹表，
  PE_1 = 4/9 < 7/15 = ρ_3(2) < 5/9 = 该实例上 greedy 最坏值；[VERIFIED-LP，精确有理穷举，
  results/J5_hardcore/J5_hardcore_oracles.py + J5_variant_certificates.md §4]；正文引用以此格为准）。
  补零扩展到一切 n ≥ 7 [HAND-PROOF-UNREVIEWED，来源 J5]（新增 singleton 起点用"先选原 argmax b、
  走其完成轨迹前缀、预测单调性封顶"的论证，n=8,9 已精确穷举复核；PE₁ 的扩展与单条 greedy 的
  restriction 论证不可混用）。
  η=1 精确复现 NWF 1978（5/6 与 19/27）。n=6 闭式 min{1/η,(9η−4)/(2(3η²+η−1))} [CONJECTURE]，
  在 n=7 被证伪。解读：枚举起点的收益可被"按 f̃ 选终点"的损失抵消（不声称必然损失满 η 因子）；
  这是 greedy 有限 K 最优性的正面证据（R=1,K=3,n≤8），非证明。
- 撤回（J5H3）："η ≥ 1.75 亦然"的连续外推（离散扫描不支持连续断言；只保留已验证网格点
  η ∈ {1.75, 2, 2.5} 等逐点结论，H_F md 已加更正注记）；"n=6 放不下三组是反转的唯一原因"
  （机制解释非唯一性证明）；"没有证据说它有下确界"（有界非空必有 inf；补零扩展下最坏比对 n 非增）。
- 引用规范（J5H3）：PE 的出处写 Nemhauser, Wolsey, Fisher (1978), Section 7, Theorem 7.1
  （bib 键 nemhauser1978analysis，三作者已核），不写易混淆的 "NW 1978"；该定理给的是保证，
  不据数值吻合声称文献证明了 PE₁ 的精确最坏值。
- 禁止声称（H-F）：PE_1 一致优于（或一致劣于）greedy；n=6/7/8 的值互相覆盖或覆盖 n≥9
  （inf over n [OPEN]）；R≥2、K≥4、all-pairs band 的任何结论（未算）。
- 线性预算候选数值结论（L2，K∈{2,3}，adversarial tie，single-element band）
  [VERIFIED-LP：36/40 配置分支枚举跑完 + 每配置 instance-rebuild certificate；
   results/L2_linear_candidates.py，五道闸门含冻结 worst_case_lp 复现 ρ_K 20/20]：
  两个同量级预算的确定性候选都没有超过 ρ_K。
  (a) top-(K+1) shortlist（先按单元素 f̃ 取前 K+1 个，再在其 K-子集上按 f̃ 取 argmax；
      查询 n+K+1 次、size ≤ K，落在 𝒜_lin 内）的精确最坏值在全部 20 个配置上远低于 ρ_K；
      数值与 1/((K−1)η+1)（n=2K）、1/(Kη)（n ≥ 2K+1，验到 n=8）逐位相符
      [闭式本身 CONJECTURE，24 个点命中，无证明]。
  (b) predictive greedy + 单轮 swap pass（查询 ≤ nK+K(n−K) = 2nK−K² < 2nK，size ≤ K）
      在 n=2K 上恰等于 ρ_K（K=2 与 K=3 各四个 η，八格全中），
      在 K=2、n ∈ {5,6} 上严格劣于 ρ_2 并随 n 下降（n=6, η=2：2/5 < 1/2）。
      K=3、n=7（L2R 2026-09-11 重跑定案，results/L2R_finish_k3n7.py，per-O 并行穷尽
      23,660/23,660 叶 × 2 格，Gate R 改编闸门 + 五道原闸门重跑 exit 0）：η=1.25 精确值
      31/51 < 92/147、η=1.5 精确值 37/69 < 9/16（差 15/833、29/1104），witness CONSISTENT，
      **严格劣于 ρ_3**；η ∈ {2,2.5} 仍是"劣于"结论（上界 4/9、16/45 在 ρ_3 之下，精确值未算）。
      n=7 四个 η 全部严格劣于 ρ_3，与 K=2 的 n>2K 模式一致；本条已无 [OPEN] 格。
  解读：与 H-F 的 PE_1 不同，n=2K 处的"小 n 超越"在这两个线性预算候选上没有出现；
  swap 用 f̃ 判断改进，误差带允许 f̃ 打平而 f 下降，故单轮 swap pass 在最坏意义下不是净收益。
  这是 greedy 有限 K 同预算最优性的又一条正面证据（K≤3、n≤7），非证明。
- 大集合查询算法数值结论（P2，第九晚，K=3，n∈{6,7}，η∈{1.5,2,2.5}，adversarial tie）
  [VERIFIED-LP：(a)(b) 12/12 配置分支枚举穷尽 + 16/16 instance-rebuild witness；七道闸门含冻结
  worst_case_lp 复现 ρ_3；results/P2_large_query_algorithms.py]：
  (a) 反向 greedy（stingy，查询大小到 n−1）全线远劣于 ρ_3 且随 n 衰减，闭式猜想 K/((n−K−1)η+K)
      （20 点吻合 [CONJECTURE]，η=1 给 K/(n−1)）；
  (b) max(前向, 反向 greedy)（按 f̃ 取优）在 n=2K=6 的三个 η 上**全部严格优于 ρ_3**
      （182/311 > 9/16、21/44 > 7/15、43/108 > 7/18；穷尽 + 全枚举复核 + Fraction 精确 witness +
      第二求解器，【最需人类判断】），n=7 三个 η 全部严格劣于 ρ_3，全程低于 1/η；
      与 H-F 的 PE_1、L2 的候选 B 同为 n=2K 现象。
  (c) 双向评分（几何平均）：比较是 LP 变量二次约束，精确值 [FAILED]；库内实例精确模拟的上界
      全部严格低于 ρ_3。
- 禁止声称（M4 追加）："c < 2 的类一律不含 greedy"（nK ≤ n^c ⟺ c ≥ 1 + log K/log n，大 n 时
  c 略大于 1 即可含 greedy；c=0 反例只说明 c=0）；PE_1 属于 Q=nK 的类（其预算 O(n²K)）；
  浮点分支穷尽等于精确有理最优（M2.1 证据等级条）；用**高比值实例**证明 worst-case 下界
  （worst case 是 min，高比值实例什么都不证明；低比值实例给的是上界）。
- 禁止声称（P2）：(b) 的 n=2K 超越延伸到 n ≥ 7（已被精确值证伪）或任何 n 无关陈述；(b) 超越 1/η
  （未发生，三值均低于 1/η）；(b) 属于 𝒜_lin（反向 pass 查询大小到 n−1，出了 T10b 的类，
  也因此与 cor:greedybudget 不冲突）；(c) 的上界当精确值；stingy 闭式当定理。
- 禁止声称（L2）：这两个候选覆盖 𝒜_lin（只是两个具体算法）；n≤7 的值覆盖更大 n
  （inf over n [OPEN]）；候选 A 的闭式对 n>8、K>3 或 m≠K+1 成立；候选 B 在 n=2K 等于 ρ_K
  推广到 n>2K（K=2、n≥5 已证伪）、或对 swap 的另一读法成立（每 slot 至多换一次时
  K=3,n=6 已略低于 ρ_3）；候选 B 落在 Q=nK 预算内（预算 2nK−K²，套 T10b 的算术只需
  Q ≤ n²/(4K⁴)，n ≥ 8K⁵ 即可，未单列陈述）；"swap 有害"读成逐实例（比较的是最坏保证）；
  把 K=3,n=7 在 η=1.25/1.5 的旧 incumbent（0.697/0.591）读成"候选 B 超过 ρ_3"
  （L2R 穷尽后证实那只是未穷尽搜索的上界，真值 31/51、37/69 在 ρ_3 之下）；
  把 η ∈ {2,2.5} 的 4/9、16/45 当成 n=7 的精确值（只是带 certificate 的上界，足以定"劣于"）。

## T12 F3 任意大小查询 hardness（附录：构造方向与有限证据，不作 theorem）
- 内容：任意大小查询、预算 Q ≤ n²/(2K²(t*+K)²) 的确定性算法在已检查参数上不超过 greedy 的渐近值。
- 状态：坏实例的单调、submodular、归一化只有有限参数穷举 [VERIFIED-LP 有限]；j、m* 一般闭式无证明；
  随机版另用未核查的构造不等式；装配 [HAND-PROOF-UNREVIEWED]。J4 裁定：不能以已完成定理计入。
- 第九晚证据（P1）：F3 的 O-无关区域 {y ≤ τ} ∪ {x > t*} 不被 N∖{e} 攻击打到（正文显式族则被打穿，
  两类 (n−1)-集合的 G 值差 a^{n−K+τ}/(K−τ) > 0）[VERIFIED-LP]。预算指数扫描：c=0.5 时 LP 值 ≈ W_K(η)、
  c ≥ 1.5 时塌缩到 1/η（8/8 组），故 Q 里的常数因子 1/(2K²(t*+K)²) 对该族是**必需的**，
  Q = n² 字面预算对任何 size-based band 的 count-grid 构造不可达。[VERIFIED-LP 有限参数，
  results/P1_asymmetric_families.md §1]
- 禁止声称：作为 theorem；任意多项式预算；n^{2−o(1)} 而不限制 K、η 的增长；"指数 2 内在上限"超出已检查的 48 组参数。
- 禁止声称（第九晚追加）：去掉 Q 的常数因子或把预算写成裸 n²；c ≥ 1.5 的任何 hardness 经由该族或其
  分块推广（P0/P1 塌缩证书）。

## T13 附录：pair greedy（R12）
- 陈述：K=4、all-pairs 误差下 pair greedy 精确最坏值 = ρ_2(η)（η∈{1.5,2,3}）。一般 K [CONJECTURE]。
- 禁止声称："exactly halves K for all K"。

## T14 附录：加性混合模型（N6；未进正文，只在 results/）
- 陈述（M2.8 范围收缩）：**单元素版** d/η_u−ε ≤ d̃ ≤ η_o d+ε ⇒ F^PG ≥ L_K(η)(OPT−2Kη_u ε)；
  "ε 项紧"**只限已验证的 N6 LP 参数点**，不作一般紧性声称。
- 禁止声称：真实 surrogate 满足该模型（量化尺度 ε 下 88% 数据行不满足）；ε 项对一般参数紧；
  单元素与 all-pairs 版本混写（N6 只做了单元素版）。

## T15 实验中的理论量（K2 后）
- ratio 分母 greedy-on-f 是 OPT 的下估 ⇒ ratio 是真实比的上估（方向勿反）。
- E2（coverage，模型内）：新定义下 16 个有害零步 run 的 η^sel=∞；其余 run 有 per-run certificate。
- E1/E3（非单调目标）：selection diagnostic + 模型违反记录；L_K 列为 reference 非 certificate。
- E4：19 个构造实例贴理论值 ≤1e−16；只在全局 η 轴与 ρ_K 比较。
- 禁止声称（M4 追加）：本文证明了 learned predictors 满足全局误差假设（实验只测有限前缀的
  diagnostic/certificate，E1/E3 且出模型）。
- 禁止声称："all real tasks lie above both guarantee curves"；"structurally zero"（E2 零对正 pair 30,416 条）。

---
维护规则：任何定理陈述改动，先改本文件对应卡，再改 .tex；卡上的状态标签与 results/ 脚本一一对应。
