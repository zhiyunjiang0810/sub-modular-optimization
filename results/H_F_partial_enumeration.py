#!/usr/bin/env python3
"""H-F: exact worst case of partial enumeration PE_1 at finite K (Tianming probe B).

PE_1 (the R=1 member of the Nemhauser-Wolsey-Fisher 1978 Section 7 family,
transplanted to the prediction model): for EVERY single element v of the ground
set, run predictive greedy STARTING from {v} until the set has K elements,
obtaining T_v; output argmax_v ftilde(T_v).  Both the per-step greedy argmax and
the final argmax over starts are resolved ADVERSARIALLY (the adversary picks the
tie it likes at every greedy step of every start, and picks which maximiser of
ftilde(T_v) is returned).

Model (paper/sections/model.tex):
    f monotone submodular, f(empty) = 0, not queryable;
    ftilde arbitrary with ftilde(empty) = 0;
    global band  d_e(S)/eta_u <= dtilde_e(S) <= eta_o d_e(S)  for ALL S and
    e notin S (single-element form of Definition 1);  eta = eta_u * eta_o.

Worst case = min over instances of f(output)/max_{|A|<=K} f(A).  As in
code/worst_case_lp.py the maximum is handled by fixing the optimal set O,
setting f(O) = 1 and minimising over the choice of O: for any instance,
normalising by f(O*) makes it feasible for the LP with O = O*, and conversely an
LP optimum with f(O) = 1 has true ratio <= its objective, so the two minima
coincide.

Structure of the computation
----------------------------
The worst case is a min over COMBINATORIAL CHOICE PROFILES of an LP value.  A
profile fixes, for each start v, the two further greedy picks (a_v, b_v), plus
the winning start v*.  Relabelling lets us fix v* = 0 and T_0 = {0,1,2} with
greedy order 0 -> 1 -> 2; O still ranges over all K-subsets and every other
start still has (n-1)(n-2) trajectories, so a raw sweep is 20 * 20^5 LPs at
n = 6.  We therefore use

  (a) a PROFILE-FREE RELAXATION giving a valid lower bound LB: for every start
      v and every e != v, greedy from {v} first moves to the ftilde-argmax and
      then only adds nonnegative predicted gain, hence
          ftilde(T_0) >= ftilde(T_v) >= ftilde({v, e}) ,
      which is linear and does not mention (a_v, b_v);

  (b) an UPPER BOUND UB from concrete profiles / concrete instances;

  (c) branch and bound over the trajectories of the remaining starts, using (a)
      at every node, whenever LB < UB.

Headline result (see results/H_F_partial_enumeration.md), K = 3:

     eta   rho_3      PE_1(n=6)   PE_1(n=7)   PE_1(n=8)
     1.5   9/16       19/29       16/27       16/27
     2.0   7/15       1/2         4/9         4/9
     2.5   7/18       2/5         43/120      16/45

so PE_1 beats greedy at n = 2K but falls BELOW rho_3 once n >= 7 (eta >= 1.75).
rho_K is n-free; PE_1's worst case is not.

Modes
-----
    instances   PE_1 on the known rho_K-attaining families (N2, U_K)
    selfcheck   reproduce rho_3 with the same row builder (gate)
    lb          the profile-free relaxation bound
    main        the deliverable table: exact PE_1 at n = 6, 7 + certificates
    sweep       15-point eta sweep at n = 6 and the closed-form conjecture
    split       (eta_u, eta_o) split invariance
    n7sweep     six-point eta sweep at n = 7
    n8          exact PE_1 at n = 8 (slow)
    crosscheck  re-run with BOTH greedy picks branched (validates the collapse)
    all         everything except n8 / n7sweep / crosscheck
Outputs: results/H_F_partial_enumeration.json (machine readable log).
"""
import itertools
import json
import os
import sys
import time
from fractions import Fraction as Fr

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code"))

TOL = 1e-9
ETAS = [1.5, 2.0, 2.5]


# ---------------------------------------------------------------------------
# closed forms
# ---------------------------------------------------------------------------
def Vj(K, j, eta):
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    return 1 - q ** j * (1 - (K - j) / (K * eta))


def rho(K, eta):
    """Exact worst case of single-step predictive greedy (T6 / thm:exact)."""
    return min(Vj(K, j, eta) for j in range(K))


def LK(K, eta):
    return 1 - (1 - 1 / (eta * K)) ** K


def UK(K, eta):
    return 1 - (1 - 1 / (eta * (K - 1) + 1)) ** K


# ---------------------------------------------------------------------------
# LP row construction
# ---------------------------------------------------------------------------
def model_rows(n, eta_u, eta_o, err_model="single"):
    """Rows (dicts col->coef) for A_ub x <= 0 encoding the model constraints:
    f monotone submodular and the prediction band.  Vars: f(S) -> S,
    ftilde(S) -> N + S with N = 2^n."""
    N = 1 << n
    F = lambda S: S
    G = lambda S: N + S
    rows = []

    def add(c):
        rows.append(c)

    for S in range(N):                                   # monotone f
        for e in range(n):
            if not S >> e & 1:
                add({F(S): 1.0, F(S | 1 << e): -1.0})
    for S in range(N):                                   # submodular f
        for e in range(n):
            if S >> e & 1:
                continue
            for e2 in range(n):
                if e2 == e or S >> e2 & 1:
                    continue
                T = S | 1 << e2
                c = {}
                for k, v in ((F(T | 1 << e), 1.0), (F(T), -1.0),
                             (F(S | 1 << e), -1.0), (F(S), 1.0)):
                    c[k] = c.get(k, 0.0) + v
                add(c)
    for A in range(N):                                   # band
        comp = (N - 1) ^ A
        if err_model == "single":
            Bs = [1 << e for e in range(n) if comp >> e & 1]
        else:
            Bs, B = [], comp
            while B:
                Bs.append(B)
                B = (B - 1) & comp
        for B in Bs:
            AB = A | B
            c = {}
            for k, v in ((F(AB), 1.0 / eta_u), (F(A), -1.0 / eta_u),
                         (G(AB), -1.0), (G(A), 1.0)):
                c[k] = c.get(k, 0.0) + v
            add(c)
            c = {}
            for k, v in ((G(AB), 1.0), (G(A), -1.0),
                         (F(AB), -eta_o), (F(A), eta_o)):
                c[k] = c.get(k, 0.0) + v
            add(c)
    return rows


def traj_rows(n, N, v, picks):
    """Greedy trajectory rows for the run started at {v} with picks = (a, b, ...).
    At each state the chosen element's predicted gain is >= every candidate's."""
    G = lambda S: N + S
    rows = []
    S = 1 << v
    for p in picks:
        for e in range(n):
            if e == p or S >> e & 1:
                continue
            rows.append({G(S | 1 << e): 1.0, G(S | 1 << p): -1.0})
        S |= 1 << p
    return rows


def relax_rows(n, N, v, Tstar_mask):
    """Profile-free necessary conditions for start v: ftilde(T_{v*}) >=
    ftilde({v,e}) for every e != v (valid because the first greedy move from {v}
    goes to the ftilde-argmax and later predicted gains are nonnegative)."""
    G = lambda S: N + S
    rows = []
    for e in range(n):
        if e == v:
            continue
        rows.append({G((1 << v) | (1 << e)): 1.0, G(Tstar_mask): -1.0})
    return rows


def sel_row(N, Tv_mask, Tstar_mask):
    """Final argmax: ftilde(T_v) <= ftilde(T_{v*})."""
    G = lambda S: N + S
    if Tv_mask == Tstar_mask:
        return None
    return {G(Tv_mask): 1.0, G(Tstar_mask): -1.0}


def _to_csr(rows, nv):
    data, indices, indptr = [], [], [0]
    for c in rows:
        for k, v in c.items():
            if v != 0.0:
                indices.append(k)
                data.append(v)
        indptr.append(len(indices))
    return csr_matrix((data, indices, indptr), shape=(len(rows), nv))


class LPBuilder:
    """Caches the (expensive) model rows for one (n, eta_u, eta_o)."""

    def __init__(self, n, eta_u, eta_o, err_model="single"):
        self.n, self.N = n, 1 << n
        self.nv = 2 * self.N
        self.base = model_rows(n, eta_u, eta_o, err_model)
        self.base_csr = _to_csr(self.base, self.nv)

    def solve(self, extra_rows, O_mask, obj_mask, want_x=False):
        A = self.base_csr
        if extra_rows:
            A = _stack(self.base_csr, _to_csr(extra_rows, self.nv))
        b = np.zeros(A.shape[0])
        obj = np.zeros(self.nv)
        obj[obj_mask] = 1.0
        A_eq = _to_csr([{0: 1.0}, {self.N: 1.0}, {O_mask: 1.0}], self.nv)
        res = linprog(obj, A_ub=A, b_ub=b, A_eq=A_eq, b_eq=[0.0, 0.0, 1.0],
                      bounds=[(None, None)] * self.nv, method="highs")
        if res.status != 0:
            return (np.inf, None) if want_x else np.inf
        return (res.fun, res.x) if want_x else res.fun


def _stack(A, B):
    from scipy.sparse import vstack
    return vstack([A, B]).tocsr()


# ---------------------------------------------------------------------------
# PE_1 / greedy on a concrete instance (adversarial ties everywhere)
# ---------------------------------------------------------------------------
def all_trajectories(n, K, g, start_mask, tol=1e-9):
    """All tie-consistent greedy continuations (on ftilde = g) from start_mask
    until K elements.  Returns the list of reached masks."""
    frontier = [start_mask]
    while bin(frontier[0]).count("1") < K:
        nxt = set()
        for S in frontier:
            gains = {e: g[S | 1 << e] - g[S] for e in range(n) if not S >> e & 1}
            best = max(gains.values())
            for e, val in gains.items():
                if val >= best - tol * max(1.0, abs(best)):
                    nxt.add(S | 1 << e)
        frontier = sorted(nxt)
    return frontier


def pe1_value(n, K, f, g, tol=1e-9):
    """Adversarial worst value of PE_1 on the instance (f, g), and diagnostics."""
    per_start = {}
    for v in range(n):
        Ts = all_trajectories(n, K, g, 1 << v, tol)
        per_start[v] = Ts
    min_pred = {v: min(g[T] for T in per_start[v]) for v in range(n)}
    best_val, best_info = np.inf, None
    for vstar in range(n):
        for T in per_start[vstar]:
            ok = all(min_pred[v] <= g[T] + tol * max(1.0, abs(g[T]))
                     for v in range(n) if v != vstar)
            if ok and f[T] < best_val:
                best_val, best_info = f[T], (vstar, T)
    OPT = max(f[S] for S in range(1 << n) if bin(S).count("1") <= K)
    return best_val / OPT, best_info, OPT, per_start


def greedy_value(n, K, f, g, tol=1e-9):
    """Adversarial worst value of plain predictive greedy (start from empty)."""
    Ts = all_trajectories(n, K, g, 0, tol)
    OPT = max(f[S] for S in range(1 << n) if bin(S).count("1") <= K)
    val = min(f[T] for T in Ts)
    return val / OPT


# ---------------------------------------------------------------------------
# Part 1: PE_1 on the known rho_K-attaining instance families
# ---------------------------------------------------------------------------
def n2_instance(K, j, eta, capped=True):
    """The three-block family of results/N2_check.py (symmetric split
    eta_u = eta_o = sqrt(eta)); returns arrays f, g on 2^{2K}."""
    s = eta ** 0.5
    eu = eo = s
    k1 = (K - 1) * eta + 1
    q = (K - 1) * eta / k1
    qj = q ** j
    delta = qj / (K * eta)
    dtil = eo * delta
    W0 = k1 / (K * eu)
    W = lambda y: W0 if y == 0 else (K - y) * eo / K

    def F(x, z, y):
        v = 1 - q ** x * (K - y) / K
        if y < K or not capped:
            v += z * delta
        return v

    def Gf(x, z, y):
        v = W0 - q ** x * W(y)
        if y < K or not capped:
            v += z * dtil
        return v

    n = 2 * K
    N = 1 << n
    # 0..j-1 = C, j..K-1 = P, K..2K-1 = O
    f = np.zeros(N)
    g = np.zeros(N)
    for S in range(N):
        x = bin(S & ((1 << j) - 1)).count("1")
        z = bin((S >> j) & ((1 << (K - j)) - 1)).count("1")
        y = bin(S >> K).count("1")
        f[S] = F(x, z, y)
        g[S] = Gf(x, z, y)
    return f, g, n


def uk_instance(K, ahat):
    """The U_K family of code/check_explicit_instance.py."""
    a = 1 - 1 / (ahat * K)
    F = lambda x, y: 1 - a ** x * (1 - y / K)
    Gf = lambda x, y: (1 - a ** x) if y == 0 else \
        1 - a ** x + a ** x * ((1 - a) + (y - 1) * a / (K - 1))
    n = 2 * K
    N = 1 << n
    f = np.zeros(N)
    g = np.zeros(N)
    for S in range(N):
        x = bin(S & ((1 << K) - 1)).count("1")
        y = bin(S >> K).count("1")
        f[S] = F(x, y)
        g[S] = Gf(x, y)
    return f, g, n


def part_instances(K=3, etas=ETAS):
    print("=" * 78)
    print("Part 1: PE_1 on the known rho_K-attaining instances (adversarial ties)")
    print("=" * 78)
    out = []
    for eta in etas:
        for j in range(K + 1):
            f, g, n = n2_instance(K, j, eta)
            pv, info, OPT, _ = pe1_value(n, K, f, g)
            gv = greedy_value(n, K, f, g)
            row = dict(family=f"N2_j{j}", K=K, eta=eta, n=n,
                       greedy_ratio=gv, pe1_ratio=pv, Vj=Vj(K, j, eta),
                       rho=rho(K, eta),
                       pe1_start=None if info is None else info[0],
                       pe1_set=None if info is None else
                       [i for i in range(n) if info[1] >> i & 1])
            out.append(row)
            print(f"  eta={eta}  N2 j={j}: greedy={gv:.6f} (V_j={Vj(K,j,eta):.6f})  "
                  f"PE_1={pv:.6f}  out={row['pe1_set']}")
        f, g, n = uk_instance(K, eta)
        pv, info, OPT, _ = pe1_value(n, K, f, g)
        gv = greedy_value(n, K, f, g)
        out.append(dict(family="U_K", K=K, eta=eta, n=n, greedy_ratio=gv,
                        pe1_ratio=pv, Vj=None, rho=rho(K, eta)))
        print(f"  eta={eta}  U_K(ahat=eta): greedy={gv:.6f} (L_K={LK(K,eta):.6f})  "
              f"PE_1={pv:.6f}")
    print()
    for eta in etas:
        best = min(r["pe1_ratio"] for r in out if r["eta"] == eta)
        print(f"  eta={eta}: min PE_1 over the known families = {best:.6f}   "
              f"rho_3 = {rho(K, eta):.6f}   -> "
              f"{'PE_1 already at/below rho_3' if best <= rho(K, eta) + 1e-9 else 'known families do NOT defeat PE_1'}")
    return out


# ---------------------------------------------------------------------------
# Part 2: self-check -- reproduce rho_3 with the same row builder
# ---------------------------------------------------------------------------
def part_selfcheck(ns=(6, 7, 8), K=3, etas=ETAS):
    """Gate: the same row builder must reproduce rho_K for PLAIN predictive
    greedy, at every n.  This is what makes the PE_1 vs greedy comparison at
    n = 7, 8 meaningful: greedy's worst case does not move with n, PE_1's does."""
    print("=" * 78)
    print("Part 2: self-check, plain greedy LP with the same row builder")
    print("=" * 78)
    out = []
    for n in ns:
        for eta in etas:
            eu = eo = eta ** 0.5
            B = LPBuilder(n, eu, eo)
            N = B.N
            picks_rows = traj_rows(n, N, 0, tuple(range(1, K)))
            # plain greedy also constrains the FIRST pick from the empty set
            first = [{N + (1 << e): 1.0, N + 1: -1.0} for e in range(1, n)]
            Os = (itertools.combinations(range(n), K) if n <= 6
                  else O_representatives(n, K))
            best = min(B.solve(picks_rows + first, sum(1 << i for i in O), 0b111)
                       for O in Os)
            print(f"  n={n} eta={eta}: full-lattice greedy LP = {best:.9f}   "
                  f"rho_{K} = {rho(K, eta):.9f}   diff = {best - rho(K, eta):+.2e}",
                  flush=True)
            out.append(dict(n=n, eta=eta, lp=best, rho=rho(K, eta)))
    return out


# ---------------------------------------------------------------------------
# Part 3: profile-free relaxation lower bound
# ---------------------------------------------------------------------------
def relaxation_lb(n, K, eta, err_model="single", eu=None, eo=None, verbose=True):
    """Lower bound on PE_1's worst case: v* = 0 and T_0 = {0,1,2} by relabelling,
    trajectory rows for start 0, profile-free rows for every other start."""
    if eu is None:
        eu = eo = eta ** 0.5
    B = LPBuilder(n, eu, eo, err_model)
    N = B.N
    Tstar = (1 << K) - 1
    rows = traj_rows(n, N, 0, tuple(range(1, K)))
    for v in range(1, n):
        rows += relax_rows(n, N, v, Tstar)
    best, bestO = np.inf, None
    for O in itertools.combinations(range(n), K):
        Om = sum(1 << i for i in O)
        val = B.solve(rows, Om, Tstar)
        if val < best:
            best, bestO = val, O
    if verbose:
        print(f"  n={n} eta={eta}: relaxation LB = {best:.6f} (argmin O={bestO})  "
              f"rho_{K} = {rho(K, eta):.6f}")
    return best, bestO, B


def part_lb(ns=(6,), K=3, etas=ETAS):
    print("=" * 78)
    print("Part 3: profile-free relaxation lower bound on PE_1")
    print("=" * 78)
    out = []
    for n in ns:
        for eta in etas:
            t0 = time.time()
            lb, O, _ = relaxation_lb(n, K, eta)
            out.append(dict(n=n, K=K, eta=eta, lb=lb, O=list(O),
                            rho=rho(K, eta), secs=time.time() - t0))
            print(f"     ({time.time()-t0:.1f}s)")
    return out


# ---------------------------------------------------------------------------
# Part 4: exact branch and bound
# ---------------------------------------------------------------------------
# Collapse of the last greedy step (used to shrink the profile space).
#
#   For a start v whose first pick is a, the adversary still has to choose the
#   second pick b.  The requirement is
#        exists b :  b in argmax_e dtilde_e({v,a})   AND   ftilde(T_0) >= ftilde({v,a,b}).
#   Since argmax_e dtilde_e({v,a}) = argmax_e ftilde({v,a,e}) (the ftilde({v,a})
#   term is common), the strongest such b is the argmax itself, so the condition
#   is EQUIVALENT to the b-free linear system
#        ftilde(T_0) >= ftilde({v,a,e})    for every e not in {v,a}.
#   Hence only the FIRST pick of each start has to be branched on: for K = 3 the
#   profile space drops from (n-1)(n-2) to (n-1) choices per start.
#   [VERIFIED-LP: the exhaustive n=6 cross-check `bnbfull` re-runs the search
#    with both picks branched and reproduces the same optimum.]
def last_step_rows(n, N, v, a, Tstar_mask):
    G = lambda S: N + S
    S = (1 << v) | (1 << a)
    return [{G(S | 1 << e): 1.0, G(Tstar_mask): -1.0}
            for e in range(n) if not S >> e & 1]


def first_step_rows(n, N, v, a):
    G = lambda S: N + S
    return [{G((1 << v) | (1 << e)): 1.0, G((1 << v) | (1 << a)): -1.0}
            for e in range(n) if e != v and e != a]


def O_representatives(n, K):
    """One representative per orbit of K-subsets under Sym({K,...,n-1}), the
    residual symmetry after fixing v* = 0 and T_0 = {0,...,K-1} in this order.
    Valid because min over profiles is constant on orbits: relabelling by a
    permutation sigma fixing 0..K-1 maps the profile set bijectively to itself
    and LP(sigma O, sigma . profile) = LP(O, profile)."""
    reps = []
    for inside in itertools.chain.from_iterable(
            itertools.combinations(range(K), r) for r in range(K + 1)):
        r = K - len(inside)
        if 0 <= r <= n - K:
            reps.append(tuple(inside) + tuple(range(K, K + r)))
    return reps


def bnb(n, K, eta, err_model="single", eu=None, eo=None, ub_init=None,
        verbose=True, time_limit=None, branch_both=False, sym_O=False):
    """Exact min over choice profiles.  v* = 0 and T_0 = {0,...,K-1} (greedy
    order 0 -> 1 -> ... -> K-1) are fixed by relabelling; O ranges over all
    K-subsets; the first pick of every other start is branched on."""
    assert K == 3, "the last-step collapse below is written for K = 3"
    if eu is None:
        eu = eo = eta ** 0.5
    B = LPBuilder(n, eu, eo, err_model)
    N = B.N
    Tstar = (1 << K) - 1
    base_traj = traj_rows(n, N, 0, tuple(range(1, K)))

    stats = dict(nodes=0, leaves=0, pruned=0, lp=0, lp_secs=0.0)
    t_start = time.time()
    best = dict(val=np.inf if ub_init is None else ub_init, profile=None, O=None)

    def rows_for(assigned, nxt):
        rows = list(base_traj)
        for v, a in assigned.items():
            if branch_both:
                rows += traj_rows(n, N, v, a)
                Tv = (1 << v) | (1 << a[0]) | (1 << a[1])
                r = sel_row(N, Tv, Tstar)
                if r is not None:
                    rows.append(r)
            else:
                rows += first_step_rows(n, N, v, a)
                rows += last_step_rows(n, N, v, a, Tstar)
        for v in range(nxt, n):
            rows += relax_rows(n, N, v, Tstar)
        return rows

    def solve(assigned, nxt, O_mask):
        stats["lp"] += 1
        t0 = time.time()
        val = B.solve(rows_for(assigned, nxt), O_mask, Tstar)
        stats["lp_secs"] += time.time() - t0
        return val

    if branch_both:
        choices = [p for p in itertools.permutations(range(n), K - 1)]
        legal = lambda v, c: v not in c
    else:
        choices = list(range(n))
        legal = lambda v, c: c != v

    def rec(O_mask, assigned, v):
        if time_limit is not None and time.time() - t_start > time_limit:
            raise TimeoutError
        stats["nodes"] += 1
        if v == n:
            stats["leaves"] += 1
            return
        kids = []
        for c in choices:
            if not legal(v, c):
                continue
            val = solve({**assigned, v: c}, v + 1, O_mask)
            if val < best["val"] - 1e-9:
                kids.append((val, c))
        kids.sort()
        for val, c in kids:
            if val >= best["val"] - 1e-9:      # incumbent improved meanwhile
                stats["pruned"] += 1
                continue
            if v + 1 == n:
                best["val"] = val
                best["profile"] = {**assigned, v: c}
                best["O"] = O_mask
                if verbose:
                    print(f"      incumbent {val:.6f}  O={O_mask:06b}  "
                          f"a={ {**assigned, v: c} }", flush=True)
            else:
                rec(O_mask, {**assigned, v: c}, v + 1)

    for O in O_representatives(n, K) if sym_O else itertools.combinations(range(n), K):
        Om = sum(1 << i for i in O)
        root = solve({}, 1, Om)
        if root >= best["val"] - 1e-9:
            stats["pruned"] += 1
            continue
        try:
            rec(Om, {}, 1)
        except TimeoutError:
            return best, stats, "TIMEOUT"
    return best, stats, "OK"


# ---------------------------------------------------------------------------
# Part 5: certificate check -- rebuild the LP optimum as an explicit instance
# ---------------------------------------------------------------------------
def check_certificate(n, K, eta, profile, O_mask, eu=None, eo=None,
                      err_model="single", tol=1e-7, verbose=True):
    """Re-solve the winning profile's LP, extract (f, ftilde), verify the model
    constraints directly on the 2^n lattice and re-run PE_1 with adversarial
    ties on the extracted instance."""
    if eu is None:
        eu = eo = eta ** 0.5
    B = LPBuilder(n, eu, eo, err_model)
    N = B.N
    Tstar = (1 << K) - 1
    rows = traj_rows(n, N, 0, tuple(range(1, K)))
    for v, a in profile.items():
        v = int(v)
        rows += first_step_rows(n, N, v, a) + last_step_rows(n, N, v, a, Tstar)
    val, x = B.solve(rows, O_mask, Tstar, want_x=True)
    f, g = x[:N].copy(), x[N:].copy()
    f -= f[0]
    g -= g[0]
    rep = dict(lp_value=val)
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
    rep.update(monotone=mono, submodular=submod, band=band)
    ratio, info, OPT, _ = pe1_value(n, K, f, g, tol=1e-7)
    rep.update(pe1_ratio_on_instance=ratio, OPT=OPT,
               greedy_ratio_on_instance=greedy_value(n, K, f, g, tol=1e-7))
    rep["consistent"] = (mono and submod and band
                         and abs(ratio - val) < 1e-6)
    if verbose:
        print(f"    certificate n={n} eta={eta}: LP={val:.9f}  "
              f"PE_1 on instance={ratio:.9f}  monotone={mono} submodular={submod} "
              f"band={band}  -> {'CONSISTENT' if rep['consistent'] else 'MISMATCH'}")
    return rep, f, g


def rationalize(x, maxden=2000):
    fr = Fr(x).limit_denominator(maxden)
    return fr if abs(float(fr) - x) < 1e-9 else None


def pe1_closed_form_n6(eta):
    """[CONJECTURE] closed form of PE_1's worst case at n = 6 = 2K, K = 3:
    min{1/eta, (9 eta - 4)/(2(3 eta^2 + eta - 1))}, switching at eta = 1 + 1/sqrt 3.
    Fitted on 5 points and confirmed on 10 further grid points (mode `sweep`)."""
    return min(1 / eta, (9 * eta - 4) / (2 * (3 * eta * eta + eta - 1)))


def part_main(ns=(6, 7), K=3, etas=ETAS, sym_O=True):
    """The deliverable table: exact PE_1 worst case at n = 6 and n = 7 plus the
    explicit-instance certificate for every entry."""
    print("=" * 78)
    print("Part 4: exact PE_1 worst case (branch and bound) + certificates")
    print("=" * 78)
    res = []
    for n in ns:
        for eta in etas:
            t0 = time.time()
            best, stats, status = bnb(n, K, eta, verbose=False, sym_O=sym_O,
                                      time_limit=3000)
            dt = time.time() - t0
            fr = rationalize(best["val"])
            print(f"  n={n} eta={eta}: PE_1 = {best['val']:.9f} ({fr})  "
                  f"status={status}  rho_{K} = {rho(K, eta):.9f}  "
                  f"1/eta = {1/eta:.9f}  LPs={stats['lp']}  ({dt:.0f}s)", flush=True)
            cert = None
            if best["profile"]:
                cert, _, _ = check_certificate(n, K, eta, best["profile"],
                                               best["O"])
            res.append(dict(n=n, K=K, eta=eta, val=best["val"], frac=str(fr),
                            status=status, rho=rho(K, eta), inv_eta=1 / eta,
                            beats_greedy=best["val"] > rho(K, eta) + 1e-9,
                            gap_vs_rho=best["val"] - rho(K, eta),
                            profile={str(k): v for k, v in
                                     (best["profile"] or {}).items()},
                            O=best["O"], lps=stats["lp"], secs=dt,
                            certificate=cert))
    return res


def part_sweep(n=6, K=3, sym_O=True):
    print("=" * 78)
    print("Part 5: eta sweep at n = 6 and the closed-form conjecture")
    print("=" * 78)
    res = []
    for eta in [1.0, 1.1, 1.2, 1.25, 1.4, 1.5, 1.6, 1.75, 1.9, 2.0, 2.1, 2.25,
                2.5, 3.0, 4.0]:
        t0 = time.time()
        best, stats, status = bnb(n, K, eta, verbose=False, sym_O=sym_O,
                                  time_limit=1200)
        cf = pe1_closed_form_n6(eta)
        ok = abs(best["val"] - cf) < 1e-9
        print(f"  eta={eta:<5}: PE_1 = {best['val']:.9f} ({rationalize(best['val'])})"
              f"   closed form = {cf:.9f}   match={ok}   ({time.time()-t0:.0f}s)",
              flush=True)
        res.append(dict(eta=eta, val=best["val"], frac=str(rationalize(best["val"])),
                        closed_form=cf, match=ok, status=status))
    print(f"  closed form matched {sum(r['match'] for r in res)}/{len(res)} points")
    return res


def part_split(n=6, K=3):
    """Sanity check for the T0 scaling reduction: replacing (eta_u, eta_o) by
    (eta_u/c, c eta_o) multiplies ftilde by c, which changes no argmax and no
    comparison of ftilde(T_v), so the worst case depends on the product only."""
    print("=" * 78)
    print("Part 6: eta_u / eta_o split does not matter (product only)")
    print("=" * 78)
    res = []
    for eu, eo in [(1.0, 2.0), (2.0, 1.0), (2.0 ** 0.5, 2.0 ** 0.5), (4.0, 0.5)]:
        if eo < 1.0:
            continue
        best, stats, status = bnb(n, K, eu * eo, eu=eu, eo=eo, verbose=False,
                                  sym_O=True, time_limit=600)
        print(f"  (eta_u,eta_o)=({eu:.4f},{eo:.4f}) product={eu*eo:.4f}: "
              f"PE_1 = {best['val']:.9f} ({rationalize(best['val'])})  {status}")
        res.append(dict(eta_u=eu, eta_o=eo, val=best["val"], status=status))
    return res


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    path = os.path.join(HERE, "H_F_partial_enumeration.json")
    log = {}
    if os.path.exists(path):
        try:
            log = json.load(open(path))
        except Exception:
            log = {}
    if mode in ("instances", "all"):
        log["instances"] = part_instances()
    if mode in ("selfcheck", "all"):
        log["selfcheck"] = part_selfcheck()
    if mode in ("lb", "all"):
        log["lb"] = part_lb()
    if mode in ("main", "all"):
        log["main"] = part_main()
    if mode in ("sweep", "all"):
        log["sweep"] = part_sweep()
    if mode in ("split", "all"):
        log["split"] = part_split()
    if mode == "n8":
        log["n8"] = part_main(ns=(8,))
    if mode == "n7sweep":
        # where does PE_1(n=7) cross below rho_3?
        out = []
        for eta in [1.0, 1.25, 1.5, 1.75, 2.0, 2.5]:
            t0 = time.time()
            best, stats, status = bnb(7, 3, eta, verbose=False, sym_O=True,
                                      time_limit=1800)
            print(f"  n=7 eta={eta}: PE_1 = {best['val']:.9f} "
                  f"({rationalize(best['val'])})  rho_3 = {rho(3, eta):.9f}  "
                  f"beats_greedy={best['val'] > rho(3, eta) + 1e-9}  {status}  "
                  f"({time.time()-t0:.0f}s)", flush=True)
            out.append(dict(n=7, eta=eta, val=best["val"],
                            frac=str(rationalize(best["val"])),
                            rho=rho(3, eta), status=status,
                            beats_greedy=best["val"] > rho(3, eta) + 1e-9))
        log["n7sweep"] = out
    if mode == "crosscheck":
        # exhaustive re-run with BOTH greedy picks branched (validates the
        # last-step collapse); seeded just above the collapsed-search optimum
        seeds = {1.5: 0.6551724137931034, 2.0: 0.5, 2.5: 0.4}
        out = []
        for eta in ETAS:
            t0 = time.time()
            best, stats, status = bnb(6, 3, eta, verbose=False, branch_both=True,
                                      ub_init=seeds[eta] + 1e-6, time_limit=1800)
            print(f"  eta={eta} branch_both: best={best['val']:.9f} "
                  f"(seed {seeds[eta]:.9f}) status={status} LPs={stats['lp']} "
                  f"({time.time()-t0:.0f}s)", flush=True)
            out.append(dict(eta=eta, val=best["val"], seed=seeds[eta],
                            status=status, lps=stats["lp"]))
        log["crosscheck_branch_both"] = out
    with open(path, "w") as fh:
        json.dump(log, fh, indent=1, default=str)
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
