"""Utility functions for the MCP server."""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
import aiohttp
from config import Config


class RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self, delay: float = Config.DEFAULT_RATE_LIMIT_DELAY):
        self.delay = delay
        self.last_request_time = 0.0
    
    async def wait(self) -> None:
        """Wait if necessary to respect rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.delay:
            wait_time = self.delay - time_since_last
            await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()


async def handle_rate_limit_retry(
    request_func: Callable,
    max_retries: int = Config.MAX_RETRIES,
    backoff_factor: float = Config.BACKOFF_FACTOR,
    debug: bool = Config.DEBUG_MODE
) -> Optional[aiohttp.ClientResponse]:
    """Handle rate limiting with exponential backoff retry."""
    
    for attempt in range(max_retries + 1):
        try:
            response = await request_func()
            
            if response.status == 200:
                return response
            elif response.status == 429:  # Rate limited
                if attempt < max_retries:
                    wait_time = backoff_factor ** attempt
                    if debug:
                        print(f"Rate limited. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    if debug:
                        print(f"Max retries reached. Final status: {response.status}")
                    return response
            else:
                if debug:
                    print(f"Request failed with status {response.status}")
                return response
                
        except Exception as e:
            if debug:
                print(f"Request attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries:
                wait_time = backoff_factor ** attempt
                await asyncio.sleep(wait_time)
            else:
                raise e
    
    return None


def save_json_to_file(data: Dict[str, Any], filename: str, directory: Path = Config.JSON_FILES_DIR) -> str:
    """Save data to JSON file with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_with_timestamp = f"{timestamp}_{filename}"
    filepath = directory / filename_with_timestamp
    
    directory.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    return str(filepath)


def load_json_from_file(filepath: str) -> Optional[Dict[str, Any]]:
    """Load data from JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        if Config.DEBUG_MODE:
            print(f"Error loading JSON file {filepath}: {str(e)}")
        return None


def create_directory_structure(base_path: Path, subdirs: List[str]) -> None:
    """Create directory structure for organizing papers."""
    for subdir in subdirs:
        (base_path / subdir).mkdir(parents=True, exist_ok=True)


def get_timestamp() -> str:
    """Get current timestamp string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def extract_arxiv_id(url_or_id: str) -> Optional[str]:
    """Extract ArXiv ID from URL or return ID if already in correct format."""
    import re
    
    # Pattern for ArXiv ID (e.g., 2301.12345 or 1234.5678v1)
    arxiv_pattern = r'(\d{4}\.\d{4,5}(?:v\d+)?|[a-z-]+/\d{7}(?:v\d+)?)'
    
    # If it's a URL, extract the ID
    if 'arxiv.org' in url_or_id:
        match = re.search(arxiv_pattern, url_or_id)
        return match.group(1) if match else None
    
    # If it's already an ID, validate and return
    if re.match(f'^{arxiv_pattern}$', url_or_id):
        return url_or_id
    
    return None


def format_authors(authors: List[Dict[str, Any]]) -> str:
    """Format author list for display."""
    if not authors:
        return "Unknown"
    
    author_names = []
    for author in authors:
        if isinstance(author, dict):
            name = author.get('name', '')
        else:
            name = str(author)
        
        if name:
            author_names.append(name)
    
    if len(author_names) <= 3:
        return ", ".join(author_names)
    else:
        return f"{', '.join(author_names[:3])}, et al."


def debug_print(message: str, debug: bool = Config.DEBUG_MODE) -> None:
    """Print debug message if debug mode is enabled."""
    if debug:
        timestamp = get_timestamp()
        print(f"[{timestamp}] DEBUG: {message}")


class AsyncContextManager:
    """Async context manager for HTTP sessions."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self) -> aiohttp.ClientSession:
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers=Config.get_api_headers()
        )
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()