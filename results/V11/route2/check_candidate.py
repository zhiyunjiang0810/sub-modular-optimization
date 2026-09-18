"""ROUTE-TWO scratch: is the hand-built candidate f (ratio 5/7 < 3/4)
compatible with SOME predictor tilde f obeying the band and making S the
tilde-f-maximal 3-set?  Exact rational feasibility via sympy linear solve is
awkward, so we use an LP feasibility test with exact-rational verification of
the answer's sign.  eta_u = 2, eta_o = 1.
"""
from fractions import Fraction
import itertools
import numpy as np
from scipy.optimize import linprog

# ground set 0=c1, 1=c2, 2=s, 3=o
n, K = 4, 3
S = 0b0111        # {c1,c2,s}
Ostar = 0b1011    # {c1,c2,o}

F = {
    0b0000: 0,
    0b0001: 1,    # c1
    0b0010: 1,    # c2
    0b0100: 3,    # s
    0b1000: 5,    # o
    0b0011: 2,    # c1c2
    0b0101: 4,    # c1 s
    0b0110: 4,    # c2 s
    0b1001: 6,    # c1 o
    0b1010: 6,    # c2 o
    0b1100: 5,    # s o
    0b0111: 5,    # c1c2s = S
    0b1011: 7,    # c1c2o = O*
    0b1101: 6,    # c1 s o
    0b1110: 6,    # c2 s o
    0b1111: 7,
}


def card(A):
    return bin(A).count("1")


def check_f():
    ok = True
    for A in range(16):
        for e in range(n):
            if A & (1 << e):
                continue
            if F[A | (1 << e)] < F[A]:
                print("monotonicity fails", A, e); ok = False
            for e2 in range(n):
                if e2 == e or (A & (1 << e2)):
                    continue
                B = A | (1 << e2)
                if F[B | (1 << e)] - F[B] > F[A | (1 << e)] - F[A]:
                    print("submodularity fails", bin(A), e, e2); ok = False
    for A in range(16):
        if card(A) == K and F[A] > F[Ostar]:
            print("O* not optimal", bin(A)); ok = False
    return ok


def feasible_tilde(eta):
    # variables g(A), A in 0..15
    nv = 16
    A_ub, b_ub = [], []
    A_eq, b_eq = [], []
    r = [0.0] * nv; r[0] = 1.0; A_eq.append(r); b_eq.append(0.0)
    for A in range(16):
        for e in range(n):
            if A & (1 << e):
                continue
            Ae = A | (1 << e)
            d = F[Ae] - F[A]
            # g(Ae)-g(A) <= d
            r = [0.0] * nv; r[Ae] = 1.0; r[A] = -1.0
            A_ub.append(r); b_ub.append(float(d))
            # g(Ae)-g(A) >= d/eta
            r = [0.0] * nv; r[A] = 1.0; r[Ae] = -1.0
            A_ub.append(r); b_ub.append(-float(d) / eta)
    for A in range(16):
        if card(A) == K:
            r = [0.0] * nv; r[A] = 1.0; r[S] = -1.0
            A_ub.append(r); b_ub.append(0.0)
    c = [0.0] * nv
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)] * nv, method="highs")
    return res


if __name__ == "__main__":
    print("f monotone submodular and O* optimal:", check_f())
    print("f(S)/f(O*) =", Fraction(F[S], F[Ostar]), "=", F[S] / F[Ostar],
          " claim K/(K+(eta-1)j) =", Fraction(3, 4))
    res = feasible_tilde(2.0)
    print("tilde f feasible?", res.success, res.message)
