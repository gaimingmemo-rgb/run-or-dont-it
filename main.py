# ============================================================
#  RUN OR DONT IT
#  (c) 2026 Project Revision / Zarto's Studios. All rights reserved.
#  Owner-authorized build for the Zartos Studios network.
# ============================================================
from ursina import *

import texture_gen
from audio_manager import AudioManager
from helpers import LightSystem
from maps import build_map, MAP_INFO
from nextbot import Nextbot
from player import Player
from ui import GameUI


class Game(Entity):
    def __init__(self):
        super().__init__()
        self.state = 'menu'            # menu / playing / paused / caught / dead / escaped
        self.current_map = None
        self.world = None
        self.player = None
        self.nextbot = None
        self.lights = LightSystem()
        self.hide_spots = []
        self.map_meta = None
        self.survival_time = 0.0
        self.exit_unlocked_at = 150.0
        self.exit_unlocked = False
        self.exit_pos = None
        self.caught_timer = 0.0

        # bake PNG textures + default sounds BEFORE anything uses them
        texture_gen.ensure_all()
        self.audio = AudioManager()

        window.color = color.black
        scene.fog_color = color.rgb(4, 4, 8)
        scene.fog_density = (10, 70)
        self.lights.ambient(color.rgb(14, 14, 20))

        # keep the UI readable no matter how lighting behaves
        try:
            camera.ui.setLightOff()
        except Exception:
            pass

        self.ui = GameUI(self)
        mouse.locked = False

    # ---------------- lifecycle ----------------
    def cleanup(self):
        self.lights.clear_map_lights()
        self.lights.ambient(color.rgb(14, 14, 20))

        if self.player is not None:
            camera.parent = scene
            camera.position = Vec3(0, 0, 0)
            camera.rotation = (0, 0, 0)
            destroy(self.player)
            self.player = None
        if self.nextbot is not None:
            destroy(self.nextbot)
            self.nextbot = None
        if self.world is not None:
            destroy(self.world)
            self.world = None
        self.hide_spots = []
        self.map_meta = None
        self.audio.stop_all()

    def start(self, map_key):
        if map_key not in MAP_INFO:
            return
        self.cleanup()
        self.current_map = map_key
        self.world = Entity()
        self.map_meta = build_map(self, map_key, self.world)
        scene.fog_density = self.map_meta['fog']

        self.survival_time = 0.0
        self.exit_unlocked = False
        self.exit_unlocked_at = self.map_meta['escape_after']
        self.exit_pos = self.map_meta['exit']

        self.player = Player(self, position=self.map_meta['spawn'])
        self.player.rotation_y = self.map_meta['spawn_look']
        self.nextbot = Nextbot(self, position=self.map_meta['nextbot_spawn'])
        self.nextbot.begin_hunt(self.map_meta['grace'])

        self.ui.show_game()
        self.ui.message('SURVIVE. THE EXIT OPENS LATER.', 4)
        self.audio.ambience.play()
        self.audio.heartbeat.play(volume=0)
        if self.audio.chase:
            self.audio.chase.play(volume=0)
        mouse.locked = True
        self.state = 'playing'

    def to_menu(self):
        self.cleanup()
        self.state = 'menu'
        mouse.locked = False
        scene.fog_density = (10, 70)
        self.ui.build_menu()

    def resume(self):
        if self.state != 'paused':
            return
        self.state = 'playing'
        self.ui.hide_pause()
        mouse.locked = True

    # ---------------- interactions ----------------
    def try_interact(self):
        p = self.player
        best, bd = None, 3.2
        for spot in self.hide_spots:
            d = (Vec3(spot['exit'].x - p.x, 0, spot['exit'].z - p.z)).length()
            if d < bd:
                bd, best = d, spot
        if best is None:
            return
        nb = self.nextbot
        if nb is not None and nb.state == 'hunting':
            dist = (Vec3(nb.x - p.x, 0, nb.z - p.z)).length()
            if dist < 9 and nb._can_see(p):
                nb.witnessed = True
            nb.search_pos = Vec3(p.world_position)
        p.hide(best)
        self.ui.message('Hidden. Press F to slip out.', 2.5)

    def player_caught(self):
        if self.state != 'playing':
            return
        self.state = 'caught'
        self.caught_timer = 0.9
        self.audio.jumpscare.play()
        try:
            camera.shake(duration=0.6, magnitude=0.7)
        except Exception:
            pass
        mouse.locked = False

    def player_escaped(self):
        if self.state != 'playing':
            return
        self.state = 'escaped'
        self.audio.stop_all()
        mouse.locked = False
        self.ui.show_win(self.survival_time)

    # ---------------- frame ----------------
    def update(self):
        if self.state == 'playing':
            dt = time.dt
            self.survival_time += dt

            if not self.exit_unlocked and self.survival_time >= self.exit_unlocked_at:
                self.exit_unlocked = True
                em = (self.map_meta or {}).get('exit_marker')
                if em:
                    em['pad'].color = color.rgb(60, 220, 90)
                    em['beam'].color = color.rgb(80, 255, 120)
                    if em['light'] is not None:
                        self.lights.set_color(em['light'], color.rgb(60, 220, 90))
                self.ui.message('THE EXIT IS OPEN. GO.', 4)

            p, nb = self.player, self.nextbot

            if self.exit_unlocked and self.exit_pos is not None:
                d = (Vec3(self.exit_pos.x - p.x, 0, self.exit_pos.z - p.z)).length()
                if d < 3.4:
                    self.player_escaped()
                    return

            dist = (Vec3(nb.x - p.x, 0, nb.z - p.z)).length()
            closeness = clamp(1.0 - dist / 45.0, 0.0, 1.0)
            if nb.state != 'hunting':
                closeness *= 0.25
            self.audio.set_chase_intensity(closeness)
            self.ui.update_hud()

        elif self.state == 'caught':
            self.caught_timer -= time.dt
            if self.caught_timer <= 0:
                self.state = 'dead'
                self.audio.stop_all()
                self.ui.show_death()

    def input(self, key):
        if key == 'escape':
            if self.state == 'playing':
                self.state = 'paused'
                mouse.locked = False
                self.ui.show_pause()
            elif self.state == 'paused':
                self.resume()


app = Ursina(title="RUN OR DONT IT - (c) 2026 Project Revision / Zarto's Studios")
window.borderless = False
window.fps_counter.enabled = False
window.exit_button.visible = False

game = Game()
app.run()
