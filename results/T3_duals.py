"""T3 step 1+2: dual multipliers of the reduced LP (code/reduced_lp.py) with labeled
constraints, for K in {2,3,4}, eta in {1.25, 1.5, 2, 2.5}; K=2 sanity check vs R4.

Row layout of reduced(K, eta) (see code/reduced_lp.py): for each t = 0..K-1, a block of
1 + 3K rows in this order:
  offset 0            : sum(t)     -sum_i g_{t,i} - sum_{s<t} d_s <= -1   (sum_i g_{t,i} >= r_t)
  offset 1+3i+0 (i<K) : pred(t,i)  g_{t,i}/eta - d_t <= 0                 (d_t >= g_{t,i}/eta)
  offset 1+3i+1 (i<K) : mono(t,i)  g_{t+1,i} - g_{t,i} <= 0
  offset 1+3i+2 (i<K) : cons(t,i)  g_{t,i} - d_t - (1-1/eta) g_{t+1,i} <= 0
scipy convention: min c'x, A x <= b, x >= 0; duals y = res.ineqlin.marginals <= 0;
dual objective b'y = primal optimum (strong duality). Here b = -1 on sum rows, 0 else,
so b'y = -sum_t y_sum(t).

Output: results/T3_duals.json + console summary.
Run: python results/T3_duals.py    (from anywhere; ~5 s)
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
import numpy as np
from reduced_lp import reduced

HERE = os.path.dirname(os.path.abspath(__file__))

def row_label(K, row):
    """Map row index of reduced(K, eta) to (type, t, i)."""
    per = 1 + 3 * K
    t, j = divmod(row, per)
    if j == 0:
        return ("sum", t, None)
    i, k = divmod(j - 1, 3)
    return (["pred", "mono", "cons"][k], t, i)

def r4_formula(eta):
    """R4 [RESEARCH_STATE.md]: rho_2(eta) = min{1/eta, 3/(2(eta+1))}."""
    return min(1.0 / eta, 3.0 / (2.0 * (eta + 1.0)))

def main():
    out = {"description": "Nonzero dual multipliers (res.ineqlin.marginals, <=0 convention) "
                          "of the reduced LP, labeled by constraint type and (t,i). "
                          "sum(t): sum_i g_{t,i} >= r_t; pred(t,i): d_t >= g_{t,i}/eta; "
                          "mono(t,i): g_{t+1,i} <= g_{t,i}; "
                          "cons(t,i): (1-1/eta) g_{t+1,i} >= g_{t,i} - d_t.",
           "entries": []}
    tol = 1e-9
    all_ok = True
    for K in [2, 3, 4]:
        for eta in [1.25, 1.5, 2.0, 2.5]:
            val, res = reduced(K, eta, return_sol=True)
            assert res.status == 0, (K, eta, res.status)
            marg = res.ineqlin.marginals
            # dual objective b'y: b = -1 on sum rows, 0 elsewhere
            per = 1 + 3 * K
            dual_obj = -sum(marg[t * per] for t in range(K))
            nz = []
            support_pattern = set()
            for r, m in enumerate(marg):
                if abs(m) > tol:
                    typ, t, i = row_label(K, r)
                    nz.append({"row": int(r), "type": typ, "t": int(t),
                               "i": (None if i is None else int(i)), "dual": float(m)})
                    support_pattern.add((typ, t))
            entry = {"K": K, "eta": eta, "lp_value": float(val),
                     "dual_objective": float(dual_obj),
                     "duality_gap": float(abs(val - dual_obj)),
                     "primal_d": [float(x) for x in res.x[:K]],
                     "primal_g_by_t": [[float(x) for x in res.x[K + t * K: K + (t + 1) * K]]
                                       for t in range(K + 1)],
                     "support_pattern_types_t": sorted(f"{typ}({t})" for typ, t in support_pattern),
                     "nonzero_duals": nz}
            if K == 2:
                r4 = r4_formula(eta)
                entry["R4_formula"] = float(r4)
                entry["abs_diff_vs_R4"] = float(abs(val - r4))
                ok = abs(val - r4) < 1e-9 and abs(dual_obj - r4) < 1e-9
                entry["R4_check"] = "PASS" if ok else "FAIL"
                all_ok &= ok
            gap_ok = abs(val - dual_obj) < 1e-9
            all_ok &= gap_ok
            out["entries"].append(entry)
            extra = f"  R4={entry.get('R4_formula', float('nan')):.9f} [{entry.get('R4_check','-')}]" if K == 2 else ""
            print(f"K={K} eta={eta:4}: primal={val:.9f} dual_obj={dual_obj:.9f} "
                  f"gap={abs(val-dual_obj):.1e}{extra}")
            print(f"   support: {entry['support_pattern_types_t']}")
    out["K2_sanity"] = ("PASS: primal = dual objective = min{1/eta, 3/(2(eta+1))} at all four eta"
                       if all_ok else "FAIL (see entries)")
    path = os.path.join(HERE, "T3_duals.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nK=2 sanity + strong duality: {'ALL PASS' if all_ok else 'FAIL'}")
    print(f"wrote {path}")

if __name__ == "__main__":
    main()
