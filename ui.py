"""Scene base class and keyboard + mouse driven button menus."""
import pygame
from gfx import draw_button, panel
from pixelfont import draw_text, text_width
from settings import *

KEYS_UP = (pygame.K_UP, pygame.K_w)
KEYS_DOWN = (pygame.K_DOWN, pygame.K_s)
KEYS_LEFT = (pygame.K_LEFT, pygame.K_a)
KEYS_RIGHT = (pygame.K_RIGHT, pygame.K_d)
KEYS_OK = (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER)


class Scene:
    """Every screen (menu, shop, match...) derives from this."""
    overlay = False          # draw the scene below first (pause menu)

    def __init__(self, app):
        self.app = app

    def enter(self):
        pass

    def handle_event(self, ev):
        pass

    def update(self, dt):
        pass

    def draw(self, surf):
        pass

    # shortcuts
    def sfx(self, name, vol=1.0):
        self.app.sound.play(name, vol)


class ButtonMenu:
    """A grid of buttons. `activate()` returns the index that was chosen (or None)."""

    def __init__(self, labels, x, y, w, h, gap=4, cols=1, scale=1):
        self.items = []
        self.cols = cols
        self.index = 0
        self.scale = scale
        for i, lab in enumerate(labels):
            c, r = i % cols, i // cols
            self.items.append(dict(label=lab, rect=pygame.Rect(x + c * (w + gap), y + r * (h + gap), w, h), enabled=True))
        self.pressed = -1

    def set_label(self, i, label):
        self.items[i]["label"] = label

    def _move(self, dx, dy):
        n = len(self.items)
        i = self.index
        if dx:
            i = (i + dx) % n
        if dy:
            j = i + dy * self.cols
            if 0 <= j < n:
                i = j
            else:
                col = i % self.cols
                rows = (n + self.cols - 1) // self.cols
                r = (i // self.cols + dy) % rows
                j = r * self.cols + col
                i = j if j < n else n - 1
        moved = i != self.index
        self.index = i
        return moved

    def handle_event(self, ev, sound=None):
        """Returns chosen index or None."""
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            moved = False
            if k in KEYS_UP:
                moved = self._move(0, -1)
            elif k in KEYS_DOWN:
                moved = self._move(0, 1)
            elif k in KEYS_LEFT:
                moved = self._move(-1, 0) if self.cols > 1 else False
            elif k in KEYS_RIGHT:
                moved = self._move(1, 0) if self.cols > 1 else False
            elif k in KEYS_OK:
                return self._choose(sound)
            if moved and sound:
                sound.play("move")
        elif ev.type == pygame.MOUSEMOTION:
            for i, it in enumerate(self.items):
                if it["rect"].collidepoint(ev.pos) and i != self.index:
                    self.index = i
                    if sound:
                        sound.play("move")
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for i, it in enumerate(self.items):
                if it["rect"].collidepoint(ev.pos):
                    self.index = i
                    return self._choose(sound)
        return None

    def _choose(self, sound):
        if not self.items[self.index]["enabled"]:
            if sound:
                sound.play("error")
            return None
        if sound:
            sound.play("click")
        return self.index

    def draw(self, surf, t=0.0):
        for i, it in enumerate(self.items):
            sel = i == self.index
            r = it["rect"]
            draw_button(surf, (r.x, r.y - (1 if sel else 0), r.w, r.h), it["label"], selected=sel,
                        disabled=not it["enabled"], scale=self.scale)
            if sel and it["enabled"]:
                bob = 1 if int(t * 4) % 2 else 0
                draw_text(surf, ">", r.x - 8 + bob, r.y + (r.h - 8) // 2, YELLOW, 1, shadow=OUTLINE)
                draw_text(surf, "<", r.right + 3 - bob, r.y + (r.h - 8) // 2, YELLOW, 1, shadow=OUTLINE)


def draw_title(surf, t, cx, y, scale=4):
    """Bouncing multicolour PALOSEBO logo."""
    word = "PALOSEBO"
    cols = [RED, ORANGE, YELLOW, LIME, TEAL, SKY, PINK, YELLOW]
    total = text_width(word, scale) + (len(word) - 1) * scale
    x = cx - total // 2
    for i, ch in enumerate(word):
        bob = int(round(__import__("math").sin(t * 3 + i * 0.7) * 2))
        w = draw_text(surf, ch, x, y + bob, cols[i], scale, shadow=OUTLINE, outline=OUTLINE)
        x += w + scale
    # ribbon
    rw = text_width("FIESTA CLIMB", 2) + 26
    rx = cx - rw // 2
    ry = y + 7 * scale + 8
    panel(surf, (rx, ry, rw, 16), RED, OUTLINE)
    surf.fill(YELLOW, (rx + 3, ry + 3, 2, 10)); surf.fill(YELLOW, (rx + rw - 5, ry + 3, 2, 10))
    draw_text(surf, "FIESTA CLIMB", cx, ry + 1, CREAM, 2, shadow=DKRED, align="center")


def dim(surf, alpha=140):
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((10, 8, 30, alpha))
    surf.blit(ov, (0, 0))
