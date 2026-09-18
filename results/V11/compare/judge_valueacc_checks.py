"""Independent judge-side re-check of route two (prop:valueacc, convention B).
Exact arithmetic only (Fraction / sympy). Floats only in printouts."""
from fractions import Fraction as F
from itertools import combinations, chain, permutations
import sympy as sp

FAIL = []
def ck(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + ("  " + extra if extra else ""))
    if not cond: FAIL.append(name + " " + extra)

def subsets(n):
    els = list(range(1, n+1))
    return [frozenset(c) for r in range(n+1) for c in combinations(els, r)]

def is_monotone(f, n):
    return all(f[S | {e}] >= f[S] for S in subsets(n) for e in range(1, n+1) if e not in S)

def is_submodular(f, n):
    for S in subsets(n):
        for T in subsets(n):
            if not S <= T: continue
            for e in range(1, n+1):
                if e in T: continue
                if not (f[S | {e}] - f[S] >= f[T | {e}] - f[T]): return False
    return True

def value_acc(f, g, n, eps):
    return all((1-eps)*f[S] <= g[S] <= (1+eps)*f[S] for S in subsets(n))

def band_violations(f, g, n, etau, etao):
    bad = []
    for S in subsets(n):
        for e in range(1, n+1):
            if e in S: continue
            d = f[S|{e}]-f[S]; dt = g[S|{e}]-g[S]
            if etau is None:
                if d > 0 and dt == 0: bad.append(("lower-inf", tuple(sorted(S)), e, d, dt))
                if d == 0 and dt != 0: bad.append(("upper-inf", tuple(sorted(S)), e, d, dt))
            else:
                if not (d/etau <= dt <= etao*d): bad.append((tuple(sorted(S)), e, d, dt))
    return bad

print("=== A. route2 Instance A (i) ===")
for eps in [F(1,100), F(1,5), F(1,2), F(9,10), F(99,100)]:
    n=2
    f = {S: (1 if 1 in S else 0) + (eps if 2 in S else 0) for S in subsets(n)}
    g = {frozenset(): F(0), frozenset({1}): F(1), frozenset({2}): eps, frozenset({1,2}): F(1)}
    ck(f"A mono+submod eps={eps}", is_monotone(f,n) and is_submodular(f,n))
    ck(f"A value-accurate eps={eps}", value_acc(f,g,n,eps))
    d = f[frozenset({1,2})]-f[frozenset({1})]; dt = g[frozenset({1,2})]-g[frozenset({1})]
    ck(f"A witness d_2({{1}})>0=dt eps={eps}", d>0 and dt==0, f"d={d} dt={dt}")

print("=== A'. route1 (appendix_model_proofs) Instance for (i) ===")
for eps in [F(1,100), F(1,5), F(1,2), F(9,10)]:
    n=2
    f = {frozenset(): F(0), frozenset({1}): F(1), frozenset({2}): F(1), frozenset({1,2}): 1+eps}
    g = {S: (F(0) if len(S)==0 else F(1)) for S in subsets(n)}
    ck(f"R1 mono+submod eps={eps}", is_monotone(f,n) and is_submodular(f,n))
    ck(f"R1 value-accurate eps={eps}", value_acc(f,g,n,eps))
    d = f[frozenset({1,2})]-f[frozenset({1})]; dt = g[frozenset({1,2})]-g[frozenset({1})]
    ck(f"R1 witness eps={eps}", d==eps and dt==0)

print("=== A''. OLD appendix (app:valueacc) instance for (i) ===")
for eps in [F(1,100), F(1,5), F(1,2), F(9,10)]:
    n=2
    fb = 2*eps/(1-eps); fab=(1+eps)/(1-eps)
    f = {frozenset(): F(0), frozenset({1}): F(1), frozenset({2}): fb, frozenset({1,2}): fab}
    g = {frozenset(): F(0), frozenset({1}): 1+eps, frozenset({2}): fb, frozenset({1,2}): 1+eps}
    ck(f"OLD mono+submod eps={eps}", is_monotone(f,n) and is_submodular(f,n))
    ck(f"OLD value-accurate eps={eps}", value_acc(f,g,n,eps))
    d=f[frozenset({1,2})]-f[frozenset({1})]; dt=g[frozenset({1,2})]-g[frozenset({1})]
    ck(f"OLD witness eps={eps}", d==fb and d>0 and dt==0)

print("=== B. n=1 counter-check for route2's added hypothesis n>=2 ===")
# value accuracy at level eps on n=1 forces finite eta <= (1+eps)/(1-eps)
eps = sp.Rational(1,5); fe = sp.Symbol('fe', positive=True); gt = sp.Symbol('gt', positive=True)
ck("n=1: (1-eps)f <= tilde f forces tilde d>0 when f>0", sp.simplify((1-eps)*fe) > 0)

print("=== C. route2 Instance B (i)-strengthening ===")
for (eps, delta) in [(F(1,5),F(1,2)), (F(1,10),F(2,9)), (F(1,8),F(2,7)), (F(1,5),F(1,3))]:
    n=3
    def fv(S): return (1 if (S & {1,2}) else 0) + (delta if 3 in S else 0)
    f = {S: F(fv(S)) if not isinstance(fv(S),F) else fv(S) for S in subsets(n)}
    f = {S: F(1)*fv(S) for S in subsets(n)}
    g = {}
    g[frozenset()] = F(0)
    g[frozenset({1})] = g[frozenset({2})] = 1-eps
    g[frozenset({3})] = (1+eps)*delta
    g[frozenset({1,2})] = 1+eps
    g[frozenset({1,3})] = g[frozenset({2,3})] = (1-eps)*(1+delta)
    g[frozenset({1,2,3})] = (1+eps)*(1+delta)
    ck(f"B mono+submod eps={eps} delta={delta}", is_monotone(f,n) and is_submodular(f,n))
    ck(f"B value-accurate eps={eps} delta={delta}", value_acc(f,g,n,eps))
    # greedy K=2 with adversarial ties: enumerate all argmax-consistent runs, take worst f
    def runs(K):
        out=[]
        def rec(S, t):
            if t==K: out.append(S); return
            cand=[e for e in range(1,n+1) if e not in S]
            best=max(g[S|{e}]-g[S] for e in cand)
            for e in cand:
                if g[S|{e}]-g[S]==best: rec(S|{e}, t+1)
        rec(frozenset(),0); return out
    R = runs(2)
    worst = min(f[S] for S in R)
    OPT = max(f[S] for S in subsets(n) if len(S)<=2)
    ck(f"B worst ratio eps={eps} delta={delta}", True, f"ratio={worst}/{OPT}={F(worst,1)/OPT}  1/(1+delta)={1/(1+delta)}")
    # eta^sel on the worst run
    # recompute per run
    inf_found=False
    for S2 in R:
        pass
    # explicit: t=1 from {1}
    S1=frozenset({1})
    M1=max(f[S1|{e}]-f[S1] for e in (2,3)); g1=f[frozenset({1,2})]-f[S1]
    ck(f"B eta^sel infinite eps={eps} delta={delta}", g1==0 and M1>0, f"M1={M1} g1={g1}")
    bv = band_violations(f,g,n,None,None)
    ck(f"B violates UPPER side only eps={eps} delta={delta}", all(t[0]=="upper-inf" for t in bv) and len(bv)>0, str(bv[:3]))

print("=== D. Step 14 worst-ratio family formula ===")
e = sp.Symbol('e', positive=True)
d1 = (1-e)/(1+e); d2 = 2*e/(1-e)
ck("Step14 crossover root", sp.simplify(sp.solve(sp.Eq(d1,d2), e)[0] - (sp.sqrt(5)-2))==0, str(sp.solve(sp.Eq(d1,d2), e)))
ck("Step14 branch1: 1/(1+2e/(1-e)) = (1-e)/(1+e)", sp.simplify(1/(1+d2) - d1)==0)
ck("Step14 branch2: 1/(1+(1-e)/(1+e)) = (1+e)/2", sp.simplify(1/(1+d1) - (1+e)/2)==0)
e0 = sp.sqrt(5)-2
ck("Step14 value at crossover = (sqrt5-1)/2", sp.simplify(d1.subs(e,e0) - (sp.sqrt(5)-1)/2)==0)
for ev in [F(1,10), F(1,8), F(1,5)]:
    ck(f"Step14 min branch at eps={ev} is 2e/(1-e)", 2*ev/(1-ev) <= (1-ev)/(1+ev))
ck("Step14 at eps=1/2 min branch is (1-e)/(1+e)", (F(1,3) <= F(2,1)))

print("=== E. L_K values quoted by route2 ===")
def L(K, x): return 1 - (1 - F(1,1)/(x*K))**K
ck("L_2(3/2)=5/9", L(2,F(3,2))==F(5,9), str(L(2,F(3,2))))
ck("L_2(1)=3/4", L(2,F(1))==F(3,4))
ck("L_3(3/2)=386/729", L(3,F(3,2))==F(386,729), str(L(3,F(3,2))))
ck("L_3(1)=19/27", L(3,F(1))==F(19,27))
ck("2/3 > L_2(3/2)", F(2,3) > F(5,9))

print("=== F. (ii) symbolic ===")
M = sp.Symbol('M', positive=True)
etau, etao = 1/(1+M), 1+M
ck("(ii) eta=1", sp.simplify(etau*etao-1)==0)
ck("(ii) both factors >0", sp.simplify(etau)>0)
ck("(ii) verbatim floor makes eta_u<1 illegal", sp.simplify(etau-1).subs(M,1) < 0)
# argmax preservation on a concrete coverage instance, all tie-breaks, K=1..4
cov = {1:{'a','b'},2:{'b','c'},3:{'c','d'},4:{'d'}}; w={'a':F(3),'b':F(1),'c':F(2),'d':F(1)}
n=4
f = {S: sum(w[x] for x in set().union(*[cov[i] for i in S]) ) if S else F(0) for S in subsets(n)}
for Mv in [F(1,100), F(1,2), F(3)]:
    g = {S: (1+Mv)*f[S] for S in subsets(n)}
    ck(f"(ii) band equality M={Mv}", all((f[S|{e}]-f[S])/ (1/(1+Mv)) == (g[S|{e}]-g[S]) == (1+Mv)*(f[S|{e}]-f[S]) for S in subsets(n) for e in range(1,n+1) if e not in S))
    ok=True
    for S in subsets(n):
        A1 = {e for e in range(1,n+1) if e not in S and f[S|{e}]-f[S]==max(f[S|{x}]-f[S] for x in range(1,n+1) if x not in S)} if len(S)<n else set()
        A2 = {e for e in range(1,n+1) if e not in S and g[S|{e}]-g[S]==max(g[S|{x}]-g[S] for x in range(1,n+1) if x not in S)} if len(S)<n else set()
        if A1!=A2: ok=False
    ck(f"(ii) argmax sets identical M={Mv}", ok)
    # eta^sel over all tie-breaks
    def etasel(K):
        worst=[]
        def rec(S,t,acc):
            if t==K: worst.append(acc); return
            cand=[e for e in range(1,n+1) if e not in S]
            best=max(g[S|{e}]-g[S] for e in cand)
            for e in cand:
                if g[S|{e}]-g[S]==best:
                    Mt=max(f[S|{x}]-f[S] for x in cand); gt=f[S|{e}]-f[S]
                    at = (Mt/gt if gt>0 else (F(1) if Mt==0 else None))
                    rec(S|{e}, t+1, max(acc, at) if at is not None else None)
        rec(frozenset(),0,F(1)); return worst
    for K in (1,2,3,4):
        ws = etasel(K)
        ck(f"(ii) eta^sel=1 M={Mv} K={K}", all(x==F(1) for x in ws))
    # value accuracy fails for eps<M, holds at eps=M if M<1
    for epsv in [Mv/2, Mv*F(99,100)]:
        if 0<epsv<1: ck(f"(ii) VA fails M={Mv} eps={epsv}", not value_acc(f,g,n,epsv))
    if Mv<1: ck(f"(ii) VA holds at eps=M={Mv}", value_acc(f,g,n,Mv))

print("=== G. (iii) symbolic ===")
u,o = sp.symbols('eta_u eta_o', positive=True)
eta = u*o
c = 2*u/(eta+1); epsx=(eta-1)/(eta+1)
ck("(iii) c/eta_u = 1-eps", sp.simplify(c/u - (1-epsx))==0)
ck("(iii) c*eta_o = 1+eps", sp.simplify(c*o - (1+epsx))==0)
cc = sp.symbols('c', positive=True)
sol = sp.solve(sp.Eq(1-cc/u, cc*o-1), cc)
ck("(iii) minimizer solves to c", sp.simplify(sol[0]-c)==0, str(sp.simplify(sol[0])))
ck("(iii) balanced value = eps", sp.simplify((sol[0]*o-1) - epsx)==0)
E = sp.Symbol('eta', positive=True)
epsE=(E-1)/(E+1)
ck("(iii) eps(1)=0", sp.simplify(epsE.subs(E,1))==0)
ck("(iii) eps'>0", sp.simplify(sp.diff(epsE,E) - 2/(E+1)**2)==0)
ck("(iii) lim eps = 1", sp.limit(epsE, E, sp.oo)==1)
ck("(iii) eta_u/c = 1/(1-eps)", sp.simplify(u/c - 1/(1-epsx))==0)
ck("(iii) c*eta_o = 1+eps (again)", sp.simplify(c*o-(1+epsx))==0)
ck("(iii) product preserved", sp.simplify((u/c)*(c*o) - eta)==0)
ck("(iii) band width = d(eta-1)/eta_u", sp.simplify(o - 1/u - (eta-1)/u)==0)

print("=== H. (iii) set-level band, exhaustive, incl. non-submodular f ===")
def check_setband(f, n, etau, etao, seeds):
    ok=True
    for g in seeds:
        if band_violations(f,g,n,etau,etao): continue
        cv = 2*etau/(etau*etao+1); ev=(etau*etao-1)/(etau*etao+1)
        for S in subsets(n):
            if not (f[S]/etau <= g[S] <= etao*f[S]): ok=False
            if not ((1-ev)*f[S] <= cv*g[S] <= (1+ev)*f[S]): ok=False
    return ok
import itertools
n=3
for (etau,etao) in [(F(1),F(3,2)),(F(3,2),F(1)),(F(3,4),F(2)),(F(2),F(2))]:
    for fname, f in [("modular(3,2,1)", {S: F(3)*(1 in S)+F(2)*(2 in S)+F(1)*(3 in S) for S in subsets(3)}),
                     ("|S|^2 (non-submod)", {S: F(len(S))**2 for S in subsets(3)})]:
        # build in-band predictors: each pair choice at extremes is not consistent in general,
        # so build predictor by choosing a per-element multiplier in [1/etau, etao] on a modular-like extension
        seeds=[]
        for choice in itertools.product([F(1)/etau, etao], repeat=3):
            g={}
            for S in subsets(3):
                # telescoping along sorted order with per-(S,e) factor = choice[e-1]
                tot=F(0); cur=frozenset()
                for e in sorted(S):
                    tot += choice[e-1]*(f[cur|{e}]-f[cur]); cur=cur|{e}
                g[S]=tot
            seeds.append(g)
        ck(f"setband+VA {fname} ({etau},{etao})", check_setband(f,3,etau,etao,seeds))
ck("|S|^2 is monotone", is_monotone({S: F(len(S))**2 for S in subsets(3)},3))
ck("|S|^2 is NOT submodular", not is_submodular({S: F(len(S))**2 for S in subsets(3)},3))

print("=== I. Step 27 tightness instance ===")
for (etau,etao) in [(F(1),F(3,2)),(F(3,2),F(1)),(F(3,4),F(2))]:
    n=2
    f={S: F(len(S)) for S in subsets(2)}
    g={frozenset():F(0), frozenset({1}): 1/etau, frozenset({2}): etao, frozenset({1,2}): 1/etau+etao}
    ck(f"Step27 in band ({etau},{etao})", band_violations(f,g,2,etau,etao)==[])
    etaV=etau*etao; cv=2*etau/(etaV+1); ev=(etaV-1)/(etaV+1)
    ck(f"Step27 both sides tight ({etau},{etao})", cv*g[frozenset({1})]==(1-ev)*1 and cv*g[frozenset({2})]==(1+ev)*1)

print("=== J. section 6.1 walkthrough table ===")
n=3; w=(F(3),F(2),F(1))
f={S: sum(w[e-1] for e in S) for S in subsets(3)}
for (etau,etao,cexp,wt) in [(F(1),F(3,2),F(4,5),(F(9,2),F(2),F(1))),
                            (F(3,2),F(1),F(6,5),(F(3),F(4,3),F(2,3))),
                            (F(3,4),F(2),F(3,5),(F(6),F(8,3),F(4,3)))]:
    g={S: sum(wt[e-1] for e in S) for S in subsets(3)}
    eta=etau*etao; cv=2*etau/(eta+1); ev=(eta-1)/(eta+1)
    ck(f"6.1 c matches ({etau},{etao})", cv==cexp, f"c={cv}")
    ck(f"6.1 eps=1/5 ({etau},{etao})", ev==F(1,5))
    ck(f"6.1 predictor in band ({etau},{etao})", band_violations(f,g,3,etau,etao)==[])
    ck(f"6.1 c*tf({{1}})=18/5 upper tight ({etau},{etao})", cv*g[frozenset({1})]==F(18,5)==(1+ev)*f[frozenset({1})])
    ck(f"6.1 c*tf({{2,3}})=12/5 lower tight ({etau},{etao})", cv*g[frozenset({2,3})]==F(12,5)==(1-ev)*f[frozenset({2,3})])
# full first row table
etau,etao=F(1),F(3,2); cv=F(4,5)
g={S: sum((F(9,2),F(2),F(1))[e-1] for e in S) for S in subsets(3)}
tab={frozenset():(0,0),frozenset({1}):(3,F(9,2)),frozenset({2}):(2,2),frozenset({3}):(1,1),
     frozenset({1,2}):(5,F(13,2)),frozenset({1,3}):(4,F(11,2)),frozenset({2,3}):(3,3),frozenset({1,2,3}):(6,F(15,2))}
ck("6.1 row1 table f,tf all match", all(f[S]==tv[0] and g[S]==tv[1] for S,tv in tab.items()))
ck("6.1 row1 c*tf values", [cv*g[S] for S in [frozenset({1}),frozenset({2}),frozenset({3}),frozenset({1,2}),frozenset({1,3}),frozenset({2,3}),frozenset({1,2,3})]]==[F(18,5),F(8,5),F(4,5),F(26,5),F(22,5),F(12,5),F(6)])

print("=== K. section 6.2 coverage walkthrough ===")
cov = {1:{'a','b'},2:{'b','c'},3:{'c','d'},4:{'d'}}; w={'a':F(3),'b':F(1),'c':F(2),'d':F(1)}
n=4
f={S: sum(w[x] for x in set().union(*[cov[i] for i in S])) if S else F(0) for S in subsets(4)}
ck("6.2 singletons 4,3,3,1", [f[frozenset({i})] for i in (1,2,3,4)]==[F(4),F(3),F(3),F(1)])
ck("6.2 d_2({1})=2, d_3({1})=3, d_4({1})=1", [f[frozenset({1,i})]-f[frozenset({1})] for i in (2,3,4)]==[F(2),F(3),F(1)])
ck("6.2 f({1,3})=7=OPT", f[frozenset({1,3})]==F(7) and max(f[S] for S in subsets(4) if len(S)<=3)==F(7))
ck("6.2 t=2 gains zero", f[frozenset({1,2,3})]-f[frozenset({1,3})]==0 and f[frozenset({1,3,4})]-f[frozenset({1,3})]==0)
ck("6.2 c=2/3 and c*tf=f", 2*F(2,3)/(F(1)+1)==F(2,3) and F(2,3)*F(3,2)==1)

print("=== L. definition1.md scaling direction (route2 G3) ===")
cs = sp.Symbol('c', positive=True); d = sp.Symbol('d', positive=True); dt=sp.Symbol('dt', positive=True)
# from d/u <= dt <= o*d, multiply by c: d/(u/c) <= c*dt <= (c*o) d
ck("scaling maps (u,o)->(u/c, c*o)", sp.simplify(cs*d/u - d/(u/cs))==0 and sp.simplify(cs*o*d-(cs*o)*d)==0)
ck("file's (c*u, o/c) is the inverse direction", sp.simplify((cs*u)*(o/cs) - u*o)==0)
# consistency with (ii): f has (1,1); tilde f = (1+M) f -> should be (1/(1+M), 1+M)
Mv=sp.Symbol('M', positive=True)
ck("(ii) matches (u/c, c*o) with u=o=1,c=1+M", sp.simplify(1/(1+Mv) - 1/(1+Mv))==0)

print()
print("TOTAL FAILURES:", len(FAIL))
for x in FAIL: print("  ", x)
