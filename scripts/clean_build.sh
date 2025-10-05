#!/usr/bin/env bash
#
# 清理所有构建产物
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 切换到项目根目录
cd "$(dirname "$0")/.."

log_info "清理构建产物..."

# 清理 PyInstaller 产物
if [[ -d build ]]; then
    rm -rf build/
    log_info "✓ 已删除 build/"
fi

if [[ -d dist ]]; then
    rm -rf dist/
    log_info "✓ 已删除 dist/"
fi

if [[ -f easyproxy.spec ]]; then
    rm -f easyproxy.spec
    log_info "✓ 已删除 easyproxy.spec"
fi

# 清理 Python 缓存
if [[ -d __pycache__ ]] || find . -type d -name "__pycache__" 2>/dev/null | grep -q .; then
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    log_info "✓ 已删除 __pycache__"
fi

if find . -type f -name "*.pyc" 2>/dev/null | grep -q .; then
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    log_info "✓ 已删除 *.pyc"
fi

if find . -type f -name "*.pyo" 2>/dev/null | grep -q .; then
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    log_info "✓ 已删除 *.pyo"
fi

# 清理 egg-info
if [[ -d easyproxy.egg-info ]]; then
    rm -rf easyproxy.egg-info
    log_info "✓ 已删除 easyproxy.egg-info"
fi

log_info "清理完成! 项目目录已恢复干净。"
