"""
集成测试：验证所有模块的导入功能
"""

import pytest
from my_python_project import get_project_logger, ConfigManager, validate_data


class TestCoreImports:
    """测试核心模块导入"""

    def test_core_imports(self):
        """测试核心模块导入"""
        from my_python_project import get_project_logger, ConfigManager, validate_data

        assert get_project_logger is not None
        assert ConfigManager is not None
        assert validate_data is not None


class TestValidatorImports:
    """测试验证器导入"""

    def test_validator_imports(self):
        """测试验证器导入"""
        from my_python_project import (
            StringValidator,
            NumberValidator,
            EmailValidator,
            DictValidator,
        )

        assert StringValidator is not None
        assert NumberValidator is not None
        assert EmailValidator is not None
        assert DictValidator is not None


class TestCacheImports:
    """测试缓存模块导入"""

    def test_cache_imports(self):
        """测试缓存模块导入"""
        from my_python_project import (
            MemoryCache,
            FileCache,
            MultiLevelCache,
            cache_result,
        )

        assert MemoryCache is not None
        assert FileCache is not None
        assert MultiLevelCache is not None
        assert cache_result is not None


class TestPerformanceImports:
    """测试性能监控导入"""

    def test_performance_imports(self):
        """测试性能监控导入"""
        from my_python_project import PerformanceMonitor, benchmark, timing_decorator

        assert PerformanceMonitor is not None
        assert benchmark is not None
        assert timing_decorator is not None


class TestPathManagementImports:
    """测试路径管理导入"""

    def test_path_management_imports(self):
        """测试路径管理导入"""
        from my_python_project import ProjectPathManager, init_project_paths

        assert ProjectPathManager is not None
        assert init_project_paths is not None


class TestExceptionImports:
    """测试异常处理导入"""

    def test_exception_imports(self):
        """测试异常处理导入"""
        from my_python_project import (
            BaseError,
            ConfigError,
            ValidationError,
            CacheError,
            handle_exceptions,
            ErrorHandler,
        )

        assert BaseError is not None
        assert ConfigError is not None
        assert ValidationError is not None
        assert CacheError is not None
        assert handle_exceptions is not None
        assert ErrorHandler is not None


class TestUtilitiesImports:
    """测试工具函数导入"""

    def test_utilities_imports(self):
        """测试工具函数导入"""
        from my_python_project import (
            now_timestamp,
            format_datetime,
            safe_filename,
            deep_merge,
            retry_on_failure,
            is_valid_email,
        )

        assert now_timestamp is not None
        assert format_datetime is not None
        assert safe_filename is not None
        assert deep_merge is not None
        assert retry_on_failure is not None
        assert is_valid_email is not None


class TestBasicFunctionality:
    """测试基本功能"""

    def test_basic_functionality(self):
        """测试基本功能是否正常工作"""
        from my_python_project import (
            get_project_logger,
            ConfigManager,
            StringValidator,
            MemoryCache,
        )

        # 测试日志
        logger = get_project_logger("test")
        logger.info("测试日志记录")

        # 测试配置管理
        config = ConfigManager()
        config.set("test.key", "test_value")
        assert config.get("test.key") == "test_value"

        # 测试验证器
        validator = StringValidator(min_length=2, max_length=10)
        result = validator.validate("test", "test_field")
        assert result == "test"

        with pytest.raises(Exception):  # 应该抛出验证错误
            validator.validate("a", "test_field")

        # 测试缓存
        cache = MemoryCache(max_size=10)
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"
