"""
Notifications Page - View and manage notifications
"""

import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:8001/v2"

def get_headers():
    """Get auth headers"""
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

def show_notifications():
    """Show notifications page"""
    st.markdown("## 🔔 Notifications")
    st.markdown("Stay updated with job matches, applications, and important alerts")
    st.markdown("")  # Spacing
    
    # Create tabs
    tab1, tab2 = st.tabs(["📬 All Notifications", "⚙️ Preferences"])
    
    with tab1:
        show_notifications_list()
    
    with tab2:
        show_notification_settings()

def show_notifications_list():
    """Show all notifications"""
    st.markdown("### 📬 Your Notifications")
    st.markdown("Filter and manage all your notifications")
    st.markdown("")  # Spacing
    
    # Filter controls
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        filter_type = st.selectbox(
            "Filter by Type",
            options=["All", "job_match", "application_update", "system"],
            format_func=lambda x: {
                "All": "All Types",
                "job_match": "🔍 Job Matches",
                "application_update": "📊 Application Updates",
                "system": "⚙️ System"
            }.get(x, x)
        )
    
    with col2:
        filter_status = st.selectbox(
            "Filter by Status",
            options=["All", "unread", "read"],
            format_func=lambda x: {
                "All": "All Status",
                "unread": "📫 Unread",
                "read": "✅ Read"
            }.get(x, x)
        )
    
    with col3:
        if st.button("✅ Mark All Read", use_container_width=True):
            mark_all_as_read()
    
    # Fetch notifications
    try:
        params = {}
        if filter_type != "All":
            params['type'] = filter_type
        if filter_status != "All":
            params['status'] = filter_status
        
        response = requests.get(
            f"{API_URL}/notifications",
            params=params,
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract notifications list from response object
            notifications = data.get('notifications', []) if isinstance(data, dict) else []
            total = data.get('total', 0) if isinstance(data, dict) else 0
            unread_count = data.get('unread', 0) if isinstance(data, dict) else 0
            
            if not notifications or len(notifications) == 0:
                st.info("📭 No notifications found. We'll notify you when something important happens!")
            else:
                st.success(f"📬 {total} notification(s) ({unread_count} unread)")
                
                # Display notifications
                for notif in notifications:
                    display_notification_card(notif)
        else:
            st.error("❌ Failed to load notifications")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to server")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def display_notification_card(notif):
    """Display a notification card"""
    notif_id = notif.get('id')
    is_read = notif.get('is_read', False)
    notif_type = notif.get('type', 'system')
    
    # Type emoji
    type_emoji = {
        'job_match': '🔍',
        'application_update': '📊',
        'system': '⚙️'
    }.get(notif_type, '📢')
    
    # Background color based on read status
    bg_color = "#f8f9fa" if is_read else "#e3f2fd"
    
    with st.container():
        st.markdown(f"""
        <div style="background-color: {bg_color}; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([5, 1])
        
        with col1:
            # Title
            title = notif.get('title', 'Notification')
            if not is_read:
                st.markdown(f"### {type_emoji} **{title}** 🔵")
            else:
                st.markdown(f"### {type_emoji} {title}")
            
            # Message
            message = notif.get('message', '')
            st.markdown(message)
            
            # Timestamp
            created_at = notif.get('created_at', '')
            if created_at:
                date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                time_ago = get_time_ago(date_obj)
                st.caption(f"🕒 {time_ago}")
        
        with col2:
            if not is_read:
                if st.button("✅ Mark Read", key=f"read_{notif_id}", use_container_width=True):
                    mark_as_read(notif_id)
            
            if st.button("🗑️ Delete", key=f"delete_{notif_id}", use_container_width=True):
                delete_notification(notif_id)
        
        st.markdown("---")

def get_time_ago(date_obj):
    """Get human-readable time ago"""
    now = datetime.now(date_obj.tzinfo)
    diff = now - date_obj
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    else:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days > 1 else ''} ago"

def mark_as_read(notif_id):
    """Mark notification as read"""
    try:
        response = requests.put(
            f"{API_URL}/notifications/{notif_id}/read",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            st.success("✅ Marked as read!")
            st.rerun()
        else:
            st.error("❌ Failed to mark as read")
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def mark_all_as_read():
    """Mark all notifications as read"""
    try:
        response = requests.put(
            f"{API_URL}/notifications/mark-all-read",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            st.success("✅ All notifications marked as read!")
            st.rerun()
        else:
            st.error("❌ Failed to mark all as read")
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def delete_notification(notif_id):
    """Delete a notification"""
    try:
        response = requests.delete(
            f"{API_URL}/notifications/{notif_id}",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            st.success("✅ Notification deleted!")
            st.rerun()
        else:
            st.error("❌ Failed to delete notification")
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def show_notification_settings():
    """Show notification settings"""
    st.markdown("### ⚙️ Notification Preferences")
    st.markdown("Customize your notification settings for the best experience")
    st.markdown("")  # Spacing
    
    try:
        # Fetch current settings
        response = requests.get(
            f"{API_URL}/notifications/settings",
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            settings = response.json()
            
            st.markdown("#### 📧 Email Notifications")
            
            email_job_matches = st.checkbox(
                "🔍 New job matches",
                value=settings.get('email_job_matches', True),
                help="Receive emails when new jobs match your profile"
            )
            
            email_application_updates = st.checkbox(
                "📊 Application status updates",
                value=settings.get('email_application_updates', True),
                help="Receive emails when your application status changes"
            )
            
            email_weekly_digest = st.checkbox(
                "📅 Weekly digest",
                value=settings.get('email_weekly_digest', True),
                help="Receive a weekly summary of your job search activity"
            )
            
            st.markdown("---")
            st.markdown("#### 🔔 In-App Notifications")
            
            push_job_matches = st.checkbox(
                "� New job matches",
                value=settings.get('push_job_matches', True),
                help="Show notifications when new jobs match your profile"
            )
            
            push_application_updates = st.checkbox(
                "📊 Application status updates",
                value=settings.get('push_application_updates', True),
                help="Show notifications when your application status changes"
            )
            
            push_system_updates = st.checkbox(
                "⚙️ System updates",
                value=settings.get('push_system_updates', True),
                help="Show notifications about system updates and maintenance"
            )
            
            st.markdown("---")
            
            # Frequency settings
            st.markdown("#### ⏰ Frequency")
            
            notification_frequency = st.select_slider(
                "Email frequency",
                options=["realtime", "daily", "weekly"],
                value=settings.get('notification_frequency', 'daily'),
                format_func=lambda x: {
                    "realtime": "⚡ Realtime",
                    "daily": "📅 Daily Digest",
                    "weekly": "📆 Weekly Digest"
                }.get(x, x),
                help="How often should we send email notifications"
            )
            
            st.markdown("---")
            
            # Save button
            if st.button("💾 Save Preferences", type="primary", use_container_width=True):
                save_notification_settings({
                    'email_job_matches': email_job_matches,
                    'email_application_updates': email_application_updates,
                    'email_weekly_digest': email_weekly_digest,
                    'push_job_matches': push_job_matches,
                    'push_application_updates': push_application_updates,
                    'push_system_updates': push_system_updates,
                    'notification_frequency': notification_frequency
                })
        else:
            st.error("❌ Failed to load settings")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to server")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def save_notification_settings(settings):
    """Save notification settings"""
    try:
        response = requests.put(
            f"{API_URL}/notifications/settings",
            json=settings,
            headers=get_headers(),
            timeout=10
        )
        
        if response.status_code == 200:
            st.success("✅ Preferences saved successfully!")
        else:
            error_msg = response.json().get('detail', 'Failed to save settings')
            st.error(f"❌ {error_msg}")
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

