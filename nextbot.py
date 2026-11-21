# ============================================================
#  RUN OR DONT IT - the NEXTBOT
#  (c) 2026 Project Revision / Zarto's Studios. All rights reserved.
# ============================================================
import math
import random

from ursina import *

from helpers import tune_pointlight


def _rot_y(v, deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return Vec3(v.x * c + v.z * s, 0, -v.x * s + v.z * c).normalized()


class Nextbot(Entity):
    """A billboard nextbot: it hunts, it searches, it gets faster forever."""

    def __init__(self, game, position=(0, 0, 0)):
        super().__init__(position=position)
        self.game = game
        self.state = 'dormant'      # dormant -> waiting -> hunting
        self.wait_time = 10.0
        self.base_speed = 6.8
        self.max_speed = 15.5
        self.speed = self.base_speed
        self.elapsed = 0.0
        self.witnessed = False      # saw you go into a hiding spot
        self.search_pos = None
        self.lurk_time = 0.0
        self.t = 0.0
        self.next_scream = 0.0

        self.root = Entity(parent=self)
        self.body = Entity(parent=self.root, model='quad', billboard=True,
                           scale=(2.0, 2.0), color=color.rgb(10, 10, 12),
                           double_sided=True)
        self.eye_l = Entity(parent=self.body, model='circle', color=color.rgb(255, 40, 40),
                            position=(-0.16, 0.22, -0.01), scale=(0.11, 0.05))
        self.eye_r = Entity(parent=self.body, model='circle', color=color.rgb(255, 40, 40),
                            position=(0.16, 0.22, -0.01), scale=(0.11, 0.05))
        self.mouth = Entity(parent=self.body, model='circle', color=color.rgb(235, 235, 235),
                            position=(0, -0.16, -0.01), scale=(0.52, 0.15))
        self.light = None
        try:
            from ursina.lights import PointLight
            self.light = PointLight(parent=self.root, color=color.rgb(110, 25, 25))
            tune_pointlight(self.light)
            game.lights.append(self.light)
        except Exception:
            self.light = None

    def begin_hunt(self, wait=10.0):
        self.state = 'waiting'
        self.wait_time = wait

    def _can_see(self, p):
        if p.hidden:
            return False
        origin = self.world_position + Vec3(0, 1.4, 0)
        target = p.world_position + Vec3(0, 1.4, 0)
        d = target - origin
        if d.length() < 0.6:
            return True
        hit = raycast(origin=origin, direction=d.normalized(), distance=d.length(),
                      ignore=(self, self.root))
        return not hit.hit

    def update(self):
        g = self.game
        if g.state != 'playing':
            return
        dt = time.dt
        self.t += dt
        p = g.player

        if self.state == 'dormant':
            return
        if self.state == 'waiting':
            self.wait_time -= dt
            if self.wait_time <= 0:
                self.state = 'hunting'
                g.audio.scream.play()
                g.ui.message('IT IS AWAKE. RUN.', 3)
            return

        # it only ever gets faster
        self.elapsed += dt
        self.speed = min(self.base_speed + self.elapsed * 0.08, self.max_speed)

        dist = Vec3(p.x - self.x, 0, p.z - self.z).length()
        has_los = self._can_see(p)

        # ---- catch checks
        if p.hidden:
            if self.witnessed and dist < 2.4:
                self.lurk_time += dt
                if self.lurk_time > 2.6:
                    g.player_caught()
                    return
            else:
                self.lurk_time = max(0.0, self.lurk_time - dt)
        else:
            if dist < 1.7:
                g.player_caught()
                return

        # ---- pick a goal
        if p.hidden:
            if self.witnessed:
                goal = Vec3(p.world_position)          # walk right up to your hiding spot
            else:
                if self.search_pos is None:
                    self.search_pos = Vec3(self.x + random.uniform(-25, 25), 0,
                                           self.z + random.uniform(-25, 25))
                goal = self.search_pos
        elif has_los:
            self.search_pos = Vec3(p.world_position)
            self.witnessed = False
            goal = Vec3(p.world_position)
        else:
            goal = self.search_pos if self.search_pos is not None else Vec3(p.world_position)

        # ---- move with obstacle steering
        to_goal = Vec3(goal.x - self.x, 0, goal.z - self.z)
        if to_goal.length() > 0.05:
            d = to_goal.normalized()
            moved = False
            for ang in (0, 30, -30, 60, -60, 95, -95):
                cand = _rot_y(d, ang)
                hit = raycast(origin=self.world_position + Vec3(0, 0.7, 0),
                              direction=cand, distance=2.6, ignore=(self, self.root))
                if not hit.hit:
                    self.position += cand * self.speed * dt
                    moved = True
                    break
            if not moved:
                self.position += d * self.speed * 0.35 * dt
        else:
            if p.hidden and not self.witnessed:
                self.search_pos = None                 # lost you - wander
            elif not p.hidden and not has_los:
                self.search_pos = Vec3(self.x + random.uniform(-25, 25), 0,
                                       self.z + random.uniform(-25, 25))

        # ---- idle screams when it is close
        if dist < 30 and self.t > self.next_scream:
            g.audio.scream.play(volume=clamp(1 - dist / 35.0, 0.15, 0.9))
            self.next_scream = self.t + random.uniform(6, 13)

        # ---- visuals: bobbing, glitch jitter, flickering eyes
        self.root.y = 1.15 + math.sin(self.t * 9) * 0.07
        self.root.x = random.uniform(-0.05, 0.05) if self.speed > 10 else 0
        flick = 0.65 + 0.35 * math.sin(self.t * 13)
        ec = color.rgb(255, int(20 + 40 * flick), int(20 + 40 * flick))
        self.eye_l.color = ec
        self.eye_r.color = ec
