"""Cuba, the cube planet: the face textures.

The Canon side (Ruby, 2026-10-04, from the description of her picture and her words): a central island shaped like a
broad cross, with arms toward the middle of each side and recessed, rounded corners, and a small hole at its centre that takes you
through the world to the Far side. Ruby: "the arms connect to the north south east and west faces", so the arms reach the four
sides and the land crosses onto the East, West, North and South sides. Readings taken here, all marked in HANDOFF.md: on those four
sides the land continues as far as her later sketches show (ARM_REACH, below); the hole is small. Colours are
placeholders, nothing about them has been said.

The Far side (Ruby, 2026-10-05): "the far side has a main island about a quarter of the sise of the face with land on the north east and
south east corners, making it half water. on the central island, north of the canyon, there is a volcano (active) (shoots lava every
reset day)". So: a main island of a quarter of the face's area around the Canyon's other end, two corner lands of an eighth each in
the north-east and south-east corners (the texture's right is East on this side: looking at Far with North up, East is on the right),
the face half water, and the volcano north of the hole on the island. Readings: the island is round, the corner lands are rounded
wedges and equal in size (an eighth each), the volcano's place north of the hole and its size. What continues past the Far side's edges onto East, North and South is
unwritten; the Far side's edges are not asserted against its neighbours.

The other four sides (Ruby, 2026-10-06, her sketches of the explorers' maps, saved in ../reference/ruby/): the North side explored by
Aquamarine, the East side discovered by Axinite, the South side by Benitoite, the West side from Chrysoberyl's map. Each sketch is read in
the texture's own orientation (row 0 the top): North has Far at the top, Canon at the bottom, East on the left and West on the right;
East has North at the top, Far on the left, Canon on the right; South has Canon at the top, Far at the bottom, East on the left (her
sketch is turned a quarter, with Canon on its right); West has North at the top, Canon on the left, Far on the right. The Plus
Continent's arm reaches onto each side as far as the sketch shows (ARM_REACH), the land shapes follow the sketches as ellipses (readings of
rough drawings); the spiral on the North side and the ringed blob with a dark dot on the West side are portals standing in
open sea (Ruby, 2026-10-10: "The rings that were drawn as “islands” were actualy portals. No crescent land, bouth spiral islands are
portals in the ocean"), painted as purple swirls on the water (purple is the colour of magic in her comics: a reading), and the crescent
that was first read on the East sketch is gone; where two sketches disagree about a shared edge the constants were set by hand so
the two textures meet (asserted in main for every edge between two drawn sides, as for Canon's). Nothing on them is named.

Ruby (2026-10-04): "make cuba look sort of like tetra as far as how landmasses are desighnd": the land is painted with Tetra's own
painter (../../tetra/pipeline: heights, render_painted, texsynth patches from Ruby's Canon painting), so the Plus Continent carries the
same painted hills, forests, shores and rivers as Tetra's faces. Which plants and colours belong where is still unwritten; the zones
here (green and forest, a little gold at the shore) are a reading.

Writes map_canon.jpg, map_north/east/south/west.jpg (from the sketches), map_far.jpg (the main island, the corner lands, the volcano and
the hole's other end), map_blank.jpg (unused now, kept as the page's fallback texture), map_*_prev.png (markers drawn) and anchors.json.
Deterministic (fixed seed).
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
ARM_REACH = {'north': 0.34, 'east': 0.23, 'south': 0.22, 'west': 0.31}   # how far the arm runs onto each side, as a fraction of the side, measured on Ruby's sketches of 2026-10-06 (she says she does not know yet; this is what the explorers drew)
EDGE_CALM = 48         # px over which the wobble dies out toward an edge, so both sides of an edge agree
FILLET = 0.07 * S      # the rounded bends where the arms meet the centre
WOBBLE = 0.030 * S     # a hand-drawn coast
HOLE_R = 0.022 * S     # the small hole at the centre
# the Far side (Ruby, 2026-10-05)
FAR_R = S * (0.25 / np.pi) ** 0.5     # a round main island of a quarter of the face's area, about the hole (its roundness is a reading)
FAR_CORNER_A = 0.355 * S              # the corner lands: quarter ellipses on the north-east and south-east corners, an eighth of the face each
FAR_CORNER_B = 0.45 * S               # (A along the top or bottom edge, B down the east edge; the wedge shape is a reading)
FAR_WOBBLE = 0.6 * WOBBLE             # a calmer coast, so the straits between the island and the corner lands stay open
VOLCANO = (S // 2, int(0.34 * S))     # north of the Canyon's other end, on the main island (how far north is a reading)
VOLCANO_R = 0.055 * S                 # the dark rock around the vent on the texture; the cone itself is a mesh in the page (a reading)
# the four sides from the sketches (fractions of the side; readings of rough drawings, see the module docstring)
NORTH_LAND = (-0.05, 0.26, 0.49, 0.46)   # ellipse centre x, y and radii: the big land on the East (left) edge, reaching the Far (top) edge; set so its edges meet the Far side's corner land (0.355 along the top) and the East side's land (about 0.71 down the left)
NORTH_PORTAL = (0.70, 0.39, 0.10)        # the spiral she drew: a portal in the sea, centre and the swirl's radius
EAST_NF = (-0.10, -0.10, 0.82, 0.55)     # the land in the North-Far (top left) corner; rx set so its top edge reaches about 0.70, where the North side's land meets it
EAST_SF = (-0.12, 1.05, 0.369, 0.52)     # the land in the South-Far (bottom left) corner; rx set so its bottom edge meets the South side's corner land (0.247 along it)
SOUTH_EF = (-0.05, 1.08, 0.40, 0.33)     # the land in the East-Far (bottom left) corner
WEST_PORTAL = (0.48, 0.64, 0.11)         # the ringed blob with the dark dot on Chrysoberyl's map: a portal in the sea, centre and the swirl's radius
PORTALS = {'north': NORTH_PORTAL, 'west': WEST_PORTAL}
SIDE_WOBBLE = 0.6 * WOBBLE


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


def rbox(x0, y0, hw, hh, r=0.0):
    """signed distance to a rounded box centred at (x0, y0)"""
    dx = np.abs(xx - x0) - hw + r
    dy = np.abs(yy - y0) - hh + r
    return np.hypot(np.maximum(dx, 0), np.maximum(dy, 0)) + np.minimum(np.maximum(dx, dy), 0) - r


def ellipse(x0, y0, rx, ry):
    """about the signed distance to an ellipse (fractions of S)"""
    e = np.hypot((xx - x0 * S) / (rx * S), (yy - y0 * S) / (ry * S))
    return (e - 1) * min(rx, ry) * S


def arm_onto(side):
    """the Plus Continent's arm crossing onto a side from the edge it shares with Canon: North's bottom edge, East's right, South's top, West's left; ARM_W wide at the edge, as on Canon, reaching ARM_REACH[side] in"""
    L = ARM_REACH[side] * S + 0.1 * S
    if side == 'north':
        return rbox(cx, S + 0.1 * S, ARM_W, L, 0.04 * S)
    if side == 'south':
        return rbox(cx, -0.1 * S, ARM_W, L, 0.04 * S)
    if side == 'east':
        return rbox(S + 0.1 * S, cy, L, ARM_W, 0.04 * S)
    return rbox(-0.1 * S, cy, L, ARM_W, 0.04 * S)


def wob(seed):
    return (fbm(seed) - 0.5) * 2 * SIDE_WOBBLE * edge_calm()


def design_side(side):
    """the land of one of the four sides from Ruby's sketch: returns the signed distance and the place to gather the relief (or None)"""
    d = arm_onto(side)
    if side == 'north':
        d = np.minimum(d, ellipse(*NORTH_LAND))
        return d + wob(SEED + 21), None
    if side == 'east':
        d = np.minimum(d, ellipse(*EAST_NF))
        d = np.minimum(d, ellipse(*EAST_SF))
        return d + wob(SEED + 23), None
    if side == 'south':
        d = np.minimum(d, ellipse(*SOUTH_EF))
        return d + wob(SEED + 25), None
    return d + wob(SEED + 27), None


def portal(tex, x0, y0, r0):
    """a portal in the sea: a purple swirl, bright on its rings and dark at its middle (what a portal looks like is unwritten; this is a reading)"""
    dx, dy = xx - x0 * S, yy - y0 * S
    r = np.hypot(dx, dy) / (r0 * S)
    th = np.arctan2(dy, dx)
    swirl = 0.5 + 0.5 * np.cos(2 * np.pi * (r * 2.5) - th)       # two and a half turns of a spiral
    body = np.clip(1 - (r - 0.85) / 0.15, 0, 1) * (r < 1.0)
    eye = np.clip(1 - r / 0.18, 0, 1)
    glow = np.clip(1 - (r - 1.0) / 0.35, 0, 1) * (r >= 1.0)
    k = (body * (0.35 + 0.55 * swirl) + 0.25 * glow)[..., None]
    violet = np.array([150, 70, 215], np.float32)
    tex = tex * (1 - 0.8 * k) + violet * (0.8 * k)
    tex = tex * (1 - 0.9 * eye[..., None]) + np.array([20, 8, 30], np.float32) * (0.9 * eye[..., None])
    return tex


def render_side(side, seed):
    d, hub = design_side(side)
    land = d < 0
    tex = painted(d, seed, hub_at=hub, hub_r=0.12 if hub else 0.21)
    if side in PORTALS:
        px, py, pr = PORTALS[side]
        assert not land[int(py * S), int(px * S)], f'the {side} portal is not in the sea'
        tex = portal(tex, px, py, pr)
    return np.clip(tex, 0, 255).astype(np.uint8), land


TRI = np.ones((S, S), bool)                           # a square face: the whole texture is the face


def far_land():
    """the Far side's land as a signed distance: the round main island about the hole, and the two corner lands"""
    d = np.hypot(xx - cx, yy - cy) - FAR_R
    for corner_y in (0.0, S - 1.0):                    # the north-east and the south-east corner; the texture's right is East on this side
        e = np.hypot((S - 1 - xx) / FAR_CORNER_A, (yy - corner_y) / FAR_CORNER_B)
        d = np.minimum(d, (e - 1) * min(FAR_CORNER_A, FAR_CORNER_B))
    return d + (fbm(SEED + 11) - 0.5) * 2 * FAR_WOBBLE * edge_calm()


def painted(d, seed, rivers=(), hub_at=None, hub_r=0.21):
    """Tetra's painter over a signed-distance land design: heights, zones (green and forest, gold along the shore: a reading), rivers."""
    land_soft = np.clip(0.5 - d / 6.0, 0, 1)
    h, d_in = heights(land_soft, seed, terrain_amp=0.06)
    # relief is a reading: gentle hills over the land and one high hub (around the middle, or around the volcano on the Far side), so the painter's mountains gather there and not everywhere
    hx, hy = hub_at or (cx, cy)
    hub = np.clip(1 - np.hypot(xx - hx, yy - hy) / (hub_r * S), 0, 1) ** 1.5
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


def render_far():
    """the Far side: the main island with the hole's other end and the volcano, the two corner lands, half water"""
    d = far_land()
    land = d < 0
    r_hole = np.hypot(xx - cx, yy - cy)
    hole = r_hole < HOLE_R
    tex = painted(d, SEED + 13, rivers=[(int(0.40 * S), int(0.56 * S)), (int(0.62 * S), int(0.61 * S))], hub_at=VOLCANO, hub_r=0.13)
    tex *= (1 - 0.45 * np.clip(1 - (r_hole - HOLE_R) / (HOLE_R * 1.6), 0, 1))[..., None]
    tex[hole] = np.array([14, 12, 20], np.float32)
    # the volcano's foot: dark rock around the vent (the cone is a mesh in the page)
    rv = np.hypot(xx - VOLCANO[0], yy - VOLCANO[1])
    rock = np.clip(1 - (rv - 0.5 * VOLCANO_R) / (0.9 * VOLCANO_R), 0, 1)[..., None]
    tex = tex * (1 - 0.6 * rock) + rock * np.array([46, 34, 32], np.float32) * 0.6
    tex[rv < 0.2 * VOLCANO_R] = np.array([34, 16, 12], np.float32)
    return np.clip(tex, 0, 255).astype(np.uint8), land, hole


def render_blank(with_hole=False):
    tex = np.zeros((S, S, 3), np.float32)
    slate = np.array([64, 68, 80], np.float32)
    tex[:] = slate * (0.86 + 0.28 * fbm(SEED + 31)[..., None])
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
    # the four sides from the sketches; the land agrees with Canon across the four shared edges (the arm is ARM_W wide at the edge on both)
    sides = {}
    for side, seed in (('north', SEED + 2), ('east', SEED + 3), ('south', SEED + 4), ('west', SEED + 5)):
        sides[side] = render_side(side, seed)
    for side, canon_edge, side_edge in (('north', land[0, :], sides['north'][1][-1, :]), ('south', land[-1, :], sides['south'][1][0, :]),
                                        ('east', land[:, 0], sides['east'][1][:, -1]), ('west', land[:, -1], sides['west'][1][:, 0])):
        agree = (canon_edge == side_edge).mean()
        assert agree > 0.985, f'edge agreement Canon/{side} {agree:.3f}'
    for px, py in ((int(0.2 * S), int(0.2 * S)), (int(0.8 * S), int(0.2 * S)), (int(0.2 * S), int(0.8 * S)), (int(0.8 * S), int(0.8 * S))):
        assert not land[py, px], f'the corner at ({px},{py}) is land'
    assert hole[S // 2, S // 2] and land[S // 2, S // 2 + int(HOLE_R) + 8]
    water = 1 - land.mean()
    # the Far side: half water, three pieces of land (the island and the two corner lands), the hole in the island, the volcano on it
    far, far_land_mask, far_hole = render_far()
    far_water = 1 - far_land_mask.mean()
    assert 0.46 < far_water < 0.54, f'the Far side is {far_water:.3f} water, not half'
    n_far, _ = cv2.connectedComponents(far_land_mask.astype(np.uint8))
    assert n_far == 4, f'the Far side has {n_far - 1} pieces of land, not three'
    assert far_land_mask[0, S - 1] and far_land_mask[S - 1, S - 1], 'no land on the north-east or the south-east corner'
    assert not far_land_mask[0, 0] and not far_land_mask[S - 1, 0], 'land on a west corner of the Far side'
    assert far_hole[S // 2, S // 2] and far_land_mask[VOLCANO[1], VOLCANO[0]]
    anchors = {'canon': {'island': [S // 2, int(0.30 * S)], 'hole': [S // 2, S // 2]},
               'far': {'hole-far': [S // 2, S // 2], 'far-island': [S // 2, int(0.68 * S)], 'volcano': list(VOLCANO), 'far-ne': [int(0.90 * S), int(0.10 * S)], 'far-se': [int(0.90 * S), int(0.90 * S)]},
               'north': {'arm-north': [S // 2, int(S - 0.5 * ARM_REACH['north'] * S)], 'north-land': [int(0.15 * S), int(0.40 * S)], 'north-portal': [int((NORTH_PORTAL[0] + 0.8 * NORTH_PORTAL[2]) * S), int(NORTH_PORTAL[1] * S)]},
               'east': {'arm-east': [int(S - 0.5 * ARM_REACH['east'] * S), S // 2], 'east-nf': [int(0.18 * S), int(0.15 * S)], 'east-sf': [int(0.06 * S), int(0.85 * S)]},
               'south': {'arm-south': [S // 2, int(0.5 * ARM_REACH['south'] * S)], 'south-ef': [int(0.10 * S), int(0.92 * S)]},
               'west': {'arm-west': [int(0.5 * ARM_REACH['west'] * S), S // 2], 'west-portal': [int((WEST_PORTAL[0] + 0.8 * WEST_PORTAL[2]) * S), int(WEST_PORTAL[1] * S)]}}
    ax, ay = anchors['canon']['island']; assert land[ay, ax] and not hole[ay, ax]
    for k, (px, py) in anchors['far'].items():
        if k != 'hole-far':
            assert far_land_mask[py, px] and not far_hole[py, px], f'the Far side marker {k} is not on land'
    n_east, _ = cv2.connectedComponents(sides['east'][1].astype(np.uint8))
    assert n_east == 4, f'the East side has {n_east - 1} pieces of land, not three (the arm, two corner lands)'
    n_north, _ = cv2.connectedComponents(sides['north'][1].astype(np.uint8))
    assert n_north == 3, f'the North side has {n_north - 1} pieces of land, not two (the arm, the large land)'
    n_west, _ = cv2.connectedComponents(sides['west'][1].astype(np.uint8))
    assert n_west == 2, f'the West side has {n_west - 1} pieces of land, not one (the arm)'
    # the edges between the drawn sides agree too (the wobble dies at the edges, so these are the designed shapes meeting): North's left column runs Far to Canon like East's top row; East's bottom row (Far to Canon) meets South's left column (Canon to Far) reversed; North's top row (East to West) meets Far's top row (West to East) reversed; East's left column meets Far's right column (both North to South); South's bottom row (East to West) meets Far's bottom row (West to East) reversed
    N, E, So, Wst = sides['north'][1], sides['east'][1], sides['south'][1], sides['west'][1]
    for name, a, b in (('North/East', N[:, 0], E[0, :]), ('East/South', E[-1, :], So[:, 0][::-1]), ('North/Far', N[0, :], far_land_mask[0, :][::-1]),
                       ('East/Far', E[:, -1 - 0][:, ] if False else E[:, 0], far_land_mask[:, -1]), ('South/Far', So[-1, :], far_land_mask[-1, :][::-1]),
                       ('North/West', N[:, -1], Wst[0, :][::-1]), ('South/West', So[:, -1], Wst[-1, :])):
        agree = (a == b).mean()
        print(f'edge {name} agreement {agree:.3f}')
        assert agree > 0.975, f'edge agreement {name} {agree:.3f}'
    water_sides = {}
    for side in ('north', 'east', 'south', 'west'):
        for k, (px, py) in anchors[side].items():
            if k.endswith('-portal'):   # the marker sits on a bright band of the swirl, four fifths of a radius east of the eye
                assert not sides[side][1][py, px], f'the {side} portal marker is on land'
            else:
                assert sides[side][1][py, px], f'the {side} marker {k} is not on land'
        water_sides[side] = round(float(1 - sides[side][1].mean()), 4)
    assert not sides['west'][1][int(WEST_PORTAL[1] * S), 0] and not sides['west'][1][5, int(WEST_PORTAL[0] * S)], 'the West side has land where the sketch has water'
    os.chdir(HERE)
    write_jpg('map_canon.jpg', canon)
    write_jpg('map_far.jpg', far)
    prev_far = cv2.cvtColor(far, cv2.COLOR_RGB2BGR).copy()
    for (px, py) in anchors['far'].values():
        cv2.circle(prev_far, (px, py), 9, (40, 220, 255), 2)
    cv2.imwrite(os.path.join(HERE, 'map_far_prev.png'), prev_far)
    write_jpg('map_blank.jpg', render_blank())
    for side in ('north', 'east', 'south', 'west'):
        write_jpg(f'map_{side}.jpg', sides[side][0])
        prev_s = cv2.cvtColor(sides[side][0], cv2.COLOR_RGB2BGR).copy()
        for (px, py) in anchors[side].values():
            cv2.circle(prev_s, (px, py), 9, (40, 220, 255), 2)
        cv2.imwrite(os.path.join(HERE, f'map_{side}_prev.png'), prev_s)
    prev = cv2.cvtColor(canon, cv2.COLOR_RGB2BGR).copy()
    for (px, py) in anchors['canon'].values():
        cv2.circle(prev, (px, py), 9, (40, 220, 255), 2)
    cv2.imwrite(os.path.join(HERE, 'map_canon_prev.png'), prev)
    json.dump({'anchors': anchors, 'water_canon': round(float(water), 4), 'water_far': round(float(far_water), 4), 'water_sides': water_sides, 'arm_reach': ARM_REACH, 'portals': PORTALS, 'hole_radius_px': HOLE_R, 'size': S},
              open(os.path.join(HERE, 'anchors.json'), 'w'), indent=1)
    print(f'canon: water {water:.3f}, land one piece reaching all four sides, hole radius {HOLE_R:.0f}px; far: water {far_water:.3f}, the island and two corner lands, the volcano at {VOLCANO}; the four sides from the sketches, water {water_sides}; wrote map_canon.jpg, map_north/east/south/west.jpg, map_far.jpg, map_blank.jpg, anchors.json')


if __name__ == '__main__':
    main()
