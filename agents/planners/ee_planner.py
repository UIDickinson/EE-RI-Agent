from typing import List, Dict, Any
from agno.planner import Planner

class EEPlanner(Planner):
    """
    EE-specific query planner
    Breaks queries into: Academic Search, Patent Analysis, 
    Component Search, Supply Chain Check
    """
    
    def __init__(self):
        super().__init__(
            name="EE Query Planner",
            description="Decomposes EE research queries into parallel tasks"
        )
        
        # Domain prioritization
        self.priority_domains = {
            "embedded_systems": "HIGH",
            "power_management": "HIGH",
            "emc_emi": "HIGH",
            "analog": "MEDIUM",
            "rf_wireless": "MEDIUM"
        }
    
    async def plan(self, task: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Decompose EE query into subtasks
        Returns list of subtasks with dependencies
        """
        # Extract key terms and domain
        domain = self._identify_domain(task)
        components = self._extract_components(task)
        
        # Standard decomposition for EE queries
        subtasks = []
        
        # Task 1: Academic Research (papers, conferences)
        subtasks.append({
            "id": "academic_search",
            "description": f"Search academic papers and conference proceedings about: {task}",
            "executor": "paper_executor",
            "priority": 1,
            "dependencies": []
        })
        
        # Task 2: Patent Analysis (concurrent with Task 1)
        subtasks.append({
            "id": "patent_search",
            "description": f"Search patents related to: {task}",
            "executor": "patent_executor",
            "priority": 1,
            "dependencies": []
        })
        
        # Task 3: Component Search (depends on domain understanding)
        if components:
            subtasks.append({
                "id": "component_search",
                "description": f"Find datasheets and specifications for: {', '.join(components)}",
                "executor": "datasheet_executor",
                "priority": 2,
                "dependencies": ["academic_search"]  # Wait for context
            })
        
        # Task 4: Supply Chain Analysis (depends on components)
        if components:
            subtasks.append({
                "id": "supply_chain",
                "description": f"Check availability, pricing, and lifecycle for: {', '.join(components)}",
                "executor": "supply_chain_executor",
                "priority": 3,
                "dependencies": ["component_search"]
            })
        
        # Task 5: TRL Classification (depends on all research)
        subtasks.append({
            "id": "trl_classification",
            "description": "Classify findings by Technology Readiness Level",
            "executor": "trl_classifier",
            "priority": 4,
            "dependencies": ["academic_search", "patent_search", "component_search"]
        })
        
        return subtasks
    
    def _identify_domain(self, query: str) -> str:
        """Identify primary EE domain from query"""
        query_lower = query.lower()
        
        domain_keywords = {
            "embedded_systems": ["mcu", "microcontroller", "embedded", "rtos", "firmware"],
            "power_management": ["pmic", "power", "converter", "regulator", "gan", "sic"],
            "emc_emi": ["emc", "emi", "filter", "shielding", "noise"],
            "analog": ["adc", "dac", "opamp", "analog"],
            "rf_wireless": ["rf", "wireless", "ble", "lora", "antenna"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(kw in query_lower for kw in keywords):
                return domain
        
        return "general"
    
    def _extract_components(self, query: str) -> List[str]:
        """Extract component names/types from query"""
        # Simple keyword extraction (can be enhanced with NER)
        component_types = [
            "ic", "mcu", "pmic", "converter", "regulator",
            "mosfet", "gan", "sic", "adc", "dac"
        ]
        
        found_components = []
        query_lower = query.lower()
        
        for comp in component_types:
            if comp in query_lower:
                found_components.append(comp.upper())
        
        return found_components

def select_planner(query: str):
    """
    Dynamically select the most appropriate planner based on query content
    
    This function analyzes the query and returns the optimal planner:
    - TRL-focused queries → TRLPlanner
    - General EE queries → EEPlanner
    
    Args:
        query: User's research query
        
    Returns:
        Planner instance (EEPlanner or TRLPlanner)
        
    Example:
        >>> planner = select_planner("What's the maturity level of GaN technology?")
        >>> # Returns TRLPlanner instance
        
        >>> planner = select_planner("Find GaN power ICs for automotive")
        >>> # Returns EEPlanner instance
    """
    from .trl_planner import TRLPlanner
    
    query_lower = query.lower()
    
    # TRL-focused keywords
    trl_keywords = [
        "maturity", "trl", "readiness", "production-ready", 
        "commercial", "available", "proven", "mature",
        "deployment", "operational", "qualified"
    ]
    
    # Check if query is TRL-focused
    if any(keyword in query_lower for keyword in trl_keywords):
        return TRLPlanner()
    
    # Default to EE Planner for general queries
    return EEPlanner()