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
    _tex_box(c, (1.2, 2, 0), (0.3, 4, 2.3), col, tex)      # right side
    _tex_box(c, (0, 4, 0), (2.7, 0.3, 2.4), col, tex)      # roof
    spot = {
        'pos': c.world_position + c.back * 0.6,
        ' ' if False else 'exit': c.world_position + c.forward * 1.6,
        'label': label,
    }
    game.hide_spots.append(spot)
    return c


