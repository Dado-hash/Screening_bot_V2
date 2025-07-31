#!/usr/bin/env python3
"""
Dashboard launcher for Cryptocurrency Screening Bot V2.
Launches the Streamlit web interface.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Launch the Streamlit dashboard."""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    dashboard_path = project_root / "src" / "dashboard" / "app.py"
    
    # Change to project root directory
    os.chdir(project_root)
    
    # Check if dashboard file exists
    if not dashboard_path.exists():
        print("❌ Dashboard file not found!")
        print(f"Expected location: {dashboard_path}")
        sys.exit(1)
    
    # Check if required packages are installed
    try:
        import streamlit
        import plotly
        print("✅ Required packages found")
    except ImportError as e:
        print(f"❌ Missing required packages: {e}")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Launch Streamlit
    print("🚀 Launching Crypto Screening Dashboard V2...")
    print(f"📂 Project root: {project_root}")
    print(f"🌐 Dashboard will open in your browser")
    print("🔧 Use Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Launch streamlit with the dashboard app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()