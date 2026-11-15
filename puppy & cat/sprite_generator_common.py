"""
Shared pixel-art drawing utilities for Puppy & Cat Desktop Pets.
Provides 64x64 grid canvas, anti-aliasing / pixel outline dilation, and particle primitives.
"""
import math
import numpy as np
from PIL import Image, ImageDraw

W, H = 64, 64
OUT = (35, 24, 18, 255)
SHADOW = (0, 0, 0, 48)
WHITE = (255, 255, 255, 255)
PINK_BEANS = (255, 155, 175, 255)
HEART_RED = (255, 75, 105, 255)
HEART_OUT = (165, 25, 45, 255)
ZZZ_PURPLE = (175, 140, 245, 255)
ZZZ_OUT = (95, 65, 165, 255)


def px(d, x, y, col):
    """Draw a single pixel on the canvas."""
    ix, iy = int(round(x)), int(round(y))
    if 0 <= ix < W and 0 <= iy < H:
        d.point((ix, iy), fill=col)


def ell(d, cx, cy, rx, ry, col):
    """Draw a solid filled ellipse centered at (cx, cy)."""
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=col)


def tline(d, p0, p1, width, col):
    """Draw a thick smooth line between p0 and p1."""
    d.line([p0, p1], fill=col, width=int(width))
    r = width / 2.0
    ell(d, p0[0], p0[1], r, r, col)
    ell(d, p1[0], p1[1], r, r, col)


class Canvas:
    """Multi-layer RGBA sprite canvas with automatic crisp 1px outline rendering."""

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
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        painter(ImageDraw.Draw(layer))
        self.img.alpha_composite(layer)


def draw_zzz(c, stage, dy=0, dx=0):
    """Draw cute floating sleep Zzz's."""
    spots = [(46 + dx, 16 + dy, 3), (52 + dx, 9 + dy, 4), (45 + dx, 3 + dy, 5)]
    for i in range(min(stage, 3)):
        x, y, s = spots[i]

        def z(d, x=x, y=y, s=s):
            for ox in (-1, 0, 1):
                for oy in (-1, 0, 1):
                    d.line([(x + ox, y + oy), (x + s + ox, y + oy)], fill=ZZZ_OUT)
                    d.line([(x + s + ox, y + oy), (x + ox, y + s + oy)], fill=ZZZ_OUT)
                    d.line([(x + ox, y + s + oy), (x + s + ox, y + s + oy)], fill=ZZZ_OUT)
            d.line([(x, y), (x + s, y)], fill=ZZZ_PURPLE)
            d.line([(x + s, y), (x, y + s)], fill=ZZZ_PURPLE)
            d.line([(x, y + s), (x + s, y + s)], fill=ZZZ_PURPLE)

        c.overlay(z)


def draw_heart(c, x, y):
    """Draw a pixel-art floating heart with dark outline."""
    pts = [
        (1, 0), (2, 0), (4, 0), (5, 0),
        (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1),
        (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2),
        (1, 3), (2, 3), (3, 3), (4, 3), (5, 3),
        (2, 4), (3, 4), (4, 4),
        (3, 5),
    ]

    def p(d):
        s = set(pts)
        for (hx, hy) in pts:
            for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (hx + ox, hy + oy) not in s:
                    px(d, x + hx + ox, y + hy + oy, HEART_OUT)
        for (hx, hy) in pts:
            px(d, x + hx, y + hy, HEART_RED)
        px(d, x + 1, y + 1, WHITE)

    c.overlay(p)
