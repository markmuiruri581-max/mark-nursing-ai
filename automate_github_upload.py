import subprocess
from pathlib import Path
from datetime import datetime

def run_git_command(command, repo_dir):
    """Helper function to run a system command safely inside your repository directory."""
    try:
        # execute command and capture output
        result = subprocess.run(
            command, 
            cwd=repo_dir, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error executing command: {' '.join(command)}")
        print(f"Details: {e.stderr.strip()}")
        return None

def main():
    # 1. Configuration & Paths
    workspace_dir = Path(r"C:\Users\KARANJA\Downloads\Assistant & Agentic AI\MNCH_Coursera_Automation_Workspace")
    
    print("🔄 Starting GitHub Automation Upload Process...")
    
    # 2. Check if .git is initialized
    git_folder = workspace_dir / ".git"
    if not git_folder.exists():
        print("📁 Git repository not detected locally. Initializing Git...")
        run_git_command(["git", "init"], workspace_dir)
        # Assumes default branch is main
        run_git_command(["git", "branch", "-M", "main"], workspace_dir)
    
    # 3. Stage all tracking and new content
    print("📦 Staging files for upload (git add)...")
    run_git_command(["git", "add", "."], workspace_dir)
    
    # 4. Create a descriptive commit message with today's date
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"Automated upload: Module 3 pipeline updates - {timestamp}"
    print(f"✍️ Committing changes: '{commit_message}'...")
    run_git_command(["git", "commit", "-m", commit_message], workspace_dir)
    
    # 5. Push code safely up to the GitHub cloud repository
    print("🚀 Pushing code portfolio up to GitHub remote repository...")
    push_result = run_git_command(["git", "push", "-u", "origin", "main"], workspace_dir)
    
    if push_result is not None:
        print("✅ Success! Your pipeline code and generated content are live on GitHub.")
    else:
        print("❌ Upload failed. Please check your internet connection or your remote 'origin' URL configuration.")

if __name__ == "__main__":
    main()