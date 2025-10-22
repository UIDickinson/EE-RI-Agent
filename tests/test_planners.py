import pytest
from agents.planners import EEPlanner, TRLPlanner, select_planner

@pytest.mark.asyncio
async def test_ee_planner():
    """Test EE Planner"""
    print("\n🔍 Testing EE Planner...")
    
    planner = EEPlanner()
    task = "Find GaN power ICs for 48V automotive applications"
    
    subtasks = await planner.plan(task)
    
    assert len(subtasks) > 0
    assert any(st["id"] == "academic_search" for st in subtasks)
    assert any(st["id"] == "patent_search" for st in subtasks)
    print(f"✅ EE Planner working - generated {len(subtasks)} subtasks")
    
    for st in subtasks:
        print(f"  - {st['id']}: {st['description'][:60]}...")

@pytest.mark.asyncio
async def test_trl_planner():
    """Test TRL Planner"""
    print("\n🔍 Testing TRL Planner...")
    
    planner = TRLPlanner()
    task = "What is the maturity level of GaN power technology?"
    
    subtasks = await planner.plan(task)
    
    assert len(subtasks) > 0
    assert any("trl" in st["id"].lower() for st in subtasks)
    print(f"✅ TRL Planner working - generated {len(subtasks)} subtasks")

def test_planner_selection():
    """Test Planner Selection Logic"""
    print("\n🔍 Testing Planner Selection...")
    
    # Should select TRL Planner
    trl_query = "What's the maturity level of GaN technology?"
    planner = select_planner(trl_query)
    assert planner.__class__.__name__ == "TRLPlanner"
    print("✅ TRL query correctly routed to TRLPlanner")
    
    # Should select EE Planner
    ee_query = "Find buck converters for automotive"
    planner = select_planner(ee_query)
    assert planner.__class__.__name__ == "EEPlanner"
    print("✅ EE query correctly routed to EEPlanner")