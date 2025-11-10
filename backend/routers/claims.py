"""
Claims Router
Endpoints for claim ingestion and management
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from loguru import logger

from database.connection import get_database
from models.schemas import (
    IngestRequest, IngestResponse, ClaimResponse,
    ClaimInDB, FilterParams
)
from agents.claim_detector import ClaimDetectionAgent
from services.embedding_service import EmbeddingService


router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_text(
    request: IngestRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Ingest new text and detect if it contains a claim
    
    POST /api/ingest
    {
        "text": "The moon landing was faked in 1969",
        "source": "https://example.com/post/123",
        "source_type": "social",
        "metadata": {}
    }
    """
    try:
        # Initialize agents
        claim_detector = ClaimDetectionAgent()
        embedding_service = EmbeddingService()
        
        # Detect claim
        detection_result = await claim_detector.detect_claim(request.text)
        
        if not detection_result["is_claim"]:
            return IngestResponse(
                claim_id=None,
                is_claim=False,
                message="No verifiable claim detected in the text",
                claim_detected=None
            )
        
        # Generate embedding
        embedding = await embedding_service.generate_embedding(detection_result["claim_text"])
        
        # Create claim document
        claim_data = ClaimInDB(
            claim_text=detection_result["claim_text"],
            source=request.source,
            source_type=request.source_type,
            entities=detection_result.get("entities", []),
            claim_type=detection_result.get("claim_type", "general"),
            confidence=detection_result.get("confidence", 0.0),
            raw_text=request.text,
            metadata=request.metadata,
            embedding=embedding,
            status="pending"
        )
        
        # Insert into database
        result = await db.claims.insert_one(claim_data.dict(by_alias=True, exclude={"id"}))
        claim_id = str(result.inserted_id)
        
        # Add to FAISS index
        await embedding_service.add_claim_to_index(
            claim_id,
            detection_result["claim_text"],
            embedding
        )
        
        logger.info(f"✅ Claim ingested: {claim_id}")
        
        # Prepare response
        claim_response = ClaimResponse(
            id=claim_id,
            claim_text=claim_data.claim_text,
            source=claim_data.source,
            source_type=claim_data.source_type,
            entities=claim_data.entities,
            claim_type=claim_data.claim_type,
            confidence=claim_data.confidence,
            status=claim_data.status,
            created_at=claim_data.created_at
        )
        
        return IngestResponse(
            claim_id=claim_id,
            is_claim=True,
            message="Claim detected and stored successfully",
            claim_detected=claim_response
        )
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.get("/claims", response_model=List[ClaimResponse])
async def get_claims(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    claim_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get list of claims with filters
    
    GET /api/claims?skip=0&limit=20&claim_type=health&status=verified
    """
    try:
        # Build query
        query = {}
        
        if claim_type:
            query["claim_type"] = claim_type
        
        if status:
            query["status"] = status
        
        if search:
            query["$text"] = {"$search": search}
        
        # Execute query
        cursor = db.claims.find(query).sort("created_at", -1).skip(skip).limit(limit)
        claims = await cursor.to_list(length=limit)
        
        # Format response
        response = []
        for claim in claims:
            # Get verdict summary if exists
            verdict_summary = None
            if claim.get("verdict_id"):
                verdict = await db.verdicts.find_one({"_id": claim["verdict_id"]})
                if verdict:
                    verdict_summary = verdict.get("verdict", "Unknown")
            
            response.append(ClaimResponse(
                id=str(claim["_id"]),
                claim_text=claim["claim_text"],
                source=claim["source"],
                source_type=claim["source_type"],
                entities=claim.get("entities", []),
                claim_type=claim["claim_type"],
                confidence=claim["confidence"],
                status=claim["status"],
                verdict_summary=verdict_summary,
                created_at=claim["created_at"]
            ))
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to get claims: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/claims/{claim_id}")
async def get_claim_detail(
    claim_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get detailed information about a specific claim
    
    GET /api/claims/507f1f77bcf86cd799439011
    """
    try:
        from bson import ObjectId
        
        # Get claim
        claim = await db.claims.find_one({"_id": ObjectId(claim_id)})
        
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        # Get verdict
        verdict = None
        if claim.get("verdict_id"):
            verdict = await db.verdicts.find_one({"_id": ObjectId(claim["verdict_id"])})
            if verdict:
                verdict["id"] = str(verdict.pop("_id"))
        
        # Get evidence
        evidence = await db.evidence.find_one({"claim_id": claim_id})
        if evidence:
            evidence["id"] = str(evidence.pop("_id"))
        
        # Get similar claims
        embedding_service = EmbeddingService()
        similar_claims = await embedding_service.find_similar_claims(
            claim["claim_text"],
            k=5,
            threshold=0.8
        )
        
        claim["id"] = str(claim.pop("_id"))
        
        return {
            "claim": claim,
            "verdict": verdict,
            "evidence": evidence,
            "similar_claims": similar_claims
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get claim detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get platform statistics
    
    GET /api/stats
    """
    try:
        total_claims = await db.claims.count_documents({})
        verified_claims = await db.verdicts.count_documents({})
        trending_clusters = await db.clusters.count_documents({"is_trending": True})
        
        # Verdict breakdown
        verdicts = await db.verdicts.aggregate([
            {"$group": {"_id": "$verdict", "count": {"$sum": 1}}}
        ]).to_list(length=10)
        
        verdict_breakdown = {v["_id"]: v["count"] for v in verdicts}
        
        return {
            "total_claims": total_claims,
            "verified_claims": verified_claims,
            "trending_clusters": trending_clusters,
            "verdict_breakdown": verdict_breakdown
        }
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
