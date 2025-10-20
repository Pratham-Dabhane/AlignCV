"""
AlignCV V2 - Modern Frontend Application
Main entry point with authentication and routing
"""

import streamlit as st
import requests
from datetime import datetime
import json

# ============================================
# CONFIGURATION
# ============================================
API_URL = "http://localhost:8001/v2"  # Updated to V2 API

# Professional Brand Colors - Enhanced palette
BRAND_COLORS = {
    "primary": "#2563EB",       # Vibrant blue
    "primary_dark": "#1E40AF",  # Dark blue
    "primary_light": "#3B82F6", # Light blue
    "secondary": "#1F2937",     # Rich charcoal
    "secondary_light": "#374151", # Medium gray
    "accent": "#06B6D4",        # Cyan accent
    "accent_light": "#22D3EE",  # Light cyan
    "success": "#10B981",       # Emerald green
    "success_light": "#34D399", # Light green
    "warning": "#F59E0B",       # Amber
    "warning_light": "#FBBF24", # Light amber
    "danger": "#EF4444",        # Red
    "danger_light": "#F87171",  # Light red
    "light": "#F9FAFB",         # Off-white
    "light_gray": "#E5E7EB",    # Light gray
    "white": "#FFFFFF",
    "dark": "#111827",          # Almost black
    "text_primary": "#111827",
    "text_secondary": "#6B7280",
    "text_light": "#9CA3AF"
}

# Page configuration
st.set_page_config(
    page_title="AlignCV - Your Career, Aligned",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"
if "navigate_to" not in st.session_state:
    st.session_state.navigate_to = None

# ============================================
# PROFESSIONAL CUSTOM CSS
# ============================================
st.markdown(f"""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}
    
    .main {{
        background: linear-gradient(135deg, {BRAND_COLORS['light']} 0%, #FFFFFF 100%);
        font-family: 'Inter', sans-serif;
    }}
    
    /* Smooth animations for all transitions */
    * {{
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    
    /* Header with modern gradient and glassmorphism */
    .brand-header {{
        text-align: center;
        padding: 3.5rem 2rem;
        background: linear-gradient(135deg, {BRAND_COLORS['primary']} 0%, {BRAND_COLORS['accent']} 100%);
        color: white;
        border-radius: 1.5rem;
        margin-bottom: 2.5rem;
        box-shadow: 0 20px 60px rgba(37, 99, 235, 0.15), 0 0 0 1px rgba(255,255,255,0.1);
        position: relative;
        overflow: hidden;
    }}
    
    .brand-header::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 100%);
        pointer-events: none;
    }}
    
    .brand-logo {{
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.75rem;
        letter-spacing: -0.05em;
        text-shadow: 0 2px 20px rgba(0,0,0,0.1);
        position: relative;
        z-index: 1;
    }}
    
    .brand-tagline {{
        font-size: 1.25rem;
        opacity: 0.95;
        font-weight: 400;
        letter-spacing: 0.05em;
        position: relative;
        z-index: 1;
    }}
    
    /* Professional Cards with depth */
    .info-card {{
        background: white;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06), 0 0 0 1px rgba(0,0,0,0.04);
        margin-bottom: 1.5rem;
        border-left: 4px solid {BRAND_COLORS['accent']};
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }}
    
    .info-card:hover {{
        box-shadow: 0 8px 30px rgba(0,0,0,0.12), 0 0 0 1px rgba(0,0,0,0.06);
        transform: translateY(-2px);
    }}
    
    /* Modern Buttons */
    .stButton>button {{
        background: linear-gradient(135deg, {BRAND_COLORS['primary']}, {BRAND_COLORS['primary_light']});
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.875rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        letter-spacing: 0.025em;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(37, 99, 235, 0.4);
        background: linear-gradient(135deg, {BRAND_COLORS['primary_dark']}, {BRAND_COLORS['primary']});
    }}
    
    .stButton>button:active {{
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
    }}
    
    /* Input Fields with modern styling */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        border: 2px solid {BRAND_COLORS['light_gray']};
        border-radius: 0.75rem;
        padding: 0.875rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: white;
    }}
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {{
        border-color: {BRAND_COLORS['primary']};
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
        outline: none;
    }}
    
    /* Select boxes */
    .stSelectbox>div>div>div {{
        border: 2px solid {BRAND_COLORS['light_gray']};
        border-radius: 0.75rem;
        transition: all 0.3s ease;
    }}
    
    .stSelectbox>div>div>div:hover {{
        border-color: {BRAND_COLORS['primary_light']};
    }}
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
        background-color: {BRAND_COLORS['light']};
        padding: 0.5rem;
        border-radius: 1rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        border-radius: 0.75rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: {BRAND_COLORS['text_secondary']};
    }}
    
    .stTabs [aria-selected="true"] {{
        background: white;
        color: {BRAND_COLORS['primary']};
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    
    /* Success/Info/Warning/Error Messages */
    .element-container .stAlert {{
        border-radius: 0.75rem;
        border: none;
        padding: 1rem 1.25rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }}
    
    .success-box {{
        background: linear-gradient(135deg, {BRAND_COLORS['success']} 0%, {BRAND_COLORS['success_light']} 100%);
        color: white;
        padding: 1.25rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3);
    }}
    
    .error-box {{
        background: linear-gradient(135deg, {BRAND_COLORS['danger']} 0%, {BRAND_COLORS['danger_light']} 100%);
        color: white;
        padding: 1.25rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(239, 68, 68, 0.3);
    }}
    
    .warning-box {{
        background: linear-gradient(135deg, {BRAND_COLORS['warning']} 0%, {BRAND_COLORS['warning_light']} 100%);
        color: white;
        padding: 1.25rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(245, 158, 11, 0.3);
    }}
    
    /* Sidebar with modern design */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {BRAND_COLORS['secondary']} 0%, {BRAND_COLORS['secondary_light']} 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }}
    
    section[data-testid="stSidebar"] .stMarkdown {{
        color: white;
    }}
    
    section[data-testid="stSidebar"] .stRadio>div {{
        background-color: rgba(255,255,255,0.05);
        padding: 1rem;
        border-radius: 0.75rem;
    }}
    
    section[data-testid="stSidebar"] .stRadio>div>label {{
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 0.5rem;
        transition: all 0.3s ease;
    }}
    
    section[data-testid="stSidebar"] .stRadio>div>label:hover {{
        background-color: rgba(255,255,255,0.1);
    }}
    
    section[data-testid="stSidebar"] [role="radio"][aria-checked="true"] {{
        background: linear-gradient(135deg, {BRAND_COLORS['primary']} 0%, {BRAND_COLORS['accent']} 100%);
        border-radius: 0.5rem;
    }}
    
    /* Metrics cards */
    [data-testid="stMetricValue"] {{
        font-size: 2rem;
        font-weight: 700;
        color: {BRAND_COLORS['primary']};
    }}
    
    [data-testid="stMetricLabel"] {{
        font-size: 0.875rem;
        font-weight: 600;
        color: {BRAND_COLORS['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    [data-testid="metric-container"] {{
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        border: 1px solid {BRAND_COLORS['light_gray']};
    }}
    
    [data-testid="metric-container"]:hover {{
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }}
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {{
        background: white;
        border: 2px dashed {BRAND_COLORS['primary_light']};
        border-radius: 1rem;
        padding: 2rem;
        transition: all 0.3s ease;
    }}
    
    [data-testid="stFileUploader"]:hover {{
        border-color: {BRAND_COLORS['primary']};
        background: {BRAND_COLORS['light']};
    }}
    
    /* Expander styling */
    .streamlit-expanderHeader {{
        background: white;
        border-radius: 0.75rem;
        border: 1px solid {BRAND_COLORS['light_gray']};
        padding: 1rem 1.5rem;
        font-weight: 600;
        color: {BRAND_COLORS['text_primary']};
        transition: all 0.3s ease;
    }}
    
    .streamlit-expanderHeader:hover {{
        background: {BRAND_COLORS['light']};
        border-color: {BRAND_COLORS['primary_light']};
    }}
    
    .streamlit-expanderContent {{
        background: white;
        border-radius: 0 0 0.75rem 0.75rem;
        border: 1px solid {BRAND_COLORS['light_gray']};
        border-top: none;
        padding: 1.5rem;
    }}
    
    /* Dividers */
    hr {{
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, {BRAND_COLORS['light_gray']}, transparent);
    }}
    
    /* Loading spinner */
    .stSpinner>div {{
        border-top-color: {BRAND_COLORS['primary']};
    }}
    
    /* Progress bar */
    .stProgress>div>div>div>div {{
        background: linear-gradient(90deg, {BRAND_COLORS['primary']}, {BRAND_COLORS['accent']});
        border-radius: 1rem;
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{visibility: hidden;}}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {BRAND_COLORS['light']};
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {BRAND_COLORS['primary_light']};
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {BRAND_COLORS['primary']};
    }}
    
    /* Responsive typography */
    h1 {{
        font-size: 2.5rem;
        font-weight: 800;
        color: {BRAND_COLORS['text_primary']};
        letter-spacing: -0.025em;
    }}
    
    h2 {{
        font-size: 2rem;
        font-weight: 700;
        color: {BRAND_COLORS['text_primary']};
        letter-spacing: -0.025em;
        margin-bottom: 1rem;
    }}
    
    h3 {{
        font-size: 1.5rem;
        font-weight: 600;
        color: {BRAND_COLORS['text_primary']};
        margin-bottom: 0.75rem;
    }}
    
    p {{
        color: {BRAND_COLORS['text_secondary']};
        line-height: 1.6;
        font-size: 1rem;
    }}
    
    /* Link styling */
    a {{
        color: {BRAND_COLORS['primary']};
        text-decoration: none;
        font-weight: 500;
        transition: all 0.3s ease;
    }}
    
    a:hover {{
        color: {BRAND_COLORS['primary_dark']};
        text-decoration: underline;
    }}
    </style>
""", unsafe_allow_html=True)

# ============================================
# HELPER FUNCTIONS
# ============================================

def render_header():
    """Render the branded header with modern design"""
    st.markdown("""
        <div class="brand-header">
            <div class="brand-logo">🎯 AlignCV</div>
            <div class="brand-tagline">Your Career, Perfectly Aligned</div>
        </div>
    """, unsafe_allow_html=True)

def logout():
    """Clear session and logout"""
    st.session_state.authenticated = False
    st.session_state.access_token = None
    st.session_state.user = None
    st.session_state.current_page = "login"
    st.rerun()

# ============================================
# MAIN APP
# ============================================

def main():
    render_header()
    
    # If not authenticated, show login/signup
    if not st.session_state.authenticated:
        from pages.auth import show_auth_page
        show_auth_page()
    else:
        # Show authenticated app with sidebar navigation
        show_authenticated_app()

def show_authenticated_app():
    """Show the main app for authenticated users"""
    
    # Check if there's a navigation request from buttons
    default_index = 0
    if st.session_state.navigate_to:
        nav_options = ["🏠 Dashboard", "📄 Documents", "💼 Jobs", "🔔 Notifications", "⚙️ Settings"]
        if st.session_state.navigate_to in nav_options:
            default_index = nav_options.index(st.session_state.navigate_to)
        st.session_state.navigate_to = None
    
    # Sidebar navigation with modern design
    with st.sidebar:
        st.markdown("### 👤 User Profile")
        st.markdown(f"**{st.session_state.user.get('name', 'User')}**")
        st.markdown(f"*{st.session_state.user.get('email', '')}*")
        st.markdown("---")
        
        # Navigation menu
        page = st.radio(
            "Navigate to:",
            ["🏠 Dashboard", "📄 Documents", "💼 Jobs", "🔔 Notifications", "⚙️ Settings"],
            key="nav_radio",
            index=default_index
        )
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
            logout()
        
        # Footer in sidebar
        st.markdown("---")
        st.caption("💼 AlignCV v2.0")
        st.caption(f"🕒 {datetime.now().strftime('%B %d, %Y')}")
    
    # Route to appropriate page
    if "Dashboard" in page:
        from pages.dashboard import show_dashboard
        show_dashboard()
    elif "Documents" in page:
        from pages.documents import show_documents
        show_documents()
    elif "Jobs" in page:
        from pages.jobs import show_jobs
        show_jobs()
    elif "Notifications" in page:
        from pages.notifications import show_notifications
        show_notifications()
    elif "Settings" in page:
        from pages.settings import show_settings
        show_settings()

if __name__ == "__main__":
    main()
