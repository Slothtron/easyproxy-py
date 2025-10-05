# EasyProxy Justfile
# 使用方法: just <recipe>
# 查看所有命令: just --list

# 默认配置
python := "python"
pip := "pip"

# 显示所有可用命令
default:
    @just --list

# 构建分发包
build:
    @echo "🔨 构建分发包..."
    @just clean
    @{{python}} -m pip install --upgrade pip setuptools wheel build twine
    @{{python}} -m build
    @echo "✓ 构建完成"
    @echo ""
    @echo "📋 生成的文件:"
    @ls -lh dist/
    @echo ""
    @echo "🔍 检查包完整性..."
    @{{python}} -m twine check dist/*
    @echo "✅ 构建成功!"

# 清理构建文件
clean:
    @echo "🧹 清理构建文件..."
    @rm -rf dist/ build/ *.egg-info easyproxy/__pycache__ 2>/dev/null || true
    @echo "✓ 清理完成"

# 开发模式安装
dev:
    @echo "🔧 开发模式安装..."
    @{{pip}} install -e .
    @echo "✅ 开发模式安装完成!"
    @{{python}} -m easyproxy --version

# 本地安装 (从源码)
install:
    @echo "📥 安装 EasyProxy (从源码)..."
    @{{pip}} install .
    @echo "✅ 安装完成!"
    @{{python}} -m easyproxy --version

# 从 dist 目录安装 (wheel 包)
install-dist:
    @echo "📥 从 dist/ 安装 EasyProxy..."
    @if [ ! -d "dist" ]; then \
        echo "❌ dist/ 目录不存在,请先运行: just build"; \
        exit 1; \
    fi
    @{{pip}} install dist/*.whl
    @echo "✅ 安装完成!"
    @easyproxy --version

# 测试安装
test-install:
    @echo "🧪 测试 EasyProxy 安装..."
    @echo ""
    @echo "📦 创建测试虚拟环境: test_venv"
    @{{python}} -m venv test_venv
    @echo "✓ 虚拟环境创建完成"
    @echo ""
    @echo "📥 安装 EasyProxy..."
    @test_venv/bin/pip install dist/*.whl
    @echo "✓ 安装完成"
    @echo ""
    @echo "🔍 测试命令..."
    @echo "  测试: easyproxy --version"
    @test_venv/bin/easyproxy --version
    @echo ""
    @echo "  测试: easyproxy --help"
    @test_venv/bin/easyproxy --help | head -10
    @echo ""
    @echo "🧹 清理测试环境..."
    @rm -rf test_venv
    @echo "✓ 清理完成"
    @echo ""
    @echo "✅ 测试成功!"

# 检查代码质量
check:
    @echo "🔍 检查代码质量..."
    @echo ""
    @echo "检查包配置..."
    @{{python}} -c "import tomllib; f=open('pyproject.toml','rb'); tomllib.load(f); print('✓ pyproject.toml 语法正确')"
    @echo ""
    @if [ -d "dist" ]; then \
        echo "检查分发包..."; \
        {{python}} -m twine check dist/*; \
    else \
        echo "⚠️  dist/ 目录不存在,请先运行: just build"; \
    fi
    @echo ""
    @echo "✅ 检查完成!"

# 运行代理服务器
run *ARGS:
    @echo "🚀 启动 EasyProxy 代理服务器..."
    @echo ""
    @{{python}} -m easyproxy start {{ARGS}}

# 生成配置文件
init OUTPUT="config.yaml":
    @echo "📝 生成配置文件: {{OUTPUT}}"
    @{{python}} -m easyproxy init {{OUTPUT}}

# 验证配置文件
validate CONFIG:
    @echo "🔍 验证配置文件: {{CONFIG}}"
    @{{python}} -m easyproxy validate -c {{CONFIG}}

# 上传到 TestPyPI (测试环境)
upload-test:
    @echo "📤 上传到 TestPyPI..."
    @{{python}} -m twine upload --repository testpypi dist/*
    @echo ""
    @echo "✅ 已上传到 TestPyPI!"
    @echo ""
    @echo "测试安装:"
    @echo "  pip install --index-url https://test.pypi.org/simple/ easyproxy"

# 上传到 PyPI (正式环境)
upload:
    @echo "⚠️  即将上传到正式 PyPI"
    @echo -n "确认上传? (y/N): " && read ans && [ $${ans:-N} = y ]
    @echo ""
    @echo "📤 上传到 PyPI..."
    @{{python}} -m twine upload dist/*
    @echo ""
    @echo "✅ 上传成功!"

# 发布新版本
release VERSION:
    @echo "🚀 准备发布 EasyProxy v{{VERSION}}..."
    @echo ""
    @echo "🔍 检查 Git 状态..."
    @if [ -n "$$(git status --porcelain)" ]; then \
        echo "⚠️  警告: 工作目录有未提交的更改"; \
        echo -n "是否继续? (y/N): "; \
        read ans; \
        [ "$${ans:-N}" = "y" ] || (echo "❌ 发布已取消" && exit 1); \
    fi
    @echo ""
    @echo "📝 更新版本号到 {{VERSION}}..."
    @sed -i 's/version = ".*"/version = "{{VERSION}}"/' pyproject.toml
    @sed -i 's/version=".*"/version="{{VERSION}}"/' easyproxy/cli.py
    @echo "  ✓ pyproject.toml"
    @echo "  ✓ easyproxy/cli.py"
    @echo ""
    @just build
    @echo ""
    @echo "🏷️  创建 Git 提交和标签..."
    @git add pyproject.toml easyproxy/cli.py
    @git commit -m "chore: bump version to {{VERSION}}"
    @git tag -a "v{{VERSION}}" -m "Release version {{VERSION}}"
    @echo ""
    @echo "✅ 发布准备完成!"
    @echo ""
    @echo "📝 后续步骤:"
    @echo "  1. 上传测试: just upload-test"
    @echo "  2. 上传正式: just upload"
    @echo "  3. 推送代码: git push origin develop"
    @echo "  4. 推送标签: git push origin v{{VERSION}}"

# 安装开发依赖
install-dev:
    @echo "📦 安装开发依赖..."
    @{{pip}} install -e ".[dev]"
    @echo "✅ 开发依赖安装完成!"

# 显示项目信息
info:
    @echo "📊 EasyProxy 项目信息"
    @echo ""
    @{{python}} --version | xargs -I {} echo "Python: {}"
    @{{pip}} --version | cut -d' ' -f1-2 | xargs -I {} echo "Pip: {}"
    @echo ""
    @grep 'version = ' pyproject.toml | head -1 | cut -d'"' -f2 | xargs -I {} echo "项目版本: {}"
    @git branch --show-current 2>/dev/null | xargs -I {} echo "Git 分支: {}" || echo "Git 分支: N/A"
    @git remote get-url origin 2>/dev/null | xargs -I {} echo "Git 远程: {}" || echo "Git 远程: N/A"
    @echo ""
    @if [ -d "dist" ]; then \
        echo "构建产物:"; \
        ls -lh dist/; \
    else \
        echo "构建产物: 无 (运行 'just build' 构建)"; \
    fi

# 卸载
uninstall:
    @echo "🗑️  卸载 EasyProxy..."
    @{{pip}} uninstall -y easyproxy
    @echo "✅ 卸载完成!"

# 帮助信息
help:
    @echo "📋 EasyProxy Justfile 使用指南"
    @echo ""
    @echo "常用命令:"
    @echo "  just dev           - 开发模式安装"
    @echo "  just build         - 构建分发包"
    @echo "  just install-dist  - 从 dist/ 安装"
    @echo "  just test-install  - 测试安装"
    @echo "  just run           - 运行代理服务器"
    @echo "  just clean         - 清理构建文件"
    @echo ""
    @echo "发布命令:"
    @echo "  just release 0.2.0  - 发布新版本"
    @echo "  just upload-test    - 上传到 TestPyPI"
    @echo "  just upload         - 上传到 PyPI"
    @echo ""
    @echo "其他命令:"
    @echo "  just check        - 检查代码质量"
    @echo "  just info         - 显示项目信息"
    @echo "  just --list       - 显示所有命令"
    @echo ""
    @echo "示例:"
    @echo "  just dev                    # 开发模式安装"
    @echo "  just run -p 8080            # 在端口 8080 运行"
    @echo "  just init my-config.yaml    # 生成配置文件"
    @echo "  just release 0.2.0          # 发布版本 0.2.0"
