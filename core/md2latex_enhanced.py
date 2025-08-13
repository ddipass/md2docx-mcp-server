"""
MD2LaTeX 增强功能层
在适配器基础上添加定制功能
"""

import re
import yaml
from pathlib import Path
from typing import Dict, Optional, List
import logging

from .md2latex_adapter import MD2LaTeXAdapter

logger = logging.getLogger(__name__)

class MD2LaTeXEnhanced:
    """
    增强功能层：在上游基础上添加定制功能
    - 中文优化处理
    - 复杂表格支持
    - 交叉引用功能
    - 与 Open_Data_Book 项目集成
    """
    
    def __init__(self):
        self.adapter = MD2LaTeXAdapter()
        self.project_root = Path(__file__).parent.parent
        self.templates_dir = self.project_root / "templates" / "latex"
        self.configs_dir = self.templates_dir / "configs"
        
        # 确保目录存在
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.configs_dir.mkdir(parents=True, exist_ok=True)
    
    def convert_with_chinese_optimization(self, 
                                        md_content: str,
                                        template_name: str = "article") -> str:
        """中文优化转换"""
        
        # 预处理：中文标点、间距等
        processed_content = self._preprocess_chinese(md_content)
        
        # 获取中文优化配置
        chinese_config = self._get_chinese_config()
        
        # 获取模板
        template_content = self._get_template(template_name)
        
        # 使用适配器进行基础转换
        latex_content = self.adapter.convert_basic(
            processed_content, 
            chinese_config,
            template_content
        )
        
        # 后处理：中文特殊格式
        return self._postprocess_chinese(latex_content)
    
    def convert_with_ctexbook_template(self, 
                                     md_content: str,
                                     chapter_title: Optional[str] = None) -> str:
        """使用 ctexbook 模板转换（基于 Open_Data_Book）"""
        
        # 预处理内容
        processed_content = self._preprocess_for_book(md_content, chapter_title)
        
        # 获取学术书籍配置
        academic_config = self._get_academic_config()
        
        # 获取 ctexbook 模板
        ctexbook_template = self._get_ctexbook_template()
        
        # 转换并应用模板
        latex_content = self.adapter.convert_basic(
            processed_content, 
            academic_config,
            ctexbook_template
        )
        
        return self._postprocess_for_book(latex_content)
    
    def convert_with_enhanced_features(self, 
                                     md_content: str,
                                     template_name: str = "enhanced",
                                     enable_cross_ref: bool = True,
                                     enable_bibliography: bool = True) -> str:
        """使用增强功能转换"""
        
        # 预处理：添加增强功能支持
        processed_content = self._preprocess_enhanced(
            md_content, 
            enable_cross_ref, 
            enable_bibliography
        )
        
        # 获取增强配置
        enhanced_config = self._get_enhanced_config()
        
        # 获取增强模板
        enhanced_template = self._get_enhanced_template()
        
        # 转换
        latex_content = self.adapter.convert_basic(
            processed_content,
            enhanced_config,
            enhanced_template
        )
        
        return self._postprocess_enhanced(latex_content)
    
    def _preprocess_chinese(self, content: str) -> str:
        """中文预处理"""
        
        # 中文标点符号优化
        content = re.sub(r'，\s+', '，', content)  # 去除逗号后多余空格
        content = re.sub(r'。\s+', '。', content)  # 去除句号后多余空格
        content = re.sub(r'；\s+', '；', content)  # 去除分号后多余空格
        
        # 中英文混排间距优化
        content = re.sub(r'([a-zA-Z0-9])\s*([，。；：！？])', r'\1\2', content)
        content = re.sub(r'([，。；：！？])\s*([a-zA-Z0-9])', r'\1 \2', content)
        
        # 引号优化
        content = re.sub(r'"([^"]*)"', r'"\1"', content)  # 英文引号转中文引号
        
        return content
    
    def _postprocess_chinese(self, latex_content: str) -> str:
        """中文后处理"""
        
        # 修复标题层次问题
        latex_content = re.sub(r'\\section\{([^}]*)\}([^\\]*?)##\s*([^\\#]*?)\\', 
                              r'\\section{\1}\n\n\2\n\n\\section{\3}\\', latex_content)
        
        # 修复段落格式
        latex_content = re.sub(r'([^\\])\s*##\s*([^\\]*?)\s*\\', r'\1\n\n\\section{\2}\n\n\\', latex_content)
        latex_content = re.sub(r'([^\\])\s*###\s*([^\\]*?)\s*\\', r'\1\n\n\\subsection{\2}\n\n\\', latex_content)
        
        # 修复列表格式
        latex_content = re.sub(r'(\d+\.\s+[^\n]*\n?)+', self._fix_ordered_list, latex_content)
        
        # 添加中文字体设置（如果需要）
        if '\\documentclass' in latex_content and 'ctex' not in latex_content:
            latex_content = latex_content.replace(
                '\\documentclass{article}',
                '\\documentclass[UTF8]{ctexart}'
            )
        
        return latex_content
    
    def _fix_ordered_list(self, match) -> str:
        """修复有序列表格式"""
        text = match.group(0)
        items = re.findall(r'\d+\.\s+([^\n]*)', text)
        
        if items:
            latex_items = '\n'.join([f'  \\item {item}' for item in items])
            return f'\n\\begin{{enumerate}}\n{latex_items}\n\\end{{enumerate}}\n'
        
        return text
    
    def _preprocess_for_book(self, content: str, chapter_title: Optional[str]) -> str:
        """书籍格式预处理"""
        
        # 如果指定了章节标题，添加到开头
        if chapter_title:
            content = f"# {chapter_title}\n\n{content}"
        
        # 确保一级标题作为章节
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            # 将一级标题转换为章节格式
            if line.startswith('# '):
                title = line[2:].strip()
                processed_lines.append(f"# {title}")
            else:
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _preprocess_enhanced(self, 
                           content: str, 
                           enable_cross_ref: bool,
                           enable_bibliography: bool) -> str:
        """增强功能预处理"""
        
        if enable_cross_ref:
            # 添加交叉引用支持
            content = self._add_cross_reference_support(content)
        
        if enable_bibliography:
            # 添加参考文献支持
            content = self._add_bibliography_support(content)
        
        return content
    
    def _add_cross_reference_support(self, content: str) -> str:
        """添加交叉引用支持"""
        
        # 为图片添加标签
        content = re.sub(
            r'!\[([^\]]*)\]\(([^)]*)\s*"([^"]*)"\)',
            r'![图 \1](\2 "\3")\n\\label{fig:\3}',
            content
        )
        
        # 为表格添加标签（简单实现）
        content = re.sub(
            r'\|([^|]*)\|([^|]*)\|',
            r'|\1|\2|',
            content
        )
        
        return content
    
    def _add_bibliography_support(self, content: str) -> str:
        """添加参考文献支持"""
        
        # 在文档末尾添加参考文献
        if not content.endswith('\n'):
            content += '\n'
        
        content += '''
## 参考文献

```latex
\\bibliographystyle{plain}
\\bibliography{references}
```
'''
        
        return content
    
    def _postprocess_chinese(self, latex_content: str) -> str:
        """中文后处理"""
        
        # LaTeX 中文优化
        latex_content = re.sub(r'\\section\{([^}]*)\}', r'\\section{\1}', latex_content)
        
        # 添加中文字体设置（如果需要）
        if '\\documentclass' in latex_content and 'ctex' not in latex_content:
            latex_content = latex_content.replace(
                '\\documentclass{article}',
                '\\documentclass[UTF8]{ctexart}'
            )
        
        return latex_content
    
    def _postprocess_for_book(self, latex_content: str) -> str:
        """书籍格式后处理"""
        
        # 将 section 转换为 chapter（如果使用 book 类）
        if '\\documentclass{book}' in latex_content or '\\documentclass{ctexbook}' in latex_content:
            latex_content = re.sub(r'\\section\{', r'\\chapter{', latex_content)
            latex_content = re.sub(r'\\subsection\{', r'\\section{', latex_content)
            latex_content = re.sub(r'\\subsubsection\{', r'\\subsection{', latex_content)
        
        return latex_content
    
    def _postprocess_enhanced(self, latex_content: str) -> str:
        """增强功能后处理"""
        
        # 添加必要的宏包
        packages_to_add = [
            '\\usepackage{hyperref}',
            '\\usepackage{cleveref}',
            '\\usepackage{natbib}'
        ]
        
        for package in packages_to_add:
            if package not in latex_content and '\\usepackage' in latex_content:
                latex_content = latex_content.replace(
                    '\\usepackage{graphicx}',
                    f'\\usepackage{{graphicx}}\n{package}'
                )
        
        return latex_content
    
    def _get_chinese_config(self) -> Dict:
        """获取中文优化配置"""
        config_file = self.configs_dir / "chinese_optimization.yaml"
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            # 返回默认中文配置
            return {
                "text": "<text>",
                "emphasis": "\\emph{<text>}",
                "strong": "\\textbf{<text>}",
                "heading": "\\<heading_types>{<text>}",
                "paragraph": "\n<text>\n",
                # 中文特殊优化
                "chinese_punctuation": True,
                "chinese_spacing": True
            }
    
    def _get_academic_config(self) -> Dict:
        """获取学术配置"""
        config_file = self.configs_dir / "academic_book.yaml"
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            # 返回默认学术配置
            return {
                "text": "<text>",
                "emphasis": "\\emph{<text>}",
                "strong": "\\textbf{<text>}",
                "heading": "\\<heading_types>{<text>}",
                "paragraph": "\n<text>\n",
                "image": """\\begin{figure}[htbp]
  \\centering
  \\includegraphics[width=0.8\\textwidth]{<url>}
  \\caption{<title>}
  \\label{fig:<title>}
\\end{figure}""",
                "table": """\\begin{table}[htbp]
  \\centering
  \\caption{<title>}
  \\begin{tabular}{<align>}
    \\toprule
    <head>
    \\midrule
    <body>
    \\bottomrule
  \\end{tabular}
  \\label{tab:<title>}
\\end{table}"""
            }
    
    def _get_enhanced_config(self) -> Dict:
        """获取增强配置"""
        # 基于学术配置，添加增强功能
        config = self._get_academic_config()
        
        # 添加增强功能配置
        config.update({
            "cross_reference": True,
            "bibliography": True,
            "index": True
        })
        
        return config
    
    def _get_template(self, template_name: str) -> str:
        """获取指定模板"""
        template_file = self.templates_dir / f"{template_name}_template.tex"
        
        if template_file.exists():
            with open(template_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # 返回默认模板
            return self._get_default_template()
    
    def _get_ctexbook_template(self) -> str:
        """获取 ctexbook 模板（基于 Open_Data_Book）"""
        template_file = self.templates_dir / "ctexbook_template.tex"
        
        if template_file.exists():
            with open(template_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # 创建基于 Open_Data_Book 的默认模板
            return self._create_ctexbook_template()
    
    def _get_enhanced_template(self) -> str:
        """获取增强模板"""
        template_file = self.templates_dir / "enhanced_template.tex"
        
        if template_file.exists():
            with open(template_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return self._create_enhanced_template()
    
    def _get_default_template(self) -> str:
        """获取默认模板"""
        return """\\documentclass[UTF8, a4paper, 12pt]{ctexart}

\\usepackage{graphicx}
\\usepackage{amsmath}
\\usepackage{amssymb}
\\usepackage{booktabs}
\\usepackage{hyperref}

\\title{文档标题}
\\author{作者}
\\date{\\today}

\\begin{document}

\\maketitle

<!-- Insert -->

\\end{document}"""
    
    def _create_ctexbook_template(self) -> str:
        """创建 ctexbook 模板（基于 Open_Data_Book）"""
        template = """\\documentclass[UTF8, a4paper, 12pt, openany]{ctexbook}

% 基于 Open_Data_Book 项目的导言区设置
\\usepackage{graphicx}
\\usepackage{amsmath}
\\usepackage{amssymb}
\\usepackage{booktabs}
\\usepackage{listings}
\\usepackage{xcolor}
\\usepackage{hyperref}
\\usepackage{geometry}
\\usepackage{fancyhdr}
\\usepackage{tcolorbox}
\\usepackage{tabularx}
\\usepackage{makeidx}
\\usepackage{url}

% 代码块设置
\\lstset{
  basicstyle=\\ttfamily\\small,
  keywordstyle=\\color{blue},
  commentstyle=\\color{green!60!black},
  stringstyle=\\color{red},
  breaklines=true,
  frame=single,
  numbers=left,
  numberstyle=\\tiny,
  numbersep=5pt
}

% 创建索引
\\makeindex

\\title{文档标题}
\\author{作者}
\\date{\\today}

\\begin{document}

\\maketitle
\\frontmatter
\\tableofcontents

\\mainmatter

<!-- Insert -->

\\backmatter
\\printindex

\\end{document}"""
        
        # 保存模板到文件
        template_file = self.templates_dir / "ctexbook_template.tex"
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(template)
        
        return template
    
    def _create_enhanced_template(self) -> str:
        """创建增强模板"""
        template = """\\documentclass[UTF8, a4paper, 12pt]{ctexart}

\\usepackage{graphicx}
\\usepackage{amsmath}
\\usepackage{amssymb}
\\usepackage{booktabs}
\\usepackage{hyperref}
\\usepackage{cleveref}
\\usepackage{natbib}
\\usepackage{makeidx}

% 中文优化设置
\\usepackage{xeCJK}

% 创建索引
\\makeindex

\\title{文档标题}
\\author{作者}
\\date{\\today}

\\begin{document}

\\maketitle

<!-- Insert -->

\\bibliographystyle{plain}
\\bibliography{references}
\\printindex

\\end{document}"""
        
        # 保存模板到文件
        template_file = self.templates_dir / "enhanced_template.tex"
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(template)
        
        return template
    
    def get_available_templates(self) -> List[str]:
        """获取可用模板列表"""
        templates = []
        
        if self.templates_dir.exists():
            for template_file in self.templates_dir.glob("*_template.tex"):
                template_name = template_file.stem.replace("_template", "")
                templates.append(template_name)
        
        # 添加内置模板
        builtin_templates = ["article", "ctexbook", "enhanced"]
        for template in builtin_templates:
            if template not in templates:
                templates.append(template)
        
        return templates
    
    def get_status(self) -> Dict:
        """获取增强功能状态"""
        return {
            "adapter_status": self.adapter.get_status(),
            "available_templates": self.get_available_templates(),
            "templates_dir": str(self.templates_dir),
            "configs_dir": str(self.configs_dir),
            "chinese_optimization": True,
            "ctexbook_support": True,
            "enhanced_features": True
        }
