"""The match itself: two-player race, time attack and practice."""
import math
import random
import pygame
import catalog
import sprites
from backgrounds import Background
from bamboo import Bamboo, sy, draw_flag
from camera import Camera
from effects import Bubbles, Events, Particles
from gfx import panel
from hud import (draw_banner, draw_countdown, draw_key_guide, draw_player_panel, draw_progress, draw_timer)
from menu import PauseScene
from pixelfont import draw_text, text_width
from player import Player
from ui import Scene
from victory import VictoryScene
from settings import *

KEYMAP_P1 = dict(up=pygame.K_w, down=pygame.K_s, left=pygame.K_a, right=pygame.K_d)
KEYMAP_P2 = dict(up=pygame.K_UP, down=pygame.K_DOWN, left=pygame.K_LEFT, right=pygame.K_RIGHT)

CHANTS = ["GO! GO! GO!", "SAKAY! SAKAY!", "TAAS PA!", "KAYA MO YAN!", "SIGE PA!"]
EVENT_SHOUT = {"wind": "HALA! HANGIN!", "rain": "ULAN! ULAN!", "cheer": "VIVA! VIVA!",
               "gust": "WOW! BUGSO!", "confetti": "YEHEY! PISTA!"}


class PlayScene(Scene):
    hide_cursor = True

    def __init__(self, app, mode, stage_id):
        super().__init__(app)
        self.mode = mode                 # "two" | "time" | "practice"
        self.stage_id = stage_id
        self.stage = catalog.STAGES[stage_id - 1]
        save = app.save
        eq = save.data["equipped"]
        self.rng = random.Random()
        self.bg = Background(stage_id, eq.get("skies", "stage"))
        self.cam = Camera()
        self.particles = Particles(self.rng)
        self.bubbles = Bubbles()
        self.events = Events(app.sound, self.particles, self.stage, self.rng, auto=(mode != "practice"))
        self.events.listeners.append(self._on_event)
        amp = 5.0 * self.stage["sway"]
        ph = self.rng.uniform(0, 6.28)
        if mode in("two", "bot"):
            self.bamboo = {1: Bamboo(POLE_X_LEFT, eq["bamboo"], eq["flags"], ph, amp),
                           2: Bamboo(POLE_X_RIGHT, eq["bamboo"], eq["flags"], ph + 2.1, amp)}
            self.players = [Player(1, "PLAYER 1", POLE_X_LEFT, [KEYMAP_P1], save.loadout(1), self.rng),
                            Player(2, "PLAYER 2", POLE_X_RIGHT, [KEYMAP_P2], save.loadout(2), self.rng)]
            if mode == "bot": self.players[1].is_bot = True 
        else:
            self.bamboo = {1: Bamboo(POLE_X_CENTER, eq["bamboo"], eq["flags"], ph, amp)}
            self.players = [Player(1, "PLAYER 1", POLE_X_CENTER, [KEYMAP_P1, KEYMAP_P2], save.loadout(1), self.rng)]
        self.flag_design = eq["flags"]
        self.world = pygame.Surface((W, H))
        self.rain_ov = pygame.Surface((W, H), pygame.SRCALPHA)
        self.rain_ov.fill((20, 30, 80, 255))
        self.flash_ov = pygame.Surface((W, H), pygame.SRCALPHA)
        self.flash_ov.fill((255, 255, 255, 255))
        self.t = 0.0
        self.race_t = 0.0
        self.cd = 0.0
        self.cd_step = -1
        self.phase = "countdown"         # countdown | racing | finish
        self.finish_t = 0.0
        self.winner = None
        self.flash = 0.0
        self.jingle = False
        self.chant_t = {1: 2.5, 2: 3.2}
        self.climb_time = {1: 0.0, 2: 0.0}
        self.near_said = False
        self.practice_msg = None
        self.sweat_t = 0.0
        self.step_alt = 0
        self.cam.snap([0.0])

    # -- lifecycle -------------------------------------------------------------------
    def enter(self):
        self.app.sound.stop_loops()
        self.app.sound.music_start()
        self.app.sound.music_duck(True)

    def on_resume(self):
        snd = self.app.sound
        if self.events.kind in ("wind", "gust"):
            snd.loop_start("wind")
        if self.events.kind == "rain":
            snd.loop_start("rain")

    def leave(self):
        self.events.stop_all()

    # -- events ------------------------------------------------------------------------
    def _on_event(self, kind):
        self.bubbles.say(EVENT_SHOUT[kind], W // 2, 68, 2.4, RED, key="event")
        if kind == "gust":
            for pl in self.players:
                pl.kick(self.events.dir * 1.1)
            self.cam.shake(2.0, 0.5)

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE and self.phase != "finish":
                self.app.push(PauseScene(self.app, self))
            elif self.mode == "practice" and pygame.K_1 <= ev.key <= pygame.K_5:
                kinds = ["wind", "rain", "gust", "confetti", "cheer"]
                self.events.start(kinds[ev.key - pygame.K_1])

    # -- update ---------------------------------------------------------------------------
    def update(self, dt):
        snd = self.app.sound
        self.t += dt
        keys = pygame.key.get_pressed()
        if self.phase == "countdown":
            self.cd += dt
            step = int(self.cd)
            if step != self.cd_step and step <= 3:
                self.cd_step = step
                snd.play("beep" if step < 3 else "go")
                if step == 3:
                    for i, pl in enumerate(self.players):
                        self.bubbles.say("GO! GO! GO!", W - 60 if pl.idx == 1 else 60, 50, 1.8, RED, key="chant%d" % pl.idx)
            if self.cd >= 3.0:
                self.phase = "racing"
        racing = self.phase == "racing"
        if racing:
            self.race_t += dt
        self.events.update(dt, racing)
        for pole in self.bamboo.values():
            pole.prepare(self.t, self.events)
        for pl in self.players:
            pole = self.bamboo[pl.idx]
            inp = pl.bot_input(pole) if getattr(pl, "is_bot", False) else pl.read_input(keys)
            pl.update(dt, inp, self.events, pole, self.t, active=racing)
            self._handle_player_events(pl, pole)
            self._crowd_logic(pl, dt, racing)
        # finishing
        if self.phase == "finish":
            self._update_finish(dt)
        # camera / background / fx
        self.cam.update(dt, [p.h for p in self.players])
        excite = 0.12 + 0.7 * self.events.cheer_level
        if self.phase == "finish":
            excite = 1.0
        self.bg.update(dt, excite)
        self.particles.update(dt)
        self.bubbles.update(dt)
        if self.flash > 0:
            self.flash = max(0.0, self.flash - dt * 1.6)

    def _handle_player_events(self, pl, pole):
        snd = self.app.sound
        cam = int(self.cam.y)
        for ev in pl.pop_events():
            x = pl.screen_x(pole)
            y = sy(pl.h, cam)
            if ev == "step":
                self.step_alt += 1
                snd.play("tok", 0.55 if pl.idx == 1 else 0.4)
                if self.step_alt % 2 == 0:
                    self.particles.sparkle(x + self.rng.randint(-4, 4), y - 8, 1, (255, 250, 200))
            elif ev == "slip":
                snd.play("slip")
                self.particles.dust(x, y - 6, 8)
                self.cam.shake(1.5, 0.3)
                self.bubbles.say("ARAY!", W - 60 if pl.idx == 1 else 60, 50, 1.4, RED, key="chant%d" % pl.idx)
                if self.mode != "two":
                    self.bubbles.say("ARAY!", W // 2, 50, 1.4, RED, key="chant1")
            elif ev == "grab" and self.phase == "racing":
                self._finish(pl)
        if pl.stamina < 25 and pl.state in ("idle", "climb"):
            self.sweat_t -= 1 / 60.0
            if self.sweat_t <= 0:
                self.particles.sweat(pl.screen_x(pole) + 7, sy(pl.h, cam) - 22)
                self.sweat_t = 0.35

    def _crowd_logic(self, pl, dt, racing):
        if not racing:
            return
        i = pl.idx
        self.climb_time[i] = self.climb_time[i] + dt if pl.moving_up else 0.0
        self.chant_t[i] -= dt
        side_x = (W - 60) if (i == 1 and self.mode == "two") else (60 if self.mode == "two" else W // 2)
        if self.chant_t[i] <= 0 and self.climb_time[i] > 1.6:
            self.bubbles.say(self.rng.choice(CHANTS), side_x, 50, 2.0, RED, key="chant%d" % i)
            self.chant_t[i] = self.rng.uniform(3.5, 5.0)
        if pl.progress >= 0.85 and not self.near_said:
            self.near_said = True
            self.bubbles.say("HALA! MALAPIT NA!", W // 2, 68, 2.6, DKRED, key="event")
            self.app.sound.play("cheer", 0.6)

    # -- finish --------------------------------------------------------------------------
    def _finish(self, winner):
        snd = self.app.sound
        self.phase = "finish"
        self.finish_t = 0.0
        self.winner = winner
        winner.finish_time = self.race_t
        pole = self.bamboo[winner.idx]
        pole.flag_taken = True
        for pl in self.players:
            if pl is not winner:
                pl.state = "defeat"
                self.bubbles.say("NICE TRY!", W - 60 if pl.idx == 1 else 60, 50, 3.0, DKRED, key="chant%d" % pl.idx)
        self.events.stop_all()
        snd.stop_loops()
        snd.play("flag")
        snd.play("cheer")
        cam = int(self.cam.y)
        self.particles.confetti_burst(winner.screen_x(pole), sy(winner.h, cam) - 20, 70, 180)
        self.flash = 0.7
        self.cam.shake(3.0, 0.6)
        self.bubbles.say("PANALO!", W // 2, 68, 3.0, RED, key="event")
        if self.mode == "practice":
            self.practice_msg = "FLAG GRABBED IN %.2f SECONDS!" % winner.finish_time

    def _update_finish(self, dt):
        self.finish_t += dt
        w = self.winner
        if self.finish_t > 0.6 and w.state == "grab":
            w.state = "victory"
        if self.finish_t > 0.9 and not self.jingle and self.mode != "practice":
            self.jingle = True
            self.app.sound.play("victory")
        if self.finish_t < 2.0 and self.rng.random() < dt * 8:
            self.particles.confetti_burst(self.rng.randint(40, W - 40), self.rng.randint(20, 70), 12, 90)
        if self.mode == "practice":
            if self.finish_t > 2.8:
                self._reset_practice()
            return
        if self.finish_t > 3.0:
            self.app.goto(VictoryScene(self.app, self._make_result()))
            self.phase = "done"

    def _reset_practice(self):
        for pl in self.players:
            pl.reset()
        for pole in self.bamboo.values():
            pole.flag_taken = False
        self.phase = "racing"
        self.race_t = 0.0
        self.winner = None
        self.practice_msg = None
        self.jingle = False
        self.near_said = False

    def _make_result(self):
        save = self.app.save
        w = self.winner
        t = w.finish_time
        limit = FAST_TIME + 1.5 * (self.stage_id - 1)
        bd = [("WIN", COIN_WIN)] if self.mode == "bot" and not getattr(w, "is_bot", False) else []
        if self.mode == "bot" and not getattr(w, "is_bot", False) and t <= limit:
            bd.append(("FAST CLIMB", COIN_FAST))
        if self.mode == "bot" and not getattr(w, "is_bot", False) and w.slips == 0 and w.danger_time < 1.0:
            bd.append(("PERFECT BALANCE", COIN_PERFECT))
        total = sum(a for _, a in bd)
        save.add_coins(total)
        st = save.data["stats"]
        new_record, best = False, None
        if self.mode == "two":
            st["matches"] += 1
            st["p%d_wins" % w.idx] += 1
        else:
            st["time_attack_runs"] += 1
            new_record = save.record_time_attack(self.stage_id, t)
            best = save.best_time(self.stage_id)
        unlocked = None
        nxt = self.stage_id + 1
        if nxt <= len(catalog.STAGES) and not save.stage_unlocked(nxt):
            save.unlock_stage(nxt)
            unlocked = nxt
        save.data["last_stage"] = self.stage_id
        save.save()
        return dict(mode=self.mode, stage=self.stage_id, winner=w.idx, time=t, coins=total, breakdown=bd,
                    new_record=new_record, best=best, unlocked_stage=unlocked,
                    loadouts={p.idx: p.loadout for p in self.players})

    # -- drawing ------------------------------------------------------------------------------
    def _draw_player(self, w, pl, cam):
        pole = self.bamboo[pl.idx]
        x = pl.screen_x(pole)
        y = sy(pl.h, cam)
        pose, frame = pl.pose()
        if y < -40 or y > H + 40:
            return
        sprites.draw_character(w, pl.loadout, x, y, pose, frame, pl.lean())
        if pl.state in ("grab", "victory"):
            draw_flag(w, x + 4, y - 40, self.flag_design, self.t)
            w.fill(BROWN, (x + 3, y - 43, 1, 22))

    def draw(self, surf):
        w = self.world
        cam = int(self.cam.y)
        self.bg.draw(w, cam, self.t)
        self.bg.draw_crowd(w, cam, self.t)
        for idx, pole in self.bamboo.items():
            pole.draw(w, cam, self.t)
        for pl in self.players:
            self._draw_player(w, pl, cam)
        self.particles.draw(w)
        if self.events.rain > 0.02:
            self.rain_ov.set_alpha(int(70 * self.events.rain))
            w.blit(self.rain_ov, (0, 0))
        dx, dy = self.cam.shake_offset()
        surf.blit(w, (0, 0))
        if dx or dy:
            surf.blit(w, (dx, dy))
        if self.flash > 0:
            self.flash_ov.set_alpha(int(150 * self.flash))
            surf.blit(self.flash_ov, (0, 0))
        self._draw_hud(surf)

    def _draw_hud(self, surf):
        t = self.t
        ev = self.events
        if self.mode == "two":
            p2, p1 = self.players
            draw_player_panel(surf, p2, 4, 2, 146, t)
            draw_player_panel(surf, p1, W - 150, 2, 146, t)
            draw_progress(surf, [p2], 6, 52, 172, "L", t)
            draw_progress(surf, [p1], W - 12, 52, 172, "R", t)
            draw_timer(surf, self.race_t, "TIME", None, t)
        else:
            p1 = self.players[0]
            draw_player_panel(surf, p1, 4, 2, 146, t)
            draw_progress(surf, [p1], 6, 52, 172, "L", t)
            best = self.app.save.best_time(self.stage_id) if self.mode == "time" else None
            draw_timer(surf, self.race_t, "TIME" if self.mode == "time" else "PRACTICE", best, t)
            draw_text(surf, self.stage["name"], W - 6, 6, WHITE, 1, shadow=OUTLINE, align="right")
        draw_banner(surf, ev.banner, t)
        self.bubbles.draw(surf)
        if self.phase == "countdown":
            draw_countdown(surf, self.cd)
            if self.mode == "two":
                draw_key_guide(surf, 2, 58, 44)
                draw_key_guide(surf, 1, W - 58, 44)
        if self.mode == "practice":
            panel(surf, (W // 2 - 150, H - 20, 300, 14), (30, 28, 70), OUTLINE)
            draw_text(surf, "1 WIND  2 RAIN  3 GUST  4 CONFETTI  5 CHEER  ESC PAUSE", W // 2, H - 17, LTGRAY, 1, align="center")
            if self.practice_msg and self.phase == "finish":
                draw_text(surf, self.practice_msg, W // 2, 100, YELLOW, 1, shadow=OUTLINE, outline=OUTLINE, align="center")
        if self.mode != "two" and self.phase == "countdown":
            draw_key_guide(surf, 1, 58, 44)
            draw_key_guide(surf, 2, W - 58, 44)
