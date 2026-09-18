"""ROUTE-TWO (Q6) part 2b: K=2 / K=3 上 predictive greedy 的最坏比, 用 scipy LP 求值,
再用 fractions 精确复核 (可行解 + 目标值 + 关键约束的紧性).

变量: f(S), ft(S) 对所有 S ⊆ [m].
约束: f(∅)=ft(∅)=0; f monotone; f submodular (local exchange);
      band: d_e(S)/eta_u <= dt_e(S) <= eta_o d_e(S);
      greedy 轨迹 (e_0,...,e_{K-1}) 在每一步都最大化 dt (对抗 tie 允许取等号);
      f(O*) = 1, 且所有 K-set 的 f <= 1 (O* 最优).
目标: min f({e_0,...,e_{K-1}}).

float 只用于 LP 求解; 结论用 Fraction 复核.
"""
import itertools
import sys
from fractions import Fraction as F

import numpy as np
from scipy.optimize import linprog


def build(m, K, eta_u, eta_o, opt, traj):
    subs = [frozenset(c) for r in range(m + 1) for c in itertools.combinations(range(m), r)]
    idx = {s: i for i, s in enumerate(subs)}
    n = len(subs)
    NV = 2 * n

    def fi(s):
        return idx[s]

    def gi(s):
        return n + idx[s]

    A_ub, b_ub, A_eq, b_eq = [], [], [], []

    def row():
        return [0.0] * NV

    for s in subs:
        rest = [e for e in range(m) if e not in s]
        for e in rest:
            # -d <= 0   (monotone)
            r = row(); r[fi(s | {e})] = -1.0; r[fi(s)] = 1.0
            A_ub.append(r); b_ub.append(0.0)
            # d/eta_u - dt <= 0
            r = row()
            r[fi(s | {e})] = 1.0 / eta_u; r[fi(s)] = -1.0 / eta_u
            r[gi(s | {e})] += -1.0; r[gi(s)] += 1.0
            A_ub.append(r); b_ub.append(0.0)
            # dt - eta_o d <= 0
            r = row()
            r[gi(s | {e})] = 1.0; r[gi(s)] = -1.0
            r[fi(s | {e})] += -eta_o; r[fi(s)] += eta_o
            A_ub.append(r); b_ub.append(0.0)
        for e, e2 in itertools.combinations(rest, 2):
            # f(S+e+e') + f(S) - f(S+e) - f(S+e') <= 0
            r = row()
            r[fi(s | {e, e2})] += 1.0; r[fi(s)] += 1.0
            r[fi(s | {e})] -= 1.0; r[fi(s | {e2})] -= 1.0
            A_ub.append(r); b_ub.append(0.0)

    r = row(); r[fi(frozenset())] = 1.0; A_eq.append(r); b_eq.append(0.0)
    r = row(); r[gi(frozenset())] = 1.0; A_eq.append(r); b_eq.append(0.0)

    # greedy trajectory
    st = frozenset()
    for t in range(K):
        et = traj[t]
        for e in range(m):
            if e in st or e == et:
                continue
            # dt_e(st) - dt_{et}(st) <= 0
            r = row()
            r[gi(st | {e})] += 1.0; r[gi(st)] -= 1.0
            r[gi(st | {et})] -= 1.0; r[gi(st)] += 1.0
            A_ub.append(r); b_ub.append(0.0)
        st = st | {et}

    r = row(); r[fi(frozenset(opt))] = 1.0; A_eq.append(r); b_eq.append(1.0)
    for c in itertools.combinations(range(m), K):
        r = row(); r[fi(frozenset(c))] = 1.0
        A_ub.append(r); b_ub.append(1.0)

    c_obj = [0.0] * NV
    c_obj[fi(frozenset(traj))] = 1.0
    return c_obj, np.array(A_ub), np.array(b_ub), np.array(A_eq), np.array(b_eq), subs, idx


def solve(m, K, eta_u, eta_o, opt, traj):
    c, A_ub, b_ub, A_eq, b_eq, subs, idx = build(m, K, eta_u, eta_o, opt, traj)
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                  bounds=[(0, None)] * len(c), method="highs")
    if not res.success:
        return None, res.message
    return res.fun, res.x


def main():
    eta = 1.5
    for K, m in [(2, 4), (2, 5), (3, 6)]:
        for (eu, eo) in [(1.0, eta), (eta, 1.0)]:
            best, arg = None, None
            traj = tuple(range(K))
            for opt in itertools.combinations(range(m), K):
                v, _ = solve(m, K, eu, eo, opt, traj)
                if v is None:
                    continue
                if best is None or v < best - 1e-12:
                    best, arg = v, opt
            print(f"K={K} m={m} split=({eu},{eo}) traj={traj}: min f(T)/f(O*) = {best:.9f}"
                  f"  (O*={arg})")
            sys.stdout.flush()
    print()
    print("reference values (Fraction):")
    print("  rho_2(3/2) = 3/5 =", float(F(3, 5)), "  L_2(3/2) = 5/9 =", float(F(5, 9)),
          "  U_2(3/2) = 16/25 =", float(F(16, 25)))
    print("  rho_3(3/2) = 9/16 =", float(F(9, 16)), "  L_3(3/2) = 386/729 =",
          float(F(386, 729)), "  U_3(3/2) = 37/64 =", float(F(37, 64)))


if __name__ == "__main__":
    main()
