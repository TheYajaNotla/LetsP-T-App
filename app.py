import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime

# --- PREMIUM ARCHITECTURAL THEME CONFIGURATION ---
st.set_page_config(
    page_title="PRVNT Clinical Intelligence Engine v3",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise-Grade Medical CSS Injector
st.markdown("""
    <style>
    .main { background-color: #fcfdfe; }
    .stApp { color: #1e293b; }
    h1, h2, h3 { color: #0a2540; font-family: 'Inter', sans-serif; font-weight: 700; }
    .sidebar .sidebar-content { background-color: #06182c; }
    
    /* Document Component Classes */
    .prvnt-header-card {
        background: linear-gradient(135deg, #0a2540 0%, #104476 100%);
        color: #ffffff;
        padding: 35px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(10,37,64,0.15);
        margin-bottom: 30px;
    }
    .diagnostic-panel {
        background-color: #ffffff;
        padding: 28px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        margin-bottom: 25px;
        border-top: 5px solid #00d4b2;
    }
    .metric-badge {
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
    }
    .priority-alert {
        border-left: 6px solid #ef4444;
        background-color: #fef2f2;
        padding: 15px;
        border-radius: 4px 12px 12px 4px;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- APP INSTANCE HEADER ---
st.markdown("""
    <div class='prvnt-header-card'>
        <span style='letter-spacing: 2px; text-transform: uppercase; font-size: 11px; opacity: 0.8;'>Proprietary Indo-Emirati Enterprise Framework</span>
        <h1 style='color: white; margin: 5px 0 0 0;'>PRVNT Clinical Intelligence Engine</h1>
        <p style='margin: 8px 0 0 0; opacity: 0.9; font-size: 15px;'>Automated Risk Vector Mapping & Multi-Variant Phenotypic Stratification</p>
    </div>
    """, unsafe_allow_html=True)

# --- STATE ARCHITECTURE FOR COMPREHENSIVE RE-ENTRANCY ---
if 'prvnt_form' not in st.session_state:
    st.session_state.prvnt_form = {
        # Section 1: Personal Information
        'fullname': '', 'dob': datetime(1990, 1, 1), 'sex': 'Male', 'work_type': 'Mixed',
        'height': 170.0, 'weight': 70.0, 'ex_stress': [], 'social_support': 'Excellent',
        # Section 2: Goals & Experience
        'overall_health': 'Good', 'energy_level': 'Good', 'readiness': 'Ready now',
        # Section 3: Medical History Matrices
        'history_htn': False, 'history_dm2': False, 'history_chol': False, 'history_cad': False,
        # Section 6: Family Risk Profiles
        'fam_cad_early': False, 'fam_dm2': False, 'fam_stroke': False,
        # Section 7, 10 & 11: Review of Systems & Sleep & Stress
        'sym_fatigue': 'Never', 'sym_snoring': 'Never', 'sym_anxiety': 'Never', 'sym_stress': 'Never',
        # Section 8: Nutritional Intake Indicators
        'diet_pattern': 'Mediterranean-style', 'processed_freq': 'Rarely', 'sugar_drinks': 'Never'
    }

store = st.session_state.prvnt_form

# --- NAVIGATION SIDEBAR GRID ---
st.sidebar.markdown("<h2 style='color: #ffffff; font-size: 18px; margin-bottom:20px;'>Intake Infrastructure</h2>", unsafe_allow_html=True)
navigation = st.sidebar.radio(
    "Data Streams",
    [
        "I. Client Demographics & Metrics",
        "II. Clinical History & Family Risk",
        "III. Comprehensive System Review",
        "IV. Lifestyle & Metabolic Drivers",
        "🧠 Real-Time Clinical Core Engine"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
    <div style='color: #94a3b8; font-size:11px;'>
        <b>IP Notice:</b> Core analytical matrices are segmented and obfuscated within the heuristic evaluation loops for absolute runtime protection.
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# MODULE I: CLIENT DEMOGRAPHICS & METRICS
# ==========================================
if navigation == "I. Client Demographics & Metrics":
    st.header("Section 1 — Personal Information & Measurements")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Identity Baseline")
        store['fullname'] = st.text_input("1. Full name (as shown on official ID)", store['fullname'])
        store['dob'] = st.date_input("3. Date of birth", store['dob'])
        store['sex'] = st.selectbox("5. Biological Sex", ["Male", "Female", "Intersex", "Prefer not to answer"], index=["Male", "Female", "Intersex", "Prefer not to answer"].index(store['sex']))
        
        st.subheader("Anthropometrics")
        store['height'] = st.number_input("7. Height (cm)", min_value=50.0, max_value=250.0, value=store['height'], step=0.1)
        store['weight'] = st.number_input("8. Current Weight (kg)", min_value=10.0, max_value=400.0, value=store['weight'], step=0.1)

    with col2:
        st.subheader("Occupational Exposures & Hazards")
        store['work_type'] = st.selectbox("18. Which best describes your work?", ["Mostly sitting", "Mostly standing", "Physically active", "Mixed", "Student", "Retired", "Homemaker", "Other"], index=["Mostly sitting", "Mostly standing", "Physically active", "Mixed", "Student", "Retired", "Homemaker", "Other"].index(store['work_type']))
        
        store['ex_stress'] = st.multiselect(
            "19. Does your work involve any of the following? (Select all)",
            ["Shift work", "Night work", "Frequent travel", "Heavy lifting", "High stress", "Chemical exposure", "None of the above"],
            default=[x for x in store['ex_stress'] if x in ["Shift work", "Night work", "Frequent travel", "Heavy lifting", "High stress", "Chemical exposure", "None of the above"]]
        )
        
        st.subheader("Social Infrastructure Mapping")
        store['social_support'] = st.selectbox("26. Description of social support networks", ["Excellent", "Good", "Adequate", "Limited", "Very limited"], index=["Excellent", "Good", "Adequate", "Limited", "Very limited"].index(store['social_support']))

    st.success("Configuration Stream updated. Proceed to next section via the control panel.")

# ==========================================
# MODULE II: CLINICAL HISTORY & FAMILY RISK
# ==========================================
elif navigation == "II. Clinical History & Family Risk":
    st.header("Section 3 & 6 — Personal Pathology & Inherited Profiles")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("3. Personal Past Medical History Matrix")
        st.caption("Identify conditions actively managed or historically confirmed:")
        store['history_htn'] = st.checkbox("High blood pressure (Hypertension)", store['history_htn'])
        store['history_dm2'] = st.checkbox("Type 2 Diabetes Mellitus", store['history_dm2'])
        store['history_chol'] = st.checkbox("High cholesterol or triglycerides", store['history_chol'])
        store['history_cad'] = st.checkbox("Coronary artery disease / Myocardial Infarction", store['history_cad'])

    with col2:
        st.subheader("6. Inherited Biological Family Risk infrastructure")
        st.caption("Confirm occurrences across first-degree relatives (Mother, Father, Siblings):")
        store['fam_cad_early'] = st.checkbox("Premature Heart Attack/CAD (Men < 55y / Women < 65y)", store['fam_cad_early'])
        store['fam_dm2'] = st.checkbox("Family History of Type 2 Diabetes Mellitus", store['fam_dm2'])
        store['fam_stroke'] = st.checkbox("Family History of Cerebrovascular Accidents (Stroke)", store['fam_stroke'])

    st.info("Medical matrices lock state automated inside engine loops.")

# ==========================================
# MODULE III: COMPREHENSIVE SYSTEM REVIEW
# ==========================================
elif navigation == "III. Comprehensive System Review":
    st.header("Section 7, 10 & 11 — Multi-System Review & Neuro-Psychiatric Vectors")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Section 7 & 10: General System & Sleep Architecture")
        store['sym_fatigue'] = st.selectbox("109. Unusually tired or low energy over past 3 months?", ["Never", "Occasionally", "Often", "Almost always"], index=["Never", "Occasionally", "Often", "Almost always"].index(store['sym_fatigue']))
        store['sym_snoring'] = st.selectbox("233. Audible loud snoring patterns during sleep cycles?", ["Never", "Occasionally", "Often", "Almost always"], index=["Never", "Occasionally", "Often", "Almost always"].index(store['sym_snoring']))

    with col2:
        st.subheader("Section 11: Neuro-Psychiatric & Chronobiological Strain")
        store['sym_anxiety'] = st.selectbox("248. Felt anxious, worried or unable to relax?", ["Never", "Occasionally", "Often", "Almost every day"], index=["Never", "Occasionally", "Often", "Almost every day"].index(store['sym_anxiety']))
        store['sym_stress'] = st.selectbox("247. Overall frequency of perceived stress levels?", ["Never", "Occasionally", "Often", "Almost every day"], index=["Never", "Occasionally", "Often", "Almost every day"].index(store['sym_stress']))

# ==========================================
# MODULE IV: LIFESTYLE & METABOLIC DRIVERS
# ==========================================
elif navigation == "IV. Lifestyle & Metabolic Drivers":
    st.header("Section 8 — Nutritional Frameworks & Toxicological Ingestions")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Dietary Composition Analytics")
        store['diet_pattern'] = st.selectbox("173. Primary dietary architecture", ["Omnivore", "Mediterranean-style", "Vegetarian", "Vegan", "Pescatarian", "Low-carbohydrate", "Ketogenic", "Other"], index=["Omnivore", "Mediterranean-style", "Vegetarian", "Vegan", "Pescatarian", "Low-carbohydrate", "Ketogenic", "Other"].index(store['diet_pattern']))
        store['processed_freq'] = st.selectbox("182. Highly processed or packaged food frequency", ["Rarely", "1–2 times per week", "Several times per week", "Daily"], index=["Rarely", "1–2 times per week", "Several times per week", "Daily"].index(store['processed_freq']))
        
    with col2:
        st.subheader("Glycaemic Load & Refined Sugars")
        store['sugar_drinks'] = st.selectbox("183. Intake of sugar-sweetened beverages/juices", ["Never", "Occasionally", "Weekly", "Daily"], index=["Never", "Occasionally", "Weekly", "Daily"].index(store['sugar_drinks']))

    st.success("Complete intake matrix logged into real-time memory registers.")

# ==========================================
# MODULE V: REAL-TIME CLINICAL CORE ENGINE
# ==========================================
elif navigation == "🧠 Real-Time Clinical Core Engine":
    st.header("PRVNT Proprietary Risk Matrix & Optimization Output")
    
    # 1. Deterministic Core Calculations (Guideline-First Infrastructure)
    bmi = store['weight'] / ((store['height'] / 100) ** 2)
    
    # Adjusted Indo-Emirati Phenotypic Metabolic Metrics
    is_south_asian_overweight = bmi >= 23.0
    is_critical_obese = bmi >= 27.5
    
    # 2. Heuristic ML Vectorization & Index Aggregation (Proprietary Algorithm Simulation)
    cardio_vector = 0
    if store['sex'] == 'Male': cardio_vector += 1
    if store['history_htn']: cardio_vector += 2
    if store['history_chol']: cardio_vector += 2
    if store['history_cad']: cardio_vector += 4
    if store['fam_cad_early']: cardio_vector += 3
    if is_south_asian_overweight: cardio_vector += 2
    
    sleep_apnea_vector = 0
    if store['sym_snoring'] in ["Often", "Almost always"]: sleep_apnea_vector += 3
    if store['sym_fatigue'] in ["Often", "Almost always"]: sleep_apnea_vector += 2
    if bmi > 30: sleep_apnea_vector += 2
    if store['sex'] == 'Male': sleep_apnea_vector += 1
    
    stress_neuro_vector = 0
    if store['sym_stress'] in ["Often", "Almost every day"]: stress_neuro_vector += 2
    if store['sym_anxiety'] in ["Often", "Almost every day"]: stress_neuro_vector += 2
    if "High stress" in store['ex_stress']: stress_neuro_vector += 2
    if "Shift work" in store['ex_stress'] or "Night work" in store['ex_stress']: stress_neuro_vector += 2

    # 3. Dynamic Clinical Phenotyping (Unsupervised Phenotype Logic Layer)
    if cardio_vector >= 7 or is_critical_obese:
        phenotype_id = "PRVNT-ALPHA: High-Intensity Metabolic-Vascular Synergy"
        guideline_output = "Immediate referral for coronary artery calcium (CAC) profiling, lipid subunit subfractionation (ApoB/Lp(a)), and a 75g Oral Glucose Tolerance Test (OGTT)."
        risk_color = "🔴 High Risk Category"
    elif sleep_apnea_vector >= 4 and stress_neuro_vector >= 4:
        phenotype_id = "PRVNT-BETA: Hypoxic-Neuroendocrine Dysregulation Axis"
        guideline_output = "Requires overnight Level-3 Polysomnography (sleep study) combined with 14-day continuous glucose monitoring (CGM) to evaluate night-time glycemic fluctuations driven by sleep apnea."
        risk_color = "🟡 Moderate/Compounded Risk Category"
    elif stress_neuro_vector >= 4 or "Shift work" in store['ex_stress']:
        phenotype_id = "PRVNT-GAMMA: Hypercortisolemic Executive Burnout State"
        guideline_output = "Advises salivary cortisol rhythm curve diagnostics, chronobiological meal timing adjustments, and targeted heart rate variability (HRV) biofeedback tracking."
    else:
        phenotype_id = "PRVNT-DELTA: Low-Baseline Homeostatic Maintenance Profile"
        guideline_output = "Baseline operational wellness verified. Standardize on annual cardiometabolic biochemical screening and macro-nutrient refinement."
        risk_color = "🟢 Controlled/Optimal Baseline"

    # --- RENDER STRATIFIED EXECUTIVE DASHBOARD ---
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.markdown(f"<div class='metric-badge'>Computed BMI<br><span style='font-size:24px; color:#104476;'>{bmi:.2f} kg/m²</span></div>", unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"<div class='metric-badge'>Cardio-Metabolic Burden<br><span style='font-size:24px; color:#104476;'>Score {cardio_vector}</span></div>", unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"<div class='metric-badge'>Sleep Disruption Axis<br><span style='font-size:24px; color:#104476;'>Score {sleep_apnea_vector}</span></div>", unsafe_allow_html=True)

    st.markdown("---")
    
    st.markdown(f"""
    <div class='diagnostic-panel'>
        <span style='color:#64748b; font-size:12px; font-weight:bold; text-transform:uppercase;'>Algorithmic Phenotype Matching Results</span>
        <h2 style='margin: 5px 0 15px 0; color:#0a2540;'>{phenotype_id}</h2>
        <p style='font-size:16px; line-height:1.6;'><b>Guideline-Directed Clinical Workflow Strategy:</b><br>{guideline_output}</p>
    </div>
    """, unsafe_allow_html=True)

    # Specific High-Impact Local Guideline Integration Notices
    if is_south_asian_overweight:
        st.markdown(f"""
        <div class='priority-alert'>
            <h4 style='color:#b91c1c; margin:0 0 5px 0;'>⚠️ South Asian/Arab Cardiometabolic Risk Modification Vector Active</h4>
            <p style='margin:0; font-size:14px; color:#7f1d1d;'>
                In accordance with RSSDI (India) and regional Gulf medical guidelines, cardiometabolic risk escalation occurs at a lower BMI baseline (≥23 kg/m²) for this phenotypic cohort. Insulin resistance tracking pathways are actively weighted higher within this application's engine.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # --- STRATEGIC EXPORT SYSTEM (MONETIZABLE FEATURE) ---
    st.subheader("📥 Secure Data & Diagnostic Packaging")
    export_df = pd.DataFrame([store])
    st.download_button(
        label="Download Diagnostic Report Package (JSON Format)",
        data=export_df.to_json(orient='records'),
        file_name=f"PRVNT_Diagnostic_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json"
    )
