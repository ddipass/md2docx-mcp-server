"""
改进版 MD2LaTeX 转换器
自维护版本，不依赖外部 submodule
"""

import yaml
import mistune
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

from .latex_renderer import ImprovedLaTeXRenderer
from mistune.plugins.math import math
from mistune.plugins.table import table

logger = logging.getLogger(__name__)


class MD2LaTeXConverter:
    """改进版 MD2LaTeX 转换器"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.configs_path = self.base_path / "configs"
        self.templates_path = self.base_path / "templates"
        
        # 预定义配置
        self.available_configs = {
            "default": "default_config.yaml",
            "chinese": "chinese_config.yaml", 
            "academic": "academic_config.yaml"
        }
        
        # 预定义模板
        self.available_templates = {
            "basic": "basic_template.tex",
            "academic": "academic_template.tex",
            "chinese_book": "chinese_book_template.tex"
        }
    
    def load_config(self, config_name: str = "default") -> Dict[str, Any]:
        """加载配置文件"""
        if config_name in self.available_configs:
            config_file = self.configs_path / self.available_configs[config_name]
        else:
            # 尝试作为文件路径
            config_file = Path(config_name)
        
        if not config_file.exists():
            logger.warning(f"配置文件不存在: {config_file}，使用默认配置")
            config_file = self.configs_path / "default_config.yaml"
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
            
            # 如果是中文或学术配置，需要合并默认配置
            if config_name in ["chinese", "academic"]:
                default_config = self.load_config("default")
                merged_config = {**default_config, **config}
                return merged_config
            
            return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return self._get_fallback_config()
    
    def load_template(self, template_name: str = "basic") -> str:
        """加载模板文件"""
        if template_name in self.available_templates:
            template_file = self.templates_path / self.available_templates[template_name]
        else:
            # 尝试作为文件路径
            template_file = Path(template_name)
        
        if not template_file.exists():
            logger.warning(f"模板文件不存在: {template_file}，使用基础模板")
            template_file = self.templates_path / "basic_template.tex"
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"加载模板文件失败: {e}")
            return self._get_fallback_template()
    
    def convert(self, 
                markdown_content: str,
                config: Union[str, Dict[str, Any]] = "default",
                template: str = "basic",
                custom_config: Optional[Dict[str, Any]] = None) -> str:
        """
        转换 Markdown 到 LaTeX
        
        Args:
            markdown_content: Markdown 内容
            config: 配置名称或配置字典
            template: 模板名称或模板路径
            custom_config: 自定义配置（会覆盖默认配置）
            
        Returns:
            LaTeX 内容
        """
        try:
            # 加载配置
            if isinstance(config, str):
                render_config = self.load_config(config)
            else:
                render_config = config
            
            # 应用自定义配置
            if custom_config:
                render_config = {**render_config, **custom_config}
            
            # 创建渲染器
            renderer = ImprovedLaTeXRenderer(render_config)
            
            # 创建 Markdown 解析器
            markdown_parser = mistune.create_markdown(
                renderer=renderer,
                plugins=[math, table]
            )
            
            # 转换内容
            latex_content = markdown_parser(markdown_content)
            
            # 加载并应用模板
            template_content = self.load_template(template)
            final_content = template_content.replace("<!-- INSERT_CONTENT -->", latex_content)
            
            return final_content
            
        except Exception as e:
            logger.error(f"转换失败: {e}")
            raise RuntimeError(f"MD2LaTeX 转换失败: {e}")
    
    def convert_file(self,
                    input_file: Union[str, Path],
                    output_file: Optional[Union[str, Path]] = None,
                    config: Union[str, Dict[str, Any]] = "default",
                    template: str = "basic",
                    custom_config: Optional[Dict[str, Any]] = None) -> str:
        """
        转换文件
        
        Args:
            input_file: 输入 Markdown 文件
            output_file: 输出 LaTeX 文件（可选）
            config: 配置名称或配置字典
            template: 模板名称
            custom_config: 自定义配置
            
        Returns:
            输出文件路径
        """
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        
        # 读取输入文件
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
        except Exception as e:
            raise RuntimeError(f"读取输入文件失败: {e}")
        
        # 转换内容
        latex_content = self.convert(
            markdown_content=markdown_content,
            config=config,
            template=template,
            custom_config=custom_config
        )
        
        # 确定输出文件路径
        if output_file is None:
            output_path = input_path.with_suffix('.tex')
        else:
            output_path = Path(output_file)
        
        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入输出文件
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(latex_content)
        except Exception as e:
            raise RuntimeError(f"写入输出文件失败: {e}")
        
        return str(output_path)
    
    def get_available_configs(self) -> Dict[str, str]:
        """获取可用配置"""
        return self.available_configs.copy()
    
    def get_available_templates(self) -> Dict[str, str]:
        """获取可用模板"""
        return self.available_templates.copy()
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """获取后备配置"""
        return {
            "text": "<text>",
            "emphasis": "\\emph{<text>}",
            "strong": "\\textbf{<text>}",
            "paragraph": "\n<text>\n",
            "heading": "\n\\<heading_type>{<text>}",
            "list_item": "\\item <text>",
            "ordered_list": "\n\\begin{enumerate}\n<text>\n\\end{enumerate}",
            "unordered_list": "\n\\begin{itemize}\n<text>\n\\end{itemize}",
            "inline_math": "$<text>$",
            "block_math": "\n\\begin{equation}\n<text>\n\\end{equation}",
            "block_code": "\n\\begin{verbatim}\n<code>\n\\end{verbatim}",
            "codespan": "\\texttt{<text>}",
            "link": "\\href{<url>}{<text>}",
            "image": "\\includegraphics{<url>}",
            "block_quote": "\n\\begin{quote}\n<text>\n\\end{quote}",
            "thematic_break": "\\noindent\\rule{\\textwidth}{1pt}",
            "linebreak": "\\\\",
            "blank_line": "\n"
        }
    
    def _get_fallback_template(self) -> str:
        """获取后备模板"""
        return """\\documentclass[UTF8, a4paper, 12pt]{ctexart}

\\usepackage{amsmath}
\\usepackage{amssymb}
\\usepackage{graphicx}
\\usepackage{hyperref}

\\begin{document}

<!-- INSERT_CONTENT -->

\\end{document}"""
