#!/usr/bin/env bash
#
# EasyProxy systemd 服务卸载脚本
# 用法: sudo ./uninstall.sh
#

set -e

# 颜色定义
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

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 root 权限
if [[ $EUID -ne 0 ]]; then
   log_error "此脚本必须以 root 权限运行"
   echo "请使用: sudo $0"
   exit 1
fi

log_info "开始卸载 EasyProxy systemd 服务..."

# 1. 停止服务
if systemctl is-active --quiet easyproxy.service; then
    log_info "停止 EasyProxy 服务..."
    systemctl stop easyproxy.service
fi

# 2. 禁用服务
if systemctl is-enabled --quiet easyproxy.service; then
    log_info "禁用 EasyProxy 服务..."
    systemctl disable easyproxy.service
fi

# 3. 删除服务文件
if [[ -f /etc/systemd/system/easyproxy.service ]]; then
    log_info "删除服务文件..."
    rm -f /etc/systemd/system/easyproxy.service
fi

# 4. 重载 systemd
log_info "重载 systemd 配置..."
systemctl daemon-reload
systemctl reset-failed

log_info "============================================"
log_info "EasyProxy systemd 服务已卸载"
log_info "============================================"
echo ""
log_warn "以下文件和目录未被删除,如需清理请手动删除:"
echo "  配置目录: /etc/easyproxy/"
echo "  日志目录: /var/log/easyproxy/"
echo "  工作目录: /opt/easyproxy/"
echo "  系统用户: easyproxy"
echo ""
log_info "如需完全清理,请执行:"
echo "  sudo rm -rf /etc/easyproxy"
echo "  sudo rm -rf /var/log/easyproxy"
echo "  sudo rm -rf /opt/easyproxy"
echo "  sudo userdel easyproxy"
