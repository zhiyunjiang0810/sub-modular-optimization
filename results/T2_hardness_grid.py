"""T2 (continued): symmetrized (x,y)-grid version of the hardness LPs.

Justification for the reduction: every constraint class (balanced equality,
single-element error band, monotonicity, submodularity, F(O)=1, OPT
normalization) is covariant under permutations within B and within O, and all
constraints are linear, so averaging any feasible solution over the group
yields a feasible solution that depends on S only through (x,y) = (|S cap B|,
|S cap O|).  Hence the full-lattice LP is feasible iff the grid LP is
feasible, and (for the relaxed-F problem, restricted to symmetric instances)
objectives agree.  Cross-checked against the full-lattice LP of
T2_hardness_lp.py on (n,K) in {(8,3),(10,3),(10,4),(12,4)} -- see
T2_grid_crosscheck output.

Modes:
  fixedF : R9 candidate F fixed; min feasible delta for the G-extension.
  relaxF : delta = 0, F(x,y) becomes a variable (monotone submodular,
           F(0,0)=0, F(0,K)=1, F <= 1 on x+y <= K); G symmetric on the
           balanced region; objective min F(K,0).  This estimates the best
           constant the R9 technique can prove once F is allowed to adapt.

Usage: python3 results/T2_hardness_grid.py crosscheck|fixedF|relaxF
Outputs: results/T2_grid_fixedF.csv, results/T2_grid_relaxF.csv
"""
import os, sys, time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
TOL = 1e-9


def balanced_grid(n, K, tau, defn):
    """boolean (n-K+1) x (K+1) array over (x,y)."""
    xs = np.arange(n - K + 1)[:, None]
    ys = np.arange(K + 1)[None, :]
    sz = xs + ys
    if defn == 'ysmall':
        return np.broadcast_to(ys <= tau, (n - K + 1, K + 1)).copy()
    if defn == 'true':
        return np.abs(ys - K * sz / n) <= tau + 1e-12
    raise ValueError(defn)


# ---------------------------------------------------------------- fixed F --
def fixedF_min_delta(n, K, eta, tau, defn, split='sqrt'):
    eta_u, eta_o = ((eta ** 0.5,) * 2) if split == 'sqrt' else (eta, 1.0)
    a = 1 - 1 / (eta * K)
    X, Y = n - K, K
    F = np.zeros((X + 1, Y + 1))
    for x in range(X + 1):
        for y in range(Y + 1):
            F[x, y] = (1 / eta_o) * (1 - a ** x * (1 - y / K))
    bal = balanced_grid(n, K, tau, defn)
    Ghat = lambda s: 1 - a ** s

    # enumerate directed grid edges (x,y)->(x+1,y) ('x') and ->(x,y+1) ('y')
    edges = []
    for x in range(X + 1):
        for y in range(Y + 1):
            if x < X: edges.append((x, y, 'x'))
            if y < Y: edges.append((x, y, 'y'))

    def endpoints(e):
        x, y, d = e
        return (x, y), ((x + 1, y) if d == 'x' else (x, y + 1))

    def dF(e):
        p, q = endpoints(e)
        return F[q] - F[p]

    cc_smin, hard = 1.0, []
    var_edges = []
    for e in edges:
        p, q = endpoints(e)
        if bal[p] and bal[q]:
            dg = Ghat(sum(q)) - Ghat(sum(p))
            df = dF(e)
            if df < TOL:
                if abs(dg) > 1e-7: hard.append((e, df, dg))
                continue
            if dg <= TOL:
                hard.append((e, df, dg)); continue
            cc_smin = max(cc_smin, df / (eta_u * dg), dg / (eta_o * df))
        else:
            var_edges.append(e)
    delta_cc = cc_smin ** 2 - 1
    if hard:
        return dict(status='INFEASIBLE-ANY-DELTA', delta_cc=delta_cc,
                    n_hard=len(hard), hard_example=str(hard[0]), min_delta=None)

    unbal = [(x, y) for x in range(X + 1) for y in range(Y + 1) if not bal[x, y]]
    vid = {p: i for i, p in enumerate(unbal)}
    nv = len(vid)

    def feasible(delta):
        s = (1 + delta) ** 0.5
        lo_c, up_c = 1 / (eta_u * s), eta_o * s
        ri = [[], [], [], []]  # rows, cols, vals, b  (ub);  eq separately
        er = [[], [], [], []]
        r = q_ = 0
        for e in var_edges:
            p, q = endpoints(e)
            ent, const = [], 0.0
            for pt, sgn in ((q, 1.0), (p, -1.0)):
                if bal[pt]: const += sgn * Ghat(sum(pt))
                else: ent.append((vid[pt], sgn))
            df = dF(e)
            if df < TOL:
                for c, v in ent:
                    er[0].append(q_); er[1].append(c); er[2].append(v)
                er[3].append(-const); q_ += 1
                continue
            for c, v in ent:
                ri[0].append(r); ri[1].append(c); ri[2].append(v)
            ri[3].append(up_c * df - const); r += 1
            for c, v in ent:
                ri[0].append(r); ri[1].append(c); ri[2].append(-v)
            ri[3].append(const - lo_c * df); r += 1
        A = coo_matrix((ri[2], (ri[0], ri[1])), shape=(r, nv)).tocsr()
        kw = {}
        if q_:
            kw['A_eq'] = coo_matrix((er[2], (er[0], er[1])), shape=(q_, nv)).tocsr()
            kw['b_eq'] = np.array(er[3])
        out = linprog(np.zeros(nv), A_ub=A, b_ub=np.array(ri[3]),
                      bounds=[(None, None)] * nv, method='highs', **kw)
        return out.status == 0

    lo = delta_cc
    if feasible(lo):
        return dict(status='FEASIBLE', min_delta=lo, delta_cc=delta_cc, n_hard=0)
    hi = max(2 * lo, 0.5)
    tries = 0
    while not feasible(hi) and tries < 12:
        hi *= 2; tries += 1
    if tries >= 12:
        return dict(status='INFEASIBLE-UP-TO-%g' % hi, min_delta=None,
                    delta_cc=delta_cc, n_hard=0)
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if feasible(mid): hi = mid
        else: lo = mid
        if hi - lo < 1e-7 * max(1.0, hi): break
    return dict(status='FEASIBLE', min_delta=hi, delta_cc=delta_cc, n_hard=0)


# --------------------------------------------------------------- relaxed F --
def relaxF_min_ratio(n, K, eta, tau, defn, split='sqrt', return_F=False):
    """delta = 0 band; F variable; returns min F(K,0) with F(0,K)=1."""
    eta_u, eta_o = ((eta ** 0.5,) * 2) if split == 'sqrt' else (eta, 1.0)
    X, Y = n - K, K
    bal = balanced_grid(n, K, tau, defn)
    nF = (X + 1) * (Y + 1)
    fid = lambda x, y: x * (Y + 1) + y
    gh0 = nF                      # Ghat_s, s = 0..n
    unbal = [(x, y) for x in range(X + 1) for y in range(Y + 1) if not bal[x, y]]
    gv0 = nF + n + 1
    gvid = {p: gv0 + i for i, p in enumerate(unbal)}
    nv = gv0 + len(unbal)

    def gref(p):
        return (gh0 + p[0] + p[1]) if bal[p] else gvid[p]

    R, C, V, b = [], [], [], []
    r = 0
    def ub(coefs, rhs=0.0):
        nonlocal r
        for c, v in coefs:
            R.append(r); C.append(c); V.append(v)
        b.append(rhs); r += 1

    eR, eC, eV, eb = [], [], [], []
    q_ = 0
    def eq(coefs, rhs=0.0):
        nonlocal q_
        for c, v in coefs:
            eR.append(q_); eC.append(c); eV.append(v)
        eb.append(rhs); q_ += 1

    edges = []
    for x in range(X + 1):
        for y in range(Y + 1):
            if x < X: edges.append(((x, y), (x + 1, y), 'x'))
            if y < Y: edges.append(((x, y), (x, y + 1), 'y'))
    # F monotone + error band
    for p, q, d in edges:
        ub([(fid(*p), 1.0), (fid(*q), -1.0)])                    # dF >= 0
        gq, gp = gref(q), gref(p)
        # dG <= eta_o dF  ->  gq - gp - eta_o (Fq - Fp) <= 0
        ub([(gq, 1.0), (gp, -1.0), (fid(*q), -eta_o), (fid(*p), eta_o)])
        # dG >= dF/eta_u  ->  (Fq-Fp)/eta_u - (gq-gp) <= 0
        ub([(fid(*q), 1 / eta_u), (fid(*p), -1 / eta_u), (gq, -1.0), (gp, 1.0)])
    # F submodular: dF at p >= dF at shifted p, for both directions of shift
    for p, q, d in edges:
        for sh in ('x', 'y'):
            px = (p[0] + (sh == 'x'), p[1] + (sh == 'y'))
            qx = (q[0] + (sh == 'x'), q[1] + (sh == 'y'))
            if px[0] > X or px[1] > Y or qx[0] > X or qx[1] > Y:
                continue
            # F[qx]-F[px] - (F[q]-F[p]) <= 0
            ub([(fid(*qx), 1.0), (fid(*px), -1.0), (fid(*q), -1.0), (fid(*p), 1.0)])
    # normalizations
    eq([(fid(0, 0), 1.0)], 0.0)
    eq([(fid(0, K), 1.0)], 1.0)
    eq([(gh0, 1.0)], 0.0)                       # Ghat_0 = 0 (f~ of empty set)
    for x in range(X + 1):
        for y in range(Y + 1):
            if 0 < x + y <= K and not (x == 0 and y == K):
                ub([(fid(x, y), 1.0)], 1.0)     # OPT = O
    obj = np.zeros(nv); obj[fid(K, 0)] = 1.0
    A_ub = coo_matrix((V, (R, C)), shape=(r, nv)).tocsr()
    A_eq = coo_matrix((eV, (eR, eC)), shape=(q_, nv)).tocsr()
    out = linprog(obj, A_ub=A_ub, b_ub=np.array(b), A_eq=A_eq, b_eq=np.array(eb),
                  bounds=[(None, None)] * nv, method='highs')
    if out.status != 0:
        return dict(status='LP-STATUS-%d' % out.status, ratio=None)
    # also report best balanced K-set value on the solution (outputs with y>0)
    Fsol = out.x[:nF].reshape(X + 1, Y + 1)
    ymax_out = min(Y, tau if defn == 'ysmall' else int(K * K / n + tau))
    alt = max(Fsol[K - y, y] for y in range(0, ymax_out + 1) if K - y <= X)
    res = dict(status='OK', ratio=float(out.fun), best_balanced_output=float(alt))
    if return_F:
        res['F'] = Fsol.tolist()
        res['Ghat'] = out.x[gh0:gh0 + n + 1].tolist()
    return res


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'crosscheck'
    if mode == 'crosscheck':
        # must reproduce the full-lattice min_delta values from T2_table.csv
        expect = {(8, 3, 1, 1.5): 0.361111, (8, 3, 2, 1.5): 2.29355,
                  (10, 4, 1, 2.0): 0.361111, (12, 4, 2, 3.0): 1.82427,
                  (10, 3, 1, 3.0): 0.777778, (12, 4, 1, 1.5): 0.234568}
        ok = True
        for (n, K, tau, eta), want in expect.items():
            r = fixedF_min_delta(n, K, eta, tau, 'ysmall')
            good = r['min_delta'] is not None and abs(r['min_delta'] - want) < 1e-4
            ok &= good
            print(f"crosscheck n={n} K={K} tau={tau} eta={eta}: grid={r['min_delta']}"
                  f" lattice={want} {'OK' if good else 'MISMATCH'}")
            rt = fixedF_min_delta(n, K, eta, tau, 'true')
            print(f"   true-def: {rt['status']} (lattice: INFEASIBLE-ANY-DELTA)"
                  f" {'OK' if 'INFEASIBLE' in rt['status'] else 'MISMATCH'}")
            ok &= 'INFEASIBLE' in rt['status']
        print('CROSSCHECK', 'PASS' if ok else 'FAIL')
        sys.exit(0 if ok else 1)

    if mode == 'fixedF':
        path = os.path.join(HERE, 'T2_grid_fixedF.csv')
        with open(path, 'w') as fh:
            fh.write('n,K,tau,eta,defn,status,min_delta,delta_cc,formula\n')
            for K in [3, 4, 6, 8, 12, 16, 24, 32]:
                n = 4 * K
                for eta in [1.5, 2.0, 3.0]:
                    a = 1 - 1 / (eta * K)
                    for tau in [1, 2]:
                        for defn in ['ysmall', 'true']:
                            t0 = time.time()
                            r = fixedF_min_delta(n, K, eta, tau, defn)
                            formula = (a ** tau * K / (K - tau)) ** 2 - 1
                            md = '%.6g' % r['min_delta'] if r['min_delta'] is not None else ''
                            fh.write(f"{n},{K},{tau},{eta},{defn},{r['status']},{md},"
                                     f"{r['delta_cc']:.6g},{formula:.6g}\n")
                            fh.flush()
                            print(f"[{time.time()-t0:5.1f}s] K={K} n={n} eta={eta} tau={tau} "
                                  f"{defn}: {r['status']} min_delta={md} formula={formula:.6g}",
                                  flush=True)
        return

    if mode == 'relaxF':
        path = os.path.join(HERE, 'T2_grid_relaxF.csv')
        with open(path, 'w') as fh:
            fh.write('n,K,tau,eta,defn,status,ratio,best_balanced_output,'
                     'one_minus_exp,LK,UK\n')
            for K in [3, 4, 6, 8, 12, 16, 24]:
                for mult in [4, 8]:
                    n = mult * K
                    for eta in [1.5, 2.0, 3.0]:
                        lim = 1 - np.exp(-1 / eta)
                        LK = 1 - (1 - 1 / (eta * K)) ** K
                        UK = 1 - (1 - 1 / (eta * (K - 1) + 1)) ** K
                        for tau in [1, 2]:
                            for defn in ['ysmall', 'true']:
                                t0 = time.time()
                                r = relaxF_min_ratio(n, K, eta, tau, defn)
                                rat = '%.6f' % r['ratio'] if r['ratio'] is not None else ''
                                bb = ('%.6f' % r.get('best_balanced_output')
                                      if r.get('best_balanced_output') is not None else '')
                                fh.write(f"{n},{K},{tau},{eta},{defn},{r['status']},{rat},"
                                         f"{bb},{lim:.6f},{LK:.6f},{UK:.6f}\n")
                                fh.flush()
                                print(f"[{time.time()-t0:5.1f}s] K={K} n={n} eta={eta} tau={tau} "
                                      f"{defn}: ratio={rat} bal_out={bb} "
                                      f"(1-e^-1/eta={lim:.4f} LK={LK:.4f} UK={UK:.4f})",
                                      flush=True)
        return
    raise SystemExit('mode crosscheck|fixedF|relaxF')


if __name__ == '__main__':
    main()
