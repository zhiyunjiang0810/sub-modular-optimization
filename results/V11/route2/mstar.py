"""Find the smallest truncation length m that makes the hideable family attain rho_K exactly."""
import sys
import numpy as np
from lp_sym import solve, rho

for K in [2, 3, 4, 5, 6, 7]:
    for eta in [1.2, 1.5, 2.5, 4.0]:
        rr, j = rho(K, eta)
        found = None
        for m in range(K, 6 * K + 6):
            r = max(4, m - 2 * K + 4)
            res, *_ = solve(K, eta, r, m)
            if not res.success:
                continue
            d = res.fun - rr
            if d < 1e-9:
                found = (m, r, res.fun, d)
                break
        print(f"K={K} eta={eta}: rho={rr:.8f}  smallest exact m = {found[0]} "
              f"(n={2*K+found[1]}, val={found[2]:.10f}, diff={found[3]:+.1e})   "
              f"2K={2*K}  K+j*+1={K+j+1}  j*={j}", flush=True)
