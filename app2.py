import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

# --- PRVNT BRAND SYSTEM INITIALIZATION ---
st.set_page_config(
    page_title="PRVNT | Clinical Intelligence Intake",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- GOOGLE FONTS & BRAND EMBEDDED CUSTOM STYLING (PRVNT STYLE GUIDE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');
    
    /* Global Overrides matching PRVNT Palette */
    .stApp {
        background-color: #F7F7F7 !important; /* PRVNT Off-White */
        color: #0F0F0F !important; /* PRVNT True Black */
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Typography Overrides */
    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -1px !important;
        text-transform: uppercase;
        color: #0F0F0F !important;
    }
    
    /* Form Interactive Card Styling */
    .prvnt-hero {
        background: linear-gradient(135deg, #0E2A36 0%, #1F4E63 100%); /* PRVNT Midnight to Harbor Blue */
        color: #F7F7F7 !important;
        padding: 45px;
        border-radius: 0px; /* Minimalist raw edges */
        margin-bottom: 35px;
        border-left: 6px solid #90B7C6; /* Aqua Mist Accent */
    }
    
    .prvnt-card {
        background-color: #FFFFFF;
        padding: 30px;
        border: 1px solid #EFEFEF;
        border-radius: 4px;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(15,15,15,0.02);
    }
    
    /* Onboarding Milestones Navigation Progress Indicator */
    .progress-pill {
        background-color: #0E2A36;
        color: #F7F7F7;
        padding: 6px 14px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-right: 10px;
        border-radius: 2px;
    }
    
    /* Gamified Action Badges */
    .metric-bubble {
        background: #0E2A36;
        color: white;
        padding: 15px;
        text-align: center;
        border-radius: 4px;
        font-family: 'Space Grotesk', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# --- MULTI-STEP STATE REGISTRY & TEMPORAL BASELINE ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'responses' not in st.session_state:
    st.session_state.responses = {}

def advance_step():
    st.session_state.step += 1
    st.rerun()

def reverse_step():
    if st.session_state.step > 1:
        st.session_state.step -= 1
        st.rerun()

# --- HEADER FRAMEWORK ---
st.markdown(f"""
    <div class="prvnt-hero">
        <p style="letter-spacing: 3px; font-weight:700; font-size:12px; margin:0; text-transform:uppercase; color:#90B7C6;">
            Next-Gen Longevity Matrix
        </p>
        <h1 style="color:#F7F7F7 !important; margin:10px 0 0 0; font-size:38px;">PRVNT BIOLOGICAL ONBOARDING</h1>
        <p style="margin:10px 0 0 0; font-size:15px; opacity:0.85; font-family:'Plus Jakarta Sans';">
            Moving healthcare from reactive treatment to proactive prevention. Let's map your future.
        </p>
    </div>
""", unsafe_allow_html=True)

# Gamified Time Tracking Element
elapsed = round(time.time() - st.session_state.start_time)
m, s = divmod(elapsed, 60)

# --- PROGRESS SYSTEM CONTAINER ---
steps_titles = {
    1: "Identity Baseline",
    2: "Pathology & Hereditary Grid",
    3: "Biometrics & Lifestyle Velocity",
    4: "Cognitive State & System Review",
    5: "Diagnostic Phenotype Engine"
}

p_col1, p_col2 = st.columns([3, 1])
with p_col1:
    st.markdown(f"**Current Milestone:** <span class='progress-pill'>Phase {st.session_state.step}/5</span> *{steps_titles[st.session_state.step]}*", unsafe_allow_html=True)
with p_col2:
    st.markdown(f"<div style='text-align:right; font-size:13px; color:#1F4E63;'>⏱️ Intake Duration: <b>{m:02d}:{s:02d}</b></div>", unsafe_allow_html=True)

st.progress(st.session_state.step / 5)
st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# PHASE 1: IDENTITY BASELINE
# ==========================================
if st.session_state.step == 1:
    st.markdown("<div class='prvnt-card'>", unsafe_allow_html=True)
    st.subheader("Demographic Infrastructure Mapping")
    
    fullname = st.text_input("1. Full name (as shown on government-issued identification)?", 
                             value=st.session_state.responses.get('fullname', ''))
    
    dob = st.date_input("2. Date of Birth", 
                        value=st.session_state.responses.get('dob', datetime(1990, 1, 1)))
    
    sex = st.selectbox("3. Biological Sex Core Vector", 
                       ["Select...", "Male", "Female", "Intersex", "Prefer not to answer"],
                       index=["Select...", "Male", "Female", "Intersex", "Prefer not to answer"].index(st.session_state.responses.get('sex', 'Select...')))
    
    occupation = st.text_input("4. Primary focus or professional occupation?", 
                               value=st.session_state.responses.get('occupation', ''))
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("Authenticate Baseline & Proceed ➔"):
        if fullname and sex != "Select...":
            st.session_state.responses['fullname'] = fullname
            st.session_state.responses['dob'] = str(dob)
            st.session_state.responses['sex'] = sex
            st.session_state.responses['occupation'] = occupation
            advance_step()
        else:
            st.error("Please provide your Name and Biological Sex to lock your diagnostic registration profile.")

# ==========================================
# PHASE 2: PATHOLOGY & HEREDITARY GRID
# ==========================================
elif st.session_state.step == 2:
    st.markdown("<div class='prvnt-card'>", unsafe_allow_html=True)
    st.subheader("Personal & Inherited Health Background Matrices")
    st.caption("Select conditions actively managed or historically confirmed within your first-degree family trees:")
    
    # Personal Matrix Input
    st.markdown("**Personal Diagnostic Matrix History:**")
    h_htn = st.checkbox("High blood pressure (Hypertension)", value=st.session_state.responses.get('history_htn', False))
    h_dm2 = st.checkbox("Type 2 Diabetes Mellitus", value=st.session_state.responses.get('history_dm2', False))
    h_chol = st.checkbox("Dyslipidemia (High Cholesterol / Lipids)", value=st.session_state.responses.get('history_chol', False))
    h_cad = st.checkbox("Coronary Artery Disease / Early Myocardial Infarction", value=st.session_state.responses.get('history_cad', False))
    
    st.markdown("<hr style='border-color:#EFEFEF;'>", unsafe_allow_html=True)
    
    # Family Matrix Input
    st.markdown("**First-Degree Hereditary Risk Profiles:**")
    f_cad = st.checkbox("Premature Cardiovascular events (Male relatives < 55yrs, Female < 65yrs)", value=st.session_state.responses.get('fam_cad_early', False))
    f_dm2 = st.checkbox("Genetic lineage presenting Type 2 Diabetes", value=st.session_state.responses.get('fam_dm2', False))
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1: st.button("⬅ Go Back", on_click=reverse_step)
    with c2: 
        if st.button("Commit Family Grid & Advance ➔"):
            st.session_state.responses['history_htn'] = h_htn
            st.session_state.responses['history_dm2'] = h_dm2
            st.session_state.responses['history_chol'] = h_chol
            st.session_state.responses['history_cad'] = h_cad
            st.session_state.responses['fam_cad_early'] = f_cad
            st.session_state.responses['fam_dm2'] = f_dm2
            advance_step()

# ==========================================
# PHASE 3: BIOMETRICS & LIFESTYLE VELOCITY
# ==========================================
elif st.session_state.step == 3:
    st.markdown("<div class='prvnt-card'>", unsafe_allow_html=True)
    st.subheader("Physical Composition & Environmental Input Fields")
    
    col1, col2 = st.columns(2)
    with col1:
        height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=float(st.session_state.responses.get('height', 175.0)))
        weight = st.number_input("Current Weight (kg)", min_value=30.0, max_value=250.0, value=float(st.session_state.responses.get('weight', 75.0)))
    
    with col2:
        diet = st.selectbox("Predominant Dietary Architecture", 
                            ["Omnivore", "Mediterranean-style", "Plant-based / Vegetarian", "Low-Carb / Ketogenic", "Processed Standard Framework"],
                            index=["Omnivore", "Mediterranean-style", "Plant-based / Vegetarian", "Low-Carb / Ketogenic", "Processed Standard Framework"].index(st.session_state.responses.get('diet_pattern', 'Omnivore')))
        
        refined_sugars = st.selectbox("Refined Sugar / Sweetened Beverage Frequency Intake",
                                      ["Never", "Rarely (1-2 times per month)", "Weekly", "Daily"],
                                      index=["Never", "Rarely (1-2 times per month)", "Weekly", "Daily"].index(st.session_state.responses.get('sugar_drinks', 'Never')))

    st.markdown("</div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1: st.button("⬅ Go Back", on_click=reverse_step)
    with c2:
        if st.button("Authorize Biometrics & Advance ➔"):
            st.session_state.responses['height'] = height
            st.session_state.responses['weight'] = weight
            st.session_state.responses['diet_pattern'] = diet
            st.session_state.responses['sugar_drinks'] = refined_sugars
            advance_step()

# ==========================================
# PHASE 4: COGNITIVE STATE & SYSTEM REVIEW
# ==========================================
elif st.session_state.step == 4:
    st.markdown("<div class='prvnt-card'>", unsafe_allow_html=True)
    st.subheader("Neuro-Psychiatric & Chronobiological Strain Trackers")
    
    fatigue = st.select_slider("Unusually tired or low energy patterns over the past 3 months?", 
                               options=["Never", "Occasionally", "Often", "Almost always"],
                               value=st.session_state.responses.get('sym_fatigue', 'Never'))
    
    snoring = st.select_slider("Audible heavy snoring or disrupted oxygen breathing cycles?",
                               options=["Never", "Occasionally", "Often", "Almost always"],
                               value=st.session_state.responses.get('sym_snoring', 'Never'))
    
    stress = st.select_slider("Perceived frequency of work/life multi-variant stress burdens?",
                              options=["Never", "Occasionally", "Often", "Almost every day"],
                              value=st.session_state.responses.get('sym_stress', 'Never'))

    st.markdown("</div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1: st.button("⬅ Go Back", on_click=reverse_step)
    with c2:
        if st.button("Finalize All Clinical Data Streams ➔"):
            st.session_state.responses['sym_fatigue'] = fatigue
            st.session_state.responses['sym_snoring'] = snoring
            st.session_state.responses['sym_stress'] = stress
            advance_step()

# ==========================================
# PHASE 5: DIAGNOSTIC PHENOTYPE ENGINE
# ==========================================
elif st.session_state.step == 5:
    st.markdown("### 🧠 PRVNT Core Phenotypic Alignment Engine")
    
    # Deterministic BMI Calculation
    w_val = st.session_state.responses.get('weight', 70)
    h_val = st.session_state.responses.get('height', 170)
    bmi = w_val / ((h_val / 100) ** 2)
    
    # Real-Time Risk Matrix Scoring Calculations
    cardio_risk_score = 0
    if st.session_state.responses.get('history_htn'): cardio_risk_score += 2
    if st.session_state.responses.get('history_chol'): cardio_risk_score += 2
    if st.session_state.responses.get('fam_cad_early'): cardio_risk_score += 3
    if bmi >= 25.0: cardio_risk_score += 2
    
    # Phenotype Output Logic
    if cardio_risk_score >= 5:
        phenotype = "PRVNT-ALPHA: Metabolic-Vascular Synergy Vector"
        strategy = "Prioritize Advanced Lipid Subfractionation testing (ApoB), Coronary Artery Calcium (CAC) baseline imaging scan, and continuous metabolic mapping."
        status_color = "#b91c1c"
    elif st.session_state.responses.get('sym_snoring') in ["Often", "Almost always"] and st.session_state.responses.get('sym_fatigue') in ["Often", "Almost always"]:
        phenotype = "PRVNT-BETA: Hypoxic Sleep Architecture Alignment Needed"
        strategy = "Suggesting an overnight screening sleep study alongside targeted circadian re-alignment steps."
        status_color = "#d97706"
    else:
        phenotype = "PRVNT-STANDARD: Balance Proactive Preventative Track"
        strategy = "Continue structural longevity screenings annually. Maintain optimal protein allocation and standard micro-nutrient targets."
        status_color = "#059669"
        
    st.markdown(f"""
        <div style="background-color:#FFFFFF; padding:35px; border-radius:4px; border-top: 6px solid {status_color}; margin-bottom:25px;">
            <p style="color:#64748b; font-size:11px; font-weight:700; text-transform:uppercase; margin:0; letter-spacing:1px;">Matched Longevity Archetype</p>
            <h2 style="margin:5px 0 15px 0; color:#0F0F0F;">{phenotype}</h2>
            <p style="font-size:15px; line-height:1.6; color:#2d3748;"><b>Immediate Actionable Protocol Strategy:</b><br>{strategy}</p>
        </div>
    """, unsafe_allow_html=True)

    # Summary Panel Metrics
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.markdown(f"<div class='metric-bubble'>CALCULATED BMI BASELINE<br><span style='font-size:24px;'>{bmi:.2f} kg/m²</span></div>", unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"<div class='metric-bubble'>CARDIOVASCULAR BURDEN COMPUTE<br><span style='font-size:24px;'>Score: {cardio_risk_score}</span></div>", unsafe_allow_html=True)
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Secure JSON data download package representing a comprehensive pipeline structure
    st.session_state.responses['computed_bmi'] = bmi
    st.session_state.responses['cardio_score'] = cardio_risk_score
    st.session_state.responses['phenotype_id'] = phenotype
    st.session_state.responses['total_onboarding_seconds'] = elapsed
    
    export_df = pd.DataFrame([st.session_state.responses])
    
    st.download_button(
        label="📥 Download Onboarding Diagnostic Database Package (JSON)",
        data=export_df.to_json(orient='records'),
        file_name=f"PRVNT_Onboarding_Manifest_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json",
        use_container_width=True
    )
    
    if st.button("🔄 Restart Intake Framework"):
        st.session_state.step = 1
        st.session_state.start_time = time.time()
        st.session_state.responses = {}
        st.rerun()
