# /feed — 论文推荐

执行以下步骤，不需要用户确认中间过程，完成后汇报结果。

## 步骤

### 1. 读取当前阅读状态
读取 `config.json` 获取 `data_dir`（`notes_dir` = `data_dir/notes`），再读取 `data_dir/notes/reading_list.md`，了解：
- 已读论文（`[x]`）及其主题
- 未读但已下载的论文

### 2. 更新 search_config.json
基于已读论文的主题和理论框架，更新 `search_config.json` 中的 `tiers.tier1/tier2/tier3.terms`，同时更新：
- `last_updated`：今天日期
- `based_on_notes`：已读笔记的文件名列表（滑动窗口最多 25 条，超出时删除最旧的）
- `update_reason`：简要说明本次更新的依据

搜索词原则（参考 MEMORY.md 里的研究方向）：
- Tier 1：核心研究问题直接相关的关键词
- Tier 2：相同机制或方法，不同研究场域
- Tier 3：野卡，跨领域灵感，技术侧为主

### 3. 运行 recommend.py
```bash
python recommend.py
```

### 4. 筛选推荐
从输出结果中，每层各选 1-2 篇最值得读的，判断标准：
- 与论文研究问题的直接相关性
- 引用数和期刊权重
- 是否填补现有阅读列表的空白

### 5. 对每篇推荐论文：尝试获取 PDF

**如果输出中有"开放获取 ✓"和 PDF URL：**
1. 用已有的 S2 元数据（作者、年份、标题）直接生成规范文件名 `Author_Year_Keywords.pdf`，下载到 `data_dir`：
   ```bash
   curl -L -o "{data_dir}/Author_Year_Keywords.pdf" "PDF_URL"
   ```
2. 对该论文执行完整精读，步骤与 `/read` 完全一致，不得简化：
   - **提取全文**：运行 `pdftotext "{data_dir}/Author_Year_Keywords.pdf" -` 提取 PDF 正文，作为笔记生成的内容基础
   - **查元数据**：运行 `python lookup_paper.py --doi "DOI"` 获取引用数、期刊指标、作者 h-index
   - **生成论文笔记**（四部分，语言：中文为主，关键引用句保留英文）：
     - **一、论文权重**：根据论文类型选对应分支，必须填完所有字段：
       - 期刊论文：期刊名（出版社）/ 数据库收录（SSCI/AHCI/ESCI/Scopus）/ Impact Factor / 领域排名（Q1/Q2 或百分位）/ 期刊 h-index；每位作者：机构、职级、研究方向、代表期刊、h-index（如可查）；引用数 & 年均引用；总体评价
       - 会议论文：会议全称 / CORE 排名（A*/A/B）/ 录用率（如可查）/ 领域地位；每位作者：机构、职级、研究方向、代表期刊、h-index（如可查）；引用数 & 年均引用；总体评价
       - 预印本（arXiv 等）：平台 & 分类 / 投稿状态或期刊版本（如已知）；每位作者：机构、职级、研究方向、代表期刊、h-index（如可查）；引用数；总体评价
     - **二、论文亮点**：方法创新 / 对系统问题的批判 / 研究对象的重要性
     - **三、可借鉴之处**：理论框架、方法细节、概念工具（直接标明可用于论文的哪个部分）
     - **四、如何用到你的论文里**：文献综述定位、建议引用句式（英文）、方法论先例、研究动机
   - **建文件夹**：`data_dir/notes/YYYY-MM-DD/PaperName/`
   - **存 PDF**：将下载的文件复制/移动到该文件夹，重命名为 `PaperName.pdf`
   - **存 MD**：将笔记保存为 `PaperName.md`
   - **同步三处**（自动执行，不提醒用户）：
     - `reading_list.md`：添加 `[x]` 条目，附相对链接
     - `search_config.json` `based_on_notes`：添加笔记文件名，滑动窗口最多 25 条
     - `MEMORY.md` `Reading Progress`：追加一行，滑动窗口最多 20 条
3. 在 recommendations.md 中标注：`✓ 已下载并精读`

**如果没有开放获取 PDF：**
在 recommendations.md 中注明获取方式：
- DOI 链接（`https://doi.org/...`）
- 机构图书馆数据库（如 Web of Science、Scopus）
- 如有 arXiv 版本，注明 arXiv ID

### 6. 写入推荐文件
将筛选结果写入 `data_dir/notes/YYYY-MM-DD/recommendations.md`（如文件夹不存在则新建）。

格式：
```markdown
# 推荐论文 YYYY-MM-DD

## Tier 1 · 核心
**[论文标题]**
作者 (年份) | 期刊 | 引用数
推荐理由：……
状态：✓ 已下载并精读 / 📥 获取方式：[DOI链接](...)

## Tier 2 · 邻域
……

## Tier 3 · 野卡
……
```

### 7. 汇报
告诉用户：哪几篇已经直接精读完毕，哪几篇需要手动获取（附获取链接）。
