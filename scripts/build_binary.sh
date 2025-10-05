#!/usr/bin/env bash
#
# EasyProxy 二进制打包脚本
# 使用 PyInstaller 将 Python 程序打包成独立可执行文件
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查 PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    log_warn "PyInstaller 未安装,正在安装..."
    pip install pyinstaller
fi

# 获取版本号
VERSION=$(python -c "from easyproxy import __version__; print(__version__)")
log_info "EasyProxy 版本: $VERSION"

# 清理旧的构建
log_step "清理旧的构建文件..."
rm -rf build/ dist/ *.spec

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 创建 PyInstaller 配置
log_step "创建 PyInstaller 配置..."
cat > easyproxy.spec << EOF
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['easyproxy/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'easyproxy.cli',
        'easyproxy.config',
        'easyproxy.proxy',
        'easyproxy.auth',
        'easyproxy.logger',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='easyproxy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
EOF

# 开始打包
log_step "开始打包 (这可能需要几分钟)..."
pyinstaller --clean easyproxy.spec

# 检查结果
if [[ -f dist/easyproxy ]]; then
    log_info "✓ 打包成功!"
    echo ""
    log_info "可执行文件位置: $(pwd)/dist/easyproxy"
    
    # 显示文件信息
    FILE_SIZE=$(du -h dist/easyproxy | cut -f1)
    log_info "文件大小: $FILE_SIZE"
    
    # 测试可执行文件
    log_step "测试可执行文件..."
    ./dist/easyproxy --version
    
    # 清理构建产物
    log_step "清理构建产物..."
    rm -rf build/
    rm -f easyproxy.spec
    log_info "✓ 已清理 build/ 和 easyproxy.spec"
    
    echo ""
    log_info "============================================"
    log_info "打包完成! 保留文件:"
    echo "  dist/easyproxy (可执行文件)"
    echo ""
    log_info "安装到系统:"
    echo "  sudo cp dist/easyproxy /usr/local/bin/"
    echo "  sudo chmod +x /usr/local/bin/easyproxy"
    echo ""
    log_info "或者安装到 /usr/bin (systemd 使用):"
    echo "  sudo cp dist/easyproxy /usr/bin/"
    echo "  sudo chmod +x /usr/bin/easyproxy"
    echo ""
    log_info "清理所有构建文件:"
    echo "  rm -rf dist/"
    log_info "============================================"
else
    log_error "打包失败!"
    # 清理失败的构建产物
    rm -rf build/ dist/ easyproxy.spec
    exit 1
fi
