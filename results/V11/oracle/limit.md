# V11 Q4c oracle 报告：cor:limit（台账 T9）

脚本：`results/V11/oracle/limit.py`（一键运行 `python3 results/V11/oracle/limit.py`，全部通过时 exit 0）
日志：`results/V11/oracle/limit.log`
机器可读：`results/V11/oracle/limit.json`
本次运行：9 个 check 全 PASS，Criterion D 的 39,240 个 (K, eta) 点 0 个 violation，exit code 0，用时 11.6 秒，随机种子 20260918。

陈述来源 `results/V11/inputs/statement_limit.md`：固定 eta ≥ 1 时 L_K(eta) 与 rho_K(eta) 都收敛到
1 − e^{−1/eta}；L_K 关于 K 单调；rho_K 关于 K 非增，K ≤ ⌊eta⌋ 时等于 1/eta，从 K ≥ ⌊eta⌋ 起严格
递减，故极限从上方逼近。路线一证明材料：`paper/sections/appendix_proofs.tex` 的 `app:asymptotics`
（约第 1373 行）、`results/H_B_asymptotic.py`、`THEOREM_LEDGER.md` 的 `## T9`。
闭式（notation.md）：k_1 = (K−1)eta+1，q = (K−1)eta/k_1，V_j = 1 − q^j(1 − (K−j)/(K·eta))，
rho_K = min_j V_j（thm:exact，T6），active branch j* = max(0, K − ⌊eta⌋)。

精确性说明：本脚本每个判定都用 `fractions.Fraction` 或 sympy。e^{−1/eta} 从不以 float 参与判定，
而是用交错 Taylor 级数（0 ≤ 1/eta ≤ 1 时各项非增，相邻部分和夹住真值）取 60 项得到精确有理
lo/hi 上下界，比较全部在有理数上完成。float 只出现在打印文本里。未修改任何既有仓库文件。

---

## 1. 查了什么，结果如何

| 编号 | 内容 | 状态标签 | 精确计数 |
|---|---|---|---|
| C0 | 复跑 `results/H_B_asymptotic.py` | [VERIFIED-LP 浮点]（其 section 0 经 `code/reduced_lp.py` 调 scipy linprog）＋[VERIFIED-SYMBOLIC]（section 2、5、6）＋[VERIFIED-EXACT]（section 4） PASS | exit code 0，4.1 秒；section 0：49 个点（7 eta × 7 K），max \|LP − closed form\| = 3.331e−16，j* 处处取到 min_j V_j；section 2：order 1 = e^{−1/eta}(2eta−1)/(2eta²) True 且 d/dm = 0 True；section 3：max \|Richardson − closed form\| = 1.288e−12；section 4：2,793 个精确有理差分（7 eta × K = 2..400），负值 0，零值只出现在 K < ⌊eta⌋；section 5：分子 84 项 0 负、常数 14，分母 165 项 0 负，直接扫描 0 个非正值；section 6：c_U = c True |
| C1 | sympy：L_K(eta) → 1 − e^{−1/eta}（symbolic eta 一次，7 个有理 eta 各一次） | [VERIFIED-SYMBOLIC] PASS | 8 个 limit |
| C2 | sympy：V_{K−⌊eta⌋}(eta) → 1 − e^{−1/eta}（symbolic (eta, m) 一次，7 个有理 eta 配 m = ⌊eta⌋ 各一次） | [VERIFIED-SYMBOLIC] PASS | 8 个 limit；symbolic m 的那次说明极限与 ⌊eta⌋ 取值无关 |
| C3 | sympy series（epsilon = 1/K，active branch V_{K−m}）：order 0 = 1 − e^{−1/eta}，order 1 = c(eta) = e^{−1/eta}(2eta−1)/(2eta²)，∂c/∂m = 0；另在 7 个有理 eta 上逐个复算 order 0、order 1 | [VERIFIED-SYMBOLIC] PASS | 1 次符号展开 + 7 次定值展开，共 17 条恒等式判定 |
| C3b | R_K = K²(rho_K − (1 − e^{−1/eta}) − c(eta)/K) 的精确有理夹逼，K ∈ {10,20,40,80,160,320,640,800} | [VERIFIED-EXHAUSTIVE]（有限区间精确检查，不是渐近证明） PASS | 56 个夹逼区间，max \|R_K\| = 0.234216（eta = 5，K = 10），判定阈值 1 |
| C4 | 精确有理差分 rho_{K+1} − rho_K ≤ 0，K = 2..200，eta ∈ {1, 3/2, 2, 5/2, 3, 7/2, 5}；等号只在 plateau（两端都 ≤ ⌊eta⌋），plateau 外严格；plateau 上 rho_K = 1/eta | [VERIFIED-EXHAUSTIVE] PASS | 1,393 个差分：0 个正、5 个零、1,388 个严格负；零点分布 eta = 3 与 7/2 各在 K = 2，eta = 5 在 K = 2..4，与 K + 1 ≤ ⌊eta⌋ 完全吻合；plateau 值 rho_K = 1/eta 在 10 个 (K, eta) 上逐点核对 |
| C5 | 精确有理差分 L_{K+1} − L_K < 0，K = 1..200，同一 eta 网格 | [VERIFIED-EXHAUSTIVE] PASS | 1,400 个差分全严格负，0 个非负；即 L_K 关于 K 递减（monotone，从上方） |
| C6 | 从上方逼近：用 e^{−1/eta} 的精确有理下界判定 1 − rho_K < lo 与 1 − L_K < lo | [VERIFIED-EXHAUSTIVE] PASS | 2,800 次精确比较（7 eta × K = 2..201 × 两条曲线），最小 slack：rho 为 7.280e−04（eta = 5，K = 201），L 为 8.152e−05（eta = 5，K = 201） |
| C7 | 闭式自洽（conditional on thm:exact / T6）：j* 取到 min_{0≤j≤K} V_j；sandwich L_K ≤ rho_K ≤ U_K | [VERIFIED-EXHAUSTIVE] PASS | 420 个 (K, eta) 点（7 eta × K = 1..60）两项各一次；U_K − L_K 最宽 0.800000（eta = 5，K = 1） |
| D | 对陈述本身的反例搜索 | [VERIFIED-EXHAUSTIVE] PASS | 39,240 个 (K, eta) 点，38,527 个精确单调性差分，0 个 violation |

C0 的精确性划分：`results/H_B_asymptotic.py` 的 section 0 用 `code/reduced_lp.py` 的 scipy
`linprog` 做浮点交叉核对（偏差 3.331e−16），该项标 [VERIFIED-LP 浮点]，不标 exact；同一脚本的
section 2/5/6 是 sympy 恒等式，section 4 是 `Fraction` 精确差分，这两类是 exact。本报告里 C1..C7
与 D 的每个判定都在本脚本内用精确算术独立重做，不依赖 H_B 的浮点部分。

复跑方式（保守选择，已记录理由）：`results/H_B_asymptotic.py` 会把 JSON 写到自己所在目录，就地
运行会覆盖既有的 `results/H_B_asymptotic.json`，违反"不修改既有仓库文件"。所以脚本把它逐字节
复制到临时 mirror 目录，并把 mirror 的 `code` 指向仓库的 `code/`，执行的源码与仓库版本 sha256
相同（f6ec7ce9f1dc7d0f...），运行前后再核对仓库脚本与其 JSON 的 sha256 均未变（日志里
`repo files untouched: True`）。mirror 的完整 rerun log 路径记录在 `limit.json` 的
`checks.C0.rerun_log`。

---

## 2. Criterion D：对陈述本身的反例搜索

搜索的两条命题：(i) rho_K 关于 K 非增，任何 rho_{K+1} > rho_K 即 FAILED；(ii) 极限从上方逼近，
任何 rho_K ≤ 1 − e^{−1/eta} 即 FAILED。附带核对 plateau 上 rho_K = 1/eta，以及等号只出现在
plateau 内部（K + 1 ≤ ⌊eta⌋）。

| 子搜索 | 参数 | 点数 | 差分数 | violation |
|---|---|---|---|---|
| D1 dense grid | 所有既约 p/q ∈ [1, 8]（q ≤ 12）共 323 个 eta × K = 2..61 | 19,380 | 19,057（696 个等号全在 plateau，18,361 严格递减） | 0 |
| D2 random grid | seed 20260918，300 个随机有理 eta ∈ [1, 30]（分母 ≤ 40）× K = 2..61 | 18,000 | 17,700（3,891 等号，13,809 严格递减） | 0 |
| D3 结构化 | 8 个情形（见下） | 1,860 | 1,770 | 0 |

D3 的 8 个结构化情形，全部 PASS：eta = 1（此时 rho_K = L_K，60 点）；integer eta = 2..8 的
branch breakpoint（420 点，21 个等号）；integer 下方 eta = k − 1/1000（420 点）；integer 上方
eta = k + 1/1000（420 点）；eta ≫ K 的全 plateau，eta ∈ {100, 1000, 10⁶}（180 点，177 个差分全为
等号）；对角线 eta = K（60 点）；大的非整数 eta ∈ {121/2, 3001/100}（120 点）；eta 从上方趋于 1，
eta = 1 + 1/d，d ∈ {10, 100, 1000}（180 点）。

worst slack（最接近违反的点）：
- 单调性：D1+D2 上最大的严格差分 rho_{K+1} − rho_K = −6.378052e−08，出现在 eta = 666/23 ≈ 28.96、
  K = 28（刚离开 plateau 的第一步，差分最小但仍严格为负）；C 网格（K ≤ 200）上为 −3.614009e−06，
  出现在 eta = 5、K = 200。
- 从上方逼近：D1+D2 上最小的 rho_K − (1 − e^{−1/eta}) 下界为 3.997729e−04，出现在 eta = 30、
  K = 61；C 网格上为 7.280246e−04（eta = 5，K = 201）。

违反数 0，没有 witness 需要记录。

---

## 3. Running example：K = 3, eta = 3/2

m = ⌊eta⌋ = 1，k_1 = 4，q = 3/4，j* = K − m = 2；rho_3 = V_2 = 9/16 = 0.5625，L_3 = 386/729 ≈ 0.529492，U_3 = 37/64 = 0.578125，满足 L_3 ≤ rho_3 ≤ U_3。
rho_4 = 1447/2662 ≈ 0.543576，rho_4 − rho_3 = −403/21296 ≈ −0.018924 < 0（严格递减，K ≥ ⌊eta⌋ = 1 之后无 plateau）。
极限 1 − e^{−2/3} ∈ [0.486582880967, 0.486582880967]（有理夹逼），rho_3 − 极限 ≥ 0.075917 > 0，c(3/2) ∈ [0.2281853862, 0.2281853862]，与台账 T9 记的 c(1.5) ≈ 0.228 一致。

---

## 4. 结论与保留

- 陈述的四个子句在检查范围内全部被 oracle 支持：两条极限（C1、C2，符号），L_K 单调（C5，精确），
  rho_K 非增且 plateau 等于 1/eta、plateau 外严格递减（C4、D，精确），从上方逼近（C6、D，精确）。
  一阶展开 rho_K = 1 − e^{−1/eta} + c(eta)/K + O(1/K²)，c(eta) = e^{−1/eta}(2eta−1)/(2eta²)
  独立复现（C3 符号；C3b 在 K ≤ 800 上精确夹逼 R_K）。
- 保留一：所有关于 rho_K 的结论都经由闭式 rho_K = min_j V_j，因此 conditional on thm:exact（台账
  T6）。C7 只核对了 j* 取到 min_j V_j，没有独立重证 thm:exact 本身。
- 保留二：C4、C5、C6、D 都是有限范围的穷举（K ≤ 200 或 K ≤ 61，eta 取自有限网格），不构成对所有
  K、所有 eta 的证明；无穷远处的单调性仍依赖 `app:asymptotics` 的导数论证，其中从连续导数过渡到
  离散差分（含 integer eta 处的 branch 切换）与尾界装配仍是 [HAND-PROOF-UNREVIEWED]，与台账 T9
  的记法一致。
- 保留三：C3b 只说明 R_K 在 K ∈ [10, 800] 与 7 个 eta 上有界（max \|R_K\| ≈ 0.234），不能声称
  O(1/K²) 的余项对 eta 一致或带显式常数，这一点台账 T9 已列为禁止声称。
- 无 FAILED 项。
