# Verification record

Repository snapshot: `zhiyunjiang0810/sub-modular-optimization`, commit `6ea1ab859409e95654015346bd214d8fea46daef` (2026-09-11 10:36:57 UTC).

The repository was read through the GitHub connector. Its mathematical source files and selected scripts were saved to a scratch copy. The original repository was not modified. The 35-page PDF was extracted and relevant theorem pages were rendered and visually checked against the source.

## Completed reruns

| Script | Scope/result |
|---|---|
| `results/N1_dual_certificate.py` | `N1_KMAX=10`; 320/320 PASS; general symbolic branches plus finite symbolic and LP checks |
| `results/N2_check.py` | 480/480 PASS after obtaining all imported repository dependencies |
| `results/T5_symbolic.py` | Complete script, exit 0 |
| `results/H_J3_gate_check.py` | 40 faces; 2,480 coordinate LPs; maximum deviation 3.94e-15; all checks PASS |
| `results/H_B_asymptotic.py --quick` | Symbolic expansion and monotonicity certificate passed; 84 positive-numerator terms, constant 14; large-K LP mode was NOT run |
| `results/L1_table.py` | Complete script, all checks PASS |
| `results/J2_core_oracles.py` | Complete script, exit 0 |
| `results/H3_j2_recheck.py` | Complete script, all checks PASS, including calibration and E2 zero-step counts |
| `results/H_E_ceiling_small_n.py` | Complete script, exit 0; grid matches C; original intersection proof step still fails as documented |
| `verify_audit.py` | Independent standard-library exact certificate verification, matching full-lattice witness, stopped-run counterexample, and sample complement-loss inequalities; all checks PASS |

The Python runtime used SymPy 1.14.0, SciPy 1.18.1, NumPy 2.5.3 and mpmath 1.3.0. Solver versions and floating tolerances do not affect the standalone Fraction verifier.

## New exact certificate

`submodular_K4_exact_duals.json` stores nonzero rational inequality multipliers and equality multipliers for each of the 16 optimal-set orbit representatives at n=8, K=4, eta_u=1, eta_o=3/2.

`verify_audit.py` reconstructs the inequalities from scratch using only Python's standard library. It checks multiplier signs and every coefficient of the dual identity exactly, then verifies a matching instance, with exact monotonicity, submodularity of both functions, error-band saturation, cardinality optimum and greedy ties. Run it with the JSON file in the same directory:

```
python verify_audit.py
```

The certificate gives rho_sub(8,4,3/2)=23/41. The restriction/padding proof in the audit report extends the statement to n>=8. The general small-n minimax result is proved in §9 of the report; finite checks are supplementary evidence, not a substitute for that proof.

## Not independently rerun

- The complete L2/L2R/H_F branch-and-bound searches. Their code and stored outputs were inspected; floating tolerances and rational reconstruction are explicitly identified in the audit.
- The claimed 253,220 all-pairs checks from J4: the original independent script was not obtained.
- The full F3 arbitrary-query construction sweep, all R-step LPs, all additive-band tightness LPs, and the full real-data experiment pipeline.

No statement in the report should be read as an independent rerun of these computations.
