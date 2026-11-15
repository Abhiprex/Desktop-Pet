import math
import os
from PIL import Image, ImageDraw, ImageFont

artifact_dir = r"C:\Users\abhip\.gemini\antigravity\brain\2dbdee45-de09-4c46-b2d5-01d3f0ea321d"
os.makedirs(artifact_dir, exist_ok=True)

VARIANTS = {
    "1": {
        "id": "royal_sun",
        "name": "Royal Sun Griffin",
        "title": "Variant 1: Royal Sun Griffin",
        "subtitle": "The Noble Golden Herald",
        "desc": "Classic mythological griffin: Tawny lion coat, snow-ivory eagle plumage, 3-plume royal crest, curved golden beak, and flame tail tuft.",
        "colors": ["#EB942D", "#FCF8EE", "#FFBE16", "#201008", "#AA4B10"],
        "OUTLINE": (42, 22, 10, 255),
        "OUTLINE_SOFT": (78, 42, 20, 255),
        "LION_BASE": (235, 148, 45, 255),
        "LION_LIGHT": (252, 190, 102, 255),
        "LION_SHADOW": (180, 105, 25, 255),
        "LION_BELLY": (255, 235, 195, 255),
        "LION_TUFT": (170, 75, 16, 255),
        "LION_TUFT_LIGHT": (215, 120, 38, 255),
        "EAGLE_BASE": (252, 248, 238, 255),
        "EAGLE_LIGHT": (255, 255, 255, 255),
        "EAGLE_SHADOW": (215, 202, 188, 255),
        "BEAK_GOLD": (255, 190, 22, 255),
        "BEAK_LIGHT": (255, 228, 90, 255),
        "BEAK_SHADOW": (200, 130, 10, 255),
        "BEAK_HOOK": (155, 88, 6, 255),
        "BEAK_CERE": (75, 45, 20, 255),
        "TALON_GOLD": (248, 165, 25, 255),
        "TALON_LIGHT": (255, 218, 75, 255),
        "TALON_SHADOW": (195, 118, 12, 255),
        "TALON_DARK_SHADOW": (150, 85, 8, 255),
        "TALON_CLAW": (34, 22, 14, 255),
        "WING_COVERT": (220, 138, 52, 255),
        "WING_COVERT_LIGHT": (246, 178, 92, 255),
        "WING_COVERT_SHADOW": (172, 98, 30, 255),
        "WING_FEATHER": (252, 246, 232, 255),
        "WING_FEATHER_SHADOW": (210, 196, 180, 255),
        "EYE_DARK": (32, 16, 8, 255),
        "EYE_COLOR": (185, 90, 15, 255),
        "EYE_LIGHT": (235, 135, 30, 255),
        "BLUSH": (255, 115, 128, 215),
        "STYLE": "ROYAL",
    },
    "2": {
        "id": "chibi_cloud",
        "name": "Chibi Cloud Griffin",
        "title": "Variant 2: Chibi Cloud Griffin (Pip)",
        "subtitle": "The Ultra-Cute Marshmallow Pip",
        "desc": "Baby puffball aesthetic: Butterscotch honey coat, whipped-cream downy plumage, fluffy round pink pom-pom tail, sparkling bright sapphire anime eyes, and button beak.",
        "colors": ["#F8C473", "#FFF8EE", "#FFD741", "#3C8CE6", "#FFAFBE"],
        "OUTLINE": (38, 26, 22, 255),
        "OUTLINE_SOFT": (72, 48, 40, 255),
        "LION_BASE": (248, 196, 115, 255),
        "LION_LIGHT": (255, 228, 165, 255),
        "LION_SHADOW": (215, 160, 85, 255),
        "LION_BELLY": (255, 250, 238, 255),
        "LION_TUFT": (255, 165, 185, 255),
        "LION_TUFT_LIGHT": (255, 210, 225, 255),
        "EAGLE_BASE": (255, 252, 245, 255),
        "EAGLE_LIGHT": (255, 255, 255, 255),
        "EAGLE_SHADOW": (228, 232, 242, 255),
        "BEAK_GOLD": (255, 215, 65, 255),
        "BEAK_LIGHT": (255, 240, 130, 255),
        "BEAK_SHADOW": (225, 175, 40, 255),
        "BEAK_HOOK": (180, 125, 25, 255),
        "BEAK_CERE": (90, 60, 35, 255),
        "TALON_GOLD": (250, 185, 95, 255),
        "TALON_LIGHT": (255, 215, 145, 255),
        "TALON_SHADOW": (215, 150, 70, 255),
        "TALON_DARK_SHADOW": (175, 115, 45, 255),
        "TALON_CLAW": (50, 35, 28, 255),
        "WING_COVERT": (250, 220, 170, 255),
        "WING_COVERT_LIGHT": (255, 240, 205, 255),
        "WING_COVERT_SHADOW": (225, 190, 135, 255),
        "WING_FEATHER": (240, 248, 255, 255),
        "WING_FEATHER_SHADOW": (195, 225, 250, 255),
        "EYE_DARK": (25, 15, 20, 255),
        "EYE_COLOR": (55, 145, 235, 255),
        "EYE_LIGHT": (135, 210, 255, 255),
        "BLUSH": (255, 120, 150, 240),
        "STYLE": "CHIBI",
    },
    "3": {
        "id": "midnight_shadow",
        "name": "Midnight Shadow Griffin",
        "title": "Variant 3: Midnight Shadow Griffin",
        "subtitle": "The Arcane Night Stalker",
        "desc": "Mystical obsidian panther body, deep twilight plumage, glowing luminous amethyst eyes, moon-silver beak & claws, and arcane violet feather tips.",
        "colors": ["#2A2D3E", "#444A62", "#CDDCF0", "#B941F5", "#7D4BC0"],
        "OUTLINE": (16, 14, 22, 255),
        "OUTLINE_SOFT": (32, 28, 44, 255),
        "LION_BASE": (42, 45, 62, 255),
        "LION_LIGHT": (68, 74, 98, 255),
        "LION_SHADOW": (24, 26, 38, 255),
        "LION_BELLY": (70, 78, 102, 255),
        "LION_TUFT": (135, 70, 210, 255),
        "LION_TUFT_LIGHT": (190, 130, 255, 255),
        "EAGLE_BASE": (32, 36, 52, 255),
        "EAGLE_LIGHT": (58, 65, 92, 255),
        "EAGLE_SHADOW": (18, 20, 32, 255),
        "BEAK_GOLD": (205, 220, 240, 255),
        "BEAK_LIGHT": (242, 248, 255, 255),
        "BEAK_SHADOW": (150, 170, 195, 255),
        "BEAK_HOOK": (100, 120, 145, 255),
        "BEAK_CERE": (22, 26, 38, 255),
        "TALON_GOLD": (175, 192, 215, 255),
        "TALON_LIGHT": (225, 238, 252, 255),
        "TALON_SHADOW": (125, 142, 168, 255),
        "TALON_DARK_SHADOW": (85, 98, 120, 255),
        "TALON_CLAW": (12, 10, 18, 255),
        "WING_COVERT": (48, 42, 70, 255),
        "WING_COVERT_LIGHT": (76, 68, 110, 255),
        "WING_COVERT_SHADOW": (28, 24, 44, 255),
        "WING_FEATHER": (88, 72, 138, 255),
        "WING_FEATHER_SHADOW": (50, 38, 82, 255),
        "EYE_DARK": (10, 8, 16, 255),
        "EYE_COLOR": (185, 65, 245, 255),
        "EYE_LIGHT": (235, 140, 255, 255),
        "BLUSH": (145, 75, 200, 160),
        "STYLE": "SHADOW",
    },
    "4": {
        "id": "arctic_blizzard",
        "name": "Arctic Blizzard Griffin",
        "title": "Variant 4: Arctic Blizzard Griffin",
        "subtitle": "Snow Leopard + Snowy Owl",
        "desc": "Sublime winter predator: Pure snowy owl dome, frosted slate beak, crystalline ice-blue eyes, snow-leopard rosette spots on flank, and a thick ringed snow-leopard tail.",
        "colors": ["#EEF4FA", "#C3D0E0", "#505F73", "#37AFFF", "#A5DAF2"],
        "OUTLINE": (26, 32, 44, 255),
        "OUTLINE_SOFT": (52, 65, 84, 255),
        "LION_BASE": (238, 244, 250, 255),
        "LION_LIGHT": (255, 255, 255, 255),
        "LION_SHADOW": (195, 208, 224, 255),
        "LION_BELLY": (248, 250, 255, 255),
        "LION_TUFT": (145, 170, 200, 255),
        "LION_TUFT_LIGHT": (210, 230, 250, 255),
        "EAGLE_BASE": (252, 254, 255, 255),
        "EAGLE_LIGHT": (255, 255, 255, 255),
        "EAGLE_SHADOW": (198, 212, 228, 255),
        "BEAK_GOLD": (80, 95, 115, 255),
        "BEAK_LIGHT": (130, 150, 175, 255),
        "BEAK_SHADOW": (55, 68, 85, 255),
        "BEAK_HOOK": (38, 48, 62, 255),
        "BEAK_CERE": (45, 55, 70, 255),
        "TALON_GOLD": (185, 210, 230, 255),
        "TALON_LIGHT": (230, 245, 255, 255),
        "TALON_SHADOW": (140, 168, 192, 255),
        "TALON_DARK_SHADOW": (95, 120, 142, 255),
        "TALON_CLAW": (22, 28, 38, 255),
        "WING_COVERT": (215, 230, 245, 255),
        "WING_COVERT_LIGHT": (245, 250, 255, 255),
        "WING_COVERT_SHADOW": (175, 195, 218, 255),
        "WING_FEATHER": (245, 252, 255, 255),
        "WING_FEATHER_SHADOW": (165, 218, 242, 255),
        "EYE_DARK": (16, 22, 32, 255),
        "EYE_COLOR": (55, 175, 250, 255),
        "EYE_LIGHT": (155, 230, 255, 255),
        "BLUSH": (120, 185, 250, 150),
        "STYLE": "ARCTIC",
    },
    "5": {
        "id": "sylvan_forest",
        "name": "Sylvan Forest Gryphlet",
        "title": "Variant 5: Sylvan Forest Gryphlet",
        "subtitle": "Barn Owl + Woodland Lynx",
        "desc": "Whimsical forest guardian: Heart-shaped ivory barn owl face disc, pointed lynx ear tufts with black whisker tips, forest sage-green feather tips, and acorn tail tuft.",
        "colors": ["#D28A44", "#FCF6E8", "#F2E4BC", "#7DA569", "#A5781E"],
        "OUTLINE": (36, 24, 15, 255),
        "OUTLINE_SOFT": (68, 46, 28, 255),
        "LION_BASE": (210, 138, 68, 255),
        "LION_LIGHT": (240, 178, 110, 255),
        "LION_SHADOW": (160, 95, 40, 255),
        "LION_BELLY": (250, 240, 215, 255),
        "LION_TUFT": (125, 68, 25, 255),
        "LION_TUFT_LIGHT": (180, 105, 45, 255),
        "EAGLE_BASE": (252, 246, 232, 255),
        "EAGLE_LIGHT": (255, 255, 245, 255),
        "EAGLE_SHADOW": (210, 188, 160, 255),
        "BEAK_GOLD": (242, 228, 188, 255),
        "BEAK_LIGHT": (255, 248, 225, 255),
        "BEAK_SHADOW": (195, 175, 135, 255),
        "BEAK_HOOK": (140, 118, 85, 255),
        "BEAK_CERE": (95, 68, 42, 255),
        "TALON_GOLD": (165, 105, 52, 255),
        "TALON_LIGHT": (205, 145, 88, 255),
        "TALON_SHADOW": (125, 75, 32, 255),
        "TALON_DARK_SHADOW": (88, 48, 20, 255),
        "TALON_CLAW": (30, 18, 10, 255),
        "WING_COVERT": (175, 115, 55, 255),
        "WING_COVERT_LIGHT": (210, 150, 85, 255),
        "WING_COVERT_SHADOW": (135, 80, 35, 255),
        "WING_FEATHER": (125, 165, 105, 255),
        "WING_FEATHER_SHADOW": (85, 122, 68, 255),
        "EYE_DARK": (26, 18, 8, 255),
        "EYE_COLOR": (165, 120, 30, 255),
        "EYE_LIGHT": (220, 175, 60, 255),
        "BLUSH": (235, 125, 90, 180),
        "STYLE": "SYLVAN",
    },
}


def draw_griffin_variant(cfg: dict, W: int = 64, H: int = 64) -> Image.Image:
    """Draws a high-fidelity 64x64 pixel art sprite for the given variant."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()
    draw = ImageDraw.Draw(img)

    style = cfg["STYLE"]
    is_chibi = style == "CHIBI"

    # Color palette aliases
    OUTLINE = cfg["OUTLINE"]
    OUTLINE_SOFT = cfg["OUTLINE_SOFT"]
    LION_BASE = cfg["LION_BASE"]
    LION_LIGHT = cfg["LION_LIGHT"]
    LION_SHADOW = cfg["LION_SHADOW"]
    LION_BELLY = cfg["LION_BELLY"]
    LION_TUFT = cfg["LION_TUFT"]
    LION_TUFT_LIGHT = cfg["LION_TUFT_LIGHT"]
    EAGLE_BASE = cfg["EAGLE_BASE"]
    EAGLE_LIGHT = cfg["EAGLE_LIGHT"]
    EAGLE_SHADOW = cfg["EAGLE_SHADOW"]
    BEAK_GOLD = cfg["BEAK_GOLD"]
    BEAK_LIGHT = cfg["BEAK_LIGHT"]
    BEAK_SHADOW = cfg["BEAK_SHADOW"]
    BEAK_HOOK = cfg["BEAK_HOOK"]
    BEAK_CERE = cfg["BEAK_CERE"]
    TALON_GOLD = cfg["TALON_GOLD"]
    TALON_LIGHT = cfg["TALON_LIGHT"]
    TALON_SHADOW = cfg["TALON_SHADOW"]
    TALON_CLAW = cfg["TALON_CLAW"]
    WING_COVERT = cfg["WING_COVERT"]
    WING_COVERT_LIGHT = cfg["WING_COVERT_LIGHT"]
    WING_COVERT_SHADOW = cfg["WING_COVERT_SHADOW"]
    WING_FEATHER = cfg["WING_FEATHER"]
    WING_FEATHER_SHADOW = cfg["WING_FEATHER_SHADOW"]
    EYE_DARK = cfg["EYE_DARK"]
    EYE_COLOR = cfg["EYE_COLOR"]
    EYE_LIGHT = cfg["EYE_LIGHT"]
    BLUSH = cfg["BLUSH"]

    # Ground Shadow
    s_rx, s_ry = (17.0, 4.0) if not is_chibi else (15.0, 4.0)
    for y in range(53, 61):
        for x in range(12, 52):
            if ((x - 32.0) / s_rx) ** 2 + ((y - 57.0) / s_ry) ** 2 <= 1.0:
                px[x, y] = (24, 16, 12, 60)

    # Torso Center
    body_cx = 26.0
    body_cy = 36.0
    body_rx = 13.0 if not is_chibi else 11.5
    body_ry = 9.5 if not is_chibi else 10.0

    # 1. Tail (Unique shape per archetype)
    tail_start_x = int(round(body_cx - body_rx + 2.0))
    tail_start_y = int(round(body_cy + 1.0))

    if style == "CHIBI":
        # Fluffy curved baby tail with cute round pom-pom
        tail_segs = [
            (tail_start_x, tail_start_y),
            (tail_start_x - 3, tail_start_y - 3),
            (tail_start_x - 4, tail_start_y - 8),
            (tail_start_x - 3, tail_start_y - 14),
            (tail_start_x + 1, tail_start_y - 17),
        ]
        # Draw tail curve
        for i in range(len(tail_segs) - 1):
            x1, y1 = tail_segs[i]
            x2, y2 = tail_segs[i + 1]
            steps = int(round(max(abs(x2 - x1), abs(y2 - y1), 1) * 3))
            for s in range(steps + 1):
                t_f = s / steps
                tx = int(round(x1 + (x2 - x1) * t_f))
                ty = int(round(y1 + (y2 - y1) * t_f))
                if 0 <= tx < W and 0 <= ty < H:
                    px[tx, ty] = LION_BASE
                    px[tx, ty - 1] = LION_BASE
        # Round fluffy pom-pom puff
        tuft_cx = tail_segs[-1][0] + 3
        tuft_cy = tail_segs[-1][1] - 2
        for ty in range(tuft_cy - 5, tuft_cy + 6):
            for tx in range(tuft_cx - 5, tuft_cx + 6):
                d = ((tx - tuft_cx) / 4.8) ** 2 + ((ty - tuft_cy) / 4.8) ** 2
                if d <= 1.0:
                    if d >= 0.75:
                        px[tx, ty] = OUTLINE
                    elif ty < tuft_cy - 1:
                        px[tx, ty] = LION_TUFT_LIGHT
                    else:
                        px[tx, ty] = LION_TUFT

    elif style == "ARCTIC":
        # Thick ringed snow leopard tail with fluffy tip
        tail_segs = [
            (tail_start_x, tail_start_y),
            (tail_start_x - 2, tail_start_y - 3),
            (tail_start_x - 4, tail_start_y - 8),
            (tail_start_x - 5, tail_start_y - 13),
            (tail_start_x - 3, tail_start_y - 19),
            (tail_start_x + 1, tail_start_y - 23),
            (tail_start_x + 6, tail_start_y - 24),
        ]
        for i in range(len(tail_segs) - 1):
            x1, y1 = tail_segs[i]
            x2, y2 = tail_segs[i + 1]
            steps = int(round(max(abs(x2 - x1), abs(y2 - y1), 1) * 4))
            for s in range(steps + 1):
                t_f = s / steps
                tx = int(round(x1 + (x2 - x1) * t_f))
                ty = int(round(y1 + (y2 - y1) * t_f))
                for w_off in (-1, 0, 1):
                    if 0 <= tx + w_off < W and 0 <= ty < H:
                        px[tx + w_off, ty] = LION_BASE
        # Snow leopard tail dark rings
        for r_x, r_y in [(tail_start_x - 4, tail_start_y - 8), (tail_start_x - 4, tail_start_y - 16), (tail_start_x + 2, tail_start_y - 23)]:
            if 0 <= r_x < W and 0 <= r_y < H:
                px[r_x, r_y] = (145, 160, 185, 255)
        # Big fluffy snow leopard tuft
        tuft_cx = tail_segs[-1][0] + 2
        tuft_cy = tail_segs[-1][1]
        tuft_pts = [
            (tuft_cx - 4, tuft_cy), (tuft_cx - 2, tuft_cy - 4), (tuft_cx + 2, tuft_cy - 5),
            (tuft_cx + 6, tuft_cy - 3), (tuft_cx + 8, tuft_cy), (tuft_cx + 7, tuft_cy + 3),
            (tuft_cx + 3, tuft_cy + 5), (tuft_cx - 1, tuft_cy + 4), (tuft_cx - 3, tuft_cy + 2)
        ]
        draw.polygon(tuft_pts, fill=LION_BASE, outline=OUTLINE)
        px[tuft_cx, tuft_cy] = (160, 180, 210, 255)
        px[tuft_cx + 2, tuft_cy + 1] = (160, 180, 210, 255)

    elif style == "SHADOW":
        # Sleek slender tail with glowing crescent blade tuft
        tail_segs = [
            (tail_start_x, tail_start_y),
            (tail_start_x - 3, tail_start_y - 3),
            (tail_start_x - 5, tail_start_y - 8),
            (tail_start_x - 6, tail_start_y - 14),
            (tail_start_x - 4, tail_start_y - 20),
            (tail_start_x, tail_start_y - 25),
            (tail_start_x + 6, tail_start_y - 27),
        ]
        for i in range(len(tail_segs) - 1):
            x1, y1 = tail_segs[i]
            x2, y2 = tail_segs[i + 1]
            steps = int(round(max(abs(x2 - x1), abs(y2 - y1), 1) * 3))
            for s in range(steps + 1):
                t_f = s / steps
                tx = int(round(x1 + (x2 - x1) * t_f))
                ty = int(round(y1 + (y2 - y1) * t_f))
                if 0 <= tx < W and 0 <= ty < H:
                    px[tx, ty] = LION_BASE
                    px[tx, ty - 1] = LION_BASE
        # Arcane glowing crescent flame tuft
        tuft_cx = tail_segs[-1][0] + 1
        tuft_cy = tail_segs[-1][1]
        crescent_pts = [
            (tuft_cx - 3, tuft_cy), (tuft_cx, tuft_cy - 4), (tuft_cx + 5, tuft_cy - 6),
            (tuft_cx + 9, tuft_cy - 3), (tuft_cx + 10, tuft_cy + 1), (tuft_cx + 7, tuft_cy + 4),
            (tuft_cx + 2, tuft_cy + 3), (tuft_cx + 4, tuft_cy)
        ]
        draw.polygon(crescent_pts, fill=LION_TUFT, outline=OUTLINE)
        px[tuft_cx + 4, tuft_cy - 2] = LION_TUFT_LIGHT
        px[tuft_cx + 6, tuft_cy - 1] = LION_TUFT_LIGHT

    else:
        # Standard Royal & Sylvan: High S-curved lion tail with flame/acorn tuft
        tail_segs = [
            (tail_start_x, tail_start_y),
            (tail_start_x - 2, tail_start_y - 2),
            (tail_start_x - 4, tail_start_y - 6),
            (tail_start_x - 5, tail_start_y - 11),
            (tail_start_x - 4, tail_start_y - 17),
            (tail_start_x - 1, tail_start_y - 22),
            (tail_start_x + 3, tail_start_y - 25),
            (tail_start_x + 8, tail_start_y - 26),
        ]
        for i in range(len(tail_segs) - 1):
            x1, y1 = tail_segs[i]
            x2, y2 = tail_segs[i + 1]
            steps = int(round(max(abs(x2 - x1), abs(y2 - y1), 1) * 3))
            for s in range(steps + 1):
                t_f = s / steps
                tx = int(round(x1 + (x2 - x1) * t_f))
                ty = int(round(y1 + (y2 - y1) * t_f))
                if 0 <= tx < W and 0 <= ty < H:
                    px[tx, ty] = LION_BASE
                    px[tx, ty - 1] = LION_BASE
        tuft_cx = int(round(tail_segs[-1][0] + 2))
        tuft_cy = int(round(tail_segs[-1][1]))
        tuft_pts = [
            (tuft_cx - 4, tuft_cy), (tuft_cx - 2, tuft_cy - 4), (tuft_cx + 2, tuft_cy - 5),
            (tuft_cx + 6, tuft_cy - 3), (tuft_cx + 8, tuft_cy), (tuft_cx + 7, tuft_cy + 3),
            (tuft_cx + 3, tuft_cy + 5), (tuft_cx - 1, tuft_cy + 4), (tuft_cx - 3, tuft_cy + 2)
        ]
        draw.polygon(tuft_pts, fill=LION_TUFT, outline=OUTLINE)
        for dy in range(-2, 3):
            for dx in range(-2, 4):
                tx, ty = tuft_cx + dx, tuft_cy + dy
                if 0 <= tx < W and 0 <= ty < H and px[tx, ty] == LION_TUFT:
                    if dy <= 0 and dx >= 0:
                        px[tx, ty] = LION_TUFT_LIGHT

    # Outline around tail path
    for ty in range(H):
        for tx in range(W):
            if px[tx, ty] == LION_BASE:
                for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nx, ny = tx + ox, ty + oy
                    if 0 <= nx < W and 0 <= ny < H and px[nx, ny] == (0, 0, 0, 0):
                        px[nx, ny] = OUTLINE

    # 2. Far Hind Leg (Lion rear paw behind)
    far_hx = int(round(body_cx - 5.0))
    far_hy = int(round(body_cy + 5.0))
    draw.rectangle([far_hx - 2, far_hy, far_hx + 2, far_hy + 3], fill=LION_SHADOW, outline=OUTLINE)
    draw.polygon([
        (far_hx - 2, far_hy + 3), (far_hx + 2, far_hy + 3),
        (far_hx + 2, far_hy + 5), (far_hx + 1, far_hy + 6),
        (far_hx - 2, far_hy + 6)
    ], fill=LION_SHADOW, outline=OUTLINE)
    if 0 <= far_hy + 5 < H:
        if 0 <= far_hx - 1 < W: px[far_hx - 1, far_hy + 5] = LION_BASE
        if 0 <= far_hx + 1 < W: px[far_hx + 1, far_hy + 5] = LION_BASE

    # 3. Torso
    in_body = [[False] * H for _ in range(W)]
    for y in range(H):
        for x in range(W):
            dx = (x - body_cx) / body_rx
            dy = (y - body_cy) / body_ry
            if dx * dx + dy * dy <= 1.0:
                in_body[x][y] = True

    for y in range(H):
        for x in range(W):
            if in_body[x][y]:
                is_edge = False
                for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nx, ny = x + ox, y + oy
                    if not (0 <= nx < W and 0 <= ny < H and in_body[nx][ny]):
                        is_edge = True
                        break
                if is_edge:
                    px[x, y] = OUTLINE
                elif y > body_cy + 4.0:
                    px[x, y] = LION_SHADOW
                elif y > body_cy + 0.5 and x < body_cx:
                    px[x, y] = LION_BELLY
                elif y < body_cy - 3.0 and x < body_cx + 2:
                    px[x, y] = LION_LIGHT
                else:
                    px[x, y] = LION_BASE

    # Special Body Spots for Arctic Blizzard & Sylvan Forest
    if style == "ARCTIC":
        # Snow leopard rosettes on flank
        for sx, sy in [(20, 34), (21, 35), (17, 36), (18, 37), (23, 38), (24, 38)]:
            if in_body[sx][sy] and px[sx, sy] != OUTLINE:
                px[sx, sy] = (165, 185, 210, 255)
    elif style == "SYLVAN":
        # Lynx tawny flank dapples
        for sx, sy in [(19, 35), (22, 36), (17, 37)]:
            if in_body[sx][sy] and px[sx, sy] != OUTLINE:
                px[sx, sy] = (150, 85, 35, 255)

    # 4. Near Hind Leg (Natural feline anatomy, separated from far leg)
    back_hx = int(round(body_cx - 12.0))
    back_hy = int(round(body_cy + 3.0))
    for y in range(int(back_hy - 4), int(back_hy + 5)):
        for x in range(int(back_hx - 3), int(back_hx + 4)):
            if 0 <= x < W and 0 <= y < H:
                d = ((x - back_hx) / 3.2) ** 2 + ((y - back_hy) / 4.2) ** 2
                if d <= 1.0:
                    if d >= 0.70 and (x <= back_hx - 2 or y >= back_hy + 3):
                        px[x, y] = OUTLINE
                    elif d >= 0.72 and x >= back_hx + 2:
                        px[x, y] = OUTLINE_SOFT
                    elif y < back_hy - 1:
                        px[x, y] = LION_LIGHT
                    elif y > back_hy + 1:
                        px[x, y] = LION_SHADOW
                    else:
                        px[x, y] = LION_BASE

    paw_pts = [
        (back_hx - 3, back_hy + 5), (back_hx + 2, back_hy + 5),
        (back_hx + 2, back_hy + 8), (back_hx + 1, back_hy + 9),
        (back_hx - 2, back_hy + 9), (back_hx - 3, back_hy + 8)
    ]
    draw.polygon(paw_pts, fill=LION_BASE, outline=OUTLINE)
    for toe_off in (-2, 0, 2):
        qx, qy = back_hx + toe_off, back_hy + 8
        if 0 <= qx < W and 0 <= qy < H:
            px[qx, qy] = LION_LIGHT

    # 5. Far Front Talon (Scaly leg & sharp curved claws)
    far_tx = int(round(body_cx + 5.0))
    far_ty = int(round(body_cy + 5.0))
    draw.rectangle([far_tx - 2, far_ty, far_tx + 2, far_ty + 3], fill=TALON_SHADOW, outline=OUTLINE)
    px[far_tx - 1, far_ty + 1] = TALON_GOLD
    px[far_tx - 1, far_ty + 2] = TALON_GOLD
    draw.polygon([
        (far_tx - 2, far_ty + 4), (far_tx + 2, far_ty + 4),
        (far_tx + 2, far_ty + 6), (far_tx + 1, far_ty + 7),
        (far_tx - 2, far_ty + 7)
    ], fill=TALON_SHADOW, outline=OUTLINE)
    px[far_tx - 1, far_ty + 6] = TALON_GOLD
    px[far_tx + 1, far_ty + 6] = TALON_GOLD
    px[far_tx - 2, far_ty + 7] = TALON_CLAW
    px[far_tx, far_ty + 7] = TALON_CLAW
    px[far_tx + 2, far_ty + 7] = TALON_CLAW

    # 6. Eagle Ruff / Mane cascading down chest
    ruff_cx = body_cx + 8.0
    ruff_cy = body_cy - 1.0
    for dy in range(-7, 9):
        for dx in range(-5, 11):
            rx, ry = int(ruff_cx + dx), int(ruff_cy + dy)
            if 0 <= rx < W and 0 <= ry < H:
                d = (dx / 7.5) ** 2 + (dy / 7.0) ** 2
                if d <= 1.0:
                    if d >= 0.80 and (dx >= 4 or dy >= 5 or dx <= -4):
                        px[rx, ry] = OUTLINE
                    elif dy < -2 or dx > 2:
                        px[rx, ry] = EAGLE_LIGHT
                    elif dy > 3:
                        px[rx, ry] = EAGLE_SHADOW
                    else:
                        px[rx, ry] = EAGLE_BASE

    # 7. Near Front Talon
    front_tx = int(round(body_cx + 12.5))
    front_ty = int(round(body_cy + 5.0))
    for fx in (-2, -1, 0, 1, 2):
        if 0 <= front_tx + fx < W and 0 <= front_ty - 1 < H:
            px[front_tx + fx, front_ty - 1] = EAGLE_LIGHT if fx in (-1, 0) else EAGLE_BASE
    draw.rectangle([front_tx - 2, front_ty, front_tx + 2, front_ty + 3], fill=TALON_GOLD, outline=OUTLINE)
    for y_t in range(front_ty, front_ty + 4):
        if 0 <= y_t < H:
            if 0 <= front_tx - 1 < W: px[front_tx - 1, y_t] = TALON_LIGHT
            if 0 <= front_tx < W: px[front_tx, y_t] = TALON_GOLD
            if 0 <= front_tx + 1 < W: px[front_tx + 1, y_t] = TALON_SHADOW
    draw.polygon([
        (front_tx - 3, front_ty + 4), (front_tx + 3, front_ty + 4),
        (front_tx + 3, front_ty + 7), (front_tx + 2, front_ty + 8),
        (front_tx - 2, front_ty + 8), (front_tx - 3, front_ty + 7)
    ], fill=TALON_GOLD, outline=OUTLINE)
    px[front_tx - 2, front_ty + 6] = TALON_LIGHT
    px[front_tx, front_ty + 6] = TALON_LIGHT
    px[front_tx + 2, front_ty + 6] = TALON_GOLD
    px[front_tx - 2, front_ty + 7] = TALON_CLAW
    px[front_tx, front_ty + 7] = TALON_CLAW
    px[front_tx + 2, front_ty + 7] = TALON_CLAW
    px[front_tx, front_ty + 8] = TALON_CLAW

    # 8. Head & Crest (Unique per archetype)
    head_cx = body_cx + (8.5 if not is_chibi else 9.0)
    head_cy = body_cy - (11.0 if not is_chibi else 11.5)
    head_rx = 11.0 if not is_chibi else 12.0
    head_ry = 10.0 if not is_chibi else 11.0

    # Crest / Ears / Tufts
    if style == "ROYAL":
        # 3 sweeping eagle feathers
        crest_polys = [
            [(head_cx - 5, head_cy - 6), (head_cx - 12, head_cy - 10), (head_cx - 8, head_cy - 5)],
            [(head_cx - 2, head_cy - 8), (head_cx - 8, head_cy - 16), (head_cx - 3, head_cy - 11)],
            [(head_cx + 2, head_cy - 9), (head_cx - 2, head_cy - 18), (head_cx + 3, head_cy - 12)],
        ]
        for c_poly in crest_polys:
            draw.polygon(c_poly, fill=EAGLE_BASE, outline=OUTLINE)

    elif style == "CHIBI":
        # Soft fluffy baby down plumes / round bunny-like tufts
        chibi_tufts = [
            [(head_cx - 4, head_cy - 7), (head_cx - 9, head_cy - 13), (head_cx - 4, head_cy - 11)],
            [(head_cx, head_cy - 9), (head_cx - 3, head_cy - 16), (head_cx + 2, head_cy - 12)],
        ]
        for c_poly in chibi_tufts:
            draw.polygon(c_poly, fill=EAGLE_LIGHT, outline=OUTLINE)

    elif style == "SHADOW":
        # Swept-back aerodynamic shadow horns
        shadow_horns = [
            [(head_cx - 4, head_cy - 7), (head_cx - 15, head_cy - 12), (head_cx - 7, head_cy - 6)],
            [(head_cx - 1, head_cy - 9), (head_cx - 12, head_cy - 19), (head_cx - 2, head_cy - 13)],
        ]
        for c_poly in shadow_horns:
            draw.polygon(c_poly, fill=EAGLE_BASE, outline=OUTLINE)
            px[int(c_poly[1][0] + 2), int(c_poly[1][1] + 2)] = (185, 65, 245, 255)

    elif style == "ARCTIC":
        # Snowy owl dome with small feather ear-tufts
        owl_tufts = [
            [(head_cx - 5, head_cy - 7), (head_cx - 8, head_cy - 13), (head_cx - 4, head_cy - 10)],
            [(head_cx + 1, head_cy - 9), (head_cx, head_cy - 14), (head_cx + 3, head_cy - 11)],
        ]
        for c_poly in owl_tufts:
            draw.polygon(c_poly, fill=EAGLE_LIGHT, outline=OUTLINE)

    elif style == "SYLVAN":
        # Tall pointed lynx ears with black whisper tips!
        lynx_ears = [
            [(head_cx - 4, head_cy - 8), (head_cx - 7, head_cy - 17), (head_cx - 1, head_cy - 11)],
            [(head_cx + 1, head_cy - 9), (head_cx + 1, head_cy - 18), (head_cx + 5, head_cy - 12)],
        ]
        for ear in lynx_ears:
            draw.polygon(ear, fill=LION_BASE, outline=OUTLINE)
            px[int(ear[1][0]), int(ear[1][1])] = OUTLINE
            px[int(ear[1][0]), int(ear[1][1] - 1)] = OUTLINE

    # Head fill
    in_head = [[False] * H for _ in range(W)]
    for y in range(H):
        for x in range(W):
            dx = (x - head_cx) / head_rx
            dy = (y - head_cy) / head_ry
            if dx * dx + dy * dy <= 1.0:
                in_head[x][y] = True

    for y in range(H):
        for x in range(W):
            if in_head[x][y]:
                is_edge = False
                for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nx, ny = x + ox, y + oy
                    if not (0 <= nx < W and 0 <= ny < H and in_head[nx][ny]):
                        is_edge = True
                        break
                if is_edge:
                    px[x, y] = OUTLINE
                elif y < head_cy - 4.0 or (x < head_cx and y < head_cy):
                    px[x, y] = EAGLE_LIGHT
                elif y > head_cy + 4.0:
                    px[x, y] = EAGLE_SHADOW
                else:
                    px[x, y] = EAGLE_BASE

    # Cheek fluffs
    for dx_c in range(-3, 4):
        for dy_c in range(-2, 3):
            qx, qy = int(head_cx - 7.0 + dx_c), int(head_cy + 3.5 + dy_c)
            if 0 <= qx < W and 0 <= qy < H and not in_head[qx][qy]:
                dist_c = abs(dx_c) + abs(dy_c)
                if dist_c == 3:
                    px[qx, qy] = OUTLINE
                elif dist_c < 3:
                    px[qx, qy] = EAGLE_LIGHT if dy_c < 0 else EAGLE_BASE

    # Sylvan Forest Barn Owl Facial Heart Mask
    if style == "SYLVAN":
        for y_m in range(int(head_cy - 4), int(head_cy + 5)):
            for x_m in range(int(head_cx - 2), int(head_cx + 8)):
                if in_head[x_m][y_m] and px[x_m, y_m] != OUTLINE:
                    px[x_m, y_m] = (255, 252, 246, 255)

    # 9. Beak (Different proportions & hook curvature per archetype)
    beak_base_x = int(round(head_cx + head_rx - 3.0))
    beak_base_y = int(round(head_cy - 0.5))

    if style == "CHIBI":
        # Shorter, adorable button hook beak
        beak_poly = [
            (beak_base_x, beak_base_y - 2),
            (beak_base_x + 4, beak_base_y - 1),
            (beak_base_x + 7, beak_base_y + 1),
            (beak_base_x + 8, beak_base_y + 3),
            (beak_base_x + 7, beak_base_y + 6),
            (beak_base_x + 5, beak_base_y + 5),
            (beak_base_x + 3, beak_base_y + 4),
            (beak_base_x, beak_base_y + 3),
        ]
        draw.polygon(beak_poly, fill=BEAK_GOLD, outline=OUTLINE)
        lower_beak = [
            (beak_base_x + 1, beak_base_y + 3),
            (beak_base_x + 5, beak_base_y + 4),
            (beak_base_x + 4, beak_base_y + 6),
            (beak_base_x + 1, beak_base_y + 5),
        ]
        draw.polygon(lower_beak, fill=BEAK_SHADOW, outline=OUTLINE)
        px[beak_base_x + 2, beak_base_y] = BEAK_LIGHT
        px[beak_base_x + 3, beak_base_y] = BEAK_LIGHT
    else:
        # Standard noble / sharp raptor hooked beak
        beak_poly = [
            (beak_base_x, beak_base_y - 3),
            (beak_base_x + 5, beak_base_y - 2),
            (beak_base_x + 9, beak_base_y + 1),
            (beak_base_x + 11, beak_base_y + 4),
            (beak_base_x + 10, beak_base_y + 8),
            (beak_base_x + 8, beak_base_y + 6),
            (beak_base_x + 4, beak_base_y + 4),
            (beak_base_x, beak_base_y + 3),
        ]
        draw.polygon(beak_poly, fill=BEAK_GOLD, outline=OUTLINE)
        lower_beak = [
            (beak_base_x + 1, beak_base_y + 3),
            (beak_base_x + 6, beak_base_y + 4),
            (beak_base_x + 5, beak_base_y + 7),
            (beak_base_x + 1, beak_base_y + 6),
        ]
        draw.polygon(lower_beak, fill=BEAK_SHADOW, outline=OUTLINE)
        for bx in range(beak_base_x + 1, beak_base_x + 9):
            for by in range(beak_base_y - 2, beak_base_y + 2):
                if 0 <= bx < W and 0 <= by < H and px[bx, by] == BEAK_GOLD and by <= beak_base_y - 1:
                    px[bx, by] = BEAK_LIGHT
        cere_x = beak_base_x + 2
        cere_y = beak_base_y - 1
        if 0 <= cere_x < W and 0 <= cere_y < H:
            px[cere_x, cere_y] = BEAK_CERE
        if 0 <= beak_base_x + 9 < W and 0 <= beak_base_y + 7 < H:
            px[beak_base_x + 9, beak_base_y + 7] = BEAK_HOOK

    # 10. Eye (Expressive eye adapted to archetype)
    eye_x = int(round(head_cx + 2.5))
    eye_y = int(round(head_cy - 1.5))

    for dy in (-3, -2, -1, 0, 1, 2):
        for dx in (-2, -1, 0, 1, 2):
            if 0 <= eye_x + dx < W and 0 <= eye_y + dy < H:
                if abs(dx) == 2 or abs(dy) >= 2:
                    px[eye_x + dx, eye_y + dy] = EYE_DARK
                else:
                    px[eye_x + dx, eye_y + dy] = EYE_COLOR

    px[eye_x, eye_y + 1] = EYE_LIGHT
    px[eye_x + 1, eye_y + 1] = EYE_LIGHT
    px[eye_x, eye_y] = EYE_DARK
    # Double sparkle for Chibi Pip
    px[eye_x - 1, eye_y - 1] = (255, 255, 255, 255)
    px[eye_x, eye_y - 1] = (255, 255, 255, 255)
    px[eye_x - 1, eye_y] = (255, 255, 255, 255)
    if is_chibi:
        px[eye_x + 1, eye_y + 1] = (255, 255, 255, 220)
    else:
        px[eye_x + 1, eye_y] = (255, 255, 255, 180)

    # Cheek Blush
    cheek_x = eye_x - 1
    cheek_y = eye_y + 4
    for dx in (-2, -1, 0, 1):
        for dy in (0, 1):
            qx, qy = cheek_x + dx, cheek_y + dy
            if 0 <= qx < W and 0 <= qy < H and in_head[qx][qy]:
                px[qx, qy] = BLUSH

    # 11. Feathered Wings (Layered coverts + flight feathers)
    wing_root_x = int(round(body_cx - 1.0))
    wing_root_y = int(round(body_cy - 5.0))

    covert_pts = [
        (wing_root_x, wing_root_y), (wing_root_x - 6, wing_root_y - 6),
        (wing_root_x - 11, wing_root_y - 5), (wing_root_x - 6, wing_root_y + 2),
        (wing_root_x, wing_root_y + 1)
    ]
    draw.polygon(covert_pts, fill=WING_COVERT, outline=OUTLINE)
    primary_feathers = [
        [(wing_root_x - 7, wing_root_y - 6), (wing_root_x - 17, wing_root_y - 14), (wing_root_x - 10, wing_root_y - 4)],
        [(wing_root_x - 10, wing_root_y - 4), (wing_root_x - 21, wing_root_y - 9), (wing_root_x - 11, wing_root_y)],
        [(wing_root_x - 10, wing_root_y - 1), (wing_root_x - 19, wing_root_y - 2), (wing_root_x - 9, wing_root_y + 2)],
    ]
    for f_poly in primary_feathers:
        draw.polygon(f_poly, fill=WING_FEATHER, outline=OUTLINE)

    for wy in range(max(0, wing_root_y - 28), min(H, wing_root_y + 24)):
        for wx in range(max(0, wing_root_x - 26), min(W, wing_root_x + 12)):
            if px[wx, wy] == WING_COVERT:
                if wy < wing_root_y - 3 and wx > wing_root_x - 3:
                    px[wx, wy] = WING_COVERT_LIGHT
                elif wy > wing_root_y + 2:
                    px[wx, wy] = WING_COVERT_SHADOW
            elif px[wx, wy] == WING_FEATHER:
                if wy > wing_root_y + 4 or (wx < wing_root_x - 14 and wy > wing_root_y):
                    px[wx, wy] = WING_FEATHER_SHADOW

    return img


def generate_all():
    print(f"Generating griffin variant assets in: {artifact_dir}")

    rendered_64 = {}
    rendered_128 = {}

    for k, cfg in VARIANTS.items():
        img64 = draw_griffin_variant(cfg)
        rendered_64[k] = img64
        # Crisp integer scaling (nearest neighbor)
        img128 = img64.resize((128, 128), Image.Resampling.NEAREST)
        rendered_128[k] = img128

        # Save individual variant preview
        fname = f"griffin_variant_{k}_{cfg['id']}.png"
        fpath = os.path.join(artifact_dir, fname)
        img128.save(fpath, format="PNG")
        print(f"Saved: {fname}")

    # Generate Comparison Sheet (5 columns side-by-side with titles and stats)
    comp_w = 5 * 180 + 20
    comp_h = 320
    comp_img = Image.new("RGBA", (comp_w, comp_h), (24, 26, 32, 255))
    comp_draw = ImageDraw.Draw(comp_img)

    # Title header
    comp_draw.text((20, 14), "BABY GRIFFIN ARCHETYPE SHOWCASE", fill=(255, 230, 160, 255))
    comp_draw.text((20, 32), "Compare 5 distinct design directions. Each features fully separated paws & sharp raptor talons.", fill=(160, 175, 195, 255))

    for idx, (k, cfg) in enumerate(VARIANTS.items()):
        card_x = 10 + idx * 180
        card_y = 60

        # Card background
        comp_draw.rounded_rectangle([card_x, card_y, card_x + 170, card_y + 245], radius=8, fill=(34, 38, 48, 255), outline=(55, 62, 78, 255), width=1)

        # Sprite placement
        spr = rendered_128[k]
        comp_img.alpha_composite(spr, (card_x + 21, card_y + 10))

        # Title text
        comp_draw.text((card_x + 10, card_y + 145), cfg["name"], fill=(255, 255, 255, 255))
        comp_draw.text((card_x + 10, card_y + 162), cfg["subtitle"], fill=(180, 195, 220, 255))

        # Color palette swatches
        for c_idx, hex_c in enumerate(cfg["colors"]):
            comp_draw.rectangle([card_x + 10 + c_idx * 16, card_y + 185, card_x + 22 + c_idx * 16, card_y + 197], fill=hex_c, outline=(20, 20, 20, 255))

        # Archetype badge
        badge_text = f"Option {k}"
        comp_draw.rounded_rectangle([card_x + 10, card_y + 210, card_x + 80, card_y + 230], radius=4, fill=(50, 60, 80, 255))
        comp_draw.text((card_x + 18, card_y + 213), badge_text, fill=(240, 245, 255, 255))

    comp_path = os.path.join(artifact_dir, "variants_comparison.png")
    comp_img.save(comp_path, format="PNG")
    print(f"Saved comparison sheet: {comp_path}")


if __name__ == "__main__":
    generate_all()
