# ============================================================
#  RUN OR DONT IT - small shared helpers
#  (c) 2026 Project Revision / Zarto's Studios. All rights reserved.
# ============================================================
import os

from ursina import load_texture

TEX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'textures')

_tex_cache = {}


def tune_pointlight(light, attenuation=(1.0, 0.06, 0.02)):
    """Give a ursina PointLight a distance falloff. Best-effort across ursina
    versions, so it never crashes if internals differ."""
    if light is None:
        return False
    try:
        light._light.setAttenuation(attenuation)
        return True
    except Exception:
        pass
    try:
        light.attenuation = attenuation
        return True
    except Exception:
        return False


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
