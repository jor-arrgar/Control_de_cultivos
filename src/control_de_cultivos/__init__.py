import os
import sys
import subprocess
from pathlib import Path
import traceback


def launch_streamlit_gui(port: int = 8000):
    """Launch Streamlit GUI in a separate process."""
    root = Path(__file__).resolve().parents[2]
    app_file = root / "src" / "control_de_cultivos" / "main.py"
    
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        str(app_file),
        "--server.port", str(port),
        "--server.headless", "true",
        "--server.enableXsrfProtection", "false"
    ]
    
    print(f"▶ Starting Streamlit GUI on http://localhost:{port}")
    
    streamlit_process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    print(f"   Process PID: {streamlit_process.pid}")
    return streamlit_process

def launch_fastapi_backend(port: int = 8001):
    """Launch FastAPI backend with better error handling."""
    print(f"\n▶ Starting FastAPI Backend on http://localhost:{port}")
    
    # Check if uvicorn is available first
    try:
        from importlib.util import find_spec
        if not find_spec("uvicorn"):
            print("   ❌ ERROR: uvicorn not installed in virtual environment")
            print("   Install with: pip install uvicorn[standard]")
            return None
        
        # Check api.py exists
        api_path = Path(__file__).resolve().parents[2] / "src" / "control_de_cultivos" / "api.py"
        if not api_path.exists():
            print(f"   ❌ ERROR: api.py not found at {api_path}")
            return None
        
        root = Path(__file__).resolve().parents[2]
        src_root = root / "src"

        env = os.environ.copy()
        env["PYTHONPATH"] = str(src_root) + os.pathsep + env.get("PYTHONPATH", "")

        uvicorn_command = [
            sys.executable,
            "-m",
            "uvicorn",
            "control_de_cultivos.api:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "info",
        ]
        
        print(f"   Command: {' '.join(uvicorn_command)}")
        print(f"   ⚠ Note: --reload removed for subprocess stability")
        
        # Start FastAPI with better logging
        fastapi_process = subprocess.Popen(
            uvicorn_command,
            cwd=str(root),
            env=env,
            stdout=subprocess.PIPE,  # Captures logs
            stderr=subprocess.PIPE,  # Captures errors separately
            text=True,
            bufsize=1
        )
        
        print(f"   Process PID: {fastapi_process.pid}")
        
        # Give process time to start properly (increase timeout)
        import time
        time.sleep(5)  # Longer startup time
        
        # Check if process is still running
        if fastapi_process.poll() is None:  # Still running
            print("   ✓ FastAPI server started successfully")
            
            # Try to connect briefly to verify
            try:
                import urllib.request
                urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2)
                print("   ✓ Verified: Server responds to health check")
            except Exception as e:
                print(f"   ⚠ Warning: Health check failed: {e}")
            
            return fastapi_process
        
        else:
            # Process died! Read stderr for error message
            stdout, stderr = fastapi_process.communicate()
            print(f"   ❌ PROCESS DIED with exit code {fastapi_process.returncode}")
            
            if stdout and len(stdout.strip()) > 100:
                print(f"   Output:\n{stdout[-500:]}")  # Last 500 chars
            
            if stderr and len(stderr.strip()) > 100:
                print(f"   Errors:\n{stderr[-1000:]}")  # Last 1000 chars (more for errors)
            
            return None
    
    except ImportError as e:
        print(f"   ❌ ERROR: Cannot import uvicorn: {e}")
        return None
    except Exception as e:
        print(f"   ❌ ERROR: Failed to start FastAPI: {e}")
        traceback.print_exc()
        return None

def main():
    """Main entry point for the application."""
    streamlit_port = int(os.getenv("STREAMLIT_PORT", 8000))
    fastapi_port = int(os.getenv("FASTAPI_PORT", 8001))
    
    print("=" * 60)
    print("   CAP Management System")
    print("=" * 60)
    print(f"Starting services...")
    print(f"  • Streamlit GUI: http://localhost:{streamlit_port}")
    print(f"  • FastAPI API:   http://localhost:{fastapi_port}/docs")
    print("=" * 60)
    
    # Start both services
    streamlit_process = launch_streamlit_gui(port=streamlit_port)
    fastapi_process = launch_fastapi_backend(port=fastapi_port)
    
    print("=" * 60)
    print(f"Services status:")
    if streamlit_process:
        print(f"  ✓ Streamlit PID: {streamlit_process.pid}")
    else:
        print(f"  ✗ Streamlit failed to start")
    
    if fastapi_process is None:
        print(f"  ⚠ FastAPI not started (errors above)")
    else:
        print(f"  ✓ FastAPI PID:   {fastapi_process.pid}")
    print("=" * 60)
    
    # Wait for processes
    try:
        if streamlit_process:
            streamlit_process.wait()
        if fastapi_process:
            fastapi_process.wait()
    except KeyboardInterrupt:
        print("\n\nShutting down CAP Management System...")
        if streamlit_process:
            streamlit_process.terminate()
        if fastapi_process and hasattr(fastapi_process, 'terminate'):
            fastapi_process.terminate()
        
        try:
            for process in [p for p in [streamlit_process, fastapi_process] if p]:
                process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("\nForce killing processes...")
            for process in [p for p in [streamlit_process, fastapi_process] if p]:
                process.kill()
    
    print("All services stopped.")

if __name__ == "__main__":
    main()