"""
Internet learning module for hot learning.
"""
import requests
from typing import List, Dict, Optional, Any
import json
import hashlib
from datetime import datetime

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


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
        knowledge = {
            'query': query,
            'topic': topic,
            'sources': [],
            'facts': [],
            'steps': [],
            'reliability': 0.0
        }
        
        # Try to use Wikipedia as a reliable source
        wikipedia_result = self._search_wikipedia(topic)
        if wikipedia_result:
            knowledge['sources'].append(wikipedia_result['source'])
            knowledge['facts'].extend(wikipedia_result['facts'])
            knowledge['steps'].extend(wikipedia_result['steps'])
            knowledge['reliability'] = wikipedia_result['reliability']
        
        # If Wikipedia fails, use built-in knowledge base
        if not knowledge['facts']:
            builtin_knowledge = self._get_builtin_knowledge(topic)
            if builtin_knowledge:
                knowledge['sources'].append(builtin_knowledge['source'])
                knowledge['facts'].extend(builtin_knowledge['facts'])
                knowledge['steps'].extend(builtin_knowledge['steps'])
                knowledge['reliability'] = builtin_knowledge['reliability']
        
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
    
    def _search_wikipedia(self, topic: str) -> Optional[Dict[str, Any]]:
        """Search Wikipedia for topic information.
        
        Args:
            topic: Topic to search for
            
        Returns:
            Dictionary with extracted knowledge or None
        """
        try:
            # Use Wikipedia API
            api_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
            clean_topic = topic.replace(" ", "_")
            response = self.session.get(f"{api_url}{clean_topic}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                result = {
                    'source': {
                        'title': data.get('title', topic),
                        'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                        'reliability': 0.9  # Wikipedia is generally reliable
                    },
                    'facts': [],
                    'steps': [],
                    'reliability': 0.9
                }
                
                # Extract summary as facts
                extract = data.get('extract', '')
                if extract:
                    # Split into sentences
                    sentences = extract.replace('. ', '.|').split('|')
                    result['facts'] = [s.strip() + '.' for s in sentences if len(s.strip()) > 20][:5]
                
                # Add description if available
                description = data.get('description', '')
                if description:
                    result['facts'].insert(0, f"{topic}: {description}")
                
                return result if result['facts'] else None
                
        except Exception as e:
            return None
        
        return None
    
    def _get_builtin_knowledge(self, topic: str) -> Optional[Dict[str, Any]]:
        """Get built-in knowledge about common topics.
        
        Args:
            topic: Topic to get knowledge about
            
        Returns:
            Dictionary with knowledge or None
        """
        # Knowledge base for common topics
        knowledge_base = {
            'python': {
                'facts': [
                    'Python: a high-level, interpreted programming language',
                    'Python emphasizes code readability with significant indentation',
                    'Python supports multiple programming paradigms including procedural, object-oriented, and functional',
                    'Python was created by Guido van Rossum and first released in 1991',
                    'Python has a comprehensive standard library often described as having "batteries included"'
                ],
                'steps': [
                    'Install Python from python.org',
                    'Write code in .py files',
                    'Run with: python filename.py',
                    'Use pip for package management'
                ]
            },
            'python3': {
                'facts': [
                    'Python 3: the current major version of Python, released in 2008',
                    'Python 3 is not fully backward compatible with Python 2',
                    'Python 3 includes improved Unicode support and better syntax',
                    'Python 3 uses print as a function: print() instead of print statement',
                    'Python 3.12 is the latest stable release with performance improvements'
                ],
                'steps': [
                    'Check version: python3 --version',
                    'Run scripts: python3 script.py',
                    'Install packages: pip3 install package_name',
                    'Create virtual environment: python3 -m venv env'
                ]
            },
            'node': {
                'facts': [
                    'Node.js: a JavaScript runtime built on Chrome\'s V8 engine',
                    'Node.js enables JavaScript to run on the server-side',
                    'Node.js uses an event-driven, non-blocking I/O model',
                    'Node.js has a large ecosystem via npm (Node Package Manager)',
                    'Node.js was created by Ryan Dahl in 2009'
                ],
                'steps': [
                    'Install Node.js from nodejs.org',
                    'Check version: node --version',
                    'Run JavaScript: node script.js',
                    'Manage packages with npm or yarn'
                ]
            },
            'javascript': {
                'facts': [
                    'JavaScript: a high-level, dynamic programming language',
                    'JavaScript is one of the core technologies of the web alongside HTML and CSS',
                    'JavaScript conforms to the ECMAScript specification',
                    'JavaScript supports event-driven, functional, and imperative programming',
                    'JavaScript can run in browsers and server-side via Node.js'
                ],
                'steps': []
            },
            'git': {
                'facts': [
                    'Git: a distributed version control system',
                    'Git was created by Linus Torvalds in 2005',
                    'Git tracks changes in source code during software development',
                    'Git enables multiple developers to work on the same project',
                    'Git is the most widely used version control system'
                ],
                'steps': [
                    'Initialize: git init',
                    'Stage changes: git add <file>',
                    'Commit: git commit -m "message"',
                    'Push to remote: git push origin main'
                ]
            }
        }
        
        # Normalize topic for lookup
        topic_key = topic.lower().strip()
        
        if topic_key in knowledge_base:
            kb_data = knowledge_base[topic_key]
            return {
                'source': {
                    'title': f'Built-in Knowledge: {topic}',
                    'url': 'cortex://builtin-knowledge',
                    'reliability': 0.8
                },
                'facts': kb_data['facts'],
                'steps': kb_data.get('steps', []),
                'reliability': 0.8
            }
        
        # Generic response for unknown topics
        return {
            'source': {
                'title': f'General Knowledge: {topic}',
                'url': 'cortex://general-knowledge',
                'reliability': 0.5
            },
            'facts': [
                f'{topic} is a topic that you want to learn about',
                f'Consider researching {topic} through official documentation',
                f'Try: cortex research "{topic} tutorial" {topic}'
            ],
            'steps': [
                f'Search for "{topic}" online',
                'Read official documentation',
                'Try practical examples',
                'Practice regularly'
            ],
            'reliability': 0.5
        }
        
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
        if not BS4_AVAILABLE:
            return {
                'facts': [],
                'steps': [],
                'reliability': 0.0
            }
            
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
