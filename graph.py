# graph.py - LangGraph workflow definition (rule-based, no LLM dependency)

from typing import Literal, Dict, Any, List
from state import GraphState, SchemeResult
from utils.db import get_schemes_for_location
from utils.eligibility import check_basic_eligibility, calculate_fpl_percentage


def intake_node(state: GraphState) -> Dict[str, Any]:
    """Process and validate user input from form."""
    raw_data = state.get("raw_form_data", {})

    if not raw_data:
        return {"parse_error": "No form data provided", "errors": ["No form data provided"]}

    # Parse children ages
    children_ages = raw_data.get("children_ages", [])
    if isinstance(children_ages, str):
        try:
            children_ages = [int(x.strip()) for x in children_ages.split(",") if x.strip()]
        except ValueError:
            children_ages = []

    has_children = raw_data.get("has_children", len(children_ages) > 0)

    profile = {
        "name": raw_data.get("name"),
        "age": raw_data.get("age"),
        "state": (raw_data.get("state") or "").upper(),
        "county": raw_data.get("county"),
        "city": raw_data.get("city"),
        "zip_code": raw_data.get("zip_code"),
        "household_size": int(raw_data.get("household_size", 1)),
        "income": int(raw_data.get("income", 0)),
        "income_type": raw_data.get("income_type"),
        "is_pregnant": bool(raw_data.get("is_pregnant", False)),
        "is_breastfeeding": bool(raw_data.get("is_breastfeeding", False)),
        "has_children": has_children,
        "children_ages": children_ages,
        "is_single_parent": bool(raw_data.get("is_single_parent", False)),
        "is_employed": bool(raw_data.get("is_employed", False)),
        "employment_type": raw_data.get("employment_type"),
        "is_veteran": bool(raw_data.get("is_veteran", False)),
        "is_disabled": bool(raw_data.get("is_disabled", False)),
        "is_student": bool(raw_data.get("is_student", False)),
        "is_homeless": bool(raw_data.get("is_homeless", False)),
        "is_domestic_violence_survivor": bool(raw_data.get("is_domestic_violence_survivor", False)),
        "is_us_citizen": bool(raw_data.get("is_us_citizen", True)),
        "is_legal_resident": bool(raw_data.get("is_legal_resident", True)),
        "housing_situation": raw_data.get("housing_situation"),
        "monthly_rent": raw_data.get("monthly_rent"),
    }

    # Validate
    if not profile["state"]:
        return {"parse_error": "Please select your state", "errors": ["State required"]}

    return {"user_profile": profile, "input_method": "form", "errors": []}


def nlu_parser_node(state: GraphState) -> Dict[str, Any]:
    """Parse voice transcript into structured profile using simple keyword extraction."""
    transcript = state.get("voice_transcript", "")

    if not transcript:
        return {"parse_error": "No voice transcript provided", "errors": ["No transcript"]}

    text = transcript.lower()

    # Extract state
    from config import US_STATES
    found_state = None
    state_names = {
        "texas": "TX", "california": "CA", "new york": "NY", "florida": "FL",
        "massachusetts": "MA", "georgia": "GA", "illinois": "IL", "ohio": "OH",
        "pennsylvania": "PA", "michigan": "MI", "north carolina": "NC",
        "virginia": "VA", "washington": "WA", "arizona": "AZ", "colorado": "CO",
        "minnesota": "MN", "wisconsin": "WI", "maryland": "MD", "indiana": "IN",
        "tennessee": "TN", "missouri": "MO", "connecticut": "CT", "oregon": "OR",
        "oklahoma": "OK", "kentucky": "KY", "louisiana": "LA", "alabama": "AL",
        "south carolina": "SC", "iowa": "IA", "utah": "UT", "arkansas": "AR",
        "mississippi": "MS", "kansas": "KS", "nevada": "NV", "nebraska": "NE",
        "new jersey": "NJ", "idaho": "ID", "hawaii": "HI", "maine": "ME",
        "montana": "MT", "new hampshire": "NH", "rhode island": "RI",
        "delaware": "DE", "south dakota": "SD", "north dakota": "ND",
        "alaska": "AK", "vermont": "VT", "wyoming": "WY", "west virginia": "WV",
        "new mexico": "NM",
        # City-based guesses
        "houston": "TX", "dallas": "TX", "san antonio": "TX", "austin": "TX",
        "los angeles": "CA", "san francisco": "CA", "san diego": "CA",
        "new york city": "NY", "nyc": "NY", "brooklyn": "NY", "manhattan": "NY",
        "miami": "FL", "orlando": "FL", "tampa": "FL", "jacksonville": "FL",
        "boston": "MA", "chicago": "IL", "atlanta": "GA", "detroit": "MI",
        "seattle": "WA", "denver": "CO", "phoenix": "AZ", "portland": "OR",
    }

    for name, code in state_names.items():
        if name in text:
            found_state = code
            break

    if not found_state:
        for code in US_STATES:
            if f" {code.lower()} " in f" {text} " or text.endswith(f" {code.lower()}"):
                found_state = code
                break

    if not found_state:
        return {
            "parse_error": "Could not determine your state. Please mention which state you live in.",
            "errors": ["State not detected"]
        }

    # Extract income
    import re
    income = 0
    income_patterns = [
        r'\$\s*([\d,]+)\s*(?:per\s+year|a\s+year|annually|/year|yearly)',
        r'\$\s*([\d,]+)\s*(?:per\s+month|a\s+month|monthly|/month)',
        r'(?:making|earn|income|salary)\s*(?:about|around|roughly)?\s*\$?\s*([\d,]+)',
        r'\$\s*([\d,]+)',
    ]
    for i, pattern in enumerate(income_patterns):
        match = re.search(pattern, text)
        if match:
            val = int(match.group(1).replace(",", ""))
            if i == 1 or "month" in text[max(0, match.start()-20):match.end()+20]:
                val *= 12
            income = val
            break

    if income == 0:
        return {
            "parse_error": "Could not determine your income. Please mention your approximate annual income.",
            "errors": ["Income not detected"]
        }

    # Extract children ages
    children_ages = []
    age_patterns = [
        r'(?:ages?|aged?)\s+([\d,\s]+(?:and\s+\d+)?)',
        r'(\d+)\s*(?:year|yr)[\s-]*old',
    ]
    for pattern in age_patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            nums = re.findall(r'\d+', m)
            children_ages.extend([int(n) for n in nums if int(n) < 19])

    has_children = len(children_ages) > 0 or any(w in text for w in ["kid", "child", "children", "son", "daughter", "baby", "infant", "toddler"])

    # Household size
    household_size = 1 + len(children_ages)
    hh_match = re.search(r'household\s*(?:of|size)?\s*(\d+)', text)
    if hh_match:
        household_size = int(hh_match.group(1))
    elif "single" in text and has_children:
        household_size = 1 + max(len(children_ages), 1)

    profile = {
        "state": found_state,
        "household_size": max(1, household_size),
        "income": income,
        "has_children": has_children,
        "children_ages": children_ages,
        "is_pregnant": any(w in text for w in ["pregnant", "expecting", "pregnancy"]),
        "is_breastfeeding": any(w in text for w in ["breastfeeding", "nursing", "breastfeed"]),
        "is_single_parent": any(w in text for w in ["single mom", "single mother", "single dad", "single father", "single parent"]),
        "is_employed": any(w in text for w in ["work", "employed", "job", "working"]),
        "employment_type": "part-time" if "part-time" in text or "part time" in text else ("full-time" if "full-time" in text or "full time" in text else "unknown"),
        "is_veteran": any(w in text for w in ["veteran", "military", "served", "army", "navy", "marines", "air force"]),
        "is_disabled": any(w in text for w in ["disabled", "disability", "handicap"]),
        "is_student": any(w in text for w in ["student", "college", "university", "school", "enrolled", "studying"]),
        "is_homeless": any(w in text for w in ["homeless", "shelter", "no home", "housing insecure", "unhoused"]),
        "is_domestic_violence_survivor": any(w in text for w in ["domestic violence", "abusive", "abuse", "dv survivor", "left an abusive"]),
        "is_us_citizen": True,
        "is_legal_resident": True,
        "housing_situation": "homeless" if "homeless" in text else ("renter" if "rent" in text else None),
    }

    return {"user_profile": profile, "input_method": "voice", "errors": []}


def eligibility_engine_node(state: GraphState) -> Dict[str, Any]:
    """
    Check eligibility for ALL schemes using rule-based engine.
    No LLM dependency — always works.
    """
    profile = state.get("user_profile", {})
    if not profile:
        return {"all_results": [], "eligible_schemes": [], "maybe_eligible_schemes": [], "not_eligible_schemes": []}

    user_state = profile.get("state", "")
    county = profile.get("county")

    # Get all applicable schemes
    all_schemes = get_schemes_for_location(user_state, county)

    all_results = []
    eligible = []
    maybe_eligible = []
    not_eligible = []

    fpl_percent = calculate_fpl_percentage(
        profile.get("income", 0),
        profile.get("household_size", 1)
    )

    for scheme in all_schemes:
        criteria = scheme.get("criteria", {})

        # Run rule-based check
        status, confidence, reason = check_basic_eligibility(profile, criteria)

        # --- Extra rules for special schemes ---

        # WIC: needs pregnancy/breastfeeding/children under 5
        if scheme["id"] in ["wic-federal"]:
            is_wic_eligible = (
                profile.get("is_pregnant") or
                profile.get("is_breastfeeding") or
                any(age <= 5 for age in profile.get("children_ages", []))
            )
            if not is_wic_eligible and not profile.get("has_children"):
                status = "not_eligible"
                confidence = 0.9
                reason = "WIC requires pregnancy, breastfeeding, or a child under 5"
            elif is_wic_eligible and status != "not_eligible":
                status = "eligible"
                confidence = 0.9
                reason = "Meets WIC categorical requirement (pregnant, breastfeeding, or child under 5) and income eligible"

        # Pregnancy Medicaid
        if scheme["id"] == "medicaid-pregnant-federal":
            if not profile.get("is_pregnant"):
                status = "not_eligible"
                confidence = 0.95
                reason = "This program is specifically for pregnant women"

        # Veteran programs
        if criteria.get("requires_veteran_status") and not profile.get("is_veteran"):
            status = "not_eligible"
            confidence = 0.95
            reason = "This program requires veteran status"

        # DV programs — open to all DV survivors
        if criteria.get("domestic_violence_priority") and profile.get("is_domestic_violence_survivor"):
            if status != "not_eligible":
                status = "eligible"
                confidence = 0.95
                reason = "Priority access for domestic violence survivors. No income requirement."

        if scheme["id"] == "fvpsa-federal":
            if profile.get("is_domestic_violence_survivor"):
                status = "eligible"
                confidence = 0.95
                reason = "Available to all DV survivors regardless of income or citizenship"
            else:
                status = "not_eligible"
                confidence = 0.9
                reason = "This program is for domestic violence survivors"

        # EITC requires employment
        if scheme["id"] == "eitc-federal":
            if not profile.get("is_employed"):
                status = "not_eligible"
                confidence = 0.95
                reason = "EITC requires earned income from work"
            elif fpl_percent <= 400:
                status = "likely_eligible"
                confidence = 0.8
                reason = f"Income at {fpl_percent}% FPL. EITC eligibility depends on filing status and number of children. File your taxes to claim."

        # SSI requires disability/elderly
        if scheme["id"] == "ssi-federal":
            if not profile.get("is_disabled") and not (profile.get("age") and profile.get("age") >= 65):
                status = "not_eligible"
                confidence = 0.95
                reason = "SSI requires disability, blindness, or age 65+"

        # Pell Grant — boost for students
        if scheme["id"] == "pell-grant-federal":
            if profile.get("is_student") and fpl_percent <= 400:
                status = "likely_eligible"
                confidence = 0.8
                reason = f"As a student with income at {fpl_percent}% FPL, you likely qualify. Complete the FAFSA to find out your exact award."
            elif not profile.get("is_student"):
                status = "maybe_eligible"
                confidence = 0.5
                reason = "Pell Grants are for students. If you plan to enroll in college, you may qualify based on your income."

        # SBA Women's — open to all women
        if scheme["id"] == "sba-women-federal":
            status = "maybe_eligible"
            confidence = 0.6
            reason = "SBA Women's Business Centers offer free counseling to all women interested in entrepreneurship."

        # Child Tax Credit — works for most families with children under 17, even high income
        if scheme["id"] == "childtaxcredit-federal":
            if profile.get("has_children") and any(age < 17 for age in profile.get("children_ages", [])):
                num_qualifying = len([a for a in profile.get("children_ages", []) if a < 17])
                income = profile.get("income", 0)
                if income <= 200000:
                    status = "eligible"
                    confidence = 0.9
                    reason = f"You have {num_qualifying} qualifying child(ren) under 17 and income below $200,000. Estimated credit: up to ${num_qualifying * 2000:,}/year."
                elif income <= 400000:
                    status = "likely_eligible"
                    confidence = 0.75
                    reason = f"You have {num_qualifying} qualifying child(ren). Credit may be partially reduced at your income level but you likely still qualify for some benefit."
                else:
                    status = "maybe_eligible"
                    confidence = 0.5
                    reason = f"You have {num_qualifying} qualifying child(ren). Credit phases out above $400,000 for married filers — check with a tax advisor."
            elif not profile.get("has_children"):
                status = "not_eligible"
                confidence = 0.95
                reason = "Requires qualifying children under 17"

        # ACA Marketplace — for those above Medicaid threshold
        if scheme["id"] == "marketplace-insurance-federal":
            if fpl_percent > 138 and fpl_percent <= 400:
                status = "likely_eligible"
                confidence = 0.85
                reason = f"Income at {fpl_percent}% FPL — above Medicaid threshold. You likely qualify for premium tax credits to reduce your health insurance costs."
            elif fpl_percent <= 138:
                status = "maybe_eligible"
                confidence = 0.5
                reason = "You may qualify for Medicaid instead, which provides better coverage. If Medicaid denies you, the Marketplace is your backup."
            elif fpl_percent > 400:
                status = "maybe_eligible"
                confidence = 0.5
                reason = "Enhanced ACA subsidies may still apply. Check Healthcare.gov to see your estimated costs."

        # SSDI — requires disability
        if scheme["id"] == "ssdi-federal":
            if profile.get("is_disabled"):
                status = "likely_eligible"
                confidence = 0.75
                reason = "You indicated a disability. If you have enough Social Security work credits and your condition prevents you from working, you may qualify for SSDI."
            else:
                status = "not_eligible"
                confidence = 0.95
                reason = "SSDI requires a qualifying disability that prevents substantial work"

        # FAFSA / Student Aid — for students or anyone considering school
        if scheme["id"] == "fafsa-federal":
            if profile.get("is_student"):
                status = "eligible"
                confidence = 0.9
                reason = f"As a student with income at {fpl_percent}% FPL, you should complete the FAFSA. You likely qualify for grants, work-study, and/or federal student loans."
            else:
                status = "maybe_eligible"
                confidence = 0.5
                reason = "If you plan to attend college or a training program, completing the FAFSA unlocks grants and student loans regardless of income."

        # Free Tax Filing — broad eligibility
        if scheme["id"] == "free-tax-filing-federal":
            income = profile.get("income", 0)
            if income <= 79000:
                status = "eligible"
                confidence = 0.9
                reason = f"Your income of ${income:,} qualifies for IRS Free File. If under $64,000, you can also get free in-person help at a VITA site."
            else:
                status = "not_eligible"
                confidence = 0.8
                reason = "IRS Free File is for income under $79,000"

        # Medicare Savings — for seniors/disabled on Medicare
        if scheme["id"] == "medicare-savings-federal":
            if profile.get("is_disabled") or (profile.get("age") and profile.get("age") >= 65):
                if status != "not_eligible":
                    status = "likely_eligible"
                    confidence = 0.7
                    reason = "If you are enrolled in Medicare, these programs can help pay your premiums and copays."
            else:
                status = "not_eligible"
                confidence = 0.9
                reason = "Requires Medicare enrollment (typically age 65+ or disabled)"

        # Senior SNAP — for 60+
        if scheme["id"] == "snap-seniors-federal":
            if profile.get("age") and profile.get("age") >= 60:
                if status != "not_eligible":
                    status = "likely_eligible"
                    confidence = 0.8
                    reason = "Seniors 60+ qualify for simplified SNAP application with medical expense deductions."
            else:
                status = "not_eligible"
                confidence = 0.9
                reason = "This simplified program is for adults 60 and older"

        # SNAP E&T — for SNAP-eligible individuals
        if scheme["id"] == "snap-employment-training-federal":
            if fpl_percent <= 130 and not profile.get("is_employed"):
                status = "likely_eligible"
                confidence = 0.75
                reason = "If you receive SNAP, you can access free job training, education, and transportation assistance."
            elif fpl_percent <= 130:
                status = "maybe_eligible"
                confidence = 0.5
                reason = "If you receive SNAP benefits, you may access additional training programs even while employed."
            else:
                status = "not_eligible"
                confidence = 0.8
                reason = "Must be a SNAP recipient (income generally under 130% FPL)"

        # Build result
        result = {
            "scheme_id": scheme["id"],
            "name": scheme.get("name", ""),
            "category": scheme.get("category", ""),
            "status": status,
            "confidence": confidence,
            "reason": reason,
            "priority_score": scheme.get("priority_score", 5),
            "apply_url": scheme.get("apply_url", ""),
            "apply_phone": scheme.get("apply_phone", ""),
            "next_steps": scheme.get("next_steps", []),
            "documents_needed": scheme.get("documents_needed", []),
            "customer_care": scheme.get("customer_care", {}),
            "benefit_amount": scheme.get("benefit_amount", ""),
            "benefit_type": scheme.get("benefit_type", ""),
            "processing_time": scheme.get("processing_time", ""),
            "description": scheme.get("description", ""),
        }

        all_results.append(result)

        if status in ["eligible", "likely_eligible"]:
            eligible.append(result)
        elif status == "maybe_eligible":
            maybe_eligible.append(result)
        else:
            not_eligible.append(result)

    # Sort each list by priority then confidence
    def sort_key(r):
        return (-r.get("priority_score", 5), -r.get("confidence", 0.5))

    eligible.sort(key=sort_key)
    maybe_eligible.sort(key=sort_key)
    not_eligible.sort(key=sort_key)
    all_results.sort(key=sort_key)

    return {
        "all_results": all_results,
        "eligible_schemes": eligible,
        "maybe_eligible_schemes": maybe_eligible,
        "not_eligible_schemes": not_eligible,
    }


def route_input(state: GraphState) -> str:
    """Route based on input method."""
    if state.get("voice_transcript"):
        return "nlu_parser"
    return "intake"


def check_profile_valid(state: GraphState) -> str:
    """Check if profile was parsed."""
    if state.get("parse_error"):
        return "error"
    if not state.get("user_profile"):
        return "error"
    return "run_engine"


# ------- Build and run -------

def build_and_run(initial_state: dict) -> dict:
    """Run the pipeline directly without LangGraph (simpler, no dependency issues)."""
    state = dict(initial_state)

    # Step 1: Route and parse input
    if state.get("voice_transcript"):
        result = nlu_parser_node(state)
    elif state.get("raw_form_data"):
        result = intake_node(state)
    else:
        return {"parse_error": "No input provided"}

    state.update(result)

    # Step 2: Check for errors
    if state.get("parse_error"):
        return state

    # Step 3: Run eligibility engine
    result = eligibility_engine_node(state)
    state.update(result)

    return state


def run_eligibility_check(form_data: dict = None, voice_transcript: str = None) -> dict:
    """
    Run eligibility check with either form data or voice transcript.
    """
    initial_state = {}

    if voice_transcript:
        initial_state["voice_transcript"] = voice_transcript
    elif form_data:
        initial_state["raw_form_data"] = form_data
    else:
        raise ValueError("Either form_data or voice_transcript must be provided")

    return build_and_run(initial_state)


if __name__ == "__main__":
    test_data = {
        "state": "TX",
        "household_size": 3,
        "income": 24000,
        "has_children": True,
        "children_ages": "3, 7",
        "is_pregnant": False,
        "is_employed": True,
        "employment_type": "part-time",
        "is_single_parent": True,
    }

    print("Running eligibility check...")
    result = run_eligibility_check(form_data=test_data)

    print(f"\n✅ Eligible ({len(result.get('eligible_schemes', []))}):")
    for s in result.get("eligible_schemes", []):
        print(f"  - {s['name']} ({s['confidence']*100:.0f}%): {s['reason']}")

    print(f"\n⚠️ Maybe ({len(result.get('maybe_eligible_schemes', []))}):")
    for s in result.get("maybe_eligible_schemes", []):
        print(f"  - {s['name']} ({s['confidence']*100:.0f}%): {s['reason']}")

    print(f"\n❌ Not Eligible ({len(result.get('not_eligible_schemes', []))}):")
    for s in result.get("not_eligible_schemes", []):
        print(f"  - {s['name']}: {s['reason']}")
