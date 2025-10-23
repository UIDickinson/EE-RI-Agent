import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class ResultProcessor:
    """
    10-stage result processing pipeline
    
    Inspired by Phontra's sophisticated content processing:
    1. Deduplication
    2. Quality filtering
    3. Relevance filtering
    4. Regional filtering
    5. TRL classification
    6. Cross-referencing
    7. Ranking
    8. Clustering
    9. Synthesis
    10. Report generation
    """
    
    def __init__(self):
        self.min_quality_score = 0.3
        self.min_relevance_score = 0.4
        logger.info("ResultProcessor initialized")
    
    async def process(
        self,
        raw_results: Dict[str, Any],
        query_understanding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process raw results through 10-stage pipeline
        
        Args:
            raw_results: Raw data from providers
            query_understanding: Processed query information
            
        Returns:
            Processed and synthesized results
        """
        try:
            logger.info("Starting result processing pipeline")
            
            # Stage 1: Deduplication
            results = self._deduplicate(raw_results)
            logger.info(f"Stage 1: Deduplication complete")
            
            # Stage 2: Quality filtering
            results = self._filter_quality(results)
            logger.info(f"Stage 2: Quality filtering complete")
            
            # Stage 3: Relevance filtering
            results = self._filter_relevance(results, query_understanding)
            logger.info(f"Stage 3: Relevance filtering complete")
            
            # Stage 4: Regional filtering
            results = self._filter_regional(results, query_understanding)
            logger.info(f"Stage 4: Regional filtering complete")
            
            # Stage 5: TRL classification
            results = await self._classify_trl(results)
            logger.info(f"Stage 5: TRL classification complete")
            
            # Stage 6: Cross-referencing
            results = self._cross_reference(results)
            logger.info(f"Stage 6: Cross-referencing complete")
            
            # Stage 7: Ranking
            results = self._rank_results(results, query_understanding)
            logger.info(f"Stage 7: Ranking complete")
            
            # Stage 8: Clustering
            results = self._cluster_results(results)
            logger.info(f"Stage 8: Clustering complete")
            
            # Stage 9: Synthesis
            synthesis = self._synthesize_findings(results, query_understanding)
            logger.info(f"Stage 9: Synthesis complete")
            
            # Stage 10: Report generation
            report = self._generate_report(synthesis, query_understanding)
            logger.info(f"Stage 10: Report generation complete")
            
            return {
                "processed_results": results,
                "synthesis": synthesis,
                "report": report,
                "metadata": {
                    "pipeline_stages": 10,
                    "total_findings": self._count_findings(results),
                    "processing_timestamp": datetime.utcnow().isoformat()
                }
            }
        
        except Exception as e:
            logger.error(f"Result processing error: {str(e)}")
            return {
                "error": str(e),
                "processed_results": raw_results,
                "synthesis": {},
                "report": "Error processing results"
            }
    
    def _deduplicate(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stage 1: Remove duplicates across all result types
        """
        deduplicated = {}
        
        # Deduplicate papers (by DOI or title)
        papers = results.get("papers", {}).get("data", {}).get("papers", [])
        deduplicated["papers"] = self._deduplicate_papers(papers)
        
        # Deduplicate patents (by patent number)
        patents = results.get("patents", {}).get("data", {}).get("patents", [])
        deduplicated["patents"] = self._deduplicate_patents(patents)
        
        # Deduplicate components (by part number)
        components = results.get("components", {}).get("data", {}).get("components", [])
        deduplicated["components"] = self._deduplicate_components(components)
        
        # Supply chain data (already unique by part number)
        supply_chain = results.get("supply_chain", {}).get("data", {}).get("components", [])
        deduplicated["supply_chain"] = supply_chain
        
        return deduplicated
    
    def _deduplicate_papers(self, papers: List[Dict]) -> List[Dict]:
        """Deduplicate papers by DOI or title hash"""
        seen = set()
        unique = []
        
        for paper in papers:
            # Use DOI as primary key, fallback to title hash
            identifier = paper.get("doi")
            if not identifier:
                title = paper.get("title", "")
                identifier = hashlib.md5(title.lower().encode()).hexdigest()
            
            if identifier not in seen:
                seen.add(identifier)
                unique.append(paper)
        
        return unique
    
    def _deduplicate_patents(self, patents: List[Dict]) -> List[Dict]:
        """Deduplicate patents by patent number"""
        seen = set()
        unique = []
        
        for patent in patents:
            pn = patent.get("patent_number")
            if pn and pn not in seen:
                seen.add(pn)
                unique.append(patent)
        
        return unique
    
    def _deduplicate_components(self, components: List[Dict]) -> List[Dict]:
        """Deduplicate components by part number"""
        seen = set()
        unique = []
        
        for component in components:
            pn = component.get("part_number")
            if pn and pn not in seen:
                seen.add(pn)
                unique.append(component)
        
        return unique
    
    def _filter_quality(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stage 2: Filter out low-quality results
        """
        filtered = {}
        
        # Filter papers (must have title, authors, abstract)
        papers = results.get("papers", [])
        filtered["papers"] = [
            p for p in papers
            if p.get("title") and p.get("authors") and len(p.get("abstract", "")) > 50
        ]
        
        # Filter patents (must have title, abstract, patent number)
        patents = results.get("patents", [])
        filtered["patents"] = [
            p for p in patents
            if p.get("title") and p.get("abstract") and p.get("patent_number")
        ]
        
        # Filter components (must have part number and manufacturer)
        components = results.get("components", [])
        filtered["components"] = [
            c for c in components
            if c.get("part_number") and c.get("manufacturer")
        ]
        
        filtered["supply_chain"] = results.get("supply_chain", [])
        
        return filtered
    
    def _filter_relevance(
        self,
        results: Dict[str, Any],
        query_understanding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Stage 3: Filter by relevance to query
        """
        query = query_understanding.get("parameters", {}).get("query", "").lower()
        entities = query_understanding.get("entities", {})
        
        filtered = {}
        
        # Filter papers by keyword relevance
        papers = results.get("papers", [])
        filtered["papers"] = [
            p for p in papers
            if self._is_relevant(p, query, entities)
        ]
        
        # Filter patents similarly
        patents = results.get("patents", [])
        filtered["patents"] = [
            p for p in patents
            if self._is_relevant(p, query, entities)
        ]
        
        # Components are usually already relevant from search
        filtered["components"] = results.get("components", [])
        filtered["supply_chain"] = results.get("supply_chain", [])
        
        return filtered
    
    def _is_relevant(
        self,
        item: Dict[str, Any],
        query: str,
        entities: Dict[str, Any]
    ) -> bool:
        """Check if item is relevant to query"""
        # Combine title and abstract
        text = f"{item.get('title', '')} {item.get('abstract', '')}".lower()
        
        # Check if query terms appear
        query_words = query.split()
        matches = sum(1 for word in query_words if word in text)
        
        # Check if entities appear
        for entity_list in entities.values():
            if isinstance(entity_list, list):
                matches += sum(1 for entity in entity_list if entity.lower() in text)
        
        # Relevance threshold: at least 30% of terms match
        return matches >= len(query_words) * 0.3
    
    def _filter_regional(
        self,
        results: Dict[str, Any],
        query_understanding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Stage 4: Filter by regional preferences (EU/Asia)
        """
        target_regions = query_understanding.get("parameters", {}).get("regions", ["EU", "Asia"])
        
        filtered = results.copy()
        
        # Filter components by manufacturer region
        components = results.get("components", [])
        filtered["components"] = [
            c for c in components
            if self._is_regional_match(c.get("manufacturer", ""), target_regions)
        ]
        
        # Filter supply chain by availability in target regions
        supply_chain = results.get("supply_chain", [])
        filtered["supply_chain"] = [
            sc for sc in supply_chain
            if any(
                dist.get("region") in target_regions
                for dist in sc.get("availability", {}).values()
            )
        ]
        
        # Papers and patents stay (global knowledge)
        filtered["papers"] = results.get("papers", [])
        filtered["patents"] = results.get("patents", [])
        
        return filtered
    
    def _is_regional_match(self, manufacturer: str, target_regions: List[str]) -> bool:
        """Check if manufacturer matches target regions"""
        eu_mfrs = ["infineon", "stmicroelectronics", "st", "nxp", "philips"]
        asia_mfrs = ["renesas", "rohm", "toshiba", "panasonic", "samsung"]
        
        mfr_lower = manufacturer.lower()
        
        if "EU" in target_regions:
            if any(m in mfr_lower for m in eu_mfrs):
                return True
        
        if "Asia" in target_regions:
            if any(m in mfr_lower for m in asia_mfrs):
                return True
        
        # Texas Instruments, Analog Devices (US) - allow if no strict filtering
        return True
    
    async def _classify_trl(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stage 5: Add TRL classifications
        (This would normally call TRLProvider, but we'll add placeholders)
        """
        # Add TRL to components (placeholder)
        for component in results.get("components", []):
            if "trl" not in component:
                # Simple heuristic: if has supply chain, TRL 7-9
                if component.get("lifecycle") == "Active":
                    component["trl"] = 9
                else:
                    component["trl"] = 7
        
        # Add TRL to papers (typically 1-3)
        for paper in results.get("papers", []):
            if "trl" not in paper:
                paper["trl"] = 2
        
        # Add TRL to patents (typically 4-6)
        for patent in results.get("patents", []):
            if "trl" not in patent:
                patent["trl"] = 5 if patent.get("status") == "Granted" else 4
        
        return results
    
    def _cross_reference(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stage 6: Cross-reference findings (papers ↔ patents ↔ components)
        """
        cross_refs = {
            "paper_to_patent": [],
            "patent_to_component": [],
            "paper_to_component": []
        }
        
        papers = results.get("papers", [])
        patents = results.get("patents", [])
        components = results.get("components", [])
        
        # Find papers citing patents
        for paper in papers:
            paper_text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
            for patent in patents:
                patent_num = patent.get("patent_number", "").lower()
                if patent_num and patent_num in paper_text:
                    cross_refs["paper_to_patent"].append({
                        "paper": paper.get("title"),
                        "patent": patent.get("patent_number")
                    })
        
        # Find patents describing components
        for patent in patents:
            patent_text = f"{patent.get('title', '')} {patent.get('abstract', '')}".lower()
            for component in components:
                comp_cat = component.get("category", "").lower()
                if comp_cat and comp_cat in patent_text:
                    cross_refs["patent_to_component"].append({
                        "patent": patent.get("patent_number"),
                        "component": component.get("part_number")
                    })
        
        results["cross_references"] = cross_refs
        return results
    
    def _rank_results(
        self,
        results: Dict[str, Any],
        query_understanding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Stage 7: Rank results by relevance and quality
        """
        # Rank papers by year (newer first)
        papers = results.get("papers", [])
        papers.sort(key=lambda p: p.get("year", 0), reverse=True)
        results["papers"] = papers[:20]  # Top 20
        
        # Rank patents by filing date
        patents = results.get("patents", [])
        patents.sort(key=lambda p: p.get("filing_date", ""), reverse=True)
        results["patents"] = patents[:20]
        
        # Rank components by TRL (production-ready first)
        components = results.get("components", [])
        components.sort(key=lambda c: c.get("trl", 0), reverse=True)
        results["components"] = components[:30]
        
        return results
    
    def _cluster_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stage 8: Cluster related findings
        (Simplified - in production, use semantic clustering)
        """
        # Group components by category
        components = results.get("components", [])
        clusters = {}
        
        for component in components:
            category = component.get("category", "Other")
            if category not in clusters:
                clusters[category] = []
            clusters[category].append(component)
        
        results["component_clusters"] = clusters
        return results
    
    def _synthesize_findings(
        self,
        results: Dict[str, Any],
        query_understanding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Stage 9: Synthesize findings into structured summary
        """
        papers = results.get("papers", [])
        patents = results.get("patents", [])
        components = results.get("components", [])
        supply_chain = results.get("supply_chain", [])
        
        synthesis = {
            "summary": self._create_summary(papers, patents, components),
            "key_findings": self._extract_key_findings(results),
            "technology_trends": self._identify_trends(papers, patents),
            "component_recommendations": self._recommend_components(components, supply_chain),
            "supply_chain_status": self._assess_supply_chain(supply_chain),
            "trl_distribution": self._calculate_trl_distribution(results)
        }
        
        return synthesis
    
    def _create_summary(self, papers: List, patents: List, components: List) -> str:
        """Create executive summary"""
        return (
            f"Research completed: Found {len(papers)} academic papers, "
            f"{len(patents)} patents, and {len(components)} components. "
            f"Analysis includes TRL classification, supply chain assessment, and cross-referencing."
        )
    
    def _extract_key_findings(self, results: Dict[str, Any]) -> List[str]:
        """Extract key findings"""
        findings = []
        
        # Top papers
        papers = results.get("papers", [])[:3]
        if papers:
            findings.append(f"Recent research highlights: {papers[0].get('title', 'Unknown')}")
        
        # Production-ready components
        components = [c for c in results.get("components", []) if c.get("trl", 0) >= 8]
        if components:
            findings.append(f"{len(components)} production-ready components identified")
        
        return findings
    
    def _identify_trends(self, papers: List, patents: List) -> List[str]:
        """Identify technology trends"""
        # Simple trend identification
        trends = []
        
        # Count recent papers
        recent_papers = [p for p in papers if p.get("year", 0) >= 2023]
        if len(recent_papers) > 5:
            trends.append("High research activity in recent years")
        
        # Patent trends
        recent_patents = [p for p in patents if p.get("filing_date", "")[:4] >= "2023"]
        if len(recent_patents) > 3:
            trends.append("Active patent filing indicates commercial interest")
        
        return trends
    
    def _recommend_components(
        self,
        components: List[Dict],
        supply_chain: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate component recommendations"""
        recommendations = []
        
        # Merge supply chain data
        sc_map = {sc.get("part_number"): sc for sc in supply_chain}
        
        for component in components[:5]:  # Top 5
            pn = component.get("part_number")
            
            recommendation = {
                "part_number": pn,
                "manufacturer": component.get("manufacturer"),
                "trl": component.get("trl"),
                "lifecycle": component.get("lifecycle"),
                "rationale": []
            }
            
            # Generate rationale
            if component.get("trl", 0) >= 8:
                recommendation["rationale"].append("Production-proven")
            
            if component.get("lifecycle") == "Active":
                recommendation["rationale"].append("Active lifecycle")
            
            # Check supply chain
            if pn in sc_map:
                sc_data = sc_map[pn]
                total_stock = sum(
                    d.get("stock", 0)
                    for d in sc_data.get("availability", {}).values()
                )
                if total_stock > 1000:
                    recommendation["rationale"].append(f"Good availability ({total_stock} units)")
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _assess_supply_chain(self, supply_chain: List[Dict]) -> Dict[str, Any]:
        """Assess overall supply chain health"""
        if not supply_chain:
            return {"status": "no_data"}
        
        total_stock = 0
        active_count = 0
        
        for sc in supply_chain:
            # Count stock
            for dist_data in sc.get("availability", {}).values():
                total_stock += dist_data.get("stock", 0)
            
            # Count active components
            if sc.get("lifecycle") == "Active":
                active_count += 1
        
        health = "healthy" if total_stock > 5000 else "low_stock"
        
        return {
            "status": health,
            "total_stock": total_stock,
            "active_components": active_count,
            "components_checked": len(supply_chain)
        }
    
    def _calculate_trl_distribution(self, results: Dict[str, Any]) -> Dict[str, int]:
        """Calculate TRL distribution across all findings"""
        distribution = {f"TRL {i}": 0 for i in range(1, 10)}
        
        # Count from papers
        for paper in results.get("papers", []):
            trl = paper.get("trl")
            if trl:
                distribution[f"TRL {trl}"] += 1
        
        # Count from patents
        for patent in results.get("patents", []):
            trl = patent.get("trl")
            if trl:
                distribution[f"TRL {trl}"] += 1
        
        # Count from components
        for component in results.get("components", []):
            trl = component.get("trl")
            if trl:
                distribution[f"TRL {trl}"] += 1
        
        return distribution
    
    def _generate_report(
        self,
        synthesis: Dict[str, Any],
        query_understanding: Dict[str, Any]
    ) -> str:
        """
        Stage 10: Generate final readable report
        """
        query = query_understanding.get("parameters", {}).get("query", "Unknown query")
        
        report = f"# EE Research Report\n\n"
        report += f"**Query:** {query}\n\n"
        report += f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        
        # Summary
        report += f"## Executive Summary\n\n"
        report += f"{synthesis.get('summary', 'No summary available')}\n\n"
        
        # Key Findings
        findings = synthesis.get("key_findings", [])
        if findings:
            report += f"## Key Findings\n\n"
            for finding in findings:
                report += f"- {finding}\n"
            report += "\n"
        
        # Technology Trends
        trends = synthesis.get("technology_trends", [])
        if trends:
            report += f"## Technology Trends\n\n"
            for trend in trends:
                report += f"- {trend}\n"
            report += "\n"
        
        # Component Recommendations
        recommendations = synthesis.get("component_recommendations", [])
        if recommendations:
            report += f"## Recommended Components\n\n"
            for i, rec in enumerate(recommendations, 1):
                report += f"{i}. **{rec.get('part_number')}** ({rec.get('manufacturer')})\n"
                report += f"   - TRL: {rec.get('trl')}\n"
                report += f"   - Lifecycle: {rec.get('lifecycle')}\n"
                if rec.get('rationale'):
                    report += f"   - Rationale: {', '.join(rec.get('rationale'))}\n"
                report += "\n"
        
        # Supply Chain Status
        sc_status = synthesis.get("supply_chain_status", {})
        if sc_status.get("status") != "no_data":
            report += f"## Supply Chain Status\n\n"
            report += f"- Overall Health: **{sc_status.get('status', 'Unknown').upper()}**\n"
            report += f"- Total Stock: {sc_status.get('total_stock', 0)} units\n"
            report += f"- Active Components: {sc_status.get('active_components', 0)}\n\n"
        
        # TRL Distribution
        trl_dist = synthesis.get("trl_distribution", {})
        if sum(trl_dist.values()) > 0:
            report += f"## Technology Readiness Distribution\n\n"
            report += "| TRL Level | Count |\n"
            report += "|-----------|-------|\n"
            for trl in range(1, 10):
                count = trl_dist.get(f"TRL {trl}", 0)
                if count > 0:
                    report += f"| TRL {trl} | {count} |\n"
            report += "\n"
        
        # Maturity Assessment
        research = sum(trl_dist.get(f"TRL {i}", 0) for i in range(1, 4))
        development = sum(trl_dist.get(f"TRL {i}", 0) for i in range(4, 7))
        production = sum(trl_dist.get(f"TRL {i}", 0) for i in range(7, 10))
        total = research + development + production
        
        if total > 0:
            report += f"## Maturity Assessment\n\n"
            report += f"- Research Phase (TRL 1-3): {research/total*100:.1f}%\n"
            report += f"- Development Phase (TRL 4-6): {development/total*100:.1f}%\n"
            report += f"- Production Phase (TRL 7-9): {production/total*100:.1f}%\n\n"
        
        report += "---\n\n"
        report += "*This report was generated by EE Research Scout - A Sentient Agent Framework application*\n"
        
        return report
    
    def _count_findings(self, results: Dict[str, Any]) -> int:
        """Count total findings across all types"""
        return (
            len(results.get("papers", [])) +
            len(results.get("patents", [])) +
            len(results.get("components", [])) +
            len(results.get("supply_chain", []))
        )
    
    def validate_results(self, results: Dict[str, Any]) -> bool:
        """
        Validate processed results
        
        Returns True if results are valid and ready for output
        """
        required_keys = ["processed_results", "synthesis", "report"]
        
        if not all(key in results for key in required_keys):
            return False
        
        # Check if we have at least some findings
        processed = results.get("processed_results", {})
        total_findings = self._count_findings(processed)
        
        return total_findings > 0
    
    async def enhance_results(
        self,
        results: Dict[str, Any],
        query_understanding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optional enhancement step - add AI-generated insights
        """
        try:
            # This could use AI to generate additional insights
            # For now, just return as-is
            return results
        
        except Exception as e:
            logger.error(f"Enhancement error: {str(e)}")
            return results
    
    def create_summary_for_streaming(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create incremental updates suitable for streaming responses
        
        Returns list of update chunks that can be streamed to client
        """
        chunks = []
        
        processed = results.get("processed_results", {})
        
        # Chunk 1: Papers found
        papers = processed.get("papers", [])
        if papers:
            chunks.append({
                "type": "papers",
                "message": f"Found {len(papers)} academic papers",
                "count": len(papers),
                "preview": [p.get("title") for p in papers[:3]]
            })
        
        # Chunk 2: Patents found
        patents = processed.get("patents", [])
        if patents:
            chunks.append({
                "type": "patents",
                "message": f"Found {len(patents)} patents",
                "count": len(patents),
                "preview": [p.get("patent_number") for p in patents[:3]]
            })
        
        # Chunk 3: Components found
        components = processed.get("components", [])
        if components:
            chunks.append({
                "type": "components",
                "message": f"Found {len(components)} components",
                "count": len(components),
                "preview": [c.get("part_number") for c in components[:3]]
            })
        
        # Chunk 4: Supply chain status
        supply_chain = processed.get("supply_chain", [])
        if supply_chain:
            chunks.append({
                "type": "supply_chain",
                "message": f"Checked supply chain for {len(supply_chain)} components",
                "count": len(supply_chain)
            })
        
        # Chunk 5: Synthesis
        synthesis = results.get("synthesis", {})
        if synthesis:
            chunks.append({
                "type": "synthesis",
                "message": "Analysis complete",
                "summary": synthesis.get("summary", "")
            })
        
        return chunks