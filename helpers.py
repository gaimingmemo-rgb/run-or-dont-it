# ============================================================
#  RUN OR DONT IT - small shared helpers
#  (c) 2026 Project Revision / Zarto's Studios. All rights reserved.
# ============================================================
import builtins
import os

from ursina import load_texture

TEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'textures')

_tex_cache = {}


def _render():
    base = getattr(builtins, 'base', None)
    return getattr(base, 'render', None) if base is not None else None


class LightSystem:
    """Raw Panda3D lights, tracked properly so cleanup never crashes.

    Ursina 8.x's PointLight wrapper registers a CHILD node on render;
    calling clearLight() on the wrapper entity makes Panda3D abort with
    'Not a Light object'. We keep the real node paths instead.
    """

    def __init__(self):
        self._nodes = []            # real light node paths (cleared each map)
        self._ambient_np = None     # persistent global ambient

    def add_point(self, parent, position, col, attenuation=(1.0, 0.06, 0.02)):
        render = _render()
        if render is None or parent is None:
            return None
        from panda3d.core import PointLight as PandaPointLight
        pl = PandaPointLight('point_light')
        pl.setColor(col)
        try:
            pl.setAttenuation(attenuation)
        except Exception:
            pass
        np = parent.attachNewNode(pl)
        try:
            np.setPos(position[0], position[1], position[2])
        except Exception:
            pass
        render.setLight(np)
        self._nodes.append(np)
        return np

    def set_color(self, np, col):
        if np is None:
            return
        try:
            np.node().setColor(col)
        except Exception:
            pass

    def ambient(self, col):
        render = _render()
        if render is None:
            return None
        if self._ambient_np is None:
            from panda3d.core import AmbientLight as PandaAmbientLight
            al = PandaAmbientLight('ambient_light')
            self._ambient_np = render.attachNewNode(al)
            render.setLight(self._ambient_np)
        self.set_color(self._ambient_np, col)
        return self._ambient_np

    def clear_map_lights(self):
        render = _render()
        for np in self._nodes:
            if render is not None:
                try:
                    render.clearLight(np)
                except Exception:
                    pass
            try:
                np.removeNode()
            except Exception:
                pass
        self._nodes.clear()


def load_tex(name, folder=TEX_DIR):
    """Load a generated PNG texture by name (no extension). Cached.
    Returns None if missing - callers then fall back to a plain color."""
    if name in _tex_cache:
        return _tex_cache[name]
    tex = None
    path = os.path.join(folder, name + '.png')
    if os.path.exists(path):
        try:
            tex = load_texture(path)
        except Exception:
            tex = None
    _tex_cache[name] = tex
    return tex
