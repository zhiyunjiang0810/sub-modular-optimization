#!/usr/bin/env python3
"""N6 step 1: factor-revealing LP for the ADDITIVE + MULTIPLICATIVE error model.

Row construction is copied from code/worst_case_lp.py (R5 / VERIFIED-LP) with a
single change: the two error-model rows carry an additive slack epsilon on the
right-hand side.  Everything else (monotone, submodular, greedy path, f(empty)=0,
ftilde(empty)=0, f(O)=1, objective f({0..K-1}), min over all K-subsets O) is
identical, so epsilon = 0 must reproduce the R5 numbers exactly.

Error model (all S, all single e not in S; OPT normalized f(O) = 1):

    d_e(S)/eta_u - epsilon  <=  dt_e(S)  <=  eta_o * d_e(S) + epsilon

LP rows (both <= 0 form pushed to <= epsilon):

    d/eta_u - dt <= epsilon
    dt - eta_o*d <= epsilon

Hand-derived bound being tested (see results/N6_additive_model.md,
[HAND-PROOF-UNREVIEWED]):

    F^PG >= L_K(eta) * (OPT - 2*K*eta_u*epsilon)
          = L_K(eta)*OPT - c(eta)*K*epsilon,   c(eta) = 2*eta_u*L_K(eta)

with eta = eta_u*eta_o and L_K(eta) = 1 - (1 - 1/(eta*K))^K.

Usage:
  python3 N6_additive_lp.py              # main grid (n=6, K=3) + slope sweep
  python3 N6_additive_lp.py --quick      # only the 4 requested (eta, epsilon) cells
"""
import argparse
import itertools
import json
import os
import sys
import time

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix

HERE = os.path.dirname(os.path.abspath(__file__))


def worst_case_additive(n, K, eta_u, eta_o, epsilon, err_model="single"):
    """Exact worst-case ratio of single-step predictive greedy under the
    additive+multiplicative error model.  Adapted from code/worst_case_lp.py;
    the ONLY structural change is `add_ub(c, epsilon)` on the two error rows."""
    N = 1 << n
    nv = 2 * N                       # f[S] -> S,  ftilde[S] -> N+S
    F = lambda S: S
    G = lambda S: N + S

    rows_ub, b_ub = [], []

    def add_ub(coefs, rhs=0.0):
        rows_ub.append(coefs)
        b_ub.append(rhs)

    # --- monotone: f[S] - f[S|e] <= 0  (verbatim from worst_case_lp.py) ---
    for S in range(N):
        for e in range(n):
            if not S >> e & 1:
                add_ub({F(S): 1, F(S | 1 << e): -1})
    # --- submodular: d_e(S|e') <= d_e(S)  (verbatim) ---
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
    # --- error model: THE ONLY CHANGE (rhs 0 -> epsilon) ---
    for A in range(N):
        comp = (N - 1) ^ A
        if err_model == "single":
            Bs = [1 << e for e in range(n) if comp >> e & 1]
        else:  # all pairs A,B disjoint, B nonempty
            Bs = []
            B = comp
            while B:
                Bs.append(B)
                B = (B - 1) & comp
        for B in Bs:
            AB = A | B
            # d/eta_u - dt <= epsilon
            c = {}
            for k, v in ((F(AB), 1 / eta_u), (F(A), -1 / eta_u),
                         (G(AB), -1), (G(A), 1)):
                c[k] = c.get(k, 0) + v
            add_ub(c, epsilon)
            # dt - eta_o*d <= epsilon
            c = {}
            for k, v in ((G(AB), 1), (G(A), -1),
                         (F(AB), -eta_o), (F(A), eta_o)):
                c[k] = c.get(k, 0) + v
            add_ub(c, epsilon)
    # --- greedy path (verbatim) ---
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

    A_ub = lil_matrix((len(rows_ub), nv))
    for i, c in enumerate(rows_ub):
        for k, v in c.items():
            A_ub[i, k] = v
    A_ub = A_ub.tocsr()
    b_ub = np.array(b_ub, dtype=float)

    SK = (1 << K) - 1
    obj = np.zeros(nv)
    obj[F(SK)] = 1
    best = (np.inf, None, None)
    for O in itertools.combinations(range(n), K):
        Om = sum(1 << i for i in O)
        A_eq = lil_matrix((3, nv))
        A_eq[0, F(0)] = 1
        A_eq[1, G(0)] = 1
        A_eq[2, F(Om)] = 1
        res = linprog(obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq.tocsr(),
                      b_eq=[0, 0, 1], bounds=[(None, None)] * nv, method="highs")
        if res.status == 0 and res.fun < best[0]:
            best = (float(res.fun), O, res.x)
    return best


def L_K(K, eta):
    return 1.0 - (1.0 - 1.0 / (eta * K)) ** K


def c_eta(K, eta_u, eta_o):
    """c(eta) = 2 * eta_u * L_K(eta) in F^PG >= L_K*OPT - c(eta)*K*eps."""
    return 2.0 * eta_u * L_K(K, eta_u * eta_o)


def additive_bound(K, eta_u, eta_o, epsilon):
    return L_K(K, eta_u * eta_o) - c_eta(K, eta_u, eta_o) * K * epsilon


def structure_probe():
    """Probe the empirical shape LP(eps) = rho_K(eta) * (1 - 2*K*eta_u*eps).

    Two sharp tests of the hand derivation:
      (a) the epsilon coefficient must involve eta_u ALONE (not eta_o, not eta):
          hold eta = eta_u*eta_o fixed and vary the split.
      (b) the critical epsilon* where the worst case collapses to 0 must be
          1/(2*K*eta_u), independent of eta_o.
    Also checks the K-scaling on (n,K) = (4,2).
    """
    print("\n\n=== structure probe: is LP(eps) = rho_K(eta)*(1 - 2*K*eta_u*eps)? ===")
    cfgs = [
        # (n, K, eta_u, eta_o, label)
        (6, 3, 2.0 ** 0.5, 2.0 ** 0.5, "K=3 eta=2 symmetric"),
        (6, 3, 2.0, 1.0, "K=3 eta=2 all under-est"),
        (6, 3, 1.0, 2.0, "K=3 eta=2 all over-est"),
        (4, 2, 2.0 ** 0.5, 2.0 ** 0.5, "K=2 eta=2 symmetric"),
    ]
    recs = []
    hdr = (f"{'config':>24} {'eps':>7} {'LP':>10} {'pred':>10} {'|LP-pred|':>10} "
           f"{'eps*(pred)':>10}")
    print(hdr)
    print("-" * len(hdr))
    for (n, K, eu, eo, lab) in cfgs:
        rho0, _, _ = worst_case_additive(n, K, eu, eo, 0.0)
        eps_star = 1.0 / (2.0 * K * eu)
        for eps in [0.0, 0.25 * eps_star, 0.5 * eps_star, 0.9 * eps_star,
                    eps_star, 1.25 * eps_star]:
            val, _, _ = worst_case_additive(n, K, eu, eo, eps)
            pred = max(0.0, rho0 * (1.0 - 2.0 * K * eu * eps))
            recs.append(dict(n=n, K=K, eta_u=eu, eta_o=eo, label=lab,
                             epsilon=eps, lp_value=val, predicted=pred,
                             abs_err=abs(val - pred), eps_star=eps_star,
                             rho_eps0=rho0))
            print(f"{lab:>24} {eps:7.4f} {val:10.6f} {pred:10.6f} "
                  f"{abs(val - pred):10.2e} {eps_star:10.5f}")
            sys.stdout.flush()
    worst = max(r["abs_err"] for r in recs)
    print(f"\n[check 4] max |LP - rho_K*(1-2*K*eta_u*eps)| over probe = {worst:.2e} "
          f"-> {'CONSISTENT' if worst < 1e-7 else 'INCONSISTENT'}")
    print("[check 5] eps* depends on eta_u only (eta fixed at 2, K=3): "
          f"all-under {1/(2*3*2.0):.5f}, symmetric {1/(2*3*2**0.5):.5f}, "
          f"all-over {1/(2*3*1.0):.5f}")
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--no-probe", action="store_true")
    ap.add_argument("--k4", action="store_true",
                    help="also verify K=4 on n=8 (about 3 minutes)")
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--K", type=int, default=3)
    args = ap.parse_args()

    n, K = args.n, args.K
    etas = [1.5, 2.0]
    eps_main = [0.01, 0.05]
    # extra points only for the local slope estimate near eps = 0
    eps_sweep = [0.0, 0.002, 0.005, 0.01, 0.02, 0.05] if not args.quick else [0.0] + eps_main

    records = []
    print(f"# additive+multiplicative worst-case LP, n={n} K={K}, "
          f"eta_u = eta_o = sqrt(eta), single-element error model")
    hdr = (f"{'eta':>5} {'eps':>7} {'LP':>10} {'bound':>10} {'LP-bound':>10} "
           f"{'drop':>9} {'slope':>9} {'c*K':>9} {'O':>10} {'sec':>6}")
    print(hdr)
    print("-" * len(hdr))
    for eta in etas:
        eu = eo = eta ** 0.5
        base = None
        for eps in eps_sweep:
            t0 = time.time()
            val, O, _ = worst_case_additive(n, K, eu, eo, eps)
            dt = time.time() - t0
            if eps == 0.0:
                base = val
            bnd = additive_bound(K, eu, eo, eps)
            drop = (base - val) if base is not None else float("nan")
            slope = (drop / eps) if eps > 0 else float("nan")
            cK = c_eta(K, eu, eo) * K
            records.append(dict(n=n, K=K, eta=eta, eta_u=eu, eta_o=eo,
                                epsilon=eps, lp_value=val, O=list(O),
                                LK=L_K(K, eta), c_eta=c_eta(K, eu, eo),
                                additive_bound=bnd, lp_minus_bound=val - bnd,
                                drop_vs_eps0=drop, empirical_slope=slope,
                                c_times_K=cK, seconds=dt))
            print(f"{eta:5.2f} {eps:7.4f} {val:10.6f} {bnd:10.6f} "
                  f"{val - bnd:10.6f} {drop:9.6f} {slope:9.4f} {cK:9.4f} "
                  f"{str(O):>10} {dt:6.1f}")
            sys.stdout.flush()

    # ---- checks ----
    print("\n=== checks ===")
    viol = [r for r in records if r["lp_minus_bound"] < -1e-9]
    print(f"[check 1] LP value >= hand-derived additive bound: "
          f"{'PASS' if not viol else 'FAIL'}  ({len(viol)} violations / {len(records)})")
    for r in viol:
        print(f"   VIOLATION eta={r['eta']} eps={r['epsilon']} "
              f"LP={r['lp_value']:.6f} bound={r['additive_bound']:.6f}")
    # eps = 0 must reproduce R5
    R5 = {(3, 1.5): 9.0 / 16.0, (3, 2.0): 7.0 / 15.0}
    print("[check 2] epsilon = 0 reproduces R5 rho_K(eta):")
    for r in records:
        if r["epsilon"] == 0.0 and (K, r["eta"]) in R5:
            ref = R5[(K, r["eta"])]
            ok = abs(r["lp_value"] - ref) < 1e-8
            print(f"   eta={r['eta']}: LP={r['lp_value']:.10f} R5={ref:.10f} "
                  f"|diff|={abs(r['lp_value'] - ref):.2e}  {'PASS' if ok else 'FAIL'}")
    # monotonicity of LP value in epsilon
    print("[check 3] LP value non-increasing in epsilon:")
    for eta in etas:
        vs = [r["lp_value"] for r in records if r["eta"] == eta]
        es = [r["epsilon"] for r in records if r["eta"] == eta]
        ok = all(vs[i] >= vs[i + 1] - 1e-9 for i in range(len(vs) - 1))
        print(f"   eta={eta}: {'PASS' if ok else 'FAIL'}  "
              f"values={[f'{v:.6f}' for v in vs]} at eps={es}")

    probe = [] if args.no_probe else structure_probe()

    k4 = []
    if args.k4:
        print("\n=== K=4 confirmation (n=8, eta=2, ~35 s per LP) ===")
        n8, K4, eu = 8, 4, 2.0 ** 0.5
        rho4, O4, _ = worst_case_additive(n8, K4, eu, eu, 0.0)
        es = 1.0 / (2 * K4 * eu)
        print(f"eps=0: LP={rho4:.10f}  (R5 rho_4(2)=22/49={22/49:.10f})  "
              f"predicted eps*={es:.6f}")
        for frac in [0.3, 0.7, 1.0, 1.3]:
            eps = frac * es
            val, _, _ = worst_case_additive(n8, K4, eu, eu, eps)
            pred = max(0.0, rho4 * (1 - 2 * K4 * eu * eps))
            bnd = additive_bound(K4, eu, eu, eps)
            k4.append(dict(n=n8, K=K4, eta=2.0, epsilon=eps, lp_value=val,
                           predicted=pred, abs_err=abs(val - pred),
                           additive_bound=bnd, holds=bool(val >= bnd - 1e-9)))
            print(f"  eps={eps:.6f} LP={val:.10f} pred={pred:.10f} "
                  f"|diff|={abs(val - pred):.2e} bound={bnd:.6f} "
                  f"LP>=bound={val >= bnd - 1e-9}")
            sys.stdout.flush()

    out = os.path.join(HERE, "N6_additive_lp.json")
    with open(out, "w") as fh:
        json.dump(dict(main_grid=records, structure_probe=probe,
                       k4_confirmation=k4), fh, indent=1)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
