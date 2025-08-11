# 📊 md2pptx 模板约束和 AI 内容生成指导

## 🎯 概述

md2pptx 对 Markdown 格式有严格的要求，特别是与模板相关的约束。本指南帮助大模型生成完全兼容 md2pptx 的 Markdown 内容。

## 🚨 关键约束 (必须遵循)

### 1. 元数据头部 (Metadata Header)
**必须**在文件开头包含元数据，以空行结束：

```markdown
template: Martin Template.pptx
pageTitleSize: 24
sectionTitleSize: 30
baseTextSize: 20
numbers: no
style.fgcolor.blue: 0000FF
style.fgcolor.red: FF0000
style.fgcolor.green: 00FF00

# 这里开始正文内容
```

### 2. 标题层次结构
md2pptx 使用特定的标题层次创建不同类型的幻灯片：

- `# 标题` → **演示标题页** (封面)
- `## 标题` → **章节分隔页** (Section Slide)  
- `### 标题` → **内容幻灯片** (Content Slide)
- `#### 标题` → **卡片标题** (Card Title)

### 3. 内容约束
- 每页要点数量：3-6 个
- 避免过长的文本
- 保持层次化结构

## 🛠️ MCP 工具使用

### 📋 获取格式指导
```
使用 get_md2pptx_format_guide 工具获取详细的格式指导
```

**示例**:
```
get_md2pptx_format_guide("business", "medium")
```

### 🎯 AI 内容生成指导
```
使用 md2pptx_content_generator Prompt 获取 AI 内容生成指导
```

**示例**:
```
md2pptx_content_generator("AI项目提案", "business", "medium", "管理层")
```

## 📝 完整示例

### 输入 (给 AI 的指令)
```
请使用 md2pptx_content_generator 为"数字化转型战略"主题生成一个商务演示，
目标受众是公司高管，需要中等长度的演示文稿。
```

### 输出 (AI 应该生成的格式)
```markdown
template: Martin Template.pptx
pageTitleSize: 24
sectionTitleSize: 30
baseTextSize: 20
numbers: no
style.fgcolor.blue: 0000FF
style.fgcolor.red: FF0000
style.fgcolor.green: 00FF00

# 数字化转型战略
企业未来发展蓝图

## 背景与挑战

### 市场环境分析
* 数字化浪潮席卷各行各业
* 客户期望快速变化
* 竞争对手加速数字化布局
* 传统业务模式面临冲击

### 内部现状评估
* 技术基础设施相对落后
* 数据孤岛现象严重
* 员工数字化技能待提升
* 业务流程自动化程度低

## 转型战略

### 战略目标
* 提升客户体验满意度
* 优化运营效率
* 创新业务模式
* 增强市场竞争力

### 核心举措
<!-- md2pptx: cardlayout: horizontal -->

#### 技术升级
* 云平台建设
* 数据中台构建
* AI/ML 能力建设

#### 流程优化
* 业务流程重塑
* 自动化部署
* 敏捷开发模式

#### 人才培养
* 数字化技能培训
* 组织架构调整
* 创新文化建设

## 实施路径

### 实施计划
|阶段|时间|重点任务|预期成果|
|:---|:---|:---|:---|
|第一阶段|Q1-Q2|基础设施建设|技术平台就绪|
|第二阶段|Q3-Q4|业务流程改造|效率提升30%|
|第三阶段|次年|创新业务拓展|新收入来源|

### 预期效益
* 运营成本降低25%
* 客户满意度提升40%
* 新业务收入占比达20%
* 市场响应速度提升50%

## 总结与下一步

### 关键成功因素
* 高层领导全力支持
* 充足的资源投入
* 全员参与和配合
* 持续的监控和调整

### 立即行动
* 成立数字化转型委员会
* 启动技术平台选型
* 制定详细实施计划
* 开展员工培训项目
```

## 🎨 高级功能示例

### 卡片布局
```markdown
### 方案对比
<!-- md2pptx: cardlayout: horizontal -->
<!-- md2pptx: cardcolour: BACKGROUND 2 -->

#### 方案A
* 成本低
* 风险小
* 周期长

#### 方案B
* 成本高
* 收益大
* 周期短
```

### 表格数据
```markdown
### 关键指标
|指标|当前|目标|
|:---|---:|---:|
|效率|75%|90%|
|成本|$100K|$80K|
```

## ✅ 质量检查清单

### 格式检查
- [ ] 包含完整的元数据头部
- [ ] 使用正确的标题层次 (#, ##, ###, ####)
- [ ] 每个标题下都有内容
- [ ] 要点数量适中 (3-6个/页)

### 内容检查
- [ ] 主题聚焦，逻辑清晰
- [ ] 适合目标受众
- [ ] 支持演讲流程
- [ ] 关键信息突出

## 🚀 在 Q CLI 中的使用

### 1. 获取格式指导
```
使用 get_md2pptx_format_guide 工具，参数设置为 "business" 和 "medium"
```

### 2. 生成内容指导
```
使用 md2pptx_content_generator Prompt，主题设置为你的演示主题
```

### 3. 转换为 PPTX
```
使用 convert_markdown 工具，格式设置为 "pptx"，模板使用 "Martin Template.pptx"
```

### 4. 验证结果
```
使用 get_conversion_status 检查转换状态和结果
```

## 💡 最佳实践

1. **始终从元数据开始**: 确保每个 md2pptx 文件都有完整的元数据头部
2. **遵循标题层次**: 严格按照 #/##/###/#### 的层次结构
3. **控制内容密度**: 每页要点不超过 6 个
4. **合理使用高级功能**: 卡片、表格等功能要适度使用
5. **测试转换结果**: 生成内容后及时转换测试

通过遵循这些指导，AI 模型可以生成完美兼容 md2pptx 的 Markdown 内容！🎉
