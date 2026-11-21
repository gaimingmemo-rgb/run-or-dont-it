# ============================================================
#  RUN OR DONT IT - menus, HUD, death / win screens
#  (c) 2026 Project Revision / Zarto's Studios. All rights reserved.
# ============================================================
from ursina import *

from maps import MAP_INFO


def _fmt(t):
    return f'{int(t // 60):02d}:{int(t % 60):02d}'


class GameUI:
    def __init__(self, game):
        self.game = game
        self.menu_root = None
        self.hud = None
        self.death_root = None
        self.pause_root = None
        self.win_root = None
        self.msg_time = 0.0
        self.build_menu()

    @staticmethod
    def _clear(root):
        if root:
            for c in list(root.children):
                destroy(c)
            destroy(root)

    def _hide_all(self):
        for attr in ('menu_root', 'hud', 'death_root', 'pause_root', 'win_root'):
            self._clear(getattr(self, attr))
            setattr(self, attr, None)

    def message(self, text, duration=2.5):
        if self.hud is not None:
            self.msg_text.text = text
            self.msg_time = duration

    # ---------------- main menu ----------------
    def build_menu(self):
        self._hide_all()
        root = self.menu_root = Entity(parent=camera.ui)
        Text('RUN OR DONT IT', parent=root, y=0.34, origin=(0, 0), scale=2.8,
             color=color.rgb(215, 35, 35))
        Text('a Zartos Studios network production', parent=root, y=0.27,
             origin=(0, 0), scale=0.85, color=color.rgb(150, 150, 160))
        for i, (key, info) in enumerate(MAP_INFO.items()):
            b = Button(parent=root, text=info['label'], scale=(0.42, 0.075),
                       position=(0, 0.08 - i * 0.11), color=color.rgb(72, 22, 22))
            b.on_click = Func(self.game.start, key)
        Text('WASD move | SHIFT sprint | SPACE jump | C duck | CTRL slide | '
             'Q/E peek | F hide | T or Right-Click flashlight | ESC pause',
             parent=root, y=-0.28, origin=(0, 0), scale=0.72, color=color.rgb(170, 170, 180))
        Text("(c) 2026 Project Revision / Zarto's Studios. All rights reserved.",
             parent=root, y=-0.43, origin=(0, 0), scale=0.7, color=color.rgb(120, 120, 130))

    # ---------------- in-game HUD ----------------
    def show_game(self):
        self._hide_all()
        root = self.hud = Entity(parent=camera.ui)
        Entity(parent=root, model='quad', origin=(-0.5, -0.5), color=color.rgb(25, 25, 30),
               scale=(0.30, 0.035), position=(-0.48, -0.455))
        self.stam_fill = Entity(parent=root, model='quad', origin=(-0.5, -0.5),
                               color=color.rgb(225, 180, 40), scale=(0.29, 0.023),
                               position=(-0.475, -0.450))
        Entity(parent=root, model='quad', origin=(-0.5, -0.5), color=color.rgb(25, 25, 30),
               scale=(0.30, 0.035), position=(-0.48, -0.415))
        self.bat_fill = Entity(parent=root, model='quad', origin=(-0.5, -0.5),
                               color=color.rgb(120, 180, 230), scale=(0.29, 0.023),
                               position=(-0.475, -0.410))
        self.timer_text = Text('', parent=root, y=0.045, origin=(0, 0), scale=1.3,
                               color=color.rgb(220, 70, 70))
        self.hint_text = Text('', parent=root, y=-0.32, origin=(0, 0), scale=0.95,
                              color=color.rgb(235, 235, 240))
        self.msg_text = Text('', parent=root, y=0.16, origin=(0, 0), scale=1.5,
                             color=color.rgb(230, 40, 40))

    def update_hud(self):
        g = self.game
        if self.hud is None or g.state != 'playing':
            return
        p = g.player
        self.stam_fill.scale_x = 0.29 * max(0.0, p.stamina) / 100.0
        self.stam_fill.color = color.rgb(225, 90, 40) if p.stamina_locked else color.rgb(225, 180, 40)
        self.bat_fill.scale_x = 0.29 * max(0.0, p.battery) / 100.0

        if g.exit_unlocked:
            self.timer_text.text = 'EXIT OPEN - RUN'
            self.timer_text.color = color.rgb(80, 240, 110)
        else:
            self.timer_text.text = 'EXIT SEALED  ' + _fmt(max(0.0, g.exit_unlocked_at - g.survival_time))

        hint = ''
        if p.hidden:
            hint = 'F - slip out quietly'
        else:
            best, bd = None, 3.2
            for spot in g.hide_spots:
                d = (Vec3(spot['exit'].x - p.x, 0, spot['exit'].z - p.z)).length()
                if d < bd:
                    bd, best = d, spot
            if best is not None:
                hint = 'F - hide in ' + best['label'].upper()
        if p.battery < 25 and p.flashlight_on:
            hint = hint + '   (battery low)'
        self.hint_text.text = hint

        if self.msg_time > 0:
            self.msg_time -= time.dt
            if self.msg_time <= 0:
                self.msg_text.text = ''

    # ---------------- pause ----------------
    def show_pause(self):
        self._clear(self.pause_root)
        root = self.pause_root = Entity(parent=camera.ui)
        Entity(parent=root, model='quad', scale=(3, 1.2), color=color.rgba(0, 0, 0, 140))
        Text('PAUSED', parent=root, y=0.2, origin=(0, 0), scale=2, color=color.rgb(220, 220, 230))
        b1 = Button(parent=root, text='RESUME', scale=(0.36, 0.07),
                    position=(0, -0.02), color=color.rgb(60, 60, 75))
        b1.on_click = Func(self.game.resume)
        b2 = Button(parent=root, text='QUIT TO MENU', scale=(0.36, 0.07),
                    position=(0, -0.12), color=color.rgb(60, 60, 75))
        b2.on_click = Func(self.game.to_menu)

    def hide_pause(self):
        self._clear(self.pause_root)
        self.pause_root = None

    # ---------------- death ----------------
    def show_death(self):
        self._hide_all()
        root = self.death_root = Entity(parent=camera.ui)
        Entity(parent=root, model='quad', scale=(3, 1.2), color=color.rgba(120, 0, 0, 150))
        face = Entity(parent=root, model='quad', scale=(1.5, 1.5), position=(0, 0.06),
                      color=color.rgb(8, 8, 10))
        Entity(parent=face, model='circle', color=color.rgb(255, 40, 40),
               position=(-0.17, 0.18, -0.01), scale=(0.16, 0.075))
        Entity(parent=face, model='circle', color=color.rgb(255, 40, 40),
               position=(0.17, 0.18, -0.01), scale=(0.16, 0.075))
        Entity(parent=face, model='circle', color=color.rgb(240, 240, 240),
               position=(0, -0.2, -0.01), scale=(0.62, 0.2))
        Text('IT CAUGHT YOU', parent=root, y=-0.32, origin=(0, 0), scale=2.2,
             color=color.rgb(255, 60, 60))
        b1 = Button(parent=root, text='RUN AGAIN', scale=(0.36, 0.07),
                    position=(0, -0.42), color=color.rgb(90, 20, 20))
        b1.on_click = Func(self.game.start, self.game.current_map)
        b2 = Button(parent=root, text='MAIN MENU', scale=(0.36, 0.07),
                    position=(0, -0.52), color=color.rgb(60, 60, 70))
        b2.on_click = Func(self.game.to_menu)

    # ---------------- win ----------------
    def show_win(self, survived):
        self._hide_all()
        root = self.win_root = Entity(parent=camera.ui)
        Entity(parent=root, model='quad', scale=(3, 1.2), color=color.rgba(0, 20, 0, 170))
        Text('YOU ESCAPED', parent=root, y=0.18, origin=(0, 0), scale=2.4,
             color=color.rgb(90, 255, 120))
        Text('survived  ' + _fmt(survived), parent=root, y=0.06, origin=(0, 0),
             scale=1.1, color=color.rgb(220, 220, 230))
        b1 = Button(parent=root, text='RUN AGAIN', scale=(0.36, 0.07),
                    position=(0, -0.12), color=color.rgb(20, 80, 30))
        b1.on_click = Func(self.game.start, self.game.current_map)
        b2 = Button(parent=root, text='MAIN MENU', scale=(0.36, 0.07),
                    position=(0, -0.22), color=color.rgb(60, 60, 70))
        b2.on_click = Func(self.game.to_menu)
