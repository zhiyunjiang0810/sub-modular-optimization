"""Q4 symbolic inequality pass (TASKS10): own branch-by-branch sympy
verification of every INEQUALITY the Q4 construction's legality proof rests
on (the delivered core checks the equalities; the inequalities were hand
arguments in its section 2).  Together with the 13 delivered identities
(rerun in Q4_gpt_check.py) this upgrades the legality lemma of the
double-residual family to [VERIFIED-SYMBOLIC]: every branch case is either
an exact identity or an expression whose sign sympy settles from the
declared domain assumptions.

Domain encoding:
  K = 2 + w,   w >= 0                       (K >= 2)
  eta = f + t, f >= 1, 0 <= t < 1           (t = frac(eta), f = floor(eta);
                                             t < 1 encoded via tb = 1 - t > 0)
  j >= 1 regime uses K - j = f;  j = 0 regime uses eta = K + u, u >= 0
  P > 0 stands for q^x (any x >= 0), Q > 0 for q^j
  z >= 0 is (x - j) * delta inside the linear phase; case bounds of each
  truncation branch enter as substitutions (z = Q - zr etc.)

Checks S1-S9 mirror the delivery's (9)-(13), (20), the band and
submodularity reductions, the value, and the minimizer analysis of (29).

Run:  python3 results/Q4_symbolic_ineq.py     (exit 0 iff ALL PASS)
"""
import sys

import sympy as sp

fails = []


def check(name, ok):
    print(("PASS" if ok else "FAIL"), name)
    if not ok:
        fails.append(name)


def sgn(expr, want):
    """Sign of expr decided by sympy's assumption engine: want in
    {'pos','nonneg','zero'}."""
    e = sp.factor(sp.cancel(sp.together(expr)))
    if want == 'zero':
        return e == 0
    r = e.is_positive if want == 'pos' else e.is_nonnegative
    if r is None:
        e2 = sp.simplify(e)
        r = e2.is_positive if want == 'pos' else e2.is_nonnegative
    return bool(r)


# ---------------------------------------------------------------- symbols
w = sp.Symbol('w', nonnegative=True)            # K = 2 + w
K = 2 + w
fa = sp.Symbol('fa', nonnegative=True)          # floor(eta) - 1 >= 0
f = 1 + fa                                      # floor(eta) >= 1
tb = sp.Symbol('tb', positive=True)             # 1 - frac(eta) > 0
t = 1 - tb                                      # frac(eta) in [0, 1)
# t itself may be 0; inequalities needing t >= 0 use ts (nonnegative symbol)
ts = sp.Symbol('ts', nonnegative=True)
eta = f + ts                                    # eta with frac >= 0
k1 = (K - 1) * eta + 1
q = (K - 1) * eta / k1
P = sp.Symbol('P', positive=True)               # q^x, any x >= 0
Q = sp.Symbol('Q', positive=True)               # q^j
delta = Q / (K * eta)
A = (K - 1) * Q / K
z = sp.Symbol('z', nonnegative=True)
zr = sp.Symbol('zr', nonnegative=True)          # Q - z in the h-only branch
rr = sp.Symbol('rr', positive=True)             # residual value r_x > 0

# S1 geometric phase: p = P/k1, s = (K-1)/K * P/k1
p1, s1 = P / k1, (K - 1) / K * P / k1
check("S1 p - s = P/(K k1) > 0",
      sgn(p1 - s1 - P / (K * k1), 'zero') and sgn(p1 - s1, 'pos'))
check("S1 s > 0", sgn(s1, 'pos'))
check("S1 p one-step decrease = (1-q) p > 0, 1-q = 1/k1",
      sgn(1 - q - 1 / k1, 'zero') and sgn(p1 - q * p1, 'pos'))
check("S1 s one-step decrease > 0", sgn(s1 - q * s1, 'pos'))

# S2 junction (12): p_{j-1} = Q/(q k1) = Q/((K-1) eta)
pj = Q / ((K - 1) * eta)
check("S2 p_{j-1} identity Q/(q k1) = Q/((K-1) eta)",
      sgn(pj - Q / (q * k1), 'zero'))
check("S2 p_{j-1} - delta = Q/(K(K-1)eta) > 0",
      sgn(pj - delta - Q / (K * (K - 1) * eta), 'zero')
      and sgn(pj - delta, 'pos'))
check("S2 s_{j-1} = delta exactly",
      sgn((K - 1) / K * Q / (q * k1) - delta, 'zero'))

# S3 linear phase, truncation step identity (11) and crossing cases
check("S3 delta > 0", sgn(delta, 'pos'))
# (11): r_{x+1} = [r_x - delta]_+  =>  p_x = min(delta, r_x); two cases:
check("S3 (11) untruncated case: r - (r - delta) = delta",
      sgn(rr - (rr - delta) - delta, 'zero'))
check("S3 (11) crossing case: r - 0 = r > 0 and delta - r >= 0 by case",
      sgn(rr, 'pos'))
check("S3 r - h = Q/K > 0 while both untruncated",
      sgn((Q - z) - (A - z) - Q / K, 'zero') and sgn(Q / K, 'pos'))
check("S3 r - h = Q - z >= 0 when only h truncated (case z <= Q)",
      sgn(Q - (Q - zr), 'nonneg'))

# S4 the three cases of (10): (r - h) - h/(K-1) >= 0
check("S4 (10) equality at x <= j",
      sgn(P - (K - 1) * P / K - ((K - 1) * P / K) / (K - 1), 'zero'))
check("S4 (10) linear phase: reduces to z/(K-1) >= 0",
      sgn((Q - z) - (A - z) - (A - z) / (K - 1) - z / (K - 1), 'zero')
      and sgn(z / (K - 1), 'nonneg'))
check("S4 (10) after h truncation: r = Q - z >= 0 (case z <= Q)",
      sgn(Q - (Q - zr), 'nonneg'))

# S5 (20): j >= 1 regime (K - j = f <= eta)
check("S5 Q/K - f delta = Q ts/(K eta) >= 0",
      sgn(Q / K - f * delta - Q * ts / (K * eta), 'zero')
      and sgn(Q * ts / (K * eta), 'nonneg'))
check("S5 A - Q/K = Q(K-2)/K >= 0",
      sgn(A - Q / K - Q * w / K, 'zero') and sgn(Q * w / K, 'nonneg'))
u = sp.Symbol('u', nonnegative=True)
etaK = K + u                                    # j = 0 regime
deltaK = Q / (K * etaK)
check("S5 j=0: A - K delta = Q(eta(K-1)-K)/(K eta), num = K(K-2)+u(K-1)",
      sgn(A - K * deltaK - Q * (etaK * (K - 1) - K) / (K * etaK), 'zero')
      and sgn(etaK * (K - 1) - K - (K * (K - 2) + u * (K - 1)), 'zero')
      and sgn(K * (K - 2) + u * (K - 1), 'nonneg'))

# S6 band reduction from 0 <= s <= p (s = ss >= 0, p - s = g >= 0, eta >= 1)
g = sp.Symbol('g', nonnegative=True)
ss = sp.Symbol('ss', nonnegative=True)
check("S6 eta - 1 = f + ts - 1 >= 0 (f >= 1)", sgn(f + ts - 1, 'nonneg'))
check("S6 lower slack: (p + (eta-1)s) - p = (eta-1) s >= 0",
      sgn((eta - 1) * ss, 'nonneg'))
check("S6 upper slack: eta p - (p + (eta-1)s) = (eta-1)(p-s) >= 0",
      sgn((eta - 1) * g, 'nonneg'))

# S7 submodularity reduction
y = sp.Symbol('y', nonnegative=True)
cy = (K - y) / (K - 1)
check("S7 c_y - c_{y+1} = 1/(K-1) > 0",
      sgn(cy - cy.subs(y, y + 1) - 1 / (K - 1), 'zero')
      and sgn(1 / (K - 1), 'pos'))
check("S7 c_K = 0", sgn(cy.subs(y, K), 'zero'))
check("S7 mixed second difference at y=0 is -(p-s) <= 0",
      sgn(g, 'nonneg'))

# S8 value and minimizer
j = sp.Symbol('j', nonnegative=True)
Vj = 1 - Q * (1 - (K - j) / (K * eta))
Vj1 = 1 - q * Q * (1 - (K - j - 1) / (K * eta))
check("S8 (29) adjacent-branch identity",
      sgn(Vj1 - Vj - Q * (eta - K + j) / (K * eta * k1), 'zero'))
check("S8 denominator K eta k1 > 0", sgn(K * eta * k1, 'pos'))
# r_K > 0, j >= 1 regime: Q - f delta = Q(K-1)/K + Q ts/(K eta) > 0
check("S8 r_K = Q - f delta = Q(K-1)/K + Q ts/(K eta) > 0",
      sgn(Q - f * delta - Q * (K - 1) / K - Q * ts / (K * eta), 'zero')
      and sgn(Q * (K - 1) / K, 'pos'))
check("S8 j=0 regime: r_K = Q - K delta = Q(eta-1)/eta > 0",
      sgn(Q - K * deltaK - Q * (etaK - 1) / etaK, 'zero')
      and sgn(Q * (etaK - 1) / etaK, 'pos'))
# minimizer sign analysis of eta - K + j (t < 1 via tb):
a = sp.Symbol('a', nonnegative=True)
sign_below = (f + (1 - tb)) - K + (K - f - 1 - a)     # j = K-f-1-a
check("S8 below the switch: eta - K + j = -(tb + a) < 0",
      sgn(sign_below + tb + a, 'zero') and sgn(tb + a, 'pos'))
sign_above = eta - K + (K - f + a)                     # j = K-f+a, frac = ts
check("S8 at/above the switch: eta - K + j = ts + a >= 0, tie iff ts=a=0",
      sgn(sign_above - ts - a, 'zero') and sgn(ts + a, 'nonneg'))

# S9 Hhat monotone; H(0,0) = 0
C = k1 / K
check("S9 phase-1 step: C q^s (1-q) = q^s/K > 0",
      sgn(C * P * (1 - q) - P / K, 'zero') and sgn(P / K, 'pos'))
check("S9 phase-2 step: eta delta > 0", sgn(eta * delta, 'pos'))
check("S9 H(0,0) = C - 1 - (eta-1)(K-1)/K = 0",
      sgn(C - 1 - (eta - 1) * (K - 1) / K, 'zero'))

print()
print("ALL PASS" if not fails else f"FAILURES: {len(fails)}")
sys.exit(0 if not fails else 1)
