import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from temporalio import activity
from temporalio.exceptions import ApplicationError
import logging

logger = logging.getLogger(__name__)

@activity.defn
def send_reminder_notification(notification_data: dict) -> bool:
    """Send reminder notification via email"""
    try:
        # For demo purposes, we'll just log the notification
        # In production, you'd integrate with email service (SendGrid, etc.)
        
        user_email = notification_data["user_email"]
        company = notification_data["company"]
        role = notification_data["role"]
        application_id = notification_data["application_id"]
        
        message = f"""
        Subject: Reminder: Follow up on your application to {company}
        
        Dear Applicant,
        
        This is a reminder that you applied for the {role} position at {company}.
        It's been a while since you submitted your application, and you might want to follow up.
        
        Application ID: {application_id}
        
        Consider:
        - Sending a polite follow-up email
        - Connecting with the hiring manager on LinkedIn
        - Checking for any updates on the company's career page
        
        Best regards,
        Job Tracker MVP
        """
        
        logger.info(f"Reminder notification sent to {user_email} for application {application_id}")
        logger.info(f"Notification content: {message}")
        
        # In production, you would send actual email here
        return True
        
    except Exception as e:
        logger.error(f"Failed to send reminder notification: {str(e)}")
        raise ApplicationError(
            f"Notification error: {str(e)}",
            non_retryable=False
        )