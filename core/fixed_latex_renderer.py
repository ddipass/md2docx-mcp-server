"""
修复版本的 LaTeX 渲染器
解决标题级别索引越界问题
"""

import sys
from pathlib import Path

# 添加上游路径
upstream_path = Path(__file__).parent.parent / "md2latex" / "Tool"
sys.path.insert(0, str(upstream_path))

from LaTeXRenderer import LaTeXRender

class FixedLaTeXRender(LaTeXRender):
    """
    修复版本的 LaTeX 渲染器
    主要修复：标题级别索引越界问题
    """
    
    def heading(self, text: str, level: int, **attrs) -> str:
        """
        修复版本的标题处理
        支持更多级别的标题
        """
        # 扩展标题类型，支持更多级别
        heading_types = [
            'section',           # level 1: #
            'subsection',        # level 2: ##  
            'subsubsection',     # level 3: ###
            'paragraph',         # level 4: ####
            'subparagraph',      # level 5: #####
            'subparagraph'       # level 6+: 使用 subparagraph
        ]
        
        t = self.my_config["heading"]
        t = t.replace("<text>", text)
        
        # 安全的索引访问，防止越界
        if level <= len(heading_types):
            heading_type = heading_types[level - 1]
        else:
            # 超出范围的标题使用最后一个类型
            heading_type = heading_types[-1]
            
        t = t.replace("<heading_types>", heading_type)
        return t
