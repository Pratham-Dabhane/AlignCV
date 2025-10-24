"""
Documents Page - Resume upload and management
"""

import streamlit as st
import requests
from datetime import datetime

API_URL = "https://aligncv-e55h.onrender.com/v2"

def get_headers():
    """Get auth headers"""
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

def show_documents():
    """Show documents page"""
    st.markdown("## 📄 My Documents")
    st.markdown("Upload, manage, and optimize your resumes with AI")
    st.markdown("")  # Spacing
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload New", "📂 My Documents", "🎯 Tailor to Job", "✨ AI Rewrite"])
    
    with tab1:
        show_upload_section()
    
    with tab2:
        show_documents_list()
    
    with tab3:
        show_tailor_to_job_section()
    
    with tab4:
        show_ai_rewrite_section()

def show_upload_section():
    """Upload resume section"""
    st.markdown("### 📤 Upload Your Resume")
    st.markdown("Upload your resume in PDF or DOCX format for AI analysis and optimization")
    st.markdown("")  # Spacing
    
    uploaded_file = st.file_uploader(
        "Drop your file here or click to browse",
        type=['pdf', 'docx'],
        help="Supported formats: PDF, DOCX • Maximum size: 5MB",
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        # Show file details
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"� **File**: {uploaded_file.name}")
        with col2:
            file_size = uploaded_file.size / 1024  # Convert to KB
            st.info(f"📊 **Size**: {file_size:.2f} KB")
        
        if st.button("🚀 Upload Resume", type="primary", use_container_width=True):
            with st.spinner("Uploading and processing your resume..."):
                try:
                    # Prepare file for upload
                    files = {
                        'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
                    }
                    
                    # Upload to API
                    response = requests.post(
                        f"{API_URL}/documents/upload",
                        files=files,
                        headers=get_headers(),
                        timeout=30
                    )
                    
                    if response.status_code in [200, 201]:
                        data = response.json()
                        st.success(f"✅ Resume uploaded successfully!")
                        st.balloons()
                        
                        # Show extracted info
                        with st.expander("📊 Extracted Information", expanded=True):
                            st.markdown(f"**Document ID**: {data.get('document_id')}")
                            st.markdown(f"**Filename**: {data.get('file_name')}")
                            st.markdown(f"**Size**: {data.get('file_size', 0) / 1024:.2f} KB")
                            
                            if 'parsed_text' in data:
                                st.markdown("**Extracted Text Preview**:")
                                st.text_area(
                                    "Preview",
                                    data['parsed_text'],
                                    height=200,
                                    disabled=True
                                )
                            
                            if 'skills' in data and data['skills']:
                                st.markdown("**Skills Detected**:")
                                st.write(", ".join(data['skills'][:10]))
                            
                            if 'roles' in data and data['roles']:
                                st.markdown("**Roles Detected**:")
                                st.write(", ".join(data['roles'][:5]))
                        
                        st.info("💡 Go to 'AI Rewrite' tab to optimize your resume!")
                    else:
                        error_msg = response.json().get('detail', 'Upload failed')
                        st.error(f"❌ {error_msg}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to server. Is the backend running?")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

def show_documents_list():
    """Show list of uploaded documents"""
    st.markdown("### 📂 Your Uploaded Documents")
    st.markdown("View and manage all your resume versions")
    st.markdown("")  # Spacing
    
    try:
        # Fetch documents from API
        response = requests.get(
            f"{API_URL}/documents/",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            # API returns {"documents": [...], "total": N}
            documents = data.get("documents", []) if isinstance(data, dict) else data
            
            if not documents or len(documents) == 0:
                st.info("📭 No documents uploaded yet. Upload your first resume!")
            else:
                st.success(f"📂 You have {len(documents)} document(s)")
                
                # Display each document
                for doc in documents:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                        
                        with col1:
                            st.markdown(f"**📄 {doc.get('file_name', 'Untitled')}**")
                        
                        with col2:
                            file_size = doc.get('file_size', 0) / 1024
                            st.markdown(f"📊 {file_size:.2f} KB")
                        
                        with col3:
                            created = doc.get('created_at', '')
                            if created:
                                date_obj = datetime.fromisoformat(created.replace('Z', '+00:00'))
                                st.markdown(f"📅 {date_obj.strftime('%b %d, %Y')}")
                        
                        with col4:
                            if st.button("🗑️", key=f"delete_{doc.get('id')}", help="Delete document"):
                                delete_document(doc.get('id'))
                        
                        # Show preview in expander
                        with st.expander("👁️ View Details"):
                            st.markdown(f"**Type**: {doc.get('file_type', 'Unknown')}")
                            st.markdown(f"**ID**: {doc.get('id')}")
                            
                            if 'extracted_text' in doc and doc['extracted_text']:
                                st.markdown("**Extracted Text**:")
                                st.text_area(
                                    "Text",
                                    doc['extracted_text'][:500] + "...",
                                    height=150,
                                    disabled=True,
                                    key=f"text_{doc.get('id')}"
                                )
                        
                        st.markdown("---")
        else:
            st.error("❌ Failed to load documents")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to server")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def delete_document(doc_id):
    """Delete a document"""
    try:
        response = requests.delete(
            f"{API_URL}/documents/{doc_id}",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            st.success("✅ Document deleted!")
            st.rerun()
        else:
            st.error("❌ Failed to delete document")
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


def show_tailor_to_job_section():
    """
    PHASE 9: Resume Tailoring to Job Description
    The killer feature that makes AlignCV stand out!
    """
    st.markdown("### 🎯 Tailor Resume to Job Description")
    st.markdown("**Optimize your resume for a specific job posting**")
    
    st.info("💡 **How it works**: Paste a job description, and our AI will analyze gaps, suggest keywords, and generate a tailored resume that maximizes your match score!")
    
    # Get documents first
    try:
        response = requests.get(
            f"{API_URL}/documents/",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            # API returns {"documents": [...], "total": N}
            documents = data.get("documents", []) if isinstance(data, dict) else data
            
            if not documents or len(documents) == 0:
                st.warning("📭 Please upload a resume first before tailoring")
                return
            
            # Select document
            doc_options = {doc['file_name']: doc for doc in documents}
            selected_doc_name = st.selectbox(
                "Select Your Resume",
                options=list(doc_options.keys()),
                help="Choose which resume to tailor",
                key="tailor_doc_select"
            )
            
            selected_doc = doc_options[selected_doc_name]
            
            # Job description input
            st.markdown("---")
            st.markdown("#### 📋 Paste Job Description")
            
            job_description = st.text_area(
                "Full Job Posting",
                placeholder="""Paste the complete job description here, including:
- Job title
- Required skills
- Responsibilities
- Qualifications
- Company info

Example:
Senior Python Developer
We're looking for an experienced Python developer with...
- 5+ years Python experience
- FastAPI, Django expertise
- AWS, Docker, Kubernetes
- etc.
""",
                height=250,
                help="The more detailed the job description, the better the tailoring!",
                key="job_desc_input"
            )
            
            # Tailoring level selector
            st.markdown("---")
            st.markdown("#### ⚙️ Tailoring Settings")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                tailoring_level = st.select_slider(
                    "Tailoring Level",
                    options=["conservative", "moderate", "aggressive"],
                    value="moderate",
                    help="""
                    - Conservative: Minimal changes, maintains authenticity
                    - Moderate: Balanced optimization (recommended)
                    - Aggressive: Comprehensive restructuring for maximum match
                    """,
                    key="tailoring_level"
                )
            
            with col2:
                level_emoji = {
                    "conservative": "🛡️",
                    "moderate": "⚖️",
                    "aggressive": "🚀"
                }
                st.markdown(f"### {level_emoji[tailoring_level]}")
            
            # Explanation of each level
            level_descriptions = {
                "conservative": "✅ Minimal changes • ✅ Maintains authenticity • ✅ Safe for all applications",
                "moderate": "✅ Balanced optimization • ✅ Strategic keyword placement • ✅ Recommended for most jobs",
                "aggressive": "✅ Maximum match score • ✅ Comprehensive restructuring • ✅ Best for dream jobs"
            }
            st.caption(level_descriptions[tailoring_level])
            
            # Show original resume preview
            with st.expander("📄 Your Original Resume Preview", expanded=False):
                st.text_area(
                    "Original",
                    selected_doc.get('extracted_text', 'No text available')[:1000] + "...",
                    height=200,
                    disabled=True,
                    key="original_preview"
                )
            
            # Tailor button
            st.markdown("---")
            
            if len(job_description.strip()) < 50:
                st.warning("⚠️ Please paste a job description (at least 50 characters)")
            else:
                if st.button("🎯 Tailor My Resume", type="primary", use_container_width=True):
                    with st.spinner(f"🧠 Analyzing job requirements and tailoring your resume ({tailoring_level} mode)..."):
                        try:
                            # Call tailoring API
                            response = requests.post(
                                f"{API_URL}/rewrite/tailor-to-job",
                                json={
                                    "resume_id": selected_doc.get('id'),
                                    "job_description": job_description,
                                    "tailoring_level": tailoring_level
                                },
                                headers=get_headers(),
                                timeout=60  # Longer timeout for AI processing
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                
                                # Check if API is in fallback mode
                                if data.get('api_status') == 'fallback' or data.get('warning'):
                                    st.warning(f"⚠️ {data.get('warning', 'API is in fallback mode - limited functionality')}")
                                
                                st.success("✅ Resume tailored successfully!")
                                st.balloons()
                                
                                # Display results in organized sections
                                st.markdown("---")
                                st.markdown("## 📊 Tailoring Results")
                                
                                # Match Score - Large Progress Bar with Color Coding
                                match_score = data.get('match_score', 0)
                                
                                # Determine color based on score
                                if match_score >= 80:
                                    bar_color = "#10B981"  # Green
                                    text_color = "#059669"
                                    emoji = "🟢"
                                elif match_score >= 60:
                                    bar_color = "#F59E0B"  # Yellow/Amber
                                    text_color = "#D97706"
                                    emoji = "🟡"
                                else:
                                    bar_color = "#EF4444"  # Red
                                    text_color = "#DC2626"
                                    emoji = "🔴"
                                
                                st.markdown(f"""
                                <div style="padding: 1.5rem; background: white; border-radius: 1rem; box-shadow: 0 4px 16px rgba(0,0,0,0.06); margin-bottom: 1.5rem;">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                        <h3 style="margin: 0; color: #1F2937;">Match Score</h3>
                                        <h2 style="margin: 0; color: {text_color};">{emoji} {match_score}%</h2>
                                    </div>
                                    <div style="width: 100%; background: #E5E7EB; border-radius: 1rem; height: 2rem; overflow: hidden;">
                                        <div style="width: {match_score}%; background: {bar_color}; height: 100%; border-radius: 1rem; transition: width 1s ease;"></div>
                                    </div>
                                    <p style="margin-top: 0.5rem; margin-bottom: 0; color: #6B7280; font-size: 0.875rem;">
                                        How well your tailored resume matches the job requirements
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Quick Stats
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.metric(
                                        "Changes Made",
                                        len(data.get('changes_made', [])),
                                        help="Number of improvements applied"
                                    )
                                
                                with col2:
                                    st.metric(
                                        "Processing Time",
                                        f"{data.get('latency', 0):.1f}s",
                                        help="AI analysis latency"
                                    )
                                
                                # Three-Column Layout for Key Info
                                st.markdown("---")
                                
                                col1, col2, col3 = st.columns(3)
                                
                                # Missing Skills
                                with col1:
                                    st.markdown("#### ⚠️ Missing Skills")
                                    if data.get('missing_skills'):
                                        for skill in data['missing_skills'][:5]:
                                            st.markdown(f"""
                                            <div style="background: #FEE2E2; color: #991B1B; padding: 0.5rem; border-radius: 0.5rem; margin-bottom: 0.5rem; font-weight: 500;">
                                                ❌ {skill}
                                            </div>
                                            """, unsafe_allow_html=True)
                                        if len(data['missing_skills']) > 5:
                                            st.caption(f"+ {len(data['missing_skills']) - 5} more skills")
                                    else:
                                        st.success("✅ All skills covered!")
                                
                                # Changes Made
                                with col2:
                                    st.markdown("#### ✅ Changes Made")
                                    if data.get('changes_made'):
                                        for change in data['changes_made'][:5]:
                                            st.markdown(f"""
                                            <div style="background: #D1FAE5; color: #065F46; padding: 0.5rem; border-radius: 0.5rem; margin-bottom: 0.5rem; font-weight: 500;">
                                                ✓ {change[:50]}{'...' if len(change) > 50 else ''}
                                            </div>
                                            """, unsafe_allow_html=True)
                                        if len(data['changes_made']) > 5:
                                            st.caption(f"+ {len(data['changes_made']) - 5} more changes")
                                    else:
                                        st.info("No changes needed")
                                
                                # Keyword Suggestions
                                with col3:
                                    st.markdown("#### 💡 Keyword Tips")
                                    if data.get('keyword_suggestions'):
                                        for suggestion in data['keyword_suggestions'][:5]:
                                            st.markdown(f"""
                                            <div style="background: #DBEAFE; color: #1E40AF; padding: 0.5rem; border-radius: 0.5rem; margin-bottom: 0.5rem; font-weight: 500;">
                                                💬 {suggestion[:50]}{'...' if len(suggestion) > 50 else ''}
                                            </div>
                                            """, unsafe_allow_html=True)
                                        if len(data['keyword_suggestions']) > 5:
                                            st.caption(f"+ {len(data['keyword_suggestions']) - 5} more tips")
                                    else:
                                        st.info("Keywords optimized")
                                
                                # Priority Improvements - Full Width Alert Box
                                if data.get('priority_improvements'):
                                    st.markdown("---")
                                    st.markdown("""
                                    <div style="background: #FEF3C7; border-left: 4px solid #F59E0B; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                                        <h4 style="margin: 0 0 0.5rem 0; color: #92400E;">🎯 Priority Improvements</h4>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    for i, improvement in enumerate(data['priority_improvements'][:5], 1):
                                        st.markdown(f"""
                                        <div style="background: white; padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 0.5rem; border-left: 3px solid #F59E0B;">
                                            <strong>{i}.</strong> {improvement}
                                        </div>
                                        """, unsafe_allow_html=True)
                                
                                
                                # Side-by-side comparison
                                st.markdown("---")
                                st.markdown("### 📋 Tailored Resume")
                                
                                # Show tailored resume in text area
                                st.text_area(
                                    "Your Optimized Resume",
                                    data.get('tailored_resume', ''),
                                    height=400,
                                    key="tailored_resume_display",
                                    help="Copy this text or download below"
                                )
                                
                                # Action buttons
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.download_button(
                                        label="📥 Download Tailored Resume",
                                        data=data.get('tailored_resume', ''),
                                        file_name=f"tailored_{selected_doc_name}.txt",
                                        mime="text/plain",
                                        use_container_width=True,
                                        type="primary"
                                    )
                                
                                with col2:
                                    if st.button("📋 Copy to Clipboard", use_container_width=True):
                                        st.info("💡 Use Ctrl+A then Ctrl+C in the text area above to copy")
                                
                                # Expanders for detailed comparison and full lists
                                st.markdown("---")
                                
                                with st.expander("📊 View Before & After Comparison", expanded=False):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.markdown("#### 📄 Original Resume")
                                        st.text_area(
                                            "Original",
                                            data.get('original_resume', ''),
                                            height=400,
                                            key="original_comparison",
                                            disabled=True
                                        )
                                    
                                    with col2:
                                        st.markdown("#### ✨ Tailored Resume")
                                        st.text_area(
                                            "Tailored",
                                            data.get('tailored_resume', ''),
                                            height=400,
                                            key="tailored_comparison"
                                        )
                                
                                # Full lists in expanders
                                if len(data.get('missing_skills', [])) > 5 or len(data.get('changes_made', [])) > 5 or len(data.get('keyword_suggestions', [])) > 5:
                                    with st.expander("📝 View All Details", expanded=False):
                                        if len(data.get('missing_skills', [])) > 5:
                                            st.markdown("#### All Missing Skills")
                                            for skill in data['missing_skills']:
                                                st.markdown(f"- ❌ {skill}")
                                        
                                        if len(data.get('changes_made', [])) > 5:
                                            st.markdown("#### All Changes Made")
                                            for change in data['changes_made']:
                                                st.markdown(f"- ✓ {change}")
                                        
                                        if len(data.get('keyword_suggestions', [])) > 5:
                                            st.markdown("#### All Keyword Suggestions")
                                            for suggestion in data['keyword_suggestions']:
                                                st.markdown(f"- 💬 {suggestion}")
                                
                                # Download analysis report
                                with st.expander("📊 Download Full Analysis Report", expanded=False):
                                    report = f"""RESUME TAILORING REPORT
{'='*50}

Job: Custom Target Position
Tailoring Level: {tailoring_level.upper()}
Match Score: {match_score}%
Processing Time: {data.get('latency', 0):.2f}s

MISSING SKILLS:
{chr(10).join(f'- {skill}' for skill in data.get('missing_skills', []))}

PRIORITY IMPROVEMENTS:
{chr(10).join(f'{i}. {imp}' for i, imp in enumerate(data.get('priority_improvements', []), 1))}

CHANGES MADE:
{chr(10).join(f'- {change}' for change in data.get('changes_made', []))}

KEYWORD SUGGESTIONS:
{chr(10).join(f'- {sug}' for sug in data.get('keyword_suggestions', []))}
"""
                                    st.download_button(
                                        label="📊 Download Analysis Report (TXT)",
                                        data=report,
                                        file_name=f"tailoring_report_{selected_doc_name}.txt",
                                        mime="text/plain",
                                        use_container_width=True
                                    )
                                
                                # Success tips
                                st.markdown("---")
                                with st.expander("💡 Next Steps & Tips"):
                                    st.markdown("""
                                    **What to do with your tailored resume:**
                                    
                                    1. ✅ **Review carefully** - Make sure all changes are accurate
                                    2. ✅ **Customize further** - Add personal touches and specific examples
                                    3. ✅ **Update missing skills** - Add them if you have relevant experience
                                    4. ✅ **Use for this job only** - Create tailored versions for different jobs
                                    5. ✅ **Track results** - Monitor interview rates with tailored vs generic resumes
                                    
                                    **Pro Tips:**
                                    - Use "moderate" tailoring for most applications
                                    - Use "aggressive" for your dream jobs where you're a near-perfect fit
                                    - Always be honest - don't add skills you don't have
                                    - Keep the tailored resume for your records
                                    - Tailor again if the job description changes
                                    """)
                                
                            else:
                                error_msg = response.json().get('detail', 'Tailoring failed')
                                st.error(f"❌ {error_msg}")
                                
                        except requests.exceptions.ConnectionError:
                            st.error("❌ Cannot connect to server. Is the backend running?")
                        except requests.exceptions.Timeout:
                            st.error("❌ Request timed out. The AI is taking longer than expected. Please try again.")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
        else:
            st.error("❌ Failed to load documents")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to server")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


def show_ai_rewrite_section():
    """AI-powered resume rewriting"""
    st.markdown("### ✨ AI Resume Rewriting")
    st.markdown("Optimize your resume with AI-powered suggestions")
    
    # Get documents first
    try:
        response = requests.get(
            f"{API_URL}/documents/",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            # API returns {"documents": [...], "total": N}
            documents = data.get("documents", []) if isinstance(data, dict) else data
            
            if not documents or len(documents) == 0:
                st.warning("📭 Please upload a resume first before using AI rewrite")
                return
            
            # Select document
            doc_options = {doc['file_name']: doc for doc in documents}
            selected_doc_name = st.selectbox(
                "Select Resume",
                options=list(doc_options.keys()),
                help="Choose which resume to rewrite"
            )
            
            selected_doc = doc_options[selected_doc_name]
            
            # Select style
            style = st.selectbox(
                "Rewriting Style",
                options=["Technical", "Management", "Creative", "Sales"],
                help="Choose the style that matches your target role"
            )
            
            # Show original text preview
            with st.expander("📄 Original Resume Text", expanded=False):
                st.text_area(
                    "Original",
                    selected_doc.get('extracted_text', 'No text available')[:1000],
                    height=200,
                    disabled=True
                )
            
            if st.button("✨ Rewrite with AI", type="primary", use_container_width=True):
                with st.spinner(f"✨ Rewriting your resume in {style} style..."):
                    try:
                        # Call AI rewrite API
                        response = requests.post(
                            f"{API_URL}/rewrite/",
                            json={
                                "resume_id": selected_doc.get('id'),
                                "rewrite_style": style
                            },
                            headers=get_headers(),
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            st.success("✅ Resume rewritten successfully!")
                            
                            # Show rewritten text
                            st.markdown("### 📝 Rewritten Resume")
                            st.text_area(
                                "Rewritten",
                                data.get('rewritten_text', ''),
                                height=300,
                                key="rewritten_text"
                            )
                            
                            # Show improvements
                            if 'improvements' in data:
                                st.markdown("### 💡 Key Improvements")
                                for improvement in data['improvements']:
                                    st.markdown(f"- ✅ {improvement}")
                            
                            # Show impact score
                            if 'impact_score' in data:
                                st.metric(
                                    "Impact Score",
                                    f"{data['impact_score']}/100",
                                    help="How impactful the improvements are"
                                )
                            
                            # Download button
                            st.download_button(
                                label="� Download Rewritten Resume",
                                data=data.get('rewritten_text', ''),
                                file_name=f"rewritten_{selected_doc_name}.txt",
                                mime="text/plain"
                            )
                        else:
                            error_msg = response.json().get('detail', 'Rewriting failed')
                            st.error(f"❌ {error_msg}")
                            
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to server")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            st.error("❌ Failed to load documents")
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
