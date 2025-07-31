"""论文分析工具模块 - 包含所有论文搜索、分析和管理功能"""

from typing import List, Dict, Any, Optional
from config import Config
from utils import debug_print, extract_arxiv_id, get_timestamp
from models import SemanticScholarPaper, ArxivPaper, CitationAnalysisResult
from arxiv_client import ArxivClient
from semantic_scholar_client import SemanticScholarClient
from paper_manager import PaperManager

# Initialize clients
arxiv_client = ArxivClient(debug=Config.DEBUG_MODE)
semantic_scholar_client = SemanticScholarClient(debug=Config.DEBUG_MODE)
paper_manager = PaperManager(debug=Config.DEBUG_MODE)


async def analyze_paper_citations(
    paper_identifier: str,
    debug: bool = Config.DEBUG_MODE
) -> Dict[str, Any]:
    """Analyze citations for a paper using ArXiv ID, DOI, or Semantic Scholar ID.
    
    Args:
        paper_identifier: ArXiv ID, DOI, URL, or Semantic Scholar paper ID
        debug: Enable debug output
    
    Returns:
        Dictionary containing citation analysis results
    """
    debug_print(f"Starting citation analysis for: {paper_identifier}", debug)
    
    try:
        # Extract ArXiv ID if it's a URL
        clean_id = extract_arxiv_id(paper_identifier) or paper_identifier
        
        # Get comprehensive analysis from Semantic Scholar
        analysis = await semantic_scholar_client.analyze_paper_citations(clean_id)
        
        if 'error' in analysis:
            return analysis
        
        # Create result object
        main_paper = SemanticScholarPaper.from_dict(analysis['main_paper'])
        citing_papers = [SemanticScholarPaper.from_dict(p) for p in analysis['citing_papers']]
        referenced_papers = [SemanticScholarPaper.from_dict(p) for p in analysis['referenced_papers']]
        
        result = CitationAnalysisResult(
            main_paper=main_paper,
            citing_papers=citing_papers,
            referenced_papers=referenced_papers,
            total_citations=analysis['citation_count'],
            total_references=analysis['reference_count'],
            analysis_timestamp=get_timestamp()
        )
        
        debug_print(f"Analysis complete: {result.total_citations} citations, {result.total_references} references", debug)
        
        return {
            'success': True,
            'main_paper': result.main_paper.to_dict(),
            'total_citations': result.total_citations,
            'total_references': result.total_references,
            'citing_papers': [p.to_dict() for p in result.citing_papers],
            'referenced_papers': [p.to_dict() for p in result.referenced_papers],
            'recommendations': analysis.get('recommendations', []),
            'timestamp': result.analysis_timestamp
        }
        
    except Exception as e:
        error_msg = f"Error analyzing citations: {str(e)}"
        debug_print(error_msg, debug)
        return {'success': False, 'error': error_msg}


async def search_papers_by_keywords(
    query: str,
    max_results: int = 20,
    year: Optional[str] = None,
    venue: Optional[List[str]] = None,
    min_citation_count: Optional[int] = None,
    debug: bool = Config.DEBUG_MODE
) -> Dict[str, Any]:
    """Search for papers using keywords with advanced filtering.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        year: Publication year filter (e.g., "2023" or "2020-2023")
        venue: List of venue names to filter by
        min_citation_count: Minimum citation count filter
        debug: Enable debug output
    
    Returns:
        Dictionary containing search results
    """
    debug_print(f"Searching papers with query: {query}", debug)
    
    try:
        search_result = await semantic_scholar_client.search_papers(
            query=query,
            year=year,
            venue=venue,
            min_citation_count=min_citation_count,
            limit=max_results
        )
        
        return {
            'success': True,
            'total_found': search_result.total,
            'returned_count': len(search_result.papers),
            'papers': [paper.to_dict() for paper in search_result.papers],
            'next_offset': search_result.next_offset
        }
        
    except Exception as e:
        error_msg = f"Error searching papers: {str(e)}"
        debug_print(error_msg, debug)
        return {'success': False, 'error': error_msg}


async def search_papers_by_author(
    author_name: str,
    max_results: int = 20,
    debug: bool = Config.DEBUG_MODE
) -> Dict[str, Any]:
    """Search for papers by author name.
    
    Args:
        author_name: Name of the author to search for
        max_results: Maximum number of results to return
        debug: Enable debug output
    
    Returns:
        Dictionary containing author's papers
    """
    debug_print(f"Searching papers by author: {author_name}", debug)
    
    try:
        # First search for the author
        authors = await semantic_scholar_client.search_authors(author_name, limit=1)
        
        if not authors:
            return {'success': False, 'error': f'Author "{author_name}" not found'}
        
        author = authors[0]
        
        # Get author's papers
        papers = await semantic_scholar_client.get_author_papers(
            author.author_id, 
            limit=max_results
        )
        
        return {
            'success': True,
            'author_info': author.to_dict(),
            'paper_count': len(papers),
            'papers': [paper.to_dict() for paper in papers]
        }
        
    except Exception as e:
        error_msg = f"Error searching papers by author: {str(e)}"
        debug_print(error_msg, debug)
        return {'success': False, 'error': error_msg}


async def get_paper_details(
    paper_id: str,
    include_citations: bool = False,
    include_references: bool = False,
    include_recommendations: bool = False,
    debug: bool = Config.DEBUG_MODE
) -> Dict[str, Any]:
    """Get detailed information about a specific paper.
    
    Args:
        paper_id: Paper identifier (ArXiv ID, DOI, or Semantic Scholar ID)
        include_citations: Include papers that cite this paper
        include_references: Include papers referenced by this paper
        include_recommendations: Include recommended similar papers
        debug: Enable debug output
    
    Returns:
        Dictionary containing paper details
    """
    debug_print(f"Getting paper details for: {paper_id}", debug)
    
    try:
        # Get main paper details
        paper = await semantic_scholar_client.get_paper(paper_id)
        
        if not paper:
            return {'success': False, 'error': f'Paper "{paper_id}" not found'}
        
        result = {
            'success': True,
            'paper': paper.to_dict()
        }
        
        # Add optional data
        if include_citations:
            citations = await semantic_scholar_client.get_paper_citations(paper_id)
            result['citations'] = [p.to_dict() for p in citations]
            result['citation_count'] = len(citations)
        
        if include_references:
            references = await semantic_scholar_client.get_paper_references(paper_id)
            result['references'] = [p.to_dict() for p in references]
            result['reference_count'] = len(references)
        
        if include_recommendations:
            recommendations = await semantic_scholar_client.get_paper_recommendations(paper_id)
            result['recommendations'] = [p.to_dict() for p in recommendations]
        
        return result
        
    except Exception as e:
        error_msg = f"Error getting paper details: {str(e)}"
        debug_print(error_msg, debug)
        return {'success': False, 'error': error_msg}


async def get_arxiv_paper(
    arxiv_id: str,
    debug: bool = Config.DEBUG_MODE
) -> Dict[str, Any]:
    """Get ArXiv paper details by ArXiv ID.
    
    Args:
        arxiv_id: ArXiv paper ID or URL
        debug: Enable debug output
    
    Returns:
        Dictionary containing ArXiv paper details
    """
    debug_print(f"Getting ArXiv paper: {arxiv_id}", debug)
    
    try:
        # Extract clean ArXiv ID
        clean_id = extract_arxiv_id(arxiv_id) or arxiv_id
        
        # Get paper from ArXiv
        paper = await arxiv_client.get_paper_by_id(clean_id)
        
        if not paper:
            return {'success': False, 'error': f'ArXiv paper "{arxiv_id}" not found'}
        
        return {
            'success': True,
            'paper': paper.to_dict()
        }
        
    except Exception as e:
        error_msg = f"Error getting ArXiv paper: {str(e)}"
        debug_print(error_msg, debug)
        return {'success': False, 'error': error_msg}


async def search_arxiv_papers(
    query: str,
    max_results: int = 10,
    sort_by: str = "relevance",
    debug: bool = Config.DEBUG_MODE
) -> Dict[str, Any]:
    """Search ArXiv for papers.
    
    Args:
        query: Search query string
        max_results: Maximum number of results
        sort_by: Sort order (relevance, lastUpdatedDate, submittedDate)
        debug: Enable debug output
    
    Returns:
        Dictionary containing ArXiv search results
    """
    debug_print(f"Searching ArXiv with query: {query}", debug)
    
    try:
        papers = await arxiv_client.search_papers(
            query=query,
            max_results=max_results,
            sort_by=sort_by
        )
        
        return {
            'success': True,
            'paper_count': len(papers),
            'papers': [paper.to_dict() for paper in papers]
        }
        
    except Exception as e:
        error_msg = f"Error searching ArXiv: {str(e)}"
        debug_print(error_msg, debug)
        return {'success': False, 'error': error_msg}


async def save_paper_to_markdown(
    paper_id: str,
    topic: str = "general",
    notes: str = "",
    debug: bool = Config.DEBUG_MODE
) -> Dict[str, Any]:
    """Save a paper to markdown format.
    
    Args:
        paper_id: Paper identifier
        topic: Topic category for organization
        notes: Additional notes to include
        debug: Enable debug output
    
    Returns:
        Dictionary containing save result
    """
    debug_print(f"Saving paper to markdown: {paper_id}", debug)
    
    try:
        # Get paper details
        paper = await semantic_scholar_client.get_paper(paper_id)
        
        if not paper:
            return {'success': False, 'error': f'Paper "{paper_id}" not found'}
        
        # Save to markdown
        filepath = paper_manager.save_paper_to_markdown(paper, topic, notes)
        
        return {
            'success': True,
            'filepath': filepath,
            'paper_title': paper.title
        }
        
    except Exception as e:
        error_msg = f"Error saving paper: {str(e)}"
        debug_print(error_msg, debug)
        return {'success': False, 'error': error_msg}


async def save_arxiv_paper_to_markdown(
    arxiv_id: str,
    topic: str = "general",
    notes: str = "",
    debug: bool = Config.DEBUG_MODE
) -> Dict[str, Any]:
    """Save an ArXiv paper to markdown format.
    
    Args:
        arxiv_id: ArXiv paper ID or URL
        topic: Topic category for organization
        notes: Additional notes to include
        debug: Enable debug output
    
    Returns:
        Dictionary containing save result
    """
    debug_print(f"Saving ArXiv paper to markdown: {arxiv_id}", debug)
    
    try:
        # Extract clean ArXiv ID
        clean_id = extract_arxiv_id(arxiv_id) or arxiv_id
        
        # Get paper from ArXiv
        paper = await arxiv_client.get_paper_by_id(clean_id)
        
        if not paper:
            return {'success': False, 'error': f'ArXiv paper "{arxiv_id}" not found'}
        
        # Save to markdown
        filepath = paper_manager.save_arxiv_paper_to_markdown(paper, topic, notes)
        
        return {
            'success': True,
            'filepath': filepath,
            'paper_title': paper.title
        }
        
    except Exception as e:
        error_msg = f"Error saving ArXiv paper: {str(e)}"
        debug_print(error_msg, debug)
        return {'success': False, 'error': error_msg}


async def organize_papers_by_topic(
    debug: bool = Config.DEBUG_MODE
) -> Dict[str, Any]:
    """Get organization of papers by topic.
    
    Args:
        debug: Enable debug output
    
    Returns:
        Dictionary containing paper organization
    """
    debug_print("Organizing papers by topic", debug)
    
    try:
        organized = paper_manager.organize_papers_by_topic()
        stats = paper_manager.get_paper_statistics()
        
        return {
            'success': True,
            'organization': organized,
            'statistics': stats
        }
        
    except Exception as e:
        error_msg = f"Error organizing papers: {str(e)}"
        debug_print(error_msg, debug)
        return {'success': False, 'error': error_msg}


async def generate_literature_review(
    topic: str,
    requirements: List[str],
    output_filename: Optional[str] = None,
    debug: bool = Config.DEBUG_MODE
) -> Dict[str, Any]:
    """Generate a literature review for papers in a topic.
    
    Args:
        topic: Topic category
        requirements: List of requirements to organize papers by
        output_filename: Optional custom filename
        debug: Enable debug output
    
    Returns:
        Dictionary containing review generation result
    """
    debug_print(f"Generating literature review for topic: {topic}", debug)
    
    try:
        filepath = paper_manager.generate_literature_review(
            topic, requirements, output_filename
        )
        
        return {
            'success': True,
            'filepath': filepath,
            'topic': topic,
            'requirements_count': len(requirements)
        }
        
    except Exception as e:
        error_msg = f"Error generating literature review: {str(e)}"
        debug_print(error_msg, debug)
        return {'success': False, 'error': error_msg}


async def create_requirement_based_review(
    paper_ids: List[str],
    requirements: List[str],
    output_filename: Optional[str] = None,
    debug: bool = Config.DEBUG_MODE
) -> Dict[str, Any]:
    """Create a requirement-based literature review from specific papers.
    
    Args:
        paper_ids: List of paper identifiers
        requirements: List of requirements to organize papers by
        output_filename: Optional custom filename
        debug: Enable debug output
    
    Returns:
        Dictionary containing review creation result
    """
    debug_print(f"Creating requirement-based review for {len(paper_ids)} papers", debug)
    
    try:
        # Get paper details
        papers = []
        for paper_id in paper_ids:
            paper = await semantic_scholar_client.get_paper(paper_id)
            if paper:
                papers.append(paper)
        
        if not papers:
            return {'success': False, 'error': 'No valid papers found'}
        
        # Create review
        filepath = paper_manager.create_requirement_based_review(
            papers, requirements, output_filename
        )
        
        return {
            'success': True,
            'filepath': filepath,
            'papers_analyzed': len(papers),
            'requirements_count': len(requirements)
        }
        
    except Exception as e:
        error_msg = f"Error creating requirement-based review: {str(e)}"
        debug_print(error_msg, debug)
        return {'success': False, 'error': error_msg}


async def search_papers_in_collection(
    keyword: str,
    debug: bool = Config.DEBUG_MODE
) -> Dict[str, Any]:
    """Search for papers in the local collection by keyword.
    
    Args:
        keyword: Keyword to search for
        debug: Enable debug output
    
    Returns:
        Dictionary containing search results
    """
    debug_print(f"Searching local collection for keyword: {keyword}", debug)
    
    try:
        matching_papers = paper_manager.search_papers_by_keyword(keyword)
        
        return {
            'success': True,
            'keyword': keyword,
            'matches_found': len(matching_papers),
            'papers': matching_papers
        }
        
    except Exception as e:
        error_msg = f"Error searching local collection: {str(e)}"
        debug_print(error_msg, debug)
        return {'success': False, 'error': error_msg}


async def get_paper_recommendations(
    paper_id: str,
    max_results: int = 10,
    debug: bool = Config.DEBUG_MODE
) -> Dict[str, Any]:
    """Get paper recommendations based on a paper.
    
    Args:
        paper_id: Paper identifier
        max_results: Maximum number of recommendations
        debug: Enable debug output
    
    Returns:
        Dictionary containing recommendations
    """
    debug_print(f"Getting recommendations for paper: {paper_id}", debug)
    
    try:
        recommendations = await semantic_scholar_client.get_paper_recommendations(
            paper_id, limit=max_results
        )
        
        return {
            'success': True,
            'paper_id': paper_id,
            'recommendation_count': len(recommendations),
            'recommendations': [paper.to_dict() for paper in recommendations]
        }
        
    except Exception as e:
        error_msg = f"Error getting recommendations: {str(e)}"
        debug_print(error_msg, debug)
        return {'success': False, 'error': error_msg}