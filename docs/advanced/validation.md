# 数据验证系统

数据验证系统提供了全面的数据验证功能，包括类型验证、格式验证、业务规则验证等，支持复杂的验证逻辑组合。

## 功能特性

- **类型验证**: 字符串、数字、列表、字典等类型验证
- **格式验证**: 邮箱、URL、日期、JSON、文件路径等格式验证
- **业务规则**: 长度、范围、模式、选择等业务规则验证
- **复合验证**: 链式验证、条件验证等复合验证器
- **装饰器支持**: 函数参数和返回值验证装饰器
- **错误处理**: 详细的验证错误信息

## 基础验证器

### 字符串验证

```python
from my_python_project.utils.validators import StringValidator

# 基础字符串验证
validator = StringValidator()
result = validator.validate("hello", "name")  # "hello"

# 长度限制
validator = StringValidator(min_length=3, max_length=10)
result = validator.validate("hello", "name")  # "hello"

# 模式匹配
validator = StringValidator(pattern=r"^\d{3}-\d{4}$")
result = validator.validate("123-4567", "phone")  # "123-4567"

# 选择限制
validator = StringValidator(choices=["red", "green", "blue"])
result = validator.validate("red", "color")  # "red"

# 自动去除空格
validator = StringValidator(strip=True)
result = validator.validate("  hello  ", "name")  # "hello"
```

### 数字验证

```python
from my_python_project.utils.validators import NumberValidator
from decimal import Decimal

# 整数验证
validator = NumberValidator(number_type=int)
result = validator.validate("42", "age")  # 42

# 浮点数验证
validator = NumberValidator(number_type=float)
result = validator.validate("3.14", "price")  # 3.14

# Decimal验证
validator = NumberValidator(number_type=Decimal)
result = validator.validate("99.99", "amount")  # Decimal('99.99')

# 范围限制
validator = NumberValidator(
    number_type=int,
    min_value=0,
    max_value=100
)
result = validator.validate("85", "score")  # 85
```

### 列表验证

```python
from my_python_project.utils.validators import ListValidator, StringValidator

# 基础列表验证
validator = ListValidator()
result = validator.validate([1, 2, 3], "numbers")  # [1, 2, 3]

# 长度限制
validator = ListValidator(min_length=2, max_length=5)
result = validator.validate([1, 2, 3], "items")  # [1, 2, 3]

# 唯一性验证
validator = ListValidator(unique=True)
result = validator.validate([1, 2, 3], "unique_items")  # [1, 2, 3]

# 项目验证
item_validator = StringValidator(min_length=2)
validator = ListValidator(item_validator=item_validator)
result = validator.validate(["ab", "cd"], "tags")  # ["ab", "cd"]
```

### 字典验证

```python
from my_python_project.utils.validators import DictValidator, StringValidator, NumberValidator

# 定义schema
schema = {
    "name": StringValidator(min_length=2),
    "age": NumberValidator(number_type=int, min_value=0),
    "email": StringValidator(pattern=r".+@.+\..+")
}

validator = DictValidator(schema=schema)

# 验证数据
data = {
    "name": "John",
    "age": 30,
    "email": "john@example.com"
}

result = validator.validate(data, "user")
# {'name': 'John', 'age': 30, 'email': 'john@example.com'}

# 允许额外字段
validator = DictValidator(schema=schema, allow_extra=True)
data_with_extra = {
    "name": "John",
    "age": 30,
    "email": "john@example.com",
    "city": "New York"  # 额外字段
}
result = validator.validate(data_with_extra, "user")
```

## 特殊格式验证器

### 邮箱验证

```python
from my_python_project.utils.validators import EmailValidator

validator = EmailValidator()
result = validator.validate("user@example.com", "email")  # "user@example.com"
result = validator.validate("USER@EXAMPLE.COM", "email")  # "user@example.com" (转为小写)
```

### URL验证

```python
from my_python_project.utils.validators import URLValidator

validator = URLValidator()
result = validator.validate("https://example.com", "website")  # "https://example.com"
result = validator.validate("http://example.com/path", "url")  # "http://example.com/path"
```

### 日期验证

```python
from my_python_project.utils.validators import DateValidator
from datetime import date

# 默认格式
validator = DateValidator()
result = validator.validate("2023-01-01", "birthday")  # date(2023, 1, 1)

# 自定义格式
validator = DateValidator(date_format="%d/%m/%Y")
result = validator.validate("01/01/2023", "date")  # date(2023, 1, 1)

# 日期范围
validator = DateValidator(
    min_date=date(2020, 1, 1),
    max_date=date(2030, 12, 31)
)
result = validator.validate("2023-06-15", "date")  # date(2023, 6, 15)
```

### JSON验证

```python
from my_python_project.utils.validators import JSONValidator, DictValidator

# 基础JSON验证
validator = JSONValidator()
result = validator.validate('{"key": "value"}', "config")  # {"key": "value"}

# 带schema的JSON验证
schema_validator = DictValidator(schema={"key": StringValidator()})
validator = JSONValidator(schema_validator=schema_validator)
result = validator.validate('{"key": "value"}', "config")  # {"key": "value"}
```

### 文件路径验证

```python
from my_python_project.utils.validators import FilePathValidator

# 基础路径验证
validator = FilePathValidator()
result = validator.validate("/tmp/file.txt", "path")  # Path("/tmp/file.txt")

# 文件必须存在
validator = FilePathValidator(must_exist=True)
result = validator.validate("existing_file.txt", "path")

# 允许的扩展名
validator = FilePathValidator(allowed_extensions=[".txt", ".json"])
result = validator.validate("config.json", "path")  # Path("config.json")
```

## 复合验证器

### 链式验证器

```python
from my_python_project.utils.validators import ChainValidator, StringValidator

# 多个验证器依次执行
validators = [
    StringValidator(strip=True),           # 先去空格
    StringValidator(min_length=3),         # 然后检查长度
    StringValidator(pattern=r"^[a-zA-Z]+$")  # 最后检查模式
]

validator = ChainValidator(validators)
result = validator.validate("  hello  ", "name")  # "hello"
```

### 条件验证器

```python
from my_python_project.utils.validators import ConditionalValidator, NumberValidator

def is_positive(value):
    return value > 0

# 根据条件选择验证器
validator = ConditionalValidator(
    condition=is_positive,
    true_validator=NumberValidator(number_type=int, min_value=1),
    false_validator=NumberValidator(number_type=int, max_value=0)
)

result = validator.validate(5, "number")   # 5 (使用positive验证器)
result = validator.validate(-5, "number")  # -5 (使用negative验证器)
```

## 验证装饰器

### 输入验证装饰器

```python
from my_python_project.utils.validators import validate_input, StringValidator, NumberValidator

@validate_input(
    name=StringValidator(min_length=2),
    age=NumberValidator(number_type=int, min_value=0)
)
def create_user(name, age):
    return f"User: {name}, Age: {age}"

# 正确调用
result = create_user(name="John", age=30)  # "User: John, Age: 30"

# 错误调用会抛出ValidationError
try:
    create_user(name="J", age=30)  # 名字太短
except ValidationError as e:
    print(e)
```

### 返回值验证装饰器

```python
from my_python_project.utils.validators import validate_return, StringValidator

@validate_return(StringValidator(min_length=5))
def get_greeting(name):
    return f"Hello {name}"

result = get_greeting("World")  # "Hello World"

# 返回值验证失败会抛出ValidationError
@validate_return(StringValidator(min_length=20))
def get_short_greeting():
    return "Hi"

try:
    get_short_greeting()
except ValidationError as e:
    print(e)
```

## 工具函数

### 数据验证函数

```python
from my_python_project.utils.validators import validate_data

# 定义验证schema
schema = {
    "username": StringValidator(min_length=3, max_length=20),
    "email": EmailValidator(),
    "age": NumberValidator(number_type=int, min_value=0, max_value=150)
}

# 验证数据
data = {
    "username": "john_doe",
    "email": "john@example.com",
    "age": 30
}

try:
    validated_data = validate_data(data, schema)
    print(validated_data)
except ValidationError as e:
    print(f"验证失败: {e}")
```

### 从类型创建验证器

```python
from my_python_project.utils.validators import create_validator_from_type
from typing import List, Optional

# 从类型提示创建验证器
validator = create_validator_from_type(str)
validator = create_validator_from_type(int)
validator = create_validator_from_type(List[str])
validator = create_validator_from_type(Optional[str])
```

## 预构建验证器

```python
from my_python_project.utils.validators import (
    string_validator, int_validator, float_validator, bool_validator,
    email_validator, url_validator, date_validator,
    optional_string, optional_int, non_empty_string, positive_int, percentage
)

# 使用预构建验证器
name = string_validator.validate("John", "name")
age = int_validator.validate("30", "age")
email = email_validator.validate("user@example.com", "email")
score = percentage.validate("85.5", "score")  # 0-100范围的浮点数
```

## 错误处理

```python
from my_python_project import ValidationError

try:
    validator = StringValidator(min_length=5)
    result = validator.validate("Hi", "greeting")
except ValidationError as e:
    print(f"验证错误: {e}")
    print(f"错误字段: {e.details}")
```

## 复杂验证示例

### 用户注册验证

```python
from my_python_project.utils.validators import (
    DictValidator, StringValidator, EmailValidator, NumberValidator,
    ListValidator, validate_data
)

# 定义用户注册schema
user_schema = {
    "username": StringValidator(
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_]+$"
    ),
    "email": EmailValidator(),
    "password": StringValidator(min_length=8),
    "age": NumberValidator(
        number_type=int,
        min_value=13,
        max_value=120
    ),
    "interests": ListValidator(
        item_validator=StringValidator(min_length=2),
        min_length=1,
        max_length=10,
        unique=True
    ),
    "profile": DictValidator(
        schema={
            "bio": StringValidator(max_length=500, required=False),
            "location": StringValidator(max_length=100, required=False)
        },
        allow_extra=False
    )
}

# 验证用户数据
user_data = {
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password123",
    "age": 25,
    "interests": ["programming", "music", "travel"],
    "profile": {
        "bio": "Software developer",
        "location": "New York"
    }
}

try:
    validated_user = validate_data(user_data, user_schema)
    print("用户数据验证成功")
except ValidationError as e:
    print(f"验证失败: {e}")
```

### API参数验证

```python
from my_python_project.utils.validators import (
    validate_input, StringValidator, NumberValidator, ListValidator
)

@validate_input(
    query=StringValidator(min_length=1, max_length=100),
    page=NumberValidator(number_type=int, min_value=1, default=1),
    per_page=NumberValidator(number_type=int, min_value=1, max_value=100, default=20),
    sort_by=StringValidator(choices=["name", "date", "score"], default="name"),
    filters=ListValidator(
        item_validator=StringValidator(),
        required=False,
        default=[]
    )
)
def search_api(query, page=1, per_page=20, sort_by="name", filters=None):
    return {
        "query": query,
        "page": page,
        "per_page": per_page,
        "sort_by": sort_by,
        "filters": filters or []
    }

# 使用API
result = search_api(
    query="python",
    page=2,
    per_page=10,
    sort_by="date",
    filters=["language:python", "stars:>100"]
)
```

## 最佳实践

1. **组合使用**: 使用复合验证器组合简单验证器
2. **错误处理**: 提供清晰的错误信息和恢复机制
3. **性能考虑**: 对于大量数据，考虑批量验证
4. **默认值**: 为可选字段提供合理的默认值
5. **文档**: 为验证规则提供清晰的文档

## 自定义验证器

```python
from my_python_project.utils.validators import Validator
from my_python_project import ValidationError

class CustomValidator(Validator):
    def __init__(self, custom_rule, **kwargs):
        super().__init__(**kwargs)
        self.custom_rule = custom_rule
    
    def _validate_value(self, value, field_name):
        if not self.custom_rule(value):
            raise ValidationError(f"字段 '{field_name}' 不符合自定义规则")
        return value

# 使用自定义验证器
def is_even(value):
    return value % 2 == 0

validator = CustomValidator(custom_rule=is_even)
result = validator.validate(4, "number")  # 4
```