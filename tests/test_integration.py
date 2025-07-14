"""
集成测试

测试各模块之间的协作和完整功能流程。
"""

import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from my_python_project import (
    ConfigManager,
    validate_data,
    MemoryCache,
    FileCache,
    cache_result,
    handle_exceptions,
    StringValidator,
    NumberValidator,
    EmailValidator,
    DictValidator,
    ValidationError,
    ConfigError,
    get_project_logger,
    auto_setup_project_logging,
)


class TestConfigValidationIntegration:
    """配置管理和数据验证集成测试"""

    def test_config_with_validation(self):
        """测试配置加载和验证的集成"""
        # 创建测试配置
        config_data = {
            "database": {"host": "localhost", "port": 5432, "username": "testuser"},
            "api": {"timeout": 30, "retries": 3},
        }

        config = ConfigManager.from_dict(config_data)

        # 定义验证schema
        schema = {
            "database": DictValidator(
                schema={
                    "host": StringValidator(min_length=1),
                    "port": NumberValidator(
                        number_type=int, min_value=1, max_value=65535
                    ),
                    "username": StringValidator(min_length=1),
                }
            ),
            "api": DictValidator(
                schema={
                    "timeout": NumberValidator(number_type=int, min_value=1),
                    "retries": NumberValidator(number_type=int, min_value=0),
                }
            ),
        }

        # 验证配置
        validated_config = validate_data(config.to_dict(), schema)

        assert validated_config["database"]["host"] == "localhost"
        assert validated_config["database"]["port"] == 5432
        assert validated_config["api"]["timeout"] == 30

    def test_config_validation_failure(self):
        """测试配置验证失败情况"""
        config_data = {
            "database": {
                "host": "",  # 空字符串，应该验证失败
                "port": 70000,  # 端口超出范围
            }
        }

        config = ConfigManager.from_dict(config_data)

        schema = {
            "database": DictValidator(
                schema={
                    "host": StringValidator(min_length=1),
                    "port": NumberValidator(
                        number_type=int, min_value=1, max_value=65535
                    ),
                }
            )
        }

        with pytest.raises(ValidationError):
            validate_data(config.to_dict(), schema)


class TestCacheConfigIntegration:
    """缓存和配置管理集成测试"""

    def test_cache_with_config(self):
        """测试缓存配置集成"""
        # 配置驱动的缓存设置
        config_data = {"cache": {"type": "memory", "max_size": 100, "default_ttl": 300}}

        config = ConfigManager.from_dict(config_data)

        # 根据配置创建缓存
        cache_config = config.get("cache")
        cache = MemoryCache(
            max_size=cache_config["max_size"], default_ttl=cache_config["default_ttl"]
        )

        # 测试缓存功能
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"

        # 测试TTL
        cache.set("ttl_key", "ttl_value", ttl=1)
        assert cache.get("ttl_key") == "ttl_value"

        time.sleep(1.1)
        assert cache.get("ttl_key") is None


class TestErrorHandlingIntegration:
    """错误处理集成测试"""

    def test_validation_error_handling(self):
        """测试验证错误处理"""

        @handle_exceptions(
            ValidationError, default_return={"error": "validation_failed"}
        )
        def process_user_data(data):
            schema = {
                "email": EmailValidator(),
                "age": NumberValidator(number_type=int, min_value=0, max_value=150),
            }
            return validate_data(data, schema)

        # 正常情况
        valid_data = {"email": "test@example.com", "age": 25}
        result = process_user_data(valid_data)
        assert result["email"] == "test@example.com"

        # 验证失败情况
        invalid_data = {"email": "invalid_email", "age": -1}
        result = process_user_data(invalid_data)
        assert result == {"error": "validation_failed"}

    def test_config_error_recovery(self):
        """测试配置错误恢复"""

        @handle_exceptions(ConfigError, default_return={"status": "fallback_config"})
        def load_config_with_fallback():
            # 尝试加载不存在的配置文件
            config = ConfigManager.from_file("/nonexistent/config.json")
            return {"status": "config_loaded", "data": config.to_dict()}

        result = load_config_with_fallback()
        assert result == {"status": "fallback_config"}


class TestCacheDecoratorIntegration:
    """缓存装饰器集成测试"""

    def test_cache_decorator_with_validation(self):
        """测试缓存装饰器与验证的集成"""
        call_count = 0

        @cache_result(ttl=60)
        def get_validated_user(user_id):
            nonlocal call_count
            call_count += 1

            # 模拟从数据库获取用户数据
            user_data = {
                "id": user_id,
                "email": f"user{user_id}@example.com",
                "age": 25,
            }

            # 验证数据
            schema = {
                "id": NumberValidator(number_type=int),
                "email": EmailValidator(),
                "age": NumberValidator(number_type=int, min_value=0, max_value=150),
            }

            return validate_data(user_data, schema)

        # 第一次调用
        user1 = get_validated_user(1)
        assert user1["email"] == "user1@example.com"
        assert call_count == 1

        # 第二次调用相同参数（使用缓存）
        user1_cached = get_validated_user(1)
        assert user1_cached["email"] == "user1@example.com"
        assert call_count == 1  # 没有增加

        # 不同参数
        user2 = get_validated_user(2)
        assert user2["email"] == "user2@example.com"
        assert call_count == 2


class TestFileSystemIntegration:
    """文件系统集成测试"""

    def test_config_file_cache_integration(self):
        """测试配置文件和文件缓存集成"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 创建配置文件
            config_file = temp_path / "config.json"
            config_data = {
                "cache": {
                    "type": "file",
                    "directory": str(temp_path / "cache"),
                    "default_ttl": 300,
                }
            }

            import json

            with open(config_file, "w") as f:
                json.dump(config_data, f)

            # 加载配置
            config = ConfigManager.from_file(config_file)
            cache_config = config.get("cache")

            # 创建文件缓存
            cache = FileCache(
                cache_dir=cache_config["directory"],
                default_ttl=cache_config["default_ttl"],
            )

            # 测试缓存功能
            cache.set("file_test", {"data": "test_value"})
            result = cache.get("file_test")
            assert result["data"] == "test_value"

            # 验证文件确实被创建
            cache_dir = Path(cache_config["directory"])
            assert cache_dir.exists()
            assert len(list(cache_dir.glob("*.cache"))) > 0


class TestLoggingIntegration:
    """日志集成测试"""

    def test_logging_with_error_handling(self):
        """测试日志和错误处理集成"""

        # 设置日志
        logger = get_project_logger("integration_test")

        @handle_exceptions(ValueError, log_errors=True)
        def risky_operation(value):
            if value < 0:
                raise ValueError("值不能为负数")
            return value * 2

        # 正常情况
        result = risky_operation(5)
        assert result == 10

        # 异常情况（会被日志记录）
        with pytest.raises(ValueError):
            risky_operation(-1)


class TestComplexWorkflow:
    """复杂工作流集成测试"""

    def test_user_registration_workflow(self):
        """测试用户注册完整工作流"""

        # 1. 配置管理
        config_data = {
            "validation": {
                "min_password_length": 8,
                "allowed_domains": ["example.com", "test.org"],
            },
            "cache": {"user_cache_ttl": 300},
        }
        config = ConfigManager.from_dict(config_data)

        # 2. 缓存设置
        cache = MemoryCache()

        # 3. 验证schema
        def create_user_schema(config):
            min_pwd_length = config.get("validation.min_password_length", 8)
            allowed_domains = config.get("validation.allowed_domains", [])

            return {
                "username": StringValidator(min_length=3, max_length=20),
                "email": EmailValidator(),
                "password": StringValidator(min_length=min_pwd_length),
                "age": NumberValidator(number_type=int, min_value=13, max_value=120),
            }

        # 4. 用户注册函数
        @cache_result(ttl=config.get("cache.user_cache_ttl", 300))
        @handle_exceptions(
            ValidationError, default_return={"error": "validation_failed"}
        )
        def register_user(user_data):
            # 验证用户数据
            schema = create_user_schema(config)
            validated_data = validate_data(user_data, schema)

            # 额外的业务验证
            allowed_domains = config.get("validation.allowed_domains", [])
            email_domain = validated_data["email"].split("@")[1]
            if email_domain not in allowed_domains:
                raise ValidationError(f"邮箱域名 {email_domain} 不被允许")

            # 模拟用户创建
            user_id = hash(validated_data["username"]) % 10000
            return {
                "user_id": user_id,
                "username": validated_data["username"],
                "email": validated_data["email"],
                "status": "registered",
            }

        # 5. 测试正常注册
        valid_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123",
            "age": 25,
        }

        result = register_user(valid_user)
        assert result["status"] == "registered"
        assert result["username"] == "testuser"

        # 6. 测试验证失败
        invalid_user = {
            "username": "tu",  # 太短
            "email": "invalid_email",
            "password": "123",  # 太短
            "age": 200,  # 太大
        }

        result = register_user(invalid_user)
        assert result == {"error": "validation_failed"}

        # 7. 测试域名限制
        wrong_domain_user = {
            "username": "testuser2",
            "email": "test@forbidden.com",
            "password": "securepassword123",
            "age": 25,
        }

        result = register_user(wrong_domain_user)
        assert result == {"error": "validation_failed"}


class TestPerformanceIntegration:
    """性能集成测试"""

    def test_performance_monitoring_integration(self):
        """测试性能监控集成"""
        from my_python_project.utils.performance import (
            monitor_performance,
            global_monitor,
        )

        @monitor_performance("test_function")
        @cache_result(ttl=60)
        def expensive_operation(n):
            # 模拟耗时操作
            time.sleep(0.01)
            return sum(range(n))

        # 执行操作
        result1 = expensive_operation(100)
        result2 = expensive_operation(100)  # 使用缓存
        result3 = expensive_operation(200)  # 新计算

        # 检查性能统计
        stats = global_monitor.get_stats("test_function")
        assert stats["count"] >= 2  # 至少执行了2次（缓存会减少实际执行次数）
        assert stats["avg_time"] > 0

        # 验证结果正确性
        assert result1 == sum(range(100))
        assert result2 == result1  # 缓存结果
        assert result3 == sum(range(200))


class TestEndToEndScenario:
    """端到端场景测试"""

    def test_complete_application_scenario(self):
        """测试完整应用场景"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 1. 创建应用配置
            config_file = temp_path / "app_config.json"
            app_config = {
                "database": {"host": "localhost", "port": 5432, "name": "testdb"},
                "cache": {
                    "type": "file",
                    "directory": str(temp_path / "cache"),
                    "default_ttl": 300,
                },
                "logging": {"level": "INFO", "file": str(temp_path / "app.log")},
                "validation": {"strict_mode": True, "max_retries": 3},
            }

            import json

            with open(config_file, "w") as f:
                json.dump(app_config, f)

            # 2. 初始化应用组件
            config = ConfigManager.from_file(config_file)

            # 验证配置
            config_schema = {
                "database": DictValidator(
                    schema={
                        "host": StringValidator(),
                        "port": NumberValidator(number_type=int),
                        "name": StringValidator(),
                    }
                ),
                "cache": DictValidator(
                    schema={
                        "type": StringValidator(choices=["memory", "file"]),
                        "directory": StringValidator(),
                        "default_ttl": NumberValidator(number_type=int),
                    }
                ),
            }

            validated_config = validate_data(config.to_dict(), config_schema)
            assert validated_config["database"]["host"] == "localhost"

            # 3. 创建缓存
            cache_config = config.get("cache")
            cache = FileCache(
                cache_dir=cache_config["directory"],
                default_ttl=cache_config["default_ttl"],
            )

            # 4. 定义业务逻辑
            @handle_exceptions(Exception, log_errors=True, default_return=None)
            @cache_result(ttl=cache_config["default_ttl"])
            def process_data(data_id):
                # 模拟数据处理
                processed_data = {
                    "id": data_id,
                    "processed_at": time.time(),
                    "status": "completed",
                }

                # 验证处理结果
                result_schema = {
                    "id": NumberValidator(number_type=int),
                    "processed_at": NumberValidator(number_type=float),
                    "status": StringValidator(choices=["completed", "failed"]),
                }

                return validate_data(processed_data, result_schema)

            # 5. 测试完整流程
            result = process_data(123)
            assert result is not None
            assert result["id"] == 123
            assert result["status"] == "completed"

            # 6. 验证缓存工作
            cached_result = process_data(123)
            assert cached_result["id"] == 123

            # 7. 验证文件系统状态
            cache_dir = Path(cache_config["directory"])
            assert cache_dir.exists()
            assert len(list(cache_dir.glob("*.cache"))) > 0
