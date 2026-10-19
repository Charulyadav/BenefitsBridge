# nodes/education_agent.py - Education & Career eligibility agent (Pell, WIOA, Childcare, SBA)

import json
from typing import Dict, Any, List

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from state import GraphState, SchemeResult
# from config import ANTHROPIC_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from utils.db import get_schemes_for_location
from utils.eligibility import check_basic_eligibility, calculate_fpl_percentage
from config import LLM_MODEL, LLM_TEMPERATURE, OLLAMA_BASE_URL
llm = ChatOllama(
    model=LLM_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=LLM_TEMPERATURE,
)


EDUCATION_CATEGORIES = ["education", "childcare", "employment"]


EDUCATION_SYSTEM_PROMPT = """You are an expert in education, childcare, and workforce development programs.
Your role is to determine eligibility for:
- Education grants (Pell Grant, state scholarships)
- Childcare assistance programs
- Workforce training (WIOA)
- Small business grants for women entrepreneurs

Consider:
- Student status requirements
- Working parent requirements for childcare
- Income limits
- Special programs for women, single parents, veterans
"""

EDUCATION_USER_PROMPT = """Analyze education/career eligibility for this user.

USER PROFILE:
- State: {state}
- Household Size: {household_size}
- Annual Income: ${income:,} ({fpl_percent}% of Federal Poverty Level)
- Has Children: {has_children}
- Children Ages: {children_ages}
- Is Single Parent: {is_single_parent}
- Is Employed: {is_employed} ({employment_type})
- Is Student: {is_student}
- Is Veteran: {is_veteran}

AVAILABLE SCHEMES:
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
- Whether they're working/in school for childcare programs
- Student status for education grants
- Single parent priorities
- Veteran benefits

Return ONLY the JSON array."""


def education_agent_node(state: GraphState) -> Dict[str, Any]:
    """
    Check eligibility for education, childcare, and employment programs.
    """
    profile = state.get("user_profile", {})
    
    if not profile:
        return {"education_results": [], "errors": ["No user profile available"]}
    
    user_state = profile.get("state", "")
    county = profile.get("county")
    
    # Get schemes
    all_schemes = get_schemes_for_location(user_state, county)
    education_schemes = [
        s for s in all_schemes 
        if s.get("category") in EDUCATION_CATEGORIES
    ]
    
    if not education_schemes:
        return {"education_results": []}
    
    fpl_percent = calculate_fpl_percentage(
        profile.get("income", 0),
        profile.get("household_size", 1)
    )
    
    # Prepare for LLM
    schemes_for_llm = []
    for s in education_schemes:
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
            SystemMessage(content=EDUCATION_SYSTEM_PROMPT),
            HumanMessage(content=EDUCATION_USER_PROMPT.format(
                state=user_state,
                household_size=profile.get("household_size", 1),
                income=profile.get("income", 0),
                fpl_percent=fpl_percent,
                has_children=profile.get("has_children", False),
                children_ages=profile.get("children_ages", []),
                is_single_parent=profile.get("is_single_parent", False),
                is_employed=profile.get("is_employed", False),
                employment_type=profile.get("employment_type", "unknown"),
                is_student=profile.get("is_student", False),
                is_veteran=profile.get("is_veteran", False),
                schemes_json=json.dumps(schemes_for_llm, indent=2)
            ))
        ]
        
        response = llm.invoke(messages)
        response_text = response.content
        
        # Parse
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
            original = next((s for s in education_schemes if s["id"] == scheme_id), None)
            if not original:
                continue
            
            results.append(SchemeResult(
                scheme_id=scheme_id,
                name=original.get("name", llm_result.get("name", "")),
                category=original.get("category", "education"),
                status=llm_result.get("status", "maybe_eligible"),
                confidence=llm_result.get("confidence", 0.5),
                reason=llm_result.get("reason", ""),
                priority_score=original.get("priority_score", 5),
                apply_url=original.get("apply_url", ""),
                next_steps=original.get("next_steps", []),
                documents_needed=original.get("documents_needed", [])
            ))
        
        return {"education_results": results}
        
    except Exception as e:
        # Fallback
        results = []
        for scheme in education_schemes:
            status, confidence, reason = check_basic_eligibility(
                profile, 
                scheme.get("criteria", {})
            )
            results.append(SchemeResult(
                scheme_id=scheme["id"],
                name=scheme["name"],
                category=scheme.get("category", "education"),
                status=status,
                confidence=confidence,
                reason=reason,
                priority_score=scheme.get("priority_score", 5),
                apply_url=scheme.get("apply_url", ""),
                next_steps=scheme.get("next_steps", []),
                documents_needed=scheme.get("documents_needed", [])
            ))
        
        return {
            "education_results": results,
            "errors": [f"LLM error, used fallback: {str(e)}"]
        }
