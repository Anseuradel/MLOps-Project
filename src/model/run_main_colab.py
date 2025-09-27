import os
import subprocess
import sys

# Run the main training script (in src/model)
exit_code = subprocess.call([sys.executable, "-m", "src.model.main_loading_by_chunks"])
if exit_code != 0:
    print(" main_loading_by_chunks.py failed, aborting push.")
    sys.exit(exit_code)

# Git commands for Colab auto-push
try:
    print("\n Adding changes first...")
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", "Auto-save before pull"], check=False)

    print("\n Pulling latest changes...")
    subprocess.run(["git", "pull", "--rebase"], check=True)

    print("\n Adding new training outputs...")
    subprocess.run(["git", "add", "outputs/"], check=True)
    subprocess.run(["git", "add", "chunks.txt"], check=True)

    print("\n Committing...")
    subprocess.run(["git", "commit", "-m", "Update model & outputs from Colab"], check=True)

    print("\n Pushing to GitHub...")
    subprocess.run(["git", "push", "origin", "main"], check=True)

    print("\n  Training results pushed successfully!")

except subprocess.CalledProcessError as e:
    print(f"\n  Git operation failed: {e}")
    sys.exit(1)
