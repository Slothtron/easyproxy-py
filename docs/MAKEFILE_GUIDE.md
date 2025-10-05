# Makefile 使用指南

本文档介绍如何使用精简的 `Makefile` 来管理 EasyProxy 项目。

## 📦 什么是 Make?

[Make](https://www.gnu.org/software/make/) 是一个经典的构建自动化工具，几乎在所有 Unix/Linux 系统上预装。

## 🚀 快速开始

```bash
# 查看所有命令
make help

# 开发模式安装
make dev

# 运行服务器
make run

# 构建包
make build
```

## 🔧 所有命令

### 开发命令

```bash
# 开发模式安装（包含开发依赖）
make dev

# 运行代理服务器
make run

# 自定义端口运行
make run ARGS='-p 8080'

# 清理构建文件
make clean
```

### 构建命令

```bash
# 构建分发包（生成 .whl 和 .tar.gz）
make build
```

### 发布命令

```bash
# 发布新版本（自动更新版本号、构建、创建标签）
make release VERSION=0.3.0
```

### 帮助命令

```bash
# 显示帮助信息
make help
```

## 🎯 工作流示例

### 场景 1: 开始开发

```bash
# 1. 克隆项目
git clone https://github.com/Slothtron/easyproxy-py.git
cd easyproxy-py

# 2. 开发模式安装
make dev

# 3. 运行测试
make run
```

### 场景 2: 构建和测试

```bash
# 1. 清理旧构建
make clean

# 2. 构建新包
make build

# 3. 测试安装
python -m venv test_venv
test_venv/bin/pip install dist/*.whl
test_venv/bin/easyproxy --version
rm -rf test_venv
```

### 场景 3: 发布新版本

```bash
# 1. 发布新版本（自动处理版本号、构建、标签）
make release VERSION=0.3.0

# 2. 推送代码和标签
git push origin develop
git push origin v0.3.0

# 3. 手动上传到 PyPI
python -m twine upload dist/*
```

### 场景 4: 日常开发

```bash
# 修改代码
vim easyproxy/proxy.py

# 直接测试（开发模式下修改立即生效）
make run

# 或
easyproxy start
```

## 📖 命令详解

### make dev

开发模式安装，包含开发依赖。

```bash
make dev
```

等同于：
```bash
pip install -e ".[dev]"
```

**特点：**
- 可编辑安装（修改代码立即生效）
- 包含开发依赖（pytest、black、mypy 等）
- 适合日常开发

### make run

运行代理服务器。

```bash
# 默认配置
make run

# 自定义参数
make run ARGS='-p 8080'
make run ARGS='-c config.yaml'
make run ARGS='--log-level DEBUG'
```

等同于：
```bash
python -m easyproxy start [ARGS]
```

### make clean

清理构建文件。

```bash
make clean
```

清理：
- `dist/` 目录
- `build/` 目录
- `*.egg-info` 目录
- `__pycache__` 目录
- `*.pyc` 文件

### make build

构建分发包。

```bash
make build
```

执行步骤：
1. 清理旧构建文件
2. 升级构建工具（build、twine）
3. 构建包（生成 .whl 和 .tar.gz）
4. 检查包完整性

生成文件：
- `dist/easyproxy-x.x.x-py3-none-any.whl` - Wheel 包（快速安装）
- `dist/easyproxy-x.x.x.tar.gz` - 源码包（完整项目）

### make release

发布新版本。

```bash
make release VERSION=0.3.0
```

执行步骤：
1. 检查版本号参数
2. 更新 `pyproject.toml` 中的版本号
3. 更新 `easyproxy/cli.py` 中的版本号
4. 构建分发包
5. 创建 Git 提交
6. 创建 Git 标签
7. 显示后续步骤提示

**注意：** 不会自动推送到远程仓库，需要手动推送。

## 🔍 高级用法

### 自定义 Python 解释器

```bash
# 使用特定 Python 版本
make PYTHON=python3.11 build
```

### 自定义 pip

```bash
# 使用特定 pip
make PIP=pip3 dev
```

### 链式调用

```bash
# 依次执行多个命令
make clean && make build
```

## 💡 提示和技巧

### 1. 查看命令执行过程

Makefile 默认隐藏命令输出（使用 `@` 前缀），如果需要查看：

```bash
# 移除 @ 前缀或使用 make -n 查看将要执行的命令
make -n build
```

### 2. 开发工作流

```bash
# 一次性设置开发环境
make dev

# 日常开发
vim easyproxy/proxy.py
make run ARGS='-p 8080'

# 提交前清理
make clean
```

### 3. 发布工作流

```bash
# 发布流程
make release VERSION=0.3.0
git push origin develop
git push origin v0.3.0
python -m twine upload dist/*
```

## 🆚 Make 的优势

1. **预装**: 几乎所有 Unix/Linux 系统都预装
2. **标准化**: 业界标准，更多开发者熟悉
3. **简洁**: 只保留核心功能，易于维护
4. **快速**: 无需额外安装和配置
5. **兼容性**: 与 CI/CD 系统无缝集成

## 📚 参考资源

- [GNU Make 官方文档](https://www.gnu.org/software/make/manual/)
- [Make 教程](https://makefiletutorial.com/)
- [Python 打包指南](https://packaging.python.org/)

## 🎓 学习建议

1. **从简单开始**: 先使用 `make help` 查看可用命令
2. **查看源码**: 打开 `Makefile` 了解实现
3. **实践**: 在实际项目中使用，熟悉常用命令
4. **保持简洁**: 只添加真正需要的命令

## 🔗 相关文档

- [QUICKSTART.md](../QUICKSTART.md) - 快速参考
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 项目结构说明
- [README.md](../README.md) - 项目主文档

## 📝 Makefile 内容

当前 Makefile 非常精简（约 80 行），只包含核心功能：

```makefile
# 开发命令
make dev     # 开发模式安装
make run     # 运行服务器
make clean   # 清理构建文件

# 构建命令
make build   # 构建分发包

# 发布命令
make release VERSION=x.x.x  # 发布新版本

# 帮助命令
make help    # 显示帮助信息
```

**设计理念：**
- ✅ 只保留最核心的功能
- ✅ 简洁明了，易于维护
- ✅ 专注于构建和开发
- ✅ 其他功能交给专门的工具

## 🎯 最佳实践

1. **使用虚拟环境**: 始终在虚拟环境中开发
2. **开发模式**: 使用 `make dev` 而不是 `pip install .`
3. **清理习惯**: 构建前先 `make clean`
4. **版本管理**: 使用 `make release` 自动化版本发布
5. **保持简洁**: 不要在 Makefile 中添加过多功能

---

**提示:** 这个精简的 Makefile 专注于核心的开发和构建任务，让项目更易维护！🚀