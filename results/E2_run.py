"""E2: Influence maximization with a PARTIALLY OBSERVED graph as surrogate.

Principles (TASKS_EXP.md, header-mandated):
1. NO artificial oracle perturbation.  f~ here is the one-hop coverage computed on
   an edge-subsampled ("crawled") copy of the graph: it is computable from
   observable data alone and never looks at f.
2. Every f evaluation is cached (src.im_graph.CachedSetFunction, key=frozenset);
   greedy is lazy/CELF (src.im_graph.lazy_greedy, quantize=None on real data).
3. Reproducible: observed-graph seeds 0..19 fixed, results to CSV, figures PNG+PDF.
4. Honest reporting: sign-violation %, zero-gain steps, trimming eps and any
   node truncation are all written to E2_notes.md.  Since TASKS4 F1.2 there is
   NO candidate truncation in any statistic: eta^path and the sign-violation %
   are computed over every remaining candidate at every trajectory state.  The
   top-50 restriction that produced the earlier (underestimated) eta^path
   numbers survives only as the sampling rule of E2_pairs_sample.csv.gz.
5. CPU only, single process; long runs are chunked by (dataset, p) and appended
   incrementally so a timeout never loses finished work.

Setting
-------
f(S)  = |{v : v in S or v is pointed to by some s in S}| on the TRUE graph.
f~(S) = same formula on an OBSERVED graph, where each input edge is kept
        independently with probability p (undirected edges kept/dropped whole;
        Graph.edge_subsample).  p in {0.3, 0.5, 0.8}, 20 observed graphs each.
K     = 1..30 (one K=30 trajectory contains every prefix).
ratio = f(greedy_f~ prefix K) / f(greedy_f prefix K); the true-value greedy is an
        OPT proxy, so the denominator OVERSTATES what an optimum would give and
        the reported ratio is an upper estimate of the competitive ratio.
eta^sel needs max_e d_e(S^t) on the TRUE graph at every trajectory state.  A full
        scan per step is O(m) and too slow, so a second CELF-style lazy max-heap
        is kept on the true graph (gains of a monotone submodular coverage
        function are non-increasing along the monotonically growing trajectory,
        so stale heap values are valid upper bounds).  --mode validate checks
        this heap against the plain full scan (im_graph.true_max_gain).
eta^path uses eps = 1 (the quantisation unit of a coverage count).

Usage
-----
  python3 results/E2_run.py --mode validate
  python3 results/E2_run.py --mode probe --dataset facebook_artist --p 0.5 --seeds 0
  python3 results/E2_run.py --mode run --dataset email_eu_core --p all --seeds 0-19
  python3 results/E2_run.py --mode aggregate      # E2_p_eta.csv
  python3 results/E2_run.py --mode figures        # figures/E2_p_eta.{png,pdf}
Outputs are appended, and (dataset, p, seed) triples already present in
results/E2_rows.csv are skipped, so the script is restartable.
"""
import argparse
import csv
import gzip
import heapq
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'src'))
from im_graph import Graph, CachedSetFunction, lazy_greedy, true_max_gain  # noqa: E402
from statistics import TrajectoryStats, unified_row, ROW_FIELDS, L_K  # noqa: E402

EPS = 1.0                 # eta^path trimming: 1 coverage count
K_MAX = 30
P_LIST = [0.3, 0.5, 0.8]
TOP_M = 50                # (d, d~) pairs SAMPLED to the pairs file per step
                          # (statistics always use every candidate: TASKS4 F1.2)
N_RANDOM = 10             # random-baseline repetitions
PAIRS_FULL_SEEDS = 3      # email: dump ALL candidate pairs only for seeds < 3

ROWS_CSV = os.path.join(HERE, 'E2_rows.csv')
PAIRS_GZ = os.path.join(HERE, 'E2_pairs_sample.csv.gz')
BASE_CSV = os.path.join(HERE, 'E2_baselines.csv')
PETA_CSV = os.path.join(HERE, 'E2_p_eta.csv')

ROW_FIELDS_E2 = list(ROW_FIELDS) + ['p']      # unified format + p (E2-specific)
PAIR_FIELDS = ['dataset', 'p', 'seed', 'step', 'element', 'd', 'd_tilde']
BASE_FIELDS = ['dataset', 'method', 'p', 'seed', 'K', 'f_value']

DATASETS = {
    'email_eu_core': dict(
        path='data/graphs/email_eu_core/email-Eu-core.txt',
        directed=True, sep=None, skip_header=False, dump_all_pairs=True),
    'facebook_politician': dict(
        path='data/graphs/facebook_gemsec/politician_edges.csv',
        directed=False, sep=',', skip_header=True, dump_all_pairs=False),
    'facebook_government': dict(
        path='data/graphs/facebook_gemsec/government_edges.csv',
        directed=False, sep=',', skip_header=True, dump_all_pairs=False),
    'facebook_artist': dict(
        path='data/graphs/facebook_gemsec/artist_edges.csv',
        directed=False, sep=',', skip_header=True, dump_all_pairs=False),
}


# --------------------------------------------------------------------------
# incremental one-hop coverage (O(deg) per gain) -- used for speed only; it is
# checked against Graph.coverage / im_graph.true_max_gain in --mode validate.
# --------------------------------------------------------------------------
class CoverageState:
    """covered[] bitmap of S ∪ N_out(S) for a monotonically growing S."""

    def __init__(self, out, n):
        self.out = out
        self.n = n
        self.covered = bytearray(n)
        self.n_covered = 0
        self.S = set()

    def gain(self, e):
        if e in self.S:
            return 0
        cov = self.covered
        g = 0 if cov[e] else 1
        for w in self.out[e]:
            if not cov[w]:
                g += 1
        return g

    def add(self, e):
        cov = self.covered
        if not cov[e]:
            cov[e] = 1
            self.n_covered += 1
        for w in self.out[e]:
            if not cov[w]:
                cov[w] = 1
                self.n_covered += 1
        self.S.add(e)


class LazyTop:
    """CELF-style lazy max-heap over a CoverageState: exact top-k gains at the
    current state without rescanning the ground set (valid because coverage is
    submodular and the state's S only grows)."""

    def __init__(self, state, ground):
        self.state = state
        self.version = 0
        self.fresh = {}
        self.heap = [(-state.gain(e), e) for e in ground]
        for e in ground:
            self.fresh[e] = 0
        heapq.heapify(self.heap)
        self.n_reeval = 0

    def advance(self):
        self.version += 1

    def top(self, k):
        out, buf = [], []
        S = self.state.S
        while len(out) < k and self.heap:
            negg, e = heapq.heappop(self.heap)
            if e in S:
                continue
            if self.fresh[e] == self.version:
                out.append((e, -negg))
                buf.append((negg, e))
            else:
                g = self.state.gain(e)
                self.fresh[e] = self.version
                self.n_reeval += 1
                heapq.heappush(self.heap, (-g, e))
        for item in buf:
            heapq.heappush(self.heap, item)
        return out


def fast_value_fn(graph, state):
    """Value function for CachedSetFunction: exact coverage, but O(deg) when the
    query is `state.S` plus one element (the CELF access pattern)."""
    def value(S):
        if len(S) == len(state.S) + 1:
            diff = S - state.S
            if len(diff) == 1:
                return float(state.n_covered + state.gain(next(iter(diff))))
        return float(graph.coverage(S))
    return value


# --------------------------------------------------------------------------
# graph loading / truncation
# --------------------------------------------------------------------------
_GRAPH_CACHE = {}


def load_graph(name, top_nodes=None):
    key = (name, top_nodes)
    if key in _GRAPH_CACHE:
        return _GRAPH_CACHE[key]
    cfg = DATASETS[name]
    g = Graph.from_file(os.path.join(ROOT, cfg['path']), directed=cfg['directed'],
                        sep=cfg['sep'], skip_header=cfg['skip_header'])
    if top_nodes is not None and top_nodes < g.n:
        g = induced_top_degree(g, top_nodes)
    _GRAPH_CACHE.clear()
    _GRAPH_CACHE[key] = g
    return g


def induced_top_degree(g, k):
    """Induced subgraph on the k highest out-degree nodes (ties by node id)."""
    deg = [len(s) for s in g.out]
    keep_list = sorted(range(g.n), key=lambda v: (-deg[v], v))[:k]
    keep_list.sort()
    idx = {v: i for i, v in enumerate(keep_list)}
    out = [set() for _ in keep_list]
    for v in keep_list:
        i = idx[v]
        for w in g.out[v]:
            j = idx.get(w)
            if j is not None:
                out[i].add(j)
    ng = object.__new__(Graph)
    ng.directed = g.directed
    ng.ids = {}
    ng.out = out
    ng.n = len(out)
    ng.m_input = sum(len(s) for s in out) // (1 if g.directed else 2)
    return ng


# --------------------------------------------------------------------------
# greedy helpers
# --------------------------------------------------------------------------
def greedy_prefix_values(graph, K):
    """Lazy greedy on the graph's own coverage; returns (picks, [f(prefix_K)])."""
    state = CoverageState(graph.out, graph.n)
    F = CachedSetFunction(fast_value_fn(graph, state))
    vals = []

    def record(t, Sbefore, chosen, gain):
        state.add(chosen)
        vals.append(state.n_covered)

    picks = lazy_greedy(F, list(range(graph.n)), K, record=record, quantize=None)
    return picks, vals


def run_one(dataset_label, gtrue, gobs, p, seed, K, den_vals, dump_all_pairs):
    """One greedy-on-f~ trajectory; returns (rows, pair_rows, diag).

    TASKS4 F1.2: the (d, d~) statistics (eta^path, sign-violation %) are ALWAYS
    computed over EVERY remaining candidate at every trajectory state.  The
    former top-50-by-d~ restriction on the three facebook graphs made eta^path
    a systematic underestimate (E2_notes.md section 4) and has been removed.
    `dump_all_pairs` now only controls how much of the candidate list is written
    to E2_pairs_sample.csv.gz (a sample file: all candidates for email seeds
    0..2, top-50 by d~ otherwise); it does not affect any statistic."""
    n = gtrue.n
    ground = list(range(n))
    true_state = CoverageState(gtrue.out, n)
    obs_state = CoverageState(gobs.out, n)
    true_top = LazyTop(true_state, ground)
    F_obs = CachedSetFunction(fast_value_fn(gobs, obs_state))
    stats = TrajectoryStats(EPS)
    num_vals = []
    pair_rows = []
    traj = []
    diag = dict(nonpos_steps=0, gain_mismatch=0)

    def record(t, Sbefore, chosen, gain_tilde):
        assert obs_state.S == Sbefore, 'state desync'
        d_chosen = true_state.gain(chosen)
        if d_chosen <= 0:
            diag['nonpos_steps'] += 1
        top1 = true_top.top(1)
        dmax = top1[0][1] if top1 else None
        if abs(obs_state.gain(chosen) - gain_tilde) > 1e-9:
            diag['gain_mismatch'] += 1
        cands = [(e, obs_state.gain(e)) for e in ground if e not in Sbefore]
        pairs = []
        has_chosen = False
        for e, dt in cands:
            d = d_chosen if e == chosen else true_state.gain(e)
            pairs.append((float(d), float(dt)))
            if e == chosen:
                has_chosen = True
        if not has_chosen:                       # always keep the chosen pair
            pairs.append((float(d_chosen), float(gain_tilde)))
            cands = list(cands) + [(chosen, gain_tilde)]
        if dump_all_pairs:                       # email seeds < 3: every pair
            dumped = list(zip(cands, pairs))
        else:                    # sample file only: top-50 by d~ (stats unaffected)
            dumped = sorted(zip(cands, pairs), key=lambda z: -z[0][1])[:TOP_M]
        for (e, dt), (d, dt2) in dumped:
            pair_rows.append((dataset_label, p, seed, t + 1, e, int(d), int(dt)))
        stats.add_step(float(d_chosen), None if dmax is None else float(dmax), pairs)
        traj.append(chosen)
        true_state.add(chosen)
        true_top.advance()
        obs_state.add(chosen)
        num_vals.append(true_state.n_covered)

    picks = lazy_greedy(F_obs, ground, K, record=record, quantize=None)
    assert len(picks) == len(num_vals)

    rows = []
    for k in range(1, len(num_vals) + 1):
        st = stats.upto(k)
        ratio = num_vals[k - 1] / den_vals[k - 1] if den_vals[k - 1] else float('nan')
        r = unified_row('E2', dataset_label, k, seed, ratio, st)
        r['p'] = p
        rows.append(r)
    diag['n_pairs_last'] = stats.upto(K)['n_pairs']
    diag['picks'] = picks
    return rows, pair_rows, diag


# --------------------------------------------------------------------------
# io helpers (incremental / restartable)
# --------------------------------------------------------------------------
def append_csv(path, fields, rows, dict_rows=True):
    new = not os.path.exists(path)
    with open(path, 'a', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields) if dict_rows else csv.writer(fh)
        if new:
            w.writeheader() if dict_rows else w.writerow(fields)
        for r in rows:
            w.writerow(r)


def append_pairs(rows):
    new = not os.path.exists(PAIRS_GZ)
    with gzip.open(PAIRS_GZ, 'at', newline='') as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(PAIR_FIELDS)
        w.writerows(rows)


def done_runs():
    done = set()
    if os.path.exists(ROWS_CSV):
        with open(ROWS_CSV) as fh:
            for r in csv.DictReader(fh):
                done.add((r['dataset'], r.get('p', ''), r['seed']))
    return done


def done_baselines():
    done = set()
    if os.path.exists(BASE_CSV):
        with open(BASE_CSV) as fh:
            for r in csv.DictReader(fh):
                done.add((r['dataset'], r['method'], r['p'], r['seed']))
    return done


# --------------------------------------------------------------------------
# modes
# --------------------------------------------------------------------------
def cmd_run(args):
    names = list(DATASETS) if args.dataset == 'all' else args.dataset.split(',')
    ps = P_LIST if args.p == 'all' else [float(x) for x in args.p.split(',')]
    seeds = parse_seeds(args.seeds)
    done = done_runs()
    bdone = done_baselines()
    for name in names:
        top_nodes = args.top_nodes
        label = args.label or (f'{name}_top{top_nodes // 1000}k' if top_nodes else name)
        t0 = time.time()
        gtrue = load_graph(name, top_nodes)
        print(f'[{name}] label={label} n={gtrue.n} m={gtrue.m_input} '
              f'load={time.time() - t0:.1f}s', flush=True)
        picks_true, den_vals = greedy_prefix_values(gtrue, K_MAX)
        print(f'[{label}] greedy-on-f done, f(K=30)={den_vals[-1]} '
              f'({time.time() - t0:.1f}s)', flush=True)
        # baselines that do not depend on (p, seed)
        brows = []
        if (label, 'greedy_f', '', '') not in bdone:
            for k, v in enumerate(den_vals, 1):
                brows.append(dict(dataset=label, method='greedy_f', p='', seed='',
                                  K=k, f_value=v))
        for r in range(N_RANDOM):
            if (label, 'random', '', str(r)) in bdone:
                continue
            rng = random.Random(10_000 + r)
            nodes = rng.sample(range(gtrue.n), K_MAX)
            st = CoverageState(gtrue.out, gtrue.n)
            for k, e in enumerate(nodes, 1):
                st.add(e)
                brows.append(dict(dataset=label, method='random', p='', seed=r,
                                  K=k, f_value=st.n_covered))
        if brows:
            append_csv(BASE_CSV, BASE_FIELDS, brows)
        for p in ps:
            for seed in seeds:
                key = (label, str(p), str(seed))
                if key in done:
                    print(f'  skip {key} (already in E2_rows.csv)', flush=True)
                    continue
                ts = time.time()
                gobs = gtrue.edge_subsample(p, seed)
                rows, pair_rows, diag = run_one(
                    label, gtrue, gobs, p, seed, K_MAX, den_vals,
                    dump_all_pairs=(DATASETS[name]['dump_all_pairs']
                                    and seed < PAIRS_FULL_SEEDS))
                append_csv(ROWS_CSV, ROW_FIELDS_E2, rows)
                append_pairs(pair_rows)
                # degree baseline on the OBSERVED graph (fair no-prediction
                # baseline: only observable information)
                if (label, 'degree_obs', str(p), str(seed)) not in bdone:
                    deg = [(len(gobs.out[v]), -v) for v in range(gobs.n)]
                    order = [-x[1] for x in sorted(deg, reverse=True)[:K_MAX]]
                    st = CoverageState(gtrue.out, gtrue.n)
                    brows = []
                    for k, e in enumerate(order, 1):
                        st.add(e)
                        brows.append(dict(dataset=label, method='degree_obs', p=p,
                                          seed=seed, K=k, f_value=st.n_covered))
                    append_csv(BASE_CSV, BASE_FIELDS, brows)
                last = rows[-1]
                print(f'  p={p} seed={seed}: ratio30={last["ratio"]} '
                      f'eta_sel30={last["eta_sel"]} eta_path30={last["eta_path_trimmed"]} '
                      f'viol%={last["viol_sign_pct"]} nonpos={diag["nonpos_steps"]} '
                      f'({time.time() - ts:.1f}s)', flush=True)


def cmd_probe(args):
    name = args.dataset
    seeds = parse_seeds(args.seeds)
    p = float(args.p)
    t0 = time.time()
    gtrue = load_graph(name, args.top_nodes)
    t_load = time.time() - t0
    t0 = time.time()
    picks_true, den_vals = greedy_prefix_values(gtrue, K_MAX)
    t_gt = time.time() - t0
    t0 = time.time()
    gobs = gtrue.edge_subsample(p, seeds[0])
    t_sub = time.time() - t0
    t0 = time.time()
    rows, pair_rows, diag = run_one(name, gtrue, gobs, p, seeds[0], K_MAX,
                                    den_vals, dump_all_pairs=False)
    t_run = time.time() - t0
    print(f'PROBE {name} n={gtrue.n} m={gtrue.m_input} p={p} seed={seeds[0]}')
    print(f'  load={t_load:.1f}s greedy_true={t_gt:.1f}s subsample={t_sub:.1f}s '
          f'run={t_run:.1f}s  -> per-run ~{t_sub + t_run:.1f}s')
    print(f'  ratio30={rows[-1]["ratio"]} eta_sel30={rows[-1]["eta_sel"]} '
          f'eta_path30={rows[-1]["eta_path_trimmed"]} viol%={rows[-1]["viol_sign_pct"]}')


def cmd_validate(args):
    """Two-method consistency: the lazy true-graph max-gain heap vs a plain full
    scan (im_graph.true_max_gain), and the O(deg) incremental coverage vs
    Graph.coverage.  Run on email_eu_core (small enough for the O(n) scan)."""
    name = 'email_eu_core'
    gtrue = load_graph(name)
    out_lines = []
    for p in P_LIST:
        for seed in (0, 1):
            gobs = gtrue.edge_subsample(p, seed)
            n = gtrue.n
            ground = list(range(n))
            # reference: plain CachedSetFunction on Graph.coverage, full scans
            F_true_ref = CachedSetFunction(lambda S: float(gtrue.coverage(S)))
            F_obs_ref = CachedSetFunction(lambda S: float(gobs.coverage(S)))
            true_state = CoverageState(gtrue.out, n)
            obs_state = CoverageState(gobs.out, n)
            true_top = LazyTop(true_state, ground)
            F_obs_fast = CachedSetFunction(fast_value_fn(gobs, obs_state))
            dmax_err = dcov_err = gain_err = 0.0
            picks_ref = lazy_greedy(F_obs_ref, ground, K_MAX, quantize=None)

            def record(t, Sbefore, chosen, gain_tilde):
                nonlocal dmax_err, dcov_err, gain_err
                lazy_max = true_top.top(1)[0][1]
                scan_max = true_max_gain(F_true_ref, set(Sbefore), ground)
                dmax_err = max(dmax_err, abs(lazy_max - scan_max))
                dcov_err = max(dcov_err,
                               abs(true_state.n_covered - F_true_ref(frozenset(Sbefore))))
                gain_err = max(gain_err,
                               abs(obs_state.gain(chosen)
                                   - F_obs_ref.gain(frozenset(Sbefore), chosen)))
                true_state.add(chosen)
                true_top.advance()
                obs_state.add(chosen)

            picks_fast = lazy_greedy(F_obs_fast, ground, K_MAX, record=record,
                                     quantize=None)
            same = picks_fast == picks_ref
            line = (f'{name} p={p} seed={seed}: max|lazy_dmax - full_scan_dmax|='
                    f'{dmax_err:g}, max|incr_coverage - Graph.coverage|={dcov_err:g}, '
                    f'max|incr_gain - cached_gain|={gain_err:g}, '
                    f'greedy trajectories identical={same}')
            print(line, flush=True)
            out_lines.append(line)
    # smaller cross-check on a mid-size graph, first 8 steps only
    g2 = load_graph('facebook_politician')
    gobs = g2.edge_subsample(0.5, 0)
    n = g2.n
    ground = list(range(n))
    F_true_ref = CachedSetFunction(lambda S: float(g2.coverage(S)))
    true_state = CoverageState(g2.out, n)
    obs_state = CoverageState(gobs.out, n)
    true_top = LazyTop(true_state, ground)
    F_obs_fast = CachedSetFunction(fast_value_fn(gobs, obs_state))
    err = 0.0
    steps = [0]

    def record2(t, Sbefore, chosen, gain_tilde):
        nonlocal err
        if steps[0] < 8:
            err = max(err, abs(true_top.top(1)[0][1]
                               - true_max_gain(F_true_ref, set(Sbefore), ground)))
        steps[0] += 1
        true_state.add(chosen)
        true_top.advance()
        obs_state.add(chosen)

    lazy_greedy(F_obs_fast, ground, 8, record=record2, quantize=None)
    line = (f'facebook_politician p=0.5 seed=0 (first 8 steps): '
            f'max|lazy_dmax - full_scan_dmax|={err:g}')
    print(line, flush=True)
    out_lines.append(line)
    with open(os.path.join(HERE, 'E2_validation.txt'), 'w') as fh:
        fh.write('\n'.join(out_lines) + '\n')


def cmd_trunccheck(args):
    """Measure the bias introduced by keeping only the top-50 d~ candidates per
    step: recompute eta^path with ALL candidates on a few runs of the large
    graphs and compare with the top-50 restriction actually used in E2_rows.csv.
    Writes results/E2_truncation_check.csv; does NOT touch E2_rows.csv."""
    names = ([n for n in DATASETS if n != 'email_eu_core']
             if args.dataset == 'all' else args.dataset.split(','))
    seeds = parse_seeds(args.seeds)
    out = []
    for name in names:
        gtrue = load_graph(name, args.top_nodes)
        _, den_vals = greedy_prefix_values(gtrue, K_MAX)
        for p in (P_LIST if args.p == 'all' else [float(x) for x in args.p.split(',')]):
            for seed in seeds:
                t0 = time.time()
                gobs = gtrue.edge_subsample(p, seed)
                rows, pair_rows, _ = run_one(name, gtrue, gobs, p, seed, K_MAX,
                                             den_vals, dump_all_pairs=False)
                full = float(rows[-1]['eta_path_trimmed'])
                mu = mo = None
                for _, _, _, _, _, d, dt in pair_rows:   # the top-50 subset
                    if d >= EPS and dt >= EPS:
                        mu = d / dt if mu is None else max(mu, d / dt)
                        mo = dt / d if mo is None else max(mo, dt / d)
                top = max(mu * mo, 1.0)
                r = dict(dataset=name, p=p, seed=seed, K=K_MAX,
                         eta_path_full=f'{full:.6g}', eta_path_top50=f'{top:.6g}',
                         ratio_top50_over_full=f'{top / full:.4f}',
                         eta_sel=rows[-1]['eta_sel'])
                out.append(r)
                print(f'{name} p={p} seed={seed}: eta_path full={full:.3f} '
                      f'top50={top:.3f} ({top / full:.3f}x) [{time.time() - t0:.1f}s]',
                      flush=True)
    fields = ['dataset', 'p', 'seed', 'K', 'eta_path_full', 'eta_path_top50',
              'ratio_top50_over_full', 'eta_sel']
    path = os.path.join(HERE, 'E2_truncation_check.csv')
    append_csv(path, fields, out)          # append: chunks accumulate
    print('wrote', path)


def quantiles(xs):
    xs = sorted(xs)
    if not xs:
        return float('nan'), float('nan'), float('nan')

    def q(f):
        if len(xs) == 1:
            return xs[0]
        i = f * (len(xs) - 1)
        lo, hi = int(i), min(int(i) + 1, len(xs) - 1)
        return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)
    return q(0.25), q(0.5), q(0.75)


def cmd_aggregate(args):
    by = {}
    with open(ROWS_CSV) as fh:
        for r in csv.DictReader(fh):
            if int(r['K']) != K_MAX:
                continue
            key = (r['dataset'], r['p'])
            by.setdefault(key, []).append(r)
    out = []
    for (ds, p), rs in sorted(by.items(), key=lambda kv: (kv[0][0], float(kv[0][1]))):
        etas = [float(x['eta_sel']) for x in rs if x['eta_sel']]
        ratios = [float(x['ratio']) for x in rs if x['ratio']]
        paths = [float(x['eta_path_trimmed']) for x in rs if x['eta_path_trimmed']]
        q1, med, q3 = quantiles(etas)
        r1, rmed, r3 = quantiles(ratios)
        p1, pmed, p3 = quantiles(paths)
        out.append(dict(dataset=ds, p=p, n_runs=len(rs),
                        eta_sel_K30_median=f'{med:.6g}',
                        eta_sel_K30_q25=f'{q1:.6g}', eta_sel_K30_q75=f'{q3:.6g}',
                        eta_sel_K30_IQR=f'{q3 - q1:.6g}',
                        eta_path_K30_median=f'{pmed:.6g}',
                        eta_path_K30_IQR=f'{p3 - p1:.6g}',
                        ratio_K30_median=f'{rmed:.6f}',
                        ratio_K30_q25=f'{r1:.6f}', ratio_K30_q75=f'{r3:.6f}',
                        LK_eta_sel_median=f'{L_K(med, K_MAX):.6f}'))
    fields = ['dataset', 'p', 'n_runs', 'eta_sel_K30_median', 'eta_sel_K30_q25',
              'eta_sel_K30_q75', 'eta_sel_K30_IQR', 'eta_path_K30_median',
              'eta_path_K30_IQR', 'ratio_K30_median', 'ratio_K30_q25',
              'ratio_K30_q75', 'LK_eta_sel_median']
    with open(PETA_CSV, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(out)
    for r in out:
        print(r, flush=True)


def cmd_figures(args):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows = list(csv.DictReader(open(PETA_CSV)))
    datasets = sorted({r['dataset'] for r in rows})
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    colors = plt.cm.viridis([0.1, 0.35, 0.6, 0.85])
    for i, ds in enumerate(datasets):
        rs = sorted([r for r in rows if r['dataset'] == ds], key=lambda r: float(r['p']))
        xs = [float(r['p']) for r in rs]
        med = [float(r['eta_sel_K30_median']) for r in rs]
        lo = [float(r['eta_sel_K30_q25']) for r in rs]
        hi = [float(r['eta_sel_K30_q75']) for r in rs]
        axes[0].plot(xs, med, 'o-', color=colors[i % 4], label=ds)
        axes[0].fill_between(xs, lo, hi, color=colors[i % 4], alpha=0.18)
        rmed = [float(r['ratio_K30_median']) for r in rs]
        rlo = [float(r['ratio_K30_q25']) for r in rs]
        rhi = [float(r['ratio_K30_q75']) for r in rs]
        axes[1].plot(xs, rmed, 'o-', color=colors[i % 4], label=ds)
        axes[1].fill_between(xs, rlo, rhi, color=colors[i % 4], alpha=0.18)
    axes[0].set_xlabel('edge retention probability $p$')
    axes[0].set_ylabel(r'$\eta^{sel}$ at $K=30$ (median, IQR band)')
    axes[0].set_title('observation quality vs prediction error')
    axes[1].set_xlabel('edge retention probability $p$')
    axes[1].set_ylabel(r'ratio $f(S^{\tilde f})/f(S^{f})$ at $K=30$')
    axes[1].set_title('observation quality vs realized ratio')
    axes[1].axhline(1.0, color='0.6', lw=0.8, ls='--')
    axes[0].set_yscale('log')
    # panel 3: baselines at K=30, normalised by greedy on f
    base = list(csv.DictReader(open(BASE_CSV)))
    gf, rnd, deg = {}, {}, {}
    for r in base:
        if r['K'] != str(K_MAX):
            continue
        if r['method'] == 'greedy_f':
            gf[r['dataset']] = float(r['f_value'])
        elif r['method'] == 'random':
            rnd.setdefault(r['dataset'], []).append(float(r['f_value']))
        elif r['method'] == 'degree_obs':
            deg.setdefault((r['dataset'], r['p']), []).append(float(r['f_value']))
    sur = {(r['dataset'], r['p']): float(r['ratio_K30_median']) for r in rows}
    width = 0.13
    for i, ds in enumerate(datasets):
        xs = [i - 2.5 * width, i - 1.5 * width, i - 0.5 * width,
              i + 0.5 * width, i + 1.5 * width]
        vals = [sur[(ds, '0.3')], sur[(ds, '0.5')], sur[(ds, '0.8')],
                sum(deg[(ds, '0.5')]) / len(deg[(ds, '0.5')]) / gf[ds],
                sum(rnd[ds]) / len(rnd[ds]) / gf[ds]]
        cs = ['#4c72b0', '#6f9bd1', '#a8c6e8', '#dd8452', '#999999']
        labs = ['pred. greedy p=0.3', 'pred. greedy p=0.5', 'pred. greedy p=0.8',
                'degree (observed, p=0.5)', 'random (10 runs)']
        for x, v, c, lb in zip(xs, vals, cs, labs):
            axes[2].bar(x, v, width, color=c, label=lb if i == 0 else None)
    axes[2].set_xticks(range(len(datasets)))
    axes[2].set_xticklabels([d.replace('facebook_', 'fb_') for d in datasets],
                            fontsize=7, rotation=15)
    axes[2].axhline(1.0, color='0.4', lw=0.8, ls='--')
    axes[2].set_ylabel(r'$f(\cdot)/f(S^{f}_{greedy})$ at $K=30$')
    axes[2].set_title('baselines (median over 20 observed graphs)')
    for ax in axes:
        ax.grid(alpha=0.25)
        ax.legend(fontsize=7)
    fig.tight_layout()
    for ext in ('png', 'pdf'):
        fig.savefig(os.path.join(ROOT, 'figures', f'E2_p_eta.{ext}'), dpi=180)
    print('wrote figures/E2_p_eta.png/.pdf')


def parse_seeds(spec):
    out = []
    for part in str(spec).split(','):
        if '-' in part:
            a, b = part.split('-')
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', default='run',
                    choices=['run', 'probe', 'validate', 'aggregate', 'figures',
                             'trunccheck'])
    ap.add_argument('--dataset', default='all')
    ap.add_argument('--p', default='all')
    ap.add_argument('--seeds', default='0-19')
    ap.add_argument('--top-nodes', type=int, default=None)
    ap.add_argument('--label', default=None)
    args = ap.parse_args()
    {'run': cmd_run, 'probe': cmd_probe, 'validate': cmd_validate,
     'aggregate': cmd_aggregate, 'figures': cmd_figures,
     'trunccheck': cmd_trunccheck}[args.mode](args)


if __name__ == '__main__':
    main()
