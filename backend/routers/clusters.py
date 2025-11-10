"""
Clusters Router
Endpoints for claim clustering and trending topics
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from loguru import logger

from database.connection import get_database
from services.clustering_service import ClusteringService


router = APIRouter()


@router.get("/clusters")
async def get_trending_clusters(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get trending claim clusters
    
    GET /api/clusters?limit=10
    """
    try:
        clustering_service = ClusteringService(db)
        clusters = await clustering_service.get_trending_clusters(limit)
        
        return {
            "clusters": clusters,
            "total": len(clusters)
        }
        
    except Exception as e:
        logger.error(f"Failed to get clusters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clusters/refresh")
async def refresh_clusters(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Refresh claim clustering (run clustering on recent claims)
    
    POST /api/clusters/refresh?hours=24
    """
    try:
        clustering_service = ClusteringService(db)
        clusters = await clustering_service.cluster_recent_claims(hours)
        
        logger.info(f"✅ Clustered claims from last {hours} hours")
        
        return {
            "status": "success",
            "clusters_created": len(clusters),
            "time_window_hours": hours
        }
        
    except Exception as e:
        logger.error(f"Clustering failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clusters/{cluster_id}")
async def get_cluster_detail(
    cluster_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get detailed information about a cluster
    
    GET /api/clusters/cluster_123456789
    """
    try:
        cluster = await db.clusters.find_one({"cluster_id": cluster_id})
        
        if not cluster:
            raise HTTPException(status_code=404, detail="Cluster not found")
        
        # Get claims in cluster
        from bson import ObjectId
        claim_ids = [ObjectId(cid) for cid in cluster["claim_ids"] if ObjectId.is_valid(cid)]
        
        claims_cursor = db.claims.find({"_id": {"$in": claim_ids}})
        claims = await claims_cursor.to_list(length=len(claim_ids))
        
        # Format claims
        for claim in claims:
            claim["id"] = str(claim.pop("_id"))
        
        cluster["id"] = str(cluster.pop("_id"))
        
        return {
            "cluster": cluster,
            "claims": claims
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get cluster detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))
