"""L1: greedy-budget corollary oracle (TASKS7).

One-click reproduction of every number and every symbolic claim behind
cor:greedybudget (ledger card T10b):

  Section 0  the deliverable table results/L1_table.csv, exact rationals:
             K in {2,3,4,5,8,10,20} x eta in {1.25,1.5,2,3,5}:
             rho_K, U_K, min{U_K, 1/eta}, gap U_K - rho_K.        [exact]
  Section 1  the counting chain of the corollary, sympy:
             pair probability, per-query bound, union over Q = nK,
             output intersection, the explicit condition n >= 4K^5,
             thetabar >= 1 at tau = 1, H_{K,1} = U_K, U_K > V_{K-1},
             greedy query count.                        [VERIFIED-SYMBOLIC]
  Section 2  gap asymptotics: series of U_K and of the active branch
             V_{K-m} in 1/K; the 1/K coefficients cancel and
             U_K - rho_K = c'(eta)/K^2 + O(1/K^3) with
             c'(eta) = e^{-1/eta} m (2 eta - m - 1)/(2 eta^2),
             m = floor(eta); both branches agree at integer eta.
                                                       [VERIFIED-SYMBOLIC,
                              conditional on thm:exact via the closed form]
  Section 3  numeric convergence, exact Fractions up to K = 400:
             K*(U_K - rho_K) -> 0 and K^2*(U_K - rho_K) -> c'(eta),
             with one Richardson step.

Outputs: results/L1_table.csv, results/L1_gap.json.  Exit 0 iff all pass.
Run: python3 results/L1_table.py
"""
import csv
import json
import math
import os
import sys
from fractions import Fraction

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
fails = []


def check(name, ok, detail=""):
    print(("PASS" if ok else "FAIL"), name, detail)
    if not ok:
        fails.append(name)


# Closed forms (same as results/H_B_asymptotic.py, T6 card), exact rational.
def V_exact(K, j, eta):
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return 1 - q ** j * (1 - Fraction(K - j, K) / eta)


def rho_exact(K, eta):
    return min(V_exact(K, j, eta) for j in range(0, K))


def U_exact(K, eta):
    k1 = (K - 1) * eta + 1
    return 1 - ((k1 - 1) / k1) ** K


# ----------------------------------------------------------------------------
# Section 0: the table
# ----------------------------------------------------------------------------
KS = [2, 3, 4, 5, 8, 10, 20]
ETAS = [Fraction(5, 4), Fraction(3, 2), Fraction(2), Fraction(3), Fraction(5)]

print("=" * 78)
print("Section 0  table  results/L1_table.csv  (exact rationals)")
print("=" * 78)
rows = []
ok_order = True
ok_ceiling = True
for K in KS:
    for eta in ETAS:
        rho = rho_exact(K, eta)
        U = U_exact(K, eta)
        cap = min(U, 1 / eta)
        gap = U - rho
        ok_order &= (gap > 0)                     # eta > 1 everywhere here
        if eta >= K:
            ok_ceiling &= (rho == 1 / eta == cap)
        rows.append({
            "K": K, "eta": float(eta),
            "rho_K": float(rho), "U_K": float(U),
            "min_UK_inv_eta": float(cap), "gap_UK_minus_rho": float(gap),
            "rho_K_exact": str(rho), "U_K_exact": str(U),
            "gap_exact": str(gap),
        })
with open(os.path.join(HERE, "L1_table.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
check("table: U_K - rho_K > 0 at all 35 points (eta > 1)", ok_order)
check("table: eta >= K  =>  rho_K = 1/eta = min{U_K, 1/eta}", ok_ceiling,
      "(greedy attains the class ceiling exactly)")
print(f"  wrote {len(rows)} rows -> results/L1_table.csv")

# ----------------------------------------------------------------------------
# Section 1: the counting chain, symbolically
# ----------------------------------------------------------------------------
print()
print("=" * 78)
print("Section 1  counting chain of cor:greedybudget  [VERIFIED-SYMBOLIC]")
print("=" * 78)
K, n, eta = sp.symbols("K n eta", positive=True)

# (a) pair probability: K(K-1)/(n(n-1)) <= (K/n)^2, slack K(n-K)/(n^2(n-1)).
lhs = K * (K - 1) / (n * (n - 1))
slack = sp.simplify((K / n) ** 2 - lhs)
check("(a) (K/n)^2 - K(K-1)/(n(n-1)) == K(n-K)/(n^2(n-1))",
      sp.simplify(slack - K * (n - K) / (n ** 2 * (n - 1))) == 0,
      "(nonnegative for K <= n)")

# (b) per query: at most C(K,2) pairs, each with probability <= (K/n)^2;
#     union over Q = nK queries.
per_query = sp.binomial(K, 2) * (K / n) ** 2
union = sp.simplify(n * K * per_query)
check("(b) nK * C(K,2) (K/n)^2 == K^4 (K-1)/(2n)",
      sp.simplify(union - K ** 4 * (K - 1) / (2 * n)) == 0)
check("(b') K^4 (K-1)/(2n) <= K^5/(2n), slack K^4/(2n)",
      sp.simplify(K ** 5 / (2 * n) - union - K ** 4 / (2 * n)) == 0)

# (c) the explicit condition n >= 4K^5: both failure terms at the boundary.
at_boundary = union.subs(n, 4 * K ** 5)
check("(c) query-union term at n = 4K^5:  K^4(K-1)/(8K^5) <= 1/8",
      sp.simplify(sp.Rational(1, 8) - at_boundary
                  - sp.Rational(1, 8) / K) == 0,
      "(slack 1/(8K))")
out_term = (K ** 2 / n).subs(n, 4 * K ** 5)
check("(c') output term at n = 4K^5:  K^2/(4K^5) == 1/(4K^3)",
      sp.simplify(out_term - 1 / (4 * K ** 3)) == 0)
# 1/(4K^3) <= 1/32 for K >= 2:  1/32 - 1/(4K^3) = (K^3 - 8)/(32 K^3).
check("(c'') 1/32 - 1/(4K^3) == (K^3-8)/(32K^3)  (>= 0 for K >= 2)",
      sp.simplify(sp.Rational(1, 32) - 1 / (4 * K ** 3)
                  - (K ** 3 - 8) / (32 * K ** 3)) == 0)
check("(c''') total 1/8 + 1/32 == 5/32 < 1/2",
      sp.Rational(1, 8) + sp.Rational(1, 32) == sp.Rational(5, 32)
      and sp.Rational(5, 32) < sp.Rational(1, 2))

# (d) tau = 1 calibration: thetabar - 1 == (eta-1)(K-1)/K  (>= 0 iff eta >= 1).
thetabar = (eta * (K - 1) + 1) / K
check("(d) thetabar(tau=1) - 1 == (eta-1)(K-1)/K",
      sp.simplify(thetabar - 1 - (eta - 1) * (K - 1) / K) == 0)

# (e) H_{K,1} == U_K by substitution.
tau = sp.symbols("tau", positive=True)
H = 1 - (1 - 1 / (eta * (K - tau) + 1)) ** K
U = 1 - (1 - 1 / (eta * (K - 1) + 1)) ** K
check("(e) H_{K,tau}|_{tau=1} == U_K", sp.simplify(H.subs(tau, 1) - U) == 0)

# (f) U_K - V_{K-1} == q^{K-1} (eta-1)/(K eta k1)  (N1 part G identity).
#     sympy does not merge symbolic exponents q^{K-1} * q on its own, so the
#     check is decomposed: (f1) 1 - 1/k1 == q, hence U_K = 1 - q^K; then
#     U_K - V_{K-1} = q^{K-1} [(1 - 1/(K eta)) - q], and (f2) identifies the
#     bracket.  Together they give the claim with exact exponent arithmetic.
k1 = (K - 1) * eta + 1
q = (K - 1) * eta / k1
check("(f1) 1 - 1/k1 == q  (so U_K = 1 - q^K)",
      sp.simplify((1 - 1 / k1) - q) == 0)
check("(f2) (1 - 1/(K eta)) - q == (eta-1)/(K eta k1)  (> 0 for eta > 1)",
      sp.simplify((1 - 1 / (K * eta)) - q - (eta - 1) / (K * eta * k1)) == 0)

# (g) greedy query count fits the budget: nK - (Kn - K(K-1)/2) = K(K-1)/2 >= 0.
check("(g) nK - (Kn - K(K-1)/2) == K(K-1)/2  (greedy is in A_lin)",
      sp.simplify(n * K - (K * n - K * (K - 1) / 2) - K * (K - 1) / 2) == 0)

# ----------------------------------------------------------------------------
# Section 2: gap asymptotics U_K - rho_K = c'(eta)/K^2 + O(1/K^3)
# ----------------------------------------------------------------------------
print()
print("=" * 78)
print("Section 2  series of U_K and V_{K-m}; c'(eta)  [VERIFIED-SYMBOLIC,")
print("           conditional on thm:exact through the closed form rho_K]")
print("=" * 78)
eps, m = sp.symbols("epsilon m", positive=True)
Ki = 1 / eps
k1i = (Ki - 1) * eta + 1
qi = (Ki - 1) * eta / k1i

Usym = 1 - sp.exp(Ki * sp.log(1 - 1 / k1i))
Vsym = 1 - sp.exp((Ki - m) * sp.log(qi)) * (1 - m / (Ki * eta))

serU = sp.expand(sp.simplify(sp.series(Usym, eps, 0, 3).removeO()))
serV = sp.expand(sp.simplify(sp.series(Vsym, eps, 0, 3).removeO()))
pU = sp.Poly(serU, eps)
pV = sp.Poly(serV, eps)

c_common = sp.exp(-1 / eta) * (2 * eta - 1) / (2 * eta ** 2)
check("U: order 0 == 1 - e^(-1/eta)",
      sp.simplify(pU.coeff_monomial(1) - (1 - sp.exp(-1 / eta))) == 0)
check("U: order 1 == c(eta) = e^(-1/eta)(2eta-1)/(2eta^2)  (same as rho_K)",
      sp.simplify(pU.coeff_monomial(eps) - c_common) == 0)
check("V_{K-m}: order 1 == c(eta) as well  =>  K (U_K - rho_K) -> 0",
      sp.simplify(pV.coeff_monomial(eps) - c_common) == 0)

cprime = sp.simplify(pU.coeff_monomial(eps ** 2) - pV.coeff_monomial(eps ** 2))
cprime_claim = sp.exp(-1 / eta) * m * (2 * eta - m - 1) / (2 * eta ** 2)
check("c'(eta) == e^(-1/eta) m (2eta - m - 1)/(2eta^2),  m = floor(eta)",
      sp.simplify(cprime - cprime_claim) == 0)
# Continuity at integer eta: the m = eta and m = eta - 1 branches agree there.
branch_hi = cprime_claim.subs(m, eta)
branch_lo = cprime_claim.subs(m, eta - 1)
common = sp.exp(-1 / eta) * (eta - 1) / (2 * eta)
check("integer eta: both branches of c' equal e^(-1/eta)(eta-1)/(2eta)",
      sp.simplify(branch_hi - common) == 0
      and sp.simplify(branch_lo - common) == 0)
# Positivity for eta > 1: with 1 <= m <= eta, 2eta - m - 1 >= m - 1 >= 0 and
# the product m(2eta - m - 1) vanishes only at m = 1, eta = 1.
pos_grid = all(
    float(cprime_claim.subs({eta: e, m: math.floor(e)})) > 0
    for e in [1.01, 1.25, 1.5, 2, 2.5, 3, 4, 5, 7.5, 10])
check("c'(eta) > 0 on the eta grid (elementary sign argument in comments)",
      pos_grid)


def cprime_num(e):
    mm = math.floor(e)
    return math.exp(-1 / e) * mm * (2 * e - mm - 1) / (2 * e ** 2)


# ----------------------------------------------------------------------------
# Section 3: numeric convergence, exact Fractions, K <= 400
# ----------------------------------------------------------------------------
print()
print("=" * 78)
print("Section 3  K (U-rho) -> 0,  K^2 (U-rho) -> c'(eta)   (exact, K <= 400)")
print("=" * 78)
K_NUM = [25, 50, 100, 200, 400]
ETAS3 = [Fraction(5, 4), Fraction(3, 2), Fraction(2), Fraction(5, 2),
         Fraction(3), Fraction(5)]
conv = {}
ok_conv = True
for e in ETAS3:
    gaps = {Kv: U_exact(Kv, e) - rho_exact(Kv, e) for Kv in K_NUM}
    k1g = {Kv: float(Kv * g) for Kv, g in gaps.items()}
    k2g = {Kv: float(Kv ** 2 * g) for Kv, g in gaps.items()}
    cp = cprime_num(float(e))
    # one Richardson step on K^2 gap: 2*x(2K) - x(K) kills the 1/K term
    rich = 2 * k2g[400] - k2g[200]
    dev_plain = abs(k2g[400] - cp)
    dev_rich = abs(rich - cp)
    halving = k1g[400] / k1g[200]
    ok_e = (dev_rich < 5e-4 and dev_rich < dev_plain
            and 0.4 < halving < 0.6 and k1g[400] < k1g[25])
    ok_conv &= ok_e
    conv[str(e)] = {
        "K_gap": k1g, "K2_gap": k2g, "c_prime": cp,
        "richardson_K2_gap": rich, "dev_plain_K400": dev_plain,
        "dev_richardson": dev_rich, "K_gap_ratio_400_over_200": halving,
        "ok": ok_e,
    }
    print(f"  eta={str(e):>4}: K*gap(400)={k1g[400]:.2e} "
          f"(ratio vs K=200: {halving:.3f}, ~1/2 => O(1/K)); "
          f"K^2*gap(400)={k2g[400]:.6f} vs c'={cp:.6f} "
          f"(Richardson dev {dev_rich:.1e})")
check("K*(U-rho) halves with K (=> -> 0); Richardson K^2*(U-rho) hits c'",
      ok_conv)

out = {
    "table_points": len(rows),
    "counting_chain": "section 1 all sympy identities",
    "c_prime_closed_form": "exp(-1/eta) * floor(eta) * (2*eta-floor(eta)-1)"
                           " / (2*eta**2)",
    "c_prime_at_integer_eta": "exp(-1/eta)*(eta-1)/(2*eta), both branches",
    "convergence": conv,
    "all_pass": not fails,
}
with open(os.path.join(HERE, "L1_gap.json"), "w") as fh:
    json.dump(out, fh, indent=1)
print()
print("wrote results/L1_gap.json")
print("ALL PASS" if not fails else f"FAILURES: {fails}")
sys.exit(0 if not fails else 1)
