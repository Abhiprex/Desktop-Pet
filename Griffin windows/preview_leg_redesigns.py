import os
import math
from PIL import Image, ImageDraw

artifact_dir = r"C:\Users\abhip\.gemini\antigravity\brain\2dbdee45-de09-4c46-b2d5-01d3f0ea321d"
os.makedirs(artifact_dir, exist_ok=True)

# We will create high-clarity 128x128 previews of the 3 leg design concepts:
# Option A: Tucked / Hovering Cute Paws (Loaf style, zero crowding)
# Option B: Clean 2-Limb Profile (Uncluttered, near paw + near talon, far limbs shadowed)
# Option C: Cute Chubby Baby Paws (Short, rounded, clearly spaced)

def create_base_griffin_body(draw, px, W=128, H=128, eye_circular=True):
    # Palette
    OUTLINE = (38, 22, 12, 255)
    LION_BASE = (235, 148, 45, 255)
    LION_LIGHT = (252, 192, 105, 255)
    LION_SHADOW = (180, 105, 25, 255)
    LION_BELLY = (255, 238, 205, 255)
    LION_TUFT = (175, 75, 18, 255)
    LION_TUFT_LIGHT = (220, 120, 38, 255)
    
    EAGLE_BASE = (252, 248, 238, 255)
    EAGLE_LIGHT = (255, 255, 255, 255)
    EAGLE_SHADOW = (215, 202, 188, 255)
    
    BEAK_GOLD = (255, 190, 22, 255)
    BEAK_LIGHT = (255, 228, 90, 255)
    BEAK_SHADOW = (195, 125, 10, 255)
    BEAK_HOOK = (150, 85, 6, 255)
    BEAK_CERE = (75, 45, 20, 255)
    
    WING_COVERT = (220, 138, 52, 255)
    WING_COVERT_LIGHT = (246, 178, 92, 255)
    WING_COVERT_SHADOW = (172, 98, 30, 255)
    WING_FEATHER = (252, 246, 232, 255)
    WING_FEATHER_SHADOW = (210, 196, 180, 255)
    
    EYE_DARK = (28, 14, 8, 255)
    EYE_AMBER = (185, 90, 15, 255)
    EYE_AMBER_LIGHT = (235, 135, 30, 255)
    BLUSH = (255, 115, 128, 190)

    # Body coordinates at 128x128
    body_cx, body_cy = 52.0, 72.0
    body_rx, body_ry = 26.0, 19.0
    
    # 1. Ground Shadow
    draw.ellipse([24, 110, 104, 124], fill=(24, 16, 12, 55))
    
    # 2. Tail (S-curve)
    tail_pts = [
        (26, 75), (20, 68), (16, 58), (14, 46), (16, 34), (22, 24), (32, 18), (42, 16)
    ]
    for i in range(len(tail_pts) - 1):
        x1, y1 = tail_pts[i]
        x2, y2 = tail_pts[i+1]
        draw.line([x1, y1, x2, y2], fill=OUTLINE, width=6)
        draw.line([x1, y1, x2, y2], fill=LION_BASE, width=4)
        
    # Tail Tuft
    draw.polygon([(40, 16), (48, 10), (56, 16), (54, 24), (46, 26), (38, 22)], fill=LION_TUFT, outline=OUTLINE)
    draw.polygon([(44, 14), (50, 12), (54, 16), (50, 20), (44, 18)], fill=LION_TUFT_LIGHT)
    
    # 3. Torso
    draw.ellipse([body_cx - body_rx, body_cy - body_ry, body_cx + body_rx, body_cy + body_ry], fill=LION_BASE, outline=OUTLINE, width=2)
    # Underbelly
    draw.chord([body_cx - body_rx + 6, body_cy - body_ry + 8, body_cx + body_rx - 10, body_cy + body_ry - 2], start=0, end=180, fill=LION_BELLY)

    # 4. Eagle Cape / Ruff (Mane cascading over chest)
    draw.ellipse([body_cx + 4, body_cy - 16, body_cx + 34, body_cy + 16], fill=EAGLE_BASE, outline=OUTLINE, width=2)
    draw.ellipse([body_cx + 10, body_cy - 12, body_cx + 32, body_cy + 10], fill=EAGLE_LIGHT)

    # 5. Head & Crest
    head_cx, head_cy = 70.0, 50.0
    head_r = 22.0
    
    # 3 Plume Crown
    draw.polygon([(head_cx - 10, head_cy - 12), (head_cx - 26, head_cy - 20), (head_cx - 16, head_cy - 10)], fill=EAGLE_BASE, outline=OUTLINE)
    draw.polygon([(head_cx - 4, head_cy - 16), (head_cx - 16, head_cy - 34), (head_cx - 6, head_cy - 22)], fill=EAGLE_BASE, outline=OUTLINE)
    draw.polygon([(head_cx + 4, head_cy - 18), (head_cx - 4, head_cy - 38), (head_cx + 6, head_cy - 24)], fill=EAGLE_BASE, outline=OUTLINE)
    
    # Dome
    draw.ellipse([head_cx - head_r, head_cy - head_r, head_cx + head_r, head_cy + head_r], fill=EAGLE_BASE, outline=OUTLINE, width=2)
    # Head highlight
    draw.ellipse([head_cx - head_r + 4, head_cy - head_r + 4, head_cx + 4, head_cy], fill=EAGLE_LIGHT)

    # 6. Hooked Beak
    beak_poly = [
        (head_cx + 16, head_cy - 6),
        (head_cx + 26, head_cy - 4),
        (head_cx + 36, head_cy + 2),
        (head_cx + 40, head_cy + 8),
        (head_cx + 38, head_cy + 18), # hook tip downward
        (head_cx + 32, head_cy + 14),
        (head_cx + 24, head_cy + 10),
        (head_cx + 16, head_cy + 8),
    ]
    draw.polygon(beak_poly, fill=BEAK_GOLD, outline=OUTLINE, width=2)
    draw.polygon([(head_cx + 18, head_cy + 8), (head_cx + 28, head_cy + 9), (head_cx + 26, head_cy + 14), (head_cx + 18, head_cy + 12)], fill=BEAK_SHADOW, outline=OUTLINE)
    # Beak bridge light
    draw.line([(head_cx + 18, head_cy - 3), (head_cx + 32, head_cy + 2)], fill=BEAK_LIGHT, width=2)
    # Cere nostril
    draw.ellipse([head_cx + 20, head_cy - 3, head_cx + 23, head_cy], fill=BEAK_CERE)

    # 7. EYE: CIRCULAR & CUTE!
    eye_x, eye_y = head_cx + 6, head_cy - 2
    if eye_circular:
        # Perfectly round, large cute anime eye
        draw.ellipse([eye_x - 7, eye_y - 7, eye_x + 7, eye_y + 7], fill=EYE_DARK)
        draw.ellipse([eye_x - 5, eye_y - 5, eye_x + 5, eye_y + 5], fill=EYE_AMBER)
        draw.ellipse([eye_x - 4, eye_y - 1, eye_x + 4, eye_y + 4], fill=EYE_AMBER_LIGHT)
        draw.ellipse([eye_x - 2, eye_y - 2, eye_x + 2, eye_y + 2], fill=EYE_DARK)
        # Big circular glossy shine
        draw.ellipse([eye_x - 4, eye_y - 5, eye_x - 1, eye_y - 2], fill=(255, 255, 255, 255))
        # Small lower bounce sparkle
        draw.ellipse([eye_x + 1, eye_y + 1, eye_x + 3, eye_y + 3], fill=(255, 255, 255, 220))
    else:
        # Boxy / rectangular eye for comparison
        draw.rectangle([eye_x - 6, eye_y - 6, eye_x + 6, eye_y + 6], fill=EYE_DARK)
        draw.rectangle([eye_x - 4, eye_y - 4, eye_x + 4, eye_y + 4], fill=EYE_AMBER)
        draw.rectangle([eye_x - 3, eye_y - 3, eye_x - 1, eye_y - 1], fill=(255, 255, 255, 255))

    # Rosy Cheek Blush
    draw.ellipse([eye_x - 6, eye_y + 9, eye_x + 2, eye_y + 14], fill=BLUSH)

    # 8. Wings
    w_root_x, w_root_y = body_cx - 2, body_cy - 12
    draw.polygon([
        (w_root_x, w_root_y), (w_root_x - 14, w_root_y - 12),
        (w_root_x - 24, w_root_y - 10), (w_root_x - 14, w_root_y + 4), (w_root_x, w_root_y + 2)
    ], fill=WING_COVERT, outline=OUTLINE, width=2)
    
    primary_wings = [
        [(w_root_x - 16, w_root_y - 12), (w_root_x - 38, w_root_y - 28), (w_root_x - 22, w_root_y - 8)],
        [(w_root_x - 22, w_root_y - 8), (w_root_x - 46, w_root_y - 18), (w_root_x - 24, w_root_y)],
        [(w_root_x - 22, w_root_y - 2), (w_root_x - 42, w_root_y - 4), (w_root_x - 20, w_root_y + 4)],
    ]
    for pw in primary_wings:
        draw.polygon(pw, fill=WING_FEATHER, outline=OUTLINE, width=2)

    return (OUTLINE, LION_BASE, LION_LIGHT, LION_SHADOW, LION_BELLY, BEAK_GOLD, BEAK_LIGHT, BEAK_SHADOW)


def render_option_a_tucked():
    """Option A: Tucked Hovering Paws (Flying baby loaf - 100% clean, zero leg collision)"""
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    px = img.load()
    OUTLINE, LION_BASE, LION_LIGHT, LION_SHADOW, LION_BELLY, TALON_GOLD, TALON_LIGHT, TALON_SHADOW = create_base_griffin_body(draw, px, 128, 128, eye_circular=True)
    
    # Back: Cute rounded lion paw tucked neatly against rear underbelly with 3 pinkish-golden toe beans
    draw.ellipse([30, 84, 46, 96], fill=LION_BASE, outline=OUTLINE, width=2)
    for bx in (33, 38, 43):
        draw.ellipse([bx - 2, 91, bx + 2, 95], fill=LION_LIGHT)
        
    # Front: Adorable little golden raptor talons curled gently against chest
    draw.ellipse([64, 82, 78, 94], fill=TALON_GOLD, outline=OUTLINE, width=2)
    # 3 cute curved talons curled inward
    for tx in (66, 70, 74):
        draw.ellipse([tx - 1, 90, tx + 2, 94], fill=TALON_LIGHT)
        draw.arc([tx - 1, 92, tx + 2, 96], start=0, end=180, fill=OUTLINE, width=2)

    return img


def render_option_b_clean_profile():
    """Option B: Clean 2-Limb Focus Profile (Clear near back paw + near front talon, far limbs shadowed)"""
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    px = img.load()
    OUTLINE, LION_BASE, LION_LIGHT, LION_SHADOW, LION_BELLY, TALON_GOLD, TALON_LIGHT, TALON_SHADOW = create_base_griffin_body(draw, px, 128, 128, eye_circular=True)

    # 1. Far Hind Paw (subtle, tucked behind in shadow)
    draw.ellipse([44, 86, 54, 98], fill=LION_SHADOW, outline=OUTLINE, width=2)
    
    # 2. Near Hind Leg (Chubby lion thigh + clear rounded 3-toed paw)
    # Thigh
    draw.ellipse([22, 74, 38, 92], fill=LION_BASE, outline=OUTLINE, width=2)
    draw.ellipse([24, 76, 34, 88], fill=LION_LIGHT)
    # Resting Paw
    draw.rounded_rectangle([22, 88, 38, 100], radius=4, fill=LION_BASE, outline=OUTLINE, width=2)
    for bx in (25, 30, 35):
        draw.ellipse([bx - 2, 95, bx + 2, 99], fill=LION_LIGHT)

    # Spacious belly clearance (x=39 to x=61 is totally open!)
    
    # 3. Far Front Talon (shadowed behind chest)
    draw.rounded_rectangle([60, 86, 68, 98], radius=3, fill=TALON_SHADOW, outline=OUTLINE, width=2)

    # 4. Near Front Talon (Crisp, solid golden eagle foot with smooth curved claws)
    draw.rounded_rectangle([68, 84, 80, 96], radius=4, fill=TALON_GOLD, outline=OUTLINE, width=2)
    draw.line([(70, 85), (70, 95)], fill=TALON_LIGHT, width=2)
    # Clean, smooth 3 claws at bottom
    for cx in (69, 74, 78):
        draw.arc([cx - 2, 93, cx + 2, 100], start=30, end=150, fill=OUTLINE, width=2)
        draw.ellipse([cx - 1, 94, cx + 1, 98], fill=(32, 20, 14, 255))

    return img


def render_option_c_chubby_baby():
    """Option C: Chubby Baby Feet (Ultra-simple, rounded toddler proportions, zero fussy joints)"""
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    px = img.load()
    OUTLINE, LION_BASE, LION_LIGHT, LION_SHADOW, LION_BELLY, TALON_GOLD, TALON_LIGHT, TALON_SHADOW = create_base_griffin_body(draw, px, 128, 128, eye_circular=True)

    # Back: Short chubby lion paw
    draw.ellipse([26, 84, 42, 98], fill=LION_BASE, outline=OUTLINE, width=2)
    draw.ellipse([28, 86, 38, 92], fill=LION_LIGHT)
    # 3 rounded pill beans
    for bx in (29, 34, 39):
        draw.ellipse([bx - 2, 92, bx + 2, 97], fill=LION_LIGHT)

    # Clear open space under belly
    
    # Front: Short chubby golden baby bird foot
    draw.ellipse([64, 84, 80, 98], fill=TALON_GOLD, outline=OUTLINE, width=2)
    draw.ellipse([66, 86, 76, 92], fill=TALON_LIGHT)
    # 3 rounded golden toes with smooth dark tips
    for tx in (67, 72, 77):
        draw.ellipse([tx - 2, 92, tx + 2, 97], fill=TALON_LIGHT)
        draw.point((tx, 97), fill=(34, 22, 14, 255))

    return img


def generate_previews():
    img_a = render_option_a_tucked()
    img_b = render_option_b_clean_profile()
    img_c = render_option_c_chubby_baby()
    
    img_a.save(os.path.join(artifact_dir, "leg_option_a_tucked.png"))
    img_b.save(os.path.join(artifact_dir, "leg_option_b_profile.png"))
    img_c.save(os.path.join(artifact_dir, "leg_option_c_chubby.png"))
    print("Saved individual leg redesign options")

    # Combined sheet
    sheet = Image.new("RGBA", (3 * 160 + 20, 240), (24, 26, 32, 255))
    sdraw = ImageDraw.Draw(sheet)
    
    sdraw.text((20, 12), "STEP 1: LEG REDESIGN CONCEPTS & CIRCULAR EYES", fill=(255, 230, 160, 255))
    sdraw.text((20, 28), "All previews feature circular eyes + native 128x128 HD clarity. Compare the 3 leg styles below:", fill=(165, 180, 200, 255))

    opts = [
        ("Option A: Tucked Hovering", "Baby loaf pose. Paws tucked neatly under belly. 0% overlap error.", img_a),
        ("Option B: Clean Profile", "Near front talon + near back paw with wide belly clearance.", img_b),
        ("Option C: Chubby Baby Feet", "Short, rounded, simplified toddler paws with smooth toe beans.", img_c)
    ]

    for idx, (title, sub, spr) in enumerate(opts):
        x = 10 + idx * 160
        y = 52
        sdraw.rounded_rectangle([x, y, x + 150, y + 175], radius=8, fill=(35, 38, 48, 255), outline=(60, 68, 85, 255), width=1)
        sheet.alpha_composite(spr, (x + 11, y + 6))
        sdraw.text((x + 8, y + 138), title, fill=(255, 255, 255, 255))
        # wrap subtext
        words = sub.split()
        l1 = " ".join(words[:4])
        l2 = " ".join(words[4:])
        sdraw.text((x + 8, y + 152), l1, fill=(170, 185, 210, 255))
        if l2:
            sdraw.text((x + 8, y + 162), l2, fill=(170, 185, 210, 255))

    sheet_path = os.path.join(artifact_dir, "leg_redesign_comparison.png")
    sheet.save(sheet_path)
    print("Saved leg comparison sheet:", sheet_path)


if __name__ == "__main__":
    generate_previews()
