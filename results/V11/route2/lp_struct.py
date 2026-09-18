"""Symmetrise the LP optimum over Sym(O) and print f, ftilde as a table indexed by
(S cap B, |S cap O|).  Also report the greedy trajectory gains d_t, a_t."""
import sys, itertools
import numpy as np
from lp_rho import solve, rho

K = int(sys.argv[1]); eta = float(eval(sys.argv[2]))
eu, eo = 1.0, eta
res, (B, O, X, n, NS, mB, mO) = solve(K, eu, eo, 0)
assert res.success
f = res.x[:NS].copy(); g = res.x[NS:].copy()

# symmetrise over permutations of O
fs = np.zeros(NS); gs = np.zeros(NS)
perms = list(itertools.permutations(range(K)))
for S in range(NS):
    for p in perms:
        T = S & ((1 << K) - 1)          # B-part
        for i in range(K):
            if S >> (K + i) & 1:
                T |= 1 << (K + p[i])
        fs[S] += f[T]; gs[S] += g[T]
fs /= len(perms); gs /= len(perms)

print(f"K={K} eta={eta}  LP opt = {res.fun:.10f}  rho={rho(K,eta)[0]:.10f}")
k1 = (K - 1) * eta + 1.0; q = (K - 1) * eta / k1
print(f"k1={k1}  q={q}")
print("\n  (Bset, |S cap O|) :   f        ftilde")
for bs in range(1 << K):
    lbl = "".join("b%d" % t for t in range(K) if bs >> t & 1) or "-"
    for i in range(K + 1):
        S = bs
        for t in range(i):
            S |= 1 << (K + t)
        print(f"  ({lbl:>8s}, {i}) : {fs[S]:9.6f} {gs[S]:9.6f}")

print("\ngreedy trajectory:")
St = 0
for t in range(K):
    Sb = St | (1 << t)
    So = St | (1 << K)
    d = fs[Sb] - fs[St]; a = fs[So] - fs[St]
    dt = gs[Sb] - gs[St]; at = gs[So] - gs[St]
    j = None
    print(f"  t={t}: F_t={fs[St]:.6f}  d_t={d:.6f}  a_t={a:.6f}  a_t/d_t={a/d if d else float('nan'):.6f}"
          f"   ftilde gains: b={dt:.6f} o={at:.6f}")
    St = Sb
print(f"  f(B)={fs[mB]:.6f}  f(O)={fs[mO]:.6f}")

print("\npredicted d_t and a_t from the claimed closed form:")
for jj in range(K):
    ds = [q ** t / k1 for t in range(jj)] + [q ** jj / (K * eta)] * (K - jj)
    aa = [q ** min(t, jj) / K for t in range(K)]
    print(f"  j={jj}: d={['%.6f'%x for x in ds]} sum={sum(ds):.6f} a={['%.6f'%x for x in aa]}")
