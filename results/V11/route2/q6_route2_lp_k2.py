"""ROUTE-TWO (Q6) part 2: predictive greedy 在 K=2 上的精确最坏比 (exact rational LP).

问 : 固定 split (eta_u, eta_o), 在 |N| = m 的所有实例 (f monotone submodular,
ft 任意集合函数, band 成立, greedy 轨迹 e_0=0, e_1=1, O* 为指定 2-set) 上,
min f({0,1}) / f(O*) 是多少?

这是一个精确有理 LP: 固定 split 后所有约束对 (f, ft) 的取值都是线性的.
用 sympy.solvers.simplex.lpmin (exact rational simplex).

对比对象: min_j V_j(eta) (= rho_K 的公式) 与 L_K(eta) (guarantee curve).
"""
import itertools
import sys
from fractions import Fraction as F

import sympy as sp
from sympy.solvers.simplex import lpmin


def subsets(m):
    for r in range(m + 1):
        for c in itertools.combinations(range(m), r):
            yield frozenset(c)


def worst_case(m, eta_u, eta_o, opt, traj=(0, 1), extra_sym=False):
    """min f(traj) s.t. f(opt)=1 and all constraints. Returns Fraction."""
    eta_u, eta_o = sp.Rational(eta_u), sp.Rational(eta_o)
    S = list(subsets(m))
    fv = {s: sp.Symbol(f"f_{sorted(s)}", nonnegative=True) for s in S}
    gv = {s: sp.Symbol(f"g_{sorted(s)}", nonnegative=True) for s in S}  # g = tilde f
    C = [sp.Eq(fv[frozenset()], 0), sp.Eq(gv[frozenset()], 0)]

    for s in S:
        rest = [e for e in range(m) if e not in s]
        for e in rest:
            d = fv[s | {e}] - fv[s]
            dt = gv[s | {e}] - gv[s]
            C.append(d >= 0)                     # monotone
            C.append(dt >= d / eta_u)            # band, lower
            C.append(dt <= eta_o * d)            # band, upper
        for e, e2 in itertools.combinations(rest, 2):   # submodular (local exchange)
            C.append(fv[s | {e}] + fv[s | {e2}] >= fv[s | {e, e2}] + fv[s])

    # greedy with adversarial ties: at state S^t the picked element maximises tilde d
    e0, e1 = traj
    for e in range(m):
        if e != e0:
            C.append(gv[frozenset({e0})] >= gv[frozenset({e})])
    for e in range(m):
        if e not in (e0, e1):
            C.append(gv[frozenset({e0, e1})] - gv[frozenset({e0})]
                     >= gv[frozenset({e0, e})] - gv[frozenset({e0})])

    # O* optimal among 2-sets, normalised to 1
    C.append(sp.Eq(fv[frozenset(opt)], 1))
    for c in itertools.combinations(range(m), 2):
        C.append(fv[frozenset(c)] <= 1)

    if extra_sym:
        # tilde f 只依赖 |S| (count-only symmetric predictor)
        by_size = {}
        for s in S:
            by_size.setdefault(len(s), []).append(s)
        for _, lst in by_size.items():
            for a, b in zip(lst, lst[1:]):
                C.append(sp.Eq(gv[a], gv[b]))

    val, _ = lpmin(fv[frozenset(traj)], C)
    return val


def main():
    eta = F(3, 2)
    splits = [(1, eta), (eta, 1)]
    for m in (4, 5):
        for (eu, eo) in splits:
            best = None
            for opt in itertools.combinations(range(m), 2):
                v = worst_case(m, eu, eo, opt)
                best = v if best is None else min(best, v)
            print(f"m={m}  split=({eu},{eo})  min over O*: {best} = {float(best):.6f}")
            sys.stdout.flush()
    # count-only symmetric predictor (hardness-relevant variant), m=5
    for (eu, eo) in splits:
        best = None
        for opt in itertools.combinations(range(5), 2):
            v = worst_case(5, eu, eo, opt, extra_sym=True)
            best = v if best is None else min(best, v)
        print(f"m=5  split=({eu},{eo})  count-only predictor: {best} = {float(best):.6f}")


if __name__ == "__main__":
    main()
