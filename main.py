"""
'Run or dont' - Main Game Executable
A high-fidelity First-Person Nextbot Survival Horror Game in Python.
"""
import os
import sys
import time
import math
from pathlib import Path
from ursina import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio")
MODEL_DIR = os.path.join(BASE_DIR, "assets", "models")
TEX_DIR = os.path.join(BASE_DIR, "assets", "textures")

from rev_network import RevNetworkManager, NetworkLobby
from maps import MapBuilder
from player import AdvancedPlayer
from nextbot import Nextbot
from minimap import MinimapHUD
from ursina.shaders import lit_with_shadows_shader

# Initialize Ursina Engine
app = Ursina(
    title="Run or dont",
    borderless=False,
    fullscreen=False,
    size=(1280, 720),
    vsync=True
)

# Enable Dynamic Shadow & PBR Lighting Shader across entire engine
Entity.default_shader = lit_with_shadows_shader

application.asset_folder = Path(BASE_DIR)
window.color = color.hex('#0a0c10')
window.fps_counter.enabled = True

# Sound effects
snd_boot = Audio("assets/audio/boot.wav", autoplay=False, loop=False, volume=0.8)
snd_menu = Audio("assets/audio/menu_ambient.wav", autoplay=False, loop=True, volume=0.55)

# Game State
rev_mgr = RevNetworkManager()
net_lobby = NetworkLobby()
map_builder = MapBuilder()

current_state = "MENU" # MENU, MAP_SELECT, MULTIPLAYER, OPTIONS, IN_GAME, JUMPSCARE
active_player = None
active_nextbot = None
active_hud = None
selected_map_name = "School"

# -------------------------------------------------------------
# 1. MAIN MENU UI & NEXTBOT BILLBOARD
# -------------------------------------------------------------
menu_root = Entity(parent=camera.ui, enabled=True)

# Dark Vignette Menu Backdrop
menu_bg = Entity(parent=menu_root, model='quad', scale=(2.0, 2.0), color=color.hex('#0d0f14'), z=1.0)

# Title & Subtitle
menu_title = Text(
    parent=menu_root,
    text="RUN OR DON'T",
    origin=(0, 0),
    position=(-0.25, 0.35),
    scale=3.2,
    color=color.hex('#ff2222'),
    z=0.0
)
menu_subtitle = Text(
    parent=menu_root,
    text="FIRST-PERSON NEXTBOT SURVIVAL HORROR",
    origin=(0, 0),
    position=(-0.25, 0.28),
    scale=1.1,
    color=color.hex('#8892a0'),
    z=0.0
)

# Rev Network Status Card
rev_card = Entity(
    parent=menu_root,
    position=(-0.25, 0.17),
    scale=(0.58, 0.11),
    model='quad',
    color=color.hex('#121822'),
    z=0.0
)
rev_status_text = Text(
    parent=menu_root,
    text=f"REV NETWORK: CONNECTED\nUser: {rev_mgr.account_name}  |  UID: {rev_mgr.account_id}\nRevNet Core v2.4 (Multiplayer Active)",
    origin=(0, 0),
    position=(-0.25, 0.17),
    scale=0.85,
    color=color.hex('#50b4ff'),
    z=-0.01
)

# Menu Navigation Buttons
btn_play = Button(
    parent=menu_root,
    text="PLAY (SELECT MAP)",
    position=(-0.25, 0.04),
    scale=(0.42, 0.08),
    color=color.hex('#9e1c1c'),
    highlight_color=color.hex('#d62828'),
    z=0.0
)
btn_mp = Button(
    parent=menu_root,
    text="MULTIPLAYER (REV NET)",
    position=(-0.25, -0.06),
    scale=(0.42, 0.08),
    color=color.hex('#1a365d'),
    highlight_color=color.hex('#2b6cb0'),
    z=0.0
)
btn_options = Button(
    parent=menu_root,
    text="CONTROLS & HOW TO PLAY",
    position=(-0.25, -0.16),
    scale=(0.42, 0.08),
    color=color.hex('#222630'),
    highlight_color=color.hex('#343a46'),
    z=0.0
)
btn_quit = Button(
    parent=menu_root,
    text="QUIT GAME",
    position=(-0.25, -0.26),
    scale=(0.42, 0.08),
    color=color.hex('#181a20'),
    highlight_color=color.hex('#5a1a1a'),
    z=0.0
)

# Looming 3D Billboard Nextbot in Menu (Right Side)
menu_bot = Entity(
    parent=menu_root,
    position=(0.42, 0.0, -0.05),
    scale=(0.42, 0.62),
    model='quad',
    texture="assets/textures/nextbot.png",
    double_sided=True,
    color=color.white
)
menu_bot_light = PointLight(position=(1.3, 0.6, 2.5), color=color.hex('#ff2222'))

# -------------------------------------------------------------
# 2. MAP SELECTION MENU
# -------------------------------------------------------------
map_select_root = Entity(parent=camera.ui, enabled=False)
map_sel_bg = Entity(parent=map_select_root, model='quad', scale=(2.0, 2.0), color=color.hex('#0d0f14'), z=1.0)

map_sel_title = Text(
    parent=map_select_root,
    text="SELECT ESCAPE MAP",
    origin=(0, 0),
    position=(0, 0.36),
    scale=2.4,
    color=color.hex('#ffffff'),
    z=0.0
)
map_sel_sub = Text(
    parent=map_select_root,
    text="All rooms and buildings are fully enterable. Outrun the Nextbot.",
    origin=(0, 0),
    position=(0, 0.29),
    scale=1.1,
    color=color.hex('#8892a0'),
    z=0.0
)

btn_map_school = Button(
    parent=map_select_root,
    text="1. SCHOOL\n\nLong Lockered Hallways\nClassrooms 101 & 102\nComputer Lab & Offices",
    position=(-0.42, 0.03),
    scale=(0.36, 0.32),
    color=color.hex('#1c2330'),
    highlight_color=color.hex('#9e1c1c'),
    z=0.0
)
btn_map_store = Button(
    parent=map_select_root,
    text="2. STORE\n\nSupermarket Aisles\nFood & Hardware Racks\nBack Storage Warehouse",
    position=(0, 0.03),
    scale=(0.36, 0.32),
    color=color.hex('#1c2330'),
    highlight_color=color.hex('#9e1c1c'),
    z=0.0
)
btn_map_city = Button(
    parent=map_select_root,
    text="3. CITY\n\nDowntown Crossroads\nDark Alleys & Dumpsters\nEnterable Corner Bodega",
    position=(0.42, 0.03),
    scale=(0.36, 0.32),
    color=color.hex('#1c2330'),
    highlight_color=color.hex('#9e1c1c'),
    z=0.0
)

btn_map_back = Button(
    parent=map_select_root,
    text="BACK TO MAIN MENU",
    position=(0, -0.28),
    scale=(0.32, 0.07),
    color=color.hex('#1e222a'),
    highlight_color=color.hex('#404552'),
    z=0.0
)

# -------------------------------------------------------------
# 3. MULTIPLAYER MENU (REV NETWORK LOBBY)
# -------------------------------------------------------------
mp_root = Entity(parent=camera.ui, enabled=False)
mp_bg = Entity(parent=mp_root, model='quad', scale=(2.0, 2.0), color=color.hex('#0d0f14'), z=1.0)

mp_title = Text(parent=mp_root, text="REV NETWORK MULTIPLAYER", origin=(0, 0), position=(0, 0.35), scale=2.2, color=color.hex('#50b4ff'), z=0.0)
mp_info = Text(
    parent=mp_root,
    text=f"Rev Network Client: {rev_mgr.account_name} ({rev_mgr.account_id})\nIntegration: Bound to local socket & peer relay on port 27015",
    origin=(0, 0),
    position=(0, 0.22),
    scale=1.0,
    color=color.hex('#9eaab8'),
    z=0.0
)

btn_mp_host = Button(parent=mp_root, text="HOST MATCH (REV NET / LAN)", position=(0, 0.06), scale=(0.42, 0.08), color=color.hex('#1a365d'), highlight_color=color.hex('#2b6cb0'), z=0.0)
btn_mp_join = Button(parent=mp_root, text="JOIN MATCH (CONNECT TO 127.0.0.1)", position=(0, -0.05), scale=(0.42, 0.08), color=color.hex('#1a365d'), highlight_color=color.hex('#2b6cb0'), z=0.0)
btn_mp_back = Button(parent=mp_root, text="BACK TO MENU", position=(0, -0.22), scale=(0.32, 0.07), color=color.hex('#1e222a'), highlight_color=color.hex('#404552'), z=0.0)
mp_log_text = Text(parent=mp_root, text="", origin=(0, 0), position=(0, -0.13), scale=1.0, color=color.yellow, z=0.0)

# -------------------------------------------------------------
# 4. OPTIONS & CONTROLS MENU
# -------------------------------------------------------------
options_root = Entity(parent=camera.ui, enabled=False)
opt_bg = Entity(parent=options_root, model='quad', scale=(2.0, 2.0), color=color.hex('#0d0f14'), z=1.0)

opt_title = Text(parent=options_root, text="CONTROLS & SURVIVAL GUIDE", origin=(0, 0), position=(0, 0.35), scale=2.2, color=color.white, z=0.0)
opt_card = Entity(parent=options_root, position=(0, 0.03), scale=(0.82, 0.50), model='quad', color=color.hex('#141820'), z=0.0)
opt_text = Text(
    parent=options_root,
    text=(
        "SURVIVAL CONTROLS:\n\n"
        "- W / A / S / D         : Walk / Run\n"
        "- Left Shift           : High-Speed Sprint\n"
        "- Left Ctrl or C (Sprint) : Momentum Slide (Boost speed & dip low)\n"
        "- Left Ctrl or C (Walk)   : Crouch / Duck\n"
        "- Z                    : Prone Drop (Crawl flat under obstacles)\n"
        "- Q / E                : Lean & Peek Left / Right around corners\n"
        "- F                    : Toggle Dynamic Flashlight\n"
        "- Mouse Look           : Look Around (Look down to see your 3D body!)\n"
        "- Space                : Jump\n"
        "- Escape               : Open / Return to Menu"
    ),
    origin=(0, 0),
    position=(0, 0.03),
    scale=0.9,
    color=color.hex('#e2e8f0'),
    z=-0.01
)
btn_opt_back = Button(parent=options_root, text="BACK TO MENU", position=(0, -0.26), scale=(0.32, 0.07), color=color.hex('#1e222a'), highlight_color=color.hex('#404552'), z=0.0)

# -------------------------------------------------------------
# 5. JUMPSCARE & GAME OVER SCREEN
# -------------------------------------------------------------
jumpscare_root = Entity(parent=camera.ui, enabled=False)
js_bg = Entity(parent=jumpscare_root, model='quad', scale=(2.0, 2.0), color=color.hex('#1a0404'), z=1.0)
js_title = Text(parent=jumpscare_root, text="YOU WERE CAUGHT", origin=(0, 0), position=(0, 0.25), scale=3.2, color=color.hex('#ff1a1a'), z=0.0)
js_time_text = Text(parent=jumpscare_root, text="SURVIVAL TIME: 00:00.00", origin=(0, 0), position=(0, 0.1), scale=1.6, color=color.hex('#f6ad55'), z=0.0)

btn_js_retry = Button(parent=jumpscare_root, text="TRY AGAIN", position=(-0.18, -0.1), scale=(0.3, 0.08), color=color.hex('#9e1c1c'), highlight_color=color.hex('#d62828'), z=0.0)
btn_js_menu = Button(parent=jumpscare_root, text="MAIN MENU", position=(0.18, -0.1), scale=(0.3, 0.08), color=color.hex('#1e222a'), highlight_color=color.hex('#404552'), z=0.0)

# -------------------------------------------------------------
# STATE TRANSITIONS
# -------------------------------------------------------------
def enter_main_menu():
    global current_state
    current_state = "MENU"
    
    menu_root.enabled = True
    map_select_root.enabled = False
    mp_root.enabled = False
    options_root.enabled = False
    jumpscare_root.enabled = False
    
    menu_bot.enabled = True
    menu_bot_light.enabled = True
    
    mouse.locked = False
    camera.parent = scene
    camera.position = (0, 0, 0)
    camera.rotation = (0, 0, 0)

    try:
        snd_menu.play()
    except Exception:
        pass

def enter_map_select():
    global current_state
    current_state = "MAP_SELECT"
    menu_root.enabled = False
    map_select_root.enabled = True
    options_root.enabled = False
    mp_root.enabled = False

def enter_multiplayer():
    global current_state
    current_state = "MULTIPLAYER"
    menu_root.enabled = False
    mp_root.enabled = True
    mp_log_text.text = f"Rev Network Status: {rev_mgr.account_name} ({rev_mgr.account_id})"

def enter_options():
    global current_state
    current_state = "OPTIONS"
    menu_root.enabled = False
    options_root.enabled = True

def start_game(map_choice):
    global current_state, active_player, active_nextbot, active_hud, selected_map_name
    selected_map_name = map_choice
    current_state = "IN_GAME"

    menu_root.enabled = False
    map_select_root.enabled = False
    mp_root.enabled = False
    options_root.enabled = False
    jumpscare_root.enabled = False
    menu_bot.enabled = False
    menu_bot_light.enabled = False

    try:
        snd_menu.stop()
    except Exception:
        pass

    # Build Map
    if map_choice == "School":
        map_builder.build_school()
    elif map_choice == "Store":
        map_builder.build_store()
    else:
        map_builder.build_city()

    if active_player:
        destroy(active_player)
    if active_nextbot:
        active_nextbot.destroy_bot()
    if active_hud:
        destroy(active_hud)

    # Spawn Player
    active_player = AdvancedPlayer(start_pos=map_builder.spawn_point)

    # Spawn Nextbot
    active_nextbot = Nextbot(
        target_player=active_player,
        spawn_pos=map_builder.bot_spawn_point,
        on_catch_callback=on_player_caught
    )

    # HUD
    active_hud = MinimapHUD(player=active_player, nextbot=active_nextbot)

def on_player_caught():
    global current_state
    current_state = "JUMPSCARE"
    mouse.locked = False
    
    if active_hud:
        final_time = active_hud.timer_text.text
        active_hud.stop()
        active_hud.hide()
        js_time_text.text = f"SURVIVAL RECORD: {final_time}"

    jumpscare_root.enabled = True

# -------------------------------------------------------------
# BUTTON BINDINGS
# -------------------------------------------------------------
btn_play.on_click = enter_map_select
btn_mp.on_click = enter_multiplayer
btn_options.on_click = enter_options
btn_quit.on_click = application.quit

btn_map_school.on_click = lambda: start_game("School")
btn_map_store.on_click = lambda: start_game("Store")
btn_map_city.on_click = lambda: start_game("City")
btn_map_back.on_click = enter_main_menu

def host_lobby_action():
    ok, msg = net_lobby.start_host()
    mp_log_text.text = msg
    if ok:
        start_game("City")

def join_lobby_action():
    ok, msg = net_lobby.connect_to_host("127.0.0.1")
    mp_log_text.text = msg
    if ok:
        start_game("City")

btn_mp_host.on_click = host_lobby_action
btn_mp_join.on_click = join_lobby_action
btn_mp_back.on_click = enter_main_menu
btn_opt_back.on_click = enter_main_menu

btn_js_retry.on_click = lambda: start_game(selected_map_name)
btn_js_menu.on_click = enter_main_menu

# -------------------------------------------------------------
# GLOBAL UPDATE
# -------------------------------------------------------------
def input(key):
    if key == 'escape':
        if current_state == "IN_GAME":
            enter_main_menu()
        elif current_state in ["MAP_SELECT", "MULTIPLAYER", "OPTIONS"]:
            enter_main_menu()

def update():
    dt = time.dt

    # Menu Nextbot subtle float
    if current_state == "MENU" and menu_bot:
        menu_bot.y = 0.0 + math.sin(time.time() * 2.5) * 0.03

    if current_state == "IN_GAME" and active_player:
        net_lobby.send_position(rev_mgr.account_id, active_player.x, active_player.y, active_player.z, active_player.rotation_y)

if __name__ == "__main__":
    enter_main_menu()
    app.run()
