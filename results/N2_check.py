#!/usr/bin/env python3
"""N2: explicit worst-case instances (f, ftilde) attaining V_j(eta) for every j.

For every K >= 2 and every 0 <= j <= K this file builds an explicit pair
(f, ftilde) on n = 2K elements whose single-step predictive greedy run (ties
broken adversarially) has ratio exactly

    V_j(eta) = 1 - q^j (1 - (K-j)/(K eta)),   k1 = (K-1) eta + 1,
                                              q  = (K-1) eta / k1 = 1 - 1/k1.

On the segment eta in [K-j, K-j+1] this V_j is min_i V_i (RESEARCH_STATE R10,
results/N1_dual_certificate.md), so the family attains the reduced-LP closed
form on every segment.  j = 0 is the modular R2 instance (value 1/eta) and
j = K is the R7 instance of the paper (value U_K); the middle j are new.

Ground set  N = C u P u O,  |C| = j, |P| = K-j, |O| = K.
Element order (matches code/worst_case_lp.py: greedy picks 0..K-1 in order):
    0 .. j-1  : C ("coherence" steps)   j .. K-1 : P ("prediction" steps)
    K .. 2K-1 : O (the optimum)
Counts of a set S:  x = |S n C|, z = |S n P|, y = |S n O|.

    eta_u eta_o = eta   (any split; the default is eta_u = eta_o = s = sqrt eta)
    delta = q^j / (K eta)        true gain of a P element
    dtil  = eta_o * delta        predicted gain of a P element
    W(0)  = k1 / (K eta_u),      W(y) = (K-y) eta_o / K   for 1 <= y <= K

    f(S)      = 1 - q^x (1 - y/K) + z * delta * chi(y)
    ftilde(S) = W(0) - q^x W(y)  + z * dtil  * chi(y)

with two variants of the cutoff chi:
  capped   (chi(y) = [y < K], the default): matches the LP optimum returned by
           code/worst_case_lp.py; monotone submodular iff eta >= K-j, i.e. on
           the segment of j and to its right;
  uncapped (chi == 1): monotone submodular for every eta >= 1, no side
           condition, same value V_j(eta).  Simpler; the j=0 member is then
           literally the modular instance of R2.

Claims verified below (see results/N2_instances.md):
  (C1) f monotone submodular, f(empty) = ftilde(empty) = 0;
  (C2) single-element AND all-pairs errors are exactly (eta_u, eta_o): every
       ratio lies in [1/eta_u, eta_o] and both ends are attained;
  (C3) OPT = max_{|S|<=K} f(S) = f(O) = 1;
  (C4) predictive greedy on ftilde, ties broken adversarially, picks C then P,
       i.e. exactly 0,1,...,K-1 (every step is a tie against the O elements);
  (C5) f(greedy output) / OPT = V_j(eta) exactly;
  (C6) the value equals the reduced LP (code/reduced_lp.py) and, for K<=3, the
       full-lattice LP (code/worst_case_lp.py), and reproduces the R5 table.

Usage:  python3 results/N2_check.py               (all parts, ~20 s)
        N2_FULLLP=0 python3 results/N2_check.py   (skip the 2^{2K} LP part)
        N2_KMAX_FULL=5 / N2_KMAX_EXACT=6 ...      (smaller sweeps)
Exit code 0 iff every check PASSes.
"""
import json
import os
import sys
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'code'))

RESULTS = []          # (part, name, ok, info)


def rec(part, name, ok, info=""):
    RESULTS.append((part, name, bool(ok), info))
    if not ok:
        print(f'   FAIL [{part}] {name}: {info[:300]}', flush=True)
    return bool(ok)


# ----------------------------------------------------------------------------
# Part 0: the closed-form instance as a function of the counts (x, z, y).
# `s` may be a float or a Fraction; arithmetic stays in that type.
# ----------------------------------------------------------------------------
class Instance:
    """s   = build parameter (f is built from eta = s^2),
       sb  = band parameter  (the declared error is eta_u = eta_o = sb).
    sb = s (default) gives the tight instance, whose greedy has ties at every
    step; sb > s gives the strict variant of section 4 of N2_instances.md,
    with value V_j(s^2) < V_j(sb^2) and strictly-preferred greedy picks."""

    def __init__(self, K, j, s, sb=None, eu=None, eo=None, capped=True):
        assert 0 <= j <= K and K >= 2   # j=K is allowed: it is the R7 instance
        self.capped = capped
        one = 1.0 if isinstance(s, float) else Fr(1)
        sb = s if sb is None else sb
        # band split: eta_u * eta_o = sb^2 ; default the symmetric R5 split
        eu = sb if eu is None else eu
        eo = sb if eo is None else eo
        self.K, self.j, self.s, self.sb = K, j, s, sb
        self.eu, self.eo = eu, eo
        self.eta = s * s
        self.eta_b = eu * eo
        self.k1 = (K - 1) * self.eta + one
        self.k1b = (K - 1) * self.eta_b + one
        self.q = (K - 1) * self.eta / self.k1
        self.qj = self.q ** j
        self.delta = self.qj / (K * self.eta)
        self.dtil = eo * self.delta
        self.W0 = self.k1b / (K * eu)
        self.one = one

    def W(self, y):
        return self.W0 if y == 0 else (self.K - y) * self.eo / self.K

    def f(self, x, z, y):
        K = self.K
        v = self.one - self.q ** x * (K - y) / K
        if y < K or not self.capped:
            v = v + z * self.delta
        return v

    def g(self, x, z, y):
        v = self.W0 - self.q ** x * self.W(y)
        if y < self.K or not self.capped:
            v = v + z * self.dtil
        return v

    def V(self):
        K, j = self.K, self.j
        return self.one - self.qj * (self.one - (K - j) / (K * self.eta))


def Vj(K, j, eta):
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return 1 - q ** j * (1 - (K - j) / (K * eta))


def UK(K, eta):
    return 1 - (1 - 1 / (eta * (K - 1) + 1)) ** K


def LK(K, eta):
    return 1 - (1 - 1 / (eta * K)) ** K


# ----------------------------------------------------------------------------
# Part 1: check on the lattice of counts (exact when s is a Fraction).
# f, ftilde are symmetric inside each of the three types, so monotonicity /
# submodularity / the error band are equivalent to the corresponding conditions
# on the count lattice.  (Part 2 re-checks everything on the real 2^{2K}
# lattice, so this equivalence is never load-bearing.)
# ----------------------------------------------------------------------------
DIRS = ('C', 'P', 'O')


def _step(state, d):
    x, z, y = state
    return (x + 1, z, y) if d == 'C' else (x, z + 1, y) if d == 'P' else (x, z, y + 1)


def _legal(I, state, d):
    x, z, y = state
    return (x < I.j) if d == 'C' else (z < I.K - I.j) if d == 'P' else (y < I.K)


def count_check(K, j, s, tol=0, tag="", sb=None, eu=None, eo=None, capped=True):
    """All claims, on the count lattice.  tol == 0 -> exact (Fraction) mode."""
    I = Instance(K, j, s, sb, eu, eo, capped)
    eu, eo = I.eu, I.eo
    zero = 0 * s
    one = I.one
    st = [(x, z, y) for x in range(j + 1) for z in range(K - j + 1)
          for y in range(K + 1)]
    fv = {p: I.f(*p) for p in st}
    gv = {p: I.g(*p) for p in st}
    out = {}

    def le(a, b):
        return a <= b + tol

    def eq(a, b):
        return abs(a - b) <= tol

    out['f_empty'] = eq(fv[(0, 0, 0)], zero) and eq(gv[(0, 0, 0)], zero)

    mono = sub = True
    for p in st:
        for d in DIRS:
            if not _legal(I, p, d):
                continue
            if not le(zero, fv[_step(p, d)] - fv[p]):
                mono = False
            for e in DIRS:
                if not _legal(I, p, e):
                    continue
                pe = _step(p, e)
                if not _legal(I, pe, d):
                    continue
                if not le(fv[_step(pe, d)] - fv[pe], fv[_step(p, d)] - fv[p]):
                    sub = False
    out['monotone'] = mono
    out['submodular'] = sub

    band = True
    hit_up = hit_lo = False
    worst_up = worst_lo = zero
    for p in st:
        for d in DIRS:
            if not _legal(I, p, d):
                continue
            pd = _step(p, d)
            df, dg = fv[pd] - fv[p], gv[pd] - gv[p]
            if eq(df, zero):
                if not eq(dg, zero):
                    band = False
                continue
            if dg <= tol:
                band = False
                continue
            if not (le(dg, eo * df) and le(df, eu * dg)):
                band = False
            if eq(dg, eo * df):
                hit_up = True
            if eq(df, eu * dg):
                hit_lo = True
            worst_up = max(worst_up, dg / df)
            worst_lo = max(worst_lo, df / dg)
    out['band'] = band
    out['eta_o_exact'] = hit_up and eq(worst_up, eo)
    out['eta_u_exact'] = hit_lo and eq(worst_lo, eu)

    opt_ok = eq(fv[(0, 0, K)], one)
    for (x, z, y) in st:
        if x + z + y <= K and not le(fv[(x, z, y)], fv[(0, 0, K)]):
            opt_ok = False
    out['opt_is_O'] = opt_ok

    state = (0, 0, 0)
    picks, ties = [], 0
    gok = True
    for t in range(K):
        want = 'C' if t < j else 'P'
        gains = {d: gv[_step(state, d)] - gv[state] for d in DIRS
                 if _legal(I, state, d)}
        best = max(gains.values())
        if not eq(gains[want], best):
            gok = False
            break
        ties += sum(1 for d, v in gains.items() if d != want and eq(v, best))
        picks.append(want)
        state = _step(state, want)
    out['greedy'] = gok and picks == ['C'] * j + ['P'] * (K - j)
    out['greedy_ties'] = ties
    if I.sb != I.s:                      # strict variant: no ties allowed
        out['greedy_strict'] = (ties == 0)
    out['ratio_is_Vj'] = eq(fv[(j, K - j, 0)] / fv[(0, 0, K)], I.V())
    ok = all(v for k, v in out.items() if isinstance(v, bool))
    rec('count', f"K={K} j={j} eta={float(I.eta):.6g} {tag}", ok,
        json.dumps({k: (v if isinstance(v, (bool, int)) else float(v))
                    for k, v in out.items()}))
    return ok, out


# ----------------------------------------------------------------------------
# Part 2: full 2^{2K} lattice (floats).  No symmetry argument used.
# ----------------------------------------------------------------------------
def build_lattice(K, j, eta, eta_band=None, split=None, capped=True):
    eu, eo = (None, None) if split is None else (float(split[0]), float(split[1]))
    I = Instance(K, j, float(eta) ** 0.5,
                 None if eta_band is None else float(eta_band) ** 0.5, eu, eo,
                 capped)
    n = 2 * K
    N = 1 << n
    maskC = (1 << j) - 1
    maskP = ((1 << K) - 1) ^ maskC
    f = np.empty(N)
    g = np.empty(N)
    for S in range(N):
        x = bin(S & maskC).count('1')
        z = bin(S & maskP).count('1')
        y = bin(S >> K).count('1')
        f[S] = I.f(x, z, y)
        g[S] = I.g(x, z, y)
    return I, n, N, f, g


def full_check(K, j, eta, tol=1e-11, all_pairs=True, eta_band=None, tag="",
               split=None, capped=True):
    I, n, N, f, g = build_lattice(K, j, eta, eta_band, split, capped)
    eu, eo = I.eu, I.eo
    out = {}
    out['f_empty'] = abs(f[0]) < tol and abs(g[0]) < tol
    mono = submod = band = True
    eu_m = eo_m = 0.0
    for S in range(N):
        for e in range(n):
            if S >> e & 1:
                continue
            Se = S | 1 << e
            d, dt = f[Se] - f[S], g[Se] - g[S]
            if d < -tol:
                mono = False
            for e2 in range(n):
                if e2 == e or S >> e2 & 1:
                    continue
                if f[Se | 1 << e2] - f[S | 1 << e2] > d + tol:
                    submod = False
            if d > tol:
                if dt <= 0:
                    band = False
                    continue
                eo_m = max(eo_m, dt / d)
                eu_m = max(eu_m, d / dt)
            elif abs(dt) > tol:
                band = False
    out['monotone'] = mono
    out['submodular'] = submod
    out['eta_u_single'] = eu_m
    out['eta_o_single'] = eo_m
    out['exact_eta_single'] = abs(eu_m - eu) < 1e-9 and abs(eo_m - eo) < 1e-9
    if all_pairs:
        eu2 = eo2 = 0.0
        for A in range(N):
            comp = (N - 1) ^ A
            B = comp
            while B:
                d, dt = f[A | B] - f[A], g[A | B] - g[A]
                if d > tol:
                    if dt <= 0:
                        band = False
                    else:
                        eo2 = max(eo2, dt / d)
                        eu2 = max(eu2, d / dt)
                elif abs(dt) > tol:
                    band = False
                B = (B - 1) & comp
        out['eta_u_pairs'] = eu2
        out['eta_o_pairs'] = eo2
        out['exact_eta_pairs'] = abs(eu2 - eu) < 1e-9 and abs(eo2 - eo) < 1e-9
    out['band_ok'] = band
    best = max(f[S] for S in range(N) if bin(S).count('1') <= K)
    Om = ((1 << K) - 1) << K
    out['opt_is_O'] = abs(best - 1.0) < 1e-9 and abs(f[Om] - 1.0) < 1e-9
    S = 0
    ok = True
    strict = True

    def typ(e):
        return 0 if e < j else (1 if e < K else 2)
    for t in range(K):
        gains = {e: g[S | 1 << e] - g[S] for e in range(n) if not S >> e & 1}
        if gains[t] < max(gains.values()) - 1e-9:
            ok = False
            break
        for e, val in gains.items():
            if typ(e) != typ(t) and val > gains[t] - 1e-12:
                strict = False
        S |= 1 << t
    out['greedy'] = ok
    if I.sb != I.s:
        out['greedy_strict_cross_type'] = strict
    out['ratio'] = f[S]
    out['Vj'] = Vj(K, j, float(eta))
    out['ratio_is_Vj'] = abs(out['ratio'] - out['Vj']) < 1e-9
    allok = all(v for k, v in out.items() if isinstance(v, bool))
    rec('full', f"K={K} j={j} eta={float(eta):.6g}{tag}", allok,
        json.dumps({k: (v if isinstance(v, bool) else float(v))
                    for k, v in out.items()}))
    return allok, out


# ----------------------------------------------------------------------------
# Part 3: LP cross-checks
# ----------------------------------------------------------------------------
def lp_cross(do_full_lp):
    import reduced_lp
    ok_all = True
    for K in range(2, 7):
        etas = [K - j + fr for j in range(1, K) for fr in (0.25, 0.75)] + [K + 0.5]
        for eta in etas:
            v = reduced_lp.reduced(K, float(eta))
            js = [jj for jj in range(K) if K - jj <= eta + 1e-12]
            vj = min(Vj(K, jj, float(eta)) for jj in js)
            ok = abs(v - vj) < 1e-9
            ok_all &= rec('lp', f"reduced LP K={K} eta={float(eta):.6g}", ok,
                          f"LP={v:.12f} min_j V_j={vj:.12f}")
    if do_full_lp:
        import worst_case_lp
        for (K, eta) in [(2, 1.5), (2, 2.5), (3, 1.5), (3, 2.5)]:
            e = float(eta) ** 0.5
            val, O, x = worst_case_lp.worst_case(2 * K, K, e, e, "single")
            vj = min(Vj(K, jj, float(eta)) for jj in range(K))
            ok = abs(val - vj) < 1e-8
            ok_all &= rec('lp', f"full-lattice LP K={K} n={2*K} eta={eta}", ok,
                          f"LP={val:.12f} min_j V_j={vj:.12f} O={O}")
    return ok_all


# ----------------------------------------------------------------------------
# Part 4: general-K symbolic verification (sympy): K, j, x, y, z all symbolic.
# T5 parametrisation: p = q^x is carried by free symbols, p = Q*R with
# Q = q^j > 0 and R = q^{x-j} >= 1.  Every inequality is certified by
# exhibiting a polynomial with non-negative coefficients after the shifts
#     R = 1 + r,   S(=eta) = m + w,   m = K - j,   K - y = y1,   m = z + zc.
# ----------------------------------------------------------------------------
def symbolic_general():
    import sympy as sp

    K, j, s, y, z = sp.symbols('K j s y z', positive=True)
    Q, R, r, w, v, kk, zc, y1, jj = sp.symbols(
        'Q R r w v kk zc y1 jj', nonnegative=True)
    S = s ** 2                                    # eta
    k1 = (K - 1) * S + 1
    q = (K - 1) * S / k1
    p = Q * R                                     # q^x, x <= j
    delta = Q / (K * S)
    dtil = Q / (K * s)
    W0 = k1 / (K * s)
    ok_all = True

    def ident(name, expr):
        nonlocal ok_all
        val = sp.simplify(sp.together(expr))
        ok_all &= rec('sym', name, val == 0, f"simplify -> {val}")

    def nonneg(name, expr, subs, gens):
        """expr >= 0, certified by non-negative coefficients after subs."""
        nonlocal ok_all
        e = sp.expand(sp.simplify(expr.subs(subs)))
        try:
            P = sp.Poly(e, *gens)
            cs = P.coeffs()
            ok = all(sp.simplify(c) >= 0 for c in cs)
        except sp.PolynomialError as exc:
            ok, cs = False, str(exc)
        ok_all &= rec('sym', name, ok, f"expr={e}  coeffs={cs}")

    # --- marginal gains of f (branches: y<=K-2 / y=K-1 / y=K) -------------
    DCf = p * (1 - q) * (K - y) / K                 # any y <= K-1 (0 at y=K)
    DPf = delta                                     # y <= K-1 (0 at y=K)
    DOf_mid = p / K                                 # y <= K-2
    DOf_last = p / K - z * delta                    # y = K-1
    # --- marginal gains of ftilde ---------------------------------------
    DCg_y0 = p * (1 - q) * W0                       # y = 0
    DCg = p * (1 - q) * (K - y) * s / K             # 1 <= y <= K-1
    DPg = dtil
    DOg_y0 = p * (W0 - (K - 1) * s / K)             # y = 0 -> 1
    DOg_mid = p * s / K                             # 1 <= y <= K-2
    DOg_last = p * s / K - z * dtil                 # y = K-1

    # --- structural identities -------------------------------------------
    ident('(1-q) k1 = 1', (1 - q) * k1 - 1)
    ident('W0 - (K-1)s/K = 1/(K s)', (W0 - (K - 1) * s / K) - 1 / (K * s))
    ident('dtil = s delta', dtil - s * delta)
    ident('f(0,0,0) = 0', (1 - 1 * K / K))
    ident('ftilde(0,0,0) = 0', W0 - 1 * W0)

    # --- (C2) error band: every ratio is s, 1/s, or k1/(K s) --------------
    ident('band C, 1<=y<=K-1:  D_C g = s D_C f', DCg - s * DCf)
    ident('band C, y=0:  D_C g = (k1/(K s)) D_C f',
          DCg_y0 - (k1 / (K * s)) * DCf.subs(y, 0))
    ident('band P:  D_P g = s D_P f', DPg - s * DPf)
    ident('band O, y=0:  D_O f = s D_O g', DOf_mid - s * DOg_y0)
    ident('band O, 1<=y<=K-2:  D_O g = s D_O f', DOg_mid - s * DOf_mid)
    ident('band O, y=K-1:  D_O g = s D_O f', DOg_last - s * DOf_last)
    nonneg('k1/(K s) >= 1/s   (i.e. k1 - K >= 0)', (k1 - K),
           {S: 1 + v, K: 2 + kk}, (kk, v))
    nonneg('k1/(K s) <= s     (i.e. K S - k1 >= 0)', (K * S - k1),
           {S: 1 + v, K: 2 + kk}, (kk, v))

    # --- (C1) monotonicity ------------------------------------------------
    nonneg('mono C:  D_C f >= 0', DCf * K * k1,
           {S: 1 + v, K - y: y1, K: 2 + kk}, (Q, R, y1, kk, v))
    nonneg('mono P:  D_P f >= 0', DPf * K * S, {S: 1 + v}, (Q, v))
    nonneg('mono O (y<=K-2):  D_O f >= 0', DOf_mid * K, {}, (Q, R))
    # the only place where eta >= K-j is needed: z <= K-j = m <= S
    nonneg('mono O (y=K-1):  D_O f >= 0  [needs eta >= K-j]',
           DOf_last * K * S, {R: 1 + r, S: (z + zc) + w}, (Q, r, z, zc, w))

    # --- (C1) submodularity: all 9 second differences ---------------------
    # a C-step multiplies q^x by q, i.e. R -> q R (Q = q^j is a constant here)
    Cstep = {R: q * R}
    nonneg('sub CC <= 0', -(DCf.subs(Cstep) - DCf) * K * k1 ** 2,
           {S: 1 + v, K - y: y1, K: 2 + kk}, (Q, R, y1, kk, v))
    ident('sub CP = 0', DCf.subs(z, z + 1) - DCf)
    nonneg('sub CO <= 0 (y+1<=K-1)',
           -(DCf.subs(y, y + 1) - DCf) * K * k1, {S: 1 + v, K: 2 + kk}, (Q, R, kk, v))
    nonneg('sub CO <= 0 (y=K-1 -> y=K, D_C f becomes 0)',
           -(0 - DCf.subs(y, K - 1)) * K * k1, {S: 1 + v, K: 2 + kk}, (Q, R, kk, v))
    ident('sub PC = 0', DPf.subs(Cstep) - DPf)
    ident('sub PP = 0', DPf.subs(z, z + 1) - DPf)
    nonneg('sub PO <= 0 (y=K-1 -> y=K, D_P f becomes 0)',
           -(0 - DPf) * K * S, {S: 1 + v}, (Q, v))
    nonneg('sub OC <= 0 (y<=K-2)', -(DOf_mid.subs(Cstep) - DOf_mid) * K * k1,
           {S: 1 + v, K: 2 + kk}, (Q, R, kk, v))
    nonneg('sub OC <= 0 (y=K-1)', -(DOf_last.subs(Cstep) - DOf_last) * K * k1,
           {S: 1 + v, K: 2 + kk}, (Q, R, kk, v))
    ident('sub OP = 0 (y<=K-2)', DOf_mid.subs(z, z + 1) - DOf_mid)
    nonneg('sub OP <= 0 (y=K-1)', -(DOf_last.subs(z, z + 1) - DOf_last) * K * S,
           {S: 1 + v}, (Q, v))
    ident('sub OO = 0 (y+1<=K-2)', DOf_mid.subs(y, y + 1) - DOf_mid)
    nonneg('sub OO <= 0 (y=K-2 -> y=K-1)', -(DOf_last - DOf_mid) * K * S,
           {S: 1 + v}, (Q, z, v))
    # the y = K face: both f and ftilde become independent of x (and of z)
    ident('D_C f = 0 at y=K', DCf.subs(y, K))
    ident('D_C g = 0 at y=K', DCg.subs(y, K))

    # --- (C3) OPT = 1:  f(x,z,y) <= 1 whenever x+z+y <= K -----------------
    # 1 - p(K-y)/K + z delta <= 1  <=>  z Q <= p S (K-y), using z <= K-y.
    nonneg('OPT: p S (K-y) - z Q >= 0  [uses z <= K-y, R>=1, S>=1]',
           (R * S * (z + y1) - z) * Q, {R: 1 + r, S: 1 + v}, (Q, r, v, z, y1))

    # --- (C4) greedy (ties broken adversarially) --------------------------
    # at state (t,0,0), t < j:  D_C g = D_O g   and   D_P g <= D_C g
    ident('greedy tie at (t,0,0):  D_C g = D_O g',
          DCg_y0.subs(y, 0) - DOg_y0)
    nonneg('greedy at (t,0,0):  D_C g - D_P g >= 0  [R = q^{x-j} >= 1]',
           (DOg_y0 - DPg) * K * s, {R: 1 + r}, (Q, r))
    # at state (j,z,0) (x = j so R = 1):  D_P g = D_O g
    ident('greedy tie at (j,z,0):  D_P g = D_O g', DPg - DOg_y0.subs(R, 1))

    # --- (C5) value = V_j --------------------------------------------------
    Vj_sym = 1 - Q * (1 - (K - j) / (K * S))
    ident('f(j, K-j, 0) = V_j', (1 - Q + (K - j) * delta) - Vj_sym)

    # --- uncapped variant: drop the [y<K] cutoff --------------------------
    # f = 1 - q^x (K-y)/K + z delta and ftilde = W0 - q^x W(y) + z dtil for
    # every y (including y=K).  Then the O-direction gain of f is p/K at every
    # y, so monotonicity holds with NO side condition and the second
    # differences OO / OP / PO vanish identically; the value is still V_j.
    # Everything else (band ratios, greedy, OPT, value) is literally the same
    # expression as the 1<=y<=K-2 branch above.
    ident('uncapped: W(K) = 0', (K - K) * s / K)
    nonneg('uncapped mono O: D_O f = p/K >= 0 (no condition on eta)',
           DOf_mid * K, {}, (Q, R))
    ident('uncapped sub OO = 0', DOf_mid.subs(y, y + 1) - DOf_mid)
    ident('uncapped sub OP = 0', DOf_mid.subs(z, z + 1) - DOf_mid)
    ident('uncapped sub PO = 0', DPf.subs(y, y + 1) - DPf)
    ident('uncapped band O at y=K-1: D_O g = s D_O f', DOg_mid - s * DOf_mid)
    ident('uncapped band P at y=K: D_P g = s D_P f', DPg - s * DPf)
    return ok_all


# ----------------------------------------------------------------------------
# Part 5: per-K exact sweep, K = 2..KMAX (T5-style mixed level).
# eta chosen so that s = sqrt(eta) is rational => Fraction arithmetic is exact.
# ----------------------------------------------------------------------------
def rational_s(target_eta):
    for den in (10, 20, 50, 100, 200, 1000, 10000):
        num = round(target_eta ** 0.5 * den)
        s = Fr(num, den)
        if abs(float(s * s) - target_eta) < 0.25:
            return s
    raise RuntimeError('no rational s found')


def exact_sweep(kmax=8):
    ok_all = True
    for K in range(2, kmax + 1):
        for j in range(K):
            m = K - j
            targets = [m + 0.25, m + 0.75] if j > 0 else [K + 0.3, K + 3.5]
            for te in targets:
                s = rational_s(te)
                assert float(s * s) >= m - 1e-12, (K, j, s)
                ok, _ = count_check(K, j, s, tol=Fr(0), tag='(exact)')
                ok_all &= ok
                ok, _ = count_check(K, j, s, tol=Fr(0), tag='(exact,uncapped)',
                                    capped=False)
                ok_all &= ok
            root = int(round(m ** 0.5))
            if root * root == m:          # left endpoint eta = K-j, exact
                ok, _ = count_check(K, j, Fr(root), tol=Fr(0),
                                    tag='(exact,left endpoint eta=K-j)')
                ok_all &= ok
    return ok_all


# ----------------------------------------------------------------------------
# Part 6: reproduce the recorded R5 table (the ground truth of the exact
# worst case, obtained in night 1 from the full-lattice LP) with the explicit
# instances -- this is the step that upgrades R10 from "LP value" to
# "attained worst case" at every recorded point.
# ----------------------------------------------------------------------------
R5_TABLE = {
    2: {1: 3 / 4, 1.5: 3 / 5, 2: 1 / 2, 2.5: 2 / 5, 3: 1 / 3, 4: 1 / 4},
    3: {1: 19 / 27, 1.5: 9 / 16, 2: 7 / 15, 2.5: 7 / 18, 3: 1 / 3, 4: 1 / 4,
        1.1: 0.670573, 1.25: 0.625850, 2.8: 0.353535, 2.95: 0.338164,
        3.05: 1 / 3.05},
    4: {1: 175 / 256, 1.5: 0.543576, 2: 22 / 49, 2.5: 0.377163, 3: 13 / 40,
        4: 1 / 4, 3.8: 0.262097, 4.2: 1 / 4.2},
}


def best_j(K, eta):
    cand = [jj for jj in range(K) if K - jj <= eta + 1e-12]
    return min(cand, key=lambda jj: Vj(K, jj, eta))


def r5_reproduction():
    ok_all = True
    for K, tab in R5_TABLE.items():
        for eta, target in sorted(tab.items()):
            j = best_j(K, float(eta))
            ok, out = full_check(K, j, float(eta), all_pairs=True,
                                 tag=f'  [R5 {target:.6f}]')
            hit = abs(out['ratio'] - target) < 1e-6
            ok_all &= rec('R5', f"K={K} eta={eta} j*={j}", ok and hit,
                          f"instance ratio={out['ratio']:.9f} R5={target:.9f} "
                          f"diff={out['ratio']-target:.2e}")
    return ok_all


# ----------------------------------------------------------------------------
# Part 7: strict-tie-breaking variant (build with eta' < eta, declare band eta)
# and the comparison with the two published bounds L_K, U_K.
# ----------------------------------------------------------------------------
def strict_variant(cases):
    ok_all = True
    for (K, j, eta, gap) in cases:
        etap = eta - gap
        if etap < K - j:
            continue
        ok, out = full_check(K, j, etap, all_pairs=True, eta_band=eta,
                             tag=f'  [strict, eta_build={etap}]')
        # V_j is decreasing in eta, so building at eta' < eta overshoots:
        # ratio = V_j(eta') > V_j(eta), and ratio -> V_j(eta) as eta' -> eta.
        excess = out['ratio'] - Vj(K, j, eta)
        ok_all &= rec('strict', f"K={K} j={j} eta={eta} eta_build={etap}",
                      ok and out.get('greedy_strict_cross_type', False)
                      and 0 <= excess < 0.05 and excess < 30 * gap,
                      f"ratio={out['ratio']:.9f} = V_j(eta')={Vj(K,j,etap):.9f}; "
                      f"V_j(eta)={Vj(K,j,eta):.9f} excess={excess:.3e} "
                      f"eta_u={out['eta_u_single']:.6f} "
                      f"eta_o={out['eta_o_single']:.6f}")
    return ok_all


def bounds_table():
    rows = []
    for K in (2, 3, 4, 5, 6, 8, 12):
        for eta in (1.0, 1.5, 2.0, 2.5, 3.0):
            j = best_j(K, eta)
            v = Vj(K, j, eta)
            rows.append(dict(K=K, eta=eta, j=j, V=v, U=UK(K, eta), L=LK(K, eta),
                             U_minus_V=UK(K, eta) - v, V_minus_L=v - LK(K, eta)))
    ok = all(r['U_minus_V'] >= -1e-15 and r['V_minus_L'] >= -1e-15 for r in rows)
    strict_gap = all(r['U_minus_V'] > 1e-12 for r in rows if r['eta'] > 1)
    rec('bounds', 'L_K <= min_j V_j <= U_K on the grid', ok, '')
    rec('bounds', 'U_K - V_{j*} > 0 for eta > 1 (R7 family cannot reach it)',
        strict_gap, json.dumps(rows[:4]))
    with open(os.path.join(HERE, 'N2_bounds.json'), 'w') as fh:
        json.dump(rows, fh, indent=1)
    return ok and strict_gap


# ----------------------------------------------------------------------------
# Part 8: compare with the stored K=2 LP witness (results/k2_witness_instances
# .json, night 1).  Our f must coincide with it element-by-element; our ftilde
# is a different point of the same (degenerate) optimal face.
# ----------------------------------------------------------------------------
def k2_witness_compare():
    path = os.path.join(HERE, 'k2_witness_instances.json')
    if not os.path.exists(path):
        return rec('witness', 'k2_witness_instances.json present', False, 'missing')
    W = json.load(open(path))
    # b1 -> the single C element, b2 -> the single P element, o1,o2 -> O
    idx = {'b1': (1, 0, 0), 'b2': (0, 1, 0), 'b1+b2': (1, 1, 0),
           'o1': (0, 0, 1), 'b1+o1': (1, 0, 1), 'b2+o1': (0, 1, 1),
           'b1+b2+o1': (1, 1, 1), 'o2': (0, 0, 1), 'b1+o2': (1, 0, 1),
           'b2+o2': (0, 1, 1), 'b1+b2+o2': (1, 1, 1), 'o1+o2': (0, 0, 2),
           'b1+o1+o2': (1, 0, 2), 'b2+o1+o2': (0, 1, 2),
           'b1+b2+o1+o2': (1, 1, 2)}
    ok_all = True
    for key, blk in sorted(W.items()):
        eta = float(key)
        I = Instance(2, 1, eta ** 0.5)
        diffs = {k: I.f(*idx[k]) - v for k, v in blk['f'].items()}
        worst = max(abs(v) for v in diffs.values())
        ok_all &= rec('witness', f"K=2 eta={eta}: our f == LP witness f",
                      worst < 1e-6, f"max|diff| = {worst:.2e}")
        ok_all &= rec('witness', f"K=2 eta={eta}: ratio == witness ratio",
                      abs(I.V() - blk['ratio']) < 1e-9,
                      f"V_1={I.V():.9f} witness={blk['ratio']:.9f}")
    return ok_all


def split_variant(cases):
    """Same instance with an asymmetric error split eta_u * eta_o = eta."""
    ok_all = True
    for (K, j, eta, eu) in cases:
        eo = eta / eu
        ok, out = full_check(K, j, eta, all_pairs=True, split=(eu, eo),
                             tag=f'  [split eta_u={eu:g}, eta_o={eo:g}]')
        ok_all &= rec('split', f"K={K} j={j} eta={eta} split=({eu:g},{eo:g})", ok,
                      f"ratio={out['ratio']:.9f} V_j={out['Vj']:.9f} "
                      f"eta_u={out['eta_u_single']:.6f} eta_o={out['eta_o_single']:.6f}")
    return ok_all


def r7_embedding():
    """j = K (no prediction steps) reproduces the R7 instance of the paper:
    same f, value U_K(eta) = 1 - q^K.  j = 0 reproduces the modular R2 instance
    with value 1/eta.  So V_j interpolates between the two known families and
    the middle j are the new ones."""
    import check_explicit_instance as CEI
    ok_all = True
    for (K, eta) in [(2, 2.0), (3, 2.5), (4, 1.5), (5, 3.0)]:
        k1 = (K - 1) * eta + 1
        ahat = k1 / K                       # R7's parameter: ahat*K = k1
        _, n, N, f7, g7 = CEI.build(K, ahat)
        I, n2, N2, f2, g2 = build_lattice(K, K, eta)
        d = float(np.max(np.abs(f7 - f2)))
        ok_all &= rec('R7', f"K={K} eta={eta}: j=K instance has R7's f", d < 1e-12,
                      f"max|f_ours - f_R7| = {d:.2e}")
        ok, out = full_check(K, K, eta, all_pairs=True, tag='  [j=K, = R7]')
        ok_all &= rec('R7', f"K={K} eta={eta}: ratio = U_K", ok
                      and abs(out['ratio'] - UK(K, eta)) < 1e-12,
                      f"ratio={out['ratio']:.9f} U_K={UK(K, eta):.9f} "
                      f"V_(K-1)={Vj(K, K-1, eta):.9f}")
    for (K, eta) in [(3, 3.5), (4, 5.0)]:
        I = Instance(K, 0, eta ** 0.5, capped=False)
        modular = all(abs(I.f(0, z, y) - (y / K + z / (K * eta))) < 1e-12
                      for z in range(K + 1) for y in range(K + 1))
        Ic = Instance(K, 0, eta ** 0.5)          # capped: same, truncated at 1
        cap_ok = all(abs(Ic.f(0, z, y) - min(I.f(0, z, y), 1.0)) < 1e-12
                     for z in range(K + 1) for y in range(K + 1))
        ok_all &= rec('R7', f"K={K} eta={eta}: uncapped j=0 = modular R2 instance",
                      modular and cap_ok and abs(I.V() - 1 / eta) < 1e-12,
                      f"V_0 = {I.V():.9f}, 1/eta = {1/eta:.9f}, "
                      f"capped = min(modular, 1): {cap_ok}")
    return ok_all


def predictor_shape():
    """Diagnostic (not a claim of the construction): ftilde is monotone but NOT
    submodular -- its O-direction gain jumps up between y=0 and y=1.  The model
    (code/worst_case_lp.py) constrains only f, and the R7 instance of the paper
    has the same feature; recorded here so the md can state it honestly."""
    rows = []
    for (K, j, eta) in [(3, 1, 2.5), (3, 2, 1.5), (4, 2, 2.5), (5, 3, 2.5)]:
        I, n, N, f, g = build_lattice(K, j, eta)
        mono = sub = True
        for S in range(N):
            for e in range(n):
                if S >> e & 1:
                    continue
                d = g[S | 1 << e] - g[S]
                if d < -1e-12:
                    mono = False
                for e2 in range(n):
                    if e2 == e or S >> e2 & 1:
                        continue
                    if g[S | 1 << e | 1 << e2] - g[S | 1 << e2] > d + 1e-12:
                        sub = False
        rows.append(dict(K=K, j=j, eta=eta, ftilde_monotone=bool(mono),
                         ftilde_submodular=bool(sub)))
    ok = all(r['ftilde_monotone'] and not r['ftilde_submodular'] for r in rows)
    return rec('shape', 'ftilde is monotone but not submodular (expected)', ok,
               json.dumps(rows))


def dump_examples():
    """Human-readable instance tables for the report."""
    ex = {}
    for (K, j, eta) in [(2, 1, 1.5), (3, 1, 2.5), (3, 2, 1.5), (4, 2, 2.5)]:
        I = Instance(K, j, eta ** 0.5)
        rows = []
        for x in range(j + 1):
            for z in range(K - j + 1):
                for y in range(K + 1):
                    rows.append(dict(x=x, z=z, y=y, f=I.f(x, z, y), g=I.g(x, z, y)))
        ex[f'K{K}_j{j}_eta{eta}'] = dict(
            K=K, j=j, eta=eta, q=I.q, k1=I.k1, delta=I.delta, dtil=I.dtil,
            W0=I.W0, Vj=I.V(), table=rows)
    with open(os.path.join(HERE, 'N2_examples.json'), 'w') as fh:
        json.dump(ex, fh, indent=1)
    print('wrote results/N2_examples.json')


# ----------------------------------------------------------------------------
def main():
    do_full_lp = os.environ.get('N2_FULLLP', '1') != '0'
    kmax_full = int(os.environ.get('N2_KMAX_FULL', '6'))
    kmax_exact = int(os.environ.get('N2_KMAX_EXACT', '8'))

    print('== Part A: full 2^{2K} lattice checks (floats) ==', flush=True)
    for K in range(2, kmax_full + 1):
        for j in range(K):
            m = K - j
            etas = [m + 0.25, m + 0.75] if j > 0 else [K + 0.5, K + 2.0]
            for eta in etas:
                full_check(K, j, eta, all_pairs=(2 * K <= 12))
            # the uncapped variant needs no segment condition: also probe
            # eta far outside [K-j, K-j+1]
            for eta in {1.25, float(K) + 1.0, m + 0.5}:
                full_check(K, j, eta, all_pairs=(2 * K <= 12), capped=False,
                           tag='  [uncapped]')
        print(f'   ... K={K} done', flush=True)

    print('== Part B: exact (Fraction) count-lattice sweep, K=2..%d =='
          % kmax_exact, flush=True)
    exact_sweep(kmax_exact)

    print('== Part C: general-K symbolic (sympy) ==', flush=True)
    symbolic_general()

    print('== Part D: reproduce the recorded R5 table ==', flush=True)
    r5_reproduction()

    print('== Part E: strict-tie-breaking variant ==', flush=True)
    strict_variant([(K, j, eta, g)
                    for (K, j, eta) in [(2, 1, 1.5), (3, 1, 2.5), (3, 2, 1.5),
                                        (4, 2, 2.5), (4, 3, 1.5), (5, 2, 3.5)]
                    for g in (0.05, 0.001)])

    print('== Part F: L_K <= min_j V_j <= U_K ==', flush=True)
    bounds_table()

    print('== Part F2: asymmetric error splits eta_u * eta_o = eta ==', flush=True)
    split_variant([(K, j, eta, eu)
                   for (K, j, eta) in [(2, 1, 1.5), (3, 1, 2.5), (3, 2, 1.5),
                                       (4, 2, 2.5), (4, 3, 1.5), (5, 3, 2.5)]
                   for eu in (1.0, eta, eta ** 0.25, eta ** 0.75)])

    print('== Part F3: j=0 / j=K endpoints (R2 and R7 instances) ==', flush=True)
    r7_embedding()

    print('== Part G: predictor shape + K=2 LP witness ==', flush=True)
    predictor_shape()
    k2_witness_compare()

    print('== Part H: LP cross-checks ==', flush=True)
    lp_cross(do_full_lp)
    dump_examples()

    n_ok = sum(1 for _, _, ok, _ in RESULTS if ok)
    n = len(RESULTS)
    print()
    for part in ('full', 'count', 'sym', 'R5', 'strict', 'bounds', 'split',
                 'R7', 'shape', 'witness', 'lp'):
        sub = [r for r in RESULTS if r[0] == part]
        bad = [r for r in sub if not r[2]]
        print(f'  {part:6s}: {len(sub)-len(bad)}/{len(sub)} PASS')
        for r in bad[:25]:
            print(f'      FAIL {r[1]}  {r[3][:200]}')
    print(f'\nTOTAL {n_ok}/{n} PASS')
    with open(os.path.join(HERE, 'N2_check.json'), 'w') as fh:
        json.dump([{'part': p, 'name': nm, 'ok': ok, 'info': inf}
                   for p, nm, ok, inf in RESULTS], fh, indent=1)
    print('wrote results/N2_check.json')
    sys.exit(0 if n_ok == n else 1)


if __name__ == '__main__':
    main()
