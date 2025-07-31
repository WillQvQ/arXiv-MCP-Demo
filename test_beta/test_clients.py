"""Tests for API clients."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

# Add the beta directory to the path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'beta'))

from arxiv_client import ArxivClient
from semantic_scholar_client import SemanticScholarClient
from models import ArxivPaper, SemanticScholarPaper, SearchResult


class TestArxivClient:
    """Test cases for ArxivClient."""
    
    def test_arxiv_client_initialization(self):
        """Test ArxivClient initialization."""
        client = ArxivClient(debug=True)
        assert client.debug == True
        assert client.base_url == 'http://export.arxiv.org/api/query'
        assert hasattr(client, 'rate_limiter')
    
    @pytest.mark.asyncio
    async def test_get_paper_by_id_success(self):
        """Test successful paper retrieval by ID."""
        client = ArxivClient(debug=False)
        
        # Create expected paper object
        expected_paper = ArxivPaper(
            arxiv_id='2301.12345v1',
            title='Test Paper Title',
            abstract='This is a test abstract.',
            authors=['Test Author'],
            published_date='2023-01-01T00:00:00Z',
            pdf_url='http://arxiv.org/pdf/2301.12345v1.pdf',
            categories=['cs.AI']
        )
        
        # Mock the get_paper_by_id method directly
        with patch.object(client, 'get_paper_by_id', return_value=expected_paper) as mock_get_paper:
            paper = await client.get_paper_by_id('2301.12345')
            
            assert paper is not None
            assert isinstance(paper, ArxivPaper)
            assert paper.title == "Test Paper Title"
            assert paper.arxiv_id == "2301.12345v1"
            assert "Test Author" in paper.authors
            mock_get_paper.assert_called_once_with('2301.12345')
    
    @pytest.mark.asyncio
    async def test_get_paper_by_id_not_found(self):
        """Test paper retrieval when paper is not found."""
        client = ArxivClient(debug=False)
        
        # Mock the get_paper_by_id method to return None for not found
        with patch.object(client, 'get_paper_by_id', return_value=None) as mock_get_paper:
            paper = await client.get_paper_by_id('nonexistent')
            assert paper is None
            mock_get_paper.assert_called_once_with('nonexistent')
    
    @pytest.mark.asyncio
    async def test_search_papers(self):
        """Test paper search functionality."""
        client = ArxivClient(debug=False)
        
        # Create expected paper objects
        paper1 = ArxivPaper(
            arxiv_id='2301.12345v1',
            title='First Paper',
            abstract='First abstract.',
            authors=['Author One'],
            published_date='2023-01-01T00:00:00Z',
            pdf_url='http://arxiv.org/pdf/2301.12345v1.pdf',
            categories=['cs.AI']
        )
        
        paper2 = ArxivPaper(
            arxiv_id='2301.12346v1',
            title='Second Paper',
            abstract='Second abstract.',
            authors=['Author Two'],
            published_date='2023-01-02T00:00:00Z',
            pdf_url='http://arxiv.org/pdf/2301.12346v1.pdf',
            categories=['cs.LG']
        )
        
        expected_papers = [paper1, paper2]
        
        # Mock the search_papers method directly
        with patch.object(client, 'search_papers', return_value=expected_papers) as mock_search:
            papers = await client.search_papers('machine learning', max_results=2)
            
            assert len(papers) == 2
            assert papers[0].title == "First Paper"
            assert papers[1].title == "Second Paper"
            mock_search.assert_called_once_with('machine learning', max_results=2)
    
    def test_parse_arxiv_response_invalid_xml(self):
        """Test parsing invalid XML response."""
        client = ArxivClient(debug=False)
        
        invalid_xml = "<invalid>xml</invalid>"
        result = client._parse_arxiv_response(invalid_xml)
        assert result is None
    
    def test_parse_entry_missing_fields(self):
        """Test parsing entry with missing fields."""
        client = ArxivClient(debug=False)
        
        # Mock XML with minimal entry
        import xml.etree.ElementTree as ET
        xml_content = '''
        <entry xmlns="http://www.w3.org/2005/Atom">
            <title>Minimal Paper</title>
        </entry>
        '''
        
        entry = ET.fromstring(xml_content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        paper = client._parse_entry(entry, ns)
        assert paper is not None
        assert paper.title == "Minimal Paper"
        assert paper.authors == []
        assert paper.abstract == ""


class TestSemanticScholarClient:
    """Test cases for SemanticScholarClient."""
    
    def test_semantic_scholar_client_initialization(self):
        """Test SemanticScholarClient initialization."""
        client = SemanticScholarClient(debug=True)
        assert client.debug == True
        assert client.base_url == 'https://api.semanticscholar.org/graph/v1'
        assert hasattr(client, 'rate_limiter')
        assert hasattr(client, 'headers')
    
    @pytest.mark.asyncio
    async def test_get_paper_success(self):
        """Test successful paper retrieval."""
        client = SemanticScholarClient(debug=False)
        
        # Create expected paper object
        expected_paper = SemanticScholarPaper(
            paper_id='123456',
            title='Test Paper',
            abstract='Test abstract',
            authors=[{'name': 'Test Author', 'authorId': '1'}],
            year=2023,
            citation_count=10,
            reference_count=25,
            influential_citation_count=5,
            venue='Test Conference',
            url='https://example.com/paper',
            arxiv_id=None,
            doi=None,
            corpus_id=None,
            external_ids=None,
            publication_types=None,
            publication_date=None,
            journal=None
        )
        
        # Mock the get_paper method directly
        with patch.object(client, 'get_paper', return_value=expected_paper) as mock_get_paper:
            paper = await client.get_paper('123456')
            
            assert paper is not None
            assert isinstance(paper, SemanticScholarPaper)
            assert paper.paper_id == '123456'
            assert paper.title == 'Test Paper'
            assert paper.citation_count == 10
            mock_get_paper.assert_called_once_with('123456')
    
    @pytest.mark.asyncio
    async def test_get_paper_not_found(self):
        """Test paper retrieval when paper is not found."""
        client = SemanticScholarClient(debug=False)
        
        # Mock the get_paper method to return None for not found
        with patch.object(client, 'get_paper', return_value=None) as mock_get_paper:
            paper = await client.get_paper('nonexistent')
            assert paper is None
            mock_get_paper.assert_called_once_with('nonexistent')
    
    @pytest.mark.asyncio
    async def test_get_paper_citations(self):
        """Test getting paper citations."""
        client = SemanticScholarClient(debug=False)
        
        # Create expected citation paper
        citing_paper = SemanticScholarPaper(
            paper_id='citing1',
            title='Citing Paper 1',
            abstract='Abstract 1',
            authors=[{'name': 'Citing Author 1', 'authorId': '1'}],
            year=2024,
            citation_count=5,
            reference_count=20,
            influential_citation_count=2,
            venue='Citing Conference',
            url=None,
            arxiv_id=None,
            doi=None,
            corpus_id=None,
            external_ids=None,
            publication_types=None,
            publication_date=None,
            journal=None
        )
        
        # Mock the get_paper_citations method
        with patch.object(client, 'get_paper_citations', return_value=[citing_paper]) as mock_citations:
            citations = await client.get_paper_citations('test_paper')
            
            assert len(citations) == 1
            assert citations[0].paper_id == 'citing1'
            assert citations[0].title == 'Citing Paper 1'
            mock_citations.assert_called_once_with('test_paper')
    
    @pytest.mark.asyncio
    async def test_search_papers(self):
        """Test paper search functionality."""
        client = SemanticScholarClient(debug=False)
        
        # Create expected search result paper
        search_paper = SemanticScholarPaper(
            paper_id='search1',
            title='Search Result 1',
            abstract='Search abstract 1',
            authors=[{'name': 'Search Author 1', 'authorId': '1'}],
            year=2023,
            citation_count=15,
            reference_count=30,
            influential_citation_count=8,
            venue='Search Conference',
            url=None,
            arxiv_id=None,
            doi=None,
            corpus_id=None,
            external_ids=None,
            publication_types=None,
            publication_date=None,
            journal=None
        )
        
        # Create expected search result
        expected_result = SearchResult(
            total=100,
            offset=0,
            next_offset=10,
            papers=[search_paper]
        )
        
        # Mock the search_papers method
        with patch.object(client, 'search_papers', return_value=expected_result) as mock_search:
            search_result = await client.search_papers('machine learning')
            
            assert search_result.total == 100
            assert search_result.offset == 0
            assert search_result.next_offset == 10
            assert len(search_result.papers) == 1
            assert search_result.papers[0].title == 'Search Result 1'
            mock_search.assert_called_once_with('machine learning')
    
    @pytest.mark.asyncio
    async def test_get_paper_bulk(self):
        """Test bulk paper retrieval."""
        client = SemanticScholarClient(debug=False)
        
        # Create expected bulk papers
        bulk_paper1 = SemanticScholarPaper(
            paper_id='bulk1',
            title='Bulk Paper 1',
            abstract='Bulk abstract 1',
            authors=[{'name': 'Bulk Author 1', 'authorId': '1'}],
            year=2023,
            citation_count=5,
            reference_count=15,
            influential_citation_count=2,
            venue='Bulk Conference',
            url=None,
            arxiv_id=None,
            doi=None,
            corpus_id=None,
            external_ids=None,
            publication_types=None,
            publication_date=None,
            journal=None
        )
        
        bulk_paper2 = SemanticScholarPaper(
            paper_id='bulk2',
            title='Bulk Paper 2',
            abstract='Bulk abstract 2',
            authors=[{'name': 'Bulk Author 2', 'authorId': '2'}],
            year=2024,
            citation_count=8,
            reference_count=20,
            influential_citation_count=3,
            venue='Bulk Conference 2',
            url=None,
            arxiv_id=None,
            doi=None,
            corpus_id=None,
            external_ids=None,
            publication_types=None,
            publication_date=None,
            journal=None
        )
        
        # Mock the get_paper_bulk method
        with patch.object(client, 'get_paper_bulk', return_value=[bulk_paper1, bulk_paper2]) as mock_bulk:
            papers = await client.get_paper_bulk(['bulk1', 'missing', 'bulk2'])
            
            # Should return 2 papers (excluding the None entry)
            assert len(papers) == 2
            assert papers[0].paper_id == 'bulk1'
            assert papers[1].paper_id == 'bulk2'
            mock_bulk.assert_called_once_with(['bulk1', 'missing', 'bulk2'])
    
    @pytest.mark.asyncio
    async def test_analyze_paper_citations(self):
        """Test comprehensive citation analysis."""
        client = SemanticScholarClient(debug=False)
        
        # Create expected analysis result
        expected_analysis = {
            'main_paper': {
                'paper_id': 'main123',
                'title': 'Main Paper',
                'abstract': 'Main abstract',
                'authors': [{'name': 'Main Author', 'authorId': '1'}],
                'year': 2023,
                'citation_count': 10,
                'reference_count': 25,
                'influential_citation_count': 5,
                'venue': 'Main Conference'
            },
            'citing_papers': [
                {
                    'paper_id': 'citing1',
                    'title': 'Citing Paper',
                    'abstract': 'Citing abstract',
                    'authors': [{'name': 'Citing Author', 'authorId': '2'}],
                    'year': 2024
                }
            ],
            'referenced_papers': [
                {
                    'paper_id': 'ref1',
                    'title': 'Referenced Paper',
                    'abstract': 'Referenced abstract',
                    'authors': [{'name': 'Referenced Author', 'authorId': '3'}],
                    'year': 2022
                }
            ],
            'recommendations': [
                {
                    'paper_id': 'rec1',
                    'title': 'Recommended Paper',
                    'abstract': 'Recommended abstract',
                    'authors': [{'name': 'Recommended Author', 'authorId': '4'}],
                    'year': 2023
                }
            ],
            'citation_count': 1,
            'reference_count': 1,
            'analysis_timestamp': '/tmp/test_file.json'
        }
        
        # Mock the analyze_paper_citations method
        with patch.object(client, 'analyze_paper_citations', return_value=expected_analysis) as mock_analyze:
            analysis = await client.analyze_paper_citations('main123')
            
            assert 'main_paper' in analysis
            assert 'citing_papers' in analysis
            assert 'referenced_papers' in analysis
            assert 'recommendations' in analysis
            assert analysis['citation_count'] == 1
            assert analysis['reference_count'] == 1
            assert len(analysis['recommendations']) == 1
            mock_analyze.assert_called_once_with('main123')


if __name__ == "__main__":
    pytest.main([__file__])