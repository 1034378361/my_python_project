# 基础使用示例

本文档提供常见使用场景的代码示例。

## 📋 日志记录示例

```python
from my_python_project import get_project_logger

logger = get_project_logger(__name__)

def process_data(data):
    logger.info("开始处理数据", extra={"count": len(data)})
    
    try:
        result = []
        for item in data:
            processed = item.upper()
            result.append(processed)
            
        logger.info("数据处理完成", extra={"result_count": len(result)})
        return result
        
    except Exception as e:
        logger.error("数据处理失败", extra={"error": str(e)})
        raise
```

## ⚙️ 配置管理示例

```python
from my_python_project import ConfigManager

# 创建配置管理器
config = ConfigManager()

# 从文件加载配置
config = ConfigManager.from_file("app.yaml")

# 设置和获取配置
config.set("database.host", "localhost")
config.set("database.port", 5432)

db_config = {
    "host": config.get("database.host"),
    "port": config.get("database.port", 3306),  # 默认值
    "name": config.get("database.name")
}

# 批量设置
config.update({
    "app.debug": True,
    "app.workers": 4
})
```

## ✅ 数据验证示例

```python
from my_python_project import (
    StringValidator, NumberValidator, EmailValidator
)

# 字符串验证
name_validator = StringValidator(min_length=2, max_length=50)
valid_name = name_validator.validate("张三", "name")

# 数字验证
age_validator = NumberValidator(min_value=0, max_value=150)
valid_age = age_validator.validate(25, "age")

# 邮箱验证
email_validator = EmailValidator()
valid_email = email_validator.validate("user@example.com", "email")

# 组合验证
def validate_user(user_data):
    validators = {
        "name": name_validator,
        "age": age_validator,
        "email": email_validator
    }
    
    try:
        for field, validator in validators.items():
            if field in user_data:
                validator.validate(user_data[field], field)
        return True, "验证通过"
    except Exception as e:
        return False, f"验证失败: {str(e)}"
```

## 💾 缓存使用示例

```python
from my_python_project import MemoryCache, cache_result
import time

# 内存缓存
cache = MemoryCache(max_size=100)

def expensive_calculation(n):
    # 检查缓存
    cache_key = f"calc_{n}"
    if cache.exists(cache_key):
        return cache.get(cache_key)
    
    # 计算结果
    time.sleep(1)  # 模拟耗时操作
    result = sum(range(n))
    
    # 存储到缓存
    cache.set(cache_key, result, ttl=300)
    return result

# 使用装饰器缓存
@cache_result(ttl=600)
def fetch_user_data(user_id):
    # 模拟数据库查询
    time.sleep(0.5)
    return {"id": user_id, "name": f"用户{user_id}"}
```

## 🔧 工具函数示例

```python
from my_python_project import (
    format_datetime, safe_filename, deep_merge
)

# 时间格式化
current_time = format_datetime()  # "2023-01-01 12:00:00"
date_only = format_datetime(fmt="%Y-%m-%d")  # "2023-01-01"

# 安全文件名
safe_name = safe_filename("用户上传/文件.txt")  # "用户上传_文件.txt"

# 字典合并
config1 = {"app": {"name": "MyApp", "debug": True}}
config2 = {"app": {"version": "1.0"}, "database": {"host": "localhost"}}
merged = deep_merge(config1, config2)
# 结果: {"app": {"name": "MyApp", "debug": True, "version": "1.0"}, "database": {"host": "localhost"}}
```

## 🚦 错误处理示例

```python
from my_python_project import handle_exceptions, BaseError

class DataProcessingError(BaseError):
    """数据处理异常"""
    pass

@handle_exceptions(DataProcessingError, default_return=[])
def process_file(filename):
    """处理文件数据"""
    with open(filename, 'r') as f:
        data = f.read()
    
    if not data:
        raise DataProcessingError("文件为空")
    
    # 处理数据
    lines = data.strip().split('\n')
    return [line.upper() for line in lines]

# 使用示例
result = process_file("data.txt")  # 如果出错会返回默认值 []
```