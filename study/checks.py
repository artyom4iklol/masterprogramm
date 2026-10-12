"""Числовые и структурные проверки; письменное понимание здесь не оценивается."""
import numpy as np
import pandas as pd
from .support import load_answers

def close(a,b):
    np.testing.assert_allclose(a,b,rtol=1e-7,atol=1e-8)

def rejects(fn,*args):
    try: fn(*args)
    except ValueError: return
    raise AssertionError('Недопустимый ввод должен вызывать ValueError')

def consumer(a):
    for m,expected in [(0,(0,0,6)),(1,(0,1,5)),(2,(0,2,4)),(12,(4,4,2)),(22,(8,6,0)),(24,(8,6,0))]:
        out=a.consumer_quadratic(m)
        x,y,l=float(out['x']),float(out['y']),float(out['shadow'])
        close([x,y,l],expected)
        assert x>=0 and y>=0 and l>=0 and 2*x+y<=m+1e-8
        close(l*(m-2*x-y),0)
        assert 8-x-2*l<=1e-8 and 6-y-l<=1e-8
        close(x*(8-x-2*l),0);close(y*(6-y-l),0)
    for m in [-1,float('nan'),float('inf')]: rejects(a.consumer_quadratic,m)

def duality(a):
    for alpha,px,py,m in [(.5,2,1,12),(.3,3,5,110),(.7,4,2,50)]:
        d=np.asarray(a.marshallian(alpha,px,py,m),dtype=float)
        close(d,[alpha*m/px,(1-alpha)*m/py]);assert (d>0).all()
        u=d[0]**alpha*d[1]**(1-alpha)
        e=a.expenditure(alpha,px,py,u);h=np.asarray(a.hicksian(alpha,px,py,u))
        close(e,m);close(h,d);close(px*h[0]+py*h[1],e)
        close(a.marshallian(alpha,px*7,py*7,m*7),d)
        close(a.expenditure(alpha,px*3,py*3,u),3*e)
        # Shephard: цены меняются, полезность фиксирована.
        delta=1e-5
        grad=[(a.expenditure(alpha,px+delta,py,u)-a.expenditure(alpha,px-delta,py,u))/(2*delta),
              (a.expenditure(alpha,px,py+delta,u)-a.expenditure(alpha,px,py-delta,u))/(2*delta)]
        np.testing.assert_allclose(grad,h,rtol=1e-5,atol=1e-6)
    rejects(a.marshallian,0,2,1,12);rejects(a.marshallian,.5,0,1,12)
    rejects(a.expenditure,.5,2,1,-1);rejects(a.hicksian,.5,2,1,-1)

def firm(a):
    for q,r,w in [(10,4,2),(0,4,2),(7,3,5),(2.5,1,1)]:
        out=a.conditional_inputs(q,r,w)
        k,l,c=float(out['K']),float(out['L']),float(out['cost'])
        assert min(k,l,c)>=0
        close(k**(1/3)*l**(2/3),q);close(c,r*k+w*l)
        expected=q*(r/(1/3))**(1/3)*(w/(2/3))**(2/3)
        close(c,expected)
        if q>0: close(l/k,2*r/w)
        changed=a.conditional_inputs(q,r*2,w*2)
        close([changed['K'],changed['L']],[k,l]);close(changed['cost'],2*c)
    rejects(a.conditional_inputs,-1,4,2);rejects(a.conditional_inputs,10,0,2)

def ols(a):
    X=np.column_stack([np.ones(5),np.arange(5)])
    y=np.array([1.,2.,2.,4.,5.])
    out=a.ols(X,y)
    close(out['beta'],[.8,1]);e=np.asarray(out['residuals']);close(e,[.2,.2,-.8,.2,.2])
    close(X.T@e,[0,0]);close(out['sigma2'],.8/3)
    close(out['covariance'],np.array([[.6,-.2],[-.2,.1]])*(.8/3))
    # Не один фиксированный пример: прогнозы инвариантны к смене масштаба x.
    XX=X.copy();XX[:,1]*=10
    out2=a.ols(XX,y);close(out2['beta'],[.8,.1]);close(XX@out2['beta'],X@out['beta'])
    rejects(a.ols,np.ones((5,2)),y);rejects(a.ols,np.eye(2),np.ones(2))

def finance(a):
    r=np.array([100.,110.,121.]);c=.6*r
    out=a.project_cashflows(120,r,c,.25,.1,30)
    close(out,[-130,39,41.9,80.9])
    # Нулевой налог и NWC изолируют экономический смысл каждого компонента.
    close(a.project_cashflows(120,r,c,0,0,30),[-120,40,44,78.4])
    close(a.project_cashflows(120,r,c,.25,0,30),[-120,40,43,68.8])
    scaled=a.project_cashflows(240,2*r,2*c,.25,.1,60)
    close(scaled,2*np.asarray(out))
    rejects(a.project_cashflows,120,r,c,1.1,.1,30)
    rejects(a.project_cashflows,120,r,c[:-1],.25,.1,30)

def growth(a):
    s=pd.Series([100.,101.,103.,102.,106.],index=pd.period_range('2020Q1',periods=5,freq='Q'))
    for h in [1,2,3]:
        out=a.growth_targets(s,h)
        assert isinstance(out,pd.Series) and out.index.equals(s.index)
        expected=[100*((s.iloc[t+h]/s.iloc[t])**(4/h)-1) for t in range(len(s)-h)]
        close(out.iloc[:-h],expected);assert out.iloc[-h:].isna().all()
        # Будущая строка влияет лишь на те цели, которые её используют.
        s2=s.copy();s2.iloc[-1]=120
        out2=a.growth_targets(s2,h);close(out2.iloc[:len(s)-h-1],out.iloc[:len(s)-h-1])
    rejects(a.growth_targets,s,0);rejects(a.growth_targets,s,1.5)
    bad=s.copy();bad.iloc[1]=0;rejects(a.growth_targets,bad,1)
    rejects(a.growth_targets,s.iloc[[0,2,3,4]],1)

CHECKS={'consumer':consumer,'duality':duality,'firm':firm,'ols':ols,'finance':finance,'growth':growth}
def run_checks(names=None):
    selected=list(CHECKS) if names is None else names
    try: a=load_answers()
    except Exception as e:return {n:{'status':'failed','message':type(e).__name__+': '+str(e)} for n in selected}
    results={}
    for name in selected:
        try: CHECKS[name](a)
        except NotImplementedError as e:results[name]={'status':'pending','message':str(e)}
        except Exception as e:results[name]={'status':'failed','message':type(e).__name__+': '+str(e)}
        else:results[name]={'status':'passed','message':'Вычислительные проверки пройдены; требуется разбор письменного решения'}
    return results
