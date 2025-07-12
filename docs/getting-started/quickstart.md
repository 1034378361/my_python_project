# 快速开始

本指南将帮助您在5分钟内开始使用 My Python Project。

## 🚀 第一个程序

### 1. 安装
```bash
pip install my_python_project
```

### 2. 简单示例
创建 `hello.py`：

```python
from my_python_project import (
    get_project_logger,
    ConfigManager,
    validate_data,
    StringValidator,
    NumberValidator
)

# 初始化日志
logger = get_project_logger(__name__)

def main():
    logger.info("程序启动")
    
    # 配置管理
    config = ConfigManager()
    config.set("app.name", "Hello World")
    
    # 数据验证
    data = {"name": "张三", "age": 25}
    
    # 使用validate_data函数进行数据验证
    schema = {
        "name": {"type": str, "required": True},
        "age": {"type": int, "required": True, "min": 0}
    }
    is_valid = validate_data(data, schema)
    
    if is_valid:
        logger.info(f"欢迎 {data['name']}！")
    else:
        logger.error("数据验证失败")

if __name__ == "__main__":
    main()
```

### 3. 运行
```bash
python hello.py
```

## 📋 常用功能

### 配置管理
```python
from my_python_project import ConfigManager

# 从文件加载配置
config = ConfigManager.from_file("config.yaml")

# 或者从字典创建
config = ConfigManager.from_dict({
    "database": {"host": "localhost", "port": 5432},
    "app": {"name": "MyApp", "debug": True}
})

# 获取配置值
host = config.get("database.host", "localhost")
port = config.get("database.port", 3306, type_hint=int)

# 设置配置值
config.set("app.version", "1.0.0")
```

### 数据验证
```python
from my_python_project import EmailValidator

validator = EmailValidator()
is_valid = validator.validate("user@example.com")
```

### 缓存使用
```python
from my_python_project import cache_result
import time

@cache_result(ttl=300)
def expensive_function(param):
    # 模拟耗时操作
    time.sleep(0.1)
    return f"处理结果: {param}"

# 使用示例
result = expensive_function("test_data")
print(result)  # 第一次调用会执行函数
result = expensive_function("test_data")  # 第二次调用使用缓存
```

## 🔗 下一步

- 阅读 [用户指南](../user-guide/config_management.md) 了解详细功能
- 查看 [实例代码](../examples/basic-usage.md) 获取更多示例
- 学习 [最佳实践](../best_practices.md) 编写高质量代码