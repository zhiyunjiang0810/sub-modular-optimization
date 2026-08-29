"""T1 baseline reproduction. One-click: python3 results/T1_baseline.py  (run from overnight/).
1. Runs code/check_explicit_instance.py (expect ALL PASS).
2. Runs code/worst_case_lp.py's worst_case() for K=2 (n=4) and K=3 (n=6),
   single-element error, eta_u = eta_o = sqrt(eta), and compares with RESEARCH_STATE.md R5.
Output: results/T1_baseline.txt
"""
import subprocess, sys, os
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "code"))
from worst_case_lp import worst_case, paper_bound

OUT = []
def emit(s=""):
    print(s); OUT.append(s)

emit("== T1.1 check_explicit_instance.py ==")
r = subprocess.run([sys.executable, os.path.join(ROOT, "code", "check_explicit_instance.py")],
                   capture_output=True, text=True, timeout=1200)
emit(r.stdout.strip())
emit(f"exit code: {r.returncode} (expect 0)")

emit("")
emit("== T1.2 worst_case_lp vs R5 (single-element error, eta_u=eta_o=sqrt(eta)) ==")
R5 = {
    2: {1.0: Fraction(3,4), 1.5: Fraction(3,5), 2.0: Fraction(1,2),
        2.5: Fraction(2,5), 3.0: Fraction(1,3), 4.0: Fraction(1,4)},
    3: {1.0: Fraction(19,27), 1.5: Fraction(9,16), 2.0: Fraction(7,15),
        2.5: Fraction(7,18), 3.0: Fraction(1,3), 4.0: Fraction(1,4)},
}
ok_all = True
for K, n in [(2, 4), (3, 6)]:
    for eta, expect in R5[K].items():
        val, O, _ = worst_case(n, K, eta**0.5, eta**0.5, "single")
        ok = abs(val - float(expect)) < 1e-7
        ok_all &= ok
        emit(f"K={K} n={n} eta={eta}: LP={val:.9f}  R5={float(expect):.9f} ({expect})  "
             f"{'OK' if ok else 'MISMATCH'}")
emit("")
emit("T1 RESULT: " + ("ALL CONSISTENT [VERIFIED-LP]" if ok_all and r.returncode == 0
                      else "INCONSISTENCY FOUND - see above"))
with open(os.path.join(HERE, "T1_baseline.txt"), "w") as fh:
    fh.write("\n".join(OUT) + "\n")
sys.exit(0 if ok_all and r.returncode == 0 else 1)
