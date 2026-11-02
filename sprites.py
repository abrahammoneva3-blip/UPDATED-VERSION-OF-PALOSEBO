"""Procedural pixel-art character sprites.

Every character is drawn pixel-by-pixel on a 16x26 canvas (18x28 with outline)
in several poses: idle, climb (4 frames), tired, slip, win, lose.  Results are
cached, so drawing during the game is just a blit.
"""
import pygame
import catalog
from gfx import add_outline, shade
from settings import *

CANVAS_W, CANVAS_H = 16, 26
SPRITE_W, SPRITE_H = CANVAS_W + 2, CANVAS_H + 2
FEET_ANCHOR = SPRITE_H - 2      # y inside the outlined sprite that sits on the pole position
CENTER_X = 9                    # x inside the outlined sprite that matches the pole centre

HY, TY = 6, 12                  # head top / torso top rows
EYE = (30, 20, 34)
MOUTH = (110, 40, 50)

# pose table: dy = body bob, la/ra = y of hand top (left/right arm), ll/rl = leg state
POSES = {
    ("idle", 0): dict(dy=0, la=5, ra=5, ll=0, rl=0, eyes="n", mouth="smile"),
    ("idle", 1): dict(dy=1, la=6, ra=6, ll=0, rl=0, eyes="n", mouth="smile"),
    ("climb", 0): dict(dy=0, la=2, ra=8, ll=1, rl=0, eyes="n", mouth="flat"),
    ("climb", 1): dict(dy=1, la=5, ra=6, ll=0, rl=0, eyes="n", mouth="flat"),
    ("climb", 2): dict(dy=0, la=8, ra=2, ll=0, rl=1, eyes="n", mouth="flat"),
    ("climb", 3): dict(dy=1, la=6, ra=5, ll=0, rl=0, eyes="n", mouth="flat"),
    ("tired", 0): dict(dy=2, la=7, ra=7, ll=0, rl=0, eyes="n", mouth="open", sweat=0),
    ("tired", 1): dict(dy=3, la=8, ra=8, ll=0, rl=0, eyes="n", mouth="open", sweat=1),
    ("slip", 0): dict(dy=-1, la=1, ra=3, ll=2, rl=0, eyes="wide", mouth="open", flail=True),
    ("slip", 1): dict(dy=0, la=3, ra=1, ll=0, rl=2, eyes="wide", mouth="open", flail=True),
    ("win", 0): dict(dy=0, la=0, ra=0, ll=0, rl=0, eyes="happy", mouth="grin", cheer=True),
    ("win", 1): dict(dy=-2, la=1, ra=1, ll=3, rl=3, eyes="happy", mouth="grin", cheer=True),
    ("lose", 0): dict(dy=3, la=14, ra=14, ll=0, rl=0, eyes="n", mouth="sad", sweat=0, droop=True),
    ("lose", 1): dict(dy=4, la=14, ra=14, ll=0, rl=0, eyes="n", mouth="sad", sweat=1, droop=True),
}

_cache = {}


def resolve(loadout):
    """Turn a loadout dict into a full design dict (colours + styles)."""
    ch = catalog.by_id(catalog.CHARACTERS, loadout.get("character", "kid"))
    d = dict(ch)
    hat_id = loadout.get("hat", "default")
    d["hat_item"] = catalog.by_id(catalog.HATS, ch["hat"] if hat_id == "default" else hat_id)
    of = loadout.get("outfit", "default")
    if of != "default":
        o = catalog.by_id(catalog.OUTFITS, of)
        d["shirt"], d["shirt2"] = o["shirt"], o["shirt2"]
        if o.get("style"):
            d["shirt_style"] = o["style"]
    acc = loadout.get("accessory", "default")
    d["acc"] = ch["acc"] if acc == "default" else acc
    return d


def _rect(s, x, y, w, h, c):
    s.fill(c, (x, y, w, h))


def _draw_hat(s, hat, hy, hx):
    kind = hat["kind"]
    c = hat.get("color", RED)
    if kind == "none":
        return
    dk, lt = shade(c, 0.72), shade(c, 1.2)
    if kind == "salakot":
        _rect(s, 7 + hx, hy - 4, 2, 1, dk)
        _rect(s, 6 + hx, hy - 3, 4, 1, c)
        _rect(s, 5 + hx, hy - 2, 6, 1, lt)
        _rect(s, 4 + hx, hy - 1, 8, 1, c)
        _rect(s, 2 + hx, hy, 12, 1, dk)
        _rect(s, 3 + hx, hy - 1, 1, 1, dk)
        for x in (6, 8, 10):
            _rect(s, x + hx, hy - 2, 1, 1, dk)
        s.set_at((5 + hx, hy + 1), RED)          # tiny chin-strap knots
        s.set_at((10 + hx, hy + 1), RED)
    elif kind == "buri":
        _rect(s, 6 + hx, hy - 3, 4, 1, c)
        _rect(s, 5 + hx, hy - 2, 6, 1, lt)
        _rect(s, 5 + hx, hy - 1, 6, 1, RED)
        _rect(s, 3 + hx, hy, 10, 1, dk)
        _rect(s, 2 + hx, hy + 1, 12, 1, c)
    elif kind == "cap":
        _rect(s, 6 + hx, hy - 1, 4, 1, c)
        _rect(s, 5 + hx, hy, 6, 2, c)
        _rect(s, 6 + hx, hy, 2, 1, lt)
        _rect(s, 4 + hx, hy + 2, 8, 1, dk)
    elif kind == "headband":
        _rect(s, 5 + hx, hy + 1, 6, 1, c)
        _rect(s, 11 + hx, hy + 1, 2, 1, c)
        _rect(s, 12 + hx, hy + 2, 1, 2, dk)
    elif kind == "bandana":
        _rect(s, 5 + hx, hy, 6, 2, c)
        for x in (6, 8, 10):
            s.set_at((x + hx, hy + 1), WHITE)
        _rect(s, 11 + hx, hy + 1, 2, 1, c)
        _rect(s, 12 + hx, hy + 2, 1, 2, dk)
    elif kind == "crown":
        for i, x in enumerate(range(5, 11)):
            s.set_at((x + hx, hy), WHITE if i % 2 == 0 else (110, 190, 90))
        for x in (6, 9):
            s.set_at((x + hx, hy - 1), WHITE)
            s.set_at((x + hx, hy + 1), (110, 190, 90))
        s.set_at((7 + hx, hy - 1), YELLOW)


def _draw_face(s, pose, hy, hx, skin, acc):
    e = pose["eyes"]
    ey = hy + 3
    if e == "wide":
        for x in (6, 9):
            s.set_at((x + hx, ey - 1), WHITE)
            s.set_at((x + hx, ey), EYE)
    elif e == "happy":
        for x in (6, 9):
            s.set_at((x + hx, ey), EYE)
            s.set_at((x + hx - 1 + (x == 9) * 2, ey + 1) if False else (x + hx, ey - 1), shade(skin, 0.6))
    else:
        for x in (6, 9):
            s.set_at((x + hx, ey), EYE)
    m = pose["mouth"]
    my = hy + 5
    if m == "smile":
        s.set_at((7 + hx, my), MOUTH); s.set_at((8 + hx, my), MOUTH)
        s.set_at((6 + hx, my - 1), shade(skin, 0.75)); s.set_at((9 + hx, my - 1), shade(skin, 0.75))
    elif m == "flat":
        s.set_at((7 + hx, my), MOUTH); s.set_at((8 + hx, my), MOUTH)
    elif m == "open":
        _rect(s, 7 + hx, my - 1, 2, 2, MOUTH)
    elif m == "grin":
        _rect(s, 6 + hx, my - 1, 4, 2, MOUTH)
        _rect(s, 7 + hx, my - 1, 2, 1, WHITE)
    elif m == "sad":
        s.set_at((7 + hx, my - 1), MOUTH); s.set_at((8 + hx, my - 1), MOUTH)
        s.set_at((6 + hx, my), MOUTH); s.set_at((9 + hx, my), MOUTH)
    if acc == "shades":
        _rect(s, 5 + hx, ey, 6, 1, (20, 16, 28))
        _rect(s, 5 + hx, ey - 1, 6, 1, (20, 16, 28)) if e == "wide" else None
        s.set_at((6 + hx, ey), (120, 140, 220))
        s.set_at((9 + hx, ey), (120, 140, 220))


def _draw_hair(s, d, hy, hx):
    hair = d["hair"]
    st = d["hair_style"]
    hl = shade(hair, 1.8)
    if st == "spiky":
        for x in (5, 7, 9):
            s.set_at((x + hx, hy - 1), hair)
        _rect(s, 5 + hx, hy, 6, 2, hair)
        s.set_at((6 + hx, hy), hl)
        s.set_at((5 + hx, hy + 2), hair); s.set_at((10 + hx, hy + 2), hair)
    elif st == "side":
        _rect(s, 5 + hx, hy, 6, 2, hair)
        _rect(s, 5 + hx, hy + 2, 2, 1, hair)
        s.set_at((8 + hx, hy), hl); s.set_at((9 + hx, hy), hl)
        s.set_at((10 + hx, hy + 2), hair)
    elif st == "slick":
        _rect(s, 5 + hx, hy, 6, 2, hair)
        _rect(s, 6 + hx, hy, 4, 1, hl)
        s.set_at((5 + hx, hy + 2), hair); s.set_at((10 + hx, hy + 2), hair)
    else:  # short
        _rect(s, 5 + hx, hy, 6, 2, hair)
        s.set_at((5 + hx, hy + 2), hair); s.set_at((10 + hx, hy + 2), hair)
        s.set_at((7 + hx, hy), hl)


def _draw_character(d, pose_name, frame, lean):
    pose = POSES[(pose_name, frame % (4 if pose_name == "climb" else 2))]
    s = pygame.Surface((CANVAS_W, CANVAS_H), pygame.SRCALPHA)
    dy = pose["dy"]
    hx = lean
    tx = int(lean * 0.5)
    skin = d["skin"]
    skin_dk = shade(skin, 0.82)
    shirt, shirt2 = d["shirt"], d["shirt2"]
    style = d["shirt_style"]
    sh_dk, sh_lt = shade(shirt, 0.78), shade(shirt, 1.12)
    pants = d["pants"]
    pa_dk = shade(pants, 0.75)
    ty = TY + dy
    hy = HY + dy
    hip = TY + 8  # 20
    kid = 0

    # ---- legs -----------------------------------------------------------------
    for side, key in ((0, "ll"), (1, "rl")):
        state = pose[key]
        x = 4 if side == 0 else 9
        out = -1 if side == 0 else 1
        if state == 0:
            top, bot = hip - 1, hip + 5
            _rect(s, x, top, 3, bot - top, skin)
            _rect(s, x + (1 if side == 0 else 0), top, 2, bot - top, skin) if False else None
            _rect(s, x + 2 * side, top, 1, bot - top, skin_dk)
            if d["pants_style"] == "long":
                _rect(s, x, top, 3, 5, pants); _rect(s, x + 2 * side, top, 1, 5, pa_dk)
                _rect(s, x, hip + 3, 3, 1, pa_dk)
            else:
                _rect(s, x, top, 3, 3, pants); _rect(s, x + 2 * side, top, 1, 3, pa_dk)
                _rect(s, x, top + 2, 3, 1, pa_dk)
            _rect(s, x + (0 if side == 0 else 0), hip + 4, 3, 2, skin)     # bare foot gripping the bamboo
            _rect(s, x + (2 if side == 0 else 0), hip + 4, 1, 2, skin_dk)
        else:
            # knee raised / kicked out
            spread = state if state > 1 else 1
            kx = x + out * spread
            _rect(s, kx, hip - 1, 3, 3, pants); _rect(s, kx, hip + 1, 3, 1, pa_dk)
            _rect(s, kx, hip + 2, 3, 2, skin)
            _rect(s, kx + out, hip + 3, 3, 2, skin)
            _rect(s, kx + out + (2 if side == 0 else 0), hip + 3, 1, 2, skin_dk)

    # ---- torso ------------------------------------------------------------------
    tx0 = 4 + tx
    tw = 8
    if style == "tank":
        _rect(s, tx0 - 0, ty, 8, 2, skin)
        _rect(s, tx0 + 1, ty, 2, 2, shirt); _rect(s, tx0 + 5, ty, 2, 2, shirt)
        _rect(s, tx0, ty + 2, 8, 6, shirt)
        _rect(s, tx0, ty + 2, 1, 6, sh_lt); _rect(s, tx0 + 7, ty + 2, 1, 6, sh_dk)
    else:
        _rect(s, tx0, ty, tw, 8, shirt)
        _rect(s, tx0, ty, 1, 8, sh_lt); _rect(s, tx0 + 7, ty, 1, 8, sh_dk)
    _rect(s, tx0, ty + 7, tw, 1, sh_dk)
    if style == "polo":
        s.set_at((tx0 + 3, ty), shirt2); s.set_at((tx0 + 4, ty), shirt2)
        s.set_at((tx0 + 2, ty), CREAM); s.set_at((tx0 + 5, ty), CREAM)
        s.set_at((tx0 + 3, ty + 1), CREAM); s.set_at((tx0 + 4, ty + 1), CREAM)
        s.set_at((tx0 + 3, ty + 3), shade(shirt, 0.8)); s.set_at((tx0 + 3, ty + 5), shade(shirt, 0.8))
    elif style == "jersey":
        _rect(s, tx0, ty, 8, 1, shirt2)
        _rect(s, tx0 + 3, ty + 2, 3, 1, shirt2); _rect(s, tx0 + 5, ty + 3, 1, 4, shirt2)   # tiny "7"
        s.set_at((tx0 + 4, ty + 5), shirt2)
        _rect(s, tx0, ty + 7, 8, 1, shirt2)
    elif style == "stripes":
        for r in (1, 3, 5):
            _rect(s, tx0, ty + r, 8, 1, shirt2)
    elif style == "barong":
        _rect(s, tx0 + 3, ty + 1, 2, 7, shade(shirt, 0.88))
        for r in (2, 4, 6):
            s.set_at((tx0 + 3, ty + r), shirt2); s.set_at((tx0 + 4, ty + r), shirt2)
        _rect(s, tx0 + 2, ty, 4, 1, shade(shirt, 0.85))
        s.set_at((tx0 + 1, ty + 5), shirt2); s.set_at((tx0 + 6, ty + 5), shirt2)
    elif style == "tee":
        _rect(s, tx0 + 2, ty, 4, 1, shirt2)
        s.set_at((tx0 + 3, ty + 3), shirt2); s.set_at((tx0 + 4, ty + 3), shirt2)
        s.set_at((tx0 + 3, ty + 4), shirt2); s.set_at((tx0 + 4, ty + 4), shirt2)   # little fiesta dot

    # ---- accessories that sit on the torso -------------------------------------
    acc = d["acc"]
    if acc == "sash":
        for i in range(8):
            y = ty + i
            if 0 <= i < 8:
                s.set_at((tx0 + i, y), RED)
                if y + 1 <= ty + 7:
                    s.set_at((tx0 + i, y + 1), YELLOW if style != "barong" else BLUE)
    elif acc == "lei":
        for i, (x, y) in enumerate([(1, 0), (2, 1), (3, 2), (4, 2), (5, 1), (6, 0)]):
            s.set_at((tx0 + x, ty + y + 1), WHITE if i % 2 == 0 else YELLOW)

    # ---- arms ---------------------------------------------------------------------
    sleeve = style in ("tee", "polo", "jersey", "stripes", "barong")
    long_sleeve = style == "barong"
    for side in (0, 1):
        la = pose["la"] if side == 0 else pose["ra"]
        if pose.get("flail"):
            ax = 0 if side == 0 else 14
            ax += (1 if side == 0 else -1) * (frame % 2) * (1 if la <= 1 else 0)
        elif pose.get("cheer"):
            ax = 1 if side == 0 else 13
        elif pose.get("droop"):
            ax = 2 if side == 0 else 12
        else:
            ax = 2 if side == 0 else 12
        ax += tx if not pose.get("flail") else 0
        top = ty + 0 if pose.get("droop") else la + dy * 0
        shoulder = ty + 1
        if pose.get("droop"):
            top = ty + 2
            _rect(s, ax, top, 2, 6, skin)
            if sleeve:
                _rect(s, ax, top, 2, 3 if not long_sleeve else 5, shirt)
            continue
        h_ = shoulder - la + 1
        if h_ < 3:
            h_ = 3
        _rect(s, ax, la, 2, h_, skin)
        _rect(s, ax + (1 if side == 0 else 0), la, 1, h_, skin_dk)
        if sleeve:
            sl = 3 if not long_sleeve else h_ - 2
            _rect(s, ax, shoulder - sl + 1, 2, sl, shirt)
            if style == "jersey":
                s.set_at((ax, shoulder - sl + 1), shirt2); s.set_at((ax + 1, shoulder - sl + 1), shirt2)
            if long_sleeve:
                _rect(s, ax, la + 2, 2, 1, shirt2)
        _rect(s, ax, la, 2, 2, skin)          # hand
        s.set_at((ax + (0 if side == 0 else 1), la), skin_dk)
        if acc == "wristbands":
            _rect(s, ax, la + 2, 2, 1, RED if not sleeve else YELLOW)

    # ---- head -----------------------------------------------------------------------
    _rect(s, 5 + hx, hy, 6, 6, skin)
    _rect(s, 10 + hx, hy + 2, 1, 4, skin_dk)
    s.set_at((5 + hx, hy + 4), shade(skin, 1.05))
    if d["id"] == "kid":
        s.set_at((5 + hx, hy + 4), (240, 130, 120)); s.set_at((10 + hx, hy + 4), (240, 130, 120))
    _draw_hair(s, d, hy, hx)
    _draw_face(s, pose, hy, hx, skin, acc)
    _draw_hat(s, d["hat_item"], hy, hx)
    if pose.get("sweat") is not None:
        sx = 11 + hx
        if pose["sweat"] == 0:
            s.set_at((sx, hy + 2), (120, 200, 255)); s.set_at((sx, hy + 3), (120, 200, 255))
        else:
            s.set_at((sx + 1, hy + 4), (120, 200, 255)); s.set_at((4 + hx - 1, hy + 1), (120, 200, 255))
    if pose.get("flail"):
        s.set_at((3 + hx, hy - 1), WHITE); s.set_at((12 + hx, hy - 1), WHITE)
    return add_outline(s)


def get_sprite(loadout, pose, frame=0, lean=0):
    """Cached, outlined 18x28 sprite. Pole centre is at x=CENTER_X, feet at y=FEET_ANCHOR."""
    key = (loadout.get("character"), loadout.get("hat"), loadout.get("outfit"), loadout.get("accessory"),
           pose, frame % 4, max(-2, min(2, int(lean))))
    spr = _cache.get(key)
    if spr is None:
        spr = _draw_character(resolve(loadout), pose, frame, max(-2, min(2, int(lean))))
        _cache[key] = spr
    return spr


def draw_character(surf, loadout, x, y, pose="idle", frame=0, lean=0, flip=False):
    """Blit so that (x, y) is the pole-centre / feet position."""
    spr = get_sprite(loadout, pose, frame, lean)
    if flip:
        spr = pygame.transform.flip(spr, True, False)
    surf.blit(spr, (int(x) - CENTER_X, int(y) - FEET_ANCHOR))


def draw_preview(surf, loadout, cx, cy, scale=3, pose="idle", frame=0):
    """Big portrait: (cx, cy) = centre of the drawn image."""
    spr = get_sprite(loadout, pose, frame, 0)
    if scale > 1:
        spr = pygame.transform.scale(spr, (spr.get_width() * scale, spr.get_height() * scale))
    surf.blit(spr, (cx - spr.get_width() // 2, cy - spr.get_height() // 2))
