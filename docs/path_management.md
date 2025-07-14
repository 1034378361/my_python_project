# 项目路径管理指南

My Python Project 提供了强大的项目路径管理功能，每次运行自动创建时间戳目录，支持标准项目结构和自定义路径。

## 核心特性

- ✅ **自动时间戳目录** - 每次运行创建独立的会话目录
- ✅ **标准项目结构** - 预定义常用目录（logs, reports, data等）
- ✅ **自定义路径支持** - 灵活创建和管理自定义目录
- ✅ **唯一文件名生成** - 避免文件覆盖
- ✅ **会话管理** - 管理历史运行记录
- ✅ **配置持久化** - 保存和恢复路径配置
- ✅ **日志系统集成** - 与日志系统深度整合

## 快速开始

### 一键设置（最简单）

```python
from my_python_project import auto_setup_project_logging

# 一行代码设置所有内容
logger, pm = auto_setup_project_logging("/var/data/myproject")

# 立即可用
logger.info("项目启动")
model_path = pm.get_model_path("trained_model.pkl")
data_path = pm.get_data_path("dataset.csv")
```

### 手动设置

```python
from my_python_project import ProjectPathManager

# 创建路径管理器
pm = ProjectPathManager("/var/data/myproject")

# 项目目录结构自动创建：
# /var/data/myproject/
# └── 20231207_143052/          # 时间戳会话目录
#     ├── logs/                 # 日志文件
#     ├── reports/              # 报告文件
#     ├── data/                 # 数据文件
#     ├── downloads/            # 下载文件
#     ├── uploads/              # 上传文件
#     ├── temp/                 # 临时文件
#     ├── output/               # 输出文件
#     ├── input/                # 输入文件
#     ├── config/               # 配置文件
#     ├── cache/                # 缓存文件
#     ├── backup/               # 备份文件
#     ├── models/               # 模型文件
#     ├── images/               # 图片文件
#     ├── documents/            # 文档文件
#     ├── scripts/              # 脚本文件
#     ├── results/              # 结果文件
#     └── path_config.json      # 路径配置文件
```

## 基本使用

### 获取标准目录路径

```python
# 方法1：使用get_path()
logs_dir = pm.get_path("logs")
data_dir = pm.get_path("data")
models_dir = pm.get_path("models")
reports_dir = pm.get_path("reports")

# 方法2：使用便捷属性
logs_dir = pm.logs_dir
data_dir = pm.data_dir
models_dir = pm.models_dir
reports_dir = pm.reports_dir
temp_dir = pm.temp_dir
output_dir = pm.output_dir

# 获取会话信息
print(f"当前会话: {pm.session_name}")     # 20231207_143052
print(f"会话目录: {pm.session_dir}")      # /var/data/myproject/20231207_143052
print(f"基础目录: {pm.base_dir}")         # /var/data/myproject
```

### 获取文件路径

```python
# 专用方法（自动添加扩展名和唯一性处理）
log_file = pm.get_log_path("application.log")              # logs/application.log
report_file = pm.get_report_path("实验报告")                 # reports/实验报告.docx
model_file = pm.get_model_path("trained_model.pkl")        # models/trained_model.pkl
data_file = pm.get_data_path("dataset.csv")               # data/dataset.csv
output_file = pm.get_output_path("results.json")          # output/results.json
temp_file = pm.get_temp_path("processing.tmp")            # temp/processing.tmp

# 通用方法
config_file = pm.get_file_path("config", "settings.yaml")  # config/settings.yaml
cache_file = pm.get_file_path("cache", "cache.db")        # cache/cache.db
```

## 高级功能

### 嵌套路径

```python
# 自动创建多级目录
processed_data = pm.get_path("data/processed")            # data/processed/
clean_data = pm.get_path("data/processed/clean")          # data/processed/clean/
raw_images = pm.get_path("images/raw")                    # images/raw/
training_logs = pm.get_path("logs/training")              # logs/training/

# 获取嵌套文件路径
clean_dataset = pm.get_file_path("data/processed/clean", "final_dataset.csv")
model_config = pm.get_file_path("models/config", "hyperparameters.json")
```

### 自定义目录

```python
# 创建自定义目录
experiments_dir = pm.create_custom_dir("experiments")
exp001_dir = pm.create_custom_dir("experiments/exp001")
results_dir = pm.create_custom_dir("experiments/exp001/results")

# 获取自定义路径
exp_path = pm.get_custom_path("experiments")                           # 目录路径
config_path = pm.get_custom_path("experiments", "config.yaml")         # 文件路径
result_path = pm.get_custom_path("experiments/exp001/results", "metrics.json")

# 检查自定义目录
print(f"自定义目录: {pm.custom_dirs}")
```

### 唯一文件名生成

避免文件覆盖，自动生成带时间戳的唯一文件名：

```python
# 第一次调用 - 使用原始名称
report1 = pm.get_unique_filename("reports", "summary.docx")
# 返回: reports/summary.docx

# 第二次调用 - 自动添加时间戳
report2 = pm.get_unique_filename("reports", "summary.docx")  
# 返回: reports/summary_20231207_143052_123.docx

# 对模型文件也同样适用
model1 = pm.get_unique_filename("models", "model.pkl")      # models/model.pkl
model2 = pm.get_unique_filename("models", "model.pkl")      # models/model_20231207_143052_456.pkl

# 实际使用示例
import pickle

# 保存模型到唯一路径
model_path = pm.get_unique_filename("models", "trained_model.pkl")
with open(model_path, 'wb') as f:
    pickle.dump(my_model, f)

print(f"模型已保存到: {model_path}")
```

### 图片路径管理

```python
# 按类型组织图片
screenshot_path = pm.get_image_path("screenshots", "screen1.png")
# 返回: images/screenshots/screen1.png

plot_path = pm.get_image_path("plots", "training_curve.png")
# 返回: images/plots/training_curve.png

# 嵌套图片目录
result_viz = pm.get_image_path("results/visualization", "confusion_matrix.png")
# 返回: images/results/visualization/confusion_matrix.png

# 目录会自动创建
figure_dir = pm.get_path("images/figures")
assert figure_dir.exists()  # True
```

## 会话管理

### 查看历史会话

```python
# 列出所有会话
sessions = pm.list_sessions()
print(f"历史会话: {sessions}")
# 输出: ['20231207_143052', '20231207_142130', '20231206_091234', ...]

# 获取特定会话目录
old_session_dir = pm.get_session_dir("20231207_142130")
print(f"上次运行目录: {old_session_dir}")

# 获取当前会话信息
info = pm.get_session_info()
print(f"会话信息: {info}")
```

### 清理旧会话

```python
# 手动清理，保留最新10个会话
pm.cleanup_old_sessions(keep_count=10)

# 自动清理（在初始化时）
pm_auto_clean = ProjectPathManager(
    "/var/data/myproject",
    auto_create_session=True
)
pm_auto_clean.cleanup_old_sessions(keep_count=5)
```

### 配置持久化

```python
# 配置自动保存到 session_dir/path_config.json
# 包含所有路径信息、自定义目录等

# 手动保存配置
pm._save_config()

# 从配置文件恢复
config_path = pm.session_dir / "path_config.json"
restored_pm = ProjectPathManager.from_config(config_path)

# 验证恢复正确
assert restored_pm.session_name == pm.session_name
assert restored_pm.custom_dirs == pm.custom_dirs
```

## 与日志系统集成

### 方法1：自动集成

```python
from my_python_project import auto_setup_project_logging

# 一步到位
logger, pm = auto_setup_project_logging("/var/data/myproject")

# 日志自动保存到会话目录的logs/子目录
logger.info("这条日志会保存到当前会话的logs目录")

# 同时获得完整的路径管理
model_path = pm.get_model_path("my_model.pkl")
logger.info(f"模型将保存到: {model_path}")
```

### 方法2：手动集成

```python
from my_python_project.utils.logging_utils import (
    setup_logging_with_path_manager,
    configure_project_logging_with_paths
)

# 创建路径管理器
pm = ProjectPathManager("/var/data/myproject")

# 单个日志记录器
logger = setup_logging_with_path_manager(pm, __name__)

# 多个专用日志记录器
loggers = configure_project_logging_with_paths(
    pm,
    log_configs={
        "main": {"filename": "main.log"},
        "database": {"filename": "database.log", "log_format": "json"},
        "training": {"filename": "training.log", "log_level": "DEBUG"},
        "inference": {"filename": "inference.log"}
    }
)

main_logger = loggers["main"]
db_logger = loggers["database"]
train_logger = loggers["training"]
infer_logger = loggers["inference"]

# 所有日志都保存在当前会话的logs/目录下
```

## 环境变量支持

```bash
# 设置环境变量
export MY_PYTHON_PROJECT_BASE_DIR="/var/data/myproject"
export MY_PYTHON_PROJECT_LOG_DIR="/var/log/myproject"  # 备用选项
```

```python
# 自动从环境变量获取路径
logger, pm = auto_setup_project_logging()  # 不需要指定路径

# 或手动使用环境变量
import os
base_dir = os.getenv("MY_PYTHON_PROJECT_BASE_DIR", ".")
pm = ProjectPathManager(base_dir)
```

## 实际应用示例

### 机器学习项目

```python
from my_python_project import auto_setup_project_logging
import pandas as pd
import pickle
from pathlib import Path

# 初始化项目
logger, pm = auto_setup_project_logging("/var/ml_projects/sentiment_analysis")

logger.info("开始情感分析项目")

# 数据处理
raw_data_path = pm.get_file_path("input", "raw_tweets.csv")
processed_data_path = pm.get_data_path("processed_tweets.csv")

logger.info(f"加载原始数据: {raw_data_path}")
df = pd.read_csv(raw_data_path)

# 数据处理...
df_processed = preprocess_data(df)
df_processed.to_csv(processed_data_path, index=False)
logger.info(f"处理后数据保存到: {processed_data_path}")

# 模型训练
model = train_model(df_processed)
model_path = pm.get_model_path("sentiment_model.pkl")
with open(model_path, 'wb') as f:
    pickle.dump(model, f)
logger.info(f"模型保存到: {model_path}")

# 生成报告
report_path = pm.get_report_path("实验报告")
generate_report(model, report_path)
logger.info(f"报告生成: {report_path}")

# 保存结果
results_dir = pm.create_custom_dir("results/final")
metrics_path = pm.get_custom_path("results/final", "metrics.json")
save_metrics(model_metrics, metrics_path)

logger.info("项目完成！")
```

### 数据分析项目

```python
from my_python_project import ProjectPathManager
import matplotlib.pyplot as plt

# 创建路径管理器
pm = ProjectPathManager("/var/analysis_projects/sales_analysis")

# 数据分析流程
input_data = pm.get_file_path("input", "sales_data.csv")
processed_data = pm.get_data_path("cleaned_sales.csv")

# 创建分析结果目录
pm.create_custom_dir("analysis")
pm.create_custom_dir("analysis/charts")
pm.create_custom_dir("analysis/tables")

# 生成图表
chart_path = pm.get_custom_path("analysis/charts", "monthly_sales.png")
plt.figure(figsize=(12, 6))
# ... 绘图代码 ...
plt.savefig(chart_path)

# 保存分析表格
table_path = pm.get_custom_path("analysis/tables", "summary_stats.csv")
summary_df.to_csv(table_path)

# 生成最终报告
report_path = pm.get_report_path("销售分析报告")
create_analysis_report(report_path)
```

### Web 应用项目

```python
from my_python_project import auto_setup_project_logging
from my_python_project.utils.logging_utils import configure_project_logging_with_paths

# 设置Web应用的日志和路径
logger, pm = auto_setup_project_logging("/var/web_apps/blog_site")

# 配置不同组件的日志
loggers = configure_project_logging_with_paths(
    pm,
    log_configs={
        "access": {"filename": "access.log"},
        "error": {"filename": "error.log", "log_level": "ERROR"},
        "database": {"filename": "database.log", "log_format": "json"},
        "auth": {"filename": "auth.log"}
    }
)

access_logger = loggers["access"]
error_logger = loggers["error"]
db_logger = loggers["database"]
auth_logger = loggers["auth"]

# 创建Web应用特定目录
pm.create_custom_dir("static")
pm.create_custom_dir("templates")
pm.create_custom_dir("uploads/images")
pm.create_custom_dir("uploads/documents")

# 文件上传处理
def handle_upload(file, file_type):
    if file_type == "image":
        upload_path = pm.get_custom_path("uploads/images", file.filename)
    else:
        upload_path = pm.get_custom_path("uploads/documents", file.filename)
    
    # 确保唯一文件名
    unique_path = pm.get_unique_filename(upload_path.parent, upload_path.name)
    
    file.save(unique_path)
    access_logger.info(f"文件上传: {unique_path}")
    return unique_path
```

## 最佳实践

### 1. 项目初始化

```python
# 在项目入口点进行初始化
def main():
    # 设置项目路径和日志
    logger, pm = auto_setup_project_logging("/var/projects/myproject")
    
    # 记录项目启动
    logger.info("=" * 50)
    logger.info(f"项目启动: My Python Project")
    logger.info(f"会话ID: {pm.session_name}")
    logger.info(f"工作目录: {pm.session_dir}")
    logger.info("=" * 50)
    
    # 返回给其他模块使用
    return logger, pm

if __name__ == "__main__":
    logger, pm = main()
```

### 2. 模块化使用

```python
# config.py
from my_python_project import get_project_paths

def get_data_path(filename):
    """获取数据文件路径"""
    pm = get_project_paths()
    if pm:
        return pm.get_data_path(filename)
    return filename

def get_model_path(filename):
    """获取模型文件路径"""
    pm = get_project_paths()
    if pm:
        return pm.get_model_path(filename)
    return filename

# 在其他模块中使用
# data_processor.py
from .config import get_data_path
import pandas as pd

def load_dataset(name):
    path = get_data_path(f"{name}.csv")
    return pd.read_csv(path)
```

### 3. 错误处理

```python
from my_python_project import ProjectPathManager
import logging

def safe_create_path_manager(base_dir, logger=None):
    """安全创建路径管理器"""
    if logger is None:
        logger = logging.getLogger(__name__)
    
    try:
        pm = ProjectPathManager(base_dir)
        logger.info(f"路径管理器创建成功: {pm.session_dir}")
        return pm
    except PermissionError:
        logger.error(f"权限不足，无法创建目录: {base_dir}")
        # 尝试使用临时目录
        import tempfile
        temp_dir = tempfile.mkdtemp()
        logger.warning(f"使用临时目录: {temp_dir}")
        return ProjectPathManager(temp_dir)
    except Exception as e:
        logger.error(f"创建路径管理器失败: {e}")
        raise
```

### 4. 配置管理

```python
# settings.py
import os
from pathlib import Path

# 项目配置
PROJECT_BASE_DIR = os.getenv(
    "MY_PYTHON_PROJECT_BASE_DIR",
    str(Path.home() / "my_python_project_projects")
)

# 会话清理设置
KEEP_SESSIONS = int(os.getenv("MY_PYTHON_PROJECT_KEEP_SESSIONS", "10"))

# 自动清理设置
AUTO_CLEANUP = os.getenv("MY_PYTHON_PROJECT_AUTO_CLEANUP", "true").lower() == "true"

def init_project():
    """初始化项目设置"""
    from my_python_project import auto_setup_project_logging
    
    logger, pm = auto_setup_project_logging(
        base_dir=PROJECT_BASE_DIR,
        cleanup_old=AUTO_CLEANUP
    )
    
    if AUTO_CLEANUP:
        pm.cleanup_old_sessions(keep_count=KEEP_SESSIONS)
    
    return logger, pm
```

## 故障排除

### 权限问题

```python
# 检查目录权限
import os
from pathlib import Path

def check_permissions(base_dir):
    base_path = Path(base_dir)
    
    # 检查父目录是否可写
    if not base_path.parent.exists():
        print(f"父目录不存在: {base_path.parent}")
        return False
    
    if not os.access(base_path.parent, os.W_OK):
        print(f"父目录不可写: {base_path.parent}")
        return False
    
    return True

# 使用检查
if check_permissions("/var/projects/myproject"):
    pm = ProjectPathManager("/var/projects/myproject")
else:
    # 使用用户主目录
    pm = ProjectPathManager("~/myproject_data")
```

### 磁盘空间问题

```python
import shutil

def check_disk_space(path, min_free_gb=1):
    """检查磁盘空间"""
    total, used, free = shutil.disk_usage(path)
    free_gb = free // (1024**3)
    
    if free_gb < min_free_gb:
        print(f"磁盘空间不足: {free_gb}GB 剩余，需要至少 {min_free_gb}GB")
        return False
    
    return True

# 在创建路径管理器前检查
if check_disk_space("/var/projects", min_free_gb=2):
    pm = ProjectPathManager("/var/projects/myproject")
```

### 调试模式

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 创建路径管理器时会输出详细信息
pm = ProjectPathManager("/var/projects/myproject", session_name="debug_session")

# 检查创建的目录
print(f"会话目录: {pm.session_dir}")
print(f"标准目录: {pm.standard_dirs}")
print(f"自定义目录: {pm.custom_dirs}")

# 验证所有目录存在
for dir_name in pm.standard_dirs:
    dir_path = pm.get_path(dir_name)
    print(f"{dir_name}: {dir_path} ({'存在' if dir_path.exists() else '不存在'})")
```