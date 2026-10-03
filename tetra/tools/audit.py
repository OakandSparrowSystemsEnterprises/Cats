"""Pre-ship audit: no em dashes, no retired names, no leftover placeholders, in the sources and in dist/ (base64 stripped).
Exit code 1 on any hit. Add retired names to RETIRED when Ruby renames or removes something."""
import re, sys, os, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EM = '—'
RETIRED = ['Mtlshia', 'Tueldan', 'The Swamp', "name:'Tropical'", 'Sunreach', 'Evermere', 'Stonehollow', 'Mistwater',
           'Frostmarch', 'Greenveld', 'Deepwood', 'Stormreach', 'snowy tundra', 'Snowy tundra', 'The Hot Kingdom', 'Uohia']
files = (glob.glob(os.path.join(ROOT, 'pipeline', '*.py')) + glob.glob(os.path.join(ROOT, 'pipeline', 'template.html')) +
         glob.glob(os.path.join(ROOT, 'dist', '*.html')) + glob.glob(os.path.join(ROOT, '*.md')) + glob.glob(os.path.join(ROOT, 'tests', '*.js')) +
         # em dashes only, in the rest of the text: legacy scripts, archived tests, tools, the reference notes, the Makefile and manifests
         glob.glob(os.path.join(ROOT, 'pipeline', 'legacy', '*.py')) + glob.glob(os.path.join(ROOT, 'tests', 'archive', '*.js')) +
         glob.glob(os.path.join(ROOT, 'tools', '*.py')) + glob.glob(os.path.join(ROOT, 'reference', '*.md')) +
         [os.path.join(ROOT, f) for f in ('Makefile', 'package.json', 'requirements.txt', '.gitignore')])
bad = 0
for f in sorted(files):
    txt = open(f, encoding='utf-8').read()
    txt = re.sub(r'data:[a-z/+-]+;base64,[A-Za-z0-9+/=]+', '', txt)
    rel = os.path.relpath(f, ROOT)
    n = txt.count(EM)
    if n and not rel.endswith('audit.py'):
        bad += 1; print(f'{rel}: {n} em dash(es)')
    if '{{' in txt and rel.startswith('dist'):
        bad += 1; print(f'{rel}: unreplaced placeholder')
    live = rel.startswith('dist') or rel.startswith('tests') or os.path.basename(rel) in ('template.html', 'build.py', 'nations.py', 'mapgen2.py')
    for name in RETIRED:            # only the files that feed the shipped page; mapgen.py's superseded designer keeps its old labels
        if live and name in txt:
            bad += 1; print(f'{rel}: retired name {name!r}')
print('audit', 'FAILED' if bad else 'clean', f'({len(files)} files)')
sys.exit(1 if bad else 0)
