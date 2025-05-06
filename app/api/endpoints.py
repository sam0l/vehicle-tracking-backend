from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ValidationError
from app import models, database
import logging
from datetime import datetime

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for validation
class TelemetryData(BaseModel):
    latitude: float
    longitude: float
    speed: float
    timestamp: str  # Expect ISO 8601 string (e.g., "2025-05-06T12:34:56")

    def to_orm_dict(self):
        data = self.dict()
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return data

class DetectionData(TelemetryData):
    sign_type: str
    image: str

@router.post("/detections")
async def create_detection(data: dict, db: Session = Depends(database.get_db)):
    logger.info(f"Received data: {data}")
    try:
        if "sign_type" in data:
            # Validate detection data
            try:
                detection_data = DetectionData(**data)
            except ValidationError as ve:
                logger.error(f"Validation error for detection data: {ve}")
                raise HTTPException(status_code=422, detail=f"Invalid detection data: {ve}")
            detection = models.Detection(**detection_data.to_orm_dict())
            db.add(detection)
            db.commit()
            db.refresh(detection)
            logger.info("Detection data saved successfully")
        else:
            # Validate telemetry data
            try:
                telemetry_data = TelemetryData(**data)
            except ValidationError as ve:
                logger.error(f"Validation error for telemetry data: {ve}")
                raise HTTPException(status_code=422, detail=f"Invalid telemetry data: {ve}")
            telemetry = models.Telemetry(**telemetry_data.to_orm_dict())
            db.add(telemetry)
            db.commit()
            db.refresh(telemetry)
            logger.info("Telemetry data saved successfully")
        return {"status": "success"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error processing detection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/telemetry")
async def get_telemetry(db: Session = Depends(database.get_db)):
    try:
        return db.query(models.Telemetry).all()
    except Exception as e:
        logger.error(f"Error fetching telemetry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching telemetry: {str(e)}")

@router.get("/detections")
async def get_detections(db: Session = Depends(database.get_db)):
    try:
        return db.query(models.Detection).all()
    except Exception as e:
        logger.error(f"Error fetching detections: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching detections: {str(e)}")
