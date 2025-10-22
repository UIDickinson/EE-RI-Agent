import os
import sys
from typing import Dict, Any, List, Optional

# Add ROMA to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'roma'))

from agno import Agent
from agno.models.openai import OpenAIChat

from planners.ee_planner import EEPlanner
from aggregators.ee_aggregator import EEAggregator
from executors.datasheet_executor import DatasheetExecutor
from executors.paper_executor import PaperExecutor
from executors.patent_executor import PatentExecutor
from executors.supply_chain_executor import SupplyChainExecutor
from agents.planners.ee_planner import select_planner

class EEResearchAgent(Agent):
    async def run_query(self, query: str) -> Dict[str, Any]:
        # Dynamically select the right planner
        self.planner = select_planner(query)
        
    """
    Recursive agent for EE research following ROMA architecture:
    - Atomizer: Determines if query needs decomposition
    - Planner: Breaks into EE-specific subtasks
    - Executors: Handle atomic tasks (datasheet search, papers, etc.)
    - Aggregator: Synthesizes findings into academic reports
    """
    
    def __init__(
        self,
        model: str = "gpt-4-turbo-preview",
        debug: bool = False,
        **kwargs
    ):
        # Initialize executors (tools)
        self.datasheet_executor = DatasheetExecutor()
        self.paper_executor = PaperExecutor()
        self.patent_executor = PatentExecutor()
        self.supply_chain_executor = SupplyChainExecutor()
        
        # Initialize custom planner and aggregator
        planner = EEPlanner()
        aggregator = EEAggregator()
        
        super().__init__(
            name="EE Research Scout",
            model=OpenAIChat(id=model),
            description=(
                "Specialized research agent for Electrical/Electronics Engineers. "
                "Focuses on Power Management ICs, EMC/EMI solutions, and Embedded Systems. "
                "Provides academic-grade technical analysis with TRL classification."
            ),
            instructions=[
                "You are an expert EE research agent.",
                "Focus on EU/Asia regions for component availability.",
                "Prioritize Embedded Systems, Power Management, and EMC/EMI solutions.",
                "Classify all findings by Technology Readiness Level (TRL 1-9).",
                "Generate academic-quality reports with proper citations.",
                "Only respond to queries - never stream or push information."
            ],
            planner=planner,
            aggregator=aggregator,
            tools=[
                self.datasheet_executor,
                self.paper_executor,
                self.patent_executor,
                self.supply_chain_executor
            ],
            markdown=True,
            debug_mode=debug,
            show_tool_calls=debug,
            **kwargs
        )
    
    def is_atomic(self, task: str) -> bool:
        """
        Atomizer: Determine if task is atomic (directly executable)
        or needs decomposition
        """
        # Simple queries that can be handled directly by executors
        atomic_patterns = [
            "datasheet for",
            "price of",
            "availability of",
            "specifications of"
        ]
        
        return any(pattern in task.lower() for pattern in atomic_patterns)
    
    async def execute_atomic(self, task: str) -> Dict[str, Any]:
        """Execute atomic task using appropriate executor"""
        task_lower = task.lower()
        
        if "datasheet" in task_lower:
            return await self.datasheet_executor.execute(task)
        elif "paper" in task_lower or "research" in task_lower:
            return await self.paper_executor.execute(task)
        elif "patent" in task_lower:
            return await self.patent_executor.execute(task)
        elif "price" in task_lower or "availability" in task_lower:
            return await self.supply_chain_executor.execute(task)
        else:
            # Default to paper search
            return await self.paper_executor.execute(task)
    
    async def run_query(self, query: str) -> Dict[str, Any]:
        """
        Main entry point for EE research queries
        Follows ROMA's recursive solve pattern
        """
        # Check if atomic
        if self.is_atomic(query):
            result = await self.execute_atomic(query)
            return {"type": "atomic", "result": result}
        
        # Complex query - use ROMA's recursive planning
        response = await self.run(query)
        
        return {
            "type": "complex",
            "result": response
        }


# Factory function for easy instantiation
def create_ee_agent(debug: bool = False) -> EEResearchAgent:
    """Create and return configured EE Research Agent"""
    return EEResearchAgent(debug=debug)