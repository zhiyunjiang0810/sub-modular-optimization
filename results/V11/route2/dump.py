import sys
import numpy as np
from lp_sym import solve, rho

K = int(sys.argv[1]); eta = float(eval(sys.argv[2])); r = int(sys.argv[3]); m = int(sys.argv[4])
res, Z, zi, gi, nz, n = solve(K, eta, r, m)
x = res.x
rr, j = rho(K, eta)
k1 = (K - 1) * eta + 1.0; q = (K - 1) * eta / k1
print(f"K={K} eta={eta} n={n} m={m}: val={res.fun:.8f} rho={rr:.8f} j*={j} k1={k1} q={q}")
print("\ngamma(s):")
for s in range(n + 1):
    if ("F", s) in gi:
        print(f"  gamma({s}) = {x[gi[('F', s)]]:.6f}")
print("Gamma(s,a) (deviating cells):")
for k in sorted(kk for kk in gi if kk[0] == "D"):
    print(f"  Gamma({k[1]},{k[2]}) = {x[gi[k]]:.6f}")
print("\nf(a,b,c)  [a=|S cap O|, b=|S cap T|, c=|S cap X|]")
for a in range(K + 1):
    for b in range(K + 1):
        row = " ".join(f"{x[zi[(a,b,c)]]:7.4f}" for c in range(r + 1))
        print(f"  a={a} b={b}: {row}")
print("\nT-chain gains d_t = f(0,t+1,0)-f(0,t,0):")
for t in range(K):
    print(f"  d_{t} = {x[zi[(0,t+1,0)]] - x[zi[(0,t,0)]]:.6f}   "
          f"(claimed: {q**t/k1 if t < j else q**j/(K*eta):.6f})")
print("O-chain gains:")
for t in range(K):
    print(f"  {x[zi[(t+1,0,0)]] - x[zi[(t,0,0)]]:.6f}")
print("competitor gains a_t = f(1,t,0)-f(0,t,0):")
for t in range(K + 1):
    print(f"  a_{t} = {x[zi[(1,t,0)]] - x[zi[(0,t,0)]]:.6f}   "
          f"(claimed: {q**min(t,j)/K:.6f})")
print("X gains at T-prefixes: f(0,t,1)-f(0,t,0):")
for t in range(K + 1):
    print(f"  {x[zi[(0,t,1)]] - x[zi[(0,t,0)]]:.6f}")
