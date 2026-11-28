"""
High-Resolution Texture & Asset Upgrader for 'Run or dont'
Generates photorealistic textures, downloads Three.js PBR textures, and mirrors to Desktop.
"""
import os
import math
import random
import requests
import shutil
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEX_DIR = os.path.join(BASE_DIR, "assets", "textures")
MODEL_DIR = os.path.join(BASE_DIR, "assets", "models")
DESKTOP_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "RunOrDont_Models")

os.makedirs(TEX_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(DESKTOP_DIR, exist_ok=True)

def download_pbr_textures():
    print("Downloading high-res PBR textures from Three.js repository...")
    base = "https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/"
    
    # 1. Realistic Red Brick
    try:
        r = requests.get(base + "brick_diffuse.jpg", timeout=10)
        with open(os.path.join(TEX_DIR, "brick_wall.png"), "wb") as f:
            f.write(r.content)
        print("- brick_wall.png updated (1024x1024 photorealistic brick)")
    except Exception as e:
        print("Failed brick:", e)

    # 2. Hardwood Planks
    try:
        r = requests.get(base + "hardwood2_diffuse.jpg", timeout=10)
        with open(os.path.join(TEX_DIR, "wood_desk.png"), "wb") as f:
            f.write(r.content)
        print("- wood_desk.png updated (1024x1024 photorealistic hardwood)")
    except Exception as e:
        print("Failed wood:", e)

    # 3. High-res School Checkerboard Linoleum Floor
    try:
        r = requests.get(base + "floors/FloorsCheckerboard_S_Diffuse.jpg", timeout=10)
        with open(os.path.join(TEX_DIR, "school_tiles.png"), "wb") as f:
            f.write(r.content)
        print("- school_tiles.png updated (1024x1024 photorealistic checkerboard)")
    except Exception as e:
        print("Failed tile:", e)

def generate_photorealistic_asphalt():
    print("Generating high-res asphalt texture...")
    w, h = 1024, 1024
    img = Image.new("RGB", (w, h), (42, 44, 48))
    draw = ImageDraw.Draw(img)
    pixels = img.load()

    # Dense gravel & tar noise
    for y in range(h):
        for x in range(w):
            n = random.randint(-18, 18)
            pixels[x, y] = (max(20, min(80, 42 + n)), max(20, min(80, 44 + n)), max(20, min(80, 48 + n)))

    # Asphalt cracks
    for _ in range(12):
        cx = random.randint(50, w - 50)
        cy = random.randint(50, h - 50)
        for _ in range(8):
            nx = cx + random.randint(-40, 40)
            ny = cy + random.randint(-40, 40)
            draw.line([(cx, cy), (nx, ny)], fill=(18, 19, 22), width=random.randint(2, 4))
            cx, cy = nx, ny

    # Double Yellow Center Road Markings
    draw.line([(480, 0), (480, h)], fill=(230, 180, 20), width=14)
    draw.line([(544, 0), (544, h)], fill=(230, 180, 20), width=14)

    # White dash lane markers on left & right edges
    dash_h = 80
    gap = 60
    y = 0
    while y < h:
        draw.line([(120, y), (120, min(h, y + dash_h))], fill=(225, 230, 235), width=10)
        draw.line([(904, y), (904, min(h, y + dash_h))], fill=(225, 230, 235), width=10)
        y += dash_h + gap

    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    img.save(os.path.join(TEX_DIR, "asphalt.png"))
    print("- asphalt.png updated (1024x1024)")

def generate_photorealistic_concrete():
    print("Generating high-res concrete texture...")
    w, h = 1024, 1024
    img = Image.new("RGB", (w, h), (140, 142, 145))
    pixels = img.load()
    draw = ImageDraw.Draw(img)

    for y in range(h):
        for x in range(w):
            n = random.randint(-25, 25)
            pixels[x, y] = (max(80, min(200, 140 + n)), max(80, min(200, 142 + n)), max(80, min(200, 145 + n)))

    # Sidewalk slab seam lines
    draw.line([(0, 512), (w, 512)], fill=(75, 78, 82), width=6)
    draw.line([(512, 0), (512, h)], fill=(75, 78, 82), width=6)
    draw.line([(0, 516), (w, 516)], fill=(190, 192, 196), width=2)
    draw.line([(516, 0), (516, h)], fill=(190, 192, 196), width=2)

    img.save(os.path.join(TEX_DIR, "concrete.png"))
    print("- concrete.png updated (1024x1024)")

def generate_supermarket_floor():
    print("Generating high-res store floor...")
    w, h = 1024, 1024
    img = Image.new("RGB", (w, h), (235, 238, 240))
    draw = ImageDraw.Draw(img)
    tile_size = 256
    for y in range(0, h, tile_size):
        for x in range(0, w, tile_size):
            # Subtle marble sheen
            draw.rectangle([x+4, y+4, x+tile_size-4, y+tile_size-4], fill=(232 + random.randint(-4, 4), 235 + random.randint(-4, 4), 238), outline=(185, 190, 195), width=3)
            # Specular light gleam across tiles
            draw.line([(x+20, y+20), (x+tile_size-20, y+20)], fill=(255, 255, 255), width=2)
    img.save(os.path.join(TEX_DIR, "store_floor.png"))
    print("- store_floor.png updated (1024x1024)")

def generate_ceiling_tile():
    print("Generating high-res ceiling tile...")
    w, h = 1024, 1024
    img = Image.new("RGB", (w, h), (220, 222, 225))
    pixels = img.load()
    draw = ImageDraw.Draw(img)

    for y in range(h):
        for x in range(w):
            n = random.randint(-15, 15)
            pixels[x, y] = (max(160, min(245, 220 + n)), max(160, min(245, 222 + n)), max(160, min(245, 225 + n)))

    grid = 256
    for i in range(0, w + 1, grid):
        draw.line([(i, 0), (i, h)], fill=(110, 115, 120), width=6)
        draw.line([(0, i), (w, i)], fill=(110, 115, 120), width=6)
        draw.line([(i+2, 0), (i+2, h)], fill=(245, 248, 250), width=2)
        draw.line([(0, i+2), (w, i+2)], fill=(245, 248, 250), width=2)

    img.save(os.path.join(TEX_DIR, "ceiling_tile.png"))
    print("- ceiling_tile.png updated (1024x1024)")

def generate_metal_lockers():
    print("Generating high-res locker texture...")
    w, h = 512, 1024
    img = Image.new("RGB", (w, h), (40, 65, 95))
    draw = ImageDraw.Draw(img)
    col_w = w // 2

    for c in range(2):
        x0 = c * col_w
        x1 = x0 + col_w
        # Steel door bevel
        draw.rectangle([x0 + 6, 12, x1 - 6, h - 12], fill=(45, 72, 105), outline=(25, 42, 65), width=4)
        draw.rectangle([x0 + 10, 16, x1 - 10, h - 16], outline=(70, 100, 140), width=2)

        # Upper louvers / ventilation vents
        for s in range(8):
            sy = 50 + (s * 14)
            draw.rectangle([x0 + 35, sy, x1 - 35, sy + 6], fill=(18, 30, 48), outline=(28, 48, 75))

        # Chrome door handle & keyhole plate
        hy = h // 2
        draw.rectangle([x1 - 42, hy - 40, x1 - 18, hy + 40], fill=(210, 215, 222), outline=(120, 125, 135), width=2)
        draw.ellipse([x1 - 34, hy - 8, x1 - 26, hy + 8], fill=(25, 25, 30))
        # Handle lever
        draw.rectangle([x1 - 48, hy + 8, x1 - 18, hy + 24], fill=(180, 185, 192), outline=(90, 95, 105))

        # Lower vents
        for s in range(5):
            sy = h - 120 + (s * 14)
            draw.rectangle([x0 + 40, sy, x1 - 40, sy + 6], fill=(18, 30, 48), outline=(28, 48, 75))

    img.save(os.path.join(TEX_DIR, "locker_metal.png"))
    print("- locker_metal.png updated (512x1024)")

def generate_supermarket_shelves():
    print("Generating high-res supermarket shelf texture...")
    w, h = 1024, 1024
    img = Image.new("RGB", (w, h), (85, 90, 98))
    draw = ImageDraw.Draw(img)
    num_tiers = 4
    tier_h = h // num_tiers

    colors = [
        (220, 40, 40), (35, 130, 225), (45, 185, 80),
        (240, 195, 35), (200, 80, 210), (235, 100, 30)
    ]

    for t in range(num_tiers):
        ty = t * tier_h
        # Metal shelf structure
        draw.rectangle([0, ty + tier_h - 24, w, ty + tier_h], fill=(190, 195, 202), outline=(50, 55, 60), width=3)
        # Yellow shelf edge price tag rail
        draw.rectangle([10, ty + tier_h - 20, w - 10, ty + tier_h - 4], fill=(245, 220, 30))

        # Array of grocery boxes / cans / packages
        bx = 15
        while bx < w - 40:
            bw = random.randint(35, 65)
            bh = random.randint(65, tier_h - 35)
            c = random.choice(colors)
            by = ty + tier_h - 24 - bh
            draw.rectangle([bx, by, bx + bw, ty + tier_h - 24], fill=c, outline=(30, 30, 35), width=2)
            # Box branding labels
            draw.rectangle([bx + 6, by + bh//4, bx + bw - 6, by + 3*bh//4], fill=(250, 250, 252), outline=(180, 180, 185))
            # Text lines on label
            for ly in range(by + bh//4 + 8, by + 3*bh//4 - 6, 8):
                draw.line([(bx + 10, ly), (bx + bw - 10, ly)], fill=(40, 40, 45), width=2)
            bx += bw + random.randint(4, 10)

    img.save(os.path.join(TEX_DIR, "shelf_metal.png"))
    print("- shelf_metal.png updated (1024x1024)")

def mirror_to_desktop():
    print(f"Exporting all updated high-res assets to Desktop: {DESKTOP_DIR}")
    for item in os.listdir(TEX_DIR):
        src = os.path.join(TEX_DIR, item)
        dst = os.path.join(DESKTOP_DIR, item)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
    for item in os.listdir(MODEL_DIR):
        src = os.path.join(MODEL_DIR, item)
        dst = os.path.join(DESKTOP_DIR, item)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
    print("Desktop assets synchronized!")

if __name__ == "__main__":
    download_pbr_textures()
    generate_photorealistic_asphalt()
    generate_photorealistic_concrete()
    generate_supermarket_floor()
    generate_ceiling_tile()
    generate_metal_lockers()
    generate_supermarket_shelves()
    mirror_to_desktop()
    print("All textures upgraded to maximum fidelity!")
