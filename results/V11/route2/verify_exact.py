"""Exact (Fraction) verification, on the FULL set lattice, of an instance produced by
the reduced LP: monotonicity, submodularity, the two band inequalities, OPT=f(O)=1,
f(T)=rho_K, and the hideability form of the surrogate.

Usage: python3 verify_exact.py K eta_num eta_den r m
"""
import sys, itertools
from fractions import Fraction as Fr
import numpy as np
from lp_sym import solve, rho

K = int(sys.argv[1]); en = int(sys.argv[2]); ed = int(sys.argv[3])
r = int(sys.argv[4]); m = int(sys.argv[5])
eta = Fr(en, ed); etaf = en / ed
eu, eo = Fr(1), eta                      # split (1, eta); general split = rescale ftilde

res, Z, zi, gi, nz, n = solve(K, etaf, r, m)
assert res.success
x = res.x

MAXDEN = 10 ** 6
F = {z: Fr(x[zi[z]]).limit_denominator(MAXDEN) for z in Z}
G = {k: Fr(x[gi[k]]).limit_denominator(MAXDEN) for k in gi}

def gkey(z):
    s = sum(z)
    return ("D", s, z[0]) if (z[0] >= 2 and s <= m) else ("F", s)
def ft(z): return G[gkey(z)]

# ---- exact repair: enforce the equalities we know must hold, then re-check ----
k1 = (K - 1) * eta + 1; q = (K - 1) * eta / k1
jstar = min(range(K), key=lambda j: float(1 - (float(q)) ** j * (1 - (K - j) / (K * etaf))))
rho_exact = 1 - q ** jstar * (1 - Fr(K - jstar, K) / eta)

cap = (K, K, r)
E = [(1, 0, 0), (0, 1, 0), (0, 0, 1)]
def add(z, e):
    w = tuple(z[i] + e[i] for i in range(3))
    return w if all(0 <= w[i] <= cap[i] for i in range(3)) else None

bad = []
def chk(cond, tag):
    if not cond: bad.append(tag)

chk(F[(0, 0, 0)] == 0, "f(empty)=0")
chk(ft((0, 0, 0)) == 0, "ftilde(empty)=0")
chk(F[(K, 0, 0)] == 1, f"f(O)=1 (got {F[(K,0,0)]})")
chk(F[(0, K, 0)] <= rho_exact, f"f(T)<=rho (got {F[(0,K,0)]} vs {rho_exact})")
for z in Z:
    if sum(z) == K: chk(F[z] <= 1, f"OPT cap at {z}")
for z in Z:
    for e in E:
        w = add(z, e)
        if w is None: continue
        chk(F[w] >= F[z], f"monotone {z}->{w}")
        d = F[w] - F[z]; dt = ft(w) - ft(z)
        chk(dt >= d / eu, f"band lower {z}->{w}: {dt} < {d}/{eu}")
        chk(dt <= eo * d, f"band upper {z}->{w}: {dt} > {eo}*{d}")
    for i, e in enumerate(E):
        for jj in range(i, 3):
            e2 = E[jj]
            w1 = add(z, e); w2 = add(z, e2)
            w12 = add(w1, e2) if w1 else None
            if w1 is None or w2 is None or w12 is None: continue
            if i == jj and z[i] + 2 > cap[i]: continue
            chk(F[w1] + F[w2] >= F[z] + F[w12], f"submod {z} {e} {e2}")

# band tightness: both ends of the band attained somewhere
lo = any(ft(add(z, e)) - ft(z) == (F[add(z, e)] - F[z]) / eu
         for z in Z for e in E if add(z, e) and F[add(z, e)] > F[z])
hi = any(ft(add(z, e)) - ft(z) == eo * (F[add(z, e)] - F[z])
         for z in Z for e in E if add(z, e) and F[add(z, e)] > F[z])
print(f"K={K} eta={eta} r={r} m={m} n={n}: j*={jstar} rho={rho_exact}={float(rho_exact):.8f}")
print(f"  f(T) = {F[(0,K,0)]} = {float(F[(0,K,0)]):.8f}")
print(f"  violations: {len(bad)}")
for b in bad[:12]: print("   ", b)
print(f"  eta_u end attained: {lo}   eta_o end attained: {hi}")
print("  d_t (T-chain):", [str(F[(0, t + 1, 0)] - F[(0, t, 0)]) for t in range(K)])
print("  claimed     :", [str(q ** t / k1 if t < jstar else q ** jstar / (K * eta)) for t in range(K)])
print("  A_t (O-gain at T_t):", [str(F[(1, t, 0)] - F[(0, t, 0)]) for t in range(K + 1)])
print("  claimed            :", [str(q ** min(t, jstar) / K) for t in range(K + 1)])
