#!/usr/bin/env python3
"""TASKS5 G4.2: conservative UNDER-estimate of OPT_K on airline (sanity check).

Why an under-estimate and not OPT.  The E1 airline rows use K = 7 on 22
features, so exact OPT_7 needs C(22,7) = 170,544 held-out evaluations per seed.
That part alone is affordable (about 0.033 s per f evaluation here, so roughly
94 minutes per seed, 15 hours for 10 seeds), and ranking those same subsets by
the surrogate would cost 0.148 s each, i.e. about 7 hours PER SEED.  Both are
far outside the 45-minute box for this task, so full enumeration is out.

What this script computes instead, per seed:

    OPT_hat = max f(S) over  A  u  B  u  {greedy^f set, greedy^ftilde set}

    A  = the top-200 K-subsets ranked by the surrogate ftilde, taken over the
         surrogate core: run greedy on ftilde for TOPM = 12 steps, keep those
         12 features, enumerate all C(12,7) = 792 K-subsets of them and score
         every one with ftilde.  (Ranking by ftilde over ALL C(22,7) subsets is
         the 7-hours-per-seed option above; the core restriction is the
         deviation that makes the ftilde ranking affordable, and it is recorded
         in G4_airline_optproxy.md.)
    B  = 2000 uniformly random K-subsets of the 22 features, drawn from a fixed
         seed (MASTER_SEED below) so the pool is reproducible.
    the two greedy sets are added so that OPT_hat >= f(greedy^f) holds by
         construction; without them the "estimate" could fall below a value we
         already know is feasible and the ratios could exceed 1.

DIRECTION OF THE ERROR.  OPT_hat is a max over a strict SUBSET of the feasible
K-subsets, so OPT_hat <= OPT.  Hence for every S,  f(S)/OPT_hat >= f(S)/OPT :
every ratio this script prints is an UPPER estimate of the corresponding
OPT-normalised ratio.  It can only under-state how much the greedy-on-f
denominator inflates the table, never over-state it.  This is a sanity check;
the experiments table keeps greedy-on-f as the denominator.

f, ftilde, the split and the greedy are all taken from results/E1_run.py by
import; nothing in results/E1_run.py or src/ is modified.

One command:

    python3 results/G4_airline_optproxy.py     # writes G4_airline_optproxy.csv

Built-in verification: the column table_ratio = f(greedy^ftilde)/f(greedy^f)
recomputed here must match the ratio column of results/E1_rows.csv at K=7 for
the same seed, to the 6 decimals that file stores.

Status: [VERIFIED-PARTIAL-ENUM] the OPT_hat values are exact maxima over the
stated candidate pool; they are lower estimates of OPT, not OPT.
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

OUT_CSV = os.path.join(HERE, 'G4_airline_optproxy.csv')
E1_ROWS = os.path.join(HERE, 'E1_rows.csv')

DATASET = 'airline'
MASTER_SEED = 20260905          # fixed: the random pool B is reproducible
TOPM = 12                       # surrogate core size, C(12,7) = 792
N_TOP_FTILDE = 200              # |A|
N_RANDOM = 2000                 # |B|

FIELDS = ['dataset', 'seed', 'K', 'opt_hat', 'f_greedy_f', 'f_greedy_ftilde',
          'table_ratio', 'ratio_ftilde_over_opt_hat', 'greedy_f_over_opt_hat',
          'opt_hat_source', 'n_cand_total', 'n_cand_ftilde_top',
          'n_cand_random', 'n_ftilde_scored', 'seconds']


def _load_E1():
    spec = importlib.util.spec_from_file_location(
        'E1_run_g4b', os.path.join(HERE, 'E1_run.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


E1 = _load_E1()


def random_pool(n_feat, K, seed, n):
    """n distinct uniformly random K-subsets, reproducible from MASTER_SEED."""
    rng = np.random.default_rng([MASTER_SEED, seed])
    out, seen = [], set()
    guard = 0
    while len(out) < n and guard < 200 * n:
        guard += 1
        c = frozenset(int(v) for v in
                      rng.choice(n_feat, size=K, replace=False))
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def one_seed(args):
    seed, K = args
    t0 = time.time()
    X, y, _ = E1.load_dataset(DATASET)
    n_feat = X.shape[1]
    ground = list(range(n_feat))
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed)
    Ftil = CachedSetFunction(E1.make_surrogate(X_train, y_train, E1.make_tree))
    Ftrue = CachedSetFunction(E1.make_true_eval(X_train, y_train, X_test,
                                                y_test, E1.make_tree))

    # E1's own two greedy runs (exact argmax at each step)
    picks_tilde = E1.greedy_exact(Ftil, ground, K)
    picks_true = E1.greedy_exact(Ftrue, ground, K)
    S_ft, S_f = frozenset(picks_tilde[:K]), frozenset(picks_true[:K])

    # (a) surrogate core -> all C(TOPM,K) subsets scored by ftilde -> top 200
    core = E1.greedy_exact(Ftil, ground, min(TOPM, n_feat))
    scored = []
    for c in combinations(sorted(core), K):
        fs = frozenset(c)
        scored.append((Ftil(fs), tuple(sorted(c)), fs))
    n_ftilde_scored = len(scored)
    scored.sort(key=lambda t: (-t[0], t[1]))     # deterministic tie-break
    A = [t[2] for t in scored[:N_TOP_FTILDE]]

    # (b) uniform random pool
    B = random_pool(n_feat, K, seed, N_RANDOM)

    src = {}
    for s in A:
        src.setdefault(s, 'ftilde_top')
    for s in B:
        src.setdefault(s, 'random')
    for s, tag in ((S_f, 'greedy_f'), (S_ft, 'greedy_ftilde')):
        src.setdefault(s, tag)

    opt_hat, arg = -1.0, None
    for s in src:
        v = Ftrue(s)
        if v > opt_hat:
            opt_hat, arg = v, s
    v_f, v_ft = Ftrue(S_f), Ftrue(S_ft)

    return dict(
        dataset=DATASET,
        seed=seed, K=K, opt_hat=opt_hat, f_greedy_f=v_f, f_greedy_ftilde=v_ft,
        table_ratio=v_ft / v_f,
        ratio_ftilde_over_opt_hat=v_ft / opt_hat,
        greedy_f_over_opt_hat=v_f / opt_hat,
        opt_hat_source=src[arg], opt_hat_set=sorted(arg),
        n_cand_total=len(src), n_cand_ftilde_top=len(A), n_cand_random=len(B),
        n_ftilde_scored=n_ftilde_scored,
        core=core, greedy_f=sorted(S_f), greedy_ftilde=sorted(S_ft),
        n_evals_f=Ftrue.evals, n_evals_ftilde=Ftil.evals,
        seconds=time.time() - t0)


def e1_ratio_at(K):
    ref = {}
    if not os.path.exists(E1_ROWS):
        return ref
    with open(E1_ROWS) as fh:
        for r in csv.DictReader(fh):
            if r['dataset'] == DATASET and int(r['K']) == K:
                ref[int(r['seed'])] = r['ratio']
    return ref


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--K', type=int, default=E1.KMAX,
                    help='budget; E1 table reports K=7')
    ap.add_argument('--seeds', type=int, default=10,
                    help='seeds 0..seeds-1 (E1 uses 0..29; 10 for time box)')
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--out', default=OUT_CSV)
    a = ap.parse_args()

    print(f'[G4.2] {DATASET} K={a.K} seeds=0..{a.seeds - 1}', flush=True)
    print(f'       full enumeration would be C(22,{a.K}) = '
          f'{math.comb(22, a.K)} subsets per seed: NOT run', flush=True)
    print(f'       candidate pool = top-{N_TOP_FTILDE} by ftilde over the '
          f'C({TOPM},{a.K})={math.comb(TOPM, a.K)} subsets of the surrogate '
          f'core, u {N_RANDOM} random subsets (MASTER_SEED={MASTER_SEED}), '
          f'u the 2 greedy sets', flush=True)

    t0 = time.time()
    jobs = [(s, a.K) for s in range(a.seeds)]
    if a.workers > 1:
        with Pool(a.workers) as pool:
            out = []
            for r in pool.imap_unordered(one_seed, jobs):
                out.append(r)
                print(f'  seed={r["seed"]} {r["seconds"]:.1f}s  '
                      f'opt_hat={r["opt_hat"]:.6f} ({r["opt_hat_source"]})  '
                      f'f(greedy^f)={r["f_greedy_f"]:.6f}  '
                      f'greedy_f/opt_hat={r["greedy_f_over_opt_hat"]:.4f}',
                      flush=True)
    else:
        out = [one_seed(j) for j in jobs]
    wall = time.time() - t0
    out.sort(key=lambda r: r['seed'])

    ref = e1_ratio_at(a.K)
    bad = []
    for r in out:
        if r['seed'] in ref and f'{r["table_ratio"]:.6f}' != ref[r['seed']]:
            bad.append((r['seed'], ref[r['seed']], f'{r["table_ratio"]:.6f}'))
    check = ('PASS (table_ratio identical to E1_rows.csv at K=%d for %d seeds)'
             % (a.K, len([r for r in out if r['seed'] in ref]))) if not bad \
        else 'FAIL ' + repr(bad)
    print(f'[G4.2] wall time {wall:.1f}s with {a.workers} workers', flush=True)
    print('[G4.2] E1 consistency:', check, flush=True)
    assert not bad, check

    with open(a.out, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in out:
            w.writerow({k: (f'{r[k]:.6f}' if isinstance(r[k], float) else r[k])
                        for k in FIELDS})
    print('wrote', a.out, flush=True)

    gf = np.array([r['greedy_f_over_opt_hat'] for r in out])
    gt = np.array([r['ratio_ftilde_over_opt_hat'] for r in out])
    tr = np.array([r['table_ratio'] for r in out])
    print()
    print(f'[G4.2] seeds 0..{a.seeds - 1}, K={a.K}')
    print(f'  f(greedy^f)/OPT_hat        median={np.median(gf):.4f} '
          f'min={gf.min():.4f} max={gf.max():.4f}')
    print(f'  f(greedy^ft)/OPT_hat       median={np.median(gt):.4f} '
          f'min={gt.min():.4f} max={gt.max():.4f}')
    print(f'  table ratio (E1 denominator) median={np.median(tr):.4f} '
          f'min={tr.min():.4f} max={tr.max():.4f}')
    print(f'  n seeds where OPT_hat > f(greedy^f): '
          f'{int((gf < 1 - 1e-12).sum())}/{len(gf)}')
    from collections import Counter
    print('  OPT_hat argmax source:',
          dict(Counter(r['opt_hat_source'] for r in out)))
    for r in out:
        print(f'  seed={r["seed"]} opt_hat_set={r["opt_hat_set"]} '
              f'greedy_f={r["greedy_f"]} core={r["core"]}')


if __name__ == '__main__':
    main()
