# /sync — 文档一致性检查

对 template 中所有文档文件做全面审查，确保逻辑前后一致。适合在批量改动后手动触发。

## 步骤

### 1. 读取所有文档
依次读取以下文件：
- `commands/` 下所有 `.md` 文件（每个命令的完整逻辑）
- `README.md`（命令列表、使用说明）
- `CLAUDE.md`（命令表格、核心规则）
- `SKILL.md`（OpenClaw 发布描述，含命令列表）
- `notes/WORKFLOW.md`（命令速查表）
- `memory/MEMORY.md`（自动同步规则）

### 2. 执行四项检查

**① 命令覆盖检查**
列出 `commands/` 下所有命令，逐一确认它们是否出现在：
- README.md 的命令循环图 ✓/✗
- README.md 的"包含什么"表格 ✓/✗
- README.md 的"日常使用"表格 ✓/✗
- CLAUDE.md 的可用命令表格 ✓/✗
- SKILL.md 的命令列表表格 ✓/✗
- WORKFLOW.md 的命令速查表 ✓/✗

**② 路径约定一致性**
检查所有命令中对以下路径的引用是否统一：
- `data_dir` 的读取方式（始终从 `config.json` 读取）
- `notes_dir = data_dir/notes` 的推导方式
- 笔记文件路径格式（`notes/YYYY-MM-DD/PaperName/PaperName.md`）

**③ 自动同步规则一致性**
`/read` 完成后需要同步三个地方（reading_list.md 的近期活跃阅读区 / search_config.json 的 based_on_notes / MEMORY.md Reading Progress）。
检查 `read.md`、`MEMORY.md` 的 Auto-sync Rules 以及 `CLAUDE.md` 的精读同步规则是否三处一致，包括：
- reading_list.md 写入 `## 近期活跃阅读` 区块（不是任意分类）
- based_on_notes 追加不删除（无滑动窗口截断）
- Reading Progress 追加不删除（无滑动窗口截断）
- `/read` 不修改 `update_reason`（仅 `/feed` 写入）
- `/recap` 负责将活跃区移入归档区并生成阶段摘要

**④ 逻辑冲突检查**
检查各命令之间是否存在矛盾描述（如同一字段的命名、同一文件的写入格式等）。

### 3. 修复所有发现的问题
不需要询问用户确认，直接修复。每处修复记录一行。

### 4. 汇报
输出检查结果：
```
✓ 无问题 / 已修复 N 处：
  - [文件名]：[修复内容]
  - ...
```
