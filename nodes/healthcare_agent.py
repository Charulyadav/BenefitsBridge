# nodes/healthcare_agent.py - Healthcare eligibility agent (Medicaid, CHIP, ACA)

import json
from typing import Dict, Any, List

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from state import GraphState, SchemeResult
from langchain_ollama import ChatOllama
# from config import ANTHROPIC_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from utils.db import get_schemes_for_location
from utils.eligibility import check_basic_eligibility, calculate_fpl_percentage
from config import LLM_MODEL, LLM_TEMPERATURE, OLLAMA_BASE_URL

llm = ChatOllama(
    model=LLM_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=LLM_TEMPERATURE,
)


HEALTHCARE_SYSTEM_PROMPT = """You are an expert healthcare benefits eligibility specialist.
Your role is to determine eligibility for Medicaid, CHIP, ACA marketplace subsidies, and other health programs.

Key considerations for healthcare programs:
- Medicaid expansion states have different income limits than non-expansion states
- CHIP covers children in families that earn too much for Medicaid
- Pregnant women often have higher income limits
- ACA subsidies are available for those above Medicaid limits

Be thorough and note state-specific variations.
"""

HEALTHCARE_USER_PROMPT = """Analyze healthcare eligibility for this user.

USER PROFILE:
- State: {state}
- Household Size: {household_size}
- Annual Income: ${income:,} ({fpl_percent}% of Federal Poverty Level)
- Has Children: {has_children}
- Children Ages: {children_ages}
- Is Pregnant: {is_pregnant}
- Is Breastfeeding: {is_breastfeeding}
- Is Disabled: {is_disabled}
- US Citizen: {is_us_citizen}
- Legal Resident: {is_legal_resident}

AVAILABLE HEALTHCARE SCHEMES:
{schemes_json}

For each scheme, return a JSON array:
[
  {{
    "scheme_id": "...",
    "name": "...",
    "status": "eligible" | "likely_eligible" | "maybe_eligible" | "not_eligible",
    "confidence": 0.0-1.0,
    "reason": "Brief explanation"
  }}
]

Consider:
- Federal vs state Medicaid rules
- Children's coverage through CHIP
- Pregnancy-related coverage expansions
- Disability considerations

Return ONLY the JSON array."""


def healthcare_agent_node(state: GraphState) -> Dict[str, Any]:
    """
    Check eligibility for healthcare programs.
    """
    profile = state.get("user_profile", {})
    
    if not profile:
        return {"healthcare_results": [], "errors": ["No user profile available"]}
    
    user_state = profile.get("state", "")
    county = profile.get("county")
    
    # Get healthcare schemes
    all_schemes = get_schemes_for_location(user_state, county)
    healthcare_schemes = [s for s in all_schemes if s.get("category") == "healthcare"]
    
    if not healthcare_schemes:
        return {"healthcare_results": []}
    
    fpl_percent = calculate_fpl_percentage(
        profile.get("income", 0),
        profile.get("household_size", 1)
    )
    
    # Prepare schemes for LLM
    schemes_for_llm = []
    for s in healthcare_schemes:
        schemes_for_llm.append({
            "id": s["id"],
            "name": s["name"],
            "level": s["level"],
            "criteria": s.get("criteria", {}),
            "description": s.get("description", "")
        })
    
    try:
        messages = [
            SystemMessage(content=HEALTHCARE_SYSTEM_PROMPT),
            HumanMessage(content=HEALTHCARE_USER_PROMPT.format(
                state=user_state,
                household_size=profile.get("household_size", 1),
                income=profile.get("income", 0),
                fpl_percent=fpl_percent,
                has_children=profile.get("has_children", False),
                children_ages=profile.get("children_ages", []),
                is_pregnant=profile.get("is_pregnant", False),
                is_breastfeeding=profile.get("is_breastfeeding", False),
                is_disabled=profile.get("is_disabled", False),
                is_us_citizen=profile.get("is_us_citizen", True),
                is_legal_resident=profile.get("is_legal_resident", True),
                schemes_json=json.dumps(schemes_for_llm, indent=2)
            ))
        ]
        
        response = llm.invoke(messages)
        response_text = response.content
        
        # Parse response
        if "```" in response_text:
            import re
            match = re.search(r'\[[\s\S]*\]', response_text)
            if match:
                response_text = match.group(0)
        
        llm_results = json.loads(response_text)
        
        # Build results
        results: List[SchemeResult] = []
        for llm_result in llm_results:
            scheme_id = llm_result.get("scheme_id")
            original = next((s for s in healthcare_schemes if s["id"] == scheme_id), None)
            if not original:
                continue
            
            results.append(SchemeResult(
                scheme_id=scheme_id,
                name=original.get("name", llm_result.get("name", "")),
                category="healthcare",
                status=llm_result.get("status", "maybe_eligible"),
                confidence=llm_result.get("confidence", 0.5),
                reason=llm_result.get("reason", ""),
                priority_score=original.get("priority_score", 5),
                apply_url=original.get("apply_url", ""),
                next_steps=original.get("next_steps", []),
                documents_needed=original.get("documents_needed", [])
            ))
        
        return {"healthcare_results": results}
        
    except Exception as e:
        # Fallback to rule-based
        results = []
        for scheme in healthcare_schemes:
            status, confidence, reason = check_basic_eligibility(
                profile, 
                scheme.get("criteria", {})
            )
            results.append(SchemeResult(
                scheme_id=scheme["id"],
                name=scheme["name"],
                category="healthcare",
                status=status,
                confidence=confidence,
                reason=reason,
                priority_score=scheme.get("priority_score", 5),
                apply_url=scheme.get("apply_url", ""),
                next_steps=scheme.get("next_steps", []),
                documents_needed=scheme.get("documents_needed", [])
            ))
        
        return {
            "healthcare_results": results,
            "errors": [f"LLM error, used fallback: {str(e)}"]
        }
