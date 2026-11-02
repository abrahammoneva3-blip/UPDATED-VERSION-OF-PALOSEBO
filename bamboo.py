"""Greased bamboo poles with sway animation, plus the waving fiesta flags."""
import math
import pygame
import catalog
from gfx import add_outline, shade, mix
from settings import *

TILE_W, TILE_H = 12, 30
SWAY_W = 1.7
_tile_cache = {}
_flag_cache = {}
_base_cache = {}


def sy(h, cam):
    """World height -> screen y."""
    return GROUND_Y - (h - cam)


# ----------------------------------------------------------------- textures --
def _pole_tile(design_id):
    if design_id in _tile_cache:
        return _tile_cache[design_id]
    d = catalog.by_id(catalog.BAMBOOS, design_id)
    base = d["color"]
    tile = pygame.Surface((TILE_W, TILE_H * 2), pygame.SRCALPHA)
    factors = [0.6, 0.85, 1.05, 1.28, 1.08, 0.9, 0.72, 0.55]
    for rep in range(2):
        oy = rep * TILE_H
        for row in range(TILE_H):
            y = oy + row
            if row < 3:  # node ring (slightly wider than the pole)
                f = (0.5, 1.0, 0.62)[row]
                c = shade(base if design_id != "guhit" else (190, 120, 60), f)
                tile.fill(c, (1, y, TILE_W - 2, 1))
                tile.fill(OUTLINE, (0, y, 1, 1))
                tile.fill(OUTLINE, (TILE_W - 1, y, 1, 1))
                if row == 1:
                    tile.fill(shade(base if design_id != "guhit" else (255, 220, 150), 1.35), (3, y, 3, 1))
                continue
            tile.fill(OUTLINE, (1, y, 1, 1))
            tile.fill(OUTLINE, (TILE_W - 2, y, 1, 1))
            for col in range(8):
                c0 = base
                if design_id == "guhit":
                    c0 = RED if ((row + col) // 5) % 2 == 0 else CREAM
                elif design_id == "laso":
                    k = (row + col) % 15
                    if k < 3:
                        c0 = RED if k != 0 else (255, 150, 150)
                c = shade(c0, factors[col])
                tile.fill(c, (2 + col, y, 1, 1))
            # greasy shine ("sebo") - broken highlight streaks
            if row in (7, 8, 9, 10, 11, 17, 18, 19, 24, 25):
                tile.fill(mix(tile.get_at((4, y))[:3], WHITE, 0.6), (4, y, 2, 1))
            if row in (13, 14, 21, 22):
                tile.fill(mix(tile.get_at((8, y))[:3], WHITE, 0.4), (8, y, 1, 1))
    _tile_cache[design_id] = tile
    return tile


def _make_flag(design_id):
    if design_id in _flag_cache:
        return _flag_cache[design_id]
    w, h = 26, 16
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    if design_id == "araw":
        s.fill(BLUE, (0, 0, w, h // 2))
        s.fill(RED, (0, h // 2, w, h // 2))
        cx, cy = 13, 8
        for a in range(8):
            ang = a * math.pi / 4
            pygame.draw.line(s, YELLOW, (cx, cy), (cx + round(math.cos(ang) * 6), cy + round(math.sin(ang) * 6)), 1)
        pygame.draw.circle(s, YELLOW, (cx, cy), 3)
        pygame.draw.circle(s, GOLD, (cx + 1, cy + 1), 1)
        s.fill(YELLOW, (0, 0, w, 1))
        s.fill(YELLOW, (0, h - 1, w, 1))
    elif design_id == "banderitas":
        cols = [RED, YELLOW, BLUE, GREEN, ORANGE, PINK]
        for x in range(w):
            s.fill(cols[(x // 4) % len(cols)], (x, 0, 1, h))
        for x in range(w):
            zig = 2 if (x // 2) % 2 == 0 else 0
            s.fill(WHITE, (x, zig, 1, 1))
        s.fill(shade(YELLOW, 0.9), (0, h - 2, w, 2))
    elif design_id == "inabel":
        s.fill(DKRED, (0, 0, w, h))
        for y in range(h):
            for x in range(w):
                k = (abs((x % 8) - 4) + abs((y % 8) - 4))
                if k == 2:
                    s.set_at((x, y), CREAM)
                elif k == 4 and (x + y) % 2 == 0:
                    s.set_at((x, y), BLACK)
                elif k == 0:
                    s.set_at((x, y), GOLD)
        s.fill(BLACK, (0, 0, w, 1)); s.fill(BLACK, (0, h - 1, w, 1))
        s.fill(CREAM, (0, 1, w, 1)); s.fill(CREAM, (0, h - 2, w, 1))
    elif design_id == "bituin":
        s.fill(DKBLUE, (0, 0, w, h))
        s.fill(WHITE, (0, 0, w, 1)); s.fill(WHITE, (0, h - 1, w, 1))
        from gfx import star
        for cx, cy, r in ((5, 8, 3), (13, 5, 3), (20, 10, 3)):
            star(s, cx, cy, r, YELLOW)
    else:  # pabalat (cut-paper)
        s.fill(PINK, (0, 0, w, h))
        for x in range(0, w, 4):
            s.fill(WHITE, (x, 0, 2, 2)); s.fill(WHITE, (x + 2, h - 2, 2, 2))
        for x in range(2, w - 2, 5):
            s.fill(YELLOW, (x, 5, 3, 1)); s.fill(YELLOW, (x + 1, 4, 1, 3)); s.fill(WHITE, (x + 1, 9, 1, 2))
        s.fill(shade(PINK, 0.75), (0, h // 2, w, 1))
    s = add_outline(s)
    _flag_cache[design_id] = s
    return s


def _make_base():
    if "b" in _base_cache:
        return _base_cache["b"]
    s = pygame.Surface((40, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(s, shade(BROWN, 0.8), (0, 5, 40, 9))
    pygame.draw.ellipse(s, BROWN, (1, 3, 38, 9))
    pygame.draw.ellipse(s, shade(BROWN, 1.25), (5, 3, 24, 4))
    for x, y, r in ((5, 8, 2), (32, 9, 2), (26, 6, 1), (11, 10, 1)):
        pygame.draw.circle(s, GRAY, (x, y), r)
        s.set_at((x - 1, y - 1), LTGRAY)
    # little banderitas ribbon around the pole foot
    for i, c in enumerate((RED, YELLOW, BLUE, RED, YELLOW)):
        s.fill(c, (13 + i * 3, 4 + (i % 2), 3, 2))
    s = add_outline(s)
    _base_cache["b"] = s
    return s


# ---------------------------------------------------------------------------- #
class Bamboo:
    def __init__(self, x, design="berde", flag="araw", phase=0.0, amp=5.0):
        self.x = x
        self.design = design
        self.flag = flag
        self.phase = phase
        self.amp = amp
        self.flag_taken = False
        self._s = 0.0
        self._ds = 0.0
        self._amp_eff = amp
        self._lean = 0.0

    # -- sway ---------------------------------------------------------------------
    def prepare(self, t, env):
        w = SWAY_W
        a = w * t + self.phase
        b = 2.3 * w * t + self.phase * 1.7 + 1.3
        self._s = 0.75 * math.sin(a) + 0.25 * math.sin(b)
        self._ds = (0.75 * w * math.cos(a) + 0.25 * 2.3 * w * math.cos(b)) / (1.325 * w)
        self._mult = env.sway_mult if env else 1.0
        self._lean = env.gust_px if env else 0.0
        self._amp_eff = self.amp * self._mult

    def offset(self, h):
        hf = max(0.0, min(1.0, h / POLE_H))
        return int(round((self._amp_eff * self._s + self._lean) * hf ** 1.5))

    def push(self, h):
        """Balance acceleration felt by a climber at height h (normalised, before gain)."""
        hf = max(0.0, min(1.0, h / POLE_H))
        return self._ds * (self._mult) * (0.35 + 0.65 * hf)

    # -- drawing ------------------------------------------------------------------
    def draw(self, surf, cam, t, taken_flag=False):
        cam = int(cam)
        tile = _pole_tile(self.design)
        y_top = max(0, sy(POLE_H, cam))
        y_bot = min(H, sy(0, cam) + 2)
        cx = self.x
        if y_bot > 0 and y_top < H:
            y = y_top - (y_top % 2)
            while y < y_bot:
                h = GROUND_Y - y + cam
                r = (-h) % TILE_H
                ox = self.offset(h)
                surf.blit(tile, (cx + ox - TILE_W // 2, y), (0, r, TILE_W, 2))
                y += 2
        # finial + flag stick
        top_off = self.offset(POLE_H)
        ty = sy(POLE_H, cam)
        fx = cx + top_off
        if -40 < ty < H + 30:
            surf.fill(OUTLINE, (fx - 1, ty - 21, 4, 22))
            surf.fill(shade(BROWN, 1.2), (fx, ty - 20, 2, 21))
            pygame.draw.circle(surf, OUTLINE, (fx + 1, ty - 22), 3)
            pygame.draw.circle(surf, GOLD, (fx + 1, ty - 22), 2)
            surf.set_at((fx + 1, ty - 23), (255, 236, 130))
            if not (taken_flag or self.flag_taken):
                self.draw_flag(surf, fx + 2, ty - 20, t)
        # base mound
        by = sy(0, cam)
        if by < H + 10:
            surf.blit(_make_base(), (cx - 20, by - 5))

    def draw_flag(self, surf, x, y, t, design=None, scale_wave=1.0):
        draw_flag(surf, x, y, design or self.flag, t + self.phase, scale_wave)


def draw_flag(surf, x, y, design, t, wave=1.0):
    """Waving flag; (x, y) = top-left where the flag attaches to its stick."""
    tex = _make_flag(design)
    w, h = tex.get_size()
    for c in range(w):
        amp = wave * min(1.0, c / 10.0) * 1.8
        oy = int(round(math.sin(t * 6.0 + c * 0.45) * amp))
        surf.blit(tex, (x + c - 1, y + oy - 1), (c, 0, 1, h))


def flag_texture(design):
    return _make_flag(design)
