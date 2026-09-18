# J9（GPT 2026-09-18 任意大小查询确定性 matching 证明）输入缺失记录

- TASKS11 Q11 引用 results/J9/j9_proof.md；指令到达时该文件在仓库全部历史、mirror、uploads 与全盘均不存在。
- 公式 (9)(10)(11)(14)(15)、序列 p_x/u_x/r_x/g_x 的定义、实例 F_{T,O}/G_O、n ≥ ⌈4cK⁵(K+2)²⌉ 的计数链均依赖原文，
  故 C2、C3、C4、D、E 与 B 的比对无法执行；不建 T10e。
- 已做（不依赖原文）：C1 的两条内联不等式 [VERIFIED-SYMBOLIC]（results/V11/oracle/j9_fragments.py，exit 0，13 项：
  e^{K−2+u} > 1+Au 于 K ≥ 3、1 < A ≤ K(K−1)、u ≥ 0 经驻点与端点分析；11/6 > log 6 经 e^{11/6} 的 12 项
  级数下界 6.2547 > 6）；盲审路线二（只看重构陈述 results/V11/inputs/statement_j9.md 与 Definition 1）
  由 Opus 子代理独立推导，产出 results/V11/route2/j9.md，待原文到齐后比对。
- 文件送达后：按 Q11 清单补 C2–C4、D、E 与比对，全过再建 T10e。

## 盲审路线二结果（2026-09-18，Opus 子代理，只看重构陈述 + Definition 1）

- 状态 PARTIAL：一般 K 的闭式构造未闭合；产出 results/V11/route2/j9.md（513 行）与同目录脚本。
- 机制：surrogate G_O 只在 deviating cells（|S| ≤ m 且 |S∩O| ≥ 2）上偏离 size-only 基线 γ(|S|)，
  true f = F_{T,O} 同时依赖算法固定输出 T 与 O（band 只约束该 pair，故算法不可见）；两个泄漏条件
  缺一不可；union bound 取 m = 2K(K+2) 得充分条件 n ≥ 4cK⁵(K+2)²，与陈述阈值逐字吻合。
- 新推导的三条必要条件 (C1)(C2)(C3)（由 global band 的 level flatness 得），取等解出轨迹
  d_t = q^t/k1（t<j）、q^j/(Kη)（t≥j），f(T) = V_j；η ≥ K 支 size-only 即精确 1/η；1 < η < K 支
  deviating cells 必需。
- 已验证：有限可行性问题 (P_{K,η}) 最优值恰 = ρ_K，K=2..7、11 个 η [VERIFIED-LP]；K=2,3,4 完整
  实例精确有理数（K=3, η=3/2: f(T)=9/16）[VERIFIED-SYMBOLIC]，capping extension 铺到任意 n
  （精确验证到 n=44/46/33）；split 无关；T-independent 纯 count-grid 族严格正 excess
  （K=2: 0.61 vs 0.60；K=3: +1.1e-3；K=4: +1.3e-4）。
- 卡点：一般 K 闭式（coverage ansatz 的凹凸冲突；ordered 构造违反 level flatness；乘积型被 LP 否证）；
  (U2) 轨迹 LP 下界方向、(U3) m* = 3(K−1)、(U6) excess 衰减率只有数值支持；(U4) 若补全读成对抗性则失效。
- 能确立的最强陈述：条件定理（在 (P_{K,η}) 可解的 (K,η) 上成立；K ≤ 7 已由 LP 确认）。
- 处理：不进正文、不建 T10e；待 j9_proof.md 到达后逐步比对。

## j9_check.py 送达（2026-09-18，同日；证明文件仍缺）

- 送达物：GPT 的校验脚本 → results/J9/j9_check.py（原样落库）。原样运行 exit 0（results/J9/j9_check_run.log）：
  37 项 sympy 恒等式中 **3 项打印 False**（(22) p_{j−1} = Kδ/(K−1)、(23) u_{j−1} = δ、row x<j 的 η u_{x−1} = q^x/K）；
  参数引理只有浮点网格（脚本自注 "sanity, not proof"，其中 "eps<eta−1" 的最小值显示 0.0）；K=3, η=3/2
  例子给 eps = 1/26、γ = 6/13、δ = 1/8、F̄(T) = 59/104、F(T) = ρ_3 = 9/16。
- 我方独立复核 results/J9/j9_own_checks.py（exit 0，54/54，results/J9/j9_own_checks.log）：
  - S：全部 37 项恒等式改写成有理函数恒等式（q^j、q^x、ν^t、ν^m 取自由符号）由 sp.cancel 判定，**全部成立**；
    脚本打印 False 的 3 项是 sympy 对符号指数 q^{K−a−1} 与 q^{K−a} 不合并的失败，不是恒等式错误
    （手算：p_{j−1} = q^{j−1}(1−q) = q^{j−1}/k1 = Kδ/(K−1)）。[VERIFIED-SYMBOLIC]
  - P：参数引理精确有理化，K = 2..12 × 15 个有理 η（1 + (K−1)i/16）+ 指令点 6/5、3/2、5/2（< K 时），
    共 188 点：m > θ、0 < eps < η−1（最小 1/256 于 K=2, η=17/16，浮点网格的 0.0 是 (η−1)² 级的舍入）、
    eps < 1/(K−1)、0 ≤ γ < 1、e^{K−2+u} > 1 + Au（e 用精确级数下界）、尾段符号 a+t+eps−K eps ν^t ≥ 0
    （t = 0..m）、K/(K−1) ≥ 1+eps、φ(m) > 0 ≥ φ(m+1) 全过；m 取 max{z ≥ 0 : φ(z) > 0}（φ 单峰、φ(0) = θ ≥ 0，
    与脚本二分根的 floor 一致；网格上无整数根并列）。[VERIFIED-EXHAUSTIVE 有理格点]
  - C2（指令项）：(14)(15) 三段序列 r_x、h_x 在 K = 2..6 × 同一 η 网格共 83 点上逐 x 精确检查：r, h ≥ 0 且
    非增、p_x ≥ u_x ≥ 0、K g_x ≥ r_x（x ≤ M）、h_M = 0、r_M = γδ、r_{M+1} = 0、相位拼接、
    F̄(K,0) = ρ_K + eps·δ；0 违反。[VERIFIED-EXHAUSTIVE 有理格点]
- 仍不能做（需要原文）：F_{T,O} 与 G_O 的集合函数定义（脚本只有 count-grid 序列与 F̄，"F(T) = ρ_K" 的
  T 相关修正未给出），故 C3 完整实例穷举、C4 不可区分性、D 对抗算法与 500 随机策略、E 量词表、
  与盲审路线二的减量步骤比对、T10e 建卡全部待 j9_proof.md。
- 与盲审路线二的可见差异（待原文后正式比对）：脚本的截断指标 m = ⌊τ⌋（φ(t) = Kη−a−t−ην^{−t} 的正根，
  K=3, η=3/2 时 m=3）与 eps = (m−θ)/(ν^m−1)；盲审用 m* = 3(K−1)（同点 m*=6）与 LP 求解的 deviating cells，
  两者同以 "T 相关的 true f" 为机制。
