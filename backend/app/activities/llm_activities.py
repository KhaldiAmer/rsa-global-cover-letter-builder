import os
import google.generativeai as genai
from temporalio import activity
from temporalio.exceptions import ApplicationError
import logging
from typing import Dict, Any

# DSPy imports
try:
    from app.dspy_modules import get_cover_letter_optimizer
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    logging.warning("DSPy not available, falling back to direct Gemini API")

logger = logging.getLogger(__name__)


def generate_cover_letter_dspy(application_data: Dict[str, Any]) -> str:
    """Generate cover letter using DSPy-optimized prompts"""
    try:
        # Extract fields from application data
        company = application_data.get("company", "")
        role = application_data.get("role", "")
        job_description = application_data.get("job_description", "")
        resume = application_data.get("resume", "")
        application_id = application_data.get("id", "")
        
        # Get the DSPy optimizer
        optimizer = get_cover_letter_optimizer()
        
        # Setup model if not already done
        if not hasattr(optimizer, 'generator') or not optimizer.generator:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ApplicationError("GEMINI_API_KEY not found", non_retryable=True)
            
            optimizer.setup_model(api_key)
            
            # Try to optimize with sample examples
            try:
                optimizer.optimize_with_examples()
                logger.info("DSPy optimizer setup and optimized successfully")
            except Exception as e:
                logger.warning(f"DSPy optimization failed, using base generator: {e}")
        
        # Generate cover letter
        cover_letter = optimizer.generate_cover_letter(
            company=company,
            role=role,
            job_description=job_description,
            resume=resume
        )
        
        logger.info(
            f"Generated cover letter for application {application_id} using DSPy"
        )
        return cover_letter
        
    except Exception as e:
        logger.error(f"DSPy cover letter generation failed: {str(e)}")
        raise ApplicationError(f"DSPy generation error: {str(e)}", non_retryable=False)


def generate_cover_letter_fallback(application_data: Dict[str, Any]) -> str:
    """Fallback cover letter generation using direct Gemini API"""
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
            f"using fallback Gemini Flash"
        )
        return cover_letter

    except Exception as e:
        logger.error(f"Failed to generate cover letter with Gemini Flash: {str(e)}")
        raise ApplicationError(f"Gemini Flash API error: {str(e)}", non_retryable=False)


@activity.defn
def generate_cover_letter(application_data: Dict[str, Any]) -> str:
    """Generate cover letter using DSPy if available, fallback to direct API"""
    application_id = application_data.get("id", "")
    
    # Try DSPy first if available
    if DSPY_AVAILABLE:
        try:
            logger.info(f"Attempting DSPy generation for application {application_id}")
            return generate_cover_letter_dspy(application_data)
        except Exception as e:
            logger.warning(f"DSPy generation failed for application {application_id}: {e}")
            logger.info("Falling back to direct Gemini API")
    
    # Fallback to direct API
    return generate_cover_letter_fallback(application_data)
