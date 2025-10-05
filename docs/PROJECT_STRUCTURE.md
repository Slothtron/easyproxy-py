# EasyProxy 项目结构

## 📁 目录结构

```
easyproxy-py/
├── easyproxy/              # 主包目录
│   ├── __init__.py        # 包初始化
│   ├── __main__.py        # 模块入口 (python -m easyproxy)
│   ├── cli.py             # 命令行接口 (Click)
│   ├── config.py          # 配置管理 (Pydantic)
│   ├── proxy.py           # 代理服务器核心
│   ├── auth.py            # 认证模块
│   └── logger.py          # 日志系统 (structlog)
│
├── scripts/               # 脚本目录 (可选)
│
├── docs/                  # 文档目录
│   ├── PACKAGING.md      # 打包和分发详细指南
│   ├── PROJECT_STRUCTURE.md  # 项目结构说明 (本文件)
│   └── architecture.md   # 架构文档
│
├── config/                # 示例配置文件
│   └── ...
│
├── pyproject.toml        # 项目配置和打包元数据 (PEP 518)
├── MANIFEST.in           # 额外文件包含规则
├── requirements.txt      # 运行时依赖
├── Makefile             # 任务运行器 (Make)
├── README.md            # 项目说明
├── QUICKSTART.md        # 快速参考
├── LICENSE              # MIT 许可证
└── .gitignore           # Git 忽略规则
```

## 🔑 关键文件说明

### pyproject.toml

现代 Python 项目的核心配置文件,包含:

- **[build-system]**: 构建系统配置
- **[project]**: 项目元数据(名称、版本、依赖等)
- **[project.scripts]**: 命令行入口点定义
  ```toml
  [project.scripts]
  easyproxy = "easyproxy.cli:main"
  ```
  这会创建 `easyproxy` 命令,指向 `easyproxy.cli.main()` 函数

### easyproxy/cli.py

命令行接口实现:
- 使用 Click 框架
- 定义所有子命令 (start, init, validate)
- `main()` 函数是命令行入口点

### easyproxy/__main__.py

允许使用 `python -m easyproxy` 运行:
```python
from easyproxy.cli import main

if __name__ == "__main__":
    main()
```

### MANIFEST.in

指定哪些非 Python 文件应包含在分发包中:
```
include README.md
include LICENSE
recursive-include docs *.md
```

### requirements.txt

运行时依赖列表:
```
pydantic>=2.6.0
PyYAML>=6.0.1
click>=8.1.0
structlog>=24.1.0
```

## 🔄 工作流程

### 开发流程

1. **克隆项目**
   ```bash
   git clone https://github.com/Slothtron/easyproxy-py.git
   cd easyproxy-py
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **开发模式安装**
   ```bash
   # 使用 Make (推荐)
   make dev
   
   # 或手动安装
   pip install -e .
   ```

4. **开发和测试**
   ```bash
   # 修改代码
   # 直接测试 (开发模式下修改立即生效)
   make run
   # 或
   easyproxy start
   ```

### 构建流程

1. **清理旧构建**
   ```bash
   make clean
   ```

2. **构建分发包**
   ```bash
   make build
   # 或
   python -m build
   ```

3. **测试安装**
   ```bash
   python -m venv test_venv
   test_venv/bin/pip install dist/*.whl
   test_venv/bin/easyproxy --version
   rm -rf test_venv
   ```

4. **检查包**
   ```bash
   python -m twine check dist/*
   ```

### 发布流程

1. **发布新版本** (自动更新版本号、构建、创建标签)
   ```bash
   make release VERSION=0.2.0
   ```

2. **推送代码和标签**
   ```bash
   git push origin develop
   git push origin v0.2.0
   ```

3. **手动上传到 PyPI**
   ```bash
   python -m twine upload dist/*
   ```

## 📦 打包机制

### 入口点 (Entry Points)

`pyproject.toml` 中定义的入口点:

```toml
[project.scripts]
easyproxy = "easyproxy.cli:main"
```

当用户 `pip install easyproxy` 后:
1. pip 会在 Python 的 `Scripts/` 或 `bin/` 目录创建 `easyproxy` 可执行文件
2. 该文件会调用 `easyproxy.cli.main()` 函数
3. 用户可以直接在命令行运行 `easyproxy`

### 包发现

setuptools 会自动发现 `easyproxy/` 目录作为 Python 包,因为:
1. 它包含 `__init__.py` 文件
2. `pyproject.toml` 中配置了 `packages = ["easyproxy"]`

### 依赖管理

- **运行时依赖**: 在 `pyproject.toml` 的 `dependencies` 中定义
- **开发依赖**: 在 `[project.optional-dependencies]` 中定义
- pip 安装时会自动安装运行时依赖

## 🛠️ 工具和脚本

### Makefile

精简的任务运行器，只保留核心功能：

```bash
# 查看所有命令
make help

# 开发命令
make dev                # 开发模式安装（包含开发依赖）
make run                # 运行服务器
make run ARGS='-p 8080' # 自定义端口
make clean              # 清理构建文件

# 构建命令
make build              # 构建分发包

# 发布命令
make release VERSION=0.3.0  # 发布新版本
```

### Make 的优势

- **预装**: 几乎所有 Unix/Linux 系统都预装
- **简洁**: 只保留核心功能，易于维护
- **标准化**: 业界标准，更多开发者熟悉
- **快速**: 无需额外安装和配置
- **兼容性**: 与 CI/CD 系统无缝集成

详细使用说明请参考 [docs/MAKEFILE_GUIDE.md](MAKEFILE_GUIDE.md)

## 📚 文档结构

- **README.md**: 项目主文档,用户首先看到的内容
- **QUICKSTART.md**: 快速参考,常用命令速查
- **docs/PROJECT_STRUCTURE.md**: 项目结构说明 (本文件)
- **docs/MAKEFILE_GUIDE.md**: Makefile 使用指南
- **docs/architecture.md**: 技术架构文档

## 🔍 重要概念

### 可编辑安装 (Editable Install)

```bash
pip install -e .
```

- 不复制文件,而是创建链接
- 修改源码立即生效,无需重新安装
- 适合开发阶段

### Wheel vs Source Distribution

- **Wheel (.whl)**: 预构建的二进制包,安装快
- **Source Distribution (.tar.gz)**: 源码包,需要构建

### 命令行入口点

通过 `[project.scripts]` 定义的入口点会:
1. 创建可执行脚本
2. 自动添加到 PATH
3. 跨平台兼容 (Windows/Linux/Mac)

## 🎯 最佳实践

1. **使用虚拟环境**: 隔离项目依赖
2. **开发模式安装**: 方便调试
3. **先测试后发布**: 使用 TestPyPI
4. **版本管理**: 遵循语义化版本
5. **文档更新**: 保持文档与代码同步
6. **使用脚本**: 自动化重复任务
7. **代码审查**: 发布前检查代码质量

## 🔗 相关资源

- [Python Packaging User Guide](https://packaging.python.org/)
- [PEP 517 - Build System](https://peps.python.org/pep-0517/)
- [PEP 518 - pyproject.toml](https://peps.python.org/pep-0518/)
- [setuptools 文档](https://setuptools.pypa.io/)
- [Click 文档](https://click.palletsprojects.com/)
