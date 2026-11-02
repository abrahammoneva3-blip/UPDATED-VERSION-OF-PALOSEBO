"""Small pixel-art drawing helpers shared by every module."""
import math
import pygame
from settings import *
from pixelfont import draw_text, text_width


def shade(c, f):
    return (max(0, min(255, int(c[0] * f))), max(0, min(255, int(c[1] * f))), max(0, min(255, int(c[2] * f))))


def mix(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t), int(a[2] + (b[2] - a[2]) * t))


def add_outline(surf, color=OUTLINE, corners=False):
    """Return a copy of `surf` with a 1px pixel-art outline (surface grows by 2px)."""
    w, h = surf.get_size()
    out = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    sil = pygame.mask.from_surface(surf).to_surface(setcolor=color + (255,), unsetcolor=(0, 0, 0, 0))
    offs = [(0, 1), (2, 1), (1, 0), (1, 2)]
    if corners:
        offs += [(0, 0), (2, 2), (0, 2), (2, 0)]
    for dx, dy in offs:
        out.blit(sil, (dx, dy))
    out.blit(surf, (1, 1))
    return out


def band_gradient(w, h, stops, band=6, dither=True):
    """Vertical banded (retro) gradient. stops = [(pos 0..1 top->bottom, colour), ...]"""
    surf = pygame.Surface((w, h))
    stops = sorted(stops, key=lambda s: s[0])

    def col_at(t):
        for i in range(len(stops) - 1):
            a, b = stops[i], stops[i + 1]
            if a[0] <= t <= b[0]:
                return mix(a[1], b[1], (t - a[0]) / max(1e-6, b[0] - a[0]))
        return stops[0][1] if t < stops[0][0] else stops[-1][1]

    y = 0
    prev = None
    while y < h:
        bh = min(band, h - y)
        c = col_at((y + bh / 2) / h)
        surf.fill(c, (0, y, w, bh))
        if dither and prev is not None:
            # checker-dither strip between bands
            for x in range(0, w, 2):
                surf.set_at((x, y), prev)
                if y + 1 < h:
                    surf.set_at((x + 1, y + 1), prev)
        prev = c
        y += bh
    return surf


def panel(surf, rect, fill=DKBLUE, border=OUTLINE, light=None, dark=None, radius_cut=True):
    """Chunky pixel panel with bevel and clipped corners."""
    x, y, w, h = rect
    light = light or shade(fill, 1.35)
    dark = dark or shade(fill, 0.65)
    surf.fill(border, (x + 1, y, w - 2, h))
    surf.fill(border, (x, y + 1, w, h - 2))
    surf.fill(fill, (x + 1, y + 1, w - 2, h - 2))
    surf.fill(light, (x + 2, y + 1, w - 4, 1))
    surf.fill(light, (x + 1, y + 2, 1, h - 4))
    surf.fill(dark, (x + 2, y + h - 2, w - 4, 1))
    surf.fill(dark, (x + w - 2, y + 2, 1, h - 4))


def draw_button(surf, rect, label, selected=False, pressed=False, disabled=False, scale=1, base=BLUE, sel=RED):
    x, y, w, h = rect
    if disabled:
        fill, txt = DKGRAY, GRAY
    elif selected:
        fill, txt = sel, WHITE
    else:
        fill, txt = base, CREAM
    off = 1 if pressed else 0
    if not pressed:
        surf.fill(shade(fill, 0.45), (x + 1, y + 2, w - 2, h - 1))
    panel(surf, (x, y + off, w, h - 1), fill, OUTLINE)
    if selected and not disabled:
        surf.fill(YELLOW, (x + 3, y + off + 2, w - 6, 1))
    ty = y + off + (h - 1 - 7 * scale) // 2
    draw_text(surf, label, x + w // 2, ty, txt, scale, shadow=shade(fill, 0.4), align="center")


def star(surf, cx, cy, r, color):
    pygame.draw.polygon(surf, color, [(cx, cy - r), (cx + 1, cy - 1), (cx + r, cy), (cx + 1, cy + 1),
                                       (cx, cy + r), (cx - 1, cy + 1), (cx - r, cy), (cx - 1, cy - 1)])


def draw_trophy(surf, x, y, scale=1):
    """Pixel-art trophy, (x, y) = top-centre."""
    s = pygame.Surface((14, 15), pygame.SRCALPHA)
    g, d, l = GOLD, shade(GOLD, 0.7), (255, 236, 130)
    s.fill(g, (3, 0, 8, 7)); s.fill(l, (4, 1, 2, 5)); s.fill(d, (9, 1, 2, 6))
    s.fill(g, (2, 1, 1, 1)); s.fill(g, (11, 1, 1, 1))
    s.fill(g, (0, 1, 2, 4)); s.fill(g, (12, 1, 2, 4))
    s.fill(OUTLINE, (1, 2, 1, 2)); s.fill(OUTLINE, (12, 2, 1, 2))
    s.fill(g, (4, 7, 6, 2)); s.fill(g, (6, 9, 2, 3))
    s.fill(BROWN, (3, 12, 8, 3)); s.fill(shade(BROWN, 1.3), (3, 12, 8, 1))
    s.fill(YELLOW, (6, 3, 2, 2))
    s = add_outline(s)
    if scale > 1:
        s = pygame.transform.scale(s, (s.get_width() * scale, s.get_height() * scale))
    surf.blit(s, (x - s.get_width() // 2, y))


def draw_coin(surf, x, y, t=0.0, spin=True):
    """Spinning pixel coin, (x, y) = centre."""
    frames = [7, 5, 3, 1, 3, 5]
    w = frames[int(t * 8) % 6] if spin else 7
    hw = max(1, w // 2)
    surf.fill(OUTLINE, (x - hw - 1, y - 4, w + 2, 9))
    surf.fill(GOLD, (x - hw, y - 3, w, 7))
    if w >= 5:
        surf.fill((255, 236, 130), (x - hw + 1, y - 2, 1, 5))
        surf.fill(shade(GOLD, 0.75), (x + hw - 1, y - 2, 1, 5))
        surf.fill(shade(GOLD, 0.75), (x - 1, y - 1, 2, 3))
    else:
        surf.fill((255, 236, 130), (x - hw, y - 3, max(1, w // 2), 7))


def draw_key(surf, x, y, label, w=9, pressed=False):
    """Little keyboard keycap, (x, y) = top-left."""
    off = 1 if pressed else 0
    surf.fill(OUTLINE, (x, y + 1, w, 10))
    surf.fill(shade(CREAM, 0.6), (x + 1, y + 2 + off * 0, w - 2, 9 - 1 if not off else 8))
    surf.fill(CREAM, (x + 1, y + 1 + off, w - 2, 8))
    surf.fill(WHITE, (x + 1, y + 1 + off, w - 2, 1))
    draw_text(surf, label, x + w // 2, y + 2 + off, OUTLINE, 1, align="center")


def make_cloud(w, h, color=WHITE, shadow=(206, 226, 246), seed=0):
    import random
    rng = random.Random(seed)
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    n = max(3, w // 12)
    for i in range(n):
        cx = int(w * (0.18 + 0.64 * i / max(1, n - 1)))
        r = rng.randint(h // 4, h // 2 - 1)
        cy = h - r - 2 - (0 if i in (0, n - 1) else rng.randint(0, h // 4))
        pygame.draw.circle(s, shadow, (cx, cy + 2), r)
    for i in range(n):
        cx = int(w * (0.18 + 0.64 * i / max(1, n - 1)))
        r = rng.randint(h // 4, h // 2 - 1)
        cy = h - r - 4 - (0 if i in (0, n - 1) else rng.randint(0, h // 4))
        pygame.draw.circle(s, color, (cx, cy), r)
    s.fill(color, (w // 8, h - 8, w * 3 // 4, 5))
    s.fill(shadow, (w // 8, h - 4, w * 3 // 4, 3))
    return s
