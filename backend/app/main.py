from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from temporalio.client import Client
import os
import logging

from app.api import applications, health
from app.models.database import init_db

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Initialize database
    init_db()

    # Connect to Temporal Cloud
    from temporalio.client import TLSConfig

    temporal_address = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
    temporal_namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    temporal_api_key = os.getenv("TEMPORAL_API_KEY")

    if temporal_api_key:
        # Temporal Cloud connection with API key via rpc_metadata
        app.state.temporal_client = await Client.connect(
            temporal_address,
            namespace=temporal_namespace,
            tls=TLSConfig(),
            rpc_metadata={"authorization": f"Bearer {temporal_api_key}"},
        )
    else:
        # Local Temporal connection
        app.state.temporal_client = await Client.connect(
            temporal_address, namespace=temporal_namespace
        )

    logger.info("Connected to Temporal")
    yield

    # Cleanup - Temporal client doesn't have a close method
    pass


app = FastAPI(
    title=os.getenv("APP_NAME", "RSA Global Cover Letter Builder"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    lifespan=lifespan,
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", os.getenv("FRONTEND_URL", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    applications.router, prefix="/api/applications", tags=["applications"]
)
app.include_router(health.router, prefix="/api/health", tags=["health"])
