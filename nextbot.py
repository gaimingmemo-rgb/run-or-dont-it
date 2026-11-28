"""
Nextbot AI & Pursuit Engine for 'Run or dont'
Features:
- Balanced, beatable, yet relentless chase AI (Speed: 9.2 m/s vs player sprint 13.5 m/s)
- Taking corners and sliding around obstacles lets players outmaneuver the Nextbot
- Proximity-based audio tension (intense music rises as nextbot nears)
- Jumpscare trigger with screen shake and ear-piercing scream on catch
"""
import os
import math
from pathlib import Path
from ursina import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Nextbot(Entity):
    def __init__(self, target_player, spawn_pos=(40, 0, 40), on_catch_callback=None, **kwargs):
        bot_tex = "assets/textures/nextbot.png"

        super().__init__(
            position=spawn_pos,
            scale=(2.2, 3.0, 1.0),
            model='quad',
            texture=bot_tex,
            double_sided=True,
            color=color.white,
            **kwargs
        )

        self.target = target_player
        self.on_catch = on_catch_callback

        # Balanced pursuit speed:
        # Player Walk: 6.5 m/s
        # Nextbot Speed: 9.2 m/s -> Outruns walking players!
        # Player Sprint: 13.5 m/s -> Player CAN outrun it by sprinting!
        # Player Slide: 18.0 m/s -> Momentum burst!
        self.base_speed = 9.2
        self.current_speed = self.base_speed

        self.caught = False
        self.distance_to_player = 999.0

        # Sinister glowing red aura
        self.aura_light = PointLight(parent=self, position=(0, 1.5, 0), color=color.hex('#ff1a1a'))

        # Audio
        self.snd_jumpscare = Audio("assets/audio/jumpscare.wav", autoplay=False, loop=False, volume=1.0)
        self.snd_chase     = Audio("assets/audio/chase_music.wav", autoplay=True, loop=True, volume=0.15)

        # Hover bobbing timer
        self.bob_timer = 0.0

    def update(self):
        if self.caught or not self.target:
            return

        dt = time.dt
        if dt > 0.08:
            dt = 0.08

        # Vector to player
        dx = self.target.x - self.x
        dz = self.target.z - self.z
        self.distance_to_player = math.sqrt(dx * dx + dz * dz)

        # Always face the player (billboard horror effect)
        angle_rad = math.atan2(dx, dz)
        self.rotation_y = math.degrees(angle_rad)

        # Move towards player with smooth pursuit
        if self.distance_to_player > 0.1:
            dir_x = dx / self.distance_to_player
            dir_z = dz / self.distance_to_player
            self.x += dir_x * self.current_speed * dt
            self.z += dir_z * self.current_speed * dt

        # Eerie hovering bob above floor
        self.bob_timer += dt * 3.5
        self.y = 1.35 + math.sin(self.bob_timer) * 0.15

        # Dynamic chase music scaling by distance
        if self.snd_chase:
            # Full volume when within 15 meters, fading out over 60 meters
            prox = clamp(1.0 - (self.distance_to_player / 65.0), 0.10, 0.95)
            self.snd_chase.volume = prox

        # Catch / Jumpscare detection
        if self.distance_to_player < 1.6 and not self.caught:
            self.trigger_jumpscare()

    def trigger_jumpscare(self):
        self.caught = True
        if self.snd_chase:
            self.snd_chase.stop()
        try:
            self.snd_jumpscare.play()
        except Exception:
            pass

        # Snap right in front of camera pivot
        if self.target and hasattr(self.target, 'camera_pivot'):
            cam_fwd = self.target.forward
            self.position = self.target.position + cam_fwd * 1.0 + Vec3(0, 0.3, 0)
            self.look_at(self.target)
            self.rotation_y += 180

        if self.on_catch:
            self.on_catch()

    def destroy_bot(self):
        if self.snd_chase:
            self.snd_chase.stop()
        destroy(self.aura_light)
        destroy(self)
