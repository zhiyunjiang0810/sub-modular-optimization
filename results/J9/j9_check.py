import sympy as sp
from fractions import Fraction as Fr
import math

K,eta,a,eps,m,t,s = sp.symbols('K eta a epsilon m t s', positive=True)
j = K - a
k1 = (K-1)*eta+1; q = (K-1)*eta/k1
P = q**j; delta = P/(K*eta); C = k1/K
nu = eta/(eta-1); theta = (K-1)*eta - a; D = K*eta - a
phi = lambda tt: D - tt - eta*nu**(-tt)
gamma = D - m - eps
print("== identities (symbolic) ==")
Vj = 1 - q**j*(1 - (K-j)/(K*eta))
print("(5)  rho = 1-P+a*delta:", sp.simplify(Vj - (1-P+a*delta))==0)
# (10) with eps = (m-theta)/(nu^m-1)
eps_def = (m-theta)/(nu**m-1)
gam = D - m - eps_def
print("(10a) gamma = nu^m phi(m)/(nu^m-1):", sp.simplify(gam - nu**m*phi(m)/(nu**m-1))==0)
print("(10b) gamma-1 = nu^m phi(m+1)/(nu^m-1):", sp.simplify(gam-1 - nu**m*phi(m+1)/(nu**m-1))==0)
print("phi(theta+1) = (eta-1)(1-nu^-theta):", sp.simplify(phi(theta+1) - (eta-1)*(1-nu**(-theta)))==0)
# sequences (14),(15) as functions of x in each phase, with generic eps
def r(x,phase):
    return {'geo':q**x, 'lin':P-(x-j+eps)*delta, 'tail':(D-eps-(x-K))*delta}[phase]
def h(x,phase):
    return {'geo':(K-1)/K*q**x, 'lin':((K-1)*eta-(x-j))*delta, 'tail':(theta-(x-K)+eps*(nu**(x-K)-1))*delta}[phase]
chk=lambda e: sp.simplify(e)==0
print("(19) g_{K+t} = (eta-eps nu^t) delta:", chk(r(K+t,'tail')-h(K+t,'tail') - (eta-eps*nu**t)*delta))
print("(20) h_M=0 with eps def:", chk((h(K+m,'tail')).subs(eps,eps_def)))
print("(20) r_M = gamma*delta:", chk(r(K+m,'tail') - gamma*delta))
print("(21a) g_{K+t+1} = nu(g_{K+t}-delta):", chk((eta-eps*nu**(t+1))*delta - nu*((eta-eps*nu**t)*delta-delta)))
print("(21b) u_{K+t} = g_{K+t+1}/eta:", chk((h(K+t,'tail')-h(K+t+1,'tail')) - (eta-eps*nu**(t+1))*delta/eta))
print("(22) p_{j-1} = K delta/(K-1):", chk(r(j-1,'geo')-r(j,'geo') - K*delta/(K-1)))
print("(22) p_j = (1+eps) delta:", chk(r(j,'geo')-r(j+1,'lin') - (1+eps)*delta))
print("(22) p_x = delta inside lin:", chk(r(s,'lin')-r(s+1,'lin') - delta))
print("(22) p_K (lin->tail) = delta:", chk(r(K,'lin')-r(K+1,'tail') - delta))
print("(22) p_x = delta inside tail:", chk(r(K+t,'tail')-r(K+t+1,'tail') - delta))
print("(22) p_M = gamma delta:", chk(r(K+m,'tail') - gamma*delta))
print("(23) u_{j-1} = delta:", chk(h(j-1,'geo')-h(j,'geo') - delta))
print("(23) u_x = delta inside lin (x<=K-1):", chk(h(s,'lin')-h(s+1,'lin') - delta))
print("splice h at x=j (geo=lin):", chk(h(j,'geo')-h(j,'lin')))
print("splice h at x=K (lin=tail):", chk(h(K,'lin')-h(K,'tail')))
print("splice r at x=K (lin=tail):", chk(r(K,'lin')-r(K,'tail')))
print("(26) Kg_{j+s}-r_{j+s} = (s-(K-1)eps) delta:", chk(K*(r(j+s,'lin')-h(j+s,'lin'))-r(j+s,'lin') - (s-(K-1)*eps)*delta))
print("g_{j+s} = (eta-eps) delta:", chk(r(j+s,'lin')-h(j+s,'lin') - (eta-eps)*delta))
print("g_j = eta delta:", chk(r(j,'geo')-h(j,'geo') - eta*delta))
e27 = K*(r(K+t,'tail')-h(K+t,'tail'))-r(K+t,'tail')
print("(27) Kg_{K+t}-r_{K+t} = (a+t+eps-K eps nu^t) delta:", chk(e27 - (a+t+eps-K*eps*nu**t)*delta))
print("(27) at t=m equals (K-1)gamma delta:", chk((e27.subs(t,m)).subs(eps,eps_def) - (K-1)*gam*delta))
print("(27) at t=0 = (a-(K-1)eps) delta:", chk(e27.subs(t,0) - (a-(K-1)*eps)*delta))
# band table y=0 edges: Delta H = eta*u_{x-1}
print("row x<j: eta u_{x-1} = q^x/K:", chk(eta*(h(s-1,'geo')-h(s,'geo')) - q**s/K))
print("row x<j: p_x = q^x/k1:", chk(r(s,'geo')-r(s+1,'geo') - q**s/k1), " g_x = q^x/K:", chk(r(s,'geo')-h(s,'geo')-q**s/K))
print("row x=0: C - eta h_0 = 1/K:", chk(C-eta*h(0,'geo')-1/K))
print("row j<x<=K: eta u_{x-1} = eta delta:", chk(eta*(h(s,'lin')-h(s+1,'lin')) - eta*delta))
print("row K<x<M: eta u_{x-1} = g_x:", chk(eta*(h(K+t,'tail')-h(K+t+1,'tail')) - (r(K+t+1,'tail')-h(K+t+1,'tail'))))
print("(33) p_j-p_{j+1} = eps delta:", chk((r(j,'geo')-r(j+1,'lin'))-(r(j+1,'lin')-r(j+2,'lin')) - eps*delta))
print("(34) p_j-u_j = eps delta:", chk((r(j,'geo')-r(j+1,'lin'))-(h(j,'lin')-h(j+1,'lin')) - eps*delta))
print("(38) Fbar(T) = 1-P+(a+eps)delta:", chk(1-r(K,'lin') - (1-P+(a+eps)*delta)))
print("first O at empty: g_0=1/K and H=1/K:", chk(r(0,'geo')-h(0,'geo')-1/K), chk(C-eta*h(0,'geo')-1/K), " second O at {o}: h_0/(K-1)=1/K:", chk(h(0,'geo')/(K-1)-1/K))
print("canonical: eta u_0 = q/K < 1/K:", chk(eta*(h(0,'geo')-h(1,'geo')) - q/K))

print("\n== parameter lemma, dense numeric grid (sanity, not proof) ==")
import numpy as np
worst = {'m>theta':1e9,'eps<eta-1':1e9,'eps<1/(K-1)':1e9,'gamma>=0':1e9,'gamma<1':1e9,'e13':1e9,'Kg-r tail min':1e9,'p>=u':1e9}
for Kv in range(2,13):
    for ev in np.linspace(1.0005, Kv-0.0005, 400):
        av=math.floor(ev); jv=Kv-av; th=(Kv-1)*ev-av; Dv=Kv*ev-av; nuv=ev/(ev-1)
        ph=lambda tt: Dv-tt-ev*nuv**(-tt)
        # root by bisection
        lo,hi=0.0,Dv
        for _ in range(200):
            mid=(lo+hi)/2
            if ph(mid)>0: lo=mid
            else: hi=mid
        tau=lo; mv=math.floor(tau)
        epsv=(mv-th)/(nuv**mv-1); gv=Dv-mv-epsv
        worst['m>theta']=min(worst['m>theta'],mv-th); worst['eps<eta-1']=min(worst['eps<eta-1'],ev-1-epsv)
        worst['eps<1/(K-1)']=min(worst['eps<1/(K-1)'],1/(Kv-1)-epsv); worst['gamma>=0']=min(worst['gamma>=0'],gv); worst['gamma<1']=min(worst['gamma<1'],1-gv)
        if Kv>=3:
            x=mv-th; u=x/ev; A=(Kv-1)*ev; worst['e13']=min(worst['e13'],math.exp(Kv-2+u)-1-A*u)
        for tt in range(0,mv+1):
            worst['Kg-r tail min']=min(worst['Kg-r tail min'],av+tt+epsv-Kv*epsv*nuv**tt)
        # p>=u at the splice: K/(K-1) >= 1+eps
        worst['p>=u']=min(worst['p>=u'],Kv/(Kv-1)-(1+epsv))
print({k:round(v,6) for k,v in worst.items()})

print("\n== K=3, eta=3/2 example ==")
Kv,ev=3,Fr(3,2); av=1; jv=2; th=Fr(2); Dv=Fr(7,2); nuv=Fr(3)
mv=3; epsv=(mv-th)/(nuv**mv-1); gv=Dv-mv-epsv
Pv=Fr(9,16); dv=Pv/(Kv*ev)
print("eps,gamma,delta:",epsv,gv,dv," Fbar(T)=",1-Pv+(av+epsv)*dv," F(T)=",1-Pv+av*dv, " rho_3=",1-Pv+av*dv)
