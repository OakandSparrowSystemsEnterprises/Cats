"""Opal's complete maps, second pass: at least half of every face is water, landmasses follow Ruby's outlines,
the southern continent is an island of its own, and all three deltas meet at the same corner (Wetia).
Since version 11 the Canon face is generated too, from the outline of Ruby's painting (design_canon).
Texture space 1024x1024, apex-up: apex (512,75.5), bl (8,948.5), br (1016,948.5)."""
import json, math
import numpy as np, cv2
from mapgen import S, APEX_UP, fbm, ridged, gauss, supergauss, wobble, tri_mask, edge_dist, render, label, codex_crop
from paintface import smooth
from edges import conform
from blobs import island as ISLAND_POLY, continent as CONTINENT_POLY
from nations import ISLAND_NATIONS, CONTINENT_NATIONS
from paintface import render_painted

APEX, BL, BR = (512.0, 75.52), (8.0, 948.48), (1016.0, 948.48)
YS, XS = np.mgrid[0:S, 0:S].astype(np.float32)
TRI = tri_mask(APEX_UP)

def edge_distance(a, b):
    """distance from every pixel to the line through a and b"""
    (x1, y1), (x2, y2) = a, b
    return np.abs((y2 - y1) * XS - (x2 - x1) * YS + x2 * y1 - y2 * x1) / math.hypot(x2 - x1, y2 - y1)
D_LEFT, D_RIGHT, D_BOTTOM = edge_distance(APEX, BL), edge_distance(APEX, BR), edge_distance(BL, BR)

def soft(mask01, blur=9):
    return cv2.GaussianBlur(np.clip(mask01, 0, 1).astype(np.float32), (0, 0), blur)

def poly_mask(pts):
    m = np.zeros((S, S), np.uint8); cv2.fillPoly(m, [np.int32(pts)], 1); return m.astype(np.float32)

def band(dist, width):
    return np.clip((width - dist) / 30.0, 0, 1)

def wedge(y_cut, feather=40):
    return np.clip((y_cut - YS) / feather, 0, 1)

def moat(mask, px):
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * px + 1, 2 * px + 1))
    return cv2.dilate((mask > 0.5).astype(np.uint8), k).astype(np.float32)

def heights(land, seed, terrain_amp=0.10):
    """land: soft 0..1 mask. Height field with a coastal plateau, gentle interior terrain, a shelf then deep water."""
    lb = (land > 0.5).astype(np.uint8)
    # drop specks: land blobs and ponds smaller than ~15 px across
    n, lab, st, _ = cv2.connectedComponentsWithStats(lb, 8)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < 260: lb[lab == i] = 0
    n, lab, st, _ = cv2.connectedComponentsWithStats(1 - lb, 8)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < 260: lb[lab == i] = 1
    d_in = cv2.distanceTransform(lb, cv2.DIST_L2, 5)
    d_out = cv2.distanceTransform(1 - lb, cv2.DIST_L2, 5)
    terrain = fbm(seed + 3, base=6, octaves=5) - 0.5
    h_land = 0.505 + 0.05 * np.clip(d_in / 25.0, 0, 1) + terrain_amp * terrain * np.clip(d_in / 40.0, 0, 1)
    h_sea = 0.49 - 0.22 * np.clip(d_out / 50.0, 0, 1) + 0.02 * (fbm(seed + 4, base=10, octaves=3) - 0.5)
    return np.where(lb > 0, h_land, h_sea).astype(np.float32), d_in

def water_fraction(h):
    return float(((h < 0.5) & TRI).sum() / TRI.sum())

# ----------------------------------------------------------------------------- West
def design_west(seed=101):
    P = {'spike': (538, 157), 'delta': (104, 885), 'island': (524, 603), 'tropicia': (690, 783)}
    rid = ridged(seed + 2)
    island = wobble(poly_mask(ISLAND_POLY), seed + 1, 10)
    tropicia = supergauss(P['tropicia'][0], P['tropicia'][1], 38, 30, p=3.0)
    keep_off = np.maximum(moat(island, 62), moat(tropicia, 44))
    top = wedge(305)
    delta = supergauss(P['delta'][0] + 20, P['delta'][1] - 10, 165, 115, p=3.0)
    mainland = wobble(np.clip(np.maximum(top, delta), 0, 1), seed, 26) * (1 - keep_off)
    land = np.clip(np.maximum.reduce([soft(mainland, 4), soft(island, 3), soft(tropicia, 2)]), 0, 1)
    land = np.clip(conform(land, 'west', seed), 0, 1) * (1 - keep_off * (1 - np.maximum(island, tropicia))) * TRI
    land = np.clip(np.maximum.reduce([land, soft(island, 3), soft(tropicia, 2)]), 0, 1) * TRI
    h, d_in = heights(land, seed)
    h += gauss(P['spike'][0], P['spike'][1] + 30, 230, 210) * (0.22 + 0.34 * rid) * np.clip(d_in / 20, 0, 1)
    h += island * (0.06 + 0.14 * rid) * np.clip(d_in / 30, 0, 1)
    dl = soft(delta * (land > 0.5), 3)
    chan = cv2.resize(cv2.resize(fbm(seed + 11, base=6, octaves=4), (S, S // 3)), (S, S))
    h = h * (1 - dl * 0.7) + (0.503 + (chan - 0.5) * 0.09) * dl * 0.7
    v_apex = np.clip(1 - (YS - APEX[1]) / (BL[1] - APEX[1]), 0, 1)
    temp = np.clip(0.5 - 0.35 * np.clip((h - 0.5) / 0.5, 0, 1) - 0.1 * v_apex + 0.12 * tropicia, 0, 1)
    moist = np.clip(0.55 + 0.25 * dl + 0.2 * island, 0, 1)
    vary = fbm(seed + 41, base=7, octaves=3)
    zones = {
        'forest': np.clip(0.5 * island + 0.9 * tropicia + 0.45 * smooth(vary, 0.52, 0.72), 0, 1),
        'green': np.clip(0.55 * (YS > 300) + 0.4 * island, 0, 1),
        'gold': np.clip(0.9 * smooth(vary, 0.62, 0.8) * (YS > 330), 0, 1),
        'plains': np.clip(0.35 + 0.7 * dl, 0, 1),
    }
    tints = {}
    sources = [(P['spike'][0] + dx, P['spike'][1] + 80 + dy) for dx, dy in [(-60, 30), (55, 20), (-15, 90), (90, 110), (-110, 120)]]
    peak = smooth(np.clip(gauss(P['spike'][0], P['spike'][1] + 30, 170, 150), 0, 1), 0.35, 0.75) * (h > 0.62)
    d = dict(height=h, temp=temp, moist=moist, sea_level=0.5, zones=zones, tints=tints, peak=peak, river_sources=sources)
    anchors = {k: list(v) for k, v in P.items()}
    return d, anchors

# ----------------------------------------------------------------------------- South
def design_south(seed=202):
    P = {'spike-south': (533, 197), 'continent-south': [float(v) for v in CONTINENT_POLY.mean(0)], 'delta-south': (915, 878)}
    rid = ridged(seed + 2)
    continent = wobble(poly_mask(CONTINENT_POLY), seed + 1, 10)
    C = P['continent-south']
    # joined to Tree Land across the Far edge (the bottom of this face), never to the West side (the right edge):
    # a broad lobe runs from the continent's south-west down to the bottom edge, where Tree Land's coast continues
    lobe = wobble(supergauss(C[0] - 110, C[1] + 215, 100, 118, rot=0.25, p=3.0), seed + 3, 16)
    keep_off = moat(np.maximum(continent, lobe), 64)
    top = wedge(275)
    delta = supergauss(P['delta-south'][0] - 10, P['delta-south'][1] - 5, 132, 98, p=3.0)
    mainland = wobble(np.clip(np.maximum(top, delta), 0, 1), seed, 26) * (1 - keep_off)
    body = np.clip(np.maximum(soft(continent, 3), soft(lobe, 3)), 0, 1)
    land = np.clip(np.maximum(soft(mainland, 4), body), 0, 1)
    land = np.clip(conform(land, 'south', seed), 0, 1) * TRI
    h, d_in = heights(land, seed)
    h += gauss(P['spike-south'][0], P['spike-south'][1] + 20, 200, 190) * (0.18 + 0.3 * rid) * np.clip(d_in / 20, 0, 1)
    h += continent * (0.05 + 0.12 * rid) * np.clip(d_in / 30, 0, 1)
    h += gauss(C[0] - 10, C[1] - 95, 105, 34, rot=0.15) * 0.42 * (0.5 + rid) * continent
    dl = soft(delta * (land > 0.5), 3)
    chan = cv2.resize(cv2.resize(fbm(seed + 11, base=6, octaves=4), (S, S // 3)), (S, S))
    h = h * (1 - dl * 0.7) + (0.503 + (chan - 0.5) * 0.09) * dl * 0.7
    v_apex = np.clip(1 - (YS - APEX[1]) / (BL[1] - APEX[1]), 0, 1)
    snowia = gauss(C[0] - 10, C[1] - 95, 120, 60)
    coldland = gauss(C[0] - 95, C[1] + 20, 90, 90); beria = gauss(C[0] + 55, C[1] + 80, 90, 80)
    temp = np.clip(0.35 + 0.6 * v_apex - 0.3 * np.clip((h - 0.5) / 0.5, 0, 1) - 0.45 * snowia + 0.1 * dl, 0, 1)
    moist = np.clip(0.6 + 0.25 * dl + 0.2 * v_apex, 0, 1)
    vary = fbm(seed + 41, base=7, octaves=3)
    treeside = smooth(YS, 760, 900) * (XS > 280) * (XS < 600)      # Tree Land's woods continue over the bottom edge
    zones = {
        'forest': np.clip(0.9 * smooth(v_apex, 0.7, 0.9) + 0.8 * beria + 0.9 * treeside + 0.3 * smooth(vary, 0.55, 0.75), 0, 1),
        'white': np.clip(1.2 * snowia, 0, 1),
        'plains': np.clip(0.9 * coldland + 0.6 * dl, 0, 1),
        'green': np.clip(0.5 * continent + 0.3, 0, 1),
        'gold': np.clip(0.6 * smooth(vary, 0.66, 0.82) * (1 - snowia) * (1 - coldland), 0, 1),
    }
    tints = {'cold': np.clip(coldland + snowia, 0, 1), 'hot': smooth(v_apex, 0.7, 0.9) * 0.5}
    sources = [(P['spike-south'][0] + dx, P['spike-south'][1] + 70 + dy) for dx, dy in [(-55, 30), (60, 20), (-100, 110), (100, 120), (0, 140)]]
    sources += [(int(C[0] + dx), int(C[1] - 60 + dy)) for dx, dy in [(-60, 0), (50, -5), (0, 20)]]
    peak = np.clip(smooth(snowia, 0.45, 0.8) * (h > 0.6) + smooth(gauss(P['spike-south'][0], P['spike-south'][1] + 10, 120, 110), 0.5, 0.9) * (h > 0.66), 0, 1)
    d = dict(height=h, temp=temp, moist=moist, sea_level=0.5, zones=zones, tints=tints, peak=peak, snowy=np.clip(1.4 * snowia + 0.3, 0, 1), river_sources=sources)
    anchors = {k: [float(v[0]), float(v[1])] for k, v in P.items()}
    return d, anchors

# ----------------------------------------------------------------------------- Far
CENTRE = (512.0, (APEX[1] + BL[1] + BR[1]) / 3)
NECK_ROT = math.atan2(915 - 693, 600 - 786)      # the neck points from Ehia toward Tree Land
def design_far(seed=303):
    P = {'mountains-far': (470, 430), 'celestial': CENTRE, 'delta-far': (118, 872), 'warmia': (666, 518), 'ehia': (736, 685), 'treeland': (600, 868)}
    rid = ridged(seed + 2); rid2 = ridged(seed + 5)
    top = wedge(235)
    # the Extreme Mountains: a massif from the apex down the middle of the face to its exact centre, Mount Celestial
    ridge = supergauss(506, 405, 60, 178, rot=0.1, p=3.0)      # (rx 66 until v11: a little slimmer to pay for the neck to Tree Land)
    celestial = supergauss(CENTRE[0], CENTRE[1], 74, 66, p=3.0)
    # the Canon-side coast, with Warmia and Ehia on broad lobes of land
    right = band(D_RIGHT, 50) * (YS > 240)
    warmia = supergauss(P['warmia'][0] + 44, P['warmia'][1] - 6, 84, 66, rot=-0.3, p=3.0)
    ehia = supergauss(P['ehia'][0] + 50, P['ehia'][1] + 8, 86, 70, rot=0.2, p=3.0)
    # Tree Land: the whole South edge from the Canon corner to the middle, where it meets the southern continent
    treeland = supergauss(600, 915, 140, 72, rot=0.0, p=4.0)
    # Ruby (2026-10-03), asked whether Tree Land and the Canon-side nations should join: "yes pleese". Her Far sketch draws
    # Warmia, Ehia and Tree Land inside one outline, so a neck of land runs from Ehia down to Tree Land, inland of the
    # bottom edge (the shared edge with the South face keeps its open water there)
    neck = supergauss(700, 790, 112, 46, rot=NECK_ROT, p=3.0)
    delta = supergauss(P['delta-far'][0] + 10, P['delta-far'][1] - 5, 102, 78, p=3.0)
    land = wobble(np.clip(np.maximum.reduce([top, ridge, celestial, right, warmia, ehia, neck, treeland, delta]), 0, 1), seed, 26)
    land = soft(land, 4)
    land = np.clip(conform(land, 'far', seed), 0, 1) * TRI
    h, d_in = heights(land, seed)
    mass = np.maximum.reduce([gauss(APEX[0], APEX[1] + 110, 160, 150), gauss(506, 410, 95, 185, rot=0.1), gauss(CENTRE[0], CENTRE[1], 70, 62)])
    h += mass * (0.30 + 0.5 * rid2) * np.clip(d_in / 25, 0, 1)
    h += gauss(CENTRE[0], CENTRE[1], 34, 34) * 0.45 * np.clip(d_in / 25, 0, 1)      # Mount Celestial itself
    dl = soft(delta * (land > 0.5), 3)
    chan = cv2.resize(cv2.resize(fbm(seed + 11, base=6, octaves=4), (S, S // 3)), (S, S))
    h = h * (1 - dl * 0.7) + (0.503 + (chan - 0.5) * 0.09) * dl * 0.7
    W_, E_, T_ = P['warmia'], P['ehia'], P['treeland']
    wb, eb, tb = gauss(W_[0] + 20, W_[1], 130, 100, rot=-0.4), gauss(E_[0] + 30, E_[1], 120, 95), np.maximum(gauss(T_[0], T_[1], 230, 120), gauss(560, 900, 150, 90))
    temp = np.clip(0.5 - 0.42 * np.clip((h - 0.55) / 0.55, 0, 1) + 0.5 * wb + 0.12 * eb + 0.1 * tb, 0, 1)
    moist = np.clip(0.5 + 0.4 * tb + 0.2 * eb - 0.4 * wb + 0.2 * dl, 0, 1)
    vary = fbm(seed + 41, base=7, octaves=3)
    zones = {
        'forest': np.clip(1.2 * tb + 0.2 * smooth(vary, 0.6, 0.8), 0, 1),
        'gold': np.clip(1.2 * wb, 0, 1),
        'green': np.clip(1.1 * eb + 0.25, 0, 1),
        'redrock': np.clip(0.9 * mass * (1 - tb), 0, 1),
        'plains': np.clip(0.7 * dl + 0.2, 0, 1),
    }
    tints = {'hot': wb * 0.8}
    sources = [(500 + dx, 430 + dy) for dx, dy in [(-90, 60), (110, 90), (-40, -120), (150, -40)]] + [(int(CENTRE[0] + dx), int(CENTRE[1] + dy)) for dx, dy in [(-50, 40), (60, 30)]]
    peak = smooth(mass, 0.45, 0.8) * (h > 0.7)
    d = dict(height=h, temp=temp, moist=moist, sea_level=0.5, zones=zones, tints=tints, peak=peak, river_sources=sources)
    anchors = {k: list(v) for k, v in P.items()}
    return d, anchors

# ----------------------------------------------------------------------------- Canon
# Ruby (2026-10-03): the Canon face "shuld not have land on the west and east sides and needs to not have clouds, be at least
# 50% water, and look like the other sides (the detail is too much for the cannon side, this is a 4th of a entire planet you know)".
# So the Canon face is Opal's map too now: Ruby's painting gives the outline and the places, the painter gives the look.
SIDE_SEA = 96      # px: the open-sea band along the Canon face's two side edges (full within SIDE_SEA - 30, gone at SIDE_SEA)

def canon_positions():
    """the 13 Canon regions, from their barycentrics in geometry.json (measured on the painting) to texture px"""
    geo = json.load(open('geometry.json')); out = {}
    for r in geo['regions']:
        if r['face'] != 'canon': continue
        l1, l2, l3 = r['b']
        out[r['id']] = (l1 * APEX[0] + l2 * BL[0] + l3 * BR[0], l1 * APEX[1] + l2 * BL[1] + l3 * BR[1])
    return out

def canon_outline(path='tex_canon.jpg'):
    """Ruby's painting as a plain outline: land wherever the painting is neither sea nor cloud. A cloud pixel takes the class of
    the nearest clear pixel (so clouds over the sea vanish and clouds over land become land), then the coast is simplified."""
    tex = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB).astype(np.float32)
    r, g, b = tex[..., 0], tex[..., 1], tex[..., 2]
    water = (b > r + 30) & (b > 95) & (g > r + 8)
    lum = tex.mean(2); sat = tex.max(2) - tex.min(2)
    cloud = (lum > 196) & (sat < 40) & ~water
    _, labels = cv2.distanceTransformWithLabels(cloud.astype(np.uint8), cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    ys, xs = np.where(~cloud)
    lut = np.zeros(int(labels.max()) + 1, np.uint8); lut[labels[ys, xs]] = water[ys, xs]
    water = lut[labels].astype(bool)
    land = (~water & (TRI > 0.5)).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13))
    land = cv2.morphologyEx(cv2.morphologyEx(land, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k)
    for _ in range(2):      # drop islets and ponds smaller than ~45 px across, both ways
        n, lab, st, _ = cv2.connectedComponentsWithStats(land, 8)
        for i in range(1, n):
            if st[i, cv2.CC_STAT_AREA] < 1800: land[lab == i] = 0
        n, lab, st, _ = cv2.connectedComponentsWithStats(1 - land, 8)
        for i in range(1, n):
            if st[i, cv2.CC_STAT_AREA] < 1800: land[lab == i] = 1
    return land.astype(np.float32)

def mask_water(mask):
    return float(((mask < 0.5) & (TRI > 0.5)).sum() / (TRI > 0.5).sum())

def settle(P, land, min_in=16, max_move=60):
    """every marker on land, well clear of the coast: a marker that the new coast left in the water, or closer than min_in px
    to it, moves to the nearest land min_in px inland. A move longer than max_move means the outline changed under a region;
    that is for a person to place, so it fails loudly instead of landing the region on some other landmass."""
    lb = (land > 0.5).astype(np.uint8); d_in = cv2.distanceTransform(lb, cv2.DIST_L2, 5)
    ys, xs = np.where((d_in >= min_in) & (TRI > 0.5)); out = {}; moved = {}
    for k, (x, y) in P.items():
        if d_in[int(round(y)), int(round(x))] >= min_in: out[k] = (float(x), float(y)); continue
        j = int(np.argmin((xs - x) ** 2 + (ys - y) ** 2)); out[k] = (float(xs[j]), float(ys[j]))
        moved[k] = round(float(math.hypot(xs[j] - x, ys[j] - y)))
        assert moved[k] <= max_move, (k, 'would move', moved[k], 'px to reach land: place it by hand')
    return out, moved

# Ruby (2026-10-03), on seeing the first generated Canon face: "we need to make islandia, egg island, and chicken island smaller
# so they can keep their shapes and for the south continent, make it sort of semi circly please". So the painting's landmasses
# are cut out whole, scaled down about their own centres (shapes kept) and moved just clear of the side sea, and the southern
# land is a half-disc rising from the middle of the bottom edge.
CANON_GROUPS = {'egg': ['whiteland', 'yolkia'], 'islandia': ['islandia'],
                'chicken': ['headlands', 'neckia', 'feathers', 'llamaland', 'footia'],
                'south': ['unoooland', 'hotland', 'rainia', 'uohia'], 'spike': ['spikia-canon']}
ISLAND_SCALE = {'egg': 0.72, 'chicken': 0.72, 'islandia': 0.80}   # how much smaller each island is than in the painting
SIDE_CLEAR = SIDE_SEA + 16                                          # px from a side edge that an island must keep
CHANNEL = 40                                                        # px of open water kept between two islands
DOME_A = 290                                                        # half-width of the southern half-disc; its height is solved for half water

def canon_pieces(outline, P):
    """the painting's landmasses as one mask per group. Where two groups share a landmass (the egg joins the southern land,
    Spikia's neck does too) it is cut along the line of equal distance to the groups' markers."""
    lb = (outline > 0.5).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(lb, 8)
    names = list(CANON_GROUPS)
    best = np.full((S, S), -1, np.int32); bestd = np.full((S, S), np.inf, np.float32)
    for gi, g in enumerate(names):
        for k in CANON_GROUPS[g]:
            x, y = P[k]; d = (XS - x) ** 2 + (YS - y) ** 2
            m = d < bestd; bestd[m] = d[m]; best[m] = gi
    pieces = {}
    for gi, g in enumerate(names):
        comps = {int(lab[int(round(P[k][1])), int(round(P[k][0]))]) for k in CANON_GROUPS[g]} - {0}
        m = (np.isin(lab, list(comps)) & (best == gi)).astype(np.uint8)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
        n2, lab2, _, _ = cv2.connectedComponentsWithStats(m, 8)
        keep = {int(lab2[int(round(P[k][1])), int(round(P[k][0]))]) for k in CANON_GROUPS[g]} - {0}
        pieces[g] = np.isin(lab2, list(keep)).astype(np.float32)
    return pieces

def place(mask, pts, s, shift=(0.0, 0.0)):
    """scale a mask, and the points on it, about the mask's centroid by s, then move both by shift"""
    ys, xs = np.where(mask > 0.5); cx, cy = float(xs.mean()), float(ys.mean())
    A = np.array([[s, 0, cx * (1 - s) + shift[0]], [0, s, cy * (1 - s) + shift[1]]], np.float32)
    out = cv2.warpAffine(mask, A, (S, S), flags=cv2.INTER_LINEAR, borderValue=0)
    return out, {k: (s * x + float(A[0, 2]), s * y + float(A[1, 2])) for k, (x, y) in pts.items()}

def disc(cx, cy, r):
    """a round island"""
    return np.clip((r - np.hypot(XS - cx, YS - cy)) / 3.0 + 0.5, 0, 1)

def egg_shape(cx, cy, rx, ry, rot, seed):
    """an egg: an oval, narrower at its top end, with a slightly wandering coast (Ruby: "egg island shuld be egg shaped (also no
    perfict circular stuff")"""
    c, s_ = math.cos(rot), math.sin(rot)
    x, y = XS - cx, YS - cy
    x, y = c * x + s_ * y, -s_ * x + c * y
    taper = 1.0 - 0.22 * np.clip(-y / ry, -1, 1)            # the top end is the narrow one
    r = np.sqrt((x / (rx * taper)) ** 2 + (y / ry) ** 2)
    return wobble(np.clip((1.0 - r) * min(rx, ry) / 3.0 + 0.5, 0, 1), seed + 13, 7)

def arch(h, R, seed):
    """the southern land: a circular segment h px tall standing on the middle of the bottom edge, cut from a circle of radius R
    (R = h gives a half-disc; a larger R a flatter arc, a smaller slice of the circle), with a slightly wandering coast"""
    cy = BL[1] + R - h
    return wobble(np.clip((R - np.hypot(XS - 512.0, YS - cy)) / 6.0 + 0.5, 0, 1) * (YS <= BL[1] + 1), seed + 9, 18)

# Ruby (2026-10-03), on the second Canon design: "make it as tall as that but have the semi sircle be more like a 6th of a circle and
# make egia and islandia perfectly shperical plz also put the chicken island above islandia now that we have the room".
DOME_H = 213                       # px: the height the half-disc had ("as tall as that")
ARC_GOAL = 1 / 6                   # the slice of a circle she asked for; the arc gets as flat as half water allows, up to this
ISLAND_R = {'egg': 66, 'islandia': 50}   # px: the egg's mean radius (it is drawn 58 x 76, tilted) and Islandia's (their sizes are a reading)
ISLANDIA_AT = (512.0, 640.0)
CHICKEN_SCALE = 0.60               # starting size of chicken island; it shrinks a notch at a time until it fits above Islandia

def design_canon(seed=404):
    P0 = canon_positions()
    rid = ridged(seed + 2)
    pieces = canon_pieces(canon_outline(), P0)
    P = {'spikia-canon': P0['spikia-canon']}
    top = wedge(290)
    # egg island: a disc where the painting's egg is, slid clear of the side sea; Whiteland on its west half, Yolkia on its east
    ys_, xs_ = np.where(pieces['egg'] > 0.5); ex, ey = float(xs_.mean()), float(ys_.mean()); r_e = ISLAND_R['egg']
    short = SIDE_CLEAR + r_e - float(D_LEFT[int(ey), int(ex)])
    if short > 0: ex += short / math.sin(math.pi / 3)
    EGG_RX, EGG_RY, EGG_ROT = 58, 76, -0.22
    egg = egg_shape(ex, ey, EGG_RX, EGG_RY, EGG_ROT, seed)
    # Whiteland west of the egg's long axis, Yolkia east of it; the border between them is a river (see the heights below)
    P['whiteland'] = (ex - 0.46 * EGG_RX, ey + 0.05 * EGG_RY); P['yolkia'] = (ex + 0.46 * EGG_RX, ey + 0.05 * EGG_RY)
    ix, iy = ISLANDIA_AT; r_i = ISLAND_R['islandia']
    ix = max(ix, ex + r_e + CHANNEL + r_i)       # Islandia keeps CHANNEL px of water from the egg (the face is narrow this high up)
    islandia = wobble(disc(ix, iy, r_i), seed + 17, 9); P['islandia'] = (ix, iy)     # round, not perfectly: "no perfict circular stuff"
    # chicken island above Islandia: its painted shape, as big as fits between Spikia's coast and Islandia with CHANNEL px of water
    ch = pieces['chicken']; ys_, xs_ = np.where(ch > 0.5); cx, cy, cy_max = float(xs_.mean()), float(ys_.mean()), float(ys_.max())
    bx = (float(xs_.min()) + float(xs_.max())) / 2                 # the middle of its width
    d_top = cv2.distanceTransform((top < 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    s_c = CHICKEN_SCALE
    for _ in range(16):
        ty = (iy - r_i - CHANNEL) - (cy_max - cy) * s_c          # centroid height that puts its lowest point CHANNEL above Islandia
        tx = 512.0 - s_c * (bx - cx)                               # its width centred on the face, where the room is
        chicken, pts = place(ch, {k: P0[k] for k in CANON_GROUPS['chicken']}, s_c, (tx - cx, ty - cy))
        on = chicken > 0.5
        if float(d_top[on].min()) >= CHANNEL and float(np.minimum(D_LEFT, D_RIGHT)[on].min()) >= SIDE_CLEAR: break
        s_c *= 0.95
    P.update(pts)
    for k in CANON_GROUPS['south']: P[k] = P0[k]
    islands = np.clip(np.maximum.reduce([top, soft(egg, 1), soft(islandia, 1), soft(chicken, 2)]), 0, 1)
    # the southern land: DOME_H tall, and as flat an arc as keeps the face half water and CHANNEL px from the islands
    d_isl = cv2.distanceTransform((islands < 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    def fit(R):
        a = arch(DOME_H, R, seed)
        land = np.clip(conform(np.clip(np.maximum(islands, a), 0, 1), 'canon', seed), 0, 1) * TRI
        return land, mask_water(land) >= 0.505 and float(d_isl[a > 0.5].min()) >= CHANNEL
    R = float(DOME_H); land, ok = fit(R)
    assert ok, 'even the half-disc does not fit: move the islands'
    R_goal = DOME_H / (1 - math.cos(math.pi * ARC_GOAL))          # the radius whose 1/6 arc is DOME_H tall
    while R < R_goal:
        R2 = min(R * 1.08, R_goal); land2, ok = fit(R2)
        if not ok: break
        R, land = R2, land2
    chord = 2 * math.sqrt(max(2 * R * DOME_H - DOME_H ** 2, 0)); frac = 2 * math.asin(min(chord / 2, 504.0) / R) / (2 * math.pi)
    print(f'canon: egg r{r_e} at ({ex:.0f},{ey:.0f}); islandia r{r_i}; chicken scale {s_c:.2f}; south arch {DOME_H} px tall, radius {R:.0f}, '
          f'about 1/{1 / frac:.1f} of a circle; water {mask_water(land):.3f}')
    P, moved = settle(P, land)
    if moved: print('canon: markers moved onto land (px):', moved)
    h, d_in = heights(land, seed)
    spike = gauss(APEX[0], APEX[1] + 120, 170, 160)
    h += spike * (0.2 + 0.32 * rid) * np.clip(d_in / 20, 0, 1)
    F, Hd = P['feathers'], P['headlands']
    feathers = gauss(F[0], F[1], 70, 52, rot=0.5); heads = gauss(Hd[0], Hd[1], 50, 44)
    h += (feathers * 0.34 + heads * 0.22) * (0.5 + rid) * np.clip(d_in / 25, 0, 1)
    # Ruby: "whiteland and yolkia need to have a rivver on the border". The egg's long axis is the border: a shallow valley runs
    # along it, highest at the north end, so a river rising there flows south down the border to the sea
    on_egg = (egg > 0.5)
    c_, s_ = math.cos(EGG_ROT), math.sin(EGG_ROT)
    ax = c_ * (XS - ex) + s_ * (YS - ey); ay = -s_ * (XS - ex) + c_ * (YS - ey)      # the egg's own axes
    valley = np.exp(-0.5 * (ax / 7.0) ** 2); slope = np.clip((ey - YS) / EGG_RY, -1, 1)
    h = np.where(on_egg, h + 0.025 * slope * np.clip(d_in / 12, 0, 1) - 0.03 * valley * np.clip(d_in / 10, 0, 1), h)
    river_top = (ex - s_ * (-0.55 * EGG_RY), ey + c_ * (-0.55 * EGG_RY))             # on the border, near the north end
    def near(k, r): x, y = P[k]; return gauss(x, y, r, r)
    white = near('whiteland', 55)
    gold = np.maximum(near('yolkia', 55), 0.7 * near('llamaland', 65))
    forest = np.maximum.reduce([near('islandia', 60), near('unoooland', 95), near('uohia', 90), 0.6 * near('feathers', 60)])
    green = np.maximum.reduce([near('neckia', 60), near('rainia', 90), near('footia', 65), 0.6 * near('islandia', 70)])
    red = np.maximum(near('headlands', 60), near('hotland', 95))
    vary = fbm(seed + 41, base=7, octaves=3)
    temp = np.clip(0.5 - 0.35 * np.clip((h - 0.5) / 0.5, 0, 1) + 0.3 * near('hotland', 110) - 0.3 * white, 0, 1)
    moist = np.clip(0.5 + 0.3 * near('rainia', 110) + 0.2 * forest - 0.2 * gold, 0, 1)
    zones = {
        'white': np.clip(1.1 * white, 0, 1),
        'gold': np.clip(gold, 0, 1),
        'forest': np.clip(forest + 0.3 * smooth(vary, 0.55, 0.75), 0, 1),
        'green': np.clip(0.9 * green + 0.2, 0, 1),
        'redrock': np.clip(0.9 * red, 0, 1),
        'plains': np.clip(0.3 + 0.5 * smooth(vary, 0.3, 0.5), 0, 1),
    }
    tints = {'hot': near('hotland', 110) * 0.8, 'cold': white * 0.5}
    sources = [(int(APEX[0] + dx), int(APEX[1] + 150 + dy)) for dx, dy in [(-50, 30), (55, 20), (-20, 90), (80, 100)]]
    sources += [(int(F[0] + dx), int(F[1] + dy)) for dx, dy in [(-30, -15), (20, 15)]]
    sources += [(int(river_top[0]), int(river_top[1]))]                                   # the border river of egg island
    peak = np.clip(smooth(spike, 0.4, 0.8) * (h > 0.64) + smooth(feathers, 0.5, 0.9) * (h > 0.62), 0, 1)
    d = dict(height=h, temp=temp, moist=moist, sea_level=0.5, zones=zones, tints=tints, peak=peak, river_sources=sources)
    anchors = {k: [float(x), float(y)] for k, (x, y) in P.items()}
    return d, anchors

LABELS = {
    'canon': [('spikia-canon', 'Spikia', 30, False, (0, 56)), ('whiteland', 'Whiteland', 20, False, (-30, 30)), ('yolkia', 'Yolkia', 20, False, (30, -30)),
              ('islandia', 'Islandia', 20, False, (0, 36)), ('headlands', 'The Headlands', 18, False, (0, -32)), ('neckia', 'Neckia', 18, False, (-48, -6)),
              ('feathers', 'The Feathers', 18, False, (-56, 22)), ('llamaland', 'Llamaland', 18, False, (56, -4)), ('footia', 'Footia', 18, False, (34, 26)),
              ('unoooland', 'Uncooland', 20, True, (0, 30)), ('hotland', "It's Hot", 20, True, (0, 30)), ('rainia', 'Rainia', 20, True, (0, 30)), ('uohia', 'Ughia', 20, True, (-40, -26))],
    'west': [('spike', 'Spikia', 34, False, (0, 60)), ('delta', 'Wetia', 26, True, (30, -30)),
             ('island', 'The Central Island', 24, False, (0, 0)), ('tropicia', 'Tropicia', 20, True, (0, 40))],
    'south': [('spike-south', 'Spikia', 34, False, (0, 60)), ('continent-south', 'The Southern Continent', 22, False, (0, 0)), ('delta-south', 'Wetia', 26, True, (-40, -30))],
    'far': [('mountains-far', 'Extreme Mountains', 30, False, (0, -70)), ('celestial', 'Mount Celestial', 22, False, (0, 34)), ('warmia', 'Warmia', 28, True, (-20, -30)), ('ehia', 'Ehia', 28, True, (-30, 0)),
            ('treeland', 'Tree Land', 28, True, (0, -40)), ('delta-far', 'Wetia', 26, True, (30, -40))],
}

def check_markers(face, d, P):
    """every marker must sit on land, well clear of the coast"""
    land = d['height'] >= d['sea_level']
    din = cv2.distanceTransform(land.astype(np.uint8), cv2.DIST_L2, 5)
    pts = dict(P)
    if face == 'west':
        for i, _, (dx, dy), _ in ISLAND_NATIONS: pts[i] = (P['island'][0] + dx, P['island'][1] + dy)
    if face == 'south':
        for i, _, (dx, dy), _ in CONTINENT_NATIONS: pts[i] = (P['continent-south'][0] + dx, P['continent-south'][1] + dy)
    bad = {k: round(float(din[int(y), int(x)])) for k, (x, y) in pts.items() if din[int(y), int(x)] < 14}
    return bad

if __name__ == '__main__':
    anchors_all = {}
    fractions = {}
    for face, fn, seed in [('canon', design_canon, 404), ('west', design_west, 101), ('south', design_south, 202), ('far', design_far, 303)]:
        d, P = fn(seed)
        frac = water_fraction(d['height']); fractions[face] = round(frac, 3)
        assert frac >= 0.5, (face, frac)
        bad = check_markers(face, d, P)
        assert not bad, (face, 'markers in or at the water:', bad)
        raw = render_painted(d, seed, TRI)
        raw[~TRI] = (22, 20, 18)
        img = raw.copy()
        for key, text, size, italic, (dx, dy) in LABELS[face]:
            x, y = P[key]; img = label(img, text, (x + dx, y + dy), size=size, italic=italic)
        cv2.imwrite(f'map_{face}.jpg', cv2.cvtColor(raw, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
        m = TRI; ys_, xs_ = np.where(m); x0, x1, y0, y1 = xs_.min(), xs_.max(), ys_.min(), ys_.max()
        cod = img[y0:y1 + 1, x0:x1 + 1]; cod = cv2.resize(cod, (560, int(cod.shape[0] * 560 / cod.shape[1])), interpolation=cv2.INTER_AREA)
        cv2.imwrite(f'codex_{face}.jpg', cv2.cvtColor(cod, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 84])
        if face == 'west':
            I = P['island']
            codex_crop(raw, I[0], I[1], 175, [(n, off, 24, True) for _, n, off, _ in ISLAND_NATIONS] + [('The Central Island', (0, 150), 26, False)], 'codex_island.jpg')
        if face == 'south':
            C = P['continent-south']
            codex_crop(raw, C[0] - 15, C[1], 192, [(n, off, 26, True) for _, n, off, _ in CONTINENT_NATIONS] + [('The Southern Continent', (15, 172), 26, False)], 'codex_continent.jpg')
        prev = img.copy()
        for k, (x, y) in P.items(): cv2.circle(prev, (int(x), int(y)), 6, (255, 255, 0), 2)
        if face == 'west':
            for _, _, (dx, dy), _ in ISLAND_NATIONS: cv2.circle(prev, (int(P['island'][0] + dx), int(P['island'][1] + dy)), 5, (255, 120, 255), 2)
        if face == 'south':
            for _, _, (dx, dy), _ in CONTINENT_NATIONS: cv2.circle(prev, (int(P['continent-south'][0] + dx), int(P['continent-south'][1] + dy)), 5, (255, 120, 255), 2)
        cv2.imwrite(f'map_{face}_prev.png', cv2.cvtColor(cv2.resize(prev, (640, 640)), cv2.COLOR_RGB2BGR))
        anchors_all[face] = P
        print(face, 'water', round(frac, 3))
    json.dump(anchors_all, open('map_anchors.json', 'w'))
    json.dump(fractions, open('water_fractions.json', 'w'))
