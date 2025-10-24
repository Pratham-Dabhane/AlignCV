#!/bin/bash

# Fix inotify watch limit error for Streamlit applications
# This script increases the system limits for file watching

echo "🔧 Fixing inotify watch limit error..."

# Check current limits
echo "📊 Current inotify limits:"
echo "fs.inotify.max_user_watches: $(cat /proc/sys/fs/inotify/max_user_watches 2>/dev/null || echo 'Not available')"
echo "fs.inotify.max_user_instances: $(cat /proc/sys/fs/inotify/max_user_instances 2>/dev/null || echo 'Not available')"
echo "fs.inotify.max_queued_events: $(cat /proc/sys/fs/inotify/max_queued_events 2>/dev/null || echo 'Not available')"

# Increase inotify limits temporarily
echo "⚡ Temporarily increasing inotify limits..."
sudo sysctl -w fs.inotify.max_user_watches=524288
sudo sysctl -w fs.inotify.max_user_instances=8192
sudo sysctl -w fs.inotify.max_queued_events=16384

# Make changes permanent
echo "💾 Making changes permanent..."
echo "fs.inotify.max_user_watches=524288" | sudo tee -a /etc/sysctl.conf
echo "fs.inotify.max_user_instances=8192" | sudo tee -a /etc/sysctl.conf
echo "fs.inotify.max_queued_events=16384" | sudo tee -a /etc/sysctl.conf

# Apply changes
sudo sysctl -p

echo "✅ Inotify limits have been increased!"
echo "📊 New limits:"
echo "fs.inotify.max_user_watches: $(cat /proc/sys/fs/inotify/max_user_watches)"
echo "fs.inotify.max_user_instances: $(cat /proc/sys/fs/inotify/max_user_instances)"
echo "fs.inotify.max_queued_events: $(cat /proc/sys/fs/inotify/max_queued_events)"

echo "🚀 You can now run your Streamlit application without inotify errors!"
