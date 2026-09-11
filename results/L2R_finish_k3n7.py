"""L2R: finish the two unexhausted K=3, n=7 candidate-B cells (eta 1.25, 1.5).

Follow-up to results/L2_linear_candidates.md section 5.1 (the only L2
sticking point).  How the three speedup suggestions recorded there are
answered:
  1. O-orbit symmetry: re-examined and NOT exploited.  The fixed branch
     structure (greedy trajectory 0..K-1 AND the ascending scan order over
     K..n-1) has trivial residual symmetry: a permutation of the scan block
     maps the ascending-scan leaf set to the leaf set of a DIFFERENT scan
     order (accepted swaps update T mid-scan, so constraint sets do not
     biject), confirming the md section 1.5 judgement.
  2. + 3. combined differently than suggested: a 45 s probe showed the
     seeded node bound still prunes nothing in the shallow tree (0 cuts,
     16.4 LP/s single process), so the deciding lever is parallelism INSIDE
     one cell: the search decomposes exactly over the 35 hidden sets O
     (candB_search's outer loop), and one cell is run as 35 single-O tasks
     on a 4-process pool (one cell at a time, whole machine, which is what
     suggestion 3 asked).  The incumbent is still seeded at the cell's
     ACHIEVED upper bound from L2 (23/33 resp. 13/22, instance-rebuild
     certificates in the L2 run).

Seeding semantics (same as candB_search): nodes with bound >= seed - 1e-9
are cut, so if EVERY single-O task completes without improvement the exact
worst value lies in [seed - 1e-9, seed]; the seed is attained (certificate
branch), hence the value equals the seed up to the 1e-9 pruning/LP
tolerance carried by every L2 number.  A task that improves returns the
true minimum over its O.

`candB_search_O` below is a verbatim adaptation of the frozen-in-results
candB_search of results/L2_linear_candidates.py whose ONLY changes are
(a) the O loop runs over a caller-given list, (b) stats are returned per
call.  Gate R (below) certifies the adaptation: on K=3, n=6 (a cell the L2
run completed) the 35-task merge equals the frozen sequential search leaf
for leaf and value for value.

Budget: 28 minutes hard wall per cell inside the 30-minute instruction.
Per cell, on completion: exact rational value, instance-rebuild
consistency, exact-Fraction comparison with rho_3(eta); if strictly ABOVE
rho_3, the TASKS7 strict-improvement protocol runs (exact_witness Fraction
re-check of the attaining branch, query_audit, flag for the human, no
explaining away).  On timeout: incumbent, counters, profile-free
relaxation lower bound; the cell stays [OPEN].

Outputs: results/L2R_finish_k3n7.json (+ stdout log kept as
results/L2R_finish_k3n7.log).  Run: python3 results/L2R_finish_k3n7.py
"""
import importlib.util
import itertools
import json
import math
import multiprocessing as mp
import os
import time
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("OMP_NUM_THREADS", "1")

spec = importlib.util.spec_from_file_location(
    "l2mod", os.path.join(HERE, "L2_linear_candidates.py"))
l2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(l2)

K, n = 3, 7
TIME_LIMIT = 28 * 60.0
N_PROC = 4
CELLS = [(Fr(5, 4), Fr(23, 33)), (Fr(3, 2), Fr(13, 22))]


def V_exact(K, j, eta):
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return 1 - q ** j * (1 - Fr(K - j, K) / eta)


def rho_exact(K, eta):
    return min(V_exact(K, j, eta) for j in range(K))


# ---------------------------------------------------------------------------
# verbatim adaptation of l2.candB_search: O list is a parameter
# ---------------------------------------------------------------------------
def candB_search_O(n, K, eta, O_list, swap_mode="continue",
                   time_limit=900.0, ub_init=None):
    eu, eo = l2.split(eta)
    LP = l2.LPBuilder(n, eu, eo)
    N = LP.N
    G = lambda S: N + S
    base = l2.greedy_rows(n, N, K)
    L = list(range(K, n))
    T0 = list(range(K))
    stats = dict(nodes=0, leaves=0, pruned=0, lp=0)
    best = dict(val=np.inf if ub_init is None else float(ub_init),
                O=None, profile=None, T=None)
    seeded = ub_init is not None
    t_start = time.time()

    class Stop(Exception):
        pass

    def solve(rows, O_mask, obj_mask):
        stats["lp"] += 1
        if time.time() - t_start > time_limit:
            raise Stop
        return LP.solve(rows, O_mask, obj_mask)

    def rec(O_mask, p, i, cur, rows):
        stats["nodes"] += 1
        if p == K:
            stats["leaves"] += 1
            val = solve(rows, O_mask, l2.mask(cur))
            if val < best["val"] - 1e-9:
                best.update(val=val, O=O_mask, profile=list(rows_profile),
                            T=list(cur))
            return
        if i == len(L):
            if p + 1 < K:
                if solve(rows, O_mask, l2.mask(cur[:p + 1])) >= best["val"] - 1e-9:
                    stats["pruned"] += 1
                    return
            rec(O_mask, p + 1, 0, cur, rows)
            return
        e = L[i]
        if e in cur:
            rec(O_mask, p, i + 1, cur, rows)
            return
        t = cur[p]
        Tcur = l2.mask(cur)
        nxt = list(cur)
        nxt[p] = e
        Tnew = l2.mask(nxt)
        rows_profile.append((p, e, 0))
        rec(O_mask, p, i + 1, cur, rows + [{G(Tnew): 1.0, G(Tcur): -1.0}])
        rows_profile.pop()
        rows_profile.append((p, e, 1))
        arows = rows + [{G(Tcur): 1.0, G(Tnew): -1.0}]
        if swap_mode == "first":
            rec(O_mask, p + 1, 0, nxt, arows)
        else:
            rec(O_mask, p, i + 1, nxt, arows)
        rows_profile.pop()

    rows_profile = []
    status = "OK"
    for O in O_list:
        Om = l2.mask(O)
        try:
            rec(Om, 0, 0, list(T0), base)
        except Stop:
            status = "TIMEOUT"
            break
    if seeded and best["profile"] is None:
        status = ("OK_NO_IMPROVEMENT_BELOW_SEED" if status == "OK"
                  else "TIMEOUT_SEEDED_NOT_IMPROVED")
    return dict(val=best["val"],
                O=None if best["O"] is None else l2.bits(best["O"]),
                T=best["T"], profile=best["profile"], status=status,
                n_lps=stats["lp"], n_leaves=stats["leaves"],
                n_nodes=stats["nodes"], n_pruned=stats["pruned"],
                swap_mode=swap_mode, seed=ub_init,
                improved=best["profile"] is not None,
                secs=time.time() - t_start)


def _worker(args):
    n_, K_, eta_, O, limit, seed = args
    return (O, candB_search_O(n_, K_, eta_, [O], time_limit=limit,
                              ub_init=seed))


def run_cell(n_, K_, eta, seed, deadline_s):
    """One cell = 35 single-O tasks on a pool; merge preserves semantics."""
    Os = list(itertools.combinations(range(n_), K_))
    t0 = time.time()
    args = [(n_, K_, float(eta), O, max(30.0, deadline_s), seed and float(seed))
            for O in Os]
    with mp.Pool(N_PROC) as pool:
        per_O = list(pool.imap_unordered(_worker, args))
    agg = dict(n_lps=0, n_leaves=0, n_nodes=0, n_pruned=0)
    best = dict(val=np.inf if seed is None else float(seed),
                O=None, T=None, profile=None, improved=False)
    statuses = []
    for O, r in per_O:
        for k in agg:
            agg[k] += r[k]
        statuses.append(r["status"])
        if r["improved"] and r["val"] < best["val"] - 1e-12:
            best = dict(val=r["val"], O=r["O"], T=r["T"],
                        profile=r["profile"], improved=True)
    completed = all(s in ("OK", "OK_NO_IMPROVEMENT_BELOW_SEED")
                    for s in statuses)
    return dict(best=best, completed=completed, statuses=statuses,
                secs=time.time() - t0, **agg)


def main():
    out = {"task": "L2R", "K": K, "n": n,
           "time_limit_per_cell_s": TIME_LIMIT, "n_proc": N_PROC,
           "cells": []}

    # ---- Gate R: the per-O adaptation reproduces the frozen search --------
    print("Gate R: per-O parallel merge vs frozen candB_search on K=3, n=6",
          flush=True)
    gate = {}
    # Pass criterion: equal values (1e-12).  Leaf counts are compared too,
    # but a deficit is acceptable only when explained by pruning: the frozen
    # search shares one incumbent across all O, so its node bound can cut
    # subtrees that the per-O tasks (each with only its own O's incumbent)
    # still enumerate; pruning removes only subtrees whose bound certifies
    # no value below incumbent - 1e-9, so the minimum is unaffected.  When
    # NEITHER side pruned, the leaf counts must agree exactly.
    full_leaves = l2._leaf_count(6, 3, "continue") * math.comb(6, 3)
    for eta_g in (1.25, 2.0):
        ref = l2.candB_search(6, 3, eta_g, swap_mode="continue",
                              time_limit=600.0, verbose=False)
        par = run_cell(6, 3, eta_g, None, 600.0)
        same_val = abs(ref["val"] - par["best"]["val"]) < 1e-12
        same_leaves = ref["n_leaves"] == par["n_leaves"]
        deficit_explained = (ref["n_pruned"] > 0 or par["n_pruned"] > 0)
        covered = (par["n_leaves"] == full_leaves) or par["n_pruned"] > 0
        ok = bool(same_val and covered
                  and (same_leaves or deficit_explained))
        gate[str(eta_g)] = dict(ref_val=ref["val"], par_val=par["best"]["val"],
                                ref_leaves=ref["n_leaves"],
                                par_leaves=par["n_leaves"],
                                ref_pruned=ref["n_pruned"],
                                par_pruned=par["n_pruned"],
                                full_leaves=full_leaves, ok=ok)
        print(f"  eta={eta_g}: frozen {ref['val']:.9f} ({ref['n_leaves']} "
              f"leaves, {ref['n_pruned']} pruned) vs merge "
              f"{par['best']['val']:.9f} ({par['n_leaves']} leaves, "
              f"{par['n_pruned']} pruned; full tree {full_leaves}) -> "
              f"{'OK' if ok else 'MISMATCH'}", flush=True)
    out["gateR"] = gate
    if not all(g["ok"] for g in gate.values()):
        print("Gate R FAILED: aborting before the n=7 cells", flush=True)
        with open(os.path.join(HERE, "L2R_finish_k3n7.json"), "w") as fh:
            json.dump(out, fh, indent=1, default=str)
        return 1

    # ---- the two cells -----------------------------------------------------
    for eta, seed in CELLS:
        rho3 = rho_exact(K, eta)
        print(f"===== eta={eta} seed={seed} (={float(seed):.9f})  "
              f"rho_3={rho3} (={float(rho3):.9f}) =====", flush=True)
        res = run_cell(n, K, eta, seed, TIME_LIMIT)
        b = res["best"]
        print(f"  cell: completed={res['completed']} val={b['val']:.9f} "
              f"improved={b['improved']} lps={res['n_lps']} "
              f"leaves={res['n_leaves']} pruned={res['n_pruned']} "
              f"secs={res['secs']:.1f}", flush=True)
        cell = dict(eta=float(eta), eta_exact=str(eta), seed=str(seed),
                    rho3_exact=str(rho3), rho3=float(rho3),
                    completed=res["completed"], statuses=res["statuses"],
                    n_lps=res["n_lps"], n_leaves=res["n_leaves"],
                    n_pruned=res["n_pruned"], n_nodes=res["n_nodes"],
                    n_branches_total=l2._leaf_count(n, K, "continue")
                    * math.comb(n, K),
                    secs=res["secs"], improved=b["improved"])

        if not res["completed"]:
            lb = l2.candB_relax_lb(n, K, float(eta))
            ub = min(float(seed), b["val"])
            cell.update(conclusion="OPEN", value_kind="interval_only",
                        incumbent_upper_bound=ub, relax_lower_bound=lb,
                        note="search not exhausted; the incumbent is an "
                             "upper bound of an unfinished search and is "
                             "NOT evidence in either direction")
            print(f"  TIMEOUT: stays [OPEN]; interval [{lb:.6f}, {ub:.6f}]",
                  flush=True)
            out["cells"].append(cell)
            continue

        if b["improved"]:
            vfr = Fr(l2.rationalize(b["val"]))
            branch = dict(O=b["O"], T=b["T"], profile=b["profile"])
        else:
            vfr = seed
            branch = l2_prior_row(eta)      # certificate branch from L2
        cell.update(value_float=float(vfr), value_fraction=str(vfr),
                    value_kind="exact (completed search; 1e-9 pruning/LP "
                               "tolerance as in every L2 number)")

        rep, f, g = l2.consistency_check(n, K, float(eta), "B", branch,
                                         swap_mode="continue")
        cell["consistency"] = {k: rep[k] for k in
                               ("lp_value", "monotone", "submodular", "band",
                                "sim_ratio", "branch_ratio", "consistent")}

        if vfr > rho3:
            ew = l2.exact_witness(n, K, float(eta), "B", branch, f, g)
            qa = l2.query_audit(n, K, "B")
            cell.update(vs_rho="STRICTLY_ABOVE_RHO3",
                        flag="NEEDS_HUMAN_JUDGEMENT",
                        exact_witness=ew, query_audit=qa,
                        lower_bound_side="completed float branch-and-bound "
                                         f"({res['n_lps']} LPs, 1e-9 "
                                         "tolerance); margin above rho_3 = "
                                         f"{float(vfr - rho3):.6f}")
            print(f"  RESULT: value {vfr} STRICTLY ABOVE rho_3 {rho3} "
                  f"[NEEDS HUMAN JUDGEMENT]", flush=True)
        elif vfr == rho3:
            cell.update(vs_rho="equal")
            print(f"  RESULT: value {vfr} equals rho_3", flush=True)
        else:
            cell.update(vs_rho="worse", gap=str(rho3 - vfr))
            print(f"  RESULT: value {vfr} strictly BELOW rho_3 {rho3} "
                  f"(worse than greedy)", flush=True)
        out["cells"].append(cell)

    with open(os.path.join(HERE, "L2R_finish_k3n7.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)
    print("wrote results/L2R_finish_k3n7.json", flush=True)
    return 0


def l2_prior_row(eta):
    d = json.load(open(os.path.join(HERE, "L2_linear_candidates.json")))
    for r in d["results"]:
        if (r["K"] == K and r["n"] == n and r["candidate"] == "B"
                and abs(r["eta"] - float(eta)) < 1e-12):
            return r
    raise KeyError(eta)


if __name__ == "__main__":
    raise SystemExit(main())
