"""Configuration settings for the MCP server."""

import os
from typing import Optional
from pathlib import Path


class Config:
    """Configuration class for the ArXiv Citation Analyzer."""
    
    # API Configuration
    SEMANTIC_SCHOLAR_API_KEY: Optional[str] = os.getenv('SEMANTIC_SCHOLAR_API_KEY')
    SEMANTIC_SCHOLAR_BASE_URL: str = 'https://api.semanticscholar.org/graph/v1'
    ARXIV_BASE_URL: str = 'http://export.arxiv.org/api/query'
    
    # Rate Limiting
    DEFAULT_RATE_LIMIT_DELAY: float = 1.0  # seconds
    MAX_RETRIES: int = 3
    BACKOFF_FACTOR: float = 2.0
    
    # Batch Processing
    BATCH_SIZE: int = 500  # Semantic Scholar batch limit
    MAX_SEARCH_RESULTS: int = 100
    
    # File Paths
    BASE_DIR: Path = Path(__file__).parent.parent  # Go up from beta/ to project root
    PAPERS_DIR: Path = BASE_DIR / 'papers'
    JSON_FILES_DIR: Path = BASE_DIR / 'json_files'
    MD_FILES_DIR: Path = BASE_DIR / 'md_files'
    
    # Debug Mode
    DEBUG_MODE: bool = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    
    # Paper Fields for API Requests
    PAPER_FIELDS = [
        'paperId', 'title', 'abstract', 'authors', 'year', 'citationCount',
        'referenceCount', 'influentialCitationCount', 'venue', 'url',
        'externalIds', 'publicationTypes', 'publicationDate', 'journal',
        'tldr', 'embedding'
    ]
    
    AUTHOR_FIELDS = [
        'authorId', 'name', 'aliases', 'affiliations', 'homepage',
        'paperCount', 'citationCount', 'hIndex'
    ]
    
    CITATION_FIELDS = [
        'paperId', 'title', 'abstract', 'authors', 'year', 'citationCount',
        'venue', 'url', 'externalIds'
    ]
    
    @classmethod
    def get_api_headers(cls) -> dict:
        """Get headers for Semantic Scholar API requests."""
        headers = {'User-Agent': 'ArXiv-Citation-Analyzer/2.0'}
        if cls.SEMANTIC_SCHOLAR_API_KEY:
            headers['x-api-key'] = cls.SEMANTIC_SCHOLAR_API_KEY
        return headers
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required directories exist."""
        for directory in [cls.PAPERS_DIR, cls.JSON_FILES_DIR, cls.MD_FILES_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_paper_fields_string(cls) -> str:
        """Get comma-separated paper fields for API requests."""
        return ','.join(cls.PAPER_FIELDS)
    
    @classmethod
    def get_author_fields_string(cls) -> str:
        """Get comma-separated author fields for API requests."""
        return ','.join(cls.AUTHOR_FIELDS)
    
    @classmethod
    def get_citation_fields_string(cls) -> str:
        """Get comma-separated citation fields for API requests."""
        return ','.join(cls.CITATION_FIELDS)


# Initialize directories on import
Config.ensure_directories()