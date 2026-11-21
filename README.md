# RUN OR DONT IT

A nextbot chase horror game. You're alone at night with a flashlight, and IT is coming.

**© 2026 Project Revision / Zarto's Studios. All rights reserved.**
This game is part of the Zartos Studios network, puppeteered by Zarto's Studios. Do not copy, distribute, or modify without written permission from the owner.

---

## What it is

- **Full 3D first-person** horror chase game (Python + Ursina/Panda3D)
- **3 huge detailed maps**: SCHOOL, STORE, CITY
- A **nextbot** that hunts you with real line-of-sight AI, searches when it loses you, and gets faster forever
- Terrifying atmosphere: night, fog, flickering lights, flashlight with battery, heartbeat that ramps with proximity, jumpscare death screen

## Graphics

All textures are **generated procedurally at first launch** (pure Python, no downloads, no assets in the repo) and cached in `assets/textures/`:

| Texture | Used for |
|---|---|
| `floor_tile` | School corridor + classroom floors |
| `concrete` | Store floor, sidewalks, foundations |
| `asphalt` | City streets |
| `brick` | Store + city walls, alley nooks |
| `wall_school` | School walls (painted upper + tile wainscot) |
| `wood` | Desks, benches, shelves, bleachers |
| `metal` | Lockers, shelves, freezers, cars, lamps |
| `locker` | Corridor locker rows |
| `ceiling` | Drop-ceiling panels |
| `blackboard` | Classroom chalkboards (chalk smudges + writing) |
| `bark` | Tree trunks |
| `grass` | Tree canopy + grass patches |
| `building1-3` | City facades with lit/dark window grids |
| `nextbot_face` | The thing that hunts you (384px horror face) |

Delete `assets/textures/` to force a re-bake.

## Props (multi-part, not single cubes)

- **School**: desks with 4 legs + chairs, teacher desks, blackboards with chalk trays, locker rows with vents, gym bleachers + basketball hoop, cafeteria tables + benches
- **Store**: aisle shelves stacked with tinted products, glass-door freezers with interior glow, checkout counters with registers, produce displays
- **City**: 3x3 building blocks with rooftop boxes/antennas/red beacons, plaza fountain, trees with bark trunks + 3-layer canopy, cars with cabins/windshields/wheels/headlights/taillights, street lamps (some flicker), bus stops, benches, hydrants, dumpsters, crosswalks

## Mechanics

| Key | Action |
|---|---|
| WASD | Move |
| SHIFT | Sprint (stamina) |
| SPACE | Jump |
| C | Crouch |
| CTRL | Slide (while sprinting) |
| Q / E | Lean / peek around corners |
| F | Hide in nearby closet/spot (or slip out) |
| T / Right-Click | Flashlight on/off |
| ESC | Pause |

**Hide system:** if the nextbot SEES you enter a hiding spot, it walks up and pulls you out. Break line of sight first!

## Install

```bash
# 1. Requires Python 3.10+
python -m pip install -r requirements.txt

# 2. Run
python main.py
```

First launch bakes textures and sounds into `assets/` — expect a few extra seconds once, then it's instant.

## Custom sounds

Drop your own (properly licensed) audio into `assets/sounds/` — any of these names overrides the generated default:

`ambience.*`, `heartbeat.*`, `chase.*`, `footstep.*`, `slide.*`, `scream.*`, `jumpscare.*`, `hide.*`

Supported: `.mp3`, `.ogg`, `.wav`

## Files

| File | Role |
|---|---|
| `main.py` | Game loop, state machine, escape/exit logic, texture baking |
| `player.py` | Movement, stamina, slide, crouch, peek, hide, flashlight |
| `nextbot.py` | Hunter AI: hunt, search, witness, catch (uses generated face) |
| `maps.py` | School / Store / City builders with detailed multi-part props |
| `texture_gen.py` | Procedural PNG texture factory (15 textures) |
| `ui.py` | Menu, HUD, pause, death & win screens |
| `audio_manager.py` | Sound loader (your files override defaults) |
| `sfx_generator.py` | Procedural default sound synthesis |
| `helpers.py` | Texture loading + light helpers |
| `requirements.txt` | Dependencies |

## Objective

Survive until the **exit unlocks** (per-map timer), then reach the glowing exit pad to escape. The nextbot only gets faster the longer you live.

---

*(c) 2026 Project Revision / Zarto's Studios — all rights reserved.*