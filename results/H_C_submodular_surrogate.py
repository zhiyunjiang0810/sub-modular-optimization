"""
H-C: certificate structure behind rho_K^sub(eta) = min_m W_m (the F4 conjecture).

Background: results/F4_submodular_ftilde.md solved the full-lattice factor-revealing
LP with submodularity imposed on the surrogate ftilde as well, and read off the
closed-form candidate

    r = 1 - 1/K,   W_m(K, eta) = (K - m r^m) / (K (1 + (eta-1) r^m)),
    rho_K^sub(eta) = min_{0 <= m <= K-1} W_m(K, eta)          [CONJECTURE]

matching 76/76 LP points.  This script follows the N1 playbook (dual certificate for
min_j V_j) and reports what it found.

Parts
  A  reproduce the two headline LP values (19/33 at K=3,eta=3/2; 23/50 at K=4,eta=2)
  B  full-lattice LP on an eta grid crossing the segment boundaries of min_m W_m
  C  dual multipliers of the full-lattice LP, symmetrised over permutations of O,
     rationalised over Q + Q/sqrt(eta); per-family support tables
  D  candidate REDUCED LP for the submodular-surrogate model built from the natural
     valid inequalities (ftilde submodular along the path, ftilde coverage, band
     chain).  NEGATIVE RESULT: its value is exactly min_j V_j, i.e. those
     inequalities do not see the extra strength.  This is the 卡点.
  E  symbolic derivation: the tight-constraint system read off the LP optimum implies
     objective = W_m, for symbolic K, m, eta_u, eta_o.               [VERIFIED-SYMBOLIC]
  F  explicit (f, ftilde) family with SUBMODULAR ftilde attaining W_m, for every
     K, m, eta and every split eta = eta_u * eta_o; checked with the F4 verifier.
                                                                    [VERIFIED-LP]

Usage
    python3 results/H_C_submodular_surrogate.py            # everything (~6 min)
    python3 results/H_C_submodular_surrogate.py --parts ADF
    python3 results/H_C_submodular_surrogate.py --quick    # smaller grids

Outputs
    results/H_C_submodular_surrogate.json    all numbers, dual tables, PASS/FAIL
Exit code 0 iff every oracle check in the run passed.
"""
import argparse
import itertools
import json
import os
import sys
import time
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix, coo_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'code'))

from F4_submodular_ftilde import verify_instance  # noqa: E402  (unmodified)

RESULTS = {}
CHECKS = []


def record(name, ok, info=None):
    CHECKS.append({'check': name, 'pass': bool(ok), 'info': info})
    print(f"   [{'PASS' if ok else 'FAIL'}] {name}" + (f"  {info}" if info else ""))
    return ok


# ---------------------------------------------------------------------------
# closed forms
# ---------------------------------------------------------------------------
def Vj(K, j, eta):
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return 1 - q ** j * (1 - (K - j) / (K * eta))


def min_V(K, eta):
    return min((Vj(K, j, eta), j) for j in range(K))


def Wm(K, m, eta):
    r = 1 - 1.0 / K
    rm = r ** m
    return (K - m * rm) / (K * (1 + (eta - 1) * rm))


def min_W(K, eta):
    return min((Wm(K, m, eta), m) for m in range(K))


def UK(K, eta):
    return 1 - (1 - 1 / (eta * (K - 1) + 1)) ** K


# ---------------------------------------------------------------------------
# Full-lattice LP.  Row construction copied from results/F4_submodular_ftilde.py
# (itself a verbatim copy of code/worst_case_lp.py plus the submod_g block);
# the only change here is that every row carries its meta data so the dual can
# be read family by family.
# ---------------------------------------------------------------------------
def build_rows(n, K, eta_u, eta_o, g_submod=True):
    N = 1 << n
    nv = 2 * N
    F = lambda S: S
    G = lambda S: N + S
    rows_ub, b_ub, tags = [], [], []

    def add(coefs, tag, meta=None, rhs=0.0):
        rows_ub.append(coefs); b_ub.append(rhs); tags.append((tag, meta))

    for S in range(N):                                   # (1) f monotone
        for e in range(n):
            if not S >> e & 1:
                add({F(S): 1, F(S | 1 << e): -1}, "mono_f", (S, e))
    for S in range(N):                                   # (2) f submodular
        for e in range(n):
            if S >> e & 1:
                continue
            for e2 in range(n):
                if e2 == e or S >> e2 & 1:
                    continue
                T = S | 1 << e2
                c = {}
                for k, v in ((F(T | 1 << e), 1), (F(T), -1),
                             (F(S | 1 << e), -1), (F(S), 1)):
                    c[k] = c.get(k, 0) + v
                add(c, "submod_f", (S, e, e2))
    if g_submod:                                         # (2b) ftilde submodular
        for S in range(N):
            for e in range(n):
                if S >> e & 1:
                    continue
                for e2 in range(n):
                    if e2 == e or S >> e2 & 1:
                        continue
                    T = S | 1 << e2
                    c = {}
                    for k, v in ((G(T | 1 << e), 1), (G(T), -1),
                                 (G(S | 1 << e), -1), (G(S), 1)):
                        c[k] = c.get(k, 0) + v
                    add(c, "submod_g", (S, e, e2))
    for A in range(N):                                   # (3) single-element band
        comp = (N - 1) ^ A
        for B in [1 << e for e in range(n) if comp >> e & 1]:
            AB = A | B
            c = {}
            for k, v in ((F(AB), 1 / eta_u), (F(A), -1 / eta_u),
                         (G(AB), -1), (G(A), 1)):
                c[k] = c.get(k, 0) + v
            add(c, "band_lo", (A, B))
            c = {}
            for k, v in ((G(AB), 1), (G(A), -1),
                         (F(AB), -eta_o), (F(A), eta_o)):
                c[k] = c.get(k, 0) + v
            add(c, "band_hi", (A, B))
    for t in range(K):                                   # (4) greedy path
        S = (1 << t) - 1
        for e in range(n):
            if e == t or S >> e & 1:
                continue
            c = {}
            for k, v in ((G(S | 1 << e), 1), (G(S), -1),
                         (G(S | 1 << t), -1), (G(S), 1)):
                c[k] = c.get(k, 0) + v
            add(c, "greedy", (t, e))
    A_ub = lil_matrix((len(rows_ub), nv))
    for i, c in enumerate(rows_ub):
        for k, v in c.items():
            A_ub[i, k] = v
    return A_ub.tocsr(), np.array(b_ub), tags


def solve_lattice(n, K, eta, O, g_submod=True, eu=None, eo=None, cache=None):
    if eu is None:
        eu = eo = eta ** 0.5
    if cache is not None and cache[0] == (n, K, eu, eo, g_submod):
        A_ub, b_ub, tags = cache[1]
    else:
        A_ub, b_ub, tags = build_rows(n, K, eu, eo, g_submod)
        if cache is not None:
            cache[0] = (n, K, eu, eo, g_submod)
            cache[1] = (A_ub, b_ub, tags)
    N = 1 << n
    nv = 2 * N
    obj = np.zeros(nv)
    obj[(1 << K) - 1] = 1.0
    Om = sum(1 << i for i in O)
    A_eq = lil_matrix((3, nv))
    A_eq[0, 0] = 1
    A_eq[1, N] = 1
    A_eq[2, Om] = 1
    res = linprog(obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq.tocsr(), b_eq=[0, 0, 1],
                  bounds=[(None, None)] * nv, method="highs")
    return res, A_ub, b_ub, tags


def lattice_value(n, K, eta, g_submod=True, all_O=True, cache=None):
    Os = (list(itertools.combinations(range(n), K)) if all_O
          else [tuple(range(K, 2 * K))])
    best = (np.inf, None)
    for O in Os:
        res, _, _, _ = solve_lattice(n, K, eta, O, g_submod, cache=cache)
        if res.status == 0 and res.fun < best[0] - 1e-13:
            best = (float(res.fun), O)
    return best


# ---------------------------------------------------------------------------
# Part A: reproduce the F4 headline numbers
# ---------------------------------------------------------------------------
def part_A():
    print("\n=== Part A: reproduce the F4 headline LP values ===")
    out = []
    cache = [None, None]
    for K, eta, target, all_O in [(3, 1.5, Fraction(19, 33), True),
                                  (4, 2.0, Fraction(23, 50), False)]:
        t0 = time.time()
        val, O = lattice_value(2 * K, K, eta, True, all_O, cache)
        w, m = min_W(K, eta)
        ok = abs(val - float(target)) < 1e-9 and abs(val - w) < 1e-9
        out.append({'K': K, 'eta': eta, 'value': val, 'target': str(target),
                    'min_m_Wm': w, 'argmin_m': m, 'O': str(O),
                    'all_O_enumerated': all_O, 'seconds': round(time.time() - t0, 1)})
        record(f"A: K={K} eta={eta} sub-LP = {target}", ok,
               f"value={val:.12f} (min_m W_m={w:.12f}, m*={m}, {time.time()-t0:.1f}s)")
    RESULTS['A_headline'] = out


# ---------------------------------------------------------------------------
# Part B: eta grid crossing the segment boundaries of min_m W_m
# ---------------------------------------------------------------------------
def segment_boundaries(K):
    """eta where argmin_m W_m switches from m+1 to m (solve W_m = W_{m+1})."""
    from scipy.optimize import brentq
    bs = []
    for m in range(K - 1):
        try:
            bs.append((m, brentq(lambda e: Wm(K, m, e) - Wm(K, m + 1, e), 1.0, 200.0)))
        except ValueError:
            pass
    return bs


def part_B(quick=False):
    print("\n=== Part B: LP on an eta grid crossing the min_m W_m segment boundaries ===")
    rows = []
    cache = [None, None]
    plan = [(2, True), (3, True)] if quick else [(2, True), (3, True), (4, False)]
    for K, all_O in plan:
        bs = segment_boundaries(K)
        etas = []
        for m, e in bs:
            etas += [round(e - 0.05, 6), round(e, 6), round(e + 0.05, 6)]
        etas = sorted(set([e for e in etas if e >= 1.0]))
        for eta in etas:
            t0 = time.time()
            val, O = lattice_value(2 * K, K, eta, True, all_O, cache)
            w, m = min_W(K, eta)
            v, j = min_V(K, eta)
            ok = abs(val - w) < 1e-8
            rows.append({'K': K, 'eta': eta, 'lp_sub': val, 'min_m_Wm': w,
                         'argmin_m': m, 'min_j_Vj': v, 'argmin_j': j,
                         'gap': val - w, 'all_O': all_O,
                         'seconds': round(time.time() - t0, 1)})
            print(f"   K={K} eta={eta:<9} LP={val:.9f}  min_m W_m={w:.9f}"
                  f"  m*={m}  dev={val-w:+.2e}  ({time.time()-t0:.1f}s)")
            sys.stdout.flush()
    worst = max(abs(r['gap']) for r in rows)
    record("B: LP = min_m W_m on all boundary-crossing eta", worst < 1e-8,
           f"{len(rows)} points, max |LP - min_m W_m| = {worst:.2e}")
    RESULTS['B_boundary_grid'] = rows
    RESULTS['B_boundaries'] = {str(K): segment_boundaries(K) for K in [2, 3, 4, 5, 6]}


# ---------------------------------------------------------------------------
# Part C: dual multipliers, symmetrised over permutations of O
# ---------------------------------------------------------------------------
def perm_set(S, n, p):
    T = 0
    for u in range(n):
        if S >> u & 1:
            T |= 1 << p[u]
    return T


def row_key(tag, meta, n, p):
    if tag in ("submod_f", "submod_g"):
        S, e, e2 = meta
        return (tag, perm_set(S, n, p), p[e], p[e2])
    if tag in ("band_lo", "band_hi"):
        A, B = meta
        return (tag, perm_set(A, n, p), perm_set(B, n, p))
    if tag == "greedy":
        t, e = meta
        return (tag, t, p[e])
    S, e = meta
    return (tag, perm_set(S, n, p), p[e])


def lab(e, K):
    return ('b%d' % e) if e < K else ('o%d' % (e - K))


def setstr(S, n, K):
    return "{" + ",".join(lab(u, K) for u in range(n) if S >> u & 1) + "}"


def xy(S, n, K):
    return (bin(S & ((1 << K) - 1)).count('1'), bin(S >> K).count('1'))


def rationalise(v, eta, maxden=5000):
    """Report v in Q, Q/sqrt(eta) or Q*sqrt(eta) when one of them is exact."""
    s = eta ** 0.5
    for scale, name in ((1.0, ""), (s, "/sqrt(eta)"), (1.0 / s, "*sqrt(eta)")):
        fr = Fraction(v * scale).limit_denominator(maxden)
        if abs(float(fr) / scale - v) < 1e-9:
            return f"{fr}{name}"
    return "?"


def Om_of(O):
    return sum(1 << i for i in O)


def part_C(quick=False):
    print("\n=== Part C: dual multipliers of the full-lattice LP (symmetrised over O) ===")
    out = {}
    plan = [(2, 1.5), (3, 1.5), (3, 2.0)] if quick else \
           [(2, 1.5), (2, 2.0), (3, 1.5), (3, 2.0), (4, 1.5), (4, 2.0)]
    for K, eta in plan:
        n = 2 * K
        O = tuple(range(K, 2 * K))
        t0 = time.time()
        res, A_ub, b_ub, tags = solve_lattice(n, K, eta, O, True)
        lam = -np.array(res.ineqlin.marginals)          # lambda >= 0
        idmap = {}
        ident = list(range(n))
        for i, (tg, meta) in enumerate(tags):
            idmap[row_key(tg, meta, n, ident)] = i
        acc = np.zeros_like(lam)
        perms = [list(range(K)) + [K + pi[j] for j in range(K)]
                 for pi in itertools.permutations(range(K))]
        for p in perms:
            for i, (tg, meta) in enumerate(tags):
                acc[idmap[row_key(tg, meta, n, p)]] += lam[i]
        acc /= len(perms)
        # symmetrisation preserves dual feasibility and the dual objective.
        # All inequality right-hand sides are 0 here; the constant sits in the
        # equality block f(O) = 1, whose multiplier is res.eqlin.marginals[2].
        yeq = np.array(res.eqlin.marginals, dtype=float)
        beq = np.array([0.0, 0.0, 1.0])
        dual_obj_raw = float(b_ub.dot(-lam) + beq.dot(yeq))
        dual_obj_sym = float(b_ub.dot(-acc) + beq.dot(yeq))
        # dual feasibility: variables are free, so A' y must equal c exactly
        N = 1 << n
        A_eq_dense = np.zeros((3, 2 * N))
        A_eq_dense[0, 0] = 1.0
        A_eq_dense[1, N] = 1.0
        A_eq_dense[2, Om_of(O)] = 1.0
        cvec = np.zeros(2 * N)
        cvec[(1 << K) - 1] = 1.0
        resid = A_ub.T.dot(-acc) + A_eq_dense.T.dot(yeq) - cvec
        feas = float(np.abs(resid).max())
        sign_ok = float(acc.min())
        entry = {'value': float(res.fun), 'value_frac':
                 str(Fraction(float(res.fun)).limit_denominator(10 ** 7)),
                 'nnz_raw': int((lam > 1e-9).sum()),
                 'nnz_sym': int((acc > 1e-9).sum()),
                 'rows': int(A_ub.shape[0]),
                 'eqlin_marginals': [float(v) for v in res.eqlin.marginals],
                 'families': {}, 'support': {}}
        for i, (tg, meta) in enumerate(tags):
            d = entry['families'].setdefault(tg, {'nnz': 0, 'rows': 0, 'sum': 0.0})
            d['rows'] += 1
            if acc[i] > 1e-9:
                d['nnz'] += 1
                d['sum'] += float(acc[i])
        print(f"  --- K={K} eta={eta}  value={entry['value_frac']} "
              f"({res.fun:.9f})  dual nnz {entry['nnz_raw']} raw / "
              f"{entry['nnz_sym']} symmetrised of {entry['rows']} rows "
              f"({time.time()-t0:.1f}s)")
        print(f"      {'family':>10} {'nnz':>5} {'rows':>6} {'sum lambda':>12}")
        for tg, d in entry['families'].items():
            print(f"      {tg:>10} {d['nnz']:>5} {d['rows']:>6} {d['sum']:>12.6f}")
        # per-family support, aggregated by the (x, y) type of the sets involved
        for tg in ['mono_f', 'submod_g', 'greedy', 'band_lo', 'band_hi']:
            items = []
            for i, (t2, meta) in enumerate(tags):
                if t2 != tg or acc[i] <= 1e-9:
                    continue
                if tg in ("submod_f", "submod_g"):
                    S, e, e2 = meta
                    desc = f"S={setstr(S,n,K)}[x,y={xy(S,n,K)}] e={lab(e,K)} e2={lab(e2,K)}"
                elif tg in ("band_lo", "band_hi"):
                    A, B = meta
                    desc = f"A={setstr(A,n,K)}[x,y={xy(A,n,K)}] B={setstr(B,n,K)}"
                elif tg == "greedy":
                    t, e = meta
                    desc = f"t={t} e={lab(e,K)}"
                else:
                    S, e = meta
                    desc = f"S={setstr(S,n,K)}[x,y={xy(S,n,K)}] e={lab(e,K)}"
                items.append({'lambda': float(acc[i]),
                              'rational': rationalise(float(acc[i]), eta),
                              'desc': desc})
            items.sort(key=lambda z: -z['lambda'])
            entry['support'][tg] = items
            if items:
                print(f"      {tg}: {len(items)} nonzero")
                shown = items if tg in ('greedy', 'mono_f') else items[:8]
                for it in shown:
                    print(f"         {it['lambda']:.9f} [{it['rational']:>16}]  {it['desc']}")
                if len(items) > len(shown):
                    print(f"         ... {len(items)-len(shown)} more (see JSON)")
        entry['dual_obj_raw'] = dual_obj_raw
        entry['dual_obj_sym'] = dual_obj_sym
        entry['dual_feas_residual'] = feas
        entry['min_multiplier'] = sign_ok
        ok = (abs(dual_obj_sym - float(res.fun)) < 1e-8 and feas < 1e-7
              and sign_ok > -1e-9)
        record(f"C: symmetrised dual is feasible with objective = LP value "
               f"(K={K}, eta={eta})", ok,
               f"b'y = {dual_obj_sym:.12f} vs {res.fun:.12f}, "
               f"|A'y - c|_inf = {feas:.2e}, min lambda = {sign_ok:.2e}")
        out[f"K{K}_eta{eta}"] = entry
    RESULTS['C_duals'] = out


# ---------------------------------------------------------------------------
# Part D: candidate reduced LP for the submodular-surrogate model
# ---------------------------------------------------------------------------
def reduced_sub(K, eta, eu=None, eo=None, drop=()):
    """Path-variable relaxation of the submodular-surrogate model.

    Variables (all >= 0):
      d_t, dd_t (= dtilde_t)                 t = 0..K-1
      g_{t,i}, gg_{t,i} (= gtilde_{t,i})     t = 0..K, i = 0..K-1
      A_t = ftilde(S^t u O) - ftilde(S^t)    t = 0..K

    Every row is a valid inequality of the model (derivations in the .md).
    """
    if eu is None:
        eu = eo = eta ** 0.5
    idx = {}

    def new(k):
        idx[k] = len(idx)
    for t in range(K):
        new(('d', t))
    for t in range(K):
        new(('dd', t))
    for t in range(K + 1):
        for i in range(K):
            new(('g', t, i))
    for t in range(K + 1):
        for i in range(K):
            new(('gg', t, i))
    for t in range(K + 1):
        new(('A', t))
    nv = len(idx)
    rows, cols, vals, b, tags = [], [], [], [], []
    r = 0

    def ub(c, rhs, tag):
        nonlocal r
        if tag[0] in drop:
            return
        for k, v in c.items():
            rows.append(r); cols.append(idx[k]); vals.append(float(v))
        b.append(float(rhs)); tags.append(tag); r += 1

    for t in range(K):
        c = {('g', t, i): -1.0 for i in range(K)}
        for s in range(t):
            c[('d', s)] = -1.0
        ub(c, -1.0, ('cover_f', t))                       # f coverage
        for i in range(K):
            ub({('g', t, i): 1.0 / eta, ('d', t): -1.0}, 0.0, ('pred', t, i))
            ub({('g', t + 1, i): 1.0, ('g', t, i): -1.0}, 0.0, ('mono', t, i))
            ub({('g', t, i): 1.0, ('d', t): -1.0,
                ('g', t + 1, i): -(1 - 1 / eta)}, 0.0, ('cons', t, i))
        ub({('dd', t): 1.0, ('d', t): -eo}, 0.0, ('band_d_hi', t))
        ub({('d', t): 1.0 / eu, ('dd', t): -1.0}, 0.0, ('band_d_lo', t))
    for t in range(K + 1):
        for i in range(K):
            ub({('gg', t, i): 1.0, ('g', t, i): -eo}, 0.0, ('band_g_hi', t, i))
            ub({('g', t, i): 1.0 / eu, ('gg', t, i): -1.0}, 0.0, ('band_g_lo', t, i))
    for t in range(K):
        for i in range(K):
            ub({('gg', t, i): 1.0, ('dd', t): -1.0}, 0.0, ('greedy', t, i))
            ub({('gg', t + 1, i): 1.0, ('gg', t, i): -1.0}, 0.0, ('sub_gg', t, i))
    for t in range(K - 1):
        ub({('dd', t + 1): 1.0, ('dd', t): -1.0}, 0.0, ('sub_dd', t))
    for t in range(K + 1):
        c = {('A', t): 1.0}
        for i in range(K):
            c[('gg', t, i)] = -1.0
        ub(c, 0.0, ('Aup', t))                            # A_t <= sum_i gg_{t,i}
        c = {('A', t): -1.0}
        for s in range(min(t, K)):
            c[('d', s)] = -1.0 / eu
        ub(c, -1.0 / eu, ('Alo_f', t))                    # A_t >= (1 - P_t)/eta_u
        c = {('A', t): -1.0}
        for s in range(min(t, K)):
            c[('dd', s)] = -1.0
        ub(c, -1.0 / eu, ('Alo_ft', t))                   # A_t >= 1/eta_u - rho~_t
    for t in range(K):
        ub({('A', t + 1): 1.0, ('A', t): -1.0}, 0.0, ('Amono', t))
        ub({('A', t): 1.0, ('dd', t): -1.0, ('A', t + 1): -1.0}, 0.0, ('Adrop', t))
    A = coo_matrix((vals, (rows, cols)), shape=(r, nv)).tocsr()
    obj = np.zeros(nv)
    for t in range(K):
        obj[idx[('d', t)]] = 1.0
    res = linprog(obj, A_ub=A, b_ub=np.array(b), bounds=[(0, None)] * nv,
                  method="highs")
    return res, idx, A, np.array(b), tags


def part_D(quick=False):
    print("\n=== Part D: candidate reduced LP (NEGATIVE RESULT / 卡点) ===")
    rows = []
    Ks = [2, 3, 4] if quick else [2, 3, 4, 5, 6, 8]
    etas = [1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0]
    n_eq_V = n_eq_W = 0
    for K in Ks:
        for eta in etas:
            res, *_ = reduced_sub(K, eta)
            v, j = min_V(K, eta)
            w, m = min_W(K, eta)
            rows.append({'K': K, 'eta': eta, 'reduced_sub': float(res.fun),
                         'min_j_Vj': v, 'min_m_Wm': w,
                         'dev_from_V': float(res.fun) - v,
                         'dev_from_W': float(res.fun) - w})
            n_eq_V += abs(res.fun - v) < 1e-9
            n_eq_W += abs(res.fun - w) < 1e-9
    print(f"   {'K':>2} {'eta':>5} {'reduced_sub':>13} {'min_j V_j':>12} "
          f"{'min_m W_m':>12} {'verdict':>10}")
    for r0 in rows:
        verdict = ('= min_j V_j' if abs(r0['dev_from_V']) < 1e-9 else
                   ('= min_m W_m' if abs(r0['dev_from_W']) < 1e-9 else 'other'))
        print(f"   {r0['K']:>2} {r0['eta']:>5} {r0['reduced_sub']:>13.9f} "
              f"{r0['min_j_Vj']:>12.9f} {r0['min_m_Wm']:>12.9f} {verdict:>12}")
    record("D: reduced-sub LP equals min_j V_j at every grid point", n_eq_V == len(rows),
           f"{n_eq_V}/{len(rows)} equal min_j V_j, {n_eq_W}/{len(rows)} equal min_m W_m")
    RESULTS['D_reduced'] = {'rows': rows, 'n_eq_V': n_eq_V, 'n_eq_W': n_eq_W,
                            'n_points': len(rows)}


# ---------------------------------------------------------------------------
# Part E: symbolic derivation of W_m from the tight system
# ---------------------------------------------------------------------------
def part_E():
    print("\n=== Part E: tight system  ==>  objective = W_m  [symbolic] ===")
    import sympy as sp
    K, m, t, eu, eo, A0 = sp.symbols('K m t eta_u eta_o A0', positive=True)
    r = 1 - 1 / K
    eta = eu * eo
    # tight relations read off the LP optimum, for t < m:
    #   A_t = K dtilde_t          (greedy tie + ftilde submodularity, "Aup")
    #   A_{t+1} = A_t - dtilde_t  ("Adrop")            ==> A_t = A0 r^t
    #   dtilde_t = eta_o d_t      (band_hi on the chosen element)
    # and at t = m:  A_m = (1 - P_m)/eta_u  ("Alo_f"), then d_t = d_m for t >= m.
    Pm = sp.simplify(sp.summation(A0 * r ** t / (K * eo), (t, 0, m - 1)))
    A0s = sp.simplify(sp.solve(sp.Eq(A0 * r ** m * eu, 1 - Pm), A0)[0])
    val = sp.simplify(Pm.subs(A0, A0s) + (K - m) * A0s * r ** m / (K * eo))
    W = (K - m * r ** m) / (K * (1 + (eta - 1) * r ** m))
    diff = sp.simplify(sp.together(sp.expand(val - W)))
    ok1 = diff == 0
    record("E1: tight system implies objective = W_m (symbolic K, m, eta_u, eta_o)",
           ok1, f"value - W_m = {diff}")
    A0_target = eo / (1 + (eta - 1) * r ** m)
    ok2 = sp.simplify(A0s - A0_target) == 0
    record("E2: A_0 = eta_o / (1 + (eta-1) r^m)", ok2,
           f"A0 = {sp.simplify(A0s)}")
    ok3 = sp.simplify(val.subs({eu: sp.sqrt(eta), eo: sp.sqrt(eta)}) - W) == 0
    # depends on eta only through the product
    e1, e2 = sp.symbols('e1 e2', positive=True)
    ok4 = sp.simplify(val.subs({eu: e1, eo: e2}) - val.subs({eu: e1 * e2, eo: 1})) == 0
    record("E3: the attained value depends on eta_u, eta_o only through eta", ok4)
    RESULTS['E_symbolic'] = {'value': str(sp.simplify(val)), 'W_m': str(sp.simplify(W)),
                             'A0': str(sp.simplify(A0s)),
                             'value_minus_W': str(diff), 'ok': bool(ok1 and ok2 and ok4)}


# ---------------------------------------------------------------------------
# Part F: explicit instance family with submodular ftilde attaining W_m
# ---------------------------------------------------------------------------
def build_instance(K, m, eta, eu=None, eo=None):
    """Ground set b_0..b_{K-1} = bits 0..K-1, o_0..o_{K-1} = bits K..2K-1.

        r = 1-1/K,  D = 1 + (eta-1) r^m,  A0 = eta_o / D,
        d_t = r^{min(t,m)} / (K D),       dtilde_t = eta_o d_t,
        cut(S) = sum_{t < m, b_t in S} d_t,       y = |S n O|

        f(S)      = sum_{b_t in S} d_t        + (y/K) (1  - cut(S))
        ftilde(S) = eta_o sum_{b_t in S} d_t  + (y/K) (A0 - eta_o cut(S))
    """
    if eu is None:
        eu = eo = eta ** 0.5
    n = 2 * K
    N = 1 << n
    r = 1 - 1.0 / K
    D = 1 + (eta - 1) * r ** m
    A0 = eo / D
    d = [r ** min(t, m) / (K * D) for t in range(K)]
    f = np.zeros(N)
    g = np.zeros(N)
    for S in range(N):
        y = bin(S >> K).count('1')
        base = sum(d[t] for t in range(K) if S >> t & 1)
        cut = sum(d[t] for t in range(m) if S >> t & 1)
        f[S] = base + (y / K) * (1.0 - cut)
        g[S] = eo * base + (y / K) * (A0 - eo * cut)
    return n, f, g, d, A0


def part_F(quick=False):
    print("\n=== Part F: explicit instance family with submodular ftilde ===")
    Ks = [2, 3, 4, 5] if quick else [2, 3, 4, 5, 6]
    etas = [1.0, 1.1, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 6.0, 10.0]
    fails, tot = [], 0
    worst_sub_g = worst_ratio = 0.0
    for K in Ks:
        for m in range(K):
            for eta in etas:
                n, f, g, d, A0 = build_instance(K, m, eta)
                v = verify_instance(n, K, f, g, eta ** 0.5, eta ** 0.5)
                W = Wm(K, m, eta)
                ok = (v['f_empty'] and v['monotone_f'] and v['submodular_f'] and
                      v['monotone_ftilde'] and v['submodular_ftilde'] and
                      v['band_ok'] and v['greedy_picks_0..K-1'] and
                      v['opt_is_one'] and abs(v['ratio'] - W) < 1e-9)
                worst_sub_g = max(worst_sub_g, v['max_submod_violation_ftilde'])
                worst_ratio = max(worst_ratio, abs(v['ratio'] - W))
                tot += 1
                if not ok:
                    fails.append({'K': K, 'm': m, 'eta': eta, 'verify': v, 'W': W})
    record("F1: family is a valid instance and attains W_m (symmetric eta split)",
           not fails, f"{tot-len(fails)}/{tot} PASS, "
                      f"max ftilde-submod violation {worst_sub_g:.2e}, "
                      f"max |ratio - W_m| {worst_ratio:.2e}")
    # asymmetric splits of eta
    fails2, tot2 = [], 0
    for K in [2, 3, 4, 5]:
        for m in range(K):
            for eta in [1.5, 2.0, 3.0]:
                for eu in [1.0, 1.2, eta ** 0.5, eta / 1.1, eta]:
                    eo = eta / eu
                    n, f, g, d, A0 = build_instance(K, m, eta, eu, eo)
                    v = verify_instance(n, K, f, g, eu, eo)
                    W = Wm(K, m, eta)
                    ok = (v['monotone_f'] and v['submodular_f'] and
                          v['submodular_ftilde'] and v['band_ok'] and
                          v['greedy_picks_0..K-1'] and v['opt_is_one'] and
                          abs(v['ratio'] - W) < 1e-9)
                    tot2 += 1
                    if not ok:
                        fails2.append({'K': K, 'm': m, 'eta': eta, 'eu': eu})
    record("F2: same family for every split eta = eta_u * eta_o", not fails2,
           f"{tot2-len(fails2)}/{tot2} PASS")
    # the family therefore certifies rho_K^sub <= min_m W_m; check it beats U_K
    cross = []
    for K in [4, 5, 6, 8, 12, 20]:
        for eta in [1.25, 1.5, 2.0, 2.5, 3.0, 4.0]:
            w, m = min_W(K, eta)
            if w > UK(K, eta) + 1e-12:
                cross.append({'K': K, 'eta': eta, 'min_m_Wm': w, 'U_K': UK(K, eta)})
    record("F3: min_m W_m > U_K at the recorded (K, eta) (now instance-backed)",
           len(cross) > 0, f"{len(cross)} grid points exceed U_K")
    # sanity: family at m = argmin reproduces the headline values
    hits = []
    for K, eta, target in [(3, 1.5, 19 / 33), (4, 1.5, 23 / 41), (4, 2.0, 23 / 50),
                           (5, 1.5, 433 / 785), (5, 2.0, 93 / 205)]:
        w, m = min_W(K, eta)
        n, f, g, d, A0 = build_instance(K, m, eta)
        v = verify_instance(n, K, f, g, eta ** 0.5, eta ** 0.5)
        hits.append({'K': K, 'eta': eta, 'target': target, 'ratio': v['ratio'],
                     'm': m, 'ok': abs(v['ratio'] - target) < 1e-9})
    record("F4: family reproduces the five F4 headline values", all(h['ok'] for h in hits),
           ", ".join(f"K={h['K']},eta={h['eta']}:{h['ratio']:.9f}" for h in hits))
    RESULTS['F_instances'] = {'n_points': tot, 'fails': fails, 'n_points_split': tot2,
                              'fails_split': fails2, 'UK_crossings': cross,
                              'headline': hits,
                              'formula': build_instance.__doc__}


# ---------------------------------------------------------------------------
# Part G: canonical duals.  (i) minimal total submod_g mass -- is the new block
# essential?  (ii) minimal-total-mass dual, symmetrised over O -- readable support.
# ---------------------------------------------------------------------------
def canonical_dual(n, K, eta, objective='total'):
    """Re-optimise inside the dual optimal face.  Returns (lambda, info)."""
    from scipy.sparse import hstack, vstack, csr_matrix
    O = tuple(range(K, 2 * K))
    N = 1 << n
    nv = 2 * N
    res, A_ub, b_ub, tags = solve_lattice(n, K, eta, O, True)
    val = float(res.fun)
    m = A_ub.shape[0]
    A_eq = np.zeros((3, nv))
    A_eq[0, 0] = 1.0
    A_eq[1, N] = 1.0
    A_eq[2, Om_of(O)] = 1.0
    c = np.zeros(nv)
    c[(1 << K) - 1] = 1.0
    M = hstack([csr_matrix(-A_ub.T), csr_matrix(A_eq.T)]).tocsr()
    tail = csr_matrix(np.concatenate([np.zeros(m), [0.0, 0.0, 1.0]])[None, :])
    Aeq2 = vstack([M, tail]).tocsr()
    beq2 = np.concatenate([c, [val]])
    bounds = [(0, None)] * m + [(None, None)] * 3
    if objective == 'total':
        w = np.ones(m)
    else:
        w = np.array([1.0 if t[0] == 'submod_g' else 0.0 for t in tags])
    r2 = linprog(np.concatenate([w, [0.0, 0.0, 0.0]]), A_eq=Aeq2, b_eq=beq2,
                 bounds=bounds, method="highs")
    if r2.status != 0:
        return None, {'status': r2.status, 'value': val}
    lam = r2.x[:m]
    return lam, {'value': val, 'obj': float(r2.fun), 'tags': tags, 'n': n,
                 'submod_g_mass': float(sum(lam[i] for i, t in enumerate(tags)
                                            if t[0] == 'submod_g'))}


def symmetrise_over_O(lam, tags, n, K):
    idmap = {}
    ident = list(range(n))
    for i, (tg, meta) in enumerate(tags):
        idmap[row_key(tg, meta, n, ident)] = i
    acc = np.zeros_like(lam)
    perms = [list(range(K)) + [K + pi[j] for j in range(K)]
             for pi in itertools.permutations(range(K))]
    for p in perms:
        for i, (tg, meta) in enumerate(tags):
            acc[idmap[row_key(tg, meta, n, p)]] += lam[i]
    return acc / len(perms)


def part_G(quick=False):
    print("\n=== Part G: canonical duals (essentiality of submod_g, greedy pattern) ===")
    ess = []
    plan = ([(2, 1.5), (2, 2.0), (3, 1.25), (3, 1.5), (3, 2.0), (3, 3.0)] if quick
            else [(2, 1.5), (2, 2.0), (3, 1.25), (3, 1.5), (3, 1.8), (3, 2.0),
                  (3, 3.0), (4, 1.25), (4, 1.5), (4, 2.0), (4, 3.0)])
    for K, eta in plan:
        n = 2 * K
        lam, info = canonical_dual(n, K, eta, 'submod_g')
        w, mstar = min_W(K, eta)
        v, jstar = min_V(K, eta)
        mass = info['submod_g_mass'] if lam is not None else None
        changed = abs(w - v) > 1e-9
        ok = (mass is not None) and ((mass > 1e-7) == changed)
        ess.append({'K': K, 'eta': eta, 'min_submod_g_mass': mass,
                    'value': info['value'], 'min_m_Wm': w, 'argmin_m': mstar,
                    'min_j_Vj': v, 'value_changes_vs_base': changed,
                    'consistent': bool(ok)})
        print(f"   K={K} eta={eta:<6} min submod_g dual mass = "
              f"{mass:.9f}   (value changes vs base: {changed})")
    record("G1: submod_g dual mass is > 0 exactly where the value moves off min_j V_j",
           all(e['consistent'] for e in ess),
           f"{sum(e['consistent'] for e in ess)}/{len(ess)}")
    # greedy-multiplier pattern in the minimal-total-mass dual
    pat = []
    plan2 = ([(3, 1.25), (3, 1.5)] if quick else
             [(3, 1.25), (3, 1.5), (3, 1.8), (4, 1.25), (4, 1.5), (4, 2.0)])
    for K, eta in plan2:
        n = 2 * K
        lam, info = canonical_dual(n, K, eta, 'total')
        if lam is None:
            continue
        acc = symmetrise_over_O(lam, info['tags'], n, K)
        eo = eta ** 0.5
        lg = {}
        for i, (tg, meta) in enumerate(info['tags']):
            if tg == 'greedy' and acc[i] > 1e-12:
                t, e = meta
                if e >= K:
                    lg.setdefault(t, set()).add(round(float(acc[i]) * eo, 10))
        w, mstar = min_W(K, eta)
        pred = {}
        for t in range(K):
            pred[t] = ((1 - w) / (K - 1) * (K / (K - 1.0)) ** t if t < mstar
                       else 1.0 / K)
        obs = {t: (list(lg[t])[0] if t in lg and len(lg[t]) == 1 else None)
               for t in range(K)}
        dev = max(abs(obs[t] - pred[t]) for t in range(K)
                  if obs[t] is not None) if any(obs[t] is not None
                                                for t in range(K)) else None
        row = {'K': K, 'eta': eta, 'm_star': mstar,
               'observed': {str(t): obs[t] for t in range(K)},
               'predicted': {str(t): pred[t] for t in range(K)},
               'max_dev': dev}
        pat.append(row)
        print(f"   K={K} eta={eta} m*={mstar}: lambda_greedy(t)*eta_o "
              f"obs={[None if obs[t] is None else round(obs[t],9) for t in range(K)]} "
              f"pred={[round(pred[t],9) for t in range(K)]}  dev={dev:.2e}")
    ok2 = all(r['max_dev'] is not None and r['max_dev'] < 1e-7 for r in pat)
    record("G2: lambda_greedy(t)*eta_o = (1-W_m)/(K-1) * (K/(K-1))^t for t < m*, "
           "= 1/K for t >= m*", ok2,
           f"{sum(1 for r in pat if r['max_dev'] is not None and r['max_dev'] < 1e-7)}"
           f"/{len(pat)} points")
    RESULTS['G_canonical_duals'] = {'essentiality': ess, 'greedy_pattern': pat}


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--parts', default='ABCDEFG')
    ap.add_argument('--quick', action='store_true')
    args = ap.parse_args()
    t0 = time.time()
    if 'A' in args.parts:
        part_A()
    if 'B' in args.parts:
        part_B(args.quick)
    if 'C' in args.parts:
        part_C(args.quick)
    if 'D' in args.parts:
        part_D(args.quick)
    if 'E' in args.parts:
        part_E()
    if 'F' in args.parts:
        part_F(args.quick)
    if 'G' in args.parts:
        part_G(args.quick)
    RESULTS['checks'] = CHECKS
    RESULTS['seconds'] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, 'H_C_submodular_surrogate.json'), 'w') as fh:
        json.dump(RESULTS, fh, indent=1, default=float)
    npass = sum(1 for c in CHECKS if c['pass'])
    print(f"\n=== {npass}/{len(CHECKS)} checks PASS, {time.time()-t0:.0f}s ===")
    print("file: results/H_C_submodular_surrogate.json")
    sys.exit(0 if npass == len(CHECKS) else 1)


if __name__ == "__main__":
    main()
