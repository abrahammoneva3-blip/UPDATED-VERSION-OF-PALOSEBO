"""Particles (confetti, rain, dust, fireworks), random fiesta events and speech bubbles."""
import math
import random
import pygame
from gfx import panel, shade
from pixelfont import draw_text, text_width
from settings import *

CONFETTI_COLORS = [RED, YELLOW, BLUE, GREEN, ORANGE, PINK, TEAL, PURPLE, WHITE]
MAX_PARTICLES = 520


class Particles:
    """Screen-space pixel particles. Each particle is a list for speed."""
    X, Y, VX, VY, LIFE, MAXLIFE, KIND, COLOR, SIZE, PHASE = range(10)

    def __init__(self, rng=None):
        self.p = []
        self.rng = rng or random.Random()
        self.pending = []

    def _add(self, kind, x, y, vx, vy, life, color, size=1):
        if len(self.p) >= MAX_PARTICLES:
            return
        self.p.append([x, y, vx, vy, life, life, kind, color, size, self.rng.uniform(0, 6.28)])

    # -- emitters ----------------------------------------------------------------
    def confetti_burst(self, x, y, n=40, power=150, up=True):
        r = self.rng
        for _ in range(n):
            a = r.uniform(0, 6.283)
            sp = r.uniform(0.3, 1.0) * power
            self._add("confetti", x, y, math.cos(a) * sp, math.sin(a) * sp - (power * 0.6 if up else 0),
                      r.uniform(1.6, 3.2), r.choice(CONFETTI_COLORS), r.choice((2, 3)))

    def confetti_fall(self, n=1):
        r = self.rng
        for _ in range(n):
            self._add("confetti", r.uniform(-10, W + 10), -4, r.uniform(-12, 12), r.uniform(10, 30),
                      r.uniform(4.0, 6.0), r.choice(CONFETTI_COLORS), r.choice((2, 3)))

    def rain(self, n=1, wind=0.0):
        r = self.rng
        for _ in range(n):
            self._add("rain", r.uniform(-30, W + 30), -6, 40 + wind * 30, r.uniform(230, 290),
                      1.2, r.choice(((150, 190, 240), (190, 220, 250))), 4)

    def streak(self, direction, n=1):
        r = self.rng
        for _ in range(n):
            x = -12 if direction > 0 else W + 12
            self._add("streak", x, r.uniform(30, H - 30), direction * r.uniform(260, 380), r.uniform(-8, 8),
                      1.8, (235, 245, 255), r.choice((6, 9, 12)))

    def leaf(self, direction, n=1):
        r = self.rng
        for _ in range(n):
            x = -6 if direction > 0 else W + 6
            self._add("leaf", x, r.uniform(20, H - 60), direction * r.uniform(90, 160), r.uniform(-10, 20),
                      3.5, r.choice((LIME, GREEN, YELLOW, ORANGE)), 2)

    def dust(self, x, y, n=5, color=(255, 240, 200)):
        r = self.rng
        for _ in range(n):
            self._add("dust", x + r.uniform(-4, 4), y + r.uniform(-2, 2), r.uniform(-25, 25), r.uniform(-30, 8),
                      r.uniform(0.3, 0.6), color, r.choice((2, 3)))

    def sparkle(self, x, y, n=6, color=YELLOW):
        r = self.rng
        for _ in range(n):
            a = r.uniform(0, 6.283)
            sp = r.uniform(20, 60)
            self._add("spark", x, y, math.cos(a) * sp, math.sin(a) * sp, r.uniform(0.3, 0.7), color, 1)

    def sweat(self, x, y):
        self._add("sweat", x, y, self.rng.uniform(-8, 8), -25, 0.5, (140, 210, 255), 2)

    def coin_pop(self, x, y):
        self._add("coin", x, y, self.rng.uniform(-8, 8), -55, 0.9, GOLD, 3)

    def rocket(self, x, y_target, color=None):
        r = self.rng
        self._add("rocket", x, H + 4, r.uniform(-12, 12), -r.uniform(170, 210), (H + 4 - y_target) / 150.0,
                  color or r.choice(CONFETTI_COLORS), 2)

    def burst(self, x, y, color, n=26, power=70):
        r = self.rng
        col2 = r.choice(CONFETTI_COLORS)
        for i in range(n):
            a = 6.283 * i / n + r.uniform(-.1, .1)
            sp = power * r.uniform(0.75, 1.0)
            self._add("fw", x, y, math.cos(a) * sp, math.sin(a) * sp, r.uniform(0.9, 1.4),
                      color if i % 3 else col2, 2)

    # -- update / draw ---------------------------------------------------------------
    def update(self, dt):
        keep = []
        for q in self.p:
            q[self.LIFE] -= dt
            if q[self.LIFE] <= 0:
                if q[self.KIND] == "rocket":
                    self.burst(q[self.X], q[self.Y], q[self.COLOR])
                continue
            k = q[self.KIND]
            ph = q[self.PHASE] = q[self.PHASE] + dt * 9.0
            if k == "confetti":
                q[self.VY] = min(q[self.VY] + 110 * dt, 62)
                q[self.VX] *= (1 - 1.2 * dt)
                q[self.X] += (q[self.VX] + math.sin(ph) * 14) * dt
                q[self.Y] += q[self.VY] * dt
            elif k == "rain":
                q[self.X] += q[self.VX] * dt
                q[self.Y] += q[self.VY] * dt
                if q[self.Y] > H:
                    continue
            elif k in ("streak",):
                q[self.X] += q[self.VX] * dt
                q[self.Y] += q[self.VY] * dt
            elif k == "leaf":
                q[self.X] += q[self.VX] * dt
                q[self.Y] += (q[self.VY] + math.sin(ph * 0.7) * 30) * dt
            elif k == "dust":
                q[self.X] += q[self.VX] * dt
                q[self.Y] += q[self.VY] * dt
                q[self.VX] *= (1 - 3 * dt)
            elif k in ("spark", "fw"):
                q[self.VY] += (60 if k == "fw" else 120) * dt
                q[self.VX] *= (1 - 0.6 * dt)
                q[self.X] += q[self.VX] * dt
                q[self.Y] += q[self.VY] * dt
            elif k == "sweat":
                q[self.VY] += 90 * dt
                q[self.X] += q[self.VX] * dt
                q[self.Y] += q[self.VY] * dt
            elif k == "coin":
                q[self.VY] += 70 * dt
                q[self.Y] += q[self.VY] * dt
                q[self.X] += q[self.VX] * dt
            elif k == "rocket":
                q[self.VY] *= (1 - 0.5 * dt)
                q[self.X] += q[self.VX] * dt
                q[self.Y] += q[self.VY] * dt
                if self.rng.random() < 0.7:
                    self._add("spark", q[self.X], q[self.Y] + 2, 0, 12, 0.3, (255, 226, 150), 1)
            keep.append(q)
        self.p = keep

    def draw(self, surf, kinds=None):
        for q in self.p:
            k = q[self.KIND]
            if kinds and k not in kinds:
                continue
            x, y = int(q[self.X]), int(q[self.Y])
            c = q[self.COLOR]
            s = q[self.SIZE]
            frac = q[self.LIFE] / q[self.MAXLIFE]
            if k == "confetti":
                w = s if math.sin(q[self.PHASE]) > 0 else max(1, s - 1)
                surf.fill(c, (x, y, w, s if w == s else s + 1))
            elif k == "rain":
                pygame.draw.line(surf, c, (x, y), (x + 1, y + s), 1)
            elif k == "streak":
                surf.fill(c, (x, y, s, 1))
            elif k == "leaf":
                surf.fill(c, (x, y, 2, 1))
                surf.fill(shade(c, 0.7), (x + 1, y + 1, 2, 1))
            elif k == "dust":
                sz = max(1, int(s * frac + 0.5))
                surf.fill(c, (x, y, sz, sz))
            elif k in ("spark", "fw"):
                if k == "fw" and frac < 0.25 and int(q[self.PHASE] * 2) % 2:
                    continue
                sz = 2 if (k == "fw" and frac > 0.3) else 1
                surf.fill(c, (x, y, sz, sz))
            elif k == "sweat":
                surf.fill(c, (x, y, 1, 2))
            elif k == "coin":
                surf.fill(OUTLINE, (x - 1, y - 1, 4, 4))
                surf.fill(c, (x, y, 2, 2))
            elif k == "rocket":
                surf.fill((255, 240, 200), (x, y, 2, 3))


# -------------------------------------------------------------------------------- #
EVENT_INFO = {
    #        duration  english          filipino               weight
    "wind": (6.5, "STRONG WIND!", "MALAKAS NA HANGIN!", 25),
    "rain": (7.0, "LIGHT RAIN!", "MADULAS ANG KAWAYAN!", 20),
    "cheer": (4.0, "FIESTA CHEER!", "VIVA! VIVA!", 20),
    "gust": (2.4, "STRONG GUST!", "BUGSO NG HANGIN!", 15),
    "confetti": (4.5, "CONFETTI!", "MASAYA ANG PISTA!", 20),
}


class Events:
    """Random fiesta events. Only one is active at a time, and they are spaced out."""

    def __init__(self, sound, particles, stage, rng=None, auto=True):
        self.sound = sound
        self.particles = particles
        self.stage = stage
        self.auto = auto
        self.rng = rng or random.Random()
        self.kind = None
        self.remaining = 0.0
        self.last = None
        self.next_in = self.rng.uniform(7.0, 10.0)
        self.wind = 0.0
        self.rain = 0.0
        self.gust_t = 99.0
        self.dir = 1
        self.banner = None      # [english, filipino, timer]
        self.kick = 0.0         # one-off balance kick (gust)
        self.listeners = []
        self._acc = {"rain": 0.0, "streak": 0.0, "leaf": 0.0, "confetti": 0.0}
        self._creak = 1.0
        self.cheer_level = 0.0  # 0..1 for crowd animation

    # -- derived environment values --------------------------------------------------
    @property
    def gust_env(self):
        t = self.gust_t
        if t >= 20:
            return 0.0
        return t / 0.25 if t < 0.25 else math.exp(-(t - 0.25) * 1.5)

    @property
    def sway_mult(self):
        return 1.0 + 1.5 * self.wind + 0.5 * self.gust_env

    @property
    def gust_px(self):
        return self.dir * self.gust_env * 12.0

    @property
    def push_bias(self):
        return self.dir * (0.55 * self.wind * self.stage.get("wind_bias", 1.0) + 2.0 * self.gust_env)

    @property
    def climb_mult(self):
        return 1.0 - 0.12 * self.rain

    @property
    def noise_mult(self):
        return (1.0 + 0.6 * self.wind + 0.35 * self.rain) * self.stage.get("sway", 1.0) ** 0.8

    @property
    def slide_extra(self):
        return 6.0 * self.rain

    # -- control ----------------------------------------------------------------------
    def start(self, kind):
        if self.kind:
            self.end()
        dur, en, fil, _ = EVENT_INFO[kind]
        self.kind = kind
        self.remaining = dur
        self.last = kind
        self.banner = [en, fil, 3.0]
        self.dir = self.rng.choice((-1, 1))
        if kind == "wind":
            self.sound.loop_start("wind")
            self.sound.play("creak")
        elif kind == "rain":
            self.sound.loop_start("rain")
        elif kind == "gust":
            self.gust_t = 0.0
            self.sound.loop_start("wind")
            self.sound.play("creak")
        elif kind == "cheer":
            self.sound.play("cheer")
        elif kind == "confetti":
            self.sound.play("pop")
            self.sound.play("cheer", 0.7)
            self.particles.confetti_burst(W // 2, H // 3, 30, 120)
        for fn in self.listeners:
            fn(kind)

    def end(self):
        if self.kind in ("wind", "gust"):
            self.sound.loop_stop("wind")
        if self.kind == "rain":
            self.sound.loop_stop("rain")
        self.kind = None
        self.remaining = 0.0
        gap = self.rng.uniform(6.0, 11.0) / max(0.5, self.stage.get("events", 1.0))
        self.next_in = gap

    def stop_all(self):
        self.sound.loop_stop("wind")
        self.sound.loop_stop("rain")
        self.kind = None
        self.wind = self.rain = 0.0
        self.gust_t = 99.0

    def _pick(self):
        kinds = [k for k in EVENT_INFO if k != self.last]
        weights = [EVENT_INFO[k][3] for k in kinds]
        return self.rng.choices(kinds, weights)[0]

    # -- per-frame ----------------------------------------------------------------------
    def update(self, dt, racing=True):
        if racing and self.auto and not self.kind:
            self.next_in -= dt
            if self.next_in <= 0:
                self.start(self._pick())
        if self.kind:
            self.remaining -= dt
            if self.remaining <= 0:
                self.end()
        tw = 1.0 if self.kind == "wind" else 0.0
        tr = 1.0 if self.kind == "rain" else 0.0
        self.wind += (tw - self.wind) * min(1.0, dt * 1.8)
        self.rain += (tr - self.rain) * min(1.0, dt * 1.5)
        if self.gust_t < 50:
            self.gust_t += dt
        tc = 1.0 if self.kind in ("cheer", "confetti") else 0.0
        self.cheer_level += (tc - self.cheer_level) * min(1.0, dt * 3.0)
        if self.banner:
            self.banner[2] -= dt
            if self.banner[2] <= 0:
                self.banner = None
        # particles from active events
        p = self.particles
        acc = self._acc
        if self.rain > 0.05:
            acc["rain"] += dt * 95 * self.rain
            n = int(acc["rain"]); acc["rain"] -= n
            p.rain(n, self.dir * 0.3)
        w = max(self.wind, self.gust_env * 0.8)
        if w > 0.05:
            acc["streak"] += dt * 9 * w
            n = int(acc["streak"]); acc["streak"] -= n
            p.streak(self.dir, n)
            acc["leaf"] += dt * 3 * w
            n = int(acc["leaf"]); acc["leaf"] -= n
            p.leaf(self.dir, n)
            self._creak -= dt
            if self._creak <= 0 and self.kind == "wind":
                self.sound.play("creak", 0.6)
                self._creak = self.rng.uniform(1.6, 2.6)
        if self.kind == "confetti":
            acc["confetti"] += dt * 34
            n = int(acc["confetti"]); acc["confetti"] -= n
            p.confetti_fall(n)


# -------------------------------------------------------------------------------- #
class Bubbles:
    """Speech bubbles for the cheering crowd."""

    def __init__(self):
        self.items = []

    def say(self, text, x, y, dur=2.2, color=RED, key=None):
        if key is not None:
            self.items = [b for b in self.items if b["key"] != key]
        self.items.append(dict(text=text, x=x, y=y, t=0.0, dur=dur, color=color, key=key))

    def clear(self):
        self.items = []

    def update(self, dt):
        for b in self.items:
            b["t"] += dt
        self.items = [b for b in self.items if b["t"] < b["dur"]]

    def draw(self, surf):
        for b in self.items:
            t = b["t"]
            if t > b["dur"] - 0.2 and int(t * 20) % 2:
                continue
            w = text_width(b["text"]) + 10
            h = 13
            bob = int(math.sin(t * 9) * 1.5) if t < 0.6 else 0
            pop = min(1.0, t / 0.12)
            ww = max(8, int(w * pop))
            x = int(b["x"] - ww // 2)
            y = int(b["y"]) + bob
            x = max(2, min(W - ww - 2, x))
            panel(surf, (x, y, ww, h), CREAM, OUTLINE, WHITE, (220, 200, 160))
            # tail
            tx = x + ww // 2
            surf.fill(OUTLINE, (tx - 2, y + h - 1, 5, 1))
            surf.fill(CREAM, (tx - 1, y + h - 1, 3, 1))
            surf.fill(OUTLINE, (tx - 1, y + h, 3, 1))
            surf.fill(CREAM, (tx, y + h, 1, 1))
            surf.fill(OUTLINE, (tx, y + h + 1, 1, 1))
            if pop >= 1.0:
                draw_text(surf, b["text"], x + ww // 2, y + 3, b["color"], 1, align="center")
