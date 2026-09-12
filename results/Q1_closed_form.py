"""Q1 (TASKS10): closed form of the relaxed-F hardness LP vertex, with the
finite-n (grid-width) branch.

Interface for Q2
----------------
    build_closed_form() -> dict with sympy expressions (see docstring there).
    instantiate(K, eta, n) -> exact Fraction grids (F, Ghat, G) + parameters.
    lp_value(n, K, eta)    -> LP optimum via the frozen builder N4_relaxF_solve.

Convention: split (eta_u, eta_o) = (eta, 1), balanced region = {y <= tau} with
tau = 1 ('ysmall'), x = |S \\ O| in 0..X, y = |S n O| in 0..K, X = n - K.

WHAT IS CLAIMED (status tags per CLAUDE.md)
-------------------------------------------
[VERIFIED-LP]  For 2 <= j <= K-1 (equivalently eta <= K-1) the value below equals
               the LP optimum at every tested (K, eta, n): 32/32 j>=2 rows of
               results/Q0_extract.py (<= 6.2e-16), 18/18 configurations of
               section A below, and 49/49 points of the n-scan in section E.
[VERIFIED-LP]  The vertex (F, Ghat, G) below coincides *entry by entry* with the
               canonical (min-mass) LP vertex on the tested grids.
[EXACT]        Every LP constraint is verified in exact rational arithmetic.
[CONJECTURE]   m*(K, eta) = ceil(eta K) - 1 (the unconstrained tail length);
               inherited from N4 (264 numerical points), not proved.
[FAILED / open] For j <= 1 (eta > K-1) the formula is only an UPPER bound on the
               LP value; see results/Q1_closed_form.md section 5.

Run:  python3 results/Q1_closed_form.py            (self-checks, ~1 min)
      python3 results/Q1_closed_form.py quick
"""
import json
import math
import os
import sys
from fractions import Fraction as Fr

import numpy as np
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

MMAX = 2000


# =============================================================== exact numbers
def params(K, eta, X=None, mmax=MMAX):
    """Exact parameters of the closed form on a grid of width X = n - K.

    k1 = eta(K-1) + 1,  q = 1 - 1/k1,  nu = eta/(eta-1),  j = K + 1 - ceil(eta),
    D(m) = q^j (nu^m/K - 1) / (eta(nu^m - 1) - m),
    D = max( q^j/(K eta), max_{1 <= m <= X-j} D(m) ),   m = None if the max is
    attained by the first term (then the phase-2 tail never closes inside the
    grid: T = infinity, represented as T = None).
    X = None means the n -> infinity grid (m ranges over all of 1..mmax).
    """
    eta = Fr(eta)
    k1 = eta * (K - 1) + 1
    q = 1 - 1 / k1
    nu = eta / (eta - 1)
    j = max(0, min(K, K + 1 - math.ceil(eta)))
    qj = q ** j
    Dbase = qj / (K * eta)
    mcap = mmax if X is None else min(mmax, X - j)
    D, mstar = Dbase, None
    nup = Fr(1)
    for m in range(1, max(0, mcap) + 1):
        nup *= nu
        den = eta * (nup - 1) - m
        if den <= 0:
            continue
        cand = qj * (nup / K - 1) / den
        if cand > D:
            D, mstar = cand, m
    T = None if mstar is None else j + mstar
    Vj = 1 - qj + (K - j) * Dbase
    return dict(eta=eta, K=K, X=X, k1=k1, q=q, nu=nu, j=j, qj=qj, D=D,
                mstar=mstar, T=T, Dbase=Dbase,
                value=1 - qj + (K - j) * D, Vj=Vj,
                excess=(K - j) * (D - Dbase))


def sequences(P, X):
    """r_x (residual), g_x (o-gain = Delta_y F(x,0)), d_x (b-gain) for x = 0..X."""
    j, D, T, q, nu, eta, K = (P['j'], P['D'], P['T'], P['q'], P['nu'],
                              P['eta'], P['K'])
    qj = P['qj']
    r, g = [], []
    for x in range(X + 2):
        if x <= j:
            r.append(q ** x)
            g.append(q ** x / K)
        elif T is None or x <= T:
            i = x - j
            nui = nu ** i
            r.append(qj - i * D)
            g.append(nui * qj / K - eta * D * (nui - 1))
        else:
            r.append(Fr(0))
            g.append(Fr(0))
    d = [r[x] - r[x + 1] for x in range(X + 1)]
    return r[:X + 1], g[:X + 1], d


def instantiate(K, eta, n, mmax=MMAX):
    """Exact (F, Ghat, G) on the grid of an n-element instance.

    F[x][y], Ghat[s] (s = 0..n), G[x][y]; split (eta_u, eta_o) = (eta, 1), so
    Ghat_{s+1} - Ghat_s = g_s / eta  and  G(x,y) = Ghat_{x+1} + (F(x,y)-F(x,1)).
    """
    X = n - K
    P = params(K, eta, X, mmax)
    eta = P['eta']
    r, g, d = sequences(P, X)
    F = [[None] * (K + 1) for _ in range(X + 1)]
    for x in range(X + 1):
        base = 1 - r[x]
        rest = (r[x] - g[x]) / (K - 1) if K > 1 else Fr(0)
        for y in range(K + 1):
            F[x][y] = base if y == 0 else base + g[x] + (y - 1) * rest
    Ghat = [Fr(0)] * (n + 1)
    for s in range(1, n + 1):
        Ghat[s] = Ghat[s - 1] + (g[s - 1] / eta if s - 1 <= X else Fr(0))
    G = [[None] * (K + 1) for _ in range(X + 1)]
    for x in range(X + 1):
        for y in range(K + 1):
            G[x][y] = Ghat[x + y] if y <= 1 else Ghat[x + 1] + (F[x][y] - F[x][1])
    return dict(P=P, F=F, Ghat=Ghat, G=G, r=r, g=g, d=d, X=X, n=n, K=K)


# ============================================================ sympy interface
def build_closed_form():
    """Symbolic closed form consumed by Q2.

    Returns a dict with keys
      'symbols'   : x, y, s, K, j, eta, n, m, X, q, nu, D, T  (sympy Symbols)
      'F'         : F(x,y)  (Piecewise in x, y)
      'Ghat'      : Ghat(s) (Piecewise in s)         -- balanced value, y <= 1
      'G_unbal'   : G(x,y) for y >= 2
      'aux'       : {'r': r(x), 'g': g(x), 'd': d(x), 'q_expr', 'nu_expr',
                     'D_expr', 'D_base', 'T_expr', 'X_expr', 'j_expr', 'm_rule'}
      'split'     : ('eta', 1)
      'domain'    : assumptions and piece boundaries
      'objective' : F(K,0) in closed form
      'limit'     : n -> infinity limit of the objective (NOT V_j, see notes)
      'Vj'        : V_j(eta) for reference
      'excess'    : limit - V_j
      'notes'     : str
    """
    x, y, s, m = sp.symbols('x y s m', integer=True, nonnegative=True)
    K, j, n, X = sp.symbols('K j n X', integer=True, positive=True)
    eta = sp.Symbol('eta', positive=True)
    q, nu, D, T = sp.symbols('q nu D T', positive=True)

    k1_e = eta * (K - 1) + 1
    q_e = 1 - 1 / k1_e
    nu_e = eta / (eta - 1)
    D_base = q ** j / (K * eta)
    D_e = q ** j * (nu ** m / K - 1) / (eta * (nu ** m - 1) - m)   # closing tail
    T_e = j + m
    X_e = n - K

    # --- residual r(x), o-gain g(x), b-gain d(x) --------------------------
    r = sp.Piecewise((q ** x, x <= j),
                     (q ** j - (x - j) * D, x <= T),
                     (sp.Integer(0), True))
    g = sp.Piecewise((q ** x / K, x <= j),
                     (nu ** (x - j) * q ** j / K - eta * D * (nu ** (x - j) - 1),
                      x <= T),
                     (sp.Integer(0), True))
    rp = r.subs(x, x + 1)
    d = sp.simplify(r - rp) if False else (r - rp)

    # --- F ----------------------------------------------------------------
    F = sp.Piecewise((1 - r, sp.Eq(y, 0)),
                     (1 - r + g + (y - 1) * (r - g) / (K - 1), True))

    # --- Ghat (balanced, depends on |S| = s only) -------------------------
    # phase 1 (s <= j+1):  Ghat_s = k1 (1 - q^s) / (K eta)
    # phase 2 (j+1 <= s <= T+1), M = s - j - 1:
    #   Ghat_s = [ k1 (1 - q^{j+1})/K + eta (q^j/K - eta D)(nu^M - 1) + eta D M ] / eta
    # phase 3 (s > T+1): saturated at the phase-2 value with M = m.
    M = s - j - 1
    ph1 = k1_e * (1 - q ** s) / (K * eta)
    ph2core = (k1_e * (1 - q ** (j + 1)) / K
               + eta * (q ** j / K - eta * D) * (nu ** M - 1) + eta * D * M) / eta
    ph3 = ph2core.subs(s, T + 1)
    Ghat = sp.Piecewise((ph1, s <= j + 1), (ph2core, s <= T + 1), (ph3, True))

    G_unbal = Ghat.subs(s, x + 1) + (F - F.subs(y, 1))   # y >= 2, eta_o = 1

    obj = 1 - q ** j + (K - j) * D                       # F(K,0), needs j < K <= T
    Vj_e = 1 - q ** j * (1 - (K - j) / (K * eta))
    limit = obj                                          # with D at m = m*
    excess = (K - j) * (D - D_base)

    domain = dict(
        K='K >= 2, integer',
        j='j = K + 1 - ceil(eta); 0 <= j <= K; the formula is LP-exact only for j >= 2',
        eta='eta in (K-j, K-j+1]; eta > 1',
        n='n >= 2K; grid width X = n - K',
        m=('m = tail length. m = min(m*, X - j) with m* = ceil(eta K) - 1 '
           '[CONJECTURE], and m is dropped entirely (D = D_base = q^j/(K eta), '
           'T = +infinity, no closing step) whenever max_{1<=mm<=X-j} D(mm) '
           '<= D_base, which happens exactly when X < K + something ~ eta K; '
           'see params() for the exact rule.'),
        pieces=('x-pieces: [0, j] geometric; (j, T] constant-d tail; (T, X] '
                'saturated (F == 1). y-pieces: y = 0; y >= 1 linear in y.'),
        q='q = (K-1) eta / ((K-1) eta + 1) = 1 - 1/k1',
        nu='nu = eta/(eta-1)',
        split='(eta_u, eta_o) = (eta, 1); any split with eta_u eta_o = eta '
              'rescales Ghat and G by a constant and leaves F unchanged.',
    )
    notes = (
        "1) The n -> infinity limit of the LP value is NOT V_j(eta): it is "
        "V_j + (K-j)(D - q^j/(K eta)) with D > q^j/(K eta) strictly (N4's excess "
        "term, reproduced here). V_j is attained exactly on the FINITE window "
        "X = n-K <= (largest m with D(m) <= q^j/(K eta)) + j, i.e. n = O((eta+2)K). "
        "So TASKS10 target (c) as written (rho_K^{(n)} -> min_j V_j) is "
        "contradicted by the data; rho_K^{(n)} is nondecreasing in n. "
        "2) At n = 2K the LP value equals min_j V_j(eta) exactly (13/13 tested "
        "(K,eta) pairs), matching the N2 instance family. "
        "3) For j <= 1 (eta > K-1) the closed form is feasible but NOT optimal: "
        "the LP value is strictly smaller; the excess-generating chain is "
        "partially blocked. Q2 should restrict to j >= 2. "
        "4) Edges Q2 must check: x = j (phase-1/phase-2 junction), x = T "
        "(closing step, g_T = r_T), x = T+1 (saturation), y = 0/1 junction, "
        "the y = 1 -> y = 2 band edges (unbalanced G rule) and the long-range "
        "chain family L of N4 section 4.1. "
        "5) m* = ceil(eta K) - 1 is [CONJECTURE] (numerics only)."
    )
    return dict(
        symbols=dict(x=x, y=y, s=s, K=K, j=j, eta=eta, n=n, m=m, X=X,
                     q=q, nu=nu, D=D, T=T),
        F=F, Ghat=Ghat, G_unbal=G_unbal,
        aux=dict(r=r, g=g, d=d, q_expr=q_e, nu_expr=nu_e, k1_expr=k1_e,
                 D_expr=D_e, D_base=D_base, T_expr=T_e, X_expr=X_e,
                 j_expr=K + 1 - sp.ceiling(eta),
                 m_rule='m = min(ceil(eta*K) - 1, X - j) when that maximises D, '
                        'else no tail closing (D = D_base, T = oo)'),
        split=('eta', 1),
        domain=domain,
        objective=obj, limit=limit, Vj=Vj_e, excess=excess, notes=notes)


# ============================================================ exact feasibility
def check_exact(K, eta, n, tol_tag='exact'):
    """Exact rational check of every LP constraint on the closed-form point."""
    sol = instantiate(K, eta, n)
    F, G, Ghat, X = sol['F'], sol['G'], sol['Ghat'], sol['X']
    eta = Fr(eta)
    bad = []
    for x in range(X + 1):
        for y in range(K + 1):
            for dx, dy in ((1, 0), (0, 1)):
                if x + dx > X or y + dy > K:
                    continue
                dF = F[x + dx][y + dy] - F[x][y]
                dG = G[x + dx][y + dy] - G[x][y]
                if dF < 0:
                    bad.append(('mono', x, y, dx, dy, str(dF)))
                if dG > dF:                      # band_up, eta_o = 1
                    bad.append(('band_up', x, y, dx, dy, str(dF - dG)))
                if dF / eta > dG:                # band_lo, eta_u = eta
                    bad.append(('band_lo', x, y, dx, dy, str(dG - dF / eta)))
                for sx, sy in ((1, 0), (0, 1)):
                    if x + dx + sx > X or y + dy + sy > K:
                        continue
                    lhs = F[x + dx + sx][y + dy + sy] - F[x + sx][y + sy]
                    if lhs > dF:
                        bad.append((f'submod_{dx}{dy}{sx}{sy}', x, y, sx, sy,
                                    str(dF - lhs)))
    for x in range(X + 1):
        for y in range(K + 1):
            if 0 < x + y <= K and not (x == 0 and y == K) and F[x][y] > 1:
                bad.append(('opt_norm', x, y, 0, 0, str(1 - F[x][y])))
            if y <= 1 and G[x][y] != Ghat[x + y]:
                bad.append(('O_indep', x, y, 0, 0, 'mismatch'))
    if F[0][0] != 0:
        bad.append(('eq_F00', 0, 0, 0, 0, str(F[0][0])))
    if F[0][K] != 1:
        bad.append(('eq_F0K', 0, K, 0, 0, str(F[0][K] - 1)))
    if Ghat[0] != 0:
        bad.append(('eq_Ghat0', 0, 0, 0, 0, str(Ghat[0])))
    return sol, bad


def lp_value(n, K, eta, tau=1, defn='ysmall'):
    import N4_relaxF_solve as S
    from scipy.optimize import linprog
    from scipy.sparse import coo_matrix
    M = S.build(n, K, float(eta), tau, defn, split='eta1')
    R, C, V, b = M['A']
    A_ub = coo_matrix((V, (R, C)), shape=(M['nrows'], M['nv'])).tocsr()
    eR, eC, eV, eb = [], [], [], []
    for i, (coefs, rhs) in enumerate(M['eqs']):
        for c, v in coefs:
            eR.append(i); eC.append(c); eV.append(v)
        eb.append(rhs)
    A_eq = coo_matrix((eV, (eR, eC)), shape=(len(M['eqs']), M['nv'])).tocsr()
    obj = np.zeros(M['nv']); obj[M['fid'](K, 0)] = 1.0
    out = linprog(obj, A_ub=A_ub, b_ub=np.array(b), A_eq=A_eq, b_eq=np.array(eb),
                  bounds=[(None, None)] * M['nv'], method='highs')
    assert out.status == 0, out.message
    return float(out.fun)


def sympy_vs_exact(K, eta, n):
    """Evaluate the sympy Piecewise expressions at every grid point and compare
    with the Fraction implementation (guards against a transcription slip)."""
    B = build_closed_form()
    S_ = B['symbols']
    P = params(K, eta, n - K)
    sub = {S_['K']: K, S_['j']: P['j'], S_['eta']: sp.Rational(Fr(eta)),
           S_['q']: sp.Rational(P['q']), S_['nu']: sp.Rational(P['nu']),
           S_['D']: sp.Rational(P['D']),
           S_['T']: (sp.Integer(P['T']) if P['T'] is not None
                     else sp.Integer(10 ** 6))}
    sol = instantiate(K, eta, n)
    X = sol['X']
    Fe = B['F'].subs(sub)
    Ge = B['Ghat'].subs(sub)
    Ue = B['G_unbal'].subs(sub)
    def _fr(expr):
        expr = sp.together(sp.expand(expr))
        r = sp.Rational(expr)
        return Fr(int(r.p), int(r.q))

    worst = Fr(0)
    for x in range(X + 1):
        for y in range(K + 1):
            worst = max(worst, abs(_fr(Fe.subs({S_['x']: x, S_['y']: y}))
                                   - sol['F'][x][y]))
            if y >= 2:
                worst = max(worst, abs(_fr(Ue.subs({S_['x']: x, S_['y']: y}))
                                       - sol['G'][x][y]))
    for s in range(0, X + 2):
        worst = max(worst, abs(_fr(Ge.subs({S_['s']: s})) - sol['Ghat'][s]))
    return worst


# ====================================================================== main
def main(quick=False):
    out = {'feasibility': [], 'value_vs_lp': [], 'vertex_match': [],
           'sympy_match': []}
    cfgs = [(3, Fr(2), 24)] if quick else [
        (3, Fr(3, 2), 6), (3, Fr(3, 2), 12), (3, Fr(3, 2), 24), (3, Fr(3, 2), 48),
        (3, Fr(19, 10), 24), (3, Fr(2), 24), (3, Fr(2), 12), (3, Fr(2), 6),
        (4, Fr(3, 2), 32), (4, Fr(19, 10), 32), (4, Fr(2), 32), (4, Fr(5, 2), 32),
        (4, Fr(5, 2), 8), (4, Fr(5, 2), 16), (5, Fr(19, 10), 40), (5, Fr(5, 2), 40),
        (5, Fr(7, 2), 20), (5, Fr(7, 2), 40),
        (3, Fr(5, 2), 24), (4, Fr(7, 2), 32),          # j <= 1: expected FAIL
    ]
    print('=' * 108)
    print('A. exact feasibility + value vs LP   (split (eta,1), balanced y<=1, tau=1)')
    print('=' * 108)
    print(f"{'K':>2} {'eta':>6} {'n':>4} {'j':>2} {'m':>4} {'T':>5} {'feas':>5} "
          f"{'closed form':>14} {'LP':>14} {'diff':>11} {'V_j':>14} {'note':>10}")
    npass = nfail = 0
    for K, eta, n in cfgs:
        sol, bad = check_exact(K, eta, n)
        P = sol['P']
        v = float(P['value'])
        vlp = lp_value(n, K, eta)
        ok = (not bad) and abs(v - vlp) < 1e-9
        note = '' if P['j'] >= 2 else 'j<=1 open'
        if P['j'] >= 2:
            npass += ok
            nfail += (not ok)
        print(f"{K:>2} {str(eta):>6} {n:>4} {P['j']:>2} {str(P['mstar']):>4} "
              f"{str(P['T']):>5} {'OK' if not bad else 'BAD':>5} {v:>14.10f} "
              f"{vlp:>14.10f} {v - vlp:>+11.2e} {float(P['Vj']):>14.10f} {note:>10}")
        out['feasibility'].append(dict(K=K, eta=str(eta), n=n, j=P['j'],
                                       mstar=P['mstar'], T=P['T'],
                                       violations=bad[:20], nviol=len(bad),
                                       value=v, lp=vlp, diff=v - vlp,
                                       Vj=float(P['Vj'])))
    print(f'\n  j>=2 configurations: {npass} PASS / {nfail} FAIL')

    print('\n' + '=' * 108)
    print('B. entrywise match against the canonical LP vertex (K=3,4, n=8K)')
    print('=' * 108)
    try:
        J = json.load(open(os.path.join(HERE, 'Q0_vertex_tables.json')))
        for key, d in J['data'].items():
            K = d['config']['K']; n = d['config']['n']; eta = Fr(d['config']['eta'])
            if n != 8 * K or K not in (3, 4):
                continue
            sol = instantiate(K, eta, n)
            Flp = np.array(d['F']); Ghlp = np.array(d['Ghat']); Glp = np.array(d['G'])
            X = sol['X']
            dF = max(abs(float(sol['F'][x][y]) - Flp[x, y])
                     for x in range(X + 1) for y in range(K + 1))
            dG = max(abs(float(sol['G'][x][y]) - Glp[x, y])
                     for x in range(X + 1) for y in range(K + 1))
            dGh = max(abs(float(sol['Ghat'][s]) - Ghlp[s]) for s in range(X + 2))
            print(f"  {key:<22} j={sol['P']['j']} maxdiff F={dF:.2e} "
                  f"Ghat={dGh:.2e} G={dG:.2e}")
            out['vertex_match'].append(dict(key=key, j=sol['P']['j'], dF=dF,
                                            dGhat=dGh, dG=dG))
    except FileNotFoundError:
        print('  (results/Q0_vertex_tables.json missing; run Q0_extract.py first)')

    print('\n' + '=' * 108)
    print('C. sympy Piecewise vs Fraction implementation (transcription guard)')
    print('=' * 108)
    for K, eta, n in ([(3, Fr(2), 24)] if quick else
                      [(3, Fr(2), 24), (3, Fr(3, 2), 12), (4, Fr(5, 2), 16)]):
        w = sympy_vs_exact(K, eta, n)
        print(f'  K={K} eta={eta} n={n}: max |sympy - Fraction| = {w}')
        out['sympy_match'].append(dict(K=K, eta=str(eta), n=n, maxdiff=str(w)))

    print('\n' + '=' * 108)
    print('D. minimal self-check requested by the task: K=3, eta=2, n=24')
    print('=' * 108)
    sol, bad = check_exact(3, Fr(2), 24)
    P = sol['P']
    vlp = lp_value(24, 3, Fr(2))
    print(f"  j = {P['j']} (the task asked for j=1; with K=3, eta=2 the segment "
          f"index is j = K+1-ceil(eta) = 2, and eta=2 is the right endpoint of "
          f"segment [K-j, K-j+1] = [1,2]).")
    print(f"  closed form F(K,0) = {P['value']} = {float(P['value']):.12f}")
    print(f"  LP optimum          = {vlp:.12f}   diff = {float(P['value']) - vlp:+.2e}")
    print(f"  V_j                 = {P['Vj']} = {float(P['Vj']):.12f}")
    print(f"  excess              = {P['excess']} = {float(P['excess']):.3e}")
    print(f"  exact feasibility violations: {len(bad)}")
    print(f"  spot values: F(1,0)={sol['F'][1][0]}, F(2,1)={sol['F'][2][1]}, "
          f"Ghat_3={sol['Ghat'][3]}, G(2,2)={sol['G'][2][2]}")
    print('\n' + '=' * 108)
    print('E. n-scan: the finite-grid law across the whole transition window')
    print('=' * 108)
    scan = []
    scfg = [(3, Fr(2))] if quick else [(3, Fr(3, 2)), (3, Fr(2)), (4, Fr(2)),
                                       (4, Fr(5, 2)), (5, Fr(7, 2))]
    nbad = 0
    for K, eta in scfg:
        Plim = params(K, eta, None)
        for n in range(2 * K, K + Plim['T'] + 3):
            Pn = params(K, eta, n - K)
            v, vlp = float(Pn['value']), lp_value(n, K, eta)
            ok = abs(v - vlp) < 1e-9
            nbad += (not ok)
            scan.append(dict(K=K, eta=str(eta), n=n, X=n - K, m=Pn['mstar'],
                             value=v, lp=vlp, diff=v - vlp, ok=ok))
    print(f'  {len(scan)} (K, eta, n) points scanned, mismatches: {nbad}')
    jumpn = {}
    for rec in scan:
        k = (rec['K'], rec['eta'])
        if rec['m'] is not None and k not in jumpn:
            jumpn[k] = rec['n']
    for k, v in jumpn.items():
        K, eta = k
        Plim = params(K, Fr(eta), None)
        print(f'  K={K} eta={eta}: value leaves V_j at n = {v}, saturates at '
              f"n = {K + Plim['T']} (= K + j + m*)")
    out['n_scan'] = scan

    print('\n' + '=' * 108)
    print('F. invariant  sum_x g_x = k1/K   (so Ghat saturates at k1/(K eta))')
    print('=' * 108)
    inv = []
    for K, eta in [(3, Fr(3, 2)), (3, Fr(2)), (4, Fr(2)), (4, Fr(5, 2)),
                   (5, Fr(19, 10)), (5, Fr(7, 2)), (6, Fr(3, 2)), (4, Fr(7, 2))]:
        Pl = params(K, eta, None)
        sl = instantiate(K, eta, K + Pl['T'] + 3)
        tot = sum(sl['g'])
        ok = (tot == Pl['k1'] / K) and (sl['Ghat'][-1] == Pl['k1'] / (K * eta))
        inv.append(dict(K=K, eta=str(eta), sum_g=str(tot),
                        k1_over_K=str(Pl['k1'] / K), ok=ok))
        print(f"  K={K} eta={eta}: sum g = {tot} , k1/K = {Pl['k1'] / K} , "
              f"Ghat_sat = {sl['Ghat'][-1]} -> {'OK' if ok else 'FAIL'}")
    out['invariant_sum_g'] = inv

    print('\n' + '=' * 108)
    print('G. symbolic sanity of the exported expressions (sympy)')
    print('=' * 108)
    B = build_closed_form()
    Sy = B['symbols']
    chk1 = sp.simplify(B['objective'].subs(Sy['D'], B['aux']['D_base']) - B['Vj'])
    t = sp.Symbol('t', positive=True)
    Dm = B['aux']['D_expr']
    lim = sp.limit(Dm.subs(Sy['nu'] ** Sy['m'], t)
                   .subs(Sy['m'], sp.log(t) / sp.log(Sy['nu'])), t, sp.oo)
    chk2 = sp.simplify(lim - B['aux']['D_base'])
    print(f'  objective(D = D_base) - V_j  = {chk1}   (must be 0)')
    print(f'  lim_(m->oo) D(m) - D_base    = {chk2}   (must be 0)')
    out['symbolic_sanity'] = dict(obj_at_Dbase_minus_Vj=str(chk1),
                                  limit_Dm_minus_Dbase=str(chk2))

    out['self_check'] = dict(K=3, eta='2', n=24, j=P['j'], value=str(P['value']),
                             lp=vlp, Vj=str(P['Vj']), excess=str(P['excess']),
                             nviol=len(bad))
    with open(os.path.join(HERE, 'Q1_selfcheck.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    print('\nwrote results/Q1_selfcheck.json')


if __name__ == '__main__':
    main(quick=(len(sys.argv) > 1 and sys.argv[1] == 'quick'))
