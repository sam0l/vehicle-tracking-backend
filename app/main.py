from fastapi import FastAPI
from app.api import endpoints

app = FastAPI()

# Include endpoints router with /api prefix
app.include_router(endpoints.router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
