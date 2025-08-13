# 📚 MD2DOCX MCP Server 文档

欢迎来到 MD2DOCX MCP Server 的文档中心！

## 📖 文档结构

### 🚀 安装和部署指南
- [`guides/MCP_INSTALLATION_GUIDE.md`](guides/MCP_INSTALLATION_GUIDE.md) - MCP 安装指南
- [`guides/DEPLOYMENT_GUIDE.md`](guides/DEPLOYMENT_GUIDE.md) - 部署指南  
- [`guides/PPTX_TEMPLATE_GUIDE.md`](guides/PPTX_TEMPLATE_GUIDE.md) - PPTX 模板使用指南

### 🏗️ 设计文档
- [`design/MD2PPTX_INTEGRATION_DESIGN.md`](design/MD2PPTX_INTEGRATION_DESIGN.md) - MD2PPTX 集成设计方案
- [`design/MD2LATEX_INTEGRATION_DESIGN.md`](design/MD2LATEX_INTEGRATION_DESIGN.md) - MD2LaTeX 集成设计方案

### 📝 示例文件
- [`examples/区块链技术专业演示.md`](examples/区块链技术专业演示.md) - MD2PPTX 格式示例

## 🔗 快速导航

### 新用户开始
1. 📖 阅读 [MCP 安装指南](guides/MCP_INSTALLATION_GUIDE.md)
2. 🚀 查看 [部署指南](guides/DEPLOYMENT_GUIDE.md)
3. 🎯 尝试转换示例文件

### 开发者资源
- 🏗️ [MD2PPTX 集成设计](design/MD2PPTX_INTEGRATION_DESIGN.md)
- 🔧 [MD2LaTeX 集成设计](design/MD2LATEX_INTEGRATION_DESIGN.md)
- 📊 [项目更新日志](../CHANGELOG.md)

## 🎯 支持的转换格式

| 格式 | 状态 | 说明 |
|------|------|------|
| **DOCX** | ✅ 稳定 | Microsoft Word 文档格式 |
| **PPTX** | ✅ 稳定 | Microsoft PowerPoint 演示文稿格式 |
| **LaTeX/PDF** | ✅ 改进版 | LaTeX 文档和 PDF 格式，支持无限级别标题 |

## 🛠️ 功能特性

### 🔄 统一转换接口
- 支持多种输出格式的统一 MCP 工具接口
- 批量转换和单文件转换
- 自动输出路径管理

### 🎨 模板和配置
- **PPTX**: 内置 Martin Template，支持自定义模板
- **LaTeX**: 多种配置（default/chinese/academic）和模板（basic/academic/chinese_book）
- **DOCX**: 支持自定义样式和格式

### 🚀 高级功能
- **表格处理**: 改进的表格渲染，支持复杂表格结构
- **中文支持**: 优化的中文字体和排版
- **代码高亮**: 支持多种编程语言的语法高亮
- **数学公式**: 完整的 LaTeX 数学公式支持

## 📁 项目结构

```
md2docx-mcp-server/
├── docs/                    # 📚 文档目录
│   ├── guides/             # 🚀 使用指南
│   ├── design/             # 🏗️ 设计文档
│   └── examples/           # 📝 示例文件
├── output/                 # 📄 输出目录
│   ├── docx/              # DOCX 输出
│   ├── pptx/              # PPTX 输出
│   └── latex/             # LaTeX/PDF 输出
├── tests/                  # 🧪 测试文件
│   └── samples/           # 测试样本
├── core/                   # 🔧 核心模块
├── md2latex/              # 📄 自维护 LaTeX 转换器
├── md2docx/               # 📄 DOCX 转换器（子模块）
├── md2pptx/               # 📊 PPTX 转换器（子模块）
└── server.py              # 🖥️ MCP 服务器
```

## 🤝 贡献指南

欢迎贡献代码和文档！请查看项目根目录的贡献指南。

## 📞 获取帮助

- 📖 查看相关指南文档
- 🐛 在 GitHub Issues 中报告问题
- 💡 提出功能建议和改进意见
