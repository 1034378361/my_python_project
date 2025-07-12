# 最佳实践指南

本文档提供了使用My Python Project开发时的最佳实践建议。

## 目录

1. [代码组织](#代码组织)
2. [配置管理](#配置管理)
3. [日志记录](#日志记录)
4. [错误处理](#错误处理)
5. [性能优化](#性能优化)
6. [测试策略](#测试策略)
7. [安全考虑](#安全考虑)
8. [部署实践](#部署实践)
9. [监控和观测](#监控和观测)
10. [代码质量](#代码质量)

## 代码组织

### 项目结构最佳实践

```
project/
├── src/
│   └── your_project/
│       ├── __init__.py          # 模块导入
│       ├── core/                # 核心业务逻辑
│       ├── api/                 # API接口
│       ├── services/            # 业务服务
│       ├── models/              # 数据模型
│       ├── utils/               # 工具函数
│       └── config/              # 配置模块
├── tests/                       # 测试代码
├── docs/                        # 文档
├── scripts/                     # 脚本文件
└── config/                      # 配置文件
```

### 模块导入最佳实践

```python
# ✅ 推荐：使用绝对导入
from my_python_project.utils import ConfigManager
from my_python_project.services.user import UserService

# ✅ 推荐：导入整个模块
from my_python_project import utils
config = utils.ConfigManager()

# ❌ 避免：过度使用相对导入
from ..utils import ConfigManager  # 在深层嵌套时难以维护

# ✅ 推荐：在__init__.py中组织导出
# src/your_project/__init__.py
from .utils.config_manager import ConfigManager
from .utils.logging_utils import get_project_logger
from .services.user import UserService

__all__ = ['ConfigManager', 'get_project_logger', 'UserService']
```

### 函数和类设计

```python
# ✅ 推荐：单一职责原则
class UserValidator:
    """专门负责用户数据验证"""
    
    def validate_email(self, email: str) -> bool:
        """验证邮箱格式"""
        pass
    
    def validate_password(self, password: str) -> bool:
        """验证密码强度"""
        pass

# ✅ 推荐：依赖注入
class UserService:
    def __init__(self, validator: UserValidator, logger: Logger):
        self.validator = validator
        self.logger = logger
    
    def create_user(self, user_data: dict):
        if self.validator.validate_email(user_data['email']):
            self.logger.info("用户创建成功")
            return True
        return False

# ✅ 推荐：类型提示
from typing import Optional, List, Dict

def process_users(users: List[Dict[str, str]]) -> Optional[List[str]]:
    """处理用户列表并返回用户名列表"""
    if not users:
        return None
    return [user['name'] for user in users]
```

## 配置管理

### 环境配置分离

```python
from my_python_project import ConfigManager
import os

# ✅ 推荐：分环境配置
def setup_config() -> ConfigManager:
    config = ConfigManager()
    
    env = os.getenv('APP_ENV', 'development')
    config_files = {
        'development': 'config/dev.yaml',
        'testing': 'config/test.yaml',
        'production': 'config/prod.yaml'
    }
    
    config.load_from_file(config_files[env])
    
    # 环境变量覆盖
    config.set('database.password', os.getenv('DB_PASSWORD'))
    config.set('api.secret_key', os.getenv('API_SECRET_KEY'))
    
    return config
```

### 配置验证

```python
from my_python_project import StringValidator, NumberValidator

# ✅ 推荐：验证配置
def validate_config(config: ConfigManager) -> bool:
    """验证配置的有效性"""
    validators = {
        'database.host': StringValidator(min_length=1),
        'database.port': NumberValidator(min_value=1, max_value=65535),
        'api.timeout': NumberValidator(min_value=1, max_value=300),
    }
    
    for key, validator in validators.items():
        value = config.get(key)
        if not validator.validate(value):
            raise ValueError(f"配置项 {key} 验证失败: {value}")
    
    return True
```

### 敏感信息处理

```python
# ✅ 推荐：敏感信息处理
class SecureConfig:
    def __init__(self, config: ConfigManager):
        self.config = config
    
    def get_database_url(self) -> str:
        """安全获取数据库URL"""
        host = self.config.get('database.host')
        port = self.config.get('database.port')
        name = self.config.get('database.name')
        user = self.config.get('database.user')
        password = os.getenv('DB_PASSWORD')  # 从环境变量获取
        
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"
    
    def mask_sensitive_config(self) -> dict:
        """返回脱敏后的配置用于日志"""
        config_dict = self.config.to_dict()
        
        # 脱敏敏感字段
        sensitive_keys = ['password', 'secret', 'key', 'token']
        for key in config_dict:
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                config_dict[key] = "***"
        
        return config_dict
```

## 日志记录

### 结构化日志

```python
from my_python_project import get_project_logger

logger = get_project_logger(__name__)

# ✅ 推荐：结构化日志
def process_order(order_id: str, user_id: str, amount: float):
    """处理订单"""
    logger.info("开始处理订单", extra={
        'order_id': order_id,
        'user_id': user_id,
        'amount': amount,
        'operation': 'process_order',
        'stage': 'start'
    })
    
    try:
        # 业务逻辑
        logger.info("订单验证通过", extra={
            'order_id': order_id,
            'operation': 'process_order',
            'stage': 'validation'
        })
        
        logger.info("订单处理成功", extra={
            'order_id': order_id,
            'user_id': user_id,
            'amount': amount,
            'operation': 'process_order',
            'stage': 'success'
        })
        
    except Exception as e:
        logger.error("订单处理失败", extra={
            'order_id': order_id,
            'user_id': user_id,
            'error': str(e),
            'operation': 'process_order',
            'stage': 'error'
        })
        raise
```

### 日志级别使用

```python
# ✅ 推荐：正确使用日志级别
class DataProcessor:
    def __init__(self):
        self.logger = get_project_logger(self.__class__.__name__)
    
    def process_data(self, data):
        # DEBUG: 详细的调试信息
        self.logger.debug(f"开始处理数据，大小: {len(data)}")
        
        # INFO: 一般信息
        self.logger.info("数据处理开始")
        
        # WARNING: 潜在问题
        if len(data) > 10000:
            self.logger.warning(f"数据量较大: {len(data)}，可能影响性能")
        
        # ERROR: 错误情况
        try:
            result = self._do_process(data)
        except Exception as e:
            self.logger.error(f"数据处理失败: {e}")
            raise
        
        # INFO: 处理完成
        self.logger.info(f"数据处理完成，结果数量: {len(result)}")
        return result
```

### 日志性能优化

```python
# ✅ 推荐：日志性能优化
class OptimizedLogger:
    def __init__(self):
        self.logger = get_project_logger(self.__class__.__name__)
    
    def log_expensive_data(self, data):
        # 只在DEBUG级别时计算昂贵的日志内容
        if self.logger.isEnabledFor(logging.DEBUG):
            expensive_info = self._calculate_expensive_info(data)
            self.logger.debug(f"详细信息: {expensive_info}")
    
    def log_with_context(self, message, **kwargs):
        # 使用extra传递上下文，避免字符串拼接
        self.logger.info(message, extra=kwargs)
```

## 错误处理

### 分层错误处理

```python
from my_python_project import handle_exceptions, BaseError

# ✅ 推荐：定义业务异常
class UserNotFoundError(BaseError):
    """用户不存在异常"""
    pass

class InvalidUserDataError(BaseError):
    """无效用户数据异常"""
    pass

# ✅ 推荐：分层错误处理
class UserRepository:
    """数据访问层"""
    
    def get_user(self, user_id: str):
        try:
            # 数据库查询
            user = database.query(f"SELECT * FROM users WHERE id = {user_id}")
            if not user:
                raise UserNotFoundError(f"用户不存在: {user_id}")
            return user
        except DatabaseError as e:
            # 转换数据库异常为业务异常
            raise BaseError(f"数据库错误: {e}") from e

class UserService:
    """业务逻辑层"""
    
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    @handle_exceptions(UserNotFoundError, default_return=None)
    def get_user_profile(self, user_id: str):
        """获取用户资料"""
        user = self.repository.get_user(user_id)
        return self._build_profile(user)

class UserController:
    """控制器层"""
    
    def __init__(self, service: UserService):
        self.service = service
    
    def get_user_endpoint(self, user_id: str):
        """API端点"""
        try:
            profile = self.service.get_user_profile(user_id)
            if profile is None:
                return {"error": "用户不存在"}, 404
            return {"user": profile}, 200
        except BaseError as e:
            logger.error(f"获取用户失败: {e}")
            return {"error": "服务内部错误"}, 500
```

### 重试和熔断

```python
from my_python_project import retry_on_exception, CircuitBreaker

# ✅ 推荐：外部服务调用保护
class ExternalAPIClient:
    def __init__(self):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            timeout=60
        )
    
    @retry_on_exception(max_retries=3, delay=1.0, backoff=2.0)
    def call_api(self, endpoint: str, data: dict):
        """调用外部API"""
        return self.circuit_breaker.call(
            lambda: self._make_request(endpoint, data)
        )
    
    def _make_request(self, endpoint: str, data: dict):
        # 实际的HTTP请求
        response = requests.post(endpoint, json=data, timeout=10)
        if response.status_code >= 500:
            raise Exception(f"服务器错误: {response.status_code}")
        return response.json()
```

## 性能优化

### 缓存策略

```python
from my_python_project import MemoryCache, FileCache, cache_result

# ✅ 推荐：分层缓存策略
class CacheStrategy:
    def __init__(self):
        # 热数据：内存缓存
        self.hot_cache = MemoryCache(max_size=1000)
        # 温数据：文件缓存
        self.warm_cache = FileCache(cache_dir='./cache')
    
    @cache_result(cache="auto", ttl=300)  # 5分钟
    def get_user_frequently(self, user_id: str):
        """频繁访问的用户数据"""
        return self._fetch_user_from_db(user_id)
    
    @cache_result(cache="file", ttl=3600)  # 1小时
    def get_user_profile(self, user_id: str):
        """用户资料数据"""
        return self._build_user_profile(user_id)
    
    @cache_result(cache="memory", ttl=86400)  # 24小时
    def get_system_config(self):
        """系统配置数据"""
        return self._load_system_config()
```

### 数据库优化

```python
# ✅ 推荐：数据库查询优化
class OptimizedUserRepository:
    def __init__(self, db_pool):
        self.db_pool = db_pool
    
    async def get_users_batch(self, user_ids: List[str]) -> List[dict]:
        """批量获取用户"""
        # 批量查询减少数据库往返
        query = "SELECT * FROM users WHERE id IN %s"
        async with self.db_pool.acquire() as conn:
            return await conn.fetch(query, (tuple(user_ids),))
    
    async def get_user_with_profile(self, user_id: str) -> dict:
        """获取用户及资料"""
        # 使用JOIN减少查询次数
        query = """
        SELECT u.*, p.avatar, p.bio 
        FROM users u 
        LEFT JOIN profiles p ON u.id = p.user_id 
        WHERE u.id = $1
        """
        async with self.db_pool.acquire() as conn:
            return await conn.fetchrow(query, user_id)
```

### 异步处理

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# ✅ 推荐：异步处理
class AsyncTaskProcessor:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def process_multiple_tasks(self, tasks: List[callable]):
        """并发处理多个任务"""
        # CPU密集型任务使用线程池
        cpu_tasks = [task for task in tasks if task.is_cpu_intensive]
        cpu_results = await asyncio.gather(*[
            asyncio.get_event_loop().run_in_executor(
                self.executor, task.execute
            ) for task in cpu_tasks
        ])
        
        # I/O密集型任务使用异步
        io_tasks = [task for task in tasks if not task.is_cpu_intensive]
        io_results = await asyncio.gather(*[
            task.execute_async() for task in io_tasks
        ])
        
        return cpu_results + io_results
    
    async def batch_process_with_limit(self, items, batch_size=100):
        """分批处理大量数据"""
        semaphore = asyncio.Semaphore(10)  # 限制并发数
        
        async def process_item(item):
            async with semaphore:
                return await self._process_single_item(item)
        
        # 分批处理
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = await asyncio.gather(*[
                process_item(item) for item in batch
            ])
            results.extend(batch_results)
        
        return results
```

## 测试策略

### 测试分层

```python
import pytest
from unittest.mock import Mock, patch

# ✅ 推荐：单元测试
class TestUserService:
    def setup_method(self):
        self.mock_repository = Mock()
        self.service = UserService(self.mock_repository)
    
    def test_get_user_success(self):
        """测试成功获取用户"""
        # Arrange
        user_data = {"id": "123", "name": "测试用户"}
        self.mock_repository.get_user.return_value = user_data
        
        # Act
        result = self.service.get_user_profile("123")
        
        # Assert
        assert result["name"] == "测试用户"
        self.mock_repository.get_user.assert_called_once_with("123")
    
    def test_get_user_not_found(self):
        """测试用户不存在"""
        # Arrange
        self.mock_repository.get_user.side_effect = UserNotFoundError()
        
        # Act & Assert
        with pytest.raises(UserNotFoundError):
            self.service.get_user_profile("nonexistent")

# ✅ 推荐：集成测试
class TestUserIntegration:
    def setup_method(self):
        self.client = TestClient(app)
    
    def test_user_crud_workflow(self):
        """测试用户CRUD工作流"""
        # 创建用户
        user_data = {"name": "测试用户", "email": "test@example.com"}
        response = self.client.post("/users", json=user_data)
        assert response.status_code == 201
        user_id = response.json()["id"]
        
        # 获取用户
        response = self.client.get(f"/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "测试用户"
        
        # 更新用户
        update_data = {"name": "更新用户"}
        response = self.client.put(f"/users/{user_id}", json=update_data)
        assert response.status_code == 200
        
        # 删除用户
        response = self.client.delete(f"/users/{user_id}")
        assert response.status_code == 204
```

### 测试数据管理

```python
# ✅ 推荐：测试数据工厂
class TestDataFactory:
    @staticmethod
    def create_user(**kwargs):
        """创建测试用户数据"""
        default_data = {
            "id": "test-user-123",
            "name": "测试用户",
            "email": "test@example.com",
            "age": 25
        }
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def create_order(**kwargs):
        """创建测试订单数据"""
        default_data = {
            "id": "test-order-123",
            "user_id": "test-user-123",
            "total": 99.99,
            "status": "pending"
        }
        default_data.update(kwargs)
        return default_data

# ✅ 推荐：测试夹具
@pytest.fixture
def test_database():
    """测试数据库夹具"""
    # 设置测试数据库
    db = create_test_database()
    yield db
    # 清理测试数据库
    cleanup_test_database(db)

@pytest.fixture
def sample_users():
    """示例用户数据"""
    return [
        TestDataFactory.create_user(name="用户1"),
        TestDataFactory.create_user(name="用户2", age=30),
        TestDataFactory.create_user(name="用户3", email="user3@example.com")
    ]
```

## 安全考虑

### 输入验证

```python
from my_python_project import StringValidator, EmailValidator

# ✅ 推荐：严格的输入验证
class UserInputValidator:
    def __init__(self):
        self.validators = {
            'username': StringValidator(
                min_length=3,
                max_length=50,
                pattern=r'^[a-zA-Z0-9_]+$'  # 只允许字母、数字、下划线
            ),
            'email': EmailValidator(),
            'password': StringValidator(
                min_length=8,
                pattern=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]'
            )
        }
    
    def validate_user_input(self, user_data: dict) -> bool:
        """验证用户输入"""
        for field, validator in self.validators.items():
            if field in user_data:
                if not validator.validate(user_data[field]):
                    raise ValidationError(f"字段 {field} 验证失败")
        return True
    
    def sanitize_input(self, text: str) -> str:
        """清理输入文本"""
        import html
        # HTML转义
        text = html.escape(text)
        # 移除SQL注入风险字符
        dangerous_chars = ["'", '"', ';', '--', '/*', '*/']
        for char in dangerous_chars:
            text = text.replace(char, '')
        return text.strip()
```

### 敏感数据保护

```python
import hashlib
import secrets
from cryptography.fernet import Fernet

# ✅ 推荐：密码安全处理
class PasswordSecurity:
    @staticmethod
    def hash_password(password: str) -> str:
        """安全哈希密码"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 迭代次数
        )
        return f"{salt}:{password_hash.hex()}"
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """验证密码"""
        try:
            salt, password_hash = hashed.split(':')
            computed_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return computed_hash.hex() == password_hash
        except ValueError:
            return False

# ✅ 推荐：数据加密
class DataEncryption:
    def __init__(self, key: bytes = None):
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """加密敏感数据"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """解密敏感数据"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

### API安全

```python
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
import jwt

# ✅ 推荐：API安全措施
class APISecurityMiddleware:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.security = HTTPBearer()
    
    def verify_token(self, token: str = Depends(HTTPBearer())):
        """验证JWT令牌"""
        try:
            payload = jwt.decode(
                token.credentials,
                self.secret_key,
                algorithms=["HS256"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="令牌已过期")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="无效令牌")
    
    def rate_limit(self, max_requests: int = 100):
        """速率限制装饰器"""
        def decorator(func):
            # 实现速率限制逻辑
            return func
        return decorator
```

## 部署实践

### 容器化部署

```dockerfile
# ✅ 推荐：多阶段Docker构建
FROM python:3.11-slim as builder

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 应用阶段
FROM python:3.11-slim

WORKDIR /app

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 复制依赖
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# 复制应用代码
COPY . .

# 设置权限
RUN chown -R appuser:appuser /app
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "my_python_project.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 环境配置

```yaml
# ✅ 推荐：docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
      - DB_PASSWORD=${DB_PASSWORD}
      - API_SECRET_KEY=${API_SECRET_KEY}
    depends_on:
      - redis
      - postgres
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

## 监控和观测

### 应用监控

```python
from my_python_project import PerformanceMonitor
import time

# ✅ 推荐：业务指标监控
class BusinessMetrics:
    def __init__(self):
        self.monitor = PerformanceMonitor()
    
    def track_user_action(self, action: str, user_id: str):
        """跟踪用户行为"""
        with self.monitor.measure(f"user_action_{action}"):
            self.monitor.increment(f"user_actions_{action}")
            self.monitor.set_gauge(f"active_user_{user_id}", 1)
    
    def track_business_event(self, event: str, value: float = 1):
        """跟踪业务事件"""
        self.monitor.increment(f"business_event_{event}", value)
        self.monitor.histogram(f"business_value_{event}", value)
    
    def get_health_metrics(self) -> dict:
        """获取健康指标"""
        return {
            "response_time_p95": self.monitor.get_percentile("response_time", 95),
            "error_rate": self.monitor.get_rate("errors"),
            "active_users": self.monitor.get_gauge("active_users"),
            "throughput": self.monitor.get_rate("requests")
        }
```

### 日志聚合

```python
# ✅ 推荐：结构化日志用于监控
class MonitoringLogger:
    def __init__(self):
        self.logger = get_project_logger("monitoring")
    
    def log_request(self, request_id: str, method: str, path: str, 
                   status_code: int, duration: float):
        """记录请求日志"""
        self.logger.info("request_completed", extra={
            "request_id": request_id,
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration * 1000,
            "metric_type": "request"
        })
    
    def log_error(self, error: Exception, context: dict):
        """记录错误日志"""
        self.logger.error("error_occurred", extra={
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "metric_type": "error"
        })
```

## 代码质量

### 代码风格

```python
# ✅ 推荐：使用类型提示
from typing import List, Dict, Optional, Union
from dataclasses import dataclass

@dataclass
class User:
    """用户数据类"""
    id: str
    name: str
    email: str
    age: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Union[str, int]]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "age": self.age
        }

# ✅ 推荐：文档字符串
def calculate_user_score(user: User, activities: List[Dict]) -> float:
    """
    计算用户评分
    
    Args:
        user: 用户对象
        activities: 用户活动列表
        
    Returns:
        用户评分（0-100）
        
    Raises:
        ValueError: 当活动数据无效时
        
    Example:
        >>> user = User("123", "张三", "test@example.com")
        >>> activities = [{"type": "login", "score": 10}]
        >>> score = calculate_user_score(user, activities)
        >>> print(score)
        10.0
    """
    if not activities:
        return 0.0
    
    total_score = sum(activity.get("score", 0) for activity in activities)
    return min(total_score, 100.0)
```

### 代码检查

```python
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-docstrings]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

## 总结

这些最佳实践涵盖了使用My Python Project进行开发的各个方面：

1. **代码组织**: 清晰的项目结构和模块设计
2. **配置管理**: 安全和灵活的配置处理
3. **日志记录**: 结构化和有意义的日志
4. **错误处理**: 分层和优雅的错误处理
5. **性能优化**: 缓存、异步和数据库优化
6. **测试策略**: 全面和可维护的测试
7. **安全考虑**: 输入验证和数据保护
8. **部署实践**: 容器化和环境管理
9. **监控观测**: 应用和业务指标监控
10. **代码质量**: 规范和工具化的代码质量控制

遵循这些最佳实践将帮助您构建高质量、可维护和可扩展的应用程序。