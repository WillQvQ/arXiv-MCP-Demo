"""Semantic Scholar API client with full endpoint support."""

import json
from typing import List, Optional, Dict, Any, Union
import aiohttp
from models import SemanticScholarPaper, AuthorInfo, SearchResult
from config import Config
from utils import (
    debug_print, AsyncContextManager, RateLimiter, 
    handle_rate_limit_retry, save_json_to_file, chunk_list
)


class SemanticScholarClient:
    """Client for interacting with Semantic Scholar API."""
    
    def __init__(self, debug: bool = Config.DEBUG_MODE):
        self.debug = debug
        self.rate_limiter = RateLimiter()
        self.base_url = Config.SEMANTIC_SCHOLAR_BASE_URL
        self.headers = Config.get_api_headers()
    
    # Paper Data Endpoints
    
    async def get_paper(self, paper_id: str, fields: Optional[List[str]] = None) -> Optional[SemanticScholarPaper]:
        """Get paper details by ID (ArXiv ID, DOI, Corpus ID, etc.)."""
        debug_print(f"Fetching paper details for: {paper_id}", self.debug)
        
        if fields is None:
            fields = Config.PAPER_FIELDS
        
        fields_str = ','.join(fields)
        url = f"{self.base_url}/paper/{paper_id}?fields={fields_str}"
        
        async with AsyncContextManager() as session:
            async def make_request():
                await self.rate_limiter.wait()
                return await session.get(url)
            
            response = await handle_rate_limit_retry(make_request, debug=self.debug)
            
            if response and response.status == 200:
                data = await response.json()
                return SemanticScholarPaper.from_dict(data)
            else:
                debug_print(f"Failed to fetch paper {paper_id}: {response.status if response else 'No response'}", self.debug)
                return None
    
    async def get_paper_authors(self, paper_id: str, fields: Optional[List[str]] = None) -> List[AuthorInfo]:
        """Get authors of a paper."""
        debug_print(f"Fetching authors for paper: {paper_id}", self.debug)
        
        if fields is None:
            fields = Config.AUTHOR_FIELDS
        
        fields_str = ','.join(fields)
        url = f"{self.base_url}/paper/{paper_id}/authors?fields={fields_str}"
        
        async with AsyncContextManager() as session:
            async def make_request():
                await self.rate_limiter.wait()
                return await session.get(url)
            
            response = await handle_rate_limit_retry(make_request, debug=self.debug)
            
            if response and response.status == 200:
                data = await response.json()
                authors = []
                for author_data in data.get('data', []):
                    authors.append(AuthorInfo.from_dict(author_data))
                return authors
            else:
                debug_print(f"Failed to fetch authors for paper {paper_id}", self.debug)
                return []
    
    async def get_paper_citations(
        self, 
        paper_id: str, 
        fields: Optional[List[str]] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> List[SemanticScholarPaper]:
        """Get papers that cite this paper."""
        debug_print(f"Fetching citations for paper: {paper_id}", self.debug)
        
        if fields is None:
            fields = Config.CITATION_FIELDS
        
        fields_str = ','.join(fields)
        url = f"{self.base_url}/paper/{paper_id}/citations?fields={fields_str}&limit={limit}&offset={offset}"
        
        async with AsyncContextManager() as session:
            async def make_request():
                await self.rate_limiter.wait()
                return await session.get(url)
            
            response = await handle_rate_limit_retry(make_request, debug=self.debug)
            
            if response and response.status == 200:
                data = await response.json()
                citations = []
                for citation_data in data.get('data', []):
                    citing_paper = citation_data.get('citingPaper', {})
                    if citing_paper:
                        citations.append(SemanticScholarPaper.from_dict(citing_paper))
                return citations
            else:
                debug_print(f"Failed to fetch citations for paper {paper_id}", self.debug)
                return []
    
    async def get_paper_references(
        self, 
        paper_id: str, 
        fields: Optional[List[str]] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> List[SemanticScholarPaper]:
        """Get papers referenced by this paper."""
        debug_print(f"Fetching references for paper: {paper_id}", self.debug)
        
        if fields is None:
            fields = Config.CITATION_FIELDS
        
        fields_str = ','.join(fields)
        url = f"{self.base_url}/paper/{paper_id}/references?fields={fields_str}&limit={limit}&offset={offset}"
        
        async with AsyncContextManager() as session:
            async def make_request():
                await self.rate_limiter.wait()
                return await session.get(url)
            
            response = await handle_rate_limit_retry(make_request, debug=self.debug)
            
            if response and response.status == 200:
                data = await response.json()
                references = []
                for ref_data in data.get('data', []):
                    cited_paper = ref_data.get('citedPaper', {})
                    if cited_paper:
                        references.append(SemanticScholarPaper.from_dict(cited_paper))
                return references
            else:
                debug_print(f"Failed to fetch references for paper {paper_id}", self.debug)
                return []
    
    async def search_papers(
        self,
        query: str,
        year: Optional[str] = None,
        venue: Optional[List[str]] = None,
        fields_of_study: Optional[List[str]] = None,
        publication_types: Optional[List[str]] = None,
        min_citation_count: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
        fields: Optional[List[str]] = None
    ) -> SearchResult:
        """Search for papers with advanced filtering."""
        debug_print(f"Searching papers with query: {query}", self.debug)
        
        if fields is None:
            fields = Config.PAPER_FIELDS
        
        # Build query parameters
        params = {
            'query': query,
            'limit': limit,
            'offset': offset,
            'fields': ','.join(fields)
        }
        
        if year:
            params['year'] = year
        if venue:
            params['venue'] = ','.join(venue)
        if fields_of_study:
            params['fieldsOfStudy'] = ','.join(fields_of_study)
        if publication_types:
            params['publicationTypes'] = ','.join(publication_types)
        if min_citation_count is not None:
            params['minCitationCount'] = min_citation_count
        
        url = f"{self.base_url}/paper/search"
        
        async with AsyncContextManager() as session:
            async def make_request():
                await self.rate_limiter.wait()
                return await session.get(url, params=params)
            
            response = await handle_rate_limit_retry(make_request, debug=self.debug)
            
            if response and response.status == 200:
                data = await response.json()
                papers = []
                for paper_data in data.get('data', []):
                    papers.append(SemanticScholarPaper.from_dict(paper_data))
                
                return SearchResult(
                    total=data.get('total', 0),
                    offset=data.get('offset', 0),
                    next_offset=data.get('next', None),
                    papers=papers
                )
            else:
                debug_print(f"Failed to search papers: {response.status if response else 'No response'}", self.debug)
                return SearchResult(total=0, offset=0, next_offset=None, papers=[])
    
    async def get_paper_bulk(
        self, 
        paper_ids: List[str], 
        fields: Optional[List[str]] = None
    ) -> List[SemanticScholarPaper]:
        """Get multiple papers in bulk (up to 500 per request)."""
        debug_print(f"Fetching {len(paper_ids)} papers in bulk", self.debug)
        
        if fields is None:
            fields = Config.PAPER_FIELDS
        
        all_papers = []
        
        # Split into chunks of 500 (API limit)
        chunks = chunk_list(paper_ids, Config.BATCH_SIZE)
        
        for i, chunk in enumerate(chunks):
            debug_print(f"Processing chunk {i+1}/{len(chunks)} with {len(chunk)} papers", self.debug)
            
            url = f"{self.base_url}/paper/batch"
            payload = {
                'ids': chunk,
                'fields': fields
            }
            
            async with AsyncContextManager() as session:
                async def make_request():
                    await self.rate_limiter.wait()
                    return await session.post(url, json=payload)
                
                response = await handle_rate_limit_retry(make_request, debug=self.debug)
                
                if response and response.status == 200:
                    data = await response.json()
                    
                    # Save raw response for debugging
                    if self.debug:
                        save_json_to_file(data, f"batch_response_chunk_{i+1}.json")
                    
                    for paper_data in data:
                        if paper_data:  # Skip None entries
                            all_papers.append(SemanticScholarPaper.from_dict(paper_data))
                else:
                    debug_print(f"Failed to fetch chunk {i+1}: {response.status if response else 'No response'}", self.debug)
        
        debug_print(f"Successfully fetched {len(all_papers)} papers from bulk request", self.debug)
        return all_papers
    
    # Author Data Endpoints
    
    async def get_author(self, author_id: str, fields: Optional[List[str]] = None) -> Optional[AuthorInfo]:
        """Get author details by ID."""
        debug_print(f"Fetching author details for: {author_id}", self.debug)
        
        if fields is None:
            fields = Config.AUTHOR_FIELDS
        
        fields_str = ','.join(fields)
        url = f"{self.base_url}/author/{author_id}?fields={fields_str}"
        
        async with AsyncContextManager() as session:
            async def make_request():
                await self.rate_limiter.wait()
                return await session.get(url)
            
            response = await handle_rate_limit_retry(make_request, debug=self.debug)
            
            if response and response.status == 200:
                data = await response.json()
                return AuthorInfo.from_dict(data)
            else:
                debug_print(f"Failed to fetch author {author_id}", self.debug)
                return None
    
    async def get_author_papers(
        self, 
        author_id: str, 
        fields: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[SemanticScholarPaper]:
        """Get papers by an author."""
        debug_print(f"Fetching papers for author: {author_id}", self.debug)
        
        if fields is None:
            fields = Config.PAPER_FIELDS
        
        fields_str = ','.join(fields)
        url = f"{self.base_url}/author/{author_id}/papers?fields={fields_str}&limit={limit}&offset={offset}"
        
        async with AsyncContextManager() as session:
            async def make_request():
                await self.rate_limiter.wait()
                return await session.get(url)
            
            response = await handle_rate_limit_retry(make_request, debug=self.debug)
            
            if response and response.status == 200:
                data = await response.json()
                papers = []
                for paper_data in data.get('data', []):
                    papers.append(SemanticScholarPaper.from_dict(paper_data))
                return papers
            else:
                debug_print(f"Failed to fetch papers for author {author_id}", self.debug)
                return []
    
    async def search_authors(
        self,
        query: str,
        fields: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuthorInfo]:
        """Search for authors."""
        debug_print(f"Searching authors with query: {query}", self.debug)
        
        if fields is None:
            fields = Config.AUTHOR_FIELDS
        
        params = {
            'query': query,
            'limit': limit,
            'offset': offset,
            'fields': ','.join(fields)
        }
        
        url = f"{self.base_url}/author/search"
        
        async with AsyncContextManager() as session:
            async def make_request():
                await self.rate_limiter.wait()
                return await session.get(url, params=params)
            
            response = await handle_rate_limit_retry(make_request, debug=self.debug)
            
            if response and response.status == 200:
                data = await response.json()
                authors = []
                for author_data in data.get('data', []):
                    authors.append(AuthorInfo.from_dict(author_data))
                return authors
            else:
                debug_print(f"Failed to search authors: {response.status if response else 'No response'}", self.debug)
                return []
    
    # Recommendations API
    
    async def get_paper_recommendations(
        self,
        paper_id: str,
        fields: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[SemanticScholarPaper]:
        """Get paper recommendations based on a paper."""
        debug_print(f"Fetching recommendations for paper: {paper_id}", self.debug)
        
        if fields is None:
            fields = Config.PAPER_FIELDS
        
        params = {
            'fields': ','.join(fields),
            'limit': limit
        }
        
        url = f"{self.base_url}/recommendations/v1/papers/forpaper/{paper_id}"
        
        async with AsyncContextManager() as session:
            async def make_request():
                await self.rate_limiter.wait()
                return await session.get(url, params=params)
            
            response = await handle_rate_limit_retry(make_request, debug=self.debug)
            
            if response and response.status == 200:
                data = await response.json()
                recommendations = []
                for rec_data in data.get('recommendedPapers', []):
                    recommendations.append(SemanticScholarPaper.from_dict(rec_data))
                return recommendations
            else:
                debug_print(f"Failed to get recommendations for paper {paper_id}", self.debug)
                return []
    
    # Utility Methods
    
    async def get_paper_embeddings(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Get SPECTER2 embeddings for a paper."""
        paper = await self.get_paper(paper_id, fields=['embedding'])
        return paper.embedding if paper else None
    
    async def analyze_paper_citations(self, paper_id: str) -> Dict[str, Any]:
        """Comprehensive citation analysis for a paper."""
        debug_print(f"Starting comprehensive citation analysis for: {paper_id}", self.debug)
        
        # Get main paper details
        main_paper = await self.get_paper(paper_id)
        if not main_paper:
            return {'error': f'Paper {paper_id} not found'}
        
        # Get citations and references
        citations = await self.get_paper_citations(paper_id)
        references = await self.get_paper_references(paper_id)
        
        # Get recommendations
        recommendations = await self.get_paper_recommendations(paper_id)
        
        analysis_result = {
            'main_paper': main_paper.to_dict(),
            'citation_count': len(citations),
            'reference_count': len(references),
            'citing_papers': [paper.to_dict() for paper in citations],
            'referenced_papers': [paper.to_dict() for paper in references],
            'recommendations': [paper.to_dict() for paper in recommendations[:10]],  # Top 10
            'analysis_timestamp': save_json_to_file({}, f"citation_analysis_{paper_id}.json")
        }
        
        # Save comprehensive analysis
        save_json_to_file(analysis_result, f"comprehensive_analysis_{paper_id}.json")
        
        debug_print(f"Citation analysis complete: {len(citations)} citations, {len(references)} references", self.debug)
        
        return analysis_result