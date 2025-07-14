"""配置模块。

提供项目基础配置功能。日志系统已移至 utils.logging_utils 模块。
"""

import json
from pathlib import Path
from typing import Any

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def get_config_dir() -> Path:
    """获取配置目录路径。
    Returns:
        配置目录的Path对象
    """
    return Path(__file__).parent


def load_config(
    config_name: str = "app_config",
    config_format: str = "auto",
    config_path: Path | None = None,
) -> dict[str, Any]:
    """加载应用配置文件。
    Args:
        config_name: 配置文件名（不含扩展名）
        config_format: 配置格式 ('json', 'yaml', 'auto')
        config_path: 自定义配置文件路径
    Returns:
        配置字典
    Raises:
        FileNotFoundError: 配置文件不存在
        ValueError: 不支持的配置格式
    """
    config_dir = get_config_dir()

    if config_path is None:
        if config_format == "auto":
            # 优先使用YAML格式（如果可用）
            yaml_path = config_dir / f"{config_name}.yaml"
            json_path = config_dir / f"{config_name}.json"

            if YAML_AVAILABLE and yaml_path.exists():
                config_path = yaml_path
                config_format = "yaml"
            elif json_path.exists():
                config_path = json_path
                config_format = "json"
            else:
                # 默认使用JSON格式
                config_path = json_path
                config_format = "json"
        elif config_format == "yaml":
            config_path = config_dir / f"{config_name}.yaml"
        elif config_format == "json":
            config_path = config_dir / f"{config_name}.json"
        else:
            raise ValueError(f"不支持的配置格式: {config_format}")

    if not config_path.exists():
        # 返回空配置而不是抛出异常
        return {}

    with open(config_path, encoding="utf-8") as f:
        if config_format == "yaml":
            if not YAML_AVAILABLE:
                raise ImportError("需要安装PyYAML来使用YAML配置: pip install PyYAML")
            config = yaml.safe_load(f) or {}
        elif config_format == "json":
            config = json.load(f)
        else:
            raise ValueError(f"不支持的配置格式: {config_format}")

    return config


def get_config_path(
    config_name: str = "app_config", config_format: str = "json"
) -> Path:
    """获取配置文件路径。

    Args:
        config_name: 配置文件名（不含扩展名）
        config_format: 配置格式 ('json', 'yaml')

    Returns:
        配置文件路径
    """
    config_dir = get_config_dir()
    return config_dir / f"{config_name}.{config_format}"


# 提供向后兼容性的函数
def init_logging(*args, **kwargs):
    """向后兼容的日志初始化函数。

    注意: 此函数已废弃，请使用 utils.logging_utils.auto_setup_project_logging()
    """
    import warnings

    warnings.warn(
        "config.init_logging 已废弃，请使用 utils.logging_utils.auto_setup_project_logging()",
        DeprecationWarning,
        stacklevel=2,
    )

    try:
        from ..src.my_python_project.utils.logging_utils import (
            auto_setup_project_logging,
        )

        auto_setup_project_logging()
    except ImportError:
        # 基本日志配置作为后备
        import logging

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )


def get_logger(name: str = None):
    """向后兼容的日志获取函数。

    注意: 此函数已废弃，请使用 utils.logging_utils.get_project_logger()
    """
    import warnings

    warnings.warn(
        "config.get_logger 已废弃，请使用 utils.logging_utils.get_project_logger()",
        DeprecationWarning,
        stacklevel=2,
    )

    try:
        from ..src.my_python_project.utils.logging_utils import get_project_logger

        return get_project_logger(name)
    except ImportError:
        import logging

        return logging.getLogger(name or "my_python_project")
