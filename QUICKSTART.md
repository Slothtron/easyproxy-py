# EasyProxy 快速参考

## 📦 打包和分发速查

### 一键构建

```bash
# 使用 Make
make build

# 或手动构建
python -m build
```

### 本地测试安装

```bash
# 创建测试虚拟环境
python -m venv test_venv
source test_venv/bin/activate
pip install dist/*.whl
easyproxy --version
deactivate
rm -rf test_venv
```

### 开发模式安装

```bash
# 使用 Make（推荐，包含开发依赖）
make dev

# 或手动安装
pip install -e ".[dev]"

# 测试命令
easyproxy --version
easyproxy start --help
```

### 发布新版本

```bash
# 发布新版本（自动更新版本号、构建、标签）
make release VERSION=0.3.0

# 手动上传到 PyPI
python -m twine upload dist/*
```

## 🚀 常用命令

### 开发相关

```bash
# 开发模式安装
make dev

# 运行代理服务器
make run

# 自定义端口
make run ARGS='-p 8080'

# 清理构建文件
make clean
```

### 构建相关

```bash
# 构建 Python 包
make build

# 查看包内容
python -m zipfile -l dist/*.whl
tar -tzf dist/*.tar.gz
```

### 安装方式

```bash
# 从 PyPI 安装
pip install easyproxy

# 从本地 wheel 安装
pip install dist/easyproxy-0.2.0-py3-none-any.whl

# 从源码安装
pip install .

# 开发模式
pip install -e ".[dev]"

# 从 Git 安装
pip install git+https://github.com/Slothtron/easyproxy-py.git
```

### 上传到 PyPI

```bash
# 上传到正式环境
python -m twine upload dist/*

# 或上传到测试环境
python -m twine upload --repository testpypi dist/*

# 从测试环境安装测试
pip install --index-url https://test.pypi.org/simple/ easyproxy
```

### 版本管理

```bash
# 使用 Make 发布新版本（自动更新版本号）
make release VERSION=0.3.0

# 或手动更新版本号
# 1. pyproject.toml 中的 version
# 2. easyproxy/cli.py 中的 version

# 提交和标签
git add .
git commit -m "chore: bump version to 0.3.0"
git tag -a v0.3.0 -m "Release version 0.3.0"
git push origin develop
git push origin v0.3.0
```

## 🔧 使用 EasyProxy

### 基本使用

```bash
# 启动服务器（默认配置）
make run
# 或
easyproxy start

# 自定义端口
make run ARGS='-p 8080'
# 或
easyproxy start -p 8080

# 自定义地址和端口
easyproxy start -H 127.0.0.1 -p 7899

# 设置日志级别
easyproxy start --log-level DEBUG
```

### 配置文件

```bash
# 生成配置文件
easyproxy init config.yaml

# 使用配置文件启动
make run ARGS='-c config.yaml'
# 或
easyproxy start -c config.yaml

# 验证配置文件
easyproxy validate -c config.yaml
```

### 测试代理

```bash
# HTTP 代理
curl -x http://127.0.0.1:7899 http://www.baidu.com

# HTTPS 代理
curl -x http://127.0.0.1:7899 https://www.baidu.com

# SOCKS5 代理
curl --socks5 127.0.0.1:7899 http://www.baidu.com

# 带认证的代理
curl -x http://username:password@127.0.0.1:7899 http://www.baidu.com
```

## 📚 文档链接

- **详细打包指南**: `docs/PACKAGING.md`
- **项目架构**: `docs/architecture.md`
- **完整文档**: `README.md`

## 🐛 故障排查

### 命令找不到

```bash
# 检查安装
pip show easyproxy

# 查看安装位置
which easyproxy

# 重新安装
pip uninstall easyproxy
pip install easyproxy
```

### 构建失败

```bash
# 清理并重试
make clean
pip install --upgrade pip setuptools wheel build
make build
```

### 上传失败

```bash
# 检查 PyPI 凭证
cat ~/.pypirc

# 检查包
python -m twine check dist/*

# 使用 token 上传
python -m twine upload --username __token__ --password pypi-xxx dist/*
```

## 💡 提示

1. **使用虚拟环境**: 始终在虚拟环境中测试
2. **先测试后发布**: 使用 TestPyPI 验证
3. **版本不可覆盖**: PyPI 不允许重复版本号
4. **保持文档更新**: 及时更新 README 和版本号
5. **使用 Make**: 自动化常见任务（`make help` 查看所有命令）
6. **构建产物**: 
   - `.whl` - 快速安装包（推荐）
   - `.tar.gz` - 完整源码包（兼容性）