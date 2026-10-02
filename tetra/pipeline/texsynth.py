"""Paint a face from the Canon art itself: harvest label-free, glow-free patches of each terrain class from
art_latest.png, then lay them over a face by class so the side faces carry the same painted detail as the Canon Face."""
import numpy as np, cv2

ART = 'art_latest.png'
PATCH = 80
STRIDE = 10
CELL = 52           # spacing of patch centres in the target
FEATHER = 16

LABELS = [  # text and chrome in the art (x0,y0,x1,y1); patches never touch these
    (390, 452, 490, 488), (522, 458, 596, 490), (682, 465, 774, 503), (874, 300, 960, 355), (884, 405, 950, 437),
    (924, 495, 1000, 550), (1010, 508, 1100, 540), (950, 586, 1020, 620),
    (170, 715, 270, 745), (340, 803, 410, 833), (235, 863, 335, 893), (465, 923, 550, 951),
    (1160, 725, 1250, 753), (970, 818, 1055, 848), (1090, 818, 1170, 848), (950, 917, 1035, 945),
    (0, 0, 460, 245), (990, 0, 1448, 205), (1215, 205, 1448, 495), (0, 470, 230, 610), (320, 120, 510, 250), (980, 130, 1160, 310),
    (0, 900, 300, 1086), (1080, 900, 1448, 1086), (1220, 940, 1448, 1086),
]
MAP_POLY = np.int32([(733, 2), (18, 857), (704, 1068), (1428, 857)])

CLASSES = ('sea', 'coast', 'white', 'gold', 'redrock', 'green', 'forest', 'plains', 'mountain', 'cliff')
PSIZE = {'sea': 48, 'white': 56, 'redrock': 56, 'mountain': 56}

def harvest():
    img = cv2.cvtColor(cv2.imread(ART), cv2.COLOR_BGR2RGB)
    H, W = img.shape[:2]
    f = img.astype(np.float32); r, g, b = f[..., 0], f[..., 1], f[..., 2]
    v = f.max(2); mn = f.min(2); sat = (v - mn) / (v + 1e-3)
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB).astype(np.float32)
    water = (b > r + 35) & (b > 100) & (b >= g - 15)
    # the field lines and the clouds that ride them: a corridor around the four known glow lines (art coords),
    # plus any thin bright streak (the blue arcs)
    glow = np.zeros((H, W), np.uint8)
    for a_, b_, wd in [((733, 2), (18, 857), 64), ((733, 2), (1428, 857), 64), ((281, 542), (704, 1068), 120), ((1174, 545), (704, 1068), 120)]:
        cv2.line(glow, a_, b_, 1, wd)
    bright = (((r > 225) & (g > 140) & (b < 185) & (r > b + 55)) | ((b > 215) & (r < 190) & (b > g + 15))).astype(np.uint8)
    bright = cv2.dilate(bright, np.ones((3, 3), np.uint8))
    n, lab_, stats, _ = cv2.connectedComponentsWithStats(bright, 8)
    dt = cv2.distanceTransform(bright, cv2.DIST_L2, 5)
    for i in range(1, n):
        x0, y0, w0, h0 = stats[i, cv2.CC_STAT_LEFT], stats[i, cv2.CC_STAT_TOP], stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT]
        if max(w0, h0) < 90: continue
        comp = lab_[y0:y0 + h0, x0:x0 + w0] == i
        if dt[y0:y0 + h0, x0:x0 + w0][comp].max() <= 11:
            sub = glow[y0:y0 + h0, x0:x0 + w0]; sub[comp] = 1
    glow = cv2.dilate(glow, np.ones((13, 13), np.uint8)) > 0
    cloud = (mn > 190) & (sat < 0.12)
    dk = (v < 30).astype(np.uint8)
    nd, ld, sd, _ = cv2.connectedComponentsWithStats(dk, 8)
    chasm = np.zeros((H, W), np.uint8)
    for i in range(1, nd):
        if sd[i, cv2.CC_STAT_AREA] >= 90 or sd[i, cv2.CC_STAT_HEIGHT] >= 28 or sd[i, cv2.CC_STAT_WIDTH] >= 28: chasm[ld == i] = 1
    chasm = cv2.dilate(chasm, np.ones((5, 5), np.uint8))
    snowpx = (mn > 165) & (sat < 0.28)
    inside = np.zeros((H, W), np.uint8); cv2.fillPoly(inside, [MAP_POLY], 1)
    inside_edge = inside.copy()
    inside = cv2.erode(inside, np.ones((21, 21), np.uint8))
    for (x0, y0, x1, y1) in LABELS: inside[y0:y1, x0:x1] = 0; inside_edge[y0:y1, x0:x1] = 0
    I = {k: cv2.integral(m.astype(np.uint8)) for k, m in dict(water=water, glow=glow, cloud=cloud, inside=inside, inside_edge=inside_edge, chasm=chasm, snowpx=snowpx).items()}
    IL = [cv2.integral(lab[..., i]) for i in range(3)]
    def frac(k, x, y, P=PATCH):
        M = I[k]; return (M[y + P, x + P] - M[y, x + P] - M[y + P, x] + M[y, x]) / (P * P)
    def labmean(x, y, P=PATCH):
        return [(M[y + P, x + P] - M[y, x + P] - M[y + P, x] + M[y, x]) / (P * P) for M in IL]
    pools = {k: [] for k in CLASSES}
    SP = 48
    for y in range(0, H - SP, 8):
        for x in range(0, W - SP, 8):
            if frac('inside', x, y, SP) < 0.999 or frac('glow', x, y, SP) > 0 or frac('water', x, y, SP) < 0.995: continue
            pools['sea'].append((x, y))
    for y in range(0, H - PATCH, STRIDE):
        for x in range(0, W - PATCH, STRIDE):
            if frac('inside', x, y) < 0.999 or frac('glow', x, y) > 0 or frac('chasm', x, y) > 0: continue
            fw = frac('water', x, y); fc = frac('cloud', x, y); fs = frac('snowpx', x, y)
            if 0.4 <= fw < 0.85: pools['coast'].append((x, y)); continue
            if fw > 0.08: continue
            L, a, bb = labmean(x, y); a -= 128; bb -= 128
            if bb > 26 and a > 6 and L > 110: pools['gold'].append((x, y))
            elif a < 5 and 8 < bb < 32 and 100 < L < 140: pools['green'].append((x, y))
            elif L <= 108: pools['forest'].append((x, y))
            elif fs > 0.1 and L > 158: continue
            else: pools['plains'].append((x, y))
    SP2 = 56
    for y in range(0, H - SP2, 6):
        for x in range(0, W - SP2, 6):
            if frac('inside', x, y, SP2) < 0.999 or frac('glow', x, y, SP2) > 0 or frac('chasm', x, y, SP2) > 0: continue
            fw = frac('water', x, y, SP2); fs = frac('snowpx', x, y, SP2)
            if fw > 0.06: continue
            L, a, bb = labmean(x, y, SP2); a -= 128; bb -= 128
            if L > 140 and fs > 0.18: pools['white'].append((x, y))
            elif a > 7 and 8 < bb <= 27 and 118 < L < 165 and fs < 0.25: pools['redrock'].append((x, y))
            elif fs > 0.1 and 118 < L <= 158 and a > 2: pools['mountain'].append((x, y))
    pools['mountain'] = [w for w in pools['mountain'] if True]
    # the world's-edge cliffs: dark rock windows hugging the rim of the map
    def seg_dist(px, py, a_, b_):
        ax, ay = a_; bx, by = b_; t = max(0, min(1, ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2)))
        return np.hypot(px - (ax + t * (bx - ax)), py - (ay + t * (by - ay)))
    rim = [((18, 857), (704, 1068)), ((704, 1068), (1428, 857)), ((281, 542), (704, 1068)), ((1174, 545), (704, 1068))]
    dark_i = cv2.integral(((mn < 120) & (sat < 0.35)).astype(np.uint8))
    for y in range(0, H - PATCH, STRIDE):
        for x in range(0, W - PATCH, STRIDE):
            cx, cy = x + PATCH / 2, y + PATCH / 2
            if min(seg_dist(cx, cy, a_, b_) for a_, b_ in rim) > 55: continue
            if frac('inside_edge', x, y) < 0.45 or frac('glow', x, y) > 0 or frac('water', x, y) > 0.15: continue
            fd = (dark_i[y + PATCH, x + PATCH] - dark_i[y, x + PATCH] - dark_i[y + PATCH, x] + dark_i[y, x]) / (PATCH * PATCH)
            if fd >= 0.2: pools['cliff'].append((x, y))
    dry = {}
    for c, pool in pools.items():
        Pc = PSIZE.get(c, PATCH)
        ranked = sorted(pool, key=lambda w: frac('water', w[0], w[1], Pc))
        dry[c] = ranked[:max(8, len(ranked) // 4)]
    pools['_dry'] = dry
    return img, pools

def feather_mask(P=PATCH, F=FEATHER):
    ramp = np.minimum(np.arange(P) + 1, P - np.arange(P)).astype(np.float32)
    ramp = np.clip(ramp / F, 0, 1)
    return np.minimum.outer(ramp, ramp)

def synth_class(img, pool, S, rng, cell=CELL, P=PATCH):
    acc = np.zeros((S, S, 3), np.float32); wsum = np.zeros((S, S), np.float32)
    fm = feather_mask(P, max(6, P // 5))
    if not pool: return acc, wsum
    half = P // 2
    cell = min(cell, P // 2)          # neighbours overlap by at least P/4 even after jitter
    jit = max(1, P // 8)
    for cy in range(-cell, S + cell, cell):
        for cx in range(-cell, S + cell, cell):
            jx, jy = rng.integers(-jit, jit + 1, 2)
            x0, y0 = cx + jx - half, cy + jy - half
            px, py = pool[rng.integers(len(pool))]
            patch = img[py:py + P, px:px + P].astype(np.float32)
            if rng.random() < 0.5: patch = patch[:, ::-1]
            xa, ya = max(0, x0), max(0, y0); xb, yb = min(S, x0 + P), min(S, y0 + P)
            if xb <= xa or yb <= ya: continue
            sub = patch[ya - y0:yb - y0, xa - x0:xb - x0]; w = fm[ya - y0:yb - y0, xa - x0:xb - x0]
            acc[ya:yb, xa:xb] += sub * w[..., None]; wsum[ya:yb, xa:xb] += w
    return acc, wsum

_pools = None
def get_pools():
    global _pools
    if _pools is None:
        _pools = harvest()
        print('patch pools:', {k: len(v) for k, v in _pools[1].items() if k != '_dry'}, 'dry:', {k: len(v) for k, v in _pools[1]['_dry'].items()})
    return _pools

SEA_GAIN = np.array([1.35, 1.22, 1.12], np.float32); SEA_LIFT = np.array([30.0, 18.0, 12.0], np.float32)
FALLBACK = {'white': 'mountain', 'redrock': 'gold', 'plains': 'green', 'mountain': 'forest', 'green': 'plains'}

_means = {}
def class_mean(img, pools, src):
    """mean colour of a class's patches (after the sea lift), cached"""
    if src not in _means:
        Pc = PSIZE.get(src, PATCH); acc = np.zeros(3, np.float64); n = 0
        for (x, y) in pools[src][:400]:
            patch = img[y:y + Pc, x:x + Pc].astype(np.float32)
            if src in ('sea', 'coast'): patch = np.clip(patch * SEA_GAIN + SEA_LIFT, 0, 255)
            acc += patch.reshape(-1, 3).mean(0); n += 1
        _means[src] = (acc / max(n, 1)).astype(np.float32)
    return _means[src]

def paint(weights, S, seed, P=PATCH, cell=None, feather=FEATHER, dry_mask=None, normalize=0.35):
    """Winner-take-all patch quilting: at every grid cell one class is drawn from the local weights and one of its
    patches is pasted, so regions stay crisp (no averaging of textures) and only patch borders blend."""
    img, pools = get_pools()
    rng = np.random.default_rng(seed)
    dry = pools['_dry']
    names = [c for c in weights if (pools.get(c) or pools.get(FALLBACK.get(c, ''), []))]
    Wt = np.stack([np.clip(weights[c], 0, 1).astype(np.float32) for c in names], 0)
    cell = cell or P // 2
    jit = max(1, P // 8); half = P // 2
    fm = feather_mask(P, feather)
    acc = np.zeros((S, S, 3), np.float32); wsum = np.zeros((S, S), np.float32)
    for cy in range(-cell, S + cell, cell):
        for cx in range(-cell, S + cell, cell):
            jx, jy = rng.integers(-jit, jit + 1, 2)
            sx, sy = int(np.clip(cx + jx, 0, S - 1)), int(np.clip(cy + jy, 0, S - 1))
            wv = Wt[:, sy, sx]
            if wv.sum() <= 1e-6: continue
            pr = wv / wv.sum()
            c = names[rng.choice(len(names), p=pr)]
            src = c if pools.get(c) else FALLBACK.get(c, c)
            pool = pools[src]; Pc = PSIZE.get(src, PATCH)
            if dry_mask is not None and dry_mask[sy, sx] and src not in ('sea', 'coast') and dry.get(src): pool = dry[src]
            px, py = pool[rng.integers(len(pool))]
            patch = img[py:py + Pc, px:px + Pc].astype(np.float32)
            if Pc != P: patch = cv2.resize(patch, (P, P), interpolation=cv2.INTER_CUBIC)
            if rng.random() < 0.5: patch = patch[:, ::-1]
            if c == 'white' and src != 'white': patch = patch * 0.78 + 255 * 0.30
            if src in ('sea', 'coast'):   # the pure-water windows come from the art's darkest sea; lift them to its overall water colour
                patch = np.clip(patch * SEA_GAIN + SEA_LIFT, 0, 255)
            # pull each patch's mean toward its class mean so neighbouring patches don't meet along a visible step
            k = 1.0 if src == 'sea' else normalize
            if k > 0:
                patch = np.clip(patch + k * (class_mean(img, pools, src) - patch.reshape(-1, 3).mean(0)), 0, 255)
            x0, y0 = cx + jx - half, cy + jy - half
            xa, ya = max(0, x0), max(0, y0); xb, yb = min(S, x0 + P), min(S, y0 + P)
            if xb <= xa or yb <= ya: continue
            sub = patch[ya - y0:yb - y0, xa - x0:xb - x0]; w = fm[ya - y0:yb - y0, xa - x0:xb - x0]
            acc[ya:yb, xa:xb] += sub * w[..., None]; wsum[ya:yb, xa:xb] += w
    hole = wsum < 1e-3
    if hole.any():
        accb = cv2.GaussianBlur(acc, (0, 0), 12); wsb = cv2.GaussianBlur(wsum, (0, 0), 12)
        acc[hole] = accb[hole]; wsum[hole] = np.maximum(wsb[hole], 1e-3)
    return acc / np.maximum(wsum, 1e-3)[..., None] / 255.0

if __name__ == '__main__':
    img, pools = harvest()
    print({k: len(v) for k, v in pools.items()})
    rows = []
    for name, pool in pools.items():
        rng = np.random.default_rng(1); row = []
        Pc = PSIZE.get(name, PATCH)
        for i in range(min(10, len(pool))):
            x, y = pool[rng.integers(len(pool))]; row.append(cv2.resize(img[y:y + Pc, x:x + Pc].copy(), (PATCH, PATCH)))
        while len(row) < 10: row.append(np.zeros((PATCH, PATCH, 3), np.uint8))
        strip = np.concatenate(row, 1); cv2.putText(strip, name, (4, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)
        rows.append(strip)
    cv2.imwrite('pools_sheet.png', cv2.cvtColor(np.concatenate(rows, 0), cv2.COLOR_RGB2BGR))
