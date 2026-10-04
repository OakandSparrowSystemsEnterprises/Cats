import base64, json, os
here = os.path.dirname(os.path.abspath(__file__))
tpl = open(os.path.join(here, 'template.html'), encoding='utf-8').read()
def b64(name, mime='image/jpeg'):
    return f'data:{mime};base64,' + base64.b64encode(open(os.path.join(here, name), 'rb').read()).decode('ascii')
geo = json.load(open(os.path.join(here, 'geometry.json')))
from nations import ISLAND_NATIONS, CONTINENT_NATIONS
names = {'spike': 'Spikia \u00b7 the spike', 'delta': 'Wetia', 'tropicia': 'Tropicia',
         'spike-south': 'Spikia \u00b7 the spike', 'delta-south': 'Wetia',
         'celestial': 'Mount Celestial', 'delta-far': 'Wetia', 'warmia': 'Warmia', 'ehia': 'Ehia', 'treeland': 'Tree Land'}
APEX, BL, BR = (512.0, 75.52), (8.0, 948.48), (1016.0, 948.48)
def bary_of(px):
    (x, y), (x1, y1), (x2, y2), (x3, y3) = px, APEX, BL, BR
    det = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
    l1 = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / det
    l2 = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / det
    return [round(l1, 4), round(l2, 4), round(1 - l1 - l2, 4)]
anchors = json.load(open(os.path.join(here, 'map_anchors.json')))
extra = []
for face in ('west', 'south', 'far'):
    for k, px in anchors[face].items():
        if k in names: extra.append(dict(id=k, name=names[k], face=face, b=bary_of(px)))
I = anchors['west']['island']
extra += [dict(id=i, name=n, face='west', b=bary_of((I[0] + dx, I[1] + dy))) for i, n, (dx, dy), _ in ISLAND_NATIONS]
C = anchors['south']['continent-south']
extra += [dict(id=i, name=n, face='south', b=bary_of((C[0] + dx, C[1] + dy))) for i, n, (dx, dy), _ in CONTINENT_NATIONS]
# the Canon regions keep their order and names from geometry.json (the painting) but sit where mapgen2 settled them on the generated map
canon_name = {r['id']: r['name'] for r in geo['regions'] if r['face'] == 'canon'}
canon = [dict(id=k, name=canon_name[k], face='canon', b=bary_of(anchors['canon'][k])) for k in canon_name if k in anchors['canon']]
assert len(canon) == len(canon_name), 'a Canon region has no anchor on the generated map'
geo['regions'] = canon + extra
# Cuba, the cube planet, lives in this same page (Ruby, 2026-10-04): its fragment and textures come from ../../cuba/pipeline
cuba_dir = os.path.normpath(os.path.join(here, '..', '..', 'cuba', 'pipeline'))
def cb64(name):
    return 'data:image/jpeg;base64,' + base64.b64encode(open(os.path.join(cuba_dir, name), 'rb').read()).decode('ascii')
cuba = open(os.path.join(cuba_dir, 'world.html'), encoding='utf-8').read()
for key, name in (('TEX_CANON', 'map_canon.jpg'), ('TEX_EAST', 'map_east.jpg'), ('TEX_WEST', 'map_west.jpg'), ('TEX_NORTH', 'map_north.jpg'),
                  ('TEX_SOUTH', 'map_south.jpg'), ('TEX_FAR', 'map_far.jpg'), ('TEX_BLANK', 'map_blank.jpg')):
    assert '{{CUBA_' + key + '}}' in cuba, key
    cuba = cuba.replace('{{CUBA_' + key + '}}', cb64(name))
cuba = cuba.replace('{{CUBA_ANCHORS}}', json.dumps(json.load(open(os.path.join(cuba_dir, 'anchors.json'))), separators=(',', ':')))
assert '{{' not in cuba, 'a Cuba placeholder was left unreplaced'
page = (tpl.replace('{{CUBA}}', cuba)
           .replace('{{TEX_CANON}}', b64('map_canon.jpg'))
           .replace('{{TEX_WEST}}', b64('map_west.jpg'))
           .replace('{{TEX_SOUTH}}', b64('map_south.jpg'))
           .replace('{{TEX_FAR}}', b64('map_far.jpg'))
           .replace('{{ZINNIA}}', b64('zinnia_q.png', 'image/png'))
           .replace('{{MAP_CANON}}', b64('codex_canon.jpg'))
           .replace('{{MAP_WEST}}', b64('codex_west.jpg'))
           .replace('{{MAP_SOUTH}}', b64('codex_south.jpg'))
           .replace('{{MAP_FAR}}', b64('codex_far.jpg'))
           .replace('{{MAP_ISLAND}}', b64('codex_island.jpg'))
           .replace('{{MAP_CONTINENT}}', b64('codex_continent.jpg'))
           .replace('{{GEOMETRY}}', json.dumps(geo, separators=(',', ':'))))
assert '{{' not in page
out_dir = os.environ.get('TETRA_OUT') or os.path.normpath(os.path.join(here, '..', 'dist'))
os.makedirs(out_dir, exist_ok=True)
open(os.path.join(out_dir, 'tetra.html'), 'w', encoding='utf-8').write(page)
standalone = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
              '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
              '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}[hidden]{display:none!important}</style>\n'
              '</head>\n<body>\n' + page + '\n</body>\n</html>\n')
open(os.path.join(out_dir, 'tetra_world.html'), 'w', encoding='utf-8').write(standalone)
print('wrote', os.path.join(out_dir, 'tetra.html'), 'and tetra_world.html;', 'fragment bytes', len(page.encode()), 'standalone bytes', len(standalone.encode()))
