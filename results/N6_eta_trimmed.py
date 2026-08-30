#!/usr/bin/env python3
"""N6 step 2: TRIMMED eta^path re-measurement under the additive+multiplicative
error model.

Same pipeline as results/T6_eta_path.py (same datasets, same 30 splits, same
caches, same seeds, same greedy tie-breaking); `get_datasets` and the constants
K_MAX / N_SPLITS / TREE_SEED / TOL / DATASET_ORDER are IMPORTED from that file.
`run_split_pairs` below is T6's `run_split` with one change: it returns the raw
(d, d~) pairs per step instead of collapsing them immediately, so both epsilon
levels are computed from a single pass.  T6_eta_path.py is NOT modified.

What changes vs T6
------------------
T6:  eta_u = max d/d~ over pairs with d > tol and d~ > tol   (tol = 1e-12)
N6:  eta_u = max d/d~ over pairs with d >= eps and d~ >= eps  (eps > 0)

epsilon levels, per split, in the units of f (accuracy):
    level 1 : eps = 1 / n_test
    level 2 : eps = 2 / n_test
n_test = size of the held-out set of that split (breast_cancer 114, wine 36,
digits20 360), i.e. one and two test-set quantization units of accuracy.

Trimming set (literal reading of the model's "both sides above the noise floor"):
    kept  <=>  |d| >= eps  AND  |d~| >= eps         -> n_pairs_kept, frac_kept
The max-ratios eta_u, eta_o are only meaningful on the positive part of that
set, so they are taken over  d >= eps AND d~ >= eps  -> n_pairs_eta.

Reported bound (hand derivation in results/N6_additive_model.md,
[HAND-PROOF-UNREVIEWED], LP-checked by results/N6_additive_lp.py):

    F^PG >= L_K(eta) * (OPT - 2*K*eta_u*eps)
    additive_bound := L_K(eta_trim) - c*K*eps,  c = 2*eta_u_trim*L_K(eta_trim)

CAVEAT recorded in the .md: (eta_u_trim, eta_o_trim, eps) certify the band only
on the KEPT pairs.  A secondary "certified" measurement therefore also solves,
over ALL recorded pairs, for the smallest (eta_u, eta_o) that satisfy
    d/eta_u - eps <= d~ <= eta_o*d + eps
at the same eps, and reports how many pairs admit no finite value at all.

Outputs:
  results/N6_eta_trimmed.csv
  figures/N6_eta_trimmed_vs_raw.png
  figures/N6_bound_vs_ratio.png

Usage:
  python3 N6_eta_trimmed.py                          # full run
  python3 N6_eta_trimmed.py --datasets wine --splits 1   # timing trial
"""
import argparse
import os
import time

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.tree import DecisionTreeClassifier

# --- reuse T6's dataset loader and constants verbatim (no modification there) ---
from T6_eta_path import (  # noqa: E402
    DATASET_ORDER,
    K_MAX,
    N_SPLITS,
    TOL,
    TREE_SEED,
    get_datasets,
)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIGDIR = os.path.join(ROOT, "figures")

EPS_LEVELS = [1, 2]  # eps = level / n_test

# Okabe-Ito subset (CVD safe): raw / eps level 1 / eps level 2
C_RAW, C_E1, C_E2, C_ACC = "#0072B2", "#D55E00", "#009E73", "#E69F00"


def run_split_pairs(X, y, seed):
    """T6_eta_path.run_split with the per-step (d, d~) pairs returned raw.

    Identical protocol: 80/20 stratified split at random_state=seed, memo caches
    keyed by frozenset, predictive greedy on f~ for K_MAX steps with ties to the
    lowest index, oracle greedy on f with the same rule.
    """
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=seed, stratify=y
    )
    maj = np.bincount(y_tr).argmax()
    f_empty = float(np.mean(y_te == maj))
    ft_empty = float(np.mean(y_tr == maj))
    f_cache, ft_cache = {}, {}

    def f(S):
        if not S:
            return f_empty
        v = f_cache.get(S)
        if v is None:
            cols = sorted(S)
            clf = DecisionTreeClassifier(random_state=TREE_SEED)
            clf.fit(X_tr[:, cols], y_tr)
            v = float(clf.score(X_te[:, cols], y_te))
            f_cache[S] = v
        return v

    def ft(S):
        if not S:
            return ft_empty
        v = ft_cache.get(S)
        if v is None:
            cols = sorted(S)
            clf = DecisionTreeClassifier(random_state=TREE_SEED)
            v = float(cross_val_score(clf, X_tr[:, cols], y_tr, cv=5).mean())
            ft_cache[S] = v
        return v

    n_feat = X.shape[1]

    def greedy(value_fn, record_pairs=False):
        S = frozenset()
        chosen, step_pairs = [], []
        for _t in range(K_MAX):
            base = value_fn(S)
            base_f = f(S) if record_pairs else None
            best_e, best_gain = None, None
            pairs = []
            for e in range(n_feat):
                if e in S:
                    continue
                gain = value_fn(S | {e}) - base
                if record_pairs:
                    d_true = f(S | {e}) - base_f
                    pairs.append((d_true, gain))  # (d_e, d~_e)
                if best_gain is None or gain > best_gain + TOL:
                    best_e, best_gain = e, gain
            S = S | {best_e}
            chosen.append(best_e)
            if record_pairs:
                step_pairs.append(pairs)
        return chosen, step_pairs

    chosen_pred, step_pairs = greedy(ft, record_pairs=True)
    chosen_oracle, _ = greedy(f, record_pairs=False)

    ratios = {}
    for K in range(1, K_MAX + 1):
        ratios[K] = f(frozenset(chosen_pred[:K])) / f(frozenset(chosen_oracle[:K]))
    return step_pairs, ratios, len(y_te)


def L_K(K, eta):
    if not np.isfinite(eta) or eta <= 0:
        return float("nan")
    return 1.0 - (1.0 - 1.0 / (eta * K)) ** K


def trimmed_stats(d, dt, eps, K):
    """Trimmed eta and the additive bound for one (split, K, eps) cell."""
    m = len(d)
    kept = (np.abs(d) >= eps) & (np.abs(dt) >= eps)
    n_kept = int(kept.sum())
    use = (d >= eps) & (dt >= eps)          # positive part of the kept set
    n_eta = int(use.sum())
    if n_eta > 0:
        eta_u = float(np.max(d[use] / dt[use]))
        eta_o = float(np.max(dt[use] / d[use]))
        eta = eta_u * eta_o
        lk = L_K(K, eta)
        c = 2.0 * eta_u * lk
        bound = lk - c * K * eps
    else:
        eta_u = eta_o = eta = lk = c = bound = float("nan")
    return dict(
        eta_u_trim=eta_u, eta_o_trim=eta_o, eta_trim=eta,
        n_pairs_kept=n_kept, frac_kept=n_kept / m,
        n_pairs_eta=n_eta, frac_eta=n_eta / m,
        LK_eta_trim=lk, c_coeff=c, additive_bound=bound,
    )


def certified_stats(d, dt, eps):
    """Smallest (eta_u, eta_o) making  d/eta_u - eps <= d~ <= eta_o*d + eps
    hold on ALL recorded pairs at this eps, plus infeasibility counts.

    lower band  d <= eta_u*(d~ + eps):
        d>0, d~+eps>0 -> requires eta_u >= d/(d~+eps)
        d>0, d~+eps<=0 -> NO finite eta_u  (infeasible_u)
        d<=0, d~+eps>=0 -> no constraint
    upper band  d~ - eps <= eta_o*d:
        d~>eps, d>0 -> requires eta_o >= (d~-eps)/d
        d~>eps, d<=0 -> NO finite eta_o  (infeasible_o)
        d~<=eps, d>=0 -> no constraint
    (pairs with d<=0 and d~+eps<0, or d~<=eps and d<0, impose UPPER limits on
    eta_u / eta_o; they are counted separately and never make the max larger.)
    """
    inf_u = (d > 0) & (dt + eps <= 0)
    inf_o = (dt > eps) & (d <= 0)
    req_u = (d > 0) & (dt + eps > 0)
    req_o = (dt > eps) & (d > 0)
    eta_u = float(np.max(d[req_u] / (dt[req_u] + eps))) if req_u.any() else 1.0
    eta_o = float(np.max((dt[req_o] - eps) / d[req_o])) if req_o.any() else 1.0
    eta_u = max(eta_u, 1.0)
    eta_o = max(eta_o, 1.0)
    n_inf = int(inf_u.sum() + inf_o.sum())
    # smallest eps at which no pair is infeasible any more
    e1 = float(np.max(-dt[(d > 0) & (dt < 0)])) if ((d > 0) & (dt < 0)).any() else 0.0
    e2 = float(np.max(dt[(dt > 0) & (d <= 0)])) if ((dt > 0) & (d <= 0)).any() else 0.0
    return dict(
        eta_u_cert=eta_u if n_inf == 0 else float("inf"),
        eta_o_cert=eta_o if n_inf == 0 else float("inf"),
        eta_cert=eta_u * eta_o if n_inf == 0 else float("inf"),
        n_infeasible=n_inf, frac_infeasible=n_inf / len(d),
        eps_min_feasible=max(e1, e2),
    )


def certified_best(d, dt, K, n_grid=80):
    """Best bound the mixed model can certify on this data, optimizing over eps.

    At eps = eps_min_feasible the model is only MARGINALLY feasible: some pair
    has d~ + eps = 0 with d > 0, so eta_u -> infinity there.  The meaningful
    question is therefore

        max_{eps >= eps_min}  L_K(eta(eps)) * (1 - 2*K*eta_u(eps)*eps)

    where (eta_u(eps), eta_o(eps)) are the smallest multipliers that make
    d/eta_u - eps <= d~ <= eta_o*d + eps hold on EVERY recorded pair.
    Larger eps shrinks eta but inflates the additive penalty, so the maximum is
    the honest "best certified bound" for this (split, K).
    """
    eps_min = certified_stats(d, dt, 0.0)["eps_min_feasible"]
    lo = max(eps_min * 1.02, 1e-6)
    grid = np.geomspace(lo, max(lo * 200.0, 0.5), n_grid)
    best = dict(eps_cert=float("nan"), eta_u_certbest=float("nan"),
                eta_o_certbest=float("nan"), eta_certbest=float("nan"),
                LK_certbest=float("nan"), bound_certbest=-np.inf,
                eps_min_feas_K=eps_min)
    for eps in grid:
        c = certified_stats(d, dt, eps)
        eu, eo = c["eta_u_cert"], c["eta_o_cert"]
        if c["n_infeasible"] > 0 or not np.isfinite(eu * eo):
            continue
        lk = L_K(K, eu * eo)
        b = lk * (1.0 - 2.0 * K * eu * eps)
        if b > best["bound_certbest"]:
            best = dict(eps_cert=float(eps), eta_u_certbest=eu,
                        eta_o_certbest=eo, eta_certbest=eu * eo,
                        LK_certbest=lk, bound_certbest=float(b),
                        eps_min_feas_K=eps_min)
    if not np.isfinite(best["bound_certbest"]):
        best["bound_certbest"] = float("nan")
    return best


def make_figures(df):
    os.makedirs(FIGDIR, exist_ok=True)
    datasets = [ds for ds in DATASET_ORDER if ds in df.dataset.unique()]
    plt.rcParams.update({
        "figure.facecolor": "white", "axes.facecolor": "white",
        "axes.grid": True, "grid.color": "#e6e6e6", "grid.linewidth": 0.6,
        "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
    })

    # ---- Figure 1: trimmed vs raw eta^path distributions ----
    ks_show = [1, 3, 5, 7]
    series = [("raw (T6)", "eta_path_raw", 1, C_RAW),
              (r"trim $\epsilon=1/n_{test}$", "eta_trim", 1, C_E1),
              (r"trim $\epsilon=2/n_{test}$", "eta_trim", 2, C_E2)]
    fig, axes = plt.subplots(1, len(datasets),
                             figsize=(4.4 * len(datasets), 3.8), sharey=True)
    axes = np.atleast_1d(axes)
    for ax, ds in zip(axes, datasets):
        for si, (lab, col, lev, c) in enumerate(series):
            data, pos = [], []
            for ki, k in enumerate(ks_show):
                sub = df[(df.dataset == ds) & (df.K == k) & (df.epsilon_level == lev)]
                v = sub[col].values.astype(float)
                v = v[np.isfinite(v)]
                data.append(v if len(v) else np.array([np.nan]))
                pos.append(ki * 1.0 + (si - 1) * 0.26)
            bp = ax.boxplot(data, positions=pos, widths=0.22, patch_artist=True,
                            medianprops=dict(color="#222222", linewidth=1.3),
                            flierprops=dict(marker="o", markersize=2.5,
                                            markerfacecolor=c,
                                            markeredgecolor="none", alpha=0.5))
            for box in bp["boxes"]:
                box.set(facecolor=c, alpha=0.35, edgecolor=c, linewidth=1.1)
            for w in bp["whiskers"] + bp["caps"]:
                w.set(color=c, linewidth=1.0)
            # direct labels: colored inline key carrying the K=7 median
            ax.text(0.025, 0.965 - 0.075 * si, f"{lab}   median @K=7: "
                    f"{np.nanmedian(data[-1]):.1f}", transform=ax.transAxes,
                    color=c, fontsize=8.5, va="top", ha="left", fontweight="bold")
        ax.set_xticks(range(len(ks_show)))
        ax.set_xticklabels([str(k) for k in ks_show])
        ax.set_yscale("log")
        ax.set_ylim(1.0, 3e6)
        ax.set_xlim(-0.55, len(ks_show) - 0.45)
        ax.set_title(ds, color="#222222")
        ax.set_xlabel("budget K")
    axes[0].set_ylabel(r"$\eta^{path}$  (log scale)")
    fig.suptitle(r"Trimmed vs raw $\eta^{path}$, 30 splits "
                 r"(trim: keep pairs with $|d|\geq\epsilon$ and $|\tilde d|\geq\epsilon$)",
                 y=1.02, fontsize=11)
    fig.tight_layout()
    p1 = os.path.join(FIGDIR, "N6_eta_trimmed_vs_raw.png")
    fig.savefig(p1, dpi=200, bbox_inches="tight")
    plt.close(fig)

    # ---- Figure 2: additive bound vs realized ratio ----
    ks = np.arange(1, K_MAX + 1)
    fig, axes = plt.subplots(1, len(datasets),
                             figsize=(6.0 * len(datasets), 3.9), sharey=True)
    axes = np.atleast_1d(axes)
    lines = [
        ("realized ratio", "ratio", 1, C_ACC, "-"),
        (r"trimmed bound $\epsilon=1/n_{test}$", "additive_bound", 1, C_E1, "-"),
        (r"trimmed bound $\epsilon=2/n_{test}$", "additive_bound", 2, C_E2, "--"),
        (r"best certified ($\epsilon$ optimized)", "bound_certbest", 1, "#666666", "-."),
        (r"$L_K(\eta^{path}_{raw})$, T6 baseline", "LK_raw", 1, C_RAW, ":"),
    ]
    for ax, ds in zip(axes, datasets):
        ends = []
        for lab, col, lev, c, st in lines:
            med, q1, q3 = [], [], []
            for k in ks:
                v = df[(df.dataset == ds) & (df.K == k) &
                       (df.epsilon_level == lev)][col].values.astype(float)
                v = v[np.isfinite(v)]
                med.append(np.nanmedian(v) if len(v) else np.nan)
                q1.append(np.nanpercentile(v, 25) if len(v) else np.nan)
                q3.append(np.nanpercentile(v, 75) if len(v) else np.nan)
            ax.plot(ks, med, st, color=c, linewidth=2)
            ax.fill_between(ks, q1, q3, color=c, alpha=0.14, linewidth=0)
            ends.append([med[-1], c, f"{lab}  {med[-1]:.3f}"])
        # direct right-edge labels, pushed apart so they never overlap
        ends.sort(key=lambda r: -r[0])
        gap = 0.105
        for i in range(1, len(ends)):
            if ends[i - 1][0] - ends[i][0] < gap:
                ends[i][0] = ends[i - 1][0] - gap
        for yv, c, txt in ends:
            ax.annotate(txt, xy=(K_MAX + 0.12, yv), xycoords="data",
                        fontsize=7.5, color=c, va="center", ha="left")
        ax.axhline(0.0, color="#bbbbbb", linewidth=0.8)
        ax.set_ylim(-0.72, 1.18)
        ax.set_xlim(0.85, K_MAX + 2.9)
        ax.set_xticks(ks)
        ax.set_title(ds, color="#222222")
        ax.set_xlabel("budget K")
    axes[0].set_ylabel("value (median, IQR band)")
    fig.suptitle(r"Additive-model bounds vs realized predictive-greedy ratio "
                 r"(bound $= L_K(\eta)\,(1-2K\eta_u\epsilon)$)",
                 y=1.02, fontsize=11)
    fig.tight_layout()
    p2 = os.path.join(FIGDIR, "N6_bound_vs_ratio.png")
    fig.savefig(p2, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return p1, p2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", nargs="+", default=DATASET_ORDER,
                    choices=DATASET_ORDER)
    ap.add_argument("--splits", type=int, default=N_SPLITS)
    ap.add_argument("--no-figures", action="store_true")
    args = ap.parse_args()

    datasets = get_datasets(args.datasets)
    rows = []
    for ds_name in args.datasets:
        X, y = datasets[ds_name]
        for seed in range(args.splits):
            t0 = time.time()
            step_pairs, ratios, n_test = run_split_pairs(X, y, seed)
            for K in range(1, K_MAX + 1):
                arr = np.array([p for t in range(K) for p in step_pairs[t]],
                               dtype=float)
                d, dt = arr[:, 0], arr[:, 1]
                # raw T6 eta^path, recomputed here as a consistency check
                v = (d > TOL) & (dt > TOL)
                if v.any():
                    eu_raw = float(np.max(d[v] / dt[v]))
                    eo_raw = float(np.max(dt[v] / d[v]))
                    eta_raw = eu_raw * eo_raw
                    lk_raw = L_K(K, eta_raw)
                else:
                    eu_raw = eo_raw = eta_raw = lk_raw = float("nan")
                cert_best = certified_best(d, dt, K)
                for lev in EPS_LEVELS:
                    eps = lev / n_test
                    rec = dict(dataset=ds_name, split=seed, K=K,
                               epsilon_level=lev, epsilon=eps, n_test=n_test,
                               n_pairs=len(d))
                    rec.update(trimmed_stats(d, dt, eps, K))
                    rec.update(certified_stats(d, dt, eps))
                    rec.update(cert_best)
                    rec.update(ratio=ratios[K], eta_path_raw=eta_raw,
                               eta_u_path_raw=eu_raw, eta_o_path_raw=eo_raw,
                               LK_raw=lk_raw)
                    rows.append(rec)
            r7 = [r for r in rows if r["dataset"] == ds_name and r["split"] == seed
                  and r["K"] == K_MAX and r["epsilon_level"] == 1][0]
            print(f"[{ds_name} split {seed}] {time.time() - t0:6.1f}s  "
                  f"n_test={n_test}  eta_raw(K=7)={r7['eta_path_raw']:.4g}  "
                  f"eta_trim(K=7,eps1)={r7['eta_trim']:.4g}  "
                  f"frac_kept={r7['frac_kept']:.3f}  "
                  f"bound={r7['additive_bound']:.4f}  ratio={r7['ratio']:.4f}",
                  flush=True)

    cols = ["dataset", "split", "K", "epsilon_level", "epsilon", "n_test",
            "eta_u_trim", "eta_o_trim", "eta_trim", "n_pairs", "n_pairs_kept",
            "frac_kept", "n_pairs_eta", "frac_eta", "ratio", "LK_eta_trim",
            "c_coeff", "additive_bound", "eta_path_raw", "eta_u_path_raw",
            "eta_o_path_raw", "LK_raw", "eta_u_cert", "eta_o_cert", "eta_cert",
            "n_infeasible", "frac_infeasible", "eps_min_feasible",
            "eps_min_feas_K", "eps_cert", "eta_u_certbest",
            "eta_o_certbest", "eta_certbest", "LK_certbest", "bound_certbest"]
    df = pd.DataFrame(rows)[cols]
    full = (args.splits == N_SPLITS and set(args.datasets) == set(DATASET_ORDER))
    out_csv = os.path.join(HERE, "N6_eta_trimmed.csv" if full
                           else "N6_eta_trimmed_trial.csv")
    df.to_csv(out_csv, index=False)
    print(f"\nwrote {out_csv}  ({len(df)} rows)"
          + ("" if full else "   [TRIAL RUN, full CSV untouched]"))

    # ---- aggregate table ----
    def q(v, p):
        v = np.asarray(v, dtype=float)
        v = v[np.isfinite(v)]
        return np.nanpercentile(v, p) if len(v) else float("nan")

    print("\n=== median [q1, q3] over splits ===")
    hdr = (f"{'dataset':>14} {'K':>2} {'lev':>3} {'eps':>7} {'eta_raw':>9} "
           f"{'eta_trim':>9} {'[q1':>8} {'q3]':>9} {'frac_kept':>9} "
           f"{'LK_trim':>8} {'bound':>9} {'ratio':>7} {'eta_cert':>9} "
           f"{'fr_infeas':>9} {'eps_minf':>8}")
    print(hdr)
    print("-" * len(hdr))
    for ds in [d for d in DATASET_ORDER if d in df.dataset.unique()]:
        for k in [1, 3, 5, 7]:
            for lev in EPS_LEVELS:
                s = df[(df.dataset == ds) & (df.K == k) & (df.epsilon_level == lev)]
                print(f"{ds:>14} {k:2d} {lev:3d} {s.epsilon.iloc[0]:7.4f} "
                      f"{q(s.eta_path_raw, 50):9.4g} {q(s.eta_trim, 50):9.4g} "
                      f"{q(s.eta_trim, 25):8.4g} {q(s.eta_trim, 75):9.4g} "
                      f"{q(s.frac_kept, 50):9.3f} {q(s.LK_eta_trim, 50):8.4f} "
                      f"{q(s.additive_bound, 50):9.4f} {q(s.ratio, 50):7.4f} "
                      f"{q(s.eta_cert, 50):9.4g} {q(s.frac_infeasible, 50):9.3f} "
                      f"{q(s.eps_min_feasible, 50):8.4f}")
    print("\n=== best CERTIFIED bound (model holds on EVERY pair, eps optimized) ===")
    hdr2 = (f"{'dataset':>14} {'K':>2} {'eps_min':>8} {'eps_opt':>8} {'eps/unit':>9} "
            f"{'eta_u':>8} {'eta_o':>8} {'eta':>8} {'L_K':>8} {'bound':>9}")
    print(hdr2)
    print("-" * len(hdr2))
    for ds in [d for d in DATASET_ORDER if d in df.dataset.unique()]:
        for k in [1, 3, 5, 7]:
            s = df[(df.dataset == ds) & (df.K == k) & (df.epsilon_level == 1)]
            unit = 1.0 / s.n_test.iloc[0]
            print(f"{ds:>14} {k:2d} {q(s.eps_min_feas_K, 50):8.4f} "
                  f"{q(s.eps_cert, 50):8.4f} {q(s.eps_cert, 50) / unit:9.2f} "
                  f"{q(s.eta_u_certbest, 50):8.4g} {q(s.eta_o_certbest, 50):8.4g} "
                  f"{q(s.eta_certbest, 50):8.4g} {q(s.LK_certbest, 50):8.4f} "
                  f"{q(s.bound_certbest, 50):9.4f}")

    # ---- sanity checks ----
    print("\n=== sanity checks ===")
    fin = df[np.isfinite(df.eta_trim)]
    print(f"[s1] eta_trim == eta_u_trim*eta_o_trim: "
          f"{np.allclose(fin.eta_trim, fin.eta_u_trim * fin.eta_o_trim, rtol=1e-9)}")
    print(f"[s2] min eta_trim = {np.nanmin(fin.eta_trim):.6g} (should be >= 1)")
    print(f"[s3] eta_trim <= eta_path_raw on all rows (trimming only removes "
          f"pairs): {bool((fin.eta_trim <= fin.eta_path_raw + 1e-9).all())}  "
          f"(violations {int((fin.eta_trim > fin.eta_path_raw + 1e-9).sum())})")
    l2 = df[df.epsilon_level == 2].reset_index(drop=True)
    l1 = df[df.epsilon_level == 1].reset_index(drop=True)
    print(f"[s4] eta_trim non-increasing in eps (level2 <= level1): "
          f"{bool((l2.eta_trim.fillna(0) <= l1.eta_trim.fillna(0) + 1e-9).all())}")
    print(f"[s5] rows with additive_bound > 0: "
          f"{int((df.additive_bound > 0).sum())} / {len(df)}")
    print(f"[s6] rows with ratio < additive_bound (bound violated by the data): "
          f"{int((df.ratio < df.additive_bound - 1e-12).sum())} / {len(df)}")
    print(f"[s7] rows where the mixed model is infeasible at this eps "
          f"(no finite eta_u/eta_o): {int((df.n_infeasible > 0).sum())} / {len(df)}")
    print(f"[s9] rows with best CERTIFIED bound > 0: "
          f"{int((df.bound_certbest > 0).sum())} / {len(df)};  "
          f"max over all rows = {np.nanmax(df.bound_certbest.values):.4f}")
    print(f"[s10] ratio < best certified bound (certified bound violated): "
          f"{int((df.ratio < df.bound_certbest - 1e-12).sum())} / {len(df)}")
    print(f"[s8] raw eta^path vs T6 CSV: ", end="")
    t6p = os.path.join(HERE, "T6_eta_path.csv")
    if full and os.path.exists(t6p):
        t6 = pd.read_csv(t6p)
        mrg = df[df.epsilon_level == 1].merge(
            t6[["dataset", "split", "K", "eta_path"]],
            on=["dataset", "split", "K"], how="inner")
        ok = np.allclose(mrg.eta_path_raw.values, mrg.eta_path.values,
                         rtol=1e-9, equal_nan=True)
        print(f"{len(mrg)} rows matched, identical: {ok}")
    else:
        print("skipped (trial run or T6 CSV missing)")

    if not args.no_figures:
        p1, p2 = make_figures(df)
        print(f"\nwrote {p1}\nwrote {p2}")


if __name__ == "__main__":
    main()
