"""Victory screen: trophy, time, coin rewards and next actions."""
import math
import random
import pygame
import catalog
import sprites
from backgrounds import Background
from bamboo import draw_flag
from effects import Particles
from gfx import draw_coin, draw_trophy, panel, shade, star
from pixelfont import draw_text, text_width
from ui import ButtonMenu, Scene, dim
from hud import P1_COLOR, P2_COLOR
from settings import *


class VictoryScene(Scene):
    def __init__(self, app, result):
        super().__init__(app)
        self.r = result
        self.t = 0.0
        self.rng = random.Random()
        eq = app.save.data["equipped"]
        self.bg = Background(result["stage"], eq.get("skies", "stage"))
        self.fx = Particles(self.rng)
        self.fw_t = 0.2
        self.shown = 0
        self.tick = 0
        last = result["stage"] >= len(catalog.STAGES)
        labels = ["PLAY AGAIN", "STAGE SELECT" if last else "NEXT STAGE", "MAIN MENU"]
        self.menu = ButtonMenu(labels, 140, 140, 74, 16, gap=7, cols=3)
        self.last_stage = last

    def enter(self):
        self.app.sound.music_duck(False)
        self.fx.confetti_burst(W // 2, 40, 50, 160)

    def handle_event(self, ev):
        if self.t < 0.6:
            return
        i = self.menu.handle_event(ev, self.app.sound)
        if i is None:
            return
        from game import PlayScene
        from menu import MainMenu, StageSelect
        app, r = self.app, self.r
        if i == 0:
            app.goto(PlayScene(app, r["mode"], r["stage"]))
        elif i == 1:
            if self.last_stage:
                app.goto(MainMenu(app))
                app.push(StageSelect(app, r["mode"]))
            else:
                app.save.data["last_stage"] = r["stage"] + 1
                app.goto(PlayScene(app, r["mode"], r["stage"] + 1))
        else:
            app.goto(MainMenu(app))

    def update(self, dt):
        self.t += dt
        self.bg.update(dt, 1.0)
        self.fw_t -= dt
        if self.fw_t <= 0:
            self.fx.rocket(self.rng.randint(30, W - 30), self.rng.randint(20, 90))
            self.fw_t = self.rng.uniform(0.6, 1.3)
        if self.rng.random() < dt * 14:
            self.fx.confetti_fall(1)
        self.fx.update(dt)
        # coin count-up
        target = self.r["coins"]
        if self.t > 0.9 and self.shown < target:
            self.shown = min(target, self.shown + max(1, int(dt * 90)))
            step = self.shown // 10
            if step != self.tick:
                self.tick = step
                self.sfx("coin", 0.5)

    def draw(self, surf):
        r, t = self.r, self.t
        self.bg.draw(surf, 0, t)
        dim(surf, 110)
        self.fx.draw(surf)
        w_idx = r["winner"]
        tone = P1_COLOR if w_idx == 1 else P2_COLOR
        bounce = int(abs(math.sin(t * 4)) * 3)
        draw_text(surf, "FLAG CAPTURED!", W // 2, 6, YELLOW, 2, shadow=OUTLINE, outline=OUTLINE, align="center")
        head = "PLAYER %d WINS!" % w_idx if r["mode"] == "two" else "TIME ATTACK COMPLETE!"
        draw_text(surf, head, W // 2, 24, tone if r["mode"] == "two" else WHITE, 3 if r["mode"] == "two" else 2,
                  shadow=OUTLINE, outline=OUTLINE, align="center")
        # podium
        wx, wy = 84, 146
        surf.fill(OUTLINE, (58, wy - 1, 54, 32)); surf.fill((214, 170, 60), (59, wy, 52, 30))
        surf.fill((255, 226, 130), (59, wy, 52, 2)); surf.fill((160, 120, 40), (59, wy + 28, 52, 2))
        draw_text(surf, "1", 85, wy + 9, OUTLINE, 2, align="center")
        pose_frame = int(t * 6) % 2
        sprites.draw_character(surf, r["loadouts"][w_idx], wx, wy, "win", pose_frame, 0)
        draw_flag(surf, wx + 5, wy - 44, self.app.save.data["equipped"]["flags"], t)
        surf.fill(BROWN, (wx + 4, wy - 47, 1, 22))
        if r["mode"] == "two":
            l_idx = 2 if w_idx == 1 else 1
            lx, ly = 30, 166
            surf.fill(OUTLINE, (10, ly - 1, 40, 12)); surf.fill((170, 176, 190), (11, ly, 38, 10))
            surf.fill((220, 224, 236), (11, ly, 38, 1))
            draw_text(surf, "2", 30, ly + 2, OUTLINE, 1, align="center")
            sprites.draw_character(surf, r["loadouts"][l_idx], lx, ly, "lose", int(t * 2) % 2, 0)
            if int(t * 1.5) % 2 == 0:
                w = text_width("NICE TRY!") + 8
                panel(surf, (lx - w // 2, ly - 46, w, 12), CREAM, OUTLINE, WHITE, (220, 200, 160))
                draw_text(surf, "NICE TRY!", lx, ly - 43, DKRED, 1, align="center")
        # info panel
        panel(surf, (140, 48, 236, 88), (40, 34, 90), OUTLINE)
        draw_text(surf, "CLIMB TIME", 152, 55, LTGRAY, 1)
        draw_text(surf, "%.2f SECONDS" % r["time"], 152, 65, WHITE, 2, shadow=OUTLINE)
        if r["mode"] == "time":
            if r["new_record"]:
                col = LIME if int(t * 4) % 2 else YELLOW
                draw_text(surf, "NEW RECORD!", 368, 55, col, 1, shadow=OUTLINE, align="right")
            elif r["best"]:
                draw_text(surf, "BEST %.2f" % r["best"], 368, 55, YELLOW, 1, shadow=OUTLINE, align="right")
        draw_coin(surf, 156, 91, t)
        draw_text(surf, "COINS EARNED", 166, 88, LTGRAY, 1)
        draw_text(surf, "+%d" % self.shown, 368, 84, YELLOW, 2, shadow=OUTLINE, align="right")
        y = 106
        shown_rows = 0
        for name, amt in r["breakdown"]:
            if t > 0.9 + shown_rows * 0.25:
                draw_text(surf, name, 156, y, CREAM, 1, shadow=OUTLINE)
                draw_text(surf, "+%d" % amt, 368, y, LIME, 1, shadow=OUTLINE, align="right")
                y += 10
            shown_rows += 1
        draw_text(surf, "TOTAL COINS: %d" % self.app.save.coins, 376, 161, WHITE, 1, shadow=OUTLINE, align="right")
        if r.get("unlocked_stage"):
            draw_text(surf, "STAGE %d UNLOCKED!" % r["unlocked_stage"], 140, 161, ORANGE if int(t * 3) % 2 else YELLOW, 1, shadow=OUTLINE)
        self.menu.draw(surf, t)
        self.bg.draw_crowd(surf, 0, t)
