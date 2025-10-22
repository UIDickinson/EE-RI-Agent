from typing import Dict, Any, List
from datetime import datetime
import asyncio

class ReportGenerator:
    """
    Generates comprehensive, academic-grade technical reports
    """
    
    def __init__(self):
        self.report_templates = {
            "quick": self._generate_quick_report,
            "deep": self._generate_deep_report
        }
    
    async def generate(
        self,
        query: str,
        data: Dict[str, Any],
        depth: str = "deep"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive report
        
        Args:
            query: Original research query
            data: Aggregated and classified data
            depth: "quick" or "deep" analysis
            
        Returns:
            Structured report with multiple sections
        """
        generator = self.report_templates.get(depth, self._generate_deep_report)
        return await generator(query, data)
    
    async def _generate_quick_report(
        self,
        query: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate quick summary report"""
        return {
            "report_type": "quick_summary",
            "executive_summary": self._create_executive_summary(query, data),
            "key_findings": self._extract_key_findings(data),
            "component_recommendations": self._recommend_components(data["components"][:5]),
            "next_steps": self._suggest_next_steps(data)
        }
    
    async def _generate_deep_report(
        self,
        query: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive academic-grade report"""
        
        report = {
            "report_type": "comprehensive_analysis",
            "title": self._generate_title(query),
            "generated_at": datetime.utcnow().isoformat(),
            
            # Executive Summary
            "executive_summary": self._create_executive_summary(query, data),
            
            # Literature Review
            "literature_review": {
                "overview": self._create_literature_overview(data["papers"]),
                "key_papers": self._highlight_key_papers(data["papers"][:10]),
                "research_trends": self._analyze_research_trends(data["papers"]),
                "knowledge_gaps": self._identify_knowledge_gaps(data)
            },
            
            # Patent Landscape
            "patent_analysis": {
                "overview": self._create_patent_overview(data["patents"]),
                "key_patents": self._highlight_key_patents(data["patents"][:10]),
                "innovation_trends": data["patents"][0].get("trends", {}) if data["patents"] else {},
                "competitive_landscape": self._analyze_competitive_landscape(data["patents"])
            },
            
            # Technical Analysis
            "technical_analysis": {
                "component_overview": self._create_component_overview(data["components"]),
                "trl_assessment": data.get("trl_summary", {}),
                "specification_comparison": self._create_spec_comparison(data["components"]),
                "performance_analysis": self._analyze_performance(data["components"]),
                "design_considerations": self._extract_design_considerations(data)
            },
            
            # Supply Chain Analysis
            "supply_chain_analysis": self._create_supply_chain_analysis(data["components"]),
            
            # Cross-Reference Analysis
            "innovation_path": self._trace_innovation_path(data.get("cross_references", {})),
            
            # Recommendations
            "recommendations": {
                "recommended_components": self._recommend_components(data["components"]),
                "alternative_approaches": self._suggest_alternatives(data),
                "implementation_guidance": self._provide_implementation_guidance(data),
                "risk_assessment": self._assess_risks(data)
            },
            
            # References
            "references": {
                "papers": self._format_paper_references(data["papers"]),
                "patents": self._format_patent_references(data["patents"]),
                "datasheets": self._format_datasheet_references(data["components"])
            },
            
            # Appendix
            "appendix": {
                "detailed_specifications": self._create_detailed_specs(data["components"]),
                "methodology": self._document_methodology(),
                "data_sources": self._list_data_sources(data)
            }
        }
        
        return report
    
    def _generate_title(self, query: str) -> str:
        """Generate report title"""
        return f"Comprehensive Analysis: {query}"
    
    def _create_executive_summary(self, query: str, data: Dict[str, Any]) -> str:
        """Create executive summary"""
        num_papers = len(data.get("papers", []))
        num_patents = len(data.get("patents", []))
        num_components = len(data.get("components", []))
        
        trl_summary = data.get("trl_summary", {})
        readiness = trl_summary.get("readiness_assessment", "Unknown")
        
        summary = f"""
Research Query: {query}

This comprehensive analysis examined {num_papers} academic papers, {num_patents} patents, 
and {num_components} components to provide a complete technology landscape assessment.

Technology Readiness: {readiness}

The analysis reveals insights across the full innovation spectrum from basic research 
to production-ready solutions, with particular focus on EU and Asia markets for 
Embedded Systems, Power Management ICs, and EMC/EMI solutions.

Key findings include component availability, supply chain status, performance 
benchmarks, and implementation recommendations suitable for professional engineering 
applications.
        """.strip()
        
        return summary
    
    def _extract_key_findings(self, data: Dict[str, Any]) -> List[str]:
        """Extract key findings"""
        findings = []
        
        # TRL findings
        trl_summary = data.get("trl_summary", {})
        if trl_summary:
            findings.append(f"Technology Maturity: {trl_summary.get('readiness_assessment', 'Unknown')}")
        
        # Component findings
        if data.get("components"):
            active_count = sum(1 for c in data["components"] if c.get("lifecycle") == "Active")
            findings.append(f"{active_count} production-ready components identified")
        
        # Supply chain findings
        supply_issues = sum(
            1 for c in data.get("components", []) 
            if c.get("supply_chain", {}).get("overall_health") == "at_risk"
        )
        if supply_issues:
            findings.append(f"⚠️  {supply_issues} components show supply chain risks")
        
        return findings
    
    def _create_literature_overview(self, papers: List[Dict[str, Any]]) -> str:
        """Create literature review overview"""
        if not papers:
            return "No academic papers found for this query."
        
        return f"""
The literature search identified {len(papers)} relevant academic publications 
spanning recent research in this domain. The papers cover theoretical foundations, 
experimental results, and practical implementations relevant to the query.
        """.strip()
    
    def _highlight_key_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Highlight most important papers"""
        key_papers = []
        
        for paper in papers[:10]:
            key_papers.append({
                "title": paper.get("title"),
                "authors": paper.get("authors", []),
                "year": paper.get("year"),
                "abstract": paper.get("abstract", "")[:300] + "...",
                "url": paper.get("url"),
                "relevance": "High"  # Could be calculated
            })
        
        return key_papers
    
    def _analyze_research_trends(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze research trends from papers"""
        # Count by year
        by_year = {}
        for paper in papers:
            year = paper.get("year")
            if year:
                by_year[str(year)] = by_year.get(str(year), 0) + 1
        
        return {
            "publication_trend": by_year,
            "trending_topics": [],  # Could extract with NLP
            "research_intensity": "Active" if len(papers) > 10 else "Limited"
        }
    
    def _identify_knowledge_gaps(self, data: Dict[str, Any]) -> List[str]:
        """Identify knowledge gaps"""
        gaps = []
        
        # Check for missing TRL levels
        trl_dist = data.get("trl_summary", {}).get("trl_distribution", {})
        if trl_dist.get("TRL 4", 0) == 0 and trl_dist.get("TRL 5", 0) == 0:
            gaps.append("Limited mid-stage development (TRL 4-5) - transition gap from research to product")
        
        # Check for limited supply chain data
        components_with_sc = sum(
            1 for c in data.get("components", []) 
            if c.get("supply_chain")
        )
        if components_with_sc < len(data.get("components", [])) * 0.5:
            gaps.append("Limited supply chain visibility for some components")
        
        return gaps
    
    def _create_patent_overview(self, patents: List[Dict[str, Any]]) -> str:
        """Create patent landscape overview"""
        if not patents:
            return "No relevant patents found in EU/Asia patent offices."
        
        return f"""
Patent analysis identified {len(patents)} relevant patents from European (EPO) 
and Asian (CNIPA, JPO) patent offices, indicating active innovation in this domain.
        """.strip()
    
    def _highlight_key_patents(self, patents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Highlight most important patents"""
        key_patents = []
        
        for patent in patents[:10]:
            key_patents.append({
                "patent_number": patent.get("patent_number"),
                "title": patent.get("title"),
                "applicant": patent.get("applicant"),
                "filing_date": patent.get("filing_date"),
                "status": patent.get("status"),
                "abstract": patent.get("abstract", "")[:300] + "...",
                "url": patent.get("url")
            })
        
        return key_patents
    
    def _analyze_competitive_landscape(self, patents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze competitive landscape from patents"""
        applicants = {}
        for patent in patents:
            applicant = patent.get("applicant", "Unknown")
            applicants[applicant] = applicants.get(applicant, 0) + 1
        
        top_applicants = dict(sorted(applicants.items(), key=lambda x: x[1], reverse=True)[:5])
        
        return {
            "top_applicants": top_applicants,
            "competitive_intensity": "High" if len(applicants) > 10 else "Moderate",
            "market_leaders": list(top_applicants.keys())[:3]
        }
    
    def _create_component_overview(self, components: List[Dict[str, Any]]) -> str:
        """Create component overview"""
        if not components:
            return "No specific components identified."
        
        return f"""
Component analysis identified {len(components)} relevant parts from major 
manufacturers. Analysis includes specifications, availability, pricing, and lifecycle status.
        """.strip()
    
    def _create_spec_comparison(self, components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create specification comparison table"""
        comparison = []
        
        for comp in components[:10]:
            comparison.append({
                "part_number": comp.get("part_number"),
                "manufacturer": comp.get("manufacturer"),
                "category": comp.get("category"),
                "key_specs": comp.get("specs", {}),
                "trl": comp.get("trl"),
                "lifecycle": comp.get("lifecycle", "Unknown")
            })
        
        return comparison
    
    def _analyze_performance(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze component performance"""
        if not components:
            return {}
        
        # Extract performance metrics
        performance = {
            "efficiency_range": self._calculate_metric_range(components, "efficiency"),
            "power_range": self._calculate_metric_range(components, "power"),
            "best_performers": self._identify_best_performers(components)
        }
        
        return performance
    
    def _calculate_metric_range(self, components: List[Dict[str, Any]], metric: str) -> Dict[str, Any]:
        """Calculate range for a specific metric"""
        values = []
        for comp in components:
            specs = comp.get("specs", {})
            if metric in specs:
                values.append(specs[metric])
        
        if values:
            return {
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values)
            }
        return {}
    
    def _identify_best_performers(self, components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify top performing components"""
        # Sort by efficiency if available
        with_efficiency = [c for c in components if c.get("specs", {}).get("efficiency")]
        sorted_comps = sorted(
            with_efficiency,
            key=lambda x: x.get("specs", {}).get("efficiency", 0),
            reverse=True
        )
        
        return [
            {
                "part_number": c.get("part_number"),
                "manufacturer": c.get("manufacturer"),
                "efficiency": c.get("specs", {}).get("efficiency")
            }
            for c in sorted_comps[:3]
        ]
    
    def _extract_design_considerations(self, data: Dict[str, Any]) -> List[str]:
        """Extract design considerations from findings"""
        considerations = []
        
        # From papers
        for paper in data.get("papers", [])[:5]:
            abstract = paper.get("abstract", "")
            if "design" in abstract.lower() or "consideration" in abstract.lower():
                considerations.append(f"Paper insight: {abstract[:100]}...")
        
        # From components
        for comp in data.get("components", [])[:5]:
            features = comp.get("features", [])
            if features:
                considerations.append(f"{comp.get('part_number')}: {', '.join(features[:2])}")
        
        # General considerations
        considerations.extend([
            "Ensure thermal management for high-power applications",
            "Consider EMC/EMI compliance requirements",
            "Verify supply chain stability before committing to design"
        ])
        
        return considerations[:10]
    
    def _create_supply_chain_analysis(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create comprehensive supply chain analysis"""
        if not components:
            return {"status": "No supply chain data available"}
        
        # Count components by lifecycle
        lifecycle_counts = {}
        for comp in components:
            lifecycle = comp.get("lifecycle", "Unknown")
            lifecycle_counts[lifecycle] = lifecycle_counts.get(lifecycle, 0) + 1
        
        # Check availability
        low_stock_count = 0
        total_stock = 0
        
        for comp in components:
            sc_data = comp.get("supply_chain", {})
            for dist, data in sc_data.items():
                stock = data.get("stock", 0)
                total_stock += stock
                if stock < 100:
                    low_stock_count += 1
        
        # Assess risk
        risk_level = "Low"
        if lifecycle_counts.get("NRND", 0) > 0 or lifecycle_counts.get("Obsolete", 0) > 0:
            risk_level = "High"
        elif low_stock_count > len(components) * 0.3:
            risk_level = "Medium"
        
        return {
            "lifecycle_distribution": lifecycle_counts,
            "stock_status": {
                "total_units_available": total_stock,
                "low_stock_components": low_stock_count,
                "healthy_stock_components": len(components) - low_stock_count
            },
            "risk_assessment": {
                "level": risk_level,
                "factors": self._identify_risk_factors(components)
            },
            "recommendations": self._supply_chain_recommendations(risk_level, components)
        }
    
    def _identify_risk_factors(self, components: List[Dict[str, Any]]) -> List[str]:
        """Identify supply chain risk factors"""
        risks = []
        
        nrnd_count = sum(1 for c in components if c.get("lifecycle") == "NRND")
        if nrnd_count > 0:
            risks.append(f"{nrnd_count} component(s) marked Not Recommended for New Design")
        
        obsolete_count = sum(1 for c in components if c.get("lifecycle") == "Obsolete")
        if obsolete_count > 0:
            risks.append(f"{obsolete_count} component(s) obsolete")
        
        single_source = sum(
            1 for c in components 
            if len(c.get("supply_chain", {})) == 1
        )
        if single_source > 0:
            risks.append(f"{single_source} component(s) from single distributor")
        
        return risks if risks else ["No significant risks identified"]
    
    def _supply_chain_recommendations(self, risk_level: str, components: List[Dict[str, Any]]) -> List[str]:
        """Generate supply chain recommendations"""
        recommendations = []
        
        if risk_level == "High":
            recommendations.append("🚨 Immediate action required: Review NRND/Obsolete components")
            recommendations.append("Consider alternative components for at-risk parts")
            recommendations.append("Establish second sources where possible")
        elif risk_level == "Medium":
            recommendations.append("⚠️  Monitor stock levels closely")
            recommendations.append("Consider placing advance orders for critical components")
        else:
            recommendations.append("✅ Supply chain appears stable")
            recommendations.append("Continue regular monitoring")
        
        return recommendations
    
    def _trace_innovation_path(self, cross_refs: Dict[str, Any]) -> Dict[str, Any]:
        """Trace innovation path from research to product"""
        return {
            "research_to_patent": len(cross_refs.get("paper_to_patent", [])),
            "patent_to_product": len(cross_refs.get("patent_to_component", [])),
            "research_to_product": len(cross_refs.get("paper_to_component", [])),
            "innovation_velocity": self._assess_innovation_velocity(cross_refs),
            "key_transitions": self._identify_key_transitions(cross_refs)
        }
    
    def _assess_innovation_velocity(self, cross_refs: Dict[str, Any]) -> str:
        """Assess how quickly research becomes product"""
        total_links = sum(len(v) for v in cross_refs.values())
        
        if total_links > 20:
            return "High - Active research-to-product pipeline"
        elif total_links > 10:
            return "Moderate - Steady innovation flow"
        else:
            return "Low - Limited research-to-product connections"
    
    def _identify_key_transitions(self, cross_refs: Dict[str, Any]) -> List[str]:
        """Identify key innovation transitions"""
        transitions = []
        
        for link in cross_refs.get("paper_to_patent", [])[:3]:
            transitions.append(f"Research '{link.get('paper')}' → Patent {link.get('patent')}")
        
        for link in cross_refs.get("patent_to_component", [])[:3]:
            transitions.append(f"Patent {link.get('patent')} → Product {link.get('component')}")
        
        return transitions
    
    def _recommend_components(self, components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Recommend best components based on multiple criteria"""
        if not components:
            return []
        
        # Score components
        scored = []
        for comp in components:
            score = self._calculate_component_score(comp)
            scored.append((score, comp))
        
        # Sort by score
        scored.sort(key=lambda x: x[0], reverse=True)
        
        # Format recommendations
        recommendations = []
        for score, comp in scored[:5]:
            recommendations.append({
                "part_number": comp.get("part_number"),
                "manufacturer": comp.get("manufacturer"),
                "category": comp.get("category"),
                "score": round(score, 2),
                "rationale": self._explain_recommendation(comp),
                "pros": self._extract_pros(comp),
                "cons": self._extract_cons(comp),
                "typical_applications": comp.get("applications", [])
            })
        
        return recommendations
    
    def _calculate_component_score(self, component: Dict[str, Any]) -> float:
        """Calculate overall component score"""
        score = 0.0
        
        # TRL score (prefer production-ready)
        trl = component.get("trl", 0)
        if trl >= 8:
            score += 30
        elif trl >= 6:
            score += 20
        else:
            score += 10
        
        # Lifecycle score
        lifecycle = component.get("lifecycle", "")
        if lifecycle == "Active":
            score += 25
        elif lifecycle == "NRND":
            score += 5
        
        # Availability score
        sc_data = component.get("supply_chain", {})
        total_stock = sum(d.get("stock", 0) for d in sc_data.values())
        if total_stock > 1000:
            score += 20
        elif total_stock > 100:
            score += 10
        
        # Performance score (if efficiency available)
        efficiency = component.get("specs", {}).get("efficiency")
        if efficiency:
            score += (efficiency / 100) * 25
        
        return score
    
    def _explain_recommendation(self, component: Dict[str, Any]) -> str:
        """Explain why component is recommended"""
        reasons = []
        
        if component.get("trl", 0) >= 8:
            reasons.append("production-ready (TRL 8+)")
        
        if component.get("lifecycle") == "Active":
            reasons.append("active lifecycle")
        
        sc_data = component.get("supply_chain", {})
        if sum(d.get("stock", 0) for d in sc_data.values()) > 1000:
            reasons.append("good availability")
        
        efficiency = component.get("specs", {}).get("efficiency")
        if efficiency and efficiency > 90:
            reasons.append(f"high efficiency ({efficiency}%)")
        
        return "Recommended for: " + ", ".join(reasons) if reasons else "General purpose use"
    
    def _extract_pros(self, component: Dict[str, Any]) -> List[str]:
        """Extract component advantages"""
        pros = []
        
        features = component.get("features", [])
        pros.extend(features[:3])
        
        if component.get("trl", 0) >= 8:
            pros.append("Production-proven")
        
        if component.get("lifecycle") == "Active":
            pros.append("Long-term availability")
        
        return pros[:5]
    
    def _extract_cons(self, component: Dict[str, Any]) -> List[str]:
        """Extract component limitations"""
        cons = []
        
        if component.get("lifecycle") == "NRND":
            cons.append("Not recommended for new designs")
        
        sc_data = component.get("supply_chain", {})
        if sum(d.get("stock", 0) for d in sc_data.values()) < 100:
            cons.append("Limited availability")
        
        if component.get("trl", 0) < 7:
            cons.append("Not yet production-ready")
        
        pricing = component.get("pricing", {})
        unit_price = pricing.get("unit_price_usd", 0)
        if unit_price > 10:
            cons.append(f"Higher cost (${unit_price})")
        
        return cons if cons else ["None significant"]
    
    def _suggest_alternatives(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest alternative approaches"""
        alternatives = []
        
        # Alternative component families
        components = data.get("components", [])
        if components:
            categories = set(c.get("category") for c in components)
            for cat in list(categories)[:3]:
                alternatives.append({
                    "approach": f"Alternative {cat} solutions",
                    "description": f"Consider other {cat} from different manufacturers",
                    "tradeoffs": "May require different PCB layout or control scheme"
                })
        
        # Alternative technologies from patents
        patents = data.get("patents", [])
        if patents:
            alternatives.append({
                "approach": "Emerging patent technologies",
                "description": "Novel approaches identified in recent patents",
                "tradeoffs": "May not be commercially available yet"
            })
        
        return alternatives
    
    def _provide_implementation_guidance(self, data: Dict[str, Any]) -> List[str]:
        """Provide implementation guidance"""
        guidance = [
            "Review datasheets thoroughly for electrical characteristics",
            "Follow manufacturer reference designs where available",
            "Conduct thermal analysis for power components",
            "Plan for EMC/EMI compliance testing",
            "Verify supply chain before finalizing BOM",
            "Consider second sources for critical components",
            "Review application notes for design best practices"
        ]
        
        # Add specific guidance based on domain
        components = data.get("components", [])
        if any("power" in c.get("category", "").lower() for c in components):
            guidance.append("Power Management: Include proper input/output filtering")
        
        if any("emc" in c.get("category", "").lower() for c in components):
            guidance.append("EMC/EMI: Follow PCB layout guidelines strictly")
        
        return guidance
    
    def _assess_risks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess implementation risks"""
        risks = {
            "technical": [],
            "supply_chain": [],
            "commercial": []
        }
        
        # Technical risks
        low_trl = sum(1 for c in data.get("components", []) if c.get("trl", 0) < 7)
        if low_trl > 0:
            risks["technical"].append(f"{low_trl} component(s) not production-proven")
        
        # Supply chain risks
        nrnd = sum(1 for c in data.get("components", []) if c.get("lifecycle") == "NRND")
        if nrnd > 0:
            risks["supply_chain"].append(f"{nrnd} component(s) at end-of-life")
        
        # Commercial risks
        if len(data.get("patents", [])) > 20:
            risks["commercial"].append("High patent density - verify freedom to operate")
        
        return risks
    
    def _format_paper_references(self, papers: List[Dict[str, Any]]) -> List[str]:
        """Format paper references in academic style"""
        references = []
        
        for i, paper in enumerate(papers[:20], 1):
            authors = ", ".join(paper.get("authors", ["Unknown"]))
            title = paper.get("title", "Untitled")
            year = paper.get("year", "n.d.")
            journal = paper.get("journal", "")
            
            ref = f"[{i}] {authors} ({year}). {title}."
            if journal:
                ref += f" {journal}."
            
            references.append(ref)
        
        return references
    
    def _format_patent_references(self, patents: List[Dict[str, Any]]) -> List[str]:
        """Format patent references"""
        references = []
        
        for patent in patents[:20]:
            pn = patent.get("patent_number", "Unknown")
            title = patent.get("title", "Untitled")
            applicant = patent.get("applicant", "Unknown")
            date = patent.get("filing_date", "n.d.")
            
            ref = f"{pn}: {applicant}. {title}. Filed {date}."
            references.append(ref)
        
        return references
    
    def _format_datasheet_references(self, components: List[Dict[str, Any]]) -> List[str]:
        """Format datasheet references"""
        references = []
        
        for comp in components[:20]:
            pn = comp.get("part_number", "Unknown")
            mfr = comp.get("manufacturer", "Unknown")
            url = comp.get("datasheet_url", "")
            
            ref = f"{pn} Datasheet. {mfr}."
            if url:
                ref += f" Available: {url}"
            
            references.append(ref)
        
        return references
    
    def _create_detailed_specs(self, components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create detailed specification tables"""
        detailed = []
        
        for comp in components:
            detailed.append({
                "part_number": comp.get("part_number"),
                "full_specifications": comp.get("specs", {}),
                "features": comp.get("features", []),
                "package_details": comp.get("package_types", []),
                "operating_conditions": {
                    "temperature_range": comp.get("specs", {}).get("temp_range"),
                    "voltage_range": f"{comp.get('specs', {}).get('vin_min')}-{comp.get('specs', {}).get('vin_max')}V"
                }
            })
        
        return detailed
    
    def _document_methodology(self) -> Dict[str, Any]:
        """Document research methodology"""
        return {
            "search_strategy": {
                "academic": "Multi-database search (IEEE, arXiv, etc.)",
                "patents": "EU (EPO) and Asia (CNIPA, JPO) patent offices",
                "components": "Manufacturer datasheets and distributor databases",
                "supply_chain": "Real-time availability from major distributors"
            },
            "selection_criteria": {
                "regional_focus": "EU and Asia markets",
                "domain_priority": "Embedded Systems > Power Management > EMC/EMI",
                "trl_classification": "9-level scale (TRL 1-9)"
            },
            "analysis_approach": {
                "synthesis": "Cross-referencing papers, patents, and products",
                "validation": "Multiple source verification",
                "scoring": "Multi-factor component evaluation"
            }
        }
    
    def _list_data_sources(self, data: Dict[str, Any]) -> List[str]:
        """List all data sources used"""
        sources = [
            "Academic: IEEE Xplore, arXiv, academic journals",
            "Patents: EPO (European Patent Office), CNIPA (China), JPO (Japan)",
            "Components: Manufacturer websites and datasheets",
            "Supply Chain: Octopart, Digi-Key, Mouser, LCSC",
            "Standards: IEC, CENELEC, GB standards"
        ]
        return sources
    
    def _suggest_next_steps(self, data: Dict[str, Any]) -> List[str]:
        """Suggest next steps for user"""
        steps = [
            "Review recommended components and download datasheets",
            "Contact distributors for volume pricing and lead times",
            "Begin preliminary design with top candidates",
            "Plan for prototype testing and validation"
        ]
        
        # Add specific steps based on findings
        if data.get("components"):
            steps.append("Request evaluation boards from manufacturers")
        
        if any(c.get("trl", 0) < 7 for c in data.get("components", [])):
            steps.append("Consider waiting for production-ready alternatives")
        
        return steps