"""
改进版 LaTeX 渲染器
基于 VMIJUNV/md-to-latex，但进行了大幅改进：
1. 支持多级标题（无限级别）
2. 改进的表格处理
3. 更好的中文支持
4. 代码高亮支持
5. 数学公式优化
"""

import mistune
from typing import Dict, Any, Optional
import re


class ImprovedLaTeXRenderer(mistune.BaseRenderer):
    """改进版 LaTeX 渲染器"""
    
    NAME = 'latex'  # 必需的属性，用于插件识别
    
    def __init__(self, config: Dict[str, Any], escape=True, allow_harmful_protocols=None):
        super().__init__()
        self._allow_harmful_protocols = allow_harmful_protocols
        self._escape = escape
        self.config = config
        
        # 扩展的标题类型，支持无限级别
        self.heading_types = [
            'section',           # level 1: #
            'subsection',        # level 2: ##  
            'subsubsection',     # level 3: ###
            'paragraph',         # level 4: ####
            'subparagraph',      # level 5: #####
        ]
        
        # 表格计数器
        self.table_counter = 0
        
    def render_token(self, token, state):
        """渲染单个 token - 更新版"""
        token_type = token['type']
        func = self._get_method(token_type)
        
        # 表格相关的 token 需要特殊处理
        if token_type in ['table', 'table_head', 'table_body', 'table_row', 'table_cell']:
            return func(token, state)
        
        # 其他 token 的处理逻辑
        attrs = token.get('attrs', {})

        if 'raw' in token:
            text = token['raw']
        elif 'children' in token:
            text = self.render_tokens(token['children'], state)
        else:
            if attrs:
                return func(**attrs)
            else:
                return func()
        
        if attrs:
            return func(text, **attrs)
        else:
            return func(text)
    
    def _get_method(self, name):
        """获取渲染方法"""
        method = getattr(self, name, None)
        if not method:
            # 如果没有对应方法，返回默认处理
            return lambda *args, **kwargs: ''
        return method
    
    # === 内联元素 ===
    
    def text(self, text: str) -> str:
        """普通文本"""
        # 转义特殊 LaTeX 字符
        text = self._escape_latex(text)
        return self.config.get("text", "<text>").replace("<text>", text)
    
    def emphasis(self, text: str) -> str:
        """斜体文本"""
        return self.config.get("emphasis", "\\emph{<text>}").replace("<text>", text)
    
    def strong(self, text: str) -> str:
        """粗体文本"""
        return self.config.get("strong", "\\textbf{<text>}").replace("<text>", text)
    
    def link(self, text: str, url: str, title: Optional[str] = None) -> str:
        """链接"""
        template = self.config.get("link", "\\href{<url>}{<text>}")
        return template.replace("<url>", url).replace("<text>", text)
    
    def image(self, alt: str, url: str, title: Optional[str] = None) -> str:
        """图片 - 改进版，支持路径解析和格式检查"""
        from pathlib import Path
        import os
        
        # 处理图片路径
        processed_url = self._process_image_path(url)
        
        # 检查图片格式兼容性
        format_info = self._check_image_format(processed_url)
        
        template = self.config.get("image", """
\\begin{figure}[H]
    \\centering
    \\includegraphics[width=0.8\\textwidth]{<url>}
    \\caption{<alt>}
    \\label{fig:<label>}
\\end{figure}""")
        
        # 生成标签
        label = re.sub(r'[^a-zA-Z0-9]', '_', alt.lower())
        
        # 如果有格式警告，添加注释
        result = template.replace("<url>", processed_url).replace("<alt>", alt).replace("<label>", label)
        
        if format_info['warning']:
            result = f"% 图片格式提示: {format_info['warning']}\n{result}"
        
        return result
    
    def _process_image_path(self, url: str) -> str:
        """处理图片路径，解决相对路径问题"""
        from pathlib import Path
        
        # 如果是绝对路径，直接返回
        if Path(url).is_absolute():
            return url
        
        # 如果是相对路径，需要根据输出目录调整
        if url.startswith('../'):
            # 从 output/latex/ 目录看，需要回到项目根目录
            # ../images/file.jpg -> ../../tests/images/file.jpg
            if 'tests/images/' in url or 'images/' in url:
                # 调整路径：从 output/latex/ 到 tests/images/
                adjusted_url = url.replace('../images/', '../../tests/images/')
                return adjusted_url
        
        # 其他情况保持原样
        return url
    
    def _check_image_format(self, url: str) -> dict:
        """检查图片格式兼容性"""
        from pathlib import Path
        
        # 获取文件扩展名
        ext = Path(url).suffix.lower()
        
        # LaTeX 原生支持的格式
        native_formats = {'.pdf', '.png', '.jpg', '.jpeg'}
        
        # 需要转换的格式
        convertible_formats = {
            '.bmp': 'BMP格式可能需要转换为PNG',
            '.tiff': 'TIFF格式可能需要转换为PNG', 
            '.tif': 'TIF格式可能需要转换为PNG',
            '.gif': 'GIF格式可能需要转换为PNG',
            '.webp': 'WebP格式可能需要转换为PNG'
        }
        
        if ext in native_formats:
            return {'compatible': True, 'warning': None}
        elif ext in convertible_formats:
            return {'compatible': False, 'warning': convertible_formats[ext]}
        else:
            return {'compatible': False, 'warning': f'未知图片格式 {ext}，建议使用 PNG/JPEG'}
    
    def codespan(self, text: str) -> str:
        """行内代码"""
        return self.config.get("codespan", "\\texttt{<text>}").replace("<text>", text)
    
    def linebreak(self) -> str:
        """换行"""
        return self.config.get("linebreak", "\\\\")
    
    def softbreak(self) -> str:
        """软换行"""
        return self.config.get("softbreak", " ")
    
    # === 块级元素 ===
    
    def paragraph(self, text: str) -> str:
        """段落"""
        return self.config.get("paragraph", "\\n<text>\\n").replace("<text>", text)
    
    def heading(self, text: str, level: int, **attrs) -> str:
        """标题 - 改进版，支持无限级别"""
        # 安全获取标题类型
        if level <= len(self.heading_types):
            heading_type = self.heading_types[level - 1]
        else:
            # 超过预定义级别，使用 subparagraph
            heading_type = "subparagraph"
        
        template = self.config.get("heading", "\\<heading_type>{<text>}")
        return template.replace("<heading_type>", heading_type).replace("<text>", text)
    
    def block_text(self, text: str) -> str:
        """块文本"""
        return self.config.get("block_text", "<text>").replace("<text>", text)
    
    def block_code(self, text: str, info: Optional[str] = None) -> str:
        """代码块 - 改进版，支持语法高亮和语言映射"""
        if info:
            # 语言映射表 - 将不支持的语言映射到支持的语言
            language_mapping = {
                'javascript': 'Java',
                'js': 'Java',
                'typescript': 'Java',
                'ts': 'Java',
                'jsx': 'Java',
                'tsx': 'Java',
                'vue': 'HTML',
                'svelte': 'HTML',
                'php': 'PHP',
                'ruby': 'Ruby',
                'go': 'C',
                'rust': 'C',
                'kotlin': 'Java',
                'swift': 'C',
                'dart': 'Java',
                'scala': 'Java',
                'clojure': 'Lisp',
                'elixir': 'Erlang',
                'haskell': 'Haskell',
                'ocaml': 'ML',
                'fsharp': 'ML',
                'powershell': 'bash',
                'dockerfile': 'bash',
                'yaml': 'XML',
                'yml': 'XML',
                'toml': 'XML',
                'json': 'XML',
                'markdown': 'TeX',
                'md': 'TeX',
                'tex': 'TeX',
                'latex': 'TeX'
            }
            
            # 将语言名称转换为小写进行匹配
            lang_lower = info.lower().strip()
            
            # 使用映射表或保持原语言名称
            mapped_lang = language_mapping.get(lang_lower, info)
            
            # 有语言信息，使用 listings 包
            template = self.config.get("block_code_with_lang", """
\\begin{lstlisting}[language=<lang>]
<code>
\\end{lstlisting}""")
            return template.replace("<lang>", mapped_lang).replace("<code>", text)
        else:
            # 无语言信息，使用 verbatim
            template = self.config.get("block_code", """
\\begin{verbatim}
<code>
\\end{verbatim}""")
            return template.replace("<code>", text)
    
    def block_quote(self, text: str) -> str:
        """引用块"""
        template = self.config.get("block_quote", """
\\begin{quote}
<text>
\\end{quote}""")
        return template.replace("<text>", text)
    
    def thematic_break(self) -> str:
        """分隔线"""
        return self.config.get("thematic_break", "\\noindent\\rule{\\textwidth}{1pt}")
    
    # === 列表 ===
    
    def list_item(self, text: str) -> str:
        """列表项"""
        return self.config.get("list_item", "\\item <text>").replace("<text>", text)
    
    def ordered_list(self, text: str) -> str:
        """有序列表"""
        template = self.config.get("ordered_list", """
\\begin{enumerate}
<text>
\\end{enumerate}""")
        return template.replace("<text>", text)
    
    def unordered_list(self, text: str) -> str:
        """无序列表"""
        template = self.config.get("unordered_list", """
\\begin{itemize}
<text>
\\end{itemize}""")
        return template.replace("<text>", text)
    
    # === 表格 - 基于 Token 结构的正确实现 ===
    
    def table(self, token, state):
        """表格 - 基于 Token 结构的正确实现"""
        self.table_counter += 1
        
        # 获取表格的子元素
        children = token.get('children', [])
        
        header_rows = []
        body_rows = []
        
        for child in children:
            if child.get('type') == 'table_head':
                # 处理表头
                head_children = child.get('children', [])
                for head_cell in head_children:
                    if head_cell.get('type') == 'table_cell':
                        cell_text = self.render_tokens(head_cell.get('children', []), state)
                        header_rows.append(f"\\textbf{{{cell_text}}}")
            
            elif child.get('type') == 'table_body':
                # 处理表体
                body_children = child.get('children', [])
                for body_row in body_children:
                    if body_row.get('type') == 'table_row':
                        row_cells = []
                        for cell in body_row.get('children', []):
                            if cell.get('type') == 'table_cell':
                                cell_text = self.render_tokens(cell.get('children', []), state)
                                row_cells.append(cell_text)
                        if row_cells:
                            body_rows.append(' & '.join(row_cells) + ' \\\\')
        
        # 计算列数
        if header_rows:
            col_count = len(header_rows)
        elif body_rows:
            col_count = body_rows[0].count('&') + 1 if body_rows else 3
        else:
            col_count = 3
        
        # 生成列对齐
        alignment = '|' + 'l|' * col_count
        
        # 组装表头行
        header_line = ' & '.join(header_rows) + ' \\\\' if header_rows else ""
        
        template = self.config.get("table", """
\\begin{table}[H]
    \\centering
    \\caption{表格 <counter>}
    \\label{tab:table<counter>}
    \\begin{tabular}{<alignment>}
        \\hline
        <header>
        \\hline
        <body>
        \\hline
    \\end{tabular}
\\end{table}""")
        
        return template.replace("<counter>", str(self.table_counter)) \
                      .replace("<alignment>", alignment) \
                      .replace("<header>", header_line) \
                      .replace("<body>", '\n        '.join(body_rows))
    
    def table_head(self, token, state):
        """表头 - 基于 Token"""
        return self.render_tokens(token.get('children', []), state)
    
    def table_body(self, token, state):
        """表体 - 基于 Token"""
        return self.render_tokens(token.get('children', []), state)
    
    def table_row(self, token, state):
        """表格行 - 基于 Token"""
        return self.render_tokens(token.get('children', []), state)
    
    def table_cell(self, token, state):
        """表格单元格 - 基于 Token"""
        text = self.render_tokens(token.get('children', []), state)
        attrs = token.get('attrs', {})
        head = attrs.get('head', False)
        
        if head:
            text = f"\\textbf{{{text}}}"
        return text
    
    # === 数学公式 ===
    
    def inline_math(self, text: str) -> str:
        """行内数学公式"""
        return self.config.get("inline_math", "$<text>$").replace("<text>", text)
    
    def block_math(self, text: str) -> str:
        """块级数学公式"""
        template = self.config.get("block_math", """
\\begin{equation}
<text>
\\end{equation}""")
        return template.replace("<text>", text)
    
    # === 辅助方法 ===
    
    def _escape_latex(self, text: str) -> str:
        """转义 LaTeX 特殊字符"""
        if not self._escape:
            return text
        
        # LaTeX 特殊字符映射
        escape_map = {
            '\\': '\\textbackslash{}',
            '{': '\\{',
            '}': '\\}',
            '$': '\\$',
            '&': '\\&',
            '%': '\\%',
            '#': '\\#',
            '^': '\\textasciicircum{}',
            '_': '\\_',
            '~': '\\textasciitilde{}',
        }
        
        for char, escaped in escape_map.items():
            text = text.replace(char, escaped)
        
        return text
    
    # === 兼容性方法 ===
    
    def disordered_list(self, text: str) -> str:
        """无序列表（兼容性别名）"""
        return self.unordered_list(text)
    
    def blank_line(self) -> str:
        """空行"""
        return self.config.get("blank_line", "\n")
