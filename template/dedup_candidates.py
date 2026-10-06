"""
多源候选论文合并去重
读取三个来源的 JSON 候选文件，按 s2_id 去重，合并来源标签，
排除已读论文、种子论文和 do_not_recommend 命中的论文，
按引用数排序，输出供 Claude 阅读的格式化列表。

并按 interest_profile.json 标记 [顶刊]（top_journals）和 [追踪作者]（known_authors）。

排除依据（均从本地文件运行时读取，不写入代码）：
  - interest_profile.json 的 active_seed_papers（按 s2_id / 标题）
  - data_dir/notes/reading_list.md 中的已读条目（按标题）
  - interest_profile.json 的 do_not_recommend（关键词，大小写不敏感，匹配标题）

用法：
  python dedup_candidates.py candidates_kw.json candidates_s2recs.json candidates_citations.json
"""

import json
import re
import sys
import os

SOURCE_LABELS = {
    "keyword_search": "关键词搜索",
    "s2_recommendations": "S2推荐",
    "citation_intersection": "引用交集",
}

_dir = os.path.dirname(os.path.abspath(__file__))

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
            content = f.read()
        try:
            papers = json.loads(content)
            all_papers.extend(papers)
        except json.JSONDecodeError:
            # 文件可能混有日志行（stderr 被合并进 stdout 时）
            # 找只含 '[' 的行作为 JSON 数组起点（日志行如 [fetch_s2_recs]... 不会匹配）
            # 用 raw_decode 从该位置解析，自动忽略数组后的尾部日志行
            m = re.search(r"^\[$", content, re.MULTILINE)
            if not m:
                print(f"[dedup] 无法提取 JSON，跳过: {path}", file=sys.stderr)
                continue
            try:
                papers, _ = json.JSONDecoder().raw_decode(content, m.start())
                all_papers.extend(papers)
            except json.JSONDecodeError as e:
                print(f"[dedup] JSON 解析失败 {path}: {e}", file=sys.stderr)
    return all_papers


def norm_title(t):
    """标题归一化：小写，只保留字母数字（含中日韩字符），用于跨来源比对"""
    return re.sub(r"[\W_]+", "", (t or "").lower())


def norm_venue(v):
    """期刊名归一化：忽略大小写、标点、开头的 The，& 视同 and"""
    v = (v or "").lower().replace("&", " and ")
    v = re.sub(r"^\s*the\s+", "", v)
    return norm_title(v)


def load_markers():
    """返回 (顶刊归一化名集合, {归一化作者名: 原名})，用于给候选打标记"""
    journals, authors = set(), {}
    profile_path = os.path.join(_dir, "interest_profile.json")
    if not os.path.exists(profile_path):
        return journals, authors
    try:
        with open(profile_path, encoding="utf-8") as f:
            profile = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"[dedup] 读取 interest_profile.json 失败，跳过顶刊/作者标记: {e}", file=sys.stderr)
        return journals, authors
    for j in profile.get("top_journals", []):
        name = j.get("name", "") if isinstance(j, dict) else j
        if isinstance(name, str) and norm_venue(name):
            journals.add(norm_venue(name))
    for a in profile.get("known_authors", []):
        if isinstance(a, dict) and a.get("follow", True) and norm_title(a.get("name")):
            authors[norm_title(a["name"])] = a["name"]
    return journals, authors


def apply_markers(papers, journals, authors):
    """给候选写入 is_top_journal 和 tracked_authors 字段，返回 (顶刊数, 追踪作者数)"""
    n_j = n_a = 0
    for p in papers:
        p["is_top_journal"] = bool(journals) and norm_venue(p.get("venue")) in journals
        p["tracked_authors"] = [authors[norm_title(n)] for n in p.get("authors", [])
                                if norm_title(n) in authors]
        n_j += p["is_top_journal"]
        n_a += bool(p["tracked_authors"])
    return n_j, n_a


def load_exclusions():
    """返回 (排除的 s2_id 集合, 排除的归一化标题集合, do_not_recommend 关键词列表)"""
    ids, titles, keywords = set(), set(), []

    profile_path = os.path.join(_dir, "interest_profile.json")
    if os.path.exists(profile_path):
        try:
            with open(profile_path, encoding="utf-8") as f:
                profile = json.load(f)
            for s in profile.get("active_seed_papers", []):
                if s.get("s2_id"):
                    ids.add(s["s2_id"].strip())
                if s.get("title"):
                    titles.add(norm_title(s["title"]))
            keywords = [k.strip().lower() for k in profile.get("do_not_recommend", [])
                        if isinstance(k, str) and k.strip()]
        except (OSError, json.JSONDecodeError) as e:
            print(f"[dedup] 读取 interest_profile.json 失败，跳过种子/屏蔽过滤: {e}", file=sys.stderr)

    cfg_path = os.path.join(_dir, "config.json")
    try:
        with open(cfg_path, encoding="utf-8") as f:
            data_dir = json.load(f).get("data_dir", "")
        rl_path = os.path.join(data_dir, "notes", "reading_list.md")
        if data_dir and os.path.exists(rl_path):
            with open(rl_path, encoding="utf-8") as f:
                for line in f:
                    # 已读条目格式：- [x] 作者 (年份). *论文标题.* 期刊. — [Name.md](...)
                    if not re.match(r"\s*[-*]\s*\[[xX]\]", line):
                        continue
                    m = re.search(r"\*+([^*]+)\*+", line)
                    if m:
                        titles.add(norm_title(m.group(1)))
    except (OSError, json.JSONDecodeError) as e:
        print(f"[dedup] 读取 reading_list.md 失败，跳过已读过滤: {e}", file=sys.stderr)

    titles.discard("")
    return ids, titles, keywords


def apply_exclusions(papers, ids, titles, keywords):
    """返回 (保留列表, 已读/种子排除数, do_not_recommend 排除列表)"""
    kept, n_read, blocked = [], 0, []
    for p in papers:
        t = p.get("title", "")
        if p.get("s2_id", "").strip() in ids or norm_title(t) in titles:
            n_read += 1
            continue
        hit = next((k for k in keywords if k in t.lower()), None)
        if hit:
            blocked.append((t, hit))
            continue
        kept.append(p)
    return kept, n_read, blocked


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

    marks = []
    if p.get("is_top_journal"):
        marks.append("[顶刊]")
    if p.get("tracked_authors"):
        marks.append(f"[追踪作者：{', '.join(p['tracked_authors'])}]")

    lines = [
        f"[{rank}] **{title}** ({year})",
        f"    {author_str} | {venue}",
        f"    来源：{source_str}" + (f"  [{tier_str}]" if tier_str else "")
        + (f"  {' '.join(marks)}" if marks else ""),
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
    papers, n_read, blocked = apply_exclusions(papers, *load_exclusions())
    n_top, n_tracked = apply_markers(papers, *load_markers())
    papers.sort(key=lambda x: x.get("citation_count") or 0, reverse=True)

    print(f"\n{'='*60}")
    print(f"  合并候选论文（共 {len(papers)} 篇，已去重）")
    print(f"  已排除：已读/种子论文 {n_read} 篇，do_not_recommend 命中 {len(blocked)} 篇")
    print(f"  ★ = 多源命中（强信号）；[顶刊] {n_top} 篇，[追踪作者] {n_tracked} 篇")
    print(f"{'='*60}\n")
    for t, k in blocked:
        print(f"  [已屏蔽 · {k}] {t}")
    if blocked:
        print()

    for i, p in enumerate(papers, 1):
        print(format_paper(p, i))
        print()

    print(f"{'='*60}")
    print(f"  请从以上列表中，优先三层各选一篇：")
    print(f"  Tier 1 直接相关 / Tier 2 大领域 / Tier 3 交叉学科")
    print(f"  参考 interest_profile.known_gaps 优先填补空白")
    print(f"  相关性相近时，优先选 ★、[顶刊]、[追踪作者]")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
