# MCP 论文研究助手 API 文档

## 概述

MCP 论文研究助手是一个基于 Model Context Protocol (MCP) 的服务器，提供了全面的学术论文研究工具。该服务器包含 18 个工具函数，分为三大类：论文分析工具、PDF 处理工具和服务信息工具。

## 服务器信息

- **服务名称**: MCP Paper Research Assistant
- **版本**: 1.0.0
- **描述**: 统一的学术论文研究和分析工具集
- **主要功能**: 论文搜索、引用分析、PDF处理、文献综述生成

## 工具分类

### 📊 论文分析工具 (13个)
### 📄 PDF处理工具 (4个)
### ℹ️ 服务信息工具 (1个)

---

## 📊 论文分析工具

### 1. analyze_paper_citations
**功能**: 分析论文的引用关系

**参数**:
- `paper_id` (string): 论文ID（ArXiv ID、DOI或Semantic Scholar ID）
- `include_references` (boolean, 可选): 是否包含参考文献，默认true
- `include_citations` (boolean, 可选): 是否包含引用该论文的文献，默认true
- `debug` (boolean, 可选): 调试模式，默认false

**返回**: 包含引用和被引论文列表的JSON对象

**示例**:
```json
{
  "success": true,
  "data": {
    "paper_title": "论文标题",
    "citations": [...],
    "references": [...]
  }
}
```

### 2. search_papers_by_keywords
**功能**: 通过关键词搜索论文

**参数**:
- `keywords` (string): 搜索关键词
- `year_filter` (string, 可选): 年份过滤器（如"2020-2023"）
- `venue_filter` (string, 可选): 会议/期刊过滤器
- `min_citations` (integer, 可选): 最小引用数
- `limit` (integer, 可选): 结果数量限制，默认10
- `debug` (boolean, 可选): 调试模式，默认false

**返回**: 搜索到的论文列表

### 3. search_papers_by_author
**功能**: 根据作者搜索论文

**参数**:
- `author_name` (string): 作者姓名
- `limit` (integer, 可选): 结果数量限制，默认10
- `debug` (boolean, 可选): 调试模式，默认false

**返回**: 该作者的论文列表

### 4. get_paper_details
**功能**: 获取论文详细信息

**参数**:
- `paper_id` (string): 论文ID
- `include_citations` (boolean, 可选): 是否包含引用信息，默认false
- `include_references` (boolean, 可选): 是否包含参考文献，默认false
- `include_recommendations` (boolean, 可选): 是否包含推荐论文，默认false
- `debug` (boolean, 可选): 调试模式，默认false

**返回**: 论文的详细信息

### 5. get_arxiv_paper
**功能**: 通过ArXiv ID获取论文信息

**参数**:
- `arxiv_id` (string): ArXiv论文ID
- `debug` (boolean, 可选): 调试模式，默认false

**返回**: ArXiv论文的详细信息

### 6. search_arxiv_papers
**功能**: 在ArXiv上搜索论文

**参数**:
- `query` (string): 搜索查询
- `max_results` (integer, 可选): 最大结果数，默认10
- `sort_by` (string, 可选): 排序方式，默认"relevance"
- `sort_order` (string, 可选): 排序顺序，默认"descending"
- `debug` (boolean, 可选): 调试模式，默认false

**返回**: ArXiv搜索结果列表

### 7. save_paper_to_markdown
**功能**: 将论文信息保存为Markdown格式

**参数**:
- `paper_id` (string): 论文ID
- `output_path` (string, 可选): 输出文件路径
- `include_citations` (boolean, 可选): 是否包含引用信息，默认true
- `include_references` (boolean, 可选): 是否包含参考文献，默认true
- `debug` (boolean, 可选): 调试模式，默认false

**返回**: 保存结果和文件路径

### 8. save_arxiv_paper_to_markdown
**功能**: 将ArXiv论文保存为Markdown格式

**参数**:
- `arxiv_id` (string): ArXiv论文ID
- `output_path` (string, 可选): 输出文件路径
- `debug` (boolean, 可选): 调试模式，默认false

**返回**: 保存结果和文件路径

### 9. organize_papers_by_topic
**功能**: 按主题组织论文

**参数**:
- `paper_ids` (array): 论文ID列表
- `debug` (boolean, 可选): 调试模式，默认false

**返回**: 按主题分组的论文列表和统计信息

### 10. generate_literature_review
**功能**: 为特定主题生成文献综述

**参数**:
- `topic` (string): 研究主题
- `max_papers` (integer, 可选): 最大论文数量，默认20
- `output_path` (string, 可选): 输出文件路径
- `debug` (boolean, 可选): 调试模式，默认false

**返回**: 生成的文献综述内容和保存路径

### 11. create_requirement_based_review
**功能**: 基于特定论文和需求创建文献综述

**参数**:
- `base_paper_id` (string): 基础论文ID
- `requirements` (string): 综述需求描述
- `output_path` (string, 可选): 输出文件路径
- `debug` (boolean, 可选): 调试模式，默认false

**返回**: 定制化文献综述内容

### 12. search_papers_in_collection
**功能**: 在本地论文集合中搜索

**参数**:
- `keywords` (string): 搜索关键词
- `collection_path` (string, 可选): 论文集合路径
- `debug` (boolean, 可选): 调试模式，默认false

**返回**: 本地搜索结果

### 13. get_paper_recommendations
**功能**: 获取基于某篇论文的推荐论文

**参数**:
- `paper_id` (string): 基础论文ID
- `limit` (integer, 可选): 推荐数量限制，默认10
- `debug` (boolean, 可选): 调试模式，默认false

**返回**: 推荐论文列表

---

## 📄 PDF处理工具

### 1. download_arxiv_pdf
**功能**: 从ArXiv下载PDF文件

**参数**:
- `arxiv_id` (string): ArXiv论文ID
- `save_path` (string, 可选): 保存路径，默认"./downloads"
- `filename` (string, 可选): 文件名（不含扩展名）
- `debug` (boolean, 可选): 调试模式，默认false

**返回**: 下载结果和文件信息

**示例**:
```json
{
  "success": true,
  "data": {
    "file_path": "/path/to/downloaded.pdf",
    "file_size": 1024000,
    "arxiv_id": "2301.00001"
  }
}
```

### 2. extract_pdf_text
**功能**: 从PDF文件中提取文本

**参数**:
- `pdf_path` (string): PDF文件路径
- `start_page` (integer, 可选): 起始页码，默认1
- `end_page` (integer, 可选): 结束页码
- `debug` (boolean, 可选): 调试模式，默认false

**返回**: 提取的文本内容和统计信息

### 3. convert_pdf_to_text
**功能**: 将PDF转换为纯文本文件

**参数**:
- `pdf_path` (string): PDF文件路径
- `output_path` (string, 可选): 输出文本文件路径
- `start_page` (integer, 可选): 起始页码，默认1
- `end_page` (integer, 可选): 结束页码
- `include_page_numbers` (boolean, 可选): 是否包含页码标记，默认true
- `encoding` (string, 可选): 文本编码，默认"utf-8"
- `debug` (boolean, 可选): 调试模式，默认false

**返回**: 转换结果和输出文件信息

### 4. process_arxiv_paper
**功能**: 一站式处理ArXiv论文（下载+文本提取）

**参数**:
- `arxiv_id` (string): ArXiv论文ID
- `save_path` (string, 可选): 保存路径，默认"./downloads"
- `extract_text` (boolean, 可选): 是否提取文本，默认true
- `text_output_path` (string, 可选): 文本输出路径
- `debug` (boolean, 可选): 调试模式，默认false

**返回**: 下载和文本提取的完整结果

---

## ℹ️ 服务信息工具

### 1. get_service_info
**功能**: 获取MCP服务器信息和可用工具列表

**参数**:
- `debug` (boolean, 可选): 调试模式，默认false

**返回**: 服务器详细信息和工具分类列表

**示例**:
```json
{
  "success": true,
  "data": {
    "service_name": "MCP Paper Research Assistant",
    "version": "1.0.0",
    "description": "统一的学术论文研究和分析工具集",
    "available_tools": {
      "paper_analysis_tools": 13,
      "pdf_processing_tools": 4,
      "service_tools": 1
    },
    "pdf_processing_available": true
  }
}
```

---

## 使用说明

### 启动服务器

```bash
# 进入项目目录
cd /path/to/MCP/beta

# 启动MCP服务器（使用STDIO传输协议）
python main.py

# 启用调试模式
python main.py --debug

# 查看所有可用工具
python main.py --list-tools
```

**注意**: MCP服务器使用STDIO传输协议，通常由MCP客户端（如Claude Desktop）自动启动和管理，不需要手动指定端口。

### 依赖要求

- Python 3.8+
- 必需依赖：`mcp`, `httpx`, `arxiv`
- PDF处理依赖：`pypdf`（可选，用于PDF相关功能）

### 安装依赖

```bash
pip install mcp httpx arxiv pypdf
```

### 注意事项

1. **API限制**: 所有工具使用Semantic Scholar API，请遵守其使用限制
2. **调试模式**: 所有工具都支持`debug`参数，用于输出详细日志
3. **错误处理**: 所有工具返回统一格式的JSON，包含`success`字段和错误信息
4. **异步实现**: 所有工具函数都是异步实现，确保高性能
5. **PDF功能**: PDF处理功能需要安装`pypdf`库，否则相关工具将不可用

### 返回格式

所有工具函数都返回以下格式的JSON对象：

```json
{
  "success": true/false,
  "data": {}, // 成功时的数据
  "error": "错误信息", // 失败时的错误描述
  "debug_info": {} // 调试模式下的额外信息
}
```

---

## 更新日志

### v1.0.0 (当前版本)
- ✅ 模块化重构完成
- ✅ 18个工具函数分类整理
- ✅ 完整的测试覆盖（90个测试用例）
- ✅ 统一的错误处理和返回格式
- ✅ 完整的API文档

---

*本文档最后更新时间: 2024年*