from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
import os

app = FastAPI(
    title="Vehicle Tracking API",
    description="API for vehicle tracking system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
origins = [
    "https://vehicle-tracking-frontend.onrender.com",
    "http://localhost:3000",
    "http://localhost:8000",
    "https://vehicle-tracking-backend-bwmz.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
    allow_origin_regex=None
)

# Include router with /api prefix
app.include_router(router, prefix="/api")

@app.on_event("startup")
async def startup():
    # Only initialize Redis if we're not in development
    if os.getenv("ENVIRONMENT") != "development":
        try:
            redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
            FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        except Exception as e:
            print(f"Redis initialization failed: {e}")
            # Continue without Redis - the app will work without caching
            pass

@app.get("/")
async def root():
    return {"message": "Vehicle Tracking Backend"}
