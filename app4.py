import streamlit as st
import random
import string
import json
import requests
from datetime import datetime

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
# Link this directly to your unique Google Apps Script deployment URL to pipe data directly to Google Sheets
GOOGLE_SHEETS_WEBAPP_URL = "https://script.google.com/macros/s/YOUR_LIVE_DEPLOYMENT_ID/exec"

# ==========================================
# PAGE INITIALIZATION & PREMIUM STYLING
# ==========================================
st.set_page_config(
    page_title="PRVNT | Clinical Intake Matrix",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Deep integration of PRVNT's premium, minimal, human-centric design tokens
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;500;600&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #FAFAFA !important;
        color: #1A1A1A !important;
    }
    
    /* Clean, insight-driven brand header block */
    .prvnt-brand-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 32px 0px 24px 0px;
        border-bottom: 1px solid #EAEAEA;
        margin-bottom: 40px;
    }
    .status-pill {
        display: inline-block;
        background: #F4F4F6;
        color: #2E2E3A;
        font-size: 0.75rem;
        font-weight: 500;
        letter-spacing: 0.03em;
        padding: 4px 14px;
        border-radius: 24px;
        margin-bottom: 12px;
    }
    h1 {
        font-weight: 500 !important;
        letter-spacing: -0.03em;
        color: #111111 !important;
    }
    h3 {
        font-weight: 500 !important;
        color: #111111 !important;
        margin-top: 36px !important;
        margin-bottom: 16px !important;
        font-size: 1.3rem !important;
        letter-spacing: -0.01em;
    }
    .section-subtitle {
        color: #666666;
        font-size: 0.95rem;
        margin-top: -12px;
        margin-bottom: 24px;
        line-height: 1.5;
    }
    
    /* Sub-group layout headers */
    .field-group-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #888888;
        margin-top: 20px;
        margin-bottom: 12px;
    }
    
    /* Elegant, understated buttons matching premium guidelines */
    .stButton>button {
        background-color: #111111 !important;
        color: #FFFFFF !important;
        border-radius: 4px !important;
        padding: 10px 28px !important;
        font-weight: 400 !important;
        letter-spacing: 0.02em;
        border: none !important;
        transition: opacity 0.2s ease;
    }
    .stButton>button:hover {
        opacity: 0.85;
    }
    
    /* Control Panel Card for Sidebar */
    .control-card {
        background: #FFFFFF;
        border: 1px solid #E5E5E5;
        padding: 24px;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Core Session States for Draft Resilience
if "registry_vault" not in st.session_state:
    st.session_state.registry_vault = {}
if "active_key" not in st.session_state:
    st.session_state.active_key = ""
if "reload_status" not in st.session_state:
    st.session_state.reload_status = ""

def create_unique_key():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

def persist_draft_state():
    key = create_unique_key() if not st.session_state.active_key else st.session_state.active_key
    st.session_state.active_key = key
    
    current_snapshot = {k: v for k, v in st.session_state.items() if not k.startswith(('registry_vault', 'reload_status', 'active_key'))}
    st.session_state.registry_vault[key] = current_snapshot

def retrieve_draft_state(target_key):
    target_key = target_key.strip().upper()
    if target_key in st.session_state.registry_vault:
        state_snapshot = st.session_state.registry_vault[target_key]
        for data_key, data_val in state_snapshot.items():
            st.session_state[data_key] = data_val
        st.session_state.active_key = target_key
        st.session_state.reload_status = "restored"
    else:
        st.session_state.reload_status = "invalid"

# ==========================================
# RENDER INTEGRATED BRAND HEADER
# ==========================================
st.markdown("""
<div class="prvnt-brand-header">
    <div>
        <div class="status-pill">🔒 Zero-Knowledge Data Architecture Enabled</div>
        <h1 style="margin:0; font-size:2.2rem;">Comprehensive Health Intake</h1>
    </div>
    <div style="display: flex; align-items: center; justify-content: right; width: 140px; height: 55px;">
        <h2 style="letter-spacing: 4px; color: #111111; font-weight: 500; margin: 0; font-size: 1.6rem;">PRVNT</h2>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# CONTROL INTERFACE & PERSISTENCE SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("### Form Operations")
    st.write("You can pause and save your form at any step. Your details will be held safely under a custom key code.")
    
    if st.button("💾 Securely Save Progress"):
        persist_draft_state()
        
    if st.session_state.active_key:
        st.markdown(f"""
        <div class="control-card">
            <span style='color:#777777; font-size:0.75rem; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;'>Your Access Key</span>
            <h2 style='color:#111111; margin:6px 0; letter-spacing:2px; font-weight:500;'>{st.session_state.active_key}</h2>
            <p style='color:#555555; font-size:0.85rem; margin:0; line-height:1.4;'>Keep this identifier nearby to load your form on any device.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Resume Previous Session")
    lookup_code = st.text_input("Provide your 8-digit token key:", max_chars=8)
    if st.button("🔄 Restore Session Data"):
        retrieve_draft_state(lookup_code)
        
    if st.session_state.reload_status == "restored":
        st.success("Your progress has been seamlessly recovered.")
    elif st.session_state.reload_status == "invalid":
        st.error("Token key could not be verified.")

# ==========================================
# PRODUCTION HEALTH INTAKE ARCHITECTURE
# ==========================================
with st.form("prvnt_master_intake_matrix"):

    # ------------------------------------------
    # SECTION 1: PERSONAL INFORMATION
    # ------------------------------------------
    st.markdown("### 1. Personal Identity & Background")
    st.markdown('<p class="section-subtitle">This section helps us understand your basic informational profile to smoothly coordinate your preventive wellness architecture.</p>', unsafe_allow_html=True)
    
    st.markdown("<div class='field-group-title'>Identity Profiles</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        full_name = st.text_input("Full name (as shown on official ID) *", value=st.session_state.get('full_name', ''))
    with c2:
        preferred_name = st.text_input("Preferred name", value=st.session_state.get('preferred_name', ''))
    with c3:
        dob = st.text_input("Date of Birth (DD/MM/YYYY) *", value=st.session_state.get('dob', ''))
        
    c4, c5, c6 = st.columns(3)
    with c4:
        legal_sex = st.selectbox("Sex assigned at birth *", ["", "Female", "Male", "Intersex", "Prefer not to answer"])
    with c5:
        pronouns = st.text_input("Preferred pronouns (Optional)", value=st.session_state.get('pronouns', ''))
    with c6:
        preferred_lang = st.text_input("Preferred language for care communication", value=st.session_state.get('preferred_lang', 'English'))

    st.markdown("<div class='field-group-title'>Biometric Measurements</div>", unsafe_allow_html=True)
    c7, c8, c9 = st.columns(3)
    with c7:
        height_metric = st.text_input("Height (e.g., cm or ft/in) *", value=st.session_state.get('height_metric', ''))
    with c8:
        weight_metric = st.text_input("Current weight (e.g., kg or lbs) *", value=st.session_state.get('weight_metric', ''))
    with c9:
        historical_weight = st.text_input("Usual adult weight (if consistently different)", value=st.session_state.get('historical_weight', ''))

    st.markdown("<div class='field-group-title'>Primary Reachability</div>", unsafe_allow_html=True)
    c10, c11 = st.columns(2)
    with c10:
        client_phone = st.text_input("Mobile number *", value=st.session_state.get('client_phone', ''))
    with c11:
        client_email = st.text_input("Email address *", value=st.session_state.get('client_email', ''))

    st.markdown("<div class='field-group-title'>Emergency Contacts</div>", unsafe_allow_html=True)
    c12, c13, c14 = st.columns(3)
    with c12:
        emergency_name = st.text_input("Contact name *", value=st.session_state.get('emergency_name', ''))
    with c13:
        emergency_rel = st.text_input("Relationship to you *", value=st.session_state.get('emergency_rel', ''))
    with c14:
        emergency_phone = st.text_input("Telephone number *", value=st.session_state.get('emergency_phone', ''))

    st.markdown("<div class='field-group-title'>Professional & Environmental Context</div>", unsafe_allow_html=True)
    c15, c16 = st.columns(2)
    with c15:
        edu_tier = st.text_input("Highest education level completed", value=st.session_state.get('edu_tier', ''))
        job_role = st.text_input("Current occupation or primary daily focus", value=st.session_state.get('job_role', ''))
        work_physicality = st.selectbox("Which description matches your daily movement pattern?", ["", "Mostly sitting", "Mostly standing", "Physically active", "Mixed", "Student", "Retired", "Homemaker", "Other"])
    with c16:
        occupational_stresses = st.multiselect(
            "Does your daily schedule or environment involve any of the following characteristics? (Select all that apply)",
            ["Shift work", "Night work", "Frequent travel", "Heavy lifting", "High stress", "Chemical exposure", "Dust exposure", "Loud noise", "Radiation", "None of the above"]
        )

    st.markdown("<div class='field-group-title'>Your Household & Support Circle</div>", unsafe_allow_html=True)
    c17, c18 = st.columns(2)
    with c17:
        marital_status = st.selectbox("Current marital status", ["", "Single", "Married", "Living with partner", "Divorced / Separated", "Widowed", "Prefer not to say"])
        living_setup = st.selectbox("Who shared your primary home environment?", ["", "Alone", "Spouse or partner", "Children", "Parents", "Extended family", "Friends or housemates", "Other"])
        social_support_depth = st.selectbox("How would you naturally evaluate your active social support system?", ["", "Excellent", "Good", "Adequate", "Limited", "Very limited"])
    with c18:
        dependents_box = st.text_area("If you care for children, elderly relatives, or other dependents regularly, please clarify briefly:", value=st.session_state.get('dependents_box', ''))
        unwell_backer = st.text_input("Who steps in to look after or support you if you fall ill?", value=st.session_state.get('unwell_backer', ''))

    # ------------------------------------------
    # SECTION 2: HEALTH GOALS & PRIORITIES
    # ------------------------------------------
    st.markdown("---")
    st.markdown("### 2. Strategic Health Vision & Goals")
    st.markdown('<p class="section-subtitle">Understanding your motivations, trajectory, and personal indicators helps us engineer a completely unique, preventative plan.</p>', unsafe_allow_html=True)
    
    st.markdown("<div class='field-group-title'>Current Trajectory</div>", unsafe_allow_html=True)
    c19, c20, c21 = st.columns(3)
    with c19:
        general_health_rate = st.selectbox("How do you evaluate your physical health right now?", ["", "Excellent", "Very good", "Good", "Fair", "Poor"])
    with c20:
        health_comparison_5yr = st.selectbox("Compared to your physical health 5 years ago, you feel:", ["", "Much better", "Slightly better", "About the same", "Slightly worse", "Much worse"])
    with c21:
        daily_energy_baseline = st.selectbox("Which description fits your baseline daily energy levels?", ["", "Excellent", "Good", "Variable", "Low", "Very low"])

    st.markdown("<div class='field-group-title'>Primary Incentives & Focus Areas</div>", unsafe_allow_html=True)
    c22, c23 = st.columns(2)
    with c22:
        joining_drivers = st.multiselect(
            "What inspired you to engage with PRVNT? (Select all that apply)",
            ["General health assessment", "Disease prevention", "Family history of disease", "Weight management", "Improve energy", "Better sleep", "Improve physical fitness", "Better nutrition", "Healthy ageing", "Manage an existing medical condition", "Ongoing unexplained symptoms", "Care coordination", "Second opinion", "Recent abnormal test results", "Recommendation from a healthcare professional", "Recommendation from family or friends", "Other"]
        )
        core_goals_12m = st.text_area("What are your three primary personal health goals for the upcoming year?", value=st.session_state.get('core_goals_12m', ''))
    with c23:
        specific_anxieties = st.text_area("Is there any specific diagnostic path or symptom you are feeling worried about?", value=st.session_state.get('specific_anxieties', ''))
        unaddressed_puzzles = st.text_area("Are there aspects of your history you feel have not been fully explained or addressed by providers?", value=st.session_state.get('unaddressed_puzzles', ''))

    st.markdown("<div class='field-group-title'>Medical Preferences & Change Engagement</div>", unsafe_allow_html=True)
    c24, c25 = st.columns(2)
    with c24:
        decision_philosophy = st.selectbox("How do you prefer to navigate healthcare decisions?", ["", "I prefer to make decisions together with my healthcare team.", "I prefer my healthcare team to guide most decisions.", "I prefer to make my own decisions after receiving medical advice.", "No preference."])
        lifestyle_readiness = st.selectbox("How prepared are you to implement changes in your habits at present?", ["", "Ready now", "Ready within the next month", "Thinking about making changes", "Not ready at present"])
    with c25:
        target_coaching_areas = st.multiselect(
            "Which foundational support landscapes are you looking to optimize?",
            ["Nutrition", "Exercise", "Sleep", "Stress management", "Weight management", "Medication review", "Managing a chronic condition", "Preventive screening", "Mental wellbeing", "Healthy ageing", "Smoking cessation", "Alcohol reduction", "Women's health", "Men's health"]
        )
        cultural_nuances = st.text_area("Are there specific cultural factors, lifestyle frameworks, or care values you want your team to be aware of?", value=st.session_state.get('cultural_nuances', ''))

    historical_friction = st.multiselect(
        "Have any of these dimensions made it difficult for you to keep up with care recommendations in the past?",
        ["Cost", "Time", "Work commitments", "Family responsibilities", "Difficulty understanding instructions", "Side effects of treatment", "Lack of motivation", "Limited access to healthcare", "None of the above"]
    )

    # ------------------------------------------
    # SECTION 3: YOUR MEDICAL TAPESTRY
    # ------------------------------------------
    st.markdown("---")
    st.markdown("### 3. Personal Health History")
    st.markdown('<p class="section-subtitle">A structured review of conditions you currently balance or have managed historically across your life.</p>', unsafe_allow_html=True)
    
    past_conditions_directory = [
        "High blood pressure (Hypertension)", "Prediabetes", "Type 1 diabetes", "Type 2 diabetes", 
        "High cholesterol or triglycerides", "Coronary artery disease / Angina", "Heart attack history",
        "Irregular heartbeat (Arrhythmia)", "Stroke or TIA", "Asthma", "Obstructive sleep apnoea",
        "Thyroid disorder", "Chronic kidney disease", "Fatty liver disease", "Gastro-oesophageal reflux (GERD)",
        "Irritable bowel syndrome (IBS)", "Inflammatory bowel disease (Crohn's / Colitis)", "Coeliac disease",
        "Osteoarthritis", "Rheumatoid arthritis", "Osteoporosis", "Cancer history", "Anaemia", 
        "Depression", "Anxiety disorder", "Attention-deficit / Hyperactivity disorder (ADHD)", "Migraine"
    ]
    
    marked_conditions = st.multiselect("Check any conditions that are a component of your background:", past_conditions_directory)
    condition_elaboration = st.text_area("For the items selected above, please add dates, treatments, or note if they are well managed:", value=st.session_state.get('condition_elaboration', ''))

    st.markdown("<div class='field-group-title'>Major Infectious Background</div>", unsafe_allow_html=True)
    infectious_directory = ["Tuberculosis", "Hepatitis A", "Hepatitis B", "Hepatitis C", "HIV", "COVID-19 requiring hospital admission", "Rheumatic fever", "Dengue fever", "Malaria", "Typhoid fever"]
    marked_infections = st.multiselect("Please select any prominent infections you have navigated:", infectious_directory)

    st.markdown("<div class='field-group-title'>Genetics & Inherited Baselines</div>", unsafe_allow_html=True)
    c26, c27 = st.columns(2)
    with c26:
        genetic_screening_exp = st.selectbox("Have you ever undergone clinical genetic or DNA analysis?", ["", "Yes", "No", "Unsure"])
        genetic_screening_notes = st.text_input("If yes, please state what type and when:", value=st.session_state.get('genetic_screening_notes', ''))
    with c27:
        familial_inherited_flag = st.selectbox("Have you ever been informed of a clear inherited condition in your line?", ["", "Yes", "No", "Unsure"])
        familial_inherited_notes = st.text_input("If yes, please note the condition details:", value=st.session_state.get('familial_inherited_notes', ''))

    # ------------------------------------------
    # SECTION 4: MEDICATIONS, SUPPLEMENTS & SENSITIVITIES
    # ------------------------------------------
    st.markdown("---")
    st.markdown("### 4. Therapeutics & Allergies")
    st.markdown('<p class="section-subtitle">A comprehensive log of what you use to support your physiology, along with all known structural vulnerabilities.</p>', unsafe_allow_html=True)
    
    st.markdown("<div class='field-group-title'>Current Medications & Supplement Intake</div>", unsafe_allow_html=True)
    rx_active_flag = st.radio("Are you taking prescription medications currently?", ["No", "Yes"])
    if rx_active_flag == "Yes":
        rx_log_details = st.text_area("Please list prescription elements (include doses, times per day, and clinical reasons):", value=st.session_state.get('rx_log_details', ''))

    otc_active_flag = st.radio("Do you use over-the-counter therapeutic items frequently (e.g., pain management, antacids, allergy care)?", ["No", "Yes"])
    if otc_active_flag == "Yes":
        otc_log_details = st.text_area("Please outline your frequent non-prescription uses:", value=st.session_state.get('otc_log_details', ''))

    supplements_active_flag = st.radio("Do you take vitamins, minerals, botanical extracts, or nutritional supplements?", ["No", "Yes"])
    if supplements_active_flag == "Yes":
        supplements_details_log = st.text_area("Please write down items, strengths, and your intentions for taking them:", value=st.session_state.get('supplements_details_log', ''))
        supplements_guide_source = st.selectbox("Who serves as your primary reference or guide for your supplement usage?", ["", "Doctor", "Dietitian / Nutritionist", "Pharmacist", "Personal trainer", "Family or friends", "Internet or social media", "Self-directed", "No one"])

    st.markdown("<div class='field-group-title'>Therapeutic Compliance & Patterns</div>", unsafe_allow_html=True)
    c28, c29 = st.columns(2)
    with c28:
        rx_discontinuation_reasons = st.text_area("Have you ever halted a prescription due to side effects? If yes, please explain:", value=st.session_state.get('rx_discontinuation_reasons', ''))
    with c29:
        rx_missed_frequency = st.selectbox("How often do you find yourself missing doses of your regular medications?", ["Never", "Rarely", "Sometimes", "Often", "I do not take regular medication"])

    st.markdown("<div class='field-group-title'>Allergies & Adaptive Reactivity</div>", unsafe_allow_html=True)
    c30, c31 = st.columns(2)
    with c30:
        allergy_med_block = st.text_area("Please specify any drug allergies and the reactions they provoke:", value=st.session_state.get('allergy_med_block', ''))
        allergy_food_selections = st.multiselect("Identify any diagnosed food allergies or strong intolerances:", ["None known", "Milk / Dairy", "Egg", "Wheat / Gluten", "Soy", "Peanut", "Tree nuts", "Fish", "Shellfish", "Sesame"])
    with c31:
        allergy_env_selections = st.multiselect("Identify your known environmental allergy expressions:", ["None known", "Pollen", "House dust mites", "Animal dander", "Mould", "Insect stings", "Latex"])
        anaphylaxis_history_flag = st.radio("Have you ever had a life-threatening, severe systemic allergic reaction (Anaphylaxis)?", ["No", "Yes"])
        if anaphylaxis_history_flag == "Yes":
            anaphylaxis_triggers = st.text_input("Please share the precise trigger agent:", value=st.session_state.get('anaphylaxis_triggers', ''))

    # ------------------------------------------
    # SUBMISSION LOGISTICS & REST EXPORT ENGINE
    # ------------------------------------------
    st.markdown("---")
    st.write("By submitting, your structured details are passed down securely to your private care space.")
    commit_payload_action = st.form_submit_button("🔒 Lock & Submit Clinical Intake Matrix")
    
    if commit_payload_action:
        unified_export_packet = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "full_name": full_name,
            "preferred_name": preferred_name,
            "dob": dob,
            "sex_assigned_at_birth": legal_sex,
            "pronouns": pronouns,
            "language_preference": preferred_lang,
            "contact_email": client_email,
            "contact_phone": client_phone,
            "height_metric": height_metric,
            "weight_metric": weight_metric,
            "historical_baseline_weight": historical_weight,
            "emergency_contact_name": emergency_name,
            "emergency_contact_phone": emergency_phone,
            "occupation_title": job_role,
            "movement_profile": work_physicality,
            "workplace_exposures": ", ".join(occupational_stresses),
            "social_support_index": social_support_depth,
            "general_health_self_rate": general_health_rate,
            "energy_baseline_index": daily_energy_baseline,
            "indicated_primary_drivers": ", ".join(joining_drivers),
            "twelve_month_milestones": core_goals_12m,
            "care_decision_style": decision_philosophy,
            "lifestyle_readiness_marker": lifestyle_readiness,
            "reported_medical_conditions": ", ".join(marked_conditions),
            "medication_allergy_manifest": allergy_med_block,
            "active_session_token": st.session_state.active_key
        }
        
        st.success("Form structural integrity verified locally.")
        
        try:
            with st.spinner("Syncing your record to the secure centralized sheet database..."):
                sync_delivery = requests.post(
                    GOOGLE_SHEETS_WEBAPP_URL,
                    json=unified_export_packet,
                    headers={"Content-Type": "application/json"},
                    timeout=12
                )
                if sync_delivery.status_code == 200:
                    st.balloons()
                    st.success("✨ Clinical record securely recorded in the central cloud Google Sheet.")
                else:
                    st.info("Record held locally. Point GOOGLE_SHEETS_WEBAPP_URL to your live Google macro script to activate full cloud pipeline mirroring.")
        except Exception as dynamic_sync_fault:
            st.info("Record held locally. Sync with your central Google Sheet
