import os
from pathlib import Path

def audit_module(module_path):
    print(f"--- Auditing Module: {module_path.name} ---")
    required_paths = [
        "00_inputs/urls.txt",
        "01_source_cards/",
        "02_final_synthesis/stage2_final_synthesis.md",
        "03_study_pack/stage3_study_pack.md"
    ]
    
    for path in required_paths:
        full_path = module_path / path
        if full_path.exists():
            status = "✅ FOUND"
        else:
            status = "❌ MISSING"
        print(f"{status}: {path}")

module_dir = Path(r"courses/global-quality-maternal-and-newborn-care/module-3")
audit_module(module_dir)