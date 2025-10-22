from typing import List, Dict, Any
from agno.aggregator import Aggregator

from tools.knowledge_graph import update_knowledge_graph
from tools.trl_classifier import classify_trl

class EEAggregator(Aggregator):
    """
    Aggregates subtask results into final EE research report
    """
    
    def __init__(self):
        super().__init__(
            name="EE Report Aggregator",
            description="Synthesizes EE research findings into academic reports"
        )
    
    async def aggregate(
        self,
        subtask_results: List[Dict[str, Any]],
        original_query: str
    ) -> Dict[str, Any]:
        """
        Aggregate all subtask results into comprehensive report
        """
        # Extract results by type
        papers = self._extract_by_source(subtask_results, "academic_papers")
        patents = self._extract_by_source(subtask_results, "patent_search")
        components = self._extract_by_source(subtask_results, "datasheet_search")
        supply_chain = self._extract_by_source(subtask_results, "supply_chain")
        
        # Classify by TRL
        classified_components = await self._classify_components(components)
        
        # Update knowledge graph
        await update_knowledge_graph({
            "query": original_query,
            "papers": papers,
            "patents": patents,
            "components": classified_components
        })
        
        # Generate comprehensive report
        report = await self._generate_report(
            original_query,
            papers,
            patents,
            classified_components,
            supply_chain
        )
        
        return report
    
    def _extract_by_source(
        self,
        results: List[Dict[str, Any]],
        source: str
    ) -> List[Dict[str, Any]]:
        """Extract results from specific source"""
        for result in results:
            if result.get("source") == source:
                return result.get("papers", []) or result.get("components", [])
        return []
    
    async def _classify_components(
        self,
        components: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Classify components by TRL"""
        for component in components:
            component["trl"] = await classify_trl(component)
        return components
    
    async def _generate_report(
        self,
        query: str,
        papers: List,
        patents: List,
        components: List,
        supply_chain: Dict
    ) -> Dict[str, Any]:
        """Generate final academic-grade report"""
        
        report = {
            "query": query,
            "executive_summary": self._create_summary(papers, components),
            "technical_analysis": {
                "components": components,
                "trl_distribution": self._trl_distribution(components),
                "supply_chain_status": supply_chain
            },
            "literature_review": {
                "papers": papers[:10],
                "patents": patents[:10],
                "key_findings": self._extract_key_findings(papers)
            },
            "recommendations": self._generate_recommendations(components, supply_chain),
            "references": self._format_references(papers, patents)
        }
        
        return report
    
    def _create_summary(self, papers: List, components: List) -> str:
        """Create executive summary"""
        return f"Found {len(papers)} relevant papers and {len(components)} components..."
    
    def _trl_distribution(self, components: List) -> Dict[str, int]:
        """Count components by TRL level"""
        distribution = {}
        for comp in components:
            trl = comp.get("trl", "Unknown")
            distribution[trl] = distribution.get(trl, 0) + 1
        return distribution
    
    def _extract_key_findings(self, papers: List) -> List[str]:
        """Extract key findings from papers"""
        return []  # Implement with LLM summarization
    
    def _generate_recommendations(self, components: List, supply_chain: Dict) -> List[str]:
        """Generate actionable recommendations"""
        return []
    
    def _format_references(self, papers: List, patents: List) -> List[str]:
        """Format academic references"""
        refs = []
        for paper in papers:
            refs.append(f"{paper.get('authors')} ({paper.get('year')}). {paper.get('title')}.")
        return refs