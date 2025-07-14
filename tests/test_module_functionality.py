"""
模块功能集成测试 - 验证所有模块的基本功能
"""

import pytest
import tempfile
import os
import time


class TestLoggingFunctionality:
    """测试日志功能"""

    def test_logging(self):
        """测试日志功能"""
        from my_python_project import get_project_logger

        logger = get_project_logger("test")
        logger.info("测试日志记录")
        logger.warning("测试警告信息")
        # 如果没有异常，说明日志功能正常


class TestConfigFunctionality:
    """测试配置管理"""

    def test_config(self):
        """测试配置管理"""
        from my_python_project import ConfigManager

        config = ConfigManager()
        config.set("test.key", "test_value")
        value = config.get("test.key")
        assert value == "test_value"

        # 测试默认值
        default_value = config.get("nonexistent.key", "default")
        assert default_value == "default"


class TestValidatorsFunctionality:
    """测试验证器"""

    def test_validators(self):
        """测试验证器"""
        from my_python_project import StringValidator, EmailValidator, NumberValidator

        # 字符串验证器
        str_validator = StringValidator(min_length=2, max_length=10)
        result = str_validator.validate("test", "test_field")
        assert result == "test"

        with pytest.raises(Exception):
            str_validator.validate("a", "test_field")

        with pytest.raises(Exception):
            str_validator.validate("a" * 20, "test_field")

        # 邮箱验证器
        email_validator = EmailValidator()
        result = email_validator.validate("test@example.com", "email_field")
        assert result == "test@example.com"

        with pytest.raises(Exception):
            email_validator.validate("invalid-email", "email_field")

        # 数字验证器
        num_validator = NumberValidator(number_type=int, min_value=0, max_value=100)
        result = num_validator.validate(50, "num_field")
        assert result == 50

        with pytest.raises(Exception):
            num_validator.validate(-1, "num_field")

        with pytest.raises(Exception):
            num_validator.validate(101, "num_field")


class TestCacheFunctionality:
    """测试缓存功能"""

    def test_cache(self):
        """测试缓存功能"""
        from my_python_project import MemoryCache, cache_result

        # 测试内存缓存
        cache = MemoryCache(max_size=10)
        cache.set("test_key", "test_value")
        value = cache.get("test_key")
        assert value == "test_value"

        # 测试缓存装饰器
        call_count = 0

        @cache_result(ttl=10)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = expensive_function(5)
        result2 = expensive_function(5)
        assert result1 == result2 == 10
        assert call_count == 1


class TestUtilsFunctionality:
    """测试工具函数"""

    def test_utils(self):
        """测试工具函数"""
        from my_python_project import (
            format_datetime,
            safe_filename,
            deep_merge,
            now_timestamp,
        )

        # 测试时间函数
        timestamp = now_timestamp()
        assert isinstance(timestamp, int)

        datetime_str = format_datetime()
        assert isinstance(datetime_str, str)

        # 测试文件名安全化
        safe_name = safe_filename("test/file.txt")
        assert "/" not in safe_name

        # 测试字典合并
        dict1 = {"a": {"b": 1}}
        dict2 = {"a": {"c": 2}}
        merged = deep_merge(dict1, dict2)
        assert merged["a"]["b"] == 1
        assert merged["a"]["c"] == 2


class TestPathManagerFunctionality:
    """测试路径管理"""

    def test_path_manager(self):
        """测试路径管理"""
        from my_python_project import ProjectPathManager, init_project_paths

        # 测试路径管理器
        path_manager = ProjectPathManager()
        session_dir = path_manager.get_session_dir()
        assert os.path.exists(session_dir)

        # 测试项目路径初始化
        paths = init_project_paths()
        assert "base_dir" in paths
        assert "session_dir" in paths


class TestExceptionsFunctionality:
    """测试异常处理"""

    def test_exceptions(self):
        """测试异常处理"""
        from my_python_project import (
            BaseError,
            ConfigError,
            ValidationError,
            handle_exceptions,
        )

        # 测试异常类
        with pytest.raises(BaseError):
            raise ConfigError("测试配置错误")

        # 测试异常处理装饰器
        @handle_exceptions(ValueError, default_return="error_handled", reraise=False)
        def error_function():
            raise ValueError("测试错误")

        result = error_function()
        assert result == "error_handled"
