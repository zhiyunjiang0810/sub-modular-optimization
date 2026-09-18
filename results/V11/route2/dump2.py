import sys
import numpy as np
import lp_sym2, lp_sym
from lp_sym import rho

K = int(sys.argv[1]); eta = float(eval(sys.argv[2])); W = int(sys.argv[3]); m = int(sys.argv[4])
res, Z, zi, gi, nz = lp_sym2.solve(K, eta, W, m)
x = res.x
rr, j = rho(K, eta)
k1 = (K - 1) * eta + 1.0; q = (K - 1) * eta / k1
print(f"[2-type, T-independent] K={K} eta={eta}: val={res.fun:.8f} rho={rr:.8f} q={q} k1={k1}")
print(" gamma:", [f"{x[gi[('F',s)]]:.5f}" for s in range(W + K + 1) if ('F', s) in gi])
print(" Gamma(s,a>=2):", {k[1:]: round(x[gi[k]], 5) for k in sorted(gi) if k[0] == 'D'})
print(" f(a,w):")
for a in range(K + 1):
    print(f"   a={a}: " + " ".join(f"{x[zi[(a,w)]]:7.4f}" for w in range(min(W, 8) + 1)))
g = [x[zi[(0, w + 1)]] - x[zi[(0, w)]] for w in range(min(W, 7))]
A = [x[zi[(1, w)]] - x[zi[(0, w)]] for w in range(min(W, 8))]
print(" g_w:", [f"{v:.5f}" for v in g])
print(" A_w:", [f"{v:.5f}" for v in A])
print(" check g_w >= A_w - (eta-1)/eta A_{w+1}:",
      [f"{g[w] - (A[w] - (eta - 1) / eta * A[w + 1]):+.2e}" for w in range(len(g) - 1)])
print(" claimed d_t:", [f"{(q**t/k1 if t < j else q**j/(K*eta)):.5f}" for t in range(K)])
