"""
Asset generator for 'Run or dont'
Generates high-res textures, 3D OBJ models, and copyright-free procedural WAV audio.
"""
import os
import math
import struct
import wave
import random
import shutil
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
TEX_DIR = os.path.join(ASSETS_DIR, "textures")
MODEL_DIR = os.path.join(ASSETS_DIR, "models")
AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")
DESKTOP_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "RunOrDont_Models")

for d in [TEX_DIR, MODEL_DIR, AUDIO_DIR, DESKTOP_DIR]:
    os.makedirs(d, exist_ok=True)

# -------------------------------------------------------------
# 1. TEXTURE GENERATORS
# -------------------------------------------------------------
def generate_noise(w, h, base_color, noise_amount=20):
    img = Image.new("RGB", (w, h), base_color)
    pixels = img.load()
    br, bg, bb = base_color
    for y in range(h):
        for x in range(w):
            n = random.randint(-noise_amount, noise_amount)
            pixels[x, y] = (
                max(0, min(255, br + n)),
                max(0, min(255, bg + n)),
                max(0, min(255, bb + n)),
            )
    return img

def create_brick_texture():
    w, h = 512, 512
    img = generate_noise(w, h, (140, 50, 40), noise_amount=25)
    draw = ImageDraw.Draw(img)
    brick_h = 32
    brick_w = 64
    mortar_color = (200, 195, 185)
    
    rows = h // brick_h
    for r in range(rows):
        y = r * brick_h
        draw.line([(0, y), (w, y)], fill=mortar_color, width=3)
        offset = (brick_w // 2) if (r % 2 == 1) else 0
        cols = (w // brick_w) + 2
        for c in range(cols):
            x = (c * brick_w) - offset
            draw.line([(x, y), (x, y + brick_h)], fill=mortar_color, width=3)
            # subtle brick highlight
            if x >= 0 and x + brick_w <= w:
                draw.rectangle([x+4, y+4, x+brick_w-4, y+brick_h-4], outline=(160, 65, 55), width=1)
    img.save(os.path.join(TEX_DIR, "brick_wall.png"))

def create_school_tiles():
    w, h = 512, 512
    tile_size = 64
    img = Image.new("RGB", (w, h), (225, 225, 230))
    draw = ImageDraw.Draw(img)
    for y in range(0, h, tile_size):
        for x in range(0, w, tile_size):
            is_dark = ((x // tile_size) + (y // tile_size)) % 2 == 0
            c = (210, 215, 220) if is_dark else (245, 245, 250)
            draw.rectangle([x, y, x + tile_size, y + tile_size], fill=c)
            # specks in linoleum
            for _ in range(15):
                sx = random.randint(x, x + tile_size - 1)
                sy = random.randint(y, y + tile_size - 1)
                speck = random.choice([(180, 180, 190), (140, 150, 160), (255, 255, 255)])
                draw.point((sx, sy), fill=speck)
            draw.rectangle([x, y, x + tile_size, y + tile_size], outline=(170, 175, 180), width=2)
    img.save(os.path.join(TEX_DIR, "school_tiles.png"))

def create_store_floor():
    w, h = 512, 512
    tile_size = 128
    img = Image.new("RGB", (w, h), (240, 240, 242))
    draw = ImageDraw.Draw(img)
    for y in range(0, h, tile_size):
        for x in range(0, w, tile_size):
            draw.rectangle([x, y, x + tile_size, y + tile_size], fill=(235 + random.randint(-5, 5), 235 + random.randint(-5, 5), 238), outline=(190, 195, 200), width=3)
            # Polish sheen highlight
            draw.line([(x + 10, y + 10), (x + tile_size - 10, y + 10)], fill=(255, 255, 255), width=2)
    img.save(os.path.join(TEX_DIR, "store_floor.png"))

def create_asphalt():
    w, h = 512, 512
    img = generate_noise(w, h, (45, 45, 48), noise_amount=18)
    draw = ImageDraw.Draw(img)
    # Double yellow line in center
    draw.line([(240, 0), (240, h)], fill=(230, 190, 30), width=6)
    draw.line([(272, 0), (272, h)], fill=(230, 190, 30), width=6)
    # Road cracks
    for _ in range(6):
        x1 = random.randint(0, w)
        y1 = random.randint(0, h)
        x2 = x1 + random.randint(-40, 40)
        y2 = y1 + random.randint(-40, 40)
        draw.line([(x1, y1), (x2, y2)], fill=(25, 25, 25), width=2)
    img.save(os.path.join(TEX_DIR, "asphalt.png"))

def create_locker_texture():
    w, h = 256, 512
    img = generate_noise(w, h, (55, 80, 110), noise_amount=15)
    draw = ImageDraw.Draw(img)
    # 2 locker doors side by side
    col_w = w // 2
    for c in range(2):
        x0 = c * col_w
        x1 = x0 + col_w
        draw.rectangle([x0 + 4, 8, x1 - 4, h - 8], outline=(40, 60, 85), width=3)
        # ventilation slits at top
        for s in range(5):
            sy = 30 + (s * 10)
            draw.line([(x0 + 20, sy), (x1 - 20, sy)], fill=(30, 45, 65), width=3)
        # handle & lock
        hy = h // 2
        draw.rectangle([x1 - 24, hy - 25, x1 - 10, hy + 25], fill=(210, 215, 220), outline=(100, 105, 110), width=2)
        draw.ellipse([x1 - 20, hy - 5, x1 - 14, hy + 5], fill=(30, 30, 30))
        # bottom vent
        for s in range(3):
            sy = h - 60 + (s * 10)
            draw.line([(x0 + 25, sy), (x1 - 25, sy)], fill=(30, 45, 65), width=3)
    img.save(os.path.join(TEX_DIR, "locker_metal.png"))

def create_wood_desk():
    w, h = 512, 512
    img = generate_noise(w, h, (180, 130, 80), noise_amount=12)
    draw = ImageDraw.Draw(img)
    # Grain lines
    for y in range(0, h, 6):
        c = (160 + random.randint(-15, 15), 110 + random.randint(-15, 15), 65 + random.randint(-10, 10))
        draw.line([(0, y), (w, y)], fill=c, width=2)
    # Knots
    for _ in range(4):
        kx = random.randint(50, w - 50)
        ky = random.randint(50, h - 50)
        draw.ellipse([kx-20, ky-8, kx+20, ky+8], outline=(120, 80, 40), width=2)
        draw.ellipse([kx-10, ky-4, kx+10, ky+4], fill=(110, 70, 35))
    img.save(os.path.join(TEX_DIR, "wood_desk.png"))

def create_supermarket_shelf():
    w, h = 512, 512
    img = generate_noise(w, h, (120, 125, 130), noise_amount=10)
    draw = ImageDraw.Draw(img)
    tier_h = h // 4
    colors = [(200, 50, 50), (40, 120, 200), (50, 180, 70), (220, 180, 40), (180, 70, 190)]
    for t in range(4):
        ty = t * tier_h
        # metal shelf lip with pricing label
        draw.rectangle([0, ty + tier_h - 14, w, ty + tier_h], fill=(230, 230, 235), outline=(90, 95, 100), width=2)
        draw.rectangle([10, ty + tier_h - 11, w - 10, ty + tier_h - 3], fill=(240, 220, 50))
        # goods/boxes on shelf
        bx = 10
        while bx < w - 30:
            bw = random.randint(25, 45)
            bh = random.randint(45, tier_h - 22)
            c = random.choice(colors)
            by = ty + tier_h - 14 - bh
            draw.rectangle([bx, by, bx + bw, ty + tier_h - 14], fill=c, outline=(30, 30, 30), width=1)
            # label on box
            draw.rectangle([bx + 4, by + bh//3, bx + bw - 4, by + 2*bh//3], fill=(250, 250, 250))
            bx += bw + random.randint(2, 6)
    img.save(os.path.join(TEX_DIR, "shelf_metal.png"))

def create_concrete():
    w, h = 512, 512
    img = generate_noise(w, h, (160, 160, 165), noise_amount=30)
    draw = ImageDraw.Draw(img)
    # Sidewalk slab lines
    draw.line([(0, 256), (w, 256)], fill=(120, 120, 125), width=4)
    draw.line([(256, 0), (256, h)], fill=(120, 120, 125), width=4)
    img.save(os.path.join(TEX_DIR, "concrete.png"))

def create_door_texture():
    w, h = 256, 512
    img = generate_noise(w, h, (100, 60, 30), noise_amount=15)
    draw = ImageDraw.Draw(img)
    draw.rectangle([8, 8, w - 8, h - 8], outline=(60, 35, 15), width=6)
    # 4 panels
    panel_h = (h - 60) // 2
    for r in range(2):
        py1 = 20 + r * (panel_h + 20)
        py2 = py1 + panel_h
        draw.rectangle([25, py1, w - 25, py2], fill=(85, 50, 25), outline=(50, 30, 10), width=4)
    # Brass doorknob
    draw.ellipse([w - 45, h // 2 - 12, w - 25, h // 2 + 12], fill=(220, 180, 50), outline=(130, 100, 20), width=2)
    img.save(os.path.join(TEX_DIR, "door_wood.png"))

def create_ceiling_texture():
    w, h = 512, 512
    img = generate_noise(w, h, (230, 230, 235), noise_amount=20)
    draw = ImageDraw.Draw(img)
    grid = 128
    for i in range(0, w, grid):
        draw.line([(i, 0), (i, h)], fill=(180, 185, 190), width=3)
        draw.line([(0, i), (w, i)], fill=(180, 185, 190), width=3)
    img.save(os.path.join(TEX_DIR, "ceiling_tile.png"))

def create_nextbot_texture():
    # Terrifying high-res distorted nextbot entity with dark background and red piercing eyes
    w, h = 512, 512
    img = Image.new("RGBA", (w, h), (18, 14, 20, 255))
    draw = ImageDraw.Draw(img)
    
    # Outer dark shadow vignette
    for r in range(256, 0, -4):
        alpha_vignette = int(255 * (1.0 - (r / 256.0)))
        draw.ellipse([256 - r, 256 - r, 256 + r, 256 + r], outline=(10, 8, 12, alpha_vignette), width=4)

    # Sickly pale humanoid head contour
    draw.ellipse([90, 40, 422, 475], fill=(215, 210, 205), outline=(90, 80, 85), width=5)
    
    # Hollow sunken black eye sockets
    draw.ellipse([140, 160, 230, 260], fill=(12, 8, 10))
    draw.ellipse([282, 160, 372, 260], fill=(12, 8, 10))
    
    # Glowing blood-red pupils with white glint
    draw.ellipse([172, 195, 198, 225], fill=(255, 20, 20))
    draw.ellipse([314, 195, 340, 225], fill=(255, 20, 20))
    draw.ellipse([182, 204, 188, 212], fill=(255, 255, 255))
    draw.ellipse([324, 204, 330, 212], fill=(255, 255, 255))
    
    # Distorted elongated smile
    draw.arc([130, 270, 382, 435], start=10, end=170, fill=(18, 10, 14), width=26)
    # Jagged teeth
    for t in range(160, 355, 16):
        draw.rectangle([t, 342, t + 10, 362], fill=(235, 230, 215), outline=(40, 35, 30))
        draw.rectangle([t + 3, 370, t + 13, 390], fill=(225, 220, 205), outline=(40, 35, 30))
        
    # Bloody dark drip veins
    for vx, vy, vlen in [(185, 260, 60), (325, 260, 55), (150, 410, 50), (360, 410, 45)]:
        draw.line([(vx, vy), (vx, vy + vlen)], fill=(120, 15, 20), width=3)
        draw.ellipse([vx-3, vy+vlen-2, vx+3, vy+vlen+6], fill=(120, 15, 20))
    
    img.save(os.path.join(TEX_DIR, "nextbot.png"))
    img.save(os.path.join(TEX_DIR, "nextbot_obunga.png"))

def create_player_body_texture():
    # Texture for the first-person body: Hoodie torso, tactical combat pants, and sneakers
    w, h = 512, 512
    img = Image.new("RGB", (w, h), (40, 45, 55))
    draw = ImageDraw.Draw(img)
    # Upper half: Dark stealth hoodie with zip line & drawstrings
    draw.rectangle([0, 0, w, 240], fill=(30, 35, 42))
    draw.line([(w // 2, 0), (w // 2, 240)], fill=(90, 95, 105), width=4)
    draw.line([(w // 2 - 25, 20), (w // 2 - 25, 120)], fill=(220, 225, 230), width=3)
    draw.line([(w // 2 + 25, 20), (w // 2 + 25, 120)], fill=(220, 225, 230), width=3)
    # Pockets
    draw.rectangle([60, 130, 190, 220], outline=(50, 55, 65), width=3)
    draw.rectangle([320, 130, 450, 220], outline=(50, 55, 65), width=3)
    
    # Middle: Tactical cargo pants (dark charcoal)
    draw.rectangle([0, 240, w, 420], fill=(45, 48, 52))
    draw.line([(w // 2, 240), (w // 2, 420)], fill=(25, 25, 28), width=5)
    # Cargo side pockets
    draw.rectangle([30, 270, 140, 370], fill=(40, 43, 47), outline=(60, 64, 70), width=2)
    draw.rectangle([370, 270, 480, 370], fill=(40, 43, 47), outline=(60, 64, 70), width=2)
    # Knee pads
    draw.ellipse([80, 380, 180, 415], fill=(25, 28, 30))
    draw.ellipse([330, 380, 430, 415], fill=(25, 28, 30))
    
    # Bottom: Running sneakers (black/red high-visibility runner)
    draw.rectangle([0, 420, w, h], fill=(20, 20, 22))
    # Sole
    draw.rectangle([0, 490, w, h], fill=(240, 240, 245))
    # Red athletic speed accents
    draw.line([(40, 450), (200, 470)], fill=(230, 35, 35), width=6)
    draw.line([(310, 470), (470, 450)], fill=(230, 35, 35), width=6)
    # White laces
    for ly in range(435, 485, 10):
        draw.line([(100, ly), (140, ly)], fill=(255, 255, 255), width=3)
        draw.line([(370, ly), (410, ly)], fill=(255, 255, 255), width=3)
        
    img.save(os.path.join(TEX_DIR, "player_body.png"))

# -------------------------------------------------------------
# 2. 3D OBJ MODEL GENERATORS
# -------------------------------------------------------------
def export_obj(filepath, vertices, uvs, normals, faces):
    with open(filepath, "w") as f:
        f.write("# Run or dont 3D Asset\n")
        for v in vertices:
            f.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
        for vt in uvs:
            f.write(f"vt {vt[0]:.4f} {vt[1]:.4f}\n")
        for vn in normals:
            f.write(f"vn {vn[0]:.4f} {vn[1]:.4f} {vn[2]:.4f}\n")
        for face in faces:
            # face elements format: (v_idx, vt_idx, vn_idx) 1-based
            f_str = " ".join([f"{item[0]}/{item[1]}/{item[2]}" for item in face])
            f.write(f"f {f_str}\n")

def create_box_model(filepath, w, h, d, y_offset=0):
    hw, hh, hd = w / 2.0, h / 2.0, d / 2.0
    cy = y_offset + hh
    # 8 vertices
    vertices = [
        (-hw, cy - hh, -hd), (hw, cy - hh, -hd), (hw, cy + hh, -hd), (-hw, cy + hh, -hd), # Front
        (-hw, cy - hh,  hd), (hw, cy - hh,  hd), (hw, cy + hh,  hd), (-hw, cy + hh,  hd), # Back
    ]
    uvs = [
        (0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)
    ]
    normals = [
        (0, 0, -1), (0, 0, 1), (-1, 0, 0), (1, 0, 0), (0, 1, 0), (0, -1, 0)
    ]
    # Faces: (v, vt, vn)
    faces = [
        # Front
        [(1, 1, 1), (2, 2, 1), (3, 3, 1), (4, 4, 1)],
        # Back
        [(6, 1, 2), (5, 2, 2), (8, 3, 2), (7, 4, 2)],
        # Left
        [(5, 1, 3), (1, 2, 3), (4, 3, 3), (8, 4, 3)],
        # Right
        [(2, 1, 4), (6, 2, 4), (7, 3, 4), (3, 4, 4)],
        # Top
        [(4, 1, 5), (3, 2, 5), (7, 3, 5), (8, 4, 5)],
        # Bottom
        [(5, 1, 6), (6, 2, 6), (2, 3, 6), (1, 4, 6)],
    ]
    export_obj(filepath, vertices, uvs, normals, faces)

def create_player_body_obj():
    # 3D model representing the player's physical body when looking down:
    # Torso (hoodie), Left & Right tactical cargo legs, Left & Right athletic running shoes.
    # Modeled in true world heights from ground (y=0) up to chest (y=1.55)
    vertices = []
    uvs = []
    normals = [(0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1), (1, 0, 0), (-1, 0, 0)]
    faces = []

    def add_cube(cx, cy, cz, sx, sy, sz, u0, v0, u1, v1):
        v_start = len(vertices) + 1
        t_start = len(uvs) + 1
        hx, hy, hz = sx / 2, sy / 2, sz / 2
        box_v = [
            (cx - hx, cy - hy, cz - hz), (cx + hx, cy - hy, cz - hz),
            (cx + hx, cy + hy, cz - hz), (cx - hx, cy + hy, cz - hz),
            (cx - hx, cy - hy, cz + hz), (cx + hx, cy - hy, cz + hz),
            (cx + hx, cy + hy, cz + hz), (cx - hx, cy + hy, cz + hz)
        ]
        vertices.extend(box_v)
        uvs.extend([(u0, v0), (u1, v0), (u1, v1), (u0, v1)])

        # Front, Back, Left, Right, Top, Bottom
        faces.append([(v_start+0, t_start+0, 4), (v_start+1, t_start+1, 4), (v_start+2, t_start+2, 4), (v_start+3, t_start+3, 4)])
        faces.append([(v_start+5, t_start+0, 3), (v_start+4, t_start+1, 3), (v_start+7, t_start+2, 3), (v_start+6, t_start+3, 3)])
        faces.append([(v_start+4, t_start+0, 6), (v_start+0, t_start+1, 6), (v_start+3, t_start+2, 6), (v_start+7, t_start+3, 6)])
        faces.append([(v_start+1, t_start+0, 5), (v_start+5, t_start+1, 5), (v_start+6, t_start+2, 5), (v_start+2, t_start+3, 5)])
        faces.append([(v_start+3, t_start+0, 1), (v_start+2, t_start+1, 1), (v_start+6, t_start+2, 1), (v_start+7, t_start+3, 1)])
        faces.append([(v_start+4, t_start+0, 2), (v_start+5, t_start+1, 2), (v_start+1, t_start+2, 2), (v_start+0, t_start+3, 2)])

    # Torso / Hoodie chest (y: 1.0 to 1.55, z: 0.12)
    add_cube(0, 1.25, 0.14, 0.58, 0.55, 0.32, 0.0, 0.5, 1.0, 1.0)
    # Left Cargo Leg (y: 0.35 to 1.0, z: 0.10)
    add_cube(-0.16, 0.65, 0.10, 0.22, 0.65, 0.26, 0.0, 0.2, 0.5, 0.5)
    # Right Cargo Leg
    add_cube(0.16, 0.65, 0.10, 0.22, 0.65, 0.26, 0.5, 0.2, 1.0, 0.5)
    # Left Sneaker Foot (y: 0.0 to 0.28, extended forward at z: 0.26)
    add_cube(-0.16, 0.14, 0.26, 0.22, 0.26, 0.48, 0.0, 0.0, 0.5, 0.2)
    # Right Sneaker Foot
    add_cube(0.16, 0.14, 0.26, 0.22, 0.26, 0.48, 0.5, 0.0, 1.0, 0.2)

    export_obj(os.path.join(MODEL_DIR, "player_body.obj"), vertices, uvs, normals, faces)

def create_nextbot_stand_obj():
    # 3D Obelisk / Monolith frame housing the nextbot entity with depth and bevels
    vertices = []
    uvs = []
    normals = [(0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1), (1, 0, 0), (-1, 0, 0)]
    faces = []

    def add_cube(cx, cy, cz, sx, sy, sz, u0, v0, u1, v1):
        v_start = len(vertices) + 1
        t_start = len(uvs) + 1
        hx, hy, hz = sx / 2, sy / 2, sz / 2
        box_v = [
            (cx - hx, cy - hy, cz - hz), (cx + hx, cy - hy, cz - hz),
            (cx + hx, cy + hy, cz - hz), (cx - hx, cy + hy, cz - hz),
            (cx - hx, cy - hy, cz + hz), (cx + hx, cy - hy, cz + hz),
            (cx + hx, cy + hy, cz + hz), (cx - hx, cy + hy, cz + hz)
        ]
        vertices.extend(box_v)
        uvs.extend([(u0, v0), (u1, v0), (u1, v1), (u0, v1)])

        faces.append([(v_start+0, t_start+0, 4), (v_start+1, t_start+1, 4), (v_start+2, t_start+2, 4), (v_start+3, t_start+3, 4)])
        faces.append([(v_start+5, t_start+0, 3), (v_start+4, t_start+1, 3), (v_start+7, t_start+2, 3), (v_start+6, t_start+3, 3)])
        faces.append([(v_start+4, t_start+0, 6), (v_start+0, t_start+1, 6), (v_start+3, t_start+2, 6), (v_start+7, t_start+3, 6)])
        faces.append([(v_start+1, t_start+0, 5), (v_start+5, t_start+1, 5), (v_start+6, t_start+2, 5), (v_start+2, t_start+3, 5)])
        faces.append([(v_start+3, t_start+0, 1), (v_start+2, t_start+1, 1), (v_start+6, t_start+2, 1), (v_start+7, t_start+3, 1)])
        faces.append([(v_start+4, t_start+0, 2), (v_start+5, t_start+1, 2), (v_start+1, t_start+2, 2), (v_start+0, t_start+3, 2)])

    # Main Face Billboard Plane/Slab (h: 2.2m, w: 1.6m, d: 0.2m)
    add_cube(0, 1.1, 0, 1.6, 2.2, 0.2, 0.0, 0.0, 1.0, 1.0)
    # Side spikes/horns for sinister silhouette
    add_cube(-0.85, 2.0, 0, 0.15, 0.5, 0.15, 0.0, 0.0, 0.2, 0.2)
    add_cube(0.85, 2.0, 0, 0.15, 0.5, 0.15, 0.0, 0.0, 0.2, 0.2)
    # Base pedestal
    add_cube(0, 0.1, 0, 1.8, 0.2, 0.6, 0.0, 0.0, 0.5, 0.5)

    export_obj(os.path.join(MODEL_DIR, "nextbot_stand.obj"), vertices, uvs, normals, faces)

def create_desk_chair_obj():
    vertices = []
    uvs = []
    normals = [(0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1), (1, 0, 0), (-1, 0, 0)]
    faces = []

    def add_cube(cx, cy, cz, sx, sy, sz):
        v_start = len(vertices) + 1
        t_start = len(uvs) + 1
        hx, hy, hz = sx / 2, sy / 2, sz / 2
        box_v = [
            (cx - hx, cy - hy, cz - hz), (cx + hx, cy - hy, cz - hz),
            (cx + hx, cy + hy, cz - hz), (cx - hx, cy + hy, cz - hz),
            (cx - hx, cy - hy, cz + hz), (cx + hx, cy - hy, cz + hz),
            (cx + hx, cy + hy, cz + hz), (cx - hx, cy + hy, cz + hz)
        ]
        vertices.extend(box_v)
        uvs.extend([(0, 0), (1, 0), (1, 1), (0, 1)])
        faces.append([(v_start+0, t_start+0, 4), (v_start+1, t_start+1, 4), (v_start+2, t_start+2, 4), (v_start+3, t_start+3, 4)])
        faces.append([(v_start+5, t_start+0, 3), (v_start+4, t_start+1, 3), (v_start+7, t_start+2, 3), (v_start+6, t_start+3, 3)])
        faces.append([(v_start+4, t_start+0, 6), (v_start+0, t_start+1, 6), (v_start+3, t_start+2, 6), (v_start+7, t_start+3, 6)])
        faces.append([(v_start+1, t_start+0, 5), (v_start+5, t_start+1, 5), (v_start+6, t_start+2, 5), (v_start+2, t_start+3, 5)])
        faces.append([(v_start+3, t_start+0, 1), (v_start+2, t_start+1, 1), (v_start+6, t_start+2, 1), (v_start+7, t_start+3, 1)])
        faces.append([(v_start+4, t_start+0, 2), (v_start+5, t_start+1, 2), (v_start+1, t_start+2, 2), (v_start+0, t_start+3, 2)])

    # Desktop top surface
    add_cube(0, 0.75, 0.2, 1.2, 0.06, 0.7)
    # 4 legs
    add_cube(-0.55, 0.37, -0.1, 0.05, 0.75, 0.05)
    add_cube(0.55, 0.37, -0.1, 0.05, 0.75, 0.05)
    add_cube(-0.55, 0.37, 0.5, 0.05, 0.75, 0.05)
    add_cube(0.55, 0.37, 0.5, 0.05, 0.75, 0.05)
    # Chair seat
    add_cube(0, 0.45, -0.4, 0.5, 0.05, 0.5)
    # Chair backrest
    add_cube(0, 0.75, -0.62, 0.5, 0.4, 0.05)
    # Chair legs
    add_cube(-0.2, 0.22, -0.2, 0.04, 0.45, 0.04)
    add_cube(0.2, 0.22, -0.2, 0.04, 0.45, 0.04)
    add_cube(-0.2, 0.22, -0.6, 0.04, 0.45, 0.04)
    add_cube(0.2, 0.22, -0.6, 0.04, 0.45, 0.04)

    export_obj(os.path.join(MODEL_DIR, "desk_chair.obj"), vertices, uvs, normals, faces)

def create_supermarket_rack_obj():
    create_box_model(os.path.join(MODEL_DIR, "shelf_rack.obj"), 2.4, 2.6, 0.8, y_offset=0)

def create_dumpster_obj():
    create_box_model(os.path.join(MODEL_DIR, "dumpster.obj"), 2.2, 1.4, 1.2, y_offset=0)

def create_streetlight_obj():
    create_box_model(os.path.join(MODEL_DIR, "streetlight.obj"), 0.4, 5.0, 0.4, y_offset=0)

def create_locker_obj():
    create_box_model(os.path.join(MODEL_DIR, "locker.obj"), 1.2, 2.2, 0.5, y_offset=0)

# -------------------------------------------------------------
# 3. PROCEDURAL COPYRIGHT-FREE AUDIO GENERATORS
# -------------------------------------------------------------
def save_wav(filename, samples, sample_rate=44100):
    filepath = os.path.join(AUDIO_DIR, filename)
    with wave.open(filepath, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        # convert float samples (-1.0 to 1.0) to 16-bit PCM
        raw = bytearray()
        for s in samples:
            val = int(max(-1.0, min(1.0, s)) * 32767)
            raw.extend(struct.pack("<h", val))
        wf.writeframes(raw)

def create_audio_assets():
    sr = 44100
    
    # 1. Menu Atmospheric Ambient (Eerie dark synth pad with low drone)
    dur = 12.0
    num_samples = int(sr * dur)
    ambient = [0.0] * num_samples
    freqs = [55.0, 82.5, 110.0, 164.8, 220.0] # A minor chord low pad
    for i in range(num_samples):
        t = i / sr
        # slow low-frequency modulations
        lfo = 0.5 + 0.5 * math.sin(2 * math.pi * 0.15 * t)
        val = 0.0
        for f in freqs:
            val += math.sin(2 * math.pi * f * t + 0.2 * math.sin(2 * math.pi * 0.5 * t)) * 0.12
        # gentle tape flutter noise
        noise = (random.random() * 2 - 1) * 0.015
        # fade in/out envelope
        env = min(1.0, t / 1.5) * min(1.0, (dur - t) / 1.5)
        ambient[i] = (val * lfo + noise) * env * 0.7
    save_wav("menu_ambient.wav", ambient, sr)

    # 2. Chase Music (High-paced 160 BPM adrenaline pumping pursuit track)
    dur = 14.0
    num_samples = int(sr * dur)
    chase = [0.0] * num_samples
    bpm = 160.0
    beat_dur = 60.0 / bpm
    for i in range(num_samples):
        t = i / sr
        beat_num = t / beat_dur
        beat_phase = beat_num % 1.0
        
        # Heavy pulsating sub-bass
        bass_note = 44.0 if (int(beat_num) % 8 < 6) else 37.0
        bass = math.sin(2 * math.pi * bass_note * t) * math.exp(-beat_phase * 3.5) * 0.45
        
        # Kick drum on every beat
        kick_freq = 150.0 * math.exp(-beat_phase * 25.0) + 40.0
        kick = math.sin(2 * math.pi * kick_freq * beat_phase) * math.exp(-beat_phase * 12.0) * 0.6
        
        # Fast hi-hats (16th notes)
        hihat_phase = (t / (beat_dur / 4.0)) % 1.0
        hihat = ((random.random() * 2 - 1) if hihat_phase < 0.15 else 0.0) * 0.2
        
        # Tension siren/stinger
        siren = math.sin(2 * math.pi * (500.0 + 200.0 * math.sin(2 * math.pi * 1.5 * t)) * t) * 0.08
        
        val = bass + kick + hihat + siren
        env = min(1.0, t / 0.5) * min(1.0, (dur - t) / 0.5)
        chase[i] = val * env * 0.8
    save_wav("chase_music.wav", chase, sr)

    # 3. Footstep Sound (Crisp sneaker step)
    dur = 0.22
    num_samples = int(sr * dur)
    step = [0.0] * num_samples
    for i in range(num_samples):
        t = i / sr
        # quick thump + friction noise
        thump = math.sin(2 * math.pi * 90.0 * (1.0 - t / dur) * t) * math.exp(-t * 28.0) * 0.6
        grit = (random.random() * 2 - 1) * math.exp(-t * 35.0) * 0.35
        step[i] = (thump + grit)
    save_wav("footstep.wav", step, sr)

    # 4. Slide Sound (Friction sneaker skid on smooth surface)
    dur = 0.75
    num_samples = int(sr * dur)
    slide = [0.0] * num_samples
    for i in range(num_samples):
        t = i / sr
        decay = math.exp(-t * 3.5)
        # filtered whoosh noise
        noise = (random.random() * 2 - 1) * decay * 0.5
        whistle = math.sin(2 * math.pi * (400.0 - 200.0 * (t / dur)) * t) * decay * 0.15
        slide[i] = noise + whistle
    save_wav("slide.wav", slide, sr)

    # 5. Flashlight Click (Sharp tactile switch)
    dur = 0.08
    num_samples = int(sr * dur)
    fl = [0.0] * num_samples
    for i in range(num_samples):
        t = i / sr
        click = math.sin(2 * math.pi * 2400.0 * t) * math.exp(-t * 120.0) * 0.8
        fl[i] = click
    save_wav("flashlight.wav", fl, sr)

    # 6. Jumpscare Screech / Glitch Blast
    dur = 1.8
    num_samples = int(sr * dur)
    scream = [0.0] * num_samples
    for i in range(num_samples):
        t = i / sr
        # Ear-splitting distorted frequency sweeps + white noise burst
        f1 = 700.0 + 1200.0 * math.sin(2 * math.pi * 30.0 * t)
        f2 = 180.0 + 40.0 * math.sin(2 * math.pi * 8.0 * t)
        dist = math.sin(2 * math.pi * f1 * t) * 0.5 + math.sin(2 * math.pi * f2 * t) * 0.5
        # harsh clipping distortion
        clipped = max(-0.8, min(0.8, dist * 3.0))
        noise = (random.random() * 2 - 1) * 0.4
        env = math.exp(-t * 1.8)
        scream[i] = (clipped + noise) * env * 0.95
    save_wav("jumpscare.wav", scream, sr)

    # 7. Bootup Chime & Glitch Sweep
    dur = 2.4
    num_samples = int(sr * dur)
    boot = [0.0] * num_samples
    for i in range(num_samples):
        t = i / sr
        if t < 1.0:
            # ascending frequency sweep
            sweep_freq = 100.0 + 800.0 * (t ** 2)
            boot[i] = math.sin(2 * math.pi * sweep_freq * t) * 0.35 * (t / 1.0)
        else:
            # harmonic chime chords (C major / E / G)
            t2 = t - 1.0
            chime = (
                math.sin(2 * math.pi * 523.25 * t2) * 0.3 +
                math.sin(2 * math.pi * 659.25 * t2) * 0.25 +
                math.sin(2 * math.pi * 783.99 * t2) * 0.2
            ) * math.exp(-t2 * 2.5)
            boot[i] = chime
    save_wav("boot.wav", boot, sr)

def copy_models_to_desktop():
    print(f"Copying 3D models and textures to Desktop: {DESKTOP_DIR}")
    for item in os.listdir(MODEL_DIR):
        src = os.path.join(MODEL_DIR, item)
        dst = os.path.join(DESKTOP_DIR, item)
        shutil.copy2(src, dst)
    for item in os.listdir(TEX_DIR):
        src = os.path.join(TEX_DIR, item)
        dst = os.path.join(DESKTOP_DIR, item)
        shutil.copy2(src, dst)
    print("Exported all 3D models and textures to Desktop successfully.")

def build_all_assets():
    print("Generating high-resolution textures...")
    create_brick_texture()
    create_school_tiles()
    create_store_floor()
    create_asphalt()
    create_locker_texture()
    create_wood_desk()
    create_supermarket_shelf()
    create_concrete()
    create_door_texture()
    create_ceiling_texture()
    create_nextbot_texture()
    create_player_body_texture()

    print("Generating 3D OBJ models...")
    create_player_body_obj()
    create_nextbot_stand_obj()
    create_desk_chair_obj()
    create_supermarket_rack_obj()
    create_dumpster_obj()
    create_streetlight_obj()
    create_locker_obj()

    print("Synthesizing copyright-free procedural audio...")
    create_audio_assets()

    print("Mirroring models & textures to user's Desktop...")
    copy_models_to_desktop()
    print("All assets generated successfully!")

if __name__ == "__main__":
    build_all_assets()
