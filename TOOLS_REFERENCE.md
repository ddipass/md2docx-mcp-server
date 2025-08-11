# MD2DOCX MCP Server - 工具参考手册

## 🛠️ 可用工具列表

### 📄 核心转换工具

#### `convert_md_to_docx`
**功能**: 将单个 Markdown 文件转换为 DOCX 格式

**参数**:
- `input_file` (必需): 输入的 Markdown 文件路径
- `output_file` (可选): 输出的 DOCX 文件路径，不指定则自动生成
- `debug` (可选): 是否启用调试模式，不指定则使用配置默认值

**使用示例**:
```python
# 基本转换
convert_md_to_docx("/path/to/document.md")

# 指定输出文件
convert_md_to_docx("/path/to/document.md", "/path/to/output.docx")

# 启用调试模式
convert_md_to_docx("/path/to/document.md", debug=True)
```

**Q CLI 提示词**:
```
请使用 convert_md_to_docx 工具将 /path/to/document.md 转换为 DOCX 格式
```

---

#### `batch_convert_md_to_docx`
**功能**: 批量转换目录中的 Markdown 文件为 DOCX 格式

**参数**:
- `input_dir` (必需): 输入目录路径
- `output_dir` (可选): 输出目录路径，不指定则使用配置默认值
- `file_pattern` (可选): 文件匹配模式，默认 "*.md"
- `parallel_jobs` (可选): 并行任务数，不指定则使用配置默认值

**使用示例**:
```python
# 基本批量转换
batch_convert_md_to_docx("/path/to/markdown/files")

# 指定输出目录
batch_convert_md_to_docx("/input", "/output")

# 自定义文件模式
batch_convert_md_to_docx("/input", file_pattern="*.markdown")

# 设置并行任务数
batch_convert_md_to_docx("/input", parallel_jobs=8)
```

**Q CLI 提示词**:
```
使用 batch_convert_md_to_docx 工具批量转换 /path/to/markdown/folder 目录下的所有 Markdown 文件
```

---

### 📁 文件管理工具

#### `list_markdown_files`
**功能**: 列出目录中的 Markdown 文件

**参数**:
- `directory` (必需): 目录路径
- `recursive` (可选): 是否递归搜索子目录，默认 False

**使用示例**:
```python
# 列出当前目录的 Markdown 文件
list_markdown_files("/path/to/directory")

# 递归搜索子目录
list_markdown_files("/path/to/directory", recursive=True)
```

**Q CLI 提示词**:
```
使用 list_markdown_files 工具列出 /path/to/directory 目录下的所有 Markdown 文件
```

---

#### `validate_markdown_file`
**功能**: 验证 Markdown 文件是否可以转换

**参数**:
- `file_path` (必需): Markdown 文件路径

**使用示例**:
```python
validate_markdown_file("/path/to/file.md")
```

**Q CLI 提示词**:
```
使用 validate_markdown_file 工具检查 /path/to/file.md 是否可以正常转换
```

---

### ⚙️ 配置管理工具

#### `configure_converter`
**功能**: 配置转换器参数设置

**参数**:
- `action` (可选): 操作类型，可选值：show/update/reset，默认 "show"
- `setting_type` (可选): 设置类型，可选值：conversion/batch/file/server/all，默认 "all"
- `**kwargs`: 具体的配置参数

**使用示例**:
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

**Q CLI 提示词**:
```
使用 configure_converter 工具更新服务器设置，将 md2docx_project_path 设置为 /path/to/md2docx
```

---

#### `get_conversion_status`
**功能**: 获取转换器状态和配置信息

**参数**: 无

**使用示例**:
```python
get_conversion_status()
```

**Q CLI 提示词**:
```
使用 get_conversion_status 工具查看当前的转换器配置和状态
```

---

### 🚀 快速配置工具

#### `quick_config_debug_mode`
**功能**: 快速设置调试模式

**参数**:
- `enabled` (可选): 是否启用调试模式，默认 True

**使用示例**:
```python
# 启用调试模式
quick_config_debug_mode(True)

# 禁用调试模式
quick_config_debug_mode(False)
```

**Q CLI 提示词**:
```
使用 quick_config_debug_mode 工具启用调试模式
```

---

#### `quick_config_output_dir`
**功能**: 快速设置输出目录

**参数**:
- `output_dir` (可选): 输出目录路径，默认 "output"

**使用示例**:
```python
# 设置自定义输出目录
quick_config_output_dir("/path/to/output")

# 使用默认输出目录
quick_config_output_dir()
```

**Q CLI 提示词**:
```
使用 quick_config_output_dir 工具设置输出目录为 /path/to/output
```

---

#### `quick_config_parallel_jobs`
**功能**: 快速设置并行任务数

**参数**:
- `jobs` (可选): 并行任务数量，默认 4

**使用示例**:
```python
# 设置并行任务数
quick_config_parallel_jobs(8)

# 使用默认值
quick_config_parallel_jobs()
```

**Q CLI 提示词**:
```
使用 quick_config_parallel_jobs 工具设置并行任务数为 8
```

---

#### `quick_config_md2docx_path`
**功能**: 快速设置 MD2DOCX 项目路径

**参数**:
- `project_path` (必需): MD2DOCX 项目的绝对路径

**使用示例**:
```python
quick_config_md2docx_path("/path/to/md2docx")
```

**Q CLI 提示词**:
```
使用 quick_config_md2docx_path 工具设置 MD2DOCX 项目路径为 /path/to/md2docx
```

---

## 🎯 工具使用场景

### 场景 1：首次使用设置
1. `get_conversion_status` - 查看当前状态
2. `quick_config_md2docx_path` - 设置项目路径
3. `quick_config_output_dir` - 设置输出目录
4. `convert_md_to_docx` - 测试转换

### 场景 2：批量文档处理
1. `list_markdown_files` - 查看目标文件
2. `quick_config_parallel_jobs` - 设置并行数
3. `batch_convert_md_to_docx` - 执行批量转换

### 场景 3：问题诊断
1. `validate_markdown_file` - 检查问题文件
2. `quick_config_debug_mode` - 启用调试模式
3. `convert_md_to_docx` - 重新转换查看详情

### 场景 4：配置管理
1. `configure_converter` - 查看或更新配置
2. 快速配置工具 - 快速调整常用设置
3. `get_conversion_status` - 验证配置更改

## 📝 最佳实践

1. **路径使用**: 始终使用绝对路径
2. **批量处理**: 先小批量测试，再大批量处理
3. **错误处理**: 启用调试模式获取详细信息
4. **性能优化**: 根据系统性能调整并行任务数
5. **配置管理**: 定期检查和备份配置设置
