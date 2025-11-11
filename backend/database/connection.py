"""
Database connection and configuration for CrisisGuard AI
Handles MongoDB and Redis connections
"""

import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase  # type: ignore
import redis.asyncio as aioredis  # type: ignore
from loguru import logger  # type: ignore


class DatabaseConfig:
    """Database configuration and connection management"""
    
    def __init__(self):
        self.mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/crisisguard")
        self.database_name = os.getenv("MONGODB_DATABASE", "crisisguard")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.redis_client: Optional[aioredis.Redis] = None
    
    async def connect_mongodb(self):
        """Connect to MongoDB"""
        try:
            self.mongo_client = AsyncIOMotorClient(
                self.mongodb_uri,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=50
            )
            # Test connection
            await self.mongo_client.admin.command('ping')  # type: ignore
            self.database = self.mongo_client[self.database_name]  # type: ignore
            logger.info(f"✅ Connected to MongoDB: {self.database_name}")
            
            # Create indexes
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            raise
    
    async def connect_redis(self):
        """Connect to Redis (optional - will continue without it)"""
        try:
            self.redis_client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20
            )
            # Test connection
            await self.redis_client.ping()  # type: ignore
            logger.info(f"✅ Connected to Redis")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed (continuing without it): {e}")
            self.redis_client = None
    
    async def disconnect_mongodb(self):
        """Disconnect from MongoDB"""
        if self.mongo_client:
            self.mongo_client.close()
            logger.info("MongoDB connection closed")
    
    async def disconnect_redis(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")
    
    async def _create_indexes(self):
        """Create database indexes for optimal performance"""
        if self.database is None:
            return
        try:
            # Claims indexes
            await self.database.claims.create_index("claim_text")  # type: ignore
            await self.database.claims.create_index([("created_at", -1)])  # type: ignore
            await self.database.claims.create_index("claim_type")  # type: ignore
            await self.database.claims.create_index("status")  # type: ignore
            await self.database.claims.create_index("cluster_id")  # type: ignore
            
            # Evidence indexes
            await self.database.evidence.create_index("claim_id")  # type: ignore
            await self.database.evidence.create_index([("created_at", -1)])  # type: ignore
            
            # Verdicts indexes
            await self.database.verdicts.create_index("claim_id")  # type: ignore
            await self.database.verdicts.create_index("verdict")  # type: ignore
            await self.database.verdicts.create_index([("confidence", -1)])  # type: ignore
            await self.database.verdicts.create_index([("created_at", -1)])  # type: ignore
            await self.database.verdicts.create_index("human_reviewed")  # type: ignore
            
            # Clusters indexes
            await self.database.clusters.create_index("cluster_id", unique=True)  # type: ignore
            await self.database.clusters.create_index("is_trending")  # type: ignore
            await self.database.clusters.create_index([("trend_score", -1)])  # type: ignore
            
            # Sources indexes
            await self.database.sources.create_index("domain", unique=True)  # type: ignore
            await self.database.sources.create_index([("reliability_rating", -1)])  # type: ignore
            
            # Alerts indexes
            await self.database.alerts.create_index([("created_at", -1)])  # type: ignore
            await self.database.alerts.create_index("severity")  # type: ignore
            await self.database.alerts.create_index("is_active")  # type: ignore
            
            # Feedback indexes
            await self.database.feedback.create_index("claim_id")  # type: ignore
            await self.database.feedback.create_index("status")  # type: ignore
            
            # Users indexes
            await self.database.users.create_index("email", unique=True)  # type: ignore
            await self.database.users.create_index("role")  # type: ignore
            
            logger.info("✅ Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Index creation warning: {e}")


# Global database instance
db_config = DatabaseConfig()


async def get_database() -> AsyncIOMotorDatabase:
    """Dependency to get database instance"""
    return db_config.database


async def get_redis() -> Optional[aioredis.Redis]:  # type: ignore
    """Dependency to get Redis instance (may be None)"""
    return db_config.redis_client
