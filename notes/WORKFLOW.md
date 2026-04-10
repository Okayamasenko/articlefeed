# 论文分析工作流

本文件夹中的每一份 `.md` 笔记都是由 **Claude Code** 读取原文 PDF 后生成的分析报告。

---

## 如何给 Claude 一篇文章

打开 Claude Code，使用以下命令：

| 命令 | 功能 |
|------|------|
| `/read` | 精读一篇论文，生成结构化笔记 |
| `/discuss 关键词` | 围绕已读论文讨论，自动记录要点到笔记 |
| `/feed` | 推荐新论文，尝试下载开放获取 PDF，能获取原文则直接完整精读 |
| `/recap` | 查看阅读进度和理论框架完整度；将近期活跃阅读归档，生成阶段研究版图摘要 |
| `/update` | 研究方向变化时同步更新配置 |
| `/sync` | 检查所有文档逻辑一致性，自动修复 |
| `/setup` | 首次配置：通过对话生成研究背景和搜索词 |

---

## 提交论文的方式

输入 `/read`，然后用以下任意一种方式提交：

### 方式一：本地 PDF（推荐）
告诉我路径：
```
文件在 /Users/yourname/Downloads/paper.pdf
```

### 方式二：DOI 或期刊链接
```
https://doi.org/10.xxxx/xxxxx
```
开放获取的文章 Claude 可以直接抓内容；付费墙文章需要你另外下载 PDF。

### 方式三：摘要 + 基本信息
直接粘贴摘要，同时告诉我期刊名和年份。

---

## Claude 输出的内容

每篇论文分析包含四个部分：

| 部分 | 内容 |
|------|------|
| **一、论文权重** | 期刊排名（SSCI/AHCI/IF）、引用数、作者学术背景（h-index、机构、研究方向） |
| **二、论文亮点** | 方法创新 / 对系统问题的批判 / 研究对象的重要性 |
| **三、可借鉴之处** | 理论框架、方法细节、概念工具 |
| **四、如何用到你的论文里** | 文献综述定位、引用句式建议、方法论先例、研究动机 |

分析语言：**中文为主，关键引用句式保留英文原文**。

---

## 笔记存放位置

所有内容按日期归档，每天一个文件夹；`/recap` 快照单独存放：

```
notes/
  YYYY-MM-DD/
    recommendations.md              ← 当天推荐列表
    Author_Year_Keywords/           ← 每篇论文（PDF + 笔记）
      Author_Year_Keywords.pdf
      Author_Year_Keywords.md
  recaps/
    YYYY-MM-DD_recap.md             ← /recap 生成的阅读进度快照
```

---

## 论文推荐系统（自动 Feed）

输入 `/feed`，Claude 会自动更新搜索词并推荐论文。能获取到开放获取 PDF 的论文，会直接按 `/read` 标准完整精读并生成笔记；无法获取的，结果写入当天的 `recommendations.md` 并附获取方式。

---

## PDF 自动重命名

新 PDF 下载后，放入 `data_dir` 目录，然后运行：

```bash
python rename_pdfs.py
python rename_pdfs.py --dry-run   # 预览，不实际改名
```

---

## 元数据查询工具

```bash
python lookup_paper.py --doi "10.xxxx/xxxxx"
python lookup_paper.py --title "论文标题关键词"
```

---

## 阅读进度快照与长记忆管理

运行 `/recap` 生成当前框架完整度分析，自动保存至 `notes/recaps/YYYY-MM-DD_recap.md`。

`/recap` 同时承担「长记忆压缩」职责：
- 将 `reading_list.md` 中「近期活跃阅读」区块的论文移入「历史归档」区块
- 生成阶段研究版图摘要（已确立的理论框架 / 方法论取向 / 知识缺口）
- 下次 `/feed` 时，Claude 读取最新 recap 摘要获取历史脉络，无需逐条翻阅归档区

**建议节奏**：每读完 5-10 篇，或感觉需要整理思路时，运行一次 `/recap`。
