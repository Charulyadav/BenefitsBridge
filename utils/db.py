# utils/db.py - Database helpers for schemes

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# Get the data directory
DATA_DIR = Path(__file__).parent.parent / "data"
SCHEMES_FILE = DATA_DIR / "schemes.json"


def load_schemes() -> List[dict]:
    """Load all schemes from JSON file"""
    if not SCHEMES_FILE.exists():
        return []
    
    with open(SCHEMES_FILE, "r") as f:
        data = json.load(f)
    return data.get("schemes", [])


def save_schemes(schemes: List[dict]) -> None:
    """Save schemes to JSON file"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    data = {
        "schemes": schemes,
        "last_updated": datetime.now().isoformat(),
        "version": "1.0"
    }
    
    with open(SCHEMES_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_scheme_by_id(scheme_id: str) -> Optional[dict]:
    """Get a single scheme by ID"""
    schemes = load_schemes()
    for scheme in schemes:
        if scheme["id"] == scheme_id:
            return scheme
    return None


def add_scheme(scheme: dict) -> bool:
    """Add a new scheme"""
    schemes = load_schemes()
    
    # Check for duplicate ID
    if any(s["id"] == scheme["id"] for s in schemes):
        return False
    
    schemes.append(scheme)
    save_schemes(schemes)
    return True


def update_scheme(scheme_id: str, updates: dict) -> bool:
    """Update an existing scheme"""
    schemes = load_schemes()
    
    for i, scheme in enumerate(schemes):
        if scheme["id"] == scheme_id:
            schemes[i].update(updates)
            schemes[i]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            save_schemes(schemes)
            return True
    return False


def delete_scheme(scheme_id: str) -> bool:
    """Delete a scheme"""
    schemes = load_schemes()
    original_length = len(schemes)
    
    schemes = [s for s in schemes if s["id"] != scheme_id]
    
    if len(schemes) < original_length:
        save_schemes(schemes)
        return True
    return False


def get_schemes_for_location(
    state: str, 
    county: Optional[str] = None, 
    city: Optional[str] = None,
    active_only: bool = True
) -> List[dict]:
    """
    Get all schemes applicable to a specific location.
    Returns federal + state + county + city schemes.
    """
    all_schemes = load_schemes()
    applicable = []
    
    for scheme in all_schemes:
        # Skip inactive schemes if requested
        if active_only and not scheme.get("is_active", True):
            continue
        
        # Federal schemes apply everywhere
        if scheme["level"] == "federal":
            applicable.append(scheme)
        
        # State schemes apply to that state
        elif scheme["level"] == "state" and scheme.get("state") == state:
            applicable.append(scheme)
        
        # County schemes apply to that county in that state
        elif scheme["level"] == "county":
            if scheme.get("state") == state and scheme.get("county") == county:
                applicable.append(scheme)
        
        # City schemes apply to that city
        elif scheme["level"] == "city":
            if scheme.get("state") == state and scheme.get("city") == city:
                applicable.append(scheme)
    
    # Sort by priority score (highest first)
    applicable.sort(key=lambda x: x.get("priority_score", 5), reverse=True)
    
    return applicable


def get_schemes_by_category(
    category: str,
    state: Optional[str] = None,
    active_only: bool = True
) -> List[dict]:
    """Get schemes filtered by category"""
    if state:
        schemes = get_schemes_for_location(state, active_only=active_only)
    else:
        schemes = load_schemes()
        if active_only:
            schemes = [s for s in schemes if s.get("is_active", True)]
    
    return [s for s in schemes if s.get("category") == category]


def get_schemes_by_admin(admin_email: str) -> List[dict]:
    """Get all schemes added by a specific admin"""
    schemes = load_schemes()
    return [s for s in schemes if s.get("added_by") == admin_email]


def get_schemes_by_jurisdiction(jurisdiction: str) -> List[dict]:
    """Get schemes for a specific admin jurisdiction"""
    schemes = load_schemes()
    
    if jurisdiction == "federal":
        return [s for s in schemes if s["level"] == "federal"]
    elif jurisdiction in ["TX", "CA", "NY", "MA", "FL"]:  # State codes
        return [s for s in schemes if s.get("state") == jurisdiction]
    else:  # County
        return [s for s in schemes if s.get("county") == jurisdiction]


def search_schemes(query: str) -> List[dict]:
    """Simple text search across scheme names and descriptions"""
    schemes = load_schemes()
    query_lower = query.lower()
    
    results = []
    for scheme in schemes:
        if (query_lower in scheme.get("name", "").lower() or
            query_lower in scheme.get("description", "").lower() or
            any(query_lower in tag.lower() for tag in scheme.get("tags", []))):
            results.append(scheme)
    
    return results
