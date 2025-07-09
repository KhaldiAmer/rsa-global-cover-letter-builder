from fastapi import APIRouter, Depends, Request
from temporalio.client import Client
import os

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "app_name": os.getenv("APP_NAME", "Job Tracker MVP"),
        "app_version": os.getenv("APP_VERSION", "1.0.0")
    }

@router.get("/temporal")
async def temporal_health(request: Request):
    """Check Temporal connection health"""
    try:
        client = request.app.state.temporal_client
        # Simple connection test
        await client.list_workflows()
        return {"status": "healthy", "temporal": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "temporal": "disconnected", "error": str(e)}