"""
Database Schemas for Edufuser

Each Pydantic model represents a MongoDB collection.
Collection name is the lowercase of the class name.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List


class Trainer(BaseModel):
    name: str = Field(..., description="Trainer full name")
    photo_url: Optional[str] = Field(None, description="Public URL to trainer photo")
    bio: Optional[str] = Field(None, description="Short biography")
    expertise: List[str] = Field(default_factory=list, description="Areas of expertise")
    certifications: List[str] = Field(default_factory=list, description="Certifications or notable skills")
    rating: Optional[float] = Field(4.5, ge=0, le=5, description="Average star rating")


class Testimonial(BaseModel):
    author: str = Field(..., description="Name of participant or institution representative")
    role: Optional[str] = Field(None, description="Role/Title or Institution")
    quote: str = Field(..., description="Testimonial quote text")
    rating: int = Field(5, ge=1, le=5, description="Star rating 1-5")


class ContractRequest(BaseModel):
    name: str = Field(..., description="Contact person full name")
    institution: Optional[str] = Field(None, description="Institution or company name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    training_type: Optional[str] = Field(None, description="Requested training type")
    preferred_dates: Optional[str] = Field(None, description="Preferred dates or timeframe")
    message: Optional[str] = Field(None, description="Additional details")
    trainer: Optional[str] = Field(None, description="Specific trainer requested (optional)")


class Service(BaseModel):
    title: str
    icon: Optional[str] = None
    description: Optional[str] = None
