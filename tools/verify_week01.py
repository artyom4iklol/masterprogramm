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
# Read the delivered schedule, not a separate hardcoded total.
schedule=(W/'README.md').read_text()
hours={}
for line in schedule.splitlines():
    cells=[x.strip() for x in line.split('|')[1:-1]]
    if len(cells)==4 and cells[0] in ['P','A','B','C','D','IR','EN','R','EX']:
        hours[cells[0]]=int(cells[2])
assert hours==dict(P=2,A=4,B=5,C=6,D=5,IR=4,EN=3,R=3,EX=4)
assert sum(hours.values())==36
for block,expected in [('A',120),('B',150),('C',180),('D',120)]:
    minutes=re.findall(r'\*\*'+block+r'[1-6]\.[^\n]*?\((\d+) минут',problems)
    assert len(minutes)==6 and sum(map(int,minutes))==expected,(block,minutes)
for num in range(1,7):
    assert re.search(r'^## P'+str(num)+r'$',(W/'12_tools_keys.md').read_text(),re.M)
assert sum(map(int,re.findall(r'\*\*P[1-6] \((\d+) минут',(W/'00_tools.md').read_text())))==55
checks['schedule_and_exercise_minutes']='36 base hours; 0–4 optional reserve; 55+120+150+180+120 exercise minutes'

# C1: compare the piecewise formula with search over original feasible leisure choices.
cases=0
for T in [1.,8.]:
 for w in [2.,10.]:
  for p in [.5,2.]:
   for ratio in [0.,.25,.999,1.,1.001,2.]:
    Y=ratio*w*T
    leisure=min(T,(w*T+Y)/(2*w));cons=(w*(T-leisure)+Y)/p
    assert leisure>0 and leisure<=T and cons>0
    grid=np.linspace(0,T,20001)[1:]
    available=w*(T-grid)+Y;grid=grid[available>0];available=available[available>0]
    values=np.log(available/p)+np.log(grid)
    value=math.log(cons)+math.log(leisure)
    assert value>=values.max()-1e-10 and value-values.max()<1e-4
    cases+=1
checks['C1_original_budget_grid_cases']=cases
assert np.allclose([min(8,(80+0)/20),(80+0)/(2*2)],[4,20])
assert min(8,(80+100)/20)==8 and 100/2==50

# D3: independent feasible-region search; marginal value compared with finite differences.
xx=np.linspace(0,5,1001)[:,None]
yy=(10-2*xx)*np.linspace(0,1,1001)[None,:]
scores=5*xx+4*yy-(xx*xx+yy*yy)/2
assert abs(scores.max()-18.9)<1e-8
assert math.isclose(2*(17/5)+(16/5),10)
def production_value(cap):
 a=np.array([5.,4.]);price=np.array([2.,1.])
 if price@a<=cap:z=a
 else:
  lo,hi=0.,10.
  for _ in range(90):
   mid=(lo+hi)/2;z=np.maximum(a-mid*price,0)
   if price@z>cap:lo=mid
   else:hi=mid
  z=np.maximum(a-hi*price,0)
 return a@z-.5*z@z
assert abs((production_value(10.00001)-production_value(10))/.00001-.8)<1e-4
assert abs(production_value(15)-production_value(10)-1.6)<1e-9
checks['D3_grid_points_and_resource_derivative']=1002001

# P: independent polynomial substitution and linear solve checks.
assert np.allclose(np.linalg.solve([[3,1],[1,2]],[7,4]),[2,1])
for x in np.linspace(-2,3,11):
 y=5-x
 assert math.isclose(x*x+3*x*y-2*y*y,-4*x*x+35*x-50,abs_tol=1e-10)
 assert math.isclose((2*x+3*y)-(3*x-4*y),-8*x+35,abs_tol=1e-10)
H=np.array([[-2,3],[3,-2]])
assert np.array([1,1])@H@np.array([1,1])==2
assert np.array([1,-1])@H@np.array([1,-1])==-10
assert math.isclose((20*3.5-3.5**2)-(20*3-3**2),6.75)
checks['P_keys']='substitution, matrix solve, quadratic directions and finite change checked'
checks['tools_exercise_keys']=6
nb=json.loads((W/'lab.ipynb').read_text())
assert nb['nbformat']==4 and nb['nbformat_minor']==5
for cell in nb['cells']:
    if cell['cell_type']=='code':compile(''.join(cell['source']),'lab.ipynb','exec')
checks['assignment_keys']=24
checks['control_and_return_keys']=9
checks['weekly_hours']=36
print(json.dumps(checks,ensure_ascii=False,indent=2))
