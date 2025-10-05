# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-10-05

### Added
- **守护进程支持**: 添加了完整的 Linux 守护进程部署方案
  - systemd 服务配置和自动安装脚本
  - Docker 容器化部署支持
  - 完整的部署文档 (`docs/DAEMON.md`)
- **日志文件参数**: 新增 `-l, --log-file` CLI 参数
  - 支持通过命令行指定日志文件路径
  - 可覆盖配置文件中的日志设置
  - 集成到 systemd 和 Docker 配置中
- **文档完善**:
  - 新增守护进程部署指南 (`docs/DAEMON.md`)
  - 更新 README 添加守护进程章节
  - 添加 Docker 部署详细文档
  - 创建 CHANGELOG 文件

### Changed
- **CLI 参数命名统一**: 将 `--logfile` 统一为 `--log-file`,与 `--log-level` 保持一致
- **守护进程日志策略**: 
  - systemd: 同时输出到 journal 和文件
  - Docker: 同时输出到容器日志和文件

### Improved
- **安全加固**: systemd 服务配置添加了完整的安全隔离选项
- **性能优化**: 配置了文件描述符限制,支持大量并发连接
- **文档质量**: 所有文档使用中文,更加详细和易读

## [0.1.0] - 2025-10-04

### Added
- 初始版本发布
- 支持 HTTP/HTTPS/SOCKS5 代理协议
- 协议自动检测功能
- Basic Auth 认证支持
- 结构化日志系统 (structlog)
- 灵活的配置系统 (YAML + 命令行参数)
- CLI 命令行工具
- 完整的项目文档

### Features
- ✅ HTTP 代理 - 标准 HTTP 代理支持
- ✅ HTTPS 代理 - CONNECT 隧道支持
- ✅ SOCKS5 代理 - 完整的 SOCKS5 协议实现
- ✅ 协议自动检测 - 自动识别客户端协议
- ✅ Basic Auth 认证 - HTTP 和 SOCKS5 统一认证
- ✅ 异步 I/O - 基于 asyncio 的高性能实现
- ✅ 配置灵活 - 支持 YAML 配置文件和命令行参数
- ✅ 日志完善 - 结构化日志和访问日志

---

## Version History

- **0.2.0** (2025-10-05) - 守护进程支持和日志增强
- **0.1.0** (2025-10-04) - 初始版本发布

---

## Upgrade Guide

### 从 0.1.0 升级到 0.2.0

**无破坏性变更** - 完全向后兼容

**新功能:**
1. 可以使用 `-l, --log-file` 参数指定日志文件
2. 可以使用 systemd 或 Docker 部署为守护进程

**升级步骤:**
```bash
# 1. 更新代码
git pull origin main

# 2. 重新安装
pip install --upgrade .

# 3. 验证版本
easyproxy --version  # 应显示 0.2.0

# 4. (可选) 部署为守护进程
cd scripts/systemd
sudo ./install.sh
```

**注意事项:**
- 如果之前使用了 `--logfile` 参数,请改为 `--log-file`
- 配置文件格式无变化,无需修改
- 所有现有功能保持不变

---

## Links

- [GitHub Repository](https://github.com/Slothtron/easyproxy-py)
- [Documentation](https://github.com/Slothtron/easyproxy-py#readme)
- [Issues](https://github.com/Slothtron/easyproxy-py/issues)
