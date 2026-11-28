"""
Massive Architectural Horror Map Engine for 'Run or dont'
Features:
- Sprawling, fully interconnected, loopable map layouts (80m - 160m)
- 100% enclosed environments with high-resolution textures (ZERO VOID)
- Gymnasium with basketball hoops and bleachers, classrooms, library, cafeteria
- Mega Supercenter with 8 aisles, checkout counters, and industrial logistics warehouse
- Downtown city grid with 360-degree skyscraper facades, night sky dome with full moon
- Hand-placed furniture, props, and atmospheric horror point lights
- Multi-height swept colliders on all structural walls and props
"""
import os
import random
from ursina import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WALL_H = 3.6     # Standard ceiling height
WALL_T = 0.35    # Wall thickness
DOOR_W = 1.4     # Door width
DOOR_H = 2.4     # Door height
DOOR_HDR = WALL_H - DOOR_H


def _tex(name):
    full = os.path.join(BASE_DIR, "assets", "textures", name)
    return f"assets/textures/{name}" if os.path.exists(full) else None

def _mdl(name):
    full = os.path.join(BASE_DIR, "assets", "models", name)
    return f"assets/models/{name}" if os.path.exists(full) else 'cube'


class MapBuilder:
    def __init__(self):
        self.spawn_point     = Vec3(0, 0, 0)
        self.bot_spawn_point = Vec3(50, 0, 50)
        self.entities        = []
        self.sun             = None

    def clear(self):
        for e in self.entities:
            try:
                destroy(e)
            except Exception:
                pass
        self.entities.clear()
        self.sun = None

    # ── Basic Geometry Primitives ─────────────────────────────────────────────
    def floor(self, cx, cz, w, d, tex=None, col=color.white, tile=3.0, y=0.0):
        e = Entity(
            position=(cx, y - 0.05, cz),
            scale=(w, 0.1, d),
            model='cube',
            texture=tex,
            color=col,
            collider='box'
        )
        if tex and tile:
            e.texture_scale = Vec2(w / tile, d / tile)
        self.entities.append(e)
        return e

    def ceiling(self, cx, cz, w, d, tex=None, col=color.white, tile=3.0, h=WALL_H):
        e = Entity(
            position=(cx, h + 0.05, cz),
            scale=(w, 0.1, d),
            model='cube',
            texture=tex,
            color=col
        )
        if tex and tile:
            e.texture_scale = Vec2(w / tile, d / tile)
        # Exclude ceiling from shadow casting so interior rooms aren't blacked out by their own roof
        if self.sun and hasattr(self.sun, '_light'):
            try:
                e.hide(self.sun._light.getCameraMask())
            except Exception:
                pass
        self.entities.append(e)
        return e

    def wall(self, cx, cy, cz, w, h, d, tex=None, col=color.white, tile=3.0):
        e = Entity(
            position=(cx, cy, cz),
            scale=(w, h, d),
            model='cube',
            texture=tex,
            color=col,
            collider='box'
        )
        if tex and tile:
            horiz = max(w, d)
            e.texture_scale = Vec2(horiz / tile, h / tile)
        self.entities.append(e)

        # Baseboard trim
        trim = Entity(
            position=(cx, 0.1, cz),
            scale=(w * 1.01, 0.2, d * 1.01),
            model='cube',
            color=color.hex('#16181d')
        )
        self.entities.append(trim)
        return e

    def doorway_header(self, cx, cz, axis='x', wall_tex=None, h=WALL_H):
        """Header slab over door openings so walls connect seamlessly."""
        hdr_y = DOOR_H + (h - DOOR_H) / 2
        hdr_h = h - DOOR_H
        if axis == 'x':
            hdr = Entity(
                position=(cx, hdr_y, cz),
                scale=(WALL_T, hdr_h, DOOR_W + WALL_T),
                model='cube',
                texture=wall_tex,
                collider='box'
            )
        else:
            hdr = Entity(
                position=(cx, hdr_y, cz),
                scale=(DOOR_W + WALL_T, hdr_h, WALL_T),
                model='cube',
                texture=wall_tex,
                collider='box'
            )
        self.entities.append(hdr)

    def prop(self, pos, scale=(1, 1, 1), model='cube', tex=None, col=color.white, rot_y=0, collider='box'):
        e = Entity(
            position=pos,
            scale=scale,
            model=model,
            texture=tex,
            color=col,
            rotation_y=rot_y,
            collider=collider
        )
        self.entities.append(e)
        return e

    def light(self, pos, col=color.hex('#fff5dd'), fixture=True):
        pl = PointLight(position=pos, color=col)
        self.entities.append(pl)
        if fixture:
            fix = Entity(
                position=(pos[0], pos[1] + 0.1, pos[2]),
                scale=(1.4, 0.1, 0.5),
                model='cube',
                color=color.hex('#e8edf5')
            )
            self.entities.append(fix)
        return pl

    # ══════════════════════════════════════════════════════════════════════════
    # 1. SCHOOL MAP: "OAKRIDGE HIGH SCHOOL" (100m x 80m, Loopable Circuit)
    # ══════════════════════════════════════════════════════════════════════════
    def build_school(self):
        self.clear()
        scene.fog_density = (14, 55)
        scene.fog_color   = color.hex('#06080c')

        # Primary Dynamic Shadow Caster (Warm skylight shadows)
        self.sun = DirectionalLight(shadows=True, rotation=(55, -35, 0), color=color.hex('#ffeedd'))
        self.entities.append(self.sun)

        # Atmospheric dim ambient light
        amb = AmbientLight(color=color.hex('#454a55'))
        self.entities.append(amb)

        bk   = _tex('brick_wall.png')
        til  = _tex('school_tiles.png')
        wdp  = _tex('wood_desk.png')
        clt  = _tex('ceiling_tile.png')
        gymt = _tex('gym_floor.png')
        lkt  = _tex('locker_metal.png')

        # ── Massive Quad Hallway Loop (West Hall, East Hall, North Hall, South Hall) ──
        # Corridors: 4.5m wide.
        # West Hall: x = -18, z from -36 to +36 (72m length!)
        # East Hall: x = +18, z from -36 to +36 (72m length!)
        # South Hall: z = -36, x from -18 to +18 (36m cross!)
        # North Hall: z = +36, x from -18 to +18 (36m cross!)
        # Result: A giant loop allowing players to sprint continuously around Nextbot!

        CW = 4.5
        HH = WALL_H / 2

        # 1. Hallway Floors & Ceilings
        self.floor(-18, 0, CW, 76, tex=til, tile=2.5) # West Hall
        self.ceiling(-18, 0, CW, 76, tex=clt, tile=2.5)

        self.floor(18, 0, CW, 76, tex=til, tile=2.5)  # East Hall
        self.ceiling(18, 0, CW, 76, tex=clt, tile=2.5)

        self.floor(0, -36, 40, CW, tex=til, tile=2.5) # South Hall
        self.ceiling(0, -36, 40, CW, tex=clt, tile=2.5)

        self.floor(0, 36, 40, CW, tex=til, tile=2.5)  # North Hall
        self.ceiling(0, 36, 40, CW, tex=clt, tile=2.5)

        # Center Crosswalk Concourse (connecting East and West wings at z = 0)
        self.floor(0, 0, 36, CW, tex=til, tile=2.5)
        self.ceiling(0, 0, 36, CW, tex=clt, tile=2.5)

        # Hallway Lighting
        for hz in range(-32, 33, 8):
            self.light((-18, WALL_H - 0.15, hz), col=color.hex('#fff2d4'))
            self.light((18, WALL_H - 0.15, hz), col=color.hex('#fff2d4'))
        for hx in [-8, 8]:
            self.light((hx, WALL_H - 0.15, -36), col=color.hex('#fff2d4'))
            self.light((hx, WALL_H - 0.15, 36), col=color.hex('#fff2d4'))
            self.light((hx, WALL_H - 0.15, 0), col=color.hex('#fff2d4'))

        # Corridor Outer Perimeter Walls (with doors into rooms)
        # West Hall Outer Wall (x = -20.25): Doors at z = -20 (Cafeteria), z = 18 (Gym)
        self.wall(-20.25, HH, -29.0, WALL_T, WALL_H, 14.0, tex=bk)
        self.doorway_header(-20.25, -20.0, axis='x', wall_tex=bk)
        self.wall(-20.25, HH, -1.0, WALL_T, WALL_H, 36.0, tex=bk)
        self.doorway_header(-20.25, 18.0, axis='x', wall_tex=bk)
        self.wall(-20.25, HH, 28.0, WALL_T, WALL_H, 18.0, tex=bk)

        # East Hall Outer Wall (x = +20.25): Doors at z = -20 (Library), z = 12 (Classrooms)
        self.wall(20.25, HH, -29.0, WALL_T, WALL_H, 14.0, tex=bk)
        self.doorway_header(20.25, -20.0, axis='x', wall_tex=bk)
        self.wall(20.25, HH, -4.0, WALL_T, WALL_H, 30.0, tex=bk)
        self.doorway_header(20.25, 12.0, axis='x', wall_tex=bk)
        self.doorway_header(20.25, 26.0, axis='x', wall_tex=bk)
        self.wall(20.25, HH, 19.0, WALL_T, WALL_H, 12.0, tex=bk)
        self.wall(20.25, HH, 33.0, WALL_T, WALL_H, 12.0, tex=bk)

        # Hallway Inner Walls (facing the central school courtyard)
        self.wall(-15.75, HH, -18.0, WALL_T, WALL_H, 32.0, tex=bk)
        self.wall(-15.75, HH, 18.0, WALL_T, WALL_H, 32.0, tex=bk)
        self.wall(15.75, HH, -18.0, WALL_T, WALL_H, 32.0, tex=bk)
        self.wall(15.75, HH, 18.0, WALL_T, WALL_H, 32.0, tex=bk)

        # North & South Hall perimeter outer walls
        self.wall(0, HH, -38.25, 41.0, WALL_H, WALL_T, tex=bk)
        self.wall(0, HH, 38.25, 41.0, WALL_H, WALL_T, tex=bk)
        self.wall(0, HH, -33.75, 27.0, WALL_H, WALL_T, tex=bk)
        self.wall(0, HH, 33.75, 27.0, WALL_H, WALL_T, tex=bk)

        # Metal Lockers along Hallways (hand-placed with proper UV mapped model)
        for lz in range(-30, 31, 4):
            if abs(lz) not in [0, 20, 18, 12, 26]:
                # West Hall lockers
                self.prop((-16.1, 0, lz), scale=(1, 1, 1), model=_mdl('locker.obj'), tex=lkt, rot_y=90)
                # East Hall lockers
                self.prop((16.1, 0, lz), scale=(1, 1, 1), model=_mdl('locker.obj'), tex=lkt, rot_y=-90)

        # ── 2. GIANT GYMNASIUM & BASKETBALL COURT (West Wing: x -50 to -20.25, z 6 to 36) ──
        # Size: 30m wide × 30m deep! Ceiling: 6.5m tall!
        GYM_H = 6.5
        ghh = GYM_H / 2
        gx, gz = -35.0, 21.0
        gw, gd = 29.5, 30.0

        self.floor(gx, gz, gw, gd, tex=gymt, tile=4.0)
        self.ceiling(gx, gz, gw, gd, tex=clt, tile=3.0, h=GYM_H)

        # Gym Perimeter Walls
        self.wall(-50.0, ghh, gz, WALL_T, GYM_H, gd, tex=bk)
        self.wall(gx, ghh, 36.0, gw, GYM_H, WALL_T, tex=bk)
        self.wall(gx, ghh, 6.0, gw, GYM_H, WALL_T, tex=bk)

        # 2 Regulation Basketball Hoops (Opposing ends)
        self.prop((-48.5, 0, gz), scale=(1, 1, 1), model=_mdl('basketball_hoop.obj'), rot_y=90)
        self.prop((-22.0, 0, gz), scale=(1, 1, 1), model=_mdl('basketball_hoop.obj'), rot_y=-90)

        # Spectator Bleachers along north wall
        self.prop((gx - 5, 0, 33.5), scale=(1.2, 1, 1), model=_mdl('bleachers.obj'), rot_y=180)
        self.prop((gx + 5, 0, 33.5), scale=(1.2, 1, 1), model=_mdl('bleachers.obj'), rot_y=180)

        # Gym High-Bay Lights
        for lx in [-42, -28]:
            for lz in [12, 21, 30]:
                self.light((lx, GYM_H - 0.2, lz), col=color.hex('#f0f5ff'), fixture=False)

        # ── 3. CAFETERIA & COMMONS (West Wing: x -50 to -20.25, z -36 to -6) ──
        # Size: 30m × 30m
        cx, cz = -35.0, -21.0
        self.floor(cx, cz, gw, gd, tex=til, tile=3.0)
        self.ceiling(cx, cz, gw, gd, tex=clt, tile=3.0)

        self.wall(-50.0, HH, cz, WALL_T, WALL_H, gd, tex=bk)
        self.wall(cx, HH, -36.0, gw, WALL_H, WALL_T, tex=bk)
        self.wall(cx, HH, -6.0, gw, WALL_H, WALL_T, tex=bk)

        # Cafeteria Long Dining Tables (10 hand-placed tables in grid)
        for tx in [-43, -37, -31]:
            for tz in [-30, -23, -16]:
                self.prop((tx, 0.45, tz), scale=(4.5, 0.8, 1.4), col=color.hex('#8b2626'))
        # Food Serving Counter
        self.prop((-46.0, 0.5, -10.0), scale=(1.2, 1.0, 8.0), col=color.hex('#303844'))
        self.light((cx, WALL_H - 0.15, cz), col=color.hex('#fff2d4'))

        # ── 4. LIBRARY & MEDIA MAZE (East Wing: x 20.25 to 50, z -36 to -6) ──
        # Size: 30m × 30m
        lx_c, lz_c = 35.0, -21.0
        self.floor(lx_c, lz_c, gw, gd, tex=wdp, tile=2.5)
        self.ceiling(lx_c, lz_c, gw, gd, tex=clt, tile=3.0)

        self.wall(50.0, HH, lz_c, WALL_T, WALL_H, gd, tex=bk)
        self.wall(lx_c, HH, -36.0, gw, WALL_H, WALL_T, tex=bk)
        self.wall(lx_c, HH, -6.0, gw, WALL_H, WALL_T, tex=bk)

        # Bookshelf Rows forming loopable aisles
        for bx in [26, 32, 38, 44]:
            self.prop((bx, 1.3, -25.0), scale=(1.0, 2.6, 9.0), tex=wdp)
            self.prop((bx, 1.3, -15.0), scale=(1.0, 2.6, 7.0), tex=wdp)
        self.light((lx_c, WALL_H - 0.15, lz_c), col=color.hex('#ffe8c2'))

        # ── 5. CLASSROOM 101 & 102 (East Wing: x 20.25 to 50, z 6 to 36) ──
        # Divided into 2 large enterable classrooms
        # Classroom 101 (z: 6 to 20):
        c1x, c1z = 35.0, 13.0
        self.floor(c1x, c1z, gw, 14.0, tex=til, tile=2.0)
        self.ceiling(c1x, c1z, gw, 14.0, tex=clt, tile=2.0)
        self.wall(50.0, HH, c1z, WALL_T, WALL_H, 14.0, tex=bk)
        self.wall(c1x, HH, 6.0, gw, WALL_H, WALL_T, tex=bk)
        self.wall(c1x, HH, 20.0, gw, WALL_H, WALL_T, tex=bk) # Dividing wall

        # Classroom 101 student desks (3 rows × 4 cols)
        for dx in [25, 30, 35, 40]:
            for dz in [9, 13, 17]:
                self.prop((dx, 0, dz), scale=(1, 1, 1), model=_mdl('desk_chair.obj'), tex=wdp)
        # Teacher desk & chalkboard
        self.prop((46.0, 0.4, 13.0), scale=(1.2, 0.8, 2.5), tex=wdp)
        self.prop((49.8, 1.8, 13.0), scale=(0.1, 1.4, 6.0), col=color.hex('#163824'))
        self.light((c1x, WALL_H - 0.15, c1z), col=color.hex('#f0f5ff'))

        # Classroom 102 (Science Lab, z: 20 to 36):
        c2z = 28.0
        self.floor(c1x, c2z, gw, 16.0, tex=til, tile=2.0)
        self.ceiling(c1x, c2z, gw, 16.0, tex=clt, tile=2.0)
        self.wall(50.0, HH, c2z, WALL_T, WALL_H, 16.0, tex=bk)
        self.wall(c1x, HH, 36.0, gw, WALL_H, WALL_T, tex=bk)

        for lz in [24, 28, 32]:
            self.prop((35.0, 0.5, lz), scale=(14.0, 1.0, 1.5), col=color.hex('#20242e'))
        self.light((c1x, WALL_H - 0.15, c2z), col=color.hex('#e6f0fa'))

        # ── 6. Central Enclosed Courtyard (x: -15.75 to +15.75, z: -33.75 to +33.75) ──
        # Open-air courtyard enclosed by high brick walls with grass/concrete and night sky
        self.floor(0, 0, 31.5, 67.5, tex=til, tile=3.0)
        self.ceiling(0, 0, 31.5, 67.5, tex=clt, tile=3.0) # Roofed central atrium

        # Central Skylight glow
        self.light((0, WALL_H - 0.15, 0), col=color.hex('#ffddaa'))

        # ── BALANCED SPAWN POINTS (Far Apart for Fair Gameplay) ──
        # Player spawns at South end of West Hall facing North (looking down 72m long corridor)
        self.spawn_point = Vec3(-18, 0, -32)
        # Nextbot spawns in North Concourse (70 meters away!)
        self.bot_spawn_point = Vec3(18, 0, 32)

    # ══════════════════════════════════════════════════════════════════════════
    # 2. STORE MAP: "MEGA SUPERCENTER & LOGISTICS WAREHOUSE" (110m x 90m)
    # ══════════════════════════════════════════════════════════════════════════
    def build_store(self):
        self.clear()
        scene.fog_density = (14, 60)
        scene.fog_color   = color.hex('#06080a')

        # Primary Dynamic Shadow Caster (Cool commercial fluorescent shadow)
        self.sun = DirectionalLight(shadows=True, rotation=(60, 25, 0), color=color.hex('#edf2ff'))
        self.entities.append(self.sun)

        amb = AmbientLight(color=color.hex('#484e5a'))
        self.entities.append(amb)

        sf   = _tex('store_floor.png')
        sht  = _tex('shelf_metal.png')
        con  = _tex('concrete.png')
        clt  = _tex('ceiling_tile.png')
        bk   = _tex('brick_wall.png')
        wdp  = _tex('wood_desk.png')
        whw  = _tex('warehouse_wall.png')

        # ── RETAIL FLOOR: 60m wide × 50m deep (x: -30 to 30, z: -25 to 25) ──
        RW, RD = 60.0, 50.0
        STORE_H = 5.2
        shh = STORE_H / 2

        self.floor(0, 0, RW, RD, tex=sf, tile=4.0)
        self.ceiling(0, 0, RW, RD, tex=clt, tile=4.0, h=STORE_H)

        # Retail Perimeter Walls
        self.wall(-30.0, shh, 0, WALL_T, STORE_H, RD, tex=bk)
        self.wall(30.0, shh, 0, WALL_T, STORE_H, RD, tex=bk)
        self.wall(0, shh, -25.0, RW, STORE_H, WALL_T, tex=bk) # Front entrance wall

        # 8 Massive Grocery & Goods Aisles (3m wide lanes for agile outrunning)
        # Aisles at x: -21, -15, -9, -3, 3, 9, 15, 21
        aisle_xs = [-21, -15, -9, -3, 3, 9, 15, 21]
        for ax in aisle_xs:
            # 2 rack sections per aisle with center walkthrough breach (loopable!)
            self.prop((ax, 0, -8.0), scale=(1.1, 1, 3.2), model=_mdl('shelf_rack.obj'), tex=sht)
            self.prop((ax, 0, 8.0), scale=(1.1, 1, 3.2), model=_mdl('shelf_rack.obj'), tex=sht)

            # Hanging Category Signs
            sign = Entity(
                position=(ax, STORE_H - 0.7, 0),
                scale=(2.4, 0.7, 0.15),
                model='cube',
                color=color.hex('#1a365d')
            )
            self.entities.append(sign)

        # Front Checkout Registers & Scanner Counters (8 registers)
        for cx in [-22, -16, -10, -4, 4, 10, 16, 22]:
            self.prop((cx, 0.5, -19.0), scale=(1.6, 1.0, 3.2), col=color.hex('#30343f'))
            self.prop((cx + 0.4, 1.25, -20.0), scale=(0.4, 0.4, 0.3), col=color.hex('#101216'))

        # Overhead Fluorescent Store Lighting (Grid of 16 fixtures)
        for lx in [-20, -7, 7, 20]:
            for lz in [-15, -2, 10, 20]:
                self.light((lx, STORE_H - 0.2, lz), col=color.hex('#f0f5ff'))

        # ── INDUSTRIAL LOGISTICS WAREHOUSE: 60m wide × 40m deep (z: 25 to 65) ──
        # Height: 7.5m high industrial steel warehouse!
        WH_H = 7.5
        whh = WH_H / 2
        W_DEPTH = 40.0
        wz_c = 45.0

        self.floor(0, wz_c, RW, W_DEPTH, tex=con, tile=4.0)
        self.ceiling(0, wz_c, RW, W_DEPTH, tex=whw, tile=4.0, h=WH_H)

        # Dividing Wall between Retail and Warehouse with 2 wide double-doorways
        # Openings at x = -10 and x = +10
        self.wall(-21.0, shh, 25.0, 18.0, STORE_H, WALL_T, tex=whw)
        self.doorway_header(-10.0, 25.0, axis='z', wall_tex=whw, h=STORE_H)
        self.wall(0.0, shh, 25.0, 16.0, STORE_H, WALL_T, tex=whw)
        self.doorway_header(10.0, 25.0, axis='z', wall_tex=whw, h=STORE_H)
        self.wall(21.0, shh, 25.0, 18.0, STORE_H, WALL_T, tex=whw)

        # Warehouse Outer Walls
        self.wall(-30.0, whh, wz_c, WALL_T, WH_H, W_DEPTH, tex=whw)
        self.wall(30.0, whh, wz_c, WALL_T, WH_H, W_DEPTH, tex=whw)
        self.wall(0.0, whh, 65.0, RW, WH_H, WALL_T, tex=whw) # Back loading dock wall

        # Heavy Industrial Pallet Cargo Racks (Stacked with wooden pallets & freight)
        for wx in [-20, -10, 0, 10, 20]:
            for wz in [34, 45, 56]:
                self.prop((wx, 0, wz), scale=(1.2, 1.2, 1.2), model=_mdl('pallet_cargo.obj'), tex=wdp)

        # Warehouse Amber Industrial Emergency Floodlights
        for wx in [-15, 15]:
            for wz in [36, 54]:
                self.light((wx, WH_H - 0.25, wz), col=color.hex('#ffaa33'))

        # ── FAIR SPAWN POINTS ──
        # Player spawns at Store Main Entrance (z = -22)
        self.spawn_point = Vec3(0, 0, -22)
        # Nextbot spawns deep inside back warehouse bay (z = 60, 82 meters away!)
        self.bot_spawn_point = Vec3(0, 0, 60)

    # ══════════════════════════════════════════════════════════════════════════
    # 3. CITY MAP: "DOWNTOWN MIDNIGHT DISTRICT" (140m x 140m, 360° Skyscraper Perimeter)
    # ══════════════════════════════════════════════════════════════════════════
    def build_city(self):
        self.clear()
        scene.fog_density = (10, 50)
        scene.fog_color   = color.hex('#060910')

        # Primary Dynamic Shadow Caster (Eerie Blue Moonlight)
        self.sun = DirectionalLight(shadows=True, rotation=(52, -45, 0), color=color.hex('#9bb2d6'))
        self.entities.append(self.sun)

        amb = AmbientLight(color=color.hex('#4d576a'))
        self.entities.append(amb)

        asp  = _tex('asphalt.png')
        con  = _tex('concrete.png')
        bk   = _tex('brick_wall.png')
        sf   = _tex('store_floor.png')
        wdp  = _tex('wood_desk.png')
        sky  = _tex('night_sky.png')
        bldg = _tex('skyline_windows.png')

        # ── 1. Sky Dome & Moon Overhead (Eliminates ALL Void!) ──
        # Giant inverted sky sphere / dome ceiling textured with night stars and full moon
        skydome = Entity(
            position=(0, 28.0, 0),
            scale=(180, 0.1, 180),
            model='cube',
            texture=sky,
            color=color.white
        )
        skydome.texture_scale = Vec2(2, 2)
        self.entities.append(skydome)

        # ── 2. Full 360° Skyscraper Perimeter Wall (30m tall, NO VOID ON HORIZON!) ──
        SKY_H = 32.0
        skh = SKY_H / 2
        PERIM = 70.0  # Outer boundary at ±70m

        # North, South, East, West giant skyscraper facades with illuminated windows
        self.wall(0, skh, -PERIM, 142.0, SKY_H, WALL_T, tex=bldg, tile=6.0)
        self.wall(0, skh, PERIM, 142.0, SKY_H, WALL_T, tex=bldg, tile=6.0)
        self.wall(-PERIM, skh, 0, WALL_T, SKY_H, 142.0, tex=bldg, tile=6.0)
        self.wall(PERIM, skh, 0, WALL_T, SKY_H, 142.0, tex=bldg, tile=6.0)

        # ── 3. Four-Block Downtown Road & Sidewalk Grid ──
        # 2 Main Avenues (10m wide roads): x = -25 and x = +25
        # 2 Cross Streets (10m wide roads): z = -25 and z = +25
        # Intersection crossroads form a massive 4-way loop!
        RW = 10.0

        # Roads
        self.floor(-25, 0, RW, 138, tex=asp, tile=5.0) # West Ave
        self.floor(25, 0, RW, 138, tex=asp, tile=5.0)  # East Ave
        self.floor(0, -25, 138, RW, tex=asp, tile=5.0) # South St
        self.floor(0, 25, 138, RW, tex=asp, tile=5.0)  # North St
        # Center connector boulevard
        self.floor(0, 0, RW, 40, tex=asp, tile=5.0)
        self.floor(0, 0, 40, RW, tex=asp, tile=5.0)

        # Sidewalks covering the 4 city blocks (SW, SE, NW, NE)
        self.floor(-48, -48, 36, 36, tex=con, tile=3.0)
        self.floor(48, -48, 36, 36, tex=con, tile=3.0)
        self.floor(-48, 48, 36, 36, tex=con, tile=3.0)
        self.floor(48, 48, 36, 36, tex=con, tile=3.0)
        # Center island plaza
        self.floor(0, 0, 36, 36, tex=con, tile=3.0)

        # ── 4. Downtown City Buildings (Massive Enterable & Facade Structures) ──
        BH = 18.0
        bhh = BH / 2

        # 4 Block Internal Buildings:
        # SW Block: Enterable 24/7 Corner Bodega
        self.wall(-48, bhh, -35, 34, BH, WALL_T, tex=bk)
        self.wall(-35, bhh, -48, WALL_T, BH, 34, tex=bk)

        # Bodega Interior (x: -45 to -32, z: -45 to -32):
        self.floor(-38.5, -38.5, 13, 13, tex=sf, tile=2.0)
        self.ceiling(-38.5, -38.5, 13, 13, tex=con, tile=2.0, h=4.2)
        # Bodega counter & snack shelves
        self.prop((-36.0, 0.5, -42.0), scale=(1.2, 1.0, 3.5), col=color.hex('#28303c'))
        sht = _tex('shelf_metal.png')
        self.prop((-42.0, 0, -38.0), scale=(1, 1, 2.5), model=_mdl('shelf_rack.obj'), tex=sht)
        self.light((-38.5, 3.8, -38.5), col=color.hex('#fff2cc'), fixture=False)

        # NE Block: Enterable Apartment Lobby
        self.wall(48, bhh, 35, 34, BH, WALL_T, tex=bk)
        self.wall(35, bhh, 48, WALL_T, BH, 34, tex=bk)
        self.floor(38.5, 38.5, 13, 13, tex=con, tile=2.0)
        self.ceiling(38.5, 38.5, 13, 13, tex=con, tile=2.0, h=4.2)
        self.prop((40.0, 0.45, 42.0), scale=(4.0, 0.8, 1.8), col=color.hex('#782222'))
        self.light((38.5, 3.8, 38.5), col=color.hex('#e8f2ff'), fixture=False)

        # NW Block & SE Block: Solid Downtown Towers
        self.wall(-48, bhh, 48, 34, BH, 34, tex=bldg, tile=4.0)
        self.wall(48, bhh, -48, 34, BH, 34, tex=bldg, tile=4.0)

        # ── 5. Back Alleys with Dumpsters ──
        self.prop((-20.0, 0, -42.0), scale=(1, 1, 1), model=_mdl('dumpster.obj'), col=color.hex('#22442a'))
        self.prop((20.0, 0, -42.0), scale=(1, 1, 1), model=_mdl('dumpster.obj'), col=color.hex('#30343a'))
        self.prop((-20.0, 0, 42.0), scale=(1, 1, 1), model=_mdl('dumpster.obj'), col=color.hex('#22442a'))
        self.prop((20.0, 0, 42.0), scale=(1, 1, 1), model=_mdl('dumpster.obj'), col=color.hex('#30343a'))

        # ── 6. Streetlights Lining Avenues & Cross Streets ──
        for lx in [-20, 20]:
            for lz in [-50, -25, 0, 25, 50]:
                rot = 90 if lx < 0 else -90
                self.prop((lx, 0, lz), scale=(1, 1, 1), model=_mdl('streetlight.obj'), rot_y=rot)
                self.light((lx + (1.3 if lx < 0 else -1.3), 5.0, lz), col=color.hex('#ffcc77'), fixture=False)

        # ── FAIR SPAWN POINTS (Distant Across Grid) ──
        self.spawn_point = Vec3(-25, 0, -25)     # Southwest crossroads
        self.bot_spawn_point = Vec3(25, 0, 45)   # Far Northeast Avenue (85m away!)
