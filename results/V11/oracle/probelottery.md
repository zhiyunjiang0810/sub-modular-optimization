# V11 Q9 oracle 报告：J8 ProbeLottery（K = 2，eta = 3/2）

脚本：`results/V11/oracle/probelottery.py`（一键运行 `python3 results/V11/oracle/probelottery.py`，全部通过时 exit 0）
日志：`results/V11/oracle/probelottery.log`
机器可读：`results/V11/oracle/probelottery.json`
本次运行：6 个 check PASS、1 个 GAP、0 个 FAILED、0 个 violation，exit code 0，用时 9.0 秒。

陈述来源 `results/V11/inputs/statement_probelottery.md`；Definition 1 用 `results/V11/inputs/definition1.md` 的 convention B
（band 的任意 split，只要 eta_u · eta_o ≤ 3/2）。

## 0. 路线甲（proof）的状态：GAP

仓库里没有 J8 的证明。`results/J8/probe_lottery.md`（含不等式 (3)、(8)-(12)）从未交付，
`results/J8/` 目录下只有 `J8_claude_spotcheck.py` 与它的 run log。因此：

- **(3)、(8)-(12) 的 LP 对偶证书无法给出，也无法核对。本项记 GAP**，不是 FAILED，也不是 VERIFIED。
- 装配时 J8 这一条的路线甲仍是缺口；本文件只做 oracle 与反例搜索，只能 refute，不能 verify。
- 命题本身的状态维持 `[HAND-PROOF-UNREVIEWED]`；本文件给出的是 `[VERIFIED-EXHAUSTIVE]` 级别的
  **未被证伪** 记录（有限实例族），不足以升级标签。

ProbeLottery 的实现是**自写**的，只依据 `statement_probelottery.md` 的算法描述（步骤 1-5、EPS = 1/10000、
8 个 secondary 集合、127/128 与 1/1024）。`results/J8/J8_claude_spotcheck.py` 没有被 import 也没有被复制，
只在 C5 里以子进程复跑并比对数字。未修改任何既有仓库文件，未运行 git。

## 1. Criterion C：查了什么，结果如何

| 编号 | 内容 | 状态标签 | 精确计数 |
|---|---|---|---|
| C1 | 紧实例：K = 2、eta = 3/2 的 double-residual 族（j = 1，k1 = 5/2、q = 3/5、Q = 3/5、delta = 1/5、C = 5/4），B 元素排在 tie order 前面，n ∈ {6, 8, 12, 20}（另跑了 7, 9, 10, 11）。期望值须精确等于 3/5 + 1/2048 | [VERIFIED-EXHAUSTIVE] PASS | 8 个 n，全部 E[f(T)] = 6149/10240 = 3/5 + 1/2048，OPT = 1；queries 30/39/48/57/66/75/84/156，对应上界 9n = 54/63/72/81/90/99/108/180；max queried size 全为 5；anchors 形如 [0, 1, n−2, 2, 3] |
| C1b | 紧实例的合法性：f 单调 submodular、band 实际 (eta_u, eta_o) = (1, 3/2)，乘积 = 3/2 | [VERIFIED-EXHAUSTIVE] PASS | 每个 n 在 count grid 上精确验（x ∈ 0..n−2，y ∈ 0..2，四个二阶差分方向 + 两向 band）；n = 6 与 n = 8 另在完整 2^n lattice 上逐 (S, e) 与逐 (S, e, e′) 复验，结论一致 |
| C2 | 2100 个随机合法实例，K = 2、eta = 3/2、n ∈ 8..12，三族：(1) 随机 weighted coverage，ftilde = f + f2/2，f2 是随机子 universe 上的 coverage；(2) 随机 modular，逐元素有理因子 (2m + a)/(2m) ∈ [1, 3/2]；(3) coverage 加 modular 的混合，加一个 band-consistent 的被支配扰动。合法性在完整 2^n lattice 上用精确整数穷举（单调、submodular、d ≤ dtilde ≤ (3/2)d），随后由输出分布精确算 E[f(T)] 并与 (3/5 + 1/400000)·OPT 比较 | [VERIFIED-EXHAUSTIVE] PASS | 2100 个实例（coverage 700 / modular 700 / mixture 700），2100 次完整 lattice 合法性检查，0 个非法，**0 个 violation**；最差比值 17/23 ≈ 0.739130（coverage 族，n = 10）；各族最差 17/23、11/14、39/49 |
| C3 | 结构化案例：eta = 1（ftilde = f）在最小合法 n = 4 与 n = 5；紧实例 n = 6..12；`results/E4_worst_instances.py` 的两个实例族在 K = 2、eta = 3/2 的成员（`results/N2_check.py` 的 V_j 族 uncapped 变体 j = 0, 1, 2；`code/check_explicit_instance.py` 的 U_K 族 ahat = 5/4），用 Fraction 按其闭式重建，逐实例在 2^n lattice 上验合法性，并对 8 种 tie order 取最差 | [VERIFIED-EXHAUSTIVE] PASS | 7 个 case：eta = 1 / n = 4 共 250 个实例，最差 31/36；eta = 1 / n = 5 共 250 个，最差 6/7；紧实例 n = 6..12 共 7 个值，全等于 6149/10240；V_0 = 2051/3072 ≈ 0.667643；V_1 = 3077/5120 = 3/5 + 1/1024 ≈ 0.600977；V_2 = 3281/5120 ≈ 0.640820；U_2 = 3281/5120（其实际 split 是 (5/4, 6/5)，乘积 3/2） |
| C4 | 算法 contract：每一次运行（C1、C3、D2 全部）输出集大小为 2、分布总质量为 1、queries ≤ 9n、被查询集合大小 ≤ 5 | [VERIFIED-EXHAUSTIVE] PASS | 覆盖 4660 次运行（C1 的 8 次、C2 的 2100 次、C3 的 500 + 32 次、D2 的 505 × 4 = 2020 次），0 次违反 |
| C5 | 复跑 `results/J8/J8_claude_spotcheck.py`（子进程，不修改、不 import） | [VERIFIED-EXHAUSTIVE] PASS | exit code 0，0.2 秒；它的四行紧实例输出 E[F] = 6149/10240 = 3/5 + 1/2048、queries 30/48/84/156、maxsize 5，与本脚本自写实现逐项一致；它的随机 coverage 行：400 个实例、violations = 0、worst ratio 4/5 |
| G1 | 不等式 (3)、(8)-(12) 的 LP 对偶证书 | **GAP** | 证明文件未交付，不等式在仓库中不存在，无法构造或核对证书 |

精确性说明：count grid 与输出分布的每个判定都用 `fractions.Fraction`；随机族的 lattice 判定用精确整数
（numpy int64，脚本带 overflow guard，实例值上界远小于 2^40）。浮点只出现在打印文本里。
本文件没有 [VERIFIED-LP 浮点] 项，因为没有调用任何浮点 LP solver。

## 2. Criterion D：对陈述本身的反例搜索

- **D1（随机搜索）**：2100 个合法实例，**0 个 violation**。最差比值 17/23 ≈ 0.739130，
  远高于 bound 240001/400000 = 3/5 + 1/400000 ≈ 0.600002500。
- **D2（局部搜索）**：从 n = 8 的紧实例出发做有理扰动，5 次 restart，每次 100 步被接受的合法扰动，
  共 **505 个合法扰动被评估**（3775 次尝试，3275 次因不合法被拒）。
  前三次 restart 走参数化方向（两条 residual 序列 r_x、h_x 与两个 band 乘子 lambda、mu，
  步长为 ±{1,2,3}/D，D ∈ {32, 64, 128, 256, 512}）；后两次 restart 直接扰动 grid 上每一个 F(x, y)、H(x, y)。
  每个候选都重新做精确合法性检查（f 单调 submodular、实际 eta_u · eta_o ≤ 3/2），
  每个合法候选再对 4 种 tie order 取最差比值；接受 sideways move，所以走的是等值平台。
  **0 个 violation。** 505 个比值里 307 个正好等于紧实例值 6149/10240，324 个低于 0.61，138 个等于 1，
  共 17 个不同值，最小的五个是 6149/10240、3077/5120、1541/2560、773/1280、389/640。
- **全局最差**：6149/10240 = 3/5 + 1/2048 ≈ 0.60048828（就是紧实例本身，n = 8，tie order 为 B 优先，
  anchors = [0, 1, 6, 2, 3]，E = 6149/10240，OPT = 1，实际 (eta_u, eta_o) = (1, 3/2)）。
  对 bound 的 slack 是 6149/10240 − 240001/400000 = **3109/6400000 ≈ 0.000485781**。
- 局部搜索没有把比值压到紧实例之下，说明在这个扰动邻域里紧实例是局部最坏点。这是数值事实，不是证明。

## 3. 两个数值关系（供 Q10 记录）

- 1/2048 = 195.3125/400000，即紧实例的余量是 claimed bound 余量的 195.3125 倍。
  陈述里的 1/400000 与实现得到的 1/2048 不冲突：前者是被声称的下界，后者是这一族上的取值。
- 紧实例上 ProbeLottery 的 anchors 为 [0, 1, n−2, 2, 3]：第三个 anchor 是一个 O 元素，
  P_0 = {0, 1} 只拿到 f = 3/5，超出 3/5 的部分全部来自 secondary 里含 O 元素的那两个集合。

## 4. Running example（K = 3，eta = 3/2）

K = 3、eta = 3/2 不在本命题的范围内（命题只声称 K = 2；K ≥ 3 与确定性版本仍是 [OPEN]），下面三行是对照值。
k1 = 4，q = 3/4，V_0 = 2/3、V_1 = 7/12、V_2 = 9/16，故 rho_3(3/2) = 9/16 = 0.5625，信息价格 1/eta = 2/3。
对应的 K = 2 一行：rho_2(3/2) = 3/5，ProbeLottery 在紧实例上取 6149/10240 = 3/5 + 1/2048，声称的 bound 是 3/5 + 1/400000。

## 5. FAILED 项

无。0 个 FAILED，0 个 violation，没有 witness。
唯一未完成项是 G1（路线甲的 LP 对偶证书），状态 GAP，原因是证明文件未交付。

## 6. 复跑的既有脚本

| 路径 | exit code | 关键计数 |
|---|---|---|
| `results/J8/J8_claude_spotcheck.py` | 0 | 4 个紧实例 n = 6, 8, 12, 20，E[F] 全为 6149/10240 = 3/5 + 1/2048，queries 30/48/84/156 ≤ 9n，maxsize 5；随机 coverage 400 个实例，violations = 0，worst ratio 4/5。未修改该文件 |

## 7. 空洞性检验（CLAUDE.md 第 4 节）

- **randomized**：去掉它，陈述变成确定性算法在 9n 次查询、|S| ≤ 5 下超过 3/5，这是 [OPEN]，本文件不涉及。限定词有内容，保留。
- **|S| ≤ 5**：去掉集合大小限制，穷举 ftilde 可达 1/eta = 2/3，陈述失去意义。限定词有内容。
- **9n**：改成 O(nK) 以外的预算会改变与 thm:linear-exact 的对照口径（该定理的预算是 nK、|S| ≤ K）。限定词有内容。
- **every instance**：本文件的 2100 + 505 + 32 个实例只是有限样本，不能把 "on every instance" 变成已验证；
  这正是 G1 这个 GAP 的位置。
