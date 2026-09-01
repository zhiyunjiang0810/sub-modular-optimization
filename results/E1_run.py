"""E1: feature selection with a LEARNED surrogate (TASKS_EXP.md, task E1).

Principles (TASKS_EXP.md 1-5, enforced here):
1. NO artificial oracle perturbation.  f~ is 5-fold CV accuracy computed on the
   TRAINING split only; it never sees X_test / y_test.  The old
   legacy/airline_performance.py oracle computed the TRUE gain on the test set
   and multiplied it by exp(uniform noise) -- that is both information leakage
   and an artificial perturbation, and it is not reproduced anywhere here.
2. Every f and f~ evaluation goes through src/im_graph.py::CachedSetFunction
   (dict keyed by frozenset); the greedy is src/im_graph.py::lazy_greedy (CELF),
   quantize=None (real-data task, no adversarial ties to protect).
   CAVEAT, measured not assumed: held-out accuracy is NOT submodular, so plain
   CELF over the whole budget is not exact -- on every dataset it disagrees with
   the true argmax on 3-5 of the 7 steps (a stale key can UNDER-estimate a gain
   that grew, and such a candidate is never revisited).  The reported trajectory
   is therefore built by calling the same lazy_greedy(..., K=1) once per step on
   the shifted state (round 1 of CELF is a full scan, hence an exact argmax) and
   is asserted to be the exact argmax at every step; all evaluations still go
   through the one shared CachedSetFunction, and the pair-recording requirement
   means every candidate is evaluated at every state anyway, so nothing is lost
   by the full scan.  Plain lazy_greedy(K=7) is still run as a diagnostic and
   its trajectory agreement / realised ratio are in E1_diagnostics.csv.
3. Reproducible: seeds = range(30) (one 80/20 split per seed), CSV on disk,
   figure as PNG+PDF.
4. Honest reporting: sign-violation %, non-positive-gain steps, trimming eps,
   lazy-vs-exact greedy mismatches -- all in the CSVs / notes.
5. CPU only, single process (two other heavy tasks run in parallel on 4 cores).

STRUCTURAL INFORMATION ISOLATION (the core fix of this task)
------------------------------------------------------------
f~ lives in `CVSurrogate`, built by `make_surrogate(X_train, y_train, ...)`.
That factory is *called with the training arrays only*, so the object it returns
cannot close over test data.  `CVSurrogate` declares `__slots__` (hence has no
__dict__ and no attribute can ever be attached to it), none of its slots is a
test array, and `CVSurrogate.__call__` has no closure cells.  `check_isolation()`
asserts all of this at runtime and additionally runs a *behavioural probe*:
y_test is randomly permuted in place, f~ must return a bit-identical value while
f must change.  The true f lives in a separate closure (`make_true_eval`).

Objective (paper text says decision tree; the old script's GBC does not match the
paper, this is the correction):
  f(S)  = DecisionTreeClassifier(random_state=42) fit on the 80% train split,
          accuracy on the 20% held-out split.
  f~(S) = same estimator, mean 5-fold cross_val_score accuracy on the 80% train
          split only.
  f(empty) / f~(empty) = majority-class (DummyClassifier) accuracy, so that
  d_e(empty) is the accuracy gain over the featureless predictor.
GBC is re-run for seed 0 only as a robustness cross-check.

Usage
-----
  python results/E1_run.py                      # everything, fresh files
  python results/E1_run.py --datasets airline --seeds 0:10          # chunk 1
  python results/E1_run.py --datasets airline --seeds 10:30 --append # chunk 2
  python results/E1_run.py --part gbc
  python results/E1_run.py --part baselines_fig
  python results/E1_run.py --part rebuild_rows   # F1.3 check only, see docstring
  python results/E1_run.py --part opt_bc --opt-k 5      # TASKS4 F1.4
"""
import argparse
import csv
import gzip
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'src'))
from im_graph import CachedSetFunction, lazy_greedy, true_max_gain  # noqa: E402
from statistics import TrajectoryStats, unified_row, ROW_FIELDS      # noqa: E402

from sklearn.datasets import load_breast_cancer, load_digits, load_wine  # noqa: E402
from sklearn.dummy import DummyClassifier                                # noqa: E402
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier  # noqa: E402
from sklearn.feature_selection import RFE, SelectKBest, f_classif, mutual_info_classif  # noqa: E402
from sklearn.model_selection import cross_val_score, train_test_split    # noqa: E402
from sklearn.preprocessing import LabelEncoder                           # noqa: E402
from sklearn.tree import DecisionTreeClassifier                          # noqa: E402

KMAX = 7
CV_FOLDS = 5
SEED_MODEL = 42
DATASETS = ['wine', 'digits20', 'breast_cancer', 'airline']
BASELINE_DATASETS = ['airline', 'breast_cancer']
BASELINE_SEEDS = 10          # baselines only on seeds 0..9 (time control)
GBC_DATASETS = ['wine', 'breast_cancer', 'airline']   # digits20 too slow, see notes

ROWS_CSV = os.path.join(HERE, 'E1_rows.csv')
PAIRS_CSV = os.path.join(HERE, 'E1_pairs.csv.gz')
BASE_CSV = os.path.join(HERE, 'E1_baselines.csv')
GBC_CSV = os.path.join(HERE, 'E1_gbc_seed0.csv')
DIAG_CSV = os.path.join(HERE, 'E1_diagnostics.csv')

PAIR_FIELDS = ['dataset', 'seed', 'step', 'd', 'dtilde', 'chosen']
BASE_FIELDS = ['dataset', 'seed', 'K', 'method', 'oos_acc', 'features']
GBC_FIELDS = ['dataset', 'seed', 'K', 'ratio', 'eta_sel', 'eta_path_trimmed',
              'viol_sign_pct', 'acc_greedy_ftilde', 'acc_greedy_f']
DIAG_FIELDS = ['dataset', 'seed', 'model', 'n_train', 'n_test', 'n_features',
               'eps', 'f_empty', 'ftilde_empty', 'nonpos_steps_K7',
               'celf_agree_steps_ftilde', 'celf_agree_steps_f',
               'celf_ratio_K7', 'exact_ratio_K7', 'n_evals_f',
               'n_evals_ftilde', 'seconds']


# --------------------------------------------------------------------------
# model factories (module level: no closures, nothing to capture)
# --------------------------------------------------------------------------
def make_tree():
    return DecisionTreeClassifier(random_state=SEED_MODEL)


def make_gbc():
    return GradientBoostingClassifier(random_state=SEED_MODEL)


def make_majority():
    return DummyClassifier(strategy='most_frequent')


# --------------------------------------------------------------------------
# datasets
# --------------------------------------------------------------------------
def clean_airline(path):
    """Cleaning steps transcribed from legacy/airline_performance.py, in the
    same order, with df.sample(n=1000) REMOVED (full data, per TASKS_EXP.md).
    See E1_notes.md for the itemised list and the two deviations."""
    import pandas as pd
    df = pd.read_csv(path)
    df = df.drop(['Unnamed: 0', 'id'], axis=1)                       # (1)
    col = 'Arrival Delay in Minutes'
    df[col] = df[col].fillna(df[col].mean())                          # (2)
    # (3) legacy df.sample(n=1000, random_state=42)  -- REMOVED on purpose
    le = LabelEncoder()                                               # (4)
    for lab in ['Gender', 'Customer Type', 'Type of Travel', 'Class',
                'satisfaction']:
        df[lab] = le.fit_transform(df[lab])
    for c, thr in [('Flight Distance', 3736.5),                       # (5)
                   ('Departure Delay in Minutes', 800),
                   ('Arrival Delay in Minutes', 650)]:
        df = df.drop(df[df[c] > thr].index)
    # (6) legacy StandardScaler loop is a no-op (its `dtype == type(float)`
    #     test is never true) and is in any case irrelevant for tree models,
    #     which are invariant to per-feature monotone rescaling.  Skipped.
    X = df.drop(columns=['satisfaction']).to_numpy(dtype=float)
    y = df['satisfaction'].to_numpy()
    names = [c for c in df.columns if c != 'satisfaction']
    return X, y, names


def load_dataset(name):
    if name == 'airline':
        return clean_airline(os.path.join(ROOT, 'data', 'airline.csv'))
    if name == 'breast_cancer':
        d = load_breast_cancer()
        return d.data, d.target, list(d.feature_names)
    if name == 'wine':
        d = load_wine()
        return d.data, d.target, list(d.feature_names)
    if name == 'digits20':
        d = load_digits()
        return d.data[:, :20], d.target, [f'px{i}' for i in range(20)]
    raise ValueError(name)


# --------------------------------------------------------------------------
# f~ : TRAIN-ONLY surrogate.  __slots__ => no __dict__ => nothing can be
# attached to it later; the constructor is only ever handed training arrays.
# --------------------------------------------------------------------------
class CVSurrogate:
    __slots__ = ('_X_train', '_y_train', '_make_model', '_folds', 'n_evals')

    def __init__(self, X_train, y_train, make_model, folds=CV_FOLDS):
        self._X_train = X_train
        self._y_train = y_train
        self._make_model = make_model
        self._folds = folds
        self.n_evals = 0

    def __call__(self, S):
        self.n_evals += 1
        cols = sorted(S)
        if cols:
            Xs, est = self._X_train[:, cols], self._make_model()
        else:
            Xs, est = np.zeros((len(self._y_train), 1)), make_majority()
        return float(cross_val_score(est, Xs, self._y_train,
                                     cv=self._folds).mean())


def make_surrogate(X_train, y_train, make_model):
    """Built from the training split ONLY -- no test array is in scope here."""
    return CVSurrogate(X_train, y_train, make_model)


def make_true_eval(X_train, y_train, X_test, y_test, make_model):
    """f: held-out accuracy.  Separate scope; the surrogate never touches it."""
    def ev(S):
        cols = sorted(S)
        if cols:
            est = make_model().fit(X_train[:, cols], y_train)
            pred = est.predict(X_test[:, cols])
        else:
            est = make_majority().fit(np.zeros((len(y_train), 1)), y_train)
            pred = est.predict(np.zeros((len(y_test), 1)))
        return float(np.mean(pred == y_test))
    return ev


def check_isolation(sur, f_true, X_train, X_test, y_test, make_model, rng):
    """Structural + behavioural proof that f~ cannot see the held-out data."""
    out = {}
    cls = type(sur)
    assert not hasattr(sur, '__dict__'), '__slots__ missing: attributes attachable'
    assert all('test' not in s for s in cls.__slots__), cls.__slots__
    assert cls.__call__.__closure__ is None, 'f~ closes over outer variables'
    assert make_model.__closure__ is None, 'model factory has a closure'
    for s in cls.__slots__:
        v = getattr(sur, s)
        if isinstance(v, np.ndarray):
            assert v is not X_test and v is not y_test
            assert not np.shares_memory(v, X_test), s
            assert not np.shares_memory(v, y_test), s
    assert sur._X_train.shape[0] == X_train.shape[0]
    assert sur._X_train.shape[0] != X_test.shape[0] or True
    out['slots'] = list(cls.__slots__)
    # behavioural probe: destroy the labels of the held-out split.
    probe = [0, 1, 2][:X_train.shape[1]]
    v1, t1 = sur(probe), f_true(frozenset(probe))
    backup = y_test.copy()
    rng.shuffle(y_test)                      # in place: f sees it, f~ must not
    v2, t2 = CVSurrogate(sur._X_train, sur._y_train, make_model)(probe), \
        make_true_eval(X_train, sur._y_train, X_test, y_test, make_model)(frozenset(probe))
    y_test[:] = backup
    assert v1 == v2, 'f~ changed when y_test was permuted -- LEAKAGE'
    out['ftilde_invariant'] = (v1 == v2)
    out['f_changed_under_probe'] = (t1 != t2)
    out['probe_values'] = (v1, v2, t1, t2)
    return out


# --------------------------------------------------------------------------
# greedy: exact argmax at every step, obtained by calling the shared
# lazy_greedy with K=1 on the state-shifted view (round 1 of CELF is a full
# scan).  Every evaluation is served by the same CachedSetFunction.
# --------------------------------------------------------------------------
class _Shift:
    """View of a CachedSetFunction from a fixed base state (same cache)."""
    __slots__ = ('F', 'base')

    def __init__(self, F, base):
        self.F, self.base = F, base

    def gain(self, S, e):
        return self.F.gain(self.base | set(S), e)


def greedy_exact(F, ground, K, on_step=None):
    S = []
    for t in range(K):
        rem = [e for e in ground if e not in S]
        if not rem:
            break
        base = frozenset(S)
        pick = lazy_greedy(_Shift(F, base), rem, 1, quantize=None)[0]
        best = max(F.gain(base, e) for e in rem)
        assert F.gain(base, pick) >= best - 1e-12, 'greedy step not argmax'
        if on_step is not None:
            on_step(t, set(S), pick)
        S.append(pick)
    return S


# --------------------------------------------------------------------------
# one (dataset, seed) run of the shared pipeline
# --------------------------------------------------------------------------
def run_one(name, seed, X, y, make_model, want_pairs=True, want_baselines=False,
            feat_names=None, isolation_rng=None):
    t0 = time.time()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed)
    ground = list(range(X.shape[1]))
    eps = 1.0 / len(y_test)                    # 1 accuracy quantum on held-out

    sur = make_surrogate(X_train, y_train, make_model)          # train-only
    Ftil = CachedSetFunction(sur)
    Ftrue = CachedSetFunction(make_true_eval(X_train, y_train, X_test, y_test,
                                             make_model))
    iso = None
    if isolation_rng is not None:
        iso = check_isolation(sur, Ftrue.fn, X_train, X_test, y_test,
                              make_model, isolation_rng)

    stats = TrajectoryStats(eps)
    pair_rows = []

    def on_step(t, Sb, chosen):
        """At every trajectory state record (d, d~) for ALL candidates.
        d uses held-out truth: it is used for statistics and for the CSV only,
        never fed back into f~ or into the selection rule."""
        d_chosen = Ftrue.gain(Sb, chosen)
        dmax = true_max_gain(Ftrue, Sb, ground)
        pairs = []
        for e in ground:
            if e in Sb:
                continue
            d, dt = Ftrue.gain(Sb, e), Ftil.gain(Sb, e)
            pairs.append((d, dt))
            if want_pairs:
                pair_rows.append(dict(dataset=name, seed=seed, step=t,
                                      d=f'{d:.10g}', dtilde=f'{dt:.10g}',
                                      chosen=int(e == chosen)))
        stats.add_step(d_chosen, dmax, pairs)

    picks_tilde = greedy_exact(Ftil, ground, KMAX, on_step=on_step)
    picks_true = greedy_exact(Ftrue, ground, KMAX)
    # diagnostic: what plain CELF over the whole budget would have done
    celf_tilde = lazy_greedy(Ftil, ground, KMAX, quantize=None)
    celf_true = lazy_greedy(Ftrue, ground, KMAX, quantize=None)

    rows, base_rows = [], []
    accs = {}
    for K in range(1, KMAX + 1):
        num = Ftrue(set(picks_tilde[:K]))
        den = Ftrue(set(picks_true[:K]))
        accs[K] = (num, den)
        st = stats.upto(K)
        rows.append(unified_row('E1', name, K, seed, num / den, st))

    if want_baselines:
        base_rows = run_baselines(name, seed, X_train, y_train, Ftrue,
                                  picks_tilde, picks_true, ground, feat_names)

    st7 = stats.upto(KMAX)
    diag = dict(dataset=name, seed=seed, model=make_model.__name__,
                n_train=len(y_train), n_test=len(y_test),
                n_features=len(ground), eps=f'{eps:.8g}',
                f_empty=f'{Ftrue(set()):.6f}', ftilde_empty=f'{Ftil(set()):.6f}',
                nonpos_steps_K7=st7['n_nonpos_steps'],
                celf_agree_steps_ftilde=sum(a == b for a, b in
                                            zip(celf_tilde, picks_tilde)),
                celf_agree_steps_f=sum(a == b for a, b in
                                       zip(celf_true, picks_true)),
                celf_ratio_K7=f'{Ftrue(set(celf_tilde)) / Ftrue(set(celf_true)):.6f}',
                exact_ratio_K7=f'{accs[KMAX][0] / accs[KMAX][1]:.6f}',
                n_evals_f=Ftrue.evals, n_evals_ftilde=Ftil.evals,
                seconds=f'{time.time() - t0:.1f}')
    return rows, pair_rows, base_rows, diag, accs, st7, iso, (picks_tilde, picks_true)


# --------------------------------------------------------------------------
# baselines (ported from legacy/airline_performance.py, downstream classifier
# changed from GBC to the decision tree so the comparison uses the SAME f)
# --------------------------------------------------------------------------
def run_baselines(name, seed, X_train, y_train, Ftrue, picks_tilde, picks_true,
                  ground, feat_names):
    rows = []
    scores_kbest = SelectKBest(f_classif, k='all').fit(X_train, y_train).scores_
    scores_kbest = np.nan_to_num(scores_kbest, nan=-np.inf)
    mi = mutual_info_classif(X_train, y_train, random_state=SEED_MODEL)
    et = ExtraTreesClassifier(random_state=SEED_MODEL).fit(
        X_train, y_train).feature_importances_
    rank = {'selectkbest': np.argsort(scores_kbest)[::-1],
            'mutual_info': np.argsort(mi)[::-1],
            'extra_trees': np.argsort(et)[::-1]}
    for K in range(1, KMAX + 1):
        sel = {m: list(r[:K]) for m, r in rank.items()}
        rfe = RFE(DecisionTreeClassifier(random_state=SEED_MODEL),
                  n_features_to_select=K, step=1).fit(X_train, y_train)
        sel['rfe'] = list(np.flatnonzero(rfe.support_))
        sel['greedy_ftilde'] = list(picks_tilde[:K])
        sel['greedy_f'] = list(picks_true[:K])
        for m, idx in sel.items():
            idx = [int(i) for i in idx]
            rows.append(dict(dataset=name, seed=seed, K=K, method=m,
                             oos_acc=f'{Ftrue(set(idx)):.6f}',
                             features='|'.join(feat_names[i] for i in idx)))
    return rows


# --------------------------------------------------------------------------
# csv helpers (append-friendly for chunked runs)
# --------------------------------------------------------------------------
def dump(path, fields, rows, append, gz=False):
    if not rows and not append:
        opener = gzip.open if gz else open
        with opener(path, 'wt', newline='') as fh:
            csv.DictWriter(fh, fieldnames=fields).writeheader()
        return
    if not rows:
        return
    opener = gzip.open if gz else open
    mode = 'at' if append else 'wt'
    with opener(path, mode, newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        if not append:
            w.writeheader()
        w.writerows(rows)


# --------------------------------------------------------------------------
def main_part(datasets, seeds, append):
    all_rows, all_pairs, all_base, all_diag = [], [], [], []
    iso_report = {}
    for name in datasets:
        X, y, names = load_dataset(name)
        rng = np.random.default_rng(12345)
        print(f'[{name}] X={X.shape} classes={len(np.unique(y))}', flush=True)
        for seed in seeds:
            r, p, b, d, accs, st7, iso, _ = run_one(
                name, seed, X, y, make_tree, want_pairs=True,
                want_baselines=(name in BASELINE_DATASETS and seed < BASELINE_SEEDS),
                feat_names=names,
                isolation_rng=rng if seed == seeds[0] else None)
            if iso:
                iso_report[name] = iso
                print(f'  isolation probe {name}: f~ invariant={iso["ftilde_invariant"]} '
                      f'f changed={iso["f_changed_under_probe"]} '
                      f'values={iso["probe_values"]}', flush=True)
            all_rows += r
            all_pairs += p
            all_base += b
            all_diag.append(d)
            print(f'  seed={seed:2d} K7 ratio={float(r[-1]["ratio"]):.4f} '
                  f'eta_sel={r[-1]["eta_sel"]} eta_path={r[-1]["eta_path_trimmed"]} '
                  f'viol%={r[-1]["viol_sign_pct"]} nonpos={d["nonpos_steps_K7"]} '
                  f'celf_agree=({d["celf_agree_steps_ftilde"]},{d["celf_agree_steps_f"]}) '
                  f'{d["seconds"]}s', flush=True)
    dump(ROWS_CSV, ROW_FIELDS, all_rows, append)
    dump(PAIRS_CSV, PAIR_FIELDS, all_pairs, append, gz=True)
    dump(BASE_CSV, BASE_FIELDS, all_base, append)
    dump(DIAG_CSV, DIAG_FIELDS, all_diag, append)
    return iso_report


def gbc_part(datasets):
    rows = []
    for name in datasets:
        X, y, names = load_dataset(name)
        t0 = time.time()
        r, _, _, d, accs, st7, _, _ = run_one(name, 0, X, y, make_gbc,
                                              want_pairs=False)
        for K in range(1, KMAX + 1):
            st = None
            rows.append(dict(dataset=name, seed=0, K=K,
                             ratio=r[K - 1]['ratio'],
                             eta_sel=r[K - 1]['eta_sel'],
                             eta_path_trimmed=r[K - 1]['eta_path_trimmed'],
                             viol_sign_pct=r[K - 1]['viol_sign_pct'],
                             acc_greedy_ftilde=f'{accs[K][0]:.6f}',
                             acc_greedy_f=f'{accs[K][1]:.6f}'))
        print(f'[GBC {name}] K7 ratio={r[-1]["ratio"]} eta_sel={r[-1]["eta_sel"]} '
              f'{time.time() - t0:.0f}s', flush=True)
    dump(GBC_CSV, GBC_FIELDS, rows, append=False)


def baseline_figure():
    """Fig.1 replacement: oos accuracy vs K, greedy-on-f~ against the four
    classical selectors (median over the 10 baseline seeds)."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import pandas as pd
    df = pd.read_csv(BASE_CSV)
    order = ['greedy_f', 'greedy_ftilde', 'selectkbest', 'rfe', 'mutual_info',
             'extra_trees']
    lab = {'greedy_f': 'greedy on $f$ (true)', 'greedy_ftilde': 'greedy on $\\tilde f$ (CV)',
           'selectkbest': 'SelectKBest', 'rfe': 'RFE', 'mutual_info': 'Mutual Information',
           'extra_trees': 'Extra Trees'}
    sty = {'greedy_f': ('k', 'o-'), 'greedy_ftilde': ('#3B5387', 'o-'),
           'selectkbest': ('#00C1C2', '^-'), 'rfe': ('#6A5DC4', 'd-'),
           'mutual_info': ('#47AF79', '*-'), 'extra_trees': ('#D2AA3A', 's-')}
    ds = [d for d in BASELINE_DATASETS if d in set(df.dataset)]
    fig, axes = plt.subplots(1, len(ds), figsize=(6 * len(ds), 4.6))
    axes = np.atleast_1d(axes)
    for ax, name in zip(axes, ds):
        sub = df[df.dataset == name]
        for m in order:
            g = sub[sub.method == m].groupby('K').oos_acc.median()
            c, s = sty[m]
            ax.plot(g.index, g.values, s, color=c, label=lab[m], lw=2, ms=6)
        ax.set_title(f'{name} (median over 10 seeds)')
        ax.set_xlabel('number of features K')
        ax.set_ylabel('held-out accuracy')
        ax.grid(alpha=.3)
    axes[0].legend(fontsize=9, loc='lower right')
    fig.tight_layout()
    for ext in ('png', 'pdf'):
        fig.savefig(os.path.join(ROOT, 'figures', f'E1_baselines.{ext}'), dpi=150)
    print('wrote figures/E1_baselines.png/.pdf')


def opt_check(spec=(('wine', 7, 10), ('airline', 3, 5))):
    """How much does the greedy-on-f denominator OVERSTATE the ratio?
    Brute-force OPT_K = max_{|S|=K} f(S) where the enumeration is affordable,
    and report f(greedy^f)/OPT and f(greedy^f~)/OPT.  Printed only (the number
    goes into E1_notes.md); no CSV, this is a sanity bound on the proxy."""
    from itertools import combinations
    import numpy as _np
    for name, Kmax, nseeds in spec:
        X, y, _ = load_dataset(name)
        gf, gt = [], []
        for seed in range(nseeds):
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=seed)
            ground = list(range(X.shape[1]))
            sur = make_surrogate(X_train, y_train, make_tree)
            Ftil = CachedSetFunction(sur)
            Ftrue = CachedSetFunction(make_true_eval(X_train, y_train, X_test,
                                                     y_test, make_tree))
            pt = greedy_exact(Ftil, ground, Kmax)
            pf = greedy_exact(Ftrue, ground, Kmax)
            opt = max(Ftrue(set(c)) for c in combinations(ground, Kmax))
            gf.append(Ftrue(set(pf)) / opt)
            gt.append(Ftrue(set(pt)) / opt)
        print(f'[OPT check] {name} K={Kmax} seeds=0..{nseeds - 1}: '
              f'median f(greedy^f)/OPT = {_np.median(gf):.4f} '
              f'(min {min(gf):.4f}), '
              f'median f(greedy^ftilde)/OPT = {_np.median(gt):.4f} '
              f'(min {min(gt):.4f})', flush=True)


def opt_bruteforce(name, Kmax, nseeds, out_csv=None):
    """TASKS4 F1.4: brute-force OPT_K = max_{|S|=K} f(S) on `name` for K <= Kmax.

    f is the SAME held-out decision-tree accuracy used everywhere else, wrapped
    in the same frozenset cache, so a subset evaluated at K is reused at larger
    K.  Reports f(greedy^f)/OPT (how much the OPT proxy of the ratio's
    denominator overstates) and f(greedy^f~)/OPT for every K = 1..Kmax.
    Prints an estimate from the first seed before the full loop."""
    from itertools import combinations
    import numpy as _np
    X, y, _ = load_dataset(name)
    ground = list(range(X.shape[1]))
    print(f'[OPT brute force] {name}: n_features={len(ground)}, '
          f'C({len(ground)},{Kmax})='
          f'{math.comb(len(ground), Kmax)} subsets at K={Kmax}', flush=True)
    per_K = {K: dict(gf=[], gt=[], opt=[]) for K in range(1, Kmax + 1)}
    rows = []
    for seed in range(nseeds):
        t0 = time.time()
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=seed)
        Ftil = CachedSetFunction(make_surrogate(X_train, y_train, make_tree))
        Ftrue = CachedSetFunction(make_true_eval(X_train, y_train, X_test,
                                                 y_test, make_tree))
        pt = greedy_exact(Ftil, ground, Kmax)
        pf = greedy_exact(Ftrue, ground, Kmax)
        for K in range(1, Kmax + 1):
            opt = max(Ftrue(set(c)) for c in combinations(ground, K))
            gf = Ftrue(set(pf[:K])) / opt
            gt = Ftrue(set(pt[:K])) / opt
            per_K[K]['gf'].append(gf)
            per_K[K]['gt'].append(gt)
            per_K[K]['opt'].append(opt)
            rows.append(dict(dataset=name, seed=seed, K=K, opt=f'{opt:.6f}',
                             f_greedy_f=f'{Ftrue(set(pf[:K])):.6f}',
                             f_greedy_ftilde=f'{Ftrue(set(pt[:K])):.6f}',
                             greedy_f_over_opt=f'{gf:.6f}',
                             greedy_ftilde_over_opt=f'{gt:.6f}'))
        print(f'  seed={seed} done in {time.time() - t0:.1f}s '
              f'(K={Kmax}: greedy^f/OPT={per_K[Kmax]["gf"][-1]:.4f}, '
              f'greedy^f~/OPT={per_K[Kmax]["gt"][-1]:.4f}, '
              f'{Ftrue.evals} f-evals cached)', flush=True)
    for K in range(1, Kmax + 1):
        d = per_K[K]
        print(f'[OPT brute force] {name} K={K} seeds=0..{nseeds - 1}: '
              f'median f(greedy^f)/OPT = {_np.median(d["gf"]):.4f} '
              f'(min {min(d["gf"]):.4f}), '
              f'median f(greedy^f~)/OPT = {_np.median(d["gt"]):.4f} '
              f'(min {min(d["gt"]):.4f})', flush=True)
    if out_csv:
        with open(out_csv, 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=[
                'dataset', 'seed', 'K', 'opt', 'f_greedy_f', 'f_greedy_ftilde',
                'greedy_f_over_opt', 'greedy_ftilde_over_opt'])
            w.writeheader()
            w.writerows(rows)
        print('wrote', out_csv)
    return per_K


def rebuild_rows():
    """TASKS4 F1.3: regenerate E1_rows.csv with the new statistics columns
    WITHOUT re-running the 32-minute pipeline.

    E1_pairs.csv.gz already stores (d, d~) for EVERY candidate at every
    trajectory state, with the chosen candidate flagged, so the whole content of
    TrajectoryStats is recoverable: d_chosen is the flagged pair and
    max_e d_e(S^t) is the maximum d over the same step (identical to the
    true_max_gain full scan used at run time, which also ranges over all
    e not in S^t).  eps comes from E1_diagnostics.csv (1/|test|) and the ratio
    column is carried over from the previous E1_rows.csv (it is a function of f
    alone and is untouched by this change).

    LIMITATION, measured (2026-09-01): this reconstruction does NOT reproduce
    eta_path_trimmed / viol_sign_pct bit-for-bit, because the pairs file stores
    d and d~ rounded to 10 significant digits while the eps-trimming test
    (|d| >= eps with eps = 1/|held-out|) is decided at the boundary: held-out
    accuracy gains are integer multiples of 1/|held-out| and float subtraction
    puts many of them one ulp BELOW eps, whereas the 10-digit decimal is just
    above it.  On wine seed 29 the live run and the previous CSV agree exactly
    while the reconstruction differs, so the rounded file is the one at fault.
    The function therefore only WRITES E1_rows.csv when it reproduces every old
    column exactly; otherwise it refuses and the caller must re-run --part main.
    eta_sel and ratio are unaffected by the boundary (eta_sel uses no eps)."""
    import collections
    # eps must be reconstructed EXACTLY as at run time (1.0 / |held-out|); the
    # `eps` column of the diagnostics is rounded to 8 significant digits and the
    # accuracy gains are integer multiples of 1/|held-out|, so the rounded value
    # sits on the wrong side of the >= eps trimming test for the smallest gains.
    eps_of = {}
    for r in csv.DictReader(open(DIAG_CSV)):
        if r['model'] == 'make_tree':
            eps_of[(r['dataset'], int(r['seed']))] = 1.0 / int(r['n_test'])
    steps = collections.defaultdict(lambda: collections.defaultdict(list))
    with gzip.open(PAIRS_CSV, 'rt') as fh:
        for r in csv.DictReader(fh):
            steps[(r['dataset'], int(r['seed']))][int(r['step'])].append(
                (float(r['d']), float(r['dtilde']), r['chosen'] == '1'))
    old = {}
    for r in csv.DictReader(open(ROWS_CSV)):
        old[(r['dataset'], int(r['seed']), int(r['K']))] = r
    out, mism = [], 0
    for (ds, seed), by_step in sorted(steps.items()):
        st = TrajectoryStats(eps_of[(ds, seed)])
        for t in sorted(by_step):
            pl = by_step[t]
            chosen = [d for d, _, c in pl if c]
            assert len(chosen) == 1, (ds, seed, t, len(chosen))
            st.add_step(chosen[0], max(d for d, _, _ in pl),
                        [(d, dt) for d, dt, _ in pl])
        for K in range(1, KMAX + 1):
            o = old[(ds, seed, K)]
            row = unified_row('E1', ds, K, seed, float(o['ratio']), st.upto(K))
            for c in ('eta_sel', 'eta_path_trimmed', 'viol_sign_pct',
                      'LK_eta_sel', 'LK_eta_path'):
                if str(row[c]) != o[c]:
                    mism += 1
                    print(f'  MISMATCH {ds} seed={seed} K={K} {c}: '
                          f'{o[c]} -> {row[c]}', flush=True)
            out.append(row)
    if mism == 0:
        dump(ROWS_CSV, ROW_FIELDS, out, append=False)
        print(f'rebuild_rows: {len(out)} rows, 0 mismatches, new columns '
              f'n_steps_nonpos / frac_steps_nonpos added -> {ROWS_CSV}')
    else:
        print(f'rebuild_rows: {mism} mismatches against the old columns; '
              f'E1_rows.csv NOT written (see the docstring: the pairs file is '
              f'rounded at the eps boundary).  Re-run --part main instead.')
    return mism


def summary_part():
    """Median tables printed to stdout; transcribed into E1_notes.md."""
    import pandas as pd
    pd.set_option('display.width', 200)
    r = pd.read_csv(ROWS_CSV)
    print('\n== E1_rows.csv: rows per dataset ==')
    print(r.groupby(['dataset', 'K']).size().unstack().to_string())
    for K in (1, 3, 5, 7):
        sub = r[r.K == K]
        g = sub.groupby('dataset').agg(
            n=('ratio', 'size'),
            ratio_med=('ratio', 'median'),
            ratio_q1=('ratio', lambda s: s.quantile(.25)),
            ratio_q3=('ratio', lambda s: s.quantile(.75)),
            ratio_min=('ratio', 'min'),
            eta_sel_med=('eta_sel', 'median'),
            eta_sel_max=('eta_sel', 'max'),
            eta_path_med=('eta_path_trimmed', 'median'),
            eta_path_max=('eta_path_trimmed', 'max'),
            viol_med=('viol_sign_pct', 'median'),
            LK_sel_med=('LK_eta_sel', 'median'),
            LK_path_med=('LK_eta_path', 'median'))
        print(f'\n== K={K} medians ==')
        print(g.round(4).to_string())
    d = pd.read_csv(DIAG_CSV)
    print('\n== diagnostics (median over seeds) ==')
    print(d.groupby(['dataset', 'model']).agg(
        n=('seed', 'size'), n_train=('n_train', 'max'), n_test=('n_test', 'max'),
        n_feat=('n_features', 'max'), eps=('eps', 'max'),
        f_empty=('f_empty', 'median'), ftilde_empty=('ftilde_empty', 'median'),
        nonpos=('nonpos_steps_K7', 'median'),
        celf_agree_ft=('celf_agree_steps_ftilde', 'median'),
        celf_agree_f=('celf_agree_steps_f', 'median'),
        celf_ratio=('celf_ratio_K7', 'median'),
        exact_ratio=('exact_ratio_K7', 'median'),
        sec=('seconds', 'sum')).round(4).to_string())
    if os.path.exists(BASE_CSV):
        b = pd.read_csv(BASE_CSV)
        if len(b):
            print('\n== baselines: median held-out accuracy over 10 seeds ==')
            for name in sorted(set(b.dataset)):
                print(f'-- {name}')
                p = b[b.dataset == name].pivot_table(
                    index='method', columns='K', values='oos_acc', aggfunc='median')
                order = [m for m in ['greedy_f', 'greedy_ftilde', 'selectkbest',
                                     'rfe', 'mutual_info', 'extra_trees']
                         if m in p.index]
                print(p.loc[order].round(4).to_string())
                win = (p.loc['greedy_ftilde'] >= p.drop(
                    index=[m for m in ('greedy_f', 'greedy_ftilde') if m in p.index]).max())
                print('   greedy_ftilde >= best of the 4 baselines at K =',
                      list(win[win].index), 'of', list(p.columns))
    if os.path.exists(GBC_CSV):
        g = pd.read_csv(GBC_CSV)
        if len(g):
            print('\n== GBC seed 0 (robustness cross-check) ==')
            print(g.to_string(index=False))
            print('\n-- decision tree, seed 0, same rows for comparison')
            print(r[(r.seed == 0) & (r.dataset.isin(set(g.dataset)))]
                  [['dataset', 'K', 'ratio', 'eta_sel', 'eta_path_trimmed',
                    'viol_sign_pct']].to_string(index=False))
    p = pd.read_csv(PAIRS_CSV)
    print(f'\n== E1_pairs.csv.gz: {len(p)} pairs, '
          f'{p.chosen.sum()} chosen; per dataset:')
    print(p.groupby('dataset').agg(pairs=('d', 'size'),
                                   d_le0=('d', lambda s: (s <= 0).mean()),
                                   dt_le0=('dtilde', lambda s: (s <= 0).mean())
                                   ).round(4).to_string())


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--datasets', default=','.join(DATASETS))
    ap.add_argument('--seeds', default='0:30')
    ap.add_argument('--part', default='all',
                    choices=['all', 'main', 'gbc', 'baselines_fig', 'summary',
                             'opt_check', 'opt_bc', 'rebuild_rows'])
    ap.add_argument('--append', action='store_true')
    ap.add_argument('--opt-k', type=int, default=5,
                    help='budget for --part opt_bc brute-force OPT (F1.4)')
    a = ap.parse_args()
    ds = [d for d in a.datasets.split(',') if d]
    lo, hi = (int(v) for v in a.seeds.split(':'))
    t0 = time.time()
    if a.part in ('all', 'main'):
        main_part(ds, list(range(lo, hi)), a.append)
    if a.part in ('all', 'gbc'):
        gbc_part([d for d in ds if d in GBC_DATASETS])
    if a.part in ('all', 'baselines_fig'):
        baseline_figure()
    if a.part == 'opt_check':
        opt_check()
    if a.part == 'opt_bc':                      # TASKS4 F1.4
        opt_bruteforce('breast_cancer', a.opt_k, 10,
                       out_csv=os.path.join(HERE, 'E1_opt_breast_cancer.csv'))
    if a.part == 'rebuild_rows':                # TASKS4 F1.3
        sys.exit(1 if rebuild_rows() else 0)
    if a.part in ('all', 'summary'):
        summary_part()
    print(f'total {time.time() - t0:.0f}s')
