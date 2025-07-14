# Web 应用示例

展示如何在 Web 应用中使用 My Python Project。

## 🌐 FastAPI 集成示例

```python
from fastapi import FastAPI, HTTPException, Depends
import time
from my_python_project import (
    get_project_logger,
    ConfigManager,
    StringValidator,
    EmailValidator,
    cache_result
)

# 初始化
app = FastAPI(title="My Python Project API")
logger = get_project_logger(__name__)
config = ConfigManager()

# 验证器
validators = {
    "name": StringValidator(min_length=2, max_length=50),
    "email": EmailValidator()
}

# 用户模型
class User:
    def __init__(self, id: int, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email

# 模拟数据库
users_db = []

@app.on_event("startup")
async def startup_event():
    """应用启动时的配置"""
    global config
    config = ConfigManager.from_file("api_config.yaml")
    logger.info("API服务启动", extra={
        "host": config.get("server.host", "localhost"),
        "port": config.get("server.port", 8000)
    })

@app.middleware("http")
async def logging_middleware(request, call_next):
    """请求日志中间件"""
    start_time = time.time()
    
    logger.info("请求开始", extra={
        "method": request.method,
        "path": request.url.path,
        "client": request.client.host
    })
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    logger.info("请求完成", extra={
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration": f"{duration:.3f}s"
    })
    
    return response

@cache_result(ttl=300)
def get_user_from_db(user_id: int):
    """从数据库获取用户（带缓存）"""
    logger.debug(f"查询用户: {user_id}")
    for user in users_db:
        if user.id == user_id:
            return user
    return None

@app.post("/users/")
async def create_user(name: str, email: str):
    """创建用户"""
    # 验证输入
    try:
        validators["name"].validate(name, "name")
        validators["email"].validate(email, "email")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"验证失败: {str(e)}")
    
    # 创建用户
    user_id = len(users_db) + 1
    user = User(user_id, name, email)
    users_db.append(user)
    
    logger.info("用户创建成功", extra={
        "user_id": user_id,
        "name": name,
        "email": email
    })
    
    return {"id": user_id, "name": name, "email": email}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """获取用户"""
    user = get_user_from_db(user_id)
    
    if not user:
        logger.warning(f"用户不存在: {user_id}")
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {"id": user.id, "name": user.name, "email": user.email}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "users_count": len(users_db),
        "config": {
            "debug": config.get("app.debug", False),
            "version": config.get("app.version", "1.0.0")
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    host = config.get("server.host", "localhost")
    port = config.get("server.port", 8000)
    
    uvicorn.run(app, host=host, port=port)
```

## 🔧 配置文件示例

创建 `api_config.yaml`：

```yaml
app:
  debug: true
  version: "1.0.0"
  name: "User API"

server:
  host: "0.0.0.0"
  port: 8000
  workers: 4

database:
  host: "localhost"
  port: 5432
  name: "userdb"

logging:
  level: "INFO"
  format: "json"
  
cache:
  ttl: 300
  max_size: 1000
```

## 🧪 测试示例

```python
from fastapi.testclient import TestClient
import pytest

client = TestClient(app)

def test_create_user():
    """测试创建用户"""
    response = client.post("/users/", json={
        "name": "张三",
        "email": "zhangsan@example.com"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "张三"
    assert data["email"] == "zhangsan@example.com"
    assert "id" in data

def test_get_user():
    """测试获取用户"""
    # 先创建用户
    create_response = client.post("/users/", json={
        "name": "李四",
        "email": "lisi@example.com"
    })
    user_id = create_response.json()["id"]
    
    # 获取用户
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "李四"
    assert data["email"] == "lisi@example.com"

def test_user_not_found():
    """测试用户不存在"""
    response = client.get("/users/999")
    assert response.status_code == 404

def test_invalid_email():
    """测试无效邮箱"""
    response = client.post("/users/", json={
        "name": "王五",
        "email": "invalid-email"
    })
    assert response.status_code == 400

def test_health_check():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "users_count" in data
```

## 📊 性能监控集成

```python
from my_python_project import PerformanceMonitor

# 添加性能监控
monitor = PerformanceMonitor()

@app.middleware("http")
async def performance_middleware(request, call_next):
    """性能监控中间件"""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    endpoint = f"{request.method}_{request.url.path}"
    
    # 记录性能数据
    monitor.record_timing(endpoint, duration)
    monitor.increment_counter("total_requests")
    
    if response.status_code >= 400:
        monitor.increment_counter("error_requests")
    
    return response

@app.get("/metrics")
async def get_metrics():
    """获取性能指标"""
    return {
        "performance": monitor.get_stats(),
        "total_requests": monitor._counters.get("total_requests", 0),
        "error_requests": monitor._counters.get("error_requests", 0)
    }
```

## 🚀 部署配置

### Docker 部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - APP_DEBUG=false
      - DB_HOST=postgres
    depends_on:
      - postgres
      - redis
    volumes:
      - ./api_config.yaml:/app/api_config.yaml
      
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: userdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7-alpine
    
volumes:
  postgres_data:
```

这个示例展示了如何在实际的 Web 应用中集成使用项目的各种功能，包括配置管理、日志记录、数据验证、缓存和性能监控。