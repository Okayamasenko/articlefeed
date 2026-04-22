"""
基于种子论文参考文献的引用交集分析
对 interest_profile.json 中的 active_seed_papers，
抓取每篇的 references（向后引用），
保留被 2 篇以上种子论文共同引用的论文（领域共识文献）。

用法：
  python fetch_citations.py > /tmp/candidates_citations.json
"""

import urllib.request
import urllib.error
import json
import os
import sys
import time
from collections import defaultdict

_dir = os.path.dirname(__file__)

with open(os.path.join(_dir, "config.json"), encoding="utf-8") as f:
    _cfg = json.load(f)

HEADERS = {
    "User-Agent": "ArticleFeed/1.0",
    "x-api-key": _cfg.get("s2_api_key", ""),
}

S2_BASE = "https://api.semanticscholar.org/graph/v1"
REF_FIELDS = "paperId,title,year,citationCount,authors,externalIds,openAccessPdf,publicationVenue,journal"


def load_seeds():
    profile_path = os.path.join(_dir, "interest_profile.json")
    if not os.path.exists(profile_path):
        print("[fetch_citations] interest_profile.json 不存在，跳过", file=sys.stderr)
        return []
    with open(profile_path, encoding="utf-8") as f:
        profile = json.load(f)
    return profile.get("active_seed_papers", [])


def fetch_references(s2_id):
    url = f"{S2_BASE}/paper/{s2_id}/references?fields={REF_FIELDS}&limit=100"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            # references 返回格式：[{"citedPaper": {...}}, ...]
            return [item["citedPaper"] for item in data.get("data", [])
                    if item.get("citedPaper", {}).get("paperId")]
    except urllib.error.HTTPError as e:
        print(f"[fetch_citations] HTTP {e.code} for {s2_id}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"[fetch_citations] 请求失败 {s2_id}: {e}", file=sys.stderr)
        return []


def normalize(p, score):
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
        "source": "citation_intersection",
        "tier": None,
        "intersection_score": score,
    }


def main():
    seeds = load_seeds()
    if not seeds:
        print("[]")
        return

    # 收集每篇种子的参考文献，统计交集
    paper_count = defaultdict(int)   # s2_id → 被几个种子引用
    paper_meta = {}                  # s2_id → paper 对象（取最后一次）

    for seed in seeds:
        s2_id = seed.get("s2_id")
        title = seed.get("title", s2_id)
        if not s2_id:
            continue
        print(f"[fetch_citations] 抓取 references: {title[:50]}...", file=sys.stderr)
        refs = fetch_references(s2_id)
        for p in refs:
            pid = p["paperId"]
            paper_count[pid] += 1
            paper_meta[pid] = p
        time.sleep(1)  # 限速

    total_seeds = len(seeds)

    # 主筛选：intersection_score >= 2
    results = [
        normalize(paper_meta[pid], paper_count[pid])
        for pid in paper_count
        if paper_count[pid] >= 2
    ]

    # Fallback：若结果少于 3 篇，降阈值至 >= 1 且 citation_count > 50
    if len(results) < 3:
        print("[fetch_citations] 主阈值结果不足 3 篇，启用 fallback（>=1 且引用>50）", file=sys.stderr)
        results = [
            normalize(paper_meta[pid], paper_count[pid])
            for pid in paper_count
            if paper_count[pid] >= 1 and (paper_meta[pid].get("citationCount") or 0) > 50
        ]

    # 按引用数降序
    results.sort(key=lambda x: x["citation_count"], reverse=True)

    print(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"[fetch_citations] 最终候选 {len(results)} 篇（共分析 {total_seeds} 个种子）", file=sys.stderr)


if __name__ == "__main__":
    main()
