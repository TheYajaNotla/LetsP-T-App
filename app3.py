import hashlib
import json
import os
import time
import base64
from datetime import date, datetime

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="PRVNT | Health Onboarding",
    page_icon="PRVNT",
    layout="wide",
    initial_sidebar_state="collapsed",
)

YES_NO = ["No", "Yes"]
FREQ = ["Never", "Occasionally", "Often", "Almost always"]
LOGO_PATH = "Copy of PRVNT Logo.jpg"  # Put your logo here in GitHub

SECTIONS = [
    {
        "title": "Your Profile",
        "summary": "The essentials that help PRVNT personalize your care experience.",
        "questions": [
            ("fullname", "Full name as shown on government-issued identification", "text", {"required": True}),
            ("preferred_name", "Preferred name", "text", {}),
            ("dob", "Date of birth", "date", {"default": date(1990, 1, 1), "required": True}),
            ("age", "Age", "number", {"min": 0, "max": 120, "default": 35}),
            ("sex", "Sex", "select", {"options": ["Female", "Male", "Intersex", "Prefer not to answer"]}),
            ("pronouns", "Preferred pronouns", "select", {"options": ["She / Her", "He / Him", "They / Them", "Other", "Prefer not to answer"]}),
            ("height", "Height", "text", {"placeholder": "cm or ft/in"}),
            ("weight_curr", "Current weight", "text", {"placeholder": "kg or lb"}),
            ("weight_usual", "Usual adult weight", "text", {}),
            ("language", "Preferred language", "text", {"default": "English"}),
            ("mobile", "Mobile number", "text", {"required": True}),
            ("email", "Email address", "text", {"required": True}),
        ],
    },
    {
        "title": "Support Network",
        "summary": "Who is around you, and who should PRVNT coordinate with when needed.",
        "questions": [
            ("emerg_name", "Emergency contact name", "text", {}),
            ("emerg_rel", "Emergency contact relationship", "text", {}),
            ("emerg_phone", "Emergency contact telephone number", "text", {}),
            ("education", "Highest level of education completed", "text", {}),
            ("occupation", "Current occupation or primary daily role", "text", {}),
            ("work_type", "Which best describes your work?", "select", {"options": ["Mostly sitting", "Mostly standing", "Physically active", "Mixed", "Student", "Retired", "Homemaker", "Other"]}),
            ("work_exposure", "Does your work involve any of the following?", "multi", {"options": ["Shift work", "Night work", "Frequent travel", "Heavy lifting", "High stress", "Chemical exposure", "Dust exposure", "Loud noise", "Radiation", "None of the above"]}),
            ("marital_status", "Current marital status", "select", {"options": ["Single", "Married", "Living with partner", "Divorced / Separated", "Widowed", "Prefer not to say"]}),
            ("living_arrangements", "Who do you currently live with?", "select", {"options": ["Alone", "Spouse or partner", "Children", "Parents", "Extended family", "Friends or housemates", "Other"]}),
            ("dependents", "Do you have children or dependents?", "radio", {"options": YES_NO}),
            ("regular_caregiver", "Do you regularly care for another person?", "radio", {"options": YES_NO}),
            ("sick_support", "Who usually supports you if you become unwell?", "text", {}),
            ("social_support_tier", "How would you describe your social support?", "select", {"options": ["Excellent", "Good", "Adequate", "Limited", "Very limited"]}),
            ("regular_provider", "Regular doctor or primary healthcare provider", "text", {}),
            ("active_care_team", "Healthcare professionals currently involved in your care", "multi", {"options": ["Family physician", "Internal medicine physician", "Cardiologist", "Endocrinologist", "Gastroenterologist", "Neurologist", "Rheumatologist", "Pulmonologist", "Nephrologist", "Oncologist", "Psychiatrist", "Psychologist", "Dietitian", "Physiotherapist", "Dentist", "Ophthalmologist", "Other"]}),
            ("care_coordinator", "Who usually coordinates your healthcare?", "select", {"options": ["Family physician", "Specialist", "I coordinate it myself", "Family member", "Other"]}),
            ("prvnt_comm_permission", "Healthcare professionals you would like PRVNT to communicate with?", "radio", {"options": YES_NO}),
        ],
    },
    {
        "title": "Health Goals",
        "summary": "What brought you here, what matters most, and how ready you feel.",
        "questions": [
            ("prompt_join_prvnt", "What prompted you to join PRVNT?", "multi", {"options": ["General health assessment", "Disease prevention", "Family history of disease", "Weight management", "Improve energy", "Better sleep", "Improve physical fitness", "Better nutrition", "Healthy ageing", "Manage an existing medical condition", "Ongoing unexplained symptoms", "Care coordination", "Second opinion", "Recent abnormal test results", "Recommendation from family/friends", "Other"]}),
            ("top_12mo_improvement", "Health concern you would most like to improve over the next 12 months", "area", {}),
            ("good_health_definition", "What does good health look like for you?", "area", {}),
            ("worries_or_fears", "Anything you are worried about that you would like to discuss?", "text", {}),
            ("overall_health_rate", "How would you rate your overall health today?", "slider_select", {"options": ["Poor", "Fair", "Good", "Very good", "Excellent"]}),
            ("health_vs_5yrs_ago", "Compared with five years ago, your health is:", "select", {"options": ["Much worse", "Slightly worse", "About the same", "Slightly better", "Much better"]}),
            ("three_health_goals", "Three most important health goals over the next 12 months", "area", {}),
            ("unaddressed_symptoms", "Anything about your health that has not been fully explained?", "text", {}),
            ("unexpected_doc_visits_12m", "Unexpected doctor visits due to illness in past 12 months", "select", {"options": ["None", "1-2", "3-5", "More than 5"]}),
            ("er_visits_12m", "Emergency room or urgent care visits in past 12 months", "select", {"options": ["None", "Once", "Twice", "Three or more times"]}),
            ("hospital_admissions_12m", "Admitted to hospital in the past 12 months?", "radio", {"options": YES_NO}),
            ("daily_energy_level", "Energy level on most days", "select", {"options": ["Very low", "Low", "Variable", "Good", "Excellent"]}),
            ("health_satisfaction", "Satisfaction with current health", "select", {"options": ["Very dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very satisfied"]}),
            ("health_improvement_confidence", "Confidence that you can improve your health", "select", {"options": ["Not confident at all", "Not very confident", "Unsure", "Confident", "Very confident"]}),
            ("readiness_to_change", "Readiness to make changes", "select", {"options": ["Not ready at present", "Thinking about making changes", "Ready within the next month", "Ready now"]}),
            ("care_decision_preference", "How involved would you like to be in decisions?", "select", {"options": ["Make decisions together with my healthcare team", "Healthcare team guides most decisions", "I decide after medical advice", "No preference"]}),
            ("desired_support_areas", "Areas you would most like support with", "multi", {"options": ["Nutrition", "Exercise", "Sleep", "Stress management", "Weight management", "Medication review", "Managing a chronic condition", "Preventive screening", "Mental wellbeing", "Healthy ageing", "Smoking cessation", "Alcohol reduction", "Women's health", "Men's health", "Other"]}),
            ("historical_plan_barriers", "What previously made it difficult to follow a healthcare plan?", "multi", {"options": ["Cost", "Time", "Work commitments", "Family responsibilities", "Difficulty understanding instructions", "Side effects of treatment", "Lack of motivation", "Limited access to healthcare", "None of the above", "Other"]}),
        ],
    },
    {
        "title": "Medical History",
        "summary": "Diagnoses, medications, allergies, surgeries, and family history.",
        "questions": [
            ("conditions", "Past or current diagnoses", "multi", {"options": ["High blood pressure / hypertension", "Prediabetes", "Type 2 diabetes", "High cholesterol / triglycerides", "Coronary artery disease / angina", "Heart attack history", "Obstructive sleep apnoea", "Asthma", "Chronic kidney disease", "Fatty liver disease", "GERD", "IBS", "Osteopenia / osteoporosis", "Cancer history", "Clinical depression", "Anxiety disorder", "Migraine", "Chronic pain syndromes"]}),
            ("takes_rx", "Are you currently taking prescription medications?", "radio", {"options": YES_NO}),
            ("rx_details", "Prescription medications with doses and frequencies", "area", {}),
            ("takes_otc", "Do you regularly take over-the-counter medicines?", "radio", {"options": YES_NO}),
            ("otc_details", "Over-the-counter products", "area", {}),
            ("takes_supplements", "Do you take vitamins, minerals, or supplements?", "radio", {"options": YES_NO}),
            ("supplement_details", "Supplements and dosages", "area", {}),
            ("supplement_advisor", "Who advises you about supplements?", "select", {"options": ["Doctor", "Dietitian / Nutritionist", "Pharmacist", "Personal trainer", "Family or friends", "Internet / Social Media", "Self-directed", "No one"]}),
            ("stopped_med_side_effects", "Ever stopped a medication due to side effects?", "radio", {"options": YES_NO}),
            ("miss_med_reason", "If you occasionally miss medication, what is the reason?", "multi", {"options": ["I forget", "Side effects", "Cost", "I feel well and do not think I need it", "Difficult schedule", "Prescription not available", "Other"]}),
            ("miss_med_frequency", "How often do you miss doses?", "select", {"options": ["Never", "Rarely", "Sometimes", "Often", "I do not take regular medication"]}),
            ("med_allergies", "Known medication allergies", "text", {}),
            ("food_allergies", "Food allergies or intolerances", "multi", {"options": ["None known", "Milk / Dairy", "Egg", "Wheat / Gluten", "Soy", "Peanut", "Tree nuts", "Fish", "Shellfish", "Sesame", "Other"]}),
            ("env_allergies", "Environmental allergies", "multi", {"options": ["None known", "Pollen", "House dust mites", "Animal dander", "Mould", "Insect stings", "Latex", "Other"]}),
            ("anaphylaxis_history", "Ever had a severe allergic reaction or anaphylaxis?", "radio", {"options": YES_NO}),
            ("wants_interaction_review", "Request supplement-medication interaction review?", "radio", {"options": ["No", "Yes", "Unsure"]}),
            ("surgery_history", "Past surgeries or invasive procedures, with reasons, years, and complications", "area", {}),
            ("hospital_admissions_non_surg", "Historical non-surgical hospital admissions", "area", {}),
            ("anaesthesia_complications", "Complications or side effects from anesthesia", "area", {}),
            ("family_history", "Family history", "multi", {"options": ["High blood pressure", "High cholesterol", "Type 2 diabetes", "Early heart attack", "Stroke events", "Confirmed cancers"]}),
            ("parental_health_status", "Parents' current health, ages, or cause/age at death", "text", {}),
        ],
    },
    {
        "title": "Body Systems",
        "summary": "A focused 90-day symptom review to guide the clinical conversation.",
        "questions": [
            ("sym_rash", "Recurring rash or skin changes", "slider_select", {"options": FREQ}),
            ("sym_bruising", "Easy bruising tendencies", "slider_select", {"options": FREQ}),
            ("sym_hair_loss", "Sudden hair loss or thinning", "slider_select", {"options": FREQ}),
            ("sym_cold_intolerance", "Feeling unusually cold", "slider_select", {"options": FREQ}),
            ("sym_thirst", "Unusually increased thirst", "slider_select", {"options": FREQ}),
            ("sym_anxiety", "Feeling anxious, worried, or unable to relax", "slider_select", {"options": FREQ}),
            ("sym_sadness", "Feeling sad, down, or hopeless", "slider_select", {"options": FREQ}),
            ("sym_overwhelmed", "Feeling completely overwhelmed by life stress", "slider_select", {"options": FREQ}),
        ],
    },
    {
        "title": "Lifestyle Signals",
        "summary": "Nutrition, movement, sleep, and environmental behaviors.",
        "questions": [
            ("diet_pattern", "Usual eating pattern", "select", {"options": ["Omnivore", "Mediterranean-style", "Vegetarian", "Vegan", "Pescatarian", "Low-carbohydrate", "Ketogenic", "Other"]}),
            ("meals_per_day", "Average meals per day", "select", {"options": ["One", "Two", "Three", "Four or more"]}),
            ("veg_servings_day", "Vegetable servings consumed daily", "select", {"options": ["None", "1-2", "3-4", "5 or more"]}),
            ("sugar_beverage_frequency", "Refined sugar or sweetened beverage frequency", "select", {"options": ["Never", "Rarely", "Weekly", "Daily"]}),
            ("exercise_sessions_week", "Physical activity sessions per week", "slider", {"min": 0, "max": 14, "default": 3}),
            ("avg_daily_steps", "Average daily step count, if known", "number", {"min": 0, "max": 100000, "default": 0}),
            ("resting_heart_rate", "Resting heart rate baseline, BPM", "number", {"min": 0, "max": 240, "default": 0}),
            ("estimated_vo2max", "Estimated VO2 max, if known", "text", {}),
            ("sleep_hours_night", "Average sleep duration per night", "slider_float", {"min": 3.0, "max": 12.0, "default": 7.0, "step": 0.5}),
            ("sleep_caffeine_dependency", "Need caffeine to feel alert in the morning?", "radio", {"options": ["Never", "Occasionally", "Most days", "Every day"]}),
            ("sleep_support_used", "Active sleep aid products used", "multi", {"options": ["Prescription medication", "Over-the-counter medication", "Melatonin", "Herbal supplements", "Relaxation techniques", "Meditation", "White noise", "CPAP device", "Nothing", "Other"]}),
            ("tobacco_use", "Tobacco smoking or vaping status", "select", {"options": ["Never smoked", "Ex-smoker", "Current user"]}),
            ("alcohol_servings_week", "Standard units or servings of alcohol consumed weekly", "number", {"min": 0, "max": 100, "default": 0}),
            ("recreational_screen_time", "Recreational non-work screen time on a typical day", "select", {"options": ["Less than 2 hours", "2-4 hours", "5-7 hours", "More than 7 hours"]}),
        ],
    },
    {
        "title": "Prevention Plan",
        "summary": "Where PRVNT should focus preventive planning and follow-up.",
        "questions": [
            ("preventive_support_targets", "Preventive reporting support areas", "multi", {"options": ["Weight management", "Cardiovascular disease prevention", "Diabetes prevention", "Cancer screening", "Vaccinations", "Healthy ageing", "Bone health", "Brain health", "Smoking cessation", "Physical activity", "Nutrition", "Mental wellbeing", "Sleep", "Women's health", "Men's health", "Unsure"]}),
            ("wants_to_prevent_top3", "What would you most like to proactively prevent in the future? Select up to three.", "multi", {"options": ["Heart disease", "Stroke", "Diabetes", "Cancer", "Osteoporosis or fractures", "Memory decline or dementia", "Loss of mobility", "Vision loss", "Chronic pain", "Frailty", "Other"], "max_selections": 3}),
            ("share_records_consent", "Willing to share historical external laboratory or medical records with PRVNT?", "radio", {"options": ["Yes", "No", "Some records only"]}),
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
    }

    .stApp {
        background:var(--paper);
        color:var(--ink);
        font-family:"Plus Jakarta Sans", "Segoe UI", Arial, sans-serif;
    }

    h1,h2,h3,h4,
    .hero h1,
    .section-intro h2,
    .metric strong {
        font-family:"Space Grotesk", "Segoe UI", Arial, sans-serif !important;
        letter-spacing:0 !important;
    }

    p,label,span,div,button,input,textarea {
        font-family:"Plus Jakarta Sans", "Segoe UI", Arial, sans-serif !important;
    }

    h1 {
        font-size:clamp(2.6rem,5vw,5rem) !important;
        line-height:.94 !important;
        max-width:980px;
    }

    .hero {
        min-height:340px;
        padding:56px 48px 34px;
        color:#fff;
        background:
            linear-gradient(110deg,rgba(14,42,54,.98),rgba(31,78,99,.88)),
            radial-gradient(circle at 84% 20%,rgba(144,183,198,.38),transparent 36%);
        border-bottom:5px solid var(--mist);
    }

    .hero-topline {
        display:flex;
        align-items:center;
        gap:18px;
        margin-bottom:28px;
    }

    .hero-logo-slot {
        width:112px;
        height:52px;
        display:flex;
        align-items:center;
        justify-content:center;
        border:1px solid rgba(255,255,255,.34);
        background:rgba(255,255,255,.08);
    }

    .hero-logo-img {
        max-width:96px;
        max-height:36px;
        object-fit:contain;
    }

    .hero-logo-placeholder {
        color:#fff;
        font-family:"Space Grotesk", "Segoe UI", Arial, sans-serif !important;
        font-weight:700;
        letter-spacing:.08em;
        font-size:.92rem;
    }

    .eyebrow {
        color:#dcebef;
        font-size:.78rem;
        font-weight:800;
        letter-spacing:.08em;
        text-transform:uppercase;
    }

    .hero p {
        max-width:780px;
        font-size:1.08rem;
        line-height:1.7;
        color:rgba(255,255,255,.86);
    }

    .metric-row {
        display:grid;
        grid-template-columns:repeat(4,minmax(0,1fr));
        gap:1px;
        border:1px solid var(--line);
        background:var(--line);
        margin:18px 0 28px;
    }

    .metric {
        background:white;
        padding:18px 20px;
    }

    .metric strong {
        display:block;
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
        color:#5c6669;
        max-width:760px;
    }

    div[data-testid="stProgress"] > div > div {
        background-color:var(--harbor);
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

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color:var(--harbor);
        background:var(--harbor);
        color:white;
    }

    .security-note {
        padding:16px 18px;
        border:1px solid var(--line);
        background:#fbfcfc;
        color:#354043;
    }

    @media (max-width:760px) {
        .hero { padding:42px 24px 28px; }
        .hero-topline { align-items:flex-start; flex-direction:column; }
        .metric-row { grid-template-columns:repeat(2,minmax(0,1fr)); }
    }
    </style>
    """, unsafe_allow_html=True)


def ensure_state():
    if "started_at" not in st.session_state:
        st.session_state.started_at = time.time()
    if "form_data" not in st.session_state:
        st.session_state.form_data = {}


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
    data["meta_schema_version"] = "prvnt-onboarding-v1"
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
        result = st.text_area(label, value=value or "", height=112)
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


def encrypt_payload(data, key):
    from cryptography.fernet import Fernet
    return Fernet(key.encode()).encrypt(json.dumps(data).encode()).decode()


def store_submission(data):
    database_url = os.getenv("PRVNT_DATABASE_URL")
    encryption_key = os.getenv("PRVNT_FERNET_KEY")

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

    st.markdown("""
    <div class="section-intro">
        <small>Final step</small>
        <h2>Review and Secure Handoff</h2>
        <p>Export the completed intake, or submit it to PRVNT's secured backend when configured.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="security-note">
    <strong>HIPAA note:</strong> this app supports encrypted database submission, but HIPAA compliance also requires
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

    answered, total, required_missing = completion_stats()
    elapsed = int(time.time() - st.session_state.started_at)
    minutes, seconds = divmod(elapsed, 60)
    progress = answered / total if total else 0

    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as logo_file:
            logo_b64 = base64.b64encode(logo_file.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" alt="PRVNT logo" class="hero-logo-img">'
    else:
        logo_html = '<div class="hero-logo-placeholder">PRVNT</div>'

    st.markdown(f"""
    <section class="hero">
        <div class="hero-topline">
            <div class="hero-logo-slot">{logo_html}</div>
            <div class="eyebrow">PRVNT Comprehensive Health Questionnaire</div>
        </div>

        <h1>Health onboarding, made precise and personal.</h1>
        <p>
            A structured health intake experience designed to turn personal history,
            goals, symptoms, habits and prevention priorities into the beginning of your PRVNT journey.
        </p>
    </section>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric"><strong>{answered}/{total}</strong><span>fields completed</span></div>
        <div class="metric"><strong>{progress:.0%}</strong><span>overall progress</span></div>
        <div class="metric"><strong>{minutes:02d}:{seconds:02d}</strong><span>session time</span></div>
        <div class="metric"><strong>{required_missing}</strong><span>required fields remaining</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(progress)

    tabs = st.tabs([section["title"] for section in SECTIONS] + ["Review"])

    for idx, (tab, section) in enumerate(zip(tabs[:-1], SECTIONS), start=1):
        with tab:
            render_section(section, idx)

    with tabs[-1]:
        review_tab()


if __name__ == "__main__":
    main()
