# Q3 失败点报告（Night 10, TASKS10）[FAILED]

日期: 2026-09-12 夜。任务: 证明同预算类 A_lin（<= nK 次、每次 |S| <= K 的查询）的
hardness 值恰为 rho_K(eta)，路线为 N4/F3 的 O-无关计数网格族 + app:greedybudget 的
transcript 论证。结论: 该路线不能达成目标，卡点是一个明确的不等式（第 2 节）。
注意 FAILED 的含义是"这条路线证不出目标"，不是"目标被证伪": A_lin 的精确值仍然
open，夹逼区间由 [rho_K, min{U_K, 1/eta}] 收窄为 [rho_K, min{W, 1/eta}] 的候选
（第 6 节，未采纳，待明早 Q4）。

## 1. 一句话卡点

O-无关计数网格族的 LP 值 rho_K^(n) 关于 n 单调不减: 在 n = 2K 处恰等于
rho_K = min_j V_j，但从 n_c = K + j + m_c 起严格超过 rho_K
（m_c = floor(eta(K-1)) + 1，[VERIFIED-SYMBOLIC]），并在
n >= K + j + m* 处饱和于 W = V_j + (K-j) E(m*) > rho_K。而 transcript 论证
（app:greedybudget 的并集界 K^5/(2n)）需要 n >= 4K^5，远在饱和点之后。
所以该族在 transcript 所需的 n 上能给出的最好 ceiling 是 W，不是 rho_K，
TASKS10 目标定理的前提 (c)（rho_K^(n) -> rho_K）不成立。

## 2. 卡住的不等式与参数区间

记（固定 K >= 3，活跃段 j = K + 1 - ceil(eta)，2 <= j <= K-1，
eta 在段 (K-j, K-j+1) 内部；k1 = (K-1)eta + 1，q = 1 - 1/k1，nu = eta/(eta-1)）:

    D_base = q^j / (K eta),
    D(m)   = q^j (nu^m / K - 1) / (eta (nu^m - 1) - m),   m >= 1,
    E(m)   = D(m) - D_base.

卡住的不等式（excess positivity）有闭式因子分解 [VERIFIED-SYMBOLIC，
results/Q2_symbolic.py C6，并另做了独立 3 行 sympy 复核]:

    E(m) = q^j (m - eta(K-1)) / ( K eta ( eta(nu^m - 1) - m ) ).

分母对 m >= 1、eta > 1 恒正（Bernoulli: nu^m >= 1 + m/(eta-1) 给出
分母 >= m/(eta-1) > 0），于是

    E(m) > 0  当且仅当  m > eta(K-1)，
    m_c = floor(eta(K-1)) + 1，  n_c = K + j + m_c。

关键结构事实（状态标签逐条）:
- E(1) < 0 恒成立 [VERIFIED-SYMBOLIC]: D(1) = q^j (K - eta(K-1))/K，
  E(1) 的符号 = -((K-1)eta - 1)(eta - 1) < 0（eta > 1）。
  超额不来自第一步，而来自长尾（m > eta(K-1) 的中段）。
- lim_{m->infinity} D(m) = D_base 且从上方趋近 [VERIFIED-SYMBOLIC]，
  所以 sup_m D(m) 在有限 m* 处取到，超额是中段现象不是极限现象。
- m_c > K - j 恒成立 [VERIFIED-SYMBOLIC]: m_c > eta(K-1) >= eta > K - j
  （活跃段内 eta > K - j）。这正是 n = 2K 恰好等于 rho_K 的原因:
  n = 2K 时网格宽度 X = K，尾巴可用长度 X - j = K - j < m_c，
  E(m) > 0 的 m 放不进网格，于是 D = D_base，LP 值 = V_j = rho_K。
  无尾窗口的精确刻画: D = D_base 当且仅当 X - j <= eta(K-1)，
  即 n <= n_c - 1。
- argmax m*(K, eta) 的取值规则: 继承自 N4/Q1 的猜想 m* = ceil(eta K) - 1
  被精确有理反例推翻（frac(eta K) 很小时差 1: 例如 K=5, eta=2001/1000 时
  真 m* = 9 而猜想给 10；共 4 个反例，见 Q2_symbolic.md）。修正规则
  m* = min{m >= 1: nu^m (eta K - 1 - m) <= K(eta-1)}，且 m* <= ceil(eta K) - 1
  [CONJECTURE，48/48 sweep 点单峰确认]。此事只影响用 m* 预测 saturation
  onset 的推断，不影响闭式 feasibility（本夜全部脚本用直接 argmax）。

参数区间:
- 2 <= j <= K-1（即 1 < eta < K-1 所在诸段）: 闭式与 LP 顶点逐格一致
  （LP-exact），上述卡点完整成立。
- j <= 1（eta > K-1）: 闭式只是上界（F(x,K) = 1 的额外约束使真 LP 值更小），
  但独立 n-sweep 显示该段同样在大 n 严格超过 rho_K
  （K=3 eta=5/2 超额 4.117e-03；K=4 eta=2 超额 3.187e-04），
  所以卡点不是 j >= 2 域的 artifact。

## 3. 与 transcript 的定量不相容

- rho_K^(n) = rho_K 恰好只在窗口 n <= n_c - 1 = K + j + floor(eta(K-1)) 内
  （含 n = 2K）。窗口是 n = O(eta K) 的线性量级。
- app:greedybudget 的 τ=1 计数链需要 n >= 4K^5 才能把
  并集界 K^5/(2n) 与输出泄露 K^2/n 压到 1/2 以下。
- 两者无交集（K >= 2 时 4K^5 远大于 O((eta+2)K)），
  且并集界的 K^5/n 形状是 transcript 结构决定的，缩不进线性窗口。

实测阶梯（results/Q2_indep_nsweep.log，全部 [VERIFIED-LP]）:

| K | eta | j | rho_K | 首个超过 rho_K 的 n | 饱和 n >= | W（饱和值） | W - rho_K |
|---|-----|---|-------|--------------------|-----------|------------|-----------|
| 3 | 3/2 | 2 | 9/16 = 0.5625 | 9 | 9 | 0.5635775862 | 1.078e-03 |
| 4 | 3/2 | 3 | 1447/2662 | 12 | 12 | 0.5437037511 | 1.275e-04 |
| 4 | 5/2 | 2 | 109/289 | 14 | 15 | 0.3781499125 | 9.873e-04 |
| 5 | 5/2 | 3 | 491/1331 | 19 | 20 | 0.3691075814 | 2.120e-04 |
| 4 | 2   | - | 22/49 | <= 16 | <= 16 | 0.4492982850 | 3.187e-04 |
| 3 | 5/2 | 1 | 7/18 | <= 12 | <= 24 | 0.3930063770 | 4.117e-03 |

（后两行是端点/j<=1 的控制组，只做 P1-P3 检查。）

## 4. Q2 四项检查的状态汇总

TASKS10 Q2 checklist 对照（详表见 results/Q2_symbolic.md）:

1. F 单调 submodular（分段，含 x=j 与 x=T 两个衔接分支）:
   [VERIFIED-SYMBOLIC]（Q2_symbolic C1 15 项 + C2 19 项）。两个衔接分支的
   submodularity 条件恰好等价于 D 在 argmax 处的局部最优性条件
   （D(m) - D(m-1) = r_T/(eta B(m-1)) 与 D(m) - r_T = (eta-1)B(m+1)(D(m)-D(m+1))
   两条恒等式），所以任何 argmax 处闭式都 feasible，无额外边条件。
2. 单元素带（四类边，split (eta,1)）: [VERIFIED-SYMBOLIC]（C3 16 项）。
   极值边清单: y-edge y=0->1 在下端 tight（dG = dF/eta，实现 eta_u = eta）；
   其余三类边（y=0 与 y=1 的 x-edge、y>=1 的 y-edge、y>=2 的 x-edge）
   全部上端 tight（dG = dF，实现 eta_o = 1），核心是主恒等式
   a(x) - a(x+1) = g(x+1)/eta（a = r - g）。
3. G 在 |S| <= K、|S∩O| <= 1 上只依赖 |S|: 构造上成立（y <= 1 区 G = Ghat(x+y)），
   相邻表示的 tie G(x+1,0) = G(x,1) 逐格核对通过；Ghat 三段相位衔接与步长
   [VERIFIED-SYMBOLIC]（C4 9 项）。
4. 比值闭式与 n -> infinity 极限 = V_j: 闭式 F(K,0) = 1 - q^j + (K-j)D 与
   归一化 [VERIFIED-SYMBOLIC]（C5），但极限 = V_j **[FAILED]**: 极限是
   W = V_j + (K-j) E(m*) > V_j（第 2 节的不等式），不是 V_j。
   这就是本夜的失败点。整数 eta 处的段切换恒等式 V_j(eta) = V_{j+1}(eta)
   于 eta = K - j: [VERIFIED-SYMBOLIC]（C7）。

支撑 oracle（全部一键复现，见第 7 节）:
- 独立 n-sweep: 6 组 (K,eta) x 33 个 LP，P1（n=2K 恰为 rho_K）、
  P2（单调不减）、P3（大 n 严格超额）、P4（饱和值与 W 闭式逐位一致、
  饱和起点 K+j+m*、临界前一步严格低于 W）全过 [VERIFIED-LP]。
- 全格点电池: 36/36 配置（K in {3,4,5,8}，全部 2 <= j <= K-1 段中点，
  n in {2K,4K,8K}）精确有理通过单调/submodular/归一/带/tie/目标值
  [VERIFIED-LP]。
- 一般 K 符号: results/Q2_symbolic.py 亲跑 exit 0，103 项 PASS，
  C0（转录守卫）到 C8（18 组全格点交叉）无一 FAILED；仅两条 [CONJECTURE]
  且都只涉及 argmax 位置 m*，不涉及 feasibility。最要害的 E(m) 因子分解
  另做了独立 sympy 复核（本报告第 2 节）。

## 5. 命名警示

本报告的 W（计数网格族的饱和常数）与 rem:exact-gap 中 H-C 的 W_m(K,eta)
（submodular-surrogate 模型的 upper-bound 实例下包络，带分段点 beta_m）
是两个不同对象，历史上都被叫过 "W_K"。写入任何正文前必须换名，
建议 W^grid_K(eta) 或 rho_bar_K(eta)。

## 6. 副产物（最需人类判断，今晚未采纳）

严格序 rho_K < W < U_K 在全部 8 个测试配置成立（K 到 12，
results/Q3_W_vs_UK.log），且 W - rho_K 随 K 衰减远快于 U_K - W
（K=8: 8.3e-08 对 1.9e-03；K=12: 1.0e-08 对 1.6e-03）。
若把 cor:greedybudget 的 ceiling 从 min{U_K, 1/eta} 换成 min{W, 1/eta}，
夹逼区间会大幅收窄。需要的补件: (i) 闭式族 validity 的一般 K 符号版: 本夜已具备
（Q2_symbolic C1-C5 全部 [VERIFIED-SYMBOLIC]）; (ii) transcript 复用检查
（族在 n >= 4K^5 处可用、O-无关区域覆盖 transcript 所需查询集）:
未做; (iii) W 的解析性质（单调性、eta -> 1 与 eta -> K 端点、
与 1/eta 的交点）: 未做。缺 (ii)(iii) 且按闸门规则，今晚不装配。
按 "Q2 未全部通过不得改正文" 闸门，今晚正文与台账均未动（无 T10c 卡）。
建议明早与 GPT 的 Q4 交叉核对时一并裁定。

## 7. 复现清单

- python3 results/Q0_extract.py            (52 个 LP 顶点 + 阶梯扫描, agent)
- python3 results/Q2_indep_nsweep.py       (独立复核, 33 个 LP, exit 0)
- python3 results/Q2_grid_check.py --sweep (36/36 精确有理电池, exit 0)
- python3 results/Q2_symbolic.py           (一般 K 符号验证)
- python3 results/Q3_W_vs_UK.py            (副产物表, exit 0)

日志: results/Q2_indep_nsweep.log, results/Q2_grid_check.log,
results/Q2_symbolic_run.log, results/Q3_W_vs_UK.log,
results/Q1_selfcheck.json, results/Q2_symbolic.json。

## 附录（Q4 交叉核对日补记）

Q4 的外部并行结果（双残差截断族）与本报告不矛盾，且闭合了目标：

- 本报告的 FAILED 结论针对的是**全局 O-无关**的计数网格族（O-无关强加于
  一切大小的 balanced 状态，沿 N4 的 LP 表述）。该结论仍真：那一类族的
  极限是 W > rho_K，卡点不等式 E(m) > 0 iff m > eta(K-1) 不变。
- 但 TASKS10 目标 (b) 原文只要求 |S| <= K 处 O-无关，transcript 论证也只
  查得到这些集合。把 LP 的 O-无关约束改到 small-set-only 后，其值在全部
  18 个测试 (K, eta, n)（含本报告表格中阶梯启动之后的 n）恰等于 rho_K
  （results/Q4_smallset_lp.py [VERIFIED-LP]）。第十晚把 (b) 实现成了
  全局约束，是路线实现对目标条件的过度约束。
- Q4 的族在正确的约束下逐点达到 rho_K（对一切 n >= 2K，无极限），
  合法性 13+34 项 [VERIFIED-SYMBOLIC] + 111+159 组精确电池，定理已装配
  为 thm:linear-exact（台账 T10c）。
- 第 6 节的副产物（用 W 换 U_K 的 ceiling）被更强的精确结果取代，
  不再需要；W 不进正文，第 5 节的命名冲突随之消解。
- 第 2 节的 m* 附注在 Q4 得到落实：appendix 的 m* 定义已改为 argmax
  形式（results.tex 未涉及）。
