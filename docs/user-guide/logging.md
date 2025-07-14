# 日志系统使用指南

My Python Project 提供了一个功能强大且灵活的日志系统，支持多种格式和高级功能。

## 快速开始

### 使用配置文件（推荐）

项目提供了预配置的日志配置文件，支持JSON和YAML格式：

```python
from my_python_project import init_project_logging

# 自动加载配置文件（优先使用config/logging_config.json或.yaml）
logger = init_project_logging()

# 指定配置文件
logger = init_project_logging("config/production_logging.yaml")

# 配置文件加载失败时使用自定义默认配置
logger = init_project_logging(
    fallback_to_default=True,
    log_level="DEBUG",
    log_format="json"
)
```

### 手动加载配置文件

```python
from my_python_project import load_logging_config_from_file

# 加载JSON配置
success = load_logging_config_from_file("config/logging_config.json")

# 加载YAML配置
success = load_logging_config_from_file("config/logging_config.yaml")

# 自动检测格式
success = load_logging_config_from_file("config/custom_logging.yaml")
```

### 一键设置（高级）

```python
from my_python_project import auto_setup_project_logging

# 一行代码设置项目日志和路径管理
logger, path_manager = auto_setup_project_logging("/var/data/myproject")

# 开始使用
logger.info("项目启动")

# 获取各种路径
model_path = path_manager.get_model_path("trained_model.pkl")
data_path = path_manager.get_data_path("dataset.csv")
report_path = path_manager.get_report_path("实验报告")

logger.info(f"模型保存路径: {model_path}")
```

### 基本使用

```python
from my_python_project import get_project_logger

# 获取日志记录器（使用默认路径）
logger = get_project_logger(__name__)

# 记录不同级别的日志
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

### 自定义日志路径

```python
from my_python_project import get_project_logger, get_logger_with_path
from pathlib import Path

# 方法1：通过参数指定自定义路径
custom_path = "/var/log/myapp/module.log"
logger = get_project_logger(__name__, log_file=custom_path)

# 方法2：使用便捷函数
logger = get_logger_with_path("/var/log/myapp/module.log", __name__)

# 方法3：使用相对路径
logger = get_project_logger(__name__, log_file="logs/modules/my_module.log")

# 方法4：动态路径
today = datetime.now().strftime("%Y%m%d")
daily_log = f"logs/daily/{today}.log"
logger = get_project_logger(__name__, log_file=daily_log)
```

### 使用装饰器

```python
from my_python_project import log_performance, log_function_call

@log_performance()
@log_function_call(log_args=True, log_result=True)
def my_function(arg1, arg2="default"):
    # 函数会自动记录调用参数、返回值和执行时间
    return f"processed {arg1} and {arg2}"
```

### 使用上下文管理器

```python
from my_python_project import log_context

logger = get_project_logger(__name__)

with log_context(logger, "数据处理"):
    # 这个代码块的执行会被记录，包括执行时间
    process_data()
```

## 配置选项

项目使用 cookiecutter 变量来配置日志系统：

- `logging_level`: 日志级别 (DEBUG, INFO, WARNING, ERROR)
- `enable_file_logging`: 是否启用文件日志 (yes/no)
- `logging_format`: 日志格式 (standard, json, custom)
- `enable_log_rotation`: 是否启用日志轮转 (yes/no)

## 日志格式

### 标准格式
```
2023-12-07 10:30:45 - my_python_project.module - INFO - 这是一条日志消息
```

### JSON格式
```json
{
  "timestamp": "2023-12-07T10:30:45.123456",
  "level": "INFO",
  "logger": "my_python_project.module",
  "message": "这是一条日志消息",
  "module": "module",
  "function": "function_name",
  "line": 42,
  "extra": {
    "user_id": "123",
    "request_id": "req-456"
  }
}
```

### 自定义格式
```
[2023-12-07 10:30:45] my_python_project.module.function_name:42 - INFO - 这是一条日志消息
```

## 项目路径管理

### 自动时间戳目录

每次运行都会自动创建基于时间戳的会话目录，确保不同运行之间的文件隔离：

```python
from my_python_project import ProjectPathManager

# 创建路径管理器，自动生成时间戳目录
pm = ProjectPathManager("/var/data/myproject")

# 目录结构示例：
# /var/data/myproject/
# ├── 20231207_143052/          # 当前会话目录
# │   ├── logs/                 # 日志文件
# │   ├── reports/              # 报告文件
# │   ├── data/                 # 数据文件
# │   ├── models/               # 模型文件
# │   ├── output/               # 输出文件
# │   └── temp/                 # 临时文件
# ├── 20231207_142130/          # 上次会话目录
# └── 20231207_141025/          # 更早会话目录

print(f"当前会话: {pm.session_name}")  # 20231207_143052
print(f"会话目录: {pm.session_dir}")   # /var/data/myproject/20231207_143052
```

### 标准项目目录

```python
# 获取标准目录路径
logs_dir = pm.get_path("logs")              # 日志目录
reports_dir = pm.get_path("reports")        # 报告目录
data_dir = pm.get_path("data")              # 数据目录
models_dir = pm.get_path("models")          # 模型目录

# 或使用便捷属性
logs_dir = pm.logs_dir
reports_dir = pm.reports_dir
data_dir = pm.data_dir
models_dir = pm.models_dir

# 获取文件路径
log_file = pm.get_log_path("application.log")
model_file = pm.get_model_path("trained_model.pkl")
report_file = pm.get_report_path("实验报告")  # 自动添加.docx扩展名
```

### 自定义目录和嵌套路径

```python
# 创建自定义目录
experiments_dir = pm.create_custom_dir("experiments")
nested_dir = pm.create_custom_dir("experiments/exp001/results")

# 获取嵌套路径
processed_data_dir = pm.get_path("data/processed")
training_logs_dir = pm.get_path("logs/training")

# 获取自定义文件路径
config_file = pm.get_custom_path("experiments", "config.json")
result_file = pm.get_custom_path("experiments/exp001/results", "metrics.csv")
```

### 唯一文件名生成

```python
# 避免文件覆盖，自动生成唯一名称
report1 = pm.get_unique_filename("reports", "summary.docx")  # summary.docx
report2 = pm.get_unique_filename("reports", "summary.docx")  # summary_20231207_143052_123.docx

# 对于模型文件
model1 = pm.get_unique_filename("models", "model.pkl")      # model.pkl
model2 = pm.get_unique_filename("models", "model.pkl")      # model_20231207_143052_456.pkl
```

## 高级功能

### 与日志系统深度集成

```python
from my_python_project import ProjectPathManager
from my_python_project.utils.logging_utils import (
    setup_logging_with_path_manager,
    configure_project_logging_with_paths
)

# 创建路径管理器
pm = ProjectPathManager("/var/data/myproject")

# 方法1：单个日志记录器
logger = setup_logging_with_path_manager(pm, __name__)

# 方法2：配置多个日志记录器
loggers = configure_project_logging_with_paths(
    pm,
    log_configs={
        "main": {"filename": "main.log"},
        "database": {"filename": "db.log", "log_format": "json"},
        "api": {"filename": "api.log", "log_level": "DEBUG"}
    }
)

main_logger = loggers["main"]
db_logger = loggers["database"]
api_logger = loggers["api"]
```

### 会话管理

```python
# 列出所有会话
sessions = pm.list_sessions()
print(f"历史会话: {sessions}")

# 清理旧会话，只保留最新的5个
pm.cleanup_old_sessions(keep_count=5)

# 获取会话信息
info = pm.get_session_info()
print(f"当前会话信息: {info}")

# 从配置文件恢复会话
config_path = pm.session_dir / "path_config.json"
restored_pm = ProjectPathManager.from_config(config_path)
```

### 配置整个项目的日志系统

```python
from my_python_project import configure_project_logging

# 自定义日志目录
loggers = configure_project_logging(
    log_dir="/var/log/myapp",
    log_level="DEBUG",
    enable_file_logging=True
)

# 使用不同的日志记录器
main_logger = loggers["main"]
error_logger = loggers["error"]
performance_logger = loggers["performance"]

# 为不同模块指定不同的日志文件
loggers = configure_project_logging(
    custom_log_files={
        "database": "/var/log/myapp/db.log",
        "api": "/var/log/myapp/api.log",
        "worker": "/var/log/myapp/worker.log"
    }
)

db_logger = loggers["database"]
api_logger = loggers["api"]
worker_logger = loggers["worker"]
```

### 完全自定义的日志记录器

```python
from my_python_project import get_configured_logger

# 完全自定义配置
logger = get_configured_logger(
    name="my_module",
    log_file="/var/log/myapp/custom.log",
    log_level="DEBUG",
    log_format="json",
    enable_rotation=True,
    max_bytes=5*1024*1024,  # 5MB
    backup_count=3
)
```

### 环境变量支持

```bash
# 设置环境变量
export MY_PYTHON_PROJECT_LOG_DIR="/var/log/myapp"
export MY_PYTHON_PROJECT_LOG_FILE="/var/log/myapp/custom.log"
```

```python
from my_python_project import get_log_path_from_env

# 从环境变量获取日志路径
log_path = get_log_path_from_env()
logger = get_logger_with_path(log_path)
```

### 性能监控

```python
from my_python_project.utils.logging_utils import log_performance

@log_performance(include_args=True)
def slow_function():
    # 函数执行时间会被自动记录
    time.sleep(1)
    return "done"
```

### 结构化日志

```python
logger.info("用户操作", extra={
    "user_id": "123",
    "action": "login",
    "ip_address": "192.168.1.1",
    "timestamp": datetime.now().isoformat()
})
```

### 性能过滤

只记录执行时间超过阈值的日志：

```python
from my_python_project.utils.logging_utils import setup_advanced_logger

logger = setup_advanced_logger(
    name="performance.logger",
    performance_threshold=0.5  # 只记录执行时间超过0.5秒的操作
)
```

## 配置文件

### 使用配置文件初始化

```python
from my_python_project.config import init_logging

# 自动选择配置格式
init_logging()

# 指定配置格式
init_logging(config_format="json")
init_logging(config_format="yaml")

# 使用自定义配置文件
init_logging(config_path=Path("custom_logging.yaml"))
```

### 配置文件位置

- `config/logging_config.json` - JSON格式配置
- `config/logging_config.yaml` - YAML格式配置

### 配置文件格式

#### JSON配置示例
项目中的 `config/logging_config.json` 提供了完整的配置示例：

```json
{
  "version": 1,
  "disable_existing_loggers": false,
  "formatters": {
    "standard": {
      "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
      "datefmt": "%Y-%m-%d %H:%M:%S"
    },
    "detailed": {
      "format": "[%(asctime)s] %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s",
      "datefmt": "%Y-%m-%d %H:%M:%S"
    },
    "json": {
      "()": "my_python_project.utils.logging_utils.JsonFormatter",
      "include_extra": true
    }
  },
  "handlers": {
    "console": {
      "class": "logging.StreamHandler",
      "level": "INFO",
      "formatter": "standard",
      "stream": "ext://sys.stdout"
    },
    "file_handler": {
      "class": "logging.FileHandler",
      "level": "INFO",
      "formatter": "detailed",
      "filename": "logs/my_python_project.log",
      "encoding": "utf-8"
    }
  },
  "loggers": {
    "my_python_project": {
      "level": "INFO",
      "handlers": ["console", "file_handler"],
      "propagate": false
    }
  }
}
```

#### YAML配置示例
`config/logging_config.yaml` 提供了相同的配置，但使用更易读的YAML格式：

```yaml
version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    datefmt: "%Y-%m-%d %H:%M:%S"
  
  detailed:
    format: "[%(asctime)s] %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s"
    datefmt: "%Y-%m-%d %H:%M:%S"

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
    stream: ext://sys.stdout

loggers:
  my_python_project:
    level: INFO
    handlers: [console, file_handler]
    propagate: false
```

#### 配置文件特性

- **动态配置**: 配置文件支持cookiecutter模板变量，会在项目生成时自动替换
- **多格式支持**: 自动检测JSON和YAML格式
- **完整功能**: 支持所有Python logging配置选项
- **性能过滤器**: 包含自定义的性能监控过滤器
- **文件轮转**: 支持日志文件自动轮转

## 日志文件

默认情况下，日志文件会保存在项目根目录的 `logs/` 文件夹中：

- `logs/my_python_project.log` - 主日志文件
- `logs/my_python_project_errors.log` - 错误日志文件
- `logs/my_python_project_performance.log` - 性能日志文件

## 环境变量

- `MY_PYTHON_PROJECT_AUTO_INIT_LOGGING`: 设置为 "false" 可禁用自动日志初始化
- `DEBUG`: 设置为 "true" 或 "1" 可启用调试模式

## 最佳实践

1. **模块级日志记录器**：每个模块使用独立的日志记录器
   ```python
   logger = get_project_logger(__name__)
   ```

2. **结构化日志**：使用 extra 字段添加上下文信息
   ```python
   logger.info("操作完成", extra={"operation": "data_sync", "duration": 1.5})
   ```

3. **异常记录**：使用 `exc_info=True` 记录完整的异常信息
   ```python
   try:
       risky_operation()
   except Exception as e:
       logger.error("操作失败", exc_info=True)
   ```

4. **性能监控**：对重要函数使用性能装饰器
   ```python
   @log_performance(logger)
   def important_function():
       pass
   ```

5. **避免敏感信息**：不要在日志中记录密码、密钥等敏感信息
   ```python
   # 错误示例
   logger.info(f"用户登录: {username}, 密码: {password}")
   
   # 正确示例
   logger.info("用户登录", extra={"username": username, "success": True})
   ```

## 故障排除

### 日志文件未创建
确保：
1. `enable_file_logging` 设置为 "yes"
2. 项目有写入权限
3. 日志目录存在

### 配置加载失败
检查：
1. 配置文件路径是否正确
2. 配置文件格式是否有效
3. 如果使用YAML，确保已安装 PyYAML

### 性能影响
如果日志影响性能：
1. 调整日志级别为 WARNING 或 ERROR
2. 禁用文件日志
3. 使用异步日志处理

## 测试

运行日志系统测试：

```bash
# 测试日志功能
python -m pytest tests/test_logging.py -v

# 测试特定功能
python -m pytest tests/test_logging.py::TestJsonFormatter -v
```

## 示例项目

### 完整的使用示例

```python
from my_python_project import (
    get_project_logger, 
    log_performance, 
    log_context,
    configure_project_logging,
    get_configured_logger
)
from datetime import datetime
from pathlib import Path

# 场景1：使用默认配置
logger = get_project_logger(__name__)
logger.info("使用默认日志配置")

# 场景2：自定义日志路径
custom_logger = get_project_logger(__name__, log_file="/var/log/myapp/custom.log")
custom_logger.info("使用自定义路径")

# 场景3：动态日志路径（按日期）
today = datetime.now().strftime("%Y%m%d")
daily_logger = get_project_logger(__name__, log_file=f"logs/daily/{today}.log")
daily_logger.info("使用日期路径")

# 场景4：配置整个项目的日志系统
loggers = configure_project_logging(
    log_dir="/var/log/myapp",
    custom_log_files={
        "database": "/var/log/myapp/db.log",
        "api": "/var/log/myapp/api.log"
    }
)

# 场景5：模块化日志系统
class DatabaseManager:
    def __init__(self):
        self.logger = get_configured_logger(
            "database",
            log_file="/var/log/myapp/database.log",
            log_format="json"
        )
    
    @log_performance()
    def connect(self):
        self.logger.info("连接数据库")
        with log_context(self.logger, "数据库连接"):
            # 模拟连接操作
            pass

class APIServer:
    def __init__(self):
        self.logger = get_configured_logger(
            "api",
            log_file="/var/log/myapp/api.log"
        )
    
    def handle_request(self, request_id):
        self.logger.info("处理请求", extra={"request_id": request_id})

@log_performance(logger)
def process_data(data):
    logger.info("开始处理数据", extra={"data_size": len(data)})
    
    with log_context(logger, "数据验证"):
        validate_data(data)
    
    with log_context(logger, "数据转换"):
        transformed_data = transform_data(data)
    
    logger.info("数据处理完成", extra={"output_size": len(transformed_data)})
    return transformed_data

if __name__ == "__main__":
    # 初始化日志系统
    from my_python_project.config import init_logging
    init_logging()
    
    # 使用不同的日志系统
    db = DatabaseManager()
    db.connect()
    
    api = APIServer()
    api.handle_request("req-123")
    
    result = process_data(["item1", "item2", "item3"])
    logger.info("程序执行完成")
```

### Docker 环境中的日志配置

```dockerfile
# Dockerfile
ENV MY_PYTHON_PROJECT_LOG_DIR=/app/logs
ENV MY_PYTHON_PROJECT_LOG_LEVEL=INFO

# 创建日志目录
RUN mkdir -p /app/logs
VOLUME ["/app/logs"]
```

```python
# 在应用中使用环境变量配置
from my_python_project import get_log_path_from_env, get_logger_with_path
import os

# 从环境变量获取配置
log_path = get_log_path_from_env()
log_level = os.getenv("MY_PYTHON_PROJECT_LOG_LEVEL", "INFO")

logger = get_logger_with_path(log_path)
logger.info("应用启动", extra={"environment": "docker"})
```