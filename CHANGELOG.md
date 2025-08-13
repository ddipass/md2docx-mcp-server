# 更新日志

## [1.2.2] - 2024-08-13

### 🎨 重大功能增强：智能语言映射与完整图片支持

#### ✨ 新增功能
- **🔤 智能代码语言映射**: 解决 JavaScript 语言支持问题
  - JavaScript/TypeScript → Java 语法高亮
  - Go/Rust/Swift → C 语法高亮
  - Vue.js/Svelte → HTML 语法高亮
  - YAML/JSON → XML 语法高亮
  - PowerShell/Dockerfile → Bash 语法高亮
  - 支持 30+ 种现代编程语言

- **📸 完整图片格式支持**: 
  - **原生支持**: JPEG, PNG, PDF
  - **转换支持**: BMP, TIFF, GIF, WebP, SVG, ICO
  - **自动转换**: 不兼容格式自动转换为 PNG
  - **智能路径**: 自动修复相对路径问题

- **🛠️ 图片转换工具集成**:
  - macOS sips 工具支持
  - rsvg-convert SVG 转换
  - ImageMagick 可选支持
  - 批量转换功能

#### 🔧 技术改进
- **语言映射系统**: 大小写不敏感的智能语言匹配
- **路径解析优化**: 从 `../images/` 自动修复为 `../../tests/images/`
- **格式兼容性检查**: 自动检测并生成格式警告
- **转换质量控制**: 自动尺寸限制和质量优化
- **错误处理增强**: 超时保护和详细错误信息

#### 🧪 测试完善
- **多语言测试**: `test_multilang_code.md` - 10+ 种编程语言
- **图片格式测试**: 
  - `test_compatible_images.md` - JPEG/PNG 原生支持
  - `test_image_formats.md` - 全格式兼容性测试
  - `test_complete_image_support.md` - 完整功能验证
- **测试资源**: 创建完整的图片测试套件

#### 📚 文档更新
- **工具说明增强**: 添加支持语言列表和图片格式说明
- **状态检查改进**: 显示 30+ 支持的编程语言
- **测试文档完善**: 详细的功能说明和使用指南
- **最佳实践**: 性能优化和使用建议

#### 🎯 验证结果
- ✅ **JavaScript 支持**: 完全解决编译错误
- ✅ **图片处理**: 292.6 KB PDF，包含 5 张不同格式图片
- ✅ **多语言高亮**: 所有现代编程语言正确映射
- ✅ **路径修复**: 相对路径自动调整
- ✅ **格式转换**: BMP/TIFF 成功转换为 PNG

## [1.2.1] - 2024-08-13

### 🧹 项目清理和文档整理

#### 📁 文件结构优化
- **测试文件整理**: 移动所有测试 Markdown 文件到 `tests/samples/` 目录
- **输出路径统一**: 所有格式的输出文件统一到 `output/` 目录
  - `output/docx/` - DOCX 文件输出
  - `output/pptx/` - PPTX 文件输出  
  - `output/latex/` - LaTeX 和 PDF 文件输出
- **清理备份文件**: 删除不再需要的 `md2latex_backup/` 目录
- **根目录清理**: 移除根目录下的临时测试文件

#### 📚 文档完善
- **更新主 README**: 添加 LaTeX/PDF 转换支持说明
- **完善文档结构**: 更新 `docs/README.md` 包含完整的功能说明
- **测试文档**: 新增 `tests/README.md` 详细说明测试文件用途
- **版本历史更新**: 更新版本信息和功能特性

#### 🔧 技术改进
- **路径处理优化**: 修复相对路径问题，统一使用绝对路径
- **表格渲染修复**: 彻底解决表格格式问题，基于 mistune token 结构重写
- **LaTeX 编译器优化**: 改进成功检测逻辑，支持警告但成功的编译

#### 🎯 用户体验提升
- **一致的输出结构**: 所有转换格式使用相同的输出目录结构
- **自动路径管理**: 无需手动指定输出路径，自动管理文件位置
- **清晰的项目结构**: 更好的文件组织和文档说明

## [1.2.0] - 2024-08-13

### 🧹 项目清理和文档整理

#### 📁 文件结构优化
- **测试文件整理**: 移动所有测试 Markdown 文件到 `tests/samples/` 目录
- **输出路径统一**: 所有格式的输出文件统一到 `output/` 目录
  - `output/docx/` - DOCX 文件输出
  - `output/pptx/` - PPTX 文件输出  
  - `output/latex/` - LaTeX 和 PDF 文件输出
- **清理备份文件**: 删除不再需要的 `md2latex_backup/` 目录
- **根目录清理**: 移除根目录下的临时测试文件

#### 📚 文档完善
- **更新主 README**: 添加 LaTeX/PDF 转换支持说明
- **完善文档结构**: 更新 `docs/README.md` 包含完整的功能说明
- **测试文档**: 新增 `tests/README.md` 详细说明测试文件用途
- **版本历史更新**: 更新版本信息和功能特性

#### 🔧 技术改进
- **路径处理优化**: 修复相对路径问题，统一使用绝对路径
- **表格渲染修复**: 彻底解决表格格式问题，基于 mistune token 结构重写
- **LaTeX 编译器优化**: 改进成功检测逻辑，支持警告但成功的编译

#### 🎯 用户体验提升
- **一致的输出结构**: 所有转换格式使用相同的输出目录结构
- **自动路径管理**: 无需手动指定输出路径，自动管理文件位置
- **清晰的项目结构**: 更好的文件组织和文档说明

## [1.2.0] - 2024-08-13

### 🚀 重大更新：自维护 MD2LaTeX 版本

#### ✨ 新增功能
- **自维护 MD2LaTeX**: 移除 Git Submodule 依赖，使用自维护版本
- **无限级别标题**: 支持任意级别的 Markdown 标题（#, ##, ###, ####, #####, ######+）
- **改进的表格处理**: 更好的表格转换和格式化
- **多种配置支持**: 
  - `default`: 默认配置，适用于一般文档
  - `chinese`: 中文优化配置，适用于中文文档
  - `academic`: 学术论文配置，适用于学术文档
- **多种模板支持**:
  - `basic`: 基础模板，适用于一般文档
  - `academic`: 学术论文模板，包含定理环境等
  - `chinese_book`: 中文书籍模板，适用于长文档
- **代码高亮支持**: 支持多种编程语言的语法高亮
- **更好的中文支持**: 优化中文字体和排版

#### 🔧 技术改进
- **模块化架构**: 清晰的模块分离和组织
- **错误处理**: 更好的错误处理和用户反馈
- **配置系统**: 灵活的配置和模板系统
- **向后兼容**: 保持与现有 MCP 工具的兼容性

#### 🛠️ 更新的 MCP 工具
- `convert_md_to_latex`: 支持新的配置和模板参数
- `convert_md_to_pdf_direct`: 支持新的配置和模板参数
- `check_md2latex_status`: 显示改进版状态信息

#### 📁 新增文件结构
```
md2latex/
├── core/
│   ├── converter.py          # 主转换器
│   ├── latex_renderer.py     # 改进版 LaTeX 渲染器
│   └── __init__.py
├── configs/
│   ├── default_config.yaml   # 默认配置
│   ├── chinese_config.yaml   # 中文优化配置
│   └── academic_config.yaml  # 学术论文配置
├── templates/
│   ├── basic_template.tex     # 基础模板
│   ├── academic_template.tex  # 学术论文模板
│   └── chinese_book_template.tex # 中文书籍模板
└── __init__.py
```

#### 🐛 修复问题
- **标题级别限制**: 修复原版本只支持 3 级标题的问题
- **索引越界**: 解决 `list index out of range` 错误
- **依赖管理**: 移除对外部 submodule 的依赖

#### 💡 使用示例
```python
# 中文文档转换
convert_md_to_latex("/path/to/chinese.md", "chinese", "basic")

# 学术论文转换
convert_md_to_latex("/path/to/paper.md", "academic", "academic")

# 中文书籍转换
convert_md_to_latex("/path/to/book.md", "chinese", "chinese_book")

# 一键 PDF 转换
convert_md_to_pdf_direct("/path/to/file.md", "chinese", "basic")
```

---

## [1.2.0] - 2024-08-13

### ✨ 新增功能
- 集成 MD2LaTeX 功能（基于 VMIJUNV/md-to-latex）
- 支持 Markdown 到 LaTeX 转换
- 支持 LaTeX 到 PDF 编译
- 中文文档优化支持

### 🔧 技术更新
- 添加 mistune>=3.0.0 和 pyyaml>=6.0.0 依赖
- Git Submodule 集成 VMIJUNV/md-to-latex 项目
- 适配器模式实现

---

## [1.1.0] - 2024-08-11

### ✨ 新增功能
- 集成 md2pptx，支持统一 DOCX/PPTX 转换
- 统一转换器架构
- 批量多格式转换支持

---

## [1.0.0] - 2024-08-10

### 🎉 首个稳定版本
- 支持 Markdown 到 DOCX 转换
- MCP 服务器基础架构
- 基本的配置管理
