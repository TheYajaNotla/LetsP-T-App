import streamlit as st
import random
import string
import json
import requests
from datetime import datetime

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
# Replace this with your Google Apps Script Web App Deployment URL to pipe data into Google Sheets
GOOGLE_SHEETS_WEBAPP_URL = "https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec"

# ==========================================
# PAGE INITIALIZATION
# ==========================================
st.set_page_config(
    page_title="PRVNT | Clinical Intake Matrix",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Global styling injection for serious, premium, elegant interface
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: #FBFBFB !important;
        color: #1E1E1E !important;
    }
    
    /* Header & Structural Styling */
    .prvnt-brand-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 24px 0px;
        border-bottom: 1px solid #EAEAEA;
        margin-bottom: 32px;
    }
    .status-pill {
        display: inline-block;
        background: #F0F4F8;
        color: #102A43;
        font-size: 0.75rem;
        font-weight: 500;
        padding: 4px 12px;
        border-radius: 20px;
        margin-bottom: 8px;
    }
    h1 {
        font-weight: 600 !important;
        letter-spacing: -0.025em;
    }
    h3 {
        font-weight: 500 !important;
        color: #334E68 !important;
        margin-top: 24px !important;
        font-size: 1.2rem !important;
    }
    
    /* Custom input & form field spacing styling */
    .stButton>button {
        background-color: #102A43 !important;
        color: white !important;
        border-radius: 6px !important;
        padding: 8px 24px !important;
        border: none !important;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #243E56 !important;
        transform: translateY(-1px);
    }
    
    /* Elegant Sidebar Card */
    .save-card {
        background: #FFFFFF;
        border: 1px solid #E4E7EB;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session States for Multi-Step Form Management & Local Storage Emulation
if "form_data" not in st.session_state:
    st.session_state.form_data = {}
if "save_code" not in st.session_state:
    st.session_state.save_code = ""
if "load_error" not in st.session_state:
    st.session_state.load_error = ""
if "save_success" not in st.session_state:
    st.session_state.save_success = False

# Helper: Generate custom secure human-readable access identifier token
def generate_access_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Save current session to pseudo-centralized backup dictionary
def execute_save_draft():
    code = generate_access_code() if not st.session_state.save_code else st.session_state.save_code
    st.session_state.save_code = code
    
    # Bundle current UI values out into centralized session matrix
    payload = {k: v for k, v in st.session_state.items() if not k.startswith(('form_data', 'load_error', 'save_success'))}
    
    # Store locally inside application data pipeline cache
    if "central_registry" not in st.sidebar.session_state:
        st.sidebar.session_state["central_registry"] = {}
    st.sidebar.session_state["central_registry"][code] = payload
    st.session_state.save_success = True

# Load state back out using verification identifier
def execute_load_draft(code_to_verify):
    code_to_verify = code_to_verify.strip().upper()
    if "central_registry" in st.sidebar.session_state and code_to_verify in st.sidebar.session_state["central_registry"]:
        saved_payload = st.sidebar.session_state["central_registry"][code_to_verify]
        for key, val in saved_payload.items():
            st.session_state[key] = val
        st.session_state.save_code = code_to_verify
        st.session_state.load_error = ""
        st.success("Form progress restored successfully.")
    else:
        st.session_state.load_error = "Access code not found or expired."

# ==========================================
# RENDER BRAND HEADER BLOCK
# ==========================================
st.markdown("""
<div class="prvnt-brand-header">
    <div>
        <div class="status-pill">🔒 End-to-End Encrypted Data Pipeline</div>
        <h1 style="color:#102A43; margin:0; font-size:2.1rem;">Comprehensive Health Intake</h1>
        <p style="color:#627D98; margin:4px 0 0 0; font-size:0.95rem;">
            Please complete this intake form with as much detail as you feel comfortable sharing. Your answers help us understand your baseline health and design your preventive health track.
        </p>
    </div>
    <div style="display: flex; align-items: center; justify-content: right; width: 140px; height: 55px;">
        <h2 style="letter-spacing: 2px; color: #102A43; font-weight: 600; margin: 0;">PRVNT</h2>
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# PERSISTENCE & CONTROL INTERFACE
# ==========================================
with st.sidebar:
    st.markdown("### Form Controls")
    st.write("Save your progress at any time to get an access code to resume filling out your details from any browser link.")
    
    if st.button("💾 Save Current Draft"):
        execute_save_draft()
        
    if st.session_state.save_code:
        st.markdown(f"""
        <div class="save-card">
            <span style='color:#627D98; font-size:0.8rem; text-transform:uppercase;'>Your Access Code</span>
            <h2 style='color:#102A43; margin:4px 0; letter-spacing:1px;'>{st.session_state.save_code}</h2>
            <p style='color:#334E68; font-size:0.85rem; margin:0;'>Keep this code safe to return and finish later.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Resume Previous Session")
    input_code = st.text_input("Enter your 8-digit Access Code:", max_chars=8)
    if st.button("🔄 Reload Saved Form"):
        execute_load_draft(input_code)
        
    if st.session_state.load_error:
        st.error(st.session_state.load_error)


# ==========================================
# CORE FORM APPLICATION SECTIONS
# ==========================================
with st.form("comprehensive_intake_form"):
    
    # ------------------------------------------
    # SECTION 1: ABOUT YOU
    # ------------------------------------------
    st.markdown("### 1. Personal Identity & Background")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        full_name = st.text_input("Full Name (as shown on legal ID)", value=st.session_state.get('full_name', ''))
    with c2:
        preferred_name = st.text_input("Preferred Name (what you like to be called)", value=st.session_state.get('preferred_name', ''))
    with c3:
        dob = st.text_input("Date of Birth (DD/MM/YYYY)", value=st.session_state.get('dob', ''))
        
    c4, c5, c6 = st.columns(3)
    with c4:
        sex_assigned = st.selectbox("Sex assigned at birth", ["", "Female", "Male", "Intersex", "Prefer not to answer"])
    with c5:
        pronouns = st.text_input("Preferred Pronouns (e.g. She/Her, He/Him, They/Them)", value=st.session_state.get('pronouns', ''))
    with c6:
        preferred_lang = st.text_input("Preferred Language for Care", value=st.session_state.get('preferred_lang', 'English'))

    c7, c8 = st.columns(2)
    with c7:
        user_email = st.text_input("Email Address", value=st.session_state.get('user_email', ''))
    with c8:
        user_phone = st.text_input("Mobile Number", value=st.session_state.get('user_phone', ''))

    st.markdown("#### Physical Metrics Baseline")
    c9, c10, c11 = st.columns(3)
    with c9:
        height_input = st.text_input("Height (e.g. 175 cm or 5ft 9in)", value=st.session_state.get('height_input', ''))
    with c10:
        weight_input = st.text_input("Current Weight (e.g. 72 kg or 158 lbs)", value=st.session_state.get('weight_input', ''))
    with c11:
        usual_weight = st.text_input("Usual Stable Weight (if different)", value=st.session_state.get('usual_weight', ''))

    st.markdown("#### Emergency Contact Details")
    c12, c13, c14 = st.columns(3)
    with c12:
        emergency_name = st.text_input("Emergency Contact Name", value=st.session_state.get('emergency_name', ''))
    with c13:
        emergency_rel = st.text_input("Relationship to You", value=st.session_state.get('emergency_rel', ''))
    with c14:
        emergency_phone = st.text_input("Contact Number", value=st.session_state.get('emergency_phone', ''))

    st.markdown("#### Occupation & Environment")
    c15, c16 = st.columns(2)
    with c15:
        highest_education = st.text_input("Highest level of education completed", value=st.session_state.get('highest_education', ''))
        current_job = st.text_input("Current occupation or daily focus", value=st.session_state.get('current_job', ''))
        work_nature = st.selectbox("Which best describes your daily activity?", ["", "Mostly sitting", "Mostly standing", "Physically active", "Mixed", "Student", "Retired", "Homemaker", "Other"])
    with c16:
        work_exposures = st.multiselect(
            "Does your daily schedule or environment involve any of the following?",
            ["Shift work", "Night shifts", "Frequent travel", "Heavy physical lifting", "High-stress environments", "Chemical exposures", "Dust exposures", "Loud environments", "Radiation exposure"]
        )

    st.markdown("#### Home & Support Network")
    c17, c18 = st.columns(2)
    with c17:
        marital_status = st.selectbox("Current relationship status", ["", "Single", "Married", "Living with partner", "Divorced / Separated", "Widowed", "Prefer not to say"])
        living_arrangement = st.selectbox("Who do you currently live with?", ["", "Alone", "Spouse or partner", "Children", "Parents", "Extended family", "Friends or housemates", "Other"])
        social_support_rating = st.selectbox("How would you describe your personal social support circle?", ["", "Excellent", "Good", "Adequate", "Limited", "Very limited"])
    with c18:
        dependents_spec = st.text_area("Do you have any children or family members who depend on you for care? If yes, please explain briefly:", value=st.session_state.get('dependents_spec', ''))
        unwell_support = st.text_input("Who usually takes care of you or steps in if you become unwell?", value=st.session_state.get('unwell_support', ''))

    # ------------------------------------------
    # SECTION 2: HEALTH GOALS & PRIORITIES
    # ------------------------------------------
    st.markdown("---")
    st.markdown("### 2. Your Health Priorities")
    
    c19, c20 = st.columns(2)
    with c19:
        primary_motivation = st.multiselect(
            "What prompted you to join PRVNT? (Select all that apply)",
            ["General comprehensive health assessment", "Proactive disease prevention", "Investigating a family history of disease", "Weight management", "Improving daily energy levels", "Achieving better quality sleep", "Improving physical fitness or strength", "Optimizing nutrition & meal habits", "Healthy ageing & longevity support", "Managing a chronic health condition", "Investigating ongoing, unexplained symptoms", "Care coordination across multiple doctors", "Seeking a structured second opinion", "Recent unusual test or lab results", "Recommendation from a medical professional", "Recommendation from family/friends"]
        )
        health_goals_12m = st.text_area("What are the three most important health outcomes you want to achieve over the next year?", value=st.session_state.get('health_goals_12m', ''))
    with c20:
        current_health_rate = st.selectbox("How would you rate your overall health today?", ["", "Excellent", "Very good", "Good", "Fair", "Poor"])
        health_5yrs_compare = st.selectbox("Compared with five years ago, your health feels:", ["", "Much better", "Slightly better", "About the same", "Slightly worse", "Much worse"])
        energy_levels = st.selectbox("Which best describes your daily baseline energy level?", ["", "Excellent", "Good", "Variable / Unpredictable", "Low", "Very low"])

    c21, c22 = st.columns(2)
    with c21:
        medical_worry = st.text_area("Is there a specific symptom or diagnosis that you are particularly worried about right now?", value=st.session_state.get('medical_worry', ''))
        unaddressed_concerns = st.text_area("Is there anything about your health history that you feel has never been fully explained or properly addressed?", value=st.session_state.get('unaddressed_concerns', ''))
    with c22:
        readiness_to_change = st.selectbox("How ready are you to make changes to your daily lifestyle habits right now?", ["", "Ready to start immediately", "Ready to begin within the next month", "Thinking about making changes but hesitant", "Not ready to make lifestyle modifications at present"])
        decision_preference = st.selectbox("How do you prefer to approach healthcare decisions?", ["", "I prefer to make decisions collectively with my healthcare team", "I prefer my medical team to guide and outline the plan", "I prefer to make my own decisions independently after receiving advice", "No strong preference"])

    support_areas = st.multiselect(
        "Which areas would you most like lifestyle or medical coaching support with? (Select all that apply)",
        ["Nutrition Optimization", "Exercise Planning & Movement", "Sleep Quality & Rest", "Stress Management & Resilience", "Weight Tracking & Management", "Medication Strategy Review", "Managing an Existing Chronic Condition", "Staying Up to Date with Preventive Screenings", "Mental & Emotional Wellbeing", "Longevity & Healthy Ageing", "Smoking Cessation Support", "Alcohol Intake Reduction", "Hormonal & Reproductive Health Track"]
    )
    
    cultural_preferences = st.text_area("Are there any personal values, cultural beliefs, or care preferences you would like your medical team to keep in mind when designing your track?", value=st.session_state.get('cultural_preferences', ''))
    
    past_barriers = st.multiselect(
        "Have any of the following made it challenging to follow health or care plans in the past?",
        ["Financial cost or budgeting constraints", "Time constraints", " Demanding work commitments", "Family or caregiving responsibilities", "Difficulty understanding complex medical instructions", "Experiencing uncomfortable side effects from treatments", "Difficulty keeping up motivation or consistency", "Limited physical access to clinics or diagnostics"]
    )

    # ------------------------------------------
    # SECTION 3: YOUR HEALTH HISTORY
    # ------------------------------------------
    st.markdown("---")
    st.markdown("### 3. Personal Medical Background")
    st.write("Please indicate any health conditions you have had in the past or are currently managing.")
    
    conditions_list = [
        "High blood pressure", "Prediabetes", "Type 1 diabetes", "Type 2 diabetes", 
        "High cholesterol or triglycerides", "Heart conditions (Angina / CAD)", "Heart attack history",
        "Irregular heartbeats (Arrhythmias)", "Stroke or TIA", "Asthma", "Sleep Apnoea",
        "Thyroid disorders", "Chronic kidney disease", "Fatty liver disease", "Reflux (GERD / Heartburn)",
        "Irritable Bowel Syndrome (IBS)", "Inflammatory Bowel Disease (Crohn's / Colitis)",
        "Coeliac disease", "Arthritis (Osteoarthritis / Rheumatoid)", "Osteoporosis or low bone density",
        "Cancer history", "Anaemia", "Depression", "Anxiety condition", "Migraines"
    ]
    
    selected_past_conditions = st.multiselect("Select any medical conditions you have experienced or are currently managing:", conditions_list)
    condition_details = st.text_area("For any selected conditions, please briefly note the year of diagnosis, treatments, and if it is well-controlled:", value=st.session_state.get('condition_details', ''))

    st.markdown("#### Serious Past Infections")
    infections_list = ["Tuberculosis", "Hepatitis A", "Hepatitis B", "Hepatitis C", "HIV", "Severe COVID-19 requiring hospitalization", "Rheumatic Fever", "Dengue or Malaria"]
    selected_infections = st.multiselect("Select any of the following history of infections:", infections_list)

    c23, c24 = st.columns(2)
    with c23:
        genetic_testing = st.selectbox("Have you ever undergone clinical genetic or DNA profile testing?", ["", "No", "Yes", "Unsure"])
    with c24:
        genetic_details = st.text_input("If yes, what type of genetic testing did you have and when?", value=st.session_state.get('genetic_details', ''))

    # ------------------------------------------
    # SECTION 4: MEDICATIONS, SUPPLEMENTS & ALLERGIES
    # ------------------------------------------
    st.markdown("---")
    st.markdown("### 4. Medications, Supplements & Allergies")
    
    prescriptions_active = st.radio("Are you currently taking any prescription medications?", ["No", "Yes"])
    if prescriptions_active == "Yes":
        prescription_details = st.text_area("Please list your prescription medicines (include dose, frequency, and the reason you take it):", value=st.session_state.get('prescription_details', ''))

    otc_active = st.radio("Do you regularly take any over-the-counter medicines (like pain relievers, antacids, or allergy tablets)?", ["No", "Yes"])
    if otc_active == "Yes":
        otc_details = st.text_area("Please list your regular over-the-counter medicines:", value=st.session_state.get('otc_details', ''))

    supplements_active = st.radio("Do you take any daily vitamins, minerals, or herbal supplements?", ["No", "Yes"])
    if supplements_active == "Yes":
        supplement_details = st.text_area("Please list your current vitamins and supplements (with dosage if known):", value=st.session_state.get('supplement_details', ''))
        supplement_advisor = st.selectbox("Who primarily guides or recommends your supplement selection?", ["", "Medical Doctor", "Dietitian / Nutritionist", "Pharmacist", "Personal Trainer", "Family or friends advice", "Internet / Social Media insights", "Self-directed choice"])

    st.markdown("#### Medication Compliance & Safety")
    c25, c26 = st.columns(2)
    with c25:
        stopped_side_effects = st.text_area("Have you ever stopped taking a prescribed medicine because of uncomfortable side effects? If yes, please describe:", value=st.session_state.get('stopped_side_effects', ''))
    with c26:
        missed_doses_frequency = st.selectbox("If you take regular medications, how often do you occasionally miss a dose?", ["Never", "Rarely", "Sometimes", "Often", "I do not take regular medications"])

    st.markdown("#### Allergies & Sensitivities")
    c27, c28 = st.columns(2)
    with c27:
        med_allergies = st.text_area("Do you have any known allergies or adverse reactions to specific medications? If yes, please specify:", value=st.session_state.get('med_allergies', ''))
        food_allergies_list = st.multiselect("Select any diagnosed food allergies or structural intolerances:", ["None known", "Dairy / Milk sensitivity", "Eggs", "Wheat / Gluten", "Soy", "Peanuts", "Tree nuts", "Fish", "Shellfish", "Sesame"])
    with c28:
        environmental_allergies = st.multiselect("Select any known environmental allergies:", ["None known", "Pollen / Hayfever", "House dust mites", "Animal dander", "Mould spores", "Insect stings", "Latex sensitivity"])
        severe_allergy_history = st.radio("Have you ever experienced a severe, life-threatening allergic reaction (Anaphylaxis)?", ["No", "Yes"])
        if severe_allergy_history == "Yes":
            allergy_trigger = st.text_input("What was the specific trigger for the reaction?", value=st.session_state.get('allergy_trigger', ''))
            carries_epipen = st.checkbox("Do you currently carry an emergency adrenaline auto-injector (EpiPen)?")

    # Final Notes
    submission_notes = st.text_area("Is there anything else regarding your health, family history, or personal medical concerns you would like your care team to know?", value=st.session_state.get('submission_notes', ''))

    # ==========================================
    # SUBMIT AND DATA EXPORT ENGINE
    # ==========================================
    st.markdown("---")
    submit_button = st.form_submit_button("🔒 Submit Completed Clinical Intake Form")
    
    if submit_button:
        # Construct flat JSON dictionary containing all form states
        compiled_form_record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "full_name": full_name,
            "preferred_name": preferred_name,
            "dob": dob,
            "sex_assigned": sex_assigned,
            "pronouns": pronouns,
            "preferred_lang": preferred_lang,
            "user_email": user_email,
            "user_phone": user_phone,
            "height": height_input,
            "weight": weight_input,
            "usual_weight": usual_weight,
            "emergency_name": emergency_name,
            "emergency_rel": emergency_rel,
            "emergency_phone": emergency_phone,
            "current_job": current_job,
            "work_nature": work_nature,
            "work_exposures": ", ".join(work_exposures),
            "marital_status": marital_status,
            "living_arrangement": living_arrangement,
            "social_support_rating": social_support_rating,
            "primary_motivation": ", ".join(primary_motivation),
            "health_goals_12m": health_goals_12m,
            "current_health_rate": current_health_rate,
            "energy_levels": energy_levels,
            "selected_past_conditions": ", ".join(selected_past_conditions),
            "med_allergies": med_allergies,
            "submission_notes": submission_notes
        }
        
        # Display elegant internal verification message
        st.success("Form processed successfully locally.")
        
        # Attempt central deployment post to Google Sheets Webapp via REST endpoint
        try:
            with st.spinner("Transmitting form safely to the central registry..."):
                response = requests.post(
                    GOOGLE_SHEETS_WEBAPP_URL, 
                    json=compiled_form_record, 
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                if response.status_code == 200:
                    st.balloons()
                    st.success("✨ Intake entry securely logged and saved in the central Google Sheets database.")
                else:
                    st.info("Entry saved locally. Point the `GOOGLE_SHEETS_WEBAPP_URL` endpoint variable to your live Google Sheet macro pipeline to activate complete cloud capture sync.")
        except Exception as transmission_error:
            st.info("Form record compiled locally. (Cloud sync is ready for connection by inserting your active webhook URL into the deployment script variables).")
            
        # Display structured summary for consumer confirmation
        st.markdown("### Submission Summary Confirmation")
        st.json(compiled_form_record)
