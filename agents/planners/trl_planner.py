from typing import List, Dict, Any
from agno.planner import Planner

class TRLPlanner(Planner):
    """
    Specialized planner for TRL-focused queries
    
    Use cases:
    - "What's the maturity level of GaN technology?"
    - "Are there production-ready solutions for X?"
    - "Compare TRL of different approaches"
    """
    
    def __init__(self):
        super().__init__(
            name="TRL Classification Planner",
            description="Plans tasks for technology readiness assessment"
        )
        
        # TRL classification criteria
        self.trl_levels = {
            1: "Basic principles observed",
            2: "Technology concept formulated",
            3: "Experimental proof of concept",
            4: "Technology validated in lab",
            5: "Technology validated in relevant environment",
            6: "Technology demonstrated in relevant environment",
            7: "System prototype in operational environment",
            8: "System complete and qualified",
            9: "Actual system proven in operational environment"
        }
    
    async def plan(self, task: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Create plan for TRL assessment
        
        Strategy:
        1. Identify technology/component to assess
        2. Search academic papers (TRL 1-3 indicators)
        3. Search patents (TRL 4-6 indicators)
        4. Search commercial products (TRL 7-9 indicators)
        5. Check supply chain (TRL 8-9 validation)
        6. Synthesize TRL classification
        """
        
        # Extract technology/component from task
        technology = self._extract_technology(task)
        
        subtasks = []
        
        # Task 1: Academic Research (Early TRL indicators)
        subtasks.append({
            "id": "academic_trl_search",
            "description": f"Search academic papers about {technology} to identify early-stage research (TRL 1-3)",
            "executor": "paper_executor",
            "priority": 1,
            "dependencies": [],
            "trl_focus": [1, 2, 3]
        })
        
        # Task 2: Patent Analysis (Mid TRL indicators)
        subtasks.append({
            "id": "patent_trl_search",
            "description": f"Search patents for {technology} to identify prototypes and validation (TRL 4-6)",
            "executor": "patent_executor",
            "priority": 1,
            "dependencies": [],
            "trl_focus": [4, 5, 6]
        })
        
        # Task 3: Commercial Product Search (High TRL indicators)
        subtasks.append({
            "id": "product_trl_search",
            "description": f"Search for commercial {technology} products (TRL 7-9)",
            "executor": "datasheet_executor",
            "priority": 1,
            "dependencies": [],
            "trl_focus": [7, 8, 9]
        })
        
        # Task 4: Supply Chain Validation (TRL 8-9 confirmation)
        subtasks.append({
            "id": "supply_chain_trl_check",
            "description": f"Check supply chain availability for {technology} to confirm production status",
            "executor": "supply_chain_executor",
            "priority": 2,
            "dependencies": ["product_trl_search"],
            "trl_focus": [8, 9]
        })
        
        # Task 5: TRL Classification Synthesis
        subtasks.append({
            "id": "trl_synthesis",
            "description": f"Synthesize TRL classification for {technology} based on all evidence",
            "executor": "trl_classifier",
            "priority": 3,
            "dependencies": ["academic_trl_search", "patent_trl_search", "product_trl_search", "supply_chain_trl_check"]
        })
        
        return subtasks
    
    def _extract_technology(self, task: str) -> str:
        """Extract technology/component name from task"""
        # Simple extraction - can be enhanced with NER
        task_lower = task.lower()
        
        # Remove common question words
        remove_words = ["what", "is", "the", "maturity", "level", "of", "trl", "for", "readiness"]
        words = [w for w in task.split() if w.lower() not in remove_words]
        
        return " ".join(words) if words else task
    
    def get_trl_criteria(self, trl_level: int) -> str:
        """Get criteria for specific TRL level"""
        return self.trl_levels.get(trl_level, "Unknown TRL level")
    
    def suggest_evidence_types(self, trl_level: int) -> List[str]:
        """Suggest what evidence is needed for each TRL"""
        evidence_map = {
            1: ["Scientific papers", "Theoretical models"],
            2: ["Concept papers", "Feasibility studies"],
            3: ["Lab experiment results", "Proof-of-concept demos"],
            4: ["Lab validation reports", "Component testing data"],
            5: ["Field test results", "Relevant environment data"],
            6: ["Prototype demonstrations", "Beta testing results"],
            7: ["Pre-production prototypes", "System integration tests"],
            8: ["Production qualification data", "Reliability testing"],
            9: ["Commercial products", "Customer deployments", "Supply chain data"]
        }
        return evidence_map.get(trl_level, [])
