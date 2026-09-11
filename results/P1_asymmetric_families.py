"""P1 (TASKS9) -- asymmetric hardness-construction families for ARBITRARY-SIZE queries.

Two candidate families are tested against the same count-grid LP skeleton that
results/N4_relaxF_solve.py uses for the (x,y)-symmetric family:

  (a) block hiding      : O is split into g blocks O_1..O_g (sizes `blocks`),
                          N\\O is one background block.  F and G are counting
                          functions of (x, y_1, ..., y_g); symmetry only inside a
                          block.  g = 1 recovers the (x,y) family exactly.
  (b) non-saturating F  : F(x,y) = 1 - a^x(1 - y/K) + phi(x) psi(y) with psi a
                          FIXED shape and phi free (the product phi*psi with both
                          free is bilinear, not an LP; see the report, section 3).

The O-free region ("band") on which the predictor must be a function of |S| only
is computed EXACTLY from the (multivariate) hypergeometric law of the count
vector of a fixed query of size s under a uniformly random hidden O:

    typical(s) = smallest set of count vectors, built greedily in decreasing
                 probability, whose complement has mass <= 1/(4Q).

Constraints (identical in form to lem:app-count of paper/sections/appendix_proofs.tex,
which is already stated for a partition into r parts, so it applies verbatim to
the block family):
    mono      : Delta_i F >= 0 for every direction i
    submod    : Delta_l Delta_i F <= 0 for every ordered pair (i,l), i = l included
    opt_norm  : F <= 1 on 0 < |S| <= K
    eq        : F(0) = 0, F(O) = 1, Ghat(0) = 0
    band      : Delta F / eta_u <= Delta G <= eta_o Delta F on every edge
    O-free    : G(state) = Ghat(|S|) for every state in the region
objective   : min F(K, 0)   (value of the best K-set the algorithm can return
                             when it misses O entirely)

Usage:  python3 results/P1_asymmetric_families.py            # full run (~ minutes)
        python3 results/P1_asymmetric_families.py --quick    # section 1 + 2 only
Writes: results/P1_asymmetric_families.json
"""
import itertools
import json
import math
import os
import sys
import time
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
TOL = 1e-7


# --------------------------------------------------------------------------
# 0.  closed-form constants of the N4 / F3 family (used only to place t*)
# --------------------------------------------------------------------------
def n4_constants(K, eta):
    k1 = eta * (K - 1) + 1
    q = 1.0 - 1.0 / k1
    j = min(K, max(0, K + 1 - math.ceil(eta - 1e-12)))
    mstar = math.ceil(eta * K - 1e-12) - 1
    tstar = j + mstar
    return dict(k1=k1, q=q, j=j, mstar=mstar, tstar=tstar)


# --------------------------------------------------------------------------
# 1.  states and exact typical sets
# --------------------------------------------------------------------------
def enumerate_y(blocks):
    return [tuple(v) for v in itertools.product(*[range(p + 1) for p in blocks])]


def states_of(n, K, blocks):
    X = n - K
    ys = enumerate_y(blocks)
    return [(x,) + y for x in range(X + 1) for y in ys]


def hyper_probs(n, K, blocks, s):
    """Exact multivariate-hypergeometric law of (y_1..y_g) for a fixed query of
    size s under a uniformly random labelled partition (O_1..O_g) of a random
    K-subset.  Returns {y-vector: Fraction}."""
    X = n - K
    tot = math.comb(n, s)
    out = {}
    for y in enumerate_y(blocks):
        sy = sum(y)
        x = s - sy
        if x < 0 or x > X:
            continue
        w = math.comb(X, x)
        for p, yi in zip(blocks, y):
            w *= math.comb(p, yi)
        if w:
            out[y] = Fraction(w, tot)
    return out


def typical_set(n, K, blocks, s, thr):
    """Smallest set of count vectors with tail mass <= thr, greedy by probability."""
    pr = hyper_probs(n, K, blocks, s)
    order = sorted(pr.items(), key=lambda kv: (-kv[1], kv[0]))
    acc = Fraction(0)
    keep = set()
    need = Fraction(1) - Fraction(thr).limit_denominator(10 ** 15)
    for y, p in order:
        if acc >= need:
            break
        keep.add(y)
        acc += p
    return keep


def necessary_set(n, K, blocks, s, thr):
    """{y : Pr[y | |S| = s] > thr}.  EVERY region whose complement has mass <= thr
    contains this set, so the LP built on it is a lower bound on the constant that
    ANY size-based O-free region can certify at this query budget."""
    pr = hyper_probs(n, K, blocks, s)
    t = Fraction(thr).limit_denominator(10 ** 15)
    return {y for y, p in pr.items() if p > t}


def region_map(n, K, blocks, kind, thr=None, tstar=None, tau=None):
    """s -> set of y-vectors on which G is required to equal Ghat(s)."""
    X = n - K
    ys = enumerate_y(blocks)
    reg = {}
    for s in range(n + 1):
        live = {y for y in ys if 0 <= s - sum(y) <= X}
        if kind == 'typ':
            reg[s] = typical_set(n, K, blocks, s, thr)
        elif kind == 'typmin':
            reg[s] = necessary_set(n, K, blocks, s, thr)
        elif kind == 'f3':                      # {sum y <= 1} union {x > t*}
            reg[s] = {y for y in live if sum(y) <= 1 or s - sum(y) > tstar}
        elif kind == 'ysmall':                  # {sum y <= tau}
            reg[s] = {y for y in live if sum(y) <= tau}
        elif kind == 'twosided':                # ||S cap O| - K|S|/n| <= tau
            reg[s] = {y for y in live if abs(sum(y) - K * s / n) <= tau + 1e-12}
        else:
            raise ValueError(kind)
    return reg


# --------------------------------------------------------------------------
# 2.  generic count-grid LP
# --------------------------------------------------------------------------
class Model:
    """F(state) is an affine expression in the decision variables, so the same
    builder serves the free-F families (a) and the structured family (b)."""

    def __init__(self, n, K, blocks, eta, reg, Fexpr, nvar_F, split='sqrt',
                 obj_state=None):
        self.n, self.K, self.blocks, self.eta = n, K, blocks, eta
        self.X = n - K
        self.eta_u, self.eta_o = ((eta ** 0.5,) * 2) if split == 'sqrt' else (eta, 1.0)
        self.states = states_of(n, K, blocks)
        self.sidx = {s: i for i, s in enumerate(self.states)}
        self.reg = reg
        self.Fexpr = Fexpr                 # state -> (const, [(var, coef), ...])
        self.ndir = 1 + len(blocks)
        self.caps = (self.X,) + tuple(blocks)
        # variable layout: [F-block | Ghat(0..n) | G(unbalanced states)]
        self.gh0 = nvar_F
        self.unbal = [st for st in self.states
                      if st[1:] not in self.reg[sum(st)]]
        self.gvid = {st: self.gh0 + n + 1 + i for i, st in enumerate(self.unbal)}
        self.nv = self.gh0 + n + 1 + len(self.unbal)
        self.obj_state = obj_state
        self._build()

    def gref(self, st):
        return self.gh0 + sum(st) if st[1:] in self.reg[sum(st)] else self.gvid[st]

    def _nb(self, st, d):
        t = list(st)
        t[d] += 1
        if t[d] > self.caps[d]:
            return None
        return tuple(t)

    def _addF(self, coefs, const, expr_state, mult):
        c, terms = self.Fexpr(expr_state)
        const[0] += mult * c
        for v, w in terms:
            coefs[v] = coefs.get(v, 0.0) + mult * w

    def _row(self, Fterms, Gterms, rhs, tag):
        coefs, const = {}, [0.0]
        for st, m in Fterms:
            self._addF(coefs, const, st, m)
        for v, m in Gterms:
            coefs[v] = coefs.get(v, 0.0) + m
        for v, w in coefs.items():
            if abs(w) > 1e-14:
                self.R.append(self.nrows)
                self.C.append(v)
                self.V.append(w)
        self.b.append(rhs - const[0])
        self.meta.append(tag)
        self.nrows += 1

    def _build(self):
        self.R, self.C, self.V, self.b, self.meta, self.nrows = [], [], [], [], [], 0
        eu, eo = self.eta_u, self.eta_o
        edges = []
        for st in self.states:
            for d in range(self.ndir):
                t = self._nb(st, d)
                if t is not None:
                    edges.append((st, t, d))
        self.edges = edges
        for p, q, d in edges:
            self._row([(p, 1.0), (q, -1.0)], [], 0.0, ('mono', p, d))
            gq, gp = self.gref(q), self.gref(p)
            self._row([(q, -eo), (p, eo)], [(gq, 1.0), (gp, -1.0)], 0.0, ('band_up', p, d))
            self._row([(q, 1.0 / eu), (p, -1.0 / eu)], [(gq, -1.0), (gp, 1.0)], 0.0,
                      ('band_lo', p, d))
        for p, q, d in edges:
            for sh in range(self.ndir):
                px, qx = self._nb(p, sh), self._nb(q, sh)
                if px is None or qx is None:
                    continue
                self._row([(qx, 1.0), (px, -1.0), (q, -1.0), (p, 1.0)], [], 0.0,
                          ('submod', p, (d, sh)))
        O = (0,) + tuple(self.blocks)
        for st in self.states:
            s = sum(st)
            if 0 < s <= self.K and st != O:
                self._row([(st, 1.0)], [], 1.0, ('opt_norm', st, ''))
        # equalities
        self.eqR, self.eqC, self.eqV, self.eqb, self.eqmeta = [], [], [], [], []
        self.neq = 0
        self._eq([( (0,) + (0,) * len(self.blocks), 1.0)], [], 0.0, ('eq_zero',))
        self._eq([(O, 1.0)], [], 1.0, ('eq_opt',))
        self._eq([], [(self.gh0, 1.0)], 0.0, ('eq_g0',))

    def _eq(self, Fterms, Gterms, rhs, tag):
        coefs, const = {}, [0.0]
        for st, m in Fterms:
            self._addF(coefs, const, st, m)
        for v, m in Gterms:
            coefs[v] = coefs.get(v, 0.0) + m
        for v, w in coefs.items():
            if abs(w) > 1e-14:
                self.eqR.append(self.neq)
                self.eqC.append(v)
                self.eqV.append(w)
        self.eqb.append(rhs - const[0])
        self.eqmeta.append(tag)
        self.neq += 1

    # ---- solving -------------------------------------------------------
    def matrices(self, rows=None):
        if rows is None:
            A = coo_matrix((self.V, (self.R, self.C)), shape=(self.nrows, self.nv)).tocsr()
            return A, np.array(self.b)
        keep = np.zeros(self.nrows, bool)
        keep[list(rows)] = True
        remap = -np.ones(self.nrows, int)
        remap[keep] = np.arange(keep.sum())
        R2, C2, V2 = [], [], []
        for r, c, v in zip(self.R, self.C, self.V):
            if keep[r]:
                R2.append(remap[r]); C2.append(c); V2.append(v)
        A = coo_matrix((V2, (R2, C2)), shape=(int(keep.sum()), self.nv)).tocsr()
        return A, np.array(self.b)[keep]

    def _eqmat(self):
        return (coo_matrix((self.eqV, (self.eqR, self.eqC)), shape=(self.neq, self.nv)).tocsr(),
                np.array(self.eqb))

    def objective(self):
        obj = np.zeros(self.nv)
        c, terms = self.Fexpr(self.obj_state)
        for v, w in terms:
            obj[v] += w
        return obj, c

    def solve(self):
        A, b = self.matrices()
        Aeq, beq = self._eqmat()
        obj, c0 = self.objective()
        out = linprog(obj, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq,
                      bounds=[(None, None)] * self.nv, method='highs')
        if out.status != 0:
            return dict(status=out.status, message=out.message, value=None)
        return dict(status=0, value=float(out.fun + c0), x=out.x)

    def elastic(self, rows=None):
        """min t s.t. A x <= b + t, equalities hard, t >= 0.  t* > tol certifies
        infeasibility of the row subset with a margin."""
        A, b = self.matrices(rows)
        Aeq, beq = self._eqmat()
        m = A.shape[0]
        A2 = coo_matrix((list(A.tocoo().data) + [-1.0] * m,
                         (list(A.tocoo().row) + list(range(m)),
                          list(A.tocoo().col) + [self.nv] * m)),
                        shape=(m, self.nv + 1)).tocsr()
        Aeq2 = coo_matrix((list(Aeq.tocoo().data),
                           (list(Aeq.tocoo().row), list(Aeq.tocoo().col))),
                          shape=(self.neq, self.nv + 1)).tocsr()
        obj = np.zeros(self.nv + 1)
        obj[self.nv] = 1.0
        out = linprog(obj, A_ub=A2, b_ub=b, A_eq=Aeq2, b_eq=beq,
                      bounds=[(None, None)] * self.nv + [(0, None)], method='highs')
        if out.status != 0:
            return None
        return float(out.fun)

    def feasible(self, rows=None):
        t = self.elastic(rows)
        return (t is not None) and (t <= 1e-9)

    # ---- reading a solution back ---------------------------------------
    def read(self, x):
        F, G = {}, {}
        for st in self.states:
            c, terms = self.Fexpr(st)
            F[st] = c + sum(x[v] * w for v, w in terms)
            G[st] = x[self.gref(st)]
        Ghat = x[self.gh0:self.gh0 + self.n + 1]
        return F, G, Ghat


# --------------------------------------------------------------------------
# 3.  IIS: deletion filter, groups first then rows
# --------------------------------------------------------------------------
def group_key(tag):
    if tag[0] == 'submod':
        return ('submod', tag[2])
    if tag[0] in ('band_up', 'band_lo', 'mono'):
        return (tag[0], tag[2])
    return (tag[0],)


def iis(model, budget_s=600):
    t0 = time.time()
    alive = set(range(model.nrows))
    if model.feasible(alive):
        return None
    groups = {}
    for i, tag in enumerate(model.meta):
        groups.setdefault(group_key(tag), []).append(i)
    # group level
    for g in sorted(groups, key=lambda k: -len(groups[k])):
        if time.time() - t0 > budget_s:
            break
        cand = alive - set(groups[g])
        if not model.feasible(cand):
            alive = cand
    # row level, chunked then singleton
    for chunk in (64, 16, 4, 1):
        changed = True
        while changed and time.time() - t0 < budget_s:
            changed = False
            rows = sorted(alive)
            for k in range(0, len(rows), chunk):
                if time.time() - t0 > budget_s:
                    break
                blk = set(rows[k:k + chunk])
                if not blk <= alive:
                    continue
                cand = alive - blk
                if not model.feasible(cand):
                    alive = cand
                    changed = True
    return sorted(alive), (time.time() - t0)


def describe_rows(model, rows):
    out = []
    for i in rows:
        tag = model.meta[i]
        out.append(dict(tag=tag[0], state=list(tag[1]) if len(tag) > 1 else None,
                        dirn=str(tag[2]) if len(tag) > 2 else None))
    return out


# --------------------------------------------------------------------------
# 4.  leakage checks (J5 N\{e} and all (n-2)-set identity classes)
# --------------------------------------------------------------------------
def leak_classes(n, K, blocks):
    """Count-vector classes of N\\{e} and N\\{e,f} by the identity of the removed
    elements.  Returns list of (label, state)."""
    X = n - K
    full = tuple(blocks)
    out1, out2 = [], []
    out1.append(('e in background', (X - 1,) + full))
    for i, p in enumerate(blocks):
        y = list(full); y[i] -= 1
        out1.append((f'e in block {i+1}', (X,) + tuple(y)))
    out2.append(('both background', (X - 2,) + full))
    for i, p in enumerate(blocks):
        y = list(full); y[i] -= 1
        out2.append((f'one bg + one in block {i+1}', (X - 1,) + tuple(y)))
        if p >= 2:
            y2 = list(full); y2[i] -= 2
            out2.append((f'two in block {i+1}', (X,) + tuple(y2)))
    for i in range(len(blocks)):
        for jj in range(i + 1, len(blocks)):
            y = list(full); y[i] -= 1; y[jj] -= 1
            out2.append((f'one in block {i+1} + one in block {jj+1}', (X,) + tuple(y)))
    return out1, out2


def leak_check(model, G):
    c1, c2 = leak_classes(model.n, model.K, model.blocks)
    rep = {}
    for name, classes in (('N_minus_e', c1), ('N_minus_2', c2)):
        vals, inreg = [], []
        for lab, st in classes:
            if st not in model.sidx:
                continue
            vals.append((lab, float(G[st])))
            inreg.append(st[1:] in model.reg[sum(st)])
        spread = (max(v for _, v in vals) - min(v for _, v in vals)) if vals else 0.0
        rep[name] = dict(values=vals, all_in_region=bool(all(inreg)),
                         spread=spread, verdict='PASS' if spread <= 1e-6 else 'LEAK')
    return rep


# --------------------------------------------------------------------------
# 5.  family builders
# --------------------------------------------------------------------------
def free_F_model(n, K, blocks, eta, reg, split='sqrt'):
    sts = states_of(n, K, blocks)
    idx = {s: i for i, s in enumerate(sts)}
    Fexpr = lambda st: (0.0, [(idx[st], 1.0)])
    return Model(n, K, blocks, eta, reg, Fexpr, len(sts), split=split,
                 obj_state=(K,) + (0,) * len(blocks))


PSI = {
    'const1':   lambda y, K: 1.0,
    'linear':   lambda y, K: y / K,
    'top_only': lambda y, K: 1.0 if y == K else 0.0,
    'quad':     lambda y, K: (y / K) ** 2,
}


def structured_F_model(n, K, eta, reg, a, psi_name, split='sqrt'):
    """family (b): F(x,y) = 1 - a^x (1 - y/K) + phi(x) psi(y), psi fixed, phi free."""
    blocks = (K,)
    X = n - K
    psi = PSI[psi_name]

    def Fexpr(st):
        x, y = st[0], st[1]
        base = 1.0 - (a ** x) * (1.0 - y / K)
        w = psi(y, K)
        return (base, [(x, w)] if abs(w) > 1e-14 else [])

    return Model(n, K, blocks, eta, reg, Fexpr, X + 1, split=split,
                 obj_state=(K, 0))


# --------------------------------------------------------------------------
# 6.  experiment drivers
# --------------------------------------------------------------------------
def run_config(name, n, K, blocks, eta, kind, c=2.0, tau=1, want_iis=False,
               iis_budget=420, split='sqrt'):
    cst = n4_constants(K, eta)
    Q = n ** c
    thr = 1.0 / (4.0 * Q)
    reg = region_map(n, K, blocks, kind, thr=thr, tstar=cst['tstar'], tau=tau)
    M = free_F_model(n, K, blocks, eta, reg, split=split)
    t0 = time.time()
    sol = M.solve()
    rec = dict(name=name, family='blocks', n=n, K=K, blocks=list(blocks), eta=eta,
               region=kind, c=c, tau=tau, Q=Q, thr=thr, tstar=cst['tstar'],
               nvar=M.nv, nrow=M.nrows, secs=round(time.time() - t0, 2))
    # region size fingerprint
    rec['region_sizes'] = {str(s): len(reg[s]) for s in (1, 2, K, K + 1, n // 2, n - 2, n - 1, n)
                           if 0 <= s <= n}
    rec['tau_at_K'] = max((sum(y) for y in reg[K]), default=None)
    if sol['status'] == 0:
        rec['status'] = 'FEASIBLE'
        rec['value'] = sol['value']
        F, G, Ghat = M.read(sol['x'])
        rec['leak'] = leak_check(M, G)
        full = (n - K,) + tuple(blocks)
        prev = (n - K - 1,) + tuple(blocks)
        rec['x_marginal_at_full_blocks'] = float(F[full] - F[prev])
        rec['Ghat_increment_at_n'] = float(Ghat[n] - Ghat[n - 1])
        rec['F_full'] = float(F[full])
        rec['F_at_O'] = float(F[(0,) + tuple(blocks)])
    else:
        rec['status'] = 'INFEASIBLE'
        rec['value'] = None
        rec['elastic_margin'] = M.elastic()
        if want_iis:
            got = iis(M, budget_s=iis_budget)
            if got:
                rows, secs = got
                rec['iis_rows'] = len(rows)
                rec['iis'] = describe_rows(M, rows)
                rec['iis_secs'] = round(secs, 1)
                rec['iis_group_counts'] = _counts(M, rows)
    return rec, M


def _counts(M, rows):
    d = {}
    for i in rows:
        k = str(group_key(M.meta[i]))
        d[k] = d.get(k, 0) + 1
    return d


def run_structured(name, n, K, eta, kind, a, psi_name, c=2.0, tau=1,
                   want_iis=False, iis_budget=300):
    cst = n4_constants(K, eta)
    Q = n ** c
    thr = 1.0 / (4.0 * Q)
    reg = region_map(n, K, (K,), kind, thr=thr, tstar=cst['tstar'], tau=tau)
    M = structured_F_model(n, K, eta, reg, a, psi_name)
    t0 = time.time()
    sol = M.solve()
    rec = dict(name=name, family='structured', n=n, K=K, eta=eta, region=kind,
               a=a, psi=psi_name, c=c, tau=tau, thr=thr, tstar=cst['tstar'],
               nvar=M.nv, nrow=M.nrows, secs=round(time.time() - t0, 2))
    if sol['status'] == 0:
        rec['status'] = 'FEASIBLE'
        rec['value'] = sol['value']
        F, G, Ghat = M.read(sol['x'])
        rec['leak'] = leak_check(M, G)
        full = (n - K, K)
        rec['x_marginal_at_full_blocks'] = float(F[full] - F[(n - K - 1, K)])
        rec['phi_K'] = float(sol['x'][K])
    else:
        rec['status'] = 'INFEASIBLE'
        rec['value'] = None
        rec['elastic_margin'] = M.elastic()
        if want_iis:
            got = iis(M, budget_s=iis_budget)
            if got:
                rows, secs = got
                rec['iis_rows'] = len(rows)
                rec['iis'] = describe_rows(M, rows)
                rec['iis_secs'] = round(secs, 1)
                rec['iis_group_counts'] = _counts(M, rows)
    return rec, M


# --------------------------------------------------------------------------
# 7.  the two closed-form certificates of family (b)  [VERIFIED-SYMBOLIC]
# --------------------------------------------------------------------------
def certificate_predictions(K, eta, a):
    """Two 2-row subsystems of the count-grid LP, each of which already decides
    family (b) for one shape of psi.  Both are read off an IIS of the full LP and
    then verified symbolically (results section 5).

    b1 (psi supported on y = K, e.g. psi = 1[y=K]):
        band_up on the x-edge at (x, K-1) and band_lo on the y-edge at (x+1, K-2)
        carry the same Ghat increment, so   Delta_y F(x+1,K-2) <= eta Delta_x F(x,K-1),
        which for the base 1 - a^x(1-y/K) reads    a <= eta/(1+eta).
    b2 (psi == 1, i.e. an additive function of x only):
        band_lo on the y-edge at (x,K-1) and band_up on the y-edge at (x+K-1,0)
        carry the same Ghat increment, so   Delta_y F(x,K-1) <= eta Delta_y F(x+K-1,0),
        which for the same base reads            eta a^(K-1) >= 1.
    """
    return dict(b1_a_le_eta_over_1plus_eta=bool(a <= eta / (1.0 + eta) + 1e-12),
                b2_eta_a_pow_Km1_ge_1=bool(eta * a ** (K - 1) >= 1.0 - 1e-12))


# --------------------------------------------------------------------------
def main():
    quick = '--quick' in sys.argv
    WK = {(3, 1.5): 0.563577586, (3, 2.0): 0.468538012,
          (4, 1.5): 0.543703751, (4, 2.0): 0.449298285}
    out = dict(meta=dict(script='results/P1_asymmetric_families.py', solver='scipy/highs',
                         note='min F(K,0) = best (smallest) hardness constant the count-grid '
                              'family can certify; the modular witness of prop:necessity '
                              'always gives 1/eta, so every LP here is FEASIBLE and the '
                              'informative quantity is the VALUE, not feasibility.'),
               S1_prejudgement=[], S1_budget_sweep=[], S2_blocks=[], S3_structured=[],
               S3_certificates=[], S4_leak=[], S5_duals=[])

    # ---------------- section 1: general (x,y) pre-judgement ---------------
    print('=== S1 pre-judgement: general (x,y) LP, K=3 n=48 c=2 eta=2 ===', flush=True)
    for kind, tau, lab in (('typ', 1, 'exact typical set, Q=n^2'),
                           ('typmin', 1, 'necessary region {Pr>1/(4Q)}, Q=n^2'),
                           ('ysmall', 1, 'y<=1'), ('ysmall', 2, 'y<=2'),
                           ('twosided', 1, 'two-sided band tau=1'),
                           ('f3', 1, 'F3 region {y<=1} U {x>t*}')):
        rec, M = run_config(f'S1/{kind}/tau{tau}', 48, 3, (3,), 2.0, kind, c=2.0, tau=tau)
        rec['label'] = lab
        rec['modular_witness'] = 0.5
        out['S1_prejudgement'].append(rec)
        print('  %-26s %-11s value=%.7f  tau@s=K=%s  leak=%s' %
              (lab, rec['status'], rec['value'], rec['tau_at_K'],
               {k: v['verdict'] for k, v in rec.get('leak', {}).items()}), flush=True)

    print('=== S1 budget sweep ===', flush=True)
    for K in (3, 4):
        for eta in (1.5, 2.0):
            for n in (16 * K, 32 * K, 64 * K):
                for c in (0.5, 1.0, 1.5, 2.0, 3.0):
                    cst = n4_constants(K, eta)
                    thr = 1.0 / (4.0 * n ** c)
                    row = dict(K=K, eta=eta, n=n, c=c, W_K=WK[(K, eta)], inv_eta=1.0 / eta)
                    for kind in ('typmin', 'typ'):
                        reg = region_map(n, K, (K,), kind, thr=thr, tstar=cst['tstar'])
                        row[kind] = free_F_model(n, K, (K,), eta, reg).solve()['value']
                        if kind == 'typ':
                            row['tau_at_K'] = max(sum(y) for y in reg[K])
                    out['S1_budget_sweep'].append(row)
                    print('  K=%d eta=%.1f n=%-4d c=%.1f  typmin=%.7f typ=%.7f  W_K=%.7f 1/eta=%.7f'
                          % (K, eta, n, c, row['typmin'], row['typ'], row['W_K'], row['inv_eta']),
                          flush=True)

    # ---------------- section 2: family (a) block hiding -------------------
    print('=== S2 block hiding ===', flush=True)
    plan = ((3, [(3,), (1, 1, 1), (2, 1)]), (4, [(4,), (2, 2), (3, 1), (1, 1, 1, 1)]))
    for K, bl in plan:
        for blocks in bl:
            for n in (16 * K, 32 * K):
                if quick and n != 16 * K:
                    continue
                for eta in (1.5, 2.0):
                    for kind in ('f3', 'typ'):
                        rec, M = run_config('S2', n, K, blocks, eta, kind, c=2.0)
                        rec['ref_xy_value'] = None
                        out['S2_blocks'].append(rec)
                        print('  K=%d blocks=%-9s n=%-4d eta=%.1f %-5s value=%.7f leak=%s xmarg@S>=O=%.6f'
                              % (K, '-'.join(map(str, blocks)), n, eta, kind, rec['value'],
                                 {k: v['verdict'] for k, v in rec['leak'].items()},
                                 rec['x_marginal_at_full_blocks']), flush=True)
    # equality against the g=1 reference
    ref = {(r['K'], r['n'], r['eta'], r['region']): r['value']
           for r in out['S2_blocks'] if len(r['blocks']) == 1}
    for r in out['S2_blocks']:
        r['ref_xy_value'] = ref.get((r['K'], r['n'], r['eta'], r['region']))
        r['equals_xy'] = abs(r['value'] - r['ref_xy_value']) <= 1e-7

    # ---------------- section 3: family (b) --------------------------------
    print('=== S3 non-saturating F ===', flush=True)
    for K in (3, 4):
        for eta in (1.5, 2.0):
            cst = n4_constants(K, eta)
            for a, an in ((cst['q'], 'q'), (1.0 - 1.0 / (eta * K), '1-1/(eta K)')):
                for psi in ('const1', 'linear', 'top_only', 'quad'):
                    for n in (16 * K, 32 * K):
                        for kind in ('f3', 'typ'):
                            want = (psi in ('const1', 'top_only', 'linear') and n == 16 * K
                                    and kind == 'f3' and an == 'q')
                            rec, M = run_structured('S3', n, K, eta, kind, a, psi,
                                                    want_iis=want, iis_budget=200)
                            rec['a_name'] = an
                            rec['predicted'] = certificate_predictions(K, eta, a)
                            out['S3_structured'].append(rec)
                            print('  K=%d eta=%.1f n=%-4d a=%-11s psi=%-9s %-5s %-11s value=%s'
                                  % (K, eta, n, an, psi, kind, rec['status'],
                                     ('%.7f' % rec['value']) if rec['value'] is not None else '-'),
                                  flush=True)
    # closed-form certificate vs LP status, on the f3 region
    for r in out['S3_structured']:
        if r['region'] != 'f3':
            continue
        pred = (r['predicted']['b2_eta_a_pow_Km1_ge_1'] if r['psi'] == 'const1'
                else r['predicted']['b1_a_le_eta_over_1plus_eta'] if r['psi'] == 'top_only'
                else None)
        if pred is not None:
            out['S3_certificates'].append(dict(K=r['K'], eta=r['eta'], n=r['n'], a=r['a'],
                                               psi=r['psi'], lp=r['status'],
                                               predicted='FEASIBLE' if pred else 'INFEASIBLE',
                                               agree=(r['status'] == ('FEASIBLE' if pred else 'INFEASIBLE'))))
    agree = sum(c['agree'] for c in out['S3_certificates'])
    print('  closed-form certificate vs LP: %d/%d agree' % (agree, len(out['S3_certificates'])),
          flush=True)

    # ---------------- section 5: dual certificate of the collapse ----------
    print('=== S5 dual certificate for F(K,0) >= 1/eta under the typical band ===', flush=True)
    for (n, K, eta) in ((48, 3, 2.0), (64, 4, 2.0)):
        cst = n4_constants(K, eta)
        reg = region_map(n, K, (K,), 'typ', thr=1.0 / (4.0 * n ** 2), tstar=cst['tstar'])
        M = free_F_model(n, K, (K,), eta, reg)
        A, b = M.matrices()
        Aeq, beq = M._eqmat()
        obj, c0 = M.objective()
        r = linprog(obj, A_ub=A, b_ub=b, A_eq=Aeq, b_eq=beq,
                    bounds=[(None, None)] * M.nv, method='highs')
        nz = [(i, float(m)) for i, m in enumerate(r.ineqlin.marginals) if abs(m) > 1e-9]
        rec = dict(n=n, K=K, eta=eta, value=float(r.fun + c0), n_nonzero_duals=len(nz),
                   eq_duals=[float(v) for v in r.eqlin.marginals],
                   rows=[dict(tag=M.meta[i][0], state=list(M.meta[i][1]),
                              dirn=str(M.meta[i][2]), mult=m) for i, m in nz])
        out['S5_duals'].append(rec)
        print('  n=%d K=%d eta=%.1f value=%.7f  %d nonzero duals' %
              (n, K, eta, rec['value'], len(nz)), flush=True)

    # ---------------- section 4: leakage summary ---------------------------
    for r in out['S1_prejudgement'] + out['S2_blocks'] + out['S3_structured']:
        if 'leak' in r:
            out['S4_leak'].append(dict(name=r.get('name'), K=r['K'], n=r['n'], eta=r['eta'],
                                       region=r['region'], blocks=r.get('blocks'),
                                       psi=r.get('psi'),
                                       Nminus1=r['leak']['N_minus_e']['verdict'],
                                       Nminus1_in_region=r['leak']['N_minus_e']['all_in_region'],
                                       Nminus2=r['leak']['N_minus_2']['verdict'],
                                       Nminus2_in_region=r['leak']['N_minus_2']['all_in_region'],
                                       spread1=r['leak']['N_minus_e']['spread'],
                                       spread2=r['leak']['N_minus_2']['spread']))
    n_leak = sum(1 for r in out['S4_leak'] if 'LEAK' in (r['Nminus1'], r['Nminus2']))
    print('=== S4 leakage: %d/%d feasible solutions LEAK ===' % (n_leak, len(out['S4_leak'])),
          flush=True)
    out['summary'] = dict(n_leak=n_leak, n_checked=len(out['S4_leak']),
                          blocks_equal_xy=all(r['equals_xy'] for r in out['S2_blocks']),
                          certificate_agreement=[agree, len(out['S3_certificates'])])
    _dump(out)


def _dump(out):
    p = os.path.join(HERE, 'P1_asymmetric_families.json')
    with open(p, 'w') as fh:
        json.dump(out, fh, indent=1, default=str)
    print('wrote', p, flush=True)


if __name__ == '__main__':
    main()
