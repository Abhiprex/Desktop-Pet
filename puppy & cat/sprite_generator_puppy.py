"""
Puppy sprite generator for Puppy & Cat Desktop Pet.
Generates a warm, golden retriever / shiba puppy with floppy ears, wagging tail,
collar with golden tag, happy tongue pant, and expressive puppy boba eyes.
"""
import os
import math
from PIL import Image, ImageDraw
from sprite_generator_common import (
    Canvas, ell, tline, px, W, H, OUT, WHITE, SHADOW,
    draw_zzz, draw_heart, PINK_BEANS
)

FUR = (248, 185, 75, 255)
FUR_LT = (255, 220, 125, 255)
FUR_DK = (212, 142, 45, 255)
CREAM = (255, 246, 226, 255)
CREAM_DK = (228, 215, 190, 255)

EAR = (205, 135, 42, 255)
EAR_DK = (175, 108, 30, 255)
EAR_LT = (230, 160, 65, 255)

COLLAR = (235, 55, 60, 255)
TAG_GOLD = (255, 220, 50, 255)

TONGUE = (255, 128, 150, 255)
NOSE = (35, 25, 22, 255)
EYE = (35, 24, 18, 255)
BLUSH = (255, 140, 160, 160)


def create_puppy_sprite(
    bob_y: float = 0.0,
    squish_y: float = 0.0,
    tail_angle: int = 0,
    front_leg_offset: tuple = (0, 0),
    back_leg_offset: tuple = (0, 0),
    ear_flop: int = 0,
    happy_eyes: bool = False,
    blink: bool = False,
    sleeping: bool = False,
    tongue_out: bool = False,
    play_bow: bool = False,
    head_offset: tuple = (0, 0),
    zzz_stage: int = 0,
    heart_pos: tuple = None,
    sparkles: bool = False,
) -> Image.Image:
    c = Canvas()
    by = round(bob_y * 1.5)
    sq = round(squish_y)

    # ---------------- Ground shadow
    if not sleeping:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([16, 56, 48, 62], fill=SHADOW)
        c.img.alpha_composite(sh)

    # ---------------- Geometry
    if sleeping:
        head_c = (35, 38)
        body_c = (27, 47)
        body_rx, body_ry = 16, 9
        by = 0
    elif play_bow:
        # Play bow: front down, rump up!
        head_c = (39 + head_offset[0], 34 + head_offset[1])
        body_c = (25, 40)
        body_rx, body_ry = 14, 8.5
    else:
        head_c = (37 + head_offset[0], 25 + by + sq + head_offset[1])
        body_c = (27, 43 + by + sq // 2)
        body_rx, body_ry = 14, 9.5

    hx, hy = head_c
    bx, byc = body_c

    # ---------------- Tail (curled fluffy puppy tail)
    ta = tail_angle
    if sleeping:
        def tail_sleep(d):
            d.arc([10, 43, 22, 54], 90, 270, fill=FUR, width=4)
        c.part(tail_sleep)
    elif play_bow:
        # Tail held high up and wagging excited!
        def tail_bow(d):
            tline(d, (bx - 10, byc - 4), (bx - 16, byc - 16 + ta * 2), 4, FUR)
            ell(d, bx - 16, byc - 16 + ta * 2, 3.2, 3.2, FUR_LT)
        c.part(tail_bow)
    else:
        def tail(d):
            tline(d, (bx - 10, byc - 2), (bx - 17, byc - 11 + ta * 2), 3.8, FUR)
            ell(d, bx - 17, byc - 11 + ta * 2, 3.0, 3.0, FUR_LT)
        c.part(tail)

    # ---------------- Back legs / haunches
    blx, bly = back_leg_offset
    if not sleeping and not play_bow:
        for ox in (-8, -1):
            def bleg(d, ox=ox):
                ell(d, bx + ox + blx, byc + body_ry - 1 + bly, 4.4, 3.2, FUR)
                ell(d, bx + ox + blx, byc + body_ry + bly, 2.0, 1.3, PINK_BEANS)
            c.part(bleg)
    elif play_bow:
        # Elevated hind legs
        def bow_legs(d):
            ell(d, bx - 6, byc + body_ry + 2, 3.8, 3.0, FUR)
            ell(d, bx, byc + body_ry + 1, 3.8, 3.0, FUR)
        c.part(bow_legs)
    else:
        # Tucked sleeping hind paw
        def sleep_paw(d):
            ell(d, 18, 51, 4.0, 2.8, FUR)
        c.part(sleep_paw)

    # ---------------- Body (warm golden with cream tummy)
    def body(d):
        ell(d, bx, byc, body_rx, body_ry, FUR)
        ell(d, bx - 2, byc - body_ry * 0.4, body_rx * 0.6, body_ry * 0.35, FUR_LT)
        ell(d, bx + 2, byc + body_ry * 0.45, body_rx * 0.75, body_ry * 0.45, CREAM)
    c.part(body)

    # ---------------- Front legs
    flx, fly = front_leg_offset
    if not sleeping and not play_bow:
        for ox in (6, 12):
            def fleg(d, ox=ox):
                x0, y0 = bx + ox + flx, byc + body_ry - 1 + fly
                ell(d, x0, y0, 3.6, 3.2, FUR)
                px(d, x0 - 1, y0 + 1, FUR_DK)
                px(d, x0 + 1, y0 + 1, FUR_DK)
            c.part(fleg)
    elif play_bow:
        # Paws stretched forward flat on ground
        def bow_front(d):
            ell(d, hx + 1, 52, 4.5, 2.6, FUR)
            ell(d, hx + 7, 52, 4.5, 2.6, FUR)
        c.part(bow_front)
    else:
        def sleep_front(d):
            ell(d, 39, 49, 3.6, 2.6, FUR)
        c.part(sleep_front)

    # ---------------- Floppy Ears (behind head)
    def ears(d):
        # Left floppy ear
        d.polygon([
            (hx - 11, hy - 6), (hx - 15, hy - 1), (hx - 14, hy + 7 + ear_flop),
            (hx - 8, hy + 6 + ear_flop), (hx - 7, hy - 3)
        ], fill=EAR)
        d.line([(hx - 13, hy + 1), (hx - 11, hy + 5 + ear_flop)], fill=EAR_DK)

        # Right floppy ear
        d.polygon([
            (hx + 8, hy - 5), (hx + 14, hy - 1), (hx + 15, hy + 7 + ear_flop),
            (hx + 9, hy + 7 + ear_flop), (hx + 6, hy - 2)
        ], fill=EAR)
        d.line([(hx + 12, hy + 1), (hx + 11, hy + 5 + ear_flop)], fill=EAR_DK)
    c.part(ears)

    # ---------------- Head & Muzzle
    def head(d):
        ell(d, hx, hy, 13.5, 11.5, FUR)
        # Forehead light patch
        ell(d, hx, hy - 4, 6.0, 3.5, FUR_LT)
        # Chubby white/cream puppy muzzle
        ell(d, hx, hy + 4.5, 7.5, 5.0, CREAM)
        ell(d, hx - 3.2, hy + 5.0, 4.0, 3.2, CREAM)
        ell(d, hx + 3.2, hy + 5.0, 4.0, 3.2, CREAM)
    c.part(head)

    # ---------------- Red collar with shiny gold tag
    if not sleeping:
        def collar(d):
            cx, cy = hx - 2, hy + 10
            d.line([(cx - 7, cy), (cx + 7, cy)], fill=COLLAR, width=2)
            # Golden medal tag dangling in center
            ell(d, cx, cy + 3, 2.0, 2.0, TAG_GOLD)
            px(d, cx - 1, cy + 2, WHITE)
        c.part(collar)

    # ---------------- Nose & Mouth
    def muzzle_details(d):
        # Shiny black button nose
        d.polygon([
            (hx - 2.5, hy + 2.0), (hx + 2.5, hy + 2.0),
            (hx, hy + 4.2)
        ], fill=NOSE)
        px(d, hx - 1, hy + 2.2, WHITE)

        # Mouth line
        d.line([(hx, hy + 4.2), (hx, hy + 6.0)], fill=OUT)
        d.line([(hx - 3, hy + 6.5), (hx, hy + 6.0)], fill=OUT)
        d.line([(hx, hy + 6.0), (hx + 3, hy + 6.5)], fill=OUT)

        # Cute pink tongue panting!
        if tongue_out:
            d.polygon([(hx - 1.5, hy + 6.5), (hx + 1.5, hy + 6.5), (hx + 1.2, hy + 10.0), (hx - 1.2, hy + 10.0)], fill=TONGUE)
            ell(d, hx, hy + 10.0, 1.4, 1.2, TONGUE)
            d.line([(hx, hy + 7.0), (hx, hy + 9.5)], fill=(225, 95, 120, 255))
    c.overlay(muzzle_details)

    # ---------------- Eyes
    eye_xs = (hx - 4.8, hx + 4.8)
    ey = hy - 1.0

    def eyes(d):
        for ex in eye_xs:
            if sleeping:
                for dx, dy in ((-2, 0), (-1, 1), (0, 1), (1, 1), (2, 0)):
                    px(d, ex + dx, ey + 1 + dy, EYE)
            elif happy_eyes:
                # Joyful kawaii curved eye arcs ^ ^
                for dx, dy in ((-2, 2), (-1, 1), (0, 0), (1, 1), (2, 2)):
                    px(d, ex + dx, ey + dy, EYE)
            elif blink:
                for dx in (-2, -1, 0, 1, 2):
                    px(d, ex + dx, ey + 1, EYE)
            else:
                # Big glistening puppy dog boba eyes!
                ell(d, ex, ey + 1, 2.5, 3.2, EYE)
                px(d, ex - 1, ey - 1, WHITE)
                px(d, ex, ey - 1, WHITE)
                px(d, ex - 1, ey, WHITE)
                px(d, ex + 1, ey + 2, WHITE)
    c.overlay(eyes)

    # ---------------- Rosy cheeks
    def blush(d):
        ell(d, hx - 8.5, hy + 4.0, 2.5, 1.6, BLUSH)
        ell(d, hx + 8.5, hy + 4.0, 2.5, 1.6, BLUSH)
    c.overlay(blush)

    # ---------------- Extras: Zzz's, hearts, sparkles
    if sleeping:
        draw_zzz(c, zzz_stage)
    if heart_pos:
        draw_heart(c, heart_pos[0], heart_pos[1])
    if sparkles:
        def spark(d):
            for sx, sy in ((hx - 12, hy - 8), (hx + 14, hy - 6), (hx - 14, hy + 8)):
                px(d, sx, sy, (255, 235, 140, 255))
                for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    px(d, sx + ox, sy + oy, (255, 235, 140, 255))
        c.overlay(spark)

    return c.img.resize((128, 128), Image.Resampling.NEAREST)


def build_puppy_frames() -> dict:
    """Build full 4-frame animation sequences for all puppy states."""
    p = create_puppy_sprite
    return {
        # IDLE: Sitting alert, happy tail wag, slow blink
        "idle": [
            p(bob_y=0.0, tail_angle=1, ear_flop=0),
            p(bob_y=-0.5, tail_angle=3, ear_flop=1, tongue_out=True),
            p(bob_y=0.0, tail_angle=0, ear_flop=0, tongue_out=True),
            p(bob_y=-0.5, tail_angle=-2, ear_flop=0, blink=True),
        ],
        # WALK: Energetic 4-leg puppy trot with tail wagging high
        "walk": [
            p(bob_y=-1.0, tail_angle=2, ear_flop=2, front_leg_offset=(2, -2), back_leg_offset=(-2, 0)),
            p(bob_y=0.4, tail_angle=0, ear_flop=0, front_leg_offset=(0, 0), back_leg_offset=(0, -2)),
            p(bob_y=-1.0, tail_angle=-2, ear_flop=2, front_leg_offset=(-2, -2), back_leg_offset=(2, 0)),
            p(bob_y=0.4, tail_angle=0, ear_flop=0, front_leg_offset=(0, 0), back_leg_offset=(0, -1)),
        ],
        # PLAY: Puppy play bow (front lowered, rump up, tail wagging, tongue out!)
        "play": [
            p(play_bow=True, tail_angle=3, happy_eyes=True, tongue_out=True, ear_flop=1),
            p(play_bow=True, tail_angle=-3, happy_eyes=True, tongue_out=True, ear_flop=0),
            p(play_bow=True, tail_angle=4, happy_eyes=True, tongue_out=True, ear_flop=1, sparkles=True),
            p(play_bow=True, tail_angle=-2, happy_eyes=True, tongue_out=True, ear_flop=0),
        ],
        # SLEEP: Curled up in a golden donut ball with soft Zzz's
        "sleep": [
            p(sleeping=True, zzz_stage=1),
            p(sleeping=True, zzz_stage=2),
            p(sleeping=True, zzz_stage=3),
            p(sleeping=True, zzz_stage=2),
        ],
        # EAT: Head bowed, happily licking kibbles & drinking water
        "eat": [
            p(bob_y=0.2, head_offset=(3, 5), ear_flop=1, happy_eyes=True),
            p(bob_y=0.8, squish_y=1, head_offset=(4, 7), ear_flop=2, tongue_out=True, happy_eyes=True),
            p(bob_y=-0.2, head_offset=(2, 4), ear_flop=0, happy_eyes=True, heart_pos=(54, 10)),
            p(bob_y=0.6, head_offset=(4, 6), ear_flop=2, tongue_out=True, happy_eyes=True, sparkles=True),
        ],
        # SNUGGLE: Paws up, hearts flying, ecstatic tail wagging & tongue pant!
        "snuggle": [
            p(bob_y=-1.5, tail_angle=3, happy_eyes=True, tongue_out=True, ear_flop=1, heart_pos=(52, 12)),
            p(bob_y=-2.5, tail_angle=-3, happy_eyes=True, tongue_out=True, ear_flop=2, heart_pos=(55, 6), sparkles=True),
            p(bob_y=-1.5, tail_angle=4, happy_eyes=True, tongue_out=True, ear_flop=1, heart_pos=(50, 10)),
            p(bob_y=-0.5, tail_angle=-2, happy_eyes=True, tongue_out=True, ear_flop=0, heart_pos=(54, 4), sparkles=True),
        ],
    }


def ensure_puppy_sprites(target_dir: str, force: bool = False) -> None:
    """Export all puppy animation frames into target directory."""
    os.makedirs(target_dir, exist_ok=True)
    frames = build_puppy_frames()
    for state, img_list in frames.items():
        for idx, img in enumerate(img_list, start=1):
            fn = os.path.join(target_dir, f"{state}_{idx}.png")
            if force or not os.path.exists(fn):
                img.save(fn)
