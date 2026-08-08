"""Fetch Google Scholar profile metrics and write them to scholar-stats.json.

Run weekly by .github/workflows/update-scholar-stats.yml.
If every fetch strategy fails (Scholar rate-limiting etc.), exits 0 without
touching the JSON so the previous numbers stay in place until the next run.
"""

import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCHOLAR_ID = "43h5Xs8AAAAJ"
SCHOLAR_URL = f"https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en"
OUT_PATH = Path(__file__).resolve().parent.parent / "scholar-stats.json"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

FETCH_URLS = [
    SCHOLAR_URL,
    "https://api.allorigins.win/raw?url=" + urllib.parse.quote(SCHOLAR_URL, safe=""),
    "https://corsproxy.io/?" + urllib.parse.quote(SCHOLAR_URL, safe=""),
]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_stats(html: str):
    # The stats table renders six cells in order:
    # citations(all), citations(since), h-index(all), h-index(since),
    # i10-index(all), i10-index(since)
    cells = re.findall(r'<td class="gsc_rsb_std">([\d,]+)</td>', html)
    if len(cells) < 6:
        return None
    values = [int(c.replace(",", "")) for c in cells[:6]]
    return {
        "citations": values[0],
        "citations_since_2021": values[1],
        "h_index": values[2],
        "h_index_since_2021": values[3],
        "i10_index": values[4],
        "i10_index_since_2021": values[5],
    }


def main() -> int:
    for url in FETCH_URLS:
        try:
            stats = parse_stats(fetch(url))
        except Exception as e:
            print(f"fetch failed for {url}: {e}", file=sys.stderr)
            continue
        if not stats:
            print(f"could not parse stats from {url}", file=sys.stderr)
            continue
        kst_today = (datetime.now(timezone.utc) + timedelta(hours=9)).strftime("%Y-%m-%d")
        stats["updated"] = kst_today
        OUT_PATH.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
        print(f"updated {OUT_PATH.name}: {stats}")
        return 0
    print("all fetch strategies failed; keeping previous stats", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
