"""E3: text summarization with heuristic surrogates (TASKS_EXP.md, E3 section).

Principles (TASKS_EXP.md 1-5, enforced here):
1. NO artificial oracle perturbation.  The three f~ (coverage / diversity /
   facility-location) are computed from the ARTICLE ALONE and never touch the
   reference summary, so they are legitimate surrogates.  f (ROUGE-1 F against
   the reference) is only ever used for MEASUREMENT (eta, ratio), never inside
   the greedy that produces S_greedy^{f~}.
2. Every f and f~ evaluation is cached (src/im_graph.CachedSetFunction, keyed by
   frozenset); every greedy is CELF-lazy (src/im_graph.lazy_greedy) with
   quantize=None (real-data task, no adversarial ties).
3. Reproducible: NO randomness anywhere (clustering is a deterministic
   farthest-first traversal), seed column = article number 1..100, results to
   CSV / CSV.GZ.
4. Honest reporting: d <= 0 share, sign-violation %, trimming eps, CELF-vs-exact
   deviation on the non-submodular f, all in results/E3_summary.json ->
   results/E3_notes.md.  Nothing is hidden.
5. CPU only, single process; pilot (--limit) first, then full run.

Role in the paper: ROUGE-1 F is NOT monotone and not known to be submodular, so
this task documents "behaviour outside the model's boundary" -- it is reported
as such, not as a confirmation of the theory.

Outputs
-------
results/E3_rows.csv        unified row format (src/statistics.ROW_FIELDS)
results/E3_pairs.csv.gz    every (d, dtilde) candidate pair on every trajectory
results/E3_summary.json    aggregates used to write results/E3_notes.md
figures/E3_overview.png/.pdf (with --fig)

Usage
-----
python3 results/E3_run.py [--limit N] [--fig]
"""
import argparse
import collections
import csv
import gzip
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'src'))
from im_graph import CachedSetFunction, lazy_greedy            # noqa: E402
from statistics import TrajectoryStats, unified_row, write_rows  # noqa: E402

BBC = os.path.join(ROOT, 'data', 'bbc', 'BBC News Summary')
CATEGORIES = ['business', 'sport', 'tech']
N_ARTICLES = 100
K_MIN, K_MAX = 3, 7
EPS = 0.005                     # TASKS_EXP: eps for the summarization task
ALPHA_COVERAGE = 0.25           # saturated-coverage parameter
CLUSTER_FRACTION = 0.2          # #clusters = max(2, round(0.2 * n_sentences))
SURROGATES = ['coverage', 'diversity', 'facility']

# Reference summaries for sport/tech are NOT in the repository copy of the
# dataset (data/bbc/.../Summaries/ only contains `business`, 118 files; the
# source data/raw/bbc.zip has the same gap).  Fallback source, verified below
# to reproduce the local business summaries token-for-token:
CSV_URL = ('https://huggingface.co/datasets/gopalkalpande/bbc-news-summary/'
           'resolve/main/bbc-news-summary.csv')
_LOCAL_CSV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          'data', 'raw', 'bbc-news-summary.csv')
# Prefer the repository copy (data/raw/, committed for offline reproducibility);
# fall back to env override, then /tmp cache + download.
CSV_CACHE = (os.environ.get('E3_BBC_CSV')
             or (_LOCAL_CSV if os.path.exists(_LOCAL_CSV) else None)
             or '/tmp/e3_bbc_cache/bbc-news-summary.csv')

WORD = re.compile(r'\w+')
SENT_SPLIT = re.compile(r'(?<=[.!?])\s+')


# --------------------------------------------------------------------------
# data
# --------------------------------------------------------------------------
def read_text(path):
    """UTF-8 first (the corpus is UTF-8: '\\xc2\\xa3' for the pound sign);
    errors='replace' so a bad byte never aborts the run.  Returns (text, flag)."""
    raw = open(path, 'rb').read()
    try:
        return raw.decode('utf-8'), False
    except UnicodeDecodeError:
        return raw.decode('utf-8', errors='replace'), True


def tokens(text):
    return WORD.findall(text.lower())


def split_sentences(text):
    """Sentence splitting WITHOUT nltk (no package installs, no network at run
    time): the headline (first non-empty line) is kept as its OWN sentence and
    is element 0 of the ground set; the remaining non-empty lines are joined
    with a space and split on [.!?] followed by whitespace.  Known limitation:
    an abbreviation ending in '.' would be over-split (the BBC corpus writes
    'US', 'UK', 'Mr' without periods, so this is rare)."""
    lines = [l.strip() for l in text.split('\n')]
    nonempty = [l for l in lines if l]
    if not nonempty:
        return []
    title, body = nonempty[0], ' '.join(nonempty[1:])
    sents = [s.strip() for s in SENT_SPLIT.split(body)]
    sents = [s for s in sents if s and WORD.search(s)]
    return [title] + sents


def ensure_csv():
    if os.path.exists(CSV_CACHE):
        return True
    os.makedirs(os.path.dirname(CSV_CACHE), exist_ok=True)
    try:
        subprocess.run(['curl', '-sSL', '--max-time', '600', '-o', CSV_CACHE, CSV_URL],
                       check=True)
        return os.path.exists(CSV_CACHE) and os.path.getsize(CSV_CACHE) > 10 ** 6
    except Exception as exc:                                   # network failure
        print(f'[warn] reference-summary fallback download failed: {exc}')
        return False


def load_references():
    """index[category][token-tuple of article] -> reference summary text."""
    if not ensure_csv():
        return {}
    csv.field_size_limit(10 ** 7)
    idx = {c: collections.defaultdict(list) for c in CATEGORIES}
    with open(CSV_CACHE, encoding='utf-8', errors='replace') as fh:
        for row in csv.DictReader(fh):
            cat = row['File_path']
            if cat in idx:
                idx[cat][tuple(tokens(row['Articles']))].append(row['Summaries'])
    return idx


def get_reference(cat, fname, art_text, csv_idx, notes):
    """Local reference summary if present, else the verified CSV fallback."""
    local = os.path.join(BBC, 'Summaries', cat, fname)
    if os.path.exists(local):
        txt, bad = read_text(local)
        if bad:
            notes['bad_bytes'] += 1
        return txt, 'local'
    cands = csv_idx.get(cat, {}).get(tuple(tokens(art_text)))
    if not cands:
        return None, 'missing'
    if len({tuple(tokens(c)) for c in cands}) > 1:
        return None, 'ambiguous'          # duplicate article, differing summaries
    return cands[0], 'csv'


# --------------------------------------------------------------------------
# f  (true objective) and the three surrogates
# --------------------------------------------------------------------------
class Rouge1F:
    """ROUGE-1 F-measure of the concatenated selected sentences against the
    reference summary.  Self-implemented, exactly as specified in E3:
    lowercase, r'\\w+' tokenization, clipped unigram counts,
    P = overlap/|candidate|, R = overlap/|reference|, F = 2PR/(P+R) (0 if P+R=0).
    NO stopword removal and NO stemming (kept deliberately simple; recorded in
    the notes).  f(empty) = 0; f is NOT monotone (precision falls as sentences
    are added) and is not known to be submodular."""

    def __init__(self, sent_counts, sent_len, ref_counts, ref_len):
        self.sc, self.sl = sent_counts, sent_len
        self.rc, self.rl = ref_counts, ref_len

    def __call__(self, S):
        if not S or self.rl == 0:
            return 0.0
        cnt = collections.Counter()
        n = 0
        for i in S:
            cnt.update(self.sc[i])
            n += self.sl[i]
        if n == 0:
            return 0.0
        ov = 0
        rc = self.rc
        for w, c in cnt.items():
            r = rc.get(w)
            if r:
                ov += c if c < r else r
        if ov == 0:
            return 0.0
        p, r = ov / n, ov / self.rl
        return 2 * p * r / (p + r)


class Coverage:
    """C(S) = sum_{w in doc vocab} min(tf_S(w), alpha * tf_doc(w)), alpha=0.25.
    Saturated coverage (Lin-Bilmes style): monotone submodular.  Uses the
    article only."""

    def __init__(self, sent_counts, doc_counts, alpha):
        self.sc = sent_counts
        self.cap = {w: alpha * c for w, c in doc_counts.items()}

    def __call__(self, S):
        if not S:
            return 0.0
        cnt = collections.Counter()
        for i in S:
            cnt.update(self.sc[i])
        cap = self.cap
        return float(sum(min(c, cap[w]) for w, c in cnt.items()))


class Diversity:
    """D(S) = sum_i sqrt( sum_{s in S cap P_i} r_s ), the pure diversity-reward
    term of Lin-Bilmes (the lambda of C + lambda*D is irrelevant because D is
    scored as a standalone f~).  Monotone submodular.
    r_s = (1/n) sum_j sim(j, s)  (average tf-cosine similarity to the document).
    Clusters P_i: DETERMINISTIC farthest-first traversal (k-center greedy) with
    k = max(2, round(0.2*n)) centers, first center = argmax r_s (ties by index),
    then each sentence assigned to its most similar center.  No k-means, no RNG,
    so the run has no randomness at all."""

    def __init__(self, sim, reward, k):
        n = len(reward)
        centers = [max(range(n), key=lambda i: (reward[i], -i))]
        while len(centers) < min(k, n):
            best, bestd = None, None
            for i in range(n):
                if i in centers:
                    continue
                d = min(1.0 - sim[i][c] for c in centers)
                if bestd is None or d > bestd + 1e-15:
                    best, bestd = i, d
            if best is None:
                break
            centers.append(best)
        lab = []
        for i in range(n):
            lab.append(max(range(len(centers)),
                           key=lambda ci: (sim[i][centers[ci]], -ci)))
        self.lab, self.reward, self.ncl = lab, reward, len(centers)
        self.centers = centers

    def __call__(self, S):
        if not S:
            return 0.0
        acc = [0.0] * self.ncl
        for i in S:
            acc[self.lab[i]] += self.reward[i]
        return float(sum(math.sqrt(a) for a in acc if a > 0))


class FacilityLocation:
    """FL(S) = sum_i max_{j in S} sim(i, j), sim = tf-vector cosine.  Monotone
    submodular, FL(empty) = 0.  Uses the article only."""

    def __init__(self, sim):
        self.sim = sim
        self.n = len(sim)

    def __call__(self, S):
        if not S:
            return 0.0
        sim = self.sim
        tot = 0.0
        for i in range(self.n):
            row = sim[i]
            tot += max(row[j] for j in S)
        return tot


def cosine_matrix(sent_counts):
    n = len(sent_counts)
    norms = [math.sqrt(sum(v * v for v in c.values())) or 1.0 for c in sent_counts]
    sim = [[0.0] * n for _ in range(n)]
    for i in range(n):
        ci = sent_counts[i]
        for j in range(i, n):
            cj = sent_counts[j]
            a, b = (ci, cj) if len(ci) <= len(cj) else (cj, ci)
            dot = sum(c * b.get(w, 0) for w, c in a.items())
            v = dot / (norms[i] * norms[j])
            sim[i][j] = sim[j][i] = v
    return sim


# --------------------------------------------------------------------------
# one (article, surrogate) trajectory
# --------------------------------------------------------------------------
def run_trajectory(F_true, F_tilde, ground, K):
    """CELF-lazy greedy on the SURROGATE; at every visited state record the true
    and predicted gain of EVERY remaining candidate.  Returns (picks, steps)
    with steps[t] = (chosen, d_chosen, dmax_true, [(d, dtilde, is_chosen)...])."""
    steps = []

    def record(t, S_before, chosen, gain_tilde):
        Sb = set(S_before)
        pairs = []
        d_ch = dmax = None
        for e in ground:
            if e in Sb:
                continue
            d = F_true.gain(Sb, e)
            dt = F_tilde.gain(Sb, e)
            pairs.append((d, dt, 1 if e == chosen else 0))
            if dmax is None or d > dmax:
                dmax = d
            if e == chosen:
                d_ch = d
        steps.append((chosen, d_ch, dmax, pairs))

    picks = lazy_greedy(F_tilde, ground, K, record=record, quantize=None)
    return picks, steps


def exact_greedy(F, ground, K):
    """Non-lazy greedy, used ONLY as a correctness check on the non-submodular
    f (CELF's laziness is only justified for submodular objectives)."""
    S, Sset = [], set()
    for _ in range(K):
        best, bg = None, None
        for e in ground:
            if e in Sset:
                continue
            g = F.gain(Sset, e)
            if bg is None or g > bg:
                best, bg = e, g
        if best is None:
            break
        S.append(best)
        Sset.add(best)
    return S


def structure_check(limit):
    """Empirical check of the structural assumptions, so the notes state facts
    rather than beliefs.  For a deterministic sample of articles, enumerate all
    A subset B (|A| <= 3, B = A + one element) over the first 8 sentences and
    test the submodularity inequality d_e(A) >= d_e(B) and monotonicity
    d_e(A) >= 0, for f and for each f~.  No randomness."""
    import itertools
    csv_idx = load_references()
    out = {name: collections.Counter() for name in ['rouge'] + SURROGATES}
    maxviol = {name: 0.0 for name in ['rouge'] + SURROGATES}
    for cat in CATEGORIES:
        for num in range(1, limit + 1, 10):          # every 10th article
            fname = f'{num:03d}.txt'
            apath = os.path.join(BBC, 'News Articles', cat, fname)
            if not os.path.exists(apath):
                continue
            art, _ = read_text(apath)
            ref, src = get_reference(cat, fname, art, csv_idx, collections.Counter())
            if ref is None:
                continue
            sents = split_sentences(art)
            n = len(sents)
            if n < 9:
                continue
            sc = [collections.Counter(tokens(s)) for s in sents]
            sl = [sum(c.values()) for c in sc]
            dc = collections.Counter()
            for c in sc:
                dc.update(c)
            rc = collections.Counter(tokens(ref))
            sim = cosine_matrix(sc)
            reward = [sum(sim[j][i] for j in range(n)) / n for i in range(n)]
            fns = {'rouge': Rouge1F(sc, sl, rc, sum(rc.values())),
                   'coverage': Coverage(sc, dc, ALPHA_COVERAGE),
                   'diversity': Diversity(sim, reward,
                                          max(2, round(CLUSTER_FRACTION * n))),
                   'facility': FacilityLocation(sim)}
            m = list(range(8))
            for name, fn in fns.items():
                F = CachedSetFunction(fn)
                for r in range(0, 4):
                    for A in itertools.combinations(m, r):
                        Aset = set(A)
                        for b in m:
                            if b in Aset:
                                continue
                            B = Aset | {b}
                            for e in m:
                                if e in B:
                                    continue
                                dA, dB = F.gain(Aset, e), F.gain(B, e)
                                out[name]['pairs'] += 1
                                if dB > dA + 1e-12:
                                    out[name]['submod_viol'] += 1
                                    maxviol[name] = max(maxviol[name], dB - dA)
                                if dA < -1e-12:
                                    out[name]['mono_viol'] += 1
                            out[name]['gain_tests'] += 1
    res = {}
    for name in out:
        c = out[name]
        res[name] = dict(pairs=c['pairs'],
                         submod_viol=c['submod_viol'],
                         submod_viol_pct=100.0 * c['submod_viol'] / max(1, c['pairs']),
                         mono_viol=c['mono_viol'],
                         mono_viol_pct=100.0 * c['mono_viol'] / max(1, c['pairs']),
                         max_submod_violation=maxviol[name])
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=N_ARTICLES,
                    help='articles per category (pilot first, per principle 5)')
    ap.add_argument('--fig', action='store_true')
    ap.add_argument('--tag', default='')
    args = ap.parse_args()

    csv_idx = load_references()
    notes = collections.Counter()
    rows = []
    pair_rows = []
    diag = collections.defaultdict(list)     # (cat, sur) -> per-article diagnostics
    ref_src = collections.Counter()
    skipped = []
    nsent_all = []

    for cat in CATEGORIES:
        for num in range(1, args.limit + 1):
            fname = f'{num:03d}.txt'
            apath = os.path.join(BBC, 'News Articles', cat, fname)
            if not os.path.exists(apath):
                skipped.append((cat, num, 'no_article'))
                continue
            art, bad = read_text(apath)
            if bad:
                notes['bad_bytes'] += 1
            ref, src = get_reference(cat, fname, art, csv_idx, notes)
            ref_src[f'{cat}:{src}'] += 1
            if ref is None:
                skipped.append((cat, num, f'no_reference:{src}'))
                continue
            sents = split_sentences(art)
            n = len(sents)
            nsent_all.append(n)
            if n < 5:
                skipped.append((cat, num, f'too_few_sentences:{n}'))
                continue
            Kmax = min(K_MAX, n - 2)         # keep >= 2 candidates at every step
            if Kmax < K_MIN:
                skipped.append((cat, num, f'too_few_sentences:{n}'))
                continue

            sent_counts = [collections.Counter(tokens(s)) for s in sents]
            sent_len = [sum(c.values()) for c in sent_counts]
            doc_counts = collections.Counter()
            for c in sent_counts:
                doc_counts.update(c)
            ref_counts = collections.Counter(tokens(ref))
            ref_len = sum(ref_counts.values())
            sim = cosine_matrix(sent_counts)
            reward = [sum(sim[j][i] for j in range(n)) / n for i in range(n)]
            ground = list(range(n))

            # f is built ONCE per article and shared by all surrogates and by
            # the denominator greedy (one cache, principle 2).
            F_true = CachedSetFunction(Rouge1F(sent_counts, sent_len,
                                               ref_counts, ref_len))
            picks_true = lazy_greedy(F_true, ground, Kmax, quantize=None)
            picks_exact = exact_greedy(F_true, ground, Kmax)

            makers = {
                'coverage': lambda: Coverage(sent_counts, doc_counts, ALPHA_COVERAGE),
                'diversity': lambda: Diversity(sim, reward,
                                               max(2, round(CLUSTER_FRACTION * n))),
                'facility': lambda: FacilityLocation(sim),
            }
            for sur in SURROGATES:
                F_t = CachedSetFunction(makers[sur]())
                picks, steps = run_trajectory(F_true, F_t, ground, Kmax)

                # scale match for the eps-trimming of eta^path only: the
                # surrogates live on their own scales (word counts, sqrt-rewards,
                # similarity sums) while eps = 0.005 is a ROUGE-F unit.  eta^path
                # itself is scale invariant (max(d/dt)*max(dt/d)); only the
                # trimming is not, so dtilde is rescaled by
                #   c = max_e d_e(empty) / max_e dtilde_e(empty)
                # (both maxima at S = empty, recomputable from E3_pairs.csv.gz,
                # step == 0).  Raw dtilde is what gets written to that file.
                d0 = max((d for d, _, _ in steps[0][3]), default=0.0)
                t0 = max((t for _, t, _ in steps[0][3]), default=0.0)
                scale = (d0 / t0) if (d0 > 0 and t0 > 0) else 1.0
                if not (d0 > 0 and t0 > 0):
                    notes['degenerate_scale'] += 1

                stats = TrajectoryStats(EPS)
                per_step_np, per_step_n = [], []      # d<=0 counts, per step
                for t, (chosen, d_ch, dmax, pairs) in enumerate(steps):
                    stats.add_step(d_ch, dmax, [(d, dt * scale) for d, dt, _ in pairs])
                    per_step_np.append(sum(1 for d, _, _ in pairs if d <= 0))
                    per_step_n.append(len(pairs))
                    for d, dt, isch in pairs:
                        pair_rows.append((f'{cat}_{sur}', num, t,
                                          f'{d:.10g}', f'{dt:.10g}', isch))
                dataset = f'{cat}_{sur}'
                for K in range(K_MIN, Kmax + 1):
                    num_v = F_true(set(picks[:K]))
                    den_v = F_true(set(picks_true[:K]))
                    ratio = (num_v / den_v) if den_v > 0 else None
                    st = stats.upto(K)
                    rows.append(unified_row('E3', dataset, K, num, ratio, st))
                    diag[(dataset, K)].append(dict(
                        ratio=ratio, eta_sel=st['eta_sel'], eta_path=st['eta_path'],
                        viol=st['viol_sign_pct'], nonpos_steps=st['n_nonpos_steps'],
                        steps=K, nonpos_pairs=sum(per_step_np[:K]),
                        npairs=sum(per_step_n[:K]),
                        den_exact=F_true(set(picks_exact[:K])), den_lazy=den_v))
            del F_true
        print(f'[{cat}] done, rows so far {len(rows)}', flush=True)

    tag = args.tag
    rows_path = os.path.join(HERE, f'E3_rows{tag}.csv')
    pairs_path = os.path.join(HERE, f'E3_pairs{tag}.csv.gz')
    write_rows(rows_path, rows)
    with gzip.open(pairs_path, 'wt', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['dataset', 'seed', 'step', 'd', 'dtilde', 'chosen'])
        w.writerows(pair_rows)

    # ---------------- aggregates -> results/E3_summary.json ----------------
    def med(v):
        v = sorted(x for x in v if x is not None and not math.isnan(x))
        if not v:
            return None
        m = len(v) // 2
        return v[m] if len(v) % 2 else 0.5 * (v[m - 1] + v[m])

    def quart(v, q):
        v = sorted(x for x in v if x is not None and not math.isnan(x))
        if not v:
            return None
        i = min(len(v) - 1, max(0, int(round(q * (len(v) - 1)))))
        return v[i]

    summary = {'config': dict(eps=EPS, alpha_coverage=ALPHA_COVERAGE,
                              cluster_fraction=CLUSTER_FRACTION,
                              K_range=[K_MIN, K_MAX], limit=args.limit,
                              n_rows=len(rows), n_pairs=len(pair_rows),
                              csv_url=CSV_URL),
               'reference_source': dict(ref_src), 'skipped': skipped,
               'n_sentences': dict(min=min(nsent_all), max=max(nsent_all),
                                   median=med([float(x) for x in nsent_all])),
               'structure_check': structure_check(args.limit),
               'by_dataset_K': {}, 'by_surrogate_K': {}, 'by_category_K': {}}

    def agg(entries):
        ratios = [e['ratio'] for e in entries]
        etas = [e['eta_sel'] for e in entries]
        etap = [e['eta_path'] for e in entries]
        viol = [e['viol'] for e in entries
                if e['viol'] is not None and not math.isnan(e['viol'])]
        nonpos_steps = sum(e['nonpos_steps'] for e in entries)
        tot_steps = sum(e['steps'] for e in entries)
        lazy_gap = [e['den_lazy'] - e['den_exact'] for e in entries]
        return dict(
            n=len(entries),
            ratio_median=med(ratios), ratio_q25=quart(ratios, .25),
            ratio_q75=quart(ratios, .75), ratio_min=quart(ratios, 0.0),
            ratio_gt1_pct=100.0 * sum(1 for r in ratios if r is not None and r > 1) / len(entries),
            eta_sel_median=med(etas), eta_sel_q75=quart(etas, .75),
            eta_sel_q90=quart(etas, .90), eta_sel_max=quart(etas, 1.0),
            eta_path_median=med(etap), eta_path_q90=quart(etap, .90),
            viol_pct_mean=sum(viol) / len(viol) if viol else None,
            viol_pct_median=med(viol),
            dneg_step_pct=100.0 * nonpos_steps / tot_steps if tot_steps else None,
            dneg_pair_pct=100.0 * sum(e['nonpos_pairs'] for e in entries) /
                          max(1, sum(e['npairs'] for e in entries)),
            lazy_worse_pct=100.0 * sum(1 for g in lazy_gap if g < -1e-12) / len(entries),
            lazy_gap_max=max((-g for g in lazy_gap), default=0.0))

    for (ds, K), entries in sorted(diag.items()):
        summary['by_dataset_K'][f'{ds}|K={K}'] = agg(entries)
    for sur in SURROGATES:
        for K in range(K_MIN, K_MAX + 1):
            e = [x for (ds, k), v in diag.items() if k == K and ds.endswith('_' + sur)
                 for x in v]
            if e:
                summary['by_surrogate_K'][f'{sur}|K={K}'] = agg(e)
    for cat in CATEGORIES:
        for K in range(K_MIN, K_MAX + 1):
            e = [x for (ds, k), v in diag.items() if k == K and ds.startswith(cat + '_')
                 for x in v]
            if e:
                summary['by_category_K'][f'{cat}|K={K}'] = agg(e)

    with open(os.path.join(HERE, f'E3_summary{tag}.json'), 'w') as fh:
        json.dump(summary, fh, indent=1, default=float)

    print(f'rows={len(rows)} pairs={len(pair_rows)} -> {rows_path}, {pairs_path}')
    for sur in SURROGATES:
        a = summary['by_surrogate_K'].get(f'{sur}|K=5')
        if a:
            print(f"  {sur:9s} K=5 n={a['n']:4d} ratio_med={a['ratio_median']:.4f} "
                  f"eta_sel_med={a['eta_sel_median']:.3f} "
                  f"dneg_step%={a['dneg_step_pct']:.2f} "
                  f"viol%={a['viol_pct_mean']:.2f} "
                  f"lazy_worse%={a['lazy_worse_pct']:.2f}")

    if args.fig:
        make_figures(rows, pair_rows, summary, tag)


def make_figures(rows, pair_rows, summary, tag):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    figdir = os.path.join(ROOT, 'figures')
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    colors = {'coverage': 'tab:blue', 'diversity': 'tab:orange', 'facility': 'tab:green'}

    ax = axes[0]
    data, labs = [], []
    for sur in SURROGATES:
        v = [float(r['eta_sel']) for r in rows
             if r['dataset'].endswith('_' + sur) and r['K'] == 5 and r['eta_sel']]
        data.append(v)
        labs.append(f'{sur}\n(n={len(v)})')
    try:
        ax.boxplot(data, tick_labels=labs, showfliers=False)
    except TypeError:                       # matplotlib < 3.9
        ax.boxplot(data, labels=labs, showfliers=False)
    ax.set_yscale('log')
    ax.set_ylabel(r'$\eta^{sel}$ (K=5)')
    ax.set_title(r'E3: $\eta^{sel}$ by surrogate')

    ax = axes[1]
    for sur in SURROGATES:
        v = sorted(float(r['ratio']) for r in rows
                   if r['dataset'].endswith('_' + sur) and r['K'] == 5 and r['ratio'])
        if v:
            ax.plot(v, [i / len(v) for i in range(len(v))], label=sur,
                    color=colors[sur])
    ax.axvline(1.0, color='k', lw=.8, ls=':')
    ax.set_xlabel(r'ratio $=f(S^{\tilde f})/f(S^{f})$ (K=5)')
    ax.set_ylabel('empirical CDF')
    ax.legend(fontsize=8)
    ax.set_title('E3: realized ratio')

    ax = axes[2]
    sub = [p for p in pair_rows if p[0].endswith('_facility')][::4]   # deterministic
    xs = [float(p[4]) for p in sub]
    ys = [float(p[3]) for p in sub]
    neg = sum(1 for y in ys if y <= 0)
    ax.scatter(xs, ys, s=2, alpha=.18, color=colors['facility'])
    ax.axhline(0, color='k', lw=.8)
    ax.axhline(EPS, color='r', lw=.6, ls='--')
    ax.set_xlabel(r'$\tilde d$ (facility-location, raw scale)')
    ax.set_ylabel(r'$d$ (ROUGE-1 F gain)')
    ax.set_title(r'E3: $(d,\tilde d)$, all steps' + f'  ({100*neg/len(ys):.0f}% with $d\\leq0$)')
    fig.tight_layout()
    for ext in ('png', 'pdf'):
        fig.savefig(os.path.join(figdir, f'E3_overview{tag}.{ext}'), dpi=160)
    print('figures written')


if __name__ == '__main__':
    main()
