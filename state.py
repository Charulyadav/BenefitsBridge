# state.py - LangGraph shared state schema

from typing import TypedDict, List, Optional, Annotated
from operator import add

class UserProfile(TypedDict, total=False):
    """User profile extracted from form or voice input"""
    # Basic info
    name: Optional[str]
    age: Optional[int]
    
    # Location
    state: str
    county: Optional[str]
    city: Optional[str]
    zip_code: Optional[str]
    
    # Household
    household_size: int
    income: int  # Annual household income
    income_type: Optional[str]  # "wages", "self-employment", "benefits", etc.
    
    # Family composition
    is_pregnant: bool
    is_breastfeeding: bool
    has_children: bool
    children_ages: List[int]
    is_single_parent: bool
    
    # Employment
    is_employed: bool
    employment_type: Optional[str]  # "full-time", "part-time", "unemployed"
    
    # Special circumstances
    is_veteran: bool
    is_disabled: bool
    is_student: bool
    is_homeless: bool
    is_domestic_violence_survivor: bool
    
    # Citizenship
    is_us_citizen: bool
    is_legal_resident: bool
    
    # Housing
    housing_situation: Optional[str]  # "renter", "owner", "homeless", "shelter"
    monthly_rent: Optional[int]


class SchemeResult(TypedDict):
    """Result of eligibility check for a single scheme"""
    scheme_id: str
    name: str
    category: str
    status: str  # "eligible", "likely_eligible", "maybe_eligible", "not_eligible"
    confidence: float  # 0.0 - 1.0
    reason: str
    priority_score: int
    apply_url: str
    next_steps: List[str]
    documents_needed: List[str]


class GraphState(TypedDict, total=False):
    """Main state that flows through the LangGraph"""
    
    # Input
    input_method: str  # "form" or "voice"
    voice_transcript: Optional[str]
    raw_form_data: Optional[dict]
    
    # Parsed profile
    user_profile: UserProfile
    parse_error: Optional[str]
    
    # Agent results (using Annotated with add to merge parallel results)
    benefits_results: Annotated[List[SchemeResult], add]
    healthcare_results: Annotated[List[SchemeResult], add]
    education_results: Annotated[List[SchemeResult], add]
    
    # Final output
    all_results: List[SchemeResult]
    eligible_schemes: List[SchemeResult]
    maybe_eligible_schemes: List[SchemeResult]
    not_eligible_schemes: List[SchemeResult]
    
    # Metadata
    processing_time: float
    errors: List[str]
