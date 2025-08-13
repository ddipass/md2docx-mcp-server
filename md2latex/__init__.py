"""
改进版 MD2LaTeX 包
自维护版本，基于 VMIJUNV/md-to-latex 但进行了大幅改进

主要改进：
1. 支持无限级别标题
2. 改进的表格处理
3. 更好的中文支持
4. 代码高亮支持
5. 多种模板和配置
6. 更好的错误处理
"""

from .core.converter import MD2LaTeXConverter
from .core.latex_renderer import ImprovedLaTeXRenderer

__version__ = "2.0.0"
__author__ = "MD2DOCX-MCP-Server Team"

# 便捷导入
def convert_markdown_to_latex(markdown_content: str, 
                            config: str = "default",
                            template: str = "basic") -> str:
    """便捷转换函数"""
    converter = MD2LaTeXConverter()
    return converter.convert(markdown_content, config, template)

def convert_file_to_latex(input_file: str,
                         output_file: str = None,
                         config: str = "default", 
                         template: str = "basic") -> str:
    """便捷文件转换函数"""
    converter = MD2LaTeXConverter()
    return converter.convert_file(input_file, output_file, config, template)

__all__ = [
    'MD2LaTeXConverter',
    'ImprovedLaTeXRenderer', 
    'convert_markdown_to_latex',
    'convert_file_to_latex'
]
