from pydantic import BaseModel, Field
from typing import List, Optional

# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class SurveyResponse(BaseModel):
    """Individual survey response"""
    text: str = Field(..., description="Response text from survey")
    respondent_id: str = Field(..., description="ID of respondent")

class SurveyData(BaseModel):
    """Parsed survey data from uploaded file"""
    responses: List[SurveyResponse] = Field(..., description="List of survey responses")
    format: str = Field(..., description="File format (csv or xlsx)")

# ============================================
# PERSONA MODELS
# ============================================

class Demographics(BaseModel):
    """Player demographics"""
    age_range: str = Field(..., description="Age range e.g., '24-32'")
    gaming_frequency: str = Field(..., description="How often they game e.g., '30+ hours per week'")
    preferred_genres: List[str] = Field(..., description="Preferred game genres")
    primary_platform: str = Field(..., description="Primary gaming platform")

class Motivations(BaseModel):
    """Player motivations"""
    primary_driver: str = Field(..., description="Main reason they play")
    engagement_factors: List[str] = Field(..., description="What keeps them engaged")
    psychological_profile: str = Field(..., description="Psychological drivers and traits")

class PainPoints(BaseModel):
    """Player pain points and frustrations"""
    frustrations: List[str] = Field(..., description="What frustrates them")
    what_they_hate: str = Field(..., description="Main dislike or pain point")

class SpendingHabits(BaseModel):
    """Player monetization profile"""
    in_game_purchase_likelihood: str = Field(..., description="Likelihood of in-game purchases")
    monetization_preference: str = Field(..., description="Preferred monetization models")
    price_sensitivity: str = Field(..., description="Price sensitivity and budget")

class PlayerPersona(BaseModel):
    """Complete player persona generated from survey data"""
    archetype_name: str = Field(..., description="Memorable persona name")
    demographics: Demographics = Field(..., description="Player demographics")
    motivations: Motivations = Field(..., description="Player motivations")
    pain_points: PainPoints = Field(..., description="Player pain points")
    spending_habits: SpendingHabits = Field(..., description="Spending and monetization habits")

# ============================================
# API RESPONSE MODELS
# ============================================

class UploadResponse(BaseModel):
    """Response from /upload endpoint"""
    status: str = Field(..., description="Status (success or error)")
    message: str = Field(..., description="Response message")
    responses_count: Optional[int] = Field(None, description="Number of responses parsed")
    format: Optional[str] = Field(None, description="File format")
    survey_data: Optional[SurveyData] = Field(None, description="Parsed survey data")

class AnalysisResponse(BaseModel):
    """Response from /analyze endpoint"""
    status: str = Field(..., description="Status (success or error)")
    message: str = Field(..., description="Response message")
    persona: Optional[PlayerPersona] = Field(None, description="Generated persona")

class ErrorResponse(BaseModel):
    """Error response"""
    status: str = Field(..., description="Error status")
    error_type: str = Field(..., description="Type of error")
    message: str = Field(..., description="Error message")
