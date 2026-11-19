#!/usr/bin/env python3
"""news-image-20261119: draw one image summing up the world news of
Thursday 19 November 2026, and write it to /output/entry.png.

Pure Python 3 standard library (zlib, struct, os, math): the grader runs
with no network and nothing installed, so the PNG encoder and a 5x7 bitmap
font are built in here. Deterministic: no clock, no randomness, no input
files -- two runs write the same bytes.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# --- palette ---------------------------------------------------------------
PAPER = (251, 248, 241)   # warm newsprint
INK = (22, 26, 34)        # near-black text
NAVY = (16, 32, 60)       # masthead band
RED = (178, 34, 34)       # rules, lead tag
GOLD = (201, 162, 39)     # date line, accents
CARD = (255, 255, 255)    # story cards
GREY = (105, 110, 118)    # footer, captions
LINE = (205, 198, 184)    # hairlines
SKY = (168, 204, 228)     # lead illustration sky
TEAL = (14, 116, 110)     # tag: health / society
BLUE = (30, 90, 168)      # tag: diplomacy
PURPLE = (104, 64, 150)   # tag: culture / science
GREEN = (46, 125, 50)     # tag: politics
ORANGE = (196, 94, 20)    # tag: weather
BROWN = (122, 82, 42)     # tag: earth

# --- canvas ----------------------------------------------------------------
px = bytearray(W * H * 3)


def fill(color):
    px[:] = bytes(color) * (W * H)


def rect(x, y, w, h, color):
    """Filled rectangle, clipped to the canvas."""
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(color) * (x1 - x0)
    for yy in range(y0, y1):
        o = (yy * W + x0) * 3
        px[o:o + len(row)] = row


def circle(cx, cy, r, color):
    for dy in range(-r, r + 1):
        dx = int(math.sqrt(max(0, r * r - dy * dy)))
        rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)


def tri(x1, y1, x2, y2, x3, y3, color):
    """Filled triangle, scanline fill."""
    pts = sorted(((x1, y1), (x2, y2), (x3, y3)), key=lambda p: p[1])
    (ax, ay), (bx, by), (cx, cy) = pts
    if ay == cy:
        return
    for y in range(max(0, ay), min(H, cy + 1)):
        xs = []
        for (px1, py1), (px2, py2) in (((ax, ay), (bx, by)), ((bx, by), (cx, cy)), ((ax, ay), (cx, cy))):
            if py1 <= y <= py2 and py2 != py1:
                xs.append(px1 + (px2 - px1) * (y - py1) / (py2 - py1))
            elif py2 <= y <= py1 and py2 != py1:
                xs.append(px2 + (px1 - px2) * (y - py2) / (py1 - py2))
        if len(xs) >= 2:
            xa, xb = int(min(xs)), int(max(xs))
            rect(xa, y, xb - xa + 1, 1, color)


def line(x1, y1, x2, y2, color, thick=1):
    n = max(abs(x2 - x1), abs(y2 - y1), 1)
    for i in range(n + 1):
        x = int(x1 + (x2 - x1) * i / n)
        y = int(y1 + (y2 - y1) * i / n)
        rect(x - thick // 2, y - thick // 2, thick, thick, color)


# --- PNG encoder (stdlib only) ---------------------------------------------
def _chunk(typ, data):
    return (struct.pack(">I", len(data)) + typ + data +
            struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))


def encode_png():
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += px[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) +
            _chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + _chunk(b"IEND", b""))


# --- 5x7 bitmap font -------------------------------------------------------
# Each glyph is 7 rows of 5 pixels ('#' on, '.' off).
FONT_UPPER = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
}
FONT_DIGITS = {
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#...#", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "#...#", ".###."),
}
FONT_LOWER = {
    'a': (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".###.", "#...#", "#....", "#...#", ".###."),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    'g': (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."),
    'j': (".....", "...#.", ".....", "..##.", "...#.", "...#.", "##.#."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
}
FONT_PUNCT = {
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '(': ("...#.", "..#..", "..#..", "..#..", "..#..", "..#..", "...#."),
    ')': (".#...", "..#..", "..#..", "..#..", "..#..", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '&': (".##..", "#..#.", "#..#.", ".#...", "#.##.", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.##.", "#....", ".###."),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '<': ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    '>': (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    '[': (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    ']': (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    '·': (".....", ".....", ".....", ".##..", ".##..", ".....", "....."),
    '•': (".....", ".....", ".....", ".##..", ".##..", ".....", "....."),
}
FONT = {}
FONT.update(FONT_UPPER)
FONT.update(FONT_DIGITS)
FONT.update(FONT_LOWER)
FONT.update(FONT_PUNCT)
BLANK = FONT[' ']


# --- text ------------------------------------------------------------------
def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, fg, bg):
    """Draw string s at (x, y), top-left, on a solid bg colour."""
    fgc = bytes(fg)
    bgc = bytes(bg)
    cx = x
    for ch in s:
        g = FONT.get(ch, BLANK)
        for row in range(7):
            bits = g[row]
            seg = bytearray()
            for col in range(5):
                seg += fgc * scale if bits[col] == '#' else bgc * scale
            seg += bgc * scale  # one column of letter spacing
            for sy in range(scale):
                yy = y + row * scale + sy
                if 0 <= yy < H:
                    o = (yy * W + cx) * 3
                    px[o:o + len(seg)] = seg
        cx += 6 * scale


def wrap(s, scale, max_w):
    """Greedy word wrap; returns a list of lines."""
    words = s.split(' ')
    lines, cur = [], ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, s, scale, fg, bg, max_w, leading=None):
    """Draw a wrapped paragraph; returns the y just below it."""
    lh = leading if leading is not None else 7 * scale + 4
    for ln in wrap(s, scale, max_w):
        draw_text(x, y, ln, scale, fg, bg)
        y += lh
    return y


def center_text(y, s, scale, fg, bg, cx=W // 2):
    draw_text(cx - text_w(s, scale) // 2, y, s, scale, fg, bg)


# --- icons (each draws inside a 56x56 box at x, y) --------------------------
def icon_controller(x, y):
    rect(x + 6, y + 16, 44, 24, (40, 40, 64))     # body
    tri(x + 6, y + 40, x + 16, y + 40, x + 6, y + 50, (40, 40, 64))
    tri(x + 50, y + 40, x + 40, y + 40, x + 50, y + 50, (40, 40, 64))
    rect(x + 12, y + 24, 4, 12, CARD)             # d-pad
    rect(x + 8, y + 28, 12, 4, CARD)
    circle(x + 40, y + 24, 2, RED)                # buttons
    circle(x + 46, y + 28, 2, GREEN)
    circle(x + 40, y + 32, 2, BLUE)
    circle(x + 34, y + 28, 2, GOLD)
    circle(x + 24, y + 33, 3, (160, 160, 170))    # sticks
    circle(x + 31, y + 33, 3, (160, 160, 170))


def icon_capitol(x, y):
    rect(x + 27, y + 4, 2, 10, INK)               # flag pole
    tri(x + 29, y + 4, x + 39, y + 7, x + 29, y + 10, RED)
    circle(x + 28, y + 26, 12, (150, 155, 165))   # dome
    rect(x + 4, y + 26, 48, 6, CARD)              # cut dome base
    rect(x + 6, y + 26, 44, 4, (120, 125, 135))   # entablature
    for cx in (10, 20, 30, 40):                   # columns
        rect(x + cx, y + 30, 4, 14, (150, 155, 165))
    rect(x + 6, y + 44, 44, 6, (120, 125, 135))   # base


def icon_crescent(x, y):
    rect(x + 4, y + 4, 48, 48, TEAL)
    circle(x + 26, y + 28, 15, GOLD)              # moon
    circle(x + 32, y + 26, 13, TEAL)              # cut the crescent
    rect(x + 37, y + 13, 4, 12, CARD)             # star sparkle
    rect(x + 33, y + 17, 12, 4, CARD)


def icon_cyclone(x, y):
    circle(x + 20, y + 20, 9, (110, 116, 124))    # cloud
    circle(x + 30, y + 16, 11, (110, 116, 124))
    circle(x + 40, y + 20, 9, (110, 116, 124))
    rect(x + 13, y + 20, 34, 10, (110, 116, 124))
    line(x + 18, y + 34, x + 14, y + 46, BLUE, 2)  # rain
    line(x + 28, y + 34, x + 24, y + 46, BLUE, 2)
    line(x + 38, y + 34, x + 34, y + 46, BLUE, 2)
    line(x + 6, y + 12, x + 16, y + 12, GREY, 2)  # wind
    line(x + 42, y + 8, x + 52, y + 8, GREY, 2)


def icon_strata(x, y):
    rect(x + 6, y + 8, 44, 8, (90, 140, 70))      # land
    rect(x + 6, y + 16, 44, 8, (200, 180, 130))   # sediment
    rect(x + 6, y + 24, 44, 8, CARD)              # the missing layer
    for dx in (10, 22, 34):
        rect(x + dx, y + 27, 8, 2, (170, 170, 170))
    rect(x + 6, y + 32, 44, 8, (150, 110, 70))    # rock
    rect(x + 6, y + 40, 44, 8, (120, 120, 125))   # bedrock
    draw_text(x + 25, y + 24, "?", 1, RED, CARD)


def icon_eu(x, y):
    rect(x + 4, y + 4, 48, 48, (0, 51, 153))
    for k in range(12):
        a = math.radians(k * 30)
        dx = 28 + int(15 * math.cos(a))
        dy = 28 + int(15 * math.sin(a))
        rect(x + dx - 1, y + dy - 1, 3, 3, GOLD)


def draw_lead_art(x, y, w, h):
    """Shenzhen summit: skyline, three flags, three leaders at a table."""
    rect(x, y, w, h, SKY)
    # skyline silhouettes
    for bx, bh in ((8, 88), (42, 118), (72, 78), (110, 138), (142, 98),
                   (176, 128), (206, 84), (240, 108), (272, 72)):
        rect(x + bx, y + h - 40 - bh, 26, bh, (58, 74, 100))
    tri(x + 118, y + h - 40 - 138, x + 128, y + h - 40 - 158,
        x + 138, y + h - 40 - 138, (58, 74, 100))  # spire
    for wx, wy in ((16, 120), (50, 90), (80, 130), (118, 100), (150, 140),
                   (184, 96), (214, 130), (248, 110), (122, 150), (186, 150)):
        rect(x + wx, y + h - wy, 3, 3, GOLD)      # lit windows
    rect(x, y + h - 40, w, 40, (40, 55, 90))      # plaza
    # three flags
    for fx, flag in ((55, "us"), (148, "cn"), (241, "ru")):
        rect(x + fx, y + 28, 3, h - 68, INK)      # pole
        if flag == "us":
            for s in range(6):
                rect(x + fx + 3, y + 28 + s * 4, 40, 4,
                     RED if s % 2 == 0 else CARD)
            rect(x + fx + 3, y + 28, 16, 12, NAVY)
            for dx in (5, 10, 15):
                for dy in (30, 35):
                    rect(x + fx + dx, y + dy, 2, 2, CARD)
        elif flag == "cn":
            rect(x + fx + 3, y + 28, 40, 24, (222, 41, 16))
            circle(x + fx + 11, y + 36, 3, GOLD)
            circle(x + fx + 20, y + 33, 1, GOLD)
            circle(x + fx + 23, y + 37, 1, GOLD)
            circle(x + fx + 20, y + 42, 1, GOLD)
        else:
            rect(x + fx + 3, y + 28, 40, 8, CARD)
            rect(x + fx + 3, y + 36, 40, 8, (0, 57, 166))
            rect(x + fx + 3, y + 44, 40, 8, (213, 0, 50))
    # table and three leaders
    for hx, skin, suit in ((100, (210, 170, 130), NAVY),
                           (148, (200, 160, 120), INK),
                           (196, (215, 180, 140), (70, 70, 80))):
        circle(x + hx, y + h - 86, 8, skin)
        rect(x + hx - 8, y + h - 78, 16, 16, suit)
    rect(x + 70, y + h - 66, 156, 8, (120, 80, 40))  # table
    rect(x + 78, y + h - 58, 6, 18, (90, 60, 30))
    rect(x + 212, y + h - 58, 6, 18, (90, 60, 30))


# --- the day's news (Thursday 19 November 2026) ------------------------------
LEAD = {
    "tag": "ASIA-PACIFIC · DIPLOMACY",
    "color": BLUE,
    "headline": "TRUMP, XI AND PUTIN MEET IN SHENZHEN",
    "body": ("The three leaders hold rare trilateral talks at the APEC summit, "
             "with Ukraine and Iran high on the agenda."),
}
CARDS = [
    {"tag": "TECHNOLOGY · CULTURE", "color": PURPLE, "icon": icon_controller,
     "headline": "GRAND THEFT AUTO VI ARRIVES",
     "body": ("After a 13-year wait, GTA VI begins its global rollout, with "
              "gamers entering Vice City from today.")},
    {"tag": "UNITED STATES · POLITICS", "color": GREEN, "icon": icon_capitol,
     "headline": "JEFFRIES TO BE FIRST BLACK SPEAKER",
     "body": ("House Democrats nominated Hakeem Jeffries as Speaker; he would "
              "be the first Black American to hold the gavel.")},
    {"tag": "WORLD · SOCIETY", "color": TEAL, "icon": icon_crescent,
     "headline": "ISLAM SET TO TOP WORLD FAITHS BY 2035",
     "body": ("A Pew Research projection says Islam will pass Christianity as "
              "the world's largest religion by 2035.")},
    {"tag": "ASIA · WEATHER", "color": ORANGE, "icon": icon_cyclone,
     "headline": "CYCLONE AKVAN NEARS INDIA",
     "body": ("Akvan is likely to cross the coast between Machilipatnam and "
              "Puri; railways review preparedness.")},
    {"tag": "SCIENCE · EARTH", "color": BROWN, "icon": icon_strata,
     "headline": "EARTH'S LOST BILLION YEARS FOUND",
     "body": ("Scientists say mantle currents and ancient ice sheets erased a "
              "billion years of Earth's history.")},
    {"tag": "EUROPE · UKRAINE", "color": BLUE, "icon": icon_eu,
     "headline": "EU PROPOSES 45BN UKRAINE LOAN",
     "body": ("The EU proposes a 45 billion euro loan for Kyiv, to be repaid "
              "after Russia pays reparations.")},
]
TICKER = ("ALSO TODAY: Iran fires on U.S. sites in Kuwait as the Gulf conflict "
          "continues • NASA to confirm Voyager 1's one-light-day milestone • "
          "Fed minutes point to further rate hikes")
FOOTER = ("Compiled from public news reports · All events of Thursday, "
          "19 November 2026")


def draw_card(x, y, w, h, card):
    rect(x, y, w, h, LINE)
    rect(x + 2, y + 2, w - 4, h - 4, CARD)
    draw_text(x + 14, y + 12, card["tag"], 2, card["color"], CARD)
    card["icon"](x + w - 68, y + 12)
    draw_para(x + 14, y + 32, card["headline"], 3, INK, CARD, w - 28 - 70)
    draw_para(x + 14, y + 92, card["body"], 2, INK, CARD, w - 28)


def draw_page():
    fill(PAPER)
    # masthead
    rect(0, 0, W, 126, NAVY)
    rect(0, 122, W, 4, GOLD)
    center_text(14, "WORLD NEWS", 7, (255, 255, 255), NAVY)
    center_text(72, "THURSDAY · 19 NOVEMBER 2026", 4, GOLD, NAVY)
    rect(0, 126, W, 6, RED)
    # lead story
    draw_text(28, 146, LEAD["tag"], 2, LEAD["color"], PAPER)
    draw_para(28, 168, LEAD["headline"], 4, INK, PAPER, 652)
    draw_para(28, 242, LEAD["body"], 3, INK, PAPER, 652)
    draw_lead_art(700, 142, 296, 230)
    # divider
    rect(28, 384, 968, 2, LINE)
    # story cards: 2 columns x 3 rows
    cw, ch, gx, gy = 472, 170, 16, 12
    for i, card in enumerate(CARDS):
        cx = 28 + (i % 2) * (cw + gx)
        cy = 398 + (i // 2) * (ch + gy)
        draw_card(cx, cy, cw, ch, card)
    # ticker + footer
    draw_para(28, 944, TICKER, 2, INK, PAPER, 968)
    center_text(1004, FOOTER, 2, GREY, PAPER)


def main():
    draw_page()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(encode_png())


if __name__ == "__main__":
    main()
