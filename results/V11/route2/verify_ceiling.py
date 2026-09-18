"""ROUTE-TWO verification for thm:ceiling (blind re-derivation).

Sections
  A  [VERIFIED-SYMBOLIC] the two closed forms of C*_{n,K}(eta) agree with
     K/(K+(eta-1)min{K,n-K}), and the adversary family's ratio equals it.
  B  [VERIFIED-EXHAUSTIVE] the adversary family: exact rational instance,
     band exactly (eta_u,eta_o), ratio exactly C*_{n,K}(eta).
  C  [VERIFIED-EXHAUSTIVE] the per-instance tight family for every j.
  D  [VERIFIED-EXHAUSTIVE] random coverage instances: every tilde-f-maximal
     K-set S satisfies f(S) >= K/(K+(eta-1)|O*\\S|) f(O*), and each step
     (J),(K),(L),(M) of the hand proof holds.
  E  [VERIFIED-SYMBOLIC] the randomized (Yao) value of the same family.

Exact arithmetic only (fractions.Fraction / sympy); floats never decide.
Rerun:  python3 verify_ceiling.py
"""
import itertools
import random
from fractions import Fraction as Fr

import sympy as sp

FAIL = []


def check(cond, msg):
    if not cond:
        FAIL.append(msg)
        print("  FAIL:", msg)


# ---------------------------------------------------------------- section A
def section_A():
    print("[A] symbolic identities")
    n, K, eta = sp.symbols("n K eta", positive=True)
    # branch n <= 2K  ->  min{K,n-K} = n-K
    lhs = K / (K + (eta - 1) * (n - K))
    rhs = K / ((2 * K - n) + (n - K) * eta)
    check(sp.simplify(lhs - rhs) == 0, "A1 branch K<=n<=2K")
    # branch n >= 2K  ->  min{K,n-K} = K
    lhs2 = K / (K + (eta - 1) * K)
    check(sp.simplify(lhs2 - 1 / eta) == 0, "A2 branch n>=2K")
    # adversary family ratio
    eu, eo, h = sp.symbols("eta_u eta_o h", positive=True)
    ratio = (K / eo) / (h * eu + (K - h) / eo)
    target = K / (K + (eu * eo - 1) * h)
    check(sp.simplify(ratio - target) == 0, "A3 adversary ratio = C*")
    print("  A1,A2,A3 ok")


# ---------------------------------------------------------------- section B
def modular(weights):
    """f(A) = sum of weights over A; returns f as a dict on bitmasks."""
    n = len(weights)
    f = {}
    for A in range(1 << n):
        f[A] = sum(weights[i] for i in range(n) if A & (1 << i))
    return f


def card(A):
    return bin(A).count("1")


def band_exact(f, g, n, eta_u, eta_o):
    """returns (feasible, lower_attained, upper_attained) for
    d/eta_u <= gd <= eta_o d on all single-element marginals."""
    feas, lo, up = True, False, False
    for A in range(1 << n):
        for e in range(n):
            if A & (1 << e):
                continue
            Ae = A | (1 << e)
            d = f[Ae] - f[A]
            gd = g[Ae] - g[A]
            if gd < d / eta_u or gd > eta_o * d:
                feas = False
            if gd == d / eta_u:
                lo = True
            if gd == eta_o * d:
                up = True
    return feas, lo, up


def best_Kset(f, n, K):
    best = max(f[A] for A in range(1 << n) if card(A) == K)
    args = [A for A in range(1 << n) if card(A) == K and f[A] == best]
    return best, args


def section_B():
    print("[B] adversary family, exact rationals")
    for n in range(2, 9):
        for K in range(2, n + 1):
            for eta_u, eta_o in [(Fr(3, 2), Fr(1)), (Fr(2), Fr(1)),
                                 (Fr(3), Fr(2)), (Fr(1), Fr(3, 2))]:
                eta = eta_u * eta_o
                h = min(K, n - K)
                if h == 0:
                    continue
                # H = last h elements; the algorithm's output T avoids H
                w = [Fr(1) / eta_o] * (n - h) + [eta_u] * h
                f = modular(w)
                g = {A: Fr(card(A)) for A in range(1 << n)}
                feas, lo, up = band_exact(f, g, n, eta_u, eta_o)
                check(feas, f"B feasible n={n} K={K} eta={eta}")
                check(lo and up, f"B error exactly (eta_u,eta_o) n={n} K={K}")
                Topt = sum(1 << i for i in range(K))       # K light elements
                fO, _ = best_Kset(f, n, K)
                ratio = f[Topt] / fO
                target = Fr(K) / (Fr(K) + (eta - 1) * h)
                check(ratio == target, f"B ratio n={n} K={K} eta={eta}: "
                                       f"{ratio} != {target}")
    print("  all (n,K,eta_u,eta_o) grids ok" if not FAIL else "  see FAILs")


# ---------------------------------------------------------------- section C
def section_C():
    print("[C] per-instance tight family for each j")
    for n in range(2, 9):
        for K in range(2, n + 1):
            for eta in (Fr(3, 2), Fr(2), Fr(3)):
                eta_u, eta_o = eta, Fr(1)
                for j in range(0, min(K, n - K) + 1):
                    # S = first K elements (weight 1); O* \ S = next j (weight eta)
                    w = [Fr(1)] * K + [eta] * j + [Fr(0)] * (n - K - j)
                    f = modular(w)
                    gw = [eta_o * Fr(1)] * K + [eta / eta_u] * j + [Fr(0)] * (n - K - j)
                    g = modular(gw)
                    feas, lo, up = band_exact(f, g, n, eta_u, eta_o)
                    check(feas, f"C band n={n} K={K} j={j}")
                    S = sum(1 << i for i in range(K))
                    gbest, gargs = best_Kset(g, n, K)
                    check(S in gargs, f"C S is tilde-f-maximal n={n} K={K} j={j}")
                    fO, fargs = best_Kset(f, n, K)
                    Ostar = sum(1 << i for i in range(K - j)) + \
                            sum(1 << i for i in range(K, K + j))
                    check(f[Ostar] == fO, f"C O* optimal n={n} K={K} j={j}")
                    jj = card(Ostar & ~S)
                    check(jj == j, f"C |O*-S| n={n} K={K} j={j}")
                    ratio = f[S] / fO
                    target = Fr(K) / (Fr(K) + (eta - 1) * j)
                    check(ratio == target,
                          f"C ratio n={n} K={K} j={j}: {ratio} != {target}")
    print("  tight for every j in 0..min(K,n-K)" if not FAIL else "  see FAILs")


# ---------------------------------------------------------------- section D
def coverage(n, universe, sets, weights):
    f = {}
    for A in range(1 << n):
        cov = set()
        for i in range(n):
            if A & (1 << i):
                cov |= sets[i]
        f[A] = sum(weights[u] for u in cov)
    return f


def section_D(trials=400, seed=20260918):
    print("[D] random coverage instances: claim + every proof step")
    rng = random.Random(seed)
    for t in range(trials):
        n = rng.choice([4, 5, 6])
        K = rng.choice([2, 3])
        if K >= n:
            continue
        eta = rng.choice([Fr(3, 2), Fr(2), Fr(3), Fr(5, 2)])
        eta_u, eta_o = eta, Fr(1)          # normalised band  d/eta <= gd <= d
        m = rng.randint(2, 6)
        universe = list(range(m))
        sets = [set(u for u in universe if rng.random() < 0.5) for _ in range(n)]
        w = {u: Fr(rng.randint(0, 6)) for u in universe}
        wt = {u: w[u] * Fr(rng.randint(1, int(eta.denominator) * 4),
                           int(eta.denominator) * 4) for u in universe}
        # keep tilde weights inside [w/eta, w]
        wt = {u: max(w[u] / eta, min(w[u], wt[u])) for u in universe}
        f = coverage(n, universe, sets, w)
        g = coverage(n, universe, sets, wt)
        feas, _, _ = band_exact(f, g, n, eta_u, eta_o)
        check(feas, f"D band trial {t}")
        fO, fargs = best_Kset(f, n, K)
        if fO == 0:
            continue
        _, gargs = best_Kset(g, n, K)
        for S in gargs:                     # adversarial tie breaking
            Ostar = fargs[0]
            for Ostar in fargs:
                j = card(Ostar & ~S)
                target = Fr(K) / (Fr(K) + (eta - 1) * j)
                check(f[S] >= target * fO,
                      f"D claim trial {t} n={n} K={K} eta={eta} j={j} "
                      f"f(S)={f[S]} f(O*)={fO}")
                # step (J): f(O*)-f(S) <= theta (f(S u O*) - f(S))
                theta = 1 - Fr(1) / eta
                check(f[Ostar] - f[S] <= theta * (f[S | Ostar] - f[S]),
                      f"D step J trial {t}")
                # step (K): f(S u O*) - f(S) <= sum_{o in O*\S} d_o(S)
                tot = sum(f[S | (1 << o)] - f[S] for o in range(n)
                          if (Ostar & ~S) & (1 << o))
                check(f[S | Ostar] - f[S] <= tot, f"D step K trial {t}")
                # step (L): d_o(S) <= eta * d_s(S-s) for all s in S, o not in S
                mmin = min(f[S] - f[S & ~(1 << s)] for s in range(n) if S & (1 << s))
                for o in range(n):
                    if S & (1 << o):
                        continue
                    check(f[S | (1 << o)] - f[S] <= eta * mmin,
                          f"D step L trial {t} o={o}")
                # step (M): sum_s d_s(S-s) <= f(S)  =>  mmin <= f(S)/K
                ssum = sum(f[S] - f[S & ~(1 << s)] for s in range(n) if S & (1 << s))
                check(ssum <= f[S], f"D step M trial {t}")
                check(mmin * K <= f[S], f"D step M' trial {t}")
    print(f"  {trials} random instances checked")


# ---------------------------------------------------------------- section E
def section_E():
    print("[E] randomized (Yao) value of the same family")
    n, K, h, eu, eo = sp.symbols("n K h eta_u eta_o", positive=True)
    eta = eu * eo
    ET = K * (h / n * eu + (n - h) / n / eo)
    fO = h * eu + (K - h) / eo
    ratio = sp.simplify(ET / fO)
    closed = K * (n + (eta - 1) * h) / (n * (K + (eta - 1) * h))
    check(sp.simplify(ratio - closed) == 0, "E1 Yao ratio closed form")
    # strictly above C* whenever eta>1 and h>=1
    Cstar = K / (K + (eta - 1) * h)
    gap = sp.simplify(closed / Cstar)
    check(sp.simplify(gap - (n + (eta - 1) * h) / n) == 0, "E2 gap factor")
    print("  E1,E2 ok:  randomized value = C* * (n+(eta-1)h)/n")


if __name__ == "__main__":
    section_A()
    section_B()
    section_C()
    section_D()
    section_E()
    print()
    if FAIL:
        print(f"{len(FAIL)} FAILURES")
        for x in FAIL[:20]:
            print("  -", x)
    else:
        print("ALL CHECKS PASSED (exact arithmetic)")
