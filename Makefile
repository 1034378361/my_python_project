# My Python Project Makefile
# 使用 uv 进行包管理

.PHONY: help install test lint format check-ci docs clean build

# 默认目标
help:
	@echo "Available commands:"
	@echo "  install     - 安装依赖"
	@echo "  test        - 运行测试"
	@echo "  lint        - 代码检查（自动修复）"
	@echo "  check-ci    - CI风格检查（不修复，与Actions一致）"
	@echo "  format      - 格式化代码"
	@echo "  docs        - 生成文档"
	@echo "  build       - 构建包"
	@echo "  clean       - 清理构建文件"

# 安装依赖
install:
	uv sync --extra full-dev

# 运行测试
test:
	uv run pytest --cov=my_python_project --cov-report=xml --cov-report=term

# 代码检查（自动修复）
lint:
	uv run ruff check . --fix
	uv run ruff format .
	uv run mypy src/ --ignore-missing-imports --explicit-package-bases

# CI风格检查（与GitHub Actions完全一致，不自动修复）
check-ci:
	uv run ruff check . --exit-non-zero-on-fix
	uv run ruff format --check .
	uv run mypy src --ignore-missing-imports --explicit-package-bases

# 格式化代码
format:
	uv run ruff format .

# 生成文档
docs:
	uv run mkdocs serve

# 构建包
build:
	uv build

# 清理构建文件
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete