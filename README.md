# RUN OR DON'T

A high-fidelity 3D First-Person Nextbot Survival Horror Game built in Python with Ursina & OpenGL.

## Features
- **Cinematic Bootup Sequence**: CRT terminal boot animation with system diagnostics & hardware sound sweeps.
- **Dynamic 3D Main Menu**: Atmospheric copyright-free high-passed ambient audio, looming 3D Nextbot entity with red glowing eyes, interactive Play, Map Select, Multiplayer, and Options menus.
- **True First-Person Body Simulation**: When looking down, you see your full 3D body (hoodie torso, tactical cargo pants, and running sneakers with stride animations).
- **Advanced Movement System**:
  - `W / A / S / D` - Movement
  - `Left Shift` - Fast Sprint
  - `Left Ctrl` or `C` (while sprinting) - High-Speed Momentum Slide with decaying friction physics
  - `Left Ctrl` or `C` (while walking) - Stealth Crouch / Duck
  - `Z` - Prone / Drop to crawl under low obstacles
  - `Q / E` - Dynamic Camera Peek & Lean around corners
  - `F` - Toggle dynamic 3D Flashlight
  - `Space` - Jump
- **Minimalist Tactical HUD**:
  - Millisecond-precision Survival Timer at the top of the screen
  - Live Threat Distance tracking with color-coded proximity warnings
  - Top-tier Circular Radar Minimap showing player heading and pulsing red Nextbot proximity (no screen-cluttering control text during rounds)
- **3 Massive Enterable Maps**:
  1. **School**: Corridors with lockers, Classroom 101, Classroom 102 with rows of desks/chairs/chalkboard, Computer Lab, Principal's office.
  2. **Store**: Supermarket department floor with multi-tier grocery aisles, cashier counters, warehouse backroom with pallet crates.
  3. **City**: Downtown crossroads with asphalt roads and sidewalks, streetlights, alley dumpsters, enterable bodega, enterable tenement apartment lobby, and warehouse.
- **Relentless Nextbot AI**:
  - High-speed pursuit pathing tuned slightly faster than standard player run speed (accelerates dynamically).
  - Proximity chase music that escalates the closer it gets.
  - Terrifying jumpscare trigger on contact with screen glitching, camera face-hug, and scream audio.
- **Rev Network Integration & Multiplayer**:
  - Automatic system scan for Rev Network client.
  - Automatically binds your community account profile (`ZarTo` / account ID).
  - Built-in UDP socket lobby hosting and joining for LAN / Rev Network direct servers.
- **Desktop Assets**:
  - All 3D OBJ models and custom high-resolution textures are exported into `C:\Users\ZarTo\Desktop\RunOrDont_Models`.
  - Convenient 1-click launcher created directly on your desktop: `Run_or_dont.bat`.

## How to Run:
Double-click `Run_or_dont.bat` on your Desktop, or run from terminal:
```bash
python main.py
```
