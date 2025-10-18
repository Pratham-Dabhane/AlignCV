"""
Settings Page - User preferences and configuration
"""

import streamlit as st
import requests

API_URL = "http://localhost:8001/v2"

def get_headers():
    """Get auth headers"""
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

def show_settings():
    """Show settings page"""
    st.markdown("## ⚙️ Settings")
    st.markdown("Manage your account and preferences")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Profile", "🔐 Security", "🎨 Preferences", "⚠️ Danger Zone"])
    
    with tab1:
        show_profile_settings()
    
    with tab2:
        show_security_settings()
    
    with tab3:
        show_preference_settings()
    
    with tab4:
        show_danger_zone()

def show_profile_settings():
    """Show profile settings"""
    st.markdown("### � Profile Information")
    st.markdown("Update your personal information")
    
    # Get current user data
    user = st.session_state.get('user', {})
    
    with st.form("profile_form"):
        name = st.text_input(
            "Full Name",
            value=user.get('name', ''),
            placeholder="Enter your full name"
        )
        
        email = st.text_input(
            "Email Address",
            value=user.get('email', ''),
            placeholder="your.email@example.com",
            disabled=True,
            help="Email cannot be changed"
        )
        
        phone = st.text_input(
            "Phone Number",
            value=user.get('phone', ''),
            placeholder="+1 (555) 123-4567"
        )
        
        location = st.text_input(
            "Location",
            value=user.get('location', ''),
            placeholder="City, State/Country"
        )
        
        linkedin = st.text_input(
            "LinkedIn Profile",
            value=user.get('linkedin_url', ''),
            placeholder="https://linkedin.com/in/yourprofile"
        )
        
        github = st.text_input(
            "GitHub Profile",
            value=user.get('github_url', ''),
            placeholder="https://github.com/yourusername"
        )
        
        bio = st.text_area(
            "Professional Bio",
            value=user.get('bio', ''),
            placeholder="Tell us about yourself and your professional experience...",
            height=150
        )
        
        submitted = st.form_submit_button("💾 Save Profile", type="primary", use_container_width=True)
        
        if submitted:
            update_profile({
                'name': name,
                'phone': phone,
                'location': location,
                'linkedin_url': linkedin,
                'github_url': github,
                'bio': bio
            })

def update_profile(profile_data):
    """Update user profile"""
    try:
        response = requests.put(
            f"{API_URL}/auth/profile",
            json=profile_data,
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            updated_user = response.json()
            st.session_state.user = updated_user
            st.success("✅ Profile updated successfully!")
        else:
            error_msg = response.json().get('detail', 'Update failed')
            st.error(f"❌ {error_msg}")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to server")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def show_security_settings():
    """Show security settings"""
    st.markdown("### 🔐 Security")
    st.markdown("Update your password and security settings")
    
    with st.form("password_form"):
        st.markdown("#### Change Password")
        
        current_password = st.text_input(
            "Current Password",
            type="password",
            placeholder="Enter your current password"
        )
        
        new_password = st.text_input(
            "New Password",
            type="password",
            placeholder="Enter new password (min 8 characters)"
        )
        
        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            placeholder="Re-enter new password"
        )
        
        submitted = st.form_submit_button("� Update Password", type="primary", use_container_width=True)
        
        if submitted:
            if not current_password or not new_password or not confirm_password:
                st.error("❌ All fields are required")
            elif len(new_password) < 8:
                st.error("❌ Password must be at least 8 characters")
            elif new_password != confirm_password:
                st.error("❌ New passwords do not match")
            else:
                change_password(current_password, new_password)
    
    st.markdown("---")
    
    # Two-factor authentication (placeholder)
    st.markdown("#### � Two-Factor Authentication")
    st.info("🚧 Two-factor authentication coming soon!")
    st.markdown("Add an extra layer of security to your account")

def change_password(current_password, new_password):
    """Change user password"""
    try:
        response = requests.put(
            f"{API_URL}/auth/change-password",
            json={
                'current_password': current_password,
                'new_password': new_password
            },
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            st.success("✅ Password updated successfully!")
        else:
            error_msg = response.json().get('detail', 'Password update failed')
            st.error(f"❌ {error_msg}")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to server")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def show_preference_settings():
    """Show preference settings"""
    st.markdown("### 🎨 Preferences")
    st.markdown("Customize your AlignCV experience")
    
    st.markdown("#### 🎯 Job Matching Preferences")
    
    with st.form("preferences_form"):
        # Job preferences
        job_types = st.multiselect(
            "Preferred Job Types",
            options=["Full-time", "Part-time", "Contract", "Freelance", "Internship"],
            default=["Full-time"],
            help="Select job types you're interested in"
        )
        
        min_salary = st.number_input(
            "Minimum Salary (USD/year)",
            min_value=0,
            max_value=1000000,
            value=0,
            step=10000,
            help="Minimum annual salary you're looking for"
        )
        
        preferred_locations = st.text_area(
            "Preferred Locations",
            placeholder="e.g., San Francisco, New York, Remote",
            help="Enter locations separated by commas"
        )
        
        remote_only = st.checkbox(
            "Remote jobs only",
            help="Only show remote positions"
        )
        
        st.markdown("---")
        st.markdown("#### 📊 Display Preferences")
        
        items_per_page = st.slider(
            "Items per page",
            min_value=10,
            max_value=50,
            value=20,
            step=5,
            help="Number of items to display per page"
        )
        
        show_company_logos = st.checkbox(
            "Show company logos",
            value=True,
            help="Display company logos in job listings"
        )
        
        submitted = st.form_submit_button("� Save Preferences", type="primary", use_container_width=True)
        
        if submitted:
            save_preferences({
                'job_types': job_types,
                'min_salary': min_salary,
                'preferred_locations': preferred_locations,
                'remote_only': remote_only,
                'items_per_page': items_per_page,
                'show_company_logos': show_company_logos
            })

def save_preferences(preferences):
    """Save user preferences"""
    try:
        response = requests.put(
            f"{API_URL}/auth/preferences",
            json=preferences,
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            st.success("✅ Preferences saved successfully!")
        else:
            error_msg = response.json().get('detail', 'Failed to save preferences')
            st.error(f"❌ {error_msg}")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to server")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def show_danger_zone():
    """Show dangerous operations"""
    st.markdown("### ⚠️ Danger Zone")
    st.markdown("Irreversible actions that affect your account")
    
    st.error("⚠️ **Warning**: These actions cannot be undone!")
    
    # Export data
    st.markdown("#### 📥 Export Your Data")
    st.markdown("Download all your data including resumes, applications, and profile information")
    
    if st.button("📥 Export Data", use_container_width=True):
        export_user_data()
    
    st.markdown("---")
    
    # Delete account
    st.markdown("#### 🗑️ Delete Account")
    st.markdown("Permanently delete your account and all associated data")
    
    with st.expander("⚠️ I understand the consequences"):
        st.warning("""
        **This will permanently delete**:
        - Your profile and account information
        - All uploaded resumes and documents
        - Job applications and bookmarks
        - Notification history
        - All other data associated with your account
        
        **This action cannot be undone!**
        """)
        
        confirm_text = st.text_input(
            "Type 'DELETE' to confirm",
            placeholder="DELETE",
            help="Type DELETE in capital letters"
        )
        
        if st.button("🗑️ Delete My Account", type="primary", use_container_width=True):
            if confirm_text == "DELETE":
                delete_account()
            else:
                st.error("❌ Please type 'DELETE' to confirm")

def export_user_data():
    """Export user data"""
    try:
        response = requests.get(
            f"{API_URL}/auth/export-data",
            headers=get_headers(),
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Convert to JSON string for download
            import json
            json_str = json.dumps(data, indent=2)
            
            st.download_button(
                label="📥 Download Data (JSON)",
                data=json_str,
                file_name="aligncv_data_export.json",
                mime="application/json"
            )
            
            st.success("✅ Data export ready!")
        else:
            st.error("❌ Failed to export data")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to server")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def delete_account():
    """Delete user account"""
    try:
        response = requests.delete(
            f"{API_URL}/auth/account",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            st.success("✅ Account deleted successfully. You will be logged out.")
            # Clear session and redirect to login
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.authenticated = False
            st.rerun()
        else:
            error_msg = response.json().get('detail', 'Account deletion failed')
            st.error(f"❌ {error_msg}")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to server")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

