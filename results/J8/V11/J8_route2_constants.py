"""Symbolic / exact check of the constants used in results/V11/route2/probelottery.md.

Rerun: python3 J8_route2_constants.py
"""
import sympy as sp
from fractions import Fraction as F

x, w, h, e, phi, Meps = sp.symbols('x w h epsilon phi M', nonnegative=True)

print('--- (1) base bound: min over x of max((1+2x)/3, 1-x) ---')
xs = sp.solve(sp.Eq((1 + 2 * x) / 3, 1 - x), x)[0]
print('    crossing x* =', xs, '  value =', sp.nsimplify((1 + 2 * xs) / 3),
      '  == 3/5 :', sp.simplify((1 + 2 * xs) / 3 - sp.Rational(3, 5)) == 0)

print('--- (2) secondary-pair bound: min over phi of max(1/3+2phi/3, 1-phi) ---')
ps = sp.solve(sp.Eq(sp.Rational(1, 3) + 2 * phi / 3, 1 - phi), phi)[0]
print('    crossing phi* =', ps, '  value =',
      sp.nsimplify(sp.Rational(1, 3) + 2 * ps / 3),
      '  == 3/5 :', sp.simplify(sp.Rational(1, 3) + 2 * ps / 3 - sp.Rational(3, 5)) == 0)

print('--- (3) rigidity chain, beta <= 3/5 + eps, OPT = 1 ---')
xhi = sp.Rational(2, 5) + sp.Rational(3, 2) * e      # R1
xlo = sp.Rational(2, 5) - e                          # R2
hhi = (3 * (sp.Rational(3, 5) + e) - xlo) / 2        # R3  h* <= (3 beta - x)/2
hlo = (1 + xlo) / 2                                  # R3  h* >= (1+x)/2
hmin = 1 + xlo - hhi                                 # R4  smaller h_i
whi = (hhi + 2 * xhi) / 3                            # R5  w_i <= (h_i+2x)/3
wlo = 1 - whi                                        # R5  w_i >= 1 - w_j
print('    x  in [', sp.expand(xlo), ',', sp.expand(xhi), ']')
print('    h* in [', sp.expand(hlo), ',', sp.expand(hhi), ']   h_min >=',
      sp.expand(hmin))
print('    w_i in [', sp.expand(wlo), ',', sp.expand(whi), ']')
Delta = sp.expand(hmin / 2 - sp.Rational(3, 2) * wlo + xhi)   # R6  Delta_i bound
print('    Delta_i = tf({b}) - tf({o_i}) <=', Delta, '  (coefficient of eps:',
      sp.expand(Delta).coeff(e), ', constant:', sp.expand(Delta).subs(e, 0), ')')
gap2 = sp.expand(sp.Rational(3, 2) * (sp.Rational(3, 5) + e)
                 - xlo / 2 - hmin)                             # R8
print('    p - tf({b,o_i})            <=', gap2, '  (coefficient of eps:',
      sp.expand(gap2).coeff(e), ', constant:', sp.expand(gap2).subs(e, 0), ')')

print('--- (4) case arithmetic, EPS = 1/10000, target excess 1/400000 ---')
EPS, TGT = F(1, 10000), F(1, 400000)
# universal deficit: every secondary set has f(A) >= (3/5 - 2 EPS) OPT
# E/OPT >= 3/5 + (127/128) eps - EPS/64
need = (F(128, 127)) * (TGT + EPS / 64)
print('    eps needed when no surplus is available:', need, '=', float(need))
# case I (some o_i outside the pool): 5 eps >= EPS * M and M >= 1/2 - (5/3) eps
epsI = sp.symbols('epsI', positive=True)
sol = sp.solve(sp.Eq(5 * epsI, sp.Rational(1, 10000)
                     * (sp.Rational(1, 2) - sp.Rational(5, 3) * epsI)), epsI)[0]
print('    eps forced in case I       :', sol, '=', float(sol),
      '   >= needed :', sp.Rational(sol) > sp.Rational(need.numerator,
                                                       need.denominator))
# case II-a (an optimal element is appended): surplus of the set {o, z_o}
eps0 = F(1, 110000)
surplus = F(5, 6) - F(5, 9) * eps0 - (F(3, 5) + eps0)
deficit7 = 7 * (eps0 + 2 * EPS)
print('    surplus of {o,z_o} >=', float(surplus),
      '  total deficit of the other 7 <=', float(deficit7),
      '  net/1024 =', float((surplus - deficit7) / 1024),
      '  >= target :', (surplus - deficit7) / 1024 >= TGT)
# pool-membership threshold: 5 eps <= EPS * M with M >= 1/2 - (5/3) eps
print('    Lemma P threshold eps <= EPS/11 = ', float(F(1, 110000)),
      ' verified:', 5 * F(1, 110000) <= EPS * (F(1, 2) - F(5, 3) * F(1, 110000)))

print('--- (5) lottery weights ---')
print('    127/128 + 8/1024 =', F(127, 128) + 8 * F(1, 1024))
print('    1024 * (1/400000) =', F(1024, 400000), '=', float(F(1024, 400000)))
print('    tight instance: 127/128*3/5 + (1+7/10+1+7/10+4*3/5)/1024 =',
      F(127, 128) * F(3, 5) + (F(1) + F(7, 10) + F(1) + F(7, 10)
                               + 4 * F(3, 5)) / 1024,
      '= 3/5 + 1/1024 :',
      F(127, 128) * F(3, 5) + (F(1) + F(7, 10) + F(1) + F(7, 10)
                               + 4 * F(3, 5)) / 1024 == F(3, 5) + F(1, 1024))
