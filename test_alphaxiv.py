"""
测试alphaxiv链接处理功能
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from arxiv_mcp_server import ArxivMCPServer

# 删除了未使用的测试函数: test_alphaxiv_extraction, test_paper_retrieval, test_citing_papers, test_referenced_papers

async def test_full_analysis(debug=False):
    """测试完整的分析流程"""
    server = ArxivMCPServer(debug_mode=debug)
    
    alphaxiv_url = "https://www.alphaxiv.org/html/2504.13958v1"
    print(f"\n测试完整分析流程：")
    print("=" * 50)
    print(f"分析链接: {alphaxiv_url}")
    
    try:
        print(f"[DEBUG] 调用analyze_paper_citations方法...")
        result = await server.analyze_paper_citations(alphaxiv_url)
                
    except Exception as e:
        print(f"完整分析时出错: {e}")

async def test_non_debug_mode(debug=False):
    """测试非debug模式"""
    server = ArxivMCPServer(debug_mode=debug)
    
    alphaxiv_url = "https://www.alphaxiv.org/html/2504.13958v1"
    print(f"\n测试非debug模式：")
    print("=" * 50)
    print(f"分析链接: {alphaxiv_url}")
    print("注意：非debug模式下不会显示调试信息")
    
    try:
        # 调用analyze_paper_citations方法，debug=False（默认值）
        result = await server.analyze_paper_citations(alphaxiv_url)
        
        if "error" in result:
            print(f"分析出错: {result['error']}")
        else:
            # 显示主论文信息
            if result and result.get('papers') and result['papers'].get('main_paper'):
                main_paper = result['papers']['main_paper']
                print(f"\n主论文信息:")
                print(f"标题: {main_paper.get('title')}")
                authors = main_paper.get('authors', [])
                if authors and isinstance(authors, list) and len(authors) > 0:
                    if isinstance(authors[0], dict):
                        author_names = [author.get('name', '') for author in authors if author and isinstance(author, dict)]
                    else:
                        author_names = [str(author) for author in authors if author]
                    if author_names:
                        print(f"作者: {', '.join(author_names)}")
                    else:
                        print(f"作者: 无作者信息")
                else:
                    print(f"作者: 无作者信息")
                print(f"发布日期: {main_paper.get('published')}")
                print(f"ArXiv ID: {main_paper.get('arxiv_id')}")
            else:
                print("无法获取主论文信息。")

            # 显示统计信息
            if result and result.get('summary'):
                print(f"\n统计信息:")
                print(f"引用该论文的文章总数: {result['summary'].get('total_citing', 0)}")
                print(f"该论文引用的文章总数: {result['summary'].get('total_referenced', 0)}")

            # 显示引用论文（简化版，不显示调试信息）
            citing_papers = result.get('papers', {}).get('citing_papers') if result else None
            if citing_papers:
                print(f"\n引用该论文的文章 ({len(citing_papers)}篇):")
                for i, paper in enumerate(citing_papers[:3]): # 只显示前3篇
                    if paper:
                        print(f"  {i+1}. {paper.get('title')}")
                        print(f"     摘要: {paper.get('abstract', '')[:100]}...")
                        print(f"     ArXiv ID: {paper.get('ArXiv')}")
                        authors = paper.get('authors', [])
                        if authors and isinstance(authors, list) and len(authors) > 0:
                            if isinstance(authors[0], dict):
                                author_names = [author.get('name', '') for author in authors if author and isinstance(author, dict)]
                            else:
                                author_names = [str(author) for author in authors if author]
                            if author_names:
                                print(f"     作者: {', '.join(author_names)}")

            # 显示被引用论文（简化版，不显示调试信息）
            referenced_papers = result.get('papers', {}).get('referenced_papers') if result else None
            if referenced_papers:
                print(f"\n该论文引用的文章 ({len(referenced_papers)}篇):")
                for i, paper in enumerate(referenced_papers[:3]): # 只显示前3篇
                    if paper:
                        print(f"  {i+1}. {paper.get('title')}")
                        print(f"     摘要: {paper.get('abstract', '')[:100]}...")
                        print(f"     ArXiv ID: {paper.get('ArXiv')}")
                        authors = paper.get('authors', [])
                        if authors and isinstance(authors, list) and len(authors) > 0:
                            if isinstance(authors[0], dict):
                                author_names = [author.get('name', '') for author in authors if author and isinstance(author, dict)]
                            else:
                                author_names = [str(author) for author in authors if author]
                            if author_names:
                                print(f"     作者: {', '.join(author_names)}")
                
    except Exception as e:
        print(f"非debug模式测试时出错: {e}")

async def main(debug=False):
    """主测试函数"""
    print("AlphaXiv MCP服务器测试")
    print("=" * 60)
    
    # 测试非debug模式
    if not debug:
        await test_non_debug_mode(debug=debug)
    else:
        # 测试完整分析流程（debug模式）
        await test_full_analysis(debug=debug)

if __name__ == "__main__":
    # 用参数控制是否进入debug模式
    import asyncio
    import sys
    debug_mode = len(sys.argv) > 1 and sys.argv[1] == "debug"
    asyncio.run(main(debug=debug_mode))

