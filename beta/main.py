#!/usr/bin/env python3
"""
统一MCP服务器 - 论文研究与PDF处理助手

这是一个集成的MCP服务器，提供论文分析和PDF处理功能。
所有具体的工具实现都在独立的模块中，这个文件仅作为服务入口。
"""

import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path

# FastMCP imports
from fastmcp import FastMCP

# 配置和工具类
from config import Config
from utils import debug_print

# 导入所有工具函数
from paper_analysis_tools import (
    analyze_paper_citations,
    search_papers_by_keywords,
    search_papers_by_author,
    get_paper_details,
    get_arxiv_paper,
    search_arxiv_papers,
    save_paper_to_markdown,
    save_arxiv_paper_to_markdown,
    organize_papers_by_topic,
    generate_literature_review,
    create_requirement_based_review,
    search_papers_in_collection,
    get_paper_recommendations
)

from pdf_processing_tools import (
    download_arxiv_pdf,
    extract_pdf_text,
    convert_pdf_to_text,
    process_arxiv_paper
)

from service_tools import get_service_info

# 检查PDF处理可用性
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

# 创建FastMCP应用
mcp = FastMCP("Unified MCP Server")

# 注册论文分析工具
mcp.tool()(analyze_paper_citations)
mcp.tool()(search_papers_by_keywords)
mcp.tool()(search_papers_by_author)
mcp.tool()(get_paper_details)
mcp.tool()(get_arxiv_paper)
mcp.tool()(search_arxiv_papers)
mcp.tool()(save_paper_to_markdown)
mcp.tool()(save_arxiv_paper_to_markdown)
mcp.tool()(organize_papers_by_topic)
mcp.tool()(generate_literature_review)
mcp.tool()(create_requirement_based_review)
mcp.tool()(search_papers_in_collection)
mcp.tool()(get_paper_recommendations)

# 注册PDF处理工具
mcp.tool()(download_arxiv_pdf)
mcp.tool()(extract_pdf_text)
mcp.tool()(convert_pdf_to_text)
mcp.tool()(process_arxiv_paper)

# 注册服务信息工具
mcp.tool()(get_service_info)

# Export the app for testing
app = mcp

if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description="统一MCP服务器 - 论文研究与PDF处理助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
功能特性:
  论文分析: 搜索、引用分析、文献综述生成
  PDF处理: ArXiv下载、文本提取、文本转换
  
示例:
  python main.py --debug
  python main.py --list-tools
        """
    )
    
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='启用调试模式'
    )
    parser.add_argument(
        '--list-tools',
        action='store_true',
        help='列出所有可用工具'
    )
    
    args = parser.parse_args()
    
    if args.list_tools:
        print("\n=== 统一MCP服务器 - 可用工具 ===")
        print("\n📄 论文分析工具:")
        paper_tools = [
            'analyze_paper_citations - 分析论文引用关系',
            'search_papers_by_keywords - 关键词搜索论文',
            'search_papers_by_author - 按作者搜索论文',
            'get_paper_details - 获取论文详细信息',
            'get_arxiv_paper - 获取ArXiv论文信息',
            'search_arxiv_papers - 搜索ArXiv论文',
            'save_paper_to_markdown - 保存论文为Markdown',
            'save_arxiv_paper_to_markdown - 保存ArXiv论文为Markdown',
            'organize_papers_by_topic - 按主题组织论文',
            'generate_literature_review - 生成文献综述',
            'create_requirement_based_review - 创建需求导向文献综述',
            'search_papers_in_collection - 搜索本地论文集',
            'get_paper_recommendations - 获取论文推荐'
        ]
        for tool in paper_tools:
            print(f"  • {tool}")
        
        print("\n🔧 PDF处理工具:")
        pdf_tools = [
            'download_arxiv_pdf - 下载ArXiv PDF文件',
            'extract_pdf_text - 提取PDF文本内容',
            'convert_pdf_to_text - 将PDF转换为文本文件',
            'process_arxiv_paper - 一站式ArXiv论文处理'
        ]
        for tool in pdf_tools:
            print(f"  • {tool}")
        
        print("\n📋 服务信息工具:")
        print("  • get_service_info - 获取服务信息")
        
        if not PdfReader:
            print("\n⚠️  PDF处理功能不可用，请安装: pip install pypdf")
        
        print("\n💡 使用示例:")
        print("  python main.py --debug")
        print("  python main.py --list-tools")
        print("")
        sys.exit(0)
    
    # 设置调试模式
    if args.debug:
        Config.DEBUG_MODE = True
    
    print(f"\n🚀 启动统一MCP服务器")
    print(f"🔧 调试模式: {'开启' if args.debug else '关闭'}")
    print(f"📄 PDF处理: {'可用' if PdfReader else '不可用 (需要安装pypdf)'}")
    print(f"📡 传输协议: STDIO")
    print(f"\n按 Ctrl+C 停止服务器\n")
    
    try:
        # FastMCP默认使用STDIO传输协议，不需要host和port参数
        mcp.run()
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")