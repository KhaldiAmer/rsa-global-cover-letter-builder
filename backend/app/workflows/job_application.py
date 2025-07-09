from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy
from typing import Optional, Dict, Any
import logging

from app.models.application import ApplicationStatus

logger = logging.getLogger(__name__)


@workflow.defn
class JobApplicationWorkflow:
    def __init__(self):
        self.status = ApplicationStatus.SUBMITTED
        self.cover_letter: Optional[str] = None
        self.reminder_sent = False
        self.updates_received = 0

    @workflow.run
    async def run(self, application_data: Dict[str, Any]) -> dict:
        """Main workflow execution"""
        # Step 1: Generate cover letter
        self.cover_letter = await workflow.execute_activity(
            "generate_cover_letter",
            application_data,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=2),
                backoff_coefficient=2.0,
            ),
        )

        # Step 2: Wait for deadline with periodic checks
        deadline_reached = await self._wait_for_deadline_or_update(application_data)

        # Step 3: Handle deadline reached
        if deadline_reached and self.status == ApplicationStatus.SUBMITTED:
            await self._handle_deadline_reached(application_data)

        # Step 4: Grace period before auto-archive
        if self.status in [
            ApplicationStatus.SUBMITTED,
            ApplicationStatus.REMINDER_SENT,
        ]:
            await workflow.sleep(timedelta(days=7))  # Grace period
            if self.status not in [
                ApplicationStatus.INTERVIEW,
                ApplicationStatus.OFFER,
                ApplicationStatus.REJECTED,
            ]:
                self.status = ApplicationStatus.ARCHIVED
                logger.info(f"Auto-archived application {application_data['id']}")

        return {
            "application_id": application_data["id"],
            "final_status": self.status.value,
            "cover_letter_generated": bool(self.cover_letter),
            "updates_received": self.updates_received,
        }

    async def _wait_for_deadline_or_update(
        self, application_data: Dict[str, Any]
    ) -> bool:
        """Wait for deadline or status update"""
        # Simple approach: just sleep for the deadline duration
        # If status changes during this time, it will be handled elsewhere
        await workflow.sleep(
            timedelta(seconds=application_data["deadline_duration_seconds"])
        )

        # If we reach here, the deadline has passed
        return True

    async def _handle_deadline_reached(self, application_data: Dict[str, Any]):
        """Handle deadline reached without update"""
        self.status = ApplicationStatus.REMINDER_SENT
        self.reminder_sent = True

        await workflow.execute_activity(
            "send_reminder_notification",
            {
                "user_email": application_data["user_email"],
                "company": application_data["company"],
                "role": application_data["role"],
                "application_id": application_data["id"],
            },
            start_to_close_timeout=timedelta(seconds=30),
        )

    @workflow.signal
    async def update_status(self, new_status):
        """Signal to update application status"""
        # Handle case where new_status might be a list
        if isinstance(new_status, list):
            if len(new_status) > 0:
                status_value = new_status[0]
            else:
                logger.warning("Received empty list for status update")
                return
        else:
            status_value = new_status

        # Convert string to ApplicationStatus enum if needed
        if isinstance(status_value, str):
            try:
                self.status = ApplicationStatus(status_value)
            except ValueError:
                logger.error(f"Invalid status value: {status_value}")
                return
        else:
            self.status = status_value

        self.updates_received += 1
        logger.info(f"Status updated to {self.status.value}")

    @workflow.query
    def get_current_status(self) -> dict:
        """Query current workflow state"""
        return {
            "status": self.status.value,
            "cover_letter_available": bool(self.cover_letter),
            "reminder_sent": self.reminder_sent,
            "updates_received": self.updates_received,
        }

    @workflow.query
    def get_cover_letter(self) -> Optional[str]:
        """Query generated cover letter"""
        return self.cover_letter
