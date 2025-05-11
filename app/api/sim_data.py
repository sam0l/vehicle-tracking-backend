from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models import DataUsage

router = APIRouter()

@router.post("/data-usage")
def post_data_usage(payload: dict, db: Session = Depends(get_db)):
    try:
        timestamp = datetime.fromisoformat(payload.get("timestamp")) if payload.get("timestamp") else datetime.utcnow()
        bytes_sent = int(payload.get("bytes_sent", 0))
        bytes_received = int(payload.get("bytes_received", 0))
        usage = DataUsage(timestamp=timestamp, bytes_sent=bytes_sent, bytes_received=bytes_received)
        db.add(usage)
        db.commit()
        db.refresh(usage)
        return {"status": "success", "id": usage.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/data-usage")
def get_data_usage(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    def get_stats(period_seconds):
        cutoff = now - timedelta(seconds=period_seconds)
        records = db.query(DataUsage).filter(DataUsage.timestamp >= cutoff).order_by(DataUsage.timestamp.asc()).all()
        total_sent = sum(r.bytes_sent for r in records)
        total_received = sum(r.bytes_received for r in records)
        points = [
            {"timestamp": r.timestamp.isoformat(), "bytes_sent": r.bytes_sent, "bytes_received": r.bytes_received}
            for r in records
        ]
        return {"bytes_sent": total_sent, "bytes_received": total_received, "points": points}
    return {
        "1d": get_stats(86400),
        "1w": get_stats(7*86400),
        "1m": get_stats(30*86400)
    } 