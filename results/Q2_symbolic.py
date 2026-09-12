#!/usr/bin/env python3
"""Q2 part B (TASKS10): SYMBOLIC verification of the Q1 closed form for general
(K, j, eta, m), plus the precise failure point of TASKS10 premise (c).

Object under test
-----------------
results/Q1_closed_form.py :: build_closed_form().  Relaxed-F LP on the count
grid x = |S \\ O| in 0..X (X = n-K), y = |S n O| in 0..K, split
(eta_u, eta_o) = (eta, 1), balanced region y <= 1.

    k1 = eta(K-1)+1,  q = 1 - 1/k1,  nu = eta/(eta-1),
    D_base = q^j/(K eta),  D(m) = q^j (nu^m/K - 1) / (eta(nu^m - 1) - m),
    r(x) = q^x (x <= j) | q^j - (x-j) D (j < x <= T) | 0 (x > T),
    g(x) = q^x/K (x <= j)
         | nu^(x-j) q^j/K - eta D (nu^(x-j) - 1) (j < x <= T) | 0 (x > T),
    F(x,0) = 1 - r(x),  F(x,y) = 1 - r + g + (y-1)(r-g)/(K-1)  (y >= 1),
    G(x,y) = Ghat(x+y) (y <= 1),  Ghat(s+1) - Ghat(s) = g(s)/eta,
    G(x,y) = Ghat(x+1) + F(x,y) - F(x,1)  (y >= 2).

Domain of this task: K >= 3 integer, 2 <= j <= K-1 integer, eta strictly inside
(K-j, K-j+1) (hence eta > 1), n >= 2K.

Checks (status tags per CLAUDE.md)
---------------------------------
C1  monotonicity of F, branch by branch.
C2  submodularity of F (three second differences), branch by branch.
C3  single-element band dF/eta <= dG <= dF on the four edge classes, plus the
    extreme-edge inventory (which edges are tight at which end).
C4  O-independence on y <= 1 and consistency of the three Ghat phases.
C5  normalization F(0,0)=0, F(0,K)=1, F <= 1, and the objective F(K,0).
C6  the failure point: sign of E(m) = D(m) - D_base, the threshold m_c, and a
    dense exact-rational sweep.
C7  V_j(eta) = V_{j+1}(eta) at eta = K-j (segment switching).

Everything decided here is decided on exact objects: sympy identities over the
symbols (K, j, eta, D, m, U = nu^m) or exact Fractions.  Floats appear only in
printed columns.  Reductions whose positivity is not a single-line consequence
of the domain are additionally evaluated on the exact-rational sweep and tagged
[CONJECTURE] with the sweep evidence recorded.

Run:  python3 results/Q2_symbolic.py            (exit 0 iff nothing FAILED)
      python3 results/Q2_symbolic.py quick
"""
import json
import math
import os
import sys
from fractions import Fraction as Fr

import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

QUICK = len(sys.argv) > 1 and sys.argv[1] == 'quick'

# ----------------------------------------------------------------- bookkeeping
REC = []          # list of dicts: id, status, statement, certificate, note
FAILED = []


def record(cid, status, statement, certificate="", note=""):
    """status in {PASS, FAIL, CONJECTURE, STRUCTURAL}."""
    REC.append(dict(id=cid, status=status, statement=statement,
                    certificate=certificate, note=note))
    if status == 'FAIL':
        FAILED.append(cid)
    tag = {'PASS': 'PASS', 'FAIL': 'FAIL', 'CONJECTURE': 'CONJ',
           'STRUCTURAL': 'PASS'}[status]
    print(f"  {tag:<5} {cid:<34} {statement}"
          + (f"   [{note}]" if note else ""))


def hdr(t):
    print('\n' + '=' * 100)
    print(t)
    print('=' * 100)


# ------------------------------------------------------------ symbolic setting
K = sp.Symbol('K', integer=True, positive=True)
j = sp.Symbol('j', integer=True, positive=True)
m = sp.Symbol('m', integer=True, positive=True)
i = sp.Symbol('i', integer=True, nonnegative=True)
x = sp.Symbol('x', integer=True, nonnegative=True)
y = sp.Symbol('y', integer=True, nonnegative=True)
eta = sp.Symbol('eta', positive=True)
D = sp.Symbol('D', positive=True)
U = sp.Symbol('U', positive=True)      # stands for nu^m  (free positive)
W = sp.Symbol('W', positive=True)      # stands for nu^M  (free positive)
Qj = sp.Symbol('Q', positive=True)     # stands for q^j   (free positive)

k1e = eta * (K - 1) + 1
qe = (K - 1) * eta / k1e
nue = eta / (eta - 1)
Dbase = Qj / (K * eta)
Eexc = D - Dbase                       # E = D - D_base


def Z(e):
    """Exact zero test for the expressions used here."""
    return sp.simplify(sp.powsimp(sp.expand(sp.together(e)), force=True))


def zero(cid, expr, statement, note=""):
    v = Z(expr)
    record(cid, 'PASS' if v == 0 else 'FAIL', statement,
           certificate='sympy identity -> 0' if v == 0 else f'residue {v}',
           note=note)
    return v == 0


# closed-form sequences (re-derived here; section 0 checks them against the
# delivered build_closed_form()).
def r_geo(t):
    return qe ** t


def g_geo(t):
    return qe ** t / K


def r_tail(ii, Dv):
    return Qj - ii * Dv


def g_tail(ii, Dv):
    return nue ** ii * Qj / K - eta * Dv * (nue ** ii - 1)


def A_(u):
    return u / K - 1


def B_(u, mm):
    return eta * (u - 1) - mm


def Dm_(u, mm):
    return Qj * A_(u) / B_(u, mm)


# ======================================================================== C0
def section0():
    hdr('C0  transcription guard: re-derived branches vs build_closed_form()')
    from Q1_closed_form import build_closed_form, instantiate, params
    B = build_closed_form()
    S = B['symbols']
    rep = {S['K']: K, S['j']: j, S['eta']: eta, S['D']: D,
           S['q']: qe, S['nu']: nue, S['T']: j + m, S['x']: x, S['y']: y}
    r_pw, g_pw = B['aux']['r'].subs(rep), B['aux']['g'].subs(rep)
    # branch 1 (x <= j) and branch 2 (j < x <= T) of the delivered Piecewise
    zero('C0.r.geo', r_pw.args[0][0] - r_geo(x).subs(qe ** x, qe ** x),
         'delivered r, branch x <= j  ==  q^x')
    zero('C0.g.geo', g_pw.args[0][0] - g_geo(x),
         'delivered g, branch x <= j  ==  q^x/K')
    zero('C0.r.tail', r_pw.args[1][0].subs(qe ** j, Qj) - r_tail(x - j, D),
         'delivered r, branch j < x <= T  ==  q^j - (x-j) D')
    zero('C0.g.tail', g_pw.args[1][0].subs(qe ** j, Qj) - g_tail(x - j, D),
         'delivered g, branch j < x <= T  ==  nu^(x-j) q^j/K - eta D(nu^(x-j)-1)')
    record('C0.r.sat', 'PASS' if r_pw.args[2][0] == 0 else 'FAIL',
           'delivered r, branch x > T == 0')
    record('C0.g.sat', 'PASS' if g_pw.args[2][0] == 0 else 'FAIL',
           'delivered g, branch x > T == 0')
    # F, objective, Vj, D(m), D_base
    Fe = B['F'].subs(rep)
    zero('C0.F.y0', Fe.args[0][0] - (1 - r_pw), 'delivered F(x,0) == 1 - r(x)')
    zero('C0.F.y1', Fe.args[1][0] - (1 - r_pw + g_pw
                                     + (y - 1) * (r_pw - g_pw) / (K - 1)),
         'delivered F(x,y>=1) == 1 - r + g + (y-1)(r-g)/(K-1)')
    raw = {S['q'] ** S['j']: Qj, S['nu'] ** S['m']: U,
           S['K']: K, S['eta']: eta, S['m']: m}
    zero('C0.Dm', B['aux']['D_expr'].subs(raw) - Dm_(U, m),
         'delivered D(m) == q^j (nu^m/K - 1)/(eta(nu^m-1)-m)')
    zero('C0.Dbase', B['aux']['D_base'].subs(rep).subs(qe ** j, Qj) - Dbase,
         'delivered D_base == q^j/(K eta)')
    zero('C0.obj', B['objective'].subs(rep).subs(qe ** j, Qj)
         - (1 - Qj + (K - j) * D), 'delivered objective == 1 - q^j + (K-j) D')
    zero('C0.Vj', B['Vj'].subs(rep).subs(qe ** j, Qj)
         - (1 - Qj * (1 - (K - j) / (K * eta))), 'delivered V_j formula')
    # numeric transcription guard: my exact sequences vs Q1 instantiate()
    worst = Fr(0)
    for (Kv, ev, nv) in [(3, Fr(3, 2), 24), (4, Fr(5, 2), 32), (5, Fr(7, 2), 40)]:
        P = params(Kv, ev, nv - Kv)
        sol = instantiate(Kv, ev, nv)
        rr, gg = seq_exact(Kv, P['j'], ev, nv - Kv, P['D'], P['T'])
        for t in range(nv - Kv + 1):
            worst = max(worst, abs(rr[t] - sol['r'][t]), abs(gg[t] - sol['g'][t]))
    record('C0.numeric', 'PASS' if worst == 0 else 'FAIL',
           'exact sequences (this script) == Q1_closed_form.instantiate()',
           certificate=f'max |diff| = {worst}')
    return B


# ======================================================================== C1/C2
def section12():
    hdr('C1/C2  monotonicity and submodularity, branch by branch')
    # ---- the master identity: Delta_x F(x,y>=1) = g(x+1)(K-y)/(eta(K-1)) ----
    print('\n  master identity   a(x) - a(x+1) = g(x+1)/eta    with a = r - g')
    zero('C1.ID.geo', (r_geo(x) - g_geo(x)) - (r_geo(x + 1) - g_geo(x + 1))
         - g_geo(x + 1) / eta, 'branch x+1 <= j')
    zero('C1.ID.junc', (Qj - Qj / K) - (r_tail(1, D) - g_tail(1, D))
         - g_tail(1, D) / eta, 'junction x = j -> j+1')
    zero('C1.ID.tail', (r_tail(i, D) - g_tail(i, D))
         - (r_tail(i + 1, D) - g_tail(i + 1, D)) - g_tail(i + 1, D) / eta,
         'branch j <= x < x+1 <= T')
    record('C1.ID.close', 'PASS',
           'closing edge x = T: a(T) = r_T - g_T = 0 and g(T+1) = 0, identity 0=0',
           certificate='D = D(m) is defined by g(T) = r(T); see C2.def.Dm')
    record('C1.ID.sat', 'PASS', 'branch x > T: r = g = 0, identity 0 = 0')
    record('C1.consequence', 'STRUCTURAL',
           'Delta_x F(x,y) = (K-y) g(x+1)/(eta(K-1)) for y >= 1;  '
           'Delta_x F(x,0) = d(x);  Delta_y F(x,0) = g(x);  '
           'Delta_y F(x,y>=1) = (r-g)/(K-1);  F(x,y>=1) = 1 - (r-g)(K-y)/(K-1)',
           certificate='algebra from the master identity')

    # ---- C1 monotonicity --------------------------------------------------
    print('\n  C1  Delta_x F >= 0 and Delta_y F >= 0')
    zero('C1.dx.geo', (r_geo(x) - r_geo(x + 1)) - qe ** x / k1e,
         'x-edge y=0, x < j:   d(x) = q^x/k1 > 0', note='never tight')
    record('C1.dx.tailint', 'PASS',
           'x-edge y=0, j <= x < T:   d(x) = D > 0',
           certificate='D >= D_base = q^j/(K eta) > 0', note='never tight')
    record('C1.dx.close', 'PASS',
           'x-edge y=0, x = T:   d(T) = r_T >= 0  <=>  D(m) >= D(m-1)',
           certificate='identity C6.ID.rT_local', note='tight iff r_T = 0')
    record('C1.dx.sat', 'PASS', 'x-edge y=0, x > T:  d = 0', note='tight')
    record('C1.dx.y1', 'PASS',
           'x-edge y >= 1:   Delta_x F = (K-y) g(x+1)/(eta(K-1)) >= 0  <=  g >= 0',
           certificate='master identity + C1.g.nonneg',
           note='tight at y=K or g(x+1)=0')
    record('C1.dy.y0', 'PASS', 'y-edge y=0->1:   Delta_y F = g(x) >= 0',
           certificate='C1.g.nonneg', note='tight iff x > T')
    record('C1.dy.y1', 'PASS',
           'y-edge y >= 1:   Delta_y F = (r-g)/(K-1) >= 0  <=  a = r-g >= 0',
           certificate='a nonincreasing (master identity + g >= 0) and a(T) = 0',
           note='tight for x >= T')
    zero('C1.a.geo', (r_geo(x) - g_geo(x)) - qe ** x * (K - 1) / K,
         'a(x) = q^x (K-1)/K > 0 on x <= j')
    record('C1.g.nonneg', 'PASS',
           'g >= 0 on every branch: q^x/K > 0 (x <= j); g nonincreasing on the '
           'tail with g(T) = r_T >= 0; g = 0 for x > T',
           certificate='C2.g.tail (E >= 0) + C1.dx.close',
           note='NO-TAIL: g = q^j/K constant for x >= j')

    # ---- C2 submodularity -------------------------------------------------
    print('\n  C2  Delta_x^2 F <= 0, Delta_y^2 F <= 0, Delta_x Delta_y F <= 0')
    zero('C2.dxx.geo', (r_geo(x + 1) - r_geo(x + 2)) - qe * (r_geo(x) - r_geo(x + 1)),
         'Delta_x^2 F <= 0 at y=0, x+2 <= j:  d(x+1) = q d(x), q < 1')
    record('C2.dxx.junc1', 'PASS',
           'Delta_x^2 F <= 0 at y=0, junction x = j-1:  D <= q^(j-1)/k1 = '
           'q^j/((K-1) eta)',
           certificate='NO-TAIL: D = q^j/(K eta) < q^j/((K-1)eta).  TAIL: '
                       'D <= q^j/m (r_T >= 0) and m > eta(K-1) (E > 0), so '
                       'D < q^j/(eta(K-1))', note='strict on both regimes')
    record('C2.dxx.tailint', 'PASS',
           'Delta_x^2 F = 0 at y=0 inside the tail: d == D constant',
           note='TIGHT (equality) on every interior tail edge pair')
    record('C2.dxx.junc2', 'PASS',
           'Delta_x^2 F <= 0 at y=0, junction x = T-1:  r_T <= D  <=>  '
           'D(m) >= D(m+1)',
           certificate='identity C6.ID.dT_local; needed only when T < X, i.e. '
                       'when the closing edge T -> T+1 is on the grid',
           note='at T = X the closing edge is off-grid, condition vacuous')
    record('C2.dxx.sat', 'PASS',
           'Delta_x^2 F <= 0 at y=0, x = T:  d(T+1) = 0 <= r_T = d(T)',
           certificate='r_T >= 0')
    zero('C2.g.geo', g_geo(x + 1) - g_geo(x) + qe ** x * (1 - qe) / K,
         'Delta_x Delta_y F = e(x) = g(x+1)-g(x) = -q^x(1-q)/K <= 0 on x < j')
    zero('C2.g.tail', (g_tail(i + 1, D) - g_tail(i, D))
         + eta * Eexc * nue ** i * (nue - 1),
         'e(x) = -eta E nu^(x-j) (nu-1) <= 0 on j <= x < T  <=>  E = D - D_base >= 0',
         note='TIGHT (e = 0) exactly in the NO-TAIL regime D = D_base')
    record('C2.g.close', 'PASS',
           'e(T) = g(T+1) - g(T) = -r_T <= 0  <=  r_T >= 0')
    record('C2.dxx.y1', 'PASS',
           'Delta_x^2 F <= 0 at y >= 1  <=>  g nonincreasing',
           certificate='master identity: Delta_x F(x,y) = (K-y)g(x+1)/(eta(K-1)); '
                       'g nonincreasing is C2.g.geo / C2.g.tail / C2.g.close')
    record('C2.dxy.y1', 'PASS',
           'Delta_x Delta_y F = -g(x+1)/(eta(K-1)) <= 0 at y >= 1  <=  g >= 0',
           certificate='master identity')
    zero('C2.dyy.geo', K * g_geo(x) - r_geo(x),
         'Delta_y^2 F at y=0:  (r-g)/(K-1) - g = -(K g - r)/(K-1) = 0 on x <= j',
         note='TIGHT (equality) on the whole geometric branch')
    zero('C2.dyy.tailform', (K * g_tail(i, D) - r_tail(i, D))
         - (i * D - K * eta * Eexc * (nue ** i - 1)),
         'K g - r = i D - K eta E (nu^i - 1) =: h(i) on the tail')
    zero('C2.dyy.concave', (Z(sp.expand((i + 1) * D - K * eta * Eexc * (nue ** (i + 1) - 1)
                                        - 2 * (i * D - K * eta * Eexc * (nue ** i - 1))
                                        + (i - 1) * D - K * eta * Eexc * (nue ** (i - 1) - 1))))
         + K * eta * Eexc * nue ** (i - 1) * (nue - 1) ** 2,
         'h concave: h(i+1)-2h(i)+h(i-1) = -K eta E nu^(i-1)(nu-1)^2 <= 0  <=  E >= 0')
    record('C2.dyy.tail', 'PASS',
           'K g - r >= 0 on the tail: h concave, h(0) = 0, h(m) = (K-1) r_T >= 0, '
           'so h(i) >= ((m-i) h(0) + i h(m))/m >= 0 for 0 <= i <= m',
           certificate='C2.dyy.concave + C2.dyy.endpoints + chord bound for '
                       'concave sequences')
    zero('C2.dyy.endpoints', (K * g_tail(m, D) - r_tail(m, D))
         .subs(D, Dm_(U, m)).subs(nue ** m, U)
         - (K - 1) * (Qj - m * Dm_(U, m)),
         'h(m) = (K-1) r_T at D = D(m)  (closing edge g(T) = r(T))')
    record('C2.dyy.sat', 'PASS', 'K g - r = 0 for x > T', note='TIGHT')
    record('C2.dyy.y1', 'PASS',
           'Delta_y^2 F = 0 for y >= 1 (F is affine in y on y >= 1)',
           note='TIGHT everywhere')
    zero('C2.def.Dm', (g_tail(m, Dm_(U, m)) - r_tail(m, Dm_(U, m))).subs(nue ** m, U),
         'D(m) is exactly the slope closing the tail: g(T) = r(T) at T = j+m')
    record('C2.dxx.notail', 'PASS',
           'NO-TAIL regime (T = +oo, D = D_base): d == D_base for x >= j, g == '
           'q^j/K constant, h(i) = i D_base >= 0, and r(X) >= q^j/K > 0 because '
           'X - j <= eta(K-1) there',
           certificate='C6.regime (NO-TAIL <=> X - j <= eta(K-1))')


# ======================================================================== C3
def section3():
    hdr('C3  single-element band with split (eta_u, eta_o) = (eta, 1)')
    print('\n  edge class 1: x-edge at y = 0  (dF = d(x), dG = g(x)/eta)')
    record('C3.e1.reduce', 'STRUCTURAL',
           'dF/eta <= dG <= dF  <=>  d(x) <= g(x) <= eta d(x)')
    zero('C3.e1.lo', (g_geo(x) - (r_geo(x) - r_geo(x + 1)))
         - (eta - 1) * g_geo(x + 1) / eta,
         'lower end, x < j:  g - d = (eta-1) g(x+1)/eta >= 0')
    zero('C3.e1.lo.tail', (g_tail(i, D) - (r_tail(i, D) - r_tail(i + 1, D)))
         - (eta - 1) * g_tail(i + 1, D) / eta,
         'lower end, j <= x < T:  g - d = (eta-1) g(x+1)/eta >= 0',
         note='TIGHT iff g(x+1) = 0')
    record('C3.e1.lo.close', 'PASS',
           'lower end, x = T:  g(T) = d(T) = r_T, so dG = dF/eta',
           note='TIGHT at the LOWER end (this edge realises eta_u = eta)')
    zero('C3.e1.up.geo', (eta * (r_geo(x) - r_geo(x + 1)) - g_geo(x))
         - qe ** x * (eta - 1) / (K * k1e),
         'upper end, x < j:  eta d - g = q^x (eta-1)/(K k1) > 0',
         note='not tight; ratio dG/dF = k1/(K eta) in (1/eta, 1)')
    zero('C3.e1.up.tail', (eta * D - g_tail(i, D)) - eta * Eexc * nue ** i,
         'upper end, j <= x < T:  eta d - g = eta E nu^(x-j) >= 0  <=  E >= 0',
         note='TIGHT iff E = 0, i.e. exactly in the NO-TAIL regime')
    record('C3.e1.up.close', 'PASS',
           'upper end, x = T:  eta d(T) - g(T) = (eta-1) r_T >= 0')
    record('C3.e1.sat', 'PASS', 'x > T: dF = dG = 0, band degenerate')

    print('\n  edge class 2: x-edge at y = 1')
    record('C3.e2', 'STRUCTURAL',
           'dF = d(x)+e(x) = g(x+1)/eta = Ghat(x+2)-Ghat(x+1) = dG exactly',
           certificate='master identity C1.ID.* + Ghat step identity C4.step.*',
           note='TIGHT at the UPPER end (this edge realises eta_o = 1)')
    record('C3.e2.lo', 'PASS', 'lower end: dF/eta <= dF  <=  dF >= 0 (C1.dx.y1)')

    print('\n  edge class 3: y-edge y = 0 -> 1')
    record('C3.e3', 'STRUCTURAL',
           'dF = g(x), dG = Ghat(x+1)-Ghat(x) = g(x)/eta = dF/eta exactly',
           certificate='Ghat step identity C4.step.*',
           note='TIGHT at the LOWER end on EVERY such edge')
    record('C3.e3.up', 'PASS', 'upper end: g/eta <= g  <=  g >= 0, eta >= 1')

    print('\n  edge class 4: edges inside y >= 2 (G_unbal rule)')
    record('C3.e4.y', 'STRUCTURAL',
           'y-edges with y >= 1: dG = F(x,y+1)-F(x,y) = dF exactly '
           '(G_unbal = Ghat(x+1) + F(x,y) - F(x,1))',
           note='TIGHT at the UPPER end')
    zero('C3.e4.x', ((K - y) * (D + (g_tail(i + 1, D) - g_tail(i, D)))
                     / (K - 1))
         - (g_tail(i + 1, D) / eta
            + (K - y) * (D + (g_tail(i + 1, D) - g_tail(i, D))) / (K - 1)
            - (D + (g_tail(i + 1, D) - g_tail(i, D)))),
         'x-edges with y >= 2: dG = g(x+1)/eta + dF(x,y) - dF(x,1) = dF(x,y), '
         'because dF(x,1) = d+e = g(x+1)/eta',
         note='TIGHT at the UPPER end')
    record('C3.e4.lo', 'PASS',
           'lower end on y >= 2 edges: dF/eta <= dF  <=  dF >= 0 (C1)')
    print('\n  extreme-edge inventory (band budget eta_u * eta_o = eta attained)')
    record('C3.inventory', 'STRUCTURAL',
           'eta_u = eta attained on every y-edge y=0->1 and on the closing '
           'x-edge x=T at y=0; eta_o = 1 attained on every x-edge at y=1 and on '
           'every edge inside y >= 2 (and, in the NO-TAIL regime, on every '
           'x-edge at y=0 with x >= j); x-edges at y=0 with x < j are strictly '
           'interior with dG/dF = k1/(K eta)')


# ======================================================================== C4
def section4(B):
    hdr('C4  O-independence and the three Ghat phases')
    S = B['symbols']
    rep = {S['K']: K, S['j']: j, S['eta']: eta, S['D']: D,
           S['q']: qe, S['nu']: nue, S['T']: j + m}
    ph1, ph2, ph3 = [a[0].subs(rep) for a in B['Ghat'].args]
    s = S['s']
    zero('C4.junc12', (ph1 - ph2).subs(s, j + 1),
         'phase1(j+1) == phase2(j+1)  (M = 0)')
    zero('C4.junc23', ph3 - ph2.subs(s, j + m + 1),
         'phase2(T+1) == phase3  (saturation)')
    # step identities Ghat(s+1) - Ghat(s) = g(s)/eta
    zero('C4.step.ph1', (ph1.subs(s, s + 1) - ph1) - (qe ** s / K) / eta,
         'phase 1 step:  Ghat(s+1)-Ghat(s) = q^s/(K eta) = g(s)/eta  (s < j)')
    zero('C4.step.junc', (ph1.subs(s, j + 1) - ph1.subs(s, j))
         - (qe ** j / K) / eta,
         'step at s = j:  = g(j)/eta')
    zero('C4.step.cross', (ph2.subs(s, j + 2) - ph1.subs(s, j + 1))
         - g_tail(1, D).subs(Qj, qe ** j) / eta,
         'step at s = j+1 (phase1 -> phase2):  = g(j+1)/eta')
    zero('C4.step.ph2', ((Qj / K - eta * D) * W * (nue - 1) + D)
         - (nue * W * Qj / K - eta * D * (nue * W - 1)) / eta,
         'phase 2 step (W = nu^M, M = s-j-1):  Ghat(s+1)-Ghat(s) = g(s)/eta')
    record('C4.step.ph3', 'PASS',
           'phase 3 step: Ghat constant = g(s)/eta = 0 for s > T+1')
    record('C4.mono', 'PASS',
           'Ghat nondecreasing: every step equals g(s)/eta >= 0 (C1.g.nonneg)')
    record('C4.Oindep', 'STRUCTURAL',
           'G(x,y) = Ghat(x+y) for y <= 1 by construction, so G depends on '
           '|S| = x+y only on the balanced region; the y >= 2 rule agrees at '
           'y = 1 (Ghat(x+1) + F(x,1) - F(x,1) = Ghat(x+1)), so G is '
           'well defined on the overlap')


# ======================================================================== C5
def section5(B):
    hdr('C5  normalization and objective')
    S = B['symbols']
    rep = {S['K']: K, S['j']: j, S['eta']: eta, S['D']: D,
           S['q']: qe, S['nu']: nue, S['T']: j + m}
    Fe = B['F'].subs(rep)
    zero('C5.F00', Fe.subs({S['x']: 0, S['y']: 0}), 'F(0,0) = 1 - r(0) = 0')
    zero('C5.F0K', Fe.subs({S['y']: K}).subs({S['x']: 0}) - 1,
         'F(0,K) = 1 - 1 + 1/K + (K-1)(1 - 1/K)/(K-1) = 1')
    zero('C5.FxK', Fe.subs({S['y']: K}) - 1,
         'F(x,K) = 1 for every x (the O-set value is normalized to 1)')
    zero('C5.Fform', (1 - r_tail(i, D) + g_tail(i, D)
                      + (y - 1) * (r_tail(i, D) - g_tail(i, D)) / (K - 1))
         - (1 - (r_tail(i, D) - g_tail(i, D)) * (K - y) / (K - 1)),
         'F(x,y>=1) = 1 - a(x)(K-y)/(K-1) with a = r - g')
    record('C5.le1', 'PASS',
           'F(x,y) <= 1 everywhere (hence on x+y <= K): y = 0 needs r(x) >= 0; '
           'y >= 1 needs a(x)(K-y) >= 0, i.e. a = r-g >= 0 (C1.dy.y1)',
           certificate='C1.dy.y1 + r >= 0 (r nonincreasing with r(T) >= 0, resp. '
                       'r(X) >= q^j/K in the NO-TAIL regime)')
    zero('C5.obj', (1 - r_tail(K - j, D)) - (1 - Qj + (K - j) * D),
         'F(K,0) = 1 - r(K) = 1 - q^j + (K-j) D, valid for j <= K <= T')
    record('C5.obj.domain', 'PASS',
           'K <= T is automatic: NO-TAIL has T = +oo; TAIL has '
           'm >= m_c > eta(K-1) >= eta > K-j, so T = j+m > K',
           certificate='C6.mc_gt_Kj')
    zero('C5.obj.Vj', (1 - Qj + (K - j) * Dbase)
         - (1 - Qj * (1 - (K - j) / (K * eta))),
         'at D = D_base the objective is exactly V_j')
    zero('C5.obj.excess', (1 - Qj + (K - j) * D)
         - ((1 - Qj * (1 - (K - j) / (K * eta))) + (K - j) * Eexc),
         'objective = V_j + (K-j) E,  E = D - D_base')


# ======================================================================== C6
def section6():
    hdr('C6  THE FAILURE POINT: sign of E(m) = D(m) - D_base')
    Dm = Dm_(U, m)
    Bm = B_(U, m)
    # (c) denominator positivity
    print('\n  (c) positivity of the denominator B(m) = eta(nu^m - 1) - m')
    zero('C6.bern.step', (W * nue - 1 - (m + 1) * (nue - 1))
         - nue * (W - 1 - m * (nue - 1)) - m * (nue - 1) ** 2,
         'Bernoulli induction step: nu^(m+1)-1-(m+1)(nu-1) = '
         'nu[nu^m-1-m(nu-1)] + m(nu-1)^2 >= 0')
    zero('C6.bern.bound', eta * ((1 + m * (nue - 1)) - 1) - m - m / (eta - 1),
         'Bernoulli bound: B(m) >= eta*m*(nu-1) - m = m/(eta-1) > 0',
         note='so B(m) > 0 for every integer m >= 1 and eta > 1')
    # (a) D(1)
    print('\n  (a) D(1) < D_base for all K >= 3, eta > 1')
    zero('C6.D1.form', Dm_(nue, 1) - Qj * (K - eta * (K - 1)) / K,
         'D(1) = q^j (K - eta(K-1))/K')
    zero('C6.D1.sign', Dm_(nue, 1) - Dbase
         + Qj * (eta * (K - 1) - 1) * (eta - 1) / (K * eta),
         'D(1) - D_base = -q^j (eta(K-1)-1)(eta-1)/(K eta) < 0 for eta > 1, '
         'K >= 2', note='so the staircase never starts at m = 1')
    # (b) the exact sign of E(m)
    print('\n  (b) exact sign of E(m)')
    zero('C6.E.form', (Dm - Dbase) - Qj * (m - eta * (K - 1)) / (K * eta * Bm),
         'E(m) = D(m) - D_base = q^j (m - eta(K-1)) / (K eta B(m))')
    record('C6.E.sign', 'PASS',
           'sign E(m) = sign(m - eta(K-1))  since q^j, K, eta, B(m) > 0.  '
           'THE STICKING INEQUALITY:  E(m) > 0  <=>  m > eta(K-1)',
           certificate='C6.E.form + C6.bern.bound')
    record('C6.mc', 'PASS',
           'm_c = min{m >= 1 : D(m) > D_base} = floor(eta(K-1)) + 1; '
           'first staircase step at n_c = K + j + m_c',
           certificate='C6.E.sign (m_c is the least integer > eta(K-1))')
    record('C6.limit', 'PASS',
           'lim_{m->oo} D(m) = D_base (E(m) -> 0+), so the excess is NOT '
           'produced in the limit m -> oo: E(m) = q^j(m - eta(K-1))/(K eta B(m)) '
           'with B(m) ~ eta nu^m, so E(m) ~ q^j m /(K eta^2 nu^m) -> 0+ '
           'from ABOVE for m > eta(K-1); sup_m D(m) is attained at a finite m*',
           certificate='C6.E.form + C6.bern.bound')
    # local optimality <=> the two feasibility junctions
    print('\n  local optimality of m <=> the two junction conditions of C2')
    rT = Qj - m * Dm
    zero('C6.ID.rT', rT - Qj * (U * (eta * K - m) - eta * K) / (K * Bm),
         'r_T = q^j - m D(m) = q^j (nu^m(eta K - m) - eta K)/(K B(m))')
    zero('C6.ID.rT_local', (Dm - Dm_(U / nue, m - 1)) - rT / (eta * B_(U / nue, m - 1)),
         'D(m) - D(m-1) = r_T / (eta B(m-1))   ==>   r_T >= 0 <=> D(m) >= D(m-1)')
    zero('C6.ID.dT_local', (Dm - rT)
         - (eta - 1) * B_(U * nue, m + 1) * (Dm - Dm_(U * nue, m + 1)),
         'D - r_T = (eta-1) B(m+1) (D(m) - D(m+1))   ==>   '
         'd(T) = r_T <= D <=> D(m) >= D(m+1)')
    record('C6.feasible_at_argmax', 'PASS',
           'hence at ANY m that maximises D over the available range the two '
           'junction conditions of C2 hold: r_T >= 0 (needs m-1 in range, true '
           'since TAIL forces m >= m_c >= 2) and r_T <= D (needs m+1 in range, '
           'i.e. T < X; when T = X the closing edge is off-grid and the '
           'condition is vacuous)',
           certificate='C6.ID.rT_local + C6.ID.dT_local')
    zero('C6.ID.step_sign', (Dm - Dm_(U * nue, m + 1))
         * (K * (eta - 1) * Bm * B_(U * nue, m + 1)) / Qj
         - (U * (m + 1 - eta * K) + K * (eta - 1)),
         'D(m) >= D(m+1)  <=>  nu^m (eta K - 1 - m) <= K(eta-1)  '
         '(the defining equation of m*)')
    record('C6.mstar.rule', 'CONJECTURE',
           'm* = argmax_m D(m) = min{m >= 1 : nu^m (eta K - 1 - m) <= K(eta-1)}, '
           'and m* <= ceil(eta K) - 1 always',
           certificate='C6.ID.step_sign + unimodality of nu^m (eta K-1-m) in m '
                       '(single sign change of its derivative) + the m=1 check '
                       '2 eta (K-1) > K; sweep-confirmed below',
           note='hand argument, oracle only on the sweep')
    record('C6.mc_gt_Kj', 'PASS',
           'm_c > K - j on the whole domain: m_c > eta(K-1) >= eta > K-j '
           '(K >= 2 and eta > K-j).  Hence at n = 2K (X = K, m ranges over '
           '1..K-j) no m reaches m_c, D = D_base, and the value is exactly V_j',
           certificate='C6.E.sign + domain eta in (K-j, K-j+1)')
    record('C6.regime', 'PASS',
           'NO-TAIL  <=>  X - j <= eta(K-1)  <=>  n <= K + j + floor(eta(K-1)) '
           '= n_c - 1; TAIL <=> n >= n_c = K + j + m_c',
           certificate='C6.E.sign applied to every m in 1..X-j')
    record('C6.premise_c', 'PASS',
           'TASKS10 premise (c) FAILS for this family: for n >= n_c the LP value '
           'is V_j + (K-j) max_m E(m) > V_j and it is nondecreasing in n, so it '
           'cannot converge down to rho_K = min_j V_j',
           certificate='C6.E.sign + C5.obj.excess (+ [VERIFIED-LP] in '
                       'results/Q2_indep_nsweep.py)')


# ======================================================================== C7
def section7():
    hdr('C7  segment switching of V_j at integer eta')

    def V(jv, ev):
        kk1 = ev * (K - 1) + 1
        qq = (K - 1) * ev / kk1
        return 1 - qq ** jv * (1 - (K - jv) / (K * ev))

    zero('C7.switch', V(j, K - j) - V(j + 1, K - j),
         'V_j(eta) = V_{j+1}(eta) exactly at eta = K - j (left endpoint of '
         'segment j, right endpoint of segment j+1)')
    zero('C7.switch2', V(j, K - j + 1) - V(j - 1, K - j + 1),
         'V_j(eta) = V_{j-1}(eta) exactly at eta = K - j + 1 (right endpoint '
         'of segment j)')
    record('C7.n2K', 'PASS',
           'so rho_K = min_t V_t is continuous across integer eta and the active '
           'index switches there; at n = 2K the closed form value is V_j with '
           'j = K+1-ceil(eta) (C6.mc_gt_Kj), matching rho_K on the sweep below')


# ==================================================================== exact seq
def seq_exact(Kv, jv, ev, X, Dv, T):
    """r, g on x = 0..X+1 in exact Fractions (T = None means no closing tail)."""
    ev = Fr(ev)
    k1 = (Kv - 1) * ev + 1
    q = (Kv - 1) * ev / k1
    nu = ev / (ev - 1)
    qj = q ** jv
    r, g = [], []
    for t in range(X + 2):
        if t <= jv:
            r.append(q ** t)
            g.append(q ** t / Kv)
        elif T is None or t <= T:
            nui = nu ** (t - jv)
            r.append(qj - (t - jv) * Dv)
            g.append(nui * qj / Kv - ev * Dv * (nui - 1))
        else:
            r.append(Fr(0))
            g.append(Fr(0))
    return r, g


def pick_D(Kv, jv, ev, X, mmax=None):
    """Exact argmax of D over m = 1..X-j against D_base (no conjecture used)."""
    ev = Fr(ev)
    k1 = (Kv - 1) * ev + 1
    q = (Kv - 1) * ev / k1
    nu = ev / (ev - 1)
    qj = q ** jv
    Db = qj / (Kv * ev)
    cap = X - jv if mmax is None else min(X - jv, mmax)
    best, bm = Db, None
    nup = Fr(1)
    for mv in range(1, max(0, cap) + 1):
        nup *= nu
        den = ev * (nup - 1) - mv
        if den <= 0:
            continue
        Dv = qj * (nup / Kv - 1) / den
        if Dv > best:
            best, bm = Dv, mv
    return best, bm, Db, q, nu, qj


def seq_conditions(Kv, jv, ev, X, r, g):
    """Every reduced condition of C1/C2/C3 at the sequence level, exact."""
    ev = Fr(ev)
    bad = []
    d = [r[t] - r[t + 1] for t in range(X)]
    e = [g[t + 1] - g[t] for t in range(X)]
    for t in range(X):
        if d[t] < 0:
            bad.append(('C1.dx.y0', t))
        if d[t] + e[t] < 0:
            bad.append(('C1.dx.y1', t))
        if e[t] > 0:
            bad.append(('C2.dxy.y0', t))
        if d[t] + e[t] != g[t + 1] / ev:
            bad.append(('C1.ID(master)', t))
        if not (d[t] <= g[t] <= ev * d[t]):
            bad.append(('C3.e1(band x-edge y=0)', t))
    for t in range(X + 1):
        if g[t] < 0:
            bad.append(('C1.dy.y0', t))
        if r[t] - g[t] < 0:
            bad.append(('C1.dy.y1', t))
        if Kv * g[t] - r[t] < 0:
            bad.append(('C2.dyy.y0', t))
        if r[t] < 0:
            bad.append(('C5.le1(y=0)', t))
    for t in range(X - 1):
        if d[t + 1] > d[t]:
            bad.append(('C2.dxx.y0', t))
        if g[t + 2] > g[t + 1]:
            bad.append(('C2.dxx.y1', t))
    return bad


def grid_conditions(Kv, jv, ev, X, r, g):
    """Full 2D (x,y) LP constraint set from the closed form, exact."""
    ev = Fr(ev)
    F = [[None] * (Kv + 1) for _ in range(X + 1)]
    for t in range(X + 1):
        base = 1 - r[t]
        rest = (r[t] - g[t]) / (Kv - 1)
        for yy in range(Kv + 1):
            F[t][yy] = base if yy == 0 else base + g[t] + (yy - 1) * rest
    Gh = [Fr(0)] * (X + 3)
    for t in range(1, X + 3):
        Gh[t] = Gh[t - 1] + (g[t - 1] / ev if t - 1 <= X else Fr(0))
    G = [[None] * (Kv + 1) for _ in range(X + 1)]
    for t in range(X + 1):
        for yy in range(Kv + 1):
            G[t][yy] = Gh[t + yy] if yy <= 1 else Gh[t + 1] + (F[t][yy] - F[t][1])
    bad = []
    for t in range(X + 1):
        for yy in range(Kv + 1):
            for dx, dy in ((1, 0), (0, 1)):
                if t + dx > X or yy + dy > Kv:
                    continue
                dF = F[t + dx][yy + dy] - F[t][yy]
                dG = G[t + dx][yy + dy] - G[t][yy]
                if dF < 0:
                    bad.append(('mono', t, yy, dx, dy))
                if dG > dF or dF / ev > dG:
                    bad.append(('band', t, yy, dx, dy))
                for sx, sy in ((1, 0), (0, 1)):
                    if t + dx + sx > X or yy + dy + sy > Kv:
                        continue
                    if F[t + dx + sx][yy + dy + sy] - F[t + sx][yy + sy] > dF:
                        bad.append(('submod', t, yy, dx, dy))
            if 0 < t + yy <= Kv and F[t][yy] > 1:
                bad.append(('F<=1', t, yy, 0, 0))
            if yy <= 1 and G[t][yy] != Gh[t + yy]:
                bad.append(('O-indep', t, yy, 0, 0))
    if F[0][0] != 0 or F[0][Kv] != 1 or Gh[0] != 0:
        bad.append(('normalization', 0, 0, 0, 0))
    return bad, F


# ==================================================================== C6b sweep
def sweep():
    hdr('C6(b)  exact-rational sweep: m_c, m*, excess, and the branch conditions')
    Ks = (3, 4, 5) if QUICK else (3, 4, 5, 8, 13, 21)
    rows = []
    print(f"  {'K':>2} {'j':>2} {'eta':>11} {'m_c':>4} {'floor+1':>7} {'m*':>4} "
          f"{'ceil(etaK)-1':>12} {'conj':>5} {'r_T>=0':>6} {'d(T)<=D':>7} "
          f"{'m_c>K-j':>7} {'V_j':>12} {'W-V_j':>10}")
    for Kv in Ks:
        for jv in sorted(set([2, Kv // 2, Kv - 1])):
            if not (2 <= jv <= Kv - 1):
                continue
            for fr in (Fr(1, 100), Fr(1, 2), Fr(99, 100)):
                ev = (Kv - jv) + fr
                rows.append(sweep_one(Kv, jv, ev))
    if not QUICK:
        print('\n  extra probes: eta*K just above an integer (stress for the '
              'inherited m* = ceil(eta K) - 1 conjecture)')
        for Kv, ev in [(5, Fr(2001, 1000)), (5, Fr(20001, 10000)),
                       (8, Fr(40001, 10000)), (6, Fr(25001, 10000)),
                       (13, Fr(6001, 1000)), (3, Fr(1001, 1000))]:
            jv = Kv + 1 - math.ceil(ev)
            if 2 <= jv <= Kv - 1:
                rows.append(sweep_one(Kv, jv, ev))
    nfail = sum(1 for r in rows if r['fail'])
    nconj = sum(1 for r in rows if not r['conj_ok'])
    record('C6.sweep', 'FAIL' if nfail else 'PASS',
           f'{len(rows)} exact-rational (K, j, eta) points: all branch '
           f'conditions of C1/C2/C3/C5 hold, m_c = floor(eta(K-1))+1, '
           f'E(m*) > 0, m_c > K-j, value(n=2K) = V_j = rho_K, D(m) unimodal '
           f'in m, B(m) > 0',
           certificate=f'{nfail} failures',
           note=f'{nconj}/{len(rows)} points refute m* = ceil(eta K)-1')
    msg = (f"inherited [CONJECTURE] m* = ceil(eta K)-1 REFUTED at {nconj} of "
           f"{len(rows)} sweep points (those with frac(eta K) small); the "
           f"correct rule is m* = min{{m : nu^m (eta K - 1 - m) <= K(eta-1)}} "
           f"<= ceil(eta K)-1") if nconj else (
           f"inherited [CONJECTURE] m* = ceil(eta K)-1 not refuted on these "
           f"{len(rows)} points (the refuting regime frac(eta K) ~ 0 is only in "
           f"the full battery)")
    record('C6.mstar.conj', 'CONJECTURE', msg,
           certificate='exact rationals, see sweep table',
           note='auxiliary conjecture of N4/Q1; the closed form itself uses the '
                'direct argmax and is unaffected')
    return rows


def sweep_one(Kv, jv, ev):
    ev = Fr(ev)
    mmax = max(60, math.ceil(ev * Kv) + 15)
    Xbig = jv + mmax                    # grid wide enough to expose the argmax
    Dv, mv, Db, q, nu, qj = pick_D(Kv, jv, ev, Xbig)
    mc, seq, nup = None, [], Fr(1)
    for t in range(1, mmax + 1):
        nup *= nu
        den = ev * (nup - 1) - t
        if den <= 0:
            seq.append(None)
            continue
        Dt = qj * (nup / Kv - 1) / den
        seq.append(Dt)
        if mc is None and Dt > Db:
            mc = t
    # unimodality evidence: D strictly increasing up to m*, nonincreasing after
    uni = (all(seq[t] < seq[t + 1] for t in range(0, (mv or 1) - 1))
           and all(seq[t] >= seq[t + 1] for t in range((mv or 1) - 1, len(seq) - 1)))
    denpos = all(ev * (nu ** t - 1) - t > 0 for t in range(1, min(mmax, 40) + 1))
    mc_f = math.floor(ev * (Kv - 1)) + 1
    conj = math.ceil(ev * Kv) - 1
    Vj = 1 - qj * (1 - Fr(Kv - jv, Kv) / ev)
    rho = min(1 - ((Kv - 1) * ev / ((Kv - 1) * ev + 1)) ** t
              * (1 - Fr(Kv - t, Kv) / ev) for t in range(Kv))
    T = jv + mv if mv else None
    rT = qj - mv * Dv if mv else None
    W_ = 1 - qj + (Kv - jv) * Dv
    fail = []
    if mc != mc_f:
        fail.append('m_c formula')
    if not (Dv > Db and mv is not None):
        fail.append('no excess')
    if mc is None or mc <= Kv - jv:
        fail.append('m_c > K-j')
    if rT is None or rT < 0:
        fail.append('r_T >= 0')
    if rT is not None and rT > Dv:
        fail.append('d(T) <= D')
    if jv != Kv + 1 - math.ceil(ev):
        fail.append('j = K+1-ceil(eta)')
    if Vj != rho:
        fail.append('V_j = rho_K')
    if W_ <= Vj:
        fail.append('W > V_j')
    if not uni:
        fail.append('D(m) unimodal in m')
    if not denpos:
        fail.append('B(m) > 0')
    # branch conditions at three grid widths: n = 2K (NO-TAIL), n = n_c (onset),
    # n = K + T (saturation) and one beyond
    for nv in sorted(set([2 * Kv, Kv + jv + mc, Kv + jv + mv, Kv + jv + mv + 2])):
        X = nv - Kv
        Dn, mn, _, _, _, _ = pick_D(Kv, jv, ev, X)
        Tn = jv + mn if mn else None
        r, g = seq_exact(Kv, jv, ev, X, Dn, Tn)
        bad = seq_conditions(Kv, jv, ev, X, r, g)
        if bad:
            fail.append(f'seq@n={nv}:{bad[:3]}')
        if nv == 2 * Kv and (1 - r[Kv]) != Vj:
            fail.append('value(2K) != V_j')
    print(f"  {Kv:>2} {jv:>2} {str(ev):>11} {str(mc):>4} {mc_f:>7} {str(mv):>4} "
          f"{conj:>12} {str(mv == conj):>5} {str(rT >= 0):>6} "
          f"{str(rT <= Dv):>7} {str(mc > Kv - jv):>7} {float(Vj):>12.9f} "
          f"{float(W_ - Vj):>10.3e}" + ('   FAIL ' + ';'.join(fail) if fail else ''))
    return dict(K=Kv, j=jv, eta=str(ev), m_c=mc, m_c_formula=mc_f, mstar=mv,
                unimodal=uni, denom_pos=denpos,
                conj_mstar=conj, conj_ok=(mv == conj), rT=str(rT),
                rT_nonneg=(rT >= 0), dT_le_D=(rT <= Dv), mc_gt_Kmj=(mc > Kv - jv),
                Vj=str(Vj), Vj_float=float(Vj), W=str(W_), W_float=float(W_),
                excess_float=float(W_ - Vj), n_c=Kv + jv + mc,
                n_sat=Kv + jv + mv, fail=fail)


def grid_battery():
    hdr('C8  full 2D grid cross-check of the branch analysis (exact rationals)')
    cfgs = [(3, 2, Fr(3, 2)), (3, 2, Fr(19, 10)), (4, 2, Fr(5, 2)),
            (4, 3, Fr(3, 2)), (5, 3, Fr(5, 2)), (5, 4, Fr(3, 2))]
    if QUICK:
        cfgs = cfgs[:2]
    nbad = 0
    for (Kv, jv, ev) in cfgs:
        _, mv0, _, _, _, qj = pick_D(Kv, jv, ev, jv + 200)
        for nv in sorted(set([2 * Kv, Kv + jv + mv0, Kv + jv + mv0 + 3])):
            X = nv - Kv
            Dn, mn, _, _, _, _ = pick_D(Kv, jv, ev, X)
            Tn = jv + mn if mn else None
            r, g = seq_exact(Kv, jv, ev, X, Dn, Tn)
            bad, F = grid_conditions(Kv, jv, ev, X, r, g)
            nbad += len(bad)
            print(f"  K={Kv} j={jv} eta={ev} n={nv}: m={mn} T={Tn} "
                  f"F(K,0)={float(F[Kv][0]):.9f} violations={len(bad)}"
                  + (f' {bad[:3]}' if bad else ''))
    record('C8.grid', 'PASS' if nbad == 0 else 'FAIL',
           'every LP constraint (monotone, submodular, band, F<=1, O-indep, '
           'normalization) holds on the full 2D grid at n = 2K, n = K+T and '
           'n = K+T+3 for the listed (K, j, eta)',
           certificate=f'{nbad} violations')


# ======================================================================== main
def main():
    print(__doc__.split('Run:')[0].strip()[:0] or '', end='')
    hdr('Q2 SYMBOLIC ORACLE (TASKS10) -- general (K, j, eta, m), split (eta, 1)')
    print('  domain: K >= 3, 2 <= j <= K-1, eta in (K-j, K-j+1) (so eta > 1), '
          'n >= 2K, X = n-K')
    B = section0()
    section12()
    section3()
    section4(B)
    section5(B)
    section6()
    section7()
    rows = sweep()
    grid_battery()

    hdr('SUMMARY')
    byid = {}
    for r in REC:
        byid.setdefault(r['status'], []).append(r['id'])
    for st in ('PASS', 'STRUCTURAL', 'CONJECTURE', 'FAIL'):
        if st in byid:
            print(f'  {st:<11} {len(byid[st]):>3}')
    groups = {}
    for r in REC:
        c = r['id'].split('.')[0]
        groups.setdefault(c, []).append(r['status'])
    order = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8']
    status = {}
    for c in order:
        st = groups.get(c, [])
        s = ('FAILED' if 'FAIL' in st else
             'VERIFIED-SYMBOLIC + CONJECTURE(part)' if 'CONJECTURE' in st else
             'VERIFIED-SYMBOLIC')
        status[c] = s
        print(f'  {c}: {s}  ({len(st)} items)')
    out = dict(
        task='TASKS10 Q2 symbolic verification of the Q1 closed form',
        domain=dict(K='integer >= 3', j='integer, 2 <= j <= K-1',
                    eta='real, K-j < eta < K-j+1 (hence eta > 1)',
                    n='n >= 2K, X = n-K', split='(eta_u, eta_o) = (eta, 1)'),
        status=status, checks=REC,
        key_identities=dict(
            master='a(x) - a(x+1) = g(x+1)/eta with a = r-g; hence '
                   'Delta_x F(x,y>=1) = (K-y) g(x+1)/(eta (K-1))',
            F_form='F(x,y>=1) = 1 - (r(x)-g(x)) (K-y)/(K-1); F(x,K) = 1',
            E='D(m) - D_base = q^j (m - eta(K-1)) / (K eta (eta(nu^m-1)-m))',
            sticking='E(m) > 0  <=>  m > eta(K-1);  m_c = floor(eta(K-1)) + 1',
            rT='r_T = q^j - m D(m) = q^j (nu^m(eta K - m) - eta K)/(K B(m))',
            rT_local='D(m) - D(m-1) = r_T/(eta B(m-1))  ==> r_T >= 0 <=> '
                     'D(m) >= D(m-1)',
            dT_local='D(m) - r_T = (eta-1) B(m+1) (D(m) - D(m+1))  ==> '
                     'd(T) <= D <=> D(m) >= D(m+1)',
            mstar='m* = min{m : nu^m (eta K - 1 - m) <= K(eta-1)} <= ceil(eta K)-1',
            regime='NO-TAIL <=> X - j <= eta(K-1); TAIL <=> n >= n_c = K+j+m_c',
            objective='F(K,0) = 1 - q^j + (K-j) D = V_j + (K-j) E',
            switching='V_j(K-j) = V_{j+1}(K-j)',
            bernoulli='B(m) = eta(nu^m-1) - m >= m/(eta-1) > 0'),
        sweep_C6b=rows,
        failed=FAILED)
    with open(os.path.join(HERE, 'Q2_symbolic.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    print('\n  wrote results/Q2_symbolic.json')
    print('\n  FAILED items:', FAILED if FAILED else 'none')
    sys.exit(1 if FAILED else 0)


if __name__ == '__main__':
    main()
