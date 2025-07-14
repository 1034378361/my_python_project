"""
配置管理系统

支持多种配置文件格式，环境变量覆盖，配置验证等功能。
"""

import json
import os
import warnings
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    warnings.warn("PyYAML not installed, YAML support disabled", stacklevel=2)

try:
    import tomllib
    HAS_TOML = True
except ImportError:
    try:
        import tomli as tomllib
        HAS_TOML = True
    except ImportError:
        HAS_TOML = False
        warnings.warn("tomllib/tomli not installed, TOML support disabled", stacklevel=2)

from .exceptions import ConfigError

T = TypeVar('T')


class ConfigManager:
    """
    统一配置管理器
    
    支持特性：
    - 多种格式：JSON、YAML、TOML、环境变量
    - 环境变量覆盖
    - 嵌套配置访问
    - 类型转换和验证
    - 配置热重载
    """
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None, 
                 env_prefix: Optional[str] = None, 
                 auto_reload: bool = False):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
            env_prefix: 环境变量前缀，如 "MYAPP_"
            auto_reload: 是否自动重载配置文件
        """
        self.config_path = Path(config_path) if config_path else None
        self.env_prefix = env_prefix or ""
        self.auto_reload = auto_reload
        self._config: Dict[str, Any] = {}
        self._file_mtime: Optional[float] = None
        
        if self.config_path and self.config_path.exists():
            self.load()
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path], 
                  env_prefix: Optional[str] = None, 
                  auto_reload: bool = False) -> 'ConfigManager':
        """从配置文件创建配置管理器"""
        return cls(config_path, env_prefix, auto_reload)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any], 
                  env_prefix: Optional[str] = None) -> 'ConfigManager':
        """从字典创建配置管理器"""
        manager = cls(env_prefix=env_prefix)
        manager._config = config_dict.copy()
        manager._apply_env_overrides()
        return manager
    
    def load(self) -> None:
        """加载配置文件"""
        if not self.config_path or not self.config_path.exists():
            raise ConfigError(f"配置文件不存在: {self.config_path}")
        
        # 检查文件修改时间
        current_mtime = self.config_path.stat().st_mtime
        if not self.auto_reload and self._file_mtime == current_mtime:
            return
        
        self._file_mtime = current_mtime
        
        # 根据文件扩展名选择解析器
        suffix = self.config_path.suffix.lower()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if suffix == '.json':
                    self._config = json.load(f)
                elif suffix in ['.yaml', '.yml']:
                    if not HAS_YAML:
                        raise ConfigError("YAML支持未安装，请安装PyYAML")
                    self._config = yaml.safe_load(f) or {}
                elif suffix == '.toml':
                    if not HAS_TOML:
                        raise ConfigError("TOML支持未安装，请安装tomllib或tomli")
                    content = f.read()
                    self._config = tomllib.loads(content)
                else:
                    raise ConfigError(f"不支持的配置文件格式: {suffix}")
        
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ConfigError(f"配置文件解析错误: {e}")
        except Exception as e:
            raise ConfigError(f"加载配置文件失败: {e}")
        
        # 应用环境变量覆盖
        self._apply_env_overrides()
    
    def _apply_env_overrides(self) -> None:
        """应用环境变量覆盖配置"""
        if not self.env_prefix:
            return
        
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                # 移除前缀并转换为配置键
                config_key = key[len(self.env_prefix):].lower()
                # 支持嵌套配置，用双下划线分隔
                keys = config_key.split('__')
                
                # 类型转换
                converted_value = self._convert_env_value(value)
                
                # 设置嵌套配置
                self._set_nested_value(self._config, keys, converted_value)
    
    def _convert_env_value(self, value: str) -> Any:
        """转换环境变量值类型"""
        # 布尔值
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # 数字
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # JSON格式
        if value.startswith(('{', '[', '"')):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        
        # 逗号分隔的列表
        if ',' in value:
            return [item.strip() for item in value.split(',')]
        
        return value
    
    def _set_nested_value(self, config: Dict, keys: list, value: Any) -> None:
        """设置嵌套配置值"""
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            elif not isinstance(config[key], dict):
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def get(self, key: str, default: Optional[T] = None, 
            type_hint: Optional[Type[T]] = None) -> T:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键如 "database.host"
            default: 默认值
            type_hint: 类型提示，用于类型转换
            
        Returns:
            配置值
        """
        if self.auto_reload and self.config_path:
            self.load()
        
        # 分割嵌套键
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
        except (KeyError, TypeError):
            if default is not None:
                return default
            raise ConfigError(f"配置键不存在: {key}")
        
        # 类型转换
        if type_hint and not isinstance(value, type_hint):
            try:
                if type_hint is bool:
                    if isinstance(value, str):
                        return value.lower() in ('true', 'yes', '1', 'on')
                    return bool(value)
                elif type_hint in (int, float, str):
                    return type_hint(value)
                elif type_hint is list and isinstance(value, str):
                    return value.split(',')
            except (ValueError, TypeError):
                if default is not None:
                    return default
                raise ConfigError(f"配置值类型转换失败: {key} -> {type_hint}")
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            value: 配置值
        """
        keys = key.split('.')
        self._set_nested_value(self._config, keys, value)
    
    def has(self, key: str) -> bool:
        """检查配置键是否存在"""
        try:
            self.get(key)
            return True
        except ConfigError:
            return False
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """更新配置"""
        self._deep_update(self._config, config_dict)
    
    def _deep_update(self, base: Dict, update: Dict) -> None:
        """深度更新字典"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """返回配置字典的副本"""
        return self._config.copy()
    
    def save(self, path: Optional[Union[str, Path]] = None) -> None:
        """保存配置到文件"""
        save_path = Path(path) if path else self.config_path
        if not save_path:
            raise ConfigError("未指定保存路径")
        
        suffix = save_path.suffix.lower()
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                if suffix == '.json':
                    json.dump(self._config, f, indent=2, ensure_ascii=False)
                elif suffix in ['.yaml', '.yml']:
                    if not HAS_YAML:
                        raise ConfigError("YAML支持未安装，请安装PyYAML")
                    yaml.dump(self._config, f, default_flow_style=False, 
                             allow_unicode=True, indent=2)
                else:
                    raise ConfigError(f"保存格式不支持: {suffix}")
        except Exception as e:
            raise ConfigError(f"保存配置文件失败: {e}")
    
    def reload(self) -> None:
        """重新加载配置文件"""
        self._file_mtime = None
        self.load()
    
    def watch_file(self, callback: Optional[Callable] = None) -> None:
        """
        监听配置文件变化（需要安装watchdog）
        
        Args:
            callback: 文件变化时的回调函数
        """
        if not self.config_path:
            raise ConfigError("无法监听：未指定配置文件路径")
        
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            
            class ConfigFileHandler(FileSystemEventHandler):
                def __init__(self, config_manager, callback_func):
                    self.config_manager = config_manager
                    self.callback_func = callback_func
                
                def on_modified(self, event):
                    if not event.is_directory and event.src_path == str(self.config_manager.config_path):
                        try:
                            self.config_manager.reload()
                            if self.callback_func:
                                self.callback_func(self.config_manager)
                        except Exception as e:
                            self.config_manager._handle_reload_error(e)
            
            observer = Observer()
            handler = ConfigFileHandler(self, callback)
            observer.schedule(handler, str(self.config_path.parent), recursive=False)
            observer.start()
            
            # 将observer存储以便后续清理
            self._file_observer = observer
            
        except ImportError:
            raise ConfigError("文件监听需要安装watchdog: pip install watchdog")
    
    def stop_watching(self) -> None:
        """停止监听配置文件"""
        if hasattr(self, '_file_observer'):
            self._file_observer.stop()
            self._file_observer.join()
            delattr(self, '_file_observer')
    
    def _handle_reload_error(self, error: Exception) -> None:
        """处理重载错误"""
        # 可以在这里添加错误恢复逻辑
        pass
    
    def validate_config(self, schema: Dict[str, Any]) -> List[str]:
        """
        验证配置
        
        Args:
            schema: 验证schema
            
        Returns:
            验证错误列表
        """
        errors = []
        
        def validate_nested(config_data, schema_data, path=""):
            for key, expected_type in schema_data.items():
                full_path = f"{path}.{key}" if path else key
                
                if key not in config_data:
                    errors.append(f"缺少必需的配置项: {full_path}")
                    continue
                
                value = config_data[key]
                
                if isinstance(expected_type, dict):
                    if not isinstance(value, dict):
                        errors.append(f"配置项 {full_path} 应该是字典类型")
                    else:
                        validate_nested(value, expected_type, full_path)
                elif isinstance(expected_type, type):
                    if not isinstance(value, expected_type):
                        errors.append(f"配置项 {full_path} 应该是 {expected_type.__name__} 类型")
        
        validate_nested(self._config, schema)
        return errors
    
    def merge_configs(self, *config_managers: 'ConfigManager') -> 'ConfigManager':
        """
        合并多个配置管理器
        
        Args:
            *config_managers: 要合并的配置管理器
            
        Returns:
            新的配置管理器
        """
        merged_config = self._config.copy()
        
        for manager in config_managers:
            merged_config = self._deep_update(merged_config, manager._config)
        
        return ConfigManager.from_dict(merged_config, self.env_prefix)
    
    def export_config(self, path: Union[str, Path], format: str = "json") -> None:
        """
        导出配置到文件
        
        Args:
            path: 导出路径
            format: 导出格式 ('json', 'yaml')
        """
        export_path = Path(path)
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                if format == "json":
                    json.dump(self._config, f, indent=2, ensure_ascii=False)
                elif format == "yaml":
                    if not HAS_YAML:
                        raise ConfigError("YAML导出需要安装PyYAML")
                    yaml.dump(self._config, f, default_flow_style=False, 
                             allow_unicode=True, indent=2)
                else:
                    raise ConfigError(f"不支持的导出格式: {format}")
        except Exception as e:
            raise ConfigError(f"导出配置失败: {e}")
    
    def create_backup(self, backup_dir: Optional[Union[str, Path]] = None) -> Path:
        """
        创建配置备份
        
        Args:
            backup_dir: 备份目录
            
        Returns:
            备份文件路径
        """
        if not self.config_path:
            raise ConfigError("无法备份：未指定配置文件路径")
        
        backup_dir = Path(backup_dir) if backup_dir else self.config_path.parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        import time
        timestamp = int(time.time())
        backup_name = f"{self.config_path.stem}_{timestamp}{self.config_path.suffix}"
        backup_path = backup_dir / backup_name
        
        # 复制配置文件
        import shutil
        shutil.copy2(self.config_path, backup_path)
        
        return backup_path
    
    def __getitem__(self, key: str) -> Any:
        """字典式访问"""
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """字典式设置"""
        self.set(key, value)
    
    def __contains__(self, key: str) -> bool:
        """支持 in 操作符"""
        return self.has(key)


# 全局配置实例
_global_config: Optional[ConfigManager] = None


def get_global_config() -> ConfigManager:
    """获取全局配置实例"""
    global _global_config
    if _global_config is None:
        raise ConfigError("全局配置未初始化，请先调用 init_global_config()")
    return _global_config


def init_global_config(config_path: Optional[Union[str, Path]] = None,
                      env_prefix: Optional[str] = None,
                      auto_reload: bool = False) -> ConfigManager:
    """初始化全局配置"""
    global _global_config
    _global_config = ConfigManager(config_path, env_prefix, auto_reload)
    return _global_config


def get_config(key: str, default: Optional[T] = None, 
               type_hint: Optional[Type[T]] = None) -> T:
    """快捷方式获取全局配置值"""
    return get_global_config().get(key, default, type_hint)


def set_config(key: str, value: Any) -> None:
    """快捷方式设置全局配置值"""
    get_global_config().set(key, value)