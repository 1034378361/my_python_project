# 缓存系统

缓存系统提供了多种缓存策略和后端，包括内存缓存、文件缓存、多层缓存等，支持TTL、LRU等策略。

## 功能特性

- **多种后端**: 内存缓存、文件缓存、Redis缓存、多层缓存
- **过期策略**: TTL（生存时间）、LRU（最近最少使用）
- **装饰器支持**: 函数结果缓存装饰器
- **线程安全**: 多线程环境下的安全操作
- **统计功能**: 缓存命中率、使用统计
- **序列化**: 支持多种序列化方式

## 内存缓存

### 基本使用

```python
from my_python_project.utils.cache import MemoryCache

# 创建内存缓存
cache = MemoryCache(max_size=1000, default_ttl=3600)

# 设置缓存
cache.set("user:123", {"name": "John", "age": 30})
cache.set("config", {"debug": True}, ttl=300)  # 5分钟过期

# 获取缓存
user = cache.get("user:123")
config = cache.get("config")

# 检查是否存在
if cache.exists("user:123"):
    print("用户数据已缓存")

# 删除缓存
cache.delete("user:123")

# 清空所有缓存
cache.clear()
```

### 容量和过期管理

```python
# 限制缓存大小，使用LRU策略
cache = MemoryCache(max_size=100)

# 设置默认TTL
cache = MemoryCache(default_ttl=3600)  # 1小时

# 获取所有键
keys = cache.keys()

# 检查缓存大小
print(f"缓存大小: {len(keys)}")
print(f"所有键: {keys}")
```

## 文件缓存

### 基本使用

```python
from my_python_project.utils.cache import FileCache

# 创建文件缓存
cache = FileCache(
    cache_dir="cache/",
    default_ttl=3600,
    serializer="pickle"  # 或 "json"
)

# 使用方式与内存缓存相同
cache.set("data", {"key": "value"})
data = cache.get("data")
```

### 持久化特性

```python
# 文件缓存在程序重启后仍然存在
cache1 = FileCache("cache/")
cache1.set("persistent_data", "This will survive restart")

# 程序重启后
cache2 = FileCache("cache/")
data = cache2.get("persistent_data")  # "This will survive restart"
```

## Redis缓存

### 基本使用

```python
import redis
from my_python_project.utils.cache import RedisCache

# 创建Redis客户端
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# 创建Redis缓存
cache = RedisCache(
    redis_client=redis_client,
    key_prefix="myapp:",
    default_ttl=3600,
    serializer="pickle"
)

# 使用方式与其他缓存相同
cache.set("user:123", {"name": "John"})
user = cache.get("user:123")
```

### 分布式缓存

```python
# Redis缓存支持分布式环境
# 多个应用实例可以共享同一个Redis缓存

# 使用键前缀避免冲突
app1_cache = RedisCache(redis_client, key_prefix="app1:")
app2_cache = RedisCache(redis_client, key_prefix="app2:")
```

## 多层缓存

### 缓存层次结构

```python
from my_python_project import MultiLevelCache, MemoryCache, FileCache

# 创建多层缓存（内存 + 文件）
memory_cache = MemoryCache(max_size=100)
file_cache = FileCache("cache/")

# 按优先级排序：内存缓存 -> 文件缓存
multi_cache = MultiLevelCache([memory_cache, file_cache])

# 设置缓存（存储在所有层级）
multi_cache.set("data", {"key": "value"})

# 获取缓存（从最快的层级获取）
data = multi_cache.get("data")  # 从内存缓存获取

# 如果内存缓存过期，会从文件缓存获取并回写到内存
```

### 故障恢复

```python
# 多层缓存具有容错能力
# 如果某一层缓存失败，会尝试其他层级

# 即使内存缓存失败，仍能从文件缓存获取数据
data = multi_cache.get("data")
```

## 缓存管理器

### 统一管理

```python
from my_python_project.utils.cache import CacheManager, MemoryCache, FileCache

# 创建缓存管理器
manager = CacheManager(default_backend=MemoryCache())

# 注册多个缓存后端
manager.register_backend("memory", MemoryCache())
manager.register_backend("file", FileCache("cache/"))

# 使用不同的缓存后端
manager.set("temp_data", "value")  # 使用默认后端
manager.set("persistent_data", "value", backend="file")  # 使用文件缓存

# 获取数据
temp_data = manager.get("temp_data")
persistent_data = manager.get("persistent_data", backend="file")
```

### 统计功能

```python
# 获取缓存管理器的后端信息
backends = manager.backends
print(f"可用后端: {list(backends.keys())}")

# 清除特定后端的缓存
for backend_name in backends:
    backends[backend_name].clear()
```

## 缓存装饰器

### 函数结果缓存

```python
from my_python_project.utils.cache import cache_result

@cache_result(ttl=300)  # 缓存5分钟
def expensive_function(x, y):
    # 耗时的计算
    import time
    time.sleep(2)
    return x + y

# 第一次调用会执行计算
result1 = expensive_function(1, 2)  # 耗时2秒，返回3

# 第二次调用使用缓存
result2 = expensive_function(1, 2)  # 立即返回3

# 不同参数会重新计算
result3 = expensive_function(2, 3)  # 耗时2秒，返回5
```

### 自定义缓存键

```python
def custom_key_func(user_id, include_profile=False):
    return f"user_data:{user_id}"

@cache_result(key_func=custom_key_func, ttl=600)
def get_user_data(user_id, include_profile=False):
    # 不管include_profile参数如何变化，都使用相同的缓存键
    return fetch_user_from_db(user_id)
```

### 限时缓存

```python
from my_python_project.utils.cache import timed_cache

@timed_cache(ttl=60)  # 1分钟过期
def get_current_time():
    import datetime
    return datetime.datetime.now()

# 在1分钟内多次调用返回相同时间
time1 = get_current_time()
time2 = get_current_time()  # 与time1相同
```

### LRU缓存

```python
from my_python_project.utils.cache import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# 使用LRU策略，最多缓存128个结果
result = fibonacci(10)
```

## 全局缓存管理

### 全局缓存实例

```python
from my_python_project.utils.cache import init_cache_manager, get_cache_manager

# 初始化全局缓存管理器
cache_manager = init_cache_manager(
    default_backend=MemoryCache(max_size=1000)
)

# 在应用的任何地方使用全局缓存
def some_function():
    manager = get_cache_manager()
    manager.set("global_data", "value")
    return manager.get("global_data")
```

## 高级用法

### 缓存穿透保护

```python
from my_python_project.utils.cache import cache_result

@cache_result(ttl=300)
def get_user_by_id(user_id):
    user = db.get_user(user_id)
    if user is None:
        # 缓存空结果以防止缓存穿透
        return {"_not_found": True}
    return user

def safe_get_user(user_id):
    result = get_user_by_id(user_id)
    if result.get("_not_found"):
        return None
    return result
```

### 缓存预热

```python
def warm_up_cache():
    """预热缓存"""
    cache = get_cache_manager()
    
    # 预加载常用数据
    for user_id in get_active_user_ids():
        user_data = fetch_user_from_db(user_id)
        cache.set(f"user:{user_id}", user_data, ttl=3600)
    
    # 预加载配置数据
    config = fetch_config_from_db()
    cache.set("app_config", config, ttl=7200)
```

### 缓存失效策略

```python
def update_user(user_id, data):
    # 更新数据库
    db.update_user(user_id, data)
    
    # 失效相关缓存
    cache = get_cache_manager()
    cache.delete(f"user:{user_id}")
    cache.delete(f"user_profile:{user_id}")
    cache.delete("user_list")  # 用户列表缓存也需要更新
```

## 错误处理

### 缓存故障处理

```python
from my_python_project import CacheError

try:
    cache = get_cache_manager()
    cache.set("key", "value")
except CacheError as e:
    print(f"缓存操作失败: {e}")
    # 继续正常流程，不依赖缓存
```

### 优雅降级

```python
def get_user_data(user_id):
    try:
        # 尝试从缓存获取
        cache = get_cache_manager()
        cached_data = cache.get(f"user:{user_id}")
        if cached_data:
            return cached_data
    except CacheError:
        # 缓存失败，记录日志但不影响功能
        logger.warning("缓存获取失败，从数据库获取")
    
    # 从数据库获取
    user_data = db.get_user(user_id)
    
    try:
        # 尝试缓存结果
        cache.set(f"user:{user_id}", user_data, ttl=3600)
    except CacheError:
        # 缓存设置失败，记录日志
        logger.warning("缓存设置失败")
    
    return user_data
```

## 性能优化

### 批量操作

```python
# 批量设置缓存
cache = get_cache_manager()
for user_id, user_data in users.items():
    cache.set(f"user:{user_id}", user_data)

# 批量获取（如果缓存支持）
user_keys = [f"user:{uid}" for uid in user_ids]
# 注意：不是所有缓存后端都支持批量操作
```

### 缓存分区

```python
# 使用不同的缓存后端存储不同类型的数据
manager = CacheManager()

# 热点数据使用内存缓存
manager.register_backend("hot", MemoryCache(max_size=1000))

# 大数据使用文件缓存
manager.register_backend("cold", FileCache("cache/"))

# 根据数据特性选择缓存后端
manager.set("user:123", user_data, backend="hot")
manager.set("report:456", large_report, backend="cold")
```

## 最佳实践

1. **选择合适的缓存策略**: 根据数据特性选择TTL、LRU等策略
2. **避免缓存穿透**: 缓存空结果或使用布隆过滤器
3. **监控缓存命中率**: 定期检查缓存效果
4. **合理设置过期时间**: 平衡数据新鲜度和性能
5. **故障恢复**: 缓存失败时有备用方案
6. **内存管理**: 控制缓存大小避免内存溢出

## 使用示例

### Web应用缓存

```python
from my_python_project.utils.cache import cache_result

@cache_result(ttl=300)
def get_article_list(category, page=1):
    return db.query_articles(category, page)

@cache_result(ttl=1800)
def get_user_profile(user_id):
    return db.get_user_profile(user_id)

# 在视图函数中使用
def article_list_view(request):
    category = request.GET.get('category', 'all')
    page = int(request.GET.get('page', 1))
    
    # 自动使用缓存
    articles = get_article_list(category, page)
    return render_template('articles.html', articles=articles)
```

### 数据库查询缓存

```python
class UserService:
    @cache_result(ttl=3600)
    def get_user_by_id(self, user_id):
        return db.session.query(User).get(user_id)
    
    @cache_result(ttl=1800)
    def get_user_permissions(self, user_id):
        return db.session.query(Permission).filter_by(user_id=user_id).all()
    
    def update_user(self, user_id, data):
        # 更新数据库
        user = db.session.query(User).get(user_id)
        user.update(data)
        db.session.commit()
        
        # 清除相关缓存
        cache = get_cache_manager()
        cache.delete(f"get_user_by_id:{user_id}")
        cache.delete(f"get_user_permissions:{user_id}")
```