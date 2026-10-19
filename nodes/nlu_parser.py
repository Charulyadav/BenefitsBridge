# nodes/nlu_parser.py - Voice transcript to structured profile

import json
import re
from typing import Dict, Any

# from langchain_anthropic import ChatAnthropic
# from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from state import GraphState
# from config import ANTHROPIC_API_KEY, LLM_MODEL, LLM_TEMPERATURE, OPENAI_API_KEY
from config import LLM_MODEL, LLM_TEMPERATURE, OLLAMA_BASE_URL


# Initialize LLM
llm = ChatOllama(
    model=LLM_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=LLM_TEMPERATURE,
)


NLU_SYSTEM_PROMPT = """You are an expert at extracting structured information from natural language.
Your task is to extract a user profile from a spoken description of someone's situation.
They are describing their situation to check eligibility for government benefits.

Extract the following fields. Use null for any field not mentioned or unclear.
Make reasonable inferences where appropriate (e.g., if they mention "my two kids ages 3 and 5", 
set has_children=true, children_ages=[3,5], household_size should include the children).

IMPORTANT: 
- Income should be ANNUAL. If they say monthly, multiply by 12.
- State should be the 2-letter abbreviation (TX, CA, NY, etc.)
- Be generous with interpretation - if they say "I work part-time", set is_employed=true
- If they mention being a single mom/dad, set is_single_parent=true
"""

NLU_USER_PROMPT = """Extract structured profile from this spoken input:

"{transcript}"

Return ONLY a valid JSON object with these exact fields (use null if not mentioned):
{{
    "name": <string or null>,
    "age": <integer or null>,
    "state": <2-letter state code or null>,
    "county": <string or null>,
    "city": <string or null>,
    "household_size": <integer>,
    "income": <annual income as integer>,
    "income_type": <"wages" | "self-employment" | "benefits" | "mixed" | null>,
    "is_pregnant": <boolean>,
    "is_breastfeeding": <boolean>,
    "has_children": <boolean>,
    "children_ages": <array of integers>,
    "is_single_parent": <boolean>,
    "is_employed": <boolean>,
    "employment_type": <"full-time" | "part-time" | "unemployed" | null>,
    "is_veteran": <boolean>,
    "is_disabled": <boolean>,
    "is_student": <boolean>,
    "is_homeless": <boolean>,
    "is_domestic_violence_survivor": <boolean>,
    "is_us_citizen": <boolean - assume true if not mentioned>,
    "is_legal_resident": <boolean - assume true if not mentioned>,
    "housing_situation": <"renter" | "owner" | "homeless" | "shelter" | null>,
    "monthly_rent": <integer or null>
}}

Return ONLY the JSON object, no explanation or markdown formatting."""


def clean_json_response(response: str) -> str:
    """Clean up LLM response to get valid JSON"""
    # Remove markdown code blocks
    response = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
    response = re.sub(r'^```\s*', '', response, flags=re.MULTILINE)
    response = re.sub(r'\s*```$', '', response, flags=re.MULTILINE)
    
    # Try to find JSON object
    match = re.search(r'\{[\s\S]*\}', response)
    if match:
        return match.group(0)
    
    return response.strip()


def nlu_parser_node(state: GraphState) -> Dict[str, Any]:
    """
    Parse voice transcript into structured profile using LLM.
    """
    transcript = state.get("voice_transcript")
    
    if not transcript:
        return {
            "parse_error": "No voice transcript provided",
            "errors": ["No voice transcript provided"]
        }
    
    try:
        # Call LLM
        messages = [
            SystemMessage(content=NLU_SYSTEM_PROMPT),
            HumanMessage(content=NLU_USER_PROMPT.format(transcript=transcript))
        ]
        
        response = llm.invoke(messages)
        response_text = response.content
        
        # Clean and parse JSON
        json_str = clean_json_response(response_text)
        profile_data = json.loads(json_str)
        
        # Validate minimum required fields
        if not profile_data.get("state"):
            return {
                "parse_error": "Could not determine your state. Please mention which state you live in.",
                "errors": ["State not detected"]
            }
        
        if not profile_data.get("income") and profile_data.get("income") != 0:
            return {
                "parse_error": "Could not determine your income. Please mention your approximate annual income.",
                "errors": ["Income not detected"]
            }
        
        # Set defaults
        if not profile_data.get("household_size"):
            # Estimate from children + 1 adult
            children_count = len(profile_data.get("children_ages", []))
            profile_data["household_size"] = max(1, children_count + 1)
        
        return {
            "user_profile": profile_data,
            "input_method": "voice",
            "errors": []
        }
        
    except json.JSONDecodeError as e:
        return {
            "parse_error": f"Could not understand the response. Please try again with clearer details.",
            "errors": [f"JSON parse error: {str(e)}"]
        }
    except Exception as e:
        return {
            "parse_error": f"An error occurred: {str(e)}",
            "errors": [str(e)]
        }
