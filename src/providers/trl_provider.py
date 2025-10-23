from typing import Dict, Any, Optional
import logging
from .base_provider import BaseProvider

logger = logging.getLogger(__name__)

class TRLProvider(BaseProvider):
    """
    Technology Readiness Level (TRL) classification provider
    
    TRL Scale:
    1-3: Basic research and concept
    4-6: Development and validation
    7-9: Production and deployment
    """
    
    def __init__(self):
        super().__init__("TRLProvider")
        
        self.trl_definitions = {
            1: "Basic principles observed and reported",
            2: "Technology concept and/or application formulated",
            3: "Analytical and experimental critical function proof of concept",
            4: "Component validation in laboratory environment",
            5: "Component validation in relevant environment",
            6: "System/subsystem model or prototype in relevant environment",
            7: "System prototype demonstration in operational environment",
            8: "Actual system completed and qualified through test and demonstration",
            9: "Actual system proven through successful mission operations"
        }
        
        # Keywords indicating different TRL levels
        self.trl_indicators = {
            1: ["theoretical", "principle", "basic research", "hypothesis", "concept"],
            2: ["concept", "feasibility", "proposed", "initial design", "formulated"],
            3: ["experiment", "proof of concept", "lab test", "prototype", "demonstration"],
            4: ["laboratory validation", "component test", "bench test", "validated"],
            5: ["field test", "relevant environment", "pilot", "validation"],
            6: ["prototype demonstration", "system test", "beta", "engineering"],
            7: ["pre-production", "qualification", "operational test", "prototype"],
            8: ["production", "qualified", "certified", "compliant", "manufacturing"],
            9: ["deployed", "commercial", "mass production", "proven", "operational"]
        }
        
        # Evidence weights for multi-source classification
        self.evidence_weights = {
            "supply_chain": 0.4,
            "datasheet": 0.3,
            "patent": 0.2,
            "paper": 0.1
        }
    
    async def fetch(
        self,
        component: Dict[str, Any] = None,
        paper: Dict[str, Any] = None,
        patent: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Classify TRL based on available evidence
        
        Args:
            component: Component data with supply chain info
            paper: Academic paper data
            patent: Patent data
        """
        try:
            if component:
                trl, confidence, justification = await self._classify_component(component)
                entity_type = "component"
                entity_id = component.get("part_number", "unknown")
            
            elif paper:
                trl, confidence, justification = await self._classify_paper(paper)
                entity_type = "paper"
                entity_id = paper.get("title", "unknown")
            
            elif patent:
                trl, confidence, justification = await self._classify_patent(patent)
                entity_type = "patent"
                entity_id = patent.get("patent_number", "unknown")
            
            else:
                raise ValueError("No data provided for TRL classification")
            
            return self._create_response(
                success=True,
                data={
                    "trl": trl,
                    "confidence": confidence,
                    "justification": justification,
                    "definition": self.trl_definitions.get(trl),
                    "entity_type": entity_type,
                    "entity_id": entity_id
                }
            )
        
        except Exception as e:
            logger.error(f"TRL classification error: {str(e)}")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    async def _classify_component(
        self,
        component: Dict[str, Any]
    ) -> tuple[int, float, str]:
        """
        Classify component TRL based on supply chain and lifecycle data
        
        Returns:
            (trl_level, confidence, justification)
        """
        reasons = []
        trl = 5  # Default mid-range
        
        # 1. Check lifecycle status (strongest indicator)
        lifecycle = component.get("lifecycle", "").lower()
        
        if lifecycle == "active":
            # Check supply chain for production volume
            availability = component.get("availability", {})
            total_stock = sum(
                dist.get("stock", 0) 
                for dist in availability.values()
            )
            
            distributor_count = len([
                d for d in availability.values() 
                if d.get("stock", 0) > 0
            ])
            
            if total_stock > 1000 and distributor_count >= 2:
                trl = 9
                reasons.append(f"Mass production: {total_stock} units across {distributor_count} distributors")
            elif total_stock > 100:
                trl = 8
                reasons.append(f"Production qualified: {total_stock} units available")
            else:
                trl = 7
                reasons.append("Active lifecycle with limited production")
        
        elif lifecycle == "nrnd":
            trl = 8
            reasons.append("Not recommended for new design (was production-ready)")
        
        elif lifecycle == "obsolete":
            trl = 9
            reasons.append("Obsolete (was fully deployed)")
        
        # 2. Check datasheet availability
        if component.get("datasheet_url"):
            if trl < 7:
                trl = 7
            reasons.append("Published datasheet available")
        
        # 3. Check specifications completeness
        specs = component.get("specifications", {})
        if len(specs) > 5:
            reasons.append(f"Comprehensive specifications ({len(specs)} parameters)")
        
        # 4. Check application notes
        if component.get("applications"):
            reasons.append(f"Documented applications: {len(component.get('applications'))}")
        
        # Calculate confidence based on available evidence
        confidence = 0.6  # Base confidence
        
        if lifecycle in ["active", "nrnd", "obsolete"]:
            confidence += 0.2
        
        if component.get("availability"):
            confidence += 0.1
        
        if component.get("datasheet_url"):
            confidence += 0.1
        
        confidence = min(confidence, 1.0)
        
        justification = f"TRL {trl}: " + "; ".join(reasons)
        
        return trl, confidence, justification
    
    async def _classify_paper(self, paper: Dict[str, Any]) -> tuple[int, float, str]:
        """
        Classify TRL from academic paper
        
        Papers typically indicate early TRL (1-3)
        """
        text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
        
        # Check for TRL indicators in text
        detected_trl = 2  # Default for papers
        confidence = 0.5
        reasons = []
        
        # Scan from highest to lowest TRL
        for trl in range(9, 0, -1):
            indicators = self.trl_indicators.get(trl, [])
            matches = [ind for ind in indicators if ind in text]
            
            if matches:
                detected_trl = trl
                reasons.append(f"Indicators: {', '.join(matches[:3])}")
                confidence = 0.6 + (len(matches) * 0.05)
                break
        
        # Papers rarely describe TRL > 6
        if detected_trl > 6:
            detected_trl = min(detected_trl, 6)
            reasons.append("Adjusted: papers typically describe TRL ≤ 6")
        
        reasons.append("Source: academic paper")
        
        confidence = min(confidence, 0.8)  # Papers have inherent uncertainty
        justification = f"TRL {detected_trl}: " + "; ".join(reasons)
        
        return detected_trl, confidence, justification
    
    async def _classify_patent(self, patent: Dict[str, Any]) -> tuple[int, float, str]:
        """
        Classify TRL from patent
        
        Patents typically indicate mid TRL (4-6)
        """
        text = f"{patent.get('title', '')} {patent.get('abstract', '')}".lower()
        status = patent.get("status", "").lower()
        
        # Base TRL from patent status
        if "granted" in status:
            base_trl = 5
            confidence = 0.7
            reasons = ["Granted patent"]
        else:
            base_trl = 4
            confidence = 0.6
            reasons = ["Pending patent"]
        
        # Check for higher TRL indicators
        for trl in range(9, base_trl, -1):
            indicators = self.trl_indicators.get(trl, [])
            matches = [ind for ind in indicators if ind in text]
            
            if matches:
                base_trl = trl
                reasons.append(f"Indicators: {', '.join(matches[:2])}")
                confidence += 0.1
                break
        
        # Patents rarely describe TRL > 7
        if base_trl > 7:
            base_trl = 7
            reasons.append("Adjusted: patents typically describe TRL ≤ 7")
        
        confidence = min(confidence, 0.85)
        justification = f"TRL {base_trl}: " + "; ".join(reasons)
        
        return base_trl, confidence, justification
    
    async def classify_batch(
        self,
        components: list = None,
        papers: list = None,
        patents: list = None
    ) -> Dict[str, Any]:
        """
        Classify multiple items in batch
        
        Returns TRL distribution and analysis
        """
        classifications = []
        
        if components:
            for comp in components:
                result = await self.fetch(component=comp)
                if result.get("success"):
                    classifications.append({
                        "type": "component",
                        "id": comp.get("part_number"),
                        "trl": result["data"]["trl"]
                    })
        
        if papers:
            for paper in papers:
                result = await self.fetch(paper=paper)
                if result.get("success"):
                    classifications.append({
                        "type": "paper",
                        "id": paper.get("title", "")[:50],
                        "trl": result["data"]["trl"]
                    })
        
        if patents:
            for patent in patents:
                result = await self.fetch(patent=patent)
                if result.get("success"):
                    classifications.append({
                        "type": "patent",
                        "id": patent.get("patent_number"),
                        "trl": result["data"]["trl"]
                    })
        
        # Generate distribution
        distribution = self._calculate_distribution(classifications)
        
        return self._create_response(
            success=True,
            data={
                "classifications": classifications,
                "distribution": distribution,
                "analysis": self._analyze_distribution(distribution)
            }
        )
    
    def _calculate_distribution(self, classifications: list) -> Dict[str, int]:
        """Calculate TRL distribution"""
        distribution = {f"TRL {i}": 0 for i in range(1, 10)}
        
        for item in classifications:
            trl = item.get("trl")
            if trl:
                distribution[f"TRL {trl}"] += 1
        
        return distribution
    
    def _analyze_distribution(self, distribution: Dict[str, int]) -> Dict[str, Any]:
        """Analyze TRL distribution"""
        total = sum(distribution.values())
        
        if total == 0:
            return {"status": "no_data"}
        
        # Calculate phase percentages
        research = sum(distribution[f"TRL {i}"] for i in range(1, 4)) / total * 100
        development = sum(distribution[f"TRL {i}"] for i in range(4, 7)) / total * 100
        production = sum(distribution[f"TRL {i}"] for i in range(7, 10)) / total * 100
        
        # Determine overall maturity
        if production > 60:
            maturity = "Mature - predominantly production-ready solutions"
        elif development > 50:
            maturity = "Active development - solutions approaching market"
        elif research > 50:
            maturity = "Early research - mostly experimental solutions"
        else:
            maturity = "Mixed maturity - solutions at various stages"
        
        return {
            "maturity_phases": {
                "research (TRL 1-3)": f"{research:.1f}%",
                "development (TRL 4-6)": f"{development:.1f}%",
                "production (TRL 7-9)": f"{production:.1f}%"
            },
            "overall_maturity": maturity,
            "total_classified": total
        }
    
    def get_trl_description(self, trl: int) -> str:
        """Get description for TRL level"""
        return self.trl_definitions.get(trl, "Unknown TRL level")
    
    def get_evidence_requirements(self, trl: int) -> list:
        """Get evidence requirements for specific TRL"""
        evidence_map = {
            1: ["Scientific papers", "Theoretical models"],
            2: ["Concept papers", "Feasibility studies"],
            3: ["Lab experiments", "Proof-of-concept demos"],
            4: ["Lab validation reports", "Component testing"],
            5: ["Field tests", "Relevant environment data"],
            6: ["Prototype demonstrations", "Beta testing"],
            7: ["Pre-production units", "System integration tests"],
            8: ["Production qualification", "Reliability testing"],
            9: ["Commercial products", "Customer deployments", "Supply chain data"]
        }
        return evidence_map.get(trl, [])
    
    def validate_response(self, response: Any) -> bool:
        """Validate TRL response"""
        if not isinstance(response, dict):
            return False
        
        data = response.get("data", {})
        trl = data.get("trl")
        
        return trl is not None and 1 <= trl <= 9