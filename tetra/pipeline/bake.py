"""Bake the four Tetra face textures from the latest map art, and emit region geometry.

Art pixel coords (1448x1086): A apex, L/R outer corners, D bottom vertex, P/Q where the
orange V meets the outer edges.
  Canon face  = kite A,P,D,Q  -> radial (angle-matched) warp into the triangle (tex_canon.jpg)
  West, South, Far = procedural 'unwritten' stone placeholders (tex_west/south/far.jpg). Nothing in the
                build reads them any more: the side faces come from mapgen2.py (map_*.jpg).
Destination: equilateral triangle in a square texture, apex top-centre, base at the bottom.
Regions are emitted as barycentric coords (apex, bl, br) of their face triangle.
"""
import json, math
import numpy as np
import cv2
from radial import radial_warp, warp_point, tri_layout

ART = 'art_latest.png'
A = (733.0, 2.0); L = (18.0, 857.0); R = (1428.0, 857.0); D = (704.0, 1068.0)
P = (281.0, 542.0); Q = (1174.0, 545.0)

def affine_warp(img, src3, dst3, S):
    M = cv2.getAffineTransform(np.float32(src3), np.float32(dst3))
    return cv2.warpAffine(img, M, (S, S), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT), M

def bary(p, a, b, c):
    (x, y), (x1, y1), (x2, y2), (x3, y3) = p, a, b, c
    det = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
    l1 = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / det
    l2 = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / det
    return (l1, l2, 1 - l1 - l2)

img = cv2.imread(ART)
H, W = img.shape[:2]
assert (W, H) == (1448, 1086), (W, H)

# ---- Canon face (kite -> triangle, radial) ----
S0 = 1024
apex0, bl0, br0 = tri_layout(S0)
ct0 = ((apex0[0] + bl0[0] + br0[0]) / 3, (apex0[1] + bl0[1] + br0[1]) / 3)
ck = (727.0, 530.0)
canon, (thetas, ratio) = radial_warp(img, [A, Q, D, P], ck, [apex0, bl0, br0], ct0, S0, smooth_deg=4.0)
cv2.imwrite('tex_canon.jpg', canon, [cv2.IMWRITE_JPEG_QUALITY, 88])

# ---- Western / Southern / Far: procedural 'unwritten' faces (tinted) ----
S1 = 1024
apex1, bl1, br1 = tri_layout(S1)

def unwritten(seed, tint_bgr):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:S1, 0:S1].astype(np.float32) / S1
    stone = np.zeros((S1, S1, 3), np.float32)          # BGR
    stone[..., 0] = 0.11 + 0.05 * y
    stone[..., 1] = 0.10 + 0.03 * y
    stone[..., 2] = 0.10 + 0.02 * x
    noise = np.zeros((S1, S1), np.float32)
    for octave, amp in [(6, 0.5), (12, 0.25), (24, 0.125), (48, 0.0625), (96, 0.03)]:
        noise += amp * cv2.resize(rng.random((octave, octave), dtype=np.float32), (S1, S1), interpolation=cv2.INTER_CUBIC)
    noise = (noise - noise.min()) / (noise.max() - noise.min())
    stone += noise[..., None] * np.array([0.09, 0.08, 0.07], np.float32)
    levels = np.abs(((noise * 16) % 1.0) - 0.5)
    contour = np.clip(1.0 - levels / 0.05, 0, 1) ** 2
    stone += contour[..., None] * np.array([0.16, 0.15, 0.13], np.float32) * 0.55
    grid = ((np.abs((x * 12) % 1.0 - 0.5) > 0.494) | (np.abs((y * 12) % 1.0 - 0.5) > 0.494)).astype(np.float32)
    stone += grid[..., None] * np.array([0.07, 0.065, 0.06], np.float32)
    flecks = (rng.random((S1, S1), dtype=np.float32) > 0.9996).astype(np.float32)
    stone += cv2.GaussianBlur(flecks, (0, 0), 1.3)[..., None] * np.array([0.8, 0.85, 0.95], np.float32) * 1.2
    stone *= np.array(tint_bgr, np.float32)
    return np.clip(stone * 255, 0, 255).astype(np.uint8)

cv2.imwrite('tex_west.jpg', unwritten(11, (0.90, 1.0, 1.18)), [cv2.IMWRITE_JPEG_QUALITY, 85])   # warm, sunward
cv2.imwrite('tex_south.jpg', unwritten(23, (1.22, 1.02, 0.90)), [cv2.IMWRITE_JPEG_QUALITY, 85])  # cool, far side
cv2.imwrite('tex_far.jpg', unwritten(7, (1.0, 1.0, 1.0)), [cv2.IMWRITE_JPEG_QUALITY, 85])        # neutral base
S3 = S1

# ---- Regions -> destination pixel -> barycentric in (apex, bl, br) ----
regions = [
    ('whiteland', 'Whiteland', 'canon', (440, 470)),
    ('yolkia', 'Yolkia', 'canon', (560, 478)),
    ('islandia', 'Islandia', 'canon', (727, 492)),
    ('headlands', 'The Headlands', 'canon', (912, 332)),
    ('neckia', 'Neckia', 'canon', (905, 428)),
    ('feathers', 'The Feathers', 'canon', (955, 524)),
    ('llamaland', 'Llamaland', 'canon', (1050, 522)),
    ('footia', 'Footia', 'canon', (985, 604)),
    ('spikia-canon', 'Spikia \u00b7 the spike', 'canon', (735, 150)),
    ('unoooland', 'Uncooland', 'canon', (540, 730)),
    ('hotland', "It's Hot", 'canon', (790, 665)),
    ('rainia', 'Rainia', 'canon', (860, 745)),
    ('uohia', 'Ughia', 'canon', (970, 700)),
]
def apply_affine(M, p):
    return (M[0, 0] * p[0] + M[0, 1] * p[1] + M[0, 2], M[1, 0] * p[0] + M[1, 1] * p[1] + M[1, 2])

geo = []
for rid, name, face, p in regions:
    q = warp_point(p, ck, ct0, thetas, ratio); tri = (apex0, bl0, br0)
    b = bary(q, *tri)
    assert all(-0.01 <= v <= 1.01 for v in b), (name, b)
    geo.append(dict(id=rid, name=name, face=face, b=[round(v, 4) for v in b]))
    print(f'{name:14s} {face:6s} dest={tuple(round(v) for v in q)} bary={tuple(round(v,3) for v in b)}')

layout = {k: dict(size=s, apex=[a[0] / s, a[1] / s], bl=[b[0] / s, b[1] / s], br=[c[0] / s, c[1] / s])
          for k, (s, (a, b, c)) in {'canon': (S0, (apex0, bl0, br0)), 'west': (S1, (apex1, bl1, br1)),
                                     'south': (S1, (apex1, bl1, br1)), 'far': (S3, (apex1, bl1, br1))}.items()}
json.dump(dict(layout=layout, regions=geo), open('geometry.json', 'w'), indent=1)
print(json.dumps(layout['canon']), json.dumps(layout['west']))
