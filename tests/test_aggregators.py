import pytest
from agents.aggregators import EEAggregator, ReportGenerator

@pytest.mark.asyncio
async def test_ee_aggregator():
    """Test EE Aggregator"""
    print("\n🔍 Testing EE Aggregator...")
    
    aggregator = EEAggregator()
    
    # Create mock subtask results
    subtask_results = [
        {
            "source": "academic_papers",
            "papers": [
                {
                    "title": "Test Paper 1",
                    "doi": "10.1234/test1",
                    "authors": ["Author 1"],
                    "year": 2024,
                    "abstract": "Test abstract 1"
                }
            ]
        },
        {
            "source": "patent_search",
            "patents": [
                {
                    "patent_number": "EP1234567B1",
                    "title": "Test Patent",
                    "applicant": "Test Company",
                    "filing_date": "2022-01-01"
                }
            ]
        },
        {
            "source": "datasheet_search",
            "components": [
                {
                    "part_number": "TEST123",
                    "manufacturer": "Test Mfr",
                    "category": "Buck Converter",
                    "lifecycle": "Active"
                }
            ]
        }
    ]
    
    result = await aggregator.aggregate(
        subtask_results,
        "Test query for GaN power ICs"
    )
    
    assert result is not None
    assert "metadata" in result
    print("✅ EE Aggregator working - generated comprehensive report")

@pytest.mark.asyncio
async def test_report_generator():
    """Test Report Generator"""
    print("\n🔍 Testing Report Generator...")
    
    generator = ReportGenerator()
    
    # Create mock data
    data = {
        "papers": [{"title": "Test Paper", "authors": ["Author"], "year": 2024}],
        "patents": [{"patent_number": "EP123", "title": "Test"}],
        "components": [{"part_number": "TEST", "manufacturer": "Test"}],
        "technologies": []
    }
    
    # Test deep report
    report = await generator.generate("Test query", data, depth="deep")
    
    assert report is not None
    assert report["report_type"] == "comprehensive_analysis"
    assert "executive_summary" in report
    assert "literature_review" in report
    assert "recommendations" in report
    print("✅ Report Generator working - generated deep report")