"""
Documents Page - Resume upload and management
"""

import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:8001/v2"

def get_headers():
    """Get auth headers"""
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

def show_documents():
    """Show documents page"""
    st.markdown("## 📄 My Documents")
    st.markdown("Upload and manage your resumes")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload", "📂 My Documents", "🎯 Tailor to Job", "✨ AI Rewrite"])
    
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
    st.markdown("### Upload Your Resume")
    st.markdown("Upload your resume in PDF or DOCX format")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'docx'],
        help="Maximum file size: 5MB"
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
    st.markdown("### Your Uploaded Documents")
    
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
                                
                                st.success("✅ Resume tailored successfully!")
                                st.balloons()
                                
                                # Display results in organized sections
                                st.markdown("---")
                                st.markdown("## 📊 Tailoring Results")
                                
                                # Match score
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    match_score = data.get('match_score', 0)
                                    color = "🟢" if match_score >= 80 else "🟡" if match_score >= 60 else "🔴"
                                    st.metric(
                                        "Match Score",
                                        f"{color} {match_score}%",
                                        help="How well your tailored resume matches the job"
                                    )
                                
                                with col2:
                                    st.metric(
                                        "Changes Made",
                                        len(data.get('changes_made', [])),
                                        help="Number of improvements applied"
                                    )
                                
                                with col3:
                                    st.metric(
                                        "Processing Time",
                                        f"{data.get('latency', 0):.1f}s",
                                        help="AI analysis latency"
                                    )
                                
                                # Missing skills
                                if data.get('missing_skills'):
                                    st.markdown("### ⚠️ Skills Gap Analysis")
                                    st.markdown("**Skills mentioned in job but missing from your resume:**")
                                    skills_html = " ".join([
                                        f'<span style="background-color: #ffe1e1; color: #c33; padding: 4px 8px; border-radius: 4px; margin: 2px; display: inline-block;">❌ {skill}</span>'
                                        for skill in data['missing_skills'][:10]
                                    ])
                                    st.markdown(skills_html, unsafe_allow_html=True)
                                    st.caption("💡 Consider adding these skills if you have relevant experience")
                                
                                # Priority improvements
                                if data.get('priority_improvements'):
                                    st.markdown("### 🎯 Priority Improvements")
                                    for i, improvement in enumerate(data['priority_improvements'][:5], 1):
                                        st.markdown(f"{i}. ✅ {improvement}")
                                
                                # Keyword suggestions
                                if data.get('keyword_suggestions'):
                                    with st.expander("💡 Keyword Suggestions", expanded=False):
                                        for suggestion in data['keyword_suggestions']:
                                            st.markdown(f"- 💬 {suggestion}")
                                
                                # Changes made
                                if data.get('changes_made'):
                                    with st.expander("📝 Detailed Changes", expanded=False):
                                        for change in data['changes_made']:
                                            st.markdown(f"- ✏️ {change}")
                                
                                # Side-by-side comparison
                                st.markdown("---")
                                st.markdown("### 📋 Before & After Comparison")
                                
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
                                
                                # Download options
                                st.markdown("---")
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.download_button(
                                        label="📥 Download Tailored Resume (TXT)",
                                        data=data.get('tailored_resume', ''),
                                        file_name=f"tailored_{selected_doc_name}.txt",
                                        mime="text/plain",
                                        use_container_width=True
                                    )
                                
                                with col2:
                                    # Download analysis report
                                    report = f"""RESUME TAILORING REPORT
{'='*50}

Job: Custom Target Position
Tailoring Level: {tailoring_level.upper()}
Match Score: {match_score}%
Processing Time: {data.get('latency', 0):.2f}s

MISSING SKILLS:
{chr(10).join(f'- {skill}' for skill in data.get('missing_skills', [])[:10])}

PRIORITY IMPROVEMENTS:
{chr(10).join(f'{i}. {imp}' for i, imp in enumerate(data.get('priority_improvements', []), 1))}

CHANGES MADE:
{chr(10).join(f'- {change}' for change in data.get('changes_made', []))}

KEYWORD SUGGESTIONS:
{chr(10).join(f'- {sug}' for sug in data.get('keyword_suggestions', []))}
"""
                                    st.download_button(
                                        label="📊 Download Analysis Report",
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
                                "resume_text": selected_doc.get('extracted_text', ''),
                                "style": style
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
