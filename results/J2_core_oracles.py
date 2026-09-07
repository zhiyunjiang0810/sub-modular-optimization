#!/usr/bin/env python3
"""J2 independent review oracles. Original code/ files are never modified.

Run from project root:
  python3 results/J2_core_oracles.py
Dependencies: sympy, numpy, scipy. Writes J2_core_oracles.json.

[VERIFIED-SYMBOLIC] identifies algebraic identities, with sign/domain arguments
spelled out in J2_hardness_repair.tex and J2_review.md. Numerical LP checks are
finite support, never a claim of a computer-verified proof for all ground sets.
"""
from collections import Counter
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import json
import math
import time

import numpy as np
import sympy as sp
from scipy.optimize import linprog, brentq
from scipy.sparse import coo_matrix

HERE = Path(__file__).resolve().parent
RESULTS = {}


def symbolic_core():
    checks = {}

    def zero(name, expr):
        residue = sp.factor(sp.cancel(sp.together(sp.powsimp(expr, force=True))))
        checks[name] = str(residue)
        assert residue == 0, (name, residue)

    u, o = sp.symbols('eta_u eta_o', positive=True)
    d, g, h, P, Q, R = sp.symbols('d g h P Q R', real=True)
    # At S, selected true gain d, optimum-element true gain g; after selecting
    # e, remaining optimum gain h. The other true edge is d+h-g. Predictor
    # gains at S are P,Q; the edge after e is R, and the other is P+R-Q.
    zero('R6 pred nonnegative-slack identity',
         d - g/(u*o) - ((o*d-P)/o + (P-Q)/o + (u*Q-g)/(u*o)))
    zero('R6 cons nonnegative-slack identity',
         (1-1/(u*o))*h-g+d -
         ((o*(d+h-g)-(P+R-Q))/o + (P-Q)/o + (u*R-h)/(u*o)))
    zero('R6 selected-optimum case c: cons',
         ((1-1/(u*o))*h-g+d).subs({g:d, h:0}))
    zero('R6 selected-optimum case c: pred slack',
         (d-g/(u*o)).subs(g,d)-d*(1-1/(u*o)))
    # Coverage telescoping has an arbitrary number of terms; verify the base
    # and the induction increment in symbols instead of enumerating that length.
    sumg, H0, Hm, Hnext, fopt, gnext = sp.symbols('sumg H0 Hm Hnext fopt gnext')
    zero('R6 coverage telescope core',
         sumg+H0-fopt - ((Hm-fopt) + sumg-(Hm-H0)))
    zero('R6 coverage induction increment',
         (sumg+gnext-(Hnext-H0))-(sumg-(Hm-H0))-(gnext-(Hnext-Hm)))

    K, v, eta = sp.symbols('K v eta', positive=True)
    k1=(K-1)*eta+1
    # Literal numerator printed at t=j, with v=K-j.
    zero('dual t=j printed numerator', K*eta*(eta-1)*(v+1-eta)
         - k1*(eta-v) - (v-1)*eta*k1 + (eta-1)**2*(K*eta-v))
    zero('dual t=j middle-terms grouping',
         -k1*(eta-v)-(v-1)*eta*k1 + k1*v*(eta-1))

    # Hardness: H=sqrt(theta)*F. Thus G/H edge ratios are the actual
    # G/F ratios divided by sqrt(theta). Use p=a^x as a free positive symbol.
    a,p = sp.symbols('a p', positive=True)
    y,tau = sp.symbols('y tau', integer=True, nonnegative=True)
    th=1/(K*(1-a))
    H=1-p*(1-y/K)
    Hx=1-a*p*(1-y/K)
    Hy=1-p*(1-(y+1)/K)
    Gb=1-p*a**y
    Gbx=1-a*p*a**y
    Gby=1-p*a**(y+1)
    Ge=1-p*a**tau*(K-y)/(K-tau)
    Gex=1-a*p*a**tau*(K-y)/(K-tau)
    Gey=1-p*a**tau*(K-y-1)/(K-tau)
    A=a**tau*K/(K-tau)
    B=a**(1-tau)
    zero('hardness balanced x-edge ratio', (Gbx-Gb)/(Hx-H)-a**y*K/(K-y))
    zero('hardness balanced y-edge ratio', (Gby-Gb)/(Hy-H)-a**y/th)
    zero('hardness outside x-edge ratio', (Gex-Ge)/(Hx-H)-A)
    zero('hardness outside y-edge ratio', (Gey-Ge)/(Hy-H)-A)
    zero('hardness branch junction y=tau', Gb.subs(y,tau)-Ge.subs(y,tau))
    zero('hardness y=K x-edge zero', (Gex-Ge).subs(y,K))
    zero('hardness true CC second difference',
         ((1-a*a*p*(1-y/K))-2*Hx+H) + p*(1-a)**2*(1-y/K))
    zero('hardness true CY second difference',
         ((1-a*p*(1-(y+1)/K))-Hx-Hy+H) + p*(1-a)/K)
    zero('hardness true YY second difference',
         (1-p*(1-(y+2)/K))-2*Hy+H)
    zero('hardness exact scalar product', th*A*B - (th*K-1)/(K-tau))
    zero('hardness smaller inflation AB-1', A*B-1-(tau-1/th)/(K-tau))
    theta=sp.symbols('theta',positive=True)
    zero('hardness balanced x-ratio monotonic increment',
         (1-1/(theta*K))*(K-y)/(K-y-1)-1
         -((theta-1)*K+y)/(theta*K*(K-y-1)))
    theta_new=(eta*(K-tau)+1)/K
    zero('hardness new calibration', (theta_new*K-1)/(K-tau)-eta)
    zero('hardness new contraction denominator',
         1/(theta_new*K)-1/(eta*(K-tau)+1))
    z=sp.symbols('z',positive=True)
    delta_eff=(tau-1/eta)/(K-tau)
    zero('hardness effective-inflation limit',
         sp.limit(delta_eff.subs(K,1/z)/z,z,0,dir='+')-(tau-1/eta))
    log_lim=sp.limit(sp.log(1-1/(eta*(1/z-tau)+1))/z,z,0,dir='+')
    zero('hardness strengthened bound logarithmic limit', log_lim+1/eta)
    return {'status':'VERIFIED-SYMBOLIC','identities':checks,'count':len(checks)}


def dual_literal_checks():
    cases=0
    for K in range(2,18):
        for j in range(K):
            lo=K-j
            for e in (F(lo),F(2*lo+1,2),F(lo+1)):
                k1=(K-1)*e+1
                q=(K-1)*e/k1
                M=K*e-(K-j)
                S=[F(0)]*(K+1)
                P=[F(0)]*(K+1)
                C=[F(0)]*(K+1)
                if j==0:
                    S[0]=1/e
                else:
                    S[0]=q**(j-1)*M/(K*k1)
                    for t in range(1,j):S[t]=q**(j-1-t)*M/k1**2
                    S[j]=(K-j+1-e)/k1
                for t in range(K):
                    if t<j:
                        C[t]=q**(j-1-t)*M/(K*k1)
                    elif t==K-1:
                        C[t]=F(0)
                        P[t]=F(1,K)
                    else:
                        C[t]=F(K-1-t)/(K*(e-1))
                        P[t]=(e-(K-t))/(K*(e-1))
                assert min(S+P+C)>=0
                for t in range(K+1):
                    cg=S[t]-P[t]/e-C[t]+(1-1/e)*(C[t-1] if t else 0)
                    assert cg==0,(K,j,e,'g',t,cg)
                for t in range(K):
                    cd=sum(S[t+1:])+K*(P[t]+C[t])
                    assert cd==1,(K,j,e,'d',t,cd)
                assert sum(S)==1-q**j*(1-F(K-j)/(K*e))
                cases+=1
    return {'status':'VERIFIED-LP','exact_fraction_weighted_sums':cases,
            'K_range':[2,17],'all_segments_and_endpoints':True,'eta_1_included':True}


def R6_full_lattice_lp():
    """Minimize EACH proposed constraint's slack over actual full-lattice
    (f,predictor) instances, not over the already-reduced LP. Include every
    optimum set, hence overlap cases a,b,c. n=4,5 keeps the check bounded.
    """
    totals=Counter()
    minima={}
    for n,K in [(4,2),(5,3)]:
        m=1<<n
        nv=2*m
        for eu,eo in [(1,1),(1,2),(2,1),(2,2)]:
            eta=eu*eo
            rows=[]; rhs=[]
            def add(items,b=0):
                dd=Counter()
                for k,v in items:dd[k]+=v
                rows.append(dict(dd));rhs.append(b)
            for s in range(m):
                rem=[e for e in range(n) if not (s>>e)&1]
                for e in rem:
                    se=s|1<<e
                    add([(s,1),(se,-1)])
                    add([(se,1/eu),(s,-1/eu),(m+se,-1),(m+s,1)])
                    add([(m+se,1),(m+s,-1),(se,-eo),(s,eo)])
                for e,h in combinations(rem,2):
                    add([(s,1),(s|1<<e|1<<h,1),(s|1<<e,-1),(s|1<<h,-1)])
                if s.bit_count()<=K:add([(s,1)],1)
            for t in range(K):
                s=(1<<t)-1
                for e in range(t+1,n):add([(m+(s|1<<e),1),(m+(s|1<<t),-1)])
            ri=[];ci=[];va=[]
            for r,row in enumerate(rows):
                for c,v in row.items():ri.append(r);ci.append(c);va.append(v)
            Aub=coo_matrix((va,(ri,ci)),shape=(len(rows),nv)).tocsr()
            bub=np.array(rhs)
            for opt in combinations(range(n),K):
                om=sum(1<<e for e in opt)
                Aeq=coo_matrix(([1,1,1],([0,1,2],[0,m,om])),shape=(3,nv)).tocsr()
                def gain(t,e):
                    s=(1<<t)-1
                    out=np.zeros(nv)
                    if not (s>>e)&1:out[s|1<<e]+=1;out[s]-=1
                    return out
                for t in range(K):
                    st=(1<<t)-1
                    dt=gain(t,t)
                    sumslack=sum((gain(t,e) for e in opt),np.zeros(nv))
                    sumslack[st]+=1
                    objs=[('sum','all',sumslack,-1)]
                    for e in opt:
                        gt=gain(t,e);gn=gain(t+1,e)
                        case='a' if e<t else ('c' if e==t else 'b')
                        objs.extend([('pred',case,dt-gt/eta,0),
                                     ('mono',case,gt-gn,0),
                                     ('cons',case,(1-1/eta)*gn-gt+dt,0)])
                    for family,case,obj,const in objs:
                        r=linprog(obj,A_ub=Aub,b_ub=bub,A_eq=Aeq,b_eq=[0,0,1],
                                  bounds=[(None,None)]*nv,method='highs')
                        assert r.success,(n,K,eu,eo,opt,t,family,r.message)
                        slack=r.fun+const
                        assert slack>=-1e-8,(n,K,eu,eo,opt,t,family,case,slack)
                        key=family+'_'+case
                        minima[key]=min(minima.get(key,float('inf')),slack)
                        totals[key]+=1
    return {'status':'VERIFIED-LP','lp_objectives':sum(totals.values()),
            'counts_by_constraint_and_case':dict(totals),'minimum_slacks':minima,
            'scope':'full lattice n=4,K=2 and n=5,K=3; all optimal K-sets; four asymmetric/symmetric bands'}


def hardness_fraction_grid():
    allcases=0;edgecount=0
    example=None
    for K in range(2,13):
        for tau in range(1,K):
            for theta in [F(1),F(6,5),F(2),F(4)]:
                # Use normalized H rather than theta^(-1/2) H, and G unchanged;
                # the product of un-clamped extreme gain ratios is invariant.
                a=1-1/(theta*K)
                A=a**tau*F(K,K-tau)
                B=a**(1-tau)
                X=K+2
                H={(x,y):1-a**x*(1-F(y,K)) for x in range(X+1) for y in range(K+1)}
                G={(x,y):(1-a**(x+y) if y<=tau else 1-a**(x+tau)*F(K-y,K-tau))
                   for x in range(X+1) for y in range(K+1)}
                rr=[]
                for x in range(X+1):
                    for y in range(K+1):
                        p=(x,y)
                        for dx,dy in [(1,0),(0,1)]:
                            q=(x+dx,y+dy)
                            if q not in H:continue
                            dh=H[q]-H[p];dg=G[q]-G[p]
                            assert dh>=0 and dg>=0
                            if dh==0:assert dg==0
                            else:rr.append(dg/dh)
                            for ex,ey in [(1,0),(0,1)]:
                                r=(x+ex,y+ey);s=(x+dx+ex,y+dy+ey)
                                if s in H:assert H[s]-H[r]<=dh
                            edgecount+=1
                assert max(rr)==A
                assert min(rr)==1/(theta*B)
                actual=max(rr)/min(rr)
                assert actual==(theta*K-1)/(K-tau)
                assert min(max(rr),1/min(rr))>=1
                symmetric_declared=theta*max(A,B)**2
                assert actual<=symmetric_declared
                assert max(H[x,y] for x,y in H if x+y<=K)==H[0,K]==1
                assert H[K,0]==1-a**K
                if (K,tau,theta)==(4,1,F(4)):
                    example={'K':K,'tau':tau,'theta':str(theta),'A':str(A),'B':str(B),
                             'original_pair_eta_u':'2','original_pair_eta_o':'5/2',
                             'actual_scalar_error':str(actual),'printed_Phi':str(symmetric_declared)}
                allcases+=1
    assert example
    return {'status':'VERIFIED-LP','exact_count_grid_cases':allcases,'edges_checked':edgecount,
            'K_range':[2,12],'all_integer_tau_1_to_Kminus1':True,'exact_error_counterexample':example}


def calibration_comparison():
    rows=[]
    for K,c,eta in [(4,0,4),(8,1,2),(16,2,2),(32,2,3),(64,3,1.5)]:
        tau=c+1
        phi=lambda th:th*max((1-1/(th*K))**tau*K/(K-tau),
                            (1-1/(th*K))**(1-tau))**2
        assert phi(1)<=eta
        old=brentq(lambda th:phi(th)-eta,1,eta)
        new=(eta*(K-tau)+1)/K
        lk=lambda th:-math.expm1(K*math.log1p(-1/(th*K)))
        assert 1<=old<=new<=eta
        rows.append(dict(K=K,c=c,eta=eta,old_design=old,new_design=new,
                         old_hardness=lk(old),new_hardness=lk(new),greedy_guarantee=lk(eta)))
    return rows


if __name__=='__main__':
    started=time.monotonic()
    for name,fn in [('symbolic',symbolic_core),('dual',dual_literal_checks),
                    ('R6_LP',R6_full_lattice_lp),('hardness',hardness_fraction_grid),
                    ('calibration',calibration_comparison)]:
        RESULTS[name]=fn()
        print(name,'PASS',flush=True)
    RESULTS['elapsed_seconds']=time.monotonic()-started
    RESULTS['all_passed']=True
    (HERE/'J2_core_oracles.json').write_text(json.dumps(RESULTS,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in RESULTS.items() if k not in ['symbolic','calibration']},indent=2))
