"""高级日志处理工具模块。

提供灵活的日志配置、结构化日志、异步日志和性能监控功能。
"""

import json
import logging
import logging.config
import os
import sys
import threading
import time
import traceback
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union


class JsonFormatter(logging.Formatter):
    """JSON格式的日志格式化器。"""
    
    def __init__(self, include_extra: bool = True):
        """初始化JSON格式化器。
        
        Args:
            include_extra: 是否包含额外字段
        """
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为JSON。
        
        Args:
            record: 日志记录
            
        Returns:
            格式化后的JSON字符串
        """
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # 添加额外字段
        if self.include_extra:
            for key, value in record.__dict__.items():
                if key not in log_data and not key.startswith('_'):
                    # 过滤标准字段
                    if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                                 'pathname', 'filename', 'module', 'exc_info', 
                                 'exc_text', 'stack_info', 'lineno', 'funcName', 
                                 'created', 'msecs', 'relativeCreated', 'thread',
                                 'threadName', 'processName', 'process', 'getMessage']:
                        log_data["extra"] = log_data.get("extra", {})
                        log_data["extra"][key] = value
        
        return json.dumps(log_data, ensure_ascii=False, default=str)


class PerformanceFilter(logging.Filter):
    """性能监控日志过滤器。"""
    
    def __init__(self, min_duration: float = 0.0):
        """初始化性能过滤器。
        
        Args:
            min_duration: 最小记录时长（秒）
        """
        super().__init__()
        self.min_duration = min_duration
    
    def filter(self, record: logging.LogRecord) -> bool:
        """过滤性能日志。
        
        Args:
            record: 日志记录
            
        Returns:
            是否应该记录该日志
        """
        # 如果记录包含duration字段，检查是否超过最小时长
        if hasattr(record, 'duration'):
            return record.duration >= self.min_duration
        return True


class LoggerManager:
    """日志管理器，提供集中的日志配置和管理。"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.loggers: Dict[str, logging.Logger] = {}
            self.config: Dict[str, Any] = {}
            self.initialized = True
    
    def setup_from_config(self, config_path: Union[str, Path]) -> None:
        """从配置文件设置日志。
        
        Args:
            config_path: 配置文件路径
        """
        if isinstance(config_path, str):
            config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"日志配置文件不存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.suffix.lower() == '.json':
                self.config = json.load(f)
            else:
                import yaml
                self.config = yaml.safe_load(f)
        
        logging.config.dictConfig(self.config)
    
    def get_logger(self, name: str) -> logging.Logger:
        """获取日志记录器。
        
        Args:
            name: 日志记录器名称
            
        Returns:
            日志记录器实例
        """
        if name not in self.loggers:
            self.loggers[name] = logging.getLogger(name)
        return self.loggers[name]


def setup_advanced_logger(
    name: Optional[str] = None,
    level: Union[str, int] = logging.INFO,
    log_file: Optional[Union[str, Path]] = None,
    log_format: str = "standard",
    date_format: str = "%Y-%m-%d %H:%M:%S",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    enable_rotation: bool = "yes" == "yes",
    json_format: bool = False,
    include_console: bool = True,
    performance_threshold: float = 0.0
) -> logging.Logger:
    """设置高级日志记录器。
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        log_file: 日志文件路径
        log_format: 日志格式
        date_format: 日期格式
        max_bytes: 单文件最大字节数
        backup_count: 备份文件数量
        enable_rotation: 是否启用文件轮转
        json_format: 是否使用JSON格式
        include_console: 是否包含控制台输出
        performance_threshold: 性能监控阈值
        
    Returns:
        配置好的日志记录器
    """
    # 处理字符串级别
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    
    # 获取logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 清除现有handlers
    logger.handlers.clear()
    
    # 选择格式化器
    if json_format or log_format == "json":
        formatter = JsonFormatter()
    else:
        if log_format == "standard":
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        elif log_format == "custom":
            format_string = "[%(asctime)s] %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s"
        else:
            format_string = log_format
        formatter = logging.Formatter(format_string, date_format)
    
    # 添加控制台handler
    if include_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        
        # 添加性能过滤器
        if performance_threshold > 0:
            console_handler.addFilter(PerformanceFilter(performance_threshold))
        
        logger.addHandler(console_handler)
    
    # 添加文件handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        if enable_rotation:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
        else:
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
        
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        
        # 添加性能过滤器
        if performance_threshold > 0:
            file_handler.addFilter(PerformanceFilter(performance_threshold))
        
        logger.addHandler(file_handler)
    
    return logger


def get_project_logger(module_name: str = None, log_file: Union[str, Path] = None) -> logging.Logger:
    """获取项目专用的日志记录器。
    
    Args:
        module_name: 模块名称，默认使用调用者的模块名
        log_file: 自定义日志文件路径，优先级高于默认配置
        
    Returns:
        项目日志记录器
    """
    if module_name is None:
        # 获取调用者的模块名
        import inspect
        frame = inspect.currentframe().f_back
        module_name = frame.f_globals.get('__name__', 'unknown')
    
    project_name = "my_python_project"
    logger_name = f"{project_name}.{module_name}"
    
    # 如果还没有配置过，使用默认配置
    logger = logging.getLogger(logger_name)
    if not logger.handlers:
        # 确定日志文件路径
        if log_file is not None:
            # 用户指定了自定义路径
            final_log_file = log_file
        elif "yes" == "yes":
            # 使用默认路径
            final_log_file = "logs/my_python_project.log"
        else:
            # 不使用文件日志
            final_log_file = None
            
        return setup_advanced_logger(
            name=logger_name,
            level="INFO",
            log_file=final_log_file,
            json_format="standard" == "json"
        )
    
    return logger


def log_performance(logger: Optional[logging.Logger] = None, 
                   level: int = logging.INFO,
                   include_args: bool = False):
    """性能监控装饰器。
    
    Args:
        logger: 日志记录器，默认使用模块logger
        level: 日志级别
        include_args: 是否包含函数参数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_project_logger(func.__module__)
            
            start_time = time.time()
            func_name = func.__qualname__
            
            try:
                # 记录函数开始
                if include_args:
                    args_repr = [repr(a) for a in args[:3]]  # 限制参数数量
                    kwargs_repr = [f"{k}={v!r}" for k, v in list(kwargs.items())[:3]]
                    signature = ", ".join(args_repr + kwargs_repr)
                    logger.log(level, f"开始执行 {func_name}({signature})")
                else:
                    logger.log(level, f"开始执行 {func_name}")
                
                # 执行函数
                result = func(*args, **kwargs)
                
                # 记录性能数据
                duration = time.time() - start_time
                logger.log(level, f"{func_name} 执行完成", 
                          extra={"duration": duration, "function": func_name, "status": "success"})
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{func_name} 执行出错: {str(e)}", 
                           extra={"duration": duration, "function": func_name, 
                                "status": "error", "error": str(e)},
                           exc_info=True)
                raise
        
        return wrapper
    return decorator


@contextmanager
def log_context(logger: logging.Logger, context_name: str, level: int = logging.INFO):
    """日志上下文管理器。
    
    Args:
        logger: 日志记录器
        context_name: 上下文名称
        level: 日志级别
    """
    start_time = time.time()
    logger.log(level, f"进入上下文: {context_name}")
    
    try:
        yield
        duration = time.time() - start_time
        logger.log(level, f"退出上下文: {context_name}", 
                  extra={"duration": duration, "context": context_name, "status": "success"})
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"上下文异常: {context_name} - {str(e)}", 
                    extra={"duration": duration, "context": context_name, 
                          "status": "error", "error": str(e)},
                    exc_info=True)
        raise


def log_function_call(logger: Optional[logging.Logger] = None, 
                     level: int = logging.DEBUG,
                     log_args: bool = True,
                     log_result: bool = False):
    """函数调用日志装饰器（增强版）。
    
    Args:
        logger: 日志记录器
        level: 日志级别
        log_args: 是否记录参数
        log_result: 是否记录返回值
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_project_logger(func.__module__)
            
            func_name = func.__qualname__
            
            # 记录函数调用
            if log_args:
                args_repr = [repr(a) for a in args[:3]]
                kwargs_repr = [f"{k}={v!r}" for k, v in list(kwargs.items())[:3]]
                signature = ", ".join(args_repr + kwargs_repr)
                logger.log(level, f"调用函数 {func_name}({signature})")
            else:
                logger.log(level, f"调用函数 {func_name}")
            
            try:
                result = func(*args, **kwargs)
                
                if log_result:
                    result_repr = repr(result)[:100]  # 限制长度
                    logger.log(level, f"{func_name} 返回: {result_repr}")
                
                return result
                
            except Exception as e:
                logger.exception(f"函数 {func_name} 执行出错: {str(e)}")
                raise
        
        return wrapper
    return decorator


# 为向后兼容保留的简化函数
def setup_logger(name: Optional[str] = None, **kwargs) -> logging.Logger:
    """简化的日志配置函数（向后兼容）。"""
    return setup_advanced_logger(name=name, **kwargs)


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器（向后兼容）。"""
    return get_project_logger(name)


def create_rotating_log(log_dir: Union[str, Path], name: str, **kwargs) -> logging.Logger:
    """创建轮转日志（向后兼容）。"""
    log_file = Path(log_dir) / f"{name}.log"
    return setup_advanced_logger(name=name, log_file=log_file, enable_rotation=True, **kwargs)


def configure_project_logging(
    log_dir: Union[str, Path] = "logs",
    log_level: Union[str, int] = "INFO",
    log_format: str = "standard",
    enable_file_logging: bool = "yes" == "yes",
    enable_rotation: bool = "yes" == "yes",
    console_output: bool = True,
    custom_log_files: Optional[Dict[str, Union[str, Path]]] = None
) -> Dict[str, logging.Logger]:
    """配置项目日志系统，支持用户自定义路径。
    
    Args:
        log_dir: 日志目录，可以是相对路径或绝对路径
        log_level: 日志级别
        log_format: 日志格式
        enable_file_logging: 是否启用文件日志
        enable_rotation: 是否启用日志轮转
        console_output: 是否输出到控制台
        custom_log_files: 自定义日志文件映射 {"logger_name": "file_path"}
        
    Returns:
        配置好的日志记录器字典
        
    Example:
        >>> # 使用默认配置
        >>> loggers = configure_project_logging()
        >>> 
        >>> # 自定义日志目录
        >>> loggers = configure_project_logging(
        ...     log_dir="/var/log/myapp",
        ...     log_level="DEBUG"
        ... )
        >>> 
        >>> # 为不同模块指定不同的日志文件
        >>> loggers = configure_project_logging(
        ...     custom_log_files={
        ...         "database": "/var/log/myapp/db.log",
        ...         "api": "/var/log/myapp/api.log",
        ...         "worker": "/var/log/myapp/worker.log"
        ...     }
        ... )
    """
    # 标准化日志目录路径
    if isinstance(log_dir, str):
        log_dir = Path(log_dir)
    
    # 确保日志目录存在
    if enable_file_logging:
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建配置好的日志记录器
    loggers = {}
    
    # 主项目日志记录器
    main_log_file = None
    if enable_file_logging:
        main_log_file = log_dir / f"my_python_project.log"
    
    loggers["main"] = setup_advanced_logger(
        name="my_python_project",
        level=log_level,
        log_file=main_log_file,
        log_format=log_format,
        enable_rotation=enable_rotation,
        include_console=console_output
    )
    
    # 错误日志记录器
    if enable_file_logging:
        error_log_file = log_dir / f"my_python_project_errors.log"
        loggers["error"] = setup_advanced_logger(
            name="my_python_project.errors",
            level="ERROR",
            log_file=error_log_file,
            log_format=log_format,
            enable_rotation=enable_rotation,
            include_console=False  # 错误日志不需要控制台输出
        )
    
    # 性能日志记录器
    if enable_file_logging:
        performance_log_file = log_dir / f"my_python_project_performance.log"
        loggers["performance"] = setup_advanced_logger(
            name="my_python_project.performance",
            level="INFO",
            log_file=performance_log_file,
            log_format="json",  # 性能日志强制使用JSON格式
            enable_rotation=enable_rotation,
            include_console=False,
            performance_threshold=0.1  # 只记录超过0.1秒的操作
        )
    
    # 自定义日志记录器
    if custom_log_files:
        for logger_name, file_path in custom_log_files.items():
            if isinstance(file_path, str):
                file_path = Path(file_path)
            
            # 确保自定义日志文件的目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            full_logger_name = f"my_python_project.{logger_name}"
            loggers[logger_name] = setup_advanced_logger(
                name=full_logger_name,
                level=log_level,
                log_file=file_path,
                log_format=log_format,
                enable_rotation=enable_rotation,
                include_console=console_output
            )
    
    return loggers


def get_configured_logger(
    name: str,
    log_file: Union[str, Path] = None,
    log_level: Union[str, int] = None,
    log_format: str = None,
    **kwargs
) -> logging.Logger:
    """获取一个配置好的日志记录器，支持完全自定义。
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件路径（可以是绝对路径或相对路径）
        log_level: 日志级别
        log_format: 日志格式
        **kwargs: 其他传递给 setup_advanced_logger 的参数
        
    Returns:
        配置好的日志记录器
        
    Example:
        >>> # 使用默认配置
        >>> logger = get_configured_logger("my_module")
        >>> 
        >>> # 自定义日志文件
        >>> logger = get_configured_logger(
        ...     "my_module",
        ...     log_file="/var/log/myapp/custom.log",
        ...     log_level="DEBUG"
        ... )
        >>> 
        >>> # 使用相对路径
        >>> logger = get_configured_logger(
        ...     "my_module",
        ...     log_file="logs/modules/my_module.log"
        ... )
    """
    # 使用默认值填充未指定的参数
    if log_level is None:
        log_level = "INFO"
    if log_format is None:
        log_format = "standard"
    
    # 处理日志文件路径
    if log_file is not None:
        if isinstance(log_file, str):
            log_file = Path(log_file)
        
        # 确保日志文件目录存在
        log_file.parent.mkdir(parents=True, exist_ok=True)
    elif "yes" == "yes":
        # 如果没有指定文件但启用了文件日志，使用默认路径
        log_file = Path("logs") / f"{name.replace('.', '_')}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 构建完整的日志记录器名称
    if not name.startswith("my_python_project"):
        full_name = f"my_python_project.{name}"
    else:
        full_name = name
    
    return setup_advanced_logger(
        name=full_name,
        level=log_level,
        log_file=log_file,
        log_format=log_format,
        **kwargs
    )


# 环境变量支持
def get_log_path_from_env(default_path: str = "logs") -> Path:
    """从环境变量获取日志路径。
    
    Args:
        default_path: 默认日志路径
        
    Returns:
        日志路径
        
    Environment Variables:
        MY_PYTHON_PROJECT_LOG_DIR: 日志目录路径
        MY_PYTHON_PROJECT_LOG_FILE: 完整日志文件路径
    """
    
    # 检查完整文件路径
    log_file = os.getenv(f"MY_PYTHON_PROJECT_LOG_FILE")
    if log_file:
        return Path(log_file)
    
    # 检查日志目录
    log_dir = os.getenv(f"MY_PYTHON_PROJECT_LOG_DIR", default_path)
    return Path(log_dir) / f"my_python_project.log"


# 模块级别的默认logger
default_logger = get_project_logger(__name__)

# 便捷函数：获取带自定义路径的项目日志记录器
def get_logger_with_path(log_path: Union[str, Path], module_name: str = None) -> logging.Logger:
    """获取指定路径的项目日志记录器（便捷函数）。
    
    Args:
        log_path: 日志文件路径
        module_name: 模块名称
        
    Returns:
        日志记录器
    """
    if module_name is None:
        import inspect
        frame = inspect.currentframe().f_back
        module_name = frame.f_globals.get('__name__', 'unknown')
    
    return get_project_logger(module_name, log_file=log_path)


# 路径管理器集成
def setup_logging_with_path_manager(
    path_manager,
    module_name: str = None,
    log_filename: str = "application.log",
    **logger_kwargs
) -> logging.Logger:
    """
    使用路径管理器设置日志系统
    
    Args:
        path_manager: ProjectPathManager实例
        module_name: 模块名称
        log_filename: 日志文件名
        **logger_kwargs: 传递给setup_advanced_logger的其他参数
        
    Returns:
        配置好的日志记录器
        
    Example:
        >>> from my_python_project.utils.path_manager import ProjectPathManager
        >>> pm = ProjectPathManager("/var/data/myproject")
        >>> logger = setup_logging_with_path_manager(pm, __name__)
    """
    if module_name is None:
        import inspect
        frame = inspect.currentframe().f_back
        module_name = frame.f_globals.get('__name__', 'unknown')
    
    # 从路径管理器获取日志路径
    log_path = path_manager.get_log_path(log_filename)
    
    # 设置默认参数
    logger_kwargs.setdefault('level', "INFO")
    logger_kwargs.setdefault('log_format', "standard")
    logger_kwargs.setdefault('enable_rotation', "yes" == "yes")
    
    return setup_advanced_logger(
        name=f"my_python_project.{module_name}",
        log_file=log_path,
        **logger_kwargs
    )


def configure_project_logging_with_paths(
    path_manager,
    log_configs: Optional[Dict[str, Dict]] = None,
    **base_config
) -> Dict[str, logging.Logger]:
    """
    使用路径管理器配置完整的项目日志系统
    
    Args:
        path_manager: ProjectPathManager实例
        log_configs: 日志配置字典 {"logger_name": {"filename": "xxx.log", ...}}
        **base_config: 基础配置参数
        
    Returns:
        配置好的日志记录器字典
        
    Example:
        >>> pm = ProjectPathManager("/var/data/myproject")
        >>> loggers = configure_project_logging_with_paths(
        ...     pm,
        ...     log_configs={
        ...         "main": {"filename": "main.log"},
        ...         "database": {"filename": "db.log", "log_format": "json"},
        ...         "api": {"filename": "api.log", "log_level": "DEBUG"}
        ...     }
        ... )
    """
    if log_configs is None:
        log_configs = {
            "main": {"filename": "my_python_project.log"},
            "error": {"filename": "errors.log", "log_level": "ERROR"},
            "performance": {"filename": "performance.log", "log_format": "json", "performance_threshold": 0.1}
        }
    
    loggers = {}
    
    for logger_name, config in log_configs.items():
        # 合并配置
        merged_config = {**base_config, **config}
        filename = merged_config.pop("filename", f"{logger_name}.log")
        
        # 获取日志路径
        log_path = path_manager.get_log_path(filename)
        
        # 设置默认值
        merged_config.setdefault('level', "INFO")
        merged_config.setdefault('log_format', "standard")
        merged_config.setdefault('enable_rotation', "yes" == "yes")
        
        # 创建日志记录器
        full_logger_name = f"my_python_project.{logger_name}"
        loggers[logger_name] = setup_advanced_logger(
            name=full_logger_name,
            log_file=log_path,
            **merged_config
        )
    
    return loggers


def auto_setup_project_logging(
    base_dir: Union[str, Path] = None,
    session_name: str = None,
    cleanup_old: bool = True,
    **path_manager_kwargs
):
    """
    自动设置项目日志系统和路径管理
    
    这是一个一站式函数，自动创建路径管理器和配置日志系统
    
    Args:
        base_dir: 项目基础目录，默认使用环境变量或当前目录
        session_name: 会话名称，默认使用时间戳
        cleanup_old: 是否清理旧会话
        **path_manager_kwargs: 传递给ProjectPathManager的其他参数
        
    Returns:
        (主日志记录器, 路径管理器实例)
        
    Example:
        >>> # 一行代码设置所有内容
        >>> logger, pm = auto_setup_project_logging("/var/data/myproject")
        >>> logger.info("项目启动")
        >>> model_path = pm.get_model_path("trained_model.pkl")
    """
    from .path_manager import ProjectPathManager, init_project_paths
    
    # 确定基础目录
    if base_dir is None:
        import os
        # 优先使用环境变量
        base_dir = os.getenv(f"MY_PYTHON_PROJECT_BASE_DIR")
        if not base_dir:
            base_dir = os.getenv(f"MY_PYTHON_PROJECT_LOG_DIR", ".")
    
    # 创建路径管理器
    path_manager = init_project_paths(
        base_dir=base_dir,
        session_name=session_name,
        **path_manager_kwargs
    )
    
    # 清理旧会话
    if cleanup_old:
        path_manager.cleanup_old_sessions()
    
    # 配置日志系统
    loggers = configure_project_logging_with_paths(path_manager)
    main_logger = loggers["main"]
    
    # 记录初始化信息
    main_logger.info(f"My Python Project 项目启动")
    main_logger.info(f"会话目录: {path_manager.session_dir}")
    main_logger.info(f"日志目录: {path_manager.logs_dir}")
    
    return main_logger, path_manager


def load_logging_config_from_file(
    config_file: Union[str, Path] = None,
    config_format: str = "auto"
) -> bool:
    """从配置文件加载日志配置。
    
    Args:
        config_file: 配置文件路径，默认自动查找
        config_format: 配置文件格式 ("json", "yaml", "auto")
        
    Returns:
        是否成功加载配置
        
    Example:
        >>> # 加载默认配置文件
        >>> load_logging_config_from_file()
        
        >>> # 加载指定配置文件
        >>> load_logging_config_from_file("config/custom_logging.json")
    """
    try:
        import yaml
    except ImportError:
        yaml = None
    
    # 确定配置文件路径
    if config_file is None:
        # 自动查找配置文件
        config_dir = Path("config")
        
        # 优先查找基于cookiecutter配置的文件
        preferred_format = "standard"
        if preferred_format == "json":
            config_file = config_dir / "logging_config.json"
        else:
            config_file = config_dir / "logging_config.yaml"
        
        # 如果首选文件不存在，查找其他格式
        if not config_file.exists():
            for ext in [".json", ".yaml", ".yml"]:
                alt_config = config_dir / f"logging_config{ext}"
                if alt_config.exists():
                    config_file = alt_config
                    break
    else:
        config_file = Path(config_file)
    
    if not config_file.exists():
        print(f"警告: 日志配置文件 {config_file} 不存在，使用默认配置")
        return False
    
    # 确定文件格式
    if config_format == "auto":
        if config_file.suffix.lower() in [".yaml", ".yml"]:
            config_format = "yaml"
        elif config_file.suffix.lower() == ".json":
            config_format = "json"
        else:
            # 尝试根据内容判断
            content = config_file.read_text(encoding='utf-8')
            if content.strip().startswith('{'):
                config_format = "json"
            else:
                config_format = "yaml"
    
    try:
        # 读取配置文件
        content = config_file.read_text(encoding='utf-8')
        
        # 解析配置
        if config_format == "json":
            import json
            config = json.loads(content)
        elif config_format == "yaml":
            if yaml is None:
                print("错误: 需要安装PyYAML来加载YAML配置文件")
                return False
            config = yaml.safe_load(content)
        else:
            print(f"错误: 不支持的配置格式 {config_format}")
            return False
        
        # 应用配置
        logging.config.dictConfig(config)
        print(f"成功加载日志配置: {config_file}")
        return True
        
    except Exception as e:
        print(f"加载日志配置失败: {e}")
        return False


def init_project_logging(
    config_file: Union[str, Path] = None,
    fallback_to_default: bool = True,
    **default_config
) -> logging.Logger:
    """初始化项目日志系统。
    
    首先尝试从配置文件加载，失败时使用默认配置。
    
    Args:
        config_file: 配置文件路径
        fallback_to_default: 是否在配置文件加载失败时使用默认配置
        **default_config: 默认配置参数
        
    Returns:
        主日志记录器
        
    Example:
        >>> # 使用配置文件初始化
        >>> logger = init_project_logging()
        
        >>> # 指定配置文件
        >>> logger = init_project_logging("config/production_logging.yaml")
        
        >>> # 带默认配置的初始化
        >>> logger = init_project_logging(
        ...     fallback_to_default=True,
        ...     log_level="DEBUG",
        ...     log_format="json"
        ... )
    """
    # 尝试加载配置文件
    config_loaded = load_logging_config_from_file(config_file)
    
    if not config_loaded and fallback_to_default:
        # 配置文件加载失败，使用默认配置
        print("使用默认日志配置")
        
        # 设置默认值
        default_config.setdefault('log_level', "INFO")
        default_config.setdefault('log_format', "standard")
        default_config.setdefault('enable_file_logging', "yes" == "yes")
        default_config.setdefault('enable_rotation', "yes" == "yes")
        
        # 配置默认日志系统
        configure_project_logging(**default_config)
    
    # 返回主日志记录器
    return get_project_logger("main")


def get_effective_logging_config() -> Dict[str, Any]:
    """获取当前有效的日志配置信息。
    
    Returns:
        当前日志配置的字典表示
    """
    config_info = {
        "loggers": {},
        "handlers": {},
        "formatters": {},
        "project_settings": {
            "default_level": "INFO",
            "default_format": "standard",
            "file_logging_enabled": "yes" == "yes",
            "log_rotation_enabled": "yes" == "yes",
        }
    }
    
    # 收集当前日志记录器信息
    for name, logger in logging.getLogger().manager.loggerDict.items():
        if isinstance(logger, logging.Logger) and name.startswith("my_python_project"):
            config_info["loggers"][name] = {
                "level": logger.level,
                "handlers": [h.__class__.__name__ for h in logger.handlers],
                "propagate": logger.propagate
            }
    
    return config_info