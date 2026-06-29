
import os
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv
from renderer import render_markdown_file
from pilot_utils import display_status_and_next_steps

def main():
    print("🔍 RUNNING CONFIGURATION DIAGNOSTICS...")
    
    # 1. Setup Workspace Paths
    workspace_dir = Path(r"C:\Users\KARANJA\Downloads\Assistant & Agentic AI\MNCH_Coursera_Automation_Workspace")
    env_file_path = workspace_dir / ".env"
    
    # 2. Force load the .env file
    load_dotenv(dotenv_path=env_file_path, override=True)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY is missing.")
        return
    api_key = api_key.strip().replace('"', '').replace("'", "")
    
    # 3. Path Configuration
    module_dir = workspace_dir / "courses" / "global-quality-maternal-and-newborn-care" / "module-3"
    input_file = module_dir / "02_final_synthesis" / "stage2_final_synthesis.md"
    output_dir = module_dir / "03_study_pack"
    output_file = output_dir / "stage3_study_pack.md"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        print(f"❌ Error: Final Synthesis file not found.")
        return

    # 4. Initialize Gemini
    genai.configure(api_key=api_key)
    system_instruction = (
        "You are an expert clinical educator. Answer ONLY using the provided text. "
        "Output structured Markdown. Keep it dense and high-yield."
    )
    model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=system_instruction)

    # 5. Execution
    print("🚀 Sending structured prompt to Gemini...")
    try:
        synthesis_content = input_file.read_text(encoding="utf-8")
        prompt = f"Analyze this synthesis and generate a Study-Pack with Quiz, Flashcards, and Discussion prompts.\n\n{synthesis_content}"
        
        response = model.generate_content(prompt)
        
        if response.text:
            output_file.write_text(response.text, encoding="utf-8")
            print(f"✅ Success! Study-Pack MD saved.")
            
            # HTML Rendering
            html_file = output_file.with_suffix('.html')
            render_markdown_file(str(output_file), str(html_file), "Module 3: Study Pack")
            print(f"🎨 Visual HTML document rendered.")
        else:
            print("⚠️ Error: Empty response from API.")
            
    except Exception as e:
        print(f"❌ API Error: {e}")

    # --- THE AUTONOMOUS NEXT STEP ---
    # This sits inside main(), aligned with the code above it.
    display_status_and_next_steps(current_stage="Stage 3: Study Pack")

if __name__ == "__main__":
    main()