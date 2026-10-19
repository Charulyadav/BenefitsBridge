# pages/admin.py - Government Admin Portal

import streamlit as st
from datetime import datetime
import json

from utils.db import (
    load_schemes,
    save_schemes,
    get_schemes_by_jurisdiction,
    add_scheme,
    update_scheme,
    delete_scheme
)
from config import ADMIN_PASSWORDS, US_STATES

# Page config
st.set_page_config(
    page_title="BenefitsBridge Admin",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global Styles (Dark Theme) ───────────────────────────────────────────────
st.markdown("""
<style>
/* ── Reset & Base ─────────────────────────────────────────────── */
header[data-testid="stHeader"] {
    background: transparent !important;
}
button[data-testid="stBaseButton-headerNoPadding"] {
    visibility: visible !important;
    color: #94a3b8 !important;
}
button[data-testid="stBaseButton-headerNoPadding"]:hover {
    color: #f1f5f9 !important;
}

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

.stApp {
    background:
        radial-gradient(circle at 20% 20%, rgba(59,130,246,0.22), transparent 40%),
        radial-gradient(circle at 80% 30%, rgba(16,185,129,0.12), transparent 40%),
        linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #020617 100%);
}

/* ── Admin Header ──────────────────────────────────────────────── */
.admin-header {
    background: linear-gradient(135deg, rgba(30,64,175,0.4) 0%, rgba(4,120,87,0.3) 100%);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 2rem;
    border-radius: 12px;
    margin: 2rem;
    backdrop-filter: blur(12px);
}
.admin-header h1 {
    color: #f1f5f9;
    margin: 0 0 0.5rem 0;
    font-size: 1.75rem;
    font-weight: 700;
}
.admin-header p {
    color: #94a3b8;
    margin: 0;
    font-size: 0.95rem;
}

/* ── Login Card ───────────────────────────────────────────────── */
.login-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 2rem;
    backdrop-filter: blur(12px);
}

/* ── Text Visibility (dark theme) ─────────────────────────────── */
.stApp, .stApp p, .stApp li, .stApp span, .stApp div {
    color: #cbd5e1;
}

/* Headings */
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
.stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
h1, h2, h3, h4, h5, h6 {
    color: #f1f5f9 !important;
}

/* Subheader styling */
div[data-testid="stSubheader"] {
    color: #f1f5f9 !important;
}

/* Form labels */
.stSelectbox label, .stNumberInput label, .stTextInput label,
.stCheckbox label, .stTextArea label, .stSlider label {
    color: #cbd5e1 !important;
    font-weight: 500 !important;
    font-size: 13.5px !important;
}

/* Checkbox text */
.stCheckbox label p,
.stCheckbox label span,
.stCheckbox span[data-testid="stCheckboxLabel"] {
    color: #cbd5e1 !important;
}

/* Input fields - dark text on light background */
.stSelectbox div[data-baseweb="select"] span,
.stSelectbox div[data-baseweb="select"] div,
.stNumberInput input,
.stTextInput input,
.stTextArea textarea {
    color: #1e293b !important;
}

/* Placeholder text */
input::placeholder, textarea::placeholder {
    color: #64748b !important;
}

/* ── Form Styling ─────────────────────────────────────────────── */
div[data-testid="stForm"] {
    border: 1px solid rgba(255,255,255,0.08) !important;
    background: rgba(15,23,42,0.5) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
}

/* Divider */
hr {
    border-color: rgba(255,255,255,0.08) !important;
}

/* ── Button Overrides ─────────────────────────────────────────── */
div.stButton > button[kind="primary"],
div.stFormSubmitButton > button {
    background: #ea580c !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
}
div.stButton > button[kind="primary"]:hover,
div.stFormSubmitButton > button:hover {
    background: #c2410c !important;
}
div.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #fb923c !important;
    border: 2px solid rgba(234,88,12,0.5) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
div.stButton > button[kind="secondary"]:hover {
    border-color: #ea580c !important;
    background: rgba(234,88,12,0.1) !important;
}

/* Default buttons */
div.stButton > button {
    background: rgba(255,255,255,0.06) !important;
    color: #cbd5e1 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 8px !important;
}
div.stButton > button:hover {
    background: rgba(255,255,255,0.1) !important;
    border-color: rgba(255,255,255,0.2) !important;
}

/* ── Tab Overrides ────────────────────────────────────────────── */
div[data-testid="stTabs"] button {
    color: #64748b !important;
    font-weight: 500 !important;
    background: transparent !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #fb923c !important;
    border-bottom-color: #ea580c !important;
}
div[data-testid="stTabs"] button:hover {
    color: #94a3b8 !important;
}

/* ── Expander Overrides ───────────────────────────────────────── */
details[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}
details summary span {
    color: #f1f5f9 !important;
}
details[data-testid="stExpander"] .stMarkdown,
details[data-testid="stExpander"] .stMarkdown p {
    color: #94a3b8 !important;
}

/* ── Metric Overrides ─────────────────────────────────────────── */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1rem 1.2rem;
}
div[data-testid="stMetric"] label {
    color: #64748b !important;
    font-size: 13px !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #f1f5f9 !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
    color: #4ade80 !important;
}

/* ── Alert Boxes ──────────────────────────────────────────────── */
div[data-testid="stAlert"] {
    border-radius: 8px !important;
}

/* Info box */
div[data-testid="stAlert"][data-baseweb="notification"] {
    background: rgba(59,130,246,0.1) !important;
    border: 1px solid rgba(59,130,246,0.2) !important;
}

/* ── Toggle Switch ────────────────────────────────────────────── */
div[data-testid="stToggle"] label span {
    color: #cbd5e1 !important;
}

/* ── Slider ───────────────────────────────────────────────────── */
div[data-testid="stSlider"] > div > div {
    color: #cbd5e1 !important;
}

/* ── Caption ──────────────────────────────────────────────────── */
.stCaption, div[data-testid="stCaptionContainer"] {
    color: #64748b !important;
}

/* ── Download Button ──────────────────────────────────────────── */
div[data-testid="stDownloadButton"] button {
    background: rgba(34,197,94,0.15) !important;
    color: #4ade80 !important;
    border: 1px solid rgba(34,197,94,0.3) !important;
}
div[data-testid="stDownloadButton"] button:hover {
    background: rgba(34,197,94,0.25) !important;
}

/* ── Streamlit Component Padding ──────────────────────────────── */
div[data-testid="stHorizontalBlock"],
div[data-testid="stForm"],
div[data-testid="stVerticalBlockBorderWrapper"] {
    margin-left: 2rem;
    margin-right: 2rem;
}

div[data-testid="stForm"] div[data-testid="stHorizontalBlock"] {
    margin-left: 0;
    margin-right: 0;
}

details[data-testid="stExpander"] {
    margin-left: 2rem;
    margin-right: 2rem;
}

div[data-testid="stTabs"] {
    margin-left: 2rem;
    margin-right: 2rem;
}

div[data-testid="stAlert"] {
    margin-left: 2rem;
    margin-right: 2rem;
}

div[data-testid="stMarkdownContainer"] hr {
    margin-left: 2rem;
    margin-right: 2rem;
}

/* Subheader padding */
div[data-testid="stSubheader"] {
    padding-left: 2rem;
}

/* ── Status Badges ────────────────────────────────────────────── */
.status-active {
    color: #4ade80;
    background: rgba(34,197,94,0.12);
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
}
.status-inactive {
    color: #f87171;
    background: rgba(239,68,68,0.12);
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
}

/* ── Scheme Card Info ─────────────────────────────────────────── */
.scheme-info {
    color: #94a3b8;
    font-size: 14px;
    line-height: 1.7;
}
.scheme-info strong {
    color: #cbd5e1;
}

/* ── Analytics Card ───────────────────────────────────────────── */
.analytics-item {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    padding: 12px 16px;
    margin: 6px 0;
    color: #94a3b8;
    font-size: 14px;
}
.analytics-item::before {
    content: "•";
    color: #fb923c;
    margin-right: 10px;
}

/* ── Settings Section ─────────────────────────────────────────── */
.settings-label {
    color: #f1f5f9;
    font-weight: 600;
    font-size: 15px;
    margin-bottom: 12px;
}

/* ── Section Divider ──────────────────────────────────────────── */
.section-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.08);
    margin: 1.5rem 0;
}

/* ── Form Section Label ───────────────────────────────────────── */
.form-section {
    color: #f1f5f9;
    font-weight: 600;
    font-size: 14px;
    margin: 1rem 0 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
    if "admin_jurisdiction" not in st.session_state:
        st.session_state.admin_jurisdiction = None
    if "admin_email" not in st.session_state:
        st.session_state.admin_email = None
    if "editing_scheme" not in st.session_state:
        st.session_state.editing_scheme = None


def login_page():
    """Display login page"""
    st.markdown("""
    <div class="admin-header">
        <h1>🏛️ BenefitsBridge Admin Portal</h1>
        <p>Government administrators can manage benefit schemes here</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.subheader("Administrator Login")

        with st.form("login_form"):
            jurisdiction = st.selectbox(
                "Select Your Jurisdiction",
                [
                    "",
                    "federal",
                    "--- States ---",
                    "TX", "CA", "NY", "MA", "FL",
                    "--- Counties ---",
                    "Harris County",
                    "Los Angeles County"
                ]
            )

            # Filter out separator options
            if jurisdiction.startswith("---"):
                jurisdiction = ""

            email = st.text_input("Admin Email", placeholder="admin@agency.gov")
            password = st.text_input("Password", type="password")

            submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted:
                if not jurisdiction:
                    st.error("Please select a jurisdiction")
                elif not email:
                    st.error("Please enter your email")
                elif ADMIN_PASSWORDS.get(jurisdiction) == password:
                    st.session_state.admin_logged_in = True
                    st.session_state.admin_jurisdiction = jurisdiction
                    st.session_state.admin_email = email
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        st.caption("Demo credentials: Use jurisdiction name as password (e.g., 'texas_admin_2024' for TX)")


def get_jurisdiction_level(jurisdiction: str) -> str:
    """Determine the level based on jurisdiction"""
    if jurisdiction == "federal":
        return "federal"
    elif jurisdiction in US_STATES:
        return "state"
    else:
        return "county"


def admin_dashboard():
    """Main admin dashboard"""
    jurisdiction = st.session_state.admin_jurisdiction
    email = st.session_state.admin_email
    level = get_jurisdiction_level(jurisdiction)

    # Header with logout
    st.markdown(f"""
    <div class="admin-header">
        <h1>{jurisdiction} Admin Portal</h1>
        <p>Logged in as: {email}</p>
    </div>
    """, unsafe_allow_html=True)

    # Logout button
    col1, col2, col3 = st.columns([4, 1, 1])
    with col3:
        if st.button("Logout", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.session_state.admin_jurisdiction = None
            st.session_state.admin_email = None
            st.rerun()

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "My Schemes",
        "Add New Scheme",
        "Analytics",
        "Settings"
    ])

    with tab1:
        view_schemes_tab(jurisdiction)

    with tab2:
        add_scheme_tab(jurisdiction, level, email)

    with tab3:
        analytics_tab(jurisdiction)

    with tab4:
        settings_tab()


def view_schemes_tab(jurisdiction: str):
    """View and manage existing schemes"""
    st.subheader("Schemes Management")

    # Toggle between jurisdiction-only and all schemes
    show_all = st.toggle("Show ALL schemes in the system", value=False)

    if show_all:
        schemes = load_schemes()
        st.info(f"Showing all {len(schemes)} schemes across all jurisdictions")
    else:
        schemes = get_schemes_by_jurisdiction(jurisdiction)
        if jurisdiction == "federal":
            st.info(f"Showing {len(schemes)} federal-level schemes")
        else:
            federal_schemes = [s for s in load_schemes() if s["level"] == "federal"]
            schemes = schemes + federal_schemes
            st.info(f"Showing {len(schemes)} schemes (your jurisdiction + federal)")

    if not schemes:
        st.info("No schemes found. Add your first scheme!")
        return

    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_category = st.selectbox(
            "Filter by Category",
            ["All"] + list(set(s.get("category", "") for s in schemes))
        )
    with col2:
        filter_status = st.selectbox(
            "Filter by Status",
            ["All", "Active", "Inactive"]
        )
    with col3:
        search = st.text_input("Search", placeholder="Search schemes...")

    # Apply filters
    filtered = schemes
    if filter_category != "All":
        filtered = [s for s in filtered if s.get("category") == filter_category]
    if filter_status == "Active":
        filtered = [s for s in filtered if s.get("is_active", True)]
    elif filter_status == "Inactive":
        filtered = [s for s in filtered if not s.get("is_active", True)]
    if search:
        search_lower = search.lower()
        filtered = [s for s in filtered if
                    search_lower in s.get("name", "").lower() or
                    search_lower in s.get("description", "").lower()]

    st.markdown(f"<p style='color:#94a3b8; padding-left:2rem;'>Showing {len(filtered)} of {len(schemes)} schemes</p>",
                unsafe_allow_html=True)

    # Display schemes
    for scheme in filtered:
        status_icon = '✅' if scheme.get('is_active', True) else '❌'
        with st.expander(f"{status_icon} **{scheme.get('name')}** — {scheme.get('category', 'N/A').title()}"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"""
                <div class="scheme-info">
                    <p><strong>ID:</strong> <code style="background:rgba(255,255,255,0.1);padding:2px 8px;border-radius:4px;color:#fb923c;">{scheme.get('id')}</code></p>
                    <p><strong>Description:</strong> {scheme.get('description', 'N/A')}</p>
                    <p><strong>Level:</strong> {scheme.get('level', 'N/A').title()}</p>
                    {'<p><strong>State:</strong> ' + scheme.get('state') + '</p>' if scheme.get("state") else ''}
                </div>
                """, unsafe_allow_html=True)

                criteria = scheme.get("criteria", {})
                if criteria.get("max_income_percent_fpl"):
                    st.markdown(
                        f"<p class='scheme-info'><strong>Income Limit:</strong> {criteria['max_income_percent_fpl']}% FPL</p>",
                        unsafe_allow_html=True)

                st.markdown(f"""
                <div class="scheme-info">
                    <p><strong>Priority Score:</strong> {scheme.get('priority_score', 5)}/10</p>
                    <p><strong>Last Updated:</strong> {scheme.get('last_updated', 'N/A')}</p>
                    <p><strong>Apply URL:</strong> <a href="{scheme.get('apply_url', '#')}" style="color:#60a5fa;">{scheme.get('apply_url', 'N/A')[:50]}...</a></p>
                </div>
                """, unsafe_allow_html=True)

                if scheme.get("benefit_amount"):
                    st.markdown(
                        f"<p class='scheme-info'><strong>Benefit Amount:</strong> {scheme.get('benefit_amount')}</p>",
                        unsafe_allow_html=True)
                if scheme.get("processing_time"):
                    st.markdown(
                        f"<p class='scheme-info'><strong>Processing Time:</strong> {scheme.get('processing_time')}</p>",
                        unsafe_allow_html=True)

                docs = scheme.get("documents_needed", [])
                if docs:
                    st.markdown(
                        f"<p class='scheme-info'><strong>Documents Required:</strong> {', '.join(docs[:3])}{'...' if len(docs) > 3 else ''}</p>",
                        unsafe_allow_html=True)

                care = scheme.get("customer_care", {})
                if care:
                    st.markdown(
                        f"<p class='scheme-info'><strong>Customer Care:</strong> {care.get('phone', 'N/A')} ({care.get('hours', 'N/A')})</p>",
                        unsafe_allow_html=True)

            with col2:
                is_active = scheme.get("is_active", True)
                if st.button(
                        "Deactivate" if is_active else "Activate",
                        key=f"toggle_{scheme['id']}",
                        use_container_width=True
                ):
                    update_scheme(scheme["id"], {"is_active": not is_active})
                    st.rerun()

                if st.button("Edit", key=f"edit_{scheme['id']}", use_container_width=True):
                    st.session_state.editing_scheme = scheme["id"]
                    st.rerun()

                if st.button("Delete", key=f"del_{scheme['id']}", use_container_width=True):
                    if delete_scheme(scheme["id"]):
                        st.success("Scheme deleted")
                        st.rerun()


def add_scheme_tab(jurisdiction: str, level: str, email: str):
    """Add a new scheme"""
    st.subheader("Add New Scheme")

    with st.form("add_scheme_form"):
        # Basic info
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Scheme Name*", placeholder="e.g., Emergency Rental Assistance")
        with col2:
            short_name = st.text_input("Short Name", placeholder="e.g., ERA")

        description = st.text_area(
            "Description*",
            placeholder="Describe what this program provides and who it helps..."
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            category = st.selectbox(
                "Category*",
                ["nutrition", "healthcare", "housing", "childcare",
                 "education", "financial", "employment", "utilities", "safety"]
            )
        with col2:
            priority = st.slider("Priority Score", 1, 10, 5)
        with col3:
            is_active = st.checkbox("Active", value=True)

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        # Eligibility Criteria
        st.markdown('<p class="form-section">Eligibility Criteria</p>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            max_income_fpl = st.number_input(
                "Max Income (% FPL)",
                min_value=0,
                max_value=500,
                value=200,
                help="Maximum income as percentage of Federal Poverty Level"
            )
        with col2:
            requires_children = st.checkbox("Requires Children")
            if requires_children:
                max_child_age = st.number_input("Max Child Age", 0, 25, 18)
            else:
                max_child_age = None
        with col3:
            requires_employment = st.checkbox("Requires Employment")
            requires_pregnancy = st.checkbox("Pregnancy-related")

        citizenship_required = st.checkbox("US Citizenship Required", value=True)
        custom_rules = st.text_area(
            "Additional Eligibility Rules",
            placeholder="Any other eligibility requirements..."
        )

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        # Application Info
        st.markdown('<p class="form-section">Application Information</p>', unsafe_allow_html=True)
        apply_url = st.text_input("Application URL*", placeholder="https://...")
        apply_phone = st.text_input("Phone Number", placeholder="1-800-...")

        next_steps = st.text_area(
            "Next Steps (one per line)",
            placeholder="Visit local office\nGather documents\nComplete application"
        )

        documents = st.text_area(
            "Required Documents (one per line)",
            placeholder="Photo ID\nProof of income\nProof of residence"
        )

        benefit_amount = st.text_input(
            "Benefit Amount",
            placeholder="e.g., $500/month, Up to $2000"
        )

        benefit_type = st.text_input(
            "Benefit Type",
            placeholder="e.g., EBT Card, Health Insurance, Direct Deposit"
        )

        processing_time = st.text_input(
            "Processing Time",
            placeholder="e.g., 30 days, 2-4 weeks"
        )

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        # Customer Care Info
        st.markdown('<p class="form-section">Customer Care Information</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            care_phone = st.text_input("Customer Care Phone", placeholder="1-800-...")
            care_hours = st.text_input("Hours of Operation", placeholder="Mon-Fri 8AM-5PM EST")
        with col2:
            care_website = st.text_input("Support Website", placeholder="https://...")
            care_notes = st.text_input("Helpful Tips", placeholder="e.g., Dial 2-1-1 for local help")

        # Submit
        submitted = st.form_submit_button("Add Scheme", use_container_width=True)

        if submitted:
            if not name or not description or not apply_url:
                st.error("Please fill in all required fields")
            else:
                scheme_id = f"{jurisdiction.lower().replace(' ', '-')}-{name.lower().replace(' ', '-')[:30]}"

                new_scheme = {
                    "id": scheme_id,
                    "name": name,
                    "short_name": short_name if short_name else None,
                    "description": description,
                    "category": category,
                    "level": level,
                    "state": jurisdiction if level == "state" else None,
                    "county": jurisdiction if level == "county" else None,
                    "criteria": {
                        "max_income_percent_fpl": max_income_fpl if max_income_fpl > 0 else None,
                        "requires_children": requires_children,
                        "max_child_age": max_child_age,
                        "requires_employment": requires_employment,
                        "requires_pregnancy": requires_pregnancy,
                        "citizenship_required": citizenship_required,
                        "custom_rules": custom_rules if custom_rules else None
                    },
                    "apply_url": apply_url,
                    "apply_phone": apply_phone if apply_phone else None,
                    "customer_care": {
                        "phone": care_phone if care_phone else (apply_phone if apply_phone else "N/A"),
                        "hours": care_hours if care_hours else "Check website",
                        "website": care_website if care_website else apply_url,
                        "notes": care_notes if care_notes else ""
                    },
                    "next_steps": [s.strip() for s in next_steps.split("\n") if s.strip()],
                    "documents_needed": [s.strip() for s in documents.split("\n") if s.strip()],
                    "benefit_amount": benefit_amount if benefit_amount else None,
                    "benefit_type": benefit_type if benefit_type else None,
                    "processing_time": processing_time if processing_time else None,
                    "is_active": is_active,
                    "priority_score": priority,
                    "added_by": email,
                    "last_updated": datetime.now().strftime("%Y-%m-%d")
                }

                schemes = load_schemes()

                if any(s["id"] == scheme_id for s in schemes):
                    st.error("A scheme with this name already exists")
                else:
                    schemes.append(new_scheme)
                    save_schemes(schemes)
                    st.success(f"Successfully added: **{name}**")
                    st.balloons()


def analytics_tab(jurisdiction: str):
    """Show usage analytics"""
    st.subheader("Analytics Dashboard")

    st.info("Analytics features coming soon! In production, this would show:")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Queries", "1,247", "+23%")
    with col2:
        st.metric("Matches Found", "892", "+18%")
    with col3:
        st.metric("Applications Started", "341", "+12%")
    with col4:
        st.metric("Unique Users", "567", "+15%")

    st.markdown('<hr class="section-divider" style="margin-left:2rem;margin-right:2rem;">', unsafe_allow_html=True)

    st.markdown('<p class="settings-label" style="padding-left:2rem;">Planned Analytics Features</p>',
                unsafe_allow_html=True)

    features = [
        "Query volume over time",
        "Most searched programs",
        "Eligibility match rates by program",
        "Geographic distribution of users",
        "Application conversion rates",
        "Common eligibility gaps"
    ]

    for feature in features:
        st.markdown(f'<div class="analytics-item" style="margin-left:2rem;margin-right:2rem;">{feature}</div>',
                    unsafe_allow_html=True)


def settings_tab():
    """Admin settings"""
    st.subheader("Settings")

    st.markdown(f"""
    <div style="padding-left:2rem;">
        <p class="settings-label">Account Settings</p>
        <p class="scheme-info"><strong>Jurisdiction:</strong> {st.session_state.admin_jurisdiction}</p>
        <p class="scheme-info"><strong>Email:</strong> {st.session_state.admin_email}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider" style="margin-left:2rem;margin-right:2rem;">', unsafe_allow_html=True)

    st.markdown('<p class="settings-label" style="padding-left:2rem;">Notification Preferences</p>',
                unsafe_allow_html=True)
    st.checkbox("Email me when new users query my schemes", value=True)
    st.checkbox("Weekly analytics digest", value=True)
    st.checkbox("Alert on eligibility rule changes", value=True)

    st.markdown('<hr class="section-divider" style="margin-left:2rem;margin-right:2rem;">', unsafe_allow_html=True)

    st.markdown('<p class="settings-label" style="padding-left:2rem;">Data Management</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Export My Schemes (JSON)"):
            schemes = get_schemes_by_jurisdiction(st.session_state.admin_jurisdiction)
            st.download_button(
                "Download JSON",
                data=json.dumps(schemes, indent=2),
                file_name=f"{st.session_state.admin_jurisdiction}_schemes.json",
                mime="application/json"
            )

    with col2:
        st.button("Import Schemes (CSV)", disabled=True)
        st.caption("Coming soon")


def main():
    """Main function"""
    init_session_state()

    if not st.session_state.admin_logged_in:
        login_page()
    else:
        admin_dashboard()


if __name__ == "__main__":
    main()
