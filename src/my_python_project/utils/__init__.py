"""工具函数包。

此包包含项目中使用的各种实用工具函数。
"""

# 明确导入各模块的主要功能
from .logging_utils import get_project_logger, log_performance, log_function_call
from .path_manager import ProjectPathManager, get_project_paths
from .config_manager import ConfigManager, get_config, set_config
from .validators import validate_data, StringValidator, NumberValidator
from .cache import MemoryCache, FileCache, cache_result
from .exceptions import (
    BaseError,
    ConfigError,
    ValidationError,
    CacheError,
    handle_exceptions,
    ErrorHandler,
)
from .common import (
    # 时间工具
    now_timestamp,
    format_datetime,
    parse_datetime,
    # 文件工具
    safe_filename,
    slugify,
    ensure_dir,
    load_json,
    save_json,
    load_yaml,
    save_yaml,
    list_files,
    get_file_size,
    # 数据工具
    deep_merge,
    flatten_dict,
    clean_text,
    chunk_list,
    calculate_md5,
    calculate_sha256,
    get_date_range,
    # 装饰器
    retry_on_failure,
    timing_decorator,
    # 验证工具
    is_valid_email,
    is_valid_url,
    # 其他工具
    generate_random_string,
    generate_uuid,
)

__all__ = [
    # 日志工具
    "get_project_logger",
    "log_performance",
    "log_function_call",
    # 路径管理
    "ProjectPathManager",
    "get_project_paths",
    # 配置管理
    "ConfigManager",
    "get_config",
    "set_config",
    # 数据验证
    "validate_data",
    "StringValidator",
    "NumberValidator",
    # 缓存
    "MemoryCache",
    "FileCache",
    "cache_result",
    # 异常处理
    "BaseError",
    "ConfigError",
    "ValidationError",
    "CacheError",
    "handle_exceptions",
    "ErrorHandler",
    # 时间工具
    "now_timestamp",
    "format_datetime",
    "parse_datetime",
    # 文件工具
    "safe_filename",
    "slugify",
    "ensure_dir",
    "load_json",
    "save_json",
    "load_yaml",
    "save_yaml",
    "list_files",
    "get_file_size",
    # 数据工具
    "deep_merge",
    "flatten_dict",
    "clean_text",
    "chunk_list",
    "calculate_md5",
    "calculate_sha256",
    "get_date_range",
    # 装饰器
    "retry_on_failure",
    "timing_decorator",
    # 验证工具
    "is_valid_email",
    "is_valid_url",
    # 其他工具
    "generate_random_string",
    "generate_uuid",
]
