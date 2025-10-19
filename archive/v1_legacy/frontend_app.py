"""
AlignCV - Frontend Application
Phase 3: Enhanced UI/UX with Brand Integration
Streamlit interface for resume and job description analysis
"""

import streamlit as st
import requests
from typing import Optional
import json
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"
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
    initial_sidebar_state="collapsed"
)

# Custom CSS for Phase 3 Enhanced Branding
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
    
    .logo-placeholder {{
        width: 80px;
        height: 80px;
        background: rgba(255,255,255,0.2);
        border-radius: 50%;
        margin: 0 auto 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        backdrop-filter: blur(10px);
    }}
    
    .tagline {{
        font-size: 1.2rem;
        opacity: 0.95;
        font-weight: 300;
        letter-spacing: 0.5px;
        margin-top: 0.5rem;
    }}
    
    /* Text Areas */
    .stTextArea textarea {{
        font-family: 'Courier New', monospace;
        font-size: 14px;
        border-radius: 0.75rem;
        border: 2px solid {BRAND_COLORS['accent']};
        padding: 1rem;
        transition: all 0.3s ease;
    }}
    
    .stTextArea textarea:focus {{
        border-color: {BRAND_COLORS['primary']};
        box-shadow: 0 0 0 3px rgba(30, 58, 138, 0.1);
    }}
    
    /* Buttons */
    .stButton > button {{
        background: linear-gradient(135deg, {BRAND_COLORS['primary']} 0%, {BRAND_COLORS['accent']} 100%);
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3);
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 58, 138, 0.4);
    }}
    
    /* Score Card */
    .score-card {{
        background: linear-gradient(135deg, {{color}} 0%, {BRAND_COLORS['primary']} 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 1rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        margin: 2rem 0;
    }}
    
    .score-value {{
        font-size: 4rem;
        font-weight: 800;
        margin: 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }}
    
    /* Strength/Gap Cards */
    .item-card {{
        background: white;
        padding: 1rem 1.25rem;
        border-radius: 0.75rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid {{border_color}};
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }}
    
    .item-card:hover {{
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    
    /* Section Headers */
    .section-header {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {BRAND_COLORS['secondary']};
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid {BRAND_COLORS['accent']};
    }}
    
    /* Info Box */
    .info-box {{
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 4px solid {BRAND_COLORS['primary']};
        margin: 1rem 0;
    }}
    
    /* Progress Bar */
    .progress-container {{
        background: rgba(0,0,0,0.1);
        height: 30px;
        border-radius: 15px;
        overflow: hidden;
        margin: 1rem 0;
    }}
    
    .progress-bar {{
        height: 100%;
        background: linear-gradient(90deg, {BRAND_COLORS['accent']} 0%, {BRAND_COLORS['primary']} 100%);
        transition: width 1s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
    }}
    
    /* Character Counter */
    .char-counter {{
        font-size: 0.85rem;
        color: {BRAND_COLORS['secondary']};
        opacity: 0.7;
        text-align: right;
        margin-top: 0.25rem;
    }}
    
    /* Responsive Design */
    @media (max-width: 768px) {{
        .brand-header {{
            padding: 1.5rem 0;
        }}
        .score-value {{
            font-size: 3rem;
        }}
        .stButton > button {{
            width: 100%;
        }}
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
            timeout=120  # 2 minutes for first-time model download
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


def render_header():
    """Render branded header with logo"""
    st.markdown("""
        <div class="brand-header">
            <div class="logo-placeholder">🎯</div>
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: 800;">AlignCV</h1>
            <p class="tagline">Your Career, Aligned</p>
            <p style="font-size: 0.9rem; opacity: 0.9; margin-top: 0.5rem; font-weight: 300;">
                Professional • Trustworthy • Empowering • Clear
            </p>
        </div>
    """, unsafe_allow_html=True)


def render_progress_bar(percentage: float, label: str = ""):
    """Render animated progress bar"""
    color = (
        BRAND_COLORS['success'] if percentage >= 75
        else BRAND_COLORS['accent'] if percentage >= 60
        else BRAND_COLORS['warning'] if percentage >= 45
        else BRAND_COLORS['danger']
    )
    
    st.markdown(f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: {percentage}%; background: {color};">
                {label}
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_score_card(match_score: float):
    """Render match score card with color coding"""
    if match_score >= 75:
        score_color = BRAND_COLORS['success']
        score_label = "Excellent Match!"
        score_icon = "🎉"
        score_message = "Your resume strongly aligns with this job description."
    elif match_score >= 60:
        score_color = BRAND_COLORS['accent']
        score_label = "Good Match!"
        score_icon = "👍"
        score_message = "Your resume matches well with several key requirements."
    elif match_score >= 45:
        score_color = BRAND_COLORS['warning']
        score_label = "Fair Match"
        score_icon = "📊"
        score_message = "Your resume covers some requirements but needs strengthening."
    else:
        score_color = BRAND_COLORS['danger']
        score_label = "Needs Improvement"
        score_icon = "📈"
        score_message = "Consider tailoring your resume to better match this role."
    
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, {score_color} 0%, {BRAND_COLORS['primary']} 100%); 
                    color: white; padding: 2.5rem; border-radius: 1rem; text-align: center; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.15); margin: 2rem 0;">
            <p style="font-size: 1.2rem; margin: 0; opacity: 0.95;">{score_icon} Match Score</p>
            <h1 style="font-size: 4rem; font-weight: 800; margin: 1rem 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">
                {match_score}%
            </h1>
            <p style="font-size: 1.3rem; margin: 0.5rem 0; font-weight: 600;">{score_label}</p>
            <p style="font-size: 1rem; opacity: 0.9; margin-top: 1rem;">{score_message}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Progress bar
    render_progress_bar(match_score, f"{match_score}%")


def generate_actionable_checklist(strengths: list, gaps: list) -> str:
    """Generate downloadable actionable checklist"""
    checklist = f"""# AlignCV - Career Alignment Checklist
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

## ✅ Your Strengths (Keep Highlighting These!)

"""
    for i, strength in enumerate(strengths, 1):
        checklist += f"{i}. {strength}\n"
    
    checklist += f"""

## 📋 Action Items (To Improve Your Match)

"""
    for i, gap in enumerate(gaps, 1):
        checklist += f"{i}. [ ] {gap}\n"
    
    checklist += """

## 💡 Next Steps

1. Review each action item above
2. Update your resume to address the gaps
3. Emphasize your strengths more prominently
4. Run the analysis again to see your improved score!

---
Powered by AlignCV - Your Career, Aligned
"""
    return checklist


def main():
    """Main application interface - Phase 3 Enhanced"""
    
    # Header
    render_header()
    
    # Instructions
    with st.expander("📖 How to Use AlignCV", expanded=False):
        st.markdown("""
        <div class="info-box">
        <h3 style="margin-top: 0;">Simple 3-Step Process</h3>
        
        **Step 1: Paste Your Resume**  
        Copy your resume text into the left text box (minimum 50 characters)
        
        **Step 2: Paste the Job Description**  
        Copy the complete job description into the right text box
        
        **Step 3: Analyze & Get Insights**  
        Click the analyze button and receive:
        
        - 📊 **Match Score:** Semantic similarity (0-100%)
        - ✅ **Strengths:** What you're doing right
        - ⚠️ **Gaps:** What to improve
        - 📋 **Actionable Checklist:** Download your personalized improvement plan
        
        </div>
        """, unsafe_allow_html=True)
    
    # Input section
    st.markdown('<h2 class="section-header">📝 Input Your Information</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📄 Resume Text**")
        resume_text = st.text_area(
            "Paste your resume here",
            height=350,
            placeholder="Paste your resume text here...\n\nExample:\nJohn Doe\nSoftware Engineer\n\nEXPERIENCE:\n• 3 years Python development\n• Built REST APIs with FastAPI\n• Experience with Docker, PostgreSQL\n\nSKILLS:\nPython, FastAPI, Docker, SQL, Git",
            label_visibility="collapsed",
            key="resume_input"
        )
        resume_length = len(resume_text)
        resume_color = BRAND_COLORS['success'] if resume_length >= 50 else BRAND_COLORS['danger']
        st.markdown(f'<p class="char-counter" style="color: {resume_color};">Character count: {resume_length} {"✓" if resume_length >= 50 else "(min. 50)"}</p>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("**💼 Job Description**")
        job_description_text = st.text_area(
            "Paste job description here",
            height=350,
            placeholder="Paste the job description here...\n\nExample:\nSoftware Engineer Position\n\nREQUIREMENTS:\n• 2+ years Python experience\n• Experience with FastAPI or Flask\n• Knowledge of REST APIs\n• Database experience (SQL/NoSQL)\n• Docker/containerization skills",
            label_visibility="collapsed",
            key="jd_input"
        )
        jd_length = len(job_description_text)
        jd_color = BRAND_COLORS['success'] if jd_length >= 50 else BRAND_COLORS['danger']
        st.markdown(f'<p class="char-counter" style="color: {jd_color};">Character count: {jd_length} {"✓" if jd_length >= 50 else "(min. 50)"}</p>', unsafe_allow_html=True)
    
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
            with st.spinner("🔄 Analyzing your resume... (First run may take 1-2 minutes to download model)"):
                result = call_api(resume_text, job_description_text)
            
            if result:
                st.success("✅ Analysis Complete!")
                
                # Display results
                st.markdown('<h2 class="section-header">📊 Your Results</h2>', unsafe_allow_html=True)
                
                # Match Score Card
                match_score = result.get("match_score", 0)
                render_score_card(match_score)
                
                st.markdown("---")
                
                # Strengths and Gaps in Collapsible Sections
                strengths = result.get("strengths", [])
                gaps = result.get("gaps", [])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    with st.expander(f"✅ Your Strengths ({len(strengths)})", expanded=True):
                        st.markdown('<p style="color: #6B7280; margin-bottom: 1rem; font-size: 0.95rem;">These are the requirements you already meet. Keep highlighting these in your resume!</p>', unsafe_allow_html=True)
                        
                        if strengths:
                            for i, strength in enumerate(strengths, 1):
                                st.markdown(f"""
                                    <div class="item-card" style="border-left-color: {BRAND_COLORS['success']};">
                                        <strong style="color: {BRAND_COLORS['success']};">#{i}</strong>
                                        <p style="margin: 0.5rem 0 0 0; color: {BRAND_COLORS['secondary']};">{strength}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("💡 No specific strengths identified. Try providing more detailed information in your resume.")
                
                with col2:
                    with st.expander(f"⚠️ Areas to Improve ({len(gaps)})", expanded=True):
                        st.markdown('<p style="color: #6B7280; margin-bottom: 1rem; font-size: 0.95rem;">Focus on addressing these gaps to improve your match score.</p>', unsafe_allow_html=True)
                        
                        if gaps:
                            for i, gap in enumerate(gaps, 1):
                                st.markdown(f"""
                                    <div class="item-card" style="border-left-color: {BRAND_COLORS['warning']};">
                                        <strong style="color: {BRAND_COLORS['warning']};">#{i}</strong>
                                        <p style="margin: 0.5rem 0 0 0; color: {BRAND_COLORS['secondary']};">{gap}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.success("🎉 No significant gaps found! Your resume looks well-aligned with this job description.")
                
                # Actionable Checklist Download
                st.markdown("---")
                st.markdown('<h2 class="section-header">📋 Actionable Checklist</h2>', unsafe_allow_html=True)
                
                checklist_content = generate_actionable_checklist(strengths, gaps)
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"""
                        <div class="info-box">
                            <strong>📥 Download Your Personalized Improvement Plan</strong>
                            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                                Get a checklist with {len(gaps)} action items to improve your resume match score.
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.download_button(
                        label="📥 Download Checklist",
                        data=checklist_content,
                        file_name=f"aligncv_checklist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                
                with col3:
                    if st.button("📋 Copy to Clipboard", use_container_width=True):
                        st.code(checklist_content, language="markdown")
                        st.success("✅ Checklist shown below - copy manually")
                
                # Show preview of checklist
                with st.expander("👀 Preview Checklist", expanded=False):
                    st.markdown(checklist_content)
                
                # Message
                if result.get("message"):
                    st.info(f"ℹ️ {result['message']}")
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
        <div style="text-align: center; opacity: 0.7; padding: 2rem 0 1rem 0;">
            <p style="font-size: 1.1rem; font-weight: 600; color: {BRAND_COLORS['primary']}; margin-bottom: 0.5rem;">
                AlignCV v0.3.0 - Phase 3: Enhanced UX & Branding ✅
            </p>
            <p style="font-size: 0.9rem; color: {BRAND_COLORS['secondary']}; margin: 0.25rem 0;">
                Built with FastAPI + Streamlit + Sentence-BERT
            </p>
            <p style="font-size: 0.85rem; color: {BRAND_COLORS['secondary']}; opacity: 0.8; margin: 0.25rem 0;">
                Using all-MiniLM-L6-v2 model for semantic analysis • 100% Free & Open Source
            </p>
            <p style="font-size: 0.8rem; color: {BRAND_COLORS['accent']}; margin-top: 1rem;">
                🎯 Your Career, Aligned
            </p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
