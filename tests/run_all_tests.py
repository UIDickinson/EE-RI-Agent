import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def run_database_tests():
    """Run database tests"""
    print("\n" + "="*80)
    print("DATABASE TESTS")
    print("="*80)
    
    from tests.test_databases import (
        test_postgres_connection,
        test_postgres_queries_table,
        test_mongodb_connection,
        test_neo4j_connection
    )
    from database.db_manager import DatabaseManager
    
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    try:
        await test_postgres_connection(db_manager)
        await test_postgres_queries_table(db_manager)
        await test_mongodb_connection(db_manager)
        await test_neo4j_connection(db_manager)
        print("\n✅ All database tests passed!")
    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
    finally:
        await db_manager.close()

async def run_tools_tests():
    """Run tools tests"""
    print("\n" + "="*80)
    print("TOOLS TESTS")
    print("="*80)
    
    from tests.test_tools import (
        test_knowledge_graph_connection,
        test_trl_classifier,
        test_regional_filter
    )
    
    try:
        await test_knowledge_graph_connection()
        await test_trl_classifier()
        test_regional_filter()
        print("\n✅ All tools tests passed!")
    except Exception as e:
        print(f"\n❌ Tools test failed: {e}")

async def run_executors_tests():
    """Run executors tests"""
    print("\n" + "="*80)
    print("EXECUTORS TESTS")
    print("="*80)
    
    from tests.test_executors import (
        test_datasheet_executor,
        test_paper_executor,
        test_patent_executor,
        test_supply_chain_executor,
        test_component_executor
    )
    
    try:
        await test_datasheet_executor()
        await test_paper_executor()
        await test_patent_executor()
        await test_supply_chain_executor()
        await test_component_executor()
        print("\n✅ All executors tests passed!")
    except Exception as e:
        print(f"\n❌ Executors test failed: {e}")

async def run_planners_tests():
    """Run planners tests"""
    print("\n" + "="*80)
    print("PLANNERS TESTS")
    print("="*80)
    
    from tests.test_planners import (
        test_ee_planner,
        test_trl_planner,
        test_planner_selection
    )
    
    try:
        await test_ee_planner()
        await test_trl_planner()
        test_planner_selection()
        print("\n✅ All planners tests passed!")
    except Exception as e:
        print(f"\n❌ Planners test failed: {e}")

async def run_aggregators_tests():
    """Run aggregators tests"""
    print("\n" + "="*80)
    print("AGGREGATORS TESTS")
    print("="*80)
    
    from tests.test_aggregators import (
        test_ee_aggregator,
        test_report_generator
    )
    
    try:
        await test_ee_aggregator()
        await test_report_generator()
        print("\n✅ All aggregators tests passed!")
    except Exception as e:
        print(f"\n❌ Aggregators test failed: {e}")

async def run_agent_tests():
    """Run agent tests"""
    print("\n" + "="*80)
    print("AGENT TESTS")
    print("="*80)
    
    from tests.test_agent import (
        test_agent_creation,
        test_agent_info,
        test_agent_atomic_query,
        test_agent_complex_query
    )
    
    try:
        test_agent_creation()
        test_agent_info()
        await test_agent_atomic_query()
        await test_agent_complex_query()
        print("\n✅ All agent tests passed!")
    except Exception as e:
        print(f"\n❌ Agent test failed: {e}")

async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("EE RESEARCH SCOUT - COMPREHENSIVE BACKEND TESTS")
    print("="*80)
    
    try:
        await run_database_tests()
        await run_tools_tests()
        await run_executors_tests()
        await run_planners_tests()
        await run_aggregators_tests()
        await run_agent_tests()
        
        print("\n" + "="*80)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\nBackend is ready for integration with frontend.")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())