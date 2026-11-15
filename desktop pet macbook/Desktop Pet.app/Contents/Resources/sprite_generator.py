"""
Chibi Griffin sprite generator for the Cozy Desktop Pet (v3, "Pip" redesign).

Design goals: maximum cuteness.
  * Big round cream-white eagle head, tiny rounded beak
  * Large glossy boba eyes with sparkles, rosy blush
  * Pointy kitten-style ear tufts with pink insides
  * Chubby honey-colored lion body with cream belly
  * Fluffy fan wings (tawny coverts, cream feathers)
  * Curly tail with a strawberry-pink pom-pom
  * Little golden front feet, back paws with pink toe beans

Every sprite is drawn on a 64x64 grid, then scaled 2x (nearest neighbour) to
128x128 so it stays crisp pixel art.  Sprites face RIGHT; main.py mirrors them.

Public API (unchanged from v3): create_griffin_sprite(...), ensure_sprites_exist()
"""
import os
import math
import numpy as np
from PIL import Image, ImageDraw

W = H = 64

# ------------------------------------------------------------------ palette
OUT = (66, 38, 28, 255)
CREAM = (255, 248, 234, 255)
CREAM_SH = (244, 225, 200, 255)
CREAM_HI = (255, 255, 255, 255)
HONEY = (248, 182, 90, 255)
HONEY_LT = (255, 210, 130, 255)
HONEY_SH = (226, 148, 62, 255)
TAWNY = (236, 156, 64, 255)
TAWNY_SH = (206, 120, 44, 255)
FOOT = (255, 205, 80, 255)
FOOT_SH = (232, 160, 40, 255)
BEAK = (255, 200, 70, 255)
BEAK_SH = (232, 150, 38, 255)
PINK = (255, 158, 175, 255)
POM = (255, 170, 160, 255)
POM_LT = (255, 205, 195, 255)
EYE = (50, 30, 40, 255)
EYE_GLOW = (110, 70, 95, 255)
WHITE = (255, 255, 255, 255)
BLUSH = (255, 125, 145, 190)
SHADOW = (40, 30, 40, 50)

CLOUD = (244, 248, 255, 255)
CLOUD_SH = (205, 219, 242, 255)
CLOUD_OUT = (140, 162, 205, 255)
ZZZ = (120, 170, 235, 255)
ZZZ_OUT = (52, 86, 150, 255)

STAR = (255, 226, 70, 255)
STAR_LT = (255, 248, 170, 255)
STAR_OUT = (176, 112, 20, 255)
HEART = (255, 84, 108, 255)
HEART_OUT = (150, 28, 52, 255)
SPARK = (255, 244, 160, 255)


# ------------------------------------------------------------------ helpers
class Canvas:
    """Layered painter: every part gets a 1px outline around its silhouette."""

    def __init__(self):
        self.img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def part(self, painter, outline=OUT):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        painter(ImageDraw.Draw(layer))
        a = np.array(layer)[:, :, 3] > 0
        if outline is not None:
            o = a.copy()
            o[1:] |= a[:-1]
            o[:-1] |= a[1:]
            o[:, 1:] |= a[:, :-1]
            o[:, :-1] |= a[:, 1:]
            arr = np.zeros((H, W, 4), dtype=np.uint8)
            arr[o] = outline
            self.img.alpha_composite(Image.fromarray(arr, "RGBA"))
        self.img.alpha_composite(layer)

    def overlay(self, painter):
        """Paint with no outline (blush, shine, small details)."""
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        painter(ImageDraw.Draw(layer))
        self.img.alpha_composite(layer)


def ell(d, cx, cy, rx, ry, fill):
    d.ellipse([round(cx - rx), round(cy - ry), round(cx + rx), round(cy + ry)], fill=fill)


def tline(d, p0, p1, w, fill):
    """Thick line with round caps."""
    d.line([(round(p0[0]), round(p0[1])), (round(p1[0]), round(p1[1]))], fill=fill, width=int(w))
    r = w / 2.0
    for p in (p0, p1):
        ell(d, p[0], p[1], r - 0.3, r - 0.3, fill)


def px(d, x, y, fill):
    d.point((round(x), round(y)), fill=fill)


def star_poly(cx, cy, r_out, r_in):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    return pts


# wing fan angle sets (degrees, 0 = right, -90 = up, 90 = down)
WING_POSES = {
    "UP": [-172, -150, -128, -106],
    "MID": [-190, -170, -150, -130],
    "GLIDE": [165, 182, -165, -148],
    "DOWN": [100, 124, 148, 172],
    "TUCKED": [150, 165, 180, 195],
}


def draw_wing(d, anchor, pose, scale=1.0, far=False):
    ax, ay = anchor
    angles = WING_POSES[pose]
    lengths = [17, 22, 22, 18]
    base = (236, 214, 188, 255) if far else CREAM
    alt = (222, 196, 168, 255) if far else CREAM_SH
    tip = TAWNY_SH if far else TAWNY
    ends = []
    for i, (a, L) in enumerate(zip(angles, lengths)):
        r = math.radians(a)
        ex = ax + math.cos(r) * L * scale
        ey = ay + math.sin(r) * L * scale
        tline(d, (ax, ay), (ex, ey), 6, base if i % 2 == 0 else alt)
        ends.append((ex, ey))
    for ex, ey in ends:
        ell(d, ex, ey, 2.3, 2.3, tip)
    cov = TAWNY_SH if far else TAWNY
    ell(d, ax, ay, 6.5 * scale, 5.6 * scale, cov)
    ell(d, ax - 1, ay - 1.5, 3.6 * scale, 2.4 * scale, HONEY_LT if not far else TAWNY)


def sparkle(c, x, y, big=False):
    def p(d):
        px(d, x, y, SPARK)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            px(d, x + dx, y + dy, SPARK)
        if big:
            for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
                px(d, x + dx, y + dy, WHITE)
    c.overlay(p)


def draw_zzz(c, stage, dy=0):
    spots = [(48, 18 + dy, 3), (53, 11 + dy, 4), (47, 5 + dy, 5)]
    for i in range(min(stage, 3)):
        x, y, s = spots[i]

        def z(d, x=x, y=y, s=s):
            for ox in (-1, 0, 1):
                for oy in (-1, 0, 1):
                    d.line([(x + ox, y + oy), (x + s + ox, y + oy)], fill=ZZZ_OUT)
                    d.line([(x + s + ox, y + oy), (x + ox, y + s + oy)], fill=ZZZ_OUT)
                    d.line([(x + ox, y + s + oy), (x + s + ox, y + s + oy)], fill=ZZZ_OUT)
            d.line([(x, y), (x + s, y)], fill=ZZZ)
            d.line([(x + s, y), (x, y + s)], fill=ZZZ)
            d.line([(x, y + s), (x + s, y + s)], fill=ZZZ)

        c.overlay(z)


def draw_heart(c, x, y):
    pts = [(1, 0), (2, 0), (4, 0), (5, 0), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1),
           (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3),
           (2, 4), (3, 4), (4, 4), (3, 5)]

    def p(d):
        s = set(pts)
        for (hx, hy) in pts:
            for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (hx + ox, hy + oy) not in s:
                    px(d, x + hx + ox, y + hy + oy, HEART_OUT)
        for (hx, hy) in pts:
            px(d, x + hx, y + hy, HEART)
        px(d, x + 1, y + 1, WHITE)

    c.overlay(p)


# ------------------------------------------------------------------ main sprite
def create_griffin_sprite(
    bob_y: float = 0.0,
    squish_y: float = 0.0,
    wing_pose: str = "MID",
    tail_angle: int = 0,
    front_paw_offset: tuple = (0, 0),
    back_paw_offset: tuple = (0, 0),
    happy_eyes: bool = False,
    blink: bool = False,
    sleeping: bool = False,
    star_stage: int = 0,
    heart_pos: tuple = None,
    sparkles: bool = False,
    zzz_stage: int = 0,
    tilt: float = 0.0,
    speed_lines: bool = False,
    no_cloud: bool = False,
    head_offset: tuple = (0, 0),
) -> Image.Image:
    c = Canvas()
    by = round(bob_y * 1.6)          # vertical bob in pixels
    sq = round(squish_y)             # body squash

    # ---------------- soft ground shadow (stays on the ground while hovering)
    if not sleeping:
        shrink = max(0, -by) // 2
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([17 + shrink, 57, 47 - shrink, 62], fill=SHADOW)
        c.img.alpha_composite(sh)

    # ---------------- cloud pillow (sleep)
    if sleeping and not no_cloud:
        puffs = [(13, 54, 8), (23, 55, 9), (33, 56, 9), (43, 55, 9), (51, 53, 7),
                 (18, 51, 7), (29, 50, 8), (40, 51, 8), (48, 50, 6)]

        def cloud(d):
            for cx, cy, r in puffs:
                ell(d, cx, cy, r, r * 0.8, CLOUD)

        c.part(cloud, outline=CLOUD_OUT)

        def cloud_sh(d):
            for cx, cy, r in puffs[:5]:
                ell(d, cx, cy + 3, r * 0.8, r * 0.38, CLOUD_SH)

        c.overlay(cloud_sh)

    # ---------------- geometry
    if sleeping:
        head_c = (36, 36)
        body_c = (28, 47)
        body_rx, body_ry = 17, 9
        by = 0
    else:
        head_c = (37 + head_offset[0], 24 + by + sq + head_offset[1])
        body_c = (28, 43 + by + sq // 2)
        body_rx, body_ry = 13, 10 - sq // 2
    hx, hy = head_c
    bx, byc = body_c

    # ---------------- tail (behind everything)
    ta = tail_angle
    if sleeping:
        tail_pts = [(12, 49), (8, 53), (14, 56), (28, 58)]
        tip = (34, 57)
    else:
        tail_pts = [(bx - 12, byc + 3), (bx - 18, byc + 3), (bx - 21, byc - 1 + ta), (bx - 22, byc - 5 + ta)]
        tip = (bx - 21, byc - 9 + ta)

    def tail(d):
        for a, b in zip(tail_pts[:-1], tail_pts[1:]):
            tline(d, a, b, 4, HONEY)
        tline(d, tail_pts[-1], tip, 4, HONEY)
        ell(d, tip[0], tip[1], 4.6, 4.6, POM)
        ell(d, tip[0] - 1, tip[1] - 1, 2.2, 2.2, POM_LT)

    c.part(tail)

    # ---------------- far wing (behind body)
    if not sleeping:
        anchor = (bx - 3, byc - 7)
        c.part(lambda d: draw_wing(d, anchor, wing_pose, 1.0, far=True))

    # ---------------- back paws
    bpx, bpy = back_paw_offset
    if not sleeping:
        for ox in (-9, -1):
            def bpaw(d, ox=ox):
                ell(d, bx + ox + bpx, byc + body_ry - 1 + bpy, 4.6, 3.4, HONEY)
                ell(d, bx + ox + bpx, byc + body_ry + bpy, 2.0, 1.4, PINK)

            c.part(bpaw)

    # ---------------- body
    def body(d):
        ell(d, bx, byc, body_rx, body_ry, HONEY)
        ell(d, bx - 3, byc - body_ry * 0.45, body_rx * 0.55, body_ry * 0.35, HONEY_LT)
        ell(d, bx + 2, byc + body_ry * 0.45, body_rx * 0.8, body_ry * 0.5, CREAM)
        for sx in (-8, -4):
            px(d, bx + sx, byc - body_ry + 2, HONEY_SH)
            px(d, bx + sx, byc - body_ry + 3, HONEY_SH)

    c.part(body)

    # ---------------- front feet (golden bird feet)
    fpx, fpy = front_paw_offset
    if not sleeping:
        for ox in (6, 12):
            def fpaw(d, ox=ox):
                x0, y0 = bx + ox + fpx, byc + body_ry - 1 + fpy
                ell(d, x0, y0, 3.6, 3.2, FOOT)
                px(d, x0 - 1, y0 + 1, FOOT_SH)
                px(d, x0 + 1, y0 + 1, FOOT_SH)

            c.part(fpaw)
    else:
        def sp(d):
            ell(d, 41, 50, 3.4, 2.8, FOOT)
            ell(d, 33, 51, 3.4, 2.8, FOOT)

        c.part(sp)

    # ---------------- near wing (tucked over body when sleeping)
    if sleeping:
        def nw(d):
            ell(d, 25, 44, 9, 6, TAWNY)
            ell(d, 23, 42, 5, 3, HONEY_LT)
            for i, off in enumerate((-6, -2, 2, 6)):
                ell(d, 25 + off, 49, 2.8, 2.2, CREAM if i % 2 == 0 else CREAM_SH)

        c.part(nw)

    # ---------------- ears (behind head)
    def ears(d):
        d.polygon([(hx - 12, hy - 5), (hx - 13, hy - 17), (hx - 3, hy - 11)], fill=HONEY)
        d.polygon([(hx + 3, hy - 11), (hx + 9, hy - 19), (hx + 13, hy - 8)], fill=HONEY)
        px(d, hx - 11, hy - 11, PINK)
        px(d, hx - 11, hy - 9, PINK)
        px(d, hx + 8, hy - 14, PINK)
        px(d, hx + 9, hy - 12, PINK)

    c.part(ears)

    # ---------------- head with fluffy cheek ruff
    def head(d):
        ell(d, hx, hy, 15, 13, CREAM)
        for ox, oy, r in ((-11, 8, 4.5), (-5, 11, 4.5), (3, 12, 4.5), (10, 9, 4.5)):
            ell(d, hx + ox, hy + oy, r, r, CREAM)
        ell(d, hx - 8, hy + 9, 4, 2.2, CREAM_SH)
        ell(d, hx, hy + 12, 5, 2, CREAM_SH)
        ell(d, hx - 4, hy - 9, 7, 2.4, CREAM_HI)
        d.polygon([(hx - 3, hy - 11), (hx, hy - 18), (hx + 3, hy - 11)], fill=CREAM)
        px(d, hx, hy - 16, HONEY_LT)
        px(d, hx, hy - 15, HONEY_LT)

    c.part(head)

    # ---------------- beak (petite diamond kawaii chick beak)
    def beak(d):
        pts = [(hx, hy + 2.0), (hx + 2.2, hy + 4.0), (hx, hy + 6.0), (hx - 2.2, hy + 4.0)]
        d.polygon(pts, fill=BEAK)
        d.line([(hx - 1.2, hy + 5.0), (hx + 1.2, hy + 5.0)], fill=BEAK_SH)
        px(d, hx, hy + 3.0, WHITE)

    c.part(beak)

    # ---------------- eyes (harmonious centered anime boba eyes)
    eye_xs = (hx - 5.0, hx + 5.0)
    ey = hy - 1

    def eyes(d):
        for ex in eye_xs:
            if sleeping:
                for dx, dy in ((-2, 0), (-1, 1), (0, 1), (1, 1), (2, 0)):
                    px(d, ex + dx, ey + 1 + dy, EYE)
            elif happy_eyes:
                for dx, dy in ((-2, 2), (-1, 1), (0, 0), (1, 1), (2, 2)):
                    px(d, ex + dx, ey + dy, EYE)
            elif blink:
                for dx in (-2, -1, 0, 1, 2):
                    px(d, ex + dx, ey + 2, EYE)
            else:
                ell(d, ex, ey + 1, 2.6, 3.4, EYE)
                ell(d, ex, ey + 3, 1.6, 1.0, EYE_GLOW)
                px(d, ex - 1, ey - 1, WHITE)
                px(d, ex, ey - 1, WHITE)
                px(d, ex - 1, ey, WHITE)
                px(d, ex + 1, ey + 3, WHITE)

    c.overlay(eyes)

    # ---------------- blush (soft rosy cheeks flanking eyes)
    def blush(d):
        ell(d, hx - 9.2, hy + 5.5, 2.8, 1.8, BLUSH)
        ell(d, hx + 9.2, hy + 5.5, 2.8, 1.8, BLUSH)

    c.overlay(blush)

    # ---------------- star cookie (EAT)
    if star_stage:
        r = {1: 6.5, 2: 4.8, 3: 3.0}[star_stage]
        scx, scy = hx + 14, hy + 15

        def star(d):
            d.polygon(star_poly(scx, scy, r, r * 0.5), fill=STAR)
            px(d, scx - 1, scy - 1, STAR_LT)

        c.part(star, outline=STAR_OUT)

        def holdpaw(d):
            ell(d, scx - 5, scy + 4, 3.2, 2.8, FOOT)

        c.part(holdpaw)
    if heart_pos:
        draw_heart(c, heart_pos[0], heart_pos[1])

    # ---------------- extras
    if sleeping:
        draw_zzz(c, zzz_stage)
    if sparkles:
        sparkle(c, 8, 18 + by, True)
        sparkle(c, 56, 12 + by)
        sparkle(c, 12, 30 + by)
    if speed_lines:
        def lines(d):
            for y, x0, x1 in ((46, 2, 9), (51, 0, 7), (41, 4, 8)):
                d.line([(x0, y + by), (x1, y + by)], fill=(255, 255, 255, 200))

        c.overlay(lines)

    img = c.img
    if tilt:
        img = img.rotate(tilt, resample=Image.Resampling.NEAREST, center=(32, 40))
    return img.resize((128, 128), Image.Resampling.NEAREST)


def create_toy_sprite() -> Image.Image:
    """A cute little striped beach ball."""
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([2, 2, 29, 29], fill=(66, 28, 70, 255))
    d.ellipse([3, 3, 28, 28], fill=(255, 108, 140, 255))
    d.pieslice([3, 3, 28, 28], 200, 260, fill=(255, 224, 90, 255))
    d.pieslice([3, 3, 28, 28], 320, 20, fill=(255, 224, 90, 255))
    d.pieslice([3, 3, 28, 28], 80, 140, fill=(120, 205, 255, 255))
    d.ellipse([12, 12, 19, 19], fill=(255, 255, 255, 255))
    d.ellipse([7, 6, 12, 10], fill=(255, 255, 255, 200))
    return img.resize((128, 128), Image.Resampling.NEAREST)


def create_bed_sprite() -> Image.Image:
    """A plush, cozy pastel oval pet bed with soft cushion, headrest pillow, and embroidered paw."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    OUT = (66, 38, 28, 255)
    RIM = (180, 130, 95, 255)
    RIM_LT = (215, 170, 130, 255)
    RIM_SH = (140, 95, 65, 255)
    CUSHION = (255, 220, 230, 255)
    CUSHION_SH = (235, 190, 205, 255)
    PILLOW = (240, 245, 255, 255)
    PILLOW_SH = (200, 215, 240, 255)
    PAW = (255, 160, 180, 255)

    # Shadow on floor
    d.ellipse([6, 42, 58, 58], fill=(40, 30, 40, 60))
    
    # Outer Bolster / Rim
    d.ellipse([7, 20, 57, 52], fill=OUT)
    d.ellipse([8, 21, 56, 51], fill=RIM_SH)
    d.ellipse([8, 21, 56, 46], fill=RIM)
    d.ellipse([10, 22, 54, 40], fill=RIM_LT)

    # Inner plush cushion
    d.ellipse([12, 26, 52, 48], fill=OUT)
    d.ellipse([13, 27, 51, 47], fill=CUSHION_SH)
    d.ellipse([13, 27, 51, 44], fill=CUSHION)
    
    # Fluffy mini headrest pillow
    d.ellipse([15, 26, 32, 36], fill=OUT)
    d.ellipse([16, 27, 31, 35], fill=PILLOW_SH)
    d.ellipse([16, 27, 31, 33], fill=PILLOW)

    # Embroidered pink paw print
    d.ellipse([34, 34, 40, 39], fill=PAW)
    d.ellipse([32, 31, 34, 33], fill=PAW)
    d.ellipse([35, 30, 37, 32], fill=PAW)
    d.ellipse([38, 30, 40, 32], fill=PAW)
    d.ellipse([41, 32, 43, 34], fill=PAW)

    return img.resize((128, 128), Image.Resampling.NEAREST)


def create_food_bowl_sprite() -> Image.Image:
    """A cute ceramic pet food dish filled with golden star kibble and berries, with a heart emblem."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    OUT = (66, 38, 28, 255)
    BOWL = (235, 95, 120, 255)
    BOWL_LT = (255, 140, 160, 255)
    BOWL_SH = (180, 60, 85, 255)
    BOWL_DK = (130, 40, 60, 255)
    FOOD_BASE = (170, 110, 55, 255)
    STAR_GOLD = (255, 225, 65, 255)
    STAR_SH = (220, 160, 35, 255)
    BERRY = (165, 55, 120, 255)
    BERRY_LT = (215, 95, 170, 255)

    # Floor shadow
    d.ellipse([10, 44, 54, 56], fill=(40, 30, 40, 60))

    # Outer base polygon + bottom arc
    base_poly = [(12, 28), (52, 28), (47, 46), (17, 46)]
    d.polygon(base_poly, fill=OUT)
    d.pieslice([17, 38, 47, 48], 0, 180, fill=OUT)
    
    # Fill body
    inner_body = [(13, 28), (51, 28), (46, 45), (18, 45)]
    d.polygon(inner_body, fill=BOWL_SH)
    d.pieslice([18, 38, 46, 47], 0, 180, fill=BOWL_SH)

    # Front highlight and base shading
    d.polygon([(16, 28), (48, 28), (44, 43), (20, 43)], fill=BOWL)
    d.polygon([(22, 28), (42, 28), (39, 41), (25, 41)], fill=BOWL_LT)

    # Rim (outer ellipse)
    d.ellipse([10, 20, 54, 34], fill=OUT)
    d.ellipse([11, 21, 53, 33], fill=BOWL)
    
    # Inner bowl food cavity (ellipse)
    d.ellipse([14, 22, 50, 32], fill=BOWL_DK)
    d.ellipse([15, 23, 49, 31], fill=FOOD_BASE)

    # Golden star kibble biscuits
    for sx, sy in ((24, 25), (32, 24), (40, 25), (28, 28), (36, 27)):
        d.ellipse([sx - 3, sy - 2, sx + 3, sy + 2], fill=STAR_GOLD)
        d.point((sx - 1, sy - 1), fill=(255, 255, 255, 255))
        d.point((sx + 1, sy + 1), fill=STAR_SH)

    # Juicy berries
    for bx, by in ((20, 27), (44, 26)):
        d.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=BERRY)
        d.point((bx - 1, by - 1), fill=BERRY_LT)

    # Cute white heart on the front of the bowl
    d.polygon([(32, 42), (28, 37), (29, 34), (32, 36), (35, 34), (36, 37)], fill=(255, 255, 255, 240))
    d.point((32, 37), fill=BOWL_LT)

    return img.resize((128, 128), Image.Resampling.NEAREST)


# ------------------------------------------------------------------ sprite sheet
STATES = ("idle", "walk", "play", "sleep", "eat", "jump")


def build_frames() -> dict:
    g = create_griffin_sprite
    return {
        "idle": [
            g(bob_y=-0.5, wing_pose="MID", tail_angle=0),
            g(bob_y=-1.5, wing_pose="UP", tail_angle=2),
            g(bob_y=-0.5, wing_pose="MID", tail_angle=0),
            g(bob_y=0.5, wing_pose="DOWN", tail_angle=-2, blink=True),
        ],
        "walk": [
            g(bob_y=-1.5, wing_pose="UP", tail_angle=2, front_paw_offset=(0, -2), back_paw_offset=(0, -2)),
            g(bob_y=-0.5, wing_pose="GLIDE", tail_angle=0, front_paw_offset=(1, -1), back_paw_offset=(0, -1)),
            g(bob_y=0.8, wing_pose="DOWN", tail_angle=-2, front_paw_offset=(0, -2), back_paw_offset=(0, -2)),
            g(bob_y=-0.3, wing_pose="MID", tail_angle=0, front_paw_offset=(1, -1), back_paw_offset=(0, -1)),
        ],
        "play": [
            g(bob_y=-2, wing_pose="UP", happy_eyes=True, tail_angle=3, front_paw_offset=(3, -4), tilt=-12),
            g(bob_y=-1, wing_pose="MID", happy_eyes=True, tail_angle=1, front_paw_offset=(4, -2), tilt=0),
            g(bob_y=-2, wing_pose="DOWN", happy_eyes=True, tail_angle=-2, front_paw_offset=(3, -4), tilt=12),
            g(bob_y=-1, wing_pose="MID", happy_eyes=True, tail_angle=0, front_paw_offset=(4, -2), tilt=0, sparkles=True),
        ],
        "sleep": [
            g(sleeping=True, wing_pose="TUCKED", zzz_stage=1),
            g(sleeping=True, wing_pose="TUCKED", zzz_stage=2),
            g(sleeping=True, wing_pose="TUCKED", zzz_stage=3),
            g(sleeping=True, wing_pose="TUCKED", zzz_stage=2),
        ],
        "eat": [
            g(bob_y=-0.5, wing_pose="MID", happy_eyes=True, star_stage=1),
            g(bob_y=0.2, wing_pose="UP", happy_eyes=True, star_stage=2, heart_pos=(55, 12)),
            g(bob_y=-0.5, wing_pose="MID", happy_eyes=True, star_stage=3, heart_pos=(55, 8)),
            g(bob_y=0.0, wing_pose="DOWN", happy_eyes=True, star_stage=0, heart_pos=(55, 4)),
        ],
        "jump": [
            g(bob_y=-1.0, wing_pose="DOWN", happy_eyes=True, sparkles=True, front_paw_offset=(2, -3), back_paw_offset=(-2, -3)),
            g(bob_y=-2.0, squish_y=-1, wing_pose="UP", happy_eyes=True, sparkles=True, speed_lines=True, front_paw_offset=(2, -3), back_paw_offset=(-2, -3)),
            g(bob_y=-2.5, wing_pose="GLIDE", happy_eyes=True, sparkles=True, speed_lines=True, front_paw_offset=(2, -3), back_paw_offset=(-2, -3)),
            g(bob_y=-1.5, wing_pose="MID", happy_eyes=True, sparkles=True, front_paw_offset=(2, -3), back_paw_offset=(-2, -3)),
        ],
        # EAT_BOWL: dipping beak into the food bowl, happily chewing kibbles
        "eat_bowl": [
            g(bob_y=0.2, tilt=-6, happy_eyes=True, sparkles=False, front_paw_offset=(2, 0), head_offset=(3, 4)),
            g(bob_y=0.8, squish_y=1, tilt=-10, happy_eyes=True, sparkles=True, front_paw_offset=(3, 0), head_offset=(5, 6)),
            g(bob_y=-0.2, tilt=-4, happy_eyes=True, heart_pos=(54, 10), head_offset=(2, 3)),
            g(bob_y=0.6, tilt=-8, happy_eyes=True, sparkles=True, front_paw_offset=(3, 0), head_offset=(4, 5)),
        ],
        "sleep_bed": [
            g(sleeping=True, wing_pose="TUCKED", zzz_stage=1, no_cloud=True),
            g(sleeping=True, wing_pose="TUCKED", zzz_stage=2, no_cloud=True),
            g(sleeping=True, wing_pose="TUCKED", zzz_stage=3, no_cloud=True),
            g(sleeping=True, wing_pose="TUCKED", zzz_stage=2, no_cloud=True),
        ],
    }


STYLES = ("cute", "real")


def ensure_sprites_exist(sprites_dir: str, force: bool = False, style: str = None) -> None:
    """Create every sprite PNG of a style inside sprites_dir if missing.

    The style is taken from the folder name (".../cute" or ".../real") unless given.
    """
    if style is None:
        style = "real" if os.path.basename(os.path.normpath(sprites_dir)).lower() == "real" else "cute"
    if style == "real":
        from sprite_generator_real import ensure_real_sprites
        ensure_real_sprites(sprites_dir, force)
        return
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
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites")
    for st in STYLES:
        ensure_sprites_exist(os.path.join(root, st), force=True, style=st)
    print("Sprites regenerated in", root)
