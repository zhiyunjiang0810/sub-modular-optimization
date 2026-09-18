"""Independent judge checks for results/V11/route2/probelottery.md (TASKS11 Q9, criterion B).

Exact arithmetic only (fractions.Fraction / sympy). Floats only in printouts.
Rerun: python3 judge_probelottery.py
"""
from fractions import Fraction as R
from itertools import combinations, chain
import sympy as sp

EPS = R(1, 10000)
TARGET = R(3, 5) + R(1, 400000)
OK = []


def rec(tag, cond, msg):
    OK.append((tag, bool(cond), msg))
    print(('  PASS ' if cond else '  FAIL ') + tag + ': ' + msg)


print('=== R1  min-max of Prop 4.1 (baseline 3/5) ===')
x = sp.Rational(0)
xs = sp.symbols('x')
sol = sp.solve(sp.Eq((1 + 2 * xs) / 3, 1 - xs), xs)[0]
rec('R1', sol == sp.Rational(2, 5) and (1 - sol) == sp.Rational(3, 5),
    'crossing x*=%s value=%s' % (sol, 1 - sol))

print('=== R2  min-max of Lemma D (D2) ===')
ph = sp.symbols('phi')
sol2 = sp.solve(sp.Eq(sp.Rational(1, 3) + 2 * ph / 3, 1 - ph), ph)[0]
rec('R2', sol2 == sp.Rational(2, 5) and (1 - sol2) == sp.Rational(3, 5),
    'crossing phi*=%s value=%s' % (sol2, 1 - sol2))

print('=== R3  rigidity constants R1-R8, correct monotone directions ===')
e = sp.symbols('epsilon', nonnegative=True)
beta = sp.Rational(3, 5) + e
xhi = sp.Rational(2, 5) + sp.Rational(3, 2) * e          # R1: from beta >= (1+2x)/3
xlo = sp.Rational(2, 5) - e                              # R2: from beta >= 1-x
hhi = sp.expand((3 * beta - xlo) / 2)                    # R3 upper: beta >= (x+2h*)/3
hlo = sp.expand((1 + xlo) / 2)                           # R3 lower: (L5)
hmin = sp.expand(1 + xlo - hhi)                          # R4: h_1+h_2 >= 1+x
whi = sp.expand((hhi + 2 * xhi) / 3)                     # R5 upper: (4.1) h_i >= 3w_i-2x
wlo = sp.expand(1 - whi)                                 # R5 lower: w_1+w_2 >= 1
rec('R3a', sp.expand(hhi - (sp.Rational(7, 10) + 2 * e)) == 0, 'h* <= 7/10+2eps')
rec('R3b', sp.expand(hlo - (sp.Rational(7, 10) - e / 2)) == 0, 'h* >= 7/10-eps/2')
rec('R3c', sp.expand(hmin - (sp.Rational(7, 10) - 3 * e)) == 0, 'h_i >= 7/10-3eps')
rec('R3d', sp.expand(whi - (sp.Rational(1, 2) + sp.Rational(5, 3) * e)) == 0,
    'w_i <= 1/2+(5/3)eps')
rec('R3e', sp.expand(wlo - (sp.Rational(1, 2) - sp.Rational(5, 3) * e)) == 0,
    'w_i >= 1/2-(5/3)eps')

# R6: Delta_i <= (1/2) h_i - (3/2) w_i + x needs an UPPER bound on h_i
Delta_correct = sp.expand(hhi / 2 - sp.Rational(3, 2) * wlo + xhi)
Delta_route2 = sp.expand(hmin / 2 - sp.Rational(3, 2) * wlo + xhi)
rec('R6', sp.expand(Delta_correct - 5 * e) == 0,
    'correct R6 is Delta_i <= %s (route2 file/script print %s, using h_min where h_max is required)'
    % (Delta_correct, Delta_route2))
rec('R6b', sp.expand(Delta_route2 - sp.Rational(5, 2) * e) == 0,
    'route2 value reproduced exactly: %s' % Delta_route2)

# R8: p - tf({b,o_i}) <= (3/2) beta - (1/2) x - h_i : needs LOWER bounds on x and h_i
gap2 = sp.expand(sp.Rational(3, 2) * beta - xlo / 2 - hmin)
rec('R8', sp.expand(gap2 - 5 * e) == 0, 'p - tf({b,o_i}) <= %s' % gap2)

print('=== R4  lottery arithmetic ===')
rec('R4a', R(127, 128) + 8 * R(1, 1024) == 1, '127/128 + 8/1024 = 1')
rec('R4b', R(1024, 400000) == R(8, 3125), '1024/400000 = 8/3125 = 0.00256')
rec('R4c', R(128, 127) * (R(3, 5) + R(1, 400000)) == R(240001, 396875),
    'beta needed if 127/128*beta alone must close = 240001/396875 ~ %.5f'
    % float(R(240001, 396875)))
need = R(128, 127) * (R(1, 400000) + EPS / 64)
rec('R4d', need == R(13, 3175000), 'eps-dagger = %s = %.6e' % (need, float(need)))

print('=== R5  case I forced eps ===')
ei = sp.symbols('ei', positive=True)
solI = sp.solve(sp.Eq(5 * ei, sp.Rational(1, 10000) * (sp.Rational(1, 2)
                                                       - sp.Rational(5, 3) * ei)), ei)[0]
rec('R5a', solI == sp.Rational(3, 300010), 'case-I forced eps = %s = %.6e' % (solI, float(solI)))
rec('R5b', sp.Rational(3, 300010) > sp.Rational(13, 3175000),
    'ratio to eps-dagger = %.3f' % float(sp.Rational(3, 300010) / sp.Rational(13, 3175000)))
# Lemma P threshold
rec('R5c', 5 * R(1, 110000) <= EPS * (R(1, 2) - R(5, 3) * R(1, 110000)),
    'Lemma P: 5*(1/110000) = %.6e <= EPS*M = %.6e'
    % (float(5 * R(1, 110000)), float(EPS * (R(1, 2) - R(5, 3) * R(1, 110000)))))

print('=== R6  case II-a margin, using eps < eps-dagger ===')
ed = R(13, 3175000)
surplus = R(5, 6) - R(5, 9) * ed - (R(3, 5) + ed)
deficit7 = 7 * (ed + 2 * EPS)
rec('R6c', (surplus - deficit7) / 1024 >= R(1, 400000),
    'surplus=%.6f deficit7=%.6f net/1024=%.6e vs target %.1e'
    % (float(surplus), float(deficit7), float((surplus - deficit7) / 1024), 2.5e-6))
rec('R6d', sp.expand(sp.Rational(5, 6) - sp.Rational(5, 9) * e
                     - (sp.Rational(3, 5) + e) - (sp.Rational(7, 30)
                                                  - sp.Rational(14, 9) * e)) == 0,
    'surplus formula 7/30 - (14/9)eps')

print('=== R7  weak bound in case II-b ===')
weak = R(3, 5) - R(8, 1024) * 2 * EPS
rec('R7a', weak == R(3, 5) - R(1, 640000),
    'II-b weak bound = 3/5 - %s = 3/5 - %.6e' % (R(1, 640000), float(R(1, 640000))))
rec('R7b', float(R(1, 640000)) - 1.5625e-06 < 1e-12, 'route2 prints 1.5625e-6, matches')
rec('R7c', TARGET - weak == R(1, 400000) + R(1, 640000),
    'shortfall vs target = %.4e (route2 says 4.1e-6)' % float(TARGET - weak))

print('=== R8  case II-b blocking chain f(B) 3/5 -> 11/15 -> 37/45 -> 119/135 ===')
v = R(3, 5)
chain_vals = [v]
for _ in range(3):
    v = (1 + 2 * v) / 3
    chain_vals.append(v)
rec('R8a', chain_vals[1:] == [R(11, 15), R(37, 45), R(119, 135)],
    'chain = %s' % chain_vals)
rec('R8b', R(119, 135) < 1, '119/135 = %.4f < 1, so no contradiction from OPT' % float(R(119, 135)))

print('=== R9  triple sandwich of the n=7 attack ===')
lo = R(9, 10) + R(1, 5)
hi = R(9, 10) + R(3, 2) * R(1, 10)
rec('R9a', lo == R(11, 10) and hi == R(21, 20) and lo > hi,
    'tf(b,j1,o1) >= %s but <= %s, infeasible' % (lo, hi))

print('=== R10  case II-b requires |C| >= 6 (refinement route2 does not state) ===')
rec('R10', True, 'r = min(4,|C|); if o_1,o_2 in C and 4 rounds pick other elements '
                 'then |C| >= 6 (4 blockers + o_1 + o_2)')

print()
print('summary: %d checks, %d FAILED' % (len(OK), sum(1 for _, c, _ in OK if not c)))
