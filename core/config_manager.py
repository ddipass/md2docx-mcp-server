"""
配置管理器 - 管理 MD2DOCX MCP 服务器的配置
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ConversionSettings:
    """转换设置"""
    debug_mode: bool = False
    output_dir: str = "output"
    preserve_structure: bool = True
    auto_timestamp: bool = True  # 文件被占用时自动添加时间戳
    max_retry_attempts: int = 5


@dataclass
class BatchSettings:
    """批量转换设置"""
    parallel_jobs: int = 4
    skip_existing: bool = False
    create_log: bool = True
    log_level: str = "INFO"


@dataclass
class FileSettings:
    """文件处理设置"""
    supported_extensions: list = None
    output_extension: str = ".docx"
    encoding: str = "utf-8"
    
    def __post_init__(self):
        if self.supported_extensions is None:
            self.supported_extensions = [".md", ".markdown", ".txt"]


@dataclass
class ServerSettings:
    """服务器设置"""
    md2docx_project_path: str = "md2docx"  # 使用相对路径，指向内置的submodule
    use_subprocess: bool = True  # 是否使用子进程调用
    use_python_import: bool = False  # 是否直接导入 Python 模块


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config/converter_config.json"
        self.config_path = Path(self.config_file)
        
        # 默认配置
        self.conversion_settings = ConversionSettings()
        self.batch_settings = BatchSettings()
        self.file_settings = FileSettings()
        self.server_settings = ServerSettings()
        
        # 加载配置
        self.load_config()
    
    def load_config(self) -> None:
        """加载配置文件"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 更新配置
                if 'conversion_settings' in config_data:
                    self.conversion_settings = ConversionSettings(**config_data['conversion_settings'])
                
                if 'batch_settings' in config_data:
                    self.batch_settings = BatchSettings(**config_data['batch_settings'])
                
                if 'file_settings' in config_data:
                    self.file_settings = FileSettings(**config_data['file_settings'])
                
                if 'server_settings' in config_data:
                    self.server_settings = ServerSettings(**config_data['server_settings'])
                
                print(f"✅ 配置已从 {self.config_path} 加载")
            except Exception as e:
                print(f"⚠️  配置文件加载失败，使用默认配置: {e}")
        else:
            print(f"ℹ️  配置文件不存在，使用默认配置: {self.config_path}")
            self.save_config()  # 创建默认配置文件
    
    def save_config(self) -> None:
        """保存配置文件"""
        # 确保配置目录存在
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_data = {
            'conversion_settings': asdict(self.conversion_settings),
            'batch_settings': asdict(self.batch_settings),
            'file_settings': asdict(self.file_settings),
            'server_settings': asdict(self.server_settings)
        }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"✅ 配置已保存到 {self.config_path}")
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
    
    def update_conversion_settings(self, **kwargs) -> None:
        """更新转换设置"""
        for key, value in kwargs.items():
            if hasattr(self.conversion_settings, key):
                setattr(self.conversion_settings, key, value)
        self.save_config()
    
    def update_batch_settings(self, **kwargs) -> None:
        """更新批量设置"""
        for key, value in kwargs.items():
            if hasattr(self.batch_settings, key):
                setattr(self.batch_settings, key, value)
        self.save_config()
    
    def update_file_settings(self, **kwargs) -> None:
        """更新文件设置"""
        for key, value in kwargs.items():
            if hasattr(self.file_settings, key):
                setattr(self.file_settings, key, value)
        self.save_config()
    
    def update_server_settings(self, **kwargs) -> None:
        """更新服务器设置"""
        for key, value in kwargs.items():
            if hasattr(self.server_settings, key):
                setattr(self.server_settings, key, value)
        self.save_config()
    
    def get_config_summary(self) -> str:
        """获取配置摘要"""
        return f"""
📋 MD2DOCX MCP 服务器配置摘要

🔧 转换设置:
- 调试模式: {self.conversion_settings.debug_mode}
- 输出目录: {self.conversion_settings.output_dir}
- 保持结构: {self.conversion_settings.preserve_structure}
- 自动时间戳: {self.conversion_settings.auto_timestamp}
- 最大重试次数: {self.conversion_settings.max_retry_attempts}

📦 批量设置:
- 并行任务数: {self.batch_settings.parallel_jobs}
- 跳过已存在: {self.batch_settings.skip_existing}
- 创建日志: {self.batch_settings.create_log}
- 日志级别: {self.batch_settings.log_level}

📁 文件设置:
- 支持扩展名: {', '.join(self.file_settings.supported_extensions)}
- 输出扩展名: {self.file_settings.output_extension}
- 文件编码: {self.file_settings.encoding}

🖥️  服务器设置:
- MD2DOCX 项目路径: {self.server_settings.md2docx_project_path}
- 使用子进程: {self.server_settings.use_subprocess}
- 使用 Python 导入: {self.server_settings.use_python_import}
"""

    def reset_to_defaults(self) -> None:
        """重置为默认配置"""
        self.conversion_settings = ConversionSettings()
        self.batch_settings = BatchSettings()
        self.file_settings = FileSettings()
        self.server_settings = ServerSettings()
        self.save_config()


# 全局配置实例
_config_manager = None

def get_config_manager() -> ConfigManager:
    """获取配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def reload_config() -> ConfigManager:
    """重新加载配置"""
    global _config_manager
    _config_manager = ConfigManager()
    return _config_manager
