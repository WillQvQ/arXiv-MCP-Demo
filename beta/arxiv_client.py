"""ArXiv API client for paper retrieval."""

import xml.etree.ElementTree as ET
from typing import List, Optional
import aiohttp
from models import ArxivPaper
from config import Config
from utils import debug_print, AsyncContextManager, RateLimiter


class ArxivClient:
    """Client for interacting with ArXiv API."""
    
    def __init__(self, debug: bool = Config.DEBUG_MODE):
        self.debug = debug
        self.rate_limiter = RateLimiter()
        self.base_url = Config.ARXIV_BASE_URL
    
    async def get_paper_by_id(self, arxiv_id: str) -> Optional[ArxivPaper]:
        """Retrieve a single paper by ArXiv ID."""
        debug_print(f"Fetching ArXiv paper: {arxiv_id}", self.debug)
        
        # Clean the ArXiv ID
        clean_id = arxiv_id.replace('arXiv:', '').strip()
        
        query_url = f"{self.base_url}?id_list={clean_id}"
        
        async with AsyncContextManager() as session:
            await self.rate_limiter.wait()
            
            try:
                async with session.get(query_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self._parse_arxiv_response(content)
                    else:
                        debug_print(f"ArXiv API error: {response.status}", self.debug)
                        return None
            except Exception as e:
                debug_print(f"Error fetching ArXiv paper {arxiv_id}: {str(e)}", self.debug)
                return None
    
    async def search_papers(
        self, 
        query: str, 
        max_results: int = 10,
        sort_by: str = "relevance",
        sort_order: str = "descending"
    ) -> List[ArxivPaper]:
        """Search for papers on ArXiv."""
        debug_print(f"Searching ArXiv for: {query}", self.debug)
        
        # Construct search query
        search_query = query.replace(' ', '+AND+')
        query_url = (
            f"{self.base_url}?"
            f"search_query=all:{search_query}&"
            f"start=0&"
            f"max_results={max_results}&"
            f"sortBy={sort_by}&"
            f"sortOrder={sort_order}"
        )
        
        async with AsyncContextManager() as session:
            await self.rate_limiter.wait()
            
            try:
                async with session.get(query_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self._parse_arxiv_search_response(content)
                    else:
                        debug_print(f"ArXiv search error: {response.status}", self.debug)
                        return []
            except Exception as e:
                debug_print(f"Error searching ArXiv: {str(e)}", self.debug)
                return []
    
    async def search_by_author(self, author_name: str, max_results: int = 10) -> List[ArxivPaper]:
        """Search for papers by author name."""
        debug_print(f"Searching ArXiv by author: {author_name}", self.debug)
        
        author_query = author_name.replace(' ', '+')
        query_url = (
            f"{self.base_url}?"
            f"search_query=au:{author_query}&"
            f"start=0&"
            f"max_results={max_results}&"
            f"sortBy=submittedDate&"
            f"sortOrder=descending"
        )
        
        async with AsyncContextManager() as session:
            await self.rate_limiter.wait()
            
            try:
                async with session.get(query_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self._parse_arxiv_search_response(content)
                    else:
                        debug_print(f"ArXiv author search error: {response.status}", self.debug)
                        return []
            except Exception as e:
                debug_print(f"Error searching ArXiv by author: {str(e)}", self.debug)
                return []
    
    async def search_by_category(self, category: str, max_results: int = 10) -> List[ArxivPaper]:
        """Search for papers by category."""
        debug_print(f"Searching ArXiv by category: {category}", self.debug)
        
        query_url = (
            f"{self.base_url}?"
            f"search_query=cat:{category}&"
            f"start=0&"
            f"max_results={max_results}&"
            f"sortBy=submittedDate&"
            f"sortOrder=descending"
        )
        
        async with AsyncContextManager() as session:
            await self.rate_limiter.wait()
            
            try:
                async with session.get(query_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        return self._parse_arxiv_search_response(content)
                    else:
                        debug_print(f"ArXiv category search error: {response.status}", self.debug)
                        return []
            except Exception as e:
                debug_print(f"Error searching ArXiv by category: {str(e)}", self.debug)
                return []
    
    def _parse_arxiv_response(self, xml_content: str) -> Optional[ArxivPaper]:
        """Parse ArXiv API XML response for a single paper."""
        try:
            root = ET.fromstring(xml_content)
            
            # Define namespace
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            # Find the first entry
            entry = root.find('atom:entry', ns)
            if entry is None:
                debug_print("No entry found in ArXiv response", self.debug)
                return None
            
            return self._parse_entry(entry, ns)
            
        except ET.ParseError as e:
            debug_print(f"Error parsing ArXiv XML: {str(e)}", self.debug)
            return None
    
    def _parse_arxiv_search_response(self, xml_content: str) -> List[ArxivPaper]:
        """Parse ArXiv API XML response for search results."""
        papers = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Define namespace
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            # Find all entries
            entries = root.findall('atom:entry', ns)
            
            for entry in entries:
                paper = self._parse_entry(entry, ns)
                if paper:
                    papers.append(paper)
            
            debug_print(f"Parsed {len(papers)} papers from ArXiv search", self.debug)
            
        except ET.ParseError as e:
            debug_print(f"Error parsing ArXiv search XML: {str(e)}", self.debug)
        
        return papers
    
    def _parse_entry(self, entry, ns: dict) -> Optional[ArxivPaper]:
        """Parse a single entry from ArXiv XML."""
        try:
            # Extract basic information
            title = entry.find('atom:title', ns)
            title_text = title.text.strip().replace('\n', ' ') if title is not None else "Unknown Title"
            
            # Extract authors
            authors = []
            for author in entry.findall('atom:author', ns):
                name_elem = author.find('atom:name', ns)
                if name_elem is not None:
                    authors.append(name_elem.text.strip())
            
            # Extract abstract
            summary = entry.find('atom:summary', ns)
            abstract = summary.text.strip().replace('\n', ' ') if summary is not None else ""
            
            # Extract ArXiv ID from the ID field
            id_elem = entry.find('atom:id', ns)
            arxiv_id = ""
            if id_elem is not None:
                # Extract ID from URL like http://arxiv.org/abs/2301.12345v1
                id_url = id_elem.text
                if '/abs/' in id_url:
                    arxiv_id = id_url.split('/abs/')[-1]
            
            # Extract published date
            published = entry.find('atom:published', ns)
            published_date = published.text if published is not None else ""
            
            # Extract PDF URL
            pdf_url = ""
            for link in entry.findall('atom:link', ns):
                if link.get('type') == 'application/pdf':
                    pdf_url = link.get('href', '')
                    break
            
            # Extract categories
            categories = []
            for category in entry.findall('atom:category', ns):
                term = category.get('term')
                if term:
                    categories.append(term)
            
            return ArxivPaper(
                title=title_text,
                authors=authors,
                abstract=abstract,
                arxiv_id=arxiv_id,
                published_date=published_date,
                pdf_url=pdf_url,
                categories=categories
            )
            
        except Exception as e:
            debug_print(f"Error parsing ArXiv entry: {str(e)}", self.debug)
            return None