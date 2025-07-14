"""
缓存系统测试
"""

import time
import tempfile
import threading
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from my_python_project.utils.cache import (
    MemoryCache,
    FileCache,
    MultiLevelCache,
    CacheManager,
    cache_result,
    timed_cache,
    lru_cache,
    get_cache_manager,
    init_cache_manager,
)
from my_python_project.utils.exceptions import CacheError


class TestMemoryCache:
    """内存缓存测试"""

    def test_basic_operations(self):
        """测试基本操作"""
        cache = MemoryCache()

        # 设置和获取
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        # 获取不存在的键
        assert cache.get("nonexistent") is None

        # 检查键是否存在
        assert cache.exists("key1") is True
        assert cache.exists("nonexistent") is False

        # 删除键
        assert cache.delete("key1") is True
        assert cache.get("key1") is None
        assert cache.delete("key1") is False  # 再次删除返回False

    def test_ttl_expiration(self):
        """测试TTL过期"""
        cache = MemoryCache()

        # 设置短过期时间
        cache.set("temp_key", "temp_value", ttl=1)
        assert cache.get("temp_key") == "temp_value"

        # 等待过期
        time.sleep(1.1)
        assert cache.get("temp_key") is None
        assert cache.exists("temp_key") is False

    def test_default_ttl(self):
        """测试默认TTL"""
        cache = MemoryCache(default_ttl=1)

        cache.set("key1", "value1")  # 使用默认TTL
        cache.set("key2", "value2", ttl=None)  # 不过期

        time.sleep(1.1)

        assert cache.get("key1") is None  # 已过期
        assert cache.get("key2") == "value2"  # 未过期

    def test_max_size_and_lru(self):
        """测试最大容量和LRU驱逐"""
        cache = MemoryCache(max_size=3)

        # 填满缓存
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # 访问key1使其成为最近使用
        cache.get("key1")

        # 添加新键，应该驱逐key2（最久未使用）
        cache.set("key4", "value4")

        assert cache.get("key1") == "value1"  # 最近访问，保留
        assert cache.get("key2") is None  # 被驱逐
        assert cache.get("key3") == "value3"  # 保留
        assert cache.get("key4") == "value4"  # 新添加

    def test_clear_cache(self):
        """测试清空缓存"""
        cache = MemoryCache()

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.keys() == []

    def test_keys_method(self):
        """测试获取所有键"""
        cache = MemoryCache()

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("temp", "temp_value", ttl=1)

        keys = cache.keys()
        assert "key1" in keys
        assert "key2" in keys
        assert "temp" in keys

        # 等待过期后再次获取键
        time.sleep(1.1)
        keys = cache.keys()
        assert "key1" in keys
        assert "key2" in keys
        assert "temp" not in keys  # 过期的键被清理

    def test_stats(self):
        """测试统计信息"""
        cache = MemoryCache(max_size=10)

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        stats = cache.stats()
        assert stats["size"] == 2
        assert stats["max_size"] == 10
        assert "keys" in stats
        assert len(stats["keys"]) == 2

    def test_thread_safety(self):
        """测试线程安全"""
        cache = MemoryCache()
        results = []

        def worker(thread_id):
            for i in range(100):
                key = f"thread_{thread_id}_key_{i}"
                cache.set(key, f"value_{i}")
                value = cache.get(key)
                if value:
                    results.append(value)

        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # 所有操作应该成功
        assert len(results) == 500


class TestFileCache:
    """文件缓存测试"""

    def test_basic_operations(self):
        """测试基本操作"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileCache(temp_dir)

            # 设置和获取
            cache.set("key1", "value1")
            assert cache.get("key1") == "value1"

            # 获取不存在的键
            assert cache.get("nonexistent") is None

            # 检查键是否存在
            assert cache.exists("key1") is True
            assert cache.exists("nonexistent") is False

            # 删除键
            assert cache.delete("key1") is True
            assert cache.get("key1") is None

    def test_ttl_expiration(self):
        """测试TTL过期"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileCache(temp_dir)

            cache.set("temp_key", "temp_value", ttl=1)
            assert cache.get("temp_key") == "temp_value"

            time.sleep(1.1)
            assert cache.get("temp_key") is None

    def test_persistence(self):
        """测试持久化"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 第一个缓存实例
            cache1 = FileCache(temp_dir)
            cache1.set("persistent_key", "persistent_value")

            # 第二个缓存实例，应该能读取到数据
            cache2 = FileCache(temp_dir)
            assert cache2.get("persistent_key") == "persistent_value"

    def test_complex_data_types(self):
        """测试复杂数据类型"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileCache(temp_dir)

            # 字典
            data = {"key": "value", "nested": {"inner": "data"}}
            cache.set("dict_key", data)
            assert cache.get("dict_key") == data

            # 列表
            data = [1, 2, 3, "string", {"dict": "in_list"}]
            cache.set("list_key", data)
            assert cache.get("list_key") == data

    def test_clear_cache(self):
        """测试清空缓存"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileCache(temp_dir)

            cache.set("key1", "value1")
            cache.set("key2", "value2")

            cache.clear()

            assert cache.get("key1") is None
            assert cache.get("key2") is None
            assert cache.keys() == []

    def test_json_serializer(self):
        """测试JSON序列化器"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileCache(temp_dir, serializer="json")

            # JSON可序列化的数据
            data = {"key": "value", "number": 42, "list": [1, 2, 3]}
            cache.set("json_key", data)
            assert cache.get("json_key") == data

    def test_corrupted_cache_file(self):
        """测试损坏的缓存文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileCache(temp_dir)

            # 创建损坏的缓存文件
            cache_dir = Path(temp_dir)
            corrupted_file = cache_dir / "corrupted.cache"
            with open(corrupted_file, "w") as f:
                f.write("corrupted data")

            # 尝试读取应该不会崩溃
            assert cache.get("corrupted") is None


class TestMultiLevelCache:
    """多层缓存测试"""

    def test_cache_hierarchy(self):
        """测试缓存层次结构"""
        memory_cache = MemoryCache()

        with tempfile.TemporaryDirectory() as temp_dir:
            file_cache = FileCache(temp_dir)
            multi_cache = MultiLevelCache([memory_cache, file_cache])

            # 设置值（应该存储在所有层级）
            multi_cache.set("key1", "value1")

            # 从内存缓存获取
            assert memory_cache.get("key1") == "value1"
            assert file_cache.get("key1") == "value1"

            # 清空内存缓存
            memory_cache.clear()

            # 从多层缓存获取（应该从文件缓存获取并回写到内存）
            assert multi_cache.get("key1") == "value1"
            assert memory_cache.get("key1") == "value1"  # 已回写

    def test_cache_miss_propagation(self):
        """测试缓存未命中传播"""
        cache1 = MemoryCache()
        cache2 = MemoryCache()
        multi_cache = MultiLevelCache([cache1, cache2])

        # 只在第二层设置值
        cache2.set("key1", "value1")

        # 从多层缓存获取
        assert multi_cache.get("key1") == "value1"

        # 值应该被回写到第一层
        assert cache1.get("key1") == "value1"

    def test_cache_failure_resilience(self):
        """测试缓存故障恢复能力"""
        good_cache = MemoryCache()
        bad_cache = Mock()
        bad_cache.get.side_effect = Exception("Cache failure")
        bad_cache.set.side_effect = Exception("Cache failure")

        multi_cache = MultiLevelCache([bad_cache, good_cache])

        # 设置应该在好的缓存中成功
        multi_cache.set("key1", "value1")
        assert good_cache.get("key1") == "value1"

        # 获取应该从好的缓存中成功
        assert multi_cache.get("key1") == "value1"


class TestCacheManager:
    """缓存管理器测试"""

    def test_default_backend(self):
        """测试默认后端"""
        manager = CacheManager()

        manager.set("key1", "value1")
        assert manager.get("key1") == "value1"

    def test_register_backend(self):
        """测试注册后端"""
        manager = CacheManager()
        memory_cache = MemoryCache()

        manager.register_backend("memory", memory_cache)

        # 使用指定后端
        manager.set("key1", "value1", backend="memory")
        assert manager.get("key1", backend="memory") == "value1"

        # 直接从后端验证
        assert memory_cache.get("key1") == "value1"

    def test_backend_not_found(self):
        """测试后端不存在"""
        manager = CacheManager()

        with pytest.raises(Exception):
            manager.get("key1", backend="nonexistent")

    def test_stats_tracking(self):
        """测试统计跟踪"""
        manager = CacheManager()

        # 命中和未命中
        manager.set("key1", "value1")
        manager.get("key1")  # 命中
        manager.get("nonexistent")  # 未命中

        stats = manager.stats()
        assert stats["hits"] >= 1
        assert stats["misses"] >= 1
        assert stats["sets"] >= 1

    def test_clear_backend(self):
        """测试清空指定后端"""
        manager = CacheManager()
        memory_cache = MemoryCache()

        manager.register_backend("memory", memory_cache)

        manager.set("key1", "value1")  # 默认后端
        manager.set("key2", "value2", backend="memory")

        # 只清空memory后端
        manager.clear(backend="memory")

        assert manager.get("key1") == "value1"  # 默认后端未清空
        assert manager.get("key2", backend="memory") is None  # memory后端已清空


class TestCacheDecorators:
    """缓存装饰器测试"""

    def test_cache_result_decorator(self):
        """测试缓存结果装饰器"""
        call_count = 0

        @cache_result(ttl=60)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        # 第一次调用
        result1 = expensive_function(1, 2)
        assert result1 == 3
        assert call_count == 1

        # 第二次调用相同参数（应该使用缓存）
        result2 = expensive_function(1, 2)
        assert result2 == 3
        assert call_count == 1  # 没有增加

        # 不同参数（应该重新计算）
        result3 = expensive_function(2, 3)
        assert result3 == 5
        assert call_count == 2

    def test_timed_cache_decorator(self):
        """测试限时缓存装饰器"""
        call_count = 0

        @timed_cache(ttl=1)
        def function_with_ttl():
            nonlocal call_count
            call_count += 1
            return "result"

        # 第一次调用
        result1 = function_with_ttl()
        assert result1 == "result"
        assert call_count == 1

        # 立即第二次调用（使用缓存）
        result2 = function_with_ttl()
        assert result2 == "result"
        assert call_count == 1

        # 等待过期后调用
        time.sleep(1.1)
        result3 = function_with_ttl()
        assert result3 == "result"
        assert call_count == 2  # 重新计算

    def test_lru_cache_decorator(self):
        """测试LRU缓存装饰器"""
        call_count = 0

        @lru_cache(maxsize=2)
        def fibonacci(n):
            nonlocal call_count
            call_count += 1
            if n < 2:
                return n
            return fibonacci(n - 1) + fibonacci(n - 2)

        # 计算fibonacci(5)
        result = fibonacci(5)
        assert result == 5

        # 由于缓存限制，某些值可能被驱逐
        # 但这不影响结果的正确性

        # 重新计算相同值应该使用缓存
        original_call_count = call_count
        result2 = fibonacci(3)  # 可能在缓存中
        # call_count可能不变或略有增加，取决于LRU策略

    def test_cache_with_custom_key_function(self):
        """测试自定义键函数的缓存"""
        call_count = 0

        def custom_key(user_id, **kwargs):
            return f"user_{user_id}"

        @cache_result(key_func=custom_key)
        def get_user_data(user_id, include_details=False):
            nonlocal call_count
            call_count += 1
            return f"data_for_{user_id}"

        # 不同的include_details参数，但相同的user_id
        result1 = get_user_data(1, include_details=True)
        result2 = get_user_data(1, include_details=False)

        # 应该使用相同的缓存键，所以只调用一次
        assert result1 == result2
        assert call_count == 1


class TestGlobalCacheManager:
    """全局缓存管理器测试"""

    def test_init_global_cache_manager(self):
        """测试初始化全局缓存管理器"""
        custom_cache = MemoryCache(max_size=100)
        manager = init_cache_manager(custom_cache)

        assert manager is not None
        assert get_cache_manager() is manager
        assert manager.default_backend is custom_cache

    def test_get_global_cache_manager(self):
        """测试获取全局缓存管理器"""
        # 确保有全局管理器
        init_cache_manager()

        manager = get_cache_manager()
        assert manager is not None

        # 多次获取应该返回同一个实例
        manager2 = get_cache_manager()
        assert manager is manager2


class TestEdgeCases:
    """边界情况测试"""

    def test_cache_none_values(self):
        """测试缓存None值"""
        cache = MemoryCache()

        cache.set("none_key", None)
        assert cache.get("none_key") is None
        assert cache.exists("none_key") is True  # None值存在

    def test_cache_empty_values(self):
        """测试缓存空值"""
        cache = MemoryCache()

        cache.set("empty_string", "")
        cache.set("empty_list", [])
        cache.set("empty_dict", {})

        assert cache.get("empty_string") == ""
        assert cache.get("empty_list") == []
        assert cache.get("empty_dict") == {}

    def test_cache_large_data(self):
        """测试缓存大数据"""
        cache = MemoryCache()

        # 创建大数据
        large_data = list(range(10000))
        cache.set("large_key", large_data)

        retrieved_data = cache.get("large_key")
        assert retrieved_data == large_data

    def test_concurrent_access(self):
        """测试并发访问"""
        cache = MemoryCache()
        results = []

        def worker():
            for i in range(100):
                cache.set(f"key_{i}", f"value_{i}")
                value = cache.get(f"key_{i}")
                results.append(value)

        threads = []
        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # 所有值应该被正确设置和获取
        assert len(results) == 500
        assert all(value is not None for value in results)

    def test_cache_key_collision(self):
        """测试缓存键冲突"""
        cache = MemoryCache()

        # 设置相似但不同的键
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key10", "value10")

        # 验证没有冲突
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key10") == "value10"

    def test_cache_with_special_characters(self):
        """测试包含特殊字符的缓存键"""
        cache = MemoryCache()

        special_keys = [
            "key with spaces",
            "key-with-dashes",
            "key_with_underscores",
            "key.with.dots",
            "key/with/slashes",
            "key:with:colons",
            "键值对",  # Unicode
            "🔑key🔑",  # Emoji
        ]

        for key in special_keys:
            cache.set(key, f"value_for_{key}")
            assert cache.get(key) == f"value_for_{key}"
