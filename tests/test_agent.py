import pytest
from agents import create_ee_agent, get_agent_info

def test_agent_creation():
    """Test Agent Creation"""
    print("\n🔍 Testing Agent Creation...")
    
    agent = create_ee_agent(debug=True)
    
    assert agent is not None
    assert agent.name == "EE Research Scout"
    print("✅ Agent created successfully")

def test_agent_info():
    """Test Agent Info"""
    print("\n🔍 Testing Agent Info...")
    
    info = get_agent_info()
    
    assert info["name"] == "EE Research & Innovation Scout"
    assert "Embedded Systems" in info["domains"]
    assert "EU" in info["regions"]
    print("✅ Agent info retrieved successfully")

@pytest.mark.asyncio
async def test_agent_atomic_query():
    """Test Agent Atomic Query Detection"""
    print("\n🔍 Testing Agent Atomic Query...")
    
    agent = create_ee_agent(debug=True)
    
    # This should be detected as atomic
    atomic_query = "datasheet for TPS54620"
    is_atomic = agent.is_atomic(atomic_query)
    
    assert is_atomic == True
    print("✅ Atomic query detected correctly")

@pytest.mark.asyncio
async def test_agent_complex_query():
    """Test Agent Complex Query Detection"""
    print("\n🔍 Testing Agent Complex Query...")
    
    agent = create_ee_agent(debug=True)
    
    # This should NOT be atomic
    complex_query = "Find the latest GaN power ICs for 48V automotive applications"
    is_atomic = agent.is_atomic(complex_query)
    
    assert is_atomic == False
    print("✅ Complex query detected correctly")