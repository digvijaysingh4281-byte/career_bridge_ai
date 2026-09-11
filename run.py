"""
CareerBridge AI - Unified Runner Script
Starts the FastAPI Backend and Streamlit Frontend concurrently.
"""
import sys
import subprocess
import time
import argparse
import os

def start_backend(host="127.0.0.1", port=8000):
    """Starts the FastAPI backend using uvicorn."""
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.backend.main:app",
        "--host", str(host),
        "--port", str(port),
        "--reload"
    ]
    print(f"🚀 Starting FastAPI Backend on http://{host}:{port} ...")
    return subprocess.Popen(cmd)

def start_frontend(port=8501):
    """Starts the Streamlit frontend."""
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        os.path.join("app", "frontend", "streamlit_app.py"),
        "--server.port", str(port),
        "--server.headless", "true"
    ]
    print(f"✨ Starting Streamlit Frontend on http://localhost:{port} ...")
    return subprocess.Popen(cmd)

def main():
    parser = argparse.ArgumentParser(description="CareerBridge AI Launcher")
    parser.add_argument("--backend-only", action="store_true", help="Launch only FastAPI backend")
    parser.add_argument("--frontend-only", action="store_true", help="Launch only Streamlit frontend")
    parser.add_argument("--host", default="127.0.0.1", help="Backend host")
    parser.add_argument("--backend-port", type=int, default=8000, help="Backend port")
    parser.add_argument("--frontend-port", type=int, default=8501, help="Frontend port")
    args = parser.parse_args()

    procs = []
    try:
        if args.backend_only:
            p_back = start_backend(host=args.host, port=args.backend_port)
            procs.append(p_back)
            p_back.wait()
        elif args.frontend_only:
            p_front = start_frontend(port=args.frontend_port)
            procs.append(p_front)
            p_front.wait()
        else:
            p_back = start_backend(host=args.host, port=args.backend_port)
            procs.append(p_back)
            # Give backend a brief moment to initialize
            time.sleep(2)
            p_front = start_frontend(port=args.frontend_port)
            procs.append(p_front)

            print("\n" + "="*60)
            print("🌟 CareerBridge AI is running successfully!")
            print(f"👉 Frontend UI:      http://localhost:{args.frontend_port}")
            print(f"👉 Backend API:     http://{args.host}:{args.backend_port}")
            print(f"👉 API Docs:        http://{args.host}:{args.backend_port}/docs")
            print("="*60 + "\n")

            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down CareerBridge AI processes...")
        for p in procs:
            p.terminate()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()
