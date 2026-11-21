# ============================================================
#  RUN OR DONT IT - audio manager
#  (c) 2026 Project Revision / Zarto's Studios. All rights reserved.
#
#  Drop your own (properly licensed) files into assets/sounds/ and they
#  WIN over the generated ones. Supported: .mp3 / .ogg / .wav
#
#    ambience.*   heartbeat.*   chase.*      footstep.*
#    slide.*     scream.*      jumpscare.*   hide.*
# ============================================================
import os

from panda3d.core import Filename

import sfx_generator

SOUND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'sounds')


def _loader():
    import builtins
    return builtins.base.loader


class Sound:
    def __init__(self, key, folder=SOUND_DIR, loop=False, volume=1.0):
        self.clip = None
        self.volume = volume
        self.loop = loop
        for ext in ('.mp3', '.ogg', '.wav'):
            path = os.path.join(folder, key + ext)
            if os.path.exists(path):
                try:
                    fn = Filename.fromOsSpecific(os.path.abspath(path))
                    self.clip = _loader().loadSfx(str(fn))
                except Exception:
                    self.clip = None
                break
        if self.clip:
            self.clip.setLoop(self.loop)
            self.clip.setVolume(volume)

    def play(self, volume=None):
        if not self.clip:
            return
        v = self.volume if volume is None else volume
        self.clip.setVolume(max(0.0, min(1.0, v)))
        self.clip.play()

    def stop(self):
        if self.clip:
            self.clip.stop()

    def set_volume(self, v):
        if self.clip:
            self.clip.setVolume(max(0.0, min(1.0, v)))


class AudioManager:
    def __init__(self):
        os.makedirs(SOUND_DIR, exist_ok=True)
        sfx_generator.ensure_all(SOUND_DIR)

        self.ambience = Sound('ambience', loop=True, volume=0.7)
        self.heartbeat = Sound('heartbeat', loop=True, volume=0.0)
        self.chase = Sound('chase', loop=True, volume=0.0)   # optional: your chase music
        self.footstep = Sound('footstep', volume=0.5)
        self.slide = Sound('slide', volume=0.6)
        self.scream = Sound('scream', volume=0.8)
        self.jumpscare = Sound('jumpscare', volume=1.0)
        self.hide = Sound('hide', volume=0.7)

    def stop_all(self):
        for s in (self.ambience, self.heartbeat, self.chase, self.scream):
            if s is not None:
                s.stop()

    def set_chase_intensity(self, closeness):
        """closeness: 0.0 (far/no chase) .. 1.0 (it is RIGHT BEHIND YOU)"""
        self.heartbeat.set_volume(0.85 * closeness)
        self.chase.set_volume(min(1.0, closeness * 1.2))
