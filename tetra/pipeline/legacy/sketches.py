"""Process Sapphire's two sketches: the West-face chart (onto the face texture) and the island kingdoms (Codex drawing)."""
import math, json
import numpy as np, cv2
from PIL import Image
from bake import unwritten, tri_layout, bary   # reuses the stone generator and layout

def flatten_ink(path, boost=3.0, sigma=40):
    img = cv2.imread(path)
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    bg = cv2.GaussianBlur(g, (0, 0), sigma)
    flat = g / np.maximum(bg, 1)
    ink = np.clip((1.0 - flat) * boost, 0, 1)
    return img, ink

def remove_ruled_lines(ink, min_len=220, tol_deg=9.0, thickness=11, exclude_dark=None):
    """Find the dominant long-line angle (the paper's ruling) and paint those lines out."""
    binm = (ink > 0.35).astype(np.uint8) * 255
    lines = cv2.HoughLinesP(binm, 1, np.pi / 360, threshold=90, minLineLength=min_len, maxLineGap=18)
    if lines is None:
        return ink, 0
    angs = []
    for x1, y1, x2, y2 in lines[:, 0]:
        a = math.degrees(math.atan2(y2 - y1, x2 - x1)) % 180
        angs.append(a)
    hist = np.histogram(angs, bins=36, range=(0, 180))[0]
    dom = (np.argmax(hist) + 0.5) * 5
    mask = np.zeros(ink.shape, np.uint8)
    n = 0
    for x1, y1, x2, y2 in lines[:, 0]:
        a = math.degrees(math.atan2(y2 - y1, x2 - x1)) % 180
        d = min(abs(a - dom), 180 - abs(a - dom))
        if d <= tol_deg:
            cv2.line(mask, (int(x1), int(y1)), (int(x2), int(y2)), 255, thickness)
            n += 1
    if exclude_dark is not None:
        mask[exclude_dark] = 0          # never erase the marker strokes
    out = ink.copy(); out[mask > 0] = 0
    return out, n

# ---------------- West face chart ----------------
img, ink = flatten_ink('west_sketch.jpg', boost=3.0)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
paper = (cv2.GaussianBlur(gray, (0, 0), 60) > 78).astype(np.uint8)
paper = cv2.erode(paper, np.ones((15, 15), np.uint8)) > 0
ink = ink * paper
b, g, r = [img[..., i].astype(np.float32) for i in range(3)]
blue_strict = ((b > 165) & (b - r > 75) & (g > 110) & (ink > 0.25)).astype(np.float32)
black = ((img.max(axis=2) < 95) & (ink > 0.5)).astype(np.float32)
darkmask = cv2.dilate((black > 0).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
ink_clean, n = remove_ruled_lines(ink, exclude_dark=darkmask)
print('ruled lines removed:', n)
blue = blue_strict * (ink_clean > 0.1)
blue = cv2.dilate(blue, np.ones((3, 3), np.uint8))
pencil = np.clip(ink_clean - black - blue, 0, 1)
pencil = cv2.GaussianBlur(pencil, (0, 0), 0.8)
# soften scattered noise
pencil[pencil < 0.18] = 0
blue = cv2.GaussianBlur(blue, (0, 0), 1.0)
black = cv2.GaussianBlur(black, (0, 0), 0.8)

A_s = (815.0, 345.0); L_s = (195.0, 1000.0); R_s = (955.0, 1050.0)
S = 1024
apex, bl, br = tri_layout(S)
M = cv2.getAffineTransform(np.float32([A_s, L_s, R_s]), np.float32([apex, bl, br]))
def warp(layer):
    return cv2.warpAffine(layer, M, (S, S), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
wp, wk, wb = warp(pencil), warp(black), warp(blue)
base = unwritten(11, (0.90, 1.0, 1.18)).astype(np.float32) / 255.0   # BGR warm stone
def over(dst, alpha, color_bgr):
    a = np.clip(alpha, 0, 1)[..., None]
    return dst * (1 - a) + np.array(color_bgr, np.float32) * a
tex = over(base, wp * 0.85, (0.62, 0.70, 0.80))     # pencil: pale parchment
tex = over(tex, wk * 0.95, (0.80, 0.90, 0.98))      # marker: bright parchment
tex = over(tex, wb * 0.95, (1.00, 0.62, 0.30))      # Sapphire's blue (BGR)
cv2.imwrite('tex_west.jpg', np.clip(tex * 255, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 88])

# place points (sketch px) -> barycentric on the face
places = {
    'spike': (812, 410), 'swamp': (470, 800), 'delta': (285, 955), 'tropical': (830, 985), 'island': (690, 770), 'tropicia': (755, 905),
}
out = {}
for k, p in places.items():
    bb = bary(p, A_s, L_s, R_s)
    assert all(-0.02 <= v <= 1.02 for v in bb), (k, bb)
    out[k] = [round(v, 4) for v in bb]
    print(k, out[k])
json.dump(out, open('west_places.json', 'w'))

# preview of the west texture with the triangle
prev = cv2.imread('tex_west.jpg')
cv2.polylines(prev, [np.int32([apex, bl, br])], True, (0, 255, 0), 1)
for k, bb in out.items():
    q = (bb[0] * apex[0] + bb[1] * bl[0] + bb[2] * br[0], bb[0] * apex[1] + bb[1] * bl[1] + bb[2] * br[1])
    cv2.circle(prev, (int(q[0]), int(q[1])), 7, (0, 255, 255), 2); cv2.putText(prev, k, (int(q[0]) + 9, int(q[1]) + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
cv2.imwrite('west_preview.png', cv2.resize(prev, (700, 700)))

# full chart (with labels) for the Codex: transparent ink PNG, cropped to the drawing
full = np.clip(pencil * 0.9 + black + blue, 0, 1)
rgba = np.zeros((*full.shape, 4), np.uint8)
rgba[..., 0] = 242; rgba[..., 1] = 232; rgba[..., 2] = 211
# blue strokes keep their colour
bl_a = np.clip(blue, 0, 1)
rgba[..., 0] = (242 * (1 - bl_a) + 90 * bl_a).astype(np.uint8)
rgba[..., 1] = (232 * (1 - bl_a) + 165 * bl_a).astype(np.uint8)
rgba[..., 2] = (211 * (1 - bl_a) + 255 * bl_a).astype(np.uint8)
rgba[..., 3] = (full * 255).astype(np.uint8)
rgba[:12, :] = 0; rgba[:, :30] = 0; rgba[:, -20:] = 0   # photo edges
im = Image.fromarray(rgba, 'RGBA')
im = im.resize((420, int(im.height * 420 / im.width)), Image.LANCZOS)
im.quantize(colors=32, method=Image.Quantize.FASTOCTREE).save('west_chart.png', optimize=True)

# ---------------- Island kingdoms sketch ----------------
img2, ink2 = flatten_ink('island_sketch.jpg', boost=3.2, sigma=45)
black2 = ((img2.max(axis=2) < 80) & (ink2 > 0.5)).astype(np.float32)
dark2 = cv2.dilate((black2 > 0).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
ink2c, n2 = remove_ruled_lines(ink2, min_len=300, tol_deg=6.0, thickness=13, exclude_dark=dark2)
print('island ruled lines removed:', n2)
ink2c = cv2.GaussianBlur(ink2c, (0, 0), 0.8); ink2c[ink2c < 0.16] = 0
ink2c[860:, :430] = 0                      # the crossed-out scribble, bottom-left
ink2c[:, :60] = 0; ink2c[:, -30:] = 0; ink2c[:30, :] = 0; ink2c[-30:, :] = 0
rgba2 = np.zeros((*ink2c.shape, 4), np.uint8)
rgba2[..., 0] = 242; rgba2[..., 1] = 232; rgba2[..., 2] = 211; rgba2[..., 3] = (np.clip(ink2c * 1.1, 0, 1) * 255).astype(np.uint8)
ys, xs = np.where(rgba2[..., 3] > 40); x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
im2 = Image.fromarray(rgba2[y0:y1 + 1, x0:x1 + 1], 'RGBA')
im2 = im2.resize((480, int(im2.height * 480 / im2.width)), Image.LANCZOS)
im2.quantize(colors=24, method=Image.Quantize.FASTOCTREE).save('island_chart.png', optimize=True)
import os
print('sizes', os.path.getsize('west_chart.png'), os.path.getsize('island_chart.png'))
for nme in ['west_chart.png', 'island_chart.png']:
    a = Image.open(nme).convert('RGBA'); p = Image.new('RGB', a.size, (8, 11, 20)); p.paste(a, (0, 0), a); p.save(nme.replace('.png', '_prev.png'))
