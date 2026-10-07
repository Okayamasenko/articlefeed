# /feed — 论文推荐

根据研究方向和阅读记录推荐论文，能拿到原文的直接精读。全程不向用户确认，完成后汇报。

## 读取

`data_dir` 从 `config.json` 读取。需要读取：
- `data_dir/notes/reading_list.md` 的 `## 近期活跃阅读`
- `memory/MEMORY.md` 的研究设计部分（跳过 Reading Progress）
- 项目根目录的 `interest_profile.json`（全部字段）
- `data_dir/notes/recaps/` 下最新一份 recap（如果有）

## 更新搜索词

根据研究方向和 `known_gaps` 更新 `search_config.json` 的三层搜索词：
- Tier 1：与核心研究问题直接相关
- Tier 2：相同机制或方法，不同研究场域
- Tier 3：跨领域灵感，偏技术侧

同时更新 `last_updated`；把本次参考的笔记文件名追加到 `based_on_notes`（不删除旧条目）；在 `update_reason` 里用 2–4 句话说明更新依据。

## 拉取候选

三个脚本互相独立，并行运行，各自把 JSON 输出到一个临时文件，然后合并：

```bash
python recommend.py --json > kw.json          # 关键词搜索
python fetch_s2_recs.py > s2recs.json         # 种子论文的相似推荐
python fetch_citations.py > citations.json    # 种子论文共同引用的基础文献
python dedup_candidates.py kw.json s2recs.json citations.json
```

`dedup_candidates.py` 已自动排除已读论文、种子论文和命中 `do_not_recommend` 的论文，并标记 ★（多源命中）、`[顶刊]`、`[追踪作者]`。

## 挑选

Tier 1、2、3 各选一篇。Tier 1 优先选能填补 `known_gaps` 的论文。关键词搜索的结果自带层级标签，其他来源由你判断归入哪一层。

- 相关性相近时，优先选带 ★、`[顶刊]`、`[追踪作者]` 的论文
- 某一层没有合适的论文就不凑数，可以从其他层补一篇，并在推荐文件里注明
- 质量优先于三层结构，不增加推荐数量

## 获取原文并精读

- **有开放获取 PDF**：下载到 `data_dir/notes/YYYY-MM-DD/Name/Name.pdf`，然后按 `/read` 的规则精读，并同步阅读记录
- **没有开放获取 PDF**：只记录获取方式（DOI 链接或 arXiv ID）

## 更新 interest_profile.json

精读可能已经改过这个文件，所以先重新读取，再一次性写入本次会话的更新：
- 新精读的论文是否应成为种子论文：上限 8 篇，满了就退役最早加入、且与当前研究阶段最远的一篇
- 被本次论文填补的 `known_gaps`：删除
- 值得追踪的新作者：加入 `known_authors`
- 整类都不相关的候选：加入 `do_not_recommend`，写成英文短关键词（如 `"medical imaging"`），脚本才能自动过滤

## 推荐文件

写入 `data_dir/notes/YYYY-MM-DD/recommendations.md`：

```markdown
# 推荐论文 YYYY-MM-DD

## Tier 1 · 核心
**论文标题**
作者 (年份) | 期刊 | 引用数
来源：关键词搜索 + S2推荐  [顶刊]
推荐理由：……
状态：✓ 已下载并精读 / 📥 获取方式：[DOI 链接](...)

## Tier 2 · 邻域
……

## Tier 3 · 交叉学科
……
```

## 汇报

告诉用户哪几篇已经精读完毕，哪几篇需要手动获取，并附上 DOI 链接。
