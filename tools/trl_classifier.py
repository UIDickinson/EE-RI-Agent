from typing import Dict, Any, Optional
import re

class TRLClassifier:
    """
    Classifies technology readiness based on multiple evidence sources
    
    TRL Scale:
    1-3: Basic research
    4-6: Development and validation
    7-9: Production and deployment
    """
    
    def __init__(self):
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
        
        # Keywords that indicate different TRL levels
        self.trl_indicators = {
            1: ["theoretical", "principle", "basic research", "hypothesis"],
            2: ["concept", "feasibility", "proposed", "initial design"],
            3: ["experiment", "proof of concept", "lab test", "prototype"],
            4: ["laboratory validation", "component test", "bench test"],
            5: ["field test", "relevant environment", "pilot"],
            6: ["prototype demonstration", "system test", "beta"],
            7: ["pre-production", "qualification", "operational test"],
            8: ["production", "qualified", "certified", "compliant"],
            9: ["deployed", "commercial", "mass production", "proven"]
        }
    
    async def classify(self, component: Dict[str, Any]) -> int:
        """
        Classify component TRL based on available data
        
        Evidence hierarchy:
        1. Explicit TRL if already classified
        2. Lifecycle status
        3. Supply chain availability
        4. Specifications completeness
        """
        # Check if already classified
        if "trl" in component:
            return component["trl"]
        
        # Check lifecycle (strongest indicator)
        lifecycle = component.get("lifecycle", "").lower()
        if lifecycle == "active":
            # Active in production = TRL 8-9
            return self._classify_from_supply_chain(component)
        elif lifecycle == "nrnd":
            return 8  # Was production-ready
        elif lifecycle == "obsolete":
            return 9  # Was fully deployed
        
        # Check supply chain availability
        if component.get("supply_chain"):
            return self._classify_from_supply_chain(component)
        
        # Check if datasheet exists (indicates at least TRL 7)
        if component.get("datasheet_url"):
            return 7
        
        # Default to mid-range if insufficient data
        return 5
    
    def _classify_from_supply_chain(self, component: Dict[str, Any]) -> int:
        """Classify based on supply chain data"""
        sc_data = component.get("supply_chain", {})
        
        if not sc_data:
            return 6
        
        # Check total stock across distributors
        total_stock = 0
        distributor_count = 0
        
        for dist, data in sc_data.items():
            stock = data.get("stock", 0)
            total_stock += stock
            if stock > 0:
                distributor_count += 1
        
        # High availability = TRL 9 (proven in operations)
        if total_stock > 1000 and distributor_count >= 2:
            return 9
        
        # Available but limited = TRL 8 (qualified)
        if total_stock > 100:
            return 8
        
        # Low stock = TRL 7 (prototype/pre-production)
        return 7
    
    async def classify_from_paper(self, paper: Dict[str, Any]) -> int:
        """Classify TRL based on academic paper content"""
        text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
        
        # Check for TRL indicators in text
        for trl in range(9, 0, -1):  # Check from highest to lowest
            indicators = self.trl_indicators.get(trl, [])
            if any(indicator in text for indicator in indicators):
                return trl
        
        # Papers typically describe TRL 1-3 research
        return 2
    
    async def classify_from_patent(self, patent: Dict[str, Any]) -> int:
        """Classify TRL based on patent content"""
        text = f"{patent.get('title', '')} {patent.get('abstract', '')}".lower()
        status = patent.get("status", "").lower()
        
        # Granted patents typically TRL 4-6 (validated concepts)
        if "granted" in status:
            base_trl = 5
        else:
            base_trl = 4
        
        # Check for higher TRL indicators
        for trl in range(9, base_trl, -1):
            indicators = self.trl_indicators.get(trl, [])
            if any(indicator in text for indicator in indicators):
                return trl
        
        return base_trl
    
    def get_justification(self, component: Dict[str, Any], trl: int) -> str:
        """Generate justification for TRL classification"""
        reasons = []
        
        lifecycle = component.get("lifecycle", "")
        if lifecycle == "Active":
            reasons.append("Active production status")
        
        sc_data = component.get("supply_chain", {})
        if sc_data:
            total_stock = sum(d.get("stock", 0) for d in sc_data.values())
            if total_stock > 1000:
                reasons.append(f"High availability ({total_stock} units in stock)")
            elif total_stock > 0:
                reasons.append(f"Available from multiple distributors")
        
        if component.get("datasheet_url"):
            reasons.append("Published datasheet available")
        
        if component.get("applications"):
            reasons.append("Documented application use cases")
        
        if not reasons:
            reasons.append("Based on typical component characteristics")
        
        return f"TRL {trl}: {', '.join(reasons)}"
    
    def get_trl_description(self, trl: int) -> str:
        """Get description for TRL level"""
        return self.trl_definitions.get(trl, "Unknown TRL level")