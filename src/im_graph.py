"""Shared experiment infrastructure: graphs, one-hop coverage, lazy (CELF) greedy.

Principles (TASKS_EXP.md, apply to every experiment script):
1. NO artificial oracle perturbation anywhere (no d~ = d*exp(X)).  Every f~ must be
   computable from observable data alone, without looking at f.
2. Every f evaluation is cached (dict keyed by frozenset); greedy is lazy (CELF).
3. Reproducible: fixed seed lists, results to CSV, figures to PNG+PDF.
4. Honest reporting: sign-violation %, zero-gain handling, trimming eps all in tables.
5. CPU only; any script that would run > 30 min is first scaled down, then up.

Note (E0): the original SubModular.ipynb is MISSING from the repository (recorded in
data/INVENTORY.md), so this module is written fresh rather than extracted from it.
Per TASKS_EXP.md, the R-step and error-oracle code of the old notebook is NOT
reproduced here.
"""
import heapq
import random


class Graph:
    """Edge-list graph; directed or undirected.  Nodes are ints 0..n-1 after
    compaction.  out[v] = set of neighbours reachable from v (for undirected
    graphs both directions are present)."""

    def __init__(self, edges, directed):
        self.directed = directed
        ids = {}
        out = []
        for u, v in edges:
            for w in (u, v):
                if w not in ids:
                    ids[w] = len(ids)
                    out.append(set())
            a, b = ids[u], ids[v]
            if a != b:
                out[a].add(b)
                if not directed:
                    out[b].add(a)
        self.ids = ids
        self.out = out
        self.n = len(out)
        self.m_input = len(edges)

    @classmethod
    def from_file(cls, path, directed, sep=None, skip_header=False):
        edges = []
        with open(path) as fh:
            for i, line in enumerate(fh):
                if skip_header and i == 0:
                    continue
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(sep) if sep else line.split()
                if sep == ',' and len(parts) < 2:
                    parts = line.split()
                edges.append((parts[0], parts[1]))
        return cls(edges, directed)

    def edge_subsample(self, p, seed):
        """Observed graph: keep each INPUT edge independently with prob p.
        For undirected graphs each undirected edge is kept/dropped as a whole."""
        rng = random.Random(seed)
        out = [set() for _ in range(self.n)]
        seen = set()
        for a in range(self.n):
            for b in self.out[a]:
                key = (a, b) if self.directed else (min(a, b), max(a, b))
                if key in seen:
                    continue
                seen.add(key)
                if rng.random() < p:
                    out[a].add(b)
                    if not self.directed:
                        out[b].add(a)
        g = object.__new__(Graph)
        g.directed = self.directed
        g.ids = self.ids
        g.out = out
        g.n = self.n
        g.m_input = sum(len(s) for s in out) // (1 if self.directed else 2)
        return g

    def coverage(self, S):
        """One-hop coverage |{v : v in S or v pointed to by some s in S}|."""
        cov = set(S)
        for s in S:
            cov |= self.out[s]
        return len(cov)


class CachedSetFunction:
    """Wrap value_fn(frozenset) -> float with a cache; counts evaluations."""

    def __init__(self, value_fn):
        self.fn = value_fn
        self.cache = {}
        self.evals = 0

    def __call__(self, S):
        key = frozenset(S)
        if key not in self.cache:
            self.cache[key] = self.fn(key)
            self.evals += 1
        return self.cache[key]

    def gain(self, S, e):
        base = frozenset(S)
        return self(base | {e}) - self(base)


def lazy_greedy(F, ground, K, tie_key=None, record=None, quantize=None):
    """CELF lazy greedy on cached set function F over `ground`, budget K.

    Returns list of picked elements (trajectory order).  Correctness of laziness
    requires F submodular; for the non-submodular objectives used in the
    experiments we still use CELF but re-validate the popped candidate against
    the runner-up (standard practice; exactness is then heuristic and any use on
    a non-submodular f must be noted in the calling script).

    record: optional callback record(t, S_before, chosen, gain_chosen) invoked
    per step, for trajectory statistics.
    tie_key: secondary sort key for equal gains (default: element order).
    quantize: if set (int d), gains are rounded to d decimals BEFORE heap
    comparison, so exact mathematical ties are not flipped by ~1e-16 float
    noise and tie_key decides them (needed for the adversarial-tie worst-case
    instances of E4; leave None for real-data tasks).
    """
    q_ = (lambda g: round(g, quantize)) if quantize is not None else (lambda g: g)
    S = []
    Sset = set()
    pq = []
    for e in ground:
        g = F.gain(Sset, e)
        pq.append((-q_(g), tie_key(e) if tie_key else e, e))
    heapq.heapify(pq)
    stale = {e: 0 for e in ground}
    rnd = 1
    while len(S) < K and pq:
        negg, tk, e = heapq.heappop(pq)
        if e in Sset:
            continue
        if stale[e] == rnd:
            S.append(e)
            Sset.add(e)
            if record is not None:
                record(len(S) - 1, Sset - {e}, e, -negg)
            rnd += 1
        else:
            g = F.gain(Sset, e)
            stale[e] = rnd
            heapq.heappush(pq, (-q_(g), tk, e))
    return S


def true_max_gain(F_true, Sset, ground):
    """max_e d_e(S) on the true function (for eta^sel); plain scan with cache."""
    best = None
    for e in ground:
        if e in Sset:
            continue
        g = F_true.gain(Sset, e)
        if best is None or g > best:
            best = g
    return best
