#!/usr/bin/env python3
"""P0 (TASKS9): the correct O-independence band, and the feasibility LP for the
(x,y)-symmetric hardness family under ARBITRARY-SIZE queries.

Question.  thm:hardness only covers queries of size <= K.  J5's N\\{e} attack
shows that the existing family leaks O on large queries: for e in O the query
N\\{e} lands at (x,y) = (n-K, K-1) and for e not in O at (n-K-1, K), and the
two predictor values differ.  A hardness proof for arbitrary-size queries needs
the predictor to be O-independent (a function of |S| alone) on the whole
"typical" region of |S \\cap O| for every query size, not only for |S| <= K.
This script writes that requirement as a linear program on the count grid and
asks whether the (x,y)-symmetric family can still do anything.

LP (variant 'spec', the one asked for in TASKS9 P0):
  variables  F(x,y), G(x,y)   for 0 <= x <= n-K, 0 <= y <= K
             Ghat(s)          for 0 <= s <= n          (free)
  (1) norm     F(0,0) = 0, F(0,K) = 1, F(x,y) <= 1 for x+y <= K
  (2) mono     Delta_x F >= 0, Delta_y F >= 0
  (3) submod   Delta_x^2 F <= 0, Delta_x Delta_y F <= 0, Delta_y^2 F <= 0
               (count-grid sufficient condition, lem:app-count)
  (4) band     on every x-edge and y-edge: d/eta <= dtilde <= d,
               d = Delta F, dtilde = Delta G.  This is the split
               (eta_u, eta_o) = (eta, 1).  Only the PRODUCT eta_u*eta_o matters:
               replacing G by beta*G multiplies every dtilde by beta and moves
               the split to (eta/beta, beta) with the same product, and it
               rescales Ghat by the same constant, so it carries no information
               about O.  (Same scaling remark as in app:hardness.)
  (5) o-indep  G(x,y) = Ghat(x+y) at every grid point with y in B(x+y)
  objective    min F(K,0)   (the ratio the algorithm gets when its output misses O)

Variant 'capped' adds F(x,y) <= 1 at EVERY grid point.  With F(0,K) = 1 and
monotonicity that forces the flat top row F(.,K) == 1 of the existing family,
so 'capped' is the LP question "can the EXISTING shape survive the band".

Two band definitions:
  (i)  'proxy'  B(s) = {y : |y - sK/n| <= t*max(1, sigma_s)},
                sigma_s = sqrt(sK/n (1 - s/n)), t = sqrt(2 log Q), Q = n^c
  (ii) 'hyper'  B(s) = the smallest (mode-centred) set of y with
                P[|S cap O| not in B(s)] <= 1/(4Q), exact hypergeometric,
                exact rational arithmetic.
Both are intersected with the feasible range y in [max(0, s-(n-K)), min(K, s)].

Usage:
  python3 results/P0_band_lp.py sweep    # 54 configs x 2 bands x 2 variants
  python3 results/P0_band_lp.py iis      # deletion-filter IIS for infeasible ones
  python3 results/P0_band_lp.py all      # both (this is what produced the json)
Outputs results/P0_band_lp.json and results/P0_band_lp_iis.json.
"""
import json
import math
import os
import sys
import time
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
TOL = 1e-7
TIME_LIMIT = 60.0

KS = [3, 4, 6]
NMULTS = [16, 32, 64]
CS = [2, 3]
ETAS = [1.5, 2.0, 3.0]
BANDS = ['proxy', 'hyper']

# (K, n/K, c, eta, band, variant) for the IIS stage
IIS_CONFIGS = [
    (3, 16, 2, 2.0, 'proxy', 'spec'),
    (3, 16, 2, 2.0, 'hyper', 'spec'),
    (3, 16, 2, 2.0, 'proxy', 'capped'),
    (3, 16, 2, 2.0, 'hyper', 'capped'),
    (3, 16, 2, 1.5, 'hyper', 'spec'),
    (3, 16, 2, 3.0, 'hyper', 'spec'),
    (3, 16, 3, 2.0, 'hyper', 'spec'),
    (3, 32, 2, 2.0, 'hyper', 'spec'),
    (4, 16, 2, 2.0, 'hyper', 'spec'),
    (4, 16, 2, 2.0, 'proxy', 'spec'),
    (6, 16, 2, 2.0, 'hyper', 'spec'),
]


# --------------------------------------------------------------------------
# bands
# --------------------------------------------------------------------------
def yrange(K, n, s):
    return max(0, s - (n - K)), min(K, s)


def band_proxy(K, n, c):
    """TASKS9 P0 proxy band."""
    Q = float(n) ** c
    t = math.sqrt(2.0 * math.log(Q))
    B = {}
    for s in range(n + 1):
        lo, hi = yrange(K, n, s)
        mu = s * K / n
        sig = math.sqrt(max(0.0, mu * (1.0 - s / n)))
        w = t * max(1.0, sig)
        B[s] = [y for y in range(lo, hi + 1) if abs(y - mu) <= w + 1e-12]
    return B, dict(t=t, Q=Q)


def band_hyper(K, n, c):
    """Exact hypergeometric tail band: smallest mode-centred set with
    P[y not in B] <= 1/(4Q).  Exact rational arithmetic."""
    Q = n ** c
    thresh = Fraction(1, 4 * Q)
    B = {}
    for s in range(n + 1):
        lo, hi = yrange(K, n, s)
        den = math.comb(n, s)
        pm = {y: Fraction(math.comb(K, y) * math.comb(n - K, s - y), den)
              for y in range(lo, hi + 1)}
        mu = s * K / n
        order = sorted(pm, key=lambda y: (-pm[y], abs(y - mu)))
        cum = Fraction(0)
        chosen = []
        for y in order:
            chosen.append(y)
            cum += pm[y]
            if 1 - cum <= thresh:
                break
        chosen.sort()
        B[s] = chosen
    return B, dict(Q=Q)


def get_band(K, n, c, kind):
    return band_proxy(K, n, c) if kind == 'proxy' else band_hyper(K, n, c)


def band_stats(K, n, B):
    """contiguity + how many levels have the band equal to the whole y range."""
    full, gaps, widths = 0, 0, []
    for s in range(n + 1):
        lo, hi = yrange(K, n, s)
        ys = B[s]
        widths.append(len(ys))
        if len(ys) == hi - lo + 1:
            full += 1
        if ys and (ys[-1] - ys[0] + 1) != len(ys):
            gaps += 1
    return dict(levels=n + 1, full_levels=full, noncontiguous=gaps,
                min_width=min(widths), max_width=max(widths))


# --------------------------------------------------------------------------
# LP
# --------------------------------------------------------------------------
def build(K, n, eta, B, variant, objcut=None):
    """Return (rows, nvar, obj_index).  A row is (group, label, {var: coef}, rhs)
    meaning  sum coef * var <= rhs."""
    X = n - K
    W = K + 1
    nF = (X + 1) * W
    iF = lambda x, y: x * W + y
    iG = lambda x, y: nF + x * W + y
    iH = lambda s: 2 * nF + s
    nvar = 2 * nF + (n + 1)
    rows = []
    add = rows.append

    # (1) normalisation / optimality of O
    add(('norm', 'F(0,0)<=0', {iF(0, 0): 1.0}, 0.0))
    add(('norm', 'F(0,0)>=0', {iF(0, 0): -1.0}, 0.0))
    add(('norm', 'F(0,K)>=1', {iF(0, K): -1.0}, -1.0))
    add(('norm', 'F(0,K)<=1', {iF(0, K): 1.0}, 1.0))
    for x in range(X + 1):
        for y in range(W):
            if (x, y) == (0, K):
                continue
            if x + y <= K or variant == 'capped':
                add(('norm', 'F(%d,%d)<=1' % (x, y), {iF(x, y): 1.0}, 1.0))

    # (2) monotonicity
    for x in range(X + 1):
        for y in range(W):
            if x < X:
                add(('mono_x', 'x(%d,%d)' % (x, y),
                     {iF(x, y): 1.0, iF(x + 1, y): -1.0}, 0.0))
            if y < K:
                add(('mono_y', 'y(%d,%d)' % (x, y),
                     {iF(x, y): 1.0, iF(x, y + 1): -1.0}, 0.0))

    # (3) submodularity (count-grid second differences)
    for x in range(X + 1):
        for y in range(W):
            if x + 2 <= X:
                add(('sub_xx', '(%d,%d)' % (x, y),
                     {iF(x + 2, y): 1.0, iF(x + 1, y): -2.0, iF(x, y): 1.0}, 0.0))
            if x + 1 <= X and y + 1 <= K:
                add(('sub_xy', '(%d,%d)' % (x, y),
                     {iF(x + 1, y + 1): 1.0, iF(x + 1, y): -1.0,
                      iF(x, y + 1): -1.0, iF(x, y): 1.0}, 0.0))
            if y + 2 <= K:
                add(('sub_yy', '(%d,%d)' % (x, y),
                     {iF(x, y + 2): 1.0, iF(x, y + 1): -2.0, iF(x, y): 1.0}, 0.0))

    # (4) single-element band, split (eta_u, eta_o) = (eta, 1)
    for x in range(X + 1):
        for y in range(W):
            nbrs = []
            if x < X:
                nbrs.append(((x + 1, y), 'x'))
            if y < K:
                nbrs.append(((x, y + 1), 'y'))
            for (u, v), d in nbrs:
                # dtilde - d <= 0
                add(('band_up', '%s(%d,%d)' % (d, x, y),
                     {iG(u, v): 1.0, iG(x, y): -1.0,
                      iF(u, v): -1.0, iF(x, y): 1.0}, 0.0))
                # d/eta - dtilde <= 0
                add(('band_lo', '%s(%d,%d)' % (d, x, y),
                     {iF(u, v): 1.0 / eta, iF(x, y): -1.0 / eta,
                      iG(u, v): -1.0, iG(x, y): 1.0}, 0.0))

    # (5) O-independence on the band
    for x in range(X + 1):
        for y in range(W):
            s = x + y
            if y in B[s]:
                add(('oind_up', '(%d,%d)' % (x, y),
                     {iG(x, y): 1.0, iH(s): -1.0}, 0.0))
                add(('oind_lo', '(%d,%d)' % (x, y),
                     {iG(x, y): -1.0, iH(s): 1.0}, 0.0))

    # optional objective cut, used to turn "the optimum is v*" into an
    # infeasible system whose IIS certifies the lower bound F(K,0) >= v*.
    if objcut is not None:
        add(('objcut', 'F(K,0)<=%.9f' % objcut, {iF(K, 0): 1.0}, objcut))

    return rows, nvar, iF(K, 0), dict(iF=iF, iG=iG, iH=iH, X=X, nF=nF)


def solve(rows, nvar, obj=None, keep=None):
    if keep is None:
        keep = range(len(rows))
    R, C, V, b = [], [], [], []
    for r, k in enumerate(keep):
        _, _, coefs, rhs = rows[k]
        for v, cf in coefs.items():
            R.append(r)
            C.append(v)
            V.append(cf)
        b.append(rhs)
    A = coo_matrix((V, (R, C)), shape=(len(b), nvar)).tocsr()
    cvec = np.zeros(nvar)
    if obj is not None:
        cvec[obj] = 1.0
    res = linprog(cvec, A_ub=A, b_ub=np.array(b), bounds=(None, None),
                  method='highs', options={'time_limit': TIME_LIMIT})
    return res


# --------------------------------------------------------------------------
# post-processing of a feasible solution
# --------------------------------------------------------------------------
def extract(res, K, n, idx):
    X, W = idx['X'], K + 1
    xv = res.x
    F = [[float(xv[idx['iF'](x, y)]) for y in range(W)] for x in range(X + 1)]
    G = [[float(xv[idx['iG'](x, y)]) for y in range(W)] for x in range(X + 1)]
    H = [float(xv[idx['iH'](s)]) for s in range(n + 1)]
    return F, G, H


def j5_check(G, K, n, B):
    """J5's N\\{e} attack and the (n-2)-set classes: do the predictor values at
    grid points of the SAME |S| agree?  Unequal values leak O."""
    X = n - K
    out = []

    def cell(x, y):
        return G[x][y] if 0 <= x <= X and 0 <= y <= K else None

    groups = [('n-1', [(X, K - 1), (X - 1, K)]),
              ('n-2', [(X, K - 2), (X - 1, K - 1), (X - 2, K)])]
    for name, pts in groups:
        vals = [(p, cell(*p)) for p in pts]
        vals = [(p, v) for p, v in vals if v is not None]
        for i in range(len(vals)):
            for j in range(i + 1, len(vals)):
                (p, a), (q, bq) = vals[i], vals[j]
                out.append(dict(level=name, p=list(p), q=list(q),
                                Gp=a, Gq=bq, diff=abs(a - bq),
                                equal=bool(abs(a - bq) <= 1e-6),
                                p_banded=bool(p[1] in B[p[0] + p[1]]),
                                q_banded=bool(q[1] in B[q[0] + q[1]])))
    return out


def violation(rows, x):
    worst, where = 0.0, None
    for g, lab, coefs, rhs in rows:
        v = sum(cf * x[i] for i, cf in coefs.items()) - rhs
        if v > worst:
            worst, where = v, (g, lab)
    return worst, where


# --------------------------------------------------------------------------
# IIS by deletion filter
# --------------------------------------------------------------------------
def iis(rows, nvar, verbose=True):
    """Deletion filter.  Stage 1: constraint-family (group) level.  Stage 2:
    block deletion with shrinking block size (a pure speed-up, it removes only
    rows whose removal keeps the system infeasible).  Stage 3: single-row
    deletion, which makes the surviving set minimal for this deletion order."""
    groups = []
    for i, (g, _, _, _) in enumerate(rows):
        if g not in groups:
            groups.append(g)
    keep = set(range(len(rows)))
    bygroup = {g: [i for i, r in enumerate(rows) if r[0] == g] for g in groups}

    res = solve(rows, nvar, keep=sorted(keep))
    if res.status != 2:
        if verbose:
            print('    cut system not infeasible (status %d: %s)'
                  % (res.status, res.message[:70]), flush=True)
        return None, None, 0, None
    nsolve = 1
    # stage 1: group-level filter
    dropped_groups = []
    for g in groups:
        trial = keep - set(bygroup[g])
        if not trial:
            continue
        r = solve(rows, nvar, keep=sorted(trial))
        nsolve += 1
        if r.status == 2:
            keep = trial
            dropped_groups.append(g)
            if verbose:
                print('    group %-8s droppable (%d rows left)' % (g, len(keep)),
                      flush=True)
    # stage 2: block deletion
    for blk in (256, 64, 16, 4):
        changed = True
        while changed:
            changed = False
            order = sorted(keep)
            for start in range(0, len(order), blk):
                block = set(order[start:start + blk])
                if not block & keep:
                    continue
                trial = keep - block
                if not trial:
                    continue
                r = solve(rows, nvar, keep=sorted(trial))
                nsolve += 1
                if r.status == 2:
                    keep = trial
                    changed = True
        if verbose:
            print('    after block %-4d: %d rows (%d solves)'
                  % (blk, len(keep), nsolve), flush=True)
    # stage 3: single-row filter
    for i in sorted(keep):
        trial = keep - {i}
        r = solve(rows, nvar, keep=sorted(trial))
        nsolve += 1
        if r.status == 2:
            keep = trial
    cert = [dict(group=rows[i][0], label=rows[i][1],
                 coefs={str(k): v for k, v in rows[i][2].items()},
                 rhs=rows[i][3]) for i in sorted(keep)]
    return cert, dropped_groups, nsolve, sorted(keep)


def certify(rows, nvar, keep, obj):
    """Re-solve min F(K,0) over the IIS rows with the objective cut removed.
    The value is the bound the certificate proves on its own, and the dual
    multipliers are the Farkas combination that yields it."""
    sub = [i for i in keep if rows[i][0] != 'objcut']
    res = solve(rows, nvar, obj=obj, keep=sub)
    lam = None
    if res.status == 0 and getattr(res, 'ineqlin', None) is not None:
        lam = [float(v) for v in res.ineqlin.marginals]
    return (int(res.status), None if res.status != 0 else float(res.fun),
            [dict(group=rows[i][0], label=rows[i][1], rhs=rows[i][3],
                  mult=None if lam is None else -lam[j])
             for j, i in enumerate(sub)])


# --------------------------------------------------------------------------
def L_K(K, eta):
    return 1.0 - (1.0 - 1.0 / (eta * K)) ** K


def sweep(variants=('spec', 'capped'), store_tables=True):
    out = []
    bandcache = {}
    for K in KS:
        for m in NMULTS:
            n = m * K
            for c in CS:
                for kind in BANDS:
                    key = (K, n, c, kind)
                    if key not in bandcache:
                        t0 = time.time()
                        bandcache[key] = get_band(K, n, c, kind)
                        if time.time() - t0 > 5:
                            print('  band %s took %.1fs' % (str(key), time.time() - t0))
                    B, binfo = bandcache[key]
                    st = band_stats(K, n, B)
                    for eta in ETAS:
                        for variant in variants:
                            t0 = time.time()
                            rows, nvar, obj, idx = build(K, n, eta, B, variant)
                            res = solve(rows, nvar, obj=obj)
                            rec = dict(K=K, n=n, nmult=m, c=c, eta=eta,
                                       band=kind, variant=variant,
                                       nrows=len(rows), nvar=nvar,
                                       band_stats=st,
                                       secs=round(time.time() - t0, 2),
                                       status=int(res.status),
                                       status_str=res.message.split('.')[0])
                            rec['feasible'] = bool(res.status == 0)
                            if res.status == 0:
                                v = float(res.fun)
                                rec['value'] = v
                                rec['L_K'] = L_K(K, eta)
                                rec['one_over_eta'] = 1.0 / eta
                                rec['limit_1_minus_exp'] = 1.0 - math.exp(-1.0 / eta)
                                rec['value_minus_L_K'] = v - rec['L_K']
                                rec['value_minus_1_over_eta'] = v - 1.0 / eta
                                F, G, H = extract(res, K, n, idx)
                                worst, where = violation(rows, res.x)
                                rec['max_violation'] = worst
                                rec['worst_row'] = None if where is None else list(where)
                                rec['j5'] = j5_check(G, K, n, B)
                                rec['j5_all_equal'] = all(d['equal'] for d in rec['j5'])
                                if store_tables and m == 16:
                                    rec['tables'] = dict(F=F, G=G, Ghat=H)
                            print('  K=%d n=%-4d c=%d eta=%-4s %-5s %-6s  %-10s %s  (%.1fs)'
                                  % (K, n, c, eta, kind, variant,
                                     'FEASIBLE' if rec['feasible'] else 'INFEASIBLE',
                                     ('%.9f' % rec['value']) if rec['feasible'] else '',
                                     rec['secs']), flush=True)
                            out.append(rec)
    return out


def band_width_table(K, n, c):
    """per-level band width, both definitions, for the md."""
    Bp, ip = band_proxy(K, n, c)
    Bh, ih = band_hyper(K, n, c)
    rowsout = []
    for s in range(n + 1):
        lo, hi = yrange(K, n, s)
        rowsout.append(dict(s=s, ylo=lo, yhi=hi,
                            mu=s * K / n,
                            proxy=Bp[s], hyper=Bh[s],
                            proxy_full=len(Bp[s]) == hi - lo + 1,
                            hyper_full=len(Bh[s]) == hi - lo + 1))
    return rowsout, ip['t']


EXTRA_N = [(6, 768, 2, 1.5, 'hyper', 'spec'), (6, 1152, 2, 1.5, 'hyper', 'spec')]


def extra_probe():
    """The only two sweep cells whose value is not 1/eta are K=6, eta=1.5, c=2
    under the hypergeometric band, and their value still moves with n.  Push n
    further to see where it settles."""
    out = []
    for (K, n, c, eta, kind, variant) in EXTRA_N:
        t0 = time.time()
        B, _ = get_band(K, n, c, kind)
        st = band_stats(K, n, B)
        rows, nvar, obj, idx = build(K, n, eta, B, variant)
        r = solve(rows, nvar, obj=obj)
        rec = dict(K=K, n=n, c=c, eta=eta, band=kind, variant=variant,
                   nrows=len(rows), status=int(r.status), band_stats=st,
                   value=float(r.fun) if r.status == 0 else None,
                   one_over_eta=1.0 / eta, L_K=L_K(K, eta),
                   secs=round(time.time() - t0, 1))
        print('  extra K=%d n=%d c=%d eta=%s %s  %s  (%.1fs)'
              % (K, n, c, eta, kind,
                 ('%.9f' % rec['value']) if rec['value'] is not None else 'INFEAS',
                 rec['secs']), flush=True)
        out.append(rec)
    return out


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    payload = {}
    if mode in ('sweep', 'all'):
        print('== sweep ==', flush=True)
        t0 = time.time()
        payload['sweep'] = sweep()
        print('sweep done in %.1fs' % (time.time() - t0))
        payload['band_width_sample'] = {
            '%d_%d_%d' % (K, n, c): band_width_table(K, n, c)[0]
            for (K, n, c) in [(3, 48, 2), (4, 64, 2), (6, 96, 2), (6, 96, 3)]}
        print('== extra large-n probe ==', flush=True)
        payload['extra_n'] = extra_probe()
        with open(os.path.join(HERE, 'P0_band_lp.json'), 'w') as fh:
            json.dump(payload, fh, indent=1)
        print('wrote P0_band_lp.json')
    if mode == 'extra':
        path = os.path.join(HERE, 'P0_band_lp.json')
        payload = json.load(open(path))
        payload['extra_n'] = extra_probe()
        with open(path, 'w') as fh:
            json.dump(payload, fh, indent=1)
        print('updated P0_band_lp.json with extra_n')
    if mode in ('iis', 'all'):
        print('== IIS (deletion filter) ==', flush=True)
        certs = []
        for (K, m, c, eta, kind, variant) in IIS_CONFIGS:
            n = m * K
            B, _ = get_band(K, n, c, kind)
            rows0, nvar, obj, idx = build(K, n, eta, B, variant)
            r0 = solve(rows0, nvar, obj=obj)
            if r0.status != 0:
                vstar, cut = None, None
                rows = rows0
            else:
                vstar = float(r0.fun)
                cut = vstar - 1e-3
                rows, nvar, obj, idx = build(K, n, eta, B, variant, objcut=cut)
            print('  IIS for K=%d n=%d c=%d eta=%s %s %s (%d rows, v*=%s, cut=%s)'
                  % (K, n, c, eta, kind, variant, len(rows),
                     'infeasible' if vstar is None else '%.9f' % vstar,
                     'none' if cut is None else '%.6f' % cut), flush=True)
            t0 = time.time()
            out = iis(rows, nvar)
            cert, dropped, nsolve, keep = out
            if cert is None:
                print('    system is feasible, no IIS')
                continue
            counts = {}
            for row in cert:
                counts[row['group']] = counts.get(row['group'], 0) + 1
            cst, cval, cmult = certify(rows, nvar, keep, obj)
            print('    IIS size %d %s, groups dropped: %s (%d solves, %.1fs)'
                  % (len(cert), counts, dropped, nsolve, time.time() - t0),
                  flush=True)
            print('    certificate alone proves F(K,0) >= %s  (status %d)'
                  % ('n/a' if cval is None else '%.9f' % cval, cst), flush=True)
            certs.append(dict(K=K, n=n, c=c, eta=eta, band=kind, variant=variant,
                              vstar=vstar, objcut=cut,
                              nrows=len(rows), iis_size=len(cert),
                              iis_group_counts=counts,
                              cert_status=cst, cert_bound=cval,
                              cert_multipliers=cmult,
                              dropped_groups=dropped, n_lp_solves=nsolve,
                              iis=cert, secs=round(time.time() - t0, 1)))
            with open(os.path.join(HERE, 'P0_band_lp_iis.json'), 'w') as fh:
                json.dump(certs, fh, indent=1)
        print('wrote P0_band_lp_iis.json')


if __name__ == '__main__':
    main()
