from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import models, database
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
import traceback
import pytz

router = APIRouter()

# Define Singapore timezone
SGT = pytz.timezone('Asia/Singapore')

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
        
        # Parse timestamp, ensure it's UTC, and convert to naive UTC for storage
        aware_dt = datetime.fromisoformat(data.timestamp)
        # Ensure it's UTC. If it's already UTC, astimezone(pytz.utc) is a no-op.
        # If it's naive, this would assume local system time, but edge sends aware UTC.
        if aware_dt.tzinfo is None or aware_dt.tzinfo.utcoffset(aware_dt) != timedelta(0):
            print(f"Warning: Incoming timestamp {data.timestamp} was not UTC or tz-naive, converting to UTC.")
            aware_utc_dt = aware_dt.astimezone(pytz.utc)
        else:
            aware_utc_dt = aware_dt
        naive_utc_dt_for_storage = aware_utc_dt.replace(tzinfo=None)
        
        # Create detection record
        db_detection = models.Detection(
            latitude=data.latitude,
            longitude=data.longitude,
            speed=data.speed,
            timestamp=naive_utc_dt_for_storage,
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
                    # Timestamp from DB (d.timestamp) is naive UTC. Convert to SGT for display.
                    "timestamp": pytz.utc.localize(d.timestamp).astimezone(SGT).isoformat(),
                    "sign_type": d.sign_type,
                    "image": d.image  # Don't truncate the image data
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
                # Timestamp from DB (d.timestamp) is naive UTC. Convert to SGT for display.
                "timestamp": pytz.utc.localize(d.timestamp).astimezone(SGT).isoformat(),
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
        
        # Timestamp from DB is naive UTC. Convert to SGT for display.
        retrieved_naive_utc_dt = latest_detection.timestamp
        aware_sgt_timestamp = pytz.utc.localize(retrieved_naive_utc_dt).astimezone(SGT)
        
        # Check if device is connected
        current_time_sgt = datetime.now(SGT) # Use SGT for comparison with SGT timestamp
        time_diff = (current_time_sgt - aware_sgt_timestamp).total_seconds() / 60
        
        if time_diff <= 60:  # Increased threshold to 60 seconds
            return {
                "status": "connected",
                "last_seen": aware_sgt_timestamp.isoformat(),
                "message": "Device is connected"
            }
        else:
            return {
                "status": "disconnected",
                "last_seen": aware_sgt_timestamp.isoformat(),
                "message": f"No recent data. Last seen {int(time_diff)} seconds ago."
            }
    except Exception as e:
        print(f"Error checking device status: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
def health_check():
    return {"status": "OK"}
