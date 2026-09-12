import streamlit as st
import os
from dotenv import load_dotenv, find_dotenv
from core.llm_engine import evaluate_patient

# ==========================================
# 1. SYSTEM INITIALIZATION & STATE
# ==========================================
st.set_page_config(
    page_title="TriageFlow | Clinical AI",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv(find_dotenv(), override=True)
SYSTEM_API_KEY = os.getenv("GOOGLE_API_KEY")

if "assessment_history" not in st.session_state:
    st.session_state.assessment_history = []

if not SYSTEM_API_KEY:
    st.error("🚨 SYSTEM OFFLINE: Core AI Engine API Key not found. Please check configuration.")
    st.stop()

# ==========================================
# 2. PREMIUM CSS ARCHITECTURE
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        :root {
            --primary: #00EA8B;
            --bg-main: #060B09;
            --bg-surface: #0A1410;
            --border: rgba(255, 255, 255, 0.08);
            --text-main: #e2e8f0;
            --text-muted: #94a3b8;
            --danger: #EF4444;
            --warning: #F59E0B;
            --success: #10B981;
        }
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        .stApp {
            background-color: var(--bg-main);
            color: var(--text-main);
        }
        
        #MainMenu, footer, header {visibility: hidden;}

        /* Typography */
        h1, h2, h3 { font-weight: 600; letter-spacing: -0.5px; }
        
        /* Input Fields & Textareas — Explicit light/dark mode override */
        .stTextArea textarea, 
        .stTextInput input, 
        .stNumberInput input {
            background-color: #0A1410 !important;
            color: #e2e8f0 !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 6px !important;
            font-family: 'Inter', sans-serif !important;
        }

        .stTextArea textarea:focus, 
        .stTextInput input:focus, 
        .stNumberInput input:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 1px var(--primary) !important;
        }

        .stTextArea textarea::placeholder, 
        .stTextInput input::placeholder {
            color: #64748b !important;
            opacity: 1 !important;
        }

        /* Selectbox container styling */
        div[data-baseweb="select"] > div {
            background-color: #0A1410 !important;
            color: #e2e8f0 !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
        }

        /* Input Labels */
        .stTextArea label, 
        .stTextInput label, 
        .stNumberInput label, 
        .stSelectbox label {
            color: var(--text-main) !important;
            font-weight: 500 !important;
        }

        /* Glassmorphism Panels */
        .glass-panel {
            background: var(--bg-surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        }

        /* Buttons */
        .stButton>button {
            background: var(--primary) !important;
            color: #000000 !important;
            border: none !important;
            border-radius: 6px;
            font-weight: 600;
            letter-spacing: 0.5px;
            padding: 0.75rem 2rem;
            transition: all 0.2s ease;
            width: 100%;
        }
        .stButton>button:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }
        
        /* Clear History Button */
        .clear-btn>button {
            background: transparent !important;
            color: var(--text-muted) !important;
            border: 1px solid var(--border) !important;
            font-size: 0.8rem;
            padding: 0.25rem 1rem;
            margin-top: 10px;
        }
        .clear-btn>button:hover {
            color: var(--text-main) !important;
            background: rgba(255,255,255,0.05) !important;
        }

        /* Section Labels */
        .section-label {
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 16px;
            border-bottom: 1px solid var(--border);
            padding-bottom: 8px;
        }

        /* Urgency Banners & Text */
        .urgency-banner {
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
            border-left: 6px solid;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .urgency-title {
            font-size: 2rem;
            font-weight: 700;
            letter-spacing: 1px;
            margin-bottom: 4px;
            text-transform: uppercase;
        }
        .urgency-subtitle {
            font-size: 1.1rem;
            font-weight: 400;
            opacity: 0.9;
        }

        /* Clinical Chips */
        .clinical-chip {
            display: inline-block;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 6px 14px;
            margin: 0 8px 8px 0;
            font-size: 0.9rem;
            font-weight: 500;
            color: var(--text-main);
        }

        /* Spectrum / Workflow */
        .workflow-step { font-size: 0.8rem; font-weight: 600; color: var(--text-muted); letter-spacing: 1px; }
        .workflow-arrow { color: var(--border); margin: 0 12px; }
        .spectrum-container { display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.2); border-radius: 6px; padding: 12px; margin-bottom: 24px; border: 1px solid var(--border); }
        .spectrum-item { flex: 1; text-align: center; font-size: 0.85rem; font-weight: 700; letter-spacing: 1px; padding: 8px; border-radius: 4px; transition: all 0.3s; }
        .spectrum-divider { width: 40px; height: 1px; background: var(--border); margin: 0 10px; }

        /* Sidebar Elements */
        [data-testid="stSidebar"] {
            background-color: #060B09;
            border-right: 1px solid var(--border);
        }
        .history-card {
            background: rgba(255,255,255,0.02);
            border: 1px solid var(--border);
            border-left: 3px solid var(--border);
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 12px;
            font-size: 0.85rem;
        }

        /* Footer */
        .dev-footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
        }
        .dev-role { font-size: 0.7rem; color: var(--text-muted); letter-spacing: 1.5px; font-weight: 700; text-transform: uppercase;}
        .dev-name { font-size: 1.05rem; color: var(--text-main); font-weight: 600; margin: 4px 0; }
        .dev-team { font-size: 0.8rem; color: var(--primary); font-weight: 500; margin-bottom: 12px;}
        .dev-links a {
            color: var(--text-muted);
            text-decoration: none;
            font-size: 0.8rem;
            margin-right: 12px;
            transition: color 0.2s;
        }
        .dev-links a:hover { color: var(--primary); }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. RENDER HELPERS
# ==========================================
def render_sidebar():
    with st.sidebar:
        st.markdown("<h2 style='color: var(--text-main); margin-bottom: 0; font-weight: 500;'><span style='color: var(--primary);'>⚕</span> TRIAGEFLOW</h2>", unsafe_allow_html=True)
        st.markdown("<div style='color: var(--text-muted); font-size: 0.85rem; margin-bottom: 2rem;'>AI-Assisted Clinical Triage</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-label'>SYSTEM</div>", unsafe_allow_html=True)
        st.markdown("● **Application** &nbsp;|&nbsp; <span style='color: var(--primary);'>READY</span>", unsafe_allow_html=True)
        st.markdown("● **AI Engine** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp; <span style='color: var(--primary);'>READY</span>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-label' style='margin-top: 2rem;'>SUPPORTED LANGUAGES</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 0.9rem; color: var(--text-muted);'>English · اردو · Roman Urdu</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-label' style='margin-top: 2rem;'>TRIAGE LEVELS</div>", unsafe_allow_html=True)
        st.markdown("🔴 <span style='color: var(--danger); font-weight: 500;'>Emergency</span><br>🟠 <span style='color: var(--warning); font-weight: 500;'>Urgent</span><br>🟢 <span style='color: var(--success); font-weight: 500;'>Routine</span>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-label' style='margin-top: 2rem;'>RECENT ASSESSMENTS</div>", unsafe_allow_html=True)
        if not st.session_state.assessment_history:
            st.markdown("<div style='color: var(--text-muted); font-size: 0.85rem; font-style: italic;'>No recent assessments.</div>", unsafe_allow_html=True)
        else:
            for item in st.session_state.assessment_history[:4]:
                color_var = "var(--danger)" if item['urgency'] == "Emergency" else "var(--warning)" if item['urgency'] == "Urgent" else "var(--success)"
                st.markdown(f"""
                <div class="history-card" style="border-left-color: {color_var};">
                    <strong style="color: {color_var}; text-transform: uppercase;">{item['urgency']}</strong>
                    <span style="color: var(--text-muted); float: right;">{item['language']}</span><br>
                    <div style="margin-top: 6px; color: var(--text-main); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; opacity: 0.9;">
                        {item['summary']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<div class='clear-btn'>", unsafe_allow_html=True)
            if st.button("Clear History", use_container_width=True):
                st.session_state.assessment_history = []
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="dev-footer">
            <div class="dev-role">TEAM LEAD</div>
            <div class="dev-name">Hamza Shoaib</div>
            <div class="dev-role" style="font-weight: 500; color: var(--text-main); letter-spacing: 0.5px;">AI & ML Engineer</div>
            <div class="dev-team">Team TriageFlow</div>
            <div class="dev-links">
                <a href="https://hamzashoaib.dev" target="_blank">Portfolio ↗</a>
                <a href="https://github.com/hamxashoaib" target="_blank">GitHub ↗</a><br>
                <a href="https://www.linkedin.com/in/ch-hamza-shoaib/" target="_blank" style="margin-top:6px; display:inline-block;">LinkedIn ↗</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_header():
    st.markdown("<h1 style='font-size: 2.2rem; margin-bottom: 0;'>AI-Assisted Clinical Triage</h1>", unsafe_allow_html=True)
    st.markdown("<div style='color: var(--text-muted); font-size: 1.1rem; margin-bottom: 32px;'>Fast patient assessment for clinical teams.</div>", unsafe_allow_html=True)

def render_ready_state():
    st.markdown("""
    <div class="glass-panel" style="text-align: center; padding: 60px 20px;">
        <h3 style="color: var(--text-main); margin-bottom: 12px; font-weight: 500;">READY FOR ASSESSMENT</h3>
        <p style="color: var(--text-muted); font-size: 1.1rem;">Enter a patient's narrative to begin AI-assisted clinical triage.</p>
    </div>
    """, unsafe_allow_html=True)

def render_session_overview():
    if not st.session_state.assessment_history:
        return
    
    total = len(st.session_state.assessment_history)
    emergencies = sum(1 for a in st.session_state.assessment_history if a['urgency'] == 'Emergency')
    urgents = sum(1 for a in st.session_state.assessment_history if a['urgency'] == 'Urgent')
    routines = sum(1 for a in st.session_state.assessment_history if a['urgency'] == 'Routine')
    
    st.markdown("<div class='section-label' style='margin-top: 40px;'>SESSION OVERVIEW</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display: flex; gap: 20px; font-size: 0.9rem; color: var(--text-muted);">
        <div>Total Assessments: <strong style="color: var(--text-main);">{total}</strong></div>
        <div>Emergency: <strong style="color: var(--danger);">{emergencies}</strong></div>
        <div>Urgent: <strong style="color: var(--warning);">{urgents}</strong></div>
        <div>Routine: <strong style="color: var(--success);">{routines}</strong></div>
    </div>
    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 8px; opacity: 0.7;">
        These values reflect current session history only and are not aggregate clinical performance metrics.
    </div>
    """, unsafe_allow_html=True)

def get_urgency_styling(urgency_level):
    level = urgency_level.upper()
    if level == "EMERGENCY":
        return {"bg": "rgba(239, 68, 68, 0.12)", "border": "var(--danger)", "text": "var(--danger)", "subtitle": "Immediate attention required"}
    elif level == "URGENT":
        return {"bg": "rgba(245, 158, 11, 0.12)", "border": "var(--warning)", "text": "var(--warning)", "subtitle": "Prompt clinical assessment required"}
    else:
        return {"bg": "rgba(16, 185, 129, 0.12)", "border": "var(--success)", "text": "var(--success)", "subtitle": "Suitable for standard clinical queue"}

# ==========================================
# 4. MAIN APPLICATION FLOW
# ==========================================
def main():
    inject_custom_css()
    render_sidebar()
    render_header()

    # --- PATIENT ASSESSMENT FORM ---
    st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>PATIENT ASSESSMENT</div>", unsafe_allow_html=True)

    col_lang, col_age, col_sex = st.columns([1.5, 1, 1])
    with col_lang:
        input_lang = st.selectbox("Language", ["Auto-Detect", "English", "Urdu", "Roman Urdu"])
    with col_age:
        input_age = st.number_input("Age", min_value=0, max_value=120, value=30, step=1)
    with col_sex:
        input_sex = st.selectbox("Sex", ["Male", "Female", "Other"])

    patient_text = st.text_area(
        "Patient Symptoms / Narrative",
        placeholder="e.g., I have chest pain since the last 10 minutes.",
        height=140
    )

    _, col_btn, _ = st.columns([1, 2, 1])
    with col_btn:
        analyze_btn = st.button("ANALYZE PATIENT")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- EVALUATION LOGIC ---
    if analyze_btn:
        if not patient_text.strip():
            st.warning("Please enter a patient narrative to proceed.")
        else:
            clinical_context = (
                f"Demographics: {input_age} yo {input_sex}. "
                f"Preferred Language: {input_lang}. "
                f"Complaint: {patient_text.strip()}"
            )
            
            with st.status("ANALYZING PATIENT", expanded=True) as status:
                st.write("Processing clinical narrative...")
                st.write("Extracting clinical signals...")
                st.write("Assessing urgency...")
                st.write("Preparing doctor summary...")
                
                try:
                    # STRICT BACKEND CALL - Unmodified
                    result = evaluate_patient(clinical_context, api_key=SYSTEM_API_KEY)
                    
                    # Update Session History
                    st.session_state.assessment_history.insert(0, {
                        "urgency": result.urgency_level,
                        "language": result.detected_language,
                        "summary": result.clinical_summary
                    })
                    
                    status.update(label="Analysis Complete", state="complete", expanded=False)
                    success = True
                except Exception as e:
                    status.update(label="Analysis Unavailable", state="error", expanded=False)
                    st.error("ANALYSIS UNAVAILABLE: The patient assessment could not be completed. Please try again.")
                    success = False

            # --- RESULT RENDERING ---
            if success:
                # 1. Workflow Visualizer
                st.markdown("""
                <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 24px; opacity: 0.8;">
                    <span class="workflow-step">PATIENT INPUT</span> <span class="workflow-arrow">→</span>
                    <span class="workflow-step">AI TRIAGE</span> <span class="workflow-arrow">→</span>
                    <span class="workflow-step">CLINICAL SIGNALS</span> <span class="workflow-arrow">→</span>
                    <span class="workflow-step" style="color: var(--primary);">URGENCY ASSESSMENT</span> <span class="workflow-arrow">→</span>
                    <span class="workflow-step">DOCTOR SUMMARY</span>
                </div>
                """, unsafe_allow_html=True)

                style = get_urgency_styling(result.urgency_level)
                
                # 2. Spectrum Visualization
                emerg_op = "1" if result.urgency_level.upper() == "EMERGENCY" else "0.3"
                urg_op = "1" if result.urgency_level.upper() == "URGENT" else "0.3"
                rout_op = "1" if result.urgency_level.upper() == "ROUTINE" else "0.3"
                
                st.markdown(f"""
                <div class="spectrum-container">
                    <div class="spectrum-item" style="color: var(--danger); opacity: {emerg_op}; border: 1px solid {'var(--danger)' if emerg_op=='1' else 'transparent'};">EMERGENCY</div>
                    <div class="spectrum-divider"></div>
                    <div class="spectrum-item" style="color: var(--warning); opacity: {urg_op}; border: 1px solid {'var(--warning)' if urg_op=='1' else 'transparent'};">URGENT</div>
                    <div class="spectrum-divider"></div>
                    <div class="spectrum-item" style="color: var(--success); opacity: {rout_op}; border: 1px solid {'var(--success)' if rout_op=='1' else 'transparent'};">ROUTINE</div>
                </div>
                """, unsafe_allow_html=True)

                # 3. Urgency Banner
                st.markdown(f"""
                <div class="urgency-banner" style="background: {style['bg']}; border-color: {style['border']};">
                    <div class="urgency-title" style="color: {style['text']};">{result.urgency_level.upper()}</div>
                    <div class="urgency-subtitle" style="color: {style['text']};">{style['subtitle']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 4. Clinical Details Panels
                col_summary, col_details = st.columns([1.2, 1])
                
                with col_summary:
                    st.markdown("<div class='glass-panel' style='height: 100%;'>", unsafe_allow_html=True)
                    st.markdown("<div class='section-label'>DOCTOR SUMMARY</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size: 1.1rem; line-height: 1.6; color: var(--text-main); margin-bottom: 24px;'>{result.clinical_summary}</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div class='section-label'>RECOMMENDED ACTION</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size: 1.05rem; padding-left: 12px; border-left: 3px solid var(--border); color: var(--text-main);'>{result.recommended_action}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                with col_details:
                    st.markdown("<div class='glass-panel' style='height: 100%;'>", unsafe_allow_html=True)
                    st.markdown("<div class='section-label'>CLINICAL SIGNALS</div>", unsafe_allow_html=True)
                    
                    # Convert identified symptoms to chips safely
                    if result.identified_symptoms:
                        chips_html = "".join([f"<div class='clinical-chip'>{sym.upper()}</div>" for sym in result.identified_symptoms])
                        st.markdown(chips_html, unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='color: var(--text-muted); font-size: 0.9rem;'>No specific clinical signals extracted.</div>", unsafe_allow_html=True)
                    
                    st.markdown("<div class='section-label' style='margin-top: 32px;'>ASSESSMENT METADATA</div>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style="margin-bottom: 8px;">
                        <span style="color: var(--text-muted); font-size: 0.9rem;">Detected Language:</span><br>
                        <span style="color: var(--text-main); font-weight: 500;">{result.detected_language}</span>
                    </div>
                    <div>
                        <span style="color: var(--text-muted); font-size: 0.9rem;">Triage Level Assigned:</span><br>
                        <span style="color: {style['text']}; font-weight: 600;">{result.urgency_level}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

    else:
        # Show empty state if no button click
        render_ready_state()

    render_session_overview()

    # --- SAFETY DISCLAIMER ---
    st.markdown("""
    <div style="text-align: center; color: var(--text-muted); font-size: 0.75rem; margin-top: 60px; padding-top: 24px; border-top: 1px solid var(--border); opacity: 0.7;">
        TriageFlow is an AI-assisted decision-support prototype and does not replace professional medical evaluation or emergency services.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
