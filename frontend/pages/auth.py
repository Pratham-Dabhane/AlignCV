"""
Authentication Page - Login & Signup
"""

import streamlit as st
import requests
from typing import Dict, Optional

API_URL = "https://aligncv-e55h.onrender.com/v2"

def show_auth_page():
    """Show login/signup page"""
    
    tab1, tab2 = st.tabs(["🔐 Login", "✍️ Sign Up"])
    
    with tab1:
        show_login()
    
    with tab2:
        show_signup()

def show_login():
    """Login form"""
    st.markdown("### 👋 Welcome Back!")
    st.markdown("Sign in to continue your job search journey")
    
    with st.form("login_form"):
        email = st.text_input("📧 Email", placeholder="you@example.com", help="Enter your registered email")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", help="Your secure password")
        
        st.markdown("")  # Spacing
        submit = st.form_submit_button("🚀 Sign In", use_container_width=True, type="primary")
        
        if submit:
            if not email or not password:
                st.error("❌ Please enter both email and password")
                return
            
            # Call login API
            try:
                response = requests.post(
                    f"{API_URL}/auth/login",
                    json={"email": email, "password": password},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Store tokens and user info
                    st.session_state.authenticated = True
                    st.session_state.access_token = data["tokens"]["access_token"]
                    st.session_state.refresh_token = data["tokens"]["refresh_token"]
                    st.session_state.user = data["user"]
                    
                    st.success(f"✅ Welcome back, {data['user']['name']}!")
                    st.rerun()
                else:
                    error_msg = response.json().get("detail", "Login failed")
                    st.error(f"❌ {error_msg}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to server. Is it running on port 8001?")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

def show_signup():
    """Signup form"""
    st.markdown("### ✨ Create Your Account")
    st.markdown("Join AlignCV and discover your perfect career match")
    
    with st.form("signup_form"):
        name = st.text_input("👤 Full Name", placeholder="John Doe", help="Your full name as you'd like it to appear")
        email = st.text_input("📧 Email", placeholder="you@example.com", help="Use a valid email address")
        password = st.text_input("🔒 Password", type="password", placeholder="Create a strong password", help="Minimum 8 characters")
        password_confirm = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter your password")
        
        st.info("💡 **Tip**: Use a strong password with a mix of letters, numbers, and symbols")
        
        st.markdown("")  # Spacing
        submit = st.form_submit_button("🚀 Create Account", use_container_width=True, type="primary")
        
        if submit:
            # Validation
            if not name or not email or not password:
                st.error("❌ Please fill in all fields")
                return
            
            if password != password_confirm:
                st.error("❌ Passwords don't match")
                return
            
            if len(password) < 8:
                st.error("❌ Password must be at least 8 characters")
                return
            
            # Call signup API
            try:
                response = requests.post(
                    f"{API_URL}/auth/signup",
                    json={
                        "name": name,
                        "email": email,
                        "password": password
                    },
                    timeout=10
                )
                
                if response.status_code == 201:
                    data = response.json()
                    
                    # Store tokens and user info
                    st.session_state.authenticated = True
                    st.session_state.access_token = data["tokens"]["access_token"]
                    st.session_state.refresh_token = data["tokens"]["refresh_token"]
                    st.session_state.user = data["user"]
                    
                    st.success(f"✅ Account created! Welcome, {data['user']['name']}!")
                    st.rerun()
                else:
                    error_msg = response.json().get("detail", "Signup failed")
                    st.error(f"❌ {error_msg}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to server. Is it running on port 8001?")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
