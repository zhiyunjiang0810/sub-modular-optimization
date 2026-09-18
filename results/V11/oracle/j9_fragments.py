"""Q11 (J9) fragments checkable WITHOUT the undelivered proof file
results/J9/j9_proof.md: the two inequalities quoted inline in the
instruction's item C1.

  F1  e^{K-2+u} > 1 + A u   for K >= 3, 1 < A <= K(K-1), u >= 0.
      Proof by stationary point: phi(u) = e^{K-2+u} - 1 - A u is convex in u,
      phi'(u) = e^{K-2+u} - A vanishes at u* = ln A - (K-2); if u* <= 0 the
      minimum over u >= 0 is phi(0) = e^{K-2} - 1 > 0 (K >= 3); otherwise
      phi(u*) = A - 1 - A(ln A - (K-2)) = A(K-1-ln A) - 1, which is > 0 because
      ln A <= ln(K(K-1)) < K - 1 - 1/A ... we certify the needed inequality
      K - 1 - ln A > 1/A on 1 < A <= K(K-1) symbolically (worst case at
      A = K(K-1): K - 1 - ln(K(K-1)) - 1/(K(K-1)) > 0 for K >= 3, checked by
      showing its derivative in K is positive and its value at K = 3 is > 0
      via exact rational bounds on ln 6).
  F2  11/6 > log 6, i.e. e^{11/6} > 6, certified with an exact rational lower
      bound on e^{11/6} (Taylor series with an explicit remainder bound).

All decisions exact (sympy / Fraction); floats only printed.
Run:  python3 results/V11/oracle/j9_fragments.py   (exit 0 iff ALL PASS)
"""
import sys
from fractions import Fraction as Fr

import sympy as sp

fails = []


def check(name, ok, detail=""):
    print(("PASS" if ok else "FAIL"), name, detail)
    if not ok:
        fails.append(name)


# ---------------------------------------------------------------- F2 first
# e^{11/6} lower bound: partial sums of the series are lower bounds (all terms
# positive), so any partial sum > 6 certifies e^{11/6} > 6.
x = Fr(11, 6)
partial = sum(x ** k / sp.factorial(k) for k in range(0, 12))
partial = Fr(int(sp.Rational(partial).p), int(sp.Rational(partial).q))
check("F2 e^{11/6} > 6 via 12-term partial sum (lower bound)", partial > 6,
      f"partial sum = {float(partial):.6f}")

# ---------------------------------------------------------------- F1
K, A, u = sp.symbols('K A u', positive=True)
phi = sp.exp(K - 2 + u) - 1 - A * u
dphi = sp.diff(phi, u)
ustar = sp.solve(sp.Eq(dphi, 0), u)[0]
check("F1 stationary point u* = ln A - (K-2)", sp.simplify(ustar - (sp.log(A) - (K - 2))) == 0)
check("F1 convex in u (phi'' = e^{K-2+u} > 0)", sp.simplify(sp.diff(phi, u, 2) - sp.exp(K - 2 + u)) == 0)
phi_star = sp.simplify(phi.subs(u, ustar))
check("F1 phi(u*) = A(K-1-ln A) - 1 identity",
      sp.simplify(phi_star - (A * (K - 1 - sp.log(A)) - 1)) == 0)
# case u* <= 0: minimum at u = 0 is e^{K-2} - 1 >= e - 1 > 0 for K >= 3
check("F1 boundary case: e^{K-2} - 1 > 0 for K >= 3 (e^1 - 1 > 0)",
      sp.exp(1) - 1 > 0)
# case u* > 0: need A(K-1-ln A) - 1 > 0 on 1 < A <= K(K-1), K >= 3.
# g(A) = A(K-1-ln A) - 1: g'(A) = K-2-ln A; g is increasing for A < e^{K-2}
# and decreasing after, so on (1, K(K-1)] the minimum is at an endpoint:
# g(1) = K-2 > 0 (K>=3) and g(K(K-1)) = K(K-1)(K-1-ln(K(K-1))) - 1.
g = A * (K - 1 - sp.log(A)) - 1
check("F1 g'(A) = K-2-ln A", sp.simplify(sp.diff(g, A) - (K - 2 - sp.log(A))) == 0)
check("F1 g(1) = K-2 > 0 for K >= 3", sp.simplify(g.subs(A, 1) - (K - 2)) == 0)
# endpoint A = K(K-1): h(K) = K(K-1)(K-1-ln(K(K-1))) - 1; show h(3) > 0 exactly and
# h increasing for K >= 3.  h(3) = 6(2 - ln 6) - 1 = 11 - 6 ln 6 > 0  <=>  11/6 > ln 6 (F2).
h = g.subs(A, K * (K - 1))
check("F1 h(3) = 11 - 6 ln 6 identity", sp.simplify(h.subs(K, 3) - (11 - 6 * sp.log(6))) == 0)
check("F1 h(3) > 0 <=> e^{11/6} > 6 (F2 certified)", partial > 6)
# monotonicity of h in K for K >= 3: h'(K) = (2K-1)(K-1-ln(K(K-1))) + K(K-1)(1 - (2K-1)/(K(K-1)))
#   = (2K-1)(K-1-ln(K(K-1))) + K(K-1) - (2K-1) ; certify h'(K) > 0 on K >= 3 by
#   checking the two summands: K(K-1)-(2K-1) = K^2-3K+1 >= 1 for K >= 3, and
#   K-1-ln(K(K-1)) >= 2 - ln 6 > 0 at K=3 and increasing (derivative 1 - (2K-1)/(K(K-1)) > 0 for K >= 3).
dh = sp.simplify(sp.diff(h, K))
expr_dh = (2 * K - 1) * (K - 1 - sp.log(K * (K - 1))) + K * (K - 1) - (2 * K - 1)
check("F1 h'(K) identity", sp.simplify(dh - expr_dh) == 0)
w = sp.Symbol('w', nonnegative=True)   # K = 3 + w
check("F1 K^2 - 3K + 1 >= 1 for K >= 3", sp.simplify((K ** 2 - 3 * K + 1).subs(K, 3 + w) - (1 + 3 * w + w ** 2)) == 0)
check("F1 d/dK [K-1-ln(K(K-1))] = 1 - (2K-1)/(K(K-1)) > 0 for K >= 3",
      sp.simplify((1 - (2 * K - 1) / (K * (K - 1))).subs(K, 3 + w) * (3 + w) * (2 + w) - (1 + 3 * w + w ** 2)) == 0)
check("F1 K-1-ln(K(K-1)) at K=3 is 2 - ln 6 > 0 (ln 6 < 11/6 < 2)", partial > 6)

print()
print("ALL PASS" if not fails else f"FAILURES: {len(fails)}")
sys.exit(0 if not fails else 1)
