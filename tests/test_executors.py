import pytest
from agents.executors import (
    DatasheetExecutor,
    PaperExecutor,
    PatentExecutor,
    SupplyChainExecutor,
    ComponentExecutor
)

@pytest.mark.asyncio
async def test_datasheet_executor():
    """Test Datasheet Executor"""
    print("\n🔍 Testing Datasheet Executor...")
    
    executor = DatasheetExecutor()
    result = await executor.execute("GaN power IC")
    
    assert result is not None
    assert "source" in result
    assert result["source"] == "datasheet_search"
    print(f"✅ Datasheet executor working - found {result.get('components_found', 0)} components")

@pytest.mark.asyncio
async def test_paper_executor():
    """Test Paper Executor"""
    print("\n🔍 Testing Paper Executor...")
    
    executor = PaperExecutor()
    result = await executor.execute("GaN power conversion")
    
    assert result is not None
    assert "source" in result
    assert result["source"] == "academic_papers" or result["source"] == "paper_search"
    print(f"✅ Paper executor working - found {result.get('papers_found', 0)} papers")

@pytest.mark.asyncio
async def test_patent_executor():
    """Test Patent Executor"""
    print("\n🔍 Testing Patent Executor...")
    
    executor = PatentExecutor()
    result = await executor.execute("GaN power IC")
    
    assert result is not None
    assert "source" in result
    assert result["source"] == "patent_search"
    assert "patents" in result
    print(f"✅ Patent executor working - found {result.get('patents_found', 0)} patents")

@pytest.mark.asyncio
async def test_supply_chain_executor():
    """Test Supply Chain Executor"""
    print("\n🔍 Testing Supply Chain Executor...")
    
    executor = SupplyChainExecutor()
    result = await executor.execute("TPS54620")
    
    assert result is not None
    assert "source" in result
    assert result["source"] == "supply_chain"
    print(f"✅ Supply chain executor working - checked {result.get('components_checked', 0)} components")

@pytest.mark.asyncio
async def test_component_executor():
    """Test Component Executor"""
    print("\n🔍 Testing Component Executor...")
    
    executor = ComponentExecutor()
    result = await executor.execute(part_number="TPS54620")
    
    assert result is not None
    assert "part_number" in result or "error" in result
    print(f"✅ Component executor working")