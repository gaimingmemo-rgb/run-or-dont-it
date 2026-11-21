# ============================================================
#  RUN OR DONT IT - map builders (SCHOOL / STORE / CITY)
#  (c) 2026 Project Revision / Zarto's Studios. All rights reserved.
# ============================================================
import random as _r

from ursina import *
from ursina.lights import PointLight

from helpers import tune_pointlight

MAP_INFO = {
    'school': {'label': 'SCHOOL'},
    'store': {'label': 'STORE'},
    'city': {'label': 'CITY'},
}


def _box(parent, pos, scale, col, collider=True):
    return Entity(parent=parent, model='cube', position=pos, scale=scale,
                  color=col, collider='box' if collider else None)


def _light(game, parent, pos, col):
    l = PointLight(parent=parent, position=pos, color=col)
    tune_pointlight(l)
    game.lights.append(l)
    return l


class FlickerLight(Entity):
    def __init__(self, game, parent, pos, col, flicker=True, lamp_scale=(0.9, 0.07, 0.9)):
        super().__init__(parent=parent, position=pos)
        self.pl = PointLight(parent=self, color=col)
        tune_pointlight(self.pl)
        game.lights.append(self.pl)
        self.base_col = col
        self.lamp = Entity(parent=self, model='cube', scale=lamp_scale, color=col)
        self.t = _r.random() * 2
        self.on = True
        self.flicker = flicker

    def update(self):
        if not self.flicker:
            return
        self.t -= time.dt
        if self.t <= 0:
            self.on = _r.random() > 0.3
            self.pl.enabled = self.on
            self.lamp.color = self.base_col if self.on else color.rgb(35, 35, 32)
            self.t = _r.uniform(0.06, 0.8)


def _closet(game, parent, x, z, rot_y, col, label):
    """U-shaped hiding closet. Opening faces local +z (rot_y rotates it)."""
    c = Entity(parent=parent, position=(x, 0, z), rotation_y=rot_y)
    _box(c, (0, 2, -1.15), (2.6, 4, 0.3), col)   # back
    _box(c, (-1.2, 2, 0), (0.3, 4, 2.3), col)    # left side
    _box(c, (1.2, 2, 0), (0.3, 4, 2.3), col)     # right side
    _box(c, (0, 4, 0), (2.7, 0.3, 2.4), col)     # roof
    spot = {
        'pos': c.world_position + c.back * 0.6,
        'exit': c.world_position + c.forward * 1.6,
        'label': label,
    }
    game.hide_spots.append(spot)
    return c


def _exit_marker(game, parent, pos):
    e = Entity(parent=parent, position=pos)
    pad = Entity(parent=e, model='cube', scale=(3.4, 0.14, 3.4),
                 position=(0, 0.07, 0), color=color.rgb(140, 40, 40))
    beam = Entity(parent=e, model='cube', scale=(0.5, 7, 0.5),
                  position=(0, 3.5, 0), color=color.rgb(160, 45, 45))
    l = _light(game, e, (0, 2.5, 0), color.rgb(140, 45, 45))
    return {'pad': pad, 'beam': beam, 'light': l}


def build_map(game, key, parent):
    if key == 'school':
        return _school(game, parent)
    if key == 'store':
        return _store(game, parent)
    if key == 'city':
        return _city(game, parent)
    raise ValueError('unknown map: ' + str(key))


# ============================================================
#  SCHOOL
# ============================================================
def _school(game, parent):
    rnd = _r.Random(11)
    W_, D_ = 120, 76
    col_wall = color.rgb(62, 58, 66)
    col_wall2 = color.rgb(48, 46, 54)
    col_desk = color.rgb(96, 70, 44)
    col_locker = color.rgb(122, 44, 44)

    Entity(parent=parent, model='plane', scale=(W_, 1, D_), color=color.rgb(40, 38, 42), collider='box')
    _box(parent, (0, 4.6, 0), (W_, 0.3, D_), color.rgb(16, 16, 20), collider=False)

    def wall(x, z, sx, sz, h=4, col=col_wall):
        _box(parent, (x, h / 2, z), (sx, h, sz), col)

    # outer shell
    wall(0, -D_ / 2, W_, 1)
    wall(0, D_ / 2, W_, 1)
    wall(-W_ / 2, 0, 1, D_)
    wall(W_ / 2, 0, 1, D_)

    # corridor along x with doorways into 4 rooms per side
    room_centers = (-45, -15, 15, 45)
    for s in (-1, 1):
        zw = 4 * s
        prev = -60
        for cx in room_centers:
            wall((prev + cx - 2.5) / 2, zw, (cx - 2.5) - prev, 0.7)
            prev = cx + 2.5
        wall((prev + 60) / 2, zw, 60 - prev, 0.7)
        for bx in (-30, 0, 30):
            wall(bx, s * 21.5, 0.7, 33)

    # room contents
    for s in (-1, 1):
        for cx in room_centers:
            if cx == 45 and s == 1:      # gym (north-east)
                for step in range(4):
                    _box(parent, (cx, 0.4 + step * 0.8, s * (15 + step * 1.7)),
                         (18, 0.8, 1.7), color.rgb(66, 58, 50))
                continue
            if cx == 45 and s == -1:     # cafeteria (south-east)
                for i in range(3):
                    for j in range(2):
                        _box(parent, (cx - 6 + i * 6, 0.38, s * (13 + j * 8)),
                             (4.2, 0.76, 1.5), color.rgb(104, 96, 86))
                continue
            # classroom: blackboard, teacher desk, desk grid
            _box(parent, (cx, 2, s * 37.2), (6, 1.6, 0.15), color.rgb(24, 26, 30), collider=False)
            _box(parent, (cx, 0.7, s * 30), (2.8, 1.4, 1.0), col_desk)
            for r_ in range(3):
                for c_ in range(4):
                    _box(parent, (cx - 6 + c_ * 4, 0.38, s * (11 + r_ * 5.5)),
                         (1.8, 0.76, 0.9), col_desk)

    # lockers along the corridor walls
    for s in (-1, 1):
        for lx in range(-56, 57, 3):
            if any(abs(lx - c) < 4 for c in room_centers):
                continue
            _box(parent, (lx, 1.05, s * 3.55), (1.5, 2.1, 0.55), col_locker)

    # hiding closets
    _closet(game, parent, -57, 2.2, 90, col_wall2, 'Janitor Closet')
    _closet(game, parent, 57, -2.2, -90, col_wall2, 'Janitor Closet')
    _closet(game, parent, -45, 35, 180, col_wall2, 'Supply Closet')
    _closet(game, parent, 15, -35, 0, col_wall2, 'Supply Closet')

    # lights
    for lx in (-50, -25, 0, 25, 50):
        FlickerLight(game, parent, (lx, 4.3, 0), color.rgb(195, 188, 160),
                     flicker=rnd.random() < 0.3)
    for s in (-1, 1):
        for cx in (-45, 15):
            FlickerLight(game, parent, (cx, 4.3, s * 20), color.rgb(150, 148, 158),
                         flicker=rnd.random() < 0.5, lamp_scale=(1.2, 0.05, 1.2))

    exit_marker = _exit_marker(game, parent, (56, 0, 0))
    return {
        'spawn': Vec3(-56, 0.05, 0), 'spawn_look': 90,
        'nextbot_spawn': Vec3(50, 0, 0),
        'exit': Vec3(56, 0, 0),
        'exit_marker': exit_marker,
        'escape_after': 150.0, 'grace': 12.0,
        'fog': (8, 55), 'bounds': (-58.5, 58.5, -36.5, 36.5),
    }


# ============================================================
#  STORE
# ============================================================
def _store(game, parent):
    rnd = _r.Random(4)
    W_, D_ = 96, 64
    col_wall = color.rgb(58, 56, 62)
    col_shelf = color.rgb(74, 74, 82)

    Entity(parent=parent, model='plane', scale=(W_, 1, D_), color=color.rgb(46, 46, 52), collider='box')
    _box(parent, (0, 4.4, 0), (W_, 0.3, D_), color.rgb(14, 14, 18), collider=False)

    def wall(x, z, sx, sz, h=4.2, col=col_wall):
        _box(parent, (x, h / 2, z), (sx, h, sz), col)

    wall(0, D_ / 2, W_, 1)
    wall(-W_ / 2, 0, 1, D_)
    wall(W_ / 2, 0, 1, D_)
    wall(-30.5, -D_ / 2, 35, 1)     # south wall, left of the entrance
    wall(30.5, -D_ / 2, 35, 1)      # south wall, right of the entrance

    # shelf aisles
    for z in (-18, -9, 0, 9, 18):
        _box(parent, (-6, 0.8, z), (56, 1.6, 1.3), col_shelf)
        _box(parent, (-6, 2.45, z), (56, 0.25, 0.6), color.rgb(58, 58, 64))
        for i in range(13):
            ix = -32 + i * 4.2
            _box(parent, (ix + rnd.uniform(-0.5, 0.5), 1.75, z + rnd.uniform(-0.2, 0.2)),
                 (1.3, 0.32, 0.8),
                 color.rgb(rnd.randint(60, 180), rnd.randint(60, 140), rnd.randint(40, 120)),
                 collider=False)

    # freezer corner (west)
    for fz in (-24, -17, -10):
        _box(parent, (-43, 1.15, fz), (5, 2.3, 4), color.rgb(150, 160, 175))
    _light(game, parent, (-41, 3.4, -17), color.rgb(90, 140, 205))
    _light(game, parent, (-41, 3.4, -24), color.rgb(80, 130, 200))

    # checkout area (south-east)
    for i in range(3):
        _box(parent, (22 + i * 8, 0.55, -26), (1.2, 1.1, 6), color.rgb(92, 92, 100))
        _box(parent, (22 + i * 8, 1.35, -27.5), (0.9, 0.6, 0.9), color.rgb(38, 38, 44), collider=False)

    # stockroom (north-east)
    wall(38, 10, 20, 0.8)
    wall(30, 12.5, 0.8, 5)
    wall(30, 24.5, 0.8, 11)
    for i in range(6):
        _box(parent, (34 + (i % 3) * 4, 0.6 + (i // 3) * 1.3, 22 - (i % 3)),
             (1.3, 1.2, 1.3), color.rgb(96, 78, 52))

    # hiding closets
    cw = color.rgb(50, 48, 56)
    _closet(game, parent, -44, -28, 0, cw, 'Freezer Nook')
    _closet(game, parent, 44, 26, -90, cw, 'Stockroom')
    _closet(game, parent, 26, -18, 180, cw, 'Service Hall')

    # lights
    FlickerLight(game, parent, (0, 4.25, 12), color.rgb(200, 200, 190), flicker=rnd.random() < 0.5)
    FlickerLight(game, parent, (0, 4.25, -12), color.rgb(200, 200, 190), flicker=False)
    FlickerLight(game, parent, (0, 4.25, -28), color.rgb(190, 185, 170), flicker=rnd.random() < 0.5)
    FlickerLight(game, parent, (36, 4.25, 20), color.rgb(170, 170, 175), flicker=False)

    exit_marker = _exit_marker(game, parent, (0, 0, -30))
    return {
        'spawn': Vec3(0, 0.05, 28), 'spawn_look': 180,
        'nextbot_spawn': Vec3(-42, 0, 22),
        'exit': Vec3(0, 0, -30),
        'exit_marker': exit_marker,
        'escape_after': 140.0, 'grace': 10.0,
        'fog': (6, 50), 'bounds': (-46.5, 46.5, -30.5, 30.5),
    }


# ============================================================
#  CITY
# ============================================================
def _city(game, parent):
    rnd = _r.Random(9)
    Entity(parent=parent, model='plane', scale=(150, 1, 150), color=color.rgb(28, 28, 33), collider='box')
    block_cols = [color.rgb(34, 33, 40), color.rgb(30, 34, 44),
                  color.rgb(38, 34, 34), color.rgb(28, 32, 36)]

    # 3x3 city blocks with streets between them
    for bx in (-50, 0, 50):
        for bz in (-50, 0, 50):
            _box(parent, (bx, 0.05, bz), (36, 0.1, 36), color.rgb(43, 43, 48), collider=False)
            if bx == 0 and bz == 0:
                continue      # central plaza = the exit
            spots = [(-9, -9), (9, -9), (-9, 9), (9, 9)]
            rnd.shuffle(spots)
            for (ox, oz) in spots[:rnd.randint(1, 2)]:
                w = rnd.uniform(13, 17)
                d = rnd.uniform(13, 17)
                h = rnd.uniform(7, 22)
                _box(parent, (bx + ox, h / 2, bz + oz), (w, h, d), rnd.choice(block_cols))
                # lit windows on the street-facing side
                fx = bx + ox + (w / 2 + 0.06 if ox > 0 else -w / 2 - 0.06)
                for _ in range(rnd.randint(3, 9)):
                    wy = rnd.uniform(1.6, max(2.6, h - 1.6))
                    wz = bz + oz + rnd.uniform(-d / 2 + 1.3, d / 2 - 1.3)
                    _box(parent, (fx, wy, wz), (0.12, 1.2, 1.0), color.rgb(190, 160, 70), collider=False)

    # plaza kiosk
    _box(parent, (0, 1.0, 7), (3.6, 2.0, 2.4), color.rgb(45, 45, 52))

    # street lamps
    lamp_pos = [(-25, -25), (-25, 25), (25, -25), (25, 25), (0, -25), (0, 25)]
    for i, (lx, lz) in enumerate(lamp_pos):
        l = Entity(parent=parent, position=(lx, 0, lz))
        _box(l, (0, 2.75, 0), (0.22, 5.5, 0.22), color.rgb(40, 40, 46))
        _box(l, (0.9, 5.4, 0), (1.8, 0.14, 0.14), color.rgb(40, 40, 46))
        if i % 3 == 0:
            FlickerLight(game, l, (1.6, 5.25, 0), color.rgb(215, 185, 125),
                         flicker=True, lamp_scale=(0.7, 0.12, 0.35))
        else:
            _box(l, (1.6, 5.25, 0), (0.7, 0.12, 0.35), color.rgb(215, 185, 125), collider=False)
            _light(game, l, (1.6, 5.0, 0), color.rgb(185, 160, 105))

    # abandoned cars
    car_cols = [color.rgb(62, 22, 26), color.rgb(24, 34, 60),
                color.rgb(40, 40, 46), color.rgb(58, 52, 30)]
    for _ in range(12):
        band = rnd.choice([-25, 25])
        off = rnd.choice([-5.2, 5.2])
        if rnd.random() < 0.5:
            pos, rot = (rnd.uniform(-62, 62), 0, band + off), 0
        else:
            pos, rot = (band + off, 0, rnd.uniform(-62, 62)), 90
        car = Entity(parent=parent, position=pos, rotation_y=rot)
        cc = rnd.choice(car_cols)
        _box(car, (0, 0.55, 0), (4.4, 0.9, 1.9), cc)
        _box(car, (0, 1.3, -0.25), (2.3, 0.7, 1.7), cc)

    # dumpsters (emergent cover - block its line of sight)
    for _ in range(7):
        band = rnd.choice([-25, 25])
        off = rnd.choice([-6.5, 6.5])
        if rnd.random() < 0.5:
            p = (rnd.uniform(-60, 60), 0.65, band + off)
        else:
            p = (band + off, 0.65, rnd.uniform(-60, 60))
        _box(parent, p, (2.2, 1.3, 1.3), color.rgb(38, 66, 44))

    # alley nooks (hide spots)
    cw = color.rgb(50, 48, 55)
    _closet(game, parent, 28.5, 20, -90, cw, 'Alley Nook')
    _closet(game, parent, -28.5, -20, 90, cw, 'Alley Nook')
    _closet(game, parent, 20, -28.5, 0, cw, 'Service Door')
    _closet(game, parent, -20, 28.5, 180, cw, 'Service Door')

    exit_marker = _exit_marker(game, parent, (0, 0, 0))
    return {
        'spawn': Vec3(0, 0.05, 70), 'spawn_look': 180,
        'nextbot_spawn': Vec3(0, 0, -70),
        'exit': Vec3(0, 0, 0),
        'exit_marker': exit_marker,
        'escape_after': 180.0, 'grace': 15.0,
        'fog': (14, 80), 'bounds': (-72, 72, -72, 72),
    }
