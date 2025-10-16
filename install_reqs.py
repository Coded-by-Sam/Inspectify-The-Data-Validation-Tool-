import sys
import os
import subprocess  # ✅ import the actual subprocess module

# Auto-install requirements.txt if not already installed
def install_requirements():
    if os.path.exists("requirements.txt"):
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                stdout=subprocess.DEVNULL,  # hide output
                stderr=subprocess.DEVNULL
            )
            print("✅ Requirements installed successfully (quiet mode).")
        except subprocess.CalledProcessError:
            print("⚠️ Failed to install requirements. Please run manually: pip install -r requirements.txt")
    else:
        print("⚠️ requirements.txt not found.")

if __name__ == "__main__":
    install_requirements()
