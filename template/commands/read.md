# /read — 论文精读

精读用户提交的论文（本地 PDF、DOI、链接或粘贴的摘要），生成笔记并更新阅读记录。全程不向用户确认。

## 笔记

- **位置**：`data_dir/notes/YYYY-MM-DD/Name/`，其中放 `Name.pdf` 和 `Name.md`。`data_dir` 从 `config.json` 读取。
- **命名**：`Author_Year_Keywords`，最多两位作者姓、年份、4 个关键词。
- **元数据**：用 `python lookup_paper.py --doi ...` 或 `--title ...` 查询。只有摘要可用时，在笔记开头标注「仅基于摘要」。
- **语言**：中文为主，关键引用句式保留英文。

笔记必须包含以下四节，标题照抄：

```markdown
# 论文标题（原文）
作者 (年份) | 期刊/会议 | DOI

## 一、论文权重
- 发表渠道：期刊写收录库（SSCI/AHCI/ESCI/Scopus）、IF、分区、期刊 h-index；会议写 CORE 排名和录用率；预印本写平台和投稿状态
- 作者：每位作者的机构、职级、研究方向、代表期刊、h-index。查不到的写「未查到」，不得编造
- 引用：总引用数和年均引用；总体评价一两句

## 二、论文亮点
方法创新 / 对现有体系的批判 / 研究对象的重要性

## 三、可借鉴之处
理论框架、方法细节、概念工具，每条注明可用于我论文的哪个部分

## 四、如何用到你的论文里
文献综述定位、建议引用句式（英文）、方法论先例、研究动机
```

第三、四节要结合 `memory/MEMORY.md` 里的研究设计来写。

## 阅读记录同步

保存笔记后更新以下文件。被 `/feed` 内嵌调用时同样执行。

- **`notes/reading_list.md`**：在 `## 近期活跃阅读` 下添加 `- [x] 作者 (年份). *论文标题.* 期刊. — [Name.md](YYYY-MM-DD/Name/Name.md)`。标题必须用 `*…*` 包住，`dedup_candidates.py` 靠它识别已读论文。
- **`search_config.json`**：把笔记文件名追加到 `based_on_notes`，并更新 `last_updated`。不删除旧条目，不修改 `update_reason`。
- **`memory/MEMORY.md`**：在 `## Reading Progress` 下追加一行 `- Name.md — 一句话核心贡献`，不超过 80 字，不删除旧条目。
- **`interest_profile.json`**：只在有变化时修改。
  - 这篇论文会在论文的多个章节被引用：加入 `active_seed_papers`，写明 `s2_id` 和 `why_seed`。上限 8 篇，满了就退役最早加入、且与当前研究阶段最远的一篇。
  - 填补了 `known_gaps` 中的某一条：删除该条。
  - 发现值得长期追踪的作者：加入 `known_authors`。

## 汇报

告诉用户笔记保存位置，并用一两句话说明最值得借鉴的一点。
