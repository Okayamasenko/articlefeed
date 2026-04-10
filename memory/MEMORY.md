# Project Memory

## Research
<!-- 在此填写你的研究主题概述，2-3句话。Claude 会据此动态更新搜索词。-->

**Topic**: [你的研究主题]

**Key variables / framework**: [核心变量或理论框架]

**Status**: [当前进展]

## Project Structure
Paths are managed in `config.json`. Update that file if folders are renamed.
- ArticleFeed dir: `recommend.py`, `lookup_paper.py`, `rename_pdfs.py`, `search_config.json`, `config.json`
- `config.json["data_dir"]` — data root; PDFs here, notes in `data_dir/notes/`

## Key Decisions
- Paper feed: Semantic Scholar API; search terms in search_config.json, updated by Claude each `/feed` session
- Three-tier reading diet: Tier 1 core / Tier 2 adjacent field / Tier 3 wild card (tech-heavy)
- Note folder structure: all analyzed papers → notes/YYYY-MM-DD/PaperName/ (PDF + MD together); recommendations list → notes/YYYY-MM-DD/recommendations.md
- PDF naming convention: Author_Year_Keywords.pdf; automated via rename_pdfs.py (no Claude needed)
- Paper analysis: interactive via Claude Code (4 sections: 论文权重 / 亮点 / 可借鉴 / 如何用到论文)
- Memory design: full history preserved; reading_list.md splits into Active and Archive zones; /recap compresses archived papers into a stage summary for efficient /feed reads

## Standing Coding Rules (apply to all future work)
1. **No hardcoded paths/keywords**: always read from config.json or derive paths relative to script location (`os.path.dirname(__file__)`). Never write absolute paths as string literals in scripts.
2. **Keep folder clean**: when adding a new script, check if any existing script is superseded and delete it. When changing workflow, immediately sync all related files (WORKFLOW.md, MEMORY.md, reading_list.md, config.json).

## Auto-sync Rules (execute automatically, no reminder needed)
After analyzing any paper (/read or /feed):
1. Add [x] entry to `## 近期活跃阅读` section of reading_list.md with correct relative link (YYYY-MM-DD/PaperName/PaperName.md, relative to notes/ dir)
2. Append paper note filename to search_config.json `based_on_notes` — **do not delete old entries**, full history preserved
3. Append one line to Reading Progress below — **do not delete old entries**, keep each line under 80 chars
4. Create the dated folder, copy PDF in, save MD — all in one step
5. Do NOT update `update_reason` in search_config.json during /read — only /feed writes update_reason

When /recap runs:
- Move all entries from `## 近期活跃阅读` to `## 历史归档` in reading_list.md
- Clear the Active section (keep heading and comment, remove entries)
- Save stage summary to recaps/YYYY-MM-DD_recap.md

## Reading Progress (所有已读，供 /feed 参考)
<!-- Claude 自动维护，追加不删除，每行格式：- PaperName.md — 一句话核心贡献 -->

## Relevant Journals
<!-- 填写你的研究领域核心期刊，Claude 评估论文权重时会用到 -->
