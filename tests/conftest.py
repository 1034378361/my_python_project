"""Pytest配置文件。"""

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """提供临时目录供测试使用。"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_data():
    """提供测试用的样例数据。"""
    return {
        "name": "test",
        "value": 42,
        "items": ["a", "b", "c"],
        "nested": {"key": "value"},
    }


@pytest.fixture
def sample_file(temp_dir, sample_data):
    """创建测试用的样例文件。"""
    import json

    file_path = temp_dir / "sample.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(sample_data, f)

    return file_path
