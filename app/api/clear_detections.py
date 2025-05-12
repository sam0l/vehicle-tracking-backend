from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, database
import traceback

router = APIRouter()

@router.post("/clear_detections")
def clear_all_detections(db: Session = Depends(database.get_db)):
    """
    Clear all detection records from the database.
    WARNING: This is a destructive operation that cannot be undone.
    """
    try:
        # Count detections before deletion
        detection_count = db.query(models.Detection).count()
        
        # Delete all records from the detections table
        db.query(models.Detection).delete()
        db.commit()
        
        return {
            "status": "success", 
            "message": f"Successfully cleared {detection_count} detection records"
        }
    except Exception as e:
        db.rollback()
        error_msg = f"Error clearing detections: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=error_msg) 