"""
CrisisGuard AI - Main FastAPI Application
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from database.connection import db_config
from routers import claims, verification, clusters, feedback, alerts


# Configure logging
logger.add(
    "logs/crisisguard_{time}.log",
    rotation="100 MB",
    retention="30 days",
    level="INFO"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting CrisisGuard AI...")
    
    try:
        await db_config.connect_mongodb()
        await db_config.connect_redis()
        logger.info("✅ All services connected")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down CrisisGuard AI...")
    await db_config.disconnect_mongodb()
    await db_config.disconnect_redis()
    logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="CrisisGuard AI",
    description="Real-time misinformation detection & verification platform",
    version="1.0.0",
    lifespan=lifespan
)


# CORS Configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(claims.router, prefix="/api", tags=["Claims"])
app.include_router(verification.router, prefix="/api", tags=["Verification"])
app.include_router(clusters.router, prefix="/api", tags=["Clusters"])
app.include_router(feedback.router, prefix="/api", tags=["Feedback"])
app.include_router(alerts.router, prefix="/api", tags=["Alerts"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "CrisisGuard AI",
        "version": "1.0.0",
        "status": "operational",
        "description": "Real-time misinformation detection & verification platform"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check MongoDB
        await db_config.database.command('ping')
        mongo_status = "healthy"
    except Exception:
        mongo_status = "unhealthy"
    
    try:
        # Check Redis
        await db_config.redis_client.ping()
        redis_status = "healthy"
    except Exception:
        redis_status = "unhealthy"
    
    overall_status = "healthy" if (mongo_status == "healthy" and redis_status == "healthy") else "degraded"
    
    return {
        "status": overall_status,
        "services": {
            "mongodb": mongo_status,
            "redis": redis_status
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
