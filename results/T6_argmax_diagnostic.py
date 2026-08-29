#!/usr/bin/env python3
"""T6 supplement: which (d, d~) pairs attain eta_u^path and eta_o^path.

Re-runs the SAME deterministic predictive-greedy trajectories as T6_eta_path.py
(same splits, seeds, caches, tie-breaking; oracle greedy omitted since it does
not affect the recorded pairs) and reports, per (dataset, split), at K = 7:
  - the pair (d, d~) attaining eta_u^path = max d/d~  (valid pairs only)
  - the pair (d, d~) attaining eta_o^path = max d~/d
  - the minimum positive d~ and minimum positive d seen on the trajectory
  - the gain-quantization scale 1/n_train (CV accuracy granularity)

Purpose: verify the mechanism claim in T6_summary.md that eta^path is driven by
near-zero gains (denominators at the quantization scale), not by large gains
being mispredicted. Output: results/T6_argmax_diagnostic.json + stdout summary.

Run AFTER (or independently of) T6_eta_path.py:  python3 T6_argmax_diagnostic.py
"""
import json
import os

import numpy as np
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.tree import DecisionTreeClassifier

from T6_eta_path import DATASET_ORDER, K_MAX, N_SPLITS, TOL, TREE_SEED, get_datasets

HERE = os.path.dirname(os.path.abspath(__file__))


def trajectory_pairs(X, y, seed):
    """Identical trajectory logic to T6_eta_path.run_split (predictive greedy)."""
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
    S = frozenset()
    pairs = []
    for _t in range(K_MAX):
        base_ft, base_f = ft(S), f(S)
        best_e, best_gain = None, None
        for e in range(n_feat):
            if e in S:
                continue
            gain = ft(S | {e}) - base_ft
            pairs.append((f(S | {e}) - base_f, gain))
            if best_gain is None or gain > best_gain + TOL:
                best_e, best_gain = e, gain
        S = S | {best_e}
    return np.array(pairs, dtype=float), len(y_tr)


def main():
    datasets = get_datasets(DATASET_ORDER)
    out = []
    for ds_name in DATASET_ORDER:
        X, y = datasets[ds_name]
        for seed in range(N_SPLITS):
            pairs, n_train = trajectory_pairs(X, y, seed)
            d, dt = pairs[:, 0], pairs[:, 1]
            valid = (d > TOL) & (dt > TOL)
            if not valid.any():
                continue
            dv, dtv = d[valid], dt[valid]
            iu, io = np.argmax(dv / dtv), np.argmax(dtv / dv)
            out.append(
                dict(
                    dataset=ds_name,
                    split=seed,
                    n_train=n_train,
                    quant_scale=1.0 / n_train,
                    argmax_u_d=dv[iu],
                    argmax_u_dt=dtv[iu],
                    eta_u=dv[iu] / dtv[iu],
                    argmax_o_d=dv[io],
                    argmax_o_dt=dtv[io],
                    eta_o=dtv[io] / dv[io],
                    min_pos_dt=float(dtv.min()),
                    min_pos_d=float(dv.min()),
                    med_pos_dt=float(np.median(dtv)),
                    med_pos_d=float(np.median(dv)),
                )
            )
            print(
                f"[{ds_name} s{seed}] eta_u={out[-1]['eta_u']:8.1f} at "
                f"(d={out[-1]['argmax_u_d']:.4f}, dt={out[-1]['argmax_u_dt']:.5f}); "
                f"eta_o={out[-1]['eta_o']:6.1f} at "
                f"(d={out[-1]['argmax_o_d']:.5f}, dt={out[-1]['argmax_o_dt']:.4f}); "
                f"1/n_train={1 / n_train:.5f}",
                flush=True,
            )
    with open(os.path.join(HERE, "T6_argmax_diagnostic.json"), "w") as fh:
        json.dump(out, fh, indent=1)

    # summary: is the eta_u denominator (predicted gain) at the quantization scale?
    for ds_name in DATASET_ORDER:
        rows = [r for r in out if r["dataset"] == ds_name]
        rel_u = [r["argmax_u_dt"] / r["quant_scale"] for r in rows]  # in units of 1/n_train
        rel_o = [r["argmax_o_d"] / r["quant_scale"] for r in rows]
        print(
            f"\n{ds_name}: argmax-eta_u predicted gain d~ in units of 1/n_train: "
            f"median {np.median(rel_u):.2f} [q1 {np.percentile(rel_u, 25):.2f}, "
            f"q3 {np.percentile(rel_u, 75):.2f}]"
        )
        print(
            f"{ds_name}: argmax-eta_o true gain d in units of 1/n_train: "
            f"median {np.median(rel_o):.2f} [q1 {np.percentile(rel_o, 25):.2f}, "
            f"q3 {np.percentile(rel_o, 75):.2f}]"
        )


if __name__ == "__main__":
    main()
