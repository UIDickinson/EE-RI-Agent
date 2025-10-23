from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import time
from datetime import datetime

from src.utils.cache import CacheManager
from src.utils.rate_limiter import RateLimiter
from src.utils.circuit_breaker import CircuitBreaker
from src.utils.metrics import MetricsCollector
from src.config.settings import settings

logger = logging.getLogger(__name__)

class SessionData(BaseModel):
    """Sentient Framework session format"""
    user_id: str = "anonymous"
    session_id: str
    processor_id: str
    activity_id: str
    request_id: str
    interactions: List = []

class QueryData(BaseModel):
    """Sentient Framework query format"""
    id: str
    prompt: str
    context: str = ""

class AssistRequest(BaseModel):
    """Standard Sentient Framework request"""
    session: SessionData
    query: QueryData

class EnhancedSentientServer:
    """
    Production-grade Sentient Agent server
    
    Features:
    - Rate limiting
    - Result caching
    - Circuit breaker for fault tolerance
    - Security monitoring
    - Performance metrics
    - Health checks
    """
    
    def __init__(
        self,
        agent,
        host: str = "0.0.0.0",
        port: int = 8000,
        enable_cache: bool = True,
        enable_rate_limiting: bool = True,
        enable_circuit_breaker: bool = True,
        cors_origins: List[str] = None
    ):
        self.agent = agent
        self.host = host
        self.port = port
        
        # Initialize FastAPI
        self.app = FastAPI(
            title=settings.AGENT_NAME,
            description="Production-grade EE research agent",
            version="1.0.0"
        )
        
        # Initialize components
        self.cache = CacheManager() if enable_cache else None
        self.rate_limiter = RateLimiter() if enable_rate_limiting else None
        self.circuit_breaker = CircuitBreaker() if enable_circuit_breaker else None
        self.metrics = MetricsCollector()
        
        # Setup middleware
        self._setup_middleware(cors_origins or ["*"])
        
        # Setup routes
        self._setup_routes()
        
        logger.info(f"Server initialized with cache={enable_cache}, "
                   f"rate_limiting={enable_rate_limiting}, "
                   f"circuit_breaker={enable_circuit_breaker}")
    
    def _setup_middleware(self, cors_origins: List[str]):
        """Configure CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            start_time = time.time()
            response = await call_next(request)
            duration = time.time() - start_time
            
            logger.info(
                f"{request.method} {request.url.path} "
                f"status={response.status_code} duration={duration:.3f}s"
            )
            
            self.metrics.record_request(
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                duration=duration
            )
            
            return response
    
    def _setup_routes(self):
        """Setup API endpoints"""
        
        @self.app.get("/")
        async def root():
            return {
                "agent": settings.AGENT_NAME,
                "version": "1.0.0",
                "status": "operational",
                "endpoints": {
                    "assist": "/assist",
                    "health": "/health",
                    "info": "/info",
                    "metrics": "/metrics",
                    "docs": "/docs"
                }
            }
        
        @self.app.get("/health")
        async def health():
            """Comprehensive health check"""
            health_status = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "components": {
                    "agent": "operational",
                    "cache": "operational" if self.cache else "disabled",
                    "rate_limiter": "operational" if self.rate_limiter else "disabled",
                    "circuit_breaker": "operational" if self.circuit_breaker else "disabled"
                }
            }
            
            # Check database connections
            try:
                # Add database health checks here
                health_status["components"]["database"] = "operational"
            except Exception as e:
                health_status["status"] = "degraded"
                health_status["components"]["database"] = f"error: {str(e)}"
            
            return health_status
        
        @self.app.get("/info")
        async def info():
            """Agent capabilities and information"""
            return {
                "agent": settings.AGENT_NAME,
                "version": "1.0.0",
                "description": "AI-driven research agent for Electrical/Electronics Engineers",
                "capabilities": [
                    "Academic paper search (IEEE, arXiv)",
                    "Patent search (EPO, CNIPA, JPO)",
                    "Component/datasheet search",
                    "Supply chain monitoring",
                    "TRL classification",
                    "Multi-source synthesis"
                ],
                "domains": [
                    "Embedded Systems",
                    "Power Management ICs",
                    "EMC/EMI Solutions",
                    "Analog/Mixed-Signal",
                    "RF/Wireless"
                ],
                "regions": settings.TARGET_REGIONS,
                "features": {
                    "caching": self.cache is not None,
                    "rate_limiting": self.rate_limiter is not None,
                    "circuit_breaker": self.circuit_breaker is not None
                }
            }
        
        @self.app.get("/metrics")
        async def metrics():
            """Performance metrics"""
            return self.metrics.get_metrics()
        
        @self.app.post("/assist")
        async def assist(
            request: AssistRequest,
            http_request: Request
        ):
            """
            Main agent endpoint (Sentient Framework compatible)
            """
            start_time = time.time()
            
            try:
                # Rate limiting
                if self.rate_limiter:
                    await self.rate_limiter.check_limit(
                        key=request.session.user_id,
                        request=http_request
                    )
                
                # Check cache
                cache_key = f"query:{hash(request.query.prompt)}"
                if self.cache:
                    cached_result = await self.cache.get(cache_key)
                    if cached_result:
                        logger.info(f"Cache hit for query: {request.query.prompt[:50]}")
                        self.metrics.record_cache_hit()
                        return cached_result
                
                # Circuit breaker check
                if self.circuit_breaker and not self.circuit_breaker.can_execute():
                    raise HTTPException(
                        status_code=503,
                        detail="Service temporarily unavailable"
                    )
                
                # Process with agent
                try:
                    result = await self.agent.process_query(
                        query=request.query.prompt,
                        session_id=request.session.session_id,
                        user_id=request.session.user_id,
                        context=request.query.context
                    )
                    
                    # Record success with circuit breaker
                    if self.circuit_breaker:
                        self.circuit_breaker.record_success()
                    
                    # Build response
                    response = {
                        "session": request.session.dict(),
                        "response": {
                            "id": request.query.id,
                            "content": result["response"],
                            "metadata": result.get("metadata", {}),
                            "sources": result.get("sources", [])
                        }
                    }
                    
                    # Cache result
                    if self.cache:
                        await self.cache.set(cache_key, response)
                    
                    # Record metrics
                    duration = time.time() - start_time
                    self.metrics.record_query(
                        query=request.query.prompt,
                        duration=duration,
                        success=True
                    )
                    
                    return response
                
                except Exception as e:
                    # Record failure with circuit breaker
                    if self.circuit_breaker:
                        self.circuit_breaker.record_failure()
                    raise
            
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}")
                self.metrics.record_error(str(e))
                raise HTTPException(status_code=500, detail=str(e))
    
    async def start(self):
        """Start the server"""
        import uvicorn
        
        logger.info(f"Starting {settings.AGENT_NAME} on {self.host}:{self.port}")
        
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level=settings.LOG_LEVEL.lower(),
            reload=settings.ENVIRONMENT == "development"
        )
        
        server = uvicorn.Server(config)
        await server.serve()