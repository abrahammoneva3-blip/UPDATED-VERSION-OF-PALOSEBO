"""Main menu, stage select, settings and pause screens."""
import math
import pygame
import catalog
import sprites
from backgrounds import Background
from bamboo import Bamboo, sy
from gfx import draw_button, draw_coin, draw_key, panel, shade, star
from pixelfont import draw_text, text_width
from ui import (ButtonMenu, Scene, KEYS_LEFT, KEYS_RIGHT, KEYS_OK, dim, draw_title)
from settings import *


def draw_coins(surf, coins, x=W - 6, y=5, t=0.0):
    s = "%d" % coins
    w = text_width(s, 1)
    panel(surf, (x - w - 26, y - 3, w + 26, 15), (30, 28, 70), OUTLINE)
    draw_coin(surf, x - w - 15, y + 4, t)
    draw_text(surf, s, x - 5, y, YELLOW, 1, shadow=OUTLINE, align="right")


# ------------------------------------------------------------------------ main --
class MainMenu(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.t = 0.0
        eq = app.save.data["equipped"]
        self.bg = Background(1, eq.get("skies", "stage"))
        self.poles = [Bamboo(38, eq["bamboo"], eq["flags"], 0.0, 3.0), Bamboo(W - 38, eq["bamboo"], eq["flags"], 2.0, 3.0)]
        labels = ["PLAY", "TWO PLAYER", "TIME ATTACK", "CHARACTERS", "SHOP", "SETTINGS", "EXIT"]
        self.menu = ButtonMenu(labels, W // 2 - 109, 92, 106, 17, gap=6, cols=2)
        self.menu.items[-1]["rect"].centerx = W//2

    def enter(self):
        self.app.sound.music_start()
        self.app.sound.stop_loops()

    def handle_event(self, ev):
        i = self.menu.handle_event(ev, self.app.sound)
        if i is None:
            return
        app = self.app
        if i == 0:
            from game import PlayScene
            stage = app.save.data.get("last_stage", 1)
            if not app.save.stage_unlocked(stage):
                stage = 1
            app.goto(PlayScene(app, "bot", stage))
        elif i == 1:
            app.push(StageSelect(app, "two"))
        elif i == 2:
            app.push(StageSelect(app, "time"))
        elif i == 3:
            from character_select import CharacterSelect
            app.push(CharacterSelect(app))
        elif i == 4:
            from shop import ShopScene
            app.push(ShopScene(app))
        elif i == 5:
            app.push(SettingsScene(app))
        elif i == 6:
            app.running = False

    def update(self, dt):
        self.t += dt
        self.bg.update(dt)

    def draw(self, surf):
        t = self.t
        self.bg.draw(surf, 0, t)
        env = None
        for p in self.poles:
            p.prepare(t, None)
            p.draw(surf, 0, t)
        # two demo climbers
        for i, p in enumerate(self.poles):
            h = 50 + 46 * (0.5 + 0.5 * math.sin(t * 0.7 + i * 2.2))
            moving = math.cos(t * 0.7 + i * 2.2) * (1 if True else 0)
            pose = "climb" if moving > 0.15 else "idle"
            frame = int(t * (5 if pose == "climb" else 2)) % (4 if pose == "climb" else 2)
            lo = self.app.save.loadout(2 if i == 0 else 1)
            sprites.draw_character(surf, lo, p.x + p.offset(h), sy(h, 0), pose, frame, 0)
        draw_title(surf, t, W // 2, 12)
        self.menu.draw(surf, t)
        draw_text(surf, "W/S/A/D OR ARROWS + ENTER", W // 2, 192, WHITE, 1, shadow=OUTLINE, align="center")
        draw_text(surf, "F11 FULLSCREEN", W // 2, 202, CREAM, 1, shadow=OUTLINE, align="center")
        draw_coins(surf, self.app.save.coins, t=t)


# ---------------------------------------------------------------- stage select --
class StageSelect(Scene):
    TITLES = {"two": "TWO PLAYER RACE", "time": "TIME ATTACK", "practice": "PRACTICE"}
    SUB = {"two": "SINO ANG UNANG MAKAKAKUHA NG BANDILA?", "time": "ISANG PLAYER - HABULIN ANG ORAS!",
           "practice": "MAG-EHERSISYO - WALANG KALABAN"}

    def __init__(self, app, mode):
        super().__init__(app)
        self.mode = mode
        self.t = 0.0
        last = app.save.data.get("last_stage", 1)
        self.index = max(0, min(len(catalog.STAGES) - 1, last - 1))
        self.msg = ""
        self.btns = [dict(label="BACK", rect=pygame.Rect(8, 194, 70, 15), act="back"),
                     dict(label="CHARACTERS", rect=pygame.Rect(W // 2 - 104, 194, 96, 15), act="chars"),
                     dict(label="START!", rect=pygame.Rect(W // 2 + 8, 194, 96, 15), act="start")]
        self.hover = 2

    def unlocked(self, i):
        return self.mode == "practice" or self.app.save.stage_unlocked(i + 1)

    def thumb(self, i):
        sid = i + 1
        sky = self.app.save.data["equipped"].get("skies", "stage")
        key = (sid, sky)
        cache = self.app.thumbs
        if key not in cache:
            bg = Background(sid, sky)
            for _ in range(20):
                bg.update(1 / 30, 0.3)
            s = pygame.Surface((W, H))
            bg.draw(s, 0, 1.0)
            bg.draw_crowd(s, 0, 1.0)
            cache[key] = pygame.transform.scale(s, (W // 2, H // 2))
        return cache[key]

    def _go(self, act):
        app = self.app
        if act == "back":
            self.sfx("back")
            app.pop()
        elif act == "chars":
            from character_select import CharacterSelect
            self.sfx("click")
            app.push(CharacterSelect(app))
        elif act == "start":
            if not self.unlocked(self.index):
                self.sfx("error")
                self.msg = "WIN THE PREVIOUS STAGE TO UNLOCK!"
                return
            from game import PlayScene
            self.sfx("click")
            app.save.data["last_stage"] = self.index + 1
            app.goto(PlayScene(app, self.mode, self.index + 1))

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            if k in KEYS_LEFT:
                self.index = (self.index - 1) % len(catalog.STAGES); self.sfx("move"); self.msg = ""
            elif k in KEYS_RIGHT:
                self.index = (self.index + 1) % len(catalog.STAGES); self.sfx("move"); self.msg = ""
            elif k in KEYS_OK:
                self._go("start")
            elif k == pygame.K_c:
                self._go("chars")
            elif k in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self._go("back")
        elif ev.type == pygame.MOUSEMOTION:
            for i, b in enumerate(self.btns):
                if b["rect"].collidepoint(ev.pos):
                    self.hover = i
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for b in self.btns:
                if b["rect"].collidepoint(ev.pos):
                    self._go(b["act"])
            if pygame.Rect(30, 84, 30, 34).collidepoint(ev.pos):
                self.index = (self.index - 1) % len(catalog.STAGES); self.sfx("move")
            if pygame.Rect(W - 60, 84, 30, 34).collidepoint(ev.pos):
                self.index = (self.index + 1) % len(catalog.STAGES); self.sfx("move")

    def update(self, dt):
        self.t += dt

    def draw(self, surf):
        st = catalog.STAGES[self.index]
        surf.fill((30, 24, 70))
        for y in range(0, H, 8):
            surf.fill((36, 30, 82), (0, y, W, 4))
        draw_text(surf, self.TITLES[self.mode], W // 2, 8, YELLOW, 2, shadow=OUTLINE, outline=OUTLINE, align="center")
        draw_text(surf, self.SUB[self.mode], W // 2, 27, LTGRAY, 1, shadow=OUTLINE, align="center")
        # preview frame
        fx, fy = W // 2 - 96, 42
        panel(surf, (fx - 6, fy - 6, 204, 120), (120, 70, 44), OUTLINE)
        surf.blit(self.thumb(self.index), (fx, fy))
        if not self.unlocked(self.index):
            ov = pygame.Surface((192, 108), pygame.SRCALPHA)
            ov.fill((10, 8, 30, 190))
            surf.blit(ov, (fx, fy))
            self._lock(surf, W // 2, fy + 40)
            draw_text(surf, "WIN STAGE %d TO UNLOCK" % self.index, W // 2, fy + 78, WHITE, 1, shadow=OUTLINE, align="center")
        # arrows
        bob = int(math.sin(self.t * 6) * 2)
        draw_text(surf, "<", 42 - bob, 84, YELLOW, 3, shadow=OUTLINE)
        draw_text(surf, ">", W - 56 + bob, 84, YELLOW, 3, shadow=OUTLINE)
        # info
        draw_text(surf, "%d/%d  %s" % (st["id"], len(catalog.STAGES), st["name"]), W // 2, 160, WHITE, 2, shadow=OUTLINE, align="center")
        draw_text(surf, st["tagline"], W // 2, 177, CREAM, 1, shadow=OUTLINE, align="center")
        # difficulty (wind) stars
        draw_text(surf, "HANGIN", 12, 118, LTGRAY, 1)
        for i in range(5):
            star(surf, 16 + i * 9, 134, 3, YELLOW if i < st["id"] else (70, 64, 120))
        if self.mode == "time":
            best = self.app.save.best_time(st["id"])
            draw_text(surf, "BEST TIME", W - 12, 118, LTGRAY, 1, align="right")
            draw_text(surf, ("%.2fs" % best) if best else "--", W - 12, 128, YELLOW, 1, shadow=OUTLINE, align="right")
        if self.msg:
            draw_text(surf, self.msg, W // 2, 187, ORANGE if int(self.t * 4) % 2 else RED, 1, shadow=OUTLINE, align="center")
        else:
            draw_text(surf, "A/D = CHOOSE STAGE   ENTER = START   C = CHARACTERS", W // 2, 187, LTGRAY, 1, align="center")
        for i, b in enumerate(self.btns):
            r = b["rect"]
            draw_button(surf, (r.x, r.y, r.w, r.h), b["label"], selected=(i == self.hover))
        draw_coins(surf, self.app.save.coins, t=self.t)

    def _lock(self, surf, cx, cy):
        surf.fill(OUTLINE, (cx - 10, cy - 1, 20, 18))
        surf.fill(GOLD, (cx - 9, cy, 18, 16)); surf.fill(shade(GOLD, 0.7), (cx - 9, cy + 13, 18, 3))
        surf.fill(OUTLINE, (cx - 7, cy - 12, 3, 12)); surf.fill(OUTLINE, (cx + 4, cy - 12, 3, 12)); surf.fill(OUTLINE, (cx - 7, cy - 13, 14, 3))
        surf.fill(LTGRAY, (cx - 6, cy - 11, 1, 11)); surf.fill(LTGRAY, (cx + 5, cy - 11, 1, 11)); surf.fill(LTGRAY, (cx - 6, cy - 12, 12, 1))
        surf.fill(OUTLINE, (cx - 2, cy + 4, 4, 6))


# --------------------------------------------------------------------- settings --
class SettingsScene(Scene):
    overlay = True

    def __init__(self, app):
        super().__init__(app)
        self.t = 0.0
        self.confirm = False
        self.msg = ""
        self.menu = ButtonMenu(["", "", "", "", "RESET SAVE DATA", "BACK"], W // 2 - 90, 64, 180, 17, gap=7, cols=1)
        self._labels()

    def _labels(self):
        s = self.app.save.settings
        self.menu.set_label(0, "MUSIC: " + ("ON" if s["music"] else "OFF"))
        self.menu.set_label(1, "SOUND EFFECTS: " + ("ON" if s["sfx"] else "OFF"))
        self.menu.set_label(2, "FULLSCREEN: " + ("ON" if self.app.fullscreen else "OFF"))
        self.menu.set_label(3, "MUSIC VOLUME: " + str(int(round(s.get("music_vol", 1.0) * 100))) + "%")
        self.menu.set_label(4, "SURE? PRESS AGAIN!" if self.confirm else "RESET SAVE DATA")

    def handle_event(self, ev):
        app = self.app
        if ev.type == pygame.KEYDOWN and self.menu.index == 3 and ev.key in KEYS_LEFT + KEYS_RIGHT:
            s = app.save.settings
            step = -0.1 if ev.key in KEYS_LEFT else 0.1
            s["music_vol"] = round(min(1.0, max(0.0, s.get("music_vol", 1.0) + step)), 1)
            app.sound.music_set_volume()
            self._labels()
            return
        if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
            self.sfx("back"); app.save.save(); app.pop(); return
        if ev.type == pygame.KEYDOWN and ev.key in KEYS_LEFT + KEYS_RIGHT and self.menu.index < 3:
            ev = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        i = self.menu.handle_event(ev, app.sound)
        if i is None:
            return
        s = app.save.settings
        if i != 4:
            self.confirm = False
        if i == 0:
            s["music"] = not s["music"]; app.sound.apply_settings()
        elif i == 1:
            s["sfx"] = not s["sfx"]; app.sound.apply_settings()
        elif i == 2:
            app.toggle_fullscreen()
        elif i == 3:
            s["music_vol"] = round((s.get("music_vol", 1.0) + 0.1) % 1.1, 1)
            app.sound.music_set_volume()
        elif i == 4:
            if self.confirm:
                app.save.reset(); app.sound.apply_settings(); self.msg = "SAVE DATA RESET!"; self.confirm = False
            else:
                self.confirm = True; self.msg = "THIS ERASES COINS AND UNLOCKS!"
        elif i == 5:
            app.save.save(); app.pop()
        self._labels()

    def update(self, dt):
        self.t += dt

    def draw(self, surf):
        dim(surf, 170)
        panel(surf, (W // 2 - 110, 18, 220, 168), (40, 34, 90), OUTLINE)
        draw_text(surf, "SETTINGS", W // 2, 28, YELLOW, 2, shadow=OUTLINE, align="center")
        self.menu.draw(surf, self.t)
        draw_text(surf, self.msg, W // 2, 170, ORANGE, 1, shadow=OUTLINE, align="center")


# ------------------------------------------------------------------------ pause --
class PauseScene(Scene):
    overlay = True

    def __init__(self, app, play):
        super().__init__(app)
        self.play = play
        self.t = 0.0
        self.menu = ButtonMenu(["RESUME", "RESTART", "SETTINGS", "MAIN MENU"], W // 2 - 60, 84, 120, 17, gap=7)

    def enter(self):
        self.app.sound.stop_loops()
        self.app.sound.music_duck(True)

    def _resume(self):
        self.app.sound.music_duck(False)
        self.app.pop()
        self.play.on_resume()

    def handle_event(self, ev):
        app = self.app
        if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_p):
            self._resume(); return
        i = self.menu.handle_event(ev, app.sound)
        if i == 0:
            self._resume()
        elif i == 1:
            from game import PlayScene
            app.sound.music_duck(False)
            app.goto(PlayScene(app, self.play.mode, self.play.stage_id))
        elif i == 2:
            app.push(SettingsScene(app))
        elif i == 3:
            app.sound.music_duck(False)
            app.goto(MainMenu(app))

    def update(self, dt):
        self.t += dt

    def draw(self, surf):
        dim(surf, 150)
        panel(surf, (W // 2 - 76, 52, 152, 122), (40, 34, 90), OUTLINE)
        draw_text(surf, "PAUSED", W // 2, 62, YELLOW, 2, shadow=OUTLINE, align="center")
        self.menu.draw(surf, self.t)
