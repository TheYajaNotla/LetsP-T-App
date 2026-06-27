import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

# --- PRVNT IDENTITY SET UP & CONFIGURATION ---
st.set_page_config(
    page_title="PRVNT | Clinical Matrix Onboarding",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- BRAND DESIGN SYSTEM & TYPOGRAPHY STYLE REGISTRY ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');
    
    /* PRVNT Premium Palette Custom Rules */
    .stApp {
        background-color: #F7F7F7 !important; /* Off-White */
        color: #0F0F0F !important; /* True Black */
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.03em !important;
        text-transform: uppercase;
        color: #0F0F0F !important;
    }
    
    .prvnt-header-block {
        background: linear-gradient(135deg, #0E2A36 0%, #1F4E63 100%); /* Midnight to Harbor Blue */
        color: #F7F7F7 !important;
        padding: 40px;
        border-left: 6px solid #90B7C6; /* Aqua Mist */
        margin-bottom: 30px;
    }
    
    .section-card {
        background-color: #FFFFFF;
        padding: 25px 35px;
        border: 1px solid #EFEFEF;
        border-radius: 2px;
        margin-bottom: 25px;
    }
    
    .gamified-status-pill {
        background-color: #0E2A36;
        color: #FFFFFF;
        padding: 4px 10px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

# --- CORE STATE INITIALIZATION ---
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.start_time = time.time()
    st.session_state.form_data = {}

# --- IMMERSIVE APP HEADER BAR ---
elapsed_seconds = round(time.time() - st.session_state.start_time)
mins, secs = divmod(elapsed_seconds, 60)

st.markdown(f"""
    <div class="prvnt-header-block">
        <span class="gamified-status-pill">Comprehensive Intake Interface</span>
        <h1 style="color:#F7F7F7; margin:10px 0 0 0; font-size:36px;">PRVNT Master Health Onboarding</h1>
        <p style="margin:8px 0 0 0; font-size:14px; opacity:0.85;">
            Dynamic execution portal incorporating full structured intake categories. All inputs persist directly into data schemas.
        </p>
    </div>
""", unsafe_allow_html=True)

# Fixed Header Tracking Bar
t_col1, t_col2 = st.columns([2, 2])
with t_col1:
    st.markdown(f"**Session Baseline:** Tracking Active Database Parameters")
with t_col2:
    st.markdown(f"<div style='text-align:right; font-size:13px; color:#1F4E63;'>⏱️ System Time-on-Page: <b>{mins:02d}:{secs:02d}</b></div>", unsafe_allow_html=True)

# --- LOGICAL CORE STAGED TABS ARCHITECTURE ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📍 1. Personal & Demographics", 
    "📈 2. Health Goals Today", 
    "📋 3. Past History & Medications", 
    "🧬 4. System Review & Habits",
    "💾 5. Save & Clinical Matrix Output"
])

# ==========================================
# TAB 1: PERSONAL & DEMOGRAPHICS
# ==========================================
with tab1:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Section 1 — Personal Information")
    
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.form_data['fullname'] = st.text_input("1. Full name (as shown on your government-issued identification)?")
        st.session_state.form_data['preferred_name'] = st.text_input("2. Preferred name?")
        st.session_state.form_data['dob'] = st.date_input("3. Date of birth?", value=datetime(1990, 1, 1))
        st.session_state.form_data['age'] = st.number_input("4. Age?", min_value=0, max_value=120, value=35)
        st.session_state.form_data['sex'] = st.selectbox("5. Sex?", ["Female", "Male", "Intersex", "Prefer not to answer"])
        st.session_state.form_data['pronouns'] = st.selectbox("6. Preferred Pronouns?", ["She / Her", "He / Him", "They / Them", "Other", "Prefer not to answer"])
    with c2:
        st.session_state.form_data['height'] = st.text_input("7. Height? (e.g., cm or ft/in)")
        st.session_state.form_data['weight_curr'] = st.text_input("8. Current Weight? (e.g., kg or lb)")
        st.session_state.form_data['weight_usual'] = st.text_input("9. Usual Adult Weight?")
        st.session_state.form_data['language'] = st.text_input("10. Preferred language?", "English")
        st.session_state.form_data['mobile'] = st.text_input("11. Mobile number?")
        st.session_state.form_data['email'] = st.text_input("12. Email address?")

    st.markdown("---")
    st.markdown("#### Emergency Contact & Social Infrastructure")
    ec1, ec2 = st.columns(2)
    with ec1:
        st.session_state.form_data['emerg_name'] = st.text_input("13. Emergency Contact name?")
        st.session_state.form_data['emerg_rel'] = st.text_input("14. Emergency Contact Relationship?")
        st.session_state.form_data['emerg_phone'] = st.text_input("15. Telephone number?")
        st.session_state.form_data['education'] = st.text_input("16. Highest level of education completed?")
        st.session_state.form_data['occupation'] = st.text_input("17. Current occupation or primary daily role?")
        st.session_state.form_data['work_type'] = st.selectbox("18. Which best describes your work?", ["Mostly sitting", "Mostly standing", "Physically active", "Mixed", "Student", "Retired", "Homemaker", "Other"])
    with ec2:
        st.session_state.form_data['work_exposure'] = st.multiselect("19. Does your work involve any of the following? (Mark all that apply)", ["Shift work", "Night work", "Frequent travel", "Heavy lifting", "High stress", "Chemical exposure", "Dust exposure", "Loud noise", "Radiation", "None of the above"])
        st.session_state.form_data['marital_status'] = st.selectbox("20. What is your current marital status?", ["Single", "Married", "Living with partner", "Divorced / Separated", "Widowed", "Prefer not to say"])
        st.session_state.form_data['living_arrangements'] = st.selectbox("21. Who do you currently live with?", ["Alone", "Spouse or partner", "Children", "Parents", "Extended family", "Friends or housemates", "Other"])
        st.session_state.form_data['dependents'] = st.radio("22. Do you have children or dependents?", ["No", "Yes"])
        st.session_state.form_data['regular_caregiver'] = st.radio("23. Do you regularly care for another person?", ["No", "Yes"])
        st.session_state.form_data['sick_support'] = st.text_input("25. Who usually supports you if you become unwell?")
        st.session_state.form_data['social_support_tier'] = st.selectbox("26. How would you describe your social support?", ["Excellent", "Good", "Adequate", "Limited", "Very limited"])

    st.markdown("---")
    st.markdown("#### Healthcare Team Coordination")
    ht1, ht2 = st.columns(2)
    with ht1:
        st.session_state.form_data['regular_provider'] = st.text_input("27. Who is your regular doctor or primary healthcare provider?")
        st.session_state.form_data['active_care_team'] = st.multiselect("28. Which healthcare professionals are currently involved in your care?", ["Family physician", "Internal medicine physician", "Cardiologist", "Endocrinologist", "Gastroenterologist", "Neurologist", "Rheumatologist", "Pulmonologist", "Nephrologist", "Oncologist", "Psychiatrist", "Psychologist", "Dietitian", "Physiotherapist", "Dentist", "Ophthalmologist", "Other"])
    with ht2:
        st.session_state.form_data['care_coordinator'] = st.selectbox("29. Who usually coordinates your healthcare?", ["Family physician", "Specialist", "I coordinate it myself", "Family member", "Other"])
        st.session_state.form_data['prvnt_comm_permission'] = st.radio("30. Are there any healthcare professionals you would like PRVNT to communicate with?", ["No", "Yes"])
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 2: HEALTH GOALS TODAY
# ==========================================
with tab2:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Section 2 — Health Goals & Current Baseline Status")
    
    st.session_state.form_data['prompt_join_prvnt'] = st.multiselect("31. What prompted you to join PRVNT? (Mark all that apply)", ["General health assessment", "Disease prevention", "Family history of disease", "Weight management", "Improve energy", "Better sleep", "Improve physical fitness", "Better nutrition", "Healthy ageing", "Manage an existing medical condition", "Ongoing unexplained symptoms", "Care coordination", "Second opinion", "Recent abnormal test results", "Recommendation from family/friends", "Other"])
    st.session_state.form_data['top_12mo_improvement'] = st.text_area("32. What health concern would you most like to improve over the next 12 months?")
    st.session_state.form_data['good_health_definition'] = st.text_area("33. What does good health look like for you?")
    st.session_state.form_data['worries_or_fears'] = st.text_input("34. Is there anything you are worried about that you would like us to discuss during your assessment?")
    
    st.markdown("---")
    g1, g2 = st.columns(2)
    with g1:
        st.session_state.form_data['overall_health_rate'] = st.select_slider("36. How would you rate your overall health today?", options=["Poor", "Fair", "Good", "Very good", "Excellent"])
        st.session_state.form_data['health_vs_5yrs_ago'] = st.selectbox("37. Compared with five years ago, your health is:", ["Much worse", "Slightly worse", "About the same", "Slightly better", "Much better"])
        st.session_state.form_data['three_health_goals'] = st.text_area("38. What are your three most important health goals over the next 12 months?")
        st.session_state.form_data['unaddressed_symptoms'] = st.text_input("41. Is there anything about your health that you feel has not been fully explained?")
    with g2:
        st.session_state.form_data['unexpected_doc_visits_12m'] = st.selectbox("42. Unexpected doctor visits due to illness in past 12 months?", ["None", "1–2", "3–5", "More than 5"])
        st.session_state.form_data['er_visits_12m'] = st.selectbox("43. Emergency room or urgent care visits in past 12 months?", ["None", "Once", "Twice", "Three or more times"])
        st.session_state.form_data['hospital_admissions_12m'] = st.radio("44. Admitted to a hospital in the past 12 months?", ["No", "Yes"])
        st.session_state.form_data['daily_energy_level'] = st.selectbox("45. Energy level on most days?", ["Very low", "Low", "Variable", "Good", "Excellent"])

    st.markdown("---")
    p1, p2 = st.columns(2)
    with p1:
        st.session_state.form_data['health_satisfaction'] = st.selectbox("46. How satisfied are you with your current health?", ["Very dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very satisfied"])
        st.session_state.form_data['health_improvement_confidence'] = st.selectbox("47. How confident are you that you can improve your health?", ["Not confident at all", "Not very confident", "Unsure", "Confident", "Very confident"])
        st.session_state.form_data['readiness_to_change'] = st.selectbox("48. How ready are you to make changes?", ["Not ready at present", "Thinking about making changes", "Ready within the next month", "Ready now"])
    with p2:
        st.session_state.form_data['care_decision_preference'] = st.selectbox("49. How involved would you like to be in decisions?", ["I prefer to make decisions together with my healthcare team.", "I prefer my healthcare team to guide most decisions.", "I prefer to make my own decisions after receiving medical advice.", "No preference."])
        st.session_state.form_data['desired_support_areas'] = st.multiselect("50. Which areas would you most like support with?", ["Nutrition", "Exercise", "Sleep", "Stress management", "Weight management", "Medication review", "Managing a chronic condition", "Preventive screening", "Mental wellbeing", "Healthy ageing", "Smoking cessation", "Alcohol reduction", "Women's health", "Men's health", "Other"])
        st.session_state.form_data['historical_plan_barriers'] = st.multiselect("51. Is there anything that has previously made it difficult for you to follow a healthcare plan?", ["Cost", "Time", "Work commitments", "Family responsibilities", "Difficulty understanding instructions", "Side effects of treatment", "Lack of motivation", "Limited access to healthcare", "None of the above", "Other"])
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 3: PAST HISTORY & MEDICATIONS
# ==========================================
with tab3:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Section 3 & 4 — Clinical Pathologies, Medications & Interventions")
    
    st.markdown("#### Past Lifetime Medical Manifestations Matrix")
    st.caption("Toggle checking box state for any active or historical clinical diagnoses:")
    
    diag_col1, diag_col2, diag_col3 = st.columns(3)
    with diag_col1:
        st.session_state.form_data['cond_htn'] = st.checkbox("High Blood Pressure (Hypertension)")
        st.session_state.form_data['cond_predm'] = st.checkbox("Prediabetes")
        st.session_state.form_data['cond_dm2'] = st.checkbox("Type 2 Diabetes")
        st.session_state.form_data['cond_chol'] = st.checkbox("High Cholesterol / Triglycerides")
        st.session_state.form_data['cond_cad'] = st.checkbox("Coronary Artery Disease / Angina")
        st.session_state.form_data['cond_heart_attack'] = st.checkbox("Heart Attack History")
    with diag_col2:
        st.session_state.form_data['cond_osa'] = st.checkbox("Obstructive Sleep Apnoea (OSA)")
        st.session_state.form_data['cond_asthma'] = st.checkbox("Asthma")
        st.session_state.form_data['cond_kidney'] = st.checkbox("Chronic Kidney Disease (CKD)")
        st.session_state.form_data['cond_fatty_liver'] = st.checkbox("Fatty Liver Disease")
        st.session_state.form_data['cond_gerd'] = st.checkbox("Gastro-oesophageal Reflux (GERD)")
        st.session_state.form_data['cond_ibs'] = st.checkbox("Irritable Bowel Syndrome (IBS)")
    with diag_col3:
        st.session_state.form_data['cond_osteoporosis'] = st.checkbox("Osteopenia / Osteoporosis")
        st.session_state.form_data['cond_cancer'] = st.checkbox("Malignancy / Cancer History")
        st.session_state.form_data['cond_depression'] = st.checkbox("Clinical Depression")
        st.session_state.form_data['cond_anxiety'] = st.checkbox("Anxiety Disorder")
        st.session_state.form_data['cond_migraine'] = st.checkbox("Migraine Profiles")
        st.session_state.form_data['cond_chronic_pain'] = st.checkbox("Chronic Pain Syndromes")

    st.markdown("---")
    st.markdown("#### Section 4 — Medications, Supplements & Allergies")
    med1, med2 = st.columns(2)
    with med1:
        st.session_state.form_data['takes_rx'] = st.radio("58. Are you currently taking any prescription medications?", ["No", "Yes"])
        st.session_state.form_data['rx_details'] = st.text_area("If Yes, list medications with doses and frequencies:")
        st.session_state.form_data['takes_otc'] = st.radio("59. Do you regularly take any over-the-counter medicines?", ["No", "Yes"])
        st.session_state.form_data['otc_details'] = st.text_area("If Yes, list OTC products:")
        st.session_state.form_data['takes_supplements'] = st.radio("60. Do you take vitamins, minerals or supplements?", ["No", "Yes"])
        st.session_state.form_data['supplement_details'] = st.text_area("If Yes, list supplements and dosages:")
        st.session_state.form_data['supplement_advisor'] = st.selectbox("61. Who advises you about supplements?", ["Doctor", "Dietitian / Nutritionist", "Pharmacist", "Personal trainer", "Family or friends", "Internet / Social Media", "Self-directed", "No one"])
    with med2:
        st.session_state.form_data['stopped_med_side_effects'] = st.radio("62. Have you ever stopped taking a medication due to side effects?", ["No", "Yes"])
        st.session_state.form_data['miss_med_reason'] = st.multiselect("64. If you occasionally miss medication, what is the reason?", ["I forget", "Side effects", "Cost", "I feel well and do not think I need it", "Difficult schedule", "Prescription not available", "Other"])
        st.session_state.form_data['miss_med_frequency'] = st.selectbox("65. How often do you miss doses?", ["Never", "Rarely", "Sometimes", "Often", "I do not take regular medication"])
        st.session_state.form_data['med_allergies'] = st.text_input("66. List any known medication allergies:")
        st.session_state.form_data['food_allergies'] = st.multiselect("67. Food allergies/intolerances:", ["None known", "Milk / Dairy", "Egg", "Wheat / Gluten", "Soy", "Peanut", "Tree nuts", "Fish", "Shellfish", "Sesame", "Other"])
        st.session_state.form_data['env_allergies'] = st.multiselect("70. Environmental allergies:", ["None known", "Pollen", "House dust mites", "Animal dander", "Mould", "Insect stings", "Latex", "Other"])
        st.session_state.form_data['anaphylaxis_history'] = st.radio("71. Have you ever had a severe allergic reaction (anaphylaxis)?", ["No", "Yes"])
        st.session_state.form_data['wants_interaction_review'] = st.radio("76. Request full clinical supplement-medication interaction review?", ["No", "Yes", "Unsure"])

    st.markdown("---")
    st.markdown("#### Section 5 & 6 — Surgical History & Hereditary Family Profiles")
    surg1, surg2 = st.columns(2)
    with surg1:
        st.session_state.form_data['surgery_history'] = st.text_area("78-79. List any past surgeries or invasive procedures (include reasons, years, complications):")
        st.session_state.form_data['hospital_admissions_non_surg'] = st.text_area("80-81. List historical non-surgical hospital admissions:")
        st.session_state.form_data['anaesthesia_complications'] = st.text_area("82-85. Detail any historical complications or side effects experienced from anesthesia:")
    with surg2:
        st.session_state.form_data['fam_hx_htn'] = st.checkbox("Family History: High Blood Pressure")
        st.session_state.form_data['fam_hx_chol'] = st.checkbox("Family History: High Cholesterol")
        st.session_state.form_data['fam_hx_dm2'] = st.checkbox("Family History: Type 2 Diabetes")
        st.session_state.form_data['fam_hx_heart_attack'] = st.checkbox("Family History: Early Heart Attack")
        st.session_state.form_data['fam_hx_stroke'] = st.checkbox("Family History: Stroke Events")
        st.session_state.form_data['fam_hx_cancer'] = st.checkbox("Family History: Confirmed Malignancies / Cancers")
        st.session_state.form_data['parental_health_status'] = st.text_input("101. Are your parents in good health? List current ages or cause/age at death:")
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 4: SYSTEM REVIEW & HABITS
# ==========================================
with tab4:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Section 7, 8, 9 & 10 — Clinical Review of Systems & Lifestyle Habits")
    
    st.markdown("#### 3-Month Symptom Manifestation Tracker")
    st.caption("Quantify recurring symptoms felt across the past 90 days:")
    
    sys1, sys2 = st.columns(2)
    with sys1:
        st.session_state.form_data['sym_rash'] = st.select_slider("156. Recurring rash or skin changes?", options=["Never", "Occasionally", "Often", "Almost always"])
        st.session_state.form_data['sym_bruising'] = st.select_slider("157. Easy bruising tendencies?", options=["Never", "Occasionally", "Often", "Almost always"])
        st.session_state.form_data['sym_hair_loss'] = st.select_slider("158. Sudden hair loss or thinning tracks?", options=["Never", "Occasionally", "Often", "Almost always"])
        st.session_state.form_data['sym_cold_intolerance'] = st.select_slider("161. Feeling unusually cold?", options=["Never", "Occasionally", "Often", "Almost always"])
    with sys2:
        st.session_state.form_data['sym_thirst'] = st.select_slider("163. Unusually increased fluid thirst metrics?", options=["Never", "Occasionally", "Often", "Almost always"])
        st.session_state.form_data['sym_anxiety'] = st.select_slider("166. Feeling anxious, worried or unable to relax?", options=["Never", "Occasionally", "Often", "Almost always"])
        st.session_state.form_data['sym_sadness'] = st.select_slider("167. Feeling sad, down or hopeless?", options=["Never", "Occasionally", "Often", "Almost always"])
        st.session_state.form_data['sym_overwhelmed'] = st.select_slider("169. Feeling completely overwhelmed by life stress?", options=["Never", "Occasionally", "Often", "Almost always"])

    st.markdown("---")
    st.markdown("#### Section 8 & 9 — Nutrition & Physical Capacity Inputs")
    nut1, nut2 = st.columns(2)
    with nut1:
        st.session_state.form_data['diet_pattern'] = st.selectbox("173. Which best describes your usual eating pattern?", ["Omnivore", "Mediterranean-style", "Vegetarian", "Vegan", "Pescatarian", "Low-carbohydrate", "Ketogenic", "Other"])
        st.session_state.form_data['meals_per_day'] = st.selectbox("174. On average, how many meals do you eat each day?", ["One", "Two", "Three", "Four or more"])
        st.session_state.form_data['veg_servings_day'] = st.selectbox("177. Vegetable servings consumed daily?", ["None", "1–2", "3–4", "5 or more"])
        st.session_state.form_data['sugar_beverage_frequency'] = st.selectbox("Refined sugar or sweetened beverage frequency intake?", ["Never", "Rarely", "Weekly", "Daily"])
    with nut2:
        st.session_state.form_data['exercise_sessions_week'] = st.slider("196. How many times per week do you engage in physical activity?", 0, 14, 3)
        st.session_state.form_data['avg_daily_steps'] = st.number_input("217. Average daily step count (if known):", value=0)
        st.session_state.form_data['resting_heart_rate'] = st.number_input("217. Resting heart rate baseline (BPM):", value=0)
        st.session_state.form_data['estimated_vo2max'] = st.text_input("217. Estimated VO₂ Max performance metrics (if known):")

    st.markdown("---")
    st.markdown("#### Section 10, 11 & 12 — Sleep Metrics & Environmental Behaviors")
    sl1, sl2 = st.columns(2)
    with sl1:
        st.session_state.form_data['sleep_hours_night'] = st.slider("221. Average sleep duration hours per night?", 3.0, 12.0, 7.0, 0.5)
        st.session_state.form_data['sleep_caffeine_dependency'] = st.radio("242. Do you need caffeine to feel alert in the morning?", ["Never", "Occasionally", "Most days", "Every day"])
        st.session_state.form_data['sleep_support_used'] = st.multiselect("244. Active sleep aid products used:", ["Prescription medication", "Over-the-counter medication", "Melatonin", "Herbal supplements", "Relaxation techniques", "Meditation", "White noise", "CPAP device", "Nothing", "Other"])
    with sl2:
        st.session_state.form_data['tobacco_use'] = st.selectbox("Tobacco smoking or vaping lifestyle habits status?", ["Never smoked", "Ex-smoker", "Current user"])
        st.session_state.form_data['alcohol_servings_week'] = st.number_input("Standard units/servings of alcohol consumed weekly?", min_value=0, max_value=100, value=0)
        st.session_state.form_data['recreational_screen_time'] = st.selectbox("376. Recreational non-work screen time on a typical day?", ["Less than 2 hours", "2–4 hours", "5–7 hours", "More than 7 hours"])
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 5: SAVE & CLINICAL MATRIX OUTPUT
# ==========================================
with tab5:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Section 16 & 17 — Preventive Summary & Manifest Compilation")
    
    st.markdown("#### Preventive Care Planning Request Settings")
    st.session_state.form_data['preventive_support_targets'] = st.multiselect("399-400. Select fields for diagnostic preventive reporting support maps:", ["Weight management", "Cardiovascular disease prevention", "Diabetes prevention", "Cancer screening", "Vaccinations", "Healthy ageing", "Bone health", "Brain health", "Smoking cessation", "Physical activity", "Nutrition", "Mental wellbeing", "Sleep", "Women's health", "Men's health", "Unsure"])
    st.session_state.form_data['wants_to_prevent_top3'] = st.multiselect("402. What would you most like to proactively prevent in the future? (Mark up to three)", ["Heart disease", "Stroke", "Diabetes", "Cancer", "Osteoporosis or fractures", "Memory decline or dementia", "Loss of mobility", "Vision loss", "Chronic pain", "Frailty", "Other"])
    st.session_state.form_data['share_records_consent'] = st.radio("406. Willing to share historical external laboratory medical records with PRVNT?", ["Yes", "No", "Some records only"])
    
    st.markdown("---")
    st.markdown("#### Database Serialization Panel")
    st.info("Clicking the commit engine compiles all structural form elements into a centralized, data-pipeline compliant clinical dataset.")
    
    # Inject active execution context properties
    st.session_state.form_data['meta_elapsed_seconds'] = elapsed_seconds
    st.session_state.form_data['meta_submission_timestamp'] = str(datetime.now())
    
    # Generate unified export DataFrame payload structured for backend mapping
    master_df = pd.DataFrame([st.session_state.form_data])
    
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="📥 Export Full Intake Payload (JSON Manifest)",
            data=master_df.to_json(orient='records'),
            file_name=f"PRVNT_Master_Intake_Manifest_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )
    with col_dl2:
        st.download_button(
            label="📄 Export Structured Data Grid (Flat CSV)",
            data=master_df.to_csv(index=False),
            file_name=f"PRVNT_Master_Intake_Grid_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Live Operational Parameters Data View")
    st.dataframe(master_df.T, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
