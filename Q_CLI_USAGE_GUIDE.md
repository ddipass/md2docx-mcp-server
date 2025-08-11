# MD2DOCX MCP Server - Q CLI 使用指南

## 🎯 Q CLI 中的提示词示例

### 基础转换任务

#### 单文件转换
```
请使用 convert_md_to_docx 工具将 /path/to/document.md 转换为 DOCX 格式
```

```
帮我把这个 Markdown 文件转换成 Word 文档：/Users/username/Documents/report.md
```

#### 批量转换
```
使用 batch_convert_md_to_docx 工具批量转换 /path/to/markdown/folder 目录下的所有 Markdown 文件
```

```
我需要将整个文件夹的 Markdown 文件都转换成 DOCX，目录是：/Users/username/Documents/markdown-files/
```

### 配置管理任务

#### 查看当前配置
```
使用 get_conversion_status 工具查看当前的转换器配置和状态
```

```
显示 MD2DOCX 转换器的当前设置和配置信息
```

#### 更新配置
```
使用 configure_converter 工具更新转换设置，启用调试模式并设置输出目录为 /path/to/output
```

```
配置 MD2DOCX 转换器：开启调试模式，设置默认输出目录为 /Users/username/Documents/output
```

#### 设置 MD2DOCX 项目路径
```
使用 configure_converter 工具配置服务器设置，将 md2docx_project_path 设置为 /path/to/md2docx
```

```
配置 MD2DOCX 项目路径：/Users/username/Workspace/md2docx
```

### 文件管理任务

#### 列出 Markdown 文件
```
使用 list_markdown_files 工具列出 /path/to/directory 目录下的所有 Markdown 文件
```

```
显示这个目录下的所有 Markdown 文件：/Users/username/Documents/
```

#### 验证文件
```
使用 validate_markdown_file 工具检查 /path/to/file.md 是否可以正常转换
```

```
检查这个 Markdown 文件是否可以转换：/Users/username/Documents/test.md
```

### 高级使用场景

#### 并行批量转换
```
使用 batch_convert_md_to_docx 工具批量转换，设置 parallel_jobs 为 8 以提高转换速度
```

```
批量转换 Markdown 文件，使用 8 个并行任务来加速处理：输入目录 /path/to/input，输出目录 /path/to/output
```

#### 调试模式转换
```
使用 convert_md_to_docx 工具转换文件，启用 debug 模式以获取详细的转换信息
```

```
以调试模式转换这个文件，我需要看到详细的转换过程：/path/to/complex-document.md
```

## 🛠️ 常用工作流程

### 工作流程 1：首次使用设置
```
1. 首先使用 get_conversion_status 查看当前状态
2. 使用 configure_converter 设置 MD2DOCX 项目路径
3. 使用 quick_config_output_dir 设置默认输出目录
4. 测试转换一个简单的 Markdown 文件
```

### 工作流程 2：批量文档处理
```
1. 使用 list_markdown_files 查看目标目录的文件
2. 使用 configure_converter 调整批量处理设置（如并行任务数）
3. 使用 batch_convert_md_to_docx 执行批量转换
4. 检查转换日志和结果
```

### 工作流程 3：问题诊断
```
1. 使用 validate_markdown_file 检查问题文件
2. 使用 configure_converter 启用调试模式
3. 使用 convert_md_to_docx 以调试模式重新转换
4. 根据错误信息调整配置或文件内容
```

## 📝 自然语言提示词模板

### 转换任务模板
- "转换这个 Markdown 文件：[文件路径]"
- "批量转换这个目录的所有 MD 文件：[目录路径]"
- "将 [文件名] 转换为 Word 文档"
- "处理整个文件夹的 Markdown 文档：[文件夹路径]"

### 配置任务模板
- "设置 MD2DOCX 的输出目录为：[目录路径]"
- "启用/禁用调试模式"
- "配置并行转换任务数为：[数字]"
- "显示当前的转换器设置"

### 管理任务模板
- "列出这个目录的 Markdown 文件：[目录路径]"
- "检查这个文件是否可以转换：[文件路径]"
- "显示转换器状态和配置"

## 🎯 最佳实践提示

### 1. 路径使用
- 始终使用绝对路径，避免相对路径引起的混淆
- 在 macOS/Linux 上使用正斜杠 `/`
- 确保路径中的文件和目录确实存在

### 2. 批量处理
- 大量文件时，适当设置并行任务数（建议 4-8）
- 先用小批量测试，确认配置正确后再处理大批量
- 注意输出目录的磁盘空间

### 3. 错误处理
- 遇到转换失败时，先启用调试模式
- 使用 validate_markdown_file 检查文件格式
- 检查 MD2DOCX 项目路径是否正确配置

### 4. 性能优化
- 根据系统性能调整并行任务数
- 定期清理输出目录的临时文件
- 监控系统资源使用情况

## 🔧 故障排除提示词

### 配置问题
```
"显示 MD2DOCX 转换器的当前配置，我需要检查设置是否正确"
"重置转换器配置到默认状态"
```

### 转换失败
```
"以调试模式转换这个文件，我需要看到详细的错误信息：[文件路径]"
"验证这个 Markdown 文件的格式是否正确：[文件路径]"
```

### 路径问题
```
"检查 MD2DOCX 项目路径配置是否正确"
"列出这个目录下的所有 Markdown 文件，确认文件存在：[目录路径]"
```

## 📚 示例对话

### 示例 1：首次使用
**用户**: "我想使用 MD2DOCX 转换器，但不知道如何开始"
**Q CLI**: 使用 get_conversion_status 工具查看当前状态，然后根据需要配置项目路径

### 示例 2：批量转换
**用户**: "我有一个包含 50 个 Markdown 文件的文件夹，需要全部转换成 Word 文档"
**Q CLI**: 使用 batch_convert_md_to_docx 工具，建议设置适当的并行任务数以提高效率

### 示例 3：问题诊断
**用户**: "转换失败了，显示格式错误"
**Q CLI**: 使用 validate_markdown_file 工具检查文件格式，然后以调试模式重新转换

这个指南帮助用户在 Q CLI 中更有效地使用 MD2DOCX MCP Server 的各种功能。
