"""
通用工具函数库

提供日常开发中常用的工具函数，包括时间处理、字符串工具、文件操作、数据结构操作等。
"""

import functools
import hashlib
import json
import os
import re
import time
import unicodedata
import warnings
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


# =============================================================================
# 时间处理工具
# =============================================================================


def now_timestamp() -> int:
    """获取当前时间戳（秒）"""
    return int(time.time())


def now_timestamp_ms() -> int:
    """获取当前时间戳（毫秒）"""
    return int(time.time() * 1000)


def format_datetime(
    dt: Optional[datetime] = None, fmt: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """
    格式化日期时间

    Args:
        dt: 日期时间对象，默认为当前时间
        fmt: 格式字符串

    Returns:
        格式化后的时间字符串
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(fmt)


def parse_datetime(date_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    解析日期时间字符串

    Args:
        date_str: 日期时间字符串
        fmt: 格式字符串

    Returns:
        解析后的日期时间对象
    """
    return datetime.strptime(date_str, fmt)


def utc_now() -> datetime:
    """获取UTC时间"""
    return datetime.now(timezone.utc)


def local_now() -> datetime:
    """获取本地时间"""
    return datetime.now()


def to_utc(dt: datetime) -> datetime:
    """转换为UTC时间"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def from_timestamp(timestamp: Union[int, float], use_utc: bool = False) -> datetime:
    """
    从时间戳创建日期时间对象

    Args:
        timestamp: 时间戳
        use_utc: 是否使用UTC时间

    Returns:
        日期时间对象
    """
    if use_utc:
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return datetime.fromtimestamp(timestamp)


# =============================================================================
# 字符串工具
# =============================================================================


def safe_filename(filename: str, replacement: str = "_") -> str:
    """
    清理文件名，移除不安全字符

    Args:
        filename: 原始文件名
        replacement: 替换字符

    Returns:
        安全的文件名
    """
    # 移除控制字符
    filename = "".join(c for c in filename if ord(c) >= 32)

    # 替换不安全字符
    unsafe_chars = r'[<>:"/\\|?*]'
    filename = re.sub(unsafe_chars, replacement, filename)

    # 移除开头和结尾的点和空格
    filename = filename.strip(". ")

    # 限制长度
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[: 200 - len(ext)] + ext

    return filename or "untitled"


def slugify(text: str, separator: str = "-") -> str:
    """
    将文本转换为URL友好的slug

    Args:
        text: 原始文本
        separator: 分隔符

    Returns:
        URL友好的字符串
    """
    # 规范化unicode
    text = unicodedata.normalize("NFKD", text)
    # 转换为ASCII
    text = text.encode("ascii", "ignore").decode("ascii")
    # 转换为小写
    text = text.lower()
    # 替换非字母数字字符
    text = re.sub(r"[^a-z0-9]+", separator, text)
    # 移除开头和结尾的分隔符
    text = text.strip(separator)
    return text


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截断字符串

    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 后缀

    Returns:
        截断后的字符串
    """
    if len(text) <= max_length:
        return text

    if max_length <= len(suffix):
        return suffix[:max_length]

    return text[: max_length - len(suffix)] + suffix


def clean_whitespace(text: str) -> str:
    """清理多余的空白字符"""
    return re.sub(r"\s+", " ", text.strip())


def extract_numbers(text: str) -> List[str]:
    """从字符串中提取所有数字"""
    return re.findall(r"\d+\.?\d*", text)


def mask_sensitive_data(text: str, mask_char: str = "*", show_chars: int = 4) -> str:
    """
    掩码敏感数据

    Args:
        text: 原始文本
        mask_char: 掩码字符
        show_chars: 显示的字符数

    Returns:
        掩码后的文本
    """
    if len(text) <= show_chars:
        return mask_char * len(text)

    return text[:show_chars] + mask_char * (len(text) - show_chars)


# =============================================================================
# 文件操作工具
# =============================================================================


def safe_read_file(
    file_path: Union[str, Path], encoding: str = "utf-8", fallback_encoding: str = "gbk"
) -> str:
    """
    安全读取文件内容

    Args:
        file_path: 文件路径
        encoding: 主要编码
        fallback_encoding: 备用编码

    Returns:
        文件内容
    """
    file_path = Path(file_path)

    try:
        return file_path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        try:
            return file_path.read_text(encoding=fallback_encoding)
        except UnicodeDecodeError:
            return file_path.read_text(encoding="utf-8", errors="ignore")


def safe_write_file(
    file_path: Union[str, Path],
    content: str,
    encoding: str = "utf-8",
    backup: bool = True,
) -> None:
    """
    安全写入文件

    Args:
        file_path: 文件路径
        content: 文件内容
        encoding: 编码
        backup: 是否创建备份
    """
    file_path = Path(file_path)

    # 创建备份
    if backup and file_path.exists():
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        backup_path.write_bytes(file_path.read_bytes())

    # 确保目录存在
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # 写入文件
    file_path.write_text(content, encoding=encoding)


def get_file_hash(file_path: Union[str, Path], algorithm: str = "sha256") -> str:
    """
    计算文件哈希值

    Args:
        file_path: 文件路径
        algorithm: 哈希算法

    Returns:
        文件哈希值
    """
    hasher = hashlib.new(algorithm)

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def find_files(
    directory: Union[str, Path], pattern: str = "*", recursive: bool = True
) -> List[Path]:
    """
    查找文件

    Args:
        directory: 搜索目录
        pattern: 文件模式
        recursive: 是否递归搜索

    Returns:
        匹配的文件列表
    """
    directory = Path(directory)

    if recursive:
        return list(directory.rglob(pattern))
    else:
        return list(directory.glob(pattern))


# =============================================================================
# 数据结构工具
# =============================================================================


def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    深度合并字典

    Args:
        dict1: 第一个字典
        dict2: 第二个字典

    Returns:
        合并后的字典
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def flatten_dict(
    d: Dict[str, Any], parent_key: str = "", sep: str = "."
) -> Dict[str, Any]:
    """
    扁平化字典

    Args:
        d: 原始字典
        parent_key: 父键名
        sep: 分隔符

    Returns:
        扁平化后的字典
    """
    items = []
    for key, value in d.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)


def unflatten_dict(d: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
    """
    反扁平化字典

    Args:
        d: 扁平化字典
        sep: 分隔符

    Returns:
        嵌套字典
    """
    result = {}
    for key, value in d.items():
        keys = key.split(sep)
        current = result
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
    return result


def remove_none_values(d: Dict[str, Any], recursive: bool = True) -> Dict[str, Any]:
    """
    移除字典中的None值

    Args:
        d: 原始字典
        recursive: 是否递归处理

    Returns:
        清理后的字典
    """
    result = {}
    for key, value in d.items():
        if value is not None:
            if recursive and isinstance(value, dict):
                cleaned = remove_none_values(value, recursive)
                if cleaned:
                    result[key] = cleaned
            else:
                result[key] = value
    return result


def unique_list(lst: List[T], key: Optional[Callable[[T], Any]] = None) -> List[T]:
    """
    去重列表，保持顺序

    Args:
        lst: 原始列表
        key: 用于提取唯一键的函数

    Returns:
        去重后的列表
    """
    seen = set()
    result = []

    for item in lst:
        k = key(item) if key else item
        if k not in seen:
            seen.add(k)
            result.append(item)

    return result


# =============================================================================
# 数值处理工具
# =============================================================================


def safe_int(value: Any, default: int = 0) -> int:
    """安全转换为整数"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """安全转换为浮点数"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_decimal(value: Any, default: Optional[Decimal] = None) -> Decimal:
    """安全转换为Decimal"""
    try:
        return Decimal(str(value))
    except (ValueError, TypeError):
        return default or Decimal("0")


def format_number(number: Union[int, float], precision: int = 2) -> str:
    """格式化数字，添加千分位分隔符"""
    return f"{number:,.{precision}f}"


def format_bytes(bytes_count: int, unit: str = "auto") -> str:
    """
    格式化字节数

    Args:
        bytes_count: 字节数
        unit: 单位 ('auto', 'B', 'KB', 'MB', 'GB', 'TB')

    Returns:
        格式化后的字符串
    """
    if unit != "auto":
        units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
        if unit in units:
            return f"{bytes_count / units[unit]:.2f} {unit}"

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_count < 1024.0:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024.0

    return f"{bytes_count:.2f} PB"


# =============================================================================
# 装饰器工具
# =============================================================================


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[type, ...] = (Exception,),
) -> Callable[[F], F]:
    """
    重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间
        backoff: 退避倍数
        exceptions: 要捕获的异常类型

    Returns:
        装饰器函数
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        raise last_exception

            raise last_exception

        return wrapper

    return decorator


def timing_decorator(func: F) -> F:
    """计时装饰器"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            print(f"{func.__name__} 执行时间: {end_time - start_time:.4f} 秒")

    return wrapper


def deprecated(reason: str = ""):
    """废弃警告装饰器"""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} 已废弃. {reason}", DeprecationWarning, stacklevel=2
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


# =============================================================================
# 其他工具
# =============================================================================


def generate_uuid() -> str:
    """生成UUID字符串"""
    import uuid

    return str(uuid.uuid4())


def generate_random_string(
    length: int = 8,
    chars: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
) -> str:
    """生成随机字符串"""
    import random

    return "".join(random.choice(chars) for _ in range(length))


def is_valid_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_valid_url(url: str) -> bool:
    """验证URL格式"""
    pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    return bool(re.match(pattern, url))


def get_object_size(obj: Any) -> int:
    """获取对象的内存大小估算"""
    import sys

    return sys.getsizeof(obj)


def deep_copy(obj: Any) -> Any:
    """深度拷贝对象"""
    import copy

    return copy.deepcopy(obj)


def pretty_print_json(data: Any, indent: int = 2) -> str:
    """格式化打印JSON"""
    return json.dumps(data, indent=indent, ensure_ascii=False)


# =============================================================================
# 文件操作工具
# =============================================================================


def ensure_dir(directory: Union[str, Path]) -> Path:
    """确保目录存在，不存在则创建"""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json(file_path: Union[str, Path]) -> Dict[str, Any]:
    """从JSON文件加载数据"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(
    data: Dict[str, Any], file_path: Union[str, Path], indent: int = 2
) -> None:
    """保存数据到JSON文件"""
    ensure_dir(Path(file_path).parent)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def load_yaml(file_path: Union[str, Path]) -> Dict[str, Any]:
    """从YAML文件加载数据"""
    try:
        import yaml

        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        raise ImportError("需要安装PyYAML: pip install PyYAML")


def save_yaml(data: Dict[str, Any], file_path: Union[str, Path]) -> None:
    """保存数据到YAML文件"""
    try:
        import yaml

        ensure_dir(Path(file_path).parent)
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    except ImportError:
        raise ImportError("需要安装PyYAML: pip install PyYAML")


def load_pickle(file_path: Union[str, Path]) -> Any:
    """从Pickle文件加载数据"""
    import pickle

    with open(file_path, "rb") as f:
        return pickle.load(f)


def save_pickle(data: Any, file_path: Union[str, Path]) -> None:
    """保存数据到Pickle文件"""
    import pickle

    ensure_dir(Path(file_path).parent)
    with open(file_path, "wb") as f:
        pickle.dump(data, f)


def get_file_size(file_path: Union[str, Path], unit: str = "bytes") -> float:
    """获取文件大小"""
    size_bytes = os.path.getsize(file_path)

    if unit == "bytes":
        return size_bytes
    elif unit == "KB":
        return size_bytes / 1024
    elif unit == "MB":
        return size_bytes / (1024 * 1024)
    elif unit == "GB":
        return size_bytes / (1024 * 1024 * 1024)
    else:
        raise ValueError(f"不支持的单位: {unit}")


def list_files(
    directory: Union[str, Path], pattern: str = "*", recursive: bool = False
) -> List[Path]:
    """列出目录中符合模式的所有文件"""
    path = Path(directory)
    if recursive:
        return list(path.rglob(pattern))
    else:
        return list(path.glob(pattern))


# =============================================================================
# 数据处理工具
# =============================================================================


def calculate_md5(data: Union[str, bytes]) -> str:
    """计算MD5哈希值"""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.md5(data).hexdigest()


def calculate_sha256(data: Union[str, bytes]) -> str:
    """计算SHA256哈希值"""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def clean_text(text: str) -> str:
    """清理文本，移除多余空白和特殊字符"""
    # 替换多个空白为单个空格
    text = re.sub(r"\s+", " ", text)
    # 移除首尾空白
    return text.strip()


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """将列表分割为指定大小的块"""
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def get_date_range(
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    date_format: str = "%Y-%m-%d",
) -> List[str]:
    """获取日期范围内的所有日期"""
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, date_format)
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, date_format)

    date_list = []
    curr_date = start_date
    while curr_date <= end_date:
        date_list.append(curr_date.strftime(date_format))
        curr_date += timedelta(days=1)

    return date_list
