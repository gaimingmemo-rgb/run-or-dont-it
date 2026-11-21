# ============================================================
#  RUN OR DONT IT - small shared helpers
#  (c) 2026 Project Revision / Zarto's Studios. All rights reserved.
# ============================================================
import os

from ursina import load_texture
from ursina.texture import Texture

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
    Returns None if missing - callers then fall back to a plain color.

    IMPORTANT: ursina's load_texture() treats its 'name' argument as a glob
    pattern searched inside its asset folders - passing an absolute OS path
    never matches anything and silently returns None. So we:
      1) try ursina's loader with the explicit folder + bare filename
      2) fall back to constructing a Texture directly from the full path
    """
    if name in _tex_cache:
        return _tex_cache[name]

    tex = None
    fname = name + '.png'
    path = os.path.join(folder, fname)

    if os.path.exists(path):
        # strategy 1: ursina's loader with a proper folder + bare file name
        try:
            from pathlib import Path
            tex = load_texture(fname, folder=Path(folder))
        except Exception:
            tex = None
        # strategy 2: direct Texture construction (version-proof)
        if tex is None:
            try:
                tex = Texture(path)
            except Exception:
                tex = None
        # strategy 3: any other ursina version quirks
        if tex is None:
            try:
                from panda3d.core import Filename
                tex = Texture(Filename.fromOsSpecific(os.path.abspath(path)))
            except Exception:
                tex = None

    _tex_cache[name] = tex
    if tex is None:
        print('  [tex] WARNING: could not load', name)
    return tex
