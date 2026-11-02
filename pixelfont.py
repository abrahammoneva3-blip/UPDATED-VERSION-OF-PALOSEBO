"""A tiny built-in 5x7 bitmap font so every piece of text is real pixel art."""
import pygame

_RAW = """
A
.###.
#...#
#...#
#####
#...#
#...#
#...#

B
####.
#...#
#...#
####.
#...#
#...#
####.

C
.###.
#...#
#....
#....
#....
#...#
.###.

D
####.
#...#
#...#
#...#
#...#
#...#
####.

E
#####
#....
#....
####.
#....
#....
#####

F
#####
#....
#....
####.
#....
#....
#....

G
.###.
#...#
#....
#.###
#...#
#...#
.###.

H
#...#
#...#
#...#
#####
#...#
#...#
#...#

I
.###.
..#..
..#..
..#..
..#..
..#..
.###.

J
..###
...#.
...#.
...#.
...#.
#..#.
.##..

K
#...#
#..#.
#.#..
##...
#.#..
#..#.
#...#

L
#....
#....
#....
#....
#....
#....
#####

M
#...#
##.##
#.#.#
#.#.#
#...#
#...#
#...#

N
#...#
##..#
#.#.#
#..##
#...#
#...#
#...#

O
.###.
#...#
#...#
#...#
#...#
#...#
.###.

P
####.
#...#
#...#
####.
#....
#....
#....

Q
.###.
#...#
#...#
#...#
#.#.#
#..#.
.##.#

R
####.
#...#
#...#
####.
#.#..
#..#.
#...#

S
.####
#....
#....
.###.
....#
....#
####.

T
#####
..#..
..#..
..#..
..#..
..#..
..#..

U
#...#
#...#
#...#
#...#
#...#
#...#
.###.

V
#...#
#...#
#...#
#...#
#...#
.#.#.
..#..

W
#...#
#...#
#...#
#.#.#
#.#.#
##.##
#...#

X
#...#
#...#
.#.#.
..#..
.#.#.
#...#
#...#

Y
#...#
#...#
.#.#.
..#..
..#..
..#..
..#..

Z
#####
....#
...#.
..#..
.#...
#....
#####

0
.###.
#...#
#..##
#.#.#
##..#
#...#
.###.

1
..#..
.##..
..#..
..#..
..#..
..#..
.###.

2
.###.
#...#
....#
...#.
..#..
.#...
#####

3
####.
....#
....#
.###.
....#
....#
####.

4
...#.
..##.
.#.#.
#..#.
#####
...#.
...#.

5
#####
#....
####.
....#
....#
#...#
.###.

6
.###.
#....
#....
####.
#...#
#...#
.###.

7
#####
....#
...#.
..#..
.#...
.#...
.#...

8
.###.
#...#
#...#
.###.
#...#
#...#
.###.

9
.###.
#...#
#...#
.####
....#
....#
.###.

.
.....
.....
.....
.....
.....
.##..
.##..

,
.....
.....
.....
.....
.##..
..#..
.#...

!
..#..
..#..
..#..
..#..
..#..
.....
..#..

?
.###.
#...#
....#
...#.
..#..
.....
..#..

:
.....
.##..
.##..
.....
.##..
.##..
.....

-
.....
.....
.....
#####
.....
.....
.....

+
.....
..#..
..#..
#####
..#..
..#..
.....

/
....#
....#
...#.
..#..
.#...
#....
#....

'
..#..
..#..
.#...
.....
.....
.....
.....

"
.#.#.
.#.#.
.....
.....
.....
.....
.....

%
##..#
##.#.
...#.
..#..
.#...
.#.##
#..##

(
...#.
..#..
.#...
.#...
.#...
..#..
...#.

)
.#...
..#..
...#.
...#.
...#.
..#..
.#...

<
...#.
..#..
.#...
#....
.#...
..#..
...#.

>
.#...
..#..
...#.
....#
...#.
..#..
.#...

=
.....
.....
#####
.....
#####
.....
.....

*
.....
#.#.#
.###.
#####
.###.
#.#.#
.....

|
..#..
..#..
..#..
..#..
..#..
..#..
..#..

[
.###.
.#...
.#...
.#...
.#...
.#...
.###.

]
.###.
...#.
...#.
...#.
...#.
...#.
.###.

\u2190
.....
..#..
.#...
#####
.#...
..#..
.....

\u2192
.....
..#..
...#.
#####
...#.
..#..
.....

\u2191
..#..
.###.
#.#.#
..#..
..#..
..#..
..#..

\u2193
..#..
..#..
..#..
..#..
#.#.#
.###.
..#..
"""


class PixelFont:
    HEIGHT = 7

    def __init__(self):
        self.glyphs = {}
        self._tinted = {}
        self._cache = {}
        for block in _RAW.strip().split("\n\n"):
            lines = block.strip("\n").split("\n")
            ch = lines[0]
            if ch.startswith("\\u"):
                ch = chr(int(ch[2:], 16))
            rows = lines[1:8]
            used = [x for x in range(5) if any(r[x] == "#" for r in rows)]
            x0, x1 = min(used), max(used)
            surf = pygame.Surface((x1 - x0 + 1, 7), pygame.SRCALPHA)
            for y, r in enumerate(rows):
                for x in range(x0, x1 + 1):
                    if r[x] == "#":
                        surf.set_at((x - x0, y), (255, 255, 255, 255))
            self.glyphs[ch] = surf

    def _glyph(self, ch, color):
        key = (ch, color)
        g = self._tinted.get(key)
        if g is None:
            base = self.glyphs.get(ch) or self.glyphs.get(ch.upper()) or self.glyphs["?"]
            g = base.copy()
            g.fill(color + (255,), special_flags=pygame.BLEND_RGBA_MULT)
            self._tinted[key] = g
        return g

    def width(self, text, scale=1):
        best = 0
        for line in text.split("\n"):
            w = 0
            for ch in line:
                w += 3 if ch == " " else self._glyph(ch, (255, 255, 255)).get_width() + 1
            best = max(best, max(0, w - 1))
        return best * scale

    def height(self, text, scale=1):
        return (8 * (text.count("\n") + 1) - 1) * scale

    def render(self, text, color, scale=1, shadow=None, outline=None):
        key = (text, color, scale, shadow, outline)
        s = self._cache.get(key)
        if s is not None:
            return s
        if len(self._cache) > 900:
            self._cache.clear()
        lines = text.split("\n")
        w = max(1, self.width(text, 1))
        h = 8 * len(lines) - 1
        base = pygame.Surface((w, h), pygame.SRCALPHA)
        for li, line in enumerate(lines):
            x = 0
            for ch in line:
                if ch == " ":
                    x += 3
                    continue
                g = self._glyph(ch, color)
                base.blit(g, (x, li * 8))
                x += g.get_width() + 1
        if scale > 1:
            base = pygame.transform.scale(base, (w * scale, h * scale))
        pad = scale if (shadow or outline) else 0
        if pad:
            out = pygame.Surface((base.get_width() + pad * 2, base.get_height() + pad * 2), pygame.SRCALPHA)
            mask = pygame.mask.from_surface(base)
            if outline:
                sil = mask.to_surface(setcolor=outline + (255,), unsetcolor=(0, 0, 0, 0))
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)):
                    out.blit(sil, (pad + dx * pad, pad + dy * pad))
            if shadow:
                sil = mask.to_surface(setcolor=shadow + (255,), unsetcolor=(0, 0, 0, 0))
                out.blit(sil, (pad + pad, pad + pad))
            out.blit(base, (pad, pad))
            base = out
        self._cache[key] = base
        return base


FONT = PixelFont()


def text_width(s, scale=1):
    return FONT.width(s, scale)


def draw_text(surf, s, x, y, color=(255, 255, 255), scale=1, shadow=None, outline=None, align="left"):
    """Draw pixel text. (x, y) is the top-left / top-centre / top-right of the text box."""
    img = FONT.render(s, color, scale, shadow, outline)
    pad = scale if (shadow or outline) else 0
    w = FONT.width(s, scale)
    if align == "center":
        x = x - w // 2
    elif align == "right":
        x = x - w
    surf.blit(img, (int(x) - pad, int(y) - pad))
    return w
