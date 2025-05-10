from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import SimData

router = APIRouter()

@router.post("/sim-data")
def post_sim_data(payload: dict, db: Session = Depends(get_db)):
    balance = str(payload.get("balance"))
    data_usage = payload.get("data_usage")
    timestamp = datetime.utcnow()
    sim_data = SimData(balance=balance, data_usage=data_usage, timestamp=timestamp)
    db.add(sim_data)
    db.commit()
    db.refresh(sim_data)
    return {"status": "success", "id": sim_data.id}

@router.get("/sim-data")
def get_sim_data(db: Session = Depends(get_db)):
    sim_data = db.query(SimData).order_by(SimData.timestamp.desc()).first()
    if not sim_data:
        raise HTTPException(status_code=404, detail="No SIM data found")
    return {
        "balance": sim_data.balance,
        "data_usage": sim_data.data_usage,
        "timestamp": sim_data.timestamp
    }

@router.get("/sim-data/consumption")
def get_sim_data_consumption(db: Session = Depends(get_db)):
    sim_data = db.query(SimData).order_by(SimData.timestamp.desc()).first()
    if not sim_data:
        raise HTTPException(status_code=404, detail="No SIM data found")
    return {
        "data_usage": sim_data.data_usage,
        "timestamp": sim_data.timestamp
    } 