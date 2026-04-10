#!/bin/bash
# ArticleFeed 一键安装
set -e

echo "ArticleFeed 安装中..."
echo ""

# 1. 创建 .claude/ 目录
mkdir -p ".claude"

# 2. .claude/commands 软链接（指向根目录的 commands/，可直接浏览和编辑）
if [ -L ".claude/commands" ] || [ -d ".claude/commands" ]; then
  echo "  .claude/commands 已就绪"
else
  ln -s "../commands" ".claude/commands"
  echo "  ✓ 创建 .claude/commands 软链接"
fi

# 3. memory 软链接（路径根据当前目录自动推算）
PROJECT_PATH=$(pwd)
ENCODED_PATH=$(echo "$PROJECT_PATH" | sed 's|/|-|g')
MEMORY_DIR="$HOME/.claude/projects/$ENCODED_PATH/memory"
mkdir -p "$MEMORY_DIR"

if [ -L "memory" ]; then
  echo "  memory 软链接已就绪"
else
  # 如果 memory/ 是真实目录（首次安装时 template 自带），先把模板文件复制过去再替换为软链接
  if [ -d "memory" ]; then
    cp -n memory/* "$MEMORY_DIR/" 2>/dev/null || true
    rm -rf "memory"
  fi
  ln -s "$MEMORY_DIR" "memory"
  echo "  ✓ 创建 memory 软链接"
fi

# 4. 权限配置（不覆盖已有文件）
if [ -f ".claude/settings.local.json" ]; then
  echo "  .claude/settings.local.json 已就绪"
else
  cp "settings.local.json" ".claude/settings.local.json"
  echo "  ✓ 复制 settings.local.json"
fi

echo ""
echo "完成！接下来："
echo "  1. 编辑 config.json，填入你的 data_dir 路径"
echo "  2. 在此目录打开 Claude Code，输入 /setup 开始配置"
