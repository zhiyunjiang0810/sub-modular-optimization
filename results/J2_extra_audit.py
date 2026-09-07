#!/usr/bin/env python3
"""J2: CSV evidence and small exact counterexamples. Requires numpy, pandas.

Run from project root: python3 results/J2_extra_audit.py
The new-definition diagnostic is deliberately NOT called a certificate on
nonmonotone objectives. Pair CSVs record decimal approximations; sign evidence
uses tolerance 1e-9. The graph, endpoint and query-budget witnesses are exact.
"""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import csv
import json
import math
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
TOL=1e-9


def coverage_witness():
    n,K=8,2
    true_edges=[(0,1),(0,2),(0,3),(0,4),(3,4),(5,6),(5,7),(6,7)]
    obs_edges=[(0,1),(0,2),(3,4)]
    def values(edges):
        adj=[1<<i for i in range(n)]
        for a,b in edges:adj[a]|=1<<b;adj[b]|=1<<a
        vv=[]
        for s in range(1<<n):
            mask=0
            for e in range(n):
                if (s>>e)&1:mask|=adj[e]
            vv.append(mask.bit_count())
        return vv
    f,g=values(true_edges),values(obs_edges)
    for v in [f,g]:
        for a in range(1<<n):
            for b in range(1<<n):assert v[a]+v[b]>=v[a|b]+v[a&b]
            for e in range(n):assert v[a|1<<e]>=v[a]
    s=0;trace=[]
    for t in range(K):
        rem=[e for e in range(n) if not (s>>e)&1]
        dg={e:g[s|1<<e]-g[s] for e in rem}
        df={e:f[s|1<<e]-f[s] for e in rem}
        pick=max(rem,key=lambda e:(dg[e],-e))
        trace.append(dict(step=t,state=s,pick=pick,true_gain=df[pick],best_true=max(df.values()),
                          predicted_gain=dg[pick],true_gains=df,predicted_gains=dg))
        s|=1<<pick
    opt=max(f[z] for z in range(1<<n) if z.bit_count()<=K)
    assert [r['pick'] for r in trace]==[0,3]
    assert opt==8 and f[s]==5
    assert trace[1]['true_gain']==0 and trace[1]['best_true']==3
    assert trace[0]['true_gain']==trace[0]['best_true']==5
    assert F(f[s],opt)==F(5,8)<F(3,4)
    return dict(status='VERIFIED-LP',n=n,K=K,true_edges=true_edges,observed_edges=obs_edges,
                trace=trace,old_eta_sel=1,ratio='5/8',old_claimed_bound='3/4',
                predictor_is_coverage_on_a_subgraph=True,
                explanation='First choice is unique; second-step ties only among equally bad nodes 3 and 4.')


def query_budget_witness():
    # c=0, K=2, n=16 satisfies n>=4K^(c+2). For EVERY possible single query
    # and subsequent output after answer zero, select two unseen elements.
    # f has weights 1,1; predictor has weights 1,2 on them. Both are modular.
    n,K=16,2
    sets=[sum(1<<e for e in z) for k in range(K+1) for z in combinations(range(n),k)]
    count=0
    for q in sets:
        for t in sets:
            hidden=[e for e in range(n) if not ((q|t)>>e)&1][:2]
            assert len(hidden)==2
            hm=sum(1<<e for e in hidden)
            assert q&hm==0 and t&hm==0
            assert (hm&hm).bit_count()==K
            count+=1
    return dict(status='VERIFIED-LP',n=n,K=K,c=0,query_output_pairs_checked=count,
                true_weights_on_hidden=[1,1],predictor_weights_on_hidden=[1,2],
                exact_scalar_error=2,output_ratio=0,
                consequence='The deterministic one-query class has worst-case ratio zero, not 1-exp(-1/eta).')


def statement_endpoints():
    K,j,eta_build=3,1,F(19,10)
    q=F((K-1)*eta_build,(K-1)*eta_build+1)
    delta=q**j/(K*eta_build)
    gain=q**j/K-(K-j)*delta
    assert gain==-F(1,72)
    return dict(strict_variant_integer_endpoint=dict(K=K,j=j,declared_eta=2,
                 build_eta=str(eta_build),state_counts=dict(x=1,z=2,y=2),
                 adding_final_O_gain=str(gain),
                 consequence='The printed capped perturbation is nonmonotone at the segment lower endpoint.'),
                submodular_surrogate_at_eta_1=dict(K=3,eta=1,ratio_both_models='19/27',
                 reason='eta_u=eta_o=1 forces predictor=f on every edge and at the empty set.'),
                Phi_derivative_typo=dict(K=4,tau=1,actual_derivative=1,printed_derivative='1/4',
                 consequence='Missing chain-rule factor K; positivity conclusion is unchanged.'))


def csv_audit():
    summary={};allrows=[];violations=[]
    for family in ['E1','E2','E3']:
        d=pd.read_csv(HERE/(family+'_rows.csv'))
        d=d[d.K>=2].copy()
        eta=d.eta_sel.to_numpy(float);k=d.K.to_numpy(int)
        L=1-(1-1/(eta*k))**k
        rho=[]
        for K,e in zip(k,eta):
            q=(K-1)*e/((K-1)*e+1)
            rho.append(min(1-q**j*(1-(K-j)/(K*e)) for j in range(K)))
        d['J2_L']=L;d['J2_rho_at_sel']=rho
        d['J2_below_L']=d.ratio+TOL<d.J2_L
        d['J2_below_rho_at_sel']=d.ratio+TOL<d.J2_rho_at_sel
        vv=d[d.J2_below_L].copy()
        vv['J2_gap']=vv.J2_L-vv.ratio
        violations.extend(vv.to_dict('records'))
        info=dict(rows_K_ge_2=len(d),below_L=int(d.J2_below_L.sum()),
                  below_rho_at_selection=int(d.J2_below_rho_at_sel.sum()),
                  below_L_with_eta_1=int((vv.eta_sel==1).sum()),
                  rows_with_nonpositive_chosen_step=int((d.n_steps_nonpos>0).sum()),
                  K5_below_L=int(d[d.K==5].J2_below_L.sum()))
        if family in ['E1','E3']:
            pairs=pd.read_csv(HERE/(family+'_pairs.csv.gz'))
            groups={}
            for key,part in pairs.groupby(['dataset','seed','step']):
                chosen=part[part.chosen==1]
                assert len(chosen)==1
                groups[key]=dict(g=float(chosen.d.iloc[0]),M=float(part.d.max()),
                                 min_gain=float(part.d.min()))
            pneg=0;zero=0;pairsneg=0;posonly=0;unmatched=0
            for row in d.to_dict('records'):
                pref=[groups.get((row['dataset'],row['seed'],t)) for t in range(int(row['K']))]
                if any(v is None for v in pref):unmatched+=1;continue
                neg=any(v['g'] < -TOL for v in pref)
                hz=any(abs(v['g'])<=TOL and v['M']>TOL for v in pref)
                nc=any(v['min_gain'] < -TOL for v in pref)
                pneg+=neg;zero+=hz;pairsneg+=nc
                posonly+=all(v['g']>TOL for v in pref)
                # This is just a diagnostic outside the monotone model.
                per=[v['M']/v['g'] if v['g']>TOL else
                     (float('inf') if v['M']>TOL else 1.) for v in pref]
                diagnostic=max([1.]+per) if not neg else None
                allrows.append(dict(family=family,dataset=row['dataset'],seed=row['seed'],K=row['K'],
                                    selected_negative=neg,harmful_zero=hz,negative_candidate_observed=nc,
                                    eta_sel_old=row['eta_sel'],eta_sel_repaired_diagnostic=diagnostic,
                                    ratio=row['ratio'],below_old_L=row['J2_below_L']))
            info.update(pair_rows=len(pairs),states=len(groups),run_prefixes_with_negative_selection=pneg,
                        run_prefixes_with_harmful_zero=zero,
                        run_prefixes_with_negative_candidate=pairsneg,all_selected_steps_positive=posonly,
                        unmatched_prefixes=unmatched)
        else:
            # The sample has no chosen marker: do not pretend to reconstruct
            # all per-step chosen gains from it. However, increments of the
            # cumulative nonpositive-step counter identify chosen-zero steps
            # for this monotone coverage objective. A positive sampled candidate
            # then suffices to certify that such a zero step was harmful.
            p=pd.read_csv(HERE/'E2_pairs_sample.csv.gz')
            info.update(sample_pairs=len(p),
                        true_zero_predicted_positive=int(((p.d==0)&(p.d_tilde>0)).sum()),
                        true_positive_predicted_zero=int(((p.d>0)&(p.d_tilde==0)).sum()))
            keys=['dataset','p','seed']
            full=pd.read_csv(HERE/'E2_rows.csv').sort_values(keys+['K'])
            full['zero_step']=full.groupby(keys).n_steps_nonpos.diff().fillna(full.n_steps_nonpos)
            assert full.zero_step.isin([0,1]).all()
            maxima=p.groupby(keys+['step']).d.max().rename('sample_max_true').reset_index()
            maxima=maxima.rename(columns={'step':'K'})
            full=full.merge(maxima,on=keys+['K'],how='left')
            assert full.sample_max_true.notna().all()
            full['confirmed_harmful_zero_step']=(full.zero_step==1)&(full.sample_max_true>0)
            full['confirmed_harmful_zero_in_prefix']=full.groupby(keys).confirmed_harmful_zero_step.cummax()
            full.to_csv(HERE/'J2_E2_zero_step_evidence.csv',index=False)
            info.update(distinct_zero_steps=int(full.zero_step.sum()),
                        confirmed_harmful_zero_steps=int(full.confirmed_harmful_zero_step.sum()),
                        zero_steps_not_resolved_by_sample=int(((full.zero_step==1)&(full.sample_max_true==0)).sum()),
                        prefixes_K_ge_2_with_confirmed_harmful_zero=int(full[full.K>=2].confirmed_harmful_zero_in_prefix.sum()),
                        trajectories=int(full.groupby(keys).ngroups),
                        trajectories_with_harmful_zero=int(full.groupby(keys).confirmed_harmful_zero_step.any().sum()),
                        pooled_zero_step_fraction=float(full.zero_step.sum()/len(full)))
        summary[family]=info
    worst=sorted(violations,key=lambda z:z['J2_gap'],reverse=True)
    if worst:pd.DataFrame(worst).to_csv(HERE/'J2_bound_violations.csv',index=False)
    pd.DataFrame(allrows).to_csv(HERE/'J2_selection_diagnostics.csv',index=False)
    return dict(tolerance=TOL,by_family=summary,
                total_rows=sum(v['rows_K_ge_2'] for v in summary.values()),
                total_below_L=sum(v['below_L'] for v in summary.values()),
                worst_L_violations=worst[:5],
                interpretation='A negative candidate disproves monotonicity on that state. Absence of such a record does not prove global model membership.')


if __name__=='__main__':
    out=dict(coverage=coverage_witness(),query_budget=query_budget_witness(),
             endpoints=statement_endpoints(),experiments=csv_audit(),all_passed=True)
    (HERE/'J2_extra_audit.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(out,indent=2,ensure_ascii=False))
