# My Python Project

[![PyPI](https://img.shields.io/pypi/v/my_python_project.svg)](https://pypi.python.org/pypi/my_python_project)
[![测试状态](https://github.com/1034378361/my_python_project/actions/workflows/test.yml/badge.svg)](https://github.com/1034378361/my_python_project/actions/workflows/test.yml)
[![代码覆盖率](https://codecov.io/gh/1034378361/my_python_project/branch/main/graph/badge.svg)](https://codecov.io/gh/1034378361/my_python_project)

现代Python项目模板，使用uv管理依赖和虚拟环境。

## 🌟 特性亮点

- 🔧 **模块化设计**: 清晰的模块分类，易于使用和扩展
- ⚙️ **配置管理**: 支持多种格式的配置文件加载
- 📝 **日志系统**: 结构化日志记录和管理
- ✅ **数据验证**: 内置多种验证器，保证数据质量
- 💾 **缓存系统**: 灵活的缓存策略，提升性能
- 📊 **性能监控**: 全面的性能追踪和分析工具
- 🔨 **实用工具**: 丰富的工具函数库，覆盖常见需求

## 🚀 快速开始

### 1. 安装
```bash
pip install my_python_project
```

### 2. 基本使用
```python
from my_python_project import get_project_logger, ConfigManager

# 初始化日志
logger = get_project_logger(__name__)

# 配置管理
config = ConfigManager()
config.set("app.name", "My Python Project")

logger.info("应用启动成功")
```


### 3. 命令行使用
```bash
# 显示帮助信息
my_python_project --help

# 查看版本
my_python_project --version
```


## 📚 文档导航

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } **快速开始**

    ---

    5分钟内上手使用，了解核心功能

    [:octicons-arrow-right-24: 开始使用](getting-started/quickstart.md)

-   :material-book-open-page-variant:{ .lg .middle } **用户指南**

    ---

    详细的功能说明和使用方法

    [:octicons-arrow-right-24: 查看指南](user-guide/config_management.md)

-   :material-lightning-bolt:{ .lg .middle } **高级功能**

    ---

    性能优化、监控和集成指南

    [:octicons-arrow-right-24: 探索高级](advanced/caching.md)

-   :material-code-tags:{ .lg .middle } **示例代码**

    ---

    丰富的实际应用示例

    [:octicons-arrow-right-24: 查看示例](examples/basic-usage.md)

</div>

## 💡 核心功能

### 配置管理
支持 JSON、YAML、TOML 等多种配置格式，提供环境变量覆盖和配置验证功能。

### 日志系统  
结构化日志记录，支持多种输出格式和日志轮转，便于生产环境监控。

### 数据验证
内置字符串、数字、邮箱等常用验证器，支持自定义验证规则和组合验证。

### 缓存系统
提供内存缓存、文件缓存等多种缓存策略，支持TTL过期和自动清理。

### 性能监控
全面的性能追踪，包括函数执行时间、内存使用、系统指标等。

## 🔗 相关链接

- [📦 PyPI 包](https://pypi.org/project/my_python_project/)
- [💻 GitHub 仓库](https://github.com/1034378361/my_python_project)
- [📝 问题反馈](https://github.com/1034378361/my_python_project/issues)
- [💬 讨论社区](https://github.com/1034378361/my_python_project/discussions)

## 📄 许可证

MIT License