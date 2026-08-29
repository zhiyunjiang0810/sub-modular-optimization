"""T2 cross-check: relaxed-F hardness LP on the FULL lattice at (n,K)=(8,3),
against the symmetrized grid LP (results/T2_hardness_grid.py relaxF).

Variables: F[S] for all S; Ghat_s (s=0..n) shared by balanced S; G[S] for
unbalanced S.  Constraints: F(empty)=0, F(O)=1, F monotone, F submodular,
F(S) <= 1 for |S| <= K (OPT = O), Ghat_0 = 0, single-element error band with
exact eta (delta = 0).  Two objectives:
  avg : minimize average of F over all K-subsets of B  -> must EQUAL grid value
        (group-averaging argument), oracle for the symmetrization.
  one : minimize F of one fixed K-subset of B          -> may be lower
        (asymmetric adversary against a single output).
Usage: python3 results/T2_relaxF_lattice_check.py
"""
import itertools, os, sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from T2_hardness_grid import relaxF_min_ratio

TOL = 1e-9


def lattice_relaxF(n, K, eta, tau, defn, objective='avg', split='sqrt'):
    eta_u, eta_o = ((eta ** 0.5,) * 2) if split == 'sqrt' else (eta, 1.0)
    N = 1 << n
    maskB = (1 << (n - K)) - 1
    x = np.array([bin(S & maskB).count('1') for S in range(N)])
    y = np.array([bin(S >> (n - K)).count('1') for S in range(N)])
    sz = x + y
    if defn == 'ysmall':
        bal = y <= tau
    else:
        bal = np.abs(y - K * sz / n) <= tau + 1e-12
    fid = lambda S: S
    gh0 = N
    unbal = [S for S in range(N) if not bal[S]]
    gvid = {S: gh0 + n + 1 + i for i, S in enumerate(unbal)}
    nv = gh0 + n + 1 + len(unbal)
    gref = lambda S: (gh0 + sz[S]) if bal[S] else gvid[S]

    R, C, V, b = [], [], [], []
    r = 0
    def ub(coefs, rhs=0.0):
        nonlocal r
        acc = {}
        for c, v in coefs:
            acc[c] = acc.get(c, 0.0) + v
        for c, v in acc.items():
            if v:
                R.append(r); C.append(c); V.append(v)
        b.append(rhs); r += 1

    for S in range(N):
        for e in range(n):
            if S >> e & 1: continue
            Se = S | 1 << e
            ub([(fid(S), 1.0), (fid(Se), -1.0)])                     # monotone
            gq, gp = gref(Se), gref(S)
            ub([(gq, 1.0), (gp, -1.0), (fid(Se), -eta_o), (fid(S), eta_o)])
            ub([(fid(Se), 1 / eta_u), (fid(S), -1 / eta_u), (gq, -1.0), (gp, 1.0)])
            for e2 in range(n):                                       # submodular
                if e2 == e or S >> e2 & 1: continue
                T = S | 1 << e2
                ub([(fid(T | 1 << e), 1.0), (fid(T), -1.0),
                    (fid(Se), -1.0), (fid(S), 1.0)])
    for S in range(1, N):
        if sz[S] <= K:
            ub([(fid(S), 1.0)], 1.0)                                  # OPT = O
    Omask = (N - 1) ^ maskB
    eR, eC, eV, eb = [0, 1, 2], [fid(0), fid(Omask), gh0], [1.0, 1.0, 1.0], [0.0, 1.0, 0.0]
    A_eq = coo_matrix((eV, (eR, eC)), shape=(3, nv)).tocsr()
    obj = np.zeros(nv)
    Bsets = list(itertools.combinations(range(n - K), K))
    if objective == 'avg':
        for T in Bsets:
            obj[fid(sum(1 << i for i in T))] = 1.0 / len(Bsets)
    else:
        obj[fid(sum(1 << i for i in Bsets[0]))] = 1.0
    A_ub = coo_matrix((V, (R, C)), shape=(r, nv)).tocsr()
    out = linprog(obj, A_ub=A_ub, b_ub=np.array(b), A_eq=A_eq, b_eq=np.array(eb),
                  bounds=[(None, None)] * nv, method='highs')
    return out.fun if out.status == 0 else None


if __name__ == '__main__':
    ok = True
    for eta in [1.5, 2.0, 3.0]:
        for tau in [1]:
            for defn in ['ysmall', 'true']:
                grid = relaxF_min_ratio(8, 3, eta, tau, defn)['ratio']
                avg = lattice_relaxF(8, 3, eta, tau, defn, 'avg')
                one = lattice_relaxF(8, 3, eta, tau, defn, 'one')
                match = avg is not None and abs(avg - grid) < 1e-6
                ok &= match
                print(f"eta={eta} tau={tau} {defn:6s}: grid={grid:.6f} "
                      f"lattice_avg={avg:.6f} {'OK' if match else 'MISMATCH'}   "
                      f"lattice_one={one:.6f} (asym gain {grid - one:+.6f})", flush=True)
    print('RELAXF LATTICE CROSSCHECK', 'PASS' if ok else 'FAIL')
    sys.exit(0 if ok else 1)
