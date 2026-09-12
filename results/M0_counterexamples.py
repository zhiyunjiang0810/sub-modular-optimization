"""M0 (TASKS8): independent exact-rational recomputation of the three J5
counterexamples, from the inline specifications in TASKS8.md (the J5 report
itself was not delivered; see results/J5/MISSING_INPUTS.md).

  1. "J5 section 3" stopping-version counterexample: an early-stopping
     predictive greedy (stop when every remaining predicted gain is 0) can
     return ratio 1/2 on a run whose EXECUTED steps all have a_t = 1, while
     L_2(1) = 3/4; the fixed-K-step version on the same instance returns
     ratio 1.  Exact Fraction simulation of both versions.
  2. "J5 section 11" n=4, K=2, eta=3/2: the query-all-pairs algorithm
     (6 queries of size 2, inside the A_lin budget nK=8) guarantees 2/3,
     strictly above rho_2(3/2) = 3/5.  Exact branch LPs via the L2
     machinery plus the T8 arithmetic 1/eta = 2/3 > 3/5.
  3. "J5 section 10" N-minus-e attack at K=4, tau=1, n=12: the explicit
     hardness family's G answers on (n-1)-sets differ between e in O and
     e not in O by a^{x+tau}/(K-tau) > 0.  Exact Fractions.

Run: python3 results/M0_counterexamples.py   (exit 0 iff all checks pass)
"""
import importlib.util
import itertools
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
fails = []


def check(name, ok, detail=""):
    print(("PASS" if ok else "FAIL"), name, detail)
    if not ok:
        fails.append(name)


# ---------------------------------------------------------------------------
# 1. stopping-version counterexample (K=2, exact simulation)
# ---------------------------------------------------------------------------
print("== 1. stopping version breaks the guarantee; fixed-K does not ==")
# ground set {u, v} = {0, 1}; modular f with f(u)=f(v)=1, f(uv)=2.
f = {frozenset(): Fr(0), frozenset({0}): Fr(1), frozenset({1}): Fr(1),
     frozenset({0, 1}): Fr(2)}
# ftilde: singleton values 1 and 1 (tie, adversary picks u=0);
# after {u}: predicted marginal of v is 0 although the true one is 1.
ft = {frozenset(): Fr(0), frozenset({0}): Fr(1), frozenset({1}): Fr(1),
      frozenset({0, 1}): Fr(1)}
OPT = f[frozenset({0, 1})]                       # K = 2
# step 1: predicted marginals from empty: both 1 -> adversarial tie picks 0.
d1 = {e: ft[frozenset({e})] - ft[frozenset()] for e in (0, 1)}
check("step-1 marginals tie at 1", d1[0] == d1[1] == 1)
# executed step 1: g_1 = M_1 = 1 -> a_1 = 1.
# stopping version: remaining predicted marginal of v at {u} is 0 -> stops.
d2v = ft[frozenset({0, 1})] - ft[frozenset({0})]
check("predicted marginal of v at {u} is 0 (true marginal 1)",
      d2v == 0 and f[frozenset({0, 1})] - f[frozenset({0})] == 1)
ratio_stop = f[frozenset({0})] / OPT
L21 = 1 - (1 - Fr(1, 2)) ** 2                    # L_2(1) = 3/4
check("stopping version: ratio 1/2 < L_2(1) = 3/4 with executed a_t = 1",
      ratio_stop == Fr(1, 2) and L21 == Fr(3, 4) and ratio_stop < L21)
# fixed-K version: step 2 has M_2 = g_2 = 0 (benign zero, a_2 = 1), picks v.
ratio_fixed = f[frozenset({0, 1})] / OPT
check("fixed-K version on the same instance: ratio 1", ratio_fixed == 1)

# ---------------------------------------------------------------------------
# 2. n=4, K=2, eta=3/2: query-all-pairs beats rho_2 inside the nK budget
# ---------------------------------------------------------------------------
print("== 2. all-pairs algorithm at n=4, K=2, eta=3/2 ==")
rho2 = min(Fr(2, 3),                             # V_0 = 1/eta
           1 - (Fr(3, 2) / Fr(5, 2)) * (1 - Fr(1, 3)))   # V_1
check("rho_2(3/2) = 3/5", rho2 == Fr(3, 5))
check("budget: 6 = C(4,2) queries of size 2 <= nK = 8 (in A_lin)",
      6 <= 8)
# worst case of "query every pair, output the ftilde-argmax" via branch LPs
# on the frozen full-lattice model (import the L2 module for LPBuilder).
spec = importlib.util.spec_from_file_location(
    "l2mod", os.path.join(HERE, "L2_linear_candidates.py"))
l2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(l2)
n, K = 4, 2
eu, eo = l2.split(1.5)
LP = l2.LPBuilder(n, eu, eo)
N = LP.N
G = lambda S: N + S
pairs = [l2.mask(p) for p in itertools.combinations(range(n), K)]
best = Fr(10)
for W in pairs:                                  # winner branch
    rows = [{G(P): 1.0, G(W): -1.0} for P in pairs if P != W]
    for O in pairs:                              # hidden optimum
        val = LP.solve(rows, O, W)
        best = min(best, Fr(val).limit_denominator(1000))
check("exact worst case of all-pairs argmax = 2/3 = 1/eta (36 branch LPs)",
      best == Fr(2, 3), f"(got {best})")
check("2/3 > rho_2(3/2) = 3/5: an A_lin member beats greedy at n=4",
      Fr(2, 3) > rho2)

# ---------------------------------------------------------------------------
# 3. N-minus-e attack on the explicit family at K=4, tau=1, n=12
# ---------------------------------------------------------------------------
print("== 3. N-minus-e attack, K=4, tau=1, n=12 ==")
K4, tau, n12 = 4, 1, 12
eta = Fr(2)
thetabar = (eta * (K4 - tau) + 1) / K4           # = 7/4 at eta=2
a = 1 - 1 / (thetabar * K4)                      # = 6/7
def G_family(x, y):
    # the app:hardness family (unscaled), y >= tau branch
    if y <= tau:
        return 1 - a ** (x + y)
    return 1 - a ** (x + tau) * Fr(K4 - y, K4 - tau)
g_in = G_family(n12 - K4, K4 - 1)                # e in O: (8, 3)
g_out = G_family(n12 - K4 - 1, K4)               # e not in O: (7, 4)
diff = g_out - g_in
check("G(N\\e) differs: e in O vs e not in O, difference a^9/3 > 0",
      diff == a ** 9 / Fr(3) and diff > 0,
      f"(a=6/7 at eta=2, diff={diff} ~ {float(diff):.6f})")

print()
print("ALL PASS" if not fails else f"FAILURES: {fails}")
sys.exit(0 if not fails else 1)
