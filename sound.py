"""Procedurally generated sound effects and music (original - no copyrighted audio).

Sounds are synthesised once and cached as WAV files in assets/sounds/, so the
game is fully offline and starts instantly on later runs.
"""
import math
import os
import random
import struct
import tempfile
import wave

import pygame
from settings import BASE_DIR

RATE = 22050
SOUND_DIR = os.path.join(BASE_DIR, "assets", "sounds")
_rng = random.Random(7)


# ---------------------------------------------------------------- synthesis --
def _synth(dur, f0, f1=None, wave_type="square", vol=0.4, attack=0.004, power=1.6, duty=0.5, vib=0.0):
    n = max(1, int(dur * RATE))
    f1 = f0 if f1 is None else f1
    out = []
    phase = 0.0
    for i in range(n):
        t = i / n
        f = f0 + (f1 - f0) * t
        if vib:
            f *= 1.0 + vib * math.sin(i / RATE * 40.0)
        phase += f / RATE
        p = phase % 1.0
        if wave_type == "square":
            s = 1.0 if p < duty else -1.0
        elif wave_type == "tri":
            s = 4.0 * abs(p - 0.5) - 1.0
        elif wave_type == "saw":
            s = 2.0 * p - 1.0
        elif wave_type == "sine":
            s = math.sin(6.2831853 * p)
        else:
            s = _rng.uniform(-1, 1)
        a = min(1.0, (i / RATE) / attack) if attack > 0 else 1.0
        out.append(s * vol * a * (1.0 - t) ** power)
    return out


def _noise(dur, vol=0.3, smooth=0.0, hp=False, power=1.0, shape=None):
    n = int(dur * RATE)
    out = []
    lp = 0.0
    for i in range(n):
        x = _rng.uniform(-1, 1)
        lp += (x - lp) * (1.0 - smooth) if smooth else x - lp
        v = (x - lp) if hp else lp
        t = i / n
        env = (1.0 - t) ** power if shape is None else shape(t)
        out.append(v * vol * env)
    return out


def _mix(*tracks):
    """tracks: lists of samples or (offset_seconds, samples)"""
    parts = [(0.0, t) if isinstance(t, list) else t for t in tracks]
    length = max(int(o * RATE) + len(s) for o, s in parts)
    out = [0.0] * length
    for o, s in parts:
        off = int(o * RATE)
        for i, v in enumerate(s):
            out[off + i] += v
    return out


def _seq(notes, wave_type="square", vol=0.3, gap=0.0, **kw):
    """notes: [(freq or 0, seconds)] -> concatenated samples"""
    out = []
    for f, d in notes:
        if f <= 0:
            out.extend([0.0] * int(d * RATE))
        else:
            out.extend(_synth(max(0.01, d - gap), f, f, wave_type, vol, **kw))
            out.extend([0.0] * int(gap * RATE))
    return out


def _hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def _write_wav(path, samples):
    peak = max(1e-6, max(abs(s) for s in samples))
    scale = 32000 * min(1.0, 0.95 / peak)
    data = struct.pack("<%dh" % len(samples), *[int(max(-32000, min(32000, s * scale))) for s in samples])
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(data)


# ------------------------------------------------------------------ effects --
def _gen_click():
    return _synth(0.06, 1300, 950, "square", 0.35, power=1.2)


def _gen_move():
    return _synth(0.035, 760, 760, "square", 0.22, power=1.0)


def _gen_back():
    return _seq([(660, 0.05), (440, 0.07)], "square", 0.3)


def _gen_error():
    return _synth(0.2, 170, 110, "saw", 0.4, power=1.0)


def _gen_tok():  # hollow bamboo knock while climbing
    return _mix(_synth(0.09, 430, 230, "sine", 0.6, attack=0.001, power=3.0),
                _noise(0.04, 0.12, smooth=0.6, power=2.0))


def _gen_creak():  # bamboo creaking in the wind
    return _mix(_synth(0.45, 150, 95, "saw", 0.16, attack=0.05, power=1.0, vib=0.06),
                _synth(0.45, 300, 200, "tri", 0.07, attack=0.08, power=1.0, vib=0.05))


def _gen_wind():
    dur = 2.4
    return _noise(dur, 0.65, smooth=0.93, shape=lambda t: math.sin(math.pi * t) ** 2 * 0.8 + 0.2 * math.sin(math.pi * t))


def _gen_rain():
    dur = 1.6
    fade = 0.05
    s = _noise(dur, 0.32, smooth=0.55, hp=True, power=0.0)
    n = len(s)
    k = int(fade * RATE)
    for i in range(k):
        s[i] *= i / k
        s[n - 1 - i] *= i / k
    return s


def _gen_slip():
    return _mix(_synth(0.38, 820, 170, "tri", 0.4, power=0.8),
                (0.30, _noise(0.12, 0.35, smooth=0.7, power=2.0)))


def _gen_flag():
    fan = _seq([(_hz(72), 0.08), (_hz(76), 0.08), (_hz(79), 0.08), (_hz(84), 0.42)], "square", 0.28, power=0.6)
    body = _seq([(_hz(60), 0.08), (_hz(64), 0.08), (_hz(67), 0.08), (_hz(72), 0.42)], "tri", 0.35, power=0.6)
    return _mix(fan, body)


def _gen_cheer():
    dur = 1.6
    crack = []
    for i in range(int(dur * RATE)):
        t = i / (dur * RATE)
        env = min(1.0, t / 0.08) * (1.0 - t) ** 0.7
        crack.append((_rng.uniform(-1, 1) if _rng.random() < 0.28 else 0.0) * env * 0.85)
    lp, sm = 0.0, []
    for v in crack:
        lp += (v - lp) * 0.35
        sm.append(lp)
    voice = _mix(_synth(dur, 262, 300, "saw", 0.05, attack=0.1, power=0.9, vib=0.03),
                 _synth(dur, 392, 440, "saw", 0.04, attack=0.1, power=0.9, vib=0.04))
    return _mix(sm, voice)


def _gen_victory():
    mel = [(67, .12), (72, .12), (76, .12), (79, .2), (76, .1), (79, .1), (84, .5), (0, .1), (79, .12), (84, .7)]
    lead = _seq([(_hz(m) if m else 0, d) for m, d in mel], "square", 0.28, gap=0.015, power=0.7)
    bass = _seq([(_hz(48), .36), (_hz(53), .36), (_hz(55), .36), (_hz(48), .9)], "tri", 0.4, power=0.5)
    return _mix(lead, bass)


def _gen_coin():
    return _seq([(_hz(83), 0.06), (_hz(88), 0.22)], "square", 0.28, power=1.4)


def _gen_beep():
    return _synth(0.14, 660, 660, "square", 0.32, power=0.6)


def _gen_go():
    return _synth(0.45, 990, 990, "square", 0.34, power=0.9)


def _gen_pop():
    return _mix(_noise(0.14, 0.4, smooth=0.5, power=2.5), _synth(0.14, 320, 980, "sine", 0.3, power=2.0))


def _gen_sad():
    return _seq([(_hz(64), 0.16), (_hz(62), 0.16), (_hz(60), 0.3)], "tri", 0.4, power=0.8)


def _gen_music():
    """Original 8-bar fiesta loop (C major, ~132 BPM): arpeggio lead, oom-pah bass, shaker."""
    bpm = 132.0
    beat = 60.0 / bpm
    eighth = beat / 2
    C, D, E, F, G, A, B = 0, 2, 4, 5, 7, 9, 11

    def n(name, octave):
        return 12 * (octave + 1) + name

    bars = [
        [n(E, 5), n(G, 5), n(E, 5), n(C, 5), n(E, 5), n(G, 5), n(C, 6), n(G, 5)],
        [n(F, 5), n(A, 5), n(F, 5), n(C, 5), n(F, 5), n(A, 5), n(C, 6), n(A, 5)],
        [n(G, 5), n(B, 5), n(G, 5), n(D, 5), n(G, 5), n(B, 5), n(D, 6), n(B, 5)],
        [n(E, 5), n(C, 5), n(E, 5), n(G, 5), n(C, 6), 0, n(C, 6), 0],
        [n(E, 5), n(A, 5), n(E, 5), n(C, 5), n(E, 5), n(A, 5), n(C, 6), n(A, 5)],
        [n(F, 5), n(C, 6), n(A, 5), n(F, 5), n(A, 5), n(C, 6), n(A, 5), n(F, 5)],
        [n(D, 5), n(G, 5), n(B, 5), n(D, 6), n(B, 5), n(G, 5), n(D, 5), n(B, 4)],
        [n(C, 6), n(G, 5), n(E, 5), n(G, 5), n(C, 6), 0, n(C, 6), 0],
    ]
    roots = [(C, G), (F, C), (G, D), (C, G), (A, E), (F, C), (G, D), (C, G)]
    lead, bass, perc = [], [], []
    for bi, bar in enumerate(bars):
        for m in bar:
            if m == 0:
                lead.extend([0.0] * int(eighth * RATE))
            else:
                lead.extend(_synth(eighth * 0.92, _hz(m), _hz(m), "square", 0.16, duty=0.25, power=1.0))
                lead.extend([0.0] * (int(eighth * RATE) - int(eighth * 0.92 * RATE)))
        r, fifth = roots[bi]
        for k in range(4):
            note = n(r, 2) if k % 2 == 0 else n(fifth, 2)
            bass.extend(_synth(beat * 0.85, _hz(note), _hz(note), "tri", 0.34, power=1.0))
            bass.extend([0.0] * (int(beat * RATE) - int(beat * 0.85 * RATE)))
        for k in range(8):
            hit = _noise(0.03, 0.10 if k % 2 == 0 else 0.06, smooth=0.3, hp=True, power=2.0)
            perc.extend(hit + [0.0] * (int(eighth * RATE) - len(hit)))
    return _mix(lead, bass, perc)


GENERATORS = {
    "click": _gen_click, "move": _gen_move, "back": _gen_back, "error": _gen_error,
    "tok": _gen_tok, "creak": _gen_creak, "wind": _gen_wind, "rain": _gen_rain,
    "slip": _gen_slip, "flag": _gen_flag, "cheer": _gen_cheer, "victory": _gen_victory,
    "coin": _gen_coin, "beep": _gen_beep, "go": _gen_go, "pop": _gen_pop, "sad": _gen_sad,
    "music": _gen_music,
}
VOLUMES = {"click": 0.7, "move": 0.5, "back": 0.6, "error": 0.6, "tok": 0.55, "creak": 0.5, "wind": 0.55,
           "rain": 0.45, "slip": 0.7, "flag": 0.8, "cheer": 0.7, "victory": 0.8, "coin": 0.6, "beep": 0.6,
           "go": 0.7, "pop": 0.6, "sad": 0.6, "music": 0.32}
CH_MUSIC, CH_WIND, CH_RAIN = 0, 1, 2


class SoundManager:
    """Loads (or generates) every sound and honours the MUSIC / SFX settings."""

    def __init__(self, settings):
        self.settings = settings
        self.sounds = {}
        self.enabled = False
        self._loops = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(RATE, -16, 1, 512)
            pygame.mixer.set_num_channels(20)
            pygame.mixer.set_reserved(3)
            self.enabled = True
        except Exception:
            return
        folder = SOUND_DIR
        try:
            os.makedirs(folder, exist_ok=True)
            if not os.access(folder, os.W_OK):
                raise OSError
        except OSError:
            folder = tempfile.mkdtemp(prefix="palosebo_snd_")
        for name, gen in GENERATORS.items():
            path = os.path.join(folder, name + ".wav")
            try:
                if not os.path.exists(path):
                    _write_wav(path, gen())
                snd = pygame.mixer.Sound(path)
                snd.set_volume(VOLUMES.get(name, 0.6))
                self.sounds[name] = snd
            except Exception:
                pass

    # -- one shots -----------------------------------------------------------
    def play(self, name, volume=1.0):
        if not (self.enabled and self.settings.get("sfx", True)):
            return
        snd = self.sounds.get(name)
        if snd:
            ch = snd.play()
            if ch is not None and volume != 1.0:
                ch.set_volume(volume)

    # -- loops (wind / rain) --------------------------------------------------
    def loop_start(self, name):
        if not (self.enabled and self.settings.get("sfx", True)) or name in self._loops:
            return
        snd = self.sounds.get(name)
        if snd:
            ch = pygame.mixer.Channel(CH_WIND if name == "wind" else CH_RAIN)
            ch.play(snd, loops=-1)
            self._loops[name] = ch

    def loop_stop(self, name):
        ch = self._loops.pop(name, None)
        if ch:
            ch.stop()

    def stop_loops(self):
        for name in list(self._loops):
            self.loop_stop(name)

    # -- music ------------------------------------------------------------------
    def music_start(self):
        if not (self.enabled and self.settings.get("music", True)):
            return
        snd = self.sounds.get("music")
        ch = pygame.mixer.Channel(CH_MUSIC)
        if snd and not ch.get_busy():
            ch.play(snd, loops=-1)
            ch.set_volume(self.settings.get("music_vol", 1.0))

    def music_stop(self):
        if self.enabled:
            pygame.mixer.Channel(CH_MUSIC).stop()

    def music_duck(self, quiet=True):
        if self.enabled:
            pygame.mixer.Channel(CH_MUSIC).set_volume((0.35 if quiet else 1.0) * self.settings.get("music_vol", 1.0))
    def music_set_volume(self):
        if self.enabled:
            pygame.mixer.Channel(CH_MUSIC).set_volume(self.settings.get("music_vol", 1.0))

    def apply_settings(self):
        if self.settings.get("music", True):
            self.music_start()
        else:
            self.music_stop()
        if not self.settings.get("sfx", True):
            self.stop_loops()
            if self.enabled:
                for i in range(3, 20):
                    pygame.mixer.Channel(i).stop()
