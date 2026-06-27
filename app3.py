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

LOGO_PATH = "assets/prvnt-logo.png"

YES_NO = ["No", "Yes"]
YES_NO_UNSURE = ["No", "Yes", "Unsure"]
FREQ = ["Never", "Occasionally", "Often", "Almost always"]
SATISFACTION = ["Very dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very satisfied"]


SECTIONS = [
    {
        "title": "Profile",
        "summary": "Core identity, contact details, and basic body metrics.",
        "questions": [
            ("fullname", "Full name as shown on government-issued identification", "text", {"required": True}),
            ("preferred_name", "Preferred name", "text", {}),
            ("dob", "Date of birth", "date", {"default": date(1990, 1, 1), "required": True}),
            ("age", "Age", "number", {"min": 0, "max": 120, "default": 35}),
            ("sex", "Sex assigned at birth", "select", {"options": ["Female", "Male", "Intersex", "Prefer not to answer"]}),
            ("gender_identity", "Gender identity", "select", {"options": ["Woman", "Man", "Non-binary", "Self-describe", "Prefer not to answer"]}),
            ("pronouns", "Preferred pronouns", "select", {"options": ["She / Her", "He / Him", "They / Them", "Other", "Prefer not to answer"]}),
            ("height", "Height", "text", {"placeholder": "cm or ft/in"}),
            ("weight_curr", "Current weight", "text", {"placeholder": "kg or lb"}),
            ("weight_usual", "Usual adult weight", "text", {}),
            ("waist_circumference", "Waist circumference, if known", "text", {"placeholder": "cm or inches"}),
            ("language", "Preferred language", "text", {"default": "English"}),
            ("mobile", "Mobile number", "text", {"required": True}),
            ("email", "Email address", "text", {"required": True}),
            ("address", "Current city and country", "text", {}),
        ],
    },
    {
        "title": "Life Context",
        "summary": "Daily context that shapes health, access, support, and follow-through.",
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
            ("financial_health_barrier", "Have costs ever delayed your care, medicines, tests, or follow-up?", "radio", {"options": YES_NO_UNSURE}),
            ("health_literacy", "How comfortable are you understanding medical instructions?", "select", {"options": ["Very comfortable", "Comfortable", "Sometimes unsure", "Often unsure"]}),
        ],
    },
    {
        "title": "Care Team",
        "summary": "Current providers, care coordination, and record sharing preferences.",
        "questions": [
            ("regular_provider", "Regular doctor or primary healthcare provider", "text", {}),
            ("active_care_team", "Healthcare professionals currently involved in your care", "multi", {"options": ["Family physician", "Internal medicine physician", "Cardiologist", "Endocrinologist", "Gastroenterologist", "Neurologist", "Rheumatologist", "Pulmonologist", "Nephrologist", "Oncologist", "Psychiatrist", "Psychologist", "Dietitian", "Physiotherapist", "Dentist", "Ophthalmologist", "Other"]}),
            ("care_coordinator", "Who usually coordinates your healthcare?", "select", {"options": ["Family physician", "Specialist", "I coordinate it myself", "Family member", "Other"]}),
            ("prvnt_comm_permission", "Are there healthcare professionals you would like PRVNT to communicate with?", "radio", {"options": YES_NO}),
            ("provider_contact_details", "If yes, list provider names and contact details", "area", {}),
            ("records_location", "Where are your most important medical records currently held?", "area", {}),
            ("share_records_consent", "Willing to share historical external laboratory or medical records with PRVNT?", "radio", {"options": ["Yes", "No", "Some records only"]}),
        ],
    },
    {
        "title": "Goals",
        "summary": "What brought you here and what a meaningful outcome looks like.",
        "questions": [
            ("prompt_join_prvnt", "What prompted you to join PRVNT?", "multi", {"options": ["General health assessment", "Disease prevention", "Family history of disease", "Weight management", "Improve energy", "Better sleep", "Improve physical fitness", "Better nutrition", "Healthy ageing", "Manage an existing medical condition", "Ongoing unexplained symptoms", "Care coordination", "Second opinion", "Recent abnormal test results", "Recommendation from family/friends", "Other"]}),
            ("top_12mo_improvement", "Health concern you would most like to improve over the next 12 months", "area", {}),
            ("good_health_definition", "What does good health look like for you?", "area", {}),
            ("worries_or_fears", "Anything you are worried about that you would like to discuss?", "area", {}),
            ("overall_health_rate", "How would you rate your overall health today?", "slider_select", {"options": ["Poor", "Fair", "Good", "Very good", "Excellent"]}),
            ("health_vs_5yrs_ago", "Compared with five years ago, your health is:", "select", {"options": ["Much worse", "Slightly worse", "About the same", "Slightly better", "Much better"]}),
            ("three_health_goals", "Three most important health goals over the next 12 months", "area", {}),
            ("unaddressed_symptoms", "Anything about your health that has not been fully explained?", "area", {}),
            ("daily_energy_level", "Energy level on most days", "select", {"options": ["Very low", "Low", "Variable", "Good", "Excellent"]}),
            ("health_satisfaction", "Satisfaction with current health", "select", {"options": SATISFACTION}),
            ("health_improvement_confidence", "Confidence that you can improve your health", "select", {"options": ["Not confident at all", "Not very confident", "Unsure", "Confident", "Very confident"]}),
            ("readiness_to_change", "Readiness to make changes", "select", {"options": ["Not ready at present", "Thinking about making changes", "Ready within the next month", "Ready now"]}),
            ("care_decision_preference", "How involved would you like to be in decisions?", "select", {"options": ["Make decisions together with my healthcare team", "Healthcare team guides most decisions", "I decide after medical advice", "No preference"]}),
            ("desired_support_areas", "Areas you would most like support with", "multi", {"options": ["Nutrition", "Exercise", "Sleep", "Stress management", "Weight management", "Medication review", "Managing a chronic condition", "Preventive screening", "Mental wellbeing", "Healthy ageing", "Smoking cessation", "Alcohol reduction", "Women's health", "Men's health", "Other"]}),
            ("historical_plan_barriers", "What previously made it difficult to follow a healthcare plan?", "multi", {"options": ["Cost", "Time", "Work commitments", "Family responsibilities", "Difficulty understanding instructions", "Side effects of treatment", "Lack of motivation", "Limited access to healthcare", "None of the above", "Other"]}),
        ],
    },
    {
        "title": "Medical History",
        "summary": "Past and current diagnoses, hospital use, and unresolved patterns.",
        "questions": [
            ("conditions", "Past or current diagnoses", "multi", {"options": ["High blood pressure / hypertension", "Prediabetes", "Type 2 diabetes", "High cholesterol / triglycerides", "Coronary artery disease / angina", "Heart attack history", "Heart failure", "Irregular heartbeat / arrhythmia", "Stroke / TIA", "Obstructive sleep apnoea", "Asthma", "COPD", "Chronic kidney disease", "Kidney stones", "Fatty liver disease", "Hepatitis", "Gallbladder disease", "GERD", "IBS", "Inflammatory bowel disease", "Coeliac disease", "Thyroid disease", "PCOS", "Autoimmune disease", "Rheumatoid arthritis", "Osteopenia / osteoporosis", "Cancer history", "Depression", "Anxiety disorder", "ADHD", "Migraine", "Chronic pain syndromes", "Long COVID", "Other"]}),
            ("current_active_conditions", "Which conditions are currently active or requiring follow-up?", "area", {}),
            ("unexpected_doc_visits_12m", "Unexpected doctor visits due to illness in past 12 months", "select", {"options": ["None", "1-2", "3-5", "More than 5"]}),
            ("er_visits_12m", "Emergency room or urgent care visits in past 12 months", "select", {"options": ["None", "Once", "Twice", "Three or more times"]}),
            ("hospital_admissions_12m", "Admitted to hospital in the past 12 months?", "radio", {"options": YES_NO}),
            ("hospital_admissions_details", "If admitted, describe reason, dates, and outcome", "area", {}),
            ("specialist_followups_pending", "Do you have pending specialist follow-ups, scans, or tests?", "area", {}),
            ("major_infections", "Significant infections or recurrent infections", "area", {}),
            ("injuries_accidents", "Major injuries, accidents, or concussions", "area", {}),
        ],
    },
    {
        "title": "Medicines",
        "summary": "Medications, supplements, allergies, and safety signals.",
        "questions": [
            ("takes_rx", "Are you currently taking prescription medications?", "radio", {"options": YES_NO}),
            ("rx_details", "Prescription medications with doses and frequencies", "area", {}),
            ("takes_otc", "Do you regularly take over-the-counter medicines?", "radio", {"options": YES_NO}),
            ("otc_details", "Over-the-counter products", "area", {}),
            ("takes_supplements", "Do you take vitamins, minerals, or supplements?", "radio", {"options": YES_NO}),
            ("supplement_details", "Supplements and dosages", "area", {}),
            ("supplement_advisor", "Who advises you about supplements?", "select", {"options": ["Doctor", "Dietitian / Nutritionist", "Pharmacist", "Personal trainer", "Family or friends", "Internet / Social Media", "Self-directed", "No one"]}),
            ("stopped_med_side_effects", "Ever stopped a medication due to side effects?", "radio", {"options": YES_NO}),
            ("stopped_med_details", "If yes, which medication and what happened?", "area", {}),
            ("miss_med_reason", "If you occasionally miss medication, what is the reason?", "multi", {"options": ["I forget", "Side effects", "Cost", "I feel well and do not think I need it", "Difficult schedule", "Prescription not available", "Other"]}),
            ("miss_med_frequency", "How often do you miss doses?", "select", {"options": ["Never", "Rarely", "Sometimes", "Often", "I do not take regular medication"]}),
            ("med_allergies", "Known medication allergies", "area", {}),
            ("food_allergies", "Food allergies or intolerances", "multi", {"options": ["None known", "Milk / Dairy", "Egg", "Wheat / Gluten", "Soy", "Peanut", "Tree nuts", "Fish", "Shellfish", "Sesame", "Other"]}),
            ("env_allergies", "Environmental allergies", "multi", {"options": ["None known", "Pollen", "House dust mites", "Animal dander", "Mould", "Insect stings", "Latex", "Other"]}),
            ("anaphylaxis_history", "Ever had a severe allergic reaction or anaphylaxis?", "radio", {"options": YES_NO}),
            ("wants_interaction_review", "Request supplement-medication interaction review?", "radio", {"options": YES_NO_UNSURE}),
        ],
    },
    {
        "title": "Procedures & Family",
        "summary": "Surgical history, anesthesia issues, and inherited risk.",
        "questions": [
            ("surgery_history", "Past surgeries or invasive procedures, with reasons, years, and complications", "area", {}),
            ("hospital_admissions_non_surg", "Historical non-surgical hospital admissions", "area", {}),
            ("anaesthesia_complications", "Complications or side effects from anesthesia", "area", {}),
            ("blood_transfusion_history", "Ever received a blood transfusion?", "radio", {"options": YES_NO_UNSURE}),
            ("family_history", "Family history", "multi", {"options": ["High blood pressure", "High cholesterol", "Type 2 diabetes", "Early heart attack", "Stroke events", "Aneurysm", "Blood clots", "Confirmed cancers", "Breast cancer", "Colon cancer", "Prostate cancer", "Ovarian cancer", "Dementia", "Parkinson's disease", "Osteoporosis", "Autoimmune disease", "Kidney disease", "Mental health condition", "Substance use disorder"]}),
            ("family_history_details", "Family history details, including relation and age at diagnosis", "area", {}),
            ("parental_health_status", "Parents' current health, ages, or cause/age at death", "area", {}),
            ("genetic_testing_history", "Have you had genetic testing or counselling?", "radio", {"options": YES_NO_UNSURE}),
            ("genetic_testing_details", "If yes, summarize relevant findings", "area", {}),
        ],
    },
    {
        "title": "Symptoms",
        "summary": "A focused review of symptoms across body systems.",
        "questions": [
            ("sym_fever", "Recurrent fever, chills, or night sweats", "slider_select", {"options": FREQ}),
            ("sym_weight_change", "Unintentional weight change", "slider_select", {"options": FREQ}),
            ("sym_fatigue", "Fatigue interfering with daily life", "slider_select", {"options": FREQ}),
            ("sym_rash", "Recurring rash or skin changes", "slider_select", {"options": FREQ}),
            ("sym_bruising", "Easy bruising tendencies", "slider_select", {"options": FREQ}),
            ("sym_hair_loss", "Sudden hair loss or thinning", "slider_select", {"options": FREQ}),
            ("sym_headache", "Headaches or migraines", "slider_select", {"options": FREQ}),
            ("sym_dizziness", "Dizziness, fainting, or balance issues", "slider_select", {"options": FREQ}),
            ("sym_vision", "Vision changes", "slider_select", {"options": FREQ}),
            ("sym_hearing", "Hearing changes or ringing in ears", "slider_select", {"options": FREQ}),
            ("sym_chest_pain", "Chest pain, pressure, or tightness", "slider_select", {"options": FREQ}),
            ("sym_palpitations", "Palpitations or irregular heartbeat sensation", "slider_select", {"options": FREQ}),
            ("sym_breathlessness", "Shortness of breath", "slider_select", {"options": FREQ}),
            ("sym_cough", "Persistent cough or wheeze", "slider_select", {"options": FREQ}),
            ("sym_reflux", "Heartburn or reflux", "slider_select", {"options": FREQ}),
            ("sym_abdominal_pain", "Abdominal pain or bloating", "slider_select", {"options": FREQ}),
            ("sym_bowel_change", "Change in bowel habit", "slider_select", {"options": FREQ}),
            ("sym_urinary", "Urinary symptoms", "slider_select", {"options": FREQ}),
            ("sym_joint_pain", "Joint pain or swelling", "slider_select", {"options": FREQ}),
            ("sym_back_neck", "Back or neck pain", "slider_select", {"options": FREQ}),
            ("sym_numbness", "Numbness, tingling, or weakness", "slider_select", {"options": FREQ}),
            ("sym_cold_intolerance", "Feeling unusually cold", "slider_select", {"options": FREQ}),
            ("sym_thirst", "Unusually increased thirst", "slider_select", {"options": FREQ}),
            ("sym_anxiety", "Feeling anxious, worried, or unable to relax", "slider_select", {"options": FREQ}),
            ("sym_sadness", "Feeling sad, down, or hopeless", "slider_select", {"options": FREQ}),
            ("sym_overwhelmed", "Feeling completely overwhelmed by life stress", "slider_select", {"options": FREQ}),
            ("sym_other_details", "Other symptoms or patterns you want PRVNT to know about", "area", {}),
        ],
    },
    {
        "title": "Nutrition",
        "summary": "Eating pattern, food quality, hydration, and appetite signals.",
        "questions": [
            ("diet_pattern", "Usual eating pattern", "select", {"options": ["Omnivore", "Mediterranean-style", "Vegetarian", "Vegan", "Pescatarian", "Low-carbohydrate", "Ketogenic", "Intermittent fasting", "Other"]}),
            ("meals_per_day", "Average meals per day", "select", {"options": ["One", "Two", "Three", "Four or more", "Variable"]}),
            ("veg_servings_day", "Vegetable servings consumed daily", "select", {"options": ["None", "1-2", "3-4", "5 or more"]}),
            ("fruit_servings_day", "Fruit servings consumed daily", "select", {"options": ["None", "1", "2", "3 or more"]}),
            ("protein_each_meal", "Do you usually include protein with meals?", "select", {"options": ["Rarely", "Sometimes", "Most meals", "Every meal"]}),
            ("ultra_processed_frequency", "Ultra-processed foods or fast food frequency", "select", {"options": ["Rarely", "Weekly", "Several times per week", "Daily"]}),
            ("sugar_beverage_frequency", "Refined sugar or sweetened beverage frequency", "select", {"options": ["Never", "Rarely", "Weekly", "Daily"]}),
            ("water_intake", "Approximate water intake per day", "select", {"options": ["Less than 1 litre", "1-2 litres", "2-3 litres", "More than 3 litres", "Unsure"]}),
            ("caffeine_day", "Caffeinated drinks per day", "select", {"options": ["None", "1", "2", "3", "4 or more"]}),
            ("appetite_change", "Recent appetite change", "radio", {"options": YES_NO_UNSURE}),
            ("nutrition_goals", "Nutrition priorities or restrictions PRVNT should know about", "area", {}),
        ],
    },
    {
        "title": "Movement",
        "summary": "Activity, strength, mobility, pain, and measurable fitness signals.",
        "questions": [
            ("exercise_sessions_week", "Physical activity sessions per week", "slider", {"min": 0, "max": 14, "default": 3}),
            ("exercise_minutes_week", "Approximate exercise minutes per week", "number", {"min": 0, "max": 2000, "default": 90}),
            ("strength_sessions_week", "Strength or resistance training sessions per week", "slider", {"min": 0, "max": 7, "default": 1}),
            ("mobility_flexibility", "Mobility, stretching, yoga, or flexibility work", "select", {"options": ["Never", "Occasionally", "Weekly", "Several times per week"]}),
            ("avg_daily_steps", "Average daily step count, if known", "number", {"min": 0, "max": 100000, "default": 0}),
            ("sitting_hours_day", "Approximate sitting hours per day", "select", {"options": ["Less than 4", "4-6", "7-9", "10 or more"]}),
            ("exercise_limitations", "What limits your physical activity?", "multi", {"options": ["Pain", "Breathlessness", "Fatigue", "Time", "Motivation", "Injury", "Fear of injury", "No access to facilities", "Nothing", "Other"]}),
            ("resting_heart_rate", "Resting heart rate baseline, BPM", "number", {"min": 0, "max": 240, "default": 0}),
            ("estimated_vo2max", "Estimated VO2 max, if known", "text", {}),
            ("fitness_goal", "What would you like your body to be able to do 12 months from now?", "area", {}),
        ],
    },
    {
        "title": "Sleep & Stress",
        "summary": "Sleep quality, recovery, mood, cognition, and stress load.",
        "questions": [
            ("sleep_hours_night", "Average sleep duration per night", "slider_float", {"min": 3.0, "max": 12.0, "default": 7.0, "step": 0.5}),
            ("sleep_quality", "Overall sleep quality", "select", {"options": ["Poor", "Fair", "Good", "Very good", "Excellent"]}),
            ("sleep_onset", "Difficulty falling asleep", "slider_select", {"options": FREQ}),
            ("sleep_maintenance", "Waking during the night", "slider_select", {"options": FREQ}),
            ("snoring", "Snoring or witnessed breathing pauses", "radio", {"options": YES_NO_UNSURE}),
            ("morning_headaches", "Morning headaches or dry mouth", "slider_select", {"options": FREQ}),
            ("daytime_sleepiness", "Daytime sleepiness", "slider_select", {"options": FREQ}),
            ("sleep_caffeine_dependency", "Need caffeine to feel alert in the morning?", "radio", {"options": ["Never", "Occasionally", "Most days", "Every day"]}),
            ("sleep_support_used", "Active sleep aid products used", "multi", {"options": ["Prescription medication", "Over-the-counter medication", "Melatonin", "Herbal supplements", "Relaxation techniques", "Meditation", "White noise", "CPAP device", "Nothing", "Other"]}),
            ("stress_level", "Current stress level", "select", {"options": ["Low", "Moderate", "High", "Very high"]}),
            ("stress_sources", "Main sources of stress", "multi", {"options": ["Work", "Family", "Relationships", "Finances", "Health", "Caregiving", "Sleep", "Life transition", "Other"]}),
            ("coping_strategies", "What helps you recover or regulate stress?", "area", {}),
            ("memory_concentration", "Memory, focus, or concentration concerns", "radio", {"options": YES_NO_UNSURE}),
        ],
    },
    {
        "title": "Substances & Environment",
        "summary": "Tobacco, alcohol, exposures, and environmental risk signals.",
        "questions": [
            ("tobacco_use", "Tobacco smoking or vaping status", "select", {"options": ["Never smoked", "Ex-smoker", "Current user"]}),
            ("tobacco_details", "If current or former user, include type, amount, and years", "area", {}),
            ("alcohol_servings_week", "Standard units or servings of alcohol consumed weekly", "number", {"min": 0, "max": 100, "default": 0}),
            ("binge_drinking", "Episodes of heavy drinking in the past month", "select", {"options": ["None", "1", "2-3", "4 or more"]}),
            ("recreational_drugs", "Recreational or non-prescribed drug use", "radio", {"options": YES_NO}),
            ("recreational_drugs_details", "If yes, what and how often?", "area", {}),
            ("recreational_screen_time", "Recreational non-work screen time on a typical day", "select", {"options": ["Less than 2 hours", "2-4 hours", "5-7 hours", "More than 7 hours"]}),
            ("sun_exposure", "Frequent intense sun exposure or tanning bed use", "radio", {"options": YES_NO_UNSURE}),
            ("home_environment", "Home environment concerns", "multi", {"options": ["Mould", "Air pollution", "Water quality", "Noise", "Overcrowding", "Safety concerns", "None", "Other"]}),
            ("travel_risk", "Frequent travel or recent travel-related illness", "area", {}),
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
            ("dental_check", "Dental check-up timing", "select", {"options": ["Within 6 months", "Within 12 months", "1-2 years ago", "More than 2 years ago", "Not sure"]}),
            ("vision_check", "Vision or eye check timing", "select", {"options": ["Within 12 months", "1-2 years ago", "More than 2 years ago", "Not sure"]}),
            ("preventive_support_targets", "Preventive reporting support areas", "multi", {"options": ["Weight management", "Cardiovascular disease prevention", "Diabetes prevention", "Cancer screening", "Vaccinations", "Healthy ageing", "Bone health", "Brain health", "Smoking cessation", "Physical activity", "Nutrition", "Mental wellbeing", "Sleep", "Women's health", "Men's health", "Unsure"]}),
            ("wants_to_prevent_top3", "What would you most like to proactively prevent in the future? Select up to three.", "multi", {"options": ["Heart disease", "Stroke", "Diabetes", "Cancer", "Osteoporosis or fractures", "Memory decline or dementia", "Loss of mobility", "Vision loss", "Chronic pain", "Frailty", "Other"], "max_selections": 3}),
            ("additional_context", "Anything else you want your PRVNT care team to understand before your assessment?", "area", {}),
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

    h1,h2,h3,h4,.brand-name,.metric strong {
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

    .prvnt-header {
        background:#fff;
        border:1px solid var(--line);
        border-top:5px solid var(--deep);
        padding:30px 34px 28px;
        margin-bottom:22px;
    }

    .brand-row {
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:22px;
        margin-bottom:28px;
    }

    .brand-left {
        display:flex;
        align-items:center;
        gap:16px;
    }

    .logo-mark {
        width:116px;
        height:50px;
        display:flex;
        align-items:center;
        justify-content:center;
        border:1px solid var(--line);
        background:#f9fbfb;
    }

    .hero-logo-img {
        max-width:98px;
        max-height:36px;
        object-fit:contain;
    }

    .hero-logo-placeholder {
        color:var(--deep);
        font-family:"Space Grotesk","Segoe UI",Arial,sans-serif !important;
        font-weight:700;
        letter-spacing:.08em;
        font-size:.92rem;
    }

    .brand-name {
        color:var(--deep);
        font-size:1.04rem;
        font-weight:700;
        letter-spacing:.08em !important;
    }

    .brand-subtitle {
        color:#667174;
        font-size:.86rem;
        margin-top:2px;
    }

    .privacy-pill {
        border:1px solid var(--line);
        color:var(--harbor);
        background:#fbfcfc;
        padding:8px 11px;
        font-size:.76rem;
        font-weight:700;
        text-transform:uppercase;
        letter-spacing:.06em;
        white-space:nowrap;
    }

    .header-copy h1 {
        color:var(--ink);
        font-size:clamp(2rem,4vw,3.8rem) !important;
        line-height:1.02 !important;
        max-width:900px;
        margin:0 0 12px;
    }

    .header-copy p {
        max-width:790px;
        color:#566164;
        font-size:1.02rem;
        line-height:1.65;
        margin:0;
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
        font-size:1.35rem;
        color:var(--deep);
    }

    .metric span {
        color:#5d686b;
        font-size:.82rem;
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

    .section-intro h2 {
        margin-top:4px !important;
        margin-bottom:6px !important;
        color:var(--ink);
    }

    .section-intro p {
        color:var(--muted);
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
        line-height:1.55;
    }

    @media (max-width:760px) {
        .block-container { padding-left:16px; padding-right:16px; }
        .prvnt-header { padding:24px 20px; }
        .brand-row { align-items:flex-start; flex-direction:column; }
        .brand-left { align-items:flex-start; flex-direction:column; }
        .privacy-pill { white-space:normal; }
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


def logo_html():
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as logo_file:
            logo_b64 = base64.b64encode(logo_file.read()).decode()
        return f'<img src="data:image/png;base64,{logo_b64}" alt="PRVNT logo" class="hero-logo-img">'
    return '<div class="hero-logo-placeholder">PRVNT</div>'


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
    data["meta_schema_version"] = "prvnt-comprehensive-intake-v3"
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

    st.markdown("""
    <div class="section-intro">
        <small>Final step</small>
        <h2>Review and Secure Handoff</h2>
        <p>Export the completed intake, or submit it to PRVNT's secured backend when configured.</p>
    </div>
    """, unsafe_allow_html=True)

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

    answered, total, required_missing = completion_stats()
    elapsed = int(time.time() - st.session_state.started_at)
    minutes, seconds = divmod(elapsed, 60)
    progress = answered / total if total else 0
    logo = logo_html()

    st.markdown(
        f"""
        <header class="prvnt-header">
            <div class="brand-row">
                <div class="brand-left">
                    <div class="logo-mark">{logo}</div>
                    <div>
                        <div class="brand-name">PRVNT</div>
                        <div class="brand-subtitle">Comprehensive Health Questionnaire</div>
                    </div>
                </div>
                <div class="privacy-pill">Private intake workspace</div>
            </div>

            <div class="header-copy">
                <h1>Your health intake, thoughtfully organized.</h1>
                <p>
                    Share your background, goals, symptoms, lifestyle signals, and prevention priorities
                    so your PRVNT care team can begin with clarity.
                </p>
            </div>
        </header>
        """,
        unsafe_allow_html=True,
    )
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
