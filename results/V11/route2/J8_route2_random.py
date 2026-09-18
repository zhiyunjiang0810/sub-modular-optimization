"""Random search for a violation of E[f(T)] >= (3/5 + 1/400000) OPT (K=2, eta=3/2).

Two predictor families, both exactly inside the band d <= tilde d <= (3/2) d:
  (a) scaled coverage: tilde f is the coverage function of the same universe with
      atom weights multiplied by s_a in [1, 3/2]  (band holds atomwise);
  (b) the pointwise-maximal predictor of the difference system (J8_route2_check),
      i.e. tilde d pushed to the upper edge wherever the system allows.
Family (a) makes tilde f submodular, family (b) does not.
Exact rational arithmetic; floats only in the printout.

Rerun: python3 J8_route2_random.py [trials]
"""
import sys, random
from fractions import Fraction as F
from itertools import combinations
from J8_route2_check import (coverage_f, probe_lottery, opt2, feasible_tilde,
                             check_submodular)

random.seed(20260918)


def rand_instance(rng):
    """Structured hard family: the universe splits into A1 (covered by o1) and
    A2 (covered by o2), and 2-4 decoys cover parts of both halves, which is the
    geometry of the exact worst case at K = 2."""
    h = rng.randint(2, 3)                       # atoms per half
    A1 = ['u%d' % i for i in range(h)]
    A2 = ['w%d' % i for i in range(h)]
    atoms = A1 + A2
    weight = {a: F(rng.randint(1, 4), 4) for a in atoms}
    ndec = rng.randint(2, 4)
    elements = ['d%d' % i for i in range(ndec)] + ['o1', 'o2']
    cover = {'o1': set(A1), 'o2': set(A2)}
    for i in range(ndec):
        k1 = rng.randint(0, h)
        k2 = rng.randint(0, h)
        c = set(rng.sample(A1, k1)) | set(rng.sample(A2, k2))
        if not c:
            c = {rng.choice(atoms)}
        cover['d%d' % i] = c
    f = coverage_f(elements, cover, weight)
    return elements, atoms, weight, cover, f


def scaled_predictor(elements, atoms, weight, cover, rng):
    s = {a: rng.choice([F(1), F(5, 4), F(4, 3), F(3, 2)]) for a in atoms}
    w2 = {a: weight[a] * s[a] for a in atoms}
    return coverage_f(elements, cover, w2)


def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    rng = random.Random(20260918)
    target = F(3, 5) + F(1, 400000)
    worst_E, worst_P0, bad = None, None, 0
    for t in range(trials):
        elements, atoms, weight, cover, f = rand_instance(rng)
        OPT = opt2(elements, f)
        if OPT == 0:
            continue
        for mode in ('scaled', 'maximal'):
            if mode == 'scaled':
                tf = scaled_predictor(elements, atoms, weight, cover, rng)
            else:
                ok, tf = feasible_tilde(elements, f, ())
                if not ok:
                    continue
            R = probe_lottery(elements, tf, f)
            r_alg, r_pg = R['E'] / OPT, f[R['P0']] / OPT
            if worst_E is None or r_alg < worst_E:
                worst_E = r_alg
            if worst_P0 is None or r_pg < worst_P0:
                worst_P0 = r_pg
            if r_alg < target:
                bad += 1
                if bad <= 3:
                    print('VIOLATION', mode, [sorted(cover[e]) for e in elements],
                          {a: str(weight[a]) for a in atoms}, float(r_alg))
            assert R['nqueries'] <= 9 * len(elements)
            assert R['maxsize'] <= 5
    print('trials:', trials, ' violations of 3/5 + 1/400000:', bad)
    print('min E/OPT       =', worst_E, '=', float(worst_E))
    print('min f(P0)/OPT   =', worst_P0, '=', float(worst_P0),
          ' (>= 3/5 ?', worst_P0 >= F(3, 5), ')')


if __name__ == '__main__':
    main()
