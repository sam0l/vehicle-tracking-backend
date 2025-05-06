from fastapi import FastAPI, Depends from fastapi.middleware.cors import CORSMiddleware from .models import Base from .database import engine, get_db from .api.endpoints import router import os

app = FastAPI()

app.add_middleware( CORSMiddleware, allow_origins=[""], # Update to frontend URL after deployment allow_credentials=True, allow_methods=[""], allow_headers=["*"], )

Base.metadata.create_all(bind=engine)

app.include_router(router, prefix="/api")

@app.get("/") async def root(): return {"message": "Vehicle Tracking Backend"}
