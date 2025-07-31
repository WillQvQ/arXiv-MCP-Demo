"""Tests for utility functions."""

import pytest
import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add the beta directory to the path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'beta'))

from utils import (
    RateLimiter, handle_rate_limit_retry, save_json_to_file, 
    load_json_from_file, sanitize_filename, chunk_list, 
    extract_arxiv_id, format_authors, debug_print, get_timestamp
)


class TestRateLimiter:
    """Test cases for RateLimiter class."""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_initialization(self):
        """Test RateLimiter initialization."""
        limiter = RateLimiter(delay=0.5)
        assert limiter.delay == 0.5
        assert limiter.last_request_time == 0.0
    
    @pytest.mark.asyncio
    async def test_rate_limiter_wait(self):
        """Test RateLimiter wait functionality."""
        limiter = RateLimiter(delay=0.1)  # Short delay for testing
        
        # First call should not wait
        start_time = asyncio.get_event_loop().time()
        await limiter.wait()
        first_wait_time = asyncio.get_event_loop().time() - start_time
        
        # Second call should wait
        start_time = asyncio.get_event_loop().time()
        await limiter.wait()
        second_wait_time = asyncio.get_event_loop().time() - start_time
        
        # Second call should take longer due to rate limiting
        assert second_wait_time >= 0.05  # Allow some tolerance


class TestHandleRateLimitRetry:
    """Test cases for handle_rate_limit_retry function."""
    
    @pytest.mark.asyncio
    async def test_successful_request(self):
        """Test successful request without retries."""
        mock_response = Mock()
        mock_response.status = 200
        
        async def mock_request():
            return mock_response
        
        result = await handle_rate_limit_retry(mock_request, max_retries=3)
        assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_rate_limited_request_with_retry(self):
        """Test rate limited request that succeeds on retry."""
        call_count = 0
        
        async def mock_request():
            nonlocal call_count
            call_count += 1
            
            mock_response = Mock()
            if call_count == 1:
                mock_response.status = 429  # Rate limited
            else:
                mock_response.status = 200  # Success
            return mock_response
        
        result = await handle_rate_limit_retry(
            mock_request, 
            max_retries=3, 
            backoff_factor=0.01,  # Short backoff for testing
            debug=False
        )
        
        assert result.status == 200
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test when max retries are exceeded."""
        async def mock_request():
            mock_response = Mock()
            mock_response.status = 429  # Always rate limited
            return mock_response
        
        result = await handle_rate_limit_retry(
            mock_request, 
            max_retries=2, 
            backoff_factor=0.01,
            debug=False
        )
        
        assert result.status == 429


class TestFileOperations:
    """Test cases for file operation functions."""
    
    def test_save_and_load_json_file(self):
        """Test saving and loading JSON files."""
        test_data = {
            'title': 'Test Paper',
            'authors': ['Author One', 'Author Two'],
            'year': 2023
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save JSON file
            filepath = save_json_to_file(
                test_data, 
                'test_paper.json', 
                directory=temp_path
            )
            
            assert Path(filepath).exists()
            assert 'test_paper.json' in filepath
            
            # Load JSON file
            loaded_data = load_json_from_file(filepath)
            assert loaded_data == test_data
    
    def test_load_nonexistent_json_file(self):
        """Test loading a non-existent JSON file."""
        result = load_json_from_file('/nonexistent/path/file.json')
        assert result is None
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Test with invalid characters
        dirty_filename = 'Test<>:"/\\|?*File.txt'
        clean_filename = sanitize_filename(dirty_filename)
        
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            assert char not in clean_filename
        
        assert 'Test' in clean_filename
        assert 'File.txt' in clean_filename
    
    def test_sanitize_filename_with_spaces(self):
        """Test filename sanitization with leading/trailing spaces."""
        filename_with_spaces = '  Test File  '
        clean_filename = sanitize_filename(filename_with_spaces)
        
        assert clean_filename == 'Test File'
        assert not clean_filename.startswith(' ')
        assert not clean_filename.endswith(' ')


class TestUtilityFunctions:
    """Test cases for various utility functions."""
    
    def test_chunk_list(self):
        """Test list chunking functionality."""
        test_list = list(range(10))  # [0, 1, 2, ..., 9]
        
        # Test chunking into groups of 3
        chunks = chunk_list(test_list, 3)
        assert len(chunks) == 4  # [0,1,2], [3,4,5], [6,7,8], [9]
        assert chunks[0] == [0, 1, 2]
        assert chunks[1] == [3, 4, 5]
        assert chunks[2] == [6, 7, 8]
        assert chunks[3] == [9]
    
    def test_chunk_empty_list(self):
        """Test chunking an empty list."""
        chunks = chunk_list([], 5)
        assert chunks == []
    
    def test_chunk_list_smaller_than_chunk_size(self):
        """Test chunking a list smaller than chunk size."""
        test_list = [1, 2, 3]
        chunks = chunk_list(test_list, 5)
        assert len(chunks) == 1
        assert chunks[0] == [1, 2, 3]
    
    def test_extract_arxiv_id_from_url(self):
        """Test extracting ArXiv ID from URLs."""
        # Test various URL formats
        test_cases = [
            ('https://arxiv.org/abs/2301.12345', '2301.12345'),
            ('http://arxiv.org/abs/2301.12345v1', '2301.12345v1'),
            ('https://arxiv.org/pdf/2301.12345.pdf', '2301.12345'),
            ('https://arxiv.org/abs/cs/0701001', 'cs/0701001'),
        ]
        
        for url, expected_id in test_cases:
            extracted_id = extract_arxiv_id(url)
            assert extracted_id == expected_id
    
    def test_extract_arxiv_id_from_id(self):
        """Test extracting ArXiv ID when input is already an ID."""
        test_cases = [
            '2301.12345',
            '2301.12345v1',
            'cs/0701001',
            'math/0601001v2'
        ]
        
        for arxiv_id in test_cases:
            extracted_id = extract_arxiv_id(arxiv_id)
            assert extracted_id == arxiv_id
    
    def test_extract_arxiv_id_invalid(self):
        """Test extracting ArXiv ID from invalid input."""
        invalid_inputs = [
            'not-an-arxiv-id',
            'https://example.com/paper',
            '123',
            ''
        ]
        
        for invalid_input in invalid_inputs:
            extracted_id = extract_arxiv_id(invalid_input)
            assert extracted_id is None
    
    def test_format_authors_list(self):
        """Test formatting author lists."""
        # Test with dictionary format (Semantic Scholar style)
        authors_dict = [
            {'name': 'John Doe', 'authorId': '1'},
            {'name': 'Jane Smith', 'authorId': '2'},
            {'name': 'Bob Johnson', 'authorId': '3'}
        ]
        
        formatted = format_authors(authors_dict)
        assert formatted == "John Doe, Jane Smith, Bob Johnson"
    
    def test_format_authors_many(self):
        """Test formatting long author lists."""
        authors = [
            {'name': f'Author {i}', 'authorId': str(i)} 
            for i in range(5)
        ]
        
        formatted = format_authors(authors)
        assert 'et al.' in formatted
        assert 'Author 0' in formatted
        assert 'Author 1' in formatted
        assert 'Author 2' in formatted
    
    def test_format_authors_empty(self):
        """Test formatting empty author list."""
        formatted = format_authors([])
        assert formatted == "Unknown"
    
    def test_format_authors_string_format(self):
        """Test formatting authors in string format."""
        authors_str = ['John Doe', 'Jane Smith']
        formatted = format_authors(authors_str)
        assert formatted == "John Doe, Jane Smith"
    
    def test_get_timestamp(self):
        """Test timestamp generation."""
        timestamp = get_timestamp()
        assert isinstance(timestamp, str)
        assert len(timestamp) > 0
        
        # Check format (YYYY-MM-DD HH:MM:SS)
        import re
        pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        assert re.match(pattern, timestamp)
    
    def test_debug_print_enabled(self):
        """Test debug print when enabled."""
        with patch('builtins.print') as mock_print:
            debug_print("Test message", debug=True)
            mock_print.assert_called_once()
            
            # Check that the call contains the debug message
            call_args = mock_print.call_args[0][0]
            assert "DEBUG: Test message" in call_args
    
    def test_debug_print_disabled(self):
        """Test debug print when disabled."""
        with patch('builtins.print') as mock_print:
            debug_print("Test message", debug=False)
            mock_print.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__])