"""
Dashboard Page - Main landing after login
"""

import streamlit as st
import requests
from datetime import datetime

API_URL = "https://aligncv-e55h.onrender.com/v2"

def get_headers():
    """Get auth headers for API requests"""
    return {
        "Authorization": f"Bearer {st.session_state.access_token}"
    }

def show_dashboard():
    """Show the main dashboard"""
    
    st.markdown("## 🏠 Dashboard")
    st.markdown(f"### Welcome back, {st.session_state.user.get('name', 'User')}! 👋")
    st.markdown("Here's your job search overview")
    st.markdown("")  # Spacing
    
    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📄 Documents",
            value="0",
            help="Total resumes uploaded"
        )
    
    with col2:
        st.metric(
            label="💼 Jobs Matched",
            value="0",
            help="Jobs matching your profile"
        )
    
    with col3:
        st.metric(
            label="⭐ Bookmarks",
            value="0",
            help="Saved job opportunities"
        )
    
    with col4:
        st.metric(
            label="✅ Applications",
            value="0",
            help="Jobs you've applied to"
        )
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### 🚀 Quick Actions")
    st.markdown("Get started with these essential features")
    st.markdown("")  # Spacing
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Upload Resume", use_container_width=True, type="primary", help="Upload and optimize your resume"):
            st.session_state.navigate_to = "📄 Documents"
            st.rerun()
    
    with col2:
        if st.button("🔍 Find Jobs", use_container_width=True, type="primary", help="Search for matching opportunities"):
            st.session_state.navigate_to = "💼 Jobs"
            st.rerun()
    
    with col3:
        if st.button("🔔 Notifications", use_container_width=True, type="primary", help="Check your updates"):
            st.session_state.navigate_to = "🔔 Notifications"
            st.rerun()
    
    st.markdown("---")
    
    # Recent Activity
    st.markdown("### 📊 Recent Activity")
    st.markdown("Stay updated with your latest actions")
    st.markdown("")  # Spacing
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📄 Recent Documents")
        st.info("💡 No documents uploaded yet. Upload your resume to get started!")
    
    with col2:
        st.markdown("#### 🔔 Recent Notifications")
        st.info("💡 No notifications yet. We'll keep you posted on matching jobs!")
    
    st.markdown("---")
    
    # Getting Started Guide
    with st.expander("📚 Getting Started Guide", expanded=False):
        st.markdown("""
        ### How to use AlignCV:
        
        1. **📤 Upload Your Resume**
           - Go to Documents page
           - Upload your resume (PDF or DOCX)
           - Our AI will extract your skills and experience
        
        2. **✨ Optimize with AI**
           - Use our AI rewriting feature
           - Get ATS-friendly suggestions
           - Improve your resume content
        
        3. **🔍 Find Matching Jobs**
           - Browse through matched jobs
           - See your compatibility score
           - Bookmark interesting opportunities
        
        4. **📝 Track Applications**
           - Mark jobs as applied
           - Track application status
           - Get notifications on updates
        
        5. **🔔 Stay Notified**
           - Get email alerts for new matches
           - Configure your preferences
           - Never miss an opportunity
        """)
    
    # Tips
    with st.expander("💡 Pro Tips", expanded=False):
        st.markdown("""
        - **Keep your resume updated**: Re-upload whenever you gain new skills
        - **Use AI rewriting**: Tailor your resume for specific job types
        - **Set notification preferences**: Get alerts for high-match jobs (>80%)
        - **Bookmark early**: Don't lose track of great opportunities
        - **Track everything**: Use application tracking to stay organized
        """)
    
    # Footer info
    st.markdown("---")
    st.caption(f"💻 AlignCV v2.0 | Last login: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
