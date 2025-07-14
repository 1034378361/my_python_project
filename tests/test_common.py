"""
测试通用工具函数模块
"""

import tempfile
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, mock_open

from my_python_project.utils.common import (
    # 时间工具
    now_timestamp,
    format_datetime,
    parse_datetime,
    # 字符串工具
    safe_filename,
    slugify,
    clean_text,
    # 文件工具
    ensure_dir,
    load_json,
    save_json,
    load_yaml,
    save_yaml,
    load_pickle,
    save_pickle,
    get_file_size,
    list_files,
    # 数据工具
    deep_merge,
    flatten_dict,
    chunk_list,
    calculate_md5,
    calculate_sha256,
    get_date_range,
    # 验证工具
    is_valid_email,
    is_valid_url,
    # 其他工具
    generate_random_string,
    generate_uuid,
    retry_on_failure,
    timing_decorator,
)


class TestTimeUtils:
    """时间工具测试"""

    def test_now_timestamp(self):
        """测试获取当前时间戳"""
        timestamp = now_timestamp()
        assert isinstance(timestamp, int)
        assert timestamp > 0

    def test_format_datetime(self):
        """测试日期时间格式化"""
        dt = datetime(2023, 12, 25, 15, 30, 45)

        # 默认格式
        result = format_datetime(dt)
        assert result == "2023-12-25 15:30:45"

        # 自定义格式
        result = format_datetime(dt, "%Y/%m/%d")
        assert result == "2023/12/25"

        # 默认当前时间
        result = format_datetime()
        assert isinstance(result, str)
        assert len(result) == 19  # "YYYY-MM-DD HH:MM:SS"

    def test_parse_datetime(self):
        """测试日期时间解析"""
        date_str = "2023-12-25 15:30:45"
        result = parse_datetime(date_str)

        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 12
        assert result.day == 25
        assert result.hour == 15
        assert result.minute == 30
        assert result.second == 45


class TestStringUtils:
    """字符串工具测试"""

    def test_safe_filename(self):
        """测试安全文件名生成"""
        # 基本测试
        assert safe_filename("hello.txt") == "hello.txt"

        # 特殊字符替换
        assert safe_filename('file<>:"|?*.txt') == "file_______.txt"

        # 中文处理
        assert safe_filename("测试文件.txt") == "测试文件.txt"

        # 长文件名截断
        long_name = "a" * 300 + ".txt"
        result = safe_filename(long_name)
        assert len(result) <= 255
        assert result.endswith(".txt")

    def test_slugify(self):
        """测试URL友好字符串生成"""
        assert slugify("Hello World") == "hello-world"
        assert slugify("测试 Test 123!@#") == "test-123"
        assert slugify("  Multiple   Spaces  ") == "multiple-spaces"
        assert slugify("") == ""

    def test_clean_text(self):
        """测试文本清理"""
        assert clean_text("  hello   world  ") == "hello world"
        assert clean_text("line1\n\nline2\t\tline3") == "line1 line2 line3"
        assert clean_text("") == ""


class TestFileUtils:
    """文件工具测试"""

    def test_ensure_dir(self):
        """测试目录创建"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "subdir" / "deep"
            result = ensure_dir(test_dir)

            assert result.exists()
            assert result.is_dir()
            assert result == test_dir

    def test_json_operations(self):
        """测试JSON文件操作"""
        test_data = {"name": "test", "value": 123, "items": [1, 2, 3]}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json_file = f.name

        try:
            # 保存JSON
            save_json(test_data, json_file)

            # 加载JSON
            loaded_data = load_json(json_file)
            assert loaded_data == test_data

        finally:
            Path(json_file).unlink(missing_ok=True)

    def test_yaml_operations(self):
        """测试YAML文件操作"""
        test_data = {"name": "test", "config": {"debug": True, "port": 8080}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml_file = f.name

        try:
            # 保存YAML
            save_yaml(test_data, yaml_file)

            # 加载YAML
            loaded_data = load_yaml(yaml_file)
            assert loaded_data == test_data

        except ImportError:
            pytest.skip("PyYAML not installed")
        finally:
            Path(yaml_file).unlink(missing_ok=True)

    def test_pickle_operations(self):
        """测试Pickle文件操作"""
        test_data = {"complex": set([1, 2, 3]), "tuple": (1, "test")}

        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
            pickle_file = f.name

        try:
            # 保存Pickle
            save_pickle(test_data, pickle_file)

            # 加载Pickle
            loaded_data = load_pickle(pickle_file)
            assert loaded_data == test_data

        finally:
            Path(pickle_file).unlink(missing_ok=True)

    def test_get_file_size(self):
        """测试文件大小获取"""
        content = "test content"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(content)
            test_file = f.name

        try:
            # 字节大小
            size_bytes = get_file_size(test_file, "bytes")
            assert size_bytes == len(content.encode("utf-8"))

            # KB大小
            size_kb = get_file_size(test_file, "KB")
            assert size_kb == size_bytes / 1024

            # 无效单位
            with pytest.raises(ValueError):
                get_file_size(test_file, "invalid")

        finally:
            Path(test_file).unlink(missing_ok=True)

    def test_list_files(self):
        """测试文件列表"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 创建测试文件
            (temp_path / "file1.txt").touch()
            (temp_path / "file2.py").touch()
            (temp_path / "subdir").mkdir()
            (temp_path / "subdir" / "file3.txt").touch()

            # 非递归搜索
            files = list_files(temp_path, "*.txt", recursive=False)
            assert len(files) == 1
            assert files[0].name == "file1.txt"

            # 递归搜索
            files = list_files(temp_path, "*.txt", recursive=True)
            assert len(files) == 2

            # 所有文件
            files = list_files(temp_path, "*", recursive=False)
            assert len(files) == 3  # 2个文件 + 1个目录


class TestDataUtils:
    """数据工具测试"""

    def test_deep_merge(self):
        """测试深度合并字典"""
        dict1 = {"a": 1, "b": {"c": 2, "d": 3}}
        dict2 = {"b": {"d": 4, "e": 5}, "f": 6}

        result = deep_merge(dict1, dict2)
        expected = {"a": 1, "b": {"c": 2, "d": 4, "e": 5}, "f": 6}

        assert result == expected
        # 确保原字典未被修改
        assert dict1 == {"a": 1, "b": {"c": 2, "d": 3}}

    def test_flatten_dict(self):
        """测试字典扁平化"""
        nested = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}

        result = flatten_dict(nested)
        expected = {"a": 1, "b.c": 2, "b.d.e": 3}

        assert result == expected

        # 自定义分隔符
        result = flatten_dict(nested, sep="_")
        expected = {"a": 1, "b_c": 2, "b_d_e": 3}
        assert result == expected

    def test_chunk_list(self):
        """测试列表分块"""
        data = list(range(10))

        # 正常分块
        chunks = chunk_list(data, 3)
        assert chunks == [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]

        # 完整分块
        chunks = chunk_list(data, 5)
        assert chunks == [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]

        # 大块大小
        chunks = chunk_list(data, 20)
        assert chunks == [data]

        # 空列表
        chunks = chunk_list([], 3)
        assert chunks == []

    def test_calculate_md5(self):
        """测试MD5计算"""
        text = "hello world"
        result = calculate_md5(text)

        assert isinstance(result, str)
        assert len(result) == 32
        assert result == "5eb63bbbe01eeed093cb22bb8f5acdc3"

        # 字节输入
        result_bytes = calculate_md5(text.encode("utf-8"))
        assert result == result_bytes

    def test_calculate_sha256(self):
        """测试SHA256计算"""
        text = "hello world"
        result = calculate_sha256(text)

        assert isinstance(result, str)
        assert len(result) == 64
        assert (
            result == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        )

    def test_get_date_range(self):
        """测试日期范围生成"""
        start = "2023-01-01"
        end = "2023-01-05"

        result = get_date_range(start, end)
        expected = [
            "2023-01-01",
            "2023-01-02",
            "2023-01-03",
            "2023-01-04",
            "2023-01-05",
        ]

        assert result == expected

        # datetime对象输入
        start_dt = datetime(2023, 1, 1)
        end_dt = datetime(2023, 1, 3)
        result = get_date_range(start_dt, end_dt)
        assert result == ["2023-01-01", "2023-01-02", "2023-01-03"]


class TestValidationUtils:
    """验证工具测试"""

    def test_is_valid_email(self):
        """测试邮箱验证"""
        # 有效邮箱
        assert is_valid_email("test@example.com") == True
        assert is_valid_email("user.name+tag@domain.co.uk") == True

        # 无效邮箱
        assert is_valid_email("invalid.email") == False
        assert is_valid_email("@domain.com") == False
        assert is_valid_email("user@") == False
        assert is_valid_email("") == False

    def test_is_valid_url(self):
        """测试URL验证"""
        # 有效URL
        assert is_valid_url("https://example.com") == True
        assert is_valid_url("http://localhost:8080/path") == True

        # 无效URL
        assert is_valid_url("not-a-url") == False
        assert is_valid_url("ftp://example.com") == False
        assert is_valid_url("") == False


class TestOtherUtils:
    """其他工具测试"""

    def test_generate_random_string(self):
        """测试随机字符串生成"""
        # 默认长度
        result = generate_random_string()
        assert len(result) == 8
        assert result.isalnum()

        # 自定义长度
        result = generate_random_string(16)
        assert len(result) == 16

        # 不同调用结果不同
        result1 = generate_random_string()
        result2 = generate_random_string()
        assert result1 != result2

    def test_generate_uuid(self):
        """测试UUID生成"""
        result = generate_uuid()

        assert isinstance(result, str)
        assert len(result) == 36  # UUID4格式长度
        assert result.count("-") == 4

        # 不同调用结果不同
        result1 = generate_uuid()
        result2 = generate_uuid()
        assert result1 != result2

    def test_retry_on_failure(self):
        """测试重试装饰器"""
        call_count = 0

        @retry_on_failure(max_retries=3, delay=0.01)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = flaky_function()
        assert result == "success"
        assert call_count == 3

    def test_timing_decorator(self):
        """测试计时装饰器"""

        @timing_decorator
        def slow_function():
            import time

            time.sleep(0.01)
            return "done"

        # 捕获标准输出来测试打印
        with patch("builtins.print") as mock_print:
            result = slow_function()
            assert result == "done"
            mock_print.assert_called_once()
            args = mock_print.call_args[0][0]
            assert "slow_function 执行时间:" in args


if __name__ == "__main__":
    pytest.main([__file__])
