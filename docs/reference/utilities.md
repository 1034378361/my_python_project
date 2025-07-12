# 工具函数参考

my_python_project 提供了一套完整的工具函数库，包括时间处理、字符串操作、文件处理、数据验证等功能。

## 🕐 时间工具

### 基础时间函数

```python
from my_python_project.utils.common import (
    now_timestamp, now_timestamp_ms, format_datetime, from_timestamp
)

# 获取当前时间戳
timestamp = now_timestamp()  # 秒级时间戳
timestamp_ms = now_timestamp_ms()  # 毫秒级时间戳

# 格式化时间
formatted = format_datetime()  # 当前时间
formatted = format_datetime(dt, "%Y-%m-%d")  # 自定义格式

# 从时间戳转换
dt = from_timestamp(timestamp)
```

## 📝 字符串工具

### 文件名和文本处理

```python
from my_python_project.utils.common import (
    safe_filename, clean_whitespace, truncate_string
)

# 安全文件名
safe_name = safe_filename("用户上传/文件.txt")  # "用户上传_文件.txt"

# 清理文本
clean = clean_whitespace("  多个   空格  ")  # "多个 空格"

# 字符串截断
short = truncate_string("很长的文本内容", 10)  # "很长的文本内容..."
```

## 📁 文件操作

### 安全文件处理

```python
from my_python_project.utils.common import (
    ensure_dir, get_file_size, safe_read_file, safe_write_file
)

# 确保目录存在
path = ensure_dir("logs/2023/01")  # 创建多级目录

# 获取文件大小
size = get_file_size("file.txt")  # 字节数

# 安全文件读写
content = safe_read_file("file.txt")
safe_write_file("file.txt", "内容", backup=True)
```

## 📊 数据处理

### 字典和列表操作

```python
from my_python_project.utils.common import (
    deep_merge, chunk_list, flatten_dict
)

# 深度合并字典
dict1 = {"a": {"b": 1}, "c": 2}
dict2 = {"a": {"d": 3}, "e": 4}
merged = deep_merge(dict1, dict2)

# 分块列表
chunks = chunk_list([1, 2, 3, 4, 5], 2)  # [[1, 2], [3, 4], [5]]

# 扁平化字典
nested = {"user": {"name": "John", "age": 30}}
flat = flatten_dict(nested)  # {"user.name": "John", "user.age": 30}
```

## 🔒 验证工具

### 格式验证

```python
from my_python_project.utils.common import (
    is_valid_email, is_valid_url
)

# 验证邮箱和URL
valid_email = is_valid_email("user@example.com")  # True
valid_url = is_valid_url("https://example.com")  # True
```

## 🎲 生成工具

### 随机值生成

```python
from my_python_project.utils.common import (
    generate_uuid, generate_random_string
)

# 生成UUID和随机字符串
uuid = generate_uuid()  # "123e4567-e89b-12d3-a456-426614174000"
random_str = generate_random_string(8)  # "aBcD3fGh"
```

## ⚡ 装饰器

### 实用装饰器

```python
from my_python_project.utils.common import (
    retry_on_failure, timing_decorator
)

# 重试装饰器
@retry_on_failure(max_retries=3, delay=1.0)
def unstable_function():
    # 可能失败的操作
    pass

# 计时装饰器
@timing_decorator
def slow_function():
    # 会打印执行时间
    pass
```

## 📈 性能工具

详细的性能监控功能请参考 [性能监控指南](../advanced/performance_monitoring.md)。

## 🔧 配置管理

详细的配置管理功能请参考 [配置管理](../user-guide/config_management.md)。

## 📋 数据验证

详细的数据验证功能请参考 [数据验证](../advanced/validation.md)。

## 💾 缓存系统

详细的缓存功能请参考 [缓存系统](../advanced/caching.md)。

---

**提示**: 所有工具函数都有适当的错误处理和默认值，确保在异常情况下程序能够继续运行。