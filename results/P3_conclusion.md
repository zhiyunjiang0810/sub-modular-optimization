# P3：第九晚汇总（TASKS9，任意大小查询下的最优常数）

今晚的问题：**任意大小查询、多项式次查询的算法类，其在误差 η 下的最优常数是否仍为 1−e^{−1/η}？**

一句话答案：**两个方向都仍然 [OPEN]，但边界被三条路线同时收紧了。** TASKS9 预设的三选一结局
实际落在两支上：P0/P1 给出"why it is hard"的 impossibility 观察（排除一整条构造路线，不排除定理），
P2 发现一个在 n=2K 严格超过 ρ_K 的多项式查询数大集合算法（【最需人类判断】，n=7 即回落）。

---

## 1. 三条路线的结论

### P0（band 定义与可行性 LP）：不是不可行，是退化

预期的 IIS 不可行没有出现。把任意大小查询真正需要的 O-无关 band（TASKS9 proxy 与精确
hypergeometric-tail 两版）写进 (x,y) 对称构造的 LP 后，**216 个 LP 全部可行**，但 spec 变体的
最优值在 106/108 个点上**精确等于 1/η**，最优解就是 prop:necessity 的 modular 实例
（F = x/(ηK) + y/K、G = (x+y)/(ηK)，零泄露）。带目标割的最小 11 行证书给出三步链：
沿 x=0 的 band 下界累加得 G(O) ≥ 1/η、沿 y=0 的 band 上界累加得 G(T) ≤ F(K,0)、
两端被同一个 Ĝ(K) 接上。平顶（capped，F ≤ 1 处处）变体在 proxy band 下退到 1.0（空陈述）。
[VERIFIED-LP 有限参数]。J5 与 (n−2) 攻击 108/108 通过，但那是 band 定义使然，代价即退化。

### P1（非对称构造族）：FAILED，三件产物

(1) 塌缩是对**整个 size-based O-free 区域族**的下界：用"任何合法区域必须包含"的必要区域
typmin(s) 复现同一塌缩（60 点）；预算指数扫描显示 c=0.5 时值 ≈ W_K(η)（F3/anysize 的量级），
**c ≥ 1.5 时 8/8 组恰为 1/η**。
(2) 分块隐藏在 56/56 个配置上与 (x,y) 族逐点同值，块结构一无所获；"S ⊇ O 处正 x-边际"与
"非平凡常数"在 count-grid 上不共存（28/28 个非平凡解的顶部 x-边际为零）。
(3) 非饱和修正族的两条闭式判据：ψ≡1 可行 ⟺ η·a^{K−1} ≥ 1；ψ = 1[y=K] 对一切 K ≥ 3、η > 1
不可行 [VERIFIED-SYMBOLIC]。副产品：独立复现 N4 的 W_K 闭式（4 点 7 位）；确认正文显式族
被 N∖{e} 攻击打穿而 F3 区域不被打到；F3 预算里的常数因子是必需的（T12 卡已更新）。

### P2（大集合查询算法）：一个 n=2K 超越现象，已按规程复核

(a) stingy 全线远劣于 ρ_3 并随 n 衰减（闭式猜想 K/((n−K−1)η+K)，20 点 [CONJECTURE]）。
(b) **max(前向, 反向 greedy) 在 n=2K=6 的三个 η 上全部严格优于 ρ_3**：182/311 > 9/16、
21/44 > 7/15、43/108 > 7/18。规程逐字执行：穷尽搜索、n=6 全枚举（4680 LP，无对称削减）复核、
Fraction 精确 witness（monotone/submodular/band 逐条 True，比值精确等于三个分数）、第二求解器。
【最需人类判断】。限定必须并列：n=7 三个 η **全部严格劣于** ρ_3；三值全部**低于 1/η**
（exhaustive 用指数多查询早已达到 1/η，新奇处只在多项式查询数）；n=6→7 只有一个数据点。
(c) 几何平均评分的比较是二次约束，精确值 [FAILED]；实例上界全在 ρ_3 之下。

## 2. 综合读法

- **Hardness 方向**（证任意大小查询类钉在 1−e^{−1/η}）：现有全部 count-grid 工具
  （(x,y) 对称、分块、非饱和修正、任何 size-based typical 区域）在 c ≥ 1.5 时只能给出 1/η，
  即 thm:ceiling 已有的东西。要往下走必须打破 count 结构本身（例如让 G 在典型区域外依赖
  更细的组合信息），今晚没有找到这样的族。F3/anysize 的 c ≤ 0.5 量级预算是该工具箱的实际边界。
- **算法方向**（找超过 greedy 的多项式大查询算法）：n=2K 处存在（P2 的 (b)，第三个独立的
  n=2K 现象，前有 H-F 的 PE_1、L2 的候选 B 持平），但没有任何证据延伸到 n ≥ 2K+1；
  三个族（PE_1、候选 B、max(fwd,rev)）在 n=2K+1 都已回落。
- 今晚所有可行 (F,G) 解都过了 J5 的 N∖{e} 检查（P0 108/108、P1 78 个解 0 LEAK），
  按用户指令执行完毕。

## 3. open-problem 段"why it is hard"草稿（English，供人类并入 conclusion）

The size cap on queries in our hardness theorem is not an artifact of the
proof but a boundary of the entire construction toolbox it belongs to.  Any
hardness family whose values depend on the query only through the counts
(|S∖O|, |S∩O|), including block refinements, must answer typical large
queries independently of O; encoding exactly that requirement as a linear
program shows the best constant such a family can certify collapses to the
trivial ceiling 1/η once the budget reaches n^{1.5}, the optimum being the
modular instance that proves the ceiling itself [finite-parameter LP
evidence, 276 programs; an 11-row certificate isolates the mechanism].  On
the algorithmic side, no polynomial-count algorithm using large queries is
known to beat ρ_K beyond n = 2K: reverse greedy decays like K/((n−K−1)η+K),
and the best-of-forward-and-reverse combination, which does exceed ρ_3 at
n = 2K on three error levels [exact LP with rational witnesses], falls
strictly below ρ_3 already at n = 2K+1.  Whether the optimal constant of
the arbitrary-size polynomial-query class at error η is 1−e^{−1/η}, 1/η, or
strictly between remains open in both directions.

（用前提醒：第一句里的 276 = P0 的 216 + P1 的 60；数字进正文要走 numbers.tex 宏。）

## 4. must-not-claim 汇总（已同步台账 T10/T11/T12）

- 不得据 P0/P1 断言任意大小查询类的最优常数是 1/η 或 1−e^{−1/η}（排除的是构造路线，
  两个方向都 [OPEN]）。
- 不得把 (b) 的 n=2K 超越延伸到 n ≥ 7（已被精确值证伪）或说成超越 1/η（未发生）；
  (b) 不属于 𝒜_lin（反向 pass 查询大小到 n−1），与 cor:greedybudget（T10b）不冲突。
- 不得用 T10 的族或其分块推广做任意大小查询的 hardness；不得去掉 T12 预算里的常数因子。
- stingy 闭式与候选 A 闭式都是 [CONJECTURE]；(c) 只有上界。
- P0 的 J5 通过是 band 定义使然，不是可引用的正面结果。

## 5. 文件指针

- P0：results/P0_band_lp.{md,py,json}、results/P0_band_lp_iis.json（11 份证书）
- P1：results/P1_asymmetric_families.{md,py,json}
- P2：results/P2_large_query_algorithms.{md,py,json} + results/_P2_shard_*.json
- 台账：T10（第九晚注 + 禁止声称）、T11（P2 行）、T12（第九晚证据 + 禁止声称）
- 记录：TASKS8.md 从未存在（编号从 7 跳到 9，按用户上传为准）；J5 无独立文件，
  其 N∖{e} 攻击以 TASKS9 背景段的内联规格为准执行。
