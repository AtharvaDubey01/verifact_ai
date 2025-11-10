"""
Verification Router
Endpoints for claim verification and fact-checking
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from loguru import logger

from database.connection import get_database
from models.schemas import VerifyRequest, VerdictResponse, VerdictInDB
from agents.evidence_retriever import EvidenceRetrieverAgent
from agents.fact_checker import FactCheckerAgent


router = APIRouter()


@router.post("/verify/{claim_id}", response_model=VerdictResponse)
async def verify_claim(
    claim_id: str,
    force_reverify: bool = False,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Verify a claim by retrieving evidence and fact-checking
    
    POST /api/verify/507f1f77bcf86cd799439011
    """
    try:
        # Get claim
        claim = await db.claims.find_one({"_id": ObjectId(claim_id)})
        
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        # Check if already verified
        if claim.get("verdict_id") and not force_reverify:
            existing_verdict = await db.verdicts.find_one({"_id": ObjectId(claim["verdict_id"])})
            if existing_verdict:
                return VerdictResponse(
                    id=str(existing_verdict["_id"]),
                    claim_id=claim_id,
                    verdict=existing_verdict["verdict"],
                    confidence=existing_verdict["confidence"],
                    reasoning=existing_verdict["reasoning"],
                    sources=existing_verdict["sources"],
                    explain_like_12=existing_verdict["explain_like_12"],
                    harm_score=existing_verdict["harm_score"],
                    recommended_action=existing_verdict["recommended_action"],
                    human_reviewed=existing_verdict.get("human_reviewed", False),
                    created_at=existing_verdict["created_at"]
                )
        
        # Update claim status
        await db.claims.update_one(
            {"_id": ObjectId(claim_id)},
            {"$set": {"status": "processing", "updated_at": datetime.utcnow()}}
        )
        
        # Initialize agents
        evidence_retriever = EvidenceRetrieverAgent()
        fact_checker = FactCheckerAgent()
        
        # Retrieve evidence
        logger.info(f"Retrieving evidence for claim {claim_id}")
        evidence_result = await evidence_retriever.retrieve_evidence(
            claim["claim_text"],
            claim.get("entities", [])
        )
        
        # Save evidence
        evidence_data = {
            "claim_id": claim_id,
            "sources": evidence_result["sources"],
            "total_sources_found": evidence_result["total_sources_found"],
            "search_queries": evidence_result["search_queries"],
            "retrieval_method": evidence_result["retrieval_method"],
            "created_at": datetime.utcnow()
        }
        
        await db.evidence.insert_one(evidence_data)
        
        # Fact-check
        logger.info(f"Fact-checking claim {claim_id}")
        start_time = datetime.utcnow()
        
        verdict_result = await fact_checker.fact_check(
            claim["claim_text"],
            evidence_result["sources"]
        )
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Save verdict
        verdict_data = VerdictInDB(
            claim_id=claim_id,
            verdict=verdict_result["verdict"],
            confidence=verdict_result["confidence"],
            reasoning=verdict_result["reasoning"],
            sources=verdict_result["sources"],
            explain_like_12=verdict_result["explain_like_12"],
            harm_score=verdict_result["harm_score"],
            recommended_action=verdict_result["recommended_action"],
            expert_explanation=verdict_result.get("expert_explanation"),
            tags=verdict_result.get("tags", []),
            processing_time_seconds=processing_time,
            human_reviewed=False
        )
        
        verdict_insert = await db.verdicts.insert_one(
            verdict_data.dict(by_alias=True, exclude={"id"})
        )
        verdict_id = str(verdict_insert.inserted_id)
        
        # Update claim with verdict
        await db.claims.update_one(
            {"_id": ObjectId(claim_id)},
            {
                "$set": {
                    "verdict_id": verdict_id,
                    "status": "verified",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Create alert if high harm score
        if verdict_result["harm_score"] >= 70:
            await _create_alert(db, claim_id, claim["claim_text"], verdict_result)
        
        logger.info(f"✅ Claim {claim_id} verified: {verdict_result['verdict']}")
        
        return VerdictResponse(
            id=verdict_id,
            claim_id=claim_id,
            verdict=verdict_result["verdict"],
            confidence=verdict_result["confidence"],
            reasoning=verdict_result["reasoning"],
            sources=verdict_result["sources"],
            explain_like_12=verdict_result["explain_like_12"],
            harm_score=verdict_result["harm_score"],
            recommended_action=verdict_result["recommended_action"],
            human_reviewed=False,
            created_at=verdict_data.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        
        # Update claim status to error
        await db.claims.update_one(
            {"_id": ObjectId(claim_id)},
            {"$set": {"status": "error", "updated_at": datetime.utcnow()}}
        )
        
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.post("/review/{verdict_id}")
async def human_review(
    verdict_id: str,
    override_verdict: Optional[str] = None,
    notes: Optional[str] = None,
    approve: bool = False,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Human review of a verdict
    
    POST /api/review/507f1f77bcf86cd799439011
    {
        "override_verdict": "False",
        "notes": "Additional context from expert review",
        "approve": true
    }
    """
    try:
        # Get verdict
        verdict = await db.verdicts.find_one({"_id": ObjectId(verdict_id)})
        
        if not verdict:
            raise HTTPException(status_code=404, detail="Verdict not found")
        
        # Update verdict
        update_data = {
            "human_reviewed": True,
            "updated_at": datetime.utcnow(),
            "is_published": approve
        }
        
        if override_verdict:
            update_data["verdict"] = override_verdict
        
        if notes:
            update_data["reviewer_notes"] = notes
        
        await db.verdicts.update_one(
            {"_id": ObjectId(verdict_id)},
            {"$set": update_data}
        )
        
        logger.info(f"✅ Verdict {verdict_id} reviewed")
        
        return {
            "verdict_id": verdict_id,
            "status": "reviewed",
            "approved": approve
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Review failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _create_alert(db, claim_id: str, claim_text: str, verdict_result: dict):
    """Create alert for high-harm claims"""
    try:
        alert_data = {
            "alert_type": "high_impact",
            "title": f"High Harm Score Detected: {verdict_result['verdict']}",
            "description": f"Claim: {claim_text[:200]}",
            "severity": "high" if verdict_result["harm_score"] < 90 else "critical",
            "related_claim_ids": [claim_id],
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        await db.alerts.insert_one(alert_data)
        logger.info(f"🚨 Alert created for claim {claim_id}")
        
    except Exception as e:
        logger.error(f"Failed to create alert: {e}")
