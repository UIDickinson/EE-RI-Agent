from typing import Dict, Any, List
import logging
from .base_provider import BaseProvider, ProviderError
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class PaperProvider(BaseProvider):
    """
    Academic paper search provider
    
    Sources:
    - arXiv (primary)
    - IEEE Xplore (requires API key)
    - Google Scholar (fallback)
    """
    
    def __init__(self):
        super().__init__("PaperProvider")
        self.arxiv_api = "http://export.arxiv.org/api/query"
        self.max_results = 20
    
    async def fetch(self, query: str, max_results: int = None) -> Dict[str, Any]:
        """
        Fetch papers from arXiv and other sources
        """
        max_results = max_results or self.max_results
        
        try:
            logger.info(f"Searching papers for: {query}")
            
            # Search arXiv
            arxiv_papers = await self._search_arxiv(query, max_results)
            
            # TODO: Add IEEE Xplore if API key available
            # ieee_papers = await self._search_ieee(query, max_results)
            
            # Combine and deduplicate
            all_papers = arxiv_papers
            
            return self._create_response(
                success=True,
                data={
                    "papers": all_papers,
                    "count": len(all_papers),
                    "sources": ["arXiv"]
                },
                metadata={
                    "query": query,
                    "max_results": max_results
                }
            )
        
        except Exception as e:
            logger.error(f"Paper search error: {str(e)}")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    async def _search_arxiv(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search arXiv for papers"""
        try:
            # Build arXiv query
            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": max_results,
                "sortBy": "relevance",
                "sortOrder": "descending"
            }
            
            response = await self._make_request(self.arxiv_api, params=params)
            
            # Parse XML response
            papers = self._parse_arxiv_xml(response.text)
            
            logger.info(f"Found {len(papers)} papers on arXiv")
            return papers
        
        except Exception as e:
            logger.error(f"arXiv search error: {str(e)}")
            return []
    
    def _parse_arxiv_xml(self, xml_text: str) -> List[Dict[str, Any]]:
        """Parse arXiv XML response"""
        papers = []
        
        try:
            root = ET.fromstring(xml_text)
            
            # arXiv uses Atom namespace
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns):
                paper = {
                    "title": self._get_text(entry, 'atom:title', ns),
                    "authors": [
                        author.find('atom:name', ns).text
                        for author in entry.findall('atom:author', ns)
                    ],
                    "abstract": self._get_text(entry, 'atom:summary', ns),
                    "url": self._get_text(entry, 'atom:id', ns),
                    "published": self._get_text(entry, 'atom:published', ns)[:4],  # Year
                    "source": "arXiv"
                }
                
                # Extract year
                try:
                    paper["year"] = int(paper["published"])
                except:
                    paper["year"] = None
                
                papers.append(paper)
        
        except ET.ParseError as e:
            logger.error(f"XML parse error: {str(e)}")
        
        return papers
    
    def _get_text(self, element, path: str, namespace: dict) -> str:
        """Safely extract text from XML element"""
        try:
            elem = element.find(path, namespace)
            return elem.text.strip() if elem is not None and elem.text else ""
        except:
            return ""
    
    def validate_response(self, response: Any) -> bool:
        """Validate paper response"""
        if not isinstance(response, dict):
            return False
        return "papers" in response.get("data", {})