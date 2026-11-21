# ============================================================
#  RUN OR DONT IT - player controller
#  (c) 2026 Project Revision / Zarto's Studios. All rights reserved.
# ============================================================
import random

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

from helpers import tune_pointlight


def _held(*names):
    """True if any of the given keys is held (covers ursina key-name variants)."""
    for n in names:
        if held_keys.get(n):
            return True
    return False


class Player(FirstPersonController):
    def __init__(self, game, position=(0, 0, 0)):
        super().__init__(position=position)
        self.game = game
        if not hasattr(self, 'mouse_sensitivity'):
            self.mouse_sensitivity = Vec2(40, 40)
        self.camera_pivot.y = 1.7
        self.base_pivot_y = 1.7
        if getattr(self, 'cursor', None):
            self.cursor.enabled = False

        # movement
        self.speed = 5.2
        self.sprint_speed = 8.6
        self.crouch_speed = 2.7
        self.vy = 0.0
        self.grounded = True

        # mechanics
        self.stamina = 100.0
        self.stamina_locked = False
        self.crouching = False
        self.sliding = 0.0
        self.slide_cooldown = 0.0
        self.leaning = 0.0
        self.step_dist = 0.0
        self.sprinting = False

        # hiding
        self.hidden = False
        self.hide_spot = None
        self._saved_pos = None

        # flashlight
        self.battery = 100.0
        self.flashlight_on = True
        self.flashlight = None
        try:
            from ursina.lights import PointLight
            self.flashlight = PointLight(parent=camera, color=color.rgb(255, 248, 220))
            tune_pointlight(self.flashlight)
            game.lights.append(self.flashlight)
        except Exception:
            self.flashlight = None

    # ---------------- movement ----------------
    def _move(self, delta):
        if delta.length() < 1e-6:
            return
        origin = self.world_position + Vec3(0, 0.5, 0)
        hit = raycast(origin=origin, direction=delta.normalized(),
                      distance=delta.length() + 0.5, ignore=(self,))
        if not hit.hit:
            self.position += delta
            self.step_dist += delta.length()
            return
        # slide along the wall we hit
        n = hit.normal
        slide = delta - n * delta.dot(n)
        if slide.length() > 1e-4:
            hit2 = raycast(origin=origin, direction=slide.normalized(),
                          distance=slide.length() + 0.4, ignore=(self,))
            if not hit2.hit:
                self.position += slide
                self.step_dist += slide.length()

    def update(self):
        g = self.game
        dt = time.dt

        # mouse look (also works while hiding - peek out of the closet)
        if mouse.locked:
            self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]
            self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
            self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -85, 85)

        if g.state != 'playing':
            return
        if self.hidden:
            self.camera_pivot.y = lerp(self.camera_pivot.y, 0.95, dt * 10)
            return

        # timers
        if self.slide_cooldown > 0:
            self.slide_cooldown -= dt
        if self.sliding > 0:
            self.sliding = max(0.0, self.sliding - dt)

        # wish direction
        fwd = Vec3(camera.forward.x, 0, camera.forward.z).normalized()
        right = Vec3(camera.right.x, 0, camera.right.z).normalized()
        move = Vec3(0, 0, 0)
        if held_keys['w']:
            move += fwd
        if held_keys['s']:
            move -= fwd
        if held_keys['d']:
            move += right
        if held_keys['a']:
            move -= right
        moving = move.length() > 0.01
        if moving:
            move = move.normalized()

        self.crouching = _held('c') and self.grounded and self.sliding <= 0

        # sprint + stamina
        self.sprinting = False
        if _held('shift', 'left shift', 'right shift') and moving \
                and not self.crouching and not self.stamina_locked and self.stamina > 0:
            self.sprinting = True
            self.stamina = max(0.0, self.stamina - 15 * dt)
            if self.stamina <= 0:
                self.stamina_locked = True
        else:
            self.stamina = min(100.0, self.stamina + 9 * dt)
            if self.stamina > 22:
                self.stamina_locked = False

        # slide (only from a sprint)
        if _held('left control', 'left ctrl', 'control') and self.grounded \
                and self.sprinting and self.sliding <= 0 and self.slide_cooldown <= 0:
            self.sliding = 0.6
            self.slide_cooldown = 1.7
            g.audio.slide.play()

        # speed
        if self.sliding > 0:
            speed = 5 + 13 * (self.sliding / 0.6)
        elif self.crouching:
            speed = self.crouch_speed
        elif self.sprinting:
            speed = self.sprint_speed
        else:
            speed = self.speed

        self._move(move * speed * dt)

        # gravity / jump
        ground = raycast(origin=self.world_position + Vec3(0, 0.5, 0),
                         direction=Vec3(0, -1, 0), distance=2.0, ignore=(self,))
        if self.vy <= 0 and ground.hit and ground.distance <= 0.55:
            self.y = ground.world_point.y
            self.vy = 0.0
            self.grounded = True
        else:
            self.grounded = False
            self.vy -= 26 * dt
            self.y += self.vy * dt
        if _held('space') and self.grounded:
            self.vy = 8.2
            self.grounded = False

        # safety net: fell out of the world
        if self.y < -12 and g.map_meta:
            self.position = g.map_meta['spawn']

        # clamp to map bounds
        if g.map_meta:
            minx, maxx, minz, maxz = g.map_meta['bounds']
            self.x = clamp(self.x, minx, maxx)
            self.z = clamp(self.z, minz, maxz)

        # footsteps
        if self.grounded and self.step_dist > (2.4 if self.sprinting else 1.9):
            self.step_dist = 0.0
            g.audio.footstep.play(volume=(0.55 if self.sprinting else 0.35))

        # camera: crouch / slide height + lean
        target_y = self.base_pivot_y
        if self.sliding > 0:
            target_y = 0.65
        elif self.crouching:
            target_y = 1.0
        self.camera_pivot.y = lerp(self.camera_pivot.y, target_y, dt * 10)

        target_lean = 0.0
        if _held('q'):
            target_lean = -1
        elif _held('e'):
            target_lean = 1
        self.leaning = lerp(self.leaning, target_lean, dt * 12)
        self.camera_pivot.x = self.leaning * 0.75
        camera.rotation = (0, 0, -self.leaning * 6)

        # flashlight battery + flicker
        if self.flashlight_on:
            self.battery = max(0.0, self.battery - dt * 0.55)
            if self.battery <= 0:
                self.flashlight_on = False
        if self.flashlight:
            flicker_on = self.flashlight_on
            if flicker_on and self.battery < 25 and random.random() < 0.10:
                flicker_on = random.random() > 0.4
            self.flashlight.enabled = flicker_on

    # ---------------- hiding ----------------
    def hide(self, spot):
        self.hidden = True
        self.hide_spot = spot
        self._saved_pos = Vec3(self.position)
        self.position = spot['pos']
        self.vy = 0.0
        self.game.audio.hide.play()

    def unhide(self):
        self.hidden = False
        self.hide_spot = None
        nb = self.game.nextbot
        if nb is not None:
            nb.witnessed = False
            nb.search_pos = Vec3(self.position)
        if self._saved_pos is not None:
            self.position = self._saved_pos
            self._saved_pos = None

    # ---------------- keys ----------------
    def input(self, key):
        g = self.game
        if g.state != 'playing':
            return
        if key == 't' or key == 'right mouse down':
            if self.battery > 0:
                self.flashlight_on = not self.flashlight_on
        elif key == 'f':
            if self.hidden:
                self.unhide()
                g.ui.message('You slip back out...', 1.5)
            else:
                g.try_interact()
