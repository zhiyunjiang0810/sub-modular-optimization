"""T2: numerical verification of the R9 poly-query hardness candidate.

Question: can the candidate G be extended to the whole lattice so that
(a) on the balanced region G depends only on |S| (equality G(S) = Ghat(|S|) = 1 - a^{|S|},
    a = 1 - 1/(eta*K), i.e. c = eta), and
(b) globally every single-element marginal stays in the inflated error band
    Delta_e G in [Delta_e F/(eta_u*s), eta_o*s*Delta_e F],  s = sqrt(1+delta)
    (so the product error is eta*(1+delta)); Delta_e F = 0 forces Delta_e G = 0.

F is fixed to the R9 form: F(x,y) = (1/eta_o) * [1 - a^x (1 - y/K)],
x = |S \\ O|, y = |S cap O|, ground set N = B cup O, |O| = K, |B| = n-K.

Balanced definitions:
  'ysmall' : y <= tau                       (the only case R9 was checked in)
  'true'   : |y - K|S|/n| <= tau            (the real concentration band)

Feasibility is decided by an LP over the unconstrained G(S) variables after
substituting the balanced equalities as constants.  Constant-vs-constant band
requirements are checked analytically first; they give an exact lower bound on
delta, and zero-width conflicts (Delta_e F = 0 but Delta_e G = const != 0)
prove infeasibility at EVERY delta -- these are reported as certificates.

Usage:  python3 results/T2_hardness_lp.py [quick|full|relaxF]
Output: results/T2_table.csv (appended per config), stdout log.
"""
import itertools, json, os, sys, time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
TOL = 1e-9


def counts(n, K):
    """x,y per bitmask; B = bits 0..n-K-1, O = bits n-K..n-1."""
    N = 1 << n
    maskB = (1 << (n - K)) - 1
    x = np.zeros(N, dtype=int); y = np.zeros(N, dtype=int)
    for S in range(N):
        x[S] = bin(S & maskB).count('1')
        y[S] = bin(S >> (n - K)).count('1')
    return x, y


def balanced_mask(n, K, tau, defn, x, y):
    N = 1 << n
    sz = x + y
    if defn == 'ysmall':
        return y <= tau
    elif defn == 'true':
        return np.abs(y - K * sz / n) <= tau + 1e-12
    raise ValueError(defn)


def analyze(n, K, eta, tau, defn, split, delta_grid=None, verbose=False):
    """Return dict with feasibility info for one config."""
    if split == 'sqrt':
        eta_u, eta_o = eta ** 0.5, eta ** 0.5
    elif split == 'u':      # eta_u = eta, eta_o = 1
        eta_u, eta_o = eta, 1.0
    else:
        raise ValueError(split)
    a = 1 - 1 / (eta * K)
    x, y = counts(n, K)
    N = 1 << n
    F = (1.0 / eta_o) * (1 - a ** x * (1 - y / K))
    Ghat = 1 - a ** (x + y).astype(float)          # candidate value 1 - a^{|S|}
    bal = balanced_mask(n, K, tau, defn, x, y)

    # --- step 3 checks: OPT is O; ratio of best B-K-set to F(O) ----------
    maskB = (1 << (n - K)) - 1
    Omask = ((1 << n) - 1) ^ maskB
    FO = F[Omask]
    bestK = max((F[S], S) for S in range(N) if bin(S).count('1') <= K)
    opt_is_O = abs(bestK[0] - FO) < TOL and y[bestK[1]] == K
    TB = (1 << K) - 1                               # K-subset of B
    ratio_B = F[TB] / FO
    LK = 1 - (1 - 1 / (eta * K)) ** K

    # --- collect marginal pairs -----------------------------------------
    # classify each (S,e): dF = F[S|e]-F[S] (constant);
    # G side: both balanced (constant), one balanced, none balanced.
    cc_smin = 0.0          # minimal product-inflation (1+delta) needed by const-const pairs
    cc_worst = None
    hard_conflicts = []    # dF == 0 but constant dG != 0  -> infeasible forever
    rows = []              # (dict coef -> val, kind, rhs_pair) built later per delta
    pair_list = []         # (S, e, dF, gS_const_or_None, gSe_const_or_None)
    for S in range(N):
        for e in range(n):
            if S >> e & 1:
                continue
            Se = S | 1 << e
            dF = F[Se] - F[S]
            gS = Ghat[S] if bal[S] else None
            gSe = Ghat[Se] if bal[Se] else None
            if gS is not None and gSe is not None:
                dG = gSe - gS
                if dF < TOL:
                    if abs(dG) > 1e-7:
                        hard_conflicts.append((S, e, float(dF), float(dG)))
                    continue
                # need dF/(eta_u*s) <= dG <= eta_o*s*dF  with s = sqrt(1+delta)
                if dG <= TOL:
                    hard_conflicts.append((S, e, float(dF), float(dG)))
                    continue
                s_lo = dF / (eta_u * dG)        # need s >= s_lo  (lower band)
                s_up = dG / (eta_o * dF)        # need s >= s_up  (upper band)
                need = max(s_lo, s_up, 1.0)
                if need > cc_smin:
                    cc_smin, cc_worst = need, (S, e, float(dF), float(dG))
            else:
                pair_list.append((S, e, float(dF), gS, gSe))

    delta_cc = cc_smin ** 2 - 1 if cc_smin > 1 else 0.0

    res = dict(n=n, K=K, eta=eta, tau=tau, defn=defn, split=split,
               a=a, opt_is_O=bool(opt_is_O), ratio_B=float(ratio_B), LK=float(LK),
               n_hard_conflicts=len(hard_conflicts),
               hard_examples=[dict(S=int(S), e=int(e), size=int(bin(S).count('1')),
                                   xy=(int(x[S]), int(y[S])), dF=dF, dG=dG)
                              for S, e, dF, dG in hard_conflicts[:3]],
               delta_cc=float(delta_cc))
    if hard_conflicts:
        res.update(status='INFEASIBLE-ANY-DELTA', min_delta=None, leak=None)
        return res

    # --- LP feasibility for the variable part at given delta -------------
    var_ids = {S: i for i, S in enumerate(np.nonzero(~bal)[0])}
    nv = len(var_ids)

    def feasible(delta):
        s = (1 + delta) ** 0.5
        lo_c, up_c = 1 / (eta_u * s), eta_o * s
        rows_i, cols, vals, b = [], [], [], []
        eq_rows_i, eq_cols, eq_vals, eq_b = [], [], [], []
        r = ri = 0
        for S, e, dF, gS, gSe in pair_list:
            Se = S | 1 << e
            # represent dG = (gSe or var) - (gS or var)
            ent = []          # (col, coef) for dG
            const = 0.0
            if gSe is None:
                ent.append((var_ids[Se], 1.0))
            else:
                const += gSe
            if gS is None:
                ent.append((var_ids[S], -1.0))
            else:
                const -= gS
            if dF < TOL:
                # force dG = 0
                for c, v in ent:
                    eq_rows_i.append(ri); eq_cols.append(c); eq_vals.append(v)
                eq_b.append(-const); ri += 1
                continue
            # dG <= up_c*dF   ->  ent <= up_c*dF - const
            for c, v in ent:
                rows_i.append(r); cols.append(c); vals.append(v)
            b.append(up_c * dF - const); r += 1
            # dG >= lo_c*dF   ->  -ent <= const - lo_c*dF
            for c, v in ent:
                rows_i.append(r); cols.append(c); vals.append(-v)
            b.append(const - lo_c * dF); r += 1
        A = coo_matrix((vals, (rows_i, cols)), shape=(r, nv)).tocsr()
        kw = {}
        if ri:
            kw['A_eq'] = coo_matrix((eq_vals, (eq_rows_i, eq_cols)),
                                    shape=(ri, nv)).tocsr()
            kw['b_eq'] = np.array(eq_b)
        out = linprog(np.zeros(nv), A_ub=A, b_ub=np.array(b),
                      bounds=[(None, None)] * nv, method='highs', **kw)
        return (out.status == 0), out

    # bisection on delta
    lo = delta_cc
    ok, sol = feasible(lo)
    if ok:
        min_delta, best = lo, sol
    else:
        hi = max(2 * lo, 0.5)
        ok_hi, sol_hi = feasible(hi)
        tries = 0
        while not ok_hi and tries < 12:
            hi *= 2; tries += 1
            ok_hi, sol_hi = feasible(hi)
        if not ok_hi:
            res.update(status='INFEASIBLE-UP-TO-DELTA-%g' % hi, min_delta=None, leak=None)
            return res
        best = sol_hi
        for _ in range(30):
            mid = 0.5 * (lo + hi)
            ok_m, sol_m = feasible(mid)
            if ok_m:
                hi, best = mid, sol_m
            else:
                lo = mid
            if hi - lo < 1e-6 * max(1.0, hi):
                break
        min_delta = hi
    # --- leak check on the found solution -------------------------------
    Gsol = np.array(Ghat)          # start from constants
    for S, i in var_ids.items():
        Gsol[S] = best.x[i]
    sz = x + y
    true_bal = balanced_mask(n, K, tau, 'true', x, y)
    leak = 0.0
    for s_ in range(n + 1):
        idx = np.nonzero((sz == s_) & true_bal)[0]
        if len(idx) > 1:
            leak = max(leak, float(Gsol[idx].max() - Gsol[idx].min()))
    res.update(status='FEASIBLE', min_delta=float(min_delta), leak=leak)
    return res


def explicit_delta(n, K, eta, tau, split):
    """Error inflation needed by the explicit R9 candidate G (ysmall def)."""
    if split == 'sqrt':
        eta_u, eta_o = eta ** 0.5, eta ** 0.5
    else:
        eta_u, eta_o = eta, 1.0
    a = 1 - 1 / (eta * K)
    x, y = counts(n, K)
    N = 1 << n
    F = (1.0 / eta_o) * (1 - a ** x * (1 - y / K))
    G = np.where(y <= tau, 1 - a ** (x + y).astype(float),
                 1 - a ** (x + tau).astype(float) * (K - y) / (K - tau))
    smin, worst = 1.0, None
    for S in range(N):
        for e in range(n):
            if S >> e & 1:
                continue
            Se = S | 1 << e
            dF, dG = F[Se] - F[S], G[Se] - G[S]
            if dF < TOL:
                if abs(dG) > 1e-7:
                    return None, ('zero-dF conflict', int(S), int(e), float(dG))
                continue
            if dG <= TOL:
                return None, ('nonpositive dG', int(S), int(e), float(dG))
            need = max(dF / (eta_u * dG), dG / (eta_o * dF), 1.0)
            if need > smin:
                smin, worst = need, (int(S), int(e))
    return smin ** 2 - 1, worst


def run(configs, csv_path):
    new = not os.path.exists(csv_path)
    with open(csv_path, 'a') as fh:
        if new:
            fh.write('n,K,tau,eta,split,balanced_def,status,min_delta,delta_cc,'
                     'delta_explicit,ratio_B,LK,opt_is_O,n_hard_conflicts,leak\n')
        for (n, K, eta, tau, defn, split) in configs:
            t0 = time.time()
            r = analyze(n, K, eta, tau, defn, split)
            dexp = ''
            if defn == 'ysmall':
                de, _ = explicit_delta(n, K, eta, tau, split)
                dexp = '%.6g' % de if de is not None else 'conflict'
            md = '%.6g' % r['min_delta'] if r['min_delta'] is not None else ''
            leak = '%.3g' % r['leak'] if r.get('leak') is not None else ''
            fh.write(f"{n},{K},{tau},{eta},{split},{defn},{r['status']},{md},"
                     f"{r['delta_cc']:.6g},{dexp},{r['ratio_B']:.6f},{r['LK']:.6f},"
                     f"{r['opt_is_O']},{r['n_hard_conflicts']},{leak}\n")
            fh.flush()
            print(f"[{time.time()-t0:6.1f}s] n={n} K={K} eta={eta} tau={tau} "
                  f"{defn:6s} {split:4s} -> {r['status']} min_delta={md} "
                  f"delta_cc={r['delta_cc']:.4g} explicit={dexp} hard={r['n_hard_conflicts']} "
                  f"leak={leak} ratio_B={r['ratio_B']:.4f} (LK={r['LK']:.4f}) optO={r['opt_is_O']}",
                  flush=True)
            if r['n_hard_conflicts']:
                print('   certificate examples:', json.dumps(r['hard_examples']), flush=True)


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'quick'
    csv_path = os.path.join(HERE, 'T2_table.csv')
    NKs = [(8, 3), (10, 3), (10, 4), (12, 4)]
    etas = [1.5, 2.0, 3.0]
    taus = [1, 2]
    if mode == 'quick':
        cfgs = [(8, 3, e, t, d, 'sqrt') for e in etas for t in taus
                for d in ('ysmall', 'true')]
    elif mode == 'full':
        cfgs = [(n, K, e, t, d, s) for (n, K) in NKs for e in etas for t in taus
                for d in ('ysmall', 'true') for s in ('sqrt', 'u')
                if not (n == 12 and s == 'u')]      # keep n=12 to sqrt split (time)
    else:
        raise SystemExit('mode quick|full')
    run(cfgs, csv_path)
