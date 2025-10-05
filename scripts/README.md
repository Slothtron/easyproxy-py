# EasyProxy 部署脚本

本目录包含 EasyProxy 在 Linux 系统上的守护进程部署脚本。

## 📁 目录结构

```
scripts/
├── systemd/          # systemd 服务配置
│   ├── easyproxy.service
│   ├── install.sh
│   └── uninstall.sh
├── docker/           # Docker 容器化配置
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .dockerignore
│   └── README.md
├── build_binary.sh   # 二进制打包脚本
├── clean_build.sh    # 清理构建产物脚本
└── README.md         # 本文件
```

## 🎯 方案选择

| 方案 | 适用场景 | 推荐指数 |
|------|----------|----------|
| **systemd** | 现代 Linux 发行版 (Ubuntu 16.04+, CentOS 7+, Debian 8+) | ⭐⭐⭐⭐⭐ |
| **Docker** | 容器化部署,需要隔离和可移植性 | ⭐⭐⭐⭐⭐ |

**快速判断:**
```bash
# 检查是否有 systemd
systemctl --version

# 检查是否有 Docker
docker --version
```

## 🚀 快速开始

### 二进制打包

```bash
# 使用 Just (推荐)
just build-bin           # 打包二进制
just install-bin         # 安装到系统
just deep-clean          # 清理所有产物 (可选)

# 或手动执行
cd scripts
./build_binary.sh
sudo cp ../dist/easyproxy /usr/bin/
./clean_build.sh         # 清理 (可选)
```

### systemd 服务

```bash
# 使用 Just (推荐)
just setup-service       # 安装服务
just remove-service      # 卸载服务

# 或手动执行
cd scripts/systemd
sudo ./install.sh
sudo systemctl start easyproxy
```

### Docker

```bash
cd scripts/docker
cp ../../config/config.example.yaml config.yaml
docker-compose up -d
```

## 📖 详细文档

查看完整的部署指南: [../docs/DAEMON.md](../docs/DAEMON.md)

## 🔧 自定义配置

所有方案都使用 `/etc/easyproxy/config.yaml` 作为配置文件。

生成默认配置:
```bash
easyproxy init /etc/easyproxy/config.yaml
```

## 🐛 故障排查

### systemd
```bash
sudo systemctl status easyproxy
sudo journalctl -u easyproxy -xe
```

### Docker
```bash
docker logs easyproxy
docker inspect easyproxy
```

## 📚 相关资源

- [完整部署文档](../docs/DAEMON.md)
- [配置说明](../README.md#配置说明)
- [项目主页](https://github.com/Slothtron/easyproxy-py)
