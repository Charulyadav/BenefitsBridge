# BenefitsBridge

**Team 5** —SheHack Hackathon Submission


## Team Members

* **Charul**
* **Sanika Sanjay Girase**
* **Sharvari Kulkarni**



## Inspiration

Millions of American women's miss out on government benefits unclaimed every year — not because they don't qualify, but because they don't know these programs exist. The application process is fragmented across dozens of federal, state, and county websites, each with its own eligibility rules, income thresholds, and paperwork requirements. A single mother in Texas working part-time might qualify for 15+ programs simultaneously (SNAP, Medicaid, CHIP, WIC, TANF, childcare subsidies, EITC, and more) but would need to visit a different website for each one, decode the eligibility criteria herself, and figure out what documents to gather.

We built BenefitsBridge to solve this. One form, one answer: every program you qualify for, why you qualify, what documents you need, and who to call for help.


## What It Does

BenefitsBridge is a web application that matches women's to government benefit programs based on their personal profile. Users can either fill out a structured form or describe their situation in natural language (including voice input via the browser's Web Speech API), and the system instantly checks eligibility across all applicable federal, state, and county programs.

For each matching program, the output includes:

* **Why you qualify** — a personalized explanation based on your income, household size, and circumstances
* **Benefit details** — what you receive, how much, and how long processing takes
* **Next steps** — a numbered action plan to apply
* **Documents needed** — the exact paperwork to gather before applying
* **Customer care information** — phone numbers, hours of operation, websites, and tips for reaching the right office

The system also includes a Government Admin Portal where agency administrators can add, edit, activate, or deactivate benefit schemes for their jurisdiction.


## Impact of the Solution

BenefitsBridge addresses the benefits gap from multiple angles:

**For women's**, it eliminates the research burden. Instead of navigating dozens of government websites and decoding eligibility tables, a user completes one form and receives a comprehensive, personalized report in seconds. The voice input option makes it accessible to people who may find forms intimidating or have limited literacy.

**For government agencies**, it increases program utilization. Benefits that go unclaimed represent wasted budget allocations and unserved populations. By surfacing all eligible programs at once, BenefitsBridge helps agencies reach the people their programs were designed to help.

**For caseworkers and community organizations**, it serves as a screening tool. A social worker can quickly assess a client's eligibility across all programs during a single intake session, rather than checking each program individually.

The system currently covers 45 programs across federal and five state jurisdictions (Texas, California, New York, Massachusetts, and Florida), with a database structure that supports unlimited expansion to all 50 states and county-level programs.


## Tech Stack

|Layer|Technology|
|-|-|
|Frontend|Streamlit (Python web framework)|
|Eligibility Engine|Pure Python rule-based engine using AI multiagent|
|NLU / Voice Input|Web Speech API (browser-native), keyword extraction parser|
|Data Storage|JSON file-based scheme database|
|Backend|LangGraph, Ollama, llama3 LLM Model, AI multiagent|
|Styling|Custom CSS (dark government-themed UI)|
|Language|Python 3.12|

**Key dependencies:**

* `streamlit` — web application framework
* `pydantic` — data validation

**Architecture:**

The application uses a pipeline architecture with three stages:

1. **Intake / NLU Parser** — Accepts structured form data or natural language input and produces a standardized user profile (state, income, household size, family situation, special circumstances).
2. **Eligibility Engine** — Checks the user profile against every applicable scheme using Federal Poverty Level calculations, categorical eligibility rules, and program-specific logic (WIC pregnancy requirements, EITC employment requirements, veteran status checks, etc.).
3. **Result Renderer** — Organizes results into eligible, maybe-eligible, and not-eligible categories, enriches each result with application steps, required documents, and customer care information, and renders everything in the UI.

## Challenges Faced

**Eligibility rule complexity.** Government benefit programs have overlapping, sometimes contradictory eligibility criteria. For example, WIC has categorical requirements (pregnancy, breastfeeding, or child under 5) layered on top of income requirements, while the EITC requires earned income but has no upper FPL limit for all situations. Encoding these rules correctly required careful study of each program's actual eligibility criteria.

**Dark-themed UI with Streamlit.** Streamlit's default components (selectboxes, checkboxes, number inputs) are designed for light backgrounds. Making text visible on a dark government-style theme required extensive CSS overrides targeting every Streamlit widget variant — including inputs with white backgrounds where the text color needed to be dark, while labels above them needed to stay light.

**Speech-to-text integration.** Streamlit's `components.html()` runs inside an iframe that cannot directly push values back into Python session state. We implemented a copy-to-clipboard bridge pattern where the speech transcript is captured in the iframe, copied by the user, and pasted into a native Streamlit text area for processing.

**Form reactivity limitations.** Streamlit forms do not support reactive widget updates — checking a checkbox inside a form cannot dynamically enable or disable another widget until the form is submitted. We restructured the employment section to work around this constraint.


## Future Scope

* **All 50 states** — Expand the scheme database with state-specific programs for every US state and territory
* **County and city programs** — Add local-level benefits (housing authorities, community action agencies, school district programs)
* **Multi-language support** — Spanish, Chinese, Vietnamese, and other languages commonly spoken by benefits-eligible populations
* **Document upload and pre-fill** — Allow users to upload tax returns or pay stubs to auto-populate income fields and generate pre-filled application forms
* **Real-time application status tracking** — Integration with state benefits portals to track application progress
* **LLM-powered conversational assistant** — Reintroduce a language model (with the rule-based engine as the ground truth) to provide conversational guidance through the application process
* **Mobile-first redesign** — Optimized layout for smartphone users, who represent a large share of the target population
* **API for partner organizations** — REST API so hospitals, schools, food banks, and social service agencies can embed eligibility screening into their own intake workflows
* **Analytics dashboard for government** — Real-time data on which programs are being searched, eligibility match rates, and geographic demand patterns to help agencies allocate outreach resources


## AI Tool Disclosure

The following AI tools were used during the development of this project:
**Claude (Anthropic)** — Used for code debugging and solving issues in code integration.

**Ollama / Llama 3.2** — The project architecture used Ollama as a local LLM for natural language understanding (parsing voice input) and eligibility assessment (multi-agent LangGraph pipeline).

## How to Run

```bash
# 1. Clone the project
cd benefitsbridge

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
streamlit run app.py

# 4. Access the admin portal (separate page)
# Navigate to /admin in the browser
# Demo credentials: Select jurisdiction, enter any email,
# use the jurisdiction password (e.g., "texas\_admin\_2024" for TX)
```

**Requirements:** Python 3.10+, a modern web browser (Chrome/Edge/Safari recommended for voice input).


## Project Structure

```
benefitsbridge/
├── app.py                  # Main citizen portal (Streamlit UI)
├── graph.py                # Eligibility pipeline (rule-based engine)
├── config.py               # Configuration, FPL tables, admin passwords
├── state.py                # Type definitions for the pipeline state
├── requirements.txt        # Python dependencies
├── data/
│   └── schemes.json        # Benefit programs database (45 schemes)
├── utils/
│   ├── db.py               # Database helpers (load, save, filter schemes)
│   └── eligibility.py      # Core eligibility calculation functions
├── pages/
│   └── admin.py            # Government admin portal
├── models/
│   └── scheme.py           # Scheme data model
├── nodes/                  # Original LangGraph agent nodes (reference)
│   ├── intake.py
│   ├── nlu\_parser.py
│   ├── benefits\_agent.py
│   ├── healthcare\_agent.py
│   ├── education\_agent.py
│   └── aggregator.py
└── components/
    └── voice\_input.py      # Web Speech API component
```
Video Demo Link: 
https://northeastern-my.sharepoint.com/:v:/g/personal/lnu_char_northeastern_edu/IQCel5zpLwSZR7mnQWPdf9RZAcptdpbM_8N9o6-bcGPlR2k?e=H2BgXD

https://drive.google.com/file/d/1KLuf2V-fqj5mdvuA2rmhoPfvVvdf5X2j/view?usp=sharing

Presentation Link:
https://northeastern-my.sharepoint.com/:p:/g/personal/kulkarni_sharvar_northeastern_edu/IQBKapjAAUSrTZnoaw_D6sduAWtC5S6_xkDfEGaqMJCh0Qs?e=4UWR2N
