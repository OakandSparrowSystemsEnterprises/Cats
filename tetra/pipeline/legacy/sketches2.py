"""South (Amethyst) and Far (Obsidian) sketches -> face textures, Codex drawings, and place coordinates.
Run after sketches.py (which runs bake.py)."""
import json, os
import numpy as np, cv2
from PIL import Image
from radial import tri_layout
from sketches import flatten_ink, remove_ruled_lines
from bake import unwritten, bary

S = 1024
apex, bl, br = tri_layout(S)

def paper_mask(img, sigma=45, thr=80, erode=15):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    m = (cv2.GaussianBlur(gray, (0, 0), sigma) > thr).astype(np.uint8)
    return cv2.erode(m, np.ones((erode, erode), np.uint8)) > 0

def layers(path, boost=3.0, sigma=35, min_len=180, tol=9.0, thick=9, black_thr=90, noise=0.16):
    img, ink = flatten_ink(path, boost=boost, sigma=sigma)
    ink = ink * paper_mask(img)
    b, g, r = [img[..., i].astype(np.float32) for i in range(3)]
    blue_strict = ((b > 165) & (b - r > 75) & (g > 110) & (ink > 0.25)).astype(np.float32)
    black = ((img.max(axis=2) < black_thr) & (ink > 0.5)).astype(np.float32)
    dark = cv2.dilate((black > 0).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    clean, n = remove_ruled_lines(ink, min_len=min_len, tol_deg=tol, thickness=thick, exclude_dark=dark)
    blue = cv2.dilate(blue_strict * (clean > 0.1), np.ones((3, 3), np.uint8))
    pencil = np.clip(clean - black - blue, 0, 1)
    pencil = cv2.GaussianBlur(pencil, (0, 0), 0.8)
    pencil = np.clip((pencil - noise) / (0.62 - noise), 0, 1)   # soft threshold: faint ruling fades, pencil stays
    return img, pencil, cv2.GaussianBlur(black, (0, 0), 0.8), cv2.GaussianBlur(blue, (0, 0), 1.0), n

def dominant_angle(ink):
    import math
    binm = (ink > 0.3).astype(np.uint8) * 255
    lines = cv2.HoughLinesP(binm, 1, np.pi / 360, threshold=60, minLineLength=120, maxLineGap=25)
    if lines is None: return 0.0
    angs = [math.degrees(math.atan2(y2 - y1, x2 - x1)) for x1, y1, x2, y2 in lines[:, 0]]
    angs = [((a + 90) % 180) - 90 for a in angs]
    hist, edges = np.histogram(angs, bins=90, range=(-45, 45))
    i = int(np.argmax(hist)); return (edges[i] + edges[i + 1]) / 2

def remove_lines_morph(ink, keep_mask, klen=45):
    """Rotate so the ruling is horizontal, open with a long horizontal kernel, subtract those runs."""
    ang = dominant_angle(ink)
    h, w = ink.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, 1.0)
    Mi = cv2.getRotationMatrix2D((w / 2, h / 2), -ang, 1.0)
    rot = cv2.warpAffine(ink, M, (w, h), flags=cv2.INTER_LINEAR)
    binm = (rot > 0.12).astype(np.uint8)
    binm = cv2.morphologyEx(binm, cv2.MORPH_CLOSE, np.ones((1, 15), np.uint8))
    runs = cv2.morphologyEx(binm, cv2.MORPH_OPEN, np.ones((1, klen), np.uint8))
    runs = cv2.dilate(runs, np.ones((7, 3), np.uint8))
    mask = cv2.warpAffine(runs.astype(np.float32), Mi, (w, h), flags=cv2.INTER_LINEAR) > 0.3
    mask[keep_mask] = False
    out = ink.copy(); out[mask] = 0
    return out

def warp_to_face(layer, tri):
    M = cv2.getAffineTransform(np.float32(tri), np.float32([apex, bl, br]))
    return cv2.warpAffine(layer, M, (S, S), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)

def over(dst, alpha, color_bgr):
    a = np.clip(alpha, 0, 1)[..., None]
    return dst * (1 - a) + np.array(color_bgr, np.float32) * a

def compose(base_bgr, parts):
    tex = base_bgr.astype(np.float32) / 255.0
    for pencil, black, blue in parts:
        tex = over(tex, pencil * 0.85, (0.62, 0.70, 0.80))
        tex = over(tex, black * 0.95, (0.80, 0.90, 0.98))
        tex = over(tex, blue * 0.95, (1.00, 0.62, 0.30))
    return np.clip(tex * 255, 0, 255).astype(np.uint8)

def drawing_png(pencil, black, blue, out, width, crop=None, clear=()):
    full = np.clip(pencil * 0.9 + black + blue, 0, 1)
    for (y0, y1, x0, x1) in clear:
        full[y0:y1, x0:x1] = 0
    if crop:
        y0, y1, x0, x1 = crop; full = full[y0:y1, x0:x1]; blue = blue[y0:y1, x0:x1]
    rgba = np.zeros((*full.shape, 4), np.uint8)
    bl_a = np.clip(blue, 0, 1)
    rgba[..., 0] = (242 * (1 - bl_a) + 90 * bl_a).astype(np.uint8)
    rgba[..., 1] = (232 * (1 - bl_a) + 165 * bl_a).astype(np.uint8)
    rgba[..., 2] = (211 * (1 - bl_a) + 255 * bl_a).astype(np.uint8)
    rgba[..., 3] = (full * 255).astype(np.uint8)
    ys, xs = np.where(rgba[..., 3] > 40)
    if len(xs):
        pad = 10; x0, x1, y0, y1 = max(0, xs.min() - pad), min(rgba.shape[1], xs.max() + pad), max(0, ys.min() - pad), min(rgba.shape[0], ys.max() + pad)
        rgba = rgba[y0:y1, x0:x1]
    im = Image.fromarray(rgba, 'RGBA')
    im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
    im.quantize(colors=32, method=Image.Quantize.FASTOCTREE).save(out, optimize=True)
    return im.size

out = {}

# ---------------- South face (Amethyst) ----------------
img, pencil, black, blue, n = layers('crop_south_sketch.png', boost=3.0, sigma=35, min_len=200, tol=8.0, thick=11, black_thr=70, noise=0.26)
print('south ruled lines removed', n)
# messenger UI at the top of the crop (the message bubble) -> clear
pencil[:230, :] = 0; black[:230, :] = 0; blue[:230, :] = 0
pencil[:, :28] = 0; black[:, :28] = 0; blue[:, :28] = 0
T, L, R = (475.0, 560.0), (120.0, 1250.0), (700.0, 1075.0)
tex = compose(unwritten(23, (1.22, 1.02, 0.90)), [(warp_to_face(pencil, [T, L, R]), warp_to_face(black, [T, L, R]), warp_to_face(blue, [T, L, R]))])
cv2.imwrite('tex_south.jpg', tex, [cv2.IMWRITE_JPEG_QUALITY, 88])
print('south chart', drawing_png(pencil, black, blue, 'south_chart.png', 380))
south_places = {'spike-south': (478, 640), 'continent-south': (478, 905), 'delta-south': (215, 1160), 'tundra-south': (470, 1120)}
out['south'] = {k: [round(v, 4) for v in bary(p, T, L, R)] for k, p in south_places.items()}

# ---------------- Far face (Obsidian): structure sketch + nations sketch ----------------
img1, p1, k1, b1, n1 = layers('crop_far_sketch.png', boost=3.0, sigma=35, min_len=200, tol=8.0, thick=11, black_thr=70, noise=0.26)
print('far ruled lines removed', n1)
p1[:420, :] = 0; k1[:420, :] = 0; b1[:420, :] = 0     # UI text above the notebook
p1[:, :100] = 0; k1[:, :100] = 0; b1[:, :100] = 0        # notebook spine
T1, L1, R1 = (400.0, 610.0), (235.0, 990.0), (640.0, 940.0)
img2, p2, k2, b2, n2 = layers('crop_far_nations.png', boost=3.2, sigma=35, min_len=200, tol=8.0, thick=11, black_thr=70, noise=0.2)
print('far nations ruled lines removed', n2)
p2[:60, :] = 0
T2, L2, R2 = (430.0, 240.0), (125.0, 850.0), (690.0, 840.0)
tex = compose(unwritten(7, (1.0, 1.0, 1.0)), [
    (warp_to_face(p1, [T1, L1, R1]) * 0.7, warp_to_face(k1, [T1, L1, R1]), warp_to_face(b1, [T1, L1, R1])),
    (warp_to_face(p2, [T2, L2, R2]), warp_to_face(k2, [T2, L2, R2]), warp_to_face(b2, [T2, L2, R2])),
])
cv2.imwrite('tex_far.jpg', tex, [cv2.IMWRITE_JPEG_QUALITY, 88])
print('far chart', drawing_png(p1, k1, b1, 'far_chart.png', 380))
print('far nations chart', drawing_png(p2, k2, b2, 'far_nations.png', 380))
far_places = {'mountains-far': (390, 790), 'delta-far': (262, 960), 'tundra-far': (445, 918), 'warmia': (505, 545), 'ehia': (540, 660), 'treeland': (560, 770)}
# warmia/ehia/treeland come from the nations sketch, the rest from the structure sketch
out['far'] = {}
for k, p in far_places.items():
    tri = (T2, L2, R2) if k in ('warmia', 'ehia', 'treeland') else (T1, L1, R1)
    bb = bary(p, *tri); assert all(-0.02 <= v <= 1.02 for v in bb), (k, bb)
    out['far'][k] = [round(v, 4) for v in bb]

# ---------------- Codex drawings: West central island nations, South continent nations ----------------
imgI, pI, kI, bI, nI = layers('crop_island_trop.png', boost=3.2, sigma=35, min_len=220, tol=7.0, thick=11, black_thr=70, noise=0.2)
print('island ruled lines removed', nI)
print('west island', drawing_png(pI, kI, bI, 'west_island.png', 380, crop=(380, 1000, 120, 720)))
imgS, pS, kS, bS, nS = layers('crop_south_nations.png', boost=3.2, sigma=35, min_len=220, tol=7.0, thick=11, black_thr=70, noise=0.2)
print('south nations ruled lines removed', nS)
print('south continent', drawing_png(pS, kS, bS, 'south_continent.png', 380, crop=(560, 1090, 200, 720)))

json.dump(out, open('south_far_places.json', 'w'), indent=1)
print(json.dumps(out))
for nme in ['south_chart.png', 'far_chart.png', 'far_nations.png', 'west_island.png', 'south_continent.png']:
    a = Image.open(nme).convert('RGBA'); pv = Image.new('RGB', a.size, (8, 11, 20)); pv.paste(a, (0, 0), a); pv.save(nme.replace('.png', '_prev.png'))
    print(nme, os.path.getsize(nme))
