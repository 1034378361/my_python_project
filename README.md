# My Python Project

[![PyPI](https://img.shields.io/pypi/v/my_python_project.svg)](https://pypi.python.org/pypi/my_python_project)
[![文档](https://img.shields.io/badge/文档-GitHub_Pages-blue)](https://1034378361.github.io/my_python_project/)
[![代码覆盖率](https://codecov.io/gh/1034378361/my_python_project/branch/main/graph/badge.svg)](https://codecov.io/gh/1034378361/my_python_project)

现代Python项目模板，使用uv管理依赖和虚拟环境。

* 开源协议: MIT License
* 文档: [https://1034378361.github.io/my_python_project](https://1034378361.github.io/my_python_project)

## 特性

* 现代化Python包结构:
  * 使用`src`布局，提高包安全性
  * 完整的类型注解支持
  * 模块化设计，易于扩展

* 自动化测试与CI:
  * 基于pytest的测试框架
  * GitHub Actions持续集成
  * 自动测试、代码风格检查
  * 自动发布到PyPI

* 类型检查:
  * 严格的mypy类型验证
  * 类型覆盖率报告
  * 预配置的类型检查设置

* 命令行接口:
  * 基于Typer的命令行工具
  * 自动生成帮助文档
  * 命令补全支持
  * 友好的错误提示

* 代码质量工具:
  * 预配置的pre-commit钩子
  * 代码格式化(Black, isort)
  * 代码质量检查(Ruff)
  * 安全性检查(Bandit)

* 完整的开发工具链:
  * 可重现的开发环境
  * 一致的代码风格
  * 自动化文档生成
  * 版本管理工具

* Docker支持:
  * 优化的Dockerfile
  * Docker Compose配置
  * 多阶段构建流程
  * 生产环境就绪配置

## 快速开始

### 安装

#### 使用Docker

```bash
# 构建Docker镜像
docker-compose build

# 运行容器
docker-compose up -d
```

#### 手动安装

从PyPI安装:

```bash
# 使用pip
pip install my_python_project

# 使用uv（推荐）
uv add my_python_project

# 或者使用pip
pip install my_python_project
```

从源码安装:

```bash
# 克隆仓库
git clone https://github.com/1034378361/my_python_project.git
cd my_python_project

# 使用uv安装（推荐）
uv sync --all-extras --dev

# 或使用pip
pip install -e ".[dev]"
```

### 使用示例

```python
from my_python_project import example_function

# 使用示例
result = example_function()
print(result)
```

### 命令行使用

安装后，可以直接使用命令行工具:

```bash
# 显示帮助信息
my_python_project --help

# 运行主要功能
my_python_project run

# 查看版本
my_python_project --version
```

## 开发

### 环境设置

```bash
# 使用uv安装开发依赖（推荐）
uv sync --all-extras --dev

# 或使用pip
pip install -e ".[dev]"

# 安装pre-commit钩子
uv run pre-commit install

# 或者使用初始化脚本一键设置
python scripts/init.py
```

### 常用命令

```bash
# 运行测试
uv run pytest

# 生成测试覆盖率报告
uv run pytest --cov=my_python_project

# 代码格式化
make format  # 或 uv run ruff format

# 代码质量检查
make lint    # 或 uv run ruff check

# 类型检查
uv run mypy src

# 本地预览文档
make docs    # 或 uv run mkdocs serve

# 构建文档
uv run mkdocs build

# 构建分发包
make dist    # 或 uv build

# 发布到PyPI
make release # 或 uv publish
```

## 发布流程

项目使用setuptools_scm进行自动版本管理：

1. 确保代码已提交：`git add . && git commit -m "功能更新"`
2. 创建版本标签：`git tag v1.0.0`
3. 推送代码和标签：
   ```bash
   git push origin main
   git push origin v1.0.0
   ```

GitHub Actions将自动构建并发布到PyPI。

版本号会自动根据Git标签生成，无需手动修改版本文件。

## 📖 文档部署

项目文档会自动部署到GitHub Pages：

### 自动部署触发条件：
- 推送到 `main` 分支时
- 修改 `docs/` 目录或 `mkdocs.yml` 文件时
- 可手动触发部署

### 启用GitHub Pages：
1. 推送项目到GitHub后，进入仓库设置
2. 在 **Pages** 部分选择 **GitHub Actions** 作为源
3. 文档将自动部署到: `https://1034378361.github.io/my_python_project/`

### 本地预览：
```bash
# 安装文档依赖
uv sync --extra docs

# 启动本地服务器
uv run mkdocs serve
# 访问 http://127.0.0.1:8000
```

详细说明请参考: [docs/deployment.md](docs/deployment.md)

## 贡献指南

欢迎贡献！请查看[CONTRIBUTING.rst](CONTRIBUTING.rst)了解如何参与项目开发。

## 更新日志

查看[CHANGELOG.md](CHANGELOG.md)了解版本历史和更新内容。
