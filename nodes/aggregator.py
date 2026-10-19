# nodes/aggregator.py - Aggregate and rank results from all agents

from typing import Dict, Any, List
from state import GraphState, SchemeResult


def aggregator_node(state: GraphState) -> Dict[str, Any]:
    """
    Combine results from all agents, remove duplicates, and rank by priority.
    """
    
    # Collect all results
    all_results: List[SchemeResult] = []
    
    benefits_results = state.get("benefits_results", [])
    healthcare_results = state.get("healthcare_results", [])
    education_results = state.get("education_results", [])
    
    all_results.extend(benefits_results)
    all_results.extend(healthcare_results)
    all_results.extend(education_results)
    
    # Remove duplicates (by scheme_id)
    seen_ids = set()
    unique_results = []
    for result in all_results:
        scheme_id = result.get("scheme_id") if isinstance(result, dict) else result.scheme_id
        if scheme_id not in seen_ids:
            seen_ids.add(scheme_id)
            unique_results.append(result)
    
    # Sort by status priority, then by priority_score
    status_order = {
        "eligible": 0,
        "likely_eligible": 1,
        "maybe_eligible": 2,
        "not_eligible": 3
    }
    
    def sort_key(result):
        if isinstance(result, dict):
            status = result.get("status", "maybe_eligible")
            priority = result.get("priority_score", 5)
            confidence = result.get("confidence", 0.5)
        else:
            status = result.status
            priority = result.priority_score
            confidence = result.confidence
        
        return (
            status_order.get(status, 2),
            -priority,  # Higher priority first
            -confidence  # Higher confidence first
        )
    
    sorted_results = sorted(unique_results, key=sort_key)
    
    # Categorize results
    eligible = []
    maybe_eligible = []
    not_eligible = []
    
    for result in sorted_results:
        status = result.get("status") if isinstance(result, dict) else result.status
        
        if status in ["eligible", "likely_eligible"]:
            eligible.append(result)
        elif status == "maybe_eligible":
            maybe_eligible.append(result)
        else:
            not_eligible.append(result)
    
    return {
        "all_results": sorted_results,
        "eligible_schemes": eligible,
        "maybe_eligible_schemes": maybe_eligible,
        "not_eligible_schemes": not_eligible
    }
