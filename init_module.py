import os
from pathlib import Path
import sys

def init_module(module_number):
    workspace = Path(r"C:\Users\KARANJA\Downloads\Assistant & Agentic AI\MNCH_Coursera_Automation_Workspace")
    course_path = workspace / "courses" / "global-quality-maternal-and-newborn-care"
    module_path = course_path / f"module-{module_number}"
    
    # Define required subfolders
    subfolders = [
        "01_source_cards",
        "01_source_cards/source_card_prompt_package_20260628113233", # Matches your naming convention
        "02_final_synthesis",
        "03_study_pack"
    ]
    
    print(f"🚀 Initializing Module {module_number} infrastructure...")
    
    for sub in subfolders:
        target = module_path / sub
        target.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {target}")
        
    print(f"\nModule {module_number} is ready for content.")
    print(f"Next Action: Place your source card prompts in: {module_path / '01_source_cards' / 'source_card_prompt_package_20260628113233'}")

if __name__ == "__main__":
    # Allows you to specify the module number (e.g., python init_module.py 4)
    module_num = sys.argv[1] if len(sys.argv) > 1 else "4"
    init_module(module_num)