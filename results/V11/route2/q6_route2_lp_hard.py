"""ROUTE-TWO (Q6, thm:linear-exact) part 3: hardness 族的 LP 检验 (一键复跑).

三种 predictor 对称性 (predictor = tilde f, 唯一可查询对象):
  mode="count"  : ft(S) 只依赖 |S|                      (完全对称)
  mode="blocks" : ft(S) 只依赖 (|S∩B_0|,...,|S∩B_{K-1}|)  (K 个 block, 每块一个隐藏好元素)
  mode="blind"  : ft(S) 只依赖 |S|, 除非 |S∩O*| >= tau   (tau-blind predictor)
f 始终 monotone submodular, band 对指定 split (eta_u, eta_o) 成立, f(O*)=1 且 O* 在
所有 K-set 中最优. fgrid=True 时额外要求 f 也是 count-grid (只依赖 (|S∩O*|,|S\\O*|)).

目标三选一:
  per-T   : min f(T), T 为一个与 O* 不交的指定 K-set      (确定性论证需要的量)
  all-T   : min max_{T 与 O* 不交} f(T)
  avg-T   : min mean_{T 与 O* 不交} f(T)                  (随机化 averaging 需要的量)

参考: rho_2(3/2)=3/5, rho_3(3/2)=9/16, 1/eta=2/3, L_2(3/2)=5/9, L_3(3/2)=386/729.
float 只出现在 LP 求解与打印中.
"""
import itertools
import sys

import numpy as np
from scipy.optimize import linprog


def lp(m, K, eta_u, eta_o, opt, mode="blind", tau=2, blocks=None,
       objective="all", T_fixed=None, fgrid=False, traj=None):
    O = frozenset(opt)
    subs = [frozenset(c) for r in range(m + 1) for c in itertools.combinations(range(m), r)]
    idx = {s: i for i, s in enumerate(subs)}
    n = len(subs)
    NV = 2 * n + 1
    ZI = 2 * n
    fi = lambda s: idx[s]
    gi = lambda s: n + idx[s]
    row = lambda: [0.0] * NV
    A_ub, b_ub, A_eq, b_eq = [], [], [], []

    for s in subs:
        rest = [e for e in range(m) if e not in s]
        for e in rest:
            r = row(); r[fi(s | {e})] = -1.0; r[fi(s)] = 1.0          # monotone
            A_ub.append(r); b_ub.append(0.0)
            r = row()                                                  # band lower
            r[fi(s | {e})] = 1.0 / eta_u; r[fi(s)] = -1.0 / eta_u
            r[gi(s | {e})] += -1.0; r[gi(s)] += 1.0
            A_ub.append(r); b_ub.append(0.0)
            r = row()                                                  # band upper
            r[gi(s | {e})] = 1.0; r[gi(s)] = -1.0
            r[fi(s | {e})] += -eta_o; r[fi(s)] += eta_o
            A_ub.append(r); b_ub.append(0.0)
        for e, e2 in itertools.combinations(rest, 2):                  # submodular
            r = row()
            r[fi(s | {e, e2})] += 1.0; r[fi(s)] += 1.0
            r[fi(s | {e})] -= 1.0; r[fi(s | {e2})] -= 1.0
            A_ub.append(r); b_ub.append(0.0)

    r = row(); r[fi(frozenset())] = 1.0; A_eq.append(r); b_eq.append(0.0)
    r = row(); r[gi(frozenset())] = 1.0; A_eq.append(r); b_eq.append(0.0)

    def key(s):
        if mode == "count":
            return (len(s),)
        if mode == "blocks":
            return tuple(len(s & b) for b in blocks)
        if mode == "blind":
            return (len(s), 0) if len(s & O) < tau else (len(s), len(s & O))
        return ("free", tuple(sorted(s)))

    cls = {}
    for s in subs:
        cls.setdefault(key(s), []).append(s)
    for _, lst in cls.items():
        for a, b in zip(lst, lst[1:]):
            r = row(); r[gi(a)] = 1.0; r[gi(b)] = -1.0
            A_eq.append(r); b_eq.append(0.0)

    if fgrid:
        cls2 = {}
        for s in subs:
            cls2.setdefault((len(s & O), len(s) - len(s & O)), []).append(s)
        for _, lst in cls2.items():
            for a, b in zip(lst, lst[1:]):
                r = row(); r[fi(a)] = 1.0; r[fi(b)] = -1.0
                A_eq.append(r); b_eq.append(0.0)

    if traj is not None:            # predictive greedy 的轨迹 (对抗 tie 允许取等号)
        st = frozenset()
        for t in range(K):
            et = traj[t]
            for e in range(m):
                if e in st or e == et:
                    continue
                r = row()
                r[gi(st | {e})] += 1.0; r[gi(st | {et})] -= 1.0
                A_ub.append(r); b_ub.append(0.0)
            st = st | {et}

    r = row(); r[fi(O)] = 1.0; A_eq.append(r); b_eq.append(1.0)
    for c in itertools.combinations(range(m), K):
        r = row(); r[fi(frozenset(c))] = 1.0
        A_ub.append(r); b_ub.append(1.0)

    c_obj = [0.0] * NV
    Ts = [frozenset(c) for c in itertools.combinations(range(m), K)
          if not (frozenset(c) & O)]
    if objective == "per":
        c_obj[fi(frozenset(T_fixed))] = 1.0
    elif objective == "avg":
        for T in Ts:
            c_obj[fi(T)] += 1.0 / len(Ts)
    else:
        for T in Ts:
            r = row(); r[fi(T)] = 1.0; r[ZI] = -1.0
            A_ub.append(r); b_ub.append(0.0)
        c_obj[ZI] = 1.0

    res = linprog(c_obj, A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)] * NV, method="highs")
    return res.fun if res.success else None


def main():
    eta = 1.5
    print("reference: rho_2(3/2)=0.600000  rho_3(3/2)=0.562500  1/eta=0.666667")
    print("\n[A] greedy 自身的精确最坏值 (predictor 自由, 固定 greedy 轨迹)")
    for K, m in [(2, 5), (3, 6)]:
        traj = tuple(range(K))
        best = None
        for opt in itertools.combinations(range(m), K):
            v = lp(m, K, 1.0, eta, opt, mode="free", objective="per",
                   T_fixed=traj, traj=traj)
            if v is not None and (best is None or v < best):
                best = v
        print(f"  K={K} m={m}: min over O* = {best:.9f}")
        sys.stdout.flush()

    print("\n[B] 对称 predictor 的天花板 (与算法输出 T 无关的构造)")
    print(f"  K=2 m=6 count-only  all-T: "
          f"{lp(6,2,1.0,eta,(4,5),mode='count',objective='all'):.9f}")
    print(f"  K=2 m=6 blocks(3+3) all-T: "
          f"{lp(6,2,1.0,eta,(2,5),mode='blocks',blocks=[frozenset({0,1,2}),frozenset({3,4,5})],objective='all'):.9f}")
    print(f"  K=3 m=6 count-only  all-T: "
          f"{lp(6,3,1.0,eta,(3,4,5),mode='count',objective='all'):.9f}")

    print("\n[C] 1-blind predictor (tau=2): 主构造")
    for (eu, eo, tag) in [(1.0, eta, "(1,3/2)"), (eta, 1.0, "(3/2,1)"),
                          (eta ** 0.5, eta ** 0.5, "(sqrt,sqrt)")]:
        for K, m, opt, T in [(2, 7, (5, 6), (0, 1)), (3, 7, (4, 5, 6), (0, 1, 2))]:
            per = lp(m, K, eu, eo, opt, mode="blind", tau=2, objective="per", T_fixed=T)
            allT = lp(m, K, eu, eo, opt, mode="blind", tau=2, objective="all")
            avg = lp(m, K, eu, eo, opt, mode="blind", tau=2, objective="avg")
            grid = lp(m, K, eu, eo, opt, mode="blind", tau=2, objective="all", fgrid=True)
            print(f"  K={K} m={m} split={tag}: per-T {per:.9f}  all-T {allT:.9f}  "
                  f"avg-T {avg:.9f}  all-T(f count-grid) {grid:.9f}")
            sys.stdout.flush()

    print("\n[D] tau=3 (2-blind) 对照, K=3")
    print(f"  K=3 m=7 all-T: {lp(7,3,1.0,eta,(4,5,6),mode='blind',tau=3,objective='all'):.9f}")

    print("\n[E] 1-blind, m 依赖性 (K=2)")
    for m in (5, 6, 7, 8, 9):
        print(f"  m={m}: all-T {lp(m,2,1.0,eta,(m-2,m-1),mode='blind',tau=2,objective='all'):.9f}"
              f"  per-T {lp(m,2,1.0,eta,(m-2,m-1),mode='blind',tau=2,objective='per',T_fixed=(0,1)):.9f}")


if __name__ == "__main__":
    main()
