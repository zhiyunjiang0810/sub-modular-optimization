#!/usr/bin/env python3
"""P2 (TASKS9): exact worst-case approximation ratio, under adversarial ties, of
three DETERMINISTIC algorithms that are allowed LARGE-SET queries (up to size n),
by full-lattice LP.  K = 3, n in {6, 7}, eta in {1.5, 2, 2.5}.

Model (identical to code/worst_case_lp.py, results/H_F_partial_enumeration.py and
results/L2_linear_candidates.py):
    f monotone submodular, f(empty) = 0, NOT queryable;
    ftilde arbitrary with ftilde(empty) = 0;
    Definition 1 band, single-element form:
        d_e(S)/eta_u <= dtilde_e(S) <= eta_o * d_e(S)   for ALL S and all e notin S,
    eta = eta_u * eta_o, split (eta_u, eta_o) = (eta, 1) (see md section 1.3).
Variables: f(S) for all 2^n subsets (column S) and ftilde(S) (column N + S).
Normalisation: fix a K-subset O, set f(O) = 1, minimise f(output), take the min
over O.  `cap` optionally adds f(S) <= 1 for every |S| <= K (which makes O an
exact maximiser); Gate 6 checks that the min over O is the same either way.

Algorithms
----------
a  REVERSE GREEDY ("stingy", the predictive version of NWF 1978 Section 4
   Theorem 4.4 [CITATION-NEEDS-VERIFICATION]).  S <- N; repeat n-K times: delete
   the element whose removal costs the least PREDICTED value, i.e. pick
   d in argmax_{e in S} ftilde(S - e)  (equivalently argmin of the predicted loss
   ftilde(S) - ftilde(S - e)); ties adversarial.  Output the surviving K-set.
   Queries have size n, n-1, ..., K+1: exactly the N - {e} queries that the J5
   attack uses.

b  COMBINATION.  T_f = K steps of forward predictive greedy from the empty set
   (same encoding as L2); T_r = the reverse-greedy output; return whichever of
   the two has the larger ftilde (ties adversarial).

c  BIDIRECTIONAL SCORE forward greedy: at state S^t pick
   argmax_e sqrt( dtilde_e(S^t) * deltatilde_e ),  deltatilde_e = ftilde(N) -
   ftilde(N - e).  The comparison is a QUADRATIC constraint in the LP variables
   and is NOT exactly LP-representable; see the md section 5.  Handled by
   (c3) exact simulation (Fraction arithmetic) on a library of instances, which
   yields UPPER bounds on the worst case, plus a sufficient-dominance restricted
   LP that produces further instances.

Every "compare two ftilde values" decision is a WEAK linear inequality and the
worst case is the min over decision branches; at equality both branches are
feasible, so the min realises adversarial tie breaking.

Modes
-----
    gates    the six gates (environment, WLOG, symmetry, split, cap, counts)
    run      one configuration (--alg --n --eta), writes a JSON shard
    all      every configuration + gates (one-click reproduction)
    eta1     algorithm a at eta = 1 (NWF Theorem 4.4 cross-check)
    cstudy   algorithm c: the (c3) instance library + restricted-LP search
    merge    merge JSON shards into results/P2_large_query_algorithms.json
Output: results/P2_large_query_algorithms.json
"""
import argparse
import itertools
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import vstack

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code"))
sys.path.insert(0, HERE)

import worst_case_lp                                        # noqa: E402  frozen
from H_F_partial_enumeration import (                       # noqa: E402
    LPBuilder, rho, Vj, UK, LK, rationalize, _to_csr, n2_instance, uk_instance)

K_MAIN = 3
NS = [6, 7]
ETAS = [1.5, 2.0, 2.5]
TOL = 1e-9


def split(eta):
    """(eta_u, eta_o) = (eta, 1): every LP coefficient stays rational, which is
    what makes the exact Fraction re-check of a witness possible.  Only the
    product matters (Gate 4)."""
    return (float(eta), 1.0)


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------
def mask(elems):
    m = 0
    for e in elems:
        m |= 1 << e
    return m


def bits(m):
    return [i for i in range(m.bit_length()) if m >> i & 1]


def pc(m):
    return bin(m).count("1")


METHOD = "highs"          # switched to highs-ipm by Gate 7 (numerical robustness)


def solve_lp(LP, rows, O_mask, obj_mask, cap_K=None, want_x=False):
    """LPBuilder.solve plus an optional cap  f(S) <= 1 for every |S| <= cap_K."""
    A = LP.base_csr
    extra = list(rows)
    rhs = [0.0] * len(extra)
    if cap_K is not None:
        for S in range(LP.N):
            if pc(S) <= cap_K and S != O_mask:
                extra.append({S: 1.0})
                rhs.append(1.0)
    if extra:
        A = vstack([A, _to_csr(extra, LP.nv)]).tocsr()
        b = np.concatenate([np.zeros(LP.base_csr.shape[0]), np.asarray(rhs)])
    else:
        b = np.zeros(A.shape[0])
    obj = np.zeros(LP.nv)
    obj[obj_mask] = 1.0
    A_eq = _to_csr([{0: 1.0}, {LP.N: 1.0}, {O_mask: 1.0}], LP.nv)
    res = linprog(obj, A_ub=A, b_ub=b, A_eq=A_eq, b_eq=[0.0, 0.0, 1.0],
                  bounds=[(None, None)] * LP.nv, method=METHOD)
    if res.status != 0:
        return (np.inf, None) if want_x else np.inf
    return (res.fun, res.x) if want_x else res.fun


# ---------------------------------------------------------------------------
# decision rows
# ---------------------------------------------------------------------------
def fwd_rows(n, N, K, traj=None):
    """Forward predictive greedy picks traj (default 0, 1, ..., K-1): at state
    S_t the chosen element beats every candidate in predicted gain.  The common
    ftilde(S_t) cancels."""
    if traj is None:
        traj = list(range(K))
    G = lambda S: N + S
    rows, S = [], 0
    for t in traj:
        for e in range(n):
            if e == t or S >> e & 1:
                continue
            rows.append({G(S | 1 << e): 1.0, G(S | 1 << t): -1.0})
        S |= 1 << t
    return rows


def rev_rows(n, N, delseq):
    """Reverse greedy deletes delseq[0], delseq[1], ... in this order: at state S
    the deleted d maximises ftilde(S - e) over e in S."""
    G = lambda S: N + S
    rows = []
    S = (1 << n) - 1
    for d in delseq:
        for e in bits(S):
            if e == d:
                continue
            rows.append({G(S ^ (1 << e)): 1.0, G(S ^ (1 << d)): -1.0})
        S ^= 1 << d
    return rows


def cmp_row(N, loser, winner):
    """ftilde(loser) <= ftilde(winner) (weak: adversarial tie)."""
    if loser == winner:
        return None
    G = lambda S: N + S
    return {G(loser): 1.0, G(winner): -1.0}


# ---------------------------------------------------------------------------
# symmetry
# ---------------------------------------------------------------------------
def block_perms(n, block):
    """All permutations of [n] permuting `block` and fixing everything else."""
    out = []
    for p in itertools.permutations(block):
        s = list(range(n))
        for a, b in zip(block, p):
            s[a] = b
        out.append(tuple(s))
    return out


def canon(perms, delseq, O):
    best = None
    for s in perms:
        key = (tuple(s[d] for d in delseq), tuple(sorted(s[o] for o in O)))
        if best is None or key < best:
            best = key
    return best


# ---------------------------------------------------------------------------
# algorithm a: reverse greedy (stingy)
# ---------------------------------------------------------------------------
def algA_branches(n, K, full_traj=False, full_O=False):
    """Branches (delseq, O).  WLOG (md 1.5): the algorithm is equivariant (every
    step is an argmax, no index order is used), so relabel the deletion sequence
    to (K, K+1, ..., n-1); the output is then {0..K-1} and the residual group is
    Sym({0..K-1}), under which O is reduced to orbit representatives."""
    if full_traj:
        delseqs = list(itertools.permutations(range(n), n - K))
    else:
        delseqs = [tuple(range(K, n))]
    Os = list(itertools.combinations(range(n), K))
    if full_traj or full_O:
        return [(d, O) for d in delseqs for O in Os]
    reps, seen = [], set()
    perms = block_perms(n, list(range(K)))
    for O in Os:
        key = canon(perms, delseqs[0], O)
        if key in seen:
            continue
        seen.add(key)
        reps.append((delseqs[0], O))
    return reps


def algA_worst(n, K, eta, eu=None, eo=None, full_traj=False, full_O=False,
               cap=False, verbose=False, time_limit=900.0):
    if eu is None:
        eu, eo = split(eta)
    LP = LPBuilder(n, eu, eo)
    N = LP.N
    br = algA_branches(n, K, full_traj, full_O)
    best = dict(val=np.inf, O=None, delseq=None)
    t0 = time.time()
    status = "OK"
    for (delseq, O) in br:
        if time.time() - t0 > time_limit:
            status = "TIMEOUT"
            break
        out = mask(e for e in range(n) if e not in delseq)
        v = solve_lp(LP, rev_rows(n, N, delseq), mask(O), out,
                     cap_K=K if cap else None)
        if v < best["val"] - 1e-12:
            best = dict(val=v, O=list(O), delseq=list(delseq))
        if verbose:
            print(f"      del={delseq} O={O}: {v:.9f}", flush=True)
    return dict(val=best["val"], O=best["O"], delseq=best["delseq"],
                T=[e for e in range(n) if e not in (best["delseq"] or [])],
                n_lps=len(br), n_branches=len(br),
                n_branches_raw=math.perm(n, n - K) * math.comb(n, K),
                status=status, secs=time.time() - t0)


# ---------------------------------------------------------------------------
# algorithm b: max(forward greedy, reverse greedy) by ftilde
# ---------------------------------------------------------------------------
def algB_branches(n, K, sym=True):
    """Branches (delseq, O, which).  WLOG (md 1.5): relabel so that the FORWARD
    greedy trajectory is 0 -> 1 -> ... -> K-1; the residual group is
    Sym({K..n-1}) (a permutation of {0..K-1} would reorder the forward
    trajectory), under which the pair (delseq, O) is reduced to orbits."""
    delseqs = list(itertools.permutations(range(n), n - K))
    Os = list(itertools.combinations(range(n), K))
    pairs = [(d, O) for d in delseqs for O in Os]
    if sym:
        perms = block_perms(n, list(range(K, n)))
        seen, reps = set(), []
        for (d, O) in pairs:
            key = canon(perms, d, O)
            if key in seen:
                continue
            seen.add(key)
            reps.append((d, O))
        pairs = reps
    return pairs


def algB_worst(n, K, eta, eu=None, eo=None, sym=True, cap=False,
               time_limit=900.0, verbose=False):
    if eu is None:
        eu, eo = split(eta)
    LP = LPBuilder(n, eu, eo)
    N = LP.N
    base = fwd_rows(n, N, K)
    Tf = (1 << K) - 1
    pairs = algB_branches(n, K, sym)
    best = dict(val=np.inf, O=None, delseq=None, which=None)
    t0, nlp, status = time.time(), 0, "OK"
    for (delseq, O) in pairs:
        if time.time() - t0 > time_limit:
            status = "TIMEOUT"
            break
        Tr = mask(e for e in range(n) if e not in delseq)
        rows = base + rev_rows(n, N, delseq)
        Om = mask(O)
        if Tr == Tf:
            outs = [("f", Tf, None)]
        else:
            outs = [("f", Tf, cmp_row(N, Tr, Tf)), ("r", Tr, cmp_row(N, Tf, Tr))]
        for (which, obj, extra) in outs:
            rr = rows if extra is None else rows + [extra]
            v = solve_lp(LP, rr, Om, obj, cap_K=K if cap else None)
            nlp += 1
            if v < best["val"] - 1e-12:
                best = dict(val=v, O=list(O), delseq=list(delseq), which=which)
                if verbose:
                    print(f"      incumbent {v:.9f} O={O} del={delseq} "
                          f"out={which}", flush=True)
    return dict(val=best["val"], O=best["O"], delseq=best["delseq"],
                which=best["which"], n_lps=nlp, n_branches=len(pairs),
                n_branches_raw=math.perm(n, n - K) * math.comb(n, K) * 2,
                status=status, secs=time.time() - t0)


# ---------------------------------------------------------------------------
# instance rebuild + tie-adversarial simulation
# ---------------------------------------------------------------------------
def rebuild(n, K, eta, rows, O_mask, obj_mask, cap=False):
    eu, eo = split(eta)
    LP = LPBuilder(n, eu, eo)
    val, x = solve_lp(LP, rows, O_mask, obj_mask, cap_K=K if cap else None,
                      want_x=True)
    N = LP.N
    f, g = x[:N].copy(), x[N:].copy()
    f -= f[0]
    g -= g[0]
    return val, f, g


def check_model(n, f, g, eu, eo, tol=1e-7):
    N = 1 << n
    mono = submod = band = True
    for S in range(N):
        for e in range(n):
            if S >> e & 1:
                continue
            d = f[S | 1 << e] - f[S]
            dt = g[S | 1 << e] - g[S]
            if d < -tol:
                mono = False
            if dt < d / eu - tol or dt > eo * d + tol:
                band = False
            for e2 in range(n):
                if e2 == e or S >> e2 & 1:
                    continue
                if f[S | 1 << e | 1 << e2] - f[S | 1 << e2] > d + tol:
                    submod = False
    return mono, submod, band


def opt_value(n, K, f):
    return max(f[S] for S in range(1 << n) if pc(S) <= K)


def _is_top(v, top, tol):
    """Tie test.  tol = 0 means EXACT equality (Fraction arithmetic): never go
    through float, or rounding of `top` silently kills the true argmax."""
    if tol == 0:
        return v == top
    return v >= top - tol * max(1.0, abs(float(top)))


def rev_finals(n, K, g, tol=1e-7):
    """All tie-consistent reverse-greedy outcomes (set of masks)."""
    states = {(1 << n) - 1}
    for _ in range(n - K):
        nxt = set()
        for S in states:
            vals = {e: g[S ^ (1 << e)] for e in bits(S)}
            top = max(vals.values())
            for e, v in vals.items():
                if _is_top(v, top, tol):
                    nxt.add(S ^ (1 << e))
        states = nxt
    return states


def fwd_finals(n, K, g, tol=1e-7):
    states = {0}
    for _ in range(K):
        nxt = set()
        for S in states:
            gains = {e: g[S | 1 << e] - g[S] for e in range(n) if not S >> e & 1}
            top = max(gains.values())
            for e, v in gains.items():
                if _is_top(v, top, tol):
                    nxt.add(S | 1 << e)
        states = nxt
    return states


def simulate_A(n, K, f, g, tol=1e-7):
    Ts = rev_finals(n, K, g, tol)
    T = min(Ts, key=lambda S: f[S])
    return f[T], T


def simulate_B(n, K, f, g, tol=1e-7):
    F = fwd_finals(n, K, g, tol)
    R = rev_finals(n, K, g, tol)
    worst, arg = np.inf, None
    for Tf in F:
        for Tr in R:
            outs = []
            if g[Tf] >= g[Tr] or (tol and g[Tf] >= g[Tr] - tol):
                outs.append(Tf)
            if g[Tr] >= g[Tf] or (tol and g[Tr] >= g[Tf] - tol):
                outs.append(Tr)
            for T in outs:
                if f[T] < worst:
                    worst, arg = f[T], (Tf, Tr, T)
    return worst, arg


def simulate_C(n, K, f, g, tol=1e-7, exact=False, fallback=False):
    """Bidirectional-score forward greedy, tie-adversarial.  Comparing the
    geometric means sqrt(dtilde * deltatilde) is the same as comparing the
    PRODUCTS because both factors are nonnegative (d >= 0 by monotonicity and
    dtilde >= d/eta_u >= 0).

    fallback=True is the variant c' that breaks a score tie by the larger
    dtilde_e(S^t) (and only then adversarially).  It matters because the score
    COLLAPSES whenever f is saturated at the top (deltatilde_e = 0 for every e),
    in which case the literal rule c leaves the choice entirely to the
    adversary."""
    full = (1 << n) - 1
    delta = [g[full] - g[full ^ (1 << e)] for e in range(n)]
    states = {0}
    ties = 0
    for _ in range(K):
        nxt = set()
        for S in states:
            d = {e: g[S | 1 << e] - g[S] for e in range(n) if not S >> e & 1}
            sc = {e: d[e] * delta[e] for e in d}
            top = max(sc.values())
            cand = [e for e, v in sc.items() if _is_top(v, top, 0 if exact else tol)]
            if fallback and len(cand) > 1:
                dtop = max(d[e] for e in cand)
                cand = [e for e in cand if _is_top(d[e], dtop, 0 if exact else tol)]
            ties = max(ties, len(cand))
            for e in cand:
                nxt.add(S | 1 << e)
        states = nxt
    T = min(states, key=lambda S: f[S])
    return f[T], T, len(states)


def consistency_check(n, K, eta, alg, res, cap=False, verbose=True):
    """Rebuild the argmin branch's LP optimum as an explicit (f, ftilde), verify
    monotone / submodular / band on the whole lattice, re-run the algorithm with
    adversarial ties and compare the ratio with the LP value."""
    eu, eo = split(eta)
    N = 1 << n
    delseq = res["delseq"]
    O_mask = mask(res["O"])
    Tr = mask(e for e in range(n) if e not in delseq)
    if alg == "a":
        rows = rev_rows(n, N, delseq)
        obj = Tr
    else:
        Tf = (1 << K) - 1
        rows = fwd_rows(n, N, K) + rev_rows(n, N, delseq)
        obj = Tf if res["which"] == "f" else Tr
        if Tr != Tf:
            rows.append(cmp_row(N, Tr, Tf) if res["which"] == "f"
                        else cmp_row(N, Tf, Tr))
    val, f, g = rebuild(n, K, eta, rows, O_mask, obj, cap=cap)
    mono, submod, band = check_model(n, f, g, eu, eo)
    OPT = opt_value(n, K, f)
    if alg == "a":
        w, arg = simulate_A(n, K, f, g)
    else:
        w, arg = simulate_B(n, K, f, g)
    rep = dict(lp_value=float(val), monotone=bool(mono), submodular=bool(submod),
               band=bool(band), OPT=float(OPT), sim_ratio=float(w / OPT),
               sim_arg=str(arg), obj_set=bits(obj), O=bits(O_mask),
               branch_ratio=float(f[obj] / OPT))
    rep["consistent"] = bool(mono and submod and band
                             and abs(w / OPT - val) < 1e-6
                             and abs(f[obj] / OPT - val) < 1e-6)
    if verbose:
        print(f"    consistency n={n} K={K} eta={eta} alg={alg}: LP={val:.9f} "
              f"sim={w/OPT:.9f} mono={mono} submod={submod} band={band} -> "
              f"{'CONSISTENT' if rep['consistent'] else 'MISMATCH'}", flush=True)
    return rep, f, g


# ---------------------------------------------------------------------------
# exact rational re-check of a witness
# ---------------------------------------------------------------------------
def to_fractions(v, maxden):
    return [Fr(float(t)).limit_denominator(maxden) for t in v]


def exact_check(n, K, eta, f, g, maxden=100000, sp=None):
    """Rationalise an instance and verify EXACTLY (Fraction arithmetic) that it
    is monotone submodular with ftilde inside the band."""
    eu, eo = sp if sp else split(eta)
    EU, EO = Fr(eu).limit_denominator(10 ** 6), Fr(eo).limit_denominator(10 ** 6)
    N = 1 << n
    F, Gt = to_fractions(f, maxden), to_fractions(g, maxden)
    ok = dict(monotone=True, submodular=True, band=True, empty=True)
    if F[0] != 0 or Gt[0] != 0:
        ok["empty"] = False
    for S in range(N):
        for e in range(n):
            if S >> e & 1:
                continue
            d = F[S | 1 << e] - F[S]
            dt = Gt[S | 1 << e] - Gt[S]
            if d < 0:
                ok["monotone"] = False
            if dt < d / EU or dt > EO * d:
                ok["band"] = False
            for e2 in range(n):
                if e2 == e or S >> e2 & 1:
                    continue
                if F[S | 1 << e | 1 << e2] - F[S | 1 << e2] > d:
                    ok["submodular"] = False
    return all(ok.values()), ok, F, Gt


def exact_witness(n, K, eta, alg, f, g, maxden=100000, sp=None):
    good, ok, F, Gt = exact_check(n, K, eta, f, g, maxden, sp)
    OPT = max(F[S] for S in range(1 << n) if pc(S) <= K)
    if alg == "a":
        w, T = simulate_A(n, K, F, Gt, tol=0)
    elif alg == "b":
        w, arg = simulate_B(n, K, F, Gt, tol=0)
        T = arg[2] if arg else None
    else:
        w, T, _ = simulate_C(n, K, F, Gt, exact=True)
    ratio = w / OPT
    return dict(exact_ok=bool(good), detail=ok, maxden=maxden,
                exact_ratio=str(ratio), exact_ratio_float=float(ratio),
                exact_T=bits(T) if T is not None else None)


# ---------------------------------------------------------------------------
# algorithm c: (c3) instance library + sufficient-dominance restricted LP
# ---------------------------------------------------------------------------
def c_restricted_lp(n, K, eta, cap=True, verbose=False):
    """A SUFFICIENT linear certificate for algorithm c's trajectory: force the
    picked element to dominate every rival in BOTH factors,
        dtilde_t(S_t) >= dtilde_e(S_t)  and  deltatilde_t >= deltatilde_e,
    which implies the product (hence the geometric mean) comparison because both
    factors are nonnegative.  The feasible set is a SUBSET of the instances on
    which c really follows the trajectory, so the LP value is a valid UPPER
    bound on c's worst case (an instance is exhibited, not a bound proved).
    Trajectory fixed to 0 -> ... -> K-1 by equivariance; O over all K-subsets."""
    eu, eo = split(eta)
    LP = LPBuilder(n, eu, eo)
    N = LP.N
    G = lambda S: N + S
    full = (1 << n) - 1
    rows = list(fwd_rows(n, N, K))
    for t in range(K):
        S = (1 << t) - 1
        for e in range(n):
            if e == t or S >> e & 1:
                continue
            # deltatilde_t >= deltatilde_e:
            #   (g[full]-g[full-t]) - (g[full]-g[full-e]) >= 0  <=>
            #   g[full ^ t] - g[full ^ e] <= 0
            rows.append({G(full ^ (1 << t)): 1.0, G(full ^ (1 << e)): -1.0})
    Tf = (1 << K) - 1
    best = (np.inf, None)
    for O in itertools.combinations(range(n), K):
        v, x = solve_lp(LP, rows, mask(O), Tf, cap_K=K if cap else None,
                        want_x=True)
        if v < best[0]:
            best = (v, (O, x))
        if verbose:
            print(f"      O={O}: {v:.9f}", flush=True)
    if best[1] is None:
        return dict(val=np.inf, O=None), None, None
    O, x = best[1]
    f, g = x[:N].copy(), x[N:].copy()
    f -= f[0]
    g -= g[0]
    return dict(val=float(best[0]), O=list(O)), f, g


def instance_library(n, K, etas, extra=None):
    """The (c3) library: for every eta, a list of (name, f, g, n) instances that
    are argmin witnesses of other algorithms in this project."""
    lib = {}
    for eta in etas:
        eu, eo = split(eta)
        items = []
        # forward predictive greedy worst case (the frozen framework's LP)
        val, O, x = worst_case_lp.worst_case(n, K, eu, eo, "single")
        N = 1 << n
        f, g = x[:N] - x[0], x[N:] - x[N]
        items.append((f"greedy_LP_argmin_n{n}", f, g, n))
        if extra:
            items += [(nm, a, b, nn) for (nm, a, b, nn, e2) in extra
                      if abs(e2 - eta) < 1e-12]
        if n == 2 * K:
            for j in range(K):
                f2, g2, n2 = n2_instance(K, j, eta)
                items.append((f"n2_instance_j{j}", f2, g2, n2))
            f3, g3, n3 = uk_instance(K, eta)
            items.append((f"uk_instance", f3, g3, n3))
        lib[eta] = items
    return lib


# ---------------------------------------------------------------------------
# gates
# ---------------------------------------------------------------------------
def run_gates(time_limit=900.0):
    out = {}
    print("=" * 78)
    print("Gate 1 (environment): reproduce rho_K with the FROZEN "
          "code/worst_case_lp.py")
    print("=" * 78)
    g1 = []
    for n in NS:
        for eta in ETAS:
            eu, eo = split(eta)
            t0 = time.time()
            val, O, _ = worst_case_lp.worst_case(n, K_MAIN, eu, eo, "single")
            d = val - rho(K_MAIN, eta)
            print(f"  K=3 n={n} eta={eta}: greedy LP = {val:.9f}  "
                  f"rho_3 = {rho(K_MAIN, eta):.9f}  diff = {d:+.2e}  "
                  f"({time.time()-t0:.0f}s)", flush=True)
            g1.append(dict(K=K_MAIN, n=n, eta=eta, lp=float(val),
                           rho=rho(K_MAIN, eta), diff=float(d),
                           passed=abs(d) < 1e-7))
    out["gate1_rho"] = g1

    print("=" * 78)
    print("Gate 2 (WLOG): algorithm a, fixing the deletion trajectory vs "
          "enumerating all ordered deletion trajectories")
    print("=" * 78)
    g2 = []
    for (K, n) in [(2, 4), (2, 5), (3, 5), (3, 6)]:
        for eta in [1.5, 2.0]:
            a = algA_worst(n, K, eta)
            b = algA_worst(n, K, eta, full_traj=True)
            print(f"  K={K} n={n} eta={eta}: fixed({a['n_lps']} LPs)="
                  f"{a['val']:.9f}  full({b['n_lps']} LPs)={b['val']:.9f}  "
                  f"diff={a['val']-b['val']:+.2e}", flush=True)
            g2.append(dict(K=K, n=n, eta=eta, fixed=float(a["val"]),
                           full=float(b["val"]),
                           diff=float(a["val"] - b["val"]),
                           passed=abs(a["val"] - b["val"]) < 1e-7))
    out["gate2_traj_wlog_A"] = g2

    print("=" * 78)
    print("Gate 3 (WLOG): algorithm b, fixed forward trajectory + (delseq,O) "
          "orbit reduction vs full (delseq,O) enumeration")
    print("=" * 78)
    g3 = []
    for (K, n) in [(2, 4), (2, 5), (3, 5), (3, 6)]:
        for eta in [1.5, 2.0, 2.5]:
            a = algB_worst(n, K, eta, sym=True)
            b = algB_worst(n, K, eta, sym=False)
            print(f"  K={K} n={n} eta={eta}: orbits({a['n_lps']} LPs)="
                  f"{a['val']:.9f}  full({b['n_lps']} LPs)={b['val']:.9f}  "
                  f"diff={a['val']-b['val']:+.2e}", flush=True)
            g3.append(dict(K=K, n=n, eta=eta, orbits=float(a["val"]),
                           full=float(b["val"]),
                           diff=float(a["val"] - b["val"]),
                           passed=abs(a["val"] - b["val"]) < 1e-7))
    out["gate3_orbit_B"] = g3

    print("=" * 78)
    print("Gate 4: (eta_u, eta_o) split invariance (only the product matters)")
    print("=" * 78)
    g4 = []
    for (K, n, alg) in [(2, 5, "a"), (3, 6, "a"), (2, 5, "b"), (3, 5, "b")]:
        eta = 2.0
        vals = []
        for (eu, eo) in [(2.0, 1.0), (1.0, 2.0), (2.0 ** 0.5, 2.0 ** 0.5)]:
            v = (algA_worst(n, K, eta, eu=eu, eo=eo)["val"] if alg == "a"
                 else algB_worst(n, K, eta, eu=eu, eo=eo)["val"])
            print(f"  K={K} n={n} alg={alg} (eu,eo)=({eu:.4f},{eo:.4f}): "
                  f"{v:.9f}", flush=True)
            vals.append(float(v))
        g4.append(dict(K=K, n=n, alg=alg, vals=vals,
                       spread=max(vals) - min(vals),
                       passed=max(vals) - min(vals) < 1e-7))
    out["gate4_split"] = g4

    print("=" * 78)
    print("Gate 5: the f(S) <= 1 cap for |S| <= K does not change the min over O")
    print("=" * 78)
    g5 = []
    for (K, n) in [(2, 5), (3, 6)]:
        for eta in [1.5, 2.5]:
            a = algA_worst(n, K, eta, cap=False)
            b = algA_worst(n, K, eta, cap=True)
            print(f"  K={K} n={n} eta={eta} alg=a: uncapped={a['val']:.9f}  "
                  f"capped={b['val']:.9f}  diff={a['val']-b['val']:+.2e}",
                  flush=True)
            g5.append(dict(K=K, n=n, eta=eta, alg="a", uncapped=float(a["val"]),
                           capped=float(b["val"]),
                           diff=float(a["val"] - b["val"]),
                           passed=abs(a["val"] - b["val"]) < 1e-7))
    out["gate5_cap"] = g5

    print("=" * 78)
    print("Gate 6: branch counts (combinatorial, no LP)")
    print("=" * 78)
    g6 = []
    for n in NS:
        K = K_MAIN
        a_raw = math.comb(n, K)
        a_red = len(algA_branches(n, K))
        b_raw = math.perm(n, n - K) * math.comb(n, K)
        b_red = len(algB_branches(n, K, sym=True))
        print(f"  K={K} n={n}: alg a  O-orbits {a_red} / {a_raw} "
              f"(x {math.perm(n, n-K)} deletion orders eliminated);  "
              f"alg b  (delseq,O) orbits {b_red} / {b_raw}", flush=True)
        g6.append(dict(K=K, n=n, A_reps=a_red, A_full_O=a_raw,
                       A_full_traj_O=math.perm(n, n - K) * a_raw,
                       B_orbits=b_red, B_pairs=b_raw))
    out["gate6_counts"] = g6

    print("=" * 78)
    print("Gate 7 (numerics): re-solve every branch with a different LP "
          "algorithm (HiGHS interior point instead of dual simplex)")
    print("=" * 78)
    global METHOD
    g7 = []
    for n in [6]:            # n = 6 only: n = 7 would double the main run cost
        for eta in ETAS:
            METHOD = "highs"
            a1 = algA_worst(n, K_MAIN, eta)["val"]
            b1 = algB_worst(n, K_MAIN, eta)["val"]
            METHOD = "highs-ipm"
            a2 = algA_worst(n, K_MAIN, eta)["val"]
            b2 = algB_worst(n, K_MAIN, eta)["val"]
            METHOD = "highs"
            print(f"  n={n} eta={eta}: a simplex={a1:.9f} ipm={a2:.9f} "
                  f"(d={a1-a2:+.1e})   b simplex={b1:.9f} ipm={b2:.9f} "
                  f"(d={b1-b2:+.1e})", flush=True)
            g7.append(dict(n=n, eta=eta, a_simplex=float(a1), a_ipm=float(a2),
                           b_simplex=float(b1), b_ipm=float(b2),
                           passed=abs(a1 - a2) < 1e-6 and abs(b1 - b2) < 1e-6))
    out["gate7_lp_method"] = g7
    return out


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------
def _classify(v, r, status):
    """What the returned number IS (copied discipline from L2 `_classify`).
    status OK      -> v is the EXACT worst case.
    status TIMEOUT -> v is the incumbent, an UPPER bound only: it can support
                      "worse than rho_K" but NEVER "strictly better"."""
    if not np.isfinite(v):
        return "none", "unknown"
    if status == "OK":
        return ("exact",
                "strictly_better" if v > r + 1e-9 else
                "equal" if abs(v - r) <= 1e-9 else "worse")
    return ("upper_bound",
            "worse" if v < r - 1e-9 else "inconclusive_upper_bound_only")


def run_config(K, n, eta, alg, time_limit=900.0, do_check=True, cap=False):
    t0 = time.time()
    print(f"[{time.strftime('%H:%M:%S')}] K={K} n={n} eta={eta} alg={alg}",
          flush=True)
    res = (algA_worst(n, K, eta, cap=cap, time_limit=time_limit) if alg == "a"
           else algB_worst(n, K, eta, cap=cap, time_limit=time_limit))
    val = res["val"]
    fr = rationalize(val) if np.isfinite(val) else None
    r = rho(K, eta)
    kind, vs_rho = _classify(val, r, res["status"])
    inv = 1.0 / eta
    row = dict(K=K, n=n, eta=eta, algorithm=alg,
               value_float=None if not np.isfinite(val) else float(val),
               value_fraction=None if fr is None else str(fr),
               value_kind=kind, value_is_upper_bound_only=(kind == "upper_bound"),
               rho=r, inv_eta=inv, U=UK(K, eta), L=LK(K, eta),
               vs_rho=vs_rho,
               gap_vs_rho=None if not np.isfinite(val) else float(val - r),
               vs_inv_eta=("above" if val > inv + 1e-9 else
                           "equal" if abs(val - inv) <= 1e-9 else "below"),
               n_branches=res.get("n_branches"),
               n_branches_raw=res.get("n_branches_raw"),
               n_lps=res.get("n_lps"), status=res["status"],
               O=res.get("O"), delseq=res.get("delseq"), T=res.get("T"),
               which=res.get("which"), secs=time.time() - t0)
    print(f"    value = {val:.9f} ({fr}) [{kind}]   rho_3 = {r:.9f}   "
          f"1/eta = {inv:.9f}  -> {vs_rho} / {row['vs_inv_eta']}   "
          f"status={res['status']}  LPs={res.get('n_lps')}  "
          f"({row['secs']:.0f}s)", flush=True)
    if do_check and np.isfinite(val) and res.get("delseq") is not None:
        rep, f, g = consistency_check(n, K, eta, alg, res, cap=cap)
        row["consistency"] = rep
        if vs_rho == "strictly_better":
            print("    *** strictly better than rho_3: exact rational re-check "
                  "***", flush=True)
            row["exact_recheck"] = exact_witness(n, K, eta, alg, f, g)
            print(f"    exact: {row['exact_recheck']}", flush=True)
        row["query_audit"] = query_audit(n, K, alg)
    return row


def query_audit(n, K, alg):
    """Query count and maximum query SIZE (the point of P2: sizes above K).
    Reverse greedy at state S queries ftilde(S) and ftilde(S - e) for every
    e in S, so the sizes run from n down to K and the count is
    sum_{s=K+1}^{n} (s + 1)."""
    rev_q = sum(s + 1 for s in range(K + 1, n + 1))
    fwd_q = sum(n - t for t in range(K))
    if alg == "a":
        q, sizes = rev_q, list(range(K, n + 1))
    elif alg == "b":
        q, sizes = fwd_q + rev_q + 2, list(range(1, n + 1))
    else:                                 # c: greedy + ftilde(N), ftilde(N - e)
        q, sizes = fwd_q + n + 1, [K, n]
    return dict(n_queries=q, max_query_size=max(sizes), K=K, n=n,
                exceeds_K=max(sizes) > K,
                poly_queries=True, note="queries of size > K are the point of P2")


def run_c_study(ns=NS, K=K_MAIN, etas=ETAS, argmin_instances=None):
    """(c3): exact simulation of algorithm c on a library of instances, plus the
    sufficient-dominance restricted LP (which manufactures further instances).
    Every number here is an UPPER bound on c's worst case."""
    out = dict(library=[], restricted_lp=[], summary=[])
    for n in ns:
        lib = instance_library(n, K, etas, extra=argmin_instances)
        for eta in etas:
            best = (np.inf, None)
            bestf = (np.inf, None)
            for (name, f, g, nn) in lib[eta]:
                if nn != n:
                    continue
                # the band is split dependent, the algorithms are not (only the
                # product eta matters): accept the instance if ANY split with
                # this product validates it (n2_instance / uk_instance are built
                # with the symmetric split sqrt(eta), sqrt(eta)).
                mono = submod = band = False
                used_split = None
                for (eu, eo) in [split(eta), (1.0, float(eta)),
                                 (eta ** 0.5, eta ** 0.5)]:
                    m2, s2, b2 = check_model(nn, f, g, eu, eo)
                    if m2 and s2 and b2:
                        mono, submod, band, used_split = m2, s2, b2, (eu, eo)
                        break
                    if used_split is None:
                        mono, submod, band = m2, s2, b2
                OPT = opt_value(nn, K, f)
                wC, TC, nstates = simulate_C(nn, K, f, g)
                wCF, TCF, nsf = simulate_C(nn, K, f, g, fallback=True)
                wA, TA = simulate_A(nn, K, f, g)
                wB, _ = simulate_B(nn, K, f, g)
                Fw = fwd_finals(nn, K, g)
                wG = min(f[S] for S in Fw)
                rowc = dict(n=nn, eta=eta, instance=name, split=str(used_split),
                            valid=bool(mono and submod and band),
                            monotone=bool(mono), submodular=bool(submod),
                            band=bool(band), OPT=float(OPT),
                            ratio_c=float(wC / OPT), ratio_a=float(wA / OPT),
                            ratio_c_fallback=float(wCF / OPT),
                            c_fallback_tie_states=nsf,
                            ratio_b=float(wB / OPT), ratio_greedy=float(wG / OPT),
                            c_tie_states=nstates, T_c=bits(TC),
                            rho=rho(K, eta), inv_eta=1.0 / eta)
                ex = None
                if mono and submod and band:
                    for md in (2000, 100000):
                        e = exact_witness(nn, K, eta, "c", f, g, maxden=md,
                                          sp=used_split)
                        if e["exact_ok"]:
                            ex = e
                            break
                    rowc["exact"] = ex
                    if ex is not None and ex["exact_ok"]:
                        rowc["ratio_c_exact"] = ex["exact_ratio"]
                if rowc["valid"] and rowc["ratio_c"] < best[0]:
                    best = (rowc["ratio_c"], name)
                if rowc["valid"] and rowc["ratio_c_fallback"] < bestf[0]:
                    bestf = (rowc["ratio_c_fallback"], name)
                out["library"].append(rowc)
                print(f"  c-sim n={nn} eta={eta} inst={name:24s} "
                      f"valid={rowc['valid']} ratio_c={rowc['ratio_c']:.9f} "
                      f"(a={rowc['ratio_a']:.6f} greedy={rowc['ratio_greedy']:.6f})"
                      f" rho_3={rho(K, eta):.6f}", flush=True)
            # restricted LP
            t0 = time.time()
            rl, f, g = c_restricted_lp(n, K, eta)
            if f is not None:
                eu, eo = split(eta)
                mono, submod, band = check_model(n, f, g, eu, eo)
                OPT = opt_value(n, K, f)
                wC, TC, ns_ = simulate_C(n, K, f, g)
                wCF, _, _ = simulate_C(n, K, f, g, fallback=True)
                ratio = float(wC / OPT)
                rl.update(n=n, eta=eta, valid=bool(mono and submod and band),
                          sim_ratio_c=ratio, T_c=bits(TC),
                          sim_ratio_c_fallback=float(wCF / OPT),
                          secs=time.time() - t0, rho=rho(K, eta))
                print(f"  c-restricted-LP n={n} eta={eta}: LP={rl['val']:.9f} "
                      f"sim_c={ratio:.9f} valid={rl['valid']} "
                      f"({rl['secs']:.0f}s)", flush=True)
                if rl["valid"] and ratio < best[0]:
                    best = (ratio, "restricted_LP")
                if rl["valid"] and rl["sim_ratio_c_fallback"] < bestf[0]:
                    bestf = (rl["sim_ratio_c_fallback"], "restricted_LP")
            out["restricted_lp"].append(rl)
            out["summary"].append(dict(n=n, eta=eta, K=K,
                                       upper_bound_c=None if not np.isfinite(best[0])
                                       else float(best[0]),
                                       argmin_instance=best[1],
                                       upper_bound_c_fallback=None
                                       if not np.isfinite(bestf[0])
                                       else float(bestf[0]),
                                       argmin_instance_fallback=bestf[1],
                                       rho=rho(K, eta), inv_eta=1.0 / eta))
    return out


def _load(p):
    if os.path.exists(p):
        try:
            return json.load(open(p))
        except Exception:
            return {}
    return {}


def _dump(p, obj):
    with open(p, "w") as fh:
        json.dump(obj, fh, indent=1, default=str)


def _key(r):
    return (r["algorithm"], r["K"], r["n"], r["eta"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="all",
                    choices=["all", "gates", "run", "merge", "cstudy", "eta1"])
    ap.add_argument("--K", type=int, default=K_MAIN)
    ap.add_argument("--n", type=int)
    ap.add_argument("--eta", type=float)
    ap.add_argument("--alg", choices=["a", "b"])
    ap.add_argument("--time-limit", type=float, default=900.0)
    ap.add_argument("--cap", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    path = os.path.join(HERE, "P2_large_query_algorithms.json")
    if args.mode == "gates":
        _dump(os.path.join(HERE, "_P2_shard_gates.json"),
              dict(gates=run_gates(args.time_limit)))
        return
    if args.mode == "eta1":
        rows = []
        for n in NS:
            for eta in [1.0, 1.25]:
                r = run_config(args.K, n, eta, "a", args.time_limit)
                rows.append(r)
        _dump(os.path.join(HERE, "_P2_shard_eta1.json"), dict(eta1=rows))
        return
    if args.mode == "cstudy":
        # needs the merged JSON: the (c3) library re-uses the (a)/(b) argmin
        # instances recorded there, so run `merge` first.
        log = _load(path)
        out = run_c_study(argmin_instances=_argmin_instances(log))
        _dump(os.path.join(HERE, "_P2_shard_c.json"), dict(c_study=out))
        return
    if args.mode == "run":
        row = run_config(args.K, args.n, args.eta, args.alg, args.time_limit,
                         cap=args.cap)
        out = args.out or os.path.join(
            HERE, f"_P2_shard_{args.alg}_{args.K}_{args.n}_{args.eta}.json")
        _dump(out, dict(results=[row]))
        print(f"wrote {out}")
        return
    if args.mode == "merge":
        log = _load(path)
        rows = {_key(r): r for r in log.get("results", [])}
        for fn in sorted(os.listdir(HERE)):
            if not (fn.startswith("_P2_shard_") and fn.endswith(".json")):
                continue
            sh = _load(os.path.join(HERE, fn))
            for r in sh.get("results", []):
                r["query_audit"] = query_audit(r["n"], r["K"], r["algorithm"])
                rows[_key(r)] = r
            for k in ("gates", "c_study", "eta1", "closed_form_A"):
                if k in sh:
                    log[k] = sh[k]
        log["results"] = [rows[k] for k in sorted(rows)]
        log["meta"] = dict(K=K_MAIN, ns=NS, etas=ETAS,
                           split="(eta_u, eta_o) = (eta, 1)",
                           generated=time.strftime("%Y-%m-%d %H:%M:%S"))
        _dump(path, log)
        print(f"merged {len(log['results'])} rows into {path}")
        return
    # all
    log = _load(path)
    rows = {_key(r): r for r in log.get("results", [])}
    log["gates"] = run_gates(args.time_limit)
    for alg in ("a", "b"):
        for n in NS:
            for eta in ETAS:
                r = run_config(args.K, n, eta, alg, args.time_limit)
                rows[_key(r)] = r
    log["results"] = [rows[k] for k in sorted(rows)]
    log["c_study"] = run_c_study(argmin_instances=_argmin_instances(log))
    _dump(path, log)
    print(f"wrote {path}")


def _argmin_instances(log):
    """Rebuild the (a)/(b) argmin instances recorded in the JSON so that the
    (c3) library can re-use them."""
    extra = []
    for r in log.get("results", []):
        if r.get("delseq") is None or r.get("value_float") is None:
            continue
        n, K, eta, alg = r["n"], r["K"], r["eta"], r["algorithm"]
        try:
            res = dict(delseq=r["delseq"], O=r["O"], which=r.get("which"))
            _, f, g = consistency_check(n, K, eta, alg, res, verbose=False)
            extra.append((f"argmin_{alg}_n{n}", f, g, n, eta))
        except Exception as exc:                      # pragma: no cover
            print(f"  (argmin rebuild failed for {alg} n={n} eta={eta}: {exc})")
    return extra


if __name__ == "__main__":
    main()
