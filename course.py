"""Локальный учебный процесс: статус, проверки, снимок сдачи, запись разбора."""
import argparse,json,sys,hashlib,zipfile,re,subprocess,platform
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
def read(path):return json.loads((ROOT/path).read_text())
def write(path,data):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def now():return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def bundle_paths():
    paths=[]
    for folder in ['work','notebooks','research']:
        paths += [p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in ['.py','.md','.ipynb','.csv','.json','.bib','.pdf','.png','.jpg','.svg'] and '__pycache__' not in p.parts and '.ipynb_checkpoints' not in p.parts]
    return sorted(paths)
def checked_state():return {str(p.relative_to(ROOT)):digest(p) for p in bundle_paths()}
def checks():
    from study.checks import run_checks
    return run_checks()
def selfcheck():
    results=checks();write('reports/selfcheck.json',{'created':now(),'python':platform.python_version(),'results':results,'file_hashes':checked_state()})
    for k,v in results.items():print(k+': '+v['status']+' — '+v['message'])
    print('Автопроверка не присваивает академическую оценку.')
    return 1 if any(v['status']=='failed' for v in results.values()) else 0
def status():
    rows=read('course.json')['assignments'];reviews=read('progress/reviews.json');results=checks();state=checked_state()
    for row in rows:
        review=reviews.get(row['id']);parts=[results[k]['status'] for k in row['code_checks']]
        if review and review['file_hashes']!=state: label=('зачтено для проверенного снимка' if review['passed'] else 'возвращено на исправление')+'; текущие файлы изменены'
        elif review:label='зачтено' if review['passed'] else 'возвращено на исправление'
        else:label='ожидает содержательного разбора'
        print(row['id']+' | '+row['title']+' | '+label+(' | код: '+','.join(parts) if parts else ''))
def submit():
    paths=bundle_paths();stamp=now();hashes=checked_state();tag=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()[:10]
    rel=Path('submissions')/(stamp+'-'+tag+'.zip');out=ROOT/rel
    if out.exists():raise ValueError('Такой снимок уже существует')
    out.parent.mkdir(exist_ok=True)
    meta={'created':stamp,'files':hashes,'week':'week01','code_checks':checks(),'python':platform.python_version()}
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for p in paths:z.write(p,p.relative_to(ROOT))
        z.writestr('SUBMISSION.json',json.dumps(meta,ensure_ascii=False,indent=2))
    log=read('progress/submissions.json');log.append({'file':str(rel),'sha256':digest(out),'created':stamp});write('progress/submissions.json',log)
    print('Пакет для разбора: '+str(rel));print('Пришли этот архив в чат вместе с конкретными вопросами. Оценка появится после разбора.')
def record_review(path):
    payload=json.loads(Path(path).read_text());items={x['id']:x for x in read('course.json')['assignments']};i=payload.get('assignment')
    if i not in items:raise ValueError('Неизвестное задание')
    for k in ['reviewer','source','feedback']:
        if not isinstance(payload.get(k),str) or not payload[k].strip():raise ValueError('Заполни '+k)
    criteria=payload.get('criteria',{});expected={'derivation','assumptions','calculations','interpretation','reproducibility'}
    if set(criteria)!=expected or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not 0<=v<=20 for v in criteria.values()):raise ValueError('Пять критериев по0…20 баллов')
    if type(payload.get('oral_passed')) is not bool or type(payload.get('critical_errors')) is not bool:raise ValueError('oral_passed и critical_errors должны быть true/false')
    result=checks();score=sum(criteria.values());code_ok=all(result[k]['status']=='passed' for k in items[i]['code_checks'])
    passed=score>=read('course.json')['pass_score'] and not payload['critical_errors'] and payload['oral_passed'] and code_ok
    record=dict(payload,score=score,passed=passed,recorded=now(),code_checks={k:result[k] for k in items[i]['code_checks']},file_hashes=checked_state())
    current=read('progress/reviews.json');current[i]=record;write('progress/reviews.json',current);write('feedback/'+i+'-'+now()+'.json',record)
    print(i+': '+str(score)+'/100; '+('зачтено' if passed else 'нужны исправления/защита'))
def environment():
    print('Python',platform.python_version())
    for name in ['numpy','pandas','scipy','matplotlib','ipykernel','jupyterlab']:
        try:
            import importlib.metadata
            print(name,importlib.metadata.version(name))
        except importlib.metadata.PackageNotFoundError:print(name,'не установлен')
def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['status','selfcheck','submit','record-review','environment']);p.add_argument('file',nargs='?');a=p.parse_args()
    if a.command=='status':status()
    elif a.command=='selfcheck':return selfcheck()
    elif a.command=='submit':submit()
    elif a.command=='environment':environment()
    elif not a.file:p.error('Для record-review укажи JSON-файл разбора')
    else:record_review(a.file)
    return 0
if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,FileNotFoundError,json.JSONDecodeError) as e:print('Ошибка:',e);sys.exit(2)
