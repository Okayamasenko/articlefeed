"""
rename_pdfs.py — 自动重命名学术 PDF

策略：
  1. pdfinfo 读内嵌元数据（本地，零网络请求）
  2. 元数据不完整时，CrossRef API 补全（免费，无需 key）
  3. 两者都失败则标记，跳过，不乱改

用法：
  python rename_pdfs.py                # 处理默认目录
  python rename_pdfs.py --dry-run      # 只预览，不实际重命名
  python rename_pdfs.py --dir PATH     # 指定目录
"""

import subprocess
import json
import urllib.request
import urllib.parse
import re
import os
import argparse
import time

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
with open(CONFIG_PATH, encoding="utf-8") as _f:
    _cfg = json.load(_f)
PDF_DIR = _cfg["data_dir"]


def is_already_renamed(filename):
    """检测是否已符合 Author_YYYY_Keywords.pdf 格式。"""
    return bool(re.search(r'_\d{4}_', filename))


def run_pdfinfo(path):
    """用 pdfinfo 读 PDF 内嵌元数据。"""
    try:
        result = subprocess.run(
            ["pdfinfo", path],
            capture_output=True, text=True, timeout=10
        )
        info = {}
        for line in result.stdout.splitlines():
            if ":" in line:
                key, _, val = line.partition(":")
                info[key.strip()] = val.strip()
        return info
    except Exception:
        return {}


def query_crossref(title):
    """用标题查 CrossRef，返回第一条结果的元数据。"""
    params = urllib.parse.urlencode({
        "query.title": title,
        "rows": 1,
        "select": "title,author,published"
    })
    url = f"https://api.crossref.org/works?{params}"
    headers = {"User-Agent": "ArticleFeed/1.0 (academic research tool)"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            items = json.loads(resp.read()).get("message", {}).get("items", [])
            return items[0] if items else None
    except Exception:
        return None


def parse_year(date_str):
    """从各种日期字符串里提取四位年份。"""
    m = re.search(r'(19|20)\d{2}', date_str or "")
    return m.group(0) if m else None


def make_filename(authors, year, title):
    """生成 Author1_Author2_YYYY_Key1_Key2_Key3.pdf"""
    # 最多取前两位作者的姓
    last_names = []
    for a in authors[:2]:
        if isinstance(a, dict):
            name = a.get("family") or a.get("name") or ""
        else:
            # "Last, First" 或 "First Last" 格式
            parts = str(a).replace(",", "").split()
            name = parts[-1] if parts else ""
        name = re.sub(r"[^a-zA-Z]", "", name).capitalize()
        if name:
            last_names.append(name)

    author_str = "_".join(last_names) or "Unknown"

    # 标题关键词：跳过停用词，取前 4 个
    stopwords = {
        "a", "an", "the", "of", "in", "on", "at", "to", "for",
        "and", "or", "but", "with", "by", "from", "as", "is", "are",
        "its", "their", "this", "that", "it", "be", "has", "have",
    }
    words = re.findall(r"[a-zA-Z]+", title or "")
    keywords = [w.capitalize() for w in words if w.lower() not in stopwords][:4]
    keyword_str = "_".join(keywords) or "Paper"

    return f"{author_str}_{year}_{keyword_str}.pdf"


def process_pdf(path, dry_run=False):
    filename = os.path.basename(path)

    if is_already_renamed(filename):
        print(f"  [跳过，已命名] {filename}")
        return

    print(f"\n  {filename}")

    # ── Step 1: pdfinfo ──────────────────────────────────────────
    info = run_pdfinfo(path)
    title  = info.get("Title", "").strip()
    author_raw = info.get("Author", "").strip()
    year   = parse_year(info.get("CreationDate", "") or info.get("ModDate", ""))

    authors = []
    if author_raw:
        # 拆分多个作者："A and B" 或 "A; B"
        for part in re.split(r"\s+and\s+|;\s*", author_raw):
            part = part.strip()
            if part:
                authors.append({"family": part.split()[-1], "given": ""})

    # ── Step 2: CrossRef（仅在缺信息时查）────────────────────────
    if title and (not year or not authors):
        print(f"    元数据不完整，查 CrossRef...")
        time.sleep(0.5)  # CrossRef 礼貌限速
        cr = query_crossref(title)
        if cr:
            if not authors:
                authors = cr.get("author", [])
            if not year:
                parts = cr.get("published", {}).get("date-parts", [[]])
                if parts and parts[0]:
                    year = str(parts[0][0])
            cr_titles = cr.get("title", [])
            if cr_titles:
                title = cr_titles[0]

    # ── Step 3: 验证 ─────────────────────────────────────────────
    if not authors:
        print(f"    ⚠ 无法确定作者 → 跳过（请手动处理）")
        return
    if not year or not (1900 <= int(year) <= 2030):
        print(f"    ⚠ 无法确定年份 → 跳过（请手动处理）")
        return
    if not title:
        title = re.sub(r"[_\-]+", " ", os.path.splitext(filename)[0])

    new_name = make_filename(authors, year, title)
    new_path = os.path.join(os.path.dirname(path), new_name)

    print(f"    → {new_name}")

    if not dry_run:
        os.rename(path, new_path)
        print(f"    ✓ 已重命名")
    else:
        print(f"    (dry-run，未执行)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default=PDF_DIR, help="PDF 所在目录")
    parser.add_argument("--dry-run", action="store_true", help="预览，不实际改名")
    args = parser.parse_args()

    pdfs = sorted(f for f in os.listdir(args.dir) if f.lower().endswith(".pdf"))
    print(f"目录：{args.dir}")
    print(f"找到 {len(pdfs)} 个 PDF\n")

    for f in pdfs:
        process_pdf(os.path.join(args.dir, f), dry_run=args.dry_run)

    print("\n完成。")


if __name__ == "__main__":
    main()
