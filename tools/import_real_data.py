"""Импорт исходных CSV FRED; никаких сетевых запросов и подстановки синтетики."""
from pathlib import Path
import argparse,hashlib,json
from datetime import datetime,timezone
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def load(path,series):
    d=pd.read_csv(path)
    date=next((k for k in ['observation_date','DATE','date'] if k in d.columns),None)
    column=next((k for k in d.columns if k.upper()==series),None)
    if date is None or column is None:raise ValueError('Нужны дата DATE/observation_date и колонка '+series)
    idx=pd.to_datetime(d[date],errors='raise');values=pd.to_numeric(d[column].replace('.',np.nan),errors='raise')
    s=pd.Series(values.to_numpy(),index=idx,name=series).sort_index()
    if s.index.has_duplicates:raise ValueError('Дубли дат в '+series)
    return s
def main():
    p=argparse.ArgumentParser();p.add_argument('--gdp',required=True,type=Path);p.add_argument('--nfci',required=True,type=Path);a=p.parse_args()
    gdp=load(a.gdp,'GDPC1');fci=load(a.nfci,'NFCI')
    gdp.index=gdp.index.to_period('Q')
    if gdp.index.has_duplicates or (gdp.dropna()<=0).any():raise ValueError('GDP должен содержать один положительный уровень на квартал')
    grouped=fci.groupby(fci.index.to_period('Q'))
    frame=pd.concat([gdp,grouped.mean().rename('NFCI'),grouped.count().rename('nfci_weeks')],axis=1).loc[gdp.index].copy()
    missing=frame[['GDPC1','NFCI']].isna().any(axis=1)
    if missing.any():raise ValueError('Не заполнены кварталы: '+', '.join(frame.index[missing].astype(str)))
    if len(frame)>1 and not np.all(np.diff(frame.index.asi8)==1):raise ValueError('Пропущены кварталы; не заполняй их автоматически')
    dest=ROOT/'data/processed';dest.mkdir(exist_ok=True)
    frame.index.name='quarter';frame.to_csv(dest/'us_gdp_nfci.csv')
    meta={'downloaded_by_user':True,'imported_utc':datetime.now(timezone.utc).isoformat(),
          'files':[{ 'series':series,'filename':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for path,series in [(a.gdp,'GDPC1'),(a.nfci,'NFCI')]],
          'aggregation':'arithmetic mean of available weekly NFCI by calendar quarter',
          'low_week_counts':{str(k):int(v) for k,v in frame['nfci_weeks'].items() if v<10},
          'limitation':'Current downloaded history; publication dates and historical vintages must be documented separately'}
    (dest/'provenance.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    print('Импортировано кварталов:',len(frame));print('Проверь nfci_weeks и публикационные даты; импорт не подтверждает доступность признаков в реальном времени.')
if __name__=='__main__':main()
