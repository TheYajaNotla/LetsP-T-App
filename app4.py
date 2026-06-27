import base64
import hashlib
import json
import os
import time
from datetime import date, datetime

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="PRVNT | Health Onboarding",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

LOGO_PATH = "Copy of PRVNT Logo.jpg"

YES_NO = ["No", "Yes"]
YES_NO_UNSURE = ["No", "Yes", "Unsure"]
FREQ = ["Never", "Occasionally", "Often", "Almost always"]


SECTIONS = [
    {
        "title": "Profile",
        "summary": "Core identity, contact details and basic body metrics.",
        "questions": [
            ("fullname", "Full name", "text", {"required": True}),
            ("preferred_name", "Preferred name", "text", {}),
            ("dob", "Date of birth", "date", {"default": date(1990, 1, 1), "required": True}),
            ("age", "Age", "number", {"min": 0, "max": 120, "default": 35}),
            ("sex", "Sex", "select", {"options": ["Female", "Male", "Intersex", "Prefer not to answer"]}),
            ("height", "Height", "text", {"placeholder": "cm or ft/in"}),
            ("weight_curr", "Current weight", "text", {"placeholder": "kg or lb"}),
            ("language", "Preferred language", "text", {"default": "English"}),
            ("mobile", "Mobile number", "text", {"required": True}),
            ("email", "Email address", "text", {"required": True}),
        ],
    },
    {
        "title": "Life Context",
        "summary": "Daily context that shapes health, access, support and follow-through.",
        "questions": [
            ("occupation", "Current occupation or primary daily role", "text", {}),
            ("work_type", "Which best describes your work?", "select", {"options": ["Mostly sitting", "Mostly standing", "Physically active", "Mixed", "Student", "Retired", "Homemaker", "Other"]}),
            ("work_exposure", "Work exposures", "multi", {"options": ["Shift work", "Night work", "Frequent travel", "Heavy lifting", "High stress", "Chemical exposure", "Dust exposure", "Loud noise", "Radiation", "None"]}),
            ("marital_status", "Current marital status", "select", {"options": ["Single", "Married", "Living with partner", "Divorced / Separated", "Widowed", "Prefer not to say"]}),
            ("living_arrangements", "Who do you currently live with?", "select", {"options": ["Alone", "Spouse or partner", "Children", "Parents", "Extended family", "Friends or housemates", "Other"]}),
            ("dependents", "Do you have children or dependents?", "radio", {"options": YES_NO}),
            ("social_support_tier", "How would you describe your social support?", "select", {"options": ["Excellent", "Good", "Adequate", "Limited", "Very limited"]}),
        ],
    },
    {
        "title": "Care Team",
        "summary": "Current providers, care coordination and record sharing preferences.",
        "questions": [
            ("regular_provider", "Regular doctor or primary healthcare provider", "text", {}),
            ("active_care_team", "Healthcare professionals currently involved in your care", "multi", {"options": ["Family physician", "Cardiologist", "Endocrinologist", "Gastroenterologist", "Neurologist", "Psychiatrist", "Psychologist", "Dietitian", "Physiotherapist", "Dentist", "Ophthalmologist", "Other"]}),
            ("care_coordinator", "Who usually coordinates your healthcare?", "select", {"options": ["Family physician", "Specialist", "I coordinate it myself", "Family member", "Other"]}),
            ("share_records_consent", "Willing to share historical laboratory or medical records with PRVNT?", "radio", {"options": ["Yes", "No", "Some records only"]}),
        ],
    },
    {
        "title": "Goals",
        "summary": "What brought you here and what a meaningful outcome looks like.",
        "questions": [
            ("prompt_join_prvnt", "What prompted you to join PRVNT?", "multi", {"options": ["General health assessment", "Disease prevention", "Family history of disease", "Weight management", "Improve energy", "Better sleep", "Improve physical fitness", "Better nutrition", "Healthy ageing", "Manage an existing condition", "Unexplained symptoms", "Care coordination", "Second opinion", "Recent abnormal test results", "Other"]}),
            ("top_12mo_improvement", "Health concern you would most like to improve over the next 12 months", "area", {}),
            ("good_health_definition", "What does good health look like for you?", "area", {}),
            ("overall_health_rate", "How would you rate your overall health today?", "slider_select", {"options": ["Poor", "Fair", "Good", "Very good", "Excellent"]}),
            ("three_health_goals", "Three most important health goals over the next 12 months", "area", {}),
            ("readiness_to_change", "Readiness to make changes", "select", {"options": ["Not ready at present", "Thinking about making changes", "Ready within the next month", "Ready now"]}),
            ("desired_support_areas", "Areas you would most like support with", "multi", {"options": ["Nutrition", "Exercise", "Sleep", "Stress management", "Weight management", "Medication review", "Preventive screening", "Mental wellbeing", "Healthy ageing", "Smoking cessation", "Alcohol reduction", "Other"]}),
        ],
    },
    {
        "title": "Medical History",
        "summary": "Past and current diagnoses, hospital use and unresolved patterns.",
        "questions": [
            ("conditions", "Past or current diagnoses", "multi", {"options": ["High blood pressure", "Prediabetes", "Type 2 diabetes", "High cholesterol", "Coronary artery disease", "Heart attack history", "Stroke / TIA", "Sleep apnoea", "Asthma", "COPD", "Chronic kidney disease", "Fatty liver disease", "GERD", "IBS", "Thyroid disease", "Autoimmune disease", "Osteoporosis", "Cancer history", "Depression", "Anxiety", "Migraine", "Chronic pain", "Other"]}),
            ("current_active_conditions", "Which conditions are currently active or requiring follow-up?", "area", {}),
            ("er_visits_12m", "Emergency room or urgent care visits in past 12 months", "select", {"options": ["None", "Once", "Twice", "Three or more times"]}),
            ("hospital_admissions_12m", "Admitted to hospital in the past 12 months?", "radio", {"options": YES_NO}),
            ("hospital_admissions_details", "If admitted, describe reason, dates, and outcome", "area", {}),
        ],
    },
    {
        "title": "Medicines",
        "summary": "Medications, supplements, allergies and safety signals.",
        "questions": [
            ("takes_rx", "Are you currently taking prescription medications?", "radio", {"options": YES_NO}),
            ("rx_details", "Prescription medications with doses and frequencies", "area", {}),
            ("takes_otc", "Do you regularly take over-the-counter medicines?", "radio", {"options": YES_NO}),
            ("otc_details", "Over-the-counter products", "area", {}),
            ("takes_supplements", "Do you take vitamins, minerals, or supplements?", "radio", {"options": YES_NO}),
            ("supplement_details", "Supplements and dosages", "area", {}),
            ("med_allergies", "Known medication allergies", "area", {}),
            ("food_allergies", "Food allergies or intolerances", "multi", {"options": ["None known", "Milk / Dairy", "Egg", "Wheat / Gluten", "Soy", "Peanut", "Tree nuts", "Fish", "Shellfish", "Sesame", "Other"]}),
            ("anaphylaxis_history", "Ever had a severe allergic reaction or anaphylaxis?", "radio", {"options": YES_NO}),
        ],
    },
    {
        "title": "Family & Procedures",
        "summary": "Surgical history, anesthesia issues and inherited risk.",
        "questions": [
            ("surgery_history", "Past surgeries or invasive procedures", "area", {}),
            ("anaesthesia_complications", "Complications or side effects from anesthesia", "area", {}),
            ("family_history", "Family history", "multi", {"options": ["High blood pressure", "High cholesterol", "Type 2 diabetes", "Early heart attack", "Stroke", "Blood clots", "Cancer", "Dementia", "Parkinson's disease", "Osteoporosis", "Autoimmune disease", "Kidney disease", "Mental health condition"]}),
            ("family_history_details", "Family history details, including relation and age at diagnosis", "area", {}),
        ],
    },
    {
        "title": "Symptoms",
        "summary": "A focused review of symptoms across body systems.",
        "questions": [
            ("sym_fever", "Recurrent fevers, dynamic temperature shifts, or nocturnal night sweats?", "slider_select", {"options": FREQ}),
            ("sym_weight_change", "Unintentional, rapid modifications to body weight parameters?", "slider_select", {"options": FREQ}),
            ("sym_fatigue", "Persistent exhaustion that disrupts normal cognitive or physical focus?", "slider_select", {"options": FREQ}),
            ("sym_rash", "Recurring skin rashes, unexpected dermal changes, or barrier shifts?", "slider_select", {"options": FREQ}),
            ("sym_bruising", "Tendency to bruise easily or develop unprovoked hematomas?", "slider_select", {"options": FREQ}),
            ("sym_hair_loss", "Accelerated hair loss or sudden thinning?", "slider_select", {"options": FREQ}),
            ("sym_headache", "Frequent localized headaches, dynamic tension bands, or visual migraines?", "slider_select", {"options": FREQ}),
            ("sym_dizziness", "Vertigo, unsteadiness, or orthostatic fainting sensations?", "slider_select", {"options": FREQ}),
            ("sym_vision", "Unexplained or sudden adjustments to visual clarity?", "slider_select", {"options": FREQ}),
            ("sym_chest_pain", "Cardiovascular pressure, restrictive chest pain, or radiating tightness?", "slider_select", {"options": FREQ}),
            ("sym_palpitations", "Premature atrial fluttering, skipped beats, or rapid unprovoked racing?", "slider_select", {"options": FREQ}),
            ("sym_breathlessness", "Shortness of breath (dyspnoea) at rest or under minor physical workloads?", "slider_select", {"options": FREQ}),
            ("sym_reflux", "Gastrointestinal reflux, frequent pyrosis, or acid indigestion?", "slider_select", {"options": FREQ}),
            ("sym_abdominal_pain", "Unspecified abdominal pain, bloating, or visceral layout cramping?", "slider_select", {"options": FREQ}),
            ("sym_bowel_change", "Recent or persistent changes to regular bowel habit outputs?", "slider_select", {"options": FREQ}),
            ("sym_joint_pain", "Articular joint pain, early morning stiffness, or structural fluid swelling?", "slider_select", {"options": FREQ}),
            ("sym_numbness", "Peripheral neuropathy, unexpected tingling, or focal motor weakness tracks?", "slider_select", {"options": FREQ}),
            ("sym_cold_intolerance", "Abnormal physical sensitivity or low tolerance to cool environments?", "slider_select", {"options": FREQ}),
            ("sym_thirst", "Persistent unprovoked thirst (polydipsia indicators)?", "slider_select", {"options": FREQ}),
            ("sym_anxiety", "Persistent psychological anxiety, hyperarousal, or difficulty relaxing?", "slider_select", {"options": FREQ}),
            ("sym_sadness", "Prolonged flat affect, feelings of low mood, or diminished motivation?", "slider_select", {"options": FREQ}),
            ("sym_other_details", "Clarify any alternative physical anomalies or trends our clinical team should look into:", "area", {}),
        ],
        
    },
    {
        "title": "Lifestyle",
        "summary": "Nutrition, movement, sleep, stress, substances, and environment.",
        "questions": [
            ("diet_pattern", "Usual eating pattern", "select", {"options": ["Omnivore", "Mediterranean-style", "Vegetarian", "Vegan", "Pescatarian", "Low-carbohydrate", "Ketogenic", "Intermittent fasting", "Other"]}),
            ("veg_servings_day", "Vegetable servings consumed daily", "select", {"options": ["None", "1-2", "3-4", "5 or more"]}),
            ("water_intake", "Approximate water intake per day", "select", {"options": ["Less than 1 litre", "1-2 litres", "2-3 litres", "More than 3 litres", "Unsure"]}),
            ("exercise_sessions_week", "Physical activity sessions per week", "slider", {"min": 0, "max": 14, "default": 3}),
            ("avg_daily_steps", "Average daily step count, if known", "number", {"min": 0, "max": 100000, "default": 0}),
            ("sleep_hours_night", "Average sleep duration per night", "slider_float", {"min": 3.0, "max": 12.0, "default": 7.0, "step": 0.5}),
            ("sleep_quality", "Overall sleep quality", "select", {"options": ["Poor", "Fair", "Good", "Very good", "Excellent"]}),
            ("stress_level", "Current stress level", "select", {"options": ["Low", "Moderate", "High", "Very high"]}),
            ("tobacco_use", "Tobacco smoking or vaping status", "select", {"options": ["Never smoked", "Ex-smoker", "Current user"]}),
            ("alcohol_servings_week", "Standard units or servings of alcohol consumed weekly", "number", {"min": 0, "max": 100, "default": 0}),
        ],
    },
    {
        "title": "Preventive Care",
        "summary": "Screenings, vaccines, dental, vision, and proactive priorities.",
        "questions": [
            ("bp_recent", "Do you know your recent blood pressure?", "text", {"placeholder": "Example: 120/80, unknown"}),
            ("labs_recent", "Have you had blood tests in the past 12 months?", "radio", {"options": YES_NO_UNSURE}),
            ("cholesterol_checked", "Cholesterol checked in the past 5 years?", "radio", {"options": YES_NO_UNSURE}),
            ("diabetes_screening", "Blood sugar or HbA1c checked in the past 3 years?", "radio", {"options": YES_NO_UNSURE}),
            ("cancer_screening_status", "Cancer screenings completed or due", "multi", {"options": ["Cervical screening", "Breast screening", "Colon screening", "Prostate screening", "Skin check", "Lung screening", "Not sure", "Not applicable"]}),
            ("vaccination_status", "Vaccinations you believe are up to date", "multi", {"options": ["Influenza", "COVID-19", "Tetanus", "Hepatitis B", "HPV", "Shingles", "Pneumococcal", "Travel vaccines", "Not sure"]}),
            ("preventive_support_targets", "Preventive reporting support areas", "multi", {"options": ["Weight management", "Cardiovascular disease prevention", "Diabetes prevention", "Cancer screening", "Vaccinations", "Healthy ageing", "Bone health", "Brain health", "Smoking cessation", "Physical activity", "Nutrition", "Mental wellbeing", "Sleep", "Women's health", "Men's health", "Unsure"]}),
            ("wants_to_prevent_top3", "What would you most like to proactively prevent? Select up to three.", "multi", {"options": ["Heart disease", "Stroke", "Diabetes", "Cancer", "Osteoporosis or fractures", "Memory decline or dementia", "Loss of mobility", "Vision loss", "Chronic pain", "Frailty", "Other"], "max_selections": 3}),
            ("additional_context", "Anything else you want your PRVNT care team to understand?", "area", {}),
        ],
    },
]


def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    :root {
        --ink:#111314;
        --deep:#0e2a36;
        --harbor:#1f4e63;
        --mist:#90b7c6;
        --paper:#f7f7f4;
        --line:#dfe7e7;
        --muted:#5c6669;
    }

    .stApp {
        background:var(--paper);
        color:var(--ink);
        font-family:"Plus Jakarta Sans","Segoe UI",Arial,sans-serif;
    }

    h1,h2,h3,h4 {
        font-family:"Space Grotesk","Segoe UI",Arial,sans-serif !important;
        letter-spacing:0 !important;
    }

    p,label,span,div,button,input,textarea {
        font-family:"Plus Jakarta Sans","Segoe UI",Arial,sans-serif !important;
    }

    .block-container {
        padding-top:28px;
        padding-bottom:46px;
        max-width:1280px;
    }

    div[data-baseweb="tab-list"] {
        gap:14px !important;
        row-gap:14px !important;
        flex-wrap:wrap;
        margin-top:18px;
        margin-bottom:24px;
        border-bottom:none !important;
    }

    button[data-baseweb="tab"] {
        padding:10px 18px !important;
        margin-right:0 !important;
        border:1px solid var(--line) !important;
        background:#fff !important;
        border-radius:4px !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        border-color:var(--deep) !important;
        background:#f9fbfb !important;
    }

    button[data-baseweb="tab"] p {
        font-weight:700 !important;
        color:var(--deep) !important;
    }

    .metric-row {
        display:grid;
        grid-template-columns:repeat(4,minmax(0,1fr));
        gap:1px;
        border:1px solid var(--line);
        background:var(--line);
        margin:16px 0 28px;
    }

    .metric {
        background:white;
        padding:17px 19px;
    }

    .metric strong {
        display:block;
        font-family:"Space Grotesk","Segoe UI",Arial,sans-serif !important;
        font-size:1.35rem;
        color:var(--deep);
    }

    .metric span {
        color:#5d686b;
        font-size:.82rem;
    }

    .section-intro {
        border-top:1px solid var(--line);
        padding:24px 0 8px;
        margin-top:6px;
    }

    .section-intro small {
        color:var(--harbor);
        font-weight:800;
        text-transform:uppercase;
        letter-spacing:.08em;
    }

    .section-intro p {
        color:var(--muted);
        max-width:760px;
    }

    .security-note {
        padding:16px 18px;
        border:1px solid var(--line);
        background:#fbfcfc;
        color:#354043;
        line-height:1.55;
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius:3px;
        border:1px solid var(--deep);
        background:var(--deep);
        color:white;
        min-height:44px;
        font-weight:750;
    }

    div[data-testid="stProgress"] > div > div {
        background-color:var(--harbor);
    }

    @media (max-width:760px) {
        .metric-row { grid-template-columns:repeat(2,minmax(0,1fr)); }
        button[data-baseweb="tab"] { padding:9px 13px !important; }
    }
    </style>
    """, unsafe_allow_html=True)


def ensure_state():
    if "started_at" not in st.session_state:
        st.session_state.started_at = time.time()
    if "form_data" not in st.session_state:
        st.session_state.form_data = {}


def show_header():
    left, right = st.columns([1, 4])

    with left:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=120)
        else:
            st.markdown("### PRVNT")

    with right:
        st.caption("Comprehensive Health Questionnaire")
        st.title("Your health intake, thoughtfully organized.")
        st.write(
            "Share your background, goals, symptoms, lifestyle signals, and prevention priorities "
            "so your PRVNT care team can begin with clarity."
        )


def question_keys():
    return [q[0] for section in SECTIONS for q in section["questions"]]


def clean_value(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def collect_payload():
    data = {key: clean_value(st.session_state.form_data.get(key)) for key in question_keys()}
    data["meta_elapsed_seconds"] = int(time.time() - st.session_state.started_at)
    data["meta_submission_timestamp"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    data["meta_schema_version"] = "prvnt-comprehensive-intake-v4"
    return data


def completion_stats():
    data = collect_payload()
    answered = sum(1 for key in question_keys() if data.get(key) not in (None, "", [], {}))
    required_missing = 0

    for section in SECTIONS:
        for key, label, qtype, cfg in section["questions"]:
            if cfg.get("required") and data.get(key) in (None, "", [], {}):
                required_missing += 1

    return answered, len(question_keys()), required_missing


def render_question(key, label, qtype, cfg):
    value = st.session_state.form_data.get(key)

    if qtype == "text":
        result = st.text_input(label, value=value or cfg.get("default", ""), placeholder=cfg.get("placeholder", ""))
    elif qtype == "area":
        result = st.text_area(label, value=value or "", height=118)
    elif qtype == "number":
        result = st.number_input(label, min_value=cfg.get("min"), max_value=cfg.get("max"), value=value if value is not None else cfg.get("default", 0))
    elif qtype == "date":
        result = st.date_input(label, value=value or cfg.get("default", date.today()))
    elif qtype == "select":
        options = cfg["options"]
        result = st.selectbox(label, options, index=options.index(value) if value in options else 0)
    elif qtype == "radio":
        options = cfg["options"]
        result = st.radio(label, options, index=options.index(value) if value in options else 0, horizontal=True)
    elif qtype == "multi":
        result = st.multiselect(label, cfg["options"], default=value or [], max_selections=cfg.get("max_selections"))
    elif qtype == "slider_select":
        options = cfg["options"]
        result = st.select_slider(label, options=options, value=value or options[0])
    elif qtype == "slider":
        result = st.slider(label, min_value=cfg.get("min", 0), max_value=cfg.get("max", 10), value=value if value is not None else cfg.get("default", 0))
    elif qtype == "slider_float":
        result = st.slider(label, min_value=cfg.get("min", 0.0), max_value=cfg.get("max", 10.0), value=value if value is not None else cfg.get("default", 0.0), step=cfg.get("step", 0.5))
    else:
        result = st.text_input(label, value=value or "")

    st.session_state.form_data[key] = result


def render_section(section, index):
    st.markdown(
        f"""
        <div class="section-intro">
            <small>Step {index}</small>
            <h2>{section["title"]}</h2>
            <p>{section["summary"]}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    questions = section["questions"]

    for i in range(0, len(questions), 2):
        cols = st.columns(2)

        for col, question in zip(cols, questions[i:i + 2]):
            with col:
                render_question(*question)


def get_secret(name):
    if os.getenv(name):
        return os.getenv(name)
    try:
        return st.secrets.get(name)
    except Exception:
        return None


def encrypt_payload(data, key):
    from cryptography.fernet import Fernet
    return Fernet(key.encode()).encrypt(json.dumps(data).encode()).decode()


def store_submission(data):
    database_url = get_secret("PRVNT_DATABASE_URL")
    encryption_key = get_secret("PRVNT_FERNET_KEY")

    if not database_url:
        raise RuntimeError("PRVNT_DATABASE_URL is not configured.")
    if not encryption_key:
        raise RuntimeError("PRVNT_FERNET_KEY is not configured.")

    import psycopg2

    encrypted = encrypt_payload(data, encryption_key)
    subject_hash = hashlib.sha256((data.get("email") or "").lower().encode()).hexdigest()

    with psycopg2.connect(database_url, sslmode="require") as conn:
        with conn.cursor() as cur:
            cur.execute("""
                create table if not exists prvnt_intake_submissions (
                    id bigserial primary key,
                    schema_version text not null,
                    subject_hash text not null,
                    encrypted_payload text not null,
                    created_at timestamptz not null default now()
                )
            """)
            cur.execute("""
                insert into prvnt_intake_submissions
                    (schema_version, subject_hash, encrypted_payload)
                values (%s, %s, %s)
                returning id
            """, (data["meta_schema_version"], subject_hash, encrypted))
            return cur.fetchone()[0]


def review_tab():
    data = collect_payload()
    df = pd.DataFrame([data])

    st.subheader("Review and Secure Handoff")
    st.write("Export the completed intake, or submit it to PRVNT's secured backend when configured.")

    st.markdown("""
    <div class="security-note">
    <strong>HIPAA note:</strong> this app supports encrypted database submission. HIPAA compliance also requires
    a signed BAA with vendors, access controls, audit logs, encryption at rest and in transit, retention policies,
    staff training, and production security review.
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            "Download JSON",
            data=json.dumps(data, indent=2),
            file_name=f"PRVNT_Intake_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True,
        )

    with col2:
        st.download_button(
            "Download CSV",
            data=df.to_csv(index=False),
            file_name=f"PRVNT_Intake_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col3:
        if st.button("Submit Securely", use_container_width=True):
            try:
                submission_id = store_submission(data)
                st.success(f"Secure submission received. Reference ID: {submission_id}")
            except Exception as exc:
                st.error(str(exc))
                st.caption("For Streamlit Cloud, set PRVNT_DATABASE_URL and PRVNT_FERNET_KEY in Secrets.")

    with st.expander("Clinical data preview", expanded=False):
        st.dataframe(df.T.rename(columns={0: "Response"}), use_container_width=True)


def main():
    inject_css()
    ensure_state()
    show_header()

    answered, total, required_missing = completion_stats()
    elapsed = int(time.time() - st.session_state.started_at)
    minutes, seconds = divmod(elapsed, 60)
    progress = answered / total if total else 0

    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric"><strong>{answered}/{total}</strong><span>fields completed</span></div>
            <div class="metric"><strong>{progress:.0%}</strong><span>overall progress</span></div>
            <div class="metric"><strong>{minutes:02d}:{seconds:02d}</strong><span>session time</span></div>
            <div class="metric"><strong>{required_missing}</strong><span>required fields remaining</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(progress)

    tabs = st.tabs([section["title"] for section in SECTIONS] + ["Review"])

    for idx, (tab, section) in enumerate(zip(tabs[:-1], SECTIONS), start=1):
        with tab:
            render_section(section, idx)

    with tabs[-1]:
        review_tab()


if __name__ == "__main__":
    main()
