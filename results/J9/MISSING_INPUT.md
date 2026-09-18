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
