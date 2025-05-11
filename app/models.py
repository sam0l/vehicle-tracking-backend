from sqlalchemy import Column, Integer, Float, String, Text, DateTime
from app.base import Base

class Telemetry(Base):
    __tablename__ = "telemetry"
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)

class Detection(Base):
    __tablename__ = "detections"
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed = Column(Float, nullable=False)
    sign_type = Column(String, nullable=True)
    image = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=False)

class DataUsage(Base):
    __tablename__ = "data_usage"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    bytes_sent = Column(Integer, nullable=False)
    bytes_received = Column(Integer, nullable=False)
