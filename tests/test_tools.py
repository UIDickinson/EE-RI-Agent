import pytest
from tools.knowledge_graph import KnowledgeGraphManager
from tools.trl_classifier import TRLClassifier
from tools.regional_filter import filter_by_region, get_regional_distributors

@pytest.mark.asyncio
async def test_knowledge_graph_connection():
    """Test Knowledge Graph Manager connection"""
    print("\n🔍 Testing Knowledge Graph Manager...")
    
    kg = KnowledgeGraphManager()
    await kg.connect()
    
    # Test adding a simple research session
    test_data = {
        "query": "Test GaN power ICs",
        "papers": [
            {
                "title": "Test Paper",
                "doi": "10.1234/test",
                "authors": ["Test Author"],
                "year": 2024,
                "abstract": "Test abstract",
                "url": "https://test.com"
            }
        ],
        "patents": [],
        "components": [],
        "cross_references": {}
    }
    
    await kg.add_research_session(
        query=test_data["query"],
        papers=test_data["papers"],
        patents=test_data["patents"],
        components=test_data["components"],
        cross_references=test_data["cross_references"]
    )
    
    print("✅ Knowledge Graph operations working")
    await kg.close()

@pytest.mark.asyncio
async def test_trl_classifier():
    """Test TRL Classifier"""
    print("\n🔍 Testing TRL Classifier...")
    
    classifier = TRLClassifier()
    
    # Test component with active lifecycle
    component = {
        "part_number": "TPS54620",
        "lifecycle": "Active",
        "supply_chain": {
            "digikey": {"stock": 5000, "region": "EU"},
            "mouser": {"stock": 3000, "region": "EU"}
        }
    }
    
    trl = await classifier.classify(component)
    assert trl >= 7  # Active with good stock should be TRL 7-9
    print(f"✅ Component classified as TRL {trl}")
    
    # Test paper classification
    paper = {
        "title": "Novel GaN Power Conversion",
        "abstract": "This paper presents experimental proof of concept for GaN-based converters"
    }
    
    paper_trl = await classifier.classify_from_paper(paper)
    assert 1 <= paper_trl <= 9
    print(f"✅ Paper classified as TRL {paper_trl}")
    
    # Test justification
    justification = classifier.get_justification(component, trl)
    assert len(justification) > 0
    print(f"✅ Justification: {justification}")

def test_regional_filter():
    """Test Regional Filter"""
    print("\n🔍 Testing Regional Filter...")
    
    component = {
        "part_number": "TPS54620",
        "manufacturer": "Texas Instruments",
        "supply_chain": {
            "digikey": {"stock": 1000, "region": "EU"},
            "lcsc": {"stock": 5000, "region": "Asia"}
        }
    }
    
    # Filter for EU/Asia
    filtered = filter_by_region(component, ["EU", "Asia"])
    assert filtered["meets_regional_requirements"] == True
    assert "EU" in filtered["regions"] or "Asia" in filtered["regions"]
    print(f"✅ Regional filter working - regions: {filtered['regions']}")
    
    # Get regional distributors
    eu_distributors = get_regional_distributors("EU")
    assert len(eu_distributors) > 0
    print(f"✅ EU distributors: {eu_distributors}")
    
    asia_distributors = get_regional_distributors("Asia")
    assert len(asia_distributors) > 0
    print(f"✅ Asia distributors: {asia_distributors}")