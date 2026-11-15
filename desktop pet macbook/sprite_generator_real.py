"""
Realistic ("heraldic") Griffin sprite generator.

A proud, majestic griffin in side profile:
  * Eagle head: white-cream plumage, sharp hooked golden beak, fierce amber eye with brow
  * Feathered neck ruff flowing into a tawny lion chest
  * Lion body, haunches and hind paws, long tail with a dark tuft
  * Eagle front legs: feathered thigh, golden scaled shin, three-toed talons with black claws
  * Big layered eagle wings: chestnut/tawny flight feathers with dark tips

Same 6 states / file names as the cute griffin, drawn on a 64x64 grid and scaled 2x.
Sprites face RIGHT; main.py mirrors them for the left direction.
"""
import os
import math
from PIL import Image, ImageDraw

from sprite_generator import (
    Canvas, ell, tline, px, W, H, SHADOW, draw_zzz, star_poly, create_toy_sprite,
    create_bed_sprite, create_food_bowl_sprite,
)

OUT = (38, 24, 16, 255)

FEATHER = (250, 245, 234, 255)
FEATHER_SH = (216, 205, 188, 255)
FEATHER_DK = (178, 164, 146, 255)

BEAK = (248, 192, 50, 255)
BEAK_LT = (255, 228, 120, 255)
BEAK_SH = (204, 142, 22, 255)
BEAK_TIP = (120, 74, 10, 255)
MOUTH = (120, 36, 36, 255)

EYE_IRIS = (255, 176, 34, 255)
EYE_PUPIL = (18, 10, 6, 255)

FUR = (212, 148, 68, 255)
FUR_LT = (238, 190, 108, 255)
FUR_SH = (166, 104, 44, 255)
FUR_BELLY = (240, 214, 160, 255)

W_COVERT = (204, 138, 62, 255)
W_COVERT_LT = (232, 178, 98, 255)
W_PRIM = (146, 88, 46, 255)
W_SEC = (186, 120, 58, 255)
W_TIP = (84, 52, 30, 255)
W_FAR = (120, 76, 44, 255)
W_FAR_SEC = (150, 98, 52, 255)

GOLD = (244, 190, 52, 255)
GOLD_SH = (194, 138, 24, 255)
CLAW = (46, 34, 28, 255)

TUFT = (150, 74, 38, 255)
TUFT_LT = (190, 108, 56, 255)

STAR_GOLD = (255, 222, 60, 255)
STAR_LT = (255, 250, 190, 255)
STAR_OUT = (175, 105, 18, 255)
STAR_SH = (210, 140, 20, 255)
STAR_CRUMB = (245, 180, 35, 255)

MEAT = (190, 60, 56, 255)
MEAT_LT = (232, 112, 100, 255)
BONE = (246, 238, 220, 255)

GROUND_Y = 55

WING_POSES = {
    "FOLDED": ([158, 166, 174, 182, 190], [13, 17, 19, 18, 15]),
    "UP": ([-95, -110, -125, -140, -155], [20, 25, 27, 25, 20]),
    "MID": ([-120, -135, -150, -165, 180], [20, 25, 27, 25, 20]),
    "GLIDE": ([-150, -165, 180, 165, 150], [20, 25, 27, 25, 20]),
    "DOWN": ([100, 115, 130, 145, 160], [18, 23, 25, 23, 18]),
}


def feather(d, base, ang, length, w0, w1, fill, tip):
    r = math.radians(ang)
    ux, uy = math.cos(r), math.sin(r)
    nx, ny = -uy, ux
    bx, by = base
    tx, ty = bx + ux * length, by + uy * length

    def poly(t0, t1):
        ax, ay = bx + ux * length * t0, by + uy * length * t0
        cx, cy = bx + ux * length * t1, by + uy * length * t1
        wa = w0 + (w1 - w0) * t0
        wc = w0 + (w1 - w0) * t1
        return [
            (ax + nx * wa / 2, ay + ny * wa / 2),
            (cx + nx * wc / 2, cy + ny * wc / 2),
            (cx + ux * 1.6, cy + uy * 1.6),
            (cx - nx * wc / 2, cy - ny * wc / 2),
            (ax - nx * wa / 2, ay - ny * wa / 2),
        ]

    d.polygon(poly(0, 1), fill=fill)
    d.polygon(poly(0.7, 1), fill=tip)


def draw_wing(d, anchor, pose, far=False):
    ax, ay = anchor
    angles, lengths = WING_POSES[pose]
    prim = W_FAR if far else W_PRIM
    sec = W_FAR_SEC if far else W_SEC
    tip = (60, 38, 24, 255) if far else W_TIP
    for i, (a, L) in enumerate(zip(angles, lengths)):
        feather(d, (ax, ay), a, L, 6, 4, prim if i % 2 == 0 else sec, tip)
    # coverts at the shoulder
    ell(d, ax, ay + 1, 8, 5.2, W_FAR_SEC if far else W_COVERT)
    ell(d, ax - 1, ay - 1, 5.5, 3, W_FAR_SEC if far else W_COVERT_LT)
    if not far:
        for k in range(4):
            px(d, ax - 6 + k * 3, ay + 4, W_PRIM)
            px(d, ax - 5 + k * 3, ay + 5, W_PRIM)


def draw_front_leg(d, top, foot, shade=False):
    gold = GOLD_SH if shade else GOLD
    thigh = FEATHER_DK if shade else FEATHER_SH
    tx, ty = top
    fx, fy = foot
    ell(d, tx, ty + 1, 4.2, 5, thigh)
    tline(d, (tx + 0.5, ty + 4), (fx, fy - 2), 3, gold)
    # scales
    px(d, (tx + fx) / 2, (ty + fy) / 2, GOLD_SH if not shade else (150, 100, 14, 255))
    # talons: three toes forward, one back
    for dx, dy in ((5, -0.5), (4.5, 1.5), (2.5, 2.8)):
        tline(d, (fx, fy - 1), (fx + dx, fy - 1 + dy), 2, gold)
        px(d, fx + dx + 1, fy - 1 + dy + 0.6, CLAW)
        px(d, fx + dx + 1.4, fy - 1 + dy + 1.4, CLAW)
    tline(d, (fx, fy - 1), (fx - 2, fy), 2, gold)


def draw_hind_leg(d, top, foot, shade=False):
    fur = FUR_SH if shade else FUR
    tx, ty = top
    fx, fy = foot
    ell(d, tx, ty, 6.2, 7, fur)
    if not shade:
        ell(d, tx - 1.5, ty - 2.5, 3.5, 3.5, FUR_LT)
    tline(d, (tx + 1, ty + 4), (fx, fy - 3), 4, fur)
    ell(d, fx + 1.5, fy - 1.2, 4.6, 2.6, fur)
    # toe lines
    for k in (0, 2):
        px(d, fx + 3 + k, fy - 0.5, FUR_SH if not shade else (120, 72, 28, 255))


def create_real_griffin_sprite(
    bob_y=0.0,
    wing_pose="FOLDED",
    tail_angle=0,
    head_dx=0,
    head_dy=0,
    eyes="open",            # "open", "blink", "closed"
    beak_open=False,
    legs=None,              # dict of (dx, lift) for fn, ff, hn, hf
    grounded=True,
    lying=False,
    head_tilt=0,
    zzz_stage=0,
    star_stage=0,
    meat_stage=0,
    sparkles=False,
    wind=False,
    tilt=0.0,
    shift_x=0,
) -> Image.Image:
    c = Canvas()
    by = round(bob_y)
    legs = legs or {}
    fn = legs.get("fn", (0, 0))
    ff = legs.get("ff", (0, 0))
    hn = legs.get("hn", (0, 0))
    hf = legs.get("hf", (0, 0))

    # ground shadow
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    spread = 0 if grounded else 4
    ImageDraw.Draw(sh).ellipse([8 + spread, 56, 54 - spread, 61], fill=SHADOW)
    c.img.alpha_composite(sh)

    # ---------------- geometry
    if lying:
        body_c, body_rx, body_ry = (26, 46), 16, 7
        shoulder = (33, 42)
        head_c = (47, 43)
        chest_top = (38, 43)
        foot_y = 53
    else:
        body_c, body_rx, body_ry = (27, 37 + by), 15, 8.5
        shoulder = (31, 31 + by)
        head_c = (47 + head_dx, 17 + head_dy + by)
        chest_top = (38, 32 + by)
        foot_y = (GROUND_Y - 1) if grounded else (GROUND_Y - 6 + by)
    hx, hy = head_c
    bx, byc = body_c

    # ---------------- spread wings (behind body)
    spread_pose = wing_pose != "FOLDED" and not lying
    if spread_pose:
        c.part(lambda d: draw_wing(d, (shoulder[0] + 4, shoulder[1] - 1), wing_pose, far=True))
        c.part(lambda d: draw_wing(d, shoulder, wing_pose, far=False))

    # ---------------- tail
    ta = tail_angle
    if lying:
        pts = [(12, 47), (7, 49), (6, 54), (16, 55)]
        tip = (21, 55)
    else:
        pts = [(bx - 13, byc - 2), (bx - 19, byc - 1), (bx - 22, byc - 7 + ta), (bx - 21, byc - 13 + ta * 2)]
        tip = (bx - 20, byc - 17 + ta * 2)

    def tail(d):
        for a, b in zip(pts[:-1], pts[1:]):
            tline(d, a, b, 3, FUR)
        tline(d, pts[-1], tip, 3, FUR)
        ell(d, tip[0], tip[1], 3, 4.2, TUFT)
        ell(d, tip[0] - 1, tip[1] - 1, 1.4, 2.4, TUFT_LT)

    c.part(tail)

    # ---------------- far legs
    if not lying:
        fy = foot_y
        c.part(lambda d: draw_hind_leg(d, (bx - 9 + hf[0] * 0.3, byc + 5), (bx - 10 + hf[0], fy - hf[1]), shade=True))
        c.part(lambda d: draw_front_leg(d, (bx + 7, byc + 4), (bx + 8 + ff[0], fy - ff[1] - (0 if grounded else 1)), shade=True))

    # ---------------- body
    def body(d):
        ell(d, bx, byc, body_rx, body_ry, FUR)
        ell(d, bx - 2, byc - body_ry * 0.45, body_rx * 0.7, body_ry * 0.4, FUR_LT)
        ell(d, bx + 1, byc + body_ry * 0.55, body_rx * 0.8, body_ry * 0.4, FUR_BELLY)
        # chest
        ell(d, chest_top[0] - 1, chest_top[1] + 4, 8, 7.5, FUR)
        ell(d, chest_top[0] - 1, chest_top[1] + 8, 6, 3.5, FUR_BELLY)

    c.part(body)

    # ---------------- near legs
    if lying:
        def paws(d):
            ell(d, 17, 49, 7, 4.5, FUR)                      # tucked haunch
            ell(d, 49, 52, 6, 2.8, GOLD)                     # front paws forward
            ell(d, 42, 52, 6, 2.8, GOLD_SH)
            for k in (0, 3):
                px(d, 53 + k * 0.5, 53, CLAW)
                px(d, 54, 51 + k * 0.5, CLAW)
        c.part(paws)
    else:
        fy = foot_y
        c.part(lambda d: draw_hind_leg(d, (bx - 8 + hn[0] * 0.3, byc + 5), (bx - 8 + hn[0], fy - hn[1])))
        c.part(lambda d: draw_front_leg(d, (bx + 12, byc + 4), (bx + 13 + fn[0], fy - fn[1] - (0 if grounded else 1))))

    # ---------------- folded wing lies over the flank
    if wing_pose == "FOLDED" or lying:
        anchor = (shoulder[0] - 1, shoulder[1] + (1 if lying else 0))
        c.part(lambda d: draw_wing(d, anchor, "FOLDED", far=False))

    # ---------------- neck (cream plumage) + ruff
    nx0, ny0 = chest_top[0], chest_top[1] + 1
    nx1, ny1 = hx - 2, hy + 4

    def neck(d):
        dx, dy = nx1 - nx0, ny1 - ny0
        ln = math.hypot(dx, dy) or 1
        ox, oy = -dy / ln, dx / ln
        wb, wt = 6.5, 4.2
        d.polygon([
            (nx0 + ox * wb, ny0 + oy * wb), (nx1 + ox * wt, ny1 + oy * wt),
            (nx1 - ox * wt, ny1 - oy * wt), (nx0 - ox * wb, ny0 - oy * wb),
        ], fill=FEATHER)
        # feather scallops along the neck
        for t in (0.15, 0.4, 0.65):
            cx, cy = nx0 + dx * t, ny0 + dy * t
            ell(d, cx + ox * 4, cy + oy * 4, 2.4, 2.4, FEATHER_SH)
            ell(d, cx - ox * 4, cy - oy * 4, 2.2, 2.2, FEATHER)
        # ruff at the base of the neck
        for k, (rx_, ry_) in enumerate(((33, 36), (36, 38), (39, 38), (42, 36))):
            ell(d, rx_, ry_ + (by if not lying else 6), 3.4, 3.4, FEATHER if k % 2 else FEATHER_SH)

    c.part(neck)

    # ---------------- head
    head_c_layer = Canvas()

    def crest(d):
        d.polygon([(hx - 3, hy - 4), (hx - 10, hy - 8), (hx - 6, hy - 1)], fill=FEATHER_SH)
        d.polygon([(hx - 4, hy), (hx - 11, hy - 2), (hx - 6, hy + 3)], fill=FEATHER_SH)

    head_c_layer.part(crest)

    def head(d):
        ell(d, hx, hy, 6.8, 5.8, FEATHER)
        ell(d, hx - 1, hy - 3, 4, 1.8, (255, 255, 255, 255))
        ell(d, hx - 2, hy + 4, 4.2, 1.6, FEATHER_SH)

    head_c_layer.part(head)

    # ---------------- beak (sharp, hooked)
    def lower_beak(d):
        o = 3 if beak_open else 0
        d.polygon([(hx + 4, hy + 2 + o), (hx + 10, hy + 3 + o), (hx + 8, hy + 5 + o), (hx + 4, hy + 5 + o)], fill=BEAK_SH)

    def upper_beak(d):
        d.polygon([
            (hx + 4, hy - 3), (hx + 9, hy - 3), (hx + 12, hy), (hx + 13, hy + 4),
            (hx + 12, hy + 7), (hx + 10, hy + 4), (hx + 7, hy + 2), (hx + 4, hy + 2),
        ], fill=BEAK)
        d.line([(hx + 5, hy - 2), (hx + 9, hy - 2)], fill=BEAK_LT)
        px(d, hx + 12, hy + 6, BEAK_TIP)
        px(d, hx + 12, hy + 5, BEAK_TIP)
        px(d, hx + 7, hy - 1, BEAK_SH)           # nostril

    if beak_open:
        head_c_layer.overlay(lambda d: d.polygon([(hx + 4, hy + 2), (hx + 10, hy + 3), (hx + 10, hy + 6), (hx + 4, hy + 5)], fill=MOUTH))
    head_c_layer.part(lower_beak)
    head_c_layer.part(upper_beak)

    # ---------------- eye (fierce amber with brow)
    ex, ey = hx + 1, hy - 1

    def eye(d):
        if eyes == "open":
            d.rectangle([ex, ey, ex + 3, ey + 3], fill=EYE_IRIS)
            d.rectangle([ex + 2, ey + 1, ex + 2, ey + 2], fill=EYE_PUPIL)
            px(d, ex, ey, (255, 240, 180, 255))
        elif eyes == "blink":
            d.line([(ex, ey + 1), (ex + 3, ey + 1)], fill=OUT)
        else:
            d.line([(ex, ey + 1), (ex + 1, ey + 2), (ex + 2, ey + 2), (ex + 3, ey + 1)], fill=OUT)
        # stern brow slanting down toward the beak
        d.line([(ex - 1, ey - 2), (ex + 4, ey - 1)], fill=OUT)

    head_c_layer.overlay(eye)

    if head_tilt:
        h_img = head_c_layer.img.rotate(head_tilt, resample=Image.Resampling.NEAREST, center=(hx, hy))
        c.img.alpha_composite(h_img)
    else:
        c.img.alpha_composite(head_c_layer.img)

    if shift_x:
        shifted = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        shifted.paste(c.img, (shift_x, 0))
        c.img = shifted

    # ---------------- star cookie (eat) / extras
    effective_star = star_stage or meat_stage
    if effective_star:
        scx, scy = 54, 52
        r_params = {
            1: (7.5, 4.0),
            2: (6.0, 3.2),
            3: (4.4, 2.3),
            4: (3.0, 1.5),
        }.get(effective_star, (7.5, 4.0))
        r_out, r_in = r_params

        def cookie(d):
            pts = star_poly(scx, scy, r_out, r_in)
            d.polygon(pts, fill=STAR_GOLD)
            d.polygon(pts, outline=STAR_OUT)
            # Sugar glaze highlight on top point and center
            px(d, scx, scy - 1, (255, 255, 240, 255))
            px(d, scx - 1, scy, (255, 255, 240, 255))
            px(d, scx + 1, scy - 1, STAR_LT)

            # Golden crispy crumbs bursting when bitten
            if effective_star >= 2:
                px(d, scx + 6, scy - 3, STAR_CRUMB)
                px(d, scx + 8, scy + 2, (220, 145, 25, 255))
                px(d, scx + 5, scy + 5, (250, 210, 60, 255))
            if effective_star >= 3:
                px(d, scx - 5, scy + 4, STAR_CRUMB)
                px(d, scx + 2, scy + 6, (220, 145, 25, 255))
                px(d, scx + 7, scy - 5, (255, 255, 240, 255))
            if effective_star >= 4:
                px(d, scx - 4, scy - 2, STAR_CRUMB)
                px(d, scx + 4, scy + 1, (250, 210, 60, 255))

        c.part(cookie)
    if lying:
        draw_zzz(c, zzz_stage, dy=13)
    if sparkles:
        for (x, y) in ((6, 12), (58, 8), (10, 26)):
            def sp(d, x=x, y=y):
                px(d, x, y, (255, 244, 160, 255))
                for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    px(d, x + ox, y + oy, (255, 244, 160, 255))
            c.overlay(sp)
    if wind:
        def lines(d):
            for y, x0, x1 in ((30, 1, 9), (38, 0, 7), (46, 2, 8)):
                d.line([(x0, y + by), (x1, y + by)], fill=(255, 255, 255, 190))
        c.overlay(lines)

    img = c.img
    if tilt:
        img = img.rotate(tilt, resample=Image.Resampling.NEAREST, center=(32, 40))
    return img.resize((128, 128), Image.Resampling.NEAREST)


STATES = ("idle", "walk", "play", "sleep", "eat", "jump")


def build_frames() -> dict:
    g = create_real_griffin_sprite
    return {
        # IDLE: proud stance, slow breathing, tail swish, blink
        "idle": [
            g(bob_y=0, tail_angle=0),
            g(bob_y=-1, tail_angle=1, head_dy=-1),
            g(bob_y=0, tail_angle=2),
            g(bob_y=0, tail_angle=0, eyes="blink"),
        ],
        # WALK: striding on all four legs, wings folded
        "walk": [
            g(bob_y=0, tail_angle=1, legs={"fn": (4, 0), "ff": (-4, 0), "hn": (-4, 0), "hf": (4, 0)}),
            g(bob_y=-1, tail_angle=0, legs={"fn": (1, 3), "ff": (-1, 0), "hn": (-1, 0), "hf": (1, 3)}),
            g(bob_y=0, tail_angle=-1, legs={"fn": (-4, 0), "ff": (4, 0), "hn": (4, 0), "hf": (-4, 0)}),
            g(bob_y=-1, tail_angle=0, legs={"fn": (-1, 0), "ff": (1, 3), "hn": (1, 3), "hf": (-1, 0)}),
        ],
        # PLAY: wings flared, screech, batting a raised talon
        "play": [
            g(bob_y=-1, wing_pose="MID", beak_open=True, tail_angle=2, legs={"fn": (6, 7)}),
            g(bob_y=-2, wing_pose="UP", beak_open=True, tail_angle=1, legs={"fn": (7, 5)}),
            g(bob_y=-1, wing_pose="MID", tail_angle=-1, legs={"fn": (6, 7)}),
            g(bob_y=-2, wing_pose="GLIDE", beak_open=True, tail_angle=2, legs={"fn": (7, 5)}),
        ],
        # SLEEP: lying down, head resting on its talons
        "sleep": [
            g(lying=True, eyes="closed", zzz_stage=1, bob_y=0),
            g(lying=True, eyes="closed", zzz_stage=2, bob_y=0),
            g(lying=True, eyes="closed", zzz_stage=3, bob_y=0),
            g(lying=True, eyes="closed", zzz_stage=2, bob_y=0),
        ],
        # EAT: head bowed, eating golden star cookie
        "eat": [
            g(head_dx=4, head_dy=24, star_stage=1, shift_x=-5),
            g(head_dx=4, head_dy=21, star_stage=2, beak_open=True, shift_x=-5),
            g(head_dx=4, head_dy=24, star_stage=3, shift_x=-5),
            g(head_dx=4, head_dy=21, star_stage=4, eyes="blink", sparkles=True, shift_x=-5),
        ],
        # JUMP / FLY: continuous soaring & wing-flapping flight cycle with tucked talons
        "jump": [
            g(bob_y=-4, wing_pose="MID", grounded=False, tail_angle=1, legs={"fn": (-1, 2), "ff": (-1, 2), "hn": (2, 2), "hf": (2, 2)}),
            g(bob_y=-6, wing_pose="UP", grounded=False, tail_angle=2, wind=True, legs={"fn": (-2, 2), "ff": (-2, 2), "hn": (3, 2), "hf": (3, 2)}),
            g(bob_y=-7, wing_pose="GLIDE", grounded=False, tail_angle=1, wind=True, sparkles=True, legs={"fn": (-2, 2), "ff": (-2, 2), "hn": (3, 2), "hf": (3, 2)}),
            g(bob_y=-4, wing_pose="DOWN", grounded=False, legs={"fn": (0, 1), "ff": (0, 1), "hn": (2, 1), "hf": (2, 1)}),
        ],
        # EAT_BOWL: head bowed down, sharp beak dipping directly into the berries and kibbles
        "eat_bowl": [
            g(head_dx=2, head_dy=10, head_tilt=-28, meat_stage=0, beak_open=False, eyes="open", shift_x=0),
            g(head_dx=3, head_dy=13, head_tilt=-36, meat_stage=0, beak_open=True, eyes="open", shift_x=0),
            g(head_dx=2, head_dy=11, head_tilt=-30, meat_stage=0, beak_open=False, eyes="blink", shift_x=0),
            g(head_dx=4, head_dy=14, head_tilt=-38, meat_stage=0, beak_open=True, eyes="open", shift_x=0),
        ],
        # SLEEP_BED: cozy curled up pose inside the bed bolster
        "sleep_bed": [
            g(lying=True, eyes="closed", zzz_stage=1, bob_y=0),
            g(lying=True, eyes="closed", zzz_stage=2, bob_y=0),
            g(lying=True, eyes="closed", zzz_stage=3, bob_y=0),
            g(lying=True, eyes="closed", zzz_stage=2, bob_y=0),
        ],
    }


def ensure_real_sprites(sprites_dir: str, force: bool = False) -> None:
    os.makedirs(sprites_dir, exist_ok=True)
    expected = (
        ["toy.png", "bed.png", "food_bowl.png"]
        + [f"{s}_{i}.png" for s in STATES for i in range(1, 5)]
        + [f"{s}_{i}.png" for s in ("eat_bowl", "sleep_bed") for i in range(1, 5)]
    )
    if not force and all(os.path.isfile(os.path.join(sprites_dir, f)) for f in expected):
        return
    for state, frames in build_frames().items():
        for i, frame in enumerate(frames, start=1):
            frame.save(os.path.join(sprites_dir, f"{state}_{i}.png"))
    create_toy_sprite().save(os.path.join(sprites_dir, "toy.png"))
    create_bed_sprite().save(os.path.join(sprites_dir, "bed.png"))
    create_food_bowl_sprite().save(os.path.join(sprites_dir, "food_bowl.png"))


if __name__ == "__main__":
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites", "real")
    ensure_real_sprites(here, force=True)
    print("Real griffin sprites regenerated in", here)
