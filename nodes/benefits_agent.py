# nodes/benefits_agent.py - Benefits eligibility agent (SNAP, WIC, TANF, Housing, Utilities)

import json
from typing import Dict, Any, List

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from state import GraphState, SchemeResult
# from config import ANTHROPIC_API_KEY, LLM_MODEL, LLM_TEMPERATURE, get_fpl
from utils.db import get_schemes_for_location
from utils.eligibility import check_basic_eligibility, calculate_fpl_percentage
from config import LLM_MODEL, LLM_TEMPERATURE, OLLAMA_BASE_URL

llm = ChatOllama(
    model=LLM_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=LLM_TEMPERATURE,
)


BENEFITS_CATEGORIES = ["nutrition", "housing", "financial", "utilities"]


BENEFITS_SYSTEM_PROMPT = """You are an expert benefits eligibility specialist.
Your role is to determine eligibility for nutrition, housing, financial assistance, and utility programs.

You will be given:
1. A user profile with their circumstances
2. A list of available schemes with their eligibility criteria

For EACH scheme, determine the user's eligibility status:
- "eligible": Clearly meets all stated criteria
- "likely_eligible": Meets main criteria, minor uncertainties
- "maybe_eligible": Some criteria met, needs verification
- "not_eligible": Clearly does not meet one or more key criteria

Be thorough but also compassionate - these are people seeking help.
Consider edge cases and note when additional verification might change the outcome.
"""

BENEFITS_USER_PROMPT = """Analyze eligibility for the following user and schemes.

USER PROFILE:
- State: {state}
- Household Size: {household_size}
- Annual Income: ${income:,} ({fpl_percent}% of Federal Poverty Level)
- Has Children: {has_children}
- Children Ages: {children_ages}
- Is Pregnant: {is_pregnant}
- Is Employed: {is_employed} ({employment_type})
- Is Veteran: {is_veteran}
- Is Disabled: {is_disabled}
- Housing Situation: {housing_situation}
- US Citizen: {is_us_citizen}

AVAILABLE SCHEMES:
{schemes_json}

For each scheme, return a JSON array with this format:
[
  {{
    "scheme_id": "...",
    "name": "...",
    "status": "eligible" | "likely_eligible" | "maybe_eligible" | "not_eligible",
    "confidence": 0.0-1.0,
    "reason": "Brief explanation of why"
  }}
]

Consider:
- Income limits vs their income
- Family composition requirements
- State-specific variations
- Any special circumstances that might help or disqualify

Return ONLY the JSON array, no other text."""


def benefits_agent_node(state: GraphState) -> Dict[str, Any]:
    """
    Check eligibility for nutrition, housing, financial, and utility programs.
    """
    profile = state.get("user_profile", {})
    
    if not profile:
        return {"benefits_results": [], "errors": ["No user profile available"]}
    
    user_state = profile.get("state", "")
    county = profile.get("county")
    
    # Get location-specific schemes
    all_schemes = get_schemes_for_location(user_state, county)
    
    # Filter to benefits categories
    benefits_schemes = [
        s for s in all_schemes 
        if s.get("category") in BENEFITS_CATEGORIES
    ]
    
    if not benefits_schemes:
        return {"benefits_results": []}
    
    # Calculate FPL percentage
    fpl_percent = calculate_fpl_percentage(
        profile.get("income", 0),
        profile.get("household_size", 1)
    )
    
    # Prepare schemes JSON (simplified for LLM)
    schemes_for_llm = []
    for s in benefits_schemes:
        schemes_for_llm.append({
            "id": s["id"],
            "name": s["name"],
            "category": s["category"],
            "level": s["level"],
            "criteria": s.get("criteria", {}),
            "description": s.get("description", "")
        })
    
    try:
        messages = [
            SystemMessage(content=BENEFITS_SYSTEM_PROMPT),
            HumanMessage(content=BENEFITS_USER_PROMPT.format(
                state=user_state,
                household_size=profile.get("household_size", 1),
                income=profile.get("income", 0),
                fpl_percent=fpl_percent,
                has_children=profile.get("has_children", False),
                children_ages=profile.get("children_ages", []),
                is_pregnant=profile.get("is_pregnant", False),
                is_employed=profile.get("is_employed", False),
                employment_type=profile.get("employment_type", "unknown"),
                is_veteran=profile.get("is_veteran", False),
                is_disabled=profile.get("is_disabled", False),
                housing_situation=profile.get("housing_situation", "unknown"),
                is_us_citizen=profile.get("is_us_citizen", True),
                schemes_json=json.dumps(schemes_for_llm, indent=2)
            ))
        ]
        
        response = llm.invoke(messages)
        response_text = response.content
        
        # Parse response
        # Clean markdown if present
        if "```" in response_text:
            import re
            match = re.search(r'\[[\s\S]*\]', response_text)
            if match:
                response_text = match.group(0)
        
        llm_results = json.loads(response_text)
        
        # Enrich results with full scheme data
        results: List[SchemeResult] = []
        for llm_result in llm_results:
            scheme_id = llm_result.get("scheme_id")
            
            # Find original scheme
            original = next((s for s in benefits_schemes if s["id"] == scheme_id), None)
            if not original:
                continue
            
            results.append(SchemeResult(
                scheme_id=scheme_id,
                name=original.get("name", llm_result.get("name", "")),
                category=original.get("category", "benefits"),
                status=llm_result.get("status", "maybe_eligible"),
                confidence=llm_result.get("confidence", 0.5),
                reason=llm_result.get("reason", ""),
                priority_score=original.get("priority_score", 5),
                apply_url=original.get("apply_url", ""),
                next_steps=original.get("next_steps", []),
                documents_needed=original.get("documents_needed", [])
            ))
        
        return {"benefits_results": results}
        
    except Exception as e:
        # Fallback: use rule-based checking
        results = []
        for scheme in benefits_schemes:
            status, confidence, reason = check_basic_eligibility(
                profile, 
                scheme.get("criteria", {})
            )
            results.append(SchemeResult(
                scheme_id=scheme["id"],
                name=scheme["name"],
                category=scheme.get("category", "benefits"),
                status=status,
                confidence=confidence,
                reason=reason,
                priority_score=scheme.get("priority_score", 5),
                apply_url=scheme.get("apply_url", ""),
                next_steps=scheme.get("next_steps", []),
                documents_needed=scheme.get("documents_needed", [])
            ))
        
        return {
            "benefits_results": results,
            "errors": [f"LLM error, used fallback: {str(e)}"]
        }
