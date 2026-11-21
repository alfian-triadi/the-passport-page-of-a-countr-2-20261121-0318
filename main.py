#!/usr/bin/env python3
"""The Passport Page of a Country That Isn't There.

Draws one invented passport spread (data page + visa/stamps page) for the
Republic of Caldara, a volcanic island republic that does not exist, and
writes it to /output/entry.png (1024x720, under 1 MiB).

Deterministic: fixed seed, no network, no clock, no randomness outside the
seeded generator. Pillow only; runs on Python 3.13 in the grader sandbox.
"""

import math
import os
import random
from PIL import Image, ImageDraw, ImageFont

RNG = random.Random(20261121)

W, H = 1024, 720
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
OUT = os.path.join(OUT_DIR, "entry.png")

# ---- palette -------------------------------------------------------------
INK = (28, 42, 38)          # near-black green ink
PAGE = (246, 238, 219)      # warm passport paper
PAGE2 = (242, 232, 208)
COVER = (31, 58, 52)        # dark green cover edge
GOLD = (176, 141, 58)
TEAL = (15, 76, 74)
TEAL_D = (10, 54, 52)
CRIMSON = (122, 31, 43)
RULE = (120, 110, 88)
FAINT = (150, 138, 112)
SKIN = (201, 143, 102)
SKIN_D = (178, 118, 80)
SKIN_L = (214, 162, 122)
HAIR = (42, 29, 24)
HAIR_L = (74, 50, 38)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"
MONO_B = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text(d, xy, s, f, fill=INK, anchor="la"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def centre(d, cx, y, s, f, fill=INK):
    d.text((cx, y), s, font=f, fill=fill, anchor="ma")


# ---- MRZ (ICAO 9303, TD3) -------------------------------------------------
def mrz_check(s):
    weights = (7, 3, 1)
    total = 0
    for i, ch in enumerate(s):
        if ch.isdigit():
            v = int(ch)
        elif ch == "<":
            v = 0
        else:
            v = ord(ch) - 55
        total += v * weights[i % 3]
    return str(total % 10)


def mrz_lines():
    line1 = "P<CLDMAROVA<<ELENA<IVANA"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "CLD004821"
    dob = "940614"
    exp = "330312"
    personal = "<" * 14
    line2 = (
        doc + mrz_check(doc)
        + "CLD" + dob + mrz_check(dob)
        + "F" + exp + mrz_check(exp)
        + personal + mrz_check(personal)
    )
    line2 += mrz_check(line2)
    return line1, line2


# ---- helpers ---------------------------------------------------------------
def guilloche(d, box, colour, waves=5, step=9):
    """Faint wavy concentric arcs inside a box, like security printing."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    maxr = max(x1 - x0, y1 - y0)
    for r in range(18, maxr, step):
        pts = []
        for a in range(0, 361, 4):
            rad = math.radians(a)
            wob = 1.6 * math.sin(a * waves * math.pi / 180.0)
            pts.append((cx + (r + wob) * math.cos(rad) * 0.62,
                        cy + (r + wob) * math.sin(rad) * 0.9))
        d.line(pts, fill=colour, width=1)


def emblem(d, cx, cy, s):
    """Coat of arms of Caldara: shield, volcano, sun, waves."""
    # shield
    shield = [(cx - 0.42 * s, cy - 0.5 * s), (cx + 0.42 * s, cy - 0.5 * s),
              (cx + 0.42 * s, cy + 0.12 * s), (cx, cy + 0.55 * s),
              (cx - 0.42 * s, cy + 0.12 * s)]
    d.polygon(shield, outline=GOLD, width=3)
    d.polygon([(cx - 0.36 * s, cy - 0.44 * s), (cx + 0.36 * s, cy - 0.44 * s),
               (cx + 0.36 * s, cy + 0.10 * s), (cx, cy + 0.47 * s),
               (cx - 0.36 * s, cy + 0.10 * s)], fill=(232, 220, 186))
    # sun
    d.ellipse([cx - 0.13 * s, cy - 0.42 * s, cx + 0.13 * s, cy - 0.16 * s],
              fill=(214, 164, 62))
    # volcano
    d.polygon([(cx - 0.30 * s, cy + 0.16 * s), (cx - 0.06 * s, cy - 0.22 * s),
               (cx + 0.06 * s, cy - 0.22 * s), (cx + 0.30 * s, cy + 0.16 * s)],
              fill=(94, 52, 44))
    d.polygon([(cx - 0.06 * s, cy - 0.22 * s), (cx + 0.06 * s, cy - 0.22 * s),
               (cx + 0.02 * s, cy - 0.13 * s), (cx - 0.03 * s, cy - 0.13 * s)],
              fill=(246, 238, 219))
    # waves
    for i, yy in enumerate((0.20, 0.28, 0.36)):
        y = cy + yy * s
        pts = []
        for x in range(int(cx - 0.30 * s), int(cx + 0.30 * s) + 1, 4):
            pts.append((x, y + 2.5 * math.sin((x - cx) * 0.09 + i)))
        d.line(pts, fill=TEAL, width=2)
    # banner
    d.rectangle([cx - 0.30 * s, cy + 0.56 * s, cx + 0.30 * s, cy + 0.72 * s],
                outline=GOLD, width=2)


def portrait(d, box):
    """Flat-illustration portrait of the holder, Elena Ivana Marova."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    cx = (x0 + x1) // 2
    # background: deep teal gradient, calm and plain like a photo booth
    for yy in range(y0, y1):
        t = (yy - y0) / h
        col = tuple(int(TEAL[i] + (TEAL_D[i] - TEAL[i]) * t) for i in range(3))
        d.line([(x0, yy), (x1, yy)], fill=col)
    # shoulders / garment
    d.polygon([(x0 - 4, y1), (x0 - 4, y0 + h * 0.78),
               (cx - 62, y0 + h * 0.70), (cx + 62, y0 + h * 0.70),
               (x1 + 4, y0 + h * 0.78), (x1 + 4, y1)], fill=CRIMSON)
    # collar + gold trim
    d.polygon([(cx - 30, y0 + h * 0.72), (cx, y0 + h * 0.86),
               (cx + 30, y0 + h * 0.72), (cx + 18, y0 + h * 0.68),
               (cx, y0 + h * 0.76), (cx - 18, y0 + h * 0.68)], fill=(232, 220, 186))
    d.line([(cx - 30, y0 + h * 0.72), (cx, y0 + h * 0.86),
            (cx + 30, y0 + h * 0.72)], fill=GOLD, width=2)
    # neck
    d.rectangle([cx - 17, y0 + h * 0.58, cx + 17, y0 + h * 0.74], fill=SKIN_D)
    d.polygon([(cx - 17, y0 + h * 0.58), (cx + 17, y0 + h * 0.58),
               (cx + 12, y0 + h * 0.66), (cx - 12, y0 + h * 0.66)], fill=SKIN_D)
    # hair back mass
    d.ellipse([cx - 58, y0 + h * 0.06, cx + 58, y0 + h * 0.62], fill=HAIR)
    d.polygon([(cx - 58, y0 + h * 0.30), (cx - 66, y0 + h * 0.72),
               (cx - 40, y0 + h * 0.72), (cx - 46, y0 + h * 0.34)], fill=HAIR)
    d.polygon([(cx + 58, y0 + h * 0.30), (cx + 66, y0 + h * 0.72),
               (cx + 40, y0 + h * 0.72), (cx + 46, y0 + h * 0.34)], fill=HAIR)
    # face
    d.ellipse([cx - 44, y0 + h * 0.13, cx + 44, y0 + h * 0.60], fill=SKIN)
    # ears
    d.ellipse([cx - 50, y0 + h * 0.33, cx - 38, y0 + h * 0.44], fill=SKIN)
    d.ellipse([cx + 38, y0 + h * 0.33, cx + 50, y0 + h * 0.44], fill=SKIN)
    d.ellipse([cx + 40, y0 + h * 0.40, cx + 45, y0 + h * 0.44], fill=GOLD)
    # hairline: swept fringe with a side part, curved lower edge, high
    # on the forehead so the face reads clearly
    fringe = [(cx - 46, y0 + h * 0.26)]
    for i in range(21):
        t = i / 20.0
        x = cx - 46 + 92 * t
        y = y0 + h * (0.26 - 0.10 * math.sin(t * math.pi)
                      + 0.035 * math.sin(t * math.pi * 2))
        fringe.append((x, y))
    fringe.append((cx + 46, y0 + h * 0.26))
    fringe.append((cx + 46, y0 + h * 0.10))
    fringe.append((cx - 46, y0 + h * 0.10))
    d.polygon(fringe, fill=HAIR)
    d.pieslice([cx - 46, y0 + h * 0.10, cx + 46, y0 + h * 0.26], 180, 360,
               fill=HAIR)
    # centre part line
    d.line([(cx - 2, y0 + h * 0.115), (cx - 6, y0 + h * 0.20)],
           fill=SKIN, width=2)
    for dx in (-38, -30, 34):
        d.arc([cx + dx - 8, y0 + h * 0.12, cx + dx + 8, y0 + h * 0.30],
              300, 60, fill=HAIR_L, width=2)
    # brows
    d.arc([cx - 32, y0 + h * 0.28, cx - 8, y0 + h * 0.36], 200, 340,
          fill=(58, 36, 28), width=3)
    d.arc([cx + 8, y0 + h * 0.28, cx + 32, y0 + h * 0.36], 200, 340,
          fill=(58, 36, 28), width=3)
    # eyes
    for ex in (cx - 20, cx + 20):
        d.ellipse([ex - 10, y0 + h * 0.37, ex + 10, y0 + h * 0.405],
                  fill=(250, 246, 236))
        d.ellipse([ex - 4, y0 + h * 0.372, ex + 4, y0 + h * 0.402],
                  fill=(74, 48, 32))
        d.ellipse([ex - 2, y0 + h * 0.38, ex + 2, y0 + h * 0.392],
                  fill=(20, 16, 14))
        d.ellipse([ex + 2, y0 + h * 0.374, ex + 4, y0 + h * 0.380],
                  fill=(255, 255, 255))
        d.arc([ex - 10, y0 + h * 0.365, ex + 10, y0 + h * 0.408], 180, 360,
              fill=(30, 22, 18), width=2)
    # nose
    d.line([(cx + 1, y0 + h * 0.41), (cx - 2, y0 + h * 0.485)], fill=SKIN_D,
           width=2)
    d.arc([cx - 6, y0 + h * 0.475, cx + 6, y0 + h * 0.505], 0, 180,
          fill=SKIN_D, width=2)
    # lips
    d.polygon([(cx - 13, y0 + h * 0.535), (cx, y0 + h * 0.525),
               (cx + 13, y0 + h * 0.535), (cx, y0 + h * 0.545)],
              fill=(164, 74, 74))
    d.polygon([(cx - 11, y0 + h * 0.545), (cx, y0 + h * 0.540),
               (cx + 11, y0 + h * 0.545), (cx, y0 + h * 0.560)],
              fill=(140, 58, 58))
    # blush
    d.ellipse([cx - 38, y0 + h * 0.44, cx - 22, y0 + h * 0.485],
              fill=(196, 120, 96))
    d.ellipse([cx + 22, y0 + h * 0.44, cx + 38, y0 + h * 0.485],
              fill=(196, 120, 96))


def stamp(d, cx, cy, r, colour, lines, rot, scale=1.0):
    """Circular border-control stamp, drawn on its own layer and rotated."""
    size = int(r * 2 * scale) + 8
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    c = size // 2
    rr = int(r * scale)
    ld.ellipse([c - rr, c - rr, c + rr, c + rr], outline=colour + (210,),
               width=3)
    ld.ellipse([c - rr + 6, c - rr + 6, c + rr - 6, c + rr - 6],
               outline=colour + (210,), width=1)
    f_top = font(SANS_B, int(13 * scale) if len(lines[0]) <= 9
                 else int(11 * scale))
    f_mid = font(SANS_B, int(15 * scale))
    f_bot = font(MONO, int(11 * scale))
    ld.text((c, c - rr + 16 * scale), lines[0], font=f_top,
            fill=colour + (220,), anchor="ma")
    ld.text((c, c - 8 * scale), lines[1], font=f_mid, fill=colour + (225,),
            anchor="ma")
    ld.text((c, c + 12 * scale), lines[2], font=f_bot, fill=colour + (220,),
            anchor="ma")
    ld.text((c, c + rr - 26 * scale), lines[3] if len(lines) > 3 else "",
            font=f_bot, fill=colour + (200,), anchor="ma")
    layer = layer.rotate(rot, resample=Image.BICUBIC, expand=False)
    d._image.paste(layer, (int(cx - size // 2), int(cy - size // 2)), layer)


def rect_stamp(d, box, colour, title, lines, rot):
    """Rectangular visa/entry stamp."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    layer = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rectangle([4, 4, w + 3, h + 3], outline=colour + (215,), width=3)
    ld.line([(4, 26), (w + 3, 26)], fill=colour + (200,), width=1)
    ld.text((w // 2 + 4, 7), title, font=font(SANS_B, 13),
            fill=colour + (225,), anchor="ma")
    y = 36
    for ln in lines:
        ld.text((w // 2 + 4, y), ln, font=font(MONO, 12),
                fill=colour + (220,), anchor="ma")
        y += 17
    layer = layer.rotate(rot, resample=Image.BICUBIC, expand=False)
    d._image.paste(layer, (x0 - 4, y0 - 4), layer)


def draw_left_page(img, d):
    x0, y0, x1, y1 = 16, 16, 512, 704
    d.rectangle([x0, y0, x1, y1], fill=PAGE)
    guilloche(d, (x0 + 8, y0 + 8, x1 - 8, y1 - 8), (226, 214, 184))
    # header
    emblem(d, x0 + 52, y0 + 52, 62)
    centre(d, x0 + 300, y0 + 22, "REPUBLIC OF CALDARA",
           font(SERIF_B, 25), INK)
    centre(d, x0 + 300, y0 + 50, "REPUBLIKA CALDARA  ·  PASSPORT",
           font(SANS_B, 12), (94, 84, 66))
    d.line([(x0 + 118, y0 + 74), (x1 - 24, y0 + 74)], fill=RULE, width=1)
    centre(d, x0 + 300, y0 + 80, "PASPOR  ·  TRAVEL DOCUMENT",
           font(SANS, 10), FAINT)
    # type / code / number row
    y = y0 + 108
    for cx, lab, val in ((x0 + 60, "TYPE", "P"),
                         (x0 + 170, "CODE", "CLD"),
                         (x0 + 330, "PASSPORT No.", "CLD 0048217")):
        text(d, (cx, y), lab, font(SANS_B, 10), FAINT)
        text(d, (cx, y + 14), val, font(SANS_B, 16), INK)
    d.line([(x0 + 24, y + 36), (x1 - 24, y + 36)], fill=RULE, width=1)
    # portrait
    px0, py0, px1, py1 = x1 - 196, y0 + 158, x1 - 24, y0 + 158 + 216
    portrait(d, (px0, py0, px1, py1))
    d.rectangle([px0, py0, px1, py1], outline=INK, width=2)
    d.rectangle([px0 - 4, py0 - 4, px1 + 4, py1 + 4], outline=GOLD, width=1)
    text(d, (px0, py1 + 8), "PHOTOGRAPH", font(SANS, 8), FAINT, anchor="la")
    # data fields
    fx, fy = x0 + 24, y0 + 158
    fields = [
        ("SURNAME / FAMILE", "MAROVA"),
        ("GIVEN NAMES / NOMO", "ELENA IVANA"),
        ("NATIONALITY / NACIE", "CALDARAN"),
        ("DATE OF BIRTH / NASCI", "14 JUN 1994"),
        ("PLACE OF BIRTH / LOCO", "PORT EMBER, CALDARA"),
        ("SEX / SEXO", "F"),
        ("DATE OF ISSUE / DATUM", "12 MAR 2023"),
        ("DATE OF EXPIRY / FINO", "12 MAR 2033"),
        ("AUTHORITY / AUCTOR", "MINISTRY OF THE INTERIOR"),
    ]
    for lab, val in fields:
        text(d, (fx, fy), lab, font(SANS_B, 9), FAINT)
        text(d, (fx, fy + 12), val, font(SERIF_B, 15), INK)
        fy += 30
    # signature
    sy = y0 + 158 + 9 * 30 + 6
    text(d, (fx, sy), "HOLDER'S SIGNATURE", font(SANS_B, 9), FAINT)
    d.line([(fx, sy + 26), (fx + 200, sy + 26)], fill=INK, width=1)
    d.text((fx + 6, sy + 12), "Elena Marova", font=font(SERIF_I, 20),
           fill=(52, 52, 66))
    # conditions box (the telling paperwork detail)
    bx0, by0, bx1, by1 = x0 + 24, y1 - 118, x1 - 24, y1 - 34
    d.rectangle([bx0, by0, bx1, by1], outline=RULE, width=1)
    d.rectangle([bx0, by0, bx1, by0 + 18], fill=(232, 220, 186))
    text(d, (bx0 + 8, by0 + 4), "CONDITIONS  ·  KONDICIOJ",
         font(SANS_B, 10), INK)
    cond = ("Valid for travel to all countries except the Obsidian Exclusion "
            "Zone. A geothermal permit is required to enter the caldera "
            "districts. This passport remains the property of the Republic "
            "of Caldara.")
    words, lines, cur = cond.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if d.textlength(trial, font=font(SERIF, 11)) <= bx1 - bx0 - 16:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    lines.append(cur)
    yy = by0 + 24
    for ln in lines:
        text(d, (bx0 + 8, yy), ln, font(SERIF, 11), INK)
        yy += 14
    # MRZ
    mrz1, mrz2 = mrz_lines()
    my = y1 - 30
    d.rectangle([x0, my - 8, x1, y1], fill=(232, 226, 204))
    text(d, (x0 + 14, my - 2), mrz1, font(MONO, 15), INK)
    text(d, (x0 + 14, my + 14), mrz2, font(MONO, 15), INK)
    text(d, (x0 + 14, y1 - 12), "1", font(SANS, 9), FAINT)


def draw_right_page(img, d):
    x0, y0, x1, y1 = 512, 16, 1008, 704
    d.rectangle([x0, y0, x1, y1], fill=PAGE2)
    guilloche(d, (x0 + 8, y0 + 8, x1 - 8, y1 - 8), (222, 208, 176))
    centre(d, (x0 + x1) // 2, y0 + 20, "VISAS", font(SERIF_B, 22), INK)
    centre(d, (x0 + x1) // 2, y0 + 46, "VIZOJ  ·  ENTRIES AND EXITS",
           font(SANS_B, 10), FAINT)
    d.line([(x0 + 24, y0 + 64), (x1 - 24, y0 + 64)], fill=RULE, width=1)
    # Sarn visa vignette (top)
    vx0, vy0, vx1, vy1 = x0 + 40, y0 + 82, x1 - 40, y0 + 82 + 118
    layer = Image.new("RGBA", (vx1 - vx0 + 10, vy1 - vy0 + 10), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rectangle([5, 5, vx1 - vx0 + 4, vy1 - vy0 + 4],
                 fill=(238, 230, 204, 255), outline=(94, 60, 44, 230), width=2)
    ld.rectangle([5, 5, vx1 - vx0 + 4, 30], fill=(94, 60, 44, 255))
    ld.text(((vx1 - vx0) // 2 + 5, 8), "VISA  —  REPUBLIC OF SARN",
            font=font(SANS_B, 13), fill=(246, 238, 219), anchor="ma")
    # flag bars of Sarn: ochre / teal / rust
    for i, col in enumerate(((198, 150, 52), (18, 90, 86), (150, 62, 44))):
        ld.rectangle([14, 40 + i * 7, 54, 40 + i * 7 + 6], fill=col + (255,))
    ld.text((64, 38), "Type: C — Single entry, 30 days", font=font(SANS, 12),
            fill=INK)
    ld.text((64, 56), "Issued: 28 APR 2026, Port Ember", font=font(SANS, 12),
            fill=INK)
    ld.text((64, 74), "Valid until: 28 OCT 2026", font=font(SANS, 12),
            fill=INK)
    ld.text((14, 92), "No. SRN-2026-11873", font=font(MONO, 11), fill=INK)
    ld.text((vx1 - vx0 - 6, 92), "FEE PAID", font=font(SANS_B, 11),
            fill=(150, 62, 44), anchor="ra")
    layer = layer.rotate(-1.5, resample=Image.BICUBIC, expand=False)
    d._image.paste(layer, (vx0 - 5, vy0 - 5), layer)
    # stamps: consistent travel history, all after issue 12 MAR 2023
    stamp(d, x0 + 120, y0 + 300, 62, (38, 84, 140),
          ["TARNOVIA", "ENTRY", "08 APR 2024", "KESTREL XING"], -12)
    stamp(d, x0 + 330, y0 + 290, 58, (38, 84, 140),
          ["TARNOVIA", "EXIT", "22 APR 2024", "KESTREL XING"], 9)
    stamp(d, x0 + 130, y0 + 470, 60, (110, 60, 130),
          ["MAREN", "ENTRY", "17 SEP 2025", "HARBOUR"], -7)
    stamp(d, x0 + 330, y0 + 460, 60, (140, 52, 40),
          ["REP. OF SARN", "ENTRY", "03 MAY 2026", "DORNA"], 11)
    stamp(d, x0 + 110, y0 + 590, 56, (140, 52, 40),
          ["REP. OF SARN", "EXIT", "19 MAY 2026", "DORNA"], -14)
    stamp(d, x0 + 430, y0 + 590, 54, (24, 92, 70),
          ["CALDARA", "ENTRY", "19 MAY 2026", "PORT EMBER"], 6)
    # departure-tax fee stamp (free gap between the two bottom stamps)
    rect_stamp(d, (x0 + 195, y0 + 560, x0 + 345, y0 + 626),
               (24, 92, 70), "DEPARTURE TAX",
               ["PAID — 40 AUR", "19 MAY 2026"], -5)
    # observations line (ties to the conditions box)
    oy = y1 - 58
    d.line([(x0 + 24, oy - 10), (x1 - 24, oy - 10)], fill=RULE, width=1)
    text(d, (x0 + 24, oy), "OBSERVATIONS", font(SANS_B, 9), FAINT)
    text(d, (x0 + 24, oy + 13),
         "Holder is a licensed volcanologist — geothermal permit",
         font(SERIF_I, 12), INK)
    text(d, (x0 + 24, oy + 28), "No. GP-2214, caldera districts only.",
         font(SERIF_I, 12), INK)
    text(d, (x1 - 14, y1 - 12), "2", font(SANS, 9), FAINT, anchor="ra")


def main():
    img = Image.new("RGB", (W, H), COVER)
    d = ImageDraw.Draw(img)
    # paper texture: faint deterministic grain
    for _ in range(900):
        x = RNG.randint(16, W - 17)
        y = RNG.randint(16, H - 17)
        v = RNG.randint(0, 14)
        d.point((x, y), fill=(238 - v, 230 - v, 212 - v))
    draw_left_page(img, d)
    draw_right_page(img, d)
    # spine + outer frame
    d.rectangle([16, 16, 1008, 704], outline=COVER, width=3)
    d.line([(512, 18), (512, 702)], fill=(120, 108, 84), width=2)
    for xx in (508, 516):
        d.line([(xx, 18), (xx, 702)], fill=(60, 52, 40), width=1)
    os.makedirs(OUT_DIR, exist_ok=True)
    img.save(OUT, format="PNG")
    # The brief names /output/entry.png; if the harness points elsewhere,
    # leave a copy at the canonical path too (best effort).
    if OUT_DIR != "/output":
        try:
            os.makedirs("/output", exist_ok=True)
            img.save("/output/entry.png", format="PNG")
        except OSError:
            pass
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
