# EasyProxy 二进制打包指南

本文档介绍如何将 EasyProxy 打包成独立的可执行文件,无需 Python 环境即可运行。

---

## 📦 为什么需要二进制打包?

**优点:**
- ✅ **无需 Python 环境** - 可以在没有 Python 的系统上运行
- ✅ **路径独立** - 不依赖特定的 Python 安装路径
- ✅ **部署简单** - 单个文件,复制即用
- ✅ **版本隔离** - 不受系统 Python 版本影响
- ✅ **systemd 友好** - 固定路径,易于配置

**缺点:**
- ⚠️ 文件较大 (约 20-50MB)
- ⚠️ 启动稍慢 (首次解压需要时间)
- ⚠️ 需要为每个平台单独打包

---

## 🛠️ 打包工具对比

| 工具 | 文件大小 | 启动速度 | 易用性 | 推荐度 |
|------|---------|---------|--------|--------|
| **PyInstaller** | 中等 (20-40MB) | 快 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Nuitka** | 小 (10-20MB) | 最快 | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **cx_Freeze** | 中等 | 快 | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **PyOxidizer** | 小 | 快 | ⭐⭐ | ⭐⭐⭐ |

---

## 🚀 方案一: PyInstaller (推荐)

### 快速开始

```bash
# 方式一: 使用 Just (推荐)
just build-bin           # 打包二进制
just install-bin         # 安装到系统
just deep-clean          # 清理所有产物 (可选)

# 方式二: 手动执行
cd scripts
./build_binary.sh        # 打包
sudo cp ../dist/easyproxy /usr/bin/
./clean_build.sh         # 清理 (可选)
```

**说明:**
- `just build-bin` 会自动清理 `build/` 和 `*.spec` 文件
- 只保留 `dist/easyproxy` 可执行文件
- `just deep-clean` 清理所有产物(包括 `dist/`)

### 手动打包

```bash
# 单文件模式 (推荐)
pyinstaller --onefile \
    --name easyproxy \
    --hidden-import easyproxy.cli \
    --hidden-import easyproxy.config \
    --hidden-import easyproxy.proxy \
    --hidden-import easyproxy.auth \
    --hidden-import easyproxy.logger \
    easyproxy/__main__.py

# 目录模式 (更快)
pyinstaller --onedir \
    --name easyproxy \
    easyproxy/__main__.py
```

### 高级选项

```bash
# 优化大小 (使用 UPX 压缩)
pyinstaller --onefile --upx-dir=/usr/bin easyproxy/__main__.py

# 去除调试信息
pyinstaller --onefile --strip easyproxy/__main__.py

# 添加图标 (Windows/macOS)
pyinstaller --onefile --icon=icon.ico easyproxy/__main__.py

# 隐藏控制台窗口 (Windows)
pyinstaller --onefile --noconsole easyproxy/__main__.py
```

---

## 🔧 方案二: Nuitka (最快)

Nuitka 将 Python 代码编译成 C 代码,性能最好。

### 安装和使用

```bash
# 1. 安装 Nuitka
pip install nuitka

# 2. 编译
python -m nuitka \
    --standalone \
    --onefile \
    --output-dir=dist \
    --output-filename=easyproxy \
    easyproxy/__main__.py

# 3. 测试
./dist/easyproxy --version
```

### 优化选项

```bash
# 启用所有优化
python -m nuitka \
    --standalone \
    --onefile \
    --lto=yes \
    --remove-output \
    easyproxy/__main__.py
```

---

## 📋 systemd 集成

打包后的二进制文件可以直接用于 systemd:

### 1. 安装二进制文件

```bash
# 复制到系统路径
sudo cp dist/easyproxy /usr/bin/easyproxy
sudo chmod +x /usr/bin/easyproxy

# 验证
/usr/bin/easyproxy --version
```

### 2. 更新 systemd 服务文件

`/etc/systemd/system/easyproxy.service`:

```ini
[Service]
# 使用二进制文件,路径固定
ExecStart=/usr/bin/easyproxy start -c /etc/easyproxy/config.yaml --log-file /var/log/easyproxy/easyproxy.log
```

### 3. 重启服务

```bash
sudo systemctl daemon-reload
sudo systemctl restart easyproxy
sudo systemctl status easyproxy
```

---

## 🐳 Docker 集成

也可以在 Docker 镜像中使用二进制文件:

```dockerfile
# 多阶段构建
FROM python:3.11-slim as builder

WORKDIR /build
COPY . .

# 安装 PyInstaller 并打包
RUN pip install pyinstaller && \
    pyinstaller --onefile --name easyproxy easyproxy/__main__.py

# 运行阶段 (更小的基础镜像)
FROM debian:bookworm-slim

# 只复制二进制文件
COPY --from=builder /build/dist/easyproxy /usr/local/bin/

# 创建用户和目录
RUN useradd -r -s /bin/false easyproxy && \
    mkdir -p /etc/easyproxy /var/log/easyproxy && \
    chown -R easyproxy:easyproxy /etc/easyproxy /var/log/easyproxy

USER easyproxy
ENTRYPOINT ["easyproxy"]
CMD ["start", "-c", "/etc/easyproxy/config.yaml"]
```

**优点:**
- 镜像更小 (从 ~200MB 降到 ~100MB)
- 不需要 Python 运行时
- 启动更快

---

## 🔍 故障排查

### 问题 1: 找不到模块

**错误:**
```
ModuleNotFoundError: No module named 'xxx'
```

**解决:**
```bash
# 添加隐藏导入
pyinstaller --onefile \
    --hidden-import xxx \
    easyproxy/__main__.py
```

### 问题 2: 文件过大

**解决:**
```bash
# 1. 使用 UPX 压缩
pyinstaller --onefile --upx-dir=/usr/bin easyproxy/__main__.py

# 2. 排除不需要的模块
pyinstaller --onefile \
    --exclude-module pytest \
    --exclude-module setuptools \
    easyproxy/__main__.py

# 3. 使用 Nuitka (更小)
python -m nuitka --standalone --onefile easyproxy/__main__.py
```

### 问题 3: 启动慢

**原因:** PyInstaller 需要解压临时文件

**解决:**
```bash
# 使用目录模式 (不是单文件)
pyinstaller --onedir easyproxy/__main__.py

# 或使用 Nuitka (编译成原生代码)
python -m nuitka --standalone --onefile easyproxy/__main__.py
```

### 问题 4: 权限问题

**错误:**
```
Permission denied: '/usr/bin/easyproxy'
```

**解决:**
```bash
sudo chmod +x /usr/bin/easyproxy
sudo chown root:root /usr/bin/easyproxy
```

---

## 📊 性能对比

| 方式 | 文件大小 | 启动时间 | 运行性能 |
|------|---------|---------|---------|
| **Python 脚本** | ~10KB | 快 (50ms) | 基准 |
| **PyInstaller** | ~30MB | 中等 (200ms) | 99% |
| **Nuitka** | ~15MB | 快 (80ms) | 105% |
| **Docker** | ~200MB | 慢 (1s) | 98% |

---

## 🎯 推荐方案

### 生产环境 (Linux 服务器)

**推荐: PyInstaller 单文件**

```bash
# 使用 Just (推荐)
just build-bin
just install-bin
just setup-service

# 或手动执行
cd scripts
./build_binary.sh
cd ..
sudo cp dist/easyproxy /usr/bin/
sudo systemctl restart easyproxy
```

**理由:**
- 部署简单,单个文件
- 无需 Python 环境
- systemd 配置固定路径
- 易于版本管理

### 开发环境

**推荐: pip 安装 (可编辑模式)**

```bash
pip install -e .
```

**理由:**
- 修改代码立即生效
- 无需重新打包
- 调试方便

### 容器化部署

**推荐: Docker 多阶段构建 + 二进制**

```dockerfile
FROM python:3.11-slim as builder
RUN pip install pyinstaller
COPY . .
RUN pyinstaller --onefile easyproxy/__main__.py

FROM debian:bookworm-slim
COPY --from=builder /build/dist/easyproxy /usr/local/bin/
```

**理由:**
- 镜像最小化
- 安全性更好
- 启动更快

---

## 📚 参考资料

- [PyInstaller 文档](https://pyinstaller.org/)
- [Nuitka 文档](https://nuitka.net/)
- [Python 打包最佳实践](https://packaging.python.org/)

---

## 🔄 自动化打包

可以集成到 CI/CD 流程:

```yaml
# .github/workflows/build.yml
name: Build Binary

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pyinstaller
          pip install -r requirements.txt
      
      - name: Build binary
        run: ./build_binary.sh
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: easyproxy-linux-amd64
          path: dist/easyproxy
```

---

**建议:** 对于 systemd 部署,使用 PyInstaller 打包成二进制文件是最佳方案! 🚀
