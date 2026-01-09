# -*- coding: utf-8 -*-
"""
Unified API Startup Script
Handles model training, dependency checks, and API server startup
"""

import os
import sys
from pathlib import Path
import subprocess

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color=Colors.END):
    """Print colored message"""
    print(f"{color}{message}{Colors.END}")

def check_models():
    """Check if ML models exist"""
    rf_exists = Path("rf_model.pkl").exists()
    xgb_exists = Path("xgb_model.pkl").exists()
    return rf_exists and xgb_exists

def train_models():
    """Train ML models"""
    print_colored("\n" + "="*60, Colors.CYAN)
    print_colored("🧠 Training ML Models (this may take a few minutes)...", Colors.YELLOW)
    print_colored("="*60, Colors.CYAN)
    
    try:
        # Import training module
        sys.path.insert(0, str(Path(__file__).parent))
        from train_and_save import train_models as train
        
        # Train and save models
        rf_model, xgb_model = train()
        
        import joblib
        joblib.dump(rf_model, "rf_model.pkl")
        joblib.dump(xgb_model, "xgb_model.pkl")
        
        print_colored("\n✅ Models trained and saved successfully!", Colors.GREEN)
        return True
        
    except Exception as e:
        print_colored(f"\n❌ Model training failed: {e}", Colors.RED)
        print_colored("⚠️  API will start without ML models (limited functionality)", Colors.YELLOW)
        return False

def check_dependencies():
    """Check if required packages are installed"""
    required = ['fastapi', 'uvicorn', 'joblib', 'pandas', 'xgboost', 'scikit-learn']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print_colored(f"\n⚠️  Missing packages: {', '.join(missing)}", Colors.YELLOW)
        print_colored("Installing required packages...", Colors.BLUE)
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print_colored("✅ Packages installed successfully!", Colors.GREEN)
        except Exception as e:
            print_colored(f"❌ Failed to install packages: {e}", Colors.RED)
            return False
    
    return True

def find_available_port(start_port=8000, max_attempts=10):
    """Find an available port"""
    import socket
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None

def start_api():
    """Start the API server"""
    print_colored("\n" + "="*60, Colors.CYAN)
    print_colored("🚀 Starting API Server...", Colors.GREEN)
    print_colored("="*60, Colors.CYAN)
    
    # Find available port
    port = find_available_port()
    if not port:
        print_colored("❌ No available ports found (tried 8000-8009)", Colors.RED)
        sys.exit(1)
    
    if port != 8000:
        print_colored(f"⚠️  Port 8000 in use, using port {port} instead", Colors.YELLOW)
    
    print_colored(f"\n📡 API will be available at: {Colors.BOLD}http://127.0.0.1:{port}{Colors.END}")
    print_colored(f"📚 Interactive docs at: {Colors.BOLD}http://127.0.0.1:{port}/docs{Colors.END}")
    print_colored(f"\n💡 Press CTRL+C to stop the server\n", Colors.YELLOW)
    
    try:
        import uvicorn
        uvicorn.run("api:app", host="127.0.0.1", port=port, reload=False, log_level="info")
    except KeyboardInterrupt:
        print_colored("\n\n✅ Server stopped gracefully", Colors.GREEN)
    except Exception as e:
        print_colored(f"\n❌ Server error: {e}", Colors.RED)
        sys.exit(1)

def main():
    """Main startup routine"""
    print_colored("\n" + "🚀 "*30, Colors.CYAN)
    print_colored("   AI-POWERED STOCK DASHBOARD API", Colors.BOLD + Colors.GREEN)
    print_colored("   Unified Startup System v2.0", Colors.CYAN)
    print_colored("🚀 "*30 + "\n", Colors.CYAN)
    
    # Change to signals directory
    os.chdir(Path(__file__).parent)
    
    # Step 1: Check dependencies
    print_colored("📦 Step 1/3: Checking dependencies...", Colors.BLUE)
    if not check_dependencies():
        print_colored("❌ Dependency check failed!", Colors.RED)
        sys.exit(1)
    print_colored("✅ All dependencies satisfied\n", Colors.GREEN)
    
    # Step 2: Check/train models
    print_colored("🧠 Step 2/3: Checking ML models...", Colors.BLUE)
    if check_models():
        print_colored("✅ Models found: rf_model.pkl, xgb_model.pkl\n", Colors.GREEN)
    else:
        print_colored("⚠️  Models not found. Training new models...", Colors.YELLOW)
        train_models()
    
    # Step 3: Start API
    print_colored("🚀 Step 3/3: Starting API server...", Colors.BLUE)
    start_api()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n👋 Goodbye!", Colors.CYAN)
        sys.exit(0)
    except Exception as e:
        print_colored(f"\n❌ Startup failed: {e}", Colors.RED)
        sys.exit(1)
