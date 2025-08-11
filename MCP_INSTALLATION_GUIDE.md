# 🚀 MCP 安装指南 - MD2DOCX 统一转换服务器

本指南将帮助你在 Amazon Q CLI 中快速安装和配置 MD2DOCX MCP 服务器。

## 📋 前置要求

- ✅ Python 3.10 或更高版本
- ✅ [uv](https://docs.astral.sh/uv/) 包管理器
- ✅ Git（用于克隆仓库和子模块）
- ✅ Amazon Q CLI

## 🎯 一键安装（推荐）

### 步骤 1: 克隆项目

```bash
# 克隆项目并自动初始化所有子模块
git clone --recursive https://github.com/ddipass/md2docx-mcp-server.git

# 进入项目目录
cd md2docx-mcp-server
```

### 步骤 2: 安装依赖

```bash
# 自动创建虚拟环境并安装所有依赖
uv sync
```

### 步骤 3: 获取项目绝对路径

```bash
# 获取当前项目的绝对路径
pwd
```

**复制输出的路径**，例如：`/Users/username/md2docx-mcp-server`

### 步骤 4: 配置 Amazon Q CLI

编辑或创建 `~/.aws/amazonq/mcp.json` 文件：

```json
{
  "mcpServers": {
    "MD2DOCX": {
      "command": "/Users/username/md2docx-mcp-server/.venv/bin/mcp",
      "args": [
        "run",
        "/Users/username/md2docx-mcp-server/server.py"
      ],
      "cwd": "/Users/username/md2docx-mcp-server"
    }
  }
}
```

**⚠️ 重要**: 将上面的 `/Users/username/md2docx-mcp-server` 替换为步骤 3 中获取的实际路径。

### 步骤 5: 验证安装

1. 启动 Amazon Q CLI
2. 运行以下命令验证安装：

```
使用 get_conversion_status 工具检查服务器状态
```

如果看到以下输出，说明安装成功：

```
🔍 统一转换器状态
🖥️  服务器信息:
- 服务器名称: MD2DOCX-Converter (统一版)
📊 格式支持:
- 支持的格式: DOCX, PPTX
- 可用转换器: DOCX, PPTX
```

## 🔧 手动安装（高级用户）

如果你需要更多控制，可以使用手动安装方式：

### 步骤 1: 克隆主项目

```bash
git clone https://github.com/ddipass/md2docx-mcp-server.git
cd md2docx-mcp-server
```

### 步骤 2: 初始化子模块

```bash
# 初始化并更新所有子模块
git submodule update --init --recursive
```

### 步骤 3: 创建虚拟环境

```bash
# 使用 uv 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
uv sync
```

### 步骤 4: 验证子模块

```bash
# 检查子模块状态
git submodule status

# 应该看到类似输出：
# 5cfe3894fc630a717ec24f375f2f8866c44c4be8 md2docx (heads/master)
# fd8e22b444231bba835d0b868aef0580a6342ee1 md2pptx (v5.4.4-5-gfd8e22b)
```

### 步骤 5: 测试转换功能

```bash
# 测试 DOCX 转换
python -c "
import asyncio
from core.unified_converter_manager import get_unified_converter_manager

async def test():
    converter = get_unified_converter_manager()
    result = await converter.convert_single_file('README.md', 'docx')
    print('DOCX 转换:', '✅ 成功' if result['success'] else '❌ 失败')
    
    result = await converter.convert_single_file('README.md', 'pptx')
    print('PPTX 转换:', '✅ 成功' if result['success'] else '❌ 失败')

asyncio.run(test())
"
```

## 🎯 快速测试

安装完成后，你可以立即测试以下功能：

### 基本转换测试

```
# 转换为 DOCX
convert_markdown("/path/to/your/file.md", "docx")

# 转换为 PPTX
convert_markdown("/path/to/your/file.md", "pptx")

# 同时转换为两种格式
convert_markdown("/path/to/your/file.md", "both")
```

### 批量转换测试

```
# 批量转换为多种格式
batch_convert_markdown("/path/to/your/markdown/folder", ["docx", "pptx"])
```

### 模板转换测试

```
# 使用内置模板转换 PPTX
convert_with_template("/path/to/your/file.md", "pptx", "Martin Template.pptx")
```

## 🚨 常见问题解决

### 问题 1: 子模块未初始化

**症状**: 错误信息包含 "项目路径不存在"

**解决方案**:
```bash
cd md2docx-mcp-server
git submodule update --init --recursive
```

### 问题 2: Python 环境问题

**症状**: 找不到 python-pptx 或其他依赖

**解决方案**:
```bash
cd md2docx-mcp-server
source .venv/bin/activate
uv sync
```

### 问题 3: 权限问题

**症状**: "Permission denied" 错误

**解决方案**:
```bash
chmod +x .venv/bin/mcp
chmod +x .venv/bin/python
```

### 问题 4: MCP 配置路径错误

**症状**: Amazon Q CLI 无法找到服务器

**解决方案**:
1. 确保使用绝对路径
2. 检查路径中没有空格或特殊字符
3. 验证 `.venv/bin/mcp` 文件存在

### 问题 5: 转换失败

**症状**: 转换过程中出现错误

**解决方案**:
```bash
# 启用调试模式
quick_config_debug_mode(True)

# 检查详细状态
get_conversion_status()

# 验证文件
validate_markdown_file("/path/to/your/file.md")
```

## 📊 功能验证清单

安装完成后，请验证以下功能：

- [ ] ✅ 服务器状态检查正常
- [ ] ✅ DOCX 转换功能正常
- [ ] ✅ PPTX 转换功能正常
- [ ] ✅ 批量转换功能正常
- [ ] ✅ 模板转换功能正常
- [ ] ✅ 配置管理功能正常

## 🔄 更新指南

当有新版本发布时，更新步骤：

```bash
cd md2docx-mcp-server

# 拉取最新代码
git pull

# 更新子模块
git submodule update --remote

# 更新依赖
uv sync

# 重启 Amazon Q CLI
```

## 📞 获取帮助

如果遇到问题：

1. 🔍 查看 [故障排除指南](README.md#故障排除)
2. 📋 运行 `get_conversion_status()` 获取详细状态
3. 🐛 在 [GitHub Issues](https://github.com/ddipass/md2docx-mcp-server/issues) 报告问题
4. 📖 查看 [详细文档](DEPLOYMENT_GUIDE.md)

---

**🎉 安装完成！现在你可以享受统一的 Markdown 文档转换体验了！**
