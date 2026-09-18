"""ROUTE-TWO blind check for J8 ProbeLottery (K=2, eta=3/2).

Exact rational arithmetic only (fractions.Fraction); floats appear in printouts only.

Contents
  1. coverage_f      : monotone submodular f built from a weighted universe (atoms).
  2. feasible_tilde  : exact feasibility of the predictor band
                       d_e(S) <= tf(SUe) - tf(S) <= (3/2) d_e(S)   for all S, e notin S,
                       together with extra difference constraints that encode the
                       adversarial run.  The whole system is a difference-constraint
                       system, so feasibility == no negative cycle (Bellman-Ford,
                       Fractions).  Returns the pointwise-maximal solution.
  3. probe_lottery   : the algorithm exactly as written in statement_probelottery.md.

Rerun: python3 J8_route2_check.py
"""
from fractions import Fraction as F
from itertools import combinations

EPS = F(1, 10000)
ETA = F(3, 2)


# ---------- 1. instances -------------------------------------------------
def coverage_f(elements, cover, weight):
    """f(S) = total weight of the atoms covered by S (monotone submodular)."""
    f = {}
    for r in range(len(elements) + 1):
        for S in combinations(elements, r):
            atoms = set()
            for e in S:
                atoms |= cover[e]
            f[frozenset(S)] = sum(weight[a] for a in atoms)
    return f


def subsets(elements):
    for r in range(len(elements) + 1):
        for S in combinations(elements, r):
            yield frozenset(S)


# ---------- 2. predictor feasibility ------------------------------------
def feasible_tilde(elements, f, extra=()):
    """extra: list of (U, V, c) meaning  tf(V) - tf(U) <= c   (U, V frozensets).

    Returns (True, tf) with tf the pointwise-maximal solution normalised to
    tf(emptyset) = 0, or (False, None) if the system is infeasible.
    """
    nodes = list(subsets(elements))
    idx = {S: i for i, S in enumerate(nodes)}
    edges = []  # (u, v, w) meaning x_v - x_u <= w
    for S in nodes:
        for e in elements:
            if e in S:
                continue
            T = S | {e}
            d = f[T] - f[S]
            edges.append((idx[S], idx[T], ETA * d))   # tf(T) - tf(S) <= 1.5 d
            edges.append((idx[T], idx[S], -d))        # tf(S) - tf(T) <= -d
    for (U, V, c) in extra:
        edges.append((idx[U], idx[V], F(c)))
    src = idx[frozenset()]
    INF = None
    dist = [INF] * len(nodes)
    dist[src] = F(0)
    for it in range(len(nodes) + 1):
        changed = False
        for (u, v, w) in edges:
            if dist[u] is None:
                continue
            nd = dist[u] + w
            if dist[v] is None or nd < dist[v]:
                dist[v] = nd
                changed = True
        if not changed:
            break
    else:
        return False, None  # still relaxing after |V| rounds: negative cycle
    if any(d is None for d in dist):
        return False, None
    tf = {S: dist[idx[S]] for S in nodes}
    # independent re-verification of the band and of the extra constraints
    for S in nodes:
        for e in elements:
            if e in S:
                continue
            T = S | {e}
            d = f[T] - f[S]
            assert d >= 0, "f not monotone"
            assert d <= tf[T] - tf[S] <= ETA * d, ("band violated", set(S), e)
    for (U, V, c) in extra:
        assert tf[V] - tf[U] <= F(c) + F(0), ("extra violated", set(U), set(V), c)
    return True, tf


def check_submodular(elements, f):
    for S in subsets(elements):
        for e in elements:
            if e in S:
                continue
            for x in elements:
                if x in S or x == e:
                    continue
                # d_e(S) >= d_e(S u {x})
                if not (f[S | {e}] - f[S] >= f[S | {e, x}] - f[S | {x}]):
                    return False
    return True


# ---------- 3. the algorithm --------------------------------------------
def probe_lottery(order, tf, f):
    """order: the fixed tie-break order of N; argmax returns the FIRST maximiser."""
    queries = {}

    def g(S):
        S = frozenset(S)
        queries[S] = queries.get(S, 0) + 1
        return tf[S]

    def argmax(cands, key):
        best, bv = None, None
        for e in cands:
            v = key(e)
            if bv is None or v > bv:
                best, bv = e, v
        return best, bv

    b, M = argmax(order, lambda e: g([e]))
    c, p = argmax([e for e in order if e != b], lambda e: g([b, e]))
    P0 = frozenset([b, c])
    C = [e for e in order
         if e != b and g([e]) >= M - EPS * M and g([b, e]) >= p - EPS * M]
    B = [b]
    secondary = []
    for _ in range(4):
        rest = [e for e in C if e not in B]
        if not rest:
            break
        v, _ = argmax(rest, lambda e: g(B + [e]))
        B.append(v)
        z, _ = argmax([x for x in order if x != v], lambda x: g([v, x]))
        secondary.append(frozenset([v, z]))
        secondary.append(frozenset([b, v]))
    while len(secondary) < 8:
        secondary.append(P0)
    E = F(127, 128) * f[P0] + sum(F(1, 1024) * f[A] for A in secondary)
    return dict(b=b, c=c, P0=P0, M=M, p=p, C=C, B=B, secondary=secondary,
                E=E, nqueries=len(queries),
                maxsize=max(len(S) for S in queries))


def opt2(elements, f):
    return max(f[frozenset(S)] for S in combinations(elements, 2))


# ---------- the near-tight instance of Section 8 ------------------------
def tight_instance():
    """x = f({b}) = 2/5, w_i = 1/2, h_i = 7/10, f(P0) = 3/5, OPT = 1."""
    elements = ['b', 'c', 'o1', 'o2']          # tie-break order
    weight = {'a1': F(1, 5), 'r1': F(3, 10), 'a2': F(1, 5), 'r2': F(3, 10),
              'cc': F(1, 5)}
    cover = {'b': {'a1', 'a2'}, 'c': {'cc'},
             'o1': {'a1', 'r1'}, 'o2': {'a2', 'r2'}}
    f = coverage_f(elements, cover, weight)
    E0 = frozenset()
    S = lambda *xs: frozenset(xs)
    M = F(3, 5)
    extra = [
        # tf({b}) = M = 3/5  (upper end of the band, 1.5 * 2/5)
        (E0, S('b'), M), (S('b'), E0, -M),
        # tf({o_i}) = M  (b wins the singleton argmax by the tie-break order)
        (E0, S('o1'), M), (S('o1'), E0, -M),
        (E0, S('o2'), M), (S('o2'), E0, -M),
        # tf({b,c}) = tf({b,o_i}) = 9/10 (c wins the pair argmax by tie-break)
        (E0, S('b', 'c'), F(9, 10)), (S('b', 'c'), E0, F(-9, 10)),
        (E0, S('b', 'o1'), F(9, 10)), (S('b', 'o1'), E0, F(-9, 10)),
        (E0, S('b', 'o2'), F(9, 10)), (S('b', 'o2'), E0, F(-9, 10)),
    ]
    return elements, f, extra


def blocking_instance():
    """Candidate adversarial instance: the pool is filled with 4 'b-clones'
    j1..j4 that win all four extension rounds, so that no element of O* is ever
    appended to B and every secondary set has value exactly (3/5) OPT."""
    elements = ['b', 'j1', 'j2', 'j3', 'j4', 'o1', 'o2']   # tie-break order
    U1 = ['u1', 'u2', 'u3', 'u4', 'u5']
    U2 = ['w1', 'w2', 'w3', 'w4', 'w5']
    weight = {a: F(1, 10) for a in U1 + U2}
    cover = {
        'b':  {'u1', 'u2', 'w1', 'w2'},
        'j1': {'u1', 'u3', 'w1', 'w3'},
        'j2': {'u1', 'u4', 'w1', 'w4'},
        'j3': {'u1', 'u5', 'w1', 'w5'},
        'j4': {'u1', 'u3', 'w1', 'w3'},
        'o1': set(U1), 'o2': set(U2),
    }
    f = coverage_f(elements, cover, weight)
    E0 = frozenset()
    S = lambda *xs: frozenset(xs)
    M, P = F(3, 5), F(9, 10)
    extra = []
    for e in ['b', 'j1', 'j2', 'j3', 'j4', 'o1', 'o2']:      # tf({e}) = M
        extra += [(E0, S(e), M), (S(e), E0, -M)]
    for e in ['j1', 'j2', 'j3', 'j4', 'o1', 'o2']:           # tf({b,e}) = p
        extra += [(E0, S('b', e), P), (S('b', e), E0, -P)]
    for j in ['j1', 'j2', 'j3', 'j4']:                       # tf({j,o}) = p
        for o in ['o1', 'o2']:
            extra += [(E0, S(j, o), P), (S(j, o), E0, -P)]
    for j in ['j1', 'j2', 'j3', 'j4']:                       # tf({j,j'}) <= p
        for k in ['j1', 'j2', 'j3', 'j4']:
            if j < k:
                extra.append((E0, S(j, k), P))
    # rounds 2, 3, 4: the clone must not lose the argmax
    B2 = S('b', 'j1')
    for x in ['j3', 'j4', 'o1', 'o2']:
        extra.append((B2 | {'j2'}, B2 | {x}, F(0)))
    B3 = S('b', 'j1', 'j2')
    for x in ['j4', 'o1', 'o2']:
        extra.append((B3 | {'j3'}, B3 | {x}, F(0)))
    B4 = S('b', 'j1', 'j2', 'j3')
    for x in ['o1', 'o2']:
        extra.append((B4 | {'j4'}, B4 | {x}, F(0)))
    return elements, f, extra


def main():
    elements, f, extra = tight_instance()
    print('f monotone submodular (exhaustive):', check_submodular(elements, f))
    print('OPT =', opt2(elements, f))
    ok, tf = feasible_tilde(elements, f, extra)
    print('predictor band + adversarial constraints feasible:', ok)
    if not ok:
        return
    for S in sorted(tf, key=lambda s: (len(s), sorted(s))):
        if len(S) <= 2:
            print('   f', sorted(S), '=', f[S], '   tf =', tf[S])
    R = probe_lottery(elements, tf, f)
    OPT = opt2(elements, f)
    print('b =', R['b'], ' c =', R['c'], ' P0 =', sorted(R['P0']),
          ' f(P0) =', f[R['P0']], '=', float(f[R['P0']] / OPT), '* OPT')
    print('pool C =', R['C'], ' B =', R['B'])
    print('secondary =', [(sorted(A), str(f[A])) for A in R['secondary']])
    print('queries =', R['nqueries'], '<= 9n =', 9 * len(elements),
          ' max queried size =', R['maxsize'])
    print('E[f(T)] =', R['E'], '=', float(R['E']))
    print('E/OPT - 3/5 =', R['E'] / OPT - F(3, 5), '=',
          float(R['E'] / OPT - F(3, 5)))
    print('target excess 1/400000 =', float(F(1, 400000)),
          ' satisfied:', R['E'] / OPT >= F(3, 5) + F(1, 400000))

    print('\n--- candidate blocking instance (4 clones in the pool) ---')
    elements, f, extra = blocking_instance()
    print('f monotone submodular (exhaustive):', check_submodular(elements, f))
    print('OPT =', opt2(elements, f))
    ok, tf = feasible_tilde(elements, f, extra)
    print('predictor band + blocking constraints feasible:', ok)
    if not ok:
        print('the difference system has a negative cycle: this configuration'
              ' of (f, tilde f) does not exist')
        return
    R = probe_lottery(elements, tf, f)
    OPT = opt2(elements, f)
    print('b =', R['b'], ' c =', R['c'], ' f(P0) =', f[R['P0']],
          ' pool C =', R['C'], ' B =', R['B'])
    print('secondary =', [(sorted(A), str(f[A])) for A in R['secondary']])
    print('queries =', R['nqueries'], '<= 9n =', 9 * len(elements),
          ' max size =', R['maxsize'])
    print('E/OPT =', R['E'] / OPT, '=', float(R['E'] / OPT),
          '  >= 3/5 + 1/400000 ?', R['E'] / OPT >= F(3, 5) + F(1, 400000))


if __name__ == '__main__':
    main()
