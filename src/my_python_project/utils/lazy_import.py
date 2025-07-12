"""
延迟导入模块

提供延迟导入功能以优化启动性能。
"""

import sys
import importlib
from typing import Any, Optional, Dict, Callable
import warnings


class LazyImport:
    """延迟导入类"""
    
    def __init__(self, module_name: str, attribute: Optional[str] = None):
        """
        初始化延迟导入
        
        Args:
            module_name: 模块名称
            attribute: 属性名称
        """
        self.module_name = module_name
        self.attribute = attribute
        self._module = None
        self._value = None
        self._imported = False
    
    def __getattr__(self, name: str) -> Any:
        """获取属性时触发导入"""
        if not self._imported:
            self._import()
        
        if self.attribute:
            return getattr(self._value, name)
        else:
            return getattr(self._module, name)
    
    def __call__(self, *args, **kwargs) -> Any:
        """调用时触发导入"""
        if not self._imported:
            self._import()
        
        if self.attribute:
            return self._value(*args, **kwargs)
        else:
            return self._module(*args, **kwargs)
    
    def _import(self):
        """执行实际导入"""
        try:
            self._module = importlib.import_module(self.module_name)
            if self.attribute:
                self._value = getattr(self._module, self.attribute)
            self._imported = True
        except ImportError as e:
            raise ImportError(f"无法导入 {self.module_name}: {e}")
    
    def is_available(self) -> bool:
        """检查模块是否可用"""
        try:
            importlib.util.find_spec(self.module_name)
            return True
        except (ImportError, AttributeError, ValueError):
            return False


class LazyModule:
    """延迟模块加载器"""
    
    def __init__(self, module_name: str):
        """
        初始化延迟模块
        
        Args:
            module_name: 模块名称
        """
        self.__name__ = module_name
        self.__module = None
        self.__imported = False
    
    def __getattr__(self, name: str) -> Any:
        """获取属性时触发导入"""
        if not self.__imported:
            self.__import_module()
        return getattr(self.__module, name)
    
    def __import_module(self):
        """导入模块"""
        try:
            self.__module = importlib.import_module(self.__name__)
            self.__imported = True
        except ImportError as e:
            raise ImportError(f"无法导入模块 {self.__name__}: {e}")


# 全局延迟导入注册表
_lazy_imports: Dict[str, LazyImport] = {}


def lazy_import(module_name: str, attribute: Optional[str] = None) -> LazyImport:
    """
    创建延迟导入对象
    
    Args:
        module_name: 模块名称
        attribute: 属性名称
        
    Returns:
        延迟导入对象
    """
    key = f"{module_name}.{attribute}" if attribute else module_name
    
    if key not in _lazy_imports:
        _lazy_imports[key] = LazyImport(module_name, attribute)
    
    return _lazy_imports[key]


def conditional_import(module_name: str, fallback: Any = None, 
                      error_handler: Optional[Callable] = None) -> Any:
    """
    条件导入，如果导入失败返回fallback
    
    Args:
        module_name: 模块名称
        fallback: 导入失败时的备用值
        error_handler: 错误处理函数
        
    Returns:
        导入的模块或fallback值
    """
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        if error_handler:
            error_handler(e)
        return fallback


def import_optional(module_name: str, package: Optional[str] = None) -> Optional[Any]:
    """
    可选导入，失败时返回None并发出警告
    
    Args:
        module_name: 模块名称
        package: 包名
        
    Returns:
        导入的模块或None
    """
    try:
        return importlib.import_module(module_name, package)
    except ImportError:
        warnings.warn(f"可选模块 {module_name} 未安装", ImportWarning)
        return None


def preload_modules(module_names: list, background: bool = False) -> Dict[str, Any]:
    """
    预加载模块
    
    Args:
        module_names: 模块名称列表
        background: 是否在后台线程中加载
        
    Returns:
        加载的模块字典
    """
    modules = {}
    
    def load_module(name):
        try:
            modules[name] = importlib.import_module(name)
        except ImportError as e:
            warnings.warn(f"预加载模块 {name} 失败: {e}")
    
    if background:
        import threading
        threads = []
        for name in module_names:
            thread = threading.Thread(target=load_module, args=(name,))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join()
    else:
        for name in module_names:
            load_module(name)
    
    return modules


# 常用的延迟导入对象
pandas = lazy_import("pandas")
numpy = lazy_import("numpy")
requests = lazy_import("requests")
yaml_loader = lazy_import("yaml", "safe_load")
redis_client = lazy_import("redis", "Redis")


class OptionalDependency:
    """可选依赖管理器"""
    
    def __init__(self):
        self._available: Dict[str, bool] = {}
        self._modules: Dict[str, Any] = {}
    
    def register(self, name: str, module_name: str, 
                install_hint: Optional[str] = None) -> None:
        """
        注册可选依赖
        
        Args:
            name: 依赖名称
            module_name: 模块名称
            install_hint: 安装提示
        """
        try:
            module = importlib.import_module(module_name)
            self._available[name] = True
            self._modules[name] = module
        except ImportError:
            self._available[name] = False
            if install_hint:
                warnings.warn(
                    f"可选依赖 {name} 未安装。安装命令: {install_hint}",
                    ImportWarning
                )
    
    def is_available(self, name: str) -> bool:
        """检查依赖是否可用"""
        return self._available.get(name, False)
    
    def get_module(self, name: str) -> Optional[Any]:
        """获取模块"""
        return self._modules.get(name)
    
    def require(self, name: str) -> Any:
        """要求依赖必须可用"""
        if not self.is_available(name):
            raise ImportError(f"必需的依赖 {name} 不可用")
        return self._modules[name]


# 全局可选依赖管理器
optional_deps = OptionalDependency()

# 注册常用的可选依赖
optional_deps.register("yaml", "yaml", "pip install PyYAML")
optional_deps.register("redis", "redis", "pip install redis")
optional_deps.register("pandas", "pandas", "pip install pandas")
optional_deps.register("numpy", "numpy", "pip install numpy")
optional_deps.register("requests", "requests", "pip install requests")
optional_deps.register("watchdog", "watchdog", "pip install watchdog")
optional_deps.register("tomli", "tomli", "pip install tomli")