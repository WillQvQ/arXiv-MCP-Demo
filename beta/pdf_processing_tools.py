"""PDF处理工具模块 - 包含所有PDF下载、文本提取和转换功能"""

import os
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional

# PDF处理相关导入
try:
    from pypdf import PdfReader  # type: ignore
    PDF_READER_AVAILABLE = True
except ImportError:
    try:
        from PyPDF2 import PdfReader  # type: ignore
        PDF_READER_AVAILABLE = True
    except ImportError:
        print("Warning: PDF processing unavailable. Install pypdf: pip install pypdf")
        PdfReader = None  # type: ignore
        PDF_READER_AVAILABLE = False

from config import Config
from utils import debug_print, extract_arxiv_id


async def download_arxiv_pdf(
    arxiv_id: str,
    download_dir: str = "./downloads",
    filename: Optional[str] = None,
    debug: bool = Config.DEBUG_MODE
) -> Dict[str, Any]:
    """Download PDF file from ArXiv using paper ID.
    
    Args:
        arxiv_id: ArXiv paper ID (e.g., '2301.07041' or 'cs.AI/0301001')
        download_dir: Directory to save the PDF file
        filename: Custom filename for the PDF (without extension)
        debug: Enable debug output
    
    Returns:
        Dictionary containing download result
    """
    debug_print(f"Downloading ArXiv PDF: {arxiv_id}", debug)
    
    try:
        # 清理ArXiv ID格式
        clean_id = arxiv_id.strip()
        if clean_id.startswith("http"):
            if "arxiv.org/abs/" in clean_id:
                clean_id = clean_id.split("arxiv.org/abs/")[-1]
            elif "arxiv.org/pdf/" in clean_id:
                clean_id = clean_id.split("arxiv.org/pdf/")[-1]
                if clean_id.endswith(".pdf"):
                    clean_id = clean_id[:-4]
        
        # 设置下载目录
        download_path = Path(download_dir)
        download_path.mkdir(parents=True, exist_ok=True)
        
        # 设置文件名
        if not filename:
            filename = clean_id.replace("/", "_")
        if not filename.endswith(".pdf"):
            filename += ".pdf"
        
        full_path = download_path / filename
        
        # 构建ArXiv PDF URL
        pdf_url = f"https://arxiv.org/pdf/{clean_id}.pdf"
        
        # 下载PDF文件
        req = urllib.request.Request(
            pdf_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                with open(full_path, 'wb') as f:
                    f.write(response.read())
                
                file_size = os.path.getsize(full_path)
                
                return {
                    'success': True,
                    'arxiv_id': clean_id,
                    'pdf_url': pdf_url,
                    'local_path': str(full_path),
                    'file_size_bytes': file_size,
                    'file_size_mb': round(file_size / (1024 * 1024), 2)
                }
            else:
                raise Exception(f"HTTP {response.status}: Failed to download PDF")
                
    except urllib.error.HTTPError as e:
        if e.code == 404:
            error_msg = f"ArXiv paper '{arxiv_id}' not found. Please check the ID."
        else:
            error_msg = f"HTTP {e.code}: {e.reason}"
        
        debug_print(error_msg, debug)
        return {
            'success': False,
            'error': error_msg,
            'arxiv_id': arxiv_id
        }
        
    except Exception as e:
        error_msg = f"Error downloading PDF: {str(e)}"
        debug_print(error_msg, debug)
        return {
            'success': False,
            'error': error_msg,
            'arxiv_id': arxiv_id
        }


async def extract_pdf_text(
    pdf_path: str,
    start_page: Optional[int] = None,
    end_page: Optional[int] = None,
    debug: bool = Config.DEBUG_MODE
) -> Dict[str, Any]:
    """Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        start_page: Start page number (0-indexed, optional)
        end_page: End page number (0-indexed, optional)
        debug: Enable debug output
    
    Returns:
        Dictionary containing extracted text and metadata
    """
    debug_print(f"Extracting text from PDF: {pdf_path}", debug)
    
    if not PDF_READER_AVAILABLE:
        return {
            'success': False,
            'error': 'PDF processing unavailable. Install pypdf: pip install pypdf'
        }
    
    try:
        if not os.path.exists(pdf_path):
            return {
                'success': False,
                'error': f'PDF file not found: {pdf_path}'
            }
        
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        
        # 确定页面范围
        if start_page is not None and end_page is not None:
            pages_to_extract = reader.pages[start_page:end_page + 1]
            actual_start = start_page
        elif start_page is not None:
            pages_to_extract = reader.pages[start_page:]
            actual_start = start_page
        elif end_page is not None:
            pages_to_extract = reader.pages[:end_page + 1]
            actual_start = 0
        else:
            pages_to_extract = reader.pages
            actual_start = 0
        
        # 提取文本
        extracted_text = ""
        for i, page in enumerate(pages_to_extract):
            page_text = page.extract_text()
            if page_text.strip():
                extracted_text += f"\n--- Page {actual_start + i + 1} ---\n"
                extracted_text += page_text
                extracted_text += "\n"
        
        word_count = len(extracted_text.split())
        char_count = len(extracted_text)
        
        return {
            'success': True,
            'pdf_path': pdf_path,
            'total_pages': total_pages,
            'extracted_pages': len(pages_to_extract),
            'word_count': word_count,
            'character_count': char_count,
            'text_content': extracted_text.strip()
        }
        
    except Exception as e:
        error_msg = f"Error extracting PDF text: {str(e)}"
        debug_print(error_msg, debug)
        return {
            'success': False,
            'error': error_msg,
            'pdf_path': pdf_path
        }


async def convert_pdf_to_text(
    pdf_path: str,
    output_path: Optional[str] = None,
    start_page: Optional[int] = None,
    end_page: Optional[int] = None,
    include_page_numbers: bool = True,
    encoding: str = "utf-8",
    debug: bool = Config.DEBUG_MODE
) -> Dict[str, Any]:
    """Convert PDF file to plain text file.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path for output text file (optional)
        start_page: Start page number (0-indexed, optional)
        end_page: End page number (0-indexed, optional)
        include_page_numbers: Include page number markers
        encoding: Text file encoding
        debug: Enable debug output
    
    Returns:
        Dictionary containing conversion result
    """
    debug_print(f"Converting PDF to text: {pdf_path}", debug)
    
    if not PDF_READER_AVAILABLE:
        return {
            'success': False,
            'error': 'PDF processing unavailable. Install pypdf: pip install pypdf'
        }
    
    try:
        if not os.path.exists(pdf_path):
            return {
                'success': False,
                'error': f'PDF file not found: {pdf_path}'
            }
        
        # 设置输出路径
        if not output_path:
            pdf_file = Path(pdf_path)
            output_file_path = pdf_file.with_suffix('.txt')
        else:
            output_file_path = Path(output_path)
        
        # 确保输出目录存在
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        
        # 确定页面范围
        if start_page is not None and end_page is not None:
            pages_to_extract = reader.pages[start_page:end_page + 1]
            actual_start = start_page
        elif start_page is not None:
            pages_to_extract = reader.pages[start_page:]
            actual_start = start_page
        elif end_page is not None:
            pages_to_extract = reader.pages[:end_page + 1]
            actual_start = 0
        else:
            pages_to_extract = reader.pages
            actual_start = 0
        
        # 提取文本
        extracted_text = ""
        for i, page in enumerate(pages_to_extract):
            page_text = page.extract_text()
            if page_text.strip():
                if include_page_numbers:
                    extracted_text += f"\n--- Page {actual_start + i + 1} ---\n"
                extracted_text += page_text
                extracted_text += "\n"
        
        # 写入文本文件
        with open(output_file_path, 'w', encoding=encoding) as f:
            f.write(extracted_text.strip())
        
        word_count = len(extracted_text.split())
        char_count = len(extracted_text)
        file_size = os.path.getsize(output_file_path)
        
        return {
            'success': True,
            'pdf_path': pdf_path,
            'output_path': str(output_file_path),
            'total_pages': total_pages,
            'extracted_pages': len(pages_to_extract),
            'word_count': word_count,
            'character_count': char_count,
            'output_file_size_bytes': file_size,
            'encoding': encoding,
            'include_page_numbers': include_page_numbers
        }
        
    except Exception as e:
        error_msg = f"Error converting PDF to text: {str(e)}"
        debug_print(error_msg, debug)
        return {
            'success': False,
            'error': error_msg,
            'pdf_path': pdf_path
        }


async def process_arxiv_paper(
    arxiv_id: str,
    download_dir: str = "./downloads",
    extract_text: bool = True,
    save_text_file: bool = True,
    debug: bool = Config.DEBUG_MODE
) -> Dict[str, Any]:
    """One-stop ArXiv paper processing: download PDF and optionally extract text.
    
    Args:
        arxiv_id: ArXiv paper ID
        download_dir: Directory to save files
        extract_text: Whether to extract text from PDF
        save_text_file: Whether to save extracted text to file
        debug: Enable debug output
    
    Returns:
        Dictionary containing processing results
    """
    debug_print(f"Processing ArXiv paper: {arxiv_id}", debug)
    
    try:
        # Step 1: Download PDF
        download_result = await download_arxiv_pdf(
            arxiv_id=arxiv_id,
            download_dir=download_dir,
            debug=debug
        )
        
        if not download_result.get('success'):
            return download_result
        
        pdf_path = download_result['local_path']
        result = {
            'success': True,
            'arxiv_id': arxiv_id,
            'pdf_downloaded': True,
            'pdf_path': pdf_path,
            'pdf_size_mb': download_result['file_size_mb']
        }
        
        # Step 2: Extract text if requested
        if extract_text and PDF_READER_AVAILABLE:
            text_result = await extract_pdf_text(pdf_path=pdf_path, debug=debug)
            
            if text_result.get('success'):
                result.update({
                    'text_extracted': True,
                    'total_pages': text_result['total_pages'],
                    'word_count': text_result['word_count'],
                    'character_count': text_result['character_count']
                })
                
                # Step 3: Save text file if requested
                if save_text_file:
                    text_file_path = Path(pdf_path).with_suffix('.txt')
                    convert_result = await convert_pdf_to_text(
                        pdf_path=pdf_path,
                        output_path=str(text_file_path),
                        debug=debug
                    )
                    
                    if convert_result.get('success'):
                        result.update({
                            'text_file_saved': True,
                            'text_file_path': convert_result['output_path'],
                            'text_file_size_bytes': convert_result['output_file_size_bytes']
                        })
                    else:
                        result['text_file_saved'] = False
                        result['text_save_error'] = convert_result.get('error')
                else:
                    result['text_content'] = text_result['text_content']
            else:
                result['text_extracted'] = False
                result['text_extraction_error'] = text_result.get('error')
        elif extract_text and not PDF_READER_AVAILABLE:
            result['text_extracted'] = False
            result['text_extraction_error'] = 'PDF processing unavailable. Install pypdf: pip install pypdf'
        
        return result
        
    except Exception as e:
        error_msg = f"Error processing ArXiv paper: {str(e)}"
        debug_print(error_msg, debug)
        return {
            'success': False,
            'error': error_msg,
            'arxiv_id': arxiv_id
        }