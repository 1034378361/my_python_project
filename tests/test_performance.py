"""
性能测试

测试各模块的性能表现和资源使用情况。
"""

import time
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from my_python_project import (
    ConfigManager,
    MemoryCache,
    FileCache,
    cache_result,
    validate_data,
    StringValidator,
    NumberValidator,
    DictValidator,
)
from my_python_project.utils.performance import (
    monitor_performance,
    global_monitor,
    benchmark,
    PerformanceMonitor,
    ObjectPool,
    BatchProcessor,
)


class TestCachePerformance:
    """缓存性能测试"""

    def test_memory_cache_performance(self):
        """测试内存缓存性能"""
        cache = MemoryCache(max_size=10000)

        # 测试写入性能
        start_time = time.time()
        for i in range(1000):
            cache.set(f"key_{i}", f"value_{i}")
        write_time = time.time() - start_time

        # 测试读取性能
        start_time = time.time()
        for i in range(1000):
            cache.get(f"key_{i}")
        read_time = time.time() - start_time

        print(f"内存缓存写入1000项耗时: {write_time:.4f}秒")
        print(f"内存缓存读取1000项耗时: {read_time:.4f}秒")

        # 性能断言
        assert write_time < 1.0  # 写入应该在1秒内完成
        assert read_time < 0.1  # 读取应该在0.1秒内完成

    def test_file_cache_performance(self):
        """测试文件缓存性能"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = FileCache(temp_dir)

            # 测试写入性能
            start_time = time.time()
            for i in range(100):  # 文件缓存较慢，使用更少的项目
                cache.set(f"key_{i}", {"data": f"value_{i}", "index": i})
            write_time = time.time() - start_time

            # 测试读取性能
            start_time = time.time()
            for i in range(100):
                cache.get(f"key_{i}")
            read_time = time.time() - start_time

            print(f"文件缓存写入100项耗时: {write_time:.4f}秒")
            print(f"文件缓存读取100项耗时: {read_time:.4f}秒")

            # 文件缓存相对较慢，但应该在合理范围内
            assert write_time < 5.0
            assert read_time < 2.0

    def test_cache_decorator_performance(self):
        """测试缓存装饰器性能"""
        call_count = 0

        @cache_result(ttl=300)
        def expensive_function(n):
            nonlocal call_count
            call_count += 1
            # 模拟耗时计算
            return sum(range(n))

        # 第一次调用（实际计算）
        start_time = time.time()
        result1 = expensive_function(1000)
        first_call_time = time.time() - start_time

        # 第二次调用（使用缓存）
        start_time = time.time()
        result2 = expensive_function(1000)
        cached_call_time = time.time() - start_time

        assert result1 == result2
        assert call_count == 1  # 只调用了一次实际函数
        assert cached_call_time < first_call_time / 10  # 缓存应该快至少10倍


class TestValidationPerformance:
    """验证器性能测试"""

    def test_simple_validation_performance(self):
        """测试简单验证性能"""
        validator = StringValidator(min_length=1, max_length=100)

        # 测试大量验证
        start_time = time.time()
        for i in range(10000):
            validator.validate(f"test_string_{i}", "field")
        validation_time = time.time() - start_time

        print(f"简单验证10000次耗时: {validation_time:.4f}秒")
        assert validation_time < 1.0  # 应该在1秒内完成

    def test_complex_validation_performance(self):
        """测试复杂验证性能"""
        schema = {
            "user": DictValidator(
                schema={
                    "name": StringValidator(min_length=2, max_length=50),
                    "email": StringValidator(pattern=r".+@.+\..+"),
                    "age": NumberValidator(number_type=int, min_value=0, max_value=150),
                    "tags": DictValidator(
                        schema={
                            "primary": StringValidator(),
                            "secondary": StringValidator(required=False),
                        }
                    ),
                }
            )
        }

        test_data = {
            "user": {
                "name": "John Doe",
                "email": "john@example.com",
                "age": 30,
                "tags": {"primary": "developer"},
            }
        }

        # 测试复杂验证性能
        start_time = time.time()
        for _ in range(1000):
            validate_data(test_data, schema)
        validation_time = time.time() - start_time

        print(f"复杂验证1000次耗时: {validation_time:.4f}秒")
        assert validation_time < 2.0  # 应该在2秒内完成


class TestConfigPerformance:
    """配置管理性能测试"""

    def test_config_loading_performance(self):
        """测试配置加载性能"""
        # 创建大配置文件
        large_config = {}
        for i in range(1000):
            large_config[f"section_{i}"] = {
                f"key_{j}": f"value_{i}_{j}" for j in range(10)
            }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            import json

            json.dump(large_config, f)
            config_file = f.name

        try:
            # 测试加载性能
            start_time = time.time()
            config = ConfigManager.from_file(config_file)
            load_time = time.time() - start_time

            # 测试访问性能
            start_time = time.time()
            for i in range(100):
                config.get(f"section_{i}.key_5")
            access_time = time.time() - start_time

            print(f"大配置文件加载耗时: {load_time:.4f}秒")
            print(f"配置访问100次耗时: {access_time:.4f}秒")

            assert load_time < 1.0  # 加载应该在1秒内完成
            assert access_time < 0.1  # 访问应该很快

        finally:
            Path(config_file).unlink()


class TestConcurrencyPerformance:
    """并发性能测试"""

    def test_cache_thread_safety_performance(self):
        """测试缓存线程安全性能"""
        cache = MemoryCache(max_size=1000)

        def worker(thread_id):
            results = []
            for i in range(100):
                key = f"thread_{thread_id}_key_{i}"
                value = f"thread_{thread_id}_value_{i}"

                # 写入
                cache.set(key, value)

                # 读取
                retrieved = cache.get(key)
                results.append(retrieved == value)

            return all(results)

        # 并发测试
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(10)]
            results = [future.result() for future in as_completed(futures)]

        concurrent_time = time.time() - start_time

        print(f"10线程并发缓存操作耗时: {concurrent_time:.4f}秒")
        assert all(results)  # 所有操作应该成功
        assert concurrent_time < 5.0  # 应该在合理时间内完成

    def test_validation_concurrency_performance(self):
        """测试验证器并发性能"""
        validator = StringValidator(min_length=1, max_length=100)

        def validate_batch(batch_id):
            success_count = 0
            for i in range(100):
                try:
                    validator.validate(f"batch_{batch_id}_item_{i}", "field")
                    success_count += 1
                except Exception:
                    pass
            return success_count

        # 并发验证测试
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(validate_batch, i) for i in range(5)]
            results = [future.result() for future in as_completed(futures)]

        concurrent_time = time.time() - start_time

        print(f"5线程并发验证耗时: {concurrent_time:.4f}秒")
        assert sum(results) == 500  # 所有验证应该成功
        assert concurrent_time < 2.0


class TestPerformanceMonitoring:
    """性能监控测试"""

    def test_performance_monitor_overhead(self):
        """测试性能监控开销"""
        monitor = PerformanceMonitor()

        # 不使用监控的函数
        def unmonitored_function(n):
            return sum(range(n))

        # 使用监控的函数
        @monitor_performance("monitored_function", monitor=monitor)
        def monitored_function(n):
            return sum(range(n))

        # 测试未监控版本
        start_time = time.time()
        for _ in range(1000):
            unmonitored_function(100)
        unmonitored_time = time.time() - start_time

        # 测试监控版本
        start_time = time.time()
        for _ in range(1000):
            monitored_function(100)
        monitored_time = time.time() - start_time

        overhead = monitored_time - unmonitored_time
        overhead_percentage = (overhead / unmonitored_time) * 100

        print(f"未监控版本耗时: {unmonitored_time:.4f}秒")
        print(f"监控版本耗时: {monitored_time:.4f}秒")
        print(f"监控开销: {overhead:.4f}秒 ({overhead_percentage:.2f}%)")

        # 监控开销应该很小
        assert overhead_percentage < 50  # 开销应该小于50%

    def test_benchmark_function(self):
        """测试基准测试功能"""

        def test_function(n):
            return sum(range(n))

        # 运行基准测试
        stats = benchmark(test_function, 1000, iterations=100)

        print(f"基准测试结果:")
        print(f"  总时间: {stats['total_time']:.4f}秒")
        print(f"  平均时间: {stats['avg_time']:.6f}秒")
        print(f"  最小时间: {stats['min_time']:.6f}秒")
        print(f"  最大时间: {stats['max_time']:.6f}秒")

        assert stats["iterations"] == 100
        assert stats["avg_time"] > 0
        assert stats["min_time"] <= stats["avg_time"] <= stats["max_time"]


class TestMemoryPerformance:
    """内存性能测试"""

    def test_object_pool_performance(self):
        """测试对象池性能"""

        # 昂贵的对象创建
        def create_expensive_object():
            # 模拟昂贵的对象创建
            return {"data": list(range(1000)), "id": time.time()}

        def reset_object(obj):
            obj["id"] = time.time()

        pool = ObjectPool(create_expensive_object, max_size=5, reset_func=reset_object)

        # 测试对象池性能
        start_time = time.time()
        objects = []
        for _ in range(100):
            obj = pool.acquire()
            objects.append(obj)
            # 模拟使用对象
            _ = sum(obj["data"])

        # 释放对象
        for obj in objects:
            pool.release(obj)

        pool_time = time.time() - start_time

        # 测试直接创建性能
        start_time = time.time()
        for _ in range(100):
            obj = create_expensive_object()
            _ = sum(obj["data"])

        direct_time = time.time() - start_time

        print(f"对象池方式耗时: {pool_time:.4f}秒")
        print(f"直接创建耗时: {direct_time:.4f}秒")

        # 对象池应该更快（在重复使用的情况下）
        improvement = (direct_time - pool_time) / direct_time * 100
        print(f"对象池性能提升: {improvement:.2f}%")

    def test_batch_processor_performance(self):
        """测试批处理器性能"""
        processed_batches = []

        def process_batch(items):
            # 模拟批处理
            processed_batches.append(len(items))
            time.sleep(0.001)  # 模拟处理时间

        processor = BatchProcessor(process_batch, batch_size=50, flush_interval=0.1)

        # 添加项目
        start_time = time.time()
        for i in range(200):
            processor.add(f"item_{i}")

        # 手动刷新剩余项目
        processor.flush()
        batch_time = time.time() - start_time

        # 测试逐个处理
        start_time = time.time()
        for i in range(200):
            process_batch([f"item_{i}"])
        individual_time = time.time() - start_time

        print(f"批处理耗时: {batch_time:.4f}秒")
        print(f"逐个处理耗时: {individual_time:.4f}秒")
        print(f"批处理数量: {len(processed_batches)}")

        # 批处理应该更高效
        assert batch_time < individual_time
        assert len(processed_batches) < 200  # 应该有批量效果


@pytest.mark.slow
class TestStressTest:
    """压力测试"""

    def test_large_dataset_validation(self):
        """测试大数据集验证"""
        # 创建大数据集
        large_dataset = []
        for i in range(1000):
            large_dataset.append(
                {
                    "id": i,
                    "name": f"user_{i}",
                    "email": f"user_{i}@example.com",
                    "age": 20 + (i % 50),
                }
            )

        schema = {
            "id": NumberValidator(number_type=int),
            "name": StringValidator(min_length=1),
            "email": StringValidator(pattern=r".+@.+\..+"),
            "age": NumberValidator(number_type=int, min_value=0, max_value=150),
        }

        start_time = time.time()
        validated_count = 0

        for item in large_dataset:
            try:
                validate_data(item, schema)
                validated_count += 1
            except Exception:
                pass

        validation_time = time.time() - start_time

        print(f"验证1000项数据耗时: {validation_time:.4f}秒")
        print(f"验证成功率: {validated_count / 1000 * 100:.1f}%")

        assert validated_count == 1000  # 所有数据应该都验证成功
        assert validation_time < 5.0  # 应该在合理时间内完成

    def test_cache_memory_usage(self):
        """测试缓存内存使用"""
        cache = MemoryCache(max_size=10000)

        # 填充大量数据
        large_data = "x" * 1000  # 1KB字符串

        start_time = time.time()
        for i in range(5000):
            cache.set(f"large_key_{i}", large_data)

        fill_time = time.time() - start_time

        # 测试访问性能
        start_time = time.time()
        hit_count = 0
        for i in range(5000):
            if cache.get(f"large_key_{i}") is not None:
                hit_count += 1

        access_time = time.time() - start_time

        print(f"填充5000个1KB项目耗时: {fill_time:.4f}秒")
        print(f"访问5000个项目耗时: {access_time:.4f}秒")
        print(f"命中率: {hit_count / 5000 * 100:.1f}%")

        assert fill_time < 2.0  # 填充应该快速
        assert access_time < 0.5  # 访问应该非常快
        assert hit_count >= 4000  # 大部分应该命中（考虑LRU驱逐）
