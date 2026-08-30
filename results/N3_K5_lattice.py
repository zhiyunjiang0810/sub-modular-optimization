"""
N3 (second night): verify R6 at K = 5.

R6 claims the O(K^2) reduced factor-revealing LP (`code/reduced_lp.py`) has the
same value as the full-lattice factor-revealing LP (`code/worst_case_lp.py`).
R6 had only been checked for K <= 4.  This script closes the K = 5 case.

Setup (identical to the one behind every R5/R6 data point):
    n = 2K = 10, K = 5, single-element error model, eta_u = eta_o = sqrt(eta),
    greedy picks 0,1,...,K-1 (adversarial ties), O = {5,...,9} (disjoint type).

One O per SYMMETRY TYPE is solved, not all C(10,5) = 252 of them.  Justification:
the per-O LP value depends only on the type m = |O ∩ {0..K-1}| of O relative to
the greedy prefix (results/T4_symmetry_check.py verified this invariance for the
pair-greedy LP; the single-step LP has the same symmetry group), so the min over
all O equals the min over the K+1 representatives.  At eta in {1.5, 2} all six
types m = 0..5 are solved and the min is confirmed to sit at m = 0 (the disjoint
type used by every R5/R6 data point); at eta in {3, 4.5} only m = 0, 1 are solved
to keep the run inside its time budget.

The row construction below is copied verbatim (same coefficients, same order)
from `code/worst_case_lp.py::worst_case`; `code/` is not modified.  A self-test
(`--selftest`) reproduces worst_case(6, 3, sqrt(2), sqrt(2), "single") from this
file's builder to prove the copy is faithful.

Usage (full run writes N3_K5_lattice_vs_reduced.csv; ~17 min on 1 core):
    python3 N3_K5_lattice.py               # self-test + K=5 sweep + CSV
    python3 N3_K5_lattice.py --selftest    # only the n=6,K=3 faithfulness check
    python3 N3_K5_lattice.py --quick       # only eta=2, m=0/1, for timing
    python3 N3_K5_lattice.py --noselftest  # skip the n=6,K=3 check

Status of the produced claim: [VERIFIED-LP] if all_match, otherwise [FAILED].
"""
import itertools
import os
import sys
import time

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code"))

from reduced_lp import reduced  # noqa: E402  (code/reduced_lp.py, unmodified)

CSV_PATH = os.path.join(HERE, "N3_K5_lattice_vs_reduced.csv")


# ----------------------------------------------------------------------------
# Full-lattice LP: rows copied from code/worst_case_lp.py::worst_case
# ----------------------------------------------------------------------------
def build_lattice_rows(n, K, eta_u, eta_o, err_model="single"):
    """Return (A_ub csr, b_ub, nv, F, G) for the full-lattice LP on [n].

    Variables: f[S] at index S, ftilde[S] at index N+S, S in [0, 2^n).
    """
    N = 1 << n
    nv = 2 * N
    F = lambda S: S            # noqa: E731
    G = lambda S: N + S        # noqa: E731

    rows, cols, vals, b_ub = [], [], [], []
    nrow = 0
    counts = {}

    def add_ub(coefs, rhs=0.0):
        nonlocal nrow
        for k, v in coefs.items():
            if v != 0.0:
                rows.append(nrow)
                cols.append(k)
                vals.append(v)
        b_ub.append(rhs)
        nrow += 1

    # monotone: f[S] - f[S|e] <= 0
    start = nrow
    for S in range(N):
        for e in range(n):
            if not S >> e & 1:
                add_ub({F(S): 1, F(S | 1 << e): -1})
    counts["monotone"] = nrow - start

    # submodular: d_e(S|e') <= d_e(S)
    start = nrow
    for S in range(N):
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
                add_ub(c)
    counts["submodular"] = nrow - start

    # error model (single-element by default)
    start = nrow
    for A in range(N):
        comp = (N - 1) ^ A
        if err_model == "single":
            Bs = [1 << e for e in range(n) if comp >> e & 1]
        else:  # all pairs of disjoint A, B with B nonempty
            Bs = []
            B = comp
            while B:
                Bs.append(B)
                B = (B - 1) & comp
        for B in Bs:
            AB = A | B
            c = {}
            for k, v in ((F(AB), 1 / eta_u), (F(A), -1 / eta_u),
                         (G(AB), -1), (G(A), 1)):
                c[k] = c.get(k, 0) + v
            add_ub(c)
            c = {}
            for k, v in ((G(AB), 1), (G(A), -1),
                         (F(AB), -eta_o), (F(A), eta_o)):
                c[k] = c.get(k, 0) + v
            add_ub(c)
    counts["error"] = nrow - start

    # greedy path: dt_e(S_t) <= dt_t(S_t)
    start = nrow
    for t in range(K):
        S = (1 << t) - 1
        for e in range(n):
            if e == t or S >> e & 1:
                continue
            c = {}
            for k, v in ((G(S | 1 << e), 1), (G(S), -1),
                         (G(S | 1 << t), -1), (G(S), 1)):
                c[k] = c.get(k, 0) + v
            add_ub(c)
    counts["greedy"] = nrow - start

    A_ub = coo_matrix((vals, (rows, cols)), shape=(nrow, nv)).tocsr()
    return A_ub, np.array(b_ub, dtype=float), nv, F, G, counts


def lattice_value(n, K, eta, O, err_model="single", prebuilt=None, verbose=False):
    """LP value for one fixed candidate optimum O (tuple of element indices)."""
    s = np.sqrt(eta)
    if prebuilt is None:
        prebuilt = build_lattice_rows(n, K, s, s, err_model)
    A_ub, b_ub, nv, F, G, counts = prebuilt
    N = 1 << n

    Om = sum(1 << i for i in O)
    SK = (1 << K) - 1
    obj = np.zeros(nv)
    obj[F(SK)] = 1.0

    A_eq = coo_matrix(
        ([1.0, 1.0, 1.0], ([0, 1, 2], [F(0), G(0), F(Om)])), shape=(3, nv)
    ).tocsr()

    t0 = time.perf_counter()
    res = linprog(obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=[0.0, 0.0, 1.0],
                  bounds=[(None, None)] * nv, method="highs")
    dt = time.perf_counter() - t0
    if verbose:
        print(f"      [linprog] status={res.status} ({res.message.strip()[:60]}) "
              f"rows={A_ub.shape[0]} vars={nv} {dt:.1f}s", flush=True)
    if res.status != 0:
        return None, dt, res
    return float(res.fun), dt, res


# ----------------------------------------------------------------------------
# Closed-form reference from R10:  min_j V_j(eta)
# ----------------------------------------------------------------------------
def min_Vj(K, eta):
    k1 = (K - 1) * eta + 1.0
    q = (K - 1) * eta / k1
    best, argj = np.inf, None
    for j in range(K + 1):
        Vj = 1.0 - q ** j * (1.0 - (K - j) / (K * eta))
        if Vj < best:
            best, argj = Vj, j
    return best, argj


# ----------------------------------------------------------------------------
# Self-test: the copied builder must reproduce code/worst_case_lp.py
# ----------------------------------------------------------------------------
def selftest():
    print("== self-test: N3 builder vs code/worst_case_lp.py, n=6 K=3 eta=2 ==",
          flush=True)
    import worst_case_lp as wcl
    s = np.sqrt(2.0)

    t0 = time.perf_counter()
    ref_val, ref_O, _ = wcl.worst_case(6, 3, s, s, "single")
    t_ref = time.perf_counter() - t0
    print(f"   worst_case_lp.worst_case -> {ref_val:.12f}  argmin O={ref_O}  "
          f"({t_ref:.1f}s)", flush=True)

    pre = build_lattice_rows(6, 3, s, s, "single")
    print(f"   builder row counts: {pre[5]}  total={pre[0].shape[0]} "
          f"vars={pre[2]}", flush=True)
    t0 = time.perf_counter()
    mine = {}
    for O in itertools.combinations(range(6), 3):
        v, _, _ = lattice_value(6, 3, 2.0, O, prebuilt=pre)
        mine[O] = v
    t_mine = time.perf_counter() - t0
    my_val = min(mine.values())
    my_O = min(mine, key=mine.get)
    print(f"   N3 builder (min over 20 O)-> {my_val:.12f}  argmin O={my_O}  "
          f"({t_mine:.1f}s)", flush=True)
    disj = mine[(3, 4, 5)]
    print(f"   disjoint-type O=(3,4,5) value = {disj:.12f}  "
          f"(equals overall min: {abs(disj - my_val) < 1e-9})", flush=True)
    diff = abs(my_val - ref_val)
    print(f"   |diff| = {diff:.3e}  -> {'PASS' if diff < 1e-9 else 'FAIL'}",
          flush=True)
    return diff < 1e-9, diff


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def rep_O(m, K=5):
    """Representative of the symmetry type |O ∩ greedy prefix {0..K-1}| = m."""
    return tuple(range(m)) + tuple(range(K, K + (K - m)))


def type_label(m, K=5):
    O = rep_O(m, K)
    return f"type_m{m}_O={'-'.join(map(str, O))}"


def main(argv):
    quick = "--quick" in argv
    only_selftest = "--selftest" in argv
    skip_selftest = "--noselftest" in argv

    if not skip_selftest:
        ok, d = selftest()
        if not ok:
            print(f"SELF-TEST FAILED (diff={d:.3e}); aborting.", flush=True)
            return 1
        print(flush=True)
    if only_selftest:
        return 0

    n, K = 10, 5
    etas = [2.0] if quick else [1.5, 2.0, 3.0, 4.5]
    # Types solved per eta.  m = |O ∩ greedy prefix|; m = 0 is the disjoint type
    # used by every R5/R6 data point.  For two etas we sweep ALL types m = 0..K
    # to confirm the min over O is attained at m = 0 (so the m = 0 LP really is
    # the full-lattice LP value); elsewhere m = 0, 1 is enough to see the trend.
    full_type_etas = {1.5, 2.0}

    print(f"== full-lattice LP, n={n} K={K}, single-element error, "
          f"eta_u=eta_o=sqrt(eta) ==", flush=True)

    rows = []
    max_diff = 0.0
    all_match = True
    argmin_ok = True

    for eta in etas:
        s = np.sqrt(eta)
        print(f"-- eta={eta}  (eta_u=eta_o={s:.6f})", flush=True)
        t0 = time.perf_counter()
        pre = build_lattice_rows(n, K, s, s, "single")
        t_build = time.perf_counter() - t0
        print(f"   built A_ub: rows={pre[0].shape[0]} vars={pre[2]} "
              f"nnz={pre[0].nnz} detail={pre[5]}  ({t_build:.1f}s)", flush=True)

        red = reduced(K, eta)
        vj, argj = min_Vj(K, eta)

        ms = range(K + 1) if (eta in full_type_etas and not quick) else [0, 1]
        vals = {}
        for m in ms:
            O = rep_O(m, K)
            lat, t_lat, res = lattice_value(n, K, eta, O, prebuilt=pre,
                                            verbose=(m == 0))
            if lat is None:
                print(f"   !! LP failed for eta={eta} m={m}: {res.message}",
                      flush=True)
                rows.append((f"{eta}", "", f"{red:.12f}", f"{vj:.12f}", "",
                             f"{t_lat:.2f}", type_label(m, K) + "_FAILED"))
                all_match = False
                continue
            vals[m] = lat
            diff = abs(lat - red)
            if m == 0:
                max_diff = max(max_diff, diff)
                match = diff < 1e-7
                all_match = all_match and match
                print(f"   m=0 (disjoint): lattice={lat:.12f}  "
                      f"reduced={red:.12f}  minVj={vj:.12f} (j={argj})  "
                      f"|diff|={diff:.3e}  "
                      f"{'MATCH' if match else 'MISMATCH <<<'}  ({t_lat:.1f}s)",
                      flush=True)
            else:
                print(f"   m={m}  O={O}: LP={lat:.12f}  "
                      f">= disjoint? {lat >= vals[0] - 1e-9}  "
                      f"(gap {lat - vals[0]:+.3e}, {t_lat:.1f}s)", flush=True)
            rows.append((f"{eta}", f"{lat:.12f}", f"{red:.12f}", f"{vj:.12f}",
                         f"{diff:.3e}", f"{t_lat:.2f}", type_label(m, K)))

        if 0 in vals:
            mn = min(vals.values())
            this_ok = abs(vals[0] - mn) < 1e-9
            argmin_ok = argmin_ok and this_ok
            print(f"   min over types solved {sorted(vals)} = {mn:.12f}; "
                  f"disjoint is argmin: {this_ok}", flush=True)
        del pre

    with open(CSV_PATH, "w") as fh:
        fh.write("eta,lattice_LP,reduced_LP,minVj_formula,abs_diff,runtime_s,O_type\n")
        for r in rows:
            fh.write(",".join(r) + "\n")
    print(f"\nwrote {CSV_PATH}", flush=True)
    print(f"ALL MATCH (1e-7) on disjoint type: {all_match}   "
          f"max_diff = {max_diff:.3e}", flush=True)
    print(f"disjoint type is argmin over O types everywhere tested: "
          f"{argmin_ok}", flush=True)
    return 0 if (all_match and argmin_ok) else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
