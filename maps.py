# ============================================================
#  RUN OR DONT IT - map builders (SCHOOL / STORE / CITY)
#  (c) 2026 Project Revision / Zarto's Studios. All rights reserved.
#
#  Every prop is multi-part: desks have legs + chairs, lockers have
#  vents, freezers have glass doors, trees have bark + canopy layers,
#  cars have cabins/wheels/headlights. Textures are generated PNGs.
# ============================================================
import random as _r

from ursina import *
from ursina.lights import PointLight

from helpers import load_tex, tune_pointlight

MAP_INFO = {
    'school': {'label': 'SCHOOL'},
    'store': {'label': 'STORE'},
    'city': {'label': 'CITY'},
}


# ---------------- textured building blocks ----------------
def _tex_box(parent, pos, scale, col, tex=None, collider=True, tiling=1):
    e = Entity(parent=parent, model='cube', position=pos, scale=scale,
               color=col, collider='box' if collider else None)
    if tex is not None:
        e.texture = tex
        try:
            e.texture_scale = (tiling, tiling)
        except Exception:
            pass
    return e


def _box(parent, pos, scale, col, collider=True):
    return _tex_box(parent, pos, scale, col, None, collider)


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
        self.lamp = Entity(parent=self, model='cube', scale=lamp_scale,
                           color=col, texture=load_tex('metal'), unlit=True)
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


# ---------------- hiding closets ----------------
def _closet(game, parent, x, z, rot_y, col, label, tex=None):
    c = Entity(parent=parent, position=(x, 0, z), rotation_y=rot_y)
    _tex_box(c, (0, 2, -1.15), (2.6, 4, 0.3), col, tex)   # back
    _tex_box(c, (-1.2, 2, 0), (0.3, 4, 2.3), col, tex)    # left side
    _tex_box(c, (1.2, 2, 0), (0.3, 4, 2.3), col, tex)     # right side
    _tex_box(c, (0, 4, 0), (2.7, 0.3, 2.4), col, tex)     # roof
    spot = {
        'pos': c.world_position + c.back * 0.6,
        'exit': c.world_position + c.forward * 1.6,
        'label': label,
    }
    game.hide_spots.append(spot)
    return c


def _exit_marker(game, parent, pos):
    e = Entity(parent=parent, position=pos)
    pad = _tex_box(e, (0, 0.07, 0), (3.4, 0.14, 3.4), color.rgb(140, 40, 40),
                   load_tex('concrete'))
    beam = _tex_box(e, (0, 3.5, 0), (0.5, 7, 0.5), color.rgb(160, 45, 45), None, False)
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
#  SHARED DETAILED PROPS
# ============================================================
def _desk(parent, x, z, rot_y):
    wood = load_tex('wood')
    d = Entity(parent=parent, position=(x, 0, z), rotation_y=rot_y)
    _tex_box(d, (0, 0.72, 0), (1.8, 0.08, 1.0), color.rgb(180, 130, 80), wood)  # top
    for (lx, lz) in ((-0.8, -0.42), (0.8, -0.42), (-0.8, 0.42), (0.8, 0.42)):
        _box(d, (lx, 0.34, lz), (0.09, 0.68, 0.09), color.rgb(70, 48, 28))     # legs
    _box(d, (0, 0.45, -0.46), (1.6, 0.08, 0.62), color.rgb(96, 70, 44))        # under tray
    ch = Entity(parent=parent, position=(x + 1.2, 0, z - 0.6), rotation_y=rot_y)
    _tex_box(ch, (0, 0.45, 0), (0.9, 0.08, 0.9), color.rgb(150, 110, 70), wood) # seat
    _box(ch, (0, 0.80, -0.40), (0.9, 0.7, 0.08), color.rgb(96, 70, 44))        # backrest
    for (lx, lz) in ((-0.36, -0.36), (0.36, -0.36), (-0.36, 0.36), (0.36, 0.36)):
        _box(ch, (lx, 0.22, lz), (0.07, 0.44, 0.07), color.rgb(70, 48, 28))
    return d


def _teacher_desk(parent, x, z, rot_y):
    wood = load_tex('wood')
    d = Entity(parent=parent, position=(x, 0, z), rotation_y=rot_y)
    _tex_box(d, (0, 0.78, 0), (2.6, 0.10, 1.1), color.rgb(170, 120, 75), wood)
    _box(d, (0, 0.40, -0.48), (2.4, 0.72, 0.10), color.rgb(80, 56, 34))
    _box(d, (0, 0.40, 0.48), (2.4, 0.72, 0.10), color.rgb(80, 56, 34))
    _box(d, (-1.2, 0.40, 0), (0.10, 0.72, 1.0), color.rgb(80, 56, 34))
    _box(d, (1.2, 0.40, 0), (0.10, 0.72, 1.0), color.rgb(80, 56, 34))
    return d


def _blackboard(parent, x, z, rot_y, scale_x=6):
    e = Entity(parent=parent, position=(x, 0, z), rotation_y=rot_y)
    _tex_box(e, (0, 2.0, 0), (scale_x, 1.6, 0.12), color.rgb(60, 90, 70),
             load_tex('blackboard'), False)
    frame_col = color.rgb(60, 46, 30)
    _box(e, (0, 2.0, -0.04), (scale_x + 0.3, 1.8, 0.10), frame_col, False)
    _box(e, (0, 1.1, 0.1), (scale_x * 0.35, 0.06, 0.06), color.rgb(150, 150, 150), False)  # chalk tray
    return e


def _locker_row(parent, x, z, rot_y, count=4):
    tex = load_tex('locker')
    g = Entity(parent=parent, position=(x, 0, z), rotation_y=rot_y)
    for i in range(count):
        _tex_box(g, (i - count / 2 + 0.5, 1.05, 0), (0.95, 2.1, 0.55),
                 color.rgb(190, 66, 62), tex)
    _box(g, (0, 0.03, 0), (count * 0.98, 0.06, 0.6), color.rgb(40, 40, 44))
    return g


def _shelf(parent, x, z, rot_y, length, shelves=4):
    """Aisle shelf with stacked tinted products."""
    metal = load_tex('metal')
    s = Entity(parent=parent, position=(x, 0, z), rotation_y=rot_y)
    _tex_box(s, (0, 1.6, 0), (length, 0.12, 0.55), color.rgb(120, 120, 130), metal)
    _tex_box(s, (0, 0.15, 0), (length, 0.30, 0.65), color.rgb(90, 90, 100), metal)
    for i in range(shelves):
        y = 0.30 + i * 0.75
        _tex_box(s, (0, y, 0), (length, 0.05, 0.50), color.rgb(110, 110, 120), metal)
        rnd = _r.Random(int(x * 7 + z * 13 + i))
        px = -length / 2 + 0.5
        while px < length / 2 - 0.5:
            pw = rnd.uniform(0.25, 0.45)
            col = color.rgb(rnd.randint(50, 170), rnd.randint(50, 140), rnd.randint(40, 110))
            _tex_box(s, (px + pw / 2, y + 0.19, 0), (pw, 0.34, 0.40), col, None, False)
            px += pw + rnd.uniform(0.06, 0.25)
    return s


def _freezer(parent, x, z, rot_y):
    metal = load_tex('metal')
    f = Entity(parent=parent, position=(x, 0, z), rotation_y=rot_y)
    _tex_box(f, (0, 1.15, -0.15), (5.0, 2.3, 3.7), color.rgb(180, 190, 205), metal)
    for s in (-1, 1):                              # glass doors
        _tex_box(f, (s * 1.25, 1.15, 1.72), (2.3, 2.1, 0.08),
                 color.rgb(120, 150, 180), None, False)
    _light(f, None if False else f, (0, 2.05, 1.5), color.rgb(120, 170, 220))
    return f


def _tree(parent, x, z, rnd):
    """Bark trunk + tapered layered canopy. NOT two cubes."""
    bark = load_tex('bark')
    t = Entity(parent=parent, position=(x, 0, z))
    h = rnd.uniform(3.2, 5.2)
    _tex_box(t, (0, h * 0.45, 0), (0.5, h * 0.9, 0.5), color.rgb(120, 85, 55), bark, tiling=2)
    _tex_box(t, (0, h * 0.92, 0), (0.7, 0.3, 0.7), color.rgb(90, 62, 40), bark)
    layers = 3
    for i in range(layers):
        ly = h * (1.02 + 0.13 * i)
        lw = 2.8 - 0.55 * i + rnd.uniform(-0.3, 0.3)
        lh = rnd.uniform(0.75, 1.15)
        col = color.rgb(38 + i * 6, 62 + i * 10, 26 + i * 5)
        _tex_box(t, (rnd.uniform(-0.15, 0.15), ly, rnd.uniform(-0.15, 0.15)),
                 (lw, lh, lw), col, load_tex('grass'), False)
    return t


def _car(parent, x, z, rot_y, rnd):
    metal = load_tex('metal')
    car = Entity(parent=parent, position=(x, 0, z), rotation_y=rot_y)
    body_col = rnd.choice([color.rgb(120, 44, 50), color.rgb(48, 68, 120),
                           color.rgb(80, 80, 90), color.rgb(116, 104, 60),
                           color.rgb(46, 84, 46)])
    _tex_box(car, (0, 0.62, 0), (4.4, 0.62, 1.95), body_col, metal)
    _tex_box(car, (0, 0.28, 0), (4.1, 0.35, 1.7), color.rgb(30, 30, 34), metal)  # underbody
    _tex_box(car, (0, 1.05, -0.15), (2.3, 0.62, 1.85), body_col, metal)          # cabin
    _tex_box(car, (0, 1.05, 0.78), (2.15, 0.50, 0.08), color.rgb(25, 32, 45), None, False)  # windshield
    _tex_box(car, (0, 1.05, -1.06), (2.15, 0.50, 0.08), color.rgb(25, 32, 45), None, False)  # rear glass
    _tex_box(car, (0, 1.32, 0), (2.35, 0.10, 1.90), color.rgb(40, 40, 44), metal)  # roof
    for s in (-1, 1):
        for wx in (1.45, -1.45):                                                     # wheels
            _tex_box(car, (wx, 0.33, s * 0.98), (0.66, 0.66, 0.30), color.rgb(18, 18, 20), None, False)
            _tex_box(car, (wx, 0.33, s * 1.02), (0.30, 0.30, 0.32), color.rgb(70, 70, 75), metal, False)
        _tex_box(car, (2.21, 0.62, s * 0.6), (0.06, 0.16, 0.30), color.rgb(210, 205, 150), None, False)  # headlights
        _tex_box(car, (-2.21, 0.66, s * 0.6), (0.06, 0.14, 0.25), color.rgb(150, 40, 35), None, False)  # taillights
    return car


def _street_lamp(game, parent, x, z, rot_y, flicker):
    metal = load_tex('metal')
    l = Entity(parent=parent, position=(x, 0, z), rotation_y=rot_y)
    _tex_box(l, (0, 0.15, 0), (0.5, 0.3, 0.5), color.rgb(45, 45, 50), concrete_tex := load_tex('concrete'))
    _tex_box(l, (0, 2.75, 0), (0.22, 5.5, 0.22), color.rgb(50, 50, 56), metal)
    _tex_box(l, (0, 5.35, 0), (0.16, 0.4, 0.16), color.rgb(50, 50, 56), metal)
    _tex_box(l, (0.75, 5.5, 0), (1.5, 0.12, 0.12), color.rgb(50, 50, 56), metal)
    _tex_box(l, (1.4, 5.38, 0), (0.7, 0.10, 0.35), color.rgb(215, 185, 125), None, False)
    if flicker:
        fl = FlickerLight(game, l, (1.4, 5.2, 0), color.rgb(215, 185, 125),
                          flicker=True, lamp_scale=(0.6, 0.08, 0.32))
    else:
        _light(game, l, (1.4, 5.0, 0), color.rgb(185, 160, 105))
        fl = None
    return l, fl


def _bench(parent, x, z, rot_y):
    wood = load_tex('wood')
    b = Entity(parent=parent, position=(x, 0, z), rotation_y=rot_y)
    _tex_box(b, (0, 0.45, 0), (2.4, 0.09, 0.55), color.rgb(130, 95, 60), wood)
    _tex_box(b, (0, 0.75, -0.26), (2.4, 0.5, 0.08), color.rgb(130, 95, 60), wood)
    for s in (-1, 1):
        _box(b, (s * 0.95, 0.22, 0), (0.10, 0.44, 0.45), color.rgb(40, 40, 44))
    return b


def _hydrant(parent, x, z):
    h = Entity(parent=parent, position=(x, 0, z))
    _box(h, (0, 0.35, 0), (0.30, 0.70, 0.30), color.rgb(150, 35, 30))
    _box(h, (0, 0.72, 0), (0.36, 0.10, 0.36), color.rgb(150, 35, 30))
    _box(h, (0, 0.80, 0), (0.16, 0.18, 0.16), color.rgb(150, 35, 30))
    for s in (-1, 1):
        _box(h, (s * 0.20, 0.45, 0), (0.14, 0.14, 0.14), color.rgb(140, 32, 28))
    return h


def _dumpster(parent, x, z, rot_y):
    d = Entity(parent=parent, position=(x, 0, z), rotation_y=rot_y)
    _box(d, (0, 0.62, 0), (2.2, 1.15, 1.3), color.rgb(38, 66, 44))
    _box(d, (0, 1.22, -0.67), (2.2, 0.14, 0.06), color.rgb(30, 52, 34))
    _box(d, (0, 1.22, 0.67), (2.2, 0.14, 0.06), color.rgb(30, 52, 34))
    _box(d, (0, 1.30, 0), (2.3, 0.10, 1.4), color.rgb(28, 48, 32))
    return d


def _bus_stop(game, parent, x, z, rot_y, flicker=False):
    glass_col = color.rgb(90, 110, 130)
    b = Entity(parent=parent, position=(x, 0, z), rotation_y=rot_y)
    metal = load_tex('metal')
    _tex_box(b, (0, 1.2, -1.0), (4.0, 2.4, 0.12), glass_col, None, False)     # back glass
    _tex_box(b, (-2.0, 1.2, 0), (0.12, 2.4, 2.0), glass_col, None, False)     # side glass
    _tex_box(b, (0, 2.45, 0), (4.2, 0.15, 2.2), color.rgb(50, 50, 56), metal)
    _bench(parent, x, z, rot_y)
    fl = None
    if flicker:
        fl = FlickerLight(game, b, (0, 2.2, 0), color.rgb(150, 180, 200),
                          flicker=True, lamp_scale=(0.5, 0.06, 0.5))
    return b, fl


# ============================================================
#  SCHOOL
# ============================================================
def _school(game, parent):
    rnd = _r.Random(11)
    W_, D_ = 120, 76
    tex_wall = load_tex('wall_school')
    tex_floor = load_tex('floor_tile')
    tex_ceil = load_tex('ceiling')

    Entity(parent=parent, model='plane', scale=(W_, 1, D_), color=color.rgb(255, 255, 255),
           texture=tex_floor, texture_scale=(24, 16), collider='box')
    _tex_box(parent, (0, 4.6, 0), (W_, 0.3, D_), color.rgb(255, 255, 255), tex_ceil, False, 24)

    def wall(x, z, sx, sz, h=4, col=None):
        col = col or color.rgb(255, 255, 255)
        _tex_box(parent, (x, h / 2, z), (sx, h, sz), col, tex_wall)

    # outer shell
    wall(0, -D_ / 2, W_, 1)
    wall(0, D_ / 2, W_, 1)
    wall(-W_ / 2, 0, 1, D_)
    wall(W_ / 2, 0, 1, D_)

    # corridor walls with doorways into 4 rooms per side
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
            if cx == 45 and s == 1:                       # GYM
                for step in range(4):                     # bleachers
                    y = 0.4 + step * 0.8
                    z = s * (15 + step * 1.7)
                    _tex_box(parent, (cx, y, z), (18, 0.8, 1.7), color.rgb(255, 255, 255),
                             load_tex('wood'), tiling=8)
                # basketball hoop
                hoop = Entity(parent=parent, position=(cx, 0, s * 36))
                _box(hoop, (0, 3.05, 0), (0.1, 0.1, 0.1), color.rgb(200, 80, 40))
                _box(hoop, (0, 3.05, 0.6), (1.8, 1.05, 0.10), color.rgb(160, 60, 30),
                     collider=False)                      # backboard
                _box(hoop, (0, 2.9, 0.75), (1.1, 0.7, 0.05), color.rgb(220, 220, 230),
                     collider=False)                      # white square
                _box(hoop, (0, 2.95, 0.42), (1.2, 0.06, 0.35), color.rgb(220, 100, 60),
                     collider=False)                     # rim
                continue
            if cx == 45 and s == -1:                      # CAFETERIA
                for i in range(3):
                    for j in range(2):
                        _tex_box(parent, (cx - 6 + i * 6, 0.38, s * (13 + j * 8)),
                                 (4.2, 0.08, 1.5), color.rgb(255, 255, 255), tex_ceil, False)
                        for (lx, lz) in ((-1.9, -0.6), (1.9, -0.6), (-1.9, 0.6), (1.9, 0.6)):
                            _box(parent, (cx - 6 + i * 6 + lx, 0.19, s * (13 + j * 8) + lz),
                                 (0.08, 0.38, 0.08), color.rgb(70, 48, 28))
                _bench(parent, cx - 10, s * 30, 90)
                _bench(parent, cx + 10, s * 30, 90)
                continue
            # CLASSROOM
            _blackboard(parent, cx, s * 36.6, 180 if s > 0 else 0, 6)
            _teacher_desk(parent, cx + 3.5, s * 32, 0)
            rnd_desk = _r.Random(int(cx * 3 + s))
            for r_ in range(3):
                for c_ in range(4):
                    _desk(parent, cx - 6 + c_ * 4, s * (11 + r_ * 5.5),
                          180 if s > 0 else 0)

    # lockers along the corridor
    locker_tex = load_tex('locker')
    for s in (-1, 1):
        for lx in range(-54, 55, 8):
            if any(abs(lx - c) < 5 for c in room_centers):
                continue
            _locker_row(parent, lx, s * 3.45, 180 if s > 0 else 0, 4)

    # ceiling fluorescents in the corridor
    for lx in (-50, -25, 0, 25, 50):
        FlickerLight(game, parent, (lx, 4.3, 0), color.rgb(195, 188, 160),
                     flicker=rnd.random() < 0.3)
    # classroom lights
    for s in (-1, 1):
        for cx in (-45, 15):
            FlickerLight(game, parent, (cx, 4.3, s * 20), color.rgb(150, 148, 158),
                         flicker=rnd.random() < 0.5, lamp_scale=(1.2, 0.05, 1.2))

    # hiding closets
    cw = color.rgb(255, 255, 255)
    _closet(game, parent, -57, 2.2, 90, cw, 'Janitor Closet', tex_wall)
    _closet(game, parent, 57, -2.2, -90, cw, 'Janitor Closet', tex_wall)
    _closet(game, parent, -45, 35, 180, cw, 'Supply Closet', tex_wall)
    _closet(game, parent, 15, -35, 0, cw, 'Supply Closet', tex_wall)

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
    tex_wall = load_tex('brick')
    tex_floor = load_tex('concrete')
    tex_ceil = load_tex('ceiling')

    Entity(parent=parent, model='plane', scale=(W_, 1, D_), color=color.rgb(255, 255, 255),
           texture=tex_floor, texture_scale=(20, 13), collider='box')
    _tex_box(parent, (0, 4.4, 0), (W_, 0.3, D_), color.rgb(255, 255, 255), tex_ceil, False, 20)

    def wall(x, z, sx, sz, h=4.2, col=None):
        col = col or color.rgb(255, 255, 255)
        _tex_box(parent, (x, h / 2, z), (sx, h, sz), col, tex_wall)

    wall(0, D_ / 2, W_, 1)
    wall(-W_ / 2, 0, 1, D_)
    wall(W_ / 2, 0, 1, D_)
    wall(-30.5, -D_ / 2, 35, 1)
    wall(30.5, -D_ / 2, 35, 1)

    # detailed aisle shelves
    for z in (-18, -9, 0, 9, 18):
        _shelf(parent, -6, z, 0, 52)

    # freezer corner (west) - glass doors + glow inside
    for fz in (-24, -17, -10):
        _freezer(parent, -43, fz, 90)

    # checkout area (south-east)
    for i in range(3):
        x = 22 + i * 8
        _tex_box(parent, (x, 0.55, -26), (1.2, 1.1, 6), color.rgb(255, 255, 255), load_tex('metal'))
        _box(parent, (x, 1.35, -27.5), (0.9, 0.6, 0.9), color.rgb(38, 38, 44), False)   # register
        _box(parent, (x, 0.28, -22.5), (0.14, 0.55, 0.14), color.rgb(120, 120, 126))   # legs

    # stockroom (north-east)
    wall(38, 10, 20, 0.8)
    wall(30, 12.5, 0.8, 5)
    wall(30, 24.5, 0.8, 11)
    wood = load_tex('wood')
    for i in range(6):
        _tex_box(parent, (34 + (i % 3) * 4, 0.6 + (i // 3) * 1.3, 22 - (i % 3)),
                 (1.3, 1.2, 1.3), color.rgb(255, 255, 255), wood)

    # produce displays near the entrance
    for (px, pz) in ((-24, -26), (-16, -26), (-24, -20), (-16, -20)):
        _tex_box(parent, (px, 0.45, pz), (3.2, 0.9, 2.4), color.rgb(255, 255, 255), load_tex('wood'))
        _box(parent, (px, 0.95, pz), (3.0, 0.08, 2.2), color.rgb(60, 70, 50), False)

    # hiding closets
    cw = color.rgb(255, 255, 255)
    _closet(game, parent, -44, -28, 0, cw, 'Freezer Nook', tex_wall)
    _closet(game, parent, 44, 26, -90, cw, 'Stockroom', tex_wall)
    _closet(game, parent, 26, -18, 180, cw, 'Service Hall', tex_wall)

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
    asph = load_tex('asphalt')
    conc = load_tex('concrete')
    grass = load_tex('grass')

    Entity(parent=parent, model='plane', scale=(150, 1, 150), color=color.rgb(255, 255, 255),
           texture=asph, texture_scale=(30, 30), collider='box')

    # sidewalks on each block
    for bx in (-50, 0, 50):
        for bz in (-50, 0, 50):
            _tex_box(parent, (bx, 0.06, bz), (36, 0.12, 36), color.rgb(255, 255, 255), conc, False, 6)

    # crosswalks on the central plaza streets
    for cx in (-12.5, 12.5):
        _tex_box(parent, (cx, 0.02, 0), (1.8, 0.05, 24), color.rgb(220, 215, 200), conc, False)
        _tex_box(parent, (cx, 0.02, 0), (1.8, 0.05, 24), color.rgb(220, 215, 200), conc, False)
    _tex_box(parent, (0, 0.02, -12.5), (24, 0.05, 1.8), color.rgb(220, 215, 200), conc, False)
    _tex_box(parent, (0, 0.02, 12.5), (24, 0.05, 1.8), color.rgb(220, 215, 200), conc, False)

    # BUILDINGS with procedural facades
    facades = ['building1', 'building2', 'building3']
    for bx in (-50, 0, 50):
        for bz in (-50, 0, 50):
            if bx == 0 and bz == 0:
                continue                                   # central plaza = exit
            spots = [(-9, -9), (9, -9), (-9, 9), (9, 9)]
            rnd.shuffle(spots)
            for (ox, oz) in spots[:rnd.randint(1, 2)]:
                w = rnd.uniform(13, 17)
                d = rnd.uniform(13, 17)
                h = rnd.uniform(10, 26)
                f = load_tex(rnd.choice(facades))
                b = _tex_box(parent, (bx + ox, h / 2, bz + oz), (w, h, d),
                             color.rgb(255, 255, 255), f, True, max(1, int(h / 6)))
                # rooftop details
                _tex_box(parent, (bx + ox, h + 0.4, bz + oz), (w * 0.4, 0.8, d * 0.4),
                         color.rgb(60, 60, 64), conc, False)              # roof box
                _box(parent, (bx + ox + w / 4, h + 1.8, bz + oz - d / 4),
                     (0.3, 2.5, 0.3), color.rgb(70, 70, 76))                # antenna
                _box(parent, (bx + ox + w / 4, h + 3.1, bz + oz - d / 4),
                     (0.1, 0.1, 0.1), color.rgb(255, 60, 60), False)        # beacon

    # plaza fountain (exit centerpiece)
    fz = Entity(parent=parent, position=(0, 0, 0))
    _tex_box(fz, (0, 0.3, 0), (5, 0.6, 5), color.rgb(255, 255, 255), conc)
    _tex_box(fz, (0, 0.65, 0), (4, 0.5, 4), color.rgb(40, 60, 80), None, False)   # water
    _tex_box(fz, (0, 1.2, 0), (1, 1.5, 1), color.rgb(255, 255, 255), conc, False)
    _tex_box(fz, (0, 2.05, 0), (2, 0.2, 2), color.rgb(255, 255, 255), conc, False)

    # trees around the plaza and streets
    tree_pts = [(-13, 13), (13, 13), (-13, -13), (13, -13),
                (-38, 13), (38, -13), (-13, 38), (13, -38),
                (38, 38), (-38, -38), (62, 0), (-62, 0), (0, 62), (0, -62)]
    for (tx, tz) in tree_pts:
        _tree(parent, tx, tz, rnd)

    # street lamps (some flicker)
    lamp_pts = [(-25, -25), (-25, 25), (25, -25), (25, 25), (0, -25), (0, 25)]
    for i, (lx, lz) in enumerate(lamp_pts):
        _street_lamp(game, parent, lx, lz, 0, flicker=(i % 3 == 0))

    # benches, hydrants, dumpsters, bus stops
    for (bx, bz, by) in ((-10, 8, 90), (10, 8, 90), (-10, -8, 270), (10, -8, 270)):
        _bench(parent, bx, bz, by)
    for (hx, hz) in ((-24, 12), (24, -12), (-12, -24), (12, 24)):
        _hydrant(parent, hx, hz)
    for _ in range(7):
        band = rnd.choice([-25, 25])
        off = rnd.choice([-6.5, 6.5])
        if rnd.random() < 0.5:
            _dumpster(parent, rnd.uniform(-60, 60), band + off, 0)
        else:
            _dumpster(parent, band + off, rnd.uniform(-60, 60), 90)
    _bus_stop(game, parent, -30, -30, 45, flicker=True)
    _bus_stop(game, parent, 30, 30, 225)

    # abandoned cars
    for _ in range(12):
        band = rnd.choice([-25, 25])
        off = rnd.choice([-5.2, 5.2])
        if rnd.random() < 0.5:
            _car(parent, rnd.uniform(-62, 62), band + off, 0, rnd)
        else:
            _car(parent, band + off, rnd.uniform(-62, 62), 90, rnd)

    # grass patches with trees on the outer ring
    for (gx, gz) in [(-64, 0), (64, 0), (0, -64), (0, 64),
                     (-64, 64), (64, -64), (-64, -64), (64, 64)]:
        _tex_box(parent, (gx, 0.03, gz), (18, 0.07, 18), color.rgb(255, 255, 255), grass, False, 4)
        _tree(parent, gx, gz, rnd)

    # alley nooks (hide spots)
    cw = color.rgb(255, 255, 255)
    tex_wall = load_tex('brick')
    _closet(game, parent, 28.5, 20, -90, cw, 'Alley Nook', tex_wall)
    _closet(game, parent, -28.5, -20, 90, cw, 'Alley Nook', tex_wall)
    _closet(game, parent, 20, -28.5, 0, cw, 'Service Door', tex_wall)
    _closet(game, parent, -20, 28.5, 180, cw, 'Service Door', tex_wall)

    exit_marker = _exit_marker(game, parent, (0, 0, 7.5))
    return {
        'spawn': Vec3(0, 0.05, 70), 'spawn_look': 180,
        'nextbot_spawn': Vec3(0, 0, -70),
        'exit': Vec3(0, 0, 7.5),
        'exit_marker': exit_marker,
        'escape_after': 180.0, 'grace': 15.0,
        'fog': (14, 80), 'bounds': (-72, 72, -72, 72),
    }
