# EasyProxy 守护进程部署指南

本文档介绍如何在 Linux 系统上将 EasyProxy 配置为后台守护进程运行。

---

## 📋 方案选择

EasyProxy 提供两种守护进程方案,请根据你的环境选择:

| 方案 | 适用场景 | 推荐指数 |
|------|----------|----------|
| **systemd** | 现代 Linux 发行版 (Ubuntu 16.04+, CentOS 7+, Debian 8+) | ⭐⭐⭐⭐⭐ |
| **Docker** | 容器化部署,需要隔离和可移植性 | ⭐⭐⭐⭐⭐ |

**快速判断:**
- ✅ 如果你的系统有 systemd → 使用 **systemd** 方案
- ✅ 如果你使用容器化部署 → 使用 **Docker** 方案

**检查你的系统:**
```bash
# 检查是否有 systemd
systemctl --version

# 检查是否有 Docker
docker --version
```

---

## 🥇 方案一: systemd (推荐)

### 特点

- ✅ 系统原生支持,零依赖
- ✅ 开机自启,崩溃自动重启
- ✅ 完善的日志管理 (journald)
- ✅ 强大的安全隔离和资源控制
- ✅ 最佳性能和稳定性

### 快速安装

```bash
# 1. 进入 systemd 脚本目录
cd scripts/systemd

# 2. 运行安装脚本 (需要 root 权限)
sudo ./install.sh

# 3. 编辑配置文件 (根据需要)
sudo nano /etc/easyproxy/config.yaml

# 4. 启动服务
sudo systemctl start easyproxy
```

**日志说明:**
- 日志同时输出到 systemd journal 和文件 `/var/log/easyproxy/easyproxy.log`
- 查看 journal 日志: `sudo journalctl -u easyproxy -f`
- 查看文件日志: `sudo tail -f /var/log/easyproxy/easyproxy.log`

### 常用命令

```bash
# 启动服务
sudo systemctl start easyproxy

# 停止服务
sudo systemctl stop easyproxy

# 重启服务
sudo systemctl restart easyproxy

# 查看状态
sudo systemctl status easyproxy

# 查看实时日志
sudo journalctl -u easyproxy -f

# 查看最近 100 行日志
sudo journalctl -u easyproxy -n 100

# 启用开机自启
sudo systemctl enable easyproxy

# 禁用开机自启
sudo systemctl disable easyproxy

# 重载配置文件 (修改 .service 文件后)
sudo systemctl daemon-reload
```

### 配置文件位置

- **服务文件**: `/etc/systemd/system/easyproxy.service`
- **配置文件**: `/etc/easyproxy/config.yaml`
- **日志文件**: `/var/log/easyproxy/easyproxy.log`
- **日志目录**: `/var/log/easyproxy/`
- **工作目录**: `/opt/easyproxy/`

### 自定义配置

编辑服务文件:
```bash
sudo nano /etc/systemd/system/easyproxy.service
```

常见自定义:

**1. 修改监听端口**
```ini
[Service]
ExecStart=/usr/bin/easyproxy start -c /etc/easyproxy/config.yaml -p 8080 --log-file /var/log/easyproxy/easyproxy.log
```

**2. 只输出到 systemd journal (不写文件)**
```ini
[Service]
ExecStart=/usr/bin/easyproxy start -c /etc/easyproxy/config.yaml
# 移除 --log-file 参数
```

**2. 调整资源限制**
```ini
[Service]
# 限制 CPU 为 2 核
CPUQuota=200%

# 限制内存为 2GB
MemoryLimit=2G

# 限制文件描述符数量
LimitNOFILE=1048576
```

**4. 修改运行用户**
```ini
[Service]
User=myuser
Group=mygroup
```

修改后重载配置:
```bash
sudo systemctl daemon-reload
sudo systemctl restart easyproxy
```

### 卸载

```bash
cd scripts/systemd
sudo ./uninstall.sh
```

---

## 🥈 方案二: Docker (容器化)

### 特点

- ✅ 完全隔离,环境一致
- ✅ 易于部署和扩展
- ✅ 内置健康检查和日志轮转
- ✅ 支持编排 (Docker Compose / Kubernetes)
- ✅ 跨平台一致性

### 快速开始

**方式一: 使用 Docker Compose (推荐)**

```bash
# 1. 进入 Docker 脚本目录
cd scripts/docker

# 2. 准备配置文件
cp ../../config/config.example.yaml config.yaml
nano config.yaml  # 编辑配置

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f
```

**方式二: 使用 Docker 命令**

```bash
# 1. 构建镜像
docker build -f scripts/docker/Dockerfile -t easyproxy:latest .

# 2. 运行容器
docker run -d \
  --name easyproxy \
  --restart unless-stopped \
  -p 7899:7899 \
  -v $(pwd)/config/config.example.yaml:/etc/easyproxy/config.yaml:ro \
  -v $(pwd)/logs:/var/log/easyproxy \
  easyproxy:latest

# 3. 查看日志
docker logs -f easyproxy
```

### 常用命令

```bash
# Docker Compose 命令
docker-compose up -d          # 启动服务
docker-compose down           # 停止并删除容器
docker-compose restart        # 重启服务
docker-compose logs -f        # 查看日志
docker-compose ps             # 查看状态

# Docker 命令
docker start easyproxy        # 启动容器
docker stop easyproxy         # 停止容器
docker restart easyproxy      # 重启容器
docker logs -f easyproxy      # 查看日志
docker ps                     # 查看运行中的容器
docker exec -it easyproxy /bin/bash  # 进入容器
```

### 配置说明

**日志说明:**
- 日志同时输出到容器日志和文件 `/var/log/easyproxy/easyproxy.log`
- 查看容器日志: `docker logs -f easyproxy`
- 查看文件日志: `docker exec easyproxy tail -f /var/log/easyproxy/easyproxy.log`
- 或通过挂载的 `./logs` 目录访问: `tail -f ./logs/easyproxy.log`

**端口映射**

修改 `docker-compose.yml`:
```yaml
ports:
  - "8080:7899"  # 主机端口:容器端口
```

**资源限制**

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # CPU 限制
      memory: 2G       # 内存限制
```

**多实例部署**

```yaml
services:
  easyproxy-1:
    # ...
    ports:
      - "7899:7899"
  
  easyproxy-2:
    # ...
    ports:
      - "7900:7899"
```

### 详细文档

查看 [scripts/docker/README.md](../scripts/docker/README.md) 获取更多信息。

---

## 🔧 高级配置

### 1. 配置文件管理

所有方案都使用 `/etc/easyproxy/config.yaml` 作为配置文件。

**生成默认配置:**
```bash
easyproxy init /etc/easyproxy/config.yaml
```

**配置示例:**
```yaml
# 监听配置
host: 0.0.0.0
port: 7899

# 支持的协议
protocols:
  - http
  - https
  - socks5

# 日志配置
log_level: INFO

# 连接配置
max_connections: 1000
connection_timeout: 300

# 认证配置 (可选)
auth:
  enabled: false
  username: user
  password: pass
```

修改配置后重启服务:
```bash
# systemd
sudo systemctl restart easyproxy

# Docker
docker-compose restart
```

### 2. 日志管理

**systemd 日志:**
```bash
# 查看实时日志
sudo journalctl -u easyproxy -f

# 查看最近 100 行
sudo journalctl -u easyproxy -n 100

# 查看指定时间范围
sudo journalctl -u easyproxy --since "2024-01-01" --until "2024-01-02"

# 查看错误日志
sudo journalctl -u easyproxy -p err

# 导出日志
sudo journalctl -u easyproxy > easyproxy.log
```

**Docker 日志:**
```bash
# 查看实时日志
docker logs -f easyproxy

# 查看最近 100 行
docker logs --tail 100 easyproxy

# 查看指定时间范围
docker logs --since 2024-01-01T00:00:00 easyproxy
```


### 3. 性能优化

**调整文件描述符限制 (支持更多并发连接):**

**systemd:**
```ini
[Service]
LimitNOFILE=1048576
```

**Docker:**
```yaml
ulimits:
  nofile:
    soft: 65536
    hard: 65536
```

### 4. 安全加固

**systemd 安全选项 (已在服务文件中配置):**
- `NoNewPrivileges=true` - 禁止提升权限
- `PrivateTmp=true` - 私有临时目录
- `ProtectSystem=strict` - 保护系统目录
- `ProtectHome=true` - 保护 home 目录
- `CapabilityBoundingSet=CAP_NET_BIND_SERVICE` - 最小权限

**防火墙配置:**
```bash
# 允许代理端口
sudo ufw allow 7899/tcp

# 限制访问来源
sudo ufw allow from 192.168.1.0/24 to any port 7899
```

### 5. 监控和告警

**检查服务状态:**

**systemd:**
```bash
sudo systemctl is-active easyproxy
sudo systemctl is-failed easyproxy
```

**Docker:**
```bash
docker inspect --format='{{.State.Health.Status}}' easyproxy
```

**Supervisor:**
```bash
sudo supervisorctl status easyproxy
```

**集成监控系统:**
- Prometheus + Grafana
- Zabbix
- Nagios
- 云监控服务 (阿里云/腾讯云)

---

## 🐛 故障排查

### 服务无法启动

**1. 检查配置文件**
```bash
easyproxy validate /etc/easyproxy/config.yaml
```

**2. 检查端口占用**
```bash
sudo netstat -tlnp | grep 7899
sudo lsof -i :7899
```

**3. 查看详细日志**
```bash
# systemd
sudo journalctl -u easyproxy -xe

# Docker
docker logs easyproxy
```

**4. 检查权限**
```bash
# 确保用户有权限访问配置文件
sudo ls -la /etc/easyproxy/config.yaml

# 确保日志目录可写
sudo ls -la /var/log/easyproxy/
```

### 服务频繁重启

**1. 检查重启次数限制**

**systemd:**
```bash
sudo systemctl status easyproxy
# 查看 "Start request repeated too quickly"
```

**2. 增加重启间隔**

编辑服务文件:
```ini
[Service]
RestartSec=30  # 增加到 30 秒
StartLimitInterval=600
StartLimitBurst=5
```

### 性能问题

**1. 检查资源使用**
```bash
# CPU 和内存
top -p $(pgrep -f easyproxy)

# 网络连接数
sudo netstat -an | grep 7899 | wc -l

# 文件描述符使用
sudo ls -l /proc/$(pgrep -f easyproxy)/fd | wc -l
```

**2. 调整资源限制**

参考上面的"性能优化"部分。

### 日志问题

**日志文件过大:**

**systemd:**
```bash
# 清理旧日志
sudo journalctl --vacuum-time=7d  # 保留 7 天
sudo journalctl --vacuum-size=1G  # 限制 1GB
```

**Docker:**
```bash
# Docker 日志已自动轮转,可在 docker-compose.yml 中配置:
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

---

## 📚 参考资料

### 官方文档

- [systemd 文档](https://www.freedesktop.org/software/systemd/man/)
- [Docker 文档](https://docs.docker.com/)

### 相关文件

- [systemd 服务文件](../scripts/systemd/easyproxy.service)
- [Docker Compose 配置](../scripts/docker/docker-compose.yml)

### 社区支持

- GitHub Issues: https://github.com/Slothtron/easyproxy-py/issues
- 项目主页: https://github.com/Slothtron/easyproxy-py

---

## 🎯 快速决策树

```
需要部署 EasyProxy 守护进程?
│
├─ 你使用容器化部署?
│  ├─ 是 → 使用 Docker 方案 ⭐⭐⭐⭐⭐
│  └─ 否 → 继续
│
└─ 你的系统有 systemd? (systemctl --version)
   ├─ 是 → 使用 systemd 方案 ⭐⭐⭐⭐⭐
   └─ 否 → 建议升级系统或使用 Docker
```

---

**祝你部署顺利! 🚀**

如有问题,请查看故障排查部分或提交 Issue。
