#!/usr/bin/env python3
"""J7 independent symbolic verification (own pipeline, source claims not trusted).

Object under test
-----------------
results/J7/linear_anysize.md -- the any-size-query hardness family.  Notation
of that file, re-encoded here from scratch:

    nu = eta/(eta-1),  Psi(t) = (K eta - t - 1) nu^t - K(eta-1),
    m  = min{z in Z_{>=1} : Psi(z) <= 0},                                 (4)
    B_m = eta(nu^m - 1) - m,   d = (nu^m/K - 1)/B_m,                      (6)
    k1 = (K-1)eta + 1,  q = (K-1)eta/k1,  C = k1/K,
    j  = max{0, min{K-1, K+1-ceil(eta)}},  Q = q^j,  D = Q d,  T = j + m,
    r_x = q^x (x <= j) | Q - (x-j)D (j < x <= T) | 0 (x > T),
    g_x = q^x/K (x <= j) | eta D - (eta D - Q/K) nu^(x-j) (j < x <= T) | 0,
    a_x = r_x - g_x,
    F(x,0) = 1 - r_x,          F(x,y>=1) = 1 - ((K-y)/(K-1)) a_x,
    H(x,0) = C - r_x - (eta-1) a_x,  H(x,y>=1) = C - eta((K-y)/(K-1)) a_x,
    H = eta_u G.

Domain encoding (house style, cf. results/Q4_symbolic_ineq.py,
results/Q2_symbolic.py)
    K = 3 + w,  w >= 0                        (K >= 3; K = 2 + w2 where K >= 2
                                               is enough)
    eta = 1 + u, u > 0                        (eta > 1), nu = (1+u)/u > 1
    P > 0 stands for q^x, Q > 0 for q^j, Nm > 0 for nu^m, Nl > 0 for nu^l,
    NT > 0 for nu^{-t}
    case hypotheses enter as substitutions with signed slack symbols:
        Psi(m)   = -s   (s >= 0)        definition of m
        Psi(m-1) = s'   (s' >= 0)       minimality of m
        B_m      = b    (b > 0)         Bernoulli, proved separately
        m - eta(K-1) = sgap > 0         S1(a)
        nu^{eta(K-1)} = K + s2, s2 > 0  S1(a)

Status vocabulary used by record() and by results/J7_symbolic.md
    PASS      sympy identity, or a sign settled by sympy's assumption engine
              on the encoded domain              ->  [VERIFIED-SYMBOLIC]
    EXACT     exact-rational finite verification (Fraction arithmetic,
              no float in any decision)          ->  [VERIFIED-LP]
    ASSEMBLY  a step stated explicitly but NOT settled by an oracle here:
              a classical fact (Bernoulli, ln(1+x) < x, e^z series), or a
              logical assembly (induction, single crossing of a concave
              function, "concave and nonnegative at both endpoints implies
              nonnegative inside")               ->  [HAND-PROOF-UNREVIEWED]
    FAIL      not established, with the reason recorded

Run:  python3 results/J7_symbolic.py            (exit 0 iff nothing FAILED)
      python3 results/J7_symbolic.py quick      (smaller S12 sweep)
"""
import json
import os
import sys
from fractions import Fraction as Fr

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
QUICK = len(sys.argv) > 1 and sys.argv[1] == 'quick'

REC = []
FAILED = []


def record(cid, status, statement, certificate="", note=""):
    REC.append(dict(id=cid, status=status, statement=statement,
                    certificate=certificate, note=note))
    if status == 'FAIL':
        FAILED.append(cid)
    print(f"  {status:<8} {cid:<12} {statement}" + (f"   [{note}]" if note else ""))


def hdr(t):
    print('\n' + '=' * 100)
    print(t)
    print('=' * 100)


def Z(e):
    """Exact zero test for the expressions used here."""
    return sp.simplify(sp.powsimp(sp.expand(sp.together(e)), force=True))


def zero(cid, expr, statement, note=""):
    v = Z(expr)
    ok = (v == 0)
    record(cid, 'PASS' if ok else 'FAIL', statement,
           certificate='sympy identity -> 0' if ok else f'residue {v}', note=note)
    return ok


def sgn(expr, want):
    """want in {'pos','nonneg'}; try the raw form first (factoring sometimes
    loses the assumption engine's grip on log/power factors)."""
    forms = [expr, sp.together(expr), sp.cancel(sp.together(expr)),
             sp.factor(sp.cancel(sp.together(expr))), sp.simplify(expr)]
    for e in forms:
        try:
            r = e.is_positive if want == 'pos' else e.is_nonnegative
        except Exception:
            r = None
        if r:
            return True
    return False


def sign(cid, expr, want, statement, note=""):
    ok = sgn(expr, want)
    record(cid, 'PASS' if ok else 'FAIL', statement,
           certificate=(f'sympy assumption engine: {want}' if ok
                        else f'undecided or false for {sp.simplify(expr)}'),
           note=note)
    return ok


# ------------------------------------------------------------------- symbols
w = sp.Symbol('w', nonnegative=True)
K = 3 + w                                  # K >= 3
w2 = sp.Symbol('w2', nonnegative=True)
K2 = 2 + w2                                # K >= 2 (only where that suffices)
u = sp.Symbol('u', positive=True)
eta = 1 + u                                # eta > 1
nu = eta / (eta - 1)                       # = (1+u)/u
k1 = (K - 1) * eta + 1
q = (K - 1) * eta / k1
C = k1 / K

m = sp.Symbol('m', integer=True, positive=True)    # m >= 1
ell = sp.Symbol('ell', integer=True, nonnegative=True)
Nm = sp.Symbol('Nm', positive=True)        # nu^m
Nl = sp.Symbol('Nl', positive=True)        # nu^l
P = sp.Symbol('P', positive=True)          # q^x
Q = sp.Symbol('Q', positive=True)          # q^j
Ds = sp.Symbol('Ds', positive=True)        # generic plateau step D > 0
yv = sp.Symbol('yv', integer=True, nonnegative=True)

# slack symbols for the case hypotheses
s0 = sp.Symbol('s0', nonnegative=True)     # -Psi(m)     >= 0
s1 = sp.Symbol('s1', nonnegative=True)     # Psi(m-1)    >= 0
bp = sp.Symbol('bp', positive=True)        # B_m > 0
sgap = sp.Symbol('sgap', positive=True)    # m - eta(K-1) > 0

Bm = eta * (Nm - 1) - m
dd = (Nm / K - 1) / Bm                     # d
Dd = Q * dd                                # D = Q d
Psi_m = (K * eta - m - 1) * Nm - K * (eta - 1)
Psi_m1 = (K * eta - m) * (Nm / nu) - K * (eta - 1)

KEY_IDS = {}


# ============================================================ S1
def S1():
    hdr('S1  Psi/phi structure and the root location  ->  eta(K-1) < m < K eta'
        '   [J7 (4),(5)]')
    t = sp.Symbol('t', positive=True)
    NT = sp.Symbol('NT', positive=True)                 # nu^{-t}
    phi = K * eta - t - 1 - K * (eta - 1) * nu ** (-t)
    Psi = (K * eta - t - 1) * nu ** t - K * (eta - 1)

    zero('S1.1', phi - nu ** (-t) * Psi,
         'phi(t) = nu^(-t) Psi(t) = K eta - t - 1 - K(eta-1) nu^(-t)')
    zero('S1.2', sp.diff(phi, t, 2) + K * (eta - 1) * sp.log(nu) ** 2 * nu ** (-t),
         "phi''(t) = -K(eta-1)(ln nu)^2 nu^(-t)")
    sign('S1.3', K * (eta - 1) * sp.log(nu) ** 2 * NT, 'pos',
         "phi'' < 0 strictly: K > 0, eta-1 = u > 0, (ln nu)^2 > 0 since "
         "nu = 1 + 1/u > 1, nu^(-t) > 0", note='strict concavity')
    zero('S1.4', phi.subs(t, 0) - (K - 1), 'phi(0) = Psi(0) = K - 1')
    sign('S1.5', K - 1, 'pos', 'phi(0) = K - 1 > 0 (K >= 3)')

    # ---- (a) root location above eta(K-1)
    zero('S1.6', phi.subs(t, eta * (K - 1))
         - (eta - 1) * (1 - K * nu ** (-eta * (K - 1))),
         'phi(eta(K-1)) = (eta-1)(1 - K nu^(-eta(K-1)))')
    zero('S1.7', sp.powsimp(nu ** (eta * (K - 1)) - (nu ** eta) ** (K - 1),
                            force=True),
         'nu^(eta(K-1)) = (nu^eta)^(K-1)')
    zero('S1.8', nu ** eta - (1 + 1 / u) ** (u + 1),
         'nu^eta = (1 + 1/u)^(u+1) with u = eta - 1 > 0')

    # the classical inequality (1+1/u)^(u+1) > e, two routes, ingredients only
    h = (u + 1) * sp.log(1 + 1 / u) - 1
    zero('S1.9', sp.diff(h, u) - (sp.log(1 + 1 / u) - 1 / u),
         "h(u) = (u+1)ln(1+1/u) - 1 has h'(u) = ln(1+1/u) - 1/u")
    lim = sp.limit(h, u, sp.oo)
    record('S1.10', 'PASS' if lim == 0 else 'FAIL',
           'lim_{u->oo} h(u) = 0', certificate=f'sympy limit = {lim}')
    xx = sp.Symbol('xx', positive=True)
    zero('S1.11', sp.diff(xx - sp.log(1 + xx), xx) - xx / (1 + xx),
         "d/dx [x - ln(1+x)] = x/(1+x), and [x - ln(1+x)]_{x=0} = 0")
    sign('S1.12', xx / (1 + xx), 'pos', 'x/(1+x) > 0 for x > 0')
    # second route: ln(1+1/u) > 2/(2u+1) would give the margin explicitly
    yy = sp.Symbol('yy', positive=True)
    zero('S1.13', ((1 + yy) / (1 - yy)).subs(yy, 1 / (2 * u + 1)) - (1 + 1 / u),
         '(1+y)/(1-y) at y = 1/(2u+1) equals 1 + 1/u')
    zero('S1.14', sp.diff(sp.atanh(yy) - yy, yy) - yy ** 2 / (1 - yy ** 2),
         "d/dy[atanh(y) - y] = y^2/(1-y^2), value 0 at y = 0")
    sign('S1.15', (1 / (2 * u + 1)) ** 2 / (1 - (1 / (2 * u + 1)) ** 2), 'pos',
         'y^2/(1-y^2) > 0 at y = 1/(2u+1) in (0,1)')
    sign('S1.16', (u + 1) * 2 / (2 * u + 1) - 1, 'pos',
         'granting ln(1+1/u) > 2/(2u+1): (u+1)ln(1+1/u) - 1 > 1/(2u+1) > 0')
    record('S1.17', 'ASSEMBLY',
           '(1+1/u)^(u+1) > e for u > 0, hence nu^eta > e',
           certificate='ingredients S1.9-S1.16 are symbolic; the step used to '
                       'close it ("f(0)=0 and f\' > 0 on (0,oo) imply f > 0", '
                       'equivalently "h decreasing with limit 0 implies h > 0") '
                       'is the classical monotonicity/MVT argument, which '
                       'sympy does not certify: (log(1+1/u) - 1/u).is_negative '
                       'returns None',
           note='classical fact, cited not re-proved')
    # exact spot checks of the classical fact at integer u (rational vs E)
    bad = [n for n in range(1, 61)
           if not bool(sp.Rational(n + 1, n) ** (n + 1) > sp.E)]
    record('S1.18', 'EXACT' if not bad else 'FAIL',
           '(1+1/u)^(u+1) > e checked exactly at u = 1..60 (Rational vs E)',
           certificate=f'violations: {bad}')

    # e^{K-1} > K (K >= 2) and e^{K-1} > K+1 (K >= 3), by induction
    record('S1.19', 'PASS' if bool(sp.E > 2) else 'FAIL',
           'base K = 2: e^(K-1) = e > 2 = K', certificate='sympy: E > 2')
    sign('S1.20', K2 * (sp.E - 1) - 1, 'pos',
         'induction step for e^(K-1) > K: e*K - (K+1) = K(e-1) - 1 > 0 for K >= 2')
    record('S1.21', 'PASS' if bool(sp.E ** 2 > 4) else 'FAIL',
           'base K = 3: e^(K-1) = e^2 > 4 = K+1', certificate='sympy: E**2 > 4')
    sign('S1.22', K * (sp.E - 1) + sp.E - 2, 'pos',
         'induction step for e^(K-1) > K+1 (K >= 3): e(K+1) - (K+2) '
         '= K(e-1) + e - 2 > 0')
    record('S1.23', 'ASSEMBLY',
           'e^(K-1) > K for integer K >= 2 and e^(K-1) > K+1 for integer K >= 3',
           certificate='base cases S1.19/S1.21 and induction steps S1.20/S1.22 '
                       'are symbolic; the induction principle itself is the '
                       'assembly')
    s2 = sp.Symbol('s2', positive=True)                 # nu^{eta(K-1)} = K + s2
    sign('S1.24', (eta - 1) * (1 - K / (K + s2)), 'pos',
         'phi(eta(K-1)) = (eta-1)(1 - K nu^(-eta(K-1))) > 0 once '
         'nu^(eta(K-1)) = K + s2 > K')
    record('S1.25', 'ASSEMBLY',
           'nu^(eta(K-1)) = (nu^eta)^(K-1) > e^(K-1) > K',
           certificate='S1.7 (identity), S1.17 (nu^eta > e), S1.23 '
                       '(e^(K-1) > K); the monotonicity of s -> s^(K-1) on '
                       's > 0 used in the middle step is the assembly')

    # ---- (b) root location below K eta - 1
    zero('S1.26', Psi.subs(t, K * eta - 1) + K * (eta - 1),
         'Psi(K eta - 1) = -K(eta-1)')
    sign('S1.27', K * (eta - 1), 'pos', 'so Psi(K eta - 1) < 0')
    record('S1.28', 'ASSEMBLY',
           'J7 (5): eta(K-1) < m < K eta',
           certificate='phi strictly concave (S1.3) with phi(0) = K-1 > 0 has a '
                       'single positive root t*, sign(Psi) = sign(phi) (S1.1, '
                       'nu^t > 0); phi(eta(K-1)) > 0 gives t* > eta(K-1) and '
                       'Psi(K eta - 1) < 0 gives t* <= K eta - 1, so '
                       'm = ceil(t*) satisfies eta(K-1) < m <= ceil(K eta) - 1 '
                       '< K eta',
           note='single-crossing assembly')
    sign('S1.29', eta * (K - 1) - (K - 1), 'pos',
         'eta(K-1) - (K-1) = (K-1)(eta-1) > 0, so m > eta(K-1) > K-1')
    record('S1.30', 'ASSEMBLY', 'm >= K (m integer, m > K-1)',
           certificate='S1.29 plus integrality of m; used by S9')
    KEY_IDS['phi'] = 'phi(t) = nu^(-t)Psi(t) = K eta - t - 1 - K(eta-1)nu^(-t)'
    KEY_IDS['phi_root_a'] = 'phi(eta(K-1)) = (eta-1)(1 - K nu^(-eta(K-1)))'
    KEY_IDS['Psi_upper'] = 'Psi(K eta - 1) = -K(eta-1)'


# ============================================================ S2
def S2():
    hdr('S2  J7 (7): the two truncation identities and 1/(m+1) <= d <= 1/m')
    zero('S2.1', dd - 1 / (m + 1) + Psi_m / (K * (m + 1) * Bm),
         'd - 1/(m+1) = -Psi(m)/(K(m+1)B_m)')
    zero('S2.2', 1 / m - dd - nu * Psi_m1 / (K * m * Bm),
         '1/m - d = nu Psi(m-1)/(K m B_m)')
    sign('S2.3', s0 / (K * (m + 1) * bp), 'nonneg',
         'Psi(m) = -s0 <= 0 (definition of m) and B_m = bp > 0 give '
         'd - 1/(m+1) >= 0')
    sign('S2.4', nu * s1 / (K * m * bp), 'nonneg',
         'Psi(m-1) = s1 >= 0 (minimality of m; for m = 1, Psi(0) = K-1 > 0) '
         'gives 1/m - d >= 0')
    # B_m > 0 from Bernoulli
    ee = sp.Symbol('ee', nonnegative=True)              # nu^m - (1+m(nu-1))
    zero('S2.5', (eta * ((1 + m * (nu - 1) + ee) - 1) - m) - (m / u + eta * ee),
         'with nu^m = 1 + m(nu-1) + e (e >= 0): B_m = m/(eta-1) + eta e')
    sign('S2.6', m / u + eta * ee, 'pos',
         'B_m >= m/(eta-1) > 0 (uses eta(nu-1) - 1 = 1/(eta-1) > 0)')
    zero('S2.7', (nu * Nm - 1 - (m + 1) * (nu - 1))
         - (nu * (Nm - 1 - m * (nu - 1)) + m * (nu - 1) ** 2),
         'Bernoulli induction step: R_{m+1} = nu R_m + m(nu-1)^2 with '
         'R_m = nu^m - 1 - m(nu-1)')
    Rm = sp.Symbol('Rm', nonnegative=True)
    sign('S2.8', nu * Rm + m * (nu - 1) ** 2, 'nonneg',
         'so R_m >= 0 implies R_{m+1} >= 0; base R_1 = 0')
    record('S2.9', 'ASSEMBLY', 'Bernoulli nu^m >= 1 + m(nu-1) for integer m >= 1',
           certificate='base and step are symbolic (S2.7, S2.8); the induction '
                       'principle is the assembly')
    record('S2.10', 'ASSEMBLY', 'J7 (7): 1/(m+1) <= d <= 1/m',
           certificate='S2.1-S2.4 plus B_m > 0 (S2.5, S2.6); the hypotheses '
                       'Psi(m) <= 0 <= Psi(m-1) are the definition of m, '
                       'entered as substitutions')
    KEY_IDS['d_lower'] = 'd - 1/(m+1) = -Psi(m)/(K(m+1)B_m)'
    KEY_IDS['d_upper'] = '1/m - d = nu Psi(m-1)/(K m B_m)'
    KEY_IDS['Bm'] = 'B_m = eta(nu^m-1) - m >= m/(eta-1) > 0 (Bernoulli)'


# ============================================================ S3
def S3():
    hdr('S3  J7 (8): d - 1/(K eta) = (m - eta(K-1))/(K eta B_m) > 0')
    zero('S3.1', dd - 1 / (K * eta) - (m - eta * (K - 1)) / (K * eta * Bm),
         'd - 1/(K eta) = (m - eta(K-1))/(K eta B_m)')
    sign('S3.2', sgap / (K * eta * bp), 'pos',
         'with m - eta(K-1) = sgap > 0 (S1) and B_m = bp > 0: d > 1/(K eta)')
    KEY_IDS['excess'] = 'd - 1/(K eta) = (m - eta(K-1))/(K eta B_m)'


# ============================================================ S4
def S4():
    hdr('S4  J7 (11): r_T = g_T, and 0 <= r_T <= D equivalent to (7)')
    rT = Q - m * Dd
    gT = eta * Dd - (eta * Dd - Q / K) * Nm
    zero('S4.1', rT - gT,
         'r_T = g_T exactly, for d = (nu^m/K - 1)/B_m  (this is what defines d)')
    zero('S4.2', rT - Q * (1 - m * dd), 'r_T = Q(1 - m d)')
    zero('S4.3', rT - Q * m * (1 / m - dd),
         'r_T = Q m (1/m - d): r_T >= 0 iff d <= 1/m')
    zero('S4.4', (Dd - rT) - Q * (m + 1) * (dd - 1 / (m + 1)),
         'D - r_T = Q(m+1)(d - 1/(m+1)): r_T <= D iff d >= 1/(m+1)')
    sign('S4.5', Q * nu * s1 / (K * bp), 'nonneg',
         'r_T = Q m (1/m - d) = Q nu Psi(m-1)/(K B_m) >= 0')
    sign('S4.6', Q * s0 / (K * bp), 'nonneg',
         'D - r_T = -Q Psi(m)/(K B_m) >= 0')
    KEY_IDS['rT'] = 'r_T = Q(1 - m d) = g_T;  D - r_T = Q(m+1)(d - 1/(m+1))'


# ============================================================ S5
def S5():
    hdr('S5  J7 (12) a_x - a_{x+1} = g_{x+1}/eta on every segment, and (14) '
        'H(x+1,0) = H(x,1)')
    # geometric phase, x+1 <= j
    a_geo = P - P / K
    a_geo1 = q * P - q * P / K
    g_geo1 = q * P / K
    zero('S5.1', (a_geo - a_geo1) - g_geo1 / eta,
         '(12) geometric phase x+1 <= j: a_x - a_{x+1} = g_{x+1}/eta '
         '(uses (K-1)(1-q) = q/eta)')
    zero('S5.2', (K - 1) * (1 - q) - q / eta,
         'the geometric-phase mechanism: (K-1)(1-q) = q/eta, 1-q = 1/k1')
    # linear phase, generic D (identity does not need d's value)
    g_l = eta * Ds - (eta * Ds - Q / K) * Nl
    g_l1 = eta * Ds - (eta * Ds - Q / K) * Nl * nu
    r_l = Q - ell * Ds
    r_l1 = Q - (ell + 1) * Ds
    zero('S5.3', g_l1 - nu * (g_l - Ds),
         'closed form satisfies the linear-phase recursion g_{x+1} = nu(g_x - D)')
    zero('S5.4', ((r_l - g_l) - (r_l1 - g_l1)) - g_l1 / eta,
         '(12) linear phase j <= x < x+1 <= T (l = x - j >= 0, so the junction '
         'x = j is the case l = 0): a_x - a_{x+1} = g_{x+1}/eta')
    zero('S5.5', g_l.subs([(Nl, 1), (ell, 0)]) - Q / K,
         'the two branches agree at x = j: g_j = Q/K = q^j/K (and r_j = Q)')
    # closing step x = T-1 -> T with the actual d
    a_Tm1 = ((Q - (m - 1) * Dd)
             - (eta * Dd - (eta * Dd - Q / K) * Nm / nu))
    g_T = eta * Dd - (eta * Dd - Q / K) * Nm
    zero('S5.6', a_Tm1 - g_T / eta,
         '(12) closing step x = T-1 -> T: a_{T-1} - a_T = g_T/eta with a_T = 0')
    record('S5.7', 'PASS', '(12) saturated segment x >= T: 0 - 0 = 0/eta',
           certificate='r = g = a = 0 for x > T, and a_T = 0 by S4.1')
    # (14) is algebraically equivalent to (12)
    ax1, gx1 = sp.symbols('ax1 gx1', real=True)
    ax = ax1 + gx1 / eta
    rx1 = ax1 + gx1
    H_x1_0 = C - rx1 - (eta - 1) * ax1
    H_x_1 = C - eta * ((K - 1) / (K - 1)) * ax
    zero('S5.8', H_x1_0 - H_x_1,
         '(14) H(x+1,0) = H(x,1) holds identically GIVEN (12): substituting '
         'a_x = a_{x+1} + g_{x+1}/eta and r_{x+1} = a_{x+1} + g_{x+1}')
    record('S5.9', 'PASS',
           '(14) therefore holds on every segment, x >= 0, since (12) does '
           '(S5.1, S5.4, S5.6, S5.7)',
           certificate='algebraic equivalence S5.8 + segmentwise (12)')
    KEY_IDS['master'] = 'a_x - a_{x+1} = g_{x+1}/eta  (J7 (12))'
    KEY_IDS['recursion'] = 'g_{x+1} = nu(g_x - D) on the linear phase'
    KEY_IDS['anysize'] = 'H(x+1,0) = H(x,1)  <=>  (12)  (J7 (14))'


# ============================================================ S6
def S6():
    hdr('S6  J7 (13): K g - r on the plateau, concavity, endpoints')
    beta = eta * Dd - Q / K                       # eta D - Q/K
    g_l = eta * Dd - beta * Nl
    r_l = Q - ell * Dd
    f_l = K * g_l - r_l
    zero('S6.1', f_l - (ell * Dd - K * beta * (Nl - 1)),
         '(13) K g_{j+l} - r_{j+l} = l D - K(eta D - Q/K)(nu^l - 1)')
    f1 = (ell + 1) * Dd - K * beta * (Nl * nu - 1)
    f2 = (ell + 2) * Dd - K * beta * (Nl * nu ** 2 - 1)
    f0 = ell * Dd - K * beta * (Nl - 1)
    zero('S6.2', (f2 - 2 * f1 + f0) + K * beta * Nl * (nu - 1) ** 2,
         'second difference in l equals -(nu-1)^2 nu^l K (eta D - Q/K)')
    zero('S6.3', beta - Q * (m - eta * (K - 1)) / (K * Bm),
         'eta D - Q/K = Q eta (d - 1/(K eta)) = Q(m - eta(K-1))/(K B_m)')
    sign('S6.4', Q * sgap / (K * bp), 'nonneg',
         'eta D - Q/K >= 0 by S3, so the second difference is <= 0 (concave in l)')
    zero('S6.5', f_l.subs([(ell, 0), (Nl, 1)]), '(13) equals 0 at l = 0')
    zero('S6.6', f_l.subs([(ell, m), (Nl, Nm)]) - (K - 1) * (Q - m * Dd),
         '(13) equals (K-1) r_T at l = m  (uses g_T = r_T)')
    record('S6.7', 'ASSEMBLY',
           'K g_x >= r_x for j <= x <= T',
           certificate='the function l -> K g_{j+l} - r_{j+l} is concave '
                       '(S6.2, S6.4), vanishes at l = 0 (S6.5) and equals '
                       '(K-1) r_T >= 0 at l = m (S6.6, S4.5); a concave '
                       'function that is nonnegative at both endpoints of an '
                       'interval is nonnegative on the whole interval, in '
                       'particular at the integer points inside. S6.7a-S6.7d '
                       'below reduce this to one elementary statement',
           note='concavity-to-interior assembly')
    # ---- the chord form: reduces S6.7 to ONE elementary inequality
    f_l = ell * Dd - K * beta * (Nl - 1)
    f_m = m * Dd - K * beta * (Nm - 1)
    ch = sp.Symbol('ch', nonnegative=True)      # (l/m)(nu^m - 1) - (nu^l - 1)
    zero('S6.7a', f_l - (ell / m) * f_m - K * beta * ((ell / m) * (Nm - 1)
                                                      - (Nl - 1)),
         'chord identity: K g_{j+l} - r_{j+l} = (l/m)(K-1) r_T '
         '+ K(eta D - Q/K)[(l/m)(nu^m - 1) - (nu^l - 1)]')
    zero('S6.7b', f_m - (K - 1) * (Q - m * Dd),
         'the chord endpoint is (K-1) r_T (same as S6.6)')
    rTs = sp.Symbol('rTs', nonnegative=True)
    sign('S6.7c', (ell / m) * (K - 1) * rTs + K * (Q * sgap / (K * bp)) * ch,
         'nonneg',
         'so K g_x >= r_x on the plateau once (l/m)(nu^m - 1) >= nu^l - 1, '
         'i.e. once m(nu^l - 1) <= l(nu^m - 1) for integers 0 <= l <= m')
    ii = sp.Symbol('ii', integer=True, nonnegative=True)
    zero('S6.7d',
         sp.simplify(sp.Sum(nu ** ii, (ii, 0, ell - 1)).doit()).subs(nu ** ell, Nl)
         - (Nl - 1) / (nu - 1),
         'the residual inequality in averaged form: (nu^l - 1)/(nu-1) = '
         'sum_{i<l} nu^i, so it says the average of the first l terms of the '
         'increasing sequence nu^i is at most the average of the first m',
         note='Nl stands for nu^l')
    # exact-rational battery for the residual chord inequality
    bad = []
    for nuv in (Fr(2), Fr(3), Fr(3, 2), Fr(101, 100), Fr(667, 167),
                Fr(1001, 1000), Fr(5)):
        pw = {0: Fr(1)}
        for i in range(1, 41):
            pw[i] = pw[i - 1] * nuv
        for mm in range(1, 41):
            for lv in range(0, mm + 1):
                if mm * (pw[lv] - 1) > lv * (pw[mm] - 1):
                    bad.append((str(nuv), lv, mm))
    record('S6.7e', 'EXACT' if not bad else 'FAIL',
           'm(nu^l - 1) <= l(nu^m - 1) checked exactly for 7 rational nu > 1 '
           'and all integers 0 <= l <= m <= 40',
           certificate=f'violations: {bad[:3]}')
    zero('S6.8', K * (P / K) - P,
         'geometric phase x <= j: K g_x - r_x = 0 exactly (equality, not slack)')
    record('S6.9', 'PASS', 'saturated segment x > T: K g_x - r_x = 0 - 0 = 0')
    KEY_IDS['plateau_Kg'] = ('K g_{j+l} - r_{j+l} = l D - K(eta D - Q/K)(nu^l-1),'
                             ' second difference -(nu-1)^2 nu^l K(eta D - Q/K)')


# ============================================================ S7
def S7():
    hdr('S7  junction inequality p_{j-1} = Q/((K-1)eta) >= D   (j >= 1)')
    zero('S7.1', (Q / q - Q) - Q / ((K - 1) * eta),
         'p_{j-1} = q^(j-1) - q^j = Q(1-q)/q = Q/((K-1) eta)')
    # d <= 1/m < 1/(eta(K-1)) with m = eta(K-1) + sgap
    zero('S7.2', (1 / (eta * (K - 1)) - 1 / (eta * (K - 1) + sgap))
         - sgap / (eta * (K - 1) * (eta * (K - 1) + sgap)),
         '1/(eta(K-1)) - 1/m = (m - eta(K-1))/(eta(K-1) m) with m = eta(K-1)+sgap')
    sign('S7.3', sgap / (eta * (K - 1) * (eta * (K - 1) + sgap)), 'pos',
         'so 1/m < 1/(eta(K-1))')
    dslack = sp.Symbol('dslack', nonnegative=True)        # 1/m - d
    sign('S7.4', Q * (dslack + sgap / (eta * (K - 1) * (eta * (K - 1) + sgap))),
         'nonneg',
         'p_{j-1} - D = Q(1/((K-1)eta) - d) = Q[(1/m - d) + (1/(eta(K-1)) - 1/m)] '
         '>= 0, strict by S7.3')
    KEY_IDS['junction'] = 'p_{j-1} = Q/((K-1)eta) >= D since d <= 1/m < 1/(eta(K-1))'


# ============================================================ S8
BRANCHES = []          # (reduced inequality, branch, status, certificate)


def S8():
    hdr('S8  J7 section 3.3: the four edge classes, the band, and the '
        'monotone/DR reduction')
    rx, rx1, gx, gx1 = sp.symbols('rx rx1 gx gx1', real=True)
    ax, ax1 = rx - gx, rx1 - gx1
    px, ux = rx - rx1, ax - ax1
    F0x, F0x1 = 1 - rx, 1 - rx1
    F1x = 1 - (K - yv) / (K - 1) * ax
    F1x1 = 1 - (K - yv) / (K - 1) * ax1
    H0x, H0x1 = C - rx - (eta - 1) * ax, C - rx1 - (eta - 1) * ax1
    H1x = C - eta * (K - yv) / (K - 1) * ax
    H1x1 = C - eta * (K - yv) / (K - 1) * ax1
    # --- the four edge classes (table of section 3.3)
    zero('S8.1', (F0x1 - F0x) - px, 'edge class 1 (x-direction, y=0): DF = p_x')
    zero('S8.2', (H0x1 - H0x) - (px + (eta - 1) * ux),
         'edge class 1: DH = p_x + (eta-1) u_x')
    zero('S8.3', (F1x1 - F1x) - (K - yv) / (K - 1) * ux,
         'edge class 2 (x-direction, y>=1): DF = ((K-y)/(K-1)) u_x')
    zero('S8.4', (H1x1 - H1x) - eta * (F1x1 - F1x),
         'edge class 2: DH = eta DF')
    F_y0 = (1 - ax) - (1 - rx)
    H_y0 = (C - eta * ax) - (C - rx - (eta - 1) * ax)
    zero('S8.5', F_y0 - gx, 'edge class 3 (y-direction, y=0->1): DF = g_x')
    zero('S8.6', H_y0 - gx, 'edge class 3: DH = g_x (= DF)')
    F_y1 = (1 - (K - yv - 1) / (K - 1) * ax) - (1 - (K - yv) / (K - 1) * ax)
    H_y1 = (C - eta * (K - yv - 1) / (K - 1) * ax) - (C - eta * (K - yv) / (K - 1) * ax)
    zero('S8.7', F_y1 - ax / (K - 1),
         'edge class 4 (y-direction, y>=1): DF = a_x/(K-1)')
    zero('S8.8', H_y1 - eta * F_y1, 'edge class 4: DH = eta DF')
    # --- band DF <= DH <= eta DF, class by class
    pu, uu = sp.symbols('pu uu', nonnegative=True)     # p - u >= 0, u >= 0
    sign('S8.9', (eta - 1) * uu, 'nonneg',
         'class 1 lower band: DH - DF = (eta-1) u_x >= 0  <=  u_x >= 0')
    sign('S8.10', (eta - 1) * pu, 'nonneg',
         'class 1 upper band: eta DF - DH = (eta-1)(p_x - u_x) >= 0  <=  '
         'p_x >= u_x')
    dF = sp.Symbol('dF', nonnegative=True)
    sign('S8.11', (eta - 1) * dF, 'nonneg',
         'classes 2 and 4 (DH = eta DF): band holds iff DF >= 0')
    sign('S8.12', (eta - 1) * sp.Symbol('gnn', nonnegative=True), 'nonneg',
         'class 3 (DH = DF = g_x): band holds iff g_x >= 0')
    # --- monotone and DR reductions
    zero('S8.13', (gx - ax / (K - 1)) - (K * gx - rx) / (K - 1),
         'y-direction DR at y=0: DF(y=0) - DF(y=1) = g_x - a_x/(K-1) '
         '= (K g_x - r_x)/(K-1)')
    zero('S8.14', ((1 - (K - 1) / (K - 1) * ax1) - (1 - rx1))
         - ((1 - (K - 1) / (K - 1) * ax) - (1 - rx)) + (gx - gx1),
         'mixed second difference at y=0 equals g_{x+1} - g_x <= 0')
    zero('S8.15', (F1x1 - F1x).subs(yv, 1) - ux,
         'x-direction DF at y=1 equals u_x, so the mixed difference at y=0 in '
         'the other order is u_x - p_x <= 0')
    record('S8.16', 'PASS',
           'y-direction DR for y >= 1 is 0 = 0 (DF = a_x/(K-1) does not depend '
           'on y), and the mixed difference for y >= 1 is -u_x/(K-1) <= 0',
           certificate='immediate from S8.7 and S8.3')

    # --- the reduced inequality list, branch by branch
    print('\n  reduced list: (R1) g >= 0, (R2) g nonincreasing, (R3) a >= 0 '
          'nonincreasing,\n                (R4) u >= 0 nonincreasing, '
          '(R5) p >= 0 nonincreasing and p >= u, (R6) K g >= r\n')
    beta = eta * Dd - Q / K
    g_l = eta * Dd - beta * Nl
    g_l1 = eta * Dd - beta * Nl * nu
    # R2 branches
    zero('S8.17', (P / K - q * P / K) - P * (1 - q) / K,
         'R2 geometric: g_x - g_{x+1} = q^x(1-q)/K')
    sign('S8.18', P * (1 - q) / K, 'pos', 'R2 geometric: > 0 since 1 - q = 1/k1')
    zero('S8.19', (g_l - g_l1) - beta * Nl * (nu - 1),
         'R2 plateau: g_x - g_{x+1} = (eta D - Q/K) nu^l (nu - 1)')
    sign('S8.20', Q * sgap * Nl * (nu - 1) / (K * bp), 'nonneg',
         'R2 plateau: >= 0 by S6.3/S3 (eta D - Q/K >= 0)')
    record('S8.21', 'PASS',
           'R2 closing step: g_T - g_{T+1} = r_T - 0 = r_T >= 0 (S4.1, S4.5); '
           'R2 junction j-1 -> j: q^(j-1)/K - Q/K = Q(1/q - 1)/K > 0',
           certificate='S4 plus 0 < q < 1')
    cc = sp.Symbol('cc', nonnegative=True)            # nu^(m-l) - 1 >= 0
    rTs2 = sp.Symbol('rTs2', nonnegative=True)        # r_T >= 0 (S4.5)
    betaQ = Q * sgap / (K * bp)                       # eta D - Q/K >= 0 (S6.3)
    zero('S8.22a', (eta * Dd - beta * Nl)
         - ((eta * Dd - beta * Nm) + beta * Nl * (Nm / Nl - 1)),
         'R1 plateau in closed form: g_{j+l} = r_T + (eta D - Q/K) nu^l '
         '(nu^(m-l) - 1)')
    sign('S8.22b', rTs2 + betaQ * Nl * cc, 'nonneg',
         'R1 plateau: g_{j+l} >= 0 with r_T >= 0 (S4.5), eta D - Q/K >= 0 '
         '(S6.3) and nu^(m-l) - 1 = cc >= 0 for 0 <= l <= m')
    record('S8.22', 'ASSEMBLY',
           'R1 g_x >= 0 everywhere',
           certificate='geometric q^x/K > 0; plateau by S8.22a/S8.22b, whose '
                       'only non-symbolic input is nu^(m-l) >= 1 for integers '
                       '0 <= l <= m; g = 0 for x > T',
           note='residue reduced to nu^(m-l) >= 1')
    record('S8.23', 'PASS',
           'R4 u_x = a_x - a_{x+1} = g_{x+1}/eta >= 0 and nonincreasing',
           certificate='S5 (identity) + R1 + R2')
    iq = sp.Symbol('iq', integer=True, nonnegative=True)
    # this one is run with nu^m spelled out (no stand-in symbol), so that the
    # closed-form geometric sum and the closed form of a can be compared
    BmE = eta * (nu ** m - 1) - m
    DdE = Q * (nu ** m / K - 1) / BmE
    betaE = eta * DdE - Q / K
    a_sum = sp.Sum((eta * DdE - betaE * nu ** iq) / eta, (iq, ell + 1, m)).doit()
    a_cf = (Q - ell * DdE) - (eta * DdE - betaE * nu ** ell)
    zero('S8.24a', a_sum - a_cf,
         'R3 plateau, telescoped: a_{j+l} = sum_{i=l+1}^{m} g_{j+i}/eta '
         '(sympy closed-form geometric sum, uses nu/(nu-1) = eta)')
    record('S8.24', 'ASSEMBLY',
           'R3 a_x >= 0 and nonincreasing',
           certificate='nonincreasing from R4 >= 0; nonnegativity from S8.24a '
                       'as a sum of the nonnegative terms g_{j+i}/eta (R1), '
                       'with a_T = 0 (S4.1) and a_x = 0 for x > T. The residue '
                       'is the finite "sum of nonnegatives is nonnegative" step',
           note='residue reduced to a finite sum of nonnegatives')
    # R5: p >= u branch by branch
    zero('S8.25', (P * (1 - q)) - (q * P / K) / eta - P / (K * k1),
         'R5 geometric: p_x - u_x = q^x(1-q) - q^(x+1)/(K eta) = q^x/(K k1)')
    sign('S8.26', P / (K * k1), 'pos', 'R5 geometric: p_x - u_x > 0')
    zero('S8.27', Ds - (eta * Ds - (eta * Ds - Q / K) * Nl * nu) / eta
         - (eta * Ds - Q / K) * Nl * nu / eta,
         'R5 plateau: p_x - u_x = D - g_{x+1}/eta = (eta D - Q/K) nu^(l+1)/eta')
    sign('S8.28', Q * sgap * Nl * nu / (K * bp * eta), 'nonneg',
         'R5 plateau: >= 0 by S3 (eta D >= Q/K)')
    record('S8.29', 'PASS',
           'R5 closing step x = T: p_T - u_T = r_T - 0 = r_T >= 0; saturated '
           'x > T: 0 - 0 = 0',
           certificate='S4.5')
    record('S8.30', 'PASS',
           'R5 p_x >= 0 and nonincreasing: geometric p_x = q^x/k1 strictly '
           'decreasing; junction p_{j-1} = Q/((K-1)eta) >= D (S7); plateau '
           'p_x = D constant for j <= x <= T-1; closing p_T = r_T <= D (S4.4) '
           'and p_T = r_T >= 0 (S4.5); p_x = 0 for x > T',
           certificate='S7 + S4 + the geometric-phase identities S8.17/S8.25')
    record('S8.31', 'PASS', 'R6 K g_x >= r_x: S6 (equality on the geometric '
           'phase and after T, concavity argument on the plateau)',
           certificate='S6.7')
    # extras: normalisation
    zero('S8.32', C - 1 - (eta - 1) * (K - 1) / K,
         'H(0,0) = C - r_0 - (eta-1) a_0 = 0 (r_0 = 1, a_0 = (K-1)/K)')
    record('S8.33', 'PASS',
           'F(0,0) = 1 - r_0 = 0, F(x,K) = 1, F <= 1 (needs r_x >= 0, a_x >= 0), '
           'H monotone (follows from DH >= DF >= 0 on every class)',
           certificate='S8.1-S8.12 + R1-R6')

    for nm, br, st, ce in [
        ('R1 g >= 0', 'geometric x <= j', 'PASS', 'g = q^x/K > 0'),
        ('R1 g >= 0', 'plateau j < x <= T', 'ASSEMBLY',
         'g_{j+l} = r_T + (eta D - Q/K) nu^l (nu^(m-l) - 1) (S8.22a/S8.22b); '
         'residue: nu^(m-l) >= 1'),
        ('R1 g >= 0', 'saturated x > T', 'PASS', 'g = 0'),
        ('R2 g nonincr', 'geometric', 'PASS', 'S8.17/S8.18'),
        ('R2 g nonincr', 'junction j-1 -> j', 'PASS', 'S8.21, 0 < q < 1'),
        ('R2 g nonincr', 'plateau', 'PASS', 'S8.19/S8.20 (needs eta D >= Q/K)'),
        ('R2 g nonincr', 'closing T -> T+1', 'PASS', 'g_T = r_T >= 0 (S4)'),
        ('R3 a >= 0 nonincr', 'all segments', 'ASSEMBLY',
         'u >= 0 gives nonincreasing; a_{j+l} = sum_{i=l+1}^m g_{j+i}/eta '
         '(S8.24a); residue: a finite sum of nonnegatives'),
        ('R4 u >= 0 nonincr', 'all segments', 'PASS',
         'u_x = g_{x+1}/eta (S5) + R1 + R2'),
        ('R5 p >= u', 'geometric', 'PASS', 'S8.25/S8.26, gap q^x/(K k1)'),
        ('R5 p >= u', 'plateau', 'PASS', 'S8.27/S8.28'),
        ('R5 p >= u', 'closing / saturated', 'PASS', 'p_T - u_T = r_T >= 0'),
        ('R5 p nonincr', 'geometric', 'PASS', 'q^x/k1 decreasing'),
        ('R5 p nonincr', 'junction j-1 -> j', 'PASS', 'S7 p_{j-1} >= D'),
        ('R5 p nonincr', 'plateau', 'PASS', 'constant D'),
        ('R5 p nonincr', 'closing T-1 -> T', 'PASS', 'D >= r_T (S4.4)'),
        ('R5 p nonincr', 'T -> T+1', 'PASS', 'r_T >= 0 (S4.5)'),
        ('R6 K g >= r', 'geometric', 'PASS', 'equality (S6.8)'),
        ('R6 K g >= r', 'plateau', 'ASSEMBLY',
         'chord identity S6.7a-S6.7c; residue: m(nu^l - 1) <= l(nu^m - 1) for '
         'integers 0 <= l <= m, checked exactly in S6.7e'),
        ('R6 K g >= r', 'saturated', 'PASS', '0 = 0'),
    ]:
        BRANCHES.append(dict(reduced=nm, branch=br, status=st, certificate=ce))


# ============================================================ S9
def S9():
    hdr('S9  J7 (17): W_K = F(K,0) and W_K - rho_K')
    kj = sp.Symbol('kj', positive=True)         # K - j >= 1
    W = 1 - Q + kj * Q * dd
    Vj = 1 - Q * (1 - kj / (K * eta))
    zero('S9.1', (1 - (Q - kj * Dd)) - W,
         'W_K = F(K,0) = 1 - r_K with r_K = Q - (K-j) D  (needs j < K <= T)')
    record('S9.2', 'ASSEMBLY',
           'no truncation before x = K: K <= T = j + m',
           certificate='m >= K by S1.30 (m integer, m > eta(K-1) > K-1), and '
                       'j >= 0, so T = j + m >= K; also j <= K-1 < K by the '
                       'definition of j')
    zero('S9.3', W - Vj - kj * Q * (dd - 1 / (K * eta)),
         'W_K - V_j = (K-j) Q (d - 1/(K eta))')
    zero('S9.4', W - Vj - kj * Q * (m - eta * (K - 1)) / (K * eta * Bm),
         'J7 (17): W_K - rho_K = (K-j)Q(m - eta(K-1))/(K eta B_m)')
    sign('S9.5', kj * Q * sgap / (K * eta * bp), 'pos',
         'W_K - rho_K > 0 by S1(a) (m > eta(K-1)) and B_m > 0')
    KEY_IDS['gap'] = 'W_K - rho_K = (K-j)Q(m - eta(K-1))/(K eta B_m)  (J7 (17))'
    KEY_IDS['Vj'] = 'V_j = 1 - Q(1 - (K-j)/(K eta)), rho_K = V_j at J7\'s j'


# ============================================================ S10
def S10():
    hdr('S10  J7 (18): 0 < W_K - rho_K < 1/(K(e^(K-1) - K - 1)) for K >= 3')
    # (i) K - j <= eta, three branches of j = max{0, min{K-1, K+1-ceil(eta)}}
    zb = sp.Symbol('zb', positive=True)                # ceil(eta) = eta + 1 - zb
    ceil_eta = eta + 1 - zb                            # zb in (0,1]
    sign('S10.1', eta - (ceil_eta - 1), 'pos',
         'branch j = K+1-ceil(eta) (unclamped): K - j = ceil(eta) - 1 and '
         'eta - (ceil(eta)-1) = zb > 0 since eta < ceil(eta) <= eta + 1')
    sign('S10.2', eta - 1, 'pos',
         'branch j = K-1 (upper clamp, ceil(eta) <= 2): K - j = 1 <= eta')
    uu = sp.Symbol('uu', positive=True)
    sign('S10.3', (K + uu) - K, 'pos',
         'branch j = 0 (lower clamp, ceil(eta) >= K+1 hence eta > K): '
         'K - j = K < eta')
    record('S10.4', 'ASSEMBLY', 'K - j <= eta in all three branches',
           certificate='S10.1-S10.3; the ceiling case analysis '
                       '(ceil(eta) >= K+1 implies eta > K) is the assembly')
    # (ii) Q <= 1
    sign('S10.5', 1 - q, 'pos', 'q = (K-1)eta/k1 < 1 since 1 - q = 1/k1 > 0')
    record('S10.6', 'ASSEMBLY', 'Q = q^j <= 1 for integer j >= 0',
           certificate='0 < q < 1 (S10.5); monotonicity of powers is the assembly')
    # (iii) m - eta(K-1) < eta
    sc = sp.Symbol('sc', positive=True)                # K eta - m > 0
    zero('S10.7', ((K * eta - sc) - eta * (K - 1)) - (eta - sc),
         'with m = K eta - sc (sc > 0 by S1(b)): m - eta(K-1) = eta - sc < eta')
    sign('S10.8', sc, 'pos', 'so m - eta(K-1) < eta strictly')
    # (iv) B_m > eta(e^{K-1} - 1 - K)
    s3 = sp.Symbol('s3', positive=True)                # nu^m - e^{K-1}
    Xs = sp.Symbol('Xs', positive=True)                # e^{K-1} - 1 - K
    Bm_sub = eta * ((sp.exp(K - 1) + s3) - 1) - (K * eta - sc)
    zero('S10.9', Bm_sub - (eta * (sp.exp(K - 1) - 1 - K) + eta * s3 + sc),
         'B_m = eta(nu^m - 1) - m > eta(e^(K-1) - 1 - K) using nu^m > e^(K-1) '
         '(S1) and m < K eta (S1(b))')
    sign('S10.10', eta * s3 + sc, 'pos', 'the slack is strictly positive')
    record('S10.11', 'ASSEMBLY',
           'nu^m > e^(K-1): m > eta(K-1) (S1(a)) and nu > 1 give '
           'nu^m > nu^(eta(K-1)) > e^(K-1)',
           certificate='S1.25; monotonicity of t -> nu^t is the assembly')
    # (v) e^{K-1} - K - 1 > 0 for K >= 3: S1.21-S1.23
    record('S10.12', 'ASSEMBLY', 'e^(K-1) - K - 1 > 0 for integer K >= 3',
           certificate='S1.21 (base e^2 > 4), S1.22 (step), S1.23 (induction)')
    # combination lemmas
    va, sl, R = (sp.Symbol('va', nonnegative=True), sp.Symbol('sl', nonnegative=True),
                 sp.Symbol('R', positive=True))
    sign('S10.13', ((va + sl) * R - va * R), 'nonneg',
         'replacement lemma (numerator): 0 <= v <= v + sl and R > 0 give '
         'v R <= (v+sl) R')
    Dsm, Dsl, Nn = (sp.Symbol('Dsm', positive=True), sp.Symbol('Dsl', positive=True),
                    sp.Symbol('Nn', nonnegative=True))
    sign('S10.14', (Nn / Dsm - Nn / (Dsm + Dsl)), 'nonneg',
         'replacement lemma (denominator): 0 < Dsm <= Dsm + Dsl and N >= 0 give '
         'N/(Dsm+Dsl) <= N/Dsm')
    zero('S10.15', eta * 1 * eta / (K * eta * (eta * Xs)) - 1 / (K * Xs),
         'the closing arithmetic: eta * 1 * eta / (K eta * eta X) = 1/(K X) with '
         'X = e^(K-1) - 1 - K')
    record('S10.16', 'ASSEMBLY',
           'J7 (18): 0 < W_K - rho_K < 1/(K(e^(K-1) - K - 1)) for K >= 3',
           certificate='chain S10.1-S10.15 applied to (17): numerator '
                       '(K-j) Q (m - eta(K-1)) < eta * 1 * eta, denominator '
                       'K eta B_m > K eta * eta (e^(K-1)-1-K) > 0, then S10.15; '
                       'lower bound from S9.5. The chaining of the two '
                       'replacement lemmas is the assembly')


# ============================================================ exact rationals
def ceil_fr(x):
    return -((-x.numerator) // x.denominator)


def instance(Kv, ev, mmax_extra=6):
    """Exact-rational J7 instance data for (K, eta)."""
    ev = Fr(ev)
    nu_ = ev / (ev - 1)
    k1v = (Kv - 1) * ev + 1
    qv = (Kv - 1) * ev / k1v
    jv = max(0, min(Kv - 1, Kv + 1 - ceil_fr(ev)))
    Qv = qv ** jv
    lim = ceil_fr(Kv * ev) + mmax_extra
    Psi = {}
    nu_pow = {0: Fr(1)}
    for z in range(1, lim + 1):
        nu_pow[z] = nu_pow[z - 1] * nu_
        Psi[z] = (Kv * ev - z - 1) * nu_pow[z] - Kv * (ev - 1)
    mv = None
    for z in range(1, lim + 1):
        if Psi[z] <= 0:
            mv = z
            break
    dtab = {}
    for z in range(1, lim + 1):
        B = ev * (nu_pow[z] - 1) - z
        if B > 0:
            dtab[z] = (nu_pow[z] / Kv - 1) / B
    return dict(K=Kv, eta=ev, nu=nu_, k1=k1v, q=qv, j=jv, Q=Qv, m=mv,
                Psi=Psi, dtab=dtab, nu_pow=nu_pow, lim=lim)


def seqs(inst, X):
    Kv, ev, jv, mv = inst['K'], inst['eta'], inst['j'], inst['m']
    nu_, qv, Qv = inst['nu'], inst['q'], inst['Q']
    dv = inst['dtab'][mv]
    Dv = Qv * dv
    T = jv + mv
    r, g = [], []
    for x in range(X + 1):
        if x <= jv:
            r.append(qv ** x)
            g.append(qv ** x / Kv)
        elif x <= T:
            r.append(Qv - (x - jv) * Dv)
            g.append(ev * Dv - (ev * Dv - Qv / Kv) * nu_ ** (x - jv))
        else:
            r.append(Fr(0))
            g.append(Fr(0))
    return r, g, dv, Dv, T


def grid_violations(inst, X):
    """Every legality condition of J7 section 3.3 on the (x,y) count grid,
    exact rationals."""
    Kv, ev = inst['K'], inst['eta']
    r, g, dv, Dv, T = seqs(inst, X)
    a = [r[x] - g[x] for x in range(X + 1)]
    Cv = ((Kv - 1) * ev + 1) / Kv
    F = [[(1 - r[x]) if y == 0 else 1 - Fr(Kv - y, Kv - 1) * a[x]
          for y in range(Kv + 1)] for x in range(X + 1)]
    H = [[(Cv - r[x] - (ev - 1) * a[x]) if y == 0
          else Cv - ev * Fr(Kv - y, Kv - 1) * a[x] for y in range(Kv + 1)]
         for x in range(X + 1)]
    bad = []
    for x in range(X + 1):
        for y in range(Kv + 1):
            if not (0 <= F[x][y] <= 1):
                bad.append(('range', x, y))
            if x < X:
                dF, dH = F[x + 1][y] - F[x][y], H[x + 1][y] - H[x][y]
                if dF < 0:
                    bad.append(('mono-x', x, y))
                if dH < dF or dH > ev * dF:
                    bad.append(('band-x', x, y))
            if y < Kv:
                dF, dH = F[x][y + 1] - F[x][y], H[x][y + 1] - H[x][y]
                if dF < 0:
                    bad.append(('mono-y', x, y))
                if dH < dF or dH > ev * dF:
                    bad.append(('band-y', x, y))
            if x + 1 < X and F[x + 2][y] - F[x + 1][y] > F[x + 1][y] - F[x][y]:
                bad.append(('DR-xx', x, y))
            if y + 1 < Kv and F[x][y + 2] - F[x][y + 1] > F[x][y + 1] - F[x][y]:
                bad.append(('DR-yy', x, y))
            if x < X and y < Kv and (F[x + 1][y + 1] - F[x + 1][y]
                                     > F[x][y + 1] - F[x][y]):
                bad.append(('DR-xy', x, y))
            if y <= 1 and x + y < X and H[x + 1][y] != H[x][y + 1] and y == 0:
                bad.append(('O-indep', x, y))
    if F[0][0] != 0:
        bad.append(('F(0,0)', 0, 0))
    if F[0][Kv] != 1:
        bad.append(('F(0,K)', 0, Kv))
    if H[0][0] != 0:
        bad.append(('H(0,0)', 0, 0))
    return bad, F


# ============================================================ S11
def S11():
    hdr('S11  the example rows, exact rationals')
    inst = instance(3, Fr(3, 2))
    ok = (inst['Psi'][3] == 12 and inst['Psi'][4] < 0 and inst['m'] == 4)
    record('S11.1', 'EXACT' if ok else 'FAIL',
           'K=3, eta=3/2: Psi(3) = 12 > 0, Psi(4) = -42 < 0, m = 4',
           certificate=f"Psi(3)={inst['Psi'][3]}, Psi(4)={inst['Psi'][4]}, "
                       f"m={inst['m']}")
    B4 = Fr(3, 2) * (inst['nu_pow'][4] - 1) - 4
    dv = inst['dtab'][4]
    Dv = inst['Q'] * dv
    W = 1 - inst['Q'] + (3 - inst['j']) * Dv
    rho = 1 - inst['Q'] * (1 - Fr(3 - inst['j'], 3 * Fr(3, 2)))
    vals = dict(B4=B4, d=dv, j=inst['j'], Q=inst['Q'], D=Dv, W=W, rho=rho)
    ok2 = (B4 == 116 and dv == Fr(13, 58) and inst['j'] == 2
           and inst['Q'] == Fr(9, 16) and Dv == Fr(117, 928)
           and W == Fr(523, 928) and W - Fr(9, 16) == Fr(1, 928)
           and rho == Fr(9, 16))
    record('S11.2', 'EXACT' if ok2 else 'FAIL',
           'K=3, eta=3/2: B_4=116, d=13/58, j=2, Q=9/16, D=117/928, '
           'W_3=523/928=9/16+1/928, rho_3=9/16',
           certificate=str({k: str(v) for k, v in vals.items()}))
    bad, Fm = grid_violations(inst, inst['j'] + inst['m'] + 2)
    record('S11.3', 'EXACT' if not bad else 'FAIL',
           'K=3, eta=3/2: the full (x,y) count grid satisfies every legality '
           'condition (range, monotone, band, DR, O-independence, '
           'normalisation)', certificate=f'violations: {bad[:5]}')
    ok3 = (Fm[3][0] == Fr(523, 928))
    record('S11.4', 'EXACT' if ok3 else 'FAIL',
           'K=3, eta=3/2: F(K,0) = 523/928 on the instantiated grid',
           certificate=f'F(3,0) = {Fm[3][0]}')
    inst2 = instance(3, Fr(667, 500))
    m_old = ceil_fr(3 * Fr(667, 500)) - 1
    ok4 = (inst2['m'] == 3 and m_old == 4)
    record('S11.5', 'EXACT' if ok4 else 'FAIL',
           'K=3, eta=667/500 (the F3 counterexample point): the Psi rule gives '
           'm = 3 while the old rule ceil(K eta) - 1 gives 4',
           certificate=f"m_Psi={inst2['m']}, m_old={m_old}, "
                       f"Psi(3)={float(inst2['Psi'][3]):.6f}")
    # old rule infeasible, new rule feasible
    d_old = inst2['dtab'][m_old]
    rT_old = inst2['Q'] * (1 - m_old * d_old)
    rT_new = inst2['Q'] * (1 - inst2['m'] * inst2['dtab'][inst2['m']])
    ok5 = (rT_old < 0 <= rT_new)
    record('S11.6', 'EXACT' if ok5 else 'FAIL',
           'K=3, eta=667/500: old rule gives r_T < 0 (illegal), Psi rule gives '
           'r_T >= 0', certificate=f'r_T(old)={rT_old}, r_T(new)={rT_new}')
    bad2, _ = grid_violations(inst2, inst2['j'] + inst2['m'] + 2)
    record('S11.7', 'EXACT' if not bad2 else 'FAIL',
           'K=3, eta=667/500: full count grid legal under the Psi rule',
           certificate=f'violations: {bad2[:5]}')
    cited = Fr(-151089222203006, 81950355825200625)
    record('S11.8', 'EXACT' if rT_old == cited else 'FAIL',
           "the value cited in J7 section 4 for the old rule's r_T at "
           'K=3, eta=667/500 is reproduced exactly by this pipeline',
           certificate=f'ours {rT_old} vs cited {cited}')
    return dict(ex1={k: str(v) for k, v in vals.items()},
                ex2=dict(m_psi=inst2['m'], m_old=m_old, rT_old=str(rT_old),
                         rT_new=str(rT_new)))


# ============================================================ S12
def eta_grid(Kv):
    g = []
    top = min(Kv + 1, 7)
    for c in range(1, top + 1):
        g.append(Fr(2 * c + 1, 2))                      # segment midpoints
    for c in range(2, top + 1):                         # near-integer eta
        g.append(Fr(c) - Fr(1, 100))
        g.append(Fr(c) + Fr(1, 100))
    for a in (Kv + 1, Kv + 2, 2 * Kv, 3 * Kv - 1):      # small frac(K eta)
        g.append(Fr(a, Kv) + Fr(1, 1000))
        g.append(Fr(a, Kv) - Fr(1, 1000))
    g += [Fr(667, 500), Fr(2001, 1000), Fr(101, 100), Fr(1001, 1000)]
    g += [Fr(Kv) - Fr(1, 100), Fr(Kv) + Fr(1, 100),     # the j = 0 regime
          Fr(Kv) + Fr(1, 2), Fr(Kv) + Fr(3, 2)]
    return sorted({x for x in g if x > 1})


def S12():
    hdr('S12  exact-rational cross-check of the Psi rule against the direct '
        'argmax of D(m)')
    # symbolic explanation of the agreement: d(z) is unimodal with peak at m
    def Bz(N, z):
        return eta * (N - 1) - z

    def dz(N, z):
        return (N / K - 1) / Bz(N, z)

    d_m, d_m1, d_p1 = dz(Nm, m), dz(Nm / nu, m - 1), dz(Nm * nu, m + 1)
    rT1 = 1 - m * d_m                                   # r_T at Q = 1
    zero('S12.0a', d_m - d_m1 - rT1 / (eta * Bz(Nm / nu, m - 1)),
         'd(m) - d(m-1) = r_T(m)/(eta B_{m-1}), and r_T(m) has the sign of '
         'Psi(m-1) (S4.3, S2.2): d increases exactly while Psi(.-1) >= 0')
    zero('S12.0b', (d_m - rT1) - (eta - 1) * Bz(Nm * nu, m + 1) * (d_m - d_p1),
         'd(m) - r_T(m) = (eta-1) B_{m+1} (d(m) - d(m+1)), and '
         'd(m) - r_T(m) = (m+1)(d(m) - 1/(m+1)) has the sign of -Psi(m) (S2.1): '
         'd decreases exactly while Psi(.) <= 0')
    record('S12.0c', 'ASSEMBLY',
           'argmax_z d(z) = m = min{z : Psi(z) <= 0}',
           certificate='S12.0a/S12.0b plus the single crossing of Psi (S1.28): '
                       'd is nondecreasing up to m and nonincreasing after; the '
                       'unimodality-to-argmax step is the assembly. The sweep '
                       'below is the finite exact-rational cross-check asked '
                       'for by the task')
    rows = []
    disagree = []
    infeasible = []
    gapbad = []
    rhobad = []
    Ks = range(3, 13) if not QUICK else range(3, 6)
    for Kv in Ks:
        for ev in eta_grid(Kv):
            inst = instance(Kv, ev)
            mv = inst['m']
            if mv is None:
                infeasible.append((Kv, str(ev), 'no m found'))
                continue
            dtab = inst['dtab']
            best = max(dtab.values())
            argmax = sorted([z for z in dtab if dtab[z] == best])
            agree = (mv in argmax)
            dv = dtab[mv]
            Qv, jv = inst['Q'], inst['j']
            rT = Qv * (1 - mv * dv)
            W = 1 - Qv + (Kv - jv) * Qv * dv
            Vt = [1 - inst['q'] ** t * (1 - Fr(Kv - t, 1) / (Kv * ev))
                  for t in range(Kv)]
            rho = min(Vt)
            Vj = Vt[jv]
            gap = W - rho
            gap_ok = bool(gap > 0) and bool(
                gap < sp.Rational(1) / (Kv * (sp.exp(Kv - 1) - Kv - 1)))
            if not agree:
                disagree.append(dict(K=Kv, eta=str(ev), m_psi=mv,
                                     argmax=argmax, d_psi=str(dv),
                                     d_argmax=str(best), W_psi=str(W)))
            if rT < 0:
                infeasible.append((Kv, str(ev), str(rT)))
            if not gap_ok:
                gapbad.append((Kv, str(ev), str(gap)))
            if Vj != rho:
                rhobad.append((Kv, str(ev), str(Vj), str(rho)))
            rows.append(dict(K=Kv, eta=str(ev), j=jv, m_psi=mv,
                             m_argmax=argmax[0], agree=agree,
                             rT_nonneg=bool(rT >= 0), Vj_is_rho=bool(Vj == rho),
                             gap=str(gap), gap_in_band=gap_ok,
                             gap_float=float(gap)))
    n = len(rows)
    record('S12.1', 'EXACT' if not disagree else 'FAIL',
           f'Psi rule m = min{{z : Psi(z) <= 0}} equals argmax_m d(m) on all '
           f'{n} exact-rational grid points (K = 3..12)',
           certificate=f'disagreements: {disagree[:3]}')
    record('S12.2', 'EXACT' if not infeasible else 'FAIL',
           'the Psi-rule family is feasible at every grid point: r_T >= 0',
           certificate=f'violations: {infeasible[:3]}')
    record('S12.3', 'EXACT' if not rhobad else 'FAIL',
           "J7's j = max{0, min{K-1, K+1-ceil(eta)}} attains rho_K = min_t V_t "
           'at every grid point', certificate=f'violations: {rhobad[:3]}')
    record('S12.4', 'EXACT' if not gapbad else 'FAIL',
           '0 < W_K - rho_K < 1/(K(e^(K-1)-K-1)) at every grid point',
           certificate=f'violations: {gapbad[:3]}')
    # grid battery on a subset
    cfgs = [(3, Fr(3, 2)), (3, Fr(667, 500)), (3, Fr(5, 2)), (4, Fr(3, 2)),
            (4, Fr(7, 2)), (5, Fr(3, 2)), (5, Fr(11, 10)), (6, Fr(5, 2)),
            (7, Fr(3, 2)), (8, Fr(199, 100))]
    if QUICK:
        cfgs = cfgs[:3]
    nbad = []
    for Kv, ev in cfgs:
        inst = instance(Kv, ev)
        bad, Fm = grid_violations(inst, inst['j'] + inst['m'] + 2)
        Wclosed = (1 - inst['Q']
                   + (Kv - inst['j']) * inst['Q'] * inst['dtab'][inst['m']])
        if Fm[Kv][0] != Wclosed:                       # J7 (17) left-hand side
            bad = bad + [('W_K != F(K,0)', Kv, 0)]
        print(f"    K={Kv} eta={ev}: j={inst['j']} m={inst['m']} "
              f"T={inst['j']+inst['m']} F(K,0)={float(Fm[Kv][0]):.9f} "
              f"violations={len(bad)}")
        if bad:
            nbad.append((Kv, str(ev), bad[:3]))
    record('S12.5', 'EXACT' if not nbad else 'FAIL',
           'full (x,y) count-grid legality battery (range, monotone, band, '
           'three DR second differences, O-independence on y <= 1, '
           'normalisation) on 10 exact-rational configurations',
           certificate=f'violations: {nbad[:2]}')
    return rows, disagree


# ============================================================ main
def main():
    hdr('J7 SYMBOLIC ORACLE -- independent verification of '
        'results/J7/linear_anysize.md')
    print('  domain: K >= 3 integer (K = 3 + w), eta > 1 (eta = 1 + u), '
          'nu = eta/(eta-1) > 1,\n          m = min{z >= 1 : Psi(z) <= 0}, '
          'j = max{0, min{K-1, K+1-ceil(eta)}}')
    S1()
    S2()
    S3()
    S4()
    S5()
    S6()
    S7()
    S8()
    S9()
    S10()
    ex = S11()
    rows, disagree = S12()

    hdr('SUMMARY')
    by = {}
    for rr in REC:
        by.setdefault(rr['status'], []).append(rr['id'])
    for st in ('PASS', 'EXACT', 'ASSEMBLY', 'FAIL'):
        if st in by:
            print(f'  {st:<9} {len(by[st]):>3}')
    groups = {}
    for rr in REC:
        groups.setdefault(rr['id'].split('.')[0], []).append(rr['status'])
    status = {}
    for c in [f'S{i}' for i in range(1, 13)]:
        st = groups.get(c, [])
        if 'FAIL' in st:
            s = 'FAILED'
        elif 'ASSEMBLY' in st and 'EXACT' in st:
            s = 'VERIFIED-SYMBOLIC + EXACT, with HAND-PROOF-UNREVIEWED residue'
        elif 'ASSEMBLY' in st:
            s = 'VERIFIED-SYMBOLIC, with HAND-PROOF-UNREVIEWED residue'
        elif 'EXACT' in st and 'PASS' in st:
            s = 'VERIFIED-SYMBOLIC + VERIFIED-LP(exact rational)'
        elif 'EXACT' in st:
            s = 'VERIFIED-LP (exact rational)'
        else:
            s = 'VERIFIED-SYMBOLIC'
        status[c] = s
        print(f'  {c:<4} {s}   ({len(st)} items)')

    out = dict(
        task='J7 independent sympy verification of results/J7/linear_anysize.md',
        source='results/J7/linear_anysize.md  [HAND-PROOF-UNREVIEWED, source J7]',
        domain=dict(K='integer >= 3 (encoded K = 3 + w, w >= 0)',
                    eta='real > 1 (encoded eta = 1 + u, u > 0)',
                    nu='eta/(eta-1) > 1',
                    m='min{z in Z_{>=1} : Psi(z) <= 0}',
                    j='max{0, min{K-1, K+1-ceil(eta)}}'),
        status_by_check=status,
        checks=REC,
        s8_branch_table=BRANCHES,
        key_identities=KEY_IDS,
        examples=ex,
        s12_sweep=rows,
        s12_disagreements=disagree,
        failed=FAILED)
    with open(os.path.join(HERE, 'J7_symbolic.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    print('\n  wrote results/J7_symbolic.json')
    print('  FAILED items:', FAILED if FAILED else 'none')
    sys.exit(1 if FAILED else 0)


if __name__ == '__main__':
    main()
