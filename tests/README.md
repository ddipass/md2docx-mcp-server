# 🧪 测试文件

本目录包含用于测试 MD2DOCX MCP Server 各种功能的测试文件。

## 📁 目录结构

```
tests/
├── samples/           # 测试样本文件
│   ├── test_chinese.md      # 中文文档测试
│   ├── test_academic.md     # 学术论文测试
│   ├── test_english_tech.md # 英文技术文档测试
│   └── ...                  # 其他测试文件
└── README.md         # 本文件
```

## 📝 测试文件说明

### 基础测试文件

| 文件名 | 用途 | 特点 |
|--------|------|------|
| `simple_test.md` | 基础功能测试 | 简单的标题和段落 |
| `test_document.md` | 通用文档测试 | 包含多种元素的综合测试 |

### 语言和格式测试

| 文件名 | 用途 | 特点 |
|--------|------|------|
| `test_chinese.md` | 中文文档测试 | 中文内容、表格、代码块 |
| `test_english_tech.md` | 英文技术文档测试 | 技术内容、代码示例 |

### 学术和专业测试

| 文件名 | 用途 | 特点 |
|--------|------|------|
| `test_academic.md` | 学术论文测试 | 摘要、关键词、参考文献、复杂表格 |

### 数学公式测试

| 文件名 | 用途 | 特点 |
|--------|------|------|
| `test_math_only.md` | 纯数学公式测试 | 各种数学公式和符号 |
| `test_no_math.md` | 无数学公式测试 | 验证非数学内容的处理 |

### 图片格式测试

| 文件名 | 用途 | 特点 |
|--------|------|------|
| `test_compatible_images.md` | LaTeX 兼容格式测试 | JPEG, PNG 原生支持 |
| `test_image_formats.md` | 全格式支持测试 | 包含 BMP, TIFF 等需转换格式 |
| `test_complete_image_support.md` | 完整图片处理测试 | 原生+转换格式综合测试 |

### 图片处理功能

| 功能 | 状态 | 说明 |
|------|------|------|
| **路径解析** | ✅ | 自动修复相对路径问题 |
| **格式检查** | ✅ | 自动检测兼容性并生成警告 |
| **原生支持** | ✅ | JPEG, PNG 直接支持 |
| **格式转换** | ✅ | BMP, TIFF 自动转换为 PNG |
| **转换工具** | ✅ | sips (macOS), rsvg-convert |

## 🚀 使用方法

### 单文件测试

```bash
# 测试 DOCX 转换
convert_md_to_docx("tests/samples/test_chinese.md")

# 测试 PPTX 转换  
convert_to_pptx("tests/samples/test_chinese.md")

# 测试 LaTeX 转换
convert_md_to_latex("tests/samples/test_chinese.md", "chinese", "basic")

# 测试 PDF 转换
convert_md_to_pdf_direct("tests/samples/test_chinese.md", "chinese", "basic")
```

### 批量测试

```bash
# 批量转换测试文件
batch_convert_markdown("tests/samples", ["docx", "pptx"])
```

## 🎯 测试重点

### 表格渲染测试
- `test_chinese.md` - 包含复杂中文表格
- `test_academic.md` - 包含学术数据表格

### 多级标题测试
- `test_chinese_level_fixed.md` - 测试 6 级以上标题
- `test_academic.md` - 复杂的章节结构

### 中文支持测试
- `test_chinese.md` - 中文字符、标点、格式
- `test_chinese_fixed.md` - 修复后的中文处理

### 数学公式测试
- `test_math_only.md` - 各种数学公式
- `test_academic.md` - 学术论文中的公式

## 📊 测试结果

所有测试文件都应该能够：
- ✅ 成功转换为 DOCX 格式
- ✅ 成功转换为 PPTX 格式（符合 MD2PPTX 格式要求的文件）
- ✅ 成功转换为 LaTeX 格式
- ✅ 成功编译为 PDF 格式

## 🔧 添加新测试文件

1. 在 `samples/` 目录中创建新的 `.md` 文件
2. 使用描述性的文件名（如 `test_功能描述.md`）
3. 在文件中包含要测试的特定功能
4. 更新本 README 文件的说明表格

## 🐛 问题报告

如果测试文件转换失败，请：
1. 检查文件格式是否正确
2. 查看错误日志
3. 在 GitHub Issues 中报告问题，包含：
   - 测试文件名
   - 转换格式
   - 错误信息
   - 预期结果
