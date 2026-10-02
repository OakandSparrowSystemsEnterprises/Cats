"""Render a designed face as painted terrain in the Canon art's own style.
d['zones'] (class -> weight map over land) decides what each region looks like; altitude adds peaks and snow."""
import numpy as np, cv2
from texsynth import paint
from mapgen import S, fbm, descend

def smooth(a, lo, hi):
    t = np.clip((a - lo) / (hi - lo), 0, 1); return t * t * (3 - 2 * t)

def render_painted(d, seed, tri_mask):
    h = d['height']; sea = d['sea_level']
    edge = cv2.distanceTransform(tri_mask.astype(np.uint8), cv2.DIST_L2, 5)
    water = h < sea; land = ~water
    lb = land.astype(np.uint8)
    d_in = cv2.distanceTransform(lb, cv2.DIST_L2, 5)
    d_out = cv2.distanceTransform(1 - lb, cv2.DIST_L2, 5)
    hl = h[land & tri_mask]
    top = np.percentile(hl, 97) if hl.size else sea + 0.5
    alt = np.clip((h - sea) / max(top - sea, 1e-3), 0, 1)
    gy, gx = np.gradient(h); slope = np.clip(np.hypot(gx, gy) * 50.0, 0, 1)
    W_ = water.astype(np.float32); L_ = land.astype(np.float32)
    w = {}
    w_sea = {'sea': np.ones_like(h)}          # open sea only: no stray islets
    # relief classes from altitude, then the zones fill the rest
    peak = np.clip(d.get('peak', smooth(alt, 0.55, 0.8)), 0, 1)
    snow = np.clip(peak * d.get('snowy', 1.0), 0, 1)
    ridge = np.maximum(smooth(alt, 0.42, 0.62), smooth(slope, 0.55, 0.85)) * (1 - snow)
    cliff = np.zeros_like(L_)          # (edge cliffs off: their patches carry water and muddy the shared edges)
    w['white'] = snow
    w['mountain'] = ridge
    rest = 1 - np.clip(snow + ridge, 0, 1)
    zones = d['zones']
    tot = sum(np.clip(z, 0, 1) for z in zones.values()) + 1e-3
    for c, z in zones.items():
        w[c] = w.get(c, 0) + rest * np.clip(z, 0, 1) / tot
    # land and sea are painted as two full layers and cut along the designed coastline, so the coast sits exactly
    # where the mask puts it (and where the neighbouring face expects it), not where a patch boundary happened to fall
    img_land = paint(w, S, seed, feather=28, dry_mask=(edge < 64))     # no lakes or rivers in the patches along the shared edges
    img_sea = paint(w_sea, S, seed + 1000, P=64, cell=22, feather=32)
    cut = np.clip(0.5 + (d_in - d_out) / 4.0, 0, 1)[..., None]
    img = img_sea * (1 - cut) + img_land * cut
    rest = rest * L_
    nx, ny = -gx * 260.0, -gy * 260.0; nz = np.ones_like(h); nl = np.sqrt(nx * nx + ny * ny + nz * nz)
    Lt = np.array([-0.55, -0.6, 0.58]); Lt /= np.linalg.norm(Lt)
    shade = np.clip((nx * Lt[0] + ny * Lt[1] + nz * Lt[2]) / nl, 0, 1)
    shade = np.where(land, 0.9 + 0.16 * shade, 1.0)
    img = img * shade[..., None]
    # shoreline: a sand rim on the land and bright shallows on the water, as the art paints its coasts
    sand = np.clip(1 - d_in / 6.0, 0, 1) * L_; shallow = np.clip(1 - d_out / 9.0, 0, 1) * W_
    img = img * (1 - sand[..., None] * 0.75) + np.array([0.87, 0.80, 0.62], np.float32) * sand[..., None] * 0.75
    img = img * (1 - shallow[..., None] * 0.55) + np.array([0.55, 0.88, 0.92], np.float32) * shallow[..., None] * 0.55
    # tints: swamp darker and greener, tundra paler, hot lands warmer
    for c, col, k in (('swamp', (0.10, 0.16, 0.08), 0.28), ('hot', (0.95, 0.72, 0.35), 0.16), ('cold', (0.85, 0.88, 0.95), 0.22)):
        z = d.get('tints', {}).get(c)
        if z is not None:
            z = np.clip(z, 0, 1) * rest
            img = img * (1 - z[..., None] * k) + np.array(col, np.float32) * z[..., None] * k
    # bring back the art's punch after the patch blending: a little sharpening and saturation
    blur = cv2.GaussianBlur(img, (0, 0), 2.0)
    img = np.clip(img + 0.45 * (img - blur), 0, 1)
    hsv = cv2.cvtColor(np.clip(img * 255, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * 1.18, 0, 255); hsv[..., 2] = np.clip(hsv[..., 2] * 1.04, 0, 255)
    img8 = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).copy()
    for (x0, y0) in d.get('river_sources', []):
        pts = descend(h, x0, y0, sea)
        if len(pts) > 25:
            draw_river(img8, pts)
    return img8

def draw_river(img, pts):
    arr = np.array(pts, np.float32); k = 7
    pad = np.vstack([np.repeat(arr[:1], k // 2, 0), arr, np.repeat(arr[-1:], k // 2, 0)])
    arr = np.stack([np.convolve(pad[:, i], np.ones(k) / k, 'valid') for i in range(2)], 1)
    n = len(arr)
    for i in range(1, n):
        wdt = 1.2 + 2.6 * (i / n)
        a = tuple(int(v) for v in arr[i - 1]); b = tuple(int(v) for v in arr[i])
        cv2.line(img, a, b, (52, 120, 160), int(round(wdt + 1.5)), cv2.LINE_AA)
    for i in range(1, n):
        wdt = 1.2 + 2.6 * (i / n)
        a = tuple(int(v) for v in arr[i - 1]); b = tuple(int(v) for v in arr[i])
        cv2.line(img, a, b, (118, 205, 232), int(round(wdt)), cv2.LINE_AA)
