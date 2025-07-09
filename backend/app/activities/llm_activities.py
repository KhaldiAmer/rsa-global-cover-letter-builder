import os
import google.generativeai as genai
from temporalio import activity
from temporalio.exceptions import ApplicationError
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


@activity.defn
def generate_cover_letter(application_data: Dict[str, Any]) -> str:
    """Generate cover letter using Gemini Flash API"""
    try:
        # Configure Gemini with optimized settings
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        # Use Gemini Flash with optimized configuration
        model = genai.GenerativeModel(
            "gemini-1.5-flash",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 800,  # Limit output for efficiency
            },
        )

        # Extract fields from application data
        company = application_data.get("company", "")
        role = application_data.get("role", "")
        job_description = application_data.get("job_description", "")
        resume = application_data.get("resume", "")
        application_id = application_data.get("id", "")

        # Build optimized prompt for Gemini Flash
        prompt = f"""
        Write a professional cover letter for this job application:
        
        Company: {company}
        Position: {role}
        Job Description: {job_description}
        My Background: {resume}
        
        Requirements:
        - Show enthusiasm for the role and company
        - Highlight relevant experience from my background
        - Explain why I'm a great fit
        - Professional but engaging tone
        - Keep it concise (300-400 words)
        - Focus on specific achievements and skills
        """

        # Generate content with error handling
        response = model.generate_content(prompt)

        if not response.text:
            raise ApplicationError(
                "Empty response from Gemini Flash", non_retryable=False
            )

        cover_letter = response.text.strip()

        logger.info(
            f"Generated cover letter for application {application_id} "
            f"using Gemini Flash"
        )
        return cover_letter

    except Exception as e:
        logger.error(f"Failed to generate cover letter with Gemini Flash: {str(e)}")
        raise ApplicationError(f"Gemini Flash API error: {str(e)}", non_retryable=False)
