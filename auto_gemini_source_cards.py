import os
import time
from pathlib import Path
from dotenv import load_dotenv
from renderer import render_markdown_file
from pilot_utils import display_status_and_next_steps
from pdf_extractor import extract_text_from_pdf  # New extraction engine

def print_api_renewal_guide(error_message):
    print("\n" + "="*60)
    print("❌ CRITICAL ERROR: GEMINI API CONNECTION FAILED")
    print(f"Details: {error_message}")
    print("="*60)

def verify_url_signature(prompt_content):
    lower_content = prompt_content.lower()
    # If any of these are found, we treat it as a PDF
    pdf_signatures = [".pdf", "/pdf", "type=pdf", "/download"]
    for signature in pdf_signatures:
        if signature in lower_content:
            return False
    return True

def main():
    print("🤖 CO-PILOT: AUTOMATED WORKSPACE CONTEXT ANALYSIS")
    
    # 1. Setup & Diagnostic Override
    workspace_dir = Path(r"C:\Users\KARANJA\Downloads\Assistant & Agentic AI\MNCH_Coursera_Automation_Workspace")
    env_file_path = workspace_dir / ".env"
    load_dotenv(dotenv_path=env_file_path, override=True)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ API Key Missing.")
        return
    api_key = api_key.strip().replace('"', '').replace("'", "")
    
    # 2. Logic Setup
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    system_rules = "You are a precise data extraction engine. Output strictly in Markdown. Use headers, bullets, and bolding for clinical density."
    model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=system_rules)
    
    module_dir = workspace_dir / "courses" / "global-quality-maternal-and-newborn-care" / "module-3"
    base_dir = module_dir / "01_source_cards"
    prompt_package_dir = base_dir / "source_card_prompt_package_20260628113233"
    
    if not prompt_package_dir.exists():
        print("📍 Missing prompt folder.")
        return

    # 3. Processing Loop
    prompt_files = sorted([f.name for f in prompt_package_dir.iterdir() if f.name.startswith('source_card_prompt_') and f.name.endswith('.md')])
    
    for idx, prompt_file in enumerate(prompt_files, start=1):
        filename = f"source_card_{idx:02d}.md"
        filepath = base_dir / filename
        
        if filepath.exists() and filepath.stat().st_size > 200:
            continue
            
        print(f"🚀 Processing: {prompt_file}")
        prompt_content = (prompt_package_dir / prompt_file).read_text(encoding='utf-8')
        
        # 4. Content Processing (PDF or Standard)
        if not verify_url_signature(prompt_content):
            print(f"📄 PDF DETECTED: Extracting from {prompt_file}...")
            # We treat the prompt content as the path/source to the PDF
            pdf_data = extract_text_from_pdf(prompt_content)
            final_prompt = f"Synthesize this clinical PDF data:\n\n{pdf_data}"
        else:
            final_prompt = prompt_content
            
        try:
            response = model.generate_content(final_prompt)
            if response.text:
                filepath.write_text(f"# Source Card {idx:02d}\n\n{response.text}", encoding='utf-8')
                render_markdown_file(str(filepath), str(filepath.with_suffix('.html')), f"Source Card {idx:02d}")
                time.sleep(2)
        except Exception as e:
            print(f"❌ API Error: {e}")
            break

    # Autonomous status reporter
    display_status_and_next_steps(current_stage="Stage 1: Source Cards")

if __name__ == "__main__":
    main()