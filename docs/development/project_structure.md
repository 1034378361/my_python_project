# 项目结构概述

本文档提供了项目的目录结构和主要文件的概述，帮助您快速了解项目组织方式。

## 顶层目录结构

```
my_python_project/
├── .github/            # GitHub Actions工作流配置
├── config/             # 配置文件目录
│   ├── __init__.py     # 配置模块初始化
│   ├── logging_config.json # JSON格式日志配置
│   └── logging_config.yaml # YAML格式日志配置
├── docs/               # MkDocs项目文档
│   ├── getting-started/    # 入门指南
│   ├── user-guide/         # 用户指南
│   ├── advanced/           # 高级功能
│   ├── examples/           # 代码示例
│   ├── reference/          # API参考
│   └── development/        # 开发文档
├── scripts/            # 辅助脚本工具
├── src/                # 源代码目录
│   └── my_python_project/  # 主包
├── tests/              # 测试文件目录
├── .gitignore          # Git忽略文件
├── .pre-commit-config.yaml # Pre-commit配置
├── CHANGELOG.md        # 更新日志
├── CONTRIBUTING.md     # 贡献指南
├── LICENSE             # 开源许可证
├── Makefile            # 项目命令集合
├── mkdocs.yml          # MkDocs文档配置
├── pyproject.toml      # 项目配置和依赖管理
└── README.md           # 项目说明
```

## 核心组件

### 源代码 (`src/`)

源代码目录使用src布局，这是Python项目的推荐做法，有助于避免导入问题和测试隔离。

```
src/my_python_project/
├── __init__.py         # 包初始化和核心导出
├── _version.py         # 版本信息（由setuptools_scm生成）
├── app.py              # FastAPI应用主模块
├── cli.py              # 命令行界面实现
├── exceptions.py       # 自定义异常类定义
└── utils/              # 工具模块集合
    ├── __init__.py     # 工具模块导出
    ├── cache.py        # 缓存系统（内存/文件缓存）
    ├── common.py       # 通用工具函数
    ├── config_manager.py # 配置管理系统
    ├── lazy_import.py  # 懒加载导入工具
    ├── logging_utils.py # 高级日志处理
    ├── path_manager.py # 项目路径管理
    ├── performance.py  # 性能监控和分析
    └── validators.py   # 数据验证系统
```

### 测试 (`tests/`)

测试目录包含所有测试文件，使用pytest框架。

```
tests/
├── __init__.py
├── conftest.py         # 共享测试配置和fixtures
├── test_my_python_project.py  # 主模块测试
├── test_app.py         # FastAPI应用测试
├── test_cache.py       # 缓存系统测试
├── test_cli.py         # CLI功能测试
├── test_common.py      # 通用工具测试
├── test_config_manager.py # 配置管理测试
├── test_data_analysis.py  # 数据分析测试
├── test_exceptions.py  # 异常处理测试
├── test_integration.py # 集成测试
├── test_lazy_import.py # 懒加载测试
├── test_logging.py     # 日志系统测试
├── test_path_manager.py # 路径管理测试
├── test_performance.py # 性能监控测试
├── test_validators.py  # 数据验证测试
└── test_version.py     # 版本管理测试
```

### 文档 (`docs/`)

文档目录使用MkDocs生成项目文档，采用分层结构组织。

```
docs/
├── getting-started/    # 入门指南
│   ├── installation.md # 安装指南
│   └── quickstart.md   # 快速开始
├── user-guide/         # 用户指南
│   ├── config_management.md # 配置管理
│   └── logging.md      # 日志系统
├── advanced/           # 高级功能
│   ├── caching.md      # 缓存系统
│   ├── validation.md   # 数据验证
│   ├── performance_monitoring.md # 性能监控
│   └── integration_guide.md # 集成指南
├── examples/           # 代码示例
│   ├── basic-usage.md  # 基础使用
│   └── web-application.md # Web应用
├── reference/          # 参考文档
│   └── utilities.md    # 工具函数参考
├── development/        # 开发文档
│   ├── contributing.md # 贡献指南
│   ├── project_structure.md # 项目结构(本文档)
│   ├── version_management.md # 版本管理
│   └── docker.md       # Docker支持
├── index.md            # 文档首页
├── usage.md            # 基本使用指南
├── best_practices.md   # 最佳实践
├── faq.md              # 常见问题
└── path_management.md  # 路径管理文档
```

### 脚本 (`scripts/`)

辅助脚本目录包含各种自动化工具。

```
scripts/
├── __init__.py
├── docker.py           # Docker操作工具(跨平台)
├── generate_changelog.py  # 变更日志生成工具
└── init.sh             # 环境初始化脚本
```

### CI/CD配置 (`.github/`)

GitHub Actions工作流配置。

```
.github/
├── workflows/
│   ├── ci.yml          # 统一CI/CD工作流(测试、质量检查、发布)
│   └── dependabot.yml  # 依赖更新配置
└── ISSUE_TEMPLATE.md   # Issue模板
```

## 主要配置文件

### pyproject.toml

现代Python项目的核心配置文件，包含:

- 项目元数据和描述
- 依赖管理(核心依赖和开发依赖)
- 构建系统配置
- 开发工具配置:
  - Ruff: 代码质量检查和格式化
  - Mypy: 静态类型检查
  - Pytest: 测试配置
  - 覆盖率报告配置

### Makefile

提供跨平台的项目命令:

- `make help` - 显示可用命令
- `make test` - 运行测试
- `make lint` - 运行代码质量检查
- `make format` - 格式化代码
- `make docs` - 构建文档
- `make setup` - 运行安装脚本
- `make venv` - 创建虚拟环境
- `make docker-build` - 构建Docker镜像
- `make docker-run` - 运行Docker容器

### setup.py

跨平台安装脚本，功能包括:

- 自动检测操作系统
- 创建虚拟环境
- 安装项目依赖(基础或开发版本)
- 配置开发环境(git hooks等)
- 支持无提示模式，适用于CI环境

## Docker支持

项目内置Docker支持:

- `Dockerfile` - 定义容器环境
- `docker-compose.yml` - 定义服务配置
- `scripts/docker.py` - 跨平台Docker操作脚本

## 开发工具与流程

### 代码质量工具

- **Ruff**: 集成了多种工具功能，包括linting和格式化
- **Mypy**: 静态类型检查
- **Pre-commit**: Git提交钩子，确保代码质量

### 测试工具

- **Pytest**: 测试框架
- **Coverage**: 代码覆盖率报告
- **Tox**: 多环境测试

### 文档工具

- **MkDocs**: 文档生成
- **Material for MkDocs**: 主题
- **MkDocStrings**: API文档自动生成

### 发布流程

1. 更新版本号(`src/my_python_project/_version.py`)
2. 推送标签(`git tag vX.Y.Z`)
3. CI自动构建并发布到PyPI
4. 自动更新CHANGELOG并创建GitHub Release

## 最佳实践

- 使用虚拟环境隔离项目依赖
- 遵循代码风格指南
- 编写测试和文档
- 使用类型注解
- 遵循语义化版本控制
- 使用分支开发新功能
