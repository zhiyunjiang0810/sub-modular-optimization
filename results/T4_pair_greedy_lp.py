"""
T4: Exact worst-case approximation ratio of the 2-step (pair) predictive greedy
via a factor-revealing LP.  [VERIFIED-LP for the (n,K,eta) points actually run]

Pair greedy: at step t (t=0,1,...,K/2-1) the algorithm queries the predicted
gain dt_I(S_t) = ftilde(S_t u I) - ftilde(S_t) of every candidate I with
1 <= |I| <= min(2, K-|S_t|) (singletons INCLUDED) and adds a set of size 2
maximizing the predicted gain (ties adversarial).

WLOG (relabeling) the greedy picks pair {0,1} first, then {2,3}:
    state S_t = {0, ..., 2t-1},   chosen pair I_t = {2t, 2t+1}.

LP for a fixed candidate optimum O (|O| = K):
    min  f({0,...,K-1})
    s.t. f monotone submodular, f(empty)=0, ftilde(empty)=0, f(O)=1
         error band (default: ALL-PAIRS, since pair greedy queries pair gains):
             d_B(A)/eta_u <= dt_B(A) <= eta_o * d_B(A)  for all disjoint A,B
         pair-greedy path:  dt_{I_t}(S_t) >= dt_I(S_t)  for all I as above.
Worst case (adversarial ties) = min over all K-subsets O.

Analytic sanity check (must hold, else bug): the standard (1/eta)-approximate
greedy analysis with pair gains gives pair_LP >= 1 - (1 - 1/(2*eta))^2 at K=4
under the all-pairs error model (partition O \\ S_t into <=2-sets; the greedy
constraint set includes both pairs and singletons, covering odd remainders).

Reproduce:  python3 results/T4_pair_greedy_lp.py            (full run, ~30 min)
            python3 results/T4_pair_greedy_lp.py smoke      (n=6 sanity, ~1 min)
Outputs:    results/T4_pair_vs_single.csv, results/T4_pair_vs_single.json
"""
import itertools, json, os, sys, time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "code"))
import worst_case_lp  # verified single-step LP (not modified)


def build_common_rows(n, K, eta_u, eta_o, err_model):
    """All rows shared across candidate optima O (A_ub x <= 0)."""
    N = 1 << n
    F = lambda S: S
    G = lambda S: N + S
    rows = []

    def add(c):
        rows.append(c)

    # monotone f: f[S] - f[S|e] <= 0
    for S in range(N):
        for e in range(n):
            if not S >> e & 1:
                add({F(S): 1, F(S | 1 << e): -1})
    # submodular f: d_e(S|e2) - d_e(S) <= 0
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
                add(c)
    # error band
    for A in range(N):
        comp = (N - 1) ^ A
        if err_model == "single":
            Bs = [1 << e for e in range(n) if comp >> e & 1]
        else:  # all disjoint pairs (A,B), B nonempty
            Bs = []
            B = comp
            while B:
                Bs.append(B)
                B = (B - 1) & comp
        for B in Bs:
            AB = A | B
            # d/eta_u - dt <= 0
            c = {}
            for k, v in ((F(AB), 1 / eta_u), (F(A), -1 / eta_u),
                         (G(AB), -1), (G(A), 1)):
                c[k] = c.get(k, 0) + v
            add(c)
            # dt - eta_o d <= 0
            c = {}
            for k, v in ((G(AB), 1), (G(A), -1),
                         (F(AB), -eta_o), (F(A), eta_o)):
                c[k] = c.get(k, 0) + v
            add(c)
    # pair-greedy path
    for t in range(K // 2):
        S = (1 << (2 * t)) - 1
        It = (1 << (2 * t)) | (1 << (2 * t + 1))
        rmax = min(2, K - 2 * t)  # sizes of competing candidate sets
        cand = [e for e in range(n) if not S >> e & 1]
        for r in range(1, rmax + 1):
            for combo in itertools.combinations(cand, r):
                Im = 0
                for e in combo:
                    Im |= 1 << e
                if Im == It:
                    continue
                # dt_I(S) - dt_{I_t}(S) <= 0  (ftilde(S) terms cancel; kept
                # explicit for clarity, they merge to coefficient 0)
                c = {}
                for k, v in ((G(S | Im), 1), (G(S), -1),
                             (G(S | It), -1), (G(S), 1)):
                    c[k] = c.get(k, 0) + v
                add(c)
    return rows


def canonical_Os(n, K):
    """One representative K-subset per symmetry type (|O&{0,1}|, |O&{2,3}|, rest).

    Justification: the LP is invariant under permutations inside {0,1}, inside
    {2,3}, and inside {4,...,n-1}.  Verified empirically at n=8: per-O values
    within each type agree to 1e-6 (see T4_pair_vs_single.json, full mode).
    """
    reps = []
    for a in range(3):
        for b in range(3):
            c = K - a - b
            if c < 0 or c > n - 4:
                continue
            reps.append(tuple(list(range(a)) + [2 + i for i in range(b)]
                              + [4 + i for i in range(c)]))
    return reps


def pair_worst_case(n, K, eta_u, eta_o, err_model="all", verbose=False,
                    O_iter=None):
    """Min over all K-subsets O of the LP value; returns (val, argmin O, per_O dict).

    O_iter: optional iterable of candidate optima (default: all K-subsets)."""
    assert K % 2 == 0, "pair greedy needs even K here"
    N = 1 << n
    nv = 2 * N
    F = lambda S: S
    G = lambda S: N + S

    rows = build_common_rows(n, K, eta_u, eta_o, err_model)
    A_ub = lil_matrix((len(rows), nv))
    for i, c in enumerate(rows):
        for k, v in c.items():
            A_ub[i, k] = v
    A_ub = A_ub.tocsr()
    b_ub = np.zeros(len(rows))

    SK = (1 << K) - 1
    obj = np.zeros(nv)
    obj[F(SK)] = 1
    best = (np.inf, None)
    per_O = {}
    if O_iter is None:
        O_iter = itertools.combinations(range(n), K)
    for O in O_iter:
        Om = 0
        for i in O:
            Om |= 1 << i
        A_eq = lil_matrix((3, nv))
        A_eq[0, F(0)] = 1
        A_eq[1, G(0)] = 1
        A_eq[2, F(Om)] = 1
        res = linprog(obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq.tocsr(),
                      b_eq=[0, 0, 1], bounds=[(None, None)] * nv,
                      method="highs")
        if res.status != 0:
            per_O[str(O)] = f"LP status {res.status}"
            continue
        per_O[str(O)] = res.fun
        if res.fun < best[0]:
            best = (res.fun, O)
        if verbose:
            print(f"  O={O}: {res.fun:.6f}", flush=True)
    return best[0], best[1], per_O


def rstep_bound(K, eta, R=2):
    """Paper R-step lower bound 1 - (1 - R/(eta*K))^(K/R), R=2, K=4 -> 1-(1-1/(2eta))^2."""
    return 1 - (1 - R / (eta * K)) ** (K // R)


R5_SINGLE = {1.5: 0.543576, 2.0: 22 / 49, 3.0: 13 / 40}  # K=4, single-element err


def rho2(eta):
    """R4 exact single-step worst case at K=2: min{1/eta, 3/(2(eta+1))}.
    Observed [VERIFIED-LP, this script]: pair greedy at K=4 matches this exactly."""
    return min(1 / eta, 3 / (2 * (eta + 1)))


def merge_csv(csv_path, new_rows):
    """Merge new rows into the CSV, replacing rows with the same (n,K,eta,err_model)."""
    cols = list(new_rows[0].keys())
    old = []
    if os.path.exists(csv_path):
        with open(csv_path) as fh:
            lines = [l.rstrip("\n") for l in fh if l.strip()]
        if lines:
            old_cols = lines[0].split(",")
            for l in lines[1:]:
                old.append(dict(zip(old_cols, l.split(","))))
    newkeys = {(str(r["n"]), str(r["K"]), str(float(r["eta"])), r["err_model"])
               for r in new_rows}
    keep = [r for r in old
            if (r["n"], r["K"], str(float(r["eta"])), r["err_model"]) not in newkeys]
    allrows = keep + [{c: str(r.get(c, "")) for c in cols} for r in new_rows]
    allrows.sort(key=lambda r: (int(r["n"]), float(r["eta"])))
    with open(csv_path, "w") as fh:
        fh.write(",".join(cols) + "\n")
        for r in allrows:
            fh.write(",".join(r.get(c, "") for c in cols) + "\n")


def rewrite_csv_from_json():
    """Rebuild T4_pair_vs_single.csv from T4_pair_vs_single.json (uniform columns)."""
    json_path = os.path.join(HERE, "T4_pair_vs_single.json")
    csv_path = os.path.join(HERE, "T4_pair_vs_single.csv")
    with open(json_path) as fh:
        details = json.load(fh)
    rows = []
    for key, blob in details.items():
        n = int(key.split("_")[0][1:])
        eta = float(key.split("eta")[1])
        K = 4
        pv = blob["pair_LP"]
        sv = blob.get("single_LP_allpairs")
        r5 = R5_SINGLE.get(eta)
        rb = rstep_bound(K, eta)
        rows.append(dict(
            n=n, K=K, eta=eta, err_model="all",
            pair_LP=round(pv, 6),
            single_LP_same_err=round(sv, 6) if sv is not None else "",
            single_R5_single_elem=round(r5, 6) if r5 is not None else "",
            Rstep_bound=round(rb, 6),
            rho2_reference=round(rho2(eta), 6),
            pair_minus_single=round(pv - sv, 6) if sv is not None else
            (round(pv - r5, 6) if r5 is not None else ""),
            sanity_pair_ge_bound=pv >= rb - 1e-6,
        ))
    rows.sort(key=lambda r: (r["n"], r["eta"]))
    cols = list(rows[0].keys())
    with open(csv_path, "w") as fh:
        fh.write(",".join(cols) + "\n")
        for r in rows:
            fh.write(",".join(str(r[c]) for c in cols) + "\n")
    print(f"rewrote {csv_path} ({len(rows)} rows)")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    if mode == "rewrite":
        rewrite_csv_from_json()
        return
    K = 4
    etas = [1.5, 2.0, 3.0]
    sym = False
    if mode == "smoke":
        ns = [6]
        run_single = False
    elif mode == "n9":
        ns = [9]
        run_single = False   # pair only; single n=9 too slow (126 LPs x ~20s)
        sym = True           # symmetry-reduced candidate optima (9 types)
    else:
        ns = [8]
        run_single = True

    csv_path = os.path.join(HERE, "T4_pair_vs_single.csv")
    json_path = os.path.join(HERE, "T4_pair_vs_single.json")
    rows_out = []
    details = {}
    if os.path.exists(json_path):
        with open(json_path) as fh:
            details = json.load(fh)
    for n in ns:
        for eta in etas:
            eu = eo = eta ** 0.5
            O_iter = canonical_Os(n, K) if sym else None
            t0 = time.time()
            pv, pO, per_O = pair_worst_case(n, K, eu, eo, "all", O_iter=O_iter)
            t1 = time.time()
            print(f"[pair]   n={n} K={K} eta={eta}  LP={pv:.6f}  argmin O={pO}  "
                  f"({t1-t0:.0f}s)", flush=True)
            sv = None
            if run_single:
                t0 = time.time()
                sv, sO, _ = worst_case_lp.worst_case(n, K, eu, eo, "all")
                t1 = time.time()
                print(f"[single] n={n} K={K} eta={eta}  LP={sv:.6f}  argmin O={sO}  "
                      f"(all-pairs err, {t1-t0:.0f}s)", flush=True)
            rb = rstep_bound(K, eta)
            r5 = R5_SINGLE.get(eta)
            # sanity: pair LP must be >= analytic R-step bound (all-pairs model)
            ok = pv >= rb - 1e-6
            print(f"         sanity pair>=Rstep_bound: {ok}  "
                  f"(pair={pv:.6f}, bound={rb:.6f})", flush=True)
            rows_out.append(dict(
                n=n, K=K, eta=eta, err_model="all",
                pair_LP=round(pv, 6),
                single_LP_same_err=round(sv, 6) if sv is not None else "",
                single_R5_single_elem=round(r5, 6) if r5 is not None else "",
                Rstep_bound=round(rb, 6),
                rho2_reference=round(rho2(eta), 6),
                pair_minus_single=round(pv - sv, 6) if sv is not None else
                (round(pv - r5, 6) if r5 is not None else ""),
                sanity_pair_ge_bound=ok,
            ))
            details[f"n{n}_eta{eta}"] = dict(
                pair_LP=pv, pair_argmin_O=list(pO), sym_reduced=sym,
                single_LP_allpairs=sv, per_O_pair=per_O)
            # write incrementally so partial runs are still on disk
            merge_csv(csv_path, rows_out)
            with open(json_path, "w") as fh:
                json.dump(details, fh, indent=1)
    print(f"wrote {csv_path} and {json_path}", flush=True)


if __name__ == "__main__":
    main()
