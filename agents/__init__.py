from .ee_research_agent import EEResearchAgent, create_ee_agent

# Import planners
from .planners import EEPlanner, TRLPlanner, select_planner

# Import executors
from .executors import (
    DatasheetExecutor,
    PaperExecutor,
    PatentExecutor,
    SupplyChainExecutor,
    ComponentExecutor
)

# Import aggregators
from .aggregators import EEAggregator, ReportGenerator

__version__ = "1.0.0"

__all__ = [
    # Main agent
    "EEResearchAgent",
    "create_ee_agent",
    
    # Planners
    "EEPlanner",
    "TRLPlanner",
    "select_planner",
    
    # Executors
    "DatasheetExecutor",
    "PaperExecutor",
    "PatentExecutor",
    "SupplyChainExecutor",
    "ComponentExecutor",
    
    # Aggregators
    "EEAggregator",
    "ReportGenerator",
]

# Agent metadata
AGENT_INFO = {
    "name": "EE Research & Innovation Scout",
    "version": __version__,
    "description": "ROMA-powered research agent for Electrical/Electronics Engineers",
    "domains": [
        "Embedded Systems",
        "Power Management ICs",
        "EMC/EMI Solutions",
        "Analog/Mixed-Signal",
        "RF/Wireless"
    ],
    "regions": ["EU", "Asia"],
    "capabilities": [
        "Multi-source research (papers, patents, datasheets)",
        "TRL classification (1-9 scale)",
        "Supply chain monitoring",
        "Knowledge graph construction",
        "Academic-grade report generation"
    ]
}

def get_agent_info():
    """Get agent metadata"""
    return AGENT_INFO

def list_available_planners():
    """List all available planners"""
    return {
        "EEPlanner": "General EE research query planner",
        "TRLPlanner": "Technology readiness assessment planner"
    }

def list_available_executors():
    """List all available executors"""
    return {
        "DatasheetExecutor": "Search and parse component datasheets",
        "PaperExecutor": "Search academic papers",
        "PatentExecutor": "Search EU/Asia patents",
        "SupplyChainExecutor": "Check component availability and pricing",
        "ComponentExecutor": "Get comprehensive component information"
    }
