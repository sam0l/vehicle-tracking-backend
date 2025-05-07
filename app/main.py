from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import endpoints

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://vehicle-tracking-frontend.onrender.com"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include endpoints router with /api prefix
app.include_router(endpoints.router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
