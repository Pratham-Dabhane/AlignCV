"""
AlignCV - Frontend Application
Streamlit interface for resume and job description analysis
"""

import streamlit as st
import requests
from typing import Optional

# Configuration
API_URL = "http://localhost:8000"
BRAND_COLORS = {
    "primary": "#1E3A8A",      # Deep blue
    "secondary": "#374151",    # Charcoal gray
    "accent": "#14B8A6"        # Teal accent
}

# Page configuration
st.set_page_config(
    page_title="AlignCV - Your Career, Aligned",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for branding
st.markdown(f"""
    <style>
    .main {{
        background-color: #F9FAFB;
    }}
    .stTextArea textarea {{
        font-family: 'Courier New', monospace;
        font-size: 14px;
    }}
    .success-box {{
        background-color: #D1FAE5;
        border-left: 4px solid {BRAND_COLORS['accent']};
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }}
    .warning-box {{
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }}
    .header-container {{
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, {BRAND_COLORS['primary']} 0%, {BRAND_COLORS['accent']} 100%);
        color: white;
        border-radius: 1rem;
        margin-bottom: 2rem;
    }}
    </style>
""", unsafe_allow_html=True)


def call_api(resume_text: str, job_description_text: str) -> Optional[dict]:
    """
    Call the backend API to analyze resume and job description
    
    Args:
        resume_text: Resume content
        job_description_text: Job description content
        
    Returns:
        API response as dictionary or None if error
    """
    try:
        response = requests.post(
            f"{API_URL}/analyze",
            json={
                "resume_text": resume_text,
                "job_description_text": job_description_text
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend API. Make sure the server is running at http://localhost:8000")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. Please try again.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API Error: {str(e)}")
        return None


def main():
    """Main application interface"""
    
    # Header
    st.markdown("""
        <div class="header-container">
            <h1>🎯 AlignCV</h1>
            <p style="font-size: 1.2rem; margin: 0;">Your Career, Aligned</p>
            <p style="font-size: 0.9rem; opacity: 0.9; margin-top: 0.5rem;">
                Professional • Trustworthy • Empowering • Clear
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Instructions
    with st.expander("📖 How to Use AlignCV", expanded=False):
        st.markdown("""
        **Simple 3-Step Process:**
        1. **Paste your resume** in the left text box
        2. **Paste the job description** in the right text box
        3. **Click Analyze** to see your match score, strengths, and gaps
        
        **What you'll get:**
        - 📊 Match Score: How well your resume aligns with the job
        - ✅ Strengths: What's already great in your resume
        - ⚠️ Gaps: What's missing or needs improvement
        - 📋 Actionable Checklist: Specific next steps (coming in future phases)
        """)
    
    # Input section
    st.markdown("### 📝 Input Your Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Resume Text**")
        resume_text = st.text_area(
            "Paste your resume here",
            height=300,
            placeholder="Paste your resume text here...\n\nExample:\nJohn Doe\nSoftware Engineer\n\nExperience:\n- 3 years Python development\n- Built REST APIs with FastAPI\n...",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("**Job Description**")
        job_description_text = st.text_area(
            "Paste job description here",
            height=300,
            placeholder="Paste the job description here...\n\nExample:\nWe are looking for a Software Engineer with:\n- 2+ years Python experience\n- Experience with FastAPI or Flask\n- Knowledge of REST APIs\n...",
            label_visibility="collapsed"
        )
    
    # Character count
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.caption(f"Resume: {len(resume_text)} characters")
    with col2:
        st.caption(f"Job Description: {len(job_description_text)} characters")
    
    # Analyze button
    st.markdown("---")
    analyze_button = st.button("🔍 Analyze Match", type="primary", use_container_width=True)
    
    # Process analysis
    if analyze_button:
        if not resume_text or not job_description_text:
            st.warning("⚠️ Please provide both resume text and job description.")
        elif len(resume_text) < 50 or len(job_description_text) < 50:
            st.warning("⚠️ Please provide more detailed resume and job description (at least 50 characters each).")
        else:
            with st.spinner("🔄 Analyzing your resume..."):
                result = call_api(resume_text, job_description_text)
            
            if result:
                st.success("✅ Analysis Complete!")
                
                # Display results
                st.markdown("### 📊 Results")
                
                # Match Score
                match_score = result.get("match_score", 0)
                st.markdown(f"""
                    <div style="background-color: {BRAND_COLORS['primary']}; color: white; padding: 2rem; border-radius: 1rem; text-align: center;">
                        <h2 style="margin: 0; color: white;">Match Score</h2>
                        <h1 style="margin: 0.5rem 0; font-size: 3rem; color: white;">{match_score}%</h1>
                        <p style="margin: 0; opacity: 0.9;">Phase 1: Dummy data - Real matching coming in Phase 2</p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Strengths and Gaps
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### ✅ Strengths")
                    strengths = result.get("strengths", [])
                    if strengths:
                        for strength in strengths:
                            st.markdown(f"- {strength}")
                    else:
                        st.info("Phase 1: Strengths analysis coming in Phase 3")
                
                with col2:
                    st.markdown("### ⚠️ Gaps to Address")
                    gaps = result.get("gaps", [])
                    if gaps:
                        for gap in gaps:
                            st.markdown(f"- {gap}")
                    else:
                        st.info("Phase 1: Gap analysis coming in Phase 3")
                
                # Message
                if result.get("message"):
                    st.info(f"ℹ️ {result['message']}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; opacity: 0.6; padding: 1rem;">
            <p>AlignCV v0.1.0 - Phase 1: Foundations & Core Architecture</p>
            <p>Built with FastAPI + Streamlit • Free & Open Source</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
