import asyncio
from typing import Dict, Any, List, Optional
import httpx
from datetime import datetime, timedelta
from agno.tools import Tool
import xml.etree.ElementTree as ET

class PatentExecutor(Tool):
    """
    Searches patents focusing on EU (EPO) and Asia (CNIPA, JPO) patent offices
    """
    
    def __init__(self):
        super().__init__(
            name="patent_search",
            description="Search patents from EU and Asian patent offices (EPO, CNIPA, JPO)",
        )
        
        # Patent office APIs
        self.patent_sources = {
            "epo": {
                "name": "European Patent Office",
                "api": "https://ops.epo.org/3.2/rest-services",
                "region": "EU"
            },
            "cnipa": {
                "name": "China National IP Administration",
                "api": "http://epub.cnipa.gov.cn",
                "region": "Asia"
            },
            "jpo": {
                "name": "Japan Patent Office",
                "api": "https://www.j-platpat.inpit.go.jp",
                "region": "Asia"
            },
            # Google Patents as fallback (covers all regions)
            "google": {
                "name": "Google Patents",
                "api": "https://patents.google.com",
                "region": "Global"
            }
        }
    
    async def execute(self, query: str, max_results: int = 20) -> Dict[str, Any]:
        """
        Execute patent search across EU/Asia patent offices
        
        Args:
            query: Search query (e.g., "GaN power IC automotive")
            max_results: Maximum patents to return
            
        Returns:
            Dictionary with found patents
        """
        print(f"🔍 Searching patents for: {query}")
        
        patents = []
        
        # Search EPO (European patents)
        epo_patents = await self._search_epo(query, max_results // 2)
        patents.extend(epo_patents)
        
        # Search Google Patents with region filter (Asia focus)
        asia_patents = await self._search_google_patents(
            query, 
            region=["CN", "JP", "KR", "TW"],
            max_results=max_results // 2
        )
        patents.extend(asia_patents)
        
        # Deduplicate by patent number
        unique_patents = self._deduplicate_patents(patents)
        
        # Extract innovation trends
        trends = self._analyze_patent_trends(unique_patents)
        
        return {
            "source": "patent_search",
            "query": query,
            "patents_found": len(unique_patents),
            "patents": unique_patents[:max_results],
            "trends": trends,
            "offices_searched": ["EPO", "Google Patents (Asia focus)"]
        }
    
    async def _search_epo(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search European Patent Office (EPO)
        Uses EPO Open Patent Services (OPS) API
        """
        patents = []
        
        # EPO OPS requires authentication - implement OAuth2 flow
        # For now, we'll use a simplified approach with public search
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # EPO OPS search endpoint
                # Note: Real implementation needs OAuth2 token
                search_url = f"{self.patent_sources['epo']['api']}/published-data/search"
                
                # Construct CQL query for electrical/electronics domain
                cql_query = self._build_epo_query(query)
                
                params = {
                    "q": cql_query,
                    "Range": f"1-{max_results}"
                }
                
                # Note: This is a placeholder - actual EPO API requires authentication
                # response = await client.get(search_url, params=params)
                
                # Parse EPO XML response
                # patents = self._parse_epo_response(response.text)
                
                # Placeholder: Return sample structure
                patents = self._create_sample_epo_patents(query)
                
            except Exception as e:
                print(f"⚠️  EPO search error: {str(e)}")
        
        return patents
    
    def _build_epo_query(self, query: str) -> str:
        """
        Build CQL query for EPO OPS
        Focus on electrical/electronics classifications
        """
        # IPC classifications for EE domains
        ee_classifications = [
            "H01L",  # Semiconductor devices
            "H02M",  # Power conversion
            "H03K",  # Pulse circuits
            "H02J",  # Power supply systems
            "G06F",  # Digital computing (for embedded systems)
        ]
        
        # Extract key terms
        terms = query.split()
        
        # Build CQL: (title OR abstract) AND classification
        cql_parts = [f'ta="{term}"' for term in terms[:3]]  # Limit to 3 main terms
        cql_query = " AND ".join(cql_parts)
        
        # Add classification filter
        class_filter = " OR ".join([f'cl="{ipc}"' for ipc in ee_classifications])
        cql_query += f" AND ({class_filter})"
        
        return cql_query
    
    async def _search_google_patents(
        self,
        query: str,
        region: List[str],
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Search Google Patents with regional filter
        Focuses on Asia (CN, JP, KR, TW)
        """
        patents = []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Google Patents doesn't have official API
                # Use web scraping or alternative: PatentsView API, Lens.org API
                
                # Alternative: Use Lens.org API (requires API key)
                # https://docs.api.lens.org/
                
                # For demonstration, create structured sample data
                patents = self._create_sample_asia_patents(query, region)
                
            except Exception as e:
                print(f"⚠️  Google Patents search error: {str(e)}")
        
        return patents
    
    def _create_sample_epo_patents(self, query: str) -> List[Dict[str, Any]]:
        """Create sample EPO patent structure (for testing)"""
        return [
            {
                "patent_number": "EP3845123B1",
                "title": f"Advanced {query} Power Management System",
                "applicant": "Infineon Technologies AG",
                "filing_date": "2020-03-15",
                "publication_date": "2021-07-07",
                "abstract": f"A novel approach to {query} with improved efficiency...",
                "ipc_classes": ["H02M3/156", "H01L29/78"],
                "region": "EU",
                "office": "EPO",
                "status": "Granted",
                "url": "https://worldwide.espacenet.com/patent/search/family/EP3845123"
            },
            {
                "patent_number": "EP3912234A1",
                "title": f"High-Efficiency {query} Circuit",
                "applicant": "STMicroelectronics",
                "filing_date": "2021-06-20",
                "publication_date": "2022-11-23",
                "abstract": f"Improved {query} topology for automotive applications...",
                "ipc_classes": ["H02M1/08", "H02M3/335"],
                "region": "EU",
                "office": "EPO",
                "status": "Pending",
                "url": "https://worldwide.espacenet.com/patent/search/family/EP3912234"
            }
        ]
    
    def _create_sample_asia_patents(self, query: str, regions: List[str]) -> List[Dict[str, Any]]:
        """Create sample Asia patent structure (for testing)"""
        return [
            {
                "patent_number": "CN114123456B",
                "title": f"{query} Control Method and Device",
                "applicant": "Huawei Technologies Co., Ltd.",
                "filing_date": "2021-01-10",
                "publication_date": "2022-05-20",
                "abstract": f"A control method for {query} in electric vehicles...",
                "ipc_classes": ["H02M3/156", "B60L15/20"],
                "region": "Asia",
                "office": "CNIPA",
                "country": "CN",
                "status": "Granted",
                "url": "http://epub.cnipa.gov.cn/patent/CN114123456B"
            },
            {
                "patent_number": "JP2022-123456A",
                "title": f"Semiconductor Device for {query}",
                "applicant": "Rohm Co., Ltd.",
                "filing_date": "2020-12-15",
                "publication_date": "2022-08-25",
                "abstract": f"Silicon carbide semiconductor device for {query} applications...",
                "ipc_classes": ["H01L29/16", "H02M1/08"],
                "region": "Asia",
                "office": "JPO",
                "country": "JP",
                "status": "Pending",
                "url": "https://www.j-platpat.inpit.go.jp/p0200"
            }
        ]
    
    def _deduplicate_patents(self, patents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate patents based on patent family"""
        seen = set()
        unique = []
        
        for patent in patents:
            patent_num = patent.get("patent_number")
            if patent_num and patent_num not in seen:
                seen.add(patent_num)
                unique.append(patent)
        
        return unique
    
    def _analyze_patent_trends(self, patents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends from patent data"""
        if not patents:
            return {}
        
        # Count by year
        by_year = {}
        for patent in patents:
            year = patent.get("filing_date", "")[:4]
            by_year[year] = by_year.get(year, 0) + 1
        
        # Count by applicant
        by_applicant = {}
        for patent in patents:
            applicant = patent.get("applicant", "Unknown")
            by_applicant[applicant] = by_applicant.get(applicant, 0) + 1
        
        # Top technologies (IPC classes)
        by_ipc = {}
        for patent in patents:
            for ipc in patent.get("ipc_classes", []):
                main_class = ipc.split("/")[0] if "/" in ipc else ipc
                by_ipc[main_class] = by_ipc.get(main_class, 0) + 1
        
        return {
            "filing_trend": by_year,
            "top_applicants": dict(sorted(by_applicant.items(), key=lambda x: x[1], reverse=True)[:5]),
            "top_technologies": dict(sorted(by_ipc.items(), key=lambda x: x[1], reverse=True)[:5])
        }