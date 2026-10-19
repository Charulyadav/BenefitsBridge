# nodes/intake.py - Profile parsing and validation node

from typing import Dict, Any
from state import GraphState, UserProfile


def validate_profile(profile: Dict) -> tuple[bool, list[str]]:
    """Validate user profile has required fields"""
    errors = []
    
    # Required fields
    if not profile.get("state"):
        errors.append("State is required")
    
    if not profile.get("household_size") or profile.get("household_size", 0) < 1:
        errors.append("Household size must be at least 1")
    
    if profile.get("income") is None or profile.get("income", 0) < 0:
        errors.append("Income must be provided")
    
    return len(errors) == 0, errors


def normalize_profile(raw_data: Dict) -> UserProfile:
    """Normalize and fill in defaults for profile data"""
    
    # Parse children ages if string
    children_ages = raw_data.get("children_ages", [])
    if isinstance(children_ages, str):
        try:
            children_ages = [int(x.strip()) for x in children_ages.split(",") if x.strip()]
        except ValueError:
            children_ages = []
    
    # Determine if has children
    has_children = raw_data.get("has_children", len(children_ages) > 0)
    
    return UserProfile(
        # Basic info
        name=raw_data.get("name"),
        age=raw_data.get("age"),
        
        # Location
        state=raw_data.get("state", "").upper(),
        county=raw_data.get("county"),
        city=raw_data.get("city"),
        zip_code=raw_data.get("zip_code"),
        
        # Household
        household_size=int(raw_data.get("household_size", 1)),
        income=int(raw_data.get("income", 0)),
        income_type=raw_data.get("income_type"),
        
        # Family
        is_pregnant=bool(raw_data.get("is_pregnant", False)),
        is_breastfeeding=bool(raw_data.get("is_breastfeeding", False)),
        has_children=has_children,
        children_ages=children_ages,
        is_single_parent=bool(raw_data.get("is_single_parent", False)),
        
        # Employment
        is_employed=bool(raw_data.get("is_employed", False)),
        employment_type=raw_data.get("employment_type"),
        
        # Special circumstances
        is_veteran=bool(raw_data.get("is_veteran", False)),
        is_disabled=bool(raw_data.get("is_disabled", False)),
        is_student=bool(raw_data.get("is_student", False)),
        is_homeless=bool(raw_data.get("is_homeless", False)),
        is_domestic_violence_survivor=bool(raw_data.get("is_domestic_violence_survivor", False)),
        
        # Citizenship
        is_us_citizen=bool(raw_data.get("is_us_citizen", True)),
        is_legal_resident=bool(raw_data.get("is_legal_resident", True)),
        
        # Housing
        housing_situation=raw_data.get("housing_situation"),
        monthly_rent=raw_data.get("monthly_rent"),
    )


def intake_node(state: GraphState) -> Dict[str, Any]:
    """
    Process and validate user input from form.
    
    Takes raw form data and creates a normalized UserProfile.
    """
    raw_data = state.get("raw_form_data", {})
    
    if not raw_data:
        return {
            "parse_error": "No form data provided",
            "errors": ["No form data provided"]
        }
    
    # Normalize the profile
    profile = normalize_profile(raw_data)
    
    # Validate
    is_valid, errors = validate_profile(dict(profile))
    
    if not is_valid:
        return {
            "parse_error": "; ".join(errors),
            "errors": errors
        }
    
    return {
        "user_profile": profile,
        "input_method": "form",
        "errors": []
    }
