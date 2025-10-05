# Justfile 使用指南

本文档介绍如何使用 `justfile` 来管理 EasyProxy 项目的常见任务。

## 📦 什么是 Just?

[Just](https://github.com/casey/just) 是一个命令运行器,类似于 `make`,但更简单、更现代。它使用 `justfile` 来定义和运行项目任务。

## 🚀 安装 Just

### Linux / macOS

```bash
# 使用 Cargo (Rust 包管理器)
cargo install just

# 使用包管理器
# Ubuntu/Debian
sudo apt install just

# Arch Linux
sudo pacman -S just

# macOS (Homebrew)
brew install just
```

### Windows

```bash
# 使用 Cargo
cargo install just

# 使用 Scoop
scoop install just

# 使用 Chocolatey
choco install just
```

### 验证安装

```bash
just --version
```

## 📋 查看所有命令

```bash
# 列出所有可用命令
just --list

# 或简写
just -l

# 显示详细帮助
just help
```

## 🔧 常用命令

### 开发相关

```bash
# 开发模式安装 (可编辑安装)
just dev

# 安装开发依赖
just setup-dev

# 清理构建文件
just clean

# 深度清理所有产物
just deep-clean
```

### 构建相关

```bash
# 构建 Python 包 (PyPI)
just build

# 打包二进制 (推荐)
just build-bin

# 检查代码质量
just check
```

### 测试相关

```bash
# 测试安装 (CI/CD)
just test
```

### 部署相关

```bash
# 安装二进制到系统
just install-bin

# 卸载二进制
just remove-bin

# 安装 systemd 服务
just setup-service

# 卸载 systemd 服务
just remove-service
```

### 运行相关

```bash
# 启动代理服务器 (默认配置)
just run

# 自定义端口
just run -p 8080

# 使用配置文件
just run -c config.yaml

# 设置日志级别
just run --log-level DEBUG

# 组合参数
just run -H 127.0.0.1 -p 8888 --log-level INFO
```

### 配置相关

```bash
# 生成配置文件
just init config.yaml

# 验证配置文件
just validate config.yaml
```

### 发布相关

```bash
# 发布新版本 (自动更新版本号、构建、创建标签)
just release 0.2.0

# 上传到 TestPyPI (测试环境)
just upload-test

# 上传到 PyPI (正式环境)
just upload
```

### 信息相关

```bash
# 显示项目信息
just info

# 显示帮助
just help
```

## 🎯 工作流示例

### 场景 1: 开始开发

```bash
# 1. 克隆项目
git clone https://github.com/Slothtron/easyproxy-py.git
cd easyproxy-py

# 2. 开发模式安装
just dev

# 3. 运行测试
just run
```

### 场景 2: 构建和测试

```bash
# 1. 清理旧构建
just clean

# 2. 构建新包
just build

# 3. 测试安装
just test
```

### 场景 4: 二进制打包和部署

```bash
# 1. 打包二进制
just build-bin

# 2. 安装到系统
just install-bin

# 3. 安装 systemd 服务
just setup-service

# 4. 查看服务状态
sudo systemctl status easyproxy
```

### 场景 3: 发布新版本

```bash
# 1. 发布新版本 (自动处理版本号、构建、标签)
just release 0.2.0

# 2. 上传到测试环境
just upload-test

# 3. 从 TestPyPI 测试安装
pip install --index-url https://test.pypi.org/simple/ easyproxy

# 4. 测试通过后,上传到正式环境
just upload

# 5. 推送代码和标签
git push origin develop
git push origin v0.2.0
```

### 场景 4: 日常开发

```bash
# 修改代码
vim easyproxy/proxy.py

# 直接测试 (开发模式下修改立即生效)
just run

# 或
easyproxy start
```

## 📖 Justfile 配方说明

### default

默认配方,显示所有可用命令。

```bash
just
# 等同于
just --list
```

### build

构建分发包,包括:
- 清理旧文件
- 安装/升级构建工具
- 构建 wheel 和源码包
- 检查包完整性

### clean

清理构建产物:
- `dist/` 目录
- `build/` 目录
- `*.egg-info` 目录
- `__pycache__` 目录

### dev

开发模式安装 (`pip install -e .`),代码修改立即生效。

### install

正常安装 (`pip install .`),复制文件到 site-packages。

### test

在临时虚拟环境中测试安装:
1. 创建虚拟环境
2. 安装构建的包
3. 测试命令
4. 清理环境

### build-bin

打包成独立二进制文件:
- 使用 PyInstaller
- 自动清理 build/ 和 *.spec
- 生成 dist/easyproxy

### install-bin

安装二进制文件到系统:
- 复制到 /usr/bin/easyproxy
- 设置执行权限
- 验证安装

### setup-service

安装 systemd 服务:
- 创建用户和目录
- 配置服务文件
- 启用开机自启

### remove-service

卸载 systemd 服务:
- 停止并禁用服务
- 删除服务文件
- 可选清理用户和数据

### remove-bin

卸载二进制文件:
- 删除 /usr/bin/easyproxy
- 删除 /usr/local/bin/easyproxy
- 提示如何卸载开发环境

### deep-clean

深度清理所有构建产物:
- 清理 dist/, build/
- 清理 *.spec, *.egg-info
- 清理 __pycache__, *.pyc

### run

运行代理服务器,支持传递参数。

```bash
just run                    # 默认配置
just run -p 8080            # 自定义端口
just run -c config.yaml     # 使用配置文件
```

### init

生成配置文件。

```bash
just init                   # 生成 config.yaml
just init my-config.yaml    # 自定义文件名
```

### validate

验证配置文件。

```bash
just validate config.yaml
```

### check

检查代码质量:
- 验证 `pyproject.toml` 语法
- 检查分发包 (如果存在)

### release

发布新版本:
1. 检查 Git 状态
2. 更新版本号 (pyproject.toml 和 cli.py)
3. 构建分发包
4. 创建 Git 提交和标签

```bash
just release 0.2.0
```

### upload-test

上传到 TestPyPI。

### upload

上传到正式 PyPI (需要确认)。

### info

显示项目信息:
- Python 版本
- Pip 版本
- 项目版本
- Git 分支和远程
- 构建产物

### help

显示详细的帮助信息。

## 🔍 高级用法

### 查看配方源码

```bash
# 查看特定配方的定义
just --show build

# 查看所有配方
just --show
```

### 在不同目录运行

```bash
# 在指定目录运行 justfile
just --working-directory /path/to/project build

# 或简写
just -d /path/to/project build
```

### 设置变量

Justfile 中定义了一些变量:

```justfile
python := "python"
pip := "pip"
```

可以在命令行覆盖:

```bash
just python=python3.11 build
```

### 调试模式

```bash
# 显示执行的命令
just --verbose build

# 或简写
just -v build
```

## 💡 提示和技巧

### 1. 自动补全

Just 支持 shell 自动补全:

```bash
# Bash
just --completions bash > /etc/bash_completion.d/just

# Zsh
just --completions zsh > /usr/local/share/zsh/site-functions/_just

# Fish
just --completions fish > ~/.config/fish/completions/just.fish
```

### 2. 别名

可以在 shell 配置中创建别名:

```bash
# ~/.bashrc 或 ~/.zshrc
alias jb='just build'
alias jr='just run'
alias jd='just dev'
```

### 3. 链式调用

```bash
# 依次执行多个命令
just clean && just build && just test-install
```

### 4. 查看执行时间

```bash
# 使用 time 命令
time just build
```

### 5. 后台运行

```bash
# 后台运行服务器
just run &

# 查看日志
tail -f /path/to/log
```

## 🆚 Just vs Make vs NuShell

### Just 的优势

1. **更简单的语法**: 不需要处理 Make 的 tab 缩进问题
2. **跨平台**: 在 Windows/Linux/macOS 上行为一致
3. **更好的错误信息**: 清晰的错误提示
4. **现代特性**: 支持参数、默认值、字符串插值等
5. **无需依赖**: 单个二进制文件,无需 shell 特定功能

### 与 Make 对比

| 特性 | Just | Make |
|------|------|------|
| 语法 | 简单直观 | 复杂(tab 缩进) |
| 跨平台 | ✅ | ⚠️ (有差异) |
| 参数支持 | ✅ 原生支持 | ⚠️ 需要变通 |
| 学习曲线 | 低 | 中等 |
| 构建系统 | ❌ | ✅ |

### 与 NuShell 脚本对比

| 特性 | Just | NuShell |
|------|------|---------|
| 安装 | 单个二进制 | 需要 NuShell |
| 语法 | 简单 | 强大但复杂 |
| 跨平台 | ✅ | ✅ |
| 学习曲线 | 低 | 高 |
| 适用场景 | 任务运行 | 通用脚本 |

## 📚 参考资源

- [Just 官方文档](https://just.systems/)
- [Just GitHub 仓库](https://github.com/casey/just)
- [Just 示例集合](https://github.com/casey/just/tree/master/examples)

## 🎓 学习建议

1. **从简单开始**: 先使用 `just --list` 查看可用命令
2. **查看源码**: 使用 `just --show` 了解配方实现
3. **实践**: 在实际项目中使用,熟悉常用命令
4. **自定义**: 根据需要添加自己的配方
5. **分享**: 与团队分享 justfile,统一工作流程

## 🔗 相关文档

- [QUICKSTART.md](../QUICKSTART.md) - 快速参考
- [PACKAGING.md](PACKAGING.md) - 打包详细指南
- [DEMO.md](DEMO.md) - 实际操作演示
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 项目结构说明
