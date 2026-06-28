import os
import google.generativeai as genai
from pathlib import Path

def main():
    # 1. Configuration & Paths
    workspace_dir = Path(r"C:\Users\KARANJA\Downloads\Assistant & Agentic AI\MNCH_Coursera_Automation_Workspace")
    module_dir = workspace_dir / "courses" / "global-quality-maternal-and-newborn-care" / "module-3"
    
    input_file = module_dir / "02_final_synthesis" / "stage2_final_synthesis.md"
    output_dir = module_dir / "03_study_pack"
    output_file = output_dir / "stage3_study_pack.md"
    
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        print(f"❌ Error: Final Synthesis file not found at {input_file}")
        return

    print("📄 Loading Final Synthesis document...")
    synthesis_content = input_file.read_text(encoding="utf-8")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY missing.")
        return
        
    genai.configure(api_key=api_key)

    # 2. Strict Guardrails (Aligned with RICKEM & Onboarding Rules)
    system_instruction = (
        "You are an expert clinical educator acting under strict closed-book constraints.\n"
        "RULE 1: Answer ONLY using the text provided. Do not invent any clinical facts, metrics, or guidelines.\n"
        "RULE 2: Output only the requested Markdown structure. No conversational filler, pleasantries, or transitions.\n"
        "RULE 3: Maintain extreme factual density. Extract high-yield operational/clinical data suitable for Anki."
    )

    prompt = (
        "Analyze the following Final Synthesis document and generate a pristine Study-Pack strictly following this schema.\n\n"
        "--- STRUCTURAL SCHEMA ---\n"
        "# Module 3: Clinical Study-Pack\n\n"
        "--- \n\n"
        "## 1. High-Yield Assessment Quiz\n"
        "Generate 5 multiple-choice questions. Format exactly as:\n"
        "**Q1. [Clear, knowledge-focused question]**\n"
        "- A) [Option A]\n"
        "- B) [Option B]\n"
        "- C) [Option C]\n"
        "- D) [Option D]\n\n"
        "### Quiz Answer Key & Clinical Rationale\n"
        "* **Q1:** [Letter] - *Rationale:* [Concise, text-grounded explanation. If an answer cannot be explicitly confirmed by the text, state 'Not stated in the provided text'].\n\n"
        "--- \n\n"
        "## 2. Active Recall Flashcard Matrix (Anki-Ready)\n"
        "Extract 5 high-yield clinical/operational concepts. Format as a table:\n"
        "| Core Concept / Term | Definition | Operational Relevance |\n"
        "| :--- | :--- | :--- |\n"
        "| Example | Example | Example |\n\n"
        "--- \n\n"
        "## 3. Clinical Discussion Prompts\n"
        "Generate 3 debate/discussion prompts. Format as:\n"
        "> **Discussion Track 1: [Topic Title]**\n"
        "> [Analytical question based on clinical realities].\n\n"
        "--- END OF SCHEMA ---\n\n"
        f"--- FINAL SYNTHESIS SOURCE TEXT ---\n{synthesis_content}\n"
    )

    print("🚀 Sending structured prompt to Gemini API...")
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_instruction
        )
        
        generation_config = genai.GenerationConfig(
            temperature=0.0, # Zero temperature forces strict factual extraction
            top_p=0.8,
            max_output_tokens=8192
        )

        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        if response.text:
            output_file.write_text(response.text, encoding="utf-8")
            print(f"✅ Success! Study-Pack saved to:\n{output_file}")
        else:
            print("⚠️ Error: Empty response from API.")
            
    except Exception as e:
        print(f"❌ API Error: {e}")

if __name__ == "__main__":
    main()