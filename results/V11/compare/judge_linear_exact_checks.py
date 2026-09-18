"""ROUTE-COMPARISON judge (TASKS11 Q6, criterion B) — thm:linear-exact (T10c / J6).

一键复跑本比对文件里的全部数值判定。不修改任何既有文件，不 import 路线二的脚本以外的仓库代码。

段落：
  [1] rho_K / V_j / L_K / U_K 的精确有理数与 sympy 恒等式（含路线二 GAP-7 的 j 取值范围）
  [2] 路线一显式族（double-residual，appendix_proofs.tex app:greedybudget）的独立合法性复核
  [3] union bound 两条计数链（路线一与路线二写法）的符号等价
  [4] 路线二 4.2 的 K=2 有理矛盾（1/6 < 2/9）逐步精确复算
  [5] 决定性对照 LP：blindness 加在"所有 size"（路线二的 (*)）还是只加在 |S| <= K（路线一）

判定一律用 fractions.Fraction / sympy；float 只出现在 LP 求解与打印。
"""
from fractions import Fraction as R
import math

import numpy as np
import sympy as sp
from scipy.optimize import linprog


# ---------------------------------------------------------------- [1] rho_K
def V_list(K, eta):
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return k1, q, [1 - q ** a * (1 - R(K - a, 1) / (K * eta)) for a in range(K + 1)]


def section1():
    print("== [1] rho_K / V_j / L_K / U_K ==")
    for K, eta in [(2, R(3, 2)), (3, R(3, 2)), (4, R(3, 2))]:
        k1, q, V = V_list(K, eta)
        LK = 1 - (1 - 1 / (eta * K)) ** K
        UK = 1 - (1 - 1 / (eta * (K - 1) + 1)) ** K
        print(f"  K={K} eta={eta}: k1={k1} q={q} V={[str(v) for v in V]}")
        print(f"     min_{{0..K-1}}={min(V[:K])}  min_{{0..K}}={min(V)}  "
              f"L_K={LK}  U_K={UK}  V_0==1/eta:{V[0] == 1/eta}  V_K==U_K:{V[K] == UK}")
    bad = []
    for K in range(2, 14):
        for eta in [R(1001, 1000), R(11, 10), R(5, 4), R(3, 2), R(7, 4), R(2), R(9, 4),
                    R(5, 2), R(3), R(4), R(K), R(K) + R(1, 3), R(K) - R(1, 3), R(2 * K)]:
            if eta <= 1:
                continue
            _, _, V = V_list(K, eta)
            js = max(0, K - math.floor(eta))
            if min(V[:K]) != min(V) or V[js] != min(V):
                bad.append((K, eta))
    print(f"  j 取值范围 0..K-1 与 0..K 给出不同 rho_K 的参数（应为空）: {bad}")
    Ks, Es, js = sp.symbols("K E j", positive=True)
    k1s = (Ks - 1) * Es + 1
    qs = (Ks - 1) * Es / k1s
    Vs = lambda a: 1 - qs ** a * (1 - (Ks - a) / (Ks * Es))
    print("  sympy: V_{j+1}-V_j - q^j(E-K+j)/(K E k1) =",
          sp.simplify(sp.cancel(Vs(js + 1) - Vs(js) - qs ** js * (Es - Ks + js) / (Ks * Es * k1s))))
    print("  sympy: V_0 - 1/eta =", sp.simplify(Vs(0) - 1 / Es),
          " V_K - U_K =", sp.simplify(Vs(Ks) - (1 - (1 - 1 / ((Ks - 1) * Es + 1)) ** Ks)))


# ------------------------------------------------- [2] 路线一显式族的独立复核
def family(K, eta, eta_u):
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    j = max(0, K - math.floor(eta))
    Q = q ** j
    d = Q / (K * eta)
    C = k1 / K

    def r(x):
        return q ** x if x <= j else max(R(0), Q - (x - j) * d)

    def h(x):
        return R(K - 1, K) * q ** x if x <= j else max(R(0), R(K - 1, K) * Q - (x - j) * d)

    def F(x, y):
        return 1 - r(x) if y == 0 else 1 - R(K - y, K - 1) * h(x)

    def H(x, y):
        return C - r(x) - (eta - 1) * h(x) if y == 0 else C - eta * R(K - y, K - 1) * h(x)

    return j, F, H, (lambda x, y: H(x, y) / eta_u)


def section2(xmax=14):
    print("== [2] 路线一 double-residual 族的独立复核（精确有理） ==")
    for K, eta in [(2, R(3, 2)), (3, R(3, 2)), (4, R(2)), (5, R(5, 2)), (6, R(7, 4))]:
        _, _, Vg = V_list(K, eta)
        rho = min(Vg)
        for eu, eo in [(R(1), eta), (eta, R(1)), (R(5, 4), eta / R(5, 4))]:
            j, F, H, ft = family(K, eta, eu)
            mono = sub = band = True
            for x in range(xmax + 1):
                for y in range(K + 1):
                    for dx, dy in [(1, 0), (0, 1)]:
                        xx, yy = x + dx, y + dy
                        if xx > xmax or yy > K:
                            continue
                        dF, dg = F(xx, yy) - F(x, y), ft(xx, yy) - ft(x, y)
                        mono &= dF >= 0
                        band &= (dF / eu <= dg <= eo * dF)
                        for sx, sy in [(1, 0), (0, 1)]:
                            if xx + sx > xmax or yy + sy > K:
                                continue
                            sub &= dF >= F(xx + sx, yy + sy) - F(x + sx, y + sy)
            norm = (F(0, 0) == 0 and ft(0, 0) == 0 and F(0, K) == 1
                    and max(F(a, K - a) for a in range(K + 1)) == 1)
            small_blind = all(H(x, 0) == H(x - 1, 1) for x in range(1, K + 1))
            leak = [(x, H(x, 0), H(x - 1, 1)) for x in range(K + 1, xmax + 1)
                    if H(x, 0) != H(x - 1, 1)]
            print(f"  K={K} eta={eta} split=({eu},{eo}) j={j}: mono={mono} sub={sub} band={band} "
                  f"norm={norm} F(K,0)={F(K, 0)} ==rho:{F(K, 0) == rho} "
                  f"blind_on_|S|<=K:{small_blind} first_leak={leak[0] if leak else None}")


# -------------------------------------------------------- [3] 两条计数链
def section3():
    print("== [3] union bound 计数链 ==")
    n, K = sp.symbols("n K", positive=True)
    r2 = n * K * sp.binomial(K, 2) * (K * (K - 1) / (n * (n - 1)))
    r1 = n * K * sp.binomial(K, 2) * (K / n) ** 2
    print("  route2: nK C(K,2) K(K-1)/(n(n-1)) - K^3(K-1)^2/(2(n-1)) =",
          sp.simplify(r2 - K ** 3 * (K - 1) ** 2 / (2 * (n - 1))))
    print("  route1: nK C(K,2) (K/n)^2 - K^4(K-1)/(2n) =",
          sp.simplify(r1 - K ** 4 * (K - 1) / (2 * n)))
    print("  K^3(K-1)^2/(2(n-1)) <= K^5/(2n) 化简为 K^2 <= n(2K-1):",
          sp.simplify(sp.factor(K ** 5 * (n - 1) - K ** 3 * (K - 1) ** 2 * n)))
    for K0, n0 in [(3, 972), (2, 128)]:
        vis = R(K0 ** 3 * (K0 - 1) ** 2, 2 * (n0 - 1))
        hit = R(K0 ** 2, n0)
        eps = R(K0 ** 2, n0) + R(K0 ** 5, 2 * n0)
        print(f"  K={K0} n={n0}: Vis<={vis} Hit<={hit} eps_n={eps}={float(eps):.6f} "
              f"(4K^5={4*K0**5})")


# ------------------------------------------- [4] 路线二 4.2 的 K=2 有理矛盾
def section4():
    print("== [4] 路线二 4.2 的 K=2 反例（eta=3/2，精确有理） ==")
    eta, K = R(3, 2), 2
    g0 = 1 / (K * eta)
    do0 = eta * g0
    gap1 = 1 - K * do0 + do0            # f(O*)=1，两个 o 在空集处各 do0，和为 1
    gap1 = 1 - g0
    g1 = gap1 / (K * eta)
    do1 = eta * g1
    f_e0o1 = g0 + do1
    f_o1 = do0
    d_e0_o1 = f_e0o1 - f_o1
    need = R(2, 9)
    print(f"  g0={g0} d_o(empty)={do0} gap1={gap1} g1={g1} d_o({{e0}})={do1}")
    print(f"  f({{e0,o1}})={f_e0o1} f({{o1}})={f_o1} -> d_e0({{o1}})={d_e0_o1}")
    print(f"  band 要求 d_e0({{o1}}) >= {need}；矛盾成立: {d_e0_o1 < need}")


# ------------------------------- [5] 决定性对照 LP：blindness 的作用范围
def grid_lp(K, eta_u, eta_o, X, mode):
    """count grid (x,y) 上的 LP：min F(K,0)。mode 决定 predictor 的盲度范围。"""
    pts = [(x, y) for x in range(X + 1) for y in range(K + 1)]
    idx = {p: i for i, p in enumerate(pts)}
    n = len(pts)
    NV = 2 * n
    Fi = lambda p: idx[p]
    Gi = lambda p: n + idx[p]
    A_ub, b_ub, A_eq, b_eq = [], [], [], []
    row = lambda: [0.0] * NV
    inb = lambda p: 0 <= p[0] <= X and 0 <= p[1] <= K
    E = [(1, 0), (0, 1)]
    for p in pts:
        for e in E:
            qp = (p[0] + e[0], p[1] + e[1])
            if not inb(qp):
                continue
            r = row(); r[Fi(qp)] = -1.0; r[Fi(p)] = 1.0
            A_ub.append(r); b_ub.append(0.0)                                  # monotone
            r = row(); r[Fi(qp)] = 1.0 / eta_u; r[Fi(p)] = -1.0 / eta_u
            r[Gi(qp)] += -1.0; r[Gi(p)] += 1.0
            A_ub.append(r); b_ub.append(0.0)                                  # band lower
            r = row(); r[Gi(qp)] = 1.0; r[Gi(p)] = -1.0
            r[Fi(qp)] += -eta_o; r[Fi(p)] += eta_o
            A_ub.append(r); b_ub.append(0.0)                                  # band upper
            for e2 in E:                                                      # grid DR
                p2 = (p[0] + e2[0], p[1] + e2[1])
                q2 = (qp[0] + e2[0], qp[1] + e2[1])
                if not (inb(p2) and inb(q2)):
                    continue
                r = row()
                r[Fi(q2)] += 1.0; r[Fi(p2)] += -1.0; r[Fi(qp)] += -1.0; r[Fi(p)] += 1.0
                A_ub.append(r); b_ub.append(0.0)
    r = row(); r[Fi((0, 0))] = 1.0; A_eq.append(r); b_eq.append(0.0)
    r = row(); r[Gi((0, 0))] = 1.0; A_eq.append(r); b_eq.append(0.0)
    cls = {}
    for (x, y) in pts:
        if mode == "count":
            k = ("s", x + y)
        elif mode == "tau2":      # 路线二的 (*)：|S∩O|<=1 的一切集合，无 size 上限
            k = ("s", x + y) if y <= 1 else ("f", x, y)
        elif mode == "tau3":
            k = ("s", x + y) if y <= 2 else ("f", x, y)
        elif mode == "small":     # 路线一：只在 |S|<=K 且 |S∩O|<=1 上要求盲
            k = ("s", x + y) if (y <= 1 and x + y <= K) else ("f", x, y)
        cls.setdefault(k, []).append((x, y))
    for k, lst in cls.items():
        if k[0] == "f":
            continue
        for a, b in zip(lst, lst[1:]):
            r = row(); r[Gi(a)] = 1.0; r[Gi(b)] = -1.0
            A_eq.append(r); b_eq.append(0.0)
    r = row(); r[Fi((0, K))] = 1.0; A_eq.append(r); b_eq.append(1.0)
    for a in range(K + 1):
        r = row(); r[Fi((a, K - a))] = 1.0; A_ub.append(r); b_ub.append(1.0)
    c = [0.0] * NV
    c[Fi((K, 0))] = 1.0
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)] * NV, method="highs")
    return res.fun if res.success else None


def section5():
    print("== [5] blindness 作用范围的对照 LP（eta=3/2，float 只用于求解与打印） ==")
    eta = 1.5
    for K in (2, 3, 4):
        _, _, V = V_list(K, R(3, 2))
        rho = min(V)
        print(f"  K={K}  rho_K={rho}={float(rho):.9f}")
        for mode in ("count", "tau3", "tau2", "small"):
            vals = [(X, grid_lp(K, 1.0, eta, X, mode)) for X in (4, 6, 8, 14)]
            txt = "  ".join(f"X={X}:{v:.9f}" for X, v in vals)
            print(f"     mode={mode:6s} {txt}")


# ------------------- [6] D2：用路线二自己的 LP 复跑 count-grid f 下的 per-T
def section6():
    print("== [6] 路线二自身 LP：count-grid f + 全 size 1-blind 的 per-T（D2） ==")
    import sys
    sys.path.insert(0, "/home/user/sub-modular-optimization/results/V11/route2")
    try:
        from q6_route2_lp_hard import lp
    except Exception as exc:                      # pragma: no cover
        print("  跳过（无法 import 路线二脚本）:", exc)
        return
    eta = 1.5
    for K, m, opt, T in [(2, 6, (4, 5), (0, 1)), (2, 7, (5, 6), (0, 1)),
                         (3, 7, (4, 5, 6), (0, 1, 2))]:
        per = lp(m, K, 1.0, eta, opt, mode="blind", tau=2, objective="per",
                 T_fixed=T, fgrid=True)
        allT = lp(m, K, 1.0, eta, opt, mode="blind", tau=2, objective="all", fgrid=True)
        avg = lp(m, K, 1.0, eta, opt, mode="blind", tau=2, objective="avg", fgrid=True)
        print(f"  K={K} m={m}: per-T {per:.9f}  all-T {allT:.9f}  avg-T {avg:.9f}")


if __name__ == "__main__":
    section1()
    section2()
    section3()
    section4()
    section5()
    section6()
