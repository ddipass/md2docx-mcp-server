"""
MD2LaTeX 适配器 V2
使用自维护的 MD2LaTeX 版本，不再依赖外部 submodule
"""

import sys
import os
from pathlib import Path
from typing import Dict, Optional, Any, Union
import logging

logger = logging.getLogger(__name__)


class MD2LaTeXAdapterV2:
    """
    MD2LaTeX 适配器 V2
    - 使用自维护的 MD2LaTeX 版本
    - 支持多种配置和模板
    - 更好的错误处理和日志记录
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.md2latex_path = self.project_root / "md2latex"
        self.available = self._check_availability()
        
        # 支持的配置和模板
        self.supported_configs = ["default", "chinese", "academic"]
        self.supported_templates = ["basic", "academic", "chinese_book"]
        
        # 版本信息
        self.version = "2.0.0"
        self.description = "自维护版 MD2LaTeX，支持多级标题和改进的表格处理"
    
    def _check_availability(self) -> bool:
        """检查 MD2LaTeX 模块是否可用"""
        required_files = [
            "core/converter.py",
            "core/latex_renderer.py",
            "configs/default_config.yaml",
            "templates/basic_template.tex"
        ]
        
        if not self.md2latex_path.exists():
            logger.warning(f"MD2LaTeX 目录不存在: {self.md2latex_path}")
            return False
        
        missing_files = []
        for file_path in required_files:
            full_path = self.md2latex_path / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            logger.warning(f"MD2LaTeX 缺少必需文件: {missing_files}")
            return False
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """获取适配器状态"""
        return {
            "available": self.available,
            "version": self.version,
            "description": self.description,
            "md2latex_path": str(self.md2latex_path),
            "supported_configs": self.supported_configs,
            "supported_templates": self.supported_templates,
            "features": [
                "无限级别标题支持",
                "改进的表格处理", 
                "中文优化",
                "代码高亮",
                "多种模板",
                "学术论文支持"
            ]
        }
    
    def convert(self,
                markdown_content: str,
                config: str = "default",
                template: str = "basic",
                custom_config: Optional[Dict[str, Any]] = None) -> str:
        """
        转换 Markdown 到 LaTeX
        
        Args:
            markdown_content: Markdown 内容
            config: 配置名称 (default/chinese/academic)
            template: 模板名称 (basic/academic/chinese_book)
            custom_config: 自定义配置
            
        Returns:
            LaTeX 内容
        """
        if not self.available:
            raise RuntimeError("MD2LaTeX 模块不可用，请检查安装")
        
        # 添加 md2latex 路径到 Python 路径
        md2latex_str = str(self.md2latex_path)
        if md2latex_str not in sys.path:
            sys.path.insert(0, md2latex_str)
        
        try:
            from md2latex import MD2LaTeXConverter
            
            converter = MD2LaTeXConverter()
            
            # 验证配置和模板
            if config not in self.supported_configs:
                logger.warning(f"不支持的配置: {config}，使用默认配置")
                config = "default"
            
            if template not in self.supported_templates:
                logger.warning(f"不支持的模板: {template}，使用基础模板")
                template = "basic"
            
            # 执行转换
            result = converter.convert(
                markdown_content=markdown_content,
                config=config,
                template=template,
                custom_config=custom_config
            )
            
            return result
            
        except ImportError as e:
            raise RuntimeError(f"无法导入 MD2LaTeX 模块: {e}")
        except Exception as e:
            raise RuntimeError(f"转换过程出错: {e}")
    
    def convert_file(self,
                    input_file: Union[str, Path],
                    output_file: Optional[Union[str, Path]] = None,
                    config: str = "default",
                    template: str = "basic",
                    custom_config: Optional[Dict[str, Any]] = None) -> str:
        """
        转换文件
        
        Args:
            input_file: 输入 Markdown 文件
            output_file: 输出 LaTeX 文件
            config: 配置名称
            template: 模板名称
            custom_config: 自定义配置
            
        Returns:
            输出文件路径
        """
        if not self.available:
            raise RuntimeError("MD2LaTeX 模块不可用，请检查安装")
        
        # 添加 md2latex 路径到 Python 路径
        md2latex_str = str(self.md2latex_path)
        if md2latex_str not in sys.path:
            sys.path.insert(0, md2latex_str)
        
        try:
            from md2latex import MD2LaTeXConverter
            
            converter = MD2LaTeXConverter()
            
            # 验证配置和模板
            if config not in self.supported_configs:
                logger.warning(f"不支持的配置: {config}，使用默认配置")
                config = "default"
            
            if template not in self.supported_templates:
                logger.warning(f"不支持的模板: {template}，使用基础模板")
                template = "basic"
            
            # 确定输出文件路径
            if output_file is None:
                # 使用统一的 output 目录结构
                output_dir = self.project_root / "output" / "latex"
                output_dir.mkdir(parents=True, exist_ok=True)
                
                input_path = Path(input_file)
                output_file = output_dir / f"{input_path.stem}.tex"
            else:
                output_file = Path(output_file)
                # 确保输出目录存在
                output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 确保使用绝对路径
            output_file = output_file.resolve()
            
            # 执行文件转换
            result_path = converter.convert_file(
                input_file=input_file,
                output_file=str(output_file),
                config=config,
                template=template,
                custom_config=custom_config
            )
            
            return str(result_path)
            
        except ImportError as e:
            raise RuntimeError(f"无法导入 MD2LaTeX 模块: {e}")
        except Exception as e:
            raise RuntimeError(f"文件转换出错: {e}")
    
    def get_available_configs(self) -> Dict[str, str]:
        """获取可用配置"""
        return {
            "default": "默认配置，适用于一般文档",
            "chinese": "中文优化配置，适用于中文文档",
            "academic": "学术论文配置，适用于学术文档"
        }
    
    def get_available_templates(self) -> Dict[str, str]:
        """获取可用模板"""
        return {
            "basic": "基础模板，适用于一般文档",
            "academic": "学术论文模板，包含定理环境等",
            "chinese_book": "中文书籍模板，适用于长文档"
        }
    
    def test_conversion(self) -> Dict[str, Any]:
        """测试转换功能"""
        test_markdown = """# 测试标题

这是一个测试文档。

## 二级标题

包含**粗体**和*斜体*文本。

### 三级标题

- 列表项 1
- 列表项 2

#### 四级标题

数学公式：$E = mc^2$

##### 五级标题

```python
print("Hello, World!")
```

###### 六级标题

测试完成。
"""
        
        results = {}
        
        for config in self.supported_configs:
            for template in self.supported_templates:
                try:
                    result = self.convert(test_markdown, config, template)
                    results[f"{config}_{template}"] = {
                        "status": "success",
                        "length": len(result),
                        "config": config,
                        "template": template
                    }
                except Exception as e:
                    results[f"{config}_{template}"] = {
                        "status": "failed",
                        "error": str(e),
                        "config": config,
                        "template": template
                    }
        
        return results


# 向后兼容的别名
class MD2LaTeXAdapter(MD2LaTeXAdapterV2):
    """向后兼容的别名"""
    pass


# 管理器类（保持兼容性）
class UpstreamManager:
    """上游管理器（兼容性类）"""
    
    def __init__(self):
        self.adapter = MD2LaTeXAdapterV2()
    
    def check_updates(self) -> Dict[str, Any]:
        """检查更新（自维护版本无需更新）"""
        return {
            "status": "self_maintained",
            "message": "当前使用自维护版本，无需检查上游更新",
            "version": self.adapter.version,
            "last_update": "2024-08-13"
        }
    
    def update(self) -> Dict[str, Any]:
        """更新（自维护版本无需更新）"""
        return {
            "status": "self_maintained",
            "message": "当前使用自维护版本，请手动更新代码",
            "version": self.adapter.version
        }
