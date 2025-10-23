import asyncio
import logging
from src.server import EnhancedSentientServer
from src.agent import EEResearchAgent
from src.config.settings import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

async def main():
    """Initialize and run the EE Research Scout server"""
    
    logger.info(f"Initializing {settings.AGENT_NAME} v1.0.0")
    
    # Initialize agent
    agent = EEResearchAgent()
    
    # Create enhanced server
    server = EnhancedSentientServer(
        agent=agent,
        host=settings.HOST,
        port=settings.PORT,
        enable_cache=settings.ENABLE_CACHE,
        enable_rate_limiting=settings.ENABLE_RATE_LIMITING,
        enable_circuit_breaker=settings.ENABLE_CIRCUIT_BREAKER,
        cors_origins=settings.CORS_ORIGINS
    )
    
    # Start server
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())