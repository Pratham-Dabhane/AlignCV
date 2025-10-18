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
BRAND_COLORS = {
    "primary": "#1E3A8A",      # Deep blue
    "secondary": "#374151",    # Charcoal gray
    "accent": "#14B8A6",       # Teal accent
    "success": "#10B981",      # Green
    "warning": "#F59E0B",      # Orange
    "danger": "#EF4444",       # Red
    "light": "#F9FAFB",        # Light gray
    "white": "#FFFFFF"
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

# ============================================
# CUSTOM CSS
# ============================================
st.markdown(f"""
    <style>
    /* Global Styles */
    .main {{
        background-color: {BRAND_COLORS['light']};
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}
    
    /* Header with Logo */
    .brand-header {{
        text-align: center;
        padding: 2.5rem 0;
        background: linear-gradient(135deg, {BRAND_COLORS['primary']} 0%, {BRAND_COLORS['accent']} 100%);
        color: white;
        border-radius: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }}
    
    .brand-logo {{
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        letter-spacing: -0.05em;
    }}
    
    .brand-tagline {{
        font-size: 1.2rem;
        opacity: 0.95;
        font-weight: 300;
        letter-spacing: 0.05em;
    }}
    
    /* Cards */
    .info-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border-left: 4px solid {BRAND_COLORS['accent']};
    }}
    
    /* Buttons */
    .stButton>button {{
        background: linear-gradient(135deg, {BRAND_COLORS['primary']}, {BRAND_COLORS['accent']});
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(30, 58, 138, 0.3);
    }}
    
    /* Success/Error Messages */
    .success-box {{
        background-color: {BRAND_COLORS['success']};
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }}
    
    .error-box {{
        background-color: {BRAND_COLORS['danger']};
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {BRAND_COLORS['secondary']};
        color: white;
    }}
    
    section[data-testid="stSidebar"] .stMarkdown {{
        color: white;
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
""", unsafe_allow_html=True)

# ============================================
# HELPER FUNCTIONS
# ============================================

def render_header():
    """Render the branded header"""
    st.markdown("""
        <div class="brand-header">
            <div class="brand-logo">🎯 AlignCV</div>
            <div class="brand-tagline">Your Career, Aligned</div>
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
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 👤 User Menu")
        st.markdown(f"**{st.session_state.user.get('name', 'User')}**")
        st.markdown(f"*{st.session_state.user.get('email', '')}*")
        st.markdown("---")
        
        # Navigation menu
        page = st.radio(
            "Navigate to:",
            ["🏠 Dashboard", "📄 Documents", "💼 Jobs", "🔔 Notifications", "⚙️ Settings"],
            key="nav_radio"
        )
        
        st.markdown("---")
        
        if st.button("🚪 Logout", key="logout_btn"):
            logout()
    
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
