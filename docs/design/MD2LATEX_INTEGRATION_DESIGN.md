# 🎯 MD2LaTeX 集成设计方案

## 📋 项目概述

将 [VMIJUNV/md-to-latex](https://github.com/VMIJUNV/md-to-latex) 集成到 MD2DOCX MCP Server 中，实现 Markdown 到 LaTeX/PDF 的转换功能。

## 🏗️ 架构设计

### 混合适配器架构（推荐）

```
md2docx-mcp-server/
├── md2latex/                          # Git Submodule (上游项目)
│   ├── Tool/
│   │   ├── LaTeXRenderer.py
│   │   ├── md_to_latex.py
│   │   └── default_convert_config.yaml
│   └── README.md
├── core/
│   ├── md2latex_adapter.py            # 适配器层
│   ├── md2latex_enhanced.py           # 增强功能
│   ├── latex_template_manager.py      # 模板管理
│   └── latex_compiler.py              # LaTeX 编译
├── templates/
│   └── latex/
│       ├── ctexbook_template.tex      # 基于 Open_Data_Book
│       ├── article_template.tex       # 文章模板
│       └── configs/
│           ├── chinese_academic.yaml  # 中文学术配置
│           ├── english_article.yaml   # 英文文章配置
│           └── book_chapter.yaml      # 书籍章节配置
└── server.py                          # 主服务器
```

## 🔧 核心组件设计

### 1. 适配器层 (`md2latex_adapter.py`)

**职责**：封装上游项目，提供统一接口

```python
class MD2LaTeXAdapter:
    """
    适配器层：封装 VMIJUNV/md-to-latex 项目
    - 处理版本兼容性
    - 提供统一的调用接口
    - 隔离上游变更影响
    """
    
    def __init__(self):
        self.upstream_path = Path(__file__).parent.parent / "md2latex"
        self.upstream_available = self._check_upstream()
    
    def _check_upstream(self) -> bool:
        """检查上游项目是否可用"""
        required_files = [
            "Tool/LaTeXRenderer.py",
            "Tool/md_to_latex.py",
            "Tool/default_convert_config.yaml"
        ]
        return all((self.upstream_path / f).exists() for f in required_files)
    
    def convert_basic(self, md_content: str, config: dict) -> str:
        """基础转换功能（使用上游代码）"""
        if not self.upstream_available:
            raise RuntimeError("上游 md2latex 项目不可用")
        
        # 动态导入上游模块
        sys.path.insert(0, str(self.upstream_path / "Tool"))
        try:
            from LaTeXRenderer import LaTeXRender
            import mistune
            # ... 使用上游代码进行转换
        finally:
            sys.path.remove(str(self.upstream_path / "Tool"))
    
    def get_upstream_version(self) -> str:
        """获取上游项目版本信息"""
        # 通过 git 或其他方式获取版本
        pass
```

### 2. 增强功能层 (`md2latex_enhanced.py`)

**职责**：在适配器基础上添加增强功能

```python
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
        self.template_manager = LaTeXTemplateManager()
    
    def convert_with_chinese_optimization(self, md_content: str) -> str:
        """中文优化转换"""
        # 预处理：中文标点、间距等
        processed_content = self._preprocess_chinese(md_content)
        
        # 使用适配器进行基础转换
        latex_content = self.adapter.convert_basic(
            processed_content, 
            self._get_chinese_config()
        )
        
        # 后处理：中文特殊格式
        return self._postprocess_chinese(latex_content)
    
    def convert_with_ctexbook_template(self, md_content: str) -> str:
        """使用 ctexbook 模板转换（基于 Open_Data_Book）"""
        # 使用我们的 ctexbook 模板
        template = self.template_manager.get_template("ctexbook")
        config = self.template_manager.get_config("chinese_academic")
        
        # 转换并应用模板
        latex_content = self.adapter.convert_basic(md_content, config)
        return template.apply(latex_content)
```

### 3. 模板管理器 (`latex_template_manager.py`)

**职责**：管理 LaTeX 模板和配置

```python
class LaTeXTemplateManager:
    """
    模板管理器：管理各种 LaTeX 模板和配置
    - 基于 Open_Data_Book 的 ctexbook 模板
    - 多种预设配置
    - 模板验证和更新
    """
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates" / "latex"
        self.configs_dir = self.templates_dir / "configs"
    
    def get_template(self, template_name: str) -> LaTeXTemplate:
        """获取指定模板"""
        template_file = self.templates_dir / f"{template_name}_template.tex"
        return LaTeXTemplate.load(template_file)
    
    def get_config(self, config_name: str) -> dict:
        """获取指定配置"""
        config_file = self.configs_dir / f"{config_name}.yaml"
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def create_ctexbook_template(self) -> str:
        """基于 Open_Data_Book 项目创建 ctexbook 模板"""
        # 基于您的项目创建模板
        pass
```

## 🔄 升级和维护策略

### 1. 上游项目更新处理

```python
class UpstreamManager:
    """上游项目管理器"""
    
    def check_upstream_updates(self) -> bool:
        """检查上游是否有更新"""
        # 通过 git submodule 检查
        pass
    
    def update_upstream(self) -> bool:
        """更新上游项目"""
        try:
            # git submodule update --remote md2latex
            subprocess.run(["git", "submodule", "update", "--remote", "md2latex"])
            return self._test_compatibility()
        except Exception as e:
            logger.error(f"上游更新失败: {e}")
            return False
    
    def _test_compatibility(self) -> bool:
        """测试兼容性"""
        # 运行测试用例，确保更新后仍然兼容
        pass
```

### 2. 版本兼容性处理

```python
class VersionCompatibility:
    """版本兼容性管理"""
    
    SUPPORTED_VERSIONS = {
        "2.0": "full_support",
        "1.x": "limited_support"
    }
    
    def get_compatibility_level(self, version: str) -> str:
        """获取兼容性级别"""
        pass
    
    def apply_version_patches(self, version: str):
        """应用版本补丁"""
        # 针对不同版本的适配代码
        pass
```

## 🛠️ MCP 工具集成

### 新增的 LaTeX 工具

```python
@mcp.tool()
async def convert_md_to_latex(
    input_file: str,
    template: str = "ctexbook",
    config: str = "chinese_academic",
    output_file: Optional[str] = None
) -> str:
    """转换 Markdown 到 LaTeX"""
    
    try:
        enhanced_converter = MD2LaTeXEnhanced()
        
        # 读取输入文件
        with open(input_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # 根据模板类型选择转换方法
        if template == "ctexbook":
            latex_content = enhanced_converter.convert_with_ctexbook_template(md_content)
        else:
            latex_content = enhanced_converter.convert_with_chinese_optimization(md_content)
        
        # 输出文件
        output_path = output_file or input_file.replace('.md', '.tex')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        return f"✅ LaTeX 转换成功: {output_path}"
    
    except Exception as e:
        return f"❌ 转换失败: {str(e)}"

@mcp.tool()
async def compile_latex_to_pdf(
    latex_file: str,
    engine: str = "xelatex",
    output_dir: Optional[str] = None
) -> str:
    """编译 LaTeX 到 PDF"""
    
    compiler = LaTeXCompiler()
    result = compiler.compile(latex_file, engine, output_dir)
    
    if result['success']:
        return f"✅ PDF 编译成功: {result['output_file']}"
    else:
        return f"❌ 编译失败: {result['error']}"

@mcp.tool()
async def convert_md_to_pdf_complete(
    input_file: str,
    template: str = "ctexbook",
    engine: str = "xelatex"
) -> str:
    """一键从 Markdown 生成 PDF"""
    
    # 先转换为 LaTeX
    latex_result = await convert_md_to_latex(input_file, template)
    if "❌" in latex_result:
        return latex_result
    
    # 再编译为 PDF
    latex_file = input_file.replace('.md', '.tex')
    pdf_result = await compile_latex_to_pdf(latex_file, engine)
    
    return pdf_result

@mcp.tool()
async def update_md2latex_upstream() -> str:
    """更新上游 md2latex 项目"""
    
    manager = UpstreamManager()
    
    if manager.check_upstream_updates():
        if manager.update_upstream():
            return "✅ 上游项目更新成功，兼容性测试通过"
        else:
            return "❌ 上游项目更新失败或兼容性测试未通过"
    else:
        return "ℹ️ 上游项目已是最新版本"

@mcp.tool()
async def check_md2latex_status() -> str:
    """检查 MD2LaTeX 模块状态"""
    
    adapter = MD2LaTeXAdapter()
    manager = UpstreamManager()
    
    status = f"""🔍 MD2LaTeX 模块状态

📦 上游项目状态:
- 可用性: {'✅ 可用' if adapter.upstream_available else '❌ 不可用'}
- 版本: {adapter.get_upstream_version()}
- 更新检查: {'有更新' if manager.check_upstream_updates() else '最新'}

🛠️ 功能模块:
- 适配器层: {'✅ 正常' if adapter.upstream_available else '❌ 异常'}
- 增强功能: ✅ 正常
- 模板管理: ✅ 正常
- LaTeX 编译: ✅ 正常

📋 可用模板:
- ctexbook: ✅ (基于 Open_Data_Book)
- article: ✅ (标准文章)
- beamer: 🚧 (开发中)

⚙️ 可用配置:
- chinese_academic: ✅ (中文学术)
- english_article: ✅ (英文文章)
- book_chapter: ✅ (书籍章节)"""
    
    return status
```

## 🎯 优势总结

### 1. **灵活的升级策略**
- Git Submodule 方式跟踪上游更新
- 适配器层隔离变更影响
- 版本兼容性管理

### 2. **功能增强**
- 在上游基础上添加中文优化
- 集成您的 Open_Data_Book 项目模板
- 提供完整的 MD → PDF 工作流

### 3. **维护友好**
- 模块化设计，职责清晰
- 自动化的兼容性测试
- 详细的状态检查工具

### 4. **向后兼容**
- 保持与现有 DOCX/PPTX 功能的一致性
- 统一的 MCP 工具接口
- 相同的配置管理方式

## 🚀 实施计划

1. **阶段1**：集成上游项目（Git Submodule）
2. **阶段2**：开发适配器层和基础功能
3. **阶段3**：添加增强功能和中文优化
4. **阶段4**：集成 ctexbook 模板（基于您的项目）
5. **阶段5**：完善 MCP 工具和测试

**这个方案既能充分利用上游项目，又能保持我们的定制化需求和升级灵活性。您觉得如何？**
