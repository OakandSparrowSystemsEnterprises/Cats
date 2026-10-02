"""Verify that land and water agree along every shared edge of the world."""
import numpy as np, cv2
from PIL import Image, ImageDraw
from edges import face_edges, S

TEX = {'canon': 'tex_canon.jpg', 'west': 'map_west.jpg', 'south': 'map_south.jpg', 'far': 'map_far.jpg'}
APEX, BL, BR = (512.0, 75.52), (8.0, 948.48), (1016.0, 948.48)
cx, cy = (APEX[0] + BL[0] + BR[0]) / 3, (APEX[1] + BL[1] + BR[1]) / 3
N = 300

def sample(tex, a, b, depths=(14, 18, 22, 26, 30)):
    ax, ay = a; bx, by = b; ex, ey = bx - ax, by - ay; L = np.hypot(ex, ey); nx, ny = -ey / L, ex / L
    if (cx - ax) * nx + (cy - ay) * ny < 0: nx, ny = -nx, -ny
    t = np.linspace(0, 1, N); rows = []; cols = None
    for depth in depths:
        xs = ax + t * ex + nx * depth; ys = ay + t * ey + ny * depth
        px = tex[np.clip(ys.round().astype(int), 0, S - 1), np.clip(xs.round().astype(int), 0, S - 1)]
        if cols is None: cols = px
        r, g, b_ = px[:, 0], px[:, 1], px[:, 2]
        rows.append(((b_ > r + 30) & (b_ > 95) & (g > r + 8)).astype(np.float32))
    w = np.mean(rows, 0); k = 9
    w = np.convolve(np.pad(w, k // 2, mode='edge'), np.ones(k) / k, 'valid')
    return (w > 0.5), cols

texs = {f: cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB).astype(np.float32) for f, p in TEX.items()}
by_edge = {}
for face in TEX:
    for key, pa, pb in face_edges(face):
        by_edge.setdefault(key, []).append((face, *sample(texs[face], pa, pb)))
img = Image.new('RGB', (N * 2 + 160, len(by_edge) * 70), (0, 0, 0)); d = ImageDraw.Draw(img)
worst = 0
for i, (key, rows) in enumerate(sorted(by_edge.items())):
    (fa, wa, ca), (fb, wb, cb) = rows
    agree = float((wa == wb).mean()); worst = max(worst, 1 - agree)
    print(f'edge {key}: {fa:5s} vs {fb:5s}  agreement {agree*100:.1f}%')
    y0 = i * 70
    d.text((4, y0 + 4), f'{key} {fa}', fill=(255, 255, 0)); d.text((4, y0 + 36), fb, fill=(255, 255, 0))
    for j in range(N):
        d.line([(150 + j * 2, y0 + 4), (150 + j * 2, y0 + 30)], fill=tuple(int(v) for v in ca[j]))
        d.line([(150 + j * 2, y0 + 36), (150 + j * 2, y0 + 62)], fill=tuple(int(v) for v in cb[j]))
        if wa[j] != wb[j]: d.line([(150 + j * 2, y0 + 31), (150 + j * 2, y0 + 35)], fill=(255, 0, 0))
img.save('edge_check.png')
print('worst disagreement', round(worst * 100, 1), '%')
