#!/usr/bin/env python3
"""
Scrape real daily contribution counts from GitHub's public, unauthenticated
contributions endpoint for the last 2 years (730 days) and write data/contributions.json
with derived stats (current streak, longest streak, best day, monthly totals).

No token, no auth, no GraphQL — just the public HTML GitHub already serves.
Run daily by .github/workflows/update-profile-art.yml.
"""
import datetime
import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_PROFILE_USER", "mransif")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def parse_contribution_cells(html):
    soup = BeautifulSoup(html, "html.parser")
    cells = soup.select("td.ContributionCalendar-day")
    days = {}
    for td in cells:
        date = td.get("data-date")
        if not date:
            continue
        td_id = td.get("id")
        tooltip_el = soup.find("tool-tip", attrs={"for": td_id}) if td_id else None
        text = tooltip_el.get_text(strip=True) if tooltip_el else ""
        if re.search(r"no contributions", text, re.I):
            count = 0
        else:
            m = re.match(r"(\d+)", text)
            count = int(m.group(1)) if m else 0
        days[date] = {"date": date, "count": count, "level": int(td.get("data-level") or 0)}
    return days


def fetch_days():
    headers = {"User-Agent": "profile-readme-bot/1.0"}
    all_days = {}
    now = datetime.date.today()

    # 1. Trailing year up to today
    resp = requests.get(URL, headers=headers, timeout=30)
    if resp.ok:
        all_days.update(parse_contribution_cells(resp.text))

    # 2. Previous 2 calendar years
    for yr in [now.year - 1, now.year - 2]:
        url = f"https://github.com/users/{USERNAME}/contributions?from={yr}-12-01&to={yr}-12-31"
        try:
            r = requests.get(url, headers=headers, timeout=30)
            if r.ok:
                all_days.update(parse_contribution_cells(r.text))
        except Exception as e:
            print(f"warning: failed to fetch year {yr}: {e}", file=sys.stderr)

    if not all_days:
        print("no calendar cells found -- github markup may have changed", file=sys.stderr)
        sys.exit(1)

    cutoff = (now - datetime.timedelta(days=730)).isoformat()
    today_str = now.isoformat()
    days = [all_days[d] for d in sorted(all_days.keys()) if d >= cutoff and d <= today_str]
    return days


def compute_current_streak(days):
    idx = len(days) - 1
    if days[idx]["count"] == 0:
        idx -= 1  # today isn't over yet
    streak = 0
    end_idx = idx
    while idx >= 0 and days[idx]["count"] > 0:
        streak += 1
        idx -= 1
    start_idx = idx + 1
    if streak == 0:
        return 0, None, None
    return streak, days[start_idx]["date"], days[end_idx]["date"]


def compute_longest_streak(days):
    longest = run = 0
    longest_start = longest_end = None
    run_start_idx = None
    for i, d in enumerate(days):
        if d["count"] > 0:
            if run == 0:
                run_start_idx = i
            run += 1
            if run > longest:
                longest = run
                longest_start = days[run_start_idx]["date"]
                longest_end = days[i]["date"]
        else:
            run = 0
    return longest, longest_start, longest_end


def build_data(days):
    total = sum(d["count"] for d in days)
    active_days = sum(1 for d in days if d["count"] > 0)
    best = max(days, key=lambda d: d["count"])
    cur_len, cur_start, cur_end = compute_current_streak(days)
    long_len, long_start, long_end = compute_longest_streak(days)

    monthly = {}
    for d in days:
        key = d["date"][:7]
        monthly[key] = monthly.get(key, 0) + d["count"]
    monthly_list = [{"month": k, "total": v} for k, v in sorted(monthly.items())]

    return {
        "username": USERNAME,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": total,
        "active_days": active_days,
        "avg_per_active_day": round(total / active_days, 1) if active_days else 0,
        "current_streak": {"length": cur_len, "start": cur_start, "end": cur_end},
        "longest_streak": {"length": long_len, "start": long_start, "end": long_end},
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": monthly_list,
        "days": days,
    }


if __name__ == "__main__":
    days = fetch_days()
    data = build_data(days)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print(f"wrote {OUT_PATH}: {data['total_contributions']} contributions across {len(days)} days ({data['range']['start']} to {data['range']['end']}), "
          f"current streak {data['current_streak']['length']}, "
          f"longest streak {data['longest_streak']['length']}")
