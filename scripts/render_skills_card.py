#!/usr/bin/env python3
"""
Render the redesigned Skills & Tools card matching the attached design:
- Deep dark canvas (#0b0c10)
- 'Skills' title in Instrument Serif with blue italic 's'
- 6 rounded white cards (#f8f9fa, rx=14)
- 27 official vector icons embedded as base64 data URIs
- Pure SVG, zero external network dependencies on GitHub

Run standalone or by update-profile-art.yml workflow.
"""
import base64
import json
import os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
FONTS = os.path.join(ROOT, "fonts")
ICONS_JSON = os.path.join(ROOT, "data", "icons", "icons_b64.json")
OUT = os.path.join(ROOT, "cards")

W = 880
H = 588
GAP_X = 16
GAP_Y = 14
CARD_W = 432
CARD_H = 138
X0 = 0
Y0 = 122

TECH = "#2f55ff"
BG_DARK = "#0b0c10"
LINE_DARK = "#21262d"
MUTED_DARK = "#8b949e"

SERIF = "'Instrument Serif', Georgia, serif"
SANS = "Geist, system-ui, -apple-system, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace"

FONT_FILES = {
    "serif": ("Instrument Serif", "normal", 400, "serif-400.woff"),
    "serif-i": ("Instrument Serif", "italic", 400, "serif-italic.woff"),
    "sans": ("Geist", "normal", 400, "geist-400.woff"),
    "sans-b": ("Geist", "normal", 600, "geist-600.woff"),
    "mono": ("Geist Mono", "normal", 400, "geistmono-400.woff"),
}

BASE_CSS = """
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes pop{0%{opacity:0;transform:scale(.3)}70%{opacity:1;transform:scale(1.15)}100%{opacity:1;transform:none}}
.r{opacity:0;animation:rise .8s cubic-bezier(.2,.7,.2,1) both;transform-box:fill-box}
.f{opacity:0;animation:fade .9s ease-out both}
.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .4s ease-out both}
@media (prefers-reduced-motion: reduce){.r,.f,.p{animation:none!important;opacity:1!important}}
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


CARDS_CONFIG = [
    {
        "title": "Databases & Data",
        "dot": "#2f55ff",
        "col": 0, "row": 0,
        "sub": "Working with reliable and scalable data solutions.",
        "items": [
            ("sql", "SQL"),
            ("postgresql", "PostgreSQL"),
            ("mongodb", "MongoDB"),
            ("prisma", "Prisma ORM"),
        ]
    },
    {
        "title": "Programming Languages",
        "dot": "#ef3b2d",
        "col": 1, "row": 0,
        "sub": "Building solutions with modern and versatile languages.",
        "items": [
            ("python", "Python"),
            ("javascript", "JavaScript (ES6+)"),
            ("typescript", "TypeScript"),
            ("c", "C"),
            ("java", "Java"),
        ]
    },
    {
        "title": "Frameworks & Backend",
        "dot": "#ffc81a",
        "col": 0, "row": 1,
        "sub": "Creating fast, scalable and interactive web applications.",
        "items": [
            ("nodejs", "Node.js"),
            ("express", "Express.js"),
            ("flask", "Flask"),
            ("react", "React.js"),
            ("nextjs", "Next.js"),
            ("html5", "HTML5"),
            ("css3", "CSS3"),
            ("tailwindcss", "Tailwind CSS"),
        ]
    },
    {
        "title": "Testing",
        "dot": "#10b981",
        "col": 1, "row": 1,
        "sub": "Ensuring quality with modern testing tools.",
        "items": [
            ("jest", "Jest"),
            ("cypress", "Cypress"),
            ("playwright", "Playwright"),
        ]
    },
    {
        "title": "Version Control & Tools",
        "dot": "#8b5cf6",
        "col": 0, "row": 2,
        "sub": "Collaborating and building efficiently with the right tools.",
        "items": [
            ("git", "Git"),
            ("github", "GitHub"),
            ("azuredevops", "Azure DevOps"),
        ]
    },
    {
        "title": "AI-assisted Development Tools",
        "dot": "#06b6d4",
        "col": 1, "row": 2,
        "sub": "Supercharging development with AI tools.",
        "items": [
            ("claude", "Claude Code"),
            ("opencode", "OpenCode"),
            ("antigravity", "Antigravity"),
            ("ollama", "Ollama"),
        ]
    }
]


def render_card(card_data, icons_b64, base_x, base_y, delay):
    title = card_data["title"]
    dot = card_data["dot"]
    sub = card_data["sub"]
    items = card_data["items"]

    items_svg = []
    n = len(items)
    inner_w = CARD_W - 32  # 360px
    step = inner_w / float(n)
    is_dense = (n >= 8)
    icon_size = 24 if is_dense else 28
    font_size = 8.5 if is_dense else 10

    for i, (icon_key, label) in enumerate(items):
        cx = 16 + (i + 0.5) * step
        ix = cx - icon_size / 2.0
        iy = 64 if is_dense else 62

        b64 = icons_b64.get(icon_key, "")
        if b64:
            img_tag = f'<image x="{ix:.1f}" y="{iy:.1f}" width="{icon_size}" height="{icon_size}" href="data:image/svg+xml;base64,{b64}"/>'
        else:
            img_tag = f'<rect x="{ix:.1f}" y="{iy:.1f}" width="{icon_size}" height="{icon_size}" rx="4" fill="#d1d5db"/>'

        text_y = iy + icon_size + 14
        items_svg.append(
            f'<g class="p" {d(delay + 0.2 + i * 0.04)}>'
            f'{img_tag}'
            f'<text x="{cx:.1f}" y="{text_y:.1f}" text-anchor="middle" font-family="{SANS}" font-size="{font_size}" font-weight="500" fill="#222222">{escape(label)}</text>'
            f'</g>'
        )

    return f"""
<g transform="translate({base_x} {base_y})">
  <g class="f" {d(delay)}>
    <rect width="{CARD_W}" height="{CARD_H}" rx="14" fill="#f8f9fa" stroke="#e5e7eb" stroke-width="1"/>
    <circle cx="22" cy="24" r="4.5" fill="{dot}"/>
    <text x="34" y="29" font-family="{SERIF}" font-style="italic" font-size="18" font-weight="600" fill="#111111">{escape(title)}</text>
    <text x="{CARD_W - 20}" y="28" text-anchor="end" font-family="{MONO}" font-size="14" fill="#9ca3af">&#8599;</text>
    <text x="22" y="47" font-family="{SANS}" font-size="11" fill="#6b7280">{escape(sub)}</text>
    {''.join(items_svg)}
  </g>
</g>
"""


def render_skills():
    icons_b64 = {}
    if os.path.exists(ICONS_JSON):
        with open(ICONS_JSON, "r", encoding="utf-8") as f:
            icons_b64 = json.load(f)

    cards_svg = []
    for c in CARDS_CONFIG:
        col = c["col"]
        row = c["row"]
        bx = X0 + col * (CARD_W + GAP_X)
        by = Y0 + row * (CARD_H + GAP_Y)
        delay = 0.9 + (row * 2 + col) * 0.1
        cards_svg.append(render_card(c, icons_b64, bx, by, delay))

    css = font_face(["serif", "serif-i", "sans", "sans-b", "mono"]) + BASE_CSS
    label_desc = "Skills: Databases & Data, Programming Languages, Frameworks & Backend, Testing, Version Control & Tools, and AI-assisted Tools"

    body = f"""
<!-- <rect width="{W}" height="{H}" rx="16" fill="{BG_DARK}"/> -->

<!-- Header -->
<!-- <g class="f" {d(0.2)}>
  <text x="0" y="36" font-family="{MONO}" font-size="11" font-weight="600" letter-spacing="1.5" fill="{MUTED_DARK}">MY SKILLS</text>
  <line x1="76" y1="32" x2="{W}" y2="32" stroke="{LINE_DARK}" stroke-width="1"/>
</g> -->

<g class="r" {d(0.4)}>
  <text x="0" y="92" font-family="{SERIF}" font-size="56" fill="#ffffff" letter-spacing="-1">My <tspan font-style="italic" fill="{TECH}">Skills</tspan></text>
</g>

<g class="f" {d(0.5)}>
  <text x="{W}" y="76" text-anchor="end" font-family="{SANS}" font-size="12.5" fill="{MUTED_DARK}">Technologies I work with</text>
  <text x="{W}" y="94" text-anchor="end" font-family="{SANS}" font-size="12.5" fill="{MUTED_DARK}">and enjoy using.</text>
</g>

<!-- 6 Cards Grid -->
{''.join(cards_svg)}
"""

    svg_content = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="{escape(label_desc)}"><title>{escape(label_desc)}</title>'
        f"<style>{css}</style>{body}</svg>"
    )

    os.makedirs(OUT, exist_ok=True)
    out_file = os.path.join(OUT, "skills.svg")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"wrote cards/skills.svg ({len(svg_content) // 1024} KB)")


if __name__ == "__main__":
    render_skills()

