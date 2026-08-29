"""
T4 auxiliary check: the per-O pair-LP value depends only on the symmetry type
(|O & {0,1}|, |O & {2,3}|, |O & rest|)  -- i.e. the LP is invariant under
permutations inside the first chosen pair, inside the second chosen pair, and
inside the remaining elements.  This justifies the symmetry-reduced candidate
enumeration (canonical_Os) used for the n=9 run in T4_pair_greedy_lp.py.

Run AFTER `python3 T4_pair_greedy_lp.py full` (needs the full per-O values in
T4_pair_vs_single.json).  Exits nonzero if any type has spread > 1e-6.
"""
import json, os, sys, ast
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "T4_pair_vs_single.json")))
bad = 0
for key, blob in sorted(d.items()):
    per = blob.get("per_O_pair", {})
    if blob.get("sym_reduced"):
        continue  # reduced runs have one O per type by construction
    groups = defaultdict(list)
    for Ostr, v in per.items():
        O = ast.literal_eval(Ostr)
        a = len([i for i in O if i in (0, 1)])
        b = len([i for i in O if i in (2, 3)])
        groups[(a, b, len(O) - a - b)].append(v)
    print(f"== {key}: pair_LP={blob['pair_LP']:.6f} argminO={blob['pair_argmin_O']}")
    for k in sorted(groups):
        vals = groups[k]
        spread = max(vals) - min(vals)
        ok = spread < 1e-6
        bad += not ok
        print(f"   type={k}: count={len(vals):2d} min={min(vals):.6f} "
              f"max={max(vals):.6f} {'OK' if ok else 'VARIES <-- symmetry violated'}")
print("SYMMETRY CHECK:", "PASS" if bad == 0 else f"FAIL ({bad} types vary)")
sys.exit(1 if bad else 0)
