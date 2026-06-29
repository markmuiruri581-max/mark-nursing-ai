import os
from pathlib import Path

def display_status_and_next_steps(current_stage):
    workspace = Path(r"C:\Users\KARANJA\Downloads\Assistant & Agentic AI\MNCH_Coursera_Automation_Workspace")
    module_dir = workspace / "courses" / "global-quality-maternal-and-newborn-care" / "module-3"
    
    # Define paths to check
    source_cards = module_dir / "01_source_cards" / "source_card_01.md"
    synthesis = module_dir / "02_final_synthesis" / "stage2_final_synthesis.md"
    study_pack = module_dir / "03_study_pack" / "stage3_study_pack.md"

    print("\n" + "="*60)
    print("🤖 CO-PILOT: STATUS DASHBOARD")
    print(f"Current State: {current_stage}")
    print("-" * 60)
    
    # Logic to determine next step
    if not source_cards.exists():
        print("STATUS: Stage 1 (Source Cards) NOT DETECTED.")
        print("NEXT COMMAND: python .\\auto_gemini_source_cards.py")
    elif not synthesis.exists():
        print("STATUS: Stage 1 complete. Synthesis pending.")
        print("NEXT COMMAND: python .\\run_stage2_synthesis.py")
    elif not study_pack.exists():
        print("STATUS: Stage 2 complete. Study-Pack pending.")
        print("NEXT COMMAND: python .\\run_stage3_studypack.py")
    else:
        print("STATUS: FULL PIPELINE COMPLETE.")
        print("NEXT STEP: Module 3 is finalized. Ready for Module 4 initialization.")
    
    print("="*60 + "\n")