import asyncio
import os
import logging
from temporalio.client import Client
from temporalio.worker import Worker

from app.workflows.job_application import JobApplicationWorkflow
from app.activities.llm_activities import generate_cover_letter
from app.activities.notification_activities import send_reminder_notification
from app.models.database import init_db

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


async def main():
    """Start Temporal worker"""
    # Initialize database
    init_db()

    # Connect to Temporal
    from temporalio.client import TLSConfig

    temporal_address = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
    temporal_namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    temporal_api_key = os.getenv("TEMPORAL_API_KEY")

    if temporal_api_key:
        # Temporal Cloud connection with API key via rpc_metadata
        client = await Client.connect(
            temporal_address,
            namespace=temporal_namespace,
            tls=TLSConfig(),
            rpc_metadata={"authorization": f"Bearer {temporal_api_key}"},
        )
    else:
        # Local Temporal connection
        client = await Client.connect(temporal_address, namespace=temporal_namespace)

    # Create worker with activity executor for sync activities
    import concurrent.futures

    worker = Worker(
        client,
        task_queue="job-applications",
        workflows=[JobApplicationWorkflow],
        activities=[generate_cover_letter, send_reminder_notification],
        activity_executor=concurrent.futures.ThreadPoolExecutor(max_workers=10),
    )

    logger.info("Starting Temporal worker...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
