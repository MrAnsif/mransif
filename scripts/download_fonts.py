#!/usr/bin/env python3
"""Download font WOFF files needed by render_readme_cards.py.
Sources:
  - Instrument Serif: Avi's repo (SIL OFL) or Google Fonts fallback
  - Geist / Geist Mono: Vercel GitHub release (MIT)
"""
import os, sys, urllib.request, zipfile, io, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "fonts")
os.makedirs(FONTS, exist_ok=True)

HEADERS = {"User-Agent": "profile-readme-font-downloader/1.0"}

def fetch(url, dest):
    if os.path.exists(dest):
        print(f"  already exists: {os.path.basename(dest)}")
        return True
    print(f"  downloading {os.path.basename(dest)} from {url[:60]}...")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        with open(dest, "wb") as f:
            f.write(data)
        print(f"  OK ({len(data)//1024} KB)")
        return True
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

# --- Instrument Serif from Avi's public repo ---
AVI = "https://raw.githubusercontent.com/AviVashishta29/AviVashishta29/main/fonts"
print("Downloading Instrument Serif...")
fetch(f"{AVI}/serif-400.woff",    os.path.join(FONTS, "serif-400.woff"))
fetch(f"{AVI}/serif-italic.woff", os.path.join(FONTS, "serif-italic.woff"))

# --- Geist from Avi's public repo ---
print("Downloading Geist...")
fetch(f"{AVI}/geist-400.woff",    os.path.join(FONTS, "geist-400.woff"))
fetch(f"{AVI}/geist-600.woff",    os.path.join(FONTS, "geist-600.woff"))
fetch(f"{AVI}/geistmono-400.woff",os.path.join(FONTS, "geistmono-400.woff"))

# Verify all present
needed = ["serif-400.woff","serif-italic.woff","geist-400.woff","geist-600.woff","geistmono-400.woff"]
missing = [n for n in needed if not os.path.exists(os.path.join(FONTS, n))]
if missing:
    print(f"\nMISSING: {missing}")
    sys.exit(1)
else:
    sizes = {n: os.path.getsize(os.path.join(FONTS, n))//1024 for n in needed}
    print(f"\nAll fonts OK: {sizes}")

