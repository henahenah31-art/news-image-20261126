#!/usr/bin/env python3
"""The World Today - 26 November 2026.

A pure-stdlib program that draws one 1024x1024 PNG summing up the world
news of 26 November 2026: 8 main stories + 30 briefs.
Deterministic: no time, no randomness, no network, no hash ordering.
Writes /output/entry.png
"""

import os
import struct
import sys
import zlib

W = 1024
H = 1024

WHITE = (255, 255, 255)
BLACK = (18, 18, 18)
NAVY = (16, 42, 92)
RED = (168, 28, 28)
GREY = (90, 90, 90)
LIGHT = (232, 236, 244)

# 5x7 bitmap font, typed from scratch. Each glyph: 7 rows of 5 bits.
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
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
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
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        for i in range(0, len(self.px), 3):
            self.px[i] = bg[0]
            self.px[i + 1] = bg[1]
            self.px[i + 2] = bg[2]

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                o = base + (xx - x0) * 3
                self.px[o] = color[0]
                self.px[o + 1] = color[1]
                self.px[o + 2] = color[2]

    def text(self, x, y, s, scale, color):
        s = s.upper()  # font is uppercase-only; fold lowercase here
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT["?"])
            for r in range(7):
                row = glyph[r]
                for c in range(5):
                    if row[c] == "1":
                        self.rect(cx + c * scale, y + r * scale, scale, scale, color)
            cx += 6 * scale
        return cx

    def text_width(self, s, scale):
        return len(s) * 6 * scale


def wrap(text, max_chars):
    """Greedy word wrap; returns list of lines, each <= max_chars."""
    lines = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for wd in words:
            if cur == "":
                cur = wd
            elif len(cur) + 1 + len(wd) <= max_chars:
                cur = cur + " " + wd
            else:
                lines.append(cur)
                cur = wd
        if cur != "":
            lines.append(cur)
    return lines


def draw_para(cv, x, y, text, scale, color, max_chars, line_h, max_lines=None):
    lines = wrap(text, max_chars)
    if max_lines is not None:
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        cv.text(x, y + i * line_h, ln, scale, color)
    return y + len(lines) * line_h


LEAD_HEAD = "MACY'S 100TH PARADE POSTPONED AS NOR'EASTER SLAMS NEW YORK"
LEAD_BODY = (
    "The 100th Macy's Thanksgiving Day Parade was postponed to Saturday, the "
    "first weather postponement in its history, as a major East Coast storm "
    "brings heavy rain and gusts over 50 mph. Organizers cited public safety."
)

# (headline, body) for mains 2..8
MAINS = [
    ("SAUDI ARABIA INTERCEPTS HOUTHI MISSILES OVER RIYADH",
     "Saudi defences shot down missiles over the capital after Houthi attacks "
     "on Jeddah and Jazan ports, as the Gulf war widens."),
    ("KIM CALLS FOR WIDER USE OF TACTICAL NUCLEAR WEAPONS",
     "North Korea's leader urged wider deployment of tactical nuclear arms "
     "during a visit to a nuclear material plant, state media said."),
    ("GUNMEN KILL AT LEAST 30 IN NIGERIA'S NIGER STATE",
     "Gunmen killed at least 30 people in a new attack in Niger state, the UN "
     "warning of escalating violence across the region."),
    ("XI'S GRAFT PROBE SHAKES CHINA'S NEXT LEADERSHIP RACE",
     "A corruption probe into Shanghai party chief Chen Jining, once tipped "
     "for the top leadership body, upends succession assumptions."),
    ("RUSSIA'S OWN FIGURES PUT WAR DEAD NEAR 500,000",
     "Moscow's own data show nearly 500,000 Russians lost in the Ukraine war, "
     "a toll now topping combined US war deaths since WWI."),
    ("ISRAEL KILLS HAMAS SECURITY CHIEF IN GAZA STRIKE",
     "Mohammad Abuelouf, who headed Hamas's interior security service, was "
     "killed with his wife and two children, medics said."),
    ("US PLANS NEW TARIFFS ON 14 TRADING PARTNERS",
     "Washington proposed tariffs on 14 partners to fight excess factory "
     "capacity, with the highest rates aimed at China."),
]

NUMBERS = [
    "30 KILLED IN NIGER STATE ATTACK",
    "500,000 RUSSIAN WAR DEAD, OWN DATA",
    "36% GARMENT WAGE RISE, BANGLADESH",
    "13,000 HA BURNED, FLINDERS ISLAND",
    "50 MPH GUSTS IN THANKSGIVING STORM",
]

BRIEFS = [
    "Houthis say they hit Saudi Ras Tanura refinery; fires reported.",
    "Two tankers hit naval mines in the Strait of Hormuz, IRGC says.",
    "Ukraine struck Russian oil refineries overnight; Putin vows reply.",
    "Colombia police free 20 hostages after 17-hour supermarket siege.",
    "Solomon Islands and Australia sign historic security treaty.",
    "India marks 18 years since the 26/11 Mumbai attacks; Constitution Day.",
    "Bangladesh garment workers win a 36% wage rise.",
    "Israel minister: Iran is developing chemical weapons.",
    "Six missing after small plane crashes into the Gulf of Mexico.",
    "US shelves plan to use Russia business deals to end Ukraine war.",
    "Fort Hood survivors lose appeal to witness Hasan's execution.",
    "Unclassified CIA system breached in cyberattack, CNN reports.",
    "Trump pardons Thanksgiving turkeys Freedom and Feathers.",
    "US deported 1,700 Indian nationals in 2026, Delhi says.",
    "India answers US tariff plan of up to 25% on its goods.",
    "RAF moves jets into hangars at night over drone threat.",
    "Eisenkot bloc aims to form a new Israeli government next week.",
    "Russian strikes cut power and gas in five Ukrainian regions.",
    "US Army blows up 4,500 kg of ageing lead azide in Iowa.",
    "Flinders Island bushfire burns 13,000 hectares; residents flee.",
    "Real Madrid hit PSV 5-1; Bellingham stunner; Arsenal, City held.",
    "Gukesh: 'always under control' at World Chess Championship.",
    "Sooryavanshi, 15, hits fastest List A double century ever.",
    "Wall Street mixed: Dow +0.33%, Nasdaq -0.62%; Nvidia -3.9%.",
    "DeepSeek founder now richest AI model creator at $55 billion.",
    "Huang-linked firms listed $270m of AI servers in China: report.",
    "Close-up images due of asteroid hit to test Earth's defences.",
    "US attorney general dodges questions on Nvidia investigation.",
    "CDC reports nine measles-related deaths in the US in 2026.",
    "Thanksgiving travel busiest in 16 years; 417,000 flights forecast.",
]


def build():
    cv = Canvas(W, H, WHITE)
    mx = 28
    # Header
    cv.text(mx, 26, "THE WORLD TODAY", 5, NAVY)
    cv.text(mx, 74, "THURSDAY 26 NOVEMBER 2026  -  38 STORIES FROM AROUND THE WORLD", 2, GREY)
    cv.rect(mx, 104, W - 2 * mx, 4, NAVY)

    # Lead story
    ly = 120
    cv.rect(mx, ly, W - 2 * mx, 3, RED)
    cv.text(mx, ly + 12, "TOP STORY", 2, RED)
    draw_para(cv, mx, ly + 34, LEAD_HEAD, 3, BLACK, 54, 26, 2)
    draw_para(cv, mx, ly + 92, LEAD_BODY, 2, BLACK, 80, 20, 3)
    cv.rect(mx, ly + 158, W - 2 * mx, 2, LIGHT)

    # Mains grid: 2 cols x 4 rows; 7 stories + numbers box
    gy = 296
    cell_w = (W - 2 * mx - 16) // 2
    cell_h = 80
    for idx in range(8):
        col = idx % 2
        row = idx // 2
        x = mx + col * (cell_w + 16)
        y = gy + row * cell_h
        if idx < 7:
            head, body = MAINS[idx]
            cv.text(x, y, "%d." % (idx + 2), 2, RED)
            draw_para(cv, x + 30, y, head, 2, BLACK, 37, 15, 2)
            draw_para(cv, x, y + 32, body, 1, BLACK, 78, 10, 3)
        else:
            cv.rect(x, y, cell_w, 68, LIGHT)
            cv.text(x + 10, y + 6, "BY THE NUMBERS", 1, NAVY)
            for j, ln in enumerate(NUMBERS):
                cv.text(x + 10, y + 20 + j * 9, ln, 1, BLACK)
        if col == 0:
            cv.rect(x + cell_w + 4, y, 2, 68, LIGHT)

    # Briefs header band
    by = 632
    cv.rect(mx, by, W - 2 * mx, 30, NAVY)
    cv.text(mx + 12, by + 8, "IN BRIEF  -  30 MORE STORIES", 2, WHITE)

    # Briefs: 2 columns x 15 rows
    bx = mx
    bcol_w = (W - 2 * mx - 16) // 2
    for i, b in enumerate(BRIEFS):
        col = i // 15
        row = i % 15
        x = bx + col * (bcol_w + 16)
        y = 674 + row * 19
        cv.text(x, y, "%02d." % (i + 1), 1, RED)
        cv.text(x + 24, y, b.upper(), 1, BLACK)

    # Footer
    fy = 978
    cv.rect(mx, fy, W - 2 * mx, 2, NAVY)
    cv.text(mx, fy + 10, "SOURCES: REUTERS, JUST SECURITY, WIRE REPORTS, 26 NOV 2026.", 1, GREY)
    cv.text(mx, fy + 24, "DRAWN BY A PROGRAM. NO NETWORK AT RENDER TIME.", 1, GREY)
    return cv


def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        c += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    out = b"\x89PNG\r\n\x1a\n"
    out += chunk(b"IHDR", ihdr)
    out += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    out += chunk(b"IEND", b"")
    return out


def main():
    cv = build()
    data = png_bytes(cv)
    out_path = "/output/entry.png"
    os.makedirs("/output", exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(data)
    print("wrote %s %d bytes" % (out_path, len(data)))


if __name__ == "__main__":
    main()
