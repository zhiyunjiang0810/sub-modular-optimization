"""
H-E (TASKS6.md): the exact deterministic unbounded-query ceiling for n < 2K.

Theorem thm:ceiling (ledger card T8) proves the 1/eta ceiling only for n >= 2K,
because its construction needs a K-set O disjoint from the algorithm's output.
For n < 2K every K-set O overlaps the output in m = |S_out cap O| >= 2K - n
elements, and the overlap must lift the ceiling above 1/eta.  This script
computes the exact value by full-lattice LP and matches it to a closed form.

Setting (the classical uninformative-prediction family behind T8):
  * ground set N = {0, ..., n-1}, K <= n < 2K;
  * ftilde(S) = b|S| (symmetric, modular).  Every single-element predicted gain
    equals b, so ftilde carries no information: a deterministic algorithm with
    arbitrary query access to ftilde has a transcript that does not depend on
    the true f, hence outputs one FIXED set S_out.  Relabelling maps any K-set
    to any other and fixes ftilde, so S_out = {0,...,K-1} is w.l.o.g.
  * the adversary then picks f (monotone, submodular, f(empty)=0) inside the
    Definition 1 band against ftilde, and the optimum O among K-sets.

Definition 1 with ftilde = b|S| reads, for every A and e not in A,
      d_e(A)/eta_u <= b <= eta_o d_e(A)   <=>   b/eta_o <= d_e(A) <= b eta_u,
so the band degenerates into a two-sided box on the true marginal gains.

LPs solved here
  LP-A (ceiling / adversary LP), variables f(A) for all A subseteq N plus the
  predicted unit gain b (a variable, see build_ceiling_rows):
      min f(S_out)
      s.t. f(empty) = 0, submodularity, b/eta_o <= d_e(A) <= b eta_u for all
           A, e not in A, f(A) <= 1 for all |A| <= K, and f(O_m) = 1
      for a canonical K-set O_m with |O_m cap S_out| = m.
      Enumerating which K-set attains the max is how "max_{|A|<=K} f(A) = 1" is
      imposed; all K-sets with the same m are equivalent under the stabiliser of
      S_out, so one representative per m suffices.  The adversary's value is
      min over m in {2K-n, ..., K}.

  LP-B (matching algorithmic side), variables f(A) and ftilde(A):
      the exact worst case of EXHAUSTIVE SEARCH over predicted values
      (Shat = argmax_{|A|<=K} ftilde(A)) at n < 2K, with ftilde free (not the
      symmetric family).  Same normalisation; extra rows ftilde(Shat) >=
      ftilde(A) for all |A| <= K, Shat = {0,...,K-1} w.l.o.g.
      LP-A is an UPPER bound on the ceiling (one adversary family), LP-B a
      LOWER bound (one algorithm), so the exact ceiling is squeezed when they
      agree.

Closed form conjectured and then proved (see H_E_ceiling_small_n.md):
      C(n, K, eta) = K / (m0 + (K - m0) eta),      m0 = max(0, 2K - n)
                   = 1 / ((1 - lam) eta + lam),    lam = m0 / K,
  i.e. the harmonic interpolation between 1/eta (n >= 2K) and 1 (n = K).
  Per overlap type m the LP value is K / (m + (K - m) eta), increasing in m,
  so the adversary takes m = m0.

What came out (details and status tags in H_E_ceiling_small_n.md):
  * LP-A equals K/(m + (K-m) eta) at all 84 grid points (max error 3.34e-16),
    and the min over m sits at m = m0, so the ceiling is C = K/(m0+(K-m0)eta);
    n = 2K reproduces T8's 1/eta.                             [VERIFIED-LP]
  * LP-B equals LP-A at all 18 (n,K,eta) points and per overlap type m, i.e.
    exhaustive search attains the ceiling on this grid.  [VERIFIED-LP at grid]
  * The natural two-step hand proof of the LP-B side FAILS: the intermediate
    quantity min f(Shat cap O) is 0 (objective="I" below), so the bound cannot
    be assembled as (P1) + (P2); see md section 5.                   [FAILED]

Usage:
    python3 H_E_ceiling_small_n.py            # full run, writes the JSON
    python3 H_E_ceiling_small_n.py --quick    # LP-A grid only

Status of the produced claims: see the md.  This file is self-contained; it
does not import from code/ and does not modify anything.
"""
import itertools
import json
import os
import sys
import time
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(HERE, "H_E_ceiling_small_n.json")
TOL = 1e-9

GRID_K = [2, 3, 4]
GRID_ETA = [1.5, 2.0, 3.0]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def bits(S):
    return bin(S).count("1")


def subsets_upto(n, K):
    """All subsets of [n] of size <= K, as bitmasks."""
    out = []
    for S in range(1 << n):
        if bits(S) <= K:
            out.append(S)
    return out


def canonical_O(n, K, m):
    """K-set with |O cap {0..K-1}| = m: first m of S_out plus K-m outside."""
    assert 0 <= m <= K and 2 * K - m <= n, (n, K, m)
    elts = list(range(m)) + list(range(K, K + (K - m)))
    return sum(1 << e for e in elts), tuple(elts)


class RowBuilder:
    def __init__(self, nv):
        self.nv = nv
        self.rows, self.cols, self.vals, self.b = [], [], [], []
        self.nrow = 0
        self.counts = {}

    def add(self, coefs, rhs=0.0):
        for k, v in coefs.items():
            if v != 0.0:
                self.rows.append(self.nrow)
                self.cols.append(k)
                self.vals.append(float(v))
        self.b.append(float(rhs))
        self.nrow += 1

    def mark(self, name, start):
        self.counts[name] = self.nrow - start

    def matrix(self):
        A = coo_matrix((self.vals, (self.rows, self.cols)),
                       shape=(self.nrow, self.nv)).tocsr()
        return A, np.array(self.b, dtype=float)


# ---------------------------------------------------------------------------
# LP-A: ceiling LP (ftilde = b|S| fixed, variables f only)
# ---------------------------------------------------------------------------
def build_ceiling_rows(n, K, eta_u, eta_o):
    """A_ub x <= b_ub for the f-only lattice LP.

    Variables: f(A) at index = bitmask A, plus the predicted unit gain b at
    index N.  b is a VARIABLE, not a constant: the objective is the ratio
    f(S_out)/max_{|A|<=K} f(A), which is invariant under f -> cf, so the
    normalisation max = 1 uses up the scale of f and the scale of ftilde must
    then be free.  Keeping b free is also exactly the scaling argument that
    makes the value depend on eta_u eta_o only (see run_split_check).
    """
    N = 1 << n
    rb = RowBuilder(N + 1)
    B = N

    # submodularity: d_e(A | e2) <= d_e(A)   (adjacent form implies the rest)
    start = rb.nrow
    for A in range(N):
        for e in range(n):
            if A >> e & 1:
                continue
            for e2 in range(n):
                if e2 == e or A >> e2 & 1:
                    continue
                T = A | 1 << e2
                c = {}
                for k, v in ((T | 1 << e, 1), (T, -1), (A | 1 << e, -1), (A, 1)):
                    c[k] = c.get(k, 0) + v
                rb.add(c)
    rb.mark("submodular", start)

    # band (Definition 1, single-element form) with dtilde_e(A) = b:
    #   d_e(A) <= b * eta_u          and     d_e(A) >= b / eta_o
    start = rb.nrow
    for A in range(N):
        for e in range(n):
            if A >> e & 1:
                continue
            Ae = A | 1 << e
            rb.add({Ae: 1.0, A: -1.0, B: -eta_u}, 0.0)         # d <= b eta_u
            rb.add({Ae: -1.0, A: 1.0, B: 1.0 / eta_o}, 0.0)    # d >= b / eta_o
    rb.mark("band", start)

    # monotone: implied by the lower band (d >= b/eta_o > 0); kept explicitly
    start = rb.nrow
    for A in range(N):
        for e in range(n):
            if not A >> e & 1:
                rb.add({A: 1.0, A | 1 << e: -1.0})
    rb.mark("monotone", start)

    # normalisation half: f(A) <= 1 for every |A| <= K
    start = rb.nrow
    for A in subsets_upto(n, K):
        rb.add({A: 1.0}, 1.0)
    rb.mark("cap", start)

    return rb


def ceiling_value(n, K, eta_u, eta_o, m, prebuilt=None, want_x=False,
                  fix_b=None):
    """LP-A value for one overlap type m."""
    if prebuilt is None:
        prebuilt = build_ceiling_rows(n, K, eta_u, eta_o)
    A_ub, b_ub = prebuilt.matrix()
    nv = prebuilt.nv
    N = 1 << n
    Om, _ = canonical_O(n, K, m)
    S_out = (1 << K) - 1

    obj = np.zeros(nv)
    obj[S_out] = 1.0
    eq_rows, eq_cols, eq_vals, rhs = [0, 1], [0, Om], [1.0, 1.0], [0.0, 1.0]
    if fix_b is not None:
        eq_rows.append(2)
        eq_cols.append(N)
        eq_vals.append(1.0)
        rhs.append(float(fix_b))
    A_eq = coo_matrix((eq_vals, (eq_rows, eq_cols)),
                      shape=(len(rhs), nv)).tocsr()
    bounds = [(None, None)] * N + [(0.0, None)]
    res = linprog(obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=rhs,
                  bounds=bounds, method="highs")
    if res.status != 0:
        return None, res
    return (float(res.fun), res.x if want_x else None), res


def closed_form(K, m, eta):
    return K / (m + (K - m) * eta)


# ---------------------------------------------------------------------------
# LP-B: exact worst case of exhaustive search over predicted values
# ---------------------------------------------------------------------------
def build_exhaustive_rows(n, K, eta_u, eta_o):
    """Variables: f(A) at index A, ftilde(A) at index N + A."""
    N = 1 << n
    rb = RowBuilder(2 * N)
    F = lambda A: A            # noqa: E731
    G = lambda A: N + A        # noqa: E731

    start = rb.nrow
    for A in range(N):
        for e in range(n):
            if A >> e & 1:
                continue
            for e2 in range(n):
                if e2 == e or A >> e2 & 1:
                    continue
                T = A | 1 << e2
                c = {}
                for k, v in ((F(T | 1 << e), 1), (F(T), -1),
                             (F(A | 1 << e), -1), (F(A), 1)):
                    c[k] = c.get(k, 0) + v
                rb.add(c)
    rb.mark("submodular", start)

    start = rb.nrow
    for A in range(N):
        for e in range(n):
            if not A >> e & 1:
                rb.add({F(A): 1.0, F(A | 1 << e): -1.0})
    rb.mark("monotone", start)

    # band: d_e(A)/eta_u <= dtilde_e(A) <= eta_o d_e(A)
    start = rb.nrow
    for A in range(N):
        for e in range(n):
            if A >> e & 1:
                continue
            Ae = A | 1 << e
            c = {}
            for k, v in ((F(Ae), 1.0 / eta_u), (F(A), -1.0 / eta_u),
                         (G(Ae), -1.0), (G(A), 1.0)):
                c[k] = c.get(k, 0) + v
            rb.add(c)
            c = {}
            for k, v in ((G(Ae), 1.0), (G(A), -1.0),
                         (F(Ae), -eta_o), (F(A), eta_o)):
                c[k] = c.get(k, 0) + v
            rb.add(c)
    rb.mark("band", start)

    # exhaustive search picks Shat = {0..K-1}: ftilde(Shat) >= ftilde(A), |A|<=K
    start = rb.nrow
    S_out = (1 << K) - 1
    for A in subsets_upto(n, K):
        if A == S_out:
            continue
        rb.add({G(A): 1.0, G(S_out): -1.0})
    rb.mark("argmax", start)

    start = rb.nrow
    for A in subsets_upto(n, K):
        rb.add({F(A): 1.0}, 1.0)
    rb.mark("cap", start)

    return rb


def exhaustive_value(n, K, eta_u, eta_o, m, prebuilt=None, objective="Shat",
                     want_x=False):
    """objective="Shat": worst case of exhaustive search (min f(Shat)).
       objective="I":    min f(Shat cap O_m), the intermediate quantity of the
                         two-step proof sketch in the md (step (P2))."""
    if prebuilt is None:
        prebuilt = build_exhaustive_rows(n, K, eta_u, eta_o)
    A_ub, b_ub = prebuilt.matrix()
    nv = prebuilt.nv
    N = 1 << n
    Om, _ = canonical_O(n, K, m)
    S_out = (1 << K) - 1

    obj = np.zeros(nv)
    obj[S_out if objective == "Shat" else (S_out & Om)] = 1.0
    A_eq = coo_matrix(([1.0, 1.0, 1.0], ([0, 1, 2], [0, N, Om])),
                      shape=(3, nv)).tocsr()
    res = linprog(obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=[0.0, 0.0, 1.0],
                  bounds=[(None, None)] * nv, method="highs")
    if res.status != 0:
        return None, res
    return float(res.fun), res


# ---------------------------------------------------------------------------
# exact (Fraction) feasibility certificate for the conjectured optimal f
# ---------------------------------------------------------------------------
def witness_check(n, K, m, eta_num, eta_den):
    """The witness attaining K/(m+(K-m)eta): modular f with weight eta on the
    K-m elements of O_m \\ S_out and weight 1 everywhere else, rescaled by
    1/sqrt(eta) ... to avoid square roots we verify the band in the equivalent
    product form b/eta_o <= d <= b eta_u with b = eta_o (see md, step 0).

    Returns a dict of exact checks (all must be True).
    """
    eta = Fraction(eta_num, eta_den)
    S_out = set(range(K))
    _, O_elts = canonical_O(n, K, m)
    heavy = set(O_elts) - S_out                       # the K-m heavy elements
    w = {e: (eta if e in heavy else Fraction(1)) for e in range(n)}

    def f(A):
        return sum(w[e] for e in A)

    checks = {}
    # modular => submodular and monotone with all marginals in [1, eta]
    checks["marginals_in_band"] = all(Fraction(1) <= w[e] <= eta
                                      for e in range(n))
    # max over K-sets
    best = max(sum(sorted((w[e] for e in A), reverse=True))
               for A in itertools.combinations(range(n), K))
    fO = f(O_elts)
    checks["O_attains_max"] = (fO == best)
    checks["f_Sout"] = f(S_out)
    checks["f_O"] = fO
    ratio = Fraction(f(S_out), 1) / fO
    checks["ratio"] = ratio
    checks["ratio_equals_closed_form"] = (
        ratio == Fraction(K, 1) / (Fraction(m) + Fraction(K - m) * eta))
    return checks


# ---------------------------------------------------------------------------
# runs
# ---------------------------------------------------------------------------
def run_grid_A(quick=False):
    print("=" * 74)
    print("LP-A: ceiling LP (ftilde = b|S|, eta_u = eta_o = sqrt(eta))")
    print("=" * 74)
    rows = []
    for K in GRID_K:
        # n = 2K is included as a sanity row: it must reproduce T8's 1/eta.
        for n in list(range(K + 1, 2 * K)) + [2 * K]:
            for eta in GRID_ETA:
                s = float(np.sqrt(eta))
                pre = build_ceiling_rows(n, K, s, s)
                m0 = max(0, 2 * K - n)
                per_m, t0 = {}, time.perf_counter()
                for m in range(m0, K + 1):
                    (val, _), res = ceiling_value(n, K, s, s, m, prebuilt=pre)
                    cf = closed_form(K, m, eta)
                    per_m[m] = (val, cf, abs(val - cf))
                dt = time.perf_counter() - t0
                vmin = min(v[0] for v in per_m.values())
                argm = min(per_m, key=lambda k: per_m[k][0])
                cf_min = closed_form(K, m0, eta)
                ok = all(v[2] < TOL for v in per_m.values())
                rows.append(dict(K=K, n=n, eta=eta, m0=m0,
                                 per_m={str(k): dict(lp=v[0], cf=v[1],
                                                     err=v[2])
                                        for k, v in per_m.items()},
                                 lp_min=vmin, argmin_m=argm,
                                 closed_form=cf_min,
                                 one_over_eta=1.0 / eta,
                                 match=bool(ok and abs(vmin - cf_min) < TOL),
                                 seconds=dt))
                print(f"K={K} n={n} eta={eta}: m0={m0} "
                      f"min={vmin:.9f} cf={cf_min:.9f} 1/eta={1/eta:.6f} "
                      f"argmin_m={argm} match={rows[-1]['match']} "
                      f"({dt:.1f}s)")
                for m in sorted(per_m):
                    v = per_m[m]
                    print(f"      m={m}: LP={v[0]:.9f}  K/(m+(K-m)eta)="
                          f"{v[1]:.9f}  |diff|={v[2]:.2e}")
                if quick:
                    break
    return rows


def run_split_check():
    """Definition 1 allows any split (eta_u, eta_o) with eta_u*eta_o = eta.
    Ledger card T0 flags "value depends only on the product" as an LP
    observation plus a one-line scaling argument.  Here the argument is exact
    FOR THIS FAMILY: with ftilde = b|S| the feasible set is
    {f submodular : b/eta_o <= d_e(A) <= b eta_u}; substituting g = (eta_o/b) f
    turns it into {g submodular : 1 <= d_e(A) <= eta_u eta_o} independently of
    the split, and the objective f(S_out)/f(O) is invariant under positive
    scaling of f.  The numeric check below confirms it at several points.
    """
    print("=" * 74)
    print("split-dependence check (eta_u * eta_o = eta fixed)")
    print("=" * 74)
    out = []
    for (K, n, eta) in [(3, 5, 2.0), (3, 4, 3.0), (4, 6, 1.5), (2, 3, 3.0)]:
        m0 = max(0, 2 * K - n)
        vals = []
        splits = [(np.sqrt(eta), np.sqrt(eta)), (eta, 1.0), (1.0, eta),
                  (eta / 1.25, 1.25)]
        for (eu, eo) in splits:
            pre = build_ceiling_rows(n, K, eu, eo)
            v = min(ceiling_value(n, K, eu, eo, m, prebuilt=pre)[0][0]
                    for m in range(m0, K + 1))
            vals.append(v)
        spread = max(vals) - min(vals)
        rec = dict(K=K, n=n, eta=eta,
                   splits=[[float(a), float(b)] for a, b in splits],
                   values=vals, spread=spread,
                   product_only=bool(spread < TOL),
                   closed_form=closed_form(K, m0, eta))
        out.append(rec)
        print(f"K={K} n={n} eta={eta}: " +
              "  ".join(f"({a:.3f},{b:.3f})->{v:.9f}"
                        for (a, b), v in zip(splits, vals)) +
              f"   spread={spread:.2e}")
    # Third form: replace the band by its split-free consequence
    #   L <= d_e(A) <= U  with  U <= eta L,  L >= 0,
    # which is what the substitution above leaves.  If the product-only claim
    # is right for this family, this LP has the same value as every split.
    prod = []
    for (K, n, eta) in [(3, 5, 2.0), (3, 4, 3.0), (4, 6, 1.5), (2, 3, 3.0)]:
        m0 = max(0, 2 * K - n)
        v = min(product_form_value(n, K, eta, m)[0] for m in range(m0, K + 1))
        prod.append(dict(K=K, n=n, eta=eta, value=v,
                         closed_form=closed_form(K, m0, eta),
                         match=bool(abs(v - closed_form(K, m0, eta)) < TOL)))
        print(f"product-form LP (L <= d <= U <= eta L)  K={K} n={n} "
              f"eta={eta}: {v:.9f}  (closed form {closed_form(K, m0, eta):.9f})")
    return out, prod


def product_form_value(n, K, eta, m):
    """LP-A rewritten with the split eliminated: variables f, L, U."""
    N = 1 << n
    rb = RowBuilder(N + 2)
    L, U = N, N + 1
    for A in range(N):
        for e in range(n):
            if A >> e & 1:
                continue
            for e2 in range(n):
                if e2 == e or A >> e2 & 1:
                    continue
                T = A | 1 << e2
                c = {}
                for k, v in ((T | 1 << e, 1), (T, -1), (A | 1 << e, -1),
                             (A, 1)):
                    c[k] = c.get(k, 0) + v
                rb.add(c)
    for A in range(N):
        for e in range(n):
            if A >> e & 1:
                continue
            Ae = A | 1 << e
            rb.add({Ae: 1.0, A: -1.0, U: -1.0})      # d <= U
            rb.add({Ae: -1.0, A: 1.0, L: 1.0})       # d >= L
    rb.add({U: 1.0, L: -eta})                        # U <= eta L
    for A in subsets_upto(n, K):
        rb.add({A: 1.0}, 1.0)
    A_ub, b_ub = rb.matrix()
    Om, _ = canonical_O(n, K, m)
    S_out = (1 << K) - 1
    obj = np.zeros(rb.nv)
    obj[S_out] = 1.0
    A_eq = coo_matrix(([1.0, 1.0], ([0, 1], [0, Om])),
                      shape=(2, rb.nv)).tocsr()
    bounds = [(None, None)] * N + [(0.0, None), (0.0, None)]
    res = linprog(obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=[0.0, 1.0],
                  bounds=bounds, method="highs")
    return (float(res.fun) if res.status == 0 else None), res


def run_output_size_check():
    """The algorithm may output |S_out| < K.  Analytically the value
    s / ((s+K-n)_+ + (n - max(s, n-K+... )) eta) is increasing in s; check
    numerically that a smaller output is never better for the algorithm."""
    print("=" * 74)
    print("output-size check: does |S_out| < K help the algorithm?")
    print("=" * 74)
    out = []
    for (K, n, eta) in [(3, 5, 2.0), (3, 4, 2.0), (4, 6, 2.0)]:
        s_eta = float(np.sqrt(eta))
        pre = build_ceiling_rows(n, K, s_eta, s_eta)
        A_ub, b_ub = pre.matrix()
        nv = pre.nv
        bounds = [(None, None)] * (nv - 1) + [(0.0, None)]
        row = {}
        for s in range(1, K + 1):
            S_out = (1 << s) - 1
            best = np.inf
            for O in itertools.combinations(range(n), K):
                Om = sum(1 << e for e in O)
                obj = np.zeros(nv)
                obj[S_out] = 1.0
                A_eq = coo_matrix(([1.0, 1.0], ([0, 1], [0, Om])),
                                  shape=(2, nv)).tocsr()
                res = linprog(obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq,
                              b_eq=[0.0, 1.0], bounds=bounds,
                              method="highs")
                if res.status == 0:
                    best = min(best, float(res.fun))
            row[s] = best
        out.append(dict(K=K, n=n, eta=eta, by_size=row,
                        best_is_full_K=bool(
                            abs(row[K] - max(row.values())) < TOL)))
        print(f"K={K} n={n} eta={eta}: " +
              "  ".join(f"|S|={s}:{v:.9f}" for s, v in row.items()))
    return out


def run_grid_B():
    print("=" * 74)
    print("LP-B: exact worst case of exhaustive search over predicted values")
    print("=" * 74)
    rows = []
    cases = [(2, 3), (3, 4), (3, 5), (4, 5), (4, 6), (4, 7)]
    for (K, n) in cases:
        for eta in GRID_ETA:
            s = float(np.sqrt(eta))
            t0 = time.perf_counter()
            pre = build_exhaustive_rows(n, K, s, s)
            m0 = max(0, 2 * K - n)
            per_m, per_m_I = {}, {}
            for m in range(m0, K + 1):
                v, res = exhaustive_value(n, K, s, s, m, prebuilt=pre)
                per_m[m] = v
                # step (P2) of the proof sketch: min f(Shat cap O), whose
                # conjectured value is m/(m + (K-m) eta)
                vI, _ = exhaustive_value(n, K, s, s, m, prebuilt=pre,
                                         objective="I")
                per_m_I[m] = dict(lp=vI, conj=m / (m + (K - m) * eta),
                                  err=abs(vI - m / (m + (K - m) * eta)))
            dt = time.perf_counter() - t0
            vmin = min(v for v in per_m.values() if v is not None)
            cf = closed_form(K, m0, eta)
            rows.append(dict(K=K, n=n, eta=eta, m0=m0,
                             per_m={str(k): v for k, v in per_m.items()},
                             per_m_min_f_I={str(k): v
                                            for k, v in per_m_I.items()},
                             P2_holds=bool(all(
                                 v["lp"] >= v["conj"] - 1e-7
                                 for v in per_m_I.values())),
                             lpB_min=vmin, ceiling_lpA=cf,
                             one_over_eta=1.0 / eta,
                             equals_ceiling=bool(abs(vmin - cf) < 1e-7),
                             above_1_over_eta=bool(vmin > 1.0 / eta + 1e-7),
                             seconds=dt))
            print(f"K={K} n={n} eta={eta}: exhaustive worst case={vmin:.9f}  "
                  f"ceiling(LP-A)={cf:.9f}  1/eta={1/eta:.6f}  "
                  f"=ceiling? {rows[-1]['equals_ceiling']}  ({dt:.1f}s)")
            for m in sorted(per_m):
                pI = per_m_I[m]
                print(f"      m={m}: f(Shat)={per_m[m]:.9f}   "
                      f"min f(Shat cap O)={pI['lp']:.9f} "
                      f"(conj m/(m+(K-m)eta)={pI['conj']:.9f}, "
                      f"err={pI['err']:.1e})")
    return rows


def run_symbolic():
    """sympy verification of the two-sided argument behind the closed form."""
    import sympy as sp
    print("=" * 74)
    print("symbolic checks (sympy)")
    print("=" * 74)
    K, m, eta, x = sp.symbols("K m eta x", positive=True)
    out = {}

    # (1) lower bound  (x + K - m)/(x + (K-m) eta) is nondecreasing in x for
    #     eta >= 1, so it is minimised at x = m (its smallest feasible value).
    expr = (x + K - m) / (x + (K - m) * eta)
    dexpr = sp.simplify(sp.diff(expr, x))
    num = sp.simplify(sp.numer(sp.together(dexpr)))
    out["d/dx numerator"] = str(sp.factor(num))     # (K-m)(eta-1) >= 0
    out["monotone_in_x"] = bool(sp.simplify(sp.factor(num) -
                                            (K - m) * (eta - 1)) == 0)
    # (2) value at x = m is the closed form
    out["value_at_x=m"] = str(sp.simplify(expr.subs(x, m) -
                                          K / (m + (K - m) * eta)))
    # (3) K/(m + (K-m) eta) is nondecreasing in m for eta >= 1
    cf = K / (m + (K - m) * eta)
    dm = sp.simplify(sp.diff(cf, m))
    out["d/dm numerator"] = str(sp.factor(sp.numer(sp.together(dm))))
    # (4) n >= 2K (m0 = 0) recovers 1/eta; n = K (m0 = K) gives 1
    out["m=0 gives 1/eta"] = str(sp.simplify(cf.subs(m, 0) - 1 / eta))
    out["m=K gives 1"] = str(sp.simplify(cf.subs(m, K) - 1))
    # (5) harmonic form 1/((1-lam) eta + lam) with lam = m/K
    lam = sp.symbols("lam", positive=True)
    out["harmonic form"] = str(sp.simplify(
        cf.subs(m, lam * K) - 1 / ((1 - lam) * eta + lam)))
    # (6) strictly above 1/eta whenever m > 0 and eta > 1
    out["gap over 1/eta"] = str(sp.simplify(sp.together(cf - 1 / eta)))
    # (7) output size s <= K: s/((s+K-n) + (n-s) eta) increasing in s
    s, n = sp.symbols("s n", positive=True)
    g = s / ((s + K - n) + (n - s) * eta)
    dg = sp.simplify(sp.diff(g, s))
    out["d/ds numerator"] = str(sp.factor(sp.numer(sp.together(dg))))
    for k, v in out.items():
        print(f"  {k}: {v}")
    return out


def main():
    quick = "--quick" in sys.argv
    t_start = time.perf_counter()
    payload = {}

    payload["lpA"] = run_grid_A(quick=quick)
    if quick:
        print(json.dumps(payload["lpA"][-1], indent=2)[:400])
        return

    splits, prodform = run_split_check()
    payload["split_check"] = splits
    payload["product_form_check"] = prodform

    payload["output_size_check"] = run_output_size_check()

    print("=" * 74)
    print("exact witness certificates (Fraction arithmetic)")
    print("=" * 74)
    wit = []
    for (K, n, (en, ed)) in [(2, 3, (3, 2)), (3, 4, (2, 1)), (3, 5, (3, 1)),
                             (4, 5, (2, 1)), (4, 6, (3, 2)), (4, 7, (3, 1))]:
        m0 = max(0, 2 * K - n)
        c = witness_check(n, K, m0, en, ed)
        rec = dict(K=K, n=n, eta=f"{en}/{ed}", m=m0,
                   ratio=str(c["ratio"]),
                   ok=bool(c["marginals_in_band"] and c["O_attains_max"]
                           and c["ratio_equals_closed_form"]))
        wit.append(rec)
        print(f"  K={K} n={n} eta={en}/{ed} m={m0}: ratio={c['ratio']} "
              f"band_ok={c['marginals_in_band']} O_is_max={c['O_attains_max']} "
              f"matches_cf={c['ratio_equals_closed_form']}")
    payload["witness"] = wit

    payload["symbolic"] = run_symbolic()
    payload["lpB"] = run_grid_B()

    payload["meta"] = dict(seconds=time.perf_counter() - t_start,
                           grid_K=GRID_K, grid_eta=GRID_ETA, tol=TOL)
    with open(JSON_PATH, "w") as fh:
        json.dump(payload, fh, indent=1)
    print(f"\nwrote {JSON_PATH}  ({payload['meta']['seconds']:.1f}s)")

    # headline
    print("\nHEADLINE  C(n,K,eta) = K / ((2K-n) + (n-K) eta)")
    allmatch = all(r["match"] for r in payload["lpA"])
    print(f"  LP-A matches closed form at every grid point: {allmatch}")
    print(f"  split-independence: "
          f"{all(r['product_only'] for r in payload['split_check'])}")
    print(f"  exhaustive search attains the ceiling: "
          f"{all(r['equals_ceiling'] for r in payload['lpB'])}")
    print(f"  proof-sketch step (P2) holds at every LP-B point: "
          f"{all(r['P2_holds'] for r in payload['lpB'])}")


if __name__ == "__main__":
    main()
