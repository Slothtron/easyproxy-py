# EasyProxy - 多协议代理服务器

一个轻量级的代理服务器,支持HTTP/HTTPS/SOCKS5协议,基于Python asyncio实现。

## 安装

### 方式一:通过 pip 安装 (推荐)

```bash
# 从 PyPI 安装(发布后可用)
pip install easyproxy

# 从 Git 仓库安装
pip install git+https://github.com/Slothtron/easyproxy-py.git

# 安装到用户目录(无需 sudo)
pip install --user easyproxy
```

### 方式二:从源码安装

```bash
# 克隆仓库
git clone https://github.com/Slothtron/easyproxy-py.git
cd easyproxy-py

# 安装
pip install .

# 或开发模式安装(修改代码立即生效)
pip install -e .
```

### 方式三:开发环境

```bash
# 克隆仓库
git clone https://github.com/Slothtron/easyproxy-py.git
cd easyproxy-py

# 安装依赖
pip install -r requirements.txt

# 直接运行
python -m easyproxy start
```

## 快速开始

### 启动代理服务器

**使用默认配置:**

```bash
easyproxy start
```

**使用配置文件:**

```bash
# 生成默认配置文件
easyproxy init config.yaml

# 使用配置文件启动
easyproxy start -c config.yaml
```

**使用命令行参数:**

```bash
# 自定义端口和日志级别
easyproxy start -p 8080 --log-level DEBUG

# 自定义监听地址
easyproxy start -H 127.0.0.1 -p 7899

# 指定日志文件
easyproxy start -l /var/log/easyproxy/proxy.log
# 或使用长选项
easyproxy start --log-file /var/log/easyproxy/proxy.log

# 组合使用多个参数
easyproxy start -p 8080 --log-level DEBUG --log-file /var/log/easyproxy/proxy.log
```

服务器默认在 `0.0.0.0:7899` 上启动。

### 使用代理

使用curl测试HTTP:

```bash
curl -x http://127.0.0.1:7899 http://www.baidu.com
```

使用curl测试HTTPS:

```bash
curl -x http://127.0.0.1:7899 https://www.baidu.com
```

使用curl测试SOCKS5:

```bash
curl --socks5 127.0.0.1:7899 http://www.baidu.com
curl --socks5 127.0.0.1:7899 https://www.baidu.com
```

使用wget测试:

```bash
http_proxy=http://127.0.0.1:7899 wget http://www.baidu.com
https_proxy=http://127.0.0.1:7899 wget https://www.baidu.com
```

配置浏览器代理:
- 代理类型: HTTP 或 SOCKS5
- 地址: 127.0.0.1
- 端口: 7899
- 支持: HTTP、HTTPS、SOCKS5

## CLI命令

### 启动服务器

```bash
easyproxy start [OPTIONS]

选项:
  -c, --config PATH       配置文件路径
  -H, --host TEXT         监听地址 (覆盖配置文件)
  -p, --port INTEGER      监听端口 (覆盖配置文件)
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
                          日志级别 (覆盖配置文件)
  -l, --log-file PATH     日志文件路径 (覆盖配置文件)
```

### 生成配置文件

```bash
easyproxy init <output_path>
```

### 验证配置文件

```bash
easyproxy validate -c <config_path>
```

### 查看版本

```bash
easyproxy --version
```

### 查看帮助

```bash
easyproxy --help
easyproxy start --help
```

## 配置说明

配置文件使用YAML格式,支持以下选项:

```yaml
# 服务器配置
host: 0.0.0.0              # 监听地址
port: 7899                 # 监听端口

# 协议配置
protocols:
  - http                   # HTTP代理
  - https                  # HTTPS代理
  - socks5                 # SOCKS5代理

# 连接配置
max_connections: 1000      # 最大并发连接数
connection_timeout: 30     # 连接超时(秒)
idle_timeout: 300          # 空闲超时(秒)
buffer_size: 8192          # 缓冲区大小(字节)

# 日志配置
log_level: INFO            # 日志级别
access_log: true           # 是否记录访问日志
log_file: null             # 日志文件路径(null=控制台)

# 认证配置(可选)
auth:
  enabled: false           # 是否启用认证
  type: basic              # 认证类型: basic
  realm: EasyProxy         # 认证域名
  users:                   # 用户名密码映射
    admin: admin123
    user1: password1
```

### 认证功能

EasyProxy支持Basic Auth认证,可以保护代理服务器免受未授权访问:

**启用认证:**
```yaml
auth:
  enabled: true
  type: basic
  realm: MyProxy
  users:
    admin: secret123
    user1: pass456
```

**使用认证的代理:**

HTTP/HTTPS代理:
```bash
# curl格式
curl -x http://username:password@127.0.0.1:7899 http://www.baidu.com

# 环境变量格式
export http_proxy=http://username:password@127.0.0.1:7899
curl http://www.baidu.com
```

SOCKS5代理:
```bash
curl --socks5 username:password@127.0.0.1:7899 http://www.baidu.com
```

**认证特性:**
- ✅ HTTP/HTTPS使用Proxy-Authorization头认证
- ✅ SOCKS5使用RFC 1929用户名/密码认证
- ✅ 统一的用户管理(HTTP和SOCKS5共享用户列表)
- ✅ 认证失败自动拒绝连接
- ✅ 详细的认证日志记录

### 日志功能

EasyProxy使用结构化日志系统(structlog),提供以下功能:

- **结构化日志** - 每条日志都包含结构化的上下文信息
- **访问日志** - 记录每个代理请求的详细信息
- **连接统计** - 实时统计连接数、流量等信息
- **彩色输出** - 开发环境下彩色控制台输出
- **JSON格式** - 可选的JSON格式输出(便于日志分析)

**日志示例:**
```
2025-10-05 09:10:23 [info     ] new_connection                 client=192.168.1.100:54321
2025-10-05 09:10:23 [info     ] protocol_detected              protocol=http client=192.168.1.100:54321
2025-10-05 09:10:23 [info     ] connecting_to_target           target=www.baidu.com:80
2025-10-05 09:10:24 [info     ] proxy_request                  client=192.168.1.100:54321 protocol=http target=www.baidu.com:80 status=success bytes_sent=156 bytes_received=2048 duration_ms=123.45
```

## 要求

- Python 3.11+
- pydantic >= 2.6.0
- PyYAML >= 6.0.1
- click >= 8.1.0
- structlog >= 24.1.0

## 特性

- ✅ **HTTP代理** - 支持标准HTTP代理
- ✅ **HTTPS代理** - 支持CONNECT隧道(端到端加密)
- ✅ **SOCKS5代理** - 完整的SOCKS5协议支持(IPv4/IPv6/域名)
- ✅ **协议自动检测** - 自动识别HTTP/HTTPS/SOCKS5协议
- ✅ **Basic Auth认证** - 支持HTTP Proxy-Authorization和SOCKS5用户名/密码认证
- ✅ **灵活配置** - 支持YAML配置文件和命令行参数
- ✅ **结构化日志** - 使用structlog提供详细的访问日志和统计信息
- ✅ **连接统计** - 实时统计连接数、流量、错误等信息
- ✅ **异步I/O** - 高性能并发处理
- ✅ **简单易用** - 开箱即用,可选配置
- ✅ **轻量级** - 最小依赖,核心功能使用Python标准库

## 守护进程部署

EasyProxy 支持在 Linux 系统上作为后台守护进程运行,提供两种部署方案:

### 🥇 systemd (推荐)

适用于现代 Linux 发行版 (Ubuntu 16.04+, CentOS 7+, Debian 8+):

```bash
# 快速安装
cd scripts/systemd
sudo ./install.sh

# 启动服务
sudo systemctl start easyproxy

# 查看状态
sudo systemctl status easyproxy

# 查看日志
sudo journalctl -u easyproxy -f
```

**特点:**
- ✅ 系统原生支持,零依赖
- ✅ 开机自启,崩溃自动重启
- ✅ 完善的日志管理和安全隔离
- ✅ 最佳性能和稳定性

### 🥈 Docker (容器化)

适用于容器化部署场景:

```bash
# 使用 Docker Compose
cd scripts/docker
cp ../../config/config.example.yaml config.yaml
docker-compose up -d

# 查看日志
docker-compose logs -f
```

**特点:**
- ✅ 完全隔离,环境一致
- ✅ 易于部署和扩展
- ✅ 内置健康检查和日志轮转

### 📖 详细文档

查看完整的守护进程部署指南: [docs/DAEMON.md](docs/DAEMON.md)

包含:
- 详细的安装步骤和配置说明
- 常用命令和管理操作
- 性能优化和安全加固
- 故障排查和监控集成

## 架构

基于Python asyncio的事件驱动架构,详见 [docs/architecture.md](docs/architecture.md)。

## 许可

MIT License
