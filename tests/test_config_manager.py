"""
配置管理系统测试
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from my_python_project.utils.config_manager import (
    ConfigManager,
    init_global_config,
    get_global_config,
    get_config,
    set_config,
)
from my_python_project.utils.exceptions import ConfigError


class TestConfigManager:
    """配置管理器测试"""

    def test_init_empty_config(self):
        """测试初始化空配置"""
        config = ConfigManager()
        assert config._config == {}
        assert config.env_prefix == ""
        assert config.auto_reload is False

    def test_init_with_parameters(self):
        """测试带参数初始化"""
        config = ConfigManager(env_prefix="TEST_", auto_reload=True)
        assert config.env_prefix == "TEST_"
        assert config.auto_reload is True

    def test_from_dict(self):
        """测试从字典创建配置"""
        test_data = {"key1": "value1", "key2": {"nested": "value2"}}
        config = ConfigManager.from_dict(test_data)

        assert config.get("key1") == "value1"
        assert config.get("key2.nested") == "value2"

    def test_set_and_get(self):
        """测试设置和获取配置"""
        config = ConfigManager()

        # 测试简单值
        config.set("test_key", "test_value")
        assert config.get("test_key") == "test_value"

        # 测试嵌套值
        config.set("nested.key", "nested_value")
        assert config.get("nested.key") == "nested_value"

    def test_get_with_default(self):
        """测试获取配置时使用默认值"""
        config = ConfigManager()

        # 不存在的键应返回默认值
        assert config.get("nonexistent", "default") == "default"

        # 存在的键应返回实际值
        config.set("existing", "value")
        assert config.get("existing", "default") == "value"

    def test_get_with_type_hint(self):
        """测试类型转换"""
        config = ConfigManager()

        # 字符串转布尔
        config.set("bool_str", "true")
        assert config.get("bool_str", type_hint=bool) is True

        config.set("bool_str", "false")
        assert config.get("bool_str", type_hint=bool) is False

        # 字符串转整数
        config.set("int_str", "42")
        assert config.get("int_str", type_hint=int) == 42

        # 字符串转浮点数
        config.set("float_str", "3.14")
        assert config.get("float_str", type_hint=float) == 3.14

    def test_has_method(self):
        """测试检查键是否存在"""
        config = ConfigManager()

        assert not config.has("nonexistent")

        config.set("existing", "value")
        assert config.has("existing")

    def test_update_config(self):
        """测试更新配置"""
        config = ConfigManager()
        config.set("key1", "old_value")

        update_data = {"key1": "new_value", "key2": "new_key"}

        config.update(update_data)

        assert config.get("key1") == "new_value"
        assert config.get("key2") == "new_key"

    def test_to_dict(self):
        """测试转换为字典"""
        config = ConfigManager()
        config.set("key1", "value1")
        config.set("key2", "value2")

        config_dict = config.to_dict()

        assert config_dict["key1"] == "value1"
        assert config_dict["key2"] == "value2"

    def test_dict_like_access(self):
        """测试字典风格的访问"""
        config = ConfigManager()

        # 设置值
        config["test_key"] = "test_value"
        assert config["test_key"] == "test_value"

        # 检查键存在
        assert "test_key" in config
        assert "nonexistent" not in config

    def test_env_override(self):
        """测试环境变量覆盖"""
        with patch.dict(
            os.environ,
            {"TEST_KEY1": "env_value1", "TEST_KEY2__NESTED": "env_nested_value"},
        ):
            config = ConfigManager(env_prefix="TEST_")

            assert config.get("key1") == "env_value1"
            assert config.get("key2.nested") == "env_nested_value"

    def test_env_type_conversion(self):
        """测试环境变量类型转换"""
        with patch.dict(
            os.environ,
            {
                "TEST_BOOL_TRUE": "true",
                "TEST_BOOL_FALSE": "false",
                "TEST_INT": "42",
                "TEST_FLOAT": "3.14",
                "TEST_LIST": "a,b,c",
            },
        ):
            config = ConfigManager(env_prefix="TEST_")

            assert config.get("bool_true") is True
            assert config.get("bool_false") is False
            assert config.get("int") == 42
            assert config.get("float") == 3.14
            assert config.get("list") == ["a", "b", "c"]

    def test_load_json_file(self):
        """测试加载JSON文件"""
        test_data = {"key1": "value1", "key2": {"nested": "value2"}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            config = ConfigManager.from_file(temp_file)

            assert config.get("key1") == "value1"
            assert config.get("key2.nested") == "value2"
        finally:
            os.unlink(temp_file)

    def test_load_nonexistent_file(self):
        """测试加载不存在的文件"""
        with pytest.raises(ConfigError, match="配置文件不存在"):
            config = ConfigManager("/nonexistent/path/config.json")
            config.load()

    def test_load_invalid_json(self):
        """测试加载无效的JSON文件"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name

        try:
            config = ConfigManager(temp_file)
            with pytest.raises(ConfigError, match="配置文件解析错误"):
                config.load()
        finally:
            os.unlink(temp_file)

    def test_save_json_file(self):
        """测试保存JSON文件"""
        config = ConfigManager()
        config.set("key1", "value1")
        config.set("key2", "value2")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_file = f.name

        try:
            config.save(temp_file)

            # 验证文件内容
            with open(temp_file, "r") as f:
                saved_data = json.load(f)

            assert saved_data["key1"] == "value1"
            assert saved_data["key2"] == "value2"
        finally:
            os.unlink(temp_file)


class TestGlobalConfig:
    """全局配置测试"""

    def test_init_global_config(self):
        """测试初始化全局配置"""
        config = init_global_config()
        assert config is not None
        assert get_global_config() is config

    def test_global_config_functions(self):
        """测试全局配置函数"""
        init_global_config()

        # 设置配置
        set_config("global_key", "global_value")

        # 获取配置
        assert get_config("global_key") == "global_value"

        # 获取不存在的配置
        with pytest.raises(ConfigError):
            get_config("nonexistent_key")

    def test_global_config_with_default(self):
        """测试全局配置的默认值"""
        init_global_config()

        # 获取不存在的配置，使用默认值
        assert get_config("nonexistent_key", "default") == "default"

    def test_global_config_not_initialized(self):
        """测试未初始化的全局配置"""
        # 重置全局配置
        import my_python_project.utils.config_manager as config_module

        config_module._global_config = None

        with pytest.raises(ConfigError, match="全局配置未初始化"):
            get_global_config()


class TestConfigTypes:
    """配置类型测试"""

    def test_nested_config_access(self):
        """测试嵌套配置访问"""
        config = ConfigManager.from_dict(
            {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "credentials": {"username": "user", "password": "pass"},
                }
            }
        )

        assert config.get("database.host") == "localhost"
        assert config.get("database.port") == 5432
        assert config.get("database.credentials.username") == "user"
        assert config.get("database.credentials.password") == "pass"

    def test_complex_nested_update(self):
        """测试复杂嵌套更新"""
        config = ConfigManager.from_dict(
            {"level1": {"level2": {"key1": "old_value", "key2": "keep_value"}}}
        )

        config.update(
            {"level1": {"level2": {"key1": "new_value", "key3": "added_value"}}}
        )

        assert config.get("level1.level2.key1") == "new_value"
        assert config.get("level1.level2.key2") == "keep_value"
        assert config.get("level1.level2.key3") == "added_value"

    def test_config_with_special_characters(self):
        """测试包含特殊字符的配置"""
        config = ConfigManager()

        # 测试键名包含特殊字符
        config.set("key-with-dash", "dash_value")
        config.set("key_with_underscore", "underscore_value")
        config.set("key.with.dots", "dot_value")

        assert config.get("key-with-dash") == "dash_value"
        assert config.get("key_with_underscore") == "underscore_value"
        assert config.get("key.with.dots") == "dot_value"
