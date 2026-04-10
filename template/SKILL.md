---
name: articlefeed
description: "Academic paper reading system — find papers via Semantic Scholar, read with structured notes, discuss with auto-recording, track progress. 7 commands: /setup /feed /read /discuss /recap /update /sync"
metadata:
  openclaw:
    requires:
      bins:
        - python
        - pdftotext
---

# ArticleFeed

学术论文阅读管理系统，运行在 Claude Code 中。帮研究者做三件事：**找论文、读论文、追踪进度**。

论文来源：[Semantic Scholar](https://www.semanticscholar.org)（AI2 维护，收录 2 亿+ 论文，覆盖人文社科和理工科，免费无需登录）。

---

## 快速安装

**第一步**：编辑 `config.json`，填入你的数据目录路径：

```json
{
  "data_dir": "/your/research/folder",
  "s2_api_key": "可选，免费申请加速搜索"
}
```

**第二步**：运行安装脚本：

```bash
cd /path/to/articlefeed
bash install.sh
```

安装脚本会自动：
1. 创建 `.claude/commands` 软链接（Claude Code 通过此链接识别技能命令）
2. 创建 `memory/` 软链接（持久记忆目录）
3. 复制权限配置（写文件、建文件夹、下载 PDF 等操作不再弹确认）

**第三步**：在 ArticleFeed 目录打开 Claude Code，输入 `/setup` 完成研究方向配置。

---

## 命令列表

| 命令 | 触发方式 | 功能 |
|------|---------|------|
| `/setup` | 首次使用 | 对话了解研究方向，生成所有配置文件 |
| `/feed` | 日常 | 更新搜索词 → 搜索 Semantic Scholar → 推荐论文 → 能获取原文则直接完整精读 |
| `/read` | 手动精读 | 提交 PDF 路径 / DOI / 摘要，生成 4 节结构化笔记 |
| `/discuss 关键词` | 深入研读 | 用作者姓、年份或标题词定位已读笔记，讨论内容自动记录到笔记 |
| `/recap` | 进度复盘 | 已读概览、理论框架完整度、下一步建议；归档活跃阅读区，生成阶段研究版图摘要，保存快照 |
| `/update` | 方向调整 | 研究方向变化时同步更新 MEMORY.md 和搜索词 |
| `/sync` | 维护 | 检查所有文档逻辑一致性，自动修复遗漏和冲突 |

---

## 笔记结构

每篇论文分析包含四个部分：

| 部分 | 内容 |
|------|------|
| **一、论文权重** | 期刊/会议排名、IF、数据库收录、引用数；各作者机构、职级、h-index |
| **二、论文亮点** | 方法创新 / 对系统问题的批判 / 研究对象的重要性 |
| **三、可借鉴之处** | 理论框架、方法细节、概念工具（标明可用于论文哪个部分） |
| **四、如何用到你的论文里** | 文献综述定位、建议引用句式（英文）、方法论先例 |

笔记语言：**中文为主，关键引用句式保留英文原文**。

---

## 依赖说明

| 依赖 | 用途 | 安装 |
|------|------|------|
| Python（标准库） | 运行搜索和元数据查询脚本 | 通常已预装 |
| pdftotext（poppler） | 提取 PDF 全文 | `brew install poppler` |
| Claude Code | 执行技能命令 | [安装说明](https://docs.anthropic.com/claude-code) |

Semantic Scholar API key 可选，无 key 也能正常使用（遇限速自动重试）。

---

## 文件结构

```
articlefeed/
├── SKILL.md                  ← 本文件
├── CLAUDE.md                 ← 项目级规则（Claude Code 自动加载）
├── install.sh                ← 一键安装
├── config.json               ← 路径和 API key 配置（唯一需要手动编辑的文件）
├── search_config.json        ← 搜索词（Claude 动态维护）
├── recommend.py              ← 关键词搜索（--json 模式供 /feed 调用）
├── fetch_s2_recs.py          ← S2 ML 推荐（基于 interest_profile 种子论文）
├── fetch_citations.py        ← 引用交集分析（种子论文共同引用的基础文献）
├── dedup_candidates.py       ← 三源合并去重
├── interest_profile.json     ← 结构化兴趣模型（/feed 和 /read 动态维护）
├── lookup_paper.py           ← 查询论文元数据（引用数、期刊、作者 h-index）
├── rename_pdfs.py            ← PDF 批量重命名
├── commands/                 ← 7 个技能文件
│   ├── setup.md
│   ├── feed.md
│   ├── read.md
│   ├── discuss.md
│   ├── recap.md
│   ├── update.md
│   └── sync.md
├── memory/
│   └── MEMORY.md             ← Claude 的持久记忆
└── notes/
    └── WORKFLOW.md           ← 工作流说明（/setup 自动部署到数据目录）

data_dir/                     ← 你在 config.json 里填的路径
  notes/
    reading_list.md
    YYYY-MM-DD/
      recommendations.md
      Author_Year_Keywords/
        Author_Year_Keywords.pdf
        Author_Year_Keywords.md
    recaps/
      YYYY-MM-DD_recap.md
```
