"""
MD2LaTeX 适配器层
封装 VMIJUNV/md-to-latex 项目，提供统一接口
"""

import sys
import os
import yaml
import subprocess
from pathlib import Path
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class MD2LaTeXAdapter:
    """
    适配器层：封装 VMIJUNV/md-to-latex 项目
    - 处理版本兼容性
    - 提供统一的调用接口
    - 隔离上游变更影响
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.upstream_path = self.project_root / "md2latex"
        self.upstream_tool_path = self.upstream_path / "Tool"
        self.upstream_available = self._check_upstream()
        
        # 版本兼容性信息
        self.supported_versions = {
            "2.0": "full_support",
            "1.x": "limited_support"
        }
    
    def _check_upstream(self) -> bool:
        """检查上游项目是否可用"""
        required_files = [
            "Tool/LaTeXRenderer.py",
            "Tool/md_to_latex.py", 
            "Tool/default_convert_config.yaml",
            "Tool/default_convert_template.txt"
        ]
        
        if not self.upstream_path.exists():
            logger.warning(f"上游项目目录不存在: {self.upstream_path}")
            return False
        
        missing_files = []
        for file_path in required_files:
            if not (self.upstream_path / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            logger.warning(f"上游项目缺少必需文件: {missing_files}")
            return False
        
        return True
    
    def get_upstream_version(self) -> str:
        """获取上游项目版本信息"""
        try:
            # 尝试从 git 获取版本信息
            result = subprocess.run(
                ["git", "describe", "--tags", "--always"],
                cwd=self.upstream_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                # 如果没有 git 信息，尝试从其他地方获取
                return "unknown"
        except Exception as e:
            logger.warning(f"无法获取上游版本信息: {e}")
            return "unknown"
    
    def check_compatibility(self, version: str = None) -> str:
        """检查版本兼容性"""
        if version is None:
            version = self.get_upstream_version()
        
        for supported_ver, level in self.supported_versions.items():
            if version.startswith(supported_ver.replace('.x', '')):
                return level
        
        return "unknown"
    
    def convert_basic(self, 
                     md_content: str, 
                     config: Optional[Dict] = None,
                     template: Optional[str] = None) -> str:
        """
        基础转换功能（使用上游代码）
        
        Args:
            md_content: Markdown 内容
            config: 转换配置（可选）
            template: 模板内容（可选）
            
        Returns:
            转换后的 LaTeX 内容
        """
        if not self.upstream_available:
            raise RuntimeError("上游 md2latex 项目不可用，请检查 submodule 是否正确初始化")
        
        # 临时添加上游路径到 Python 路径
        upstream_tool_str = str(self.upstream_tool_path)
        if upstream_tool_str not in sys.path:
            sys.path.insert(0, upstream_tool_str)
        
        try:
            # 动态导入上游模块
            from LaTeXRenderer import LaTeXRender
            import mistune
            from mistune.plugins.math import math
            from mistune.plugins.table import table
            
            # 加载默认配置
            default_config = self._load_default_config()
            if config:
                # 合并自定义配置
                merged_config = {**default_config, **config}
            else:
                merged_config = default_config
            
            # 创建渲染器
            renderer = LaTeXRender(my_config=merged_config)
            markdown_parser = mistune.create_markdown(
                renderer=renderer, 
                plugins=[math, table]
            )
            
            # 转换 Markdown 到 LaTeX
            latex_content = markdown_parser(md_content)
            
            # 如果提供了模板，应用模板
            if template:
                latex_content = template.replace("<!-- Insert -->", latex_content)
            else:
                # 使用默认模板
                default_template = self._load_default_template()
                latex_content = default_template.replace("<!-- Insert -->", latex_content)
            
            return latex_content
            
        except ImportError as e:
            raise RuntimeError(f"无法导入上游模块: {e}")
        except Exception as e:
            raise RuntimeError(f"转换过程出错: {e}")
        finally:
            # 清理 Python 路径
            if upstream_tool_str in sys.path:
                sys.path.remove(upstream_tool_str)
    
    def _load_default_config(self) -> Dict:
        """加载默认配置"""
        config_file = self.upstream_tool_path / "default_convert_config.yaml"
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"无法加载默认配置: {e}")
            return {}
    
    def _load_default_template(self) -> str:
        """加载默认模板"""
        template_file = self.upstream_tool_path / "default_convert_template.txt"
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"无法加载默认模板: {e}")
            return "<!-- Insert -->"  # 最简模板
    
    def get_status(self) -> Dict[str, Any]:
        """获取适配器状态信息"""
        return {
            "upstream_available": self.upstream_available,
            "upstream_path": str(self.upstream_path),
            "upstream_version": self.get_upstream_version(),
            "compatibility": self.check_compatibility(),
            "required_files_exist": self._check_upstream()
        }

class UpstreamManager:
    """上游项目管理器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.upstream_path = self.project_root / "md2latex"
    
    def check_upstream_updates(self) -> bool:
        """检查上游是否有更新"""
        try:
            # 获取远程更新
            subprocess.run(
                ["git", "fetch", "origin"],
                cwd=self.upstream_path,
                check=True,
                capture_output=True
            )
            
            # 检查是否有新的提交
            result = subprocess.run(
                ["git", "rev-list", "HEAD...origin/main", "--count"],
                cwd=self.upstream_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                count = int(result.stdout.strip())
                return count > 0
            
        except Exception as e:
            logger.error(f"检查上游更新失败: {e}")
        
        return False
    
    def update_upstream(self) -> bool:
        """更新上游项目"""
        try:
            # 更新 submodule
            result = subprocess.run(
                ["git", "submodule", "update", "--remote", "md2latex"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # 测试兼容性
                return self._test_compatibility()
            else:
                logger.error(f"上游更新失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"上游更新异常: {e}")
            return False
    
    def _test_compatibility(self) -> bool:
        """测试兼容性"""
        try:
            # 创建适配器实例进行测试
            adapter = MD2LaTeXAdapter()
            
            # 简单的兼容性测试
            test_md = "# 测试标题\n\n这是一个测试段落。"
            result = adapter.convert_basic(test_md)
            
            # 检查结果是否包含预期的 LaTeX 内容
            return "\\section{测试标题}" in result and "这是一个测试段落" in result
            
        except Exception as e:
            logger.error(f"兼容性测试失败: {e}")
            return False
    
    def get_update_status(self) -> Dict[str, Any]:
        """获取更新状态"""
        return {
            "has_updates": self.check_upstream_updates(),
            "current_version": MD2LaTeXAdapter().get_upstream_version(),
            "last_check": "now"  # 可以添加时间戳
        }
