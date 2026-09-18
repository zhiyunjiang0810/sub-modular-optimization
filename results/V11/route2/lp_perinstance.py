"""ROUTE-TWO scratch: LP test of the per-instance claim
    f(S) >= K/(K+(eta-1)*|O* \ S|) * f(O*)
for S a tilde-f-maximizing K-set, O* an f-optimal K-set.

WLOG for this direction: eta_o = 1, eta_u = eta (rescaling tilde f does not
move its argmax and maps (eta_u,eta_o) -> (c eta_u, eta_o/c)).

Variables: f(A), g(A)=tilde f(A) for all A subset of N.  All constraints are
linear, so the worst case is an LP.  Floats here (exploration only); the
decisions are re-checked exactly in lp_exact_check.py.
"""
import itertools
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog


def subsets(n):
    return list(range(1 << n))


def bits(A):
    out = []
    i = 0
    while (1 << i) <= A:
        if A & (1 << i):
            out.append(i)
        i += 1
    return out


def card(A):
    return bin(A).count("1")


def solve(n, K, eta, S, Ostar, verbose=False):
    N = 1 << n
    # variable order: f(A) for A in 0..N-1, then g(A)
    nv = 2 * N

    def fi(A):
        return A

    def gi(A):
        return N + A

    A_ub, b_ub, A_eq, b_eq = [], [], [], []

    def row():
        return [0.0] * nv

    # f(empty)=0, g(empty)=0
    r = row(); r[fi(0)] = 1.0; A_eq.append(r); b_eq.append(0.0)
    r = row(); r[gi(0)] = 1.0; A_eq.append(r); b_eq.append(0.0)

    for A in range(N):
        for e in range(n):
            if A & (1 << e):
                continue
            Ae = A | (1 << e)
            # monotone: f(A) - f(Ae) <= 0
            r = row(); r[fi(A)] = 1.0; r[fi(Ae)] = -1.0
            A_ub.append(r); b_ub.append(0.0)
            # submodular: d_e(A) >= d_e(A+e') for e' not in A+e
            for e2 in range(n):
                if e2 == e or (A & (1 << e2)):
                    continue
                B = A | (1 << e2)
                Be = B | (1 << e)
                # f(Be)-f(B) - f(Ae)+f(A) <= 0
                r = row()
                r[fi(Be)] += 1.0; r[fi(B)] -= 1.0
                r[fi(Ae)] -= 1.0; r[fi(A)] += 1.0
                A_ub.append(r); b_ub.append(0.0)
            # band with eta_o = 1, eta_u = eta:
            #   g(Ae)-g(A) <= f(Ae)-f(A)
            r = row()
            r[gi(Ae)] += 1.0; r[gi(A)] -= 1.0
            r[fi(Ae)] -= 1.0; r[fi(A)] += 1.0
            A_ub.append(r); b_ub.append(0.0)
            #   g(Ae)-g(A) >= (f(Ae)-f(A))/eta
            r = row()
            r[gi(A)] += 1.0; r[gi(Ae)] -= 1.0
            r[fi(Ae)] += 1.0 / eta; r[fi(A)] -= 1.0 / eta
            A_ub.append(r); b_ub.append(0.0)

    Ksets = [A for A in range(N) if card(A) == K]
    for A in Ksets:
        # g(S) >= g(A)
        r = row(); r[gi(A)] = 1.0; r[gi(S)] = -1.0
        A_ub.append(r); b_ub.append(0.0)
        # f(Ostar) >= f(A)
        r = row(); r[fi(A)] = 1.0; r[fi(Ostar)] = -1.0
        A_ub.append(r); b_ub.append(0.0)

    # normalise f(Ostar) = 1
    r = row(); r[fi(Ostar)] = 1.0; A_eq.append(r); b_eq.append(1.0)

    c = row(); c[fi(S)] = 1.0
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)] * nv, method="highs")
    if not res.success:
        return None, None
    return res.fun, res.x


def main():
    for n in (3, 4, 5):
        for K in (2, 3):
            if K > n:
                continue
            for eta in (Fraction(3, 2), Fraction(2), Fraction(3)):
                etaf = float(eta)
                for j in range(0, min(K, n - K) + 1):
                    # S = {0..K-1}; O* shares K-j elements with S
                    S = sum(1 << i for i in range(K))
                    common = list(range(K - j))
                    outside = list(range(K, K + j))
                    if K + j > n:
                        continue
                    Ostar = sum(1 << i for i in common + outside)
                    val, _ = solve(n, K, etaf, S, Ostar)
                    pred = float(Fraction(K, 1) / (Fraction(K) + (eta - 1) * j))
                    flag = "OK " if val is None or val >= pred - 1e-7 else "VIOL"
                    tight = "tight" if val is not None and abs(val - pred) < 1e-7 else ""
                    print(f"n={n} K={K} eta={eta} j={j}  LPmin={val}  claim={pred:.6f}  {flag} {tight}")


if __name__ == "__main__":
    main()
