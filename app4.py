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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
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
if "form_registry" not in st.session_state:
    st.session_state.form_registry = {}
if "active_key" not in st.session_state:
    st.session_state.active_key = ""
if "reload_status" not in st.session_state:
    st.session_state.reload_status = ""

def create_unique_key():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

def persist_draft_state():
    key = create_unique_key() if not st.session_state.active_key else st.session_state.active_key
    st.session_state.active_key = key
    
    current_snapshot = {k: v for k, v in st.session_state.items() if not k.startswith(('form_registry', 'reload_status', 'active_key'))}
    
    if "registry_vault" not in st.sidebar.session_state:
        st.sidebar.session_state["registry_vault"] = {}
    st.sidebar.session_state["registry_vault"][key] = current_snapshot

def retrieve_draft_state(target_key):
    target_key = target_key.strip().upper()
    if "registry_vault" in st.sidebar.session_state and target_key in st.sidebar.session_state["registry_vault"]:
        state_snapshot = st.sidebar.session_state["registry_vault"][target_key]
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
""", unsafe_allow_html
