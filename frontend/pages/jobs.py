"""
Jobs Page - Job matching and applications
"""

import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:8001/v2"

def get_headers():
    """Get auth headers"""
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

def show_jobs():
    """Show jobs page"""
    st.markdown("## 💼 Job Matching")
    st.markdown("Find jobs that match your skills")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Find Jobs", "⭐ Bookmarks", "📊 Applications"])
    
    with tab1:
        show_job_matching()
    
    with tab2:
        show_bookmarks()
    
    with tab3:
        show_applications()

def show_job_matching():
    """Show job matching section"""
    st.markdown("### 🔍 Find Matching Jobs")
    
    # Search controls
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Search Keywords",
            placeholder="e.g., Python Developer, Data Scientist",
            help="Enter job titles or keywords"
        )
    
    with col2:
        min_score = st.slider(
            "Min Match Score",
            min_value=0,
            max_value=100,
            value=60,
            help="Minimum match score percentage"
        )
    
    if st.button("🔍 Search Jobs", type="primary", use_container_width=True):
        search_jobs(search_query, min_score)

def search_jobs(query, min_score):
    """Search for matching jobs"""
    with st.spinner("🔍 Finding matching jobs..."):
        try:
            # Call job matching API
            params = {}
            if query:
                params['query'] = query
            params['min_score'] = min_score / 100  # Convert to 0-1 range
            
            response = requests.get(
                f"{API_URL}/jobs/match",
                params=params,
                headers=get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                jobs = response.json()
                
                if not jobs or len(jobs) == 0:
                    st.info("📭 No matching jobs found. Try adjusting your search criteria.")
                else:
                    st.success(f"✅ Found {len(jobs)} matching job(s)")
                    
                    # Display jobs
                    for job in jobs:
                        display_job_card(job)
            else:
                error_msg = response.json().get('detail', 'Search failed')
                st.error(f"❌ {error_msg}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to server")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def display_job_card(job):
    """Display a job card"""
    with st.container():
        # Header with match score
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"### {job.get('title', 'Untitled Position')}")
            company = job.get('company', 'Unknown Company')
            location = job.get('location', 'Location not specified')
            st.markdown(f"**🏢 {company}** | 📍 {location}")
        
        with col2:
            match_score = job.get('match_score', 0) * 100
            color = "🟢" if match_score >= 80 else "🟡" if match_score >= 60 else "🔴"
            st.markdown(f"### {color} {match_score:.0f}%")
            st.caption("Match Score")
        
        # Job details
        col1, col2, col3 = st.columns(3)
        
        with col1:
            salary = job.get('salary_range', 'Not specified')
            st.markdown(f"💰 **Salary**: {salary}")
        
        with col2:
            job_type = job.get('job_type', 'Full-time')
            st.markdown(f"💼 **Type**: {job_type}")
        
        with col3:
            posted = job.get('posted_date', '')
            if posted:
                st.markdown(f"📅 **Posted**: {posted}")
        
        # Description
        description = job.get('description', 'No description available')
        with st.expander("📝 Job Description"):
            st.markdown(description[:500] + "..." if len(description) > 500 else description)
        
        # Required skills
        if 'required_skills' in job and job['required_skills']:
            st.markdown("**Required Skills**:")
            skills_html = " ".join([f'<span style="background-color: #e1f5ff; padding: 4px 8px; border-radius: 4px; margin: 2px; display: inline-block;">{skill}</span>' for skill in job['required_skills']])
            st.markdown(skills_html, unsafe_allow_html=True)
        
        # Actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("⭐ Bookmark", key=f"bookmark_{job.get('id')}", use_container_width=True):
                bookmark_job(job.get('id'))
        
        with col2:
            if st.button("✅ Apply", key=f"apply_{job.get('id')}", use_container_width=True, type="primary"):
                apply_to_job(job.get('id'))
        
        with col3:
            job_url = job.get('url', '')
            if job_url:
                st.link_button("� View Job", job_url, use_container_width=True)
        
        st.markdown("---")

def bookmark_job(job_id):
    """Bookmark a job"""
    try:
        response = requests.post(
            f"{API_URL}/jobs/bookmarks",
            json={"job_id": job_id},
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            st.success("⭐ Job bookmarked!")
            st.rerun()
        else:
            error_msg = response.json().get('detail', 'Bookmark failed')
            st.error(f"❌ {error_msg}")
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def apply_to_job(job_id):
    """Apply to a job"""
    try:
        response = requests.post(
            f"{API_URL}/jobs/applications",
            json={"job_id": job_id, "status": "applied"},
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            st.success("✅ Application submitted!")
            st.balloons()
            st.rerun()
        else:
            error_msg = response.json().get('detail', 'Application failed')
            st.error(f"❌ {error_msg}")
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def show_bookmarks():
    """Show bookmarked jobs"""
    st.markdown("### ⭐ Your Bookmarked Jobs")
    
    try:
        response = requests.get(
            f"{API_URL}/jobs/bookmarks",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            bookmarks = response.json()
            
            if not bookmarks or len(bookmarks) == 0:
                st.info("📭 No bookmarked jobs yet. Start searching to find jobs you like!")
            else:
                st.success(f"⭐ You have {len(bookmarks)} bookmarked job(s)")
                
                for bookmark in bookmarks:
                    job = bookmark.get('job', {})
                    
                    with st.container():
                        col1, col2 = st.columns([4, 1])
                        
                        with col1:
                            st.markdown(f"### {job.get('title', 'Untitled')}")
                            st.markdown(f"**🏢 {job.get('company', 'Unknown')}** | 📍 {job.get('location', 'Unknown')}")
                        
                        with col2:
                            if st.button("🗑️", key=f"remove_{bookmark.get('id')}", help="Remove bookmark"):
                                remove_bookmark(bookmark.get('id'))
                        
                        # Actions
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Apply", key=f"apply_bookmark_{job.get('id')}", use_container_width=True):
                                apply_to_job(job.get('id'))
                        with col2:
                            job_url = job.get('url', '')
                            if job_url:
                                st.link_button("🔗 View Job", job_url, use_container_width=True)
                        
                        st.markdown("---")
        else:
            st.error("❌ Failed to load bookmarks")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to server")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def remove_bookmark(bookmark_id):
    """Remove a bookmark"""
    try:
        response = requests.delete(
            f"{API_URL}/jobs/bookmarks/{bookmark_id}",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            st.success("✅ Bookmark removed!")
            st.rerun()
        else:
            st.error("❌ Failed to remove bookmark")
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def show_applications():
    """Show job applications"""
    st.markdown("### 📊 Your Applications")
    
    try:
        response = requests.get(
            f"{API_URL}/jobs/applications",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            applications = response.json()
            
            if not applications or len(applications) == 0:
                st.info("📭 No applications yet. Apply to jobs to track them here!")
            else:
                st.success(f"📊 You have {len(applications)} application(s)")
                
                # Group by status
                statuses = {}
                for app in applications:
                    status = app.get('status', 'applied')
                    if status not in statuses:
                        statuses[status] = []
                    statuses[status].append(app)
                
                # Display stats
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Applied", statuses.get('applied', []) and len(statuses['applied']) or 0)
                with col2:
                    st.metric("Interviewing", statuses.get('interviewing', []) and len(statuses['interviewing']) or 0)
                with col3:
                    st.metric("Offered", statuses.get('offered', []) and len(statuses['offered']) or 0)
                with col4:
                    st.metric("Rejected", statuses.get('rejected', []) and len(statuses['rejected']) or 0)
                
                st.markdown("---")
                
                # Display applications
                for app in applications:
                    job = app.get('job', {})
                    status = app.get('status', 'applied')
                    
                    # Status emoji
                    status_emoji = {
                        'applied': '📤',
                        'interviewing': '💬',
                        'offered': '🎉',
                        'rejected': '❌'
                    }.get(status, '📄')
                    
                    with st.container():
                        col1, col2, col3 = st.columns([3, 2, 1])
                        
                        with col1:
                            st.markdown(f"### {job.get('title', 'Untitled')}")
                            st.markdown(f"**{job.get('company', 'Unknown')}**")
                        
                        with col2:
                            st.markdown(f"{status_emoji} **Status**: {status.title()}")
                            applied_date = app.get('applied_date', '')
                            if applied_date:
                                date_obj = datetime.fromisoformat(applied_date.replace('Z', '+00:00'))
                                st.markdown(f"📅 {date_obj.strftime('%b %d, %Y')}")
                        
                        with col3:
                            # Update status dropdown
                            new_status = st.selectbox(
                                "Update",
                                options=['applied', 'interviewing', 'offered', 'rejected'],
                                index=['applied', 'interviewing', 'offered', 'rejected'].index(status),
                                key=f"status_{app.get('id')}",
                                label_visibility="collapsed"
                            )
                            
                            if new_status != status:
                                update_application_status(app.get('id'), new_status)
                        
                        st.markdown("---")
        else:
            st.error("❌ Failed to load applications")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to server")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def update_application_status(app_id, new_status):
    """Update application status"""
    try:
        response = requests.put(
            f"{API_URL}/jobs/applications/{app_id}",
            json={"status": new_status},
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            st.success(f"✅ Status updated to {new_status}!")
            st.rerun()
        else:
            st.error("❌ Failed to update status")
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

