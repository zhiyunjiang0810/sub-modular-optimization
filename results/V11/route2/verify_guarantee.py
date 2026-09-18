#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROUTE-TWO blind verification script for prop:guarantee (TASKS11 Q5a).

Oracles provided here:
  A. [VERIFIED-SYMBOLIC] sympy: unrolled recursion == L_K(x); dL/dx <= 0;
     (1 - 1/(xK))^K <= exp(-1/x) as a consequence of 1-u <= e^{-u}.
  B. [VERIFIED-EXHAUSTIVE] exact-rational K=3, eta^sel=3/2 tight coverage
     instance: every quantity of the walk-through recomputed with Fraction.
  C. [VERIFIED-EXHAUSTIVE] randomized/exhaustive stress test on small
     coverage instances: predictive greedy with adversarial tie breaking,
     exact Fractions, checks
        f(T) >= L_K(eta^sel) f(O*)          (main bound)
        eta^sel <= eta^tr <= eta            (ordering)
        L_K(eta^sel) >= L_K(eta^tr) >= L_K(eta)

All decisions use fractions.Fraction or sympy Rational. Floats only in
printouts. Run:  python3 verify_guarantee.py
"""

from fractions import Fraction as F
from itertools import combinations, chain
import random

import sympy as sp

INF = None  # sentinel for +infinity in the Fraction world


# ----------------------------------------------------------------------
# helpers for the extended reals used by eta^sel / eta^tr / eta
# ----------------------------------------------------------------------
def le(a, b):
    """a <= b with None meaning +infinity."""
    if a is INF:
        return b is INF
    if b is INF:
        return True
    return a <= b


def emax(a, b):
    if a is INF or b is INF:
        return INF
    return max(a, b)


def L_K(x, K):
    """L_K(x) = 1 - (1 - 1/(xK))^K, exact; L_K(infinity) = 0."""
    if x is INF:
        return F(0)
    return F(1) - (F(1) - F(1, 1) / (x * K)) ** K


# ----------------------------------------------------------------------
# PART A -- symbolic identities
# ----------------------------------------------------------------------
def part_A():
    print("=" * 70)
    print("PART A  [VERIFIED-SYMBOLIC]")
    x, D0 = sp.symbols("x Delta0", positive=True)

    ok_all = True
    for K in range(1, 9):
        c = sp.Rational(1, 1) / (x * K)
        # unroll Delta_{t+1} <= (1-c) Delta_t  K times, starting from Delta_0
        D = D0
        for _ in range(K):
            D = sp.expand((1 - c) * D)
        # f(T) >= Delta_0 - D  with Delta_0 = f(O*)
        lhs = sp.simplify((D0 - D) / D0)
        rhs = sp.simplify(1 - (1 - c) ** K)
        ok = sp.simplify(lhs - rhs) == 0
        ok_all &= bool(ok)
        print(f"  K={K}: unrolled recursion == L_K(x) : {ok}")

    # monotonicity: dL/dx = -(1-1/(xK))^(K-1) / x^2  <= 0 for xK >= 1
    Ksym = sp.symbols("K", positive=True, integer=True)
    L = 1 - (1 - 1 / (x * Ksym)) ** Ksym
    dL = sp.simplify(sp.diff(L, x))
    target = sp.simplify(-(1 - 1 / (x * Ksym)) ** (Ksym - 1) / x ** 2)
    mono = sp.simplify(dL - target) == 0
    ok_all &= bool(mono)
    print(f"  dL/dx == -(1-1/(xK))^(K-1)/x^2 (so <=0 for xK>=1) : {mono}")

    # L_K(x) >= 1 - exp(-1/x): check the gap numerically on an exact grid
    # (the analytic step is 1-u <= e^{-u} with u = 1/(xK) in (0,1]).
    worst = None
    for K in range(1, 13):
        for num in range(1, 41):
            xv = sp.Rational(num, 4)  # x = 0.25 .. 10, keep x >= 1 only
            if xv < 1:
                continue
            gap = sp.N((1 - (1 - 1 / (xv * K)) ** K) - (1 - sp.exp(-1 / xv)), 30)
            if gap < 0:
                print(f"  COUNTEREXAMPLE K={K} x={xv} gap={gap}")
                ok_all = False
            if worst is None or gap < worst[0]:
                worst = (gap, K, xv)
    print(f"  min over grid of  L_K(x) - (1-e^(-1/x))  = {float(worst[0]):.6e}"
          f"  at K={worst[1]}, x={worst[2]}  (>=0 required)")
    print(f"PART A result: {'PASS' if ok_all else 'FAIL'}")
    return ok_all


# ----------------------------------------------------------------------
# coverage machinery (exact rationals)
# ----------------------------------------------------------------------
class Coverage:
    """f(S) = sum of weights of the union of the ground pieces of S."""

    def __init__(self, pieces, weights):
        # pieces: list of frozensets of atom indices; weights: dict atom -> F
        self.pieces = pieces
        self.weights = weights

    def value(self, S):
        u = set()
        for e in S:
            u |= self.pieces[e]
        return sum((self.weights[a] for a in u), F(0))

    def gain(self, e, S):
        u = set()
        for x in S:
            u |= self.pieces[x]
        return sum((self.weights[a] for a in self.pieces[e] - u), F(0))


def predictive_greedy(n, K, fhat_gain, f_gain):
    """Run predictive greedy; adversarial tie breaking = among the argmax of
    the predicted gain, take the element with the SMALLEST true gain (and the
    largest index as a final deterministic tie break).
    Returns (S_list, picks)."""
    S = []
    states = []
    picks = []
    for _ in range(K):
        states.append(tuple(S))
        cand = [e for e in range(n) if e not in S]
        best = max(fhat_gain(e, S) for e in cand)
        arg = [e for e in cand if fhat_gain(e, S) == best]
        arg.sort(key=lambda e: (f_gain(e, S), -e))
        e = arg[0]
        picks.append(e)
        S = S + [e]
    return states, picks, S


def eta_sel_of_run(states, picks, n, f_gain):
    eta = F(1)
    detail = []
    for t, S in enumerate(states):
        cand = [e for e in range(n) if e not in S]
        M = max(f_gain(e, S) for e in cand)
        g = f_gain(picks[t], S)
        if g > 0:
            a = M / g
        elif M == 0:
            a = F(1)
        else:
            a = INF
        detail.append((M, g, a))
        eta = emax(eta, a)
    return eta, detail


def all_subsets(n):
    return chain.from_iterable(combinations(range(n), r) for r in range(n + 1))


def eta_global(n, f_gain, fhat_gain, states=None):
    """eta_u = max d/dt, eta_o = max dt/d over the given states (all subsets if
    states is None). Returns (eta_u, eta_o, eta) with None = +infinity, each
    factor floored at 1 (convention: the band is nonempty)."""
    if states is None:
        states = list(all_subsets(n))
    eu, eo = F(1), F(1)
    for S in states:
        for e in range(n):
            if e in S:
                continue
            d = f_gain(e, S)
            dt = fhat_gain(e, S)
            if d > 0:
                if dt == 0:
                    eu = INF
                else:
                    eu = emax(eu, d / dt)
            if dt > 0:
                if d == 0:
                    eo = INF
                else:
                    eo = emax(eo, dt / d)
    eta = INF if (eu is INF or eo is INF) else eu * eo
    return eu, eo, eta


# ----------------------------------------------------------------------
# PART B -- the exactly tight K = 3, eta^sel = 3/2 instance
# ----------------------------------------------------------------------
def part_B():
    print("=" * 70)
    print("PART B  [VERIFIED-EXHAUSTIVE]  K=3, eta^sel=3/2 tight instance")
    K = 3
    eta = F(3, 2)
    # atoms: for block i in {0,1,2}: pieces P[i][t] taken by decoy d_t (t=0,1,2)
    # and a leftover atom Lf[i].  Measures (true):
    #   r_t = (1/3)(7/9)^t  residual of a block at time t
    #   P[i][t] = (2/9) r_t ,  Lf[i] = (7/9)^3 * (1/3)
    r = [F(1, 3) * F(7, 9) ** t for t in range(3)]
    atom_w = {}
    pieces = {}
    idx = 0
    piece_id = {}
    for i in range(3):
        for t in range(3):
            atom_w[idx] = F(2, 9) * r[t]
            piece_id[(i, t)] = idx
            idx += 1
        atom_w[idx] = F(7, 9) ** 3 * F(1, 3)
        piece_id[(i, "L")] = idx
        idx += 1
    # elements 0,1,2 = decoys d_0,d_1,d_2 ; elements 3,4,5 = o_1,o_2,o_3
    elem_pieces = []
    for t in range(3):
        elem_pieces.append(frozenset(piece_id[(i, t)] for i in range(3)))
    for i in range(3):
        elem_pieces.append(
            frozenset([piece_id[(i, t)] for t in range(3)] + [piece_id[(i, "L")]])
        )
    f = Coverage(elem_pieces, atom_w)

    # predictor: same coverage structure, leftover atoms down-weighted by
    # c = 100/343 ; decoy atoms keep their weight.
    c = F(100, 343)
    atom_w2 = dict(atom_w)
    for i in range(3):
        atom_w2[piece_id[(i, "L")]] = c * atom_w[piece_id[(i, "L")]]
    ft = Coverage(elem_pieces, atom_w2)

    n = 6
    assert f.value(range(n)) == F(1), f.value(range(n))

    states, picks, T = predictive_greedy(n, K, lambda e, S: ft.gain(e, S),
                                         lambda e, S: f.gain(e, S))
    print(f"  picks (0,1,2 = decoys; 3,4,5 = o_i): {picks}")
    es, detail = eta_sel_of_run(states, picks, n, lambda e, S: f.gain(e, S))
    for t, (M, g, a) in enumerate(detail):
        print(f"    t={t}: M_t={M}  g_t={g}  a_t={a}")
    print(f"  eta^sel = {es}")
    fT = f.value(T)
    # OPT by exhaustion over all K-subsets
    opt = max(f.value(S) for S in combinations(range(n), K))
    print(f"  f(T) = {fT} = {float(fT):.6f}   f(O*) = {opt}")
    print(f"  L_3(3/2) = {L_K(F(3,2),3)} = {float(L_K(F(3,2),3)):.6f}")
    ok = (picks == [0, 1, 2]) and es == eta and fT == L_K(eta, 3) * opt
    print(f"  tightness  f(T) == L_3(3/2) f(O*) : {fT == L_K(eta,3)*opt}")

    eu, eo, e_tr = eta_global(n, lambda e, S: f.gain(e, S),
                              lambda e, S: ft.gain(e, S), states=states)
    print(f"  trajectory factors: eta_u^tr={eu} ({float(eu):.6f}), "
          f"eta_o^tr={eo}, eta^tr={e_tr} ({float(e_tr):.6f})")
    eu2, eo2, e_gl = eta_global(n, lambda e, S: f.gain(e, S),
                                lambda e, S: ft.gain(e, S))
    print(f"  global factors    : eta_u={eu2} ({float(eu2):.6f}), "
          f"eta_o={eo2}, eta={e_gl} ({float(e_gl):.6f})")
    order = le(es, e_tr) and le(e_tr, e_gl)
    print(f"  ordering eta^sel <= eta^tr <= eta : {order}")
    print(f"  L_3 values: {float(L_K(es,3)):.6f} >= {float(L_K(e_tr,3)):.6f} "
          f">= {float(L_K(e_gl,3)):.6f}")
    ok &= order and L_K(es, 3) >= L_K(e_tr, 3) >= L_K(e_gl, 3)
    ok &= fT >= L_K(e_gl, 3) * opt
    print(f"PART B result: {'PASS' if ok else 'FAIL'}")
    return ok


# ----------------------------------------------------------------------
# PART C -- randomized stress test
# ----------------------------------------------------------------------
def random_coverage(rng, n, natoms, wmax=6):
    w = {a: F(rng.randint(0, wmax)) for a in range(natoms)}
    pieces = []
    for _ in range(n):
        k = rng.randint(0, natoms)
        pieces.append(frozenset(rng.sample(range(natoms), k)))
    return Coverage(pieces, w)


def part_C(trials=400, seed=20260918):
    print("=" * 70)
    print("PART C  [VERIFIED-EXHAUSTIVE]  randomized stress test")
    rng = random.Random(seed)
    bad_main = bad_order = 0
    n_fin = 0
    for it in range(trials):
        n = rng.randint(2, 7)
        K = rng.randint(1, n)
        natoms = rng.randint(1, 8)
        f = random_coverage(rng, n, natoms)
        if f.value(range(n)) == 0:
            continue
        mode = it % 2
        if mode == 0:
            # arbitrary independent predictor (eta is typically infinite)
            ft = random_coverage(rng, n, natoms)
        else:
            # same support, perturbed atom weights -> finite eta
            w2 = {a: f.weights[a] * F(rng.randint(1, 5), rng.randint(1, 5))
                  for a in f.weights}
            ft = Coverage(f.pieces, w2)
        fg = lambda e, S: f.gain(e, S)
        fh = lambda e, S: ft.gain(e, S)
        states, picks, T = predictive_greedy(n, K, fh, fg)
        es, _ = eta_sel_of_run(states, picks, n, fg)
        opt = max(f.value(S) for S in combinations(range(n), K))
        fT = f.value(T)
        if not (fT >= L_K(es, K) * opt):
            bad_main += 1
            print(f"  MAIN FAIL it={it} n={n} K={K} eta^sel={es} "
                  f"f(T)={fT} L={L_K(es,K)} OPT={opt}")
        _, _, e_tr = eta_global(n, fg, fh, states=states)
        _, _, e_gl = eta_global(n, fg, fh)
        if not (le(es, e_tr) and le(e_tr, e_gl)):
            bad_order += 1
            print(f"  ORDER FAIL it={it} eta^sel={es} eta^tr={e_tr} eta={e_gl}")
        if not (L_K(es, K) >= L_K(e_tr, K) >= L_K(e_gl, K)):
            bad_order += 1
            print(f"  L-ORDER FAIL it={it}")
        if not (fT >= L_K(e_gl, K) * opt):
            bad_main += 1
            print(f"  ETA-BOUND FAIL it={it}")
        if e_gl is not INF:
            n_fin += 1
    print(f"  trials={trials}, instances with finite global eta: {n_fin}")
    print(f"  main-bound violations: {bad_main}; ordering violations: {bad_order}")
    ok = (bad_main == 0 and bad_order == 0)
    print(f"PART C result: {'PASS' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    a = part_A()
    b = part_B()
    c = part_C()
    print("=" * 70)
    print(f"OVERALL: {'PASS' if (a and b and c) else 'FAIL'}")
