#!/usr/bin/env python3
"""L2 (TASKS7): exact worst-case approximation ratio, under adversarial ties, of
two DETERMINISTIC LINEAR-QUERY-BUDGET candidate algorithms, by full-lattice LP.

Model (identical to code/worst_case_lp.py and results/H_F_partial_enumeration.py):
    f monotone submodular, f(empty) = 0, NOT queryable;
    ftilde arbitrary with ftilde(empty) = 0;
    Definition 1 band, single-element form:
        d_e(S)/eta_u <= dtilde_e(S) <= eta_o * d_e(S)   for ALL S and all e notin S,
    eta = eta_u * eta_o.
Variables: f(S) for all 2^n subsets (column S) and ftilde(S) (column N + S), N = 2^n.
Normalisation: fix a K-subset O, set f(O) = 1, minimise, then take the min over O
(same argument as code/worst_case_lp.py: any instance normalised by f(O*) is
feasible for the LP with O = O*, and an LP optimum with f(O) = 1 has true ratio
<= its objective, so the two minima coincide).

Candidates
----------
A  top-m shortlist, m = K+1.
   (1) query ftilde({e}) for every e (n queries, size 1);
   (2) shortlist M = the m elements with the largest ftilde({e}) (ties adversarial);
   (3) query ftilde(A) for every A in binom(M, K)  (C(m,K) = K+1 queries, size K);
   (4) output argmax_{A in binom(M,K)} ftilde(A) (ties adversarial).
   Queries: n + K + 1, each of size <= K.

B  predictive greedy + one swap pass.
   (1) K steps of predictive greedy from the empty set: at state S add
       argmax_e dtilde_e(S) (ties adversarial); T_0 = (g_1, ..., g_K) in
       insertion order.  <= nK queries of size <= K.
   (2) one pass over the FIXED pair list  (slot p = 1..K in insertion order)
       x (e in [n] \ T_0 in ascending index order): query ftilde(T - T[p] + e)
       and accept the swap if it is larger than ftilde(T), where T is the CURRENT
       set.  Exactly K(n-K) checks, each on a set of size exactly K.
   Queries: <= nK + K(n-K).
   `swap_mode`:
       "continue" (default, the literal reading of TASKS7): after an accepted
           swap the scan continues with the next pair;
       "first": at most one accepted swap per slot (break to the next slot).

Every "compare two ftilde values" decision is encoded as a WEAK linear inequality
and the worst case is the min over decision branches.  At an equality both
branches are feasible, so the min automatically realises adversarial tie
breaking.  (For B's swap test this means the LP evaluates the tie-adversarial
version of "accept iff strictly larger"; see the md, section 1.4, and the
`strict` column of the consistency check, which re-runs the strict rule on the
rebuilt instance.)

Modes
-----
    gates      external gates: reproduce rho_K with code/worst_case_lp.py, the
               O-symmetry reduction, the (eta_u, eta_o) split invariance
    run        one configuration (--K --n --eta --cand), writes a JSON shard
    all        every configuration in sequence (one-click reproduction)
    merge      merge JSON shards into results/L2_linear_candidates.json
Outputs: results/L2_linear_candidates.json
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
from scipy.sparse import csr_matrix, vstack

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code"))
sys.path.insert(0, HERE)

# frozen framework (import only, never modified) and the H-F row builder
import worst_case_lp                                     # noqa: E402
from H_F_partial_enumeration import (                    # noqa: E402
    LPBuilder, model_rows, rho, Vj, UK, LK, rationalize)

TOL = 1e-9
CONFIGS = [(2, 4), (2, 5), (2, 6), (3, 6), (3, 7)]
ETAS = [1.25, 1.5, 2.0, 2.5]

# Default (eta_u, eta_o) split.  RATIONAL on purpose: with eta_o = 1 every LP
# coefficient is rational for the eta values used here, which is what makes the
# exact Fraction re-check of a witness possible.  Section 1.3 of the md gives the
# scaling argument that only the product eta matters; `gates` checks it numerically.
def split(eta):
    return (float(eta), 1.0)


# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------
def mask(elems):
    m = 0
    for e in elems:
        m |= 1 << e
    return m


def bits(m):
    return [i for i in range(m.bit_length()) if m >> i & 1]


def greedy_rows(n, N, K):
    """Predictive greedy picks 0, 1, ..., K-1 in this order (adversarial ties):
    at state S_t = {0..t-1} the chosen element t has dtilde_t(S_t) >= dtilde_e(S_t)
    for every other candidate e.  The common ftilde(S_t) cancels."""
    G = lambda S: N + S
    rows = []
    for t in range(K):
        S = (1 << t) - 1
        for e in range(n):
            if e == t or S >> e & 1:
                continue
            rows.append({G(S | 1 << e): 1.0, G(S | 1 << t): -1.0})
    return rows


# ---------------------------------------------------------------------------
# candidate A
# ---------------------------------------------------------------------------
def candA_rows(n, K, N):
    """Branch fixed by relabelling: shortlist M = {0..K}, output A* = {0..K-1}."""
    m = K + 1
    G = lambda S: N + S
    rows = []
    for e in range(m):                       # e in M beats every e' outside M
        for e2 in range(m, n):
            rows.append({G(1 << e2): 1.0, G(1 << e): -1.0})
    Astar = (1 << K) - 1
    for A in itertools.combinations(range(m), K):   # A* is the ftilde-argmax in M
        Am = mask(A)
        if Am != Astar:
            rows.append({G(Am): 1.0, G(Astar): -1.0})
    return rows, Astar


def candA_O_reps(n, K):
    """Orbit representatives of the K-subsets O under the stabiliser of the fixed
    branch, Sym({0..K-1}) x Sym({K}) x Sym({K+1..n-1}); see md section 1.2."""
    m = K + 1
    blocks = [list(range(K)), list(range(K, m)), list(range(m, n))]
    reps = []
    for i in range(len(blocks[0]) + 1):
        for j in range(len(blocks[1]) + 1):
            k = K - i - j
            if 0 <= k <= len(blocks[2]):
                reps.append(tuple(blocks[0][:i] + blocks[1][:j] + blocks[2][:k]))
    return reps


def candA_worst(n, K, eta, eu=None, eo=None, full_O=False, verbose=False):
    if eu is None:
        eu, eo = split(eta)
    B = LPBuilder(n, eu, eo)
    rows, Astar = candA_rows(n, K, B.N)
    Os = (list(itertools.combinations(range(n), K)) if full_O
          else candA_O_reps(n, K))
    best = dict(val=np.inf, O=None)
    nlp = 0
    for O in Os:
        val = B.solve(rows, mask(O), Astar)
        nlp += 1
        if val < best["val"] - 1e-12:
            best = dict(val=val, O=list(O))
        if verbose:
            print(f"      O={O}: {val:.9f}")
    n_branches_raw = math.comb(n, K + 1) * (K + 1)
    return dict(val=best["val"], O=best["O"], n_lps=nlp,
                n_branches=len(Os), n_branches_raw=n_branches_raw,
                branch=dict(M=list(range(K + 1)), Astar=list(range(K))),
                status="OK")


# ---------------------------------------------------------------------------
# candidate B
# ---------------------------------------------------------------------------
def candB_search(n, K, eta, eu=None, eo=None, swap_mode="continue",
                 time_limit=900.0, verbose=False, ub_init=None):
    """Exhaustive min over (O, accept/reject profile) with branch and bound.

    Relabelling (md section 1.2) fixes the greedy trajectory to 0 -> 1 -> ... ->
    K-1 AND the scan list to K < K+1 < ... < n-1 in this order, so O still ranges
    over ALL C(n,K) subsets.

    Node bound: the slots already finalised (slots 0..p-1) are contained in every
    final T below the node, so f monotone gives f(T_final) >= f(B) and the LP with
    objective f(B) and the node's constraints is a valid lower bound for the whole
    subtree.  Node constraints are a subset of every leaf's, so it is also a
    relaxation on the instance side.
    """
    if eu is None:
        eu, eo = split(eta)
    LP = LPBuilder(n, eu, eo)
    N = LP.N
    G = lambda S: N + S
    base = greedy_rows(n, N, K)
    L = list(range(K, n))                        # scan list, ascending
    T0 = list(range(K))                          # slots in insertion order
    stats = dict(nodes=0, leaves=0, pruned=0, lp=0)
    # ub_init seeds the incumbent.  Every node whose bound is >= ub_init is cut,
    # so a search that COMPLETES without improving certifies worst case >= ub_init
    # (a valid LOWER bound); a search that improves behaves as if unseeded.
    best = dict(val=np.inf if ub_init is None else float(ub_init),
                O=None, profile=None, T=None)
    seeded = ub_init is not None
    t_start = time.time()

    class Stop(Exception):
        pass

    def solve(rows, O_mask, obj_mask):
        stats["lp"] += 1
        if time.time() - t_start > time_limit:
            raise Stop
        return LP.solve(rows, O_mask, obj_mask)

    def rec(O_mask, p, i, cur, rows):
        stats["nodes"] += 1
        if p == K:                                          # leaf
            stats["leaves"] += 1
            val = solve(rows, O_mask, mask(cur))
            if val < best["val"] - 1e-9:
                best.update(val=val, O=O_mask, profile=list(rows_profile),
                            T=list(cur))
                if verbose:
                    print(f"      incumbent {val:.9f} O={bits(O_mask)} T={cur}",
                          flush=True)
            return
        if i == len(L):                                     # slot p is now final
            if p + 1 < K:        # bound with the finalised prefix cur[0..p]
                if solve(rows, O_mask, mask(cur[:p + 1])) >= best["val"] - 1e-9:
                    stats["pruned"] += 1
                    return
            rec(O_mask, p + 1, 0, cur, rows)
            return
        e = L[i]
        if e in cur:                                        # already inside T
            rec(O_mask, p, i + 1, cur, rows)
            return
        t = cur[p]
        Tcur = mask(cur)
        nxt = list(cur)
        nxt[p] = e
        Tnew = mask(nxt)
        # reject: ftilde(T - t + e) <= ftilde(T)
        rows_profile.append((p, e, 0))
        rec(O_mask, p, i + 1, cur, rows + [{G(Tnew): 1.0, G(Tcur): -1.0}])
        rows_profile.pop()
        # accept: ftilde(T - t + e) >= ftilde(T)
        rows_profile.append((p, e, 1))
        arows = rows + [{G(Tcur): 1.0, G(Tnew): -1.0}]
        if swap_mode == "first":
            rec(O_mask, p + 1, 0, nxt, arows)
        else:
            rec(O_mask, p, i + 1, nxt, arows)
        rows_profile.pop()

    rows_profile = []
    status = "OK"
    for O in itertools.combinations(range(n), K):
        Om = mask(O)
        try:
            rec(Om, 0, 0, list(T0), base)
        except Stop:
            status = "TIMEOUT"
            break
    n_leaves_total = _leaf_count(n, K, swap_mode) * math.comb(n, K)
    if seeded and best["profile"] is None:
        # exhaustive search never went below the seed: a certified LOWER bound.
        # If it also ran out of time, the returned number is just the seed and
        # certifies nothing.
        status = ("OK_NO_IMPROVEMENT_BELOW_SEED" if status == "OK"
                  else "TIMEOUT_SEEDED_NOT_IMPROVED")
    return dict(val=best["val"], O=None if best["O"] is None else bits(best["O"]),
                T=best["T"], profile=best["profile"], status=status,
                n_lps=stats["lp"], n_leaves=stats["leaves"],
                n_nodes=stats["nodes"], n_pruned=stats["pruned"],
                n_branches=n_leaves_total, swap_mode=swap_mode,
                seed=ub_init, improved=best["profile"] is not None,
                secs=time.time() - t_start)


def solve_with_rhs(LP, extra_rows, extra_rhs, O_mask, obj_mask, want_x=False):
    """LPBuilder.solve, but the extra rows may have a nonzero right-hand side
    (needed for the eps-strict variant of candidate B's swap test)."""
    from H_F_partial_enumeration import _to_csr
    A = LP.base_csr
    b = np.zeros(A.shape[0])
    if extra_rows:
        A = vstack([A, _to_csr(extra_rows, LP.nv)]).tocsr()
        b = np.concatenate([b, np.asarray(extra_rhs, dtype=float)])
    obj = np.zeros(LP.nv)
    obj[obj_mask] = 1.0
    A_eq = _to_csr([{0: 1.0}, {LP.N: 1.0}, {O_mask: 1.0}], LP.nv)
    res = linprog(obj, A_ub=A, b_ub=b, A_eq=A_eq, b_eq=[0.0, 0.0, 1.0],
                  bounds=[(None, None)] * LP.nv, method="highs")
    if res.status != 0:
        return (np.inf, None) if want_x else np.inf
    return (res.fun, res.x) if want_x else res.fun


def candB_eps(n, K, eta, eps, eu=None, eo=None, swap_mode="continue",
              time_limit=600.0):
    """Candidate B with the LITERAL strict swap rule relaxed to a margin:
    accept requires ftilde(T-t+e) >= ftilde(T) + eps, reject requires <=.
    eps > 0 is an under-approximation of "strictly larger"; the value is
    non-decreasing as eps grows, and lim_{eps -> 0+} equals the eps = 0
    (tie-adversarial) value iff the tie convention does not move the infimum."""
    if eu is None:
        eu, eo = split(eta)
    LP = LPBuilder(n, eu, eo)
    N = LP.N
    G = lambda S: N + S
    base = greedy_rows(n, N, K)
    L = list(range(K, n))
    best = dict(val=np.inf)
    t0 = time.time()
    nlp = [0]

    class Stop(Exception):
        pass

    def solve(rows, rhs, O_mask, obj_mask):
        nlp[0] += 1
        if time.time() - t0 > time_limit:
            raise Stop
        return solve_with_rhs(LP, rows, rhs, O_mask, obj_mask)

    def rec(O_mask, p, i, cur, rows, rhs):
        if p == K:
            v = solve(rows, rhs, O_mask, mask(cur))
            if v < best["val"] - 1e-12:
                best["val"] = v
            return
        if i == len(L):
            if p + 1 < K and solve(rows, rhs, O_mask,
                                   mask(cur[:p + 1])) >= best["val"] - 1e-12:
                return
            rec(O_mask, p + 1, 0, cur, rows, rhs)
            return
        e = L[i]
        if e in cur:
            rec(O_mask, p, i + 1, cur, rows, rhs)
            return
        Tc = mask(cur)
        nxt = list(cur)
        nxt[p] = e
        Tn = mask(nxt)
        rec(O_mask, p, i + 1, cur,
            rows + [{G(Tn): 1.0, G(Tc): -1.0}], rhs + [0.0])
        arows = rows + [{G(Tc): 1.0, G(Tn): -1.0}]
        arhs = rhs + [-eps]
        if swap_mode == "first":
            rec(O_mask, p + 1, 0, nxt, arows, arhs)
        else:
            rec(O_mask, p, i + 1, nxt, arows, arhs)

    status = "OK"
    for O in itertools.combinations(range(n), K):
        try:
            rec(mask(O), 0, 0, list(range(K)), base, [0.0] * len(base))
        except Stop:
            status = "TIMEOUT"
            break
    return dict(val=best["val"], eps=eps, status=status, n_lps=nlp[0],
                secs=time.time() - t0)


def _leaf_count(n, K, swap_mode):
    """Number of accept/reject profiles per O (combinatorial, no LP)."""
    L = list(range(K, n))

    def rec(p, i, cur):
        if p == K:
            return 1
        if i == len(L):
            return rec(p + 1, 0, cur)
        e = L[i]
        if e in cur:
            return rec(p, i + 1, cur)
        nxt = list(cur)
        nxt[p] = e
        if swap_mode == "first":
            return rec(p, i + 1, cur) + rec(p + 1, 0, nxt)
        return rec(p, i + 1, cur) + rec(p, i + 1, nxt)

    return rec(0, 0, list(range(K)))


def greedy_rows_traj(n, N, traj):
    """Greedy trajectory rows for an ARBITRARY ordered trajectory (used only by
    Gate 5, which checks that fixing traj = (0,...,K-1) is WLOG)."""
    G = lambda S: N + S
    rows, S = [], 0
    for t in traj:
        for e in range(n):
            if e == t or S >> e & 1:
                continue
            rows.append({G(S | 1 << e): 1.0, G(S | 1 << t): -1.0})
        S |= 1 << t
    return rows


def candB_search_traj(n, K, eta, traj, eu=None, eo=None, swap_mode="continue",
                      time_limit=600.0, incumbent=np.inf):
    """Candidate B restricted to one ordered greedy trajectory `traj`, with the
    scan list = sorted([n] \\ traj) in ASCENDING GLOBAL INDEX order (the real
    algorithm).  Gate 5 minimises this over all ordered trajectories and compares
    with candB_search, which only uses traj = (0, 1, ..., K-1)."""
    if eu is None:
        eu, eo = split(eta)
    LP = LPBuilder(n, eu, eo)
    N = LP.N
    G = lambda S: N + S
    base = greedy_rows_traj(n, N, traj)
    L = sorted(e for e in range(n) if e not in traj)
    best = dict(val=incumbent)
    t0 = time.time()

    class Stop(Exception):
        pass

    def solve(rows, O_mask, obj_mask):
        if time.time() - t0 > time_limit:
            raise Stop
        return LP.solve(rows, O_mask, obj_mask)

    def rec(O_mask, p, i, cur, rows):
        if p == K:
            v = solve(rows, O_mask, mask(cur))
            if v < best["val"] - 1e-12:
                best["val"] = v
            return
        if i == len(L):
            if p + 1 < K and solve(rows, O_mask,
                                   mask(cur[:p + 1])) >= best["val"] - 1e-9:
                return
            rec(O_mask, p + 1, 0, cur, rows)
            return
        e = L[i]
        if e in cur:
            rec(O_mask, p, i + 1, cur, rows)
            return
        Tc = mask(cur)
        nxt = list(cur)
        nxt[p] = e
        Tn = mask(nxt)
        rec(O_mask, p, i + 1, cur, rows + [{G(Tn): 1.0, G(Tc): -1.0}])
        arows = rows + [{G(Tc): 1.0, G(Tn): -1.0}]
        if swap_mode == "first":
            rec(O_mask, p + 1, 0, nxt, arows)
        else:
            rec(O_mask, p, i + 1, nxt, arows)

    status = "OK"
    for O in itertools.combinations(range(n), K):
        try:
            rec(mask(O), 0, 0, list(traj), base)
        except Stop:
            status = "TIMEOUT"
            break
    return dict(val=best["val"], status=status, secs=time.time() - t0)


def candB_relax_lb(n, K, eta, eu=None, eo=None):
    """Profile-free relaxation: a valid LOWER bound on candidate B's worst case,
    used when the exhaustive search times out.  Valid rows for every profile:
      (i)  ftilde(T_final) >= ftilde(T_0)   (accepted swaps never lower ftilde);
      (ii) for slot 0 and every e in the scan list,
           ftilde(T_0 - g_0 + e) <= ftilde(T_final).
           At the moment (0, e) is examined the current set is T_0 with slot 0
           replaced by some c, so T_cur - c + e = T_0 - g_0 + e whatever c is;
           whether the check accepts or rejects, that value is <= ftilde of the
           set held afterwards, hence <= ftilde(T_final).
    Minimised over the final set m and over O."""
    if eu is None:
        eu, eo = split(eta)
    LP = LPBuilder(n, eu, eo)
    N = LP.N
    G = lambda S: N + S
    base = greedy_rows(n, N, K)
    T0m = (1 << K) - 1
    best = np.inf
    for O in itertools.combinations(range(n), K):
        Om = mask(O)
        for m_set in itertools.combinations(range(n), K):
            mm = mask(m_set)
            rows = list(base)
            if mm != T0m:
                rows.append({G(T0m): 1.0, G(mm): -1.0})
            for e in range(K, n):
                s = (T0m ^ 1) | (1 << e)
                if s != mm:
                    rows.append({G(s): 1.0, G(mm): -1.0})
            v = LP.solve(rows, Om, mm)
            best = min(best, v)
    return best


# ---------------------------------------------------------------------------
# instance rebuild + simulation (consistency check)
# ---------------------------------------------------------------------------
def rebuild(n, K, eta, rows, O_mask, obj_mask, eu=None, eo=None):
    if eu is None:
        eu, eo = split(eta)
    LP = LPBuilder(n, eu, eo)
    val, x = LP.solve(rows, O_mask, obj_mask, want_x=True)
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
    return max(f[S] for S in range(1 << n) if bin(S).count("1") <= K)


def simulate_A(n, K, f, g, tol=1e-7):
    """All tie-consistent executions of candidate A; adversary minimises f."""
    m = K + 1
    sing = [g[1 << e] for e in range(n)]
    worst, arg = np.inf, None
    for M in itertools.combinations(range(n), m):
        out = [e for e in range(n) if e not in M]
        if out and min(sing[e] for e in M) < max(sing[e] for e in out) - tol:
            continue
        cand = list(itertools.combinations(M, K))
        top = max(g[mask(A)] for A in cand)
        for A in cand:
            if g[mask(A)] >= top - tol and f[mask(A)] < worst:
                worst, arg = f[mask(A)], (M, A)
    return worst, arg


def simulate_B(n, K, f, g, swap_mode="continue", strict=False, tol=1e-7):
    """All tie-consistent executions of candidate B; adversary minimises f.
    strict=False: the swap test may accept whenever ftilde(new) >= ftilde(cur)
    (tie-adversarial, matching the LP).  strict=True: the literal deterministic
    rule, accept iff ftilde(new) > ftilde(cur) (+tol)."""
    # greedy trajectories with adversarial ties
    trajs = [[]]
    for _ in range(K):
        nxt = []
        for tr in trajs:
            S = mask(tr)
            gains = {e: g[S | 1 << e] - g[S] for e in range(n) if not S >> e & 1}
            top = max(gains.values())
            for e, v in gains.items():
                if v >= top - tol * max(1.0, abs(top)):
                    nxt.append(tr + [e])
        trajs = nxt
    worst, arg = np.inf, None
    for tr in trajs:
        L = sorted(e for e in range(n) if e not in tr)
        stack = [(0, 0, list(tr), list())]
        while stack:
            p, i, cur, prof = stack.pop()
            if p == K:
                if f[mask(cur)] < worst:
                    worst, arg = f[mask(cur)], (tuple(tr), tuple(cur), tuple(prof))
                continue
            if i == len(L):
                stack.append((p + 1, 0, cur, prof))
                continue
            e = L[i]
            if e in cur:
                stack.append((p, i + 1, cur, prof))
                continue
            nxt = list(cur)
            nxt[p] = e
            dv = g[mask(nxt)] - g[mask(cur)]
            if strict:
                if dv > tol:
                    stack.append(((p + 1, 0, nxt, prof + [(p, e, 1)])
                                  if swap_mode == "first"
                                  else (p, i + 1, nxt, prof + [(p, e, 1)])))
                else:
                    stack.append((p, i + 1, cur, prof + [(p, e, 0)]))
            else:
                if dv <= tol:
                    stack.append((p, i + 1, cur, prof + [(p, e, 0)]))
                if dv >= -tol:
                    stack.append(((p + 1, 0, nxt, prof + [(p, e, 1)])
                                  if swap_mode == "first"
                                  else (p, i + 1, nxt, prof + [(p, e, 1)])))
    return worst, arg


def consistency_check(n, K, eta, cand, res, swap_mode="continue", verbose=True):
    """Rebuild the argmin branch's LP optimum as an explicit (f, ftilde), verify
    monotone / submodular / band on the whole lattice, re-run the algorithm with
    adversarial ties and compare the ratio with the LP value."""
    eu, eo = split(eta)
    N = 1 << n
    if cand == "A":
        rows, obj = candA_rows(n, K, N)
        O_mask = mask(res["O"])
    else:
        rows = list(greedy_rows(n, N, K))
        G = lambda S: N + S
        cur = list(range(K))
        for (p, e, acc) in res["profile"]:
            Tc, nx = mask(cur), list(cur)
            nx[p] = e
            Tn = mask(nx)
            rows.append({G(Tn): 1.0, G(Tc): -1.0} if acc == 0
                        else {G(Tc): 1.0, G(Tn): -1.0})
            if acc:
                cur = nx
        obj = mask(res["T"])
        O_mask = mask(res["O"])
    val, f, g = rebuild(n, K, eta, rows, O_mask, obj)
    mono, submod, band = check_model(n, f, g, eu, eo)
    OPT = opt_value(n, K, f)
    if cand == "A":
        w, arg = simulate_A(n, K, f, g)
        strict_w = None
    else:
        w, arg = simulate_B(n, K, f, g, swap_mode, strict=False)
        strict_w, _ = simulate_B(n, K, f, g, swap_mode, strict=True)
    rep = dict(lp_value=val, monotone=bool(mono), submodular=bool(submod),
               band=bool(band), OPT=OPT, sim_ratio=w / OPT,
               sim_arg=str(arg), obj_set=bits(obj), O=bits(O_mask),
               branch_ratio=f[obj] / OPT,
               strict_ratio=None if strict_w is None else strict_w / OPT)
    rep["consistent"] = bool(mono and submod and band
                             and abs(w / OPT - val) < 1e-6
                             and abs(f[obj] / OPT - val) < 1e-6)
    if verbose:
        print(f"    consistency n={n} K={K} eta={eta} cand={cand}: LP={val:.9f} "
              f"sim={w/OPT:.9f} mono={mono} submod={submod} band={band} -> "
              f"{'CONSISTENT' if rep['consistent'] else 'MISMATCH'}"
              + ("" if strict_w is None
                 else f"   [strict-rule value {strict_w/OPT:.9f}]"), flush=True)
    return rep, f, g


# ---------------------------------------------------------------------------
# exact rational re-check of a witness (only needed when a candidate beats rho_K)
# ---------------------------------------------------------------------------
def exact_witness(n, K, eta, cand, res, f, g, maxden=100000):
    """Rationalise the rebuilt instance and verify EXACTLY (Fraction arithmetic)
    monotonicity, submodularity, the band, the branch inequalities and the ratio.
    A success certifies worst_case <= the exact ratio (a witness instance); the
    matching >= direction rests on the exhaustive branch enumeration + LP."""
    eu, eo = split(eta)
    EU, EO = Fr(eu).limit_denominator(10**6), Fr(eo).limit_denominator(10**6)
    N = 1 << n
    F = [Fr(float(v)).limit_denominator(maxden) for v in f]
    Gt = [Fr(float(v)).limit_denominator(maxden) for v in g]
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
    if cand == "A":
        w, arg = simulate_A(n, K, [float(v) for v in F], [float(v) for v in Gt])
        out = mask(arg[1]) if arg else None
    else:
        w, arg = simulate_B(n, K, [float(v) for v in F], [float(v) for v in Gt])
        out = mask(arg[1]) if arg else None
    OPT = max(F[S] for S in range(N) if bin(S).count("1") <= K)
    ratio = None if out is None else F[out] / OPT
    return dict(exact_ok=all(ok.values()), detail=ok,
                exact_ratio=None if ratio is None else str(ratio),
                exact_ratio_float=None if ratio is None else float(ratio))


# ---------------------------------------------------------------------------
# gates
# ---------------------------------------------------------------------------
def run_gates():
    out = {}
    print("=" * 78)
    print("Gate 1: reproduce rho_K with the FROZEN code/worst_case_lp.py")
    print("=" * 78)
    g1 = []
    for (K, n) in CONFIGS:
        for eta in ETAS:
            eu, eo = split(eta)
            val, O, _ = worst_case_lp.worst_case(n, K, eu, eo, "single")
            d = val - rho(K, eta)
            print(f"  K={K} n={n} eta={eta}: greedy LP = {val:.9f}  "
                  f"rho_K = {rho(K, eta):.9f}  diff = {d:+.2e}", flush=True)
            g1.append(dict(K=K, n=n, eta=eta, lp=val, rho=rho(K, eta), diff=d))
    out["gate1_rho"] = g1

    print("=" * 78)
    print("Gate 2: candidate A, O-symmetry reduction vs full O enumeration")
    print("=" * 78)
    g2 = []
    for (K, n) in [(2, 4), (2, 5), (3, 6)]:
        for eta in [1.5, 2.0]:
            a = candA_worst(n, K, eta)
            b = candA_worst(n, K, eta, full_O=True)
            print(f"  K={K} n={n} eta={eta}: reps({a['n_lps']} LPs)={a['val']:.9f}  "
                  f"full({b['n_lps']} LPs)={b['val']:.9f}  "
                  f"diff={a['val']-b['val']:+.2e}", flush=True)
            g2.append(dict(K=K, n=n, eta=eta, reps=a["val"], full=b["val"],
                           diff=a["val"] - b["val"]))
    out["gate2_symmetry"] = g2

    print("=" * 78)
    print("Gate 3: (eta_u, eta_o) split invariance (only the product matters)")
    print("=" * 78)
    g3 = []
    for (K, n, cand) in [(2, 4, "A"), (2, 4, "B"), (2, 5, "B"), (3, 6, "A")]:
        eta = 2.0
        for (eu, eo) in [(2.0, 1.0), (1.0, 2.0), (2.0 ** 0.5, 2.0 ** 0.5)]:
            if cand == "A":
                v = candA_worst(n, K, eta, eu=eu, eo=eo)["val"]
            else:
                v = candB_search(n, K, eta, eu=eu, eo=eo, time_limit=600)["val"]
            print(f"  K={K} n={n} cand={cand} (eu,eo)=({eu:.4f},{eo:.4f}): "
                  f"{v:.9f}", flush=True)
            g3.append(dict(K=K, n=n, cand=cand, eta_u=eu, eta_o=eo, val=v))
    out["gate3_split"] = g3

    print("=" * 78)
    print("Gate 4: candidate B leaf counts (combinatorial, no LP)")
    print("=" * 78)
    g4 = []
    for (K, n) in CONFIGS:
        c = _leaf_count(n, K, "continue")
        fst = _leaf_count(n, K, "first")
        tot = math.comb(n, K)
        print(f"  K={K} n={n}: profiles/O continue={c} first={fst}   "
              f"#O={tot}   leaves continue={c*tot} first={fst*tot}")
        g4.append(dict(K=K, n=n, per_O_continue=c, per_O_first=fst, nO=tot))
    out["gate4_leafcounts"] = g4

    print("=" * 78)
    print("Gate 5: candidate B, fixing the greedy trajectory to (0..K-1) is WLOG")
    print("=" * 78)
    g5 = []
    for (K, n) in [(2, 4), (2, 5)]:
        for eta in [1.25, 2.0]:
            fixed = candB_search(n, K, eta, time_limit=600)["val"]
            allt = np.inf
            worst_traj = None
            for traj in itertools.permutations(range(n), K):
                v = candB_search_traj(n, K, eta, traj, time_limit=600)["val"]
                if v < allt:
                    allt, worst_traj = v, traj
            print(f"  K={K} n={n} eta={eta}: fixed traj = {fixed:.9f}   "
                  f"min over all {math.perm(n, K)} ordered trajs = {allt:.9f} "
                  f"(argmin {worst_traj})   diff = {fixed-allt:+.2e}", flush=True)
            g5.append(dict(K=K, n=n, eta=eta, fixed=fixed, all_trajs=allt,
                           argmin_traj=list(worst_traj), diff=fixed - allt))
    out["gate5_trajectory_wlog"] = g5
    return out


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------
def run_config(K, n, eta, cand, swap_mode="continue", time_limit=900.0,
               do_check=True, seed=None):
    t0 = time.time()
    print(f"[{time.strftime('%H:%M:%S')}] K={K} n={n} eta={eta} cand={cand} "
          f"mode={swap_mode} seed={seed}", flush=True)
    if cand == "A":
        res = candA_worst(n, K, eta)
    else:
        res = candB_search(n, K, eta, swap_mode=swap_mode, time_limit=time_limit,
                           ub_init=seed)
    val = res["val"]
    fr = rationalize(val) if np.isfinite(val) else None
    r, U = rho(K, eta), UK(K, eta)
    kind, vs_rho, vs_U = _classify(val, r, U, res["status"])
    row = dict(K=K, n=n, eta=eta, candidate=cand, swap_mode=swap_mode,
               value_float=None if not np.isfinite(val) else float(val),
               value_fraction=None if fr is None else str(fr),
               value_kind=kind,
               value_is_upper_bound_only=(kind == "upper_bound"),
               value_is_lower_bound_only=(kind == "lower_bound"),
               n_branches=res.get("n_branches"), n_lps=res.get("n_lps"),
               n_leaves=res.get("n_leaves"), n_pruned=res.get("n_pruned"),
               status=res["status"], rho=r, U=U, seed=res.get("seed"),
               vs_rho=vs_rho, vs_U=vs_U,
               gap_vs_rho=None if not np.isfinite(val) else float(val - r),
               O=res.get("O"), T=res.get("T"),
               profile=res.get("profile"), secs=time.time() - t0)
    print(f"    value = {val:.9f} ({fr}) [{row['value_kind']}]   "
          f"rho_{K} = {r:.9f}   U_{K} = {U:.9f}"
          f"   -> {row['vs_rho']}   status={res['status']}  "
          f"LPs={res.get('n_lps')}  ({row['secs']:.0f}s)", flush=True)
    if res["status"] == "TIMEOUT":
        lb = candB_relax_lb(n, K, eta)
        row["timeout_upper_bound"] = float(val)
        row["relaxation_lower_bound"] = float(lb)
        print(f"    TIMEOUT: incumbent (upper bound) {val:.9f}, "
              f"profile-free relaxation lower bound {lb:.9f}", flush=True)
    have_branch = (cand == "A") or (res.get("profile") is not None)
    if do_check and np.isfinite(val) and have_branch:
        rep, f, g = consistency_check(n, K, eta, cand, res, swap_mode)
        row["consistency"] = rep
        if vs_rho == "strictly_better":
            print("    *** strictly better than rho_K: exact rational re-check ***",
                  flush=True)
            row["exact_recheck"] = exact_witness(n, K, eta, cand, res, f, g)
            row["query_audit"] = query_audit(n, K, cand)
            print(f"    exact: {row['exact_recheck']}", flush=True)
    return row


def query_audit(n, K, cand):
    """Check the L1 assumptions (queries of size <= K, at most nK of them)."""
    if cand == "A":
        q, sizes = n + math.comb(K + 1, K), [1, K]
    else:
        q = sum(n - t for t in range(K)) + K * (n - K)
        sizes = [1, K]
    return dict(n_queries=q, budget_nK=n * K, max_query_size=max(sizes),
                size_ok=max(sizes) <= K, budget_ok=q <= n * K)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="all",
                    choices=["all", "gates", "run", "merge", "lb",
                             "extra", "epsstudy"])
    ap.add_argument("--K", type=int)
    ap.add_argument("--n", type=int)
    ap.add_argument("--eta", type=float)
    ap.add_argument("--cand", choices=["A", "B"])
    ap.add_argument("--swap-mode", default="continue", choices=["continue", "first"])
    ap.add_argument("--time-limit", type=float, default=900.0)
    ap.add_argument("--seed", type=float, default=None,
                    help="seed the branch-and-bound incumbent (candidate B). A "
                         "search that COMPLETES without improving on the seed "
                         "certifies worst case >= seed.")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    path = os.path.join(HERE, "L2_linear_candidates.json")
    if args.mode == "gates":
        log = _load(path)
        log["gates"] = run_gates()
        _dump(path, log)
        return
    if args.mode == "lb":
        print(candB_relax_lb(args.n, args.K, args.eta))
        return
    if args.mode == "extra":
        # md section 3.3 (swap_mode = first) and section 4.6 (candidate A at larger n)
        extra = dict(A_larger_n=[], B_swapmode_first=[])
        for (K, n) in [(2, 7), (2, 8), (3, 8)]:
            for eta in ETAS:
                r = candA_worst(n, K, eta)
                print(f"  A K={K} n={n} eta={eta}: {r['val']:.9f} "
                      f"({rationalize(r['val'])})  1/(K eta) = {1/(K*eta):.9f}",
                      flush=True)
                extra["A_larger_n"].append(
                    dict(K=K, n=n, eta=eta, val=r["val"],
                         frac=str(rationalize(r["val"])), rho=rho(K, eta)))
        for (K, n) in [(2, 5), (2, 6), (3, 6)]:
            for eta in ETAS:
                r = candB_search(n, K, eta, swap_mode="first", time_limit=600)
                print(f"  B(first) K={K} n={n} eta={eta}: {r['val']:.9f} "
                      f"({rationalize(r['val'])})  rho = {rho(K, eta):.9f}  "
                      f"{r['status']}", flush=True)
                extra["B_swapmode_first"].append(
                    dict(K=K, n=n, eta=eta, val=r["val"],
                         frac=str(rationalize(r["val"])), status=r["status"],
                         rho=rho(K, eta)))
        _dump(os.path.join(HERE, "_L2_shard_extra.json"), dict(extra=extra))
        return
    if args.mode == "epsstudy":
        # md section 4.5: does the tie convention move the infimum?
        out = []
        for (K, n, eta) in [(2, 5, 1.25), (2, 6, 1.25), (2, 6, 2.0),
                            (2, 4, 1.25), (3, 6, 1.25), (3, 6, 2.0)]:
            row = dict(K=K, n=n, eta=eta)
            for eps in [0.0, 1e-8, 1e-6, 1e-4]:
                r = (candB_search(n, K, eta, time_limit=600) if eps == 0.0
                     else candB_eps(n, K, eta, eps, time_limit=600))
                row[f"eps_{eps:g}"] = r["val"]
                row[f"status_{eps:g}"] = r["status"]
                print(f"  K={K} n={n} eta={eta} eps={eps:g}: {r['val']:.9f} "
                      f"{r['status']}", flush=True)
            out.append(row)
        _dump(os.path.join(HERE, "_L2_shard_eps.json"), dict(eps_study=out))
        return
    if args.mode == "merge":
        log = _load(path)
        rows = {(_key(r)): r for r in log.get("results", [])}
        for fn in sorted(os.listdir(HERE)):
            if fn.startswith("_L2_shard_") and fn.endswith(".json"):
                sh = _load(os.path.join(HERE, fn))
                if "seeded" in fn:
                    # seeded re-runs answer a different question; keep them out
                    # of `results` so they cannot overwrite an unseeded row
                    log.setdefault("seeded_reruns", [])
                    have = {_key(x) for x in log["seeded_reruns"]}
                    for r in sh.get("results", []):
                        _normalise_labels(r)
                        if _key(r) in have:
                            log["seeded_reruns"] = [
                                x for x in log["seeded_reruns"] if _key(x) != _key(r)]
                        log["seeded_reruns"].append(r)
                    continue
                for r in sh.get("results", []):
                    rows[_key(r)] = r
                for k in ("extra", "eps_study"):
                    if k in sh:
                        log[k] = sh[k]
                if "gate5" in sh:
                    log.setdefault("gates", {})["gate5_trajectory_wlog"] = sh["gate5"]
        for r in rows.values():
            _normalise_labels(r)
        log["results"] = [rows[k] for k in sorted(rows)]
        _dump(path, log)
        print(f"merged {len(log['results'])} rows into {path}")
        return
    if args.mode == "run":
        row = run_config(args.K, args.n, args.eta, args.cand,
                         args.swap_mode, args.time_limit, seed=args.seed)
        sfx = "" if args.seed is None else "_seeded"
        out = args.out or os.path.join(
            HERE, f"_L2_shard_{args.cand}_{args.K}_{args.n}_{args.eta}"
                  f"_{args.swap_mode}{sfx}.json")
        _dump(out, dict(results=[row]))
        print(f"wrote {out}")
        return
    # all
    log = _load(path)
    log.setdefault("results", [])
    rows = {(_key(r)): r for r in log["results"]}
    log["gates"] = run_gates()
    for cand in ("A", "B"):
        for (K, n) in CONFIGS:
            for eta in ETAS:
                r = run_config(K, n, eta, cand, args.swap_mode, args.time_limit)
                rows[_key(r)] = r
    log["results"] = [rows[k] for k in sorted(rows)]
    _dump(path, log)
    print(f"wrote {path}")


def _classify(v, r, U, status):
    """What the returned number actually IS, and what it licenses.

    status "OK"                          -> v is the EXACT worst case.
    status "TIMEOUT"                     -> v is the incumbent, an UPPER bound
        on the exact worst case: it can support "worse than rho_K" (exact <= v <
        rho) but NEVER "strictly better".
    status "OK_NO_IMPROVEMENT_BELOW_SEED"-> the exhaustive search finished
        without going below the seed, so v (= the seed) is a certified LOWER
        bound: it can support "strictly better than rho_K" (exact >= v > rho)
        but never "worse"."""
    if not np.isfinite(v):
        return "none", "unknown", "unknown"
    if status == "OK":
        return ("exact",
                "strictly_better" if v > r + 1e-9 else
                "equal" if abs(v - r) <= 1e-9 else "worse",
                "above_U" if v > U + 1e-9 else
                "equal_U" if abs(v - U) <= 1e-9 else "below_U")
    if status == "OK_NO_IMPROVEMENT_BELOW_SEED":
        return ("lower_bound",
                "strictly_better" if v > r + 1e-9
                else "inconclusive_lower_bound_only",
                "above_U" if v > U + 1e-9 else "inconclusive_lower_bound_only")
    if status == "TIMEOUT_SEEDED_NOT_IMPROVED":
        # a seeded search that neither completed nor improved on the seed: the
        # returned number IS the seed and carries no information whatsoever.
        return ("none_seed_not_improved", "no_information", "no_information")
    return ("upper_bound",
            "worse" if v < r - 1e-9 else "inconclusive_upper_bound_only",
            "below_U" if v < U - 1e-9 else "inconclusive_upper_bound_only")


def _normalise_labels(r):
    """Recompute value_kind / vs_rho / vs_U from status (see _classify)."""
    v = r.get("value_float")
    if v is None:
        return r
    kind, vs_rho, vs_U = _classify(v, rho(r["K"], r["eta"]),
                                   UK(r["K"], r["eta"]), r.get("status"))
    r["value_kind"] = kind
    r["value_is_upper_bound_only"] = (kind == "upper_bound")
    r["value_is_lower_bound_only"] = (kind == "lower_bound")
    r["vs_rho"], r["vs_U"] = vs_rho, vs_U
    return r


def _key(r):
    return (r["candidate"], r["K"], r["n"], r["eta"], r.get("swap_mode", ""))


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


if __name__ == "__main__":
    main()
