"""Camera that keeps both climbers in view whenever possible."""
import math
import random
from settings import *


class Camera:
    def __init__(self):
        self.y = 0.0
        self.shake_t = 0.0
        self.shake_amp = 0.0
        self._rng = random.Random(3)

    def target_for(self, heights):
        """Camera height (world y at the ground line). Keeps everybody in frame if possible."""
        if not heights:
            return 0.0
        lo, hi = min(heights), max(heights)
        mid = (lo + hi) / 2.0
        want = mid - 62.0
        cam_min = hi - 96.0     # leader's feet stay below the HUD / banner (screen y >= 80)
        cam_max = lo + 24.0     # trailing player's feet stay on screen (screen y <= 200)
        if cam_min <= cam_max:
            want = max(cam_min, min(cam_max, want))
        else:                   # too far apart: follow the leader
            want = cam_min
        return max(0.0, min(MAX_CAM, want))

    def update(self, dt, heights):
        tgt = self.target_for(heights)
        k = 1.0 - math.exp(-3.5 * dt)
        self.y += (tgt - self.y) * k
        if self.shake_t > 0:
            self.shake_t -= dt

    def snap(self, heights):
        self.y = self.target_for(heights)

    def shake(self, amp=2.0, dur=0.4):
        self.shake_amp = amp
        self.shake_t = dur

    def shake_offset(self):
        if self.shake_t <= 0:
            return 0, 0
        a = self.shake_amp * min(1.0, self.shake_t / 0.3)
        return int(self._rng.uniform(-a, a)), int(self._rng.uniform(-a, a))
