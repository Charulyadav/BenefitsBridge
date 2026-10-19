# models/scheme.py - Pydantic models for schemes

from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class SchemeLevel(str, Enum):
    FEDERAL = "federal"
    STATE = "state"
    COUNTY = "county"
    CITY = "city"


class SchemeCategory(str, Enum):
    NUTRITION = "nutrition"
    HEALTHCARE = "healthcare"
    HOUSING = "housing"
    CHILDCARE = "childcare"
    EDUCATION = "education"
    FINANCIAL = "financial"
    EMPLOYMENT = "employment"
    SAFETY = "safety"
    UTILITIES = "utilities"


class EligibilityCriteria(BaseModel):
    """Eligibility criteria for a scheme"""
    
    # Income limits
    max_income_percent_fpl: Optional[int] = Field(
        None, 
        description="Maximum income as percentage of Federal Poverty Level (e.g., 130 = 130% FPL)"
    )
    max_income_absolute: Optional[int] = Field(
        None,
        description="Maximum absolute income in dollars"
    )
    
    # Age requirements
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    
    # Family requirements
    requires_children: bool = False
    max_child_age: Optional[int] = None
    min_child_age: Optional[int] = None
    requires_pregnancy: bool = False
    requires_breastfeeding: bool = False
    
    # Employment
    requires_employment: bool = False
    requires_unemployment: bool = False
    
    # Special circumstances
    requires_veteran_status: bool = False
    requires_disability: bool = False
    requires_student_status: bool = False
    domestic_violence_priority: bool = False
    homeless_priority: bool = False
    
    # Citizenship
    citizenship_required: bool = True
    legal_resident_ok: bool = True
    
    # Asset limits
    max_assets: Optional[int] = None
    
    # Custom rules (for complex eligibility)
    custom_rules: Optional[str] = Field(
        None,
        description="Free-text description of additional eligibility rules"
    )


class Scheme(BaseModel):
    """A government benefit scheme/program"""
    
    # Identification
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Display name")
    short_name: Optional[str] = Field(None, description="Abbreviated name")
    description: str = Field(..., description="Brief description")
    
    # Classification
    category: SchemeCategory
    level: SchemeLevel
    
    # Geographic scope
    state: Optional[str] = Field(None, description="State code (e.g., 'TX')")
    county: Optional[str] = Field(None, description="County name")
    city: Optional[str] = Field(None, description="City name")
    
    # Eligibility
    criteria: EligibilityCriteria
    
    # Application information
    apply_url: str = Field(..., description="URL to apply")
    apply_phone: Optional[str] = None
    apply_in_person: Optional[str] = Field(None, description="Address for in-person applications")
    
    next_steps: List[str] = Field(default_factory=list)
    documents_needed: List[str] = Field(default_factory=list)
    processing_time: Optional[str] = Field(None, description="e.g., '2-4 weeks'")
    
    # Benefits details
    benefit_amount: Optional[str] = Field(None, description="e.g., '$234/month average'")
    benefit_type: Optional[str] = Field(None, description="e.g., 'EBT Card', 'Direct Deposit'")
    
    # Admin metadata
    is_active: bool = True
    priority_score: int = Field(5, ge=1, le=10, description="Display priority (higher = show first)")
    added_by: str = Field(..., description="Admin email who added this")
    last_updated: str = Field(..., description="ISO date of last update")
    
    # Optional
    tags: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=lambda: ["en"])


class SchemeDatabase(BaseModel):
    """Container for all schemes"""
    schemes: List[Scheme]
    last_updated: str
    version: str = "1.0"
