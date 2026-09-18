import json, sys
import numpy as np
from lp_sym import solve, rho

out = []
for K in [2, 3, 4, 5, 6]:
    for eta in [1.05, 1.2, 1.5, 1.9, 2.0, 2.5, 3.0, 3.7, 4.5, 6.0, 8.0]:
        for m in [2 * K, 2 * K + 2]:
            r = 4
            try:
                res, *_ = solve(K, eta, r, m)
            except Exception as ex:
                out.append(dict(K=K, eta=eta, m=m, err=str(ex))); continue
            rr, j = rho(K, eta)
            val = res.fun if res.success else None
            out.append(dict(K=K, eta=eta, m=m, r=r, val=val, rho=rr, jstar=j,
                            diff=(val - rr) if val is not None else None))
            print(f"K={K} eta={eta} m={m}: val={val:.8f} rho={rr:.8f} j*={j} diff={val-rr:+.2e}",
                  flush=True)
json.dump(out, open("sweep_results.json", "w"), indent=1)
