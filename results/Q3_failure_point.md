# Q3 失败点报告（Night 10, TASKS10）[FAILED]

日期: 2026-09-12 夜。任务: 证明同预算类 A_lin（<= nK 次、每次 |S| <= K 的查询）的
hardness 值恰为 rho_K(eta)，路线为 N4/F3 的 O-无关计数网格族 + app:greedybudget 的
transcript 论证。结论: 该路线不能达成目标，卡点是一个明确的不等式（第 2 节）。
注意 FAILED 的含义是"这条路线证不出目标"，不是"目标被证伪": A_lin 的精确值仍然
open，夹逼区间由 [rho_K, min{U_K, 1/eta}] 收窄为 [rho_K, min{W, 1/eta}] 的候选
（第 6 节，未采纳，待明早 Q4）。

## 1. 一句话卡点

O-无关计数网格族的 LP 值 rho_K^(n) 关于 n 单调不减: 在 n = 2K 处恰等于
rho_K = min_j V_j，但从 n = K + j + m_c 起严格超过 rho_K，并在
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

卡住的不等式（excess positivity）:

    存在 m >= 1 使 E(m) > 0。

等价地（分母 eta(nu^m - 1) - m 对 m >= 1、eta > 1 恒正，由 Bernoulli
不等式 nu^m >= 1 + m/(eta-1) 得其 >= m/(eta-1) > 0，[VERIFIED-SYMBOLIC]
见 results/Q2_symbolic.md C6c），E(m) > 0 当且仅当

    N(m) := eta nu^m (K-1) - K (eta - 1) nu^m ... 见 Q2_symbolic.md C6 的
    规范形（sympy 给出的公分子）。

关键结构事实（状态见第 4 节）:
- E(1) < 0 恒成立: D(1) = q^j (K - eta(K-1))/K，
  E(1) 的符号 = -((K-1)eta - 1)(eta - 1) < 0（eta > 1）。
  所以超额不来自第一步，而来自长尾。
- E(m) 在 m 充分大时 > 0，首个正的 m 记 m_c(K, eta)；
  D(m) 的 argmax 记 m*(K, eta)，数值上 m* = ceil(eta K) - 1 [CONJECTURE]。
- m_c > K - j 在全部测试参数上成立，这正是 n = 2K 恰好等于 rho_K 的原因:
  n = 2K 时网格宽度 X = K，尾巴可用长度 X - j = K - j < m_c，
  E(m) > 0 的 m 放不进网格，于是 D = D_base，LP 值 = V_j = rho_K。

参数区间:
- 2 <= j <= K-1（即 1 < eta < K-1 所在诸段）: 闭式与 LP 顶点逐格一致
  （LP-exact），上述卡点完整成立。
- j <= 1（eta > K-1）: 闭式只是上界（F(x,K) = 1 的额外约束使真 LP 值更小），
  但独立 n-sweep 显示该段同样在大 n 严格超过 rho_K
  （K=3 eta=5/2 超额 4.117e-03；K=4 eta=2 超额 3.187e-04），
  所以卡点不是 j >= 2 域的 artifact。

## 3. 与 transcript 的定量不相容

- rho_K^(n) = rho_K 恰好只在窗口 n <= K + j + m_c - 1 内（含 n = 2K）。
  m_c 与 m* 都是 Theta(eta K) 量级（数值上 m* = ceil(eta K) - 1），
  所以窗口是 n = O((eta+2)K)。
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

1. F 单调 submodular（分段）: [PLACEHOLDER-C1C2]
2. 单元素带（四类边，split (eta,1)）: [PLACEHOLDER-C3]
3. G 在 |S| <= K、|S∩O| <= 1 上只依赖 |S|: 构造上成立（y <= 1 区 G = Ghat(x+y)），
   相邻表示的 tie G(x+1,0) = G(x,1) 逐格核对通过；Ghat 相位衔接 [PLACEHOLDER-C4]。
4. 比值闭式与 n -> infinity 极限 = V_j: **[FAILED]**。极限是
   W = V_j + (K-j) E(m*) > V_j（第 2 节的不等式），不是 V_j。
   这就是本夜的失败点。整数 eta 处的段切换恒等式 [PLACEHOLDER-C7]。

支撑 oracle（全部一键复现，见第 7 节）:
- 独立 n-sweep: 6 组 (K,eta) x 33 个 LP，P1（n=2K 恰为 rho_K）、
  P2（单调不减）、P3（大 n 严格超额）、P4（饱和值与 W 闭式逐位一致、
  饱和起点 K+j+m*、临界前一步严格低于 W）全过 [VERIFIED-LP]。
- 全格点电池: 36/36 配置（K in {3,4,5,8}，全部 2 <= j <= K-1 段中点，
  n in {2K,4K,8K}）精确有理通过单调/submodular/归一/带/tie/目标值
  [VERIFIED-LP]。
- 一般 K 符号: results/Q2_symbolic.md [PLACEHOLDER-SYMBOLIC-SUMMARY]

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
夹逼区间会大幅收窄。需要的补件: (i) 闭式族 validity 的一般 K 符号版
（Q2_symbolic 的 C1-C5）; (ii) transcript 复用检查（族在 n >= 4K^5 处
可用、O-无关区域覆盖 transcript 所需查询集）; (iii) W 的解析性质
（单调性、eta -> 1 与 eta -> K 端点、与 1/eta 的交点）。
按 "Q2 未全部通过不得改正文" 闸门，今晚正文与台账均未动（无 T10c 卡）。
建议明早与 GPT 的 Q4 交叉核对时一并裁定。

## 7. 复现清单

- python3 results/Q0_extract.py            (52 个 LP 顶点 + 阶梯扫描, agent)
- python3 results/Q2_indep_nsweep.py       (独立复核, 33 个 LP, exit 0)
- python3 results/Q2_grid_check.py --sweep (36/36 精确有理电池, exit 0)
- python3 results/Q2_symbolic.py           (一般 K 符号验证)
- python3 results/Q3_W_vs_UK.py            (副产物表, exit 0)

日志: results/Q2_indep_nsweep.log, results/Q2_grid_check.log,
results/Q3_W_vs_UK.log, results/Q1_selfcheck.json, results/Q2_symbolic.json。
