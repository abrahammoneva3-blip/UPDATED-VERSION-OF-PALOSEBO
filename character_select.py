"""Character + cosmetics screen. Both players edit their look at the same time."""
import math
import pygame
import catalog
import sprites
from gfx import draw_button, panel, shade
from menu import draw_coins
from pixelfont import draw_text, text_width
from ui import Scene
from settings import *

ROWS = [("CHARACTER", "characters", catalog.CHARACTERS, "character"),
        ("HAT", "hats", catalog.HATS, "hat"),
        ("OUTFIT", "outfits", catalog.OUTFITS, "outfit"),
        ("ACCESSORY", "accessories", catalog.ACCESSORIES, "accessory")]

KEYSETS = {
    1: dict(up=pygame.K_w, down=pygame.K_s, left=pygame.K_a, right=pygame.K_d),
    2: dict(up=pygame.K_UP, down=pygame.K_DOWN, left=pygame.K_LEFT, right=pygame.K_RIGHT),
}


class CharacterSelect(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.t = 0.0
        self.row = {1: 0, 2: 0}
        self.done_rect = pygame.Rect(W // 2 - 50, 196, 100, 15)

    def options(self, key, items):
        unlocked = self.app.save.data["unlocked"][key]
        ids = [it["id"] for it in items if it["id"] in unlocked]
        if key != "characters":
            ids = ["default"] + ids
        return ids

    def name_of(self, key, items, item_id):
        if item_id == "default":
            return "DEFAULT"
        return catalog.by_id(items, item_id)["name"]

    def _change(self, player, d):
        lo = self.app.save.loadout(player)
        label, key, items, slot = ROWS[self.row[player]]
        opts = self.options(key, items)
        cur = lo.get(slot, "default")
        i = opts.index(cur) if cur in opts else 0
        lo[slot] = opts[(i + d) % len(opts)]
        self.sfx("move")

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            if k in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_BACKSPACE):
                self.sfx("back" if k != pygame.K_RETURN else "click")
                self.app.save.save()
                self.app.pop()
                return
            for p, km in KEYSETS.items():
                if k == km["up"]:
                    self.row[p] = (self.row[p] - 1) % len(ROWS); self.sfx("move")
                elif k == km["down"]:
                    self.row[p] = (self.row[p] + 1) % len(ROWS); self.sfx("move")
                elif k == km["left"]:
                    self._change(p, -1)
                elif k == km["right"]:
                    self._change(p, 1)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.done_rect.collidepoint(ev.pos):
                self.sfx("click"); self.app.save.save(); self.app.pop()

    def update(self, dt):
        self.t += dt

    def _panel(self, surf, p, x):
        tone = (255, 120, 90) if p == 1 else (110, 190, 255)
        w = 184
        panel(surf, (x, 30, w, 152), (40, 34, 90), OUTLINE)
        surf.fill(tone, (x + 4, 34, 5, 9))
        draw_text(surf, "PLAYER %d" % p, x + 13, 34, tone, 1, shadow=OUTLINE)
        draw_text(surf, "WASD" if p == 1 else "\u2190\u2191\u2192\u2193", x + w - 6, 34, LTGRAY, 1, align="right")
        lo = self.app.save.loadout(p)
        # portrait on a little bamboo stage
        px = x + 34
        panel(surf, (x + 6, 48, 56, 100), (60, 110, 160), OUTLINE)
        surf.fill((90, 150, 90), (x + 7, 128, 54, 19))
        surf.fill((120, 176, 64), (px - 3, 49, 6, 79)); surf.fill((80, 130, 50), (px + 1, 49, 2, 79))
        frame = int(self.t * 2) % 2
        sprites.draw_preview(surf, lo, px, 108, 3, "idle", frame)
        ch = catalog.by_id(catalog.CHARACTERS, lo["character"])
        draw_text(surf, ch["name"], x + 34, 153, YELLOW, 1, shadow=OUTLINE, align="center")
        # rows
        for i, (label, key, items, slot) in enumerate(ROWS):
            ry = 48 + i * 25
            sel = self.row[p] == i
            rx = x + 68
            draw_text(surf, label, rx, ry, LTGRAY if not sel else WHITE, 1)
            r = (rx, ry + 8, 110, 13)
            panel(surf, r, tone if sel else (60, 54, 120), OUTLINE)
            nm = self.name_of(key, items, lo.get(slot, "default"))
            draw_text(surf, nm, rx + 55, ry + 11, WHITE, 1, shadow=OUTLINE, align="center")
            if sel:
                b = 1 if int(self.t * 4) % 2 else 0
                draw_text(surf, "<", rx - 6 - b + 4, ry + 11, YELLOW, 1, shadow=OUTLINE)
                draw_text(surf, ">", rx + 110 - 2 + b, ry + 11, YELLOW, 1, shadow=OUTLINE)
        n_locked = sum(1 for _, key, items, _ in ROWS for it in items if it["id"] not in self.app.save.data["unlocked"][key] and it["price"] > 0)
        draw_text(surf, "%d ITEMS IN SHOP" % n_locked, x + w - 6, 168, LTGRAY, 1, align="right")

    def draw(self, surf):
        surf.fill((30, 24, 70))
        for y in range(0, H, 8):
            surf.fill((36, 30, 82), (0, y, W, 4))
        draw_text(surf, "CHOOSE YOUR CLIMBER", W // 2, 5, YELLOW, 2, shadow=OUTLINE, outline=OUTLINE, align="center")
        draw_text(surf, "ALL CHARACTERS PLAY EXACTLY THE SAME - LOOKS ONLY!", W // 2, 22, LTGRAY, 1, shadow=OUTLINE, align="center")
        self._panel(surf, 2, 8)
        self._panel(surf, 1, W - 8 - 184)
        draw_text(surf, "UP/DOWN = ROW    LEFT/RIGHT = CHANGE", W // 2, 186, LTGRAY, 1, align="center")
        r = self.done_rect
        draw_button(surf, (r.x, r.y, r.w, r.h), "DONE", selected=True)
        draw_coins(surf, self.app.save.coins, t=self.t)
