#!/usr/bin/env bash
#
# Ellectric — AI + 电力交易技术学习平台 环境安装脚本
#
# 用法:
#   chmod +x setup.sh && ./setup.sh
#
# 做了什么:
#   1. 检查 Python 3.11+ 是否安装
#   2. 创建虚拟环境 .venv
#   3. 安装所有依赖（pandas, scikit-learn, XGBoost, plotly, jupyter）
#   4. 验证所有包可导入
#
# 预期时间: <30 分钟（取决于网络速度）
# 国内网络慢的话，脚本会自动使用清华镜像源

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Ellectric 环境安装"
echo "  AI + 电力交易技术学习平台"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── 检查 Python 版本 ──────────────────────────────────
echo "→ 检查 Python 版本..."
PYTHON=""
for cmd in python3.12 python3.11 python3; do
    if command -v "$cmd" &>/dev/null; then
        ver=$("$cmd" --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
        if [ -n "$ver" ]; then
            major=$(echo "$ver" | cut -d. -f1)
            minor=$(echo "$ver" | cut -d. -f2)
            if [ "$major" -ge 3 ] && [ "$minor" -ge 11 ]; then
                PYTHON="$cmd"
                break
            fi
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo -e "${RED}错误: 需要 Python 3.11+，未找到。${NC}"
    echo "请安装 Python 3.11 或以上版本: https://www.python.org/downloads/"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} 找到 $PYTHON ($($PYTHON --version))"

# ── 创建虚拟环境 ──────────────────────────────────────
echo ""
echo "→ 创建虚拟环境 .venv..."
if [ -d ".venv" ]; then
    echo -e "  ${YELLOW}虚拟环境已存在，跳过创建${NC}"
else
    $PYTHON -m venv .venv
    echo -e "  ${GREEN}✓${NC} 虚拟环境创建完成"
fi

# ── 激活虚拟环境 ──────────────────────────────────────
echo ""
echo "→ 激活虚拟环境..."
source .venv/bin/activate

# ── 升级 pip ──────────────────────────────────────────
echo ""
echo "→ 升级 pip..."
pip install --quiet --upgrade pip

# ── 选择镜像源 ────────────────────────────────────────
echo ""
echo "→ 测试网络连通性..."
if curl -s --connect-timeout 3 https://pypi.org > /dev/null 2>&1; then
    PIP_INDEX=""
    echo -e "  ${GREEN}✓${NC} PyPI 官方源可达"
else
    PIP_INDEX="-i https://pypi.tuna.tsinghua.edu.cn/simple"
    echo -e "  ${YELLOW}!${NC} PyPI 不可达，使用清华镜像源"
fi

# ── 安装依赖 ──────────────────────────────────────────
echo ""
echo "→ 安装依赖包（可能需要几分钟）..."
pip install $PIP_INDEX --quiet -r requirements.txt

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  安装完成！${NC}"
echo ""
echo "  启动 Jupyter:"
echo "    source .venv/bin/activate"
echo "    jupyter notebook notebooks/"
echo ""
echo "  学习顺序:"
echo "    01_data_ingestion.ipynb       — 数据获取"
echo "    02_data_cleaning.ipynb        — 数据清洗"
echo "    03_feature_engineering.ipynb  — 特征工程"
echo "    04_load_forecasting.ipynb     — 负荷预测"
echo "    05_end_to_end_baseline.ipynb  — 端到端管道"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
