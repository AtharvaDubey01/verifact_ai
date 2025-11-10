"""
Alerts Router
Endpoints for alert management
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from loguru import logger

from database.connection import get_database


router = APIRouter()


@router.get("/alerts")
async def get_alerts(
    severity: Optional[str] = Query(None),
    is_active: bool = Query(True),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get alerts with filters
    
    GET /api/alerts?severity=high&is_active=true&limit=20
    """
    try:
        query = {"is_active": is_active}
        
        if severity:
            query["severity"] = severity
        
        cursor = db.alerts.find(query).sort("created_at", -1).limit(limit)
        alerts = await cursor.to_list(length=limit)
        
        # Format
        for alert in alerts:
            alert["id"] = str(alert.pop("_id"))
        
        return {
            "alerts": alerts,
            "total": len(alerts)
        }
        
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Mark an alert as resolved
    
    POST /api/alerts/507f1f77bcf86cd799439011/resolve
    """
    try:
        from datetime import datetime
        
        result = await db.alerts.update_one(
            {"_id": ObjectId(alert_id)},
            {
                "$set": {
                    "is_active": False,
                    "resolved_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        logger.info(f"✅ Alert {alert_id} resolved")
        
        return {
            "alert_id": alert_id,
            "status": "resolved"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/subscribe")
async def subscribe_to_alerts(
    email: str,
    severity_threshold: str = "medium",
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Subscribe to alert notifications
    
    POST /api/alerts/subscribe
    {
        "email": "user@example.com",
        "severity_threshold": "high"
    }
    """
    # This is a placeholder for email subscription logic
    # In production, integrate with email service or webhook system
    
    logger.info(f"Alert subscription: {email} (threshold: {severity_threshold})")
    
    return {
        "status": "subscribed",
        "email": email,
        "severity_threshold": severity_threshold,
        "message": "You will receive alerts via email"
    }
