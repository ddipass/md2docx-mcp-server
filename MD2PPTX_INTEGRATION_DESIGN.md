# 🎯 MD2PPTX 集成设计方案

## 📋 项目概述

将 [md2pptx](https://github.com/MartinPacker/md2pptx) 集成到现有的 MD2DOCX MCP Server 中，实现统一的 Markdown 文档转换平台。

## 🏗️ 架构设计

### 方案1：统一转换器架构（推荐）

```
md2docx-mcp-server/
├── server.py                     # 主 MCP 服务器
├── core/
│   ├── config_manager.py          # 扩展配置管理
│   ├── converter_manager.py       # 统一转换管理器
│   ├── docx_converter.py          # DOCX 转换器
│   └── pptx_converter.py          # PPTX 转换器（新增）
├── md2docx/                       # Git Submodule
├── md2pptx/                       # Git Submodule（新增）
├── templates/                     # 模板目录（新增）
│   ├── docx/
│   └── pptx/
└── output/
    ├── docx/
    └── pptx/
```

### 核心设计原则

1. **🔄 统一接口**: 相同的 MCP 工具接口，支持多种输出格式
2. **📦 模块化**: 每种格式独立的转换器模块
3. **⚙️ 配置驱动**: 统一的配置管理，支持格式特定选项
4. **🚀 并行处理**: 支持同时转换多种格式
5. **🛡️ 错误隔离**: 一种格式失败不影响其他格式

## 🛠️ 实现方案

### 1. 扩展配置系统

```python
@dataclass
class ConversionSettings:
    debug_mode: bool = False
    output_dir: str = "output"
    supported_formats: List[str] = field(default_factory=lambda: ["docx", "pptx"])
    default_format: str = "docx"
    preserve_structure: bool = True
    auto_timestamp: bool = True
    max_retry_attempts: int = 5

@dataclass
class PPTXSettings:
    template_file: str = ""
    slide_layout: str = "default"
    theme: str = "default"
    aspect_ratio: str = "16:9"  # 16:9 or 4:3
    font_size: int = 18
    enable_animations: bool = False
```

### 2. 统一转换器接口

```python
class BaseConverter(ABC):
    @abstractmethod
    async def convert(self, input_file: str, output_file: str, **kwargs) -> Dict:
        pass
    
    @abstractmethod
    def validate_input(self, input_file: str) -> bool:
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        pass

class DOCXConverter(BaseConverter):
    # 现有的 DOCX 转换逻辑
    pass

class PPTXConverter(BaseConverter):
    # 新的 PPTX 转换逻辑
    async def convert(self, input_file: str, output_file: str, **kwargs) -> Dict:
        # 调用 md2pptx
        pass
```

### 3. 增强的 MCP 工具

```python
@mcp.tool()
async def convert_markdown(
    input_file: str,
    output_format: str = "docx",  # docx, pptx, both
    output_file: Optional[str] = None,
    template: Optional[str] = None,
    debug: Optional[bool] = None
) -> str:
    """
    统一的 Markdown 转换工具
    
    Args:
        input_file: 输入的 Markdown 文件路径
        output_format: 输出格式 (docx/pptx/both)
        output_file: 输出文件路径（可选）
        template: 模板文件路径（可选）
        debug: 调试模式
    """

@mcp.tool()
async def batch_convert_markdown(
    input_dir: str,
    output_formats: List[str] = ["docx"],  # ["docx", "pptx"]
    output_dir: Optional[str] = None,
    parallel_jobs: Optional[int] = None
) -> str:
    """
    批量转换支持多格式输出
    """

@mcp.tool()
async def convert_with_template(
    input_file: str,
    output_format: str,
    template_file: str,
    output_file: Optional[str] = None
) -> str:
    """
    使用模板转换
    """
```

## 🎯 用户体验设计

### Q CLI 使用示例

```python
# 转换为 DOCX（默认）
convert_markdown("/path/to/file.md")

# 转换为 PPTX
convert_markdown("/path/to/file.md", "pptx")

# 同时转换为两种格式
convert_markdown("/path/to/file.md", "both")

# 使用模板转换
convert_with_template("/path/to/file.md", "pptx", "/path/to/template.pptx")

# 批量转换多种格式
batch_convert_markdown("/path/to/folder", ["docx", "pptx"])
```

### 智能格式检测

```python
@mcp.tool()
async def smart_convert(
    input_file: str,
    auto_detect_format: bool = True,
    preferred_format: str = "docx"
) -> str:
    """
    智能转换 - 根据内容特征推荐最佳格式
    
    - 检测到大量列表 → 推荐 PPTX
    - 检测到表格和长文本 → 推荐 DOCX
    - 检测到图片和短文本 → 推荐 PPTX
    """
```

## 📦 部署和安装

### 1. 添加 md2pptx 子模块

```bash
cd md2docx-mcp-server
git submodule add https://github.com/MartinPacker/md2pptx.git md2pptx
```

### 2. 更新依赖

```toml
# pyproject.toml
[project]
dependencies = [
    "fastmcp",
    "python-docx",
    "python-pptx",  # 新增
    "lxml",         # md2pptx 依赖
    "pillow",       # 可选，图片处理
]
```

### 3. 配置模板

```
templates/
├── pptx/
│   ├── default.pptx
│   ├── business.pptx
│   └── academic.pptx
└── docx/
    ├── default.docx
    └── report.docx
```

## 🔧 技术实现细节

### 1. md2pptx 调用方式

```python
# 方式1：子进程调用
async def _convert_via_subprocess_pptx(self, input_file: str, output_file: str):
    cmd = [
        sys.executable, "md2pptx", output_file
    ]
    
    # 通过 stdin 传递 markdown 内容
    with open(input_file, 'r') as f:
        content = f.read()
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(md2pptx_path)
    )
    
    stdout, stderr = await process.communicate(input=content.encode())

# 方式2：Python 模块导入
async def _convert_via_import_pptx(self, input_file: str, output_file: str):
    # 添加 md2pptx 到 sys.path
    sys.path.insert(0, str(md2pptx_path))
    
    # 直接调用 md2pptx 的转换函数
    # 需要分析 md2pptx 的内部 API
```

### 2. 模板管理

```python
class TemplateManager:
    def __init__(self):
        self.template_dir = Path("templates")
    
    def get_template(self, format_type: str, template_name: str) -> Path:
        template_path = self.template_dir / format_type / f"{template_name}.{format_type}"
        return template_path if template_path.exists() else None
    
    def list_templates(self, format_type: str) -> List[str]:
        template_dir = self.template_dir / format_type
        return [f.stem for f in template_dir.glob(f"*.{format_type}")]
```

### 3. 格式特定配置

```python
class FormatSpecificConfig:
    def __init__(self):
        self.docx_config = {
            "font_family": "Arial",
            "font_size": 12,
            "line_spacing": 1.15
        }
        
        self.pptx_config = {
            "slide_size": "16:9",
            "theme": "default",
            "transition": "none",
            "template": "default.pptx"
        }
```

## 🎯 分阶段实施计划

### Phase 1: 基础集成（1-2周）
- ✅ 添加 md2pptx 子模块
- ✅ 创建 PPTXConverter 类
- ✅ 实现基本的 convert_markdown 工具
- ✅ 更新配置系统

### Phase 2: 功能增强（2-3周）
- ✅ 实现批量转换多格式
- ✅ 添加模板支持
- ✅ 智能格式检测
- ✅ 错误处理和重试机制

### Phase 3: 用户体验优化（1-2周）
- ✅ 完善 Q CLI 集成
- ✅ 添加更多模板
- ✅ 性能优化
- ✅ 文档和示例

### Phase 4: 高级功能（可选）
- ✅ 自定义主题支持
- ✅ 动画和过渡效果
- ✅ 图表和图形增强
- ✅ 协作功能

## 🚀 预期收益

1. **🎯 一站式解决方案**: 单一 MCP 服务器支持多种输出格式
2. **⚡ 提升效率**: 批量转换多种格式，节省时间
3. **🎨 丰富选择**: 支持模板和主题，满足不同需求
4. **🔄 统一体验**: 相同的接口和配置，降低学习成本
5. **📈 扩展性**: 为未来添加更多格式（如 PDF）奠定基础

## 💡 创新特性

1. **智能推荐**: 根据内容特征推荐最适合的输出格式
2. **模板生态**: 内置多种专业模板，支持自定义
3. **并行转换**: 同时生成多种格式，提高效率
4. **格式互转**: 支持 DOCX ↔ PPTX 之间的转换
5. **预览功能**: 转换前预览效果

这个设计方案将使你的 MCP 服务器成为真正的**文档转换中心**！🎉
