import os
from typing import Dict, Any, Optional
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
from neo4j import AsyncGraphDatabase

class DatabaseManager:
    """
    Unified database manager for PostgreSQL, MongoDB, and Neo4j
    """
    
    def __init__(self):
        # PostgreSQL
        self.pg_pool = None
        self.pg_config = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": int(os.getenv("POSTGRES_PORT", 5432)),
            "database": os.getenv("POSTGRES_DB", "ee_scout"),
            "user": os.getenv("POSTGRES_USER", "postgres"),
            "password": os.getenv("POSTGRES_PASSWORD", "changeme")
        }
        
        # MongoDB
        self.mongo_client = None
        self.mongo_db = None
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        
        # Neo4j
        self.neo4j_driver = None
        self.neo4j_config = {
            "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            "user": os.getenv("NEO4J_USER", "neo4j"),
            "password": os.getenv("NEO4J_PASSWORD", "changeme")
        }
    
    async def initialize(self):
        """Initialize all database connections"""
        await self._init_postgres()
        await self._init_mongodb()
        await self._init_neo4j()
        print("✅ All databases initialized")
    
    async def _init_postgres(self):
        """Initialize PostgreSQL connection pool"""
        try:
            self.pg_pool = await asyncpg.create_pool(
                **self.pg_config,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            print("✅ PostgreSQL connected")
        except Exception as e:
            print(f"⚠️  PostgreSQL connection error: {e}")
    
    async def _init_mongodb(self):
        """Initialize MongoDB connection"""
        try:
            self.mongo_client = AsyncIOMotorClient(self.mongo_uri)
            self.mongo_db = self.mongo_client.ee_scout
            # Test connection
            await self.mongo_client.admin.command('ping')
            print("✅ MongoDB connected")
        except Exception as e:
            print(f"⚠️  MongoDB connection error: {e}")
    
    async def _init_neo4j(self):
        """Initialize Neo4j connection"""
        try:
            self.neo4j_driver = AsyncGraphDatabase.driver(
                self.neo4j_config["uri"],
                auth=(self.neo4j_config["user"], self.neo4j_config["password"])
            )
            # Test connection
            async with self.neo4j_driver.session() as session:
                await session.run("RETURN 1")
            print("✅ Neo4j connected")
        except Exception as e:
            print(f"⚠️  Neo4j connection error: {e}")
    
    async def close(self):
        """Close all database connections"""
        if self.pg_pool:
            await self.pg_pool.close()
        if self.mongo_client:
            self.mongo_client.close()
        if self.neo4j_driver:
            await self.neo4j_driver.close()
        print("✅ All database connections closed")
    
    # PostgreSQL helpers
    async def pg_execute(self, query: str, *args):
        """Execute PostgreSQL query"""
        async with self.pg_pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def pg_fetch(self, query: str, *args):
        """Fetch multiple rows from PostgreSQL"""
        async with self.pg_pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def pg_fetchrow(self, query: str, *args):
        """Fetch single row from PostgreSQL"""
        async with self.pg_pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    # MongoDB helpers
    def mongo_collection(self, name: str):
        """Get MongoDB collection"""
        return self.mongo_db[name]
    
    # Neo4j helpers
    def neo4j_session(self):
        """Get Neo4j session"""
        return self.neo4j_driver.session()


# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions
async def init_databases():
    """Initialize all databases"""
    await db_manager.initialize()

async def close_databases():
    """Close all database connections"""
    await db_manager.close()

def get_postgres_pool():
    """Get PostgreSQL connection pool"""
    return db_manager.pg_pool

def get_mongodb_collection(collection_name: str):
    """Get MongoDB collection"""
    return db_manager.mongo_collection(collection_name)

def get_neo4j_driver():
    """Get Neo4j driver"""
    return db_manager.neo4j_driver

async def get_postgres_connection():
    """Get PostgreSQL connection from pool"""
    return await db_manager.pg_pool.acquire()