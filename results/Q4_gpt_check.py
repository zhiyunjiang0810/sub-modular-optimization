"""Q4 gate (TASKS10): the verification core supplied verbatim with the
morning cross-check delivery (external parallel result, source: GPT).
Saved unmodified except for this docstring; run as
  python3 results/Q4_gpt_check.py
Expected: "13 symbolic identities: PASS" then
  configs=159, edges=111032, DR=207842, balanced=2441.
H always denotes eta_u * G, so the rational checks need no sqrt(eta).
"""
from fractions import Fraction as R
from math import ceil
import sympy as sp

# ---------- General symbolic branch identities ----------
K, E, Q, z, y = sp.symbols("K E Q z y", positive=True)
p, s, r, h = sp.symbols("p s r h", real=True)
j = sp.symbols("j", integer=True, nonnegative=True)

k1 = (K - 1) * E + 1
q = (K - 1) * E / k1
D = Q / (K * E)
A = Q * (K - 1) / K
C = k1 / K

identities = [
    # Junction: B increment drops; one-O increment continues.
    D - (K - 1) / K * Q / (q * k1),
    (K - 1) / K * Q / (q * k1) - D,

    # Initial and linear phases of H.
    C - Q - (E - 1) * Q * (K - 1) / K - C * (1 - Q),
    C - E * Q * (K - 1) / K - C * (1 - q * Q),
    C - (Q - z) - (E - 1) * (A - z)
        - (C * (1 - Q) + E * z),
    C - E * (A - z)
        - (C * (1 - Q) + E * (z + D)),

    # First-vs-later O marginal.
    (Q - z) - (A - z) - (A - z) / (K - 1)
        - z / (K - 1),

    # All four scaled-predictor edge identities.
    (C - (r - p) - (E - 1) * (h - s))
        - (C - r - (E - 1) * h)
        - (p + (E - 1) * s),
    (C - E * h) - (C - r - (E - 1) * h) - (r - h),
    (C - E * (K - y) * (h - s) / (K - 1))
        - (C - E * (K - y) * h / (K - 1))
        - E * (K - y) * s / (K - 1),
    (C - E * (K - y - 1) * h / (K - 1))
        - (C - E * (K - y) * h / (K - 1))
        - E * h / (K - 1),

    # Objective and adjacent branches.
    1 - Q + (K - j) * D
        - (1 - Q * (1 - (K - j) / (K * E))),
    (1 - q * Q * (1 - (K - j - 1) / (K * E)))
        - (1 - Q * (1 - (K - j) / (K * E)))
        - Q * (E - K + j) / (K * E * k1),
]
assert all(sp.cancel(expr) == 0 for expr in identities)
print("13 symbolic identities: PASS")


# ---------- Exact finite-parameter checks ----------
counts = dict(configs=0, edges=0, DR=0, balanced=0)

for k in range(2, 13):
    etas = sorted({
        R(1001, 1000), R(5, 4), R(3, 2), R(7, 4),
        R(2), R(9, 4), R(5, 2), R(3),
        R(k) - R(1, 3), R(k), R(k) + R(1, 3), R(k + 1)
    })
    for e in etas:
        js = {max(0, k - e.numerator // e.denominator)}
        if e.denominator == 1 and 2 <= e <= k:
            js.add(k - int(e) + 1)  # Other tied optimal branch.

        for jj in js:
            counts["configs"] += 1
            kk = (k - 1) * e + 1
            qq = (k - 1) * e / kk
            Qj = qq ** jj
            delta = Qj / (k * e)
            const = kk / k
            end = jj + ceil(k * e) + 2

            def values(x, y):
                if x <= jj:
                    r = qq ** x
                    h = R(k - 1, k) * r
                else:
                    z = (x - jj) * delta
                    r = max(R(0), Qj - z)
                    h = max(R(0), R(k - 1, k) * Qj - z)
                if y == 0:
                    return 1 - r, const - r - (e - 1) * h
                c = R(k - y, k - 1)
                return 1 - c * h, const - e * c * h

            tab = {
                (x, y): values(x, y)
                for x in range(end + 1)
                for y in range(k + 1)
            }

            assert tab[0, 0] == (0, 0)
            assert tab[0, k][0] == 1
            assert all(0 <= f <= 1 for f, H in tab.values())

            for x in range(end + 1):
                for y in range(k + 1):
                    for dx, dy in [(1, 0), (0, 1)]:
                        xx, yy = x + dx, y + dy
                        if xx > end or yy > k:
                            continue
                        df = tab[xx, yy][0] - tab[x, y][0]
                        dH = tab[xx, yy][1] - tab[x, y][1]
                        assert 0 <= df <= dH <= e * df
                        counts["edges"] += 1

                        for sx, sy in [(1, 0), (0, 1)]:
                            if xx + sx > end or yy + sy > k:
                                continue
                            df2 = (
                                tab[xx + sx, yy + sy][0]
                                - tab[x + sx, y + sy][0]
                            )
                            assert df >= df2
                            counts["DR"] += 1

                    if x + y <= k and y <= 1:
                        assert tab[x, y][1] == tab[x + y, 0][1]
                        counts["balanced"] += 1

            for t in range(k):
                df = tab[t + 1, 0][0] - tab[t, 0][0]
                assert df == (qq ** t / kk if t < jj else delta)
                assert (
                    tab[t, 1][0] - tab[t, 0][0]
                    == qq ** min(t, jj) / k
                )
                assert tab[t + 1, 0][1] == tab[t, 1][1]

            rho = min(
                1 - qq ** a * (1 - R(k - a, k) / e)
                for a in range(k)
            )
            assert tab[k, 0][0] == rho

            # Both actual error endpoints are attained.
            assert tab[0, 1][1] == tab[0, 1][0]
            assert (
                tab[0, 2][1] - tab[0, 1][1]
                == e * (tab[0, 2][0] - tab[0, 1][0])
            )

print(counts)
# configs=159, edges=111032, DR=207842, balanced=2441
