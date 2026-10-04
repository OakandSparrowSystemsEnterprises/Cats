"""Pre-ship audit for Cuba: no em dashes anywhere, no unreplaced placeholders in dist/. Exit 1 on any hit."""
import glob, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files = (glob.glob(os.path.join(ROOT, 'pipeline', '*.py')) + glob.glob(os.path.join(ROOT, 'pipeline', 'template.html')) +
         glob.glob(os.path.join(ROOT, 'dist', '*.html')) + glob.glob(os.path.join(ROOT, '*.md')) + glob.glob(os.path.join(ROOT, 'tests', '*.js')) +
         glob.glob(os.path.join(ROOT, 'tools', '*.py')) + glob.glob(os.path.join(ROOT, 'reference', '**', '*.md'), recursive=True) +
         [os.path.join(ROOT, f) for f in ('Makefile', 'package.json')])
bad = 0
for f in sorted(files):
    txt = re.sub(r'data:[a-z/+-]+;base64,[A-Za-z0-9+/=]+', '', open(f, encoding='utf-8').read())
    rel = os.path.relpath(f, ROOT)
    n = txt.count('—')
    if n and not rel.endswith('audit.py'):
        bad += 1; print(f'{rel}: {n} em dash(es)')
    if '{{' in txt and rel.startswith('dist'):
        bad += 1; print(f'{rel}: unreplaced placeholder')
print('audit', 'FAILED' if bad else 'clean', f'({len(files)} files)')
sys.exit(1 if bad else 0)
