# 模块集成指南

本指南展示了如何在项目中有效使用各个核心模块，以及它们之间的协作方式。

## 核心模块架构

```
my_python_project/
├── 配置管理 (config_manager.py)
├── 数据验证 (validators.py)
├── 缓存系统 (cache.py)
├── 异常处理 (exceptions.py)
├── 通用工具 (common.py)
├── 日志系统 (logging_utils.py)
└── 路径管理 (path_manager.py)
```

## 典型使用场景

### 1. Web API开发

```python
from my_python_project import (
    ConfigManager, validate_data, cache_result,
    StringValidator, NumberValidator, handle_exceptions
)

# 初始化配置和缓存
config = ConfigManager.from_file("config.json")
cache_manager = init_cache_manager()

# API参数验证
api_schema = {
    "username": StringValidator(min_length=3, max_length=20),
    "email": EmailValidator(),
    "age": NumberValidator(number_type=int, min_value=0, max_value=150)
}

@handle_exceptions(ValidationError, default_return={"error": "Invalid input"})
@cache_result(ttl=300)
def create_user_api(request_data):
    # 验证输入数据
    validated_data = validate_data(request_data, api_schema)
    
    # 使用配置
    db_url = config.get("database.url")
    
    # 处理业务逻辑
    return {"status": "success", "user": validated_data}
```

### 2. 数据处理管道

```python
from my_python_project import (
    log_performance, retry_on_failure, safe_read_file,
    ProjectPathManager, MemoryCache
)

# 初始化路径管理
paths = ProjectPathManager()
cache = MemoryCache(max_size=1000)

@log_performance
@retry_on_failure(max_retries=3)
def process_data_file(filename):
    """处理数据文件的完整流程"""
    
    # 路径管理
    input_path = paths.get_data_path() / filename
    output_path = paths.get_output_path() / f"processed_{filename}"
    
    # 检查缓存
    cache_key = f"processed_{filename}"
    if cache.exists(cache_key):
        return cache.get(cache_key)
    
    # 安全读取文件
    raw_data = safe_read_file(input_path)
    
    # 数据处理逻辑
    processed_data = perform_data_processing(raw_data)
    
    # 缓存结果
    cache.set(cache_key, processed_data, ttl=3600)
    
    return processed_data
```

### 3. 配置驱动的应用

```python
from my_python_project import (
    init_global_config, get_config, auto_setup_project_logging,
    ErrorHandler, BaseError
)

class Application:
    def __init__(self, config_file="config.yaml"):
        # 初始化配置
        init_global_config(config_file, env_prefix="MYAPP_")
        
        # 初始化日志
        auto_setup_project_logging()
        
        # 初始化错误处理
        self.error_handler = ErrorHandler()
        self.setup_error_callbacks()
    
    def setup_error_callbacks(self):
        """设置错误回调"""
        def on_config_error(error, context):
            # 配置错误的特殊处理
            self.reload_config()
        
        self.error_handler.register_callback("ConfigError", on_config_error)
    
    def start(self):
        """启动应用"""
        # 读取配置
        host = get_config("server.host", "localhost")
        port = get_config("server.port", 8000, type_hint=int)
        debug = get_config("debug", False, type_hint=bool)
        
        # 启动服务
        self.run_server(host, port, debug)
```

### 4. 数据验证和转换

```python
from my_python_project import (
    DictValidator, ListValidator, StringValidator, 
    DateValidator, validate_input, ValidationError
)

# 复杂数据结构验证
user_profile_schema = {
    "personal_info": DictValidator(
        schema={
            "name": StringValidator(min_length=2, max_length=50),
            "email": EmailValidator(),
            "birth_date": DateValidator(date_format="%Y-%m-%d")
        }
    ),
    "preferences": DictValidator(
        schema={
            "language": StringValidator(choices=["zh", "en", "es"]),
            "timezone": StringValidator(pattern=r"^[A-Za-z_/]+$")
        },
        required=False
    ),
    "tags": ListValidator(
        item_validator=StringValidator(min_length=1),
        max_length=10,
        unique=True
    )
}

@validate_input(
    user_data=DictValidator(schema=user_profile_schema)
)
def create_user_profile(user_data):
    """创建用户配置文件"""
    # 数据已经验证过，可以安全使用
    return {
        "id": generate_user_id(),
        "profile": user_data,
        "created_at": now_timestamp()
    }
```

## 模块间协作模式

### 1. 配置-缓存-日志协作

```python
# 基于配置的缓存和日志设置
def setup_application():
    # 1. 加载配置
    config = ConfigManager.from_file("app_config.yaml")
    
    # 2. 根据配置设置缓存
    cache_type = config.get("cache.type", "memory")
    if cache_type == "redis":
        redis_config = config.get("cache.redis")
        cache_backend = RedisCache(redis_client, **redis_config)
    else:
        cache_backend = MemoryCache(
            max_size=config.get("cache.max_size", 1000)
        )
    
    init_cache_manager(cache_backend)
    
    # 3. 配置日志级别
    log_level = config.get("logging.level", "INFO")
    setup_advanced_logger(level=log_level)
```

### 2. 验证-异常-缓存协作

```python
@handle_exceptions(ValidationError, log_errors=True)
@cache_result(ttl=600)
def get_validated_user_data(user_id, include_sensitive=False):
    """获取并验证用户数据"""
    
    # 数据验证
    user_id_validator = NumberValidator(number_type=int, min_value=1)
    validated_id = user_id_validator.validate(user_id, "user_id")
    
    # 获取数据
    raw_data = fetch_user_from_database(validated_id)
    
    # 数据清理和验证
    if not include_sensitive:
        # 移除敏感信息
        raw_data = remove_sensitive_fields(raw_data)
    
    # 验证数据完整性
    user_schema = get_user_validation_schema()
    return validate_data(raw_data, user_schema)
```

## 性能优化建议

### 1. 延迟导入

```python
# 避免在模块级别导入所有功能
def get_cache_manager():
    """延迟导入缓存管理器"""
    from my_python_project.utils.cache import get_cache_manager
    return get_cache_manager()

def validate_email(email):
    """延迟导入邮箱验证器"""
    from my_python_project.utils.validators import EmailValidator
    validator = EmailValidator()
    return validator.validate(email, "email")
```

### 2. 缓存策略

```python
# 分层缓存策略
def setup_multi_level_cache():
    """设置多层缓存"""
    from my_python_project import MemoryCache, FileCache, MultiLevelCache
    
    # 热数据：内存缓存
    hot_cache = MemoryCache(max_size=500)
    
    # 温数据：文件缓存
    warm_cache = FileCache("cache/warm/")
    
    # 组合缓存
    return MultiLevelCache([hot_cache, warm_cache])
```

### 3. 批量操作

```python
def batch_validate_users(user_list):
    """批量验证用户数据"""
    from my_python_project import validate_data
    
    user_schema = get_user_schema()
    results = []
    errors = []
    
    for i, user_data in enumerate(user_list):
        try:
            validated = validate_data(user_data, user_schema)
            results.append(validated)
        except ValidationError as e:
            errors.append({"index": i, "error": str(e)})
    
    return {"validated": results, "errors": errors}
```

## 错误处理最佳实践

### 1. 分层错误处理

```python
from my_python_project import (
    BaseError, ConfigError, ValidationError, 
    ErrorHandler, handle_exceptions
)

# 应用级错误处理
app_error_handler = ErrorHandler()

@handle_exceptions((ConfigError, ValidationError), 
                  callback=app_error_handler.handle_error)
def application_logic():
    """应用主逻辑"""
    pass

# 业务级错误处理
@handle_exceptions(BaseError, default_return=None, log_errors=True)
def business_operation():
    """业务操作"""
    pass
```

### 2. 错误恢复策略

```python
@retry_on_exception(max_retries=3, exceptions=(NetworkError,))
def resilient_api_call():
    """具有重试机制的API调用"""
    try:
        return make_api_request()
    except NetworkTimeoutError:
        # 网络超时，允许重试
        raise
    except AuthenticationError:
        # 认证错误，不应重试
        refresh_auth_token()
        raise
```

这种模块化设计确保了：
- **高内聚**：每个模块职责单一明确
- **低耦合**：模块间依赖关系清晰
- **易扩展**：可以轻松添加新功能模块
- **易测试**：每个模块都可以独立测试
- **易维护**：代码结构清晰，便于维护