"""
论文元数据查询工具
用法：
  python lookup_paper.py --doi "10.xxxx/xxxxx"
  python lookup_paper.py --title "The Effect of Identity Signaling..."
"""

import urllib.request
import urllib.parse
import json
import argparse
import sys
import os

S2_BASE = "https://api.semanticscholar.org/graph/v1"

_cfg_path = os.path.join(os.path.dirname(__file__), "config.json")
with open(_cfg_path, encoding="utf-8") as _f:
    _cfg = json.load(_f)

HEADERS = {
    "User-Agent": "ArticleFeed/1.0",
    "x-api-key": _cfg.get("s2_api_key", ""),
}

PAPER_FIELDS = "title,year,citationCount,journal,authors,externalIds,abstract,publicationVenue"
AUTHOR_FIELDS = "name,hIndex,citationCount,affiliations"


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def get_paper_by_doi(doi):
    url = f"{S2_BASE}/paper/DOI:{urllib.parse.quote(doi)}?fields={PAPER_FIELDS}"
    return fetch(url)


def get_paper_by_title(title):
    params = urllib.parse.urlencode({"query": title, "fields": PAPER_FIELDS, "limit": 1})
    url = f"{S2_BASE}/paper/search?{params}"
    data = fetch(url)
    if data.get("data"):
        return data["data"][0]
    return None


def get_author(author_id):
    url = f"{S2_BASE}/author/{author_id}?fields={AUTHOR_FIELDS}"
    return fetch(url)


def format_output(paper):
    lines = []

    title = paper.get("title", "N/A")
    year = paper.get("year", "N/A")
    citations = paper.get("citationCount", "N/A")

    venue = paper.get("publicationVenue") or paper.get("journal") or {}
    journal_name = venue.get("name", "N/A") if isinstance(venue, dict) else "N/A"

    doi = (paper.get("externalIds") or {}).get("DOI", "N/A")
    paper_id = paper.get("paperId", "N/A")

    lines.append("=" * 60)
    lines.append(f"标题: {title}")
    lines.append(f"年份: {year}")
    lines.append(f"S2 ID: {paper_id}")
    lines.append(f"DOI:  {doi}")
    lines.append(f"期刊: {journal_name}")
    lines.append(f"被引: {citations} 次")
    lines.append("")

    authors = paper.get("authors", [])
    if authors:
        lines.append(f"作者 ({len(authors)} 人):")
        for a in authors[:5]:  # 最多显示5位
            author_id = a.get("authorId")
            name = a.get("name", "N/A")
            if author_id:
                try:
                    detail = get_author(author_id)
                    h = detail.get("hIndex", "?")
                    c = detail.get("citationCount", "?")
                    aff = detail.get("affiliations", [])
                    aff_str = aff[0] if aff else "N/A"
                    lines.append(f"  - {name} | h-index: {h} | 总引用: {c} | 机构: {aff_str}")
                except Exception:
                    lines.append(f"  - {name}")
        if len(authors) > 5:
            lines.append(f"  ... 共 {len(authors)} 位作者")

    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="查询论文元数据")
    parser.add_argument("--doi", help="论文 DOI")
    parser.add_argument("--title", help="论文标题（模糊搜索）")
    parser.add_argument("--json", action="store_true", help="输出原始 JSON（含 paperId）")
    args = parser.parse_args()

    if not args.doi and not args.title:
        print("请提供 --doi 或 --title 参数")
        sys.exit(1)

    try:
        if args.doi:
            paper = get_paper_by_doi(args.doi)
        else:
            paper = get_paper_by_title(args.title)
            if not paper:
                print("未找到匹配论文")
                sys.exit(1)

        if args.json:
            print(json.dumps(paper, ensure_ascii=False, indent=2))
        else:
            print(format_output(paper))
    except Exception as e:
        print(f"查询失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
