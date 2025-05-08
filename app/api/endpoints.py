from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import models, database
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
import traceback

router = APIRouter()

class DetectionData(BaseModel):
    latitude: float
    longitude: float
    speed: float
    timestamp: str
    sign_type: Optional[str] = None
    image: Optional[str] = None

@router.post("/detections")
def create_detection(data: DetectionData, db: Session = Depends(database.get_db)):
    try:
        # Log incoming data for debugging
        print(f"Received data: {data}")
        
        # Create detection record
        db_detection = models.Detection(
            latitude=data.latitude,
            longitude=data.longitude,
            speed=data.speed,
            timestamp=datetime.fromisoformat(data.timestamp),
            sign_type=data.sign_type,
            image=data.image
        )
        
        # Add and commit
        db.add(db_detection)
        db.commit()
        db.refresh(db_detection)
        
        # Invalidate cache after new detection
        FastAPICache.clear()
        
        return {"status": "success", "message": "Data received successfully"}
    except Exception as e:
        db.rollback()
        error_msg = f"Error creating detection: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/detections")
@cache(expire=30)  # Cache for 30 seconds
def get_detections(
    db: Session = Depends(database.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
) -> dict:
    try:
        # Get total count
        total = db.query(models.Detection).count()
        
        # Get paginated detections
        detections = db.query(models.Detection)\
            .order_by(models.Detection.timestamp.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "data": [
                {
                    "id": d.id,
                    "latitude": d.latitude,
                    "longitude": d.longitude,
                    "speed": d.speed,
                    "timestamp": d.timestamp.isoformat(),
                    "sign_type": d.sign_type,
                    "image": d.image[:100] + "..." if d.image and len(d.image) > 100 else d.image  # Truncate large images
                }
                for d in detections
            ]
        }
    except Exception as e:
        print(f"Error fetching detections: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/past_detections")
@cache(expire=30)  # Cache for 30 seconds
def get_past_detections(
    db: Session = Depends(database.get_db),
    skip: int = Query(3, ge=0),
    limit: int = Query(50, ge=1, le=100)
) -> List[dict]:
    # Get total count
    total = db.query(models.Detection).count()
    
    # Get paginated detections
    detections = db.query(models.Detection)\
        .order_by(models.Detection.timestamp.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": [
            {
                "id": d.id,
                "latitude": d.latitude,
                "longitude": d.longitude,
                "speed": d.speed,
                "timestamp": d.timestamp.isoformat(),
                "sign_type": d.sign_type,
                "image": d.image[:100] + "..." if d.image and len(d.image) > 100 else d.image  # Truncate large images
            }
            for d in detections
        ]
    }

@router.get("/device_status")
def get_device_status(db: Session = Depends(database.get_db)):
    try:
        # Get the most recent detection
        latest_detection = db.query(models.Detection)\
            .order_by(models.Detection.timestamp.desc())\
            .first()
        
        if not latest_detection:
            return {
                "status": "disconnected",
                "last_seen": None,
                "message": "No data available"
            }
        
        # Check if the data is recent (within 5 minutes)
        now = datetime.utcnow()
        time_diff = (now - latest_detection.timestamp).total_seconds() / 60
        
        if time_diff <= 5:
            return {
                "status": "connected",
                "last_seen": latest_detection.timestamp.isoformat(),
                "message": "Device is connected"
            }
        else:
            return {
                "status": "disconnected",
                "last_seen": latest_detection.timestamp.isoformat(),
                "message": "No recent data"
            }
    except Exception as e:
        print(f"Error checking device status: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def health_check():
    return {"status": "OK"}
