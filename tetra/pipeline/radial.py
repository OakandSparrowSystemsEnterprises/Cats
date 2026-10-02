"""Radial (star-shaped) warp of the kite A,P,D,Q into the destination triangle."""
import math, json
import numpy as np
import cv2

A = (733.0, 2.0); L = (18.0, 857.0); R = (1428.0, 857.0); D = (704.0, 1068.0)
P = (281.0, 542.0); Q = (1174.0, 545.0)

def tri_layout(S, margin=8):
    w = S - 2 * margin
    h = w * math.sqrt(3) / 2
    m = (S - h) / 2
    return (S / 2, m), (margin, S - m), (S - margin, S - m)

def ray_poly_dist(c, poly, thetas):
    """distance from centre c to the polygon boundary along each angle (poly convex, CCW or CW)."""
    cx, cy = c
    out = np.full_like(thetas, np.inf)
    n = len(poly)
    dx, dy = np.cos(thetas), np.sin(thetas)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        ex, ey = x2 - x1, y2 - y1
        # solve c + t*d = p1 + s*e
        den = dx * ey - dy * ex
        with np.errstate(divide='ignore', invalid='ignore'):
            t = ((x1 - cx) * ey - (y1 - cy) * ex) / den
            s = ((x1 - cx) * dy - (y1 - cy) * dx) / den
        ok = (np.abs(den) > 1e-9) & (t > 0) & (s >= -1e-6) & (s <= 1 + 1e-6)
        out = np.where(ok, np.minimum(out, t), out)
    return out

def radial_warp(img, kite, ck, tri, ct, S, smooth_deg=4.0):
    """Build remap so that dest triangle <- source kite via angle-matched radial scaling.
    Radius ratio r_k(theta)/r_t(theta) is smoothed angularly to soften creases."""
    nT = 3600
    thetas = np.linspace(-math.pi, math.pi, nT, endpoint=False)
    rk = ray_poly_dist(ck, kite, thetas)
    rt = ray_poly_dist(ct, tri, thetas)
    ratio = rk / rt
    if smooth_deg > 0:
        k = int(smooth_deg / 360 * nT)
        ker = np.exp(-0.5 * (np.arange(-3 * k, 3 * k + 1) / k) ** 2); ker /= ker.sum()
        ratio = np.convolve(np.concatenate([ratio[-3 * k:], ratio, ratio[:3 * k]]), ker, mode='same')[3 * k:-3 * k]
    ys, xs = np.mgrid[0:S, 0:S].astype(np.float32)
    dxp = xs - ct[0]; dyp = ys - ct[1]
    ang = np.arctan2(dyp, dxp)
    idx = ((ang + math.pi) / (2 * math.pi) * nT).astype(int) % nT
    rr = ratio[idx].astype(np.float32)
    mapx = (ck[0] + dxp * rr).astype(np.float32)
    mapy = (ck[1] + dyp * rr).astype(np.float32)
    return cv2.remap(img, mapx, mapy, interpolation=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT), (thetas, ratio)

def warp_point(p, ck, ct, thetas, ratio):
    """map a source point (art px) to dest px using the same radial map (inverse of remap direction)."""
    dx, dy = p[0] - ck[0], p[1] - ck[1]
    ang = math.atan2(dy, dx)
    i = int(round((ang + math.pi) / (2 * math.pi) * len(thetas))) % len(thetas)
    r = ratio[i]
    return (ct[0] + dx / r, ct[1] + dy / r)

if __name__ == '__main__':
    img = cv2.imread('art_latest.png')
    S = 1280
    apex, bl, br = tri_layout(S)
    tri = [apex, bl, br]
    ct = ((apex[0] + bl[0] + br[0]) / 3, (apex[1] + bl[1] + br[1]) / 3)
    ck = (727.0, 530.0)
    kite = [A, Q, D, P]
    out, (thetas, ratio) = radial_warp(img, kite, ck, tri, ct, S)
    cv2.imwrite('tex_canon_radial.jpg', out, [cv2.IMWRITE_JPEG_QUALITY, 88])
    # draw triangle + region points for inspection
    dbg = out.copy()
    cv2.polylines(dbg, [np.int32([apex, bl, br])], True, (0, 255, 0), 2)
    regions = {'Whiteland': (440, 470), 'Yolkia': (560, 478), 'Islandia': (727, 492), 'Headlands': (912, 332),
               'Neckia': (905, 428), 'Feathers': (955, 524), 'Llamaland': (1050, 522), 'Footia': (985, 604)}
    for n, p in regions.items():
        q = warp_point(p, ck, ct, thetas, ratio)
        cv2.circle(dbg, (int(q[0]), int(q[1])), 8, (0, 255, 255), 2)
        cv2.putText(dbg, n, (int(q[0]) + 10, int(q[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.imwrite('tex_canon_radial_dbg.png', cv2.resize(dbg, (800, 800)))
    print('centroid', ct, 'kite centre', ck)
