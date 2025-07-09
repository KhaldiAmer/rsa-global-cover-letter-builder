from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta
from enum import Enum


class ApplicationStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
    REMINDER_SENT = "REMINDER_SENT"
    ARCHIVED = "ARCHIVED"


class JobApplication(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    id: str
    company: str
    role: str
    job_description: str
    resume: str
    user_email: str
    deadline_duration: timedelta
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: ApplicationStatus = ApplicationStatus.SUBMITTED


class ApplicationCreate(BaseModel):
    company: str
    role: str
    job_description: str
    resume: str
    user_email: str
    deadline_weeks: int = 4


class ApplicationResponse(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    id: str
    workflow_id: str
    status: ApplicationStatus
    company: str
    role: str
    cover_letter_available: bool = False
    reminder_sent: bool = False
    created_at: Optional[datetime] = None


class StatusUpdate(BaseModel):
    status: str
