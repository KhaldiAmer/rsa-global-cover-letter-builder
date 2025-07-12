"""
DSPy module for cover letter generation with systematic prompt optimization.
"""

import dspy
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class CoverLetterSignature(dspy.Signature):
    """Generate a professional cover letter that matches job requirements and showcases relevant experience."""
    
    company: str = dspy.InputField(desc="Company name applying to")
    role: str = dspy.InputField(desc="Job position title")
    job_description: str = dspy.InputField(desc="Job requirements and responsibilities")
    resume: str = dspy.InputField(desc="Candidate's background, skills, and experience")
    
    cover_letter: str = dspy.OutputField(
        desc="Professional cover letter (300-400 words) showing enthusiasm, relevant experience, and fit for the role"
    )


class CoverLetterGenerator(dspy.Module):
    """DSPy module for generating optimized cover letters."""
    
    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(CoverLetterSignature)
    
    def forward(self, company: str, role: str, job_description: str, resume: str) -> dspy.Prediction:
        """Generate a cover letter using DSPy chain of thought reasoning."""
        return self.generate(
            company=company,
            role=role, 
            job_description=job_description,
            resume=resume
        )


def cover_letter_quality_metric(example, prediction, trace=None) -> float:
    """
    Evaluate cover letter quality based on multiple criteria.
    
    Returns a score between 0 and 1, where 1 is the highest quality.
    """
    if not hasattr(prediction, 'cover_letter') or not prediction.cover_letter:
        return 0.0
    
    cover_letter = prediction.cover_letter.strip()
    
    # Word count check (300-400 words optimal)
    word_count = len(cover_letter.split())
    if 300 <= word_count <= 400:
        word_score = 1.0
    elif word_count < 200:
        word_score = 0.3  # Too short
    elif word_count > 600:
        word_score = 0.5  # Too long
    else:
        # Gradually decrease score as we move away from optimal range
        word_score = max(0.6, 1 - abs(350 - word_count) / 200)
    
    # Company and role mention check
    company_mentioned = example.company.lower() in cover_letter.lower() if hasattr(example, 'company') else 0
    role_mentioned = example.role.lower() in cover_letter.lower() if hasattr(example, 'role') else 0
    
    # Professional language indicators
    professional_phrases = [
        "i am excited", "i am passionate", "i would like to", "i am writing to",
        "i believe", "my experience", "i have", "i would bring", "thank you"
    ]
    professional_score = sum(1 for phrase in professional_phrases 
                           if phrase in cover_letter.lower()) / len(professional_phrases)
    
    # Structure check (basic paragraph structure)
    paragraphs = [p.strip() for p in cover_letter.split('\n\n') if p.strip()]
    structure_score = min(1.0, len(paragraphs) / 3)  # Expect 3+ paragraphs
    
    # Combine scores
    total_score = (
        word_score * 0.3 +           # 30% weight on word count
        company_mentioned * 0.2 +    # 20% weight on company mention
        role_mentioned * 0.2 +       # 20% weight on role mention  
        professional_score * 0.2 +   # 20% weight on professional language
        structure_score * 0.1        # 10% weight on structure
    )
    
    return min(1.0, total_score)


class CoverLetterOptimizer:
    """Helper class for optimizing DSPy cover letter generation."""
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.model_name = model_name
        self.generator = None
        self.optimized_generator = None
    
    def setup_model(self, api_key: str):
        """Setup the language model for DSPy."""
        try:
            # Configure DSPy with Gemini
            lm = dspy.Google(model=self.model_name, api_key=api_key)
            dspy.settings.configure(lm=lm)
            
            # Initialize generator
            self.generator = CoverLetterGenerator()
            logger.info(f"DSPy configured with {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to setup DSPy model: {e}")
            raise
    
    def create_training_examples(self) -> list:
        """Create sample training examples for optimization."""
        examples = [
            dspy.Example(
                company="TechCorp",
                role="Software Engineer",
                job_description="Develop scalable web applications using Python and React. 5+ years experience required.",
                resume="Senior Software Engineer with 6 years experience in Python, React, and cloud technologies.",
                cover_letter="""Dear Hiring Manager,

I am excited to apply for the Software Engineer position at TechCorp. With over 6 years of experience developing scalable web applications using Python and React, I am confident I would be a valuable addition to your team.

In my current role as Senior Software Engineer, I have successfully built and deployed multiple high-traffic applications using the exact technologies mentioned in your job description. My expertise in Python backend development combined with React frontend skills aligns perfectly with your requirements.

I am particularly drawn to TechCorp's innovative approach to solving complex technical challenges. I would welcome the opportunity to contribute my experience in cloud technologies and scalable architecture to help drive your projects forward.

Thank you for considering my application. I look forward to discussing how my skills and passion for technology can benefit TechCorp.

Best regards,
[Your Name]"""
            ),
            
            dspy.Example(
                company="DataInc",
                role="Data Scientist", 
                job_description="Analyze large datasets and build ML models. PhD in Statistics or related field preferred.",
                resume="PhD in Statistics with 4 years experience in machine learning and data analysis.",
                cover_letter="""Dear DataInc Hiring Team,

I am writing to express my strong interest in the Data Scientist position at DataInc. With a PhD in Statistics and 4 years of hands-on experience in machine learning and data analysis, I am well-prepared to contribute to your data science initiatives.

My doctoral research focused on advanced statistical modeling techniques, which I have since applied to real-world problems in my professional career. I have successfully built and deployed ML models that have driven significant business value, including predictive analytics systems that improved operational efficiency by 25%.

I am particularly excited about DataInc's commitment to leveraging data for strategic decision-making. Your recent work in advanced analytics aligns perfectly with my passion for transforming complex datasets into actionable insights.

I would welcome the opportunity to discuss how my statistical expertise and practical ML experience can contribute to DataInc's continued success.

Sincerely,
[Your Name]"""
            )
        ]
        
        return examples
    
    def optimize_with_examples(self, training_examples: list = None) -> CoverLetterGenerator:
        """Optimize the generator using training examples."""
        if not self.generator:
            raise ValueError("Model must be setup first using setup_model()")
        
        if training_examples is None:
            training_examples = self.create_training_examples()
        
        try:
            # Use BootstrapFewShot for optimization
            optimizer = dspy.BootstrapFewShot(
                metric=cover_letter_quality_metric,
                max_bootstrapped_demos=4,
                max_labeled_demos=2
            )
            
            # Compile the optimized generator
            self.optimized_generator = optimizer.compile(
                self.generator,
                trainset=training_examples
            )
            
            logger.info("DSPy cover letter generator optimized successfully")
            return self.optimized_generator
            
        except Exception as e:
            logger.error(f"Failed to optimize DSPy generator: {e}")
            # Return non-optimized generator as fallback
            return self.generator
    
    def generate_cover_letter(self, company: str, role: str, job_description: str, resume: str) -> str:
        """Generate a cover letter using the optimized or base generator."""
        generator = self.optimized_generator if self.optimized_generator else self.generator
        
        if not generator:
            raise ValueError("Generator not initialized. Call setup_model() first.")
        
        try:
            result = generator(
                company=company,
                role=role,
                job_description=job_description,
                resume=resume
            )
            
            return result.cover_letter
            
        except Exception as e:
            logger.error(f"DSPy cover letter generation failed: {e}")
            raise


# Global optimizer instance
_cover_letter_optimizer = None


def get_cover_letter_optimizer() -> CoverLetterOptimizer:
    """Get or create the global cover letter optimizer instance."""
    global _cover_letter_optimizer
    
    if _cover_letter_optimizer is None:
        _cover_letter_optimizer = CoverLetterOptimizer()
    
    return _cover_letter_optimizer