"""J7 (18) finite-configuration oracle: exact-rational verification that

    0 < W_K(eta) - rho_K(eta) < 1/(K (e^{K-1} - K - 1))      (K >= 3)

on the same 99-config sweep as results/J7_grid_check.py.  Decision is fully
exact: e is replaced by the rational UPPER bound e < B = 2718281829/10^9,
which makes 1/(K(B^{K-1}-K-1)) a rational LOWER bound on the right-hand
side; gap < that lower bound implies the claim.  (General-K status of (18)
is the symbolic pipeline's S10; this script is the finite cross-check.)

Run:  python3 results/J7_bound18_check.py     (exit 0 iff ALL PASS)
"""
import math
import sys
from fractions import Fraction as Fr

E_UP = Fr(2718281829, 10 ** 9)          # e < E_UP (e = 2.718281828459...)

fails = []


def check(name, ok, detail=""):
    if not ok:
        fails.append(name)
        print("FAIL", name, detail)


def gap_exact(K, eta):
    eta = Fr(eta)
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    nu = eta / (eta - 1)
    j = max(0, min(K - 1, K + 1 - math.ceil(eta)))
    Q = q ** j
    m = next(z for z in range(1, 10 * K * (int(eta) + 2) + 10)
             if (K * eta - z - 1) * nu ** z - K * (eta - 1) <= 0)
    Bm = eta * (nu ** m - 1) - m
    return (K - j) * Q * (m - eta * (K - 1)) / (K * eta * Bm)


def main():
    n = 0
    for K in range(3, 13):
        rhs_lower = 1 / (K * (E_UP ** (K - 1) - K - 1))
        etas = {Fr(21, 20), Fr(5, 4), Fr(3, 2), Fr(2), Fr(5, 2), Fr(3),
                Fr(667, 500), Fr(3 * K - 1, 3), Fr(K), Fr(2 * K + 1, 2)}
        for eta in sorted(e for e in etas if e > 1):
            g = gap_exact(K, eta)
            check(f"(18) K={K} eta={eta}", 0 < g < rhs_lower,
                  f"gap={float(g):.3e} bound={float(rhs_lower):.3e}")
            n += 1
    print(f"configs: {n}")
    print("ALL PASS" if not fails else f"FAILURES: {len(fails)}")
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
