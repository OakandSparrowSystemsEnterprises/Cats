"""Opal's complete maps, second pass: at least half of every face is water, landmasses follow Ruby's outlines,
the southern continent is an island of its own, and all three deltas meet at the same corner (Wetia).
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
def design_far(seed=303):
    P = {'mountains-far': (470, 430), 'celestial': CENTRE, 'delta-far': (118, 872), 'warmia': (666, 518), 'ehia': (736, 685), 'treeland': (600, 868)}
    rid = ridged(seed + 2); rid2 = ridged(seed + 5)
    top = wedge(235)
    # the Extreme Mountains: a massif from the apex down the middle of the face to its exact centre, Mount Celestial
    ridge = supergauss(506, 405, 66, 178, rot=0.1, p=3.0)
    celestial = supergauss(CENTRE[0], CENTRE[1], 74, 66, p=3.0)
    # the Canon-side coast, with Warmia and Ehia on broad lobes of land
    right = band(D_RIGHT, 50) * (YS > 240)
    warmia = supergauss(P['warmia'][0] + 44, P['warmia'][1] - 6, 84, 66, rot=-0.3, p=3.0)
    ehia = supergauss(P['ehia'][0] + 50, P['ehia'][1] + 8, 86, 70, rot=0.2, p=3.0)
    # Tree Land: the whole South edge from the Canon corner to the middle, where it meets the southern continent
    treeland = supergauss(600, 915, 140, 72, rot=0.0, p=4.0)
    delta = supergauss(P['delta-far'][0] + 10, P['delta-far'][1] - 5, 108, 82, p=3.0)
    land = wobble(np.clip(np.maximum.reduce([top, ridge, celestial, right, warmia, ehia, treeland, delta]), 0, 1), seed, 26)
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

LABELS = {
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
    for face, fn, seed in [('west', design_west, 101), ('south', design_south, 202), ('far', design_far, 303)]:
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
