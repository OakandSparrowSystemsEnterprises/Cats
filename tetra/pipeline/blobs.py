"""Ruby's outlines, read off the sketches by hand (photo tracing was unreliable), placed in texture space (1024, apex-up)."""
import json
import numpy as np, cv2
from radial import tri_layout
apex, bl, br = tri_layout(1024)

def smooth_closed(pts, n=200, sigma=2.5):
    pts = np.vstack([pts, pts[:1]]).astype(np.float32)
    seg = np.hypot(*np.diff(pts, axis=0).T); cum = np.concatenate([[0], np.cumsum(seg)])
    t = np.linspace(0, cum[-1], n, endpoint=False)
    x = np.interp(t, cum, pts[:, 0]); y = np.interp(t, cum, pts[:, 1])
    k = int(sigma * 3); ker = np.exp(-0.5 * (np.arange(-k, k + 1) / sigma) ** 2); ker /= ker.sum()
    xs = np.convolve(np.concatenate([x[-k:], x, x[:k]]), ker, 'same')[k:-k]
    ys = np.convolve(np.concatenate([y[-k:], y, y[:k]]), ker, 'same')[k:-k]
    return np.stack([xs, ys], 1).astype(np.float32)

def to_texture(pts, src_tri):
    M = cv2.getAffineTransform(np.float32(src_tri), np.float32([apex, bl, br]))
    return cv2.transform(np.float32(pts)[None], M)[0]

def scale_about(pts, s, c=None):
    c = pts.mean(0) if c is None else np.float32(c)
    return (pts - c) * s + c

# ---- Southern continent: Amethyst's South sketch (crop_south_sketch.png coords; blob region offset (330,700)) ----
cont_sketch = np.float32([
    (95, 95), (130, 80), (175, 68), (215, 72), (232, 85),            # top, rising to the right
    (240, 130), (243, 200), (245, 260), (250, 300),                   # right side
    (300, 285), (330, 300), (335, 330), (300, 345), (260, 352),       # small peninsula at the lower right
    (240, 362), (200, 372), (150, 372), (90, 360), (45, 340),         # bottom
    (30, 300), (40, 240), (55, 180), (70, 130),                       # left side, leaning out toward the bottom
]) + np.float32([330, 700])
T, L, R = (475.0, 560.0), (120.0, 1250.0), (700.0, 1075.0)
# the photo is sheared by perspective: take the position from the chart, but keep the shape as she drew it
M = cv2.getAffineTransform(np.float32([T, L, R]), np.float32([apex, bl, br]))
scale = float(np.sqrt(abs(np.linalg.det(M[:, :2]))))
cont_centre = cv2.transform(cont_sketch.mean(0)[None, None], M)[0, 0]
cw = (cont_sketch[:, 0].max() - cont_sketch[:, 0].min()) * scale
ch = (cont_sketch[:, 1].max() - cont_sketch[:, 1].min()) * scale

# ---- Central island: outline from the 'central island nations' sketch, sized and placed from Sapphire's West chart ----
isl_sketch = np.float32([
    (75, 140), (110, 95), (170, 70), (230, 55), (300, 45), (350, 55), (400, 70), (430, 110), (440, 160),
    (445, 220), (440, 290), (430, 340), (420, 380), (400, 420), (350, 450), (300, 470), (250, 490), (200, 500),
    (150, 480), (110, 440), (80, 390), (60, 330), (55, 260), (60, 200),
])
def place(pts, center, width, height):
    p = pts - pts.mean(0)
    w, h = p[:, 0].max() - p[:, 0].min(), p[:, 1].max() - p[:, 1].min()
    p[:, 0] *= width / w; p[:, 1] *= height / h
    return p + np.float32(center)
ISLAND_CENTER = (528.0, 606.0)
island = smooth_closed(place(isl_sketch, ISLAND_CENTER, 186, 232), 200, 2.0)
continent = smooth_closed(place(cont_sketch, (cont_centre[0] - 30, cont_centre[1] - 20), cw * 0.72, ch * 0.72), 200, 2.0)
print('continent as drawn', round(cw), round(ch), 'placed at', cont_centre.round())

def fit_inside(pts, margin, shrink_step=0.97, max_iter=30):
    """shrink about the centroid until the polygon keeps `margin` px from the face edges"""
    m = np.zeros((1024, 1024), np.uint8); cv2.fillPoly(m, [np.int32([apex, bl, br])], 1)
    dist = cv2.distanceTransform(m, cv2.DIST_L2, 5)
    for _ in range(max_iter):
        xi = np.clip(pts[:, 0].round().astype(int), 0, 1023); yi = np.clip(pts[:, 1].round().astype(int), 0, 1023)
        if dist[yi, xi].min() >= margin: break
        pts = scale_about(pts, shrink_step)
    return pts

continent = fit_inside(continent, 46)
island = fit_inside(island, 46)
if __name__ == '__main__':
    print('continent bbox', continent.min(0).round(), continent.max(0).round(), 'centroid', continent.mean(0).round())
    print('island bbox', island.min(0).round(), island.max(0).round(), 'centroid', island.mean(0).round())
    prev = np.full((1024, 1024, 3), 30, np.uint8)
    cv2.polylines(prev, [np.int32([apex, bl, br])], True, (90, 90, 90), 2)
    cv2.polylines(prev, [np.int32(continent)], True, (120, 200, 255), 3)
    cv2.polylines(prev, [np.int32(island)], True, (120, 255, 160), 3)
    cv2.imwrite('blobs_prev.png', cv2.resize(prev, (512, 512)))
    json.dump(dict(continent=continent.round(1).tolist(), island=island.round(1).tolist()), open('blobs.json', 'w'))
