# ArticleFeed

学术论文阅读管理系统，运行在 Claude Code 中。帮研究者做三件事：找论文、读论文、追踪进度。

## 可用命令

| 命令 | 功能 |
|------|------|
| `/setup` | 首次配置：对话了解研究方向，生成 MEMORY.md、search_config.json、reading_list.md |
| `/feed` | 论文推荐：更新搜索词 → 搜索 Semantic Scholar → 筛选推荐 → 尝试下载开放获取 PDF → 能获取原文则直接完整精读（与 /read 质量一致） |
| `/read` | 论文精读：4节结构化笔记（论文权重 / 亮点 / 可借鉴 / 如何用到论文），存入数据目录 |
| `/recap` | 阅读进度：已读概览、理论框架完整度、下一步建议；归档活跃阅读区，生成阶段研究版图摘要，保存快照至 recaps/ |
| `/discuss 关键词` | 论文讨论：用作者姓、年份或标题关键词定位已读笔记，进入问答模式，自动将有价值的讨论内容追加到笔记文件 |
| `/update` | 研究方向有变化时：同步更新 MEMORY.md 和 search_config.json |
| `/sync` | 文档一致性检查：审查所有命令和文档文件，修复命令遗漏、路径不一致、逻辑冲突等问题 |

## 文件结构

```
ArticleFeed/               ← 项目根目录（克隆后得到的文件夹）
  config.json              ← 唯一需要用户手动编辑的文件（填写 data_dir 路径）
  search_config.json       ← Semantic Scholar 搜索词，由 Claude 在 /feed 时动态更新
  interest_profile.json    ← 结构化兴趣模型（种子论文/文献缺口/追踪作者），/feed 和 /read 动态维护
  commands/                ← 技能文件（.claude/commands 软链接指向此目录）
  memory/MEMORY.md         ← Claude 的持久记忆（install.sh 创建软链接到用户 ~/.claude/）
  recommend.py             ← 关键词搜索脚本（--json 模式，/feed 时调用）
  fetch_s2_recs.py         ← S2 ML 向量推荐（基于 interest_profile 种子论文）
  fetch_citations.py       ← 引用交集分析（种子论文共同引用的基础文献）
  dedup_candidates.py      ← 三源合并去重（★ 标注多源命中强信号）
  rename_pdfs.py           ← PDF 批量重命名（Author_Year_Keywords.pdf 格式）
  lookup_paper.py          ← 查询论文元数据（DOI → 引用数、期刊、作者 h-index）

data_dir/                  ← 用户在 config.json 中填写的路径（PDF 放这里）
  notes/
    reading_list.md        ← 阅读追踪列表（分「近期活跃阅读」和「历史归档」两区）
    recaps/
      YYYY-MM-DD_recap.md  ← /recap 生成的阶段研究版图摘要（/feed 读取此文件替代翻阅归档区）
    YYYY-MM-DD/
      recommendations.md
      Author_Year_Keywords/
        Author_Year_Keywords.pdf
        Author_Year_Keywords.md
```

## 核心规则

**文件写入**：所有命令执行过程中的文件操作（写笔记、更新 reading_list.md、写 recommendations.md、更新 search_config.json、更新 MEMORY.md 等）**直接执行，不向用户请求确认**。命令说明中凡标注"自动执行"或"无需提醒"的步骤，均属此类。

**路径**：所有路径从 `config.json` 读取 `data_dir`，脚本内用 `os.path.dirname(__file__)` 推算自身位置，禁止在代码中硬编码绝对路径。

**精读后必须同步**（自动执行，无需提醒）：
1. `reading_list.md` 的 `## 近期活跃阅读` 区块 — 添加 `[x]` 条目，附相对链接（`YYYY-MM-DD/Name/Name.md`，相对于 notes/ 目录）
2. `search_config.json` `based_on_notes` — 追加笔记文件名，**不删除旧条目**，完整保留
3. 建日期文件夹，复制 PDF，保存 MD — 一步完成
4. **不修改** `search_config.json` 的 `update_reason`（仅 `/feed` 更新检索词时写入）
5. `interest_profile.json` — 评估是否加入 `active_seed_papers`、填掉 `known_gaps`、追加 `known_authors`（见 read.md Step 8）

**`/recap` 时额外执行**（自动执行，无需提醒）：
- 将 `reading_list.md` 的 `## 近期活跃阅读` 中所有条目移入 `## 历史归档`（按年月分组），清空活跃区
- 生成阶段研究版图摘要，保存至 `recaps/YYYY-MM-DD_recap.md`

**首次使用**：编辑 `config.json` 填写 `data_dir`，运行 `bash install.sh`（自动创建软链接并从 `template/` 复制初始配置文件），然后打开 Claude Code 输入 `/setup` 完成研究方向配置。

## 文档同步规则（自动执行，无需提醒）

每次新增或修改 `commands/` 下任何文件后，立即检查并更新以下三个文件，确保新命令已被记录、描述一致：

1. **README.md** — 命令循环图、"包含什么"表格、"日常使用"表格
2. **CLAUDE.md**（本文件）— 可用命令表格
3. **SKILL.md** — OpenClaw 命令列表表格
4. **notes/WORKFLOW.md** — 顶部命令速查表

同时检查：
- 各命令文件之间的路径约定是否统一（`data_dir`、`notes_dir` 等）
- 自动同步规则（reading_list / search_config / MEMORY.md）在各命令中是否描述一致
- 有无命令之间的逻辑冲突
