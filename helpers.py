# ============================================================
#  RUN OR DONT IT - small shared helpers
#  (c) 2026 Project Revision / Zarto's Studios. All rights reserved.
# ============================================================


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
