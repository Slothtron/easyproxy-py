# EasyProxy 打包和分发指南

本文档介绍如何将 EasyProxy 打包并分发,使其可以通过 `pip install` 安装。

## 📦 打包准备

### 1. 项目结构

确保项目结构如下:
```
easyproxy-py/
├── easyproxy/           # 主包目录
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py          # CLI入口
│   ├── config.py
│   ├── proxy.py
│   ├── auth.py
│   └── logger.py
├── pyproject.toml      # 现代打包配置(推荐)
├── MANIFEST.in         # 额外文件包含规则
├── README.md           # 项目说明
├── LICENSE             # 许可证
└── requirements.txt    # 依赖列表
```

### 2. 安装打包工具

```bash
pip install --upgrade pip setuptools wheel build twine
```

## 🔨 构建分发包

### 方法一:使用 build (推荐)

```bash
# 构建源码分发包和wheel包
python -m build

# 生成的文件在 dist/ 目录:
# - easyproxy-0.1.0.tar.gz (源码包)
# - easyproxy-0.1.0-py3-none-any.whl (wheel包)
```

### 方法二:使用 setuptools

```bash
# 构建源码分发包
python setup.py sdist

# 构建wheel包
python setup.py bdist_wheel

# 同时构建两者
python setup.py sdist bdist_wheel
```

## 📤 分发方式

### 方式一:上传到 PyPI (公开分发)

#### 1. 注册 PyPI 账号
- 访问 https://pypi.org/account/register/
- 注册账号并验证邮箱

#### 2. 配置 API Token (推荐)
```bash
# 在 PyPI 网站生成 API token
# 创建 ~/.pypirc 文件
cat > ~/.pypirc << 'EOF'
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcC...你的token...
EOF

chmod 600 ~/.pypirc
```

#### 3. 上传到 TestPyPI (测试环境)
```bash
# 先在测试环境验证
python -m twine upload --repository testpypi dist/*

# 测试安装
pip install --index-url https://test.pypi.org/simple/ easyproxy
```

#### 4. 上传到正式 PyPI
```bash
python -m twine upload dist/*
```

#### 5. 用户安装
```bash
# 安装最新版本
pip install easyproxy

# 安装指定版本
pip install easyproxy==0.1.0

# 升级到最新版本
pip install --upgrade easyproxy
```

### 方式二:本地安装 (开发测试)

#### 开发模式安装 (可编辑)
```bash
# 在项目根目录执行
pip install -e .

# 修改代码后立即生效,无需重新安装
```

#### 从源码安装
```bash
# 在项目根目录执行
pip install .
```

#### 从 wheel 包安装
```bash
pip install dist/easyproxy-0.1.0-py3-none-any.whl
```

#### 从 tar.gz 包安装
```bash
pip install dist/easyproxy-0.1.0.tar.gz
```

### 方式三:私有 PyPI 服务器

如果不想公开发布,可以搭建私有 PyPI 服务器:

#### 使用 devpi
```bash
# 安装 devpi
pip install devpi-server devpi-client

# 启动服务器
devpi-init
devpi-server --start

# 配置客户端
devpi use http://localhost:3141
devpi user -c myuser password=mypassword
devpi login myuser --password=mypassword
devpi index -c dev

# 上传包
devpi upload

# 用户安装
pip install --index-url http://localhost:3141/myuser/dev/+simple/ easyproxy
```

#### 使用 pypiserver
```bash
# 安装
pip install pypiserver

# 启动服务器
mkdir ~/pypi-packages
pypi-server run -p 8080 ~/pypi-packages

# 上传包
pip install twine
twine upload --repository-url http://localhost:8080 dist/*

# 用户安装
pip install --index-url http://localhost:8080/simple/ easyproxy
```

### 方式四:Git 仓库直接安装

```bash
# 从 GitHub 安装
pip install git+https://github.com/Slothtron/easyproxy-py.git

# 从指定分支安装
pip install git+https://github.com/Slothtron/easyproxy-py.git@develop

# 从指定标签安装
pip install git+https://github.com/Slothtron/easyproxy-py.git@v0.1.0
```

### 方式五:文件共享 (局域网/内网)

```bash
# 1. 将 dist/ 目录复制到共享位置
cp -r dist/ /shared/packages/easyproxy/

# 2. 用户从共享位置安装
pip install /shared/packages/easyproxy/easyproxy-0.1.0-py3-none-any.whl

# 或通过 HTTP 服务器
cd dist/
python -m http.server 8000

# 用户安装
pip install http://server-ip:8000/easyproxy-0.1.0-py3-none-any.whl
```

## 🎯 安装后使用

安装完成后,`easyproxy` 命令将自动添加到系统 PATH:

```bash
# 查看版本
easyproxy --version

# 启动服务器
easyproxy start

# 生成配置文件
easyproxy init config.yaml

# 使用配置文件启动
easyproxy start -c config.yaml

# 验证配置
easyproxy validate -c config.yaml
```

## 🔄 版本管理

### 更新版本号

在 `pyproject.toml` 中更新版本:
```toml
[project]
version = "0.2.0"  # 更新这里
```

同时更新 `easyproxy/cli.py` 中的版本:
```python
@click.version_option(version="0.2.0", prog_name="easyproxy")
```

### 语义化版本规范

遵循 [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0): 不兼容的 API 变更
- **MINOR** (0.1.0): 向后兼容的功能新增
- **PATCH** (0.0.1): 向后兼容的问题修复

### 发布流程

```bash
# 1. 更新版本号
# 编辑 pyproject.toml 和 cli.py

# 2. 提交更改
git add .
git commit -m "chore: bump version to 0.2.0"

# 3. 创建标签
git tag -a v0.2.0 -m "Release version 0.2.0"

# 4. 推送到远程
git push origin develop
git push origin v0.2.0

# 5. 清理旧构建
rm -rf dist/ build/ *.egg-info

# 6. 构建新版本
python -m build

# 7. 上传到 PyPI
python -m twine upload dist/*
```

## 🧪 测试打包

### 在虚拟环境中测试

```bash
# 创建测试虚拟环境
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
# 或 test_env\Scripts\activate  # Windows

# 安装构建的包
pip install dist/easyproxy-0.1.0-py3-none-any.whl

# 测试命令
easyproxy --version
easyproxy start --help

# 清理
deactivate
rm -rf test_env
```

### 检查包内容

```bash
# 查看 wheel 包内容
unzip -l dist/easyproxy-0.1.0-py3-none-any.whl

# 查看 tar.gz 包内容
tar -tzf dist/easyproxy-0.1.0.tar.gz

# 使用 twine 检查包
python -m twine check dist/*
```

## 📋 最佳实践

1. **始终在虚拟环境中测试**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **使用 TestPyPI 先测试**
   - 避免在正式 PyPI 上发布错误版本

3. **版本号不可重复使用**
   - PyPI 不允许覆盖已发布的版本

4. **保持 README.md 更新**
   - PyPI 会显示 README 作为项目描述

5. **添加 .gitignore**
   - 避免提交构建产物到版本控制

6. **使用 pre-commit hooks**
   - 确保代码质量

7. **编写测试**
   - 确保打包后功能正常

## 🐛 常见问题

### 问题 1: 命令找不到

```bash
# 检查 PATH
echo $PATH

# 检查安装位置
pip show easyproxy

# 重新安装
pip uninstall easyproxy
pip install easyproxy
```

### 问题 2: 版本冲突

```bash
# 卸载旧版本
pip uninstall easyproxy

# 清理缓存
pip cache purge

# 重新安装
pip install easyproxy
```

### 问题 3: 依赖问题

```bash
# 查看依赖树
pip install pipdeptree
pipdeptree -p easyproxy

# 强制重新安装依赖
pip install --force-reinstall easyproxy
```

## 📚 参考资源

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI 官方文档](https://pypi.org/help/)
- [setuptools 文档](https://setuptools.pypa.io/)
- [PEP 517 - 构建系统](https://peps.python.org/pep-0517/)
- [PEP 518 - pyproject.toml](https://peps.python.org/pep-0518/)
- [Semantic Versioning](https://semver.org/)
