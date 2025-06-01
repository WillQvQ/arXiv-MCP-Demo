# ArXiv Citation Analyzer MCP Server

一个用于根据 arxiv 文章链接自动检索引用和被引用的文章的工具，能够汇总它们的标题、摘要、链接等信息。

## 功能特点

- ✅ **多链接格式支持**: 支持标准 arxiv 链接和 alphaxiv 链接
- ✅ **引用关系检索**: 自动获取论文的引用和被引用关系
- ✅ **论文信息汇总**: 提取论文标题、摘要、作者等详细信息
- ✅ **结构化输出**: 返回格式化的论文信息和统计数据
- ✅ **智能缓存机制**: 自动缓存已查询结果，避免重复请求，提升效率

## 📋 测试结果

已成功测试AlphaXiv链接处理：

```
🔗 测试链接: https://www.alphaxiv.org/html/2504.13958v1
📄 论文标题: ToolRL: Reward is All Tool Learning Needs
👥 作者: Hao Liang, Yifan Zhang, Xinyi Liu, Zhiwei Liu, Jie Liu, Weijie Huang, Jiahao Zhang, Wentao Zhang, Bin Cui
📅 发布日期: 2024-04-22T08:59:59Z

✅ 内容分析结果:
- 论文与工具学习相关
- 论文与强化学习相关  
- 论文与奖励机制相关
```

## 🛠️ 安装配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API 密钥（可选）

**无需 API 密钥也可使用！** Semantic Scholar API 支持无认证访问，但有速率限制（每秒1000次请求，所有用户共享）。

如需更高速率限制，可设置环境变量添加 API 密钥：

```bash
# 在终端中设置环境变量
export SEMANTIC_SCHOLAR_API_KEY="your_api_key_here"

# 或者在运行前临时设置
SEMANTIC_SCHOLAR_API_KEY="your_api_key_here" python3 arxiv_mcp_server.py
```

**速率限制对比：**
- 无 API 密钥：1000 请求/秒（所有用户共享）
- 有 API 密钥：更高的个人速率限制

## 🎯 使用方法

直接运行 `arxiv_mcp_server.py` 脚本，并调用 `analyze_paper_citations` 方法：

```python
import asyncio
from arxiv_mcp_server import ArxivMCPServer

async def main():
    server = ArxivMCPServer(debug_mode=True) # 设置 debug_mode=True 查看详细日志
    arxiv_url = "https://www.alphaxiv.org/html/2504.13958v1"
    result = await server.analyze_paper_citations(arxiv_url)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

**缓存机制说明**：
- 首次查询时，系统会从 Semantic Scholar API 获取数据，并将结果保存到 `json_files/` 目录中。
- 后续对相同 `arxiv_id` 的查询，如果 `json_files/` 目录中存在对应的缓存文件，系统将直接读取缓存数据，避免重复的网络请求，显著提高响应速度。
- 只有成功获取到完整数据时，才会生成缓存文件。如果查询失败或数据不完整，则不会保存缓存。

### 支持的链接格式

- `https://arxiv.org/abs/2504.13958`
- `https://arxiv.org/pdf/2504.13958.pdf`
- `https://www.alphaxiv.org/html/2504.13958v1`
- `2504.13958`
- `2504.13958v1`

## 检索功能说明

- 获取论文基本信息（标题、摘要、作者、发布日期）
- 检索引用该论文的相关文章
- 检索该论文引用的参考文献
- 统计引用关系数量

## 🧪 测试

运行测试脚本验证功能：

```bash
# 基础功能测试（无需API密钥）
python3 simple_test.py

# 完整功能测试（需要API密钥）
python3 test_alphaxiv.py
```

## 返回结果格式

```json
{
  "papers": {
    "main_paper": {
      "title": "论文标题",
      "abstract": "论文摘要",
      "url": "arxiv链接",
      "authors": ["作者列表"],
      "published": "发布日期",
      "arxiv_id": "arxiv ID"
    },
    "citing_papers": [...],
    "referenced_papers": [...]
  },
  "summary": {
    "total_citing": 15,
    "total_referenced": 23
  }
}
```

## API 密钥申请指南

### Semantic Scholar API
1. 访问 [Semantic Scholar API](https://www.semanticscholar.org/product/api)
2. 注册账户并申请 API 密钥
3. 设置环境变量（任选一种方式）：

```bash
# 临时设置（仅当前会话有效）
export SEMANTIC_SCHOLAR_API_KEY="your_api_key_here"

# 永久设置（添加到shell配置文件）
echo 'export SEMANTIC_SCHOLAR_API_KEY="your_api_key_here"' >> ~/.zshrc
source ~/.zshrc

# 或者在Docker中使用
-e SEMANTIC_SCHOLAR_API_KEY="your_api_key_here"
```

## 注意事项

- **无需 API 密钥即可使用**，但建议申请以获得更好性能
- 无 API 密钥时共享速率限制（1000请求/秒），高峰期可能较慢
- 有 API 密钥时享有更高的个人速率限制
- 服务专注于信息检索，不进行智能分析


## 🚀 快速上手

🎯 **快速开始**: 运行 `python3 test_alphaxiv.py` 验证基础功能！