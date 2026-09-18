"""ROUTE-TWO scratch: which constraint families does the per-instance bound
need?  Variants: restrict the tilde-f-maximality family and/or the
f-optimality family and see how the LP minimum moves.
"""
import numpy as np
from fractions import Fraction
from scipy.optimize import linprog


def card(A):
    return bin(A).count("1")


def lp(n, K, eta, S, Ostar, maxtilde="all", opt="all"):
    N = 1 << n
    nv = 2 * N
    fi = lambda A: A
    gi = lambda A: N + A
    A_ub, b_ub, A_eq, b_eq = [], [], [], []
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
            for e2 in range(n):
                if e2 == e or (A & (1 << e2)):
                    continue
                B = A | (1 << e2); Be = B | (1 << e)
                r = row(); r[fi(Be)] += 1.0; r[fi(B)] -= 1.0
                r[fi(Ae)] -= 1.0; r[fi(A)] += 1.0
                A_ub.append(r); b_ub.append(0.0)
            r = row(); r[gi(Ae)] += 1.0; r[gi(A)] -= 1.0
            r[fi(Ae)] -= 1.0; r[fi(A)] += 1.0
            A_ub.append(r); b_ub.append(0.0)
            r = row(); r[gi(A)] += 1.0; r[gi(Ae)] -= 1.0
            r[fi(Ae)] += 1.0 / eta; r[fi(A)] -= 1.0 / eta
            A_ub.append(r); b_ub.append(0.0)

    for A in range(N):
        if card(A) != K:
            continue
        inter = card(A & S)
        take_mt = (maxtilde == "all"
                   or (maxtilde == "opt" and A == Ostar)
                   or (maxtilde == "swap1" and inter == K - 1)
                   or (maxtilde == "swap1+opt" and (inter == K - 1 or A == Ostar)))
        take_op = (opt == "all"
                   or (opt == "swap1" and inter == K - 1)
                   or (opt == "none" and False))
        if take_mt:
            r = row(); r[gi(A)] = 1.0; r[gi(S)] = -1.0
            A_ub.append(r); b_ub.append(0.0)
        if take_op:
            r = row(); r[fi(A)] = 1.0; r[fi(Ostar)] = -1.0
            A_ub.append(r); b_ub.append(0.0)

    r = row(); r[fi(Ostar)] = 1.0; A_eq.append(r); b_eq.append(1.0)
    c = row(); c[fi(S)] = 1.0
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)] * nv, method="highs")
    return res.fun if res.success else None


def main():
    cases = [(4, 3, 1), (5, 3, 2), (5, 2, 2), (6, 3, 3), (6, 4, 2)]
    for (n, K, j) in cases:
        for eta in (Fraction(3, 2), Fraction(2)):
            S = sum(1 << i for i in range(K))
            Ostar = sum(1 << i for i in list(range(K - j)) + list(range(K, K + j)))
            claim = float(Fraction(K) / (Fraction(K) + (eta - 1) * j))
            out = {}
            for mt in ("all", "opt", "swap1", "swap1+opt"):
                for op in ("all", "none"):
                    out[(mt, op)] = lp(n, K, float(eta), S, Ostar, mt, op)
            print(f"n={n} K={K} j={j} eta={eta} claim={claim:.6f}")
            for k, v in out.items():
                mark = "=claim" if v is not None and abs(v - claim) < 1e-7 else ""
                print(f"    maxtilde={k[0]:<10} opt={k[1]:<5} min={v:.6f} {mark}")


if __name__ == "__main__":
    main()
