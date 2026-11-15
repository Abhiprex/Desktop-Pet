"""
Furniture sprite generator for Puppy & Cat Desktop Pet.
Generates:
- puppy_bed.png: Cozy blue bolster dog bed with bone-print cushion
- kitten_bed.png: Plush pastel circular cat bed with paw-print cushion
- puppy_bowl.png: Sturdy dog bowl with kibbles & fresh water
- kitten_bowl.png: Cat saucer with tuna snacks & creamy milk
- toy_ball.png: Multi-colored bouncy play ball
"""
import os
from PIL import Image, ImageDraw
from sprite_generator_common import W, H, OUT, WHITE, px, ell

# Furniture dimensions: rendered on 64x64 grid and scaled 2x to 128x128
DOG_BLUE = (65, 125, 225, 255)
DOG_BLUE_DK = (42, 85, 165, 255)
DOG_BLUE_LT = (110, 170, 255, 255)

CAT_PINK = (255, 150, 185, 255)
CAT_PINK_DK = (215, 105, 145, 255)
CAT_PINK_LT = (255, 205, 225, 255)

CUSHION_CREAM = (255, 246, 225, 255)
CUSHION_CREAM_DK = (228, 214, 188, 255)

CUSHION_MINT = (220, 248, 235, 255)
CUSHION_MINT_DK = (185, 220, 205, 255)

WATER_BLUE = (100, 205, 255, 255)
WATER_SH = (60, 155, 215, 255)
WATER_HL = (210, 245, 255, 255)

MILK_WHITE = (252, 252, 250, 255)
MILK_SH = (225, 225, 230, 255)

KIBBLE_GOLD = (218, 150, 52, 255)
KIBBLE_DK = (165, 98, 30, 255)
TUNA_PINK = (245, 115, 125, 255)
TUNA_DK = (195, 75, 88, 255)


def create_puppy_bed_sprite() -> Image.Image:
    """Cozy deep oval dog bed with soft bolster walls and bone motif."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Soft ground shadow
    d.ellipse([10, 48, 54, 60], fill=(0, 0, 0, 40))

    # Outer blue bolster rim
    d.ellipse([10, 25, 54, 55], fill=OUT)
    d.ellipse([11, 26, 53, 54], fill=DOG_BLUE_DK)
    d.ellipse([11, 28, 53, 53], fill=DOG_BLUE)
    d.ellipse([13, 27, 51, 38], fill=DOG_BLUE_LT)

    # Inner cozy cream cushion
    d.ellipse([15, 33, 49, 51], fill=OUT)
    d.ellipse([16, 34, 48, 50], fill=CUSHION_CREAM_DK)
    d.ellipse([17, 34, 47, 48], fill=CUSHION_CREAM)

    # Soft back pillow roll
    d.ellipse([20, 31, 36, 40], fill=WHITE)
    d.ellipse([21, 32, 35, 39], fill=CUSHION_CREAM)

    # Embroidered dog bone in center of bed cushion
    bx, by = 35, 41
    d.line([(bx - 3, by), (bx + 3, by)], fill=DOG_BLUE_DK, width=2)
    for ox, oy in ((-4, -1), (-4, 1), (4, -1), (4, 1)):
        d.ellipse([bx + ox - 1, by + oy - 1, bx + ox + 1, by + oy + 1], fill=DOG_BLUE_DK)
    for ox, oy in ((-4, -1), (-4, 1), (4, -1), (4, 1)):
        d.point((bx + ox, by + oy), fill=DOG_BLUE_LT)

    return img.resize((128, 128), Image.Resampling.NEAREST)


def create_kitten_bed_sprite() -> Image.Image:
    """Plush circular pastel cat bed with soft fleece bolster and embroidered paw."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Ground shadow
    d.ellipse([11, 48, 53, 59], fill=(0, 0, 0, 40))

    # Outer pastel pink fleece rim
    d.ellipse([11, 26, 53, 54], fill=OUT)
    d.ellipse([12, 27, 52, 53], fill=CAT_PINK_DK)
    d.ellipse([12, 29, 52, 52], fill=CAT_PINK)
    d.ellipse([14, 28, 50, 38], fill=CAT_PINK_LT)

    # Inner soft minty cushion
    d.ellipse([16, 34, 48, 50], fill=OUT)
    d.ellipse([17, 35, 47, 49], fill=CUSHION_MINT_DK)
    d.ellipse([18, 35, 46, 48], fill=CUSHION_MINT)

    # Embroidered kitten paw print
    px_c, py_c = 32, 42
    # Main pad
    d.ellipse([px_c - 3, py_c - 2, px_c + 3, py_c + 2], fill=CAT_PINK)
    # 3 Toe beans
    d.ellipse([px_c - 4, py_c - 5, px_c - 2, py_c - 3], fill=CAT_PINK)
    d.ellipse([px_c - 1, py_c - 6, px_c + 1, py_c - 4], fill=CAT_PINK)
    d.ellipse([px_c + 2, py_c - 5, px_c + 4, py_c - 3], fill=CAT_PINK)

    return img.resize((128, 128), Image.Resampling.NEAREST)


def create_puppy_bowl_sprite() -> Image.Image:
    """Sturdy dual-compartment dog bowl: left side crunchy kibbles, right side fresh water."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Shadow
    d.ellipse([14, 46, 50, 56], fill=(0, 0, 0, 42))

    # Outer bowl body
    d.ellipse([14, 28, 50, 52], fill=OUT)
    d.ellipse([15, 29, 49, 51], fill=DOG_BLUE_DK)
    d.ellipse([15, 31, 49, 50], fill=DOG_BLUE)
    d.ellipse([16, 30, 48, 41], fill=DOG_BLUE_LT)

    # Inner split compartment basin
    d.ellipse([17, 33, 47, 45], fill=OUT)
    d.ellipse([18, 34, 46, 44], fill=(30, 45, 65, 255))

    # Left: crunchy kibbles & savory bits
    d.ellipse([19, 35, 32, 43], fill=KIBBLE_DK)
    for kx, ky in ((22, 37), (27, 36), (24, 40), (29, 39)):
        d.ellipse([kx - 2, ky - 1, kx + 2, ky + 1], fill=KIBBLE_GOLD)
        d.point((kx, ky - 1), fill=(255, 240, 150, 255))

    # Right: fresh crystal water
    d.ellipse([32, 35, 45, 43], fill=WATER_SH)
    d.ellipse([33, 35, 44, 42], fill=WATER_BLUE)
    d.line([(35, 37), (41, 37)], fill=WATER_HL)
    d.point((42, 38), fill=WHITE)

    # White bone badge on front of bowl
    d.line([(30, 47), (34, 47)], fill=WHITE, width=2)
    d.point((29, 46), fill=WHITE)
    d.point((29, 48), fill=WHITE)
    d.point((35, 46), fill=WHITE)
    d.point((35, 48), fill=WHITE)

    return img.resize((128, 128), Image.Resampling.NEAREST)


def create_kitten_bowl_sprite() -> Image.Image:
    """Cute cat saucer: left side pink salmon bits, right side creamy fresh milk."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Shadow
    d.ellipse([14, 46, 50, 56], fill=(0, 0, 0, 42))

    # Outer saucer body
    d.ellipse([14, 29, 50, 51], fill=OUT)
    d.ellipse([15, 30, 49, 50], fill=CAT_PINK_DK)
    d.ellipse([15, 32, 49, 49], fill=CAT_PINK)
    d.ellipse([16, 31, 48, 40], fill=CAT_PINK_LT)

    # Inner basin
    d.ellipse([17, 34, 47, 45], fill=OUT)
    d.ellipse([18, 35, 46, 44], fill=(70, 35, 48, 255))

    # Left: pink salmon / tuna treats
    d.ellipse([19, 36, 32, 43], fill=TUNA_DK)
    for tx, ty in ((22, 38), (27, 37), (25, 40), (29, 39)):
        d.ellipse([tx - 2, ty - 1, tx + 2, ty + 1], fill=TUNA_PINK)
        d.point((tx, ty - 1), fill=WHITE)

    # Right: creamy milk
    d.ellipse([32, 36, 45, 43], fill=MILK_SH)
    d.ellipse([33, 36, 44, 42], fill=MILK_WHITE)
    d.line([(36, 37), (40, 37)], fill=WHITE)

    # Cute kitten face badge on front
    d.ellipse([30, 46, 34, 48], fill=WHITE)
    d.point((29, 45), fill=WHITE)
    d.point((35, 45), fill=WHITE)
    d.point((32, 47), fill=CAT_PINK_DK)

    return img.resize((128, 128), Image.Resampling.NEAREST)


def create_toy_ball_sprite() -> Image.Image:
    """Playful striped rubber ball for puppy & kitten play."""
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([2, 2, 29, 29], fill=OUT)
    d.ellipse([3, 3, 28, 28], fill=(255, 80, 110, 255))
    d.pieslice([3, 3, 28, 28], 200, 265, fill=(255, 220, 60, 255))
    d.pieslice([3, 3, 28, 28], 325, 30, fill=(255, 220, 60, 255))
    d.pieslice([3, 3, 28, 28], 85, 145, fill=(80, 195, 255, 255))
    d.ellipse([12, 12, 19, 19], fill=WHITE)
    d.ellipse([7, 6, 12, 10], fill=(255, 255, 255, 180))
    return img.resize((128, 128), Image.Resampling.NEAREST)
