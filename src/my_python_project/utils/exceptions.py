"""
异常处理系统

定义项目中使用的自定义异常类和错误处理工具。
"""

import sys
import traceback
from typing import Any, Dict, Optional, Type, Union, Callable
from functools import wraps
import logging

# 获取logger
logger = logging.getLogger(__name__)


# =============================================================================
# 基础异常类
# =============================================================================

class BaseError(Exception):
    """基础异常类"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        """
        初始化异常
        
        Args:
            message: 错误消息
            error_code: 错误代码
            details: 详细信息
        """
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        if self.details:
            return f"{self.message} (详情: {self.details})"
        return self.message


# =============================================================================
# 配置相关异常
# =============================================================================

class ConfigError(BaseError):
    """配置错误"""
    pass


class ConfigNotFoundError(ConfigError):
    """配置未找到错误"""
    pass


class ConfigValidationError(ConfigError):
    """配置验证错误"""
    pass


# =============================================================================
# 数据相关异常
# =============================================================================

class DataError(BaseError):
    """数据错误"""
    pass


class ValidationError(DataError):
    """数据验证错误"""
    pass


class SerializationError(DataError):
    """序列化错误"""
    pass


class DatabaseError(DataError):
    """数据库错误"""
    pass


# =============================================================================
# 网络相关异常
# =============================================================================

class NetworkError(BaseError):
    """网络错误"""
    pass


class RequestError(NetworkError):
    """请求错误"""
    pass


class NetworkTimeoutError(NetworkError):
    """网络超时错误"""
    pass


class AuthenticationError(NetworkError):
    """认证错误"""
    pass


class AuthorizationError(NetworkError):
    """授权错误"""
    pass


# =============================================================================
# 文件相关异常
# =============================================================================

class FileError(BaseError):
    """文件错误"""
    pass


class ProjectFileNotFoundError(FileError):
    """项目文件未找到错误"""
    pass


class ProjectFilePermissionError(FileError):
    """项目文件权限错误"""
    pass


class FileFormatError(FileError):
    """文件格式错误"""
    pass


# =============================================================================
# 缓存相关异常
# =============================================================================

class CacheError(BaseError):
    """缓存错误"""
    pass


class CacheKeyError(CacheError):
    """缓存键错误"""
    pass


class CacheSerializationError(CacheError):
    """缓存序列化错误"""
    pass


# =============================================================================
# 业务逻辑相关异常
# =============================================================================

class BusinessError(BaseError):
    """业务逻辑错误"""
    pass


class ResourceNotFoundError(BusinessError):
    """资源未找到错误"""
    pass


class ResourceExistsError(BusinessError):
    """资源已存在错误"""
    pass


class OperationNotAllowedError(BusinessError):
    """操作不被允许错误"""
    pass


class QuotaExceededError(BusinessError):
    """配额超限错误"""
    pass


class RateLimitError(BusinessError):
    """频率限制错误"""
    pass


# =============================================================================
# 系统相关异常
# =============================================================================

class SystemError(BaseError):
    """系统错误"""
    pass


class DependencyError(SystemError):
    """依赖错误"""
    pass


class CompatibilityError(SystemError):
    """兼容性错误"""
    pass


class InitializationError(SystemError):
    """初始化错误"""
    pass


# =============================================================================
# 异常处理装饰器
# =============================================================================

def handle_exceptions(exceptions: Union[Type[Exception], tuple] = Exception,
                     default_return: Any = None,
                     log_errors: bool = True,
                     reraise: bool = True,
                     callback: Optional[Callable] = None) -> Callable:
    """
    异常处理装饰器
    
    Args:
        exceptions: 要捕获的异常类型
        default_return: 默认返回值
        log_errors: 是否记录错误日志
        reraise: 是否重新抛出异常
        callback: 异常回调函数
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                if log_errors:
                    logger.error(f"函数 {func.__name__} 发生异常: {e}", exc_info=True)
                
                if callback:
                    try:
                        callback(e, func, args, kwargs)
                    except Exception as cb_error:
                        logger.error(f"异常回调函数执行失败: {cb_error}")
                
                if reraise:
                    raise
                
                return default_return
        
        return wrapper
    return decorator


def suppress_exceptions(exceptions: Union[Type[Exception], tuple] = Exception,
                       log_errors: bool = True,
                       default_return: Any = None) -> Callable:
    """
    抑制异常装饰器
    
    Args:
        exceptions: 要抑制的异常类型
        log_errors: 是否记录错误日志
        default_return: 默认返回值
        
    Returns:
        装饰器函数
    """
    return handle_exceptions(
        exceptions=exceptions,
        default_return=default_return,
        log_errors=log_errors,
        reraise=False
    )


def retry_on_exception(max_retries: int = 3,
                      delay: float = 1.0,
                      backoff: float = 2.0,
                      exceptions: Union[Type[Exception], tuple] = Exception,
                      log_errors: bool = True) -> Callable:
    """
    异常重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间
        backoff: 退避倍数
        exceptions: 要重试的异常类型
        log_errors: 是否记录错误日志
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        if log_errors:
                            logger.warning(
                                f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {e}, "
                                f"{current_delay} 秒后重试"
                            )
                        
                        import time
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        if log_errors:
                            logger.error(
                                f"函数 {func.__name__} 重试 {max_retries} 次后仍然失败: {e}",
                                exc_info=True
                            )
                        raise last_exception
            
            raise last_exception
        
        return wrapper
    return decorator


# =============================================================================
# 异常处理工具
# =============================================================================

class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化错误处理器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger(__name__)
        self.error_counts = {}
        self.error_callbacks = {}
        self.error_patterns = {}  # 错误模式检测
        self.recovery_strategies = {}  # 恢复策略
        self.circuit_breakers = {}  # 熔断器
    
    def handle_error(self, error: Exception, 
                    context: Optional[Dict[str, Any]] = None,
                    notify: bool = True) -> None:
        """
        处理错误
        
        Args:
            error: 异常对象
            context: 上下文信息
            notify: 是否通知
        """
        error_type = type(error).__name__
        
        # 记录错误次数
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # 记录日志
        self.logger.error(
            f"处理错误: {error_type} - {error}",
            extra={'context': context or {}},
            exc_info=True
        )
        
        # 执行回调
        if error_type in self.error_callbacks:
            try:
                self.error_callbacks[error_type](error, context)
            except Exception as callback_error:
                self.logger.error(f"错误回调执行失败: {callback_error}")
        
        # 通知处理
        if notify:
            self._notify_error(error, context)
    
    def _notify_error(self, error: Exception, 
                     context: Optional[Dict[str, Any]] = None) -> None:
        """通知错误"""
        # 这里可以实现邮件通知、短信通知等
        pass
    
    def register_callback(self, error_type: str, 
                         callback: Callable) -> None:
        """
        注册错误回调
        
        Args:
            error_type: 错误类型名称
            callback: 回调函数
        """
        self.error_callbacks[error_type] = callback
    
    def get_error_stats(self) -> Dict[str, int]:
        """获取错误统计"""
        return self.error_counts.copy()
    
    def reset_stats(self) -> None:
        """重置错误统计"""
        self.error_counts.clear()
    
    def register_recovery_strategy(self, error_type: str, 
                                 strategy: Callable[[Exception, Dict], Any]) -> None:
        """
        注册错误恢复策略
        
        Args:
            error_type: 错误类型名称
            strategy: 恢复策略函数
        """
        self.recovery_strategies[error_type] = strategy
    
    def add_error_pattern(self, pattern_name: str, 
                         error_types: tuple, 
                         threshold: int = 5,
                         time_window: int = 60) -> None:
        """
        添加错误模式检测
        
        Args:
            pattern_name: 模式名称
            error_types: 错误类型元组
            threshold: 阈值
            time_window: 时间窗口（秒）
        """
        self.error_patterns[pattern_name] = {
            'error_types': error_types,
            'threshold': threshold,
            'time_window': time_window,
            'occurrences': []
        }
    
    def check_error_patterns(self, error: Exception) -> Optional[str]:
        """
        检查错误模式
        
        Args:
            error: 异常对象
            
        Returns:
            匹配的模式名称，如果有的话
        """
        import time
        current_time = time.time()
        error_type = type(error).__name__
        
        for pattern_name, pattern_config in self.error_patterns.items():
            if any(error_type == et.__name__ if hasattr(et, '__name__') else str(et) 
                  for et in pattern_config['error_types']):
                
                # 清理过期的记录
                pattern_config['occurrences'] = [
                    t for t in pattern_config['occurrences']
                    if current_time - t <= pattern_config['time_window']
                ]
                
                # 添加当前错误
                pattern_config['occurrences'].append(current_time)
                
                # 检查是否超过阈值
                if len(pattern_config['occurrences']) >= pattern_config['threshold']:
                    return pattern_name
        
        return None
    
    def attempt_recovery(self, error: Exception, 
                        context: Optional[Dict[str, Any]] = None) -> Any:
        """
        尝试错误恢复
        
        Args:
            error: 异常对象
            context: 上下文信息
            
        Returns:
            恢复结果，如果成功的话
        """
        error_type = type(error).__name__
        
        if error_type in self.recovery_strategies:
            try:
                return self.recovery_strategies[error_type](error, context or {})
            except Exception as recovery_error:
                self.logger.error(f"恢复策略执行失败: {recovery_error}")
        
        return None


# =============================================================================
# 熔断器
# =============================================================================

class CircuitBreaker:
    """熔断器实现"""
    
    def __init__(self, failure_threshold: int = 5, 
                 timeout: int = 60,
                 expected_exception: Type[Exception] = Exception):
        """
        初始化熔断器
        
        Args:
            failure_threshold: 失败阈值
            timeout: 超时时间（秒）
            expected_exception: 预期的异常类型
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs):
        """
        通过熔断器调用函数
        
        Args:
            func: 要调用的函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            函数结果
            
        Raises:
            CircuitBreakerOpenError: 熔断器打开时
        """
        if self.state == 'OPEN':
            if self._should_attempt_reset():
                self.state = 'HALF_OPEN'
            else:
                raise CircuitBreakerOpenError(
                    f"熔断器打开，失败次数: {self.failure_count}"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置"""
        import time
        return (self.last_failure_time is not None and 
                time.time() - self.last_failure_time >= self.timeout)
    
    def _on_success(self):
        """成功时的处理"""
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def _on_failure(self):
        """失败时的处理"""
        import time
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'


class CircuitBreakerOpenError(BaseError):
    """熔断器打开错误"""
    pass


def circuit_breaker(failure_threshold: int = 5, 
                   timeout: int = 60,
                   expected_exception: Type[Exception] = Exception):
    """
    熔断器装饰器
    
    Args:
        failure_threshold: 失败阈值
        timeout: 超时时间（秒）
        expected_exception: 预期的异常类型
        
    Returns:
        装饰器函数
    """
    breaker = CircuitBreaker(failure_threshold, timeout, expected_exception)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# 上下文管理器
# =============================================================================

class error_context:
    """错误上下文管理器"""
    
    def __init__(self, error_handler: Optional[ErrorHandler] = None,
                 context: Optional[Dict[str, Any]] = None,
                 suppress: bool = False):
        """
        初始化错误上下文管理器
        
        Args:
            error_handler: 错误处理器
            context: 上下文信息
            suppress: 是否抑制异常
        """
        self.error_handler = error_handler or ErrorHandler()
        self.context = context or {}
        self.suppress = suppress
        self.error = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error = exc_val
            self.error_handler.handle_error(exc_val, self.context)
            
            if self.suppress:
                return True
        
        return False


# =============================================================================
# 异常信息格式化
# =============================================================================

def format_exception(error: Exception, 
                    include_traceback: bool = True) -> Dict[str, Any]:
    """
    格式化异常信息
    
    Args:
        error: 异常对象
        include_traceback: 是否包含堆栈跟踪
        
    Returns:
        格式化后的异常信息
    """
    error_info = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'error_args': error.args,
    }
    
    # 如果是自定义异常，包含额外信息
    if isinstance(error, BaseError):
        error_info.update(error.to_dict())
    
    # 包含堆栈跟踪
    if include_traceback:
        error_info['traceback'] = traceback.format_exc()
    
    return error_info


def get_exception_chain(error: Exception) -> list:
    """
    获取异常链
    
    Args:
        error: 异常对象
        
    Returns:
        异常链列表
    """
    chain = []
    current = error
    
    while current is not None:
        chain.append({
            'type': type(current).__name__,
            'message': str(current),
            'args': current.args
        })
        current = current.__cause__ or current.__context__
    
    return chain


# =============================================================================
# 全局异常处理
# =============================================================================

def setup_global_exception_handler(error_handler: Optional[ErrorHandler] = None):
    """
    设置全局异常处理器
    
    Args:
        error_handler: 错误处理器
    """
    handler = error_handler or ErrorHandler()
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        """全局异常处理函数"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        handler.handle_error(exc_value, {
            'exc_type': exc_type.__name__,
            'exc_traceback': ''.join(traceback.format_tb(exc_traceback))
        })
    
    sys.excepthook = handle_exception


# 创建全局错误处理器实例
global_error_handler = ErrorHandler()


# =============================================================================
# 便捷函数
# =============================================================================

def safe_execute(func: Callable, *args, default_return: Any = None, 
                log_errors: bool = True, **kwargs) -> Any:
    """
    安全执行函数
    
    Args:
        func: 要执行的函数
        *args: 位置参数
        default_return: 默认返回值
        log_errors: 是否记录错误日志
        **kwargs: 关键字参数
        
    Returns:
        函数结果或默认值
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger.error(f"安全执行函数 {func.__name__} 失败: {e}", exc_info=True)
        return default_return


def ensure_exception_type(error: Any, 
                         exception_type: Type[Exception] = BaseError) -> Exception:
    """
    确保异常类型
    
    Args:
        error: 错误对象
        exception_type: 期望的异常类型
        
    Returns:
        异常对象
    """
    if isinstance(error, Exception):
        return error
    elif isinstance(error, str):
        return exception_type(error)
    else:
        return exception_type(f"未知错误: {error}")


def reraise_with_context(error: Exception, context: str) -> None:
    """
    重新抛出异常并添加上下文
    
    Args:
        error: 原始异常
        context: 上下文信息
    """
    new_message = f"{context}: {error}"
    if isinstance(error, BaseError):
        error.message = new_message
        raise error
    else:
        raise type(error)(new_message) from error