from pathlib import Path
import importlib.util
import numpy as np

def project_root():
    for p in [Path.cwd(), *Path.cwd().parents]:
        if (p/'course.json').is_file(): return p
    raise FileNotFoundError('Открой ноутбук внутри папки masters-2027')

def load_answers():
    path=project_root()/'work/week01/answers.py'
    spec=importlib.util.spec_from_file_location('student_answers',path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def attempt(function,*args):
    try: return function(*args)
    except NotImplementedError as e:
        print('НЕ ВЫПОЛНЕНО:', e)
        return None

def npv(cashflows,rate):
    c=np.asarray(cashflows,dtype=float)
    if c.ndim!=1 or not np.isfinite(c).all() or not np.isfinite(rate) or rate<=-1:
        raise ValueError('Нужен конечный одномерный поток и ставка>-1')
    return float(np.sum(c/(1+rate)**np.arange(c.size)))
