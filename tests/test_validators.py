"""
数据验证器测试
"""

import json
import tempfile
from datetime import date, datetime
from pathlib import Path
from decimal import Decimal

import pytest

from my_python_project.utils.validators import (
    Validator,
    StringValidator,
    NumberValidator,
    ListValidator,
    DictValidator,
    EmailValidator,
    URLValidator,
    DateValidator,
    JSONValidator,
    FilePathValidator,
    ChainValidator,
    ConditionalValidator,
    TypeValidator,
    validate_input,
    validate_return,
    validate_data,
    create_validator_from_type,
    string_validator,
    int_validator,
    email_validator,
    url_validator,
)
from my_python_project.utils.exceptions import ValidationError


class TestBaseValidator:
    """基础验证器测试"""

    def test_validator_init(self):
        """测试验证器初始化"""
        validator = Validator(required=True, allow_none=False)
        assert validator.required is True
        assert validator.allow_none is False

    def test_required_validation(self):
        """测试必需字段验证"""
        validator = Validator(required=True)

        # 必需字段不能为None
        with pytest.raises(ValidationError, match="是必需的"):
            validator.validate(None, "test_field")

    def test_allow_none_validation(self):
        """测试允许None值验证"""
        validator = Validator(required=True, allow_none=True)

        # 允许None值
        assert validator.validate(None, "test_field") is None

    def test_optional_field(self):
        """测试可选字段"""
        validator = Validator(required=False)

        # 可选字段可以为None
        assert validator.validate(None, "test_field") is None

    def test_callable_validator(self):
        """测试验证器可调用"""
        validator = Validator()

        # 验证器应该是可调用的
        assert callable(validator)
        assert validator("test_value") == "test_value"


class TestStringValidator:
    """字符串验证器测试"""

    def test_string_validation(self):
        """测试字符串验证"""
        validator = StringValidator()

        assert validator.validate("test", "field") == "test"
        assert validator.validate(123, "field") == "123"  # 自动转换

    def test_string_strip(self):
        """测试字符串去空格"""
        validator = StringValidator(strip=True)

        assert validator.validate("  test  ", "field") == "test"

        validator = StringValidator(strip=False)
        assert validator.validate("  test  ", "field") == "  test  "

    def test_string_length_validation(self):
        """测试字符串长度验证"""
        validator = StringValidator(min_length=2, max_length=5)

        # 正常长度
        assert validator.validate("abc", "field") == "abc"

        # 太短
        with pytest.raises(ValidationError, match="长度不能少于"):
            validator.validate("a", "field")

        # 太长
        with pytest.raises(ValidationError, match="长度不能超过"):
            validator.validate("abcdef", "field")

    def test_string_pattern_validation(self):
        """测试字符串模式验证"""
        validator = StringValidator(pattern=r"^\d{3}-\d{4}$")

        # 匹配模式
        assert validator.validate("123-4567", "field") == "123-4567"

        # 不匹配模式
        with pytest.raises(ValidationError, match="格式不正确"):
            validator.validate("abc-defg", "field")

    def test_string_choices_validation(self):
        """测试字符串选择验证"""
        validator = StringValidator(choices=["red", "green", "blue"])

        # 有效选择
        assert validator.validate("red", "field") == "red"

        # 无效选择
        with pytest.raises(ValidationError, match="必须是以下值之一"):
            validator.validate("yellow", "field")


class TestNumberValidator:
    """数字验证器测试"""

    def test_int_validation(self):
        """测试整数验证"""
        validator = NumberValidator(number_type=int)

        assert validator.validate(42, "field") == 42
        assert validator.validate("42", "field") == 42
        assert validator.validate(3.14, "field") == 3  # 截断

    def test_float_validation(self):
        """测试浮点数验证"""
        validator = NumberValidator(number_type=float)

        assert validator.validate(3.14, "field") == 3.14
        assert validator.validate("3.14", "field") == 3.14
        assert validator.validate(42, "field") == 42.0

    def test_decimal_validation(self):
        """测试Decimal验证"""
        validator = NumberValidator(number_type=Decimal)

        result = validator.validate("3.14", "field")
        assert isinstance(result, Decimal)
        assert result == Decimal("3.14")

    def test_number_range_validation(self):
        """测试数字范围验证"""
        validator = NumberValidator(min_value=0, max_value=100, number_type=int)

        # 正常范围
        assert validator.validate(50, "field") == 50

        # 太小
        with pytest.raises(ValidationError, match="不能小于"):
            validator.validate(-1, "field")

        # 太大
        with pytest.raises(ValidationError, match="不能大于"):
            validator.validate(101, "field")

    def test_invalid_number_conversion(self):
        """测试无效数字转换"""
        validator = NumberValidator(number_type=int)

        with pytest.raises(ValidationError, match="无法转换为"):
            validator.validate("abc", "field")


class TestListValidator:
    """列表验证器测试"""

    def test_list_validation(self):
        """测试列表验证"""
        validator = ListValidator()

        assert validator.validate([1, 2, 3], "field") == [1, 2, 3]
        assert validator.validate((1, 2, 3), "field") == [1, 2, 3]  # 元组转列表

    def test_list_length_validation(self):
        """测试列表长度验证"""
        validator = ListValidator(min_length=2, max_length=4)

        # 正常长度
        assert validator.validate([1, 2, 3], "field") == [1, 2, 3]

        # 太短
        with pytest.raises(ValidationError, match="长度不能少于"):
            validator.validate([1], "field")

        # 太长
        with pytest.raises(ValidationError, match="长度不能超过"):
            validator.validate([1, 2, 3, 4, 5], "field")

    def test_list_unique_validation(self):
        """测试列表唯一性验证"""
        validator = ListValidator(unique=True)

        # 唯一元素
        assert validator.validate([1, 2, 3], "field") == [1, 2, 3]

        # 重复元素
        with pytest.raises(ValidationError, match="存在重复项"):
            validator.validate([1, 2, 2], "field")

    def test_list_item_validation(self):
        """测试列表项验证"""
        item_validator = StringValidator(min_length=2)
        validator = ListValidator(item_validator=item_validator)

        # 有效项
        assert validator.validate(["ab", "cd"], "field") == ["ab", "cd"]

        # 无效项
        with pytest.raises(ValidationError, match="索引 1 验证失败"):
            validator.validate(["ab", "c"], "field")

    def test_non_list_validation(self):
        """测试非列表验证"""
        validator = ListValidator()

        with pytest.raises(ValidationError, match="必须是列表或元组"):
            validator.validate("not a list", "field")


class TestDictValidator:
    """字典验证器测试"""

    def test_dict_validation(self):
        """测试字典验证"""
        schema = {
            "name": StringValidator(),
            "age": NumberValidator(number_type=int, min_value=0),
        }
        validator = DictValidator(schema=schema)

        data = {"name": "John", "age": 30}
        result = validator.validate(data, "field")

        assert result["name"] == "John"
        assert result["age"] == 30

    def test_dict_required_fields(self):
        """测试字典必需字段"""
        schema = {
            "name": StringValidator(required=True),
            "age": NumberValidator(number_type=int, required=False),
        }
        validator = DictValidator(schema=schema)

        # 缺少必需字段
        with pytest.raises(ValidationError):
            validator.validate({"age": 30}, "field")

        # 只有必需字段
        result = validator.validate({"name": "John"}, "field")
        assert result["name"] == "John"
        assert "age" not in result

    def test_dict_allow_extra(self):
        """测试字典允许额外字段"""
        schema = {"name": StringValidator()}

        # 不允许额外字段
        validator = DictValidator(schema=schema, allow_extra=False)
        with pytest.raises(ValidationError, match="包含未定义的字段"):
            validator.validate({"name": "John", "extra": "value"}, "field")

        # 允许额外字段
        validator = DictValidator(schema=schema, allow_extra=True)
        result = validator.validate({"name": "John", "extra": "value"}, "field")
        assert result["name"] == "John"
        assert result["extra"] == "value"

    def test_non_dict_validation(self):
        """测试非字典验证"""
        validator = DictValidator()

        with pytest.raises(ValidationError, match="必须是字典"):
            validator.validate("not a dict", "field")


class TestSpecialValidators:
    """特殊验证器测试"""

    def test_email_validation(self):
        """测试邮箱验证"""
        validator = EmailValidator()

        # 有效邮箱
        assert validator.validate("test@example.com", "field") == "test@example.com"
        assert validator.validate("USER@EXAMPLE.COM", "field") == "user@example.com"

        # 无效邮箱
        with pytest.raises(ValidationError, match="不是有效的邮箱地址"):
            validator.validate("invalid-email", "field")

    def test_url_validation(self):
        """测试URL验证"""
        validator = URLValidator()

        # 有效URL
        assert (
            validator.validate("https://example.com", "field") == "https://example.com"
        )
        assert (
            validator.validate("http://example.com/path", "field")
            == "http://example.com/path"
        )

        # 无效URL
        with pytest.raises(ValidationError, match="不是有效的URL"):
            validator.validate("invalid-url", "field")

    def test_date_validation(self):
        """测试日期验证"""
        validator = DateValidator()

        # 字符串日期
        result = validator.validate("2023-01-01", "field")
        assert isinstance(result, date)
        assert result == date(2023, 1, 1)

        # 日期对象
        test_date = date(2023, 1, 1)
        assert validator.validate(test_date, "field") == test_date

        # 无效日期格式
        with pytest.raises(ValidationError, match="日期格式不正确"):
            validator.validate("invalid-date", "field")

    def test_date_range_validation(self):
        """测试日期范围验证"""
        min_date = date(2023, 1, 1)
        max_date = date(2023, 12, 31)
        validator = DateValidator(min_date=min_date, max_date=max_date)

        # 正常范围
        assert validator.validate("2023-06-15", "field") == date(2023, 6, 15)

        # 太早
        with pytest.raises(ValidationError, match="不能早于"):
            validator.validate("2022-12-31", "field")

        # 太晚
        with pytest.raises(ValidationError, match="不能晚于"):
            validator.validate("2024-01-01", "field")

    def test_json_validation(self):
        """测试JSON验证"""
        validator = JSONValidator()

        # 有效JSON字符串
        json_str = '{"key": "value"}'
        result = validator.validate(json_str, "field")
        assert result == {"key": "value"}

        # 已解析的对象
        obj = {"key": "value"}
        assert validator.validate(obj, "field") == obj

        # 无效JSON
        with pytest.raises(ValidationError, match="JSON解析失败"):
            validator.validate("invalid json", "field")

    def test_filepath_validation(self):
        """测试文件路径验证"""
        validator = FilePathValidator()

        # 字符串路径
        path_str = "/tmp/test.txt"
        result = validator.validate(path_str, "field")
        assert isinstance(result, Path)
        assert str(result) == path_str

        # Path对象
        path_obj = Path("/tmp/test.txt")
        assert validator.validate(path_obj, "field") == path_obj

    def test_filepath_extension_validation(self):
        """测试文件扩展名验证"""
        validator = FilePathValidator(allowed_extensions=[".txt", ".json"])

        # 允许的扩展名
        assert validator.validate("test.txt", "field") == Path("test.txt")
        assert validator.validate("test.json", "field") == Path("test.json")

        # 不允许的扩展名
        with pytest.raises(ValidationError, match="文件扩展名必须是"):
            validator.validate("test.pdf", "field")


class TestComplexValidators:
    """复合验证器测试"""

    def test_chain_validator(self):
        """测试链式验证器"""
        validators = [
            StringValidator(strip=True),
            StringValidator(min_length=3),
            StringValidator(pattern=r"^[a-zA-Z]+$"),
        ]
        validator = ChainValidator(validators)

        # 通过所有验证
        assert validator.validate("  hello  ", "field") == "hello"

        # 在某个验证器失败
        with pytest.raises(ValidationError):
            validator.validate("  hi  ", "field")  # 长度不够

    def test_conditional_validator(self):
        """测试条件验证器"""

        def is_positive(value):
            return value > 0

        positive_validator = NumberValidator(number_type=int, min_value=1)
        negative_validator = NumberValidator(number_type=int, max_value=-1)

        validator = ConditionalValidator(
            condition=is_positive,
            true_validator=positive_validator,
            false_validator=negative_validator,
        )

        # 正数
        assert validator.validate(5, "field") == 5

        # 负数
        assert validator.validate(-5, "field") == -5

        # 零（不符合任何条件）
        assert validator.validate(0, "field") == 0  # 使用原值


class TestValidationDecorators:
    """验证装饰器测试"""

    def test_validate_input_decorator(self):
        """测试输入验证装饰器"""

        @validate_input(
            name=StringValidator(min_length=2),
            age=NumberValidator(number_type=int, min_value=0),
        )
        def create_user(name, age):
            return f"User: {name}, Age: {age}"

        # 有效输入
        result = create_user(name="John", age=30)
        assert result == "User: John, Age: 30"

        # 无效输入
        with pytest.raises(ValidationError):
            create_user(name="J", age=30)  # 名字太短

    def test_validate_return_decorator(self):
        """测试返回值验证装饰器"""

        @validate_return(StringValidator(min_length=5))
        def get_message():
            return "Hello World"

        # 有效返回值
        assert get_message() == "Hello World"

        @validate_return(StringValidator(min_length=20))
        def get_short_message():
            return "Hi"

        # 无效返回值
        with pytest.raises(ValidationError):
            get_short_message()


class TestUtilityFunctions:
    """工具函数测试"""

    def test_validate_data_function(self):
        """测试数据验证函数"""
        schema = {"name": StringValidator(), "age": NumberValidator(number_type=int)}

        data = {"name": "John", "age": 30}
        result = validate_data(data, schema)

        assert result["name"] == "John"
        assert result["age"] == 30

    def test_create_validator_from_type(self):
        """测试从类型创建验证器"""
        # 字符串类型
        validator = create_validator_from_type(str)
        assert isinstance(validator, StringValidator)

        # 整数类型
        validator = create_validator_from_type(int)
        assert isinstance(validator, NumberValidator)

        # 列表类型
        validator = create_validator_from_type(list)
        assert isinstance(validator, ListValidator)

        # 字典类型
        validator = create_validator_from_type(dict)
        assert isinstance(validator, DictValidator)


class TestPrebuiltValidators:
    """预构建验证器测试"""

    def test_string_validator(self):
        """测试字符串验证器"""
        assert string_validator.validate("test", "field") == "test"

    def test_int_validator(self):
        """测试整数验证器"""
        assert int_validator.validate(42, "field") == 42

    def test_email_validator(self):
        """测试邮箱验证器"""
        assert (
            email_validator.validate("test@example.com", "field") == "test@example.com"
        )

    def test_url_validator(self):
        """测试URL验证器"""
        assert (
            url_validator.validate("https://example.com", "field")
            == "https://example.com"
        )


class TestEdgeCases:
    """边界情况测试"""

    def test_empty_string_validation(self):
        """测试空字符串验证"""
        validator = StringValidator(min_length=0)
        assert validator.validate("", "field") == ""

        validator = StringValidator(min_length=1)
        with pytest.raises(ValidationError):
            validator.validate("", "field")

    def test_zero_validation(self):
        """测试零值验证"""
        validator = NumberValidator(number_type=int, min_value=0)
        assert validator.validate(0, "field") == 0

        validator = NumberValidator(number_type=int, min_value=1)
        with pytest.raises(ValidationError):
            validator.validate(0, "field")

    def test_empty_list_validation(self):
        """测试空列表验证"""
        validator = ListValidator(min_length=0)
        assert validator.validate([], "field") == []

        validator = ListValidator(min_length=1)
        with pytest.raises(ValidationError):
            validator.validate([], "field")

    def test_nested_validation_errors(self):
        """测试嵌套验证错误"""
        schema = {
            "users": ListValidator(
                item_validator=DictValidator(
                    schema={
                        "name": StringValidator(min_length=2),
                        "email": EmailValidator(),
                    }
                )
            )
        }

        validator = DictValidator(schema=schema)

        # 嵌套验证失败
        data = {
            "users": [
                {"name": "John", "email": "john@example.com"},
                {"name": "J", "email": "invalid-email"},  # 多个错误
            ]
        }

        with pytest.raises(ValidationError):
            validator.validate(data, "field")
