"""服务信息工具模块 - 包含服务信息和工具列表功能"""

from typing import Dict, Any
from config import Config

# PDF处理相关导入检查
try:
    from pypdf import PdfReader  # type: ignore
except ImportError:
    try:
        from PyPDF2 import PdfReader  # type: ignore
    except ImportError:
        PdfReader = None


async def get_service_info(
    debug: bool = Config.DEBUG_MODE
) -> Dict[str, Any]:
    """Get service information and available tools list.
    
    Args:
        debug: Enable debug output
    
    Returns:
        Dictionary containing service information
    """
    return {
        'service_name': '统一MCP服务器',
        'description': '论文研究与PDF处理助手 - 集成论文搜索、分析、PDF下载、文本提取等功能',
        'version': '2.0.0',
        'available_tools': {
            'paper_analysis': [
                'analyze_paper_citations',
                'search_papers_by_keywords',
                'search_papers_by_author',
                'get_paper_details',
                'get_arxiv_paper',
                'search_arxiv_papers',
                'save_paper_to_markdown',
                'save_arxiv_paper_to_markdown',
                'organize_papers_by_topic',
                'generate_literature_review',
                'create_requirement_based_review',
                'search_papers_in_collection',
                'get_paper_recommendations'
            ],
            'pdf_processing': [
                'download_arxiv_pdf',
                'extract_pdf_text',
                'convert_pdf_to_text',
                'process_arxiv_paper'
            ],
            'service_info': [
                'get_service_info'
            ]
        },
        'pdf_processing_available': PdfReader is not None,
        'debug_mode': debug
    }