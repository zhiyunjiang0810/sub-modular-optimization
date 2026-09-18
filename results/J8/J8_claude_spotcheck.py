# Claude spot-check: implement ProbeLottery (K=2) exactly as stated and run it on
# (a) the K=2, eta=3/2 double-residual tight instance (adversarial ties: B elements first),
# (b) random weighted-coverage instances with G = F + (1/2) F' (so dF <= dG <= 3/2 dF).
# Finite tests can only refute; they do not verify the general proof.
from fractions import Fraction as R
from itertools import combinations
import random

EPS = R(1, 10000)
TARGET = R(3, 5) + R(1, 400000)

def probe_lottery(N, G):
    """N: list of elements in fixed tie-break order (argmax picks the first maximiser).
    G: oracle on frozensets. Returns (distribution {frozenset: prob}, queries, maxsize)."""
    cache = {}
    stats = {'q': 0, 'maxsize': 0}
    def g(S):
        S = frozenset(S)
        if S not in cache:
            cache[S] = G(S); stats['q'] += 1; stats['maxsize'] = max(stats['maxsize'], len(S))
        return cache[S]
    def argmax(cands, key):
        best, bv = None, None
        for e in cands:
            v = key(e)
            if bv is None or v > bv: best, bv = e, v
        return best, bv
    # 1. singletons
    b, M = argmax(N, lambda e: g({e}))
    # 2. pairs containing b
    c, p = argmax([e for e in N if e != b], lambda e: g({b, e}))
    P0 = frozenset({b, c})
    # 3. pool
    C = [e for e in N if e != b and g({e}) >= M - EPS*M and g({b, e}) >= p - EPS*M]
    # 4. extensions
    B = [b]; secondary = []
    for _ in range(4):
        rest = [e for e in C if e not in B]
        if not rest: break
        v, _ = argmax(rest, lambda e: g(set(B) | {e}))
        B.append(v)
        zv, _ = argmax([z for z in N if z != v], lambda z: g({v, z}))
        secondary.append(frozenset({v, zv}))
        secondary.append(frozenset({b, v}))
    while len(secondary) < 8: secondary.append(P0)
    dist = {}
    dist[P0] = dist.get(P0, R(0)) + R(127, 128)
    for T in secondary: dist[T] = dist.get(T, R(0)) + R(1, 1024)
    assert sum(dist.values()) == 1
    return dist, stats['q'], stats['maxsize'], B

# ---------- (a) tight instance, K=2, eta=3/2 (J6 double-residual family, j=1) ----------
def tight_instance(n):
    K, eta = 2, R(3, 2)
    k1 = (K-1)*eta + 1; q = (K-1)*eta/k1; j = 1; Q = q**j; delta = Q/(K*eta); C = k1/K
    def r(x): return q**x if x <= j else max(R(0), Q - (x-j)*delta)
    def h(x): return R(K-1, K)*q**x if x <= j else max(R(0), R(K-1, K)*Q - (x-j)*delta)
    def F(x, y): return 1 - r(x) if y == 0 else 1 - R(K-y, K-1)*h(x)
    def H(x, y): return C - r(x) - (eta-1)*h(x) if y == 0 else C - eta*R(K-y, K-1)*h(x)
    Bel = list(range(n-2)); Oel = [n-2, n-1]
    cnt = lambda S: (sum(1 for e in S if e in Bel), sum(1 for e in S if e in Oel))
    Fs = lambda S: F(*cnt(S)); Gs = lambda S: H(*cnt(S))   # eta_u = 1, so G = H
    return Bel + Oel, Fs, Gs, frozenset(Oel)

for n in [6, 8, 12, 20]:
    N, Fs, Gs, O = tight_instance(n)
    dist, nq, ms, B = probe_lottery(N, Gs)
    ev = sum(pr*Fs(T) for T, pr in dist.items())
    print(f"tight n={n}: anchors={B} (O={sorted(O)})  E[F]={ev} = 3/5 + {ev-R(3,5)}  ok={ev>=TARGET}  queries={nq}<=9n={9*n}  maxsize={ms}")

# ---------- (b) random coverage instances ----------
random.seed(7)
worst = None; viol = 0; trials = 0
for trial in range(400):
    n = random.randint(4, 9); U = list(range(random.randint(6, 16)))
    w = {u: R(random.randint(1, 9)) for u in U}
    cov = {e: frozenset(random.sample(U, random.randint(1, max(1, len(U)//2)))) for e in range(n)}
    Uh = set(random.sample(U, len(U)//2))
    def Fs(S, cov=cov, w=w): return sum(w[u] for u in set().union(*[cov[e] for e in S])) if S else R(0)
    def Fp(S, cov=cov, w=w, Uh=Uh): return sum(w[u] for u in set().union(*[cov[e] for e in S]) if u in Uh) if S else R(0)
    Gs = lambda S, Fs=Fs, Fp=Fp: Fs(S) + Fp(S)/2          # dF <= dG <= 3/2 dF
    N = list(range(n)); random.shuffle(N)
    OPT = max(Fs(frozenset(P)) for P in combinations(N, 2))
    dist, nq, ms, B = probe_lottery(N, Gs)
    ev = sum(pr*Fs(T) for T, pr in dist.items())
    ratio = ev/OPT; trials += 1
    assert nq <= 9*n and ms <= 5, (nq, n, ms)
    if ratio < TARGET: viol += 1
    if worst is None or ratio < worst: worst = ratio
print(f"random coverage: {trials} instances, violations={viol}, worst ratio={worst} ({float(worst):.4f})")
