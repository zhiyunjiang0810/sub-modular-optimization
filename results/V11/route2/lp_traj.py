"""Trajectory LP: the three necessary conditions
   (ii)  K*A_t + sum_{s<t} p_s >= 1          [OPT + submodularity]
   (iii) p_t >= A_t - ((eta-1)/eta) A_{t+1}  [level-(t+1) flatness of the surrogate]
   (iv)  A_t >= A_{t+1}                      [submodularity]
minimise sum_t p_t.  Claim: the value is exactly rho_K(eta) = min_j V_j(eta).
"""
import numpy as np
from scipy.optimize import linprog


def traj(K, eta):
    # vars: A_0..A_K (K+1), p_0..p_{K-1} (K)
    nA = K + 1; nv = nA + K
    A_ub, b_ub = [], []
    def ub(co, r):
        row = np.zeros(nv)
        for i, c in co: row[i] += c
        A_ub.append(row); b_ub.append(r)
    for t in range(K):
        ub([(nA + t, -1.0), (t, 1.0), (t + 1, -(eta - 1) / eta)], 0.0)     # (iii)
        ub([(t, -float(K))] + [(nA + s, -1.0) for s in range(t)], -1.0)    # (ii)
    ub([(K, -float(K))] + [(nA + s, -1.0) for s in range(K)], -1.0)
    for t in range(K):
        ub([(t + 1, 1.0), (t, -1.0)], 0.0)                                 # (iv)
    c = np.zeros(nv); c[nA:] = 1.0
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  bounds=[(0, None)] * nv, method="highs")
    return res


def rho(K, eta):
    k1 = (K - 1) * eta + 1.0; q = (K - 1) * eta / k1
    v = [1 - q ** j * (1 - (K - j) / (K * eta)) for j in range(K)]
    return min(v), int(np.argmin(v)), q, k1


if __name__ == "__main__":
    worst = 0.0
    for K in range(2, 13):
        for eta in [1.01, 1.1, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.5, 7.0, 10.0, 20.0]:
            res = traj(K, eta); r, j, q, k1 = rho(K, eta)
            d = abs(res.fun - r); worst = max(worst, d)
            if d > 1e-9:
                print(f"MISMATCH K={K} eta={eta}: LP={res.fun:.10f} rho={r:.10f}")
    print(f"trajectory LP == rho_K on the whole grid, max |diff| = {worst:.2e}")
    K, eta = 3, 1.5
    res = traj(K, eta); r, j, q, k1 = rho(K, eta)
    print(f"\nK=3 eta=1.5: LP={res.fun}, rho={r}, j*={j}, q={q}, k1={k1}")
    print(" A_t =", np.round(res.x[:K + 1], 8), " (claimed", [q ** min(t, j) / K for t in range(K + 1)], ")")
    print(" p_t =", np.round(res.x[K + 1:], 8),
          " (claimed", [q ** t / k1 if t < j else q ** j / (K * eta) for t in range(K)], ")")
