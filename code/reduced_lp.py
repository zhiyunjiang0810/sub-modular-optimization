"""Reduced O(K^2) factor-revealing LP for the exact worst case of single-step predictive greedy.
Vars: d_t (t<K), g_{t,i} (t<=K, i<K). OPT=1, r_t = 1 - sum_{s<t} d_s.
  sum_i g_{t,i} >= r_t ; d_t >= g_{t,i}/eta ; g_{t+1,i} <= g_{t,i} ; (1-1/eta) g_{t+1,i} >= g_{t,i} - d_t.
min sum_t d_t."""
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

def reduced(K, eta, return_sol=False):
    nd=K; g=lambda t,i: nd+t*K+i; nv=nd+(K+1)*K
    rows=[];cols=[];vals=[];b=[]; r=0
    def ub(c,rhs=0.0):
        nonlocal r
        for k,v in c.items(): rows.append(r);cols.append(k);vals.append(v)
        b.append(rhs); r+=1
    for t in range(K):
        c={g(t,i):-1.0 for i in range(K)}
        for s in range(t): c[s]=-1.0
        ub(c,-1.0)
        for i in range(K):
            ub({g(t,i):1.0/eta, t:-1.0})
            ub({g(t+1,i):1.0, g(t,i):-1.0})
            ub({g(t,i):1.0, t:-1.0, g(t+1,i):-(1-1/eta)})
    A=coo_matrix((vals,(rows,cols)),shape=(r,nv)).tocsr()
    obj=np.zeros(nv); obj[:K]=1
    res=linprog(obj,A_ub=A,b_ub=np.array(b),bounds=[(0,None)]*nv,method="highs")
    return (res.fun,res) if return_sol else res.fun

if __name__=="__main__":
    for eta in [1.5,2.0,3.0,5.0]:
        Ks=[25,50,100,200,400,800]
        vals={K:reduced(K,eta) for K in Ks}
        rich=[(vals[2*K]*2*K - vals[K]*K)/K for K in Ks[:-1]]
        print(f"eta={eta}: "+"  ".join(f"K={K}:{v:.5f}" for K,v in vals.items()))
        print(f"   Richardson (a+b/K) limits: {['%.5f'%x for x in rich]}   1-e^(-1/eta)={1-np.exp(-1/eta):.5f}")
