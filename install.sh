#!/bin/bash
# ArticleFeed 一键安装
# 创建 commands 和 memory 软链接，复制权限配置

set -e

echo "ArticleFeed 安装中..."
echo ""

# 1. commands 软链接（相对路径，指向 .claude/commands/）
if [ -L "commands" ]; then
  echo "  commands 软链接已就绪"
else
  ln -s ".claude/commands" "commands"
  echo "  ✓ 创建 commands 软链接"
fi

# 2. memory 软链接（路径根据当前目录自动推算）
PROJECT_PATH=$(pwd)
ENCODED_PATH=$(echo "$PROJECT_PATH" | sed 's|/|-|g')
MEMORY_DIR="$HOME/.claude/projects/$ENCODED_PATH/memory"
mkdir -p "$MEMORY_DIR"

if [ -L "memory" ]; then
  echo "  memory 软链接已就绪"
else
  ln -s "$MEMORY_DIR" "memory"
  echo "  ✓ 创建 memory 软链接 → $MEMORY_DIR"
fi

# 3. 权限配置（不覆盖已有文件）
if [ -f ".claude/settings.local.json" ]; then
  echo "  .claude/settings.local.json 已就绪"
else
  cp "template/settings.local.json" ".claude/settings.local.json"
  echo "  ✓ 复制 settings.local.json"
fi

# 4. 配置文件（不覆盖已有文件）
for f in config.json search_config.json interest_profile.json; do
  if [ -f "$f" ]; then
    echo "  $f 已就绪"
  else
    cp "template/$f" "$f"
    echo "  ✓ 复制 $f（请编辑 config.json 填写 data_dir）"
  fi
done

echo ""
echo "完成！编辑 config.json 填写数据目录路径，然后在此目录打开 Claude Code，输入 /setup 开始配置。"
