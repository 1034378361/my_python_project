# 性能监控指南

本文档详细介绍了My Python Project中的高级性能监控功能。

## 目录

1. [概述](#概述)
2. [基础性能监控](#基础性能监控)
3. [高级性能追踪](#高级性能追踪)
4. [请求追踪](#请求追踪)
5. [内存分析](#内存分析)
6. [性能告警](#性能告警)
7. [报告生成](#报告生成)
8. [最佳实践](#最佳实践)

## 概述

项目提供了多层次的性能监控功能：

- **基础监控**: 函数执行时间、内存使用等
- **高级追踪**: 系统指标、统计分析、阈值告警
- **请求追踪**: 端到端请求监控
- **内存分析**: 详细内存使用分析
- **性能报告**: 可视化性能数据

## 基础性能监控

### 简单计时

```python
from my_python_project import timing_decorator

@timing_decorator
def slow_function():
    """被监控的函数"""
    import time
    time.sleep(1)
    return "完成"

# 调用函数，自动打印执行时间
result = slow_function()
```

### 性能监控装饰器

```python
from my_python_project import PerformanceMonitor

monitor = PerformanceMonitor()

@monitor.timer("数据处理")
def process_data(data_size):
    """数据处理函数"""
    import time
    time.sleep(data_size * 0.01)
    return f"处理了 {data_size} 条数据"

# 使用上下文管理器
with monitor.measure("数据库查询"):
    # 模拟数据库查询
    time.sleep(0.2)

# 获取报告
report = monitor.get_report()
print(report)
```

### 基准测试

```python
from my_python_project import benchmark

def test_function(n):
    return sum(range(n))

# 运行基准测试
stats = benchmark(test_function, 10000, iterations=1000)

print(f"平均时间: {stats['avg_time']:.6f}s")
print(f"最小时间: {stats['min_time']:.6f}s")
print(f"最大时间: {stats['max_time']:.6f}s")
```

## 高级性能追踪

### 启用全局监控

```python
from my_python_project import (
    start_performance_monitoring,
    stop_performance_monitoring,
    track_performance,
    get_performance_tracker
)

# 启动全局性能监控
start_performance_monitoring()

# 手动添加指标
track_performance("custom_metric", 42.5, "ms", {
    "component": "data_processor",
    "operation": "transform"
})

# 获取性能追踪器
tracker = get_performance_tracker()

# 添加告警回调
def performance_alert(alert_data):
    print(f"性能告警: {alert_data['metric']['name']} = {alert_data['metric']['value']}")
    print(f"阈值: {alert_data['threshold']}, 严重程度: {alert_data['severity']}")

tracker.add_alert_callback(performance_alert)

# 设置自定义阈值
tracker.thresholds['response_time'] = 0.5  # 500ms

# 停止监控
# stop_performance_monitoring()
```

### 高级装饰器

```python
from my_python_project import advanced_performance_monitor

@advanced_performance_monitor(
    metric_prefix="api_call",
    include_memory=True,
    include_gc=True
)
def api_call(endpoint, data):
    """API调用函数"""
    import requests
    import time
    
    # 模拟API调用
    time.sleep(0.1)
    
    if endpoint == "/error":
        raise Exception("API错误")
    
    return {"status": "success", "data": data}

# 调用函数，自动记录性能指标
try:
    result = api_call("/users", {"name": "test"})
    print(f"API调用成功: {result}")
except Exception as e:
    print(f"API调用失败: {e}")

# 查看性能统计
tracker = get_performance_tracker()
stats = tracker.get_statistics("api_call_duration")
print(f"API调用统计: {stats}")
```

### 系统指标监控

```python
from my_python_project import get_performance_tracker
from datetime import timedelta

tracker = get_performance_tracker()

# 启动后台系统监控
tracker.start_monitoring()

# 等待一段时间收集数据
import time
time.sleep(10)

# 获取CPU使用率统计
cpu_stats = tracker.get_statistics("cpu_usage", timedelta(minutes=5))
print(f"CPU使用率统计: {cpu_stats}")

# 获取内存使用率统计
memory_stats = tracker.get_statistics("memory_usage", timedelta(minutes=5))
print(f"内存使用率统计: {memory_stats}")

# 停止监控
tracker.stop_monitoring()
```

## 请求追踪

### 基础请求追踪

```python
from my_python_project import get_request_tracker
import uuid

request_tracker = get_request_tracker()

def process_user_request(user_id, action):
    """处理用户请求"""
    request_id = str(uuid.uuid4())
    
    with request_tracker.track_request(request_id, {
        "user_id": user_id,
        "action": action,
        "source": "web"
    }) as ctx:
        # 添加事件
        ctx.add_event("validation_start")
        
        # 模拟验证
        time.sleep(0.1)
        ctx.add_event("validation_complete", {"status": "success"})
        
        # 添加处理事件
        ctx.add_event("processing_start")
        time.sleep(0.2)
        
        # 设置结果元数据
        ctx.set_metadata("result_size", 1024)
        ctx.add_event("processing_complete")
        
        return {"request_id": request_id, "status": "completed"}

# 处理请求
result = process_user_request("user123", "update_profile")
print(f"请求结果: {result}")

# 获取请求信息
request_info = request_tracker.get_request_info(result["request_id"])
print(f"请求详情: {request_info}")

# 获取慢请求
slow_requests = request_tracker.get_slow_requests(threshold=0.15)
print(f"慢请求: {slow_requests}")
```

### Web框架集成

```python
from fastapi import FastAPI, Request
from my_python_project import get_request_tracker
import uuid
import time

app = FastAPI()
request_tracker = get_request_tracker()

@app.middleware("http")
async def request_tracking_middleware(request: Request, call_next):
    """请求追踪中间件"""
    request_id = str(uuid.uuid4())
    
    with request_tracker.track_request(request_id, {
        "method": request.method,
        "path": request.url.path,
        "client_ip": request.client.host,
        "user_agent": request.headers.get("user-agent")
    }) as ctx:
        # 添加请求开始事件
        ctx.add_event("request_start")
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 添加成功事件
            ctx.add_event("request_success", {
                "status_code": response.status_code
            })
            
            # 设置响应元数据
            ctx.set_metadata("response_size", len(response.body) if hasattr(response, 'body') else 0)
            
            return response
            
        except Exception as e:
            # 添加错误事件
            ctx.add_event("request_error", {
                "error_type": type(e).__name__,
                "error_message": str(e)
            })
            raise

@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    """获取用户API"""
    # 模拟数据库查询
    await asyncio.sleep(0.1)
    
    return {"user_id": user_id, "name": f"用户{user_id}"}

@app.get("/api/slow")
async def slow_endpoint():
    """慢端点"""
    await asyncio.sleep(2)  # 模拟慢操作
    return {"message": "慢操作完成"}
```

## 内存分析

### 基础内存分析

```python
from my_python_project import get_memory_profiler

profiler = get_memory_profiler()

# 设置基线
profiler.set_baseline("应用启动")

def memory_intensive_operation():
    """内存密集型操作"""
    # 创建大量对象
    data = []
    for i in range(100000):
        data.append({"id": i, "data": f"item_{i}"})
    
    # 拍摄快照
    profiler.take_snapshot("创建对象后")
    
    # 处理数据
    processed = [item for item in data if item["id"] % 2 == 0]
    
    # 再次拍摄快照
    profiler.take_snapshot("处理数据后")
    
    return len(processed)

# 执行操作
result = memory_intensive_operation()
print(f"处理结果: {result}")

# 与基线比较
comparison = profiler.compare_with_baseline()
if comparison:
    print(f"内存增长: {comparison['size_diff_mb']:.2f} MB")
    print(f"对象增长: {comparison['count_diff']}")

# 获取内存趋势
trend = profiler.get_memory_trend()
print(f"内存趋势: {trend}")
```

### 内存泄漏检测

```python
from my_python_project import get_memory_profiler
import gc

profiler = get_memory_profiler()

class PotentialLeak:
    """可能泄漏的类"""
    def __init__(self, data):
        self.data = data
        self.refs = []

def detect_memory_leak():
    """检测内存泄漏"""
    # 设置基线
    profiler.set_baseline("泄漏检测开始")
    
    objects = []
    
    for iteration in range(10):
        # 创建对象
        for i in range(1000):
            obj = PotentialLeak(f"data_{iteration}_{i}")
            objects.append(obj)
        
        # 每次迭代后拍摄快照
        profiler.take_snapshot(f"迭代_{iteration}")
        
        # 模拟一些对象被删除
        if len(objects) > 5000:
            del objects[:1000]
            gc.collect()
    
    # 最终比较
    final_comparison = profiler.compare_with_baseline()
    if final_comparison:
        growth_rate = final_comparison['size_diff_mb'] / final_comparison['time_diff']
        print(f"内存增长率: {growth_rate:.4f} MB/秒")
        
        if growth_rate > 0.1:  # 阈值
            print("⚠️ 检测到潜在内存泄漏")
        else:
            print("✅ 未检测到明显内存泄漏")

# 运行泄漏检测
detect_memory_leak()
```

## 性能告警

### 配置告警规则

```python
from my_python_project import get_performance_tracker

tracker = get_performance_tracker()

# 配置阈值
tracker.thresholds.update({
    'api_response_time': 1.0,      # API响应时间 1秒
    'database_query_time': 0.5,    # 数据库查询时间 500ms
    'memory_usage': 80.0,          # 内存使用率 80%
    'cpu_usage': 85.0,             # CPU使用率 85%
    'error_rate': 5.0,             # 错误率 5%
})

# 告警处理函数
def handle_performance_alert(alert_data):
    """处理性能告警"""
    metric = alert_data['metric']
    threshold = alert_data['threshold']
    severity = alert_data['severity']
    
    print(f"🚨 性能告警")
    print(f"指标: {metric['name']}")
    print(f"当前值: {metric['value']} {metric['unit']}")
    print(f"阈值: {threshold}")
    print(f"严重程度: {severity}")
    print(f"时间: {metric['timestamp']}")
    
    # 可以在这里集成告警系统
    if severity == 'critical':
        send_critical_alert(metric)
    else:
        send_warning_alert(metric)

def send_critical_alert(metric):
    """发送严重告警"""
    print(f"📧 发送严重告警邮件: {metric['name']}")
    # 集成邮件、短信、Slack等告警系统

def send_warning_alert(metric):
    """发送警告告警"""
    print(f"📝 记录警告日志: {metric['name']}")
    # 记录到日志系统

# 注册告警处理器
tracker.add_alert_callback(handle_performance_alert)

# 启动监控
tracker.start_monitoring()
```

### 自定义告警规则

```python
from my_python_project import get_performance_tracker
from datetime import timedelta

tracker = get_performance_tracker()

def custom_alert_checker():
    """自定义告警检查器"""
    # 检查最近5分钟的响应时间
    response_times = tracker.get_metrics_by_name(
        "api_response_time", 
        timedelta(minutes=5)
    )
    
    if len(response_times) > 10:
        # 计算P95响应时间
        values = [m.value for m in response_times]
        values.sort()
        p95_index = int(len(values) * 0.95)
        p95_value = values[p95_index]
        
        if p95_value > 2.0:  # P95超过2秒
            print(f"⚠️ P95响应时间过高: {p95_value:.2f}s")
    
    # 检查错误率
    error_count = len([m for m in tracker.get_metrics_by_name("api_error", timedelta(minutes=5))])
    total_count = len([m for m in tracker.get_metrics_by_name("api_request", timedelta(minutes=5))])
    
    if total_count > 0:
        error_rate = (error_count / total_count) * 100
        if error_rate > 10:  # 错误率超过10%
            print(f"🚨 错误率过高: {error_rate:.2f}%")

# 定期运行自定义检查
import threading
import time

def periodic_check():
    while True:
        custom_alert_checker()
        time.sleep(60)  # 每分钟检查一次

# 启动后台检查
check_thread = threading.Thread(target=periodic_check, daemon=True)
check_thread.start()
```

## 报告生成

### 生成性能报告

```python
from my_python_project import get_performance_tracker
from datetime import timedelta

tracker = get_performance_tracker()

# 生成最近1小时的报告
report = tracker.generate_report(timedelta(hours=1))
print(report)

# 导出指标数据
json_data = tracker.export_metrics('json', timedelta(hours=1))
with open('performance_metrics.json', 'w') as f:
    f.write(json_data)

csv_data = tracker.export_metrics('csv', timedelta(hours=1))
with open('performance_metrics.csv', 'w') as f:
    f.write(csv_data)
```

### 自定义报告

```python
from my_python_project import get_performance_tracker, get_request_tracker
from datetime import datetime, timedelta

def generate_custom_report():
    """生成自定义性能报告"""
    tracker = get_performance_tracker()
    request_tracker = get_request_tracker()
    
    now = datetime.now()
    
    report = [
        "自定义性能报告",
        "=" * 60,
        f"生成时间: {now.strftime('%Y-%m-%d %H:%M:%S')}",
        f"报告周期: 最近1小时",
        ""
    ]
    
    # API性能统计
    api_stats = tracker.get_statistics("api_response_time", timedelta(hours=1))
    if api_stats:
        report.extend([
            "📊 API性能统计:",
            f"  平均响应时间: {api_stats['mean']:.3f}s",
            f"  P95响应时间: {api_stats['p95']:.3f}s",
            f"  P99响应时间: {api_stats['p99']:.3f}s",
            f"  最慢请求: {api_stats['max']:.3f}s",
            ""
        ])
    
    # 系统资源统计
    cpu_stats = tracker.get_statistics("cpu_usage", timedelta(hours=1))
    memory_stats = tracker.get_statistics("memory_usage", timedelta(hours=1))
    
    if cpu_stats:
        report.extend([
            "💻 系统资源统计:",
            f"  平均CPU使用率: {cpu_stats['mean']:.1f}%",
            f"  峰值CPU使用率: {cpu_stats['max']:.1f}%",
        ])
    
    if memory_stats:
        report.extend([
            f"  平均内存使用率: {memory_stats['mean']:.1f}%",
            f"  峰值内存使用率: {memory_stats['max']:.1f}%",
            ""
        ])
    
    # 慢请求分析
    slow_requests = request_tracker.get_slow_requests(threshold=1.0)
    if slow_requests:
        report.extend([
            "🐌 慢请求分析:",
            f"  慢请求总数: {len(slow_requests)}",
        ])
        
        for i, req in enumerate(slow_requests[:5]):  # 显示最慢的5个
            report.append(f"  {i+1}. {req['duration']:.3f}s - {req.get('metadata', {}).get('path', 'unknown')}")
        
        report.append("")
    
    # 错误分析
    error_metrics = [m for m in tracker.metrics if 'error' in m.name]
    if error_metrics:
        error_count = len(error_metrics)
        report.extend([
            "❌ 错误分析:",
            f"  错误总数: {error_count}",
            ""
        ])
    
    return "\n".join(report)

# 生成并保存报告
custom_report = generate_custom_report()
print(custom_report)

# 保存到文件
with open(f'performance_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt', 'w', encoding='utf-8') as f:
    f.write(custom_report)
```

## 最佳实践

### 1. 监控策略

```python
# 分层监控策略
class ApplicationMonitoring:
    def __init__(self):
        self.tracker = get_performance_tracker()
        self.request_tracker = get_request_tracker()
        self.memory_profiler = get_memory_profiler()
    
    def setup_monitoring(self):
        """设置监控"""
        # 1. 系统级监控
        self.tracker.start_monitoring()
        
        # 2. 应用级阈值
        self.tracker.thresholds.update({
            'http_request_duration': 1.0,
            'database_query_duration': 0.5,
            'cache_hit_rate': 80.0,
            'memory_usage': 85.0
        })
        
        # 3. 告警处理
        self.tracker.add_alert_callback(self._handle_alert)
        
        # 4. 定期清理
        self._start_cleanup_tasks()
    
    def _handle_alert(self, alert_data):
        """处理告警"""
        # 实现告警逻辑
        pass
    
    def _start_cleanup_tasks(self):
        """启动清理任务"""
        def cleanup():
            import time
            while True:
                # 清理旧的请求记录
                self.request_tracker.cleanup_old_requests(max_age=3600)
                time.sleep(300)  # 每5分钟清理一次
        
        import threading
        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()
```

### 2. 性能优化建议

```python
# 性能优化装饰器组合
from functools import wraps

def optimize_and_monitor(cache_ttl=300, alert_threshold=1.0):
    """优化和监控装饰器组合"""
    def decorator(func):
        # 首先应用缓存
        cached_func = cache_result(ttl=cache_ttl)(func)
        
        # 然后应用性能监控
        monitored_func = advanced_performance_monitor(
            metric_prefix=func.__name__,
            include_memory=True
        )(cached_func)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 添加自定义阈值检查
            start_time = time.time()
            try:
                result = monitored_func(*args, **kwargs)
                duration = time.time() - start_time
                
                if duration > alert_threshold:
                    track_performance(f"{func.__name__}_slow", 1, "count", {
                        "duration": duration,
                        "threshold": alert_threshold
                    })
                
                return result
            except Exception as e:
                track_performance(f"{func.__name__}_exception", 1, "count", {
                    "exception_type": type(e).__name__
                })
                raise
        
        return wrapper
    return decorator

# 使用示例
@optimize_and_monitor(cache_ttl=600, alert_threshold=0.5)
def expensive_computation(n):
    """耗时计算"""
    import time
    time.sleep(n * 0.1)
    return sum(range(n))
```

### 3. 监控仪表板

```python
def create_monitoring_dashboard():
    """创建监控仪表板数据"""
    tracker = get_performance_tracker()
    request_tracker = get_request_tracker()
    
    # 收集关键指标
    dashboard_data = {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "cpu_usage": tracker.get_statistics("cpu_usage", timedelta(minutes=5)),
            "memory_usage": tracker.get_statistics("memory_usage", timedelta(minutes=5)),
            "disk_io": tracker.get_statistics("disk_read_mb", timedelta(minutes=5))
        },
        "application": {
            "response_time": tracker.get_statistics("api_response_time", timedelta(minutes=5)),
            "error_rate": len([m for m in tracker.metrics if 'error' in m.name]),
            "request_count": len([m for m in tracker.metrics if 'request' in m.name])
        },
        "requests": {
            "active_requests": len([r for r in request_tracker.requests.values() if r['status'] == 'running']),
            "slow_requests": len(request_tracker.get_slow_requests(threshold=1.0)),
            "total_requests": len(request_tracker.requests)
        }
    }
    
    return dashboard_data

# 定期生成仪表板数据
def dashboard_updater():
    """仪表板数据更新器"""
    while True:
        dashboard_data = create_monitoring_dashboard()
        
        # 保存到文件或发送到监控系统
        with open('/tmp/monitoring_dashboard.json', 'w') as f:
            json.dump(dashboard_data, f, indent=2, default=str)
        
        time.sleep(30)  # 每30秒更新一次

# 启动仪表板更新
dashboard_thread = threading.Thread(target=dashboard_updater, daemon=True)
dashboard_thread.start()
```

### 4. 生产环境配置

```python
# 生产环境性能监控配置
def setup_production_monitoring():
    """生产环境监控配置"""
    tracker = get_performance_tracker()
    
    # 1. 调整采样频率
    tracker.sampling_interval = 5.0  # 5秒采样一次
    
    # 2. 设置生产环境阈值
    tracker.thresholds.update({
        'cpu_usage': 90.0,        # 更高的CPU阈值
        'memory_usage': 90.0,     # 更高的内存阈值
        'response_time': 2.0,     # 较宽松的响应时间
        'error_rate': 1.0,        # 较严格的错误率
    })
    
    # 3. 集成外部监控系统
    def prometheus_exporter(alert_data):
        """Prometheus指标导出"""
        # 集成Prometheus
        pass
    
    def datadog_exporter(alert_data):
        """Datadog指标导出"""
        # 集成Datadog
        pass
    
    tracker.add_alert_callback(prometheus_exporter)
    tracker.add_alert_callback(datadog_exporter)
    
    # 4. 启动监控
    tracker.start_monitoring()
    
    print("✅ 生产环境性能监控已启动")

# 在应用启动时调用
if os.getenv('ENV') == 'production':
    setup_production_monitoring()
```

## 总结

高级性能监控功能提供了：

1. **全面监控**: 系统指标、应用指标、请求追踪
2. **智能告警**: 阈值检测、自定义规则、多级告警
3. **深度分析**: 统计分析、趋势分析、内存分析
4. **易于集成**: 装饰器、中间件、自动化配置
5. **灵活导出**: JSON、CSV、自定义报告格式

通过合理使用这些功能，可以实现对应用性能的全面监控和优化。