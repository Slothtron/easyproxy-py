# EasyProxy Makefile
# 使用方法: make <target>
# 查看所有命令: make help

.DEFAULT_GOAL := help
PYTHON := python
PIP := pip

# =============================================================================
# 帮助信息
# =============================================================================

.PHONY: help
help: ## 显示帮助信息
	@echo "EasyProxy Makefile"
	@echo ""
	@echo "开发命令:"
	@echo "  make dev     - 开发模式安装"
	@echo "  make run     - 运行代理服务器"
	@echo "  make clean   - 清理构建文件"
	@echo ""
	@echo "构建命令:"
	@echo "  make build   - 构建分发包"
	@echo ""
	@echo "发布命令:"
	@echo "  make release VERSION=x.x.x  - 发布新版本"
	@echo ""
	@echo "示例:"
	@echo "  make dev"
	@echo "  make run ARGS='-p 8080'"
	@echo "  make release VERSION=0.3.0"

# =============================================================================
# 开发命令
# =============================================================================

.PHONY: dev
dev: ## 开发模式安装
	$(PIP) install -e ".[dev]"
	@echo "开发模式安装完成"

.PHONY: run
run: ## 运行代理服务器
	$(PYTHON) -m easyproxy start $(ARGS)

.PHONY: clean
clean: ## 清理构建文件
	@rm -rf dist/ build/ *.egg-info __pycache__ 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "清理完成"

# =============================================================================
# 构建命令
# =============================================================================

.PHONY: build
build: clean ## 构建分发包
	$(PYTHON) -m pip install --upgrade build twine
	$(PYTHON) -m build
	$(PYTHON) -m twine check dist/*
	@echo "构建完成"

# =============================================================================
# 发布命令
# =============================================================================

.PHONY: release
release: ## 发布新版本
	@test -n "$(VERSION)" || (echo "错误: 请指定版本号 (make release VERSION=x.x.x)" && exit 1)
	@sed -i 's/version = ".*"/version = "$(VERSION)"/' pyproject.toml
	@sed -i 's/version=".*"/version="$(VERSION)"/' easyproxy/cli.py
	@$(MAKE) build
	@git add pyproject.toml easyproxy/cli.py
	@git commit -m "chore: bump version to $(VERSION)"
	@git tag -a "v$(VERSION)" -m "Release version $(VERSION)"
	@echo ""
	@echo "发布准备完成! 后续步骤:"
	@echo "  git push origin develop"
	@echo "  git push origin v$(VERSION)"
	@echo "  python -m twine upload dist/*"