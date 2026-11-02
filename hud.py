"""In-game HUD: stamina, balance, progress, timer, banners and countdown."""
import math
import pygame
from gfx import panel, shade, draw_key, star
from pixelfont import draw_text, text_width
import sprites
from settings import *

P1_COLOR = (255, 120, 90)
P2_COLOR = (110, 190, 255)


def _bar(surf, x, y, w, h, frac, color, back=(40, 30, 60)):
    surf.fill(OUTLINE, (x - 1, y - 1, w + 2, h + 2))
    surf.fill(back, (x, y, w, h))
    fw = int(w * max(0.0, min(1.0, frac)))
    if fw > 0:
        surf.fill(color, (x, y, fw, h))
        surf.fill(shade(color, 1.35), (x, y, fw, 1))


def draw_player_panel(surf, pl, x, y, w, t):
    tone = P1_COLOR if pl.idx == 1 else P2_COLOR
    keys = "WASD" if pl.idx == 1 else "\u2190\u2191\u2192\u2193"
    panel(surf, (x, y, w, 31), (30, 28, 70), OUTLINE)
    surf.fill(tone, (x + 3, y + 3, 4, 7))
    draw_text(surf, "PLAYER %d" % pl.idx, x + 10, y + 3, tone, 1, shadow=OUTLINE)
    draw_text(surf, keys, x + w - 5, y + 3, LTGRAY, 1, shadow=OUTLINE, align="right")
    bx, bw = x + 50, w - 56
    # stamina
    s = pl.stamina / STAMINA_MAX
    col = LIME if s > 0.5 else (YELLOW if s > 0.25 else RED)
    if s <= 0.25 and int(t * 6) % 2:
        col = shade(col, 0.6)
    draw_text(surf, "STAMINA", x + 4, y + 12, CREAM, 1)
    _bar(surf, bx, y + 13, bw, 5, s, col)
    # balance: green / yellow / red zones with a marker
    draw_text(surf, "BALANCE", x + 4, y + 21, CREAM, 1)
    by = y + 22
    surf.fill(OUTLINE, (bx - 1, by - 1, bw + 2, 7))
    zone = bw // 2
    surf.fill(RED, (bx, by, bw, 5))
    surf.fill(YELLOW, (bx + int(bw * 0.15), by, int(bw * 0.7), 5))
    surf.fill(LIME, (bx + int(bw * 0.32), by, int(bw * 0.36), 5))
    surf.fill(OUTLINE, (bx + bw // 2, by, 1, 5))
    mx = bx + bw // 2 + int(pl.balance * (bw // 2 - 1))
    danger = pl.danger
    mc = WHITE if not (danger and int(t * 10) % 2) else (255, 90, 90)
    surf.fill(OUTLINE, (mx - 1, by - 2, 3, 9))
    surf.fill(mc, (mx, by - 1, 1, 7))
    if pl.state == "slip":
        draw_text(surf, "ARAY!", x + w // 2, y + 33, RED, 1, shadow=OUTLINE, align="center")
    elif pl.exhausted and int(t * 4) % 2:
        draw_text(surf, "PAGOD!", x + w // 2, y + 33, ORANGE, 1, shadow=OUTLINE, align="center")


def draw_progress(surf, players, x, top, bottom, side, t, flag_design="araw"):
    """Slim vertical climb gauge with a marker per player."""
    surf.fill(OUTLINE, (x - 1, top - 1, 7, bottom - top + 2))
    surf.fill((44, 40, 84), (x, top, 5, bottom - top))
    for yy in range(top, bottom, 8):
        surf.fill((70, 64, 120), (x + 1, yy, 3, 1))
    for pl in players:
        tone = P1_COLOR if pl.idx == 1 else P2_COLOR
        py = int(bottom - 5 - (bottom - top - 8) * pl.progress)
        off = -3 if pl.idx == 2 else 0
        surf.fill(OUTLINE, (x - 2 + (2 if pl.idx == 1 else -2), py - 2, 9, 9)) if len(players) > 1 else surf.fill(OUTLINE, (x - 2, py - 2, 9, 9))
        cx = x + (2 if pl.idx == 1 and len(players) > 1 else (-2 if len(players) > 1 else 0))
        surf.fill(tone, (cx - 1 + 0, py - 1, 7, 7))
        draw_text(surf, str(pl.idx) if len(players) > 1 else "", cx + 3, py, OUTLINE, 1, align="center")
    star(surf, x + 2, top - 5, 3, YELLOW)


def draw_timer(surf, secs, label="TIME", best=None, t=0.0):
    w = 76
    x = W // 2 - w // 2
    panel(surf, (x, 2, w, 31), (30, 28, 70), OUTLINE)
    draw_text(surf, label, W // 2, 5, LTGRAY, 1, align="center")
    txt = "%05.2f" % secs
    draw_text(surf, txt, W // 2, 14, WHITE, 2, shadow=OUTLINE, align="center")
    if best is not None:
        draw_text(surf, "BEST %.2f" % best, W // 2, 27, YELLOW, 1, align="center")


def draw_banner(surf, banner, t):
    if not banner:
        return
    en, fil, remaining = banner
    slide = min(1.0, (3.0 - remaining) / 0.25) if remaining > 2.7 else 1.0
    out = min(1.0, remaining / 0.3)
    y = int(-26 + 26 * slide * out) + 35
    w = max(text_width(en, 2), text_width(fil)) + 22
    x = W // 2 - w // 2
    panel(surf, (x, y, w, 26), (120, 30, 60), OUTLINE)
    surf.fill(YELLOW, (x + 3, y + 2, w - 6, 1))
    draw_text(surf, en, W // 2, y + 4, WHITE, 2, shadow=OUTLINE, align="center")
    draw_text(surf, fil, W // 2, y + 18, YELLOW, 1, shadow=OUTLINE, align="center")


def draw_countdown(surf, phase_t, hint=True):
    """3-2-1-GO! Large pixel numbers. phase_t = seconds since countdown start."""
    if phase_t < 3.0:
        n = 3 - int(phase_t)
        frac = phase_t - int(phase_t)
        sc = 8 - int(frac * 3)
        col = (YELLOW, ORANGE, RED)[3 - n]
        draw_text(surf, str(n), W // 2, 58, col, sc, shadow=OUTLINE, outline=OUTLINE, align="center")
    elif phase_t < 3.8:
        draw_text(surf, "GO!", W // 2, 58, LIME, 8, shadow=OUTLINE, outline=OUTLINE, align="center")
    if hint and phase_t < 3.0:
        panel(surf, (W // 2 - 150, 118, 300, 30), (30, 28, 70), OUTLINE)
        draw_text(surf, "UMAKYAT SA KAWAYAN! KUNIN ANG BANDILA!", W // 2, 123, YELLOW, 1, shadow=OUTLINE, align="center")
        draw_text(surf, "CLIMB THE BAMBOO - GRAB THE FLAG FIRST!", W // 2, 134, WHITE, 1, shadow=OUTLINE, align="center")


def draw_key_guide(surf, idx, cx, y):
    """Little keyboard layout so nobody has to guess the controls."""
    if idx == 1:
        up, left, down, right = "W", "A", "S", "D"
        title, col = "PLAYER 1", P1_COLOR
        l1, l2 = "W S = CLIMB", "A D = BALANCE"
    else:
        up, left, down, right = "\u2191", "\u2190", "\u2193", "\u2192"
        title, col = "PLAYER 2", P2_COLOR
        l1, l2 = "\u2191 \u2193 = CLIMB", "\u2190 \u2192 = BALANCE"
    panel(surf, (cx - 42, y, 84, 62), (30, 28, 70), OUTLINE)
    draw_text(surf, title, cx, y + 4, col, 1, shadow=OUTLINE, align="center")
    draw_key(surf, cx - 5, y + 14, up, 10)
    draw_key(surf, cx - 17, y + 26, left, 10)
    draw_key(surf, cx - 5, y + 26, down, 10)
    draw_key(surf, cx + 7, y + 26, right, 10)
    draw_text(surf, l1, cx, y + 41, CREAM, 1, align="center")
    draw_text(surf, l2, cx, y + 51, YELLOW, 1, align="center")
