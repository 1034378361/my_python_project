"""
测试异常处理系统
"""

import time
import pytest
from unittest.mock import Mock, patch

from my_python_project.utils.exceptions import (
    # 基础异常
    BaseError, ConfigError, ValidationError, CacheError,
    NetworkTimeoutError, ProjectFileNotFoundError,
    BusinessError, SystemError,
    
    # 异常处理工具
    handle_exceptions, suppress_exceptions, retry_on_exception,
    ErrorHandler, CircuitBreaker, CircuitBreakerOpenError,
    error_context, safe_execute,
    
    # 异常格式化
    format_exception, get_exception_chain
)


class TestBaseExceptions:
    """基础异常类测试"""
    
    def test_base_error(self):
        """测试基础异常"""
        error = BaseError("Test error", error_code="TEST_001", details={"key": "value"})
        
        assert str(error) == "Test error (详情: {'key': 'value'})"
        assert error.error_code == "TEST_001"
        assert error.details == {"key": "value"}
        
        # 测试to_dict方法
        error_dict = error.to_dict()
        expected = {
            'error_type': 'BaseError',
            'error_code': 'TEST_001',
            'message': 'Test error',
            'details': {'key': 'value'}
        }
        assert error_dict == expected
    
    def test_specific_exceptions(self):
        """测试特定异常类型"""
        # ConfigError
        config_error = ConfigError("Configuration not found")
        assert isinstance(config_error, BaseError)
        assert config_error.error_code == "ConfigError"
        
        # ValidationError
        validation_error = ValidationError("Invalid data")
        assert isinstance(validation_error, BaseError)
        
        # CacheError
        cache_error = CacheError("Cache operation failed")
        assert isinstance(cache_error, BaseError)
    
    def test_renamed_exceptions(self):
        """测试重命名的异常（避免与内置异常冲突）"""
        # NetworkTimeoutError (原TimeoutError)
        timeout_error = NetworkTimeoutError("Network timeout")
        assert isinstance(timeout_error, BaseError)
        
        # ProjectFileNotFoundError (原FileNotFoundError)
        file_error = ProjectFileNotFoundError("File not found")
        assert isinstance(file_error, BaseError)


class TestExceptionDecorators:
    """异常处理装饰器测试"""
    
    def test_handle_exceptions_default(self):
        """测试基本异常处理装饰器"""
        @handle_exceptions(ValueError, default_return="error", reraise=False)
        def risky_function(value):
            if value < 0:
                raise ValueError("Negative value")
            return value * 2
        
        # 正常情况
        assert risky_function(5) == 10
        
        # 异常情况
        assert risky_function(-1) == "error"
    
    def test_handle_exceptions_reraise(self):
        """测试重新抛出异常"""
        @handle_exceptions(ValueError, log_errors=False)
        def failing_function():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError, match="Always fails"):
            failing_function()
    
    def test_handle_exceptions_with_callback(self):
        """测试带回调的异常处理"""
        callback_called = False
        
        def error_callback(error, func, args, kwargs):
            nonlocal callback_called
            callback_called = True
            assert isinstance(error, ValueError)
            assert func.__name__ == "test_function"
        
        @handle_exceptions(ValueError, callback=error_callback, reraise=False)
        def test_function():
            raise ValueError("Test error")
        
        test_function()
        assert callback_called
    
    def test_suppress_exceptions(self):
        """测试异常抑制装饰器"""
        @suppress_exceptions(ZeroDivisionError, default_return=0)
        def divide_function(a, b):
            return a / b
        
        # 正常情况
        assert divide_function(10, 2) == 5
        
        # 异常情况（被抑制）
        assert divide_function(10, 0) == 0
    
    def test_retry_on_exception(self):
        """测试重试装饰器"""
        attempt_count = 0
        
        @retry_on_exception(max_retries=3, delay=0.01, exceptions=(ValueError,))
        def flaky_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = flaky_function()
        assert result == "success"
        assert attempt_count == 3
    
    def test_retry_exhausted(self):
        """测试重试次数耗尽"""
        @retry_on_exception(max_retries=2, delay=0.01)
        def always_failing():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError, match="Always fails"):
            always_failing()


class TestErrorHandler:
    """错误处理器测试"""
    
    def test_error_handler_basic(self):
        """测试基本错误处理"""
        handler = ErrorHandler()
        
        error = ValueError("Test error")
        context = {"user_id": 123, "action": "test"}
        
        # 不应该抛出异常
        handler.handle_error(error, context)
        
        # 检查错误统计
        stats = handler.get_error_stats()
        assert stats["ValueError"] == 1
    
    def test_error_handler_callback(self):
        """测试错误回调"""
        handler = ErrorHandler()
        callback_called = False
        
        def error_callback(error, context):
            nonlocal callback_called
            callback_called = True
            assert isinstance(error, ValueError)
            assert context["test"] == True
        
        handler.register_callback("ValueError", error_callback)
        
        error = ValueError("Test error")
        handler.handle_error(error, {"test": True})
        
        assert callback_called
    
    def test_error_stats(self):
        """测试错误统计"""
        handler = ErrorHandler()
        
        # 记录多个错误
        handler.handle_error(ValueError("Error 1"))
        handler.handle_error(ValueError("Error 2"))
        handler.handle_error(TypeError("Error 3"))
        
        stats = handler.get_error_stats()
        assert stats["ValueError"] == 2
        assert stats["TypeError"] == 1
        
        # 重置统计
        handler.reset_stats()
        stats = handler.get_error_stats()
        assert len(stats) == 0
    
    def test_recovery_strategy(self):
        """测试错误恢复策略"""
        handler = ErrorHandler()
        
        def recovery_strategy(error, context):
            return "recovered_value"
        
        handler.register_recovery_strategy("ValueError", recovery_strategy)
        
        error = ValueError("Test error")
        result = handler.attempt_recovery(error, {"test": True})
        
        assert result == "recovered_value"
    
    def test_error_patterns(self):
        """测试错误模式检测"""
        handler = ErrorHandler()
        
        # 注册错误模式：5分钟内出现3次ValueError
        handler.add_error_pattern(
            "frequent_value_errors",
            (ValueError,),
            threshold=3,
            time_window=300
        )
        
        # 触发错误
        error = ValueError("Test error")
        
        # 前两次不应该匹配模式
        assert handler.check_error_patterns(error) is None
        assert handler.check_error_patterns(error) is None
        
        # 第三次应该匹配模式
        result = handler.check_error_patterns(error)
        assert result == "frequent_value_errors"


class TestCircuitBreaker:
    """熔断器测试"""
    
    def test_circuit_breaker_success(self):
        """测试熔断器正常工作"""
        breaker = CircuitBreaker(failure_threshold=3, timeout=1)
        
        def success_function():
            return "success"
        
        # 正常调用
        result = breaker.call(success_function)
        assert result == "success"
        assert breaker.state == "CLOSED"
    
    def test_circuit_breaker_failure(self):
        """测试熔断器失败处理"""
        breaker = CircuitBreaker(failure_threshold=2, timeout=0.1)
        
        def failing_function():
            raise ValueError("Always fails")
        
        # 第一次失败
        with pytest.raises(ValueError):
            breaker.call(failing_function)
        assert breaker.state == "CLOSED"
        
        # 第二次失败，触发熔断
        with pytest.raises(ValueError):
            breaker.call(failing_function)
        assert breaker.state == "OPEN"
        
        # 熔断器打开，直接抛出熔断器异常
        with pytest.raises(CircuitBreakerOpenError):
            breaker.call(failing_function)
    
    def test_circuit_breaker_recovery(self):
        """测试熔断器恢复"""
        breaker = CircuitBreaker(failure_threshold=1, timeout=0.01)
        
        def toggle_function():
            if not hasattr(toggle_function, 'should_succeed'):
                toggle_function.should_succeed = False
            if toggle_function.should_succeed:
                return "success"
            else:
                raise ValueError("Fails")
        
        # 触发熔断
        with pytest.raises(ValueError):
            breaker.call(toggle_function)
        assert breaker.state == "OPEN"
        
        # 等待超时
        time.sleep(0.02)
        
        # 设置成功
        toggle_function.should_succeed = True
        
        # 应该能够恢复
        result = breaker.call(toggle_function)
        assert result == "success"
        assert breaker.state == "CLOSED"


class TestContextManager:
    """上下文管理器测试"""
    
    def test_error_context_suppress(self):
        """测试错误上下文抑制"""
        handler = ErrorHandler()
        
        with error_context(handler, suppress=True) as ctx:
            raise ValueError("Test error")
        
        # 异常被抑制，上下文中有错误记录
        assert isinstance(ctx.error, ValueError)
        
        # 错误被记录到处理器
        stats = handler.get_error_stats()
        assert stats["ValueError"] == 1
    
    def test_error_context_not_suppress(self):
        """测试错误上下文不抑制"""
        handler = ErrorHandler()
        
        with pytest.raises(ValueError):
            with error_context(handler, suppress=False):
                raise ValueError("Test error")


class TestUtilityFunctions:
    """工具函数测试"""
    
    def test_safe_execute(self):
        """测试安全执行函数"""
        def success_function():
            return "success"
        
        def failing_function():
            raise ValueError("Failure")
        
        # 成功情况
        result = safe_execute(success_function)
        assert result == "success"
        
        # 失败情况，返回默认值
        result = safe_execute(failing_function, default_return="default")
        assert result == "default"
        
        # 失败情况，无默认值
        result = safe_execute(failing_function)
        assert result is None
    
    def test_format_exception(self):
        """测试异常格式化"""
        error = ValueError("Test error")
        
        # 包含堆栈跟踪
        result = format_exception(error, include_traceback=True)
        assert result["error_type"] == "ValueError"
        assert result["error_message"] == "Test error"
        assert "traceback" in result
        
        # 不包含堆栈跟踪
        result = format_exception(error, include_traceback=False)
        assert "traceback" not in result
    
    def test_format_base_error(self):
        """测试BaseError格式化"""
        error = BaseError("Test error", error_code="TEST_001", details={"key": "value"})
        result = format_exception(error, include_traceback=False)
        
        assert result["error_type"] == "BaseError"
        assert result["error_code"] == "TEST_001"
        assert result["details"] == {"key": "value"}
    
    def test_get_exception_chain(self):
        """测试异常链获取"""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise RuntimeError("Secondary error") from e
        except RuntimeError as e:
            chain = get_exception_chain(e)
            
            assert len(chain) == 2
            assert chain[0]["type"] == "RuntimeError"
            assert chain[0]["message"] == "Secondary error"
            assert chain[1]["type"] == "ValueError"
            assert chain[1]["message"] == "Original error"


if __name__ == "__main__":
    pytest.main([__file__])