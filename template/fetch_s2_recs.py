"""
基于种子论文的 S2 ML 推荐
读取 interest_profile.json 中的 active_seed_papers，
调用 S2 Recommendations API，输出候选论文 JSON。

用法：
  python fetch_s2_recs.py > /tmp/candidates_s2recs.json
"""

import urllib.request
import urllib.error
import json
import os
import sys
import time

_dir = os.path.dirname(__file__)

with open(os.path.join(_dir, "config.json"), encoding="utf-8") as f:
    _cfg = json.load(f)

HEADERS = {
    "User-Agent": "ArticleFeed/1.0",
    "x-api-key": _cfg.get("s2_api_key", ""),
    "Content-Type": "application/json",
}

S2_RECS_URL = "https://api.semanticscholar.org/recommendations/v1/papers/"
PAPER_FIELDS = "paperId,title,year,citationCount,authors,externalIds,openAccessPdf,publicationVenue,journal"


def load_seeds():
    profile_path = os.path.join(_dir, "interest_profile.json")
    if not os.path.exists(profile_path):
        print("[fetch_s2_recs] interest_profile.json 不存在，跳过", file=sys.stderr)
        return []
    with open(profile_path, encoding="utf-8") as f:
        profile = json.load(f)
    seeds = profile.get("active_seed_papers", [])
    return [s["s2_id"] for s in seeds if s.get("s2_id")]


def fetch_recommendations(positive_ids, limit=20):
    params = f"?fields={PAPER_FIELDS}&limit={limit}"
    url = S2_RECS_URL + params
    body = json.dumps({"positivePaperIds": positive_ids}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=HEADERS, method="POST")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read())
                return data.get("recommendedPapers", [])
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(5 * (attempt + 1))
            else:
                print(f"[fetch_s2_recs] HTTP {e.code}: {e.reason}", file=sys.stderr)
                return []
        except Exception as e:
            print(f"[fetch_s2_recs] 请求失败: {e}", file=sys.stderr)
            return []
    return []


def normalize(p):
    venue = p.get("publicationVenue") or p.get("journal") or {}
    journal = venue.get("name", "") if isinstance(venue, dict) else ""
    doi = (p.get("externalIds") or {}).get("DOI", "")
    oa_url = (p.get("openAccessPdf") or {}).get("url", "")
    authors = [a.get("name", "") for a in p.get("authors", [])]
    return {
        "s2_id": p.get("paperId", ""),
        "title": p.get("title", ""),
        "authors": authors,
        "year": p.get("year"),
        "venue": journal,
        "citation_count": p.get("citationCount") or 0,
        "doi": doi,
        "open_access_url": oa_url,
        "source": "s2_recommendations",
        "tier": None,
    }


def main():
    seeds = load_seeds()
    if not seeds:
        print("[]")
        return

    print(f"[fetch_s2_recs] 使用 {len(seeds)} 篇种子论文查询推荐...", file=sys.stderr)
    papers = fetch_recommendations(seeds)
    results = [normalize(p) for p in papers if p.get("paperId")]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"[fetch_s2_recs] 获得 {len(results)} 篇候选", file=sys.stderr)


if __name__ == "__main__":
    main()
