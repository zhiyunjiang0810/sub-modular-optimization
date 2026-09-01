"""F3: does the N4 explicit (F, G) survive the TRUE balanced band?

CONTEXT
-------
RESEARCH_STATE.md R11(b): the R9 candidate (F = eta_o^{-1}(1 - a^x(1 - y/K)),
Ghat_s = 1 - a^s) is infeasible for EVERY delta once "balanced" is taken to be
the true concentration band  |y - K|S|/n| <= tau  instead of  y <= tau.  The
structural certificate there is: F is flat in x along y = K while Ghat keeps
increasing, so band_up forces Delta Ghat <= 0 and band_lo forces it > 0.

results/N4_hardness_construction.md gives a DIFFERENT, explicit (F, G) --
the optimizer of the same LP under the  y <= tau  definition -- for which
F(x,K) == 1 as well.  Question F3(a): does the same flatness certificate kill
it?  Answer produced by this script: NO for the reason R11(b) gives (N4's Ghat
SATURATES, so Delta Ghat = 0 there too), but YES for a new reason, see below.

WHAT IS COMPUTED
----------------
Eight sections, all on the (x, y) grid, x = |S \\ O| in 0..n-K, y = |S cap O| in 0..K.
Everything is in the SCALED predictor  Gs := sqrt(eta) * G  of results/N4_check.py,
so with an inflation factor c = sqrt(1 + delta) the single-element band
    Delta F/(eta_u c) <= Delta G <= eta_o c Delta F      (eta_u = eta_o = sqrt(eta))
becomes
    Delta F / c <= Delta Gs <= eta c Delta F.

  A  fixedFG : N4's F AND G verbatim.  (a) leakage test: on the balanced region
               is G a function of |S| only (i.e. constant on each level
               s = x + y)?  (b) band test: the smallest c that the fixed pair
               admits, edge by edge.  No LP.
  B  fixedF  : N4's F frozen; Ghat_s (one variable per level) and G on the
               unbalanced points are free.  Two oracles: (i) a structural
               per-level test on the constraints whose BOTH endpoints are
               balanced ("constant-constant"), which yields either a lower
               bound delta_cc or a 2-constraint infeasibility certificate;
               (ii) an LP over the free G variables, bisected on delta.
  C  relaxF  : control.  F is a variable too (= the R11(c)/N4 section 2 LP).
               Reuses results/T2_hardness_grid.relaxF_min_ratio unchanged.
  D  cap     : mode B with the balanced-equality constraint imposed only on
               levels s <= smax (i.e. against algorithms whose queries have
               size at most smax).  Reports the largest feasible smax.
  E  nthresh : smallest n at which mode B becomes feasible (tau = 1), against
               the prediction n > K(T+1).
  F  tau     : how the best constant the relaxed-F LP can prove degrades as the
               band widens; it hits the trivial 1/eta ceiling of R2 at
               tau ~ ceil(K/eta).
  G  cert    : the universal 2-constraint certificate, exact rational arithmetic
               (subcommand "cert").
  H  window  : G is O-oblivious on all of {x > T} by itself, so only queries
               with |S| <= T+K can leak (subcommand "cert").

Run:  python3 results/F3_check.py            (sections A-F; CSV + JSON, ~25 min,
                                              of which sections A-E take ~4 min)
      python3 results/F3_check.py quick      (K = 4 only, n = 8K, ~5 s)
      python3 results/F3_check.py cert       (sections G and H, ~40 s)

Outputs: results/F3_delta_table.csv, results/F3_check.json (flushed after every
section, so a slow late LP cannot lose the table).
"""
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import N4_check as N4                                    # noqa: E402
from T2_hardness_grid import balanced_grid, relaxF_min_ratio  # noqa: E402

TOL = 1e-11


# --------------------------------------------------------------------- setup
def grid_edges(X, K):
    """Directed unit edges of the (x,y) grid, x in 0..X, y in 0..K."""
    out = []
    for x in range(X + 1):
        for y in range(K + 1):
            if x < X:
                out.append(((x, y), (x + 1, y), 'x'))
            if y < K:
                out.append(((x, y), (x, y + 1), 'y'))
    return out


def n4_instance(n, K, eta):
    """N4 closed form on the grid of width X = n-K.  Returns floats + params."""
    X = n - K
    P, F, Ghs, Gs, r, g, d = N4.solution(K, Fr(eta), X, n)
    Ff = np.array([[float(v) for v in row] for row in F])
    Gf = np.array([[float(v) for v in row] for row in Gs])
    return dict(P=P, X=X, F=Ff, Gs=Gf, Ghat=[float(v) for v in Ghs],
                r=[float(v) for v in r], g=[float(v) for v in g],
                d=[float(v) for v in d], Fexact=F, Gexact=Gs)


def bal_mask(n, K, tau, defn, smax=None):
    b = balanced_grid(n, K, tau, defn)
    if smax is not None:
        X = n - K
        xs = np.arange(X + 1)[:, None]
        ys = np.arange(K + 1)[None, :]
        b = b & ((xs + ys) <= smax)
    return b


# ------------------------------------------------------------------- mode A
def mode_A(n, K, eta, tau, defn):
    """N4's (F, G) verbatim: leakage on the balanced region + implied band."""
    I = n4_instance(n, K, eta)
    X, F, Gs, Ge = I['X'], I['F'], I['Gs'], I['Gexact']
    bal = bal_mask(n, K, tau, defn)

    # (a) leakage: G must be constant on each level of the balanced region.
    #     Done in EXACT rational arithmetic (Ge holds Fractions).
    levels = {}
    for x in range(X + 1):
        for y in range(K + 1):
            if bal[x, y]:
                levels.setdefault(x + y, []).append((x, y))
    n_bad_lvl, max_spread, worst = 0, Fr(0), None
    for s in sorted(levels):
        vals = [Ge[x][y] for (x, y) in levels[s]]
        sp = max(vals) - min(vals)
        if sp != 0:
            n_bad_lvl += 1
            if sp > max_spread:
                max_spread = sp
                worst = dict(level=s, points=[[x, y, float(Ge[x][y])]
                                              for (x, y) in levels[s]])
    leak_ok = (n_bad_lvl == 0)

    # (b) band: G is fixed, so the required inflation is read off edge by edge.
    cmin, hard = 1.0, []
    for p, q, _dr in grid_edges(X, K):
        dF = F[q] - F[p]
        dG = Gs[q] - Gs[p]
        if dF < TOL and abs(dG) > 1e-9:
            hard.append(dict(edge=[list(p), list(q)], dF=float(dF), dG=float(dG),
                             why='dF=0 but dG>0'))
            continue
        if dF < TOL:
            continue
        if dG <= TOL:
            hard.append(dict(edge=[list(p), list(q)], dF=float(dF), dG=float(dG),
                             why='dG=0 but dF>0'))
            continue
        cmin = max(cmin, dF / dG, dG / (eta * dF))
    if hard:
        return dict(mode='A_fixedFG', status='INFEASIBLE-ANY-DELTA',
                    min_delta=None, leak_ok=leak_ok, n_bad_levels=n_bad_lvl,
                    max_leak=float(max_spread), leak_witness=worst,
                    n_hard_edges=len(hard), hard_example=hard[0])
    return dict(mode='A_fixedFG',
                status='FEASIBLE-BAND' if leak_ok else 'LEAKS',
                min_delta=cmin ** 2 - 1, leak_ok=leak_ok,
                n_bad_levels=n_bad_lvl, max_leak=float(max_spread),
                leak_witness=worst, n_hard_edges=0, hard_example=None)


# --------------------------------------------- exact infeasibility certificate
def flat_cycle_certificate(Fex, bal, X, K):
    """Exact, delta-free infeasibility oracle for the frozen-F band LP.

    For every grid edge the band forces
        Delta F / c <= Delta Gs <= eta c Delta F      (c = sqrt(1+delta) >= 1),
    hence  Delta Gs = 0  on a FLAT edge (Delta F = 0) and  Delta Gs > 0  on a
    LIVE edge (Delta F > 0), for EVERY finite delta.  Identify the G-variables:
    all balanced points on one level s share the variable Ghat_s (the no-leakage
    constraint), and the two endpoints of a flat edge share their value.  If,
    after this contraction, some live edge joins a component to itself, or a
    directed cycle of live edges appears, the LP is infeasible for every delta.
    The returned cycle is an irreducible infeasible subset of constraints.

    Exact rational arithmetic (Fex holds Fractions), so "flat" is exact.
    """
    def vid(p):
        return ('L', p[0] + p[1]) if bal[p] else ('P', p)

    parent = {}

    def find(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    edges = grid_edges(X, K)
    live = []
    for p, q, _dr in edges:
        dF = Fex[q[0]][q[1]] - Fex[p[0]][p[1]]
        if dF == 0:
            union(vid(p), vid(q))
        else:
            live.append((p, q, dF))
    adj = {}
    for p, q, dF in live:
        a, b = find(vid(p)), find(vid(q))
        if a == b:                                     # self-loop: 2-constraint IIS
            return dict(kind='self-loop', cycle=[[list(p), list(q), float(dF)]],
                        component=str(a), length=1)
        adj.setdefault(a, []).append((b, p, q, dF))
    # cycle search over the contracted digraph
    WHITE, GREY, BLACK = 0, 1, 2
    color, stack = {}, []
    nodes = list(adj)

    def dfs(u):
        color[u] = GREY
        for (v, p, q, dF) in adj.get(u, ()):
            stack.append((p, q, dF))
            if color.get(v, WHITE) == WHITE:
                r = dfs(v)
                if r is not None:
                    return r
            elif color[v] == GREY:
                # unwind to the first occurrence of v
                cyc = []
                for (pp, qq, dd) in reversed(stack):
                    cyc.append([list(pp), list(qq), float(dd)])
                    if find(vid(pp)) == v:
                        break
                return list(reversed(cyc))
            stack.pop()
        color[u] = BLACK
        return None

    sys.setrecursionlimit(200000)
    for u in nodes:
        if color.get(u, WHITE) == WHITE:
            stack = []
            c = dfs(u)
            if c is not None:
                return dict(kind='cycle', cycle=c, length=len(c))
    return None


# ------------------------------------------------------------------- mode B
def cc_analysis(F, bal, X, K, eta):
    """Constant-constant analysis: per level s, the balanced->balanced edges all
    pin the SAME increment Ghat_{s+1} - Ghat_s.  Feasibility of that single
    variable needs  max dF <= eta (1+delta) min dF  over those edges."""
    per_level = {}
    for p, q, _dr in grid_edges(X, K):
        if bal[p] and bal[q]:
            per_level.setdefault(p[0] + p[1], []).append((p, q, float(F[q] - F[p])))
    ratio, worst, cert = 1.0, None, None
    for s in sorted(per_level):
        es = per_level[s]
        lo = min(e[2] for e in es)
        hi = max(e[2] for e in es)
        if lo < TOL and hi > TOL:
            e0 = min(es, key=lambda e: e[2])
            e1 = max(es, key=lambda e: e[2])
            cert = dict(level=s,
                        flat_edge=[list(e0[0]), list(e0[1])], flat_dF=e0[2],
                        live_edge=[list(e1[0]), list(e1[1])], live_dF=e1[2],
                        n_edges_at_level=len(es))
            return dict(hard=True, ratio=float('inf'), certificate=cert,
                        worst_level=s)
        if lo > TOL and hi / lo > ratio:
            ratio, worst = hi / lo, dict(
                level=s, min_dF=lo, max_dF=hi,
                min_edge=[list(min(es, key=lambda e: e[2])[0]),
                          list(min(es, key=lambda e: e[2])[1])],
                max_edge=[list(max(es, key=lambda e: e[2])[0]),
                          list(max(es, key=lambda e: e[2])[1])])
    return dict(hard=False, ratio=ratio, delta_cc=max(0.0, ratio / eta - 1.0),
                worst=worst)


def mode_B(n, K, eta, tau, defn, smax=None, I=None):
    """N4's F frozen, Ghat and unbalanced G free.  Min delta."""
    if I is None:
        I = n4_instance(n, K, eta)
    X, F = I['X'], I['F']
    bal = bal_mask(n, K, tau, defn, smax)

    cyc = flat_cycle_certificate(I['Fexact'], bal, X, K)
    if cyc is not None:
        return dict(mode='B_fixedF', status='INFEASIBLE-ANY-DELTA',
                    min_delta=None, delta_cc=None, certificate=cyc,
                    cc_ratio=None)
    cc = cc_analysis(F, bal, X, K, eta)
    if cc['hard']:                       # should be unreachable after the cycle test
        return dict(mode='B_fixedF', status='INFEASIBLE-ANY-DELTA',
                    min_delta=None, delta_cc=None, certificate=cc['certificate'],
                    cc_ratio=None)

    unbal = [(x, y) for x in range(X + 1) for y in range(K + 1) if not bal[x, y]]
    gv = {p: (n + 1) + i for i, p in enumerate(unbal)}
    nv = (n + 1) + len(unbal)
    edges = grid_edges(X, K)

    def gref(p):
        return (p[0] + p[1]) if bal[p] else gv[p]

    def feasible(delta):
        c = math.sqrt(1.0 + delta)
        R, C, V, b = [], [], [], []
        row = 0
        for p, q, _dr in edges:
            dF = float(F[q] - F[p])
            gq, gp = gref(q), gref(p)
            if gq == gp:                      # same variable, nothing to impose
                continue
            # dGs <= eta c dF
            R += [row, row]; C += [gq, gp]; V += [1.0, -1.0]
            b.append(eta * c * dF); row += 1
            # dGs >= dF/c
            R += [row, row]; C += [gq, gp]; V += [-1.0, 1.0]
            b.append(-dF / c); row += 1
        A = coo_matrix((V, (R, C)), shape=(row, nv)).tocsr()
        out = linprog(np.zeros(nv), A_ub=A, b_ub=np.array(b),
                      A_eq=coo_matrix(([1.0], ([0], [0])), shape=(1, nv)).tocsr(),
                      b_eq=np.array([0.0]),
                      bounds=[(None, None)] * nv, method='highs')
        return out.status == 0

    lo = cc['delta_cc']
    if feasible(lo):
        return dict(mode='B_fixedF', status='FEASIBLE', min_delta=lo,
                    delta_cc=lo, cc_ratio=cc['ratio'], cc_worst=cc['worst'],
                    certificate=None)
    hi = max(2 * lo, 0.5)
    for _ in range(14):
        if feasible(hi):
            break
        hi *= 2
    else:
        return dict(mode='B_fixedF', status='INFEASIBLE-UP-TO-%.4g' % hi,
                    min_delta=None, delta_cc=lo, cc_ratio=cc['ratio'],
                    cc_worst=cc['worst'], certificate=None)
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if feasible(mid):
            hi = mid
        else:
            lo = mid
        if hi - lo < 1e-7 * max(1.0, hi):
            break
    return dict(mode='B_fixedF', status='FEASIBLE', min_delta=hi,
                delta_cc=cc['delta_cc'], cc_ratio=cc['ratio'],
                cc_worst=cc['worst'], certificate=None)


# ------------------------------------------------------------------- mode D
def mode_D(n, K, eta, tau, defn):
    """Largest query-size cap smax for which the frozen-F band LP stays feasible.

    smax = K is the query model of results/N5_bounded_query_hardness.tex.
    The scan uses the FULL LP (not only the constant-constant test)."""
    I = n4_instance(n, K, eta)
    T = I['P']['T']
    best, best_delta, first_bad, bad = None, None, None, None
    for smax in range(K, min(n, 3 * (T + K)) + 1):
        r = mode_B(n, K, eta, tau, defn, smax=smax, I=I)
        if r['status'] != 'FEASIBLE':
            first_bad, bad = smax, r
            break
        best, best_delta = smax, r['min_delta']
    dK = mode_B(n, K, eta, tau, defn, smax=K, I=I)          # the N5 query model
    return dict(mode='D_cap', smax_max=best, T=T, delta_at_smax=best_delta,
                delta_at_K=dK.get('min_delta'), status_at_K=dK['status'],
                first_bad_smax=first_bad,
                first_bad_status=(bad['status'] if bad else None),
                certificate=(bad.get('certificate') if bad else None))


# --------------------------------------------------------------------- main
def cert_str(c, fallback=None):
    if c is None:
        return '' if fallback is None else str(fallback)
    e = c['cycle'][0]
    return ('%s len=%d, live edge (%d,%d)->(%d,%d) dF=%.4g inside one '
            'flat/level component' % (c['kind'], c['length'], e[0][0], e[0][1],
                                      e[1][0], e[1][1], e[2]))


def certificate_check():
    """G.  The universal 2-constraint certificate, in exact rational arithmetic.

    Claim [HAND-PROOF-UNREVIEWED, oracle-matched below].  Let T be the tail
    length of the N4 closed form (r_x = g_x = 0 for x > T, and r_T = g_T > 0, so
    F(T,y) = 1 for every y >= 1).  Let K >= 3 and n - K >= T.  For an integer
    m with 1 <= m <= K-2 the three points
        P1 = (T, m)    and    P2 = (T-1, m+1)   (both on level T+m),
        P3 = (T, m+1)                           (on level T+m+1)
    carry the two edges
        flat  edge  P1 -> P3 :  Delta F = 1 - 1 = 0,
        live  edge  P2 -> P3 :  Delta F = 1 - F(T-1,m+1)
                              = (r_{T-1} - g_{T-1})(K-1-m)/(K-1) > 0.
    If P1, P2, P3 are all balanced, the no-leakage constraint pins their
    predictor values to Ghat_{T+m}, Ghat_{T+m}, Ghat_{T+m+1}, and
        band_up on the flat edge  =>  Ghat_{T+m+1} - Ghat_{T+m} <= 0,
        band_lo on the live edge  =>  Ghat_{T+m+1} - Ghat_{T+m} > 0,
    an irreducible infeasible subset of size 2, for EVERY delta and for every
    choice of G off the balanced region.
    For m = 1 the balancedness condition reads
      definition y <= tau  :  tau >= 2                        (any n),
      true band            :  K(T+1)/n >= 2 - tau, i.e. for tau = 1
                              n <= K(T+1)   and for tau >= 2 always.
    Larger m covers the small-n regime where the band centre K|S|/n has already
    climbed above y = 2 by level T.
    """
    print('G.  universal 2-constraint certificate (exact rational arithmetic)')
    print(f"{'K':>3} {'eta':>5} {'tau':>4} {'n':>6} {'T':>4} {'defn':>7} "
          f"{'flat==0':>9} {'dF(live,1)':>11} {'m fires':>11} "
          f"{'oracle: infeasible':>19} {'witness':>10}")
    npass = nfail = 0
    for K in [3, 4, 5, 6, 8]:
        for eta in [Fr(3, 2), Fr(2), Fr(5, 2), Fr(3)]:
            for tau in [1, 2]:
                for mult in [8, 16, 32]:
                    for defn in ['true', 'ysmall']:
                        n = mult * K
                        I = n4_instance(n, K, float(eta))
                        T, X, Fe = I['P']['T'], I['X'], I['Fexact']
                        if T + 1 > X or K < 3:
                            continue
                        bal = bal_mask(n, K, tau, defn)
                        flat_ok, live_ok, mfire = True, True, None
                        for m in range(1, K - 1):
                            if Fe[T][m + 1] - Fe[T][m] != 0:
                                flat_ok = False
                            if Fe[T][m + 1] - Fe[T - 1][m + 1] <= 0:
                                live_ok = False
                            if (mfire is None and bal[T, m] and bal[T - 1, m + 1]
                                    and bal[T, m + 1]):
                                mfire = m
                        live = float(Fe[T][2] - Fe[T - 1][2])
                        cyc = flat_cycle_certificate(Fe, bal, X, K)
                        got = (cyc is not None)
                        pe = ([[T - 1, mfire + 1], [T, mfire + 1]]
                              if mfire is not None else None)
                        same = (got and pe is not None
                                and any(c[0] == pe[0] and c[1] == pe[1]
                                        for c in cyc['cycle']))
                        ok = (flat_ok and live_ok
                              and ((mfire is not None) == got))
                        npass += ok; nfail += (not ok)
                        print(f"{K:3d} {str(eta):>5} {tau:4d} {n:6d} {T:4d} "
                              f"{defn:>7} {str(int(flat_ok)):>9} {live:11.3e} "
                              f"{str(mfire):>11} {str(got):>19} "
                              f"{('m=%d hit' % mfire if same else ('-' if not got else 'other')):>10}"
                              f"{'' if ok else '   <-- FAIL'}")
    print(f"\n  {npass} PASS / {nfail} FAIL.  Checked: Delta F on the flat edge is "
          f"exactly 0 and on the live edge is > 0 (exact rationals), and the "
          f"delta-free\n  cycle oracle reports infeasibility EXACTLY when "
          f"P1, P2, P3 are balanced.")

    print()
    print('H.  the far field answers O-independently by itself: is G(x,y) = Ghat_{x+y} '
          'on ALL of {x > T}?')
    print('  (if yes, only queries with |S \\ O| <= T can leak, so the union bound '
          'runs over sets of size <= T+K)')
    print(f"{'K':>3} {'eta':>5} {'n':>6} {'T':>4} {'#points x>T':>12} "
          f"{'max |G - Ghat_{x+y}|':>22} {'largest leaking |S|':>20}")
    h_pass = h_fail = 0
    for K in [3, 4, 6, 8]:
        for eta in [Fr(3, 2), Fr(2), Fr(3)]:
            n = 16 * K
            I = n4_instance(n, K, float(eta))
            T, X, Fe, Ge, Gh = (I['P']['T'], I['X'], I['Fexact'], I['Gexact'],
                                N4.solution(K, Fr(eta), I['X'], n)[2])
            worst, cnt, big = Fr(0), 0, 0
            for x in range(X + 1):
                for y in range(K + 1):
                    dev = abs(Ge[x][y] - Gh[x + y])
                    if x > T:
                        cnt += 1
                        worst = max(worst, dev)
                    if dev != 0:
                        big = max(big, x + y)
            ok = (worst == 0) and (big <= T + K)
            h_pass += ok; h_fail += (not ok)
            print(f"{K:3d} {str(eta):>5} {n:6d} {T:4d} {cnt:12d} "
                  f"{str(worst):>22} {big:20d}{'' if ok else '   <-- FAIL'}")
    print(f"\n  {h_pass} PASS / {h_fail} FAIL.  G is exactly level-constant on "
          f"{{x > T}} and every leaking set has |S| <= T + K.")
    return 0 if (nfail == 0 and h_fail == 0) else 1


def main(quick=False):
    Ks = [4] if quick else [4, 6]
    mults = [8] if quick else [8, 16, 32]
    etas = [2.0] if quick else [1.5, 2.0, 3.0]
    taus = [1] if quick else [1, 2]
    defns = ['true', 'ysmall']

    rows, blob = [], {'A': [], 'B': [], 'C': [], 'D': []}

    csv = os.path.join(HERE, 'F3_delta_table.csv')

    def dump():
        """Flush after every section so a slow late LP cannot lose the table."""
        with open(csv, 'w') as fh:
            fh.write('n,K,tau,eta,defn,mode,status,min_delta,note\n')
            for r in rows:
                fh.write('%(n)s,%(K)s,%(tau)s,%(eta)s,%(defn)s,%(mode)s,%(status)s,'
                         '%(min_delta)s,%(note)s\n' % r)
        with open(os.path.join(HERE, 'F3_check.json'), 'w') as fh:
            json.dump(blob, fh, indent=1, default=str)

    print('=' * 108)
    print('A/B.  N4 explicit (F,G) under the TRUE balanced band |y - K|S|/n| <= tau')
    print('=' * 108)
    print(f"{'K':>2} {'n':>5} {'tau':>3} {'eta':>4} {'defn':>7} | "
          f"{'A:leak':>10} {'A:status':>22} {'A:delta':>9} | "
          f"{'B:status':>22} {'B:delta':>9} {'B:cert level':>13}")
    for K in Ks:
        for mult in mults:
            n = mult * K
            for eta in etas:
                for tau in taus:
                    for defn in defns:
                        t0 = time.time()
                        A = mode_A(n, K, eta, tau, defn)
                        B = mode_B(n, K, eta, tau, defn)
                        for d in (A, B):
                            d.update(n=n, K=K, tau=tau, eta=eta, defn=defn,
                                     secs=round(time.time() - t0, 2))
                        blob['A'].append(A); blob['B'].append(B)
                        certlvl = (('%s(len %d)' % (B['certificate']['kind'],
                                                    B['certificate']['length']))
                                   if B.get('certificate') else '')
                        print(f"{K:2d} {n:5d} {tau:3d} {eta:4.1f} {defn:>7} | "
                              f"{'OK' if A['leak_ok'] else 'NO(%d lv)' % A['n_bad_levels']:>10} "
                              f"{A['status']:>22} "
                              f"{('%.6g' % A['min_delta']) if A['min_delta'] is not None else '-':>9} | "
                              f"{B['status']:>22} "
                              f"{('%.6g' % B['min_delta']) if B['min_delta'] is not None else '-':>9} "
                              f"{str(certlvl):>13}", flush=True)
                        for d in (A, B):
                            rows.append(dict(
                                n=n, K=K, tau=tau, eta=eta, defn=defn,
                                mode=d['mode'], status=d['status'],
                                min_delta=('' if d['min_delta'] is None
                                           else '%.9g' % d['min_delta']),
                                note=(('leak_levels=%d' % d['n_bad_levels'])
                                      if d['mode'].startswith('A')
                                      else ('cert_level=%s' % certlvl
                                            if certlvl != '' else
                                            'delta_cc=%.6g' % d['delta_cc']))))

    dump()

    print()
    print('=' * 108)
    print('D.  largest query-size cap smax for which the frozen-F LP stays feasible '
          '(true band); T = N4 tail length')
    print('=' * 108)
    print(f"{'K':>2} {'n':>5} {'tau':>3} {'eta':>4} {'T':>4} {'smax*':>6} "
          f"{'delta(smax*)':>13} {'first bad':>10}  {'certificate at the first bad cap'}")
    for K in Ks:
        for mult in mults:
            n = mult * K
            for eta in etas:
                for tau in taus:
                    D = mode_D(n, K, eta, tau, 'true')
                    D.update(n=n, K=K, tau=tau, eta=eta, defn='true')
                    blob['D'].append(D)
                    cs = cert_str(D['certificate'], D['first_bad_status'])
                    print(f"{K:2d} {n:5d} {tau:3d} {eta:4.1f} {D['T']:4d} "
                          f"{str(D['smax_max']):>6} "
                          f"{('%.6g' % D['delta_at_smax']) if D.get('delta_at_smax') is not None else '-':>13} "
                          f"{str(D['first_bad_smax']):>10}  {cs}", flush=True)
                    rows.append(dict(n=n, K=K, tau=tau, eta=eta, defn='true',
                                     mode='D_cap',
                                     status='SMAX=%s' % D['smax_max'],
                                     min_delta=('' if D.get('delta_at_smax') is None
                                                else '%.9g' % D['delta_at_smax']),
                                     note='T=%d first_bad_smax=%s' % (D['T'],
                                                                     D['first_bad_smax'])))

    dump()

    print()
    print('=' * 108)
    print('C.  control: same LP with F ALSO a variable (R11(c) / N4 section 2)')
    print('=' * 108)
    print(f"{'K':>2} {'n':>5} {'tau':>3} {'eta':>4} {'defn':>7} {'status':>10} "
          f"{'min F(K,0)':>12} {'V_j (R10)':>11} {'U_K':>9}")
    for K in Ks:
        for mult in mults:
            n = mult * K
            for eta in ([2.0] if quick else [1.5, 2.0, 3.0]):
                for tau in taus:
                    for defn in defns:
                        t0 = time.time()
                        try:
                            r = relaxF_min_ratio(n, K, eta, tau, defn)
                        except Exception as ex:          # pragma: no cover
                            r = dict(status='EXC:%s' % type(ex).__name__, ratio=None)
                        P = N4.params(K, Fr(eta))
                        UK = 1 - (1 - 1 / (eta * (K - 1) + 1)) ** K
                        r.update(n=n, K=K, tau=tau, eta=eta, defn=defn,
                                 Vj=float(P['Vj']), UK=UK,
                                 secs=round(time.time() - t0, 2))
                        blob['C'].append(r)
                        print(f"{K:2d} {n:5d} {tau:3d} {eta:4.1f} {defn:>7} "
                              f"{r['status']:>10} "
                              f"{('%.9f' % r['ratio']) if r['ratio'] is not None else '-':>12} "
                              f"{float(P['Vj']):11.9f} {UK:9.6f}  [{r['secs']}s]",
                              flush=True)
                        rows.append(dict(n=n, K=K, tau=tau, eta=eta, defn=defn,
                                         mode='C_relaxF', status=r['status'],
                                         min_delta='0',
                                         note=('ratio=%.9f' % r['ratio']
                                               if r['ratio'] is not None else '')))

    dump()

    print()
    print('=' * 108)
    print('E.  smallest n for which the frozen-F construction survives the true band '
          '(exact cycle oracle), vs the prediction n >= K(T+1)/tau')
    print('=' * 108)
    print('  prediction: the construction survives iff tau = 1 and n > K(T+1); '
          'for tau >= 2 no n works (y = 2 enters the band at every level).')
    print(f"{'K':>2} {'eta':>4} {'tau':>3} {'T':>4} {'n_min(found)':>13} "
          f"{'K(T+1)+1':>11} {'match':>6} {'delta at n_min':>15}")
    for K in Ks:
        for eta in etas:
            for tau in taus:
                I0 = n4_instance(4 * K, K, eta)
                T = I0['P']['T']
                pred = (K * (T + 1) + 1) if tau == 1 else None
                if tau == 1:
                    cand = range(max(2 * K, K * (T + 1) - 5), K * (T + 1) + 9)
                else:                       # sparse probe: is ANY n admissible?
                    cand = [m * K for m in (2, 4, 8, 16, 32, 64)]
                nmin = None
                for n in cand:
                    I = n4_instance(n, K, eta)
                    if flat_cycle_certificate(I['Fexact'],
                                              bal_mask(n, K, tau, 'true'),
                                              I['X'], K) is None:
                        nmin = n
                        break
                dd = None
                if nmin is not None:
                    dd = mode_B(nmin, K, eta, tau, 'true')['min_delta']
                blob.setdefault('E', []).append(
                    dict(K=K, eta=eta, tau=tau, T=T, n_min=nmin, pred=pred,
                         delta_at_nmin=dd))
                print(f"{K:2d} {eta:4.1f} {tau:3d} {T:4d} {str(nmin):>13} "
                      f"{str(pred):>11} {'YES' if nmin == pred else 'no':>6} "
                      f"{('%.6g' % dd) if dd is not None else '-':>15}", flush=True)
                rows.append(dict(n=(nmin if nmin else ''), K=K, tau=tau, eta=eta,
                                 defn='true', mode='E_nthreshold',
                                 status=('NMIN=%s' % nmin),
                                 min_delta=('' if dd is None else '%.9g' % dd),
                                 note='T=%d pred=%s' % (T, pred)))

    dump()

    print()
    print('=' * 108)
    print('F.  how the best constant the technique can prove degrades with tau '
          '(relaxF, true band, n = 16K)')
    print('=' * 108)
    print(f"{'K':>2} {'eta':>4} " + ' '.join(f"{'tau='+str(t):>12}" for t in
                                             [1, 2, 3, 4, 6])
          + f" {'V_j (R10)':>11} {'U_K':>9} {'1-e^-1/eta':>11}")
    for K in ([6] if quick else [6, 8, 12]):
        for eta in ([2.0] if quick else [1.5, 2.0, 3.0]):
            n = 16 * K
            vals = []
            for t in [1, 2, 3, 4, 6]:
                # (K, eta) = (12, 3) makes HiGHS crawl on this LP (> 20 min per
                # solve) and adds nothing to the trend; skipped deliberately and
                # reported as '-'.  Same for K = 12 with tau >= 6 at eta = 3.
                if t >= K or (K >= 12 and eta >= 3.0):
                    vals.append(None); continue
                try:
                    vals.append(relaxF_min_ratio(n, K, eta, t, 'true')['ratio'])
                except Exception:
                    vals.append(None)
            P = N4.params(K, Fr(eta))
            UK = 1 - (1 - 1 / (eta * (K - 1) + 1)) ** K
            lim = 1 - math.exp(-1 / eta)
            blob.setdefault('F', []).append(
                dict(K=K, eta=eta, n=n, taus=[1, 2, 3, 4, 6], values=vals,
                     Vj=float(P['Vj']), UK=UK, limit=lim))
            print(f"{K:2d} {eta:4.1f} " +
                  ' '.join(f"{v:12.9f}" if v is not None else f"{'-':>12}"
                           for v in vals)
                  + f" {float(P['Vj']):11.9f} {UK:9.6f} {lim:11.6f}", flush=True)
            for t, v in zip([1, 2, 3, 4, 6], vals):
                rows.append(dict(n=n, K=K, tau=t, eta=eta, defn='true',
                                 mode='F_tau_sweep',
                                 status=('OK' if v is not None else 'SKIP'),
                                 min_delta='0',
                                 note=('relaxF_ratio=%.9f' % v if v is not None
                                       else '')))

    dump()
    print('\nwrote results/F3_delta_table.csv and results/F3_check.json')
    return 0


if __name__ == '__main__':
    if 'cert' in sys.argv:
        sys.exit(certificate_check())
    sys.exit(main(quick=('quick' in sys.argv)))
