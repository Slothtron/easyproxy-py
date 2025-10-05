# EasyProxy 演示指南

本文档演示如何从零开始构建、打包和分发 EasyProxy。

## 🎬 场景一: 本地开发和测试

### 步骤 1: 准备环境

```bash
# 进入项目目录
cd /home/lolioy/workspace/projects/easyproxy-py

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 查看当前 Python 版本
python --version  # 应该是 3.11+
```

### 步骤 2: 开发模式安装

```bash
# 方式一: 使用任务文件
nu Taskfile.nu dev

# 方式二: 手动安装
pip install -e .
```

### 步骤 3: 测试命令

```bash
# 查看版本
easyproxy --version
# 输出: easyproxy, version 0.1.0

# 查看帮助
easyproxy --help

# 生成配置文件
easyproxy init my-config.yaml

# 启动代理服务器
easyproxy start

# 在另一个终端测试
curl -x http://127.0.0.1:7899 http://www.baidu.com
```

## 🎬 场景二: 构建分发包

### 步骤 1: 清理旧构建

```bash
# 使用任务文件
nu Taskfile.nu clean

# 或手动清理
rm -rf dist/ build/ *.egg-info
```

### 步骤 2: 构建包

```bash
# 方式一: 使用构建脚本 (推荐)
nu scripts/build.nu

# 方式二: 使用任务文件
nu Taskfile.nu build

# 方式三: 手动构建
python -m build
```

### 步骤 3: 查看生成的文件

```bash
ls -lh dist/
# 输出:
# easyproxy-0.1.0-py3-none-any.whl  (Wheel 包)
# easyproxy-0.1.0.tar.gz            (源码包)
```

### 步骤 4: 检查包

```bash
# 检查包完整性
python -m twine check dist/*

# 查看 wheel 包内容
unzip -l dist/easyproxy-0.1.0-py3-none-any.whl

# 查看源码包内容
tar -tzf dist/easyproxy-0.1.0.tar.gz
```

## 🎬 场景三: 测试安装

### 方式一: 使用测试脚本

```bash
nu scripts/test-install.nu
```

这个脚本会:
1. 创建临时虚拟环境
2. 安装构建的包
3. 测试所有命令
4. 清理环境

### 方式二: 手动测试

```bash
# 创建测试环境
python -m venv test_env
source test_env/bin/activate

# 安装 wheel 包
pip install dist/easyproxy-0.1.0-py3-none-any.whl

# 测试命令
easyproxy --version
easyproxy --help
easyproxy init test-config.yaml
cat test-config.yaml

# 启动服务器 (Ctrl+C 停止)
easyproxy start -p 8888

# 清理
deactivate
rm -rf test_env test-config.yaml
```

## 🎬 场景四: 分发给用户

### 方式 A: 上传到 PyPI (公开分发)

#### 1. 注册 PyPI 账号

访问 https://pypi.org/account/register/ 注册账号

#### 2. 配置 API Token

```bash
# 在 PyPI 网站生成 API token
# 创建配置文件
cat > ~/.pypirc << 'EOF'
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcC...你的token...
EOF

chmod 600 ~/.pypirc
```

#### 3. 上传到 TestPyPI (测试)

```bash
# 使用发布脚本
nu scripts/release.nu 0.1.0 --test-only

# 或手动上传
python -m twine upload --repository testpypi dist/*
```

#### 4. 从 TestPyPI 测试安装

```bash
# 创建新环境测试
python -m venv test_pypi_env
source test_pypi_env/bin/activate

# 从 TestPyPI 安装
pip install --index-url https://test.pypi.org/simple/ easyproxy

# 测试
easyproxy --version
easyproxy start

# 清理
deactivate
rm -rf test_pypi_env
```

#### 5. 上传到正式 PyPI

```bash
# 使用发布脚本
nu scripts/release.nu 0.1.0

# 或手动上传
python -m twine upload dist/*
```

#### 6. 用户安装

用户现在可以直接安装:
```bash
pip install easyproxy
easyproxy --version
```

### 方式 B: 通过文件共享 (内网/局域网)

#### 1. 复制分发包到共享位置

```bash
# 复制到共享目录
cp dist/*.whl /shared/packages/

# 或通过 HTTP 服务器分发
cd dist/
python -m http.server 8000
```

#### 2. 用户从共享位置安装

```bash
# 从本地文件安装
pip install /shared/packages/easyproxy-0.1.0-py3-none-any.whl

# 从 HTTP 服务器安装
pip install http://192.168.1.100:8000/easyproxy-0.1.0-py3-none-any.whl
```

### 方式 C: 通过 Git 仓库

#### 1. 推送到 Git 仓库

```bash
git add .
git commit -m "feat: add packaging support"
git push origin develop

# 创建版本标签
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```

#### 2. 用户从 Git 安装

```bash
# 从 GitHub 安装
pip install git+https://github.com/Slothtron/easyproxy-py.git

# 从指定分支安装
pip install git+https://github.com/Slothtron/easyproxy-py.git@develop

# 从指定标签安装
pip install git+https://github.com/Slothtron/easyproxy-py.git@v0.1.0
```

### 方式 D: 私有 PyPI 服务器

#### 使用 pypiserver

```bash
# 安装 pypiserver
pip install pypiserver

# 创建包目录
mkdir ~/pypi-packages
cp dist/*.whl ~/pypi-packages/

# 启动服务器
pypi-server run -p 8080 ~/pypi-packages
```

#### 用户安装

```bash
# 从私有服务器安装
pip install --index-url http://your-server:8080/simple/ easyproxy

# 或配置为默认源
pip config set global.index-url http://your-server:8080/simple/
pip install easyproxy
```

## 🎬 场景五: 版本更新

### 步骤 1: 更新代码

```bash
# 修改代码,添加新功能
# ...

# 更新版本号
# 编辑 pyproject.toml: version = "0.2.0"
# 编辑 easyproxy/cli.py: version="0.2.0"
```

### 步骤 2: 构建新版本

```bash
# 清理旧构建
nu Taskfile.nu clean

# 构建新版本
nu scripts/build.nu
```

### 步骤 3: 发布新版本

```bash
# 使用发布脚本 (自动更新版本号、构建、上传、打标签)
nu scripts/release.nu 0.2.0

# 或手动操作
python -m twine upload dist/*
git add .
git commit -m "chore: bump version to 0.2.0"
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin develop
git push origin v0.2.0
```

### 步骤 4: 用户升级

```bash
# 用户升级到新版本
pip install --upgrade easyproxy

# 或安装指定版本
pip install easyproxy==0.2.0
```

## 🎬 场景六: 卸载和清理

### 用户卸载

```bash
# 卸载包
pip uninstall easyproxy

# 清理缓存
pip cache purge
```

### 开发者清理

```bash
# 清理构建文件
nu Taskfile.nu clean

# 或手动清理
rm -rf dist/ build/ *.egg-info
rm -rf easyproxy/__pycache__
rm -rf venv/
```

## 📊 完整工作流程图

```
开发阶段:
  克隆项目 → 创建虚拟环境 → 开发模式安装 (pip install -e .)
     ↓
  修改代码 → 测试 → 提交代码
     ↓
构建阶段:
  更新版本号 → 清理旧构建 → 构建分发包 (python -m build)
     ↓
  检查包 (twine check) → 测试安装
     ↓
发布阶段:
  上传到 TestPyPI (测试) → 验证安装
     ↓
  上传到 PyPI (正式) → 创建 Git 标签 → 推送代码
     ↓
用户使用:
  pip install easyproxy → easyproxy start
```

## 💡 实用技巧

### 快速重新构建和测试

```bash
# 一键清理、构建、测试
nu Taskfile.nu clean && nu Taskfile.nu build && nu scripts/test-install.nu
```

### 查看已安装的包信息

```bash
# 查看包信息
pip show easyproxy

# 查看包文件列表
pip show -f easyproxy

# 查看依赖树
pip install pipdeptree
pipdeptree -p easyproxy
```

### 本地测试不同 Python 版本

```bash
# 使用 Python 3.11
python3.11 -m venv venv311
source venv311/bin/activate
pip install dist/*.whl
easyproxy --version
deactivate

# 使用 Python 3.12
python3.12 -m venv venv312
source venv312/bin/activate
pip install dist/*.whl
easyproxy --version
deactivate
```

### 调试安装问题

```bash
# 详细安装日志
pip install -v dist/*.whl

# 强制重新安装
pip install --force-reinstall dist/*.whl

# 不使用缓存
pip install --no-cache-dir dist/*.whl
```

## 🎯 总结

通过以上演示,您应该能够:

1. ✅ 在开发模式下安装和测试项目
2. ✅ 构建可分发的 wheel 和源码包
3. ✅ 测试安装流程
4. ✅ 选择合适的分发方式
5. ✅ 发布到 PyPI 或私有服务器
6. ✅ 管理版本更新

更多详细信息,请参考:
- **快速参考**: `QUICKSTART.md`
- **详细指南**: `docs/PACKAGING.md`
- **项目结构**: `docs/PROJECT_STRUCTURE.md`
