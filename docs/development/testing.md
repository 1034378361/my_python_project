# 测试指南

本项目采用pytest作为测试框架，提供了完整的测试覆盖和多种测试类型。

## 📋 测试结构

```
tests/
├── __init__.py                    # 测试包初始化
├── conftest.py                    # pytest配置和fixtures
├── test_*.py                      # 单元测试
├── test_imports_integration.py   # 导入集成测试
├── test_module_functionality.py  # 模块功能集成测试
└── test_integration.py           # 完整集成测试
```

## 🔧 测试类型

### 单元测试
针对单个模块或函数的测试：

- `test_cache.py` - 缓存系统测试
- `test_config_manager.py` - 配置管理测试
- `test_validators.py` - 数据验证测试
- `test_exceptions.py` - 异常处理测试
- `test_logging.py` - 日志系统测试
- `test_performance.py` - 性能监控测试
- `test_common.py` - 工具函数测试
- `test_path_manager.py` - 路径管理测试
- `test_lazy_import.py` - 懒加载测试

### 集成测试
测试模块间的协作：

- `test_imports_integration.py` - 验证所有模块能正确导入
- `test_module_functionality.py` - 验证模块功能正常工作
- `test_integration.py` - 端到端集成测试

### 应用测试
测试应用程序入口点：

- `test_app.py` - 主应用模块测试
- `test_cli.py` - 命令行接口测试
- `test_data_analysis.py` - 数据分析模块测试

## 🚀 运行测试

### 基本命令

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_cache.py

# 运行特定测试类
pytest tests/test_cache.py::TestMemoryCache

# 运行特定测试方法
pytest tests/test_cache.py::TestMemoryCache::test_basic_operations
```

### 测试选项

```bash
# 显示详细输出
pytest -v

# 显示测试覆盖率
pytest --cov=my_python_project

# 生成HTML覆盖率报告
pytest --cov=my_python_project --cov-report=html

# 并行运行测试（需要pytest-xdist）
pytest -n auto

# 只运行失败的测试
pytest --lf

# 停止在第一个失败的测试
pytest -x
```

### 测试标记

项目使用pytest标记来分类测试：

```bash
# 运行快速测试
pytest -m "not slow"

# 运行集成测试
pytest -m integration

# 运行性能测试
pytest -m performance
```

## 📊 测试覆盖率

目标：保持95%以上的测试覆盖率

### 检查覆盖率

```bash
# 生成覆盖率报告
pytest --cov=my_python_project --cov-report=term-missing

# 生成HTML报告（在htmlcov/目录）
pytest --cov=my_python_project --cov-report=html

# 生成XML报告（用于CI）
pytest --cov=my_python_project --cov-report=xml
```

### 覆盖率配置

在 `pyproject.toml` 中配置覆盖率选项：

```toml
[tool.coverage.run]
source = ["src/my_python_project"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
    "*/site-packages/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError"
]
```

## 🏗️ 编写测试

### 测试结构

```python
"""
测试模块的描述
"""
import pytest
from my_python_project import ModuleToTest


class TestModuleClass:
    """测试类的描述"""
    
    def setup_method(self):
        """每个测试方法前的准备"""
        self.instance = ModuleToTest()
    
    def test_basic_functionality(self):
        """测试基本功能"""
        result = self.instance.some_method()
        assert result == expected_value
    
    def test_error_handling(self):
        """测试错误处理"""
        with pytest.raises(ExpectedException):
            self.instance.failing_method()
```

### 使用Fixtures

在 `conftest.py` 中定义的fixtures：

```python
def test_with_config(sample_config):
    """使用配置fixture的测试"""
    assert sample_config.get("test.key") == "test_value"

def test_with_cache(memory_cache):
    """使用缓存fixture的测试"""
    memory_cache.set("key", "value")
    assert memory_cache.get("key") == "value"
```

### 参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    ("test@example.com", True),
    ("invalid-email", False),
    ("", False),
])
def test_email_validation(input, expected):
    """参数化的邮箱验证测试"""
    validator = EmailValidator()
    result = validator.is_valid(input)
    assert result == expected
```

## 🔍 测试最佳实践

### 1. 测试命名
- 使用描述性的测试名称
- 格式：`test_<action>_<expected_result>`
- 例：`test_cache_set_returns_true_on_success`

### 2. 测试组织
- 一个测试文件对应一个模块
- 使用测试类组织相关测试
- 保持测试的独立性

### 3. 断言
- 使用明确的断言
- 提供有意义的错误消息
- 优先使用pytest的高级断言

### 4. 测试数据
- 使用fixtures管理测试数据
- 避免硬编码的测试数据
- 使用临时文件和目录

### 5. 异常测试
```python
# 好的异常测试
def test_config_raises_error_for_missing_file():
    with pytest.raises(ConfigError, match="File not found"):
        ConfigManager.from_file("nonexistent.json")

# 避免这样
def test_config_error():
    try:
        ConfigManager.from_file("nonexistent.json")
        assert False, "Should have raised error"
    except ConfigError:
        pass
```

## 🔧 调试测试

### 添加调试信息

```python
def test_with_debug():
    """带调试信息的测试"""
    result = complex_function()
    print(f"Debug: result = {result}")  # 使用 -s 标志查看
    assert result == expected
```

### 运行调试

```bash
# 显示print输出
pytest -s

# 进入调试器
pytest --pdb

# 在失败时进入调试器
pytest --pdb --tb=short
```

## 📈 持续集成

### GitHub Actions
项目配置了自动测试流程：

```yaml
- name: Run tests
  run: |
    pytest --cov=my_python_project --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
```

### 本地预提交检查

```bash
# 运行所有检查（包括测试）
make test

# 或手动运行
pytest --cov=my_python_project --cov-fail-under=95
```

## 🎯 测试策略

### 测试金字塔
- **70%** 单元测试：快速、隔离的测试
- **20%** 集成测试：测试模块间交互
- **10%** 端到端测试：完整功能测试

### 关键测试点
1. **公共API**：所有对外暴露的接口
2. **边界条件**：空值、极值、异常情况
3. **错误处理**：异常路径和恢复机制
4. **性能关键**：缓存、数据库操作等
5. **配置敏感**：依赖配置的功能

## 📚 相关资源

- [pytest文档](https://docs.pytest.org/)
- [pytest-cov文档](https://pytest-cov.readthedocs.io/)
- [测试最佳实践](https://docs.python-guide.org/writing/tests/)
- [Python测试指南](https://realpython.com/python-testing/)