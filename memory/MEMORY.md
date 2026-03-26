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
- Paper feed: Semantic Scholar API; search terms in search_config.json, updated by Claude each session
- Three-tier reading diet: Tier 1 core / Tier 2 adjacent field / Tier 3 wild card (tech-heavy)
- Note folder structure: all analyzed papers → notes/YYYY-MM-DD/PaperName/ (PDF + MD together); recommendations list → notes/YYYY-MM-DD/recommendations.md
- PDF naming convention: Author_Year_Keywords.pdf; automated via rename_pdfs.py (no Claude needed)
- Paper analysis: interactive via Claude Code (4 sections: 论文权重 / 亮点 / 可借鉴 / 如何用到论文)

## Standing Coding Rules (apply to all future work)
1. **No hardcoded paths/keywords**: always read from config.json or derive paths relative to script location (`os.path.dirname(__file__)`). Never write absolute paths as string literals in scripts.
2. **Keep folder clean**: when adding a new script, check if any existing script is superseded and delete it. When changing workflow, immediately sync all related files (WORKFLOW.md, MEMORY.md, reading_list.md, config.json).

## Auto-sync Rules (execute automatically, no reminder needed)
After analyzing any paper:
1. Add [x] entry to reading_list.md with correct relative link (YYYY-MM-DD/PaperName/PaperName.md, relative to notes/ dir)
2. Add paper note filename to search_config.json `based_on_notes` — keep max 25 entries (sliding window, drop oldest)
3. Add to Reading Progress below — keep max 20 entries (sliding window, drop oldest)
4. Create the dated folder, copy PDF in, save MD — all in one step

## Reading Progress (最近已读，供 /feed 参考)
<!-- Claude 自动维护，最多 20 条，超出时删除最旧的 -->

## Relevant Journals
<!-- 填写你的研究领域核心期刊，Claude 评估论文权重时会用到 -->
