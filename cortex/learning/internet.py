"""
Internet learning module for hot learning.
"""
import requests
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup
import json
import hashlib
from datetime import datetime


class InternetLearner:
    """Fetches and processes knowledge from the internet."""
    
    def __init__(self, brain=None):
        """Initialize internet learner.
        
        Args:
            brain: Brain instance for storing learned knowledge
        """
        self.brain = brain
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Cortex/0.1.0 (Learning Agent)'
        })
        
    def search_and_learn(self, query: str, topic: str) -> Dict[str, Any]:
        """Search for knowledge and learn from results.
        
        Args:
            query: Search query
            topic: Topic to categorize knowledge
            
        Returns:
            Dictionary with learned knowledge
        """
        # Simulate search (in production, use real search API)
        results = self._mock_search(query)
        
        knowledge = {
            'query': query,
            'topic': topic,
            'sources': [],
            'facts': [],
            'steps': [],
            'reliability': 0.0
        }
        
        for result in results[:3]:  # Process top 3 results
            try:
                content = self._fetch_content(result['url'])
                if content:
                    extracted = self._extract_knowledge(content, topic)
                    knowledge['sources'].append({
                        'url': result['url'],
                        'title': result['title'],
                        'reliability': extracted['reliability']
                    })
                    knowledge['facts'].extend(extracted['facts'])
                    knowledge['steps'].extend(extracted['steps'])
            except Exception as e:
                continue
                
        # Calculate overall reliability
        if knowledge['sources']:
            knowledge['reliability'] = sum(
                s['reliability'] for s in knowledge['sources']
            ) / len(knowledge['sources'])
        
        # Store in brain if available
        if self.brain and knowledge['facts']:
            for fact in knowledge['facts']:
                self.brain.learn_fact(
                    topic=topic,
                    fact=fact,
                    source_type='internet',
                    reliability=knowledge['reliability']
                )
                
        return knowledge
        
    def _mock_search(self, query: str) -> List[Dict]:
        """Mock search results (replace with real search API).
        
        Args:
            query: Search query
            
        Returns:
            List of search results
        """
        # In production, integrate with real search API
        return [
            {
                'title': f'Documentation for {query}',
                'url': f'https://docs.example.com/{query.replace(" ", "-")}',
                'snippet': 'Official documentation...'
            },
            {
                'title': f'Tutorial: {query}',
                'url': f'https://tutorial.example.com/{query.replace(" ", "-")}',
                'snippet': 'Step-by-step guide...'
            },
            {
                'title': f'Best practices: {query}',
                'url': f'https://blog.example.com/{query.replace(" ", "-")}',
                'snippet': 'Best practices and tips...'
            }
        ]
        
    def _fetch_content(self, url: str, timeout: int = 10) -> Optional[str]:
        """Fetch content from URL.
        
        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            
        Returns:
            HTML content or None
        """
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            return None
            
    def _extract_knowledge(self, html: str, topic: str) -> Dict[str, Any]:
        """Extract knowledge from HTML content.
        
        Args:
            html: HTML content
            topic: Topic for categorization
            
        Returns:
            Extracted knowledge
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        knowledge = {
            'facts': [],
            'steps': [],
            'reliability': 0.7  # Base reliability
        }
        
        # Extract paragraphs as facts
        paragraphs = soup.find_all('p')
        for p in paragraphs[:5]:  # Limit to first 5 paragraphs
            text = p.get_text(strip=True)
            if len(text) > 20:  # Minimum length
                knowledge['facts'].append(text[:200])  # Limit length
                
        # Extract ordered lists as steps
        ordered_lists = soup.find_all('ol')
        for ol in ordered_lists[:2]:  # Limit to first 2 lists
            steps = [li.get_text(strip=True) for li in ol.find_all('li')]
            knowledge['steps'].extend(steps[:10])  # Limit steps
            
        # Adjust reliability based on content quality
        if len(knowledge['facts']) > 3:
            knowledge['reliability'] += 0.1
        if len(knowledge['steps']) > 0:
            knowledge['reliability'] += 0.1
            
        knowledge['reliability'] = min(knowledge['reliability'], 0.95)
        
        return knowledge
        
    def learn_from_docs(self, doc_url: str, topic: str) -> Dict[str, Any]:
        """Learn from documentation URL.
        
        Args:
            doc_url: Documentation URL
            topic: Topic to categorize
            
        Returns:
            Learned knowledge
        """
        content = self._fetch_content(doc_url)
        if not content:
            return {'error': 'Failed to fetch documentation'}
            
        extracted = self._extract_knowledge(content, topic)
        
        # Store in brain
        if self.brain and extracted['facts']:
            for fact in extracted['facts']:
                self.brain.learn_fact(
                    topic=topic,
                    fact=fact,
                    source=doc_url,
                    source_type='internet',
                    reliability=extracted['reliability']
                )
                
        return {
            'topic': topic,
            'source': doc_url,
            'facts_learned': len(extracted['facts']),
            'steps_learned': len(extracted['steps']),
            'reliability': extracted['reliability']
        }


class DocumentParser:
    """Parses documents for knowledge extraction."""
    
    @staticmethod
    def parse_markdown(content: str) -> Dict[str, Any]:
        """Parse markdown content.
        
        Args:
            content: Markdown content
            
        Returns:
            Parsed knowledge
        """
        lines = content.split('\n')
        knowledge = {
            'headings': [],
            'code_blocks': [],
            'lists': [],
            'paragraphs': []
        }
        
        current_block = []
        in_code_block = False
        
        for line in lines:
            line = line.strip()
            
            # Code blocks
            if line.startswith('```'):
                if in_code_block:
                    knowledge['code_blocks'].append('\n'.join(current_block))
                    current_block = []
                in_code_block = not in_code_block
                continue
                
            if in_code_block:
                current_block.append(line)
                continue
                
            # Headings
            if line.startswith('#'):
                knowledge['headings'].append(line.lstrip('#').strip())
            # Lists
            elif line.startswith(('-', '*', '+')):
                knowledge['lists'].append(line.lstrip('-*+ ').strip())
            # Paragraphs
            elif line and not line.startswith(('```', '#', '-', '*', '+')):
                knowledge['paragraphs'].append(line)
                
        return knowledge
        
    @staticmethod
    def parse_pdf(file_path: str) -> Dict[str, Any]:
        """Parse PDF document.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Parsed knowledge
        """
        try:
            from pypdf import PdfReader
            
            reader = PdfReader(file_path)
            knowledge = {
                'page_count': len(reader.pages),
                'text': [],
                'metadata': reader.metadata
            }
            
            for page in reader.pages[:10]:  # Limit to first 10 pages
                text = page.extract_text()
                if text:
                    knowledge['text'].append(text)
                    
            return knowledge
        except Exception as e:
            return {'error': str(e)}
            
    @staticmethod
    def extract_code_patterns(code: str, language: str = 'python') -> List[str]:
        """Extract patterns from code.
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            List of identified patterns
        """
        patterns = []
        
        # Simple pattern detection (can be enhanced)
        if 'def ' in code or 'function ' in code:
            patterns.append('function_definition')
        if 'class ' in code:
            patterns.append('class_definition')
        if 'import ' in code or 'require(' in code:
            patterns.append('module_import')
        if 'if ' in code:
            patterns.append('conditional_logic')
        if 'for ' in code or 'while ' in code:
            patterns.append('iteration')
            
        return patterns
