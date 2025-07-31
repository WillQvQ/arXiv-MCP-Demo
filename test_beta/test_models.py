"""Tests for data models."""

import pytest
import json
from datetime import datetime
from pathlib import Path

# Add the beta directory to the path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'beta'))

from models import (
    ArxivPaper, SemanticScholarPaper, AuthorInfo, 
    CitationAnalysisResult, SearchResult
)


class TestArxivPaper:
    """Test cases for ArxivPaper model."""
    
    def test_arxiv_paper_creation(self):
        """Test creating an ArxivPaper instance."""
        paper = ArxivPaper(
            title="Test Paper",
            authors=["Author One", "Author Two"],
            abstract="This is a test abstract.",
            arxiv_id="2301.12345",
            published_date="2023-01-01",
            pdf_url="https://arxiv.org/pdf/2301.12345.pdf",
            categories=["cs.AI", "cs.LG"]
        )
        
        assert paper.title == "Test Paper"
        assert len(paper.authors) == 2
        assert paper.arxiv_id == "2301.12345"
        assert "cs.AI" in paper.categories
    
    def test_arxiv_paper_to_dict(self):
        """Test converting ArxivPaper to dictionary."""
        paper = ArxivPaper(
            title="Test Paper",
            authors=["Author One"],
            abstract="Test abstract",
            arxiv_id="2301.12345",
            published_date="2023-01-01",
            pdf_url="https://arxiv.org/pdf/2301.12345.pdf",
            categories=["cs.AI"]
        )
        
        paper_dict = paper.to_dict()
        assert isinstance(paper_dict, dict)
        assert paper_dict['title'] == "Test Paper"
        assert paper_dict['arxiv_id'] == "2301.12345"
    
    def test_arxiv_paper_to_json(self):
        """Test converting ArxivPaper to JSON."""
        paper = ArxivPaper(
            title="Test Paper",
            authors=["Author One"],
            abstract="Test abstract",
            arxiv_id="2301.12345",
            published_date="2023-01-01",
            pdf_url="https://arxiv.org/pdf/2301.12345.pdf",
            categories=["cs.AI"]
        )
        
        json_str = paper.to_json()
        assert isinstance(json_str, str)
        
        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed['title'] == "Test Paper"
    
    def test_arxiv_paper_from_dict(self):
        """Test creating ArxivPaper from dictionary."""
        data = {
            'title': "Test Paper",
            'authors': ["Author One"],
            'abstract': "Test abstract",
            'arxiv_id': "2301.12345",
            'published_date': "2023-01-01",
            'pdf_url': "https://arxiv.org/pdf/2301.12345.pdf",
            'categories': ["cs.AI"]
        }
        
        paper = ArxivPaper.from_dict(data)
        assert paper.title == "Test Paper"
        assert paper.arxiv_id == "2301.12345"


class TestSemanticScholarPaper:
    """Test cases for SemanticScholarPaper model."""
    
    def test_semantic_scholar_paper_creation(self):
        """Test creating a SemanticScholarPaper instance."""
        paper = SemanticScholarPaper(
            paper_id="123456",
            title="Test Paper",
            abstract="This is a test abstract.",
            authors=[{"name": "Author One", "authorId": "1"}],
            year=2023,
            citation_count=10,
            reference_count=25,
            influential_citation_count=5,
            venue="Test Conference",
            url="https://example.com/paper",
            arxiv_id="2301.12345",
            doi="10.1000/test",
            corpus_id="corpus123",
            external_ids={"ArXiv": "2301.12345"},
            publication_types=["JournalArticle"],
            publication_date="2023-01-01",
            journal={"name": "Test Journal"}
        )
        
        assert paper.paper_id == "123456"
        assert paper.title == "Test Paper"
        assert paper.citation_count == 10
        assert paper.year == 2023
    
    def test_get_author_names(self):
        """Test extracting author names."""
        paper = SemanticScholarPaper(
            paper_id="123456",
            title="Test Paper",
            abstract=None,
            authors=[
                {"name": "Author One", "authorId": "1"},
                {"name": "Author Two", "authorId": "2"},
                {"authorId": "3"}  # Missing name
            ],
            year=2023,
            citation_count=10,
            reference_count=25,
            influential_citation_count=5,
            venue=None,
            url=None,
            arxiv_id=None,
            doi=None,
            corpus_id=None,
            external_ids=None,
            publication_types=None,
            publication_date=None,
            journal=None
        )
        
        author_names = paper.get_author_names()
        assert len(author_names) == 2
        assert "Author One" in author_names
        assert "Author Two" in author_names
    
    def test_semantic_scholar_paper_serialization(self):
        """Test serialization and deserialization."""
        original_paper = SemanticScholarPaper(
            paper_id="123456",
            title="Test Paper",
            abstract="Test abstract",
            authors=[{"name": "Author One", "authorId": "1"}],
            year=2023,
            citation_count=10,
            reference_count=25,
            influential_citation_count=5,
            venue="Test Conference",
            url="https://example.com/paper",
            arxiv_id=None,
            doi=None,
            corpus_id=None,
            external_ids=None,
            publication_types=None,
            publication_date=None,
            journal=None
        )
        
        # Convert to dict and back
        paper_dict = original_paper.to_dict()
        reconstructed_paper = SemanticScholarPaper.from_dict(paper_dict)
        
        assert reconstructed_paper.paper_id == original_paper.paper_id
        assert reconstructed_paper.title == original_paper.title
        assert reconstructed_paper.citation_count == original_paper.citation_count


class TestAuthorInfo:
    """Test cases for AuthorInfo model."""
    
    def test_author_info_creation(self):
        """Test creating an AuthorInfo instance."""
        author = AuthorInfo(
            author_id="author123",
            name="Test Author",
            aliases=["T. Author", "Test A."],
            affiliations=["Test University"],
            homepage="https://testauthor.com",
            paper_count=50,
            citation_count=1000,
            h_index=15
        )
        
        assert author.author_id == "author123"
        assert author.name == "Test Author"
        assert author.h_index == 15
        assert len(author.aliases) == 2
    
    def test_author_info_serialization(self):
        """Test AuthorInfo serialization."""
        author = AuthorInfo(
            author_id="author123",
            name="Test Author",
            aliases=None,
            affiliations=None,
            homepage=None,
            paper_count=50,
            citation_count=1000,
            h_index=15
        )
        
        author_dict = author.to_dict()
        reconstructed = AuthorInfo.from_dict(author_dict)
        
        assert reconstructed.author_id == author.author_id
        assert reconstructed.name == author.name
        assert reconstructed.paper_count == author.paper_count


class TestCitationAnalysisResult:
    """Test cases for CitationAnalysisResult model."""
    
    def test_citation_analysis_result_creation(self):
        """Test creating a CitationAnalysisResult instance."""
        main_paper = SemanticScholarPaper(
            paper_id="main123",
            title="Main Paper",
            abstract="Main abstract",
            authors=[{"name": "Main Author", "authorId": "1"}],
            year=2023,
            citation_count=10,
            reference_count=25,
            influential_citation_count=5,
            venue="Main Conference",
            url=None,
            arxiv_id=None,
            doi=None,
            corpus_id=None,
            external_ids=None,
            publication_types=None,
            publication_date=None,
            journal=None
        )
        
        citing_paper = SemanticScholarPaper(
            paper_id="citing123",
            title="Citing Paper",
            abstract="Citing abstract",
            authors=[{"name": "Citing Author", "authorId": "2"}],
            year=2024,
            citation_count=5,
            reference_count=30,
            influential_citation_count=2,
            venue="Citing Conference",
            url=None,
            arxiv_id=None,
            doi=None,
            corpus_id=None,
            external_ids=None,
            publication_types=None,
            publication_date=None,
            journal=None
        )
        
        result = CitationAnalysisResult(
            main_paper=main_paper,
            citing_papers=[citing_paper],
            referenced_papers=[],
            total_citations=1,
            total_references=0,
            analysis_timestamp="2023-01-01 12:00:00"
        )
        
        assert result.main_paper.paper_id == "main123"
        assert len(result.citing_papers) == 1
        assert result.total_citations == 1
        assert result.analysis_timestamp == "2023-01-01 12:00:00"
    
    def test_citation_analysis_result_serialization(self):
        """Test CitationAnalysisResult serialization."""
        main_paper = SemanticScholarPaper(
            paper_id="main123",
            title="Main Paper",
            abstract="Main abstract",
            authors=[{"name": "Main Author", "authorId": "1"}],
            year=2023,
            citation_count=10,
            reference_count=25,
            influential_citation_count=5,
            venue="Main Conference",
            url=None,
            arxiv_id=None,
            doi=None,
            corpus_id=None,
            external_ids=None,
            publication_types=None,
            publication_date=None,
            journal=None
        )
        
        result = CitationAnalysisResult(
            main_paper=main_paper,
            citing_papers=[],
            referenced_papers=[],
            total_citations=0,
            total_references=0,
            analysis_timestamp="2023-01-01 12:00:00"
        )
        
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert 'main_paper' in result_dict
        assert 'citing_papers' in result_dict
        assert 'total_citations' in result_dict
        
        json_str = result.to_json()
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed['total_citations'] == 0


class TestSearchResult:
    """Test cases for SearchResult model."""
    
    def test_search_result_creation(self):
        """Test creating a SearchResult instance."""
        paper = SemanticScholarPaper(
            paper_id="search123",
            title="Search Result Paper",
            abstract="Search result abstract",
            authors=[{"name": "Search Author", "authorId": "1"}],
            year=2023,
            citation_count=5,
            reference_count=15,
            influential_citation_count=2,
            venue="Search Conference",
            url=None,
            arxiv_id=None,
            doi=None,
            corpus_id=None,
            external_ids=None,
            publication_types=None,
            publication_date=None,
            journal=None
        )
        
        search_result = SearchResult(
            total=100,
            offset=0,
            next_offset=10,
            papers=[paper]
        )
        
        assert search_result.total == 100
        assert search_result.offset == 0
        assert search_result.next_offset == 10
        assert len(search_result.papers) == 1
        assert search_result.papers[0].paper_id == "search123"
    
    def test_search_result_serialization(self):
        """Test SearchResult serialization."""
        search_result = SearchResult(
            total=50,
            offset=10,
            next_offset=None,
            papers=[]
        )
        
        result_dict = search_result.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict['total'] == 50
        assert result_dict['offset'] == 10
        assert result_dict['next_offset'] is None
        assert result_dict['papers'] == []


if __name__ == "__main__":
    pytest.main([__file__])