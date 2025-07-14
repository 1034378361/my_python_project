"""Top-level package for My Python Project."""

import logging
import os

__author__ = """周元琦"""
__email__ = "zyq1034378361@gmail.com"

# 版本号获取，优先级：包元数据 > _version.py > fallback
# 多级版本获取机制，确保在任何环境下都能正确获取版本号
# Python 3.11+ 原生支持 importlib.metadata，符合最佳实践文档要求
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("my_python_project")
except PackageNotFoundError:
    # 开发环境或未安装的包，尝试从_version.py获取
    try:
        from ._version import __version__
    except ImportError:
        __version__ = "0.1.0"  # fallback版本


# 配置日志系统
# 尝试从配置文件初始化日志，如果失败则使用基本配置
try:
    from .utils.logging_utils import auto_setup_project_logging, get_project_logger

    # 初始化高级日志系统
    auto_setup_project_logging()
    logger = get_project_logger()
    logger.info(f"My Python Project v{__version__} 启动")
except Exception:
    # 回退到基本日志配置
    logging.basicConfig(
        level=logging.INFO
        if os.environ.get("DEBUG", "").lower() not in ("1", "true")
        else logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("my_python_project")
    logger.warning("使用基本日志配置（高级日志系统初始化失败）")

# 导入工具函数
from . import utils

# 导出核心功能模块 - 只导出最常用的接口，减少启动时间
try:
    # 核心工具
    from .utils.cache import FileCache, MemoryCache, MultiLevelCache, cache_result
    from .utils.common import (
        deep_merge,
        format_datetime,
        is_valid_email,
        now_timestamp,
        retry_on_failure,
        safe_filename,
        timing_decorator,
    )
    from .utils.config_manager import ConfigManager
    from .utils.exceptions import (
        BaseError,
        CacheError,
        ConfigError,
        ErrorHandler,
        ValidationError,
        handle_exceptions,
    )
    from .utils.logging_utils import (
        auto_setup_project_logging,
        get_project_logger,
        init_project_logging,
        load_logging_config_from_file,
    )
    from .utils.path_manager import ProjectPathManager, init_project_paths
    from .utils.performance import PerformanceMonitor, benchmark
    from .utils.validators import (
        DictValidator,
        EmailValidator,
        NumberValidator,
        StringValidator,
        validate_data,
    )

    __all__ = [
        # 版本和基础
        "__version__",
        "utils",
        # 核心功能
        "get_project_logger",
        "auto_setup_project_logging",
        "load_logging_config_from_file",
        "init_project_logging",
        "ConfigManager",
        "validate_data",
        "MemoryCache",
        "FileCache",
        "MultiLevelCache",
        "cache_result",
        # 性能监控
        "PerformanceMonitor",
        "benchmark",
        # 路径管理
        "ProjectPathManager",
        "init_project_paths",
        # 验证器
        "StringValidator",
        "NumberValidator",
        "DictValidator",
        "EmailValidator",
        # 异常处理
        "BaseError",
        "ConfigError",
        "ValidationError",
        "CacheError",
        "handle_exceptions",
        "ErrorHandler",
        # 常用工具
        "now_timestamp",
        "format_datetime",
        "safe_filename",
        "deep_merge",
        "retry_on_failure",
        "timing_decorator",
        "is_valid_email",
    ]

except ImportError as e:
    logger.warning(f"某些模块导入失败，可能影响功能可用性: {e}")
    __all__ = ["__version__", "utils"]
