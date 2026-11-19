#!/usr/bin/env python3
"""
THE WHOLE DAY — Broadsheet Edition
A deterministic PIL renderer for the make.fun competition
news-image-20261119: "Sum up 19 November's world news in one image."

Running this file writes entry.png (1024x1024) beside itself.
Fully deterministic: fixed seed, no clock, no network.
It counts the story items it renders from its own data structures
and prints the count.
"""

import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- constants
W = H = 1024
MARGIN = 22
PAGE_W = W - 2 * MARGIN            # 980
COL_GAP = 12
COL_W = (PAGE_W - COL_GAP) // 2    # 484
COL_L = MARGIN
COL_R = MARGIN + COL_W + COL_GAP

FONT_DIR = "/usr/share/fonts/truetype/noto"
DEJAVU_DIR = "/usr/share/fonts/truetype/dejavu"

SERIF_BLACK = "NotoSerif-Black.ttf"
SERIF_BOLD = "NotoSerif-Bold.ttf"
SERIF_REG = "NotoSerif-Regular.ttf"
SERIF_IT = "NotoSerif-Italic.ttf"
SANS_BOLD = "NotoSans-Bold.ttf"
SANS_REG = "NotoSans-Regular.ttf"
SANS_SB = "NotoSans-SemiBold.ttf"

_font_cache = {}


def F(name, size, directory=FONT_DIR):
    key = (name, size, directory)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(f"{directory}/{name}", size)
    return _font_cache[key]


def SYM(size):
    return F("DejaVuSans-Bold.ttf", size, DEJAVU_DIR)


# ---------------------------------------------------------------- palette
PAPER = (247, 241, 227)
PAPER_DEEP = (240, 231, 208)
INK = (26, 23, 18)
INK_SOFT = (58, 52, 44)
GRAY = (110, 100, 86)
RULE = (196, 184, 156)
RULE_DARK = (90, 80, 64)

C_WORLD = (127, 29, 29)
C_MONEY = (30, 86, 49)
C_SCIENCE = (15, 94, 104)
C_SOCIETY = (94, 53, 177)
C_SPORT = (20, 33, 61)
C_DARK = (24, 22, 20)
C_RED = (164, 38, 30)
C_GOLD = (176, 132, 30)

# ---------------------------------------------------------------- data
HEROES = [
    {
        "kicker": "APEC SUMMIT · SHENZHEN",
        "source": "NYT / BBC",
        "headline": "Trump, Xi and Putin Meet in Shenzhen",
        "deck": ("Xi embraced Trump on the tarmac as APEC leaders gathered in "
                 "Shenzhen for a rare trilateral with Putin."),
        "glance": "AT A GLANCE — Tarmac embrace · Trilateral talks · APEC plenary",
        "scene": "shenzhen",
        "accent": C_WORLD,
    },
    {
        "kicker": "STRAIT OF HORMUZ · ESCALATION",
        "source": "WIRE REPORTS",
        "headline": "Iran Strikes US Sites as Carriers Converge on Hormuz",
        "deck": ("Iran hit US drone and missile sites in Kuwait and Bahrain; US "
                 "forces struck Qeshm Island as a third carrier arrived."),
        "glance": "AT A GLANCE — Qeshm struck · Merchant ship hit · 3 carriers in region",
        "scene": "hormuz",
        "accent": C_SPORT,
    },
]

SECTIONS = [
    {
        "name": "WORLD", "color": C_WORLD, "thumb": "bridge",
        "cards": [
            ("KERCH STRAIT", "Crimean Bridge Attacked Again, Official Says",
             "A Russian official reports a fresh strike on the Kerch crossing "
             "linking Crimea to mainland Russia."),
            ("BRUSSELS", "EU Proposes €45bn Loan for Ukraine",
             "The loan would be repaid only after Russia pays reparations."),
            ("GAZA", "Israel Launches Rare Gaza Ground Operation",
             "Israeli forces move beyond the Yellow Line in a rare incursion."),
            ("PYONGYANG", "North Korea Fires Ballistic Missiles",
             "The launch came hours after a US–South Korea–Japan joint drill."),
            ("THE HAGUE", "Myanmar Faces Historic UN Genocide Verdict",
             "Judges rule on the Rohingya case in a landmark genocide verdict."),
            ("CANBERRA", "Australia Sanctions Israeli Settlers",
             "Canberra targets settlers over West Bank expansion."),
            ("WASHINGTON", "Democrats Nominate Hakeem Jeffries",
             "Jeffries is set to become the first Black Speaker of the House."),
        ],
    },
    {
        "name": "SCIENCE & PLANET", "color": C_SCIENCE, "thumb": "voyager",
        "cards": [
            ("DEEP SPACE", "Voyager 1 Reaches One Light-Day",
             "NASA's Voyager 1 hits the one-light-day milestone, nearly 50 "
             "years after launch."),
            ("OCEANS", "Nearly All Coral Reefs Face Extinction",
             "An IUCN study warns reefs could vanish within 50 years."),
            ("FINLAND", "Finland Approves Permanent Nuclear Repository",
             "The world's first permanent nuclear waste repository is approved."),
            ("BAY OF BENGAL", "Cyclone Akvan Bears Down on the Coast",
             "Akvan is set to cross the Machilipatnam–Puri coast on 20 November."),
            ("ORBIT", "ESA Chief Calls for Space Laws",
             "Europe's space chief urges space laws and satellite surveillance."),
        ],
    },
    {
        "name": "MONEY & TECH", "color": C_MONEY, "thumb": "chart",
        "cards": [
            ("IPO WATCH", "Anthropic Raises $81.3bn in Record IPO",
             "The biggest IPO of all time leaves Anthropic poised for a "
             "$1.4tn market debut."),
            ("NVIDIA", "Jensen Huang Steps Down at Nvidia",
             "Acting CEO Colette Kress promises earlier raises; H-series "
             "China shipments halted."),
            ("FED WATCH", "Fed Officials Expect Further Rate Hikes",
             "Minutes show most officials expect further rate hikes ahead."),
            ("ENERGY", "Oil Prices Drop as Supplies Improve",
             "Improving supplies outweigh Middle East tensions in the market."),
            ("INDIA", "Amazon Pledges $7bn for Renewables in India",
             "The $7bn renewable-energy investment runs through 2030."),
            ("HAMBURG", "Germany Blocks Cosco Takeover of Zippel",
             "Berlin stops Cosco's bid for the Hamburg logistics firm Zippel."),
        ],
    },
    {
        "name": "SOCIETY & CULTURE", "color": C_SOCIETY, "thumb": "vice",
        "cards": [
            ("GAMING", "GTA VI Begins Its Global Rollout",
             "Gamers enter Vice City as the game launches worldwide after a "
             "13-year wait. (AP/BBC)"),
            ("ART MARKET", "Van Gogh Sells for Record $190.4m",
             "The record sale followed a row over the painting's Nazi history."),
            ("PEW STUDY", "Islam on Track to Be Largest Religion by 2035",
             "Pew projects Islam to become the world's largest religion by 2035."),
            ("FRANCE", "France Sees Fourth Weekend of Protests",
             "Protesters rally for a fourth weekend over living costs."),
            ("LONDON", "Modi Meets Prince and Princess of Wales",
             "The meeting in London centred on UK–India ties."),
            ("OBITUARY", "Pearl Harbor Survivor Gebhard Galle Dies at 105",
             "Gebhard Galle, a Pearl Harbor survivor, has died aged 105."),
        ],
    },
]

SPORT = [
    ("INDIA 2–1 PAKISTAN", "SAFF Championship final in Dhaka — India lift the trophy"),
    ("MAVERICKS 116–94 WARRIORS", "Cooper Flagg scores 33 points with 9 assists"),
    ("CAVALIERS 105–102 GRIZZLIES", "Cleveland edge a three-point thriller"),
    ("ENGLAND v AUSTRALIA · ODI", "Ben Duckett hits 133 as England take charge"),
    ("INDIA WOMEN v MALAYSIA", "Asian Champions Trophy hockey opener in Bhopal"),
]

NUMBERS = [
    ("$190.4M", "VAN GOGH RECORD"),
    ("$81.3BN", "ANTHROPIC IPO"),
    ("€45BN", "EU UKRAINE LOAN"),
    ("$12BN", "VENEZUELAN OIL"),
    ("$7BN", "AMAZON INDIA ENERGY"),
    ("1 LIGHT-DAY", "VOYAGER 1 MILESTONE"),
    ("56–44", "US SENATE MAJORITY"),
    ("105 YRS", "PEARL HARBOR SURVIVOR"),
]

MARKETS = [
    {"kind": "oil", "name": "OIL", "note": "Prices drop as improving supply "
     "outweighs Middle East tensions", "down": True},
    {"kind": "gold", "name": "GOLD", "note": "Prices slip as a strong dollar "
     "weighs on the metal", "down": True},
    {"kind": "storm", "name": "ANDHRA COAST", "note": "Cyclone Akvan makes "
     "landfall on 20 November", "down": False},
]

TICKER = [
    "EU extends Russia sanctions three more years",
    "Berlin charges alleged Russian informant Ilona W.",
    "Jaishankar: defence ties key ahead of India–Japan 2+2",
    "World COPD Day urges early diagnosis",
    "German climber survives 100-metre Alps fall",
    "LPG tanker sunk off Bulgaria was hit by projectiles, official says",
    "Congress targets Modi government over inflation, seeks white paper",
    "Saudi Arabia says danger has passed in three southern cities",
]

STORY_COUNT = (
    len(HEROES)
    + sum(len(s["cards"]) for s in SECTIONS)
    + len(SPORT)
    + len(NUMBERS)
    + len(MARKETS)
    + len(TICKER)
)

# ---------------------------------------------------------------- helpers


def tw(d, s, font):
    return d.textlength(s, font=font)


def wrap(d, s, font, maxw):
    words = s.split()
    lines, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(d, t, font) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def tracked(d, xy, s, font, fill, tracking=2):
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=font, fill=fill)
        x += tw(d, ch, font) + tracking
    return x - tracking


def tracked_w(d, s, font, tracking=2):
    return sum(tw(d, ch, font) for ch in s) + tracking * (len(s) - 1)


def fit_size(d, s, name, start, min_size, maxw):
    size = start
    while size > min_size and tw(d, s, F(name, size)) > maxw:
        size -= 1
    return size


def paper_texture(img):
    """Subtle deterministic halftone/noise grain over the whole page."""
    rng = random.Random(20261119)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for _ in range(5200):
        x = rng.randrange(W)
        y = rng.randrange(H)
        a = rng.randrange(3, 9)
        tone = rng.choice([(120, 100, 70), (255, 252, 240)])
        od.point((x, y), fill=tone + (a,))
    for _ in range(700):
        x = rng.randrange(W - 2)
        y = rng.randrange(H)
        a = rng.randrange(3, 7)
        od.line([(x, y), (x + 2, y)], fill=(120, 100, 70, a))
    img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"),
              (0, 0))
    return img


# ---------------------------------------------------------------- hero art

def scene_shenzhen(d, x, y, w, h):
    # sky bands
    d.rectangle([x, y, x + w, y + h], fill=(214, 230, 240))
    d.rectangle([x, y + h * 2 // 3, x + w, y + h], fill=(238, 226, 196))
    # halftone dots in sky
    for i in range(26):
        for j in range(4):
            cx = x + 12 + i * 18
            cy = y + 8 + j * 14
            d.ellipse([cx, cy, cx + 2, cy + 2], fill=(170, 196, 214))
    # sun
    sx, sy = x + w - 78, y + 26
    d.ellipse([sx - 24, sy - 24, sx + 24, sy + 24], fill=(246, 196, 84))
    d.ellipse([sx - 17, sy - 17, sx + 17, sy + 17], fill=(250, 214, 110))
    # clouds
    for (cx, cy, s) in [(x + 40, y + 20, 1.0), (x + 150, y + 12, 0.7),
                        (x + 268, y + 30, 0.85)]:
        cw, chh = int(64 * s), int(16 * s)
        d.ellipse([cx, cy, cx + cw, cy + chh], fill=(250, 250, 246))
        d.ellipse([cx + cw // 4, cy - int(8 * s), cx + cw * 3 // 4,
                   cy + chh], fill=(250, 250, 246))
    # birds
    for (bx, by) in [(x + 96, y + 52), (x + 116, y + 60), (x + 330, y + 16)]:
        d.arc([bx, by, bx + 10, by + 6], 200, 330, fill=INK_SOFT, width=1)
        d.arc([bx + 9, by, bx + 19, by + 6], 210, 340, fill=INK_SOFT, width=1)
    # skyline
    base = y + h - 46
    towers = [(6, 58, 30), (42, 84, 24), (72, 44, 34), (112, 96, 26),
              (144, 62, 30), (386, 74, 28), (420, 50, 32)]
    for (tx, th, twd) in towers:
        d.rectangle([x + tx, base - th, x + tx + twd, base], fill=(74, 92, 110))
        for wy in range(base - th + 6, base - 6, 9):
            for wx in range(x + tx + 4, x + tx + twd - 4, 7):
                d.rectangle([wx, wy, wx + 3, wy + 4], fill=(238, 220, 150))
    d.rectangle([x + 112, base - 104, x + 138, base - 96], fill=(74, 92, 110))
    # flag poles + flags (centre)
    pole_x = [x + 196, x + 232, x + 268]
    flag_cols = [(178, 34, 34), (36, 74, 140), (178, 34, 34)]
    for i, px in enumerate(pole_x):
        d.line([(px, base), (px, base - 108)], fill=(52, 48, 44), width=2)
        d.polygon([(px, base - 108), (px + 30, base - 100), (px, base - 90)],
                  fill=flag_cols[i])
        if i == 1:
            for s_ in range(3):
                d.line([(px + 3, base - 105 + s_ * 5), (px + 27,
                         base - 103 + s_ * 5)], fill=(240, 240, 240), width=1)
    # tarmac
    d.rectangle([x, base, x + w, y + h], fill=(168, 158, 140))
    for i in range(7):
        lx = x + 14 + i * 66
        d.line([(lx, y + h - 8), (lx + 26, y + h - 8)], fill=(240, 236, 220),
               width=2)
    # jet on tarmac
    jx, jy = x + 300, base + 12
    d.polygon([(jx, jy), (jx + 74, jy + 5), (jx + 96, jy + 12), (jx + 74,
              jy + 15), (jx + 8, jy + 13)], fill=(238, 238, 234),
              outline=(90, 90, 90))
    d.polygon([(jx + 8, jy), (jx - 8, jy - 10), (jx + 16, jy + 2)],
              fill=(178, 34, 34))
    d.polygon([(jx + 44, jy + 4), (jx + 60, jy - 8), (jx + 66, jy + 5)],
              fill=(200, 200, 196))
    for wx in range(jx + 16, jx + 66, 8):
        d.ellipse([wx, jy + 6, wx + 3, jy + 9], fill=(60, 90, 130))
    # red carpet
    d.polygon([(x + 178, y + h - 4), (x + 292, y + h - 4), (x + 262, base + 8),
               (x + 208, base + 8)], fill=(164, 38, 30))
    d.line([(x + 182, y + h - 4), (x + 210, base + 8)], fill=(216, 178, 90),
           width=1)
    d.line([(x + 288, y + h - 4), (x + 260, base + 8)], fill=(216, 178, 90),
           width=1)
    # crowd silhouettes
    for i in range(15):
        cx = x + 22 + i * 12
        cy = y + h - 18
        d.ellipse([cx, cy, cx + 6, cy + 6], fill=(40, 38, 36))
        d.pieslice([cx - 2, cy + 5, cx + 8, cy + 15], 180, 360,
                   fill=(40, 38, 36))
    for i in range(11):
        cx = x + w - 150 + i * 12
        cy = y + h - 18
        d.ellipse([cx, cy, cx + 6, cy + 6], fill=(40, 38, 36))
        d.pieslice([cx - 2, cy + 5, cx + 8, cy + 15], 180, 360,
                   fill=(40, 38, 36))


def scene_hormuz(d, x, y, w, h):
    # hazy sky
    d.rectangle([x, y, x + w, y + 44], fill=(226, 216, 188))
    d.ellipse([x + 26, y + 8, x + 62, y + 40], fill=(244, 200, 110))
    sea_y = y + 44
    d.rectangle([x, sea_y, x + w, y + h], fill=(52, 96, 124))
    # coastlines both sides
    d.polygon([(x, sea_y), (x + 92, sea_y), (x + 66, sea_y + 40),
               (x + 84, sea_y + 74), (x, y + h)], fill=(196, 172, 122))
    d.polygon([(x + w, sea_y), (x + w - 96, sea_y), (x + w - 60, sea_y + 36),
               (x + w - 88, sea_y + 78), (x + w, y + h)], fill=(186, 160, 112))
    # strait dashed route
    for i in range(9):
        rx = x + 120 + i * 26
        d.line([(rx, sea_y + 52), (rx + 14, sea_y + 52)], fill=(240, 240, 230),
               width=2)
    # wave lines
    rng = random.Random(7)
    for r in range(6):
        wy = sea_y + 12 + r * 15
        for i in range(16):
            wx = x + 96 + i * 22 + (r % 2) * 9
            if wx < x + w - 108:
                d.arc([wx, wy, wx + 12, wy + 5], 180, 360,
                      fill=(140, 186, 205), width=1)
    # aircraft carrier (centre)
    cx, cy = x + 128, sea_y + 58
    cw_ = 216
    d.polygon([(cx, cy + 26), (cx + 16, cy + 40), (cx + cw_ - 8, cy + 40),
               (cx + cw_ + 14, cy + 24), (cx + cw_, cy + 18), (cx + 8, cy + 18)],
              fill=(64, 70, 78))
    d.rectangle([cx - 4, cy + 12, cx + cw_ + 8, cy + 20], fill=(88, 96, 106))
    # island tower
    d.rectangle([cx + 148, cy - 16, cx + 172, cy + 12], fill=(88, 96, 106))
    d.rectangle([cx + 152, cy - 24, cx + 168, cy - 16], fill=(64, 70, 78))
    d.line([(cx + 160, cy - 38), (cx + 160, cy - 24)], fill=(40, 40, 40),
           width=2)
    for wx in range(cx + 152, cx + 170, 6):
        d.rectangle([wx, cy - 6, wx + 3, cy - 2], fill=(220, 232, 240))
    # deck planes
    for px in (cx + 22, cx + 66, cx + 108):
        d.polygon([(px, cy + 16), (px + 20, cy + 13), (px + 28, cy + 16),
                   (px + 20, cy + 18)], fill=(210, 214, 218))
        d.polygon([(px + 4, cy + 15), (px - 2, cy + 9), (px + 9, cy + 14)],
                  fill=(190, 194, 198))
    # wake
    for i in range(4):
        d.line([(cx - 8 - i * 4, cy + 42 + i * 2), (cx - 44 - i * 10,
                cy + 44 + i * 3)], fill=(200, 224, 234), width=1)
        d.line([(cx + cw_ + 6, cy + 40), (cx + cw_ + 34 + i * 6, cy + 42 + i * 2)],
               fill=(200, 224, 234), width=1)
    # escort ship (right, smaller)
    ex, ey = x + w - 108, sea_y + 30
    d.polygon([(ex, ey + 16), (ex + 8, ey + 24), (ex + 62, ey + 24),
               (ex + 72, ey + 14), (ex + 60, ey + 10), (ex + 8, ey + 10)],
              fill=(70, 78, 88))
    d.rectangle([ex + 26, ey, ex + 42, ey + 10], fill=(96, 104, 114))
    d.line([(ex + 34, ey - 10), (ex + 34, ey)], fill=(40, 40, 40), width=1)
    # merchant ship (far left in strait)
    mx, my = x + 108, sea_y + 16
    d.polygon([(mx, my + 10), (mx + 6, my + 16), (mx + 44, my + 16),
               (mx + 50, my + 9), (mx + 40, my + 6), (mx + 6, my + 6)],
              fill=(150, 60, 44))
    d.rectangle([mx + 12, my, mx + 34, my + 6], fill=(120, 120, 116))
    # place markers
    lab = F(SANS_BOLD, 9)
    for (tx, ty, name) in [(x + 16, sea_y + 62, "QESHM"),
                           (x + w - 62, sea_y + 8, "KUWAIT"),
                           (x + w - 66, sea_y + 84, "BAHRAIN")]:
        d.ellipse([tx, ty, tx + 7, ty + 7], fill=C_RED, outline=(255, 250, 240))
        d.text((tx + 10, ty - 2), name, font=lab, fill=(30, 28, 24))


# ---------------------------------------------------------------- thumbs

def thumb_bridge(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=(196, 222, 234))
    d.rectangle([x, y + s - 12, x + s, y + s], fill=(52, 96, 124))
    for i in range(4):
        d.arc([x + 4 + i * 10, y + s - 15, x + 14 + i * 10, y + s - 9],
              180, 360, fill=(220, 238, 246), width=1)
    d.rectangle([x + 6, y + 8, x + 9, y + s - 12], fill=(90, 90, 90))
    d.rectangle([x + s - 9, y + 8, x + s - 6, y + s - 12], fill=(90, 90, 90))
    d.arc([x + 4, y + 2, x + s - 4, y + s - 8], 180, 360, fill=(164, 38, 30),
          width=2)
    d.rectangle([x, y + s - 16, x + s, y + s - 13], fill=(70, 70, 70))
    d.rectangle([x + 18, y + s - 21, x + 26, y + s - 16], fill=(200, 60, 40))


def thumb_chart(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=(232, 240, 226))
    for i in range(3):
        d.line([(x + 5, y + 10 + i * 11), (x + s - 5, y + 10 + i * 11)],
               fill=(200, 210, 190), width=1)
    pts = [(x + 5, y + s - 10), (x + 15, y + s - 16), (x + 24, y + s - 13),
           (x + 33, y + s - 24), (x + s - 6, y + 8)]
    d.line(pts, fill=C_MONEY, width=2)
    d.polygon([(x + s - 6, y + 8), (x + s - 13, y + 9), (x + s - 7, y + 15)],
              fill=C_MONEY)
    for (px, py) in [(x + 10, y + 10), (x + s - 14, y + s - 12)]:
        d.ellipse([px, py, px + 9, py + 9], fill=(216, 178, 60),
                  outline=(150, 118, 30))
        d.text((px + 2, py + 1), "$", font=F(SANS_BOLD, 7), fill=(90, 70, 10))


def thumb_voyager(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=(24, 30, 52))
    rng = random.Random(11)
    for _ in range(16):
        sx = x + rng.randrange(4, s - 4)
        sy = y + rng.randrange(4, s - 4)
        d.point((sx, sy), fill=(240, 240, 220))
        if rng.random() < 0.3:
            d.point((sx + 1, sy), fill=(200, 200, 190))
    # dish
    d.pieslice([x + 8, y + 10, x + 32, y + 32], 300, 130, fill=(226, 226, 220))
    d.line([(x + 20, y + 20), (x + 30, y + 8)], fill=(226, 226, 220), width=1)
    d.ellipse([x + 29, y + 6, x + 33, y + 10], fill=(250, 214, 110))
    d.line([(x + 20, y + 24), (x + 14, y + s - 6)], fill=(180, 180, 175),
           width=2)
    d.line([(x + 20, y + 24), (x + 28, y + s - 6)], fill=(180, 180, 175),
           width=2)
    # signal arcs
    for r in (8, 13, 18):
        d.arc([x + 30 - r // 2, y + 4 - r // 3, x + 30 + r, y + 6 + r],
              300, 60, fill=(140, 200, 230), width=1)


def thumb_vice(d, x, y, s):
    d.rectangle([x, y, x + s, y + s], fill=(250, 196, 150))
    d.ellipse([x + s - 18, y + 5, x + s - 5, y + 18], fill=(246, 160, 60))
    d.rectangle([x, y + s - 12, x + s, y + s], fill=(90, 170, 190))
    for (bx, bh) in [(4, 14), (13, 20), (24, 12)]:
        d.rectangle([x + bx, y + s - 12 - bh, x + bx + 7, y + s - 12],
                    fill=(70, 60, 90))
    # palm
    px, py = x + s - 14, y + s - 12
    d.line([(px, py), (px - 3, py - 18)], fill=(90, 64, 40), width=2)
    for a in range(5):
        ex = px - 3 + (a - 2) * 5
        d.arc([ex - 5, py - 24, ex + 6, py - 13], 180, 330, fill=(40, 130, 70),
              width=2)


THUMBS = {"bridge": thumb_bridge, "chart": thumb_chart,
          "voyager": thumb_voyager, "vice": thumb_vice}

# ---------------------------------------------------------------- sections


def draw_masthead(d):
    # top double rule
    d.rectangle([MARGIN, 22, W - MARGIN, 25], fill=INK)
    d.line([(MARGIN, 29), (W - MARGIN, 29)], fill=INK, width=1)
    meta = F(SANS_BOLD, 10)
    d.text((MARGIN, 34), "Vol. I · No. 19", font=meta, fill=INK_SOFT)
    centre = "INDEPENDENT · PRINTED ON ONE PAGE"
    d.text(((W - tw(d, centre, meta)) / 2, 34), centre, font=meta,
           fill=INK_SOFT)
    right = "50 STORIES · ONE PAGE · ONE DAY"
    d.text((W - MARGIN - tw(d, right, meta), 34), right, font=meta,
           fill=INK_SOFT)
    # nameplate
    name = "THE WHOLE DAY"
    size = fit_size(d, name, SERIF_BLACK, 50, 30, 720)
    nf = F(SERIF_BLACK, size)
    d.text(((W - tw(d, name, nf)) / 2, 44), name, font=nf, fill=INK)
    # date line
    date = ("Thursday, 19 November 2026   —   BROADSHEET EDITION · "
            "ALL THE DAY'S NEWS ON ONE PAGE")
    df = F(SANS_BOLD, 11)
    d.text(((W - tw(d, date, df)) / 2, 99), date, font=df, fill=C_RED)
    d.line([(MARGIN, 114), (W - MARGIN, 114)], fill=INK, width=1)
    d.rectangle([MARGIN, 117, W - MARGIN, 120], fill=INK)
    return 122


HERO_H = 262


def draw_hero(d, hero, x, y, w):
    h = HERO_H
    # offset shadow
    d.rectangle([x + 3, y + 3, x + w + 3, y + h + 3], fill=(222, 212, 186))
    d.rectangle([x, y, x + w, y + h], fill=(252, 248, 238), outline=RULE_DARK,
                width=1)
    accent = hero["accent"]
    # kicker bar
    d.rectangle([x, y, x + w, y + 16], fill=accent)
    kf = F(SANS_BOLD, 10)
    tracked(d, (x + 10, y + 3), hero["kicker"], kf, (255, 252, 244), 1)
    sf = F(SANS_BOLD, 9)
    d.text((x + w - 10 - tw(d, hero["source"], sf), y + 3), hero["source"],
           font=sf, fill=(255, 252, 244))
    # art
    ax, ay, aw, ah = x + 6, y + 19, w - 12, 150
    clip = Image.new("RGB", (aw, ah), PAPER)
    cd = ImageDraw.Draw(clip)
    if hero["scene"] == "shenzhen":
        scene_shenzhen(cd, 0, 0, aw, ah)
    else:
        scene_hormuz(cd, 0, 0, aw, ah)
    d._image.paste(clip, (ax, ay))
    d.rectangle([ax, ay, ax + aw, ay + ah], outline=RULE_DARK, width=1)
    # text block: headline + deck + at-a-glance, centred in the zone
    # below the art so both heroes sit balanced.
    hf = F(SERIF_BOLD, 22)
    head_lines = wrap(d, hero["headline"], hf, w - 20)[:2]
    df = F(SANS_REG, 11)
    deck_lines = wrap(d, hero["deck"], df, w - 20)[:2]
    gf = F(SANS_BOLD, 9)
    block_h = len(head_lines) * 23 + 3 + len(deck_lines) * 11 + 4 + 10
    zone_y = ay + ah + 4
    zone_h = (y + h - 3) - zone_y
    hy = zone_y + max(0, (zone_h - block_h) // 2)
    for ln in head_lines:
        d.text((x + 10, hy), ln, font=hf, fill=INK)
        hy += 23
    hy += 3
    for ln in deck_lines:
        d.text((x + 10, hy), ln, font=df, fill=INK_SOFT)
        hy += 11
    hy += 4
    d.text((x + 10, hy), hero["glance"], font=gf, fill=accent)
    return y + h


def draw_section_header(d, sec, x, y, w):
    col = sec["color"]
    d.rectangle([x, y, x + w, y + 18], fill=col)
    tf = F(SERIF_BOLD, 12)
    tracked(d, (x + 10, y + 3), sec["name"], tf, (255, 252, 244), 1)
    tag = f"{len(sec['cards'])} STORIES"
    gf = F(SANS_BOLD, 9)
    d.text((x + w - 10 - tw(d, tag, gf), y + 5), tag, font=gf,
           fill=(255, 252, 244))
    return y + 18


def draw_card(d, sec, idx, card, x, y, w):
    """Draw one story card; returns the y just below it."""
    kicker, headline, deck = card
    col = sec["color"]
    lead = idx == 0
    text_x = x + 2
    text_w = w - 4
    if lead:
        ts = 40
        THUMBS[sec["thumb"]](d, x + 2, y + 2, ts)
        d.rectangle([x + 2, y + 2, x + 2 + ts, y + 2 + ts], outline=RULE_DARK,
                    width=1)
        text_x = x + 2 + ts + 9
        text_w = w - (text_x - x) - 2
    # headline line: kicker (sans caps, section colour) + serif headline
    kf = F(SANS_BOLD, 10)
    kw = tw(d, kicker, kf) + 8
    hf_size = 13
    hf = F(SERIF_BOLD, hf_size)
    if tw(d, headline, hf) > text_w - kw:
        print(f"WARNING: headline too wide: {headline}", file=sys.stderr)
    cy = y + 2
    d.text((text_x, cy + 2), kicker, font=kf, fill=col)
    d.text((text_x + kw, cy), headline, font=hf, fill=INK)
    cy += 15
    # deck
    df = F(SANS_REG, 10)
    max_lines = 2 if lead else 1
    deck_lines = wrap(d, deck, df, text_w)
    if len(deck_lines) > max_lines:
        print(f"WARNING: deck wraps {len(deck_lines)} lines: {deck}",
              file=sys.stderr)
    for ln in deck_lines[:max_lines]:
        d.text((text_x, cy), ln, font=df, fill=INK_SOFT)
        cy += 11
    bottom = max(cy, y + 2 + 40 + 1) if lead else cy
    d.line([(x + 2, bottom), (x + w - 2, bottom)], fill=RULE, width=1)
    return bottom + 1


def draw_column(d, sections, x, y, w):
    cy = y
    for si, sec in enumerate(sections):
        if si:
            cy += 5
        cy = draw_section_header(d, sec, x, cy, w) + 2
        for idx, card in enumerate(sec["cards"]):
            cy = draw_card(d, sec, idx, card, x, cy, w)
    return cy


# ---------------------------------------------------------------- bands

def draw_sport(d, y):
    h = 40
    d.rectangle([MARGIN, y, W - MARGIN, y + h], fill=C_SPORT)
    lf = F(SERIF_BLACK, 14)
    d.text((MARGIN + 12, y + 5), "SPORT", font=lf, fill=(255, 252, 244))
    tf = F(SANS_BOLD, 8)
    tracked(d, (MARGIN + 13, y + 24), "SCOREBOARD", tf, (190, 205, 230), 1)
    ix = MARGIN + 96
    iw = (W - MARGIN - ix - 8) // 5
    for i, (score, caption) in enumerate(SPORT):
        cx = ix + i * iw
        if i:
            d.line([(cx - 5, y + 6), (cx - 5, y + h - 6)],
                   fill=(90, 110, 150), width=1)
        s_size = 11
        while s_size > 9 and tw(d, score, F(SERIF_BOLD, s_size)) > iw - 6:
            s_size -= 1
        sf = F(SERIF_BOLD, s_size)
        d.text((cx, y + 4), score, font=sf, fill=(255, 226, 130))
        cf = F(SANS_REG, 9)
        ly = y + 19
        for ln in wrap(d, caption, cf, iw - 6)[:2]:
            d.text((cx, ly), ln, font=cf, fill=(226, 232, 240))
            ly += 10
    return y + h


def draw_numbers(d, y):
    # header strip
    hf = F(SANS_BOLD, 10)
    tracked(d, (MARGIN + 2, y), "BY THE NUMBERS", hf, C_RED, 2)
    sub = "THE DAY IN FIGURES"
    sf = F(SANS_REG, 9)
    d.text((W - MARGIN - 2 - tw(d, sub, sf), y + 1), sub, font=sf, fill=GRAY)
    ry = y + 14
    d.line([(MARGIN, ry), (W - MARGIN, ry)], fill=RULE_DARK, width=1)
    ry += 4
    cw_ = PAGE_W // 8
    lf = F(SANS_BOLD, 8)
    for i, (val, label) in enumerate(NUMBERS):
        cx = MARGIN + i * cw_
        if i:
            d.line([(cx - 6, ry + 2), (cx - 6, ry + 22)], fill=RULE, width=1)
        vs = 15
        while vs > 11 and tw(d, val, F(SERIF_BLACK, vs)) > cw_ - 10:
            vs -= 1
        d.text((cx, ry), val, font=F(SERIF_BLACK, vs), fill=INK)
        ly = ry + vs + 2
        for ln in wrap(d, label, lf, cw_ - 8)[:1]:
            d.text((cx, ly), ln, font=lf, fill=GRAY)
            ly += 10
    return y + 41


def sparkline(d, x, y, w, h, down, color):
    pts = []
    n = 7
    for i in range(n):
        px = x + i * (w // (n - 1))
        frac = i / (n - 1)
        base = frac if down else 1 - frac
        py = y + 3 + base * (h - 8) + ((i * 37) % 5) - 2
        pts.append((px, py))
    d.line(pts, fill=color, width=2)
    ex, ey = pts[-1]
    d.ellipse([ex - 2, ey - 2, ex + 2, ey + 2], fill=color)


def storm_icon(d, x, y, s):
    d.ellipse([x + 4, y + 4, x + s - 10, y + s - 14], fill=(120, 130, 140))
    d.ellipse([x + s - 22, y + 8, x + s - 2, y + s - 12], fill=(105, 116, 128))
    cx, cy = x + s // 2, y + s // 2 + 4
    for r in (11, 7):
        d.arc([cx - r, cy - r, cx + r, cy + r], 40, 300, fill=(240, 244, 248),
              width=2)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(240, 244, 248))
    for i in range(3):
        rx = x + 8 + i * 9
        d.line([(rx, y + s - 8), (rx - 3, y + s - 2)], fill=(70, 120, 170),
               width=2)


def draw_markets(d, y):
    hf = F(SANS_BOLD, 10)
    tracked(d, (MARGIN + 2, y), "MARKETS & WEATHER", hf, C_MONEY, 2)
    ry = y + 13
    cw_ = (PAGE_W - 2 * 10) // 3
    nf = F(SANS_BOLD, 11)
    tf = F(SANS_REG, 10)
    for i, item in enumerate(MARKETS):
        cx = MARGIN + i * (cw_ + 10)
        d.rectangle([cx, ry, cx + cw_, ry + 38], fill=(252, 248, 238),
                    outline=RULE, width=1)
        if item["kind"] == "storm":
            storm_icon(d, cx + 6, ry + 3, 32)
        else:
            color = C_RED if item["down"] else C_MONEY
            sparkline(d, cx + 8, ry + 8, 52, 22, item["down"], color)
            # down triangle
            tx, ty = cx + 66, ry + 9
            d.polygon([(tx, ty), (tx + 10, ty), (tx + 5, ty + 8)], fill=C_RED)
        tx = cx + 84
        d.text((tx, ry + 3), item["name"], font=nf, fill=INK)
        ly = ry + 17
        for ln in wrap(d, item["note"], tf, cw_ - (tx - cx) - 8)[:2]:
            d.text((tx, ly), ln, font=tf, fill=INK_SOFT)
            ly += 11
    return ry + 38


def draw_ticker(d, y):
    h = 38
    d.rectangle([MARGIN, y, W - MARGIN, y + h], fill=C_DARK)
    lf = F(SANS_BOLD, 10)
    d.rectangle([MARGIN + 8, y + 7, MARGIN + 92, y + 25], fill=C_RED)
    d.text((MARGIN + 15, y + 11), "LATE WIRE", font=lf, fill=(255, 252, 244))
    sep = "  ◆  "
    text = sep.join(TICKER)
    tf = F(SANS_REG, 10)
    tx = MARGIN + 104
    ly = y + 3
    for ln in wrap(d, text, tf, W - MARGIN - tx - 6)[:3]:
        # draw separators in red, rest in paper white
        cx = tx
        parts = ln.split("◆")
        for pi, part in enumerate(parts):
            if pi:
                d.text((cx, ly), "◆", font=SYM(8), fill=(240, 120, 100))
                cx += tw(d, "◆", SYM(8)) + 4
            d.text((cx, ly), part, font=tf, fill=(240, 236, 224))
            cx += tw(d, part, tf)
        ly += 11
    return y + h


# ---------------------------------------------------------------- main

def render():
    img = Image.new("RGB", (W, H), PAPER)
    img = paper_texture(img)
    d = ImageDraw.Draw(img)
    d._image = img  # allow hero art paste

    # page frame
    d.rectangle([9, 9, W - 10, H - 10], outline=RULE_DARK, width=1)
    d.rectangle([13, 13, W - 14, H - 14], outline=RULE, width=1)

    y = draw_masthead(d)                       # -> 122
    # heroes
    hero_y = y
    draw_hero(d, HEROES[0], COL_L, hero_y, COL_W)
    draw_hero(d, HEROES[1], COL_R, hero_y, COL_W)
    # body columns: left WORLD + SCIENCE, right MONEY + SOCIETY
    body_y = hero_y + HERO_H + 6
    left_end = draw_column(d, SECTIONS[0:2], COL_L, body_y, COL_W)
    right_end = draw_column(d, SECTIONS[2:4], COL_R, body_y, COL_W)
    body_end = max(left_end, right_end)
    # folio line
    folio = "— All 50 stories continued on this page · The Whole Day —"
    ff = F(SERIF_IT, 10)
    d.text(((W - tw(d, folio, ff)) / 2, body_end + 1), folio, font=ff,
           fill=GRAY)
    # bands
    y = body_end + 13
    y = draw_sport(d, y) + 5
    y = draw_numbers(d, y) + 3
    y = draw_markets(d, y) + 5
    y = draw_ticker(d, y)
    if y > H - 13:  # inner page frame sits at H-14
        print(f"WARNING: layout overflow, ends at y={y}", file=sys.stderr)
    return img


def main():
    out = Path(__file__).resolve().parent / "entry.png"
    img = render()
    img.save(out, format="PNG", optimize=True)
    print(f"STORY_COUNT={STORY_COUNT}")
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
