# MD2DOCX MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-green.svg)](https://modelcontextprotocol.io/)

一个基于 Model Context Protocol (MCP) 的 Markdown 到 DOCX 转换服务器，提供强大的文档转换功能。

## ✨ 特性

- 🔄 **单文件转换** - 将单个 Markdown 文件转换为 DOCX 格式
- 📦 **批量转换** - 批量处理目录中的多个 Markdown 文件
- ⚙️ **灵活配置** - 支持多种转换参数和设置
- 🔍 **文件管理** - 列出和验证 Markdown 文件
- 🚀 **并行处理** - 支持多线程并行转换
- 📊 **详细日志** - 完整的转换过程记录
- 🛡️ **错误处理** - 智能的错误恢复和重试机制
- 📦 **开箱即用** - 内置 md2docx 依赖，无需额外安装

## 🏗️ 架构设计

本项目采用 MCP (Model Context Protocol) 架构，通过 Git Submodule 集成 [md2docx](https://github.com/wangqiqi/md2docx) 项目，实现开箱即用的部署体验。

### 项目结构

```
md2docx-mcp-server/
├── server.py                 # 主 MCP 服务器文件
├── pyproject.toml            # 项目配置
├── README.md                 # 项目说明
├── DEPLOYMENT_GUIDE.md       # 部署指南
├── core/                     # 核心模块
│   ├── __init__.py
│   ├── config_manager.py     # 配置管理器
│   └── converter_manager.py  # 转换管理器
├── md2docx/                  # Git Submodule (内置依赖)
│   ├── src/
│   │   ├── cli.py           # md2docx CLI 接口
│   │   └── converter/       # 转换器模块
│   └── requirements.txt
├── config/                   # 配置文件目录
│   └── converter_config.json # 转换器配置（自动生成）
└── .venv/                    # 虚拟环境
```

### 设计原则

1. **开箱即用** - 通过 Git Submodule 内置所有依赖
2. **模块化** - 清晰的模块分离和职责划分
3. **可配置** - 所有参数都可以通过配置文件或 MCP 工具调整
4. **异步处理** - 支持异步操作和并行处理
5. **错误恢复** - 智能的错误处理和重试机制

## 安装和设置

### 1. 环境要求

- Python 3.10+
- uv 包管理器
- Git（用于子模块管理）

### 2. 克隆项目（包含依赖）

```bash
# 推荐：克隆时同时初始化子模块
git clone --recursive https://github.com/your-username/md2docx-mcp-server.git

# 或者分步执行
git clone https://github.com/your-username/md2docx-mcp-server.git
cd md2docx-mcp-server
git submodule update --init --recursive
```

### 3. 创建虚拟环境并安装依赖

```bash
cd md2docx-mcp-server
uv sync
```

### 4. 激活虚拟环境

```bash
source .venv/bin/activate
```

### 5. 验证安装

项目已内置 md2docx 依赖，无需额外配置：

```python
# 通过 MCP 工具验证
get_conversion_status()
```

## 🛠️ MCP 工具说明

### 核心转换工具

#### `convert_md_to_docx`
转换单个 Markdown 文件为 DOCX 格式

**参数:**
- `input_file` (str): 输入的 Markdown 文件路径
- `output_file` (str, 可选): 输出的 DOCX 文件路径
- `debug` (bool, 可选): 是否启用调试模式

**使用示例:**
```python
convert_md_to_docx("/path/to/file.md")
convert_md_to_docx("/path/to/file.md", "/path/to/output.docx")
convert_md_to_docx("/path/to/file.md", debug=True)
```

#### `batch_convert_md_to_docx`
批量转换目录中的 Markdown 文件

**参数:**
- `input_dir` (str): 输入目录路径
- `output_dir` (str, 可选): 输出目录路径
- `file_pattern` (str): 文件匹配模式（默认 "*.md"）
- `parallel_jobs` (int, 可选): 并行任务数

**使用示例:**
```python
batch_convert_md_to_docx("/path/to/markdown/files")
batch_convert_md_to_docx("/input", "/output")
batch_convert_md_to_docx("/input", file_pattern="*.markdown")
batch_convert_md_to_docx("/input", parallel_jobs=8)
```

### 文件管理工具

#### `list_markdown_files`
列出目录中的 Markdown 文件

**参数:**
- `directory` (str): 目录路径
- `recursive` (bool): 是否递归搜索

**使用示例:**
```python
list_markdown_files("/path/to/directory")
list_markdown_files("/path/to/directory", recursive=True)
```

#### `validate_markdown_file`
验证 Markdown 文件是否可以转换

**参数:**
- `file_path` (str): Markdown 文件路径

**使用示例:**
```python
validate_markdown_file("/path/to/file.md")
```

### 配置管理工具

#### `configure_converter`
配置转换器参数设置

**参数:**
- `action` (str): 操作类型 (show/update/reset)
- `setting_type` (str): 设置类型 (conversion/batch/file/server/all)
- `**kwargs`: 具体的配置参数

**使用示例:**
```python
# 查看所有配置
configure_converter("show", "all")

# 更新转换设置
configure_converter("update", "conversion", debug_mode=True, output_dir="/custom/output")

# 更新批量设置
configure_converter("update", "batch", parallel_jobs=8, skip_existing=True)

# 更新服务器设置
configure_converter("update", "server", md2docx_project_path="/path/to/md2docx")

# 重置配置
configure_converter("reset")
```

#### 快速配置工具

```python
# 快速设置调试模式
quick_config_debug_mode(True)

# 快速设置输出目录
quick_config_output_dir("/custom/output")

# 快速设置并行任务数
quick_config_parallel_jobs(8)

# 快速设置 MD2DOCX 项目路径
quick_config_md2docx_path("/path/to/md2docx")
```

### 状态检查工具

#### `get_conversion_status`
获取转换器状态和配置信息

**使用示例:**
```python
get_conversion_status()
```

## 🎯 MCP Prompts - Q CLI 智能助手

本服务器包含两个智能 MCP Prompts，为 Q CLI 用户提供交互式指导：

### 📄 `md2docx_conversion_guide`
**智能转换助手** - 根据任务类型提供个性化的转换建议

**功能:**
- 自动分析任务类型（单文件、批量、配置、调试）
- 提供 AI 推荐的最佳解决方案
- 显示完整的工具矩阵和决策树
- 包含快速开始示例和重要提示

**Q CLI 使用:**
```
请使用 md2docx_conversion_guide 获取转换指导
```

### 🔧 `md2docx_troubleshooting_guide`
**故障排除助手** - 针对常见问题提供诊断和解决方案

**功能:**
- 智能分析错误类型（路径、格式、权限、配置问题）
- 提供分步诊断流程
- 包含常见问题的具体解决方案
- 完整的故障排除工作流程

**Q CLI 使用:**
```
请使用 md2docx_troubleshooting_guide 获取故障排除帮助
```

这些 Prompts 让 Q CLI 能够：
- 🤖 **智能推荐**: 根据用户需求自动推荐最适合的工具和参数
- 📋 **分步指导**: 提供清晰的操作步骤和命令示例
- 🔍 **问题诊断**: 快速定位和解决常见问题
- 💡 **最佳实践**: 分享使用技巧和注意事项

## 配置选项

### 转换设置 (ConversionSettings)
- `debug_mode`: 调试模式开关
- `output_dir`: 默认输出目录
- `preserve_structure`: 保持文档结构
- `auto_timestamp`: 文件冲突时自动添加时间戳
- `max_retry_attempts`: 最大重试次数

### 批量设置 (BatchSettings)
- `parallel_jobs`: 并行任务数
- `skip_existing`: 跳过已存在的文件
- `create_log`: 创建转换日志
- `log_level`: 日志级别

### 文件设置 (FileSettings)
- `supported_extensions`: 支持的文件扩展名
- `output_extension`: 输出文件扩展名
- `encoding`: 文件编码

### 服务器设置 (ServerSettings)
- `md2docx_project_path`: MD2DOCX 项目路径
- `use_subprocess`: 是否使用子进程调用
- `use_python_import`: 是否直接导入 Python 模块

## 使用方式

### 1. 子进程调用方式（推荐）
通过子进程调用原 md2docx 项目的 CLI 接口，完全隔离，更安全稳定。

### 2. Python 模块导入方式
直接导入原 md2docx 项目的 Python 模块，性能更好但需要处理依赖冲突。

## 🔧 MCP 配置

### Amazon Q CLI 配置

在 `~/.aws/amazonq/mcp.json` 文件中添加以下配置：

```json
{
  "mcpServers": {
    "MD2DOCX": {
      "command": "/absolute/path/to/md2docx-mcp-server/.venv/bin/mcp",
      "args": [
        "run",
        "/absolute/path/to/md2docx-mcp-server/server.py"
      ],
      "cwd": "/absolute/path/to/md2docx-mcp-server"
    }
  }
}
```

**重要**: 请将 `/absolute/path/to/md2docx-mcp-server` 替换为你的实际项目路径。

### 获取项目绝对路径

```bash
cd md2docx-mcp-server
pwd
# 将输出的路径复制到配置文件中
```

### 验证配置

启动 Amazon Q CLI 后，你应该能看到 MD2DOCX 工具可用。可以使用以下命令测试：

```
使用 get_conversion_status 工具检查服务器状态
```

## 🎯 Q CLI 使用指南

### 基本使用提示词

#### 单文件转换
```
请使用 convert_md_to_docx 工具将 /path/to/document.md 转换为 DOCX 格式
```

#### 批量转换
```
使用 batch_convert_md_to_docx 工具批量转换 /path/to/markdown/folder 目录下的所有 Markdown 文件
```

#### 配置管理
```
使用 configure_converter 工具更新服务器设置，将 md2docx_project_path 设置为 /path/to/md2docx
```

更多详细的使用示例和提示词，请参考：
- [Q CLI 使用指南](./Q_CLI_USAGE_GUIDE.md) - 详细的提示词示例和工作流程
- [工具参考手册](./TOOLS_REFERENCE.md) - 完整的工具功能说明

## 启动服务器（开发模式）

```bash
# 激活虚拟环境
source .venv/bin/activate

# 启动 MCP 服务器
python server.py
```

## 错误处理

- **文件冲突**: 自动添加时间戳后缀
- **权限错误**: 多次重试机制
- **编码错误**: 自动检测和处理
- **路径错误**: 详细的错误信息和建议

## 日志记录

- 支持多级别日志记录
- 批量转换自动生成详细日志文件
- 包含转换时间、文件大小、成功率等统计信息

## 性能优化

- 多线程并行处理
- 智能任务调度
- 内存使用优化
- 异步 I/O 操作

## 扩展性

- 模块化设计，易于扩展新功能
- 配置驱动，支持自定义参数
- 插件化架构，支持添加新的转换器

## 许可证

MIT License

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交变更
4. 推送到分支
5. 创建 Pull Request
