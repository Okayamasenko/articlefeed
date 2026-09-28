"""
论文推荐脚本 — 按三个层级从 Semantic Scholar 搜索候选论文

搜索词从 search_config.json 动态读取，由 Claude 根据阅读记录维护。
每次运行 Claude 会先更新 search_config.json，再跑此脚本。

用法：
  python recommend.py           # 每个层级各取 5 篇
  python recommend.py --n 8     # 每个层级各取 8 篇
"""

import urllib.request
import urllib.parse
import json
import argparse
import os
import sys
import time

S2_BASE = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = "title,year,citationCount,journal,authors,externalIds,openAccessPdf,publicationVenue"

_cfg_path = os.path.join(os.path.dirname(__file__), "config.json")
with open(_cfg_path, encoding="utf-8") as _f:
    _cfg = json.load(_f)

HEADERS = {
    "User-Agent": "ArticleFeed/1.0 (research assistant)",
    "x-api-key": _cfg.get("s2_api_key", ""),
}
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "search_config.json")


def load_config(quiet=False):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    out = sys.stderr if quiet else sys.stdout
    print(f"配置更新于：{config.get('last_updated', '?')}", file=out)
    print(f"依据笔记：{', '.join(config.get('based_on_notes', []))}", file=out)
    print(f"更新原因：{config.get('update_reason', '—')}\n", file=out)
    return config["tiers"]


def search_s2(query, n=5, retries=3):
    params = urllib.parse.urlencode({
        "query": query,
        "fields": FIELDS,
        "limit": n,
    })
    url = f"{S2_BASE}?{params}"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read()).get("data", [])
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                wait = 5 * (attempt + 1)
                print(f"  [限速，等待 {wait}s 重试] {query[:40]}...", file=sys.stderr)
                time.sleep(wait)
            else:
                raise
    return []


def format_paper(p, rank):
    title = p.get("title", "N/A")
    year = p.get("year", "?")
    citations = p.get("citationCount", 0)

    venue = p.get("publicationVenue") or p.get("journal") or {}
    journal = venue.get("name", "N/A") if isinstance(venue, dict) else "N/A"

    authors = p.get("authors", [])
    author_names = [a.get("name", "") for a in authors[:3]]
    author_str = ", ".join(author_names)
    if len(authors) > 3:
        author_str += " et al."

    doi = (p.get("externalIds") or {}).get("DOI", "")
    oa_pdf = p.get("openAccessPdf") or {}
    oa_url = oa_pdf.get("url", "")
    oa_str = f"开放获取 ✓  {oa_url}" if oa_url else "需订阅"
    doi_url = f"https://doi.org/{doi}" if doi else "N/A"

    return (
        f"  [{rank}] {title}\n"
        f"      {author_str} ({year}) | {journal}\n"
        f"      引用：{citations} | {oa_str}\n"
        f"      DOI：{doi_url}"
    )


def paper_to_dict(p, tier_key):
    """将 S2 paper 对象归一化为统一 schema（供 --json 和 dedup_candidates.py 使用）"""
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
        "source": "keyword_search",
        "tier": tier_key,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=5, help="每个层级最终展示几篇")
    parser.add_argument("--json", action="store_true", help="输出 JSON 数组（供 dedup_candidates.py 使用）")
    args = parser.parse_args()

    tiers = load_config(quiet=args.json)
    all_papers_json = []

    for tier_key, tier_data in tiers.items():
        label = tier_data["label"]
        description = tier_data["description"]
        queries = tier_data["terms"]

        if not args.json:
            print(f"\n{'='*60}")
            print(f"  {label}  —  {description}")
            print(f"{'='*60}")

        seen = set()
        papers = []
        for q in queries:
            try:
                results = search_s2(q, args.n)
                for p in results:
                    pid = p.get("paperId")
                    if pid and pid not in seen:
                        seen.add(pid)
                        papers.append(p)
                time.sleep(2)
            except Exception as e:
                if not args.json:
                    print(f"  [搜索失败] {q}: {e}")

        papers.sort(key=lambda x: x.get("citationCount") or 0, reverse=True)
        papers = papers[:args.n]

        if args.json:
            all_papers_json.extend(paper_to_dict(p, tier_key) for p in papers)
        else:
            for i, p in enumerate(papers, 1):
                print(format_paper(p, i))
                print()

    if args.json:
        print(json.dumps(all_papers_json, ensure_ascii=False, indent=2))
    else:
        print("\n" + "="*60)
        print("  候选论文拉取完成，等待 Claude 筛选推荐。")
        print("="*60)


if __name__ == "__main__":
    main()
