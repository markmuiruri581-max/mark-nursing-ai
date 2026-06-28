import os
import google.generativeai as genai
from pathlib import Path

def main():
    # 1. Configuration & Paths
    # Assuming your script is run from the workspace root or we use absolute paths
    workspace_dir = Path(r"C:\Users\KARANJA\Downloads\Assistant & Agentic AI\MNCH_Coursera_Automation_Workspace")
    module_dir = workspace_dir / "courses" / "global-quality-maternal-and-newborn-care" / "module-3"
    
    input_file = module_dir / "01_source_cards" / "combined_source_cards.md"
    output_dir = module_dir / "02_final_synthesis"
    output_file = output_dir / "stage2_final_synthesis.md"
    
    # Create the output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # 2. Check if input file exists
    if not input_file.exists():
        print(f"❌ Error: Could not find master file at {input_file}")
        return

    print("📄 Loading combined source cards...")
    master_content = input_file.read_text(encoding="utf-8")

    # 3. Initialize Gemini API
    # Ensure GEMINI_API_KEY is set in your environment variables
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable is missing.")
        return
        
    genai.configure(api_key=api_key)

    # 4. Construct System Instructions & Prompt
    # We use system instructions to enforce strict healthcare AI guardrails
    system_instruction = (
        "You are an expert clinical educator, global health researcher, and AI assistant "
        "building a Coursera course on Global Quality Maternal and Newborn Care.\n"
        "Your task is to execute Stage 2: Final Synthesis.\n\n"
        "STRICT HEALTHCARE GUARDRAILS:\n"
        "- Do not invent facts, statistics, clinical recommendations, or quotes.\n"
        "- Base all synthesis strictly and exclusively on the provided source cards.\n"
        "- Do not provide patient-specific medical advice.\n"
        "- Maintain absolute clinical and academic rigor.\n"
        "- If source cards conflict, state the different perspectives neutrally."
    )

    prompt = (
        "Please synthesize the following combined source cards into a comprehensive, cohesive 'Final Synthesis' "
        "markdown document for Module 3.\n\n"
        "Requirements:\n"
        "1. Organize the content logically by thematic areas, creating an overarching narrative.\n"
        "2. Use clear Markdown headings (H1, H2, H3), subheadings, and bullet points.\n"
        "3. Highlight key global health terms or statistics in bold.\n"
        "4. Include brief citations pointing back to the source cards (e.g., [Source Card 03]) to maintain traceability.\n"
        "5. Conclude with a brief 'Key Takeaways' section summarizing the module.\n\n"
        f"--- SOURCE CARDS START ---\n{master_content}\n--- SOURCE CARDS END ---\n"
    )

    # 5. Call the API
    print("🚀 Sending prompt to Gemini API (gemini-2.5-flash)...")
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_instruction
        )
        
        # Generation configuration optimized for factual, structured educational text
        generation_config = genai.GenerationConfig(
            temperature=0.2, # Lower temperature reduces hallucinations
            top_p=0.8,
            max_output_tokens=8192 # Ensures we don't cut off long syntheses
        )

        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        # 6. Save the output
        if response.text:
            output_file.write_text(response.text, encoding="utf-8")
            print(f"✅ Success! Stage 2 Final Synthesis saved to:\n{output_file}")
        else:
            print("⚠️ Error: Received an empty response from the API.")
            
    except Exception as e:
        print(f"❌ An error occurred during API execution: {e}")

if __name__ == "__main__":
    main()