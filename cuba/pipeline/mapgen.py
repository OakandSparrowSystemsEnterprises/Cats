"""Cuba, the cube planet: the face textures.

Only the Canon side is drawn (Ruby, 2026-10-04, from the description of her picture and her words): a central island shaped like a
broad cross, with arms toward the middle of each side and recessed, rounded corners, and a small hole at its centre that takes you
through the world to the Far side. Ruby: "the arms connect to the north south east and west faces", so the arms reach the four
sides and the land crosses onto the East, West, North and South sides. Readings taken here, all marked in HANDOFF.md: on those four
sides the land continues a short way (TONGUE) and stops, the rest of them being uncharted slate; the hole is small; the Far side gets
the hole's other end and nothing else. Colours are placeholders, nothing about them has been said.

Ruby (2026-10-04): "make cuba look sort of like tetra as far as how landmasses are desighnd": the land is painted with Tetra's own
painter (../../tetra/pipeline: heights, render_painted, texsynth patches from Ruby's Canon painting), so the Plus Continent carries the
same painted hills, forests, shores and rivers as Tetra's faces. Which plants and colours belong where is still unwritten; the zones
here (green and forest, a little gold at the shore) are a reading.

Writes map_canon.jpg, map_east/west/north/south.jpg (the tongue of land at the edge shared with Canon), map_far.jpg (the hole's other
end), map_blank.jpg, map_canon_prev.png (markers drawn) and anchors.json. Deterministic (fixed seed).
"""
import json, os, sys, numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
TETRA = os.path.normpath(os.path.join(HERE, '..', '..', 'tetra', 'pipeline'))
sys.path.insert(0, TETRA); os.chdir(TETRA)          # Tetra's painter reads art_latest.png from its own folder
from mapgen2 import heights                          # noqa: E402
from paintface import render_painted                 # noqa: E402
S = 1024
SEED = 7
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
cx = cy = S / 2

# the island, in face pixels (the face is S by S, north at the top)
CENTRE = 0.19 * S      # half-width of the broad centre
ARM_W = 0.105 * S      # half-width of an arm
ARM_LEN = 0.56 * S     # the arms run past the sides, so the land crosses the edges (Ruby: the arms connect to the four faces)
TONGUE = 0.14 * S      # how far the land continues onto the neighbouring side (a reading; nothing said)
EDGE_CALM = 48         # px over which the wobble dies out toward an edge, so both sides of an edge agree
FILLET = 0.07 * S      # the rounded bends where the arms meet the centre
WOBBLE = 0.030 * S     # a hand-drawn coast
HOLE_R = 0.022 * S     # the small hole at the centre


def noise(shape, cell, seed):
    r = np.random.default_rng(seed)
    small = r.random((shape[0] // cell + 2, shape[1] // cell + 2)).astype(np.float32)
    return cv2.resize(small, (shape[1], shape[0]), interpolation=cv2.INTER_CUBIC)


def fbm(seed, cells=(256, 128, 64, 32), weights=(1, .5, .25, .125)):
    n = sum(w * noise((S, S), c, seed + i) for i, (c, w) in enumerate(zip(cells, weights)))
    return (n - n.min()) / (n.max() - n.min())


def rrect(hw, hh, r):
    """signed distance to a rounded rectangle centred on the face"""
    dx = np.abs(xx - cx) - hw + r
    dy = np.abs(yy - cy) - hh + r
    return np.hypot(np.maximum(dx, 0), np.maximum(dy, 0)) + np.minimum(np.maximum(dx, dy), 0) - r


def smin(a, b, k):
    """smooth union of two signed distances: the rounded bend where two shapes meet"""
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b + (a - b) * h - k * h * (1 - h)


def edge_calm():
    """1 in the middle of the face, 0 at the sides: the coast is drawn calm where it crosses an edge"""
    m = np.minimum(np.minimum(xx, S - 1 - xx), np.minimum(yy, S - 1 - yy))
    return np.clip(m / EDGE_CALM, 0, 1)


def island():
    d = smin(rrect(CENTRE, CENTRE, 0.05 * S), rrect(ARM_LEN, ARM_W, 0.04 * S), FILLET)
    d = smin(d, rrect(ARM_W, ARM_LEN, 0.04 * S), FILLET)
    d = d + (fbm(SEED) - 0.5) * 2 * WOBBLE * edge_calm()
    return d


def tongue():
    """the land continuing onto a neighbouring side, drawn with the tongue at the TOP edge, centred; rotated per side"""
    dx = np.abs(xx - cx) - ARM_W
    dy = yy - TONGUE
    d = np.hypot(np.maximum(dx, 0), np.maximum(dy, 0)) + np.minimum(np.maximum(dx, dy), 0)
    d = d + (fbm(SEED + 5) - 0.5) * 2 * WOBBLE * edge_calm()
    return d


TRI = np.ones((S, S), bool)                           # a square face: the whole texture is the face


def painted(d, seed, rivers=()):
    """Tetra's painter over a signed-distance land design: heights, zones (green and forest, gold along the shore: a reading), rivers."""
    land_soft = np.clip(0.5 - d / 6.0, 0, 1)
    h, d_in = heights(land_soft, seed, terrain_amp=0.06)
    # relief is a reading: gentle hills over the land and one high hub around the middle, so the painter's mountains gather there and not everywhere
    hub = np.clip(1 - np.hypot(xx - cx, yy - cy) / (0.21 * S), 0, 1) ** 1.5
    h = np.where(land_soft > 0.5, h + 0.09 * hub, h).astype(np.float32)
    n = fbm(seed + 41)
    zones = {'green': np.clip(0.55 + 0.6 * (n - 0.5), 0, 1), 'forest': np.clip(0.45 + 0.8 * (0.5 - n), 0, 1),
             'gold': np.clip(1 - d_in / 40.0, 0, 1) * 0.5}
    img = render_painted({'height': h, 'sea_level': 0.5, 'zones': zones, 'river_sources': list(rivers)}, seed, TRI)
    return img.astype(np.float32)


def render_canon():
    d = island()
    land = d < 0
    hole = np.hypot(xx - cx, yy - cy) < HOLE_R
    tex = painted(d, SEED, rivers=[(int(0.5 * S), int(0.22 * S)), (int(0.78 * S), int(0.5 * S)), (int(0.5 * S), int(0.8 * S))])
    hole_shade = np.clip(1 - (np.hypot(xx - cx, yy - cy) - HOLE_R) / (HOLE_R * 1.6), 0, 1)
    tex *= (1 - 0.45 * hole_shade)[..., None]
    tex[hole] = np.array([14, 12, 20], np.float32)
    return np.clip(tex, 0, 255).astype(np.uint8), land, hole


def render_blank(with_hole=False, with_tongue=False):
    tex = np.zeros((S, S, 3), np.float32)
    slate = np.array([64, 68, 80], np.float32)
    tex[:] = slate * (0.86 + 0.28 * fbm(SEED + 31)[..., None])
    if with_tongue:   # the arm's land painted like the Canon side, its sea fading into the uncharted slate away from the coast
        d = tongue(); img = painted(d, SEED + 7)
        keep = np.clip(1 - (d - 24.0) / 40.0, 0, 1)[..., None]
        tex = img * keep + tex * (1 - keep)
    if with_hole:
        r = np.hypot(xx - cx, yy - cy)
        tex *= (1 - 0.45 * np.clip(1 - (r - HOLE_R) / (HOLE_R * 1.6), 0, 1))[..., None]
        tex[r < HOLE_R] = np.array([14, 12, 20], np.float32)
    return np.clip(tex, 0, 255).astype(np.uint8)


def write_jpg(name, rgb):
    cv2.imwrite(os.path.join(HERE, name), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])


def main():
    canon, land, hole = render_canon()
    # checks: one piece of land, its four arms reaching the middle of each side, the corners water, the hole in the middle
    n, _ = cv2.connectedComponents(land.astype(np.uint8))
    assert n == 2, f'the land is {n - 1} pieces'
    for px, py in ((S // 2, 0), (S // 2, S - 1), (0, S // 2), (S - 1, S // 2)):
        assert land[py, px], f'an arm does not reach the side at ({px},{py})'
    q = int(0.25 * S)
    assert not land[0, :q].any() and not land[0, -q:].any() and not land[-1, :q].any() and not land[-1, -q:].any(), 'land at a corner edge'
    # the land agrees across the four edges: Canon's edge rows against the tongue's top row (the tongue texture is rotated per side)
    t = tongue() < 0
    for canon_edge in (land[0, :], land[-1, :], land[:, 0], land[:, -1]):
        agree = (canon_edge == t[0, :]).mean()
        assert agree > 0.985, f'edge agreement {agree:.3f}'
    for px, py in ((int(0.2 * S), int(0.2 * S)), (int(0.8 * S), int(0.2 * S)), (int(0.2 * S), int(0.8 * S)), (int(0.8 * S), int(0.8 * S))):
        assert not land[py, px], f'the corner at ({px},{py}) is land'
    assert hole[S // 2, S // 2] and land[S // 2, S // 2 + int(HOLE_R) + 8]
    water = 1 - land.mean()
    anchors = {'canon': {'island': [S // 2, int(0.30 * S)], 'hole': [S // 2, S // 2]}, 'far': {'hole-far': [S // 2, S // 2]}}
    ax, ay = anchors['canon']['island']; assert land[ay, ax] and not hole[ay, ax]
    os.chdir(HERE)
    write_jpg('map_canon.jpg', canon)
    write_jpg('map_far.jpg', render_blank(with_hole=True))
    write_jpg('map_blank.jpg', render_blank())
    # the neighbouring sides, tongue at the edge they share with Canon: East's right edge, West's left, North's bottom, South's top
    base = render_blank(with_tongue=True)                  # tongue at the top edge
    write_jpg('map_south.jpg', base)
    write_jpg('map_north.jpg', np.ascontiguousarray(np.rot90(base, 2)))
    write_jpg('map_east.jpg', np.ascontiguousarray(np.rot90(base, -1)))    # top -> right
    write_jpg('map_west.jpg', np.ascontiguousarray(np.rot90(base, 1)))     # top -> left
    prev = cv2.cvtColor(canon, cv2.COLOR_RGB2BGR).copy()
    for (px, py) in anchors['canon'].values():
        cv2.circle(prev, (px, py), 9, (40, 220, 255), 2)
    cv2.imwrite(os.path.join(HERE, 'map_canon_prev.png'), prev)
    json.dump({'anchors': anchors, 'water_canon': round(float(water), 4), 'hole_radius_px': HOLE_R, 'size': S},
              open(os.path.join(HERE, 'anchors.json'), 'w'), indent=1)
    print(f'canon: water {water:.3f}, land one piece reaching all four sides, hole radius {HOLE_R:.0f}px; wrote map_canon.jpg, map_east/west/north/south.jpg, map_far.jpg, map_blank.jpg, anchors.json')


if __name__ == '__main__':
    main()
