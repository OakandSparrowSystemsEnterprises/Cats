"""Shared-edge land/water profiles, so a landmass that touches a face's edge continues onto the neighbouring face.

Tetrahedron: V0 apex (Spikia), V1, V2, V3 base (V3 = Wetia corner). Faces and their texture layout (apex, bl, br):
  canon (0,1,2)  west (0,3,1)  south (0,2,3)  far (1,3,2)
Every shared edge is keyed by its sorted vertex pair; t runs from the lower vertex id to the higher one.
The Canon bottom edge (1-2) is measured from Ruby's painting (tex_canon.jpg); the five other edges are designed here,
including the Canon side edges, which are open sea below Spikia since version 11."""
import json, os
import numpy as np, cv2

S = 1024
APEX, BL, BR = (512.0, 75.52), (8.0, 948.48), (1016.0, 948.48)
FACE_IDX = {'canon': (0, 1, 2), 'west': (0, 3, 1), 'south': (0, 2, 3), 'far': (1, 3, 2)}
LOCAL = {0: APEX, 1: BL, 2: BR}     # local corner slot -> texture position
N = 400
SPIKE_T = 0.25     # how far down the Canon side edges Spikia reaches (West wedge(305) and South wedge(275) sit at t 0.26 and 0.23)

def smooth(a, lo, hi):
    t = np.clip((a - lo) / (hi - lo), 0, 1); return t * t * (3 - 2 * t)

def measure_canon(path='tex_canon.jpg'):
    tex = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB).astype(np.float32)
    cx, cy = (APEX[0] + BL[0] + BR[0]) / 3, (APEX[1] + BL[1] + BR[1]) / 3
    def sample(a, b):
        ax, ay = a; bx, by = b; ex, ey = bx - ax, by - ay; L = np.hypot(ex, ey); nx, ny = -ey / L, ex / L
        if (cx - ax) * nx + (cy - ay) * ny < 0: nx, ny = -nx, -ny
        t = np.linspace(0, 1, N); rows = []
        for depth in (14, 18, 22, 26, 30):
            xs = ax + t * ex + nx * depth; ys = ay + t * ey + ny * depth
            px = tex[np.clip(ys.round().astype(int), 0, S - 1), np.clip(xs.round().astype(int), 0, S - 1)]
            r, g, b_ = px[:, 0], px[:, 1], px[:, 2]
            rows.append(((b_ > r + 30) & (b_ > 95) & (g > r + 8)).astype(np.float32))
        w = np.mean(rows, 0); k = 9
        w = np.convolve(np.pad(w, k // 2, mode='edge'), np.ones(k) / k, 'valid')
        b = (w > 0.5).astype(np.uint8)[None, :]
        # drop bays and headlands shorter than ~2.5% of the edge: too small to survive the painting anyway
        kk = np.ones((1, 7), np.uint8)
        b = cv2.morphologyEx(cv2.morphologyEx(b, cv2.MORPH_OPEN, kk), cv2.MORPH_CLOSE, kk)
        return b[0].astype(np.float32)
    # canon: apex=V0, bl=V1, br=V2 -> (0,1) apex->bl, (0,2) apex->br, (1,2) bl->br (all in canonical t direction)
    return {'0-1': sample(APEX, BL), '0-2': sample(APEX, BR), '1-2': sample(BL, BR)}

def designed(intervals):
    t = np.linspace(0, 1, N); w = np.zeros(N, np.float32)
    for a, b in intervals: w[(t >= a) & (t <= b)] = 1
    return w

PROFILE_FILE = 'edge_profiles.json'
def profiles():
    if os.path.exists(PROFILE_FILE):
        d = json.load(open(PROFILE_FILE)); return {k: np.array(v, np.float32) for k, v in d.items()}
    p = measure_canon()                            # 1-2, the Canon bottom edge, stays as Ruby painted it (the Far face already follows it)
    # Ruby (2026-10-03): the Canon face "shuld not have land on the west and east sides": open sea along both side edges,
    # from the foot of Spikia (t = SPIKE_T, matching the West and South spikes) down to the corners
    p['0-1'] = designed([(SPIKE_T, 1.0)])
    p['0-2'] = designed([(SPIKE_T, 1.0)])
    p['0-3'] = designed([(0.40, 0.60)])            # west left / south right: Spikia, a bay in the swamp coast, land down to Wetia
    p['1-3'] = designed([(0.28, 0.75)])            # west bottom / far left: land at both corners, open sea between
    p['2-3'] = designed([(0.10, 0.30), (0.54, 0.80)])            # south bottom / far bottom: Tree Land runs from the V2 corner to the middle and meets the southern continent; open sea; then Wetia
    json.dump({k: v.tolist() for k, v in p.items()}, open(PROFILE_FILE, 'w'))
    return p

def water_profile(edge_key, t):
    """water (1) / land (0) along the edge at parameter t, softened over ~1.5% of the edge"""
    w = profiles()[edge_key]
    k = 3; ws = np.convolve(np.pad(w, k // 2, mode='edge'), np.ones(k) / k, 'valid')
    return np.interp(t, np.linspace(0, 1, N), ws)

def face_edges(face):
    """the three edges of a face as (edge_key, texture point at t=0, texture point at t=1)"""
    idx = FACE_IDX[face]; out = []
    for i, j in ((0, 1), (0, 2), (1, 2)):
        va, vb = idx[i], idx[j]; pa, pb = LOCAL[i], LOCAL[j]
        if va > vb: va, vb, pa, pb = vb, va, pb, pa
        out.append((f'{va}-{vb}', pa, pb))
    return out

def transitions(edge_key):
    w = profiles()[edge_key]
    idx = np.where(w[1:] != w[:-1])[0]
    return (idx + 0.5) / (N - 1)

def conform(land, face, seed=5, base=58.0, vary=28.0):
    """Blend a soft land mask (S,S, 0..1) toward the shared-edge profiles inside a band along each edge.
    The band tapers to a sliver where the profile flips from land to water, so the strips end in rounded
    headlands and the bays have rounded heads instead of rectangular ones; its inner boundary wanders with noise."""
    from mapgen import fbm
    ys, xs = np.mgrid[0:S, 0:S].astype(np.float32)
    rng = np.random.default_rng(seed)
    out = land.astype(np.float32).copy()
    noise = (fbm(seed + 77, base=9, octaves=3) - 0.5) * 2.0
    for key, (ax, ay), (bx, by) in face_edges(face):
        ex, ey = bx - ax, by - ay; L2 = ex * ex + ey * ey
        t = np.clip(((xs - ax) * ex + (ys - ay) * ey) / L2, 0, 1)
        dist = np.abs(ey * xs - ex * ys + bx * ay - by * ax) / np.sqrt(L2)
        wat = water_profile(key, t)
        tr = transitions(key)
        dT = np.min(np.abs(t[..., None] - tr[None, None, :]), axis=2) if len(tr) else np.ones_like(t)
        taper = smooth(dT, 0.0, 0.065)
        wob = np.interp(t, np.linspace(0, 1, 24), rng.random(24))
        width = (base + vary * wob) * (0.56 + 0.44 * taper) + 14.0 * noise
        e = smooth(dist, width, width * 0.42)
        out = out * (1 - e) + (1 - wat) * e
    return out

if __name__ == '__main__':
    p = profiles()
    for k, v in p.items(): print(k, 'water frac', round(float(v.mean()), 3))
