import subprocess
import sys
import time
from pathlib import Path

def main():
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    app_path = base_dir / "app.py"

    cmd = [
        sys.executable,
        "-m", "streamlit",
        "run", str(app_path),
        "--server.port=8501",
        "--server.headless=true",
        "--server.runOnSave=false",
        "--server.fileWatcherType=none",
        "--browser.gatherUsageStats=false"
    ]

    # SADECE Streamlit'i başlat
    process = subprocess.Popen(cmd)

    # CPU yakmadan process'i hayatta tut
    try:
        while process.poll() is None:
            time.sleep(2)
    except KeyboardInterrupt:
        process.terminate()

if __name__ == "__main__":
    main()
