"""Проверка структуры курса; этот результат не является оценкой учащегося."""
from pathlib import Path
import json, ast, re

ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'course.json').read_text())
assert manifest['hours']==sum(x['hours'] for x in manifest['assignments'])==48
assert len(manifest['assignments'])==9
assert len({x['id'] for x in manifest['assignments']})==9
for a in manifest['assignments']:
    assert (ROOT/a['file']).is_file(),a['file']
    assert (ROOT/'work/week01'/f"{a['id']}.md").is_file()
for folder in ['study','work','tools']:
    for p in (ROOT/folder).rglob('*.py'):
        if '__pycache__' not in p.parts:ast.parse(p.read_text(),str(p))
ast.parse((ROOT/'course.py').read_text())
notebooks=list((ROOT/'notebooks').glob('*.ipynb'))
assert len(notebooks)==5
for p in notebooks:
    n=json.loads(p.read_text());assert n['nbformat']==4 and n['nbformat_minor']==5
    ids=[c['id'] for c in n['cells']];assert len(ids)==len(set(ids))
    for c in n['cells']:
        assert c['cell_type'] in ['markdown','code']
        if c['cell_type']=='code':compile(''.join(c['source']),str(p),'exec')
text=(ROOT/'_toc.yml').read_text()
for path in re.findall(r'(?:file|root): (.+)',text):
    assert any((ROOT/(path.strip()+ext)).is_file() for ext in ['.md','.ipynb']),path
for path in ['README.md','START_HERE.html','requirements.txt','_config.yml','docs/WORKFLOW.md','docs/VERIFICATION.md','literature/references.bib']:
    assert (ROOT/path).is_file(),path
print('Infrastructure integrity passed: 9 assignments, 5 notebooks, 48 planned hours.')
