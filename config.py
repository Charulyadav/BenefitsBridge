# config.py - Configuration

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
SCHEMES_FILE = DATA_DIR / "schemes.json"
PROMPTS_DIR = BASE_DIR / "prompts"

# LLM Configuration (optional — app works without LLM via rule-based engine)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "none")  # "none", "ollama", "anthropic", "openai"
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")
LLM_TEMPERATURE = 0.1
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Admin passwords (in production, use proper auth!)
ADMIN_PASSWORDS = {
    "federal": "fed_admin_2024",
    "TX": "texas_admin_2024",
    "CA": "california_admin_2024",
    "NY": "newyork_admin_2024",
    "MA": "massachusetts_admin_2024",
    "FL": "florida_admin_2024",
    "Harris County": "harris_admin_2024",
    "Los Angeles County": "la_admin_2024",
}

# US States
US_STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]

# 2024 Federal Poverty Level (annual income)
FPL_2024 = {
    1: 15060, 2: 20440, 3: 25820, 4: 31200,
    5: 36580, 6: 41960, 7: 47340, 8: 52720,
}


def get_fpl(household_size: int) -> int:
    """Get Federal Poverty Level for household size"""
    if household_size <= 8:
        return FPL_2024.get(household_size, FPL_2024[1])
    return FPL_2024[8] + (household_size - 8) * 5380
