# MCP 论文研究助手 - Beta 版本

基于 Model Context Protocol (MCP) 的统一学术论文研究工具，提供全面的论文分析、PDF处理和文献综述生成功能。

## ✨ 核心特性

- 🔍 **智能论文搜索**: 支持关键词、作者、ArXiv等多维度搜索
- 📊 **引用关系分析**: 深度分析论文引用网络和学术影响力
- 📄 **PDF智能处理**: ArXiv论文下载、文本提取和格式转换
- 📚 **文献综述生成**: 自动化生成结构化文献综述
- 🏗️ **模块化架构**: 18个专业工具函数，易于扩展和维护
- 🚀 **异步高性能**: 全异步实现，支持批量处理和并发操作

## 📁 项目结构

```
beta/
├── main.py                      # 🚀 MCP服务器入口 (180行精简实现)
├── paper_analysis_tools.py      # 📊 论文分析工具 (13个函数)
├── pdf_processing_tools.py      # 📄 PDF处理工具 (4个函数)
├── service_tools.py             # ℹ️  服务信息工具 (1个函数)
├── semantic_scholar_client.py   # 🔗 Semantic Scholar API客户端
├── arxiv_client.py              # 📚 ArXiv API客户端
├── paper_manager.py             # 📋 论文管理和文件操作
├── models.py                    # 📐 数据模型定义
├── config.py                    # ⚙️  配置管理
├── utils.py                     # 🛠️  工具函数
├── demo.py                      # 🎯 功能演示脚本
├── API_Documentation.md         # 📖 完整API文档
└── requirements.txt             # 📦 依赖包列表

test_beta/
├── test_*.py                    # 🧪 各模块测试文件 (90个测试用例)
├── run_tests.py                 # 🏃 测试运行器
└── conftest.py                  # ⚙️  测试配置
```

### 🏗️ 模块化设计

- **主服务器**: <mcfile name="main.py" path="/Users/yuning/workspace/MCP/beta/main.py"></mcfile> - 180行精简入口，注册18个工具函数
- **论文分析**: <mcfile name="paper_analysis_tools.py" path="/Users/yuning/workspace/MCP/beta/paper_analysis_tools.py"></mcfile> - 13个专业论文分析工具
- **PDF处理**: <mcfile name="pdf_processing_tools.py" path="/Users/yuning/workspace/MCP/beta/pdf_processing_tools.py"></mcfile> - 4个PDF处理和转换工具
- **服务信息**: <mcfile name="service_tools.py" path="/Users/yuning/workspace/MCP/beta/service_tools.py"></mcfile> - 服务状态和工具列表

## 主要功能

### 1. 论文搜索与获取
- **关键词搜索**：支持高级过滤（年份、期刊、引用数）
- **作者搜索**：查找特定作者的所有论文
- **ArXiv集成**：直接从ArXiv获取论文信息
- **论文详情**：获取完整的论文元数据

### 2. 引用关系分析
- **引用分析**：分析论文的引用和被引用关系
- **推荐系统**：基于论文内容的智能推荐
- **批量处理**：高效处理大量论文数据

### 3. 论文管理
- **Markdown导出**：将论文信息保存为结构化Markdown
- **灵活分类**：支持自定义主题分类和组织方式
- **本地搜索**：在已保存的论文中搜索

### 4. 文献综述生成
- **需求驱动**：根据特定需求组织论文
- **自动分类**：智能分组相关论文
- **格式化输出**：生成专业的文献综述

## 🚀 快速开始

### 1. 📦 安装依赖
```bash
cd /Users/yuning/workspace/MCP/beta
pip install -r requirements.txt
```

### 2. ⚙️ 配置环境变量（可选）
```bash
export SEMANTIC_SCHOLAR_API_KEY="your_api_key_here"
export DEBUG_MODE="true"  # 启用调试模式
```

### 3. 🎯 启动MCP服务器
```bash
# 启动服务器（使用STDIO传输协议）
python main.py

# 启用调试模式
python main.py --debug

# 查看所有可用工具
python main.py --list-tools
```

**注意**: MCP服务器使用STDIO传输协议，通常由MCP客户端（如Claude Desktop）自动启动和管理。

### 4. 🧪 运行测试
```bash
cd ../test_beta
python run_tests.py
```

### 5. 🎮 功能演示
```bash
python demo.py  # 运行功能演示脚本
```

## 🛠️ API功能列表

### 📊 论文分析工具 (13个)
- `analyze_paper_citations(paper_identifier)` - 分析论文引用关系
- `get_paper_details(paper_id)` - 获取论文详细信息
- `get_paper_recommendations(paper_id)` - 获取相关论文推荐
- `search_papers_by_keywords(query, year, venue, min_citation_count)` - 关键词搜索
- `search_papers_by_author(author_name)` - 作者搜索
- `search_arxiv_papers(query, sort_by)` - ArXiv搜索
- `search_papers_in_collection(keyword)` - 本地搜索
- `get_arxiv_paper(arxiv_id)` - 获取ArXiv论文
- `save_paper_to_markdown(paper_id, topic, notes)` - 保存论文到Markdown
- `save_arxiv_paper_to_markdown(arxiv_id, topic, notes)` - 保存ArXiv论文
- `organize_papers_by_topic()` - 按主题组织论文
- `generate_literature_review(topic, requirements)` - 生成文献综述
- `create_requirement_based_review(paper_ids, requirements)` - 创建需求驱动的综述

### 📄 PDF处理工具 (4个)
- `download_arxiv_pdf(arxiv_id, save_path, filename)` - 下载ArXiv PDF文件
- `extract_pdf_text(pdf_path, start_page, end_page)` - 提取PDF文本内容
- `convert_pdf_to_text(pdf_path, output_path, start_page, end_page)` - 将PDF转换为文本文件
- `process_arxiv_paper(arxiv_id, download_pdf, extract_text)` - 一站式ArXiv论文处理

### ℹ️ 服务信息工具 (1个)
- `get_service_info()` - 获取服务信息和工具列表

> 📖 **详细文档**: 查看 <mcfile name="API_Documentation.md" path="/Users/yuning/workspace/MCP/beta/API_Documentation.md"></mcfile> 获取完整的API参数说明和使用示例。

## 🤖 MCP客户端集成

本服务器完全兼容 Model Context Protocol (MCP) 标准，可以与以下客户端无缝集成：

### 🎯 Claude Desktop 集成
在 Claude Desktop 的配置文件中添加：
```json
{
  "mcpServers": {
    "paper-research-assistant": {
      "command": "python",
      "args": ["/Users/yuning/workspace/MCP/beta/main.py"],
      "env": {
        "SEMANTIC_SCHOLAR_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### 🔧 其他MCP客户端
- **Trae AI**: 使用内置的MCP支持
- **自定义客户端**: 通过STDIO协议连接
- **编程接口**: 使用 `fastmcp.Client` 进行程序化访问

### 💡 使用建议
1. **智能论文搜索**：让AI根据你的研究需求找到相关论文
2. **引用关系分析**：深入了解论文的学术影响和发展脉络
3. **文献综述生成**：自动化创建结构化的研究综述
4. **PDF批量处理**：高效处理大量学术文档

## 💡 使用示例

### 📊 分析单篇论文
```python
# 分析论文引用关系
result = await analyze_paper_citations("2504.20073")
print(f"找到 {result['data']['total_citations']} 篇引用论文")
print(f"被引用 {result['data']['total_references']} 次")
```

### 🔍 搜索相关研究
```python
# 高级关键词搜索
result = await search_papers_by_keywords(
    query="reinforcement learning LLM",
    year="2023-2024",
    min_citation_count=10
)
print(f"找到 {len(result['data']['papers'])} 篇相关论文")
```

### 📄 处理ArXiv论文
```python
# 一站式处理ArXiv论文
result = await process_arxiv_paper(
    arxiv_id="2504.20073",
    download_pdf=True,
    extract_text=True
)
print(f"PDF已下载到: {result['data']['pdf_path']}")
print(f"文本已提取，共 {result['data']['text_stats']['total_pages']} 页")
```

### 📚 生成文献综述
```python
# 创建需求驱动的文献综述
result = await create_requirement_based_review(
    paper_ids=["paper1", "paper2", "paper3"],
    requirements=["多轮对话", "自我进化", "强化学习"]
)
print("文献综述已生成:", result['data']['review_path'])
```

### 🎯 演示脚本
运行 <mcfile name="demo.py" path="/Users/yuning/workspace/MCP/beta/demo.py"></mcfile> 查看完整的功能演示：
```bash
python demo.py
```

## ⚙️ 配置选项

在 <mcfile name="config.py" path="/Users/yuning/workspace/MCP/beta/config.py"></mcfile> 中可以调整：

- **API配置**: Semantic Scholar API密钥和基础URL
- **速率限制**: 请求间隔和重试策略 (默认1秒间隔，最多3次重试)
- **文件路径**: 论文保存目录和文件命名格式
- **调试模式**: 详细日志输出和错误追踪
- **批处理**: 并发请求数量和超时设置

### 🔧 环境变量
```bash
# Semantic Scholar API密钥（可选，提高请求限制）
export SEMANTIC_SCHOLAR_API_KEY="your_api_key_here"

# 启用调试模式
export DEBUG_MODE="true"

# 自定义论文保存路径
export PAPERS_DIR="/path/to/your/papers"
```

## 🧪 测试覆盖

项目包含完整的测试套件，覆盖所有核心功能：

- **测试用例**: 90个测试用例，100%通过率
- **代码覆盖率**: 51%覆盖率，涵盖关键功能路径
- **模块测试**: 每个工具模块都有独立的测试文件
- **集成测试**: 端到端功能验证

```bash
# 运行完整测试套件
cd test_beta && python run_tests.py

# 运行特定模块测试
python -m pytest test_paper_analysis_tools.py -v

# 生成覆盖率报告
python run_tests.py --coverage
```

## 🔧 故障排除

### 常见问题

1. **🚫 API限制错误 (429)**
   - **现象**: `Rate limit exceeded` 错误
   - **解决**: 工具会自动重试，或设置 `SEMANTIC_SCHOLAR_API_KEY` 提高限制

2. **🌐 网络连接问题**
   - **现象**: 请求超时或连接失败
   - **解决**: 检查网络连接，确认API服务可访问

3. **📁 文件权限错误**
   - **现象**: 无法保存论文或创建目录
   - **解决**: 确保对 `papers/` 目录有写入权限

4. **📦 依赖包问题**
   - **现象**: `ModuleNotFoundError` 或导入错误
   - **解决**: 运行 `pip install -r requirements.txt` 重新安装依赖

5. **📄 PDF处理失败**
   - **现象**: PDF下载或文本提取失败
   - **解决**: 确保安装了 `pypdf` 库: `pip install pypdf`

### 🐛 调试模式

启用调试模式获取详细日志：
```bash
python main.py --debug
```

或设置环境变量：
```bash
export DEBUG_MODE="true"
python main.py
```

### 📞 获取帮助

- **查看工具列表**: `python main.py --list-tools`
- **API文档**: 查看 <mcfile name="API_Documentation.md" path="/Users/yuning/workspace/MCP/beta/API_Documentation.md"></mcfile>
- **功能演示**: 运行 `python demo.py`
- **测试验证**: 运行 `cd test_beta && python run_tests.py`

## 🤝 贡献指南

欢迎贡献代码和改进建议！请遵循以下准则：

### 📋 开发流程
1. **Fork项目** 并创建功能分支
2. **编写测试** 确保新功能有对应的测试用例
3. **遵循规范** 保持代码风格一致性
4. **更新文档** 反映新功能和变更
5. **提交PR** 包含清晰的变更说明

### 🧪 测试要求
- 所有新功能必须有单元测试
- 测试覆盖率不能降低
- 确保所有现有测试通过

### 📝 代码规范
- 使用类型提示 (Type Hints)
- 遵循PEP 8代码风格
- 添加详细的文档字符串
- 保持向后兼容性

## 📄 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

---

## 🎯 项目状态

- ✅ **核心功能**: 18个工具函数全部实现
- ✅ **模块化重构**: 代码结构优化完成
- ✅ **测试覆盖**: 90个测试用例，100%通过
- ✅ **文档完善**: API文档和使用指南完整
- ✅ **MCP兼容**: 完全支持MCP协议标准

**版本**: Beta 1.0.0  
**最后更新**: 2024年12月  
**维护状态**: 积极维护中 🚀