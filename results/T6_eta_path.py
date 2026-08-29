#!/usr/bin/env python3
"""T6: eta^path measurement for a real feature-selection surrogate.

Setting (reviewer R2-2, "when does the prediction-error criterion matter"):
  ground set = features of a sklearn dataset
  f(S)  = held-out (20%) accuracy of DecisionTreeClassifier(random_state=0)
          trained on the training split restricted to feature subset S
  f~(S) = 5-fold CV accuracy (cross_val_score mean, deterministic
          StratifiedKFold(5), no shuffle) of the same model on the training split
  f(empty) = fraction of test samples equal to the TRAINING-set majority class
  f~(empty) = fraction of training samples equal to the training-set majority
  (this equals DummyClassifier(strategy='most_frequent') accuracy; we compute the
  frequency directly, choice documented in T6_summary.md)

Protocol per (dataset, split seed in 0..29):
  - 80/20 stratified train_test_split(random_state=seed)
  - memo caches for f and f~ (dict keyed by frozenset), shared within the split
  - single-step greedy on f~ for K_MAX=7 steps (one K=7 trajectory contains all
    prefixes; ties broken toward the lowest feature index; the argmax is taken
    over raw predicted gains, even if the best gain is <= 0, since the paper's
    predictive greedy always fills the budget)
  - at each trajectory state S^t, record (d_e(S^t), d~_e(S^t)) for ALL remaining
    candidates e
  - oracle greedy on f with the same tie-breaking and its own use of the f cache
  - for each K = 1..7 (pairs from states t < K):
      eta_u^path = max d/d~ over pairs with d > tol and d~ > tol
      eta_o^path = max d~/d over the same pairs
      eta^path   = eta_u^path * eta_o^path
      frac_nonpos_d   = fraction of pairs with d  <= tol
      frac_nonpos_dt  = fraction of pairs with d~ <= tol
      frac_direction_violation = fraction with sign(d) and sign(d~) strictly
                                 opposite (d > tol and d~ < -tol, or vice versa)
      pairs with d <= tol or d~ <= tol are EXCLUDED from eta but counted above
      ratio(K) = f(S~_K) / f(S_K^oracle)   (raw held-out accuracies)
      LK_bound = 1 - (1 - 1/(eta^path * K))^K  with the same split's eta^path(K)
  tol = 1e-12 (guards float noise around exact-zero accuracy differences)

Outputs (all one-shot reproducible from this script):
  results/T6_eta_path.csv
  figures/T6_eta_path_distribution.png
  figures/T6_ratio_vs_bound.png
  aggregate median/IQR table printed to stdout (quoted in results/T6_summary.md)

openml airline satisfaction is SKIPPED: the environment has no reliable network
access (agent-proxy restricted), per task instructions this is recorded here and
in T6_summary.md.

Usage:
  python3 T6_eta_path.py                 # full run (3 datasets x 30 splits)
  python3 T6_eta_path.py --datasets wine --splits 1   # timing trial
"""
import argparse
import os
import time

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer, load_digits, load_wine
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.tree import DecisionTreeClassifier

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIGDIR = os.path.join(ROOT, "figures")

K_MAX = 7
N_SPLITS = 30
TREE_SEED = 0
TOL = 1e-12

# Okabe-Ito subset, CVD-validated (dataviz validate_palette.js: ALL CHECKS PASS)
PALETTE = {"breast_cancer": "#0072B2", "wine": "#E69F00", "digits20": "#009E73"}
DATASET_ORDER = ["breast_cancer", "wine", "digits20"]


def get_datasets(names):
    out = {}
    if "breast_cancer" in names:
        d = load_breast_cancer()
        out["breast_cancer"] = (d.data, d.target)
    if "wine" in names:
        d = load_wine()
        out["wine"] = (d.data, d.target)
    if "digits20" in names:
        d = load_digits()
        out["digits20"] = (d.data[:, :20], d.target)  # first 20 pixel features
    return out


def run_split(X, y, seed):
    """One train/test split: predictive + oracle greedy, per-K statistics."""
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
        """Greedy on value_fn; ties -> lowest index. Optionally record, at each
        state, (d_e, d~_e) for every candidate (uses both f and ft)."""
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

    rows = []
    for K in range(1, K_MAX + 1):
        pairs = np.array(
            [p for t in range(K) for p in step_pairs[t]], dtype=float
        )  # shape (m, 2): [:,0]=d, [:,1]=d~
        d, dt = pairs[:, 0], pairs[:, 1]
        m = len(pairs)
        frac_nonpos_d = float(np.mean(d <= TOL))
        frac_nonpos_dt = float(np.mean(dt <= TOL))
        viol = ((d > TOL) & (dt < -TOL)) | ((d < -TOL) & (dt > TOL))
        frac_dirviol = float(np.mean(viol))
        valid = (d > TOL) & (dt > TOL)
        if valid.any():
            eta_u = float(np.max(d[valid] / dt[valid]))
            eta_o = float(np.max(dt[valid] / d[valid]))
            eta = eta_u * eta_o
            lk = 1.0 - (1.0 - 1.0 / (eta * K)) ** K
        else:
            eta_u = eta_o = eta = lk = float("nan")
        S_pred = frozenset(chosen_pred[:K])
        S_orac = frozenset(chosen_oracle[:K])
        ratio = f(S_pred) / f(S_orac)
        rows.append(
            dict(
                K=K,
                eta_u_path=eta_u,
                eta_o_path=eta_o,
                eta_path=eta,
                ratio=ratio,
                LK_bound=lk,
                frac_nonpos_d=frac_nonpos_d,
                frac_nonpos_dt=frac_nonpos_dt,
                frac_direction_violation=frac_dirviol,
                n_pairs=m,
                n_valid_pairs=int(valid.sum()),
            )
        )
    return rows


def make_figures(df):
    os.makedirs(FIGDIR, exist_ok=True)
    datasets = [ds for ds in DATASET_ORDER if ds in df.dataset.unique()]
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.grid": True,
            "grid.color": "#e6e6e6",
            "grid.linewidth": 0.6,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.size": 10,
        }
    )

    # Figure 1: eta^path distribution over splits, per dataset, per K (boxplots)
    fig, axes = plt.subplots(
        1, len(datasets), figsize=(4.0 * len(datasets), 3.6), sharey=True
    )
    axes = np.atleast_1d(axes)
    for ax, ds in zip(axes, datasets):
        sub = df[df.dataset == ds]
        data = [sub[sub.K == k].eta_path.dropna().values for k in range(1, K_MAX + 1)]
        c = PALETTE[ds]
        bp = ax.boxplot(
            data,
            tick_labels=[str(k) for k in range(1, K_MAX + 1)],
            patch_artist=True,
            widths=0.55,
            medianprops=dict(color="#222222", linewidth=1.4),
            flierprops=dict(
                marker="o", markersize=3, markerfacecolor=c, markeredgecolor="none",
                alpha=0.55,
            ),
        )
        for box in bp["boxes"]:
            box.set(facecolor=c, alpha=0.35, edgecolor=c, linewidth=1.2)
        for w in bp["whiskers"] + bp["caps"]:
            w.set(color=c, linewidth=1.1)
        med7 = np.nanmedian(sub[sub.K == K_MAX].eta_path.values)
        ax.text(
            0.98, 0.96, f"median @K=7: {med7:.1f}",
            transform=ax.transAxes, ha="right", va="top", fontsize=9, color="#333333",
        )
        ax.set_yscale("log")
        ax.set_title(ds, color="#222222")
        ax.set_xlabel("budget K")
    axes[0].set_ylabel(r"$\eta^{path}$  (log scale)")
    fig.suptitle(
        r"$\eta^{path}$ over 30 random splits (decision tree, CV surrogate)",
        y=1.02, fontsize=11,
    )
    fig.tight_layout()
    p1 = os.path.join(FIGDIR, "T6_eta_path_distribution.png")
    fig.savefig(p1, dpi=200, bbox_inches="tight")
    plt.close(fig)

    # Figure 2: realized ratio vs the L_K(eta^path) bound (median + IQR bands)
    fig, axes = plt.subplots(
        1, len(datasets), figsize=(4.0 * len(datasets), 3.6), sharey=True
    )
    axes = np.atleast_1d(axes)
    ks = np.arange(1, K_MAX + 1)
    for ax, ds in zip(axes, datasets):
        sub = df[df.dataset == ds]
        c = PALETTE[ds]
        for col, style, lab in [
            ("ratio", "-", r"ratio $f(\tilde S_K)/f(S_K^{oracle})$"),
            ("LK_bound", "--", r"$L_K(\eta^{path})$ bound"),
        ]:
            med = np.array([np.nanmedian(sub[sub.K == k][col]) for k in ks])
            q1 = np.array([np.nanpercentile(sub[sub.K == k][col], 25) for k in ks])
            q3 = np.array([np.nanpercentile(sub[sub.K == k][col], 75) for k in ks])
            color = c if col == "ratio" else "#666666"
            ax.plot(ks, med, style, color=color, linewidth=2, label=lab)
            ax.fill_between(ks, q1, q3, color=color, alpha=0.18, linewidth=0)
        ax.set_ylim(0, 1.12)
        ax.axhline(1.0, color="#bbbbbb", linewidth=0.8)
        ax.set_title(ds, color="#222222")
        ax.set_xlabel("budget K")
        ax.text(
            ks[-1], np.nanmedian(sub[sub.K == K_MAX]["ratio"]) + 0.045,
            f"{np.nanmedian(sub[sub.K == K_MAX]['ratio']):.3f}",
            ha="right", fontsize=9, color=c,
        )
    axes[0].set_ylabel("value (median, IQR band)")
    axes[0].legend(loc="lower left", frameon=False, fontsize=8)
    fig.suptitle(
        "Realized predictive-greedy ratio vs worst-case bound "
        r"$L_K(\eta^{path}) = 1-(1-1/(\eta^{path}K))^K$",
        y=1.02, fontsize=11,
    )
    fig.tight_layout()
    p2 = os.path.join(FIGDIR, "T6_ratio_vs_bound.png")
    fig.savefig(p2, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return p1, p2


def aggregate_table(df):
    """Median and IQR per (dataset, K) for the key columns."""
    recs = []
    for ds in [d for d in DATASET_ORDER if d in df.dataset.unique()]:
        for k in range(1, K_MAX + 1):
            sub = df[(df.dataset == ds) & (df.K == k)]
            rec = dict(dataset=ds, K=k, n_splits=len(sub))
            for col in [
                "eta_u_path", "eta_o_path", "eta_path", "ratio", "LK_bound",
                "frac_nonpos_d", "frac_nonpos_dt", "frac_direction_violation",
            ]:
                v = sub[col].values.astype(float)
                rec[f"{col}_med"] = np.nanmedian(v)
                rec[f"{col}_q1"] = np.nanpercentile(v, 25)
                rec[f"{col}_q3"] = np.nanpercentile(v, 75)
            recs.append(rec)
    return pd.DataFrame(recs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--datasets", nargs="+", default=DATASET_ORDER,
        choices=DATASET_ORDER,
    )
    ap.add_argument("--splits", type=int, default=N_SPLITS)
    ap.add_argument("--no-figures", action="store_true")
    args = ap.parse_args()

    datasets = get_datasets(args.datasets)
    all_rows = []
    for ds_name in args.datasets:
        X, y = datasets[ds_name]
        for seed in range(args.splits):
            t0 = time.time()
            rows = run_split(X, y, seed)
            for r in rows:
                r["dataset"] = ds_name
                r["split"] = seed
            all_rows.extend(rows)
            print(
                f"[{ds_name} split {seed}] {time.time() - t0:6.1f}s  "
                f"eta_path(K=7)={rows[-1]['eta_path']:.3g}  "
                f"ratio(K=7)={rows[-1]['ratio']:.4f}",
                flush=True,
            )

    cols = [
        "dataset", "split", "K", "eta_u_path", "eta_o_path", "eta_path",
        "ratio", "LK_bound", "frac_nonpos_d", "frac_nonpos_dt",
        "frac_direction_violation", "n_pairs", "n_valid_pairs",
    ]
    df = pd.DataFrame(all_rows)[cols]
    out_csv = os.path.join(HERE, "T6_eta_path.csv")
    if args.splits == N_SPLITS and set(args.datasets) == set(DATASET_ORDER):
        df.to_csv(out_csv, index=False)
        print(f"wrote {out_csv}  ({len(df)} rows)")
    else:
        out_csv = os.path.join(HERE, "T6_eta_path_trial.csv")
        df.to_csv(out_csv, index=False)
        print(f"TRIAL RUN -> wrote {out_csv} (full CSV untouched)")

    agg = aggregate_table(df)
    with pd.option_context("display.width", 250, "display.max_columns", 50):
        print("\n=== aggregate (median [q1,q3]) ===")
        show = agg[
            ["dataset", "K", "eta_path_med", "eta_path_q1", "eta_path_q3",
             "eta_u_path_med", "eta_o_path_med", "ratio_med", "ratio_q1",
             "ratio_q3", "LK_bound_med", "frac_nonpos_d_med",
             "frac_nonpos_dt_med", "frac_direction_violation_med"]
        ]
        print(show.to_string(index=False, float_format=lambda x: f"{x:.4g}"))

    # sanity check 1: ratio should exceed the bound whenever both defined
    both = df.dropna(subset=["LK_bound"])
    n_below = int((both.ratio < both.LK_bound - 1e-12).sum())
    print(f"\n[sanity] rows with ratio < LK_bound: {n_below} / {len(both)}")
    # sanity check 2: eta = eta_u * eta_o
    ok = np.allclose(
        both.eta_path, both.eta_u_path * both.eta_o_path, rtol=1e-9
    )
    print(f"[sanity] eta_path == eta_u*eta_o for all rows: {ok}")
    # sanity check 3: eta >= 1 automatically (max-product over pairs)
    print(f"[sanity] min eta_path = {np.nanmin(both.eta_path):.6g} (should be >= 1)")

    if not args.no_figures:
        p1, p2 = make_figures(df)
        print(f"wrote {p1}\nwrote {p2}")


if __name__ == "__main__":
    main()
