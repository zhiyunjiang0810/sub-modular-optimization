"""
M3.2 oracle: two-sided exact certificate for rho^sub_{8,4}(3/2) = 23/41.

Model (TASKS8 M3.2 / ledger card T7, "submodular surrogate"):
  ground set [n] with n = 8, budget K = 4;
  BOTH f and ftilde monotone submodular with f(empty) = ftilde(empty) = 0;
  Definition-1 single-element error band  d_e(S)/eta_u <= dtilde_e(S) <= eta_o d_e(S)
  for every S and every e not in S, with eta = eta_u * eta_o = 3/2;
  single-step predictive greedy, K = 4 steps, adversarial tie breaking;
  rho^sub_{8,4}(3/2) := min over instances of f(T)/max_{|S|<=K} f(S).

What this script does
  A  branch/orbit structure + full-lattice LP (2 * 2^8 = 512 variables, one per
     subset per function) for every target set O, floating point (HiGHS).
     The greedy branch is pinned to b_0..b_3 = 0,1,2,3 by relabelling; what is
     left to enumerate is the position of O, 70 sets falling into 16 orbits.
  B  exact rational instance for the UPPER side: the H-C section 6 family at
     K=4, m=2, eta=3/2 rebuilt over Fraction and verified property by property.
  C  exact rational DUAL certificates for the LOWER side: for each orbit
     representative, a nonnegative rational multiplier vector lambda with
     A' lambda = y e_{f(O)} - c and y >= 23/41, verified in Fraction arithmetic.
     Weak duality then gives LP(O) >= 23/41 for every O, hence
     rho^sub_{8,4}(3/2) >= 23/41.
  D  comparison numbers U_4(3/2) = 8080/14641, rho_4(3/2) = min_j V_j.

Reuse: the row families are the ones of code/worst_case_lp.py (frozen, imported
for its documented row list only) as extended in results/F4_submodular_ftilde.py
and results/H_C_submodular_surrogate.py; neither file is modified.  Two
deliberate differences from H-C build_rows, both recorded and both checked to
leave the LP value unchanged (Part A gate):
  (i)  ftilde monotonicity rows are ADDED (the model of this task asks for a
       monotone submodular surrogate; H-C constrained only submodularity of
       ftilde);
  (ii) the submodularity block is de-duplicated: H-C emits (S,e,e2) and
       (S,e2,e), which are the same inequality.

Usage
    python3 results/M3_rhosub_K4_exact.py --parts ABCD
    python3 results/M3_rhosub_K4_exact.py --parts A --quick
Outputs
    results/M3_rhosub_K4_exact.json
Exit code 0 iff every oracle check passed.
"""
import argparse
import itertools
import json
import os
import sys
import time
from fractions import Fraction as Fr

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

N_GROUND = 8
K_BUDGET = 4
ETA = Fr(3, 2)
# rational split of eta; the LP value depends on (eta_u, eta_o) only through the
# product (Lemma 0' scaling bijection ftilde -> c ftilde), re-checked in Part A.
ETA_U = Fr(3, 2)
ETA_O = Fr(1, 1)
TARGET = Fr(23, 41)

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
    return 1 - q ** j * (1 - Fr(K - j, K) / eta)


def min_V(K, eta):
    return min((Vj(K, j, eta), j) for j in range(K))


def Wm(K, m, eta):
    r = Fr(K - 1, K)
    rm = r ** m
    return (K - m * rm) / (K * (1 + (eta - 1) * rm))


def min_W(K, eta):
    return min((Wm(K, m, eta), m) for m in range(K))


def UK(K, eta):
    return 1 - (1 - 1 / (eta * (K - 1) + 1)) ** K


def LK(K, eta):
    return 1 - (1 - 1 / (eta * K)) ** K


# ---------------------------------------------------------------------------
# Part A infrastructure: the full-lattice LP
# ---------------------------------------------------------------------------
def build_rows(n=N_GROUND, K=K_BUDGET, eu=ETA_U, eo=ETA_O,
               mono_g=True, dedupe=True, g_submod=True):
    """Rows of the factor-revealing LP, as (tag, meta, {var: Fraction}).

    Variables: F(S) = S, G(S) = 2^n + S, for S != 0 (f(empty)=ftilde(empty)=0
    is substituted, so the two empty-set columns simply do not appear).
    Every row means  <coef, x>  <=  0.
    The greedy branch is pinned: at step t the algorithm sees S^t = {0..t-1}
    and picks t, so the tie-tolerant rule dtilde_t(S^t) >= dtilde_e(S^t) is
    encoded as ftilde(S^t u e) - ftilde(S^t u t) <= 0.
    """
    N = 1 << n

    def F(S):
        return S

    def G(S):
        return N + S

    rows = []

    def add(coefs, tag, meta):
        c = {k: v for k, v in coefs.items() if v != 0 and k != F(0) and k != G(0)}
        rows.append((tag, meta, c))

    for S in range(N):                                   # (1) f monotone
        for e in range(n):
            if not S >> e & 1:
                add({F(S): Fr(1), F(S | 1 << e): Fr(-1)}, "mono_f", (S, e))
    if mono_g:                                           # (1b) ftilde monotone
        for S in range(N):
            for e in range(n):
                if not S >> e & 1:
                    add({G(S): Fr(1), G(S | 1 << e): Fr(-1)}, "mono_g", (S, e))
    for S in range(N):                                   # (2) f submodular
        for e in range(n):
            if S >> e & 1:
                continue
            for e2 in range(n):
                if e2 == e or S >> e2 & 1:
                    continue
                if dedupe and e2 < e:
                    continue
                c = {}
                for k, v in ((F(S | 1 << e | 1 << e2), Fr(1)), (F(S | 1 << e2), Fr(-1)),
                             (F(S | 1 << e), Fr(-1)), (F(S), Fr(1))):
                    c[k] = c.get(k, Fr(0)) + v
                add(c, "submod_f", (S, e, e2))
    if g_submod:                                         # (2b) ftilde submodular
        for S in range(N):
            for e in range(n):
                if S >> e & 1:
                    continue
                for e2 in range(n):
                    if e2 == e or S >> e2 & 1:
                        continue
                    if dedupe and e2 < e:
                        continue
                    c = {}
                    for k, v in ((G(S | 1 << e | 1 << e2), Fr(1)), (G(S | 1 << e2), Fr(-1)),
                                 (G(S | 1 << e), Fr(-1)), (G(S), Fr(1))):
                        c[k] = c.get(k, Fr(0)) + v
                    add(c, "submod_g", (S, e, e2))
    for A in range(N):                                   # (3) single-element band
        for e in range(n):
            if A >> e & 1:
                continue
            AB = A | 1 << e
            c = {}
            for k, v in ((F(AB), 1 / eu), (F(A), -1 / eu), (G(AB), Fr(-1)), (G(A), Fr(1))):
                c[k] = c.get(k, Fr(0)) + v
            add(c, "band_lo", (A, e))
            c = {}
            for k, v in ((G(AB), Fr(1)), (G(A), Fr(-1)), (F(AB), -eo), (F(A), eo)):
                c[k] = c.get(k, Fr(0)) + v
            add(c, "band_hi", (A, e))
    for t in range(K):                                   # (4) greedy branch
        S = (1 << t) - 1
        for e in range(n):
            if e == t or S >> e & 1:
                continue
            c = {}
            for k, v in ((G(S | 1 << e), Fr(1)), (G(S | 1 << t), Fr(-1))):
                c[k] = c.get(k, Fr(0)) + v
            add(c, "greedy", (t, e))
    return rows


def cap_rows(n=N_GROUND, K=K_BUDGET):
    """Optional normalisation block  f(S) <= 1 for |S| <= K  (rhs 1, not 0)."""
    out = []
    for S in range(1 << n):
        if bin(S).count('1') <= K:
            out.append(("cap_f", (S,), {S: Fr(1)}))
    return out


def lp_matrices(rows, n=N_GROUND):
    """Dense-index CSR matrix over the 2*(2^n - 1) non-empty-set variables."""
    N = 1 << n
    cols = [S for S in range(1, N)] + [N + S for S in range(1, N)]
    cidx = {c: i for i, c in enumerate(cols)}
    r, c, v = [], [], []
    for i, (_tag, _meta, coefs) in enumerate(rows):
        for k, val in coefs.items():
            r.append(i)
            c.append(cidx[k])
            v.append(float(val))
    A = coo_matrix((v, (r, c)), shape=(len(rows), len(cols))).tocsr()
    return A, cidx, cols


def solve_lattice_float(rows, O, n=N_GROUND, K=K_BUDGET, A=None, cidx=None,
                        caps=0):
    """min f(T) s.t. rows <= 0 (first len(rows)-caps rows), f(S)<=1 caps, f(O)=1."""
    if A is None:
        A, cidx, _ = lp_matrices(rows, n)
    N = 1 << n
    nv = A.shape[1]
    b = np.zeros(A.shape[0])
    if caps:
        b[-caps:] = 1.0
    obj = np.zeros(nv)
    obj[cidx[(1 << K) - 1]] = 1.0
    Om = sum(1 << i for i in O)
    Aeq = coo_matrix(([1.0], ([0], [cidx[Om]])), shape=(1, nv)).tocsr()
    res = linprog(obj, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=[1.0],
                  bounds=[(None, None)] * nv, method="highs")
    return res


# ---------------------------------------------------------------------------
# branch / orbit structure
# ---------------------------------------------------------------------------
def orbit_group(O, n=N_GROUND, K=K_BUDGET):
    """Permutations of [n] fixing 0..K-1 pointwise (the pinned greedy branch)
    and mapping O to itself.  Returned as tuples p with p[u] = image of u."""
    tail = list(range(K, n))
    out = []
    for perm in itertools.permutations(tail):
        p = list(range(K)) + list(perm)
        if {p[u] for u in O} == set(O):
            out.append(tuple(p))
    return out


def orbit_key_O(O, n=N_GROUND, K=K_BUDGET):
    """Invariant of O under permutations of [n]\\[K]: (O cap [K], |O \\ [K]|)."""
    inT = tuple(sorted(u for u in O if u < K))
    return (inT, len([u for u in O if u >= K]))


def all_O(n=N_GROUND, K=K_BUDGET):
    return list(itertools.combinations(range(n), K))


def orbit_reps(n=N_GROUND, K=K_BUDGET):
    seen = {}
    for O in all_O(n, K):
        k = orbit_key_O(O, n, K)
        seen.setdefault(k, []).append(O)
    return seen


# ---------------------------------------------------------------------------
def part_A(quick=False):
    print("\n=== Part A: branch/orbit structure and full-lattice LP (float) ===")
    n, K = N_GROUND, K_BUDGET
    reps = orbit_reps(n, K)
    sizes = {str(k): len(v) for k, v in reps.items()}
    record("A0: 70 target sets fall into 16 orbits summing to C(8,4)",
           len(reps) == 16 and sum(len(v) for v in reps.values()) == 70,
           f"{len(reps)} orbits, sizes {sorted(len(v) for v in reps.values())}")
    t0 = time.time()
    rows = build_rows()
    A, cidx, _cols = lp_matrices(rows)
    fam = {}
    for tag, _m, _c in rows:
        fam[tag] = fam.get(tag, 0) + 1
    idents = set(row_ident(tag, meta, N_GROUND) for tag, meta, _c in rows)
    coefvecs = set(tuple(sorted(c.items())) for _t, _m, c in rows)
    record("A5: row labels and row coefficient vectors are both injective "
           "(no duplicated inequality, so the dual transport in Part C is "
           "well defined)",
           len(idents) == len(rows) and len(coefvecs) == len(rows),
           f"{len(rows)} rows, {len(idents)} distinct labels, "
           f"{len(coefvecs)} distinct coefficient vectors")
    print(f"   rows={A.shape[0]} vars={A.shape[1]} families={fam} "
          f"({time.time()-t0:.1f}s)")
    RESULTS['A_lp_shape'] = {'rows': int(A.shape[0]), 'vars': int(A.shape[1]),
                             'families': fam, 'orbit_sizes': sizes}

    # full enumeration over all 70 target sets (the symmetry-reduction gate)
    vals = {}
    t0 = time.time()
    todo = all_O(n, K) if not quick else [v[0] for v in reps.values()]
    for O in todo:
        res = solve_lattice_float(rows, O, A=A, cidx=cidx)
        vals[O] = float(res.fun) if res.status == 0 else None
        print(f"   O={O} value={vals[O]!r}  ({time.time()-t0:.0f}s)")
        sys.stdout.flush()
    RESULTS['A_values_all_O'] = {str(k): v for k, v in vals.items()}
    # gate: constant on orbits
    worst = 0.0
    byorb = {}
    for O, v in vals.items():
        byorb.setdefault(orbit_key_O(O, n, K), []).append(v)
    for k, vs in byorb.items():
        worst = max(worst, max(vs) - min(vs))
    if not quick:
        record("A1: LP value is constant on each of the 16 orbits (full 70-set gate)",
               worst < 1e-7, f"max spread inside an orbit = {worst:.2e}")
    best = min(vals.values())
    record("A2: min over target sets = 23/41", abs(best - 23 / 41) < 1e-7,
           f"min = {best:.12f}, 23/41 = {23/41:.12f}, "
           f"argmin orbits = {[str(k) for k, vs in byorb.items() if min(vs) < best + 1e-9]}")
    RESULTS['A_orbit_values'] = {str(k): {'value': min(vs), 'size': len(vs)}
                                 for k, vs in byorb.items()}

    # split invariance of the LP value (Lemma 0'): same eta, three splits
    inv = []
    Odis = tuple(range(K, 2 * K))
    for eu, eo in [(Fr(3, 2), Fr(1)), (Fr(1), Fr(3, 2)), (Fr(5, 4), Fr(6, 5))]:
        rws = build_rows(eu=eu, eo=eo)
        A2, cidx2, _ = lp_matrices(rws)
        r2 = solve_lattice_float(rws, Odis, A=A2, cidx=cidx2)
        inv.append({'eta_u': str(eu), 'eta_o': str(eo), 'value': float(r2.fun)})
        print(f"   split eta_u={eu} eta_o={eo}: {float(r2.fun):.12f}")
    spread = max(x['value'] for x in inv) - min(x['value'] for x in inv)
    record("A3: LP value depends on the split only through eta = eta_u eta_o",
           spread < 1e-7, f"spread over three rational splits = {spread:.2e}")
    RESULTS['A_split_invariance'] = inv

    # variant gate: H-C row set (no ftilde monotonicity, duplicated submod rows)
    var = []
    for label, kw in [('with_mono_g_dedup', {}),
                      ('HC_rowset_no_mono_g', {'mono_g': False, 'dedupe': False}),
                      ('no_mono_g_dedup', {'mono_g': False})]:
        rws = build_rows(**kw)
        A2, cidx2, _ = lp_matrices(rws)
        r2 = solve_lattice_float(rws, Odis, A=A2, cidx=cidx2)
        var.append({'variant': label, 'rows': A2.shape[0], 'value': float(r2.fun)})
        print(f"   variant {label}: rows={A2.shape[0]} value={float(r2.fun):.12f}")
    spread = max(x['value'] for x in var) - min(x['value'] for x in var)
    record("A4: adding ftilde monotonicity / de-duplicating submod rows does not "
           "move the value at the argmin orbit", spread < 1e-7,
           f"spread = {spread:.2e} (all = {var[0]['value']:.12f})")
    RESULTS['A_rowset_variants'] = var
    RESULTS['A_seconds'] = round(time.time() - t0, 1)


# ---------------------------------------------------------------------------
# Part B: exact rational instance (upper side)
# ---------------------------------------------------------------------------
def build_instance_exact(K, m, eu, eo):
    """H-C section 6 family, in exact rational arithmetic.

        r = 1-1/K,  D = 1 + (eta-1) r^m,  A0 = eta_o / D,
        d_t = r^{min(t,m)} / (K D),
        cut(S) = sum_{t<m, b_t in S} d_t,   y = |S cap O|
        f(S)      = sum_{b_t in S} d_t       + (y/K)(1  - cut(S))
        ftilde(S) = eta_o sum_{b_t in S} d_t + (y/K)(A0 - eta_o cut(S))
    """
    eta = eu * eo
    n = 2 * K
    N = 1 << n
    r = Fr(K - 1, K)
    D = 1 + (eta - 1) * r ** m
    A0 = eo / D
    d = [r ** min(t, m) / (K * D) for t in range(K)]
    f = [Fr(0)] * N
    g = [Fr(0)] * N
    for S in range(N):
        y = bin(S >> K).count('1')
        base = sum((d[t] for t in range(K) if S >> t & 1), Fr(0))
        cut = sum((d[t] for t in range(m) if S >> t & 1), Fr(0))
        f[S] = base + Fr(y, K) * (1 - cut)
        g[S] = eo * base + Fr(y, K) * (A0 - eo * cut)
    return n, f, g, d, A0


def verify_instance_exact(n, K, f, g, eu, eo):
    """Every property checked with Fraction arithmetic, no tolerance."""
    N = 1 << n
    out = {'zero_at_empty': f[0] == 0 and g[0] == 0}
    mono_f = mono_g = sub_f = sub_g = True
    band_lo_ok = band_hi_ok = True
    eu_real = Fr(0)
    eo_real = Fr(0)
    for S in range(N):
        for e in range(n):
            if S >> e & 1:
                continue
            Se = S | 1 << e
            d, dt = f[Se] - f[S], g[Se] - g[S]
            mono_f = mono_f and d >= 0
            mono_g = mono_g and dt >= 0
            if dt > eo * d:
                band_hi_ok = False
            if eu * dt < d:
                band_lo_ok = False
            if d > 0:
                eo_real = max(eo_real, dt / d)
                if dt > 0:
                    eu_real = max(eu_real, d / dt)
            for e2 in range(n):
                if e2 == e or S >> e2 & 1:
                    continue
                sub_f = sub_f and (f[Se | 1 << e2] - f[S | 1 << e2]) <= d
                sub_g = sub_g and (g[Se | 1 << e2] - g[S | 1 << e2]) <= dt
    out['monotone_f'] = mono_f
    out['monotone_ftilde'] = mono_g
    out['submodular_f'] = sub_f
    out['submodular_ftilde'] = sub_g
    out['band_lo_ok'] = band_lo_ok
    out['band_hi_ok'] = band_hi_ok
    out['eta_u_realised'] = eu_real
    out['eta_o_realised'] = eo_real
    out['eta_realised'] = eu_real * eo_real
    # greedy with adversarial tie breaking: b_t must be a maximiser at step t
    S = 0
    greedy_ok = True
    trace = []
    for t in range(K):
        gains = {e: g[S | 1 << e] - g[S] for e in range(n) if not S >> e & 1}
        mx = max(gains.values())
        tie = [e for e in gains if gains[e] == mx]
        greedy_ok = greedy_ok and gains[t] == mx
        trace.append({'t': t, 'chosen': t, 'gain': str(gains[t]), 'max': str(mx),
                      'tied_with': tie})
        S |= 1 << t
    out['greedy_branch_ok'] = greedy_ok
    out['greedy_trace'] = trace
    out['f_T'] = f[(1 << K) - 1]
    out['opt'] = max(f[S] for S in range(N) if bin(S).count('1') <= K)
    out['opt_is_f_O'] = out['opt'] == f[((1 << K) - 1) << K]
    out['ratio'] = out['f_T'] / out['opt']
    return out


def part_B():
    print("\n=== Part B: exact rational instance (upper side) ===")
    K = K_BUDGET
    w, mstar = min_W(K, ETA)
    print(f"   min_m W_m(4, 3/2) = {w} at m* = {mstar}")
    out = {'m_star': mstar, 'W_mstar': str(w), 'splits': []}
    ok_all = True
    for eu, eo in [(Fr(3, 2), Fr(1)), (Fr(1), Fr(3, 2)), (Fr(5, 4), Fr(6, 5))]:
        n, f, g, d, A0 = build_instance_exact(K, mstar, eu, eo)
        v = verify_instance_exact(n, K, f, g, eu, eo)
        ok = (v['zero_at_empty'] and v['monotone_f'] and v['submodular_f'] and
              v['monotone_ftilde'] and v['submodular_ftilde'] and
              v['band_lo_ok'] and v['band_hi_ok'] and
              v['eta_realised'] == ETA and v['greedy_branch_ok'] and
              v['opt_is_f_O'] and v['ratio'] == TARGET)
        ok_all = ok_all and ok
        out['splits'].append({
            'eta_u': str(eu), 'eta_o': str(eo),
            'd': [str(x) for x in d], 'A0': str(A0),
            'ratio': str(v['ratio']), 'opt': str(v['opt']),
            'eta_u_realised': str(v['eta_u_realised']),
            'eta_o_realised': str(v['eta_o_realised']),
            'checks': {k: (str(v[k]) if not isinstance(v[k], (bool, list)) else v[k])
                       for k in ('zero_at_empty', 'monotone_f', 'submodular_f',
                                 'monotone_ftilde', 'submodular_ftilde',
                                 'band_lo_ok', 'band_hi_ok', 'greedy_branch_ok',
                                 'opt_is_f_O')},
            'greedy_trace': v['greedy_trace'],
            'ok': ok})
        print(f"   split ({eu},{eo}): ratio = {v['ratio']}, opt = {v['opt']}, "
              f"eta realised = {v['eta_u_realised']}*{v['eta_o_realised']}"
              f" = {v['eta_realised']}, all checks {'OK' if ok else 'FAILED'}")
    # the instance table at the canonical split, for the write-up
    n, f, g, d, A0 = build_instance_exact(K, mstar, ETA_U, ETA_O)
    out['f_table'] = {str(S): str(f[S]) for S in range(1 << n)}
    out['g_table'] = {str(S): str(g[S]) for S in range(1 << n)}
    record("B1: explicit rational (f, ftilde) attains exactly 23/41 with every "
           "model property verified in Fraction arithmetic", ok_all,
           f"ratio = 23/41 at 3 rational splits of eta = 3/2", )
    # B2: the same instance is an exactly feasible point of the LP that Part C
    # certifies, so primal and dual meet on the same object (this also catches a
    # sign error in any row family: a flipped row would be violated here).
    rows = build_rows()
    x = {S: f[S] for S in range(1, 1 << n)}
    x.update({(1 << n) + S: g[S] for S in range(1, 1 << n)})
    worst = None
    nbad = 0
    for tag, meta, coefs in rows:
        s = sum((val * x[k] for k, val in coefs.items()), Fr(0))
        if s > 0:
            nbad += 1
            if worst is None or s > worst[0]:
                worst = (s, tag, meta)
    Om = ((1 << K) - 1) << K
    ok2 = (nbad == 0 and f[Om] == 1 and f[(1 << K) - 1] == TARGET)
    record("B2: the instance is an exactly feasible point of LP(O = {o_0..o_3}) "
           "with f(O) = 1 and objective 23/41 (primal side of the same LP)", ok2,
           f"{len(rows)} rows, {nbad} violated, f(O) = {f[Om]}, "
           f"f(T) = {f[(1 << K) - 1]}")
    out['primal_feasible_rows'] = len(rows)
    out['primal_violated_rows'] = nbad
    # B3: independent verifier (results/F4_submodular_ftilde.py, unmodified)
    try:
        sys.path.insert(0, HERE)
        from F4_submodular_ftilde import verify_instance  # noqa: E402
        v3 = verify_instance(n, K, np.array([float(z) for z in f]),
                             np.array([float(z) for z in g]),
                             float(ETA_U), float(ETA_O))
        ok3 = (v3['f_empty'] and v3['monotone_f'] and v3['submodular_f'] and
               v3['monotone_ftilde'] and v3['submodular_ftilde'] and
               v3['band_ok'] and v3['greedy_picks_0..K-1'] and v3['opt_is_one']
               and abs(v3['ratio'] - float(TARGET)) < 1e-12)
        record("B3: F4's own verifier (unmodified) accepts the instance", ok3,
               f"ratio = {v3['ratio']:.12f}, eta realised = "
               f"{v3['eta_u_realised']:.6f} * {v3['eta_o_realised']:.6f}")
        out['F4_verifier'] = {k: (float(z) if isinstance(z, float) else bool(z))
                              for k, z in v3.items() if k != 'greedy_trace'}
    except Exception as exc:                                  # pragma: no cover
        record("B3: F4's own verifier (unmodified) accepts the instance", False,
               f"import/eval failed: {exc}")
    RESULTS['B_instance'] = out


# ---------------------------------------------------------------------------
# Part C: exact rational dual certificates (lower side)
# ---------------------------------------------------------------------------
def permute_set(S, p, n=N_GROUND):
    T = 0
    for u in range(n):
        if S >> u & 1:
            T |= 1 << p[u]
    return T


def row_image(tag, meta, p, n=N_GROUND):
    if tag in ("mono_f", "mono_g"):
        S, e = meta
        return (tag, permute_set(S, p, n), p[e])
    if tag in ("submod_f", "submod_g"):
        S, e, e2 = meta
        a, b = sorted((p[e], p[e2]))
        return (tag, permute_set(S, p, n), a, b)
    if tag in ("band_lo", "band_hi"):
        A, e = meta
        return (tag, permute_set(A, p, n), p[e])
    if tag == "greedy":
        t, e = meta
        return (tag, t, p[e])
    raise ValueError(tag)


def row_ident(tag, meta, n=N_GROUND):
    return row_image(tag, meta, tuple(range(n)), n)


def reduced_dual_system(rows, O, group, n=N_GROUND, K=K_BUDGET):
    """Symmetry-reduced dual equations.

    A dual multiplier vector may be averaged over the group G = group without
    losing feasibility or objective, so we may look for lambda constant on row
    orbits.  With  lambda_r = mu_{orbit(r)},  the dual equation for variable v
    reads  sum_omega mu_omega * (sum_{r in omega} a_{r,v}) = y [v = f(O)] - c_v,
    and it is the same equation for all v in one variable orbit.

    Returns (var_orbit_reps, row_orbits, Ahat, rhs_c, rhs_y) with
      Ahat[omega][vrep] = sum_{r in omega} a_{r, vrep}   (Fractions)
    """
    N = 1 << n
    # variable orbits
    vrep = {}
    for S in range(1, N):
        img = min(permute_set(S, p, n) for p in group)
        vrep[S] = img
    var_reps = sorted(set(vrep.values()))
    # row orbits: bucket every row under its canonical image in the group orbit
    buckets = {}
    for i, (tag, meta, _c) in enumerate(rows):
        img = min(row_image(tag, meta, p, n) for p in group)
        buckets.setdefault(img, []).append(i)
    orbits = sorted(buckets.keys(), key=lambda z: (str(z[0]), z[1:]))
    # Ahat
    Ahat = []
    for img in orbits:
        acc = {}
        for i in buckets[img]:
            tag, meta, coefs = rows[i]
            for k, val in coefs.items():
                S = k if k < N else k - N
                base = 0 if k < N else N
                key = base + vrep[S]
                acc[key] = acc.get(key, Fr(0)) + val
        Ahat.append({k: v for k, v in acc.items() if v != 0})
    cols = [S for S in var_reps] + [N + S for S in var_reps]
    return cols, orbits, buckets, Ahat, vrep


def solve_reduced_dual(cols, orbits, Ahat, O, K=K_BUDGET, n=N_GROUND,
                       y_fixed=None, sparsify=True):
    """Find mu >= 0 (and y) with  sum_omega mu_omega Ahat[omega] = y e_{f(O)} - c.

    With y_fixed given, this is a feasibility LP (min sum mu -> sparse vertex).
    With y free, maximise y (the symmetry-reduced dual LP).
    """
    N = 1 << n
    cidx = {c: i for i, c in enumerate(cols)}
    Om = sum(1 << i for i in O)
    T = (1 << K) - 1
    nrow = len(cols)
    ncol = len(orbits) + (0 if y_fixed is not None else 1)
    r, c, v = [], [], []
    for j, acc in enumerate(Ahat):
        for k, val in acc.items():
            r.append(cidx[k])
            c.append(j)
            v.append(float(val))
    rhs = np.zeros(nrow)
    rhs[cidx[T]] -= 1.0                       # -c
    if y_fixed is not None:
        rhs[cidx[Om]] += float(y_fixed)
    else:
        r.append(cidx[Om])
        c.append(len(orbits))
        v.append(-1.0)                        # move y to the left-hand side
    A = coo_matrix((v, (r, c)), shape=(nrow, ncol)).tocsr()
    if y_fixed is not None:
        obj = np.ones(ncol) if sparsify else np.zeros(ncol)
        bounds = [(0, None)] * ncol
    else:
        obj = np.zeros(ncol)
        obj[-1] = -1.0
        bounds = [(0, None)] * len(orbits) + [(None, None)]
    res = linprog(obj, A_eq=A, b_eq=rhs, bounds=bounds, method="highs")
    return res, A, rhs, cidx


def exact_solve_support(cols, orbits, Ahat, O, support, y_fixed, K=K_BUDGET,
                        n=N_GROUND):
    """Solve  sum_{omega in support} mu_omega Ahat[omega] = y e_{f(O)} - c
    exactly over Fraction, by Gaussian elimination on the support columns."""
    N = 1 << n
    cidx = {c: i for i, c in enumerate(cols)}
    Om = sum(1 << i for i in O)
    T = (1 << K) - 1
    nrow = len(cols)
    # rows of the linear system, as sparse dicts over support positions
    M = [dict() for _ in range(nrow)]
    for j, om in enumerate(support):
        for k, val in Ahat[om].items():
            M[cidx[k]][j] = val
    rhs = [Fr(0)] * nrow
    rhs[cidx[T]] -= 1
    rhs[cidx[Om]] += y_fixed
    m = len(support)
    # sparse Gaussian elimination with Markowitz-ish pivoting
    rows_left = list(range(nrow))
    piv_col = {}
    order = []
    used = [False] * nrow
    for _ in range(m):
        # choose the pivot column not yet used, with the sparsest viable row
        best = None
        for j in range(m):
            if j in piv_col:
                continue
            cand = [i for i in rows_left if (not used[i]) and M[i].get(j)]
            if not cand:
                continue
            i = min(cand, key=lambda i: len(M[i]))
            if best is None or len(M[i]) < best[2]:
                best = (i, j, len(M[i]))
        if best is None:
            break
        i, j, _ = best
        piv_col[j] = i
        used[i] = True
        order.append((i, j))
        pv = M[i][j]
        for i2 in rows_left:
            if i2 == i or not M[i2].get(j):
                continue
            fac = M[i2][j] / pv
            for k2, val in M[i].items():
                nv = M[i2].get(k2, Fr(0)) - fac * val
                if nv == 0:
                    M[i2].pop(k2, None)
                else:
                    M[i2][k2] = nv
            rhs[i2] = rhs[i2] - fac * rhs[i]
    # back-substitute
    mu = [Fr(0)] * m
    for i, j in reversed(order):
        s = rhs[i]
        for k2, val in M[i].items():
            if k2 != j:
                s -= val * mu[k2]
        mu[j] = s / M[i][j]
    # consistency of the rows that were not used as pivots
    resid_ok = True
    for i in range(nrow):
        if used[i]:
            continue
        s = Fr(0)
        for k2, val in M[i].items():
            s += val * mu[k2]
        if s != rhs[i]:
            resid_ok = False
            break
    return mu, resid_ok


def verify_dual_exact(rows, buckets, orbits, support, mu, O, y, K=K_BUDGET,
                      n=N_GROUND):
    """Lift mu back to the FULL row set and check A' lambda = y e_{f(O)} - c
    coefficient by coefficient, in Fraction arithmetic."""
    N = 1 << n
    lam = {}
    for pos, om in enumerate(support):
        if mu[pos] == 0:
            continue
        # a group-invariant multiplier vector is CONSTANT on each row orbit
        for i in buckets[orbits[om]]:
            lam[i] = lam.get(i, Fr(0)) + mu[pos]
    acc = {}
    for i, val in lam.items():
        _tag, _meta, coefs = rows[i]
        for k, a in coefs.items():
            acc[k] = acc.get(k, Fr(0)) + val * a
    target = {}
    target[(1 << K) - 1] = target.get((1 << K) - 1, Fr(0)) - 1
    Om = sum(1 << i for i in O)
    target[Om] = target.get(Om, Fr(0)) + y
    target = {k: v for k, v in target.items() if v != 0}
    acc = {k: v for k, v in acc.items() if v != 0}
    ok = (acc == target)
    nonneg = all(v >= 0 for v in lam.values())
    return ok, nonneg, lam


def transport_certificate(rows, row_index, lam, p, n=N_GROUND):
    """Push a multiplier vector through a relabelling p of the ground set."""
    out = {}
    for i, val in lam.items():
        tag, meta, _c = rows[i]
        out[row_index[row_image(tag, meta, p, n)]] = val
    return out


def check_identity_exact(rows, lam, O, y, K=K_BUDGET, n=N_GROUND):
    acc = {}
    for i, val in lam.items():
        _tag, _meta, coefs = rows[i]
        for k, a in coefs.items():
            acc[k] = acc.get(k, Fr(0)) + val * a
    acc = {k: v for k, v in acc.items() if v != 0}
    target = {(1 << K) - 1: Fr(-1)}
    Om = sum(1 << i for i in O)
    target[Om] = target.get(Om, Fr(0)) + y
    target = {k: v for k, v in target.items() if v != 0}
    return acc == target and all(v >= 0 for v in lam.values())


def part_C(orbits_to_do=None, y_mode='target', time_budget=None):
    print("\n=== Part C: exact rational dual certificates (lower side) ===")
    n, K = N_GROUND, K_BUDGET
    rows = build_rows()
    row_index = {row_ident(tag, meta, n): i for i, (tag, meta, _c) in enumerate(rows)}
    reps = orbit_reps(n, K)
    keys = sorted(reps.keys(), key=lambda z: (len(z[0]), z))
    out = []
    n_members_ok = 0
    t_start = time.time()
    for ki, key in enumerate(keys):
        if orbits_to_do is not None and ki not in orbits_to_do:
            continue
        if time_budget and time.time() - t_start > time_budget:
            print(f"   [budget] stopping before orbit {ki}")
            break
        O = reps[key][0]
        t0 = time.time()
        group = orbit_group(O, n, K)
        cols, orbs, buckets, Ahat, _vrep = reduced_dual_system(rows, O, group, n, K)
        res, _A, _rhs, _cidx = solve_reduced_dual(cols, orbs, Ahat, O, K, n,
                                                  y_fixed=TARGET)
        status = res.status
        entry = {'orbit_index': ki, 'orbit_key': str(key), 'O': str(O),
                 'orbit_size': len(reps[key]), 'group_order': len(group),
                 'n_var_orbits': len(cols), 'n_row_orbits': len(orbs),
                 'lp_status': int(status)}
        if status != 0:
            entry['exact'] = False
            entry['note'] = 'feasibility LP at y = 23/41 failed'
            print(f"   orbit {ki} {key}: dual feasibility LP status {status}")
            out.append(entry)
            continue
        x = res.x
        supp = [j for j in range(len(orbs)) if x[j] > 1e-9]
        entry['support_size'] = len(supp)
        mu, consistent = exact_solve_support(cols, orbs, Ahat, O, supp, TARGET, K, n)
        nonneg = all(v >= 0 for v in mu)
        ok, nn2, lam = verify_dual_exact(rows, buckets, orbs, supp, mu, O, TARGET, K, n)
        entry['exact_system_consistent'] = bool(consistent)
        entry['mu_nonnegative'] = bool(nonneg and nn2)
        entry['full_lift_identity_ok'] = bool(ok)
        entry['exact'] = bool(consistent and nonneg and nn2 and ok)
        entry['n_full_rows_used'] = len(lam)
        entry['y'] = str(TARGET)
        # transport the certificate to every other member of the orbit and
        # re-verify the identity there (exact, no LP)
        members_ok = 0
        if entry['exact']:
            for Op in reps[key]:
                p = None
                for q in itertools.permutations(range(K, n)):
                    cand = tuple(range(K)) + q
                    if tuple(sorted(cand[u] for u in O)) == tuple(sorted(Op)):
                        p = cand
                        break
                if p is None:
                    continue
                lam2 = transport_certificate(rows, row_index, lam, p, n)
                if check_identity_exact(rows, lam2, Op, TARGET, K, n):
                    members_ok += 1
        entry['orbit_members_verified'] = members_ok
        n_members_ok += members_ok
        entry['dual'] = [{'orbit': str(orbs[j]), 'mu': str(mu[pos]),
                          'n_rows_in_orbit': len(buckets[orbs[j]])}
                         for pos, j in enumerate(supp) if mu[pos] != 0]
        entry['seconds'] = round(time.time() - t0, 1)
        print(f"   orbit {ki} {key}: |G|={len(group)} varorb={len(cols)} "
              f"roworb={len(orbs)} supp={len(supp)} -> exact={entry['exact']} "
              f"members {members_ok}/{len(reps[key])} ({entry['seconds']}s)")
        sys.stdout.flush()
        out.append(entry)
    done = [e for e in out if e.get('exact')]
    record("C1: exact rational dual certificate at y = 23/41 per orbit",
           len(done) == len(out) and len(out) > 0,
           f"{len(done)}/{len(out)} orbits attempted closed exactly")
    record("C2: certificate transported to every target set in each orbit "
           "and re-verified exactly",
           n_members_ok == sum(e['orbit_size'] for e in done),
           f"{n_members_ok} of the 70 target sets carry an exact certificate")
    # tightness probe: no dual can certify more than 23/41 at the argmin orbit
    Odis = tuple(range(K, 2 * K))
    grp = orbit_group(Odis, n, K)
    cols, orbs, buckets, Ahat, _v = reduced_dual_system(rows, Odis, grp, n, K)
    probes = []
    for eps in (Fr(1, 10000), Fr(1, 1000)):
        r2, *_ = solve_reduced_dual(cols, orbs, Ahat, Odis, K, n,
                                    y_fixed=TARGET + eps)
        probes.append({'y': str(TARGET + eps), 'lp_status': int(r2.status),
                       'feasible': r2.status == 0})
    record("C3: the dual system is infeasible at y > 23/41 on the argmin orbit "
           "(the certificate is tight, not a loose bound)",
           all(not p['feasible'] for p in probes),
           ", ".join(f"y={p['y']}: status {p['lp_status']}" for p in probes))
    RESULTS['C_duals'] = {'orbits': out, 'n_exact': len(done),
                          'n_orbits_total': 16,
                          'n_target_sets_certified': n_members_ok,
                          'tightness_probe': probes}


# ---------------------------------------------------------------------------
def part_D():
    print("\n=== Part D: comparison numbers ===")
    K = K_BUDGET
    u = UK(K, ETA)
    v, j = min_V(K, ETA)
    w, m = min_W(K, ETA)
    l = LK(K, ETA)
    gt = TARGET > u
    lhs = TARGET.numerator * u.denominator
    rhs = u.numerator * TARGET.denominator
    record("D1: 23/41 > U_4(3/2) = 8080/14641 exactly", gt,
           f"23*14641 = {lhs} > {rhs} = 41*8080")
    RESULTS['D_comparison'] = {
        'rho_sub': str(TARGET), 'rho_sub_float': float(TARGET),
        'U_4': str(u), 'U_4_float': float(u),
        'rho_4_minjVj': str(v), 'rho_4_float': float(v), 'argmin_j': j,
        'L_4': str(l), 'L_4_float': float(l),
        'min_m_Wm': str(w), 'argmin_m': m,
        'cross_multiplication': f"{lhs} > {rhs}"}
    for k2, val in RESULTS['D_comparison'].items():
        print(f"   {k2}: {val}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--parts', default='ABCD')
    ap.add_argument('--quick', action='store_true')
    ap.add_argument('--orbits', default=None,
                    help='comma separated orbit indices for Part C')
    ap.add_argument('--budget', type=float, default=None,
                    help='seconds budget for Part C')
    ap.add_argument('--out', default='M3_rhosub_K4_exact.json')
    args = ap.parse_args()
    t0 = time.time()
    if 'A' in args.parts:
        part_A(args.quick)
    if 'B' in args.parts:
        part_B()
    if 'C' in args.parts:
        todo = (None if not args.orbits else
                set(int(z) for z in args.orbits.split(',')))
        part_C(todo, time_budget=args.budget)
    if 'D' in args.parts:
        part_D()
    RESULTS['checks'] = CHECKS
    RESULTS['seconds'] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, args.out), 'w') as fh:
        json.dump(RESULTS, fh, indent=1, default=str)
    npass = sum(1 for c in CHECKS if c['pass'])
    print(f"\n=== {npass}/{len(CHECKS)} checks PASS, {time.time()-t0:.0f}s ===")
    print(f"file: results/{args.out}")
    sys.exit(0 if npass == len(CHECKS) else 1)


if __name__ == "__main__":
    main()
