"""Trace Ruby's blob outlines (southern continent, central island) from the sketches into texture-space polygons."""
import json, math
import numpy as np, cv2
from sketches import flatten_ink, remove_ruled_lines
from radial import tri_layout

apex, bl, br = tri_layout(1024)

def seed_region(ink, seed, thr=0.3, close=15):
    wall = (ink > thr).astype(np.uint8)
    wall = cv2.morphologyEx(wall, cv2.MORPH_CLOSE, np.ones((close, close), np.uint8))
    free = (1 - wall).astype(np.uint8)
    n, lab = cv2.connectedComponents(free, connectivity=4)
    region = (lab == lab[seed[1], seed[0]]).astype(np.uint8)
    region = cv2.morphologyEx(region, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    region = cv2.dilate(region, np.ones((7, 7), np.uint8))       # take back the line's own width
    return region

def contour_of(region, eps=2.0):
    cs, _ = cv2.findContours(region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cs, key=cv2.contourArea)
    return cv2.approxPolyDP(c, eps, True)[:, 0, :].astype(np.float32)

def smooth_closed(pts, n=160, sigma=2.0):
    """resample a closed polygon to n points and smooth it"""
    pts = np.vstack([pts, pts[:1]])
    seg = np.hypot(*np.diff(pts, axis=0).T); cum = np.concatenate([[0], np.cumsum(seg)])
    t = np.linspace(0, cum[-1], n, endpoint=False)
    x = np.interp(t, cum, pts[:, 0]); y = np.interp(t, cum, pts[:, 1])
    k = int(sigma * 3); ker = np.exp(-0.5 * (np.arange(-k, k + 1) / sigma) ** 2); ker /= ker.sum()
    xs = np.convolve(np.concatenate([x[-k:], x, x[:k]]), ker, 'same')[k:-k]
    ys = np.convolve(np.concatenate([y[-k:], y, y[:k]]), ker, 'same')[k:-k]
    return np.stack([xs, ys], 1).astype(np.float32)

def to_texture(pts, src_tri):
    M = cv2.getAffineTransform(np.float32(src_tri), np.float32([apex, bl, br]))
    return cv2.transform(pts[None], M)[0]

def fit(pts, center, width, height):
    """scale a polygon (any coords) to the given texture size, centred at center"""
    p = pts - pts.mean(0)
    w, h = p[:, 0].max() - p[:, 0].min(), p[:, 1].max() - p[:, 1].min()
    p[:, 0] *= width / w; p[:, 1] *= height / h
    return p + np.array(center, np.float32)

out = {}
# ---- continent: Amethyst's South sketch; ruled lines removed, seed at the continent marker ----
img, ink = flatten_ink('crop_south_sketch.png', boost=3.0, sigma=35)
ink[:230, :] = 0
clean, _ = remove_ruled_lines(ink, min_len=200, tol_deg=8.0, thickness=9)
reg = seed_region(clean, (478, 905), thr=0.3, close=17)
print('continent region area', int(reg.sum()))
c = smooth_closed(contour_of(reg), 160, 2.5)
T, L, R = (475.0, 560.0), (120.0, 1250.0), (700.0, 1075.0)
cont = to_texture(c, [T, L, R])
print('continent bbox', cont.min(0).round(), cont.max(0).round(), 'centroid', cont.mean(0).round())
out['continent'] = cont.round(1).tolist()

# ---- island: the 'central island nations' sketch gives the outline; Sapphire's West sketch gives the size and place ----
img2, ink2 = flatten_ink('crop_island_trop.png', boost=3.2, sigma=35)
clean2, _ = remove_ruled_lines(ink2, min_len=220, tol_deg=7.0, thickness=9)
reg2 = seed_region(clean2, (300, 600), thr=0.3, close=17)
print('island region area', int(reg2.sum()))
c2 = smooth_closed(contour_of(reg2), 160, 2.5)
# size from the West sketch: the X'd blob spans ~ (560..800, 620..900) sketch px -> texture via the sketch->texture affine scale
A_s, L_s, R_s = (815.0, 345.0), (195.0, 1000.0), (955.0, 1050.0)
box = to_texture(np.float32([[560, 620], [800, 620], [800, 900], [560, 900]]), [A_s, L_s, R_s])
bw, bh = box[:, 0].max() - box[:, 0].min(), box[:, 1].max() - box[:, 1].min()
anchors = json.load(open('map_anchors.json'))
I = anchors['west']['island']
isl = fit(c2, I, bw * 0.92, bh * 0.92)
print('island size', round(bw * 0.92), round(bh * 0.92), 'centre', [round(v) for v in I])
out['island'] = isl.round(1).tolist()
json.dump(out, open('blobs.json', 'w'))

prev = np.full((1024, 1024, 3), 30, np.uint8)
cv2.polylines(prev, [np.int32([apex, bl, br])], True, (90, 90, 90), 2)
cv2.polylines(prev, [np.int32(cont)], True, (120, 200, 255), 3)
cv2.polylines(prev, [np.int32(isl)], True, (120, 255, 160), 3)
cv2.imwrite('blobs_prev.png', cv2.resize(prev, (512, 512)))
