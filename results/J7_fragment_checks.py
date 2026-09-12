"""J6/J7 gate day: exact verification of every J7 claim that is checkable
WITHOUT the undelivered file results/J7/linear_anysize.md (see
results/J6J7_gate.md for the gate ruling; J7's 8 identities, its corrected
truncation formula and its own instance cannot be verified until the file
arrives).

Part 1  The cited F3 counterexample, exact rationals: at K = 3,
        eta = 667/500 the old truncation rule m* = ceil(eta K) - 1 gives
        r_{t*} < 0 (family infeasible), the true argmax of D(m) is one
        smaller, the corrected candidate rule agrees with the argmax, and
        the family at the argmax is feasible (r_{t*} >= 0).  This is the
        same corner-point failure class as the four Q2 counterexamples
        (frac(eta K) small).
Part 2  Shape check of J7's claimed bound W_K = rho_K + exponentially
        small term: W - rho_K > 0 and geometrically decaying in K at
        fixed eta (successive-ratio table, K <= 14, two eta values).
        Supporting numerics only, no general-K claim adopted.
Part 3  Best-effort adversarial simulation in the ANY-SIZE linear regime,
        on the fully verified globally O-independent family of
        results/Q1_closed_form.py (the J7-shaped stand-in; J7's own
        instance is undelivered): worst-case (adversarial ties) forward
        predictive greedy, reverse greedy (deletion, queries of size up
        to n so outside A_lin), and max(forward, reverse), at K = 3,
        n = 8..12.  Check: every value is <= W_K(eta), the claimed
        any-size ceiling.

Run:  python3 results/J7_fragment_checks.py     (exit 0 iff ALL PASS)
"""
import math
import os
import sys
from fractions import Fraction as Fr
from functools import lru_cache

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import Q1_closed_form as Q1

fails = []


def check(name, ok, detail=""):
    print(("PASS" if ok else "FAIL"), name, detail)
    if not ok:
        fails.append(name)


def rho_exact(K, eta):
    eta = Fr(eta)
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return min(1 - q ** t * (1 - Fr(K - t, K) / eta) for t in range(K))


def Dm_table(K, eta, j, mmax=40):
    eta = Fr(eta)
    k1 = (K - 1) * eta + 1
    q = 1 - 1 / k1
    nu = eta / (eta - 1)
    Qj = q ** j
    out = {}
    for m in range(1, mmax + 1):
        den = eta * (nu ** m - 1) - m
        if den > 0:
            out[m] = Qj * (nu ** m / K - 1) / den
    return out, Qj, nu, q


def W_inf(K, eta):
    j = K + 1 - math.ceil(Fr(eta))
    D, Qj, _, _ = Dm_table(K, eta, j)
    eta = Fr(eta)
    best = max(Qj / (K * eta), max(D.values()))
    return 1 - Qj + (K - j) * best


# ------------------------------------------------- Part 1: F3 counterexample
def part1():
    K, eta = 3, Fr(667, 500)
    j = K + 1 - math.ceil(eta)                       # = 2
    m_old = math.ceil(eta * K) - 1                   # ceil(2001/500)=5 -> 4
    check("P1 j = 2", j == 2, f"j={j}")
    check("P1 old rule m* = 4", m_old == 4, f"m_old={m_old}")
    D, Qj, nu, q = Dm_table(K, eta, j)
    argmax = max(D, key=lambda m: D[m])
    check("P1 true argmax of D(m) is 3 (one below the old rule)",
          argmax == 3, f"argmax={argmax}")
    check("P1 D(4) < D(3) strictly", D[4] < D[3],
          f"D(3)={float(D[3]):.10f} D(4)={float(D[4]):.10f}")
    r_old = Qj - m_old * max(Qj / (K * eta), D[m_old])
    check("P1 old-rule family infeasible: r_{t*} = Q - 4 D(4) < 0",
          r_old < 0, f"r_t*={float(r_old):.6e} = {r_old}")
    r_new = Qj - argmax * D[argmax]
    check("P1 argmax family feasible: r_{t*} = Q - 3 D(3) >= 0",
          r_new >= 0, f"r_t*={float(r_new):.6e}")
    m_corr = min(m for m in range(1, 40)
                 if nu ** m * (eta * K - 1 - m) <= K * (eta - 1))
    check("P1 corrected candidate rule agrees with the argmax",
          m_corr == argmax, f"m_corr={m_corr}")
    mc = math.floor(eta * (K - 1)) + 1
    check("P1 excess threshold m_c = floor(eta(K-1))+1 = 3 (E(m)>0 iff m>2.668)",
          mc == 3 and D[3] > Qj / (K * eta) and D[2] <= Qj / (K * eta),
          f"m_c={mc}")


# ------------------------------- Part 2: W - rho_K exponentially small shape
def part2():
    for eta in (Fr(3, 2), Fr(667, 500)):
        gaps = {}
        for K in range(3, 15):
            gaps[K] = W_inf(K, eta) - rho_exact(K, eta)
            check(f"P2 W - rho_K > 0 at K={K} eta={eta}", gaps[K] > 0)
        dec = all(gaps[K + 1] < gaps[K] for K in range(4, 14))
        check(f"P2 gap strictly decreasing in K (K>=4) at eta={eta}", dec)
        print(f"    eta={eta}: successive ratios gap(K+1)/gap(K):",
              " ".join(f"{float(gaps[K+1]/gaps[K]):.4f}"
                       for K in range(3, 14)))


# ------------------------- Part 3: adversarial simulation, any-size regime
def part3():
    K = 3
    for eta in (Fr(3, 2), Fr(667, 500)):
        W = W_inf(K, eta)
        rho = rho_exact(K, eta)
        for n in range(8, 13):
            sol = Q1.instantiate(K, eta, n)
            F, G = sol['F'], sol['G']
            X = n - K

            @lru_cache(maxsize=None)
            def fwd(x, y):
                if x + y == K:
                    return F[x][y]
                cands = []
                if x < X:
                    cands.append((G[x + 1][y] - G[x][y], (x + 1, y)))
                if y < K:
                    cands.append((G[x][y + 1] - G[x][y], (x, y + 1)))
                best = max(c[0] for c in cands)
                return min(fwd(*c[1]) for c in cands if c[0] == best)

            @lru_cache(maxsize=None)
            def rev(x, y):
                if x + y == K:
                    return F[x][y]
                cands = []
                if x >= 1 and x + y - 1 >= K:
                    cands.append((G[x][y] - G[x - 1][y], (x - 1, y)))
                if y >= 1 and x + y - 1 >= K:
                    cands.append((G[x][y] - G[x][y - 1], (x, y - 1)))
                # smallest predicted loss is removed; adversary breaks ties
                best = min(c[0] for c in cands)
                return min(rev(*c[1]) for c in cands if c[0] == best)

            wf, wr = fwd(0, 0), rev(X, K)
            wmax = max(wf, wr)
            check(f"P3 K=3 eta={eta} n={n} max(fwd,rev) <= W",
                  wmax <= W,
                  f"fwd={float(wf):.6f} rev={float(wr):.6f} "
                  f"W={float(W):.6f} rho={float(rho):.6f}")
            fwd.cache_clear(); rev.cache_clear()


def main():
    part1()
    part2()
    part3()
    print()
    print("ALL PASS" if not fails else f"FAILURES: {len(fails)}")
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
