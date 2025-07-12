# 路径管理系统

My Python Project 提供了强大的项目路径管理功能，用于统一管理项目中的各种路径和文件组织。

## 🎯 功能概述

路径管理系统的主要特性：

- **会话目录管理**: 基于时间戳的唯一会话目录
- **标准目录结构**: 自动创建项目所需的标准目录
- **日志系统集成**: 与日志系统无缝集成，支持路径感知的日志记录
- **唯一文件名生成**: 自动生成带时间戳的唯一文件名
- **跨平台支持**: 兼容Windows、Linux、macOS等平台

## 🚀 基础使用

### 初始化路径管理器

```python
from my_python_project import ProjectPathManager, init_project_paths

# 方法1: 使用便捷函数初始化
path_manager = init_project_paths(
    base_dir="./workspace"
)

# 方法2: 直接创建管理器实例
path_manager = ProjectPathManager(
    base_dir="./workspace",
    session_name=None,  # 自动生成时间戳会话名
    auto_create_session=True
)
```

### 获取项目路径

```python
# 获取各种项目路径
print(f"基础目录: {path_manager.base_dir}")
print(f"会话目录: {path_manager.session_dir}")
print(f"数据目录: {path_manager.data_dir}")
print(f"日志目录: {path_manager.logs_dir}")
print(f"输出目录: {path_manager.output_dir}")
print(f"临时目录: {path_manager.temp_dir}")

# 会话相关信息
print(f"当前会话名: {path_manager.session_name}")
print(f"会话信息: {path_manager.get_session_info()}")
```

## 📁 目录结构管理

### 标准目录结构

路径管理器会自动创建以下标准目录结构：

```
workspace/
└── 20231201_143022/                   # 基于时间戳的会话目录
    ├── logs/                          # 日志文件
    ├── reports/                       # 报告文件
    ├── data/                          # 数据文件
    ├── downloads/                     # 下载文件
    ├── uploads/                       # 上传文件
    ├── temp/                          # 临时文件
    ├── output/                        # 输出文件
    ├── input/                         # 输入文件
    ├── config/                        # 配置文件
    ├── cache/                         # 缓存文件
    ├── backup/                        # 备份文件
    ├── models/                        # 模型文件
    ├── images/                        # 图片文件
    ├── documents/                     # 文档文件
    ├── scripts/                       # 脚本文件
    ├── results/                       # 结果文件
    └── path_config.json               # 路径配置文件
```

### 自定义目录

```python
# 创建自定义目录
models_dir = path_manager.create_custom_dir("models")
reports_dir = path_manager.create_custom_dir("reports")

# 使用自定义路径
model_path = path_manager.get_path("models")
report_path = path_manager.get_path("reports")

# 创建嵌套目录
training_dir = path_manager.create_custom_dir("models/training")
evaluation_dir = path_manager.create_custom_dir("models/evaluation")
```

## 📄 文件名管理

### 生成唯一文件名

```python
# 生成带时间戳的唯一文件名
log_file = path_manager.get_unique_filename("logs", "app.log")
# 结果: logs/app_20231201_143022_123.log

data_file = path_manager.get_unique_filename("data", "data.json")
# 结果: data/data_20231201_143022_456.json

# 使用便捷方法
log_path = path_manager.get_log_path("application")
# 结果: logs/application.log (如果不存在) 或 logs/application_20231201_143022_789.log
```

### 获取完整文件路径

```python
# 在不同目录下获取文件路径
log_path = path_manager.get_file_path("logs", "app.log")
data_path = path_manager.get_file_path("output", "results.json")
temp_path = path_manager.get_file_path("temp", "temp_data.txt")

# 使用便捷方法
model_path = path_manager.get_model_path("trained_model.pkl")
report_path = path_manager.get_report_path("analysis_report")
data_path = path_manager.get_data_path("dataset.csv")

print(f"日志文件: {log_path}")
print(f"模型文件: {model_path}")
print(f"报告文件: {report_path}")
```

## 🔗 与日志系统集成

### 路径感知的日志配置

```python
from my_python_project import get_project_logger, auto_setup_project_logging

# 自动配置基于路径的日志系统
auto_setup_project_logging(
    base_dir="./workspace",
    project_name="my_project"
)

# 获取配置好路径的日志器
logger = get_project_logger(__name__)

# 日志将自动写入到路径管理器指定的日志目录
logger.info("应用启动")
logger.error("发生错误", extra={"error_code": "E001"})
```

### 手动配置日志路径

```python
from my_python_project import get_logger_with_path

# 为特定模块配置日志路径
logger = get_logger_with_path(
    logger_name="data_processor",
    log_dir=path_manager.logs_dir,
    log_level="INFO"
)

# 使用配置好的日志器
logger.info("开始数据处理")
```

## 🛠️ 高级功能

### 路径信息导出

```python
# 导出路径信息到JSON
path_info = path_manager.to_dict()
print(path_info)

# 保存路径配置
import json
with open("path_config.json", "w") as f:
    json.dump(path_info, f, indent=2, default=str)
```

### 会话恢复

```python
# 从现有会话ID恢复路径管理器
existing_session = "20231201_143022_abc123"
restored_manager = ProjectPathManager.from_session_id(
    base_dir="./workspace",
    project_name="my_project",
    session_id=existing_session
)

print(f"恢复的会话: {restored_manager.session_id}")
```

### 清理和维护

```python
# 清理过期的会话目录（超过7天）
path_manager.cleanup_old_sessions(max_age_days=7)

# 清理临时文件
path_manager.cleanup_temp_files()

# 获取目录大小统计
stats = path_manager.get_directory_stats()
print(f"项目总大小: {stats['total_size_mb']:.2f} MB")
print(f"文件总数: {stats['total_files']}")
```

## 🔧 配置选项

### 路径管理器配置

```python
# 完整配置示例
path_manager = ProjectPathManager(
    base_dir="./workspace",
    project_name="my_project",
    create_session_dir=True,          # 是否创建会话目录
    session_dir_format="%Y%m%d_%H%M%S",  # 会话目录时间格式
    auto_create_subdirs=True,         # 自动创建子目录
    enable_cleanup=True,              # 启用自动清理
    max_session_age_days=30,          # 会话保留天数
    custom_dirs={                     # 自定义目录配置
        "models": "models",
        "cache": "cache",
        "backup": "backup"
    }
)
```

### 环境变量支持

```python
import os

# 通过环境变量配置路径
os.environ["PROJECT_BASE_DIR"] = "/opt/projects"
os.environ["PROJECT_NAME"] = "production_app"

# 自动从环境变量读取配置
path_manager = init_project_paths()
```

## 📊 实际应用示例

### 数据科学项目

```python
from my_python_project import init_project_paths, get_project_logger

# 初始化数据科学项目路径
path_manager = init_project_paths(
    base_dir="./ml_workspace",
    project_name="customer_analysis"
)

logger = get_project_logger(__name__)

# 数据处理
def process_data():
    # 输入数据路径
    raw_data_path = path_manager.get_file_path("raw_data.csv", "data")
    
    # 处理后数据保存路径
    processed_data_path = path_manager.get_file_path("processed_data.csv", "output")
    
    # 模型保存路径
    model_path = path_manager.get_file_path("model.pkl", "models")
    
    logger.info(f"处理数据: {raw_data_path} -> {processed_data_path}")
    
    # ... 数据处理逻辑 ...
    
    logger.info(f"模型保存到: {model_path}")

# 生成报告
def generate_report():
    report_path = path_manager.get_unique_filename("analysis_report.html", "output")
    logger.info(f"生成报告: {report_path}")
    
    # ... 报告生成逻辑 ...
```

### Web应用日志管理

```python
from fastapi import FastAPI
from my_python_project import auto_setup_project_logging, get_project_logger

# 初始化Web应用的路径和日志
auto_setup_project_logging(
    base_dir="/var/log/webapp",
    project_name="api_service"
)

app = FastAPI()
logger = get_project_logger("api")

@app.get("/process")
async def process_request():
    logger.info("API请求开始处理")
    
    # 业务逻辑...
    
    logger.info("API请求处理完成")
    return {"status": "success"}
```

## 🔍 故障排除

### 常见问题

**Q: 权限错误，无法创建目录**
```python
# 解决方案：检查并设置适当的权限
try:
    path_manager = init_project_paths(base_dir="./workspace")
except PermissionError:
    # 使用用户目录
    import os
    user_dir = os.path.expanduser("~/my_projects")
    path_manager = init_project_paths(base_dir=user_dir)
```

**Q: 磁盘空间不足**
```python
# 解决方案：定期清理和监控
path_manager.cleanup_old_sessions(max_age_days=7)
stats = path_manager.get_directory_stats()

if stats["total_size_mb"] > 1000:  # 大于1GB
    logger.warning(f"项目目录过大: {stats['total_size_mb']:.2f} MB")
```

**Q: 会话目录冲突**
```python
# 解决方案：使用更精确的时间戳或添加随机后缀
path_manager = ProjectPathManager(
    base_dir="./workspace",
    project_name="my_project",
    session_dir_format="%Y%m%d_%H%M%S_%f",  # 包含微秒
    add_random_suffix=True  # 添加随机后缀
)
```

---

路径管理系统为项目提供了统一、可靠的文件和目录管理方案，特别适合需要组织大量文件和日志的复杂项目。