"""ROUTE-TWO blind derivation, symbolic checks (sympy).

Checks, all symbolic in (K, eta, j, m, d) or (K, eta, u, d):
 S1  H(x+1,0) = H(x,1) on the geometric part, the plateau part, and
     across the two junctions, with NO extra condition;
     at the closing step x = t* it is equivalent to a_{t*} = 0.
 S2  the design equation a_{t*} = 0 solved for d.
 S3  d - 1/(K eta) = (m - eta(K-1)) / (K eta Theta(m)), Theta = eta nu^m - m - eta.
 S4  a_{j+1} - a_j = Q (d - 1/K)/(eta - 1)  and the convexity-at-j condition
     reduces to d >= 1/(K eta).
 S5  K g_x >= r_x on the plateau  <=>  chi(u) >= 0, chi concave, chi(0)=0,
     chi(m) >= 0  <=>  nu^m (K eta - m) >= K eta  <=>  m d <= 1.
 S6  a nonincreasing on the plateau  <=>  m d <= 1.
 S7  (1-q)/q = 1/((K-1) eta)   and   V_0 = 1/eta.
 S8  W_K - V_j = q^j (K-j) (d - 1/(K eta)).
Run:  python3 check_symbolic.py
"""
import sympy as sp

K, eta, j, m, u, d, x = sp.symbols('K eta j m u d x', positive=True)

k1 = (K - 1) * eta + 1
q = (K - 1) * eta / k1
nu = eta / (eta - 1)
Q = q**j
C = k1 / K
D = Q * d
A = eta * D - Q / K


def r_geo(xx):
    return q**xx


def g_geo(xx):
    return q**xx / K


def r_pl(uu):                      # uu = x - j, 0 <= uu <= m
    return Q - uu * D


def g_pl(uu):
    return eta * D - (eta * D - Q / K) * nu**uu


def a_geo(xx):
    return sp.simplify(r_geo(xx) - g_geo(xx))


def a_pl(uu):
    return sp.simplify(r_pl(uu) - g_pl(uu))


def H0_geo(xx):
    return C - r_geo(xx) - (eta - 1) * a_geo(xx)


def H0_pl(uu):
    return C - r_pl(uu) - (eta - 1) * a_pl(uu)


def H1_geo(xx):
    return C - eta * a_geo(xx)


def H1_pl(uu):
    return C - eta * a_pl(uu)


out = []

# ---------- S1 : H(x+1,0) = H(x,1) ----------
s1a = sp.simplify(H0_geo(x + 1) - H1_geo(x))                  # both sides geometric
s1b = sp.simplify(H0_pl(u + 1) - H1_pl(u))                    # both sides plateau
s1c = sp.simplify(H0_pl(1) - H1_geo(j))                       # junction x=j -> j+1
# closing step x = t*: r,g,a are 0 beyond t*, so H(t*+1,0) = C
s1d = sp.simplify((C) - H1_pl(m))                             # = eta * a_{t*}
out.append(('S1 geometric  H(x+1,0)-H(x,1)', sp.simplify(s1a)))
out.append(('S1 plateau    H(x+1,0)-H(x,1)', sp.simplify(s1b)))
out.append(('S1 junction   H(j+1,0)-H(j,1)', sp.simplify(s1c)))
out.append(('S1 closing    H(t*+1,0)-H(t*,1) = eta*a_{t*}',
            sp.simplify(s1d - eta * a_pl(m))))

# ---------- S2 : design equation ----------
design = sp.simplify(a_pl(m))                                  # must vanish
dstar = sp.solve(sp.Eq(design, 0), d)[0]
dstar = sp.simplify(dstar)
out.append(('S2 d solved from a_{t*}=0', dstar))
dclosed = (nu**m - K) / (K * (eta * nu**m - m - eta))
out.append(('S2 d - closed form', sp.simplify(dstar - dclosed)))

# ---------- S3 : d - 1/(K eta) ----------
Theta = eta * nu**m - m - eta
out.append(('S3 d-1/(K eta) - (m-eta(K-1))/(K eta Theta)',
            sp.simplify(dclosed - 1 / (K * eta) - (m - eta * (K - 1)) / (K * eta * Theta))))

# ---------- S4 : first plateau increment ----------
inc1 = sp.simplify(a_pl(1) - a_geo(j))
out.append(('S4 a_{j+1}-a_j - Q(d-1/K)/(eta-1)',
            sp.simplify(inc1 - Q * (d - sp.Rational(1, 1) / K) / (eta - 1))))
incm1 = sp.simplify(a_geo(j) - a_geo(j - 1))
out.append(('S4 a_j - a_{j-1} + Q/(K eta)', sp.simplify(incm1 + Q / (K * eta))))
# convexity at j:  inc1 >= incm1  <=>  (d-1/K)/(eta-1) >= -1/(K eta)  <=> d >= 1/(K eta)
conv_j = sp.simplify(((d - 1 / K) / (eta - 1) + 1 / (K * eta)) * (eta - 1))
out.append(('S4 convexity-at-j residual (should be d - 1/(K eta))',
            sp.simplify(conv_j - (d - 1 / (K * eta)))))

# ---------- S5 : K g >= r on the plateau ----------
chi = sp.simplify((K * g_pl(u) - r_pl(u)) / Q)
chi_target = u * d - (K * eta * d - 1) * (nu**u - 1)
out.append(('S5 (K g - r)/Q - chi', sp.simplify(chi - chi_target)))
# chi(m) >= 0 under the design equation  <=>  nu^m (K eta - m) >= K eta
chi_m = sp.simplify(chi_target.subs({u: m, d: dclosed}))
crit = sp.simplify(sp.factor(sp.together(chi_m)))
out.append(('S5 chi(m) factored', crit))
# and  m d <= 1  <=>  same
md_res = sp.simplify(1 - m * dclosed)
out.append(('S5 (1 - m d) factored', sp.factor(sp.together(md_res))))

# ---------- S6 : last plateau increment of a ----------
lastinc = sp.simplify(a_pl(m) - a_pl(m - 1))
lastinc_sub = sp.simplify(lastinc.subs(d, dclosed))
out.append(('S6 a_{t*}-a_{t*-1} under design eq (sign = sign of (m d - 1))',
            sp.simplify(sp.factor(sp.together(lastinc_sub)))))

# ---------- S7 ----------
out.append(('S7 (1-q)/q - 1/((K-1)eta)', sp.simplify((1 - q) / q - 1 / ((K - 1) * eta))))
V = lambda jj: 1 - q**jj * (1 - (K - jj) / (K * eta))
out.append(('S7 V_0 - 1/eta', sp.simplify(V(0) - 1 / eta)))

# ---------- S8 ----------
WK = 1 - (Q - (K - j) * D)          # r_K = Q - (K-j) D , valid for j < K <= t*
out.append(('S8 W_K - V_j - q^j (K-j)(d - 1/(K eta))',
            sp.simplify(WK - V(j) - q**j * (K - j) * (d - 1 / (K * eta)))))

for name, val in out:
    print(f'{name:58s} -> {val}')
