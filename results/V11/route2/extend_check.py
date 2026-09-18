"""Capping-extension check.

Take the LP-optimal count-grid instance with r0 = m+1 generic elements, verify that
f is saturated (constant) at every level >= s0 <= m+1, then define for arbitrary
r >= r0:      f_ext(a,b,c) := f(a,b,min(c,r0)),   ftilde_ext likewise,
and verify ALL constraints of the extended instance exactly (Fractions).
"""
import sys, itertools
from fractions import Fraction as Fr
from lp_sym import solve

K = int(sys.argv[1]); en, ed = int(sys.argv[2]), int(sys.argv[3])
m = int(sys.argv[4]); rbig = int(sys.argv[5])
eta = Fr(en, ed); eu, eo = Fr(1), eta
r0 = m + 1
res, Z, zi, gi, nz, n0 = solve(K, float(eta), r0, m)
assert res.success
x = res.x
F0 = {z: Fr(x[zi[z]]).limit_denominator(10 ** 7) for z in Z}
G0 = {k: Fr(x[gi[k]]).limit_denominator(10 ** 7) for k in gi}

k1 = (K - 1) * eta + 1; q = (K - 1) * eta / k1
V = [1 - q ** j * (1 - Fr(K - j, K) / eta) for j in range(K)]
rho = min(V)
print(f"K={K} eta={eta} m={m} r0={r0}: LP f(T)={F0[(0,K,0)]} rho={rho} "
      f"match={F0[(0,K,0)]==rho}")

# saturation level of the base table
smax = max(F0.values())
sat = min(s for s in range(0, K + K + r0 + 1)
          if all(F0[z] == smax for z in Z if sum(z) >= s))
print(f"  max f = {smax}; f is constant on every level >= {sat} (m+1 = {m+1})")

def Fe(a, b, c): return F0[(a, b, min(c, r0))]
def gkey(s, a): return ("D", s, a) if (a >= 2 and s <= m) else ("F", s)
def fte(a, b, c):
    s = a + b + c
    k = gkey(min(s, K + K + r0), a) if s > m else gkey(s, a)
    # beyond the base grid the surrogate is the (constant) flat tail gamma(>=r0 level)
    if s > m:
        return G0[("F", min(s, K + K + r0))] if ("F", min(s, K + K + r0)) in G0 else G0[("F", K + K + r0)]
    return G0[k]

cap = (K, K, rbig); E = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
def add(z, e):
    w = tuple(z[i] + e[i] for i in range(3))
    return w if all(0 <= w[i] <= cap[i] for i in range(3)) else None
ZZ = [(a, b, c) for a in range(K + 1) for b in range(K + 1) for c in range(rbig + 1)]
bad = []
for z in ZZ:
    if sum(z) == K and Fe(*z) > 1: bad.append(("cap", z))
    for e in E:
        w = add(z, e)
        if w is None: continue
        d = Fe(*w) - Fe(*z); dt = fte(*w) - fte(*z)
        if d < 0: bad.append(("mon", z, e))
        if dt < d / eu: bad.append(("lo", z, e, d, dt))
        if dt > eo * d: bad.append(("hi", z, e, d, dt))
    for i, e in enumerate(E):
        for j2 in range(i, 3):
            e2 = E[j2]; w1 = add(z, e); w2 = add(z, e2); w12 = add(w1, e2) if w1 else None
            if w1 is None or w2 is None or w12 is None: continue
            if i == j2 and z[i] + 2 > cap[i]: continue
            if Fe(*w1) + Fe(*w2) < Fe(*z) + Fe(*w12): bad.append(("sub", z, e, e2))
print(f"  extended to r={rbig} (n={2*K+rbig}): f(O)={Fe(K,0,0)} f(T)={Fe(0,K,0)} "
      f"violations={len(bad)}")
for b in bad[:8]: print("    ", b)
