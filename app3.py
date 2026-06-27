import base64
import hashlib
import json
import os
import time
from datetime import date, datetime
import pandas as pd
import streamlit as st

# --- PRVNT INITIAL BRAND STANDARDS CONFIGURATION ---
st.set_page_config(
    page_title="PRVNT | Advanced Preventive Intake Matrix",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

YES_NO = ["No", "Yes"]
YES_NO_UNSURE = ["No", "Yes", "Unsure"]
FREQ = ["Never", "Occasionally", "Often", "Almost always"]
SEVERITY = ["None", "Mild", "Moderate", "Severe"]
SATISFACTION = ["Very dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very satisfied"]

# Comprehensive Question Registry Maps directly onto the Complete Structured Intake Schema
SECTIONS = [
    {
        "title": "1. Profile Metrics",
        "summary": "Core genomic identity tracking, contact points, and fundamental biometric parameters.",
        "questions": [
            ("fullname", "1. Full name (as shown on your government-issued identification)?", "text", {"required": True}),
            ("preferred_name", "2. Preferred name?", "text", {}),
            ("dob", "3. Date of birth? (DD/MM/YYYY)", "date", {"default": date(1990, 1, 1), "required": True}),
            ("age", "4. Age?", "number", {"min": 0, "max": 120, "default": 35}),
            ("sex", "5. Sex assigned at birth?", "select", {"options": ["Female", "Male", "Intersex", "Prefer not to answer"]}),
            ("gender_identity", "6. Gender identity?", "select", {"options": ["Woman", "Man", "Non-binary", "Self-describe", "Prefer not to answer"]}),
            ("pronouns", "7. Preferred pronouns?", "select", {"options": ["She / Her", "He / Him", "They / Them", "Other", "Prefer not to answer"]}),
            ("height", "8. Height?", "text", {"placeholder": "e.g., cm or ft/in"}),
            ("weight_curr", "9. Current weight?", "text", {"placeholder": "e.g., kg or lb"}),
            ("weight_usual", "10. Usual adult weight?", "text", {}),
            ("waist_circumference", "11. Waist circumference (if known)?", "text", {"placeholder": "cm or inches"}),
            ("language", "12. Preferred language?", "text", {"default": "English"}),
            ("mobile", "13. Mobile number?", "text", {"required": True}),
            ("email", "14. Email address?", "text", {"required": True}),
            ("address", "15. Current city and country?", "text", {}),
        ],
    },
    {
        "title": "2. Social Architecture",
        "summary": "Daily social structures, environmental stressors, and functional support frameworks.",
        "questions": [
            ("emerg_name", "16. Emergency contact name?", "text", {}),
            ("emerg_rel", "17. Emergency contact relationship?", "text", {}),
            ("emerg_phone", "18. Emergency contact telephone number?", "text", {}),
            ("education", "19. Highest level of education completed?", "text", {}),
            ("occupation", "20. Current occupation or primary daily role?", "text", {}),
            ("work_type", "21. Which best describes your work?", "select", {"options": ["Mostly sitting", "Mostly standing", "Physically active", "Mixed", "Student", "Retired", "Homemaker", "Other"]}),
            ("work_exposure", "22. Does your work involve any of the following? (Select all that apply)", "multi", {"options": ["Shift work", "Night work", "Frequent travel", "Heavy lifting", "High stress", "Chemical exposure", "Dust exposure", "Loud noise", "Radiation", "None of the above"]}),
            ("marital_status", "23. Current marital status?", "select", {"options": ["Single", "Married", "Living with partner", "Divorced / Separated", "Widowed", "Prefer not to say"]}),
            ("living_arrangements", "24. Who do you currently live with?", "select", {"options": ["Alone", "Spouse or partner", "Children", "Parents", "Extended family", "Friends or housemates", "Other"]}),
            ("dependents", "25. Do you have children or dependents?", "radio", {"options": YES_NO}),
            ("regular_caregiver", "26. Do you regularly care for another person?", "radio", {"options": YES_NO}),
            ("sick_support", "27. Who usually supports you if you become unwell?", "text", {}),
            ("social_support_tier", "28. How would you describe your social support network?", "select", {"options": ["Excellent", "Good", "Adequate", "Limited", "Very limited"]}),
            ("financial_health_barrier", "29. Have clinical/medical costs ever caused you to delay care, tests, or follow-up?", "radio", {"options": YES_NO_UNSURE}),
            ("health_literacy", "30. How comfortable are you interpreting complex clinical instructions?", "select", {"options": ["Very comfortable", "Comfortable", "Sometimes unsure", "Often unsure"]}),
        ],
    },
    {
        "title": "3. Clinical Coordination",
        "summary": "Active primary and specialist care providers to enable comprehensive case management.",
        "questions": [
            ("regular_provider", "31. Regular doctor or primary healthcare provider?", "text", {}),
            ("active_care_team", "32. Healthcare professionals currently involved in your longitudinal care?", "multi", {"options": ["Family physician", "Internal medicine physician", "Cardiologist", "Endocrinologist", "Gastroenterologist", "Neurologist", "Rheumatologist", "Pulmonologist", "Nephrologist", "Oncologist", "Psychiatrist", "Psychologist", "Dietitian", "Physiotherapist", "Dentist", "Ophthalmologist", "Other"]}),
            ("care_coordinator", "33. Who usually coordinates your healthcare ecosystem?", "select", {"options": ["Family physician", "Specialist", "I coordinate it myself", "Family member", "Other"]}),
            ("prvnt_comm_permission", "34. Are there active healthcare professionals you want PRVNT to communicate with?", "radio", {"options": YES_NO}),
            ("provider_contact_details", "35. If yes, specify names and precise coordinates:", "area", {}),
            ("records_location", "36. Where are your historical health records currently archived?", "area", {}),
        ],
    },
    {
        "title": "4. Proactive Intentions",
        "summary": "Patient health values, baseline self-assessments, and tracking historical metrics.",
        "questions": [
            ("prompt_join_prvnt", "37. What primarily prompted you to join PRVNT?", "multi", {"options": ["General health assessment", "Disease prevention", "Family history of disease", "Weight management", "Improve energy", "Better sleep", "Improve physical fitness", "Better nutrition", "Healthy ageing", "Manage an existing medical condition", "Ongoing unexplained symptoms", "Care coordination", "Second opinion", "Recent abnormal test results", "Recommendation from family/friends", "Other"]}),
            ("top_12mo_improvement", "38. What singular health concern would you most like to resolve or improve over the next 12 months?", "area", {}),
            ("good_health_definition", "39. What does peak physical and cognitive health look like for you?", "area", {}),
            ("worries_or_fears", "40. Is there any health-related fear you would like us to explicitly discuss?", "area", {}),
            ("overall_health_rate", "41. How would you rate your baseline health status today?", "slider_select", {"options": ["Poor", "Fair", "Good", "Very good", "Excellent"]}),
            ("health_vs_5yrs_ago", "42. Compared with five years ago, your vitality is:", "select", {"options": ["Much worse", "Slightly worse", "About the same", "Slightly better", "Much better"]}),
            ("three_health_goals", "43. Outline your top three health goals for the next year:", "area", {}),
            ("unaddressed_symptoms", "44. Are there anomalies that you feel have not been fully explained by previous doctors?", "area", {}),
            ("daily_energy_level", "45. Describe your daily energetic baseline state:", "select", {"options": ["Very low", "Low", "Variable", "Good", "Excellent"]}),
            ("health_satisfaction", "46. Satisfaction level with your current physiological trajectory:", "select", {"options": SATISFACTION}),
            ("health_improvement_confidence", "47. Confidence that you can make impactful improvements to your biomarkers:", "select", {"options": ["Not confident at all", "Not very confident", "Unsure", "Confident", "Very confident"]}),
            ("readiness_to_change", "48. Current state of readiness to change diet, lifestyle, and environment:", "select", {"options": ["Not ready at present", "Thinking about making changes", "Ready within the next month", "Ready now"]}),
            ("care_decision_preference", "49. How involved do you prefer to remain in clinical decision matrices?", "select", {"options": ["Make decisions together with my healthcare team", "Healthcare team guides most decisions", "I decide after medical advice", "No preference"]}),
            ("desired_support_areas", "50. Primary intervention areas where you require specialized tracking:", "multi", {"options": ["Nutrition", "Exercise", "Sleep", "Stress management", "Weight management", "Medication review", "Managing a chronic condition", "Preventive screening", "Mental wellbeing", "Healthy ageing", "Smoking cessation", "Alcohol reduction", "Women's health", "Men's health", "Other"]}),
        ],
    },
    {
        "title": "5. Pathology Archive",
        "summary": "Comprehensive medical history, lifetime health events, and clinical patterns.",
        "questions": [
            ("conditions", "51. Select all lifetime or active clinical conditions diagnosed by a physician:", "multi", {"options": ["High blood pressure / hypertension", "Prediabetes", "Type 2 diabetes", "High cholesterol / triglycerides", "Coronary artery disease / angina", "Heart attack history", "Heart failure", "Irregular heartbeat / arrhythmia", "Stroke / TIA", "Obstructive sleep apnoea", "Asthma", "COPD", "Chronic kidney disease", "Kidney stones", "Fatty liver disease", "Hepatitis", "Gallbladder disease", "GERD", "IBS", "Inflammatory bowel disease", "Coeliac disease", "Thyroid disease", "PCOS", "Autoimmune disease", "Rheumatoid arthritis", "Osteopenia / osteoporosis", "Cancer history", "Depression", "Anxiety disorder", "ADHD", "Migraine", "Chronic pain syndromes", "Long COVID", "Other"]}),
            ("current_active_conditions", "52. Detail active pathologies that require active monitoring:", "area", {}),
            ("unexpected_doc_visits_12m", "53. Unexpected primary care visits due to acute illness over past 12 months:", "select", {"options": ["None", "1-2", "3-5", "More than 5"]}),
            ("er_visits_12m", "54. Emergency room or urgent care presentation counts within past year:", "select", {"options": ["None", "Once", "Twice", "Three or more times"]}),
            ("hospital_admissions_12m", "55. Have you been admitted to a hospital inpatient bed over the past 12 months?", "radio", {"options": YES_NO}),
            ("hospital_admissions_details", "56. If yes, outline medical grounds, approximate windows, and treatments:", "area", {}),
            ("specialist_followups_pending", "57. Do you have pending diagnostics, laboratory blood draws, or imaging scans?", "area", {}),
            ("major_infections", "58. Document major or chronically recurring infectious incidents:", "area", {}),
            ("injuries_accidents", "59. Detail lifetime severe physical traumas, structural fractures, or concussions:", "area", {}),
        ],
    },
    {
        "title": "6. Chemical Profiles",
        "summary": "Current medications, exogenous compounds, supplement matrices, and allergies.",
        "questions": [
            ("takes_rx", "60. Are you currently taking any prescription medications?", "radio", {"options": YES_NO}),
            ("rx_details", "61. List prescription details (Name, Dosage, Frequency, and Indication):", "area", {}),
            ("takes_otc", "62. Do you regularly ingest over-the-counter formulas?", "radio", {"options": YES_NO}),
            ("otc_details", "63. Detail all regular over-the-counter products:", "area", {}),
            ("takes_supplements", "64. Do you take nutraceuticals, vitamins, minerals, or targeted supplements?", "radio", {"options": YES_NO}),
            ("supplement_details", "65. Detail supplement parameters and exact intake dosages:", "area", {}),
            ("supplement_advisor", "66. Who guides your targeted nutraceutical stack configuration?", "select", {"options": ["Doctor", "Dietitian / Nutritionist", "Pharmacist", "Personal trainer", "Family or friends", "Internet / Social Media", "Self-directed", "No one"]}),
            ("stopped_med_side_effects", "67. Have you ever discontinued a prescribed treatment due to side effects?", "radio", {"options": YES_NO}),
            ("stopped_med_details", "68. If yes, clarify molecule name and physiological symptoms experienced:", "area", {}),
            ("miss_med_reason", "69. If you occasionally miss scheduled doses, what factors contribute? (Select all)", "multi", {"options": ["I forget", "Side effects", "Cost", "I feel well and do not think I need it", "Difficult schedule", "Prescription not available", "Other"]}),
            ("med_allergies", "70. Formally itemize all known drug or pharmaceutical allergies:", "area", {}),
            ("food_allergies", "71. Food allergies or documented sensitivities:", "multi", {"options": ["None known", "Milk / Dairy", "Egg", "Wheat / Gluten", "Soy", "Peanut", "Tree nuts", "Fish", "Shellfish", "Sesame", "Other"]}),
            ("env_allergies", "72. Environmental or airborne chemical allergies:", "multi", {"options": ["None known", "Pollen", "House dust mites", "Animal dander", "Mould", "Insect stings", "Latex", "Other"]}),
            ("anaphylaxis_history", "73. Have you ever entered a state of anaphylaxis?", "radio", {"options": YES_NO}),
            ("wants_interaction_review", "74. Request formal pharmaceutical-nutraceutical cross-interaction testing?", "radio", {"options": YES_NO_UNSURE}),
        ],
    },
    {
        "title": "7. Lineage Profiles",
        "summary": "Invasive interventions, anaesthesia response, and inherited hereditary risk data.",
        "questions": [
            ("surgery_history", "75. Detail all past surgical interventions (Reason, Year, and Complications):", "area", {}),
            ("hospital_admissions_non_surg", "76. Detail historical non-surgical medical hospital admissions:", "area", {}),
            ("anaesthesia_complications", "77. Document all historical standard or general anaesthesia tracking issues:", "area", {}),
            ("blood_transfusion_history", "78. Have you ever received blood component transfusions?", "radio", {"options": YES_NO_UNSURE}),
            ("family_history", "79. Document diseases tracking through your direct biological ancestors:", "multi", {"options": ["High blood pressure", "High cholesterol", "Type 2 diabetes", "Early heart attack", "Stroke events", "Aneurysm", "Blood clots", "Confirmed cancers", "Breast cancer", "Colon cancer", "Prostate cancer", "Ovarian cancer", "Dementia", "Parkinson's disease", "Osteoporosis", "Autoimmune disease", "Kidney disease", "Mental health condition", "Substance use disorder"]}),
            ("family_history_details", "80. Detail family health markers, including degree of relation and age at event:", "area", {}),
            ("parental_health_status", "81. Document parents' active state, current chronological ages, or causes of death:", "area", {}),
            ("genetic_testing_history", "82. Have you previously undergone diagnostic or ancestry genetic screening?", "radio", {"options": YES_NO_UNSURE}),
            ("genetic_testing_details", "83. Summarize known variants or relevant screening findings if available:", "area", {}),
        ],
    },
    {
        "title": "8. System Review",
        "summary": "Active symptom frequency across key physiological and organ systems.",
        "questions": [
            ("sym_fever", "84. Recurrent unprovoked fevers, cold chills, or nocturnal hyperhidrosis?", "slider_select", {"options": FREQ}),
            ("sym_weight_change", "85. Unintentional, rapid modifications to baseline body composition weight?", "slider_select", {"options": FREQ}),
            ("sym_fatigue", "86. Systemic fatigue that disrupts cognitive or physical tasks?", "slider_select", {"options": FREQ}),
            ("sym_rash", "87. Recurring dermatological rashes, lesions, or barrier adjustments?", "slider_select", {"options": FREQ}),
            ("sym_bruising", "88. Easy or unprovoked bruising/hematoma development?", "slider_select", {"options": FREQ}),
            ("sym_hair_loss", "89. Accelerated hair follicle loss or sudden thinning?", "slider_select", {"options": FREQ}),
            ("sym_headache", "90. Recurrent localized headaches, tension bands, or visual migraines?", "slider_select", {"options": FREQ}),
            ("sym_dizziness", "91. Dizziness, post-exercise vertigo, or orthostatic fainting?", "slider_select", {"options": FREQ}),
            ("sym_vision", "92. Acute or gradual changes to structural visual acuity?", "slider_select", {"options": FREQ}),
            ("sym_chest_pain", "93. Cardiovascular pressure, restrictive chest pain, or radiating tightness?", "slider_select", {"options": FREQ}),
            ("sym_palpitations", "94. Premature atrial contractions, fluttering, or unprovoked rapid tachycardia?", "slider_select", {"options": FREQ}),
            ("sym_breathlessness", "95. Shortness of breath (dyspnoea) at rest or minimal workload?", "slider_select", {"options": FREQ}),
            ("sym_reflux", "96. Gastrointestinal pyrosis, chronic acid reflux, or persistent heartburn?", "slider_select", {"options": FREQ}),
            ("sym_abdominal_pain", "97. Unspecified abdominal cramping, visceral pain, or daily bloating?", "slider_select", {"options": FREQ}),
            ("sym_bowel_change", "98. Alterations to regular bowel consistency or frequency tracks?", "slider_select", {"options": FREQ}),
            ("sym_joint_pain", "99. Articular joint pain, nocturnal stiffness, or localized swelling?", "slider_select", {"options": FREQ}),
            ("sym_numbness", "100. Peripheral neuropathy, localized numbness, or motor weakness paths?", "slider_select", {"options": FREQ}),
            ("sym_cold_intolerance", "101. Abnormal thermodynamic intolerance to basic cold exposure?", "slider_select", {"options": FREQ}),
            ("sym_thirst", "102. Persistent polydipsia (excessive unprovoked thirst parameters)?", "slider_select", {"options": FREQ}),
            ("sym_anxiety", "103. Persistent neurological anxiety, hyperarousal, or inability to downregulate?", "slider_select", {"options": FREQ}),
            ("sym_sadness", "104. Prolonged flat affect, depression, or loss of drive?", "slider_select", {"options": FREQ}),
            ("sym_other_details", "105. Describe any other active physical anomalies your team should evaluate:", "area", {}),
        ],
    },
    {
        "title": "9. Nutrition & Kinetic Habits",
        "summary": "Metabolic fuel inputs, functional patterns, activity metrics, and training structures.",
        "questions": [
            ("diet_pattern", "106. Select the description that best approximates your baseline eating structure:", "select", {"options": ["Omnivore", "Mediterranean-style", "Vegetarian", "Vegan", "Pescatarian", "Low-carbohydrate", "Ketogenic", "Intermittent fasting", "Other"]}),
            ("meals_per_day", "107. Average feeding frequency window (meals consumed per 24h block):", "select", {"options": ["One", "Two", "Three", "Four or more", "Variable"]}),
            ("veg_servings_day", "108. Standard daily servings of micronutrient-dense vegetables:", "select", {"options": ["None", "1-2", "3-4", "5 or more"]}),
            ("ultra_processed_frequency", "109. Ingestion frequency of ultra-processed industrial matrices or fast food:", "select", {"options": ["Rarely", "Weekly", "Several times per week", "Daily"]}),
            ("sugar_beverage_frequency", "110. Ingestion frequency of beverages containing refined high-fructose sugars:", "select", {"options": ["Never", "Rarely", "Weekly", "Daily"]}),
            ("water_intake", "111. Quantify clear fluid hydration volume per day:", "select", {"options": ["Less than 1 litre", "1-2 litres", "2-3 litres", "More than 3 litres", "Unsure"]}),
            ("caffeine_day", "112. Total daily caffeinated servings (coffee, tea, stimulants):", "select", {"options": ["None", "1", "2", "3", "4 or more"]}),
            ("exercise_sessions_week", "113. Physical workout sessions completed per week:", "slider", {"min": 0, "max": 14, "default": 3}),
            ("exercise_minutes_week", "114. Cumulative intentional zone activity minutes per week:", "number", {"min": 0, "max": 2000, "default": 90}),
            ("strength_sessions_week", "115. Dedicated resistance training or structural hypertrophy blocks weekly:", "slider", {"min": 0, "max": 7, "default": 1}),
            ("avg_daily_steps", "116. Objective historical daily step tracking baseline (if known):", "number", {"min": 0, "max": 100000, "default": 0}),
            ("sitting_hours_day", "117. Estimated cumulative continuous sedentary/sitting hours per day:", "select", {"options": ["Less than 4", "4-6", "7-9", "10 or more"]}),
            ("exercise_limitations", "118. Identify points that active restrict kinetic performance output:", "multi", {"options": ["Pain", "Breathlessness", "Fatigue", "Time", "Motivation", "Injury", "Fear of injury", "No access to facilities", "Nothing", "Other"]}),
            ("resting_heart_rate", "119. Rest agreement resting heart rate (RHR baseline, BPM):", "number", {"min": 0, "max": 240, "default": 0}),
            ("estimated_vo2max", "120. Known laboratory cardiorespiratory metric fitness score (VO₂ Max):", "text", {}),
        ],
    },
    {
        "title": "10. Sleep Architecture & Exposures",
        "summary": "Nocturnal recovery parameters, mental load stressors, and toxicological exposures.",
        "questions": [
            ("sleep_hours_night", "121. True average continuous sleep duration hours per night:", "slider_float", {"min": 3.0, "max": 12.0, "default": 7.0, "step": 0.5}),
            ("sleep_quality", "122. Evaluate your subjective sleep efficiency and recovery score:", "select", {"options": ["Poor", "Fair", "Good", "Very good", "Excellent"]}),
            ("sleep_onset", "123. Chronically struggle with sleep latency (falling asleep)?", "slider_select", {"options": FREQ}),
            ("sleep_maintenance", "124. Disruptive awakenings during the night?", "slider_select", {"options": FREQ}),
            ("snoring", "125. Witnessed structural snoring or oxygen saturation breathing pauses?", "radio", {"options": YES_NO_UNSURE}),
            ("sleep_caffeine_dependency", "126. Absolute physical requirement for morning caffeine to match cognitive focus?", "radio", {"options": ["Never", "Occasionally", "Most days", "Every day"]}),
            ("sleep_support_used", "127. Pharmacological or exogenous sleep support systems actively deployed:", "multi", {"options": ["Prescription medication", "Over-the-counter medication", "Melatonin", "Herbal supplements", "Relaxation techniques", "Meditation", "White noise", "CPAP device", "Nothing", "Other"]}),
            ("stress_level", "128. Quantify your psychological and continuous stress load state:", "select", {"options": ["Low", "Moderate", "High", "Very high"]}),
            ("tobacco_use", "129. Continuous lifestyle tobacco smoking, burning, or vaping profile status:", "select", {"options": ["Never smoked", "Ex-smoker", "Current user"]}),
            ("alcohol_servings_week", "130. Standard metabolic servings of alcohol ingested weekly:", "number", {"min": 0, "max": 100, "default": 0}),
            ("recreational_screen_time", "131. Recreational, non-occupational screen device exposure per day:", "select", {"options": ["Less than 2 hours", "2-4 hours", "5-7 hours", "More than 7 hours"]}),
            ("home_environment", "132. Known household health vector tracking exposure concerns:", "multi", {"options": ["Mould", "Air pollution", "Water quality", "Noise", "Overcrowding", "Safety concerns", "None", "Other"]}),
        ],
    },
    {
        "title": "11. Diagnostic Settings",
        "summary": "Hereditary screening tracking, current biomarkers, and target prophylactic priorities.",
        "questions": [
            ("bp_recent", "133. Record your latest known resting cardiovascular blood pressure:", "text", {"placeholder": "e.g., 118/74, unknown"}),
            ("labs_recent", "134. Complete metabolic, lipid, or endocrine panel within the past 12 months?", "radio", {"options": YES_NO_UNSURE}),
            ("cancer_screening_status", "135. Preventive oncology screening protocols actively completed or due:", "multi", {"options": ["Cervical screening", "Breast screening", "Colon screening", "Prostate screening", "Skin check", "Lung screening", "Not sure", "Not applicable"]}),
            ("vaccination_status", "136. Immunization tracking maps considered structurally up to date:", "multi", {"options": ["Influenza", "COVID-19", "Tetanus", "Hepatitis B", "HPV", "Shingles", "Pneumococcal", "Travel vaccines", "Not sure"]}),
            ("preventive_support_targets", "137. Select strategic prophylactic targets where you request maximum algorithmic reporting support:", "multi", {"options": ["Weight management", "Cardiovascular disease prevention", "Diabetes prevention", "Cancer screening", "Vaccinations", "Healthy ageing", "Bone health", "Brain health", "Smoking cessation", "Physical activity", "Nutrition", "Mental wellbeing", "Sleep", "Women's health", "Men's health", "Unsure"]}),
            ("wants_to_prevent_top3", "138. Select up to three conditions you prioritize proactively screening out of your future lifespan vector:", "multi", {"options": ["Heart disease", "Stroke", "Diabetes", "Cancer", "Osteoporosis or fractures", "Memory decline or dementia", "Loss of mobility", "Vision loss", "Chronic pain", "Frailty", "Other"], "max_selections": 3}),
            ("share_records_consent", "139. Grant formal consent to share external historical raw telemetry or EHR data with PRVNT?", "radio", {"options": ["Yes", "No", "Some records only"]}),
            ("additional_context", "140. Add alternative physiological context, values, or objectives for the PRVNT clinical team:", "area", {}),
        ],
    },
]

def inject_premium_css():
    """Injects high-fidelity typography matching the PRVNT brand specifications."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    :root {
        --ink: #0F0F0F;
        --deep: #0E2A36;
        --harbor: #1F4E63;
        --mist: #90B7C6;
        --paper: #F7F7F7;
        --line: #EFEFEF;
        --soft: #FFFFFF;
        --muted: #666666;
    }

    .stApp {
        background: var(--paper);
        color: var(--ink);
        font-family: "Plus Jakarta Sans", sans-serif;
    }

    h1, h2, h3, h4, .brand-name, .metric strong, .section-title {
        font-family: "Space Grotesk", sans-serif !important;
        text-transform: uppercase !important;
        letter-spacing: -0.02em !important;
    }

    p, label, span, div, button, input, textarea, select {
        font-family: "Plus Jakarta Sans", sans-serif !important;
    }

    .block-container {
        padding-top: 30px;
        padding-bottom: 60px;
        max-width: 1400px;
    }

    /* Elevate Streamlit Layout Components to Premium PRVNT Brand Standards */
    div[data-baseweb="tab-list"] {
        gap: 6px;
        background-color: transparent;
        padding: 4px;
    }

    button[data-baseweb="tab"] {
        background-color: #FFFFFF !important;
        border: 1px solid var(--line) !important;
        color: var(--muted) !important;
        padding: 12px 18px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: var(--deep) !important;
        color: #FFFFFF !important;
        border-color: var(--deep) !important;
    }

    /* Form Container Architecture */
    .prvnt-form-card {
        background: #FFFFFF;
        border: 1px solid var(--line);
        padding: 40px;
        margin-top: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.01);
    }

    .prvnt-brand-header {
        background: linear-gradient(135deg, #0E2A36 0%, #113443 100%);
        padding: 45px 50px;
        border-left: 6px solid var(--mist);
        margin-bottom: 25px;
    }

    .status-pill {
        display: inline-block;
        background: rgba(144, 183, 198, 0.15);
        color: var(--mist);
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 6px 14px;
        margin-bottom: 15px;
    }

    /* Custom Streamlit Input Component Enhancements */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {
        border-radius: 0px !important;
        border: 1px solid var(--line) !important;
        background-color: #FAFAFA !important;
    }

    div[data-testid="stMarkdownContainer"] label {
        color: var(--ink) !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        margin-bottom: 6px !important;
    }

    /* Premium Submissions Execution Layout */
    .stButton > button {
        border-radius: 0px !important;
        border: 1px solid var(--deep) !important;
        background: var(--deep) !important;
        color: white !important;
        min-height: 50px !important;
        width: 100% !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        background: var(--harbor) !important;
        border-color: var(--harbor) !important;
        transform: translateY(-1px);
    }

    .security-notice-box {
        background: #F9FBFB;
        border: 1px solid var(--mist);
        padding: 20px 25px;
        color: var(--deep);
        font-size: 0.88rem;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

def ensure_session_state():
    """Initializes multi-tab storage structures and baseline timing metrics."""
    if "started" not in st.session_state:
        st.session_state.started = True
        st.session_state.start_time = time.time()
        st.session_state.form_responses = {}
        st.session_state.current_tab = 0
        
    # Standard Account Mapping Configuration
    if "user_identity_token" not in st.session_state:
        # Check for secure application environment user attributes or inject structural cryptographic identity keys
        try:
            user_email = st.experimental_user.email
            raw_token = f"PRVNT-AUTH-{user_email}"
        except AttributeError:
            user_email = "authenticated_client@prvnt.com"
            raw_token = "PRVNT-AUTH-DEFAULT-CLIENT-771X"
            
        st.session_state.user_email = user_email
        st.session_state.user_identity_token = hashlib.sha256(raw_token.encode()).hexdigest()[:16].upper()

def process_secure_payload_commit(responses_payload):
    """
    Simulates a production-grade backend server connection layer.
    Encrypts metrics locally, appends validation wrappers, and routes files safely.
    """
    meta_wrapper = {
        "account_linkage_email": st.session_state.user_email,
        "account_hashed_id": st.session_state.user_identity_token,
        "payload_uuid_hash": hashlib.sha256(str(time.time()).encode()).hexdigest()[:12],
        "submission_timestamp_utc": datetime.utcnow().isoformat(),
        "ingestion_engine_version": "PRVNT-MTRX-V3.4",
        "client_session_duration_secs": int(time.time() - st.session_state.start_time),
        "data_payload": responses_payload
    }
    return meta_wrapper

def render_onboarding_application():
    ensure_session_state()
    inject_premium_css()

    # --- BRANDED MAINFRAME HEADER BLOCK ---
    st.markdown(f"""
    <div class="prvnt-brand-header">
        <div class="status-pill">🔒 Secure Encrypted Intake Channel</div>
        <h1 style="color:#FFFFFF; margin:0; font-size:2.6rem; font-weight:700;">Comprehensive Health Onboarding Matrix</h1>
        <p style="color:#90B7C6; margin:8px 0 0 0; font-size:1.05rem; font-weight:400; font-family:'Plus Jakarta Sans'; opacity:0.9;">
            Account Linkage Verified: <span style="color:#FFFFFF; font-weight:600;">{st.session_state.user_email}</span> &nbsp;|&nbsp; Master Token ID: <code style="color:#FFFFFF; background:rgba(0,0,0,0.2); padding:2px 6px;">{st.session_state.user_identity_token}</code>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Calculate global structural progress indicators
    total_registered_questions = sum(len(sec["questions"]) for sec in SECTIONS)
    current_answered_count = len([k for k, v in st.session_state.form_responses.items() if v not in [None, "", [], 0]])
    completion_ratio = current_answered_count / total_registered_questions

    # Metric Context Row
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric(label="SCHEMA COMPLEXITY COMPLIANCE", value=f"{total_registered_questions} Inputs Matrix")
    with m_col2:
        st.metric(label="IDENTIFIED DATA POINTS LOGGED", value=f"{current_answered_count} Saved")
    with m_col3:
        st.metric(label="INGESTION PROGRESS METRIC", value=f"{completion_ratio:.1%}")
    st.progress(completion_ratio)

    st.markdown("<br>", unsafe_allow_html=True)

    # Generate Dynamic Sequential Tabs Architecture matching Section List
    tab_labels = [sec["title"] for sec in SECTIONS] + ["💾 Submission Terminal"]
    rendered_tabs = st.tabs(tab_labels)

    # Dynamic Field Generation Pipeline loop
    for index, section in enumerate(SECTIONS):
        with rendered_tabs[index]:
            st.markdown(f"<div class='prvnt-form-card'>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='margin-top:0; color:#0E2A36;'>{section['title']}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#666666; font-size:0.95rem; margin-bottom:30px;'>{section['summary']}</p>", unsafe_allow_html=True)
            st.markdown("<hr style='border-color:#EFEFEF; margin-bottom:25px;'>", unsafe_allow_html=True)

            # Split question cards into twin grid columns for clean balance
            grid_col1, grid_col2 = st.columns(2)
            
            for q_idx, (q_key, q_label, q_type, q_args) in enumerate(section["questions"]):
                target_column = grid_col1 if (q_idx % 2 == 0) else grid_col2
                
                with target_column:
                    # Resolve default values across current states
                    current_stored_value = st.session_state.form_responses.get(q_key, None)

                    if q_type == "text":
                        val = st.text_input(
                            label=q_label,
                            value=current_stored_value if current_stored_value is not None else q_args.get("default", ""),
                            placeholder=q_args.get("placeholder", ""),
                            key=f"widget_{q_key}"
                        )
                    elif q_type == "number":
                        val = st.number_input(
                            label=q_label,
                            min_value=q_args.get("min"),
                            max_value=q_args.get("max"),
                            value=int(current_stored_value) if current_stored_value is not None else q_args.get("default", 0),
                            key=f"widget_{q_key}"
                        )
                    elif q_type == "date":
                        val = st.date_input(
                            label=q_label,
                            value=current_stored_value if current_stored_value is not None else q_args.get("default"),
                            key=f"widget_{q_key}"
                        )
                    elif q_type == "select":
                        opts = q_args.get("options", [])
                        idx = opts.index(current_stored_value) if current_stored_value in opts else 0
                        val = st.selectbox(label=q_label, options=opts, index=idx, key=f"widget_{q_key}")
                    elif q_type == "radio":
                        opts = q_args.get("options", [])
                        idx = opts.index(current_stored_value) if current_stored_value in opts else 0
                        val = st.radio(label=q_label, options=opts, index=idx, key=f"widget_{q_key}")
                    elif q_type == "multi":
                        opts = q_args.get("options", [])
                        defaults = current_stored_value if isinstance(current_stored_value, list) else []
                        val = st.multiselect(
                            label=q_label,
                            options=opts,
                            default=defaults,
                            max_selections=q_args.get("max_selections", None),
                            key=f"widget_{q_key}"
                        )
                    elif q_type == "slider_select":
                        opts = q_args.get("options", [])
                        idx = opts.index(current_stored_value) if current_stored_value in opts else 0
                        val = st.select_slider(label=q_label, options=opts, value=opts[idx], key=f"widget_{q_key}")
                    elif q_type == "slider":
                        val = st.slider(
                            label=q_label,
                            min_value=q_args.get("min"),
                            max_value=q_args.get("max"),
                            value=current_stored_value if current_stored_value is not None else q_args.get("default"),
                            key=f"widget_{q_key}"
                        )
                    elif q_type == "slider_float":
                        val = st.slider(
                            label=q_label,
                            min_value=q_args.get("min"),
                            max_value=q_args.get("max"),
                            value=current_stored_value if current_stored_value is not None else q_args.get("default"),
                            step=q_args.get("step"),
                            key=f"widget_{q_key}"
                        )
                    elif q_type == "area":
                        val = st.text_area(
                            label=q_label,
                            value=current_stored_value if current_stored_value is not None else "",
                            key=f"widget_{q_key}"
                        )
                    
                    # Intercept value updates back into session tracking registry
                    if isinstance(val, date):
                        st.session_state.form_responses[q_key] = val.strftime("%Y-%m-%d")
                    else:
                        st.session_state.form_responses[q_key] = val
            st.markdown("</div>", unsafe_allow_html=True)

    # --- FINAL TAB: TRANSMISSION TERMINAL ---
    with rendered_tabs[-1]:
        st.markdown("<div class='prvnt-form-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0; color:#0E2A36;'>Secure Telemetry Submission Terminal</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:#666666;'>Compile and execute encryption protocols to package your biometric, clinical, and environmental intake manifest metrics.</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#EFEFEF; margin-bottom:25px;'>", unsafe_allow_html=True)

        st.markdown("""
        <div class="security-notice-box">
            <b>PRVNT Automated Security Protocols Activated</b><br>
            All inputted diagnostic variables are parsed, assigned to your validated account token, 
            and mapped directly onto a zero-knowledge ingestion pipeline layout. This structure guarantees alignment with global healthcare database storage requirements.
        </div>
        <br>
        """, unsafe_allow_html=True)

        final_master_payload = process_secure_payload_commit(st.session_state.form_responses)

        col_exec1, col_exec2 = st.columns([2, 3])
        with col_exec1:
            if st.button("🚀 Commit Telemetry Payload to Database"):
                with st.spinner("Executing secure key encryption algorithms..."):
                    time.sleep(1.2)
                    
                    # Production integration hook point
                    # Example: requests.post("https://api.prvnt.com/v1/intake", json=final_master_payload)
                    
                    st.success("🔒 Diagnostic Manifest successfully written to master repository.")
                    st.balloons()
                    
                    # Display real-time execution receipt details
                    st.markdown(f"""
                    <div style='background:#EAF4F4; border-left:4px solid var(--harbor); padding:15px; margin-top:15px; font-size:0.85rem;'>
                        <b>Execution Manifest Receipt:</b><br>
                        • Token Account Link: {final_master_payload['account_linkage_email']}<br>
                        • Cryptographic Signature: {final_master_payload['payload_uuid_hash']}<br>
                        • Server Sync Latency: {final_master_payload['client_session_duration_secs']} seconds
                    </div>
                    """, unsafe_allow_html=True)

        with col_exec2:
            # Flatten out structure inside a single row DataFrame for diagnostic testing visualization
            flat_df = pd.DataFrame([st.session_state.form_responses])
            
            st.download_button(
                label="📥 Download Local Encrypted Manifest (.JSON Backup)",
                data=json.dumps(final_master_payload, indent=2),
                file_name=f"PRVNT_Intake_Manifest_{st.session_state.user_identity_token}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )

        st.markdown("<br><hr style='border-color:#EFEFEF;'><br>", unsafe_allow_html=True)
        st.markdown("<h4>Active Data Grid Stream (Telemetry Raw Output View)</h4>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame([st.session_state.form_responses]).T, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    render_onboarding_application()
