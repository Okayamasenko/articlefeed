# /feed — 论文推荐

执行以下步骤，不需要用户确认中间过程，完成后汇报结果。

## 步骤

### 1. 读取当前阅读状态

读取 `config.json` 获取 `data_dir`（`notes_dir` = `data_dir/notes`），然后读取以下文件：

**必读：**
- `data_dir/notes/reading_list.md` 的 `## 近期活跃阅读` 区块
- `memory/MEMORY.md`（研究设计/变量/方法论；**跳过 Reading Progress 区块**，该区块已由 interest_profile 覆盖）
- `ArticleFeed/interest_profile.json`（全部字段：active_seed_papers / known_gaps / known_authors / do_not_recommend）

**若存在则读：**
- `data_dir/notes/recaps/` 下最新一份 `YYYY-MM-DD_recap.md`

### 2. 更新 search_config.json

基于 MEMORY.md 研究方向 + `interest_profile.known_gaps`（缺什么就往 tier1/tier2 加对应词）更新三层搜索词，同时更新：
- `last_updated`：今天日期
- `based_on_notes`：追加本次参考的笔记文件名（不删旧条目）
- `update_reason`：2-4 句说明本次更新依据

搜索词原则：
- Tier 1：核心研究问题直接相关的关键词
- Tier 2：相同机制或方法，不同研究场域
- Tier 3：野卡，跨领域灵感，技术侧为主

### 3. 并行运行三个搜索脚本

三个脚本互相独立，可同时运行：

```bash
python recommend.py --json > /tmp/candidates_kw.json
python fetch_s2_recs.py > /tmp/candidates_s2recs.json
python fetch_citations.py > /tmp/candidates_citations.json
```

- `recommend.py --json`：关键词搜索（基于 search_config.json）
- `fetch_s2_recs.py`：S2 ML 推荐（基于 interest_profile.active_seed_papers）
- `fetch_citations.py`：引用交集分析（基于种子论文的参考文献，被多篇共同引用的基础文献）

### 4. 合并去重

```bash
python dedup_candidates.py \
  /tmp/candidates_kw.json \
  /tmp/candidates_s2recs.json \
  /tmp/candidates_citations.json
```

读取格式化输出。★ 标注的论文为多源命中（强信号），优先考虑。

### 5. 遴选，优先三层各一篇

从合并列表中分配：

- **Tier 1 直接相关**：与论文研究问题直接对应，优先选能填 `interest_profile.known_gaps` 的
- **Tier 2 大领域相关**：相同偏见机制或评估方法，不同研究场域
- **Tier 3 交叉学科**：跨领域灵感，技术侧或社会科学侧均可

keyword 搜索结果自带 tier 标签可参考，S2 推荐和引用交集的由 Claude 判断归哪层。

**边界情况**：若本次候选中某一层确实没有合适论文，不强行凑数，可从其他层补选一篇，在 recommendations.md 里注明。质量优先，三层结构其次。

### 6. 对每篇选中的论文：尝试获取 PDF

**如果有开放获取 URL：**
1. 生成规范文件名 `Author_Year_Keywords.pdf`，下载：
   ```bash
   curl -L -o "{data_dir}/Author_Year_Keywords.pdf" "PDF_URL"
   ```
2. 执行完整精读（步骤与 `/read` 完全一致，包括四节笔记）：
   - `pdftotext "PDF路径" -` 提取全文
   - `python lookup_paper.py --doi "DOI"` 获取元数据
   - 生成四节笔记（一、论文权重 / 二、论文亮点 / 三、可借鉴之处 / 四、如何用到论文里）
   - 建文件夹 `notes/YYYY-MM-DD/PaperName/`，存 PDF 和 MD

3. 同步三处（自动执行，不提醒）：
   - `reading_list.md` 的 `## 近期活跃阅读`：添加 `[x]` 条目，附相对链接
   - `search_config.json` `based_on_notes`：追加笔记文件名（不删旧条目）
   - `MEMORY.md` `Reading Progress`：追加一行（不删旧条目）

4. **执行 /read 的 interest_profile 更新步骤**（见 read.md Step 8）

**如果没有开放获取 PDF：**
注明获取方式（DOI 链接 / arXiv ID）。

### 7. 会话级更新 interest_profile.json

**先重新读取 `interest_profile.json` 当前状态**（步骤 6 的精读可能已修改过），再做本次会话的整体更新：

- 精读的论文够不够格成为新 seed？若是，加入 `active_seed_papers`
- `known_gaps` 有没有被这次找到的论文填掉？有则移除
- 有没有值得追踪的新作者？加入 `known_authors`
- 这次候选里有没有整类都不相关的？加入 `do_not_recommend`
- **active_seed_papers 上限为 8 篇**：超出时退役最早加入且与当前研究阶段最远的一篇

一次写入，不分步。

### 8. 写入推荐文件

将筛选结果写入 `data_dir/notes/YYYY-MM-DD/recommendations.md`（文件夹不存在则新建）。

格式：
```markdown
# 推荐论文 YYYY-MM-DD

## Tier 1 · 核心
**[论文标题]**
作者 (年份) | 期刊 | 引用数
来源：关键词搜索 + S2推荐
推荐理由：……
状态：✓ 已下载并精读 / 📥 获取方式：[DOI链接](...)

## Tier 2 · 邻域
……

## Tier 3 · 交叉学科
……
```

### 9. 汇报
告诉用户：哪几篇已直接精读完毕，哪几篇需要手动获取（附 DOI 链接）。
