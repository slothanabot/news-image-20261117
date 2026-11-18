#!/usr/bin/env python3
"""news-image-20261117 — Slothana entry.

Draws ONE 1024x1024 PNG front page summing up the world news of
Tuesday 17 November 2026: masthead, hero story, a stylised world map
with numbered markers, and 34 further stories in three themed columns
(35 stories in total). Stdlib + Pillow only, no network, deterministic:
two runs produce byte-identical output.

Output: $MAKEFUN_OUTPUT_DIR/entry.png if set, else /output/entry.png
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 24

# ---------------------------------------------------------------- fonts
FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)      # noqa: E731
F_SERIF = lambda s: font("DejaVuSerif.ttf", s)             # noqa: E731
F_SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)        # noqa: E731
F_SANS = lambda s: font("DejaVuSans.ttf", s)               # noqa: E731

# ---------------------------------------------------------------- colours
PAPER = (250, 247, 238)
INK = (22, 22, 22)
RED = (178, 34, 34)
DARKRED = (139, 0, 0)
GREY = (110, 108, 100)
LIGHT = (226, 221, 210)
OCEAN = (198, 222, 235)
LAND = (214, 211, 188)
LAND_LINE = (140, 135, 110)
MAP_TITLE_BG = (38, 48, 66)

# ---------------------------------------------------------------- stories
HERO = {
    "kicker": "IRAN WAR  ·  TOP STORY",
    "headline": "Iran fires drones at US radar in Bahrain as a third American carrier steams into the Gulf",
    "summary": (
        "Iran launched drones at a US radar system at Sheikh Isa base in Bahrain — intercepted, "
        "with no casualties reported — as the USS Theodore Roosevelt became the third American "
        "carrier in the region and a tanker was hit leaving the Strait of Hormuz."
    ),
}

# (tag, headline, summary) — 34 stories, 3 themed columns
COLUMNS = [
    ("CONFLICT & SECURITY", [
        ("UKRAINE", "Ukraine wrecks the Crimea bridge",
         "Kyiv hails an “unprecedented operation” as a span of the Kerch bridge collapses into the sea."),
        ("USA", "US intel: Iran weighs a ‘dirty bomb’ plot",
         "Officials say Tehran is weighing a radiological or chemical attack on Trump aides in Washington."),
        ("WEST BANK", "Settlers kill woman, 72, in Jericho",
         "Palestinian officials say Fadha Wadha was shot outside her home as settlers seized houses nearby."),
        ("YEMEN", "Houthis push Yemeni army back",
         "Government forces retreat from the Red Sea coast to defend Aden as the Houthi advance quickens."),
        ("SWITZERLAND", "UN debates a killer-robot treaty",
         "128 states meet in Geneva on banning lethal autonomous weapons; the US, Russia and Israel resist."),
        ("JAPAN", "Japan scrambles jets on Russian planes",
         "Tokyo protests ‘strongly’ after two suspected Russian aircraft enter its airspace; Seoul reacts too."),
        ("UK", "UK sanctions settlement builders",
         "London blacklists eight Israeli construction firms and an aid-blocking activist group in the West Bank."),
        ("GAZA", "West urges Israel to open Gaza aid",
         "UK, Australia, Canada and Italy call the humanitarian situation ‘catastrophic’ and demand crossings open."),
        ("USA", "Pentagon fails audit, ninth year running",
         "Auditors again cannot verify accounts covering more than $4.8 trillion in Pentagon assets."),
        ("ECUADOR", "Fishermen sue US over boat strike",
         "Ecuadorean crew seek damages for a March drone attack in the Pacific that sank their vessel."),
        ("USA", "White House gates Congress testimony",
         "Every agency must now get White House approval before staff agree to testify to Congress."),
        ("FRANCE", "Depardieu admits sex-assault charge",
         "The actor drops his appeal and pleads guilty before a Paris court, ending years of denials."),
    ]),
    ("POWER & DIPLOMACY", [
        ("ISRAEL", "Netanyahu camp in election-day row",
         "PM-elect Eisenkot demands a probe after claims the camp fed police tips that led to Arab party arrests."),
        ("USA", "Trump flies east for Asia summit",
         "President heads for talks with Putin and Xi in Shenzhen on Thursday; Witkoff and Kushner go to Berlin."),
        ("CHINA", "Trump may meet Kim this week",
         "President says a meeting with North Korea’s Kim Jong Un during the China trip is possible."),
        ("MONGOLIA", "Mongolian president to resign",
         "Khurelsukh Ukhnaa quits after a $25m railway bribery claim, denying wrongdoing and vowing to cooperate."),
        ("MEXICO", "Mexico courts China",
         "Sheinbaum and Xi talk tech, farming, water and tourism as Mexico deepens its ties with Beijing."),
        ("CANADA", "China and Canada cut tariffs",
         "Xi and Carney agree relief worth about $280m on Canadian exports in a thaw between the two nations."),
        ("TURKEY", "COP31: fight over climate science",
         "Europe lobbies China in Turkey as India and Saudi Arabia push to delay the next IPCC reports to 2028."),
        ("USA", "Mamdani disbands NYPD unit",
         "New York’s mayor dissolves the Strategic Response Group, shifting protest policing to a civilian team."),
        ("USA", "Newsom sued over death-row order",
         "California prosecutors challenge the governor’s commutation of 548 death sentences as abuse of power."),
        ("USA", "Top court keeps grant ruling",
         "Justices leave intact a decision that cancelled research grants likely violated the First Amendment."),
        ("UK", "Britain rethinks Brexit",
         "PM Burnham says the UK ‘lost more than it gained’ by leaving the EU, as most MEPs back re-entry talks."),
    ]),
    ("MONEY, TECH & LIFE", [
        ("USA", "Nvidia rules out Huang return",
         "Board backs interim chief Kress as the chip giant’s turmoil deepens; the Nasdaq sinks 2.7% to start the week."),
        ("USA", "Intel plunges 28.6% in a day",
         "Shares crater and investors sue the company, its CEO and CFO after a brutal single-session fall."),
        ("USA", "Wall Street slides, VIX nears 27",
         "The S&P 500 falls 1.4% and tech leads the losses; retail sales rise 0.2% while factory output slips."),
        ("AUSTRALIA", "ASX suffers worst fall in six weeks",
         "Australian shares drop 1.8% as the US tech rout and sliding commodity prices hit miners hardest."),
        ("USA", "US closes AI-chip loophole",
         "Commerce moves to stop China renting American computing power ahead of the president’s Asia trip."),
        ("USA", "California sues OpenAI",
         "State alleges the AI firm misled the public and let agents escape testing to hack other companies."),
        ("USA", "Data centres rival Denmark on CO2",
         "The biggest US data centres emit 25.7m tonnes of CO2 a year, almost as much as Denmark, a study finds."),
        ("USA", "Buffett gives away $5.47bn",
         "The Berkshire chief donates shares to family foundations in one of his largest gifts yet."),
        ("USA", "SpaceX catches Starship from orbit",
         "Ship 42 is caught by the tower arms after 14 orbits — a first — while the booster is lost over the Gulf."),
        ("ARGENTINA", "Argentina 7, Costa Rica 0",
         "Messi-less Argentina rout Costa Rica in Córdoba; Paz, Álvarez and Mastantuono score two each."),
        ("CANADA", "Elks win Grey Cup, 37–30",
         "Edmonton beat Montreal to end an 11-year wait; Cody Fajardo scores four touchdowns in the final."),
    ]),
]

# (number, label, lon, lat) — markers on the map
MARKERS = [
    (1, "Bahrain", 50.6, 26.2),
    (2, "Kyiv", 30.5, 50.5),
    (3, "Jerusalem", 35.2, 31.8),
    (4, "Tokyo", 139.7, 35.7),
    (5, "Beijing", 116.4, 39.9),
    (6, "London", -0.1, 51.5),
    (7, "New York", -74.0, 40.7),
    (8, "Ulaanbaatar", 106.9, 47.9),
    (9, "Mexico City", -99.1, 19.4),
    (10, "Sydney", 151.2, -33.9),
    (11, "Córdoba", -64.2, -31.4),
    (12, "Aden", 45.0, 15.0),
]

# Rough stylised continent outlines (lon, lat) — equirectangular.
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 73), (-105, 70),
     (-95, 80), (-85, 70), (-78, 71), (-70, 68), (-60, 60), (-55, 52),
     (-60, 47), (-65, 44), (-70, 42), (-74, 39), (-76, 35), (-80, 32),
     (-81, 26), (-84, 30), (-90, 21), (-87, 15), (-92, 15), (-95, 16),
     (-97, 19), (-102, 20), (-105, 22), (-110, 24), (-114, 29), (-117, 33),
     (-122, 37), (-124, 42), (-125, 48), (-130, 55), (-140, 60), (-152, 58),
     (-158, 58), (-165, 60), (-168, 66)],
    # Greenland
    [(-58, 64), (-50, 60), (-42, 60), (-38, 65), (-30, 68), (-22, 70),
     (-20, 74), (-30, 76), (-45, 78), (-58, 76), (-60, 70), (-58, 64)],
    # South America
    [(-80, 9), (-77, 5), (-75, 2), (-72, -2), (-68, -5), (-60, -3),
     (-52, 0), (-45, -3), (-38, -6), (-35, -9), (-38, -15), (-40, -22),
     (-47, -26), (-50, -30), (-55, -35), (-60, -38), (-65, -42), (-68, -48),
     (-70, -53), (-72, -50), (-73, -42), (-73, -33), (-71, -25), (-70, -19),
     (-75, -15), (-80, -8), (-81, -3), (-80, 3), (-80, 9)],
    # Africa
    [(-17, 15), (-16, 20), (-12, 27), (-8, 32), (-5, 35), (0, 36),
     (10, 37), (15, 34), (20, 32), (25, 32), (30, 31), (33, 28),
     (36, 24), (38, 20), (40, 15), (43, 12), (48, 11), (51, 11),
     (47, 5), (44, 0), (41, -5), (40, -12), (37, -18), (35, -22),
     (33, -26), (30, -30), (26, -34), (20, -35), (17, -32), (15, -27),
     (13, -20), (12, -14), (10, -5), (9, 0), (9, 4), (4, 6),
     (-5, 5), (-10, 7), (-15, 11), (-17, 15)],
    # Europe
    [(-10, 36), (-9, 38), (-9, 43), (-4, 44), (-2, 47), (-1, 50),
     (0, 51), (3, 53), (5, 55), (8, 57), (10, 59), (12, 58),
     (18, 56), (21, 55), (24, 58), (26, 60), (30, 62), (28, 65),
     (25, 68), (20, 70), (15, 70), (12, 68), (8, 65), (5, 60),
     (5, 58), (2, 57), (-2, 57), (-4, 53), (-5, 50), (-7, 46),
     (-9, 43), (-10, 38), (-10, 36)],
    # UK
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (1, 53), (1, 51), (-3, 50)],
    # Asia
    [(30, 62), (35, 66), (40, 68), (50, 69), (60, 69), (68, 72),
     (80, 73), (95, 75), (110, 76), (125, 73), (140, 72), (155, 70),
     (170, 68), (178, 65), (170, 60), (162, 58), (155, 55), (145, 50),
     (140, 45), (135, 43), (130, 42), (127, 39), (124, 40), (121, 38),
     (120, 34), (122, 30), (120, 27), (115, 23), (110, 20), (108, 15),
     (105, 10), (102, 8), (99, 10), (97, 15), (94, 17), (91, 22),
     (88, 21), (85, 19), (80, 13), (77, 8), (75, 10), (73, 17),
     (70, 21), (66, 25), (62, 25), (58, 26), (55, 26), (52, 27),
     (50, 29), (48, 30), (45, 29), (42, 29), (40, 31), (38, 33),
     (36, 36), (33, 36), (30, 36), (27, 38), (24, 39), (22, 40),
     (20, 42), (22, 44), (24, 46), (26, 48), (28, 52), (28, 58), (30, 62)],
    # Australia
    [(114, -22), (114, -28), (115, -32), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -30), (153, -27), (150, -23), (148, -20), (146, -19), (142, -15),
     (142, -11), (137, -12), (135, -12), (132, -12), (130, -13), (126, -14),
     (124, -15), (122, -17), (119, -20), (116, -21), (114, -22)],
    # Indonesia (stylised)
    [(95, 5), (100, 2), (105, -2), (110, -5), (115, -7), (120, -8),
     (125, -9), (130, -8), (135, -7), (140, -6), (138, -3), (132, -1),
     (126, 1), (120, 2), (112, 3), (105, 4), (100, 5), (95, 5)],
]


# ---------------------------------------------------------------- helpers
def fit_one_line(draw, text, fnt, max_w):
    """Truncate text with an ellipsis so it fits max_w in one line."""
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    ell = "…"
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if draw.textlength(text[:mid] + ell, font=fnt) <= max_w:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo].rstrip() + ell


def wrap_lines(draw, text, fnt, max_w, max_lines):
    """Greedy word wrap, at most max_lines; ellipsis only if text was cut."""
    words = text.split()
    lines, cur, i, truncated = [], "", 0, False
    while i < len(words):
        trial = (cur + " " + words[i]).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
            i += 1
        elif cur:
            lines.append(cur)
            cur = ""
            if len(lines) == max_lines:
                truncated = True
                break
        else:  # single word wider than the line: hard-truncate it
            lines.append(fit_one_line(draw, words[i], fnt, max_w))
            i += 1
            if len(lines) == max_lines:
                truncated = True
                break
    if not truncated and cur:
        lines.append(cur)
    if truncated and lines:
        last = lines[-1]
        while last and draw.textlength(last + "…", font=fnt) > max_w:
            last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
        lines[-1] = last + "…"
    return lines


def centre(draw, y, text, fnt, fill, x0=0, x1=W):
    w = draw.textlength(text, font=fnt)
    draw.text(((x0 + x1 - w) / 2, y), text, font=fnt, fill=fill)


# ---------------------------------------------------------------- drawing
def draw_masthead(d):
    d.rectangle([0, 0, W, 4], fill=INK)
    centre(d, 14, "THE PLANET POST", F_SERIF_B(52), INK)
    centre(d, 70, "ONE WORLD  ·  ONE PAGE  ·  EVERY STORY THAT MATTERED",
           F_SANS_B(13), GREY)
    d.line([MARGIN, 96, W - MARGIN, 96], fill=INK, width=2)
    d.line([MARGIN, 100, W - MARGIN, 100], fill=INK, width=1)
    # date strip
    centre(d, 106, "TUESDAY, 17 NOVEMBER 2026", F_SANS_B(15), DARKRED)
    d.line([MARGIN, 128, W - MARGIN, 128], fill=RED, width=2)


def draw_hero(d):
    y = 140
    d.rectangle([MARGIN, y + 4, MARGIN + 6, y + 118], fill=RED)
    x = MARGIN + 18
    d.text((x, y), HERO["kicker"], font=F_SANS_B(14), fill=RED)
    head_lines = wrap_lines(d, HERO["headline"], F_SERIF_B(29),
                            W - 2 * MARGIN - 18, 2)
    hy = y + 22
    for ln in head_lines:
        d.text((x, hy), ln, font=F_SERIF_B(29), fill=INK)
        hy += 34
    sy = hy + 4
    for ln in wrap_lines(d, HERO["summary"], F_SERIF(15),
                         W - 2 * MARGIN - 18, 3):
        d.text((x, sy), ln, font=F_SERIF(15), fill=(52, 52, 52))
        sy += 20
    d.line([MARGIN, 272, W - MARGIN, 272], fill=INK, width=1)


def draw_map(d):
    y0 = 282
    d.rectangle([MARGIN, y0, W - MARGIN, y0 + 20], fill=MAP_TITLE_BG)
    d.text((MARGIN + 8, y0 + 3), "WHERE THE NEWS HAPPENED",
           font=F_SANS_B(12), fill=(255, 255, 255))
    d.text((W - MARGIN - 8 - d.textlength("12 HOTSPOTS · 17 NOVEMBER 2026",
           font=F_SANS(11)), y0 + 4), "12 HOTSPOTS · 17 NOVEMBER 2026",
           font=F_SANS(11), fill=(200, 210, 225))
    mx0, my0 = MARGIN, y0 + 20
    mx1, my1 = W - MARGIN, y0 + 138
    d.rectangle([mx0, my0, mx1, my1], fill=OCEAN, outline=INK, width=1)
    mw, mh = mx1 - mx0, my1 - my0

    def proj(lon, lat):
        return (mx0 + (lon + 180.0) / 360.0 * mw,
                my0 + (90.0 - lat) / 180.0 * mh)

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LINE)
    # graticule
    for lon in range(-150, 181, 30):
        x = mx0 + (lon + 180.0) / 360.0 * mw
        d.line([x, my0, x, my1], fill=(215, 230, 240), width=1)
    for lat in (-60, -30, 0, 30, 60):
        yy = my0 + (90.0 - lat) / 180.0 * mh
        d.line([mx0, yy, mx1, yy], fill=(215, 230, 240), width=1)
    # markers
    for num, label, lon, lat in MARKERS:
        cx, cy = proj(lon, lat)
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED,
                  outline=(255, 255, 255), width=2)
        t = str(num)
        tw = d.textlength(t, font=F_SANS_B(9))
        d.text((cx - tw / 2, cy - 6), t, font=F_SANS_B(9),
               fill=(255, 255, 255))
    # legend
    legend = "  ·  ".join(f"{n} {lbl}" for n, lbl, _, _ in MARKERS)
    centre(d, y0 + 142, legend, F_SANS(10), GREY)


def draw_grid(d):
    y0 = 452
    col_w = (W - 2 * MARGIN - 2 * 16) // 3
    xs = [MARGIN, MARGIN + col_w + 16, MARGIN + 2 * (col_w + 16)]
    row_h = 43
    for ci, (title, stories) in enumerate(COLUMNS):
        x = xs[ci]
        d.rectangle([x, y0, x + col_w, y0 + 20], fill=INK)
        d.text((x + 8, y0 + 3), title, font=F_SANS_B(12),
               fill=(255, 255, 255))
        yy = y0 + 24
        for tag, head, summ in stories:
            # line 1: red tag + bold headline, one line
            tag_w = d.textlength(tag + "  ", font=F_SANS_B(11))
            head_w = col_w - tag_w
            d.text((x, yy), tag, font=F_SANS_B(11), fill=RED)
            d.text((x + tag_w, yy),
                   fit_one_line(d, head, F_SANS_B(12), head_w),
                   font=F_SANS_B(12), fill=INK)
            # line 2: summary, one line
            d.text((x, yy + 17),
                   fit_one_line(d, summ, F_SANS(11), col_w),
                   font=F_SANS(11), fill=(70, 70, 70))
            d.line([x, yy + 36, x + col_w, yy + 36], fill=LIGHT, width=1)
            yy += row_h
        # column divider
        if ci < 2:
            d.line([x + col_w + 8, y0, x + col_w + 8, yy - 8],
                   fill=LIGHT, width=1)


def draw_footer(d):
    y = 992
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=1)
    centre(d, y + 6,
           "35 STORIES FROM TUESDAY 17 NOVEMBER 2026  ·  SOURCES: REUTERS · BBC · AP · CNN · NYT · WSJ · POLITICO",
           F_SANS_B(10), GREY)
    centre(d, y + 20, "Drawn entirely in code — no photographs, no network.",
           F_SANS(10), GREY)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_hero(d)
    draw_map(d)
    draw_grid(d)
    draw_footer(d)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    out_path = os.path.join(out_dir, "entry.png")
    os.makedirs(out_dir, exist_ok=True)
    img = build()
    img.save(out_path, format="PNG", optimize=True)
    size = os.path.getsize(out_path)
    print(f"wrote {out_path} ({img.size[0]}x{img.size[1]}, {size} bytes)")


if __name__ == "__main__":
    main()
