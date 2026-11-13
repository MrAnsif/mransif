#!/usr/bin/env python3
"""
Fetch LeetCode daily submission activity for the last 1 year (53 weeks / 371 days)
via LeetCode's public GraphQL endpoint and write data/leetcode.json.

No authentication or session required.
Run daily by .github/workflows/update-profile-art.yml.
"""
import datetime
import json
import math
import os
import sys
import urllib.request

USERNAME = os.environ.get("LEETCODE_USER", "ansif01")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "leetcode.json")
GRAPHQL_URL = "https://leetcode.com/graphql"

CALENDAR_QUERY = """query calendar($username: String!, $year: Int) {
  user: matchedUser(username: $username) {
    calendar: userCalendar(year: $year) {
      calendar: submissionCalendar
      streak
      totalActiveDays
    }
    submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
        submissions
      }
    }
  }
}"""


def calc_level(count, max_cnt=8):
    """
    Sine-curve opacity calculation matching JacobLinCool's LeetCode-Stats-Card:
    opacity = sin(min(1.0, (count + 0.5) / max_cnt) * pi / 2)
    Maps smoothly from 1 to 5 for non-zero counts.
    """
    if count <= 0:
        return 0
    opacity = math.sin(min(1.0, (count + 0.5) / float(max_cnt)) * math.pi * 0.5)
    if opacity < 0.45:
        return 1
    elif opacity < 0.65:
        return 2
    elif opacity < 0.82:
        return 3
    elif opacity < 0.95:
        return 4
    else:
        return 5


def fetch_leetcode_data():
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    now = datetime.date.today()
    years = [now.year - 1, now.year]

    raw_calendar = {}
    streak = 0
    total_active_days = 0
    ac_stats = {}

    for yr in years:
        payload = json.dumps({"query": CALENDAR_QUERY, "variables": {"username": USERNAME, "year": yr}}).encode("utf-8")
        req = urllib.request.Request(GRAPHQL_URL, data=payload, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            user = data.get("data", {}).get("user")
            if user:
                cal_info = user.get("calendar") or {}
                raw_json = cal_info.get("calendar")
                if raw_json:
                    raw_calendar.update(json.loads(raw_json))
                if cal_info.get("streak") is not None:
                    streak = max(streak, int(cal_info.get("streak", 0)))
                if cal_info.get("totalActiveDays") is not None:
                    total_active_days = max(total_active_days, int(cal_info.get("totalActiveDays", 0)))

                stats_list = user.get("submitStatsGlobal", {}).get("acSubmissionNum", [])
                for s in stats_list:
                    ac_stats[s.get("difficulty")] = {
                        "count": s.get("count", 0),
                        "submissions": s.get("submissions", 0),
                    }
        except Exception as e:
            print(f"warning: failed to fetch LeetCode data for year {yr}: {e}", file=sys.stderr)

    # Convert timestamps to YYYY-MM-DD
    by_date = {}
    for ts_str, cnt in raw_calendar.items():
        dt = datetime.datetime.fromtimestamp(int(ts_str), datetime.timezone.utc).date()
        by_date[dt.isoformat()] = cnt

    # Build trailing 53 weeks (371 days) ending at current week's Saturday
    # Matches GitHub contribution calendar grid alignment
    lead_offset = (now.weekday() + 1) % 7  # 0 for Sunday
    end_date = now + datetime.timedelta(days=(6 - lead_offset))  # Saturday of current week
    total_days = 53 * 7  # 371 days
    start_date = end_date - datetime.timedelta(days=total_days - 1)

    days = []
    curr = start_date
    while curr <= end_date:
        d_str = curr.isoformat()
        cnt = by_date.get(d_str, 0) if curr <= now else 0
        days.append({
            "date": d_str,
            "count": cnt,
            "level": calc_level(cnt),
        })
        curr += datetime.timedelta(days=1)

    total_submissions = sum(d["count"] for d in days)
    active_days_1yr = sum(1 for d in days if d["count"] > 0)
    best_day = max(days, key=lambda d: d["count"]) if days else {"date": "", "count": 0}

    return {
        "username": USERNAME,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "streak": streak,
        "total_active_days_profile": total_active_days,
        "active_days_1yr": active_days_1yr,
        "total_submissions_1yr": total_submissions,
        "best_day_1yr": {"date": best_day["date"], "count": best_day["count"]},
        "problems_solved": ac_stats,
        "days": days,
    }


if __name__ == "__main__":
    data = fetch_leetcode_data()
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    solved_all = data.get("problems_solved", {}).get("All", {}).get("count", 0)
    print(f"wrote {OUT_PATH}: {data['total_submissions_1yr']} submissions in 1 year, "
          f"streak {data['streak']} days, {solved_all} problems solved")

