"""
数据验证器

提供各种数据验证功能，包括类型验证、格式验证、业务规则验证等。
"""

import re
import json
from typing import Any, Dict, List, Optional, Union, Callable, Type, TypeVar, get_origin, get_args
from datetime import datetime, date
from decimal import Decimal
from functools import wraps
from pathlib import Path

from .exceptions import ValidationError

T = TypeVar('T')


# =============================================================================
# 基础验证器
# =============================================================================

class Validator:
    """基础验证器类"""
    
    def __init__(self, required: bool = True, allow_none: bool = False):
        """
        初始化验证器
        
        Args:
            required: 是否必需
            allow_none: 是否允许None值
        """
        self.required = required
        self.allow_none = allow_none
    
    def validate(self, value: Any, field_name: str = "value") -> Any:
        """
        验证值
        
        Args:
            value: 要验证的值
            field_name: 字段名称
            
        Returns:
            验证后的值
            
        Raises:
            ValidationError: 验证失败时抛出
        """
        # 检查必需性
        if value is None:
            if self.required and not self.allow_none:
                raise ValidationError(f"字段 '{field_name}' 是必需的")
            if self.allow_none:
                return None
        
        return self._validate_value(value, field_name)
    
    def _validate_value(self, value: Any, field_name: str) -> Any:
        """子类实现的具体验证逻辑"""
        return value
    
    def __call__(self, value: Any, field_name: str = "value") -> Any:
        """使验证器可调用"""
        return self.validate(value, field_name)


# =============================================================================
# 类型验证器
# =============================================================================

class TypeValidator(Validator):
    """类型验证器"""
    
    def __init__(self, expected_type: Type, **kwargs):
        """
        初始化类型验证器
        
        Args:
            expected_type: 期望的类型
            **kwargs: 传递给父类的参数
        """
        super().__init__(**kwargs)
        self.expected_type = expected_type
    
    def _validate_value(self, value: Any, field_name: str) -> Any:
        if not isinstance(value, self.expected_type):
            raise ValidationError(
                f"字段 '{field_name}' 期望类型 {self.expected_type.__name__}, "
                f"实际类型 {type(value).__name__}"
            )
        return value


class StringValidator(Validator):
    """字符串验证器"""
    
    def __init__(self, min_length: Optional[int] = None,
                 max_length: Optional[int] = None,
                 pattern: Optional[str] = None,
                 choices: Optional[List[str]] = None,
                 strip: bool = True,
                 **kwargs):
        """
        初始化字符串验证器
        
        Args:
            min_length: 最小长度
            max_length: 最大长度
            pattern: 正则表达式模式
            choices: 可选值列表
            strip: 是否去除首尾空格
            **kwargs: 传递给父类的参数
        """
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = re.compile(pattern) if pattern else None
        self.choices = choices
        self.strip = strip
    
    def _validate_value(self, value: Any, field_name: str) -> str:
        if not isinstance(value, str):
            try:
                value = str(value)
            except Exception:
                raise ValidationError(f"字段 '{field_name}' 无法转换为字符串")
        
        if self.strip:
            value = value.strip()
        
        # 长度验证
        if self.min_length is not None and len(value) < self.min_length:
            raise ValidationError(
                f"字段 '{field_name}' 长度不能少于 {self.min_length} 个字符"
            )
        
        if self.max_length is not None and len(value) > self.max_length:
            raise ValidationError(
                f"字段 '{field_name}' 长度不能超过 {self.max_length} 个字符"
            )
        
        # 模式验证
        if self.pattern and not self.pattern.match(value):
            raise ValidationError(f"字段 '{field_name}' 格式不正确")
        
        # 选择验证
        if self.choices and value not in self.choices:
            raise ValidationError(
                f"字段 '{field_name}' 必须是以下值之一: {', '.join(self.choices)}"
            )
        
        return value


class NumberValidator(Validator):
    """数字验证器"""
    
    def __init__(self, min_value: Optional[Union[int, float]] = None,
                 max_value: Optional[Union[int, float]] = None,
                 number_type: Type = float,
                 **kwargs):
        """
        初始化数字验证器
        
        Args:
            min_value: 最小值
            max_value: 最大值
            number_type: 数字类型 (int, float, Decimal)
            **kwargs: 传递给父类的参数
        """
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.number_type = number_type
    
    def _validate_value(self, value: Any, field_name: str) -> Union[int, float, Decimal]:
        try:
            if self.number_type == Decimal:
                value = Decimal(str(value))
            else:
                value = self.number_type(value)
        except (ValueError, TypeError):
            raise ValidationError(
                f"字段 '{field_name}' 无法转换为 {self.number_type.__name__}"
            )
        
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(
                f"字段 '{field_name}' 不能小于 {self.min_value}"
            )
        
        if self.max_value is not None and value > self.max_value:
            raise ValidationError(
                f"字段 '{field_name}' 不能大于 {self.max_value}"
            )
        
        return value


class ListValidator(Validator):
    """列表验证器"""
    
    def __init__(self, item_validator: Optional[Validator] = None,
                 min_length: Optional[int] = None,
                 max_length: Optional[int] = None,
                 unique: bool = False,
                 **kwargs):
        """
        初始化列表验证器
        
        Args:
            item_validator: 列表项验证器
            min_length: 最小长度
            max_length: 最大长度
            unique: 是否要求唯一
            **kwargs: 传递给父类的参数
        """
        super().__init__(**kwargs)
        self.item_validator = item_validator
        self.min_length = min_length
        self.max_length = max_length
        self.unique = unique
    
    def _validate_value(self, value: Any, field_name: str) -> List[Any]:
        if not isinstance(value, (list, tuple)):
            raise ValidationError(f"字段 '{field_name}' 必须是列表或元组")
        
        value = list(value)
        
        # 长度验证
        if self.min_length is not None and len(value) < self.min_length:
            raise ValidationError(
                f"字段 '{field_name}' 长度不能少于 {self.min_length}"
            )
        
        if self.max_length is not None and len(value) > self.max_length:
            raise ValidationError(
                f"字段 '{field_name}' 长度不能超过 {self.max_length}"
            )
        
        # 唯一性验证
        if self.unique and len(value) != len(set(value)):
            raise ValidationError(f"字段 '{field_name}' 中存在重复项")
        
        # 验证每一项
        if self.item_validator:
            validated_items = []
            for i, item in enumerate(value):
                try:
                    validated_item = self.item_validator.validate(
                        item, f"{field_name}[{i}]"
                    )
                    validated_items.append(validated_item)
                except ValidationError as e:
                    raise ValidationError(f"字段 '{field_name}' 索引 {i} 验证失败: {e}")
            return validated_items
        
        return value


class DictValidator(Validator):
    """字典验证器"""
    
    def __init__(self, schema: Optional[Dict[str, Validator]] = None,
                 allow_extra: bool = False,
                 **kwargs):
        """
        初始化字典验证器
        
        Args:
            schema: 字段验证器映射
            allow_extra: 是否允许额外字段
            **kwargs: 传递给父类的参数
        """
        super().__init__(**kwargs)
        self.schema = schema or {}
        self.allow_extra = allow_extra
    
    def _validate_value(self, value: Any, field_name: str) -> Dict[str, Any]:
        if not isinstance(value, dict):
            raise ValidationError(f"字段 '{field_name}' 必须是字典")
        
        validated_data = {}
        
        # 验证已定义的字段
        for key, validator in self.schema.items():
            field_value = value.get(key)
            try:
                validated_value = validator.validate(field_value, f"{field_name}.{key}")
                if validated_value is not None or validator.allow_none:
                    validated_data[key] = validated_value
            except ValidationError as e:
                raise ValidationError(f"字段 '{field_name}.{key}' 验证失败: {e}")
        
        # 处理额外字段
        if self.allow_extra:
            for key, value in value.items():
                if key not in self.schema:
                    validated_data[key] = value
        else:
            extra_keys = set(value.keys()) - set(self.schema.keys())
            if extra_keys:
                raise ValidationError(
                    f"字段 '{field_name}' 包含未定义的字段: {', '.join(extra_keys)}"
                )
        
        return validated_data


# =============================================================================
# 特殊格式验证器
# =============================================================================

class EmailValidator(Validator):
    """邮箱验证器"""
    
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    def _validate_value(self, value: Any, field_name: str) -> str:
        if not isinstance(value, str):
            raise ValidationError(f"字段 '{field_name}' 必须是字符串")
        
        if not self.EMAIL_PATTERN.match(value):
            raise ValidationError(f"字段 '{field_name}' 不是有效的邮箱地址")
        
        return value.lower()


class URLValidator(Validator):
    """URL验证器"""
    
    URL_PATTERN = re.compile(
        r'^https?://[^\s/$.?#].[^\s]*$',
        re.IGNORECASE
    )
    
    def _validate_value(self, value: Any, field_name: str) -> str:
        if not isinstance(value, str):
            raise ValidationError(f"字段 '{field_name}' 必须是字符串")
        
        if not self.URL_PATTERN.match(value):
            raise ValidationError(f"字段 '{field_name}' 不是有效的URL")
        
        return value


class DateValidator(Validator):
    """日期验证器"""
    
    def __init__(self, date_format: str = "%Y-%m-%d",
                 min_date: Optional[date] = None,
                 max_date: Optional[date] = None,
                 **kwargs):
        """
        初始化日期验证器
        
        Args:
            date_format: 日期格式
            min_date: 最小日期
            max_date: 最大日期
            **kwargs: 传递给父类的参数
        """
        super().__init__(**kwargs)
        self.date_format = date_format
        self.min_date = min_date
        self.max_date = max_date
    
    def _validate_value(self, value: Any, field_name: str) -> date:
        if isinstance(value, date):
            date_value = value
        elif isinstance(value, str):
            try:
                date_value = datetime.strptime(value, self.date_format).date()
            except ValueError:
                raise ValidationError(
                    f"字段 '{field_name}' 日期格式不正确，期望格式: {self.date_format}"
                )
        else:
            raise ValidationError(f"字段 '{field_name}' 必须是日期或日期字符串")
        
        if self.min_date and date_value < self.min_date:
            raise ValidationError(
                f"字段 '{field_name}' 不能早于 {self.min_date}"
            )
        
        if self.max_date and date_value > self.max_date:
            raise ValidationError(
                f"字段 '{field_name}' 不能晚于 {self.max_date}"
            )
        
        return date_value


class JSONValidator(Validator):
    """JSON验证器"""
    
    def __init__(self, schema_validator: Optional[Validator] = None, **kwargs):
        """
        初始化JSON验证器
        
        Args:
            schema_validator: JSON数据验证器
            **kwargs: 传递给父类的参数
        """
        super().__init__(**kwargs)
        self.schema_validator = schema_validator
    
    def _validate_value(self, value: Any, field_name: str) -> Any:
        if isinstance(value, str):
            try:
                parsed_value = json.loads(value)
            except json.JSONDecodeError as e:
                raise ValidationError(f"字段 '{field_name}' JSON解析失败: {e}")
        else:
            parsed_value = value
        
        if self.schema_validator:
            return self.schema_validator.validate(parsed_value, field_name)
        
        return parsed_value


class FilePathValidator(Validator):
    """文件路径验证器"""
    
    def __init__(self, must_exist: bool = False,
                 allowed_extensions: Optional[List[str]] = None,
                 **kwargs):
        """
        初始化文件路径验证器
        
        Args:
            must_exist: 文件是否必须存在
            allowed_extensions: 允许的文件扩展名
            **kwargs: 传递给父类的参数
        """
        super().__init__(**kwargs)
        self.must_exist = must_exist
        self.allowed_extensions = allowed_extensions
    
    def _validate_value(self, value: Any, field_name: str) -> Path:
        if not isinstance(value, (str, Path)):
            raise ValidationError(f"字段 '{field_name}' 必须是字符串或Path对象")
        
        path = Path(value)
        
        if self.must_exist and not path.exists():
            raise ValidationError(f"字段 '{field_name}' 指定的文件不存在: {path}")
        
        if self.allowed_extensions:
            if path.suffix.lower() not in [ext.lower() for ext in self.allowed_extensions]:
                raise ValidationError(
                    f"字段 '{field_name}' 文件扩展名必须是: {', '.join(self.allowed_extensions)}"
                )
        
        return path


# =============================================================================
# 复合验证器
# =============================================================================

class ChainValidator(Validator):
    """链式验证器"""
    
    def __init__(self, validators: List[Validator], **kwargs):
        """
        初始化链式验证器
        
        Args:
            validators: 验证器列表
            **kwargs: 传递给父类的参数
        """
        super().__init__(**kwargs)
        self.validators = validators
    
    def _validate_value(self, value: Any, field_name: str) -> Any:
        for validator in self.validators:
            value = validator.validate(value, field_name)
        return value


class ConditionalValidator(Validator):
    """条件验证器"""
    
    def __init__(self, condition: Callable[[Any], bool],
                 true_validator: Validator,
                 false_validator: Optional[Validator] = None,
                 **kwargs):
        """
        初始化条件验证器
        
        Args:
            condition: 条件函数
            true_validator: 条件为真时的验证器
            false_validator: 条件为假时的验证器
            **kwargs: 传递给父类的参数
        """
        super().__init__(**kwargs)
        self.condition = condition
        self.true_validator = true_validator
        self.false_validator = false_validator
    
    def _validate_value(self, value: Any, field_name: str) -> Any:
        if self.condition(value):
            return self.true_validator.validate(value, field_name)
        elif self.false_validator:
            return self.false_validator.validate(value, field_name)
        else:
            return value


# =============================================================================
# 验证装饰器
# =============================================================================

def validate_input(**field_validators):
    """
    输入验证装饰器
    
    Args:
        **field_validators: 字段名到验证器的映射
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 验证关键字参数
            for field_name, validator in field_validators.items():
                if field_name in kwargs:
                    try:
                        kwargs[field_name] = validator.validate(
                            kwargs[field_name], field_name
                        )
                    except ValidationError as e:
                        raise ValidationError(
                            f"函数 {func.__name__} 参数验证失败: {e}"
                        )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_return(validator: Validator):
    """
    返回值验证装饰器
    
    Args:
        validator: 验证器
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            try:
                return validator.validate(result, f"{func.__name__}_return")
            except ValidationError as e:
                raise ValidationError(
                    f"函数 {func.__name__} 返回值验证失败: {e}"
                )
        
        return wrapper
    return decorator


# =============================================================================
# 验证工具函数
# =============================================================================

def validate_data(data: Dict[str, Any], 
                 schema: Dict[str, Validator]) -> Dict[str, Any]:
    """
    验证数据字典
    
    Args:
        data: 要验证的数据
        schema: 验证模式
        
    Returns:
        验证后的数据
        
    Raises:
        ValidationError: 验证失败时抛出
    """
    validator = DictValidator(schema=schema)
    return validator.validate(data, "data")


def create_validator_from_type(type_hint: Type) -> Validator:
    """
    从类型提示创建验证器
    
    Args:
        type_hint: 类型提示
        
    Returns:
        对应的验证器
    """
    origin = get_origin(type_hint)
    args = get_args(type_hint)
    
    if origin is Union:
        # 处理Optional类型
        if len(args) == 2 and type(None) in args:
            non_none_type = next(arg for arg in args if arg is not type(None))
            validator = create_validator_from_type(non_none_type)
            validator.allow_none = True
            return validator
    
    if origin is list:
        item_type = args[0] if args else Any
        item_validator = create_validator_from_type(item_type) if item_type != Any else None
        return ListValidator(item_validator=item_validator)
    
    if origin is dict:
        return DictValidator()
    
    if type_hint == str:
        return StringValidator()
    elif type_hint == int:
        return NumberValidator(number_type=int)
    elif type_hint == float:
        return NumberValidator(number_type=float)
    elif type_hint == bool:
        return TypeValidator(bool)
    elif type_hint == date:
        return DateValidator()
    elif type_hint == datetime:
        return TypeValidator(datetime)
    else:
        return TypeValidator(type_hint)


# =============================================================================
# 常用验证器实例
# =============================================================================

# 基础类型验证器
string_validator = StringValidator()
int_validator = NumberValidator(number_type=int)
float_validator = NumberValidator(number_type=float)
bool_validator = TypeValidator(bool)

# 特殊格式验证器
email_validator = EmailValidator()
url_validator = URLValidator()
date_validator = DateValidator()

# 可选验证器
optional_string = StringValidator(required=False, allow_none=True)
optional_int = NumberValidator(number_type=int, required=False, allow_none=True)

# 常用组合验证器
non_empty_string = StringValidator(min_length=1)
positive_int = NumberValidator(number_type=int, min_value=1)
percentage = NumberValidator(number_type=float, min_value=0, max_value=100)