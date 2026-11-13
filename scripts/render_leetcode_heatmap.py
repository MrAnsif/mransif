#!/usr/bin/env python3
"""
Render the 1-year LeetCode submission heatmap as an animated SVG into cards/leetcode-heatmap.svg.

Exact match to the GitHub contribution heatmap design ("Three Worlds":
paper #f3f3f1, ink #111111, electric blue #2f55ff; Instrument Serif & Geist Mono).
All fonts embedded as base64 data URIs. No external dependencies. No emojis.

Run by .github/workflows/update-profile-art.yml after fetch_leetcode.py.
"""
import base64
import datetime
import json
import os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DATA = os.path.join(ROOT, "data", "leetcode.json")
OUT = os.path.join(ROOT, "cards")
FONTS = os.path.join(ROOT, "fonts")

# Brand tokens matching cards/heatmap.svg
PAPER = "#f3f3f1"
PAPER_DEEP = "#e2e2de"
INK = "#111111"
MUTED = "#6e6e73"
TECH = "#2f55ff"
W = 880

BLUE = [PAPER_DEEP, "#c8d3ff", "#94a8ff", "#6280ff", TECH, "#1a3be0"]

SERIF = "'Instrument Serif', Georgia, serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace"

FONT_FILES = {
    "serif": ("Instrument Serif", "normal", 400, "serif-400.woff"),
    "serif-i": ("Instrument Serif", "italic", 400, "serif-italic.woff"),
    "mono": ("Geist Mono", "normal", 400, "geistmono-400.woff"),
}

BASE_CSS = """
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes pop{0%{opacity:0;transform:scale(.3)}70%{opacity:1;transform:scale(1.15)}100%{opacity:1;transform:none}}
.r{opacity:0;animation:rise .8s cubic-bezier(.2,.7,.2,1) both;transform-box:fill-box}
.f{opacity:0;animation:fade .9s ease-out both}
.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .4s ease-out both}
@media (prefers-reduced-motion: reduce){.r,.f,.p{animation:none!important;opacity:1!important;transform:none!important}}
"""


def font_face(keys):
    out = []
    for k in keys:
        fam, style, weight, fn = FONT_FILES[k]
        path = os.path.join(FONTS, fn)
        if os.path.exists(path):
            b64 = base64.b64encode(open(path, "rb").read()).decode()
            out.append(
                f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};"
                f"src:url(data:font/woff;base64,{b64}) format('woff')}}"
            )
    return "".join(out)


def d(s):
    return f'style="animation-delay:{s:.2f}s"'


def render_heatmap():
    if not os.path.exists(DATA):
        print(f"error: {DATA} not found. Run fetch_leetcode.py first.", file=os.sys.stderr)
        return

    with open(DATA, "r", encoding="utf-8") as f:
        data = json.load(f)

    days = data["days"]
    first = datetime.date.fromisoformat(days[0]["date"])
    lead = (first.weekday() + 1) % 7
    cell, step, gx, gy = 12, 15, 44, 96
    cells, months, seen = [], [], set()

    for i, day in enumerate(days):
        k = i + lead
        col, row = divmod(k, 7)
        date = datetime.date.fromisoformat(day["date"])
        if date.day <= 7 and (date.year, date.month) not in seen and row == 0:
            seen.add((date.year, date.month))
            months.append((col, date.strftime("%b")))

        c = day["count"]
        lvl = day.get("level", 0)
        delay = 1.0 + col * 0.03 + row * 0.02
        cells.append(
            f'<rect class="p" style="animation-delay:{delay:.2f}s" x="{gx + col * step}" y="{gy + row * step}" '
            f'width="{cell}" height="{cell}" rx="3" fill="{BLUE[lvl]}">'
            f'<title>{day["date"]}: {c} submission{"s" if c != 1 else ""}</title></rect>'
        )

    ncols = (len(days) + lead + 6) // 7
    right = gx + ncols * step - 3

    labels = "".join(
        f'<text x="{gx + col * step}" y="{gy + 7 * step + 16}" font-family="{MONO}" font-size="11" fill="{MUTED}">{m}</text>'
        for col, m in months if col < ncols - 12
    )

    legend_x = right - len(BLUE) * 14
    legend = "".join(
        f'<rect x="{legend_x + i * 14}" y="{gy + 7 * step + 6}" width="11" height="11" rx="2.5" fill="{c}"/>'
        for i, c in enumerate(BLUE)
    )

    streak = data.get("streak", 0)
    total_subs = data.get("total_submissions_1yr", 0)
    h = gy + 7 * step + 44

    css = font_face(["serif", "serif-i", "mono"]) + BASE_CSS
    label_text = f"LeetCode submission graph: {total_subs:,} submissions in the last year, {streak}-day streak"

    body = f"""
<rect width="{W}" height="{h}" rx="14" fill="{PAPER}"/>
<text class="r" {d(0.8)} x="42" y="62" font-family="{SERIF}" font-size="34" fill="{INK}">LeetCode, <tspan font-style="italic" fill="{TECH}">in blue</tspan></text>
<text class="f" {d(0.8)} x="{right}" y="60" text-anchor="end" font-family="{MONO}" font-size="12" letter-spacing="1"><tspan fill="{TECH}" font-weight="600">{streak}-DAY STREAK</tspan><tspan fill="{MUTED}">  ·  REFRESHED DAILY</tspan></text>
{''.join(cells)}
<g class="f" {d(2.4)}>{labels}
<text x="{legend_x - 8}" y="{gy + 7 * step + 16}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">less</text>
{legend}
<text x="{legend_x + len(BLUE) * 14 + 2}" y="{gy + 7 * step + 16}" font-family="{MONO}" font-size="11" fill="{MUTED}">more</text></g>
"""

    svg_content = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.3f}" height="{h + 12}" viewBox="0 0 {W:.3f} {h + 12}" '
        f'role="img" aria-label="{escape(label_text)}"><title>{escape(label_text)}</title>'
        f"<style>{css}</style>{body}</svg>"
    )

    os.makedirs(OUT, exist_ok=True)
    out_file = os.path.join(OUT, "leetcode-heatmap.svg")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"wrote cards/leetcode-heatmap.svg ({len(svg_content) // 1024} KB)")


if __name__ == "__main__":
    render_heatmap()

