"""
Kitten sprite generator for Puppy & Cat Desktop Pet.
Generates an adorable orange tabby / calico kitten with pointy triangular ears,
slender swishing tail, white paws/socks, emerald green eyes, and fine whiskers.
"""
import os
import math
from PIL import Image, ImageDraw
from sprite_generator_common import (
    Canvas, ell, tline, px, W, H, OUT, WHITE, SHADOW,
    draw_zzz, draw_heart, PINK_BEANS
)

FUR = (248, 162, 70, 255)
FUR_LT = (255, 206, 125, 255)
FUR_DK = (206, 116, 38, 255)
STRIPE = (185, 95, 28, 255)
CREAM = (255, 248, 235, 255)

INNER_EAR = (255, 165, 185, 255)
NOSE_PINK = (255, 135, 155, 255)
EYE = (65, 185, 105, 255)
EYE_DK = (25, 20, 18, 255)
BLUSH = (255, 145, 165, 150)
WHISKER = (255, 255, 255, 220)


def create_kitten_sprite(
    bob_y: float = 0.0,
    squish_y: float = 0.0,
    tail_angle: int = 0,
    front_leg_offset: tuple = (0, 0),
    back_leg_offset: tuple = (0, 0),
    pounce: bool = False,
    kneading: bool = False,
    happy_eyes: bool = False,
    blink: bool = False,
    sleeping: bool = False,
    head_offset: tuple = (0, 0),
    zzz_stage: int = 0,
    heart_pos: tuple = None,
    sparkles: bool = False,
) -> Image.Image:
    c = Canvas()
    by = round(bob_y * 1.4)
    sq = round(squish_y)

    # ---------------- Ground shadow
    if not sleeping:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([17, 56, 47, 62], fill=SHADOW)
        c.img.alpha_composite(sh)

    # ---------------- Geometry
    if sleeping:
        head_c = (36, 38)
        body_c = (26, 47)
        body_rx, body_ry = 15, 8.5
        by = 0
    elif pounce:
        # Pounce / batting pose
        head_c = (38 + head_offset[0], 27 + head_offset[1])
        body_c = (25, 42)
        body_rx, body_ry = 13, 8.5
    else:
        head_c = (37 + head_offset[0], 25 + by + sq + head_offset[1])
        body_c = (27, 43 + by + sq // 2)
        body_rx, body_ry = 13, 9.0

    hx, hy = head_c
    bx, byc = body_c

    # ---------------- Slender cat tail with graceful S-curve
    ta = tail_angle
    if sleeping:
        def tail_sleep(d):
            d.arc([8, 42, 22, 53], 90, 270, fill=FUR, width=3)
        c.part(tail_sleep)
    elif pounce:
        # Pounce tail held high and swishing
        def tail_pounce(d):
            pts = [(bx - 9, byc - 2), (bx - 15, byc - 10 + ta * 2), (bx - 12, byc - 18 + ta * 2)]
            for p0, p1 in zip(pts[:-1], pts[1:]):
                tline(d, p0, p1, 3.2, FUR)
            ell(d, pts[-1][0], pts[-1][1], 2.2, 2.2, CREAM)
        c.part(tail_pounce)
    else:
        def tail(d):
            pts = [(bx - 9, byc - 1), (bx - 16, byc - 8 + ta * 2), (bx - 13, byc - 16 + ta * 2)]
            for p0, p1 in zip(pts[:-1], pts[1:]):
                tline(d, p0, p1, 3.0, FUR)
            ell(d, pts[-1][0], pts[-1][1], 2.0, 2.0, CREAM)
            # Tip stripe
            px(d, pts[-1][0], pts[-1][1] + 1, STRIPE)
        c.part(tail)

    # ---------------- Back legs / haunches
    blx, bly = back_leg_offset
    if not sleeping:
        for ox in (-8, -1):
            def bleg(d, ox=ox):
                ell(d, bx + ox + blx, byc + body_ry - 1 + bly, 4.0, 3.0, FUR)
                # White cat socks!
                ell(d, bx + ox + blx, byc + body_ry + bly, 2.2, 1.4, CREAM)
            c.part(bleg)
    else:
        def sleep_paw(d):
            ell(d, 18, 50, 3.8, 2.6, CREAM)
        c.part(sleep_paw)

    # ---------------- Body (orange tabby with stripes and white chest bib)
    def body(d):
        ell(d, bx, byc, body_rx, body_ry, FUR)
        # Soft lighter belly
        ell(d, bx - 2, byc - body_ry * 0.4, body_rx * 0.55, body_ry * 0.35, FUR_LT)
        # White chest bib
        ell(d, bx + 3, byc + body_ry * 0.45, body_rx * 0.65, body_ry * 0.45, CREAM)
        # Tabby stripes across flank
        for sx in (-6, -2, 2):
            d.line([(bx + sx, byc - body_ry + 2), (bx + sx + 1, byc - body_ry + 6)], fill=STRIPE, width=1)
    c.part(body)

    # ---------------- Front legs
    flx, fly = front_leg_offset
    if not sleeping and not pounce and not kneading:
        for ox in (5, 11):
            def fleg(d, ox=ox):
                x0, y0 = bx + ox + flx, byc + body_ry - 1 + fly
                ell(d, x0, y0, 3.2, 3.0, FUR)
                # White paws
                ell(d, x0, y0 + 1, 2.2, 1.6, CREAM)
                px(d, x0 - 1, y0 + 2, PINK_BEANS)
            c.part(fleg)
    elif kneading:
        # Alternating kneading front paws ("making biscuits")
        def knead_legs(d):
            ell(d, bx + 5, byc + body_ry - 2, 3.4, 2.8, CREAM)
            ell(d, bx + 12, byc + body_ry + 1, 3.4, 2.8, CREAM)
        c.part(knead_legs)
    elif pounce:
        # Raised batting paw!
        def pounce_legs(d):
            ell(d, bx + 5, byc + body_ry, 3.2, 2.8, CREAM)
            # Right paw batting in the air
            ell(d, bx + 13, byc + body_ry - 5, 3.4, 3.0, CREAM)
            px(d, bx + 13, byc + body_ry - 5, PINK_BEANS)
        c.part(pounce_legs)
    else:
        def sleep_front(d):
            ell(d, 38, 48, 3.4, 2.4, CREAM)
        c.part(sleep_front)

    # ---------------- Pointy Cat Ears (behind head)
    def ears(d):
        # Left pointy ear
        d.polygon([
            (hx - 11, hy - 4), (hx - 12, hy - 17), (hx - 2, hy - 9)
        ], fill=FUR)
        # Pink inner ear fuzz
        d.polygon([
            (hx - 10, hy - 5), (hx - 11, hy - 14), (hx - 4, hy - 9)
        ], fill=INNER_EAR)

        # Right pointy ear
        d.polygon([
            (hx + 2, hy - 9), (hx + 12, hy - 17), (hx + 11, hy - 4)
        ], fill=FUR)
        # Pink inner ear fuzz
        d.polygon([
            (hx + 4, hy - 9), (hx + 11, hy - 14), (hx + 10, hy - 5)
        ], fill=INNER_EAR)
    c.part(ears)

    # ---------------- Head & Muzzle
    def head(d):
        ell(d, hx, hy, 13.0, 11.0, FUR)
        # Tabby M-marking on forehead
        d.line([(hx - 3, hy - 8), (hx - 1, hy - 5)], fill=STRIPE)
        d.line([(hx - 1, hy - 5), (hx, hy - 7)], fill=STRIPE)
        d.line([(hx, hy - 7), (hx + 1, hy - 5)], fill=STRIPE)
        d.line([(hx + 1, hy - 5), (hx + 3, hy - 8)], fill=STRIPE)

        # Cute white muzzle pillows
        ell(d, hx - 2.8, hy + 4.5, 3.6, 2.8, CREAM)
        ell(d, hx + 2.8, hy + 4.5, 3.6, 2.8, CREAM)
        ell(d, hx, hy + 5.5, 2.5, 2.0, CREAM)
    c.part(head)

    # ---------------- Nose & Whiskers
    def face_details(d):
        # Tiny pink cat nose
        d.polygon([
            (hx - 1.8, hy + 2.8), (hx + 1.8, hy + 2.8),
            (hx, hy + 4.2)
        ], fill=NOSE_PINK)

        # Mouth line
        d.line([(hx, hy + 4.2), (hx, hy + 5.2)], fill=OUT)
        d.line([(hx - 2.5, hy + 5.8), (hx, hy + 5.2)], fill=OUT)
        d.line([(hx, hy + 5.2), (hx + 2.5, hy + 5.8)], fill=OUT)

        # Cute delicate white whiskers
        d.line([(hx - 6, hy + 4), (hx - 14, hy + 2)], fill=WHISKER)
        d.line([(hx - 6, hy + 5), (hx - 14, hy + 6)], fill=WHISKER)
        d.line([(hx + 6, hy + 4), (hx + 14, hy + 2)], fill=WHISKER)
        d.line([(hx + 6, hy + 5), (hx + 14, hy + 6)], fill=WHISKER)
    c.overlay(face_details)

    # ---------------- Eyes
    eye_xs = (hx - 4.8, hx + 4.8)
    ey = hy - 1.0

    def eyes(d):
        for ex in eye_xs:
            if sleeping:
                # Contented sleepy curve
                for dx, dy in ((-2, 0), (-1, 1), (0, 1), (1, 1), (2, 0)):
                    px(d, ex + dx, ey + 1 + dy, OUT)
            elif happy_eyes:
                # Happy cat eye smile ^ ^
                for dx, dy in ((-2, 2), (-1, 1), (0, 0), (1, 1), (2, 2)):
                    px(d, ex + dx, ey + dy, OUT)
            elif blink:
                for dx in (-2, -1, 0, 1, 2):
                    px(d, ex + dx, ey + 1, OUT)
            else:
                # Beautiful emerald cat eyes with vertical slit pupil
                ell(d, ex, ey + 1, 2.6, 3.2, EYE)
                # Slit pupil
                d.line([(ex, ey - 1), (ex, ey + 3)], fill=EYE_DK)
                # Highlights
                px(d, ex - 1, ey - 1, WHITE)
                px(d, ex + 1, ey + 2, WHITE)
    c.overlay(eyes)

    # ---------------- Rosy blush
    def blush(d):
        ell(d, hx - 8.0, hy + 4.2, 2.4, 1.5, BLUSH)
        ell(d, hx + 8.0, hy + 4.2, 2.4, 1.5, BLUSH)
    c.overlay(blush)

    # ---------------- Extras: Zzz's, hearts, sparkles
    if sleeping:
        draw_zzz(c, zzz_stage)
    if heart_pos:
        draw_heart(c, heart_pos[0], heart_pos[1])
    if sparkles:
        def spark(d):
            for sx, sy in ((hx - 11, hy - 9), (hx + 13, hy - 7), (hx - 13, hy + 7)):
                px(d, sx, sy, (255, 235, 140, 255))
                for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    px(d, sx + ox, sy + oy, (255, 235, 140, 255))
        c.overlay(spark)

    return c.img.resize((128, 128), Image.Resampling.NEAREST)


def build_kitten_frames() -> dict:
    """Build full 4-frame animation sequences for all kitten states."""
    k = create_kitten_sprite
    return {
        # IDLE: Sitting gracefully, tail curling, slow blink
        "idle": [
            k(bob_y=0.0, tail_angle=1),
            k(bob_y=-0.4, tail_angle=3),
            k(bob_y=0.0, tail_angle=0),
            k(bob_y=-0.4, tail_angle=-2, blink=True),
        ],
        # WALK: Sleek, graceful cat trot with tail held curved
        "walk": [
            k(bob_y=-0.8, tail_angle=2, front_leg_offset=(2, -2), back_leg_offset=(-2, 0)),
            k(bob_y=0.3, tail_angle=0, front_leg_offset=(0, 0), back_leg_offset=(0, -2)),
            k(bob_y=-0.8, tail_angle=-2, front_leg_offset=(-2, -2), back_leg_offset=(2, 0)),
            k(bob_y=0.3, tail_angle=0, front_leg_offset=(0, 0), back_leg_offset=(0, -1)),
        ],
        # PLAY: Batting paw & playful pounce wiggle!
        "play": [
            k(pounce=True, tail_angle=3, happy_eyes=True),
            k(pounce=True, tail_angle=-3, happy_eyes=True, sparkles=True),
            k(pounce=True, tail_angle=4, happy_eyes=True),
            k(pounce=True, tail_angle=-2, happy_eyes=True),
        ],
        # SLEEP: Curled up in a neat cat loaf/ball with gentle Zzz's
        "sleep": [
            k(sleeping=True, zzz_stage=1),
            k(sleeping=True, zzz_stage=2),
            k(sleeping=True, zzz_stage=3),
            k(sleeping=True, zzz_stage=2),
        ],
        # EAT: Delicate lapping milk & nibbling salmon bits
        "eat": [
            k(bob_y=0.2, head_offset=(2, 4), happy_eyes=True),
            k(bob_y=0.7, squish_y=1, head_offset=(3, 6), happy_eyes=True),
            k(bob_y=-0.2, head_offset=(1, 3), happy_eyes=True, heart_pos=(54, 10)),
            k(bob_y=0.5, head_offset=(3, 5), happy_eyes=True, sparkles=True),
        ],
        # SNUGGLE: Kneading paws ("making biscuits"), purring blush, floating hearts!
        "snuggle": [
            k(kneading=True, tail_angle=2, happy_eyes=True, heart_pos=(52, 12)),
            k(kneading=True, tail_angle=-2, happy_eyes=True, heart_pos=(55, 6), sparkles=True),
            k(kneading=True, tail_angle=3, happy_eyes=True, heart_pos=(50, 10)),
            k(kneading=True, tail_angle=-1, happy_eyes=True, heart_pos=(54, 4), sparkles=True),
        ],
    }


def ensure_kitten_sprites(target_dir: str, force: bool = False) -> None:
    """Export all kitten animation frames into target directory."""
    os.makedirs(target_dir, exist_ok=True)
    frames = build_kitten_frames()
    for state, img_list in frames.items():
        for idx, img in enumerate(img_list, start=1):
            fn = os.path.join(target_dir, f"{state}_{idx}.png")
            if force or not os.path.exists(fn):
                img.save(fn)
