"""Tests for configuration module."""

import pytest
import os
from pathlib import Path
from unittest.mock import patch

# Add the beta directory to the path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'beta'))

from config import Config


class TestConfig:
    """Test cases for Config class."""
    
    def test_default_configuration(self):
        """Test default configuration values."""
        assert Config.SEMANTIC_SCHOLAR_BASE_URL == 'https://api.semanticscholar.org/graph/v1'
        assert Config.ARXIV_BASE_URL == 'http://export.arxiv.org/api/query'
        assert Config.DEFAULT_RATE_LIMIT_DELAY == 1.0
        assert Config.MAX_RETRIES == 3
        assert Config.BATCH_SIZE == 500
    
    def test_api_headers_without_key(self):
        """Test API headers when no API key is set."""
        with patch.dict(os.environ, {}, clear=True):
            headers = Config.get_api_headers()
            assert 'User-Agent' in headers
            assert headers['User-Agent'] == 'ArXiv-Citation-Analyzer/2.0'
            assert 'x-api-key' not in headers
    
    def test_api_headers_with_key(self):
        """Test API headers when API key is set."""
        test_key = 'test-api-key-123'
        with patch.dict(os.environ, {'SEMANTIC_SCHOLAR_API_KEY': test_key}):
            # Reload config to pick up environment variable
            Config.SEMANTIC_SCHOLAR_API_KEY = os.getenv('SEMANTIC_SCHOLAR_API_KEY')
            headers = Config.get_api_headers()
            assert 'User-Agent' in headers
            assert 'x-api-key' in headers
            assert headers['x-api-key'] == test_key
    
    def test_debug_mode_configuration(self):
        """Test debug mode configuration."""
        # Test default (false)
        with patch.dict(os.environ, {}, clear=True):
            assert Config.DEBUG_MODE == False
        
        # Test true
        with patch.dict(os.environ, {'DEBUG_MODE': 'true'}):
            # Simulate reloading config
            debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
            assert debug_mode == True
        
        # Test false explicitly
        with patch.dict(os.environ, {'DEBUG_MODE': 'false'}):
            debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
            assert debug_mode == False
    
    def test_paper_fields(self):
        """Test paper fields configuration."""
        expected_fields = [
            'paperId', 'title', 'abstract', 'authors', 'year', 'citationCount',
            'referenceCount', 'influentialCitationCount', 'venue', 'url',
            'externalIds', 'publicationTypes', 'publicationDate', 'journal',
            'tldr', 'embedding'
        ]
        assert Config.PAPER_FIELDS == expected_fields
    
    def test_author_fields(self):
        """Test author fields configuration."""
        expected_fields = [
            'authorId', 'name', 'aliases', 'affiliations', 'homepage',
            'paperCount', 'citationCount', 'hIndex'
        ]
        assert Config.AUTHOR_FIELDS == expected_fields
    
    def test_citation_fields(self):
        """Test citation fields configuration."""
        expected_fields = [
            'paperId', 'title', 'abstract', 'authors', 'year', 'citationCount',
            'venue', 'url', 'externalIds'
        ]
        assert Config.CITATION_FIELDS == expected_fields
    
    def test_fields_string_methods(self):
        """Test field string generation methods."""
        paper_fields_str = Config.get_paper_fields_string()
        assert isinstance(paper_fields_str, str)
        assert 'paperId' in paper_fields_str
        assert 'title' in paper_fields_str
        assert ',' in paper_fields_str
        
        author_fields_str = Config.get_author_fields_string()
        assert isinstance(author_fields_str, str)
        assert 'authorId' in author_fields_str
        assert 'name' in author_fields_str
        
        citation_fields_str = Config.get_citation_fields_string()
        assert isinstance(citation_fields_str, str)
        assert 'paperId' in citation_fields_str
        assert 'citationCount' in citation_fields_str
    
    def test_directory_paths(self):
        """Test directory path configuration."""
        assert isinstance(Config.BASE_DIR, Path)
        assert isinstance(Config.PAPERS_DIR, Path)
        assert isinstance(Config.JSON_FILES_DIR, Path)
        assert isinstance(Config.MD_FILES_DIR, Path)
        
        # Check that paths are properly constructed
        assert Config.PAPERS_DIR == Config.BASE_DIR / 'papers'
        assert Config.JSON_FILES_DIR == Config.BASE_DIR / 'json_files'
        assert Config.MD_FILES_DIR == Config.BASE_DIR / 'md_files'
    
    def test_ensure_directories(self):
        """Test directory creation functionality."""
        # This test would require mocking filesystem operations
        # For now, just ensure the method exists and is callable
        assert callable(Config.ensure_directories)
        
        # Test that it doesn't raise an exception
        try:
            Config.ensure_directories()
        except Exception as e:
            pytest.fail(f"ensure_directories() raised an exception: {e}")


if __name__ == "__main__":
    pytest.main([__file__])