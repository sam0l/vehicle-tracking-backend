from fastapi import APIRouter, Depends from sqlalchemy.orm import Session from ..models import Telemetry, Detection from ..database import get_db from datetime import datetime

router = APIRouter()

@router.post("/detections") async def receive_data(data: dict, db: Session = Depends(get_db)): try: if 'image' in data: detection = Detection( latitude=data['latitude'], longitude=data['longitude'], speed=data['speed'], sign_type=data['sign_type'], image=data['image'], timestamp=datetime.fromtimestamp(data['timestamp']) ) db.add(detection) else: telemetry = Telemetry( latitude=data['latitude'], longitude=data['longitude'], speed=data['speed'], timestamp=datetime.fromtimestamp(data['timestamp']) ) db.add(telemetry) db.commit() return {"status": "success"} except Exception as e: print(f"Error storing data: {e}") return {"status": "error", "message": str(e)}

@router.get("/telemetry") async def get_telemetry(db: Session = Depends(get_db)): try: telemetry = db.query(Telemetry).all() return [{"latitude": t.latitude, "longitude": t.longitude, "speed": t.speed, "timestamp": t.timestamp} for t in telemetry] except Exception as e: print(f"Error fetching telemetry: {e}") return {"status": "error", "message": str(e)}

@router.get("/detections") async def get_detections(db: Session = Depends(get_db)): try: detections = db.query(Detection).all() return [{"latitude": d.latitude, "longitude": d.longitude, "speed": d.speed, "sign_type": d.sign_type, "image": d.image, "timestamp": d.timestamp} for d in detections] except Exception as e: print(f"Error fetching detections: {e}") return {"status": "error", "message": str(e)}
