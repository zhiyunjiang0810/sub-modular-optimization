"""ROUTE-TWO scratch: inspect the LP optimum's greedy trajectory profile."""
import numpy as np
from lp_full_instance import solve, V


def report(K, eta):
    n = 2 * K
    NS = 1 << n
    res = solve(K, eta, verbose=False)
    x = res.x
    f = lambda S: x[S]
    ft = lambda S: x[NS + S]
    jstar = min(range(K), key=lambda j: V(K, eta, j))
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    print(f"\n=== K={K} eta={eta}  LP={res.fun:.8f}  minV={V(K,eta,jstar):.8f} j*={jstar}")
    R = 1.0
    for t in range(K):
        St = (1 << t) - 1
        Ste = St | (1 << t)
        g = f(Ste) - f(St)
        ms = [f(St | (1 << i)) - f(St) for i in range(K, n)]
        print(f" t={t}: f(S^t)={f(St):.6f} R_t={1-f(St):.6f} g_t={g:.6f} "
              f"m_i,t={['%.6f'%v for v in ms]}")
        # predicted
        if t < jstar:
            gp, mp = R / k1, R / K
        else:
            Rj = q ** jstar
            gp, mp = Rj / (K * eta), Rj / K
        print(f"       predicted g={gp:.6f} m={mp:.6f}")
        R -= g
    # predictor gains along the trajectory
    for t in range(K):
        St = (1 << t) - 1
        dte = ft(St | (1 << t)) - ft(St)
        dto = [ft(St | (1 << i)) - ft(St) for i in range(K, n)]
        print(f" t={t}: dt_e={dte:.6f}  dt_o={['%.6f'%v for v in dto]}")


if __name__ == '__main__':
    report(2, 1.5)
    report(3, 1.5)
    report(3, 2.5)
    report(4, 1.5)
