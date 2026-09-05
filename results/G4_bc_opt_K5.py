#!/usr/bin/env python3
"""TASKS5 G4.1: brute-force OPT_K on breast_cancer up to K=5.

Night 4 (TASKS4 F1.4) stopped at K=4 because the serial estimate for K=1..5 was
about 74 minutes on a contended machine (see results/F1_fixes.md section 4,
"K=5 的 OPT 没有测").  This script closes that gap.

What it computes, for every seed and every K = 1..KMAX:

    OPT_K            = max_{|S|=K} f(S)          (EXHAUSTIVE enumeration)
    f(greedy^f [:K]) = value of the greedy-on-f prefix
    f(greedy^ft[:K]) = value of the greedy-on-ftilde prefix

f is the SAME held-out decision-tree accuracy used everywhere else in E1
(results/E1_run.py: make_true_eval + make_tree, 80/20 split with
random_state=seed), and ftilde is the SAME train-only 5-fold CV surrogate
(make_surrogate).  Both are wrapped in the same CachedSetFunction keyed by
frozenset, exactly as opt_bruteforce() in E1_run.py does, so a subset evaluated
at K is reused at larger K.  Nothing in E1_run.py or src/ is modified: the
module is loaded and its functions are called.

Difference from E1_run.py --part opt_bc: seeds are spread over a process pool
(the per-seed computation is completely independent and deterministic, so the
output is bit-for-bit identical to the serial loop; --workers 1 reproduces the
serial order).  This is what makes K=5 affordable.

One command:

    python3 results/G4_bc_opt_K5.py            # writes G4_bc_opt_K5.csv

Verification built in: the K <= 4 rows produced here are compared against
results/E1_opt_breast_cancer.csv (night 4) and must agree to the 6 decimals
that file stores.  A mismatch is a hard failure.

Status: [VERIFIED-EXHAUSTIVE] for the OPT values (full enumeration of
C(30,K) subsets, K <= 5).
"""
import argparse
import csv
import importlib.util
import math
import os
import sys
import time
from itertools import combinations
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'src'))

from im_graph import CachedSetFunction                      # noqa: E402
from sklearn.model_selection import train_test_split        # noqa: E402

OUT_CSV = os.path.join(HERE, 'G4_bc_opt_K5.csv')
REF_CSV = os.path.join(HERE, 'E1_opt_breast_cancer.csv')
FIELDS = ['dataset', 'seed', 'K', 'opt', 'f_greedy_f', 'f_greedy_ftilde',
          'greedy_f_over_opt', 'greedy_ftilde_over_opt']

DATASET = 'breast_cancer'


def _load_E1():
    """Import results/E1_run.py as a module without modifying it."""
    spec = importlib.util.spec_from_file_location(
        'E1_run_g4', os.path.join(HERE, 'E1_run.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


E1 = _load_E1()


def one_seed(args):
    """Everything for a single seed.  Pure function of (seed, Kmax)."""
    seed, Kmax = args
    t0 = time.time()
    X, y, _ = E1.load_dataset(DATASET)
    ground = list(range(X.shape[1]))
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed)
    Ftil = CachedSetFunction(E1.make_surrogate(X_train, y_train, E1.make_tree))
    Ftrue = CachedSetFunction(E1.make_true_eval(X_train, y_train, X_test,
                                                y_test, E1.make_tree))
    pt = E1.greedy_exact(Ftil, ground, Kmax)
    pf = E1.greedy_exact(Ftrue, ground, Kmax)
    rows, best_sets = [], {}
    for K in range(1, Kmax + 1):
        opt, arg = -1.0, None
        for c in combinations(ground, K):
            v = Ftrue(set(c))
            if v > opt:
                opt, arg = v, c
        vf = Ftrue(set(pf[:K]))
        vt = Ftrue(set(pt[:K]))
        best_sets[K] = list(arg)
        rows.append(dict(dataset=DATASET, seed=seed, K=K, opt=f'{opt:.6f}',
                         f_greedy_f=f'{vf:.6f}',
                         f_greedy_ftilde=f'{vt:.6f}',
                         greedy_f_over_opt=f'{vf / opt:.6f}',
                         greedy_ftilde_over_opt=f'{vt / opt:.6f}'))
    return dict(seed=seed, rows=rows, best_sets=best_sets,
                greedy_f=pf, greedy_ftilde=pt,
                n_evals_f=Ftrue.evals, n_evals_ftilde=Ftil.evals,
                seconds=time.time() - t0)


def check_against_night4(rows):
    """The K <= 4 rows must reproduce results/E1_opt_breast_cancer.csv."""
    if not os.path.exists(REF_CSV):
        return 'SKIPPED (reference file missing)'
    ref = {}
    with open(REF_CSV) as fh:
        for r in csv.DictReader(fh):
            ref[(r['dataset'], int(r['seed']), int(r['K']))] = r
    n, bad = 0, []
    for r in rows:
        key = (r['dataset'], int(r['seed']), int(r['K']))
        if key not in ref:
            continue
        n += 1
        for col in FIELDS[3:]:
            if ref[key][col] != r[col]:
                bad.append((key, col, ref[key][col], r[col]))
    if bad:
        raise AssertionError(f'night-4 mismatch on {len(bad)} cells: {bad[:5]}')
    return f'PASS ({n} rows identical to E1_opt_breast_cancer.csv)'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kmax', type=int, default=5)
    ap.add_argument('--seeds', type=int, default=10,
                    help='seeds 0..seeds-1 (night 4 used 10)')
    ap.add_argument('--workers', type=int, default=4,
                    help='process pool size; results do not depend on it')
    ap.add_argument('--out', default=OUT_CSV)
    a = ap.parse_args()

    n_feat = 30
    total = sum(math.comb(n_feat, K) for K in range(1, a.kmax + 1))
    print(f'[G4.1] {DATASET}: n_features={n_feat}, seeds=0..{a.seeds - 1}, '
          f'Kmax={a.kmax}', flush=True)
    for K in range(1, a.kmax + 1):
        print(f'       C(30,{K}) = {math.comb(n_feat, K)}', flush=True)
    print(f'       distinct subsets per seed = {total}, '
          f'x{a.seeds} seeds = {total * a.seeds}', flush=True)

    t0 = time.time()
    jobs = [(s, a.kmax) for s in range(a.seeds)]
    if a.workers > 1:
        with Pool(a.workers) as pool:
            out = []
            for res in pool.imap_unordered(one_seed, jobs):
                out.append(res)
                print(f'  seed={res["seed"]} done in {res["seconds"]:.1f}s '
                      f'({res["n_evals_f"]} f-evals, '
                      f'{res["n_evals_ftilde"]} ftilde-evals)', flush=True)
    else:
        out = []
        for j in jobs:
            res = one_seed(j)
            out.append(res)
            print(f'  seed={res["seed"]} done in {res["seconds"]:.1f}s',
                  flush=True)
    wall = time.time() - t0
    out.sort(key=lambda r: r['seed'])
    rows = [r for res in out for r in res['rows']]

    print(f'[G4.1] wall time {wall:.1f}s with {a.workers} workers', flush=True)
    print('[G4.1] night-4 consistency:', check_against_night4(rows), flush=True)

    with open(a.out, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    print('wrote', a.out, flush=True)

    print()
    print('| K | subsets C(30,K) | median f(greedy^f)/OPT | min | '
          'median f(greedy^ft)/OPT | min |')
    print('|---|---|---|---|---|---|')
    for K in range(1, a.kmax + 1):
        gf = [float(r['greedy_f_over_opt']) for r in rows if r['K'] == K]
        gt = [float(r['greedy_ftilde_over_opt']) for r in rows if r['K'] == K]
        print(f'| {K} | {math.comb(n_feat, K)} | {np.median(gf):.4f} | '
              f'{min(gf):.4f} | {np.median(gt):.4f} | {min(gt):.4f} |')
    print()
    for K in (a.kmax,):
        gf = [float(r['greedy_f_over_opt']) for r in rows if r['K'] == K]
        print(f'[G4.1] K={K} f(greedy^f)/OPT per seed: '
              + ' '.join(f'{v:.4f}' for v in gf), flush=True)
        print(f'[G4.1] K={K} mean={np.mean(gf):.4f} '
              f'median={np.median(gf):.4f} min={min(gf):.4f} '
              f'max={max(gf):.4f}', flush=True)
    for res in out:
        print(f'  seed={res["seed"]} OPT_{a.kmax} argmax features='
              f'{res["best_sets"][a.kmax]} greedy^f={sorted(res["greedy_f"])} '
              f'greedy^ftilde={sorted(res["greedy_ftilde"])}', flush=True)


if __name__ == '__main__':
    main()
