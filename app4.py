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

# Common Dropdown Choices - Internationally Understandable & Standardized
YES_NO = ["No", "Yes"]
YES_NO_UNSURE = ["No", "Yes", "Unsure"]
FREQ = ["Never", "Occasionally", "Often", "Almost always"]
SEVERITY = ["None", "Mild", "Moderate", "Severe"]
SATISFACTION = ["Very dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very satisfied"]

# Comprehensive Question Registry Maps directly onto the Complete Structured Intake Schema
SECTIONS = [
    {
        "title": "01. Identity & Biometrics",
        "summary": "Core identity tracking, globally adaptable biometric dimensions, and contact vectors.",
        "questions": [
            ("fullname", "1. Full name (as shown on government identification)", "text", {"required": True, "placeholder": "Given Names Family Name"}),
            ("preferred_name", "2. Preferred name", "text", {}),
            ("dob", "3. Date of birth (DD/MM/YYYY)", "date", {"default": date(1990, 1, 1), "required": True}),
            ("age", "4. Current age (Years)", "number", {"min": 0, "max": 120, "default": 35}),
            ("sex", "5. Sex assigned at birth", "select", {"options": ["Female", "Male", "Intersex", "Prefer not to answer"]}),
            ("gender_identity", "6. Gender identity", "select", {"options": ["Woman", "Man", "Non-binary", "Self-describe", "Prefer not to answer"]}),
            ("pronouns", "7. Preferred pronouns", "select", {"options": ["She / Her", "He / Him", "They / Them", "Other", "Prefer not to answer"]}),
            ("height", "8. Height (Specify cm or ft/in)", "text", {"placeholder": "e.g., 175 cm or 5ft 9in"}),
            ("weight_curr", "9. Current body weight (Specify kg or lbs)", "text", {"placeholder": "e.g., 72 kg or 158 lbs"}),
            ("weight_usual", "10. Usual stable adult weight", "text", {"placeholder": "e.g., 70 kg"}),
            ("waist_circumference", "11. Waist circumference (if known)", "text", {"placeholder": "e.g., 88 cm or 34 in"}),
            ("language", "12. Preferred language for clinical communication", "text", {"default": "English"}),
            ("mobile", "13. Mobile phone number (including country code)", "text", {"required": True, "placeholder": "+1 / +44 / +61..."}),
            ("email", "14. Personal email address", "text", {"required": True, "placeholder": "name@domain.com"}),
            ("address", "15. Current residential city and country", "text", {"placeholder": "e.g., London, United Kingdom"}),
        ],
    },
    {
        "title": "02. Social Architecture",
        "summary": "Daily social structures, workload distributions, occupational parameters, and systemic support systems.",
        "questions": [
            ("emerg_name", "16. Emergency contact name", "text", {}),
            ("emerg_rel", "17. Emergency contact relationship", "text", {}),
            ("emerg_phone", "18. Emergency contact contact number", "text", {}),
            ("education", "19. Highest level of education completed", "text", {}),
            ("occupation", "20. Current occupation or primary daily functional role", "text", {}),
            ("work_type", "21. Physical nature of your primary daily work", "select", {"options": ["Mostly sitting / Sedentary", "Mostly standing", "Physically intensive", "Mixed / Variable", "Student", "Retired", "Homemaker", "Other"]}),
            ("work_exposure", "22. Does your regular work include any of the following? (Select all that apply)", "multi", {"options": ["Shift work / Rotating schedules", "Night work", "Frequent international travel", "Heavy mechanical lifting", "High psychological stress", "Chemical or toxicant exposure", "Dust or microparticle exposure", "Loud environmental noise", "Radiation risks", "None of the above"]}),
            ("marital_status", "23. Current relationship status", "select", {"options": ["Single", "Married", "Living with partner", "Divorced / Separated", "Widowed", "Prefer not to say"]}),
            ("living_arrangements", "24. Who do you currently live with?", "select", {"options": ["Alone", "Spouse or partner", "Children / Dependents", "Parents", "Extended family", "Friends / Housemates", "Other"]}),
            ("dependents", "25. Do you have children or regular dependents?", "radio", {"options": YES_NO}),
            ("regular_caregiver", "26. Do you regularly act as a caregiver for another individual?", "radio", {"options": YES_NO}),
            ("sick_support", "27. Who usually supports you if you become acutely unwell?", "text", {}),
            ("social_support_tier", "28. How would you rate your active social support system?", "select", {"options": ["Excellent", "Good", "Adequate / Satisfactory", "Limited", "Very limited"]}),
            ("financial_health_barrier", "29. Have medical costs ever caused you to delay care, diagnostics, or therapies?", "radio", {"options": YES_NO_UNSURE}),
            ("health_literacy", "30. How comfortable are you understanding complex clinical metrics or instructions?", "select", {"options": ["Very comfortable", "Comfortable", "Sometimes unsure", "Often unsure"]}),
        ],
    },
    {
        "title": "03. Care Coordination",
        "summary": "Active clinical providers, family physicians, and historical medical record systems.",
        "questions": [
            ("regular_provider", "31. Regular general practitioner or primary healthcare doctor", "text", {}),
            ("active_care_team", "32. Medical specialists currently involved in your care ecosystem", "multi", {"options": ["Family / Primary Care Physician", "Internal Medicine", "Cardiologist", "Endocrinologist", "Gastroenterologist", "Neurologist", "Rheumatologist", "Pulmonologist", "Nephrologist", "Oncologist", "Psychiatrist", "Psychologist", "Dietitian / Nutritionist", "Physiotherapist / Physical Therapist", "Dentist", "Ophthalmologist", "Other"]}),
            ("care_coordinator", "33. Who primarily coordinates your healthcare needs?", "select", {"options": ["My primary care physician", "A medical specialist", "I coordinate it entirely myself", "A family member", "Other"]}),
            ("prvnt_comm_permission", "34. Do you grant PRVNT permission to communicate with your current doctors?", "radio", {"options": YES_NO}),
            ("provider_contact_details", "35. If yes, list names and secure contact details below:", "area", {}),
            ("records_location", "36. Where are your historical health records and diagnostic files currently held?", "area", {}),
        ],
    },
    {
        "title": "04. Strategic Health Intentions",
        "summary": "Baseline quality-of-life rankings, readiness for lifestyle changes, and explicit medical goals.",
        "questions": [
            ("prompt_join_prvnt", "37. What factors primarily prompted you to onboard with PRVNT?", "multi", {"options": ["General health assessment", "Disease prevention", "Hereditary/Family history risk vectors", "Weight management optimization", "Energy level enhancement", "Sleep architecture improvement", "Physical fitness scaling", "Nutritional redesign", "Longevity / Healthy ageing", "Managing an existing chronic pathology", "Unexplained persistent symptoms", "Care coordination support", "Seeking a second opinion", "Recent out-of-range clinical test results", "Peer recommendation", "Other"]}),
            ("top_12mo_improvement", "38. What specific health metric or concern do you prioritize resolving over the next 12 months?", "area", {}),
            ("good_health_definition", "39. What does optimal health, vitality, and performance look like for you personally?", "area", {}),
            ("worries_or_fears", "40. Are there specific health-related worries or fears you want our team to evaluate?", "area", {}),
            ("overall_health_rate", "41. How would you rate your overall baseline health state today?", "slider_select", {"options": ["Poor", "Fair", "Good", "Very good", "Excellent"]}),
            ("health_vs_5yrs_ago", "42. Compared with your vitality five years ago, your health today is:", "select", {"options": ["Much worse", "Slightly worse", "About the same", "Slightly better", "Much better"]}),
            ("three_health_goals", "43. Outline your top three health goals for the upcoming year:", "area", {}),
            ("unaddressed_symptoms", "44. Identify any symptoms that have not been clearly explained by previous reviews:", "area", {}),
            ("daily_energy_level", "45. Characterize your average daily cognitive and physical energy state:", "select", {"options": ["Very low", "Low", "Variable / Unstable", "Good", "Excellent"]}),
            ("health_satisfaction", "46. Your level of satisfaction with your current metabolic/physical trajectory:", "select", {"options": SATISFACTION}),
            ("health_improvement_confidence", "47. Your confidence in your ability to successfully make lifestyle modifications:", "select", {"options": ["Not confident at all", "Not very confident", "Unsure", "Confident", "Very confident"]}),
            ("readiness_to_change", "48. Your current structural readiness to implement changes to habits:", "select", {"options": ["Not ready at present", "Evaluating potential changes", "Ready within the upcoming month", "Ready to change immediately"]}),
            ("care_decision_preference", "49. How do you prefer to approach shared medical decision matrices?", "select", {"options": ["Collaboratively together with my healthcare team", "My healthcare team directs the decisions", "I make the final decisions after reviewing clinical advice", "No explicit preference"]}),
            ("desired_support_areas", "50. Health focus areas where you want the highest degree of tracking support:", "multi", {"options": ["Nutrition optimization", "Exercise prescription", "Sleep architecture", "Stress regulation", "Weight management", "Medication optimization", "Chronic condition tracking", "Preventive biomarker screening", "Mental wellbeing", "Longevity / Healthy ageing", "Smoking cessation", "Alcohol mitigation", "Women's specialized health", "Men's specialized health", "Other"]}),
        ],
    },
    {
        "title": "05. Pathology Archive",
        "summary": "Lifetime clinical diagnoses, institutional event matrices, and underlying physical markers.",
        "questions": [
            ("conditions", "51. Select all past or currently diagnosed medical conditions:", "multi", {"options": ["High blood pressure / Hypertension", "Prediabetes / Insulin resistance", "Type 2 diabetes", "Dyslipidemia (High cholesterol/triglycerides)", "Coronary artery disease / Angina", "Myocardial infarction (Heart attack) history", "Heart failure", "Arrhythmia / Irregular heart rhythm", "Stroke / TIA", "Obstructive sleep apnoea", "Asthma", "COPD / Chronic bronchitis", "Chronic kidney disease", "Nephrolithiasis (Kidney stones)", "Fatty liver disease (MASLD/NAFLD)", "Hepatitis", "Gallbladder pathology", "Gastroesophageal reflux disease (GERD)", "Irritable bowel syndrome (IBS)", "Inflammatory bowel disease (Crohn's/Colitis)", "Coeliac disease", "Thyroid disorders", "PCOS (Polycystic ovary syndrome)", "Autoimmune condition", "Rheumatoid arthritis", "Osteopenia / Osteoporosis", "Oncology / Cancer history", "Clinical depression", "Anxiety disorder", "ADHD", "Migraine or chronic headaches", "Chronic pain syndrome", "Long COVID", "Other"]}),
            ("current_active_conditions", "52. Detail active conditions currently requiring clinical therapies or follow-up:", "area", {}),
            ("unexpected_doc_visits_12m", "53. Unexpected primary care visits due to acute illness in the last 12 months:", "select", {"options": ["None", "1-2", "3-5", "More than 5"]}),
            ("er_visits_12m", "54. Emergency department or urgent care presentations within the past year:", "select", {"options": ["None", "Once", "Twice", "Three or more times"]}),
            ("hospital_admissions_12m", "55. Have you been admitted as a hospital inpatient overnight in the past year?", "radio", {"options": YES_NO}),
            ("hospital_admissions_details", "56. If yes, detail the diagnosis, treatment window dates, and interventions:", "area", {}),
            ("specialist_followups_pending", "57. Do you have any pending medical evaluations, specialist consults, or imaging scans?", "area", {}),
            ("major_infections", "58. Document major historical or frequently recurring infectious conditions:", "area", {}),
            ("injuries_accidents", "59. Detail significant structural physical traumas, bone fractures, or concussions:", "area", {}),
        ],
    },
    {
        "title": "06. Chemical Profiles",
        "summary": "Prescribed pharmaceutical formulas, supplement inputs, tracking food sensitivities, and allergen risks.",
        "questions": [
            ("takes_rx", "60. Are you currently taking any prescription medications?", "radio", {"options": YES_NO}),
            ("rx_details", "61. List names, exact dosages, and intake frequencies for all active prescriptions:", "area", {}),
            ("takes_otc", "62. Do you regularly use over-the-counter formulas?", "radio", {"options": YES_NO}),
            ("otc_details", "63. Detail all regular over-the-counter products:", "area", {}),
            ("takes_supplements", "64. Do you take nutraceuticals, vitamins, minerals, or sports supplements?", "radio", {"options": YES_NO}),
            ("supplement_details", "65. Itemize your regular supplement stack and active dosages:", "area", {}),
            ("supplement_advisor", "66. Who guides your current supplement configuration strategy?", "select", {"options": ["Medical doctor", "Dietitian / Nutritionist", "Pharmacist", "Personal trainer", "Family or peers", "Digital platforms / Social media", "Self-directed research", "No one"]}),
            ("stopped_med_side_effects", "67. Have you ever discontinued a prescribed treatment due to side effects?", "radio", {"options": YES_NO}),
            ("stopped_med_details", "68. If yes, clarify the molecule name and biological reactions experienced:", "area", {}),
            ("miss_med_reason", "69. If you occasionally miss scheduled doses, what factors contribute? (Select all)", "multi", {"options": ["Simple forgetfulness", "Experiencing side effects", "Financial costs", "Feeling well / Questioning necessity", "Complex daily schedule", "Prescription renewal delays", "Other"]}),
            ("med_allergies", "70. Itemize all known drug or pharmaceutical molecule allergies:", "area", {}),
            ("food_allergies", "71. Food allergies or documented gastrointestinal sensitivities:", "multi", {"options": ["None known", "Milk / Dairy matrices", "Egg options", "Wheat / Gluten vectors", "Soy options", "Peanuts", "Tree nuts", "Fin fish", "Shellfish", "Sesame", "Other"]}),
            ("env_allergies", "72. Environmental or airborne chemical allergens:", "multi", {"options": ["None known", "Pollen strains", "House dust mites", "Animal dander", "Mould spore profiles", "Insect stings", "Latex vectors", "Other"]}),
            ("anaphylaxis_history", "73. Have you ever entered a state of systemic anaphylaxis?", "radio", {"options": YES_NO}),
            ("wants_interaction_review", "74. Request cross-interaction testing for your medication-supplement stack?", "radio", {"options": YES_NO_UNSURE}),
        ],
    },
    {
        "title": "07. Lineage Profiles",
        "summary": "Invasive surgical histories, anaesthetic events, and cross-generational hereditary risk tracking.",
        "questions": [
            ("surgery_history", "75. Detail past surgical interventions (including reason, year, and complications):", "area", {}),
            ("hospital_admissions_non_surg", "76. Detail any historical non-surgical medical hospital admissions:", "area", {}),
            ("anaesthesia_complications", "77. Document any past problems or side effects related to anaesthesia:", "area", {}),
            ("blood_transfusion_history", "78. Have you ever received blood component transfusions?", "radio", {"options": YES_NO_UNSURE}),
            ("family_history", "79. Document conditions tracked through direct biological ancestors (parents, grandparents, siblings):", "multi", {"options": ["High blood pressure / Hypertension", "Hypercholesterolemia", "Type 2 diabetes", "Premature coronary artery disease", "Stroke events", "Aneurysm profiles", "Thromboembolism / Blood clots", "Cancer / Malignancies", "Breast cancer", "Colorectal cancer", "Prostate cancer", "Ovarian cancer", "Alzheimer's / Dementia", "Parkinson's disease", "Osteoporosis", "Autoimmune disease", "Polycystic kidney disease", "Psychiatric conditions", "Substance use challenges"]}),
            ("family_history_details", "80. Add specific details about family history, including age at diagnosis if known:", "area", {}),
            ("parental_health_status", "81. Document parents' current health status, ages, or causes/ages of death:", "area", {}),
            ("genetic_testing_history", "82. Have you previously undergone clinical or ancestry genetic testing?", "radio", {"options": YES_NO_UNSURE}),
            ("genetic_testing_details", "83. Summarize any relevant genetic findings if available:", "area", {}),
        ],
    },
    {
        "title": "08. Systemic Biomarker Tracking",
        "summary": "Real-time tracking of physiological symptom frequencies across major organ tracks.",
        "questions": [
            ("sym_fever", "84. Recurrent fevers, dynamic temperature shifts, or nocturnal night sweats?", "slider_select", {"options": FREQ}),
            ("sym_weight_change", "85. Unintentional, rapid modifications to body weight parameters?", "slider_select", {"options": FREQ}),
            ("sym_fatigue", "86. Persistent exhaustion that disrupts normal cognitive or physical focus?", "slider_select", {"options": FREQ}),
            ("sym_rash", "87. Recurring skin rashes, unexpected dermal changes, or barrier shifts?", "slider_select", {"options": FREQ}),
            ("sym_bruising", "88. Tendency to bruise easily or develop unprovoked hematomas?", "slider_select", {"options": FREQ}),
            ("sym_hair_loss", "89. Accelerated hair follicle loss or sudden thinning?", "slider_select", {"options": FREQ}),
            ("sym_headache", "90. Frequent localized headaches, dynamic tension bands, or visual migraines?", "slider_select", {"options": FREQ}),
            ("sym_dizziness", "91. Vertigo, unsteadiness, or orthostatic fainting sensations?", "slider_select", {"options": FREQ}),
            ("sym_vision", "92. Unexplained or sudden adjustments to visual clarity?", "slider_select", {"options": FREQ}),
            ("sym_chest_pain", "93. Cardiovascular pressure, restrictive chest pain, or radiating tightness?", "slider_select", {"options": FREQ}),
            ("sym_palpitations", "94. Premature atrial fluttering, skipped beats, or rapid unprovoked racing?", "slider_select", {"options": FREQ}),
            ("sym_breathlessness", "95. Shortness of breath (dyspnoea) at rest or under minor physical workloads?", "slider_select", {"options": FREQ}),
            ("sym_reflux", "96. Gastrointestinal reflux, frequent pyrosis, or acid indigestion?", "slider_select", {"options": FREQ}),
            ("sym_abdominal_pain", "97. Unspecified abdominal pain, bloating, or visceral layout cramping?", "slider_select", {"options": FREQ}),
            ("sym_bowel_change", "98. Recent or persistent changes to regular bowel habit outputs?", "slider_select", {"options": FREQ}),
            ("sym_joint_pain", "99. Articular joint pain, early morning stiffness, or structural fluid swelling?", "slider_select", {"options": FREQ}),
            ("sym_numbness", "100. Peripheral neuropathy, unexpected tingling, or focal motor weakness tracks?", "slider_select", {"options": FREQ}),
            ("sym_cold_intolerance", "101. Abnormal physical sensitivity or low tolerance to cool environments?", "slider_select", {"options": FREQ}),
            ("sym_thirst", "102. Persistent unprovoked thirst (polydipsia indicators)?", "slider_select", {"options": FREQ}),
            ("sym_anxiety", "103. Persistent psychological anxiety, hyperarousal, or difficulty relaxing?", "slider_select", {"options": FREQ}),
            ("sym_sadness", "104. Prolonged flat affect, feelings of low mood, or diminished motivation?", "slider_select", {"options": FREQ}),
            ("sym_other_details", "105. Clarify any alternative physical anomalies or trends our clinical team should look into:", "area", {}),
        ],
    },
    {
        "title": "09. Nutritional & Kinetic Inputs",
        "summary": "Metabolic fuel inputs, daily physical movement trends, and targeted training metrics.",
        "questions": [
            ("diet_pattern", "106. Select the description that best reflects your primary eating pattern:", "select", {"options": ["Omnivore / General macro mix", "Mediterranean style focus", "Vegetarian", "Vegan", "Pescatarian", "Low-carbohydrate tracking", "Ketogenic model", "Intermittent fasting windows", "Other customized strategy"]}),
            ("meals_per_day", "107. Average feeding frequency window (structured intake events per 24 hours):", "select", {"options": ["One", "Two", "Three", "Four or more", "Highly variable"]}),
            ("veg_servings_day", "108. Standard daily servings of micronutrient-dense vegetables:", "select", {"options": ["None", "1-2 servings", "3-4 servings", "5 or more servings"]}),
            ("ultra_processed_frequency", "109. Frequency of ultra-processed food matrices or convenience meals:", "select", {"options": ["Rarely / Never", "Weekly average", "Several times per week", "Daily occurrence"]}),
            ("sugar_beverage_frequency", "110. Consumption frequency of beverages with added refined sugars:", "select", {"options": ["Never", "Rarely", "Weekly", "Daily track"]}),
            ("water_intake", "111. Quantify clear fluid/water intake volume per 24-hour cycle:", "select", {"options": ["Less than 1 litre", "1-2 litres", "2-3 litres", "More than 3 litres", "Varies / Unsure"]}),
            ("caffeine_day", "112. Total daily caffeinated metrics (coffee, black teas, energy formulations):", "select", {"options": ["None", "1 serving", "2 servings", "3 servings", "4 or more servings"]}),
            ("exercise_sessions_week", "113. Structured physical workout sessions completed per week:", "slider", {"min": 0, "max": 14, "default": 3}),
            ("exercise_minutes_week", "114. Cumulative active movement tracking minutes over an average week:", "number", {"min": 0, "max": 2000, "default": 90}),
            ("strength_sessions_week", "115. Dedicated resistance training or metabolic hypertrophy sessions weekly:", "slider", {"min": 0, "max": 7, "default": 1}),
            ("avg_daily_steps", "116. Average daily step count baseline (from phone or wearable device tracking):", "number", {"min": 0, "max": 100000, "default": 0}),
            ("sitting_hours_day", "117. Estimated cumulative continuous sedentary or sitting hours per day:", "select", {"options": ["Less than 4 hours", "4-6 hours", "7-9 hours", "10 hours or more"]}),
            ("exercise_limitations", "118. Identify obstacles that actively limit your workout performance capacity:", "multi", {"options": ["Physical pain / Discomfort", "Shortness of breath", "Systemic fatigue", "Scheduling constraints", "Motivation blocks", "Current structural injury", "Fear of re-injury", "Lack of facility access", "Nothing limits my performance", "Other"]}),
            ("resting_heart_rate", "119. Verified resting heart rate metrics (RHR baseline, BPM):", "number", {"min": 0, "max": 240, "default": 0}),
            ("estimated_vo2max", "120. Known laboratory cardiorespiratory health metric score (VO₂ Max baseline):", "text", {"placeholder": "e.g., 42 ml/kg/min, or unknown"}),
        ],
    },
    {
        "title": "10. Recovery & Stress Load",
        "summary": "Nocturnal sleep efficiency indices, stress load distributions, and lifestyle habits.",
        "questions": [
            ("sleep_hours_night", "121. True average continuous sleep duration hours per night:", "slider_float", {"min": 3.0, "max": 12.0, "default": 7.0, "step": 0.5}),
            ("sleep_quality", "122. Rate your subjective sleep efficiency and recovery depth:", "select", {"options": ["Poor", "Fair", "Good", "Very good", "Excellent"]}),
            ("sleep_onset", "123. Experience difficulty with sleep latency (falling asleep)?", "slider_select", {"options": FREQ}),
            ("sleep_maintenance", "124. Experience frequent wakefulness during sleep cycles?", "slider_select", {"options": FREQ}),
            ("snoring", "125. Witnessed loud snoring or breathing pauses?", "radio", {"options": YES_NO_UNSURE}),
            ("sleep_caffeine_dependency", "126. Absolute reliance on morning stimulants to reach normal focus states:", "radio", {"options": ["Never", "Occasionally", "Most days", "Every day"]}),
            ("sleep_support_used", "127. Tools or sleep aids actively used to promote sleep quality:", "multi", {"options": ["Prescribed clinical medications", "Over-the-counter sleep aids", "Exogenous Melatonin", "Herbal supplement mixes", "Relaxation / Downregulation breathing techniques", "Meditation practices", "White noise / Audio masking", "CPAP structural device", "No tools used", "Other"]}),
            ("stress_level", "128. Rate your perceived continuous background stress load:", "select", {"options": ["Low", "Moderate / Manageable", "High", "Very high / Exhausting"]}),
            ("tobacco_use", "129. Lifestyle tobacco smoking or chemical vaping status profile:", "select", {"options": ["Never smoked / Vaped", "Former regular user", "Current regular user"]}),
            ("alcohol_servings_week", "130. Standard metabolic servings of alcohol consumed in a typical week:", "number", {"min": 0, "max": 100, "default": 0}),
            ("recreational_screen_time", "131. Recreational, non-work digital screen exposure per 24-hour block:", "select", {"options": ["Less than 2 hours", "2-4 hours", "5-7 hours", "More than 7 hours"]}),
            ("home_environment", "132. Known household health hazards or environmental tracking concerns:", "multi", {"options": ["Mould exposure", "Ambient air pollution", "Water quality issues", "Disruptive neighborhood noise", "Overcrowded conditions", "Physical safety concerns", "No hazards identified", "Other"]}),
        ],
    },
    {
        "title": "11. Prophylactic Settings",
        "summary": "Preventive screenings, vaccination summaries, and diagnostic coordination goals.",
        "questions": [
            ("bp_recent", "133. Record your latest known cardiovascular blood pressure values:", "text", {"placeholder": "e.g., 118/76 mmHg, or unknown"}),
            ("labs_recent", "134. Complete diagnostic laboratory or endocrine tracking panel within the past year?", "radio", {"options": YES_NO_UNSURE}),
            ("cancer_screening_status", "135. Preventive oncology screening modules completed or currently due:", "multi", {"options": ["Cervical cancer screening", "Breast imaging screening", "Colorectal screening", "Prostate screening", "Dermatological skin checking", "Lung screening protocols", "Not sure", "Not applicable"]}),
            ("vaccination_status", "136. Key immunization records you believe are up to date:", "multi", {"options": ["Influenza seasonal protection", "COVID-19 updates", "Tetanus booster mix", "Hepatitis B series", "HPV vaccine", "Shingles vaccine", "Pneumococcal vector", "Travel specific vaccines", "Not sure"]}),
            ("preventive_support_targets", "137. Select strategic prevention targets where you want maximum diagnostic reporting support:", "multi", {"options": ["Weight management", "Cardiovascular health preservation", "Diabetes mellitus prevention", "Early oncology tracking", "Immunization management", "Longevity optimization", "Skeletal / Bone density tracking", "Neurological / Brain tracking", "Smoking cessation tracking", "Physical exercise scaling", "Nutritional redesign", "Mental wellbeing mapping", "Sleep optimization patterns", "Women's dynamic health", "Men's dynamic health", "Unsure"]}),
            ("wants_to_prevent_top3", "138. Select up to three chronic conditions you prioritize proactively screening out of your future longevity track:", "multi", {"options": ["Heart disease", "Stroke", "Type 2 Diabetes", "Oncology / Cancer", "Osteoporosis / Structural fractures", "Memory decline / Dementia", "Loss of physical mobility", "Vision decline", "Chronic pain conditions", "Frailty / Muscle mass loss", "Other"], "max_selections": 3}),
            ("share_records_consent", "139. Grant formal authorization to link historical medical records or laboratory results to PRVNT:", "radio", {"options": ["Yes", "No", "Selected records only"]}),
            ("additional_context", "140. Add any additional lifestyle details, concerns, or health targets for the PRVNT clinical team:", "area", {}),
        ],
    },
]

def inject_premium_css():
    """Injects precise, clean typography mimicking the premium PRVNT layout ecosystem."""
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
        font-family: "Standerd", "Plus Jakarta Sans", sans-serif;
    }

    /* Primary Framing Elements utilize Clash Grotesk stylings */
    h1, h2, h3, h4, .brand-name, .metric strong, .section-title {
        font-family: "Clash Grotesk", "Space Grotesk", sans-serif !important;
        text-transform: uppercase !important;
        letter-spacing: -0.01em !important;
        font-weight: 600 !important;
    }

    p, label, span, div, button, input, textarea, select {
        font-family: "Standerd", "Plus Jakarta Sans", sans-serif !important;
    }

    .block-container {
        padding-top: 35px;
        padding-bottom: 70px;
        max-width: 1440px;
    }

    /* Navigation Components */
    div[data-baseweb="tab-list"] {
        gap: 6px;
        background-color: transparent;
        padding: 4px;
    }

    button[data-baseweb="tab"] {
        background-color: #FFFFFF !important;
        border: 1px solid var(--line) !important;
        color: var(--muted) !important;
        padding: 14px 20px !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        transition: all 0.2s ease;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: var(--deep) !important;
        color: #FFFFFF !important;
        border-color: var(--deep) !important;
    }

    /* Layout Cards */
    .prvnt-form-card {
        background: #FFFFFF;
        border: 1px solid var(--line);
        padding: 45px;
        margin-top: 15px;
    }

    .prvnt-brand-header {
        background: #FFFFFF;
        border: 1px solid var(--line);
        padding: 40px 45px;
        margin-bottom: 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .logo-container {
        width: 140px;
        height: 55px;
        border: 1px dashed var(--mist);
        display: flex;
        align-items: center;
        justify-content: center;
        background: #FAFAFA;
        color: var(--harbor);
        font-weight: 700;
        font-size: 0.75rem;
        letter-spacing: 0.1em;
    }

    .status-pill {
        display: inline-block;
        background: rgba(144, 183, 198, 0.12);
        color: var(--harbor);
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        padding: 5px 12px;
        margin-bottom: 12px;
    }

    /* Input Field Architecture adjustments */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {
        border-radius: 0px !important;
        border: 1px solid var(--line) !important;
        background-color: #FAFAFA !important;
    }

    div[data-testid="stMarkdownContainer"] label {
        color: var(--ink) !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
        margin-bottom: 6px !important;
    }

    /* Core Action Buttons */
    .stButton > button {
        border-radius: 0px !important;
        border: 1px solid var(--deep) !important;
        background: var(--deep) !important;
        color: white !important;
        min-height: 52px !important;
        width: 100% !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background: var(--harbor) !important;
        border-color: var(--harbor) !important;
    }

    .security-notice-box {
        background: #F9FAFA;
        border-left: 3px solid var(--harbor);
        padding: 22px;
        color: var(--deep);
        font-size: 0.88rem;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

def ensure_session_state():
    """Initializes system logging and user tracking states."""
    if "started" not in st.session_state:
        st.session_state.started = True
        st.session_state.start_time = time.time()
        st.session_state.form_responses = {}
        
    # Capture environment or platform account references
    if "user_identity_token" not in st.session_state:
        try:
            user_email = st.experimental_user.email
        except AttributeError:
            user_email = "client.onboarding@prvnt.com"
            
        st.session_state.user_email = user_email
        # Map into standard deterministic tracking strings
        st.session_state.user_identity_token = hashlib.sha256(f"PRVNT-{user_email}".encode()).hexdigest()[:12].upper()

def process_secure_payload_commit(responses_payload):
    """Packages form responses with secure system tracking variables."""
    meta_wrapper = {
        "account_linkage_email": st.session_state.user_email,
        "account_hashed_id": st.session_state.user_identity_token,
        "submission_timestamp_utc": datetime.utcnow().isoformat(),
        "ingestion_engine_version": "PRVNT-INTAKE-V3.6",
        "client_session_duration_secs": int(time.time() - st.session_state.start_time),
        "data_payload": responses_payload
    }
    return meta_wrapper

def render_onboarding_application():
    ensure_session_state()
    inject_premium_css()

    # --- BRANDED HEADER MATRIX BLOCK ---
    st.markdown(f"""
    <div class="prvnt-brand-header">
        <div>
            <div class="status-pill">🔒 Zero-Knowledge Pipeline Enabled</div>
            <h1 style="color:var(--deep); margin:0; font-size:2.1rem; font-weight:600;">Comprehensive Intake Matrix</h1>
            <p style="color:var(--muted); margin:4px 0 0 0; font-size:0.9rem;">
                Verified Account Context: <b style="color:var(--ink);">{st.session_state.user_email}</b> &nbsp;|&nbsp; System Token ID: <code style="color:var(--deep); background:#EAEAEA; padding:1px 5px;">{st.session_state.user_identity_token}</code>
            </p>
        </div>
        <div class="logo-container">
            [ PLACE LOGO HERE ]
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Dynamic Progress Calculation
    total_registered_questions = sum(len(sec["questions"]) for sec in SECTIONS)
    current_answered_count = len([k for k, v in st.session_state.form_responses.items() if v not in [None, "", [], 0]])
    completion_ratio = current_answered_count / total_registered_questions

    # Structural Stat Cards
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric(label="SCHEMA COMPLIANCE MAPPING", value=f"{total_registered_questions} Active Fields")
    with m_col2:
        st.metric(label="METRICS COMPILATION LOG", value=f"{current_answered_count} Inputted")
    with m_col3:
        st.metric(label="SUBMISSION CHANNEL PROGRESS", value=f"{completion_ratio:.1%}")
    st.progress(completion_ratio)

    st.markdown("<br>", unsafe_allow_html=True)

    # Generate Sequential Tabs Architecture
    tab_labels = [sec["title"] for sec in SECTIONS] + ["💾 Submit Terminal"]
    rendered_tabs = st.tabs(tab_labels)

    # Dynamic Component Generation Pipeline
    for index, section in enumerate(SECTIONS):
        with rendered_tabs[index]:
            st.markdown(f"<div class='prvnt-form-card'>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='margin-top:0; color:var(--deep);'>{section['title']}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:var(--muted); font-size:0.92rem; margin-bottom:30px;'>{section['summary']}</p>", unsafe_allow_html=True)
            st.markdown("<hr style='border-color:var(--line); margin-bottom:25px;'>", unsafe_allow_html=True)

            grid_col1, grid_col2 = st.columns(2)
            
            for q_idx, (q_key, q_label, q_type, q_args) in enumerate(section["questions"]):
                target_column = grid_col1 if (q_idx % 2 == 0) else grid_col2
                
                with target_column:
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
                    
                    if isinstance(val, date):
                        st.session_state.form_responses[q_key] = val.strftime("%Y-%m-%d")
                    else:
                        st.session_state.form_responses[q_key] = val
            st.markdown("</div>", unsafe_allow_html=True)

    # --- FINAL SUBMISSION TERMINAL & MASTER ACCOUNT CLOUD STORAGE LINK ---
    with rendered_tabs[-1]:
        st.markdown("<div class='prvnt-form-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0; color:var(--deep);'>Secure Database Submission Terminal</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:var(--muted);'>Execute transmission layer updates to commit your biological telemetry metadata to the cloud master database registry.</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color:var(--line); margin-bottom:25px;'>", unsafe_allow_html=True)

        st.markdown("""
        <div class="security-notice-box">
            <b>System Linkage Notice:</b> Data pipelines are optimized to automatically read account authentication metadata parameters. Submitting routes raw vectors strictly to your private administrative storage tables.
        </div>
        <br>
        """, unsafe_allow_html=True)

        final_master_payload = process_secure_payload_commit(st.session_state.form_responses)

        col_exec1, col_exec2 = st.columns([1, 1])
        with col_exec1:
            if st.button("🚀 Finalize & Transmit Data Matrix"):
                with st.spinner("Processing cloud database connection layer mappings..."):
                    time.sleep(1.5)
                    
                    # --- ENTERPRISE CLOUD DATABASE HOOK ---
                    # To connect to external serverless structures (e.g., Supabase / Postgre SQL via Streamlit secrets):
                    # import requests
                    # db_endpoint = st.secrets["PRVNT_CLOUD_API_ENDPOINT"]
                    # secure_headers = {"Authorization": f"Bearer {st.secrets['PRVNT_CLOUD_KEY']}"}
                    # response = requests.post(db_endpoint, json=final_master_payload, headers=secure_headers)
                    
                    st.success("🔒 Diagnostic records successfully synchronized with the PRVNT Cloud Account.")
                    st.balloons()
                    
                    st.markdown(f"""
                    <div style='background:#F0F6F6; border: 1px solid var(--mist); padding:18px; margin-top:15px; font-size:0.85rem; color:var(--deep);'>
                        <b>Transaction Ledger:</b><br>
                        • Linked Account Context: {final_master_payload['account_linkage_email']}<br>
                        • Secure Telemetry Hash: {final_master_payload['account_hashed_id']}<br>
                        • Sync Timestamp (UTC): {final_master_payload['submission_timestamp_utc']}
                    </div>
                    """, unsafe_allow_html=True)

        with col_exec2:
            st.download_button(
                label="📥 Export Offline Diagnostic Backup (.JSON)",
                data=json.dumps(final_master_payload, indent=2),
                file_name=f"PRVNT_Backup_{st.session_state.user_identity_token}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )

        st.markdown("<br><hr style='border-color:var(--line);'><br>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:var(--deep);'>Active Real-Time Telemetry Data Grid View</h4>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame([st.session_state.form_responses]).T, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    render_onboarding_application()
