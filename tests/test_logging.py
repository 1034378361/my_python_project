"""日志系统测试模块。"""

import json
import logging
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from my_python_project.utils.logging_utils import (
    JsonFormatter,
    PerformanceFilter,
    LoggerManager,
    setup_advanced_logger,
    get_project_logger,
    log_performance,
    log_function_call,
    log_context,
    configure_project_logging,
    get_configured_logger,
    get_logger_with_path,
    get_log_path_from_env,
)


class TestJsonFormatter:
    """测试JSON格式化器。"""

    def test_basic_formatting(self):
        """测试基本格式化功能。"""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test.logger"
        assert log_data["message"] == "Test message"
        assert log_data["line"] == 42
        assert "timestamp" in log_data

    def test_exception_formatting(self):
        """测试异常信息格式化。"""
        formatter = JsonFormatter()

        try:
            raise ValueError("Test error")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

            record = logging.LogRecord(
                name="test.logger",
                level=logging.ERROR,
                pathname="test.py",
                lineno=42,
                msg="Error occurred",
                args=(),
                exc_info=exc_info,
            )

            result = formatter.format(record)
            log_data = json.loads(result)

            assert "exception" in log_data
            assert log_data["exception"]["type"] == "ValueError"
            assert log_data["exception"]["message"] == "Test error"
            assert isinstance(log_data["exception"]["traceback"], list)

    def test_extra_fields(self):
        """测试额外字段。"""
        formatter = JsonFormatter(include_extra=True)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # 添加额外字段
        record.user_id = "123"
        record.request_id = "req-456"

        result = formatter.format(record)
        log_data = json.loads(result)

        assert "extra" in log_data
        assert log_data["extra"]["user_id"] == "123"
        assert log_data["extra"]["request_id"] == "req-456"


class TestPerformanceFilter:
    """测试性能过滤器。"""

    def test_duration_filtering(self):
        """测试时长过滤。"""
        filter_obj = PerformanceFilter(min_duration=0.5)

        # 创建快速记录
        fast_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Fast",
            args=(),
            exc_info=None,
        )
        fast_record.duration = 0.1

        # 创建慢速记录
        slow_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Slow",
            args=(),
            exc_info=None,
        )
        slow_record.duration = 1.0

        assert not filter_obj.filter(fast_record)
        assert filter_obj.filter(slow_record)

    def test_no_duration_attribute(self):
        """测试没有duration属性的记录。"""
        filter_obj = PerformanceFilter(min_duration=0.5)

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="No duration",
            args=(),
            exc_info=None,
        )

        assert filter_obj.filter(record)


class TestLoggerManager:
    """测试日志管理器。"""

    def test_singleton_pattern(self):
        """测试单例模式。"""
        manager1 = LoggerManager()
        manager2 = LoggerManager()

        assert manager1 is manager2

    def test_logger_caching(self):
        """测试日志记录器缓存。"""
        manager = LoggerManager()

        logger1 = manager.get_logger("test.logger")
        logger2 = manager.get_logger("test.logger")

        assert logger1 is logger2

    def test_config_loading(self):
        """测试配置加载。"""
        manager = LoggerManager()

        # 创建临时配置文件
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"simple": {"format": "%(levelname)s - %(message)s"}},
            "handlers": {
                "console": {"class": "logging.StreamHandler", "formatter": "simple"}
            },
            "root": {"level": "INFO", "handlers": ["console"]},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            config_path = f.name

        try:
            manager.setup_from_config(config_path)
            # 验证配置已应用
            assert manager.config == config
        finally:
            Path(config_path).unlink()


class TestLoggerSetup:
    """测试日志记录器设置。"""

    def test_basic_setup(self):
        """测试基本设置。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"

            logger = setup_advanced_logger(
                name="test.logger",
                level=logging.INFO,
                log_file=log_file,
                log_format="standard",
            )

            logger.info("Test message")

            # 验证日志文件存在
            assert log_file.exists()

            # 验证日志内容
            content = log_file.read_text()
            assert "Test message" in content
            assert "INFO" in content

    def test_json_format(self):
        """测试JSON格式。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"

            logger = setup_advanced_logger(
                name="test.logger",
                level=logging.INFO,
                log_file=log_file,
                json_format=True,
            )

            logger.info("Test message")

            # 验证JSON格式
            content = log_file.read_text().strip()
            log_data = json.loads(content)

            assert log_data["message"] == "Test message"
            assert log_data["level"] == "INFO"

    def test_rotation_setup(self):
        """测试文件轮转设置。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"

            logger = setup_advanced_logger(
                name="test.logger",
                level=logging.INFO,
                log_file=log_file,
                enable_rotation=True,
                max_bytes=100,  # 非常小的文件大小以触发轮转
                backup_count=2,
            )

            # 写入足够的日志触发轮转
            for i in range(50):
                logger.info(f"Test message {i}")

            # 验证轮转文件存在
            assert log_file.exists()
            # 可能存在轮转文件（.1, .2等）


class TestDecorators:
    """测试装饰器。"""

    def test_log_performance_decorator(self):
        """测试性能监控装饰器。"""
        mock_logger = MagicMock()

        @log_performance(mock_logger)
        def test_function():
            time.sleep(0.1)
            return "result"

        result = test_function()

        assert result == "result"
        assert mock_logger.log.called

        # 验证日志调用
        calls = mock_logger.log.call_args_list
        assert len(calls) >= 1

        # 验证包含duration信息
        final_call = calls[-1]
        assert "duration" in final_call[1].get("extra", {})

    def test_log_function_call_decorator(self):
        """测试函数调用装饰器。"""
        mock_logger = MagicMock()

        @log_function_call(mock_logger, log_args=True, log_result=True)
        def test_function(arg1, arg2="default"):
            return f"processed {arg1} and {arg2}"

        result = test_function("hello", arg2="world")

        assert result == "processed hello and world"
        assert mock_logger.log.called

        # 验证记录了参数和结果
        calls = [str(call) for call in mock_logger.log.call_args_list]
        call_content = " ".join(calls)
        assert "hello" in call_content
        assert "world" in call_content

    def test_log_context_manager(self):
        """测试上下文管理器。"""
        mock_logger = MagicMock()

        with log_context(mock_logger, "test_context"):
            time.sleep(0.1)

        assert mock_logger.log.called
        assert mock_logger.error.not_called

        # 验证上下文进入和退出都被记录
        calls = mock_logger.log.call_args_list
        assert len(calls) >= 2

    def test_log_context_with_exception(self):
        """测试上下文管理器异常处理。"""
        mock_logger = MagicMock()

        with pytest.raises(ValueError):
            with log_context(mock_logger, "test_context"):
                raise ValueError("Test error")

        # 验证记录了错误
        assert mock_logger.error.called
        error_call = mock_logger.error.call_args
        assert "Test error" in str(error_call)


class TestProjectLogger:
    """测试项目专用日志记录器。"""

    def test_get_project_logger(self):
        """测试获取项目日志记录器。"""
        logger = get_project_logger("test.module")

        assert isinstance(logger, logging.Logger)
        assert "my_python_project" in logger.name

    def test_auto_module_detection(self):
        """测试自动模块检测。"""
        # 这个测试会自动检测当前模块名
        logger = get_project_logger()

        assert isinstance(logger, logging.Logger)
        assert "my_python_project" in logger.name

    def test_custom_log_file_path(self):
        """测试自定义日志文件路径。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_log_path = Path(temp_dir) / "custom" / "my_app.log"

            logger = get_project_logger("test.module", log_file=custom_log_path)
            logger.info("Test message")

            # 验证自定义路径的日志文件被创建
            assert custom_log_path.exists()

            # 验证日志内容
            content = custom_log_path.read_text()
            assert "Test message" in content


class TestConfigIntegration:
    """测试配置集成。"""

    def test_yaml_dependency_optional(self):
        """测试YAML依赖是可选的。"""
        # 这个测试验证即使没有PyYAML，系统也能正常工作
        with patch("my_python_project.config.YAML_AVAILABLE", False):
            from my_python_project.config import load_logging_config

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as f:
                json.dump({"version": 1}, f)
                config_path = f.name

            try:
                config = load_logging_config("json", Path(config_path))
                assert config["version"] == 1
            finally:
                Path(config_path).unlink()


class TestCustomPathSupport:
    """测试自定义路径支持。"""

    def test_configure_project_logging_custom_dir(self):
        """测试配置项目日志系统，自定义目录。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_log_dir = Path(temp_dir) / "custom_logs"

            loggers = configure_project_logging(
                log_dir=custom_log_dir, log_level="DEBUG", enable_file_logging=True
            )

            # 验证返回的日志记录器
            assert "main" in loggers
            assert "error" in loggers
            assert "performance" in loggers

            # 测试日志记录
            loggers["main"].info("Test main logger")
            loggers["error"].error("Test error logger")

            # 验证文件创建
            main_log = custom_log_dir / "my_python_project.log"
            error_log = custom_log_dir / "my_python_project_errors.log"

            assert main_log.exists()
            assert error_log.exists()

            # 验证内容
            assert "Test main logger" in main_log.read_text()
            assert "Test error logger" in error_log.read_text()

    def test_configure_project_logging_custom_files(self):
        """测试配置项目日志系统，自定义文件映射。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_files = {
                "database": Path(temp_dir) / "db" / "database.log",
                "api": Path(temp_dir) / "api" / "web.log",
                "worker": Path(temp_dir) / "workers" / "background.log",
            }

            loggers = configure_project_logging(
                log_dir=Path(temp_dir) / "main",
                custom_log_files=custom_files,
                enable_file_logging=True,
            )

            # 验证自定义日志记录器
            assert "database" in loggers
            assert "api" in loggers
            assert "worker" in loggers

            # 测试每个日志记录器
            loggers["database"].info("Database operation")
            loggers["api"].info("API request")
            loggers["worker"].info("Background task")

            # 验证文件创建和内容
            assert custom_files["database"].exists()
            assert custom_files["api"].exists()
            assert custom_files["worker"].exists()

            assert "Database operation" in custom_files["database"].read_text()
            assert "API request" in custom_files["api"].read_text()
            assert "Background task" in custom_files["worker"].read_text()

    def test_get_configured_logger_custom_path(self):
        """测试获取自定义路径的配置日志记录器。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_log_file = Path(temp_dir) / "modules" / "custom_module.log"

            logger = get_configured_logger(
                "custom_module",
                log_file=custom_log_file,
                log_level="DEBUG",
                log_format="json",
            )

            logger.info("Custom logger test", extra={"module": "custom_module"})

            # 验证文件创建
            assert custom_log_file.exists()

            # 验证JSON格式
            content = custom_log_file.read_text().strip()
            log_data = json.loads(content)

            assert log_data["message"] == "Custom logger test"
            assert log_data["extra"]["module"] == "custom_module"

    def test_get_logger_with_path_convenience(self):
        """测试便捷函数获取指定路径的日志记录器。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "convenience.log"

            logger = get_logger_with_path(log_path, "convenience_module")
            logger.info("Convenience function test")

            assert log_path.exists()
            assert "Convenience function test" in log_path.read_text()

    def test_environment_variable_log_path(self):
        """测试从环境变量获取日志路径。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 测试LOG_DIR环境变量
            with patch.dict("os.environ", {"MY_PYTHON_PROJECT_LOG_DIR": temp_dir}):
                log_path = get_log_path_from_env()
                expected_path = Path(temp_dir) / "my_python_project.log"
                assert log_path == expected_path

            # 测试LOG_FILE环境变量
            custom_file = str(Path(temp_dir) / "custom.log")
            with patch.dict("os.environ", {"MY_PYTHON_PROJECT_LOG_FILE": custom_file}):
                log_path = get_log_path_from_env()
                assert log_path == Path(custom_file)

    def test_absolute_vs_relative_paths(self):
        """测试绝对路径和相对路径的处理。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 测试绝对路径
            abs_path = Path(temp_dir) / "absolute.log"
            logger1 = get_configured_logger("test1", log_file=abs_path)
            logger1.info("Absolute path test")

            assert abs_path.exists()
            assert "Absolute path test" in abs_path.read_text()

            # 测试相对路径（需要确保在临时目录中执行）
            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                rel_path = "relative/path/relative.log"
                logger2 = get_configured_logger("test2", log_file=rel_path)
                logger2.info("Relative path test")

                full_path = Path(temp_dir) / rel_path
                assert full_path.exists()
                assert "Relative path test" in full_path.read_text()
            finally:
                os.chdir(original_cwd)

    def test_concurrent_logging_different_paths(self):
        """测试并发日志记录到不同路径。"""
        import threading
        import time

        with tempfile.TemporaryDirectory() as temp_dir:
            results = {}

            def worker(worker_id):
                log_file = Path(temp_dir) / f"worker_{worker_id}.log"
                logger = get_configured_logger(f"worker_{worker_id}", log_file=log_file)

                for i in range(10):
                    logger.info(f"Worker {worker_id} message {i}")
                    time.sleep(0.01)

                results[worker_id] = log_file

            # 启动多个工作线程
            threads = []
            for i in range(3):
                t = threading.Thread(target=worker, args=(i,))
                threads.append(t)
                t.start()

            # 等待所有线程完成
            for t in threads:
                t.join()

            # 验证结果
            for worker_id, log_file in results.items():
                assert log_file.exists()
                content = log_file.read_text()

                # 验证该工作线程的所有消息都存在
                for i in range(10):
                    assert f"Worker {worker_id} message {i}" in content


# 集成测试
class TestLoggingIntegration:
    """测试日志系统集成。"""

    def test_full_logging_workflow(self):
        """测试完整的日志工作流程。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "integration.log"

            # 设置日志系统
            logger = setup_advanced_logger(
                name="integration.test",
                level=logging.INFO,
                log_file=log_file,
                json_format=True,
            )

            # 使用装饰器
            @log_performance(logger)
            @log_function_call(logger, log_args=True)
            def test_workflow(data):
                logger.info("Processing data", extra={"data_size": len(data)})
                return f"processed {len(data)} items"

            # 执行测试
            result = test_workflow(["item1", "item2", "item3"])

            # 验证结果
            assert result == "processed 3 items"
            assert log_file.exists()

            # 验证日志内容
            content = log_file.read_text()
            lines = [line for line in content.strip().split("\n") if line]

            # 每行都应该是有效的JSON
            for line in lines:
                log_data = json.loads(line)
                assert "timestamp" in log_data
                assert "level" in log_data
                assert "message" in log_data

            # 验证特定日志存在
            log_messages = [json.loads(line)["message"] for line in lines]
            assert any("Processing data" in msg for msg in log_messages)
            assert any("processed 3 items" in msg for msg in log_messages)


if __name__ == "__main__":
    pytest.main([__file__])
