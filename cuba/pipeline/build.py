"""Inline the textures and anchors into template.html -> dist/cuba.html (fragment, what the artifact is published from)
and dist/cuba_world.html (the same wrapped in a full document, the standalone file)."""
import base64, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), 'dist')
os.makedirs(OUT, exist_ok=True)


def b64(name):
    return 'data:image/jpeg;base64,' + base64.b64encode(open(os.path.join(HERE, name), 'rb').read()).decode()


page = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
data = json.load(open(os.path.join(HERE, 'anchors.json')))
for key, val in (('TEX_CANON', b64('map_canon.jpg')), ('TEX_FAR', b64('map_far.jpg')), ('TEX_BLANK', b64('map_blank.jpg')),
                 ('TEX_EAST', b64('map_east.jpg')), ('TEX_WEST', b64('map_west.jpg')), ('TEX_NORTH', b64('map_north.jpg')), ('TEX_SOUTH', b64('map_south.jpg')),
                 ('ANCHORS', json.dumps(data))):
    assert '{{' + key + '}}' in page, key
    page = page.replace('{{' + key + '}}', val)
assert '{{' not in page, 'a placeholder was left unreplaced'
open(os.path.join(OUT, 'cuba.html'), 'w', encoding='utf-8').write(page)
standalone = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
              '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
              '</head>\n<body>\n' + page + '\n</body>\n</html>\n')
open(os.path.join(OUT, 'cuba_world.html'), 'w', encoding='utf-8').write(standalone)
print('wrote dist/cuba.html and dist/cuba_world.html;', 'fragment bytes', len(page.encode()), 'standalone bytes', len(standalone.encode()))
