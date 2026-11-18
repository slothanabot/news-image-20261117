#!/usr/bin/env python3
"""THE PLANET POST - front page for Tuesday 17 November 2026.

Draws a single 1024x1024 PNG newspaper front page summing up the day's
world news in 35 real stories, using the Python standard library ONLY.

No third-party packages, no system fonts, no files read at runtime: the
PNG encoder is hand-rolled (zlib + struct + CRC32 chunks) and every
letter is drawn from a built-in 5x7 bitmap font defined below.

Output: $MAKEFUN_OUTPUT_DIR/entry.png when set, else /output/entry.png
when /output exists, else ./entry.png. Two runs are byte-identical.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 242, 232)
INK = (22, 22, 22)
RED = (176, 32, 32)
OCEAN = (164, 203, 224)
LAND = (206, 190, 148)
LAND_EDGE = (150, 134, 96)
RULE = (120, 112, 96)
WHITE = (255, 255, 255)
GREY = (96, 90, 80)

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs. Each glyph is 7 rows of 5 characters; "#" is ink.
# Written from scratch for this program; lowercase sits on rows 2-6
# with descenders on row 6.

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    "q": ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("00100", "00100", "01110", "00100", "00100", "00100", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "01110", "00000", "01110", "00000", "00000"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
}

# ---------------------------------------------------------------- canvas

class Canvas:
    """An RGB pixel buffer with tiny drawing primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def _off(self, x, y):
        return (y * self.w + x) * 3

    def set_px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = self._off(x, y)
            self.px[o] = color[0]
            self.px[o + 1] = color[1]
            self.px[o + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            o = self._off(x0, yy)
            self.px[o:o + len(row)] = row

    def hline(self, x, y, w, color, t=1):
        self.fill_rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.fill_rect(x, y, t, h, color)

    def rect(self, x, y, w, h, color, t=1):
        self.hline(x, y, w, color, t)
        self.hline(x, y + h - t, w, color, t)
        self.vline(x, y, h, color, t)
        self.vline(x + w - t, y, h, color, t)

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = math.isqrt(r * r - dy * dy)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = math.isqrt(r * r - dy * dy)
            self.set_px(cx - dx, cy + dy, color)
            self.set_px(cx + dx, cy + dy, color)


# ---------------------------------------------------------------- text

def text_width(text, scale):
    """Pixel width of text at the given scale (no trailing gap)."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def draw_text(cv, x, y, text, scale, color):
    """Draw text with its top-left corner at (x, y)."""
    cx = x
    for ch in text:
        glyph = FONT.get(ch)
        if glyph is None:
            cx += 6 * scale
            continue
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    cv.fill_rect(cx + col * scale, y + row * scale,
                                 scale, scale, color)
        cx += 6 * scale
    return cx


def draw_text_centered(cv, cx, y, text, scale, color):
    draw_text(cv, cx - text_width(text, scale) // 2, y, text, scale, color)


def wrap_text(text, max_w, scale):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- png

def _chunk(kind, data):
    return (struct.pack(">I", len(data)) + kind + data +
            struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))


def encode_png(w, h, rgb):
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)  # filter: none
        raw += rgb[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" +
            _chunk(b"IHDR", ihdr) +
            _chunk(b"IDAT", zlib.compress(bytes(raw), 6)) +
            _chunk(b"IEND", b""))

# ---------------------------------------------------------------- stories
# 35 real stories from Tuesday 17 November 2026.
# (tag, headline, one-line summary). Headlines are upper case on purpose.

HERO_HEADLINE = ("IRAN FIRES DRONES AT US RADAR IN BAHRAIN AS THIRD "
                  "US CARRIER ENTERS THE GULF")
HERO_STANDFIRST = ("Bahrain says its air defences intercepted the drones, "
                   "the third Iranian attack in five days, as the USS "
                   "Theodore Roosevelt joins two other carriers in the "
                   "region and the war grinds into its ninth month.")
HERO_FACTS = ("3 US CARRIERS IN THE REGION  |  20+ WARSHIPS  |  "
              "3RD ATTACK IN 5 DAYS")

DAY_NUMBERS = [
    ("372", "civilians killed in Ukraine in October, says the UN"),
    ("1,441", "Ukrainian drones downed by Russia in one night"),
    ("35.6", "German investor morale, up from 28.1 in October"),
]

COLUMNS = [
    ("CONFLICT & SECURITY", [
        ("UKRAINE",
         "UKRAINE HITS KERCH BRIDGE FOR SECOND DAY; ROAD SPAN FALLS INTO SEA",
         "Zelensky calls it an unprecedented seven-stage op."),
        ("UKRAINE",
         "RUSSIAN MISSILES HIT TWO KYIV BRIDGES; TWO KILLED",
         "Heating and water cut in parts of the capital."),
        ("UKRAINE",
         "UN: 372 CIVILIANS KILLED IN UKRAINE IN OCTOBER",
         "Deadliest October since the invasion began."),
        ("BELGIUM",
         "AT RAMSTEIN, US URGES EUROPE TO FUND MORE ARMS FOR KYIV",
         "Colby faults Kyiv strikes on Russian sites."),
        ("GERMANY",
         "BERLIN AND OSLO TO FUND $300M AIR-DEFENCE PACKAGE",
         "New PURL deal to rush interceptors to Kyiv."),
        ("UNITED NATIONS",
         "GAZA PEACE BOARD WARNS CEASEFIRE COULD COLLAPSE",
         "Bleak report to UN council urges full compliance."),
        ("GAZA",
         "1,649 KILLED IN GAZA SINCE CEASEFIRE, OFFICIALS SAY",
         "Aid trucks reach only a third of agreed total."),
        ("RUSSIA",
         "MOSCOW SAYS IT DOWNED A RECORD 1,441 DRONES",
         "Second straight night of huge Ukrainian raids."),
        ("UKRAINE",
         "KYIV: NORTH KOREA SENDS RUSSIA DOZENS OF MISSILES A MONTH",
         "Zelensky urges allies to match the threat."),
        ("RUSSIA",
         "UKRAINE STRIKES SALAVAT REFINERY DEEP IN RUSSIA",
         "Latest hit in the campaign on Russian oil."),
        ("UKRAINE",
         "THREE-WAVE DRONE ATTACK HITS ZAKARPATTIA IN THE WEST",
         "Blasts in Mukachevo and Uzhhorod, officials say."),
        ("IRAN",
         "TEHRAN SAYS IT SEIZED A US DRONE NEAR HORMUZ",
         "Claim comes as Gulf tensions climb; US silent."),
    ]),
    ("POWER & DIPLOMACY", [
        ("PHILIPPINES",
         "TRUMP LANDS IN MANILA FOR FIRST QUAD SUMMIT IN TWO YEARS",
         "US, Japan, Australia, India meet before China."),
        ("CHINA",
         "TRUMP, XI AND PUTIN SET FOR SHENZHEN MEETING ON THURSDAY",
         "First three-way summit; nukes, trade on table."),
        ("PHILIPPINES",
         "UN CHIEF URGES LEADERS TO COMMIT TO DENUCLEARISATION",
         "Guterres opens ASEAN week with plea to big three."),
        ("PHILIPPINES",
         "ASEAN WRAPS UP: SEA CODE IN FINAL PHASE, CHAIR TO SINGAPORE",
         "49th summit ends as Trump arrives in Manila."),
        ("PHILIPPINES",
         "TRUMP TO SIGN TRADE DEAL WITH THAILAND IN MANILA",
         "White House touts pact as Asia tour begins."),
        ("JAPAN",
         "JAPAN PM TAKAICHI JOINS MANILA TALKS, THEN HEADS TO CHINA",
         "First Quad for Tokyo's new leader."),
        ("CHINA",
         "BEIJING HAILS EXTRAORDINARY CHINA-ASEAN TRADE TIES",
         "Premier Li urges bloc to stand united on trade."),
        ("UNITED STATES",
         "US RETAIL SALES DUE AS FED SPEAKERS TAKE THE STAGE",
         "Waller, Williams, Hammack, Musalem all speak."),
        ("IRELAND",
         "DUBLIN SITS ON 6.7BN EURO SURPLUS - AND SPENDS LITTLE",
         "Taoiseach wary of splash despite tax windfall."),
        ("BELGIUM",
         "PARTNERS PLEDGE 70M EUROS TO CLEAR MINES IN UKRAINE",
         "Demining fund announced at Brussels conference."),
        ("PAKISTAN",
         "ISLAMABAD AWAITS US REPLY ON IRAN HORMUZ PLAN",
         "Two-day plan to reopen the strait still pending."),
    ]),
    ("MONEY | TECH | LIFE", [
        ("UNITED STATES",
         "NVIDIA REPORTS AFTER THE BELL; STAND-IN CEO FACES GRILLING",
         "Kress takes questions days after Huang's exit."),
        ("UNITED STATES",
         "CHIP ROUT DEEPENS AS US TIGHTENS AI EXPORT CURBS",
         "SOX index fell 5% on Monday; Nasdaq lost 2%."),
        ("UNITED STATES",
         "INTEL DOWN 50% SINCE OCTOBER AS CHIP SLIDE BITES",
         "Still up 50% on the year despite the rout."),
        ("UNITED STATES",
         "US HOMEBUILDER MOOD HITS 14-1/2 YEAR LOW",
         "NAHB index falls to 25 as mortgage rates bite."),
        ("GERMANY",
         "GERMAN INVESTOR MORALE BEATS FORECASTS AT 35.6",
         "ZEW index rises from 28.1 in November."),
        ("GERMANY",
         "DEUTSCHE BANK SLIDES 5% ON LEAKED RECORDS",
         "Fresh scrutiny of the lender's past clients."),
        ("UNITED STATES",
         "OUTAGE WAVE HITS MICROSOFT, FAA, JPMORGAN AND APPLE",
         "NSA reports brief outage; Trump plays it down."),
        ("UNITED STATES",
         "DISNEY AND HOME DEPOT REPORT AS EARNINGS SEASON ROLLS ON",
         "Retail sales and results crowd Tuesday's diary."),
        ("UNITED KINGDOM",
         "OIL AND COPPER FALL AS CHIP ROUT SPREADS",
         "Volatility gauge rises; yields tick back."),
        ("UKRAINE",
         "UKRAINE OIL EXPORTS HOLD AT 230,000 TONNES",
         "Shipments survive attacks on processing plants."),
        ("SINGAPORE",
         "BINANCE REELS FROM $6.3BN HACK LINKED TO NORTH KOREA",
         "Heist named in a wave of tech incidents."),
    ]),
]

# ---------------------------------------------------------------- world map
# Stylised world map: land given as (row, first_col, last_col) spans on a
# 30 row x 64 column grid. Columns span longitude -180..180, rows span
# latitude 90..-90 (Antarctica omitted).
LAND_SPANS = [
    (0, 22, 23),
    (1, 12, 16), (1, 21, 27), (1, 35, 35),
    (2, 8, 20), (2, 21, 28), (2, 37, 62),
    (3, 2, 8), (3, 9, 21), (3, 22, 26), (3, 32, 36), (3, 37, 63),
    (4, 3, 7), (4, 8, 20), (4, 23, 25), (4, 33, 36), (4, 38, 62),
    (5, 4, 6), (5, 9, 19), (5, 31, 31), (5, 33, 60),
    (6, 10, 19), (6, 31, 38), (6, 39, 58),
    (7, 10, 19), (7, 31, 37), (7, 40, 57),
    (8, 11, 19), (8, 31, 36), (8, 41, 56),
    (9, 11, 17), (9, 29, 37), (9, 38, 41), (9, 44, 54),
    (10, 12, 15), (10, 29, 38), (10, 39, 42), (10, 45, 53),
    (11, 13, 16), (11, 29, 38), (11, 40, 42), (11, 45, 47), (11, 49, 52),
    (12, 15, 17), (12, 30, 39), (12, 46, 46), (12, 49, 51),
    (13, 18, 23), (13, 31, 38), (13, 49, 55),
    (14, 18, 24), (14, 32, 38), (14, 50, 53),
    (15, 18, 25), (15, 33, 38),
    (16, 18, 25), (16, 33, 38), (16, 52, 56),
    (17, 19, 24), (17, 34, 38), (17, 52, 58),
    (18, 19, 23), (18, 34, 37), (18, 52, 58),
    (19, 20, 23), (19, 35, 37), (19, 53, 57),
    (20, 20, 22), (20, 35, 36), (20, 54, 57),
    (21, 21, 21), (21, 61, 62),
    (22, 21, 21), (22, 61, 61),
    (23, 21, 21),
    (24, 21, 21),
]


def build_world_grid():
    grid = [["."] * 64 for _ in range(30)]
    for row, first, last in LAND_SPANS:
        for c in range(first, last + 1):
            grid[row][c] = "#"
    return ["".join(r) for r in grid]


WORLD = build_world_grid()

# (number, name, longitude, latitude) - markers drawn on the map.
HOTSPOTS = [
    (1, "BAHRAIN", 50.6, 26.2),
    (2, "KYIV", 30.5, 50.4),
    (3, "JERUSALEM", 35.2, 31.8),
    (4, "TOKYO", 139.7, 35.7),
    (5, "BEIJING", 116.4, 39.9),
    (6, "LONDON", -0.1, 51.5),
    (7, "NEW YORK", -74.0, 40.7),
    (8, "ULAANBAATAR", 106.9, 47.9),
    (9, "MEXICO CITY", -99.1, 19.4),
    (10, "SYDNEY", 151.2, -33.9),
    (11, "CORDOBA", -64.2, -31.4),
    (12, "ADEN", 45.0, 12.8),
]


def draw_map(cv, x, y, w, h):
    """Draw the stylised world map with numbered hotspot markers."""
    cv.fill_rect(x, y, w, h, OCEAN)
    cols = 64
    rows = 30
    cw = w // cols
    ch = h // rows
    for r in range(rows):
        line = WORLD[r]
        for c in range(cols):
            if c < len(line) and line[c] == "#":
                cv.fill_rect(x + c * cw, y + r * ch, cw, ch, LAND)
    # hotspot markers: red disc, white number
    for num, _name, lon, lat in HOTSPOTS:
        mx = x + int((lon + 180.0) / 360.0 * w)
        my = y + int((90.0 - lat) / 180.0 * h)
        cv.disc(mx, my, 7, RED)
        cv.ring(mx, my, 7, WHITE)
        label = str(num)
        draw_text(cv, mx - text_width(label, 1) // 2, my - 3, label, 1, WHITE)


# ---------------------------------------------------------------- layout

def draw_masthead(cv):
    draw_text_centered(cv, W // 2, 26, "THE PLANET POST", 6, INK)
    cv.hline(28, 84, 968, INK, 3)
    cv.hline(28, 89, 968, INK, 1)
    draw_text_centered(cv, W // 2, 98,
                       "TUESDAY, 17 NOVEMBER 2026  |  35 STORIES, ONE PAGE",
                       1, INK)
    cv.hline(28, 112, 968, INK, 1)


def draw_hero(cv):
    x, y, w = 28, 124, 620
    cv.fill_rect(x, y, 74, 16, RED)
    draw_text(cv, x + 6, y + 5, "TOP STORY", 1, WHITE)
    draw_text(cv, x + 86, y + 5, "THE GULF", 1, RED)
    lines = wrap_text(HERO_HEADLINE, w, 3)
    yy = y + 28
    for line in lines:
        draw_text(cv, x, yy, line, 3, INK)
        yy += 22
    yy += 6
    for line in wrap_text(HERO_STANDFIRST, w, 1):
        draw_text(cv, x, yy, line, 1, INK)
        yy += 10
    yy += 8
    cv.hline(x, yy, w, RULE, 1)
    yy += 10
    draw_text(cv, x, yy, HERO_FACTS, 1, RED)
    yy += 24
    cv.hline(x, yy, w, INK, 1)
    yy += 10
    draw_text(cv, x, yy, "THE DAY IN NUMBERS", 1, INK)
    yy += 14
    for num, label in DAY_NUMBERS:
        draw_text(cv, x, yy, num, 1, RED)
        draw_text(cv, x + 62, yy, label, 1, INK)
        yy += 13


def draw_map_panel(cv):
    x, y, w, h = 664, 124, 332, 228
    cv.rect(x, y, w, h, INK, 1)
    draw_text(cv, x + 10, y + 6, "THE WORLD AT A GLANCE", 1, INK)
    draw_map(cv, x + 6, y + 22, 320, 150)
    # legend: two columns of six hotspots
    ly = y + 178
    for i, (num, name, _lon, _lat) in enumerate(HOTSPOTS):
        col = 0 if i < 6 else 1
        row = i if i < 6 else i - 6
        lx = x + 10 + col * 162
        draw_text(cv, lx, ly + row * 8, str(num) + " " + name, 1, INK)


def draw_columns(cv):
    top = 372
    col_w = 312
    gap = 16
    for i, (title, stories) in enumerate(COLUMNS):
        x = 28 + i * (col_w + gap)
        cv.fill_rect(x, top, col_w, 22, INK)
        draw_text(cv, x + 8, top + 8, title, 1, WHITE)
        yy = top + 34
        for tag, headline, summary in stories:
            draw_text(cv, x, yy, tag, 1, RED)
            yy += 10
            for line in wrap_text(headline, col_w, 1):
                draw_text(cv, x, yy, line, 1, INK)
                yy += 10
            draw_text(cv, x, yy, summary, 1, GREY)
            yy += 10
            cv.hline(x, yy, col_w, RULE, 1)
            yy += 12


def draw_footer(cv):
    cv.hline(28, 962, 968, INK, 2)
    draw_text_centered(cv, W // 2, 972,
                       "SOURCES: REUTERS | BBC | AP | CNN | NYT | WSJ | POLITICO",
                       1, INK)
    draw_text_centered(cv, W // 2, 986,
                       "ALL STORIES DATED TUESDAY 17 NOVEMBER 2026",
                       1, GREY)


def build_page():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_hero(cv)
    draw_map_panel(cv)
    draw_columns(cv)
    draw_footer(cv)
    return cv


def output_path():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        return os.path.join(out_dir, "entry.png")
    if os.path.isdir("/output"):
        return "/output/entry.png"
    return "entry.png"


def main():
    cv = build_page()
    data = encode_png(W, H, cv.px)
    path = output_path()
    with open(path, "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
