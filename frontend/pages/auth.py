"""
Authentication Page - Login & Signup
"""

import streamlit as st
import requests
import json
import time
from typing import Dict, Optional

API_URL = "https://aligncv-e55h.onrender.com/v2"


def _post_with_retry(url: str, payload: dict, timeout_seconds: int = 30, retries: int = 2):
    """POST helper with retry for transient Render cold-start timeouts."""
    last_error = None
    for attempt in range(retries):
        try:
            return requests.post(url, json=payload, timeout=timeout_seconds)
        except requests.exceptions.ReadTimeout as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(1)
                continue
            raise
    raise last_error

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
                response = _post_with_retry(
                    f"{API_URL}/auth/login",
                    {"email": email, "password": password},
                    timeout_seconds=30,
                    retries=2,
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # Store tokens and user info
                        st.session_state.authenticated = True
                        st.session_state.access_token = data["tokens"]["access_token"]
                        st.session_state.refresh_token = data["tokens"]["refresh_token"]
                        st.session_state.user = data["user"]
                        
                        st.success(f"✅ Welcome back, {data['user']['name']}!")
                        st.rerun()
                    except (json.JSONDecodeError, KeyError) as e:
                        st.error(f"❌ Invalid response from server: {str(e)}")
                else:
                    try:
                        error_msg = response.json().get("detail", "Login failed")
                        st.error(f"❌ {error_msg}")
                    except json.JSONDecodeError:
                        st.error(f"❌ Login failed (Status: {response.status_code})")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend API. Please try again in a few seconds.")
            except requests.exceptions.ReadTimeout:
                st.error("❌ Login timed out. The backend may be waking up; please try again.")
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
                response = _post_with_retry(
                    f"{API_URL}/auth/signup",
                    {
                        "name": name,
                        "email": email,
                        "password": password,
                    },
                    timeout_seconds=30,
                    retries=2,
                )
                
                if response.status_code == 201:
                    try:
                        data = response.json()
                        
                        # Store tokens and user info
                        st.session_state.authenticated = True
                        st.session_state.access_token = data["tokens"]["access_token"]
                        st.session_state.refresh_token = data["tokens"]["refresh_token"]
                        st.session_state.user = data["user"]
                        
                        st.success(f"✅ Account created! Welcome, {data['user']['name']}!")
                        st.rerun()
                    except (json.JSONDecodeError, KeyError) as e:
                        st.error(f"❌ Invalid response from server: {str(e)}")
                else:
                    try:
                        error_msg = response.json().get("detail", "Signup failed")
                        st.error(f"❌ {error_msg}")
                    except json.JSONDecodeError:
                        st.error(f"❌ Signup failed (Status: {response.status_code})")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend API. Please try again in a few seconds.")
            except requests.exceptions.ReadTimeout:
                st.error("❌ Signup timed out. The backend may be waking up; please try again.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
