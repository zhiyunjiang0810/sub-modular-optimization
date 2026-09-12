"""Q3 byproduct table (TASKS10): the O-independent count-grid family's
saturation value W sits strictly BETWEEN rho_K and the arbitrary-size
explicit-instance bound U_K, so it is a candidate STRONGER ceiling for the
greedy-budget class A_lin than the U_K used in cor:greedybudget.

  rho_K(eta) = min_j V_j,   V_j = 1 - q^j (1 - (K-j)/(K eta)),
  W(K, eta)  = 1 - q^j* + (K-j*) max(q^j*/(K eta), max_m D(m)),
               j* = K + 1 - ceil(eta)  (non-integer eta),
               D(m) = q^j (nu^m/K - 1)/(eta (nu^m - 1) - m),
  U_K(eta)   = 1 - (1 - 1/((K-1) eta + 1))^K.

W values are the LP saturation values confirmed in Q2_indep_nsweep.py
(bit-match at every tested config); this script only tabulates the exact
closed forms.  All arithmetic exact, floats for display only.

Run:  python3 results/Q3_W_vs_UK.py
"""
import math
import sys
from fractions import Fraction as Fr


def refs(K, eta):
    eta = Fr(eta)
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    UK = 1 - (1 - 1 / k1) ** K
    rho = min(1 - q ** j * (1 - Fr(K - j, K) / eta) for j in range(K))
    j = K + 1 - math.ceil(eta)
    nu = eta / (eta - 1)
    D = q ** j / (K * eta)
    for m in range(1, math.ceil(eta * K) + 3):
        den = eta * (nu ** m - 1) - m
        if den > 0:
            D = max(D, q ** j * (nu ** m / K - 1) / den)
    W = 1 - q ** j + (K - j) * D
    return rho, W, UK


def main():
    print(f"{'K':>3} {'eta':>6} | {'rho_K':>12} {'W':>12} {'U_K':>12} "
          f"| {'W-rho_K':>10} {'U_K-W':>10} {'U_K-rho_K':>10}")
    ok = True
    for K, eta in [(3, Fr(3, 2)), (4, Fr(3, 2)), (4, Fr(5, 2)),
                   (5, Fr(5, 2)), (5, Fr(7, 2)), (8, Fr(7, 2)),
                   (8, Fr(3, 2)), (12, Fr(5, 2))]:
        rho, W, UK = refs(K, eta)
        print(f"{K:>3} {str(eta):>6} | {float(rho):12.9f} {float(W):12.9f} "
              f"{float(UK):12.9f} | {float(W - rho):10.3e} "
              f"{float(UK - W):10.3e} {float(UK - rho):10.3e}")
        if not (rho < W < UK):
            ok = False
            print(f"    ORDER VIOLATION at K={K} eta={eta}")
    print()
    print("strict order rho_K < W < U_K on all rows:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
