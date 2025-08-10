"""Tests for main MCP server functionality."""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, mock_open
from pathlib import Path

# Add the beta directory to the path for imports
import sys
import os
beta_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'beta'))
if beta_path not in sys.path:
    sys.path.insert(0, beta_path)

from main import app
from models import SemanticScholarPaper, ArxivPaper, AuthorInfo, CitationAnalysisResult, SearchResult

# Import individual tool functions for testing
from paper_analysis_tools import (
    analyze_paper_citations,
    search_papers_by_keywords,
    search_papers_by_author,
    get_paper_details,
    get_arxiv_paper,
    search_arxiv_papers,
    save_paper_to_markdown,
    organize_papers_by_topic,
    generate_literature_review,
    search_papers_in_collection,
    get_paper_recommendations,
    create_requirement_based_review
)

from pdf_processing_tools import (
    download_arxiv_pdf,
    extract_pdf_text,
    convert_pdf_to_text,
    process_arxiv_paper
)

from service_tools import get_service_info


class TestMCPServer:
    """Test cases for MCP server tools."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = app
    
    @pytest.mark.asyncio
    async def test_analyze_paper_citations(self):
        """Test citation analysis tool."""
        # Mock the semantic scholar client
        mock_analysis = {
            'main_paper': {
                'paper_id': '123456',
                'title': 'Test Paper',
                'abstract': 'Test abstract',
                'authors': [],
                'year': 2023,
                'citation_count': 10,
                'reference_count': 5,
                'influential_citation_count': 3,
                'venue': 'Test Venue',
                'url': None,
                'arxiv_id': None,
                'doi': None,
                'corpus_id': None,
                'external_ids': {},
                'publication_types': [],
                'publication_date': None,
                'journal': None
            },
            'citing_papers': [
                {
                    'paper_id': 'citing1',
                    'title': 'Citing Paper 1',
                    'abstract': 'Citing abstract',
                    'authors': [],
                    'year': 2023,
                    'citation_count': 5,
                    'reference_count': 3,
                    'influential_citation_count': 2,
                    'venue': 'Citing Venue',
                    'url': None,
                    'arxiv_id': None,
                    'doi': None,
                    'corpus_id': None,
                    'external_ids': {},
                    'publication_types': [],
                    'publication_date': None,
                    'journal': None
                }
            ],
            'referenced_papers': [
                {
                    'paper_id': 'ref1',
                    'title': 'Referenced Paper 1',
                    'abstract': 'Referenced abstract',
                    'authors': [],
                    'year': 2022,
                    'citation_count': 20,
                    'reference_count': 10,
                    'influential_citation_count': 8,
                    'venue': 'Referenced Venue',
                    'url': None,
                    'arxiv_id': None,
                    'doi': None,
                    'corpus_id': None,
                    'external_ids': {},
                    'publication_types': [],
                    'publication_date': None,
                    'journal': None
                }
            ],
            'recommendations': [
                {
                    'paper_id': 'rec1',
                    'title': 'Recommended Paper 1',
                    'citation_count': 15
                }
            ],
            'citation_count': 1,
            'reference_count': 1,
            'analysis_file': '/tmp/analysis.json'
        }
        
        with patch('semantic_scholar_client.SemanticScholarClient.analyze_paper_citations') as mock_analyze:
            mock_analyze.return_value = mock_analysis
            
            # Test the tool function directly
            result = await analyze_paper_citations('123456')
            
            assert 'main_paper' in result
            assert result['main_paper']['paper_id'] == '123456'
            assert result['total_citations'] == 1
            assert len(result['citing_papers']) == 1
            assert len(result['referenced_papers']) == 1
            assert len(result['recommendations']) == 1
    
    @pytest.mark.asyncio
    async def test_search_papers_by_keywords(self):
        """Test keyword search tool."""
        # Mock search result
        mock_papers = [
            SemanticScholarPaper(
                paper_id='search1',
                title='Machine Learning Paper',
                abstract='This paper discusses ML algorithms.',
                authors=[{
                    'name': 'ML Author',
                    'authorId': '1'
                }],
                year=2023,
                citation_count=10,
                reference_count=20,
                influential_citation_count=5,
                venue='ML Conference',
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
        
        mock_search_result = SearchResult(
            total=1,
            offset=0,
            next_offset=None,
            papers=mock_papers
        )
        
        with patch('semantic_scholar_client.SemanticScholarClient.search_papers') as mock_search:
            mock_search.return_value = mock_search_result
            
            result = await search_papers_by_keywords('machine learning', max_results=10)
            
            assert 'papers' in result
            assert len(result['papers']) == 1
            assert result['papers'][0]['title'] == 'Machine Learning Paper'
    
    @pytest.mark.asyncio
    async def test_search_papers_by_author(self):
        """Test author search tool."""
        # Mock author search result
        mock_author_data = {
            'authorId': 'author123',
            'name': 'Test Author',
            'paperCount': 10,
            'citationCount': 100,
            'papers': [
                {
                    'paperId': 'paper1',
                    'title': 'Author Paper 1',
                    'abstract': 'First paper by the author.',
                    'authors': [{'name': 'Test Author', 'authorId': 'author123'}],
                    'year': 2023,
                    'citationCount': 15,
                    'referenceCount': 25,
                    'influentialCitationCount': 8,
                    'venue': 'Author Conference',
                    'url': None,
                    'arxivId': None,
                    'doi': None,
                    'corpusId': None,
                    'externalIds': {},
                    'publicationTypes': [],
                    'publicationDate': None,
                    'journal': None
                }
            ]
        }
        
        with patch('semantic_scholar_client.SemanticScholarClient.search_authors') as mock_search_authors:
            with patch('semantic_scholar_client.SemanticScholarClient.get_author_papers') as mock_author_papers:
                # Mock author search result
                from models import AuthorInfo
                mock_author = AuthorInfo(
                    name='Test Author', 
                    author_id='author123',
                    aliases=[],
                    affiliations=[],
                    homepage=None,
                    paper_count=15,
                    citation_count=200,
                    h_index=8
                )
                mock_search_authors.return_value = [mock_author]
                
                # Mock author papers
                mock_papers = [SemanticScholarPaper.from_dict(mock_author_data['papers'][0])]
                mock_author_papers.return_value = mock_papers
                
                result = await search_papers_by_author('Test Author', max_results=10)
            
            assert 'author_info' in result
            assert 'papers' in result
            assert result['author_info']['name'] == 'Test Author'
            assert len(result['papers']) == 1
            assert result['papers'][0]['title'] == 'Author Paper 1'
    
    @pytest.mark.asyncio
    async def test_get_paper_details(self):
        """Test paper details retrieval tool."""
        # Mock paper data
        mock_paper = SemanticScholarPaper(
            paper_id='details123',
            title='Detailed Paper',
            abstract='This is a detailed paper abstract.',
            authors=[{
                'name': 'Detail Author',
                'authorId': 'detail1'
            }],
            year=2023,
            citation_count=15,
            reference_count=25,
            influential_citation_count=8,
            venue='Detail Conference',
            url=None,
            arxiv_id=None,
            doi=None,
            corpus_id=None,
            external_ids={},
            publication_types=[],
            publication_date=None,
            journal=None
        )

        
        with patch('semantic_scholar_client.SemanticScholarClient.get_paper') as mock_get:
            mock_get.return_value = mock_paper
            
            result = await get_paper_details('details123')
            
            assert 'paper' in result
            assert result['paper']['paper_id'] == 'details123'
            assert result['paper']['title'] == 'Detailed Paper'
            assert result['paper']['citation_count'] == 15
    
    @pytest.mark.asyncio
    async def test_get_arxiv_paper(self):
        """Test ArXiv paper retrieval tool."""
        # Mock ArXiv paper
        mock_paper = ArxivPaper(
            title='ArXiv Test Paper',
            authors=['ArXiv Author 1', 'ArXiv Author 2'],
            abstract='This is an ArXiv paper abstract.',
            arxiv_id='2301.12345',
            published_date='2023-01-15',
            pdf_url='https://arxiv.org/pdf/2301.12345.pdf',
            categories=['cs.AI', 'cs.LG']
        )
        
        with patch('arxiv_client.ArxivClient.get_paper_by_id') as mock_get:
            mock_get.return_value = mock_paper
            
            result = await get_arxiv_paper('2301.12345')
            
            assert 'paper' in result
            assert result['paper']['arxiv_id'] == '2301.12345'
            assert result['paper']['title'] == 'ArXiv Test Paper'
            assert len(result['paper']['authors']) == 2
    
    @pytest.mark.asyncio
    async def test_search_arxiv_papers(self):
        """Test ArXiv paper search tool."""
        # Mock ArXiv search results
        mock_papers = [
            ArxivPaper(
                title='ArXiv Search Result 1',
                authors=['Search Author 1'],
                abstract='First search result.',
                arxiv_id='2301.11111',
                published_date='2023-01-10',
                pdf_url='https://arxiv.org/pdf/2301.11111.pdf',
                categories=['cs.AI']
            ),
            ArxivPaper(
                title='ArXiv Search Result 2',
                authors=['Search Author 2'],
                abstract='Second search result.',
                arxiv_id='2301.22222',
                published_date='2023-01-20',
                pdf_url='https://arxiv.org/pdf/2301.22222.pdf',
                categories=['cs.LG']
            )
        ]
        
        with patch('arxiv_client.ArxivClient.search_papers') as mock_search:
            mock_search.return_value = mock_papers
            
            result = await search_arxiv_papers('machine learning', max_results=10)
            
            assert 'papers' in result
            assert len(result['papers']) == 2
            assert result['papers'][0]['title'] == 'ArXiv Search Result 1'
            assert result['papers'][1]['title'] == 'ArXiv Search Result 2'
    
    @pytest.mark.asyncio
    async def test_save_paper_to_markdown(self):
        """Test saving paper to markdown tool."""
        # Mock paper data
        paper_data = {
            'paper_id': 'save123',
            'title': 'Paper to Save',
            'abstract': 'This paper will be saved.',
            'authors': [{'name': 'Save Author', 'author_id': '1'}],
            'year': 2023,
            'citation_count': 5,
            'reference_count': 15,
            'influential_citation_count': 2,
            'venue': 'Save Conference',
            'url': None,
            'arxiv_id': None,
            'doi': None,
            'corpus_id': None,
            'external_ids': None,
            'publication_types': None,
            'publication_date': None,
            'journal': None
        }
        
        with patch('paper_manager.PaperManager.save_paper_to_markdown') as mock_save:
            mock_save.return_value = '/fake/path/paper_to_save.md'
            
            # Mock get_paper to return the paper data
            with patch('semantic_scholar_client.SemanticScholarClient.get_paper') as mock_get_paper:
                mock_get_paper.return_value = SemanticScholarPaper.from_dict(paper_data)
                
                result = await save_paper_to_markdown('save123', 'machine_learning')
            
            assert 'filepath' in result
            assert 'paper_to_save.md' in result['filepath']
            assert result['success'] == True
    
    @pytest.mark.asyncio
    async def test_organize_papers_by_topic(self):
        """Test organizing papers by topic tool."""
        # Mock papers data
        papers_data = [
            {
                'paper_id': 'org1',
                'title': 'ML Paper for Organization',
                'abstract': 'Machine learning research.',
                'authors': [{'name': 'Org Author 1', 'author_id': '1'}],
                'year': 2023,
                'citation_count': 10,
                'reference_count': 20,
                'influential_citation_count': 5,
                'venue': 'ML Conference'
            },
            {
                'paper_id': 'org2',
                'title': 'Robotics Paper for Organization',
                'abstract': 'Robot navigation systems.',
                'authors': [{'name': 'Org Author 2', 'author_id': '2'}],
                'year': 2023,
                'citation_count': 8,
                'reference_count': 18,
                'influential_citation_count': 3,
                'venue': 'Robotics Conference'
            }
        ]
        
        mock_organization = {
            'machine_learning': ['/fake/path/ml_paper.md'],
            'robotics': ['/fake/path/robotics_paper.md']
        }
        
        with patch('paper_manager.PaperManager.organize_papers_by_topic') as mock_organize:
            mock_organize.return_value = mock_organization
            
            result = await organize_papers_by_topic()
            
            assert 'organization' in result
            assert 'machine_learning' in result['organization']
            assert 'robotics' in result['organization']
            assert len(result['organization']['machine_learning']) == 1
            assert len(result['organization']['robotics']) == 1
    
    @pytest.mark.asyncio
    async def test_generate_literature_review(self):
        """Test literature review generation tool."""
        # Mock papers data
        papers_data = [
            {
                'paper_id': 'review1',
                'title': 'Review Paper 1',
                'abstract': 'First paper for review.',
                'authors': [{'name': 'Review Author 1', 'author_id': '1'}],
                'year': 2023,
                'citation_count': 20,
                'reference_count': 30,
                'influential_citation_count': 10,
                'venue': 'Review Conference'
            }
        ]
        
        mock_review = "# Literature Review: Test Topic\n\n## Overview\n\nThis is a test review."
        
        with patch('paper_manager.PaperManager.generate_literature_review') as mock_gen:
            mock_gen.return_value = mock_review
            
            result = await generate_literature_review('Test Topic', ['requirement1', 'requirement2'])
            
            assert 'filepath' in result
            assert 'Literature Review: Test Topic' in result['filepath']
            assert 'Overview' in result['filepath']
    
    @pytest.mark.asyncio
    async def test_search_papers_in_collection(self):
        """Test searching papers in local collection tool."""
        # Mock search results
        mock_results = [
            {
                'file_path': '/fake/path/found_paper1.md',
                'title': 'Found Paper 1',
                'content_snippet': 'This paper matches the search query.'
            },
            {
                'file_path': '/fake/path/found_paper2.md',
                'title': 'Found Paper 2',
                'content_snippet': 'Another paper that matches.'
            }
        ]
        
        with patch('paper_manager.PaperManager.search_papers_by_keyword') as mock_search:
            mock_search.return_value = mock_results
            
            result = await search_papers_in_collection('search query')
            
            assert 'papers' in result
            assert len(result['papers']) == 2
            assert result['papers'][0]['title'] == 'Found Paper 1'
            assert result['papers'][1]['title'] == 'Found Paper 2'
    
    @pytest.mark.asyncio
    async def test_get_paper_recommendations(self):
        """Test paper recommendations tool."""
        # Mock recommendations
        mock_recommendations = [
            SemanticScholarPaper(
                paper_id='rec1',
                title='Recommended Paper 1',
                abstract='This is a recommended paper.',
                authors=[AuthorInfo(
                    name='Rec Author 1', 
                    author_id='1',
                    aliases=[],
                    affiliations=[],
                    homepage=None,
                    paper_count=0,
                    citation_count=0,
                    h_index=0
                )],
                year=2023,
                citation_count=15,
                reference_count=25,
                influential_citation_count=8,
                venue='Rec Conference',
                url=None,
                arxiv_id=None,
                doi=None,
                corpus_id=None,
                external_ids=None,
                publication_types=None,
                publication_date=None,
                journal=None
            )
        ]
        
        with patch('semantic_scholar_client.SemanticScholarClient.get_paper_recommendations') as mock_rec:
            mock_rec.return_value = mock_recommendations
            
            result = await get_paper_recommendations('base123', max_results=5)
            
            assert 'recommendations' in result
            assert len(result['recommendations']) == 1
            assert result['recommendations'][0]['title'] == 'Recommended Paper 1'
    
    @pytest.mark.asyncio
    async def test_create_requirement_based_review(self):
        """Test requirement-based review creation tool."""
        # Mock papers and requirements
        papers_data = [
            {
                'paper_id': 'req1',
                'title': 'Requirement Paper 1',
                'abstract': 'Multi-turn reinforcement learning research.',
                'authors': [{'name': 'Req Author 1', 'authorId': '1'}],
                'year': 2023,
                'citation_count': 12,
                'reference_count': 22,
                'influential_citation_count': 6,
                'venue': 'RL Conference',
                'url': None,
                'arxiv_id': None,
                'doi': None,
                'corpus_id': None,
                'external_ids': {},
                'publication_types': [],
                'publication_date': None,
                'journal': None
            }
        ]
        
        requirements = ['Multi-turn reinforcement learning', 'Large-scale systems']
        
        mock_review = "# Requirement-Based Literature Review\n\n## Multi-turn reinforcement learning - Related\n\nFound papers."
        
        with patch('paper_manager.PaperManager.create_requirement_based_review') as mock_create:
            mock_create.return_value = mock_review
            
            with patch('semantic_scholar_client.SemanticScholarClient.get_paper') as mock_get_paper:
                mock_get_paper.return_value = SemanticScholarPaper.from_dict(papers_data[0])
                
                result = await create_requirement_based_review(['req1'], requirements)
            
            assert 'filepath' in result
            assert 'Requirement-Based Literature Review' in result['filepath']
            assert 'Multi-turn reinforcement learning' in result['filepath']
    
    # ===== PDF Processing Tests =====
    
    @pytest.mark.asyncio
    async def test_download_arxiv_pdf(self):
        """Test ArXiv PDF download tool."""
        # Mock successful download
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value = b'fake pdf content'
        
        with patch('urllib.request.urlopen') as mock_urlopen:
            with patch('os.path.getsize') as mock_getsize:
                with patch('pathlib.Path.mkdir') as mock_mkdir:
                    with patch('builtins.open', mock_open()) as mock_file:
                        mock_urlopen.return_value.__enter__.return_value = mock_response
                        mock_getsize.return_value = 1024000  # 1MB
                        
                        result = await download_arxiv_pdf('2301.07041')
                        
                        assert result['success'] == True
                        assert result['arxiv_id'] == '2301.07041'
                        assert result['file_size_mb'] == 0.98
                        assert 'local_path' in result
    
    @pytest.mark.asyncio
    async def test_download_arxiv_pdf_not_found(self):
        """Test ArXiv PDF download with 404 error."""
        from urllib.error import HTTPError
        
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.side_effect = HTTPError(None, 404, 'Not Found', None, None)
            
            result = await download_arxiv_pdf('invalid_id')
            
            assert result['success'] == False
            assert 'not found' in result['error'].lower()
            assert result['arxiv_id'] == 'invalid_id'
    
    @pytest.mark.asyncio
    async def test_extract_pdf_text(self):
        """Test PDF text extraction tool."""
        # Mock PDF reader
        mock_page = Mock()
        mock_page.extract_text.return_value = 'This is page 1 content.'
        
        mock_reader = Mock()
        mock_reader.pages = [mock_page]
        
        with patch('pdf_processing_tools.PdfReader') as mock_pdf_reader:
            with patch('os.path.exists') as mock_exists:
                mock_pdf_reader.return_value = mock_reader
                mock_exists.return_value = True
                
                result = await extract_pdf_text('/fake/path/test.pdf')
                
                assert result['success'] == True
                assert result['total_pages'] == 1
                assert result['word_count'] == 9  # "This is page 1 content." has 9 words
                assert 'This is page 1 content.' in result['text_content']
    
    @pytest.mark.asyncio
    async def test_extract_pdf_text_no_pypdf(self):
        """Test PDF text extraction when pypdf is not available."""
        with patch('pdf_processing_tools.PDF_READER_AVAILABLE', False):
            result = await extract_pdf_text('/fake/path/test.pdf')
            
            assert result['success'] == False
            assert 'pypdf' in result['error'].lower()
    
    @pytest.mark.asyncio
    async def test_extract_pdf_text_file_not_found(self):
        """Test PDF text extraction with missing file."""
        with patch('pdf_processing_tools.PdfReader') as mock_pdf_reader:
            with patch('os.path.exists') as mock_exists:
                mock_exists.return_value = False
                
                result = await extract_pdf_text('/fake/path/missing.pdf')
                
                assert result['success'] == False
                assert 'not found' in result['error'].lower()
    
    @pytest.mark.asyncio
    async def test_convert_pdf_to_text(self):
        """Test PDF to text conversion tool."""
        # Mock PDF reader
        mock_page = Mock()
        mock_page.extract_text.return_value = 'This is converted text.'
        
        mock_reader = Mock()
        mock_reader.pages = [mock_page]
        
        with patch('pdf_processing_tools.PdfReader') as mock_pdf_reader:
            with patch('os.path.exists') as mock_exists:
                with patch('pathlib.Path.mkdir') as mock_mkdir:
                    with patch('builtins.open', mock_open()) as mock_file:
                        with patch('os.path.getsize') as mock_getsize:
                            mock_pdf_reader.return_value = mock_reader
                            mock_exists.return_value = True
                            mock_getsize.return_value = 512
                            
                            result = await convert_pdf_to_text('/fake/path/test.pdf')
                            
                            assert result['success'] == True
                            assert result['total_pages'] == 1
                            assert result['word_count'] == 8  # "This is converted text." has 8 words
                            assert result['output_file_size_bytes'] == 512
                            assert 'output_path' in result
    
    @pytest.mark.asyncio
    async def test_process_arxiv_paper(self):
        """Test one-stop ArXiv paper processing tool."""
        # Mock download result
        mock_download_result = {
            'success': True,
            'arxiv_id': '2301.07041',
            'local_path': '/fake/path/2301.07041.pdf',
            'file_size_mb': 1.5
        }
        
        # Mock text extraction result
        mock_text_result = {
            'success': True,
            'total_pages': 10,
            'word_count': 5000,
            'character_count': 30000,
            'text_content': 'Extracted paper content...'
        }
        
        # Mock text conversion result
        mock_convert_result = {
            'success': True,
            'output_path': '/fake/path/2301.07041.txt',
            'output_file_size_bytes': 25000
        }
        
        with patch('pdf_processing_tools.download_arxiv_pdf') as mock_download:
            with patch('pdf_processing_tools.extract_pdf_text') as mock_extract:
                with patch('pdf_processing_tools.convert_pdf_to_text') as mock_convert:
                    with patch('pdf_processing_tools.PdfReader') as mock_pdf_reader:
                        mock_download.return_value = mock_download_result
                        mock_extract.return_value = mock_text_result
                        mock_convert.return_value = mock_convert_result
                        mock_pdf_reader.return_value = True  # Simulate pypdf available
                        
                        result = await process_arxiv_paper('2301.07041')
                        
                        assert result['success'] == True
                        assert result['arxiv_id'] == '2301.07041'
                        assert result['pdf_downloaded'] == True
                        assert result['text_extracted'] == True
                        assert result['text_file_saved'] == True
                        assert result['total_pages'] == 10
                        assert result['word_count'] == 5000
    
    @pytest.mark.asyncio
    async def test_process_arxiv_paper_download_failed(self):
        """Test ArXiv paper processing when download fails."""
        mock_download_result = {
            'success': False,
            'error': 'Download failed',
            'arxiv_id': 'invalid_id'
        }
        
        with patch('pdf_processing_tools.download_arxiv_pdf') as mock_download:
            mock_download.return_value = mock_download_result
            
            result = await process_arxiv_paper('invalid_id')
            
            assert result['success'] == False
            assert result['error'] == 'Download failed'
    
    @pytest.mark.asyncio
    async def test_get_service_info(self):
        """Test service information tool."""
        result = await get_service_info()
        
        assert 'service_name' in result
        assert 'description' in result
        assert 'version' in result
        assert 'available_tools' in result
        assert 'paper_analysis' in result['available_tools']
        assert 'pdf_processing' in result['available_tools']
        assert 'service_info' in result['available_tools']
        assert len(result['available_tools']['paper_analysis']) == 13
        assert len(result['available_tools']['pdf_processing']) == 4
        assert len(result['available_tools']['service_info']) == 1
        assert 'pdf_processing_available' in result


if __name__ == "__main__":
    pytest.main([__file__])