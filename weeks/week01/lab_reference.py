"""Ключ D5. Открывать после самостоятельной попытки.
Не импортируется учебным ноутбуком автоматически.
"""
import math

def consumer(m):
    m=float(m)
    if not math.isfinite(m) or m<0:
        raise ValueError("m must be finite and nonnegative")
    if m <= 2:
        return dict(x=0.0,y=m,shadow=6-m)
    if m <= 22:
        return dict(x=(2*m-4)/5,y=(m+8)/5,shadow=(22-m)/5)
    return dict(x=8.0,y=6.0,shadow=0.0)

def value(m):
    a=consumer(m)
    return 8*a['x']+6*a['y']-(a['x']**2+a['y']**2)/2
