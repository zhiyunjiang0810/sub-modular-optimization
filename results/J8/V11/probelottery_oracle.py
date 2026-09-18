#!/usr/bin/env python3
"""V11 Q9 oracle for the J8 ProbeLottery proposition (TASKS11 Q9).

Statement under test (results/V11/inputs/statement_probelottery.md):

    Proposition (ProbeLottery).  Let K = 2 and eta = 3/2.  There is a randomized
    algorithm, ProbeLottery, that makes at most 9n queries to ftilde, each on a
    set of size at most 5, outputs a set of size 2, and satisfies on every
    instance (f, ftilde) with f monotone submodular, f(empty) = 0, and ftilde of
    error at most eta = 3/2 (Definition 1, any split with eta_u eta_o = 3/2):

        E[f(T)] >= (3/5 + 1/400000) OPT,

    the expectation over the algorithm's own randomness only.

Route one (a proof to check line by line) does NOT exist in this repository:
the proof file results/J8/probe_lottery.md carrying the inequalities (3) and
(8)-(12) was never delivered.  The only route-one material present is
results/J8/J8_claude_spotcheck.py (the algorithm as implemented, the tight
instance value 3/5 + 1/2048, 400 random coverage instances) and section 4 of
HANDOFF_2026-09-18 (the statement).  The LP dual certificates for (3) and
(8)-(12) therefore cannot be produced here; the item is recorded as GAP, see
check G1 below.  Nothing in this file verifies the proposition itself: finite
instance families can only refute it.

This script implements ProbeLottery from the algorithm description in the
statement file alone.  results/J8/J8_claude_spotcheck.py is neither imported
nor copied; it is rerun as a separate process in check C5 and its numbers are
compared with the numbers produced here.

Criterion C (oracle)
  C1  tight instance: the K = 2, eta = 3/2 double-residual family (j = 1) with
      the B elements first in the tie order, n in {6, 8, 12, 20}.  Expected
      value exactly 3/5 + 1/2048, at most 9n queries, maximum queried size 5.
      Instance legality (f monotone submodular, band eta_u eta_o <= 3/2) is
      checked exactly on the count grid for every n and, in addition, on the
      full 2^n lattice for n = 6 and n = 8.            [VERIFIED-EXHAUSTIVE]
  C2  >= 2000 random legal instances, K = 2, eta = 3/2, n in 8..12, three
      families (weighted coverage plus a half sub-universe residual; modular
      with per-element factors in [1, 3/2]; mixtures with band-consistent
      dominated perturbations).  Legality (monotone, submodular, band) is
      verified exhaustively on the full 2^n lattice in exact integers, then
      E[f(T)] is computed exactly from the output distribution and compared
      with (3/5 + 1/400000) OPT.  Query count and queried size checked on
      every run.                                        [VERIFIED-EXHAUSTIVE]
  C3  structured cases: eta = 1 (ftilde = f) at the smallest legal n (4 and 5);
      the tight instance at n = 6..12; the two instance families used by
      results/E4_worst_instances.py, rebuilt exactly in Fractions at their
      K = 2, eta = 3/2 members (V_j family of results/N2_check.py for
      j = 0, 1, 2, uncapped variant; U_K family of
      code/check_explicit_instance.py at ahat = 5/4).   [VERIFIED-EXHAUSTIVE]
  C4  algorithm-contract checks on every run of C1-C3 and D2: output sets have
      size 2, the output distribution has total mass 1, at most 9n queries,
      queried sets of size at most 5.                   [VERIFIED-EXHAUSTIVE]
  C5  rerun results/J8/J8_claude_spotcheck.py in a subprocess, record its exit
      code and key numbers, and compare them with this script's own numbers on
      the same tight instances.                         [VERIFIED-EXHAUSTIVE]
  G1  LP dual certificates for the inequalities (3), (8)-(12) of the
      undelivered proof: GAP, the proof file does not exist.

Criterion D (counterexample search on the statement itself)
  D1  the random instances of C2 are the search: violations and worst ratio.
  D2  local search: 5 restarts x 100 accepted steps (500 evaluated
      perturbations) on the tight instance, perturbing the two residual
      sequences, the two band multipliers and, in the generic half, every grid
      value, each time re-checking legality exactly and taking the worst tie
      order out of four.  Worst ratio and its instance are reported.

House rules: exact arithmetic for every decision (fractions.Fraction on the
count grid and on the output distribution; exact int64 lattice arithmetic with
an explicit overflow guard for the random families).  Floats appear only in
printouts.  No existing repository file is modified; no git command is run.

Usage:  python3 results/V11/oracle/probelottery.py
Exit code 0 iff every check passed (a GAP is not a failure).
"""

import json
import os
import random
import subprocess
import sys
import time
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir, os.pardir))

EPS = Fr(1, 10000)                       # the pool threshold of the algorithm
TARGET = Fr(3, 5) + Fr(1, 400000)        # the claimed bound
TIGHT_VALUE = Fr(3, 5) + Fr(1, 2048)     # the claimed value on the tight family
ETA = Fr(3, 2)
K = 2

SEEDS = {
    'C2_coverage': 20260901,
    'C2_modular': 20260902,
    'C2_mixture': 20260903,
    'C3_eta1_n4': 20260904,
    'C3_eta1_n5': 20260905,
    'D2_local': 20260906,
}

RESULTS = []      # (name, status, detail)
COUNTS = {}
WITNESSES = []
LOGLINES = []


def say(msg=''):
    print(msg, flush=True)
    LOGLINES.append(msg)


def rec(name, status, detail):
    RESULTS.append((name, status, detail))
    say(f'[{status}] {name}: {detail}')


# ---------------------------------------------------------------------------
# 1. ProbeLottery, implemented from statement_probelottery.md only.
# ---------------------------------------------------------------------------
class CountingOracle:
    """Caches queries, counts distinct queried sets, tracks the largest one."""

    def __init__(self, fun):
        self.fun = fun
        self.cache = {}
        self.queries = 0
        self.maxsize = 0

    def __call__(self, elems):
        key = frozenset(elems)
        hit = self.cache.get(key, None)
        if hit is None:
            hit = self.fun(key)
            self.cache[key] = hit
            self.queries += 1
            if len(key) > self.maxsize:
                self.maxsize = len(key)
        return hit


def first_argmax(items, value):
    """argmax returning the FIRST maximiser in the given order."""
    best, bestval = None, None
    for it in items:
        v = value(it)
        if bestval is None or v > bestval:
            best, bestval = it, v
    return best, bestval


def probe_lottery(order, gfun):
    """ProbeLottery, steps 1-5 of statement_probelottery.md.

    order : ground set as a list, fixed tie-break order.
    gfun  : the surrogate, called on a frozenset.
    Returns (distribution, queries, maxsize, anchors).
    """
    g = CountingOracle(gfun)

    # 1. singletons
    b, M = first_argmax(order, lambda e: g([e]))

    # 2. pairs containing b
    rest_of_b = [e for e in order if e != b]
    c, p = first_argmax(rest_of_b, lambda e: g([b, e]))
    P0 = frozenset((b, c))

    # 3. pool
    pool = [e for e in rest_of_b
            if g([e]) >= M - EPS * M and g([b, e]) >= p - EPS * M]

    # 4. extensions, at most four rounds, so |anchors| <= 5
    anchors = [b]
    secondary = []
    for _ in range(4):
        avail = [e for e in pool if e not in anchors]
        if not avail:
            break
        v, _ = first_argmax(avail, lambda e: g(anchors + [e]))
        anchors.append(v)
        zv, _ = first_argmax([z for z in order if z != v], lambda z: g([v, z]))
        secondary.append(frozenset((v, zv)))
        secondary.append(frozenset((b, v)))
    while len(secondary) < 8:
        secondary.append(P0)

    # 5. output distribution
    dist = {}
    dist[P0] = dist.get(P0, Fr(0)) + Fr(127, 128)
    for T in secondary:
        dist[T] = dist.get(T, Fr(0)) + Fr(1, 1024)
    return dist, g.queries, g.maxsize, anchors


def contract_ok(dist, queries, maxsize, n):
    """C4: mass one, output sets of size 2, <= 9n queries, queried size <= 5."""
    problems = []
    if sum(dist.values()) != 1:
        problems.append(f'total mass {sum(dist.values())}')
    for T in dist:
        if len(T) != 2:
            problems.append(f'output set {sorted(T)} of size {len(T)}')
    if queries > 9 * n:
        problems.append(f'{queries} queries > 9n = {9 * n}')
    if maxsize > 5:
        problems.append(f'queried size {maxsize} > 5')
    return problems


# ---------------------------------------------------------------------------
# 2. Count-grid instances (x = |S n B|, y = |S n O|, |O| = K = 2) in Fractions.
# ---------------------------------------------------------------------------
class CountGrid:
    """f(S) = Fg[x][y], ftilde(S) = Hg[x][y] with x = |S n B|, y = |S n O|."""

    def __init__(self, nb, Fg, Hg, label=''):
        self.nb = nb                 # number of B elements; n = nb + 2
        self.n = nb + 2
        self.F = Fg                  # dict (x, y) -> Fraction, 0 <= x <= nb, 0 <= y <= 2
        self.H = Hg
        self.label = label

    def counts(self, S):
        y = sum(1 for e in S if e >= self.nb)
        return len(S) - y, y

    def fset(self, S):
        x, y = self.counts(S)
        return self.F[(x, y)]

    def hset(self, S):
        x, y = self.counts(S)
        return self.H[(x, y)]

    def opt(self):
        return max(self.F[(2, 0)], self.F[(1, 1)], self.F[(0, 2)])

    def legality(self):
        """Exact legality on the grid.  For a function of the two counts the
        grid conditions are necessary and sufficient for monotone submodular,
        and the gains of the two parts are grid differences, so the band is a
        grid condition too.  Returns (problems, eta_u, eta_o)."""
        bad = []
        nb, F, H = self.nb, self.F, self.H
        if F[(0, 0)] != 0:
            bad.append('f(empty) != 0')
        if H[(0, 0)] != 0:
            bad.append('ftilde(empty) != 0')
        dxF = {(x, y): F[(x + 1, y)] - F[(x, y)]
               for x in range(nb) for y in range(3)}
        dyF = {(x, y): F[(x, y + 1)] - F[(x, y)]
               for x in range(nb + 1) for y in range(2)}
        dxH = {(x, y): H[(x + 1, y)] - H[(x, y)]
               for x in range(nb) for y in range(3)}
        dyH = {(x, y): H[(x, y + 1)] - H[(x, y)]
               for x in range(nb + 1) for y in range(2)}
        for key, d in list(dxF.items()) + list(dyF.items()):
            if d < 0:
                bad.append(f'f not monotone at {key}')
        # submodularity: both gains non-increasing in both coordinates
        for x in range(nb):
            for y in range(3):
                if x + 1 < nb and dxF[(x, y)] < dxF[(x + 1, y)]:
                    bad.append(f'dxF increasing in x at {(x, y)}')
                if y + 1 < 3 and dxF[(x, y)] < dxF[(x, y + 1)]:
                    bad.append(f'dxF increasing in y at {(x, y)}')
        for x in range(nb + 1):
            for y in range(2):
                if x < nb and dyF[(x, y)] < dyF[(x + 1, y)]:
                    bad.append(f'dyF increasing in x at {(x, y)}')
                if y + 1 < 2 and dyF[(x, y)] < dyF[(x, y + 1)]:
                    bad.append(f'dyF increasing in y at {(x, y)}')
        # band: actual (eta_u, eta_o) over all grid differences
        eta_u = Fr(1)
        eta_o = Fr(1)
        for dF, dH in ((dxF, dxH), (dyF, dyH)):
            for key in dF:
                d, dt = dF[key], dH[key]
                if dt < 0:
                    bad.append(f'negative predicted gain at {key}')
                    continue
                if d == 0:
                    if dt != 0:
                        bad.append(f'zero true gain with nonzero prediction at {key}')
                    continue
                if dt == 0:
                    bad.append(f'zero prediction with positive true gain at {key}')
                    continue
                eta_u = max(eta_u, d / dt)
                eta_o = max(eta_o, dt / d)
        if eta_u * eta_o > ETA:
            bad.append(f'eta_u eta_o = {eta_u * eta_o} > 3/2')
        return bad, eta_u, eta_o

    def lattice_legality(self):
        """The same check done element by element on the full 2^n lattice,
        used as a cross-check of the grid criterion for small n."""
        bad = []
        n = self.n
        elems = list(range(n))
        subsets = []
        for m in range(1 << n):
            subsets.append(frozenset(e for e in elems if (m >> e) & 1))
        eta_u = Fr(1)
        eta_o = Fr(1)
        for S in subsets:
            for e in elems:
                if e in S:
                    continue
                Se = S | {e}
                d = self.fset(Se) - self.fset(S)
                dt = self.hset(Se) - self.hset(S)
                if d < 0:
                    bad.append(f'not monotone at ({sorted(S)}, {e})')
                if d == 0 and dt != 0:
                    bad.append(f'zero gain, nonzero prediction at ({sorted(S)}, {e})')
                if d > 0:
                    if dt <= 0:
                        bad.append(f'nonpositive prediction at ({sorted(S)}, {e})')
                    else:
                        eta_u = max(eta_u, d / dt)
                        eta_o = max(eta_o, dt / d)
                for e2 in elems:
                    if e2 == e or e2 in S:
                        continue
                    d2 = self.fset(Se | {e2}) - self.fset(S | {e2})
                    if d2 > d:
                        bad.append(f'not submodular at ({sorted(S)}, {e}, {e2})')
        if eta_u * eta_o > ETA:
            bad.append(f'lattice eta_u eta_o = {eta_u * eta_o} > 3/2')
        return bad, eta_u, eta_o

    def run(self, order):
        dist, q, ms, anchors = probe_lottery(order, self.hset)
        ev = sum(pr * self.fset(T) for T, pr in dist.items())
        return dist, q, ms, anchors, ev


def tight_grid(n):
    """The K = 2, eta = 3/2 double-residual family, j = 1, of the statement."""
    k1 = (K - 1) * ETA + 1                  # 5/2
    q = (K - 1) * ETA / k1                  # 3/5
    j = 1
    Q = q ** j                              # 3/5
    delta = Q / (K * ETA)                   # 1/5
    C = k1 / K                              # 5/4
    nb = n - 2

    def r(x):
        return q ** x if x <= j else max(Fr(0), Q - (x - j) * delta)

    def h(x):
        return Fr(K - 1, K) * q ** x if x <= j else \
            max(Fr(0), Fr(K - 1, K) * Q - (x - j) * delta)

    Fg, Hg = {}, {}
    for x in range(nb + 1):
        rx, hx = r(x), h(x)
        Fg[(x, 0)] = 1 - rx
        Fg[(x, 1)] = 1 - hx
        Fg[(x, 2)] = Fr(1)
        Hg[(x, 0)] = C - rx - (ETA - 1) * hx
        Hg[(x, 1)] = C - ETA * hx
        Hg[(x, 2)] = C
    return CountGrid(nb, Fg, Hg, label=f'tight_n{n}')


# ---------------------------------------------------------------------------
# 3. Lattice instances in exact integers (random families of C2 and C3).
# ---------------------------------------------------------------------------
OVERFLOW_GUARD = 1 << 40


class LatticeInstance:
    """f and 2*ftilde as exact int64 arrays over 2^n subsets, same scaling."""

    def __init__(self, n, f, h, label=''):
        self.n = n
        self.f = f                       # int64, the objective (scaled)
        self.h = h                       # int64, the surrogate in the same scale
        self.label = label
        if max(int(np.max(np.abs(f))), int(np.max(np.abs(h)))) >= OVERFLOW_GUARD:
            raise AssertionError('overflow guard: lattice values too large')

    def fset(self, S):
        m = 0
        for e in S:
            m |= 1 << e
        return int(self.f[m])

    def hset(self, S):
        m = 0
        for e in S:
            m |= 1 << e
        return int(self.h[m])

    def opt(self):
        best = 0
        for a in range(self.n):
            for b in range(a + 1, self.n):
                best = max(best, int(self.f[(1 << a) | (1 << b)]))
        return best

    def legality_eta_u_one(self):
        """Exhaustive over the 2^n lattice, exact integers.  Checks f monotone
        submodular and the band in the rescaled split (eta_u, eta_o) = (1, 3/2),
        which is the form the statement writes: d <= dtilde <= (3/2) d."""
        bad = []
        n, f, h = self.n, self.f, self.h
        idx = np.arange(1 << n, dtype=np.int64)
        for e in range(n):
            S = idx[((idx >> e) & 1) == 0]
            df = f[S | (1 << e)] - f[S]
            dh = h[S | (1 << e)] - h[S]
            if np.any(df < 0):
                bad.append(f'f not monotone in element {e}')
            if np.any(dh < df):
                bad.append(f'band lower side broken at element {e}')
            if np.any(2 * dh > 3 * df):
                bad.append(f'band upper side broken at element {e}')
            for e2 in range(n):
                if e2 == e:
                    continue
                T = idx[(((idx >> e) & 1) == 0) & (((idx >> e2) & 1) == 0)]
                d1 = f[T | (1 << e)] - f[T]
                d2 = f[T | (1 << e) | (1 << e2)] - f[T | (1 << e2)]
                if np.any(d1 < d2):
                    bad.append(f'f not submodular in ({e}, {e2})')
        return bad

    def run(self, order):
        dist, q, ms, anchors = probe_lottery(order, self.hset)
        ev = sum(pr * Fr(self.fset(T)) for T, pr in dist.items())
        return dist, q, ms, anchors, ev


def coverage_values(n, cov, wval):
    """f over all subsets from per-element coverage masks, by subset DP."""
    covmask = np.zeros(1 << n, dtype=np.int64)
    for m in range(1, 1 << n):
        low = m & (-m)
        e = low.bit_length() - 1
        covmask[m] = covmask[m ^ low] | cov[e]
    return wval[covmask]


def universe_weight_table(usize, w):
    tab = np.zeros(1 << usize, dtype=np.int64)
    for m in range(1, 1 << usize):
        low = m & (-m)
        u = low.bit_length() - 1
        tab[m] = tab[m ^ low] + w[u]
    return tab


def modular_values(n, wts):
    vals = np.zeros(1 << n, dtype=np.int64)
    for m in range(1, 1 << n):
        low = m & (-m)
        e = low.bit_length() - 1
        vals[m] = vals[m ^ low] + wts[e]
    return vals


def random_coverage_instance(rng, n):
    """Family 1: f weighted coverage, ftilde = f + f2/2 with f2 the coverage
    restricted to a random sub-universe.  Then d <= dtilde <= (3/2) d."""
    usize = rng.randint(6, 14)
    w = [rng.randint(1, 9) for _ in range(usize)]
    cov = []
    for _ in range(n):
        k = rng.randint(1, max(1, usize // 2))
        bits = rng.sample(range(usize), k)
        m = 0
        for u in bits:
            m |= 1 << u
        cov.append(m)
    sub = set(rng.sample(range(usize), usize // 2))
    w2 = [w[u] if u in sub else 0 for u in range(usize)]
    tab, tab2 = universe_weight_table(usize, w), universe_weight_table(usize, w2)
    fv = coverage_values(n, cov, tab)
    f2 = coverage_values(n, cov, tab2)
    return LatticeInstance(n, 2 * fv, 2 * fv + f2, label='coverage')


def random_modular_instance(rng, n, m=12):
    """Family 2: f modular, ftilde with per-element factors (2m + a)/(2m)
    in [1, 3/2] for 0 <= a <= m, all rational."""
    w = [rng.randint(1, 9) for _ in range(n)]
    a = [rng.randint(0, m) for _ in range(n)]
    base = modular_values(n, [2 * m * wi for wi in w])
    pred = modular_values(n, [(2 * m + ai) * wi for wi, ai in zip(w, a)])
    return LatticeInstance(n, 2 * base, 2 * pred, label='modular')


def random_mixture_instance(rng, n):
    """Family 3: f = weighted coverage + modular, ftilde = f + g/2 with g a
    band-consistent dominated perturbation (same coverage sets with smaller
    weights, plus a smaller modular part), so 0 <= dg <= df everywhere."""
    usize = rng.randint(6, 12)
    w = [rng.randint(1, 9) for _ in range(usize)]
    wp = [rng.randint(0, wi) for wi in w]
    cov = []
    for _ in range(n):
        k = rng.randint(1, max(1, usize // 2))
        bits = rng.sample(range(usize), k)
        mm = 0
        for u in bits:
            mm |= 1 << u
        cov.append(mm)
    v = [rng.randint(0, 6) for _ in range(n)]
    vp = [rng.randint(0, vi) if vi > 0 else 0 for vi in v]
    fv = coverage_values(n, cov, universe_weight_table(usize, w)) + \
        modular_values(n, v)
    gv = coverage_values(n, cov, universe_weight_table(usize, wp)) + \
        modular_values(n, vp)
    return LatticeInstance(n, 2 * fv, 2 * fv + gv, label='mixture')


def random_eta_one_instance(rng, n):
    """eta = 1: ftilde = f, f a random weighted coverage plus modular."""
    usize = rng.randint(4, 10)
    w = [rng.randint(1, 9) for _ in range(usize)]
    cov = []
    for _ in range(n):
        k = rng.randint(1, max(1, usize // 2))
        bits = rng.sample(range(usize), k)
        mm = 0
        for u in bits:
            mm |= 1 << u
        cov.append(mm)
    v = [rng.randint(0, 5) for _ in range(n)]
    fv = coverage_values(n, cov, universe_weight_table(usize, w)) + \
        modular_values(n, v)
    return LatticeInstance(n, 2 * fv, 2 * fv, label='eta1')


# ---------------------------------------------------------------------------
# 4. The two families used by results/E4_worst_instances.py, K = 2, eta = 3/2,
#    rebuilt exactly in Fractions (the repository versions run in floats and
#    only at K in {3, 5, 8}; they are cited, not imported, and not modified).
# ---------------------------------------------------------------------------
class PartitionInstance:
    """f, ftilde given by closed forms in the counts of a three-part ground
    set.  parts: list of (size, name).  value: callable(counts) -> Fraction."""

    def __init__(self, sizes, fval, hval, label=''):
        self.sizes = sizes
        self.n = sum(sizes)
        self.fval = fval
        self.hval = hval
        self.label = label
        self.part = []
        for i, s in enumerate(sizes):
            self.part += [i] * s

    def counts(self, S):
        c = [0] * len(self.sizes)
        for e in S:
            c[self.part[e]] += 1
        return tuple(c)

    def fset(self, S):
        return self.fval(self.counts(S))

    def hset(self, S):
        return self.hval(self.counts(S))

    def opt(self):
        best = Fr(0)
        for a in range(self.n):
            for b in range(a + 1, self.n):
                best = max(best, self.fset(frozenset((a, b))))
        return best

    def lattice_legality(self):
        bad = []
        elems = list(range(self.n))
        eta_u = eta_o = Fr(1)
        for m in range(1 << self.n):
            S = frozenset(e for e in elems if (m >> e) & 1)
            for e in elems:
                if e in S:
                    continue
                Se = S | {e}
                d = self.fset(Se) - self.fset(S)
                dt = self.hset(Se) - self.hset(S)
                if d < 0:
                    bad.append(f'not monotone at ({sorted(S)}, {e})')
                if d == 0 and dt != 0:
                    bad.append(f'zero gain nonzero prediction ({sorted(S)}, {e})')
                if d > 0:
                    if dt <= 0:
                        bad.append(f'nonpositive prediction ({sorted(S)}, {e})')
                    else:
                        eta_u = max(eta_u, d / dt)
                        eta_o = max(eta_o, dt / d)
                for e2 in elems:
                    if e2 == e or e2 in S:
                        continue
                    if self.fset(Se | {e2}) - self.fset(S | {e2}) > d:
                        bad.append(f'not submodular ({sorted(S)}, {e}, {e2})')
        if eta_u * eta_o > ETA:
            bad.append(f'eta_u eta_o = {eta_u * eta_o} > 3/2')
        return bad, eta_u, eta_o

    def run(self, order):
        dist, q, ms, anchors = probe_lottery(order, self.hset)
        ev = sum(pr * self.fset(T) for T, pr in dist.items())
        return dist, q, ms, anchors, ev


def vj_instance(j):
    """V_j family of results/N2_check.py (uncapped variant), K = 2, eta = 3/2,
    split (eta_u, eta_o) = (1, 3/2).  Ground set C (size j), P (size K-j),
    O (size K); f = 1 - q^x (1 - y/K) + z delta, ftilde = W(0) - q^x W(y)
    + z dtil."""
    eta_u, eta_o = Fr(1), ETA
    k1 = (K - 1) * ETA + 1
    q = (K - 1) * ETA / k1
    delta = q ** j / (K * ETA)
    dtil = eta_o * delta
    W = {0: k1 / (K * eta_u)}
    for y in range(1, K + 1):
        W[y] = Fr(K - y, K) * eta_o

    def fval(c):
        x, z, y = c
        return 1 - q ** x * (1 - Fr(y, K)) + z * delta

    def hval(c):
        x, z, y = c
        return W[0] - q ** x * W[y] + z * dtil

    return PartitionInstance((j, K - j, K), fval, hval, label=f'V_{j}')


def uk_instance(ahat=Fr(5, 4)):
    """U_K family of code/check_explicit_instance.py at K = 2, ahat = 5/4,
    whose all-pairs error is (ahat K - 1)/(K - 1) = 3/2."""
    a = 1 - Fr(1, 1) / (ahat * K)

    def fval(c):
        x, y = c
        return 1 - a ** x * (1 - Fr(y, K))

    def hval(c):
        x, y = c
        if y == 0:
            return 1 - a ** x
        return 1 - a ** x + a ** x * ((1 - a) + (y - 1) * a / (K - 1))

    return PartitionInstance((K, K), fval, hval, label='U_2')


# ---------------------------------------------------------------------------
# C1 + C3(tight): the tight family.
# ---------------------------------------------------------------------------
def check_tight():
    say('\n=== C1 / C3: tight K = 2, eta = 3/2 double-residual family (j = 1) ===')
    rows = []
    problems = []
    for n in [6, 7, 8, 9, 10, 11, 12, 20]:
        inst = tight_grid(n)
        bad, eu, eo = inst.legality()
        if bad:
            problems.append(f'n={n} grid legality: {bad[:3]}')
        order = list(range(n))          # B elements first, then the two O elements
        dist, q, ms, anchors, ev = inst.run(order)
        problems += [f'n={n}: {p}' for p in contract_ok(dist, q, ms, n)]
        opt = inst.opt()
        ratio = ev / opt
        if ev != TIGHT_VALUE or opt != 1:
            problems.append(f'n={n}: E[f(T)] = {ev}, OPT = {opt}, expected '
                            f'{TIGHT_VALUE} and 1')
        if ratio < TARGET:
            problems.append(f'n={n}: ratio {ratio} < target {TARGET}')
            WITNESSES.append({'check': 'C1', 'n': n, 'ratio': str(ratio)})
        rows.append({'n': n, 'E': str(ev), 'OPT': str(opt), 'ratio': str(ratio),
                     'ratio_minus_3_5': str(ratio - Fr(3, 5)),
                     'queries': q, 'bound_9n': 9 * n, 'maxsize': ms,
                     'anchors': anchors, 'eta_u': str(eu), 'eta_o': str(eo)})
        say(f'  n={n:2d}: E[f(T)]={ev} = 3/5 + {ev - Fr(3, 5)}  OPT={opt}  '
            f'queries={q} <= {9 * n}  maxsize={ms}  anchors={anchors}  '
            f'(eta_u,eta_o)=({eu},{eo})')
    # cross-check the grid criterion against the full lattice for n = 6, 8
    for n in (6, 8):
        bad, eu, eo = tight_grid(n).lattice_legality()
        if bad:
            problems.append(f'n={n} lattice legality: {bad[:3]}')
        say(f'  full 2^{n} lattice legality: {"ok" if not bad else bad[:3]}, '
            f'actual (eta_u, eta_o) = ({eu}, {eo}), product {eu * eo}')
    COUNTS['C1_n_values'] = len(rows)
    COUNTS['C1_tight_runs'] = len(rows)
    return rows, problems


# ---------------------------------------------------------------------------
# C2 / D1: random legal instances.
# ---------------------------------------------------------------------------
def check_random():
    say('\n=== C2 / D1: random legal instances, K = 2, eta = 3/2, n = 8..12 ===')
    plan = [('coverage', random_coverage_instance, SEEDS['C2_coverage'], 700),
            ('modular', random_modular_instance, SEEDS['C2_modular'], 700),
            ('mixture', random_mixture_instance, SEEDS['C2_mixture'], 700)]
    total = 0
    viol = 0
    worst = None
    worst_info = None
    per_family = {}
    problems = []
    legality_checks = 0
    for name, maker, seed, reps in plan:
        rng = random.Random(seed)
        fam_worst = None
        fam_n = 0
        for _ in range(reps):
            n = rng.randint(8, 12)
            inst = maker(rng, n)
            opt = inst.opt()
            if opt <= 0:
                continue
            bad = inst.legality_eta_u_one()
            legality_checks += 1
            if bad:
                problems.append(f'{name}: illegal instance {bad[:2]}')
                continue
            order = list(range(n))
            rng.shuffle(order)
            dist, q, ms, anchors, ev = inst.run(order)
            problems += [f'{name} n={n}: {p}' for p in contract_ok(dist, q, ms, n)]
            ratio = ev / Fr(opt)
            total += 1
            fam_n += 1
            if ratio < TARGET:
                viol += 1
                WITNESSES.append({'check': 'C2', 'family': name, 'n': n,
                                  'ratio': str(ratio),
                                  'f': [int(x) for x in inst.f],
                                  'ftilde2': [int(x) for x in inst.h],
                                  'order': order})
            if worst is None or ratio < worst:
                worst = ratio
                worst_info = {'family': name, 'n': n, 'ratio': str(ratio),
                              'order': order, 'anchors': anchors}
            if fam_worst is None or ratio < fam_worst:
                fam_worst = ratio
        per_family[name] = {'instances': fam_n, 'worst_ratio': str(fam_worst),
                            'worst_ratio_float': float(fam_worst)}
        say(f'  {name:9s}: {fam_n} instances, worst ratio {fam_worst} '
            f'({float(fam_worst):.6f})')
    COUNTS['C2_instances'] = total
    COUNTS['C2_legality_checks'] = legality_checks
    COUNTS['C2_violations'] = viol
    say(f'  total {total} instances, violations {viol}, worst ratio {worst} '
        f'({float(worst):.6f}), target {TARGET} ({float(TARGET):.6f})')
    return total, viol, worst, worst_info, per_family, problems


# ---------------------------------------------------------------------------
# C3: structured cases.
# ---------------------------------------------------------------------------
def check_structured(tight_rows):
    say('\n=== C3: structured cases ===')
    cases = []
    problems = []
    # (i) eta = 1, ftilde = f, smallest legal n
    for n, seed in ((4, SEEDS['C3_eta1_n4']), (5, SEEDS['C3_eta1_n5'])):
        rng = random.Random(seed)
        worst = None
        cnt = 0
        for _ in range(250):
            inst = random_eta_one_instance(rng, n)
            opt = inst.opt()
            if opt <= 0:
                continue
            bad = inst.legality_eta_u_one()
            if bad:
                problems.append(f'eta=1 n={n} illegal: {bad[:2]}')
                continue
            order = list(range(n))
            rng.shuffle(order)
            dist, q, ms, anchors, ev = inst.run(order)
            problems += [f'eta1 n={n}: {p}' for p in contract_ok(dist, q, ms, n)]
            ratio = ev / Fr(opt)
            cnt += 1
            if ratio < TARGET:
                problems.append(f'eta=1 n={n}: ratio {ratio} < target')
                WITNESSES.append({'check': 'C3-eta1', 'n': n, 'ratio': str(ratio),
                                  'f': [int(x) for x in inst.f], 'order': order})
            if worst is None or ratio < worst:
                worst = ratio
        cases.append({'case': f'eta=1 (ftilde=f), n={n}', 'instances': cnt,
                      'worst_ratio': str(worst), 'outcome': 'PASS'})
        say(f'  eta = 1, n = {n}: {cnt} instances, worst ratio {worst} '
            f'({float(worst):.6f})')
        COUNTS[f'C3_eta1_n{n}_instances'] = cnt
    # (ii) the tight instance at n = 6..12 (values already computed in C1)
    tight_small = [r for r in tight_rows if 6 <= r['n'] <= 12]
    all_equal = all(Fr(r['E']) == TIGHT_VALUE for r in tight_small)
    cases.append({'case': 'tight instance n = 6..12', 'instances': len(tight_small),
                  'worst_ratio': str(TIGHT_VALUE),
                  'outcome': 'PASS' if all_equal else 'FAIL'})
    say(f'  tight instance n = 6..12: {len(tight_small)} values, all equal to '
        f'3/5 + 1/2048 = {TIGHT_VALUE}: {all_equal}')
    if not all_equal:
        problems.append('tight instance n = 6..12 not constant')
    # (iii) the two families of results/E4_worst_instances.py at K = 2, eta = 3/2
    fam = [vj_instance(0), vj_instance(1), vj_instance(2), uk_instance()]
    for inst in fam:
        bad, eu, eo = inst.lattice_legality()
        if bad:
            problems.append(f'{inst.label} legality: {bad[:2]}')
        n = inst.n
        worst = None
        worst_order = None
        orders = [list(range(n)), list(reversed(range(n)))]
        rng = random.Random(4242)
        for _ in range(6):
            o = list(range(n))
            rng.shuffle(o)
            orders.append(o)
        for order in orders:
            dist, q, ms, anchors, ev = inst.run(order)
            problems += [f'{inst.label}: {p}' for p in contract_ok(dist, q, ms, n)]
            ratio = ev / inst.opt()
            if worst is None or ratio < worst:
                worst, worst_order = ratio, order
        if worst < TARGET:
            problems.append(f'{inst.label}: ratio {worst} < target')
            WITNESSES.append({'check': 'C3-E4family', 'label': inst.label,
                              'ratio': str(worst), 'order': worst_order})
        cases.append({'case': f'E4 family {inst.label} (K=2, eta=3/2)',
                      'instances': len(orders), 'worst_ratio': str(worst),
                      'outcome': 'PASS' if worst >= TARGET else 'FAIL'})
        say(f'  E4 family {inst.label:4s}: n={n}, actual (eta_u,eta_o)=({eu},{eo}), '
            f'product {eu * eo}, worst over {len(orders)} tie orders '
            f'{worst} ({float(worst):.6f})')
    COUNTS['C3_cases'] = len(cases)
    return cases, problems


# ---------------------------------------------------------------------------
# C5: rerun the delivered spot-check script.
# ---------------------------------------------------------------------------
def rerun_spotcheck():
    say('\n=== C5: rerun results/J8/J8_claude_spotcheck.py ===')
    path = os.path.join(ROOT, 'results', 'J8', 'J8_claude_spotcheck.py')
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, path], cwd=ROOT, capture_output=True,
                           text=True, timeout=900)
        out = p.stdout.strip().splitlines()
        code = p.returncode
        err = p.stderr.strip().splitlines()[-3:]
    except Exception as exc:                                  # pragma: no cover
        return {'path': 'results/J8/J8_claude_spotcheck.py', 'exit_code': None,
                'error': str(exc)}, [f'rerun failed: {exc}']
    dt = time.time() - t0
    for line in out:
        say(f'  | {line}')
    say(f'  exit code {code}, {dt:.1f} s')
    problems = []
    if code != 0:
        problems.append(f'J8_claude_spotcheck.py exit code {code}: {err}')
    return {'path': 'results/J8/J8_claude_spotcheck.py', 'exit_code': code,
            'seconds': round(dt, 1), 'stdout': out, 'stderr_tail': err}, problems


# ---------------------------------------------------------------------------
# D2: local search around the tight instance.
# ---------------------------------------------------------------------------
def grid_from_params(nb, r, h, lam, mu):
    """F(x,0) = 1 - r_x, F(x,1) = 1 - h_x, F(x,2) = 1;
    H(x,0) = C - r_x - lam h_x, H(x,1) = C - mu h_x, H(x,2) = C, C = 1 + lam h_0.
    The tight instance is r_x, h_x of tight_grid with lam = 1/2, mu = 3/2."""
    C = 1 + lam * h[0]
    Fg, Hg = {}, {}
    for x in range(nb + 1):
        Fg[(x, 0)] = 1 - r[x]
        Fg[(x, 1)] = 1 - h[x]
        Fg[(x, 2)] = Fr(1)
        Hg[(x, 0)] = C - r[x] - lam * h[x]
        Hg[(x, 1)] = C - mu * h[x]
        Hg[(x, 2)] = C
    return CountGrid(nb, Fg, Hg, label='perturbed')


def tight_params(n):
    g = tight_grid(n)
    nb = g.nb
    r = [1 - g.F[(x, 0)] for x in range(nb + 1)]
    h = [1 - g.F[(x, 1)] for x in range(nb + 1)]
    return nb, r, h, Fr(1, 2), Fr(3, 2)


def worst_over_orders(inst, rng, n_orders=4):
    n = inst.n
    orders = [list(range(n)), list(reversed(range(n)))]
    for _ in range(max(0, n_orders - 2)):
        o = list(range(n))
        rng.shuffle(o)
        orders.append(o)
    worst = None
    info = None
    problems = []
    for order in orders:
        dist, q, ms, anchors, ev = inst.run(order)
        problems += contract_ok(dist, q, ms, n)
        ratio = ev / inst.opt()
        if worst is None or ratio < worst:
            worst, info = ratio, {'order': order, 'anchors': anchors,
                                  'E': str(ev), 'OPT': str(inst.opt())}
    return worst, info, problems


def local_search(trials=500, restarts=5):
    say('\n=== D2: local search around the tight instance (perturb within the band) ===')
    rng = random.Random(SEEDS['D2_local'])
    n = 8
    nb0, r0, h0, lam0, mu0 = tight_params(n)
    evaluated = 0
    attempts = 0
    rejected = 0
    worst = None
    worst_state = None
    per_restart = []
    steps_per = trials // restarts
    problems = []
    ratios = []
    for restart in range(restarts):
        r, h, lam, mu = list(r0), list(h0), lam0, mu0
        base = grid_from_params(nb0, r, h, lam, mu)
        bad, _, _ = base.legality()
        assert not bad, bad
        cur, cur_info, pr = worst_over_orders(base, rng)
        problems += pr
        evaluated += 1
        ratios.append(cur)
        generic = (restart >= 3)        # last two restarts perturb every grid value
        cur_grid = base
        steps_done = 0
        while steps_done < steps_per:
            attempts += 1
            if attempts > 200 * trials:
                break
            D = rng.choice([32, 64, 128, 256, 512])
            if not generic:
                r2, h2 = list(r), list(h)
                lam2, mu2 = lam, mu
                for _ in range(rng.randint(1, 3)):
                    which = rng.choice(['r', 'h', 'lam', 'mu'])
                    step = Fr(rng.randint(-3, 3), D)
                    if which == 'r':
                        i = rng.randint(1, nb0)
                        r2[i] = max(Fr(0), r2[i] + step)
                    elif which == 'h':
                        i = rng.randint(0, nb0)
                        h2[i] = max(Fr(0), h2[i] + step)
                    elif which == 'lam':
                        lam2 = max(Fr(0), lam2 + step)
                    else:
                        mu2 = max(Fr(0), mu2 + step)
                cand = grid_from_params(nb0, r2, h2, lam2, mu2)
            else:
                Fg = dict(cur_grid.F)
                Hg = dict(cur_grid.H)
                for _ in range(rng.randint(1, 4)):
                    x = rng.randint(0, nb0)
                    y = rng.randint(0, 2)
                    if (x, y) == (0, 0):
                        continue
                    step = Fr(rng.randint(-3, 3), D)
                    if rng.random() < 0.5:
                        Fg[(x, y)] = max(Fr(0), Fg[(x, y)] + step)
                    else:
                        Hg[(x, y)] = max(Fr(0), Hg[(x, y)] + step)
                cand = CountGrid(nb0, Fg, Hg, label='perturbed-generic')
            bad, eu, eo = cand.legality()
            if bad or cand.opt() <= 0:
                rejected += 1
                continue
            val, info, pr = worst_over_orders(cand, rng)
            problems += pr
            evaluated += 1
            steps_done += 1
            ratios.append(val)
            if worst is None or val < worst:
                worst = val
                worst_state = {'restart': restart, 'generic': generic,
                               'ratio': str(val), 'ratio_float': float(val),
                               'eta_u': str(eu), 'eta_o': str(eo),
                               'F': {f'{k[0]},{k[1]}': str(v)
                                     for k, v in sorted(cand.F.items())},
                               'H': {f'{k[0]},{k[1]}': str(v)
                                     for k, v in sorted(cand.H.items())},
                               **info}
            if val <= cur:                # descend, sideways moves accepted
                cur, cur_info, cur_grid = val, info, cand
                if not generic:
                    r, h, lam, mu = (r2, h2, lam2, mu2)
        per_restart.append({'restart': restart, 'generic': generic,
                            'best_ratio': str(cur), 'steps': steps_done})
        say(f'  restart {restart} ({"generic grid" if generic else "parametric"}): '
            f'{steps_done} accepted steps, local worst ratio {cur} '
            f'({float(cur):.8f})')
    viol = 1 if (worst is not None and worst < TARGET) else 0
    if viol:
        WITNESSES.append({'check': 'D2', **worst_state})
    distinct = sorted(set(ratios))
    hist = {'equal_to_tight_value': sum(1 for r in ratios if r == TIGHT_VALUE),
            'below_0.61': sum(1 for r in ratios if r < Fr(61, 100)),
            'below_0.65': sum(1 for r in ratios if r < Fr(65, 100)),
            'equal_to_one': sum(1 for r in ratios if r == 1),
            'distinct_values': len(distinct),
            'five_smallest': [str(r) for r in distinct[:5]]}
    COUNTS['D2_evaluated'] = evaluated
    COUNTS['D2_attempts'] = attempts
    COUNTS['D2_rejected'] = rejected
    COUNTS['D2_equal_to_tight_value'] = hist['equal_to_tight_value']
    COUNTS['D2_distinct_ratios'] = len(distinct)
    say(f'  ratio histogram: {hist["equal_to_tight_value"]} equal to the tight '
        f'value, {hist["below_0.61"]} below 0.61, {hist["below_0.65"]} below '
        f'0.65, {hist["equal_to_one"]} equal to 1, {len(distinct)} distinct '
        f'values; five smallest {hist["five_smallest"]}')
    say(f'  {evaluated} legal perturbations evaluated ({attempts} attempts, '
        f'{rejected} rejected as illegal)')
    say(f'  worst ratio {worst} = {float(worst):.8f}, target {TARGET} = '
        f'{float(TARGET):.8f}, slack {worst - TARGET}')
    return worst, worst_state, per_restart, viol, problems, hist


# ---------------------------------------------------------------------------
# running example numbers (K = 3, eta = 3/2), for the report
# ---------------------------------------------------------------------------
def running_example():
    K3, eta = 3, Fr(3, 2)
    k1 = (K3 - 1) * eta + 1
    q = (K3 - 1) * eta / k1
    V = [1 - q ** j * (1 - Fr(K3 - j, 1) / (K3 * eta)) for j in range(K3)]
    rho3 = min(V)
    return {'K': 3, 'eta': '3/2', 'k1': str(k1), 'q': str(q),
            'V': [str(v) for v in V], 'rho_3': str(rho3),
            'one_over_eta': str(1 / eta),
            'rho_2': '3/5', 'tight_value': str(TIGHT_VALUE),
            'claimed_bound': str(TARGET)}


# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    say('V11 Q9 oracle: J8 ProbeLottery (K = 2, eta = 3/2)')
    say(f'statement: results/V11/inputs/statement_probelottery.md')
    say(f'target bound: E[f(T)] >= ({TARGET}) OPT = {float(TARGET):.9f} OPT')
    say(f'seeds: {SEEDS}')

    all_problems = []

    tight_rows, p1 = check_tight()
    all_problems += p1
    rec('C1 tight instance n in {6,8,12,20}', 'PASS' if not p1 else 'FAIL',
        f'E[f(T)] = 3/5 + 1/2048 = {TIGHT_VALUE} on every n, queries <= 9n, '
        f'max queried size 5')

    total, viol, worst_rand, worst_info, per_family, p2 = check_random()
    all_problems += p2
    rec('C2 random legal instances (n = 8..12)',
        'PASS' if (not p2 and viol == 0) else 'FAIL',
        f'{total} instances, {viol} violations, worst ratio '
        f'{worst_rand} = {float(worst_rand):.6f}')

    cases, p3 = check_structured(tight_rows)
    all_problems += p3
    rec('C3 structured cases', 'PASS' if not p3 else 'FAIL',
        f'{len(cases)} cases: eta = 1 at n = 4, 5; tight at n = 6..12; '
        f'V_0, V_1, V_2 and U_2 of the E4 families')

    rec('C4 algorithm contract', 'PASS' if not all_problems else 'FAIL',
        'every run: output sets of size 2, mass 1, queries <= 9n, queried '
        'size <= 5')

    rerun, p5 = rerun_spotcheck()
    all_problems += p5
    same = any('6149/10240' in line for line in rerun.get('stdout', []))
    if not same:
        all_problems.append('spot-check tight value not seen in its output')
    rec('C5 rerun J8_claude_spotcheck.py',
        'PASS' if (not p5 and same) else 'FAIL',
        f'exit code {rerun.get("exit_code")}, tight value 6149/10240 matches '
        f'this script')

    rec('G1 LP dual certificates for (3), (8)-(12)', 'GAP',
        'the proof file results/J8/probe_lottery.md was not delivered; the '
        'inequalities do not exist in the repository, so no dual certificate '
        'can be built or checked')

    worst_loc, worst_state, per_restart, viol_loc, p6, hist = local_search()
    all_problems += p6
    rec('D2 local search (500 evaluated perturbations)',
        'PASS' if viol_loc == 0 else 'FAIL',
        f'worst ratio {worst_loc} = {float(worst_loc):.8f} >= target')

    worst_all = min(worst_rand, worst_loc)
    ok = not all_problems
    elapsed = time.time() - t0

    say('\n=== summary ===')
    for name, status, detail in RESULTS:
        say(f'  {status:5s} {name}')
    say(f'  random instances: {total}, violations: {viol}')
    say(f'  worst ratio overall: {worst_all} = {float(worst_all):.8f}, '
        f'target {float(TARGET):.8f}, slack {worst_all - TARGET}')
    say(f'  problems: {len(all_problems)}')
    for p in all_problems[:20]:
        say(f'    ! {p}')
    say(f'  elapsed {elapsed:.1f} s; exit code {0 if ok else 1}')

    payload = {
        'script': 'results/V11/oracle/probelottery.py',
        'statement': 'J8 ProbeLottery: K = 2, eta = 3/2, randomized, <= 9n '
                     'queries, queried sets of size <= 5, output of size 2, '
                     'E[f(T)] >= (3/5 + 1/400000) OPT on every legal instance',
        'sources': {
            'statement': 'results/V11/inputs/statement_probelottery.md',
            'definition': 'results/V11/inputs/definition1.md (convention B)',
            'route_one': 'NOT DELIVERED: results/J8/probe_lottery.md with the '
                         'inequalities (3), (8)-(12) does not exist in the '
                         'repository',
            'implementation_reference': 'results/J8/J8_claude_spotcheck.py '
                                        '(rerun only, not imported)',
            'handoff': 'HANDOFF_2026-09-18.md section 4',
            'e4_families': 'results/E4_worst_instances.py via results/N2_check.py '
                           'and code/check_explicit_instance.py (cited, rebuilt '
                           'exactly in Fractions, not modified)',
        },
        'seeds': SEEDS,
        'target_bound': str(TARGET),
        'tight_value': str(TIGHT_VALUE),
        'checks': [{'name': n, 'status': s, 'detail': d} for n, s, d in RESULTS],
        'counts': COUNTS,
        'tight_rows': tight_rows,
        'random': {'instances': total, 'violations': viol,
                   'worst_ratio': str(worst_rand),
                   'worst_ratio_float': float(worst_rand),
                   'worst_instance': worst_info, 'per_family': per_family},
        'structured': cases,
        'rerun': rerun,
        'local_search': {'evaluated': COUNTS.get('D2_evaluated'),
                         'attempts': COUNTS.get('D2_attempts'),
                         'rejected': COUNTS.get('D2_rejected'),
                         'violations': viol_loc,
                         'worst_ratio': str(worst_loc),
                         'worst_ratio_float': float(worst_loc),
                         'worst_state': worst_state,
                         'ratio_histogram': hist,
                         'per_restart': per_restart},
        'worst_ratio_overall': str(worst_all),
        'worst_slack_overall': str(worst_all - TARGET),
        'violations_total': viol + viol_loc,
        'witnesses': WITNESSES,
        'problems': all_problems,
        'running_example': running_example(),
        'elapsed_seconds': round(elapsed, 1),
        'exit_code': 0 if ok else 1,
    }
    with open(os.path.join(HERE, 'probelottery.json'), 'w') as fh:
        json.dump(payload, fh, indent=1, sort_keys=False)
        fh.write('\n')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
