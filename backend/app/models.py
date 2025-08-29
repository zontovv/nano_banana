"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime


class DoodleRequest(BaseModel):
    """
    Request model for doodle generation.
    """
    
    occasion: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="The occasion or event to create a doodle for (in Russian, Ukrainian, or English)"
    )
    style_hint: Optional[str] = Field(
        None,
        max_length=200,
        description="Optional style hint for the doodle generation"
    )
    
    @field_validator('occasion')
    @classmethod
    def validate_occasion(cls, v: str) -> str:
        """
        Clean and validate the occasion text.
        
        Args:
            v: Occasion text
            
        Returns:
            str: Cleaned occasion text
        """
        v = v.strip()
        if not v:
            raise ValueError("Occasion cannot be empty")
        return v


class DoodleResponse(BaseModel):
    """
    Response model for doodle generation.
    """
    
    success: bool
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    occasion: str
    generation_time: float
    timestamp: datetime = Field(default_factory=datetime.now)
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """
    Health check response model.
    """
    
    status: Literal["healthy", "unhealthy"]
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)