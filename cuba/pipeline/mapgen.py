"""Cuba, the cube planet: the face textures.

Only the Canon side is drawn (Ruby, 2026-10-04, from the description of her picture and her words): a central island shaped like a
broad cross, with arms toward the middle of each side and recessed, rounded corners, and a small hole at its centre that takes you
through the world to the Far side. Ruby: "the arms connect to the north south east and west faces", so the arms reach the four
sides and the land crosses onto the East, West, North and South sides. Readings taken here, all marked in HANDOFF.md: on those four
sides the land continues a short way (TONGUE) and stops, the rest of them being uncharted slate; the hole is small; the Far side gets
the hole's other end and nothing else. Colours are placeholders, nothing about them has been said.

Writes map_canon.jpg, map_east/west/north/south.jpg (the tongue of land at the edge shared with Canon), map_far.jpg (the hole's other
end), map_blank.jpg, map_canon_prev.png (markers drawn) and anchors.json. Deterministic (fixed seed).
"""
import json, os, numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
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


def paint_land(tex, d, land):
    """placeholder land colours: sand at the shore, grass inland, a drawn coastline"""
    inland = np.clip(-d / 120.0, 0, 1)
    sand = np.array([206, 186, 140], np.float32); grass = np.array([128, 150, 92], np.float32)
    ground = sand[None, None] * (1 - inland[..., None]) + grass[None, None] * inland[..., None]
    ground *= 0.86 + 0.28 * fbm(SEED + 23)[..., None]
    tex[land] = ground[land]
    rim = (d > -3) & (d < 1)
    tex[rim] *= 0.72


def render_canon():
    d = island()
    land = d < 0
    hole = np.hypot(xx - cx, yy - cy) < HOLE_R
    # colours are placeholders (nothing said yet): a sea blue, a sand and grass land, the hole dark
    tex = np.zeros((S, S, 3), np.float32)
    depth = np.clip(d / 90.0, 0, 1)                       # distance from the coast, 0 at the shore
    sea_deep = np.array([34, 70, 112], np.float32); sea_shallow = np.array([70, 128, 170], np.float32)
    sea = sea_shallow[None, None] * (1 - depth[..., None]) + sea_deep[None, None] * depth[..., None]
    sea *= 0.92 + 0.16 * fbm(SEED + 11)[..., None]
    tex[~land] = sea[~land]
    paint_land(tex, d, land)
    hole_shade = np.clip(1 - (np.hypot(xx - cx, yy - cy) - HOLE_R) / (HOLE_R * 1.6), 0, 1)
    tex *= (1 - 0.45 * hole_shade)[..., None]
    tex[hole] = np.array([14, 12, 20], np.float32)
    return np.clip(tex, 0, 255).astype(np.uint8), land, hole


def render_blank(with_hole=False, with_tongue=False):
    tex = np.zeros((S, S, 3), np.float32)
    slate = np.array([64, 68, 80], np.float32)
    tex[:] = slate * (0.86 + 0.28 * fbm(SEED + 31)[..., None])
    if with_tongue:
        d = tongue(); paint_land(tex, d, d < 0)
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
