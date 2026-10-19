# app.py - BenefitsBridge Women Portal

import streamlit as st
import time
import streamlit.components.v1 as components
from typing import Dict

from graph import run_eligibility_check
from config import US_STATES

# Page configuration
st.set_page_config(
    page_title="BenefitsBridge",
    page_icon="BB",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global Styles ────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Reset & Base ─────────────────────────────────────────────── */
/* Hide header elements but keep sidebar toggle visible */
header[data-testid="stHeader"] {
    background: transparent !important;
}
header[data-testid="stHeader"] > div:first-child {
    background: transparent !important;
}
/* Keep the sidebar toggle button visible and styled */
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

/* ── Navbar ────────────────────────────────────────────────────── */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 2rem;
    background: rgba(15, 23, 42, 0.95);
    border-bottom: 1px solid rgba(255,255,255,0.08);
    position: sticky;
    top: 0;
    z-index: 9999;
    backdrop-filter: blur(12px);
}
.nav-left {
    display: flex;
    align-items: center;
    gap: 12px;
}
.nav-logo {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #1e40af, #047857);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 800;
    color: white;
    letter-spacing: -0.5px;
}
.nav-brand {
    font-weight: 700;
    font-size: 18px;
    color: #f1f5f9;
}
.nav-brand span { color: #fb923c; }
.nav-subtitle {
    font-size: 11.5px;
    color: #94a3b8;
    margin-top: -2px;
    letter-spacing: 0.2px;
}

/* ── Hero ──────────────────────────────────────────────────────── */
.hero {
    padding: 3rem 2rem 2rem 2rem;
    color: #f1f5f9;
}
.hero-badge {
    display: inline-block;
    border: 1.5px solid rgba(255,255,255,0.2);
    padding: 4px 14px;
    border-radius: 999px;
    font-size: 12px;
    color: #cbd5e1;
    backdrop-filter: blur(8px);
    background: rgba(255,255,255,0.06);
    letter-spacing: 0.3px;
    margin-bottom: 1rem;
}
.hero h1 {
    font-size: 2.6rem;
    font-weight: 800;
    line-height: 1.15;
    margin: 0;
    color: #f1f5f9;
}
.hero h1 .accent { color: #fb923c; }
.hero-desc {
    color: #94a3b8;
    font-size: 1.05rem;
    line-height: 1.7;
    margin-top: 1rem;
    max-width: 640px;
}

/* ── Content Panel ────────────────────────────────────────────── */
.content-panel {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    margin: 0 2rem 2rem 2rem;
    padding: 2rem;
    backdrop-filter: blur(12px);
}
.panel-title {
    color: #f1f5f9;
    font-size: 1.15rem;
    font-weight: 600;
    margin-bottom: 0.3rem;
    padding-left: 2rem;
}
.panel-subtitle {
    color: #94a3b8;
    font-size: 0.88rem;
    margin-bottom: 1.5rem;
    padding-left: 2rem;
}

/* ── Voice Section ────────────────────────────────────────────── */
.voice-instruction {
    color: #94a3b8;
    font-weight: 500;
    font-size: 14px;
    padding-left: 2rem;
}

/* ── Section Labels ───────────────────────────────────────────── */
.section-label {
    color: #64748b;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
    margin-top: 16px;
}
.section-label:first-child {
    margin-top: 0;
}

/* ── Form Overrides ───────────────────────────────────────────── */
.stSelectbox label, .stNumberInput label, .stTextInput label,
.stCheckbox label, .stTextArea label {
    color: #cbd5e1 !important;
    font-weight: 500 !important;
    font-size: 13.5px !important;
}
div[data-testid="stForm"] {
    border: 1px solid rgba(255,255,255,0.08) !important;
    background: rgba(15,23,42,0.5) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
}

/* ── Text Visibility (dark theme) ─────────────────────────────── */
.stApp, .stApp p, .stApp li, .stApp span, .stApp div {
    color: #cbd5e1;
}

/* Checkbox label text */
.stCheckbox label p,
.stCheckbox label span,
.stCheckbox span[data-testid="stCheckboxLabel"] {
    color: #cbd5e1 !important;
}

/* Selectbox / dropdown text */
.stSelectbox [data-testid="stWidgetLabel"] {
    color: #cbd5e1 !important;
}
.stSelectbox div[data-baseweb="select"] span,
.stSelectbox div[data-baseweb="select"] div {
    color: #1e293b !important;
}

/* Number input text */
.stNumberInput input,
.stNumberInput div[data-baseweb] input {
    color: #1e293b !important;
}

/* Text input text */
.stTextInput input,
.stTextInput div[data-baseweb] input {
    color: #1e293b !important;
}

/* Text area */
.stTextArea textarea {
    color: #1e293b !important;
}

/* Markdown content */
.stMarkdown, .stMarkdown p, .stMarkdown li,
.stMarkdown ol li, .stMarkdown ul li,
.stMarkdown strong, .stMarkdown b {
    color: #cbd5e1 !important;
}

/* Section headers */
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
.stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
    color: #f1f5f9 !important;
}

/* Expander body text */
details[data-testid="stExpander"] .stMarkdown,
details[data-testid="stExpander"] .stMarkdown p,
details[data-testid="stExpander"] .stMarkdown li,
details[data-testid="stExpander"] .stMarkdown strong {
    color: #94a3b8 !important;
}

/* Placeholder text */
input::placeholder, textarea::placeholder {
    color: #64748b !important;
}

/* Divider */
hr { border-color: rgba(255,255,255,0.08) !important; }

/* Spinner text */
.stSpinner > div { color: #cbd5e1 !important; }

/* Link button text */
a[data-testid="stBaseLinkButton-primary"] p,
div.stLinkButton a p {
    color: #ffffff !important;
}

/* ── Streamlit Button Override ────────────────────────────────── */
div.stButton > button[kind="primary"],
div.stFormSubmitButton > button {
    background: #ea580c !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    letter-spacing: 0.2px !important;
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

/* ── Metric Overrides ─────────────────────────────────────────── */
div[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1rem 1.2rem;
}
div[data-testid="stMetric"] label { color: #64748b !important; font-size: 13px !important; }
div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #f1f5f9 !important; }

/* ── Tab Overrides ────────────────────────────────────────────── */
div[data-testid="stTabs"] button {
    color: #64748b !important;
    font-weight: 500 !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #fb923c !important;
    border-bottom-color: #ea580c !important;
}

/* ── Expander Overrides ───────────────────────────────────────── */
details[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}
details summary span { color: #f1f5f9 !important; }

/* ── Result Cards ─────────────────────────────────────────────── */
.result-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 6px;
}
.result-name {
    font-size: 1.05rem;
    font-weight: 600;
    color: #f1f5f9;
}
.result-cat {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.4px;
    text-transform: uppercase;
}
.cat-nutrition   { background: rgba(34,197,94,0.12); color: #4ade80; }
.cat-healthcare  { background: rgba(59,130,246,0.12); color: #60a5fa; }
.cat-housing     { background: rgba(250,204,21,0.12); color: #facc15; }
.cat-childcare   { background: rgba(244,114,182,0.12); color: #f472b6; }
.cat-education   { background: rgba(167,139,250,0.12); color: #a78bfa; }
.cat-financial   { background: rgba(45,212,191,0.12); color: #2dd4bf; }
.cat-employment  { background: rgba(251,146,60,0.12); color: #fb923c; }
.cat-utilities   { background: rgba(148,163,184,0.12); color: #94a3b8; }

.conf-bar {
    height: 6px;
    border-radius: 3px;
    background: rgba(255,255,255,0.06);
    margin: 8px 0;
    overflow: hidden;
}
.conf-fill {
    height: 100%;
    border-radius: 3px;
}
.conf-high  { background: #22c55e; }
.conf-med   { background: #facc15; }
.conf-low   { background: #ef4444; }

.reason-text {
    color: #94a3b8;
    font-size: 14px;
    line-height: 1.6;
    margin: 6px 0 10px 0;
}

.benefit-box {
    background: rgba(34,197,94,0.06);
    border: 1px solid rgba(34,197,94,0.15);
    border-radius: 8px;
    padding: 10px 14px;
    margin: 8px 0;
    font-size: 13.5px;
    color: #86efac;
}
.benefit-box strong { color: #4ade80; }

.care-box {
    background: rgba(59,130,246,0.06);
    border: 1px solid rgba(59,130,246,0.12);
    border-radius: 8px;
    padding: 12px 14px;
    margin-top: 6px;
}
.care-box h4 { color: #60a5fa; margin: 0 0 6px 0; font-size: 13.5px; font-weight: 600; }
.care-box p  { margin: 2px 0; font-size: 13px; color: #94a3b8; }
.care-box a  { color: #60a5fa; }

/* ── Success / Warning / Error Overrides ──────────────────────── */
div[data-testid="stAlert"] { border-radius: 8px !important; }

/* ── Footer ───────────────────────────────────────────────────── */
.footer {
    text-align: center;
    color: #475569;
    padding: 2.5rem 2rem 1.5rem 2rem;
    font-size: 13px;
    letter-spacing: 0.2px;
}
.footer a { color: #64748b; text-decoration: underline; }

/* ── Link Buttons ─────────────────────────────────────────────── */
a[data-testid="stBaseLinkButton-primary"],
a[data-testid="stBaseLinkButton-secondary"],
a[data-testid="baseLinkButton-secondary"],
div.stLinkButton a {
    background: #ea580c !important;
    border-radius: 8px !important;
    border: none !important;
}
div.stLinkButton a p,
div.stLinkButton a span {
    color: #ffffff !important;
}

/* ── Toggle Buttons Container ─────────────────────────────────── */
.toggle-container {
    padding: 0 2rem 1.5rem 2rem;
}

/* ── Streamlit Component Padding ──────────────────────────────── */
/* Horizontal padding for native Streamlit elements below hero */
div[data-testid="stHorizontalBlock"],
div[data-testid="stForm"],
div[data-testid="stVerticalBlockBorderWrapper"] {
    margin-left: 2rem;
    margin-right: 2rem;
}

/* Fix for nested horizontal blocks (columns inside forms) */
div[data-testid="stForm"] div[data-testid="stHorizontalBlock"] {
    margin-left: 0;
    margin-right: 0;
}

/* Expander padding */
details[data-testid="stExpander"] {
    margin-left: 2rem;
    margin-right: 2rem;
}

/* Tabs padding */
div[data-testid="stTabs"] {
    margin-left: 2rem;
    margin-right: 2rem;
}

/* Alert/info/success boxes */
div[data-testid="stAlert"] {
    margin-left: 2rem;
    margin-right: 2rem;
}

/* Metrics row */
div[data-testid="stMetric"] {
    /* Already has margin from horizontal block parent */
}

/* Dividers */
div[data-testid="stMarkdownContainer"] hr {
    margin-left: 2rem;
    margin-right: 2rem;
}

/* HTML Components (speech widget) */
iframe[title="streamlit_components.v1.components.html"] {
    margin-left: 2rem !important;
    margin-right: 2rem !important;
    width: calc(100% - 4rem) !important;
}

/* Text area in voice section */
div[data-testid="stTextArea"] {
    margin-left: 2rem;
    margin-right: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ── Navbar ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <div class="nav-left">
        <div class="nav-logo">BB</div>
        <div>
            <div class="nav-brand">Benefits<span>Bridge</span></div>
            <div class="nav-subtitle">Government Scheme Finder</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">Government Scheme Discovery Platform</div>
    <h1>Find Every Benefit<br><span class="accent">You Deserve</span></h1>
    <p class="hero-desc">
        Many women miss out on the government benefits they are entitled to.
        BenefitsBridge instantly matches your profile to all eligible Federal
        and State schemes &mdash; free, fast, and verified.
    </p>
</div>
""", unsafe_allow_html=True)


# ── Category Helpers ─────────────────────────────────────────────────────────
CAT_CLASSES = {
    "nutrition": "cat-nutrition", "healthcare": "cat-healthcare",
    "housing": "cat-housing", "childcare": "cat-childcare",
    "education": "cat-education", "financial": "cat-financial",
    "employment": "cat-employment", "utilities": "cat-utilities",
}


def display_result_card(scheme: Dict):
    """Render a single result card inside an expander."""
    name = scheme.get("name", "Unknown")
    category = scheme.get("category", "")
    reason = scheme.get("reason", "")
    confidence = scheme.get("confidence", 0.5)
    apply_url = scheme.get("apply_url", "")
    next_steps = scheme.get("next_steps", [])
    documents = scheme.get("documents_needed", [])
    customer_care = scheme.get("customer_care", {})
    benefit_amount = scheme.get("benefit_amount", "")
    benefit_type = scheme.get("benefit_type", "")
    processing_time = scheme.get("processing_time", "")
    apply_phone = scheme.get("apply_phone", "")

    cat_cls = CAT_CLASSES.get(category, "cat-financial")
    conf_pct = int(confidence * 100)
    conf_cls = "conf-high" if confidence >= 0.8 else ("conf-med" if confidence >= 0.6 else "conf-low")

    with st.expander(f"**{name}**  —  {category.title()}"):
        st.markdown(
            f'<span class="result-cat {cat_cls}">{category}</span>'
            f'&nbsp;&nbsp;<span style="color:#64748b;font-size:12px;">{conf_pct}% confidence</span>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="conf-bar"><div class="conf-fill {conf_cls}" style="width:{conf_pct}%"></div></div>',
            unsafe_allow_html=True
        )

        st.markdown(f'<p class="reason-text"><strong>Why you qualify:</strong> {reason}</p>', unsafe_allow_html=True)

        if benefit_amount:
            parts = [f"<strong>Benefit:</strong> {benefit_amount}"]
            if benefit_type:
                parts.append(f" &mdash; {benefit_type}")
            if processing_time:
                parts.append(f" &nbsp;|&nbsp; Processing: {processing_time}")
            st.markdown(f'<div class="benefit-box">{"".join(parts)}</div>', unsafe_allow_html=True)

        col_a, col_b = st.columns(2)

        with col_a:
            if next_steps:
                st.markdown("**Next Steps**")
                for i, step in enumerate(next_steps, 1):
                    st.markdown(f"{i}. {step}")
            if documents:
                st.markdown("---")
                st.markdown("**Documents Needed**")
                for doc in documents:
                    st.markdown(f"- {doc}")

        with col_b:
            phone = customer_care.get("phone", apply_phone or "N/A") if customer_care else (apply_phone or "N/A")
            hours = customer_care.get("hours", "Check website") if customer_care else "Check website"
            website = customer_care.get("website", apply_url or "") if customer_care else (apply_url or "")
            notes = customer_care.get("notes", "") if customer_care else ""

            st.markdown(
                f'<div class="care-box">'
                f'<h4>Contact Information</h4>'
                f'<p><strong>Phone:</strong> {phone}</p>'
                f'<p><strong>Hours:</strong> {hours}</p>'
                + (f'<p><strong>Website:</strong> <a href="{website}" target="_blank">{website[:60]}{"..." if len(website) > 60 else ""}</a></p>' if website else "")
                + (f'<p><strong>Tip:</strong> {notes}</p>' if notes else "")
                + '</div>',
                unsafe_allow_html=True
            )

        if apply_url:
            st.link_button("Apply Now", apply_url)


def display_results(result: Dict):
    """Show results organized by eligibility status."""
    eligible = result.get("eligible_schemes", [])
    maybe = result.get("maybe_eligible_schemes", [])
    not_eligible = result.get("not_eligible_schemes", [])
    total = len(eligible) + len(maybe) + len(not_eligible)

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Eligible", len(eligible))
    c2.metric("May Qualify", len(maybe))
    c3.metric("Not Eligible", len(not_eligible))
    c4.metric("Total Checked", total)
    st.markdown("---")

    tab_e, tab_m, tab_n = st.tabs([
        f"Eligible ({len(eligible)})",
        f"May Qualify ({len(maybe)})",
        f"Not Eligible ({len(not_eligible)})"
    ])

    with tab_e:
        if eligible:
            st.success(f"You likely qualify for **{len(eligible)} programs**.")
            for s in eligible:
                display_result_card(s)
        else:
            st.info("No confirmed matches. Check the 'May Qualify' tab for possible programs.")

    with tab_m:
        if maybe:
            st.warning(f"**{len(maybe)} programs** may apply to you with additional verification.")
            for s in maybe:
                display_result_card(s)
        else:
            st.info("No programs in this category.")

    with tab_n:
        if not_eligible:
            st.error(f"You do not currently qualify for **{len(not_eligible)} programs**.")
            for s in not_eligible:
                display_result_card(s)
        else:
            st.info("No programs ruled you out.")


# ── Session State ────────────────────────────────────────────────────────────
if "section" not in st.session_state:
    st.session_state.section = "form"

# ── Section Toggle ───────────────────────────────────────────────────────────
col1, col2, _ = st.columns([1, 1, 4])
with col1:
    if st.button("Fill Form", type="primary" if st.session_state.section == "form" else "secondary", key="btn_form", use_container_width=True):
        st.session_state.section = "form"
with col2:
    if st.button("Describe Situation", type="primary" if st.session_state.section == "voice" else "secondary", key="btn_voice", use_container_width=True):
        st.session_state.section = "voice"

st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)

# ── FORM SECTION ─────────────────────────────────────────────────────────────
if st.session_state.section == "form":
    st.markdown(
        '<div class="panel-title">Eligibility Assessment</div>'
        '<div class="panel-subtitle">Provide your details below. The more information you share, the more accurate your results.</div>',
        unsafe_allow_html=True
    )

    with st.form("eligibility_form"):
        # Location
        st.markdown('<p class="section-label">Location</p>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            state = st.selectbox("State *", [""] + US_STATES, index=0)
        with col2:
            county = st.text_input("County", placeholder="e.g., Harris County")
        with col3:
            city = st.text_input("City", placeholder="e.g., Houston")

        # Household
        st.markdown('<p class="section-label">Household & Income</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            household_size = st.number_input("Household Size *", min_value=1, max_value=15, value=1)
        with col2:
            income = st.number_input("Annual Household Income ($) *", min_value=0, max_value=500000, value=0, step=1000)

        # Family
        st.markdown('<p class="section-label">Family Situation</p>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            is_pregnant = st.checkbox("Pregnant")
        with col2:
            is_breastfeeding = st.checkbox("Breastfeeding")
        with col3:
            has_children = st.checkbox("Have children under 18")
        with col4:
            is_single_parent = st.checkbox("Single parent")

        children_ages = ""
        if has_children:
            children_ages = st.text_input("Children's ages (comma-separated)", placeholder="e.g., 3, 7, 12")

        # Employment
        st.markdown('<p class="section-label">Employment</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            is_employed = st.checkbox("Currently employed")
        with col2:
            employment_type = st.selectbox("Employment type", ["Not employed", "full-time", "part-time", "self-employed", "seasonal"])

        # Special
        st.markdown('<p class="section-label">Special Circumstances</p>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            is_veteran = st.checkbox("Veteran")
        with col2:
            is_disabled = st.checkbox("Disabled")
        with col3:
            is_student = st.checkbox("Student")
        with col4:
            is_homeless = st.checkbox("Homeless / housing insecure")

        col1, col2 = st.columns(2)
        with col1:
            is_dv_survivor = st.checkbox("Domestic violence survivor")
        with col2:
            housing_situation = st.selectbox("Housing situation", ["", "renter", "owner", "homeless", "shelter", "living with family"])

        submitted = st.form_submit_button("Check Eligibility", type="primary", use_container_width=True)

        if submitted:
            if not state:
                st.error("Please select your state to continue.")
            else:
                form_data = {
                    "state": state,
                    "county": county or None,
                    "city": city or None,
                    "household_size": household_size,
                    "income": income,
                    "is_pregnant": is_pregnant,
                    "is_breastfeeding": is_breastfeeding,
                    "has_children": has_children,
                    "children_ages": children_ages,
                    "is_single_parent": is_single_parent,
                    "is_employed": is_employed,
                    "employment_type": employment_type if is_employed and employment_type != "Not employed" else "unemployed",
                    "is_veteran": is_veteran,
                    "is_disabled": is_disabled,
                    "is_student": is_student,
                    "is_homeless": is_homeless,
                    "is_domestic_violence_survivor": is_dv_survivor,
                    "housing_situation": housing_situation or None,
                }

                with st.spinner("Analyzing eligibility across federal, state, and local programs..."):
                    t0 = time.time()
                    result = run_eligibility_check(form_data=form_data)
                    elapsed = time.time() - t0

                if result.get("parse_error"):
                    st.error(result["parse_error"])
                else:
                    n = len(result.get("eligible_schemes", []))
                    st.success(f"Analysis complete in {elapsed:.1f}s — found **{n} programs** you likely qualify for.")
                    display_results(result)

# ── VOICE SECTION ────────────────────────────────────────────────────────────
elif st.session_state.section == "voice":
    st.markdown(
        '<div class="panel-title">Describe Your Situation</div>'
        '<div class="panel-subtitle">Click the microphone and speak naturally, or type your description. Include your state, income, and family details.</div>',
        unsafe_allow_html=True
    )

    # ── Speech-to-Text Widget (Web Speech API) ───────────────────────────
    speech_html = """
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        .voice-wrap {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 24px;
            margin: 0;
        }
        .mic-row {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 16px;
        }
        .mic-btn {
            width: 62px; height: 62px;
            border-radius: 50%;
            border: none;
            background: linear-gradient(135deg, #1e40af, #047857);
            cursor: pointer;
            font-size: 26px;
            display: flex; align-items: center; justify-content: center;
            transition: all 0.25s;
            box-shadow: 0 4px 16px rgba(30,64,175,0.35);
            color: white;
        }
        .mic-btn:hover { transform: scale(1.05); }
        .mic-btn.recording {
            background: linear-gradient(135deg, #dc2626, #ea580c);
            animation: pulse 1.4s ease-in-out infinite;
            box-shadow: 0 4px 20px rgba(220,38,38,0.4);
        }
        @keyframes pulse {
            0%,100% { transform: scale(1); }
            50% { transform: scale(1.07); }
        }
        .status { font-size: 14px; color: #94a3b8; }
        .status.rec { color: #ef4444; font-weight: 600; }
        .transcript-box {
            width: 100%;
            min-height: 80px;
            background: rgba(15,23,42,0.6);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 14px;
            font-size: 14.5px;
            line-height: 1.6;
            color: #cbd5e1;
            resize: vertical;
            font-family: inherit;
        }
        .transcript-box:focus { outline: none; border-color: #3b82f6; }
        .hint { margin-top: 10px; font-size: 12.5px; color: #64748b; }
        .error-msg { color: #ef4444; font-size: 13px; margin-top: 8px; display: none; }
        .browser-warn {
            background: rgba(250,204,21,0.08);
            border: 1px solid rgba(250,204,21,0.2);
            border-radius: 8px;
            padding: 12px;
            font-size: 13px;
            color: #fbbf24;
            margin-bottom: 14px;
        }
        .copy-btn {
            margin-top: 14px;
            padding: 10px 24px;
            border: none;
            border-radius: 8px;
            background: #ea580c;
            color: white;
            font-size: 13.5px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .copy-btn:hover { background: #c2410c; }
        .copy-btn:disabled { opacity: 0.4; cursor: not-allowed; }
    </style>

    <div class="voice-wrap">
        <div id="browserWarn"></div>
        <div class="mic-row">
            <button class="mic-btn" id="micBtn" onclick="toggleRec()">&#x1F3A4;</button>
            <span class="status" id="status">Click the microphone and start speaking</span>
        </div>
        <textarea class="transcript-box" id="transcript"
            placeholder="Your speech will appear here. You can also type or edit directly."></textarea>
        <div class="hint" id="hint">
            Example: "I am a single mother in Texas with two children ages 3 and 7, making $24,000 a year working part-time."
        </div>
        <div class="error-msg" id="errMsg"></div>
        <button class="copy-btn" id="copyBtn" onclick="copyText()" disabled>
            Copy text to clipboard, then paste below
        </button>
    </div>

    <script>
        let recog = null, isRec = false, final_t = '', interim_t = '';
        const bw = document.getElementById('browserWarn');

        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            bw.innerHTML = '<div class="browser-warn">Speech recognition is not supported in this browser. Use Google Chrome, Microsoft Edge, or Safari for voice input. You can type your description in the box below.</div>';
            document.getElementById('micBtn').disabled = true;
            document.getElementById('micBtn').style.opacity = '0.3';
            document.getElementById('micBtn').style.cursor = 'not-allowed';
        } else {
            const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
            recog = new SR();
            recog.continuous = true;
            recog.interimResults = true;
            recog.lang = 'en-US';

            recog.onresult = (e) => {
                interim_t = '';
                for (let i = e.resultIndex; i < e.results.length; i++) {
                    if (e.results[i].isFinal) final_t += e.results[i][0].transcript + ' ';
                    else interim_t += e.results[i][0].transcript;
                }
                updateBox();
            };

            recog.onerror = (e) => {
                const em = document.getElementById('errMsg');
                const msgs = {
                    'no-speech': 'No speech detected. Please try again.',
                    'audio-capture': 'No microphone found. Check your microphone settings.',
                    'not-allowed': 'Microphone access denied. Allow microphone access in your browser settings.'
                };
                em.textContent = msgs[e.error] || ('Error: ' + e.error);
                em.style.display = 'block';
                stopRec();
            };

            recog.onend = () => { if (isRec) { try { recog.start(); } catch(x){} } };
        }

        function updateBox() {
            const box = document.getElementById('transcript');
            const full = final_t + interim_t;
            if (full.trim()) {
                box.value = full;
                document.getElementById('copyBtn').disabled = false;
            }
        }

        function toggleRec() { if (!recog) return; isRec ? stopRec() : startRec(); }

        function startRec() {
            final_t = ''; interim_t = '';
            document.getElementById('errMsg').style.display = 'none';
            document.getElementById('transcript').value = '';
            document.getElementById('copyBtn').disabled = true;
            try {
                recog.start();
                isRec = true;
                document.getElementById('micBtn').classList.add('recording');
                document.getElementById('micBtn').innerHTML = '&#x23F9;';
                document.getElementById('status').textContent = 'Listening... Click to stop';
                document.getElementById('status').classList.add('rec');
                document.getElementById('hint').textContent = 'Speak naturally. Mention your state, income, family situation, and any special circumstances.';
            } catch(x) {}
        }

        function stopRec() {
            isRec = false;
            try { recog.stop(); } catch(x) {}
            document.getElementById('micBtn').classList.remove('recording');
            document.getElementById('micBtn').innerHTML = '&#x1F3A4;';
            document.getElementById('status').textContent = 'Done. Review your text below, then copy and paste it into the input box.';
            document.getElementById('status').classList.remove('rec');
        }

        function copyText() {
            const box = document.getElementById('transcript');
            const text = box.value.trim();
            if (text) {
                navigator.clipboard.writeText(text).then(() => {
                    document.getElementById('copyBtn').textContent = 'Copied — paste in the box below';
                    setTimeout(() => {
                        document.getElementById('copyBtn').textContent = 'Copy text to clipboard, then paste below';
                    }, 3000);
                }).catch(() => { box.select(); document.execCommand('copy'); });
            }
        }
    </script>
    """
    components.html(speech_html, height=370)

    st.markdown("---")
    st.markdown('<p class="voice-instruction">Paste your transcribed text here, or type directly:</p>', unsafe_allow_html=True)

    if "voice_transcript" not in st.session_state:
        st.session_state.voice_transcript = ""

    transcript = st.text_area(
        "Situation description",
        value=st.session_state.voice_transcript,
        height=110,
        placeholder="Paste your speech here, or type your situation directly...",
        key="voice_text_area",
        label_visibility="collapsed"
    )

    if transcript:
        if st.button("Check Eligibility", type="primary", key="voice_submit", use_container_width=True):
            with st.spinner("Understanding your situation and checking programs..."):
                t0 = time.time()
                result = run_eligibility_check(voice_transcript=transcript)
                elapsed = time.time() - t0

            if result.get("parse_error"):
                st.error(result["parse_error"])
                st.info("Make sure to include your state, income, and family situation.")
            else:
                n = len(result.get("eligible_schemes", []))
                st.success(f"Analysis complete in {elapsed:.1f}s — found **{n} programs** you likely qualify for.")
                display_results(result)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">'
    'BenefitsBridge &mdash; Government Scheme Discovery Platform'
    '&nbsp;&nbsp;|&nbsp;&nbsp;<a href="/admin">Admin Portal</a>'
    '</div>',
    unsafe_allow_html=True
)
