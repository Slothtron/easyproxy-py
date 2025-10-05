# EasyProxy 快速参考

## 📦 打包和分发速查

### 一键构建

```bash
# 使用 Just (推荐)
just build

# 或手动构建
python -m build
```

### 本地测试安装

```bash
# 使用 Just
just test

# 或手动测试
python -m venv test_env
source test_env/bin/activate
pip install dist/*.whl
easyproxy --version
deactivate
rm -rf test_env
```

### 二进制打包

```bash
# 打包二进制
just build-bin

# 安装到系统
just install-bin

# 卸载
just remove-bin

# 深度清理
just deep-clean
```

### 开发模式安装

```bash
# 使用 Just (推荐)
just dev

# 或手动安装
pip install -e .

# 测试命令
easyproxy --version
easyproxy start --help
```

### 发布到 PyPI

```bash
# 发布新版本 (自动更新版本号、构建、标签)
just release 0.1.0

# 上传到测试环境
just upload-test

# 上传到正式环境
just upload

# 或手动发布
python -m twine upload dist/*
```

## 🚀 常用命令

### 构建相关

```bash
# 清理构建文件
just clean

# 深度清理 (包括二进制)
just deep-clean

# 构建 Python 包
just build

# 打包二进制 (推荐)
just build-bin

# 检查包
just check

# 查看包内容
unzip -l dist/*.whl
tar -tzf dist/*.tar.gz
```

### 部署相关

```bash
# 安装二进制
just install-bin

# 安装 systemd 服务
just setup-service

# 卸载服务
just remove-service

# 卸载二进制
just remove-bin
```

### 安装方式

```bash
# 从 PyPI 安装
pip install easyproxy

# 从本地 wheel 安装
pip install dist/easyproxy-0.1.0-py3-none-any.whl

# 从源码安装
pip install .

# 开发模式
pip install -e .

# 从 Git 安装
pip install git+https://github.com/Slothtron/easyproxy-py.git
```

### 上传到 PyPI

```bash
# 上传到测试环境
python -m twine upload --repository testpypi dist/*

# 从测试环境安装
pip install --index-url https://test.pypi.org/simple/ easyproxy

# 上传到正式环境
python -m twine upload dist/*
```

### 版本管理

```bash
# 使用 Just 发布新版本 (自动更新版本号)
just release 0.2.0

# 或手动更新版本号
# 1. pyproject.toml 中的 version
# 2. easyproxy/cli.py 中的 version

# 提交和标签
git add .
git commit -m "chore: bump version to 0.2.0"
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin develop
git push origin v0.2.0
```

## 🔧 使用 EasyProxy

### 基本使用

```bash
# 启动服务器 (默认配置)
just run
# 或
easyproxy start

# 自定义端口
just run -p 8080
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
just init config.yaml
# 或
easyproxy init config.yaml

# 使用配置文件启动
just run -c config.yaml
# 或
easyproxy start -c config.yaml

# 验证配置文件
just validate config.yaml
# 或
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
rm -rf dist/ build/ *.egg-info
pip install --upgrade pip setuptools wheel build
python -m build
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
5. **使用 Just**: 自动化常见任务 (`just --list` 查看所有命令)
6. **查看帮助**: `just help` 获取详细使用说明
