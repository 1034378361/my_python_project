"""
性能优化工具

提供性能监控、内存优化、缓存优化等功能。
"""

import functools
import gc
import json
import statistics
import sys
import threading
import time
import weakref
from collections import defaultdict, deque
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, history_size: int = 1000):
        """
        初始化性能监控器

        Args:
            history_size: 历史记录大小
        """
        self.history_size = history_size
        self._timings: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=history_size)
        )
        self._counters: Dict[str, int] = defaultdict(int)
        self._memory_usage: deque = deque(maxlen=history_size)
        self._lock = threading.RLock()

    def record_timing(self, name: str, duration: float) -> None:
        """记录执行时间"""
        with self._lock:
            self._timings[name].append(duration)
            self._counters[f"{name}_calls"] += 1

    def increment_counter(self, name: str, value: int = 1) -> None:
        """增加计数器"""
        with self._lock:
            self._counters[name] += value

    def record_memory_usage(self) -> None:
        """记录内存使用情况"""
        try:
            import psutil

            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            with self._lock:
                self._memory_usage.append((time.time(), memory_mb))
        except ImportError:
            # 如果没有psutil，使用简单的内存监控
            import sys

            objects_count = len(gc.get_objects())
            with self._lock:
                self._memory_usage.append((time.time(), objects_count))

    def get_stats(self, name: Optional[str] = None) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            if name:
                if name in self._timings:
                    timings = list(self._timings[name])
                    return {
                        "count": len(timings),
                        "total_time": sum(timings),
                        "avg_time": sum(timings) / len(timings) if timings else 0,
                        "min_time": min(timings) if timings else 0,
                        "max_time": max(timings) if timings else 0,
                        "recent_times": timings[-10:],  # 最近10次
                    }
                else:
                    return {"count": 0}
            else:
                stats = {}
                for timing_name, timings in self._timings.items():
                    timings_list = list(timings)
                    stats[timing_name] = {
                        "count": len(timings_list),
                        "total_time": sum(timings_list),
                        "avg_time": sum(timings_list) / len(timings_list)
                        if timings_list
                        else 0,
                        "min_time": min(timings_list) if timings_list else 0,
                        "max_time": max(timings_list) if timings_list else 0,
                    }

                # 添加计数器统计
                stats["counters"] = dict(self._counters)

                # 添加内存统计
                if self._memory_usage:
                    recent_memory = [mem for _, mem in list(self._memory_usage)[-10:]]
                    stats["memory"] = {
                        "current": recent_memory[-1] if recent_memory else 0,
                        "avg": sum(recent_memory) / len(recent_memory)
                        if recent_memory
                        else 0,
                        "max": max(recent_memory) if recent_memory else 0,
                        "min": min(recent_memory) if recent_memory else 0,
                    }

                return stats

    def reset(self) -> None:
        """重置所有统计"""
        with self._lock:
            self._timings.clear()
            self._counters.clear()
            self._memory_usage.clear()


# 全局性能监控器
global_monitor = PerformanceMonitor()


def monitor_performance(
    name: str | None = None, monitor: PerformanceMonitor | None = None
):
    """
    性能监控装饰器

    Args:
        name: 监控名称
        monitor: 性能监控器实例
    """

    def decorator(func: Callable) -> Callable:
        monitor_instance = monitor or global_monitor
        monitor_name = name or f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                monitor_instance.record_timing(monitor_name, duration)
                monitor_instance.record_memory_usage()

        return wrapper

    return decorator


class ObjectPool:
    """对象池，用于重用昂贵的对象"""

    def __init__(
        self,
        factory: Callable,
        max_size: int = 10,
        reset_func: Callable | None = None,
    ):
        """
        初始化对象池

        Args:
            factory: 对象工厂函数
            max_size: 最大池大小
            reset_func: 重置对象的函数
        """
        self.factory = factory
        self.max_size = max_size
        self.reset_func = reset_func
        self._pool: list[Any] = []
        self._lock = threading.Lock()

    def acquire(self) -> Any:
        """获取对象"""
        with self._lock:
            if self._pool:
                return self._pool.pop()
            else:
                return self.factory()

    def release(self, obj: Any) -> None:
        """释放对象回池中"""
        with self._lock:
            if len(self._pool) < self.max_size:
                if self.reset_func:
                    self.reset_func(obj)
                self._pool.append(obj)

    def __enter__(self):
        """上下文管理器支持"""
        self._current_obj = self.acquire()
        return self._current_obj

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器支持"""
        self.release(self._current_obj)
        del self._current_obj


class WeakCache:
    """弱引用缓存，自动清理不再使用的对象"""

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._weak_refs: Dict[str, weakref.ReferenceType] = {}

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key in self._weak_refs:
            obj = self._weak_refs[key]()
            if obj is not None:
                return obj
            else:
                # 对象已被垃圾回收，清理缓存
                del self._weak_refs[key]
                self._cache.pop(key, None)
        return None

    def set(self, key: str, value: Any) -> None:
        """设置缓存值"""

        def cleanup(ref):
            self._cache.pop(key, None)
            self._weak_refs.pop(key, None)

        self._weak_refs[key] = weakref.ref(value, cleanup)
        self._cache[key] = True  # 标记存在

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._weak_refs.clear()


class BatchProcessor:
    """批处理器，将多个操作批量执行以提高性能"""

    def __init__(
        self,
        processor: Callable[[List], Any],
        batch_size: int = 100,
        flush_interval: float = 1.0,
    ):
        """
        初始化批处理器

        Args:
            processor: 批处理函数
            batch_size: 批处理大小
            flush_interval: 刷新间隔（秒）
        """
        self.processor = processor
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._batch: List[Any] = []
        self._last_flush = time.time()
        self._lock = threading.Lock()

    def add(self, item: Any) -> None:
        """添加项目到批处理"""
        with self._lock:
            self._batch.append(item)

            # 检查是否需要刷新
            should_flush = (
                len(self._batch) >= self.batch_size
                or time.time() - self._last_flush >= self.flush_interval
            )

            if should_flush:
                self._flush()

    def _flush(self) -> None:
        """刷新批处理"""
        if self._batch:
            batch = self._batch.copy()
            self._batch.clear()
            self._last_flush = time.time()

            try:
                self.processor(batch)
            except Exception as e:
                # 处理失败，可以实现重试逻辑
                pass

    def flush(self) -> None:
        """手动刷新"""
        with self._lock:
            self._flush()


def memoize_with_ttl(ttl: float = 300):
    """
    带TTL的记忆化装饰器

    Args:
        ttl: 生存时间（秒）
    """

    def decorator(func: Callable) -> Callable:
        cache = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 创建缓存键
            key = (args, tuple(sorted(kwargs.items())))
            current_time = time.time()

            # 检查缓存
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < ttl:
                    return result
                else:
                    del cache[key]

            # 计算结果并缓存
            result = func(*args, **kwargs)
            cache[key] = (result, current_time)

            return result

        # 添加缓存管理方法
        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_info = lambda: {"cache_size": len(cache), "ttl": ttl}

        return wrapper

    return decorator


def profile_memory_usage(func: Callable) -> Callable:
    """
    内存使用分析装饰器
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import tracemalloc

        # 开始跟踪
        tracemalloc.start()
        initial_memory = tracemalloc.get_traced_memory()[0]

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            current_memory, peak_memory = tracemalloc.get_traced_memory()
            memory_diff = current_memory - initial_memory

            print(f"函数 {func.__name__} 内存使用:")
            print(f"  内存变化: {memory_diff / 1024 / 1024:.2f} MB")
            print(f"  峰值内存: {peak_memory / 1024 / 1024:.2f} MB")

            tracemalloc.stop()

    return wrapper


class LazyProperty:
    """延迟属性，只在第一次访问时计算"""

    def __init__(self, func: Callable):
        self.func = func
        self.__doc__ = func.__doc__

    def __get__(self, obj, cls):
        if obj is None:
            return self

        value = self.func(obj)
        setattr(obj, self.func.__name__, value)
        return value


def optimize_gc(generation: int = 0, threshold_factor: float = 1.5):
    """
    优化垃圾回收设置

    Args:
        generation: 垃圾回收代数
        threshold_factor: 阈值因子
    """
    import gc

    # 获取当前阈值
    thresholds = gc.get_threshold()

    # 调整阈值
    new_thresholds = tuple(
        int(t * threshold_factor) if i >= generation else t
        for i, t in enumerate(thresholds)
    )

    gc.set_threshold(*new_thresholds)

    # 启用垃圾回收调试（开发环境）
    if __debug__:
        gc.set_debug(gc.DEBUG_STATS)


# 性能分析工具
def benchmark(
    func: Callable, *args, iterations: int = 1000, **kwargs
) -> Dict[str, float]:
    """
    性能基准测试

    Args:
        func: 要测试的函数
        *args: 函数参数
        iterations: 迭代次数
        **kwargs: 函数关键字参数

    Returns:
        性能统计信息
    """
    times = []

    for _ in range(iterations):
        start_time = time.perf_counter()
        func(*args, **kwargs)
        end_time = time.perf_counter()
        times.append(end_time - start_time)

    return {
        "iterations": iterations,
        "total_time": sum(times),
        "avg_time": sum(times) / len(times),
        "min_time": min(times),
        "max_time": max(times),
        "median_time": sorted(times)[len(times) // 2],
    }


# 高级性能追踪功能


@dataclass
class PerformanceMetric:
    """性能指标数据类"""

    name: str
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
        }


class AdvancedPerformanceTracker:
    """高级性能追踪器"""

    def __init__(self, sampling_interval: float = 1.0):
        """
        初始化高级性能追踪器

        Args:
            sampling_interval: 采样间隔（秒）
        """
        self.sampling_interval = sampling_interval
        self.metrics: List[PerformanceMetric] = []
        self.is_running = False
        self._background_thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
        self._start_time = time.time()

        # 性能阈值
        self.thresholds = {
            "cpu_usage": 80.0,  # CPU使用率阈值(%)
            "memory_usage": 85.0,  # 内存使用率阈值(%)
            "response_time": 1.0,  # 响应时间阈值(秒)
            "error_rate": 5.0,  # 错误率阈值(%)
        }

        # 告警回调
        self.alert_callbacks: List[Callable] = []

    def add_metric(
        self,
        name: str,
        value: float,
        unit: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """添加性能指标"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            context=context or {},
        )

        with self._lock:
            self.metrics.append(metric)

        # 检查阈值
        self._check_thresholds(metric)

    def start_monitoring(self) -> None:
        """开始后台监控"""
        if self.is_running:
            return

        self.is_running = True
        self._background_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self._background_thread.start()

    def stop_monitoring(self) -> None:
        """停止后台监控"""
        self.is_running = False
        if self._background_thread:
            self._background_thread.join(timeout=5.0)

    def _monitoring_loop(self) -> None:
        """监控循环"""
        while self.is_running:
            try:
                self._collect_system_metrics()
                time.sleep(self.sampling_interval)
            except Exception as e:
                print(f"监控错误: {e}")

    def _collect_system_metrics(self) -> None:
        """收集系统指标"""
        try:
            import psutil

            # CPU使用率
            cpu_percent = psutil.cpu_percent()
            self.add_metric("cpu_usage", cpu_percent, "%")

            # 内存使用率
            memory = psutil.virtual_memory()
            self.add_metric("memory_usage", memory.percent, "%")
            self.add_metric("memory_available", memory.available / 1024**3, "GB")

            # 磁盘I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                self.add_metric("disk_read_mb", disk_io.read_bytes / 1024**2, "MB")
                self.add_metric("disk_write_mb", disk_io.write_bytes / 1024**2, "MB")

            # 网络I/O
            net_io = psutil.net_io_counters()
            if net_io:
                self.add_metric("network_sent_mb", net_io.bytes_sent / 1024**2, "MB")
                self.add_metric("network_recv_mb", net_io.bytes_recv / 1024**2, "MB")

        except ImportError:
            # psutil不可用，使用基本指标
            self._collect_basic_metrics()
        except Exception as e:
            print(f"收集系统指标失败: {e}")

    def _collect_basic_metrics(self) -> None:
        """收集基本指标（不需要psutil）"""
        # Python进程信息
        import resource

        # 内存使用量
        memory_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # 在Linux上是KB，在macOS上是字节
        if sys.platform == "darwin":
            memory_mb = memory_usage / 1024**2
        else:
            memory_mb = memory_usage / 1024

        self.add_metric("process_memory", memory_mb, "MB")

        # 垃圾回收信息
        gc_stats = gc.get_stats()
        for i, gen_stats in enumerate(gc_stats):
            self.add_metric(f"gc_gen{i}_collections", gen_stats["collections"], "count")
            self.add_metric(f"gc_gen{i}_collected", gen_stats["collected"], "count")

    def _check_thresholds(self, metric: PerformanceMetric) -> None:
        """检查阈值并触发告警"""
        threshold = self.thresholds.get(metric.name)
        if threshold and metric.value > threshold:
            alert_data = {
                "metric": metric.to_dict(),
                "threshold": threshold,
                "severity": "warning" if metric.value < threshold * 1.2 else "critical",
            }

            for callback in self.alert_callbacks:
                try:
                    callback(alert_data)
                except Exception as e:
                    print(f"告警回调失败: {e}")

    def add_alert_callback(self, callback: Callable) -> None:
        """添加告警回调"""
        self.alert_callbacks.append(callback)

    def get_metrics_by_name(
        self, name: str, time_range: Optional[timedelta] = None
    ) -> List[PerformanceMetric]:
        """按名称获取指标"""
        now = datetime.now()
        with self._lock:
            metrics = [m for m in self.metrics if m.name == name]

            if time_range:
                cutoff_time = now - time_range
                metrics = [m for m in metrics if m.timestamp >= cutoff_time]

            return metrics

    def get_statistics(
        self, metric_name: str, time_range: Optional[timedelta] = None
    ) -> Dict[str, float]:
        """获取指标统计信息"""
        metrics = self.get_metrics_by_name(metric_name, time_range)
        if not metrics:
            return {}

        values = [m.value for m in metrics]

        return {
            "count": len(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0,
            "p95": statistics.quantiles(values, n=20)[18]
            if len(values) >= 20
            else max(values),
            "p99": statistics.quantiles(values, n=100)[98]
            if len(values) >= 100
            else max(values),
        }

    def export_metrics(
        self, format: str = "json", time_range: Optional[timedelta] = None
    ) -> str:
        """导出指标数据"""
        now = datetime.now()
        with self._lock:
            metrics = self.metrics.copy()

            if time_range:
                cutoff_time = now - time_range
                metrics = [m for m in metrics if m.timestamp >= cutoff_time]

        if format == "json":
            return json.dumps([m.to_dict() for m in metrics], indent=2, default=str)
        elif format == "csv":
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)

            # 写入表头
            writer.writerow(["name", "value", "unit", "timestamp", "context"])

            # 写入数据
            for metric in metrics:
                writer.writerow(
                    [
                        metric.name,
                        metric.value,
                        metric.unit,
                        metric.timestamp.isoformat(),
                        json.dumps(metric.context),
                    ]
                )

            return output.getvalue()
        else:
            raise ValueError(f"不支持的格式: {format}")

    def generate_report(self, time_range: Optional[timedelta] = None) -> str:
        """生成性能报告"""
        now = datetime.now()
        uptime = now.timestamp() - self._start_time

        report = [
            "性能追踪报告",
            "=" * 50,
            f"报告时间: {now.strftime('%Y-%m-%d %H:%M:%S')}",
            f"运行时间: {uptime:.2f} 秒",
            "",
        ]

        # 获取所有指标名称
        with self._lock:
            metric_names = set(m.name for m in self.metrics)

        # 为每个指标生成统计
        for name in sorted(metric_names):
            stats = self.get_statistics(name, time_range)
            if stats:
                report.extend(
                    [
                        f"指标: {name}",
                        f"  样本数: {stats['count']}",
                        f"  平均值: {stats['mean']:.4f}",
                        f"  中位数: {stats['median']:.4f}",
                        f"  最小值: {stats['min']:.4f}",
                        f"  最大值: {stats['max']:.4f}",
                        f"  标准差: {stats['std_dev']:.4f}",
                        f"  95分位: {stats['p95']:.4f}",
                        f"  99分位: {stats['p99']:.4f}",
                        "",
                    ]
                )

        return "\n".join(report)


class RequestTracker:
    """请求追踪器"""

    def __init__(self):
        self.requests: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()

    @contextmanager
    def track_request(self, request_id: str, metadata: Optional[Dict[str, Any]] = None):
        """追踪请求的上下文管理器"""
        start_time = time.time()

        with self._lock:
            self.requests[request_id] = {
                "start_time": start_time,
                "metadata": metadata or {},
                "events": [],
                "status": "running",
            }

        try:
            yield self._create_request_context(request_id)
        except Exception as e:
            self._update_request_status(request_id, "failed", error=str(e))
            raise
        else:
            self._update_request_status(request_id, "completed")
        finally:
            end_time = time.time()
            with self._lock:
                if request_id in self.requests:
                    self.requests[request_id]["end_time"] = end_time
                    self.requests[request_id]["duration"] = end_time - start_time

    def _create_request_context(self, request_id: str):
        """创建请求上下文"""

        class RequestContext:
            def __init__(self, tracker, req_id):
                self.tracker = tracker
                self.request_id = req_id

            def add_event(self, event: str, data: Optional[Dict[str, Any]] = None):
                """添加事件"""
                self.tracker._add_request_event(self.request_id, event, data)

            def set_metadata(self, key: str, value: Any):
                """设置元数据"""
                self.tracker._set_request_metadata(self.request_id, key, value)

        return RequestContext(self, request_id)

    def _add_request_event(
        self, request_id: str, event: str, data: Optional[Dict[str, Any]] = None
    ):
        """添加请求事件"""
        with self._lock:
            if request_id in self.requests:
                self.requests[request_id]["events"].append(
                    {"event": event, "timestamp": time.time(), "data": data or {}}
                )

    def _set_request_metadata(self, request_id: str, key: str, value: Any):
        """设置请求元数据"""
        with self._lock:
            if request_id in self.requests:
                self.requests[request_id]["metadata"][key] = value

    def _update_request_status(self, request_id: str, status: str, **kwargs):
        """更新请求状态"""
        with self._lock:
            if request_id in self.requests:
                self.requests[request_id]["status"] = status
                self.requests[request_id].update(kwargs)

    def get_request_info(self, request_id: str) -> Optional[Dict[str, Any]]:
        """获取请求信息"""
        with self._lock:
            return self.requests.get(request_id, {}).copy()

    def get_slow_requests(self, threshold: float = 1.0) -> List[Dict[str, Any]]:
        """获取慢请求"""
        with self._lock:
            slow_requests = []
            for req_id, req_info in self.requests.items():
                duration = req_info.get("duration", 0)
                if duration > threshold:
                    slow_requests.append(
                        {"request_id": req_id, "duration": duration, **req_info}
                    )

            return sorted(slow_requests, key=lambda x: x["duration"], reverse=True)

    def cleanup_old_requests(self, max_age: float = 3600):
        """清理旧请求记录"""
        current_time = time.time()
        with self._lock:
            to_remove = []
            for req_id, req_info in self.requests.items():
                start_time = req_info.get("start_time", current_time)
                if current_time - start_time > max_age:
                    to_remove.append(req_id)

            for req_id in to_remove:
                del self.requests[req_id]


class MemoryProfiler:
    """内存分析器"""

    def __init__(self):
        self.snapshots: List[Dict[str, Any]] = []
        self._baseline: Optional[Dict[str, Any]] = None

    def take_snapshot(self, label: str = "") -> Dict[str, Any]:
        """拍摄内存快照"""
        try:
            import tracemalloc

            if not tracemalloc.is_tracing():
                tracemalloc.start()

            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics("lineno")

            # 分析前10个内存使用最多的位置
            top_10 = []
            for stat in top_stats[:10]:
                top_10.append(
                    {
                        "filename": stat.traceback.format()[0]
                        if stat.traceback
                        else "unknown",
                        "size_mb": stat.size / 1024**2,
                        "count": stat.count,
                    }
                )

            snapshot_data = {
                "timestamp": time.time(),
                "label": label,
                "total_size_mb": sum(stat.size for stat in top_stats) / 1024**2,
                "total_count": sum(stat.count for stat in top_stats),
                "top_allocations": top_10,
            }

            self.snapshots.append(snapshot_data)
            return snapshot_data

        except ImportError:
            # tracemalloc不可用，使用基本内存信息
            import sys

            snapshot_data = {
                "timestamp": time.time(),
                "label": label,
                "total_size_mb": sys.getsizeof({}),  # 简化的内存信息
                "total_count": 1,
                "top_allocations": [],
            }
            self.snapshots.append(snapshot_data)
            return snapshot_data

    def set_baseline(self, label: str = "baseline"):
        """设置内存基线"""
        self._baseline = self.take_snapshot(label)

    def compare_with_baseline(self) -> Optional[Dict[str, Any]]:
        """与基线比较"""
        if not self._baseline or not self.snapshots:
            return None

        current = self.snapshots[-1]

        return {
            "baseline": self._baseline,
            "current": current,
            "size_diff_mb": current["total_size_mb"] - self._baseline["total_size_mb"],
            "count_diff": current["total_count"] - self._baseline["total_count"],
            "time_diff": current["timestamp"] - self._baseline["timestamp"],
        }

    def get_memory_trend(self) -> Dict[str, Any]:
        """获取内存趋势"""
        if len(self.snapshots) < 2:
            return {}

        sizes = [s["total_size_mb"] for s in self.snapshots]
        timestamps = [s["timestamp"] for s in self.snapshots]

        # 计算趋势
        if len(sizes) > 1:
            growth_rate = (sizes[-1] - sizes[0]) / (timestamps[-1] - timestamps[0])
        else:
            growth_rate = 0

        return {
            "snapshot_count": len(self.snapshots),
            "min_size_mb": min(sizes),
            "max_size_mb": max(sizes),
            "current_size_mb": sizes[-1],
            "growth_rate_mb_per_sec": growth_rate,
            "total_time_span": timestamps[-1] - timestamps[0],
        }


# 全局性能追踪器实例
_global_tracker = AdvancedPerformanceTracker()
_request_tracker = RequestTracker()
_memory_profiler = MemoryProfiler()


def get_performance_tracker() -> AdvancedPerformanceTracker:
    """获取全局性能追踪器"""
    return _global_tracker


def get_request_tracker() -> RequestTracker:
    """获取全局请求追踪器"""
    return _request_tracker


def get_memory_profiler() -> MemoryProfiler:
    """获取全局内存分析器"""
    return _memory_profiler


def track_performance(
    metric_name: str,
    value: float,
    unit: str = "",
    context: Optional[Dict[str, Any]] = None,
):
    """添加性能指标到全局追踪器"""
    _global_tracker.add_metric(metric_name, value, unit, context)


def start_performance_monitoring():
    """启动全局性能监控"""
    _global_tracker.start_monitoring()


def stop_performance_monitoring():
    """停止全局性能监控"""
    _global_tracker.stop_monitoring()


# 装饰器增强
def advanced_performance_monitor(
    metric_prefix: str = "", include_memory: bool = False, include_gc: bool = False
):
    """高级性能监控装饰器"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 准备指标名称
            base_name = metric_prefix or func.__name__

            # 内存快照（如果需要）
            if include_memory:
                _memory_profiler.take_snapshot(f"{base_name}_start")

            # GC信息（如果需要）
            gc_before = None
            if include_gc:
                gc_before = gc.get_stats()

            # 执行函数并测量时间
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                track_performance(f"{base_name}_success", 1, "count")
                return result
            except Exception as e:
                track_performance(
                    f"{base_name}_error",
                    1,
                    "count",
                    {"error_type": type(e).__name__, "error_message": str(e)},
                )
                raise
            finally:
                end_time = time.perf_counter()
                duration = end_time - start_time

                # 记录执行时间
                track_performance(f"{base_name}_duration", duration, "seconds")

                # 内存快照（如果需要）
                if include_memory:
                    _memory_profiler.take_snapshot(f"{base_name}_end")

                # GC信息（如果需要）
                if include_gc and gc_before:
                    gc_after = gc.get_stats()
                    for i, (before, after) in enumerate(zip(gc_before, gc_after)):
                        collections_diff = after["collections"] - before["collections"]
                        if collections_diff > 0:
                            track_performance(
                                f"{base_name}_gc_gen{i}",
                                collections_diff,
                                "collections",
                            )

        return wrapper

    return decorator
