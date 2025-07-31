"""Tests for paper manager functionality."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# Add the beta directory to the path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'beta'))

from paper_manager import PaperManager
from models import ArxivPaper, SemanticScholarPaper, AuthorInfo
from config import Config


class TestPaperManager:
    """Test cases for PaperManager."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = PaperManager(debug=True)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_paper_manager_initialization(self):
        """Test PaperManager initialization."""
        assert self.manager.debug == True
        assert hasattr(self.manager, 'papers_dir')
        assert hasattr(self.manager, 'md_files_dir')
    
    def test_ensure_directory_structure(self):
        """Test directory structure creation."""
        self.manager._ensure_directory_structure()
        
        # Check if main directories are created
        assert self.manager.papers_dir.exists()
        assert self.manager.md_files_dir.exists()
    
    def test_sanitize_filename(self):
        """Test filename sanitization using utils function."""
        from utils import sanitize_filename
        
        # Test normal filename
        result = sanitize_filename("Normal Paper Title")
        assert "normal" in result.lower()
        
        # Test filename with special characters
        result = sanitize_filename("Paper: With/Special\\Characters?")
        assert "paper" in result.lower()
        
        # Test filename with multiple spaces
        result = sanitize_filename("Paper   With    Multiple   Spaces")
        assert "paper" in result.lower()
    
    def test_generate_paper_markdown(self):
        """Test Semantic Scholar paper markdown generation."""
        # Create test paper
        paper = SemanticScholarPaper(
            paper_id="123456",
            title="Test Paper Title",
            abstract="This is a test abstract for the paper.",
            authors=[{"name": "John Doe", "authorId": "1"}, {"name": "Jane Smith", "authorId": "2"}],
            year=2023,
            citation_count=10,
            reference_count=25,
            influential_citation_count=5,
            venue="Test Conference",
            url="https://example.com/paper",
            arxiv_id=None,
            doi=None,
            corpus_id=None,
            external_ids={},
            publication_types=[],
            publication_date=None,
            journal=None
        )
        
        markdown = self.manager._generate_paper_markdown(paper)
        
        # Check if markdown contains expected content
        assert "# Test Paper Title" in markdown
        assert "John Doe" in markdown
        assert "Jane Smith" in markdown
        assert "2023" in markdown
        assert "10" in markdown
        assert "Test Conference" in markdown
        assert "This is a test abstract for the paper." in markdown
    
    def test_generate_arxiv_paper_markdown(self):
        """Test ArXiv paper markdown generation."""
        # Create test paper
        paper = ArxivPaper(
            title="ArXiv Test Paper",
            authors=["Alice Johnson", "Bob Wilson"],
            abstract="This is an ArXiv test abstract.",
            arxiv_id="2301.12345",
            published_date="2023-01-15",
            pdf_url="https://arxiv.org/pdf/2301.12345.pdf",
            categories=["cs.AI", "cs.LG"]
        )
        
        markdown = self.manager._generate_arxiv_paper_markdown(paper)
        
        # Check if markdown contains expected content
        assert "# ArXiv Test Paper" in markdown
        assert "Alice Johnson" in markdown
        assert "Bob Wilson" in markdown
        assert "2301.12345" in markdown
        assert "2023-01-15" in markdown
        assert "cs.AI" in markdown
        assert "This is an ArXiv test abstract." in markdown
    
    @patch('builtins.open', new_callable=mock_open)
    def test_save_paper_to_markdown(self, mock_file):
        """Test saving paper to markdown file."""
        # Create test paper
        paper = SemanticScholarPaper(
            paper_id="123456",
            title="Test Save Paper",
            abstract="Test abstract for saving.",
            authors=[{"name": "Test Author", "authorId": "1"}],
            year=2023,
            citation_count=5,
            reference_count=15,
            influential_citation_count=2,
            venue="Test Venue",
            url=None,
            arxiv_id=None,
            doi=None,
            corpus_id=None,
            external_ids={},
            publication_types=[],
            publication_date=None,
            journal=None
        )
        
        result = self.manager.save_paper_to_markdown(paper, "ML")
        
        # Check if file was "written"
        mock_file.assert_called_once()
        assert ".md" in result
        assert "ML" in result
    
    def test_search_papers_by_keyword(self):
        """Test searching papers by keyword."""
        # This method exists in PaperManager
        result = self.manager.search_papers_by_keyword("machine learning")
        assert isinstance(result, list)
    
    def test_organize_papers_by_topic(self):
        """Test organizing papers by topic."""
        # This method returns existing papers organized by topic
        result = self.manager.organize_papers_by_topic()
        
        # Check that result is a dictionary
        assert isinstance(result, dict)
        
        # Check that all values are lists
        for topic, papers in result.items():
            assert isinstance(papers, list)
    
    def test_get_paper_statistics(self):
        """Test paper statistics generation."""
        stats = self.manager.get_paper_statistics()
        
        # Check that stats is a dictionary with expected keys
        assert isinstance(stats, dict)
        assert "total_papers" in stats
        assert "papers_by_topic" in stats
        assert "topics" in stats
        
        # Check that values are of correct types
        assert isinstance(stats["total_papers"], int)
        assert isinstance(stats["papers_by_topic"], dict)
        assert isinstance(stats["topics"], list)
    
    def test_generate_literature_review(self):
        """Test literature review generation."""
        # Test with a topic and requirements
        topic = "ML"
        requirements = ["deep learning", "neural networks"]
        
        # This will create a review file
        result = self.manager.generate_literature_review(topic, requirements)
        
        # Check that a file path is returned
        assert isinstance(result, str)
        assert ".md" in result or "No papers found" in result or "does not exist" in result
    
    # Removed test_search_papers_in_collection as this method doesn't exist
    
    def test_create_requirement_based_review(self):
        """Test requirement-based review creation."""
        # Create test papers
        papers = [
            SemanticScholarPaper(
                paper_id="1",
                title="Reinforcement Learning Survey",
                abstract="Multi-turn reinforcement learning for agents.",
                authors=[{"name": "RL Author", "authorId": "1"}],
                year=2023,
                citation_count=50,
                reference_count=0,
                influential_citation_count=0,
                venue="RL Conference",
                url=None,
                arxiv_id=None,
                doi=None,
                corpus_id=None,
                external_ids={},
                publication_types=[],
                publication_date=None,
                journal=None
            )
        ]
        
        requirements = [
            "Multi-turn reinforcement learning",
            "Large-scale systems"
        ]
        
        result = self.manager.create_requirement_based_review(papers, requirements)
        
        # Check that a file path is returned
        assert isinstance(result, str)
        assert ".md" in result


if __name__ == "__main__":
    pytest.main([__file__])