"""
Advanced First-Person Controller for 'Run or dont'
Features:
- Solid non-penetrating multi-ray swept collision on X and Z (zero noclip)
- Anti-stick depenetration: touching a wall NEVER freezes or locks player
- Sprint with all keyboard Shift variants (left, right, generic)
- Stamina system (100 stamina, 12s full sprint, fast regen on walk)
- Momentum slide (C / Ctrl while sprinting): speed boosts to 18 m/s then decays
- Prone crawl (Z) & Crouch (C / Ctrl)
- Q / E corner leaning
- Flashlight toggle (F)
- 3D tactical body visible when looking down
- Footstep, slide, and flashlight audio
"""
import os
import math
import random
from ursina import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class AdvancedPlayer(Entity):
    def __init__(self, start_pos=(0, 0, 0), **kwargs):
        super().__init__(position=start_pos, **kwargs)

        # ── Physical Collision Radius & Heights ──────────────────────────────
        self.player_radius = 0.28  # Collision hull radius (m)
        self.stand_height  = 1.80  # Standing eye level
        self.crouch_height = 1.10  # Crouched eye level
        self.prone_height  = 0.50  # Prone eye level
        self.slide_height  = 0.75  # Slide eye level
        self.cur_height    = self.stand_height

        # ── Camera & Reticle ──────────────────────────────────────────────────
        self.camera_pivot = Entity(parent=self, y=self.stand_height)
        camera.parent = self.camera_pivot
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        camera.fov = 85

        # Minimalist white crosshair dot
        self.reticle = Entity(
            parent=camera.ui,
            model='quad',
            color=color.rgba(255, 255, 255, 160),
            scale=(0.003, 0.003)
        )

        # ── Look Controls ─────────────────────────────────────────────────────
        self.mouse_sensitivity = Vec2(40, 40)
        self.pitch = 0.0
        self.yaw   = 0.0
        self.roll  = 0.0
        self.peek_offset = 0.0

        # ── Speeds (m/s) ──────────────────────────────────────────────────────
        self.walk_speed   = 6.5
        self.sprint_speed = 13.5   # Faster than Nextbot (9.2 m/s) so player CAN outrun it!
        self.crouch_speed = 3.8
        self.prone_speed  = 2.2
        self.slide_speed  = 18.0

        # ── Stamina System ────────────────────────────────────────────────────
        self.max_stamina = 100.0
        self.stamina     = 100.0
        self.stamina_drain_rate = 8.0   # ~12.5 seconds of non-stop sprinting
        self.stamina_regen_rate = 14.0  # Fast recovery when walking/standing

        # ── Movement State ────────────────────────────────────────────────────
        self.velocity    = Vec3(0, 0, 0)
        self.is_sprinting= False
        self.is_crouching= False
        self.is_prone    = False
        self.is_sliding  = False
        self.slide_timer = 0.0
        self.slide_dir   = Vec3(0, 0, 0)

        self.is_grounded = True
        self.vert_vel    = 0.0
        self.gravity     = 24.0
        self.jump_speed  = 7.0

        # ── Dynamic Flashlight (F) ────────────────────────────────────────────
        self.flashlight_on = True
        self.fl = PointLight(
            parent=camera,
            position=(0.25, 0.0, 0.5),
            color=color.hex('#fff8e8')
        )

        # ── True 3D Player Body (Visible when looking down!) ──────────────────
        self.body_rig = Entity(
            parent=self,
            position=(0, 0.05, 0),
            scale=(1.0, 1.0, 1.0),
            model='assets/models/player_body.obj',
            texture='assets/textures/player_body.png',
            color=color.white
        )

        # ── Audio ─────────────────────────────────────────────────────────────
        self.snd_step       = Audio("assets/audio/footstep.wav",   autoplay=False, loop=False, volume=0.5)
        self.snd_slide      = Audio("assets/audio/slide.wav",      autoplay=False, loop=False, volume=0.7)
        self.snd_flashlight = Audio("assets/audio/flashlight.wav", autoplay=False, loop=False, volume=0.6)

        self.step_timer = 0.0
        self.walk_cycle = 0.0

        mouse.locked = True

    # ── Input Handling ────────────────────────────────────────────────────────
    def toggle_flashlight(self):
        self.flashlight_on = not self.flashlight_on
        self.fl.enabled = self.flashlight_on
        try:
            self.snd_flashlight.play()
        except Exception:
            pass

    def input(self, key):
        if key == 'f':
            self.toggle_flashlight()

        if key == 'space' and self.is_grounded and not self.is_sliding and not self.is_prone:
            self.vert_vel = self.jump_speed
            self.is_grounded = False

        if key == 'z':
            self.is_prone = not self.is_prone
            if self.is_prone:
                self.is_sliding = False
                self.is_crouching = False

        # Slide activation: Ctrl or C while sprinting with stamina
        if key in ('left control', 'c'):
            if self.is_sprinting and not self.is_sliding and self.is_grounded and self.stamina > 10:
                self.is_sliding = True
                self.slide_timer = 1.1
                self.stamina -= 12.0
                fwd = self.forward
                self.slide_dir = Vec3(fwd.x, 0, fwd.z).normalized()
                try:
                    self.snd_slide.play()
                except Exception:
                    pass

    # ── Anti-Stick Swept Collision Resolver ───────────────────────────────────
    def _move_axis_safe(self, axis_idx, move_amount):
        """
        Move player along axis (0=X, 2=Z) by move_amount.
        Uses multi-height raycasts to prevent wall noclip.
        Crucially, if player is already touching a surface, it NEVER locks/freezes movement.
        """
        if abs(move_amount) < 0.0001:
            return

        sign = 1.0 if move_amount > 0 else -1.0
        dir_vec = Vec3(0, 0, 0)
        dir_vec[axis_idx] = sign

        req_dist = abs(move_amount) + self.player_radius

        # Ray heights: feet (0.35m), waist (0.95m), chest (1.50m)
        heights = (0.35, 0.95, 1.50) if not self.is_prone else (0.20, 0.40)
        min_hit_dist = 999.0

        for h in heights:
            origin = self.position + Vec3(0, h, 0)
            hit = raycast(
                origin,
                dir_vec,
                distance=req_dist,
                traverse_target=scene,
                ignore=[self, self.body_rig]
            )
            # Only consider genuine blocking hits ahead of movement direction
            if hit.hit and hit.distance > 0.02:
                if hit.distance < min_hit_dist:
                    min_hit_dist = hit.distance

        if min_hit_dist < req_dist:
            # Wall detected: allow movement up to player_radius margin
            allowed = max(0.0, min_hit_dist - self.player_radius - 0.01)
            actual_move = allowed * sign
        else:
            actual_move = move_amount

        if axis_idx == 0:
            self.x += actual_move
        elif axis_idx == 2:
            self.z += actual_move

    # ── Per-Frame Update Loop ─────────────────────────────────────────────────
    def update(self):
        dt = time.dt
        if dt > 0.08:
            dt = 0.08

        # 1. Mouse Look (Pitch, Yaw)
        self.yaw += mouse.velocity[0] * self.mouse_sensitivity.x
        self.pitch -= mouse.velocity[1] * self.mouse_sensitivity.y
        self.pitch = clamp(self.pitch, -88, 88)

        self.rotation_y = self.yaw
        self.camera_pivot.rotation_x = self.pitch

        # 2. Q/E Corner Leaning
        target_roll = 0.0
        target_peek = 0.0
        if held_keys['q']:
            target_roll = 12.0
            target_peek = -0.45
        elif held_keys['e']:
            target_roll = -12.0
            target_peek = 0.45

        self.roll = lerp(self.roll, target_roll, dt * 10.0)
        self.peek_offset = lerp(self.peek_offset, target_peek, dt * 10.0)
        self.camera_pivot.rotation_z = self.roll
        camera.x = self.peek_offset

        # 3. Posture & Height
        self.is_crouching = (held_keys['left control'] or held_keys['c']) and not self.is_sliding

        if self.is_sliding:
            target_h = self.slide_height
        elif self.is_prone:
            target_h = self.prone_height
        elif self.is_crouching:
            target_h = self.crouch_height
        else:
            target_h = self.stand_height

        self.cur_height = lerp(self.cur_height, target_h, dt * 12.0)
        self.camera_pivot.y = self.cur_height

        # 4. Universal Shift Sprint & Stamina Mechanics
        shift_held = (
            held_keys['shift'] or held_keys['left shift'] or held_keys['right shift']
        )
        moving_forward = held_keys['w'] or held_keys['a'] or held_keys['d']

        if shift_held and moving_forward and not self.is_crouching and not self.is_prone and not self.is_sliding and self.stamina > 2.0:
            self.is_sprinting = True
            self.stamina = max(0.0, self.stamina - self.stamina_drain_rate * dt)
        else:
            self.is_sprinting = False
            # Regenerate stamina when not sprinting
            if not self.is_sliding:
                self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen_rate * dt)

        # Speed evaluation
        if self.is_sliding:
            self.slide_timer -= dt
            decay = max(0.0, self.slide_timer / 1.1)
            cur_speed = lerp(self.walk_speed, self.slide_speed, decay)
            if self.slide_timer <= 0:
                self.is_sliding = False
        elif self.is_prone:
            cur_speed = self.prone_speed
        elif self.is_crouching:
            cur_speed = self.crouch_speed
        elif self.is_sprinting:
            cur_speed = self.sprint_speed
        else:
            cur_speed = self.walk_speed

        # Calculate desired movement direction
        if self.is_sliding:
            desired_vel = self.slide_dir * cur_speed
        else:
            raw_input = Vec3(
                (held_keys['d'] - held_keys['a']),
                0,
                (held_keys['w'] - held_keys['s'])
            )
            if raw_input.length() > 0:
                norm_in = raw_input.normalized()
                fwd = Vec3(self.forward.x, 0, self.forward.z).normalized()
                rgt = Vec3(self.right.x, 0, self.right.z).normalized()
                desired_vel = (fwd * norm_in.z + rgt * norm_in.x) * cur_speed
            else:
                desired_vel = Vec3(0, 0, 0)

        # Responsive velocity ramp
        self.velocity.x = lerp(self.velocity.x, desired_vel.x, dt * 18.0)
        self.velocity.z = lerp(self.velocity.z, desired_vel.z, dt * 18.0)

        # 5. Apply Horizontal Movement Separately (X, then Z) for butter-smooth wall-sliding
        self._move_axis_safe(0, self.velocity.x * dt)
        self._move_axis_safe(2, self.velocity.z * dt)

        # 6. Gravity & Ground Clamping
        if not self.is_grounded:
            self.vert_vel -= self.gravity * dt
        self.y += self.vert_vel * dt

        # Downward ground detection ray
        ground_ray = raycast(
            self.position + Vec3(0, 0.6, 0),
            Vec3(0, -1, 0),
            distance=0.75,
            traverse_target=scene,
            ignore=[self, self.body_rig]
        )

        if ground_ray.hit and self.vert_vel <= 0:
            ground_y = ground_ray.world_point.y
            if ground_y >= self.y - 0.25:
                self.y = ground_y
                self.vert_vel = 0.0
                self.is_grounded = True
        else:
            if self.y <= 0.0:
                self.y = 0.0
                self.vert_vel = 0.0
                self.is_grounded = True
            else:
                self.is_grounded = False

        # 7. First-Person 3D Body Animation (Visible when looking down!)
        is_moving = Vec2(self.velocity.x, self.velocity.z).length() > 0.4
        if is_moving and self.is_grounded:
            freq = 13.0 if self.is_sprinting else 8.5
            self.walk_cycle += dt * freq
            self.body_rig.position = (
                math.sin(self.walk_cycle) * 0.03,
                0.05,
                math.cos(self.walk_cycle) * 0.02
            )
            self.step_timer += dt
            step_int = 0.27 if self.is_sprinting else 0.43
            if self.step_timer >= step_int:
                self.step_timer = 0.0
                try:
                    self.snd_step.pitch = 0.9 + random.random() * 0.2
                    self.snd_step.play()
                except Exception:
                    pass
        else:
            self.body_rig.position = (0, 0.05, 0)
            self.step_timer = 0.12

        self.body_rig.scale_y = self.cur_height / self.stand_height
