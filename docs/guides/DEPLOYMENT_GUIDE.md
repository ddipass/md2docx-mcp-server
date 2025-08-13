# 🚀 MD2DOCX MCP Server 部署指南

## 📦 方案2：Git Submodule 集成方案

本项目采用 Git Submodule 方式集成 md2docx 项目，实现开箱即用的部署体验。

### 🎯 方案优势

- ✅ **开箱即用**: 无需单独安装 md2docx 项目
- ✅ **版本控制**: 通过 submodule 锁定特定版本
- ✅ **自动更新**: 可以轻松更新到最新版本
- ✅ **独立部署**: 单一仓库包含所有依赖
- ✅ **标准实践**: 使用 Git 标准的 submodule 机制

### 📋 项目结构

```
md2docx-mcp-server/
├── server.py                 # 主 MCP 服务器文件
├── core/                     # 核心模块
│   ├── config_manager.py     # 配置管理器
│   └── converter_manager.py  # 转换管理器
├── md2docx/                  # Git Submodule (md2docx 项目)
│   ├── src/
│   │   ├── cli.py           # md2docx CLI 接口
│   │   └── converter/       # 转换器模块
│   └── requirements.txt
├── config/                   # 配置文件目录
├── output/                   # 默认输出目录
└── .gitmodules              # Git submodule 配置
```

## 🛠️ 部署步骤

### 1. 克隆项目（包含子模块）

```bash
# 方式1：克隆时同时初始化子模块
git clone --recursive https://github.com/your-username/md2docx-mcp-server.git

# 方式2：先克隆再初始化子模块
git clone https://github.com/your-username/md2docx-mcp-server.git
cd md2docx-mcp-server
git submodule update --init --recursive
```

### 2. 安装依赖

```bash
cd md2docx-mcp-server
uv sync
```

### 3. 激活虚拟环境

```bash
source .venv/bin/activate
```

### 4. 验证安装

```bash
python server.py
# 或者通过 MCP 工具测试
```

## 🔄 子模块管理

### 更新子模块到最新版本

```bash
# 更新到最新版本
git submodule update --remote md2docx

# 提交更新
git add md2docx
git commit -m "Update md2docx submodule to latest version"
```

### 切换到特定版本

```bash
cd md2docx
git checkout v1.0.0  # 切换到特定标签
cd ..
git add md2docx
git commit -m "Pin md2docx to version v1.0.0"
```

### 查看子模块状态

```bash
git submodule status
```

## 🔧 配置说明

### 默认配置

项目已配置为使用相对路径 `md2docx`，指向内置的子模块：

```json
{
  "server_settings": {
    "md2docx_project_path": "md2docx",
    "use_subprocess": true,
    "use_python_import": false
  }
}
```

### 自定义配置

如果需要使用外部的 md2docx 项目：

```python
# 通过 MCP 工具配置
quick_config_md2docx_path("/path/to/external/md2docx")
```

## 🚀 Amazon Q CLI 配置

在 `~/.aws/amazonq/mcp.json` 中添加：

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

## 🔍 故障排除

### 子模块未初始化

**症状**: `MD2DOCX 项目路径不存在: md2docx`

**解决方案**:
```bash
git submodule update --init --recursive
```

### 子模块版本冲突

**症状**: 子模块指向错误的提交

**解决方案**:
```bash
git submodule update --remote
git add md2docx
git commit -m "Update submodule"
```

### 权限问题

**症状**: 无法执行 md2docx CLI

**解决方案**:
```bash
chmod +x md2docx/src/cli.py
```

## 📈 版本管理最佳实践

1. **锁定版本**: 在生产环境中锁定特定版本
2. **定期更新**: 定期检查和更新子模块
3. **测试验证**: 更新后进行完整测试
4. **文档记录**: 记录版本变更和兼容性

## 🎯 开发者指南

### 修改子模块

```bash
cd md2docx
# 进行修改
git add .
git commit -m "Fix: some issue"
git push origin main

cd ..
git add md2docx
git commit -m "Update md2docx with fixes"
```

### 贡献代码

1. Fork 主项目和子模块项目
2. 在各自项目中进行修改
3. 提交 Pull Request
4. 更新子模块引用

这种方案确保了项目的独立性和可维护性，同时提供了最佳的用户体验！
