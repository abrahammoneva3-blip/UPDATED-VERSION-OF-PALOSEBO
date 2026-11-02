"""Procedural pixel-art fiesta stages: parallax sky, mountains, houses, crowd, banderitas."""
import math
import random
import pygame
import catalog
from gfx import add_outline, band_gradient, shade, mix, make_cloud
from pixelfont import draw_text, text_width
from effects import Particles
from settings import *

SKY_H = 500
FAR_A, MID_A, NEAR_A = 150, 150, 90      # pixels above the ground line in each layer
BELOW = H - GROUND_Y                     # 40 px of ground below the ground line

# ------------------------------------------------------------------ stage looks --
LOOKS = {
    1: dict(sky=[(0, (60, 140, 228)), (1, (196, 232, 255))], far=[(120, 170, 200), (92, 152, 128)],
            grass=(96, 170, 70), plaza=(200, 156, 100), sun=True, crowd_pal=None),
    2: dict(sky=[(0, (86, 160, 232)), (1, (255, 236, 196))], far=[(150, 176, 196), (104, 156, 130)],
            grass=(110, 172, 80), plaza=(218, 190, 154), sun=True),
    3: dict(sky=[(0, (110, 90, 180)), (0.55, (255, 150, 120)), (1, (255, 214, 140))], far=[(150, 110, 170), (120, 96, 150)],
            grass=(238, 208, 140), plaza=(246, 222, 160), sun=True),
    4: dict(sky=[(0, (104, 168, 236)), (1, (255, 240, 214))], far=[(110, 140, 176), (80, 110, 150)],
            grass=(84, 154, 84), plaza=(190, 156, 110), sun=True),
    5: dict(sky=[(0, (24, 26, 84)), (0.6, (150, 80, 160)), (1, (255, 150, 120))], far=[(74, 56, 120), (56, 46, 100)],
            grass=(66, 128, 76), plaza=(176, 136, 112), sun=False),
}
THEMES = {
    "sunset": dict(sky=[(0, (100, 70, 170)), (0.5, (240, 120, 120)), (1, (255, 200, 120))], tint=(255, 226, 200)),
    "night": dict(sky=[(0, (12, 14, 50)), (1, (70, 60, 130))], tint=(150, 160, 215), stars=True),
}


def _surf(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def _thatch(s, poly, base, seed=1):
    pygame.draw.polygon(s, base, poly)


# ---------------------------------------------------------------- structures --
def make_kubo(variant=0):
    s = _surf(48, 46)
    wood, dk = (110, 70, 44), (74, 46, 34)
    for x in (8, 16, 30, 38):
        s.fill(wood, (x, 30, 2, 16)); s.fill(dk, (x + 1, 30, 1, 16))
    s.fill((176, 128, 70), (5, 28, 38, 2)); s.fill(dk, (5, 30, 38, 1))
    wall = (214, 172, 100) if variant % 2 == 0 else (196, 150, 84)
    s.fill(wall, (8, 15, 32, 13))
    for y in range(15, 28):
        for x in range(8, 40):
            if (x + y) % 4 == 0:
                s.set_at((x, y), shade(wall, 0.8))
    s.fill(dk, (18, 18, 12, 7)); s.fill((40, 30, 40), (19, 19, 10, 5))
    pygame.draw.line(s, (176, 128, 70), (18, 17), (29, 17), 1)
    s.fill((150, 100, 60), (18, 25, 12, 1))
    thatch, thd = (222, 184, 92), (176, 136, 60)
    pygame.draw.polygon(s, thd, [(0, 18), (47, 18), (35, 1), (12, 1)])
    pygame.draw.polygon(s, thatch, [(1, 16), (46, 16), (34, 2), (13, 2)])
    for y in range(4, 17, 3):
        s.fill(thd, (max(2, 14 - (y - 2) * 1), y, 30 + (y - 2) * 2, 1))
    for x in range(1, 47, 3):
        s.set_at((x, 17), thd)
    s.fill(dk, (40, 30, 1, 16))
    for i in range(6):
        s.fill(dk, (41 + i // 3, 30 + i * 2, 3, 1))
    return add_outline(s)


def make_stall(c1, c2):
    s = _surf(30, 30)
    s.fill((110, 70, 44), (2, 8, 2, 22)); s.fill((110, 70, 44), (26, 8, 2, 22))
    s.fill((150, 100, 60), (3, 20, 24, 10)); s.fill((190, 140, 84), (3, 20, 24, 2))
    for i, c in enumerate((RED, YELLOW, BLUE, GREEN)):
        s.fill(c, (5 + i * 5, 17, 3, 3))
    for x in range(0, 30, 6):
        s.fill(c1, (x, 4, 3, 6)); s.fill(c2, (x + 3, 4, 3, 6))
    s.fill(c1, (0, 1, 30, 3))
    for x in range(0, 30, 6):
        s.fill(c1, (x + 1, 10, 2, 1)); s.fill(c2, (x + 4, 10, 2, 1))
    return add_outline(s)


def make_church():
    s = _surf(64, 66)
    wall, sh = (244, 230, 194), (214, 196, 156)
    s.fill(wall, (6, 32, 52, 34)); s.fill(sh, (50, 32, 8, 34))
    pygame.draw.polygon(s, (178, 84, 62), [(4, 34), (60, 34), (32, 20)])
    pygame.draw.polygon(s, (204, 108, 78), [(8, 33), (56, 33), (32, 22)])
    s.fill(wall, (22, 6, 20, 30)); s.fill(sh, (38, 6, 4, 30))
    pygame.draw.polygon(s, (178, 84, 62), [(20, 8), (44, 8), (32, 0)])
    s.fill(YELLOW, (31, -1, 2, 1)) if False else None
    s.fill(GOLD, (31, 0, 2, 3)); s.fill(GOLD, (30, 1, 4, 1))
    pygame.draw.circle(s, (60, 40, 60), (32, 15), 4); s.fill((60, 40, 60), (28, 15, 9, 6))
    s.fill(GOLD, (31, 15, 2, 3))
    s.fill((60, 40, 60), (28, 46, 9, 20)); pygame.draw.circle(s, (60, 40, 60), (32, 46), 4)
    s.fill((130, 86, 56), (30, 48, 5, 18))
    for x in (12, 46):
        s.fill((60, 40, 60), (x, 40, 5, 9)); s.fill((120, 180, 230), (x + 1, 41, 3, 6))
    s.fill(sh, (6, 62, 52, 4))
    return add_outline(s)


def make_jeepney(c1, c2):
    s = _surf(60, 26)
    s.fill(c1, (2, 6, 54, 12)); s.fill(c2, (2, 14, 54, 4)); s.fill(WHITE, (2, 13, 54, 1))
    s.fill(c1, (44, 12, 14, 8)); s.fill(shade(c1, 1.2), (46, 9, 10, 4))
    s.fill(c1, (4, 2, 38, 5)); s.fill(shade(c1, 1.25), (4, 2, 38, 1))
    for x in range(6, 40, 8):
        s.fill((150, 210, 240), (x, 8, 6, 5)); s.fill(WHITE, (x, 8, 1, 2))
    s.fill((150, 210, 240), (48, 10, 7, 3))
    for x in range(4, 42, 4):
        s.fill(YELLOW if (x // 4) % 2 else WHITE, (x, 3, 2, 1))
    s.fill(LTGRAY, (56, 15, 3, 4)); s.fill(YELLOW, (57, 13, 2, 2))
    for x in (12, 46):
        pygame.draw.circle(s, BLACK, (x, 19), 4); pygame.draw.circle(s, LTGRAY, (x, 19), 2)
    for x in range(6, 40, 6):
        s.set_at((x, 16), RED)
    return add_outline(s)


def make_bangka():
    s = _surf(46, 18)
    pygame.draw.polygon(s, (120, 76, 44), [(6, 8), (40, 8), (34, 14), (12, 14)])
    s.fill((170, 116, 66), (6, 7, 34, 2)); s.fill(RED, (12, 10, 22, 1))
    s.fill((170, 130, 80), (12, 3, 2, 5)); s.fill((170, 130, 80), (30, 3, 2, 5))
    s.fill((200, 160, 90), (0, 4, 46, 1))
    s.fill((120, 76, 44), (0, 3, 8, 3)); s.fill((120, 76, 44), (38, 3, 8, 3))
    pygame.draw.polygon(s, WHITE, [(22, 0), (22, 7), (12, 7)]) if False else None
    return add_outline(s)


def make_coconut(h, lean, seed=0, palm=(52, 150, 64)):
    rng = random.Random(seed)
    w = 90 + abs(lean) * 2
    s = _surf(w, h + 30)
    bx = w // 2 - lean // 2
    pts = []
    for y in range(h):
        t = y / h
        x = bx + lean * (t ** 1.8)
        pts.append((int(x), h + 29 - y))
    for i, (x, y) in enumerate(pts):
        tw = 4 if i < h * 0.6 else 3
        c = (150, 108, 66) if (i // 5) % 2 == 0 else (124, 86, 52)
        s.fill(c, (x - tw // 2, y, tw, 1)); s.fill((90, 60, 40), (x + tw // 2, y, 1, 1))
    cx, cy = pts[-1]
    for k in range(9):
        a = math.pi * (0.1 + 0.8 * k / 8) + math.pi
        a = math.pi + (k - 4) * 0.42
        length = rng.randint(22, 32)
        px, py = cx, cy
        for st in range(1, length):
            u = st / length
            px = cx + math.cos(a) * st * 1.05
            py = cy + math.sin(a) * st * 0.42 * (1 - u) * -1 + (u * u) * 16
            c = palm if st % 3 else shade(palm, 0.7)
            s.fill(c, (int(px), int(py), 2, 2))
            if st % 3 == 0:
                s.fill(shade(palm, 1.2), (int(px), int(py) - 1, 1, 1))
                s.fill(shade(palm, 0.8), (int(px) + (1 if math.cos(a) > 0 else -1), int(py) + 2, 1, 2))
    for dx in (-3, 3, 0):
        pygame.draw.circle(s, (100, 70, 40), (cx + dx, cy + 3), 2)
    return add_outline(s)


def make_pine(h, seed=0):
    rng = random.Random(seed)
    s = _surf(46, h + 6)
    cx = 23
    s.fill((100, 66, 44), (cx - 2, h - 26, 4, 30))
    layers = max(4, h // 16)
    for i in range(layers):
        y = 4 + i * (h - 30) // layers
        wdt = 6 + i * 26 // layers + 4
        col = (30, 100 + rng.randint(0, 24), 62)
        pygame.draw.polygon(s, col, [(cx, y), (cx - wdt, y + 18), (cx + wdt, y + 18)])
        pygame.draw.polygon(s, shade(col, 1.25), [(cx, y), (cx - wdt, y + 18), (cx - wdt // 3, y + 18)])
    return add_outline(s)


def make_banana(seed=0):
    s = _surf(32, 30)
    s.fill((110, 150, 60), (15, 12, 3, 18))
    for a in (-1.2, -0.6, 0, 0.6, 1.2):
        for st in range(1, 13):
            x = 16 + math.sin(a) * st * 1.2
            y = 12 - math.cos(a) * st * 0.6 + st * st * 0.05
            s.fill((60, 160, 60) if st % 3 else (40, 120, 50), (int(x), int(y), 3, 2))
    s.fill(YELLOW, (14, 14, 4, 4)); s.fill(GOLD, (14, 17, 4, 1))
    return add_outline(s)


def make_bush(c=(58, 140, 66), w=28):
    s = _surf(w, 16)
    for i in range(3):
        pygame.draw.circle(s, shade(c, 0.8), (6 + i * (w - 12) // 2, 10), 6)
    for i in range(3):
        pygame.draw.circle(s, c, (6 + i * (w - 12) // 2, 8), 5)
    for i in range(6):
        s.set_at((random.Random(i).randint(3, w - 4), random.Random(i + 9).randint(4, 12)), (255, 90, 120))
    return add_outline(s)


def make_stage(w, title, grand=False):
    """The fiesta stage with a banner, lights and bamboo columns."""
    h = 46 if not grand else 56
    s = _surf(w, h)
    s.fill((150, 100, 60), (0, h - 12, w, 12)); s.fill((190, 140, 84), (0, h - 12, w, 2))
    for x in range(2, w, 8):
        s.fill(shade((150, 100, 60), 0.7), (x, h - 10, 1, 10))
    for x in range(0, w, 6):
        s.fill(RED if (x // 6) % 2 == 0 else YELLOW, (x, h - 4, 6, 3))
    s.fill((60, 40, 80), (4, 12, w - 8, h - 24))
    for x in range(6, w - 6, 6):
        s.fill((80, 56, 110), (x, 12, 3, h - 24))
    s.fill(RED, (2, 6, w - 4, 8))
    for x in range(2, w - 4, 5):
        s.fill(YELLOW, (x, 14, 3, 2)); s.fill(BLUE, (x + 2, 14, 2, 1))
    draw_text(s, title, w // 2, 7, CREAM, 1, shadow=DKRED, align="center")
    for x in (0, w - 3):
        s.fill((120, 176, 64), (x, 2, 3, h - 10)); s.fill((80, 130, 50), (x + 2, 2, 1, h - 10))
        for y in (10, 22, 34):
            s.fill((60, 100, 40), (x, y, 3, 1))
    for x in range(6, w - 6, 8):
        s.fill(YELLOW, (x, 3, 2, 2)); s.set_at((x, 2), WHITE)
    if grand:
        for x in (6, w - 14):
            s.fill(DKGRAY, (x, h - 26, 8, 14)); s.fill(GRAY, (x + 2, h - 24, 4, 4)); s.fill(GRAY, (x + 2, h - 18, 4, 4))
    return add_outline(s)


def make_volcano(w=150, h=112):
    s = _surf(w, h)
    cx = w // 2
    for y in range(h):
        t = y / h
        half = 4 + (w // 2 - 4) * (t ** 1.6)
        col = (92, 92, 130) if t < 0.72 else (72, 120, 100)
        if t < 0.72 and int(t * 40) % 5 == 0:
            col = (78, 78, 112)
        s.fill(col, (int(cx - half), y, int(half * 2), 1))
        s.fill(shade(col, 1.2), (int(cx - half), y, max(1, int(half * 0.35)), 1))
    return s


def make_ridge(w, hh, col, seed, amp=40, base=0.5, rounded=False):
    rng = random.Random(seed)
    s = _surf(w, hh + 120)
    pts = []
    f1, f2, f3 = rng.uniform(0.02, 0.04), rng.uniform(0.05, 0.09), rng.uniform(0.11, 0.2)
    p1, p2, p3 = rng.uniform(0, 6), rng.uniform(0, 6), rng.uniform(0, 6)
    for x in range(w):
        v = math.sin(x * f1 + p1) * 0.55 + math.sin(x * f2 + p2) * 0.3 + math.sin(x * f3 + p3) * 0.15
        if not rounded:
            v = 1 - abs(v)
        y = int(hh * (1 - base) - v * amp * 0.5 + amp * 0.3)
        s.fill(col, (x, y, 1, hh + 120 - y))
        s.fill(shade(col, 1.18), (x, y, 1, 2))
        if x % 3 == 0 and not rounded:
            s.fill(shade(col, 0.88), (x, y + 6, 1, 8))
    return s


def make_spectator(seed, cheer, pal):
    rng = random.Random(seed)
    s = _surf(10, 17)
    skin = rng.choice([(222, 160, 104), (190, 126, 76), (238, 188, 130), (176, 112, 70)])
    shirt = rng.choice(pal)
    hair = rng.choice([(30, 22, 30), (50, 32, 24), (20, 16, 24), (80, 60, 50)])
    kid = rng.random() < 0.25
    top = 4 if kid else 2
    s.fill(shirt, (2, top + 6, 6, 8 if not kid else 6)); s.fill(shade(shirt, 0.8), (7, top + 6, 1, 8))
    pants = rng.choice([(50, 50, 90), (90, 70, 50), (60, 60, 70)])
    s.fill(pants, (2, top + 12 if not kid else top + 11, 6, 17))
    s.fill(skin, (2, top, 6, 6)); s.fill(hair, (2, top, 6, 2))
    s.set_at((3, top + 3), EYE_C); s.set_at((6, top + 3), EYE_C)
    if cheer:
        s.fill(skin, (0, top - 2, 2, 5)); s.fill(skin, (8, top - 2, 2, 5))
        s.fill(shirt, (0, top + 3, 2, 3)); s.fill(shirt, (8, top + 3, 2, 3))
        s.set_at((4, top + 4), MOUTH_C); s.set_at((5, top + 4), MOUTH_C)
        if rng.random() < 0.4:
            fc = rng.choice(FIESTA_COLORS)
            s.fill(fc, (8, top - 5, 2, 3)); s.fill(fc, (9, top - 3, 1, 1))
    else:
        s.fill(skin, (0, top + 6, 2, 4)); s.fill(skin, (8, top + 6, 2, 4))
        s.fill(shirt, (0, top + 6, 2, 2)); s.fill(shirt, (8, top + 6, 2, 2))
        s.set_at((4, top + 4), MOUTH_C); s.set_at((5, top + 4), MOUTH_C)
    if rng.random() < 0.3:
        c = STRAW
        s.fill(c, (1, top - 1, 8, 1)); s.fill(shade(c, 0.85), (3, top - 2, 4, 1))
    return add_outline(s)


EYE_C = (30, 20, 34)
MOUTH_C = (120, 40, 50)


# ------------------------------------------------------------------ background --
class Background:
    def __init__(self, stage_id, sky="stage"):
        self.stage_id = stage_id
        self.look = dict(LOOKS[stage_id])
        self.theme = THEMES.get(sky)
        if self.theme:
            self.look["sky"] = self.theme["sky"]
        self.rng = random.Random(stage_id * 131 + 5)
        self.t = 0.0
        self.night = bool(self.theme and self.theme.get("stars")) or stage_id == 5
        self.fx = Particles(random.Random(stage_id))
        self.fw_timer = 0.5
        self.excite = 0.0
        self._build()

    # -- building --------------------------------------------------------------------
    def _tint(self, surf):
        if self.theme:
            surf.fill(self.theme["tint"] + (255,), special_flags=pygame.BLEND_RGB_MULT)
        elif self.stage_id == 5:
            surf.fill((190, 180, 225, 255), special_flags=pygame.BLEND_RGB_MULT)
        return surf

    def _build(self):
        sid, L, rng = self.stage_id, self.look, self.rng
        self.sky = band_gradient(W, SKY_H, L["sky"], band=7)
        if self.night:
            r = random.Random(11)
            for _ in range(70):
                x, y = r.randint(0, W - 1), r.randint(0, SKY_H - 120)
                self.sky.set_at((x, y), WHITE if r.random() < 0.6 else (255, 236, 160))
                if r.random() < 0.15:
                    self.sky.set_at((x + 1, y), (200, 200, 255))
        # ---- far layer -----------------------------------------------------------------
        far = _surf(W, FAR_A + 80)
        far_cols = [mix(c, L["sky"][-1][1], 0.15) for c in L["far"]]
        if self.theme:
            far_cols = [shade(c, 0.7 if self.night else 1.0) for c in far_cols]
        if sid == 4:
            far.blit(make_ridge(W, 110, far_cols[0], 4, 50, 0.6), (0, FAR_A - 118))
            far.blit(make_volcano(), (206, FAR_A - 112 + 4))
            far.blit(make_ridge(W, 70, far_cols[1], 9, 26, 0.5, rounded=True), (0, FAR_A - 70))
        elif sid == 3:
            far.fill((60, 140, 200), (0, FAR_A - 46, W, 130))
            for i in range(8):
                far.fill(mix((60, 140, 200), (40, 100, 170), i / 8), (0, FAR_A - 46 + i * 5, W, 5))
            far.fill((255, 230, 190), (0, FAR_A - 46, W, 1))
            far.blit(make_ridge(120, 40, far_cols[1], 21, 20, 0.5, rounded=True), (-10, FAR_A - 46 - 34))
            far.blit(make_ridge(140, 36, far_cols[0], 22, 18, 0.5, rounded=True), (260, FAR_A - 46 - 30))
        else:
            far.blit(make_ridge(W, 100, far_cols[0], sid * 3, 44, 0.55), (0, FAR_A - 100))
            far.blit(make_ridge(W, 66, far_cols[1], sid * 3 + 1, 28, 0.5, rounded=True), (0, FAR_A - 60))
        self.far = self._tint(far)
        # ---- mid layer --------------------------------------------------------------------
        mid = _surf(W, MID_A + 70)
        gy = MID_A
        hill = shade(L["grass"], 0.85)
        mid.fill(hill, (0, gy - 2, W, 80))
        pal = [RED, BLUE, YELLOW, GREEN, ORANGE, PINK, WHITE, TEAL]
        if sid == 1:
            mid.blit(make_kubo(0), (20, gy - 42)); mid.blit(make_kubo(1), (322, gy - 42))
            mid.blit(make_banana(1), (78, gy - 26)); mid.blit(make_banana(2), (286, gy - 26))
            mid.blit(make_stage(112, "VIVA! PISTA!"), (136, gy - 48))
        elif sid == 2:
            mid.blit(make_church(), (8, gy - 64))
            mid.blit(make_kubo(1), (326, gy - 42))
            mid.blit(make_bush(), (84, gy - 14)); mid.blit(make_bush((70, 150, 60)), (290, gy - 14))
            mid.blit(make_stage(104, "PISTA NG BAYAN"), (140, gy - 48))
        elif sid == 3:
            mid.fill(L["grass"], (0, gy - 2, W, 80))
            mid.blit(make_kubo(0), (10, gy - 42)); mid.blit(make_kubo(1), (330, gy - 42))
            mid.blit(make_stage(112, "PISTA SA BAYBAY"), (136, gy - 48))
        elif sid == 4:
            for i, x in enumerate((6, 44, 322, 356)):
                mid.blit(make_pine(60 + (i % 2) * 14, i), (x - 12, gy - 62 - (i % 2) * 14))
            mid.blit(make_kubo(1), (72, gy - 42)); mid.blit(make_kubo(0), (270, gy - 42))
            mid.blit(make_stage(104, "PISTA SA BUNDOK"), (140, gy - 48))
        else:
            mid.blit(make_kubo(0), (8, gy - 42)); mid.blit(make_kubo(1), (328, gy - 42))
            mid.blit(make_stage(150, "GRAND FIESTA!", True), (117, gy - 58))
        self.mid = self._tint(mid)
        # ---- near layer -----------------------------------------------------------------------
        near = _surf(W, NEAR_A + BELOW)
        gy = NEAR_A
        near.fill(L["grass"], (0, gy, W, BELOW))
        r = random.Random(sid)
        for _ in range(240):
            x, y = r.randint(0, W - 1), r.randint(gy + 1, gy + BELOW - 1)
            near.set_at((x, y), shade(L["grass"], r.choice((0.85, 1.15))))
        px0, px1 = (40, W - 40) if sid != 3 else (0, W)
        near.fill(L["plaza"], (px0, gy, px1 - px0, BELOW))
        for _ in range(140):
            x, y = r.randint(px0, px1 - 1), r.randint(gy + 1, gy + BELOW - 1)
            near.set_at((x, y), shade(L["plaza"], r.choice((0.88, 1.1))))
        if sid == 2:
            for x in range(px0, px1, 16):
                for y in range(gy + 2, gy + BELOW, 8):
                    near.fill(shade(L["plaza"], 0.9), (x + ((y // 8) % 2) * 8, y, 8, 1))
        near.fill(shade(L["plaza"], 0.7), (px0, gy, px1 - px0, 1))
        near.fill(shade(L["grass"], 0.6), (0, gy, px0, 1)); near.fill(shade(L["grass"], 0.6), (px1, gy, W - px1, 1))
        # bamboo fence, stalls and props
        for x0, x1 in ((0, 46), (W - 46, W)):
            for x in range(x0, x1, 4):
                near.fill((176, 150, 70), (x, gy - 14, 3, 15)); near.fill((120, 100, 50), (x + 2, gy - 14, 1, 15))
                near.fill((236, 210, 120), (x, gy - 15, 3, 1))
            near.fill((140, 110, 50), (x0, gy - 10, x1 - x0, 2)); near.fill((140, 110, 50), (x0, gy - 4, x1 - x0, 2))
        stall_cols = [(RED, WHITE), (BLUE, YELLOW), (GREEN, WHITE), (ORANGE, YELLOW)]
        if sid == 2:
            near.blit(make_jeepney(RED, BLUE), (292, gy - 22))
            near.blit(make_stall(*stall_cols[1]), (52, gy - 27))
        elif sid == 3:
            near.blit(make_stall(*stall_cols[2]), (54, gy - 27)); near.blit(make_stall(*stall_cols[0]), (300, gy - 27))
        elif sid == 5:
            near.blit(make_stall(*stall_cols[3]), (52, gy - 27)); near.blit(make_stall(*stall_cols[1]), (302, gy - 27))
            near.blit(make_jeepney(YELLOW, RED), (166, gy - 4)) if False else None
        else:
            near.blit(make_stall(*stall_cols[0]), (54, gy - 27)); near.blit(make_stall(*stall_cols[1]), (300, gy - 27))
        self.near = self._tint(near)
        # ---- tall trees -------------------------------------------------------------------------
        if sid == 4:
            self.trees = [(4, make_pine(300, 1)), (W - 42, make_pine(340, 2))]
            self.trees = [(x, self._tint(t)) for x, t in self.trees]
        else:
            self.trees = [(-22, self._tint(make_coconut(330, 24, 3))), (W - 68, self._tint(make_coconut(380, -22, 4)))]
        # ---- clouds -----------------------------------------------------------------------------
        cc, cs = (WHITE, (206, 226, 246))
        if self.night:
            cc, cs = (96, 92, 150), (70, 66, 120)
        elif sid in (3, 5):
            cc, cs = ((255, 214, 190), (240, 160, 150))
        self.clouds = []
        for i in range(11):
            w = rng.randint(40, 84)
            self.clouds.append(dict(s=make_cloud(w, w // 3 + 6, cc, cs, i), x=rng.uniform(0, W), hgt=rng.randint(30, 560),
                                    v=rng.uniform(2, 7), p=rng.uniform(0.35, 0.6)))
        # ---- crowd -------------------------------------------------------------------------------
        pal = [RED, BLUE, YELLOW, GREEN, ORANGE, PINK, WHITE, TEAL, PURPLE]
        n = catalog.STAGES[sid - 1]["crowd"]
        self.crowd = []
        for i in range(n):
            row = i % 3 if sid == 5 else i % 2
            x = rng.randint(6, W - 12)
            while abs(x - POLE_X_LEFT) < 12 or abs(x - POLE_X_RIGHT) < 12 or abs(x - POLE_X_CENTER) < 12:
                x = rng.randint(6, W - 12)
            self.crowd.append(dict(x=x, row=row, phase=rng.uniform(0, 6.28), a=make_spectator(i, False, pal),
                                   b=make_spectator(i, True, pal)))
        self.crowd.sort(key=lambda c: c["row"])
        if self.night or self.theme:
            for c in self.crowd:
                c["a"] = self._tint(c["a"].copy()); c["b"] = self._tint(c["b"].copy())
        self.smoke = []
        self._bangka = self._tint(make_bangka())

    # -- animation ----------------------------------------------------------------------------------
    def update(self, dt, excite=0.0):
        self.t += dt
        self.excite = excite
        for c in self.clouds:
            c["x"] += c["v"] * dt
            if c["x"] > W + 10:
                c["x"] = -c["s"].get_width() - 10
        if self.stage_id == 5 or (self.theme and self.theme.get("stars") and self.stage_id != 4):
            self.fw_timer -= dt
            if self.fw_timer <= 0:
                self.fx.rocket(self.rng.randint(60, W - 60), self.rng.randint(24, 96))
                self.fw_timer = self.rng.uniform(0.9, 2.0)
        self.fx.update(dt)

    def draw(self, surf, cam, t=None):
        cam = int(cam)
        t = self.t if t is None else t
        sid = self.stage_id
        surf.blit(self.sky, (0, H - SKY_H + int(cam * 0.35)))
        # sun / moon
        sy_ = GROUND_Y - 90 + int(cam * 0.3)
        if self.night and sy_ < H + 30:
            my_ = GROUND_Y - 100 + int(cam * 0.3)
            pygame.draw.circle(surf, (250, 246, 210), (300, my_), 9)
            pygame.draw.circle(surf, (222, 218, 180), (303, my_ + 2), 3)
            pygame.draw.circle(surf, (222, 218, 180), (297, my_ - 3), 2)
        elif self.look.get("sun") and not self.night:
            sx, syy = (210, GROUND_Y - 72 + int(cam * 0.25)) if sid == 3 else (312, GROUND_Y - 100 + int(cam * 0.3))
            r = 14 if sid == 3 else 9
            if syy < H + 30:
                col = (255, 236, 160) if sid != 3 else (255, 244, 190)
                for k, a in enumerate((0.25, 0.12)):
                    pygame.draw.circle(surf, mix(col, (255, 255, 255), 0.2), (sx, syy), r + 5 + k * 4, 1)
                pygame.draw.circle(surf, col, (sx, syy), r)
                pygame.draw.circle(surf, (255, 252, 226), (sx - 2, syy - 2), r // 2)
        if sid == 5 or (self.theme and self.theme.get("stars")):
            self.fx.draw(surf)
        # clouds
        for c in self.clouds:
            y = GROUND_Y - c["hgt"] + int(cam * c["p"])
            if -30 < y < H:
                surf.blit(c["s"], (int(c["x"]), y))
        # far layer
        fy = GROUND_Y - FAR_A + int(cam * 0.2)
        if fy < H:
            surf.blit(self.far, (0, fy))
            if sid == 3:
                sea_y = fy + FAR_A - 46
                for i in range(16):
                    x = int((i * 27 + t * 9) % (W + 20)) - 10
                    y = sea_y + 6 + (i * 11) % 38
                    surf.fill((200, 236, 250), (x, y, 5, 1))
                    surf.fill((200, 236, 250), (x + 2, y + 1, 3, 1))
            if sid == 4:
                for i in range(5):
                    a = (t * 0.6 + i * 0.5) % 2.5
                    px = 281 + int(math.sin(t + i) * 3 + a * 3)
                    py = fy + FAR_A - 112 + 4 - int(a * 10)
                    r = 3 + int(a * 2)
                    pygame.draw.circle(surf, (236, 236, 244), (px, py), r)
        if sid == 3 and fy + FAR_A - 46 < H:
            bx = int((t * 3.0) % (W + 60)) - 50
            surf.blit(self._bangka, (bx, fy + FAR_A - 46 + 12))
        # mid layer
        my = GROUND_Y - MID_A + int(cam * 0.75)
        if my < H:
            surf.blit(self.mid, (0, my))
        # tall trees + banderitas
        for x, tr in self.trees:
            ty = GROUND_Y + cam - (tr.get_height() - 30)
            if ty < H:
                surf.blit(tr, (x, ty))
        self._banderitas(surf, cam, t)
        # near layer
        ny = GROUND_Y - NEAR_A + cam
        if ny < H:
            surf.blit(self.near, (0, ny))

    def draw_crowd(self, surf, cam, t=None):
        cam = int(cam)
        t = self.t if t is None else t
        base = GROUND_Y + cam
        if base > H + 20 or base < -40:
            pass
        exc = max(0.0, min(1.0, self.excite))
        for c in self.crowd:
            y = base + 8 + c["row"] * 11
            if y > H + 4 or y < -20:
                continue
            speed = 3.5 + exc * 6
            up = math.sin(t * speed + c["phase"]) > (0.4 - exc * 1.2)
            spr = c["b"] if (up and exc > 0.05) or (exc <= 0.05 and math.sin(t * 2 + c["phase"]) > 0.85) else c["a"]
            bob = int(abs(math.sin(t * speed + c["phase"])) * (1 + exc * 2))
            surf.blit(spr, (c["x"], y - bob - 2))

    def _banderitas(self, surf, cam, t):
        cols = [RED, YELLOW, BLUE, GREEN, ORANGE, PINK, TEAL, PURPLE]
        for hgt in (60, 200, 340, 480, 610):
            y0 = GROUND_Y - hgt + cam
            if not (-20 < y0 < H + 20):
                continue
            sag = 9
            wob = int(math.sin(t * 1.3 + hgt) * 1)
            pts = []
            for x in range(-4, W + 10, 8):
                u = (x + 4) / (W + 8)
                pts.append((x, y0 + int(4 * sag * u * (1 - u)) - sag // 2 + wob))
            pygame.draw.lines(surf, (70, 52, 44), False, pts, 1)
            for i, x in enumerate(range(6, W, 14)):
                u = (x + 4) / (W + 8)
                y = y0 + int(4 * sag * u * (1 - u)) - sag // 2 + int(math.sin(t * 1.3 + hgt) * 1)
                c = cols[(i + hgt // 60) % len(cols)]
                fl = int(math.sin(t * 5 + i) * 1.2)
                pygame.draw.polygon(surf, c, [(x - 4, y + 1), (x + 4 + fl, y + 1), (x + fl // 2, y + 9)])
                surf.fill(shade(c, 1.25), (x - 3, y + 1, 7, 1))
