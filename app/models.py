from sqlalchemy import Column, Integer, Float, String, DateTime 
from sqlalchemy.ext.declarative 
import declarative_base 
from datetime import datetime

Base = declarative_base()

class Telemetry(Base): 
    tablename = "telemetry" 
    id = Column(Integer, primary_key=True, index=True) 
    latitude = Column(Float) 
    longitude = Column(Float) 
    speed = Column(Float) 
    timestamp = Column(DateTime, default=datetime.utcnow)

class Detection(Base): 
    tablename = "detections" 
    id = Column(Integer, primary_key=True, index=True) 
    latitude = Column(Float) 
    longitude = Column(Float) 
    speed = Column(Float) 
    sign_type = Column(String) 
    image = Column(String) # Base64 encoded timestamp = Column(DateTime, default=datetime.utcnow)
