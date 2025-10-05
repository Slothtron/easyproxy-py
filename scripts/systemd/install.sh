#!/usr/bin/env bash
#
# EasyProxy systemd 服务安装脚本
# 用法: sudo ./install.sh
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否以 root 运行
if [[ $EUID -ne 0 ]]; then
   log_error "此脚本必须以 root 权限运行"
   echo "请使用: sudo $0"
   exit 1
fi

# 检查 systemd 是否可用
if ! command -v systemctl &> /dev/null; then
    log_error "systemd 不可用,请使用其他守护进程方案"
    exit 1
fi

log_info "开始安装 EasyProxy systemd 服务..."

# 1. 创建专用用户和组
if ! id -u easyproxy &> /dev/null; then
    log_info "创建 easyproxy 用户和组..."
    useradd --system --no-create-home --shell /usr/sbin/nologin easyproxy
else
    log_info "用户 easyproxy 已存在,跳过创建"
fi

# 2. 创建必要的目录
log_info "创建目录结构..."

mkdir -p /etc/easyproxy
mkdir -p /var/log/easyproxy
mkdir -p /opt/easyproxy

# 设置目录权限
chown -R easyproxy:easyproxy /etc/easyproxy
chown -R easyproxy:easyproxy /var/log/easyproxy
chown -R easyproxy:easyproxy /opt/easyproxy

chmod 755 /etc/easyproxy
chmod 755 /var/log/easyproxy
chmod 755 /opt/easyproxy

# 3. 生成默认配置文件 (如果不存在)
if [[ ! -f /etc/easyproxy/config.yaml ]]; then
    log_info "生成默认配置文件..."
    
    if command -v easyproxy &> /dev/null; then
        easyproxy init /etc/easyproxy/config.yaml
        chown easyproxy:easyproxy /etc/easyproxy/config.yaml
        chmod 640 /etc/easyproxy/config.yaml
    else
        log_warn "easyproxy 命令不可用,跳过配置文件生成"
        log_warn "请手动创建 /etc/easyproxy/config.yaml"
    fi
else
    log_info "配置文件已存在: /etc/easyproxy/config.yaml"
fi

# 4. 复制 systemd 服务文件
log_info "安装 systemd 服务文件..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/easyproxy.service"

if [[ ! -f "$SERVICE_FILE" ]]; then
    log_error "找不到服务文件: $SERVICE_FILE"
    exit 1
fi

cp "$SERVICE_FILE" /etc/systemd/system/easyproxy.service
chmod 644 /etc/systemd/system/easyproxy.service

# 5. 重载 systemd
log_info "重载 systemd 配置..."
systemctl daemon-reload

# 6. 启用服务 (开机自启)
log_info "启用 EasyProxy 服务 (开机自启)..."
systemctl enable easyproxy.service

log_info "============================================"
log_info "EasyProxy systemd 服务安装完成!"
log_info "============================================"
echo ""
log_info "配置文件: /etc/easyproxy/config.yaml"
log_info "日志目录: /var/log/easyproxy/"
echo ""
log_info "常用命令:"
echo "  启动服务:   sudo systemctl start easyproxy"
echo "  停止服务:   sudo systemctl stop easyproxy"
echo "  重启服务:   sudo systemctl restart easyproxy"
echo "  查看状态:   sudo systemctl status easyproxy"
echo "  查看日志:   sudo journalctl -u easyproxy -f"
echo "  禁用自启:   sudo systemctl disable easyproxy"
echo ""
log_warn "请先编辑配置文件,然后启动服务:"
echo "  sudo nano /etc/easyproxy/config.yaml"
echo "  sudo systemctl start easyproxy"
