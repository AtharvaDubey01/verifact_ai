"""
Feedback Router
Endpoints for user feedback and appeals
"""

from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from loguru import logger

from database.connection import get_database
from models.schemas import FeedbackBase, FeedbackInDB


router = APIRouter()


@router.post("/feedback")
async def submit_feedback(
    feedback: FeedbackBase,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Submit feedback or appeal for a claim
    
    POST /api/feedback
    {
        "claim_id": "507f1f77bcf86cd799439011",
        "feedback_type": "correction",
        "content": "This verdict is incorrect because...",
        "user_email": "user@example.com",
        "supporting_links": ["https://..."]
    }
    """
    try:
        # Verify claim exists
        from bson import ObjectId
        claim = await db.claims.find_one({"_id": ObjectId(feedback.claim_id)})
        
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        # Create feedback document
        feedback_data = FeedbackInDB(**feedback.dict())
        
        # Insert
        result = await db.feedback.insert_one(
            feedback_data.dict(by_alias=True, exclude={"id"})
        )
        
        feedback_id = str(result.inserted_id)
        
        logger.info(f"✅ Feedback submitted: {feedback_id}")
        
        return {
            "feedback_id": feedback_id,
            "status": "submitted",
            "message": "Thank you for your feedback. It will be reviewed by our team."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/{claim_id}")
async def get_claim_feedback(
    claim_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get all feedback for a claim
    
    GET /api/feedback/507f1f77bcf86cd799439011
    """
    try:
        cursor = db.feedback.find({"claim_id": claim_id}).sort("created_at", -1)
        feedback_list = await cursor.to_list(length=100)
        
        # Format
        for feedback in feedback_list:
            feedback["id"] = str(feedback.pop("_id"))
        
        return {
            "claim_id": claim_id,
            "feedback": feedback_list,
            "total": len(feedback_list)
        }
        
    except Exception as e:
        logger.error(f"Failed to get feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))
