#!/usr/bin/env python3
"""Independent checks of statements in REVIEW_BRIEF.md (2026-09-07).

Python 3.10+; standard library only. No manuscript or original scripts needed.
Run: python3 results/J1_independent_audit.py > results/J1_oracle_output.json

This does NOT verify R6, the exact-ratio dual certificate, or the completeness
of the hardness construction's two distortion branches: their sources were
not present in the supplied archive. All arithmetic for finite witnesses and
the lattice enumeration is exact (fractions.Fraction).
"""

from fractions import Fraction as F
from itertools import permutations, product
import json
import math


def remaining(mask, n):
    return [e for e in range(n) if not (mask >> e) & 1]


def marginal(values, mask, e):
    return values[mask | (1 << e)] - values[mask]


def assert_monotone_submodular(values, n):
    assert values[0] == 0
    for a in range(1 << n):
        for e in remaining(a, n):
            assert marginal(values, a, e) >= 0
        # All-pairs lattice inequality, not just sampled diminishing returns.
        for b in range(1 << n):
            assert values[a] + values[b] >= values[a | b] + values[a & b]


def trace_data(values, order, n, k):
    assert len(order) == k and len(set(order)) == k
    state = 0
    gains, bests = [], []
    states = []
    for e in order:
        states.append(state)
        gains.append(marginal(values, state, e))
        bests.append(max(marginal(values, state, x) for x in remaining(state, n)))
        state |= 1 << e
    old_terms = [F(m, g) for m, g in zip(bests, gains) if g > 0]
    # None leaves the brief's unspecified max-of-empty convention unspecified.
    old_eta = max(old_terms) if old_terms else None
    bad_zero = any(g == 0 and m > 0 for g, m in zip(gains, bests))
    repaired_eta = None if bad_zero else max([F(1)] + old_terms)
    uniform = F(0) if bad_zero else 1 - (1 - 1 / (k * repaired_eta)) ** k
    residual_product = F(1)
    for g, m in zip(gains, bests):
        quality = F(g, m) if m > 0 else F(1)
        residual_product *= 1 - quality / k
    optimum = max(values[s] for s in range(1 << n) if s.bit_count() <= k)
    return dict(
        states=states,
        order=order,
        gains=gains,
        bests=bests,
        old_eta=old_eta,
        repaired_eta="infinity" if bad_zero else repaired_eta,
        repaired_uniform_bound=uniform,
        product_bound=1 - residual_product,
        output=values[state],
        optimum=optimum,
        ratio=F(values[state], optimum) if optimum else None,
    )


def greedy_order(values, n, k):
    state, order = 0, []
    for _ in range(k):
        e = max(remaining(state, n), key=lambda x: (marginal(values, state, x), -x))
        order.append(e)
        state |= 1 << e
    return tuple(order)


def error_band(values, predicted, n, states=None):
    ratios = []
    for s in range(1 << n) if states is None else states:
        for e in remaining(s, n):
            actual = marginal(values, s, e)
            estimate = marginal(predicted, s, e)
            if actual == 0:
                if estimate != 0:
                    return {"eta": "infinity"}
            elif estimate <= 0:
                return {"eta": "infinity"}
            else:
                ratios.append(F(estimate, actual))
    under = max([F(1)] + [1 / r for r in ratios])
    over = max([F(1)] + ratios)
    return {"eta_u": under, "eta_o": over, "eta": under * over}


def zero_gain_counterexample():
    # Elements a,b,c. True weights 1,1,0; predictor weights 2,1,3.
    n, k = 3, 2
    weights, predicted_weights = (1, 1, 0), (2, 1, 3)
    values = [sum(w for i, w in enumerate(weights) if (s >> i) & 1) for s in range(8)]
    predicted = [sum(w for i, w in enumerate(predicted_weights) if (s >> i) & 1) for s in range(8)]
    assert_monotone_submodular(values, n)
    assert_monotone_submodular(predicted, n)
    order = greedy_order(predicted, n, k)
    assert order == (2, 0)
    run = trace_data(values, order, n, k)
    assert run["old_eta"] == 1
    assert run["ratio"] == F(1, 2) < F(3, 4)
    assert run["repaired_eta"] == "infinity"
    assert run["product_bound"] == F(1, 2)
    assert error_band(values, predicted, n)["eta"] == "infinity"
    for s, chosen in zip(run["states"], order):
        assert all(marginal(predicted, s, chosen) > marginal(predicted, s, e)
                   for e in remaining(s, n) if e != chosen)
    return {"true_weights": weights, "predicted_weights": predicted_weights, **run,
            "old_claimed_bound": F(3, 4), "strict_greedy": True}


def two_rulers_counterexample():
    # C={0,1}, O={2,3}; x=|S intersect C|, y=|S intersect O|.
    # f=1-(3/4)^x(1-y/2), predictor=1-(1/3)^x(1-y/2).
    n, k = 4, 2
    values, predicted = [], []
    for s in range(16):
        x = (s & 3).bit_count()
        y = (s >> 2).bit_count()
        values.append(1 - F(3, 4) ** x * (1 - F(y, 2)))
        predicted.append(1 - F(1, 3) ** x * (1 - F(y, 2)))
    assert_monotone_submodular(values, n)
    assert_monotone_submodular(predicted, n)
    order = greedy_order(predicted, n, k)
    assert order == (0, 1)
    run = trace_data(values, order, n, k)
    assert run["old_eta"] == run["repaired_eta"] == 2
    assert run["ratio"] == F(7, 16)
    assert run["repaired_uniform_bound"] == run["product_bound"] == F(7, 16)
    for s, chosen in zip(run["states"], order):
        assert all(marginal(predicted, s, chosen) > marginal(predicted, s, o) for o in (2, 3))
    global_band = error_band(values, predicted, n)
    trajectory_band = error_band(values, predicted, n, run["states"])
    assert global_band["eta"] == F(27, 2)
    assert trajectory_band["eta"] == 6
    # At K=2, eta=2, BOTH displayed V_j values equal 1/2.
    displayed_v = [1 - F(2, 3) ** j * (1 - F(2 - j, 4)) for j in (0, 1)]
    assert min(displayed_v) == F(1, 2) > run["ratio"]
    return {**run, "global_band": global_band, "trajectory_band": trajectory_band,
            "displayed_rho_at_selection_error": min(displayed_v),
            "strict_preference_over_optimal_elements": True,
            "all_true_values": values, "all_predictor_values": predicted}


def complete_small_lattice_check():
    # ALL normalized functions on 3 elements with every value in {0,1,2,3}.
    # Filter by ALL lattice submodularity inequalities and monotonicity edges.
    # For every accepted function, test ALL ordered runs, K=1,2,3, against
    # independently enumerated OPT. This is finite support, not a general proof.
    n = 3
    monotone_edges = [(s, s | (1 << e)) for s in range(8) for e in remaining(s, n)]
    lattice_pairs = [(a, b, a | b, a & b) for a in range(8) for b in range(8)]
    traces = [(k, order) for k in range(1, n + 1) for order in permutations(range(n), k)]
    accepted = checked = old_violations = bad_zero_runs = 0
    for nonempty_values in product(range(4), repeat=7):
        f = (0,) + nonempty_values
        if any(f[b] < f[a] for a, b in monotone_edges):
            continue
        if any(f[a] + f[b] < f[u] + f[i] for a, b, u, i in lattice_pairs):
            continue
        accepted += 1
        for k, order in traces:
            run = trace_data(f, order, n, k)
            checked += 1
            assert run["output"] >= run["repaired_uniform_bound"] * run["optimum"]
            assert run["output"] >= run["product_bound"] * run["optimum"]
            assert run["product_bound"] >= run["repaired_uniform_bound"]
            if run["repaired_eta"] == "infinity":
                bad_zero_runs += 1
            if run["old_eta"] is not None:
                old_bound = 1 - (1 - 1 / (k * run["old_eta"])) ** k
                if run["output"] < old_bound * run["optimum"]:
                    old_violations += 1
                    assert run["repaired_eta"] == "infinity"
    assert old_violations > 0
    return {"candidate_functions": 4 ** 7, "monotone_submodular_functions": accepted,
            "ordered_runs_checked": checked, "uniform_bound_failures": 0,
            "product_bound_failures": 0, "old_definition_violations": old_violations,
            "runs_with_harmful_zero": bad_zero_runs,
            "scope": "n=3; all values in {0,1,2,3}; K=1,2,3; all ordered runs"}


def finite_delta_branch_check():
    k, tau, theta = 4, 2, F(13, 10)
    a = 1 - 1 / (theta * k)
    first = (a ** tau * F(k, k - tau)) ** 2
    second = (a ** (1 - tau)) ** 2
    assert theta < 2 - F(1, tau)
    assert first > second
    exact_switch_decimal = 1 / (k * (1 - (1 - tau / k) ** (1 / (2 * tau - 1))))
    count = 0
    for tau2 in range(1, 7):
        for k2 in range(2 * tau2, 2 * tau2 + 9):
            for theta2 in (F(1), F(6, 5), F(13, 10), F(3, 2), F(2), F(4), F(10)):
                a2 = 1 - 1 / (theta2 * k2)
                aa = a2 ** tau2 * F(k2, k2 - tau2)
                bb = a2 ** (1 - tau2)
                assert (aa >= bb) == (a2 ** (2 * tau2 - 1) >= F(k2 - tau2, k2))
                count += 1
    return {"K": k, "tau": tau, "theta": theta, "first_squared_branch": first,
            "second_squared_branch": second, "asymptotic_switch": 2 - F(1, tau),
            "finite_switch_decimal": exact_switch_decimal, "branch_equivalence_checks": count,
            "scope": "Only compares the TWO GIVEN formulas. Does not prove they exhaust distortion."}


def encode(value):
    if isinstance(value, F):
        return str(value)
    raise TypeError(type(value).__name__)


if __name__ == "__main__":
    output = {
        "zero_gain_counterexample": zero_gain_counterexample(),
        "two_rulers_counterexample": two_rulers_counterexample(),
        "small_lattice_oracle": complete_small_lattice_check(),
        "finite_delta_branch_check": finite_delta_branch_check(),
        "all_assertions_passed": True,
        "not_reviewed": ["R6 reduction", "dual coefficient matching", "hardness distortion completeness",
                         "original CSV figures", "Theorem 6 source construction", "new ICLR PDF layout"],
    }
    print(json.dumps(output, default=encode, ensure_ascii=False, indent=2))
