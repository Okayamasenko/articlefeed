"""
多源候选论文合并去重
读取三个来源的 JSON 候选文件，按 s2_id 去重，合并来源标签，
按引用数排序，输出供 Claude 阅读的格式化列表。

用法：
  python dedup_candidates.py candidates_kw.json candidates_s2recs.json candidates_citations.json
"""

import json
import sys
import os

SOURCE_LABELS = {
    "keyword_search": "关键词搜索",
    "s2_recommendations": "S2推荐",
    "citation_intersection": "引用交集",
}

TIER_LABELS = {
    "tier1": "Tier1·核心",
    "tier2": "Tier2·邻域",
    "tier3": "Tier3·野卡",
}


def load_candidates(paths):
    all_papers = []
    for path in paths:
        if not os.path.exists(path):
            print(f"[dedup] 文件不存在，跳过: {path}", file=sys.stderr)
            continue
        with open(path, encoding="utf-8") as f:
            try:
                papers = json.load(f)
                all_papers.extend(papers)
            except json.JSONDecodeError as e:
                print(f"[dedup] JSON 解析失败 {path}: {e}", file=sys.stderr)
    return all_papers


def dedup(papers):
    """按 s2_id 去重，合并 source 和 tier 标签"""
    merged = {}  # s2_id → paper dict
    for p in papers:
        pid = p.get("s2_id", "").strip()
        if not pid:
            # 无 s2_id 时用 doi 作 fallback key
            pid = f"doi:{p.get('doi', '').strip()}" if p.get("doi") else None
        if not pid:
            continue

        if pid not in merged:
            merged[pid] = dict(p)
            merged[pid]["sources"] = []
            merged[pid]["tiers"] = []

        src = p.get("source", "")
        if src and src not in merged[pid]["sources"]:
            merged[pid]["sources"].append(src)

        tier = p.get("tier")
        if tier and tier not in merged[pid]["tiers"]:
            merged[pid]["tiers"].append(tier)

        # 取最高引用数（不同来源元数据可能略有差异）
        if (p.get("citation_count") or 0) > (merged[pid].get("citation_count") or 0):
            merged[pid]["citation_count"] = p["citation_count"]

    return list(merged.values())


def format_paper(p, rank):
    title = p.get("title", "N/A")
    year = p.get("year", "?")
    venue = p.get("venue", "N/A") or "N/A"
    citations = p.get("citation_count", 0)
    oa = "✓" if p.get("open_access_url") else "✗"
    doi = p.get("doi", "")

    sources = p.get("sources", [])
    source_str = " + ".join(SOURCE_LABELS.get(s, s) for s in sources)
    if len(sources) >= 2:
        source_str = f"★ {source_str}"  # 多源命中加星标注

    tiers = p.get("tiers", [])
    tier_str = " / ".join(TIER_LABELS.get(t, t) for t in tiers) if tiers else ""

    authors = p.get("authors", [])
    author_str = ", ".join(authors[:3])
    if len(authors) > 3:
        author_str += " et al."

    lines = [
        f"[{rank}] **{title}** ({year})",
        f"    {author_str} | {venue}",
        f"    来源：{source_str}" + (f"  [{tier_str}]" if tier_str else ""),
        f"    引用：{citations} | 开放获取：{oa}" + (f" | DOI: {doi}" if doi else ""),
    ]
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("用法: python dedup_candidates.py file1.json [file2.json ...]")
        sys.exit(1)

    paths = sys.argv[1:]
    papers = load_candidates(paths)
    papers = dedup(papers)
    papers.sort(key=lambda x: x.get("citation_count") or 0, reverse=True)

    print(f"\n{'='*60}")
    print(f"  合并候选论文（共 {len(papers)} 篇，已去重）")
    print(f"  ★ = 多源命中（强信号）")
    print(f"{'='*60}\n")

    for i, p in enumerate(papers, 1):
        print(format_paper(p, i))
        print()

    print(f"{'='*60}")
    print(f"  请从以上列表中，优先三层各选一篇：")
    print(f"  Tier 1 直接相关 / Tier 2 大领域 / Tier 3 交叉学科")
    print(f"  参考 interest_profile.known_gaps 优先填补空白")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
