#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
项目路径管理模块

提供统一的项目路径管理功能，包括：
1. 基于时间戳的会话目录管理
2. 标准项目目录结构
3. 日志系统集成
4. 自定义路径支持
5. 唯一文件名生成
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union, List
import json


class ProjectPathManager:
    """
    项目路径管理器
    
    为每个项目运行创建基于时间戳的会话目录，并管理所有相关路径。
    集成日志系统，提供标准的项目目录结构。
    
    特性:
    - 每次运行自动创建时间戳目录
    - 标准项目目录结构（logs, reports, data等）
    - 日志系统深度集成
    - 支持自定义目录和文件创建
    - 路径配置持久化
    - 唯一文件名生成
    
    示例:
        # 创建路径管理器
        pm = ProjectPathManager("/var/data/myproject")
        
        # 获取当前会话的日志路径
        log_path = pm.get_log_path("application.log")
        
        # 创建自定义目录
        pm.create_custom_dir("models/trained")
        model_path = pm.get_custom_path("models/trained", "model.pkl")
    """
    
    def __init__(
        self, 
        base_dir: Union[str, Path],
        session_name: Optional[str] = None,
        auto_create_session: bool = True,
        standard_dirs: Optional[List[str]] = None,
        config_file: Optional[str] = "path_config.json"
    ):
        """
        初始化项目路径管理器
        
        Args:
            base_dir: 项目基础目录
            session_name: 会话名称，默认使用时间戳
            auto_create_session: 是否自动创建会话目录
            standard_dirs: 标准目录列表，None则使用默认
            config_file: 配置文件名，None则不保存配置
        """
        self.base_dir = Path(base_dir).resolve()
        self.config_file = config_file
        
        # 生成会话名称（时间戳目录）
        if session_name is None:
            session_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_name = session_name
        
        # 会话目录
        self.session_dir = self.base_dir / session_name
        
        # 标准目录结构
        if standard_dirs is None:
            standard_dirs = [
                "logs",        # 日志文件
                "reports",     # 报告文件  
                "data",        # 数据文件
                "downloads",   # 下载文件
                "uploads",     # 上传文件
                "temp",        # 临时文件
                "output",      # 输出文件
                "input",       # 输入文件
                "config",      # 配置文件
                "cache",       # 缓存文件
                "backup",      # 备份文件
                "models",      # 模型文件
                "images",      # 图片文件
                "documents",   # 文档文件
                "scripts",     # 脚本文件
                "results"      # 结果文件
            ]
        
        self.standard_dirs = standard_dirs
        self.custom_dirs = {}  # 用户自定义目录
        
        # 创建目录结构
        if auto_create_session:
            self._create_directory_structure()
            
        # 保存配置
        if config_file:
            self._save_config()
            
        # 获取日志记录器
        self.logger = logging.getLogger(f"my_python_project.path_manager")
        self.logger.info(f"项目路径管理器初始化完成")
        self.logger.info(f"基础目录: {self.base_dir}")
        self.logger.info(f"会话目录: {self.session_dir}")
    
    def _create_directory_structure(self):
        """创建标准目录结构"""
        # 确保基础目录存在
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建会话目录
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建标准目录
        for dir_name in self.standard_dirs:
            dir_path = self.session_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _save_config(self):
        """保存路径配置到文件"""
        config = {
            "base_dir": str(self.base_dir),
            "session_name": self.session_name,
            "session_dir": str(self.session_dir),
            "standard_dirs": self.standard_dirs,
            "custom_dirs": {k: str(v) for k, v in self.custom_dirs.items()},
            "created_at": datetime.now().isoformat(),
            "project_name": "my_python_project"
        }
        
        config_path = self.session_dir / self.config_file
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def from_config(cls, config_path: Union[str, Path]) -> 'ProjectPathManager':
        """从配置文件加载路径管理器"""
        config_path = Path(config_path)
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        pm = cls(
            base_dir=config["base_dir"],
            session_name=config["session_name"],
            auto_create_session=False,
            standard_dirs=config["standard_dirs"],
            config_file=None
        )
        
        # 恢复自定义目录
        for name, path in config["custom_dirs"].items():
            pm.custom_dirs[name] = Path(path)
        
        return pm
    
    def get_path(self, path_type: str) -> Path:
        """
        获取指定类型的路径
        
        Args:
            path_type: 路径类型，支持:
                     - 标准目录名: 'logs', 'reports', 'data'等
                     - 嵌套路径: 'data/processed', 'models/trained'
                     - 自定义路径: 用户通过create_custom_dir创建的路径
                     
        Returns:
            路径对象
            
        示例:
            logs_dir = pm.get_path("logs")
            nested_dir = pm.get_path("data/processed") 
            custom_dir = pm.get_path("my_custom_dir")
        """
        # 检查是否为嵌套路径
        if "/" in path_type:
            parts = path_type.split("/")
            base_part = parts[0]
            sub_parts = parts[1:]
            
            # 基础部分必须是标准目录或自定义目录
            if base_part in self.standard_dirs:
                base_path = self.session_dir / base_part
            elif base_part in self.custom_dirs:
                base_path = self.custom_dirs[base_part]
            else:
                # 创建新的自定义目录
                base_path = self.session_dir / base_part
                self.custom_dirs[base_part] = base_path
            
            # 构建完整路径
            full_path = base_path / Path(*sub_parts)
            full_path.mkdir(parents=True, exist_ok=True)
            return full_path
        
        # 检查标准目录
        if path_type in self.standard_dirs:
            return self.session_dir / path_type
        
        # 检查自定义目录
        if path_type in self.custom_dirs:
            return self.custom_dirs[path_type]
        
        # 创建新的自定义目录
        new_path = self.session_dir / path_type
        new_path.mkdir(parents=True, exist_ok=True)
        self.custom_dirs[path_type] = new_path
        
        # 更新配置
        if self.config_file:
            self._save_config()
        
        return new_path
    
    def get_file_path(self, path_type: str, filename: str) -> Path:
        """
        获取指定目录下的文件路径
        
        Args:
            path_type: 路径类型
            filename: 文件名
            
        Returns:
            完整文件路径
        """
        return self.get_path(path_type) / filename
    
    def get_unique_filename(self, path_type: str, filename: str) -> Path:
        """
        获取唯一的文件路径，避免重名
        
        Args:
            path_type: 路径类型
            filename: 文件名
            
        Returns:
            唯一的文件路径
        """
        base_path = self.get_path(path_type)
        file_path = Path(filename)
        name_part = file_path.stem
        ext_part = file_path.suffix
        
        # 尝试使用原始文件名
        full_path = base_path / filename
        if not full_path.exists():
            return full_path
        
        # 如果文件已存在，添加时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # 精确到毫秒
        new_filename = f"{name_part}_{timestamp}{ext_part}"
        return base_path / new_filename
    
    def create_custom_dir(self, dir_name: str) -> Path:
        """
        创建自定义目录
        
        Args:
            dir_name: 目录名称，支持嵌套路径
            
        Returns:
            创建的目录路径
            
        示例:
            pm.create_custom_dir("models/trained")
            pm.create_custom_dir("experiments/exp001")
        """
        if "/" in dir_name:
            # 嵌套路径
            dir_path = self.session_dir / dir_name
        else:
            # 简单路径
            dir_path = self.session_dir / dir_name
            
        dir_path.mkdir(parents=True, exist_ok=True)
        self.custom_dirs[dir_name] = dir_path
        
        # 更新配置
        if self.config_file:
            self._save_config()
        
        self.logger.info(f"创建自定义目录: {dir_path}")
        return dir_path
    
    def get_custom_path(self, dir_name: str, filename: str = None) -> Path:
        """
        获取自定义目录路径或文件路径
        
        Args:
            dir_name: 自定义目录名称
            filename: 文件名（可选）
            
        Returns:
            目录路径或文件路径
        """
        if dir_name not in self.custom_dirs:
            self.create_custom_dir(dir_name)
        
        dir_path = self.custom_dirs[dir_name]
        
        if filename:
            return dir_path / filename
        return dir_path
    
    # 特定类型的路径获取方法
    def get_log_path(self, log_name: str) -> Path:
        """获取日志文件路径"""
        if not log_name.endswith('.log'):
            log_name = f"{log_name}.log"
        return self.get_unique_filename("logs", log_name)
    
    def get_report_path(self, report_name: str, format: str = "docx") -> Path:
        """获取报告文件路径"""
        if not report_name.endswith(f'.{format}'):
            report_name = f"{report_name}.{format}"
        return self.get_unique_filename("reports", report_name)
    
    def get_data_path(self, data_name: str) -> Path:
        """获取数据文件路径"""
        return self.get_unique_filename("data", data_name)
    
    def get_model_path(self, model_name: str) -> Path:
        """获取模型文件路径"""
        return self.get_unique_filename("models", model_name)
    
    def get_output_path(self, output_name: str) -> Path:
        """获取输出文件路径"""
        return self.get_unique_filename("output", output_name)
    
    def get_temp_path(self, temp_name: str) -> Path:
        """获取临时文件路径"""
        return self.get_unique_filename("temp", temp_name)
    
    def get_image_path(self, image_type: str, filename: str) -> Path:
        """
        获取图片文件路径
        
        Args:
            image_type: 图片类型/子目录
            filename: 图片文件名
            
        Returns:
            图片文件路径
        """
        return self.get_file_path(f"images/{image_type}", filename)
    
    # 便捷属性
    @property
    def logs_dir(self) -> Path:
        """日志目录"""
        return self.get_path("logs")
    
    @property
    def reports_dir(self) -> Path:
        """报告目录"""
        return self.get_path("reports")
    
    @property
    def data_dir(self) -> Path:
        """数据目录"""
        return self.get_path("data")
    
    @property
    def models_dir(self) -> Path:
        """模型目录"""
        return self.get_path("models")
    
    @property
    def output_dir(self) -> Path:
        """输出目录"""
        return self.get_path("output")
    
    @property
    def temp_dir(self) -> Path:
        """临时目录"""
        return self.get_path("temp")
    
    # 会话管理
    def list_sessions(self) -> List[str]:
        """列出所有会话目录"""
        if not self.base_dir.exists():
            return []
        
        sessions = []
        for item in self.base_dir.iterdir():
            if item.is_dir() and item.name.replace("_", "").replace("-", "").isdigit():
                sessions.append(item.name)
        
        return sorted(sessions, reverse=True)  # 最新的在前
    
    def get_session_dir(self, session_name: str = None) -> Path:
        """获取指定会话的目录"""
        if session_name is None:
            return self.session_dir
        return self.base_dir / session_name
    
    def cleanup_old_sessions(self, keep_count: int = 10):
        """清理旧的会话目录，保留最新的几个"""
        sessions = self.list_sessions()
        
        if len(sessions) <= keep_count:
            return
        
        # 删除旧的会话目录
        sessions_to_delete = sessions[keep_count:]
        for session_name in sessions_to_delete:
            session_path = self.base_dir / session_name
            if session_path.exists() and session_path != self.session_dir:
                import shutil
                shutil.rmtree(session_path)
                self.logger.info(f"清理旧会话目录: {session_path}")
    
    def get_session_info(self) -> Dict:
        """获取当前会话信息"""
        return {
            "session_name": self.session_name,
            "session_dir": str(self.session_dir),
            "base_dir": str(self.base_dir),
            "standard_dirs": self.standard_dirs,
            "custom_dirs": {k: str(v) for k, v in self.custom_dirs.items()},
            "total_sessions": len(self.list_sessions())
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"ProjectPathManager(session='{self.session_name}', base='{self.base_dir}')"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return (f"ProjectPathManager(base_dir='{self.base_dir}', "
                f"session_name='{self.session_name}', "
                f"standard_dirs={len(self.standard_dirs)}, "
                f"custom_dirs={len(self.custom_dirs)})")


# 全局路径管理器实例（可选）
_global_path_manager: Optional[ProjectPathManager] = None


def init_project_paths(
    base_dir: Union[str, Path],
    session_name: Optional[str] = None,
    **kwargs
) -> ProjectPathManager:
    """
    初始化全局项目路径管理器
    
    Args:
        base_dir: 项目基础目录
        session_name: 会话名称
        **kwargs: 其他传递给ProjectPathManager的参数
        
    Returns:
        项目路径管理器实例
    """
    global _global_path_manager
    _global_path_manager = ProjectPathManager(base_dir, session_name, **kwargs)
    return _global_path_manager


def get_project_paths() -> Optional[ProjectPathManager]:
    """获取全局项目路径管理器"""
    return _global_path_manager


def get_project_path(path_type: str) -> Optional[Path]:
    """获取项目路径（便捷函数）"""
    if _global_path_manager:
        return _global_path_manager.get_path(path_type)
    return None