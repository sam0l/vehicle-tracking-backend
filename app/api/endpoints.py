from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, database
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

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
    db_detection = models.Detection(
        latitude=data.latitude,
        longitude=data.longitude,
        speed=data.speed,
        timestamp=datetime.fromisoformat(data.timestamp),
        sign_type=data.sign_type,
        image=data.image
    )
    db.add(db_detection)
    db.commit()
    db.refresh(db_detection)
    # Invalidate cache after new detection
    FastAPICache.clear()
    return {"status": "success"}

@router.get("/detections")
@cache(expire=30)  # Cache for 30 seconds
def get_detections(db: Session = Depends(database.get_db)) -> List[dict]:
    detections = db.query(models.Detection).order_by(models.Detection.timestamp.desc()).all()
    return [
        {
            "id": d.id,
            "latitude": d.latitude,
            "longitude": d.longitude,
            "speed": d.speed,
            "timestamp": d.timestamp.isoformat(),
            "sign_type": d.sign_type,
            "image": d.image
        }
        for d in detections
    ]

@router.get("/past_detections")
@cache(expire=30)  # Cache for 30 seconds
def get_past_detections(db: Session = Depends(database.get_db)) -> List[dict]:
    # Fetch all detections except the latest 3, ordered by timestamp descending
    detections = db.query(models.Detection).order_by(models.Detection.timestamp.desc()).offset(3).all()
    return [
        {
            "id": d.id,
            "latitude": d.latitude,
            "longitude": d.longitude,
            "speed": d.speed,
            "timestamp": d.timestamp.isoformat(),
            "sign_type": d.sign_type,
            "image": d.image
        }
        for d in detections
    ]

@router.get("/health")
def health_check():
    return {"status": "OK"}
