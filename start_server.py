"""
Simple script to start the server in the background.
"""
import subprocess
import sys

if __name__ == "__main__":
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.v2.app_v2:app_v2", "--port", "8001"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    print(f"Server started with PID: {proc.pid}")
    print("Server is starting... Check http://localhost:8001/v2/health")
    print(f"To stop: taskkill /PID {proc.pid} /F")
    
    # Print initial output
    for i in range(20):  # Print first 20 lines
        line = proc.stdout.readline()
        if line:
            print(line.strip())
        if "Application startup complete" in line:
            print("\n✅ Server is ready!")
            break
    
    print(f"\nServer running in background (PID: {proc.pid})")
