import os
import math
from PIL import Image, ImageDraw

artifact_dir = r"C:\Users\abhip\.gemini\antigravity\brain\2dbdee45-de09-4c46-b2d5-01d3f0ea321d"
os.makedirs(artifact_dir, exist_ok=True)

# Principles of ULTRA-CUTE Chibi Character Design (Sanrio / Pokémon / Tamagotchi):
# 1. NO predatory hooked beak: Tiny cute triangular/rounded chick beak (gentle, happy)
# 2. NO raptor glare: Huge, friendly, glossy dark anime boba eyes with big round sparkles
# 3. Soft, chubby, round marshmallow proportions (60% head, 40% body)
# 4. Cute soft kitten ears + feathered tufts
# 5. Adorable little kitten paws with pink toe beans (no intimidating claws)
# 6. Fluffy rounded flutter wings + pom-pom tail

def draw_ultra_cute_griffin(style="pip"):
    W, H = 128, 128
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if style == "pip":
        # Warm golden honey & whipped cream
        OUTLINE = (42, 28, 20, 255)
        BODY_MAIN = (252, 200, 115, 255)     # Warm honey butter
        BODY_LIGHT = (255, 225, 160, 255)
        BODY_SHADOW = (225, 165, 80, 255)
        CHEST_WHITE = (255, 252, 246, 255)   # Fluffy cream
        BEAK_COLOR = (255, 185, 45, 255)     # Cute apricot gold
        BEAK_LIGHT = (255, 220, 110, 255)
        EYE_MAIN = (28, 18, 24, 255)         # Deep warm boba dark
        EYE_IRIS = (65, 120, 215, 255)       # Sapphire glow at bottom
        BLUSH_COLOR = (255, 120, 145, 180)   # Rosy pink blush
        BEANS = (255, 165, 180, 255)         # Pink toe beans
        TAIL_TUFT = (255, 170, 185, 255)     # Pink pastel pom-pom
        WING_COLOR = (255, 245, 230, 255)
    elif style == "breeze":
        # Pastel cloud & sky
        OUTLINE = (30, 32, 48, 255)
        BODY_MAIN = (220, 232, 252, 255)
        BODY_LIGHT = (245, 250, 255, 255)
        BODY_SHADOW = (185, 205, 235, 255)
        CHEST_WHITE = (255, 255, 255, 255)
        BEAK_COLOR = (255, 195, 75, 255)
        BEAK_LIGHT = (255, 230, 135, 255)
        EYE_MAIN = (22, 20, 34, 255)
        EYE_IRIS = (95, 75, 200, 255)        # Amethyst glow
        BLUSH_COLOR = (255, 130, 165, 175)
        BEANS = (255, 180, 200, 255)
        TAIL_TUFT = (180, 215, 255, 255)
        WING_COLOR = (245, 250, 255, 255)
    else: # "sunny"
        # Baby chick yellow & butterscotch
        OUTLINE = (45, 30, 15, 255)
        BODY_MAIN = (255, 218, 105, 255)
        BODY_LIGHT = (255, 240, 165, 255)
        BODY_SHADOW = (228, 180, 70, 255)
        CHEST_WHITE = (255, 255, 245, 255)
        BEAK_COLOR = (255, 155, 45, 255)
        BEAK_LIGHT = (255, 200, 105, 255)
        EYE_MAIN = (25, 18, 12, 255)
        EYE_IRIS = (145, 80, 25, 255)        # Amber chocolate glow
        BLUSH_COLOR = (255, 110, 130, 180)
        BEANS = (255, 155, 170, 255)
        TAIL_TUFT = (255, 180, 90, 255)
        WING_COLOR = (255, 250, 230, 255)

    # 1. Soft Ground Shadow
    draw.ellipse([32, 108, 96, 122], fill=(30, 20, 20, 45))

    # Center positions: Big round head, plump cuddly body
    head_cx, head_cy = 64.0, 50.0
    body_cx, body_cy = 60.0, 78.0

    # 2. Cute Pom-Pom Tail
    tail_pts = [(body_cx - 16, body_cy + 2), (body_cx - 24, body_cy - 4), (body_cx - 30, body_cy - 12)]
    draw.line(tail_pts, fill=OUTLINE, width=5)
    draw.line(tail_pts, fill=BODY_MAIN, width=3)
    # Fluffy round pom-pom at tip
    draw.ellipse([body_cx - 40, body_cy - 22, body_cx - 24, body_cy - 6], fill=TAIL_TUFT, outline=OUTLINE, width=2)
    draw.ellipse([body_cx - 36, body_cy - 20, body_cx - 28, body_cy - 12], fill=(255, 255, 255, 200))

    # 3. Fluffy Chubby Torso
    draw.ellipse([body_cx - 22, body_cy - 14, body_cx + 22, body_cy + 16], fill=BODY_MAIN, outline=OUTLINE, width=2)
    # Cream Belly
    draw.ellipse([body_cx - 16, body_cy - 6, body_cx + 18, body_cy + 14], fill=CHEST_WHITE)

    # 4. Cute Little Hovering / Loafing Kitten Paws
    # Back Paw
    draw.ellipse([body_cx - 18, body_cy + 8, body_cx - 2, body_cy + 20], fill=BODY_MAIN, outline=OUTLINE, width=2)
    for bx in (-14, -10, -6):
        draw.ellipse([body_cx + bx - 1, body_cy + 13, body_cx + bx + 1, body_cy + 17], fill=BEANS)
    # Front Paw
    draw.ellipse([body_cx + 8, body_cy + 8, body_cx + 24, body_cy + 20], fill=BODY_MAIN, outline=OUTLINE, width=2)
    for fx in (12, 16, 20):
        draw.ellipse([body_cx + fx - 1, body_cy + 13, body_cx + fx + 1, body_cy + 17], fill=BEANS)

    # 5. Adorable Little Rounded Wings (Fluffy baby chick/angel wings)
    wing_poly = [
        (body_cx - 6, body_cy - 6),
        (body_cx - 18, body_cy - 18),
        (body_cx - 28, body_cy - 16),
        (body_cx - 34, body_cy - 6),
        (body_cx - 28, body_cy + 6),
        (body_cx - 14, body_cy + 8),
        (body_cx - 4, body_cy + 2),
    ]
    draw.polygon(wing_poly, fill=WING_COLOR, outline=OUTLINE, width=2)
    # Feather vane accents
    draw.line([(body_cx - 22, body_cy - 10), (body_cx - 12, body_cy + 2)], fill=BODY_LIGHT, width=2)
    draw.line([(body_cx - 28, body_cy - 2), (body_cx - 16, body_cy + 4)], fill=BODY_LIGHT, width=2)

    # 6. Big Fluffy Kitten / Griffin Ears with interior pink
    # Left Ear
    draw.polygon([(head_cx - 24, head_cy - 16), (head_cx - 30, head_cy - 34), (head_cx - 12, head_cy - 24)], fill=BODY_MAIN, outline=OUTLINE, width=2)
    draw.polygon([(head_cx - 22, head_cy - 18), (head_cx - 26, head_cy - 30), (head_cx - 15, head_cy - 23)], fill=BEANS)
    # Right Ear
    draw.polygon([(head_cx + 12, head_cy - 24), (head_cx + 30, head_cy - 34), (head_cx + 24, head_cy - 16)], fill=BODY_MAIN, outline=OUTLINE, width=2)
    draw.polygon([(head_cx + 15, head_cy - 23), (head_cx + 26, head_cy - 30), (head_cx + 22, head_cy - 18)], fill=BEANS)

    # Soft Feather Crest Tuft between ears
    draw.ellipse([head_cx - 6, head_cy - 30, head_cx + 6, head_cy - 20], fill=CHEST_WHITE, outline=OUTLINE, width=2)

    # 7. Big Round Marshmallow Head
    head_rx, head_ry = 27.0, 24.0
    draw.ellipse([head_cx - head_rx, head_cy - head_ry, head_cx + head_rx, head_cy + head_ry], fill=BODY_MAIN, outline=OUTLINE, width=2)
    # Soft forehead light
    draw.ellipse([head_cx - 18, head_cy - 20, head_cx + 18, head_cy - 4], fill=BODY_LIGHT)

    # Fluffy White Baby Cheek Tufts
    draw.ellipse([head_cx - head_rx - 2, head_cy + 2, head_cx - head_rx + 10, head_cy + 16], fill=CHEST_WHITE, outline=OUTLINE, width=2)
    draw.ellipse([head_cx + head_rx - 10, head_cy + 2, head_cx + head_rx + 2, head_cy + 16], fill=CHEST_WHITE, outline=OUTLINE, width=2)

    # 8. HUGE, SOULFUL, GLOSSY ANIME BOBA EYES (100% Friendly & Cute!)
    # Left Eye
    lx, ly = head_cx - 12, head_cy + 2
    draw.ellipse([lx - 7, ly - 9, lx + 7, ly + 9], fill=EYE_MAIN)
    draw.arc([lx - 7, ly - 9, lx + 7, ly + 9], start=20, end=160, fill=EYE_IRIS, width=3)
    # Big sparkling specular reflection (upper-left)
    draw.ellipse([lx - 4, ly - 6, lx + 1, ly - 1], fill=(255, 255, 255, 255))
    # Small twinkle reflection (lower-right)
    draw.ellipse([lx + 2, ly + 2, lx + 4, ly + 5], fill=(255, 255, 255, 230))

    # Right Eye
    rx, ry = head_cx + 12, head_cy + 2
    draw.ellipse([rx - 7, ry - 9, rx + 7, ry + 9], fill=EYE_MAIN)
    draw.arc([rx - 7, ry - 9, rx + 7, ry + 9], start=20, end=160, fill=EYE_IRIS, width=3)
    # Big sparkling specular reflection (upper-left)
    draw.ellipse([rx - 4, ry - 6, rx + 1, ry - 1], fill=(255, 255, 255, 255))
    # Small twinkle reflection (lower-right)
    draw.ellipse([rx + 2, ry + 2, rx + 4, ry + 5], fill=(255, 255, 255, 230))

    # 9. TINY, ADORABLE BUTTON BEAK (NO Scary Predatory Hook!)
    # A sweet, rounded, petite baby-chick beak: cute little triangle
    draw.polygon([(head_cx - 4, head_cy + 4), (head_cx + 4, head_cy + 4), (head_cx, head_cy + 10)], fill=BEAK_COLOR, outline=OUTLINE, width=2)
    draw.polygon([(head_cx - 3, head_cy + 5), (head_cx + 3, head_cy + 5), (head_cx, head_cy + 7)], fill=BEAK_LIGHT)

    # 10. Big Rosy Blush Cheeks
    draw.ellipse([lx - 8, ly + 6, lx + 2, ly + 13], fill=BLUSH_COLOR)
    draw.ellipse([rx - 2, ry + 6, rx + 8, ry + 13], fill=BLUSH_COLOR)

    # 11. Cute little heart floating above
    draw.polygon([(head_cx + 18, head_cy - 28), (head_cx + 22, head_cy - 34), (head_cx + 26, head_cy - 28), (head_cx + 22, head_cy - 24)], fill=(255, 105, 130, 255))
    draw.ellipse([head_cx + 18, head_cy - 32, head_cx + 22, head_cy - 28], fill=(255, 105, 130, 255))
    draw.ellipse([head_cx + 22, head_cy - 32, head_cx + 26, head_cy - 28], fill=(255, 105, 130, 255))

    return img


def generate_all():
    pip_img = draw_ultra_cute_griffin("pip")
    breeze_img = draw_ultra_cute_griffin("breeze")
    sunny_img = draw_ultra_cute_griffin("sunny")

    pip_img.save(os.path.join(artifact_dir, "cute_griffin_pip.png"))
    breeze_img.save(os.path.join(artifact_dir, "cute_griffin_breeze.png"))
    sunny_img.save(os.path.join(artifact_dir, "cute_griffin_sunny.png"))
    print("Saved individual cute griffin images")

    # Comparison sheet
    sheet = Image.new("RGBA", (3 * 160 + 20, 230), (24, 26, 32, 255))
    sdraw = ImageDraw.Draw(sheet)

    sdraw.text((20, 10), "PURE CUTE / CHIBI BABY GRIFFIN REDESIGN", fill=(255, 225, 160, 255))
    sdraw.text((20, 26), "Zero scary raptor hooks. Zero angry eyes. 100% cozy baby kitten + chick fluff!", fill=(170, 185, 210, 255))

    cards = [
        ("Style 1: Pip (Honey & Cream)", "Cute button beak, boba eyes, soft kitten ears, pink toe beans.", pip_img),
        ("Style 2: Breeze (Cloud Pastel)", "Dreamy cloud feathers, amethyst boba eyes, pastel pom-pom.", breeze_img),
        ("Style 3: Sunny (Buttercup Chick)", "Bright cheerful honey chick fluff, warm amber eyes, sweet smile.", sunny_img),
    ]

    for idx, (title, desc, img_asset) in enumerate(cards):
        x = 10 + idx * 160
        y = 48
        sdraw.rounded_rectangle([x, y, x + 150, y + 172], radius=8, fill=(34, 38, 48, 255), outline=(58, 66, 82, 255), width=1)
        sheet.alpha_composite(img_asset, (x + 11, y + 4))
        sdraw.text((x + 8, y + 134), title, fill=(255, 255, 255, 255))
        words = desc.split()
        l1 = " ".join(words[:4])
        l2 = " ".join(words[4:])
        sdraw.text((x + 8, y + 148), l1, fill=(170, 185, 210, 255))
        if l2:
            sdraw.text((x + 8, y + 158), l2, fill=(170, 185, 210, 255))

    comp_path = os.path.join(artifact_dir, "cute_griffins_comparison.png")
    sheet.save(comp_path)
    print("Saved cute comparison sheet:", comp_path)


if __name__ == "__main__":
    generate_all()
