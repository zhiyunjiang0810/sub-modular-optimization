"""Standalone exact verification for the independent audit (Python standard library).

Run: python verify_audit.py
Keep submodular_K4_exact_duals.json in the same directory.
No solver or downloaded repository is required. Fractions are checked exactly.
"""
from fractions import Fraction as F
from pathlib import Path
import json

N, K, ETA = 8, 4, F(3, 2)
SIZE = 1 << N

def row(terms):
    out = {}
    for i, x in terms:
        out[i] = out.get(i, F(0)) + x
    return out

def inequalities():
    # Each row is <= 0. Variables: f[S], then surrogate[S].
    for S in range(SIZE):
        for e in range(N):
            if not S >> e & 1:
                yield {S: F(1), S | (1 << e): F(-1)}
    for offset in (0, SIZE):
        for S in range(SIZE):
            for e in range(N):
                if S >> e & 1:
                    continue
                for h in range(N):
                    if e == h or S >> h & 1:
                        continue
                    T = S | (1 << h)
                    yield row([(offset + (T | (1 << e)), F(1)),
                               (offset + T, F(-1)),
                               (offset + (S | (1 << e)), F(-1)),
                               (offset + S, F(1))])
    for S in range(SIZE):
        for e in range(N):
            if S >> e & 1:
                continue
            T = S | (1 << e)
            yield {T: F(1), S: F(-1), SIZE + T: F(-1), SIZE + S: F(1)}
            yield {SIZE + T: F(1), SIZE + S: F(-1), T: -ETA, S: ETA}
    for t in range(K):
        S = (1 << t) - 1
        for e in range(N):
            if e == t or S >> e & 1:
                continue
            yield row([(SIZE + (S | (1 << e)), F(1)), (SIZE + S, F(-1)),
                       (SIZE + (S | (1 << t)), F(-1)), (SIZE + S, F(1))])

rows = list(inequalities())
certs = json.loads(Path(__file__).with_name('submodular_K4_exact_duals.json').read_text())
assert len(certs) == 16
patterns = set()
lower_bounds = []
for cert in certs:
    O = cert['O']
    assert len(O) == K and len(set(O)) == K and all(0 <= i < N for i in O)
    patterns.add(sum(1 << i for i in O if i < K))
    coeff = [F(0)] * (2 * SIZE)
    for i, s in cert['dual_nonzero']:
        y = F(s)
        assert y <= 0
        for v, a in rows[i].items():
            coeff[v] += y * a
    z = list(map(F, cert['equality_dual']))
    for v, a in zip([0, SIZE, sum(1 << i for i in O)], z):
        coeff[v] += a
    coeff[(1 << K) - 1] -= 1
    assert all(x == 0 for x in coeff), O
    assert z[2] == F(cert['bound']) >= F(23, 41)
    lower_bounds.append(z[2])
assert patterns == set(range(16))
assert min(lower_bounds) == F(23, 41)

# Matching explicit witness from the general family, m=2, eta_u=1.
r, m = F(3, 4), 2
D = 1 + (ETA - 1) * r ** m
d = [r ** min(t, m) / (K * D) for t in range(K)]
f, g = [], []
for S in range(SIZE):
    bsum = sum((d[t] for t in range(K) if S >> t & 1), F(0))
    cut = sum((d[t] for t in range(m) if S >> t & 1), F(0))
    y = sum(S >> t & 1 for t in range(K, N))
    f.append(bsum + F(y, K) * (1 - cut))
    g.append(ETA * bsum + F(y, K) * (ETA / D - ETA * cut))
assert f[0] == g[0] == 0
hit_lower = hit_upper = False
for S in range(SIZE):
    for e in range(N):
        if S >> e & 1:
            continue
        T = S | (1 << e)
        df, dg = f[T] - f[S], g[T] - g[S]
        assert 0 <= df <= dg <= ETA * df
        hit_lower |= df > 0 and df == dg
        hit_upper |= df > 0 and dg == ETA * df
        for h in range(N):
            if h == e or S >> h & 1:
                continue
            Sh = S | (1 << h)
            Th = T | (1 << h)
            assert f[Th] - f[Sh] <= df
            assert g[Th] - g[Sh] <= dg
assert hit_lower and hit_upper
assert max(f[S] for S in range(SIZE) if S.bit_count() <= K) == 1
for t in range(K):
    S = (1 << t) - 1
    chosen = g[S | (1 << t)] - g[S]
    assert chosen > 0
    assert all(chosen >= g[S | (1 << e)] - g[S]
               for e in range(N) if not S >> e & 1)
assert f[(1 << K) - 1] == F(23, 41)
U = 1 - F(9, 11) ** 4
assert F(23, 41) - U == F(5463, 600281) > 0

# Dossier stopping-rule counterexample: f is modular, g=min(1,f).
f2 = [F((S & 3).bit_count()) for S in range(16)]
g2 = [min(F(1), x) for x in f2]
S = 0
ratios = []
for t in range(2):
    candidates = [e for e in range(4) if not S >> e & 1]
    e = max(candidates, key=lambda e: g2[S | (1 << e)] - g2[S])
    if g2[S | (1 << e)] - g2[S] <= 0:
        break
    M = max(f2[S | (1 << h)] - f2[S] for h in candidates)
    ratios.append(M / (f2[S | (1 << e)] - f2[S]))
    S |= 1 << e
assert max(ratios) == 1 and f2[S] / 2 == F(1, 2) < F(3, 4)

print('PASS: 16 orbit representatives, exact rational dual identities')
print('PASS: matching full-lattice witness; rho_sub(4, 3/2) = 23/41')
print('PASS: 23/41 - U_4(3/2) = 5463/600281 > 0')
print('PASS: stopped-run counterexample has ratio 1/2 < L_2(1)=3/4')

# Exact checks of the new small-n minimax proof on the explicit submodular
# witness above, for every output K-set. The general proof is in the report.
from itertools import combinations
full = SIZE - 1
for budget in range((N + 1)//2, N):
    ell = N - budget
    feasible = [S for S in range(SIZE) if S.bit_count() == budget]
    T = max(feasible, key=lambda S: g[S])
    O = max(feasible, key=lambda S: f[S])
    R, Rstar = full ^ T, full ^ O
    h = lambda A: f[full] - f[full ^ A]
    assert h(R) <= ETA * h(Rstar)
    subsets = [sum(1 << i for i in J) for J in combinations(
        [i for i in range(N) if T >> i & 1], ell)]
    mean = sum((h(A) for A in subsets), F(0)) / len(subsets)
    assert h(Rstar) <= mean <= F(ell,budget)*h(T) <= F(ell,budget)*f[T]
    assert f[O] <= (1 + (ETA-1)*F(ell,budget))*f[T]
print('PASS: complement-loss inequalities in the small-n minimax proof')
