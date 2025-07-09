from fastapi import APIRouter, HTTPException, Depends, Request
from temporalio.client import Client
from typing import List
import uuid
from datetime import timedelta
import logging

from app.models.application import (
    JobApplication,
    ApplicationCreate,
    ApplicationResponse,
    ApplicationStatus,
    StatusUpdate,
)
from app.workflows.job_application import JobApplicationWorkflow
from app.models.database import (
    get_db,
    save_application,
    get_application,
    get_all_applications,
)

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_temporal_client(request: Request) -> Client:
    return request.app.state.temporal_client


@router.post("/", response_model=ApplicationResponse)
async def create_application(
    application_data: ApplicationCreate,
    client: Client = Depends(get_temporal_client),
    db=Depends(get_db),
):
    """Create new job application and start workflow"""
    # Create application instance
    application = JobApplication(
        id=str(uuid.uuid4()),
        company=application_data.company,
        role=application_data.role,
        job_description=application_data.job_description,
        resume=application_data.resume,
        user_email=application_data.user_email,
        deadline_duration=timedelta(weeks=application_data.deadline_weeks),
    )

    # Save to database
    save_application(db, application)

    # Start Temporal workflow with serializable data
    workflow_data = {
        "id": application.id,
        "company": application.company,
        "role": application.role,
        "job_description": application.job_description,
        "resume": application.resume,
        "user_email": application.user_email,
        "deadline_duration_seconds": int(application.deadline_duration.total_seconds()),
        "created_at": application.created_at.isoformat(),
        "status": application.status.value,
    }

    handle = await client.start_workflow(
        JobApplicationWorkflow.run,
        workflow_data,
        id=f"job-app-{application.id}",
        task_queue="job-applications",
    )

    return ApplicationResponse(
        id=application.id,
        workflow_id=handle.id,
        status=ApplicationStatus.SUBMITTED,
        company=application.company,
        role=application.role,
        created_at=application.created_at,
    )


@router.get("/", response_model=List[ApplicationResponse])
async def list_applications(
    client: Client = Depends(get_temporal_client), db=Depends(get_db)
):
    """List all job applications with current status"""
    applications = get_all_applications(db)
    responses = []

    for app in applications:
        try:
            handle = client.get_workflow_handle(f"job-app-{app.id}")
            status = await handle.query(JobApplicationWorkflow.get_current_status)

            responses.append(
                ApplicationResponse(
                    id=app.id,
                    workflow_id=f"job-app-{app.id}",
                    status=ApplicationStatus(status["status"]),
                    company=app.company,
                    role=app.role,
                    cover_letter_available=status["cover_letter_available"],
                    reminder_sent=status["reminder_sent"],
                    created_at=app.created_at,
                )
            )
        except Exception as e:
            logger.error(f"Error querying workflow {app.id}: {str(e)}")
            # Return application with basic info if workflow query fails
            responses.append(
                ApplicationResponse(
                    id=app.id,
                    workflow_id=f"job-app-{app.id}",
                    status=ApplicationStatus.SUBMITTED,
                    company=app.company,
                    role=app.role,
                    created_at=app.created_at,
                )
            )

    return responses


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application_detail(
    application_id: str,
    client: Client = Depends(get_temporal_client),
    db=Depends(get_db),
):
    """Get specific application details"""
    application = get_application(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    try:
        handle = client.get_workflow_handle(f"job-app-{application_id}")
        status = await handle.query(JobApplicationWorkflow.get_current_status)

        return ApplicationResponse(
            id=application.id,
            workflow_id=f"job-app-{application.id}",
            status=ApplicationStatus(status["status"]),
            company=application.company,
            role=application.role,
            cover_letter_available=status["cover_letter_available"],
            reminder_sent=status["reminder_sent"],
            created_at=application.created_at,
        )
    except Exception as e:
        logger.error(f"Error querying workflow {application_id}: {str(e)}")
        # Return application with basic info if workflow query fails
        # Try to get cover letter status as fallback
        try:
            handle = client.get_workflow_handle(f"job-app-{application_id}")
            cover_letter = await handle.query(JobApplicationWorkflow.get_cover_letter)
            cover_letter_available = bool(cover_letter)
        except Exception:
            cover_letter_available = False

        return ApplicationResponse(
            id=application.id,
            workflow_id=f"job-app-{application.id}",
            status=ApplicationStatus.SUBMITTED,
            company=application.company,
            role=application.role,
            cover_letter_available=cover_letter_available,
            reminder_sent=False,
            created_at=application.created_at,
        )


@router.post("/{application_id}/status")
async def update_application_status(
    application_id: str,
    status_update: StatusUpdate,
    client: Client = Depends(get_temporal_client),
):
    """Update application status via Temporal signal"""
    try:
        handle = client.get_workflow_handle(f"job-app-{application_id}")
        await handle.signal(
            JobApplicationWorkflow.update_status,
            ApplicationStatus(status_update.status),
        )

        return {"message": "Status updated successfully"}
    except Exception as e:
        logger.error(f"Error updating status for {application_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{application_id}/cover-letter")
async def get_cover_letter(
    application_id: str, client: Client = Depends(get_temporal_client)
):
    """Get generated cover letter"""
    try:
        handle = client.get_workflow_handle(f"job-app-{application_id}")
        cover_letter = await handle.query(JobApplicationWorkflow.get_cover_letter)

        if not cover_letter:
            raise HTTPException(
                status_code=404, detail="Cover letter not yet generated"
            )

        return {"cover_letter": cover_letter}
    except Exception as e:
        logger.error(f"Error getting cover letter for {application_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
