"""
Internet learning module for hot learning with real search engine integration.
"""
import requests
from typing import List, Dict, Optional, Any
import json
import hashlib
from datetime import datetime
import urllib.parse
import re

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


class InternetLearner:
    """Fetches and processes knowledge from the internet using multiple search engines."""
    
    def __init__(self, brain=None):
        """Initialize internet learner.
        
        Args:
            brain: Brain instance for storing learned knowledge
        """
        self.brain = brain
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.search_engines = ['duckduckgo', 'wikipedia']
        
    def search_and_learn(self, query: str, topic: str) -> Dict[str, Any]:
        """Search for knowledge and learn from results using multiple search engines.
        
        Args:
            query: Search query
            topic: Topic to categorize knowledge
            
        Returns:
            Dictionary with learned knowledge
        """
        # Extract core topic from natural language queries
        clean_topic = self._extract_core_topic(topic)
        
        knowledge = {
            'query': query,
            'topic': clean_topic,
            'sources': [],
            'facts': [],
            'steps': [],
            'reliability': 0.0,
            'summary': ''  # Add summary field for comprehensive answer
        }
        
        # Try DuckDuckGo first (no API key needed, instant answers)
        # Use clean_topic for better search results
        ddg_result = self._search_duckduckgo(clean_topic, clean_topic)
        if ddg_result and ddg_result['facts']:
            knowledge['sources'].append(ddg_result['source'])
            knowledge['facts'].extend(ddg_result['facts'])
            knowledge['steps'].extend(ddg_result['steps'])
            knowledge['reliability'] = max(knowledge['reliability'], ddg_result['reliability'])
        
        # Then try Wikipedia as a reliable source
        wikipedia_result = self._search_wikipedia(clean_topic)
        if wikipedia_result and wikipedia_result['facts']:
            # Avoid duplicates
            new_facts = [f for f in wikipedia_result['facts'] if f not in knowledge['facts']]
            if new_facts:
                knowledge['sources'].append(wikipedia_result['source'])
                knowledge['facts'].extend(new_facts[:5])  # Limit to 5 more facts
                knowledge['steps'].extend(wikipedia_result['steps'])
                # Weighted average with more weight on higher reliability
                if knowledge['reliability'] > 0:
                    # Weighted average favoring higher scores
                    knowledge['reliability'] = (knowledge['reliability'] * 0.4 + wikipedia_result['reliability'] * 0.6)
                else:
                    knowledge['reliability'] = wikipedia_result['reliability']
        
        # If both fail, use built-in knowledge base
        if not knowledge['facts']:
            builtin_knowledge = self._get_builtin_knowledge(clean_topic)
            if builtin_knowledge:
                knowledge['sources'].append(builtin_knowledge['source'])
                knowledge['facts'].extend(builtin_knowledge['facts'])
                knowledge['steps'].extend(builtin_knowledge['steps'])
                knowledge['reliability'] = builtin_knowledge['reliability']
        
        # Store in brain if available with proper confidence scores
        if self.brain and knowledge['facts']:
            # Use reliability as confidence for better scoring
            confidence = min(knowledge['reliability'], 0.95)  # Cap at 0.95 to allow for improvement
            for fact in knowledge['facts']:
                self.brain.learn_fact(
                    topic=clean_topic,
                    fact=fact,
                    confidence=confidence,  # Pass reliability as confidence
                    source_type='internet',
                    reliability=knowledge['reliability']
                )
        
        # Generate comprehensive summary
        if knowledge['facts']:
            # Take first 3 facts as summary
            top_facts = knowledge['facts'][:3]
            knowledge['summary'] = ' '.join(top_facts)
                
        return knowledge
    
    def _extract_core_topic(self, topic: str) -> str:
        """Extract core topic from natural language input.
        
        Args:
            topic: Raw topic string (may include conversational text)
            
        Returns:
            Clean core topic
        """
        # Remove common conversational phrases
        stop_phrases = [
            ' and i ', ' i want to ', ' i need to ', ' how to ', ' how do i ',
            ' tell me about ', ' what is ', ' what are ', ' explain ',
            ' make code in ', ' write code in ', ' program in ', ' code in ',
            ' learn about ', ' tutorial for ', ' guide to ', ' and ', ' in '
        ]
        
        topic_lower = ' ' + topic.lower() + ' '  # Add spaces for boundary matching
        for phrase in stop_phrases:
            topic_lower = topic_lower.replace(phrase, ' ')
        
        topic_lower = topic_lower.strip()
        
        # Common multi-word topics (check these first)
        multi_word_topics = [
            'machine learning', 'deep learning', 'data science', 'artificial intelligence',
            'web development', 'mobile development', 'software engineering', 'computer science',
            'natural language processing', 'computer vision'
        ]
        
        for multi_word in multi_word_topics:
            if multi_word in topic_lower:
                return multi_word
        
        # Common programming languages and technologies
        single_word_topics = [
            'javascript', 'typescript', 'python', 'java', 'c++', 'c#', 'ruby',
            'php', 'swift', 'kotlin', 'golang', 'rust', 'scala', 'perl',
            'html', 'css', 'sql', 'bash', 'shell', 'react', 'angular', 'vue',
            'node', 'nodejs', 'django', 'flask', 'spring', 'docker', 'kubernetes',
            'git', 'linux', 'windows', 'macos', 'android', 'ios', 'web', 'mobile'
        ]
        
        # Check for single word topics (prioritize longer matches first)
        sorted_topics = sorted(single_word_topics, key=len, reverse=True)
        for known in sorted_topics:
            if known in topic_lower:
                return known
        
        # If no known topic found, return first meaningful word (not stop word)
        words = topic_lower.split()
        stop_words = ['and', 'the', 'a', 'an', 'to', 'of', 'for', 'on', 'with', 'as', 'by', 'i']
        for word in words:
            word = word.strip()
            if word and word not in stop_words and len(word) > 2:
                return word
        
        # Fallback to original topic
        return topic.strip()
    
    def _search_duckduckgo(self, query: str, topic: str) -> Optional[Dict[str, Any]]:
        """Search DuckDuckGo for instant answers and web results.
        
        Args:
            query: Search query
            topic: Topic for categorization
            
        Returns:
            Dictionary with extracted knowledge or None
        """
        try:
            # Use DuckDuckGo Instant Answer API (no API key needed)
            api_url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
            
            response = self.session.get(api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                result = {
                    'source': {
                        'title': f'DuckDuckGo: {query}',
                        'url': f'https://duckduckgo.com/?q={urllib.parse.quote(query)}',
                        'reliability': 0.90  # Increased for better instant answers
                    },
                    'facts': [],
                    'steps': [],
                    'reliability': 0.90  # Increased base reliability
                }
                
                # Extract abstract (main answer)
                abstract = data.get('Abstract', '').strip()
                if abstract and len(abstract) > 20:
                    # Split into sentences
                    sentences = re.split(r'(?<=[.!?])\s+', abstract)
                    result['facts'].extend([s.strip() for s in sentences if len(s.strip()) > 20][:5])
                
                # Extract answer (direct answer)
                answer = data.get('Answer', '').strip()
                if answer and len(answer) > 20:
                    # Remove HTML tags if any
                    answer_clean = re.sub(r'<[^>]+>', '', answer)
                    if answer_clean not in result['facts']:
                        result['facts'].insert(0, answer_clean)
                
                # Extract definition
                definition = data.get('Definition', '').strip()
                if definition and len(definition) > 20:
                    if definition not in result['facts']:
                        result['facts'].insert(0, f"{topic}: {definition}")
                
                # Extract related topics as additional facts
                related = data.get('RelatedTopics', [])
                for item in related[:3]:  # Limit to 3
                    if isinstance(item, dict) and 'Text' in item:
                        text = item['Text'].strip()
                        if text and len(text) > 20 and text not in result['facts']:
                            result['facts'].append(text)
                
                return result if result['facts'] else None
                
        except Exception as e:
            return None
        
        return None
    
    def _search_web_scrape(self, query: str, topic: str) -> Optional[Dict[str, Any]]:
        """Search web and scrape results (fallback method).
        
        Args:
            query: Search query
            topic: Topic for categorization
            
        Returns:
            Dictionary with extracted knowledge or None
        """
        if not BS4_AVAILABLE:
            return None
            
        try:
            # Use DuckDuckGo HTML search (no JavaScript needed)
            search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                result = {
                    'source': {
                        'title': f'Web Search: {query}',
                        'url': search_url,
                        'reliability': 0.75
                    },
                    'facts': [],
                    'steps': [],
                    'reliability': 0.75
                }
                
                # Extract search result snippets
                results = soup.find_all('a', class_='result__snippet')
                for snippet in results[:5]:  # First 5 results
                    text = snippet.get_text(strip=True)
                    if text and len(text) > 30:
                        result['facts'].append(text)
                
                return result if result['facts'] else None
                
        except Exception as e:
            return None
        
        return None
    
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
                        'reliability': 0.95  # Wikipedia is highly reliable for factual content
                    },
                    'facts': [],
                    'steps': [],
                    'reliability': 0.95  # Increased for verified encyclopedic content
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
            },
            'java': {
                'facts': [
                    'Java: a high-level, class-based, object-oriented programming language',
                    'Java was originally developed by James Gosling at Sun Microsystems (now Oracle)',
                    'Java follows the "write once, run anywhere" (WORA) principle via the JVM',
                    'Java is widely used for enterprise applications, Android apps, and web services',
                    'Java has automatic memory management through garbage collection',
                    'Java is strongly typed and uses compiled bytecode for platform independence'
                ],
                'steps': [
                    'Install JDK (Java Development Kit) from Oracle or OpenJDK',
                    'Write code in .java files',
                    'Compile with: javac YourClass.java',
                    'Run with: java YourClass',
                    'Use Maven or Gradle for dependency management'
                ]
            },
            'c++': {
                'facts': [
                    'C++: a high-performance, general-purpose programming language',
                    'C++ is an extension of C with object-oriented features',
                    'C++ provides low-level memory manipulation and high-level abstractions',
                    'C++ is widely used for system software, game engines, and performance-critical applications',
                    'C++ supports multiple programming paradigms including procedural, object-oriented, and generic'
                ],
                'steps': [
                    'Install compiler (g++, clang, or MSVC)',
                    'Write code in .cpp files',
                    'Compile with: g++ -o program program.cpp',
                    'Run with: ./program',
                    'Use CMake for build management'
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
                    'reliability': 0.88  # Increased for curated high-quality content
                },
                'facts': kb_data['facts'],
                'steps': kb_data.get('steps', []),
                'reliability': 0.88  # Curated knowledge is reliable
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
