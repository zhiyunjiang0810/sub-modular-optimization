#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROUTE-TWO blind verification for lem:coherence (T5) and its sharp form.

Exact rational arithmetic only (fractions.Fraction / sympy). Floats appear
only inside printouts.

Parts
  A  [VERIFIED-SYMBOLIC]  the two swap identities for f and for ftilde
  B  [VERIFIED-LP]        exact vertex enumeration of the local polytope,
                          minimising eta*D - C and (1-1/eta)*C - (B-A)
  C  [VERIFIED-LP]        same, with the submodularity rows removed
                          (shows band alone suffices), and with the
                          ftilde swap identity removed (shows it is needed)
  D  [VERIFIED-EXHAUSTIVE] the K = 2 extremal instance, all four band rows
  E  [VERIFIED-EXHAUSTIVE] a K = 3 predictive-greedy run on a coverage
                          instance with eta = 3/2, lemma checked at every
                          state of the run

Run:  python3 results/V11/route2/verify_coherence.py
"""

from fractions import Fraction as F
from itertools import combinations
import sympy as sp

OK = "ok"
BAD = "FAIL"
failures = []


def check(name, cond):
    print(("  [%s] " % (OK if cond else BAD)) + name)
    if not cond:
        failures.append(name)


# ---------------------------------------------------------------- Part A
def part_A():
    print("\n== Part A  swap identities  [VERIFIED-SYMBOLIC] ==")
    # generic set function values on the 4-point lattice above S
    f0, fe, fp, fep = sp.symbols("f0 fe fp fep")  # f(S), f(S+e), f(S+e'), f(S+e+e')
    A = fe - f0          # d_e(S)
    B = fp - f0          # d_{e'}(S)
    C = fep - fe         # d_{e'}(S + e)
    D = fep - fp         # d_e(S + e')
    check("A + C - B - D == 0 identically", sp.simplify(A + C - B - D) == 0)
    check("D - C == A - B identically", sp.simplify((D - C) - (A - B)) == 0)
    # the same holds for any set function, in particular for ftilde
    g0, ge, gp, gep = sp.symbols("g0 ge gp gep")
    At, Bt, Ct, Dt = ge - g0, gp - g0, gep - ge, gep - gp
    check("At + Ct - Bt - Dt == 0 identically", sp.simplify(At + Ct - Bt - Dt) == 0)
    check("Dt - Ct == At - Bt identically", sp.simplify((Dt - Ct) - (At - Bt)) == 0)
    # slack decomposition of item (i): the three nonnegative terms
    eu, eo = sp.symbols("eta_u eta_o", positive=True)
    lhs = eo * D - C / eu
    rhs = (eo * D - Dt) + (At - Bt) + (Ct - C / eu)
    check("slack decomposition eta_o*D - C/eta_u == (eta_o D - Dt) + (At - Bt) "
          "+ (Ct - C/eta_u)", sp.simplify(lhs - rhs) == 0)


# ---------------------------------------------------------------- Part B/C
# variables x = (A, B, C, D, At, Bt, Ct, Dt)
NV = 8
IA, IB, IC, ID, IAt, IBt, ICt, IDt = range(NV)


def row(**kw):
    r = [F(0)] * NV
    for k, v in kw.items():
        r[globals()["I" + k]] = F(v)
    return r


def build(eta_u, eta_o, submodular=True, tilde_identity=True):
    """Return (equalities, inequalities) as lists of (row, rhs) with
    row . x == rhs  resp.  row . x >= rhs."""
    eqs = []
    eqs.append((row(A=1, B=-1, C=1, D=-1), F(0)))          # f swap identity
    if tilde_identity:
        eqs.append((row(At=1, Bt=-1, Ct=1, Dt=-1), F(0)))  # ftilde swap identity
    eqs.append((row(A=1, B=1, C=1, D=1), F(1)))            # normalisation
    ins = []
    for v in ("A", "B", "C", "D"):
        ins.append((row(**{v: 1}), F(0)))                      # monotone: gain >= 0
    for v, vt in (("A", "At"), ("B", "Bt"), ("C", "Ct"), ("D", "Dt")):
        ins.append((row(**{vt: 1, v: -F(1) / eta_u}), F(0)))   # dtilde >= d/eta_u
        ins.append((row(**{v: eta_o, vt: -1}), F(0)))          # eta_o d >= dtilde
    ins.append((row(At=1, Bt=-1), F(0)))                       # hypothesis
    if submodular:
        ins.append((row(B=1, C=-1), F(0)))                     # d_{e'}(S+e) <= d_{e'}(S)
        ins.append((row(A=1, D=-1), F(0)))                     # d_e(S+e') <= d_e(S)
    return eqs, ins


def solve_exact(M, b):
    """Gaussian elimination over Fraction. Returns unique solution or None."""
    n = len(M)
    M = [r[:] + [b[i]] for i, r in enumerate(M)]
    piv = []
    r = 0
    for c in range(NV):
        p = None
        for i in range(r, n):
            if M[i][c] != 0:
                p = i
                break
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]
        M[r] = [v / pv for v in M[r]]
        for i in range(n):
            if i != r and M[i][c] != 0:
                fct = M[i][c]
                M[i] = [M[i][j] - fct * M[r][j] for j in range(NV + 1)]
        piv.append(c)
        r += 1
        if r == n:
            break
    if len(piv) != NV:
        return None
    for i in range(r, n):
        if any(M[i][j] != 0 for j in range(NV)) is False and M[i][NV] != 0:
            return None
    x = [F(0)] * NV
    for i, c in enumerate(piv):
        x[c] = M[i][NV]
    return x


def feasible(x, eqs, ins):
    for rw, rhs in eqs:
        if sum(rw[i] * x[i] for i in range(NV)) != rhs:
            return False
    for rw, rhs in ins:
        if sum(rw[i] * x[i] for i in range(NV)) < rhs:
            return False
    return True


def lp_min(obj, eqs, ins):
    """Exact minimum of obj . x over the polytope, by vertex enumeration.
    Returns (value, argmin) or (None, None) if the polytope is empty."""
    ne = len(eqs)
    need = NV - ne
    best = None
    arg = None
    for pick in combinations(range(len(ins)), need):
        M = [rw for rw, _ in eqs] + [ins[i][0] for i in pick]
        b = [rhs for _, rhs in eqs] + [ins[i][1] for i in pick]
        x = solve_exact(M, b)
        if x is None:
            continue
        if not feasible(x, eqs, ins):
            continue
        val = sum(obj[i] * x[i] for i in range(NV))
        if best is None or val < best:
            best, arg = val, x
    return best, arg


def obj_i(eta):
    o = [F(0)] * NV
    o[ID] = F(eta)
    o[IC] = F(-1)
    return o            # eta*D - C  >= 0  is exactly item (i)


def obj_ii(eta):
    o = [F(0)] * NV
    o[IC] = 1 - F(1) / F(eta)
    o[IB] = F(-1)
    o[IA] = F(1)
    return o            # (1-1/eta)C - (B-A) >= 0 is exactly item (ii)


SPLITS = [(F(1), F(3, 2)), (F(3, 2), F(1)), (F(3, 4), F(2)), (F(2), F(3, 4)),
          (F(1), F(2)), (F(2), F(1)), (F(4, 3), F(3, 2)), (F(1), F(3)), (F(3), F(1))]


def part_B():
    print("\n== Part B  exact LP over the local polytope  [VERIFIED-LP] ==")
    for eu, eo in SPLITS:
        eta = eu * eo
        eqs, ins = build(eu, eo, submodular=True, tilde_identity=True)
        v1, x1 = lp_min(obj_i(eta), eqs, ins)
        v2, x2 = lp_min(obj_ii(eta), eqs, ins)
        print("  eta_u=%s eta_o=%s eta=%s : min(eta*D - C) = %s , "
              "min((1-1/eta)C - (B-A)) = %s" % (eu, eo, eta, v1, v2))
        check("(i) holds and is tight, eta=%s split (%s,%s)" % (eta, eu, eo), v1 == 0)
        check("(ii) holds and is tight, eta=%s split (%s,%s)" % (eta, eu, eo), v2 == 0)
        if eta == F(3, 2) and eu == 1:
            print("      argmin of (i): A=%s B=%s C=%s D=%s | At=%s Bt=%s Ct=%s Dt=%s"
                  % tuple(x1))


def part_C():
    print("\n== Part C  which hypotheses are load bearing  [VERIFIED-LP] ==")
    eu, eo = F(1), F(3, 2)
    eta = eu * eo
    # C1: drop both submodularity rows
    eqs, ins = build(eu, eo, submodular=False, tilde_identity=True)
    v1, _ = lp_min(obj_i(eta), eqs, ins)
    v2, _ = lp_min(obj_ii(eta), eqs, ins)
    print("  without submodularity: min(eta*D - C) = %s , min((1-1/eta)C-(B-A)) = %s"
          % (v1, v2))
    check("(i) survives deletion of submodularity", v1 == 0)
    check("(ii) survives deletion of submodularity", v2 == 0)
    # C2: drop the ftilde swap identity (i.e. forget that dtilde comes from a
    #     set function) but keep everything else
    eqs, ins = build(eu, eo, submodular=True, tilde_identity=False)
    v1b, xb = lp_min(obj_i(eta), eqs, ins)
    v2b, _ = lp_min(obj_ii(eta), eqs, ins)
    print("  without the ftilde swap identity: min(eta*D - C) = %s , "
          "min((1-1/eta)C-(B-A)) = %s" % (v1b, v2b))
    check("(i) fails once the ftilde swap identity is dropped", v1b < 0)
    check("(ii) fails once the ftilde swap identity is dropped", v2b < 0)
    if xb is not None:
        print("      witness: A=%s B=%s C=%s D=%s | At=%s Bt=%s Ct=%s Dt=%s" % tuple(xb))
    # C3: the DR comparison C <= B is exactly what submodularity buys
    eqs, ins = build(eu, eo, submodular=False, tilde_identity=True)
    o = [F(0)] * NV
    o[IB] = F(1)
    o[IC] = F(-1)
    v3, x3 = lp_min(o, eqs, ins)      # min(B - C) without submodularity
    print("  without submodularity: min(B - C) = %s  (so d_{e'}(S+e) <= d_{e'}(S) "
          "is not implied by the band)" % v3)
    check("B - C can be negative without submodularity", v3 < 0)
    # C4: the plain band form (1-1/eta)B >= B-A, no submodularity needed either
    eqs, ins = build(eu, eo, submodular=False, tilde_identity=True)
    o = [F(0)] * NV
    o[IB] = (1 - F(1) / eta) - 1
    o[IA] = F(1)
    v4, _ = lp_min(o, eqs, ins)
    print("  without submodularity: min((1-1/eta)B - (B-A)) = %s" % v4)
    check("plain band form (1-1/eta)B >= B-A holds and is tight", v4 == 0)


# ---------------------------------------------------------------- Part D
def part_D():
    print("\n== Part D  K = 2 extremal instance, eta = 3/2  [VERIFIED-EXHAUSTIVE] ==")
    eu, eo, eta = F(1), F(3, 2), F(3, 2)
    # f on N = {e, e'}, S = empty
    f = {frozenset(): F(0), frozenset("e"): F(1), frozenset("p"): F(4, 3),
         frozenset("ep"): F(2)}
    g = {frozenset(): F(0), frozenset("e"): F(3, 2), frozenset("p"): F(3, 2),
         frozenset("ep"): F(5, 2)}   # g = ftilde
    A = f[frozenset("e")] - f[frozenset()]
    B = f[frozenset("p")] - f[frozenset()]
    C = f[frozenset("ep")] - f[frozenset("e")]
    D = f[frozenset("ep")] - f[frozenset("p")]
    At = g[frozenset("e")] - g[frozenset()]
    Bt = g[frozenset("p")] - g[frozenset()]
    Ct = g[frozenset("ep")] - g[frozenset("e")]
    Dt = g[frozenset("ep")] - g[frozenset("p")]
    print("  A=%s B=%s C=%s D=%s | At=%s Bt=%s Ct=%s Dt=%s" % (A, B, C, D, At, Bt, Ct, Dt))
    check("monotone", min(A, B, C, D) >= 0)
    check("submodular, strictly: C < B and D < A", C < B and D < A)
    for nm, d, dt in (("d_e(S)", A, At), ("d_e'(S)", B, Bt),
                      ("d_e'(S+e)", C, Ct), ("d_e(S+e')", D, Dt)):
        check("band on %s: %s <= %s <= %s" % (nm, d / eu, dt, eo * d),
              d / eu <= dt <= eo * d)
    check("hypothesis At >= Bt", At >= Bt)
    check("(i) with EQUALITY: D == C/eta", D == C / eta)
    check("(ii) with EQUALITY: (1-1/eta)C == B - A", (1 - F(1) / eta) * C == B - A)
    check("order transfer Dt >= Ct", Dt >= Ct)
    check("all three slacks vanish: (eo*D-Dt, At-Bt, Ct-C/eu) = (%s,%s,%s)"
          % (eo * D - Dt, At - Bt, Ct - C / eu),
          eo * D - Dt == 0 and At - Bt == 0 and Ct - C / eu == 0)
    check("min form: B-A <= (1-1/eta)*min(B,C), and min is C (submodularity)",
          B - A <= (1 - F(1) / eta) * min(B, C) and min(B, C) == C)
    # a whole family, for every rational eta > 1 and every C in (0, eta*A]
    print("  family sweep (equality in (i) and (ii) for every eta and every C):")
    for eta2 in (F(3, 2), F(2), F(5, 2), F(3), F(7, 3)):
        for c in (F(1, 2), F(1), F(3, 2), eta2):
            a = F(1)
            b = a + c * (1 - 1 / eta2)
            d = c / eta2
            ok = (a + c == b + d and min(a, b, c, d) >= 0 and c <= b and d <= a
                  and b <= eta2 * a and d == c / eta2
                  and (1 - 1 / eta2) * c == b - a)
            check("family eta=%s C=%s: monotone+submodular+band tight" % (eta2, c), ok)


# ---------------------------------------------------------------- Part E
def part_E():
    print("\n== Part E  K = 3 predictive-greedy run, eta = 3/2  [VERIFIED-EXHAUSTIVE] ==")
    eu, eo, eta = F(1), F(3, 2), F(3, 2)
    # weighted coverage: true weights w, predicted weights wt, ratio in [1, 3/2]
    w = {"u1": F(4), "u2": F(5), "u3": F(6), "u4": F(2), "u5": F(3)}
    wt = {"u1": F(6), "u2": F(5), "u3": F(6), "u4": F(3), "u5": F(3)}
    cov = {"a": {"u1", "u4"}, "b": {"u2", "u4"}, "c": {"u3"}, "g": {"u5"}}
    N = ["a", "b", "c", "g"]
    K = 3
    for u in w:
        check("weight ratio of %s in [1, 3/2]" % u, F(1) <= wt[u] / w[u] <= F(3, 2))

    def f(S):
        return sum(w[u] for u in set().union(*[cov[e] for e in S]) if True) if S else F(0)

    def ft(S):
        return sum(wt[u] for u in set().union(*[cov[e] for e in S]) if True) if S else F(0)

    def d(e, S):
        return f(tuple(set(S) | {e})) - f(S)

    def dt(e, S):
        return ft(tuple(set(S) | {e})) - ft(S)

    S = tuple()
    for t in range(K):
        rest = [e for e in N if e not in S]
        mx = max(dt(e, S) for e in rest)
        # adversarial tie breaking: among the predicted argmax take the worst true gain
        cand = [e for e in rest if dt(e, S) == mx]
        e_pick = min(cand, key=lambda e: (d(e, S), e))
        e_true = max(rest, key=lambda e: (d(e, S), e))
        print("  t=%d  S=%s  predicted gains %s  true gains %s  -> picks %s, "
              "true best %s" % (t, S, {e: str(dt(e, S)) for e in rest},
                                {e: str(d(e, S)) for e in rest}, e_pick, e_true))
        for ep in rest:
            if ep == e_pick or dt(e_pick, S) < dt(ep, S):
                continue
            A = d(e_pick, S)
            B = d(ep, S)
            C = d(ep, tuple(set(S) | {e_pick}))
            D = d(e_pick, tuple(set(S) | {ep}))
            At = dt(e_pick, S)
            Bt = dt(ep, S)
            Ct = dt(ep, tuple(set(S) | {e_pick}))
            Dt = dt(e_pick, tuple(set(S) | {ep}))
            tag = "t=%d e=%s e'=%s" % (t, e_pick, ep)
            check(tag + " swap identity A+C=B+D", A + C == B + D)
            check(tag + " band consequence B <= eta*A", B <= eta * A)
            check(tag + " order transfer Dt >= Ct", Dt >= Ct)
            check(tag + " (i) D >= C/eta  [%s >= %s]" % (D, C / eta), D >= C / eta)
            check(tag + " (ii) (1-1/eta)C >= B-A  [%s >= %s]"
                  % ((1 - F(1) / eta) * C, B - A), (1 - F(1) / eta) * C >= B - A)
            check(tag + " DR (submodularity) C <= B", C <= B)
            check(tag + " slack decomposition adds up",
                  eo * D - C / eu == (eo * D - Dt) + (At - Bt) + (Ct - C / eu))
            check(tag + " min form B-A <= (1-1/eta)min(B,C)",
                  B - A <= (1 - F(1) / eta) * min(B, C))
        S = tuple(set(S) | {e_pick})
    print("  final f(S^K) = %s" % f(S))
    best = max(f(c) for c in combinations(N, K))
    print("  OPT over all %d-subsets = %s ; ratio = %s" % (K, best, f(S) / best))


if __name__ == "__main__":
    part_A()
    part_B()
    part_C()
    part_D()
    part_E()
    print("\n=== %d failed checks ===" % len(failures))
    for x in failures:
        print("   " + x)
