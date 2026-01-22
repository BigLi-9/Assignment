import logging
import json
import asyncio
import google.generativeai as genai
from typing import Optional
from app.models import (
    PlayerPersona, Demographics, Motivations, PainPoints, SpendingHabits
)
from app.config import settings

logger = logging.getLogger(__name__)

class GeminiAnalyzer:
    """Analyze survey data using Gemini API"""
    
    def __init__(self):
        try:
            genai.configure(api_key=settings.gemini_api_key)
            # Use gemini-2.5-flash (free tier compatible)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.logger = logger
            self.logger.info("Gemini API initialized successfully (gemini-2.5-flash)")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini: {str(e)}")
            raise
    
    def create_analysis_prompt(self, survey_responses: list) -> str:
        """Create a prompt for Gemini to analyze survey data"""
        
        responses_text = "\n".join([f"- {resp}" for resp in survey_responses])
        
        prompt = f"""You are an expert game design analyst specializing in player psychology and experience design.

Analyze the following player survey responses and create a detailed player persona.

SURVEY RESPONSES:
{responses_text}

Generate a comprehensive player persona with these EXACT JSON structure (no markdown, pure JSON):

{{
  "archetype_name": "A memorable persona name (e.g., 'The Curious Adventurer')",
  "demographics": {{
    "age_range": "e.g., '24-32'",
    "gaming_frequency": "e.g., '30+ hours per week'",
    "preferred_genres": ["list", "of", "genres"],
    "primary_platform": "e.g., 'PC'"
  }},
  "motivations": {{
    "primary_driver": "Main reason they play",
    "engagement_factors": ["what", "keeps", "them", "engaged"],
    "psychological_profile": "Description of psychological drivers"
  }},
  "pain_points": {{
    "frustrations": ["what", "frustrates", "them"],
    "what_they_hate": "Main dislike or pain point"
  }},
  "spending_habits": {{
    "in_game_purchase_likelihood": "e.g., 'Moderate - would pay for story DLC'",
    "monetization_preference": "e.g., 'Battle Pass or Story DLC'",
    "price_sensitivity": "e.g., 'Willing to pay 20+ for significant content'"
  }}
}}

IMPORTANT:
- Return ONLY valid JSON, no markdown or extra text
- Base all information on the actual survey responses
- Be specific and actionable in descriptions
- Focus on game player psychology, not generic personas
- All fields must be populated based on the survey data
"""
        return prompt
    
    async def analyze_survey(self, survey_responses: list, game_title: Optional[str] = None) -> PlayerPersona:
        """
        Analyze survey responses and generate player persona
        
        Args:
            survey_responses: List of survey response texts
            game_title: Optional game title for context
            
        Returns:
            PlayerPersona object with analysis results
        """
        try:
            self.logger.info(f"Starting analysis of {len(survey_responses)} responses")
            
            # Create prompt
            prompt = self.create_analysis_prompt(survey_responses)
            
            # Call Gemini API
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=2048,
                    )
                )
            )
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            response_text = response_text.strip()
            
            self.logger.info(f"Gemini response received, parsing JSON")
            
            # Parse JSON
            persona_data = json.loads(response_text)
            
            # Validate and create PersonaResponse model
            persona = PlayerPersona(
                archetype_name=persona_data["archetype_name"],
                demographics=Demographics(**persona_data["demographics"]),
                motivations=Motivations(**persona_data["motivations"]),
                pain_points=PainPoints(**persona_data["pain_points"]),
                spending_habits=SpendingHabits(**persona_data["spending_habits"])
            )
            
            self.logger.info(f"✓ Persona generated successfully: {persona.archetype_name}")
            
            return persona
        
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse Gemini JSON response: {str(e)}")
            raise ValueError(f"Failed to parse API response as JSON")
        
        except Exception as e:
            self.logger.error(f"Gemini analysis error: {str(e)}")
            raise


# Create singleton instance
analyzer = GeminiAnalyzer()
