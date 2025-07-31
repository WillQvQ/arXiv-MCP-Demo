"""Data models for ArXiv and Semantic Scholar papers."""

from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
import json


@dataclass
class ArxivPaper:
    """Data model for ArXiv papers."""
    title: str
    authors: List[str]
    abstract: str
    arxiv_id: str
    published_date: str
    pdf_url: str
    categories: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArxivPaper':
        """Create instance from dictionary."""
        return cls(**data)


@dataclass
class SemanticScholarPaper:
    """Data model for Semantic Scholar papers."""
    paper_id: str
    title: str
    abstract: Optional[str]
    authors: List[Dict[str, Any]]
    year: Optional[int]
    citation_count: int
    reference_count: int
    influential_citation_count: int
    venue: Optional[str]
    url: Optional[str]
    arxiv_id: Optional[str]
    doi: Optional[str]
    corpus_id: Optional[str]
    external_ids: Optional[Dict[str, Any]]
    publication_types: Optional[List[str]]
    publication_date: Optional[str]
    journal: Optional[Dict[str, Any]]
    citations: Optional[List[Dict[str, Any]]] = None
    references: Optional[List[Dict[str, Any]]] = None
    embedding: Optional[Dict[str, Any]] = None
    tldr: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SemanticScholarPaper':
        """Create instance from dictionary."""
        # Map API field names to model field names
        field_mapping = {
            'paperId': 'paper_id',
            'citationCount': 'citation_count',
            'referenceCount': 'reference_count',
            'influentialCitationCount': 'influential_citation_count',
            'arxivId': 'arxiv_id',
            'corpusId': 'corpus_id',
            'externalIds': 'external_ids',
            'publicationTypes': 'publication_types',
            'publicationDate': 'publication_date'
        }
        
        # Get valid field names for this class
        import inspect
        valid_fields = set(inspect.signature(cls).parameters.keys())
        
        # Convert field names
        converted_data = {}
        for key, value in data.items():
            new_key = field_mapping.get(key, key)
            # Only include fields that are defined in the model
            if new_key in valid_fields:
                converted_data[new_key] = value
        
        # Set default values for required fields if missing
        defaults = {
            'citation_count': 0,
            'reference_count': 0,
            'influential_citation_count': 0,
            'authors': [],
            'arxiv_id': None,
            'doi': None,
            'corpus_id': None
        }
        
        for key, default_value in defaults.items():
            if key not in converted_data:
                converted_data[key] = default_value
        
        return cls(**converted_data)
    
    def get_author_names(self) -> List[str]:
        """Extract author names from author objects."""
        return [author.get('name', '') for author in self.authors if author.get('name')]


@dataclass
class AuthorInfo:
    """Data model for author information."""
    author_id: str
    name: str
    aliases: Optional[List[str]]
    affiliations: Optional[List[str]]
    homepage: Optional[str]
    paper_count: Optional[int]
    citation_count: Optional[int]
    h_index: Optional[int]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuthorInfo':
        """Create instance from dictionary."""
        # Map API field names to model field names
        field_mapping = {
            'authorId': 'author_id',
            'paperCount': 'paper_count',
            'citationCount': 'citation_count',
            'hIndex': 'h_index'
        }
        
        # Convert field names
        converted_data = {}
        for key, value in data.items():
            new_key = field_mapping.get(key, key)
            converted_data[new_key] = value
        
        return cls(**converted_data)


@dataclass
class CitationAnalysisResult:
    """Result of citation analysis."""
    main_paper: SemanticScholarPaper
    citing_papers: List[SemanticScholarPaper]
    referenced_papers: List[SemanticScholarPaper]
    total_citations: int
    total_references: int
    analysis_timestamp: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'main_paper': self.main_paper.to_dict(),
            'citing_papers': [paper.to_dict() for paper in self.citing_papers],
            'referenced_papers': [paper.to_dict() for paper in self.referenced_papers],
            'total_citations': self.total_citations,
            'total_references': self.total_references,
            'analysis_timestamp': self.analysis_timestamp
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)


@dataclass
class SearchResult:
    """Search result from Semantic Scholar API."""
    total: int
    offset: int
    next_offset: Optional[int]
    papers: List[SemanticScholarPaper]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'total': self.total,
            'offset': self.offset,
            'next_offset': self.next_offset,
            'papers': [paper.to_dict() for paper in self.papers]
        }