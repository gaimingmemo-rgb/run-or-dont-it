"""
Minimalist Tactical Radar & Survival Timer for 'Run or dont'
Features:
- Survival Timer on top of screen with millisecond accuracy & distance tracker
- Circular Radar Minimap showing player position/heading and pulsing Nextbot proximity threat
- Zero cluttering control hints on screen for maximum horror immersion
"""
import math
from ursina import *

class MinimapHUD(Entity):
    def __init__(self, player, nextbot, **kwargs):
        super().__init__(parent=camera.ui, **kwargs)
        self.player = player
        self.nextbot = nextbot
        self.elapsed_time = 0.0
        self.is_active = True

        # 1. Top HUD: Survival Timer & Stamina Bar
        self.timer_bg = Entity(
            parent=self,
            position=(0, 0.44),
            scale=(0.34, 0.09),
            model='quad',
            color=color.hex('#0f1216')
        )
        self.timer_text = Text(
            parent=self,
            text="TIME: 00:00.00",
            origin=(0, 0),
            position=(0, 0.46),
            scale=1.1,
            color=color.hex('#f0f5ff'),
            z=-0.01
        )
        self.distance_text = Text(
            parent=self,
            text="THREAT: 50.0m",
            origin=(0, 0),
            position=(0, 0.43),
            scale=0.85,
            color=color.hex('#ff5a5a'),
            z=-0.01
        )

        # Stamina Bar beneath timer
        self.stamina_bg = Entity(
            parent=self,
            position=(0, 0.405),
            scale=(0.32, 0.014),
            model='quad',
            color=color.hex('#141820')
        )
        self.stamina_fill = Entity(
            parent=self,
            position=(0, 0.405, -0.01),
            scale=(0.316, 0.010),
            model='quad',
            color=color.hex('#00e5ff')
        )

        # 2. Minimap / Radar HUD (Top-Right or Bottom-Right)
        radar_x = 0.72
        radar_y = -0.32
        radar_size = 0.28

        self.radar_bg = Entity(
            parent=self,
            position=(radar_x, radar_y),
            scale=(radar_size, radar_size),
            model='circle',
            color=color.hex('#0c1014')
        )
        # Outer Radar Ring
        self.radar_ring = Entity(
            parent=self.radar_bg,
            scale=(1.02, 1.02),
            model='circle',
            color=color.hex('#283c50')
        )
        self.radar_inner_ring = Entity(
            parent=self.radar_bg,
            scale=(0.5, 0.5),
            model='circle',
            color=color.hex('#1e2d3c')
        )

        # Crosshair lines
        self.ch_h = Entity(parent=self.radar_bg, scale=(1.0, 0.02), model='quad', color=color.hex('#465a6e'))
        self.ch_v = Entity(parent=self.radar_bg, scale=(0.02, 1.0), model='quad', color=color.hex('#465a6e'))

        # Center Player Marker (Cyan Triangle/Arrow pointing up)
        self.player_dot = Entity(
            parent=self.radar_bg,
            position=(0, 0, -0.01),
            scale=(0.12, 0.12),
            model='quad',
            color=color.cyan
        )

        # Nextbot Threat Blip (Pulsing Red)
        self.nextbot_blip = Entity(
            parent=self.radar_bg,
            position=(0, 0, -0.02),
            scale=(0.14, 0.14),
            model='circle',
            color=color.red
        )
        
        self.pulse_timer = 0.0
        self.radar_range = 60.0 # meters on radar

    def update(self):
        if not self.is_active:
            return

        dt = time.dt
        if dt > 0.1:
            dt = 0.1

        # 1. Update Survival Timer & Stamina
        self.elapsed_time += dt
        mins = int(self.elapsed_time // 60)
        secs = int(self.elapsed_time % 60)
        millis = int((self.elapsed_time * 100) % 100)
        self.timer_text.text = f"{mins:02d}:{secs:02d}.{millis:02d}"

        if self.player and hasattr(self.player, 'stamina'):
            pct = clamp(self.player.stamina / 100.0, 0.0, 1.0)
            self.stamina_fill.scale_x = pct * 0.316
            # Color transition: Cyan when full, Orange when low, Red when exhausted
            if pct > 0.4:
                self.stamina_fill.color = color.hex('#00e5ff')
            elif pct > 0.15:
                self.stamina_fill.color = color.hex('#ffaa00')
            else:
                self.stamina_fill.color = color.hex('#ff2222')

        # 2. Update Threat Distance & Blip Position
        if self.player and self.nextbot and not self.nextbot.caught:
            dist = self.nextbot.distance_to_player
            self.distance_text.text = f"THREAT: {dist:.1f}m"
            
            # Distance color warning
            if dist > 30:
                self.distance_text.color = color.hex('#50dc78') # Green / Safe
            elif dist > 15:
                self.distance_text.color = color.hex('#ffc832') # Yellow / Approaching
            else:
                self.distance_text.color = color.hex('#ff2828') # Red / Danger!

            # Radar coordinates relative to player's facing direction
            # World offset
            wx = self.nextbot.x - self.player.x
            wz = self.nextbot.z - self.player.z

            # Rotate relative to player yaw
            rad = math.radians(-self.player.rotation_y)
            rx = wx * math.cos(rad) - wz * math.sin(rad)
            rz = wx * math.sin(rad) + wz * math.cos(rad)

            # Map to radar circle [-0.45, 0.45]
            nx = (rx / self.radar_range) * 0.45
            ny = (rz / self.radar_range) * 0.45

            # Clamp within radar circle
            mag = math.sqrt(nx*nx + ny*ny)
            if mag > 0.46:
                nx = (nx / mag) * 0.46
                ny = (ny / mag) * 0.46

            self.nextbot_blip.position = (nx, ny, -0.02)

            # Pulsing effect on nextbot blip
            self.pulse_timer += dt * 6.0
            pulse_scale = 0.12 + 0.05 * math.sin(self.pulse_timer)
            self.nextbot_blip.scale = (pulse_scale, pulse_scale)
        else:
            self.distance_text.text = "THREAT: ELIMINATED"
            self.nextbot_blip.enabled = False

    def stop(self):
        self.is_active = False

    def hide(self):
        self.enabled = False

    def show(self):
        self.enabled = True
