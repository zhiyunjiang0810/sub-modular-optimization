#!/usr/bin/env python3
"""V11 ROUTE-COMPARISON judge checks for thm:exact (ledger T6).

Independent re-verification, by the comparison judge, of BOTH routes:

  route one : paper/sections/appendix_proofs.tex, app:exact (dual multipliers
              eq:duals-jpos / eq:duals-jzero, attaining family eq:vj-family)
              and app:validity (four constraint families).
  route two : results/V11/route2/exact.md (aggregate LP (P), dual (D) with
              multipliers z/w/y, coverage attaining instance with predictor
              ftilde = f - (1 - 1/eta) max_i mu(A_{o_i} cap C(S))).

Nothing in this file is imported from either route's own scripts: every object
is re-implemented from the write-ups.  Exact arithmetic only (sympy symbolic in
eta, fractions.Fraction for instances); floats appear in the last block, which
is a cross-check printout and carries no decision.

Run:  python3 results/V11/compare/judge_exact_checks.py
Blocks and status tags (CLAUDE.md):
  B1 route-two dual certificate, K = 2..7, all j, symbolic eta [VERIFIED-SYMBOLIC]
  B2 route-one dual certificate, K = 2..7, all j, symbolic eta [VERIFIED-SYMBOLIC]
  B3 segment structure / closed forms, K = 2..8, symbolic eta [VERIFIED-SYMBOLIC]
  B4 route-two attaining instance, K = 2..5, exhaustive over all (S,e) [VERIFIED-EXHAUSTIVE]
  B5 route-one attaining instance, K = 2..4, exhaustive, on and off segment [VERIFIED-EXHAUSTIVE]
  B6 route-two LP primal point, K = 2..8, exact rational feasibility [VERIFIED-EXHAUSTIVE]
  B7 LP variants (sum+pred+mono vs sum+cons+mono vs all four), HiGHS floats [VERIFIED-LP, cross-check only]
"""
from fractions import Fraction as F
from itertools import combinations

import sympy as sp

ETA = sp.Symbol("eta", positive=True)


# --------------------------------------------------------------------------
# shared symbols
# --------------------------------------------------------------------------
def k1q(K):
    k1 = (K - 1) * ETA + 1
    return k1, (K - 1) * ETA / k1


def Vj_sym(K, j):
    k1, q = k1q(K)
    return 1 - q ** j * (1 - sp.Rational(K - j, 1) / (K * ETA))


def segment(K, j):
    return (K - j, None if j == 0 else K - j + 1)


def nonneg_on_segment(expr, K, j):
    """True iff expr >= 0 for every eta in the segment of j (exact)."""
    e = sp.cancel(sp.together(sp.simplify(expr)))
    if e == 0:
        return True
    lo, hi = segment(K, j)
    num, den = sp.fraction(e)
    probe = sp.Rational(2 * lo + 1, 2)
    if sp.simplify(den.subs(ETA, probe)) < 0:
        num, den = -num, -den
    s = sp.Symbol("s", nonnegative=True)
    if hi is None:
        try:
            pn = sp.Poly(sp.expand(num.subs(ETA, lo + s)), s)
            pd = sp.Poly(sp.expand(den.subs(ETA, lo + s)), s)
            if all(c >= 0 for c in pn.all_coeffs()) and all(c >= 0 for c in pd.all_coeffs()):
                return True
        except sp.PolynomialError:
            pass
        return bool(sp.simplify(sp.minimum(e, ETA, sp.Interval(lo, sp.oo))) >= 0)
    return bool(sp.simplify(sp.minimum(e, ETA, sp.Interval(lo, hi))) >= 0)


# --------------------------------------------------------------------------
# B1  route two: aggregate LP (P) and its dual (D)
# --------------------------------------------------------------------------
def route2_multipliers(K, j):
    k1, q = k1q(K)
    th = 1 - 1 / ETA
    z = {t: sp.Rational(1, K) for t in range(j, K)}
    if j >= 1:
        zjm1 = (K * ETA - K + j) / (K * k1)
        z[j - 1] = sp.simplify(zjm1)
        for t in range(0, j - 1):
            z[t] = sp.simplify(q ** (j - 1 - t) * zjm1)
    w = {t: (sp.Integer(0) if t < j else sp.simplify(th / K - sp.Rational(K - 1 - t, 1) / (K * ETA)))
         for t in range(K)}
    y = {}
    for t in range(K):
        ztm1 = z[t - 1] if t >= 1 else sp.Integer(0)
        wtm1 = w[t - 1] if t >= 1 else sp.Integer(0)
        y[t] = sp.simplify(z[t] - th * ztm1 - w[t] + wtm1)
    return z, w, y, th


def block1(Kmax=7):
    rep = []
    for K in range(2, Kmax + 1):
        for j in range(K):
            z, w, y, th = route2_multipliers(K, j)
            for t in range(K):
                rep.append(nonneg_on_segment(z[t], K, j))
                rep.append(nonneg_on_segment(w[t], K, j))
                rep.append(nonneg_on_segment(y[t], K, j))
                rep.append(nonneg_on_segment(1 - (sum(y[u] for u in range(t + 1, K)) + K * z[t]), K, j))
                ztm1 = z[t - 1] if t >= 1 else sp.Integer(0)
                wtm1 = w[t - 1] if t >= 1 else sp.Integer(0)
                rep.append(sp.simplify(y[t] - z[t] + th * ztm1 + w[t] - wtm1) == 0)
            rep.append(nonneg_on_segment(w[K - 1] - th * z[K - 1], K, j))
            rep.append(sp.simplify(sum(y.values()) - Vj_sym(K, j)) == 0)
    return rep


# --------------------------------------------------------------------------
# B2  route one: eq:duals-jpos / eq:duals-jzero against eq:redlp
# --------------------------------------------------------------------------
def route1_multipliers(K, j):
    k1, q = k1q(K)
    M = K * ETA - (K - j)
    lS = {t: sp.Integer(0) for t in range(K + 1)}
    lP = {t: sp.Integer(0) for t in range(K + 1)}
    lC = {t: sp.Integer(0) for t in range(-1, K + 1)}
    if j >= 1:
        lS[0] = q ** (j - 1) * M / (K * k1)
        for t in range(1, j):
            lS[t] = q ** (j - 1 - t) * M / k1 ** 2
        lS[j] = (K - j + 1 - ETA) / k1
        for t in range(j):
            lC[t] = q ** (j - 1 - t) * M / (K * k1)
    else:
        lS[0] = 1 / ETA
    for t in range(j, K):
        lC[t] = sp.Integer(0) if K - 1 - t == 0 else sp.Rational(K - 1 - t, 1) / (K * (ETA - 1))
        lP[t] = sp.Rational(1, K) if (j == K - 1 and t == K - 1) else (ETA - (K - t)) / (K * (ETA - 1))
    return lS, lP, lC


def block2(Kmax=7):
    rep = []
    for K in range(2, Kmax + 1):
        for j in range(K):
            lS, lP, lC = route1_multipliers(K, j)
            d = sp.symbols(f"d0:{K}")
            g = sp.Matrix(K + 1, K, lambda a, b: sp.Symbol(f"g{a}_{b}"))
            Sig = 0
            for t in range(j + 1):
                Sig += lS[t] * (sum(g[t, i] for i in range(K)) + sum(d[s] for s in range(t)) - 1)
            for t in range(j, K):
                for i in range(K):
                    Sig += lP[t] * (d[t] - g[t, i] / ETA)
            for t in range(K):
                for i in range(K):
                    Sig += lC[t] * ((1 - 1 / ETA) * g[t + 1, i] - g[t, i] + d[t])
            rep.append(sp.simplify(sp.expand(Sig - (sum(d) - Vj_sym(K, j)))) == 0)
            for t in range(K + 1):
                for lam in (lS[t], lP[t], lC[t]):
                    rep.append(nonneg_on_segment(lam, K, j))
    return rep


# --------------------------------------------------------------------------
# B3  segment structure and closed forms
# --------------------------------------------------------------------------
def block3(Kmax=8):
    rep = []
    for K in range(2, Kmax + 1):
        k1, q = k1q(K)
        c = lambda j: q ** j * (1 - sp.Rational(K - j, 1) / (K * ETA))
        for i in range(K - 1):
            rep.append(sp.simplify(sp.together(Vj_sym(K, i) - Vj_sym(K, i + 1)
                                               - q ** i * (K - i - ETA) / (K * ETA * k1))) == 0)
            ratio = sp.cancel(sp.simplify((c(i + 1) - c(i)) / (K - i - ETA)))
            num, den = sp.fraction(ratio)
            s = sp.Symbol("s", nonnegative=True)
            pn = sp.Poly(sp.expand(num.subs(ETA, 1 + s)), s)
            pd = sp.Poly(sp.expand(den.subs(ETA, 1 + s)), s)
            rep.append(all(cc >= 0 for cc in pn.all_coeffs()) and all(cc >= 0 for cc in pd.all_coeffs())
                       and sp.simplify(ratio.subs(ETA, 1)) > 0)
        VK = 1 - q ** K
        rep.append(sp.simplify(VK - Vj_sym(K, K - 1) - q ** (K - 1) * (1 / k1 - 1 / (K * ETA))) == 0)
        rep.append(sp.simplify(Vj_sym(K, 0) - 1 / ETA) == 0)
    forms = {2: {1: sp.Rational(3, 2) / (ETA + 1)},
             3: {2: (16 * ETA + 3) / (3 * (2 * ETA + 1) ** 2), 1: sp.Rational(7, 3) / (2 * ETA + 1)},
             4: {3: (135 * ETA ** 2 + 36 * ETA + 4) / (4 * (3 * ETA + 1) ** 3),
                 2: (21 * ETA + 2) / (2 * (3 * ETA + 1) ** 2), 1: sp.Rational(13, 4) / (3 * ETA + 1)}}
    for K, fs in forms.items():
        for j, form in fs.items():
            rep.append(sp.simplify(Vj_sym(K, j) - form) == 0)
    return rep


# --------------------------------------------------------------------------
# B4  route two's attaining instance (coverage f, ftilde = f - (1-1/eta) beta)
# --------------------------------------------------------------------------
def r2_instance(K, j, eta):
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    R = [F(1)]
    g = []
    for t in range(K):
        gt = R[t] / k1 if t < j else R[j] / (K * eta)
        g.append(gt)
        R.append(R[t] - gt)
    Rj = R[j]
    opts = list(range(K, 2 * K))
    atoms = {}
    for i in range(K):
        for s in range(j):
            atoms[("h", i, s)] = (g[s] / K, frozenset({opts[i], s}))
        atoms[("inf", i)] = (Rj / K, frozenset({opts[i]}))
    for t in range(j, K):
        atoms[("tau", t)] = (g[t], frozenset({t}))
    return dict(K=K, j=j, eta=eta, q=q, g=g, opts=opts, atoms=atoms, n=2 * K)


def r2_check(K, j, eta):
    inst = r2_instance(K, j, eta)
    n, atoms, opts = inst["n"], inst["atoms"], inst["opts"]
    th = 1 - F(1) / eta
    allS = [frozenset(c) for r in range(n + 1) for c in combinations(range(n), r)]

    def f(S):
        return sum(m for (m, cov) in atoms.values() if cov & S)

    def beta(S):
        best = F(0)
        for oi in opts:
            best = max(best, sum(m for (_, (m, cov)) in atoms.items() if oi in cov and (cov & S)))
        return best

    fc = {S: f(S) for S in allS}
    ftc = {S: fc[S] - th * beta(S) for S in allS}
    fails = []
    if fc[frozenset()] != 0 or ftc[frozenset()] != 0:
        fails.append("norm")
    for S in allS:
        for e in range(n):
            if e in S:
                continue
            d, dt = fc[S | {e}] - fc[S], ftc[S | {e}] - ftc[S]
            if d < 0:
                fails.append(("mono", e))
            if not (d / eta <= dt <= d):
                fails.append(("band", e))
            if d == 0 and dt != 0:
                fails.append(("zeropres", e))
            for x in range(n):
                if x in S or x == e:
                    continue
                if d < fc[S | {e, x}] - fc[S | {x}]:
                    fails.append(("submod", e, x))
    if fc[frozenset(opts)] != 1 or max(fc[frozenset(c)] for c in combinations(range(n), K)) != 1:
        fails.append("FOPT")
    S = frozenset()
    for t in range(K):
        gains = {e: ftc[S | {e}] - ftc[S] for e in range(n) if e not in S}
        mx = max(gains.values())
        if gains[t] != mx:
            fails.append(("greedy", t))
            break
        if not set(opts) <= {e for e in gains if gains[e] == mx}:
            fails.append(("tie-not-full", t))
        S = S | {t}
    V = 1 - inst["q"] ** j * (1 - F(K - j, 1) / (K * eta))
    if len(S) == K and fc[S] != V:
        fails.append(("FALG", fc[S], V))
    return fails


def block4():
    etas = [F(1), F(5, 4), F(3, 2), F(2), F(9, 4), F(5, 2), F(3), F(7, 2), F(4), F(9, 2), F(5), F(6)]
    rep, off = [], []
    for K in (2, 3, 4):
        for j in range(K):
            for eta in etas:
                fl = r2_check(K, j, eta)
                rep.append(not fl)
                if eta < K - j:
                    off.append(not fl)
    for j in range(5):
        for eta in [F(1), F(3, 2), F(2), F(5, 2), F(3), F(4), F(5), F(6)]:
            if eta < 5 - j:
                continue
            rep.append(not r2_check(5, j, eta))
    return rep, off


# --------------------------------------------------------------------------
# B5  route one's attaining family eq:vj-family, split (eta_u, eta_o) = (eta, 1)
# --------------------------------------------------------------------------
def r1_check(K, j, eta, eta_u=None, eta_o=F(1)):
    eta_u = eta if eta_u is None else eta_u
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    dj = q ** j / (K * eta)
    W0 = k1 / (K * eta_u)
    n = 2 * K
    C, P, O = set(range(j)), set(range(j, K)), set(range(K, 2 * K))

    def W(y):
        return W0 if y == 0 else (K - y) * eta_o / F(K)

    def counts(S):
        return len(S & C), len(S & P), len(S & O)

    def f(S):
        x, z, y = counts(S)
        return 1 - q ** x * (1 - F(y, K)) + z * dj * (1 if y < K else 0)

    def ft(S):
        x, z, y = counts(S)
        return W0 - q ** x * W(y) + z * eta_o * dj * (1 if y < K else 0)

    allS = [frozenset(c) for r in range(n + 1) for c in combinations(range(n), r)]
    fc, ftc = {S: f(S) for S in allS}, {S: ft(S) for S in allS}
    fails = []
    for S in allS:
        for e in range(n):
            if e in S:
                continue
            d, dt = fc[S | {e}] - fc[S], ftc[S | {e}] - ftc[S]
            if d < 0:
                fails.append("mono")
            if not (d / eta_u <= dt <= eta_o * d):
                fails.append("band")
            for x in range(n):
                if x in S or x == e:
                    continue
                if d < fc[S | {e, x}] - fc[S | {x}]:
                    fails.append("submod")
    if fc[frozenset(O)] != 1 or max(fc[frozenset(c)] for c in combinations(range(n), K)) != 1:
        fails.append("FOPT")
    S = frozenset()
    for t in range(K):
        gains = {e: ftc[S | {e}] - ftc[S] for e in range(n) if e not in S}
        if gains[t] != max(gains.values()):
            fails.append("greedy")
            break
        S = S | {t}
    V = 1 - q ** j * (1 - F(K - j, 1) / (K * eta))
    if len(S) == K and fc[S] != V:
        fails.append("FALG")
    return sorted(set(fails))


def block5():
    on, off = [], []
    for K in (2, 3, 4):
        for j in range(K):
            for eta in [F(1), F(3, 2), F(2), F(5, 2), F(3), F(4), F(5)]:
                fl = r1_check(K, j, eta)
                (on if eta >= K - j else off).append((K, j, eta, fl))
    return on, off


# --------------------------------------------------------------------------
# B6  route two's trajectory point is exactly feasible for (P) with value V_j
# --------------------------------------------------------------------------
def block6(Kmax=8):
    rep = []
    for K in range(2, Kmax + 1):
        for j in range(K):
            for eta in [F(1), F(5, 4), F(3, 2), F(2), F(5, 2), F(3), F(4), F(11, 2), F(9)]:
                k1 = (K - 1) * eta + 1
                q = (K - 1) * eta / k1
                th = 1 - F(1) / eta
                R, g = [F(1)], []
                for t in range(K):
                    gt = R[t] / k1 if t < j else R[j] / (K * eta)
                    g.append(gt)
                    R.append(R[t] - gt)
                P = [R[t] if t <= j else R[j] for t in range(K + 1)]
                ok = all(sum(g[s] for s in range(t)) + P[t] - 1 >= 0
                         and K * g[t] + th * P[t + 1] - P[t] >= 0
                         and P[t] - P[t + 1] >= 0 for t in range(K))
                V = 1 - q ** j * (1 - F(K - j, 1) / (K * eta))
                rep.append(ok and sum(g) == V)
    return rep


# --------------------------------------------------------------------------
# B7  LP variants (floats, cross-check printout only)
# --------------------------------------------------------------------------
def block7():
    import numpy as np
    from scipy.optimize import linprog

    def lp(K, eta, pred=True, cons=True, mono=True):
        th = 1 - 1 / eta
        nv = 2 * K + 1
        c = np.zeros(nv)
        c[:K] = 1
        A, b = [], []
        for t in range(K):
            r = np.zeros(nv); r[:t] = -1; r[K + t] = -1; A.append(r); b.append(-1)
        if pred:
            for t in range(K):
                r = np.zeros(nv); r[t] = -K * eta; r[K + t] = 1; A.append(r); b.append(0)
        if cons:
            for t in range(K):
                r = np.zeros(nv); r[t] = -K; r[K + t + 1] = -th; r[K + t] = 1; A.append(r); b.append(0)
        if mono:
            for t in range(K):
                r = np.zeros(nv); r[K + t] = -1; r[K + t + 1] = 1; A.append(r); b.append(0)
        return linprog(c, A_ub=np.array(A), b_ub=np.array(b), bounds=[(0, None)] * nv,
                       method="highs").fun

    out = []
    for K in (2, 3, 4, 5):
        for eta in (1.0, 1.5, 2.0, 3.0, 4.5):
            k1 = (K - 1) * eta + 1
            q = (K - 1) * eta / k1
            rho = min(1 - q ** j * (1 - (K - j) / (K * eta)) for j in range(K))
            LK = 1 - (1 - 1 / (K * eta)) ** K
            out.append((K, eta, lp(K, eta, cons=False), LK, lp(K, eta, pred=False), rho, lp(K, eta)))
    return out


if __name__ == "__main__":
    r = block1(); print(f"B1 route-two dual : {len(r)} checks, {r.count(False)} failures")
    r = block2(); print(f"B2 route-one dual : {len(r)} checks, {r.count(False)} failures")
    r = block3(); print(f"B3 segments/forms : {len(r)} checks, {r.count(False)} failures")
    r, off = block4()
    print(f"B4 route-two inst : {len(r)} cases, {r.count(False)} failures "
          f"({len(off)} of them with eta < K-j, {off.count(False)} failures)")
    on, offc = block5()
    print(f"B5 route-one inst : on-segment {len(on)} cases, "
          f"{sum(1 for x in on if x[3])} failures; off-segment {len(offc)} cases, "
          f"{sum(1 for x in offc if x[3])} failures (expected: all off-segment fail)")
    for x in offc[:4]:
        print("   off-segment example", x)
    r = block6(); print(f"B6 primal point   : {len(r)} cases, {r.count(False)} failures")
    print("B7 LP variants (floats, cross-check only):")
    print("   K  eta   sum+pred+mono     L_K      sum+cons+mono    rho_K     all four")
    for (K, eta, a, LK, b, rho, c) in block7():
        print(f"   {K}  {eta:<4} {a:.9f}  {LK:.9f}  {b:.9f}  {rho:.9f}  {c:.9f}")
