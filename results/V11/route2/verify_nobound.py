#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROUTE-TWO blind verification for prop:necessity (no bound, no guarantee).

Exact arithmetic only (fractions.Fraction / sympy).  Floats appear in printouts only.

Checks
  C1 [VERIFIED-SYMBOLIC]  K/n + K^2/(n(n-K)) == K/(n-K)   (randomized bookkeeping identity)
  C2 [VERIFIED-EXHAUSTIVE] for the family f_A(S) = |S cap A| + w |S \ A|, w = K/(n-K):
        (a) f_A is normalized, nonnegative, monotone, submodular on the full lattice
        (b) O* = A is an optimal K-set, f_A(O*) = K
        (c) the single predictor ftilde(S) = |S| meets Definition 1 with
            (eta_u, eta_o) = (1, (n-K)/K) and these factors are the minimal ones,
            so eta = (n-K)/K
        (d) for EVERY T with |T| <= K there is an A with |A| = K and
            f_A(T) <= K/(n-K) * f_A(A)      (deterministic claim)
  C3 [VERIFIED-EXHAUSTIVE] with eps = K^2/(n(n-K)) and g_A(S) = |S cap A| + eps |S \ A|:
        for EVERY T with |T| <= K the average over all A of size K satisfies
            avg_A g_A(T) <= K/(n-K) * K     (randomized / Yao claim)
        and eta(g) = 1/eps = n(n-K)/K^2
  C4 [VERIFIED-EXHAUSTIVE] the K=3, eta=3/2 walk-through (w = 2/3): the claimed bound
        K/(n-K) is met exactly for n in {6,7} and violated for n >= 8, i.e. at fixed eta
        the family stops certifying the bound once n grows.
  C5 [VERIFIED-EXHAUSTIVE] for n < 2K the construction fails: min over A of
        f_A(T)/f_A(A) >= (2K-n)/K > 0 for |T| = K.

Run:  python3 results/V11/route2/verify_nobound.py
"""

from fractions import Fraction as F
from itertools import combinations, chain
import sympy as sp

FAIL = []


def check(name, cond, detail=""):
    if not cond:
        FAIL.append(f"{name}: {detail}")
        print(f"  [FAILED] {name} {detail}")
    return cond


def subsets(ground):
    for r in range(len(ground) + 1):
        for S in combinations(ground, r):
            yield frozenset(S)


def modular(A, w):
    """f(S) = |S cap A| + w |S \\ A| as a closure."""
    return lambda S: len(S & A) * F(1) + w * len(S - A)


# ---------------------------------------------------------------- C1 symbolic
def c1():
    n, K = sp.symbols("n K", positive=True)
    expr = sp.simplify(K / n + K**2 / (n * (n - K)) - K / (n - K))
    ok = check("C1 identity K/n + K^2/(n(n-K)) = K/(n-K)", sp.simplify(expr) == 0, str(expr))
    print(f"C1 [VERIFIED-SYMBOLIC] residual = {expr}  ok={ok}")


# ------------------------------------------------- lattice property checkers
def lattice_props(N, f):
    """normalized, nonnegative, monotone, submodular -- full lattice, exact."""
    ok = True
    ok &= f(frozenset()) == 0
    for S in subsets(N):
        ok &= f(S) >= 0
        for e in N:
            if e in S:
                continue
            ok &= f(S | {e}) - f(S) >= 0                      # monotone
    for S in subsets(N):
        for T in subsets(N):
            if not S <= T:
                continue
            for e in N:
                if e in T:
                    continue
                dS = f(S | {e}) - f(S)
                dT = f(T | {e}) - f(T)
                ok &= dS >= dT                                 # submodular
    return ok


def eta_factors(N, f, ft):
    """minimal (eta_u, eta_o) of Definition 1 over ALL S and e not in S; None if support mismatch."""
    eu = F(0)
    eo = F(0)
    for S in subsets(N):
        for e in N:
            if e in S:
                continue
            d = f(S | {e}) - f(S)
            dt = ft(S | {e}) - ft(S)
            if (d == 0) != (dt == 0):
                return None                                    # support condition violated
            if d == 0:
                continue
            eu = max(eu, F(d) / F(dt))                          # d/eta_u <= dt
            eo = max(eo, F(dt) / F(d))                          # dt <= eta_o d
    return (max(eu, F(1, 1) * 0 + eu), eo) if False else (eu, eo)


# ------------------------------------------------- C2 deterministic exhaustion
def c2(nmax=8, kmax=3, verbose=True):
    print("C2 [VERIFIED-EXHAUSTIVE] deterministic family, w = K/(n-K)")
    for K in range(1, kmax + 1):
        for n in range(2 * K, nmax + 1):
            N = list(range(n))
            w = F(K, n - K)
            bound = F(K, n - K)
            ft = lambda S: F(len(S))
            Asets = [frozenset(A) for A in combinations(N, K)]

            # (a)(b)(c) on one representative A (family is symmetric under relabelling)
            A0 = Asets[0]
            f0 = modular(A0, w)
            check(f"C2a n={n} K={K} lattice", lattice_props(N, f0))
            opt = max(f0(frozenset(S)) for S in combinations(N, K))
            check(f"C2b n={n} K={K} O*=A", f0(A0) == K and opt == K, f"f(A)={f0(A0)} opt={opt}")
            ef = eta_factors(N, f0, ft)
            check(f"C2c n={n} K={K} eta", ef is not None and ef == (F(1), F(n - K, K)), f"got {ef}")

            # (d) every deterministic output T of size <= K
            worst = F(0)
            for size in range(0, K + 1):
                for T in combinations(N, size):
                    T = frozenset(T)
                    best_for_adv = min(modular(A, w)(T) for A in Asets)   # adversary picks A
                    ratio = F(best_for_adv, 1) / F(K)
                    worst = max(worst, ratio)
                    check(f"C2d n={n} K={K} T={sorted(T)}", ratio <= bound,
                          f"ratio={ratio} > {bound}")
            if verbose:
                print(f"  n={n} K={K}: eta={F(n-K,K)}  max_T min_A f_A(T)/f_A(O*) = {worst} "
                      f"(= {float(worst):.4f}), claimed bound K/(n-K) = {bound}")


# -------------------------------------------------- C3 randomized exhaustion
def c3(nmax=8, kmax=3):
    print("C3 [VERIFIED-EXHAUSTIVE] randomized / averaging, eps = K^2/(n(n-K))")
    for K in range(1, kmax + 1):
        for n in range(2 * K, nmax + 1):
            N = list(range(n))
            eps = F(K * K, n * (n - K))
            bound = F(K, n - K)
            Asets = [frozenset(A) for A in combinations(N, K)]
            m = len(Asets)
            worst = F(0)
            for size in range(0, K + 1):
                for T in combinations(N, size):
                    T = frozenset(T)
                    tot = sum(modular(A, eps)(T) for A in Asets)
                    avg_ratio = (tot / m) / F(K)
                    worst = max(worst, avg_ratio)
                    check(f"C3 n={n} K={K} T={sorted(T)}", avg_ratio <= bound,
                          f"avg ratio={avg_ratio} > {bound}")
            # eta of the eps-instance
            A0 = Asets[0]
            ef = eta_factors(N, modular(A0, eps), lambda S: F(len(S)))
            check(f"C3 eta n={n} K={K}", ef == (F(1), F(1, 1) / eps), f"got {ef}")
            print(f"  n={n} K={K}: eps={eps} eta={1/eps}  max_T avg_A ratio = {worst} "
                  f"(= {float(worst):.4f}) <= {bound}")


# --------------------------------------------------- C4 K=3, eta=3/2 walk-through
def c4():
    print("C4 [VERIFIED-EXHAUSTIVE] K=3, eta=3/2 (w = 2/3) as n grows")
    K = 3
    w = F(2, 3)
    for n in range(2 * K, 11):
        N = list(range(n))
        Asets = [frozenset(A) for A in combinations(N, K)]
        T = frozenset(range(K))                     # any K-set; symmetry makes the choice free
        adv = min(modular(A, w)(T) for A in Asets)
        ratio = F(adv, 1) / F(K)
        bound = F(K, n - K)
        ef = eta_factors(N, modular(Asets[0], w), lambda S: F(len(S)))
        certifies = ratio <= bound
        print(f"  n={n}: eta={ef[0]*ef[1]}  f(T)={adv} f(O*)={K} ratio={ratio} "
              f"bound K/(n-K)={bound}  certifies={certifies}")
        check("C4 eta is 3/2", ef == (F(1), F(3, 2)), f"got {ef}")
        check(f"C4 n={n} expected certification", certifies == (n <= 7), "")


# ------------------------------------------------------- C5 why n >= 2K is needed
def c5():
    print("C5 [VERIFIED-EXHAUSTIVE] n < 2K: forced overlap, ratio bounded away from 0")
    for K in range(2, 5):
        for n in range(K, 2 * K):
            N = list(range(n))
            w = F(1, 100)                            # any w; overlap term dominates
            Asets = [frozenset(A) for A in combinations(N, K)]
            T = frozenset(range(K))
            adv = min(modular(A, w)(T) for A in Asets)
            lo = F(2 * K - n, K)
            ratio = F(adv, 1) / F(K)
            check(f"C5 n={n} K={K}", ratio >= lo, f"ratio={ratio} < {lo}")
            print(f"  n={n} K={K}: min_A ratio = {ratio} >= (2K-n)/K = {lo}")


if __name__ == "__main__":
    c1()
    c2()
    c3()
    c4()
    c5()
    print()
    if FAIL:
        print(f"FAILURES ({len(FAIL)}):")
        for x in FAIL:
            print("  -", x)
    else:
        print("ALL CHECKS PASS (exact arithmetic).")
