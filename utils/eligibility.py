# utils/eligibility.py - Eligibility calculation helpers

from typing import Dict, List, Tuple, Optional
from config import get_fpl


def calculate_fpl_percentage(income: int, household_size: int) -> int:
    """Calculate income as percentage of Federal Poverty Level"""
    fpl = get_fpl(household_size)
    if fpl == 0:
        return 0
    return int((income / fpl) * 100)


def check_income_eligibility(
    income: int,
    household_size: int,
    max_income_percent_fpl: Optional[int] = None,
    max_income_absolute: Optional[int] = None
) -> Tuple[bool, str]:
    """
    Check if income meets eligibility criteria.
    Returns (is_eligible, reason)
    """
    fpl_percentage = calculate_fpl_percentage(income, household_size)
    
    # Check FPL-based limit
    if max_income_percent_fpl is not None:
        if fpl_percentage <= max_income_percent_fpl:
            return True, f"Income is {fpl_percentage}% of FPL (limit: {max_income_percent_fpl}%)"
        else:
            return False, f"Income is {fpl_percentage}% of FPL, exceeds {max_income_percent_fpl}% limit"
    
    # Check absolute limit
    if max_income_absolute is not None:
        if income <= max_income_absolute:
            return True, f"Income ${income:,} is below ${max_income_absolute:,} limit"
        else:
            return False, f"Income ${income:,} exceeds ${max_income_absolute:,} limit"
    
    # No income limit specified
    return True, "No income limit for this program"


def check_age_eligibility(
    age: Optional[int],
    min_age: Optional[int] = None,
    max_age: Optional[int] = None
) -> Tuple[bool, str]:
    """Check age eligibility"""
    if age is None:
        return True, "Age not specified"
    
    if min_age is not None and age < min_age:
        return False, f"Age {age} is below minimum age {min_age}"
    
    if max_age is not None and age > max_age:
        return False, f"Age {age} exceeds maximum age {max_age}"
    
    return True, "Age requirement met"


def check_children_eligibility(
    has_children: bool,
    children_ages: List[int],
    requires_children: bool = False,
    max_child_age: Optional[int] = None,
    min_child_age: Optional[int] = None
) -> Tuple[bool, str]:
    """Check children-related eligibility"""
    
    if requires_children and not has_children:
        return False, "Program requires children in household"
    
    if not has_children or not children_ages:
        if requires_children:
            return False, "Program requires children in household"
        return True, "No children requirements"
    
    # Check child age limits
    if max_child_age is not None:
        qualifying_children = [age for age in children_ages if age <= max_child_age]
        if not qualifying_children:
            return False, f"No children under age {max_child_age}"
        return True, f"Has {len(qualifying_children)} child(ren) under {max_child_age}"
    
    if min_child_age is not None:
        qualifying_children = [age for age in children_ages if age >= min_child_age]
        if not qualifying_children:
            return False, f"No children over age {min_child_age}"
    
    return True, "Children eligibility met"


def check_basic_eligibility(
    profile: Dict,
    criteria: Dict
) -> Tuple[str, float, str]:
    """
    Quick eligibility check based on basic criteria.
    Returns (status, confidence, reason)
    
    Status: "eligible", "likely_eligible", "maybe_eligible", "not_eligible"
    """
    reasons = []
    is_eligible = True
    confidence = 1.0
    
    # Check income
    if criteria.get("max_income_percent_fpl") or criteria.get("max_income_absolute"):
        income_ok, income_reason = check_income_eligibility(
            profile.get("income", 0),
            profile.get("household_size", 1),
            criteria.get("max_income_percent_fpl"),
            criteria.get("max_income_absolute")
        )
        reasons.append(income_reason)
        if not income_ok:
            return "not_eligible", 0.9, income_reason
    
    # Check citizenship
    if criteria.get("citizenship_required", False):
        is_citizen = profile.get("is_us_citizen", True)
        is_legal_resident = profile.get("is_legal_resident", True)
        legal_ok = criteria.get("legal_resident_ok", True)
        
        if not is_citizen and not (legal_ok and is_legal_resident):
            return "not_eligible", 0.95, "Citizenship/residency requirement not met"
    
    # Check children requirement
    if criteria.get("requires_children", False):
        children_ok, children_reason = check_children_eligibility(
            profile.get("has_children", False),
            profile.get("children_ages", []),
            requires_children=True,
            max_child_age=criteria.get("max_child_age"),
            min_child_age=criteria.get("min_child_age")
        )
        reasons.append(children_reason)
        if not children_ok:
            return "not_eligible", 0.9, children_reason
    
    # Check pregnancy requirement
    if criteria.get("requires_pregnancy", False):
        if not profile.get("is_pregnant", False):
            return "not_eligible", 0.95, "Program requires pregnancy"
    
    # Check employment requirements
    if criteria.get("requires_employment", False):
        if not profile.get("is_employed", False):
            return "not_eligible", 0.85, "Program requires employment"
    
    if criteria.get("requires_unemployment", False):
        if profile.get("is_employed", False):
            return "not_eligible", 0.85, "Program requires unemployment"
    
    # Check veteran status
    if criteria.get("requires_veteran_status", False):
        if not profile.get("is_veteran", False):
            return "not_eligible", 0.95, "Program requires veteran status"
    
    # Check disability
    if criteria.get("requires_disability", False):
        if not profile.get("is_disabled", False):
            return "not_eligible", 0.95, "Program requires disability status"
    
    # If custom rules exist, lower confidence
    if criteria.get("custom_rules"):
        confidence = 0.75
        reasons.append(f"Additional rules may apply: {criteria['custom_rules']}")
        return "likely_eligible", confidence, "; ".join(reasons)
    
    return "eligible", confidence, "; ".join(reasons) if reasons else "Meets all basic criteria"


def rank_schemes(schemes_with_status: List[Dict]) -> List[Dict]:
    """
    Rank schemes by priority and eligibility status.
    """
    # Status weight
    status_weight = {
        "eligible": 100,
        "likely_eligible": 75,
        "maybe_eligible": 50,
        "not_eligible": 0
    }
    
    def score(scheme):
        status = scheme.get("status", "maybe_eligible")
        priority = scheme.get("priority_score", 5)
        confidence = scheme.get("confidence", 0.5)
        
        return (
            status_weight.get(status, 50) +
            priority * 5 +
            confidence * 20
        )
    
    return sorted(schemes_with_status, key=score, reverse=True)
