"""Application shell: window, scaling, scene stack, fade transitions."""
import pygame
from settings import *
from save_system import SaveSystem
from sound import SoundManager


class App:
    def __init__(self):
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption(GAME_TITLE)
        self.save = SaveSystem()
        self.fullscreen = bool(self.save.settings.get("fullscreen", False))
        self.window = None
        self._set_display()
        self.canvas = pygame.Surface((W, H))
        self._scaled = None
        self.view = (0, 0, 1.0)
        self.clock = pygame.time.Clock()
        self.sound = SoundManager(self.save.settings)
        self.scenes = []
        self.running = True
        self.thumbs = {}
        self.fade = 0.0            # 0 clear .. 1 black
        self.fade_dir = 0
        self.pending = None
        self.mouse_t = 99.0
        self.mouse_pos = (0, 0)
        pygame.mouse.set_visible(False)

    # -- display -------------------------------------------------------------------------
    def _desktop(self):
        try:
            return pygame.display.get_desktop_sizes()[0]
        except Exception:
            info = pygame.display.Info()
            return info.current_w, info.current_h

    def _set_display(self):
        if self.fullscreen:
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            dw, dh = self._desktop()
            k = 3
            while k > 1 and (W * k > dw - 40 or H * k > dh - 90):
                k -= 1
            self.window = pygame.display.set_mode((W * k, H * k), pygame.RESIZABLE)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.save.settings["fullscreen"] = self.fullscreen
        self._set_display()
        self._scaled = None

    # -- scenes -----------------------------------------------------------------------------
    def push(self, scene):
        scene.enter()
        self.scenes.append(scene)

    def pop(self):
        if self.scenes:
            old = self.scenes.pop()
            if hasattr(old, "leave"):
                old.leave()

    def goto(self, scene):
        """Replace the whole stack with `scene`, with a quick fade."""
        self.pending = scene
        self.fade_dir = 1

    def _swap(self):
        for s in self.scenes:
            if hasattr(s, "leave"):
                s.leave()
        self.scenes = []
        self.push(self.pending)
        self.pending = None
        self.fade_dir = -1

    # -- main loop ----------------------------------------------------------------------------
    def _map_mouse(self, ev):
        x, y, k = self.view
        px, py = ev.pos
        pos = (int((px - x) / k), int((py - y) / k))
        d = dict(ev.dict)
        d["pos"] = pos
        self.mouse_pos = pos
        self.mouse_t = 0.0
        return pygame.event.Event(ev.type, d)

    def start(self):
        from menu import MainMenu
        self.push(MainMenu(self))
        self.sound.apply_settings()

    def frame(self, dt):
        """One step of the main loop (events, update, fade, draw)."""
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_F11:
                self.toggle_fullscreen()
            elif ev.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                ev = self._map_mouse(ev)
                if self.scenes and self.fade_dir == 0:
                    self.scenes[-1].handle_event(ev)
            elif self.scenes and self.fade_dir == 0:
                self.scenes[-1].handle_event(ev)
        if self.scenes:
            self.scenes[-1].update(dt)
        self.mouse_t += dt
        if self.fade_dir > 0:
            self.fade = min(1.0, self.fade + dt / 0.18)
            if self.fade >= 1.0:
                self._swap()
        elif self.fade_dir < 0:
            self.fade = max(0.0, self.fade - dt / 0.22)
            if self.fade <= 0.0:
                self.fade_dir = 0
        self._draw()

    def run(self):
        self.start()
        while self.running:
            self.frame(min(self.clock.tick(FPS) / 1000.0, 0.05))
        self.save.save()
        pygame.quit()

    def _draw(self):
        c = self.canvas
        start = len(self.scenes) - 1
        while start > 0 and self.scenes[start].overlay:
            start -= 1
        for s in self.scenes[start:]:
            s.draw(c)
        top = self.scenes[-1] if self.scenes else None
        if self.mouse_t < 3.0 and not getattr(top, "hide_cursor", False):
            mx, my = self.mouse_pos
            pygame.draw.polygon(c, OUTLINE, [(mx - 1, my - 1), (mx + 8, my + 5), (mx + 4, my + 6), (mx + 6, my + 11), (mx + 3, my + 12), (mx + 1, my + 7), (mx - 1, my + 10)])
            pygame.draw.polygon(c, WHITE, [(mx, my), (mx + 6, my + 5), (mx + 3, my + 5), (mx + 5, my + 9), (mx + 3, my + 10), (mx + 1, my + 6), (mx, my + 8)])
        if self.fade > 0:
            ov = pygame.Surface((W, H))
            ov.set_alpha(int(255 * self.fade))
            c.blit(ov, (0, 0))
        win = pygame.display.get_surface()
        ww, wh = win.get_size()
        k = min(ww / W, wh / H)
        if k >= 1:
            k = int(k)
        size = (max(1, int(W * k)), max(1, int(H * k)))
        x, y = (ww - size[0]) // 2, (wh - size[1]) // 2
        self.view = (x, y, k)
        if self._scaled is None or self._scaled.get_size() != size:
            self._scaled = pygame.Surface(size)
        win.fill((0, 0, 0))
        pygame.transform.scale(c, size, self._scaled)
        win.blit(self._scaled, (x, y))
        pygame.display.flip()
