# 配置管理系统

配置管理系统提供了统一的配置文件处理、环境变量覆盖、类型转换等功能，支持多种配置文件格式。

## 功能特性

- **多格式支持**: JSON、YAML、TOML格式
- **环境变量覆盖**: 支持环境变量覆盖配置文件设置
- **嵌套配置**: 支持点号分隔的嵌套配置访问
- **类型转换**: 自动类型转换和验证
- **热重载**: 可选的配置文件自动重载
- **全局配置**: 全局配置管理器单例

## 基本用法

### 从文件加载配置

```python
from my_python_project.utils.config_manager import ConfigManager

# 从JSON文件加载
config = ConfigManager.from_file("config.json")

# 从YAML文件加载（需要安装PyYAML）
config = ConfigManager.from_file("config.yaml")

# 从TOML文件加载（需要安装tomli/tomllib）
config = ConfigManager.from_file("config.toml")
```

### 从字典创建配置

```python
config_data = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "mydb"
    },
    "debug": True
}

config = ConfigManager.from_dict(config_data)
```

### 访问配置

```python
# 简单访问
host = config.get("database.host")  # "localhost"
port = config.get("database.port")  # 5432

# 带默认值
timeout = config.get("database.timeout", 30)  # 如果不存在则返回30

# 类型转换
port = config.get("database.port", type_hint=int)  # 确保返回整数
debug = config.get("debug", type_hint=bool)  # 确保返回布尔值
```

### 设置配置

```python
# 设置简单值
config.set("app.name", "My App")

# 设置嵌套值
config.set("database.credentials.username", "admin")

# 更新配置
config.update({"api": {"key": "secret-key"}})
```

## 环境变量覆盖

配置管理器支持通过环境变量覆盖配置文件设置：

```python
# 使用环境变量前缀
config = ConfigManager.from_file("config.json", env_prefix="MYAPP_")

# 环境变量 MYAPP_DATABASE__HOST 会覆盖 database.host
# 环境变量 MYAPP_DEBUG 会覆盖 debug
```

### 环境变量命名规则

- 使用指定的前缀（如 `MYAPP_`）
- 用双下划线 `__` 分隔嵌套配置
- 自动类型转换：
  - `"true"`, `"yes"`, `"1"`, `"on"` → `True`
  - `"false"`, `"no"`, `"0"`, `"off"` → `False`
  - 纯数字 → 整数或浮点数
  - 逗号分隔 → 列表
  - JSON格式 → 对应的Python对象

## 全局配置管理

```python
from my_python_project.utils.config_manager import (
    init_global_config, get_config, set_config
)

# 初始化全局配置
init_global_config("config.json", env_prefix="MYAPP_")

# 在应用任何地方访问配置
database_host = get_config("database.host")
debug_mode = get_config("debug", default=False)

# 设置全局配置
set_config("runtime.startup_time", "2023-01-01 10:00:00")
```

## 配置文件格式

### JSON格式

```json
{
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "mydb",
        "credentials": {
            "username": "admin",
            "password": "secret"
        }
    },
    "debug": true,
    "features": ["feature1", "feature2"]
}
```

### YAML格式

```yaml
database:
  host: localhost
  port: 5432
  name: mydb
  credentials:
    username: admin
    password: secret

debug: true
features:
  - feature1
  - feature2
```

### TOML格式

```toml
debug = true
features = ["feature1", "feature2"]

[database]
host = "localhost"
port = 5432
name = "mydb"

[database.credentials]
username = "admin"
password = "secret"
```

## 高级功能

### 自动重载

```python
# 启用自动重载
config = ConfigManager.from_file("config.json", auto_reload=True)

# 文件修改后会自动重新加载
value = config.get("some.key")  # 总是获取最新值
```

### 配置验证

```python
# 检查配置是否存在
if config.has("database.host"):
    host = config.get("database.host")

# 使用 in 操作符检查配置键
if "database.host" in config:
    host = config.get("database.host")
```

### 配置更新

```python
# 更新配置
new_config = {
    "database": {
        "port": 5433,  # 更新现有值
        "timeout": 30  # 添加新值
    }
}

config.update(new_config)
```

### 保存配置

```python
# 保存到原文件
config.save()

# 保存到新文件
config.save("new_config.json")
```

## 错误处理

```python
from my_python_project import ConfigError

try:
    config = ConfigManager.from_file("nonexistent.json")
except ConfigError as e:
    print(f"配置加载失败: {e}")

try:
    value = config.get("nonexistent.key")
except ConfigError as e:
    print(f"配置键不存在: {e}")
```

## 最佳实践

1. **使用环境变量**: 为不同环境使用不同的配置值
2. **配置分层**: 将配置按功能模块分组
3. **提供默认值**: 为可选配置提供合理的默认值
4. **配置验证**: 在应用启动时验证关键配置
5. **敏感信息**: 使用环境变量存储敏感信息如密码、密钥

## 配置文件示例

```json
{
  "app": {
    "name": "My Application",
    "version": "1.0.0",
    "debug": false
  },
  "database": {
    "host": "localhost",
    "port": 5432,
    "name": "myapp",
    "pool_size": 10,
    "timeout": 30
  },
  "redis": {
    "host": "localhost",
    "port": 6379,
    "db": 0
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "app.log"
  },
  "api": {
    "host": "0.0.0.0",
    "port": 8000,
    "workers": 4
  }
}
```

对应的环境变量：
```bash
export MYAPP_APP__DEBUG=true
export MYAPP_DATABASE__HOST=prod-db-server
export MYAPP_DATABASE__PASSWORD=secure-password
export MYAPP_API__PORT=8080
```