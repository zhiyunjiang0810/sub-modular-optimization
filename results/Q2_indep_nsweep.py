"""Q2 part 0 (TASKS10): independent re-verification of the pivotal Q0/Q1
finding, before any general-K symbolic work:

  (P1) the relaxed-F LP value rho_K^{(n)} of the O-independent count-grid
       family equals rho_K = min_j V_j EXACTLY at n = 2K;
  (P2) rho_K^{(n)} is nondecreasing in n (staircase), NOT decreasing;
  (P3) for large n the value saturates STRICTLY ABOVE rho_K, so the route
       of TASKS10 premise (c) (rho_K^{(n)} -> rho_K as n -> infinity)
       fails for this family;
  (P4, consistency only) the saturation value matches the Q1 closed form
       W = 1 - q^j + (K-j) * max(q^j/(K eta), max_m D(m)),
       D(m) = q^j (nu^m/K - 1)/(eta (nu^m - 1) - m),  nu = eta/(eta-1),
       with saturation onset n >= K + T, T = j + m*, m* = ceil(eta K) - 1.

The LP calls reuse Q0_extract.solve_full (the only working entry point:
N4_relaxF_solve.solve hard-codes split='sqrt' and its canonical pass is
unbounded for split='eta1' without the Ghat pinning added there), but every
reference value (V_j, rho_K, W) is recomputed here in exact rationals,
independent of Q0_extract's helpers.  Vertex feasibility at n = 2K and at
the largest n is rechecked with Q0_extract.recheck (float, tol 1e-7).

Run:  python3 results/Q2_indep_nsweep.py          (exit 0 iff all PASS)
"""
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import Q0_extract as Q  # solve_full + recheck only

TOL = 1e-8          # LP float tolerance for equality checks
EXCESS_MIN = 1e-6   # strictness threshold for "saturates above rho_K"

fails = []


def check(name, ok, detail=""):
    print(("PASS" if ok else "FAIL"), name, detail)
    if not ok:
        fails.append(name)


# ---------------- exact references, written independently of Q0_extract ----
def V_exact(K, j, eta):
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return 1 - q ** j * (1 - Fr(K - j, K) / eta)


def rho_exact(K, eta):
    return min(V_exact(K, t, eta) for t in range(K))


def W_exact(K, eta):
    """Q1 closed-form saturation value (consistency reference, exact)."""
    j = K + 1 - math.ceil(eta)          # active segment index, non-integer eta
    assert 0 < Fr(eta) and Fr(eta) != int(eta), "use non-integer eta here"
    eta = Fr(eta)
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    nu = eta / (eta - 1)
    mstar = math.ceil(eta * K) - 1
    Dbase = q ** j / (K * eta)
    best = Dbase
    for m in range(1, mstar + 3):
        den = eta * (nu ** m - 1) - m
        if den <= 0:
            continue
        Dm = q ** j * (nu ** m / K - 1) / den
        best = max(best, Dm)
    return 1 - q ** j + (K - j) * best, j, mstar


# --------------------------------------------------------------- battery ---
# (K, eta, formula_checks?)  formula checks need non-integer eta with j >= 2
CONFIGS = [
    (3, Fr(3, 2), True),    # j = 2
    (4, Fr(3, 2), True),    # j = 3
    (4, Fr(5, 2), True),    # j = 2
    (5, Fr(5, 2), True),    # j = 3
    (4, Fr(2), False),      # integer endpoint: model checks P1-P3 only
    (3, Fr(5, 2), False),   # j = 1 domain: model checks P1-P3 only
]


def n_list(K, eta, formula):
    ns = set(range(2 * K, 2 * K + 3)) | {4 * K, 8 * K}
    if formula:
        mstar = math.ceil(eta * K) - 1
        j = K + 1 - math.ceil(eta)
        T = j + mstar
        ns |= set(range(K + T - 2, K + T + 3))
    return sorted(n for n in ns if n >= 2 * K)


def run_config(K, eta, formula):
    rho = rho_exact(K, eta)
    print(f"\n== K={K} eta={eta} rho_K={rho}={float(rho):.9f} ==")
    vals = {}
    for n in n_list(K, eta, formula):
        r = Q.solve_full(n, K, eta)
        vals[n] = r['ratio']
        viol = None
        if n in (2 * K, max(n_list(K, eta, formula))):
            viol = Q.recheck(r['F'], r['G'], r['Ghat'], r['bal'], K, float(eta))
            check(f"K={K} eta={eta} n={n} vertex feasible (recheck)",
                  not viol, str(viol) if viol else "")
        print(f"   n={n:3d}  value={r['ratio']:.10f}"
              f"  (value - rho_K = {r['ratio'] - float(rho):+.3e})")
    ns = sorted(vals)
    # P1: exact rho_K at n = 2K
    check(f"K={K} eta={eta} P1 value(2K) == rho_K",
          abs(vals[2 * K] - float(rho)) < TOL,
          f"{vals[2*K]:.10f} vs {float(rho):.10f}")
    # P2: nondecreasing in n
    mono = all(vals[b] >= vals[a] - 1e-9
               for a, b in zip(ns, ns[1:]))
    check(f"K={K} eta={eta} P2 nondecreasing in n", mono,
          str([(n, vals[n]) for n in ns]) if not mono else "")
    # P3: strict excess at the largest n
    nmax = ns[-1]
    check(f"K={K} eta={eta} P3 value({nmax}) > rho_K strictly",
          vals[nmax] - float(rho) > EXCESS_MIN,
          f"excess {vals[nmax] - float(rho):.3e}")
    if formula:
        W, j, mstar = W_exact(K, eta)
        T = j + mstar
        # P4a: saturation value matches W
        check(f"K={K} eta={eta} P4a value({nmax}) == W (closed form)",
              abs(vals[nmax] - float(W)) < TOL,
              f"{vals[nmax]:.10f} vs W={float(W):.10f}")
        # P4b: already saturated at n = K + T, and flat beyond
        flat = [n for n in ns if n >= K + T]
        satur = all(abs(vals[n] - float(W)) < TOL for n in flat)
        check(f"K={K} eta={eta} P4b flat at W for n >= K+T={K+T}", satur,
              str([(n, vals[n]) for n in flat]) if not satur else "")
        # P4c: strictly below W one step before the onset (staircase is real)
        if K + T - 1 in vals and K + T - 1 >= 2 * K:
            check(f"K={K} eta={eta} P4c value(K+T-1) < W strictly",
                  float(W) - vals[K + T - 1] > EXCESS_MIN,
                  f"gap {float(W) - vals[K+T-1]:.3e}")
    return vals


def main():
    for K, eta, formula in CONFIGS:
        run_config(K, eta, formula)
    print()
    print("ALL PASS" if not fails else f"FAILURES: {len(fails)}")
    for f in fails:
        print("  FAIL", f)
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
