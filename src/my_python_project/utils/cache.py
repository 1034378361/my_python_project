"""
缓存系统

提供内存缓存、文件缓存、Redis缓存等多种缓存策略和装饰器。
"""

import hashlib
import json
import pickle
import threading
import time
import warnings
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union

from .exceptions import CacheError, CacheKeyError, CacheSerializationError

T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])


# =============================================================================
# 缓存接口
# =============================================================================

class CacheBackend(ABC, Generic[T]):
    """缓存后端接口"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[T]:
        """获取缓存值"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: T, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """清空缓存"""
        pass
    
    @abstractmethod
    def keys(self) -> List[str]:
        """获取所有缓存键"""
        pass


# =============================================================================
# 内存缓存实现
# =============================================================================

class MemoryCache(CacheBackend[T]):
    """内存缓存实现"""

    _UNSET = object()  # 哨兵值，用于区分未设置和显式传入None

    def __init__(self, max_size: int = 1000, default_ttl: Optional[int] = None):
        """
        初始化内存缓存
        
        Args:
            max_size: 最大缓存数量
            default_ttl: 默认过期时间（秒）
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[T]:
        """获取缓存值"""
        with self._lock:
            if key not in self._cache:
                return None
            
            cache_item = self._cache[key]
            
            # 检查是否过期
            if self._is_expired(cache_item):
                self.delete(key)
                return None
            
            # 更新访问时间
            self._access_times[key] = time.time()
            return cache_item['value']
    
    def set(self, key: str, value: T, ttl=_UNSET) -> None:
        """设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值  
            ttl: 生存时间（秒）。默认使用default_ttl，None表示不过期
        """
        with self._lock:
            # 检查容量限制
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_lru()
            
            # 计算过期时间
            expires_at = None
            if ttl is self._UNSET:
                # 使用默认TTL
                if self.default_ttl is not None:
                    expires_at = time.time() + self.default_ttl
            elif ttl is not None:
                # 显式指定TTL
                expires_at = time.time() + ttl
            # 如果ttl is None，则expires_at保持None，表示不过期
            
            # 存储缓存项
            self._cache[key] = {
                'value': value,
                'created_at': time.time(),
                'expires_at': expires_at
            }
            self._access_times[key] = time.time()
    
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._access_times.pop(key, None)
                return True
            return False
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        with self._lock:
            if key not in self._cache:
                return False
            
            cache_item = self._cache[key]
            if self._is_expired(cache_item):
                self.delete(key)
                return False
            
            return True
    
    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
    
    def keys(self) -> List[str]:
        """获取所有缓存键"""
        with self._lock:
            # 清理过期键
            expired_keys = []
            for key, cache_item in self._cache.items():
                if self._is_expired(cache_item):
                    expired_keys.append(key)
            
            for key in expired_keys:
                self.delete(key)
            
            return list(self._cache.keys())
    
    def stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hit_ratio': self._calculate_hit_ratio(),
                'keys': list(self._cache.keys())
            }
    
    def _is_expired(self, cache_item: Dict[str, Any]) -> bool:
        """检查缓存项是否过期"""
        expires_at = cache_item.get('expires_at')
        return expires_at is not None and time.time() > expires_at
    
    def _evict_lru(self) -> None:
        """驱逐最近最少使用的项"""
        if not self._access_times:
            return
        
        # 找到最久未访问的键
        lru_key = min(self._access_times.keys(), 
                     key=lambda k: self._access_times[k])
        self.delete(lru_key)
    
    def _calculate_hit_ratio(self) -> float:
        """计算命中率（简化实现）"""
        # 这是一个简化的实现，实际应用中可能需要更复杂的统计
        return 0.0


# =============================================================================
# 文件缓存实现
# =============================================================================

class FileCache(CacheBackend[T]):
    """文件缓存实现"""
    
    def __init__(self, cache_dir: Union[str, Path], 
                 default_ttl: Optional[int] = None,
                 serializer: str = 'pickle'):
        """
        初始化文件缓存
        
        Args:
            cache_dir: 缓存目录
            default_ttl: 默认过期时间（秒）
            serializer: 序列化方式 ('pickle', 'json')
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        self.serializer = serializer
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[T]:
        """获取缓存值"""
        with self._lock:
            cache_file = self._get_cache_file(key)
            
            if not cache_file.exists():
                return None
            
            try:
                with open(cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                
                # 检查是否过期
                if self._is_expired(cache_data):
                    cache_file.unlink(missing_ok=True)
                    return None
                
                return self._deserialize(cache_data['value'])
            
            except Exception as e:
                cache_file.unlink(missing_ok=True)
                raise CacheSerializationError(f"文件缓存反序列化失败: {e}")
    
    def set(self, key: str, value: T, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        with self._lock:
            cache_file = self._get_cache_file(key)
            
            # 计算过期时间
            expires_at = None
            if ttl is not None:
                expires_at = time.time() + ttl
            elif self.default_ttl is not None:
                expires_at = time.time() + self.default_ttl
            
            # 序列化数据
            cache_data = {
                'value': self._serialize(value),
                'created_at': time.time(),
                'expires_at': expires_at
            }
            
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(cache_data, f)
            except Exception as e:
                raise CacheSerializationError(f"文件缓存序列化失败: {e}")
    
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        with self._lock:
            cache_file = self._get_cache_file(key)
            if cache_file.exists():
                cache_file.unlink()
                return True
            return False
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        return self.get(key) is not None
    
    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            for cache_file in self.cache_dir.glob('*.cache'):
                cache_file.unlink(missing_ok=True)
    
    def keys(self) -> List[str]:
        """获取所有缓存键"""
        with self._lock:
            keys = []
            for cache_file in self.cache_dir.glob('*.cache'):
                key = cache_file.stem
                if self.exists(key):
                    keys.append(key)
            return keys
    
    def _get_cache_file(self, key: str) -> Path:
        """获取缓存文件路径"""
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{safe_key}.cache"
    
    def _serialize(self, value: T) -> bytes:
        """序列化值"""
        if self.serializer == 'pickle':
            return pickle.dumps(value)
        elif self.serializer == 'json':
            return json.dumps(value).encode()
        else:
            raise CacheSerializationError(f"不支持的序列化方式: {self.serializer}")
    
    def _deserialize(self, data: bytes) -> T:
        """反序列化值"""
        if self.serializer == 'pickle':
            return pickle.loads(data)
        elif self.serializer == 'json':
            return json.loads(data.decode())
        else:
            raise CacheSerializationError(f"不支持的序列化方式: {self.serializer}")
    
    def _is_expired(self, cache_data: Dict[str, Any]) -> bool:
        """检查缓存项是否过期"""
        expires_at = cache_data.get('expires_at')
        return expires_at is not None and time.time() > expires_at


# =============================================================================
# Redis缓存实现
# =============================================================================

class RedisCache(CacheBackend[T]):
    """Redis缓存实现"""
    
    def __init__(self, redis_client, key_prefix: str = "", 
                 default_ttl: Optional[int] = None,
                 serializer: str = 'pickle'):
        """
        初始化Redis缓存
        
        Args:
            redis_client: Redis客户端
            key_prefix: 键前缀
            default_ttl: 默认过期时间（秒）
            serializer: 序列化方式 ('pickle', 'json')
        """
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl
        self.serializer = serializer
        
        # 检查Redis连接
        try:
            self.redis.ping()
        except Exception as e:
            raise CacheError(f"Redis连接失败: {e}")
    
    def get(self, key: str) -> Optional[T]:
        """获取缓存值"""
        try:
            full_key = self._get_full_key(key)
            data = self.redis.get(full_key)
            
            if data is None:
                return None
            
            return self._deserialize(data)
        
        except Exception as e:
            raise CacheError(f"Redis获取缓存失败: {e}")
    
    def set(self, key: str, value: T, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        try:
            full_key = self._get_full_key(key)
            serialized_value = self._serialize(value)
            
            # 设置过期时间
            expire_time = ttl or self.default_ttl
            
            if expire_time:
                self.redis.setex(full_key, expire_time, serialized_value)
            else:
                self.redis.set(full_key, serialized_value)
        
        except Exception as e:
            raise CacheError(f"Redis设置缓存失败: {e}")
    
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            full_key = self._get_full_key(key)
            return bool(self.redis.delete(full_key))
        
        except Exception as e:
            raise CacheError(f"Redis删除缓存失败: {e}")
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            full_key = self._get_full_key(key)
            return bool(self.redis.exists(full_key))
        
        except Exception as e:
            raise CacheError(f"Redis检查缓存失败: {e}")
    
    def clear(self) -> None:
        """清空缓存"""
        try:
            pattern = f"{self.key_prefix}*"
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
        
        except Exception as e:
            raise CacheError(f"Redis清空缓存失败: {e}")
    
    def keys(self) -> List[str]:
        """获取所有缓存键"""
        try:
            pattern = f"{self.key_prefix}*"
            redis_keys = self.redis.keys(pattern)
            return [key.decode().replace(self.key_prefix, "", 1) for key in redis_keys]
        
        except Exception as e:
            raise CacheError(f"Redis获取键列表失败: {e}")
    
    def _get_full_key(self, key: str) -> str:
        """获取完整的键名"""
        return f"{self.key_prefix}{key}"
    
    def _serialize(self, value: T) -> bytes:
        """序列化值"""
        if self.serializer == 'pickle':
            return pickle.dumps(value)
        elif self.serializer == 'json':
            return json.dumps(value).encode()
        else:
            raise CacheSerializationError(f"不支持的序列化方式: {self.serializer}")
    
    def _deserialize(self, data: bytes) -> T:
        """反序列化值"""
        if self.serializer == 'pickle':
            return pickle.loads(data)
        elif self.serializer == 'json':
            return json.loads(data.decode())
        else:
            raise CacheSerializationError(f"不支持的序列化方式: {self.serializer}")


# =============================================================================
# 多层缓存实现
# =============================================================================

class MultiLevelCache(CacheBackend[T]):
    """多层缓存实现"""
    
    def __init__(self, caches: List[CacheBackend[T]]):
        """
        初始化多层缓存
        
        Args:
            caches: 缓存后端列表，按优先级排序
        """
        self.caches = caches
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[T]:
        """获取缓存值"""
        with self._lock:
            for i, cache in enumerate(self.caches):
                try:
                    value = cache.get(key)
                    if value is not None:
                        # 将值回写到更高层级的缓存
                        for j in range(i):
                            try:
                                self.caches[j].set(key, value)
                            except Exception:
                                pass
                        return value
                except Exception:
                    continue
            return None
    
    def set(self, key: str, value: T, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        with self._lock:
            for cache in self.caches:
                try:
                    cache.set(key, value, ttl)
                except Exception:
                    continue
    
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        with self._lock:
            deleted = False
            for cache in self.caches:
                try:
                    if cache.delete(key):
                        deleted = True
                except Exception:
                    continue
            return deleted
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        return self.get(key) is not None
    
    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            for cache in self.caches:
                try:
                    cache.clear()
                except Exception:
                    continue
    
    def keys(self) -> List[str]:
        """获取所有缓存键"""
        all_keys = set()
        for cache in self.caches:
            try:
                all_keys.update(cache.keys())
            except Exception:
                continue
        return list(all_keys)


# =============================================================================
# 缓存管理器
# =============================================================================

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, default_backend: Optional[CacheBackend] = None):
        """
        初始化缓存管理器
        
        Args:
            default_backend: 默认缓存后端
        """
        self.default_backend = default_backend or MemoryCache()
        self.backends: Dict[str, CacheBackend] = {}
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
    
    def register_backend(self, name: str, backend: CacheBackend) -> None:
        """注册缓存后端"""
        self.backends[name] = backend
    
    def get_backend(self, name: Optional[str] = None) -> CacheBackend:
        """获取缓存后端"""
        if name is None:
            return self.default_backend
        
        if name not in self.backends:
            raise CacheKeyError(f"缓存后端 '{name}' 不存在")
        
        return self.backends[name]
    
    def get(self, key: str, backend: Optional[str] = None) -> Optional[Any]:
        """获取缓存值"""
        try:
            cache = self.get_backend(backend)
            value = cache.get(key)
            
            if value is not None:
                self._stats['hits'] += 1
            else:
                self._stats['misses'] += 1
            
            return value
        
        except Exception as e:
            self._stats['misses'] += 1
            raise CacheError(f"获取缓存失败: {e}")
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None,
            backend: Optional[str] = None) -> None:
        """设置缓存值"""
        try:
            cache = self.get_backend(backend)
            cache.set(key, value, ttl)
            self._stats['sets'] += 1
        
        except Exception as e:
            raise CacheError(f"设置缓存失败: {e}")
    
    def delete(self, key: str, backend: Optional[str] = None) -> bool:
        """删除缓存值"""
        try:
            cache = self.get_backend(backend)
            result = cache.delete(key)
            if result:
                self._stats['deletes'] += 1
            return result
        
        except Exception as e:
            raise CacheError(f"删除缓存失败: {e}")
    
    def clear(self, backend: Optional[str] = None) -> None:
        """清空缓存"""
        try:
            cache = self.get_backend(backend)
            cache.clear()
        
        except Exception as e:
            raise CacheError(f"清空缓存失败: {e}")
    
    def stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self._stats.copy()
    
    def reset_stats(self) -> None:
        """重置统计信息"""
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }


# =============================================================================
# 缓存装饰器
# =============================================================================

def cache_result(ttl: Optional[int] = None, 
                key_func: Optional[Callable] = None,
                backend: Optional[str] = None,
                cache_manager: Optional[CacheManager] = None):
    """
    缓存函数结果装饰器
    
    Args:
        ttl: 过期时间（秒）
        key_func: 自定义键生成函数
        backend: 缓存后端名称
        cache_manager: 缓存管理器
        
    Returns:
        装饰器函数
    """
    def decorator(func: F) -> F:
        manager = cache_manager or _get_global_cache_manager()
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = _generate_cache_key(func, args, kwargs)
            
            # 尝试从缓存获取
            try:
                cached_value = manager.get(cache_key, backend)
                if cached_value is not None:
                    return cached_value
            except Exception:
                pass
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            
            try:
                manager.set(cache_key, result, ttl, backend)
            except Exception:
                pass
            
            return result
        
        return wrapper
    return decorator


def timed_cache(ttl: int):
    """
    限时缓存装饰器
    
    Args:
        ttl: 过期时间（秒）
        
    Returns:
        装饰器函数
    """
    return cache_result(ttl=ttl)


def lru_cache(maxsize: int = 128):
    """
    LRU缓存装饰器
    
    Args:
        maxsize: 最大缓存数量
        
    Returns:
        装饰器函数
    """
    def decorator(func: F) -> F:
        cache = MemoryCache(max_size=maxsize)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = _generate_cache_key(func, args, kwargs)
            
            # 尝试从缓存获取
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            
            return result
        
        return wrapper
    return decorator


# =============================================================================
# 工具函数
# =============================================================================

def _generate_cache_key(func: Callable, args: tuple, kwargs: dict) -> str:
    """生成缓存键"""
    key_parts = [func.__module__, func.__name__]
    
    # 添加位置参数
    if args:
        key_parts.append(str(args))
    
    # 添加关键字参数
    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        key_parts.append(str(sorted_kwargs))
    
    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def _get_global_cache_manager() -> CacheManager:
    """获取全局缓存管理器"""
    global _global_cache_manager
    if _global_cache_manager is None:
        _global_cache_manager = CacheManager()
    return _global_cache_manager


# =============================================================================
# 全局缓存管理器
# =============================================================================

_global_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """获取全局缓存管理器"""
    return _get_global_cache_manager()


def init_cache_manager(default_backend: Optional[CacheBackend] = None) -> CacheManager:
    """初始化全局缓存管理器"""
    global _global_cache_manager
    _global_cache_manager = CacheManager(default_backend)
    return _global_cache_manager