# ArticleFeed — 快速上手

ArticleFeed 是一套运行在 Claude Code 里的学术论文阅读系统，帮你做三件事：**找论文、读论文、追踪进度**。

## 它是怎么工作的

整个系统由两部分组成：

- **Python 脚本**：搜索论文、查询引用数和作者信息、批量重命名 PDF。数据来源是 [Semantic Scholar](https://www.semanticscholar.org)——由艾伦人工智能研究所（AI2）维护的免费学术搜索引擎，收录超过 2 亿篇论文，覆盖人文社科和理工科，无需登录
- **Claude Code 技能（skill）**：你输入 `/feed`、`/read` 等命令，Claude 就会执行对应的流程——更新搜索词、精读分析、写笔记、存文件

两者配合形成一个循环：

```
/setup   →  首次配置：对话了解研究方向，生成所有配置文件
/feed    →  发现候选论文，尝试下载开放获取 PDF，能获取原文则直接完整精读
/read    →  精读一篇论文，生成结构化笔记，存入数据目录
/discuss →  围绕已读论文深入讨论，讨论内容自动记录到笔记
/recap   →  全局视图：读了什么、还缺什么、下一步读哪里；归档活跃阅读区，生成阶段研究版图摘要
/update  →  研究方向有变化时，同步更新搜索词和记忆
/sync    →  检查所有文档逻辑一致性，自动修复发现的问题
```

Claude 会记住你的研究背景（存在 `memory/MEMORY.md`），每次 `/feed` 都基于你已读的论文动态调整推荐方向。笔记按日期归档，和 PDF 放在一起，存入你指定的数据目录。

---

## 包含什么

| 文件 | 说明 |
|------|------|
| `recommend.py` | 三层论文推荐，从 Semantic Scholar 搜索 |
| `lookup_paper.py` | 查询论文元数据（引用数、期刊、作者 h-index） |
| `rename_pdfs.py` | 自动重命名 PDF（pdfinfo + CrossRef） |
| `config.json` | 路径和 API key 配置 |
| `search_config.json` | 搜索词配置，由 Claude 动态更新 |
| `commands/` | `/feed` `/read` `/discuss` `/recap` `/update` `/sync` `/setup` 技能文件 |
| `memory/MEMORY.md` | Claude 的持久记忆（自动维护） |
| `install.sh` | 一键安装脚本 |
| `notes/WORKFLOW.md` | 工作流说明（`/setup` 自动部署到数据目录） |
| `notes/reading_list.md` | 阅读追踪列表（`/setup` 自动部署到数据目录） |

---

## 目录结构说明

脚本文件和笔记/PDF 放在不同的文件夹里：

```
ArticleFeed/          ← 下载本项目后得到的文件夹，放在你习惯的位置，如桌面
  config.json         ← 唯一需要你编辑的文件，填入数据目录路径

你的数据目录/         ← data_dir，PDF 放这里，笔记自动存入 notes/ 子目录
  notes/
```

---

## 配置步骤

### 第零步：安装依赖

**Claude Code**（若尚未安装）：参考 [官方文档](https://docs.anthropic.com/claude-code)。

**poppler**（PDF 工具库，提供 `pdftotext`）：

```bash
# Mac
brew install poppler

# Windows（需先安装 Chocolatey）
choco install poppler

# Linux (Debian/Ubuntu)
sudo apt install poppler-utils
```

Python 仅使用标准库，无需额外安装。

### 第一步：填写路径
编辑 `config.json`，填入你的研究数据文件夹路径（PDF 放这里，笔记自动存入其中的 `notes/` 子目录）：

```json
{
  "data_dir": "你的研究数据文件夹路径",
  "s2_api_key": "你的 Semantic Scholar API key（可选，免费申请）"
}
```

**如何获取路径：**

- **Mac**：在 Finder 中找到目标文件夹，右键 → 按住 Option 键 → 点击「拷贝"xxx"的路径名」，粘贴即可。或者直接把文件夹拖入终端窗口，会自动显示路径。
- **Windows**：在文件资源管理器中打开目标文件夹，点击地址栏，复制显示的路径。或按住 Shift 右键文件夹 → 「复制为路径」。
- **Linux**：在终端中进入目标文件夹，运行 `pwd` 即可。

路径格式示例：
```
Mac/Linux:  /Users/yourname/Documents/Notes
Windows:    C:\Users\yourname\Documents\Notes
```

**不填 API key 也能正常使用**，Semantic Scholar 免费层无需注册。有 key 时速率限制更宽松，搜索更快；没有 key 时遇到限速会自动重试，不影响结果。

如需申请：https://www.semanticscholar.org/product/api

### 第二步：运行安装脚本

打开终端，进入 ArticleFeed 目录，运行安装脚本：

```bash
cd /path/to/ArticleFeed   # 将路径替换为实际位置，Mac 上可把文件夹直接拖入终端窗口自动填入路径
bash install.sh
```

脚本会自动完成：
- 在 `.claude/` 下创建 `commands` 软链接，指向根目录的 `commands/`（Claude Code 通过此链接识别技能命令）
- 创建 `memory/` 软链接，指向 Claude 的记忆目录（可直接在项目里浏览和编辑）
- 复制权限配置（写文件、建文件夹、下载 PDF 等操作不再弹出确认）

之后对 `commands/` 和 `memory/` 的任何修改都会实时生效，无需重复操作。

### 第三步：运行 `/setup`，让 Claude 帮你完成剩余配置
在 ArticleFeed 目录打开 Claude Code：

```bash
claude
```

输入 `/setup`，Claude 会通过对话了解你的研究方向，自动生成：
- `memory/MEMORY.md`（研究背景）
- `search_config.json`（初始搜索词）
- `data_dir/notes/reading_list.md`（阅读列表，含适合你领域的分类）

**不需要手动编辑这些文件。**

---

## 日常使用

| 操作 | 方式 |
|------|------|
| 首次配置 | `/setup` — 通过对话生成所有配置 |
| 获取今日推荐论文 | `/feed` — 自动更新搜索词并推荐，能获取原文则直接完整精读 |
| 精读分析一篇论文 | `/read` — 提供 PDF 路径、DOI 或摘要 |
| 围绕一篇论文深入讨论 | `/discuss 关键词` — 如作者姓、年份或标题词，自动记录有价值的讨论内容到笔记 |
| 研究方向有变化 | `/update` — 告诉 Claude 变化内容，同步更新配置和搜索词 |
| 新增命令后检查文档 | `/sync` — 自动检查所有文档一致性，修复遗漏和冲突 |
| 查看阅读进度和框架空缺 | `/recap` — 已读概览、理论框架完整度、下一步建议；归档活跃阅读区，生成阶段研究版图摘要 |
| 重命名新下载的 PDF | 在 ArticleFeed 目录下运行 `python rename_pdfs.py` |
| 查询论文元数据 | 在 ArticleFeed 目录下运行 `python lookup_paper.py --doi "..."` |

---

## 文件夹结构（运行后）

```
data_dir/                         ← 你在 config.json 里填的路径
  notes/                          ← 自动生成，无需手动创建
    reading_list.md
    WORKFLOW.md
    recaps/
      YYYY-MM-DD_recap.md
    YYYY-MM-DD/
      recommendations.md
      Author_Year_Keywords/
        Author_Year_Keywords.pdf
        Author_Year_Keywords.md
```

---

## 更新日志

### 2026-04-04
**`/recap` 新增长记忆压缩机制**
- `reading_list.md` 拆为两个区：`## 近期活跃阅读`（/read 写入）和 `## 历史归档`（/recap 归档）
- `/recap` 执行后会将活跃区整体移入归档区，并生成**阶段研究版图摘要**，保存至 `recaps/YYYY-MM-DD_recap.md`
- `/feed` 改为读取最新 recap 摘要代替逐条翻阅归档区，提升长期使用时的上下文效率

**同步规则调整**
- `search_config.json` 的 `based_on_notes` 和 `MEMORY.md` 的 `Reading Progress` 改为只追加、不删除旧条目（原为滑动窗口）
- `search_config.json` 的 `update_reason` 字段仅由 `/feed` 更新检索词时写入，`/read` 不再触碰该字段
