"""Pytest configuration and fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_arxiv_paper():
    """Sample ArXiv paper for testing."""
    from models import ArxivPaper
    
    return ArxivPaper(
        arxiv_id="2301.12345",
        title="Sample ArXiv Paper",
        abstract="This is a sample abstract for testing purposes.",
        authors=["John Doe", "Jane Smith"],
        published="2023-01-15",
        categories=["cs.AI", "cs.LG"],
        pdf_url="https://arxiv.org/pdf/2301.12345.pdf"
    )


@pytest.fixture
def sample_semantic_scholar_paper():
    """Sample Semantic Scholar paper for testing."""
    from models import SemanticScholarPaper, AuthorInfo
    
    return SemanticScholarPaper(
        paper_id="123456789",
        title="Sample Semantic Scholar Paper",
        abstract="This is a sample abstract for Semantic Scholar testing.",
        authors=[
            AuthorInfo(name="Alice Johnson", author_id="1"),
            AuthorInfo(name="Bob Wilson", author_id="2")
        ],
        year=2023,
        citation_count=25,
        reference_count=40,
        influential_citation_count=12,
        venue="Sample Conference",
        url="https://example.com/paper"
    )


@pytest.fixture
def sample_papers_list(sample_arxiv_paper, sample_semantic_scholar_paper):
    """List of sample papers for testing."""
    return [sample_arxiv_paper, sample_semantic_scholar_paper]


@pytest.fixture
def mock_config(temp_dir):
    """Mock configuration for testing."""
    from config import Config
    
    config = Config()
    config.papers_dir = temp_dir
    config.debug = True
    return config


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_http_response():
    """Mock HTTP response for testing."""
    class MockResponse:
        def __init__(self, status=200, json_data=None, text_data=None):
            self.status = status
            self._json_data = json_data or {}
            self._text_data = text_data or ""
        
        async def json(self):
            return self._json_data
        
        async def text(self):
            return self._text_data
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
    
    return MockResponse


@pytest.fixture
def mock_semantic_scholar_response():
    """Mock Semantic Scholar API response."""
    return {
        'paperId': 'test123',
        'title': 'Test Paper Title',
        'abstract': 'This is a test abstract.',
        'authors': [
            {'name': 'Test Author 1', 'authorId': '1'},
            {'name': 'Test Author 2', 'authorId': '2'}
        ],
        'year': 2023,
        'citationCount': 10,
        'referenceCount': 25,
        'influentialCitationCount': 5,
        'venue': 'Test Conference',
        'url': 'https://example.com/test-paper',
        'arxivId': None,
        'doi': None,
        'corpusId': None,
        'externalIds': None,
        'publicationTypes': None,
        'publicationDate': None,
        'journal': None
    }


@pytest.fixture
def mock_arxiv_xml_response():
    """Mock ArXiv XML response."""
    return '''
    <?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
        <entry>
            <id>http://arxiv.org/abs/2301.12345v1</id>
            <title>Test ArXiv Paper</title>
            <summary>This is a test ArXiv abstract.</summary>
            <published>2023-01-15T00:00:00Z</published>
            <author><name>Test ArXiv Author 1</name></author>
            <author><name>Test ArXiv Author 2</name></author>
            <link type="application/pdf" href="http://arxiv.org/pdf/2301.12345v1.pdf"/>
            <category term="cs.AI"/>
            <category term="cs.LG"/>
        </entry>
    </feed>
    '''