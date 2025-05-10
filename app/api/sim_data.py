from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import time

router = APIRouter(prefix="/api/sim-data", tags=["sim-data"])

# In-memory storage for SIM data (in production, use database)
sim_data = {
    'balance': None,
    'consumption': {
        'current_rate': 0,
        'total_bytes': 0,
        'last_update': None
    }
}

class SimDataUpdate(BaseModel):
    balance: float
    unit: str
    timestamp: Optional[int] = None

class DataConsumptionUpdate(BaseModel):
    current_rate: float
    total_bytes: float
    timestamp: Optional[int] = None

@router.get("/")
async def get_sim_data():
    """Get current SIM data balance."""
    if not sim_data['balance']:
        raise HTTPException(status_code=404, detail="No SIM data available")
    return sim_data['balance']

@router.get("/consumption")
async def get_data_consumption():
    """Get current data consumption statistics."""
    return sim_data['consumption']

@router.post("/")
async def update_sim_data(data: SimDataUpdate):
    """Update SIM data from edge device."""
    try:
        sim_data['balance'] = {
            'balance': data.balance,
            'unit': data.unit,
            'timestamp': data.timestamp or int(time.time())
        }
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/consumption")
async def update_data_consumption(data: DataConsumptionUpdate):
    """Update data consumption statistics from edge device."""
    try:
        sim_data['consumption'] = {
            'current_rate': data.current_rate,
            'total_bytes': data.total_bytes,
            'last_update': data.timestamp or int(time.time())
        }
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 