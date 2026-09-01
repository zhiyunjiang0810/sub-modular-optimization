"""F2.1: the (K, eta) = (5, 4) anomaly of the relaxed-F hardness LP, in exact arithmetic.

BACKGROUND
----------
results/N4_hardness_construction.md reports that the closed-form construction of
N4 reproduces the optimum of the relaxed-F LP at every tested (K, eta) with
eta <= K-1, with ONE exception: at (K, eta) = (5, 4) the construction value is
3.2e-7 ABOVE the HiGHS optimum.  Since the LP is a minimisation, the closed form
is then not optimal there (or HiGHS is wrong).  This script decides which.

WHY EXACT ARITHMETIC IS AVAILABLE HERE
--------------------------------------
eta = 4 is rational and sqrt(eta) = 2 is an exact binary float, so every entry of
the LP matrix built by results/N4_relaxF_solve.py::build is one of
{-2, -1, -1/2, 1/2, 1, 2} and every right-hand side is 0 or 1.  Every IEEE double
is itself a dyadic rational, so Fraction(x) is an exact, lossless reading of any
float vector: residuals of a float solution can be evaluated with ZERO rounding.

WHAT IS PROVED HERE (section C)
-------------------------------
An explicit rational point x* of the (5,4) LP is exhibited and verified in exact
Fraction arithmetic to satisfy EVERY inequality (with slack >= 1e-9), every
equality (exactly), and every sign bound, while its objective is strictly below
the closed-form construction value.  A feasible point of a minimisation LP whose
objective beats a candidate proves the candidate is not optimal.  No trust in
HiGHS is required for that conclusion: HiGHS is used only to propose x*, and the
proposal is then checked exactly.

The point x* is produced by solving the LP with every inequality right-hand side
tightened by eps = 1e-9 and with HiGHS' primal feasibility tolerance forced to
1e-10 < eps, so that the returned float vector is exactly feasible for the
ORIGINAL LP with slack about eps.  (With the default tolerance 1e-7 > eps the
returned vector still violates a handful of constraints at the 1e-15 level and
the certificate fails; the script reports that control too.)

MECHANISM (section D)
---------------------
The construction of N4 satisfies F(x, K) = 1 for every x, i.e. the true function
saturates at the OPT value as soon as all K elements of O are in the set.  The LP
does not require this: the normalisation F <= 1 is imposed only on sets of size
<= K, and monotonicity only forces F(x, K) >= F(0, K) = 1.  Adding either
    F(x, K) = 1  for all x      or      F(x, 0) <= 1  for all x
to the LP raises its optimum to the closed-form value exactly, at (5,4) and
everywhere else.  The unconstrained (5,4) optimum uses F(x, K) = 1 + x*eps with
eps ~ 1.76e-4 > 0, which the construction forbids.

Run:  python3 results/F2_54_exact.py           (sections A-D + local eta scan)
      python3 results/F2_54_exact.py full      (adds the K = 3..8 grid scan)
"""
import json
import os
import sys
import warnings
from fractions import Fraction as Fr

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import N4_relaxF_solve as S   # noqa: E402  (frozen LP builder)
import N4_check as C          # noqa: E402  (frozen closed form, exact Fractions)

K0, ETA0 = 5, Fr(4)
OUT = {}


# --------------------------------------------------------------- LP plumbing
def pieces(K, eta, X, extra_eq=None, extra_ub=None):
    """Return (M, A_ub, b_ub, A_eq, b_eq, obj, bounds) for the ysmall(tau=1) LP."""
    n = X + K
    M = S.build(n, K, float(eta), 1, 'ysmall')
    R, Cc, V, b = M['A']
    R, Cc, V, b = list(R), list(Cc), list(V), list(b)
    nr = M['nrows']
    for coefs, rhs in (extra_ub or []):
        for c, v in coefs:
            R.append(nr); Cc.append(c); V.append(v)
        b.append(rhs); nr += 1
    A_ub = coo_matrix((V, (R, Cc)), shape=(nr, M['nv'])).tocsr()
    eqs = list(M['eqs']) + list(extra_eq or [])
    eR, eC, eV, eb = [], [], [], []
    for i, (coefs, rhs) in enumerate(eqs):
        for c, v in coefs:
            eR.append(i); eC.append(c); eV.append(v)
        eb.append(rhs)
    A_eq = coo_matrix((eV, (eR, eC)), shape=(len(eqs), M['nv'])).tocsr()
    obj = np.zeros(M['nv']); obj[M['fid'](K, 0)] = 1.0
    bnds = [(None, None)] * M['nF'] + [(0, None)] * (M['nv'] - M['nF'])
    return M, A_ub, np.array(b), A_eq, np.array(eb), obj, bnds, eqs


def solve(K, eta, X, extra_eq=None, extra_ub=None, eps=0.0, tol=None):
    M, A, b, Aeq, beq, obj, bnds, eqs = pieces(K, eta, X, extra_eq, extra_ub)
    opts = {} if tol is None else dict(primal_feasibility_tolerance=tol,
                                       dual_feasibility_tolerance=tol)
    o = linprog(obj, A_ub=A, b_ub=b - eps, A_eq=Aeq, b_eq=beq, bounds=bnds,
                method='highs', options=opts)
    assert o.status == 0, o.message
    return o, M


def exact_audit(M, x_float, K):
    """Exact Fraction audit of a float vector against the ORIGINAL LP."""
    R, Cc, V, b = M['A']
    rows = {}
    for r_, c_, v_ in zip(R, Cc, V):
        rows.setdefault(r_, []).append((c_, Fr(v_)))
    x = [Fr(v) for v in x_float]
    worst = None; nviol = 0
    for r_, terms in rows.items():
        s = sum(v * x[c] for c, v in terms) - Fr(b[r_])
        if s > 0:
            nviol += 1
        if worst is None or s > worst:
            worst = s
    eq_ok = all(sum(Fr(v) * x[c] for c, v in coefs) == Fr(rhs)
                for coefs, rhs in M['eqs'])
    neg = sum(1 for i in range(M['nF'], M['nv']) if x[i] < 0)
    return dict(n_violations=nviol, worst_residual=worst, eq_exact=eq_ok,
                n_negative_G=neg, objective=x[M['fid'](K, 0)])


def line(s=''):
    print(s, flush=True)


# ------------------------------------------------------------------ sections
def section_A():
    line('=' * 88)
    line('A. the closed-form construction at (K, eta) = (5, 4), exact rationals')
    line('=' * 88)
    P = C.params(K0, ETA0)
    X = max(4 * K0, P['T'] + K0 + 5)
    _, F, bad = C.check_exact(K0, ETA0, X)
    line(f"  q = {P['q']}   j = {P['j']}   m* = {P['mstar']}   T = {P['T']}   D = {P['D']}")
    line(f"  exact feasibility of the construction (grid X = {X}): "
         f"{len(bad)} violations")
    line(f"  construction value = {P['value']}")
    line(f"                     = {float(P['value']):.18f}")
    line(f"  V_j (R10 reduced-LP closed form) = {P['Vj']} = {float(P['Vj']):.18f}")
    OUT['A'] = dict(q=str(P['q']), j=P['j'], mstar=P['mstar'], T=P['T'],
                    D=str(P['D']), value=str(P['value']),
                    value_float=float(P['value']), Vj=str(P['Vj']),
                    construction_violations=len(bad), X=X)
    return P


def section_B(P):
    line()
    line('=' * 88)
    line('B. the HiGHS optimum at (5,4): stable in n, in method and in tolerance')
    line('=' * 88)
    rows = []
    line(f"  {'X':>4} {'n':>4}  {'LP optimum':>20}   {'construction - LP':>18}")
    for X in [12, 16, 20, 21, 22, 24, 28, 31, 40]:
        o, _ = solve(K0, ETA0, X)
        rows.append(dict(X=X, n=X + K0, value=float(o.fun)))
        line(f"  {X:4d} {X + K0:4d}  {o.fun:20.15f}   {float(P['value']) - o.fun:18.3e}")
    line("  (X = 22 is the first grid wide enough to hold the length-T tail, T = 21)")
    X = 22
    meth = []
    for m, opt in [('highs', {}), ('highs-ds', {}), ('highs-ipm', {}),
                   ('highs', dict(presolve=False)),
                   ('highs', dict(primal_feasibility_tolerance=1e-10,
                                  dual_feasibility_tolerance=1e-10))]:
        M, A, b, Aeq, beq, obj, bnds, _ = pieces(K0, ETA0, X)
        o = linprog(obj, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq, bounds=bnds,
                    method=m, options=opt)
        res = float((A @ o.x - b).max())
        meth.append(dict(method=m, options=str(opt), value=float(o.fun), max_resid=res))
        line(f"  {m:>10} {str(opt):<62} {o.fun:.15f}  max float residual {res:.2e}")
    OUT['B'] = dict(n_sweep=rows, methods=meth)


def section_C(P):
    line()
    line('=' * 88)
    line('C. EXACT certificate: a rational feasible point that beats the construction')
    line('=' * 88)
    X = 22
    line(f"  {'eps':>8} {'primal tol':>11} {'exact max residual':>19} {'#viol':>6} "
         f"{'eq exact':>9} {'#G<0':>5}  {'exact objective':>19}  beats?")
    best = None
    trials = []
    for eps, tol in [(0.0, None), (1e-9, None), (1e-9, 1e-10), (3e-9, 1e-10),
                     (1e-8, 1e-10), (1e-7, 1e-10)]:
        o, M = solve(K0, ETA0, X, eps=eps, tol=tol)
        a = exact_audit(M, o.x, K0)
        feas = a['n_violations'] == 0 and a['eq_exact'] and a['n_negative_G'] == 0
        beats = a['objective'] < P['value']
        line(f"  {eps:8.1e} {str(tol):>11} {float(a['worst_residual']):19.3e} "
             f"{a['n_violations']:6d} {str(a['eq_exact']):>9} {a['n_negative_G']:5d}  "
             f"{float(a['objective']):19.15f}  "
             f"{'YES' if (feas and beats) else ('no' if feas else 'not exactly feasible')}")
        trials.append(dict(eps=eps, tol=tol, n_violations=a['n_violations'],
                           worst_residual=float(a['worst_residual']),
                           eq_exact=a['eq_exact'], n_negative_G=a['n_negative_G'],
                           objective=float(a['objective']),
                           exactly_feasible=feas, beats_construction=beats))
        if feas and beats and (best is None or a['objective'] < best[1]['objective']):
            best = (dict(eps=eps, tol=tol), a)
    line()
    if best is None:
        line('  NO exact certificate found -> verdict undecided by this route')
        OUT['C'] = dict(trials=trials, certificate=None)
        return None
    cfg, a = best
    gap = P['value'] - a['objective']
    line(f"  CERTIFICATE (eps = {cfg['eps']:.0e}, primal tol = {cfg['tol']:.0e}):")
    line(f"    every inequality holds with slack >= {-float(a['worst_residual']):.1e} "
         f"(exact Fraction arithmetic, 0 violations)")
    line(f"    every equality holds exactly; all predictor variables >= 0")
    line(f"    exact objective  = {float(a['objective']):.18f}")
    line(f"    construction     = {float(P['value']):.18f}")
    line(f"    construction - certificate = {float(gap):.6e}  > 0")
    line(f"    (the certificate is a dyadic rational; its objective has a "
         f"{len(str(a['objective'].denominator))}-digit denominator)")
    line()
    line('  VERDICT: REAL DIFFERENCE.  The N4 closed form is NOT optimal at (5,4);')
    line('           HiGHS is not at fault (its answer is even slightly lower still).')
    OUT['C'] = dict(trials=trials, certificate=dict(
        eps=cfg['eps'], tol=cfg['tol'], objective=float(a['objective']),
        objective_num=str(a['objective'].numerator),
        objective_den=str(a['objective'].denominator),
        construction=float(P['value']), gap=float(gap),
        min_slack=-float(a['worst_residual'])))
    return a


def section_D(P):
    line()
    line('=' * 88)
    line('D. mechanism: the construction over-imposes F(x,K) = 1')
    line('=' * 88)
    X = 22
    o, M = solve(K0, ETA0, X)
    F = o.x[:M['nF']].reshape(X + 1, K0 + 1)
    line('  optimal LP solution, x-slice profile (r_x = 1 - F(x,0), g_x = F(x,1) - F(x,0)):')
    line(f"    {'x':>3} {'r_x (LP)':>14} {'r_x (constr)':>14} {'g_x (LP)':>14} "
         f"{'g_x (constr)':>14} {'F(x,K) - 1':>12}")
    _, rc, gc, dc = C.sequences(K0, ETA0, X)
    for x in [0, 1, 2, 3, 5, 10, 15, 20, 21, 22]:
        line(f"    {x:3d} {1 - F[x, 0]:14.10f} {float(rc[x]):14.10f} "
             f"{F[x, 1] - F[x, 0]:14.10f} {float(gc[x]):14.10f} {F[x, K0] - 1:12.3e}")
    eps_lp = F[1, K0] - 1
    line(f"  F(x,K) - 1 is linear in x with slope {eps_lp:.6e} "
         f"(construction: identically 0)")
    fid = M['fid']
    tests = [('base LP (no extra constraint)', None, None),
             ('+ F(x,K) = 1 for all x',
              [([(fid(x, K0), 1.0)], 1.0) for x in range(1, X + 1)], None),
             ('+ F(x,0) <= 1 for all x', None,
              [([(fid(x, 0), 1.0)], 1.0) for x in range(X + 1)]),
             ('+ both', [([(fid(x, K0), 1.0)], 1.0) for x in range(1, X + 1)],
              [([(fid(x, 0), 1.0)], 1.0) for x in range(X + 1)])]
    line()
    line(f"  {'variant':<34} {'LP optimum':>18} {'minus construction':>19}")
    res = []
    for name, eq, ub in tests:
        oo, _ = solve(K0, ETA0, X, extra_eq=eq, extra_ub=ub)
        line(f"  {name:<34} {oo.fun:18.15f} {oo.fun - float(P['value']):19.2e}")
        res.append(dict(variant=name, value=float(oo.fun),
                        minus_construction=float(oo.fun) - float(P['value'])))
    line()
    line('  Reading: the normalisation of the LP is  F <= 1 on sets of size <= K only,')
    line('  and monotonicity forces F(x,K) >= F(0,K) = 1.  The construction picks the')
    line('  boundary F(x,K) = 1 (equivalently F(x,0) <= 1 for every x, i.e. the residual')
    line('  chain closes at r_T = 0).  At (5,4) the optimum instead lets the true')
    line('  function keep a constant gain in the B direction after O is covered.')
    OUT['D'] = dict(eps_slope=float(eps_lp), variants=res)


def section_E(full):
    line()
    line('=' * 88)
    line('E. how isolated is (5,4)?  construction - LP over a (K, eta) grid, eta <= K-1')
    line('=' * 88)
    etas = [Fr(5, 4), Fr(3, 2), Fr(7, 4), Fr(2), Fr(9, 4), Fr(5, 2), Fr(11, 4),
            Fr(3), Fr(7, 2), Fr(15, 4), Fr(4), Fr(17, 4), Fr(9, 2), Fr(5),
            Fr(6), Fr(7)]
    Ks = range(3, 9) if full else range(3, 7)
    line(f"  {'K':>3} {'eta':>6} {'j':>3} {'m*':>4} {'construction':>18} "
         f"{'LP':>18} {'diff':>10}")
    grid = []
    for K in Ks:
        for eta in etas:
            if eta > K - 1:
                continue
            P = C.params(K, eta)
            X = max(4 * K, P['T'] + K + 5)
            o, _ = solve(K, eta, X)
            d = float(P['value']) - o.fun
            flag = '   <== ANOMALY' if d > 1e-9 else ''
            line(f"  {K:3d} {str(eta):>6} {P['j']:3d} {str(P['mstar']):>4} "
                 f"{float(P['value']):18.12f} {o.fun:18.12f} {d:10.2e}{flag}")
            grid.append(dict(K=K, eta=str(eta), construction=float(P['value']),
                             lp=float(o.fun), diff=d))
    line()
    line('  local scan in eta at K = 5 (eta > K-1 = 4 is the already documented regime')
    line('  where the closed form is only an upper bound):')
    line(f"  {'eta':>8} {'j':>3} {'construction':>16} {'LP':>16} {'diff':>10} "
         f"{'F(1,K)-1':>11}")
    loc = []
    for eta in [Fr(19, 5), Fr(39, 10), Fr(79, 20), Fr(399, 100), Fr(4),
                Fr(401, 100), Fr(81, 20), Fr(21, 5)]:
        P = C.params(5, eta)
        X = max(20, P['T'] + 10)
        o, M = solve(5, eta, X)
        F = o.x[:M['nF']].reshape(X + 1, 6)
        d = float(P['value']) - o.fun
        line(f"  {str(eta):>8} {P['j']:3d} {float(P['value']):16.12f} {o.fun:16.12f} "
             f"{d:10.2e} {F[1, 5] - 1:11.3e}"
             f"{'   (eta > K-1)' if eta > 4 else ''}")
        loc.append(dict(eta=str(eta), j=P['j'], construction=float(P['value']),
                        lp=float(o.fun), diff=d, F1K_minus_1=float(F[1, 5] - 1)))
    OUT['E'] = dict(grid=grid, local_eta_scan=loc, full=full)


def main():
    full = 'full' in sys.argv
    P = section_A()
    section_B(P)
    cert = section_C(P)
    section_D(P)
    section_E(full)
    with open(os.path.join(HERE, 'F2_54_exact.json'), 'w') as fh:
        json.dump(OUT, fh, indent=1)
    line()
    line('wrote results/F2_54_exact.json')
    return 0 if cert is not None else 1


if __name__ == '__main__':
    sys.exit(main())
