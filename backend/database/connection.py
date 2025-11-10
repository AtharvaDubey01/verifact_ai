"""
Database connection and configuration for CrisisGuard AI
Handles MongoDB and Redis connections
"""

import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import redis.asyncio as aioredis
from loguru import logger


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
            await self.mongo_client.admin.command('ping')
            self.database = self.mongo_client[self.database_name]
            logger.info(f"✅ Connected to MongoDB: {self.database_name}")
            
            # Create indexes
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            raise
    
    async def connect_redis(self):
        """Connect to Redis"""
        try:
            self.redis_client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20
            )
            # Test connection
            await self.redis_client.ping()
            logger.info(f"✅ Connected to Redis")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise
    
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
        try:
            # Claims indexes
            await self.database.claims.create_index("claim_text")
            await self.database.claims.create_index([("created_at", -1)])
            await self.database.claims.create_index("claim_type")
            await self.database.claims.create_index("status")
            await self.database.claims.create_index("cluster_id")
            
            # Evidence indexes
            await self.database.evidence.create_index("claim_id")
            await self.database.evidence.create_index([("created_at", -1)])
            
            # Verdicts indexes
            await self.database.verdicts.create_index("claim_id")
            await self.database.verdicts.create_index("verdict")
            await self.database.verdicts.create_index([("confidence", -1)])
            await self.database.verdicts.create_index([("created_at", -1)])
            await self.database.verdicts.create_index("human_reviewed")
            
            # Clusters indexes
            await self.database.clusters.create_index("cluster_id", unique=True)
            await self.database.clusters.create_index("is_trending")
            await self.database.clusters.create_index([("trend_score", -1)])
            
            # Sources indexes
            await self.database.sources.create_index("domain", unique=True)
            await self.database.sources.create_index([("reliability_rating", -1)])
            
            # Alerts indexes
            await self.database.alerts.create_index([("created_at", -1)])
            await self.database.alerts.create_index("severity")
            await self.database.alerts.create_index("is_active")
            
            # Feedback indexes
            await self.database.feedback.create_index("claim_id")
            await self.database.feedback.create_index("status")
            
            # Users indexes
            await self.database.users.create_index("email", unique=True)
            await self.database.users.create_index("role")
            
            logger.info("✅ Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Index creation warning: {e}")


# Global database instance
db_config = DatabaseConfig()


async def get_database() -> AsyncIOMotorDatabase:
    """Dependency to get database instance"""
    return db_config.database


async def get_redis() -> aioredis.Redis:
    """Dependency to get Redis instance"""
    return db_config.redis_client
