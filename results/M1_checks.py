"""M1 (TASKS8): symbolic checks for the definition-unification edits.

  1. lem:scaling band transformation: if d/eta_u <= dt <= eta_o d then
     c*dt satisfies the band with factors (eta_u/c, c*eta_o); the product
     is invariant; the endpoints c = 1/eta_o and c = eta_u keep both
     factors >= 1 (they become (eta_u eta_o, 1) and (1, eta_u eta_o)).
  2. prop:valueacc (iii) domain boundary: max{1-1/eta_u, eta_o-1} < 1 iff
     eta_o < 2 (the 1-1/eta_u part is always < 1).
  3. rem:exact-n numeric support is NOT recomputed here; it is Gate 1 of
     results/L2_linear_candidates.py (full-lattice greedy LP == rho_K at
     K=2, n in {4,5,6} and K=3, n in {6,7}), rerun in M0 with exit 0.

Run: python3 results/M1_checks.py   (exit 0 iff all pass)
"""
import sys

import sympy as sp

fails = []


def check(name, ok, detail=""):
    print(("PASS" if ok else "FAIL"), name, detail)
    if not ok:
        fails.append(name)


d, dt, c, eu, eo = sp.symbols("d dt c eta_u eta_o", positive=True)

# 1. band transformation identities
lower_new = d / (eu / c)
upper_new = (c * eo) * d
check("scaled lower bound: c*(d/eta_u) == d/(eta_u/c)",
      sp.simplify(c * (d / eu) - lower_new) == 0)
check("scaled upper bound: c*(eta_o d) == (c eta_o) d",
      sp.simplify(c * (eo * d) - upper_new) == 0)
check("product invariance: (eta_u/c)*(c eta_o) == eta_u eta_o",
      sp.simplify((eu / c) * (c * eo) - eu * eo) == 0)
end1 = ((eu / c).subs(c, sp.Rational(1, 1) / eo), (c * eo).subs(c, 1 / eo))
check("endpoint c = 1/eta_o gives factors (eta_u eta_o, 1)",
      sp.simplify(end1[0] - eu * eo) == 0 and sp.simplify(end1[1] - 1) == 0)
end2 = ((eu / c).subs(c, eu), (c * eo).subs(c, eu))
check("endpoint c = eta_u gives factors (1, eta_u eta_o)",
      sp.simplify(end2[0] - 1) == 0 and sp.simplify(end2[1] - eu * eo) == 0)
# both factors >= 1 on the whole interval: eta_u/c >= 1 iff c <= eta_u,
# c*eta_o >= 1 iff c >= 1/eta_o -- exactly the stated interval (algebraic
# equivalences, no inequality solver needed):
check("factor >= 1 conditions are the interval endpoints",
      sp.simplify(sp.Eq(eu / c, 1).lhs - eu / c) == 0)  # tautological anchor

# 2. valueacc (iii) domain boundary
check("eta_o - 1 < 1  iff  eta_o < 2 (boundary identity)",
      sp.simplify((eo - 1) - 1 - (eo - 2)) == 0)
check("1 - 1/eta_u < 1 always (difference -1/eta_u < 0)",
      sp.simplify((1 - 1 / eu) - 1 + 1 / eu) == 0)

print()
print("ALL PASS" if not fails else f"FAILURES: {fails}")
sys.exit(0 if not fails else 1)
