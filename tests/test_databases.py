import pytest
import asyncio
from database.db_manager import DatabaseManager

@pytest.fixture
async def db_manager():
    """Fixture to initialize and cleanup database manager"""
    manager = DatabaseManager()
    await manager.initialize()
    yield manager
    await manager.close()

@pytest.mark.asyncio
async def test_postgres_connection(db_manager):
    """Test PostgreSQL connection"""
    print("\n🔍 Testing PostgreSQL connection...")
    
    # Simple query
    result = await db_manager.pg_fetchrow("SELECT 1 as test")
    assert result['test'] == 1
    print("✅ PostgreSQL connected successfully")

@pytest.mark.asyncio
async def test_postgres_queries_table(db_manager):
    """Test queries table operations"""
    print("\n🔍 Testing PostgreSQL queries table...")
    
    # Insert test query
    query_hash = "test_hash_123"
    await db_manager.pg_execute(
        """
        INSERT INTO queries (query_text, query_hash, status)
        VALUES ($1, $2, $3)
        ON CONFLICT (query_hash) DO NOTHING
        """,
        "Test query", query_hash, "processing"
    )
    
    # Fetch query
    result = await db_manager.pg_fetchrow(
        "SELECT * FROM queries WHERE query_hash = $1",
        query_hash
    )
    assert result is not None
    assert result['query_text'] == "Test query"
    print("✅ Queries table working")
    
    # Cleanup
    await db_manager.pg_execute(
        "DELETE FROM queries WHERE query_hash = $1",
        query_hash
    )

@pytest.mark.asyncio
async def test_mongodb_connection(db_manager):
    """Test MongoDB connection"""
    print("\n🔍 Testing MongoDB connection...")
    
    collection = db_manager.mongo_collection("test_collection")
    
    # Insert test document
    result = await collection.insert_one({"test": "data", "value": 123})
    assert result.inserted_id is not None
    print("✅ MongoDB connected and insert working")
    
    # Fetch document
    doc = await collection.find_one({"test": "data"})
    assert doc['value'] == 123
    print("✅ MongoDB query working")
    
    # Cleanup
    await collection.delete_one({"_id": result.inserted_id})

@pytest.mark.asyncio
async def test_neo4j_connection(db_manager):
    """Test Neo4j connection"""
    print("\n🔍 Testing Neo4j connection...")
    
    async with db_manager.neo4j_session() as session:
        # Create test node
        result = await session.run(
            "CREATE (n:TestNode {name: 'test'}) RETURN n"
        )
        record = await result.single()
        assert record is not None
        print("✅ Neo4j connected and create working")
        
        # Query node
        result = await session.run(
            "MATCH (n:TestNode {name: 'test'}) RETURN n"
        )
        record = await result.single()
        assert record is not None
        print("✅ Neo4j query working")
        
        # Cleanup
        await session.run("MATCH (n:TestNode {name: 'test'}) DELETE n")