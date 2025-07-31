"""Paper management functionality for organizing and saving papers."""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from models import ArxivPaper, SemanticScholarPaper
from config import Config
from utils import debug_print, sanitize_filename, format_authors, save_json_to_file


class PaperManager:
    """Manages paper storage, organization, and literature review generation."""
    
    def __init__(self, debug: bool = Config.DEBUG_MODE):
        self.debug = debug
        self.papers_dir = Config.PAPERS_DIR
        self.md_files_dir = Config.MD_FILES_DIR
        
        # Ensure directories exist
        self._ensure_directory_structure()
    
    def _ensure_directory_structure(self) -> None:
        """Create the basic directory structure for organizing papers."""
        # Create main directories
        for directory in [self.papers_dir, self.md_files_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_paper_to_markdown(
        self, 
        paper: SemanticScholarPaper, 
        topic: str = "general", 
        notes: str = ""
    ) -> str:
        """Save a paper to markdown format in the specified topic directory."""
        debug_print(f"Saving paper to markdown: {paper.title}", self.debug)
        
        # Create topic directory if it doesn't exist
        topic_dir = self.md_files_dir / topic
        topic_dir.mkdir(parents=True, exist_ok=True)
        
        # Sanitize filename
        filename = sanitize_filename(paper.title[:100]) + ".md"
        filepath = topic_dir / filename
        
        # Create markdown content
        content = self._generate_paper_markdown(paper, notes)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        debug_print(f"Paper saved to: {filepath}", self.debug)
        return str(filepath)
    
    def save_arxiv_paper_to_markdown(
        self, 
        paper: ArxivPaper, 
        topic: str = "general", 
        notes: str = ""
    ) -> str:
        """Save an ArXiv paper to markdown format."""
        debug_print(f"Saving ArXiv paper to markdown: {paper.title}", self.debug)
        
        # Create topic directory if it doesn't exist
        topic_dir = self.md_files_dir / topic
        topic_dir.mkdir(parents=True, exist_ok=True)
        
        # Sanitize filename
        filename = sanitize_filename(paper.title[:100]) + ".md"
        filepath = topic_dir / filename
        
        # Create markdown content
        content = self._generate_arxiv_paper_markdown(paper, notes)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        debug_print(f"ArXiv paper saved to: {filepath}", self.debug)
        return str(filepath)
    
    def organize_papers_by_topic(self) -> Dict[str, List[str]]:
        """List all papers organized by topic."""
        debug_print("Organizing papers by topic", self.debug)
        
        organized_papers = {}
        
        for topic_dir in self.md_files_dir.iterdir():
            if topic_dir.is_dir():
                topic_name = topic_dir.name
                papers = []
                
                for paper_file in topic_dir.glob('*.md'):
                    papers.append(paper_file.name)
                
                organized_papers[topic_name] = papers
        
        return organized_papers
    
    def generate_literature_review(
        self, 
        topic: str, 
        requirements: List[str],
        output_filename: Optional[str] = None
    ) -> str:
        """Generate a literature review for papers in a specific topic."""
        debug_print(f"Generating literature review for topic: {topic}", self.debug)
        
        topic_dir = self.md_files_dir / topic
        if not topic_dir.exists():
            # Create the topic directory if it doesn't exist
            topic_dir.mkdir(parents=True, exist_ok=True)
            return f"Topic directory '{topic}' was created but contains no papers yet."
        
        # Read all papers in the topic
        papers_content = []
        for paper_file in topic_dir.glob('*.md'):
            with open(paper_file, 'r', encoding='utf-8') as f:
                content = f.read()
                papers_content.append({
                    'filename': paper_file.name,
                    'content': content
                })
        
        if not papers_content:
            return f"No papers found in topic '{topic}'."
        
        # Generate review content
        review_content = self._generate_review_markdown(topic, requirements, papers_content)
        
        # Save review
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"literature_review_{topic}_{timestamp}.md"
        
        review_filepath = self.md_files_dir / output_filename
        with open(review_filepath, 'w', encoding='utf-8') as f:
            f.write(review_content)
        
        debug_print(f"Literature review saved to: {review_filepath}", self.debug)
        return str(review_filepath)
    
    def search_papers_by_keyword(self, keyword: str) -> List[Dict[str, str]]:
        """Search for papers containing a specific keyword."""
        debug_print(f"Searching papers by keyword: {keyword}", self.debug)
        
        matching_papers = []
        
        for topic_dir in self.md_files_dir.iterdir():
            if topic_dir.is_dir():
                for paper_file in topic_dir.glob('*.md'):
                    try:
                        with open(paper_file, 'r', encoding='utf-8') as f:
                            content = f.read().lower()
                            if keyword.lower() in content:
                                matching_papers.append({
                                    'topic': topic_dir.name,
                                    'filename': paper_file.name,
                                    'filepath': str(paper_file)
                                })
                    except Exception as e:
                        debug_print(f"Error reading file {paper_file}: {str(e)}", self.debug)
        
        return matching_papers
    
    def get_paper_statistics(self) -> Dict[str, Any]:
        """Get statistics about saved papers."""
        debug_print("Calculating paper statistics", self.debug)
        
        stats = {
            'total_papers': 0,
            'papers_by_topic': {},
            'topics': []
        }
        
        for topic_dir in self.md_files_dir.iterdir():
            if topic_dir.is_dir():
                topic_name = topic_dir.name
                paper_count = len(list(topic_dir.glob('*.md')))
                
                stats['papers_by_topic'][topic_name] = paper_count
                stats['total_papers'] += paper_count
                stats['topics'].append(topic_name)
        
        return stats
    
    def _generate_paper_markdown(self, paper: SemanticScholarPaper, notes: str = "") -> str:
        """Generate markdown content for a Semantic Scholar paper."""
        authors_str = format_authors(paper.authors)
        
        content = f"""# {paper.title}

## Metadata
- **Paper ID**: {paper.paper_id}
- **Authors**: {authors_str}
- **Year**: {paper.year or 'Unknown'}
- **Venue**: {paper.venue or 'Unknown'}
- **Citation Count**: {paper.citation_count}
- **Reference Count**: {paper.reference_count}
- **Influential Citations**: {paper.influential_citation_count}

## Links
"""
        
        if paper.url:
            content += f"- **Paper URL**: {paper.url}\n"
        
        if paper.arxiv_id:
            content += f"- **ArXiv**: https://arxiv.org/abs/{paper.arxiv_id}\n"
        
        if paper.doi:
            content += f"- **DOI**: https://doi.org/{paper.doi}\n"
        
        content += "\n## Abstract\n\n"
        
        if paper.abstract:
            content += paper.abstract
        else:
            content += "No abstract available."
        
        if paper.tldr and paper.tldr.get('text'):
            content += f"\n\n## TL;DR\n\n{paper.tldr['text']}"
        
        if notes:
            content += f"\n\n## Notes\n\n{notes}"
        
        content += f"\n\n## External IDs\n\n"
        if paper.external_ids:
            for key, value in paper.external_ids.items():
                content += f"- **{key}**: {value}\n"
        
        content += f"\n\n---\n*Saved on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        return content
    
    def _generate_arxiv_paper_markdown(self, paper: ArxivPaper, notes: str = "") -> str:
        """Generate markdown content for an ArXiv paper."""
        authors_str = ", ".join(paper.authors) if paper.authors else "Unknown"
        
        content = f"""# {paper.title}

## Metadata
- **ArXiv ID**: {paper.arxiv_id}
- **Authors**: {authors_str}
- **Published**: {paper.published_date}
- **Categories**: {', '.join(paper.categories) if paper.categories else 'Unknown'}

## Links
- **ArXiv**: https://arxiv.org/abs/{paper.arxiv_id}
- **PDF**: {paper.pdf_url}

## Abstract

{paper.abstract if paper.abstract else 'No abstract available.'}
"""
        
        if notes:
            content += f"\n\n## Notes\n\n{notes}"
        
        content += f"\n\n---\n*Saved on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        return content
    
    def _generate_review_markdown(
        self, 
        topic: str, 
        requirements: List[str], 
        papers_content: List[Dict[str, str]]
    ) -> str:
        """Generate literature review markdown content."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        content = f"""# Literature Review: {topic.title()}

*Generated on {timestamp}*

## Overview

This literature review covers {len(papers_content)} papers in the {topic} domain, organized according to the following requirements:

"""
        
        for i, req in enumerate(requirements, 1):
            content += f"{i}. {req}\n"
        
        content += "\n## Papers by Requirements\n\n"
        
        # Organize papers by requirements
        for i, requirement in enumerate(requirements, 1):
            content += f"### Requirement {i}: {requirement}\n\n"
            
            # Find papers that might match this requirement
            # This is a simple keyword-based matching - could be enhanced with NLP
            req_keywords = requirement.lower().split()
            matching_papers = []
            
            for paper in papers_content:
                paper_text = paper['content'].lower()
                if any(keyword in paper_text for keyword in req_keywords):
                    matching_papers.append(paper)
            
            if matching_papers:
                for paper in matching_papers:
                    # Extract title from markdown content
                    lines = paper['content'].split('\n')
                    title = lines[0].replace('# ', '') if lines else paper['filename']
                    
                    # Extract ArXiv link if available
                    arxiv_link = "Unknown"
                    for line in lines:
                        if 'arxiv.org/abs/' in line:
                            arxiv_link = line.split('](')[0].split('[')[-1] if '](' in line else line.strip()
                            break
                        elif '**ArXiv**:' in line:
                            arxiv_link = line.split('**ArXiv**: ')[-1].strip()
                            break
                    
                    # Extract key features (this could be enhanced)
                    key_features = "Advanced research in the field"
                    
                    # Extract technologies (simple keyword extraction)
                    tech_keywords = ['learning', 'neural', 'deep', 'machine', 'AI', 'algorithm', 'model']
                    found_tech = []
                    for line in lines:
                        for tech in tech_keywords:
                            if tech.lower() in line.lower() and tech not in found_tech:
                                found_tech.append(tech.title())
                    
                    technologies = ', '.join(found_tech[:3]) if found_tech else "Machine Learning"
                    
                    content += f"""#### {title}
- ArXiv链接: `{arxiv_link}`
- 关键特点: {key_features}
- 相关技术: {technologies}

"""
            else:
                content += "No papers found matching this requirement.\n\n"
        
        # Add summary section
        content += "## Summary\n\n"
        content += f"This review analyzed {len(papers_content)} papers across {len(requirements)} requirements. "
        content += "The papers demonstrate significant advances in the field and provide valuable insights for future research.\n\n"
        
        # Add all papers list
        content += "## All Papers Reviewed\n\n"
        for paper in papers_content:
            lines = paper['content'].split('\n')
            title = lines[0].replace('# ', '') if lines else paper['filename']
            content += f"- {title}\n"
        
        return content
    
    def create_requirement_based_review(
        self,
        papers: List[SemanticScholarPaper],
        requirements: List[str],
        output_filename: Optional[str] = None
    ) -> str:
        """Create a requirement-based literature review from a list of papers."""
        debug_print(f"Creating requirement-based review for {len(papers)} papers", self.debug)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if output_filename is None:
            timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"requirement_review_{timestamp_file}.md"
        
        content = f"""# Literature Review

*Generated on {timestamp}*

## Overview

This review analyzes {len(papers)} papers according to the specified requirements.

"""
        
        # Organize papers by requirements
        for i, requirement in enumerate(requirements, 1):
            content += f"## 需求{i}-相关\n\n"
            
            # Simple keyword matching - could be enhanced
            req_keywords = requirement.lower().split()
            matching_papers = []
            
            for paper in papers:
                paper_text = f"{paper.title} {paper.abstract or ''}".lower()
                if any(keyword in paper_text for keyword in req_keywords):
                    matching_papers.append(paper)
            
            for paper in matching_papers:
                arxiv_link = f"https://arxiv.org/abs/{paper.arxiv_id}" if paper.arxiv_id else paper.url or "Unknown"
                
                # Extract key features from abstract
                key_features = paper.abstract[:100] + "..." if paper.abstract else "Advanced research methodology"
                
                # Extract technologies (simple approach)
                technologies = "Machine Learning, Deep Learning"
                if paper.abstract:
                    if 'reinforcement' in paper.abstract.lower():
                        technologies = "Reinforcement Learning, " + technologies
                    if 'nlp' in paper.abstract.lower() or 'language' in paper.abstract.lower():
                        technologies = "NLP, " + technologies
                
                content += f"""### {paper.title}
- ArXiv链接: `{arxiv_link}`
- 关键特点: {key_features}
- 相关技术: {technologies}

"""
        
        # Add intersection section if multiple requirements
        if len(requirements) > 1:
            content += f"## 需求1 & 需求2 都相关的论文\n\n"
            # Find papers that match multiple requirements
            multi_match_papers = []
            for paper in papers:
                paper_text = f"{paper.title} {paper.abstract or ''}".lower()
                match_count = 0
                for requirement in requirements:
                    req_keywords = requirement.lower().split()
                    if any(keyword in paper_text for keyword in req_keywords):
                        match_count += 1
                
                if match_count >= 2:
                    multi_match_papers.append(paper)
            
            for paper in multi_match_papers:
                arxiv_link = f"https://arxiv.org/abs/{paper.arxiv_id}" if paper.arxiv_id else paper.url or "Unknown"
                key_features = paper.abstract[:100] + "..." if paper.abstract else "Comprehensive research approach"
                technologies = "Multi-domain Machine Learning"
                
                content += f"""### {paper.title}
- ArXiv链接: `{arxiv_link}`
- 关键特点: {key_features}
- 相关技术: {technologies}

"""
        
        # Save the review
        review_filepath = self.md_files_dir / output_filename
        with open(review_filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        debug_print(f"Requirement-based review saved to: {review_filepath}", self.debug)
        return str(review_filepath)