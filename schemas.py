"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Core schemas for the Cybersecurity recruitment app

class Job(BaseModel):
    """
    Jobs collection schema
    Collection name: "job"
    """
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    country: str = Field(..., description="Country (Cyprus or Greece)")
    city: Optional[str] = Field(None, description="City")
    employment_type: str = Field(..., description="Full-time, Part-time, Contract, Internship")
    salary_min: Optional[int] = Field(None, ge=0, description="Minimum salary (gross annual)")
    salary_max: Optional[int] = Field(None, ge=0, description="Maximum salary (gross annual)")
    description: str = Field(..., description="Role description")
    skills: List[str] = Field(default_factory=list, description="Key skills (e.g., SOC, SIEM, GRC)")
    contact_email: EmailStr = Field(..., description="Contact email for the role")
    language: str = Field("en", description="Language of the posting: en/el")

class Application(BaseModel):
    """
    Applications collection schema
    Collection name: "application"
    """
    job_id: str = Field(..., description="Referenced job id")
    name: str = Field(..., description="Candidate full name")
    email: EmailStr = Field(..., description="Candidate email")
    phone: Optional[str] = Field(None, description="Candidate phone")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    cover_letter: Optional[str] = Field(None, description="Short cover letter")
    cv_url: str = Field(..., description="Public URL to the uploaded CV file")

# Example schemas (kept for reference; not used by the app)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
