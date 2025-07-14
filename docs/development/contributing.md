# 开发指南

欢迎贡献！本文档将指导您如何参与 My Python Project 的开发。

## 🚀 快速开始

### 1. 准备环境
```bash
# 克隆仓库
git clone git@github.com:1034378361/my_python_project.git
cd my_python_project

# 初始化开发环境
python scripts/init.py

# 或手动使用uv
uv sync --dev

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows
```

### 2. 验证安装
```bash
# 运行测试确保环境正常
make test

# 检查代码质量
make lint
```

## 📋 开发工作流

### 分支管理
```bash
# 创建功能分支
git checkout -b feature/your-feature-name

# 或创建修复分支
git checkout -b fix/bug-description
```

### 开发循环
```bash
# 1. 编写代码
# 2. 运行测试
make test

# 3. 代码检查和格式化
make lint
make format

# 4. 提交代码
git add .
git commit -m "feat: 添加新功能"

# 5. 推送和创建PR
git push origin feature/your-feature-name
```

## 🎯 代码标准

### 代码风格
- **工具链**: Ruff (格式化 + 检查)
- **行长度**: 88字符
- **类型注解**: 必须使用类型提示
- **文档字符串**: 公共API必须有docstring

### 测试要求
- **覆盖率**: > 85%
- **测试框架**: pytest
- **测试类型**: 单元测试 + 集成测试
- **命名**: `test_*.py` 或 `*_test.py`

### 提交规范
遵循[约定式提交](https://www.conventionalcommits.org/)：

```bash
# 功能
git commit -m "feat: 添加配置管理模块"

# 修复
git commit -m "fix: 修复缓存清理bug"

# 文档
git commit -m "docs: 更新API文档"

# 测试
git commit -m "test: 添加用户验证测试"

# 重构
git commit -m "refactor: 优化性能监控代码"
```

## 🏗️ 项目架构

```
my_python_project/
├── src/my_python_project/
│   ├── __init__.py              # 模块入口
│   ├── app.py                   # 应用主入口
│   ├── cli.py                   # 命令行接口
│   ├── utils/                   # 工具模块
│   │   ├── config_manager.py    # 配置管理
│   │   ├── logging_utils.py     # 日志工具
│   │   └── validators.py        # 数据验证
│   └── exceptions.py            # 异常定义
├── tests/                       # 测试文件
├── docs/                        # 文档
├── scripts/                     # 工具脚本
└── pyproject.toml              # 项目配置
```

## 🔧 开发工具

### Make 命令
```bash
make help        # 显示所有可用命令
make test        # 运行测试
make lint        # 代码检查
make format      # 格式化代码
make docs        # 生成文档
make clean       # 清理缓存
make install     # 安装依赖
```

### 手动命令
```bash
# 运行特定测试
uv run pytest tests/test_config.py -v

# 运行带覆盖率的测试
uv run pytest --cov=my_python_project --cov-report=html

# 类型检查
uv run mypy src/my_python_project

# 代码格式化
uv run ruff format .

# 代码检查
uv run ruff check .
```

## 📚 文档开发

### 文档结构
```
docs/
├── getting-started/     # 入门指南
├── user-guide/         # 用户指南
├── advanced/           # 高级功能
├── examples/           # 示例代码
├── reference/          # 参考文档
└── development/        # 开发文档
```

### 文档规范
- 使用Markdown格式
- 每个模块都需要文档
- 提供完整的代码示例
- 包含错误处理示例

## 🧪 测试策略

### 测试分类
1. **单元测试**: 测试单个函数/类
2. **集成测试**: 测试模块间交互
3. **性能测试**: 测试性能指标
4. **回归测试**: 确保修复不破坏现有功能

### 测试最佳实践
```python
# 使用清晰的测试名称
def test_config_manager_loads_yaml_file_successfully():
    pass

# 使用fixture共享测试数据
@pytest.fixture
def sample_config():
    return {"app": {"name": "test"}}

# 测试异常情况
def test_validator_raises_error_for_invalid_email():
    with pytest.raises(ValidationError):
        validate_email("invalid-email")
```

## 🚢 发布流程

### 版本管理
- 使用[语义化版本](https://semver.org/)
- 版本号通过Git标签自动管理
- 使用setuptools_scm自动生成版本

### 发布步骤
1. 确保所有测试通过
2. 更新CHANGELOG.md
3. 创建Git标签: `git tag v1.0.0`
4. 推送标签: `git push origin v1.0.0`
5. GitHub Actions自动构建和发布

## ❓ 常见问题

### Q: 如何添加新的依赖？
A: 在 `pyproject.toml` 中添加，然后运行 `uv sync`

### Q: 如何运行特定测试？
A: 使用 `uv run pytest tests/test_specific.py::test_function`

### Q: 代码检查失败怎么办？
A: 运行 `make format` 自动修复格式问题，然后运行 `make lint` 检查

### Q: 如何调试测试？
A: 使用 `uv run pytest --pdb` 进入调试模式

### Q: 如何添加新的工具模块？
A: 在 `src/my_python_project/utils/` 下添加，并在 `__init__.py` 中导出

## 📞 获取帮助

- 🐛 报告Bug: [GitHub Issues](https://github.com/1034378361/my_python_project/issues)
- 💡 功能请求: [GitHub Discussions](https://github.com/1034378361/my_python_project/discussions)
- 📖 文档问题: 直接提交PR或创建Issue

**感谢您的贡献！每一个PR都让项目变得更好。** 🙏