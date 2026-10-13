"""Author QA for the week-one keys, not a student grade. Contains answer checks."""
from pathlib import Path
import importlib.util
import json
import math
import re
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
W=ROOT/'weeks/week01'
spec=importlib.util.spec_from_file_location('week1_reference',W/'lab_reference.py')
ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
checks={}

def utility(x,y): return 8*x+6*y-(x*x+y*y)/2

def projection(m):
    # Independent construction: project unconstrained optimum onto budget set
    # by solving its monotone resource equation; no analytical regime cutoffs.
    a=np.array([8.,6.]);p=np.array([2.,1.])
    if p@a<=m:return a
    lo,hi=0.,float(max(a/p))+1
    for _ in range(90):
        mid=(lo+hi)/2
        z=np.maximum(a-mid*p,0)
        if p@z>m:lo=mid
        else:hi=mid
    return np.maximum(a-hi*p,0)

rng=np.random.default_rng(271828)
ms=np.r_[0.,2.,22.,2-1e-8,2+1e-8,22-1e-8,22+1e-8,rng.uniform(0,50,400)]
for m in ms:
    ans=ref.consumer(m);z=np.array([ans['x'],ans['y']]);p=np.array([2.,1.])
    assert np.allclose(z,projection(m),atol=1e-9)
    assert (z>=-1e-10).all() and p@z<=m+1e-9
    lam=ans['shadow'];mu=lam*p-(np.array([8.,6.])-z)
    assert lam>=0 and (mu>=-1e-9).all()
    assert abs(lam*(m-p@z))<1e-7 and np.max(abs(mu*z))<1e-7
for bad in [-1,float('nan'),float('inf'),-float('inf')]:
    try:ref.consumer(bad)
    except ValueError:pass
    else:raise AssertionError('invalid input not rejected')
checks['D5_independent_projection_and_KKT_cases']=len(ms)
for m in [0.,1.,2.,12.,22.,26.]:
    h=1e-5
    der=(ref.value(m+h)-ref.value(m))/h
    assert abs(der-ref.consumer(m)['shadow'])<1e-4
checks['D5_value_derivative']=6

# Matrix solves provide a separate arithmetic path for both quadratic examples.
for A,b,z,value in [([[2,1],[1,2]],[6,4],[8/3,2/3],28/3),
                     ([[4,-1],[-1,2]],[8,6],[22/7,32/7],184/7),
                     ([[4,2],[2,2]],[10,4],[3,-1],13)]:
    A=np.array(A,dtype=float);b=np.array(b,dtype=float)
    zz=np.linalg.solve(A,b)
    assert np.allclose(zz,z) and np.linalg.eigvalsh(A).min()>0
    assert math.isclose(b@zz-.5*zz@A@zz,value)
checks['quadratic_examples_and_EX2']=3

# Parameterized one-dimensional keys vs exhaustive bounded searches.
q=np.linspace(0,3,30001)
for b in [-5,0,.01,3,11.9,12,20]:
    z=max(0,min(b/4,3));v=b*z-2*z*z
    assert v+1e-10>=np.max(b*q-2*q*q)
for F in [0,9,11.25,12,13]:
    for cap in [1.5,3.]:
        qq=np.linspace(0,cap,10001);vals=12*qq-3*qq**2-F;vals[0]=0
        target=max(0,12*min(2,cap)-3*min(2,cap)**2-F)
        assert target+1e-9>=vals.max() and target-vals.max()<1e-5
checks['A2_A5_parameter_grid']=17

for c in [1.,2.]: # C5 and R28a
    for p in [.2,.8,1.,1.5,2.,3.]:
        for m in [.1,.5,1.,2.,7.]:
            z=max(0,min(c/p-1,m/p))
            grid=np.linspace(0,m/p,10001)
            val=c*np.log1p(z)+m-p*z
            assert val+1e-10>=np.max(c*np.log1p(grid)+m-p*grid)
checks['C5_R28a_grid_cases']=60

# EX3 new structural constraint: grid the entire feasible region, including slack budgets.
for m in [.1,.99,1.,1.01,2.,5.]:
    x=max(0,(m-1)/2);y=min(m,1);val=math.log1p(x)+y
    xs=np.linspace(0,m/2,501)
    ys=np.linspace(0,min(m,1),501)
    X,Y=np.meshgrid(xs,ys,indexing='ij');ok=2*X+Y<=m+1e-10
    assert val+1e-9>=np.max((np.log1p(X)+Y)[ok])
    if m<1:lam,nu,mux=1.,0.,1.
    elif m>1:lam,nu,mux=1/(m+1),1-1/(m+1),0.
    else:lam,nu,mux=.75,.25,.5
    assert abs(1/(1+x)-2*lam+mux)<1e-10
    assert abs(1-lam-nu)<1e-10
    assert abs(mux*x)+abs(nu*(1-y))<1e-10
checks['EX3_independent_grid_and_multipliers']=6

# R7a uses different coefficients and equal prices.
for m in [0,1,3,4,7,9]:
    if m<=3:x,y,lam=m,0,5-m
    elif m<=7:x,y,lam=(m+3)/2,(m-3)/2,(7-m)/2
    else:x,y,lam=5,2,0
    mus=np.array([lam-5+x,lam-2+y])
    assert np.min(mus)>=-1e-10 and abs(mus@[x,y])<1e-10
    assert x+y<=m and abs(lam*(m-x-y))<1e-10
checks['R7a_KKT']=6

# Every assignment/control ID has its own written solution.
problems=(W/'08_problems.md').read_text();solutions=(W/'10_solutions.md').read_text()
ids=re.findall(r'\*\*([ABCD][1-6])\.',problems)
assert len(ids)==24 and len(set(ids))==24
for name in ids:assert re.search(r'^## '+name+r'$',solutions,re.M),name
for name in ['EX1','EX2','EX3','EX4','R0','R7a','R7b','R28a','R28b']:
    assert re.search(r'^## '+name+r'$',(W/'11_assessment_keys.md').read_text(),re.M),name
assert sum([5,5,6,6,4,3,3,4])==36
nb=json.loads((W/'lab.ipynb').read_text())
assert nb['nbformat']==4 and nb['nbformat_minor']==5
for cell in nb['cells']:
    if cell['cell_type']=='code':compile(''.join(cell['source']),'lab.ipynb','exec')
checks['assignment_keys']=24
checks['control_and_return_keys']=9
checks['weekly_hours']=36
print(json.dumps(checks,ensure_ascii=False,indent=2))
