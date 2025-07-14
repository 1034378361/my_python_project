"""
测试延迟导入模块
"""

import pytest
import sys
import importlib
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path

from my_python_project.utils.lazy_import import (
    LazyImport,
    LazyModule,
    lazy_import,
    conditional_import,
    import_optional,
    preload_modules,
    OptionalDependency,
    optional_deps,
    pandas,
    numpy,
    requests,
)


class TestLazyImport:
    """LazyImport类测试"""

    def test_lazy_import_initialization(self):
        """测试LazyImport初始化"""
        # 基本初始化
        lazy_obj = LazyImport("os")
        assert lazy_obj.module_name == "os"
        assert lazy_obj.attribute is None
        assert lazy_obj._imported is False

        # 带属性的初始化
        lazy_attr = LazyImport("os", "path")
        assert lazy_attr.module_name == "os"
        assert lazy_attr.attribute == "path"
        assert lazy_attr._imported is False

    def test_lazy_import_module_access(self):
        """测试模块访问触发导入"""
        lazy_os = LazyImport("os")

        # 访问属性应该触发导入
        result = lazy_os.getcwd
        assert lazy_os._imported is True
        assert lazy_os._module is not None
        assert callable(result)

    def test_lazy_import_attribute_access(self):
        """测试属性访问"""
        lazy_path = LazyImport("os", "path")

        # 访问子属性应该触发导入
        result = lazy_path.join
        assert lazy_path._imported is True
        assert lazy_path._value is not None
        assert callable(result)

    def test_lazy_import_call(self):
        """测试调用功能"""
        lazy_len = LazyImport("builtins", "len")

        # 调用应该触发导入并执行
        result = lazy_len([1, 2, 3])
        assert result == 3
        assert lazy_len._imported is True

    def test_lazy_import_invalid_module(self):
        """测试无效模块导入"""
        lazy_invalid = LazyImport("nonexistent_module_12345")

        with pytest.raises(ImportError, match="无法导入"):
            lazy_invalid.some_attr

    def test_lazy_import_invalid_attribute(self):
        """测试无效属性"""
        lazy_invalid_attr = LazyImport("os", "nonexistent_attribute")

        with pytest.raises(AttributeError):
            lazy_invalid_attr.some_method()

    def test_is_available(self):
        """测试模块可用性检查"""
        # 标准库模块应该可用
        lazy_os = LazyImport("os")
        assert lazy_os.is_available() is True

        # 不存在的模块应该不可用
        lazy_invalid = LazyImport("nonexistent_module_12345")
        assert lazy_invalid.is_available() is False


class TestLazyModule:
    """LazyModule类测试"""

    def test_lazy_module_initialization(self):
        """测试LazyModule初始化"""
        lazy_mod = LazyModule("json")
        assert lazy_mod.__name__ == "json"
        assert lazy_mod._LazyModule__imported is False
        assert lazy_mod._LazyModule__module is None

    def test_lazy_module_access(self):
        """测试模块属性访问"""
        lazy_json = LazyModule("json")

        # 访问属性应该触发导入
        dumps_func = lazy_json.dumps
        assert lazy_json._LazyModule__imported is True
        assert lazy_json._LazyModule__module is not None
        assert callable(dumps_func)

    def test_lazy_module_invalid(self):
        """测试无效模块"""
        lazy_invalid = LazyModule("nonexistent_module_12345")

        with pytest.raises(ImportError, match="无法导入模块"):
            lazy_invalid.some_attr


class TestLazyImportFunction:
    """lazy_import函数测试"""

    def test_lazy_import_function(self):
        """测试lazy_import函数"""
        # 创建延迟导入对象
        lazy_os = lazy_import("os")
        assert isinstance(lazy_os, LazyImport)
        assert lazy_os.module_name == "os"

        # 带属性的延迟导入
        lazy_path = lazy_import("os", "path")
        assert isinstance(lazy_path, LazyImport)
        assert lazy_path.module_name == "os"
        assert lazy_path.attribute == "path"

    def test_lazy_import_caching(self):
        """测试延迟导入缓存"""
        # 同一个模块应该返回相同的对象
        lazy1 = lazy_import("os")
        lazy2 = lazy_import("os")
        assert lazy1 is lazy2

        # 不同的属性应该返回不同的对象
        lazy_path1 = lazy_import("os", "path")
        lazy_path2 = lazy_import("os", "getcwd")
        assert lazy_path1 is not lazy_path2


class TestConditionalImport:
    """conditional_import函数测试"""

    def test_conditional_import_success(self):
        """测试成功的条件导入"""
        module = conditional_import("os")
        assert module is not None
        assert hasattr(module, "getcwd")

    def test_conditional_import_failure(self):
        """测试失败的条件导入"""
        fallback = "fallback_value"
        result = conditional_import("nonexistent_module_12345", fallback)
        assert result == fallback

    def test_conditional_import_with_error_handler(self):
        """测试带错误处理的条件导入"""
        error_caught = []

        def error_handler(error):
            error_caught.append(error)

        result = conditional_import(
            "nonexistent_module_12345", "fallback", error_handler
        )

        assert result == "fallback"
        assert len(error_caught) == 1
        assert isinstance(error_caught[0], ImportError)


class TestImportOptional:
    """import_optional函数测试"""

    def test_import_optional_success(self):
        """测试成功的可选导入"""
        module = import_optional("os")
        assert module is not None
        assert hasattr(module, "getcwd")

    def test_import_optional_failure(self):
        """测试失败的可选导入"""
        with pytest.warns(ImportWarning, match="可选模块.*未安装"):
            result = import_optional("nonexistent_module_12345")
            assert result is None

    def test_import_optional_with_package(self):
        """测试带包名的可选导入"""
        # 测试相对导入
        result = import_optional(".json", "json")
        # 这个可能失败，但不应该抛出异常
        assert result is None or hasattr(result, "loads")


class TestPreloadModules:
    """preload_modules函数测试"""

    def test_preload_modules_sync(self):
        """测试同步预加载"""
        modules = preload_modules(["os", "json"], background=False)

        assert "os" in modules
        assert "json" in modules
        assert hasattr(modules["os"], "getcwd")
        assert hasattr(modules["json"], "loads")

    def test_preload_modules_async(self):
        """测试异步预加载"""
        modules = preload_modules(["os", "json"], background=True)

        assert "os" in modules
        assert "json" in modules
        assert hasattr(modules["os"], "getcwd")
        assert hasattr(modules["json"], "loads")

    def test_preload_modules_with_invalid(self):
        """测试包含无效模块的预加载"""
        with pytest.warns(UserWarning, match="预加载模块.*失败"):
            modules = preload_modules(["os", "nonexistent_module_12345"])

        assert "os" in modules
        assert "nonexistent_module_12345" not in modules


class TestOptionalDependency:
    """OptionalDependency类测试"""

    def test_optional_dependency_initialization(self):
        """测试OptionalDependency初始化"""
        opt_deps = OptionalDependency()
        assert isinstance(opt_deps._available, dict)
        assert isinstance(opt_deps._modules, dict)

    def test_register_available_dependency(self):
        """测试注册可用依赖"""
        opt_deps = OptionalDependency()
        opt_deps.register("os_test", "os")

        assert opt_deps.is_available("os_test") is True
        assert opt_deps.get_module("os_test") is not None
        assert hasattr(opt_deps.get_module("os_test"), "getcwd")

    def test_register_unavailable_dependency(self):
        """测试注册不可用依赖"""
        opt_deps = OptionalDependency()

        with pytest.warns(ImportWarning, match="可选依赖.*未安装"):
            opt_deps.register(
                "invalid_test", "nonexistent_module_12345", "pip install nonexistent"
            )

        assert opt_deps.is_available("invalid_test") is False
        assert opt_deps.get_module("invalid_test") is None

    def test_require_available_dependency(self):
        """测试要求可用依赖"""
        opt_deps = OptionalDependency()
        opt_deps.register("os_test", "os")

        module = opt_deps.require("os_test")
        assert module is not None
        assert hasattr(module, "getcwd")

    def test_require_unavailable_dependency(self):
        """测试要求不可用依赖"""
        opt_deps = OptionalDependency()
        opt_deps._available["invalid_test"] = False

        with pytest.raises(ImportError, match="必需的依赖.*不可用"):
            opt_deps.require("invalid_test")


class TestGlobalLazyImports:
    """全局延迟导入测试"""

    def test_global_pandas_import(self):
        """测试全局pandas导入"""
        # 检查pandas对象是否是LazyImport实例
        assert isinstance(pandas, LazyImport)
        assert pandas.module_name == "pandas"

        # 如果pandas可用，测试访问
        if pandas.is_available():
            # 触发导入
            pd_version = pandas.__version__
            assert isinstance(pd_version, str)

    def test_global_numpy_import(self):
        """测试全局numpy导入"""
        assert isinstance(numpy, LazyImport)
        assert numpy.module_name == "numpy"

        if numpy.is_available():
            # 测试numpy函数
            arr = numpy.array([1, 2, 3])
            assert len(arr) == 3

    def test_global_requests_import(self):
        """测试全局requests导入"""
        assert isinstance(requests, LazyImport)
        assert requests.module_name == "requests"

        if requests.is_available():
            # 测试requests有get方法
            assert hasattr(requests, "get")


class TestGlobalOptionalDeps:
    """全局可选依赖测试"""

    def test_global_optional_deps(self):
        """测试全局可选依赖管理器"""
        assert isinstance(optional_deps, OptionalDependency)

    def test_registered_dependencies(self):
        """测试预注册的依赖"""
        expected_deps = [
            "yaml",
            "redis",
            "pandas",
            "numpy",
            "requests",
            "watchdog",
            "tomli",
        ]

        for dep in expected_deps:
            # 检查依赖是否已注册（无论是否可用）
            available = optional_deps.is_available(dep)
            assert isinstance(available, bool)


class TestErrorHandling:
    """错误处理测试"""

    def test_import_error_handling(self):
        """测试导入错误处理"""
        lazy_invalid = LazyImport("nonexistent_module_12345")

        with pytest.raises(ImportError):
            lazy_invalid.some_method()

    def test_attribute_error_handling(self):
        """测试属性错误处理"""
        lazy_os = LazyImport("os")

        with pytest.raises(AttributeError):
            lazy_os.nonexistent_attribute

    @patch("importlib.import_module")
    def test_module_import_failure(self, mock_import):
        """测试模块导入失败"""
        mock_import.side_effect = ImportError("Test error")

        lazy_obj = LazyImport("test_module")

        with pytest.raises(ImportError, match="无法导入"):
            lazy_obj.some_attr


class TestPerformance:
    """性能测试"""

    def test_lazy_import_overhead(self):
        """测试延迟导入开销"""
        import time

        # 测试延迟导入创建时间
        start_time = time.time()
        for _ in range(1000):
            lazy_import("os")
        end_time = time.time()

        creation_time = end_time - start_time
        assert creation_time < 1.0  # 应该很快

    def test_first_access_time(self):
        """测试首次访问时间"""
        import time

        lazy_os = LazyImport("os")

        # 测试首次访问时间
        start_time = time.time()
        lazy_os.getcwd
        end_time = time.time()

        access_time = end_time - start_time
        assert access_time < 0.1  # 首次访问应该在100ms内


if __name__ == "__main__":
    pytest.main([__file__])
