"""V11 judge (criterion B) for cor:limit / ledger T9: route-one vs route-two cross checks.

All decisions use fractions.Fraction or sympy; mpmath (60 digits) only where a transcendental
bound is compared. Run: python3 results/V11/compare/judge_limit_checks.py
Expected tail line: FAILURES: 0
"""
from fractions import Fraction as F
import math, sympy as sp

ETAS = [F(1), F(11,10), F(5,4), F(3,2), F(2), F(7,3), F(5,2), F(3), F(7,2), F(4),
        F(9,2), F(5), F(6), F(17,2), F(10), F(100), F(1000)]
KMAX = 60
fails = []
def rec(name, ok, info=""):
    print(("PASS " if ok else "FAIL ") + name + ("  " + info if info else ""))
    if not ok: fails.append((name, info))

def q_k1(K, eta):
    k1 = (K-1)*eta + 1
    return (K-1)*eta/k1, k1
def h(K, j, eta):
    q,_ = q_k1(K, eta)
    c = 1 - F(K-j, K)/eta
    return q**j * c
def V(K, j, eta):
    return 1 - h(K, j, eta)

# ---- C-A: min over {0..K-1} equals min over {0..K}  (route1 range vs route2 range)
ok = True; bad = None
for eta in ETAS:
    for K in range(1, KMAX+1):
        a = min(V(K,j,eta) for j in range(0, K))
        b = min(V(K,j,eta) for j in range(0, K+1))
        if a != b:
            ok = False; bad = (eta, K, a, b); break
    if not ok: break
rec("A. min_{0<=j<=K-1} V_j == min_{0<=j<=K} V_j (paper range vs route2 range)", ok, str(bad))

# ---- C-B: argmax agreement: route1 j=max(0,K-floor(eta)), route2 j*=max(0,K-ceil(eta)+1)
ok = True; bad=None
for eta in ETAS:
    fl = math.floor(eta); ce = math.ceil(eta)
    for K in range(1, KMAX+1):
        j1 = max(0, K-fl); j2 = max(0, K-ce+1)
        M = max(h(K,j,eta) for j in range(0,K+1))
        v1 = h(K, min(j1,K), eta); v2 = h(K, j2, eta)
        if v1 != M or v2 != M:
            ok=False; bad=(eta,K,j1,j2,M,v1,v2); break
    if not ok: break
rec("B. both route1 j=K-floor(eta) and route2 j*=K-ceil(eta)+1 attain max h", ok, str(bad))

# ---- C-C: route2 Step 4 difference identity, symbolic
K,eta,j = sp.symbols('K eta j', positive=True)
k1s = (K-1)*eta+1; qs = (K-1)*eta/k1s
hs = lambda jj: qs**jj*(1-(K-jj)/(K*eta))
# divide by q^{j-1} first: sympy does not combine q**j - q**(j-1) with a symbolic exponent
lhs = sp.simplify((hs(j)-hs(j-1))/qs**(j-1))
rhs = (K-eta+1-j)/(K*eta*k1s)
resid = sp.simplify(sp.expand(lhs-rhs))
ok_int = True; bad_int = None
for Kv in range(2, 9):
    for ev in [F(1), F(3,2), F(7,3), F(5), F(10)]:
        for jv in range(1, Kv+1):
            if h(Kv,jv,ev)-h(Kv,jv-1,ev) != (((Kv-1)*ev/((Kv-1)*ev+1))**(jv-1))*(Kv-ev+1-jv)/(Kv*ev*((Kv-1)*ev+1)):
                ok_int = False; bad_int = (Kv, ev, jv)
rec("C. Step 4 identity h(j)-h(j-1) = q^{j-1}(K-eta+1-j)/(K eta k1)", resid==0 and ok_int, str(bad_int))

# ---- C-D: route2 Step 8 closed form Lambda(K) == max_j h, for K >= ceil(eta)
ok=True; bad=None
for eta in ETAS:
    p = math.ceil(eta)
    for K in range(p, KMAX+1):
        q,_ = q_k1(K,eta)
        Lam = q**(K-p+1) * (1 - F(p-1,K)/eta)
        M = max(h(K,jj,eta) for jj in range(0,K+1))
        if Lam != M: ok=False; bad=(eta,K,Lam,M); break
    if not ok: break
rec("D. Step 8 closed form Lambda(K) == max_j h_K(j) for K>=ceil(eta)", ok, str(bad))

# ---- C-E: route1 P(K) == route2 Lambda(K) for K >= floor(eta)>=1 (incl. integer eta)
ok=True; bad=None
for eta in ETAS:
    m = math.floor(eta); p = math.ceil(eta)
    for K in range(max(1,m), KMAX+1):
        q,_ = q_k1(K,eta)
        P = q**(K-m)*(1-F(m,K)/eta)
        Lam = q**(K-p+1)*(1-F(p-1,K)/eta)
        if P != Lam: ok=False; bad=(eta,K,P,Lam); break
    if not ok: break
rec("E. route1 P(K)=q^{K-m}(1-m/(K eta)) == route2 Lambda(K)", ok, str(bad))

# ---- C-F: derivative identities of route1 and route2 agree (symbolic)
Ks, es, ms = sp.symbols('K eta m', positive=True)
x = (Ks-1)*es+1
d_route1 = sp.log(1-1/x) + (Ks-ms)/((Ks-1)*x) + ms/(Ks*(Ks*es-ms))
# route2 in t; substitute t = x, s = m, u = K - s
t = sp.symbols('t', positive=True)
Kt = (t-1)/es + 1
u = Kt - ms
d_route2_t = sp.Rational(1,1)/es*sp.log(1-1/t) + u/(t*(t-1)) + ms/((t+es-1-ms)*(t+es-1))
# dlogP/dK = eta * dlnLambda/dt
diff = sp.simplify(sp.expand(d_route1 - es*d_route2_t.subs(t, x)))
rec("F. route1 dlogP/dK identity == eta * route2 dlnLambda/dt identity", sp.simplify(diff)==0, str(diff))

# ---- C-G: route2 Step 9 rearranged identity (the boxed one), symbolic minus series term
s_, = sp.symbols('s', nonnegative=True),
u2 = (t-1)/es + 1 - s_
lnLam = u2*sp.log(1-1/t) + sp.log(t+es-1-s_) - sp.log(t+es-1)
dd = sp.diff(lnLam, t)
boxed = -( -sp.log(1-1/t) - 1/t )/es + (1-s_)/(t*(t-1)) + s_/((t+es-1-s_)*(t+es-1))
rec("G. Step 9 boxed identity (with Sigma = -ln(1-1/t)-1/t)", sp.simplify(sp.expand(dd-boxed))==0)

# ---- C-H: route2 Step 9 sufficient condition K(2eta-1)/(2eta) >= s for all K>=ceil(eta)
ok=True; bad=None
for eta in ETAS:
    p = math.ceil(eta); s = p-1
    for K in range(p, KMAX+1):
        if not (K*(2*eta-1) >= 2*eta*s): ok=False; bad=(eta,K,s); break
    if not ok: break
rec("H. Step 9.4 sufficient condition K(2eta-1)/(2eta) >= s", ok, str(bad))

# ---- C-I: Lambda strictly increasing (exact) for K >= ceil(eta)
ok=True; bad=None
for eta in ETAS:
    p = math.ceil(eta)
    for K in range(p, KMAX):
        f1 = max(h(K,jj,eta) for jj in range(0,K+1))
        f2 = max(h(K+1,jj,eta) for jj in range(0,K+2))
        if not f2 > f1: ok=False; bad=(eta,K,f1,f2); break
    if not ok: break
rec("I. Lambda(K+1) > Lambda(K) exact for K>=ceil(eta)", ok, str(bad))

# ---- C-J: plateau iff K <= floor(eta); and rho non-increasing, strict from K>=floor(eta)
ok1=ok2=ok3=True; b1=b2=b3=None
for eta in ETAS:
    fl = math.floor(eta)
    rho = {K: min(V(K,jj,eta) for jj in range(0,K)) for K in range(1,KMAX+1)}
    for K in range(1,KMAX+1):
        plateau = (rho[K] == 1/eta)
        if plateau != (K <= fl): ok1=False; b1=(eta,K,rho[K]); break
    for K in range(1,KMAX):
        if rho[K+1] > rho[K]: ok2=False; b2=(eta,K); break
        if K >= fl and not rho[K+1] < rho[K]: ok3=False; b3=(eta,K,rho[K],rho[K+1]); break
rec("J1. plateau rho_K=1/eta  iff  K<=floor(eta)", ok1, str(b1))
rec("J2. rho_K non-increasing in K", ok2, str(b2))
rec("J3. rho_{K+1} < rho_K for all K >= floor(eta)", ok3, str(b3))

# ---- C-K: edge case eta=1, K=1 -> 2 (route2 Step 9 needs t>1)
eta=F(1)
r1 = min(V(1,jj,eta) for jj in range(0,1)); r2 = min(V(2,jj,eta) for jj in range(0,2))
rec("K. eta=1: rho_1=1 > rho_2=3/4 (case outside Step 9 domain t>1)", r1==1 and r2==F(3,4), f"rho1={r1} rho2={r2}")

# ---- C-L: uniform bound h_K(j) <= e^{-1/eta}  (mpmath high precision)
import mpmath as mp
mp.mp.dps = 60
ok=True; bad=None; worst=None
for eta in ETAS:
    e = mp.mpf(eta.numerator)/mp.mpf(eta.denominator)
    bound = mp.e**(-1/e)
    for K in range(1,KMAX+1):
        for jj in range(0,K+1):
            val = mp.mpf(h(K,jj,eta).numerator)/mp.mpf(h(K,jj,eta).denominator)
            sl = bound-val
            if worst is None or sl < worst[0]: worst=(sl,eta,K,jj)
            if sl < 0: ok=False; bad=(eta,K,jj,val,bound)
rec("L. h_K(j) <= e^{-1/eta} for all K<=60, all j", ok, f"min slack {mp.nstr(worst[0],6)} at eta={worst[1]},K={worst[2]},j={worst[3]}")

# ---- C-M: rho_K <= U_K and rho_K <= V_{K-1} < U_K (paper's route)
ok1=ok2=True; b=None
for eta in ETAS:
    for K in range(2,KMAX+1):
        q,_=q_k1(K,eta)
        U = 1-q**K
        rho = min(V(K,jj,eta) for jj in range(0,K))
        if rho > U: ok1=False; b=(eta,K)
        if eta>1 and not (V(K,K-1,eta) < U): ok2=False; b=(eta,K)
rec("M1. rho_K <= U_K", ok1, str(b))
rec("M2. V_{K-1} < U_K for eta>1 (paper's justification of the upper bound)", ok2, str(b))

# ---- C-N: route2 numeric table 3.1 spot values (eta=3/2)
eta=F(3,2)
tab = {1:F(2,3),2:F(3,5),3:F(9,16),4:F(1447,2662)}
ok=all(min(V(K,jj,eta) for jj in range(0,K))==v for K,v in tab.items())
rec("N. route2 table 3.1 rho_K values (eta=3/2, K=1..4)", ok,
    str({K: str(min(V(K,jj,eta) for jj in range(0,K))) for K in tab}))

# ---- C-O: L_K strictly decreasing, L_K > 1-e^{-1/eta}
def L(K,eta): return 1-(1-1/(eta*K))**K
ok1=ok2=True; b=None
for eta in ETAS:
    e = mp.mpf(eta.numerator)/mp.mpf(eta.denominator); lim = 1-mp.e**(-1/e)
    for K in range(1,KMAX):
        if not L(K+1,eta) < L(K,eta): ok1=False; b=(eta,K)
        lv = L(K,eta)
        if not mp.mpf(lv.numerator)/mp.mpf(lv.denominator) > lim: ok2=False; b=(eta,K)
rec("O1. L_K strictly decreasing", ok1, str(b))
rec("O2. L_K > 1-e^{-1/eta}", ok2, str(b))

# ---- C-P: route1's 1/K coefficient c(eta) (not in route2) -- sanity numeric
eta=F(3,2); e=mp.mpf(1.5)
K=4000
q,_=q_k1(K,eta); m=1
rho = min(V(K,jj,eta) for jj in range(0,K))
val = mp.mpf(rho.numerator)/mp.mpf(rho.denominator)
c_pred = mp.e**(-1/e)*(2*e-1)/(2*e**2)
rec("P. route1 c(eta) consistent with route2 numbers (eta=3/2, K=4000)",
    abs(K*(val-(1-mp.e**(-1/e))) - c_pred) < mp.mpf('1e-3'),
    f"K*(rho-lim)={mp.nstr(K*(val-(1-mp.e**(-1/e))),8)} c={mp.nstr(c_pred,8)}")

# ---- C-Q: route1 prose claims (uniqueness of the minimizing index; first drop; tail bound)
ok=True; bad=None
for eta in ETAS:
    if eta.denominator==1: continue
    fl=math.floor(eta)
    for Kv in range(max(1,fl), 41):
        vals=[V(Kv,jj,eta) for jj in range(0,Kv)]
        m_=min(vals)
        if vals.count(m_)!=1 or vals.index(m_)!=max(0,Kv-fl): ok=False; bad=(eta,Kv); break
    if not ok: break
rec("Q1. route1: argmin unique and equal to K-floor(eta) at noninteger eta", ok, str(bad))

ok=True; bad=None
for eta in ETAS:
    if eta.denominator!=1: continue
    m_=int(eta)
    for Kv in range(m_+1, 41):
        vals=[V(Kv,jj,eta) for jj in range(0,Kv)]
        mm=min(vals); idx=[i for i,v in enumerate(vals) if v==mm]
        want = [Kv-m_, Kv-m_+1] if Kv-m_+1<=Kv-1 else [Kv-m_]
        if idx!=want: ok=False; bad=(eta,Kv,idx,want); break
    if not ok: break
rec("Q2. route1: at integer eta the two adjacent endpoints both minimize", ok, str(bad))

ok=True; bad=None
for eta in ETAS:
    fl=math.floor(eta)
    if fl<1: continue
    Kv=fl+1; k1v=(Kv-1)*eta+1
    drop=(Kv-eta)/(Kv*eta*k1v)
    actual=min(V(fl,jj,eta) for jj in range(0,fl))-min(V(Kv,jj,eta) for jj in range(0,Kv))
    if not (drop>0 and actual>=drop): ok=False; bad=(eta,drop,actual); break
rec("Q3. route1: first drop off the plateau (K-eta)/(K eta k1) is a valid lower bound", ok, str(bad))

ok=True; bad=None
for xv in [mp.mpf('1.0001'),mp.mpf('1.01'),mp.mpf('1.5'),mp.mpf(2),mp.mpf(3),mp.mpf(10),mp.mpf(100),mp.mpf('1e4'),mp.mpf('1e8')]:
    val=1/xv+1/(2*xv**2)+1/(3*xv**2*(xv-1))+mp.log(1-1/xv)
    if val<0: ok=False; bad=(xv,val)
rec("Q4. route1 tail bound -log(1-1/x) <= 1/x+1/(2x^2)+1/(3x^2(x-1)), x>1 (mpmath 60 digits)", ok, str(bad))

print("\nFAILURES:", len(fails))
for f_ in fails: print("  ", f_)
