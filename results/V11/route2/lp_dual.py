"""ROUTE-TWO scratch: dual certificate of the per-instance LP, to read off
which inequalities a hand proof must combine."""
import numpy as np
from fractions import Fraction
from scipy.optimize import linprog


def card(A):
    return bin(A).count("1")


def name(A, n):
    return "{" + ",".join(str(i) for i in range(n) if A & (1 << i)) + "}"


def build(n, K, eta, S, Ostar):
    N = 1 << n
    nv = 2 * N
    fi = lambda A: A
    gi = lambda A: N + A
    A_ub, b_ub, lbl = [], [], []
    A_eq, b_eq = [], []
    row = lambda: [0.0] * nv

    r = row(); r[fi(0)] = 1.0; A_eq.append(r); b_eq.append(0.0)
    r = row(); r[gi(0)] = 1.0; A_eq.append(r); b_eq.append(0.0)

    for A in range(N):
        for e in range(n):
            if A & (1 << e):
                continue
            Ae = A | (1 << e)
            r = row(); r[fi(A)] = 1.0; r[fi(Ae)] = -1.0
            A_ub.append(r); b_ub.append(0.0)
            lbl.append(f"mono f({name(A,n)})<=f({name(Ae,n)})")
            for e2 in range(n):
                if e2 == e or (A & (1 << e2)):
                    continue
                B = A | (1 << e2); Be = B | (1 << e)
                r = row(); r[fi(Be)] += 1.0; r[fi(B)] -= 1.0
                r[fi(Ae)] -= 1.0; r[fi(A)] += 1.0
                A_ub.append(r); b_ub.append(0.0)
                lbl.append(f"submod d_{e}({name(B,n)})<=d_{e}({name(A,n)})")
            r = row(); r[gi(Ae)] += 1.0; r[gi(A)] -= 1.0
            r[fi(Ae)] -= 1.0; r[fi(A)] += 1.0
            A_ub.append(r); b_ub.append(0.0)
            lbl.append(f"band-up  gd_{e}({name(A,n)})<=d_{e}({name(A,n)})")
            r = row(); r[gi(A)] += 1.0; r[gi(Ae)] -= 1.0
            r[fi(Ae)] += 1.0 / eta; r[fi(A)] -= 1.0 / eta
            A_ub.append(r); b_ub.append(0.0)
            lbl.append(f"band-lo  gd_{e}({name(A,n)})>=d_{e}({name(A,n)})/eta")

    for A in range(N):
        if card(A) != K:
            continue
        r = row(); r[gi(A)] = 1.0; r[gi(S)] = -1.0
        A_ub.append(r); b_ub.append(0.0)
        lbl.append(f"MAXTILDE  gf({name(A,n)})<=gf(S)")
        r = row(); r[fi(A)] = 1.0; r[fi(Ostar)] = -1.0
        A_ub.append(r); b_ub.append(0.0)
        lbl.append(f"OPT       f({name(A,n)})<=f(O*)")

    r = row(); r[fi(Ostar)] = 1.0; A_eq.append(r); b_eq.append(1.0)
    c = row(); c[fi(S)] = 1.0
    return c, A_ub, b_ub, A_eq, b_eq, lbl, fi, gi


def run(n, K, eta, S, Ostar):
    c, A_ub, b_ub, A_eq, b_eq, lbl, fi, gi = build(n, K, eta, S, Ostar)
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)] * (2 * (1 << n)), method="highs")
    print(f"--- n={n} K={K} eta={eta} S={name(S,n)} O*={name(Ostar,n)}  min f(S)={res.fun:.6f}")
    marg = res.ineqlin.marginals
    print("  active dual multipliers (|y|>1e-9), MAXTILDE / OPT / band only:")
    for y, L in zip(marg, lbl):
        if abs(y) > 1e-9 and (L.startswith("MAXTILDE") or L.startswith("OPT")):
            print(f"    y={-y:+.6f}  {L}")
    print("  primal f values:")
    for A in range(1 << n):
        print(f"    f({name(A,n)})={res.x[fi(A)]:.4f}  gf={res.x[gi(A)]:.4f}")


if __name__ == "__main__":
    # n=4, K=3, j=1: S={0,1,2}, O*={0,1,3}
    run(4, 3, 2.0, 0b0111, 0b1011)
