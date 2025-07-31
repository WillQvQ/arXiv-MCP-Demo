#!/usr/bin/env python3
"""
演示脚本 - 展示MCP论文研究助手的功能
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import (
    search_papers_by_keywords,
    get_paper_details,
    analyze_paper_citations
)

async def demo_basic_functions():
    """演示基础功能"""
    print("🔍 演示：搜索论文")
    print("=" * 50)
    
    try:
        # 搜索论文
        search_result = await search_papers_by_keywords(
            "machine learning", 
            max_results=2
        )
        
        if 'papers' in search_result and search_result['papers']:
            paper = search_result['papers'][0]
            print(f"找到论文: {paper['title']}")
            print(f"作者: {', '.join([author['name'] for author in paper['authors']])}")
            print(f"引用数: {paper.get('citation_count', 'N/A')}")
            
            # 获取论文详情
            print("\n📄 演示：获取论文详情")
            print("=" * 50)
            
            paper_id = paper['paper_id']
            details = await get_paper_details(paper_id)
            
            if 'paper' in details:
                detail_paper = details['paper']
                print(f"论文ID: {detail_paper['paper_id']}")
                print(f"摘要: {detail_paper['abstract'][:200]}...")
                print(f"发表年份: {detail_paper.get('year', 'N/A')}")
                
                # 分析引用
                print("\n📊 演示：分析论文引用")
                print("=" * 50)
                
                citation_analysis = await analyze_paper_citations(paper_id)
                
                if 'analysis' in citation_analysis:
                    analysis = citation_analysis['analysis']
                    print(f"引用该论文的数量: {analysis.get('citation_count', 0)}")
                    print(f"该论文引用的数量: {analysis.get('reference_count', 0)}")
                else:
                    print(f"引用分析失败: {citation_analysis.get('error', '未知错误')}")
            else:
                print(f"获取详情失败: {details.get('error', '未知错误')}")
        else:
            print("未找到相关论文")
            
    except Exception as e:
        print(f"演示过程中出错: {e}")

async def main():
    """主函数"""
    print("🚀 MCP论文研究助手 - 功能演示")
    print("=" * 60)
    print("")
    
    await demo_basic_functions()
    
    print("\n✅ 演示完成！")
    print("\n💡 提示:")
    print("- 使用 'python main.py --unified' 启动统一服务器")
    print("- 使用 'python start_server.py --list' 查看所有可用服务")
    print("- 查看 README.md 了解更多使用方法")

if __name__ == "__main__":
    asyncio.run(main())