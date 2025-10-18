"""
Start Celery Worker and Beat Scheduler

This script starts both the Celery worker (for processing tasks) 
and Celery beat (for scheduling periodic tasks).

Requirements:
- Upstash Redis credentials in .env
- SendGrid API key in .env (for email sending)

Usage:
    python start_celery.py
"""

import subprocess
import sys
import os
from pathlib import Path

# Ensure we're in the project root
project_root = Path(__file__).parent
os.chdir(project_root)

print("\n" + "=" * 70)
print("Starting AlignCV Celery Services")
print("=" * 70)

# Check if .env exists
if not (project_root / ".env").exists():
    print("\n❌ Error: .env file not found!")
    print("   Please create .env file with:")
    print("   - UPSTASH_REDIS_REST_URL")
    print("   - UPSTASH_REDIS_REST_TOKEN")
    print("   - SENDGRID_API_KEY")
    sys.exit(1)

print("\n📋 Starting Celery Worker...")
print("-" * 70)
print("   Celery worker processes background tasks")
print("   Tasks: check_new_jobs, send_job_match_email, send_daily_digest")
print()

# Start Celery worker in background
if sys.platform == "win32":
    # Windows requires --pool=solo
    worker_cmd = [
        sys.executable, "-m", "celery",
        "-A", "backend.v2.notifications.celery_app",
        "worker",
        "--loglevel=info",
        "--pool=solo",
        "--logfile=logs/celery_worker.log"
    ]
else:
    # Unix/Linux/Mac
    worker_cmd = [
        sys.executable, "-m", "celery",
        "-A", "backend.v2.notifications.celery_app",
        "worker",
        "--loglevel=info",
        "--logfile=logs/celery_worker.log"
    ]

print("Command:", " ".join(worker_cmd))
print("\n⏳ Starting worker (this may take a moment)...")

try:
    worker_process = subprocess.Popen(
        worker_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Wait a bit and check if it started successfully
    import time
    time.sleep(3)
    
    if worker_process.poll() is None:
        print("✅ Celery worker started successfully!")
        print(f"   PID: {worker_process.pid}")
        print(f"   Logs: logs/celery_worker.log")
    else:
        print("❌ Celery worker failed to start")
        output = worker_process.stdout.read()
        print(f"   Error: {output}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Failed to start Celery worker: {e}")
    sys.exit(1)

print("\n📅 Starting Celery Beat (Scheduler)...")
print("-" * 70)
print("   Celery beat schedules periodic tasks")
print("   Schedule: check_new_jobs (daily at 9 AM UTC)")
print("            send_daily_digest (daily/weekly at 9 AM UTC)")
print()

# Start Celery beat
beat_cmd = [
    sys.executable, "-m", "celery",
    "-A", "backend.v2.notifications.celery_app",
    "beat",
    "--loglevel=info",
    "--logfile=logs/celery_beat.log"
]

print("Command:", " ".join(beat_cmd))
print("\n⏳ Starting beat scheduler...")

try:
    beat_process = subprocess.Popen(
        beat_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    time.sleep(3)
    
    if beat_process.poll() is None:
        print("✅ Celery beat started successfully!")
        print(f"   PID: {beat_process.pid}")
        print(f"   Logs: logs/celery_beat.log")
    else:
        print("❌ Celery beat failed to start")
        output = beat_process.stdout.read()
        print(f"   Error: {output}")
        worker_process.kill()
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Failed to start Celery beat: {e}")
    worker_process.kill()
    sys.exit(1)

print("\n" + "=" * 70)
print("🎉 Celery Services Running!")
print("=" * 70)
print("\n✅ Services started:")
print(f"   Worker PID: {worker_process.pid}")
print(f"   Beat PID: {beat_process.pid}")
print("\n📊 Monitoring:")
print("   Worker logs: logs/celery_worker.log")
print("   Beat logs: logs/celery_beat.log")
print("\n🛑 To stop:")
print("   Press Ctrl+C or kill the processes")
print("\n💡 Tip: Run 'python scripts/test_phase7_notifications.py' to test")
print()

# Keep running and monitor processes
try:
    print("⏳ Monitoring processes (Press Ctrl+C to stop)...")
    while True:
        time.sleep(5)
        if worker_process.poll() is not None:
            print("\n⚠️  Celery worker stopped unexpectedly!")
            beat_process.kill()
            sys.exit(1)
        if beat_process.poll() is not None:
            print("\n⚠️  Celery beat stopped unexpectedly!")
            worker_process.kill()
            sys.exit(1)
            
except KeyboardInterrupt:
    print("\n\n🛑 Stopping Celery services...")
    worker_process.terminate()
    beat_process.terminate()
    worker_process.wait()
    beat_process.wait()
    print("✅ Celery services stopped")
    print()
