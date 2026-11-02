"""Player: climbing, stamina, balance and slipping."""
import math
import random
from settings import *

EXT_GAIN = 2.2          # how strongly pole sway shakes the balance meter
NOISE_TAU = 0.9
NOISE_SIGMA = 1.6
WOBBLE = 0.45           # extra wobble while actively climbing


class Input:
    __slots__ = ("up", "down", "left", "right")

    def __init__(self, up=False, down=False, left=False, right=False):
        self.up, self.down, self.left, self.right = up, down, left, right


class Player:
    def __init__(self, idx, name, pole_x, keymaps, loadout, rng=None):
        self.idx = idx                  # 1 or 2
        self.name = name
        self.pole_x = pole_x
        self.keymaps = keymaps          # list of dicts {up, down, left, right} (pygame keys)
        self.loadout = loadout
        self.rng = rng or random.Random()
        self.reset()

    def reset(self):
        self.h = 0.0
        self.stamina = STAMINA_MAX
        self.balance = 0.0
        self.bvel = 0.0
        self.noise = 0.0
        self.state = "idle"            # idle climb down slip grab victory defeat
        self.slip_t = 0.0
        self.edge_t = 0.0
        self.grace = 0.0
        self.slips = 0
        self.danger_time = 0.0
        self.anim_t = 0.0
        self.climb_phase = 0.0
        self.step_count = 0
        self.events = []
        self.finish_time = None
        self.moving_up = False
        self.exhausted = False
        self.near_top_said = False

    # -- input ----------------------------------------------------------------------
    def read_input(self, keys):
        inp = Input()
        for km in self.keymaps:
            inp.up |= bool(keys[km["up"]])
            inp.down |= bool(keys[km["down"]])
            inp.left |= bool(keys[km["left"]])
            inp.right |= bool(keys[km["right"]])
        return inp

    def bot_input(self, bamboo):
        inp = Input()
        inp.up = self.stamina > 15
        if self.balance > 0.2:
            inp.left = True
        elif self.balance < -0.2:
            inp.right = True
        return inp
    
    # -- helpers ---------------------------------------------------------------------
    @property
    def progress(self):
        return max(0.0, min(1.0, self.h / TOP_H))

    @property
    def danger(self):
        return abs(self.balance) > BAL_DANGER

    def stamina_factor(self):
        s = self.stamina
        if s >= STAMINA_LOW:
            return 1.0
        return STAMINA_MIN_FACTOR + (1.0 - STAMINA_MIN_FACTOR) * (s / STAMINA_LOW)

    def kick(self, v):
        self.bvel += v

    def pop_events(self):
        ev, self.events = self.events, []
        return ev

    # -- main update ---------------------------------------------------------------------
    def update(self, dt, inp, env, bamboo, t, active=True):
        self.anim_t += dt
        if self.state in ("grab", "victory", "defeat"):
            return
        if not active:
            inp = Input()
        if self.state == "slip":
            self.slip_t -= dt
            self.h = max(0.0, self.h - self._slip_speed * dt)
            self.balance += (0.0 - self.balance) * min(1.0, dt * 5.0)
            self.bvel *= max(0.0, 1.0 - 6.0 * dt)
            self.stamina = min(STAMINA_MAX, self.stamina + 6.0 * dt)
            if self.slip_t <= 0:
                self.state = "idle"
                self.grace = 0.8
            return

        climbing = inp.up and not inp.down
        going_down = inp.down and not inp.up and self.h > 0
        f = self.stamina_factor()

        # ---- movement ------------------------------------------------------------------
        speed = 0.0
        if climbing:
            speed = CLIMB_SPEED * f * env.climb_mult
            if self.danger:
                speed *= 0.55
            self.h += speed * dt
            self.state = "climb"
            self.climb_phase += dt * (3.0 + 5.0 * f)
            step = int(self.climb_phase * 0.5)
            if step != self.step_count:
                self.step_count = step
                self.events.append("step")
        elif going_down:
            self.h = max(0.0, self.h - DOWN_SPEED * dt)
            self.state = "down"
            self.climb_phase -= dt * 6.0
        else:
            self.state = "idle"
            if self.h > 0:                     # greased pole: resting slides you down a little
                slide = GREASE_SLIDE + env.slide_extra + (4.0 if self.danger else 0.0)
                self.h = max(0.0, self.h - slide * dt)
        self.moving_up = climbing

        # ---- stamina -------------------------------------------------------------------
        if climbing:
            self.stamina += (-STAMINA_DRAIN * f + STAMINA_SLOW_RECOVER * (1.0 - f)) * dt
        elif going_down:
            self.stamina += STAMINA_REST_DOWN * dt
        else:
            self.stamina += STAMINA_REST * dt
        self.stamina = max(0.0, min(STAMINA_MAX, self.stamina))
        if self.stamina <= 0.5:
            self.exhausted = True
        elif self.stamina > 25:
            self.exhausted = False

        # ---- balance -----------------------------------------------------------------------
        hf = max(0.0, min(1.0, self.h / POLE_H))
        ext = bamboo.push(self.h) * EXT_GAIN + env.push_bias
        sigma = NOISE_SIGMA * (0.5 + 0.5 * hf) * env.noise_mult
        self.noise += (-self.noise / NOISE_TAU) * dt + sigma * math.sqrt(2.0 / NOISE_TAU * dt) * self.rng.gauss(0, 1)
        acc = ext + self.noise
        if climbing:
            acc += WOBBLE * math.sin(self.climb_phase * math.pi)
        u = (1 if inp.right else 0) - (1 if inp.left else 0)
        acc += u * BAL_CONTROL
        acc += -BAL_SPRING * self.balance - BAL_DAMP * self.bvel
        self.bvel += acc * dt
        self.balance += self.bvel * dt
        if abs(self.balance) >= 1.0:
            self.balance = math.copysign(1.0, self.balance)
            if self.bvel * self.balance > 0:
                self.bvel = 0.0
        if self.grace > 0:
            self.grace -= dt
        if self.danger:
            self.danger_time += dt

        if abs(self.balance) >= 0.98 and self.grace <= 0:
            self.edge_t += dt
            if self.edge_t >= BAL_EDGE_GRACE and self.h > 8:
                self._slip(env)
                return
        else:
            self.edge_t = max(0.0, self.edge_t - dt * 2.0)

        # ---- flag! ---------------------------------------------------------------------------
        if self.h >= TOP_H:
            self.h = TOP_H
            self.state = "grab"
            self.events.append("grab")

    def _slip(self, env):
        dist = min(self.h, SLIP_DIST * (1.0 + 0.1 * env.rain))
        self._slip_speed = dist / SLIP_TIME
        self.slip_t = SLIP_TIME
        self.state = "slip"
        self.slips += 1
        self.edge_t = 0.0
        self.balance *= 0.3
        self.bvel = 0.0
        self.events.append("slip")

    # -- presentation --------------------------------------------------------------------------
    def pose(self):
        """(pose_name, frame) for sprites.get_sprite."""
        s = self.state
        if s == "slip":
            return "slip", int(self.anim_t * 10) % 2
        if s == "victory":
            return "win", int(self.anim_t * 6) % 2
        if s == "grab":
            return "win", 0
        if s == "defeat":
            return "lose", int(self.anim_t * 2) % 2
        if s in ("climb", "down"):
            return "climb", int(self.climb_phase) % 4
        if self.stamina < 25:
            return "tired", int(self.anim_t * 3) % 2
        return "idle", int(self.anim_t * 2) % 2

    def lean(self):
        return int(round(self.balance * 2.0))

    def screen_x(self, bamboo):
        wob = 0
        if self.danger and self.state != "slip":
            wob = 1 if int(self.anim_t * 18) % 2 else -1
        return self.pole_x + bamboo.offset(self.h) + wob
