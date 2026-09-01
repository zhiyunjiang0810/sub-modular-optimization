"""F1.1  Cross-check the self-implemented ROUGE-1 F of E3_run.py against the
reference implementation `rouge_score` (Google, pip package rouge-score).

Design
------
* 30 articles per BBC category (business / sport / tech), the same articles and
  the same reference summaries that E3_run.py uses (results/E3_run.py helpers
  are imported, nothing is re-implemented here).
* For every article a FIXED collection of candidate summaries is built (the same
  set is scored by both implementations):
    - the first min(n, 10) singleton sentences,
    - the prefixes [s_0..s_{K-1}] for K = 1..5,
    - the greedy-on-f prefixes for K = 1..5 (greedy computed with the E3
      implementation; the SUBSETS are what matters, not who produced them).
* Both implementations score the SAME (candidate text, reference text) pair:
    ours  = E3_run.Rouge1F(...)( S )                      (set-based)
    theirs= rouge_scorer.RougeScorer(['rouge1'], use_stemmer=False)
              .score(reference, ' '.join(selected sentences))['rouge1'].fmeasure

`rouge_score` must be importable; it is installed in a virtualenv, so run this
with that interpreter:

  <venv>/bin/python results/F1_rouge_check.py            # writes F1_rouge_check.json
  python3 results/F1_rouge_check.py --json-only          # (needs rouge_score too)

Output: results/F1_rouge_check.json (per-article max/mean abs diff, worst cases,
token-level diagnostics), consumed by results/F1_rouge_check.md.
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'src'))

import E3_run as E3                                          # noqa: E402
from rouge_score import rouge_scorer, tokenize as rs_tokenize  # noqa: E402
from im_graph import CachedSetFunction, lazy_greedy          # noqa: E402

N_PER_CAT = 30


def candidate_subsets(n, picks_true):
    subs = []
    for i in range(min(n, 10)):
        subs.append((i,))
    for K in range(1, 6):
        if K <= n:
            subs.append(tuple(range(K)))
        if K <= len(picks_true):
            subs.append(tuple(sorted(picks_true[:K])))
    out, seen = [], set()
    for s in subs:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=N_PER_CAT)
    args = ap.parse_args()

    scorer = rouge_scorer.RougeScorer(['rouge1'], use_stemmer=False)
    csv_idx = E3.load_references()
    notes = collections.Counter()

    recs = []
    per_article = []
    tok_stats = collections.Counter()
    for cat in E3.CATEGORIES:
        used = 0
        num = 0
        while used < args.limit:
            num += 1
            if num > 400:
                break
            fname = f'{num:03d}.txt'
            apath = os.path.join(E3.BBC, 'News Articles', cat, fname)
            if not os.path.exists(apath):
                continue
            art, _ = E3.read_text(apath)
            ref, src = E3.get_reference(cat, fname, art, csv_idx, notes)
            if ref is None:
                continue
            sents = E3.split_sentences(art)
            n = len(sents)
            if n < 5:
                continue
            used += 1

            sent_counts = [collections.Counter(E3.tokens(s)) for s in sents]
            sent_len = [sum(c.values()) for c in sent_counts]
            ref_counts = collections.Counter(E3.tokens(ref))
            ref_len = sum(ref_counts.values())
            F = CachedSetFunction(E3.Rouge1F(sent_counts, sent_len,
                                             ref_counts, ref_len))
            Kmax = min(5, n - 2)
            picks_true = lazy_greedy(F, list(range(n)), max(Kmax, 1), quantize=None)

            # token-level diagnostics on the reference and the whole article
            ours_ref = E3.tokens(ref)
            theirs_ref = rs_tokenize.tokenize(ref, None)
            tok_stats['ref_len_ours'] += len(ours_ref)
            tok_stats['ref_len_theirs'] += len(theirs_ref)
            if ours_ref != theirs_ref:
                tok_stats['ref_token_mismatch_articles'] += 1

            diffs = []
            for S in candidate_subsets(n, picks_true):
                ours = F(set(S))
                cand_text = ' '.join(sents[i] for i in S)
                theirs = scorer.score(ref, cand_text)['rouge1'].fmeasure
                d = abs(ours - theirs)
                diffs.append(d)
                recs.append(dict(cat=cat, article=num, S=list(S),
                                 ours=ours, theirs=theirs, absdiff=d))
            per_article.append(dict(cat=cat, article=num, n_sent=n,
                                    ref_src=src, n_subsets=len(diffs),
                                    max_absdiff=max(diffs),
                                    mean_absdiff=sum(diffs) / len(diffs),
                                    ref_tokens_ours=len(ours_ref),
                                    ref_tokens_theirs=len(theirs_ref)))
        print(f'[{cat}] {used} articles compared', flush=True)

    alld = [r['absdiff'] for r in recs]
    worst = sorted(recs, key=lambda r: -r['absdiff'])[:15]
    n_gt = sum(1 for d in alld if d > 1e-6)
    summary = dict(
        n_articles=len(per_article), n_comparisons=len(alld),
        max_absdiff=max(alld), mean_absdiff=sum(alld) / len(alld),
        median_absdiff=sorted(alld)[len(alld) // 2],
        n_comparisons_gt_1e_6=n_gt,
        frac_comparisons_gt_1e_6=n_gt / len(alld),
        n_articles_with_any_gt_1e_6=sum(1 for a in per_article
                                        if a['max_absdiff'] > 1e-6),
        ref_token_mismatch_articles=tok_stats['ref_token_mismatch_articles'],
        ref_tokens_ours_total=tok_stats['ref_len_ours'],
        ref_tokens_theirs_total=tok_stats['ref_len_theirs'],
        worst=worst, per_article=per_article)
    out = os.path.join(HERE, 'F1_rouge_check.json')
    with open(out, 'w') as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ('worst', 'per_article')}, indent=1))
    print('worst 5:', json.dumps(worst[:5], indent=1))
    print('wrote', out)


if __name__ == '__main__':
    main()
