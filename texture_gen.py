# ============================================================
#  RUN OR DONT IT - procedural texture factory
#  (c) 2026 Project Revision / Zarto's Studios. All rights reserved.
#
#  Generates real PNG textures on first launch using Panda3D's
#  PNMImage. No downloads, no binaries in the repo, no PIL needed.
#  Delete assets/textures/ to force regeneration.
#
#  First launch takes a few extra seconds - it is baking textures.
# ============================================================
import math
import os
import random

from panda3d.core import PNMImage, Filename

TEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'textures')


def _new(size):
    img = PNMImage(size, size)
    try:
        if img.get_num_channels() < 3:
            img.set_num_channels(3)
    except Exception:
        pass
    return img


def _write(name, buf):
    os.makedirs(TEX_DIR, exist_ok=True)
    S = len(buf)
    img = _new(S)
    for y in range(S):
        row = buf[y]
        for x in range(S):
            c = row[x]
            img.set_xel(x, y, c[0], c[1], c[2])
    path = os.path.join(TEX_DIR, name)
    img.write(Filename.fromOsSpecific(os.path.abspath(path)))
    print('  [tex]', name)


def _clamp(v):
    return 0.0 if v < 0.0 else (1.0 if v > 1.0 else v)


def _blank(S, base):
    return [[(base[0], base[1], base[2]) for _ in range(S)] for _ in range(S)]


def _noise(buf, S, rng, amt):
    for y in range(S):
        row = buf[y]
        for x in range(S):
            n = rng.uniform(-amt, amt)
            c = row[x]
            row[x] = (_clamp(c[0] + n), _clamp(c[1] + n), _clamp(c[2] + n))


def _blotches(buf, S, rng, count, rmin, rmax, darken=0.12):
    for _ in range(count):
        cx, cy = rng.randrange(S), rng.randrange(S)
        rad = rng.randint(rmin, rmax)
        for dy in range(-rad, rad + 1):
            for dx in range(-rad, rad + 1):
                if dx * dx + dy * dy <= rad * rad:
                    x, y = (cx + dx) % S, (cy + dy) % S
                    f = 1.0 - darken * (1.0 - (dx * dx + dy * dy) / float(rad * rad))
                    c = buf[y][x]
                    buf[y][x] = (_clamp(c[0] * f), _clamp(c[1] * f), _clamp(c[2] * f))


# ---------------- floors / grounds ----------------
def gen_floor_tile():
    S, rng, T = 128, random.Random(101), 16
    buf = [[None] * S for _ in range(S)]
    for y in range(S):
        ty, ry = divmod(y, T)
        for x in range(S):
            tx, rx = divmod(x, T)
            base = (0.58, 0.56, 0.53) if (tx + ty) % 2 == 0 else (0.30, 0.31, 0.35)
            n = rng.uniform(-0.03, 0.03)
            r, g, b = base[0] + n, base[1] + n, base[2] + n
            if rx < 1 or ry < 1:                       # grout
                r = g = b = 0.15 + rng.uniform(-0.02, 0.02)
            buf[y][x] = (_clamp(r), _clamp(g), _clamp(b))
    _noise(buf, S, rng, 0.015)
    _blotches(buf, S, rng, 14, 3, 10, 0.15)
    _write('floor_tile.png', buf)


def gen_concrete():
    S, rng = 128, random.Random(102)
    buf = _blank(S, (0.40, 0.40, 0.42))
    _noise(buf, S, rng, 0.045)
    _blotches(buf, S, rng, 18, 4, 16, 0.18)
    for _ in range(4):                                # cracks
        x, y = rng.randrange(S), rng.randrange(S)
        for _ in range(rng.randint(18, 40)):
            buf[y][x] = (0.20, 0.20, 0.22)
            x = (x + rng.randint(-1, 1)) % S
            y = (y + rng.randint(-1, 1)) % S
    _write('concrete.png', buf)


def gen_asphalt():
    S, rng = 128, random.Random(103)
    buf = _blank(S, (0.11, 0.11, 0.13))
    _noise(buf, S, rng, 0.030)
    for _ in range(220):                              # lighter aggregate specks
        x, y = rng.randrange(S), rng.randrange(S)
        c = buf[y][x]
        buf[y][x] = (_clamp(c[0] + 0.10), _clamp(c[1] + 0.10), _clamp(c[2] + 0.12))
    _blotches(buf, S, rng, 10, 5, 18, 0.22)           # oil stains
    _write('asphalt.png', buf)


# ---------------- walls ----------------
def gen_brick():
    S, rng = 128, random.Random(104)
    buf = _blank(S, (0.52, 0.50, 0.47))                # mortar
    BH, BW = 16, 32
    for row in range(S // BH):
        off = 0 if row % 2 == 0 else BW // 2
        for bx in range(-1, S // BW + 1):
            x0 = bx * BW + off
            jitter = rng.uniform(-0.08, 0.08)
            br, bg, bb = 0.42 + jitter, 0.19 + jitter * 0.5, 0.14 + jitter * 0.5
            for y in range(row * BH, row * BH + BH - 2):
                for x in range(x0, x0 + BW - 2):
                    if 0 <= x < S:
                        n = rng.uniform(-0.02, 0.02)
                        buf[y][x] = (_clamp(br + n), _clamp(bg + n), _clamp(bb + n))
    _blotches(buf, S, rng, 10, 3, 9, 0.15)
    _write('brick.png', buf)


def gen_wall_school():
    S, rng = 128, random.Random(105)
    buf = _blank(S, (0.60, 0.58, 0.55))                # painted upper wall
    T = 16
    for y in range(S - 44, S):                         # tile wainscot band
        ry = y - (S - 44)
        for x in range(S):
            base = (0.34, 0.38, 0.44)
            n = rng.uniform(-0.03, 0.03)
            r, g, b = base[0] + n, base[1] + n, base[2] + n
            if ry % T < 1 or x % T < 1:
                r = g = b = 0.16
            buf[y][x] = (_clamp(r), _clamp(g), _clamp(b))
    for y in range(S - 6, S):                          # baseboard
        for x in range(S):
            buf[y][x] = (0.14, 0.13, 0.12)
    _noise(buf, S, rng, 0.018)
    for _ in range(10):                                # grime streaks near floor
        x = rng.randrange(S)
        for y in range(S - 30, S):
            if rng.random() < 0.7:
                c = buf[y][x]
                buf[y][x] = (c[0] * 0.9, c[1] * 0.9, c[2] * 0.9)
    _write('wall_school.png', buf)


# ---------------- surfaces / props ----------------
def gen_wood():
    S, rng = 128, random.Random(106)
    buf = [[None] * S for _ in range(S)]
    PW = 32
    for plank in range(S // PW):
        j = rng.uniform(-0.05, 0.05)
        base = (0.42 + j, 0.28 + j * 0.6, 0.16 + j * 0.4)
        phase = rng.uniform(0, 6.28)
        for y in range(S):
            grain = 0.06 * math.sin(y * 0.25 + phase) + 0.03 * math.sin(y * 0.9 + phase * 2)
            for x in range(plank * PW, plank * PW + PW):
                n = rng.uniform(-0.02, 0.02)
                if x - plank * PW < 1:                 # plank gap
                    buf[y][x] = (0.10, 0.06, 0.04)
                else:
                    buf[y][x] = (_clamp(base[0] + grain + n),
                                 _clamp(base[1] + grain + n),
                                 _clamp(base[2] + grain + n))
    _blotches(buf, S, rng, 8, 3, 8, 0.12)
    _write('wood.png', buf)


def gen_metal():
    S, rng = 128, random.Random(107)
    buf = _blank(S, (0.52, 0.53, 0.56))
    for y in range(S):                                 # brushed streaks
        off = rng.uniform(-0.04, 0.04)
        for x in range(S):
            n = rng.uniform(-0.02, 0.02)
            buf[y][x] = (_clamp(0.52 + off + n), _clamp(0.53 + off + n), _clamp(0.56 + off + n))
    G = 32                                             # rivets
    for gy in range(0, S, G):
        for gx in range(0, S, G):
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    x, y = gx + 2 + dx, gy + 2 + dy
                    if 0 <= x < S and 0 <= y < S and dx * dx + dy * dy <= 4:
                        buf[y][x] = ((0.35 if dx < 0 else 0.62),
                                     (0.36 if dx < 0 else 0.63),
                                     (0.39 if dx < 0 else 0.66))
    _write('metal.png', buf)


def gen_locker():
    S, rng = 128, random.Random(108)
    buf = _blank(S, (0.40, 0.14, 0.13))
    _noise(buf, S, rng, 0.02)
    for y in range(14, 34, 5):                         # vent slats
        for x in range(18, S - 18):
            if (x // 4) % 2 == 0:
                buf[y][x] = (0.14, 0.05, 0.05)
    for y in range(40, 46):                            # name plate
        for x in range(S - 40, S - 16):
            buf[y][x] = (0.75, 0.74, 0.70)
    for x in range(S - 24, S - 20):                    # handle
        for y in range(60, 82):
            buf[y][x] = (0.78, 0.77, 0.73)
    for y in range(S - 10, S):                         # grime
        for x in range(S):
            if rng.random() < 0.5:
                c = buf[y][x]
                buf[y][x] = (c[0] * 0.8, c[1] * 0.8, c[2] * 0.8)
    _write('locker.png', buf)


def gen_ceiling():
    S, rng = 128, random.Random(109)
    buf = _blank(S, (0.74, 0.73, 0.70))
    _noise(buf, S, rng, 0.025)
    G = 64
    for y in range(S):
        for x in range(S):
            if x % G < 2 or y % G < 2:                 # panel grid
                buf[y][x] = (0.52, 0.51, 0.49)
    _blotches(buf, S, rng, 5, 3, 8, 0.15)              # water stains
    _write('ceiling.png', buf)


def gen_blackboard():
    S, rng = 128, random.Random(110)
    buf = _blank(S, (0.07, 0.13, 0.10))
    _noise(buf, S, rng, 0.02)
    for _ in range(10):                                # chalk smudges
        cx, cy = rng.randrange(S), rng.randrange(S)
        for dy in range(-6, 7):
            for dx in range(-6, 7):
                if dx * dx + dy * dy <= 36:
                    x, y = (cx + dx) % S, (cy + dy) % S
                    if rng.random() < 0.3:
                        c = buf[y][x]
                        buf[y][x] = (_clamp(c[0] + 0.06), _clamp(c[1] + 0.08), _clamp(c[2] + 0.06))
    for _ in range(9):                                 # chalk writing strokes
        x, y = rng.randrange(S - 30), rng.randrange(S - 20) + 10
        w, h = rng.randint(10, 26), rng.randint(4, 9)
        for yy in range(y, min(S, y + h)):
            xx = x
            for _ in range(w):
                if 0 <= xx < S and rng.random() < 0.8:
                    buf[yy][xx] = (0.72, 0.75, 0.72)
                xx += 1
    _write('blackboard.png', buf)


def gen_bark():
    S, rng = 128, random.Random(111)
    buf = _blank(S, (0.24, 0.17, 0.12))
    for x in range(S):                                 # vertical streaks
        v = 0.5 + 0.5 * math.sin(x * 0.5)
        for y in range(S):
            n = rng.uniform(-0.04, 0.04)
            f = 0.75 + 0.45 * v
            buf[y][x] = (_clamp((0.24 * f) + n), _clamp((0.17 * f) + n), _clamp((0.12 * f) + n))
    for _ in range(4):                                 # knots
        cx, cy = rng.randrange(S), rng.randrange(S)
        for dy in range(-7, 8):
            for dx in range(-4, 5):
                if (dx * dx) / 16.0 + (dy * dy) / 49.0 <= 1:
                    x, y = (cx + dx) % S, (cy + dy) % S
                    buf[y][x] = (0.10, 0.07, 0.05)
    _write('bark.png', buf)


def gen_grass():
    S, rng = 128, random.Random(112)
    buf = _blank(S, (0.12, 0.19, 0.08))
    _noise(buf, S, rng, 0.05)
    _blotches(buf, S, rng, 12, 4, 12, 0.2)
    for _ in range(300):                               # blades
        x, y = rng.randrange(S), rng.randrange(S)
        h = rng.randint(2, 5)
        for k in range(h):
            yy = (y + k) % S
            buf[yy][x] = (_clamp(buf[yy][x][0] + 0.06),
                          _clamp(buf[yy][x][1] + 0.10),
                          _clamp(buf[yy][x][2] + 0.04))
    _write('grass.png', buf)


# ---------------- city facades ----------------
def _gen_building(name, seed, base):
    S, rng = 256, random.Random(seed)
    buf = _blank(S, base)
    _noise(buf, S, rng, 0.025)
    margin, cols, rows = 14, 6, 8
    cw = (S - 2 * margin) / float(cols)
    rh = (S - 2 * margin) / float(rows)
    for ry in range(rows):
        for rx in range(cols):
            wx0 = int(margin + rx * cw + 5)
            wx1 = int(margin + (rx + 1) * cw - 5)
            wy0 = int(margin + ry * rh + 5)
            wy1 = int(margin + (ry + 1) * rh - 5)
            lit = rng.random() < 0.22
            for y in range(wy0, wy1):
                for x in range(wx0, wx1):
                    if lit:
                        t = (y - wy0) / float(max(1, wy1 - wy0))
                        r = 1.00 - 0.25 * t
                        g = 0.80 - 0.28 * t
                        b = 0.45 - 0.20 * t
                    else:
                        t = (y - wy0) / float(max(1, wy1 - wy0))
                        r, g, b = 0.03, 0.04, 0.06
                        if t < 0.3:                    # sky reflection at window top
                            r, g, b = 0.10, 0.12, 0.17
                    n = rng.uniform(-0.02, 0.02)
                    buf[y][x] = (_clamp(r + n), _clamp(g + n), _clamp(b + n))
            if lit and rng.random() < 0.4:             # lit window frame glow
                for x in range(wx0 - 1, wx1 + 1):
                    buf[wy1 - 1][x] = (_clamp(buf[wy1 - 1][x][0] * 1.1),
                                        _clamp(buf[wy1 - 1][x][1] * 1.1), buf[wy1 - 1][x][2])
    for ry in range(rows + 1):                         # floor seams
        y = int(margin + ry * rh) - 1
        if 0 <= y < S:
            for x in range(S):
                buf[y][x] = (base[0] * 0.7, base[1] * 0.7, base[2] * 0.7)
    for y in range(S - 10, S):                         # street grime at base
        for x in range(S):
            if rng.random() < 0.6:
                c = buf[y][x]
                buf[y][x] = (c[0] * 0.85, c[1] * 0.85, c[2] * 0.85)
    _write(name, buf)


def gen_building1():
    _gen_building('building1.png', 201, (0.16, 0.15, 0.19))


def gen_building2():
    _gen_building('building2.png', 202, (0.13, 0.16, 0.20))


def gen_building3():
    _gen_building('building3.png', 203, (0.17, 0.13, 0.13))


# ---------------- THE FACE ----------------
def gen_nextbot_face():
    S = 384
    rng = random.Random(666)
    buf = _blank(S, (0.02, 0.02, 0.03))
    hx, hy, hrx, hry = S * 0.5, S * 0.55, S * 0.37, S * 0.45
    exs = (S * 0.345, S * 0.655)
    ey = S * 0.42
    erx, ery = S * 0.145, S * 0.185
    prad = S * 0.055
    mx, my, mrx, mry = S * 0.5, S * 0.78, S * 0.26, S * 0.15
    for y in range(S):
        for x in range(S):
            dxh, dyh = (x - hx) / hrx, (y - hy) / hry
            d2 = dxh * dxh + dyh * dyh
            if d2 <= 1.0:
                shade = 1.0 - 0.50 * math.sqrt(d2)
                n = rng.uniform(-0.03, 0.03)
                r, g, b = 0.50 * shade + n, 0.46 * shade + n, 0.40 * shade + n
                buf[y][x] = (_clamp(r), _clamp(g), _clamp(b))
                # eye sockets
                for ex in exs:
                    dxe, dye = (x - ex) / erx, (y - ey) / ery
                    e2 = dxe * dxe + dye * dye
                    if e2 <= 1.0:
                        buf[y][x] = (0.0, 0.0, 0.0)
                        dpx, dpy = x - ex, y - ey
                        pd2 = dpx * dpx + dpy * dpy
                        if pd2 <= prad * prad:
                            t = math.sqrt(pd2) / prad
                            buf[y][x] = (_clamp(1.0 - 0.85 * t),
                                         _clamp(0.06 * (1 - t)),
                                         _clamp(0.06 * (1 - t)))
                # mouth
                dxm, dym = (x - mx) / mrx, (y - my) / mry
                if dxm * dxm + dym * dym <= 1.0:
                    buf[y][x] = (0.03, 0.0, 0.0)
                    # teeth along the upper lip
                    ty = int(my - mry)
                    if abs(y - ty) < 14 and (x % 26) < 16 and abs(x - mx) < mrx - 6:
                        buf[y][x] = (0.78, 0.76, 0.70)
    # grain
    for y in range(S):
        for x in range(S):
            if buf[y][x] != (0.02, 0.02, 0.03) and rng.random() < 0.5:
                n = rng.uniform(-0.02, 0.02)
                c = buf[y][x]
                buf[y][x] = (_clamp(c[0] + n), _clamp(c[1] + n), _clamp(c[2] + n))
    _write('nextbot_face.png', buf)


# ---------------- registry ----------------
_GENERATORS = {
    'floor_tile.png': gen_floor_tile,
    'concrete.png': gen_concrete,
    'asphalt.png': gen_asphalt,
    'brick.png': gen_brick,
    'wall_school.png': gen_wall_school,
    'wood.png': gen_wood,
    'metal.png': gen_metal,
    'locker.png': gen_locker,
    'ceiling.png': gen_ceiling,
    'blackboard.png': gen_blackboard,
    'bark.png': gen_bark,
    'grass.png': gen_grass,
    'building1.png': gen_building1,
    'building2.png': gen_building2,
    'building3.png': gen_building3,
    'nextbot_face.png': gen_nextbot_face,
}


def ensure_all(folder=TEX_DIR):
    os.makedirs(folder, exist_ok=True)
    todo = [n for n, fn in _GENERATORS.items()
            if not os.path.exists(os.path.join(folder, n))]
    if todo:
        print('RUN OR DONT IT: baking', len(todo), 'textures (first launch only)...')
        for n in todo:
            _GENERATORS[n]()
