"""Independent re-verification of the two tight instances:
 (a) route2's n=4 coverage instance (results/V11/route2/probelottery.md section 10)
 (b) the delivered spot-check's J6 double-residual family (results/J8/J8_claude_spotcheck.py)
Exact rationals only. Rerun: python3 judge_instances.py
"""
from fractions import Fraction as R
from itertools import combinations

EPS = R(1, 10000)
TARGET = R(3, 5) + R(1, 400000)


def subsets(N):
    for k in range(len(N) + 1):
        for S in combinations(N, k):
            yield frozenset(S)


def check_f(N, f):
    """monotone + submodular + normalized, exhaustive."""
    assert f(frozenset()) == 0, 'f(empty) != 0'
    for S in subsets(N):
        for e in N:
            if e in S:
                continue
            if f(S | {e}) - f(S) < 0:
                return False, ('monotone', S, e)
    for S in subsets(N):
        for T in subsets(N):
            if not S <= T:
                continue
            for e in N:
                if e in T:
                    continue
                if f(S | {e}) - f(S) < f(T | {e}) - f(T):
                    return False, ('submodular', S, T, e)
    return True, None


def check_band(N, f, g, lo=R(1), hi=R(3, 2)):
    """lo*d <= dtilde <= hi*d for every S and e not in S."""
    for S in subsets(N):
        for e in N:
            if e in S:
                continue
            d = f(S | {e}) - f(S)
            dt = g(S | {e}) - g(S)
            if not (lo * d <= dt <= hi * d):
                return False, (sorted(S), e, d, dt)
    return True, None


def probe_lottery(N, g):
    cache, stats = {}, {'q': 0, 'ms': 0}

    def G(S):
        S = frozenset(S)
        if S not in cache:
            cache[S] = g(S)
            stats['q'] += 1
            stats['ms'] = max(stats['ms'], len(S))
        return cache[S]

    def argmax(c, key):
        best, bv = None, None
        for x in c:
            v = key(x)
            if bv is None or v > bv:
                best, bv = x, v
        return best, bv

    b, M = argmax(N, lambda x: G({x}))
    c, p = argmax([x for x in N if x != b], lambda x: G({b, x}))
    P0 = frozenset({b, c})
    C = [x for x in N if x != b and G({x}) >= M - EPS * M and G({b, x}) >= p - EPS * M]
    B, sec = [b], []
    for _ in range(4):
        rest = [x for x in C if x not in B]
        if not rest:
            break
        v, _ = argmax(rest, lambda x: G(set(B) | {x}))
        B.append(v)
        zv, _ = argmax([z for z in N if z != v], lambda z: G({v, z}))
        sec.append(frozenset({v, zv}))
        sec.append(frozenset({b, v}))
    r = len(B) - 1
    while len(sec) < 8:
        sec.append(P0)
    dist = {P0: R(127, 128)}
    for T in sec:
        dist[T] = dist.get(T, R(0)) + R(1, 1024)
    assert sum(dist.values()) == 1
    return dict(P0=P0, b=b, c=c, C=C, B=B, r=r, sec=sec, dist=dist,
                q=stats['q'], ms=stats['ms'])


print('===== (a) route2 n=4 coverage instance =====')
N4 = ['b', 'c', 'o1', 'o2']
wt = {'u1': R(1, 5), 'r1': R(3, 10), 'u2': R(1, 5), 'r2': R(3, 10), 'cc': R(1, 5)}
cov = {'b': {'u1', 'u2'}, 'c': {'cc'}, 'o1': {'u1', 'r1'}, 'o2': {'u2', 'r2'}}
f4 = lambda S: sum(wt[u] for u in set().union(*[cov[e] for e in S])) if S else R(0)
tf_tab = {frozenset(): R(0), frozenset({'b'}): R(3, 5), frozenset({'c'}): R(3, 10),
          frozenset({'o1'}): R(3, 5), frozenset({'o2'}): R(3, 5),
          frozenset({'b', 'c'}): R(9, 10), frozenset({'b', 'o1'}): R(9, 10),
          frozenset({'b', 'o2'}): R(9, 10), frozenset({'c', 'o1'}): R(9, 10),
          frozenset({'c', 'o2'}): R(9, 10), frozenset({'o1', 'o2'}): R(27, 20)}
# the file lists only subsets of size <= 2; extend to size 3,4 by the maximal
# (greedy-from-below) completion tf(S) = min over e in S of tf(S-e) + (3/2) d_e(S-e)
order = sorted(subsets(N4), key=len)
for S in order:
    if S in tf_tab:
        continue
    tf_tab[S] = min(tf_tab[S - {e}] + R(3, 2) * (f4(S) - f4(S - {e})) for e in S)
g4 = lambda S: tf_tab[frozenset(S)]
ok, why = check_f(N4, f4)
print('  f monotone submodular exhaustive:', ok, why or '')
ok2, why2 = check_band(N4, f4, g4)
print('  band on all (S,e):', ok2, why2 or '')
OPT4 = max(f4(frozenset(P)) for P in combinations(N4, 2))
print('  OPT =', OPT4, ' f({b,c}) =', f4(frozenset({'b', 'c'})))
res = probe_lottery(N4, g4)
ev4 = sum(pr * f4(T) for T, pr in res['dist'].items())
print('  b=%s c=%s C=%s B=%s r=%d' % (res['b'], res['c'], res['C'], res['B'], res['r']))
print('  E[f(T)]/OPT =', ev4 / OPT4, '= 3/5 +', ev4 / OPT4 - R(3, 5),
      ' target met:', ev4 / OPT4 >= TARGET)
print('  queries =', res['q'], '<= 9n =', 9 * 4, ' max queried size =', res['ms'])

print()
print('===== (b) delivered spot-check tight instance (J6 double-residual, j=1) =====')


def tight_instance(n):
    K, eta = 2, R(3, 2)
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    j = 1
    Q = q ** j
    delta = Q / (K * eta)
    C = k1 / K

    def rr(xx):
        return q ** xx if xx <= j else max(R(0), Q - (xx - j) * delta)

    def hh(xx):
        return R(K - 1, K) * q ** xx if xx <= j else max(R(0), R(K - 1, K) * Q - (xx - j) * delta)

    def F(xx, y):
        return 1 - rr(xx) if y == 0 else 1 - R(K - y, K - 1) * hh(xx)

    def H(xx, y):
        return C - rr(xx) - (eta - 1) * hh(xx) if y == 0 else C - eta * R(K - y, K - 1) * hh(xx)

    Bel = list(range(n - 2))
    Oel = [n - 2, n - 1]
    cnt = lambda S: (sum(1 for e in S if e in Bel), sum(1 for e in S if e in Oel))
    return Bel + Oel, (lambda S: F(*cnt(S))), (lambda S: H(*cnt(S))), frozenset(Oel)


for n in (6, 8):
    N, Fs, Gs, O = tight_instance(n)
    okf, whyf = check_f(N, Fs) if n <= 8 else (None, None)
    okb, whyb = check_band(N, Fs, Gs) if n <= 8 else (None, None)
    OPT = max(Fs(frozenset(P)) for P in combinations(N, 2))
    res = probe_lottery(N, Gs)
    ev = sum(pr * Fs(T) for T, pr in res['dist'].items())
    beta = Fs(res['P0'])
    print('  n=%d  f mono+submod: %s %s' % (n, okf, whyf or ''))
    print('        band on all (S,e): %s %s' % (okb, whyb or ''))
    print('        OPT=%s  O*=%s  b=%s c=%s  beta=f(P0)=%s = %s OPT'
          % (OPT, sorted(O), res['b'], res['c'], beta, beta / OPT))
    print('        pool C=%s  |C|=%d  B=%s  r=%d' % (res['C'], len(res['C']), res['B'], res['r']))
    print('        secondary values:', [str(Fs(T)) for T in res['sec']])
    print('        E/OPT = %s = 3/5 + %s   queries=%d<=9n=%d  maxsize=%d'
          % (ev / OPT, ev / OPT - R(3, 5), res['q'], 9 * n, res['ms']))
    print('        sum_j (gamma_j - beta) =',
          sum(Fs(T) / OPT for T in res['sec']) - 8 * beta / OPT)
    print('        o_i in pool?', [(o, o in res['C']) for o in sorted(O)])
    print('        target met:', ev / OPT >= TARGET)
