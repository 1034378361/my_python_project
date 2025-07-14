"""路径管理器测试模块。"""

import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from my_python_project.utils.path_manager import (
    ProjectPathManager,
    init_project_paths,
    get_project_paths,
    get_project_path,
)


class TestProjectPathManager:
    """测试项目路径管理器。"""

    def test_initialization(self):
        """测试初始化。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectPathManager(temp_dir, session_name="test_session")

            assert pm.base_dir == Path(temp_dir).resolve()
            assert pm.session_name == "test_session"
            assert pm.session_dir == pm.base_dir / "test_session"
            assert pm.session_dir.exists()

    def test_auto_session_name(self):
        """测试自动生成会话名称。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectPathManager(temp_dir)

            # 验证会话名称格式
            assert len(pm.session_name) == 15  # YYYYMMDD_HHMMSS
            assert "_" in pm.session_name

            # 验证可以解析为时间
            try:
                datetime.strptime(pm.session_name, "%Y%m%d_%H%M%S")
            except ValueError:
                pytest.fail("会话名称格式不正确")

    def test_standard_directories_creation(self):
        """测试标准目录创建。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            standard_dirs = ["logs", "reports", "data", "models"]
            pm = ProjectPathManager(
                temp_dir, session_name="test", standard_dirs=standard_dirs
            )

            # 验证所有标准目录都被创建
            for dir_name in standard_dirs:
                dir_path = pm.session_dir / dir_name
                assert dir_path.exists()
                assert dir_path.is_dir()

    def test_get_path_standard(self):
        """测试获取标准路径。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectPathManager(temp_dir, session_name="test")

            logs_path = pm.get_path("logs")
            assert logs_path == pm.session_dir / "logs"
            assert logs_path.exists()

    def test_get_path_nested(self):
        """测试获取嵌套路径。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectPathManager(temp_dir, session_name="test")

            nested_path = pm.get_path("data/processed/clean")
            expected_path = pm.session_dir / "data" / "processed" / "clean"

            assert nested_path == expected_path
            assert nested_path.exists()

    def test_get_path_custom(self):
        """测试获取自定义路径。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectPathManager(temp_dir, session_name="test")

            custom_path = pm.get_path("experiments")
            expected_path = pm.session_dir / "experiments"

            assert custom_path == expected_path
            assert custom_path.exists()
            assert "experiments" in pm.custom_dirs

    def test_get_file_path(self):
        """测试获取文件路径。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectPathManager(temp_dir, session_name="test")

            file_path = pm.get_file_path("logs", "app.log")
            expected_path = pm.session_dir / "logs" / "app.log"

            assert file_path == expected_path

    def test_get_unique_filename(self):
        """测试获取唯一文件名。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectPathManager(temp_dir, session_name="test")

            # 第一次调用，文件不存在
            file_path1 = pm.get_unique_filename("logs", "test.log")
            assert file_path1.name == "test.log"

            # 创建文件
            file_path1.touch()

            # 第二次调用，文件存在，应该生成新名称
            file_path2 = pm.get_unique_filename("logs", "test.log")
            assert file_path2.name.startswith("test_")
            assert file_path2.name.endswith(".log")
            assert file_path1 != file_path2

    def test_create_custom_dir(self):
        """测试创建自定义目录。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectPathManager(temp_dir, session_name="test")

            # 创建简单自定义目录
            custom_dir = pm.create_custom_dir("experiments")
            assert custom_dir.exists()
            assert "experiments" in pm.custom_dirs

            # 创建嵌套自定义目录
            nested_dir = pm.create_custom_dir("models/trained/v1")
            assert nested_dir.exists()
            assert "models/trained/v1" in pm.custom_dirs

    def test_get_custom_path(self):
        """测试获取自定义路径。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectPathManager(temp_dir, session_name="test")

            # 获取目录路径
            dir_path = pm.get_custom_path("experiments")
            assert dir_path.exists()

            # 获取文件路径
            file_path = pm.get_custom_path("experiments", "exp1.json")
            expected_path = pm.session_dir / "experiments" / "exp1.json"
            assert file_path == expected_path

    def test_specific_path_methods(self):
        """测试特定类型的路径方法。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectPathManager(temp_dir, session_name="test")

            # 测试各种特定路径方法
            log_path = pm.get_log_path("app.log")
            assert log_path.suffix == ".log"
            assert "logs" in str(log_path)

            report_path = pm.get_report_path("summary")
            assert report_path.suffix == ".docx"
            assert "reports" in str(report_path)

            data_path = pm.get_data_path("dataset.csv")
            assert "data" in str(data_path)

            model_path = pm.get_model_path("model.pkl")
            assert "models" in str(model_path)

    def test_image_path(self):
        """测试图片路径。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectPathManager(temp_dir, session_name="test")

            image_path = pm.get_image_path("screenshots", "screen1.png")
            expected_path = pm.session_dir / "images" / "screenshots" / "screen1.png"

            assert image_path == expected_path
            # 验证目录被创建
            assert image_path.parent.exists()

    def test_convenience_properties(self):
        """测试便捷属性。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectPathManager(temp_dir, session_name="test")

            assert pm.logs_dir == pm.session_dir / "logs"
            assert pm.reports_dir == pm.session_dir / "reports"
            assert pm.data_dir == pm.session_dir / "data"
            assert pm.models_dir == pm.session_dir / "models"
            assert pm.output_dir == pm.session_dir / "output"
            assert pm.temp_dir == pm.session_dir / "temp"

    def test_config_saving_and_loading(self):
        """测试配置保存和加载。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建并配置路径管理器
            pm1 = ProjectPathManager(temp_dir, session_name="test")
            pm1.create_custom_dir("experiments")
            pm1.create_custom_dir("models/trained")

            # 验证配置文件存在
            config_path = pm1.session_dir / "path_config.json"
            assert config_path.exists()

            # 从配置文件加载
            pm2 = ProjectPathManager.from_config(config_path)

            assert pm2.base_dir == pm1.base_dir
            assert pm2.session_name == pm1.session_name
            assert pm2.session_dir == pm1.session_dir
            assert pm2.custom_dirs == pm1.custom_dirs

    def test_session_management(self):
        """测试会话管理。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建多个会话
            pm1 = ProjectPathManager(temp_dir, session_name="20231201_120000")
            pm2 = ProjectPathManager(temp_dir, session_name="20231202_120000")
            pm3 = ProjectPathManager(temp_dir, session_name="20231203_120000")

            sessions = pm3.list_sessions()
            assert len(sessions) >= 3
            assert "20231201_120000" in sessions
            assert "20231202_120000" in sessions
            assert "20231203_120000" in sessions

            # 测试清理旧会话
            pm3.cleanup_old_sessions(keep_count=2)
            remaining_sessions = pm3.list_sessions()
            assert len(remaining_sessions) == 2
            # 最新的两个会话应该保留
            assert "20231202_120000" in remaining_sessions
            assert "20231203_120000" in remaining_sessions

    def test_session_info(self):
        """测试会话信息。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectPathManager(temp_dir, session_name="test")
            pm.create_custom_dir("experiments")

            info = pm.get_session_info()

            assert info["session_name"] == "test"
            assert info["session_dir"] == str(pm.session_dir)
            assert info["base_dir"] == str(pm.base_dir)
            assert "experiments" in info["custom_dirs"]
            assert "total_sessions" in info

    def test_string_representations(self):
        """测试字符串表示。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectPathManager(temp_dir, session_name="test")

            str_repr = str(pm)
            assert "test" in str_repr
            assert temp_dir in str_repr

            repr_str = repr(pm)
            assert "ProjectPathManager" in repr_str
            assert "test" in repr_str


class TestGlobalPathManager:
    """测试全局路径管理器。"""

    def test_init_and_get_global_manager(self):
        """测试初始化和获取全局管理器。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 初始化全局管理器
            pm = init_project_paths(temp_dir, session_name="global_test")

            assert pm is not None
            assert pm.session_name == "global_test"

            # 获取全局管理器
            global_pm = get_project_paths()
            assert global_pm is pm

            # 测试便捷函数
            logs_path = get_project_path("logs")
            assert logs_path == pm.get_path("logs")

    def test_get_project_path_without_init(self):
        """测试未初始化时获取项目路径。"""
        # 重置全局管理器
        import my_python_project.utils.path_manager as pm_module

        pm_module._global_path_manager = None

        path = get_project_path("logs")
        assert path is None


class TestIntegrationWithLogging:
    """测试与日志系统的集成。"""

    def test_logging_integration(self):
        """测试日志系统集成。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            from my_python_project.utils.logging_utils import (
                setup_logging_with_path_manager,
                auto_setup_project_logging,
            )

            # 手动集成
            pm = ProjectPathManager(temp_dir, session_name="logging_test")
            logger = setup_logging_with_path_manager(pm, "test_module")

            assert logger is not None

            # 测试日志记录
            logger.info("测试日志消息")

            # 验证日志文件
            log_files = list(pm.logs_dir.glob("*.log"))
            assert len(log_files) > 0

    def test_auto_setup_logging(self):
        """测试自动设置日志系统。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            from my_python_project.utils.logging_utils import auto_setup_project_logging

            logger, pm = auto_setup_project_logging(temp_dir)

            assert logger is not None
            assert pm is not None
            assert pm.base_dir == Path(temp_dir).resolve()

            # 测试日志记录
            logger.info("自动设置测试")

            # 验证文件结构
            assert pm.logs_dir.exists()
            assert pm.session_dir.exists()

    def test_environment_variable_integration(self):
        """测试环境变量集成。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {"MY_PYTHON_PROJECT_BASE_DIR": temp_dir}):
                from my_python_project.utils.logging_utils import (
                    auto_setup_project_logging,
                )

                logger, pm = auto_setup_project_logging()

                assert pm.base_dir == Path(temp_dir).resolve()


class TestErrorHandling:
    """测试错误处理。"""

    def test_invalid_config_file(self):
        """测试无效配置文件。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建无效配置文件
            invalid_config = Path(temp_dir) / "invalid.json"
            invalid_config.write_text("invalid json content")

            with pytest.raises(json.JSONDecodeError):
                ProjectPathManager.from_config(invalid_config)

    def test_permission_handling(self):
        """测试权限处理。"""
        # 这个测试在实际运行时可能需要特殊权限设置
        # 在CI环境中可能会跳过
        pass

    def test_path_edge_cases(self):
        """测试路径边界情况。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectPathManager(temp_dir, session_name="edge_test")

            # 测试空路径
            with pytest.raises(ValueError):
                pm.get_path("")

            # 测试特殊字符
            special_path = pm.get_path("test-dir_with.special")
            assert special_path.exists()


class TestPerformance:
    """测试性能。"""

    def test_large_number_of_directories(self):
        """测试大量目录创建。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectPathManager(temp_dir, session_name="perf_test")

            # 创建大量目录
            import time

            start_time = time.time()

            for i in range(100):
                pm.create_custom_dir(f"test_dir_{i}")

            end_time = time.time()
            duration = end_time - start_time

            # 应该在合理时间内完成（这里设置为5秒）
            assert duration < 5.0

            # 验证所有目录都被创建
            assert len(pm.custom_dirs) >= 100

    def test_path_resolution_performance(self):
        """测试路径解析性能。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            pm = ProjectPathManager(temp_dir, session_name="perf_test")

            # 创建一些目录
            for i in range(10):
                pm.create_custom_dir(f"dir_{i}")

            # 测试大量路径解析
            import time

            start_time = time.time()

            for i in range(1000):
                path = pm.get_path(f"dir_{i % 10}")
                assert path.exists()

            end_time = time.time()
            duration = end_time - start_time

            # 路径解析应该很快
            assert duration < 1.0


if __name__ == "__main__":
    pytest.main([__file__])
