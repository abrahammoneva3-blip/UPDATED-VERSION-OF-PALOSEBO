"""Fiesta shop - spend coins on cosmetic unlocks. Nothing here changes gameplay."""
import math
import pygame
import catalog
import sprites
import bamboo as bamboo_mod
from backgrounds import THEMES, LOOKS
from gfx import band_gradient, draw_button, draw_coin, panel, shade
from menu import draw_coins
from pixelfont import draw_text, text_width
from ui import Scene, KEYS_UP, KEYS_DOWN, KEYS_LEFT, KEYS_RIGHT, KEYS_OK
from settings import *

EQUIPPABLE = ("flags", "bamboo", "skies")
COLS, CARD_W, CARD_H, GAPX = 4, 66, 70, 5


class ShopScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.t = 0.0
        self.cat = 0
        self.sel = 0
        self.focus = "cat"
        self.msg = ""
        self.msg_t = 0.0
        self._previews = {}

    # -- helpers --------------------------------------------------------------------
    @property
    def category(self):
        return catalog.CATEGORIES[self.cat]

    def items(self):
        return self.category[2]

    def owned(self, key, item_id):
        return self.app.save.is_unlocked(key, item_id)

    def equipped(self, key, item_id):
        return key in EQUIPPABLE and self.app.save.data["equipped"].get(key) == item_id

    def say(self, text):
        self.msg, self.msg_t = text, 3.0

    def card_rect(self, i):
        c, r = i % COLS, i // COLS
        return pygame.Rect(98 + c * (CARD_W + GAPX), 46 + r * (CARD_H + 6), CARD_W, CARD_H)

    def cat_rect(self, i):
        return pygame.Rect(8, 46 + i * 19, 82, 16)

    # -- actions ----------------------------------------------------------------------
    def activate(self):
        name, key, items = self.category
        it = items[self.sel]
        save = self.app.save
        if self.owned(key, it["id"]):
            if key in EQUIPPABLE:
                save.data["equipped"][key] = it["id"]
                self.sfx("click"); self.say("EQUIPPED: " + it["name"])
                save.save()
            else:
                self.sfx("click"); self.say("YOURS! EQUIP IT IN CHARACTERS")
            return
        if save.coins >= it["price"]:
            save.add_coins(-it["price"])
            save.unlock(key, it["id"])
            self.sfx("coin")
            if key in EQUIPPABLE:
                save.data["equipped"][key] = it["id"]
                self.say("UNLOCKED AND EQUIPPED!")
            else:
                self.say("UNLOCKED! EQUIP IT IN CHARACTERS")
            save.save()
        else:
            self.sfx("error")
            self.say("NOT ENOUGH COINS! NEED %d MORE" % (it["price"] - save.coins))

    def handle_event(self, ev):
        n = len(self.items())
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            if k in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                if self.focus == "items":
                    self.focus = "cat"; self.sfx("back")
                else:
                    self.sfx("back"); self.app.save.save(); self.app.pop()
                return
            if self.focus == "cat":
                if k in KEYS_UP:
                    self.cat = (self.cat - 1) % len(catalog.CATEGORIES); self.sel = 0; self.sfx("move")
                elif k in KEYS_DOWN:
                    self.cat = (self.cat + 1) % len(catalog.CATEGORIES); self.sel = 0; self.sfx("move")
                elif k in KEYS_RIGHT or k in KEYS_OK:
                    self.focus = "items"; self.sel = 0; self.sfx("click")
            else:
                if k in KEYS_LEFT:
                    if self.sel % COLS == 0:
                        self.focus = "cat"
                    else:
                        self.sel -= 1
                    self.sfx("move")
                elif k in KEYS_RIGHT:
                    self.sel = min(n - 1, self.sel + 1) if self.sel % COLS < COLS - 1 else self.sel; self.sfx("move")
                elif k in KEYS_UP:
                    self.sel = max(0, self.sel - COLS) ; self.sfx("move")
                elif k in KEYS_DOWN:
                    self.sel = min(n - 1, self.sel + COLS); self.sfx("move")
                elif k in KEYS_OK:
                    self.activate()
        elif ev.type == pygame.MOUSEMOTION:
            for i in range(len(catalog.CATEGORIES)):
                if self.cat_rect(i).collidepoint(ev.pos) and (i != self.cat):
                    self.cat, self.sel, self.focus = i, 0, "cat"
            if self.focus == "items" or True:
                for i in range(n):
                    if self.card_rect(i).collidepoint(ev.pos) and (self.focus != "items" or i != self.sel):
                        self.focus, self.sel = "items", i
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if pygame.Rect(W - 76, 196, 68, 15).collidepoint(ev.pos):
                self.sfx("back"); self.app.save.save(); self.app.pop(); return
            for i in range(len(catalog.CATEGORIES)):
                if self.cat_rect(i).collidepoint(ev.pos):
                    self.cat, self.sel, self.focus = i, 0, "cat"; self.sfx("click")
            for i in range(n):
                if self.card_rect(i).collidepoint(ev.pos):
                    self.focus, self.sel = "items", i
                    self.activate()

    def update(self, dt):
        self.t += dt
        if self.msg_t > 0:
            self.msg_t -= dt

    # -- drawing ------------------------------------------------------------------------
    def _preview(self, surf, key, it, r):
        cx = r.x + r.w // 2
        top = r.y + 3
        area_h = 36
        if key in ("characters", "hats", "outfits", "accessories"):
            lo = dict(character="kid", hat="none", outfit="default", accessory="none")
            if key == "characters":
                lo = dict(character=it["id"], hat="default", outfit="default", accessory="default")
            elif key == "hats":
                lo["hat"] = it["id"]
            elif key == "outfits":
                lo["character"] = "student"; lo["outfit"] = it["id"]
            else:
                lo["accessory"] = it["id"]
            spr = sprites.get_sprite(lo, "idle", int(self.t * 2) % 2, 0)
            big = pygame.transform.scale(spr, (spr.get_width() * 2, spr.get_height() * 2))
            off = 0 if key in ("characters", "hats") else 8
            surf.fill((70, 120, 170), (r.x + 3, top, r.w - 6, area_h))
            surf.blit(big, (cx - big.get_width() // 2, top), (0, off, big.get_width(), area_h))
        elif key == "flags":
            surf.fill((70, 120, 170), (r.x + 3, top, r.w - 6, area_h))
            tex = bamboo_mod.flag_texture(it["id"])
            big = pygame.transform.scale(tex, (tex.get_width() * 2, tex.get_height() * 2))
            surf.blit(big, (cx - big.get_width() // 2 + 2, top + 4 + int(math.sin(self.t * 4) * 1)))
            surf.fill(BROWN, (cx - big.get_width() // 2 - 2, top + 2, 2, 32))
        elif key == "bamboo":
            surf.fill((70, 120, 170), (r.x + 3, top, r.w - 6, area_h))
            tile = bamboo_mod._pole_tile(it["id"])
            big = pygame.transform.scale(tile, (tile.get_width() * 2, tile.get_height() * 2))
            surf.blit(big, (cx - big.get_width() // 2, top), (0, 0, big.get_width(), area_h))
        else:
            k = ("s", it["id"])
            if k not in self._previews:
                if it["id"] == "stage":
                    stops = LOOKS[1]["sky"]
                else:
                    stops = THEMES[it["id"]]["sky"]
                g = band_gradient(r.w - 6, area_h, stops, band=5)
                if it["id"] == "night":
                    for sx, sy_ in ((6, 5), (20, 12), (34, 4), (46, 16), (12, 22), (52, 8)):
                        g.set_at((sx, sy_), WHITE)
                self._previews[k] = g
            surf.blit(self._previews[k], (r.x + 3, top))

    def draw(self, surf):
        surf.fill((30, 24, 70))
        for y in range(0, H, 8):
            surf.fill((36, 30, 82), (0, y, W, 4))
        draw_text(surf, "FIESTA SHOP", W // 2, 8, YELLOW, 2, shadow=OUTLINE, outline=OUTLINE, align="center")
        draw_text(surf, "TINDAHAN - COSMETICS ONLY, NO GAMEPLAY BOOSTS", W // 2, 27, LTGRAY, 1, shadow=OUTLINE, align="center")
        name, key, items = self.category
        # categories
        for i, (cn, ck, ci) in enumerate(catalog.CATEGORIES):
            r = self.cat_rect(i)
            sel = i == self.cat
            draw_button(surf, (r.x, r.y, r.w, r.h), cn, selected=sel and self.focus == "cat",
                        base=(70, 64, 140) if not sel else (200, 90, 60))
        # cards
        for i, it in enumerate(items):
            r = self.card_rect(i)
            sel = self.focus == "items" and i == self.sel
            own = self.owned(key, it["id"])
            eq = self.equipped(key, it["id"])
            panel(surf, (r.x, r.y - (2 if sel else 0), r.w, r.h), (200, 90, 60) if sel else (52, 46, 110), OUTLINE)
            self._preview(surf, key, it, pygame.Rect(r.x, r.y - (2 if sel else 0), r.w, r.h))
            words = it["name"].split(" ")
            lines = [" ".join(words[:1]), " ".join(words[1:])] if len(words) > 1 and text_width(it["name"]) > r.w - 6 else [it["name"]]
            ny = r.y + 41 - (2 if sel else 0)
            for j, ln in enumerate(lines):
                draw_text(surf, ln, r.x + r.w // 2, ny + j * 8, WHITE, 1, shadow=OUTLINE, align="center")
            py = r.y + r.h - 11 - (2 if sel else 0)
            if eq:
                draw_text(surf, "EQUIPPED", r.x + r.w // 2, py, LIME, 1, shadow=OUTLINE, align="center")
            elif own:
                draw_text(surf, "OWNED", r.x + r.w // 2, py, CREAM, 1, shadow=OUTLINE, align="center")
            else:
                afford = self.app.save.coins >= it["price"]
                s = str(it["price"])
                w = text_width(s) + 10
                draw_coin(surf, r.x + r.w // 2 - w // 2 + 3, py + 3, self.t, spin=False)
                draw_text(surf, s, r.x + r.w // 2 - w // 2 + 10, py, YELLOW if afford else (255, 120, 120), 1, shadow=OUTLINE)
            if not own:
                surf.fill(OUTLINE, (r.right - 12, r.y + 3, 9, 9)); surf.fill(GOLD, (r.right - 11, r.y + 6, 7, 5))
                surf.fill(OUTLINE, (r.right - 10, r.y + 3, 1, 3)); surf.fill(OUTLINE, (r.right - 6, r.y + 3, 1, 3))
        # footer
        if self.msg_t > 0:
            draw_text(surf, self.msg, W // 2 - 30, 200, ORANGE if int(self.t * 5) % 2 else YELLOW, 1, shadow=OUTLINE, align="center")
        else:
            draw_text(surf, "ARROWS = MOVE   ENTER = BUY / EQUIP   ESC = BACK", W // 2 - 30, 200, LTGRAY, 1, align="center")
        draw_button(surf, (W - 76, 196, 68, 15), "BACK")
        draw_coins(surf, self.app.save.coins, t=self.t)
