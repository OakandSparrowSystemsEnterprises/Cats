"""Opal's complete maps: procedural painted maps for the West, South and Far faces, laid out from the explorers' sketches.
Texture space is 1024x1024; the face triangle is apex-up (West, South) or apex-down (Far, so it reads upright from below).
"""
import json, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from nations import ISLAND_NATIONS, CONTINENT_NATIONS

S = 1024
APEX_UP = dict(apex=(512.0, 75.52), bl=(8.0, 948.48), br=(1016.0, 948.48))
APEX_DOWN = dict(apex=(512.0, 948.48), bl=(8.0, 75.52), br=(1016.0, 75.52))

def bary_px(b, lay):
    return (b[0] * lay['apex'][0] + b[1] * lay['bl'][0] + b[2] * lay['br'][0],
            b[0] * lay['apex'][1] + b[1] * lay['bl'][1] + b[2] * lay['br'][1])

# ---------------- noise ----------------
def vnoise(cells, seed):
    rng = np.random.default_rng(seed)
    g = rng.random((cells + 1, cells + 1), dtype=np.float32)
    return cv2.resize(g, (S, S), interpolation=cv2.INTER_CUBIC)

def fbm(seed, base=3, octaves=7, gain=0.55):
    out = np.zeros((S, S), np.float32); amp = 1.0; tot = 0.0
    for i in range(octaves):
        out += amp * vnoise(base * (2 ** i), seed * 31 + i); tot += amp; amp *= gain
    out /= tot
    out = (out - out.min()) / (out.max() - out.min() + 1e-6)
    return out

def warped(seed, strength=90.0):
    dx = (fbm(seed + 7, base=2, octaves=4) - 0.5) * strength
    dy = (fbm(seed + 13, base=2, octaves=4) - 0.5) * strength
    ys, xs = np.mgrid[0:S, 0:S].astype(np.float32)
    base = fbm(seed, base=3, octaves=7)
    return cv2.remap(base, xs + dx, ys + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def ridged(seed):
    f = fbm(seed, base=4, octaves=6, gain=0.5)
    r = 1.0 - np.abs(2 * f - 1.0)
    return r * r

def gauss(cx, cy, rx, ry=None, rot=0.0):
    ry = ry or rx
    ys, xs = np.mgrid[0:S, 0:S].astype(np.float32)
    x = xs - cx; y = ys - cy
    if rot:
        c, s = math.cos(rot), math.sin(rot); x, y = c * x + s * y, -s * x + c * y
    return np.exp(-0.5 * ((x / rx) ** 2 + (y / ry) ** 2))

def supergauss(cx, cy, rx, ry=None, rot=0.0, p=4.0):
    ry = ry or rx
    ys, xs = np.mgrid[0:S, 0:S].astype(np.float32)
    x = xs - cx; y = ys - cy
    if rot:
        c, s_ = math.cos(rot), math.sin(rot); x, y = c * x + s_ * y, -s_ * x + c * y
    r2 = (x / rx) ** 2 + (y / ry) ** 2
    return np.exp(-0.5 * r2 ** (p / 2))

def wobble(mask, seed, strength=38.0):
    """Displace a mask by low-frequency noise so its outline stops being an ellipse."""
    dx = (fbm(seed + 71, base=5, octaves=3) - 0.5) * strength * 2
    dy = (fbm(seed + 83, base=5, octaves=3) - 0.5) * strength * 2
    ys, xs = np.mgrid[0:S, 0:S].astype(np.float32)
    return cv2.remap(mask.astype(np.float32), xs + dx, ys + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def tri_mask(lay):
    m = np.zeros((S, S), np.uint8)
    cv2.fillPoly(m, [np.int32([lay['apex'], lay['bl'], lay['br']])], 1)
    return m.astype(bool)

def edge_dist(lay):
    """distance (px) to the nearest triangle edge, inside the triangle."""
    m = tri_mask(lay).astype(np.uint8)
    return cv2.distanceTransform(m, cv2.DIST_L2, 5)

# ---------------- colour helpers ----------------
def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0

def lerp(a, b, t):
    t = np.clip(t, 0, 1)[..., None]
    return a * (1 - t) + b * t

def blend(base, color, mask):
    m = np.clip(mask, 0, 1)[..., None]
    return base * (1 - m) + color * m

# ---------------- renderer ----------------
def render(design, seed, lay):
    """design: dict with height (S,S) float, temp (S,S) 0..1, moist (S,S) 0..1, sea_level, labels list"""
    h = design['height']; temp = design['temp']; moist = design['moist']; sea = design['sea_level']
    land = h > sea
    depth = np.clip((sea - h) / 0.25, 0, 1)
    alt = np.clip((h - sea) / (h.max() - sea + 1e-6), 0, 1)

    # --- base colours ---
    deep = hexc('#123b73'); mid = hexc('#1f6cb3'); shallow = hexc('#46b0df'); shore = hexc('#9be0ee')
    water = lerp(shore, shallow, depth * 3.0)
    water = lerp(water, mid, (depth - 0.2) * 2.0)
    water = lerp(water, deep, (depth - 0.55) * 2.2)
    wave = fbm(seed + 99, base=12, octaves=3)
    water = water * (0.94 + 0.12 * wave[..., None])

    sand = hexc('#e0cc93'); grass = hexc('#7aa844'); grass2 = hexc('#9dc255'); jungle = hexc('#2d7a2c'); jungle2 = hexc('#1f5f22')
    taiga = hexc('#3d6a3e'); tundra = hexc('#cfd3c9'); tundra2 = hexc('#b5bcaf'); snow = hexc('#f5f7f9'); rock = hexc('#8a7d6e'); rock2 = hexc('#b3a898')
    swampc = hexc('#5d6f37'); swamp2 = hexc('#4a6b52'); savanna = hexc('#c2ab55'); dry = hexc('#d2b06a')

    veg_noise = fbm(seed + 5, base=16, octaves=3)
    # temperature bands
    cold = np.clip((0.35 - temp) / 0.35, 0, 1)
    hot = np.clip((temp - 0.62) / 0.3, 0, 1)
    wet = np.clip((moist - 0.5) / 0.4, 0, 1)
    dryness = np.clip((0.42 - moist) / 0.3, 0, 1)
    landc = lerp(grass, grass2, veg_noise)
    landc = lerp(landc, jungle, hot * wet)
    landc = lerp(landc, lerp(jungle, jungle2, veg_noise), hot * wet * 0.6)
    landc = lerp(landc, savanna, hot * (1 - wet) * 0.8)
    landc = lerp(landc, dry, dryness * 0.9)
    landc = lerp(landc, lerp(swampc, swamp2, veg_noise), np.clip((moist - 0.78) / 0.2, 0, 1) * (1 - cold))
    landc = lerp(landc, taiga, cold * 0.6)
    landc = lerp(landc, lerp(tundra, tundra2, veg_noise), np.clip((cold - 0.35) / 0.4, 0, 1))
    # altitude: rock then snow, snowline lower when cold
    gy, gx = np.gradient(h)
    slope = np.clip(np.hypot(gx, gy) * 40.0, 0, 1)
    rockm = np.clip((alt - 0.5) / 0.25, 0, 1) * 0.9 + slope * 0.45
    landc = lerp(landc, lerp(rock, rock2, veg_noise), np.clip(rockm, 0, 1))
    snowline = 0.66 - 0.36 * cold + 0.25 * hot
    snowm = np.clip((alt - snowline) / 0.12, 0, 1)
    landc = lerp(landc, snow, snowm)
    # beaches
    coast = np.clip((h - sea) / 0.02, 0, 1) * (1 - np.clip((h - sea) / 0.06, 0, 1))
    landc = lerp(landc, sand, coast * (1 - cold) * 0.9)

    img = np.where(land[..., None], landc, water)

    # --- hillshade ---
    nx, ny = -gx * 260.0, -gy * 260.0
    nz = np.ones_like(h)
    nl = np.sqrt(nx * nx + ny * ny + nz * nz)
    L = np.array([-0.55, -0.6, 0.58]); L /= np.linalg.norm(L)
    shade = (nx * L[0] + ny * L[1] + nz * L[2]) / nl
    shade = 0.58 + 0.5 * np.clip(shade, 0, 1)
    shade = np.where(land, shade, 0.94 + 0.06 * shade)
    img = img * shade[..., None]

    # --- rivers ---
    for (x0, y0) in design.get('river_sources', []):
        pts = descend(h, x0, y0, sea)
        if len(pts) > 25:
            draw_river(img, pts, hexc('#3d9fd6'))

    # --- forest speckle / texture ---
    grain = fbm(seed + 21, base=48, octaves=2)
    img = img * (0.95 + 0.1 * grain[..., None])
    forest = design.get('forest')
    if forest is not None:
        dots = (vnoise(180, seed + 3) > 0.62) & land & (forest > 0.3) & (snowm < 0.2)
        dots = cv2.GaussianBlur(dots.astype(np.float32), (0, 0), 1.1)
        img = blend(img, hexc('#244d22'), dots * forest * 0.8)

    img = np.clip(img, 0, 1)
    out = (img * 255).astype(np.uint8)
    # painterly pass
    out = cv2.bilateralFilter(out, 7, 40, 7)
    # outside the triangle: dark stone so edges read as the world's rim
    m = tri_mask(lay)
    stone = (np.array([22, 20, 18], np.uint8))
    out[~m] = stone
    # rim darkening
    ed = edge_dist(lay)
    rim = np.clip(ed / 26.0, 0, 1)
    out = (out.astype(np.float32) * (0.55 + 0.45 * rim)[..., None]).astype(np.uint8)
    return out

def descend(h, x, y, sea, max_steps=900):
    pts = [(x, y)]
    x, y = int(x), int(y)
    for _ in range(max_steps):
        best = None; bh = h[y, x]
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0: continue
                xx, yy = x + dx * 2, y + dy * 2
                if 0 <= xx < S and 0 <= yy < S and h[yy, xx] < bh:
                    bh = h[yy, xx]; best = (xx, yy)
        if best is None: break
        x, y = best; pts.append((x, y))
        if h[y, x] <= sea: break
    return pts

def draw_river(img, pts, color):
    if len(pts) > 8:
        arr = np.array(pts, np.float32); k = 7
        pad = np.vstack([np.repeat(arr[:1], k // 2, 0), arr, np.repeat(arr[-1:], k // 2, 0)])
        arr = np.stack([np.convolve(pad[:, i], np.ones(k) / k, 'valid') for i in range(2)], 1)
        pts = [tuple(v) for v in arr]
    n = len(pts)
    for i in range(1, n):
        w = 1.0 + 2.2 * (i / n)
        a = np.array(pts[i - 1], np.float32); b = np.array(pts[i], np.float32)
        cv2.line(img, tuple(np.int32(a)), tuple(np.int32(b)), tuple(float(c) for c in color), int(round(w)), cv2.LINE_AA)

# ---------------- labels ----------------
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
def _font(name):
    for d in (_os.path.join(_HERE, 'fonts'), '/usr/share/fonts/truetype/google-fonts'):
        f = _os.path.join(d, name)
        if _os.path.exists(f): return f
    raise FileNotFoundError(name + ' (expected in pipeline/fonts/)')
FONT_I = _font('Lora-Italic-Variable.ttf')
FONT_R = _font('Lora-Variable.ttf')
def label(img, text, xy, size=30, italic=False, color=(46, 36, 22), halo=(245, 236, 214)):
    pil = Image.fromarray(img)
    d = ImageDraw.Draw(pil)
    f = ImageFont.truetype(FONT_I if italic else FONT_R, size)
    x, y = xy
    bbox = d.textbbox((0, 0), text, font=f); w = bbox[2] - bbox[0]; hh = bbox[3] - bbox[1]
    x -= w / 2; y -= hh / 2
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
        d.text((x + dx, y + dy), text, font=f, fill=halo + (170,))
    d.text((x, y), text, font=f, fill=color)
    return np.array(pil)

# ---------------- face designs ----------------
def design_west(places, lay, seed=101):
    P = {k: bary_px(v, lay) for k, v in places.items()}
    base = warped(seed, 80)
    h = 0.60 + (base - 0.5) * 0.30
    # spike massif at the apex, ridged
    rid = ridged(seed + 2)
    spike = gauss(P['spike'][0], P['spike'][1] + 40, 250, 230)
    h += spike * (0.25 + 0.32 * rid)
    # inland sea around the central island, with Tropicia in the ring
    I = P['island']; T = P['tropicia']
    ang = math.atan2(T[1] - I[1], T[0] - I[0])
    lc = (I[0] + 0.75 * (T[0] - I[0]), I[1] + 0.75 * (T[1] - I[1]))
    basin = wobble(np.maximum(supergauss(I[0], I[1], 168, 158, rot=ang, p=3.5), supergauss(lc[0], lc[1], 118, 92, rot=ang, p=3.0)), seed, 34)
    # swamp: flatten near sea level with pools
    sw = gauss(P['swamp'][0], P['swamp'][1], 190, 150, rot=0.5)
    h = h * (1 - sw * 0.85) + (0.525 + 0.03 * (fbm(seed + 8, base=10, octaves=3) - 0.5)) * sw * 0.85
    pools = (fbm(seed + 9, base=14, octaves=3) > 0.64).astype(np.float32) * sw
    h -= pools * 0.05
    # delta: low braided land at the lower-left corner opening to a small bay
    dl = gauss(P['delta'][0], P['delta'][1], 120, 95)
    bay = gauss(P['delta'][0] - 60, P['delta'][1] + 55, 95, 75)
    h -= bay * 0.38
    chan = fbm(seed + 11, base=6, octaves=4)
    chan = cv2.resize(chan, (S, S // 3)); chan = cv2.resize(chan, (S, S))   # stretched: braided
    h = h * (1 - dl * 0.75) + (0.505 + (chan - 0.5) * 0.10) * dl * 0.75
    # tropical coast band along the right edge (hills)
    ed = edge_dist(lay)
    right_band = gauss(P['tropical'][0] + 40, P['tropical'][1] - 120, 220, 420, rot=-0.55)
    h += right_band * 0.08 * (fbm(seed + 4, base=8, octaves=4) - 0.4)
    # the inland sea, carved last so nothing fills it back in; then the island and Tropicia rise out of it
    seabed = 0.32 + 0.05 * (fbm(seed + 17, base=8, octaves=3) - 0.5)
    h = h * (1 - basin) + seabed * basin
    isl = wobble(supergauss(I[0], I[1], 84, 70, rot=-0.4, p=3.5), seed + 1, 22)
    h += isl * (0.38 + 0.24 * rid)
    h += supergauss(T[0], T[1], 34, 27, p=3.0) * 0.42
    sea_level = 0.5
    # climate
    v_apex = np.zeros((S, S), np.float32)
    ys, xs = np.mgrid[0:S, 0:S].astype(np.float32)
    v_apex = np.clip(1 - (ys - lay['apex'][1]) / (lay['bl'][1] - lay['apex'][1]), 0, 1)
    temp = 0.52 - 0.35 * np.clip((h - 0.5) / 0.5, 0, 1) + 0.42 * right_band - 0.05 * v_apex
    moist = 0.55 + 0.5 * sw + 0.3 * right_band + 0.25 * dl + 0.15 * basin + 0.25 * gauss(I[0], I[1], 110, 90)
    forest = np.clip(0.25 + 0.7 * right_band + 0.3 * (fbm(seed + 6, base=6, octaves=3) - 0.4), 0, 1)
    sources = [(int(P['spike'][0] + dx), int(P['spike'][1] + 70 + dy)) for dx, dy in [(-70, 40), (60, 30), (-20, 90), (100, 120), (-120, 130)]]
    return dict(height=h, temp=np.clip(temp, 0, 1), moist=np.clip(moist, 0, 1), sea_level=sea_level, forest=forest, river_sources=sources), P

def design_south(places, lay, seed=202):
    P = {k: bary_px(v, lay) for k, v in places.items()}
    base = warped(seed, 90)
    h = 0.60 + (base - 0.5) * 0.30
    rid = ridged(seed + 2)
    spike = gauss(P['spike-south'][0], P['spike-south'][1] + 50, 240, 230)
    h += spike * (0.24 + 0.3 * rid)
    C = P['continent-south']
    basin = wobble(np.maximum(supergauss(C[0], C[1], 185, 152, rot=-0.15, p=3.5), supergauss(C[0] - 205, C[1] + 45, 150, 118, rot=-0.3, p=3.0)), seed, 34)
    # delta bay at the lower-left
    D = P['delta-south']
    bay = gauss(D[0] - 70, D[1] + 60, 105, 80)
    h -= bay * 0.40
    dl = gauss(D[0], D[1], 120, 95)
    chan = fbm(seed + 11, base=6, octaves=4); chan = cv2.resize(cv2.resize(chan, (S, S // 3)), (S, S))
    h = h * (1 - dl * 0.75) + (0.505 + (chan - 0.5) * 0.10) * dl * 0.75
    # the sea, carved last; the continent rises out of it with a snowy spine
    seabed = 0.32 + 0.05 * (fbm(seed + 17, base=8, octaves=3) - 0.5)
    h = h * (1 - basin) + seabed * basin
    cont = wobble(supergauss(C[0], C[1], 96, 76, rot=0.35, p=4.0), seed + 1, 24)
    h += cont * (0.38 + 0.22 * rid)
    h += gauss(C[0] - 5, C[1] - 30, 70, 22, rot=0.25) * 0.22 * (0.5 + rid) * cont
    sea_level = 0.5
    ys, xs = np.mgrid[0:S, 0:S].astype(np.float32)
    v_apex = np.clip(1 - (ys - lay['apex'][1]) / (lay['bl'][1] - lay['apex'][1]), 0, 1)
    temp = 0.22 + 0.85 * v_apex - 0.3 * np.clip((h - 0.5) / 0.5, 0, 1)
    moist = 0.6 + 0.15 * basin + 0.25 * dl + 0.2 * v_apex
    forest = np.clip(0.35 + 0.5 * v_apex + 0.3 * (fbm(seed + 6, base=6, octaves=3) - 0.4), 0, 1)
    sources = [(int(P['spike-south'][0] + dx), int(P['spike-south'][1] + 80 + dy)) for dx, dy in [(-60, 40), (70, 20), (-110, 130), (110, 140), (0, 160)]]
    sources += [(int(C[0] + dx), int(C[1] - 40 + dy)) for dx, dy in [(-60, 0), (50, -5), (0, 10)]]
    return dict(height=h, temp=np.clip(temp, 0, 1), moist=np.clip(moist, 0, 1), sea_level=sea_level, forest=forest, river_sources=sources), P

def design_far(places, lay, seed=303):
    P = {k: bary_px(v, lay) for k, v in places.items()}
    base = warped(seed, 70)
    rid = ridged(seed + 2)
    h = 0.60 + (base - 0.5) * 0.26 + rid * 0.12
    M = P['mountains-far']
    rid2 = ridged(seed + 5)
    h += gauss(M[0], M[1], 250, 210, rot=0.2) * (0.18 + 0.45 * rid2)
    # warm basin (Warmia), temperate valley (Ehia): lower and smoother
    W = P['warmia']; E = P['ehia']; T = P['treeland']
    wb = gauss(W[0], W[1], 150, 105, rot=-0.3); eb = gauss(E[0], E[1], 140, 100, rot=0.4)
    h = h * (1 - wb * 0.7) + (0.56 + 0.05 * (fbm(seed + 8, base=8, octaves=3) - 0.5)) * wb * 0.7
    h = h * (1 - eb * 0.7) + (0.57 + 0.05 * (fbm(seed + 9, base=8, octaves=3) - 0.5)) * eb * 0.7
    # delta bay at the bottom vertex
    D = P['delta-far']
    bay = wobble(gauss(D[0] + 10, D[1] + 45, 100, 90), seed, 30)
    h -= bay * 0.5
    dl = gauss(D[0], D[1] - 40, 110, 100)
    chan = fbm(seed + 11, base=6, octaves=4); chan = cv2.resize(cv2.resize(chan, (S // 3, S)), (S, S))
    h = h * (1 - dl * 0.65) + (0.505 + (chan - 0.5) * 0.10) * dl * 0.65
    sea_level = 0.5
    temp = 0.55 - 0.42 * np.clip((h - 0.55) / 0.55, 0, 1) + 0.55 * wb + 0.15 * eb + 0.1 * gauss(T[0], T[1], 150, 120)
    moist = 0.5 + 0.35 * gauss(T[0], T[1], 170, 130) + 0.2 * eb - 0.4 * wb + 0.2 * dl
    forest = np.clip(0.15 + 0.85 * gauss(T[0], T[1], 170, 130) + 0.35 * eb + 0.25 * (fbm(seed + 6, base=6, octaves=3) - 0.4), 0, 1)
    sources = [(int(M[0] + dx), int(M[1] + dy)) for dx, dy in [(-120, 60), (110, 90), (0, 150), (-60, -110), (140, -60), (60, 200)]]
    return dict(height=h, temp=np.clip(temp, 0, 1), moist=np.clip(moist, 0, 1), sea_level=sea_level, forest=forest, river_sources=sources), P

LABELS = {
    'west': [('spike', 'Spikia', 34, False, (0, 60)), ('swamp', 'The Swamp', 28, True, (0, 0)), ('delta', 'Wetia', 26, True, (30, -30)), ('tropical', 'Tropical', 28, True, (-70, -20)),
             ('island', 'The Central Island', 24, False, (0, 0)), ('tropicia', 'Tropicia', 20, True, (0, 40))],
    'south': [('spike-south', 'Spikia', 34, False, (0, 60)), ('continent-south', 'The Southern Continent', 22, False, (0, 112)), ('delta-south', 'Wetia', 26, True, (40, -30)),
              ('continent-south', 'Snowia', 20, True, (0, -40)), ('continent-south', 'Coldland', 20, True, (-52, 24)), ('continent-south', 'Beria', 20, True, (52, 26))],
    'far': [('mountains-far', 'Extreme Mountains', 30, False, (0, -70)), ('warmia', 'Warmia', 28, True, (-20, -30)), ('ehia', 'Ehia', 28, True, (-30, 0)), ('treeland', 'Tree Land', 28, True, (-40, -30)),
            ('delta-far', 'Wetia', 26, True, (40, -40))],
}

def build(face, places, lay, design_fn, seed):
    d, P = design_fn(places, lay, seed)
    raw = render(d, seed, lay)
    img = raw.copy()
    for key, text, size, italic, (dx, dy) in LABELS[face]:
        x, y = P[key]; img = label(img, text, (x + dx, y + dy), size=size, italic=italic)
    return img, raw, P

def codex_crop(raw, cx, cy, half, labels, out, scale=2):
    x0, y0 = int(cx - half), int(cy - half); x1, y1 = x0 + 2 * half, y0 + 2 * half
    crop = raw[max(0, y0):y1, max(0, x0):x1]
    crop = cv2.resize(crop, (crop.shape[1] * scale, crop.shape[0] * scale), interpolation=cv2.INTER_CUBIC)
    for text, (dx, dy), size, italic in labels:
        crop = label(crop, text, ((cx - x0 + dx) * scale, (cy - y0 + dy) * scale), size=size, italic=italic)
    cv2.imwrite(out, cv2.cvtColor(crop, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 86])
    return crop

if __name__ == '__main__':
    west = json.load(open('west_places.json'))
    sf = json.load(open('south_far_places.json'))
    south = {k: v for k, v in sf['south'].items() if k != 'tundra-south'}
    far = {k: v for k, v in sf['far'].items() if k != 'tundra-far'}
    anchors = {}
    for face, places, lay, fn, seed in [('west', west, APEX_UP, design_west, 101), ('south', south, APEX_UP, design_south, 202), ('far', far, APEX_UP, design_far, 303)]:
        img, raw, P = build(face, places, lay, fn, seed)
        anchors[face] = {k: list(v) for k, v in P.items()}
        cv2.imwrite(f'map_{face}.jpg', cv2.cvtColor(raw, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])   # the world wears the clean map; names live on the markers
        # Codex copy: the triangle only, 560px wide
        m = tri_mask(lay); ys_, xs_ = np.where(m); x0, x1, y0, y1 = xs_.min(), xs_.max(), ys_.min(), ys_.max()
        cod = img[y0:y1 + 1, x0:x1 + 1]; cod = cv2.resize(cod, (560, int(cod.shape[0] * 560 / cod.shape[1])), interpolation=cv2.INTER_AREA)
        cv2.imwrite(f'codex_{face}.jpg', cv2.cvtColor(cod, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 84])
        if face == 'west':
            I = P['island']
            codex_crop(raw, I[0], I[1], 150, [(n, off, 24, True) for _, n, off, _ in ISLAND_NATIONS] + [('The Central Island', (0, 118), 26, False)], 'codex_island.jpg')
        if face == 'south':
            C = P['continent-south']
            codex_crop(raw, C[0], C[1], 160, [(n, off, 26, True) for _, n, off, _ in CONTINENT_NATIONS] + [('The Southern Continent', (0, 118), 26, False)], 'codex_continent.jpg')
        prev = img.copy()
        for k, (x, y) in P.items():
            cv2.circle(prev, (int(x), int(y)), 6, (255, 255, 0), 2)
        cv2.imwrite(f'map_{face}_prev.png', cv2.cvtColor(cv2.resize(prev, (640, 640)), cv2.COLOR_RGB2BGR))
        print(face, 'done')
    json.dump(anchors, open('map_anchors.json', 'w'))
